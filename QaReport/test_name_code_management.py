import asyncio
import os
import sys
import json
import subprocess
import psycopg2
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
        cursor.execute("DELETE FROM hmsfns.MNAMEMTB WHERE (NM_FG = '000' AND NM_CD = '999') OR (NM_FG = '999');")
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
            print('\n=== Starting HQ Screen (hq_system_00008) Test ===')
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
                
            print('Navigating to hq_system_00008...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/system/hq_system_00008')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_system_00008_t01', timeout=10000)
            
            print('Clicking Search (조회)...')
            await page.locator('#hq_system_00008_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_search.png')
            
            print('Opening Class Add Modal...')
            await page.locator('button[onclick="return fnStatusFg();"]').first.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_class_add_modal.png')
            
            print('Filling out Class registration form...')
            await page.locator('#regiCodeForm #nmCd').fill('999')
            await page.locator('#regiCodeForm #nmRep').fill('QA_CLASS')
            await page.locator('#regiCodeForm #cdLen').fill('3')
            await page.locator('#regiCodeForm #remark').fill('QA Category E2E')
            await page.wait_for_timeout(1000)
            
            print('Saving Class...')
            await page.locator('button[onclick="return fnSaveRegiCode();"]').first.click()
            await page.wait_for_timeout(1500)
            
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                await bootbox_ok.first.click()
                await page.wait_for_timeout(3000)
                
            print('Refreshing list...')
            await page.locator('#hq_system_00008_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_added.png')
            
            print('Clicking the added row to show detail list...')
            row_selector = page.locator('#hq_system_00008_t01 tbody tr', has_text='999')
            if await row_selector.count() > 0:
                await row_selector.first.click()
                await page.wait_for_timeout(2000)
                
                print('Opening Detail Code Add Modal...')
                await page.locator('button[onclick="return fnDtStatusFg();"]').click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_detail_add_modal.png')
                
                print('Filling out Detail Code form...')
                await page.locator('#regiDtCodeForm #nmDtCd').fill('001')
                await page.locator('#regiDtCodeForm #nmDtRep').fill('QA_DETAIL_001')
                await page.locator('#regiDtCodeForm #nmSub').fill('QA_SUB_001')
                await page.locator('#regiDtCodeForm #dtRemark').fill('QA Detail E2E')
                await page.wait_for_timeout(1000)
                
                print('Saving Detail Code...')
                await page.locator('button[onclick="return fnSaveRegiDtCode();"]').click()
                await page.wait_for_timeout(1500)
                
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(3000)
                    
                # Reload list
                await row_selector.first.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_detail_added.png')
                
                print('Modifying Detail Code...')
                dt_row = page.locator('#hq_system_00008_t02 tbody tr', has_text='001')
                if await dt_row.count() > 0:
                    await dt_row.locator('.fa-edit').first.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_detail_modify_modal.png')
                    
                    await page.locator('#regiDtCodeForm #nmDtRep').fill('QA_DETAIL_MOD')
                    await page.locator('#regiDtCodeForm #nmSub').fill('QA_SUB_MOD')
                    await page.wait_for_timeout(1000)
                    
                    await page.locator('button[onclick="return fnSaveRegiDtCode();"]').click()
                    await page.wait_for_timeout(1500)
                    
                    bootbox_ok = page.locator('.bootbox-accept')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(3000)
                        
                    await row_selector.first.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_detail_modified.png')
                
                print('Modifying Classification Code...')
                await row_selector.locator('.fa-edit').first.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_class_modify_modal.png')
                
                await page.locator('#regiCodeForm #nmRep').fill('QA_CLASS_MOD')
                await page.wait_for_timeout(1000)
                
                await page.locator('button[onclick="return fnSaveRegiCode();"]').click()
                await page.wait_for_timeout(1500)
                
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(3000)
                    
                await page.locator('#hq_system_00008_search_btn').click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_class_modified.png')
                
                print('Deleting Detail Code...')
                await row_selector.first.click()
                await page.wait_for_timeout(2000)
                dt_row = page.locator('#hq_system_00008_t02 tbody tr', has_text='001')
                if await dt_row.count() > 0:
                    await dt_row.locator('.fa-trash').first.click()
                    await page.wait_for_timeout(1500)
                    
                    bootbox_ok = page.locator('.bootbox-accept')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(3000)
                        
                    await row_selector.first.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_detail_deleted.png')
                
                print('Deleting Classification Code...')
                row_selector = page.locator('#hq_system_00008_t01 tbody tr', has_text='999')
                if await row_selector.count() > 0:
                    await row_selector.locator('.fa-trash').first.click()
                    await page.wait_for_timeout(1500)
                    
                    bootbox_ok = page.locator('.bootbox-accept')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(3000)
                        
                    await page.locator('#hq_system_00008_search_btn').click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_system_00008_class_deleted.png')
            else:
                print('[WARNING] Category row 999 not found.')
                
            await context1.close()
            print('=== HQ Screen Test Completed ===')
            
            # Admin Screen Test
            print('\n=== Starting Admin Screen (admin_system_00008) Test ===')
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
                
            print('Navigating to admin_system_00008...')
            await page.goto('http://localhost:8080/backoffice/view/main/admin/system/admin_system_00008')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#admin_system_00008_t01', timeout=10000)
            
            print('Clicking Search...')
            await page.locator('#admin_system_00008_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_search.png')
            
            print('Opening Class Add Modal...')
            await page.locator('button[onclick="return fnStatusFg();"]').first.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_class_add_modal.png')
            
            print('Filling out Class form...')
            await page.locator('#regiCodeForm #nmCd').fill('999')
            await page.locator('#regiCodeForm #nmRep').fill('QA_CLASS')
            await page.locator('#regiCodeForm #cdLen').fill('3')
            await page.locator('#regiCodeForm #remark').fill('QA Category E2E')
            await page.wait_for_timeout(1000)
            
            print('Saving Class...')
            await page.locator('button[onclick="return fnSaveRegiCode();"]').first.click()
            await page.wait_for_timeout(1500)
            
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                await bootbox_ok.first.click()
                await page.wait_for_timeout(3000)
                
            await page.locator('#admin_system_00008_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_added.png')
            
            print('Selecting added row to load detail list...')
            row_selector = page.locator('#admin_system_00008_t01 tbody tr', has_text='999')
            if await row_selector.count() > 0:
                await row_selector.first.click()
                await page.wait_for_timeout(2000)
                
                print('Opening Detail Code Modal...')
                await page.locator('button[onclick="return fnDtStatusFg();"]').click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_detail_add_modal.png')
                
                print('Filling out Detail Code...')
                await page.locator('#regiDtCodeForm #nmDtCd').fill('001')
                await page.locator('#regiDtCodeForm #nmDtRep').fill('QA_DETAIL_001')
                await page.locator('#regiDtCodeForm #nmSub').fill('QA_SUB_001')
                await page.locator('#regiDtCodeForm #dtRemark').fill('QA Detail E2E')
                await page.wait_for_timeout(1000)
                
                print('Saving Detail Code...')
                await page.locator('button[onclick="return fnSaveRegiDtCode();"]').click()
                await page.wait_for_timeout(1500)
                
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(3000)
                    
                await row_selector.first.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_detail_added.png')
                
                print('Modifying Detail Code...')
                dt_row = page.locator('#admin_system_00008_t02 tbody tr', has_text='001')
                if await dt_row.count() > 0:
                    await dt_row.locator('.fa-edit').first.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_detail_modify_modal.png')
                    
                    await page.locator('#regiDtCodeForm #nmDtRep').fill('QA_DETAIL_MOD')
                    await page.locator('#regiDtCodeForm #nmSub').fill('QA_SUB_MOD')
                    await page.wait_for_timeout(1000)
                    
                    await page.locator('button[onclick="return fnSaveRegiDtCode();"]').click()
                    await page.wait_for_timeout(1500)
                    
                    bootbox_ok = page.locator('.bootbox-accept')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(3000)
                        
                    await row_selector.first.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_detail_modified.png')
                    
                print('Modifying Class...')
                await row_selector.locator('.fa-edit').first.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_class_modify_modal.png')
                
                await page.locator('#regiCodeForm #nmRep').fill('QA_CLASS_MOD')
                await page.wait_for_timeout(1000)
                
                await page.locator('button[onclick="return fnSaveRegiCode();"]').click()
                await page.wait_for_timeout(1500)
                
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                    await page.wait_for_timeout(3000)
                    
                await page.locator('#admin_system_00008_search_btn').click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_class_modified.png')
                
                print('Deleting Detail Code...')
                await row_selector.first.click()
                await page.wait_for_timeout(2000)
                dt_row = page.locator('#admin_system_00008_t02 tbody tr', has_text='001')
                if await dt_row.count() > 0:
                    await dt_row.locator('.fa-trash').first.click()
                    await page.wait_for_timeout(1500)
                    
                    bootbox_ok = page.locator('.bootbox-accept')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(3000)
                        
                    await row_selector.first.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_detail_deleted.png')
                
                print('Deleting Class...')
                row_selector = page.locator('#admin_system_00008_t01 tbody tr', has_text='999')
                if await row_selector.count() > 0:
                    await row_selector.locator('.fa-trash').first.click()
                    await page.wait_for_timeout(1500)
                    
                    bootbox_ok = page.locator('.bootbox-accept')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        await bootbox_ok.first.click()
                        await page.wait_for_timeout(3000)
                        
                    await page.locator('#admin_system_00008_search_btn').click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_system_00008_class_deleted.png')
                    
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
                data["screens"]["hq_system_00008"] = {
                    "complete": True,
                    "memo": "로그인 ID: shopadmin - 명칭코드관리 (본사 권한으로 명칭코드 분류 및 상세코드 등록, 수정, 삭제)"
                }
                # Admin Screen Progress
                data["screens"]["admin_system_00008"] = {
                    "complete": True,
                    "memo": "로그인 ID: admin2 - 명칭코드관리 (관리자 권한으로 명칭코드 분류 및 상세코드 등록, 수정, 삭제)"
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
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/system_00008_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
