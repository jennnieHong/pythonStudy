import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def run_test():
    async with async_playwright() as p:
        try:
            print('Attempting to launch browser in headless mode...')
            browser = await p.chromium.launch(headless=True, slow_mo=800)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            # Listen to console messages and network requests
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            
            async def log_response(response):
                if "hq_stock_00006" in response.url:
                    try:
                        print(f"API Response [{response.url}]: {await response.text()[:1000]}")
                    except Exception as e:
                        pass
            
            page.on("response", log_response)

            # Step 1: Navigate to main page
            print('Navigating to http://localhost:8080/backoffice ...')
            await page.goto('http://localhost:8080/backoffice')
            await page.wait_for_timeout(3000)
            
            # Check if we need to log out first
            if 'main' in page.url or await page.locator('.logout-btn, a[href*="logout"]').count() > 0:
                print('Already logged in. Force logging out...')
                await page.goto('http://localhost:8080/backoffice/logout')
                await page.wait_for_timeout(2000)
                await page.goto('http://localhost:8080/backoffice')
                await page.wait_for_timeout(2000)

            # Wait for login input box
            print('Waiting for login box...')
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            # Login with fnbadmin / 0000 (F&B HQ Administrator)
            print('Logging in with fnbadmin...')
            await page.locator('#login_userid').fill('fnbadmin')
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
            
            # Handle duplicate user bootbox if present
            await page.wait_for_timeout(2000)
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                confirm_text = await page.locator('.bootbox-body').first.inner_text()
                print(f'Bootbox modal detected: {confirm_text}')
                if '접속 중인 사용자' in confirm_text or 'duplicate' in confirm_text or '종료' in confirm_text:
                    print('Duplicate user session. Clicking Yes to retry...')
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(3000)
            
            # Handle login success bootbox if present
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                success_text = await page.locator('.bootbox-body').first.inner_text()
                print(f'Login success bootbox modal: {success_text}')
                await bootbox_ok.first.click()
                await page.wait_for_timeout(3000)

            print('Waiting for redirection to main dashboard...')
            await page.wait_for_load_state('networkidle')
            print('Current URL after login attempt:', page.url)
            
            # Step 2: Navigate to target screen (hq_stock_00006)
            print('Navigating to hq_stock_00006 (HQ Stock Adjustment Status)...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00006')
            await page.wait_for_timeout(4000)
            
            # Set search range from 2025-01-01 to today
            print('Setting date range from 2025-01-01 to today...')
            await page.evaluate("() => { $('#searchFromDate').datepicker('setDate', '2025-01-01'); }")
            await page.evaluate("() => { $('#searchToDate').datepicker('setDate', 'today'); }")
            await page.wait_for_timeout(1000)
            
            # Click [조회] (Search)
            print('Clicking search button...')
            await page.evaluate("() => { searchModify(); }")
            await page.wait_for_timeout(4000)
            
            # Capture the initial search result
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00006_search.png')
            print('Captured search screen.')
            
            # Check if there are row data in the summary table
            no_data = page.locator('#hq_stock_00006_t01 tbody tr.no-records-found')
            rows = page.locator('#hq_stock_00006_t01 tbody tr')
            
            if await no_data.count() == 0 and await rows.count() > 0:
                print(f'Rows detected in summary table: {await rows.count()}. Clicking the first row to view details...')
                # Click the first row
                await rows.first.click()
                await page.wait_for_timeout(4000)
                
                # Capture detail table screenshot
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00006_detail.png')
                print('Captured detail screen.')
            else:
                print('No adjustment records found for this period. Summary table is empty.')
                
        except Exception as e:
            print('Error occurred:', e)
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
