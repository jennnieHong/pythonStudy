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
    if "sdaypmtb" not in tables:
        print("sdaypmtb key not found in tables. Initializing...")
        tables["sdaypmtb"] = {
            "memo": "가맹점별 일자 단위 프로모션(행사/우대) 매출 집계 테이블입니다. (Daily Promotion Sales Aggregate)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "영업 일자가 종료되고 일일 마감 배치가 기동되거나 POS 마감 신호 수신 시, 프로모션 대상 거래 내역을 집계하여 연도별, 프로모션 코드별, 처리 구분별로 거래 건수와 총 매출액, 할인 금액, 포인트 사용액을 합산하여 신규 생성(Insert)합니다.",
            "memo_u": "해당 일자의 소급 매출 보정, 반품 거래 발생, 또는 마감 재처리 배치 가동 시 기존 프로모션 집계 데이터를 갱신(Update) 처리합니다.",
            "memo_d": "통계 및 행사 성과 분석 자료로서 물리 삭제는 원칙적으로 금지되며, 시스템 폐기 및 마이그레이션 정책에 의해서만 정리됩니다.",
            "memo_r": "백오피스 매출 현황 조회 및 마케팅 분석 화면(예: 프로모션별 매출 분석, 행사 상품 판매 현황, 마케팅 성과 분석 대시보드)에서 행사 할인 실적을 대조하기 위해 조회됩니다."
        }
        
    sdaypmtb = tables["sdaypmtb"]
    
    # Add/Update related_tables with all verified related tables
    sdaypmtb["related_tables"] = [
        {
            "table_name": "tpromatb",
            "description": "[프로모션 행사 마스터] SDAYPMTB.PROMOTION_YEAR = TPROMATB.PROMOTION_YEAR AND SDAYPMTB.PROMOTION_CD = TPROMATB.PROMOTION_CD 조인을 통해 개별 집계 레코드의 제휴 카드사 정보, 프로모션 명칭 및 행사 상세 사양 정보를 가져옵니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] SDAYPMTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 프로모션 매출이 발생한 가맹점 매장의 세부 정보 및 소속 브랜드 체인을 확인합니다."
        },
        {
            "table_name": "sdailytb",
            "description": "[가맹점 일 매출 집계] 동일 영업 일자의 총 매출액 및 총 할인액(DC_AMT) 대비 프로모션 할인 비중을 대조하고 검증하기 위해 매장코드와 영업일자 기준으로 조인 연동합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with sdaypmtb details!")
        
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
