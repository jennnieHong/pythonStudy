import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def run_test():
    async with async_playwright() as p:
        try:
            print('Attempting to launch browser in headless mode...')
            browser = await p.chromium.launch(headless=True, slow_mo=100)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            # Listen to console messages
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            
            # Step 1: Navigate to login page
            print('Navigating to http://localhost:8080/backoffice ...')
            await page.goto('http://localhost:8080/backoffice')
            await page.wait_for_timeout(2000)
            
            if 'main' in page.url or await page.locator('.logout-btn, a[href*="logout"]').count() > 0:
                print('Already logged in. Force logging out...')
                await page.goto('http://localhost:8080/backoffice/logout')
                await page.wait_for_timeout(2000)
                await page.goto('http://localhost:8080/backoffice')
                await page.wait_for_timeout(2000)

            # Wait for login input box
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            # Login
            print('Logging in with shopadmin...')
            await page.locator('#login_userid').fill('shopadmin')
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
            await page.wait_for_timeout(2000)
            
            # Handle duplicate user session confirm modal if present
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                confirm_text = await page.locator('.bootbox-body').first.inner_text()
                print(f'Bootbox modal: {confirm_text}')
                await bootbox_ok.first.click()
                await page.wait_for_timeout(3000)
                
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)

            print('Redirected URL:', page.url)
            
            # Step 2: Navigate to target screen (hq_stock_00008)
            print('Navigating to hq_stock_00008 (HQ Waste Status)...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00008')
            await page.wait_for_timeout(3000)
            
            # Select store NC0007 (CAFE)
            print('Selecting store NC0007...')
            await page.evaluate("() => { $('#hq_stock_00008_msCombo_ms_select').selectpicker('val', 'NC0007'); $('#hq_stock_00008_msCombo_ms_select').change(); }")
            await page.wait_for_timeout(1000)
            
            # Test Case 1: Search with non-matching partial code 'T9999'
            print('--- Test Case 1: Searching with non-matching code T9999 ---')
            await page.evaluate("() => { $('#hq_stock_00008_searchGoodsNmCd_goosCd_Input').val('T9999'); }")
            await page.wait_for_timeout(500)
            await page.locator('#hq_stock_00008_search_btn').click()
            await page.wait_for_timeout(3000)
            
            # Verify grids are empty
            t01_rows = await page.locator('#hq_stock_00008_t01 tbody tr').count()
            t02_rows = await page.locator('#hq_stock_00008_t02 tbody tr').count()
            t01_text = await page.locator('#hq_stock_00008_t01 tbody tr').first.inner_text()
            t02_text = await page.locator('#hq_stock_00008_t02 tbody tr').first.inner_text()
            print(f't01 rows: {t01_rows}, text: "{t01_text.strip()}"')
            print(f't02 rows: {t02_rows}, text: "{t02_text.strip()}"')
            
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00008_search_empty.png')
            print('Captured search empty screen.')
            
            # Test Case 2: Search with exact code 'T0000291'
            print('--- Test Case 2: Searching with exact code T0000291 ---')
            await page.evaluate("() => { $('#hq_stock_00008_searchGoodsNmCd_goosCd_Input').val('T0000291'); }")
            await page.wait_for_timeout(500)
            await page.locator('#hq_stock_00008_search_btn').click()
            await page.wait_for_timeout(3000)
            
            # Check row count
            t01_rows = await page.locator('#hq_stock_00008_t01 tbody tr').count()
            t01_text = await page.locator('#hq_stock_00008_t01 tbody tr').first.inner_text()
            print(f't01 rows: {t01_rows}, text: "{t01_text.strip()}"')
            
            if t01_rows > 0 and "조회된 데이터가 없습니다" not in t01_text:
                print('First grid has data. Clicking the first row to check details...')
                await page.locator('#hq_stock_00008_t01 tbody tr').first.click()
                await page.wait_for_timeout(3000)
                
                t02_rows = await page.locator('#hq_stock_00008_t02 tbody tr').count()
                t02_text = await page.locator('#hq_stock_00008_t02 tbody tr').first.inner_text()
                print(f't02 rows: {t02_rows}, text: "{t02_text.strip()}"')
                
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00008_search_partial_success.png')
                print('Captured search partial success screen.')
            else:
                print('FAIL: First grid was empty for partial search!')

        except Exception as e:
            print('Error occurred:', e)
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
