import asyncio
import os
import sys
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

SCREENSHOT_DIR = r"D:\hmTest\backoffice\QaReport"

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
        await page.wait_for_timeout(1500)

async def run_e2e_test():
    # 0. Set up user/store mapping for fnbadmin (make NC0005 part of C002 as HQ)
    print("[DB SETUP] Updating store NC0005 to belong to chain C002 as HQ...")
    query_db("UPDATE hmsfns.MMEMBSTB SET chain_no = 'C002', chain_hq_yn = 'Y' WHERE ms_no = 'NC0005'")
    
    print("[DB SETUP] Cleaning up any existing test records for contract carryover to extend dates...")
    query_db("DELETE FROM hmsfns.TPRICETB WHERE price_fg='2' AND start_date='20260801'")
    query_db("DELETE FROM hmsfns.TESHISTB WHERE estim_type_cd='001' AND estim_from_cd='0002' AND estim_fr_date='20260801'")
    query_db("UPDATE hmsfns.TESFRHTB SET estim_fr_date='20230101', estim_to_date='20231231' WHERE chain_no='C002' AND estim_type_cd='001' AND estim_from_cd='0002'")
    
    try:
        async with async_playwright() as p:
            print("Starting Playwright (headless=True)...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()
            
            # 1. Login as fnbadmin
            logged_in = await perform_login(context, page, "fnbadmin", "1")
            if not logged_in:
                await browser.close()
                return
                
            # Response listener to inspect Ajax responses
            async def handle_response(response):
                if "selectEstimType" in response.url or "search" in response.url or "extendDate" in response.url:
                    try:
                        text = await response.text()
                        print(f"\n[API RESPONSE] URL: {response.url}\n  STATUS: {response.status}\n  BODY: {text[:500]}")
                    except Exception as e:
                        print(f"[API RESPONSE ERROR] {e}")
            page.on("response", handle_response)

            async def handle_request(request):
                if "selectEstimType" in request.url or "search" in request.url or "extendDate" in request.url:
                    print(f"\n[API REQUEST] URL: {request.url}\n  METHOD: {request.method}\n  POST DATA: {request.post_data}")
            page.on("request", handle_request)
            
            page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
                
            # 2. Navigate to hq_esti_00008
            url = "http://localhost:8080/backoffice/view/main/hq/estimate/hq_esti_00008"
            print(f"Navigating to {url}...")
            await page.goto(url)
            await page.wait_for_timeout(3000)
            
            # Screenshot 1: Initial State
            ss_path_1 = os.path.join(SCREENSHOT_DIR, "hq_esti_00008_1_initial.png")
            await page.screenshot(path=ss_path_1)
            print(f"Saved Screenshot 1 (Initial) to {ss_path_1}")
            
            # Wait for type select options to load
            print("Waiting for estimTypeCd options to load...")
            try:
                await page.wait_for_function("""
                    () => {
                        const sel = document.getElementById('searchEstimTypeCd_estimTypeCd_select');
                        return sel && sel.options.length > 1;
                    }
                """, timeout=15000)
            except Exception as e:
                print(f"[WARNING] Timeout waiting for type select options: {e}")

            # Print initial select options
            opts = await page.evaluate("""
                (() => {
                    const typeSel = document.getElementById('searchEstimTypeCd_estimTypeCd_select');
                    const typeOpts = typeSel ? Array.from(typeSel.options).map(o => ({value: o.value, text: o.text})) : [];
                    return { typeOpts };
                })()
            """)
            print("Initial estimTypeCd options:", opts['typeOpts'])

            # 3. Select estimate form in search criteria
            print("Selecting estimate type '001'...")
            await page.evaluate("""
                const typeSelect = document.getElementById('searchEstimTypeCd_estimTypeCd_select');
                if (typeSelect) {
                    typeSelect.value = '001';
                    $(typeSelect).selectpicker('refresh');
                    // Trigger change to load estimFromCd options
                    $(typeSelect).trigger('change');
                }
            """)
            
            # Wait for from select options to load
            print("Waiting for estimFromCd options to load...")
            try:
                await page.wait_for_function("""
                    () => {
                        const sel = document.getElementById('searchEstimTypeCd_estimFromCd_select');
                        return sel && sel.options.length > 0 && Array.from(sel.options).some(o => o.value === '0002');
                    }
                """, timeout=15000)
            except Exception as e:
                print(f"[WARNING] Timeout waiting for from select options: {e}")

            # Print options of second select after change
            opts2 = await page.evaluate("""
                (() => {
                    const fromSel = document.getElementById('searchEstimTypeCd_estimFromCd_select');
                    const fromOpts = fromSel ? Array.from(fromSel.options).map(o => ({value: o.value, text: o.text})) : [];
                    return { fromOpts };
                })()
            """)
            print("estimFromCd options after change:", opts2['fromOpts'])
            
            print("Selecting estimate form '0002'...")
            await page.evaluate("""
                const fromSelect = document.getElementById('searchEstimTypeCd_estimFromCd_select');
                if (fromSelect) {
                    fromSelect.value = '0002';
                    $(fromSelect).selectpicker('refresh');
                }
            """)
            await page.wait_for_timeout(1000)
            
            # Click search
            print("Clicking search button...")
            await page.click("#hq_esti_00008_search_btn")
            await page.wait_for_timeout(3000)
            
            # Screenshot 2: Search Results
            ss_path_2 = os.path.join(SCREENSHOT_DIR, "hq_esti_00008_2_searched.png")
            await page.screenshot(path=ss_path_2)
            print(f"Saved Screenshot 2 (Searched) to {ss_path_2}")
            
            # 4. Input extend dates
            print("Inputting extend From/To dates...")
            await page.evaluate("""
                document.getElementById('extendFromDate').value = '2026-08-01';
                document.getElementById('extendEndDate').value = '2026-08-31';
            """)
            await page.wait_for_timeout(500)
            
            # Click extend/carryover
            print("Clicking carryover (이월) button...")
            await page.click("#hq_esti_00008_extend_btn")
            await page.wait_for_timeout(1000)
            
            # Screenshot 3: Before Confirm
            ss_path_3_pre = os.path.join(SCREENSHOT_DIR, "hq_esti_00008_3_confirm_dialog.png")
            await page.screenshot(path=ss_path_3_pre)
            print(f"Saved Screenshot (Confirm Dialog) to {ss_path_3_pre}")
            
            # Accept confirmation dialog
            await accept_bootbox_confirm(page)
            await page.wait_for_timeout(3000)
            
            # Screenshot 3: Carryover Finished
            ss_path_3 = os.path.join(SCREENSHOT_DIR, "hq_esti_00008_4_finished.png")
            await page.screenshot(path=ss_path_3)
            print(f"Saved Screenshot 3 (Finished) to {ss_path_3}")
            
            # Database Verification
            print("\n[DB CHECK - TESFRHTB HEADER (Depth 1)]")
            frh_row = query_db("SELECT chain_no, estim_type_cd, estim_from_cd, estim_fr_date, estim_to_date, estim_proc_fg FROM hmsfns.TESFRHTB WHERE chain_no='C002' AND estim_type_cd='001' AND estim_from_cd='0002'")
            print("  TESFRHTB:", frh_row)
            
            print("\n[DB CHECK - TPRICETB (Depth 2)]")
            tprice_rows = query_db("SELECT chain_no, goods_cd, price_fg, start_date, end_date, price, pre_price FROM hmsfns.TPRICETB WHERE chain_no='C002' AND price_fg='2' AND start_date='20260801'")
            print("  TPRICETB:")
            for r in tprice_rows:
                print("    ->", r)
                
            print("\n[DB CHECK - TESHISTB HISTORY]")
            teshist_rows = query_db("SELECT chain_no, estim_goods_cd, estim_seq, estim_fr_date, estim_to_date, estim_aly_prc FROM hmsfns.TESHISTB WHERE chain_no='C002' AND estim_type_cd='001' AND estim_from_cd='0002' AND estim_fr_date='20260801'")
            print("  TESHISTB:")
            for r in teshist_rows:
                print("    ->", r)

            # Trigger cascade check (Depth 3 check: MPRICETB & Log table TPRILGTB)
            print("\n[DB CHECK - TRIGGER CASCADE (Depth 3)]")
            tprilg_recs = query_db("SELECT COUNT(*) FROM hmsfns.TPRILGTB WHERE chain_no='C002' AND price_fg='2' AND start_date='20260801'")
            print("  TPRILGTB logs count (expected >0):", tprilg_recs[0]['count'] if tprilg_recs else 0)
            
            # Look at MPRICETB
            mprice_recs = query_db("SELECT COUNT(*) FROM hmsfns.MPRICETB WHERE goods_cd IN (SELECT estim_goods_cd FROM hmsfns.TESVDUTB WHERE chain_no='C002' AND estim_type_cd='001' AND estim_from_cd='0002' AND estim_prc_apply_yn='Y') AND price_fg='2' AND start_date='20260801'")
            print("  MPRICETB records count (expected >0 if TPRICETB update/insert triggers selectMpricetbRestore/Calculated and inserts into MPRICETB):", mprice_recs[0]['count'] if mprice_recs else 0)
            
            await browser.close()
            print("\nE2E Playwright test and validation finished.")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
    finally:
        # Restore store mapping
        print("[DB CLEANUP] Restoring store NC0005 mapping to chain C001...")
        query_db("UPDATE hmsfns.MMEMBSTB SET chain_no = 'C001', chain_hq_yn = 'N' WHERE ms_no = 'NC0005'")

if __name__ == '__main__':
    asyncio.run(run_e2e_test())
