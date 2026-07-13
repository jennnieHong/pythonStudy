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
    if "mvndrgtb" not in tables:
        print("mvndrgtb key not found in tables. Initializing...")
        tables["mvndrgtb"] = {
            "memo": "거래선 취급상품 MASTER 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 거래선 취급상품 MASTER 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mvndrgtb = tables["mvndrgtb"]
    
    # Add/Update related_tables with all verified related tables in the vendor goods flow
    mvndrgtb["related_tables"] = [
        {
            "table_name": "mvndrmtb",
            "description": "[매장별 거래처 마스터] MVNDRGTB.VENDOR = MVNDRMTB.VENDOR 조인을 통해 개별 거래처와 해당 거래처가 공급 및 납품하는 취급 상품(원자재) 목록을 1:N 관계로 묶어 줍니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] MVNDRGTB.GOODS_CD = MGOODSTB.GOODS_CD 조인을 통해 거래처 취급 대상이 되는 상품의 표준 사양, 바코드, 한글 명칭 정보를 연동 조회합니다."
        },
        {
            "table_name": "tgoodstb",
            "description": "[체인 상품 마스터] 체인 레벨의 원부자재/상품 표준 사양 조회 시 거래처 취급 상품 규격 정보를 대조하기 위해 조인합니다."
        },
        {
            "table_name": "imcriotb",
            "description": "[매장별 현재고 마스터] 발주 등록(st_vendor_00003) 또는 상품 조회(st_master_00013) 시, 해당 거래처가 납품하는 개별 상품들의 현재 전산 재고량(CUR_QTY)을 함께 조회하여 화면에 뿌려줍니다."
        },
        {
            "table_name": "obreqdtb",
            "description": "[발주 상세 로그] 신규 발주서 등록(getNotReqGoodsList) 시, 해당 거래처가 취급하는 단품 정보를 조인하여 신규 발주 전표의 상세 행 데이터를 생성합니다."
        },
        {
            "table_name": "obslpdtb",
            "description": "[납품 상세 로그] 매장 입고/반품 처리(selectVendorGoodsList) 시, 해당 거래처의 취급 단품 정보를 조인하여 입고/반품 전표의 상세 품목 행 데이터를 생성합니다."
        },
        {
            "table_name": "tpricetb",
            "description": "[체인 단가 마스터] 거래처별 납품 매입 계약 단가 정보를 파싱하고 정합성을 검증하기 위해 조인합니다."
        },
        {
            "table_name": "mmsclstb",
            "description": "[매장별 상품 분류] 거래처 취급 상품 목록에서 카테고리(대/중/소분류)별 상품 필터링 조회를 위해 조인합니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 거래선 취급상품의 유효 상태 코드, 발주 제한 여부 등 공통 코드의 한글 정의를 조회할 때 조인 매핑합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MVNDRGTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 거래처 취급 상품(매입처) 목록을 격리하여 제어합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [st_master_00013] 또는 거래처 관리 화면에서 특정 거래처의 취급 상품을 새로 등록, 수정, 또는 제외(삭제)할 시 조작 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mvndrgtb details!")
        
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
