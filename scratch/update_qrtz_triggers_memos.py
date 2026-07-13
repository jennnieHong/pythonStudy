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
    if "qrtz_triggers" not in tables:
        print("qrtz_triggers key not found in tables. Initializing...")
        tables["qrtz_triggers"] = {
            "memo": "Quartz 스케줄러에서 관리하는 트리거 마스터 테이블입니다. (Quartz Triggers Master)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "Quartz 스케줄러 라이브러리가 크론이나 단순 주기 기동 등 스케줄 작업(Job)을 트리거하기 위한 스케줄러 트리거 설정을 데이터베이스에 등록할 때 자동 생성됩니다.",
            "memo_u": "웹 백오피스 스케줄러 관리 화면이나 Quartz 데몬 스레드에서 해당 트리거 설정을 수정하거나, 실행 주기, 상태 코드 등을 변경할 때 자동으로 업데이트됩니다.",
            "memo_d": "해당 배치 스케줄러 트리거가 영구 중지되거나 스케줄링 잡이 삭제(Hard Delete)될 때 함께 물리 삭제됩니다.",
            "memo_r": "Quartz 데몬 스케줄러 스레드가 주기적으로 실행할 트리거 목록을 감시하고 다음 실행 예정 시간(NEXT_FIRE_TIME)을 계산하기 위해 조회됩니다."
        }
        
    qrtz_triggers = tables["qrtz_triggers"]
    
    # Add/Update related_tables with all verified related tables in Quartz Scheduler standard schema
    qrtz_triggers["related_tables"] = [
        {
            "table_name": "qrtz_job_details",
            "description": "[쿼츠 배치 작업 상세] QRTZ_TRIGGERS.SCHED_NAME = QRTZ_JOB_DETAILS.SCHED_NAME AND QRTZ_TRIGGERS.JOB_NAME = QRTZ_JOB_DETAILS.JOB_NAME AND QRTZ_TRIGGERS.JOB_GROUP = QRTZ_JOB_DETAILS.JOB_GROUP 조인을 통해 트리거가 최종적으로 실행할 대상 Job 명세의 마스터 정보와 연결됩니다."
        },
        {
            "table_name": "qrtz_cron_triggers",
            "description": "[스케줄러 크론 트리거] 크론 표현식 기반의 실행 주기를 정의하는 트리거 상세 테이블로, 트리거 타입(TRIGGER_TYPE)이 'CRON'인 경우 1:1 관계를 형성하며 상세 설정 정보를 가져옵니다."
        },
        {
            "table_name": "qrtz_simple_triggers",
            "description": "[스케줄러 단순 트리거] 지정된 횟수와 간격으로 반복 실행하는 단순 반복 트리거 상세 테이블로, 트리거 타입(TRIGGER_TYPE)이 'SIMPLE'인 경우 1:1 관계를 형성하며 상세 설정 정보를 가져옵니다."
        },
        {
            "table_name": "qrtz_simprop_triggers",
            "description": "[스케줄러 속성 트리거] 자바의 Properties, Date, Long, Dec 등 개별 타입 속성값을 포함하여 기동하는 개선된 속성 기반 트리거 상세 테이블로, 1:1 조인을 통해 관련 속성들을 조회합니다."
        },
        {
            "table_name": "qrtz_blob_triggers",
            "description": "[스케줄러 직렬화 트리거] 사용자 정의 직렬화 바이너리 매개변수를 포함하는 커스텀 트리거 상세 테이블로, 1:1 조인을 통해 바이너리 상세 설정을 조회합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_triggers details!")
        
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
