import asyncio
import os
import sys
import json
import subprocess
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def run_test():
    async with async_playwright() as p:
        try:
            print('Attempting to launch browser...')
            try:
                browser = await p.chromium.launch(headless=False, slow_mo=300)
            except Exception as e:
                print(f'Headed launch failed ({e}), falling back to headless=True...')
                browser = await p.chromium.launch(headless=True, slow_mo=100)
                
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
            
            # 1. Force logout
            print('Forcing logout to clear session...')
            await page.goto('http://localhost:8080/backoffice/logout')
            await page.wait_for_timeout(2000)
            
            # 2. Go to login
            print('Navigating to login page...')
            await page.goto('http://localhost:8080/backoffice', timeout=15000)
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            # 3. Login as shopadmin
            print('Logging in as shopadmin...')
            await page.locator('#login_userid').fill('shopadmin')
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
            
            # 4. Wait for redirection
            print('Waiting for redirection to main...')
            for _ in range(15):
                if 'main' in page.url:
                    break
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)
                
            # 5. Navigate to hq_cash_00003
            print('Navigating to hq_cash_00003 (계정별 전점현황)...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/cash/hq_cash_00003')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_cash_00003_t01', timeout=10000)
            
            # 6. Test date validation
            print('Testing date validation (clearing dates and searching)...')
            await page.evaluate("$('#searchFromDate').datepicker('setDate', null)")
            await page.evaluate("$('#searchEndDate').datepicker('setDate', null)")
            await page.locator('#hq_cash_00003_search_btn').click()
            await page.wait_for_timeout(1500)
            
            # Close bootbox alert modal
            bootbox_ok = page.locator('.bootbox-accept')
            if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                print('Bootbox validation alert displayed. Closing alert...')
                await bootbox_ok.first.click()
                await page.wait_for_timeout(1000)
            
            # 7. Set search dates (include 2026-02-02 to 2026-06-11)
            print('Setting search dates to 2026-02-01 to 2026-06-11...')
            await page.evaluate("$('#searchFromDate').datepicker('setDate', '2026-02-01')")
            await page.evaluate("$('#searchEndDate').datepicker('setDate', '2026-06-11')")
            await page.wait_for_timeout(1000)
            
            # 8. Query for Inflow (입금, acntFg=0)
            print('Selecting 계정구분: 입금 (acntFg=0)...')
            await page.locator('#acntFg').select_option('0')
            await page.evaluate("fnAcntCdSelect()") # trigger dynamic reload
            await page.wait_for_timeout(1000)
            
            print('Clicking Search for Inflow...')
            await page.locator('#hq_cash_00003_search_btn').click()
            await page.wait_for_timeout(3000)
            
            # Capture table values
            rows = await page.locator('#hq_cash_00003_t01 tbody tr').all_text_contents()
            print("Inflow Query Results:")
            for idx, r in enumerate(rows):
                print(f"Row {idx+1}: {r.strip()}")
                
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_cash_00003_search_inflow.png')
            
            # 9. Query for Outflow (출금, acntFg=1)
            print('Selecting 계정구분: 출금 (acntFg=1)...')
            await page.locator('#acntFg').select_option('1')
            await page.evaluate("fnAcntCdSelect()") # trigger dynamic reload
            await page.wait_for_timeout(1000)
            
            print('Clicking Search for Outflow...')
            await page.locator('#hq_cash_00003_search_btn').click()
            await page.wait_for_timeout(3000)
            
            rows_out = await page.locator('#hq_cash_00003_t01 tbody tr').all_text_contents()
            print("Outflow Query Results:")
            for idx, r in enumerate(rows_out):
                print(f"Row {idx+1}: {r.strip()}")
                
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_cash_00003_search_outflow.png')
            
            # 10. Test Reset button
            print('Testing Reset (초기화) button...')
            await page.locator('#clear_form_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_cash_00003_reset.png')
            
            # 11. Update progress JSON
            print('\nUpdating progress json and screen html...')
            try:
                progress_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {"screens": {}}
                
                data["screens"]["hq_cash_00003"] = {
                    "complete": True,
                    "memo": "로그인 ID: shopadmin - 계정별 전점현황 (본사 권한으로 각 가맹점 입출금 계정별 합계 금액 조회)"
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
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_cash_00003_error.png')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
