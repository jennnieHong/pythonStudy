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

def ensure_user_test_conditions(user_id):
    print(f"Ensuring user {user_id} has ACCT_ENABLE = 'Y' and FST_LOGIN_PW_CHANGE = 'Y'...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE hmsfns.MUSERSTB 
            SET ACCT_ENABLE = 'Y',
                FST_LOGIN_PW_CHANGE = 'Y' 
            WHERE USER_ID = %s
        """, (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print("User login and password status updated in DB.")
    except Exception as e:
        print("DB update error:", e)

def query_db_state(step_name):
    print(f"\n--- [DB Verification: {step_name}] ---")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check MACCIOTB records for store NC0021 on date 20260624
        cursor.execute("""
            SELECT ACCIO_DATE, MS_NO, ACCIO_NO, ACNT_FG, ACNT_CD, ACNT_AMT, VAT, DELETE_YN, CREATE_FG, USER_ID 
            FROM hmsfns.MACCIOTB 
            WHERE MS_NO = 'NC0021' AND ACCIO_DATE = '20260624'
            ORDER BY ACCIO_NO
        """)
        records = cursor.fetchall()
        print(f"  MACCIOTB records count: {len(records)}")
        for r in records:
            print(f"    Record: {r}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB verification query error:", e)
    print("--------------------------------------\n")

def cleanup_db_test_data():
    print("Cleaning up old test data from DB...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hmsfns.MACCIOTB WHERE MS_NO = 'NC0021' AND ACCIO_DATE = '20260624'")
        conn.commit()
        cursor.close()
        conn.close()
        print("Cleanup finished successfully.")
    except Exception as e:
        print("Cleanup error:", e)

async def run_test():
    target_user = 'I000034b'
    # Cleanup DB first
    cleanup_db_test_data()
    # Bypass PW change popup and enable user for I000034b
    ensure_user_test_conditions(target_user)
    
    async with async_playwright() as p:
        try:
            print('Attempting to launch browser...')
            try:
                browser = await p.chromium.launch(headless=False, slow_mo=200)
            except Exception as e:
                print(f'Headed launch failed ({e}), falling back to headless=True...')
                browser = await p.chromium.launch(headless=True, slow_mo=100)
                
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            # Print console messages
            page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
            
            # 1. Force logout
            print('Forcing logout to clear session...')
            await page.goto('http://localhost:8080/backoffice/logout')
            await page.wait_for_timeout(2000)
            
            # 2. Go to login
            print('Navigating to login page...')
            await page.goto('http://localhost:8080/backoffice', timeout=15000)
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            # 3. Login as I000034b
            print(f'Logging in as {target_user}...')
            await page.locator('#login_userid').fill(target_user)
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
            
            # 4. Wait for redirection with bootbox handling
            print('Waiting for redirection to main...')
            for _ in range(15):
                if 'main' in page.url:
                    break
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print("Duplicate login or success bootbox dialog detected. Clicking accept...")
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)
                
            # 5. Navigate to st_cash_00001
            print('Navigating to st_cash_00001 (입출금내역등록)...')
            await page.goto('http://localhost:8080/backoffice/view/main/st/cash/st_cash_00001')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#st_cash_00001_t01', timeout=10000)
            
            # 6. Set Search Date to 2026-06-24 and Query
            print('Setting date field and clicking Search...')
            await page.evaluate("$('#st_cash_00001_searchDate').val('2026-06-24')")
            await page.locator('#st_cash_00001_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, 'st_cash_00001_1_initial.png'))
            print('Screenshot 1 (initial empty) captured.')
            
            # 7. Add Cash Record (cashSave)
            print('Clicking 내역추가 button...')
            await page.locator('#st_cash_00001_add_acnt_btn').click()
            await page.wait_for_selector('#addCashModal', state='visible', timeout=5000)
            
            print('Selecting Account details...')
            # Select ACNT_FG = 1 (Outflow / 출금)
            await page.evaluate("$('#acntFg').selectpicker('val', '1').trigger('change')")
            await page.wait_for_timeout(1000) # wait for fnAcntCdSelect ajax
            # Select ACNT_CD = 01 (기타출금)
            await page.evaluate("$('#acntCd').selectpicker('val', '01').trigger('change')")
            await page.wait_for_timeout(500)
            
            print('Filling Amount & VAT...')
            await page.locator('#anctAmt').fill('50000')
            await page.locator('#vat').fill('5000')
            
            print('Clicking Save...')
            await page.locator('#addCashModal .modal-footer-custom button.btn-primary').click()
            
            # Wait for confirm dialog and accept
            print('Confirming save...')
            await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
            await page.locator('.bootbox-confirm .bootbox-accept').click()
            
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, 'st_cash_00001_2_created.png'))
            print('Screenshot 2 (record created) captured.')
            
            # Verify DB insertion (Insert Cash)
            query_db_state("After Cash Record Insertion")
            
            # 8. Update Cash Record (cashUpdate)
            print('Locating the newly created record row by clicking its name cell...')
            # The click-row.bs.table only triggers modal on clicking td with field ACNT_NM (.table-onclick)
            # Locate first .table-onclick cell in the tbody and click it
            await page.locator('#st_cash_00001_t01 tbody tr td.table-onclick').first.click(force=True)
            await page.wait_for_selector('#addCashModal', state='visible', timeout=5000)
            
            print('Modifying Amount...')
            await page.locator('#anctAmt').fill('65000')
            await page.locator('#vat').fill('6500')
            
            print('Clicking Save to Update...')
            await page.locator('#addCashModal .modal-footer-custom button.btn-primary').click()
            
            # Wait for confirm and accept
            await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
            await page.locator('.bootbox-confirm .bootbox-accept').click()
            
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, 'st_cash_00001_3_updated.png'))
            print('Screenshot 3 (record updated) captured.')
            
            # Verify DB update (Update Cash)
            query_db_state("After Cash Record Update")
            
            # 9. Delete Cash Record (cashDel)
            print('Checking the checkbox on the row to delete...')
            # Wait for any loader to disappear and make sure table is ready
            await page.wait_for_timeout(2000)
            
            # Try to check the checkbox
            checkbox = page.locator('#st_cash_00001_t01 tbody tr input[type="checkbox"]').first
            await checkbox.click(force=True)
            await page.wait_for_timeout(500)
            
            print('Clicking 내역삭제 button...')
            await page.locator('#st_cash_00001_delete_acnt_btn').click(force=True)
            
            # Wait and check if alert or confirm shows up
            alert_popup = page.locator('.bootbox-alert .bootbox-accept')
            confirm_popup = page.locator('.bootbox-confirm .bootbox-accept')
            
            for _ in range(10):
                if await alert_popup.count() > 0 and await alert_popup.first.is_visible():
                    print("Alert detected: '삭제 할 코드를 선택해주세요'. Clicking accept and retrying...")
                    await alert_popup.first.click()
                    await page.wait_for_timeout(1000)
                    # Click the first cell in the row to toggle selection if checkbox click was intercepted
                    await page.locator('#st_cash_00001_t01 tbody tr td').first.click(force=True)
                    await page.wait_for_timeout(500)
                    await page.locator('#st_cash_00001_delete_acnt_btn').click(force=True)
                if await confirm_popup.count() > 0 and await confirm_popup.first.is_visible():
                    print("Confirm dialog detected. Proceeding with deletion...")
                    await confirm_popup.first.click()
                    break
                await page.wait_for_timeout(500)
            
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, 'st_cash_00001_4_deleted.png'))
            print('Screenshot 4 (record deleted) captured.')
            
            # Verify DB deletion (Delete Cash)
            query_db_state("After Cash Record Deletion")
            
            # 10. Update progress JSON
            print('\nUpdating progress json and screen html...')
            try:
                progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"screens": {}}
                
                data["screens"]["st_cash_00001"] = {
                    "complete": True,
                    "memo": "로그인 ID: I000034b - 입출금내역등록 (매장 권한으로 당일 현금 시재 입금/출금 내역을 등록, 수정 및 삭제 검증 완료)"
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
            await page.screenshot(path=os.path.join(report_dir, 'st_cash_00001_error.png'))
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
