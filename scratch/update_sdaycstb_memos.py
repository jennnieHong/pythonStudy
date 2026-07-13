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
    if "sdaycstb" not in tables:
        print("sdaycstb key not found in tables. Initializing...")
        tables["sdaycstb"] = {
            "memo": "가맹점별 시간대/연령대/성별 매출 집계 테이블입니다. (Hourly Age & Gender Sales Aggregate)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "영업 일자가 종료되고 일일 마감 배치가 기동되거나 POS 마감 신호 수신 시, 당일 매출 영수증 및 고객 멤버십 거래 데이터를 기반으로 시간대별, 내/외국인별, 연령대별(10대~50대 이상), 성별 매출과 고객 수를 합산하여 신규 생성(Insert)합니다.",
            "memo_u": "해당 일자의 소급 매출 보정, 반품 거래 발생, 또는 마감 재처리 배치 가동 시 기존 일집계 데이터를 갱신(Update) 처리합니다.",
            "memo_d": "통계 및 고객 행동 분석용 장기 감사 자료로서 물리 삭제는 원칙적으로 금지되며, 일정 기간 경과 후 데이터 백업 정책에 따라 정기 배치를 통해서만 Hard Delete 처리됩니다.",
            "memo_r": "백오피스 매출 현황 조회 및 마케팅 분석 화면(예: 시간대별 매출 현황, 고객 연령/성별 매출 분석, 마케팅 분석 대시보드)에서 핵심 소스로 조회됩니다."
        }
        
    sdaycstb = tables["sdaycstb"]
    
    # Add/Update related_tables with all verified related tables
    sdaycstb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] SDAYCSTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 연령대별 매출이 집계된 가맹점 매장의 세부 정보 및 소속 브랜드 체인을 확인합니다."
        },
        {
            "table_name": "sdailytb",
            "description": "[가맹점 일 매출 집계] 동일 영업 일자의 총 매출액 대조 및 일일 고객수 검증을 위해 매장코드와 영업일자 기준으로 조인 연동합니다."
        },
        {
            "table_name": "tsm_tran_mst",
            "description": "[매출 영수증 마스터] SDAYCSTB.MS_NO = TSM_TRAN_MST.MS_NO AND SDAYCSTB.SALE_DATE = TSM_TRAN_MST.SALE_DATE 조인을 통해 시간대별/연령대별 집계 실적의 기초가 된 원본 영수증 거래 데이터를 역추적할 때 사용됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with sdaycstb details!")
        
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
