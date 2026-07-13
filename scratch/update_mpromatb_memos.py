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
    if "mpromatb" not in tables:
        print("mpromatb key not found in tables. Initializing...")
        tables["mpromatb"] = {
            "memo": "프로모션 마스터 - 매장 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 프로모션 마스터 - 매장 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mpromatb = tables["mpromatb"]
    
    # Add/Update related_tables with all verified related tables in the promotion configuration flow
    mpromatb["related_tables"] = [
        {
            "table_name": "tpromatb",
            "description": "[본사 프로모션 마스터] 본사 기준의 프로모션 설정 테이블입니다. 본사에서 프로모션 CUD 발생 시 DB 트리거(TPROMA_T01) 및 프로시저를 기동하여 가맹 매장별 프로모션 마스터(MPROMATB)에 실시간으로 전파(UPSERT/DELETE)를 수행합니다."
        },
        {
            "table_name": "mprogdtb",
            "description": "[매장 프로모션 대상 상품] 1:N 조인 관계를 통해 프로모션 행사 마스터에 종속되는 구체적인 할인 대상 상품군 및 상품별 개별 할인 조건(할인율, 금액) 명세를 연결합니다."
        },
        {
            "table_name": "mprosgtb",
            "description": "[프로모션 대상 매장/그룹] 특정 프로모션 행사가 적용될 가맹점 등급 그룹 또는 구체적인 개별 허용 매장 목록 정보를 대조 매핑합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MPROMATB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 활성화된 개별 프로모션 정책들을 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 매장별 프로모션 상태값 수동 제어(활성/비활성), 예외 기간 조정 등 CUD 액션 발생 시 변경 감사 이력을 MMSLOGTB에 기록합니다."
        },
        {
            "table_name": "saregitb",
            "description": "[매출 실적 마스터] 프로모션 할인 혜택이 적용되어 발생한 판매 매출 대장을 집계 및 분석할 때 프로모션 마스터 코드 조인을 통해 행사명과 프로모션별 매출 통계를 노출합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mpromatb details!")
        
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
