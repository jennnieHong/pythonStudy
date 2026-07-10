import json
import os
import sys
import subprocess

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
    if "mnamemtb" not in tables:
        print("mnamemtb key not found in tables. Initializing...")
        tables["mnamemtb"] = {
            "memo": "시스템-명칭 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 시스템-명칭 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mnamemtb = tables["mnamemtb"]
    
    # Add/Update related_tables
    mnamemtb["related_tables"] = [
        {
            "table_name": "mnamestb",
            "description": "[시스템 상세 명칭 마스터] MNAMEMTB.NM_CD = MNAMESTB.NM_CD 조인을 통해 명칭 대분류(그룹) 코드 하위에 소속되는 실제 상세 명칭 코드(소분류)들을 1:N으로 연결하여 전체 시스템 공통 코드 체계를 구성합니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] 상품의 속성 코드(과세구분, 단품구분 등)를 명칭 코드 테이블과 매핑하여 조회 시 동적 한글 속성 명칭을 매핑 및 노출합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 공통 명칭 마스터 대분류 정보의 추가, 수정, 삭제 등의 관리자 조작 행위 발생 시 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mnamemtb related_tables!")
        
        # Automatically run generate_table_dictionary.py to compile HTML
        gen_script = r"D:\hmTest\backoffice\QaReport\generate_table_dictionary.py"
        if os.path.exists(gen_script):
            print("Auto-running generate_table_dictionary.py to rebuild HTML...")
            # Run without subprocess.run shell output issues by calling directly
            os.system(f'python "{gen_script}"')
            print("Successfully regenerated hms_db_dictionary.html!")
        else:
            print(f"Generator script not found: {gen_script}")
    except Exception as e:
        print(f"Error saving JSON or generating HTML: {e}")

if __name__ == '__main__':
    update_memos()
