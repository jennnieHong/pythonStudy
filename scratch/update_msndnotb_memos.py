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
    if "msndnotb" not in tables:
        print("msndnotb key not found in tables. Initializing...")
        tables["msndnotb"] = {
            "memo": "매장 발신자번호 관리 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 매장 발신자번호 관리 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    msndnotb = tables["msndnotb"]
    
    # Add/Update related_tables with all verified related tables
    msndnotb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MSNDNOTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 특정 가맹점(매장)에 속한 법적으로 허가 및 승인된 SMS 발신용 전화번호 목록을 1:N으로 귀속시켜 관리합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [매장관리 (admin_master_00004)] 화면 등에서 관리자가 특정 매장의 발신자 번호를 추가(insertSendNo), 변경, 혹은 삭제할 시 조작 이력을 MMSLOGTB에 실시간 적재합니다."
        },
        {
            "table_name": "mmsurltb",
            "description": "[가맹점별 데몬 URL] 가맹점 연동 데몬이나 통신 채널을 통해 발신번호 유효성 체크 및 실시간 SMS 발송 처리를 연동 기동할 때 데몬 정보와 함께 연계 조회됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with msndnotb details!")
        
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
