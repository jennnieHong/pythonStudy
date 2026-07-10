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
    if "mpospgtb" not in tables:
        print("mpospgtb key not found in tables. Initializing...")
        tables["mpospgtb"] = {
            "memo": "POS에서 실적 조회하는 프로그램 관리 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 POS에서 실적 조회하는 프로그램 관리 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mpospgtb = tables["mpospgtb"]
    
    # Add/Update related_tables
    mpospgtb["related_tables"] = [
        {
            "table_name": "mmspostb",
            "description": "[매장별 POS 마스터] MPOSPGTB에 등록된 실적 조회용 프로그램(웹앱)은 개별 매장의 POS 단말기(MMSPOSTB) 환경에서 구동되므로, 단말기별 프로그램 기능 활성화 및 배포 상태를 통제하는 연계 관계를 갖습니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] POS 실적 조회 프로그램 정보의 추가, 명칭 변경, 실행 경로(PHP_PATH) 수정 등의 CUD 발생 시 변경 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mpospgtb related_tables!")
        
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
