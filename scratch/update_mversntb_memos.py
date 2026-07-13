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
    if "mversntb" not in tables:
        print("mversntb key not found in tables. Initializing...")
        tables["mversntb"] = {
            "memo": "버전 상세/배포 이력 테이블입니다.",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "포스 버전 등록/배포 화면에서 매장별로 패키지 버전을 할당하여 배포를 기동(saveMsList)할 때 상세 행 레코드가 생성됩니다.",
            "memo_u": "포스 단말기에서 파일을 정상 수신하여 다운로드 및 설치를 마쳤을 때 진행률 및 적용 완료 시간 정보가 업데이트됩니다.",
            "memo_d": "데이터 정합성 및 무결성 보장을 위해 행 물리 삭제를 금지하며, 사용을 중단하거나 보정 전표를 발행하여 처리해야 합니다.",
            "memo_r": "매장별 포스 패치 버전 최종 설치 현황, 그리고 [POS 버전 다운로드 내역 (admin_system_00002)] 화면에서 다운로드 성공 이력을 조회할 때 참조됩니다."
        }
        
    mversntb = tables["mversntb"]
    
    # Add/Update related_tables with all verified related tables in the POS version deployment history
    mversntb["related_tables"] = [
        {
            "table_name": "mversmtb",
            "description": "[버전관리 마스터] MVERSNTB.VER_NO = MVERSMTB.VER_NO 조인을 통해 배포 패키지 원본 정보(버전명, 파일 경로)와 매장별 다운로드 이력을 N:1 관계로 연계합니다."
        },
        {
            "table_name": "mmembstb",
            "description": "[가맹점 매장 마스터] 개별 가맹점(MS_NO) 기준으로 패키지 다운로드 완료 이력(selectVersionHistoryList)을 대조하고 점포 분류를 필터링하기 위해 조인합니다."
        },
        {
            "table_name": "tchaintb",
            "description": "[브랜드 체인 마스터] 버전 패치 및 다운로드 내역의 소속 브랜드를 매핑하고, 브랜드 단위 다운로드 성공률 통계 조회 시 조인됩니다."
        },
        {
            "table_name": "mnamemtb",
            "description": "[시스템 명칭 마스터] 개별 매장 포스의 패키지 파일 다운로드 성공 여부, 진행 중 상태값 코드의 공통 한글 설명 명칭을 조인 조회합니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 패치 적용 상태 현황 조회 시, 강제 재전송이나 패치 초기화 조작을 수행한 현장 관리자 사원의 이름을 매핑해 줍니다."
        },
        {
            "table_name": "mmslogtb",
            "description": "[웹 변경 이력 로그] [POS 버전 등록/배포] 메뉴에서 매장별 배포 플래그를 인위적으로 재설정하거나, 실패 이력을 초기화(deleteVersionList)할 때 조작 감사 이력을 MMSLOGTB에 실시간 적재합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with mversntb details!")
        
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
