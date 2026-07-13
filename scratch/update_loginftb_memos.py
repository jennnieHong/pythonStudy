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
    if "loginftb" not in tables:
        print("loginftb key not found in tables. Initializing...")
        tables["loginftb"] = {
            "memo": "백오피스 웹 로그인 실패 이력 관리 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자가 백오피스 로그인 시 비밀번호 불일치 등으로 접속에 실패할 때 실패 사유, 시도 IP 및 일시를 기록하기 위해 신규 레코드가 생성됩니다.",
            "memo_u": "로그 적재 전용 수집 테이블로, 최초 생성 후 직접적인 데이터 필드 수정은 발생하지 않고 연동 수신 상태 코드값 등만 업데이트됩니다.",
            "memo_d": "데이터 이력 추적 및 정합성 감사를 위하여, 시스템 설계상 행 삭제(Delete)를 수행하지 않습니다.",
            "memo_r": "특정 계정의 로그인 실패 횟수(최대 5회 제한 등) 누적 여부를 체크하여 계정을 차단(Lock) 처리하기 위해 로그인 인증 프로세스 기동 시 조회됩니다."
        }
        
    loginftb = tables["loginftb"]
    
    # Add/Update related_tables with all related tables
    loginftb["related_tables"] = [
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] LOGINFTB.USER_ID = MUSERSTB.USER_ID 조인을 통해 로그인 시도에 실패한 사용자의 상세 계정 정보(한글 성명, 소속 부서) 및 현재 계정 활성 상태(ACCT_ENABLE)를 매핑해 줍니다."
        },
        {
            "table_name": "loginstb",
            "description": "[사용자 로그인 성공 이력] 로그인 성공 이력을 기록하는 LOGINSTB 테이블과 함께 연계 조회되어, 특정 계정의 비정상 로그인 시도 탐지 및 접속 통계 대장을 구성할 때 교차 참조됩니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 로그인 실패 5회 초과로 인해 계정이 자동 잠금 처리되거나, 관리자가 관리자 화면에서 특정 계정의 잠금 상태를 수동으로 해제하는 조작을 가할 때 감사 이력을 MMSLOGTB에 실시간 기록합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with loginftb related_tables!")
        
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
