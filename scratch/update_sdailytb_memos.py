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
    if "sdailytb" not in tables:
        print("sdailytb key not found in tables. Initializing...")
        tables["sdailytb"] = {
            "memo": "가맹점(매장)별 일자 단위 매출 집계 테이블입니다. (Store Daily Sales Aggregate)",
            "starred": True,
            "color": "none",
            "columns": {},
            "memo_c": "영업 일자가 종료되고 일일 마감 배치가 기동되거나 POS 마감 신호 수신 시, 당일 매출 영수증 데이터(tsm_tran_mst)를 기반으로 지불 수단별(현금, 카드, 제휴 등) 및 할인 유형별 매출 데이터를 합산하여 신규 생성(Insert)합니다.",
            "memo_u": "해당 일자의 소급 매출 보정, 반품 거래 발생, 또는 마감 재처리 배치 가동 시 기존 일집계 데이터를 갱신(Update) 처리합니다.",
            "memo_d": "통계 및 감사 자료의 일관성 보존을 위해 물리 삭제(Hard Delete)는 원칙적으로 금지되며, 시스템 폐기 및 마이그레이션 정책에 의해서만 정리됩니다.",
            "memo_r": "백오피스 매출 현황 조회(예: 기간별 매출 추이, 가맹점 일별 매출 현황, 매출 통계 대시보드) 화면에서 핵심적인 집계 소스로 조회됩니다."
        }
        
    sdailytb = tables["sdailytb"]
    
    # Add/Update related_tables with all verified related tables
    sdailytb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] SDAILYTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 일 매출이 집계된 가맹점 매장의 세부 정보 및 소속 브랜드 체인을 확인합니다."
        },
        {
            "table_name": "smonthtb",
            "description": "[가맹점 월 매출 집계] 일 매출 데이터를 연월별로 2차 합산하여 월 단위 매출 통계 데이터(SMONTHTB)를 작성할 때 데이터 원천으로 연동됩니다."
        },
        {
            "table_name": "saregitb",
            "description": "[정산 내역] 포스별 교대/일정산 내역(SAREGITB)과 일자별 총 집계 매출(SDAILYTB)을 상호 대조하여 현금 과부족이나 정산 불일치를 검증할 때 연계됩니다."
        },
        {
            "table_name": "tsm_tran_mst",
            "description": "[매출 영수증 마스터] SDAILYTB.MS_NO = TSM_TRAN_MST.MS_NO AND SDAILYTB.SALE_DATE = TSM_TRAN_MST.SALE_DATE 조인을 통해 일별 매출 집계 결과의 원천 영수증 상세 거래를 역추적(Drill-down)할 때 사용됩니다."
        },
        {
            "table_name": "sdaypmtb",
            "description": "[일자별 프로모션 집계] SDAILYTB.MS_NO = SDAYPMTB.MS_NO AND SDAILYTB.SALE_DATE = SDAYPMTB.SALE_DATE 조인을 통해 당일 전체 매출 중 개별 프로모션(행사/우대) 할인 집계 데이터를 상호 대조 분석합니다."
        },
        {
            "table_name": "strnchtb",
            "description": "[외상 수금 상세] SDAILYTB.MS_NO = STRNCHTB.MS_NO AND SDAILYTB.SALE_DATE = STRNCHTB.SALE_DATE 조인을 통해 당일 매출 중 발생한 외상 매출 총액과 실제 외상 수금(수령)된 상세 내역의 실적을 매핑 검증합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with sdailytb details (including sdaypmtb and strnchtb)!")
        
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
