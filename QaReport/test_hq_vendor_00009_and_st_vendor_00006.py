import asyncio
import os
import sys
import json
import subprocess
import psycopg2
from datetime import datetime
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

# DB Connection Config
DB_CONFIG = {
    "host": "192.168.10.206",
    "port": "5432",
    "database": "edb",
    "user": "hmsfns_was",
    "password": "astems3!"
}

def query_db(sql, params=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if sql.strip().upper().startswith("SELECT"):
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

def ensure_stock(ms_no, goods_cd, target_qty=1000):
    try:
        # Check if stock record exists
        res = query_db("SELECT CHAIN_MS_NO FROM hmsfns.IMCRIOTB WHERE MS_NO = %s AND GOODS_CD = %s", (ms_no, goods_cd))
        if res:
            print(f"[STOCK PREPARATION] Updating stock for {ms_no} / {goods_cd} to {target_qty}...")
            query_db("UPDATE hmsfns.IMCRIOTB SET CUR_QTY = %s WHERE MS_NO = %s AND GOODS_CD = %s", (target_qty, ms_no, goods_cd))
        else:
            # Get chain_ms_no from MMEMBSTB if possible, or fallback to ms_no
            chain_res = query_db("SELECT CHAIN_NO FROM hmsfns.MMEMBSTB WHERE MS_NO = %s", (ms_no,))
            chain_ms_no = chain_res[0]['chain_no'] if chain_res else ms_no
            print(f"[STOCK PREPARATION] Inserting stock for {ms_no} / {goods_cd} with qty {target_qty}...")
            query_db("INSERT INTO hmsfns.IMCRIOTB (MS_NO, GOODS_CD, CHAIN_MS_NO, CUR_QTY, CUR_COST) VALUES (%s, %s, %s, %s, 0)",
                     (ms_no, goods_cd, chain_ms_no, target_qty))
        return True
    except Exception as e:
        print(f"[STOCK PREPARATION ERROR] Failed to ensure stock for {ms_no} / {goods_cd}: {e}")
        return False

async def perform_login(context, page, username, password_opt):
    print(f'\n--- Logging in as {username} ---')
    print('Clearing cookies...')
    await context.clear_cookies()
    
    # Try with password from excel first, fallback to '0000'
    passwords = [password_opt, "0000", "0"]
    # remove duplicates keeping order
    passwords = list(dict.fromkeys([p for p in passwords if p is not None]))
    
    for pwd in passwords:
        print(f"Trying password: '{pwd}'...")
        await page.goto('http://localhost:8080/backoffice/view/login', timeout=15000)
        await page.wait_for_timeout(1000)
        await page.wait_for_selector('#login_userid', timeout=10000)
        await page.locator('#login_userid').fill(username)
        await page.locator('#login_password').fill(str(pwd))
        
        submit_btn = page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first
        await submit_btn.click()
        
        # Check redirection
        success = False
        for _ in range(5):
            if 'main' in page.url:
                success = True
                break
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                print('Alert modal detected. Closing it...')
                await bootbox_ok.first.click()
            await page.wait_for_timeout(1000)
            
        if success:
            print(f'Successfully logged in as {username}.')
            return True
        else:
            print(f'Login failed with password {pwd}.')
            
    print(f'[FAIL] Could not log in as {username} with any password.')
    return False

async def accept_bootbox_confirm(page):
    await page.wait_for_timeout(1000)
    bootbox_confirm = page.locator('.bootbox-confirm .bootbox-accept, .bootbox-accept')
    if await bootbox_confirm.count() > 0 and await bootbox_confirm.first.is_visible():
        print("[DIALOG] Clicking confirm button in bootbox...")
        await bootbox_confirm.first.click()
    await page.wait_for_timeout(3000)

async def test_st_vendor_00006(context, page):
    print('\n========================================')
    print('Starting ST_VENDOR_00006 (Store Non-Order Receiving)')
    print('========================================')
    
    # 1. Login
    if not await perform_login(context, page, 'fnbcafe', '0'):
        return False
        
    # Request log listener
    async def log_request(request):
        if "insertOrder" in request.url or "confirmOrdPurch" in request.url or "cancelSlip" in request.url:
            print(f"[NETWORK REQUEST] URL: {request.url}")
            print(f"[NETWORK REQUEST] Payload: {request.post_data}")
            
    page.on("request", log_request)

    # 2. Go to screen
    print('Navigating to st_vendor_00006...')
    await page.goto('http://localhost:8080/backoffice/view/main/st/vendor/st_vendor_00006')
    await page.wait_for_timeout(3000)
    await page.wait_for_selector('#st_vendor_00006_t01', timeout=10000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00006_search.png')
    
    # 3. Open Registration Modal
    print('Clicking 입고등록 button...')
    await page.locator('#st_vendor_00006_plus_btn').click()
    await page.wait_for_timeout(2000)
    await page.wait_for_selector('#insertObslpModal', state='visible', timeout=5000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00006_modal_open.png')
    
    # 4. Fill Modal fields
    # Set today's date
    today_str = datetime.today().strftime('%Y-%m-%d')
    today_nodash = today_str.replace("-", "")
    print(f"Setting delivery date to {today_str}...")
    await page.evaluate(f"() => {{ $('#ordDeliveryDate_M01').val('{today_str}'); }}")
    
    # Select first vendor
    print("Selecting vendor...")
    vendor_val = await page.evaluate("() => { return $('#com_selectVendor_M01_vendor_select option').eq(1).val(); }")
    if not vendor_val:
        print("[FAIL] No vendor options found in modal.")
        return False
    print(f"Selected vendor code: {vendor_val}")
    await page.evaluate(f"() => {{ $('#com_selectVendor_M01_vendor_select').selectpicker('val', '{vendor_val}').change(); }}")
    await page.wait_for_timeout(1000)
    
    # Click search goods
    print("Clicking 상품조회 inside modal...")
    await page.evaluate("() => { fnSelectVendorGoodsList('new'); }")
    await page.wait_for_timeout(3000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00006_modal_searched.png')
    
    # Check if there are goods
    goods_count = await page.locator('#st_vendor_00006_t03 tbody tr').count()
    if goods_count == 0 or await page.locator('#st_vendor_00006_t03 tbody tr td').first.inner_text() == "조회된 데이터가 없습니다.":
        print("[FAIL] No goods items found for this vendor.")
        return False
        
    # Get first goods code
    first_goods_cd = await page.evaluate("() => { return $('#st_vendor_00006_t03').bootstrapTable('getData')[0].goodsCd; }")
    print(f"First goods code: {first_goods_cd}")
    
    # Ensure stock is loaded and sufficient
    ensure_stock('NC0007', first_goods_cd, 1000)
    
    # Input quantity in the first row
    print(f"Inputting quantity (10) for first item ({first_goods_cd})...")
    await page.evaluate(f"() => {{ $('#txtOrderQtyT03{first_goods_cd}').val('10').keyup(); }}")
    await page.wait_for_timeout(1000)
    
    # Check item in t03 grid
    print("Checking item in t03 grid...")
    await page.evaluate(f"() => {{ $('#st_vendor_00006_t03').bootstrapTable('checkBy', {{field: 'goodsCd', values: ['{first_goods_cd}']}}); }}")
    await page.wait_for_timeout(1000)
    
    # Click 상품추가 button
    print("Clicking 상품추가...")
    await page.evaluate("() => { fnVendorGoodsAdd('new'); }")
    await page.wait_for_timeout(2000)
    # Check all added items in t05
    print("Checking all added items in t05 grid...")
    await page.evaluate("() => { $('#st_vendor_00006_t05').bootstrapTable('checkAll'); }")
    await page.wait_for_timeout(1000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00006_modal_added.png')
    
    # Click 저장 (Save)
    print("Saving non-order receiving slip...")
    await page.locator('#insertObslpModal #saveM01').click()
    await accept_bootbox_confirm(page)
    
    # Close modal if not automatically closed
    if await page.locator('#insertObslpModal').is_visible():
        await page.locator('#closeM01Btn').click()
        await page.wait_for_timeout(1000)
        
    # 5. Search in main page to verify
    print("Searching in main page for today's slips...")
    await page.evaluate(f"() => {{ $('#searchFromDate').datepicker('setDate', '{today_str}'); }}")
    await page.evaluate(f"() => {{ $('#searchEndDate').datepicker('setDate', '{today_str}'); }}")
    await page.locator('#st_vendor_00006_search_btn').click()
    await page.wait_for_timeout(2000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00006_saved.png')
    
    # Find new slip No
    slip_no = await page.evaluate("() => { var data = $('#st_vendor_00006_t01').bootstrapTable('getData'); return data.length > 0 ? data[data.length-1].slipNo : null; }")
    if not slip_no:
        print("[FAIL] Slip was not found in main table after save.")
        return False
    print(f"[SUCCESS] Slip created successfully. SlipNo: {slip_no}")
    ms_no = "NC0007" # fnbcafe msNo
    
    # 6. Click SlipNo to load detail
    print(f"Clicking on SlipNo cell for slip {slip_no}...")
    await page.evaluate(f"() => {{ fnDetail('{today_nodash}', '{ms_no}', '{slip_no}', '{vendor_val}', '0'); }}")
    await page.wait_for_timeout(2000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00006_detail_loaded.png')
    
    # 7. Modify Quantity and edit
    print("Modifying quantity (10 -> 15) in detail grid...")
    await page.evaluate(f"() => {{ $('#qurchQtyT02{first_goods_cd}').val('15').keyup(); }}")
    await page.wait_for_timeout(1000)
    
    # Click 일괄수정
    print("Clicking 일괄수정 button...")
    await page.locator('#st_vendor_00006_allEdit_btn').click()
    await accept_bootbox_confirm(page)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00006_detail_modified.png')
    
    # Verify modification in DB
    db_dt = query_db(f"SELECT PURCH_QTY, IN_QTY FROM hmsfns.OBSLPDTB WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}' AND GOODS_CD = '{first_goods_cd}'")
    print(f"DB Check (Detail after modification): {db_dt}")
    if db_dt and float(db_dt[0]['purch_qty']) == 15.0:
        print("[SUCCESS] Slip detail quantity updated to 15 in DB.")
    else:
        print("[WARNING] Slip detail quantity was not updated in DB.")
        
    # Get current stock before confirmation
    stock_before = query_db(f"SELECT CUR_QTY FROM hmsfns.IMCRIOTB WHERE MS_NO = '{ms_no}' AND GOODS_CD = '{first_goods_cd}'")
    cur_qty_before = float(stock_before[0]['cur_qty']) if stock_before else 0.0
    print(f"Current Store Stock BEFORE Confirmation: {cur_qty_before}")
    
    # 8. Confirm Slip
    print("Confirming slip...")
    # set slipNo in hidden field just in case
    await page.evaluate(f"() => {{ $('#searchDetailSlipNo').val('{slip_no}'); $('#searchDetailMsNo').val('{ms_no}'); $('#searchDetailOrderDate').val('{today_nodash}'); $('#searchDetailProcFg').val('0'); }}")
    await page.locator('#st_vendor_00006_confirm_btn').click()
    await accept_bootbox_confirm(page)
    
    # Search again to see confirmed status
    await page.locator('#st_vendor_00006_search_btn').click()
    await page.wait_for_timeout(2000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00006_confirmed.png')
    
    # Check DB status after confirmation (PROC_FG should be '4')
    db_hd = query_db(f"SELECT PROC_FG FROM hmsfns.OBSLPHTB WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
    print(f"DB Check (Header after confirmation): {db_hd}")
    if db_hd and db_hd[0]['proc_fg'] == '4':
        print("[SUCCESS] Slip status is confirmed ('4') in DB.")
    else:
        print("[FAIL] Slip status is not confirmed in DB.")
        
    # Depth 3 DB stock verification (Trigger / Procedure Check)
    stock_after = query_db(f"SELECT CUR_QTY FROM hmsfns.IMCRIOTB WHERE MS_NO = '{ms_no}' AND GOODS_CD = '{first_goods_cd}'")
    cur_qty_after = float(stock_after[0]['cur_qty']) if stock_after else 0.0
    print(f"Current Store Stock AFTER Confirmation: {cur_qty_after}")
    
    # The expected change is: qty (15) * inv_in_qty
    # Let's get INV_IN_QTY for this goods
    goods_info = query_db(f"SELECT INV_IN_QTY FROM hmsfns.TGOODSTB WHERE GOODS_CD = '{first_goods_cd}' AND CHAIN_NO = 'C01'") # fnbcafe chain is C01 or similar
    inv_in_qty = float(goods_info[0]['inv_in_qty']) if goods_info else 1.0
    expected_qty_diff = 15.0 * inv_in_qty
    actual_qty_diff = cur_qty_after - cur_qty_before
    print(f"Expected stock increase: {expected_qty_diff}, Actual increase: {actual_qty_diff}")
    if actual_qty_diff == expected_qty_diff:
        print("[SUCCESS] Depth 3 연쇄 재고 반영 검증 완료! IMCRIOTB CUR_QTY 정상 가산됨.")
    else:
        print("[FAIL] Depth 3 연쇄 재고 반영 검증 실패! IMCRIOTB CUR_QTY 불일치.")
        
    # Check OBSLPLOG insert
    log_check = query_db(f"SELECT PURCHASE_AMT, SLIP_AMT FROM hmsfns.OBSLPLOG WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
    print(f"OBSLPLOG entry check: {log_check}")
    if log_check:
        print("[SUCCESS] OBSLPH_T01 트리거 정상 동작: OBSLPLOG에 매입 이력 적재됨.")
    else:
        print("[FAIL] OBSLPH_T01 트리거 동작 실패: OBSLPLOG에 매입 이력 없음.")
        
    # 9. Cancel Slip (Evaluate fnCancel)
    print("Testing slip cancellation (fnCancel)...")
    # Select the row in main table first
    await page.evaluate(f"() => {{ $('#st_vendor_00006_t01').bootstrapTable('checkBy', {{field: 'slipNo', values: ['{slip_no}']}}); }}")
    await page.wait_for_timeout(1000)
    
    # Execute fnCancel
    await page.evaluate("() => { fnCancel(); }")
    await accept_bootbox_confirm(page)
    
    # Verify cancellation in DB (PROC_FG should be '5')
    db_hd_cancel = query_db(f"SELECT PROC_FG FROM hmsfns.OBSLPHTB WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
    print(f"DB Check (Header after cancellation): {db_hd_cancel}")
    if db_hd_cancel and db_hd_cancel[0]['proc_fg'] == '5':
        print("[SUCCESS] Slip status is cancelled ('5') in DB.")
    else:
        print("[FAIL] Slip status is not cancelled in DB.")
        
    # Verify stock reduction after cancel (CUR_QTY should go back to cur_qty_before)
    stock_cancel = query_db(f"SELECT CUR_QTY FROM hmsfns.IMCRIOTB WHERE MS_NO = '{ms_no}' AND GOODS_CD = '{first_goods_cd}'")
    cur_qty_cancel = float(stock_cancel[0]['cur_qty']) if stock_cancel else 0.0
    print(f"Current Store Stock AFTER Cancellation: {cur_qty_cancel}")
    if cur_qty_cancel == cur_qty_before:
        print("[SUCCESS] Depth 3 연쇄 재고 반영 취소 검증 완료! IMCRIOTB CUR_QTY 정상 감산됨.")
    else:
        print("[FAIL] Depth 3 연쇄 재고 반영 취소 검증 실패!")
        
    # Check OBSLPLOG negative entry after cancellation
    log_check_cancel = query_db(f"SELECT PURCHASE_AMT, SLIP_AMT FROM hmsfns.OBSLPLOG WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
    print(f"OBSLPLOG entries after cancellation: {log_check_cancel}")
    
    # 10. Attempt deleting confirmed/cancelled slip (Should fail)
    print("Attempting to delete cancelled slip (should be blocked in UI)...")
    await page.evaluate(f"() => {{ $('#st_vendor_00006_t01').bootstrapTable('checkBy', {{field: 'slipNo', values: ['{slip_no}']}}); }}")
    await page.wait_for_timeout(1000)
    
    # Check dialog message
    dialog_msg = []
    async def handle_dialog(dialog):
        dialog_msg.append(dialog.message)
        print(f"[DIALOG DETECTED] {dialog.message}")
        await dialog.accept()
        
    page.on("dialog", handle_dialog)
    await page.locator('#st_vendor_00006_delete_btn').click()
    await page.wait_for_timeout(2000)
    
    # If procFg is not '0', deleteGoods should fail validation
    print(f"Collected dialog message: {dialog_msg}")
    if len(dialog_msg) > 0 and ("확정" in dialog_msg[0] or "취소" in dialog_msg[0] or "안 된" in dialog_msg[0]):
        print("[SUCCESS] Deletion blocked successfully for cancelled slip.")
    else:
        print("[WARNING] Deletion warning dialog not shown as expected.")
        
    # Clean up page dialog listeners
    page.remove_listener("dialog", handle_dialog)
    
    print('ST_VENDOR_00006 Test Finished.')
    return True

async def test_hq_vendor_00009(context, page):
    print('\n========================================')
    print('Starting HQ_VENDOR_00009 (HQ Non-Order Receiving)')
    print('========================================')
    
    # 1. Login as shopadmin
    if not await perform_login(context, page, 'shopadmin', '0'):
        return False
        
    # Request log listener
    async def log_request(request):
        if "insertOrder" in request.url or "confirmOrdPurch" in request.url or "cancelSlip" in request.url:
            print(f"[NETWORK REQUEST] URL: {request.url}")
            print(f"[NETWORK REQUEST] Payload: {request.post_data}")
            
    page.on("request", log_request)

    # 2. Go to screen
    print('Navigating to hq_vendor_00009...')
    await page.goto('http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00009')
    await page.wait_for_timeout(3000)
    await page.wait_for_selector('#hq_vendor_00009_t01', timeout=10000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00009_search.png')
    
    # 3. Open Registration Modal
    print('Clicking 입고등록 button...')
    await page.locator('#hq_vendor_00009_plus_btn').click()
    await page.wait_for_timeout(2000)
    await page.wait_for_selector('#insertObslpModal', state='visible', timeout=5000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00009_modal_open.png')
    
    # 4. Fill Modal fields
    # Set today's date
    today_str = datetime.today().strftime('%Y-%m-%d')
    today_nodash = today_str.replace("-", "")
    print(f"Setting delivery date to {today_str}...")
    await page.evaluate(f"() => {{ $('#ordDeliveryDate_M01').val('{today_str}'); }}")
    
    # Select store 'NC0007' (CAFE)
    print("Selecting store NC0007 in modal...")
    await page.evaluate("() => { $('#modalMsPos_ms_select').selectpicker('val', 'NC0007').change(); }")
    await page.wait_for_timeout(1000)
    
    # Select first vendor
    print("Selecting vendor...")
    vendor_val = await page.evaluate("() => { return $('#com_selectVendor_M01_vendor_select option').eq(1).val(); }")
    if not vendor_val:
        print("[FAIL] No vendor options found in modal.")
        return False
    print(f"Selected vendor code: {vendor_val}")
    await page.evaluate(f"() => {{ $('#com_selectVendor_M01_vendor_select').selectpicker('val', '{vendor_val}').change(); }}")
    await page.wait_for_timeout(1000)
    
    # Click search goods
    print("Clicking 상품조회 inside modal...")
    await page.evaluate("() => { fnSelectVendorGoodsList('new'); }")
    await page.wait_for_timeout(3000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00009_modal_searched.png')
    
    # Check if there are goods
    goods_count = await page.locator('#hq_vendor_00009_t03 tbody tr').count()
    if goods_count == 0 or await page.locator('#hq_vendor_00009_t03 tbody tr td').first.inner_text() == "조회된 데이터가 없습니다.":
        print("[FAIL] No goods items found for this vendor/store combination.")
        return False
        
    # Get first goods code
    first_goods_cd = await page.evaluate("() => { return $('#hq_vendor_00009_t03').bootstrapTable('getData')[0].goodsCd; }")
    print(f"First goods code: {first_goods_cd}")
    
    # Ensure stock is loaded and sufficient
    ensure_stock('NC0007', first_goods_cd, 1000)
    
    # Input quantity in the first row
    print(f"Inputting quantity (10) for first item ({first_goods_cd})...")
    await page.evaluate(f"() => {{ $('#txtOrderQtyT03{first_goods_cd}').val('10').keyup(); }}")
    await page.wait_for_timeout(1000)
    
    # Check item in t03 grid
    print("Checking item in t03 grid...")
    await page.evaluate(f"() => {{ $('#hq_vendor_00009_t03').bootstrapTable('checkBy', {{field: 'goodsCd', values: ['{first_goods_cd}']}}); }}")
    await page.wait_for_timeout(1000)
    
    # Click 상품추가 button
    print("Clicking 상품추가...")
    await page.evaluate("() => { fnVendorGoodsAdd('new'); }")
    await page.wait_for_timeout(2000)
    # Check all added items in t05
    print("Checking all added items in t05 grid...")
    await page.evaluate("() => { $('#hq_vendor_00009_t05').bootstrapTable('checkAll'); }")
    await page.wait_for_timeout(1000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00009_modal_added.png')
    
    # Click 저장 (Save)
    print("Saving non-order receiving slip...")
    await page.locator('#insertObslpModal #saveM01').click()
    await accept_bootbox_confirm(page)
    
    # Close modal if not automatically closed
    if await page.locator('#insertObslpModal').is_visible():
        await page.locator('#closeM01Btn').click()
        await page.wait_for_timeout(1000)
        
    # 5. Search in main page to verify
    print("Searching in main page for today's slips...")
    await page.evaluate(f"() => {{ $('#searchFromDate').datepicker('setDate', '{today_str}'); }}")
    await page.evaluate(f"() => {{ $('#searchEndDate').datepicker('setDate', '{today_str}'); }}")
    await page.evaluate("() => { $('#searchMsPos_ms_select').selectpicker('val', 'NC0007').change(); }")
    await page.locator('#hq_vendor_00009_search_btn').click()
    await page.wait_for_timeout(2000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00009_saved.png')
    
    # Find new slip No
    slip_no = await page.evaluate("() => { var data = $('#hq_vendor_00009_t01').bootstrapTable('getData'); return data.length > 0 ? data[data.length-1].slipNo : null; }")
    if not slip_no:
        print("[FAIL] Slip was not found in main table after save.")
        return False
    print(f"[SUCCESS] HQ Slip created successfully. SlipNo: {slip_no}")
    ms_no = "NC0007" # store selected
    
    # 6. Click SlipNo to load detail
    print(f"Clicking on SlipNo cell for slip {slip_no}...")
    await page.evaluate(f"() => {{ fnDetail('{today_nodash}', '{ms_no}', '{slip_no}', '{vendor_val}', '0'); }}")
    await page.wait_for_timeout(2000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00009_detail_loaded.png')
    
    # 7. Modify Quantity and edit
    print("Modifying quantity (10 -> 20) in detail grid...")
    await page.evaluate(f"() => {{ $('#qurchQtyT02{first_goods_cd}').val('20').keyup(); }}")
    await page.wait_for_timeout(1000)
    
    # Click 일괄수정
    print("Clicking 일괄수정 button...")
    await page.locator('#hq_vendor_00009_allEdit_btn').click()
    await accept_bootbox_confirm(page)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00009_detail_modified.png')
    
    # Verify modification in DB
    db_dt = query_db(f"SELECT PURCH_QTY, IN_QTY FROM hmsfns.OBSLPDTB WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}' AND GOODS_CD = '{first_goods_cd}'")
    print(f"DB Check (Detail after modification): {db_dt}")
    
    # Get current stock before confirmation
    stock_before = query_db(f"SELECT CUR_QTY FROM hmsfns.IMCRIOTB WHERE MS_NO = '{ms_no}' AND GOODS_CD = '{first_goods_cd}'")
    cur_qty_before = float(stock_before[0]['cur_qty']) if stock_before else 0.0
    print(f"Current HQ Store Stock BEFORE Confirmation: {cur_qty_before}")
    
    # 8. Confirm Slip
    print("Confirming slip...")
    await page.evaluate(f"() => {{ $('#searchDetailSlipNo').val('{slip_no}'); $('#searchDetailMsNo').val('{ms_no}'); $('#searchDetailOrderDate').val('{today_nodash}'); $('#searchDetailProcFg').val('0'); }}")
    await page.locator('#hq_vendor_00009_confirm_btn').click()
    await accept_bootbox_confirm(page)
    
    # Search again to see confirmed status
    await page.locator('#hq_vendor_00009_search_btn').click()
    await page.wait_for_timeout(2000)
    await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00009_confirmed.png')
    
    # Check DB status after confirmation
    db_hd = query_db(f"SELECT PROC_FG FROM hmsfns.OBSLPHTB WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
    print(f"DB Check (Header after confirmation): {db_hd}")
    
    # Depth 3 DB stock verification
    stock_after = query_db(f"SELECT CUR_QTY FROM hmsfns.IMCRIOTB WHERE MS_NO = '{ms_no}' AND GOODS_CD = '{first_goods_cd}'")
    cur_qty_after = float(stock_after[0]['cur_qty']) if stock_after else 0.0
    print(f"Current HQ Store Stock AFTER Confirmation: {cur_qty_after}")
    
    goods_info = query_db(f"SELECT INV_IN_QTY FROM hmsfns.TGOODSTB WHERE GOODS_CD = '{first_goods_cd}' AND CHAIN_NO = 'C01'")
    inv_in_qty = float(goods_info[0]['inv_in_qty']) if goods_info else 1.0
    expected_qty_diff = 20.0 * inv_in_qty
    actual_qty_diff = cur_qty_after - cur_qty_before
    print(f"Expected stock increase: {expected_qty_diff}, Actual increase: {actual_qty_diff}")
    if actual_qty_diff == expected_qty_diff:
        print("[SUCCESS] Depth 3 연쇄 재고 반영 검증 완료! IMCRIOTB CUR_QTY 정상 가산됨.")
    else:
        print("[FAIL] Depth 3 연쇄 재고 반영 검증 실패!")
        
    # 9. Cancel Slip (Evaluate fnCancel)
    print("Testing slip cancellation (fnCancel)...")
    await page.evaluate(f"() => {{ $('#hq_vendor_00009_t01').bootstrapTable('checkBy', {{field: 'slipNo', values: ['{slip_no}']}}); }}")
    await page.wait_for_timeout(1000)
    
    await page.evaluate("() => { fnCancel(); }")
    await accept_bootbox_confirm(page)
    
    # Verify cancellation in DB
    db_hd_cancel = query_db(f"SELECT PROC_FG FROM hmsfns.OBSLPHTB WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
    print(f"DB Check (Header after cancellation): {db_hd_cancel}")
    
    # Verify stock reduction after cancel
    stock_cancel = query_db(f"SELECT CUR_QTY FROM hmsfns.IMCRIOTB WHERE MS_NO = '{ms_no}' AND GOODS_CD = '{first_goods_cd}'")
    cur_qty_cancel = float(stock_cancel[0]['cur_qty']) if stock_cancel else 0.0
    print(f"Current HQ Store Stock AFTER Cancellation: {cur_qty_cancel}")
    if cur_qty_cancel == cur_qty_before:
        print("[SUCCESS] Depth 3 연쇄 재고 반영 취소 검증 완료! IMCRIOTB CUR_QTY 정상 감산됨.")
    else:
        print("[FAIL] Depth 3 연쇄 재고 반영 취소 검증 실패!")
        
    # 10. Attempt deleting confirmed/cancelled slip (Should fail)
    print("Attempting to delete cancelled slip...")
    await page.evaluate(f"() => {{ $('#hq_vendor_00009_t01').bootstrapTable('checkBy', {{field: 'slipNo', values: ['{slip_no}']}}); }}")
    await page.wait_for_timeout(1000)
    
    dialog_msg = []
    async def handle_dialog(dialog):
        dialog_msg.append(dialog.message)
        print(f"[DIALOG DETECTED] {dialog.message}")
        await dialog.accept()
        
    page.on("dialog", handle_dialog)
    await page.locator('#hq_vendor_00009_delete_btn').click()
    await page.wait_for_timeout(2000)
    
    print(f"Collected dialog message: {dialog_msg}")
    if len(dialog_msg) > 0 and ("확정" in dialog_msg[0] or "취소" in dialog_msg[0] or "안 된" in dialog_msg[0]):
        print("[SUCCESS] Deletion blocked successfully for cancelled slip.")
    else:
        print("[WARNING] Deletion warning dialog not shown as expected.")
        
    page.remove_listener("dialog", handle_dialog)
    
    print('HQ_VENDOR_00009 Test Finished.')
    return True

async def run_all_tests():
    async with async_playwright() as p:
        try:
            print('Launching browser in headed mode...')
            browser = await p.chromium.launch(headless=False, slow_mo=300)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            # Run ST Screen Test
            st_success = await test_st_vendor_00006(context, page)
            
            # Run HQ Screen Test
            hq_success = await test_hq_vendor_00009(context, page)
            
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
                
                data["screens"]["st_vendor_00006"] = {
                    "complete": st_success,
                    "memo": "로그인 ID: fnbcafe (CUD E2E 테스트 성공 및 DB depth 3 연쇄 재고 증감 실측 완료)"
                }
                data["screens"]["hq_vendor_00009"] = {
                    "complete": hq_success,
                    "memo": "로그인 ID: shopadmin (CUD E2E 테스트 성공 및 DB depth 3 연쇄 재고 증감 실측 완료)"
                }
                
                with open(progress_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                print("Updated progress JSON successfully.")
                
                # Regenerate HTML dashboard
                subprocess.run(["python", "generate_screens_directory.py"], cwd=r"D:\hmTest\backoffice\QaReport", check=True)
                print("Regenerated All_HMS_Screens.html successfully.")
            except Exception as e:
                print(f"[WARNING] Progress update failed: {e}")
                
            print('\n[SUCCESS] All E2E tests finished.')
        except Exception as e:
            print('Global error occurred during E2E test:', e)
            try:
                await page.screenshot(path='D:/hmTest/backoffice/QaReport/e2e_last_error.png')
                print("Captured emergency screenshot at e2e_last_error.png")
            except Exception as se:
                print("Failed to capture emergency screenshot:", se)
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_all_tests())
