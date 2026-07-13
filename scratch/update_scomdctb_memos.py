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
    if "scomdctb" not in tables:
        print("scomdctb key not found in tables. Initializing...")
        tables["scomdctb"] = {
            "memo": "본사 제휴 할인 카드/업체 마스터의 POS 단말기 송신용 대기(동기화) 테이블입니다. (Partnership Company POS Sync Log)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "본사 제휴사 마스터 테이블(TCOMDCTB)에 신규 제휴 카드가 등록되거나 수정/삭제될 때, 실시간 동기화 트리거(Tr_TCOMDCTB_T01)가 작동하여 POS 송신용 변경 이력 데이터를 SCOMDCTB에 자동으로 삽입(Insert)합니다.",
            "memo_u": "POS 전송 대기 및 이력 관리를 목적으로 설계되었으므로, 적재된 레코드에 대한 수동 업데이트 작업은 발생하지 않습니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 전송 완료된 오래된 로그는 시스템 데이터 보존 정책에 따라 정기 배치(Hard Delete)를 통해 비워집니다.",
            "memo_r": "POS 단말기가 마스터 동기화(Telex S10 / M26)를 요청할 때, 아직 동기화되지 않은 최종 제휴 카드사 명세 및 할인율 설정을 내려주기 위해 조회됩니다."
        }
        
    scomdctb = tables["scomdctb"]
    
    # Add/Update related_tables with all verified related tables
    scomdctb["related_tables"] = [
        {
            "table_name": "tcomdctb",
            "description": "[본사 제휴사 마스터] SCOMDCTB.COMP_CD = TCOMDCTB.COMP_CD 조인을 통해 본사 기준의 원본 제휴 카드사 정보 및 제휴 혜택 마스터 데이터를 연결합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] SCOMDCTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 특정 매장에 적용되는 제휴 카드 동기화 여부 및 배포 매장 범위를 확인합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with scomdctb details!")
        
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
