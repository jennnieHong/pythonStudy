import asyncio
import os
import sys
import json
import subprocess
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

def update_screens_progress_memo(screen_id, login_id, description):
    progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
    
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
        bootbox_ok = page.locator(".bootbox-accept")
        if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
            print("Force login modal detected. Clicking OK...")
            await bootbox_ok.first.click()
            await page.wait_for_timeout(2000)
        await page.wait_for_timeout(1000)
        
    print("Login phase completed. Final URL:", page.url)
    if "main" not in page.url:
        raise Exception("Login failed. Could not reach main page.")

async def run_hq_test(playwright):
    print("=================== STARTING HQ_SALES_00026 TEST (HQ) ===================")
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
        
        async def handle_dialog(dialog):
            print(f"[HQ DIALOG] Type: {dialog.type} | Message: {dialog.message}")
            await dialog.accept()
        page.on("dialog", lambda d: asyncio.create_task(handle_dialog(d)))
        
        # Login as fnbadmin
        await login_helper(page, "fnbadmin", "0000")
        
        # Navigate to hq_sales_00026
        print("Navigating directly to hq_sales_00026...")
        await page.goto("http://localhost:8080/backoffice/view/main/hq/sales/hq_sales_00026")
        await page.wait_for_timeout(4000)
        
        # Set Date to 2026-06-02 and select ms/pos
        print("Setting searchFromDate/searchEndDate to 2026-06-02 and selecting store NC0003...")
        await page.evaluate("""() => {
            $('#searchFromDate').datepicker('setDate', '2026-06-02');
            $('#searchEndDate').datepicker('setDate', '2026-06-02');
            $('#selectPos_ms_select').val('NC0003');
            $('#selectPos_ms_select').selectpicker('refresh');
            $('#selectPos_ms_select').trigger('change');
        }""")
        await page.wait_for_timeout(2000)
        
        # Click search
        print("Clicking search button...")
        await page.locator("#hq_sales_00026_search_btn").click()
        await page.wait_for_timeout(4000)
        
        # Screenshot
        os.makedirs("D:/hmTest/backoffice/QaReport", exist_ok=True)
        screenshot_path = "D:/hmTest/backoffice/QaReport/hq_sales_00026_search.png"
        await page.screenshot(path=screenshot_path)
        print(f"HQ Search screenshot saved to {screenshot_path}.")
        
        update_screens_progress_memo("hq_sales_00026", "fnbadmin", "본사 당일매출 조회 완료 (조회일자 2026-06-02, 매장 NC0003 조회)")
        
        # Logout
        print("Logging out...")
        await page.goto("http://localhost:8080/backoffice/logout")
        await page.wait_for_timeout(2000)
        
    except Exception as e:
        print("Error during HQ E2E test:", e)
    finally:
        if browser:
            await browser.close()

async def run_st_test(playwright):
    print("=================== STARTING ST_SALES_00026 TEST (STORE) ===================")
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
        
        async def handle_dialog(dialog):
            print(f"[ST DIALOG] Type: {dialog.type} | Message: {dialog.message}")
            await dialog.accept()
        page.on("dialog", lambda d: asyncio.create_task(handle_dialog(d)))
        
        # Login as I000034a (NC0003 매장 담당)
        await login_helper(page, "I000034a", "0000")
        
        # Navigate to st_sales_00026
        print("Navigating directly to st_sales_00026...")
        await page.goto("http://localhost:8080/backoffice/view/main/st/sales/st_sales_00026")
        await page.wait_for_timeout(4000)
        
        # Set Date to 2026-06-02
        print("Setting searchFromDate/searchEndDate to 2026-06-02...")
        await page.evaluate("""() => {
            $('#searchFromDate').datepicker('setDate', '2026-06-02');
            $('#searchEndDate').datepicker('setDate', '2026-06-02');
        }""")
        await page.wait_for_timeout(2000)
        
        # Click search
        print("Clicking search button...")
        await page.locator("#st_sales_00026_search_btn").click()
        await page.wait_for_timeout(4000)
        
        # Screenshot
        screenshot_path = "D:/hmTest/backoffice/QaReport/st_sales_00026_search.png"
        await page.screenshot(path=screenshot_path)
        print(f"ST Search screenshot saved to {screenshot_path}.")
        
        update_screens_progress_memo("st_sales_00026", "I000034a", "매장 당일매출 조회 완료 (조회일자 2026-06-02 조회)")
        
        # Logout
        print("Logging out...")
        await page.goto("http://localhost:8080/backoffice/logout")
        await page.wait_for_timeout(2000)
        
    except Exception as e:
        print("Error during ST E2E test:", e)
    finally:
        if browser:
            await browser.close()

async def run_admin_test(playwright):
    print("=================== STARTING ADMIN_SALES_00002 TEST (ADMIN) ===================")
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
        
        async def handle_dialog(dialog):
            print(f"[ADMIN DIALOG] Type: {dialog.type} | Message: {dialog.message}")
            await dialog.accept()
        page.on("dialog", lambda d: asyncio.create_task(handle_dialog(d)))
        
        # Login as admin2
        await login_helper(page, "admin2", "0000")
        
        # Navigate to admin_sales_00002
        print("Navigating directly to admin_sales_00002...")
        await page.goto("http://localhost:8080/backoffice/view/main/admin/sales/admin_sales_00002")
        await page.wait_for_timeout(4000)
        
        # Set Date to 2026-06-02 and select ms/pos
        print("Setting searchFromDate/searchEndDate to 2026-06-02 and selecting store NC0003...")
        await page.evaluate("""() => {
            $('#searchFromDate').datepicker('setDate', '2026-06-02');
            $('#searchEndDate').datepicker('setDate', '2026-06-02');
            $('#selectPos_ms_select').val('NC0003');
            $('#selectPos_ms_select').selectpicker('refresh');
            $('#selectPos_ms_select').trigger('change');
        }""")
        await page.wait_for_timeout(2000)
        
        # Click search
        print("Clicking search button...")
        await page.locator("#admin_sales_00002_search_btn").click()
        await page.wait_for_timeout(4000)
        
        # Screenshot
        screenshot_path = "D:/hmTest/backoffice/QaReport/admin_sales_00002_search.png"
        await page.screenshot(path=screenshot_path)
        print(f"ADMIN Search screenshot saved to {screenshot_path}.")
        
        update_screens_progress_memo("admin_sales_00002", "admin2", "어드민 당일매출 조회 완료 (조회일자 2026-06-02, 매장 NC0003 조회)")
        
        # Logout
        print("Logging out...")
        await page.goto("http://localhost:8080/backoffice/logout")
        await page.wait_for_timeout(2000)
        
    except Exception as e:
        print("Error during ADMIN E2E test:", e)
    finally:
        if browser:
            await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run_hq_test(playwright)
        await run_st_test(playwright)
        await run_admin_test(playwright)

if __name__ == "__main__":
    asyncio.run(main())
