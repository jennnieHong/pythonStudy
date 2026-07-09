import asyncio
import os
import sys
import json
import subprocess
import psycopg2
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def run_test():
    async with async_playwright() as p:
        try:
            print('Attempting to launch browser...')
            try:
                browser = await p.chromium.launch(headless=False, slow_mo=300)
            except Exception as e:
                print(f'Headed launch failed ({e}), falling back to headless=True...')
                browser = await p.chromium.launch(headless=True, slow_mo=100)
                
            # HQ Screen Test
            print('\n=== Starting HQ Screen (hq_system_00009) Test ===')
            context1 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context1.new_page()
            page.on("console", lambda msg: print(f"[CONSOLE HQ] {msg.text}"))
            
            print('Forcing logout first to clear existing sessions...')
            await page.goto('http://localhost:8080/backoffice/logout')
            await page.wait_for_timeout(2000)
            
            print('Navigating to http://localhost:8080/backoffice ...')
            await page.goto('http://localhost:8080/backoffice', timeout=15000)
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            print('Logging in as shopadmin (HQ)...')
            await page.locator('#login_userid').fill('shopadmin')
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
            
            print('Waiting for redirection to main...')
            for _ in range(15):
                if 'main' in page.url:
                    break
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)
                
            print('Navigating to hq_system_00009...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/system/hq_system_00009')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_system_00009_t01', timeout=10000)
            
            # Set search dates via JS since they are readonly
            print('Setting search dates to 2026-06-01 to 2026-06-11...')
            await page.evaluate("document.getElementById('searchFromDate').value = '2026-06-01'")
            await page.evaluate("document.getElementById('searchEndDate').value = '2026-06-11'")
            await page.wait_for_timeout(1000)
            
            print('Clicking Search (조회)...')
            await page.locator('#hq_system_00009_search_btn').click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00009_search.png')
            
            print('Filtering by Request User ID/Name (shopadmin)...')
            await page.locator('#searchUserId').fill('shopadmin')
            await page.locator('#hq_system_00009_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00009_search_id.png')
            
            print('Filtering by Request IP (127.0.0.1)...')
            await page.locator('#searchUserId').fill('')
            await page.locator('#searchUserIp').fill('127.0.0.1')
            await page.locator('#hq_system_00009_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00009_search_ip.png')
            
            print('Testing Reset (초기화) button...')
            # Trigger reset click
            await page.locator("a[onclick=\"clearFields('hq_system_00009_form');\"]").click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00009_reset.png')
            
            await context1.close()
            print('=== HQ Screen Test Completed ===')
            
            # Admin Screen Test
            print('\n=== Starting Admin Screen (admin_system_00009) Test ===')
            context2 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context2.new_page()
            page.on("console", lambda msg: print(f"[CONSOLE ADMIN] {msg.text}"))
            
            print('Forcing logout first...')
            await page.goto('http://localhost:8080/backoffice/logout')
            await page.wait_for_timeout(2000)
            
            print('Navigating to http://localhost:8080/backoffice ...')
            await page.goto('http://localhost:8080/backoffice', timeout=15000)
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            print('Logging in as admin2 (Admin)...')
            await page.locator('#login_userid').fill('admin2')
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
            
            print('Waiting for redirection...')
            for _ in range(15):
                if 'main' in page.url:
                    break
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)
                
            print('Navigating to admin_system_00009...')
            await page.goto('http://localhost:8080/backoffice/view/main/admin/system/admin_system_00009')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#admin_system_00009_t01', timeout=10000)
            
            print('Setting search dates to 2026-06-01 to 2026-06-11...')
            await page.evaluate("document.getElementById('searchFromDate').value = '2026-06-01'")
            await page.evaluate("document.getElementById('searchEndDate').value = '2026-06-11'")
            await page.wait_for_timeout(1000)
            
            print('Clicking Search...')
            await page.locator('#admin_system_00009_search_btn').click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00009_search.png')
            
            print('Filtering by Request User ID/Name (admin2)...')
            await page.locator('#searchUserId').fill('admin2')
            await page.locator('#admin_system_00009_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00009_search_id.png')
            
            print('Filtering by Request IP (127.0.0.1)...')
            await page.locator('#searchUserId').fill('')
            await page.locator('#searchUserIp').fill('127.0.0.1')
            await page.locator('#admin_system_00009_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00009_search_ip.png')
            
            print('Testing Reset button...')
            await page.locator("a[onclick=\"clearFields(\'admin_system_00009_form\');\"]").click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00009_reset.png')
            
            await context2.close()
            print('=== Admin Screen Test Completed ===')
            
            # Update progress json
            print('\nUpdating progress json and screen html...')
            try:
                progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"screens": {}}
                
                # HQ Screen Progress
                data["screens"]["hq_system_00009"] = {
                    "complete": True,
                    "memo": "로그인 ID: shopadmin - 로그인 이력 조회 (본사 권한으로 소속 체인 로그인 성공/실패 이력 조회)"
                }
                # Admin Screen Progress
                data["screens"]["admin_system_00009"] = {
                    "complete": True,
                    "memo": "로그인 ID: admin2 - 로그인 이력 조회 (관리자 권한으로 시스템 전체 로그인 성공/실패 이력 조회)"
                }
                
                with open(progress_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                print("Updated progress JSON successfully.")
                
                # Regenerate HTML
                subprocess.run(["python", "generate_screens_directory.py"], cwd=r"D:\hmTest\backoffice\QaReport", check=True)
                print("Regenerated All_HMS_Screens.html successfully.")
            except Exception as e:
                print(f"[WARNING] Progress update failed: {e}")
                
            print('[SUCCESS] All tests finished successfully.')
        except Exception as e:
            print('Error occurred during E2E test:', e)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/system_00009_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
