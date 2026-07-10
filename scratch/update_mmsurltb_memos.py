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
    if "mmsurltb" not in tables:
        print("mmsurltb key not found in tables. Initializing...")
        tables["mmsurltb"] = {
            "memo": "가맹점별 Daemon URL 관리 MASTER 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 가맹점별 Daemon URL 관리 MASTER 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mmsurltb = tables["mmsurltb"]
    
    # Add/Update related_tables
    mmsurltb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MMSURLTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 외부 통신 연동용 데몬 서버의 API 주소(URL, 포트, 상태)를 관리합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 매장별 데몬 연동 주소 변경, 복구, 또는 서버 교체 등의 CUD 발생 시 변경 이력을 기록하여 관리자 감사 경로를 보장합니다."
        },
        {
            "table_name": "msndnotb",
            "description": "[메시지 전송 및 알림 마스터] 가맹점별 데몬 통신 연동 에러 또는 서비스 알림 전송 실패 시 해당 매장의 데몬 주소 정보를 참조하여 통신 복구를 시도합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mmsurltb related_tables!")
        
        # Automatically run generate_table_dictionary.py to compile HTML
        gen_script = r"D:\hmTest\backoffice\QaReport\generate_table_dictionary.py"
        if os.path.exists(gen_script):
            print("Auto-running generate_table_dictionary.py to rebuild HTML...")
            subprocess.run([sys.executable, gen_script], check=True)
            print("Successfully regenerated hms_db_dictionary.html!")
        else:
            print(f"Generator script not found: {gen_script}")
    except Exception as e:
        print(f"Error saving JSON or generating HTML: {e}")

if __name__ == '__main__':
    update_memos()
