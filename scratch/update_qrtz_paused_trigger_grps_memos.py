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
    if "qrtz_paused_trigger_grps" not in tables:
        print("qrtz_paused_trigger_grps key not found in tables. Initializing...")
        tables["qrtz_paused_trigger_grps"] = {
            "memo": "일시 정지된 트리거 그룹 목록 테이블입니다. (Quartz Paused Trigger Groups)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "Quartz 스케줄러 배치 모듈 또는 백오피스 컨트롤러에서 특정 트리거 그룹 전체를 일시 정지(Pause)시킬 때 해당 그룹 레코드가 자동으로 생성됩니다.",
            "memo_u": "일시정지 상태값 트래킹 및 옵션 변경 시 Quartz 엔진에 의해 내부적으로 업데이트될 수 있습니다.",
            "memo_d": "일시 정지했던 트리거 그룹을 다시 재개(Resume)하여 활성화할 때, Quartz 배치 엔진에 의해 해당 행이 즉시 물리 삭제(Hard Delete)됩니다.",
            "memo_r": "Quartz 엔진 내부에서 트리거의 가동 여부를 판단할 때, 해당 트리거가 속한 그룹이 일시정지 목록에 등록되어 있는지 필터링하기 위해 조회됩니다."
        }
        
    qrtz_paused_trigger_grps = tables["qrtz_paused_trigger_grps"]
    
    # Add/Update related_tables with all verified related tables in Quartz Scheduler standard schema
    qrtz_paused_trigger_grps["related_tables"] = [
        {
            "table_name": "qrtz_triggers",
            "description": "[스케줄러 트리거 기본] QRTZ_PAUSED_TRIGGER_GRPS.SCHED_NAME = QRTZ_TRIGGERS.SCHED_NAME AND QRTZ_PAUSED_TRIGGER_GRPS.TRIGGER_GROUP = QRTZ_TRIGGERS.TRIGGER_GROUP 조인을 통해, 일시정지 처리된 트리거 그룹과 이에 속한 개별 트리거 마스터 리스트를 1:N 관계로 묶어 줍니다."
        },
        {
            "table_name": "qrtz_job_details",
            "description": "[쿼츠 배치 작업 상세] 일시정지된 트리거 그룹에 귀속된 트리거들이 실행시킬 타깃 배치 Job 명세를 식별하기 위해 QRTZ_TRIGGERS 마스터 조인을 거쳐 간접적으로 조인 관계를 형성합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_paused_trigger_grps details!")
        
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
