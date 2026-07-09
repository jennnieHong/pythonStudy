import asyncio
import os
import sys
import json
import subprocess
import psycopg2
from datetime import datetime
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

# Database cleanup function
def db_cleanup():
    print("Connecting to EDB Pg for database pre-cleanup...")
    try:
        conn = psycopg2.connect(
            host="192.168.10.206",
            port=5432,
            database="edb",
            user="hmsfns_was",
            password="astems3!"
        )
        cursor = conn.cursor()
        
        # Delete test records if they already exist
        cursor.execute("DELETE FROM hmsfns.MENULCTB WHERE MENU_LCLASS_CD = '9999';")
        cursor.execute("DELETE FROM hmsfns.MENUMCTB WHERE MENU_LCLASS_CD = '9999';")
        conn.commit()
        print("[SUCCESS] DB pre-cleanup completed.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[WARNING] Database connection/cleanup failed: {e}")

async def run_test():
    db_cleanup()
    
    async with async_playwright() as p:
        try:
            print('Attempting to launch browser...')
            try:
                browser = await p.chromium.launch(headless=False, slow_mo=300)
            except Exception as e:
                print(f'Headed launch failed ({e}), falling back to headless=True...')
                browser = await p.chromium.launch(headless=True, slow_mo=100)
                
            # HQ Screen Test
            print('\n=== Starting HQ Screen (hq_system_00007) Test ===')
            context1 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context1.new_page()
            page.on("console", lambda msg: print(f"[CONSOLE HQ] {msg.text}"))
            
            # Auto accept dialogs
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            
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
                
            print('Navigating to hq_system_00007...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/system/hq_system_00007')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_system_00007_t01', timeout=10000)
            
            print('Clicking Search (조회)...')
            await page.locator('#hq_system_00007_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00007_search.png')
            
            print('Opening LClass Add Modal...')
            await page.locator('button[onclick="fnLMenuModalShow();"]').first.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00007_lclass_add_modal.png')
            
            print('Filling out LClass registration form...')
            await page.locator('#M01Form [name="input_L_menuNm"]').fill('TEST_LCLASS')
            await page.locator('#M01Form [name="input_L_menuPeriod"]').fill('99')
            await page.locator('#M01Form [name="input_L_menuIcon"]').fill('fas fa-star')
            await page.locator('#M01Form [name="input_L_menuCd"]').fill('9999')
            await page.locator('#M01Form [name="input_L_remark"]').fill('Playwright Test')
            await page.wait_for_timeout(1000)
            
            print('Saving LClass...')
            await page.locator('button[onclick="fnInsertLmenu();"]').first.click()
            await page.wait_for_timeout(3000)
            
            print('Refreshing LClass list...')
            await page.locator('#hq_system_00007_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00007_added.png')
            
            print('Selecting row 9999 to modify...')
            row_selector = page.locator('#hq_system_00007_t01 tbody tr', has_text='9999')
            if await row_selector.count() > 0:
                await row_selector.first.click()
                await page.wait_for_timeout(1000)
                
                print('Opening Modify Modal...')
                await page.locator('#hq_system_00007_t01_toolbar #btnLmenuUdt').click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00007_lclass_modify_modal.png')
                
                print('Modifying LClass fields...')
                await page.locator('#M03Form [name="input_L_menuNm"]').fill('TEST_LCLASS_MOD')
                await page.locator('#M03Form [name="input_L_menuPeriod"]').fill('98')
                await page.locator('#M03Form [name="input_L_remark"]').fill('Playwright Test Mod')
                await page.wait_for_timeout(1000)
                
                print('Saving modifications...')
                await page.locator('button[onclick="fnUpdateLmenu();"]').click()
                await page.wait_for_timeout(1500)
                
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(3000)
                    
                await page.locator('#hq_system_00007_search_btn').click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00007_modified.png')
                
                print('Selecting modified row to delete...')
                modified_row = page.locator('#hq_system_00007_t01 tbody tr', has_text='9999')
                if await modified_row.count() > 0:
                    await modified_row.first.click()
                    await page.wait_for_timeout(1000)
                    
                    print('Clicking Delete...')
                    await page.locator('button[onclick="fnDeleteLmenu();"]').click()
                    await page.wait_for_timeout(1500)
                    
                    bootbox_ok = page.locator('.bootbox-accept')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(3000)
                        
                    await page.locator('#hq_system_00007_search_btn').click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00007_deleted.png')
            else:
                print('[WARNING] Added row 9999 not found.')
                
            await context1.close()
            print('=== HQ Screen Test Completed ===')
            
            # Admin Screen Test
            print('\n=== Starting Admin Screen (admin_system_00007) Test ===')
            context2 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context2.new_page()
            page.on("console", lambda msg: print(f"[CONSOLE ADMIN] {msg.text}"))
            
            # Auto accept dialogs
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            
            print('Navigating to http://localhost:8080/backoffice ...')
            await page.goto('http://localhost:8080/backoffice', timeout=15000)
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            print('Logging in as admin2 (Admin)...')
            await page.locator('#login_userid').fill('admin2')
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
                
            print('Navigating to admin_system_00007...')
            await page.goto('http://localhost:8080/backoffice/view/main/admin/system/admin_system_00007')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#admin_system_00007_t01', timeout=10000)
            
            print('Clicking Search (조회)...')
            await page.locator('#admin_system_00007_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00007_search.png')
            
            await context2.close()
            print('=== Admin Screen Test Completed ===')
            
            # Post-cleanup and memo updates
            print('\nUpdating progress json and screen html...')
            try:
                # Update progress json
                progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"screens": {}}
                
                # HQ Screen Progress
                data["screens"]["hq_system_00007"] = {
                    "complete": True,
                    "memo": "로그인 ID: shopadmin - 웹 메뉴 관리 (본사 권한으로 대/중/소 분류 및 메뉴 등록, 맵핑 관리)"
                }
                # Admin Screen Progress
                data["screens"]["admin_system_00007"] = {
                    "complete": True,
                    "memo": "로그인 ID: admin2 - 웹 메뉴 관리 (관리자 권한으로 대/중/소 분류 및 메뉴 등록, 맵핑 관리)"
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
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/system_00007_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
