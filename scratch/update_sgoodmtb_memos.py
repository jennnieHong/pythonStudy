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
    if "sgoodmtb" not in tables:
        print("sgoodmtb key not found in tables. Initializing...")
        tables["sgoodmtb"] = {
            "memo": "가맹점(매장)의 상품별 월 단위 매출 집계 테이블입니다. (Monthly Product Sales Aggregate)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "매월 마감 정산 배치 기동 시, 해당 월의 일자별 상품 매출 집계 데이터(sgoodstb) 또는 개별 판매 상세 영수증(tsm_tran_dtl)을 바탕으로 상품별 판매 수량, 매출 총액, 할인 및 부가세 등을 월 단위로 2차 합산하여 신규 생성(Insert)합니다.",
            "memo_u": "영업 마감 후 매출 소급 보정, 반품 재계산, 또는 월별 실적 재배치 처리 시 해당 월/매장/상품 레코드가 갱신(Update) 처리됩니다.",
            "memo_d": "과거 판매 실적 및 연간 상품 소비 트렌드 분석에 필수적인 통계 정보이므로 물리 삭제는 엄격히 금지됩니다.",
            "memo_r": "백오피스 상품 분석 메뉴(예: 상품별 월별 매출 순위, 카테고리별 월 실적 현황, 베스트셀러 상품 추이)에서 조회 소스로 사용됩니다."
        }
        
    sgoodmtb = tables["sgoodmtb"]
    
    # Add/Update related_tables with all verified related tables
    sgoodmtb["related_tables"] = [
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] SGOODMTB.GOODS_CD = MGOODSTB.GOODS_CD 조인을 통해 개별 집계 대상 상품의 상품 한글 명칭, 규격, 바코드 등 기본 정보를 연계합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] SGOODMTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 월별 상품 매출이 발생한 가맹점 매장의 브랜드 체인 소속을 확인합니다."
        },
        {
            "table_name": "sgoodstb",
            "description": "[가맹점 상품별 일 매출 집계] 상품별 월 매출 집계의 직접적인 일 단위 원천 데이터로서, 일자별 데이터를 당월 기준으로 합산(Roll-up)하여 SGOODMTB 레코드를 구성합니다."
        },
        {
            "table_name": "smonthtb",
            "description": "[가맹점 월 매출 집계] 동일 가맹점 매장의 당월 총 매출액(SALE_TOT, SALE_AMT)과 비교 검증하고 대조하기 위해 조인하여 정량적 정합성을 확인합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with sgoodmtb details!")
        
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
