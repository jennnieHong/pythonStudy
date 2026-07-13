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
    
    # Fix description from "발주 DETAIL" to "매장별 거래처 납품/입고 상세"
    tables["obslpdtb"] = {
        "memo": "구매의뢰-DETAIL 테이블입니다. (매장별 거래처 납품/입고 상세)",
        "starred": False,
        "color": "orange",
        "columns": {},
        "memo_c": "사용자 관리자 화면에서 구매의뢰-DETAIL 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
        "memo_u": "진행 상태 플래그값(PROC_FG) 변경에 따른 비즈니스 단계 처리 혹은 수동 보정 처리가 일어날 때 수량이 변경됩니다.",
        "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
        "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
    }
    
    obslpdtb = tables["obslpdtb"]
    
    # Add/Update related_tables with all verified related tables in the delivery/billing detail flow
    obslpdtb["related_tables"] = [
        {
            "table_name": "obslphtb",
            "description": "[납품서 헤더 마스터] OBSLPDTB.SLIP_DATE = OBSLPHTB.SLIP_DATE AND OBSLPDTB.SLIP_SEQ = OBSLPHTB.SLIP_SEQ 조인을 통해 입고/납품 전표 마스터 헤더 정보와 세부 품목별 매입 명세 내역을 1:N 관계로 묶어 줍니다."
        },
        {
            "table_name": "obreqdtb",
            "description": "[발주서 상세 품목] 발주 대비 검수/매입 처리를 기동할 때, 원본 발주 요청서와 매칭하여 발주수량 대비 입고 검수량을 비교/대조하기 위해 조인합니다."
        },
        {
            "table_name": "obreqhtb",
            "description": "[발주서 마스터 헤더] 발주서 헤더 정보와 대조하여 발주 잔량 및 검수 차이를 추적하기 위해 조인합니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] OBSLPDTB.GOODS_CD = MGOODSTB.GOODS_CD 조인을 통해 입고된 원부자재/상품의 한글 이름, 규격 및 바코드 정보를 연동 조회합니다."
        },
        {
            "table_name": "tgoodstb",
            "description": "[체인 상품 마스터] 체인 레벨의 원천 상품 표준 규격 및 마스터 사양 조회를 위해 조인합니다."
        },
        {
            "table_name": "mvndrmtb",
            "description": "[매장별 거래처 마스터] 해당 입고/매입 전표의 공급처(거래처 VENDOR) 정보를 연계 조회하기 위해 조인합니다."
        },
        {
            "table_name": "tvndrmtb",
            "description": "[본사 거래처 마스터] 본사 직속 계약 거래처 대장을 매칭하기 위해 조인합니다."
        },
        {
            "table_name": "tpricetb",
            "description": "[체인 단가 마스터] 입고 시 적용될 계약 매입 단가 정보를 대조하고 정합성을 검증하기 위해 조인합니다."
        },
        {
            "table_name": "imcriotb",
            "description": "[매장별 현재고 마스터] 입고 확정 처리(confirmVendorOrderDt)가 기동되면 매장별 현재고 테이블 IMCRIOTB.CUR_QTY 에 입고 확정 수량만큼 재고를 가산하는 재고 흐름을 연동합니다."
        },
        {
            "table_name": "tsm_cty_buy_dtl",
            "description": "[매입 거래 상세] 매장의 정산 마감 인터페이스 배치 기동 시, 결제 완료된 매입 명세를 tsm_cty_buy_dtl에 밀어넣을 때 원천 데이터로 연계(insertObslDetailPos)됩니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 입고 진행 상태(임시저장, 확정완료 등) 및 구분 코드의 공통 한글 명칭을 조인 조회합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] OBSLPDTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 입고 상세 정보를 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [매장 검수관리 (st_vendor_00002)] 또는 [본사 검수관리 (hq_vendor_00004)] 화면에서 입고 내역을 검수 등록, 수정, 혹은 전표 삭제 시 조작 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with obslpdtb details!")
        
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
