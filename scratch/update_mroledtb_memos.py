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
    if "mroledtb" not in tables:
        print("mroledtb key not found in tables. Initializing...")
        tables["mroledtb"] = {
            "memo": "웹 메뉴 권한 설정 마스터 - 메뉴 리스트 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 웹 메뉴 권한 설정 마스터 - 메뉴 리스트 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mroledtb = tables["mroledtb"]
    
    # Add/Update related_tables with all verified related tables
    mroledtb["related_tables"] = [
        {
            "table_name": "mrolehtb",
            "description": "[웹 메뉴 권한 설정 마스터 헤더] MROLEDTB.ROLE_CD = MROLEHTB.ROLE_CD 조인을 통해 권한 그룹 마스터 헤더 정보와 해당 그룹에 귀속된 상세 개별 메뉴별 권한(조회, 저장, 삭제 여부) 정보를 1:N으로 결합합니다."
        },
        {
            "table_name": "usermltb",
            "description": "[사용자별 메뉴 권한 매핑] 특정 사원/사용자 계정에 권한 그룹(ROLE_CD)을 할당(insertUserRole / updateUserRole)하여 개별 사용자가 최종적으로 로그인 후 접근 가능한 메뉴 권한을 바인딩합니다."
        },
        {
            "table_name": "menummtb",
            "description": "[웹 메뉴 마스터] MROLEDTB.MENU_CD = MENUMMTB.MENU_CD 조인을 통해 권한 그룹에 소속된 실제 웹 화면 메뉴의 영문/한글 명칭, 실행 파일 경로를 매치하여 화면 접근을 제어합니다."
        },
        {
            "table_name": "menulctb",
            "description": "[메뉴 대분류 마스터] 권한 트리 뷰 구성 또는 그룹별 메뉴 리스트 필터링 시 대분류 레벨의 코드 명칭을 조인 조회하기 위해 연동합니다."
        },
        {
            "table_name": "menumctb",
            "description": "[메뉴 중분류 마스터] 메뉴 트리 구조에 따른 권한 통제 목록을 화면에 그릴 때 중분류 레벨의 코드 명칭을 조인 조회하기 위해 참조합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [웹 메뉴 권한 설정 마스터관리 (hq_master_00022)] 등에서 이루어지는 권한 그룹별 메뉴 추가(addMenu), 세부 권한 변경, 메뉴 삭제(deleteMenu) 시 조작 이력을 MMSLOGTB에 기록합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mroledtb details!")
        
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
