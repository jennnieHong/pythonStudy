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
    if "mrolehtb" not in tables:
        print("mrolehtb key not found in tables. Initializing...")
        tables["mrolehtb"] = {
            "memo": "웹 메뉴 권한 설정 마스터 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 웹 메뉴 권한 설정 마스터 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "사용 여부 컬럼(USE_YN)을 'N'으로 업데이트하여 미사용 처리하는 소프트 삭제(Soft Delete) 방식으로 비활성화합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mrolehtb = tables["mrolehtb"]
    
    # Add/Update related_tables with all verified related tables
    mrolehtb["related_tables"] = [
        {
            "table_name": "mroledtb",
            "description": "[웹 메뉴 권한 설정 마스터 상세] MROLEHTB.ROLE_CD = MROLEDTB.ROLE_CD 조인을 통해 권한 그룹에 포함된 개별 웹 메뉴 목록 및 각 메뉴별 CRUD 상세 조작 권한(조회, 저장, 삭제 등) 설정을 1:N 관계로 지정합니다."
        },
        {
            "table_name": "usermltb",
            "description": "[사용자별 메뉴 권한 매핑] 사원관리(admin_emp_00001 등) 화면에서 사원에게 특정 웹 권한 그룹(ROLE_CD)을 매핑(insertUserRole / updateUserRole)할 때 헤더 정보를 연동합니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 권한 설정 메인 그리드 조회(getRoleHeaderList) 시, 권한 그룹을 생성하거나 최종 수정한 작업자(user_id)의 한글 성명과 부서를 조인 매핑하여 화면에 노출합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [웹 메뉴 권한 설정 마스터관리 (hq_master_00022)] 화면 등에서 권한 그룹 헤더 신규 등록(saveMenuMaster), 마스터 수정, 또는 권한 삭제(deleteMenuMasterHeader) 조작 발생 시 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mrolehtb details!")
        
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
