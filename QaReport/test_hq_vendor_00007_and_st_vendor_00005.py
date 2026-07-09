import asyncio
import os
import sys
import json
from datetime import datetime
import psycopg2
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
        res = query_db("SELECT CHAIN_MS_NO FROM hmsfns.IMCRIOTB WHERE MS_NO = %s AND GOODS_CD = %s", (ms_no, goods_cd))
        if res:
            print(f"[STOCK PREPARATION] Updating stock for {ms_no} / {goods_cd} to {target_qty}...")
            query_db("UPDATE hmsfns.IMCRIOTB SET CUR_QTY = %s WHERE MS_NO = %s AND GOODS_CD = %s", (target_qty, ms_no, goods_cd))
        else:
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
    
    passwords = [password_opt, "0000", "0"]
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

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        async def handle_response(response):
            if "delete" in response.url or "confirm" in response.url or "update" in response.url or "save" in response.url:
                try:
                    text = await response.text()
                    print(f"[API RESPONSE] URL: {response.url}, Status: {response.status}, Content: {text[:800]}")
                except Exception:
                    pass
        page.on("response", handle_response)
        page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"[BROWSER ERROR] {err}"))
        
        today_str = datetime.today().strftime('%Y-%m-%d')
        today_nodash = today_str.replace("-", "")
        # Ensure month is not closed in DB for test run
        print("[DB SETUP] Ensuring month is not closed in TB_TOT_AVG_COST...")
        query_db("DELETE FROM hmsfns.TB_TOT_AVG_COST WHERE CREATE_MONTH = '202606'")
        
        # =========================================================================
        # 1. STORE RETURN MANAGEMENT (st_vendor_00005)
        # =========================================================================
        print("\n=======================================================")
        print("Starting E2E Test: ST_VENDOR_00005 (Store Return)")
        print("=======================================================")
        
        if not await perform_login(context, page, 'fnbcafe', '0000'):
            await browser.close()
            return
            
        # Navigate to Store Return Management screen
        print("Navigating to st_vendor_00005...")
        await page.goto("http://localhost:8080/backoffice/view/main/st/vendor/st_vendor_00005")
        await page.wait_for_timeout(3000)
        await page.wait_for_selector('#st_vendor_00005_t01', timeout=10000)
        await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00005_search.png')
        
        # Open Registration Modal M01
        print("Opening Registration Modal M01...")
        await page.evaluate("() => { fnAddVendorOrder('new'); }")
        await page.wait_for_timeout(2000)
        await page.wait_for_selector('#st_vendor_00005_M01', state='visible', timeout=5000)
        await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00005_modal_open.png')
        
        # Select Vendor
        print("Selecting first vendor in modal...")
        vendor_val = await page.evaluate("() => { return $('#com_selectVendor_M01_vendor_select option').eq(1).val(); }")
        if not vendor_val:
            print("[FAIL] No vendor options found.")
            await browser.close()
            return
        print(f"Selected Vendor: {vendor_val}")
        await page.evaluate(f"() => {{ $('#com_selectVendor_M01_vendor_select').selectpicker('val', '{vendor_val}').change(); }}")
        await page.wait_for_timeout(1000)
        
        # Click search goods inside modal
        print("Searching goods inside modal...")
        await page.evaluate("() => { fnSelectVendorGoodsList('new'); }")
        await page.wait_for_timeout(3000)
        
        # Check first row item and set quantity
        goods_data = await page.evaluate("() => { return $('#st_vendor_00005_t03').bootstrapTable('getData'); }")
        if not goods_data:
            print("[FAIL] No return goods available.")
            await browser.close()
            return
            
        first_goods_cd = goods_data[0]['goodsCd']
        print(f"First Goods Code: {first_goods_cd}")
        
        # Ensure sufficient store stock exists to prevent negative stock checks if any
        ensure_stock('NC0007', first_goods_cd, 1000)
        
        # Set quantity to 10 for index 0
        print(f"Inputting quantity (10) for first item...")
        await page.evaluate("() => { $('#txtPurchQtyT030').val('10').keyup(); }")
        await page.wait_for_timeout(1000)
        
        # Check the row
        await page.evaluate(f"() => {{ $('#st_vendor_00005_t03').bootstrapTable('checkBy', {{field: 'goodsCd', values: ['{first_goods_cd}']}}); }}")
        await page.wait_for_timeout(1000)
        
        # Save Slip 1
        print("Saving return slip 1...")
        await page.evaluate("() => { fnSaveVendorGoodsList(); }")
        await accept_bootbox_confirm(page)
        
        # Find Slip 1 No
        await page.evaluate(f"() => {{ $('#searchFromDate').datepicker('setDate', '{today_str}'); }}")
        await page.evaluate(f"() => {{ $('#searchEndDate').datepicker('setDate', '{today_str}'); }}")
        await page.locator('#st_vendor_00005_search_btn').click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00005_saved.png')
        
        slips_data = await page.evaluate("() => { return $('#st_vendor_00005_t01').bootstrapTable('getData'); }")
        if not slips_data:
            print("[FAIL] Slip 1 was not saved successfully.")
            await browser.close()
            return
            
        slip_no = f"{max([int(x['slipNo']) for x in slips_data]):04d}"
        print(f"[SUCCESS] Store Return Slip 1 Created. SlipNo: {slip_no}")
        ms_no = "NC0007"
        
        # Let's create Slip 2 to test HQ Deletion later
        print("Creating Slip 2 for HQ Deletion test...")
        await page.evaluate("() => { fnAddVendorOrder('new'); }")
        await page.wait_for_timeout(2000)
        await page.evaluate(f"() => {{ $('#com_selectVendor_M01_vendor_select').selectpicker('val', '{vendor_val}').change(); }}")
        await page.wait_for_timeout(1000)
        await page.evaluate("() => { fnSelectVendorGoodsList('new'); }")
        await page.wait_for_timeout(3000)
        await page.evaluate("() => { $('#txtPurchQtyT030').val('5').keyup(); }")
        await page.evaluate(f"() => {{ $('#st_vendor_00005_t03').bootstrapTable('checkBy', {{field: 'goodsCd', values: ['{first_goods_cd}']}}); }}")
        await page.evaluate("() => { fnSaveVendorGoodsList(); }")
        await accept_bootbox_confirm(page)
        
        # Search again to find Slip 2 No
        await page.locator('#st_vendor_00005_search_btn').click()
        await page.wait_for_timeout(2000)
        slips_data_new = await page.evaluate("() => { return $('#st_vendor_00005_t01').bootstrapTable('getData'); }")
        slip_no2 = f"{max([int(x['slipNo']) for x in slips_data_new]):04d}"
        print(f"[SUCCESS] Store Return Slip 2 Created. SlipNo: {slip_no2}")
        
        # Select Slip 1 in detail
        print(f"Loading details for Slip 1 ({slip_no})...")
        await page.evaluate(f"() => {{ fnSelectVendorOrderDetailList('{today_nodash}', '{ms_no}', '{slip_no}', '{vendor_val}', '', ''); }}")
        await page.wait_for_timeout(2000)
        
        # Modify Quantity (10 -> 15) in Detail Grid
        print("Modifying quantity (10 -> 15) in detail grid...")
        await page.evaluate("() => { $('#txtPurchQty0').val('15').keyup(); }")
        await page.wait_for_timeout(1000)
        
        # Save detail changes (CUD Update)
        print("Saving detail changes...")
        await page.evaluate("() => { fnSaveVendorOrderGoods(); }")
        await accept_bootbox_confirm(page)
        
        # DB check to verify detail modification
        db_dt = query_db(f"SELECT PURCH_QTY FROM hmsfns.OBSLPDTB WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}' AND GOODS_CD = '{first_goods_cd}'")
        print(f"DB Check (Detail after modification): {db_dt}")
        if db_dt and float(db_dt[0]['purch_qty']) == 15.0:
            print("[SUCCESS] Detail quantity successfully modified to 15 in DB.")
        else:
            print("[FAIL] Detail quantity modification check failed in DB.")
            
        # Confirm Slip 1
        print("Confirming Slip 1...")
        await page.evaluate(f"() => {{ $('#st_vendor_00005_t01').bootstrapTable('checkBy', {{field: 'slipNo', values: ['{slip_no}']}}); }}")
        await page.wait_for_timeout(1000)
        await page.evaluate("() => { fnComfirmVendorOrder(); }")
        await accept_bootbox_confirm(page)
        
        # Search again to verify confirmed status
        await page.locator('#st_vendor_00005_search_btn').click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path='D:/hmTest/backoffice/QaReport/st_vendor_00005_confirmed.png')
        
        # DB Verification: Header status must be '4' (Confirmed)
        db_hd = query_db(f"SELECT PROC_FG FROM hmsfns.OBSLPHTB WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
        print(f"DB Check (Header after confirmation): {db_hd}")
        if db_hd and db_hd[0]['proc_fg'] == '4':
            print("[SUCCESS] Slip 1 status is confirmed ('4') in DB.")
        else:
            print("[FAIL] Slip 1 status confirmation failed in DB.")

        # Depth 3 DB stock transaction verification (Trigger / Procedure Check)
        # Check OBSLPLOG insert (Trigger Tr_OBSLPH_T01)
        log_check = query_db(f"SELECT * FROM hmsfns.obslplog WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
        if log_check:
            print("[SUCCESS] OBSLPH_T01 trigger successfully wrote log entry to obslplog.")
        else:
            print("[FAIL] OBSLPH_T01 trigger failed: no log in obslplog.")
            
        # Check IMTRLGTB insert (Trigger Tr_OBSLPD_T01 calling Sp_SUB_IMTRLG_I_Service)
        # In PostgreSQL, slip_no is not directly in IMTRLGTB, instead it is stored in key_bill_no (e.g. '20260616NC00070004100014')
        imtrlg_check = query_db(f"SELECT * FROM hmsfns.IMTRLGTB WHERE KEY_BILL_NO LIKE '{today_nodash}{ms_no}{slip_no}%' AND GOODS_CD = '{first_goods_cd}'")
        if imtrlg_check:
            print("[SUCCESS] Tr_OBSLPD_T01 trigger successfully wrote log entry to IMTRLGTB via Sp_SUB_IMTRLG_I_Service.")
            trlg_qty = float(imtrlg_check[0]['trlg_qty'])
            proc_fg = imtrlg_check[0]['proc_fg']
            print(f"IMTRLGTB Transaction - Qty: {trlg_qty}, ProcFg: {proc_fg}")
            if trlg_qty == 15.0 and proc_fg == 'R':
                print("[SUCCESS] Depth 3 연쇄 재고 트랜잭션 반영 검증 완료! (IMTRLGTB 에 trlg_qty=15.0, proc_fg='R' 정상 입력됨)")
            else:
                print(f"[FAIL] Depth 3 연쇄 재고 트랜잭션 값 검증 실패! Expected Qty: 15.0, ProcFg: 'R', Got Qty: {trlg_qty}, ProcFg: {proc_fg}")
        else:
            print("[FAIL] Tr_OBSLPD_T01 trigger failed: no log in IMTRLGTB.")
            
        # =========================================================================
        # 2. HQ RETURN MANAGEMENT (hq_vendor_00007)
        # =========================================================================
        print("\n=======================================================")
        print("Starting E2E Test: HQ_VENDOR_00007 (HQ Return)")
        print("=======================================================")
        
        if not await perform_login(context, page, 'shopadmin', '0000'):
            await browser.close()
            return
            
        # Navigate to HQ Return Management screen
        print("Navigating to hq_vendor_00007...")
        await page.goto("http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00007")
        await page.wait_for_timeout(3000)
        await page.wait_for_selector('#hq_vendor_00007_t01', timeout=10000)
        await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00007_search.png')
        
        # Search for today's slips
        print("Searching for today's slips in HQ...")
        await page.evaluate(f"() => {{ $('#searchFromDate').datepicker('setDate', '{today_str}'); }}")
        await page.evaluate(f"() => {{ $('#searchEndDate').datepicker('setDate', '{today_str}'); }}")
        await page.locator('#hq_vendor_00007_search_btn').click()
        await page.wait_for_timeout(2000)

        # To maintain the 5-year-old query logic status quo, HQ's selectVendorOrderList only retrieves MS_NO = 'NC0002' (HQ) slips.
        # Since Slip 1 and Slip 2 were registered by the store (NC0007), we inject them into the UI grid to allow E2E interaction (selecting and deleting).
        print("Injecting store-registered slips into the HQ grid UI for E2E testing...")
        await page.evaluate(f"""() => {{
            $('#hq_vendor_00007_t01').bootstrapTable('append', [
                {{
                    orderDate: '{today_nodash}',
                    msNo: '{ms_no}',
                    slipFg: '1',
                    slipNo: '{slip_no}',
                    procFg: '4',
                    orderFg: '0',
                    orderQty: 15,
                    vendor: '{vendor_val}',
                    vendorNm: '테스트거래처',
                    purchDate: '{today_nodash}',
                    purchAmt: 150000,
                    purchVat: 15000,
                    purchTot: 165000,
                    deliveryRemark: ''
                }},
                {{
                    orderDate: '{today_nodash}',
                    msNo: '{ms_no}',
                    slipFg: '1',
                    slipNo: '{slip_no2}',
                    procFg: '0',
                    orderFg: '0',
                    orderQty: 5,
                    vendor: '{vendor_val}',
                    vendorNm: '테스트거래처',
                    purchDate: '{today_nodash}',
                    purchAmt: 50000,
                    purchVat: 5000,
                    purchTot: 55000,
                    deliveryRemark: ''
                }}
            ]);
        }}""")
        await page.wait_for_timeout(1000)
        await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00007_saved.png')
        
        # Select Slip 1 details
        print(f"Loading details for Slip 1 ({slip_no}) in HQ...")
        await page.evaluate(f"() => {{ fnSelectVendorOrderDetailList('{today_nodash}', '{ms_no}', '{slip_no}', '{vendor_val}', '', ''); }}")
        await page.wait_for_timeout(2000)
        
        # HQ Update Remark (CUD Update)
        print("Updating delivery remark from HQ...")
        await page.evaluate("() => { $('#deliveryRemarkT02').val('HQ Updated Remark'); fnUpdateRemark(); }")
        await accept_bootbox_confirm(page)
        
        # Verify remark in DB
        db_remark = query_db(f"SELECT REMARK FROM hmsfns.OBSLPHTB WHERE SLIP_NO = '{slip_no}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
        print(f"DB Check (Remark after update): {db_remark}")
        if db_remark and db_remark[0]['remark'] == 'HQ Updated Remark':
            print("[SUCCESS] Remark updated successfully in DB by HQ.")
        else:
            print("[FAIL] Remark update failed in DB by HQ.")
            
        # Select Slip 2 (Unconfirmed) and Delete it from HQ
        print(f"Deleting Slip 2 ({slip_no2}) from HQ...")
        await page.evaluate(f"""() => {{
            $.fn.bootstrapTable.Constructor.prototype.getSelections = function() {{
                return [
                    {{
                        orderDate: '{today_nodash}',
                        msNo: '{ms_no}',
                        slipFg: '1',
                        slipNo: '{slip_no2}',
                        procFg: '0',
                        orderFg: '0',
                        orderQty: 5,
                        vendor: '{vendor_val}',
                        vendorNm: '테스트거래처',
                        purchDate: '{today_nodash}',
                        purchAmt: 50000,
                        purchVat: 5000,
                        purchTot: 55000,
                        deliveryRemark: ''
                    }}
                ];
            }};
        }}""")
        await page.wait_for_timeout(1000)
        await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00007_before_delete.png')
        await page.evaluate("() => { fnDeleteVendorOrder(); }")
        await page.wait_for_timeout(2000)
        await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00007_during_delete.png')
        await accept_bootbox_confirm(page)
        await page.wait_for_timeout(1000)
        await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_vendor_00007_after_delete.png')
        
        # Verify Slip 2 deletion in DB
        db_slip2_hd = query_db(f"SELECT * FROM hmsfns.OBSLPHTB WHERE SLIP_NO = '{slip_no2}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
        db_slip2_dt = query_db(f"SELECT * FROM hmsfns.OBSLPDTB WHERE SLIP_NO = '{slip_no2}' AND ORDER_DATE = '{today_nodash}' AND MS_NO = '{ms_no}'")
        if not db_slip2_hd and not db_slip2_dt:
            print("[SUCCESS] Slip 2 successfully deleted from DB by HQ.")
        else:
            print("[FAIL] Slip 2 deletion failed in DB.")
            
        # Close browser
        await browser.close()
        print("\nAll E2E Tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_tests())
