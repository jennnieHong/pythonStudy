import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def login(page, user_id, password):
    print(f'Attempting to login as {user_id}...')
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

async def run_store_test(page):
    print('\n=== STARTING STORE TEST: st_vendor_00012 ===')
    # Login as fnbcafe (Store NC0007)
    await login(page, 'fnbcafe', '0000')
    
    # Navigate to st_vendor_00012
    print('Navigating to st_vendor_00012...')
    await page.goto('http://localhost:8080/backoffice/view/main/st/vendor/st_vendor_00012')
    await page.wait_for_timeout(3000)
    await page.wait_for_selector('#st_vendor_00012_t01', timeout=10000)
    
    # Set date range to 2026-06-04 (NC0007 has data here)
    print('Setting date range to 2026-06-04...')
    await page.evaluate("() => { $('#searchFromDate').datepicker('setDate', '2026-06-04'); }")
    await page.evaluate("() => { $('#searchEndDate').datepicker('setDate', '2026-06-04'); }")
    await page.wait_for_timeout(1000)
    
    # Click Search
    print('Clicking Search Button...')
    await page.locator('#st_vendor_00012_search_btn').click()
    await page.wait_for_timeout(4000)
    
    # Take screenshot of search results
    screenshot_dir = 'D:/hmTest/backoffice/QaReport'
    os.makedirs(screenshot_dir, exist_ok=True)
    
    search_screenshot = os.path.join(screenshot_dir, 'st_vendor_00012_search.png')
    await page.screenshot(path=search_screenshot)
    print(f'Search screenshot saved to {search_screenshot}')
    
    # Check records loaded and click details
    click_target = page.locator('#st_vendor_00012_t01 tbody tr td.table-onclick').first
    if await click_target.count() > 0:
        print('Clicking purchase request cell to load details...')
        await click_target.click()
        await page.wait_for_timeout(4000)
        
        detail_screenshot = os.path.join(screenshot_dir, 'st_vendor_00012_detail.png')
        await page.screenshot(path=detail_screenshot)
        print(f'Detail screenshot saved to {detail_screenshot}')
    else:
        print('[WARNING] No clickable purchReqNo found in table.')
        
    # Reset
    print('Clicking reset button...')
    await page.locator('#clear_form_btn').click()
    await page.wait_for_timeout(2000)
    
    reset_screenshot = os.path.join(screenshot_dir, 'st_vendor_00012_reset.png')
    await page.screenshot(path=reset_screenshot)
    print(f'Reset screenshot saved to {reset_screenshot}')

async def run_hq_test(page):
    print('\n=== STARTING HQ TEST: hq_vendor_00014 ===')
    # Login as shopadmin (HQ user)
    await login(page, 'shopadmin', '0000')
    
    # Navigate to hq_vendor_00014
    print('Navigating to hq_vendor_00014...')
    await page.goto('http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00014')
    await page.wait_for_timeout(3000)
    await page.wait_for_selector('#hq_vendor_00014_t01', timeout=10000)
    
    # Set date range to 2026-06-04
    print('Setting date range to 2026-06-04...')
    await page.evaluate("() => { $('#searchFromDate').datepicker('setDate', '2026-06-04'); }")
    await page.evaluate("() => { $('#searchEndDate').datepicker('setDate', '2026-06-04'); }")
    await page.wait_for_timeout(1000)
    
    # Select Store NC0007 (CAFE)
    print('Waiting for store selector...')
    await page.wait_for_selector('#selectMsPos_ms_select option', state='attached', timeout=10000)
    print('Selecting store NC0007...')
    await page.evaluate("() => { $('#selectMsPos_ms_select').selectpicker('val', 'NC0007').change(); }")
    await page.wait_for_timeout(1000)
    
    # Click Search
    print('Clicking Search Button...')
    await page.locator('#hq_vendor_00014_search_btn').click()
    await page.wait_for_timeout(4000)
    
    screenshot_dir = 'D:/hmTest/backoffice/QaReport'
    search_screenshot = os.path.join(screenshot_dir, 'hq_vendor_00014_search.png')
    await page.screenshot(path=search_screenshot)
    print(f'Search screenshot saved to {search_screenshot}')
    
    # Click details
    click_target = page.locator('#hq_vendor_00014_t01 tbody tr td.table-onclick').first
    if await click_target.count() > 0:
        print('Clicking purchase request cell to load details...')
        await click_target.click()
        await page.wait_for_timeout(4000)
        
        detail_screenshot = os.path.join(screenshot_dir, 'hq_vendor_00014_detail.png')
        await page.screenshot(path=detail_screenshot)
        print(f'Detail screenshot saved to {detail_screenshot}')
    else:
        print('[WARNING] No clickable purchReqNo found in table.')
        
    # Reset
    print('Clicking reset button...')
    await page.locator('#clear_form_btn').click()
    await page.wait_for_timeout(2000)
    
    reset_screenshot = os.path.join(screenshot_dir, 'hq_vendor_00014_reset.png')
    await page.screenshot(path=reset_screenshot)
    print(f'Reset screenshot saved to {reset_screenshot}')

async def main():
    async with async_playwright() as p:
        try:
            print('Launching browser (headless=False)...')
            # Run with headless=False as explicitly requested by user
            browser = await p.chromium.launch(headless=False, slow_mo=100)
            
            # Store E2E Test (fnbcafe / Store NC0007)
            print('Starting Store Test Session...')
            context1 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page1 = await context1.new_page()
            
            # Hook browser logs
            page1.on("console", lambda msg: print(f"STORE CONSOLE: {msg.text}"))
            
            # Hook HTTP errors
            def handle_resp1(response):
                if response.status >= 400:
                    try:
                        print(f"STORE HTTP ERROR {response.status}: {response.request.method} {response.url}")
                    except Exception:
                        pass
            page1.on("response", handle_resp1)
            
            await run_store_test(page1)
            await context1.close()
            print('Store Test Session closed.')
            
            # HQ E2E Test (shopadmin)
            print('\nStarting HQ Test Session...')
            context2 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page2 = await context2.new_page()
            
            # Hook browser logs
            page2.on("console", lambda msg: print(f"HQ CONSOLE: {msg.text}"))
            
            # Hook HTTP errors
            def handle_resp2(response):
                if response.status >= 400:
                    try:
                        print(f"HQ HTTP ERROR {response.status}: {response.request.method} {response.url}")
                    except Exception:
                        pass
            page2.on("response", handle_resp2)
            
            await run_hq_test(page2)
            await context2.close()
            print('HQ Test Session closed.')
            
            print('\n=== ALL E2E TESTS COMPLETED SUCCESSFULY ===')
            
        except Exception as e:
            print('An error occurred during test execution:', e)
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
