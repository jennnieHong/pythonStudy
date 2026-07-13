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
    if "muserstb" not in tables:
        print("muserstb key not found in tables. Initializing...")
        tables["muserstb"] = {
            "memo": "사용자 마스터 테이블. 시스템 사용자 계정 정보를 보관합니다.",
            "starred": True,
            "color": "none",
            "columns": {},
            "memo_c": "백오피스 사용자/사원 등록 시 생성됩니다.",
            "memo_u": "사용자 권한, 비밀번호, 소속 매장 변경 시 수정되며, 수정 내역은 SSUSERTB 및 MMSLOGTB에 동기화 처리됩니다.",
            "memo_d": "acct_expire = 'Y' 설정을 통한 사용자 계정 만료 처리로 논리 삭제(Soft Delete)를 수행합니다.",
            "memo_r": "백오피스 로그인 인증 및 권한 확인, 매장별 사원 정보 조회 시 핵심 테이블로 사용됩니다."
        }
        
    muserstb = tables["muserstb"]
    
    # Add/Update related_tables with all verified related tables grouped by business domain
    muserstb["related_tables"] = [
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] MUSERSTB.MS_NO = MMEMBSTB.MS_NO 조인을 통해 본사 직원(system_type = 'HQ') 혹은 매장 사원('ST')의 소속 매장(점포)을 특정하고 매핑 관리합니다."
        },
        {
            "table_name": "tchaintb",
            "description": "[브랜드 체인 마스터] 사용자가 관리 또는 속해 있는 브랜드 구분(chain_no) 표준 정보를 매핑하여 가동합니다."
        },
        {
            "table_name": "usermltb",
            "description": "[사용자별 메뉴 권한 매핑] 사용자가 개별 로그인 후 접근 가능한 웹 권한 그룹(ROLE_CD)을 맵 매핑하고, 사용자 등급별 상세 화면/메뉴 권한 정보를 조회합니다."
        },
        {
            "table_name": "mrolehtb",
            "description": "[웹 메뉴 권한 헤더] 권한 마스터 화면 조회 시, 해당 권한 롤을 등록/수정한 관리자 사원의 한글 명칭과 소속을 매핑해 줍니다."
        },
        {
            "table_name": "menummtb",
            "description": "[웹 메뉴 마스터] 메뉴 권한 할당 및 사용자별 커스텀 메뉴 구성 화면에서 권한을 바인딩하기 위해 조인합니다."
        },
        {
            "table_name": "strnhdtb",
            "description": "[매출 거래 헤더] 포스에서 거래 영수증이 발행될 때 판매를 수행한 담당 캐셔(사원 EMP_ID)의 실명을 매핑 조회하여 영수증 및 매출 대장에 캐셔 한글명을 출력합니다."
        },
        {
            "table_name": "sordidtb",
            "description": "[주문 사원 실적] 매장 내 특정 직원의 개인별 매출/판매 실적 및 기여도를 집계하여 분석 리포트를 렌더링할 때 조인됩니다."
        },
        {
            "table_name": "canchdtb",
            "description": "[주문 취소 마스터] 매출 거래의 중간 취소 또는 보정 전표 처리를 최종 승인 및 실행한 관리자 사원의 이름을 매치해 줍니다."
        },
        {
            "table_name": "mvndrmtb",
            "description": "[매장별 거래처 마스터] 협력업체/거래처 직원 계정 등록 및 매장 직원 인적사항 매핑 조회 시 사용됩니다."
        },
        {
            "table_name": "tvndrmtb",
            "description": "[체인 거래처 마스터] 본사 직속 협력업체 사원 계정 승인 및 마스터 조회 시 연계됩니다."
        },
        {
            "table_name": "imdusetb",
            "description": "[매장별 폐기 마스터] 원자재 및 상품 폐기 등록 시 해당 폐기를 직접 수기 입력하고 확정 처리한 관리자의 실명을 감사 로그 대조용으로 조인합니다."
        },
        {
            "table_name": "imrealtb",
            "description": "[매장별 재고 실사] 재고 전수 실사를 확정하여 현재고 보정을 가동한 현장 작업자 정보를 매치합니다."
        },
        {
            "table_name": "mversntb",
            "description": "[포스 패치 버전] 새로운 포스 패치 패키지를 본사에서 배포/승인 처리한 본사 기획자의 계정 이력을 조인 매핑합니다."
        },
        {
            "table_name": "loginstb",
            "description": "[사용자 로그인 성공 이력] 사용자가 시스템에 접속할 때 사용자 한글 성명과 접속 IP, 계정 타입을 일치시켜 로그인 감사 로그 대장을 작성합니다."
        },
        {
            "table_name": "srvlogtb",
            "description": "[웹 서비스 호출 로그] 특정 서비스 API DML 실행 시 해당 액션을 기동한 사용자(작성자/수정자)의 실명 감사를 수행하기 위해 조인합니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] 백오피스 내 관리자 계정 생성, 잠금 설정/해제 등 사용자 마스터의 직접적인 CUD 발생 시 변경 감사 로그를 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with muserstb details!")
        
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
