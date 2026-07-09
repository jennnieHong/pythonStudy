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

async def dismiss_passwords_modal(page):
    print("Force dismissing passwordsModal (password expiration/reset prompt)...")
    await page.evaluate("""() => {
        try {
            if (typeof $ !== 'undefined') {
                $('#passwordsModal').modal('hide');
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
                console.log('Dismissed passwordsModal using jQuery.');
            } else {
                const m = document.getElementById('passwordsModal');
                if (m) m.style.display = 'none';
                const backdrops = document.getElementsByClassName('modal-backdrop');
                for (let b of backdrops) { b.remove(); }
                document.body.classList.remove('modal-open');
                console.log('Dismissed passwordsModal using Vanilla JS.');
            }
        } catch(e) {
            console.error('Error dismissing passwordsModal:', e);
        }
    }""")
    await page.wait_for_timeout(1000)

async def run_test():
    target_user = 'shopbrand'
    
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
            print("\nStarting Playwright (headless=True)...")
            try:
                browser = await p.chromium.launch(headless=False, slow_mo=100)
            except Exception as e:
                print(f"Headed launch failed ({e}), falling back to headless=True...")
                browser = await p.chromium.launch(headless=True, slow_mo=100)
                
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()
            
            page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
            
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
                try:
                    await page.screenshot(path=os.path.join(report_dir, 'st_sales_00021_error.png'))
                except:
                    pass
                return

            print("Login successful. Navigating to st_sales_00021 (매장 POS정산내역)...")
            await page.goto('http://localhost:8080/backoffice/view/main/st/sales/st_sales_00021')
            await page.wait_for_timeout(2000)
            
            await dismiss_passwords_modal(page)
            
            await page.wait_for_selector('#st_sales_00021_t01', timeout=10000)
            print("매장 POS 정산내역 화면이 정상 로딩되었습니다.")
            
            # Set search date
            print("Setting searchDate to '2026-06-02' via JS...")
            await page.evaluate("() => { $('#searchDate').val('2026-06-02'); }")
            
            # Search
            print("Clicking 조회 button...")
            await page.locator('#st_sales_00021_search_btn').click()
            
            # Wait for data table row
            print("Waiting for data table rows to render...")
            await page.wait_for_selector('#st_sales_00021_t01 tbody tr td.table-onclick', timeout=10000)
            
            await page.wait_for_timeout(1000)
            await page.screenshot(path=os.path.join(report_dir, 'st_sales_00021_search.png'))
            print('Screenshot 1 (Search Result) captured.')
            
            # Click the cell (first cell with .table-onclick) to trigger detail modal
            print("Clicking store name cell to trigger detail modal...")
            await page.locator('#st_sales_00021_t01 tbody tr td.table-onclick').first.click(force=True)
            
            # Wait for detail modal to become visible
            print("Waiting for detailSearchModal to open...")
            await page.wait_for_selector('#detailSearchModal', state='visible', timeout=5000)
            
            await page.wait_for_timeout(1000)
            await page.screenshot(path=os.path.join(report_dir, 'st_sales_00021_detail.png'))
            print('Screenshot 2 (Detail Modal) captured.')
            
            # Close modal
            print("Closing detail modal...")
            await page.evaluate("$('#detailSearchModal').modal('hide')")
            await page.wait_for_timeout(500)
            
            # Update Progress JSON
            print('\nUpdating progress json...')
            try:
                progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"screens": {}}
                
                data["screens"]["st_sales_00021"] = {
                    "complete": True,
                    "memo": f"로그인 ID: {target_user} - 매장 POS 정산내역 (매장 권한으로 2026-06-02 정산 내역 및 상세 정산 항목 모달 조회 완료)"
                }
                
                with open(progress_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("Updated progress JSON successfully for st_sales_00021.")
            except Exception as e:
                print(f"[WARNING] Progress update failed: {e}")
                
            print('[SUCCESS] st_sales_00021 E2E test completed successfully.')

    except Exception as e:
        print('Error occurred during E2E test:', e)
        try:
            await page.screenshot(path=os.path.join(report_dir, 'st_sales_00021_error.png'))
        except:
            pass
    finally:
        # DB RESTORE
        print(f"\n[DB RESTORE] Restoring original credentials for {target_user}...")
        query_db(
            "UPDATE hmsfns.MUSERSTB SET PASSWD = %s, LAST_DTIME = %s, FST_LOGIN_PW_CHANGE = %s, ACCT_ENABLE = %s, ACCT_LOCK = %s WHERE USER_ID = %s",
            (backup_data['passwd'], backup_data['last_dtime'], backup_data['fst_login_pw_change'], backup_data['acct_enable'], backup_data['acct_lock'], target_user),
            fetch=False
        )
        print("[DB RESTORE COMPLETE]")

if __name__ == '__main__':
    asyncio.run(run_test())
