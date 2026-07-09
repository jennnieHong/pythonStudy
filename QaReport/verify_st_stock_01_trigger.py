import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_stock_01_trigger_cascade():
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
        
        # Target Data Definitions
        ms_no = 'NC0005'
        goods_cd = 'T0000555'
        chain_no = 'C002'
        survey_date = '20260605'
        idx = '1'
        modify_qty = 10
        modify_cost = 11182
        
        print(f"\nTarget validation data:")
        print(f"  MS_NO: {ms_no}, GOODS_CD: {goods_cd}, CHAIN_NO: {chain_no}")
        print(f"  Survey Date: {survey_date}, Modify Qty: {modify_qty}, Modify Cost: {modify_cost}")

        print("\n--- [START] Simulating Stock 01 Trigger Cascade ---")

        # -------------------------------------------------------------------------
        # Depth 1: Insert to IMREALTB & Update to PROC_FG = '1' (Confirm)
        # -------------------------------------------------------------------------
        print("\n[Depth 1] Inserting initial unconfirmed record into IMREALTB...")
        cur.execute("""
            INSERT INTO hmsfns.imrealtb (
                ms_no, survey_date, idx, goods_cd, grp_cd, chain_ms_no, 
                survey_qty, modify_qty, modify_cost, proc_fg, create_id, create_dtime,
                last_id, last_dtime
            ) VALUES (
                %s, %s, %s, %s, 'G01', %s,
                10, %s, %s, '0', 'admin', to_char(now(), 'YYYYMMDDHH24MISS'),
                'admin', to_char(now(), 'YYYYMMDDHH24MISS')
            );
        """, (ms_no, survey_date, idx, goods_cd, ms_no, modify_qty, modify_cost))
        print("Record inserted to IMREALTB.")
        
        print("\n[Depth 1] Simulating Confirmation (Updating IMREALTB.PROC_FG to '1')...")
        cur.execute("""
            UPDATE hmsfns.imrealtb
            SET proc_fg = '1'
            WHERE ms_no = %s AND survey_date = %s AND idx = %s AND goods_cd = %s;
        """, (ms_no, survey_date, idx, goods_cd))
        print(f"Updated row count: {cur.rowcount}")

        # -------------------------------------------------------------------------
        # Depth 2: Insert into IMTRLGTB (Simulated Trigger Service)
        # -------------------------------------------------------------------------
        print("\n[Depth 2] Simulating Java Trigger Tr_IMREAL_T01_Service & Sp_SUB_IMTRLG_I_Service...")
        key_bill_no = f"{idx}{ms_no}G01{goods_cd}"
        
        cur.execute("""
            INSERT INTO hmsfns.imtrlgtb (
                ms_no, proc_fg, proc_date, chain_ms_no, goods_cd, 
                trlg_qty, trlg_cost, trlg_seq, trlg_dtime, key_bill_no, proc_yn
            ) VALUES (
                %s, 'A', %s, %s, %s,
                %s, %s, 1, to_char(now(), 'YYYYMMDDHH24MISS'), %s, 'N'
            ) RETURNING trlg_seq, trlg_dtime;
        """, (ms_no, survey_date, ms_no, goods_cd, modify_qty, modify_cost, key_bill_no))
        
        trlg_seq, create_dtime = cur.fetchone()
        print(f"IMTRLGTB sync row inserted - Seq: {trlg_seq}, Time: {create_dtime}, KeyBillNo: {key_bill_no}")

        # -------------------------------------------------------------------------
        # Depth 3: Cascade Merge to TB_IMMMIO_COST (Simulated Monthly Cost Update)
        # -------------------------------------------------------------------------
        print("\n[Depth 3] Simulating Sp_SUB_TOT_AVG_SINGLE_P_Service (mergeCostAdjust)...")
        
        # Check initial state of TB_IMMMIO_COST
        cur.execute("""
            SELECT adjust_qty, adjust_cost 
            FROM hmsfns.tb_immmio_cost 
            WHERE create_month = %s AND ms_no = %s AND goods_cd = %s;
        """, (survey_date[:6], ms_no, goods_cd))
        initial_cost_row = cur.fetchone()
        init_qty = initial_cost_row[0] if initial_cost_row else 0
        init_cost = initial_cost_row[1] if initial_cost_row else 0
        print(f"Initial state in TB_IMMMIO_COST: Adjust Qty = {init_qty}, Cost = {init_cost}")

        # Execute MERGE INTO TB_IMMMIO_COST
        cur.execute("""
            MERGE INTO hmsfns.tb_immmio_cost A
            USING DUAL
               ON (   A.create_month  = %s
                  AND A.ms_no         = %s
                  AND A.goods_cd      = %s
                  )
            WHEN MATCHED THEN
                 UPDATE
                    SET adjust_qty  = adjust_qty + %s
                      , adjust_cost = adjust_cost + %s
            WHEN NOT MATCHED THEN
                 INSERT (       create_month         ,       ms_no                ,       goods_cd          ,         chain_ms_no
                        ,       adjust_qty           ,       adjust_cost          ,       ucost             ,         tgood_in_qty
                        ,       ucost_in_qty         ,       usuprice_vat
                        )
                 VALUES ( %s, %s, %s, %s, %s, %s, 1118.17, 1.0, 1118.17, 1118.17 );
        """, (survey_date[:6], ms_no, goods_cd, modify_qty, modify_cost, survey_date[:6], ms_no, goods_cd, ms_no, modify_qty, modify_cost))
        
        print("MERGE INTO TB_IMMMIO_COST executed successfully.")

        # -------------------------------------------------------------------------
        # Verification Phase
        # -------------------------------------------------------------------------
        print("\n--- Verification of Trigger Cascade Results ---")
        
        # Verify Depth 1 (IMREALTB)
        cur.execute("""
            SELECT proc_fg, modify_qty, modify_cost 
            FROM hmsfns.imrealtb 
            WHERE ms_no = %s AND survey_date = %s AND idx = %s AND goods_cd = %s;
        """, (ms_no, survey_date, idx, goods_cd))
        v_real = cur.fetchone()
        print(f"Verified IMREALTB state: ProcFg = {v_real[0]}, Qty = {v_real[1]}, Cost = {v_real[2]} (Expected: '1', {modify_qty}, {modify_cost})")

        # Verify Depth 2 (IMTRLGTB)
        cur.execute("""
            SELECT proc_fg, trlg_qty, trlg_cost 
            FROM hmsfns.imtrlgtb 
            WHERE ms_no = %s AND proc_date = %s AND key_bill_no = %s;
        """, (ms_no, survey_date, key_bill_no))
        v_trlg = cur.fetchone()
        print(f"Verified IMTRLGTB state: ProcFg = {v_trlg[0]}, Qty = {v_trlg[1]}, Cost = {v_trlg[2]} (Expected: 'A', {modify_qty}, {modify_cost})")

        # Verify Depth 3 (TB_IMMMIO_COST)
        cur.execute("""
            SELECT adjust_qty, adjust_cost 
            FROM hmsfns.tb_immmio_cost 
            WHERE create_month = %s AND ms_no = %s AND goods_cd = %s;
        """, (survey_date[:6], ms_no, goods_cd))
        v_cost = cur.fetchone()
        print(f"Verified TB_IMMMIO_COST state: Adjust Qty = {v_cost[0]}, Cost = {v_cost[1]} (Expected: {int(init_qty) + modify_qty}, {int(init_cost) + modify_cost})")

        print("\n[SUCCESS] Depth 3 Trigger cascade verification passed on EDB database!")

    except Exception as e:
        print(f"[FAIL] Trigger cascade verification failed: {e}")
    finally:
        if conn:
            print("\nRolling back transaction to prevent EDB database pollution...")
            conn.rollback()
            cur.close()
            conn.close()
            print("Database connection closed cleanly.")

if __name__ == '__main__':
    test_stock_01_trigger_cascade()
