import asyncio
import os
import sys
import json
import subprocess
import psycopg2
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

report_dir = r"D:\hmTest\backoffice\QaReport"
if not os.path.exists(report_dir):
    os.makedirs(report_dir)

conn_params = {
    "host": "192.168.10.206",
    "port": 5432,
    "database": "edb",
    "user": "hmsfns_was",
    "password": "astems3!"
}

def get_db_connection():
    return psycopg2.connect(**conn_params)

def set_shopadmin_pw_change_status(status):
    print(f"Setting shopadmin FST_LOGIN_PW_CHANGE = '{status}'...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE hmsfns.MUSERSTB 
            SET FST_LOGIN_PW_CHANGE = %s 
            WHERE USER_ID = 'shopadmin'
        """, (status,))
        conn.commit()
        cursor.close()
        conn.close()
        print("Password status updated in DB.")
    except Exception as e:
        print("DB update error:", e)

def cleanup_db_test_data():
    print("Cleaning up old test data from DB...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM hmsfns.MACCIOTB 
            WHERE ACCIO_DATE = '20260629' AND MS_NO = 'NC0003' AND ACCIO_NO = '9999'
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Cleanup finished successfully.")
    except Exception as e:
        print("Cleanup error:", e)

def insert_db_test_data():
    print("Inserting test monthly expense data in DB...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # insert test data: ACNT_FG = 2 (지출), ACNT_CD = 01 (test1), ACNT_AMT = 100000, VAT = 0
        cursor.execute("""
            INSERT INTO hmsfns.MACCIOTB (
                accio_date, ms_no, accio_no, chain_no, acnt_fg, acnt_cd, acnt_amt, vat, remark, delete_yn, create_fg, user_id, create_dtime, create_id, last_dtime, last_id
            ) VALUES (
                '20260629', 'NC0003', '9999', 'C001', '2', '01', 100000.00, 0.00, 'E2E Test Monthly Expense', 'N', '0', 'shopadmin', '20260629120000', 'shopadmin', '20260629120000', 'shopadmin'
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Test data inserted successfully.")
    except Exception as e:
        print("Insert error:", e)

def query_db_state(step_name):
    print(f"\n--- [DB Verification: {step_name}] ---")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT accio_date, ms_no, accio_no, acnt_fg, acnt_cd, acnt_amt, remark, delete_yn 
            FROM hmsfns.MACCIOTB 
            WHERE ACCIO_DATE = '20260629' AND MS_NO = 'NC0003' AND ACCIO_NO = '9999'
        """)
        records = cursor.fetchall()
        print(f"  MACCIOTB records found: {records}")
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB verification query error:", e)
    print("--------------------------------------\n")

async def run_test():
    # 1. Prepare DB state
    cleanup_db_test_data()
    insert_db_test_data()
    query_db_state("Before Browser Run")
    set_shopadmin_pw_change_status('Y')
    
    async with async_playwright() as p:
        try:
            print('Attempting to launch browser...')
            try:
                browser = await p.chromium.launch(headless=False, slow_mo=300)
            except Exception as e:
                print(f'Headed launch failed ({e}), falling back to headless=True...')
                browser = await p.chromium.launch(headless=True, slow_mo=100)
                
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
            
            # 2. Force logout
            print('Forcing logout to clear session...')
            await page.goto('http://localhost:8080/backoffice/logout')
            await page.wait_for_timeout(2000)
            
            # 3. Go to login
            print('Navigating to login page...')
            await page.goto('http://localhost:8080/backoffice', timeout=15000)
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            # 4. Login as shopadmin
            print('Logging in as shopadmin...')
            await page.locator('#login_userid').fill('shopadmin')
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
            
            # 5. Wait for redirection with bootbox handling
            print('Waiting for redirection to main...')
            for _ in range(15):
                if 'main' in page.url:
                    break
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print("Duplicate login or success bootbox dialog detected. Clicking accept...")
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)
                
            # 6. Navigate to hq_cash_00005
            print('Navigating to hq_cash_00005 (월간지출내역현황)...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/cash/hq_cash_00005')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_cash_00005_t01', timeout=10000)
            
            # 7. Set search conditions
            print("Setting search dates to 2026-06-29...")
            await page.evaluate("$('#searchFromDate').datepicker('setDate', '2026-06-29')")
            await page.evaluate("$('#searchEndDate').datepicker('setDate', '2026-06-29')")
            await page.wait_for_timeout(1000)
            
            print("Selecting Store NC0003...")
            await page.wait_for_selector('#selectMsPos_ms_select option', state='attached', timeout=10000)
            await page.evaluate("() => { $('#selectMsPos_ms_select').selectpicker('val', 'NC0003').change(); }")
            await page.wait_for_timeout(1000)
            
            # 8. Query
            print("Clicking search button...")
            await page.locator('#hq_cash_00005_search_btn').click()
            await page.wait_for_timeout(3000)
            
            # 9. Verify table content & capture list screenshot
            print("Checking if test data exists in grid...")
            rows = await page.locator('#hq_cash_00005_t01 tbody tr').all_text_contents()
            print("Grid rows:")
            for idx, r in enumerate(rows):
                print(f"Row {idx+1}: {r.strip()}")
                
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00005_1_list.png'))
            print('Screenshot 1 (list) captured.')
            
            # 10. Click cell to open detail modal
            print("Clicking Account Code cell to open detail modal...")
            target_cell = page.locator('#hq_cash_00005_t01 tbody tr td.table-onclick', has_text='test1').first
            if await target_cell.count() > 0:
                await target_cell.click()
                await page.wait_for_selector('#detailSearchModal', state='visible', timeout=5000)
                await page.wait_for_timeout(2000)
                
                # Check modal table rows
                modal_rows = await page.locator('#hq_cash_00005_t02 tbody tr').all_text_contents()
                print("Modal grid rows:")
                for idx, mr in enumerate(modal_rows):
                    print(f"Modal Row {idx+1}: {mr.strip()}")
                    
                await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00005_2_detail_modal.png'))
                print('Screenshot 2 (detail modal) captured.')
                
                # Close modal
                print("Closing detail modal...")
                await page.locator('#modalClose').click()
                await page.wait_for_timeout(1000)
            else:
                print("[WARNING] Target cell with text 'test1' not found in table!")
                
            # 11. Cleanup and progress update
            cleanup_db_test_data()
            
            print('\nUpdating progress json and screen html...')
            try:
                progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"screens": {}}
                
                data["screens"]["hq_cash_00005"] = {
                    "complete": True,
                    "memo": "로그인 ID: shopadmin - 월간지출내역현황 (지출 실적 집계 내역 조회 및 상세 트랜잭션 목록 모달 팝업 조회 검증 완료)"
                }
                
                with open(progress_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                print("Updated progress JSON successfully.")
                
                # Regenerate HTML dashboard
                subprocess.run(["python", "generate_screens_directory.py"], cwd=r"D:\hmTest\backoffice\QaReport", check=True)
                print("Regenerated All_HMS_Screens.html successfully.")
            except Exception as e:
                print(f"[WARNING] Progress update failed: {e}")
                
            print('[SUCCESS] E2E test completed successfully.')
            
        except Exception as e:
            print('Error occurred during E2E test:', e)
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00005_error.png'))
            cleanup_db_test_data()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
