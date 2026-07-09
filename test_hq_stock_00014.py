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

def run_e2e_test():
    with sync_playwright() as p:
        print("Launching browser (headless=False)...")
        browser = p.chromium.launch(headless=False, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        # 공통 얼럿/모달 처리
        def handle_dialog(dialog):
            print(f"[Dialog] Message: {dialog.message}")
            dialog.accept()
        page.on("dialog", handle_dialog)
        
        print("\n=== Start HQ Monthly Stock Log Search (hq_stock_00014) Test ===")
        # 1. 로그인
        if not perform_login(context, page, "shopadmin", "0000"):
            return
            
        dismiss_passwords_modal(page)
        
        # 2. 재고 로그 조회 화면 진입
        print("Navigating to Stock Log page...")
        page.goto("http://localhost:8080/backoffice/view/main/hq/stock/hq_stock_00014")
        time.sleep(3)
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_stock_00014_initial.png"))
        print("[Screenshot] Saved hq_stock_00014_initial.png")
        
        # 3. 조회 기간 및 매장코드(NC0007) 바인딩 및 조회 조건 설정
        print("Setting query conditions...")
        page.evaluate("""() => {
            // 시작일 / 종료일 설정
            $('#searchFromDate').val('2026-06-20');
            $('#searchEndDate').val('2026-06-22');
            
            // 매장선택 컴포넌트(NC0007 - CAFE) 지정
            var selectShop = $('#selectMsPos select');
            if (selectShop.length > 0) {
                selectShop.selectpicker('val', 'NC0007').trigger('change');
            }
        }""")
        time.sleep(1.5)
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_stock_00014_conditions.png"))
        print("[Screenshot] Saved hq_stock_00014_conditions.png")
        
        # 4. 조회 실행
        print("Clicking search button...")
        page.click("#hq_stock_00014_searchStockLogList_btn")
        time.sleep(3) # 데이터 로딩 대기
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_stock_00014_results.png"))
        print("[Screenshot] Saved hq_stock_00014_results.png")
        
        # 5. 그리드 데이터 단언(assert) 검증
        print("Verifying grid rows...")
        
        # 그리드 내부의 로우 개수 및 데이터 체크
        row_count = page.locator("#hq_stock_00014_t01 tbody tr").count()
        print(f"Grid row count: {row_count}")
        
        # 비어있는 상태('No matching records found')가 아닌지 체크
        first_row_text = page.locator("#hq_stock_00014_t01 tbody tr").first.text_content()
        assert "No matching" not in first_row_text, "그리드에 재고 로그 데이터가 로드되지 않았습니다."
        
        # 각 수불유형별 로우 데이터 확인
        # 첫 번째 로우: T0000001 ((Food)그뤼에르 치즈), 매입입고, 수량 10, 단가 15,000
        # 두 번째 로우: T0000002, 폐기, 수량 5, 단가 10,000
        # 세 번째 로우: T0000291, 매출, 수량 2, 단가 25,000
        all_text = [page.locator("#hq_stock_00014_t01 tbody tr").nth(i).text_content() for i in range(row_count)]
        for text in all_text:
            print("Row data:", text)
            
        assert any("매입입고" in t and "10" in t for t in all_text), "매입입고 로그 데이터 불일치"
        assert any("폐기" in t and "5" in t for t in all_text), "폐기 로그 데이터 불일치"
        assert any("매출" in t and "2" in t for t in all_text), "매출 로그 데이터 불일치"
        
        print("Grid data validation succeeded!")
        
        # 6. 수불유형 필터 테스트 (매입입고로 좁혀지는지 검증)
        print("\nTesting suber type filter (ProcFG = P)...")
        page.evaluate("""() => {
            $('#searchProcFg').selectpicker('val', 'P').trigger('change');
        }""")
        time.sleep(1)
        
        page.click("#hq_stock_00014_searchStockLogList_btn")
        time.sleep(2)
        
        filtered_row_count = page.locator("#hq_stock_00014_t01 tbody tr").count()
        print(f"Filtered grid row count: {filtered_row_count}")
        
        filtered_row_text = page.locator("#hq_stock_00014_t01 tbody tr").first.text_content()
        print("Filtered Row text:", filtered_row_text)
        
        assert filtered_row_count == 1, f"Expected 1 filtered row, but got {filtered_row_count}"
        assert "매입입고" in filtered_row_text, "필터링된 결과에 매입입고 유형이 없습니다."
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_stock_00014_filtered.png"))
        print("[Screenshot] Saved hq_stock_00014_filtered.png")
        
        # 최종 로그아웃
        page.goto("http://localhost:8080/backoffice/auth/logout")
        time.sleep(2)
        
        print("\n*** All Playwright E2E Stock Log Tests Completed Successfully! ***")
        browser.close()

if __name__ == "__main__":
    run_e2e_test()
