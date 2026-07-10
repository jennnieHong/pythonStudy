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
    if "mmstbltb" not in tables:
        print("mmstbltb key not found in tables. Initializing...")
        tables["mmstbltb"] = {
            "memo": "매장별 테이블 마스터 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "테이블 관리 화면에서 점포 내 구역별 테이블 정보(테이블 코드, 테이블명, 위치 좌표 등)를 등록할 때 신규 레코드가 생성됩니다.",
            "memo_u": "화면을 통해 테이블 명칭, 사용 여부, 배치 상태(좌표 등)를 수정하여 저장 시 업데이트가 수행됩니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "테이블별 주문 등록, 정산/마감 정보 수집, 그리고 일자별 테이블 매출 현황 조회 시 조인 기준으로 널리 조회됩니다."
        }
        
    mmstbltb = tables["mmstbltb"]
    
    # Add/Update related_tables
    mmstbltb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MMSTBLTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 주문용 테이블 배치 마스터 정보를 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 테이블 신규 등록, 배치 위치 이동, 구역 변경 등 테이블 마스터 정보의 CUD 행위 발생 시 감사 이력 로그를 MMSLOGTB에 저장합니다."
        },
        {
            "table_name": "saregitb",
            "description": "[매출 거래 실적 마스터] 일자별 주문 취소나 테이블그룹/테이블별 매출 실적 분석 시 테이블 코드 조인을 통해 분석 통계를 제공합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mmstbltb related_tables!")
        
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
