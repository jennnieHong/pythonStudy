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
    if "scdlogtb" not in tables:
        print("scdlogtb key not found in tables. Initializing...")
        tables["scdlogtb"] = {
            "memo": "POS 단말기에서 처리된 실시간 신용카드 승인 및 취소 로그 테이블입니다. (Credit Card Approval Log)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "POS 단말기에서 신용카드 결제 및 승인/취소 거래가 정상적으로 수행되면, 연동 전문 수신(Telex/웹 API)을 통해 신규 카드 승인 로그 데이터가 실시간 생성(Insert)됩니다.",
            "memo_u": "승인 이력 및 금융 보안 정보의 투명한 보존을 위해 한 번 적재된 신용카드 승인 로그 데이터의 인위적인 수정을 금지합니다.",
            "memo_d": "세무 및 회계 감사 자료 보존 기한 준수를 위해 데이터 물리 삭제(Hard Delete)는 엄격히 금지되며, 일정 기간 경과 후 아카이빙 배치 프로세스에 의해서만 분할 삭제됩니다.",
            "memo_r": "백오피스 매출 현황 조회 화면(예: 카드사 승인 내역, 카드 매출 현황) 및 마감 정산 대조, 과부족 차액 분석 시 상세 거래 이력을 추적하기 위해 조회됩니다."
        }
        
    scdlogtb = tables["scdlogtb"]
    
    # Add/Update related_tables with all verified related tables
    scdlogtb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] SCDLOGTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 카드 승인 거래가 발생한 가맹점 매장의 상세 인프라 정보 및 브랜드를 연계합니다."
        },
        {
            "table_name": "saregitb",
            "description": "[정산 내역] 매장 정산 내역의 신용카드 매출 집계액(CARD_AMT) 및 건수(CARD_CNT)와 실시간 개별 카드 승인액의 누적 합계를 대조하여 정산 금액 검증 시 조인 연동됩니다."
        },
        {
            "table_name": "tsm_tran_mst",
            "description": "[매출 영수증 마스터] SCDLOGTB.MS_NO = TSM_TRAN_MST.MS_NO AND SCDLOGTB.SALE_DATE = TSM_TRAN_MST.SALE_DATE AND SCDLOGTB.POS_NO = TSM_TRAN_MST.POS_NO AND SCDLOGTB.BILL_NO = TSM_TRAN_MST.BILL_NO 조인을 통해 영수증 단위 매출 건과 실제 처리된 카드 결제 거래 이력을 대조 매핑합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with scdlogtb details!")
        
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
