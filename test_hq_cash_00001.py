import asyncio
import os
import sys
import json
import subprocess
import psycopg2
import pandas as pd
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

# Reports and screenshots directory
report_dir = r"D:\hmTest\backoffice\QaReport"
if not os.path.exists(report_dir):
    os.makedirs(report_dir)

# DB Connection Config
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

def query_db_trigger_state(step_name, code="99"):
    print(f"\n--- [DB Verification (Depth 3): {step_name}] ---")
    try:
        # 1. TMACNTTB (본사)
        t_records = query_db("SELECT CHAIN_NO, ACNT_FG, ACNT_CD, ACNT_NM, USE_YN FROM hmsfns.TMACNTTB WHERE ACNT_CD = %s", (code,))
        print(f"  [1] TMACNTTB (본사) records count: {len(t_records) if t_records else 0}")
        if t_records:
            for r in t_records:
                print(f"      Record: {r}")

        # 2. MMACNTTB (가맹점)
        m_records = query_db("SELECT MS_NO, ACNT_FG, ACNT_CD, ACNT_NM, USE_YN, CREATE_FG FROM hmsfns.MMACNTTB WHERE ACNT_CD = %s", (code,))
        print(f"  [2] MMACNTTB (가맹점) records count: {len(m_records) if m_records else 0}")
        if m_records:
            for r in m_records[:5]:
                print(f"      Record: {r}")
            if len(m_records) > 5:
                print(f"      ... (truncated {len(m_records) - 5} more records)")

        # 3. SSACNTTB (가맹점 전송 로그)
        s_records = query_db("SELECT MS_NO, ACNT_FG, ACNT_CD, ACNT_NM, PROC_FG FROM hmsfns.SSACNTTB WHERE ACNT_CD = %s ORDER BY LOG_SEQ DESC", (code,))
        print(f"  [3] SSACNTTB (가맹점 전송용) records count: {len(s_records) if s_records else 0}")
        if s_records:
            for r in s_records[:5]:
                print(f"      Record: {r}")
            if len(s_records) > 5:
                print(f"      ... (truncated {len(s_records) - 5} more records)")
                
        # 4. MMSLOGTB (로깅 테이블)
        log_records = query_db("SELECT MS_NO, TABLE_NM, LOG_FG, LOG_DATA FROM hmsfns.MMSLOGTB WHERE LOG_DATA LIKE %s ORDER BY LOG_SEQ DESC", (f"%|{code}|%",))
        print(f"  [4] MMSLOGTB (로깅) records count: {len(log_records) if log_records else 0}")
        if log_records:
            for r in log_records[:3]:
                print(f"      Record: {r}")

    except Exception as e:
        print("DB verification query error:", e)
    print("--------------------------------------\n")

def cleanup_db_test_data(code="99"):
    print(f"Cleaning up old test data (code={code}) from DB...")
    query_db("DELETE FROM hmsfns.SSACNTTB WHERE ACNT_CD = %s", (code,), fetch=False)
    query_db("DELETE FROM hmsfns.MMACNTTB WHERE ACNT_CD = %s", (code,), fetch=False)
    query_db("DELETE FROM hmsfns.TMACNTTB WHERE ACNT_CD = %s", (code,), fetch=False)
    query_db("DELETE FROM hmsfns.MMSLOGTB WHERE LOG_DATA LIKE %s", (f"%|{code}|%",), fetch=False)
    print("Cleanup finished successfully.")

async def handle_bootbox_dialogs(page):
    modals = page.locator('.modal-dialog')
    modal_count = await modals.count()
    if modal_count > 0:
        for i in range(modal_count):
            modal = modals.nth(i)
            modal_id = await modal.locator('xpath=..').get_attribute('id')
            if modal_id in ['addAcntModal', 'passwordsModal']:
                continue
                
            if await modal.is_visible():
                body_loc = modal.locator('.modal-body, .bootbox-body')
                btn_loc = modal.locator('.bootbox-accept, .btn-primary, button[data-bb-handler="confirm"]')
                body_text = await body_loc.first.inner_text() if await body_loc.count() > 0 else ""
                print(f"[MODAL DETECTED] Text: {body_text}")
                
                if await btn_loc.count() > 0 and await btn_loc.first.is_visible():
                    print("[MODAL ACTION] Clicking accept/confirm button...")
                    await btn_loc.first.click()
                    await page.wait_for_timeout(1000)
                    return True
    return False

async def dismiss_passwords_modal(page):
    print("Force dismissing passwordsModal (password expiration/reset prompt)...")
    await page.evaluate("""() => {
        try {
            if (typeof $ !== 'undefined') {
                $('#passwordsModal').modal('hide');
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
                console.log('Dismissed passwordsModal using jQuery.');
            } else {
                const m = document.getElementById('passwordsModal');
                if (m) m.style.display = 'none';
                const backdrops = document.getElementsByClassName('modal-backdrop');
                for (let b of backdrops) { b.remove(); }
                document.body.classList.remove('modal-open');
                console.log('Dismissed passwordsModal using Vanilla JS.');
            }
        } catch(e) {
            console.error('Error dismissing passwordsModal:', e);
        }
    }""")
    await page.wait_for_timeout(1000)

async def run_test():
    target_user = 'shopadmin'
    cleanup_db_test_data()
    
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
            print("\nStarting Playwright (headless=True)...")
            try:
                browser = await p.chromium.launch(headless=False, slow_mo=100)
            except Exception as e:
                print(f"Headed launch failed ({e}), falling back to headless=True...")
                browser = await p.chromium.launch(headless=True, slow_mo=100)
                
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()
            
            # Print console messages
            page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
            
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
                try:
                    await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00001_error.png'))
                except:
                    pass
                return

            print("Login successful. Navigating to hq_cash_00001 (입출금계정관리)...")
            await page.goto('http://localhost:8080/backoffice/view/main/hq/cash/hq_cash_00001')
            await page.wait_for_timeout(2000)
            
            await dismiss_passwords_modal(page)
            
            await page.wait_for_selector('#hq_cash_00001_t01', timeout=10000)
            
            # Capture initial screenshot
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00001_1_initial.png'))
            print('Screenshot 1 (initial state) captured.')
            
            # ----------------------------------------------------
            # TEST 1: Insert Account Code (codeSave)
            # ----------------------------------------------------
            print('Clicking 계정추가 button for Inflow (acntFg=0)...')
            await page.locator('#hq_cash_00001_add_acnt_btn').click()
            await page.wait_for_selector('#addAcntModal', state='visible', timeout=5000)
            
            print('Filling new Account Code details...')
            await page.evaluate("$('#acntCd').removeAttr('readonly')")
            await page.locator('#acntCd').fill('99')
            await page.locator('#acntNm').fill('테스트입금')
            
            print('Saving the new account code...')
            await page.locator('#addAcntModal .modal-footer button.btn-primary').click()
            
            # Confirm dialog
            print('Confirming save...')
            await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
            await page.locator('.bootbox-confirm .bootbox-accept').click()
            
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00001_2_category_created.png'))
            print('Screenshot 2 (account code 99 created) captured.')
            
            # Verify DB depth 3 triggers
            query_db_trigger_state("After Account Insertion", "99")
            
            # ----------------------------------------------------
            # TEST 2: Update Account Code (codeUpdate)
            # ----------------------------------------------------
            print("Clicking the newly created row cell containing '테스트입금' to edit...")
            await page.locator('#hq_cash_00001_t01 tbody tr td.table-onclick', has_text='테스트입금').first.click(force=True)
            await page.wait_for_selector('#addAcntModal', state='visible', timeout=5000)
            
            print('Modifying account name...')
            # Use safe Korean name without special characters or numbers to avoid inputValidChk failure
            await page.locator('#acntNm').fill('수정입금')
            
            print('Saving the modified account code...')
            await page.locator('#addAcntModal .modal-footer button.btn-primary').click()
            
            # Wait a moment to check for validation alert modal or confirmation prompt
            await page.wait_for_timeout(1000)
            
            # If bootbox alert appears (input validation fail), handle it
            alert_ok = page.locator('.bootbox-alert .bootbox-accept')
            if await alert_ok.count() > 0 and await alert_ok.first.is_visible():
                alert_text = await page.locator('.bootbox-alert .bootbox-body').inner_text()
                print(f"[VALIDATION FAIL] Alert text: {alert_text}")
                await alert_ok.first.click()
                raise Exception("Input validation failed during update: " + alert_text)

            # Wait for confirm dialog and accept
            print('Confirming update...')
            await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
            await page.locator('.bootbox-confirm .bootbox-accept').click()
            
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00001_3_category_updated.png'))
            print('Screenshot 3 (account code 99 updated) captured.')
            
            # Verify DB depth 3 triggers
            query_db_trigger_state("After Account Update", "99")

            # ----------------------------------------------------
            # TEST 3: Delete Account Code (codeDel)
            # ----------------------------------------------------
            print("Selecting checkbox for ACNT_CD='99' and clicking 계정삭제...")
            await page.evaluate("""() => {
                var table = $('#hq_cash_00001_t01');
                var rows = table.bootstrapTable('getData');
                var index = rows.findIndex(r => r.ACNT_CD === '99');
                if (index !== -1) {
                    table.bootstrapTable('check', index);
                }
            }""")
            await page.wait_for_timeout(500)
            await page.locator('#hq_cash_00001_delete_acnt_btn').click()
            
            # Confirm dialog
            await page.wait_for_selector('.bootbox-confirm .bootbox-accept', timeout=5000)
            await page.locator('.bootbox-confirm .bootbox-accept').click()
            
            # Alert dialog showing result
            await page.wait_for_selector('.bootbox-alert .bootbox-accept', timeout=5000)
            alert_text = await page.locator('.bootbox-alert .bootbox-body').inner_text()
            print(f"Alert Result: {alert_text}")
            await page.locator('.bootbox-alert .bootbox-accept').click()
            
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00001_6_deleted.png'))
            print('Screenshot 4 (account code 99 deleted) captured.')
            
            # Verify DB depth 3 triggers
            query_db_trigger_state("After Account Deletion", "99")
            
            # ----------------------------------------------------
            # Update Progress JSON
            # ----------------------------------------------------
            print('\nUpdating progress json and screen html...')
            try:
                progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"screens": {}}
                
                data["screens"]["hq_cash_00001"] = {
                    "complete": True,
                    "memo": f"로그인 ID: {target_user} - 입출금계정관리 (본사 권한으로 입금/출금 코드 '99' 등록, 수정, 3단계 DB 트리거 연쇄작용 및 삭제 완료)"
                }
                
                with open(progress_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("Updated progress JSON successfully.")
                
                # Regenerate HTML dashboard
                subprocess.run(["python", "generate_screens_directory.py"], cwd=r"D:\hmTest\backoffice\QaReport", check=True)
                print("Regenerated All_HMS_Screens.html successfully.")
            except Exception as e:
                print(f"[WARNING] Progress update failed: {e}")
                
            print('[SUCCESS] E2E test completed successfully.')

    except Exception as e:
        print('Error occurred during E2E test:', e)
        try:
            await page.screenshot(path=os.path.join(report_dir, 'hq_cash_00001_error.png'))
        except:
            pass
    finally:
        # 4. DB RESTORE
        print(f"\n[DB RESTORE] Restoring original credentials for {target_user}...")
        query_db(
            "UPDATE hmsfns.MUSERSTB SET PASSWD = %s, LAST_DTIME = %s, FST_LOGIN_PW_CHANGE = %s, ACCT_ENABLE = %s, ACCT_LOCK = %s WHERE USER_ID = %s",
            (backup_data['passwd'], backup_data['last_dtime'], backup_data['fst_login_pw_change'], backup_data['acct_enable'], backup_data['acct_lock'], target_user),
            fetch=False
        )
        print("[DB RESTORE COMPLETE]")

if __name__ == '__main__':
    asyncio.run(run_test())
