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
    
    # Update/Create mmspostb memo structure and fix broken korean texts
    tables["mmspostb"] = {
        "memo": "매장별 POS 마스터 테이블입니다.",
        "starred": False,
        "color": "none",
        "columns": {},
        "memo_c": "매장별 환경설정 등록 또는 백오피스 POS 장비 관리 화면에서 신규 POS 번호를 추가 입력하여 저장 시 레코드가 생성됩니다.",
        "memo_u": "화면의 POS 설정 수정 폼을 통해 속성 값을 변경하거나 트리거/백엔드 동기화 로직에 의해 수정됩니다.",
        "memo_d": "매출 거래 및 마감 정산과의 참조 무결성을 보장하기 위해 물리적 행 삭제는 지양하며, 폐기 또는 사용 안함 상태로 변경 처리해야 합니다.",
        "memo_r": "각 매장별 POS 단말기 정보, POS별 매출 집계 및 전송 상태 조회 화면에서 콤보박스나 그리드 바인딩 시 참조/조회됩니다.",
        "related_tables": [
            {
                "table_name": "mmembvtb",
                "description": "[매장 환경설정 마스터] 가맹점의 POS 사용 대수 설정에 따라 MMEMBV_T01 트리거 혹은 백엔드 로직에서 MMSPOSTB에 POS 번호(POS_NO)별 신규 행을 자동/수동 생성하거나 동기화합니다. MMSPOSTB.MS_NO = MMEMBVTB.MS_NO 조인 관계를 맺습니다."
            },
            {
                "table_name": "mmembstb",
                "description": "[가맹점 매장 마스터] MMSPOSTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(MS_NO)에 속한 POS 장비들의 마스터 명칭과 상태를 연계 조회하고 관리합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "[웹 변경 이력 로그] POS 장비 정보 생성, 변경 및 폐기 시 변경 감사 로그를 MMSLOGTB에 기록하여 장비 이력을 추적합니다."
            }
        ]
    }
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mmspostb details and corrected broken text!")
        
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
