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

SCREENSHOT_DIR = r"C:\Users\uoshj\.gemini\antigravity-ide\brain\a6eb74d7-4237-4316-bd5d-fbf2d71150e6"

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

async def perform_login(context, page, username, password_opt):
    print(f'\n--- Logging in as {username} ---')
    print('Clearing cookies...')
    await context.clear_cookies()
    
    passwords = [password_opt, "0000", "0"]
    passwords = list(dict.fromkeys([p for p in passwords if p is not None]))
    
    for pwd in passwords:
        print(f"Trying password: '{pwd}'...")
        await page.goto('http://localhost:8080/backoffice/view/login', timeout=15000)
        await page.wait_for_timeout(1000)
        await page.wait_for_selector('#login_userid', timeout=10000)
        await page.locator('#login_userid').fill(username)
        await page.locator('#login_password').fill(str(pwd))
        
        submit_btn = page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first
        await submit_btn.click()
        
        success = False
        for _ in range(5):
            if 'main' in page.url:
                success = True
                break
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                print('Alert modal detected. Closing it...')
                await bootbox_ok.first.click()
            await page.wait_for_timeout(1000)
            
        if success:
            print(f'Successfully logged in as {username}.')
            return True
        else:
            print(f'Login failed with password {pwd}.')
            
    print(f'[FAIL] Could not log in as {username} with any password.')
    return False

async def accept_bootbox_confirm(page):
    await page.wait_for_timeout(1000)
    bootbox_confirm = page.locator('.bootbox-confirm .bootbox-accept, .bootbox-accept')
    if await bootbox_confirm.count() > 0 and await bootbox_confirm.first.is_visible():
        print("[DIALOG] Clicking confirm button in bootbox...")
        await bootbox_confirm.first.click()
        await page.wait_for_timeout(1500)

async def run_e2e_test():
    # 0. Set up user info (Configure shopadmin store NC0007 as required)
    print("[DB SETUP] Updating shopadmin ms_no to NC0007...")
    query_db("UPDATE hmsfns.MUSERSTB SET MS_NO = 'NC0007' WHERE USER_ID = 'shopadmin'")
    
    try:
        async with async_playwright() as p:
            print("Starting Playwright (headless=False)...")
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()
            
            # 1. Login as shopadmin
            logged_in = await perform_login(context, page, "shopadmin", "0000")
            if not logged_in:
                await browser.close()
                return
                
            # Response listener to inspect Ajax responses
            async def handle_response(response):
                if "updateExtraCostAmt" in response.url or "selectVendor" in response.url:
                    try:
                        text = await response.text()
                        print(f"\n[API RESPONSE] URL: {response.url}\n  STATUS: {response.status}\n  BODY: {text[:500]}")
                    except Exception as e:
                        print(f"[API RESPONSE ERROR] {e}")
            page.on("response", handle_response)
                
            # 2. Navigate to hq_vendor_00008
            url = "http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00008"
            print(f"Navigating to {url}...")
            await page.goto(url)
            await page.wait_for_timeout(2000)
            
            # Screenshot 1: Initial State
            ss_path_1 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00008_1_initial.png")
            await page.screenshot(path=ss_path_1)
            print(f"Saved Screenshot 1 (Initial) to {ss_path_1}")
            
            # 3. Set Date filter to 2026-06-01 ~ 2026-06-30
            print("Setting search date range (2026-06-01 ~ 2026-06-30) inside same month...")
            await page.evaluate("""
                document.getElementById('searchFromDate').value = '2026-06-01';
                document.getElementById('searchEndDate').value = '2026-06-30';
            """)
            await page.wait_for_timeout(500)
            
            # Select store filter just in case
            await page.evaluate("""
                const selectElement = document.querySelector('#com_selectMsNo select');
                if (selectElement) {
                    selectElement.value = 'NC0007';
                    $(selectElement).selectpicker('refresh');
                }
            """)
            await page.wait_for_timeout(500)
            
            # Click search
            print("Clicking search button...")
            await page.click("#hq_vendor_00008_search_btn")
            await page.wait_for_timeout(2000)
            
            # Screenshot 2: Search Results
            ss_path_2 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00008_2_searched.png")
            await page.screenshot(path=ss_path_2)
            print(f"Saved Screenshot 2 (Searched) to {ss_path_2}")
            
            # 4. Select the target row (slip 0003)
            # Select bootstrap table checkbox index 0 (first row returned, which should be slip 0003)
            print("Checking first row in table...")
            await page.locator('input[name="btSelectItem"]').first.check()
            await page.wait_for_timeout(500)
            
            # Input extra cost amount (e.g. 20000)
            print("Filling extraCostAmt input to '20000'...")
            await page.locator("#extraCostAmt").fill("20000")
            await page.wait_for_timeout(500)
            
            # Select process flag (amount-based '0')
            print("Setting process flag to '0' (amount)...")
            await page.evaluate("""
                const procSelect = document.getElementById('com_selectProcFg');
                if (procSelect) {
                    procSelect.value = '0';
                    $(procSelect).selectpicker('refresh');
                }
            """)
            await page.wait_for_timeout(500)
            
            # Apply extra cost
            print("Clicking apply extra cost button...")
            await page.click("#hq_vendor_00008_update_btn")
            await accept_bootbox_confirm(page)
            
            # Wait for reload
            await page.wait_for_timeout(2000)
            
            # Screenshot 3: Applied State
            ss_path_3 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00008_3_applied.png")
            await page.screenshot(path=ss_path_3)
            print(f"Saved Screenshot 3 (Applied) to {ss_path_3}")
            
            # Database Verification
            print("\n[DB CHECK - EXTRA COST APPLIED]")
            obslph_row = query_db("SELECT order_date, ms_no, slip_no, slip_extra_cost_amt, slip_extra_cost_create_date FROM hmsfns.OBSLPHTB WHERE order_date='20260615' AND ms_no='NC0007' AND slip_no='0003'")
            print("  OBSLPHTB:", obslph_row)
            obslpd_rows = query_db("SELECT order_date, line_no, goods_cd, purch_qty, purch_ucost, goods_extra_cost_amt, goods_extra_cost_yn, goods_extra_cost_create_date FROM hmsfns.OBSLPDTB WHERE order_date='20260615' AND ms_no='NC0007' AND slip_no='0003'")
            print("  OBSLPDTB:")
            for r in obslpd_rows:
                print("    ->", r)
                
            # Trigger cascade check (Depth 3 check: IMTRLGTB & obslplog)
            print("\n[DB CHECK - TRIGGER CASCADE (Depth 3)]")
            imtrlg_recs = query_db("SELECT COUNT(*) FROM hmsfns.IMTRLGTB WHERE KEY_BILL_NO LIKE '20260615NC00070003%'")
            obslplog_recs = query_db("SELECT COUNT(*) FROM hmsfns.obslplog WHERE MS_NO = 'NC0007' AND ORDER_DATE = '20260615'")
            print("  IMTRLGTB count (expected 0 because proc_fg = 4 but no state transition U occurred):", imtrlg_recs[0]['count'] if imtrlg_recs else 0)
            print("  obslplog count (expected 0):", obslplog_recs[0]['count'] if obslplog_recs else 0)

            await browser.close()
            print("\nE2E Playwright test and validation finished.")
            
    finally:
        # Restore user info
        print("[DB CLEANUP] Restoring shopadmin ms_no to NC0002...")
        query_db("UPDATE hmsfns.MUSERSTB SET MS_NO = 'NC0002' WHERE USER_ID = 'shopadmin'")

if __name__ == '__main__':
    asyncio.run(run_e2e_test())
