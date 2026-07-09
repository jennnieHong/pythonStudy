import asyncio
import os
import sys
import json
import psycopg2
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

report_dir = r"D:\hmTest\backoffice\QaReport"
if not os.path.exists(report_dir):
    os.makedirs(report_dir)

# Create a temporary dummy file to upload
dummy_file_path = os.path.join(report_dir, "qa_test_file.txt")
with open(dummy_file_path, "w", encoding="utf-8") as f:
    f.write("This is a temporary dummy file generated for Automated QA E2E Testing of Notice Board File Upload.")

DB_CONFIG = {
    "host": "192.168.10.206",
    "port": "5432",
    "database": "edb",
    "user": "hmsfns_was",
    "password": "astems3!"
}

def query_db(sql, params=None, fetch=True):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if fetch:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            result = cursor.rowcount
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"[DB ERROR] Failed to execute query: {sql}. Error: {e}")
        return None

async def dismiss_modal(page, modal_id):
    await page.evaluate(f"""() => {{
        try {{
            if (typeof $ !== 'undefined') {{
                $('#{modal_id}').modal('hide');
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
            }} else {{
                const m = document.getElementById('{modal_id}');
                if (m) m.style.display = 'none';
                const backdrops = document.getElementsByClassName('modal-backdrop');
                for (let b of backdrops) {{ b.remove(); }}
                document.body.classList.remove('modal-open');
            }}
        }} catch(e) {{}}
    }}""")
    await page.wait_for_timeout(500)

async def run_test():
    target_user = 'fnbadmin'
    
    print(f"[DB BACKUP] Backing up credentials for {target_user}...")
    res = query_db("SELECT PASSWD, LAST_DTIME, FST_LOGIN_PW_CHANGE, ACCT_ENABLE, ACCT_LOCK FROM hmsfns.MUSERSTB WHERE USER_ID = %s", (target_user,))
    if res:
        backup_data = res[0]
        print(f"  Backup state: {backup_data}")
    else:
        print(f"  [ERROR] Failed to backup user {target_user}")
        return
        
    query_db(
        "UPDATE hmsfns.MUSERSTB SET PASSWD = %s, ACCT_ENABLE = 'Y', ACCT_LOCK = 'N', AUTH_FAILURE_CNT = 0, FST_LOGIN_PW_CHANGE = 'Y' WHERE USER_ID = %s",
        ('$2a$10$uJZY4u/YPOGVTb/QYpvQ/OGpS9CkmFUWFKLomdmSrCOsPZWWQEg6i', target_user), # hash for '0000'
        fetch=False
    )
    print("Temporary credentials set in DB.")

    try:
        async with async_playwright() as p:
            print("\nStarting Playwright...")
            try:
                try:
                    browser = await p.chromium.launch(headless=False, slow_mo=100)
                except Exception as e:
                    print(f"Headed launch failed ({e}), falling back to headless=True...")
                    browser = await p.chromium.launch(headless=True, slow_mo=100)
                    
                context = await browser.new_context(viewport={"width": 1280, "height": 800})
                page = await context.new_page()
                
                # 1. Force logout
                print('Forcing logout to clear session...')
                await page.goto('http://localhost:8080/backoffice/logout')
                await page.wait_for_timeout(1000)
                
                # 2. Go to login
                print('Navigating to login page...')
                await page.goto('http://localhost:8080/backoffice', timeout=15000)
                await page.wait_for_selector('#login_userid', timeout=10000)
                
                # 3. Login
                print(f'Logging in as {target_user}...')
                await page.locator('#login_userid').fill(target_user)
                await page.locator('#login_password').fill('0000')
                await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
                
                # 4. Wait for redirection with bootbox handling
                print('Waiting for redirection to main...')
                success = False
                for _ in range(15):
                    if 'main' in page.url:
                        success = True
                        break
                    bootbox_ok = page.locator('.bootbox-accept, .modal-footer .btn-primary')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        print("Duplicate login or alert modal detected. Clicking accept...")
                        await bootbox_ok.first.click()
                    await page.wait_for_timeout(1000)
                    
                if not success:
                    print(f"[FAIL] Redirection failed. Current URL: {page.url}")
                    return
 
                print("Login successful. Navigating to hq_commu_00002 (공지사항 등록 관리)...")
                await page.goto('http://localhost:8080/backoffice/view/main/hq/communication/hq_commu_00002')
                await page.wait_for_timeout(2000)
                await dismiss_modal(page, 'passwordsModal')
                
                # Check grid load
                await page.wait_for_selector('#hq_commu_00002_t01', timeout=10000)
                print("공지사항 등록 관리 화면 정상 로드 확인.")
                
                # Clean up existing test notices from DB
                query_db("DELETE FROM hmsfns.BBSNTUTB WHERE IDX IN (SELECT IDX FROM hmsfns.BBSNTCTB WHERE TITLE = 'Auto QA Notice')", fetch=False)
                query_db("DELETE FROM hmsfns.BBSNTCTB WHERE TITLE = 'Auto QA Notice'", fetch=False)
                print("Cleaned up existing test data from DB.")
                
                # 1. Click 새 글쓰기 button
                print("Clicking 새 글쓰기 button...")
                await page.locator('#hq_commu_00002_edit_btn').click()
                await page.wait_for_timeout(1000)
                
                # 2. Fill form in 새 글쓰기 모달
                print("Filling form to write a new notice...")
                
                # Populate dates via datepicker setDate
                await page.evaluate("""() => {
                    $('#searchFromDate').datepicker('setDate', new Date());
                    let nextWeek = new Date();
                    nextWeek.setDate(nextWeek.getDate() + 7);
                    $('#searchEndDate').datepicker('setDate', nextWeek);
                }""")
                await page.wait_for_timeout(500)
                
                # Title
                await page.locator('#nTitle').fill('Auto QA Notice')
                
                # Summernote content
                await page.evaluate("""() => {
                    $('#summernote-insert-notice').summernote('code', '<p>This notice is created by Playwright Automated E2E QA Test.</p>');
                }""")
                await page.wait_for_timeout(500)
                
                # Attach file
                print(f"Selecting attachment file: {dummy_file_path}")
                await page.locator('#files-insert-notice').set_input_files(dummy_file_path)
                await page.wait_for_timeout(1000)
                
                # 3. Save
                print("Clicking 등록 button...")
                await page.locator('#divSaveBtnArea button.modal-footer-btn').first.click()
                await page.wait_for_timeout(1500)
                
                # Accept confirmation dialog
                confirm_btn = page.locator('button:has-text("OK"), button:has-text("확인"), .bootbox-accept')
                if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                    print("Confirm dialog detected. Clicking '확인'...")
                    await confirm_btn.first.click()
                await page.wait_for_timeout(4000) # Wait for Ajax save and file upload to finish
                
                # Check DB for Notice and File
                print("Checking DB to verify notice insertion...")
                notice_db = query_db("SELECT IDX FROM hmsfns.BBSNTCTB WHERE TITLE = 'Auto QA Notice'")
                if not notice_db:
                    raise Exception("[FAIL] Notice was not inserted into hmsfns.BBSNTCTB.")
                
                notice_idx = notice_db[0]['idx']
                print(f"[SUCCESS] Notice inserted into DB. IDX = {notice_idx}")
                
                print("Checking DB to verify attachment file upload...")
                file_db = query_db("SELECT FILE_IDX, FILE_NM FROM hmsfns.BBSNTUTB WHERE IDX = %s", (str(notice_idx),))
                if not file_db:
                    raise Exception("[FAIL] Attachment was not uploaded or bound to notice in hmsfns.BBSNTUTB.")
                
                print(f"[SUCCESS] Attachment verified in DB: {file_db}")
                
                # 4. Search registered notice in UI
                print("Searching registered notice in grid...")
                await page.locator('#searchTerms').select_option(value='0') # Title
                await page.locator('#searchContents').fill('Auto QA Notice')
                await page.locator('#hq_commu_00002_search_btn').click()
                await page.wait_for_timeout(1500)
                
                # Check grid row exists
                row_selector = '#hq_commu_00002_t01 tbody tr td.table-onclick:has-text("Auto QA Notice")'
                await page.wait_for_selector(row_selector, timeout=5000)
                print("[SUCCESS] Registered notice exists in search results grid.")
                
                # Take screenshot of search result
                screenshot_path = os.path.join(report_dir, 'hq_commu_00002_search.png')
                await page.screenshot(path=screenshot_path)
                print(f'Search result screenshot captured at: {screenshot_path}')
                
                # 5. Click on the Title cell to open detail
                print("Opening detail modal for cleanup...")
                await page.locator('#hq_commu_00002_t01 tbody tr td.table-onclick').first.click()
                await page.wait_for_timeout(2000)
                
                # Click 삭제 button inside detail modal (hq_commu_00002_M03)
                print("Clicking 삭제 button in detail modal...")
                await page.locator('button:has-text("삭제"), .modal-footer button[onclick="fn_deleteNotice();"]').first.click()
                await page.wait_for_timeout(1000)
                
                # Accept delete confirm
                confirm_btn = page.locator('button:has-text("OK"), button:has-text("확인"), .bootbox-accept')
                if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                    print("Delete confirm dialog detected. Clicking '확인'...")
                    await confirm_btn.first.click()
                await page.wait_for_timeout(2000)
                
                # DB verify final cascade deletion
                remain_notice = query_db("SELECT 1 FROM hmsfns.BBSNTCTB WHERE IDX = %s", (notice_idx,))
                remain_file = query_db("SELECT 1 FROM hmsfns.BBSNTUTB WHERE IDX = %s", (str(notice_idx),))
                print(f"Notice Exist: {bool(remain_notice)}, Attachment Exist: {bool(remain_file)}")
                if not remain_notice and not remain_file:
                    print("[SUCCESS] Cascade cleanup completed successfully.")
                else:
                    print("[WARNING] Cascade cleanup did not fully delete data.")
                
                print('[SUCCESS] hq_commu_00002 E2E test completed successfully.')

            except Exception as e:
                print('Error occurred during E2E test:', e)
                try:
                    await page.screenshot(path=os.path.join(report_dir, 'hq_commu_00002_error.png'))
                    print("Captured error screenshot: hq_commu_00002_error.png")
                except Exception as se:
                    print("Failed to capture error screenshot:", se)
            finally:
                if 'browser' in locals() or 'browser' in globals():
                    await browser.close()
    finally:
        # DB RESTORE USER CREDENTIALS
        print(f"\n[DB RESTORE] Restoring original credentials for {target_user}...")
        query_db(
            "UPDATE hmsfns.MUSERSTB SET PASSWD = %s, LAST_DTIME = %s, FST_LOGIN_PW_CHANGE = %s, ACCT_ENABLE = %s, ACCT_LOCK = %s WHERE USER_ID = %s",
            (backup_data['passwd'], backup_data['last_dtime'], backup_data['fst_login_pw_change'], backup_data['acct_enable'], backup_data['acct_lock'], target_user),
            fetch=False
        )
        print("[DB RESTORE COMPLETE]")
        
        # Remove dummy file
        if os.path.exists(dummy_file_path):
            os.remove(dummy_file_path)

if __name__ == '__main__':
    asyncio.run(run_test())
