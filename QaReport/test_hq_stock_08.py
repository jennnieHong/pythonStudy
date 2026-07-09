import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def run_test():
    async with async_playwright() as p:
        try:
            print('Attempting to launch browser in headed mode (headless=False)...')
            browser = await p.chromium.launch(headless=False, slow_mo=300)
        except Exception as e:
            print(f'Headed launch failed ({e}), falling back to headless=True...')
            browser = await p.chromium.launch(headless=True, slow_mo=100)
            
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        try:
            print('Starting QA E2E Playwright Test for hq_stock_00008 (HQ Waste Status)...')
            
            # Automatically accept dialogs
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            
            # Step 1: Navigate to main/login url
            print('Navigating to http://localhost:8080/backoffice ...')
            max_retries = 10
            for i in range(max_retries):
                try:
                    await page.goto('http://localhost:8080/backoffice', timeout=10000)
                    break
                except Exception as e:
                    print(f'Waiting for Tomcat to be ready... ({i+1}/{max_retries})')
                    await page.wait_for_timeout(3000)
            else:
                print('[FAIL] Failed to reach backoffice after retries.')
                await browser.close()
                return
                
            await page.wait_for_load_state('networkidle')
            
            # Step 2: Check if already logged in. If yes, log out first.
            print('Current URL:', page.url)
            if 'main' in page.url or await page.locator('#login_userid').count() == 0:
                print('Already logged in. Attempting to logout to satisfy the "logout and login again" requirement...')
                try:
                    await page.evaluate("() => { if (typeof backofficeLogout === 'function') { backofficeLogout(); } else { document.getElementById('backoffice-logout').submit(); } }")
                    await page.wait_for_timeout(3000)
                    await page.wait_for_load_state('networkidle')
                    print('Redirection after logout. Current URL:', page.url)
                except Exception as ex:
                    print('Failed to trigger logout via JS:', ex)
                    # Fallback: navigate directly to logout url
                    await page.goto('http://localhost:8080/backoffice/auth/logout')
                    await page.wait_for_timeout(3000)
                    await page.goto('http://localhost:8080/backoffice')
                    await page.wait_for_load_state('networkidle')
            
            # Perform Login
            if 'login' in page.url or await page.locator('#login_userid').count() > 0:
                print('Logging in with Headquarters Admin (shopadmin)...')
                await page.locator('#login_userid').fill('shopadmin')
                await page.locator('#login_password').fill('0000')
                
                submit_btn = page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first
                await submit_btn.click()
                
            print('Waiting for redirection to main dashboard...')
            try:
                for _ in range(15):
                    if 'main' in page.url:
                        break
                    bootbox_ok = page.locator('.bootbox-accept')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        print('Popup detected. Clicking OK...')
                        await bootbox_ok.first.click()
                    await page.wait_for_timeout(2000)
            except Exception as e:
                print('Exception in login wait loop:', e)
                
            await page.wait_for_load_state('networkidle')
            print('Login phase completed. Current URL:', page.url)
            
            if 'main' not in page.url:
                print('[FAIL] Login failed.')
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00008_login_fail.png')
                await browser.close()
                return
                
            # Step 3: Navigate to target screen
            print('Navigating directly to hq_stock_00008...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00008')
            await page.wait_for_timeout(3000)
            
            # Wait for bootstrap table components to load
            await page.wait_for_selector('#hq_stock_00008_t01', timeout=10000)
            print('[SUCCESS] Navigated to HQ Waste Status screen.')
            
            # Set search dates to 2026-06-01 ~ 2026-06-10 (since DB has waste data on 2026-06-05)
            print('Setting search dates to 2026-06-01 ~ 2026-06-10...')
            await page.evaluate("() => { $('#hq_stock_00008_fromDate').val('2026-06-01'); $('#hq_stock_00008_toDate').val('2026-06-10'); }")
            await page.wait_for_timeout(1000)
            
            # Step 4: Select Store NC0007 in MsCombo
            print('Selecting store NC0007...')
            await page.evaluate("() => { $('#hq_stock_00008_msCombo_ms_select').selectpicker('val', 'NC0007'); }")
            await page.wait_for_timeout(1000)
            
            # Step 5: Perform Search
            print('Clicking Search Button...')
            search_btn = page.locator('#hq_stock_00008_search_btn')
            if await search_btn.count() > 0:
                await search_btn.first.click()
                await page.wait_for_timeout(3000)
                await page.wait_for_load_state('networkidle')
                print('[SUCCESS] Search completed.')
            else:
                print('[FAIL] Search button not found.')
                
            # Save screenshot of results
            screenshot_path = 'D:/hmTest/backoffice/QaReport/hq_stock_00008_search.png'
            await page.screenshot(path=screenshot_path)
            print(f'Screenshot saved to {screenshot_path}')
            
            # Step 6: Click first row in hq_stock_00008_t01 (waste date/reason cell with class table-onclick)
            first_row_cell = page.locator('#hq_stock_00008_t01 td.table-onclick').first
            if await first_row_cell.count() > 0:
                print('Clicking first row to display waste detail table...')
                await first_row_cell.click()
                await page.wait_for_timeout(3000)
                
                detail_screenshot_path = 'D:/hmTest/backoffice/QaReport/hq_stock_00008_detail.png'
                await page.screenshot(path=detail_screenshot_path)
                print(f'Detail screenshot saved to {detail_screenshot_path}')
            else:
                print('[WARNING] No rows found in hq_stock_00008_t01 to click.')
                
            print('All test steps finished.')
            
        except Exception as e:
            print('Error occurred during test script execution:', e)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00008_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
