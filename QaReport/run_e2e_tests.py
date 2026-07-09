import asyncio
import os
import sys
import json
import subprocess
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

def update_screens_progress_memo(screen_id, login_id, description):
    progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
    
    # Load existing json or initialize empty structure
    data = {"screens": {}}
    if os.path.exists(progress_path):
        try:
            with open(progress_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read progress json: {e}")
            
    if "screens" not in data:
        data["screens"] = {}
        
    screen_entry = data["screens"].get(screen_id, {"complete": False, "memo": ""})
    existing_memo = screen_entry.get("memo", "")
    new_line = f"로그인 ID: {login_id} - {description}"
    
    if existing_memo:
        lines = existing_memo.split("\n")
        if lines[0] != new_line:
            new_memo = new_line + "\n" + existing_memo
        else:
            new_memo = existing_memo
    else:
        new_memo = new_line
        
    screen_entry["memo"] = new_memo
    screen_entry["complete"] = True
    data["screens"][screen_id] = screen_entry
    
    try:
        with open(progress_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Successfully updated progress memo for {screen_id} in hms_screens_progress.json")
    except Exception as e:
        print(f"Failed to write progress json: {e}")

    # Regenerate screens directory HTML
    try:
        print("Regenerating All_HMS_Screens.html...")
        subprocess.run(["python", "generate_screens_directory.py"], cwd=r"D:\hmTest\backoffice\QaReport", check=True)
    except Exception as e:
        print(f"Failed to run generate_screens_directory.py: {e}")

async def login_helper(page, username, password):
    print(f"Navigating to login page for {username}...")
    await page.goto("http://localhost:8080/backoffice", timeout=15000)
    await page.wait_for_load_state("networkidle")
    
    if "login" in page.url or await page.locator("#login_userid").count() > 0:
        print(f"Filling credentials for {username}...")
        await page.locator("#login_userid").fill(username)
        await page.locator("#login_password").fill(password)
        await page.locator('button[type="submit"]').click()
        await page.wait_for_timeout(2000)
        
    print("Checking for 'already logged in' bootbox modal or redirection...")
    for _ in range(15):
        if "main" in page.url:
            break
        # Check if force-login confirm dialog is visible
        bootbox_ok = page.locator(".bootbox-accept")
        if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
            print("Force login modal detected. Clicking OK...")
            await bootbox_ok.first.click()
            await page.wait_for_timeout(2000)
        await page.wait_for_timeout(1000)
        
    print("Login phase completed. Final URL:", page.url)
    if "main" not in page.url:
        raise Exception("Login failed. Could not reach main page.")

async def run_st_test(playwright):
    print("=================== STARTING ST_VENDOR_00002 TEST ===================")
    browser = None
    try:
        try:
            print("Attempting to launch browser in headed mode (headless=False)...")
            browser = await playwright.chromium.launch(headless=False, slow_mo=300)
        except Exception as e:
            print(f"Headed launch failed ({e}), falling back to headless=True...")
            browser = await playwright.chromium.launch(headless=True, slow_mo=100)
            
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        # Handle dialogs
        async def handle_dialog(dialog):
            print(f"[ST DIALOG] Type: {dialog.type} | Message: {dialog.message}")
            await dialog.accept()
        page.on("dialog", lambda d: asyncio.create_task(handle_dialog(d)))
        
        # Perform Login
        await login_helper(page, "fnbcafe", "0000")
        
        # Navigate to target page
        print("Navigating directly to st_vendor_00002...")
        await page.goto("http://localhost:8080/backoffice/view/main/st/vendor/st_vendor_00002")
        await page.wait_for_timeout(4000)
        
        # Set date parameters via datepicker API
        print("Setting dates to 2024-02-01 via datepicker...")
        await page.evaluate("""() => {
            $('#searchFromDate').datepicker('setDate', '2024-02-01');
            $('#searchEndDate').datepicker('setDate', '2024-02-01');
        }""")
        await page.wait_for_timeout(1500)
        
        # Click search
        print("Clicking search button...")
        await page.locator("#st_vendor_00002_searchOrderList_btn").click()
        await page.wait_for_timeout(4000)
        
        # Take search screenshot
        os.makedirs("D:/hmTest/backoffice/QaReport", exist_ok=True)
        await page.screenshot(path="D:/hmTest/backoffice/QaReport/st_vendor_00002_search.png")
        print("Search screenshot saved.")
        
        # Click on the purchReqNo cell to load detail
        purch_req_cell = page.locator("#st_vendor_00002_t01 td.table-onclick").first
        if await purch_req_cell.count() > 0:
            print("Clicking first cell to open details...")
            await purch_req_cell.click()
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path="D:/hmTest/backoffice/QaReport/st_vendor_00002_detail.png")
            print("Detail screenshot saved.")
            
            # Find checkQty input field in detail table
            check_qty_input = page.locator("input[id^='checkQty_20240201_NC0007_']").first
            if await check_qty_input.count() > 0:
                print("Setting check quantity to 2...")
                await check_qty_input.fill("2")
                await page.wait_for_timeout(1000)
                
                # Save check
                print("Clicking save check button...")
                await page.locator("#st_vendor_00002_saveCheck_btn").click()
                await page.wait_for_timeout(1500)
                bootbox_accept = page.locator(".bootbox-accept")
                if await bootbox_accept.count() > 0:
                    print("Clicking Bootbox accept for save check...")
                    await bootbox_accept.first.click()
                await page.wait_for_timeout(3000)
                
                await page.screenshot(path="D:/hmTest/backoffice/QaReport/st_vendor_00002_saved.png")
                print("Saved check screenshot saved.")
                
                # Select row in Table 1 to confirm
                print("Selecting first checkbox in Table 1...")
                checkbox = page.locator("#st_vendor_00002_t01 input[type='checkbox']").nth(1)
                await checkbox.check()
                await page.wait_for_timeout(1000)
                
                # Confirm check
                print("Clicking confirm check button...")
                await page.locator("#st_vendor_00002_confirmCheck_btn").click()
                await page.wait_for_timeout(1500)
                bootbox_accept = page.locator(".bootbox-accept")
                if await bootbox_accept.count() > 0:
                    print("Clicking Bootbox accept for confirm check...")
                    await bootbox_accept.first.click()
                await page.wait_for_timeout(3000)
                
                # Refresh table
                await page.locator("#st_vendor_00002_searchOrderList_btn").click()
                await page.wait_for_timeout(3000)
                await page.screenshot(path="D:/hmTest/backoffice/QaReport/st_vendor_00002_confirmed.png")
                print("Confirmed check screenshot saved.")
                
                # Select row and cancel check to restore status
                print("Checking checkbox to cancel...")
                await page.locator("#st_vendor_00002_t01 input[type='checkbox']").nth(1).check()
                await page.wait_for_timeout(1000)
                
                print("Clicking cancel check button...")
                await page.locator("#st_vendor_00002_cancelCheck_btn").click()
                await page.wait_for_timeout(1500)
                bootbox_accept = page.locator(".bootbox-accept")
                if await bootbox_accept.count() > 0:
                    print("Clicking Bootbox accept for cancel check...")
                    await bootbox_accept.first.click()
                await page.wait_for_timeout(3000)
                
                # Final refresh
                await page.locator("#st_vendor_00002_searchOrderList_btn").click()
                await page.wait_for_timeout(2000)
                print("ST test finished successfully.")
                update_screens_progress_memo("st_vendor_00002", "fnbcafe", "매장 검수관리 (개별 매장에서 검수 수량을 입력/확정/취소 처리)")
            else:
                print("[WARNING] checkQty input not found.")
        else:
            print("[WARNING] No orders found in Table 1.")
            
        # Logout
        print("Logging out...")
        await page.goto("http://localhost:8080/backoffice/logout")
        await page.wait_for_timeout(2000)
    except Exception as e:
        print("Error during ST E2E test:", e)
    finally:
        if browser:
            await browser.close()

async def run_hq_test(playwright):
    print("=================== STARTING HQ_VENDOR_00004 TEST ===================")
    browser = None
    try:
        try:
            print("Attempting to launch browser in headed mode (headless=False)...")
            browser = await playwright.chromium.launch(headless=False, slow_mo=300)
        except Exception as e:
            print(f"Headed launch failed ({e}), falling back to headless=True...")
            browser = await playwright.chromium.launch(headless=True, slow_mo=100)
            
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        # Handle dialogs
        async def handle_dialog(dialog):
            print(f"[HQ DIALOG] Type: {dialog.type} | Message: {dialog.message}")
            await dialog.accept()
        page.on("dialog", lambda d: asyncio.create_task(handle_dialog(d)))
        
        # Perform Login as shopadmin (Chain C001 HQ user)
        await login_helper(page, "shopadmin", "0000")
        
        # Navigate to target page
        print("Navigating directly to hq_vendor_00004...")
        await page.goto("http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00004")
        await page.wait_for_timeout(4000)
        
        # Set date and store parameters via jQuery APIs
        print("Setting dates to 2024-02-01 and selecting store NC0007...")
        await page.evaluate("""() => {
            $('#searchFromDate').datepicker('setDate', '2024-02-01');
            $('#searchEndDate').datepicker('setDate', '2024-02-01');
            $('#searchMsNo_div_ms_select').val('NC0007');
            $('#searchMsNo_div_ms_select').selectpicker('refresh');
            $('#searchMsNo_div_ms_select').trigger('change');
        }""")
        await page.wait_for_timeout(2000)
        
        # Click search
        print("Clicking search button...")
        await page.locator("#hq_vendor_00004_searchOrderList_btn").click()
        await page.wait_for_timeout(4000)
        
        # Take search screenshot
        await page.screenshot(path="D:/hmTest/backoffice/QaReport/hq_vendor_00004_search.png")
        print("Search screenshot saved.")
        
        # Click on the purchReqNo cell to load detail
        purch_req_cell = page.locator("#hq_vendor_00004_t01 td.table-onclick").first
        if await purch_req_cell.count() > 0:
            print("Clicking first cell to open details...")
            await purch_req_cell.click()
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path="D:/hmTest/backoffice/QaReport/hq_vendor_00004_detail.png")
            print("Detail screenshot saved.")
            
            # Find checkQty input field in detail table
            check_qty_input = page.locator("input[id^='checkQty_20240201_NC0007_']").first
            if await check_qty_input.count() > 0:
                print("Setting check quantity to 3...")
                await check_qty_input.fill("3")
                await page.wait_for_timeout(1000)
                
                # Save check
                print("Clicking save check button...")
                await page.locator("#hq_vendor_00004_saveCheck_btn").click()
                await page.wait_for_timeout(1500)
                bootbox_accept = page.locator(".bootbox-accept")
                if await bootbox_accept.count() > 0:
                    print("Clicking Bootbox accept for save check...")
                    await bootbox_accept.first.click()
                await page.wait_for_timeout(3000)
                
                await page.screenshot(path="D:/hmTest/backoffice/QaReport/hq_vendor_00004_saved.png")
                print("Saved check screenshot saved.")
                
                # Select row in Table 1 to confirm
                print("Selecting first checkbox in Table 1...")
                checkbox = page.locator("#hq_vendor_00004_t01 input[type='checkbox']").nth(1)
                await checkbox.check()
                await page.wait_for_timeout(1000)
                
                # Confirm check
                print("Clicking confirm check button...")
                await page.locator("#hq_vendor_00004_confirmCheck_btn").click()
                await page.wait_for_timeout(1500)
                bootbox_accept = page.locator(".bootbox-accept")
                if await bootbox_accept.count() > 0:
                    print("Clicking Bootbox accept for confirm check...")
                    await bootbox_accept.first.click()
                await page.wait_for_timeout(3000)
                
                # Refresh table
                await page.locator("#hq_vendor_00004_searchOrderList_btn").click()
                await page.wait_for_timeout(3000)
                await page.screenshot(path="D:/hmTest/backoffice/QaReport/hq_vendor_00004_confirmed.png")
                print("Confirmed check screenshot saved.")
                
                # Select row and cancel check to restore status
                print("Checking checkbox to cancel...")
                await page.locator("#hq_vendor_00004_t01 input[type='checkbox']").nth(1).check()
                await page.wait_for_timeout(1000)
                
                print("Clicking cancel check button...")
                await page.locator("#hq_vendor_00004_cancelCheck_btn").click()
                await page.wait_for_timeout(1500)
                bootbox_accept = page.locator(".bootbox-accept")
                if await bootbox_accept.count() > 0:
                    print("Clicking Bootbox accept for cancel check...")
                    await bootbox_accept.first.click()
                await page.wait_for_timeout(3000)
                
                # Final refresh
                await page.locator("#hq_vendor_00004_searchOrderList_btn").click()
                await page.wait_for_timeout(2000)
                print("HQ test finished successfully.")
                update_screens_progress_memo("hq_vendor_00004", "shopadmin", "본사 검수관리 (본사 권한으로 매장별 발주 건에 대해 검수 수량 입력/확정/취소 처리)")
            else:
                print("[WARNING] checkQty input not found.")
        else:
            print("[WARNING] No orders found in Table 1.")
            
        # Logout
        print("Logging out...")
        await page.goto("http://localhost:8080/backoffice/logout")
        await page.wait_for_timeout(2000)
    except Exception as e:
        print("Error during HQ E2E test:", e)
    finally:
        if browser:
            await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run_st_test(playwright)
        await run_hq_test(playwright)

if __name__ == "__main__":
    asyncio.run(main())
