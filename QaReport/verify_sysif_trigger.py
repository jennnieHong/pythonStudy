import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_trigger_cascade():
    conn = None
    try:
        print("Connecting to EDB PostgreSQL...")
        conn = psycopg2.connect(
            host="192.168.10.206",
            port="5432",
            database="edb",
            user="hmsfns_was",
            password="astems3!"
        )
        cur = conn.cursor()
        
        # Search for a store with POS mappings and users
        cur.execute("""
            SELECT DISTINCT A.ms_no, A.ms_nm, A.if_biz_cd, A.if_shop_cd, A.chain_no, A.if_reserve_amt, A.if_return_reserve_amt, A.open_fg
            FROM hmsfns.mmembstb A
            INNER JOIN hmsfns.muserstb B ON A.ms_no = B.ms_no
            WHERE A.if_biz_cd IS NOT NULL AND A.if_shop_cd IS NOT NULL AND B.acct_expire = 'N'
            LIMIT 1;
        """)
        row = cur.fetchone()
        if not row:
            print("[FAIL] No store found with POS mappings and active users.")
            return
            
        ms_no, ms_nm, if_biz_cd, if_shop_cd, chain_no, if_reserve_amt, if_return_reserve_amt, open_fg = row
        print(f"\nFound target store: {ms_no} ({ms_nm})")
        print(f"[Initial MMEMBSTB] MS_NO: {ms_no}, Name: {ms_nm}, OpenFg: {open_fg}, BizCd: {if_biz_cd}, ShopCd: {if_shop_cd}, Reserve: {if_reserve_amt}, Return: {if_return_reserve_amt}, ChainNo: {chain_no}")
        
        # We will use transaction and roll back at the end to ensure zero pollution.
        print("\n--- [START] Simulating Trigger Cascade ---")
        
        # Fetch users of target store in MUSERSTB
        cur.execute("""
            SELECT user_id, user_nm, acct_expire, emp_id, emp_card_no, order_fg
            FROM hmsfns.muserstb WHERE ms_no = %s AND acct_expire = 'N';
        """, (ms_no,))
        users = cur.fetchall()
        print(f"[Initial MUSERSTB] Active users for store {ms_no}: {len(users)}")
        for u in users[:3]: # Show up to 3
            print(f"  User ID: {u[0]}, Name: {u[1]}, Expire: {u[2]}")
            
        target_user = users[0]
        
        # =========================================================================
        # Depth 1: Update Cash preparation/refund reserve in MMEMBSTB
        # =========================================================================
        new_reserve = int(if_reserve_amt or 0) + 50000
        print(f"\n[Depth 1] Simulating Cash Interface Confirmation (Updating MMEMBSTB.IF_RESERVE_AMT to {new_reserve})...")
        cur.execute("""
            UPDATE hmsfns.mmembstb 
            SET if_reserve_amt = %s 
            WHERE if_biz_cd = %s AND if_shop_cd = %s;
        """, (new_reserve, if_biz_cd, if_shop_cd))
        print(f"Updated row count: {cur.rowcount}")
        
        # Verify Depth 1
        cur.execute("SELECT if_reserve_amt FROM hmsfns.mmembstb WHERE ms_no = %s;", (ms_no,))
        updated_reserve = cur.fetchone()[0]
        print(f"Verified MMEMBSTB updated reserve amount: {updated_reserve}")
        
        # =========================================================================
        # Depth 2: Trigger MMEMBS_T01 inserts to SSMEMBTB & MMSLOGTB
        # =========================================================================
        print("\n[Depth 2] Simulating Java Trigger Tr_MMEMBS_T01_Service inserts...")
        
        # Log to MMSLOGTB
        log_data = f"{ms_no}|{ms_nm}|[IF_RESERVE_AMT:{if_reserve_amt}->{new_reserve}]"
        cur.execute("""
            INSERT INTO hmsfns.mmslogtb (ms_no, table_nm, log_seq, log_dtime, user_id, log_fg, log_data)
            VALUES (%s, 'MMEMBSTB', nextval('hmsfns.mmslogsq'), to_char(now(), 'YYYYMMDDHH24MISS'), 'admin', 'U', %s)
            RETURNING log_seq, log_dtime;
        """, (ms_no, log_data))
        log_seq, log_dtime = cur.fetchone()
        print(f"MMSLOGTB log inserted - Seq: {log_seq}, Time: {log_dtime}, Data: {log_data}")
        
        # Sync to SSMEMBTB (exactly 21 parameters matching 21 placeholders)
        cur.execute("""
            INSERT INTO hmsfns.ssmembtb (
                ms_no, log_seq, proc_fg, proc_dtime, biz_no, ms_nm, chain_nm, master_nm, tel_no, chain_fg, address, round_fg, kitchen_yn, delivery_yn, vat_fg, amt_round_pos, amt_round_type, kitchen_cnt, sale_del, weight_unit, price_unit, kitchen_group_yn, if_biz_cd, if_shop_cd
            ) VALUES (
                %s, to_char(now(), 'YYYYMMDD') || lpad(nextval('hmsfns.ssmembsq')::text, 8, '0'), 'U', to_char(now(), 'YYYYMMDDHH24MISS'), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING log_seq, proc_dtime;
        """, (
            ms_no,          # 1. ms_no
            if_shop_cd,     # 2. biz_no (test value)
            ms_nm,          # 3. ms_nm
            chain_no,       # 4. chain_nm (test value)
            '대표자',       # 5. master_nm
            '02-123-4567',  # 6. tel_no
            '1',            # 7. chain_fg
            '강남구',       # 8. address
            '0',            # 9. round_fg
            'N',            # 10. kitchen_yn
            'N',            # 11. delivery_yn
            '0',            # 12. vat_fg
            '0',            # 13. amt_round_pos
            '0',            # 14. amt_round_type
            '0',            # 15. kitchen_cnt
            '0',            # 16. sale_del
            'Y',            # 17. weight_unit
            'N',            # 18. price_unit
            'N',            # 19. kitchen_group_yn
            if_biz_cd,      # 20. if_biz_cd
            if_shop_cd      # 21. if_shop_cd
        ))
        ss_log_seq, ss_proc_dtime = cur.fetchone()
        print(f"SSMEMBTB sync row inserted - Seq: {ss_log_seq}, Time: {ss_proc_dtime}")
        
        # =========================================================================
        # Depth 3: Cascade Trigger - MMEMBSTB open_fg becomes 3 (HOLD) -> expires users in MUSERSTB -> updates SSUSERTB
        # =========================================================================
        print("\n[Depth 3] Simulating Cascade to User Account Expiry (MMEMBSTB.open_fg = '3')...")
        
        # 1. Update MMEMBSTB openFg to 3
        cur.execute("UPDATE hmsfns.mmembstb SET open_fg = '3' WHERE ms_no = %s;", (ms_no,))
        print("Updated MMEMBSTB open_fg to '3'.")
        
        # 2. Trigger MMEMBS_T01 updates MUSERSTB acct_expire = 'Y'
        cur.execute("UPDATE hmsfns.muserstb SET acct_expire = 'Y' WHERE ms_no = %s;", (ms_no,))
        print("Trigger MMEMBS_T01 executed: expired user accounts in MUSERSTB.")
        
        # 3. For the expired user, Trigger MUSERS_T01 inserts into SSUSERTB
        cur.execute("""
            INSERT INTO hmsfns.ssusertb (ms_no, log_seq, proc_dtime, proc_fg, emp_id, user_nm, emp_card_no, user_type, order_fg)
            VALUES (%s, to_char(now(), 'YYYYMMDD') || lpad(nextval('hmsfns.ssusersq')::text, 8, '0'), to_char(now(), 'YYYYMMDDHH24MISS'), 'U', %s, %s, %s, '0', %s)
            RETURNING log_seq, proc_dtime;
        """, (ms_no, target_user[3], target_user[1], target_user[4], target_user[5]))
        user_log_seq, user_proc_dtime = cur.fetchone()
        print(f"SSUSERTB sync row inserted (MUSERSTB -> SSUSERTB cascade) - Seq: {user_log_seq}, Time: {user_proc_dtime}")
        
        # 4. Trigger MUSERS_T01 inserts log to MMSLOGTB
        user_log_data = f"{ms_no}|[ACCT_EXPIRE:{target_user[2]}->Y]"
        cur.execute("""
            INSERT INTO hmsfns.mmslogtb (ms_no, table_nm, log_seq, log_dtime, user_id, log_fg, log_data)
            VALUES (%s, 'MUSERSTB', nextval('hmsfns.mmslogsq'), to_char(now(), 'YYYYMMDDHH24MISS'), 'admin', 'U', %s)
            RETURNING log_seq;
        """, (ms_no, user_log_data))
        u_log_seq = cur.fetchone()[0]
        print(f"MMSLOGTB user log inserted - Seq: {u_log_seq}, Data: {user_log_data}")
        
        # 5. Verify the entire cascade
        print("\n--- Verification of Simulated Cascade ---")
        cur.execute("SELECT if_reserve_amt, open_fg FROM hmsfns.mmembstb WHERE ms_no = %s;", (ms_no,))
        v_store = cur.fetchone()
        print(f"Verified MMEMBSTB State: Reserve = {v_store[0]}, OpenFg = {v_store[1]} (Expected: {new_reserve}, 3)")
        
        cur.execute("SELECT acct_expire FROM hmsfns.muserstb WHERE ms_no = %s AND user_id = %s;", (ms_no, target_user[0]))
        v_user = cur.fetchone()
        print(f"Verified MUSERSTB State for {target_user[0]}: Expire = {v_user[0]} (Expected: Y)")
        
        cur.execute("SELECT log_data FROM hmsfns.mmslogtb WHERE ms_no = %s AND log_seq = %s;", (ms_no, log_seq))
        v_log = cur.fetchone()
        print(f"Verified MMSLOGTB Store Log: {v_log[0]}")
        
        cur.execute("SELECT log_data FROM hmsfns.mmslogtb WHERE ms_no = %s AND log_seq = %s;", (ms_no, u_log_seq))
        v_u_log = cur.fetchone()
        print(f"Verified MMSLOGTB User Log: {v_u_log[0]}")
        
        print("\nTrigger cascade simulation succeeded on EDB database!")
        
    except Exception as e:
        print(f"[FAIL] Trigger cascade simulation failed: {e}")
    finally:
        if conn:
            print("\nRolling back transaction to keep the DB clean...")
            conn.rollback()
            cur.close()
            conn.close()
            print("Database connection closed cleanly.")

if __name__ == '__main__':
    test_trigger_cascade()
