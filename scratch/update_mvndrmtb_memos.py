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
    if "mvndrmtb" not in tables:
        print("mvndrmtb key not found in tables. Initializing...")
        tables["mvndrmtb"] = {
            "memo": "거래선 MASTER 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 거래선 MASTER 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mvndrmtb = tables["mvndrmtb"]
    
    # Add/Update related_tables with all verified related tables in the vendor management flow
    mvndrmtb["related_tables"] = [
        {
            "table_name": "tvndrmtb",
            "description": "[본사 거래처 마스터] 본사 표준 거래처 마스터 테이블입니다. 본사 계약 표준 거래처 설정 내용을 가맹점(MS_NO) 하위의 매장 거래처(MVNDRMTB)로 복사 배포 및 전파할 때 연계됩니다."
        },
        {
            "table_name": "mvndrgtb",
            "description": "[거래처 취급상품] MVNDRMTB.VENDOR = MVNDRGTB.VENDOR 조인을 통해 개별 거래처와 해당 거래처가 공급 및 납품하는 취급 상품(원자재) 목록을 1:N 관계로 묶어 줍니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] 거래처가 공급하는 개별 원부자재/상품의 한글 이름, 규격 및 바코드를 매핑 조회하기 위해 GOODS_CD 기준으로 조인 관계를 갖습니다."
        },
        {
            "table_name": "tgoodstb",
            "description": "[체인 상품 마스터] 체인 레벨의 원부자재/상품 표준 사양 조회 시 거래처 상품 규격 정보를 대조하기 위해 조인합니다."
        },
        {
            "table_name": "mbankmtb",
            "description": "[거래처 거래 은행 마스터] 거래처 계좌번호 및 거래 은행 한글 명칭 조회를 위해 1:1 매칭 조회(getVendorDetail) 조인을 맺습니다."
        },
        {
            "table_name": "strnwetb",
            "description": "[매출 외상 전표 마스터] 외상 결제 대금 회수 및 거래처별 매출 정산 대금 대조 시 조인합니다."
        },
        {
            "table_name": "weasdttb",
            "description": "[외상 결제 상세 로그] 외상 대금 정산 및 기입된 거래처 정보와의 정합성 검증 시 조인합니다."
        },
        {
            "table_name": "obreqhtb",
            "description": "[발주 마스터 테이블] 가맹점이 특정 거래처로 발주 전표를 작성하고 내역을 조회할 때 VENDOR 코드를 조인(getDetailList)합니다."
        },
        {
            "table_name": "obreqdtb",
            "description": "[발주 상세 로그] 발주 상세 내역 조회 및 발주서 구성 시 품목과 매핑하기 위해 조인합니다."
        },
        {
            "table_name": "obslphtb",
            "description": "[납품 마스터 테이블] 거래처로부터 입고/납품 처리 및 반품 처리 시 전표 승인 상태를 대조하기 위해 조인(selectVendorOrderList)합니다."
        },
        {
            "table_name": "obslpdtb",
            "description": "[납품 상세 로그] 납품 상세 내역 조회 및 매입 수량/금액 정산 시 품목과 매핑하기 위해 조인합니다."
        },
        {
            "table_name": "mmsclstb",
            "description": "[매장별 상품 분류] 거래처가 취급하는 상품들의 대/중/소분류 기준명을 조회하여 필터링 화면을 구성할 때 조인합니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 거래처의 거래 상태(거래중, 중단, 정지 등) 및 거래처 유형 공통 코드 한글 정의를 조회할 때 조인 매핑합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MVNDRMTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 거래처 마스터 정보를 분할 격리하여 연계합니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 거래처별 담당 관리 사원의 한글 명칭과 계정을 현황 조회 시 조인 매핑합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 거래처 신규 등록, 계좌 변경, 거래처 사용 중단 등 조작(CUD) 발생 시 감사 로그를 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mvndrmtb details!")
        
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
