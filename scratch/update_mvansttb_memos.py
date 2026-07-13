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
    if "mvansttb" not in tables:
        print("mvansttb key not found in tables. Initializing...")
        tables["mvansttb"] = {
            "memo": "VAN 카드사 대비 표준카드사 정보 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 VAN 카드사 대비 표준카드사 정보 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mvansttb = tables["mvansttb"]
    
    # Add/Update related_tables with all verified related tables in the VAN mapping flow
    mvansttb["related_tables"] = [
        {
            "table_name": "vanmsttb",
            "description": "[VAN사 마스터] MVANSTTB.VAN_CD = VANMSTTB.VAN_CD 조인을 통해 개별 VAN사별 규격 코드와 표준 카드사 연동 매핑 정보를 1:N으로 연결합니다."
        },
        {
            "table_name": "mcardmtb",
            "description": "[신용카드사 코드 마스터] VAN사 고유 카드사 분류 코드와 표준 카드사 마스터(MCARDMTB.CARD_CD) 코드를 조인(selectVanCardList)하여 화면에 한글 표준카드사 명칭을 노출해 줍니다."
        },
        {
            "table_name": "scdlogtb",
            "description": "[신용카드 승인 이력 로그] 결제 완료된 영수증 정보 조회 시, 개별 영수증 승인 카드사 코드를 표준 카드사 한글명으로 치환하기 위해 getCreditBillCardInfo 쿼리에서 조인 참조됩니다."
        },
        {
            "table_name": "weasdttb",
            "description": "[외상 결제 상세 로그] 외상 및 각종 비신용카드 간편 결제 로그에서 승인 카드사 코드와의 정합성 검증 시 조인 대조됩니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [VAN 카드사 정보 등록관리] 화면에서 카드사 매핑 추가(insertVanCard), 수정(updateVanCard), 혹은 삭제(deleteVanCard) 시 조작 이력을 MMSLOGTB에 실시간 기록합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mvansttb details!")
        
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
