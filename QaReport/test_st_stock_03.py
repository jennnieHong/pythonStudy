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
            
            # Listen to console messages and network requests
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            
            async def log_response(response):
                if "goodsSelect" in response.url or "selectGoodsLclass" in response.url:
                    try:
                        print(f"API Response [{response.url}]: {await response.text()[:1000]}")
                    except Exception as e:
                        pass
            
            async def log_request(request):
                if "goodsSelect" in request.url:
                    print(f"API Request [{request.url}] Payload: {request.post_data}")

            page.on("request", log_request)
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
            
            # Login
            print('Logging in with fnbcafe...')
            await page.locator('#login_userid').fill('fnbcafe')
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
                    await page.wait_for_timeout(3000) # wait for logout & login retry
            
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
            
            # Step 2: Navigate to target screen
            print('Navigating to st_stock_00003 (Store Waste Registration)...')
            await page.goto('http://localhost:8080/backoffice/view/main/st/stock/st_stock_00003')
            await page.wait_for_timeout(3000)
            
            # Click [등록] (Add) Button to open modal popup
            print('Clicking [등록] (Add) Button...')
            await page.locator('#st_stock_00003_add_btn').click()
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00003_popup_open.png')
            print('Captured popup screen.')
            
            # Click [조회] inside modal
            print('Clicking [조회] inside the modal...')
            await page.evaluate("() => { fnSearchGoods(); }")
            await page.wait_for_timeout(4000)
            
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00003_popup_searched.png')
            print('Captured popup searched screen.')
            
            # Check row count
            rows = page.locator('#st_stock_00003_t02 tbody tr')
            rows_count = await rows.count()
            print(f"Number of rows in popup: {rows_count}")
            
            if rows_count > 0:
                print("First row text:", await rows.first.inner_text())
                
                # Check the checkbox of the first product
                print("Selecting first product checkbox...")
                await rows.first.locator('input[type="checkbox"]').click()
                await page.wait_for_timeout(1000)
                
                # Click [선택] (Select) Button
                print("Clicking select button...")
                await page.locator('#st_stock_00003_M1_save_btn').click()
                await page.wait_for_timeout(2000)
                
                # Handle bootbox confirm modal for registration
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print("Clicking OK on registration confirm...")
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(4000) # Wait for page load and table refresh
                
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00003_added_in_grid.png')
                print('Captured main grid after product addition.')
                
                # Now set quantity and reason on the main table
                print("Filling waste quantity '2'...")
                await page.evaluate("() => { $('#main_duse_ea_qty_0').val('2').keyup(); }")
                await page.wait_for_timeout(1000)
                
                # Select a valid reason code from dropdown options
                reason_val = await page.evaluate("() => { return $('#st_stock_00003_selReason_combo_select option').eq(1).val() || '01'; }")
                print(f"Selecting reason value: {reason_val}")
                await page.evaluate(f"() => {{ $('#select_reason_0').selectpicker('val', '{reason_val}'); $('#select_reason_0').change(); }}")
                await page.wait_for_timeout(1000)
                
                # Click [저장] (Save) Button
                print("Clicking [저장] (Save) Button...")
                await page.locator('#st_stock_00003_save_btn').click()
                await page.wait_for_timeout(2000)
                
                # Handle bootbox confirm modal for saving
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print("Clicking OK on save confirm...")
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(4000)
                
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00003_saved.png')
                print('Captured main grid after save.')
                
                # Select the checkbox of the row in the main grid
                print("Selecting checkbox of the row to confirm...")
                await page.locator('#st_stock_00003_t01 tbody tr').first.locator('input[type="checkbox"]').click()
                await page.wait_for_timeout(1000)
                
                # Click [확정] (Confirm) Button
                print("Clicking [확정] (Confirm) Button...")
                await page.locator('#st_stock_00003_confirm_btn').click()
                await page.wait_for_timeout(2000)
                
                # Handle bootbox confirm modal for confirmation
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print("Clicking OK on confirm...")
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(4000)
                    
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00003_confirmed.png')
                print('Captured main grid after confirmation.')
            else:
                print("No products available to register in the popup!")

        except Exception as e:
            print('Error occurred:', e)
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())

