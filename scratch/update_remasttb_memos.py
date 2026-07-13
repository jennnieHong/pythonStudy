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
    if "remasttb" not in tables:
        print("remasttb key not found in tables. Initializing...")
        tables["remasttb"] = {
            "memo": "POS 마스터 데이터 재수신(재전송) 요청을 관리하는 테이블입니다. (Master Re-download Registration Table)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자가 백오피스 웹 화면(예: POS 마스터 재전송 요청 화면)에서 특정 매장 및 POS 단말기에 대해 특정 마스터 전문의 재전송을 요청하면 신규 요청 레코드가 생성(Insert)됩니다.",
            "memo_u": "데이터의 직접적인 업데이트 보다는 처리 완료 시 처리 여부(PROC_YN)를 'Y'로 갱신하고 최종 처리 일시(LAST_DTIME)를 업데이트합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 처리 완료 상태(PROC_YN = 'Y') 보존 후 백업 정책에 따라 정기 정리 배치에서 Hard Delete 처리될 수 있습니다.",
            "memo_r": "POS 단말기가 기동하거나 매장 마스터 동기화(Telex S10)를 요청할 때, 재전송 요청 대기 건(PROC_YN = 'N')이 존재하는지 조회하여 우선 동기화 대상으로 바인딩하기 위해 조회됩니다."
        }
        
    remasttb = tables["remasttb"]
    
    # Add/Update related_tables with all verified related tables
    remasttb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] REMASTTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 재전송을 요청한 가맹점 매장의 세부 정보 및 소속 브랜드 체인을 확인합니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 마스터 재전송 요청을 등록한 사용자(CREATE_ID) 정보를 매핑하여 감사 추적 및 이력 관리에 사용합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with remasttb details!")
        
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
