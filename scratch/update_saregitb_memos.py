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
    if "saregitb" not in tables:
        print("saregitb key not found in tables. Initializing...")
        tables["saregitb"] = {
            "memo": "포스 단말기별 교대 정산 및 일자별 정산 내역 테이블입니다. (POS Shift & Daily Settlement History)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "각 포스 단말기에서 캐셔가 로그인하여 정산(교대 정산, 중간 정산, 마감 정산 등)을 완료하고 해당 정산 내역 전문을 전송할 때 자동으로 신규 레코드가 생성(Insert)됩니다.",
            "memo_u": "정산 이력의 투명성과 회계 감사 목적상 한 번 적재된 정산 데이터는 인위적으로 수정하지 않는 것을 원칙으로 하며, 수정 사유 발생 시 보정 데이터를 전송하거나 재정산 전문을 통해 신규 적재합니다.",
            "memo_d": "세무 및 회계 감사 자료 보존 기한 준수를 위해 데이터 물리 삭제(Hard Delete)는 엄격히 금지되며, 일정 기간 경과 후 아카이빙 배치 프로세스에 의해서만 분할 삭제됩니다.",
            "memo_r": "백오피스 매장 매출 정산 조회 화면(예: 포스별 정산 현황, 일자별 과부족 현황) 및 현금 시재 확인 등 정산 대조 분석을 위해 조회됩니다."
        }
        
    saregitb = tables["saregitb"]
    
    # Add/Update related_tables with all verified related tables
    saregitb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] SAREGITB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 정산 내역이 발생한 가맹점 매장의 세부 정보 및 소속 브랜드 체인을 확인합니다."
        },
        {
            "table_name": "sdailytb",
            "description": "[가맹점 일 매출 집계] 포스별 교대/일정산 내역을 일자별, 매장별로 합산하여 가맹점 일 매출 집계 데이터(SDAILYTB)와 과부족(시재 편차) 검증 대조를 수행하기 위해 연동됩니다."
        },
        {
            "table_name": "scdlogtb",
            "description": "[신용카드 승인 로그] 정산 내역에 기록된 신용카드 승인 총액(CARD_AMT) 및 건수(CARD_CNT)와 개별 신용카드 승인 상세 로그(SCDLOGTB) 간의 금액/건수 일치 여부를 대조 검증하기 위해 조인 연계됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with saregitb details!")
        
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
