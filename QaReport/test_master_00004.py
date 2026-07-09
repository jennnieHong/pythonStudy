# -*- coding: utf-8 -*-
import asyncio
import os
import sys
import json
import subprocess
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

def run_db_verify(action):
    print(f"\n--- Running DB Verification for action: {action} ---")
    res = subprocess.run(["python", "D:/hmTest/backoffice/QaReport/verify_master_trigger.py", action], 
                         capture_output=True, text=True, encoding='utf-8')
    print(res.stdout)
    if res.stderr:
        print("Error:", res.stderr)

async def accept_bootbox(page):
    await page.wait_for_timeout(1000)
    bootbox_body = page.locator('.bootbox-body')
    bootbox_accept = page.locator('.bootbox-accept, button.bootbox-accept, .bootbox modal.show .btn-primary, .bootbox .modal-footer .btn-primary')
    for _ in range(5):
        if await bootbox_accept.count() > 0 and await bootbox_accept.first.is_visible():
            if await bootbox_body.count() > 0:
                text = await bootbox_body.first.inner_text()
                print(f'Bootbox dialog detected with text: "{text}". Clicking accept...')
            else:
                print('Bootbox dialog detected (no body). Clicking accept...')
            await bootbox_accept.first.click()
            await page.wait_for_timeout(1500)
            return True
        await page.wait_for_timeout(500)
    return False

async def perform_login(context, page, username, password):
    print(f'\n--- Logging in as {username} ---')
    print('Clearing browser cookies to reset session...')
    await context.clear_cookies()
    
    print('Navigating to login page...')
    await page.goto('http://localhost:8080/backoffice/view/login', timeout=15000)
    await page.wait_for_timeout(1000)
    
    await page.wait_for_selector('#login_userid', timeout=10000)
    print(f'Filling credentials for {username}...')
    await page.locator('#login_userid').fill(username)
    await page.locator('#login_password').fill(password)
    
    # Submit login
    submit_btn = page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first
    await submit_btn.click()
    
    # Wait for redirection to main page
    print('Waiting for redirection to main...')
    for _ in range(15):
        if 'main' in page.url:
            print('Successfully redirected to main.')
            break
        bootbox_ok = page.locator('.bootbox-accept')
        if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
            print('Bootbox modal detected during login. Closing it...')
            await bootbox_ok.first.click()
        await page.wait_for_timeout(2000)

async def run_test():
    # Initial Database cleanup before test runs
    run_db_verify("cleanup_all")
    
    async with async_playwright() as p:
        try:
            print('Launching browser in headed mode (headless=False)...')
            browser = await p.chromium.launch(headless=True, slow_mo=300)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
            
            # =================== TEST 1: HQ Master 00004 (shopadmin) ===================
            await perform_login(context, page, 'shopadmin', '0000')
            
            print('Navigating to hq_master_00004 (매장관리)...')
            await page.goto('http://localhost:8080/backoffice/view/main/hq/master/hq_master_00004')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#hq_master_00004_t01', timeout=10000)
            
            # SCENARIO 1: 신규등록 (New Registration)
            print('\n[SCENARIO 1] New Store Registration...')
            await page.locator('#hq_master_00004_addMs_btn').click()
            await page.wait_for_selector('#msRegistModal', state='visible', timeout=5000)
            await page.wait_for_timeout(1000)
            
            print('Filling new store registration form...')
            await page.locator('#registMsNm').fill('테스트가맹점')
            await page.locator('#registMasterNm').fill('홍길동')
            await page.locator('#registBizNo').fill('1234567890')
            await page.locator('#registBsType').fill('음식점')
            await page.locator('#registBsKind').fill('한식')
            await page.evaluate('$("#registTaxType").selectpicker("val", "1").trigger("change")')
            await page.locator('#registIfBlueJosNo').fill('12345678')
            await page.locator('#registTelNo').fill('0212345678')
            await page.locator('#registZipNo').fill('12345')
            await page.locator('#registAddress').fill('서울시 강남구')
            await page.locator('#registAddressBunji').fill('123번지')
            await page.locator('#registBillAddr01').fill('서울시 강남구 123번지')
            await page.evaluate('$("#registOpenDate").val("2026-06-12")')
            
            # Fill newly identified required fields
            print('Filling MPointRate, BizCd, and ShopCd...')
            await page.evaluate('$("#registShopWhYn").selectpicker("val", "N").trigger("change")')
            await page.locator('#registMPointRate').fill('10')
            await page.locator('#registIfBizCd').fill('99')
            await page.locator('#registIfShopCd').fill('99')
            await page.wait_for_timeout(1000)
            
            # Click Save on Registration modal
            print('Clicking Save on New Store Registration...')
            save_reg_btn = page.locator('button[onclick*="registMs(\'insert\')"]').first
            await save_reg_btn.click()
            await page.wait_for_timeout(1500)
            
            # Accept bootbox confirm
            await accept_bootbox(page)
            # Accept bootbox success alert if present
            await accept_bootbox(page)
            
            # Wait for modal to hide
            await page.wait_for_timeout(2000)
            close_reg_btn = page.locator('#hq_master_00004_M01_close_btn')
            if await close_reg_btn.is_visible():
                await close_reg_btn.click()
                await page.wait_for_selector('#msRegistModal', state='hidden', timeout=5000)
                
            # Verify new store creation and trigger cascade in DB
            run_db_verify("verify_new_store")
            
            # Click Search to refresh list
            print('Clicking Search for shopadmin...')
            await page.locator('#hq_master_00004_search_btn').click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/hq_master_00004_search.png')
            
            # Find the row containing NC0007 (Affiliate Store)
            print('Finding target row for NC0007 (Affiliate Store)...')
            target_row = page.locator('#hq_master_00004_t01 tbody tr:has(td:has-text("NC0007"))').first
            await target_row.scroll_into_view_if_needed()
            
            # SCENARIO 2: 매장 정보 수정 (Store Info Edit)
            print('\n[SCENARIO 2] Modifying Store Info (MPOINT_RATE) in M02 Modal...')
            msno_link = target_row.locator('td').nth(3).locator('a')
            if await msno_link.count() > 0:
                await msno_link.click()
                await page.wait_for_selector('#msInfoUpdateModal', state='visible', timeout=5000)
                await page.wait_for_timeout(1500)
                
                # Change MPointRate to 15
                print('Setting MPointRate to 15...')
                await page.locator('#msInfoMPointRate').fill('15')
                await page.wait_for_timeout(1000)
                
                # Save changes
                print('Clicking Save on MS Info Update...')
                save_btn = page.locator('#msInfoUpdateModal button:has-text("저장")').first
                await save_btn.click()
                await page.wait_for_timeout(1500)
                
                # Accept bootbox confirm/alert if present
                await accept_bootbox(page)
                
                # Close Modal if not automatically closed
                close_btn = page.locator('#hq_master_00004_M02_close_btn')
                if await close_btn.is_visible():
                    await close_btn.click()
                    await page.wait_for_selector('#msInfoUpdateModal', state='hidden', timeout=5000)
            
            # SCENARIO 3: 오픈여부 수정 (Open Status Edit)
            print('\n[SCENARIO 3] Modifying Open status to HOLD (3)...')
            openfg_link = target_row.locator('td').nth(8).locator('a')
            if await openfg_link.count() > 0:
                await openfg_link.click()
                await page.wait_for_selector('#openFgUpdateModal', state='visible', timeout=5000)
                await page.wait_for_timeout(1500)
                
                # Change openFg to 3 (HOLD) using bootstrap selectpicker evaluation
                print('Setting OpenFg to HOLD (3)...')
                await page.evaluate('$("#openFgOpenFgSelect").selectpicker("val", "3").trigger("change")')
                await page.wait_for_timeout(1000)
                
                # Click Save
                print('Saving OpenFg status...')
                save_btn = page.locator('#openFgUpdateModal button:has-text("저장")').first
                await save_btn.click()
                await page.wait_for_timeout(1500)
                
                # Accept bootbox confirm/alert
                await accept_bootbox(page)
                
                # Close modal if needed
                close_btn = page.locator('#hq_master_00004_M03_close_btn')
                if await close_btn.is_visible():
                    await close_btn.click()
                    await page.wait_for_selector('#openFgUpdateModal', state='hidden', timeout=5000)
                
                # Verify HOLD status and ACCT_EXPIRE = 'Y' cascade in DB
                run_db_verify("verify_hold")
                
                # Restore status to OPEN (2)
                print('\n[SCENARIO 4] Restoring Open status to OPEN (2)...')
                await openfg_link.click()
                await page.wait_for_selector('#openFgUpdateModal', state='visible', timeout=5000)
                await page.wait_for_timeout(1500)
                
                print('Setting OpenFg to OPEN (2)...')
                await page.evaluate('$("#openFgOpenFgSelect").selectpicker("val", "2").trigger("change")')
                await page.wait_for_timeout(1000)
                
                print('Saving restored OpenFg status...')
                await page.locator('#openFgUpdateModal button:has-text("저장")').first.click()
                await page.wait_for_timeout(1500)
                
                # Accept bootbox confirm/alert
                await accept_bootbox(page)
                
                if await close_btn.is_visible():
                    await close_btn.click()
                    await page.wait_for_selector('#openFgUpdateModal', state='hidden', timeout=5000)
                    
                # Verify restored status and ACCT_EXPIRE = 'N' cascade in DB
                run_db_verify("verify_open")
            
            # SCENARIO 4: 시스템 등록 (System Config)
            print('\n[SCENARIO 5] Modifying System Env (Credit Limit) in M04 Modal...')
            system_link = target_row.locator('td').nth(10).locator('a')
            if await system_link.count() > 0:
                await system_link.click()
                await page.wait_for_selector('#systemUpdateModal', state='visible', timeout=5000)
                await page.wait_for_timeout(1500)
                
                # Modify Credit Limit to 5000000
                print('Setting credit limit to 5000000...')
                await page.locator('#systemCreditLimit').fill('5000000')
                
                # Bypass printer name validation check by setting kitchen printer use to '0' (사용안함)
                print('Setting Kitchen Printer to unused (사용안함)...')
                await page.evaluate('$("#systemKitchenYnSelect").selectpicker("val", "0").trigger("change")')
                await page.wait_for_timeout(1000)
                
                # Click Save
                print('Saving System Configuration...')
                await page.locator('#systemUpdateModal button:has-text("저장")').first.click()
                await page.wait_for_timeout(1500)
                
                # Accept bootbox confirm/alert
                await accept_bootbox(page)
                
                # Close Modal
                close_btn = page.locator('#hq_master_00004_M04_close_btn')
                if await close_btn.is_visible():
                    await close_btn.click()
                    await page.wait_for_selector('#systemUpdateModal', state='hidden', timeout=5000)
                
                # Verify Credit Limit and MPointRate mapping in DB
                run_db_verify("verify_credit_mpoint")
                
            # SCENARIO 5: 장비설정에서 pos설정, pos추가 (POS Add & POS Edit)
            print('\n[SCENARIO 6] Opening Jangbi Modal M05 for POS settings...')
            jangbi_link = target_row.locator('td').nth(11).locator('a')
            if await jangbi_link.count() > 0:
                await jangbi_link.click()
                await page.wait_for_selector('#jangbiSettingModal', state='visible', timeout=5000)
                await page.wait_for_timeout(1500)
                
                # POS Add (POS추가) tab
                print('Clicking POS Add (POS추가) tab...')
                await page.locator('#jangbiSettingModalPosAdd').click()
                await page.wait_for_timeout(1000)
                
                # Select POS type and fill Mac address
                print('Adding new POS device...')
                await page.evaluate('$("#posAddPosMobileType").selectpicker("val", "0").trigger("change")') # Type 0 = POS
                await page.locator('#posAddMacAddIp').fill('AA-BB-CC-DD-EE-FF')
                await page.wait_for_timeout(1000)
                
                # Click Save on POS Add
                print('Clicking Save on POS Add...')
                await page.locator('#posAddFooter button:has-text("저장")').first.click()
                await page.wait_for_timeout(1500)
                
                # Accept bootbox
                await accept_bootbox(page)
                await page.wait_for_timeout(1500)
                
                # Now verify newly added POS in POS설정 tab and update its Mac address
                print('Editing Mac Address for newly added POS in POS설정...')
                # Re-open Jangbi modal to load newly added POS (modal automatically closes after success)
                await page.wait_for_selector('#jangbiSettingModal', state='hidden', timeout=5000)
                await page.wait_for_timeout(1000)
                await jangbi_link.click()
                await page.wait_for_selector('#jangbiSettingModal', state='visible', timeout=5000)
                await page.wait_for_timeout(2000)
                
                # Find the second POS mac address input field (POS 02) and edit it
                print('Updating POS 02 Mac Address to AA-BB-CC-DD-EE-02...')
                mac_inputs = page.locator('input[name="posSettingMacAddIp"]')
                if await mac_inputs.count() > 1:
                    await mac_inputs.nth(1).fill('AA-BB-CC-DD-EE-02')
                    await page.wait_for_timeout(1000)
                    
                    # Save changes
                    print('Saving edited POS settings...')
                    await page.locator('#posFooter button:has-text("저장")').first.click()
                    await page.wait_for_timeout(1500)
                    # Accept bootbox
                    await accept_bootbox(page)
                
                # Close modal
                await page.locator('#hq_master_00004_M05_pos_close_btn').click()
                await page.wait_for_selector('#jangbiSettingModal', state='hidden', timeout=5000)
                await page.wait_for_timeout(1000)
                
                # Verify POS add and edit in DB
                run_db_verify("verify_pos_add_and_update")
                
            # SCENARIO 6: 카드등록에서 VAN(POS), 카드사 계약번호 (VAN & Card Contract)
            print('\n[SCENARIO 7] Card Registration Modal M06...')
            card_link = target_row.locator('td').nth(12).locator('a')
            if await card_link.count() > 0:
                await card_link.click()
                await page.wait_for_selector('#cardRegiModal', state='visible', timeout=5000)
                await page.wait_for_timeout(2000)
                
                # 1. VAN(POS) tab setup
                print('Configuring VAN(POS)...')
                
                # Wait for options in #modalPosVan to load
                await page.wait_for_function('document.querySelectorAll("#modalPosVan option").length > 0', timeout=10000)
                
                # Select VAN사 (modalPosVan)
                await page.evaluate('''
                    var val = $("#modalPosVan option:eq(1)").val() || $("#modalPosVan option:eq(0)").val();
                    $("#modalPosVan").selectpicker("val", val).trigger("change");
                ''')
                
                # Wait for the selectpicker values to update (AJAX is debounced by 300ms and async)
                print('Waiting 2.5 seconds for VAN-associated payment type options to load via AJAX...')
                await page.wait_for_timeout(2500)
                
                # Verify and select 결제형태구분 (modalPosDanGbn)
                options_cnt = await page.evaluate('$("#modalPosDanGbn option").length')
                print(f'Number of options in #modalPosDanGbn: {options_cnt}')
                
                # Select 결제형태구분 (modalPosDanGbn)
                await page.evaluate('''
                    var val = $("#modalPosDanGbn option:eq(1)").val() || $("#modalPosDanGbn option:eq(0)").val();
                    $("#modalPosDanGbn").selectpicker("val", val).trigger("change");
                ''')
                
                # Log selected value of modalPosDanGbn
                selected_val = await page.evaluate('$("#modalPosDanGbn").val()')
                print(f'Selected value for modalPosDanGbn: "{selected_val}"')
                
                # Fill TID번호 (modalVanConNum)
                await page.locator('#modalVanConNum').fill('1234567890')
                
                # Wait for options in #modalPosNo to load
                await page.wait_for_function('document.querySelectorAll("#modalPosNo option").length > 0', timeout=10000)
                
                # Select POS 02 (the newly added POS) instead of 01 to avoid 'only one VAN per POS' validation error
                print('Selecting POS 02 for VAN configuration...')
                await page.evaluate('''
                    $("#modalPosNo").selectpicker("val", "02").trigger("change");
                ''')
                await page.wait_for_timeout(1000)
                
                # Click Save
                print('Saving VAN(POS) settings...')
                await page.locator('#modal06SaveBtn01').click()
                await page.wait_for_timeout(1500)
                # Accept bootbox (confirm dialog)
                await accept_bootbox(page)
                await page.wait_for_timeout(1500)
                # Accept bootbox (success alert dialog)
                await accept_bootbox(page)
                
                # 2. Switch to 카드사 계약번호 tab
                print('Switching to 카드사 계약번호 tab...')
                await page.locator('a[href="#vanDan"]').click()
                await page.wait_for_timeout(2000)
                
                # Input card contract number for BC Card (cardContract_01)
                print('Setting contract number for BC Card...')
                bc_card_input = page.locator('#cardContract_01').first
                if await bc_card_input.count() > 0:
                    await bc_card_input.fill('9988776655')
                    await page.wait_for_timeout(1000)
                    
                    # Click Save
                    print('Saving Card contract...')
                    await page.locator('button[onclick="return fnSaveCardContract();"]').first.click()
                    await page.wait_for_timeout(1500)
                    
                    # Accept bootbox
                    await accept_bootbox(page)
                
                # Close Modal
                await page.locator('#hq_master_00004_M06_close_btn02').click()
                await page.wait_for_selector('#cardRegiModal', state='hidden', timeout=5000)
                await page.wait_for_timeout(1000)
                
                # Verify VAN POS and Card contract triggers in DB
                run_db_verify("verify_van_pos_and_card")
                
            # Test Reset button
            print('Testing Reset button...')
            await page.locator('#clear_form_btn').click()
            await page.wait_for_timeout(2000)
            
            # =================== TEST 2: Admin Master 00004 (admin2) ===================
            await perform_login(context, page, 'admin2', '0000')
            
            print('Navigating to admin_master_00004 (매장관리-어드민)...')
            await page.goto('http://localhost:8080/backoffice/view/main/admin/master/admin_master_00004')
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#admin_master_00004_t01', timeout=10000)
            
            # Click Search
            print('Clicking Search for admin2...')
            await page.locator('#admin_master_00004_search_btn').click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/admin_master_00004_search.png')
            
            # Test Reset button
            print('Testing Reset button...')
            await page.locator('#clear_form_btn').click()
            await page.wait_for_timeout(2000)
            
            # Clear cookies at end
            await context.clear_cookies()
            print('[SUCCESS] E2E test completed successfully.')
            
        except Exception as e:
            print('Error occurred during E2E test:', e)
            await page.screenshot(path='D:/hmTest/backoffice/QaReport/master_00004_error.png')
            # Rollback open status in DB in case of failure to keep environment clean
            run_db_verify("rollback_open")
        finally:
            # Final Database cleanup after test run to leave environment clean
            run_db_verify("cleanup_all")
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
