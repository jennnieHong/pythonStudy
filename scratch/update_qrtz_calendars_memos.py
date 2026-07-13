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
    if "qrtz_calendars" not in tables:
        print("qrtz_calendars key not found in tables. Initializing...")
        tables["qrtz_calendars"] = {
            "memo": "특정 날짜 제외를 위한 캘린더 데이터 테이블입니다. (Quartz Calendars)",
            "starred": False,
            "color": "none",
            "columns": {},
            "memo_c": "Quartz 스케줄러 라이브러리가 기동하여 스케줄링 배치 실행 주기에서 배제할 특정 영업 제외일/공휴일 캘린더 설정을 등록할 때 자동 생성됩니다.",
            "memo_u": "웹 백오피스 스케줄러 관리 화면이나 쿼츠 스레드 내부에서 제외 영업일 캘린더 룰을 수정할 때 자동으로 업데이트됩니다.",
            "memo_d": "해당 캘린더 설정 또는 제외일 규칙이 삭제될 때 물리 삭제(Hard Delete)됩니다.",
            "memo_r": "Quartz 엔진 내부에서 트리거가 작동하기 직전, 오늘 날짜가 실행 제외 캘린더(Calendar) 룰에 속하는지 판별하기 위해 조회됩니다."
        }
        
    qrtz_calendars = tables["qrtz_calendars"]
    
    # Add/Update related_tables with all verified related tables in Quartz Scheduler standard schema
    qrtz_calendars["related_tables"] = [
        {
            "table_name": "qrtz_triggers",
            "description": "[스케줄러 트리거 기본] QRTZ_TRIGGERS.SCHED_NAME = QRTZ_CALENDARS.SCHED_NAME AND QRTZ_TRIGGERS.CALENDAR_NAME = QRTZ_CALENDARS.CALENDAR_NAME 조인을 통해, 트리거가 배치 스케줄링 기동 시 참고해야 하는 제외 영업일/공휴일 캘린더 명세를 1:N 관계로 결합합니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_calendars details!")
        
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
