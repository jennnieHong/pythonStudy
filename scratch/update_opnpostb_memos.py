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
    if "opnpostb" not in tables:
        print("opnpostb key not found in tables. Initializing...")
        tables["opnpostb"] = {
            "memo": "포스 오픈 테이블 테이블입니다. (매장 POS 개시/영업일 관리 마스터)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "매장 POS 트랜잭션 전송 수신 또는 화면 내 업무 전표 저장 처리를 통해 신규 행이 삽입됩니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "일자별 실적 통계 조회, 결산 대시보드 그래프 구성, 그리고 기간별 마감 정산 화면에서 통계 쿼리를 통해 조회됩니다."
        }
        
    opnpostb = tables["opnpostb"]
    
    # Add/Update related_tables with all verified related tables in the POS open/close flow
    opnpostb["related_tables"] = [
        {
            "table_name": "saregitb",
            "description": "[매출 마스터 테이블] checkLoginCnt 쿼리에서 조인되어, 특정 일자 영업 개시를 수행한 POS 기기별로 실제 거래 매출 내역이 발생했는지 시재 체크 시 매핑 조회됩니다."
        },
        {
            "table_name": "mvancotb",
            "description": "[매장 VAN 단말기 마스터] 마감 정산 배치(selectCloseDateMsList) 기동 시, 개시된 포스의 결제 단말기 유효성(TID 계약 상태)을 정합성 검증하기 위해 조인합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] OPNPOSTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 POS 개점 일자 및 개시 상태 대장을 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 웹 백오피스에서 점주나 관리자가 영업일 개점 일자를 강제로 초기화하거나 강제 폐점 조작할 때 조작 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with opnpostb details!")
        
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
