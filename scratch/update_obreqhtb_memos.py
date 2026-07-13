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
    if "obreqhtb" not in tables:
        print("obreqhtb key not found in tables. Initializing...")
        tables["obreqhtb"] = {
            "memo": "구매의뢰-HEADER 테이블입니다. (매장별 거래처 발주 헤더)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 구매의뢰-HEADER 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "진행 상태 플래그값(PROC_FG) 변경에 따른 비즈니스 단계 처리 혹은 수동 보정 처리가 일어날 때 수량이 변경됩니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    obreqhtb = tables["obreqhtb"]
    
    # Add/Update related_tables with all verified related tables in the order request header flow
    obreqhtb["related_tables"] = [
        {
            "table_name": "obreqdtb",
            "description": "[발주서 상세 품목] OBREQHTB.REQ_DATE = OBREQDTB.REQ_DATE AND OBREQHTB.REQ_SEQ = OBREQDTB.REQ_SEQ 조인을 통해 발주서 마스터 헤더 정보와 세부 발주 품목 상세 내역을 1:N 관계로 묶어 줍니다."
        },
        {
            "table_name": "mvndrmtb",
            "description": "[매장별 거래처 마스터] 발주 요청서의 타깃 매입처(VENDOR) 정보를 조인 조회하여 발주처 상호, 대표자명, 사업자번호 등을 연동 노출합니다."
        },
        {
            "table_name": "tvndrmtb",
            "description": "[본사 거래처 마스터] 본사 통합 계약 거래처 대장을 매칭하기 위해 조인합니다."
        },
        {
            "table_name": "obslphtb",
            "description": "[납품서 헤더 마스터] 발주된 전표 건(REQ_DATE, REQ_SEQ)에 대해 매장 입고/납품 처리(OBSLPHTB)가 일어났을 때, 발주 대비 입고 완료 여부를 대조(selectVendorOrderList)하기 위해 조인합니다."
        },
        {
            "table_name": "obslpdtb",
            "description": "[납품 상세 로그] 발주 상세 내역과 매입 전표 내역의 전수 검수 대조를 수행하여 발주 잔량 및 검수 차이를 추적할 때 조인합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] 발주를 신청한 가맹 매장(MS_NO)의 기본 주소, 전화번호 및 점주 명칭을 조회하기 위해 조인합니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 해당 발주서를 작성, 승인, 혹은 발주 전송을 최종 실행한 관리 사원의 실명을 이력 조회 시 매핑합니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 발주서 진행 구분 상태 코드(PROC_FG: 임시저장, 본사승인, 발주완료 등) 및 배송 상태 공통 코드의 한글 설명을 매핑합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [구매의뢰요청관리 (hq_vendor_00001)] 화면 등에서 관리자가 발주 요청서를 신규 작성(saveRequest), 본사 승인 처리(confirmRequest), 혹은 발주 삭제 시 조작 감사 이력을 MMSLOGTB에 실시간 기록합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with obreqhtb details!")
        
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
