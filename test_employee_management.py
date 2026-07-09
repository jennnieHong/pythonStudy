import time
import os
import psycopg2
from playwright.sync_api import sync_playwright

DB_PARAMS = {
    "host": "192.168.10.206",
    "port": 5432,
    "database": "edb",
    "user": "hmsfns_was",
    "password": "astems3!"
}

SCREENSHOT_DIR = r"C:\Users\uoshj\.gemini\antigravity-ide\brain\1a4236fc-92c9-48e6-b3ea-a3f6617131ea"

def db_cleanup():
    """테스트용 계정 잔존 데이터 강제 삭제"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    test_ids = ['playadmin01', 'playhq001', 'playst001']
    try:
        print("[DB Cleanup] Starting cleanup for test accounts...")
        # 1. SSUSERTB 정리 (EMP_ID 기준)
        cursor.execute("SELECT EMP_ID FROM hmsfns.MUSERSTB WHERE USER_ID IN %s", (tuple(test_ids),))
        emp_ids = [r[0] for r in cursor.fetchall() if r[0]]
        if emp_ids:
            cursor.execute("DELETE FROM hmsfns.SSUSERTB WHERE EMP_ID IN %s", (tuple(emp_ids),))
            print(f"[DB Cleanup] Deleted SSUSERTB rows for EMP_IDs: {emp_ids}")
            
        # 2. USERMLTB & TB_USER_LAST_MENU 정리
        cursor.execute("DELETE FROM hmsfns.USERMLTB WHERE USER_ID IN %s", (tuple(test_ids),))
        cursor.execute("DELETE FROM hmsfns.TB_USER_LAST_MENU WHERE USER_ID IN %s", (tuple(test_ids),))
        
        # 3. MUSERSTB 정리
        cursor.execute("DELETE FROM hmsfns.MUSERSTB WHERE USER_ID IN %s", (tuple(test_ids),))
        
        # 4. MMSLOGTB 정리
        cursor.execute("DELETE FROM hmsfns.MMSLOGTB WHERE TABLE_NM = 'MUSERSTB' AND LOG_DATA LIKE '%play%'")
        
        conn.commit()
        print("[DB Cleanup] DB Cleanup completed successfully.")
    except Exception as e:
        conn.rollback()
        print(f"[DB Cleanup] Error during DB Cleanup: {e}")
    finally:
        cursor.close()
        conn.close()

def verify_db_insert(user_id):
    """MUSERSTB 등록 및 자바 트리거에 의한 SSUSERTB 적재 여부 확인 (Depth 2 검증)"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    try:
        # MUSERSTB 확인
        cursor.execute("SELECT EMP_ID, USER_NM FROM hmsfns.MUSERSTB WHERE USER_ID = %s", (user_id,))
        muser = cursor.fetchone()
        assert muser is not None, f"MUSERSTB에 USER_ID={user_id}가 존재하지 않습니다."
        emp_id = muser[0]
        print(f"[DB Verify] MUSERSTB insert verified for {user_id} (EMP_ID: {emp_id})")
        
        # SSUSERTB 확인
        cursor.execute("SELECT PROC_FG, PROC_DTIME FROM hmsfns.SSUSERTB WHERE MS_NO = 'NC0001' AND EMP_ID = %s ORDER BY PROC_DTIME DESC", (emp_id,))
        ssuser = cursor.fetchone()
        assert ssuser is not None, f"SSUSERTB (POS 연동)에 EMP_ID={emp_id} 데이터가 적재되지 않았습니다. (Java 트리거 미작동)"
        print(f"[DB Verify] SSUSERTB sync verified. PROC_FG: {ssuser[0]}, PROC_DTIME: {ssuser[1]}")
        return emp_id
    finally:
        cursor.close()
        conn.close()

def verify_db_update(user_id):
    """MUSERSTB 수정 및 MMSLOGTB 변경이력 적재 여부 확인 (Depth 2 검증)"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    try:
        # MMSLOGTB 확인
        cursor.execute("SELECT LOG_FG, LOG_DATA FROM hmsfns.MMSLOGTB WHERE TABLE_NM = 'MUSERSTB' AND LOG_FG = 'U' AND LOG_DATA LIKE %s", (f"%{user_id}%",))
        mmslog = cursor.fetchone()
        assert mmslog is not None, f"MMSLOGTB에 USER_ID={user_id}의 UPDATE 변경 로그가 적재되지 않았습니다."
        print(f"[DB Verify] MMSLOGTB Update log verified. LOG_DATA: {mmslog[1]}")
    finally:
        cursor.close()
        conn.close()

def verify_db_delete(emp_id):
    """MUSERSTB 삭제 및 SSUSERTB에 삭제('D') 플래그 전송 여부 확인"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    try:
        # MUSERSTB 확인
        cursor.execute("SELECT COUNT(*) FROM hmsfns.MUSERSTB WHERE EMP_ID = %s", (emp_id,))
        cnt = cursor.fetchone()[0]
        assert cnt == 0, f"MUSERSTB에 EMP_ID={emp_id}가 여전히 존재합니다. (삭제 실패)"
        print(f"[DB Verify] MUSERSTB delete verified for EMP_ID: {emp_id}")
        
        # SSUSERTB 확인
        cursor.execute("SELECT PROC_FG FROM hmsfns.SSUSERTB WHERE EMP_ID = %s ORDER BY PROC_DTIME DESC LIMIT 1", (emp_id,))
        ssuser = cursor.fetchone()
        assert ssuser is not None and ssuser[0] == 'D', f"SSUSERTB에 EMP_ID={emp_id}의 삭제 플래그('D') 데이터가 유실되었습니다."
        print("[DB Verify] SSUSERTB delete status 'D' sync verified.")
    finally:
        cursor.close()
        conn.close()

def dismiss_passwords_modal(page):
    """비밀번호 강제 변경 팝업 우회"""
    print("[UI] Force dismissing passwordsModal...")
    page.evaluate("""() => {
        try {
            if (typeof $ !== 'undefined') {
                $('#passwordsModal').modal('hide');
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
            } else {
                const m = document.getElementById('passwordsModal');
                if (m) m.style.display = 'none';
                const backdrops = document.getElementsByClassName('modal-backdrop');
                for (let b of backdrops) { b.remove(); }
                document.body.classList.remove('modal-open');
            }
        } catch(e) {
            console.error(e);
        }
    }""")
    time.sleep(1)

def perform_login(context, page, username, password):
    """이중 로그인 모달 우회 지원 로그인 함수"""
    print(f"\n--- Logging in as {username} ---")
    context.clear_cookies()
    page.goto("http://localhost:8080/backoffice/view/login")
    page.wait_for_selector("#login_userid", timeout=10000)
    page.fill("#login_userid", username)
    page.fill("#login_password", password)
    page.locator("button[type='submit'], button.btn, a.btn").first.click()
    
    # 이중 로그인 모달 및 부트박스 팝업 처리 루프
    for _ in range(10):
        time.sleep(1)
        if 'main' in page.url:
            print(f"Successfully logged in as {username}.")
            return True
        # 부트박스 확인 모달 클릭
        bootbox_ok = page.locator('.bootbox-accept, .modal-footer .btn-primary')
        if bootbox_ok.count() > 0 and bootbox_ok.first.is_visible():
            print("[UI] Double login modal detected. Clicking confirm...")
            bootbox_ok.first.click()
            time.sleep(1.5)
    print(f"[FAIL] Login failed for {username}. Current URL: {page.url}")
    return False

def run_e2e_test():
    db_cleanup() # 선행 클린업
    
    with sync_playwright() as p:
        # 크롬 브라우저 기동 (headless=False)
        browser = p.chromium.launch(headless=False, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        # 공통 얼럿/모달 처리 (이중 로그인 수락 등)
        def handle_dialog(dialog):
            print(f"[Dialog] Message: {dialog.message}")
            dialog.accept()
        page.on("dialog", handle_dialog)
        
        # ----------------------------------------------------
        # 1. ADMIN 사원관리 (admin_emp_00001) 테스트
        # ----------------------------------------------------
        print("\n=== Start ADMIN Employee Management Test ===")
        if not perform_login(context, page, "admin2", "0000"):
            return
            
        dismiss_passwords_modal(page)
        
        # admin 사원관리 화면 진입
        page.goto("http://localhost:8080/backoffice/view/main/admin/employee/admin_emp_00001")
        time.sleep(3)
        
        # 매장 탭 클릭 (한글 인코딩 방지를 위해 속성 선택자 사용)
        page.locator('a[onclick="fnChange(\'shop\');"]').click()
        time.sleep(2)
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "admin_emp_00001_initial.png"))
        print("[Screenshot] Saved admin_emp_00001_initial.png")
        
        # 계정 생성 모달 오픈
        page.click("#admin_emp_00001_add_ms_btn")
        time.sleep(1.5)
        
        # 모달 폼 작성
        page.fill("#addUserModal #addUserId", "playadmin01")
        page.click("#addUserModal #btDupChk")
        time.sleep(1)
        
        page.fill("#addUserModal #userNm", "E2EadminTest")
        page.fill("#addUserModal #addEmail", "playadmin@hmotors.com")
        page.fill("#addUserModal #addTelNo", "010-9999-8888")
        
        # selectpicker 렌더링 우회하여 jQuery로 값 직접 바인딩
        page.evaluate("""() => {
            $('#addUser_userType_store_combo_select').selectpicker('val', '1');
            $('#addOrderFg').selectpicker('val', '0');
            $('#addUseYn').selectpicker('val', 'Y');
            $('#hqEmp0101M01MsNo').val('NC0001');
            $('#hqYn').val('shop');
        }""")
        time.sleep(1.5)
        
        # 저장 버튼 클릭
        page.click("#addUserModal button.btn-primary")
        time.sleep(2.5) # DB 반영 대기
        
        # DB 검증 (Insert & Java Trigger)
        emp_id = verify_db_insert("playadmin01")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "admin_emp_00001_saved.png"))
        print("[Screenshot] Saved admin_emp_00001_saved.png")
        
        # 사원 정보 수정
        # 검색
        page.fill("#admin_emp_00001_form input[name='storeUserId']", "playadmin01")
        page.click("#admin_emp_00001_search_btn_store")
        time.sleep(2)
        
        # 목록의 첫 행 더블클릭
        page.locator("#admin_emp_00001_t02 tbody tr").first.dblclick()
        time.sleep(2)
        
        # 수정 폼 작성
        page.fill("#editUserModal #editNm", "E2EadminTestModify")
        page.fill("#editUserModal #chkpassWd", "0000") # 세션 비밀번호인 0000 입력
        
        page.evaluate("""() => {
            $('#edit_userType_store_combo_select').selectpicker('val', '1');
            $('#editOrderFg').selectpicker('val', '0');
            $('#editUseYn').selectpicker('val', 'Y');
        }""")
        time.sleep(1.5)
        
        # 수정 저장
        page.click("#editUserModal button.btn-primary")
        time.sleep(2.5)
        
        # DB 검증
        verify_db_update("playadmin01")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "admin_emp_00001_updated.png"))
        print("[Screenshot] Saved admin_emp_00001_updated.png")
        
        # 삭제
        page.locator("#admin_emp_00001_t02 tbody tr input[type='checkbox']").first.click()
        time.sleep(1)
        page.click("#admin_emp_00001_delete_ms_btn")
        time.sleep(1.5)
        
        # 비밀번호 확인 모달 (#deleteChkModal) 처리
        page.fill("#deleteChkModal #passWd", "0000")
        page.click("#deleteChkModal button.btn-primary")
        time.sleep(2.5)
        
        # DB 삭제 검증
        verify_db_delete(emp_id)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "admin_emp_00001_deleted.png"))
        print("[Screenshot] Saved admin_emp_00001_deleted.png")
        
        # 로그아웃
        page.goto("http://localhost:8080/backoffice/auth/logout")
        time.sleep(2)
        
        # ----------------------------------------------------
        # 2. HQ 사원관리 (hq_emp_00001) 테스트
        # ----------------------------------------------------
        print("\n=== Start HQ Employee Management Test ===")
        if not perform_login(context, page, "shopadmin", "0000"):
            return
        
        dismiss_passwords_modal(page)
        
        page.goto("http://localhost:8080/backoffice/view/main/hq/employee/hq_emp_00001")
        time.sleep(3)
        
        # 매장 탭 클릭 (한글 인코딩 방지를 위해 속성 선택자 사용)
        page.locator('a[onclick="fnChange(\'shop\');"]').click()
        time.sleep(2)
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_emp_00001_initial.png"))
        print("[Screenshot] Saved hq_emp_00001_initial.png")
        
        page.click("#hq_emp_00001_add_ms_btn")
        time.sleep(1.5)
        
        page.fill("#addUserModal #addUserId", "playhq001")
        page.click("#addUserModal #btDupChk")
        time.sleep(1)
        
        page.fill("#addUserModal #userNm", "E2EhqTest")
        page.fill("#addUserModal #addEmail", "playhq@hmotors.com")
        page.fill("#addUserModal #addTelNo", "010-7777-6666")
        
        page.evaluate("""() => {
            $('#addUser_userType_store_combo_select').selectpicker('val', '1');
            $('#addOrderFg').selectpicker('val', '0');
            $('#addUseYn').selectpicker('val', 'Y');
            $('#hqEmp0101M01MsNo').val('NC0001');
            $('#hqYn').val('shop');
        }""")
        time.sleep(1.5)
        
        page.click("#addUserModal button.btn-primary")
        time.sleep(2.5)
        
        emp_id = verify_db_insert("playhq001")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_emp_00001_saved.png"))
        print("[Screenshot] Saved hq_emp_00001_saved.png")
        
        # 수정
        page.fill("#hq_emp_00001_form input[name='storeUserId']", "playhq001")
        page.click("#hq_emp_00001_search_btn_store")
        time.sleep(2)
        
        page.locator("#hq_emp_00001_t02 tbody tr").first.dblclick()
        time.sleep(2)
        
        page.fill("#editUserModal #editNm", "E2EhqTestModify")
        page.fill("#editUserModal #chkpassWd", "0000")
        
        page.evaluate("""() => {
            $('#edit_userType_store_combo_select').selectpicker('val', '1');
            $('#editOrderFg').selectpicker('val', '0');
            $('#editUseYn').selectpicker('val', 'Y');
        }""")
        time.sleep(1.5)
        
        page.click("#editUserModal button.btn-primary")
        time.sleep(2.5)
        
        verify_db_update("playhq001")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_emp_00001_updated.png"))
        print("[Screenshot] Saved hq_emp_00001_updated.png")
        
        # 삭제
        page.locator("#hq_emp_00001_t02 tbody tr input[type='checkbox']").first.click()
        time.sleep(1)
        page.click("#hq_emp_00001_delete_ms_btn")
        time.sleep(1.5)
        
        page.fill("#deleteChkModal #passWd", "0000")
        page.click("#deleteChkModal button.btn-primary")
        time.sleep(2.5)
        
        verify_db_delete(emp_id)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_emp_00001_deleted.png"))
        print("[Screenshot] Saved hq_emp_00001_deleted.png")
        
        page.goto("http://localhost:8080/backoffice/auth/logout")
        time.sleep(2)
        
        # ----------------------------------------------------
        # 3. ST 사원관리 (st_emp_00001) 테스트
        # ----------------------------------------------------
        print("\n=== Start ST Employee Management Test ===")
        if not perform_login(context, page, "fnbcafe", "0000"):
            return
        
        dismiss_passwords_modal(page)
        
        page.goto("http://localhost:8080/backoffice/view/main/st/employee/st_emp_00001")
        time.sleep(3)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "st_emp_00001_initial.png"))
        print("[Screenshot] Saved st_emp_00001_initial.png")
        
        page.click("#st_emp_00001_add_ms_btn")
        time.sleep(1.5)
        
        page.fill("#addUserModal #addUserId", "playst001")
        page.click("#addUserModal #btDupChk")
        time.sleep(1)
        
        page.fill("#addUserModal #userNm", "E2EstTest")
        page.fill("#addUserModal #addEmail", "playst@hmotors.com")
        page.fill("#addUserModal #addTelNo", "010-5555-4444")
        
        # ST 화면은 본사 구분(HQ) 없이 매장 구분만 있으므로 #addUser_userType_combo_select 사용
        page.evaluate("""() => {
            $('#addUser_userType_combo_select').selectpicker('val', '1');
            $('#addOrderFg').selectpicker('val', '0');
            $('#addUseYn').selectpicker('val', 'Y');
            $('#hqEmp0101M01MsNo').val('NC0001');
            $('#hqYn').val('shop');
        }""")
        time.sleep(1.5)
        
        page.click("#addUserModal button.btn-primary")
        time.sleep(2.5)
        
        emp_id = verify_db_insert("playst001")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "st_emp_00001_saved.png"))
        print("[Screenshot] Saved st_emp_00001_saved.png")
        
        # 수정
        page.fill("#st_emp_00001_form input[name='storeUserId']", "playst001")
        page.click("#st_emp_00001_search_btn_store")
        time.sleep(2)
        
        page.locator("#st_emp_00001_t02 tbody tr").first.dblclick()
        time.sleep(2)
        
        page.fill("#editUserModal #editNm", "E2EstTestModify")
        page.fill("#editUserModal #chkpassWd", "0000")
        
        page.evaluate("""() => {
            $('#edit_userType_combo_select').selectpicker('val', '1');
            $('#editOrderFg').selectpicker('val', '0');
            $('#editUseYn').selectpicker('val', 'Y');
        }""")
        time.sleep(1.5)
        
        page.click("#editUserModal button.btn-primary")
        time.sleep(2.5)
        
        verify_db_update("playst001")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "st_emp_00001_updated.png"))
        print("[Screenshot] Saved st_emp_00001_updated.png")
        
        # 삭제
        page.locator("#st_emp_00001_t02 tbody tr input[type='checkbox']").first.click()
        time.sleep(1)
        page.click("#st_emp_00001_delete_ms_btn")
        time.sleep(1.5)
        
        page.fill("#deleteChkModal #passWd", "0000")
        page.click("#deleteChkModal button.btn-primary")
        time.sleep(2.5)
        
        verify_db_delete(emp_id)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "st_emp_00001_deleted.png"))
        print("[Screenshot] Saved st_emp_00001_deleted.png")
        
        # 최종 로그아웃
        page.goto("http://localhost:8080/backoffice/auth/logout")
        time.sleep(2)
        
        print("\n*** All E2E Employee Management Tests Passed and DB Logs Verified! ***")
        browser.close()

if __name__ == "__main__":
    try:
        run_e2e_test()
    finally:
        # 테스트 종료 후 최종 정리
        db_cleanup()
