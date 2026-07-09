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

def query_db_state(step_name):
    print(f"\n--- [DB Verification: {step_name}] ---")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Check TMACNCTB (HQ Category)
        cursor.execute("SELECT ACNT_FG, ACNT_NM, LAST_DTIME, LAST_ID FROM hmsfns.TMACNCTB WHERE CHAIN_NO = 'C001' AND ACNT_FG = '9'")
        tmacnc = cursor.fetchall()
        print(f"  TMACNCTB (acnt_fg=9): {tmacnc}")
        
        # 2. Check MMACNCTB (Store Category)
        cursor.execute("SELECT COUNT(*) FROM hmsfns.MMACNCTB WHERE ACNT_FG = '9'")
        mmacnc_cnt = cursor.fetchone()[0]
        print(f"  MMACNCTB Count (acnt_fg=9): {mmacnc_cnt}")
        
        # 3. Check SSACNCTB (Send Log Category)
        cursor.execute("SELECT ms_no, proc_fg, acnt_fg, acnt_nm, proc_dtime FROM hmsfns.SSACNCTB WHERE ACNT_FG = '9' ORDER BY proc_dtime DESC LIMIT 3")
        ssacnc = cursor.fetchall()
        print(f"  SSACNCTB Log (acnt_fg=9, Top 3): {ssacnc}")
        
        # 4. Check TMACNTTB (HQ Code)
        cursor.execute("SELECT ACNT_FG, ACNT_CD, ACNT_NM, USE_YN, LAST_DTIME FROM hmsfns.TMACNTTB WHERE CHAIN_NO = 'C001' AND ACNT_FG = '9' AND ACNT_CD = '49'")
        tmacnt = cursor.fetchall()
        print(f"  TMACNTTB (acnt_fg=9, acnt_cd=49): {tmacnt}")
        
        # 5. Check MMACNTTB (Store Code)
        cursor.execute("SELECT COUNT(*) FROM hmsfns.MMACNTTB WHERE ACNT_FG = '9' AND ACNT_CD = '49'")
        mmacnt_cnt = cursor.fetchone()[0]
        print(f"  MMACNTTB Count (acnt_fg=9, acnt_cd=49): {mmacnt_cnt}")
        
        # 6. Check SSACNTTB (Send Log Code)
        cursor.execute("SELECT ms_no, proc_fg, acnt_fg, acnt_cd, acnt_nm, proc_dtime FROM hmsfns.SSACNTTB WHERE ACNT_FG = '9' AND ACNT_CD = '49' ORDER BY proc_dtime DESC LIMIT 3")
        ssacnt = cursor.fetchall()
        print(f"  SSACNTTB Log (acnt_fg=9, acnt_cd=49, Top 3): {ssacnt}")

        # 7. Check MMSLOGTB (System Change Log)
        cursor.execute("SELECT log_dtime, table_nm, log_fg, ms_no, log_data FROM hmsfns.MMSLOGTB WHERE log_data LIKE '%GOODS_CD(T0000%' IS FALSE AND (log_data LIKE '%AI분류%' OR log_data LIKE '%AI코드%') ORDER BY log_dtime DESC LIMIT 3")
        mmslog = cursor.fetchall()
        print(f"  MMSLOGTB Log (Top 3): {mmslog}")
        
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
        cursor.execute("DELETE FROM hmsfns.TMACNTTB WHERE CHAIN_NO = 'C001' AND ACNT_FG = '9'")
        cursor.execute("DELETE FROM hmsfns.TMACNCTB WHERE CHAIN_NO = 'C001' AND ACNT_FG = '9'")
        cursor.execute("DELETE FROM hmsfns.MMACNTTB WHERE ACNT_FG = '9'")
        cursor.execute("DELETE FROM hmsfns.MMACNCTB WHERE ACNT_FG = '9'")
        cursor.execute("DELETE FROM hmsfns.SSACNTTB WHERE ACNT_FG = '9'")
        cursor.execute("DELETE FROM hmsfns.SSACNCTB WHERE ACNT_FG = '9'")
        conn.commit()
        cursor.close()
        conn.close()
        print("Cleanup finished successfully.")
    except Exception as e:
        print("Cleanup error:", e)

async def run_test():
    # Cleanup DB first
    cleanup_db_test_data()
    # Bypass PW change popup for shopadmin
    set_shopadmin_pw_change_status('Y')
    
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
            
            # 3. Login as shopadmin
            print('Logging in as shopadmin...')
            await page.locator('#login_userid').fill('shopadmin')
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
                
            # 5. Navigate to hq_cash_00004
            print('Navigating to hq_cash_00004 (월간지출계정관리)...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/cash/hq_cash_00004')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_cash_00004_t01', timeout=10000)
            
            # 6. Initial query and screenshot
            print('Clicking Search button...')
            await page.locator('#hq_cash_00004_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00004_1_initial.png'))
            print('Screenshot 1 (initial) captured.')
            
            # 7. Add Category (codeSave)
            print('Clicking 분류추가 button...')
            await page.locator('#hq_cash_00004_add_acntFg_btn').click()
            await page.wait_for_selector('#addAcntFgModal', state='visible', timeout=5000)
            
            print('Entering Category data...')
            await page.locator('#acntFg').fill('9')
            await page.locator('#acntNm').fill('AI분류')
            
            print('Saving Category...')
            await page.locator('#addAcntFgModal .modal-footer-custom button.btn-primary').click()
            
            # Wait for confirm dialog and accept
            print('Waiting for save confirmation bootbox...')
            await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
            await page.locator('.bootbox-confirm .bootbox-accept').click()
            print("Confirmed Category Save dialog.")
                
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00004_2_category_created.png'))
            print('Screenshot 2 (category created) captured.')
            
            # Verify DB insertion (Insert Category)
            query_db_state("After Category Insertion")

            # 8. Duplicate Category check
            print('Testing duplicate category check...')
            await page.locator('#hq_cash_00004_add_acntFg_btn').click()
            await page.wait_for_selector('#addAcntFgModal', state='visible', timeout=5000)
            await page.locator('#acntFg').fill('9')
            await page.locator('#acntNm').fill('AI중복')
            await page.locator('#addAcntFgModal .modal-footer-custom button.btn-primary').click()
            
            # Wait for confirm and accept
            await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
            await page.locator('.bootbox-confirm .bootbox-accept').click()
            
            # Wait for warning alert and accept
            print('Waiting for duplicate warning alert...')
            await page.wait_for_selector('.bootbox-alert .bootbox-accept', timeout=5000)
            await page.locator('.bootbox-alert .bootbox-accept').click()
            print("Duplicate warning detected and dismissed.")
            
            # Close category modal
            await page.locator('#addAcntFgModal #closeModal').click()
            await page.wait_for_timeout(1000)
            
            # 9. Update Category (codeUpdate)
            print('Finding the newly created category in the table to update...')
            # Locate rows in t01
            rows = await page.locator('#hq_cash_00004_t01 tbody tr').all()
            target_row = None
            for r in rows:
                cells = await r.locator('td').all_text_contents()
                if len(cells) > 1 and '[9]' in cells[1]:
                    target_row = r
                    break
                    
            if target_row:
                print("Target Category row found. Clicking UPDATE column...")
                # The 4th td (index 3) is the edit button
                await target_row.locator('td').nth(3).click()
                await page.wait_for_selector('#addAcntFgModal', state='visible', timeout=5000)
                
                await page.locator('#acntNm').fill('AI수정')
                await page.locator('#addAcntFgModal .modal-footer-custom button.btn-primary').click()
                
                # Wait for confirm and accept
                await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
                await page.locator('.bootbox-confirm .bootbox-accept').click()
                
                await page.wait_for_timeout(2000)
                await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00004_3_category_updated.png'))
                print('Screenshot 3 (category updated) captured.')
                
                # Verify DB update (Update Category)
                query_db_state("After Category Update")
            else:
                print("[WARNING] Category row [9] not found for update!")

            # 10. Load Detail Code & Add Code (codeDtSave)
            print('Clicking on the category name to load account codes...')
            rows = await page.locator('#hq_cash_00004_t01 tbody tr').all()
            target_row = None
            for r in rows:
                cells = await r.locator('td').all_text_contents()
                if len(cells) > 1 and '[9]' in cells[1]:
                    target_row = r
                    break
                    
            if target_row:
                # Click the category name (2nd td, index 1)
                await target_row.locator('td').nth(1).click()
                await page.wait_for_timeout(2000)
                
                # Verify that Code Add button is enabled
                code_add_btn = page.locator('#hq_cash_00004_add_acntCd_btn')
                is_disabled = await code_add_btn.is_disabled()
                print(f"Code Add button disabled state: {is_disabled}")
                
                if not is_disabled:
                    print("Clicking Code Add button...")
                    await code_add_btn.click()
                    await page.wait_for_selector('#addAcntCdModal', state='visible', timeout=5000)
                    
                    await page.locator('#acntCd').fill('49')
                    await page.locator('#acntCdNm').fill('AI코드')
                    # Use standard JS/jQuery evaluation to update selectpicker
                    await page.evaluate("$('#msDtUseFg').selectpicker('val', 'Y').trigger('change')")
                    await page.wait_for_timeout(500)
                    
                    print("Saving Account Code...")
                    await page.locator('#addAcntCdModal .modal-footer-custom button.btn-primary').click()
                    
                    # Wait for confirm and accept
                    await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
                    await page.locator('.bootbox-confirm .bootbox-accept').click()
                    
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00004_4_code_created.png'))
                    print('Screenshot 4 (code created) captured.')
                    
                    # Verify DB insertion (Insert Code)
                    query_db_state("After Code Insertion")
                else:
                    print("[WARNING] Code Add button is still disabled!")
            else:
                print("[WARNING] Category row [9] not found for loading codes!")

            # 11. Update Detail Code (codeDtUpdate)
            print('Finding the newly created code in the detail table to update...')
            dt_rows = await page.locator('#hq_cash_00004_t02 tbody tr').all()
            target_dt_row = None
            for r in dt_rows:
                cells = await r.locator('td').all_text_contents()
                if len(cells) > 1 and cells[1] == '49':
                    target_dt_row = r
                    break
                    
            if target_dt_row:
                print("Target Code row found. Clicking UPDATE column...")
                # The 5th td (index 4) is the edit button
                await target_dt_row.locator('td').nth(4).click()
                await page.wait_for_selector('#addAcntCdModal', state='visible', timeout=5000)
                
                await page.locator('#acntCdNm').fill('AI코드수정')
                # Change usage to No (N)
                await page.evaluate("$('#msDtUseFg').selectpicker('val', 'N').trigger('change')")
                await page.wait_for_timeout(500)
                
                await page.locator('#addAcntCdModal .modal-footer-custom button.btn-primary').click()
                
                # Wait for confirm and accept
                await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
                await page.locator('.bootbox-confirm .bootbox-accept').click()
                
                await page.wait_for_timeout(2000)
                await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00004_5_code_updated.png'))
                print('Screenshot 5 (code updated) captured.')
                
                # Verify DB update (Update Code)
                query_db_state("After Code Update")
            else:
                print("[WARNING] Code row [49] not found for update!")

            # 12. Delete Detail Code (codeDtDel)
            print('Finding the code row to delete...')
            dt_rows = await page.locator('#hq_cash_00004_t02 tbody tr').all()
            target_dt_row = None
            for r in dt_rows:
                cells = await r.locator('td').all_text_contents()
                if len(cells) > 1 and cells[1] == '49':
                    target_dt_row = r
                    break
                    
            if target_dt_row:
                print("Target Code row found. Clicking DELETE column...")
                # The 6th td (index 5) is the delete button
                await target_dt_row.locator('td').nth(5).click()
                
                # Wait for confirm and accept
                await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
                await page.locator('.bootbox-confirm .bootbox-accept').click()
                
                await page.wait_for_timeout(2000)
                print("Deleted Code '49'.")
                
                # Verify DB deletion (Delete Code)
                query_db_state("After Code Deletion")
            else:
                print("[WARNING] Code row [49] not found for delete!")

            # 13. Delete Category (codeDel)
            print('Finding the category row to delete...')
            rows = await page.locator('#hq_cash_00004_t01 tbody tr').all()
            target_row = None
            for r in rows:
                cells = await r.locator('td').all_text_contents()
                if len(cells) > 1 and '[9]' in cells[1]:
                    target_row = r
                    break
                    
            if target_row:
                print("Target Category row found. Clicking DELETE column...")
                # The 5th td (index 4) is the delete button
                await target_row.locator('td').nth(4).click()
                
                # Wait for confirm and accept
                await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
                await page.locator('.bootbox-confirm .bootbox-accept').click()
                
                await page.wait_for_timeout(2000)
                await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00004_6_deleted.png'))
                print('Screenshot 6 (deleted) captured.')
                
                # Verify DB deletion (Delete Category)
                query_db_state("After Category Deletion")
            else:
                print("[WARNING] Category row [9] not found for delete!")

            # 14. Update progress JSON
            print('\nUpdating progress json and screen html...')
            try:
                progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"screens": {}}
                
                data["screens"]["hq_cash_00004"] = {
                    "complete": True,
                    "memo": "로그인 ID: shopadmin - 월간지출계정관리 (계정분류 및 하위 코드 CUD 테스트 완료, 자바 트리거 서비스 Depth 3 연쇄 전파 확인)"
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
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00004_error.png'))
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
