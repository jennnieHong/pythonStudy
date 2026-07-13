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
    if "obslplog" not in tables:
        print("obslplog key not found in tables. Initializing...")
        tables["obslplog"] = {
            "memo": "OBSLPLOG 테이블 정보입니다. (매장별 거래처 납품/입고 전송 로그)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "매장 POS 트랜잭션 전송 수신 또는 화면 내 업무 전표 저장 처리를 통해 신규 행이 삽입됩니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "일자별 실적 통계 조회, 결산 대시보드 그래프 구성, 그리고 기간별 마감 정산 화면에서 통계 쿼리를 통해 조회됩니다."
        }
        
    obslplog = tables["obslplog"]
    
    # Add/Update related_tables with all verified related tables in the delivery/billing transmission flow
    obslplog["related_tables"] = [
        {
            "table_name": "obslphtb",
            "description": "[납품서 헤더 마스터] OBSLPLOG.SLIP_DATE = OBSLPHTB.SLIP_DATE AND OBSLPLOG.SLIP_SEQ = OBSLPHTB.SLIP_SEQ 조인을 통해 입고/납품 전표 마스터 정보와 해당 전표의 POS 전송 이력 및 전송 성공 여부를 1:1 관계로 매치합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] 개별 매장(MS_NO) 기준으로 입고 전송 이력을 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 관리자가 입고 전표 전송을 수동으로 재시도하거나 전송 로그 실패 이력을 초기화할 시 조작 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with obslplog details!")
        
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
