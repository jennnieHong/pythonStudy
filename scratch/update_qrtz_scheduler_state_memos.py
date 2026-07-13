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
    if "qrtz_scheduler_state" not in tables:
        print("qrtz_scheduler_state key not found in tables. Initializing...")
        tables["qrtz_scheduler_state"] = {
            "memo": "클러스터 노드(서버)들의 상태 관리 테이블입니다. (Quartz Scheduler State)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "Quartz 스케줄러를 탑재한 WAS/배치 프로세스가 기동(Start)하면서 자신의 고유 노드 ID(INSTANCE_NAME)를 등록할 때 실시간으로 생성됩니다.",
            "memo_u": "생존 헬스체크 입증을 위해, 스케줄러 노드 데몬이 주기적으로 자신의 Heartbeat 체크 타임스탬프(LAST_CHECKIN_TIME)를 동적으로 업데이트합니다.",
            "memo_d": "해당 배치 노드가 정상적으로 종료(Shutdown)되거나, 타 노드가 생존 감시(Check-in Fail)를 통해 오프라인으로 판정하여 퇴출(Hard Delete)시킬 때 삭제됩니다.",
            "memo_r": "다른 스케줄러 노드가 기동 중인지, 혹은 중단된 노드가 획득했던 미완료 스케줄 락을 양도받아 복구해야 하는지 감시(Check-in) 시 조회됩니다."
        }
        
    qrtz_scheduler_state = tables["qrtz_scheduler_state"]
    
    # Add/Update related_tables with all verified related tables in Quartz Scheduler standard schema
    qrtz_scheduler_state["related_tables"] = [
        {
            "table_name": "qrtz_locks",
            "description": "[스케줄러 동기화 락] QRTZ_SCHEDULER_STATE.SCHED_NAME = QRTZ_LOCKS.SCHED_NAME 조인을 통해, 활성 노드의 생존 감시 및 장애 노드가 쥐고 있는 락(TRIGGER_ACCESS 등)의 소유권을 회수하여 가동 권한을 재분배할 때 조인 연계됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_scheduler_state details!")
        
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
