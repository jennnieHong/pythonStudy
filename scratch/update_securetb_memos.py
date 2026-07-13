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
    if "securetb" not in tables:
        print("securetb key not found in tables. Initializing...")
        tables["securetb"] = {
            "memo": "백오피스 웹 사용자 계정 및 비밀번호 보안 정책 설정 마스터 테이블입니다. (Web Security Policy Master)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "시스템 구축 시 보안 전역 설정용 단일 행 레코드가 기본 데이터베이스 시드(Seed) 스크립트를 통해 생성되며, 별도의 행 추가(Insert)는 원천 배제됩니다.",
            "memo_u": "본사 웹 관리자 화면 [사용자 보안정책 관리 (admin_system_00006)] 화면에서 로그인 실패 제한, 계정 비활성화 주기, 비밀번호 복잡도 등의 설정을 변경 시 업데이트(Update)가 작동합니다.",
            "memo_d": "시스템 전반의 로그인 통제 및 감사 보안 정책 보존을 위해 이 테이블에 대한 데이터 삭제(Delete)는 허용되지 않습니다.",
            "memo_r": "어드민 웹 로그인 시 계정 잠금 여부 확인, 비밀번호 변경 주기 계산, 혹은 비밀번호 복합성 검증 시 전역 기준으로 상시 조회됩니다."
        }
        
    securetb = tables["securetb"]
    
    # Add/Update related_tables with all verified related tables
    securetb["related_tables"] = [
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 사용자 로그인(인증), 비밀번호 복잡도 체크, 혹은 비밀번호 강제 변경 주기(PW_CHANGE_DATE) 계산 시 SECURETB의 전역 보안 정책 설정을 대조하여 위반 여부를 검증합니다."
        },
        {
            "table_name": "loginftb",
            "description": "[로그인 실패 이력 로그] 사용자가 로그인 실패 시 SECURETB.LOGIN_FAIL_LOCK_CNT 설정값과 비교하여 실패 횟수를 카운팅하고, 실패 임계치 도달 시 계정 잠금 처리를 수행하기 위해 연계됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with securetb details!")
        
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
