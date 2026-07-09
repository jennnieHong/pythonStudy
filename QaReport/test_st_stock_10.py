import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def run_test():
    async with async_playwright() as p:
        try:
            print('Attempting to launch browser in headless mode...')
            browser = await p.chromium.launch(headless=False, slow_mo=800)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            # Listen to console messages and network requests
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            
            async def log_response(response):
                if "st_stock_00010" in response.url:
                    try:
                        print(f"API Response [{response.url}]: {await response.text()[:500]}")
                    except Exception:
                        pass
            
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
            
            # Login with fnbcafe / 0000
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
                    await page.wait_for_timeout(3000)
            
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
            
            # Step 2: Navigate to target screen (st_stock_00010)
            print('Navigating to st_stock_00010 (Store Transfer)...')
            await page.goto('http://localhost:8080/backoffice/view/main/st/stock/st_stock_00010')
            await page.wait_for_timeout(4000)
            
            # Test Tab 1: 전표등록 (Send)
            print('--- Testing Send (전표등록) Tab ---')
            print('Setting date range from 2024-01-01 to today for Send Tab...')
            await page.evaluate("() => { $('#searchFromDate').datepicker('setDate', '2024-01-01'); }")
            await page.evaluate("() => { $('#searchEndDate').datepicker('setDate', 'today'); }")
            await page.wait_for_timeout(1000)
            
            print('Clicking Send Search button...')
            await page.locator('#st_stock_00010_search_btn_send').click()
            await page.wait_for_timeout(3000)
            
            # Capture Send tab screen
            os.makedirs('D:/hmTest/backoffice/QaReport', exist_ok=True)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00010_send.png')
            print('Captured Send tab screen.')
            
            # Test Tab 2: 입고확정 (Recv)
            print('--- Testing Recv (입고확정) Tab ---')
            # Click the Recv Tab Link
            await page.locator('text="입고확정"').first.click()
            await page.wait_for_timeout(2000)
            
            print('Setting date range from 2024-01-01 to today for Recv Tab...')
            await page.evaluate("() => { $('#searchFromDate_recv').datepicker('setDate', '2024-01-01'); }")
            await page.evaluate("() => { $('#searchEndDate_recv').datepicker('setDate', 'today'); }")
            await page.wait_for_timeout(1000)
            
            print('Clicking Recv Search button...')
            await page.locator('#st_stock_00010_search_btn_recv').click()
            await page.wait_for_timeout(3000)
            
            # Capture Recv tab screen
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00010_recv.png')
            print('Captured Recv tab screen.')
            
            # If there are records in the recv table, click the first one to test details mapping
            no_data = page.locator('#st_stock_00010_t02 tbody tr.no-records-found')
            rows = page.locator('#st_stock_00010_t02 tbody tr')
            
            if await no_data.count() == 0 and await rows.count() > 0:
                print(f'Rows detected in recv table: {await rows.count()}. Clicking the first row to select it...')
                await rows.first.click()
                await page.wait_for_timeout(1000)
                print('Clicking the Slip No link to load details...')
                await page.locator('#st_stock_00010_t02 tbody tr a.text-primary').first.click()
                await page.wait_for_timeout(3000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00010_recv_detail.png')
                print('Captured Recv detail screen.')
                
                # Perform Confirm Transaction
                print('Clicking Confirm button to open Confirm Modal...')
                await page.locator('#st_stock_00010_confirm_btn_recv').click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00010_recv_modal.png')
                print('Captured Recv modal screen.')
                
                print('Clicking Save/Confirm button inside modal...')
                await page.locator('#recvConfirmModalM02').click()
                await page.wait_for_timeout(2000)
                
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0:
                    confirm_text = await page.locator('.bootbox-body').first.inner_text()
                    print(f'Bootbox confirm detected: {confirm_text}')
                    print('Accepting bootbox confirmation...')
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(3000)
                    
                    # Handle success alert or error alert
                    bootbox_ok_alert = page.locator('.bootbox-accept')
                    if await bootbox_ok_alert.count() > 0:
                        alert_text = await page.locator('.bootbox-body').first.inner_text()
                        print(f'Alert after confirm: {alert_text}')
                        await bootbox_ok_alert.first.click()
                        await page.wait_for_timeout(2000)
                        
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00010_recv_confirmed.png')
                print('Captured Recv confirmed screen.')
            else:
                print('No recv records found.')

        except Exception as e:
            print('Error occurred:', e)
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
