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
            print('Starting Comprehensive Playwright Test for hq_stock_00019 (Current Stock - Store Total)...')
            
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
            
            # Perform Login
            if 'login' in page.url or await page.locator('#login_userid').count() > 0:
                print('Logging in with Shop Admin (shopadmin)...')
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
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00019_login_fail.png')
                await browser.close()
                return
                
            # Step 2: Navigate to target screen
            print('Navigating directly to hq_stock_00019...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00019')
            await page.wait_for_timeout(3000)
            # Wait for bootstrap table components to load
            await page.wait_for_selector('#hq_stock_00019_t01', timeout=10000)
            print('[SUCCESS] Navigated to Current Stock (Store Total) screen.')
            
            # Set search date to 2025-06-23 (since DB has stock data for this date)
            print('Setting search date to 2025-06-23...')
            await page.evaluate("() => { $('#searchDate').val('2025-06-23'); }")
            await page.wait_for_timeout(1000)
            
            # Step 3: Trigger Store Selection Modal
            print('Opening Store Selection Modal...')
            store_btn = page.locator('#selectMsPos button.input-group-append-btn')
            if await store_btn.count() > 0:
                await store_btn.first.click()
                await page.wait_for_timeout(2000)
                
                # Click "전체" (Select All) in modal
                all_btn = page.locator('#addStoreModal button:has-text("전체")')
                if await all_btn.count() > 0:
                    print('Selecting ALL stores...')
                    await all_btn.first.click()
                    await page.wait_for_timeout(1000)
                else:
                    print('[WARNING] "전체" button not found in modal.')
            else:
                print('[FAIL] Store search button not found.')
                
            # Step 4: Perform Search
            print('Clicking Search Button...')
            search_btn = page.locator('#hq_stock_00019_search_btn')
            if await search_btn.count() > 0:
                await search_btn.first.click()
                await page.wait_for_timeout(3000)
                await page.wait_for_load_state('networkidle')
                print('[SUCCESS] Search completed.')
            else:
                print('[FAIL] Search button not found.')
                
            # Save screenshot of results
            screenshot_path = 'D:/hmTest/backoffice/QaReport/hq_stock_00019_search.png'
            await page.screenshot(path=screenshot_path)
            print(f'Screenshot saved to {screenshot_path}')
            
            # Step 5: Check Detail Modal (Click first goods item)
            # Find a cell with class 'table-onclick' (Goods Code column)
            first_goods_cell = page.locator('#hq_stock_00019_t01 td.table-onclick').first
            if await first_goods_cell.count() > 0:
                print('Clicking first goods code to open stock ledger detail modal...')
                await first_goods_cell.click()
                await page.wait_for_timeout(3000)
                
                modal_screenshot_path = 'D:/hmTest/backoffice/QaReport/hq_stock_00019_detail_modal.png'
                await page.screenshot(path=modal_screenshot_path)
                print(f'Detail Modal screenshot saved to {modal_screenshot_path}')
                
                # Close the modal
                close_btn = page.locator('#stockModal button:has-text("닫기"), #stockModal button.close').first
                if await close_btn.count() > 0:
                    print('Closing detail modal...')
                    await close_btn.click()
                    await page.wait_for_timeout(1000)
            else:
                print('[WARNING] No goods items found in table to click for details.')
                
            print('All test steps finished.')
            
        except Exception as e:
            print('Error occurred during test script execution:', e)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00019_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
