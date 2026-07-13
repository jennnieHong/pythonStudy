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
    if "obreqdtb" not in tables:
        print("obreqdtb key not found in tables. Initializing...")
        tables["obreqdtb"] = {
            "memo": "구매의뢰-DETAIL 테이블입니다. (매장별 거래처 발주 상세)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 구매의뢰-DETAIL 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    obreqdtb = tables["obreqdtb"]
    
    # Add/Update related_tables with all verified related tables in the order request detail flow
    obreqdtb["related_tables"] = [
        {
            "table_name": "obreqhtb",
            "description": "[발주서 마스터 헤더] OBREQDTB.REQ_DATE = OBREQHTB.REQ_DATE AND OBREQDTB.REQ_SEQ = OBREQHTB.REQ_SEQ 조인을 통해 발주서 마스터 헤더 정보와 세부 발주 품목 상세 내역을 1:N 관계로 묶어 줍니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] OBREQDTB.GOODS_CD = MGOODSTB.GOODS_CD 조인을 통해 발주 신청된 상품(원자재)의 표준 사양, 한글 명칭, 바코드 정보를 연동 조회합니다."
        },
        {
            "table_name": "tgoodstb",
            "description": "[체인 상품 마스터] 체인 레벨의 원천 상품 표준 규격 및 마스터 사양 조회를 위해 조인합니다."
        },
        {
            "table_name": "mvndrmtb",
            "description": "[매장별 거래처 마스터] 발주 상세 품목을 납품할 계약 매장 거래처 정보를 연계 조회하기 위해 조인합니다."
        },
        {
            "table_name": "tvndrmtb",
            "description": "[본사 거래처 마스터] 본사 직속 계약 거래처 정보를 대조하기 위해 조인합니다."
        },
        {
            "table_name": "mvndrgtb",
            "description": "[거래처 취급상품] 발주 등록 시, 거래처가 실제 취급 가능한 승인된 납품 품목인지 유효성을 검증하기 위해 조인(getNotReqGoodsList)합니다."
        },
        {
            "table_name": "tpricetb",
            "description": "[체인 단가 마스터] 발주 등록 시 적용될 거래처별 계약 매입 단가 정보를 대조하고 정합성을 검증하기 위해 조인합니다."
        },
        {
            "table_name": "obslphtb",
            "description": "[납품서 헤더 마스터] 발주 확정 건에 대해 거래처가 실제로 매장으로 납품을 완료하여 입고 전표를 생성하고 대조할 때 발주 대비 실입고량 검수 조회를 위해 조인합니다."
        },
        {
            "table_name": "obslpdtb",
            "description": "[납품 상세 로그] 입고 전표 및 반품 전표 생성 시 발주 수량과 입고 수량의 편차를 계산하기 위해 조인합니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 발주 상품의 진행 상태 코드(발주 요청, 발주 승인, 입고 완료 등)의 공통 한글 명칭을 조인 조회합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] OBREQDTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 발주 상세 정보를 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [구매의뢰요청관리 (hq_vendor_00001)] 화면 등에서 관리자가 발주 상세 항목을 추가(addRequestGoods), 수정, 혹은 삭제(deleteRequestGoods) 시 조작 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with obreqdtb details!")
        
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
