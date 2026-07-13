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
    if "qrtz_simprop_triggers" not in tables:
        print("qrtz_simprop_triggers key not found in tables. Initializing...")
        tables["qrtz_simprop_triggers"] = {
            "memo": "Java 8 날짜 타입 등 개선된 트리거 속성 정보 테이블입니다. (Quartz Simprop Triggers)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "Quartz 스케줄러 라이브러리가 개선된 자바 Properties/Date 혹은 기타 기본형 데이터 타입을 포함한 트리거를 데이터베이스에 등록할 때 자동 생성됩니다.",
            "memo_u": "웹 백오피스 스케줄러 관리 화면이나 Quartz 데몬 스레드에서 해당 트리거의 Properties 속성 정보가 변경/갱신될 때 자동으로 업데이트됩니다.",
            "memo_d": "해당 배치 스케줄러 트리거가 영구 중지되거나 스케줄링 잡이 삭제(Hard Delete)될 때 함께 삭제됩니다.",
            "memo_r": "Quartz 엔진 내부에서 트리거를 복원하여 스케줄링 기동 시 해당 Properties 상세 속성 데이터를 주입하기 위해 조회됩니다."
        }
        
    qrtz_simprop_triggers = tables["qrtz_simprop_triggers"]
    
    # Add/Update related_tables with all verified related tables in Quartz Scheduler standard schema
    qrtz_simprop_triggers["related_tables"] = [
        {
            "table_name": "qrtz_triggers",
            "description": "[스케줄러 트리거 기본] QRTZ_SIMPROP_TRIGGERS.SCHED_NAME = QRTZ_TRIGGERS.SCHED_NAME AND QRTZ_SIMPROP_TRIGGERS.TRIGGER_NAME = QRTZ_TRIGGERS.TRIGGER_NAME AND QRTZ_SIMPROP_TRIGGERS.TRIGGER_GROUP = QRTZ_TRIGGERS.TRIGGER_GROUP 조인을 통해 트리거 마스터 설정과 세부 자바 Properties 속성 설정을 1:1 관계로 연결합니다."
        },
        {
            "table_name": "qrtz_job_details",
            "description": "[쿼츠 배치 작업 상세] 트리거가 최종적으로 실행할 타깃 Quartz Job 명세 정보를 대조하기 위해 QRTZ_TRIGGERS 마스터 조인을 거쳐 연계됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_simprop_triggers details!")
        
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
