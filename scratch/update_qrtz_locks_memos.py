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
    if "qrtz_locks" not in tables:
        print("qrtz_locks key not found in tables. Initializing...")
        tables["qrtz_locks"] = {
            "memo": "클러스터 동시성 제어를 위한 행 단위 락 정보 테이블입니다. (Quartz Locks)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "Quartz 스케줄러 라이브러리가 로딩되어 기동 시, 동기화 잠금 획득을 위해 TRIGGER_ACCESS, STATE_ACCESS 등의 기본 락 정보 행이 최초 1회 생성됩니다.",
            "memo_u": "스케줄러 엔진이 트리거 상태를 평가하거나 노드 체크를 시작하기 전에, 동시성 확보를 위해 해당 행에 대해 SELECT ... FOR UPDATE (비관적 락) 쿼리를 날려 행을 잠급니다. (데이터 속성의 물리적 갱신은 수행되지 않음)",
            "memo_d": "데이터 정합성 및 스케줄 락 보장을 위해 인위적인 행 삭제를 금지하며, 스케줄러 자체를 폐기하지 않는 한 행 삭제는 발생하지 않습니다.",
            "memo_r": "배치 서버 다중화 노드 환경에서 스케줄 변경 권한을 먼저 획득한 노드만 독점적으로 배치를 가동할 수 있도록 검증 시 조회됩니다."
        }
        
    qrtz_locks = tables["qrtz_locks"]
    
    # Add/Update related_tables with all verified related tables in Quartz Scheduler standard schema
    qrtz_locks["related_tables"] = [
        {
            "table_name": "qrtz_scheduler_state",
            "description": "[스케줄러 상태 정보] QRTZ_LOCKS.SCHED_NAME = QRTZ_SCHEDULER_STATE.SCHED_NAME 조인을 통해, 클러스터링으로 묶인 복수의 스케줄러 노드(Node)들의 생존 주기 상태와 락 정합성을 대조하기 위해 연계합니다."
        },
        {
            "table_name": "qrtz_fired_triggers",
            "description": "[스케줄러 실행 중인 트리거 인스턴스] 배치 스레드가 트리거를 Fired 시키기 전, 중복 가동 방지를 위해 QRTZ_LOCKS의 TRIGGER_ACCESS 잠금을 획득하므로 락 획득 트랜잭션과 연동됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_locks details!")
        
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
