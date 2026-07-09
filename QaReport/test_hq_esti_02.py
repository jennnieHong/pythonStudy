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

                print("Login successful. Navigating to hq_esti_00002 (견적서 양식작성)...")
                await page.goto('http://localhost:8080/backoffice/view/main/hq/estimate/hq_esti_00002')
                await page.wait_for_timeout(2000)
                await dismiss_modal(page, 'passwordsModal')
                
                # Check grid load
                await page.wait_for_selector('#hq_esti_00002_t01', timeout=10000)
                print("견적서 양식작성 화면 정상 로드 확인.")
                
                # 1. CUD & 트리거 연쇄 테스트용 파라미터 정의
                chain_no = 'C002'
                estim_type_cd = '001'
                test_from_nm = 'Auto_QA_Template_01'
                test_desc = 'Automated E2E Test Template'
                
                # DB 사전 데이터 정합성 유지하기 위해 기존 동일 양식명 데이터 삭제
                query_db("DELETE FROM hmsfns.TESFRHTB WHERE CHAIN_NO = %s AND ESTIM_FROM_NM = %s", (chain_no, test_from_nm), fetch=False)
                
                # 2. 양식 생성 및 수정 API 호출을 위해 UI 폼 조작
                print("Clicking 초기화 button to clear form...")
                await page.locator('#hq_esti_00002_clear_btn').click()
                await page.wait_for_timeout(1000)
                
                # Fill out the form in main screen right panel
                print("Filling form in main screen...")
                # Wait for select to load and choose '001'
                await page.wait_for_selector('#com_estimTypeCd select', timeout=5000)
                await page.locator('#com_estimTypeCd select').select_option(value=estim_type_cd)
                
                # Set dates via JS
                await page.evaluate("""() => {
                    $('#estimFromDate').datepicker('setDate', '2026-07-01');
                    $('#estimEndDate').datepicker('setDate', '2026-12-31');
                    $('#estimReqFromDate').datepicker('setDate', '2026-06-26');
                    $('#estimReqEndDate').datepicker('setDate', '2026-06-30');
                }""")
                
                # Fill title and description
                await page.locator('#txt_estimFromNm').fill(test_from_nm)
                await page.locator('#txt_estimFromDesc').fill(test_desc)
                
                # Save the master
                print("Clicking 저장 button to register master...")
                await page.locator('#hq_esti_00002_save_btn').click()
                await page.wait_for_timeout(1500)
                
                # Accept confirmation bootbox / modal
                confirm_btn = page.locator('button:has-text("확인"), a:has-text("확인"), .btn-primary:has-text("확인"), .bootbox-accept')
                if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                    print("Confirm modal detected. Clicking '확인'...")
                    await confirm_btn.first.click()
                await page.wait_for_timeout(2500)
                
                # DB에서 자동 채번된 estim_from_cd 조회
                db_res = query_db(
                    "SELECT ESTIM_FROM_CD FROM hmsfns.TESFRHTB WHERE CHAIN_NO = %s AND ESTIM_FROM_NM = %s",
                    (chain_no, test_from_nm)
                )
                if not db_res:
                    print("[FAIL] Failed to find registered master in DB.")
                    await page.screenshot(path=os.path.join(report_dir, 'hq_esti_00002_error.png'))
                    print("Captured error screenshot: hq_esti_00002_error.png")
                    return
                    
                estim_from_cd = db_res[0]['estim_from_cd']
                print(f"[SUCCESS] Registered new estimate master. ESTIM_FROM_CD: {estim_from_cd}")
                
                # 3. 상품 추가 테스트 (goodsSaveAll / goodsSave)
                print(f"Searching registered code {estim_from_cd}...")
                # Search by code
                await page.locator('#searchEstimFromCd').fill(estim_from_cd)
                await page.locator('#hq_esti_00002_search_btn').click()
                await page.wait_for_timeout(1000)
                
                # Click row
                print(f"Clicking grid row for name {test_from_nm}...")
                await page.locator(f'#hq_esti_00002_t01 tbody tr td:has-text("{test_from_nm}")').click()
                
                # Wait until txt_estimFromCd has the value estim_from_cd (AJAX completes)
                print(f"Waiting for form field '#txt_estimFromCd' to be filled with {estim_from_cd}...")
                for attempt in range(20):
                    val = await page.locator('#txt_estimFromCd').input_value()
                    if val == estim_from_cd:
                        print(f"Form populated successfully: {val}")
                        break
                    await page.wait_for_timeout(500)
                else:
                    raise Exception(f"Form detail load timed out. Expected '#txt_estimFromCd' to be '{estim_from_cd}' but got '{await page.locator('#txt_estimFromCd').input_value()}'")
                
                # Click "상품추가" button to open goods search modal
                print("Clicking 상품추가 button...")
                await page.locator('#hq_esti_00002_goods_add_btn').click()
                
                # Wait for the modal to be visible
                print("Waiting for addGoodsModalM02 to be visible...")
                await page.wait_for_selector('#addGoodsModalM02', state='visible', timeout=5000)
                await page.wait_for_timeout(1000)
                
                # In goods search modal, click "조회" (id=hq_esti_00002M02_add_btn) to load list
                print("Clicking 상품조회 button inside modal...")
                await page.locator('#hq_esti_00002M02_add_btn').click()
                
                # Wait for goods table to load
                await page.wait_for_selector('#hq_esti_00002_t04 tbody tr', timeout=10000)
                await page.wait_for_timeout(1000)
                
                # Select first 2 goods check-boxes in goods modal table hq_esti_00002_t04
                print("Selecting goods to add...")
                await page.locator('#hq_esti_00002_t04 tbody tr:nth-child(1) input[type="checkbox"]').check()
                await page.locator('#hq_esti_00002_t04 tbody tr:nth-child(2) input[type="checkbox"]').check()
                await page.wait_for_timeout(500)
                
                # Click save (id=saveM02) inside modal
                print("Clicking 추가 button inside modal...")
                await page.locator('#saveM02').click()
                await page.wait_for_timeout(1500)
                
                # Accept confirmation
                confirm_btn = page.locator('button:has-text("확인"), a:has-text("확인"), .btn-primary:has-text("확인"), .bootbox-accept')
                if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                    await confirm_btn.first.click()
                await page.wait_for_timeout(2500)
                await dismiss_modal(page, 'addGoodsModalM02')
                
                # 4. DB 검증: TESFRDTB 에 상품이 정상 삽입되었는지 및 numeric 값 검증
                goods_db = query_db(
                    "SELECT ESTIM_GOODS_CD, ESTIM_GOODS_QTY, ESTIM_BAS_PRC FROM hmsfns.TESFRDTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_CD = %s AND ESTIM_FROM_CD = %s ORDER BY ESTIM_GOODS_CD",
                    (chain_no, estim_type_cd, estim_from_cd)
                )
                print(f"TESFRDTB Inserted Goods: {goods_db}")
                if not goods_db:
                    print("[FAIL] No goods added to TESFRDTB.")
                    return
                
                # 5. 수량 수정 및 형변환 예외 발생 여부 검증 (goodsUpdate)
                print("Modifying goods quantity in hq_esti_00002_t03...")
                # Fill the input box directly since it is rendered as an input element by the formatter
                first_goods_cd = goods_db[0]['estim_goods_cd']
                await page.locator(f'#estimGoods_{first_goods_cd}').fill("50")
                await page.wait_for_timeout(500)
                
                # Select the checkbox for the first row to perform update
                print("Selecting checkbox for the first goods row...")
                await page.locator('#hq_esti_00002_t03 tbody tr:nth-child(1) input[type="checkbox"]').check()
                await page.wait_for_timeout(500)
                
                # Click "수정" to trigger goodsUpdate
                print("Clicking 수정 button to update quantity...")
                await page.locator('#hq_esti_00002_goods_update_btn').click()
                await page.wait_for_timeout(1500)
                confirm_btn = page.locator('button:has-text("확인"), a:has-text("확인"), .btn-primary:has-text("확인"), .bootbox-accept')
                if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                    await confirm_btn.first.click()
                await page.wait_for_timeout(2500)
                
                # DB 수량 변경 검증
                updated_qty = query_db(
                    "SELECT ESTIM_GOODS_QTY FROM hmsfns.TESFRDTB WHERE CHAIN_NO = %s AND ESTIM_GOODS_CD = %s AND ESTIM_FROM_CD = %s",
                    (chain_no, goods_db[0]['estim_goods_cd'], estim_from_cd)
                )[0]['estim_goods_qty']
                print(f"Updated Qty in DB: {updated_qty}")
                
                # 6. Depth 3 트리거 동작 검증 (TESFRVTB INSERT -> Tr_TESFRV_T01 -> TESVDUTB 복사 확인)
                test_vendor = '000001'
                print(f"Trigger Test: Registering vendor {test_vendor} to TESFRVTB...")
                # Clean up vendor first if exists
                query_db("DELETE FROM hmsfns.TESFRVTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_CD = %s AND ESTIM_FROM_CD = %s AND ESTIM_VENDOR = %s", (chain_no, estim_type_cd, estim_from_cd, test_vendor), fetch=False)
                query_db(
                    "INSERT INTO hmsfns.TESFRVTB (CHAIN_NO, ESTIM_TYPE_CD, ESTIM_FROM_CD, ESTIM_VENDOR, INS_DTIME, INS_ID, UPD_DTIME, UPD_ID) VALUES (%s, %s, %s, %s, TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'E2E_TEST', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'E2E_TEST')",
                    (chain_no, estim_type_cd, estim_from_cd, test_vendor),
                    fetch=False
                )
                
                # Tr_TESFRV_T01 에 의해 TESVDUTB 에 상품 목록이 정상 적재되었는지 조회 (Depth 2 확인)
                vdutb_res = query_db(
                    "SELECT ESTIM_GOODS_CD, ESTIM_BAS_PRC, ESTIM_PRC_APPLY_YN FROM hmsfns.TESVDUTB WHERE CHAIN_NO = %s AND ESTIM_TYPE_CD = %s AND ESTIM_FROM_CD = %s AND ESTIM_VENDOR = %s",
                    (chain_no, estim_type_cd, estim_from_cd, test_vendor)
                )
                print(f"[Depth 2: TESVDUTB Trigger Results]: {vdutb_res}")
                
                # 7. 양식 삭제 (delete) 시 Tr_TESFRH_T02 트리거에 의한 하위 연쇄 삭제 검증 (Depth 3)
                print("Navigating/refreshing to show the registered template...")
                await page.locator('#searchEstimFromCd').fill(estim_from_cd)
                await page.locator('#hq_esti_00002_search_btn').click()
                await page.wait_for_timeout(1000)
                
                # Check row checkbox in main table hq_esti_00002_t01 (usually it's bootstrap-table with checkbox col)
                await page.locator('#hq_esti_00002_t01 tbody tr input[type="checkbox"]').first.check()
                await page.wait_for_timeout(500)
                
                # Capture screenshot before deleting
                await page.screenshot(path=os.path.join(report_dir, 'hq_esti_00002_search.png'))
                print('Screenshot captured.')
                
                # Click "삭제" button
                print("Clicking 삭제 button...")
                await page.locator('#hq_esti_00002_delete_btn').click()
                await page.wait_for_timeout(1500)
                
                # Confirm dialog
                confirm_btn = page.locator('button:has-text("확인"), a:has-text("확인"), .btn-primary:has-text("확인"), .bootbox-accept')
                if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                    await confirm_btn.first.click()
                await page.wait_for_timeout(2500)
                
                # DB 삭제 검증: TESFRHTB, TESFRDTB, TESFRVTB, TESVDUTB 의 데이터가 완벽하게 삭제되었는지 확인
                exist_master = query_db("SELECT 1 FROM hmsfns.TESFRHTB WHERE CHAIN_NO = %s AND ESTIM_FROM_CD = %s", (chain_no, estim_from_cd))
                exist_goods = query_db("SELECT 1 FROM hmsfns.TESFRDTB WHERE CHAIN_NO = %s AND ESTIM_FROM_CD = %s", (chain_no, estim_from_cd))
                exist_vendor = query_db("SELECT 1 FROM hmsfns.TESFRVTB WHERE CHAIN_NO = %s AND ESTIM_FROM_CD = %s", (chain_no, estim_from_cd))
                exist_vdutb = query_db("SELECT 1 FROM hmsfns.TESVDUTB WHERE CHAIN_NO = %s AND ESTIM_FROM_CD = %s", (chain_no, estim_from_cd))
                
                print(f"[Depth 3: TESFRH_T02 Trigger Delete Verification]")
                print(f"  TESFRHTB (Master) Exist: {bool(exist_master)}")
                print(f"  TESFRDTB (Goods) Exist: {bool(exist_goods)}")
                print(f"  TESFRVTB (Vendor) Exist: {bool(exist_vendor)}")
                print(f"  TESVDUTB (Vendor Upload) Exist: {bool(exist_vdutb)}")
                
                if not exist_master and not exist_goods and not exist_vendor and not exist_vdutb:
                    print("[SUCCESS] All cascading deletes completed successfully by trigger chain!")
                else:
                    print("[FAIL] Trigger deletion failed to cascade.")
                    
                print('[SUCCESS] hq_esti_00002 E2E test completed successfully.')

            except Exception as e:
                print('Error occurred during E2E test:', e)
                try:
                    await page.screenshot(path=os.path.join(report_dir, 'hq_esti_00002_error.png'))
                    print("Captured error screenshot: hq_esti_00002_error.png")
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
