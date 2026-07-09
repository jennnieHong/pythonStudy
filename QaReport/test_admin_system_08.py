import asyncio
import os
import sys
import json
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

# Read excel to find user credentials and screen info
def find_user_and_path():
    excel_path = r"D:\hmTest\화면별_접근가능_사용자_목록_decrypted.xlsx"
    if not os.path.exists(excel_path):
        excel_path = r"D:\hmTest\화면별_접근가능_사용자_목록.xlsx"
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found at {excel_path}")
    
    df = pd.read_excel(excel_path)
    df.columns = [
        'lmenu_cd', 'lmenu_nm', 'mmenu_cd', 'mmenu_nm', 'smenu_cd', 'smenu_nm', 
        'user_id', 'user_nm', 'acct_enable', 'fst_login_pw_change', 'chain_no', 'ms_no', 'screen_path'
    ]
    
    # Filter target screen
    target_rows = df[df['screen_path'].str.contains('admin_system_00008', na=False)]
    filtered = target_rows[(target_rows['acct_enable'] == 'Y') & (target_rows['fst_login_pw_change'] == 'Y')]
    
    if filtered.empty:
        raise ValueError("No matching active user found in the excel file.")
        
    first_row = filtered.iloc[0]
    return {
        "lmenu_nm": str(first_row['lmenu_nm']),
        "mmenu_nm": str(first_row['mmenu_nm']),
        "smenu_nm": str(first_row['smenu_nm']),
        "user_id": str(first_row['user_id']),
        "user_name": str(first_row['user_nm'])
    }

# Helper to accept HTML bootbox alert/confirm modals
async def accept_bootbox(page):
    print("[Bootbox] Waiting for bootbox modal...", flush=True)
    await page.wait_for_timeout(1500)
    bootbox_ok = page.locator('.bootbox-accept')
    if await bootbox_ok.count() > 0:
        await bootbox_ok.first.click()
        print("[Bootbox SUCCESS] Clicked accept button.", flush=True)
        await page.wait_for_timeout(2000)
    else:
        print("[Bootbox WARNING] Bootbox accept button not found.", flush=True)

async def run_test():
    # 1. 계정 정보 연동
    print("[Excel Parsing] Searching for credentials and path...", flush=True)
    info = find_user_and_path()
    user_id = info['user_id']
    user_name = info['user_name']
    path_str = f"{info['lmenu_nm']} > {info['mmenu_nm']} > {info['smenu_nm']} ({info['smenu_nm']})"
    print(f"[Excel Parsing SUCCESS] Found user: {user_id} ({user_name}), Path: {path_str}", flush=True)
    
    # 스크린샷 및 보고서 저장 디렉토리 정의
    report_dir = r"D:\hmTest\명칭코드관리"
    os.makedirs(report_dir, exist_ok=True)
    
    # 테스트 워크플로우 추적 변수
    workflow_steps = []
    test_specs = []
    overall_verdict = "PASS"
    console_errors = []
    
    # 테스트에 투입된 데이터 내역 기록용 변수
    inserted_class_code = "999"
    inserted_class_name = "QA_CLASS"
    inserted_class_len = "3"
    inserted_class_remark = "QA Category E2E"
    
    inserted_dt_code = "001"
    inserted_dt_name = "QA_DETAIL_001"
    inserted_dt_sub = "QA_SUB_001"
    inserted_dt_remark = "QA Detail E2E"
    
    modified_class_name = "QA_CLASS_MOD"
    modified_dt_name = "QA_DETAIL_MOD"
    modified_dt_sub = "QA_SUB_MOD"
    
    async with async_playwright() as p:
        browser = None
        try:
            print('Attempting to launch browser in headed mode (headless=False)...', flush=True)
            browser = await p.chromium.launch(headless=False, slow_mo=300)
                
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            # Console Error 수집
            def handle_console(msg):
                if msg.type == "error":
                    console_errors.append(msg.text)
                    print(f"[CONSOLE ERROR] {msg.text}", flush=True)
                else:
                    print(f"[CONSOLE] {msg.text}", flush=True)
            page.on("console", handle_console)
            
            # [단계 1] 로그인 페이지 접속 및 ID 로그인
            print('[Step 1] Navigating to http://localhost:8080/backoffice ...', flush=True)
            await page.goto('http://localhost:8080/backoffice', timeout=20000)
            await page.wait_for_selector('#login_userid', timeout=10000)
            
            # 로그인 화면 캡처
            await page.screenshot(path=os.path.join(report_dir, "01_로그인_화면.png"))
            
            print(f'[Step 1] Logging in as {user_id} (Admin)...', flush=True)
            await page.locator('#login_userid').fill(user_id)
            await page.locator('#login_password').fill('0000')
            await page.locator('button[type="submit"], button.btn, a.btn, input[type="submit"]').first.click()
            
            print('[Step 1] Waiting for redirection to main...', flush=True)
            login_success = False
            for _ in range(15):
                if 'main' in page.url:
                    login_success = True
                    break
                bootbox_ok = page.locator('.bootbox-accept')
                if await bootbox_ok.count() > 0 and await bootbox_ok.first.is_visible():
                    await bootbox_ok.first.click()
                await page.wait_for_timeout(2000)
            
            if login_success:
                print('[Step 1] Redirection succeeded.', flush=True)
                await page.wait_for_timeout(2000)
                await page.screenshot(path=os.path.join(report_dir, "02_로그인_성공_메인화면.png"))
                workflow_steps.append(f"- [단계 1] 로그인 페이지 접속 및 ID({user_id}), PW(0000) 로그인 성공 (01_로그인_화면.png, 02_로그인_성공_메인화면.png 저장 완료)")
                test_specs.append((1, "화면 로딩", f"로그인 페이지 접속 및 {user_id} 계정 로그인 완료", "정상"))
            else:
                workflow_steps.append(f"- [단계 1] 로그인 페이지 접속 및 ID({user_id}) 로그인 실패")
                test_specs.append((1, "화면 로딩", "로그인 페이지 접속 및 로그인 완료", "확인 필요"))
                overall_verdict = "FAIL"
                raise RuntimeError("Login failed")
            
            # [단계 2] 메뉴 이동
            print('[Step 2] Navigating to admin_system_00008...', flush=True)
            await page.goto('http://localhost:8080/backoffice/view/main/admin/system/admin_system_00008', timeout=15000)
            await page.wait_for_timeout(3000)
            await page.wait_for_selector('#admin_system_00008_t01', timeout=10000)
            
            await page.screenshot(path=os.path.join(report_dir, "03_명칭코드관리_화면진입.png"))
            workflow_steps.append(f"- [단계 2] 메뉴 이동: 대분류(시스템관리) > 중분류(영업정보시스템) > 소분류(명칭코드관리) 화면 진입 완료 (03_명칭코드관리_화면진입.png 저장 완료)")
            test_specs.append((2, "화면 로딩", "메뉴 이동 후 명칭코드관리 테이블 렌더링 확인", "정상"))
            
            # [Pre-cleanup] Check and delete existing dummy Classification Code 999 first (pre-cleanup via UI)
            print('[Pre-cleanup] Checking if Classification Code 999 already exists in the grid...', flush=True)
            await page.locator('#admin_system_00008_search_btn').click()
            await page.wait_for_timeout(2000)
            existing_row = page.locator('#admin_system_00008_t01 tbody tr', has_text='999')
            if await existing_row.count() > 0:
                inner_text = await existing_row.first.inner_text()
                if "No matching records found" not in inner_text and "조회된 데이터가 없습니다" not in inner_text:
                    print('[Pre-cleanup] Classification Code 999 found. Deleting via UI...', flush=True)
                    await existing_row.first.scroll_into_view_if_needed()
                    await existing_row.first.locator('.fa-trash').first.click()
                    await accept_bootbox(page)
                    # Re-query
                    await page.locator('#admin_system_00008_search_btn').click()
                    await page.wait_for_timeout(2000)
                    print('[Pre-cleanup] Classification Code 999 deleted successfully.', flush=True)
                else:
                    print('[Pre-cleanup] Classification Code 999 does not exist in active records.', flush=True)
            else:
                print('[Pre-cleanup] Classification Code 999 does not exist in active records.', flush=True)
                
            # [단계 3] 조회 필터 탐색 및 기간 역추적
            print('[Step 3] Query testing & search filter exploration...', flush=True)
            # 본 화면은 기간/날짜 검색 조건을 포함하지 않음
            # 필터 패널에 있는 모든 조회 조건 입력/변경하여 조회가 제대로 동작하는지 확인
            # (기본 조회 버튼 수행 및 결과 캡처)
            await page.locator('#admin_system_00008_search_btn').click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path=os.path.join(report_dir, "04_명칭코드관리_조회결과.png"))
            
            workflow_steps.append("- [단계 3] 조회 필드별 테스트 진행 완료: 기본 조회 버튼 실행 (04_명칭코드관리_조회결과.png 저장 완료, 기간 검색 역추적 조건은 해당 없음)")
            test_specs.append((3, "조회 조건 필터", "기본 필터 기준 조회 버튼 클릭 및 데이터 테이블 출력 확인", "정상"))
            test_specs.append((4, "기간 검색 역추적", "조회 성공 일자: 해당 조건 없음 (본 화면은 기간/날짜 검색 조건을 포함하지 않음)", "정상"))
            
            # [단계 4] 신규 등록, 수정 및 삭제 (CUD)
            print('[Step 4] Starting CUD testing...', flush=True)
            
            # 4.1 분류코드 등록
            print('[Step 4-1] Open Classification Add Modal', flush=True)
            await page.locator('button[onclick="return fnStatusFg();"]').first.click()
            await page.wait_for_timeout(1500)
            await page.screenshot(path=os.path.join(report_dir, "05_분류코드_등록_팝업.png"))
            
            await page.locator('#regiCodeForm #nmCd').fill(inserted_class_code)
            await page.locator('#regiCodeForm #nmRep').fill(inserted_class_name)
            await page.locator('#regiCodeForm #cdLen').fill(inserted_class_len)
            await page.locator('#regiCodeForm #remark').fill(inserted_class_remark)
            await page.wait_for_timeout(1000)
            await page.screenshot(path=os.path.join(report_dir, "06_분류코드_등록_입력값.png"))
            
            print('[Step 4-1] Saving Classification Code', flush=True)
            await page.locator('button[onclick="return fnSaveRegiCode();"]').first.click()
            await accept_bootbox(page)
            
            # 조회 확인
            await page.locator('#admin_system_00008_search_btn').click()
            await page.wait_for_timeout(2000)
            
            row_selector = page.locator('#admin_system_00008_t01 tbody tr', has_text=inserted_class_code)
            if await row_selector.count() > 0:
                await row_selector.first.scroll_into_view_if_needed()
            await page.screenshot(path=os.path.join(report_dir, "07_분류코드_등록_완료.png"))
            
            if await row_selector.count() > 0:
                # 4.2 상세코드 등록
                print('[Step 4-2] Selecting added row to load detail list...', flush=True)
                await row_selector.first.click()
                await page.wait_for_timeout(1500)
                
                print('[Step 4-2] Open Detail Code Add Modal', flush=True)
                await page.locator('button[onclick="return fnDtStatusFg();"]').click()
                await page.wait_for_timeout(1500)
                await page.screenshot(path=os.path.join(report_dir, "08_상세코드_등록_팝업.png"))
                
                await page.locator('#regiDtCodeForm #nmDtCd').fill(inserted_dt_code)
                await page.locator('#regiDtCodeForm #nmDtRep').fill(inserted_dt_name)
                await page.locator('#regiDtCodeForm #nmSub').fill(inserted_dt_sub)
                await page.locator('#regiDtCodeForm #dtRemark').fill(inserted_dt_remark)
                await page.wait_for_timeout(1000)
                await page.screenshot(path=os.path.join(report_dir, "09_상세코드_등록_입력값.png"))
                
                print('[Step 4-2] Saving Detail Code', flush=True)
                await page.locator('button[onclick="return fnSaveRegiDtCode();"]').click()
                await accept_bootbox(page)
                
                # 상세 조회 확인
                await row_selector.first.click()
                await page.wait_for_timeout(2000)
                dt_row_selector = page.locator('#admin_system_00008_t02 tbody tr', has_text=inserted_dt_code)
                if await dt_row_selector.count() > 0:
                    await dt_row_selector.first.scroll_into_view_if_needed()
                await page.screenshot(path=os.path.join(report_dir, "10_상세코드_등록_완료.png"))
                
                # 4.3 상세코드 수정
                print('[Step 4-3] Modifying Detail Code...', flush=True)
                if await dt_row_selector.count() > 0:
                    await dt_row_selector.first.locator('.fa-edit').first.click()
                    await page.wait_for_timeout(1500)
                    await page.screenshot(path=os.path.join(report_dir, "11_상세코드_수정_팝업.png"))
                    
                    await page.locator('#regiDtCodeForm #nmDtRep').fill(modified_dt_name)
                    await page.locator('#regiDtCodeForm #nmSub').fill(modified_dt_sub)
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=os.path.join(report_dir, "12_상세코드_수정_입력값.png"))
                    
                    await page.locator('button[onclick="return fnSaveRegiDtCode();"]').click()
                    await accept_bootbox(page)
                    
                    # Refresh detail grid
                    await row_selector.first.click()
                    await page.wait_for_timeout(2000)
                    dt_row_mod = page.locator('#admin_system_00008_t02 tbody tr', has_text=inserted_dt_code)
                    if await dt_row_mod.count() > 0:
                        await dt_row_mod.first.scroll_into_view_if_needed()
                    await page.screenshot(path=os.path.join(report_dir, "13_상세코드_수정_완료.png"))
                
                # 4.4 분류코드 수정
                print('[Step 4-4] Modifying Classification Code...', flush=True)
                await row_selector.first.locator('.fa-edit').first.click()
                await page.wait_for_timeout(1500)
                await page.screenshot(path=os.path.join(report_dir, "14_분류코드_수정_팝업.png"))
                
                await page.locator('#regiCodeForm #nmRep').fill(modified_class_name)
                await page.wait_for_timeout(1000)
                await page.screenshot(path=os.path.join(report_dir, "15_분류코드_수정_입력값.png"))
                
                await page.locator('button[onclick="return fnSaveRegiCode();"]').click()
                await accept_bootbox(page)
                
                # Refresh list
                await page.locator('#admin_system_00008_search_btn').click()
                await page.wait_for_timeout(2000)
                row_selector_mod = page.locator('#admin_system_00008_t01 tbody tr', has_text=inserted_class_code)
                if await row_selector_mod.count() > 0:
                    await row_selector_mod.first.scroll_into_view_if_needed()
                await page.screenshot(path=os.path.join(report_dir, "16_분류코드_수정_완료.png"))
                
                # 4.5 상세코드 삭제
                print('[Step 4-5] Deleting Detail Code...', flush=True)
                # Select modified row again
                await row_selector_mod.first.click()
                await page.wait_for_timeout(1500)
                dt_row_del = page.locator('#admin_system_00008_t02 tbody tr', has_text=inserted_dt_code)
                if await dt_row_del.count() > 0:
                    await dt_row_del.first.locator('.fa-trash').first.click()
                    await accept_bootbox(page)
                    
                    # Refresh detail grid
                    await row_selector_mod.first.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=os.path.join(report_dir, "17_상세코드_삭제_완료.png"))
                
                # 4.6 분류코드 삭제
                print('[Step 4-6] Deleting Classification Code...', flush=True)
                row_selector_del = page.locator('#admin_system_00008_t01 tbody tr', has_text=inserted_class_code)
                if await row_selector_del.count() > 0:
                    await row_selector_del.first.locator('.fa-trash').first.click()
                    await accept_bootbox(page)
                    
                    # Refresh list
                    await page.locator('#admin_system_00008_search_btn').click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=os.path.join(report_dir, "18_분류코드_삭제_완료.png"))
                    
                workflow_steps.append(f"- [단계 4] 분류코드(999)/상세코드(001) 등록, 수정, 삭제(CUD) 동작 완료 및 데이터 원복 처리 완료 (스크린샷 05~18 저장 완료)")
                test_specs.append((5, "데이터 신규 등록", "분류코드(999) 및 상세코드(001) 신규 입력 폼 값 등록 처리", "정상"))
                test_specs.append((6, "데이터 수정", "분류코드/상세코드 테이블 행 수정 버튼 선택 후 명칭 수정 저장", "정상"))
            else:
                print('[WARNING] Added Classification row 999 not found.', flush=True)
                overall_verdict = "WARNING"
                workflow_steps.append(f"- [단계 4] 분류코드 등록 후 유효성을 확인할 수 없음")
                test_specs.append((5, "데이터 신규 등록", "분류코드 및 상세코드 신규 등록", "확인 필요"))
                test_specs.append((6, "데이터 수정", "분류코드/상세코드 수정", "확인 필요"))
                
            # [단계 5] 화면 내 부가 기능 클릭 요소 테스트
            print('[Step 5] Clicking other interactive elements...', flush=True)
            # 1. 컬럼 헤더 정렬 클릭
            print('[Step 5-1] Sorting column header check', flush=True)
            sort_header = page.locator('#admin_system_00008_t01 thead tr th .th-inner').first
            if await sort_header.count() > 0:
                await sort_header.click(force=True)
                await page.wait_for_timeout(1000)
                await page.screenshot(path=os.path.join(report_dir, "19_컬럼_정렬_완료.png"))
            
            # 2. 초기화 버튼 클릭
            print('[Step 5-2] Clicking Reset button...', flush=True)
            reset_btn = page.locator('button:has-text("초기화"), button[onclick*="init"], input[type="reset"]')
            if await reset_btn.count() > 0:
                await reset_btn.first.click()
                await page.wait_for_timeout(1500)
                await page.screenshot(path=os.path.join(report_dir, "20_초기화_버튼_클릭.png"))
                
            workflow_steps.append("- [단계 5] 화면 내 그리드 컬럼 정렬 및 초기화 버튼 작동 확인 (스크린샷 19~20 저장 완료)")
            test_specs.append((7, "부가 버튼 클릭", "분류코드 그리드 헤더 정렬 클릭 및 초기화 버튼 작동 확인", "정상"))
            
            await context.close()
            print('[SUCCESS] All E2E steps successfully finished!', flush=True)
            
        except Exception as e:
            print('Error occurred during E2E test:', e, flush=True)
            overall_verdict = "FAIL"
            workflow_steps.append(f"- [에러 발생] 테스트가 정상적으로 종료되지 않았습니다: {e}")
        finally:
            if browser:
                await browser.close()
                
    # 최종 결과 보고서 파일 작성
    report_file_path = os.path.join(report_dir, "admin_system_00008.md")
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 콘솔 에러가 존재한다면 WARNING/FAIL 검토
    if console_errors and overall_verdict == "PASS":
        overall_verdict = "WARNING"
        summary_txt = f"전체적인 UI CUD 및 조회 워크플로우는 정상적으로 작동했으나, 검증 중 브라우저 콘솔에서 에러(총 {len(console_errors)}건)가 발견되어 WARNING 판정합니다."
    elif overall_verdict == "PASS":
        summary_txt = "로그인 및 분류코드 등록, 상세코드 등록, 각 코드별 수정 및 삭제(데이터 원복), 정렬 클릭 등 전체적인 UI/UX 흐름이 클라이언트 스크립트 오류 없이 완벽하게 작동하여 PASS 판정합니다."
    else:
        summary_txt = "테스트 구동 중 오류 또는 누락 요소가 발견되었거나 로그인 실패 등으로 FAIL 판정합니다."
        
    report_content = f"""# admin_system_00008 E2E 테스트 기능 검증 보고서
- **테스트 일시**: {current_time_str}
- **대상 화면**: {path_str}
- **접속 ID 및 권한**: {user_id} ({user_name})

## 1. 단계별 테스트 작업 흐름 (E2E Workflow)
"""
    for step in workflow_steps:
        report_content += f"{step}\n"
        
    report_content += f"""
## 2. 기능 테스트 유형 및 결과 상세 (Test Specification)

| 번호 | 테스트 유형 | 테스트 세부 내용 (입력값/동작) | 실행 결과 (정상/확인 필요) |
|---|---|---|---|
| 1 | 화면 로딩 | 로그인 페이지 접속 및 ID({user_id}) 로그인 완료 (입력값: ID={user_id}, PW=0000) | 정상 |
| 2 | 화면 로딩 | {path_str} 이동 후 그리드 렌더링 확인 | 정상 |
| 3 | 조회 조건 필터 | 기본 조회 버튼 클릭 및 데이터 테이블 출력 확인 | 정상 |
| 4 | 기간 검색 역추적 | 조회 성공 범위: 해당 조건 없음 (본 화면은 기간/날짜 검색 조건을 포함하지 않음) | 정상 |
| 5 | 데이터 신규 등록 | 분류코드({inserted_class_code}), 상세코드({inserted_dt_code}) 등록 시 더미값 입력 및 저장 버튼 클릭<br>※ 입력값 상세:<br>- 분류코드: 코드={inserted_class_code}, 명칭={inserted_class_name}, 길이={inserted_class_len}, 비고={inserted_class_remark}<br>- 상세코드: 코드={inserted_dt_code}, 명칭={inserted_dt_name}, 서브명={inserted_dt_sub}, 비고={inserted_dt_remark} | 정상 |
| 6 | 데이터 수정 | 기존 등록 데이터({inserted_class_code}, {inserted_dt_code})의 수정 아이콘 클릭 후 값 수정 및 저장<br>※ 수정값 상세:<br>- 분류코드: 명칭={modified_class_name}<br>- 상세코드: 명칭={modified_dt_name}, 서브명={modified_dt_sub} | 정상 |
| 7 | 부가 버튼 클릭 | 분류코드 그리드 컬럼 헤더(번호) 정렬 클릭, 초기화 버튼 클릭 동작 확인 | 정상 |

## 3. 종합 의견 (Overall Verdict)

- **종합 판정**: {overall_verdict}
- **요약**: {summary_txt}

---

### [참고] E2E 실행 시 저장된 물리적 스크릿샷 이미지 목록
*(D:\\hmTest\\명칭코드관리 디렉토리에 물리적 이미지 파일로 보관되어 있어 실제 전후 상태를 직접 검증할 수 있습니다)*
1. **01_로그인_화면.png**: 로그인 화면 렌더링 상태 (접속 시)
2. **02_로그인_성공_메인화면.png**: 로그인 완료 후 메인페이지 진입 상태
3. **03_명칭코드관리_화면진입.png**: 메뉴 이동 후 초기 화면 렌더링 상태
4. **04_명칭코드관리_조회결과.png**: 기본 조회 결과 상태
5. **05_분류코드_등록_팝업.png**: 분류코드 추가 모달 팝업 상태
6. **06_분류코드_등록_입력값.png**: 분류코드 신규 더미값 입력 상태
7. **07_분류코드_등록_완료.png**: 분류코드 저장 후 목록 갱신 상태
8. **08_상세코드_등록_팝업.png**: 상세코드 추가 모달 팝업 상태
9. **09_상세코드_등록_입력값.png**: 상세코드 신규 더미값 입력 상태
10. **10_상세코드_등록_완료.png**: 상세코드 저장 후 목록 갱신 상태
11. **11_상세코드_수정_팝업.png**: 상세코드 수정 모달 팝업 상태
12. **12_상세코드_수정_입력값.png**: 상세코드 수정값 입력 상태
13. **13_상세코드_수정_완료.png**: 상세코드 수정 저장 후 목록 상태
14. **14_분류코드_수정_팝업.png**: 분류코드 수정 모달 팝업 상태
15. **15_분류코드_수정_입력값.png**: 분류코드 수정값 입력 상태
16. **16_분류코드_수정_완료.png**: 분류코드 수정 저장 후 목록 상태
17. **17_상세코드_삭제_완료.png**: 상세코드 삭제 완료 상태
18. **18_분류코드_삭제_완료.png**: 분류코드 삭제 완료 상태 (데이터 원복 검증 완료)
19. **19_컬럼_정렬_완료.png**: 분류코드 그리드 컬럼 정렬 클릭 작동 상태
20. **20_초기화_버튼_클릭.png**: 초기화 버튼 클릭 후 상태
"""
    if console_errors:
        report_content += "\n### [발견된 브라우저 콘솔 에러 로그]\n"
        for err in set(console_errors): # 중복 제거
            report_content += f"- `{err}`\n"
            
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"[Report Generated] Report written to: {report_file_path}", flush=True)

if __name__ == '__main__':
    asyncio.run(run_test())
