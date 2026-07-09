import asyncio
import os
import sys
import json
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
    # 0. Set up user info
    print("[DB SETUP] Updating shopadmin ms_no to NC0007 and emp_id to 9999...")
    query_db("UPDATE hmsfns.MUSERSTB SET MS_NO = 'NC0007', EMP_ID = '9999' WHERE USER_ID = 'shopadmin'")
    
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
                
            # 2. Navigate to hq_vendor_00002
            url = "http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00002"
            print(f"Navigating to {url}...")
            await page.goto(url)
            await page.wait_for_timeout(2000)
            
            # Screenshot 1: Initial State
            ss_path_1 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00002_1_initial.png")
            await page.screenshot(path=ss_path_1)
            print(f"Saved Screenshot 1 (Initial) to {ss_path_1}")
            
            # 3. Set Date filter to 2026-06-18 (evaluation)
            print("Setting search date to 2026-06-18...")
            await page.evaluate("""
                document.getElementById('searchFromDate').value = '2026-06-18';
                document.getElementById('searchEndDate').value = '2026-06-18';
            """)
            await page.wait_for_timeout(500)
            
            # Click search
            print("Clicking search button...")
            await page.click("#hq_vendor_00002_search_btn")
            await page.wait_for_timeout(2000)
            
            # Screenshot 2: Search Results
            ss_path_2 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00002_2_searched.png")
            await page.screenshot(path=ss_path_2)
            print(f"Saved Screenshot 2 (Searched) to {ss_path_2}")
            
            # 4. Modify quantity/price and Save
            print("Modifying first item supplyQty to 5.0 and purchUnitPrc to 25000.0...")
            await page.evaluate("""
                const qtyInput = document.getElementById('requestQty_240201000701_T0000011');
                const prcInput = document.getElementById('requestUnitPrc_240201000701_T0000011');
                if (qtyInput && prcInput) {
                    qtyInput.value = '5.0';
                    prcInput.value = '25000.0';
                    // Trigger keyup to calculate amt
                    qtyInput.dispatchEvent(new Event('keyup'));
                }
            """)
            await page.wait_for_timeout(500)
            
            # Select first item row checkbox (Bootstrap table checkbox, index 0 is first row)
            print("Checking first row in table...")
            await page.locator('input[name="btSelectItem"]').first.check()
            await page.wait_for_timeout(500)
            
            print("Clicking save request button...")
            await page.click("#hq_vendor_00002_saveRequest_btn")
            await accept_bootbox_confirm(page)
            
            # Screenshot 3: Saved State
            ss_path_3 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00002_3_saved.png")
            await page.screenshot(path=ss_path_3)
            print(f"Saved Screenshot 3 (Saved) to {ss_path_3}")
            
            # 5. Perform 품의처리 (confirmRequest)
            # Select headerCheck checkbox (전표 레벨 체크)
            print("Checking the headerCheck for 240201000701...")
            await page.check("#headerCheck_240201000701_5")
            await page.wait_for_timeout(500)
            
            print("Clicking confirm request (품의처리) button...")
            await page.click("#hq_vendor_00002_confirmRequest_btn")
            await accept_bootbox_confirm(page)
            
            # Screenshot 4: Confirmed State
            ss_path_4 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00002_4_confirmed.png")
            await page.screenshot(path=ss_path_4)
            print(f"Saved Screenshot 4 (Confirmed) to {ss_path_4}")
            
            # 6. Perform 품의취소 (cancelRequest)
            print("Checking the headerCheck for confirmed전표...")
            await page.check("#headerCheck_240201000701_1")
            await page.wait_for_timeout(500)
            
            print("Clicking cancel request (품의취소) button...")
            await page.click("#hq_vendor_00002_cancelRequest_btn")
            await accept_bootbox_confirm(page)
            
            # Screenshot 5: Canceled State
            ss_path_5 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00002_5_canceled.png")
            await page.screenshot(path=ss_path_5)
            print(f"Saved Screenshot 5 (Canceled) to {ss_path_5}")
            
            # 7. Confirm again to proceed to supply confirm
            print("Checking the headerCheck for canceled전표...")
            await page.check("#headerCheck_240201000701_2")
            await page.wait_for_timeout(500)
            
            print("Clicking confirm request button again...")
            await page.click("#hq_vendor_00002_confirmRequest_btn")
            await accept_bootbox_confirm(page)
            
            # 8. Perform 발주확정 (confirmSupply)
            print("Checking the headerCheck for confirmed전표 to perform 발주확정...")
            await page.check("#headerCheck_240201000701_1")
            await page.wait_for_timeout(500)
            
            print("Clicking confirm supply (발주확정) button...")
            await page.click("#hq_vendor_00002_confirmSupply_btn")
            await accept_bootbox_confirm(page)
            
            # Screenshot 6: Supply Confirmed State
            ss_path_6 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00002_6_supply_confirmed.png")
            await page.screenshot(path=ss_path_6)
            print(f"Saved Screenshot 6 (Supply Confirmed) to {ss_path_6}")
            
            # Database check inside confirm block
            print("\n[DB CHECK - SUPPLY CONFIRMED]")
            obslph_row = query_db("SELECT order_date, ms_no, slip_no, purch_req_no, proc_fg FROM hmsfns.OBSLPHTB WHERE purch_req_no = '240201000701'")
            print("  OBSLPHTB:", obslph_row)
            obslpd_rows = query_db("SELECT order_date, line_no, goods_cd, order_qty, order_ucost, order_amt, fictitious_vat, fictitious_vat_amt FROM hmsfns.OBSLPDTB WHERE purch_req_no = '240201000701'")
            print("  OBSLPDTB:")
            for r in obslpd_rows:
                print("    ->", r)
                
            # 9. Perform 발주취소 (cancelSupply)
            print("Checking the headerCheck for supply confirmed전표 to perform 발주취소...")
            await page.check("#headerCheck_240201000701_3")
            await page.wait_for_timeout(500)
            
            print("Clicking cancel supply (발주취소) button...")
            await page.click("#hq_vendor_00002_cancelSupply_btn")
            await accept_bootbox_confirm(page)
            
            # Screenshot 7: Supply Canceled State
            ss_path_7 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00002_7_supply_canceled.png")
            await page.screenshot(path=ss_path_7)
            print(f"Saved Screenshot 7 (Supply Canceled) to {ss_path_7}")
            
            # Database check after cancel supply
            print("\n[DB CHECK - SUPPLY CANCELED]")
            obslph_row_cancelled = query_db("SELECT count(*) FROM hmsfns.OBSLPHTB WHERE purch_req_no = '240201000701'")
            obslpd_rows_cancelled = query_db("SELECT count(*) FROM hmsfns.OBSLPDTB WHERE purch_req_no = '240201000701'")
            print("  OBSLPHTB count (expected 0):", obslph_row_cancelled[0]['count'] if obslph_row_cancelled else 0)
            print("  OBSLPDTB count (expected 0):", obslpd_rows_cancelled[0]['count'] if obslpd_rows_cancelled else 0)
            
            # 10. Check downstream tables for 수불 배제
            print("\n[DB CHECK - DOWNSTREAM TABLES]")
            imtrlg_recs = query_db("SELECT COUNT(*) FROM hmsfns.IMTRLGTB WHERE KEY_BILL_NO LIKE '260618NC0007%%'")
            obslplog_recs = query_db("SELECT COUNT(*) FROM hmsfns.obslplog WHERE MS_NO = 'NC0007' AND ORDER_DATE = '260618'")
            print("  Downstream IMTRLGTB count (expected 0):", imtrlg_recs[0]['count'] if imtrlg_recs else 0)
            print("  Downstream obslplog count (expected 0):", obslplog_recs[0]['count'] if obslplog_recs else 0)

            await browser.close()
            print("\nE2E Playwright test and validation finished.")
            
    finally:
        # Restore user info
        print("[DB CLEANUP] Restoring shopadmin ms_no to NC0002 and emp_id to 0001...")
        query_db("UPDATE hmsfns.MUSERSTB SET MS_NO = 'NC0002', EMP_ID = '0001' WHERE USER_ID = 'shopadmin'")

if __name__ == '__main__':
    asyncio.run(run_e2e_test())
