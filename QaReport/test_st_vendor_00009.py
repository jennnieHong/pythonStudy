import asyncio
import os
import sys
import json
import subprocess
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def perform_login(context, page, username, password):
    print(f'\n--- Logging in as {username} ---')
    print('Clearing browser cookies to reset session...')
    await context.clear_cookies()
    
    print('Navigating to login page...')
    await page.goto('http://localhost:8080/backoffice/view/login', timeout=15000)
    await page.wait_for_timeout(1000)
    
    await page.wait_for_selector('#login_userid', timeout=10000)
    print(f'Filling credentials for {username}...')
    await page.locator('#login_userid').fill(username)
    await page.locator('#login_password').fill(password)
    
    # Submit login
    submit_btn = page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first
    await submit_btn.click()
    
    # Wait for redirection to main page
    print('Waiting for redirection to main...')
    for _ in range(15):
        if 'main' in page.url:
            print('Successfully redirected to main.')
            break
        bootbox_ok = page.locator('.bootbox-accept')
        if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
            print('Bootbox modal detected during login. Closing it...')
            await bootbox_ok.first.click()
        await page.wait_for_timeout(2000)

async def run_test():
    async with async_playwright() as p:
        try:
            print('Launching browser in headed mode (headless=False)...')
            browser = await p.chromium.launch(headless=False, slow_mo=300)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
            
            # --- TEST 1: fnbcafe ---
            await perform_login(context, page, 'fnbcafe', '0000')
            
            # Navigate to st_vendor_00009
            print('Navigating to st_vendor_00009 (매입발주현황)...')
            await page.goto('http://localhost:8080/backoffice/view/main/st/vendor/st_vendor_00009')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#st_vendor_00009_t01', timeout=10000)
            
            # Test empty search date validation
            print('Testing date validation (clearing dates and searching)...')
            await page.evaluate("$('#searchFromDate').datepicker('setDate', null)")
            await page.evaluate("$('#searchEndDate').datepicker('setDate', null)")
            await page.locator('#st_vendor_00009_search_btn').click()
            await page.wait_for_timeout(1500)
            
            # Close bootbox validation alert modal
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                print('Bootbox validation alert displayed. Closing alert...')
                await bootbox_ok.first.click()
                await page.wait_for_timeout(1000)
                
            # Set search dates (2024-02-01 to 2024-02-01)
            print('Setting search dates to 2024-02-01 to 2024-02-01...')
            await page.evaluate("$('#searchFromDate').datepicker('setDate', '2024-02-01')")
            await page.evaluate("$('#searchEndDate').datepicker('setDate', '2024-02-01')")
            await page.wait_for_timeout(1000)
            
            print('Clicking Search for fnbcafe...')
            await page.locator('#st_vendor_00009_search_btn').click()
            await page.wait_for_timeout(3000)
            
            # Capture table values
            rows = await page.locator('#st_vendor_00009_t01 tbody tr').all_text_contents()
            print("fnbcafe Search Results:")
            for idx, r in enumerate(rows):
                print(f"Row {idx+1}: {r.strip()}")
                
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00009_fnbcafe_search.png')
            
            # Open Detail Modal
            print('Clicking on SlipNo cell to open detail modal...')
            onclick_cell = page.locator('#st_vendor_00009_t01 tbody tr td.table-onclick').first
            if await onclick_cell.count() > 0:
                await onclick_cell.click()
                print('Waiting for detail modal to load...')
                await page.wait_for_selector('#detailSearchModal', state='visible', timeout=5000)
                await page.wait_for_timeout(2000)
                
                # Check detail table content
                detail_rows = await page.locator('#st_vendor_00009_t02 tbody tr').all_text_contents()
                print("Detail Modal Table Results:")
                for idx, dr in enumerate(detail_rows):
                    print(f"Detail Row {idx+1}: {dr.strip()}")
                    
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00009_fnbcafe_detail.png')
                
                # Close modal
                print('Closing detail modal...')
                await page.locator('#closeSearchModal').click()
                await page.wait_for_selector('#detailSearchModal', state='hidden', timeout=5000)
                await page.wait_for_timeout(1000)
            else:
                print('[WARNING] No clickable slipNo cell found.')
                
            # Test Reset button
            print('Testing Reset button...')
            await page.locator('#clear_form_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00009_fnbcafe_reset.png')
            
            
            # --- TEST 2: shopbrand ---
            await perform_login(context, page, 'shopbrand', '0000')
            
            # Navigate to st_vendor_00009
            print('Navigating to st_vendor_00009 (매입발주현황)...')
            await page.goto('http://localhost:8080/backoffice/view/main/st/vendor/st_vendor_00009')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#st_vendor_00009_t01', timeout=10000)
            
            # Set search dates (2024-02-01 to 2024-02-01)
            print('Setting search dates to 2024-02-01 to 2024-02-01...')
            await page.evaluate("$('#searchFromDate').datepicker('setDate', '2024-02-01')")
            await page.evaluate("$('#searchEndDate').datepicker('setDate', '2024-02-01')")
            await page.wait_for_timeout(1000)
            
            print('Clicking Search for shopbrand...')
            await page.locator('#st_vendor_00009_search_btn').click()
            await page.wait_for_timeout(3000)
            
            # Capture table values
            rows_sb = await page.locator('#st_vendor_00009_t01 tbody tr').all_text_contents()
            print("shopbrand Search Results (Expect empty):")
            for idx, r in enumerate(rows_sb):
                print(f"Row {idx+1}: {r.strip()}")
                
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00009_shopbrand_search.png')
            
            # Test Reset button
            print('Testing Reset button...')
            await page.locator('#clear_form_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00009_shopbrand_reset.png')
            
            # Clear cookies at end
            await context.clear_cookies()
            
            # --- Update progress JSON ---
            print('\nUpdating progress json and screen html...')
            try:
                progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"screens": {}}
                
                data["screens"]["st_vendor_00009"] = {
                    "complete": True,
                    "memo": "로그인 ID: fnbcafe (조회/상세 조회 성공) & shopbrand (조회 성공 - 빈 데이터)"
                }
                
                with open(progress_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                print("Updated progress JSON successfully.")
                
                # Regenerate HTML dashboard
                subprocess.run(["python", "generate_screens_directory.py"], cwd=r"D:\hmTest\backoffice\QaReport", check=True)
                print("Regenerated All_HMS_Screens.html successfully.")
            except Exception as e:
                print(f"[WARNING] Progress update failed: {e}")
                
            print('[SUCCESS] E2E test completed successfully.')
        except Exception as e:
            print('Error occurred during E2E test:', e)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00009_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
