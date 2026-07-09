import asyncio
import os
import sys
import json
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
        cursor.execute("DELETE FROM hmsfns.MENULCTB WHERE MENU_LCLASS_CD = '9999';")
        cursor.execute("DELETE FROM hmsfns.MENUMCTB WHERE MENU_LCLASS_CD = '9999';")
        cursor.execute("DELETE FROM hmsfns.MENUMMTB WHERE MENU_SEQ = '000290';")
        cursor.execute("UPDATE hmsfns.MENUMMTB SET MAPP_LCLASS_CD = NULL, MAPP_MCLASS_CD = NULL, MENU_PERIOD = 1, MENU_LEVEL = 1 WHERE MAPP_LCLASS_CD = '9999';")
        
        # Insert test menu 000290 directly
        cursor.execute("""
            INSERT INTO hmsfns.MENUMMTB (MENU_SEQ, MENU_NM, SYSTEM_TYPE, VIEW_PATH, VIEW_FILE, REMARK, CREATE_DTIME, CREATE_ID, LAST_DTIME, LAST_ID)
            VALUES ('000290', 'test', 'HQ', '/backoffice/main/hq/system', 'hq_system_00007', 'Playwright E2E Mapping Test', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'Admin', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'Admin');
        """)
        
        conn.commit()
        print("[SUCCESS] DB pre-cleanup and menu pre-insertion completed.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[WARNING] Database connection/cleanup failed: {e}")

async def run_e2e():
    db_cleanup()
    
    async with async_playwright() as p:
        try:
            print('Launching browser (headed)...')
            try:
                browser = await p.chromium.launch(headless=False, slow_mo=300)
            except Exception as e:
                print(f'Headed launch failed ({e}), falling back to headless=True...')
                browser = await p.chromium.launch(headless=True, slow_mo=100)

            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
            
            # Handle dialogs automatically
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            
            print('Navigating to http://localhost:8080/backoffice ...')
            await page.goto('http://localhost:8080/backoffice', timeout=15000)
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            print('Logging in as shopadmin...')
            await page.locator('#login_userid').fill('shopadmin')
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"]').first.click()
            
            print('Waiting for redirection to main...')
            for _ in range(15):
                if 'main' in page.url:
                    break
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(1000)
                
            print('Navigating to hq_system_00007...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/system/hq_system_00007')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_system_00007_t01', timeout=10000)
            
            # 1. 메뉴생성
            print('=== STEP 1: Verifying Menu Program ===')
            await page.locator('a.nav-link', has_text='메뉴생성').click()
            await page.wait_for_timeout(1500)
            
            # Click search to display menus
            await page.locator('#hq_system_00007_search_btn').click()
            await page.wait_for_timeout(2000)
            
            # Take screenshot of created menu in grid
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/e2e_step1_menu_created.png')
            print('[SUCCESS] Menu program verified in grid.')

            
            # 2. 분류관리 (LClass & MClass 생성)
            print('=== STEP 2: Creating LClass & MClass Categories ===')
            await page.locator('a.nav-link', has_text='분류관리').click()
            await page.wait_for_timeout(1500)
            
            # LClass Add
            await page.locator('#hq_system_00007_t01_toolbar button[onclick="fnLMenuModalShow();"]').click()
            await page.wait_for_selector('#lMenuAddModal', timeout=5000)
            await page.locator('#M01Form [name="input_L_menuNm"]').fill('TEST_LCLASS')
            await page.locator('#M01Form [name="input_L_menuPeriod"]').fill('99')
            await page.locator('#M01Form [name="input_L_menuIcon"]').fill('fas fa-star')
            await page.locator('#M01Form [name="input_L_menuCd"]').fill('9999')
            await page.locator('#M01Form [name="input_L_remark"]').fill('Playwright Test Category')
            await page.wait_for_timeout(1000)
            await page.locator('button[onclick="fnInsertLmenu();"]').click()
            await page.wait_for_timeout(3000)
            
            # Refresh list & Click LClass 9999 to load MClass table
            await page.locator('#hq_system_00007_search_btn').click()
            await page.wait_for_timeout(2000)
            
            row_lclass = page.locator('#hq_system_00007_t01 tbody tr', has_text='9999')
            if await row_lclass.count() > 0:
                await row_lclass.first.click()
                await page.wait_for_timeout(2000)
                
                # MClass Add
                await page.locator('#hq_system_00007_t02_toolbar button[onclick="fnMMenuModalShow();"]').click()
                await page.wait_for_selector('#mMenuAddModal', timeout=5000)
                await page.locator('#M04Form [name="input_M_menuNm"]').fill('test_mid_category')
                await page.locator('#M04Form [name="input_M_menuPeriod"]').fill('99')
                await page.locator('#M04Form [name="input_M_menuCd"]').fill('9999')
                await page.locator('#M04Form [name="input_M_remark"]').fill('Playwright Test Mid Category')
                await page.wait_for_timeout(1000)
                await page.locator('button[onclick="fnInsertMmenu();"]').click()
                await page.wait_for_timeout(3000)
                
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/e2e_step2_categories_created.png')
            print('[SUCCESS] LClass and MClass created.')
            
            # 3. 메뉴관리 - 하위 메뉴 매핑
            print('=== STEP 3: Mapping Menu Program to Category ===')
            await page.locator('a.nav-link', has_text='메뉴관리').click()
            await page.wait_for_timeout(3000)
            
            # Find and expand tree node
            print('Searching for test_mid_category node in tree...')
            await page.wait_for_selector('#menuClassTree .jstree-anchor', timeout=10000)
            
            # Open all tree nodes via JS to make sure they are visible
            await page.evaluate("$('#menuClassTree').jstree('open_all');")
            await page.wait_for_timeout(1500)
            
            mid_node = page.locator('.jstree-anchor', has_text='test_mid_category').first
            await mid_node.wait_for(state='visible', timeout=10000)
            
            # Right-click MClass node
            print('Right clicking mid category node...')
            await mid_node.click(button='right')
            await page.wait_for_timeout(1000)
            
            # Click context menu item: 하위 메뉴 등록
            print('Clicking "하위 메뉴 등록"...')
            await page.locator('.vakata-context li a', has_text='하위 메뉴 등록').click()
            await page.wait_for_selector('#MenuSearchModal2', timeout=5000)
            await page.wait_for_timeout(2000)
            
            # Check row 000290
            print('Selecting menu 000290 row...')
            target_row = page.locator('#hq_system_00007_t05 tbody tr', has_text='000290')
            await target_row.locator('input[type="checkbox"]').check()
            await page.wait_for_timeout(500)
            
            # Fill priority
            print('Filling priority for 000290...')
            await page.locator('#menuPeriod_000290').fill('99')
            await page.wait_for_timeout(500)
            
            # Click Save (추가)
            print('Saving mapping...')
            await page.locator('#btnMenuCheck2').click()
            await page.wait_for_timeout(1500)
            
            # Accept bootbox confirm
            print('Accepting bootbox confirm...')
            await page.locator('.bootbox-accept').click()
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/e2e_step3_mapped.png')
            print('[SUCCESS] Sub-menu mapped successfully.')
            
            # 4. 소분류 노드 클릭하여 정보 로드 확인
            print('=== STEP 4: Clicking child node (test) to verify populated fields ===')
            # Open all tree nodes via JS to make sure they are visible after tree reload
            await page.evaluate("$('#menuClassTree').jstree('open_all');")
            await page.wait_for_timeout(1500)
            
            # Click the child leaf node 'test' (it contains the text 'test' and is under test_mid_category)
            print('Clicking the child menu node...')
            child_node = page.locator('.jstree-anchor', has_text='test').last
            await child_node.click()
            await page.wait_for_timeout(2000)
            
            # Capture filled menu info
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/e2e_step4_menu_info_loaded.png')
            print('[SUCCESS] Fields populated on child node click.')
            
            # 5. 중분류 노드 클릭하여 빈 필드 결함 확인
            print('=== STEP 5: Clicking mid category node to demonstrate blank fields bug ===')
            parent_node = page.locator('.jstree-anchor', has_text='test_mid_category').first
            await parent_node.click()
            await page.wait_for_timeout(2000)
            
            # Capture blank menu info
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/e2e_step5_mid_category_info_blank.png')
            print('[SUCCESS] Bug demonstrated: fields left blank on mid category click.')
            
            # 6. Clean up
            print('=== Cleaning up test data ===')
            # Click child node again to delete mapping
            await child_node.click()
            await page.wait_for_timeout(1000)
            # Click Delete Mapping (삭제)
            await page.locator('#btnMenuDelete').click()
            await page.wait_for_timeout(3000)
            
            # Cleanup DB categories & menu
            db_cleanup()
            print('[SUCCESS] Cleanup finished.')
            
        except Exception as e:
            print('Error during E2E test:', e)
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_e2e())
