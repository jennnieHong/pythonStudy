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
            print('Starting Playwright E2E Test for hq_stock_00005 (HQ Stock Adjustment)...')
            
            # Automatically accept dialogs (bootbox alerts/confirms)
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            
            # Step 1: Login
            print('Navigating to http://localhost:8080/backoffice ...')
            max_retries = 5
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
            
            # Force logout if already logged in
            if 'main' in page.url or await page.locator('.logout-btn, a[href*="logout"]').count() > 0:
                print('Already logged in. Force logging out...')
                await page.goto('http://localhost:8080/backoffice/logout')
                await page.wait_for_timeout(2000)
                await page.goto('http://localhost:8080/backoffice')
                await page.wait_for_load_state('networkidle')
                
            # Login with fnbadmin
            if 'login' in page.url or await page.locator('#login_userid').count() > 0:
                print('Logging in with F&B Admin (fnbadmin)...')
                await page.locator('#login_userid').fill('fnbadmin')
                await page.locator('#login_password').fill('0000')
                await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
                
            print('Waiting for redirection to main...')
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
                print('Exception during login wait:', e)
                
            await page.wait_for_load_state('networkidle')
            print('Login completed. Current URL:', page.url)
            
            if 'main' not in page.url:
                print('[FAIL] Login failed.')
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00005_login_fail.png')
                await browser.close()
                return
                
            # Step 2: Navigate to target screen hq_stock_00005
            print('Navigating to hq_stock_00005 (HQ Stock Adjustment)...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00005')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_stock_00005_t01', timeout=10000)
            print('[SUCCESS] Navigated to HQ Stock Adjustment screen.')
            
            # Wait for store option NC0006 (KITCHEN) to load in main page
            print('Waiting for store option NC0006 to load in main page...')
            await page.wait_for_selector('#selectMsPos_ms_select option[value="NC0006"]', state='attached', timeout=10000)
            await page.wait_for_timeout(1000)
            
            today_str = datetime.today().strftime('%Y-%m-%d')
            target_store = 'NC0006'
            print(f'Setting date: {today_str} and store: {target_store}...')
            
            await page.evaluate(f"() => {{ $('#surveyDate').val('{today_str}'); }}")
            await page.evaluate(f"() => {{ $('#selectMsPos_ms_select').selectpicker('val', '{target_store}').change(); }}")
            await page.wait_for_timeout(2000)
            
            # Click Search (Use a[onclick="searchModify();"])
            print('Clicking Search (조회)...')
            await page.locator('a[onclick="searchModify();"]').first.click()
            await page.wait_for_timeout(3000)
            
            # Check if there is an error bootbox alert opened
            bootbox_alert = page.locator('.bootbox-alert .bootbox-accept')
            if await bootbox_alert.count() > 0 and await bootbox_alert.first.is_visible():
                print('[WARNING] Bootbox alert detected! Clicking OK to close...')
                await bootbox_alert.first.click()
                await page.wait_for_timeout(1500)
                
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00005_search.png')
            print('[SUCCESS] Initial Search completed.')
            
            # Clean up existing items to start fresh
            rows = page.locator('#hq_stock_00005_t01 tbody tr')
            first_row_text = await rows.first.text_content() if await rows.count() > 0 else ""
            if await rows.count() > 0 and '조회된 데이터가 없습니다' not in first_row_text and 'No matching records found' not in first_row_text:
                print('Existing unconfirmed items found. Cleaning up...')
                await page.evaluate("() => { $('#hq_stock_00005_t01').bootstrapTable('checkAll'); }")
                await page.wait_for_timeout(1000)
                
                # Click Delete
                delete_btn = page.locator('a[onclick="deleteGoods();"]').first
                await delete_btn.click()
                await page.wait_for_timeout(2000)
                
                # Confirm popup
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(2500)
                
                # Refresh search
                await page.locator('a[onclick="searchModify();"]').first.click()
                await page.wait_for_timeout(2000)
                print('[SUCCESS] Pre-cleanup done.')
            
            # Step 3: Open Register Modal
            print('Opening Registration Modal...')
            await page.locator('a[onclick="addGoods();"]').first.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00005_add_modal.png')
            
            # Wait for NC0006 store option in modal to load
            print('Waiting for store option NC0006 to load in modal...')
            await page.wait_for_selector('#modal_selectMsPos_ms_select option[value="NC0006"]', state='attached', timeout=10000)
            await page.wait_for_timeout(1000)
            
            # Select store and date in modal
            print('Setting modal parameters...')
            await page.evaluate(f"() => {{ $('#modal_selectMsPos_ms_select').selectpicker('val', '{target_store}').change(); }}")
            await page.evaluate(f"() => {{ $('#modal_surveyDate').val('{today_str}'); }}")
            await page.wait_for_timeout(2000)
            
            # Search inside modal
            print('Clicking modal Search...')
            await page.locator('button[onclick="AddGoodsModal_SearchGoods();"]').first.click()
            await page.wait_for_timeout(4000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00005_add_modal_loaded.png')
            
            # Select first item (T0000001 or similar)
            print('Selecting first goods item in modal...')
            first_checkbox = page.locator('#hq_stock_00005_t02 tbody tr input[type="checkbox"]').first
            if await first_checkbox.count() > 0:
                await first_checkbox.click()
                await page.wait_for_timeout(1000)
                
                # Click "선택" (Confirm select) button
                print('Clicking 선택 (Confirm Select)...')
                await page.locator('#btnMultiSelectModal').first.click()
                await page.wait_for_timeout(2000)
                
                # Handle confirms
                bootbox_ok = page.locator('.bootbox-accept')
                for _ in range(3):
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(2000)
                
                print('[SUCCESS] Selection completed and added to main grid.')
            else:
                print('[FAIL] No goods items found in modal.')
                await browser.close()
                return
            
            # Step 4: Search main grid again to load the added item
            print('Refreshing main grid search...')
            await page.evaluate(f"() => {{ $('#surveyDate').val('{today_str}'); }}")
            await page.evaluate(f"() => {{ $('#selectMsPos_ms_select').selectpicker('val', '{target_store}').change(); }}")
            await page.locator('a[onclick="searchModify();"]').first.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00005_added_list.png')
            
            # Step 5: Input Quantity and Save
            print('Modifying quantity and details...')
            # Find the quantity input field in the grid
            box_input = page.locator('input[id^="input_boxQty_"]').first
            if await box_input.count() > 0:
                await box_input.click()
                await box_input.focus()
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await box_input.press_sequentially('10')
                await page.wait_for_timeout(1500)
                
                # Select a reason
                await page.evaluate("() => { $('select[name=\"select_reason\"]').first().selectpicker('val', '003').change(); }")
                await page.wait_for_timeout(1000)
                
                print('Saving modified slip...')
                await page.locator('a[onclick="saveGoods();"]').first.click()
                await page.wait_for_timeout(2000)
                
                bootbox_ok = page.locator('.bootbox-accept')
                for _ in range(3):
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(2000)
                
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00005_saved_qty.png')
                print('[SUCCESS] Slip details saved successfully.')
                
                # Step 6: Select the item and Click Confirm (확정)
                print('Selecting item to confirm...')
                row_chk = page.locator('#hq_stock_00005_t01 tbody tr input[type="checkbox"]').first
                if await row_chk.count() > 0:
                    await row_chk.click()
                    await page.wait_for_timeout(1000)
                    
                    print('Clicking 확정...')
                    await page.locator('a[onclick="confirmModify();"]').first.click()
                    await page.wait_for_timeout(2000)
                    
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(4000)
                        
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00005_confirmed.png')
                    print('[SUCCESS] Slip confirmed successfully.')
                else:
                    print('[WARNING] Checkbox for confirmation not found.')
            else:
                print('[WARNING] Quantity inputs not found.')
                
            print('All test steps finished.')
            
        except Exception as e:
            print('Error occurred during E2E test:', e)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00005_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
