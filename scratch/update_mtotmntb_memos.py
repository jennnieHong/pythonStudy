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
    if "mtotmntb" not in tables:
        print("mtotmntb key not found in tables. Initializing...")
        tables["mtotmntb"] = {
            "memo": "전체주문내역 테이블입니다. (주문 시 요구사항 관리용 마스터)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 주문 시 요구사항 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mtotmntb = tables["mtotmntb"]
    
    # Add/Update related_tables with all verified related tables in the order requirement flow
    mtotmntb["related_tables"] = [
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] 특정 주문 요구사항(예: '샷 추가', '얼음 많이' 등)이 적용 가능한 상품 유형을 판별하고 매핑하기 위해 GOODS_CD 기준으로 조인하여 연동합니다."
        },
        {
            "table_name": "stotmntb",
            "description": "[체인 주문요구사항 마스터] 본사 브랜드 표준 주문요구사항 설정 정보를 가맹점(MS_NO) 하위의 매장 요구사항 테이블(MTOTMNTB)로 동기화(복사 배포) 및 전파할 때 연계됩니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MTOTMNTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 주문 요구사항 마스터 정보를 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [주문요구사항관리 (st_master_00004)] 화면 등에서 관리자가 주문 요구사항 항목을 새로 등록(insert), 내용 수정, 또는 삭제할 시 조작 이력을 MMSLOGTB에 실시간 기록합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mtotmntb details!")
        
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
