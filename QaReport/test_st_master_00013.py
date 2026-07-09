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
            
            # Network Response Logger
            def handle_response(response):
                if response.status >= 400:
                    try:
                        print(f"HTTP ERROR {response.status}: {response.request.method} {response.url}")
                    except Exception as ex:
                        print(f"HTTP ERROR {response.status} on URL: {response.url}")
            page.on("response", handle_response)
            
            print('=== STARTING TEST: st_master_00013 (ST Vendor Goods Status) ===')
            
            # Step 1: Login (fnbcafe / 0000)
            await login(page, 'fnbcafe', '0000')
            
            # Step 2: Navigate to target page
            print('Navigating to st_master_00013...')
            await page.goto('http://localhost:8080/backoffice/view/main/st/master/st_master_00013')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#st_master_00013_t01', timeout=10000)
            
            # Step 3: Click Search Button directly
            print('Clicking Search Button (All Vendors)...')
            await page.locator('#st_master_00013_search_btn').click()
            await page.wait_for_timeout(4000)
            
            # Save screenshot of all results
            os.makedirs('d:/hmTest/backoffice/QaReport', exist_ok=True)
            search_screenshot_path = 'd:/hmTest/backoffice/QaReport/st_master_00013_search.png'
            await page.screenshot(path=search_screenshot_path)
            print(f'All goods result screenshot saved to {search_screenshot_path}')
            
            # Verify records loaded
            no_records = page.locator('#st_master_00013_t01 tbody tr.no-records-found')
            records_count = await page.locator('#st_master_00013_t01 tbody tr').count()
            if await no_records.count() > 0 or records_count == 0:
                print('[WARNING] No records found on table.')
            else:
                print(f'Table loaded with {records_count} rows.')
                
            # Step 4: Filter by Vendor 000001
            print('Waiting for vendor selector to load...')
            await page.wait_for_selector('#searchVendr_vendor_select option', state='attached', timeout=10000)
            print('Selecting vendor 000001...')
            await page.evaluate("() => { $('#searchVendr_vendor_select').selectpicker('val', '000001').change(); }")
            await page.wait_for_timeout(1000)
            
            # Click Search Button again
            print('Clicking Search Button (Filtered by Vendor 000001)...')
            await page.locator('#st_master_00013_search_btn').click()
            await page.wait_for_timeout(4000)
            
            # Save screenshot of filtered results
            filter_screenshot_path = 'd:/hmTest/backoffice/QaReport/st_master_00013_filter.png'
            await page.screenshot(path=filter_screenshot_path)
            print(f'Filtered result screenshot saved to {filter_screenshot_path}')
            
            # Verify filtered records
            filtered_count = await page.locator('#st_master_00013_t01 tbody tr').count()
            print(f'Filtered table loaded with {filtered_count} rows.')
            
            print('E2E Test for st_master_00013 completed successfully!')
            
        except Exception as e:
            print('Error occurred during st_master_00013 E2E test:', e)
            await page.screenshot(path='d:/hmTest/backoffice/QaReport/st_master_00013_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
