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
    if "imtrlgtb" not in tables:
        print("imtrlgtb key not found in tables. Initializing...")
        tables["imtrlgtb"] = {
            "memo": "재고 갱신용 LOG 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "매장 POS 트랜잭션 전송 수신 또는 화면 내 업무 전표 저장 처리를 통해 신규 행이 삽입됩니다.",
            "memo_u": "진행 상태 플래그값(PROC_FG) 변경에 따른 비즈니스 단계 처리 혹은 수동 보정 처리가 일어날 때 수량이 변경됩니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "일자별 실적 통계 조회, 결산 대시보드 그래프 구성, 그리고 기간별 마감 정산 화면에서 통계 쿼리를 통해 조회됩니다."
        }
        
    imtrlgtb = tables["imtrlgtb"]
    
    # Add/Update related_tables with ALL related tables in the inventory transaction flow
    imtrlgtb["related_tables"] = [
        {
            "table_name": "imcriotb",
            "description": "[매장별 현재고 마스터] IMTRLGTB에 실시간 적재된 수불 변동 로그를 기준으로, 매장별 상품의 실시간 전산 현재고량(CUR_QTY)을 가감(+/-) 조정하여 실재고를 갱신합니다."
        },
        {
            "table_name": "imddiotb",
            "description": "[일수불 실적 테이블] DmIMTR01 배치 데몬 프로세스가 기동할 때 IMTRLGTB의 일별 수불 내역을 영업일 단위로 롤업 집계하여 일수불 실적(IMDDIOTB)에 누적 합산합니다."
        },
        {
            "table_name": "immmiotb",
            "description": "[월수불 실적 테이블] DmIMTR01 배치 데몬이 수불 변동 이력을 월 단위로 집계하여 해당월의 입출고 결산 실적(IMMMIOTB)에 누적 갱신 처리합니다."
        },
        {
            "table_name": "imtrbktb",
            "description": "[수불 백업 로그] DmIMTR01 배치 수행이 완료되어 각 실적 테이블에 성공적으로 반영된 IMTRLGTB 데이터를 보관 이관(insertIMTRBKTB) 처리하고 원본 수불 로그는 삭제 처리하여 대기 큐를 비워줍니다."
        },
        {
            "table_name": "imremstb",
            "description": "[재고 실사 마스터] 매장 실사 등록 확정 시 전산 재고와의 실사 차이 조정을 위한 변동 분을 계산하고, 이 보정용 수불 내역을 생성하여 IMTRLGTB에 이관 및 연동시킵니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] 수불 발생 상품에 대한 상세 규격, 매장 매핑 상태 및 상품 분류 정보를 매핑 조회하기 위해 GOODS_CD 기준으로 조인 관계를 형성합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with imtrlgtb related_tables!")
        
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
