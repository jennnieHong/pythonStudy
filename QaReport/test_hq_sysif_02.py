import asyncio
import os
import sys
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
            print('Starting Playwright Test for hq_sysif_00002 (Cash 시재 입출금 등록)...')
            
            # Auto-accept dialogs (e.g. bootbox alerts/confirms)
            async def handle_dialog(dialog):
                print(f"[DIALOG] {dialog.message}")
                await dialog.accept()
            page.on("dialog", lambda d: asyncio.create_task(handle_dialog(d)))
            
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
            
            # Force logout if already logged in to ensure clean login
            if 'main' in page.url or await page.locator('.logout-btn, a[href*="logout"]').count() > 0:
                print('Already logged in. Navigating to logout URL to force re-login...')
                await page.goto('http://localhost:8080/backoffice/logout')
                await page.wait_for_timeout(2000)
                await page.goto('http://localhost:8080/backoffice')
                await page.wait_for_load_state('networkidle')
            
            # Login with shopadmin / 0000
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
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_sysif_00002_login_fail.png')
                await browser.close()
                return
                
            # Step 2: Navigate to target screen hq_sysif_00002
            print('Navigating directly to hq_sysif_00002...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/systeminterface/hq_sysif_00002')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_sysif_00002_t01', timeout=10000)
            print('[SUCCESS] Navigated to Cash 시재 입출금 등록 screen.')
            
            # Take screenshot of initial state
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_sysif_00002_initial.png')
            
            # Step 3: Select store NC0011 (매장_강남점 / if_biz_cd = 01, if_shop_cd = 20)
            print('Selecting store NC0011 (강남점)...')
            await page.evaluate("() => { $('#selectMsPos_ms_select').selectpicker('val', 'NC0011'); }")
            await page.wait_for_timeout(1000)
            
            # Step 4: Click [조회] button
            print('Clicking [조회] button...')
            await page.locator('#hq_sysif_00002_searchRegiList_btn').click()
            print('Waiting for search request to execute (expecting timeout or connection exception due to unreachable Tibero)...')
            
            # Let the query run and wait to capture network timeout or error dialog
            await page.wait_for_timeout(7000)
            
            # Capture the screen state after search attempt
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_sysif_00002_searched_error.png')
            print('[SUCCESS] Captured searched state screenshot (expecting empty grid or error due to unreachable Tibero).')
            
        except Exception as err:
            print(f'[ERROR] Test encountered an exception: {err}')
        finally:
            await browser.close()
            print('Browser closed. Test finished.')

if __name__ == '__main__':
    asyncio.run(run_test())
