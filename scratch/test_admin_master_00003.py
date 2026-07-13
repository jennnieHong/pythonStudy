import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def run_test():
    console_errors = []
    console_logs = []
    
    async with async_playwright() as p:
        browser = None
        try:
            print("Launching browser in headed mode...", flush=True)
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            def handle_console(msg):
                log_msg = f"[{msg.type.upper()}] {msg.text}"
                console_logs.append(log_msg)
                print(log_msg, flush=True)
                if msg.type == "error" or "SyntaxError" in msg.text:
                    console_errors.append(msg.text)
            page.on("console", handle_console)
            page.on("pageerror", lambda err: console_errors.append(err.message) or print(f"[PAGE ERROR] {err.message}", flush=True))
            
            # Step 1: Login
            print("Navigating to http://localhost:8080/backoffice ...", flush=True)
            await page.goto('http://localhost:8080/backoffice', timeout=20000)
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            print("Logging in as admin2...", flush=True)
            await page.locator('#login_userid').fill('admin2')
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"]').first.click()
            
            # Redirect wait loop
            login_success = False
            for _ in range(15):
                if 'main' in page.url:
                    login_success = True
                    break
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print("[Bootbox] Found alert. Clicking accept...", flush=True)
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)
                
            if not login_success:
                raise RuntimeError("Login failed due to redirection timeout.")
                
            print("Login succeeded.", flush=True)
            await page.wait_for_timeout(2000)
            
            # Step 2: Navigate to admin_master_00003
            print("Navigating to admin_master_00003...", flush=True)
            await page.goto('http://localhost:8080/backoffice/view/main/admin/master/admin_master_00003', timeout=15000)
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#admin_master_00003_t01', timeout=10000)
            print("Table rendered.", flush=True)
            
            # Print the generated HTML of all chain links
            print("\n--- Listing HTML of all chain links ---", flush=True)
            link_selector = '#admin_master_00003_t01 tbody tr td a.text-primary'
            link_count = await page.locator(link_selector).count()
            target_idx = 0
            
            for idx in range(link_count):
                html = await page.locator(link_selector).nth(idx).evaluate("el => el.outerHTML")
                print(f"[{idx}] {html}", flush=True)
                # Find a link that contains consecutive single quotes or looks escaped
                if "''" in html or "&#39;&#39;" in html:
                    target_idx = idx
            
            print(f"\nClicking chain link at index {target_idx}...", flush=True)
            await page.locator(link_selector).nth(target_idx).click()
            await page.wait_for_timeout(2000)
                
            print("\n--- Execution Finished ---", flush=True)
            if console_errors:
                print(f"Detected {len(console_errors)} errors:", flush=True)
                for err in console_errors:
                    print(f" - {err}", flush=True)
            else:
                print("No console errors detected.", flush=True)
                
        except Exception as e:
            print(f"Error during execution: {e}", flush=True)
        finally:
            if browser:
                await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
