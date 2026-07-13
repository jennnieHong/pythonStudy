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
    if "qrtz_fired_triggers" not in tables:
        print("qrtz_fired_triggers key not found in tables. Initializing...")
        tables["qrtz_fired_triggers"] = {
            "memo": "현재 활성화(실행 중)된 트리거 정보 테이블입니다. (Quartz Fired Triggers)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "Quartz 스케줄러 배치 기동 시, 해당 트리거가 임계시간에 도달하여 실제로 기동(Fired)되고 배치 Job이 작동(Running)을 개시할 때 실시간 트랜잭션 데이터가 삽입됩니다.",
            "memo_u": "배치 가동 중간 상태(상태 플래그, 완료 여부 등)를 동적으로 트래킹하기 위해 Quartz 엔진에 의해 업데이트됩니다.",
            "memo_d": "배치 Job의 실행이 종료(Success/Fail 완료)되면, 가동 상태 해제를 위해 Quartz 배치 스레드가 해당 인스턴스 행을 테이블에서 즉시 삭제(Hard Delete)합니다.",
            "memo_r": "배치 서버 다중화 환경(Clustering)에서 특정 노드가 가동 중인 배치 인스턴스 중복 실행을 방지하기 위해 락(Lock) 대조 용도로 조회됩니다."
        }
        
    qrtz_fired_triggers = tables["qrtz_fired_triggers"]
    
    # Add/Update related_tables with all verified related tables in Quartz Scheduler standard schema
    qrtz_fired_triggers["related_tables"] = [
        {
            "table_name": "qrtz_triggers",
            "description": "[스케줄러 트리거 기본] QRTZ_FIRED_TRIGGERS.SCHED_NAME = QRTZ_TRIGGERS.SCHED_NAME AND QRTZ_FIRED_TRIGGERS.TRIGGER_NAME = QRTZ_TRIGGERS.TRIGGER_NAME AND QRTZ_FIRED_TRIGGERS.TRIGGER_GROUP = QRTZ_TRIGGERS.TRIGGER_GROUP 조인을 통해 현재 실행 중인 인스턴스의 원본 트리거 명세를 1:1 매치합니다."
        },
        {
            "table_name": "qrtz_job_details",
            "description": "[쿼츠 배치 작업 상세] QRTZ_FIRED_TRIGGERS.SCHED_NAME = QRTZ_JOB_DETAILS.SCHED_NAME AND QRTZ_FIRED_TRIGGERS.JOB_NAME = QRTZ_JOB_DETAILS.JOB_NAME AND QRTZ_FIRED_TRIGGERS.JOB_GROUP = QRTZ_JOB_DETAILS.JOB_GROUP 조인을 통해 현재 러닝 상태로 실행되고 있는 대상 배치 Job 사양 정보를 1:1로 매핑합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_fired_triggers details!")
        
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
