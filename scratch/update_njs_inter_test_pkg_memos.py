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
    if "njs_inter_test_pkg" not in tables:
        print("njs_inter_test_pkg key not found in tables. Initializing...")
        tables["njs_inter_test_pkg"] = {
            "memo": "NJS_INTER_TEST_PKG 테이블 정보입니다. (포스 연동 인터페이스 테스트 패키지 상세)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "매장 POS 트랜잭션 전송 수신 또는 화면 내 업무 전표 저장 처리를 통해 신규 행이 삽입됩니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "일자별 실적 통계 조회, 결산 대시보드 그래프 구성, 그리고 기간별 마감 정산 화면에서 통계 쿼리를 통해 조회됩니다."
        }
        
    njs_inter_test_pkg = tables["njs_inter_test_pkg"]
    
    # Add/Update related_tables with all verified related tables in the telex/interface testing flow
    njs_inter_test_pkg["related_tables"] = [
        {
            "table_name": "njs_inter_test",
            "description": "[인터페이스 테스트 마스터] NJS_INTER_TEST_PKG.TR_NO = NJS_INTER_TEST.TR_NO 조인을 통해 테스트 거래 마스터 전표 정보와 세트 메뉴(패키지) 상세 구성 리스트를 N:1 관계로 대조합니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] NJS_INTER_TEST_PKG.GOODS_CD = MGOODSTB.GOODS_CD 조인을 통해 세트메뉴 내의 개별 구성 품목(단품)의 규격 및 포스 판매 단가 정보를 매핑합니다."
        },
        {
            "table_name": "tgoodstb",
            "description": "[체인 상품 마스터] 체인 레벨의 원천 상품 마스터 사양 조회를 위해 조인합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] 개별 매장(MS_NO) 기준으로 테스트 패키지 상세 트랜잭션 정보를 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 연동 테스트 모듈에서 패키지/세트 테스트 거래를 전송하거나 데이터 삭제/초기화 시 조작 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with njs_inter_test_pkg details!")
        
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
