import time
import os
import json
from playwright.sync_api import sync_playwright

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
        
        print("\n=== Start HQ Month Ucost Rate Search (hq_vendor_00018) Test ===")
        # 1. 로그인
        if not perform_login(context, page, "shopadmin", "0000"):
            return
            
        dismiss_passwords_modal(page)
        
        # 2. 월단위 원가율 현황 조회 화면 진입
        print("Navigating to Ucost Rate page...")
        page.goto("http://localhost:8080/backoffice/view/main/hq/vendor/hq_vendor_00018")
        time.sleep(3)
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_vendor_00018_initial.png"))
        print("[Screenshot] Saved hq_vendor_00018_initial.png")
        
        # 3. 조회 기간(2026-06) 및 매장코드(NC0003 - 고양 Shop) 바인딩 및 조회 조건 설정
        print("Setting query conditions...")
        page.evaluate("""() => {
            // 조회월 설정
            $('#searchMonth').val('2026-06');
            
            // 매장선택 컴포넌트 지정
            var selectShop = $('#selectMs_ms_select');
            if (selectShop.length > 0) {
                selectShop.selectpicker('val', 'NC0003').trigger('change');
            }
        }""")
        time.sleep(1.5)
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_vendor_00018_conditions.png"))
        print("[Screenshot] Saved hq_vendor_00018_conditions.png")
        
        # 4. 조회 실행
        print("Clicking search button...")
        page.click("#hq_vendor_00018_search_btn")
        time.sleep(3) # 데이터 로딩 대기
        
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "hq_vendor_00018_results.png"))
        print("[Screenshot] Saved hq_vendor_00018_results.png")
        
        # 5. 그리드 데이터 단언(assert) 검증
        print("Verifying grid rows...")
        row_count = page.locator("#hq_vendor_00018_t01 tbody tr").count()
        print(f"Grid row count: {row_count}")
        
        # 비어있는 상태('No matching records found')가 아닌지 체크
        first_row_text = page.locator("#hq_vendor_00018_t01 tbody tr").first.text_content()
        assert "No matching" not in first_row_text, "그리드에 원가율 데이터가 로드되지 않았습니다."
        
        all_text = [page.locator("#hq_vendor_00018_t01 tbody tr").nth(i).text_content() for i in range(row_count)]
        for text in all_text:
            print("Row data:", text)
            
        assert any("NC0003" in t and "고양 Shop" in t for t in all_text), "고양 Shop 원가율 데이터 매핑 실패"
        
        print("Grid data validation succeeded!")
        
        # 최종 로그아웃
        page.goto("http://localhost:8080/backoffice/auth/logout")
        time.sleep(2)
        
        print("\n*** All Playwright E2E Ucost Rate Tests Completed Successfully! ***")
        browser.close()

if __name__ == "__main__":
    run_e2e_test()
