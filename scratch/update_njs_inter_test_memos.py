import json
import os
import sys

def update_memos():
    path = r'd:\hmTest\backoffice\QaReport\table_memos.json'
    
    # 1. Load existing data
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
        
    tables = data.get("tables", {})
    if "njs_inter_test" not in tables:
        print("njs_inter_test key not found in tables. Initializing...")
        tables["njs_inter_test"] = {
            "memo": "NJS_INTER_TEST 테이블 정보입니다. (포스 연동 인터페이스 테스트 마스터)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "매장 POS 트랜잭션 전송 수신 또는 화면 내 업무 전표 저장 처리를 통해 신규 행이 삽입됩니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "일자별 실적 통계 조회, 결산 대시보드 그래프 구성, 그리고 기간별 마감 정산 화면에서 통계 쿼리를 통해 조회됩니다."
        }
        
    njs_inter_test = tables["njs_inter_test"]
    
    # Add/Update related_tables with all verified related tables in the telex/interface testing flow
    njs_inter_test["related_tables"] = [
        {
            "table_name": "njs_inter_test_goods",
            "description": "[인터페이스 테스트 상품 상세] NJS_INTER_TEST의 마스터 거래 건에 귀속된 테스트용 상세 판매 상품(원자재/메뉴) 정보 명세들을 1:N 조인 관계로 연결하여 관리합니다."
        },
        {
            "table_name": "njs_inter_test_use",
            "description": "[인터페이스 테스트 결제 내역] 테스트용 인터페이스 거래에서 발생한 결제 수단별(현금, 신용카드, 포인트 등) 승인 상세 내역을 1:N 관계로 귀속시켜 기록합니다."
        },
        {
            "table_name": "njs_inter_test_cancel",
            "description": "[인터페이스 테스트 취소 내역] 테스트 거래 중 결제 취소 또는 반품 처리가 발생한 경우의 승인 취소 정합성을 1:1 매칭하여 보관합니다."
        },
        {
            "table_name": "njs_inter_test_pkg",
            "description": "[인터페이스 테스트 패키지] 세트 메뉴 혹은 복합 묶음 상품의 인터페이스 거래 연동 테스트 시 묶음 구성 사양을 조인 매핑합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] 개별 매장(MS_NO) 기준으로 인터페이스 테스트 트랜잭션 정보 및 전송 채널 상태를 파티셔닝하여 제어합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 연동 테스트 모듈에서 강제 트랜잭션 전송 테스트를 기동하거나, 기존 테스트 데이터 삭제/초기화 시 조작 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with njs_inter_test details!")
        
        # Automatically run generate_table_dictionary.py to compile HTML
        gen_script = r"D:\hmTest\backoffice\QaReport\generate_table_dictionary.py"
        if os.path.exists(gen_script):
            print("Auto-running generate_table_dictionary.py to rebuild HTML...")
            os.system(f'python "{gen_script}"')
            print("Successfully regenerated hms_db_dictionary.html!")
        else:
            print(f"Generator script not found: {gen_script}")
    except Exception as e:
        print(f"Error saving JSON or generating HTML: {e}")

if __name__ == '__main__':
    update_memos()
