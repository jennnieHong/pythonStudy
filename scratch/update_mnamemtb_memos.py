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
    if "mnamemtb" not in tables:
        print("mnamemtb key not found in tables. Initializing...")
        tables["mnamemtb"] = {
            "memo": "시스템-명칭 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 시스템-명칭 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mnamemtb = tables["mnamemtb"]
    
    # Add/Update related_tables with ALL verified related tables grouped by business domain
    mnamemtb["related_tables"] = [
        {
            "table_name": "mnamestb",
            "description": "[시스템 상세 명칭 마스터] MNAMEMTB.NM_CD = MNAMESTB.NM_CD 조인을 통해 명칭 대분류(그룹) 코드 하위에 소속되는 실제 상세 명칭 코드(소분류)들을 1:N으로 연결하여 전체 시스템 공통 코드 체계를 구성합니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] 상품의 속성 코드(과세구분, 단품구분 등)를 명칭 코드 테이블과 매핑하여 조회 시 동적 한글 속성 명칭을 매핑 및 노출합니다."
        },
        {
            "table_name": "tgoodstb",
            "description": "[체인 상품 마스터] 체인 레벨의 원부자재/상품 표준 사양 조회 시 속성 공통 코드를 표준 명칭으로 치환하기 위해 참조합니다."
        },
        {
            "table_name": "mpricetb",
            "description": "[매장별 상품 단가] 매장별 가격의 책정 성격 및 단가 유형(포장 단가, 배달 단가 등) 한글 코드 명칭을 매핑합니다."
        },
        {
            "table_name": "tpricetb",
            "description": "[체인 단가 마스터] 체인 레벨 표준 가격의 적용 타입 및 적용 조건 코드 번역을 위해 조인합니다."
        },
        {
            "table_name": "tb_recipe",
            "description": "[상품 레시피 마스터] 레시피 구분(반제품/완제품/원자재 등)의 구분 코드를 한글 명칭으로 변환하기 위해 조인합니다."
        },
        {
            "table_name": "tb_recipe_goods_history",
            "description": "[레시피 변경 이력] 레시피의 변동 구분, 상태 값 등 코드의 변경 이력 추적 시 코드 정보를 매칭합니다."
        },
        {
            "table_name": "imcriotb",
            "description": "[매장별 현재고 마스터] 재고의 상태 코드, 보관 유형, 재고 성격 코드(양품, 불량 등)를 공통 코드 테이블과 매핑하여 해석합니다."
        },
        {
            "table_name": "imrealtb",
            "description": "[매장별 재고 실사] 재고 조사 시 실사 구분, 조정 사유 코드(도난, 파손, 유통기한 등)의 한글 명칭 조인 시 사용됩니다."
        },
        {
            "table_name": "imddiotb",
            "description": "[일수불 실적 테이블] 일일 수불 거래 유형 코드(입고, 출고, 반품, 폐기 등)를 한글로 변환하기 위해 대조 조회합니다."
        },
        {
            "table_name": "immmiotb",
            "description": "[월수불 실적 테이블] 월간 재고 입출고 마감 유형 및 조정 유형 등 코드의 상세 이름을 조인 매핑합니다."
        },
        {
            "table_name": "imdusetb",
            "description": "[매장별 폐기 마스터] 폐기 사유(유통기한 경과, 보관 부주의, 파손 등) 코드의 한글 정의를 조회 화면에 바인딩합니다."
        },
        {
            "table_name": "strndttb",
            "description": "[매출 상세 테이블] 주문 채널, 결제 유형, 프로모션 할인 형태 등의 공통 코드 한글 해석 명칭을 조인하여 리포트를 구성합니다."
        },
        {
            "table_name": "obreqhtb",
            "description": "[발주 마스터 테이블] 가맹점 발주 진행 상태(발주요청, 확정, 입고완료 등) 및 배송 방식 코드의 한글 명칭 매핑에 조인됩니다."
        },
        {
            "table_name": "obslphtb",
            "description": "[납품 마스터 테이블] 납품/출고 처리 단계 코드, 차량 배정 구분 등 코드값들의 한글 명칭 해석 조인에 사용됩니다."
        },
        {
            "table_name": "mvndrmtb",
            "description": "[거래처 마스터 테이블] 거래처 성격 구분, 결제 조건, 거래 상태(거래중, 중단) 코드의 한글 명칭 해석 시 참조합니다."
        },
        {
            "table_name": "mmsclstb",
            "description": "[매장별 상품 분류] 상품의 대분류, 중분류, 소분류 카테고리의 한글 코드 표준 명칭을 매핑 및 결합합니다."
        },
        {
            "table_name": "mversmtb",
            "description": "[패치 버전 마스터] 포스 패치 버전의 상태 코드, 장비 구분 코드의 한글 정의 조인에 사용됩니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 사용자 직무, 직급, 시스템 로그인 등급 등의 코드 값을 조인하여 관리자 화면에 해석 명칭으로 뿌려줍니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 공통 명칭 마스터 대분류 정보의 추가, 수정, 삭제 등의 관리자 조작 행위 발생 시 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mnamemtb details!")
        
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
