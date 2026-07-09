import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def login(page, user_id, password):
    print(f'Attempting to login as {user_id}...')
    await page.goto('http://localhost:8080/backoffice')
    await page.wait_for_load_state('networkidle')
    
    # Check if already logged in
    if 'main' in page.url or await page.locator('.logout-btn, a[href*="logout"]').count() > 0:
        print('Already logged in. Force logging out...')
        try:
            await page.goto('http://localhost:8080/backoffice/logout')
            await page.wait_for_timeout(2000)
        except Exception:
            pass
        await page.goto('http://localhost:8080/backoffice')
        await page.wait_for_load_state('networkidle')
        
    await page.locator('#login_userid').fill(user_id)
    await page.locator('#login_password').fill(password)
    await page.locator('button[type="submit"]').first.click()
    
    # Handle duplicate session popups if any
    for _ in range(15):
        await page.wait_for_timeout(500)
        if 'main' in page.url:
            break
        bootbox_accept = page.locator('.bootbox-accept')
        if await bootbox_accept.count() > 0 and await bootbox_accept.first.is_visible():
            print('Duplicate login session detected. Accepting to disconnect other session...')
            await bootbox_accept.first.click()
            await page.wait_for_timeout(1000)
            
    try:
        await page.wait_for_url('**/view/main/**', timeout=8000)
        print(f'Successfully logged in as {user_id}.')
    except Exception:
        print(f'Login navigation wait finished. Current URL: {page.url}')
        if 'main' not in page.url:
            raise Exception(f"Failed to login as {user_id}. URL: {page.url}")

async def run_test():
    async with async_playwright() as p:
        try:
            print('Launching browser...')
            browser = await p.chromium.launch(headless=True, slow_mo=100)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            # Browser Console Log
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            
            # Network Response Logger for debugging 404 errors
            def handle_response(response):
                if response.status >= 400:
                    try:
                        print(f"HTTP ERROR {response.status}: {response.request.method} {response.url}")
                    except Exception as ex:
                        print(f"HTTP ERROR {response.status} on URL: {response.url} (Error getting request details: {ex})")
            page.on("response", handle_response)
            
            print('=== STARTING TEST: hq_vendor_00017 (HQ Vendor Inbound Aggregate) ===')
            
            # Step 1: Login
            await login(page, 'shopadmin', '0000')
            
            # Step 2: Navigate to target page
            print('Navigating to hq_vendor_00017...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00017')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_vendor_00017_t01', timeout=10000)
            
            # Step 3: Select store NC0007 and Date 2024-02-01
            print('Setting date range to 2024-02-01...')
            await page.evaluate("() => { $('#searchFromDate').datepicker('setDate', '2024-02-01'); }")
            await page.evaluate("() => { $('#searchEndDate').datepicker('setDate', '2024-02-01'); }")
            await page.wait_for_timeout(1000)
            
            print('Waiting for store selector to load...')
            await page.wait_for_selector('#selectMsPos_ms_select option', state='attached', timeout=10000)
            print('Selecting store NC0007...')
            await page.evaluate("() => { $('#selectMsPos_ms_select').selectpicker('val', 'NC0007').change(); }")
            await page.wait_for_timeout(1000)
            
            # Step 4: Click Search Button
            print('Clicking Search Button...')
            await page.locator('#hq_vendor_00017_search_btn').click()
            await page.wait_for_timeout(4000)
            
            # Save screenshot of search results
            os.makedirs('d:/hmTest/backoffice/QaReport', exist_ok=True)
            search_screenshot_path = 'd:/hmTest/backoffice/QaReport/hq_vendor_00017_search.png'
            await page.screenshot(path=search_screenshot_path)
            print(f'Search result screenshot saved to {search_screenshot_path}')
            
            # Verify records loaded
            no_records = page.locator('#hq_vendor_00017_t01 tbody tr.no-records-found')
            records_count = await page.locator('#hq_vendor_00017_t01 tbody tr').count()
            if await no_records.count() > 0 or records_count == 0:
                print('[WARNING] No records found on table.')
            else:
                print(f'Table loaded with {records_count} rows.')
                
            # Step 5: Test Print Function
            print('Clicking Print Button...')
            await page.locator('#hq_vendor_00017_printOrder_btn').click()
            await page.wait_for_timeout(4000)
            
            # Check if print wrap is filled with data
            print_wrap_html = await page.evaluate("() => $('#print_wrap').html()")
            print(f"print_wrap length: {len(print_wrap_html) if print_wrap_html else 0} characters.")
            
            # Temporarily show print wrapper to capture the print layout
            print('Revealing print wrap for capture...')
            await page.evaluate("() => { $('#print_wrap').css({ 'display': 'block', 'position': 'absolute', 'top': 0, 'left': 0, 'width': '100%', 'z-index': 99999, 'background': 'white' }); }")
            await page.wait_for_timeout(2000)
            
            print_screenshot_path = 'd:/hmTest/backoffice/QaReport/hq_vendor_00017_print.png'
            await page.screenshot(path=print_screenshot_path)
            print(f'Print wrapper screenshot saved to {print_screenshot_path}')
            
            # Hide it back
            await page.evaluate("() => { $('#print_wrap').hide(); }")
            
            print('E2E Test for hq_vendor_00017 completed successfully!')
            
        except Exception as e:
            print('Error occurred during hq_vendor_00017 E2E test:', e)
            await page.screenshot(path='d:/hmTest/backoffice/QaReport/hq_vendor_00017_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
