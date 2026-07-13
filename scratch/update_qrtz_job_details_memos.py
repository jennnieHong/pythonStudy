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
    if "qrtz_job_details" not in tables:
        print("qrtz_job_details key not found in tables. Initializing...")
        tables["qrtz_job_details"] = {
            "memo": "Job의 정의 및 상세 정보 저장 테이블입니다. (Quartz Job Details)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "Quartz 스케줄러 배치 모듈 기동 시, Java 코드로 정의된 개별 배치 작업 클래스(JobClass) 명세 정보가 최초 등록될 때 신규 생성됩니다.",
            "memo_u": "웹 백오피스 스케줄러 조작 화면이나 배치 데몬 스레드에서 해당 작업의 속성 파라미터 설정을 수정할 시 자동으로 업데이트됩니다.",
            "memo_d": "해당 스케줄러 배치 Job 설정이 영구 중지되거나 폐기(Hard Delete)될 때 함께 삭제됩니다.",
            "memo_r": "Quartz 스케줄러 데몬이 기동되어 실행 가능한 배치 Job의 인스턴스를 메모리에 로딩하고 초기화할 때 조회됩니다."
        }
        
    qrtz_job_details = tables["qrtz_job_details"]
    
    # Add/Update related_tables with all verified related tables in Quartz Scheduler standard schema
    qrtz_job_details["related_tables"] = [
        {
            "table_name": "qrtz_triggers",
            "description": "[스케줄러 트리거 기본] QRTZ_TRIGGERS.SCHED_NAME = QRTZ_JOB_DETAILS.SCHED_NAME AND QRTZ_TRIGGERS.JOB_NAME = QRTZ_JOB_DETAILS.JOB_NAME AND QRTZ_TRIGGERS.JOB_GROUP = QRTZ_JOB_DETAILS.JOB_GROUP 조인을 통해 등록된 배치 Job 상세 정보와 해당 Job을 동작시킬 크론/심플 트리거 설정을 1:N 관계로 묶어 줍니다."
        },
        {
            "table_name": "qrtz_fired_triggers",
            "description": "[스케줄러 실행 중인 트리거 인스턴스] 현재 백그라운드 스레드에서 실제 실행 상태에 진입한 활성 스케줄 인스턴스 정보와 1:N 조인 매핑됩니다."
        },
        {
            "table_name": "qrtz_api_log",
            "description": "[쿼츠 API 실행 로그] 배치 작업이 동작하는 과정에서 외부 전송/인터페이스 API를 기동하였을 때 발생하는 트랜잭션 에러 로그(ERR_CTNT) 이력과 1:N 관계로 연계됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_job_details details!")
        
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
