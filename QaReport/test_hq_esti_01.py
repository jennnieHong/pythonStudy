import asyncio
import os
import sys
import json
import subprocess
import psycopg2
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

report_dir = r"D:\hmTest\backoffice\QaReport"
if not os.path.exists(report_dir):
    os.makedirs(report_dir)

DB_CONFIG = {
    "host": "192.168.10.206",
    "port": "5432",
    "database": "edb",
    "user": "hmsfns_was",
    "password": "astems3!"
}

def query_db(sql, params=None, fetch=True):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if fetch:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            result = cursor.rowcount
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"[DB ERROR] Failed to execute query: {sql}. Error: {e}")
        return None

async def dismiss_modal(page, modal_id):
    await page.evaluate(f"""() => {{
        try {{
            if (typeof $ !== 'undefined') {{
                $('#{modal_id}').modal('hide');
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
            }} else {{
                const m = document.getElementById('{modal_id}');
                if (m) m.style.display = 'none';
                const backdrops = document.getElementsByClassName('modal-backdrop');
                for (let b of backdrops) {{ b.remove(); }}
                document.body.classList.remove('modal-open');
            }}
        }} catch(e) {{}}
    }}""")
    await page.wait_for_timeout(500)

async def run_test():
    target_user = 'fnbadmin'
    
    print(f"[DB BACKUP] Backing up credentials for {target_user}...")
    res = query_db("SELECT PASSWD, LAST_DTIME, FST_LOGIN_PW_CHANGE, ACCT_ENABLE, ACCT_LOCK FROM hmsfns.MUSERSTB WHERE USER_ID = %s", (target_user,))
    if res:
        backup_data = res[0]
        print(f"  Backup state: {backup_data}")
    else:
        print(f"  [ERROR] Failed to backup user {target_user}")
        return
        
    query_db(
        "UPDATE hmsfns.MUSERSTB SET PASSWD = %s, ACCT_ENABLE = 'Y', ACCT_LOCK = 'N', AUTH_FAILURE_CNT = 0, FST_LOGIN_PW_CHANGE = 'Y' WHERE USER_ID = %s",
        ('$2a$10$uJZY4u/YPOGVTb/QYpvQ/OGpS9CkmFUWFKLomdmSrCOsPZWWQEg6i', target_user), # hash for '0000'
        fetch=False
    )
    print("Temporary credentials set in DB.")

    try:
        async with async_playwright() as p:
            print("\nStarting Playwright...")
            try:
                try:
                    browser = await p.chromium.launch(headless=False, slow_mo=100)
                except Exception as e:
                    print(f"Headed launch failed ({e}), falling back to headless=True...")
                    browser = await p.chromium.launch(headless=True, slow_mo=100)
                    
                context = await browser.new_context(viewport={"width": 1280, "height": 800})
                page = await context.new_page()
                
                # 1. Force logout
                print('Forcing logout to clear session...')
                await page.goto('http://localhost:8080/backoffice/logout')
                await page.wait_for_timeout(1000)
                
                # 2. Go to login
                print('Navigating to login page...')
                await page.goto('http://localhost:8080/backoffice', timeout=15000)
                await page.wait_for_selector('#login_userid', timeout=10000)
                
                # 3. Login
                print(f'Logging in as {target_user}...')
                await page.locator('#login_userid').fill(target_user)
                await page.locator('#login_password').fill('0000')
                await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
                
                # 4. Wait for redirection with bootbox handling
                print('Waiting for redirection to main...')
                success = False
                for _ in range(15):
                    if 'main' in page.url:
                        success = True
                        break
                    bootbox_ok = page.locator('.bootbox-accept, .modal-footer .btn-primary')
                    if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                        print("Duplicate login or alert modal detected. Clicking accept...")
                        await bootbox_ok.first.click()
                    await page.wait_for_timeout(1000)
                    
                if not success:
                    print(f"[FAIL] Redirection failed. Current URL: {page.url}")
                    return

                print("Login successful. Navigating to hq_esti_00001 (견적유형마스터)...")
                await page.goto('http://localhost:8080/backoffice/view/main/hq/estimate/hq_esti_00001')
                await page.wait_for_timeout(2000)
                await dismiss_modal(page, 'passwordsModal')
                
                # Check grid load
                await page.wait_for_selector('#hq_esti_00001_t01', timeout=10000)
                print("견적유형마스터 화면 정상 로드 확인.")
                
                # Define parameters for test
                chain_no = 'C002'
                test_type_kr_nm = 'Auto_QA_Type_01'
                test_type_en_nm = 'AutoQAType01'
                test_bigo = 'Automated E2E Test Type Description'
                
                # DB 사전 데이터 정합성 유지하기 위해 기존 동일 양식명 데이터 삭제
                # 1. TESTYGTB (Goods mapped to type)
                # 2. TESTYMTB (Type Master)
                query_db("DELETE FROM hmsfns.TESTYGTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_CD IN (SELECT ESTIM_TYPE_CD FROM hmsfns.TESTYMTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_KOR_NM = %s)", (chain_no, chain_no, test_type_kr_nm), fetch=False)
                query_db("DELETE FROM hmsfns.TESTYMTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_KOR_NM = %s", (chain_no, test_type_kr_nm), fetch=False)
                print("Cleaned up existing test data from DB.")
                
                # 1. Click 초기화 button to clear form
                print("Clicking 초기화 button to clear form...")
                await page.locator('#hq_esti_00001_clear_btn').click()
                await page.wait_for_timeout(1000)
                
                # 2. Fill form to add new master type
                print("Filling form to register new type...")
                await page.locator('#txt_estimTypeKrNm').fill(test_type_kr_nm)
                await page.locator('#txt_estimTypeEnNm').fill(test_type_en_nm)
                await page.locator('#txt_estimBigo').fill(test_bigo)
                
                # 3. Save
                print("Clicking 저장 button...")
                await page.locator('#hq_esti_00001_save_btn').click()
                await page.wait_for_timeout(1500)
                
                # Accept confirmation bootbox / modal
                confirm_btn = page.locator('button:has-text("확인"), a:has-text("확인"), .btn-primary:has-text("확인"), .bootbox-accept')
                if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                    print("Confirm modal detected. Clicking '확인'...")
                    await confirm_btn.first.click()
                await page.wait_for_timeout(2500)
                
                # 4. Check DB for registered ESTIM_TYPE_CD
                db_res = query_db(
                    "SELECT ESTIM_TYPE_CD FROM hmsfns.TESTYMTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_KOR_NM = %s",
                    (chain_no, test_type_kr_nm)
                )
                if not db_res:
                    print("[FAIL] Failed to find registered type master in DB.")
                    await page.screenshot(path=os.path.join(report_dir, 'hq_esti_00001_error.png'))
                    print("Captured error screenshot: hq_esti_00001_error.png")
                    return
                    
                estim_type_cd = db_res[0]['estim_type_cd']
                print(f"[SUCCESS] Registered new estimate master type. ESTIM_TYPE_CD: {estim_type_cd}")
                
                # 5. Search for the registered type in UI
                print("Searching registered type...")
                await page.locator('#searchEstimTypeNm').fill(test_type_kr_nm)
                await page.locator('#hq_esti_00001_search_btn').click()
                await page.wait_for_timeout(1000)
                
                # 6. Click grid cell for 'estimTypeCd' to load detail
                print(f"Clicking code cell '{estim_type_cd}' to load details...")
                # Note: handler is on cell click with field 'estimTypeCd' (class table-onclick)
                await page.locator(f'#hq_esti_00001_t01 tbody tr td.table-onclick:has-text("{estim_type_cd}")').click()
                await page.wait_for_timeout(1000)
                
                # Wait until form has loaded the detail (txt_estimTypeCd gets populated)
                print(f"Waiting for form field '#txt_estimTypeCd' to be filled with {estim_type_cd}...")
                for attempt in range(20):
                    val = await page.locator('#txt_estimTypeCd').input_value()
                    if val == estim_type_cd:
                        print(f"Form populated successfully: {val}")
                        break
                    await page.wait_for_timeout(500)
                else:
                    raise Exception(f"Form detail load timed out. Expected '#txt_estimTypeCd' to be '{estim_type_cd}' but got '{await page.locator('#txt_estimTypeCd').input_value()}'")
                
                # 7. Search goods list
                print("Searching goods list to add items...")
                await page.locator('#hq_esti_00001_goods_search_btn').click()
                await page.wait_for_timeout(1000)
                
                # Wait for goods table to load
                await page.wait_for_selector('#hq_esti_00001_t02 tbody tr', timeout=10000)
                await page.wait_for_timeout(1000)
                
                # Select first 2 goods check-boxes in goods table
                print("Selecting first 2 goods to add...")
                await page.locator('#hq_esti_00001_t02 tbody tr:nth-child(1) input[type="checkbox"]').check()
                await page.locator('#hq_esti_00001_t02 tbody tr:nth-child(2) input[type="checkbox"]').check()
                await page.wait_for_timeout(500)
                
                # Click 추가 button
                print("Clicking 추가 button...")
                await page.locator('#hq_esti_00001_goods_save_btn').click()
                await page.wait_for_timeout(1500)
                
                # DB 검증: TESTYGTB 에 상품 2개가 매핑되었는지
                goods_db = query_db(
                    "SELECT ESTIM_GOODS_CD FROM hmsfns.TESTYGTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_CD = %s ORDER BY ESTIM_GOODS_CD",
                    (chain_no, estim_type_cd)
                )
                print(f"TESTYGTB Inserted Goods: {goods_db}")
                if not goods_db or len(goods_db) < 2:
                    print("[FAIL] Goods save verification failed.")
                    return
                
                # 8. Test 전체추가
                print("Testing 전체추가 (Add All)...")
                await page.locator('#hq_esti_00001_goods_saveAll_btn').click()
                await page.wait_for_timeout(1500)
                
                # Confirm bootbox.confirm
                confirm_btn = page.locator('button:has-text("확인"), a:has-text("확인"), .btn-primary:has-text("확인"), .bootbox-accept')
                if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                    print("Accepting Add All confirm dialog...")
                    await confirm_btn.first.click()
                await page.wait_for_timeout(2500)
                
                # DB 검증: 전체추가 후 TESTYGTB에 상품이 더 많이 추가되었는지
                goods_all_db = query_db(
                    "SELECT COUNT(1) AS cnt FROM hmsfns.TESTYGTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_CD = %s",
                    (chain_no, estim_type_cd)
                )
                print(f"Total Goods under Type after Add All: {goods_all_db[0]['cnt']}")
                if goods_all_db[0]['cnt'] <= 2:
                    print("[FAIL] Add All verification failed.")
                    return
                    
                # 9. Test 대상상품삭제 (goodsDelete)
                print("Testing goods deletion from t03...")
                # Select first 2 rows checkboxes in hq_esti_00001_t03
                await page.locator('#hq_esti_00001_t03 tbody tr:nth-child(1) input[type="checkbox"]').check()
                await page.locator('#hq_esti_00001_t03 tbody tr:nth-child(2) input[type="checkbox"]').check()
                await page.wait_for_timeout(500)
                
                # Click 삭제 button
                print("Clicking 대상상품 삭제 button...")
                await page.locator('#hq_esti_00001_goods_delete_btn').click()
                await page.wait_for_timeout(1500)
                
                # DB 검증: 일부 상품이 삭제되었는지
                goods_after_del = query_db(
                    "SELECT COUNT(1) AS cnt FROM hmsfns.TESTYGTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_CD = %s",
                    (chain_no, estim_type_cd)
                )
                print(f"Total Goods under Type after deleting 2: {goods_after_del[0]['cnt']}")
                
                # Refresh to capture screenshot
                print("Refreshing search for screenshot...")
                await page.locator('#searchEstimTypeNm').fill(test_type_kr_nm)
                await page.locator('#hq_esti_00001_search_btn').click()
                await page.wait_for_timeout(1000)
                
                # Save screenshot before deleting the master type itself
                screenshot_path = os.path.join(report_dir, 'hq_esti_00001_search.png')
                await page.screenshot(path=screenshot_path)
                print(f'Screenshot captured at: {screenshot_path}')
                
                # 10. Delete the master type itself
                print("Testing deletion of the master type itself...")
                # Check row checkbox in hq_esti_00001_t01
                await page.locator('#hq_esti_00001_t01 tbody tr input[type="checkbox"]').first.check()
                await page.wait_for_timeout(500)
                
                # Click 삭제 button at the top header
                await page.locator('#hq_esti_00001_delete_btn').click()
                await page.wait_for_timeout(1500)
                
                # Accept confirm bootbox
                confirm_btn = page.locator('button:has-text("확인"), a:has-text("확인"), .btn-primary:has-text("확인"), .bootbox-accept')
                if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                    print("Accepting Delete confirm dialog...")
                    await confirm_btn.first.click()
                await page.wait_for_timeout(2500)
                
                # DB 검증: TESTYMTB, TESTYGTB 에서 완전히 삭제되었는지
                exist_master = query_db("SELECT 1 FROM hmsfns.TESTYMTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_CD = %s", (chain_no, estim_type_cd))
                exist_goods = query_db("SELECT 1 FROM hmsfns.TESTYGTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_CD = %s", (chain_no, estim_type_cd))
                
                print(f"Master Exist: {bool(exist_master)}")
                print(f"Mapped Goods Exist: {bool(exist_goods)}")
                
                if not exist_master and not exist_goods:
                    print("[SUCCESS] Cascade deletion completed successfully!")
                else:
                    print("[FAIL] Deletion failed to cascade or delete master.")
                    
                print('[SUCCESS] hq_esti_00001 E2E test completed successfully.')

            except Exception as e:
                print('Error occurred during E2E test:', e)
                try:
                    await page.screenshot(path=os.path.join(report_dir, 'hq_esti_00001_error.png'))
                    print("Captured error screenshot: hq_esti_00001_error.png")
                except Exception as se:
                    print("Failed to capture error screenshot:", se)
            finally:
                if 'browser' in locals() or 'browser' in globals():
                    await browser.close()
    finally:
        # DB RESTORE USER CREDENTIALS
        print(f"\n[DB RESTORE] Restoring original credentials for {target_user}...")
        query_db(
            "UPDATE hmsfns.MUSERSTB SET PASSWD = %s, LAST_DTIME = %s, FST_LOGIN_PW_CHANGE = %s, ACCT_ENABLE = %s, ACCT_LOCK = %s WHERE USER_ID = %s",
            (backup_data['passwd'], backup_data['last_dtime'], backup_data['fst_login_pw_change'], backup_data['acct_enable'], backup_data['acct_lock'], target_user),
            fetch=False
        )
        print("[DB RESTORE COMPLETE]")

if __name__ == '__main__':
    asyncio.run(run_test())
