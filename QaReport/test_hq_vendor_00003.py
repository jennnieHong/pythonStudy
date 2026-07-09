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

SCREENSHOT_DIR = r"C:\Users\uoshj\.gemini\antigravity-ide\brain\a6eb74d7-4237-4316-bd5d-fbf2d71150e6"

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
        await page.wait_for_timeout(1000)

async def run_e2e_test():
    # 0. Temporarily change shopadmin's ms_no to NC0007 and emp_id to 9999 to query NC0007 data and avoid Musersx1 unique constraint
    print("[DB SETUP] Updating shopadmin ms_no to NC0007 and emp_id to 9999...")
    query_db("UPDATE hmsfns.MUSERSTB SET MS_NO = 'NC0007', EMP_ID = '9999' WHERE USER_ID = 'shopadmin'")
    
    # 0.1 Reset PURCH_SEND_YN = 'N' for the test targets to allow testing
    print("[DB SETUP] Resetting PURCH_SEND_YN to 'N' for 20240201 orders...")
    query_db("UPDATE hmsfns.OBSLPHTB SET PURCH_SEND_YN = 'N', PURCH_SEND_DATE = NULL, PURCH_SEND_MAIL_ADDR = NULL WHERE ORDER_DATE = '20240201' AND MS_NO = 'NC0007'")
    
    try:
        async with async_playwright() as p:
            print("Starting Playwright (headless=False)...")
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()
            
            # Intercept network responses to capture server exceptions
            async def handle_response(response):
                if "vendor" in response.url or "MailInterface" in response.url:
                    try:
                        text = await response.text()
                        if response.status != 200:
                            print(f"\n[SERVER RESPONSE ERROR] URL: {response.url}\nStatus: {response.status}\nBody:\n{text}\n")
                    except Exception as e:
                        pass
            page.on("response", handle_response)
            
            # 1. Login as shopadmin
            logged_in = await perform_login(context, page, "shopadmin", "0000")
            if not logged_in:
                await browser.close()
                return
                
            # 2. Navigate to hq_vendor_00003
            url = "http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00003"
            print(f"Navigating to {url}...")
            await page.goto(url)
            await page.wait_for_timeout(2000)
            
            # Screenshot 1: Initial State
            ss_path_1 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00003_1_initial.png")
            await page.screenshot(path=ss_path_1)
            print(f"Saved Screenshot 1 (Initial) to {ss_path_1}")
            
            # 3. Set Date filter to 2024-02-01 (since the inputs are readonly, use JS evaluation)
            print("Setting search date to 2024-02-01...")
            await page.evaluate("""
                document.getElementById('searchFromDate').value = '2024-02-01';
                document.getElementById('searchEndDate').value = '2024-02-01';
            """)
            await page.wait_for_timeout(500)
            
            # Click search
            print("Clicking search button...")
            await page.click("#hq_vendor_00003_searchOrderList_btn")
            await page.wait_for_timeout(2000)
            
            # Screenshot 2: Search Results
            ss_path_2 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00003_2_searched.png")
            await page.screenshot(path=ss_path_2)
            print(f"Saved Screenshot 2 (Searched) to {ss_path_2}")
            
            # 4. Click the first row to load detail panel
            # Col 2 is the 'purchReqNo' (발주번호) column that triggers fnDetail
            print("Clicking the first order's purchReqNo to load detail...")
            await page.locator("#hq_vendor_00003_t01 tbody tr").first.locator("td").nth(1).click()
            await page.wait_for_timeout(2000)
            
            # Screenshot 3: Details Loaded
            ss_path_3 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00003_3_detail.png")
            await page.screenshot(path=ss_path_3)
            print(f"Saved Screenshot 3 (Detail Loaded) to {ss_path_3}")
            
            # 5. Click '미리보기' button
            print("Opening email preview modal...")
            await page.click("#hq_vendor_00003_previewOrder_btn")
            await page.wait_for_timeout(2000)
            
            # Screenshot 4: Email Preview Modal
            ss_path_4 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00003_4_preview.png")
            await page.screenshot(path=ss_path_4)
            print(f"Saved Screenshot 4 (Preview Modal) to {ss_path_4}")
            
            # Close Preview Modal
            print("Closing preview modal...")
            await page.click("#closeModal")
            await page.wait_for_timeout(1000)
            
            # 6. Check first row and click '출력' button
            print("Checking the row for print...")
            await page.evaluate("""
                $('#hq_vendor_00003_t01').bootstrapTable('check', 0);
            """)
            await page.wait_for_timeout(1000)
            
            print("Clicking print button...")
            await page.click("#hq_vendor_00003_printOrder_btn")
            await page.wait_for_timeout(2000)
            
            # Screenshot 5: Print preview or state after print click
            ss_path_5 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00003_5_print_preview.png")
            await page.screenshot(path=ss_path_5)
            print(f"Saved Screenshot 5 (Print State) to {ss_path_5}")
            
            # 7. Click '메일전송' button
            print("Clicking email send button...")
            await page.click("#hq_vendor_00003_emailOrder_btn")
            await page.wait_for_timeout(3000)
            
            # Dismiss success alert
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                print('Closing success bootbox alert...')
                await bootbox_ok.first.click()
                await page.wait_for_timeout(1000)
                
            # Screenshot 6: Email Sent State
            ss_path_6 = os.path.join(SCREENSHOT_DIR, "hq_vendor_00003_6_mail_sent.png")
            await page.screenshot(path=ss_path_6)
            print(f"Saved Screenshot 6 (Mail Sent) to {ss_path_6}")
            
            # =========================================================================
            # DB Validation
            # =========================================================================
            print("\n=== Performing Database Validation ===")
            
            # Check 1: IF_RTMS_MAILQUEUE 적재 여부
            mail_records = query_db("""
                SELECT MID, SNAME, SMAIL, SUBJECT, IF_YN 
                  FROM hmsfns.IF_RTMS_MAILQUEUE 
                 WHERE SUBJECT LIKE '%%발주 요청서%%' 
                 ORDER BY CREATE_DTIME DESC LIMIT 3
            """)
            print("\n[DB VALIDATION] Recent mail queue entries:")
            if mail_records:
                for idx, mr in enumerate(mail_records):
                    print(f"  [{idx+1}] MID={mr['mid']}, SNAME={mr['sname']}, SMAIL={mr['smail']}, SUBJECT={mr['subject']}, IF_YN={mr['if_yn']}")
            else:
                print("  [WARNING] No records found in IF_RTMS_MAILQUEUE matching '발주 요청서'!")
                
            # Check 2: OBSLPHTB.PURCH_SEND_YN 및 PURCH_SEND_DATE 갱신 여부
            updated_orders = query_db("""
                SELECT ORDER_DATE, MS_NO, SLIP_NO, PURCH_SEND_YN, PURCH_SEND_DATE, PURCH_SEND_MAIL_ADDR 
                  FROM hmsfns.OBSLPHTB 
                 WHERE ORDER_DATE = '20240201' AND MS_NO = 'NC0007'
                 ORDER BY SLIP_NO
            """)
            print("\n[DB VALIDATION] Updated OBSLPHTB status:")
            if updated_orders:
                for idx, uo in enumerate(updated_orders):
                    print(f"  [{idx+1}] Date={uo['order_date']}, Slip={uo['slip_no']}, SendYn={uo['purch_send_yn']}, SendDate={uo['purch_send_date']}, SendAddr={uo['purch_send_mail_addr']}")
            else:
                print("  [WARNING] No records found in OBSLPHTB for 20240201 / NC0007!")
                
            # Check 3: Downstream 수불 이력 (IMTRLGTB) 및 로그 (obslplog) 검증
            # 이 화면은 이메일 전송에 국한되므로 수불 기록이 없어야 함
            key_bill_prefix = "20240201NC0007%"
            imtrlg_recs = query_db("SELECT COUNT(*) AS cnt FROM hmsfns.IMTRLGTB WHERE KEY_BILL_NO LIKE %s", (key_bill_prefix,))
            print(f"\n[DB VALIDATION] Downstream IMTRLGTB records count: {imtrlg_recs[0]['cnt'] if imtrlg_recs else 0} (Expected: 0)")
            
            obslplog_recs = query_db("SELECT COUNT(*) AS cnt FROM hmsfns.obslplog WHERE MS_NO = 'NC0007' AND ORDER_DATE = '20240201'")
            print(f"[DB VALIDATION] Downstream obslplog records count: {obslplog_recs[0]['cnt'] if obslplog_recs else 0} (Expected: 0)")
            
            await browser.close()
            print("\nE2E Playwright test and validation finished.")
            
    finally:
        # Restore shopadmin's ms_no to NC0002 and emp_id to 0001
        print("[DB CLEANUP] Restoring shopadmin ms_no to NC0002 and emp_id to 0001...")
        query_db("UPDATE hmsfns.MUSERSTB SET MS_NO = 'NC0002', EMP_ID = '0001' WHERE USER_ID = 'shopadmin'")

if __name__ == '__main__':
    asyncio.run(run_e2e_test())
