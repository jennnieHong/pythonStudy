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
    if "mversmtb" not in tables:
        print("mversmtb key not found in tables. Initializing...")
        tables["mversmtb"] = {
            "memo": "버젼관리 MASTER 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "사용자 관리자 화면에서 버젼관리 MASTER 정보를 입력하여 저장하면 신규 레코드가 생성되는 마스터 테이블입니다.",
            "memo_u": "화면의 수정 폼을 통해 속성 값을 수정한 후 [저장] 시 업데이트 쿼리가 동작하여 기존 행 정보를 갱신합니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "화면 진입 시 코드 콤보박스 바인딩, 입력 검증용 중복 확인, 또는 연관 트랜잭션 화면 조회 시 조인 기준으로 조회됩니다."
        }
        
    mversmtb = tables["mversmtb"]
    
    # Add/Update related_tables with all verified related tables in the POS version deployment flow
    mversmtb["related_tables"] = [
        {
            "table_name": "mversntb",
            "description": "[버전 상세/배포 이력] MVERSMTB.VER_NO = MVERSNTB.VER_NO 조인을 통해 등록된 개별 패키지 버전 마스터 정보와 각 매장별 패치 전송 상태 및 버전 상세 정보를 1:N 관계로 묶어 줍니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] 특정 버전 패키지를 배포할 대상 점포(getMsList)를 조회하거나, 버전이 실제 적용된 매장별 패치 이력을 조회(selectVersionHistoryList)하기 위해 조인합니다."
        },
        {
            "table_name": "mmembptb",
            "description": "[매장 IP 및 장비 정보] 버전 배포 시 각 매장의 POS 기기 사양 및 IP 대역 등의 연결 인프라 사양 정보를 조인합니다."
        },
        {
            "table_name": "tchaintb",
            "description": "[브랜드 체인 마스터] 버전 패키지가 적용되는 대상 매장들의 소속 체인을 판별하여, 체인별 버전 격리 배포 정책 구성 시 연계됩니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 버전 패키지의 파일 상태 코드, 배포 진행 현황 등의 공통 코드 한글 명칭을 매핑하여 화면에 출력합니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 패치 버전을 최초 빌드 및 업로드하고 배포를 실행/승인한 본사 관리자 사원의 이름을 이력 현황에서 매핑해 줍니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [POS 버전 등록/배포 (admin_system_00001)] 화면 등에서 관리자가 버전 패키지 신규 업로드(insert), 속성 변경, 또는 배포 상태 전환 시 조작 이력을 MMSLOGTB에 실시간 기록합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mversmtb details!")
        
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
