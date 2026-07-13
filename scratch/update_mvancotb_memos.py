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
    if "mvancotb" not in tables:
        print("mvancotb key not found in tables. Initializing...")
        tables["mvancotb"] = {
            "memo": "매장 VAN사 계약번호 관리 MASTER 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "VAN POS 단말기(TID) 등록 시 생성되며, SVANCOTB 테이블로 연동 데이터가 자동 Insert됩니다.",
            "memo_u": "VAN 단말기 정보 수정 시 동작하며, 변경 사항은 SVANCOTB에 동기화 처리됩니다.",
            "memo_d": "단말기 해지 시 삭제 또는 미사용 상태로 변경됩니다.",
            "memo_r": "POS 매출 결제 시 승인 단말기 정보(TID)를 검증하고 매핑하기 위해 읽어옵니다."
        }
        
    mvancotb = tables["mvancotb"]
    
    # Add/Update related_tables with all verified related tables in the VAN billing flow
    mvancotb["related_tables"] = [
        {
            "table_name": "vanmsttb",
            "description": "[VAN사 마스터] MVANCOTB.VAN_CD = VANMSTTB.VAN_CD 조인을 통해 각 매장별로 제휴/계약된 VAN 대리점 정보 및 승인 시스템 표준 정보를 매핑합니다."
        },
        {
            "table_name": "mmcardtb",
            "description": "[매장 카드사 계약정보] 매장별 VAN 대행 계약 정보를 기준으로, 신용카드 가맹점 번호와 수수료 계약 조건들을 조회(getCardList) 대조 시 연계합니다."
        },
        {
            "table_name": "mcardmtb",
            "description": "[신용카드사 코드 마스터] 매장별 카드 결제 시 승인을 제공한 카드사의 명칭 및 결제 대금 정산 방식을 조인 조회합니다."
        },
        {
            "table_name": "opnpostb",
            "description": "[매장 POS 개시 관리] 마감 인터페이스 및 개점 영업일 정산 검증 시 결제 승인 모듈 단말기 작동 유효성을 매칭하기 위해 조인 조회됩니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MVANCOTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 체결된 단말기 ID(TID) 및 카드 VAN 통신 포트 설정을 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [매장관리 (admin_master_00004)] 화면 등에서 관리자가 특정 매장의 단말기 계약번호 추가(insertPosVan), 정보 수정, 혹은 해제(deleteAllVanPos) 시 조작 감사 로그를 MMSLOGTB에 저장합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mvancotb details!")
        
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
