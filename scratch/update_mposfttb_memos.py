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
    if "mposfttb" not in tables:
        print("mposfttb key not found in tables. Initializing...")
        tables["mposfttb"] = {
            "memo": "매장용 POS 기능 권한 제어 마스타 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 매장용 POS 기능 권한 제어 마스타 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mposfttb = tables["mposfttb"]
    
    # Add/Update related_tables
    mposfttb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MPOSFTTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 POS 기능 권한(할인, 반품, 서비스 등록 제한 등) 통제 마스터 정보를 분할 관리합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [POS 기능 권한 제어 (admin_system_00003)] 등에서 이루어지는 기능별 허용 레벨이나 등급 변경 등의 조작 감사 기록을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mposfttb related_tables!")
        
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
