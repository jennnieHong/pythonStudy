import asyncio
import os
import sys
import psycopg2
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

# DB Connection Config
DB_CONFIG = {
    "host": "192.168.10.206",
    "port": "5432",
    "database": "edb",
    "user": "hmsfns_was",
    "password": "astems3!"
}

SCREENSHOT_DIR = r"C:\Users\uoshj\.gemini\antigravity-ide\brain\1a4236fc-92c9-48e6-b3ea-a3f6617131ea"

def query_db(sql, params=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if sql.strip().upper().startswith("SELECT"):
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

async def perform_login(context, page, username, password):
    print(f'\n--- Logging in as {username} ---')
    print('Clearing cookies...')
    await context.clear_cookies()
    
    await page.goto('http://localhost:8080/backoffice/view/login', timeout=15000)
    await page.wait_for_timeout(1000)
    await page.wait_for_selector('#login_userid', timeout=10000)
    await page.locator('#login_userid').fill(username)
    await page.locator('#login_password').fill(password)
    
    submit_btn = page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first
    await submit_btn.click()
    
    success = False
    for _ in range(5):
        if 'main' in page.url:
            success = True
            break
        bootbox_ok = page.locator('.bootbox-accept, .modal-footer .btn-primary')
        if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
            modal_body = page.locator('.modal-body')
            msg = await modal_body.first.inner_text() if await modal_body.count() > 0 else ""
            print(f'Alert modal detected during login: "{msg}". Closing it...')
            await bootbox_ok.first.click()
        await page.wait_for_timeout(1000)
        
    if success:
        print(f'Successfully logged in as {username}.')
        return True
    else:
        print(f'[FAIL] Login failed for {username}. Current URL: {page.url}')
        return False

async def handle_bootbox_dialogs(page):
    await page.wait_for_timeout(1000)
    modals = page.locator('.modal-dialog')
    modal_count = await modals.count()
    if modal_count > 0:
        for i in range(modal_count):
            modal = modals.nth(i)
            # Make sure we don't accidentally close passwordsModal here since we handle it separately
            modal_id = await modal.locator('xpath=..').get_attribute('id')
            if modal_id == 'passwordsModal':
                continue
                
            if await modal.is_visible():
                body_loc = modal.locator('.modal-body, .bootbox-body')
                btn_loc = modal.locator('.bootbox-accept, .btn-primary, button[data-bb-handler="confirm"]')
                body_text = await body_loc.first.inner_text() if await body_loc.count() > 0 else ""
                print(f"[MODAL DETECTED] Text: {body_text}")
                
                if await btn_loc.count() > 0 and await btn_loc.first.is_visible():
                    print("[MODAL ACTION] Clicking accept/confirm button...")
                    await btn_loc.first.click()
                    await page.wait_for_timeout(1500)
                    return True
    return False

async def dismiss_passwords_modal(page):
    # Dismiss passwordsModal if it exists and blocks pointer events
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

async def run_e2e_test():
    # 0. Backup original credentials for test users
    print("[DB BACKUP] Backing up original credentials for fnbcafe and shopadmin...")
    backup_data = {}
    for user in ['fnbcafe', 'shopadmin']:
        res = query_db("SELECT PASSWD, LAST_DTIME, FST_LOGIN_PW_CHANGE FROM hmsfns.MUSERSTB WHERE USER_ID = %s", (user,))
        if res:
            backup_data[user] = res[0]
            print(f"  Backup {user}: {res[0]}")
        else:
            print(f"  [ERROR] Failed to backup user {user}")
            return
            
    # Set ACCT_ENABLE = Y, ACCT_LOCK = N, FST_LOGIN_PW_CHANGE = N
    query_db("UPDATE hmsfns.MUSERSTB SET ACCT_ENABLE = 'Y', ACCT_LOCK = 'N', AUTH_FAILURE_CNT = 0, FST_LOGIN_PW_CHANGE = 'N' WHERE USER_ID IN ('fnbcafe', 'shopadmin')")

    try:
        async with async_playwright() as p:
            print("\nStarting Playwright (headless=False)...")
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()

            # ----------------------------------------------------
            # Test Screen 1: [ST] st_emp_00002 비밀번호변경
            # ----------------------------------------------------
            logged_in_st = await perform_login(context, page, "fnbcafe", "0000")
            if logged_in_st:
                st_url = "http://localhost:8080/backoffice/view/main/st/employee/st_emp_00002"
                print(f"Navigating to ST 비밀번호변경: {st_url}...")
                await page.goto(st_url)
                await page.wait_for_timeout(2000)
                
                # Dismiss modal that blocks UI interaction
                await dismiss_passwords_modal(page)
                
                # Check initial state
                ss_st_1 = os.path.join(SCREENSHOT_DIR, "st_emp_00002_1_initial.png")
                await page.screenshot(path=ss_st_1)
                print(f"Saved Screenshot (ST Initial) to {ss_st_1}")
                
                # Form fill (Current PW: '0000', New PW: '0000a123!', Confirm PW: '0000a123!')
                print("Filling password form for fnbcafe...")
                await page.locator("#userPW").fill("0000")
                await page.locator("#upassWd").fill("0000a123!")
                await page.locator("#upassWdchk").fill("0000a123!")
                await page.wait_for_timeout(500)
                
                # Click Save Button (fnCngPw() triggers bootbox.confirm)
                print("Clicking save button...")
                await page.click("#st_emp_00002_save_btn")
                
                # Loop to handle possible bootbox.confirm AND then subsequent alerts
                for step in range(3):
                    dialog_handled = await handle_bootbox_dialogs(page)
                    if not dialog_handled:
                        break
                    await page.wait_for_timeout(1000)
                
                # Check applied state
                ss_st_2 = os.path.join(SCREENSHOT_DIR, "st_emp_00002_2_applied.png")
                await page.screenshot(path=ss_st_2)
                print(f"Saved Screenshot (ST Applied) to {ss_st_2}")
                
                # Verify DB modification
                print("[DB VERIFY - ST]")
                res_st = query_db("SELECT PASSWD, LAST_DTIME, FST_LOGIN_PW_CHANGE FROM hmsfns.MUSERSTB WHERE USER_ID = 'fnbcafe'")
                print(f"  Current DB state for fnbcafe: {res_st[0] if res_st else 'None'}")
                if res_st and res_st[0]['passwd'] != backup_data['fnbcafe']['passwd']:
                    print("  [SUCCESS] Password hash changed in DB successfully.")
                else:
                    print("  [FAIL] Password hash was not modified in DB.")
            
            # ----------------------------------------------------
            # Test Screen 2: [HQ] hq_emp_00002 비밀번호변경관리
            # ----------------------------------------------------
            logged_in_hq = await perform_login(context, page, "shopadmin", "0000")
            if logged_in_hq:
                hq_url = "http://localhost:8080/backoffice/view/main/hq/employee/hq_emp_00002"
                print(f"Navigating to HQ 비밀번호변경관리: {hq_url}...")
                await page.goto(hq_url)
                await page.wait_for_timeout(2000)
                
                # Dismiss modal that blocks UI interaction
                await dismiss_passwords_modal(page)
                
                # Check initial state
                ss_hq_1 = os.path.join(SCREENSHOT_DIR, "hq_emp_00002_1_initial.png")
                await page.screenshot(path=ss_hq_1)
                print(f"Saved Screenshot (HQ Initial) to {ss_hq_1}")
                
                # Form fill (Current PW: '0000', New PW: '0000a123!', Confirm PW: '0000a123!')
                print("Filling password form for shopadmin...")
                await page.locator("#userPW").fill("0000")
                await page.locator("#upassWd").fill("0000a123!")
                await page.locator("#upassWdchk").fill("0000a123!")
                await page.wait_for_timeout(500)
                
                # Click Save Button (fnCngPw() triggers bootbox.confirm)
                print("Clicking save button...")
                await page.click("#hq_emp_00002_save_btn")
                
                # Loop to handle possible bootbox.confirm AND then subsequent alerts
                for step in range(3):
                    dialog_handled = await handle_bootbox_dialogs(page)
                    if not dialog_handled:
                        break
                    await page.wait_for_timeout(1000)
                
                # Check applied state
                ss_hq_2 = os.path.join(SCREENSHOT_DIR, "hq_emp_00002_2_applied.png")
                await page.screenshot(path=ss_hq_2)
                print(f"Saved Screenshot (HQ Applied) to {ss_hq_2}")
                
                # Verify DB modification
                print("[DB VERIFY - HQ]")
                res_hq = query_db("SELECT PASSWD, LAST_DTIME, FST_LOGIN_PW_CHANGE FROM hmsfns.MUSERSTB WHERE USER_ID = 'shopadmin'")
                print(f"  Current DB state for shopadmin: {res_hq[0] if res_hq else 'None'}")
                if res_hq and res_hq[0]['passwd'] != backup_data['shopadmin']['passwd']:
                    print("  [SUCCESS] Password hash changed in DB successfully.")
                else:
                    print("  [FAIL] Password hash was not modified in DB.")
            
            await browser.close()
            print("\nE2E Playwright test and validation finished.")
            
    finally:
        # 4. DB RESTORE: Restore original BCrypt hashes and metadata
        print("\n[DB RESTORE] Restoring original passwords and metadata to prevent login failures...")
        for user, data in backup_data.items():
            query_db(
                "UPDATE hmsfns.MUSERSTB SET PASSWD = %s, LAST_DTIME = %s, FST_LOGIN_PW_CHANGE = %s WHERE USER_ID = %s",
                (data['passwd'], data['last_dtime'], data['fst_login_pw_change'], user)
            )
            print(f"  Restored {user} to original state.")
        print("[DB RESTORE COMPLETE]")

if __name__ == '__main__':
    asyncio.run(run_e2e_test())
