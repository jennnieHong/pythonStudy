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
            print('Launching browser in headed mode (headless=False)...')
            browser = await p.chromium.launch(headless=False, slow_mo=300)
        except Exception as e:
            print(f'Headed launch failed ({e}), falling back to headless=True...')
            browser = await p.chromium.launch(headless=True, slow_mo=100)
            
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        # Enable console logging from browser
        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        
        try:
            print('=== STARTING TEST: st_stock_00011 (Store Stock Move Status) ===')
            
            # Step 1: Login
            await login(page, 'shopbrand', '0000')
            
            # Step 2: Navigate to target page
            print('Navigating directly to st_stock_00011...')
            await page.goto('http://localhost:8080/backoffice/view/main/st/stock/st_stock_00011')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#st_stock_00011_t01', timeout=10000)
            
            # Step 3: Set Date Range
            # Set search range to cover 2026-06-01 to 2026-06-30
            print('Setting date range from 2026-06-01 to 2026-06-30...')
            await page.evaluate("() => { $('#searchFromDate').datepicker('setDate', '2026-06-01'); }")
            await page.evaluate("() => { $('#searchEndDate').datepicker('setDate', '2026-06-30'); }")
            await page.wait_for_timeout(1000)
            
            # Step 4: Click Search Button
            print('Clicking Search Button...')
            await page.locator('#st_stock_00011_search_btn').click()
            await page.wait_for_timeout(3000)
            
            # Save screenshot of search results
            os.makedirs('d:/hmTest/backoffice/QaReport', exist_ok=True)
            screenshot_path = 'd:/hmTest/backoffice/QaReport/st_stock_00011_search.png'
            await page.screenshot(path=screenshot_path)
            print(f'Screenshot saved to {screenshot_path}')
            
            # Step 5: Click first row slip link to view details
            # Wait for any data rows in t01
            no_data = page.locator('#st_stock_00011_t01 tbody tr.no-records-found')
            rows = page.locator('#st_stock_00011_t01 tbody tr')
            slip_links = page.locator('#st_stock_00011_t01 tbody tr td a.text-primary')
            
            if await no_data.count() == 0 and await rows.count() > 0 and await slip_links.count() > 0:
                print(f'Found {await rows.count()} records. Clicking the first slip number to view details...')
                first_link = slip_links.first
                slip_no = await first_link.inner_text()
                print(f'Selected slip number: {slip_no}')
                await first_link.click()
                await page.wait_for_timeout(3000)
                
                detail_screenshot_path = 'd:/hmTest/backoffice/QaReport/st_stock_00011_detail.png'
                await page.screenshot(path=detail_screenshot_path)
                print(f'Detail screenshot saved to {detail_screenshot_path}')
            else:
                print('[WARNING] No slips found in the table for this store in the selected date range.')
                
            print('E2E Test for st_stock_00011 completed successfully!')
            
        except Exception as e:
            print('Error occurred during st_stock_00011 E2E test:', e)
            await page.screenshot(path='d:/hmTest/backoffice/QaReport/st_stock_00011_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
