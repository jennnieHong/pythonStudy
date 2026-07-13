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
    
    # Initialize/Update scnlhdtb
    if "scnlhdtb" not in tables:
        print("scnlhdtb key not found in tables. Initializing...")
        tables["scnlhdtb"] = {
            "memo": "결제 승인 처리 전에 판매 등록 과정에서 발생한 거래 취소(반려/취소) 헤더 테이블입니다. (Void before Payment Header)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "POS 단말기에서 사용자가 주문 항목들을 입력한 후 결제 완료 전에 전체 주문을 취소(Void)하면 해당 취소 거래 내역 전문(Telex/웹 API)이 전송되어 신규 레코드가 자동 생성(Insert)됩니다.",
            "memo_u": "취소 이력의 감사 추적 목적상 이미 생성된 결제 전 취소 헤더 레코드는 원칙적으로 수정하지 않습니다.",
            "memo_d": "세무 및 감사 자료 보존 정책에 따라 물리 삭제는 금지하며, 일정 보존 기간 만료 후 아카이빙 정리 배치에 의해서만 데이터가 정리됩니다.",
            "memo_r": "백오피스 매출 현황 조회 및 거래 예외 분석 화면(예: 결제전 취소 내역 조회, 캐셔별 거래 반려 분석)에서 거래 취소 요약 현황을 조회하기 위해 사용됩니다."
        }
    else:
        # Just update if it exists
        tables["scnlhdtb"].update({
            "memo": "결제 승인 처리 전에 판매 등록 과정에서 발생한 거래 취소(반려/취소) 헤더 테이블입니다. (Void before Payment Header)",
            "memo_c": "POS 단말기에서 사용자가 주문 항목들을 입력한 후 결제 완료 전에 전체 주문을 취소(Void)하면 해당 취소 거래 내역 전문(Telex/웹 API)이 전송되어 신규 레코드가 자동 생성(Insert)됩니다.",
            "memo_u": "취소 이력의 감사 추적 목적상 이미 생성된 결제 전 취소 헤더 레코드는 원칙적으로 수정하지 않습니다.",
            "memo_d": "세무 및 감사 자료 보존 정책에 따라 물리 삭제는 금지하며, 일정 보존 기간 만료 후 아카이빙 정리 배치에 의해서만 데이터가 정리됩니다.",
            "memo_r": "백오피스 매출 현황 조회 및 거래 예외 분석 화면(예: 결제전 취소 내역 조회, 캐셔별 거래 반려 분석)에서 거래 취소 요약 현황을 조회하기 위해 사용됩니다."
        })
        
    tables["scnlhdtb"]["related_tables"] = [
        {
            "table_name": "scnldttb",
            "description": "[결제전 취소 상세] SCNLHDTB.MS_NO = SCNLDTTB.MS_NO AND SCNLHDTB.SALE_DATE = SCNLDTTB.SALE_DATE AND SCNLHDTB.POS_NO = SCNLDTTB.POS_NO AND SCNLHDTB.CANCEL_NO = SCNLDTTB.CANCEL_NO 조인을 통해 취소된 거래의 헤더 정보와 상세 취소 상품 내역을 1:N 관계로 연계합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] SCNLHDTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 거래 취소가 발생한 매장의 가맹점 마스터 정보를 확인합니다."
        }
    ]

    # Initialize/Update scnldttb
    if "scnldttb" not in tables:
        print("scnldttb key not found in tables. Initializing...")
        tables["scnldttb"] = {
            "memo": "결제 승인 처리 전에 판매 등록 과정에서 발생한 거래 취소(반려/취소) 상세 상품 정보 테이블입니다. (Void before Payment Detail)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "POS 단말기 결제 전 취소 거래가 접수되면, 헤더 데이터(scnlhdtb) 생성 시 취소된 상품 단위 개별 명세가 자동으로 상세 레코드로 동시 생성(Insert)됩니다.",
            "memo_u": "취소 상세 내역의 무결성을 위해 개별 레코드의 속성 수정은 허용하지 않습니다.",
            "memo_d": "헤더 테이블과 동일하게 물리 삭제는 엄격히 금지되며, 연관 정리 배치 프로세스에 의해서만 Hard Delete가 실행될 수 있습니다.",
            "memo_r": "결제전 취소 영수증 복원 조회 및 취소 상품별 통계 화면에서 개별 취소 품목과 수량을 대조하기 위해 조회됩니다."
        }
    else:
        # Just update if it exists
        tables["scnldttb"].update({
            "memo": "결제 승인 처리 전에 판매 등록 과정에서 발생한 거래 취소(반려/취소) 상세 상품 정보 테이블입니다. (Void before Payment Detail)",
            "memo_c": "POS 단말기 결제 전 취소 거래가 접수되면, 헤더 데이터(scnlhdtb) 생성 시 취소된 상품 단위 개별 명세가 자동으로 상세 레코드로 동시 생성(Insert)됩니다.",
            "memo_u": "취소 상세 내역의 무결성을 위해 개별 레코드의 속성 수정은 허용하지 않습니다.",
            "memo_d": "헤더 테이블과 동일하게 물리 삭제는 엄격히 금지되며, 연관 정리 배치 프로세스에 의해서만 Hard Delete가 실행될 수 있습니다.",
            "memo_r": "결제전 취소 영수증 복원 조회 및 취소 상품별 통계 화면에서 개별 취소 품목과 수량을 대조하기 위해 조회됩니다."
        })
        
    tables["scnldttb"]["related_tables"] = [
        {
            "table_name": "scnlhdtb",
            "description": "[결제전 취소 헤더] SCNLDTTB.MS_NO = SCNLHDTB.MS_NO AND SCNLDTTB.SALE_DATE = SCNLHDTB.SALE_DATE AND SCNLDTTB.POS_NO = SCNLHDTB.POS_NO AND SCNLDTTB.CANCEL_NO = SCNLHDTB.CANCEL_NO 조인을 통해 개별 상품 취소 내역에 대한 거래자 정보 및 일시 등 마스터 요약 정보를 연계합니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] SCNLDTTB.GOODS_CD = MGOODSTB.GOODS_CD 조인을 통해 취소된 개별 상품의 한글 명칭 및 품목 규격 정보를 화면에 노출하기 위해 연동됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with scnlhdtb and scnldttb details!")
        
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
