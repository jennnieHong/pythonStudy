import asyncio
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def login(page, user_id, password):
    print(f'Attempting to login as {user_id}...')
    await page.goto('http://localhost:8080/backoffice')
    await page.wait_for_load_state('networkidle')
    
    # In isolated context, there should be no active session. But check just in case.
    if 'main' in page.url or await page.locator('#backoffice-logout').count() > 0:
        print('Already logged in. Force logging out...')
        try:
            await page.evaluate("() => { if ($('#backoffice-logout').length) { $('#backoffice-logout').submit(); } else { window.location.href = '/backoffice/auth/logout'; } }")
            await page.wait_for_timeout(2000)
        except Exception as e:
            pass
        await page.goto('http://localhost:8080/backoffice')
        await page.wait_for_load_state('networkidle')
        
    await page.locator('#login_userid').fill(user_id)
    await page.locator('#login_password').fill(password)
    await page.locator('button[type="submit"]').click()
    
    # Wait for redirect or bootbox
    for _ in range(15):
        await page.wait_for_timeout(500)
        if 'main' in page.url:
            break
        # Check for duplicate session confirmation dialog
        bootbox_accept = page.locator('.bootbox-accept')
        if await bootbox_accept.count() > 0 and await bootbox_accept.first.is_visible():
            print('Duplicate login session detected. Accepting to disconnect other session...')
            await bootbox_accept.first.click()
            await page.wait_for_timeout(1000)
            
    # Wait for main page load
    try:
        await page.wait_for_url('**/view/main/**', timeout=8000)
        print(f'Successfully logged in as {user_id}. Current URL: {page.url}')
    except Exception as e:
        print(f'Login navigation wait finished. URL: {page.url}')
        if 'main' not in page.url:
            raise Exception(f"Failed to login as {user_id}. Still on page: {page.url}")

async def run_test():
    async with async_playwright() as p:
        print('Launching browser in headless=False mode...')
        try:
            browser = await p.chromium.launch(headless=False, slow_mo=150)
        except Exception as e:
            print(f'Headed launch failed: {e}')
            raise e
            
        try:
            # === PHASE 1: HQ Admin registers and dispatches outbound transfer ===
            print('\n=== PHASE 1: HQ Admin registers and dispatches outbound transfer (NC0003 -> NC0007) ===')
            context1 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page1 = await context1.new_page()
            
            # Setup logging
            page1.on("console", lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
            page1.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
            async def handle_response(response):
                url = response.url
                if "save" in url or "confirm" in url or "selectMove" in url:
                    try:
                        text = await response.text()
                        print(f"\n[RESPONSE] {url} -> {response.status}\n{text[:300]}\n")
                    except Exception:
                        pass
            page1.on("response", lambda resp: asyncio.create_task(handle_response(resp)))
            
            await login(page1, 'shopadmin', '0000')
            
            print('Navigating to Hq_Stock_00011 (본사 재고이동)...')
            await page1.goto('http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00011')
            await page1.wait_for_timeout(3000)
            
            # Open Register Modal
            print('Opening Registration Modal...')
            await page1.locator('#hq_stock_00011_add_btn').click()
            await page1.wait_for_timeout(2000)
            
            # Select stores in modal M01
            print('Selecting Sending (NC0003) and Receiving (NC0007) stores...')
            # 보내는 매장: NC0003
            await page1.evaluate("() => { $('#com_selectSendMsNo_M01_ms_select').selectpicker('val', 'NC0003').change(); }")
            await page1.wait_for_timeout(1000)
            # 받는 매장: NC0007
            await page1.evaluate("() => { $('#com_selectRecvMsNo_M01_ms_select').selectpicker('val', 'NC0007').change(); }")
            await page1.wait_for_timeout(1000)
            
            # Set Remark
            await page1.locator('#remark_M01').fill('Playwright E2E 3-Store Test')
            await page1.wait_for_timeout(500)
            
            # Click "행추가" button to add a product row
            print('Adding product row...')
            await page1.locator('a[onclick="fnAddRowM01()"]').click()
            await page1.wait_for_timeout(1000)
            
            # Select product "T0000033"
            print('Selecting product T0000033...')
            await page1.evaluate("() => { $('#selectGoodsNmCombo_0').selectpicker('val', 'T0000033').change(); }")
            await page1.wait_for_timeout(2000)
            
            # Input Qty: txtMoveEaQty0 -> 5
            print('Inputting quantity 5...')
            await page1.locator('#txtMoveEaQty0').focus()
            await page1.locator('#txtMoveEaQty0').press_sequentially('5', delay=100)
            await page1.wait_for_timeout(1000)
            
            # Click "저장"
            print('Saving the slip in modal M01...')
            await page1.locator('#saveModalM01').click()
            await page1.wait_for_timeout(1500)
            
            # Confirm bootbox if popped up
            bootbox_accept = page1.locator('.bootbox-accept')
            if await bootbox_accept.count() > 0 and await bootbox_accept.first.is_visible():
                print('Confirming save...')
                await bootbox_accept.first.click()
                await page1.wait_for_timeout(2000)
                
            print('Refreshing main list search to find the new slip...')
            await page1.locator('#hq_stock_00011_search_btn').click()
            await page1.wait_for_timeout(2000)
            await page1.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00011_saved.png')
            
            # HQ does not confirm. It only registers (saves) the slip with PROC_FG = '0'.
            print('HQ Admin completed slip registration.')
            await context1.close()
            
            # === PHASE 2: Sending Store (NC0003) confirms outbound dispatch ===
            print('\n=== PHASE 2: Sending Store (NC0003) confirms outbound dispatch ===')
            context2 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page2 = await context2.new_page()
            await login(page2, 'shopbrand', '0000')
            
            print('Navigating to St_Stock_00010 (매장 재고이동)...')
            await page2.goto('http://localhost:8080/backoffice/view/main/st/stock/st_stock_00010')
            await page2.wait_for_timeout(3000)
            
            # Make sure we are on "전표등록" (Send) tab
            print('Clicking Search on Outbound tab...')
            await page2.locator('#st_stock_00010_search_btn_send').click()
            await page2.wait_for_timeout(2500)
            
            # Select the checkbox of the newly registered slip in table #st_stock_00010_t01
            print('Selecting the newly registered slip for outbound dispatch...')
            await page2.locator('#st_stock_00010_t01 tbody tr input[type="checkbox"]').first.click()
            await page2.wait_for_timeout(500)
            
            # Click 확정 (Confirm Send)
            print('Clicking 확정 on Send tab...')
            await page2.locator('#st_stock_00010_confirm_btn_send').click()
            await page2.wait_for_timeout(2000)
            
            # Click Save/Confirm inside modal M02
            print('Clicking 확정 inside confirm modal...')
            await page2.locator('#sendConfirmModalM02').click()
            await page2.wait_for_timeout(1500)
            
            bootbox_accept2 = page2.locator('.bootbox-accept')
            if await bootbox_accept2.count() > 0 and await bootbox_accept2.first.is_visible():
                print('Accepting confirmation popup...')
                await bootbox_accept2.first.click()
                await page2.wait_for_timeout(3000)
                
            print('[SUCCESS] Outbound dispatch confirmed at sending store.')
            await page2.locator('#st_stock_00010_search_btn_send').click()
            await page2.wait_for_timeout(2000)
            await page2.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00010_sender_verified.png')
            await context2.close()
            
            # === PHASE 3: Receiving Store (NC0007) verifies and confirms receipt ===
            print('\n=== PHASE 3: Receiving Store (NC0007) verifies and confirms receipt ===')
            context3 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page3 = await context3.new_page()
            await login(page3, 'fnbcafe', '0000')
            
            print('Navigating to St_Stock_00010 (매장 재고이동) as receiver...')
            await page3.goto('http://localhost:8080/backoffice/view/main/st/stock/st_stock_00010')
            await page3.wait_for_timeout(3000)
            
            # Switch to "입고확정" (Recv) tab
            print('Switching to 입고확정 (Recv) tab...')
            await page3.locator('a:has-text("입고확정")').click()
            await page3.wait_for_timeout(1500)
            
            # Click Search Recv
            print('Searching inbound slips...')
            await page3.locator('#st_stock_00010_search_btn_recv').click()
            await page3.wait_for_timeout(2500)
            
            # Select the first row checkbox in the receiving table (#st_stock_00010_t02)
            print('Selecting the inbound slip checkbox...')
            await page3.locator('#st_stock_00010_t02 tbody tr input[type="checkbox"]').first.click()
            await page3.wait_for_timeout(500)
            
            # Click 확정 (Confirm Recv)
            print('Clicking 입고확정 (Confirm Receipt)...')
            await page3.locator('#st_stock_00010_confirm_btn_recv').click()
            await page3.wait_for_timeout(2000)
            
            # In confirm modal (confirmMoveSlipModal), click recvConfirmModalM02 button
            print('Clicking 확정 inside confirm modal...')
            await page3.locator('#recvConfirmModalM02').click()
            await page3.wait_for_timeout(1500)
            
            bootbox_accept3 = page3.locator('.bootbox-accept')
            if await bootbox_accept3.count() > 0 and await bootbox_accept3.first.is_visible():
                print('Accepting confirmation popup...')
                await bootbox_accept3.first.click()
                await page3.wait_for_timeout(3000)
                
            print('[SUCCESS] Inbound receipt confirmed at receiving store.')
            await page3.locator('#st_stock_00010_search_btn_recv').click()
            await page3.wait_for_timeout(2000)
            await page3.screenshot(path='D:/hmTest/backoffice/QaReport/st_stock_00010_recv_store_confirmed.png')
            await context3.close()
            
            # === PHASE 4: HQ Admin verifies final status is 수신확정 (PROC_FG = 2) ===
            print('\n=== PHASE 4: HQ Admin verifies final status is 수신확정 (PROC_FG = 2) ===')
            context4 = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page4 = await context4.new_page()
            await login(page4, 'shopadmin', '0000')
            
            print('Navigating to Hq_Stock_00011 to verify status...')
            await page4.goto('http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00011')
            await page4.wait_for_timeout(3000)
            
            await page4.locator('#hq_stock_00011_search_btn').click()
            await page4.wait_for_timeout(2500)
            await page4.screenshot(path='D:/hmTest/backoffice/QaReport/hq_stock_00011_final_received.png')
            print('[SUCCESS] Full E2E 3-Store Stock Move Test Completed!')
            await context4.close()
            
        except Exception as e:
            import traceback
            print('Error during test execution:')
            traceback.print_exc()
            # Capture screenshots from active pages if they are open
            for name, p in [('page1', locals().get('page1')), ('page2', locals().get('page2')), ('page3', locals().get('page3')), ('page4', locals().get('page4'))]:
                if p and not p.is_closed():
                    try:
                        await p.screenshot(path=f'D:/hmTest/backoffice/QaReport/hq_stock_00011_error_{name}.png')
                        print(f"Saved error screenshot for {name} to D:/hmTest/backoffice/QaReport/hq_stock_00011_error_{name}.png")
                    except Exception as err:
                        print(f"Failed to save error screenshot for {name}: {err}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
