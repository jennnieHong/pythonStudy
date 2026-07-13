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
    if "msubmntb" not in tables:
        print("msubmntb key not found in tables. Initializing...")
        tables["msubmntb"] = {
            "memo": "매장별 부가주문내역 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 매장별 부가주문내역 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    msubmntb = tables["msubmntb"]
    
    # Add/Update related_tables with all verified related tables in the submenu configuration
    msubmntb["related_tables"] = [
        {
            "table_name": "mmbumstb",
            "description": "[매장 부가메뉴 분류 마스터] MSUBMNTB.MS_NO = MMBUMSTB.MS_NO AND MSUBMNTB.CLPLU_CD = MMBUMSTB.CLPLU_CD 조인을 통해 부가메뉴 대분류 카테고리 정보와 개별 상세 부가 상품(서브메뉴) 지정 목록을 1:N 관계로 결합 관리합니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] MSUBMNTB.MS_NO = MGOODSTB.MS_NO AND MSUBMNTB.GOODS_CD = MGOODSTB.GOODS_CD 조인을 통해 부가메뉴에 추가된 원자재/서브 상품의 한글 명칭 및 규격을 연계 노출합니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 부가메뉴 상세 목록 조회(selectGoodsKeyList) 시 필수 선택 속성 코드 등의 공통 코드 한글 해석 명칭을 조인하여 가져옵니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MSUBMNTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 POS 터치키 부가메뉴 설정을 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [POS 부가메뉴 등록 (hq_master_00009)] 등의 화면에서 부가 메뉴 항목을 새로 추가(insertGoodsKey), 순서 수정, 또는 삭제(deleteGoodsKey) 시 변경 감사 이력을 MMSLOGTB에 실시간 기록합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with msubmntb details!")
        
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
