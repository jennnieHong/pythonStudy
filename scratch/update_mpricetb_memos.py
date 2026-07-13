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
    if "mpricetb" not in tables:
        print("mpricetb key not found in tables. Initializing...")
        tables["mpricetb"] = {
            "memo": "매장별 단가 관리 MASTER 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 매장별 단가 관리 MASTER 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mpricetb = tables["mpricetb"]
    
    # Add/Update related_tables with all verified related tables
    mpricetb["related_tables"] = [
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] 단가 정보의 기준이 되는 매장별 상품 테이블로, GOODS_CD 조인을 통해 각 상품별 정상 판매가, 할인 한계가 등을 연계 관리합니다."
        },
        {
            "table_name": "tpricetb",
            "description": "[체인 단가 마스터] 본사/체인 표준 단가 마스터로, 신규 매장 오픈이나 단가 일괄 배포/적용 정책 실행 시 매장별 단가(MPRICETB) 테이블로 복사 및 매핑됩니다."
        },
        {
            "table_name": "tgoodstb",
            "description": "[체인 상품 마스터] 본사 체인 표준 상품 규격과 단가 마스터를 비교하고 검증하기 위해 조인합니다."
        },
        {
            "table_name": "mmcplktb",
            "description": "[매장별 POS 터치키패드 배치] POS 터치키 상품 지정 및 상세 정보(단가 포함) 노출 화면에서 터치키에 할당된 개별 상품의 단가를 동적 조회하기 위해 조인됩니다."
        },
        {
            "table_name": "tmcplktb",
            "description": "[체인 POS 터치키패드 배치] 체인 표준 터치키 레이아웃 생성 및 상품별 단가 정보 연쇄 조회 시 조인됩니다."
        },
        {
            "table_name": "mmssrctb",
            "description": "[매장별 레시피 소스 마스터] 소스 구성에 소속된 상품의 단가를 참조하여 최종 상품 레시피의 소스 원가 산출 및 비율 분석 시 조인됩니다."
        },
        {
            "table_name": "tmssrctb",
            "description": "[체인 레시피 소스 마스터] 체인 표준 레시피 소스 원가 비율 대조 분석 시 조인 연계됩니다."
        },
        {
            "table_name": "imrealtb",
            "description": "[매장별 재고 실사] 재고 조사 시 실사 차이 수량에 대해 실제 재고 단가를 곱하여 총 실사 조정 금액(재고 자산 가액)을 산출할 때 조인됩니다."
        },
        {
            "table_name": "imdusetb",
            "description": "[매장별 폐기 마스터] 매장 폐기 등록 및 현황 조회 시, 폐기 수량에 상품 단가를 곱해 폐기 손실 총액(금액)을 동적 환산하기 위해 조인합니다."
        },
        {
            "table_name": "mmsclstb",
            "description": "[매장별 상품 분류] 상품 단가 조회 시 대/중/소분류 표준 분류명과 결합하여 카테고리별 단가 현황을 노출합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MPRICETB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 상품 판매 단가 정보를 분할 격리하여 연계합니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 단가 정보의 수정 및 생성을 가동한 관리자 정보를 매핑합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 상품 단가 등록, 단가 인상/인하 등 CUD 발생 시의 이력을 감사하기 위해 변경 로그를 MMSLOGTB에 저장합니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 가격 적용 유형(매장 전산용, 포장용, 배달용 등) 코드의 공통 한글 이름을 가져오기 위해 조인합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mpricetb details!")
        
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
