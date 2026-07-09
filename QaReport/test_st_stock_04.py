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
            print('Starting Comprehensive Playwright Test for st_stock_00004 (Store Waste Status)...')
            
            # Automatically accept dialogs
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            
            # Step 1: Login
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
            
            # Wait for either login input box or logout button to ensure page is loaded
            print('Waiting for key page elements...')
            try:
                await page.wait_for_selector('#login_userid, .logout-btn, a[href*="logout"]', timeout=8000)
            except Exception as e:
                print('Wait selector timeout, checking URL:', page.url)

            # If already logged in, force logout
            if 'main' in page.url or await page.locator('.logout-btn, a[href*="logout"]').count() > 0:
                print('Already logged in. Navigating to logout URL to force re-login...')
                await page.goto('http://localhost:8080/backoffice/logout')
                await page.wait_for_timeout(2000)
                await page.goto('http://localhost:8080/backoffice')
                await page.wait_for_selector('#login_userid', timeout=8000)
            
            # Login with fnbcafe / 0000 (Cafe manager)
            if await page.locator('#login_userid').count() > 0:
                print('Logging in with Cafe Manager (fnbcafe)...')
                await page.locator('#login_userid').fill('fnbcafe')
                await page.locator('#login_password').fill('0000')
                await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
                
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
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00004_login_fail.png')
                await browser.close()
                return
                
            # Step 2: Navigate to target screen st_stock_00004
            print('Navigating directly to st_stock_00004 (Store Waste Status)...')
            await page.goto('http://localhost:8080/backoffice/view/main/st/stock/st_stock_00004')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#st_stock_00004_t01', timeout=10000)
            print('[SUCCESS] Navigated to Store Waste Status screen.')
            
            # Set search criteria: date range (2025-06-01 to 2025-06-30)
            print('Setting date search criteria (From: 2025-06-01, To: 2025-06-30)...')
            await page.evaluate("() => { $('#searchFromDate').datepicker('setDate', '2025-06-01'); }")
            await page.evaluate("() => { $('#searchEndDate').datepicker('setDate', '2025-06-30'); }")
            await page.wait_for_timeout(1000)
            
            # Click Search (조회)
            print('Clicking Search (조회) Button...')
            await page.locator('#st_stock_00004_search_btn').click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00004_search.png')
            print('[SUCCESS] Summary search completed.')
            
            # Step 3: Click a row to open detail grid
            first_disuse_link = page.locator('#st_stock_00004_t01 a.text-primary').first
            if await first_disuse_link.count() > 0:
                print('Clicking first waste summary link to fetch detailed logs...')
                await first_disuse_link.click()
                await page.wait_for_timeout(3000)
                
                detail_screenshot_path = 'D:/hmTest/backoffice/QaReport/st_stock_00004_detail.png'
                await page.screenshot(path=detail_screenshot_path)
                print(f'Detail grid screenshot saved to {detail_screenshot_path}')
            else:
                print('[WARNING] No waste summary links found in the table to click for details.')
                
            print('All test steps finished.')
            
        except Exception as e:
            print('Error occurred during test script execution:', e)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00004_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
