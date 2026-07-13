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
    if "mmssrctb" not in tables:
        print("mmssrctb key not found in tables. Initializing...")
        tables["mmssrctb"] = {
            "memo": "매장별 소스 MASTER 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 매장별 소스 MASTER 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mmssrctb = tables["mmssrctb"]
    
    # Add/Update related_tables with ALL 16 related tables verified by auto_relations scan
    mmssrctb["related_tables"] = [
        {
            "table_name": "tmssrctb",
            "description": "[본사 소스 마스터] 본사 기준의 레시피 소스 구성 마스터 테이블입니다. 신규 매장 오픈이나 본사 정책에 따라 매장별 소스 정보(MMSSRCTB)로 데이터를 복사 및 동기화할 때 연계됩니다."
        },
        {
            "table_name": "mgoodstb",
            "description": "[매장별 상품 마스터] 매장별 레시피 소스의 기준이 되는 상품 마스터 정보를 매핑 조회하기 위해 GOODS_CD 기준으로 조인 관계를 형성합니다."
        },
        {
            "table_name": "tgoodstb",
            "description": "[체인 상품 마스터] 체인 레벨의 원부자재/상품 사양 정보를 조회하고 검증하기 위해 조인하여 해석합니다."
        },
        {
            "table_name": "mpricetb",
            "description": "[매장별 상품 단가] 매장별 소스 원자재 가격 정보를 조회하여 최종 상품 레시피 소스 원가 분석 및 단가 매핑에 반영합니다."
        },
        {
            "table_name": "tpricetb",
            "description": "[체인 단가 마스터] 체인 표준 소스 단가 정책을 조회하고, 매장별 단가 편차를 대조 분석할 때 조인됩니다."
        },
        {
            "table_name": "imcriotb",
            "description": "[매장별 현재고 마스터] 수불 발생 및 소스 원자재 재조정 시 실시간 전산 현재고 테이블과 연계하여 현재 재고량을 파악하고 대조합니다."
        },
        {
            "table_name": "imrealtb",
            "description": "[매장별 재고 실사] 소스 원자재 실사 입력 및 조정 내역 등록 화면에서 원부자재 대조 실적을 작성할 때 조인 조회됩니다."
        },
        {
            "table_name": "imddiotb",
            "description": "[일수불 실적 테이블] 일일 단위의 소스 원부자재 수불량 변동 및 현재고 수량 집계 분석 시 조인됩니다."
        },
        {
            "table_name": "immmiotb",
            "description": "[월수불 실적 테이블] 월말 마감 수불 처리 및 재고 결산 분석 시 소스 원부자재 월간 변동 누적량을 조회하기 위해 조인합니다."
        },
        {
            "table_name": "tb_recipe_goods",
            "description": "[상품 레시피 원자재 명세] 소스 구성에 소속된 하위 구성품(레시피 반제품/원자재) 목록을 1:N 조인을 통해 파싱하고 전파합니다."
        },
        {
            "table_name": "imdusetb",
            "description": "[매장별 폐기 마스터] 소스 및 원부자재 상품의 폐기 등록 시, 해당 상품 코드의 소스 구성 정보를 검증하기 위해 조인 연동됩니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MMSSRCTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 가맹점(매장) 단위로 소스 구성 기초 마스터 정보를 분할 격리하여 연계합니다."
        },
        {
            "table_name": "mmembvtb",
            "description": "[매장 환경설정 마스터] 매장별 소스 원가 계산 방식 설정이나 재고 배포 룰 설정을 매핑하여 비즈니스 가동에 활용합니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 소스 마스터의 등록/수정/삭제 조작을 수행한 본사/매장 직원의 상세 정보를 매핑합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 매장별 레시피 소스의 추가, 단가 변경, 폐기 등의 CUD 행위 발생 시 감사 이력 로그를 MMSLOGTB에 실시간 적재합니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 소스의 상태 코드, 규격 단위 등의 공통 코드 한글 명칭을 바인딩하기 위해 조인합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mmssrctb details!")
        
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
