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

SCREENSHOT_DIR = r"C:\Users\uoshj\.gemini\antigravity-ide\brain\5b781763-17f9-44c1-92ff-e431cff8ecde"

def dismiss_passwords_modal(page):
    """비밀번호 강제 변경 팝업 우회"""
    print("[UI] Dismissing passwordsModal...")
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

def check_db_close_status(month="202606"):
    """STCKIOTB 마감 상태 체크"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT STOCK_MONTH, PROC_YN, PROC_ID, CANCEL_YN 
        FROM hmsfns.STCKIOTB 
        WHERE STOCK_MONTH = %s 
        ORDER BY PROC_CREATE_DTIME DESC LIMIT 1
    """, (month,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def check_db_latest_error():
    """STCKERTB 에러 로그 체크"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT REMARK 
        FROM hmsfns.STCKERTB 
        ORDER BY CREATE_DTIME DESC LIMIT 1
    """)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

def clear_db_close_records(month="202606"):
    """이전 테스트 기록 완벽 삭제 (클린 스타트) 및 이월 기초 데이터 복원"""
    print(f"[DB] Cleaning up STCKIOTB, STCKERTB, IMMMIOTB for {month}...")
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hmsfns.STCKIOTB WHERE STOCK_MONTH = %s", (month,))
    cursor.execute("DELETE FROM hmsfns.STCKERTB WHERE STOCK_MONTH = %s", (month,))
    cursor.execute("DELETE FROM hmsfns.IMMMIOTB WHERE CREATE_MONTH = %s", (month,))
    
    # 1. 전월(202605)로부터 202606 재고 이월(Carry Over) 복원 (41개 컬럼)
    print("[DB] Restoring IMMMIOTB carryover from 202605 to 202606...")
    cursor.execute("""
        INSERT INTO hmsfns.IMMMIOTB (
            create_month, ms_no, goods_cd, chain_ms_no,
            start_qty, start_cost,
            purch_qty, purch_cost, purch_extra_cost,
            return_qty, return_cost,
            sale_qty, sale_cost, sale_extra_cost,
            in_qty, in_cost,
            out_qty, out_cost,
            disuse_qty, disuse_cost,
            adjust_qty, adjust_cost,
            tin_qty, tin_cost,
            tout_qty, tout_cost,
            end_qty, end_cost,
            returndis_qty, returndis_cost,
            move_in_qty, move_in_cost,
            move_out_qty, move_out_cost,
            wholesale_qty, wholesale_cost,
            wholesale_rt_qty, wholesale_rt_cost,
            start_cost_totavg, end_cost_totavg,
            purch_gab_extra_cost
        )
        SELECT 
            '202606', ms_no, goods_cd, chain_ms_no,
            end_qty, end_cost,
            0, 0, 0,
            0, 0,
            0, 0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            end_qty, end_cost,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0
        FROM hmsfns.IMMMIOTB
        WHERE CREATE_MONTH = '202605'
    """)
    
    # 2. 202606에 입출고 트랜잭션이 존재하지만 기초 이월 데이터가 없는 신규 취급 상품들에 대한 IMMMIOTB 초기화 (41개 컬럼)
    print("[DB] Initializing IMMMIOTB rows for new active products in IMDDIOTB...")
    cursor.execute("""
        INSERT INTO hmsfns.IMMMIOTB (
            create_month, ms_no, goods_cd, chain_ms_no,
            start_qty, start_cost,
            purch_qty, purch_cost, purch_extra_cost,
            return_qty, return_cost,
            sale_qty, sale_cost, sale_extra_cost,
            in_qty, in_cost,
            out_qty, out_cost,
            disuse_qty, disuse_cost,
            adjust_qty, adjust_cost,
            tin_qty, tin_cost,
            tout_qty, tout_cost,
            end_qty, end_cost,
            returndis_qty, returndis_cost,
            move_in_qty, move_in_cost,
            move_out_qty, move_out_cost,
            wholesale_qty, wholesale_cost,
            wholesale_rt_qty, wholesale_rt_cost,
            start_cost_totavg, end_cost_totavg,
            purch_gab_extra_cost
        )
        SELECT DISTINCT
            '202606', L.ms_no, L.goods_cd,
            COALESCE((SELECT chain_ms_no FROM hmsfns.IMMMIOTB WHERE ms_no = L.ms_no LIMIT 1), 'NC0002'),
            0, 0,
            0, 0, 0,
            0, 0,
            0, 0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0, 0,
            0
        FROM hmsfns.IMDDIOTB L
        WHERE L.CREATE_DATE LIKE '202606%'
          AND L.MS_NO IN (SELECT MS_NO FROM hmsfns.MMEMBSTB WHERE CHAIN_NO = 'C001')
          AND NOT EXISTS (
              SELECT 1 FROM hmsfns.IMMMIOTB X
              WHERE X.CREATE_MONTH = '202606'
                AND X.MS_NO = L.MS_NO
                AND X.GOODS_CD = L.GOODS_CD
          )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def run_e2e_test():
    # 클린 스타트 실행
    clear_db_close_records("202606")
    
    with sync_playwright() as p:
        print("Launching browser (headless=False)...")
        browser = p.chromium.launch(headless=False, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        # 공통 다이얼로그(얼럿) 수락 핸들러
        def handle_dialog(dialog):
            print(f"[Dialog] Message: {dialog.message}")
            dialog.accept()
        page.on("dialog", handle_dialog)
        
        print("\n=== Start HQ Month Close (hq_stock_00013) Test ===")
        # 1. 로그인
        if not perform_login(context, page, "shopadmin", "0000"):
            return
            
        dismiss_passwords_modal(page)
        
        # 2. 월마감 관리 화면 진입
        print("Navigating to Month Close page...")
        page.goto("http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00013")
        time.sleep(3)
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_stock_00013_initial.png"))
        print("[Screenshot] Saved hq_stock_00013_initial.png")
        
        # 3. 월마감 진행
        print("Executing excuteMonthClose...")
        page.click("#hq_stock_00013_excute_btn")
        time.sleep(1.5)
        
        # 부트박스 컨펌 수락
        bootbox_confirm = page.locator('.bootbox-confirm .bootbox-accept')
        if bootbox_confirm.count() > 0 and bootbox_confirm.first.is_visible():
            print("[UI] Clicking confirm month close...")
            bootbox_confirm.first.click()
            time.sleep(10) # 배치 구동 대기
            
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_stock_00013_closed.png"))
        print("[Screenshot] Saved hq_stock_00013_closed.png")
        
        # 4. DB 검증 (정상 마감 여부)
        status = check_db_close_status("202606")
        print(f"[DB Verification] Close record: {status}")
        assert status is not None and status[1] == 'Y', "마감이 데이터베이스에 정상 적재되지 않았습니다."
        print("[SUCCESS] FIFO Month Close completed in DB!")
        
        # 5. 중복 마감 예외 테스트
        print("\nExecuting excuteMonthClose again to test duplicate check...")
        page.click("#hq_stock_00013_excute_btn")
        time.sleep(1.5)
        if bootbox_confirm.count() > 0 and bootbox_confirm.first.is_visible():
            print("[UI] Clicking confirm duplicate month close...")
            bootbox_confirm.first.click()
            time.sleep(8) # 에러 반환 대기
            
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_stock_00013_dup_error.png"))
        print("[Screenshot] Saved hq_stock_00013_dup_error.png")
        
        # DB 에러 테이블 검증
        latest_err = check_db_latest_error()
        print(f"[DB Verification] Latest Error Log: {latest_err}")
        assert "MONTHS STOCK EXISTS" in latest_err, "중복 마감 예외가 발생하지 않았습니다."
        print("[SUCCESS] Duplicate close blocked and logged successfully!")
        
        # 알림창(부트박스 얼럿) 닫기
        bootbox_alert_ok = page.locator('.bootbox-alert .bootbox-accept, .bootbox-alert .modal-footer .btn-primary, .bootbox-alert .btn-primary')
        if bootbox_alert_ok.count() > 0 and bootbox_alert_ok.first.is_visible():
            print("[UI] Dismissing duplicate close alert modal...")
            bootbox_alert_ok.first.click()
            time.sleep(1)
            
        # 6. 재마감 진행 (reDoMonthClose)
        print("\nExecuting reDoMonthClose (redo close)...")
        page.click("#hq_stock_00013_reExcute_btn")
        time.sleep(1.5)
        
        if bootbox_confirm.count() > 0 and bootbox_confirm.first.is_visible():
            print("[UI] Clicking confirm redo month close...")
            bootbox_confirm.first.click()
            time.sleep(10) # 재마감 대기
            
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_stock_00013_redo.png"))
        print("[Screenshot] Saved hq_stock_00013_redo.png")
        
        # DB 재검증 (최신 로우가 CANCEL_YN='N'이고 이전 로우가 CANCEL_YN='Y' 상태인지)
        status_redo = check_db_close_status("202606")
        print(f"[DB Verification] Redo record: {status_redo}")
        assert status_redo is not None and status_redo[1] == 'Y' and status_redo[3] == 'N', "재마감이 정상 수행되지 않았습니다."
        print("[SUCCESS] Redo Month Close completed successfully!")
        
        # 최종 로그아웃
        page.goto("http://localhost:8080/backoffice/auth/logout")
        time.sleep(2)
        
        print("\n*** All Playwright E2E Month Close Tests Completed Successfully! ***")
        browser.close()

if __name__ == "__main__":
    run_e2e_test()
