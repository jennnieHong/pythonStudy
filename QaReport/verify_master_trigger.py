# -*- coding: utf-8 -*-
import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_connection():
    return psycopg2.connect(
        host="192.168.10.206",
        port=5432,
        database="edb",
        user="hmsfns_was",
        password="astems3!"
    )

def check_status(action):
    conn = get_connection()
    cur = conn.cursor()
    
    test_ms_no = "NC0007"
    new_ms_no = "NC0021"
    
    try:
        if action == "cleanup_all":
            print("\n=== [DB Clean-up] Deleting all test data from DB to ensure clean state ===")
            
            # 1. Clean up NC% (New Stores excluding base stores) and all cascaded sub-master tables
            tables = [
                "MMEMBSTB", "MMEMBVTB", "MMEMBPTB", "SSMEMBTB", "MMSLOGTB", "MUSERSTB", "SSUSERTB",
                "MMLCLSTB", "MMMCLSTB", "MMSCLSTB", "MGOODSTB", "MMACNTTB", "MMSSRCTB", 
                "MMCPLUTB", "MMCPLKTB", "MMBUMSTB", "MSUBMNTB", "MMACNCTB", "MKTFRTTB", 
                "MKTFDCTB", "MPROMATB", "MPROGDTB", "MPRICETB", "MVNDRMTB", "MVNDRGTB",
                "WFNENVTB", "MSNDNOTB"
            ]
            for t in tables:
                cur.execute(f"DELETE FROM hmsfns.{t} WHERE MS_NO LIKE %s AND MS_NO NOT IN ('NC0001', 'NC0002', 'NC0007')", ('NC%',))
            
            # 2. Clean up NC0007 Added POS (POS numbers other than 01)
            cur.execute("DELETE FROM hmsfns.MMEMBPTB WHERE MS_NO = %s AND POS_NO <> '01'", (test_ms_no,))
            cur.execute("DELETE FROM hmsfns.SSMEMPTB WHERE MS_NO = %s AND POS_NO <> '01'", (test_ms_no,))
            
            # 3. Clean up NC0007 Added VAN POS (TID: 1234567890 or POS_NO <> '01')
            cur.execute("DELETE FROM hmsfns.MVANCOTB WHERE MS_NO = %s AND (CAT_ID = '1234567890' OR POS_NO <> '01')", (test_ms_no,))
            cur.execute("DELETE FROM hmsfns.SVANCOTB WHERE MS_NO = %s AND (CAT_ID = '1234567890' OR POS_NO <> '01')", (test_ms_no,))
            
            # 4. Clean up NC0007 Card Contract (CARD_CO: 01)
            # Since card contracts are merged, we can delete card contract for CARD_CO='01' or reset it if needed.
            cur.execute("DELETE FROM hmsfns.MMCARDTB WHERE MS_NO = %s AND CARD_CO = '01'", (test_ms_no,))
            cur.execute("DELETE FROM hmsfns.SSCARDTB WHERE MS_NO = %s AND CARD_CO = '01'", (test_ms_no,))
            
            conn.commit()
            print("[SUCCESS] All test data cleaned up successfully.")
            
        elif action == "verify_new_store":
            # Dynamic lookup for the newly created store code
            cur.execute("SELECT MS_NO FROM hmsfns.MMEMBSTB WHERE MS_NO LIKE %s AND MS_NO NOT IN ('NC0001', 'NC0002', 'NC0007') ORDER BY CREATE_DTIME DESC LIMIT 1", ('NC%',))
            row = cur.fetchone()
            if row:
                new_ms_no = row[0]
                print(f"Dynamically detected newly created store: {new_ms_no}")
            else:
                print(f"No new store found, fallback to {new_ms_no}")
                
            print(f"\n=== [DB Verification] Checking if New Store {new_ms_no} is successfully registered ===")
            
            # Check MMEMBSTB
            cur.execute("SELECT MS_NO, MS_NM, CHAIN_HQ_YN FROM hmsfns.MMEMBSTB WHERE MS_NO = %s", (new_ms_no,))
            store = cur.fetchone()
            if store:
                print(f"Store in MMEMBSTB: {store[0]} ({store[1]}), HQ_YN: {store[2]}")
            else:
                print("[FAIL] Store not found in MMEMBSTB.")
                
            # Check MMEMBVTB (Default Env)
            cur.execute("SELECT COUNT(*) FROM hmsfns.MMEMBVTB WHERE MS_NO = %s", (new_ms_no,))
            env_cnt = cur.fetchone()[0]
            print(f"Env Records in MMEMBVTB: {env_cnt}")
            
            # Check MMEMBPTB (Default POS)
            cur.execute("SELECT COUNT(*) FROM hmsfns.MMEMBPTB WHERE MS_NO = %s", (new_ms_no,))
            pos_cnt = cur.fetchone()[0]
            print(f"POS Records in MMEMBPTB: {pos_cnt}")
            
            # Check SSMEMBTB (POS Transmission)
            cur.execute("SELECT COUNT(*) FROM hmsfns.SSMEMBTB WHERE MS_NO = %s", (new_ms_no,))
            ss_cnt = cur.fetchone()[0]
            print(f"POS Sync Records in SSMEMBTB: {ss_cnt}")
            
            # Check MMSLOGTB (Log)
            cur.execute("SELECT LOG_DATA, LOG_DTIME FROM hmsfns.MMSLOGTB WHERE MS_NO = %s ORDER BY LOG_DTIME DESC LIMIT 1", (new_ms_no,))
            log = cur.fetchone()
            if log:
                print(f"Latest MMSLOGTB Log: {log[0]} (Time: {log[1]})")
                
            if store and env_cnt > 0 and pos_cnt > 0 and ss_cnt > 0:
                print("[SUCCESS] New Store Registration and Trigger Cascade (Depth 2/3) verified successfully!")
            else:
                print("[FAIL] New Store Trigger Cascade incomplete.")
                
        elif action == "verify_hold":
            print("\n=== [DB Verification] Checking if NC0007 users are EXPIRED (ACCT_EXPIRE='Y') ===")
            cur.execute("SELECT USER_ID, USER_NM, ACCT_EXPIRE FROM hmsfns.MUSERSTB WHERE MS_NO = %s", (test_ms_no,))
            users = cur.fetchall()
            print(f"Total Users: {len(users)}")
            expired_users = [u for u in users if u[2] == 'Y']
            print(f"Expired Users (ACCT_EXPIRE='Y'): {len(expired_users)} / {len(users)}")
            
            # Check SSUSERTB
            cur.execute("SELECT COUNT(*) FROM hmsfns.SSUSERTB WHERE MS_NO = %s", (test_ms_no,))
            ss_cnt = cur.fetchone()[0]
            print(f"SSUSERTB Records for NC0007: {ss_cnt}")
            
            if len(expired_users) == len(users) and len(users) > 0:
                print("[SUCCESS] Java Trigger Cascade verified: All users expired when store went HOLD.")
            else:
                print("[FAIL] Java Trigger Cascade: Not all users are expired.")
                
        elif action == "verify_open":
            print("\n=== [DB Verification] Checking if NC0007 users are ACTIVE (ACCT_EXPIRE='N') ===")
            cur.execute("SELECT USER_ID, USER_NM, ACCT_EXPIRE FROM hmsfns.MUSERSTB WHERE MS_NO = %s", (test_ms_no,))
            users = cur.fetchall()
            print(f"Total Users: {len(users)}")
            active_users = [u for u in users if u[2] == 'N']
            print(f"Active Users (ACCT_EXPIRE='N'): {len(active_users)} / {len(users)}")
            
            if len(active_users) == len(users) and len(users) > 0:
                print("[SUCCESS] Java Trigger Cascade verified: All users reactivated when store went OPEN.")
            else:
                print("[FAIL] Java Trigger Cascade: Not all users are active.")
                
        elif action == "rollback_open":
            print("\n=== [DB Clean-up] Rolling back NC0007 to OPEN in DB ===")
            cur.execute("UPDATE hmsfns.MMEMBSTB SET OPEN_FG = '2', USE_YN = 'Y' WHERE MS_NO = %s", (test_ms_no,))
            cur.execute("UPDATE hmsfns.MUSERSTB SET ACCT_EXPIRE = 'N' WHERE MS_NO = %s", (test_ms_no,))
            conn.commit()
            print("[SUCCESS] DB Rollback completed successfully.")
            
        elif action == "verify_credit_mpoint":
            print("\n=== [DB Verification] Checking credit_limit and mpoint_rate ===")
            cur.execute("SELECT MPOINT_RATE FROM hmsfns.MMEMBSTB WHERE MS_NO = %s", (test_ms_no,))
            mpoint = cur.fetchone()[0]
            cur.execute("SELECT CREDIT_LIMIT FROM hmsfns.MMEMBVTB WHERE MS_NO = %s", (test_ms_no,))
            credit = cur.fetchone()[0]
            print(f"MPOINT_RATE: {mpoint}, CREDIT_LIMIT: {credit}")
            
            # Check log
            cur.execute("SELECT LOG_DATA, LOG_DTIME FROM hmsfns.MMSLOGTB WHERE MS_NO = %s ORDER BY LOG_DTIME DESC LIMIT 1", (test_ms_no,))
            log = cur.fetchone()
            if log:
                print(f"Latest MMSLOGTB Log: {log[0]} (Time: {log[1]})")
                
            if credit is not None and int(credit) == 5000000:
                print("[SUCCESS] Credit Limit saved and trigger logged successfully.")
            else:
                print("[FAIL] Credit Limit verify failed.")
                
        elif action == "verify_pos_add_and_update":
            print(f"\n=== [DB Verification] Checking added/updated POS 02 for {test_ms_no} ===")
            
            # Check MMEMBPTB
            cur.execute("SELECT POS_NO, MAC_ADD_IP, ORDER_YN FROM hmsfns.MMEMBPTB WHERE MS_NO = %s AND POS_NO = '02'", (test_ms_no,))
            pos = cur.fetchone()
            if pos:
                print(f"POS in MMEMBPTB: POS {pos[0]}, Mac: {pos[1]}, OrderYN: {pos[2]}")
            else:
                print("[FAIL] POS 02 not found in MMEMBPTB.")
                
            # Check SSMEMPTB
            cur.execute("SELECT COUNT(*) FROM hmsfns.SSMEMPTB WHERE MS_NO = %s AND POS_NO = '02'", (test_ms_no,))
            ss_cnt = cur.fetchone()[0]
            print(f"Sync Records in SSMEMPTB for POS 02: {ss_cnt}")
            
            # Check MMSLOGTB
            cur.execute("SELECT LOG_DATA, LOG_DTIME FROM hmsfns.MMSLOGTB WHERE MS_NO = %s AND LOG_DATA LIKE '%%02|%%' ORDER BY LOG_DTIME DESC LIMIT 1", (test_ms_no,))
            log = cur.fetchone()
            if log:
                print(f"Latest POS log in MMSLOGTB: {log[0]} (Time: {log[1]})")
                
            if pos and ss_cnt > 0:
                print("[SUCCESS] POS Addition and Update trigger verified successfully.")
            else:
                print("[FAIL] POS Trigger check failed.")
                
        elif action == "verify_van_pos_and_card":
            print(f"\n=== [DB Verification] Checking VAN(POS) and Card contract for {test_ms_no} ===")
            
            # Check MVANCOTB (VAN POS)
            cur.execute("SELECT VAN_CD, POS_NO, CAT_ID FROM hmsfns.MVANCOTB WHERE MS_NO = %s AND CAT_ID = '1234567890'", (test_ms_no,))
            van = cur.fetchall()
            print(f"VAN POS Records (TID: 1234567890): {len(van)}")
            for v in van:
                print(f"  VAN Code: {v[0]}, POS: {v[1]}, TID: {v[2]}")
                
            # Check SVANCOTB (VAN transmission)
            cur.execute("SELECT COUNT(*) FROM hmsfns.SVANCOTB WHERE MS_NO = %s AND CAT_ID = '1234567890'", (test_ms_no,))
            svan_cnt = cur.fetchone()[0]
            print(f"Sync Records in SVANCOTB: {svan_cnt}")
            
            # Check MMCARDTB (Card Contract)
            cur.execute("SELECT CARD_CO, MS_CARD_NO FROM hmsfns.MMCARDTB WHERE MS_NO = %s AND CARD_CO = '01'", (test_ms_no,))
            card = cur.fetchone()
            if card:
                print(f"Card contract in MMCARDTB: Card {card[0]}, Contract: {card[1]}")
            else:
                print("[FAIL] Card contract not found in MMCARDTB.")
                
            # Check SSCARDTB (Card transmission)
            cur.execute("SELECT COUNT(*) FROM hmsfns.SSCARDTB WHERE MS_NO = %s AND CARD_CO = '01'", (test_ms_no,))
            ss_cnt = cur.fetchone()[0]
            print(f"Sync Records in SSCARDTB: {ss_cnt}")
            
            if len(van) > 0 and svan_cnt > 0 and card:
                print("[SUCCESS] VAN(POS) and Card Contract Registration trigger verified successfully.")
            else:
                print("[FAIL] VAN/Card trigger check failed.")
                
    except Exception as e:
        print("Error during DB verification:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        check_status(sys.argv[1])
    else:
        check_status("verify_open")
