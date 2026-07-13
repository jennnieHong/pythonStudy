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
    
    # Fix description to '스케줄러 쿼츠 배치 작업 실행 로그 테이블'
    tables["qrtz_log"] = {
        "memo": "스케줄러 쿼츠 배치 작업 실행 로그 테이블입니다. (Quartz Scheduler Execution Log)",
        "starred": False,
        "color": "none",
        "columns": {},
        "memo_c": "Quartz 스케줄러 배치 Job의 실행 완료 시점(성공 혹은 실패)에, 총 처리 건수(TOTAL_CNT), 성공 건수(SUCCESS_CNT), 실패 건수(FAIL_CNT) 및 에러 메시지(ERR_MSG) 등의 실행 실적 레코드를 Insert하여 생성합니다.",
        "memo_u": "실행이 끝난 후 적재되는 감사 목적의 히스토리 로그 테이블이므로 수동 업데이트는 차단됩니다.",
        "memo_d": "데이터베이스 공간 최적화를 위해 월 단위 혹은 분기 단위 배치 정리 프로세스를 돌려 오래된 로그는 물리 삭제(Hard Delete) 처리합니다.",
        "memo_r": "웹 백오피스 [배치 실행 로그 조회 (admin_system_00014)] 화면의 메인 그리드(searchBatchLogList)에 일자별/상태별 배치 가동 통계 및 실패 에러 메시지를 조회할 때 참조됩니다."
    }
    
    qrtz_log = tables["qrtz_log"]
    
    # Add/Update related_tables with all verified related tables in Quartz Scheduler standard schema
    qrtz_log["related_tables"] = [
        {
            "table_name": "qrtz_job_details",
            "description": "[스케줄러 작업 마스터 상세] QRTZ_LOG.SCHED_NAME = QRTZ_JOB_DETAILS.SCHED_NAME AND QRTZ_LOG.JOB_NAME = QRTZ_JOB_DETAILS.JOB_NAME AND QRTZ_LOG.JOB_GROUP = QRTZ_JOB_DETAILS.JOB_GROUP 조인을 통해, 실행된 배치 작업의 클래스 정의 정보와 최종 실행 이력을 1:N 관계로 묶어 줍니다."
        },
        {
            "table_name": "qrtz_api_log",
            "description": "[쿼츠 API 실행 로그] 특정 배치 작업 실패 시 동반 실행된 외부 연동 API 통신 도중 에러가 발생했는지, HTTP 응답 결과(RES_CD)와 세부 에러 파라미터를 교차 추적할 때 조인합니다."
        },
        {
            "table_name": "muserstb",
            "description": "[시스템 사용자 마스터] 특정 배치 작업을 백오피스 콘솔에서 수동으로 즉시 실행(Trigger)한 경우, 해당 작업을 개시한 관리자 계정(CRTN_ID)의 한글 실명을 매핑 노출하는 데 연동됩니다."
        }
    ]
    
    # 3. Save back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Successfully updated table_memos.json with qrtz_log details!")
        
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
