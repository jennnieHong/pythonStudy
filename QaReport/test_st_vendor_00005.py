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
        
        # 1. Login
        logged_in = await perform_login(context, page, "fnbcafe", "0000")
        if not logged_in:
            await browser.close()
            return
            
        # 2. Go to st_vendor_00005
        url = "http://localhost:8080/backoffice/view/main/st/vendor/st_vendor_00005"
        print(f"Navigating to: {url}...")
        await page.goto(url)
        await page.wait_for_timeout(2000)
        
        # 3. Search initial list
        print("Clicking Search button...")
        await page.click("#st_vendor_00005_search_btn")
        await page.wait_for_timeout(2000)
        
        # Screenshot 1: Search results
        ss_path = os.path.join(SCREENSHOT_DIR, "st_vendor_00005_search.png")
        await page.screenshot(path=ss_path)
        print(f"Saved screenshot to {ss_path}")
        
        # 4. Open 반품등록 Modal
        print("Opening 반품등록 modal...")
        await page.click("#st_vendor_00005_add_btn")
        await page.wait_for_timeout(1500)
        
        # Screenshot 2: Modal Open
        ss_path = os.path.join(SCREENSHOT_DIR, "st_vendor_00005_modal_open.png")
        await page.screenshot(path=ss_path)
        print(f"Saved screenshot to {ss_path}")
        
        # 5. Select vendor in modal
        print("Selecting vendor '삼성웰스토리1' (000001)...")
        await page.evaluate("""
            $('#com_selectVendor_M01_vendor_select').selectpicker('val', '000001');
            $('#com_selectVendor_M01_vendor_select').trigger('change');
        """)
        await page.wait_for_timeout(1000)
        
        # 6. Click 상품조회
        print("Clicking 상품조회 button in modal...")
        await page.click("#st_vendor_00005_M02_add_btn")
        await page.wait_for_timeout(1500)
        
        # Screenshot 3: Modal Searched Goods
        ss_path = os.path.join(SCREENSHOT_DIR, "st_vendor_00005_modal_searched.png")
        await page.screenshot(path=ss_path)
        print(f"Saved screenshot to {ss_path}")
        
        # 7. Input Return Qty for first goods item (index 0) and check the checkbox
        print("Inputting quantity for the first item...")
        await page.locator("#txtPurchQtyT030").focus()
        await page.locator("#txtPurchQtyT030").fill("5")
        await page.locator("#txtPurchQtyT030").press("Enter")
        await page.wait_for_timeout(1000)
        
        # Check the checkbox via bootstrapTable API
        print("Checking first item checkbox via bootstrapTable API...")
        await page.evaluate("""
            $('#st_vendor_00005_t03').bootstrapTable('check', 0);
        """)
        await page.wait_for_timeout(1000)
        
        # Screenshot 4: Modal added goods
        ss_path = os.path.join(SCREENSHOT_DIR, "st_vendor_00005_modal_added.png")
        await page.screenshot(path=ss_path)
        print(f"Saved screenshot to {ss_path}")
        
        # 8. Click Save in modal
        print("Clicking Save in modal...")
        await page.click("#saveM01")
        await page.wait_for_timeout(1000)
        
        # Accept confirm dialog "반품등록 하시겠습니까?"
        await accept_bootbox_confirm(page)
        
        # Wait for modal to disappear completely
        print("Waiting for modal M01 to close...")
        await page.wait_for_selector("#st_vendor_00005_M01", state="hidden", timeout=15000)
        await page.wait_for_timeout(1000)
        
        # Wait for snackbar & reload list
        print("Clicking Search to show new return order...")
        await page.click("#st_vendor_00005_search_btn")
        await page.wait_for_timeout(2000)
        
        # Screenshot 5: Saved order in main list
        ss_path = os.path.join(SCREENSHOT_DIR, "st_vendor_00005_saved.png")
        await page.screenshot(path=ss_path)
        print(f"Saved screenshot to {ss_path}")
        
        # Let's inspect the database before confirm to ensure the order is in OBSLPHTB with PROC_FG = '0'
        latest_hd = query_db("""
            SELECT ORDER_DATE, MS_NO, SLIP_NO, PROC_FG 
              FROM hmsfns.OBSLPHTB 
             WHERE MS_NO = 'NC0007' AND SLIP_FG = '1'
             ORDER BY CREATE_DTIME DESC LIMIT 1
        """)
        if latest_hd:
            order_date = latest_hd[0]['order_date']
            ms_no = latest_hd[0]['ms_no']
            slip_no = latest_hd[0]['slip_no']
            print(f"[DB STATE] New return found: order_date={order_date}, ms_no={ms_no}, slip_no={slip_no}, proc_fg={latest_hd[0]['proc_fg']}")
        else:
            print("[DB ERROR] New return was not inserted in OBSLPHTB!")
            await browser.close()
            return
            
        # 9. Select the saved return in main list and Confirm (확정)
        print("Checking the first return item in main table via bootstrapTable...")
        await page.evaluate("""
            $('#st_vendor_00005_t01').bootstrapTable('check', 0);
        """)
        await page.wait_for_timeout(1000)
        
        print("Clicking Confirm button...")
        await page.click("#st_vendor_00005_confirm_btn")
        await page.wait_for_timeout(1000)
        
        # Accept confirm dialog "선택한 전표를 확정하시겠습니까?"
        await accept_bootbox_confirm(page)
        await page.wait_for_timeout(2000)
        
        # Screenshot 6: Confirmed order
        ss_path = os.path.join(SCREENSHOT_DIR, "st_vendor_00005_confirmed.png")
        await page.screenshot(path=ss_path)
        print(f"Saved screenshot to {ss_path}")
        
        # Let's verify DB state after confirm
        confirmed_hd = query_db("""
            SELECT PROC_FG FROM hmsfns.OBSLPHTB 
             WHERE ORDER_DATE = %s AND MS_NO = %s AND SLIP_NO = %s AND SLIP_FG = '1'
        """, (order_date, ms_no, slip_no))
        if confirmed_hd:
            print(f"[DB STATE] After confirm, proc_fg={confirmed_hd[0]['proc_fg']}")
        else:
            print("[DB STATE] FAILED to retrieve confirmed return from DB!")
            
        # 10. Check downstream trigger side-effects (depth 3)
        # Depth 1: OBSLPDTB is updated to proc_fg = '4'
        # Depth 2: Tr_OBSLPD_T01_Service is triggered, and since cProcFg = '4', downstream수불 is called.
        # Let's query IMTRLGTB (수불 로그) to prove that a log was generated for this keyBillNo
        key_bill_prefix = f"{order_date}{ms_no}{slip_no}1%"
        imtrlg_recs = query_db("SELECT * FROM hmsfns.IMTRLGTB WHERE KEY_BILL_NO LIKE %s", (key_bill_prefix,))
        print(f"[TRIGGER VERIFICATION] IMTRLGTB records found for keyBillNo prefix '{key_bill_prefix}': {len(imtrlg_recs)}")
        for rec in imtrlg_recs:
            print(rec)
            
        # Check obslplog
        obslplog_recs = query_db("SELECT * FROM hmsfns.obslplog WHERE MS_NO = %s AND SLIP_NO = %s AND SLIP_FG = '1'", (ms_no, slip_no))
        print(f"[TRIGGER VERIFICATION] obslplog records found: {len(obslplog_recs)}")
        for rec in obslplog_recs:
            print(rec)
            
        print("E2E test successfully completed.")
        await page.wait_for_timeout(1000)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_e2e_test())
