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
    
    # Fix description to '쿼츠 API 실행 로그 테이블'
    tables["qrtz_api_log"] = {
        "memo": "쿼츠 API 실행 로그 테이블입니다. (Quartz Scheduler API Log)",
        "starred": False,
        "color": "none",
        "columns": {},
        "memo_c": "백그라운드 배치 코어 모듈(batchCore)의 AOP 로깅 프레임워크(LoggerAopMapper)가 작동하여, 연동 API 호출 및 외부 전송 트랜잭션이 수행될 때 자동으로 Insert 처리되어 생성됩니다.",
        "memo_u": "로그 적재 목적으로 설계된 이력용 테이블이므로 데이터 삽입 후 인위적인 업데이트 처리는 수행하지 않습니다.",
        "memo_d": "과거 로그 정리를 위해 주기적인 데이터 파티셔닝 드롭 또는 정기 배치 클렌징(Hard Delete) 처리를 통해 데이터를 비워냅니다.",
        "memo_r": "배치 연동 실패 에러 모니터링 화면 및 시스템 관리자 로그 웹 화면에서 에러 로그(ERR_CTNT)와 파라미터 대조 시 조회됩니다."
    }
    
    qrtz_api_log = tables["qrtz_api_log"]
    
    # Add/Update related_tables with all verified related tables in quartz scheduler logs
    qrtz_api_log["related_tables"] = [
        {
            "table_name": "qrtz_job_details",
            "description": "[쿼츠 작업 마스터 상세] 배치 스케줄러가 특정 작업(Job)을 트리거하여 가동하는 과정에서 외부 호출한 API의 전송 파라미터 및 헤더 이력을 QRTZ_API_LOG에 적재하므로 작업 실행 이력과 연계됩니다."
        },
        {
            "table_name": "qrtz_log",
            "description": "[쿼츠 실행 로그] 배치의 물리적 성공/실패 메인 로그 데이터와 교차 대조하여, 특정 배치 작업 실패 시 발생한 API 통신의 상세 HTTP 에러 코드(RES_CD)와 예외 트레이스(ERR_CTNT)를 추적할 때 조인 참조됩니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 웹 관리자 화면에서 특정 연동 API(POS 전송 등)를 수동 기동하여 로그가 생성된 경우, 해당 액션을 호출한 관리자 계정(CRTN_ID)을 식별하기 위해 조인 매핑합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_api_log details!")
        
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
