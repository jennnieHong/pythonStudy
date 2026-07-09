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
            print('Starting Comprehensive Playwright Test for st_stock_00007 (Store Current Stock)...')
            
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
            
            # If already logged in, force logout
            if 'main' in page.url or await page.locator('.logout-btn, a[href*="logout"]').count() > 0:
                print('Already logged in. Navigating to logout URL to force re-login...')
                await page.goto('http://localhost:8080/backoffice/logout')
                await page.wait_for_timeout(2000)
                await page.goto('http://localhost:8080/backoffice')
                await page.wait_for_load_state('networkidle')
            
            # Login with fnbcafe / 0000
            if 'login' in page.url or await page.locator('#login_userid').count() > 0:
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
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00007_login_fail.png')
                await browser.close()
                return
                
            # Step 2: Navigate to target screen st_stock_00007
            print('Navigating directly to st_stock_00007...')
            await page.goto('http://localhost:8080/backoffice/view/main/st/stock/st_stock_00007')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#st_stock_00007_t01', timeout=10000)
            print('[SUCCESS] Navigated to Store Current Stock screen.')
            
            # Set search criteria: date
            print('Setting search criteria (date: 2025-06-23)...')
            await page.evaluate("() => { $('#searchDate').val('2025-06-23'); }")
            await page.wait_for_timeout(1000)
            
            # Dynamically check and select store if needed
            store_selector = page.locator('#selectMsPos_ms_select')
            if await store_selector.count() > 0 and await store_selector.is_visible():
                selected_store = await store_selector.input_value()
                print(f'Default selected store: {selected_store}')
                if not selected_store:
                    first_option_val = await page.locator('#selectMsPos_ms_select option').first.get_attribute('value')
                    print(f'Selecting first store option: {first_option_val}')
                    await page.evaluate(f"() => {{ $('#selectMsPos_ms_select').selectpicker('val', '{first_option_val}'); }}")
                    await page.wait_for_timeout(1000)
            else:
                print('Store selector (#selectMsPos_ms_select) not found or not visible. Skipping store selection (store bind from session).')
            
            # Click Search (조회)
            print('Clicking Search (조회) Button...')
            await page.locator('#st_stock_00007_search_btn').click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00007_search.png')
            print('[SUCCESS] Search completed.')
            
            # Step 3: Open Detail Modal (Click first goods item)
            first_goods_cell = page.locator('#st_stock_00007_t01 td.table-onclick').first
            if await first_goods_cell.count() > 0:
                print('Clicking first goods code to open stock ledger detail modal...')
                await first_goods_cell.click()
                await page.wait_for_timeout(4000)
                
                modal_screenshot_path = 'D:/hmTest/backoffice/QaReport/st_stock_00007_detail_modal.png'
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
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00007_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
