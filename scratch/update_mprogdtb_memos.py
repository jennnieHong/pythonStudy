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
    if "mprogdtb" not in tables:
        print("mprogdtb key not found in tables. Initializing...")
        tables["mprogdtb"] = {
            "memo": "프로모션 대상 상품  테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 프로모션 대상 상품 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mprogdtb = tables["mprogdtb"]
    
    # Add/Update related_tables with all related tables
    mprogdtb["related_tables"] = [
        {
            "table_name": "mpromatb",
            "description": "[매장별 프로모션 마스터] MPROGDTB.MS_NO = MPROMATB.MS_NO AND MPROGDTB.PROMO_CD = MPROMATB.PROMO_CD 조인을 통해 개별 프로모션 행사 정보(기간, 할인 방식, 행사 등급)와 대상 상품 상세 리스트를 N:1 관계로 구성합니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] MPROGDTB.MS_NO = MGOODSTB.MS_NO AND MPROGDTB.GOODS_CD = MGOODSTB.GOODS_CD 조인을 통해 프로모션 할인 대상이 되는 개별 상품의 한글 명칭, 규격 및 표준 단가를 매핑합니다."
        },
        {
            "table_name": "tprogdtb",
            "description": "[체인 프로모션 대상 상품] 본사 브랜드 표준 프로모션 상품 정책 정보를 특정 가맹점(MS_NO) 하위의 매장 프로모션 대상 상품 정보로 복사 배포 및 전파할 때 연계됩니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MPROGDTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 프로모션 대상 상품 정보를 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 특정 프로모션 행사의 대상 상품군 추가, 삭제, 특정 품목의 할인율 커스텀 조정 시 조작 이력을 MMSLOGTB에 실시간 기록합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mprogdtb details!")
        
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
