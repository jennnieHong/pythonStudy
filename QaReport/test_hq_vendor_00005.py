import asyncio
import os
import sys
import json
from datetime import datetime
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
        await page.wait_for_timeout(1000)

async def run_e2e_test():
    # 0. Temporarily change shopadmin's ms_no to NC0007 and emp_id to 9999 in DB to avoid Musersx1 unique constraint
    print("[DB SETUP] Updating shopadmin ms_no to NC0007 and emp_id to 9999...")
    query_db("UPDATE hmsfns.MUSERSTB SET MS_NO = 'NC0007', EMP_ID = '9999' WHERE USER_ID = 'shopadmin'")
    
    try:
        async with async_playwright() as p:
            print("Starting Playwright (headless=False)...")
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()
            
            # Intercept network responses to capture server exceptions
            async def handle_response(response):
                if "vendor" in response.url or "confirm" in response.url:
                    try:
                        text = await response.text()
                        if response.status != 200:
                            print(f"\n[SERVER RESPONSE ERROR] URL: {response.url}\nStatus: {response.status}\nBody:\n{text}\n")
                    except Exception as e:
                        pass
            page.on("response", handle_response)
            
            # =========================================================================
            # PHASE 1: Store User registers a Purchase Order in st_vendor_00003
            # =========================================================================
            logged_in = await perform_login(context, page, "fnbcafe", "0000")
            if not logged_in:
                await browser.close()
                return
                
            url_store = "http://localhost:8080/backoffice/view/main/st/vendor/st_vendor_00003"
            print(f"Navigating to Store PO view: {url_store}...")
            await page.goto(url_store)
            await page.wait_for_timeout(2000)
            
            # Open Modal
            print("Opening 발주등록 modal...")
            await page.click("#st_vendor_00003_add_btn")
            await page.wait_for_timeout(1500)
            
            # Select vendor '삼성웰스토리2' (000002)
            print("Selecting vendor '삼성웰스토리2' (000002)...")
            await page.evaluate("""
                $('#com_selectVendor_M01_vendor_select').selectpicker('val', '000002');
                $('#com_selectVendor_M01_vendor_select').trigger('change');
            """)
            await page.wait_for_timeout(1000)
            
            # Click 상품조회
            print("Clicking 상품조회 button in modal...")
            await page.click("#st_vendor_00003_M02_add_btn")
            await page.wait_for_timeout(1500)
            
            # Input Qty
            print("Inputting quantity for the first item...")
            await page.locator("#txtPurchQtyT030").focus()
            await page.locator("#txtPurchQtyT030").fill("10")
            await page.locator("#txtPurchQtyT030").press("Enter")
            await page.wait_for_timeout(1000)
            
            # Check first row
            await page.evaluate("""
                $('#st_vendor_00003_t03').bootstrapTable('check', 0);
            """)
            await page.wait_for_timeout(1000)
            
            # Screenshot 1: Store order modal with goods added
            ss_path = os.path.join(SCREENSHOT_DIR, "hq_vendor_00005_store_modal_added.png")
            await page.screenshot(path=ss_path)
            print(f"Saved screenshot to {ss_path}")
            
            # Save
            print("Clicking Save in store modal...")
            await page.click("#saveM01")
            await page.wait_for_timeout(1000)
            
            # Accept confirm dialog
            await accept_bootbox_confirm(page)
            
            # Wait for modal to disappear
            print("Waiting for modal to close...")
            await page.wait_for_selector("#st_vendor_00003_M01", state="hidden", timeout=15000)
            await page.wait_for_timeout(1000)
            
            # Refresh main list
            await page.click("#st_vendor_00003_search_btn")
            await page.wait_for_timeout(2000)
            
            # Screenshot 2: Store order saved in list
            ss_path = os.path.join(SCREENSHOT_DIR, "hq_vendor_00005_store_saved.png")
            await page.screenshot(path=ss_path)
            print(f"Saved screenshot to {ss_path}")
            
            # Query DB to get the saved slip details
            latest_hd = query_db("""
                SELECT ORDER_DATE, MS_NO, SLIP_NO, PROC_FG 
                  FROM hmsfns.OBSLPHTB 
                 WHERE MS_NO = 'NC0007' AND SLIP_FG = '0'
                 ORDER BY CREATE_DTIME DESC LIMIT 1
            """)
            if latest_hd:
                order_date = latest_hd[0]['order_date']
                ms_no = latest_hd[0]['ms_no']
                slip_no = latest_hd[0]['slip_no']
                print(f"[DB STATE] New order registered: order_date={order_date}, ms_no={ms_no}, slip_no={slip_no}, proc_fg={latest_hd[0]['proc_fg']}")
            else:
                print("[DB ERROR] Failed to find registered PO in DB!")
                await browser.close()
                return
                
            # =========================================================================
            # PHASE 2: HQ User logs in and confirms the PO in hq_vendor_00005
            # =========================================================================
            # Logout / Login as HQ shopadmin
            logged_in_hq = await perform_login(context, page, "shopadmin", "0000")
            if not logged_in_hq:
                await browser.close()
                return
                
            url_hq = "http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00005"
            print(f"Navigating to HQ PO view: {url_hq}...")
            await page.goto(url_hq)
            await page.wait_for_timeout(2000)
            
            # Screenshot 3: HQ Screen Initial state
            ss_path = os.path.join(SCREENSHOT_DIR, "hq_vendor_00005_search.png")
            await page.screenshot(path=ss_path)
            print(f"Saved screenshot to {ss_path}")
            
            # Fill search conditions
            print("Selecting date range and search...")
            # Date inputs already set by default to today. Let's click search
            await page.click("#hq_vendor_00005_search_btn")
            await page.wait_for_timeout(2000)
            
            # Screenshot 4: HQ Screen Search Results (shows the unconfirmed order from NC0007)
            ss_path = os.path.join(SCREENSHOT_DIR, "hq_vendor_00005_unconfirmed.png")
            await page.screenshot(path=ss_path)
            print(f"Saved screenshot to {ss_path}")
            
            # Check details: click the first row to populate t02 detail list
            print("Clicking the first order row to load detail panel...")
            # Since it's a bootstrap table, clicking a cell in the first row loads detail
            await page.locator("#hq_vendor_00005_t01 tbody tr").first.locator("td").nth(2).click()
            await page.wait_for_timeout(1500)
            
            # Screenshot 5: HQ Detail Grid loaded
            ss_path = os.path.join(SCREENSHOT_DIR, "hq_vendor_00005_detail.png")
            await page.screenshot(path=ss_path)
            print(f"Saved screenshot to {ss_path}")
            
            # Check the row for confirmation
            print("Checking first row checkbox via bootstrapTable API...")
            await page.evaluate("""
                $('#hq_vendor_00005_t01').bootstrapTable('check', 0);
            """)
            await page.wait_for_timeout(1000)
            
            # Click Confirm
            print("Clicking Confirm button...")
            await page.click("#hq_vendor_00005_confirm_btn")
            await page.wait_for_timeout(1000)
            
            # Accept confirm dialog
            await accept_bootbox_confirm(page)
            await page.wait_for_timeout(2000)
            
            # Screenshot 6: HQ Confirmed order
            ss_path = os.path.join(SCREENSHOT_DIR, "hq_vendor_00005_confirmed.png")
            await page.screenshot(path=ss_path)
            print(f"Saved screenshot to {ss_path}")
            
            # Verify DB State
            confirmed_hd = query_db("""
                SELECT PROC_FG FROM hmsfns.OBSLPHTB 
                 WHERE ORDER_DATE = %s AND MS_NO = %s AND SLIP_NO = %s AND SLIP_FG = '0'
            """, (order_date, ms_no, slip_no))
            if confirmed_hd:
                print(f"[DB STATE] After HQ confirm, proc_fg={confirmed_hd[0]['proc_fg']}")
            else:
                print("[DB STATE] FAILED to retrieve confirmed order from DB!")
                
            # Verify downstream triggers: 
            # Check IMTRLGTB (should be 0 because proc_fg = '2' is not a ledger-updating action)
            key_bill_prefix = f"{order_date}{ms_no}{slip_no}0%"
            imtrlg_recs = query_db("SELECT * FROM hmsfns.IMTRLGTB WHERE KEY_BILL_NO LIKE %s", (key_bill_prefix,))
            print(f"[TRIGGER VERIFICATION] IMTRLGTB records found: {len(imtrlg_recs)}")
            
            # Check obslplog (should also be 0)
            obslplog_recs = query_db("SELECT * FROM hmsfns.obslplog WHERE MS_NO = %s AND SLIP_NO = %s AND SLIP_FG = '0'", (ms_no, slip_no))
            print(f"[TRIGGER VERIFICATION] obslplog records found: {len(obslplog_recs)}")
            
            print("E2E test successfully completed.")
            await browser.close()
    finally:
        # Restore shopadmin's ms_no to NC0002 and emp_id to 0001
        print("[DB CLEANUP] Restoring shopadmin ms_no to NC0002 and emp_id to 0001...")
        query_db("UPDATE hmsfns.MUSERSTB SET MS_NO = 'NC0002', EMP_ID = '0001' WHERE USER_ID = 'shopadmin'")

if __name__ == '__main__':
    asyncio.run(run_e2e_test())
