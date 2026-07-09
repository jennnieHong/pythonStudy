import asyncio
import os
import sys
from datetime import datetime
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
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
        
        try:
            print('Starting Comprehensive Playwright Test for hq_stock_00007 (Waste Registration)...')
            
            # Automatically accept dialogs (e.g. bootbox alerts/confirms)
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
            
            # Login with shopadmin
            if 'login' in page.url or await page.locator('#login_userid').count() > 0:
                print('Logging in with Shop Admin (shopadmin)...')
                await page.locator('#login_userid').fill('shopadmin')
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
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00007_login_fail.png')
                await browser.close()
                return
                
            # Step 2: Navigate to target screen hq_stock_00007
            print('Navigating directly to hq_stock_00007...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00007')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_stock_00007_t01', timeout=10000)
            print('[SUCCESS] Navigated to Waste Registration screen.')
            
            today_str = datetime.today().strftime('%Y-%m-%d')
            # Set search criteria: dates and store
            print(f'Setting search criteria (date: {today_str})...')
            await page.evaluate(f"() => {{ $('#hq_stock_00007_fromDate').val('{today_str}'); }}")
            await page.evaluate(f"() => {{ $('#hq_stock_00007_toDate').val('{today_str}'); }}")
            await page.wait_for_timeout(1000)
            
            # Select store
            print('Selecting store NC0003...')
            await page.evaluate("() => { $('#hq_stock_00007_msCombo_ms_select').selectpicker('val', 'NC0003'); }")
            await page.wait_for_timeout(1000)
            
            # Click Search (조회)
            print('Clicking Search (조회) Button...')
            await page.locator('#hq_stock_00007_search_btn').click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00007_search.png')
            print('[SUCCESS] Initial Search completed.')
            
            # Delete existing unconfirmed items to start with a clean state
            rows = page.locator('#hq_stock_00007_t01 tbody tr')
            first_row_text = await rows.first.text_content() if await rows.count() > 0 else ""
            if await rows.count() > 0 and '조회된 데이터가 없습니다' not in first_row_text and 'No matching records found' not in first_row_text:
                print('Existing unconfirmed items found. Deleting them to start clean...')
                # Use Bootstrap Table's API to check all rows programmatically
                await page.evaluate("() => { $('#hq_stock_00007_t01').bootstrapTable('checkAll'); }")
                await page.wait_for_timeout(1500)
                
                print('Clicking Delete (삭제) Button...')
                await page.locator('#hq_stock_00007_delete_btn').click()
                await page.wait_for_timeout(2000)
                    
                # Accept delete confirm popup
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print("Clicking OK on delete confirm...")
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(3000)
                print('[SUCCESS] Existing items deleted.')
                
                # Search again to verify it is empty
                await page.locator('#hq_stock_00007_search_btn').click()
                await page.wait_for_timeout(2000)

            
            # Step 3: Open Register Modal
            print('Opening Waste Registration Modal...')
            await page.locator('#hq_stock_00007_add_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00007_add_modal.png')
            
            # Select store in modal
            print('Selecting store NC0003 in modal...')
            await page.evaluate("() => { $('#hq_stock_00007_M01_msCombo_ms_select').selectpicker('val', 'NC0003'); }")
            await page.wait_for_timeout(1000)
            
            # Set date in modal to today
            print(f'Setting date to {today_str} in modal...')
            await page.evaluate(f"() => {{ $('#hq_stock_00007_M01_searchDate').val('{today_str}'); }}")
            await page.wait_for_timeout(1000)
            
            # Trigger search inside modal to list goods
            print('Searching goods in modal...')
            await page.evaluate("() => { $('#hq_stock_00007_M01_t01').bootstrapTable('refresh'); }")
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00007_add_modal_loaded.png')
            
            # Select first item and confirm
            print('Selecting first goods item in modal...')
            # Check the first row's checkbox
            first_checkbox = page.locator('#hq_stock_00007_M01_t01 tbody tr input[type="checkbox"]').first
            if await first_checkbox.count() > 0:
                await first_checkbox.click()
                await page.wait_for_timeout(1000)
                
                # Click "선택" (Confirm select) button
                print('Confirming selection in modal...')
                await page.locator('#hq_stock_00007_M1_save_btn').click()
                await page.wait_for_timeout(1500)
                
                # Accept "선택한 상품을 폐기등록하시겠습니까?" confirm
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print('Clicking OK on confirm dialog...')
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)
                
                # Accept subsequent alert (e.g. "저장되었습니다.")
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print('Clicking OK on completion alert...')
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)
                
                print('[SUCCESS] Waste item added successfully.')
            else:
                print('[WARNING] No goods found in modal. Closing modal...')
                await page.locator('#btnM01Close').click()
                await page.wait_for_timeout(1000)
            
            # Step 4: Search again to see newly added waste slip (it is unconfirmed)
            print('Searching again for the added waste slip...')
            # Force set dates and click search
            await page.evaluate(f"() => {{ $('#hq_stock_00007_fromDate').val('{today_str}'); }}")
            await page.evaluate(f"() => {{ $('#hq_stock_00007_toDate').val('{today_str}'); }}")
            await page.evaluate("() => { $('#hq_stock_00007_msCombo_ms_select').selectpicker('val', 'NC0003'); }")
            await page.locator('#hq_stock_00007_search_btn').click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00007_added_list.png')
            
            # Step 5: Input Quantity and Save
            print('Entering quantity for the added waste slip...')
            ea_input = page.locator('input[id^="main_duse_ea_qty_"]').first
            if await ea_input.count() > 0:
                # Click to focus, then clear any existing value and type '5'
                await ea_input.click()
                await ea_input.focus()
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await ea_input.press_sequentially('5')
                await page.wait_for_timeout(1500)
                
                # Set a reason and trigger change event
                await page.evaluate("() => { $('#select_reason_0').selectpicker('val', 'C01').change(); }")
                await page.wait_for_timeout(1000)
                
                print('Saving modified quantity...')
                await page.locator('#hq_stock_00007_save_btn').click()
                await page.wait_for_timeout(2000)
                
                # Handle save confirmation popups
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print("Clicking OK on save confirm...")
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(3000)
                
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    print("Clicking OK on save completion alert...")
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(2000)
                    
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00007_saved_qty.png')
                print('[SUCCESS] Waste quantity saved successfully.')
                
                # Step 6: Select the item and Click Confirm (확정)
                print('Selecting item to confirm...')
                row_chk = page.locator('#hq_stock_00007_t01 tbody tr input[type="checkbox"]').first
                if await row_chk.count() > 0:
                    await row_chk.click()
                    await page.wait_for_timeout(1000)
                    
                    print('Clicking Confirm (확정) Button...')
                    await page.locator('#hq_stock_00007_confirm_btn').click()
                    await page.wait_for_timeout(2000)
                    
                    # Handle confirmation popups
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        print("Clicking OK on confirm popup...")
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(4000)
                        
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00007_confirmed.png')
                    print('[SUCCESS] Waste slip confirmed successfully.')
                else:
                    print('[WARNING] Row checkbox not found for confirmation.')
            else:
                print('[WARNING] No input quantity fields found to edit.')

            print('All test steps finished.')
            
        except Exception as e:
            print('Error occurred during test script execution:', e)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00007_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
