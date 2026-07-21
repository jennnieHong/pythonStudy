import json
import os

def update_all_memos():
    memos_path = r"D:\hmTest\backoffice\QaReport\table_memos.json"
    
    if not os.path.exists(memos_path):
        print(f"File not found: {memos_path}")
        return
        
    try:
        with open(memos_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read json: {e}")
        return

    if "tables" not in data:
        data["tables"] = {}

    # Save existing user state (starred and color) to prevent overwriting
    user_states = {}
    if "tables" in data:
        for t_name, t_info in data["tables"].items():
            user_states[t_name] = {
                "starred": t_info.get("starred", False),
                "color": t_info.get("color", "none")
            }

    # 1. IF_RECPSVTB MEMO
    if_recpsvtb_memo = (
        "### 1. 테이블 개요\n"
        "통합 인터페이스 로그 테이블 (`IF LOG TABLE`). Tibero에서 HMS PostgreSQL로 수신되는 배치 작업(카드사, 거래처/고객사, 부서, 사원, 월마감 등)의 실행 이력과 건수(총 건수, 성공 건수), 에러 메시지 등을 기록하여 인터페이스 모니터링에 활용됩니다.\n\n"
        "### 2. 배치 서비스 & XML 매퍼 상세 매핑\n"
        "각 배치 수신 서비스가 전체 데이터 수신 루프를 완료한 시점에 최종 결과를 `insertIfRecpsvtb` 쿼리를 통해 일괄 등록합니다.\n\n"
        "| 연계 업무 | 배치 서비스 클래스 (Java) | MyBatis Mapper XML 파일 | SQL ID |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **카드사 마스터 수신** (`IF_FB_206`) | `CardService.java` | `CardInerface_SqlMapper.xml` | `insertIfRecpsvtb` |\n"
        "| **거래처/고객 마스터 수신** (`IF_FB_201`) | `CustService.java` | `CustInerface_SqlMapper.xml` | `insertIfRecpsvtb` |\n"
        "| **부서 정보 수신** (`IF_FB_202`) | `DeptService.java` | `DeptInerface_SqlMapper.xml` | `insertIfRecpsvtb` |\n"
        "| **사원 정보 수신** (`IF_FB_303`) | `EmpService.java` | `EmpInerface_SqlMapper.xml` | `insertIfRecpsvtb` |\n"
        "| **매출 월마감 수신** (`IF_FB_006`) | `CloseService.java` | `CloseInerface_SqlMapper.xml` | `insertIfRecpsvtb` |\n\n"
        "### 3. 데이터 조회 (Select) 활용\n"
        "배치 실행 완료 후 또는 다른 배치 작업에서 해당 `PROC_SEQ` 기준의 데이터 처리 건수(총 건수, 성공 수 등)를 비교하기 위해 조회합니다.\n"
        "* **반송 메일 인터페이스** (`ReturnMailInerface_SqlMapper.xml` ➡️ `getReseultCount`)\n"
        "* **카드사 마스터 수신** (`CardInerface_SqlMapper.xml` ➡️ `getReseultCount`)\n\n"
        "### 4. 백오피스 화면 연계 여부\n"
        "* **직접적인 화면 연계 없음**: 현재 백오피스 소스코드(`backoffice` 모듈) 내부를 전수 조사한 결과, `IF_RECPSVTB` 테이블명을 직접 참조하거나 조회하는 SQL Mapper 쿼리는 존재하지 않습니다.\n"
        "* **용도**: 일반 백오피스 사용자 화면 노출용이 아니며, **배치 서버(hyundai-batch) 내부 로깅 및 데이터 이관 정합성 추적용**으로만 내부적으로 사용됩니다."
    )

    data["tables"]["if_recpsvtb"] = {
        "memo": if_recpsvtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "if_api": "인터페이스 API ID (예: 'IF_FB_201' - 거래처, 'IF_FB_202' - 부서, 'IF_FB_303' - 사원, 'IF_FB_006' - 월마감, 'IF_FB_206' - 카드사)",
            "proc_date": "인터페이스 반영 일자 (YYYYMMDD)",
            "proc_seq": "인터페이스 처리 순번 (IF_HJ_RECPSVSQ 시퀀스 사용)",
            "tot_cnt": "수신된 총 데이터 건수",
            "success_cnt": "성공적으로 HMS에 이관 완료된 데이터 건수",
            "remark": "처리 중 발생한 오류 메시지 또는 비고",
            "proc_dtime": "인터페이스 처리 시간 (YYYYMMDDHH24MISS)",
            "proc_id": "인터페이스를 실행한 주체 ID (예: 'JAVA_BATCH')"
        },
        "memo_c": "각 배치 수신 서비스(CardService, CloseService, CustService, DeptService, EmpService) 루프 실행 종료 후, 최종 결과를 새로운 트랜잭션으로 입력합니다.\n\n[백엔드 API 및 소스 확인]\n- 각 Mapper.xml (MyBatis ID: `insertIfRecpsvtb`)",
        "memo_u": "일반적으로 인터페이스 실행 이력 로그이므로 업데이트는 발생하지 않으나, 재처리 시 관련 기록 확인용으로 활용됩니다.",
        "memo_d": "과거 로그 보관 주기에 맞춰 배치 삭제 처리 등을 수행할 수 있습니다.",
        "memo_r": "배치 로그 조회 화면 및 시스템 관리자의 모니터링 기능에서 연관 테이블과 함께 조회됩니다.",
        "related_tables": [
            {
                "table_name": "bathrstb",
                "description": "배치 자체의 실행 이력을 관리하는 테이블이며, IF_RECPSVTB는 개별 배치 단위 인터페이스의 데이터 송수신 결과를 로깅하는 용도로 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "월마감 및 거래처 등 점포 기준을 참조하기 위해 가맹점 마스터 정보를 JOIN하여 처리합니다."
            },
            {
                "table_name": "mcardmtb",
                "description": "카드사 마스터 정보 인터페이스(IF_FB_206) 처리 결과를 로깅하기 위해 연계됩니다."
            },
            {
                "table_name": "tvndrmtb",
                "description": "거래처 마스터 정보 인터페이스(IF_FB_201) 처리 결과를 로깅하기 위해 연계됩니다."
            },
            {
                "table_name": "tdeptmtb",
                "description": "부서 정보 인터페이스(IF_FB_202) 처리 결과를 로깅하기 위해 연계됩니다."
            },
            {
                "table_name": "tifemptb",
                "description": "사원 정보 인터페이스(IF_FB_303) 처리 결과를 로깅하기 위해 연계됩니다."
            },
            {
                "table_name": "mclosetb",
                "description": "매출 월마감 인터페이스(IF_FB_006) 처리 결과를 로깅하기 위해 연계됩니다."
            }
        ]
    }

    # 2. IF_RTMS_MAILQUEUE MEMO
    if_rtms_mailqueue_memo = (
        "### 1. 테이블 개요\n"
        "메일 발송 예약 인터페이스 테이블 (`IF_RTMS_MAILQUEUE`).\n"
        "백오피스 화면(견적 요청서 전송, 발주 요청서 전송 등)에서 메일을 보낼 때 발송 예약 상태로 데이터를 적재하며, 외부 메일 서버 연동 및 배치 모듈에서 이를 읽어 발송 완료 후 상태를 업데이트하는 통합 메일 큐 테이블입니다.\n\n"
        "### 2. 백오피스 화면 & 배치 서비스 매핑\n"
        "이 테이블은 백오피스 메일 발송 화면과 메일 연동 데몬, 그리고 반송 배치 서비스에서 공동 사용됩니다.\n\n"
        "| 연계 업무 | 물리 화면 / 모듈 | MyBatis Mapper XML 파일 | SQL ID |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **견적 요청서 이메일 전송** | 본사 견적요청서 발송 (`Hq_Esti_00004`) | `Hq_Esti_00004_Sql.xml` | `insertEstiEmail` (Insert) |\n"
        "| **발주 요청서 이메일 전송** | 본사 발주요청서 발송 (`Hq_Vendor_00003`) | `Hq_Vendor_00003_Sql.xml` | `insertPurchEmail` (Insert) |\n"
        "| **미발송 메일 배치 연동** | 메일 전송 데몬 프로세스 | `Pos_MailInterface_Sql.xml` | `selectMailList` (Select) <br> `updateMail` (Update) |\n"
        "| **반송 메일 추적 및 알림** | 반송 메일 처리 배치 서비스 | `ReturnMailInerface_SqlMapper.xml` | `selectReturnMailList` (Select) <br> `insertIfRtmsMailQueue` (Insert) <br> `updateIfRtmsMailQueue` (Update) |\n\n"
        "### 3. 테이블 간 조인 및 연계 상세 설명\n"
        "* **`IF_RTMS_RECIPIENTINFO` (메일 수신자 정보)**\n"
        "  - **조인 키**: `IF_RTMS_MAILQUEUE.MID = IF_RTMS_RECIPIENTINFO.MID AND IF_RTMS_MAILQUEUE.SUBID = IF_RTMS_RECIPIENTINFO.SUBID`\n"
        "  - **설명**: 메일 한 건당 1:N의 관계를 가지며 실제 수신자(받는 이) 정보들이 맵핑됩니다.\n"
        "* **`TESFRVTB` (견적 요청 협력사 정보)**\n"
        "  - **연계 키**: `CHAIN_NO, ESTIM_TYPE_CD, ESTIM_FROM_CD, ESTIM_VENDOR`\n"
        "  - **설명**: 견적 요청서 이메일 발송 화면에서 메일 큐 입력과 동시에 본사 견적 협력사 정보 테이블의 이메일 전송 여부 상태(`ESTIM_SEND_YN = 'S'`)를 갱신합니다.\n"
        "* **`OBSLPHTB` (발주 헤더 테이블)**\n"
        "  - **연계 키**: `ORDER_DATE, MS_NO, SLIP_NO, SLIP_FG`\n"
        "  - **설명**: 본사 발주요청서 이메일 발송 완료 시 이 테이블의 발송 여부 상태(`PURCH_SEND_YN = 'S'`) 및 메일 주소를 갱신합니다."
    )

    data["tables"]["if_rtms_mailqueue"] = {
        "memo": if_rtms_mailqueue_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "mid": "메시지 아이디 (매장코드(6)_YYYYMMDDHH24MISS(14)_RANDOMSEQ(5) 형식)",
            "subid": "서브 아이디 (0부터 순차 일련번호)",
            "tid": "서비스 아이디 (0 : 고정값)",
            "sname": "발송자 명",
            "smail": "발송자 이메일 주소",
            "sid": "발송자 ID",
            "rpos": "대상자 추출 방법 (0: 테이블 직접 입력, 1: 쿼리 입력, 2: 파일)",
            "query": "대상자 추출 정보 (RPOS 1: 추출 쿼리, RPOS 2: 파일 경로)",
            "ctnpos": "메일 컨텐츠 위치 (0: DB HTML, 1: 웹 URL, 2: 파일 경로)",
            "subject": "메일 제목",
            "contents": "컨텐츠 템플릿 CLOB (CTNSPOS 0: HTML소스, 1: 웹 URL, 2: 파일)",
            "cdate": "예약 일자",
            "sdate": "메일 생성 일자",
            "status": "예약 항목 상태코드. (0: 예약, 1: 발송자주소에러, 2: 수신자주소에러, 3: 리스트추출실패, 5: 생성에러, Y: 생성완료)",
            "dbcode": "데이터베이스 연결 코드",
            "charset": "사용할 CHARSET (0: EUC-KR, 3: UTF-8)",
            "issecure": "0: 암호 안함, 1: 암호메일, 2: 암호 + 위변조",
            "securetemplate": "암호 사용 시 표지 템플릿 파일 경로",
            "attachfile01": "첨부파일1 경로",
            "attachfile02": "첨부파일2 경로",
            "attachfile03": "첨부파일3 경로",
            "attachfile04": "첨부파일4 경로",
            "attachfile05": "첨부파일5 경로",
            "create_dtime": "생성일시 (YYYYMMDDHH24MISS)",
            "if_yn": "인터페이스 처리 여부 (Y: 처리완료, N: 미처리)",
            "if_dtime": "인터페이스 처리 일시 (YYYYMMDDHH24MISS)",
            "return_yn": "반송알림 여부 (Y: 반송됨, N: 미반송)",
            "ori_mid": "원래 메시지 ID (반송 메일 처리 시 원본 메일 매핑용)"
        },
        "memo_c": "백오피스 화면에서 견적 요청 또는 발주 요청 시 이메일 발송 트랜잭션 내에서 등록됩니다.\n\n[백오피스 소스 코드]\n- 견적 전송: Hq_Esti_00004_Sql.xml (MyBatis ID: `insertEstiEmail`)\n- 발주 전송: Hq_Vendor_00003_Sql.xml (MyBatis ID: `insertPurchEmail`)\n\n[배치 소스 코드]\n- 반송 메일 알림 등록: ReturnMailInerface_SqlMapper.xml (MyBatis ID: `insertIfRtmsMailQueue`)",
        "memo_u": "메일 발송 완료 후 상태를 변경하거나 반송 처리가 일어날 때 업데이트됩니다.\n\n[백오피스 소스 코드]\n- 메일 연동: Pos_MailInterface_Sql.xml (MyBatis ID: `updateMail`)\n\n[배치 소스 코드]\n- 반송 메일 처리: ReturnMailInerface_SqlMapper.xml (MyBatis ID: `updateIfRtmsMailQueue`)",
        "memo_d": "과거 발송 완료된 로그 및 큐에 대해 정기 보관 연수가 지나면 영구 삭제 처리 등이 발생합니다.",
        "memo_r": "발송 대기중인 메일을 읽어들여 실제 SMTP 발송 서버로 전달하거나 반송 메일을 추적할 때 조회됩니다.\n\n[백오피스 소스 코드]\n- 메일 연동: Pos_MailInterface_Sql.xml (MyBatis ID: `selectMailList`)\n\n[배치 소스 코드]\n- 반송 메일 처리: ReturnMailInerface_SqlMapper.xml (MyBatis ID: `selectReturnMailList`)",
        "related_tables": [
            {
                "table_name": "if_rtms_recipientinfo",
                "description": "메일 수신자 정보 테이블. [조인 키: IF_RTMS_MAILQUEUE.MID = IF_RTMS_RECIPIENTINFO.MID AND IF_RTMS_MAILQUEUE.SUBID = IF_RTMS_RECIPIENTINFO.SUBID] 메일 한 건당 다수의 수신자를 1:N 관계로 관리하며 메일 발송 시 함께 참조됩니다."
            },
            {
                "table_name": "tesfrvtb",
                "description": "견적 요청 협력사 정보 테이블. [연계 키: CHAIN_NO, ESTIM_TYPE_CD, ESTIM_FROM_CD, ESTIM_VENDOR] 견적요청서 전송 화면(Hq_Esti_00004)에서 메일 전송 완료 시 이 테이블의 전송 여부 상태(ESTIM_SEND_YN = 'S')를 업데이트하여 이메일 발송 성공 여부와 동기화합니다."
            },
            {
                "table_name": "obslphtb",
                "description": "발주 헤더 테이블. [연계 키: ORDER_DATE, MS_NO, SLIP_NO, SLIP_FG] 본사 발주요청서 전송 화면(Hq_Vendor_00003)에서 거래처 발송 시 이 테이블의 발송 여부 상태(PURCH_SEND_YN = 'S') 및 주소를 연동합니다."
            },
            {
                "table_name": "if_recpsvtb",
                "description": "인터페이스 통계 로그 테이블. [연계 키: PROC_SEQ] 반송 메일 처리 배치 서비스(ReturnMailInerface)에서 처리 완료 후 데이터 정합성 확인 결과 카운트를 로깅할 때 PROC_SEQ 단위로 연계됩니다."
            }
        ]
    }

    # 3. IF_RTMS_RECIPIENTINFO MEMO
    if_rtms_recipientinfo_memo = (
        "### 1. 테이블 개요\n"
        "메일 수신자 정보 인터페이스 테이블 (`IF_RTMS_RECIPIENTINFO`).\n"
        "메일 발송 예약 건(`IF_RTMS_MAILQUEUE`)에 대해 발송 대상 수신자(받는 사람) 리스트를 1:N 관계로 관리하며 메일 실제 발송 시 연계 참조되는 테이블입니다.\n\n"
        "### 2. 백오피스 화면 & 배치 서비스 매핑\n"
        "이 테이블은 백오피스 메일 발송 화면과 메일 연동 데몬 모듈에서 공동 사용됩니다.\n\n"
        "| 연계 업무 | 물리 화면 / 모듈 | MyBatis Mapper XML 파일 | SQL ID |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **견적 요청서 수신자 등록** | 본사 견적요청서 발송 (`Hq_Esti_00004`) | `Hq_Esti_00004_Sql.xml` | `insertEstiRecipient` (Insert) |\n"
        "| **발주 요청서 수신자 등록** | 본사 발주요청서 발송 (`Hq_Vendor_00003`) | `Hq_Vendor_00003_Sql.xml` | `insertPurchRecipient` (Insert) |\n"
        "| **미발송 수신자 목록 조회** | 메일 전송 데몬 프로세스 | `Pos_MailInterface_Sql.xml` | `selectRecipientList` (Select) <br> `updateRecipient` (Update) |\n\n"
        "### 3. 테이블 간 조인 및 연계 상세 설명\n"
        "* **`IF_RTMS_MAILQUEUE` (메일 발송 예약 IF)와의 조인**\n"
        "  - **조인 형태**: 1:N 조인 (일대다 조인 / One-to-Many Join)\n"
        "  - **조인 키**: `IF_RTMS_MAILQUEUE.MID = IF_RTMS_RECIPIENTINFO.MID AND IF_RTMS_MAILQUEUE.SUBID = IF_RTMS_RECIPIENTINFO.SUBID`\n"
        "  - **설명**: 특정 예약 메시지(`MID`, `SUBID`)의 메일 본문에 매핑된 모든 수신자들을 조회하기 위해 필수 조인됩니다.\n\n"
        "### 4. 트리거 연동 정보\n"
        "* **트리거 사용 여부**: **해당 없음 (트리거 없음)**\n"
        "  - DB 수준의 TRIGGER가 아니라 자바 비즈니스 로직 트랜잭션 단에서 `IF_RTMS_MAILQUEUE`를 인서트한 후, 연속해서 `IF_RTMS_RECIPIENTINFO`에 수신처(RMAIL, RNAME)를 건별로 직접 INSERT하는 방식으로 동작합니다."
    )

    data["tables"]["if_rtms_recipientinfo"] = {
        "memo": if_rtms_recipientinfo_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "mid": "메시지 아이디 (매장코드(6)_YYYYMMDDHH24MISS(14)_RANDOMSEQ(5) 형식)",
            "subid": "서브 아이디 (0부터 순차 일련번호)",
            "tid": "서비스 아이디 (0 : 고정값)",
            "rid": "수신자 ID (메일 ID에서 도메인 제외한 영역)",
            "rname": "수신자 이름",
            "rmail": "수신자 이메일 주소",
            "create_dtime": "생성일시 (YYYYMMDDHH24MISS)",
            "if_yn": "인터페이스 처리 여부 (Y: 처리완료, N: 미처리)",
            "if_dtime": "인터페이스 처리일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "백오피스 화면에서 견적 요청 또는 발주 요청 시 이메일 발송 트랜잭션 내에서 등록됩니다.\n\n[백오피스 소스 코드]\n- 견적 수신자 등록: Hq_Esti_00004_Sql.xml (MyBatis ID: `insertEstiRecipient`)\n- 발주 수신자 등록: Hq_Vendor_00003_Sql.xml (MyBatis ID: `insertPurchRecipient`)",
        "memo_u": "메일 발송 완료 후 수신자 상태를 처리 완료 상태로 변경합니다.\n\n[백오피스 소스 코드]\n- 수신자 상태 변경: Pos_MailInterface_Sql.xml (MyBatis ID: `updateRecipient`)",
        "memo_d": "과거 발송 완료된 로그 및 큐에 대해 정기 보관 연수가 지나면 영구 삭제 처리 등이 발생합니다.",
        "memo_r": "발송 대기중인 수신자 목록을 읽어들여 실제 SMTP 발송 서버로 전달할 때 조회됩니다.\n\n[백오피스 소스 코드]\n- 수신자 목록 조회: Pos_MailInterface_Sql.xml (MyBatis ID: `selectRecipientList`)",
        "related_tables": [
            {
                "table_name": "if_rtms_mailqueue",
                "description": "메일 발송 예약 테이블. [조인 키: IF_RTMS_MAILQUEUE.MID = IF_RTMS_RECIPIENTINFO.MID AND IF_RTMS_MAILQUEUE.SUBID = IF_RTMS_RECIPIENTINFO.SUBID] 메일 내용과 수신처를 연결하기 위해 N:1 형태로 매핑 조인됩니다."
            }
        ]
    }

    # 4. IF_SEDPSVTB MEMO
    if_sedpsvtb_memo = (
        "### 1. 테이블 개요\n"
        "통합 매장별 인터페이스 로그 테이블 (`IF LOG TABLE`). Tibero에서 HMS PostgreSQL로 수신 또는 송신 처리되는 매장 단위 배치 작업(매장 발주, 본사 발주 이관 등)의 실행 이력과 점포별 데이터 건수(총 건수, 성공 건수), 에러 메시지(`REMARK`), 매장코드(`MS_NO`) 등을 기록하여 점포별 인터페이스 상태 모니터링에 활용됩니다.\n\n"
        "### 2. 배치 서비스 & XML 매퍼 상세 매핑\n"
        "각 배치 수신 서비스 및 연계 모듈이 매장별 루프를 돌면서 실행 결과를 `insertIfSedpsvtb` 쿼리를 통해 등록합니다.\n\n"
        "| 연계 업무 | 물리 화면 / 모듈 | MyBatis Mapper XML 파일 | SQL ID |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **본사 발주 이관 배치** | 발주 이관 배치 서비스 (`ObslService`) | `ObslInerface_SqlMapper.xml` | `insertIfSedpsvtb` (Insert) <br> `getReseultCount` (Select) |\n"
        "| **매장 발주요청 수신 배치** | 매장 발주요청 수신 배치 (`ShopObslService`) | `ShopObslInerface_SqlMapper.xml` | `insertIfSedpsvtb` (Insert) <br> `getReseultCount` (Select) |\n"
        "| **인터페이스 전송 에러 로깅** | 공통 에러 처리 프로시저 (`SUB_IF_HYDM_SEND_ERR_P`) | `Sp_SUB_IF_HYDM_SEND_ERR_P_Sql.xml` | `insert` (Insert) |\n\n"
        "### 3. 테이블 간 조인 및 연계 상세 설명\n"
        "* **`tsm_cty_buy_mst` (매장 매입 마스터 스테이징)**\n"
        "  - **조인 키**: `IF_SEDPSVTB.PROC_SEQ = TSM_CTY_BUY_MST.POS_SEND_SEQ`\n"
        "  - **설명**: 발주 이관 배치를 통해 스테이징 테이블로 이관된 전송 이력(`POS_SEND_SEQ`)과 `IF_SEDPSVTB`의 이력 로그(`PROC_SEQ`)가 매핑됩니다.\n"
        "* **`mmembstb` (가맹점 마스터)**\n"
        "  - **조인 키**: `IF_SEDPSVTB.MS_NO = MMEMBSTB.MS_NO`\n"
        "  - **설명**: 매장별 인터페이스 로그(`if_sedpsvtb.ms_no`)를 가맹점 마스터(`mmembstb.ms_no`)와 조인하여 점포명, 가맹점 정보를 노출하는 데 사용됩니다.\n"
        "* **`obslphtb` (발주 헤더 테이블)**\n"
        "  - **연계 키**: `PROC_SEQ` (인터페이스 처리 순번) 및 `MS_NO` (매장코드)\n"
        "  - **설명**: 배치가 돌면서 성공/실패 여부를 `if_sedpsvtb`에 기록하며, `obslphtb`의 `IF_PURCH_YN` 이나 `IF_PURCH_CANCEL_YN` 상태값과 연계됩니다.\n\n"
        "### 4. 트리거 연동 정보\n"
        "* **트리거 사용 여부**: **해당 없음 (트리거 없음)**\n"
        "  - 데이터베이스 수준의 `TRIGGER`에 의해 동작하는 것이 아니며, Java 배치 서비스 또는 에러 처리 프로시저(`SUB_IF_HYDM_SEND_ERR_P`)에서 비즈니스 트랜잭션 수행 도중 에러가 나거나 처리가 완료되었을 때 직접 SQL `INSERT`를 호출합니다."
    )

    data["tables"]["if_sedpsvtb"] = {
        "memo": if_sedpsvtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "if_api": "인터페이스 반영 ID / API ID (예: 'IF_FB_006', 'IF_FB_007')",
            "proc_date": "인터페이스 반영 조건 일자 (YYYYMMDD)",
            "proc_seq": "데이타 순번 (인터페이스 시퀀스 번호)",
            "proc_yn": "처리 구분 (Y: 성공, E: 에러)",
            "ms_no": "매장코드 (점포 코드)",
            "tot_cnt": "수신된 총 데이터 건수 (DATA CNT)",
            "success_cnt": "성공적으로 처리 완료된 데이터 건수",
            "remark": "처리 에러 메시지 또는 비고",
            "proc_dtime": "처리일시 (YYYYMMDDHH24MISS)",
            "proc_id": "처리자 ID (예: 'JAVA_BATCH', 'ASTEMS')"
        },
        "memo_c": "Java 배치 작업 또는 프로시저(SUB_IF_HYDM_SEND_ERR_P) 내에서 수신/송신 완료 및 에러 발생 시 등록됩니다.",
        "memo_u": "일반적으로 인터페이스 실행 이력 로그이므로 업데이트는 발생하지 않습니다.",
        "memo_d": "과거 로그 보관 주기에 맞춰 배치 삭제 처리 등을 수행할 수 있습니다.",
        "memo_r": "점포별 이관 현황 결과 조회 시 사용됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_cty_buy_mst",
                "description": "매장 매입 마스터 스테이징 테이블. [조인 키: IF_SEDPSVTB.PROC_SEQ = TSM_CTY_BUY_MST.POS_SEND_SEQ] 발주 이관 배치를 통해 스테이징으로 적재된 건의 전송 순번과 로깅 이력을 매핑합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [조인 키: IF_SEDPSVTB.MS_NO = MMEMBSTB.MS_NO] 매장 코드를 조인하여 가맹점 이름을 맵핑 노출할 때 연계됩니다."
            },
            {
                "table_name": "obslphtb",
                "description": "발주 헤더 테이블. [연계 키: PROC_SEQ, MS_NO] 발주 이관 배치가 성공/실패 여부를 IF_SEDPSVTB에 기록하며 발주서 헤더의 상태와 연계됩니다."
            }
        ]
    }

    # 5. IFSLRETB MEMO
    ifslretb_memo = (
        "### 1. 테이블 개요\n"
        "일자별 매출관련 현장마감 테이블 (`IFSLRETB`).\n"
        "가맹점/매장(`MS_NO`)의 영업일자별(`SALE_DATE`) 일일 마감 처리 내역(현장마감 여부 `MS_CLOSE_YN`, 마감입금액, 준비금 반환액, 현금매출액, 익일준비금, 과부족액 등)을 저장하고 검증하기 위한 인터페이스용 핵심 상태 제어 테이블입니다.\n\n"
        "### 2. 일 마감 진행 조건 (Closing Conditions)\n"
        "현장 마감 버튼을 클릭하면 내부 서비스(`Hq_Sysif_00001_Service.closeRegi`)에서 다음의 사전 조건 검증을 거친 후 마감을 수행합니다.\n"
        "* **매출-정산 건수 및 금액 일치 여부 (`billCntError`)**: `STRNHDTB` (매출 원장)와 `SAREGITB` (정산기 정산정보)의 건수 및 합계 금액 대조.\n"
        "* **당일 포스 로그인(오픈) 여부 (`LoginCntError`)**: `OPNPOSTB` (오픈 정보)와 `SAREGITB` (정산 내역) 매칭 확인.\n"
        "* **마감월 회계 마감 여부**: `MCLOSETB` (월 마감 여부 `CLS_YN = 'Y'` 일 때 마감 불가).\n\n"
        "### 3. 마감 진행 시 데이터 상태 변화 (`MS_CLOSE_YN`)\n"
        "* **`'N'` (미마감/현장마감 완료)**: 화면에서 현장마감 버튼 클릭 시 최초 진입 상태. 로컬 DB 마감 수치 적재 상태.\n"
        "* **`'Y'` (마감 성공/송신 성공)**: 로컬 DB 가공 적재 후 본사 Tibero DB 연동이 성공하면 변경되는 최종 상태.\n"
        "* **`'E'` (연동 실패/에러)**: 본사 DB API 연동 및 데이터 송신 중 오류(커넥션 단절, 중복 키 등) 발생 시 기록되는 오류 상태.\n\n"
        "### 4. 백오피스 화면 & POS 연동 매핑\n"
        "이 테이블은 백오피스 일일 마감 검증/조회 화면 및 POS 매출 데이터 이관 데몬 프로세스에서 공동으로 갱신/참조됩니다.\n\n"
        "| 연계 업무 | 물리 화면 / 모듈 | MyBatis Mapper XML 파일 | SQL ID |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **매장 현장 마감 검증 및 조회** | 매장현장마감검증 (`Hq_Sysif_00001`) | `Hq_Sysif_00001_Sql.xml` | `getRegiList` (Select) <br> `getDetailRegiList` (Select) <br> `saveRegiData` (Merge) <br> `closeRegi` (Merge) |\n"
        "| **시재 수신 연동** | 시재수신이관 (`Hq_Sysif_00002`) | `Hq_Sysif_00002_Sql.xml` | `getSaleEndCnt` (Select) <br> `updateSaleEnd` (Update) |\n"
        "| **POS 매출 연동 배치** | POS 매출 연동 모듈 | `Pos_SaleInterface_Sql.xml` | `updateClose` (Update) <br> `closeRegi` (Merge) |\n"
        "| **매장 이관 데이터 송신 프로시저** | 이관 송신 프로시저 | `Sp_SUB_IF_HYDM_SEND_P_Sql.xml` | `SUB_IF_HYDM_SEND_P` (Select 검증) |\n\n"
        "### 5. 테이블 간 조인 및 연계 상세 설명\n"
        "* **`saregitb` (정산기 정산정보)**\n"
        "  - **조인 형태**: Left Outer Join (`IFSLRETB.MS_NO(+) = SAREGITB.MS_NO AND IFSLRETB.SALE_DATE(+) = SAREGITB.SALE_DATE`)\n"
        "  - **설명**: 정산기에서 집계된 실제 현금 시재액과 현장 마감 완료 상태를 매핑하여 매출 과부족액(`OVER_AMT`) 등을 대조합니다.\n"
        "* **`mmembstb` (가맹점 마스터)**\n"
        "  - **조인 형태**: Inner Join\n"
        "  - **조인 키**: `IFSLRETB.MS_NO = MMEMBSTB.MS_NO`\n"
        "  - **설명**: 매장 코드를 조인하여 명칭(`MS_NM`) 및 가맹점 체인 정보를 가져옵니다.\n"
        "* **`strnhdtb` (매출 거래 헤더)**\n"
        "  - **연계 방식**: Group By 집계 연동\n"
        "  - **설명**: 영업일자별 매출 원장 헤더의 현금 매출 총합(`CASH_TOT`)을 집계해 정산 정보와 상호 대조합니다.\n"
        "* **`TSM_*` (회계 연동 테이블군)**\n"
        "  - **연계 방식**: 마감 성공(`MS_CLOSE_YN = 'Y'`) 시 로컬 DB `TSM_*` 데이터의 `POS_SEND_YN` 상태가 `'Y'`로 업데이트되며 본사 Tibero DB에 동기식으로 원격 Insert 적재됩니다.\n"
        "  - **대상 테이블**: `TSM_TRAN_MST`, `TSM_TRAN_DTL`, `TSM_SALS_AGG_MST`, `TSM_SHOP_DAYCLS_MST`, `TSM_CASH_RCPS_MST`.\n\n"
        "### 6. 마감 취소 및 원복 가이드\n"
        "마감을 취소하여 미마감 상태로 원복하려면 다음 작업을 수행해야 합니다:\n"
        "1. **마감 상태 초기화 (`IFSLRETB`)**:\n"
        "   `UPDATE hmsfns.IFSLRETB SET MS_CLOSE_YN = 'N', REMARK = ' ' WHERE SALE_DATE = '...' AND MS_NO = '...';`\n"
        "2. **연동 테이블 임시 데이터 삭제 (`TSM_*`)**:\n"
        "   `TSM_TRAN_MST`, `TSM_TRAN_DTL`, `TSM_SALS_AGG_MST`, `TSM_SHOP_DAYCLS_MST`, `TSM_CASH_RCPS_MST` 테이블에서 대상 영업일자의 미전송(`N`) 및 에러(`E`) 데이터를 삭제합니다. (이미 송신완료된 `Y` 건은 본사 DB 데이터 삭제와 연계 필수)"
    )

    data["tables"]["ifslretb"] = {
        "memo": ifslretb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "sale_date": "영업일자 (YYYYMMDD)",
            "ms_close_yn": "매장현장 마감 여부 (Y: 마감함, N: 마감안함)",
            "cl_deposit_amt": "마감입금액 (현금 시재 IF 시 29번 - 매출마감입금액)",
            "re_reserve_amt": "준비금반환액 (현금 시재 IF 시 51번 - 준비금반환액)",
            "sale_cahs_deposit_amt": "현금매출액 (21번)",
            "return_reserve_amt": "준비금환불 (52번)",
            "next_reserve_amt": "익일준비금 (53번)",
            "over_amt": "과부족액 (80번)",
            "remark": "비고 (프로시저 수행 오류 메시지 등)",
            "create_dtime": "최초 등록일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 수정일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정자 ID"
        },
        "memo_c": "백오피스 마감검증 화면 또는 POS 매출 연동 완료 트랜잭션 내에서 등록됩니다.",
        "memo_u": "현장 마감 완료 처리, 마감 금액 수정, 또는 시재 수신 연동 시 갱신됩니다.",
        "memo_d": "매출 마감 데이터이므로 영구 삭제는 거의 발생하지 않으며 정기 이월 처리됩니다.",
        "memo_r": "매장 마감 상태 확인 및 준비금/익일 시재액 검증 시 주로 조회됩니다.",
        "related_tables": [
            {
                "table_name": "saregitb",
                "description": "정산기 정산정보 테이블. [조인 키: IFSLRETB.MS_NO(+) = SAREGITB.MS_NO AND IFSLRETB.SALE_DATE(+) = SAREGITB.SALE_DATE] 실제 POS 정산기 현금 내역과 마감 여부 상태를 outer join하여 대조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [조인 키: IFSLRETB.MS_NO = MMEMBSTB.MS_NO] 매장 코드를 통해 가맹점 상세 정보(점명 등)를 연동합니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 거래 헤더 테이블. [연계 키: MS_NO, SALE_DATE] 영업일자의 원장 거래 내역과 대조하여 마감 및 시재 검증을 수행합니다."
            }
        ]
    }

    # 6. IMCRIOTB RELATED TABLES UPDATE
    if "imcriotb" in data["tables"]:
        # Redefine the full detailed related_tables for imcriotb
        data["tables"]["imcriotb"]["related_tables"] = [
            {
                "table_name": "tgoodstb",
                "description": "[현재고현황 조회 / 발주등록(hq_vendor_00005) / 폐기등록(hq_stock_00007) 화면] 재고 대상이 되는 마스터 상품 테이블입니다. 현재고 테이블의 상품코드(goods_cd)를 기준으로 N:1 조인(imcriotb.goods_cd = tgoodstb.goods_cd)하여 상품의 명칭, 규격, 분류 코드를 매핑해 조회합니다."
            },
            {
                "table_name": "imtrlgtb",
                "description": "[실시간 재고 반영 및 수불로그 검증 통합테스트] 재고의 입출고 변동 로그를 기록하는 수불 이력 테이블입니다. 매입 확정, 매출, 폐기 처리 등 재고 변동 사건 발생 시 imtrlgtb에 로그가 인서트됨과 동시에 imcriotb의 현재고 수량(cur_qty)이 실시간 업데이트되어 정합성을 유지합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "[현재고현황 조회 / 무발주 입고 관리 화면(hq_vendor_00009)] 현재고를 보유한 가맹 점포의 식별용 마스터 테이블입니다. 점포코드(ms_no) 조인을 통해 본사에서 가맹점별 보유 재고의 한글 점포명 및 체인 그룹별 재고 통계를 집계할 때 사용됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "[무발주 입고 관리 화면(hq_vendor_00009, st_vendor_00006)] 무발주 매입/입고의 상세 품목 규격 정보입니다. 입고 확정 시 obslpdtb의 입고 수량만큼 imcriotb의 현재고 수량이 증가하도록 트랜잭션이 연동되며, 무발주 입고 상세 내역 조회 시 매입한 상품의 매장 내 실시간 현재고를 대조하여 화면에 보여줍니다."
            },
            {
                "table_name": "imdusetb",
                "description": "[폐기관리(hq_stock_00007) / 폐기등록 화면] 가맹점의 폐기 정보를 기록하는 테이블입니다. 폐기 확정(proc_fg='1') 처리 시 DB 내부 트리거(IMDUSE_T01)가 기동하여, imdusetb의 상품 폐기 수량만큼 imcriotb 테이블의 실시간 현재고 수량(cur_qty) 및 원가 금액(cur_cost)을 즉각 감산 업데이트 연동합니다."
            },
            {
                "table_name": "imclostb",
                "description": "[재고 마감 관리 화면 / 월수불 마감 배치] 매장의 재고 마감 이력을 관리하는 테이블입니다. 매장별 재고 마감 배치 또는 마감 처리 화면 구동 시 imcriotb에 기록된 현재 재고 수량을 마감 마스터 테이블(imclostb)의 당월 기말 재고(end_qty) 및 익월 기초 재고(start_qty)로 매핑 적재하여 마감 장부를 마감 연동합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. [조인 키: IMCRIOTB.MS_NO = MGOODSTB.MS_NO AND IMCRIOTB.GOODS_CD = MGOODSTB.GOODS_CD (N:1 Join)] 매장별 상품 삭제 시 트리거(Tr_MGOODS_T01)가 작동하여 IMCRIOTB에서 해당 점포/상품의 현재고 데이터를 연쇄 삭제(Hard Delete)합니다."
            },
            {
                "table_name": "imrealtb",
                "description": "재고실사 테이블. [조인 키: IMCRIOTB.MS_NO = IMREALTB.MS_NO AND IMCRIOTB.GOODS_CD = IMREALTB.GOODS_CD] 재고실사 확정 화면(hq_stock_00005, st_stock_00001)에서 저장 시, IMCRIOTB의 장부 재고(CUR_QTY)와 매장의 실사 수량을 대조하여 과부족 수량 및 금액(MODIFY_QTY, MODIFY_COST)을 산출하는 기준이 됩니다."
            },
            {
                "table_name": "stckiotb",
                "description": "매장 간 재고 조정 및 이동 상세 테이블. [조인 키: IMCRIOTB.MS_NO = STCKIOTB.MS_NO AND IMCRIOTB.GOODS_CD = STCKIOTB.GOODS_CD] 매장 재고조정/이동 등록 화면(hq_stock_00007)에서 출고 또는 이동 처리 시, IMCRIOTB의 현재고(CUR_QTY) 수량을 체크하여 가용 재고 범위를 초과하지 않는지 검증합니다."
            },
            {
                "table_name": "immmiotb",
                "description": "월별 상품 수불 집계 테이블. [조인 키: IMCRIOTB.MS_NO = IMMMIOTB.MS_NO AND IMCRIOTB.GOODS_CD = IMMMIOTB.GOODS_CD] 월 수불 마감 및 선입선출 재고 정산 프로시저(SUB_STOCK_FIFO_MAIN_P) 실행 시, IMMMIOTB의 기말재고 및 기말원가 결과를 바탕으로 IMCRIOTB의 현재고 원가금액(CUR_COST)을 동기화 갱신(Update)합니다."
            },
            {
                "table_name": "mgmvdttb",
                "description": "점포 간 재고 이동 상세 테이블. [연계 키: GOODS_CD (매장 코드 매핑은 SEND_MS_NO 및 RECEIVE_MS_NO 기준)] 매장 간 재고 이동 등록 화면(St_Stock_00010)에서 출고 가용 수량을 확인하기 위해 IMCRIOTB의 현재고(CUR_QTY)를 조회합니다. 또한 점포 이동 확정(proc_fg='2') 처리 시 DB 트리거(MGMVHD_T01)가 작동하여 수불 데이터가 생성되고, 이에 따라 보내는 점포의 현재고는 차감, 받는 점포의 현재고는 가산 처리됩니다."
            },
            {
                "table_name": "mmssrctb",
                "description": "매장별 상품 바코드 테이블. [조인 키: IMCRIOTB.GOODS_CD = MMSSRCTB.GOODS_CD AND IMCRIOTB.MS_NO = MMSSRCTB.MS_NO] 매장 현고조회, 실사등록 및 판매 등록 시 바코드를 스캔하여 상품(GOODS_CD) 및 그 현재고를 추적하기 위해 N:1 매핑 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "시스템 명칭 코드 마스터 테이블. [조인 키: TGOODSTB.ORD_UNIT = MNAMEMTB.NM_CD (NM_FG='121') 또는 TGOODSTB.INV_UNIT = MNAMEMTB.NM_CD (NM_FG='122')] 재고실사등록 및 현고조회 시 재고 단위(박스, 낱개, EA 등)의 한글 표준 명칭을 매칭하여 출력하기 위해 조인 사용됩니다."
            },
            {
                "table_name": "mvndrgtb",
                "description": "매장 거래처별 상품 마스터 테이블. [조인 키: IMCRIOTB.GOODS_CD = MVNDRGTB.GOODS_CD AND IMCRIOTB.MS_NO = MVNDRGTB.MS_NO] 매장 현고조회 화면(st_master_00013) 등에서 특정 납품처/공급사별 취급 상품과 현재고를 매칭하여 필터링 조회하기 위한 연계 테이블입니다."
            },
            {
                "table_name": "mvndrmtb",
                "description": "매장 거래처 마스터 테이블. [조인 키: MVNDRGTB.VENDOR = MVNDRMTB.VENDOR AND MVNDRGTB.MS_NO = MVNDRMTB.MS_NO] 거래처 상품 매핑 테이블(mvndrgtb)을 매개로 하여, 현재고 현황 및 정산 시 공급업체의 한글 상호명(VENDOR_NM)을 매칭 노출하기 위해 outer join 연계됩니다."
            },
            {
                "table_name": "tmlclstb",
                "description": "상품 대분류 마스터 테이블. [연계 키: TGOODSTB.LCLASS_CD = TMLCLSTB.LCLASS_CD AND TGOODSTB.CHAIN_NO = TMLCLSTB.CHAIN_NO] 현재고 현황 및 수불 조회 시 상품 대분류 정보(LCLASS_NM)를 표시하기 위해 상품 마스터 테이블을 경유하여 조인 연계됩니다."
            },
            {
                "table_name": "tmmclstb",
                "description": "상품 중분류 마스터 테이블. [연계 키: TGOODSTB.LCLASS_CD = TMMCLSTB.LCLASS_CD AND TGOODSTB.MCLASS_CD = TMMCLSTB.MCLASS_CD AND TGOODSTB.CHAIN_NO = TMMCLSTB.CHAIN_NO] 현재고 현황 및 수불 조회 시 상품 중분류 정보(MCLASS_NM)를 표시하기 위해 상품 마스터 테이블을 경유하여 조인 연계됩니다."
            },
            {
                "table_name": "tmsclstb",
                "description": "상품 소분류 마스터 테이블. [연계 키: TGOODSTB.LCLASS_CD = TMSCLSTB.LCLASS_CD AND TGOODSTB.MCLASS_CD = TMSCLSTB.MCLASS_CD AND TGOODSTB.SCLASS_CD = TMSCLSTB.SCLASS_CD AND TGOODSTB.CHAIN_NO = TMSCLSTB.CHAIN_NO] 현재고 현황 및 수불 조회 시 상품 소분류 정보(SCLASS_NM)를 표시하기 위해 상품 마스터 테이블을 경유하여 조인 연계됩니다."
            },
            {
                "table_name": "tmssrctb",
                "description": "본사용 상품 바코드 마스터 테이블. [조인 키: IMCRIOTB.GOODS_CD = TMSSRCTB.GOODS_CD AND IMCRIOTB.CHAIN_MS_NO = TMSSRCTB.CHAIN_NO] 본사/체인 레벨의 상품 바코드 정보 테이블. 현재고 조회 및 바코드 연동 시 상품코드(GOODS_CD)에 해당하는 바코드 번호(SOURCE)를 조회하기 위해 N:1 매핑 조인됩니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. [조인 키: IMCRIOTB.GOODS_CD = TPRICETB.GOODS_CD AND IMCRIOTB.CHAIN_MS_NO = TPRICETB.CHAIN_NO] 상품별 판매가 및 공급가 단가 마스터 테이블. 현재고 보유 현황 및 재고 수량의 금액 환산(UCOST, FEE_RATE 등) 시, 유효 시작/종료 일자 기준의 단가 정보를 조인하여 산출하는 데 사용됩니다."
            },
            {
                "table_name": "tvndrgtb",
                "description": "본사 거래처별 상품 마스터 테이블. [조인 키: IMCRIOTB.GOODS_CD = TVNDRGTB.GOODS_CD AND IMCRIOTB.CHAIN_MS_NO = TVNDRGTB.CHAIN_NO] 본사/체인 기준의 거래처별 취급 상품 정보 테이블. 가맹점 현재고 현황 조회 및 본사 재고 실사 연동 시, 각 상품의 원천 공급 거래처(VENDOR) 정보를 조인하여 거래처별 재고 보유 상태를 조회할 때 연계됩니다."
            },
            {
                "table_name": "imddiotb",
                "description": "일수불 정보 테이블. [조인 키: IMCRIOTB.MS_NO = IMDDIOTB.MS_NO AND IMCRIOTB.GOODS_CD = IMDDIOTB.GOODS_CD] 일일 상품 수불 집계 테이블입니다. 영업일자별 수불 변동 사항을 일자별로 집계하여 저장하며, 월 마감 시 월수불 테이블(IMMMIOTB)과 함께 현재고(IMCRIOTB)의 정합성 검증 및 단수 조정을 처리하는 기준이 됩니다."
            },
            {
                "table_name": "imremstb",
                "description": "재고실사 마스터 테이블. [조인 키: IMCRIOTB.MS_NO = IMREMSTB.MS_NO] 매장 재고실사 등록 및 마감 여부(PROC_YN, CLOSE_YN)를 관리하며, 실사 확정 시 트리거(IMREMS_T01)가 작동하여 임시 실사 데이터(IMRETPTB)와 현재고(IMCRIOTB)를 기반으로 수불 마감(IMMMCLTB)을 적재하고 현재고 원가를 갱신 연동합니다."
            },
            {
                "table_name": "imretptb",
                "description": "재고실사 임시 등록 테이블. [조인 키: IMCRIOTB.MS_NO = IMRETPTB.MS_NO AND IMCRIOTB.GOODS_CD = IMRETPTB.GOODS_CD] 재고실사 등록 진행 중 임시 데이터를 수집하는 테이블로, 실사 마감 확정 시 현재고(IMCRIOTB.CUR_QTY) 수치 및 매장 단가를 읽어와 임시 데이터를 실사 확정 데이터(IMREALTB)로 가공 및 삽입(Insert)하는 데 연계됩니다."
            },
            {
                "table_name": "mgmvhdtb",
                "description": "점포 간 재고 이동 마스터 테이블. [조인 키: MGMVDTTB 및 MGMVHDTB 연동] 점포 간 재고 이동 시 마스터 전표의 확정 상태(PROC_FG = '2') 변경 시 트리거(MGMVHD_T01)가 기동되어 IMCRIOTB의 매장별 현재고를 출고지 차감 및 입고지 가산으로 분기 업데이트합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "매장 재고 조정/이동 헤더 테이블. [조인 키: STCKIOTB 및 STCKHITB 연동] 매장 내 재고 조정(폐기, 이동 등) 시 마스터 전표 정보와 상태를 기록하며, 상세 내역(STCKIOTB)에서 IMCRIOTB 현재고 수량을 가용한 한도 내에서 제어하는 용도의 최상위 테이블입니다."
            },
            {
                "table_name": "obslphtb",
                "description": "무발주 매입/입고 헤더 테이블. [조인 키: OBSLPDTB 및 OBSLPHTB 연동] 가맹점의 무발주 입고 확정 시 마스터 전표를 저장하고, 입고 상세(OBSLPDTB)의 품목 수량만큼 EDB 로컬 현재고(IMCRIOTB.CUR_QTY)를 증가 업데이트 연동하는 흐름을 관리합니다."
            },
            {
                "table_name": "tvndrmtb",
                "description": "본사 거래처 마스터 테이블. [조인 키: TVNDRGTB.VENDOR = TVNDRMTB.VENDOR AND TVNDRGTB.CHAIN_NO = TVNDRMTB.CHAIN_NO] 본사 기준 공급업체의 상호명 등 세부 인적 사항을 관리하며, 본사 재고 실사 및 가맹점 현재고 현황 조회 시 공급사 코드에 대응하는 한글 상호명을 매치 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "mpricetb",
                "description": "매장별 상품 단가 마스터 테이블. [조인 키: IMCRIOTB.GOODS_CD = MPRICETB.GOODS_CD AND IMCRIOTB.MS_NO = MPRICETB.MS_NO] 특정 가맹점별로 다르게 책정될 수 있는 입고/판매 단가 마스터입니다. 현재고 수량(CUR_QTY)에 대조하여 매장 자체 재고의 원가 금액(CUR_COST)을 산정하거나 수불 금액을 집계할 때 조인됩니다."
            },
            {
                "table_name": "sgoodmtb",
                "description": "상품 월 매출 집계 테이블. [조인 키: IMCRIOTB.GOODS_CD = SGOODMTB.GOODS_CD AND IMCRIOTB.MS_NO = SGOODMTB.MS_NO] 월 단위 상품 매출 실적을 집계하는 테이블입니다. 매장 상품 정보 수정 및 삭제 유효성 체크 시(chkSgoodmtb), 과거 매출 실적 여부와 함께 IMCRIOTB의 현재고 존치 여부를 사전 검증하기 위한 제약 조건 테이블로 연계됩니다."
            },
            {
                "table_name": "mmlclstb",
                "description": "매장별 상품 대분류 마스터 테이블. [연계 키: MGOODSTB.LCLASS_CD = MMLCLSTB.LCLASS_CD AND MGOODSTB.MS_NO = MMLCLSTB.MS_NO] 가맹점별로 독자적인 상품 분류 체계를 운영할 때, 해당 매장의 대분류 한글 명칭(LCLASS_NM)을 매장 상품 마스터(MGOODSTB)를 경유하여 현재고(IMCRIOTB)와 조인 연계합니다."
            },
            {
                "table_name": "mmmclstb",
                "description": "매장별 상품 중분류 마스터 테이블. [연계 키: MGOODSTB.LCLASS_CD = MMMCLSTB.LCLASS_CD AND MGOODSTB.MCLASS_CD = MMMCLSTB.MCLASS_CD AND MGOODSTB.MS_NO = MMMCLSTB.MS_NO] 가맹점별 상품 중분류 한글 명칭(MCLASS_NM)을 매장 상품 마스터(MGOODSTB)를 경유하여 현재고(IMCRIOTB)와 조인 연계합니다."
            },
            {
                "table_name": "mmsclstb",
                "description": "매장별 상품 소분류 마스터 테이블. [연계 키: MGOODSTB.LCLASS_CD = MMSCLSTB.LCLASS_CD AND MGOODSTB.MCLASS_CD = MMSCLSTB.MCLASS_CD AND MGOODSTB.SCLASS_CD = MMSCLSTB.SCLASS_CD AND MGOODSTB.MS_NO = MMSCLSTB.MS_NO] 가맹점별 상품 소분류 한글 명칭(SCLASS_NM)을 매장 상품 마스터(MGOODSTB)를 경유하여 현재고(IMCRIOTB)와 조인 연계합니다."
            },
            {
                "table_name": "tb_recipe",
                "description": "레시피 마스터 테이블. [조인 키: TGOODSTB.RECIPE_CD = TB_RECIPE.RECIPE_CD] 제조/레시피 상품(SET_FG = '2')의 레시피 기본 속성(수불 마감 여부 STOCK_YN 등)을 정의합니다. 제조 상품의 입출고/판매 발생 시 레시피 폭발(Explosion) 수불 프로시저(SUB_RECIPE_IO_P)를 거쳐, 연관된 개별 원부재료의 IMCRIOTB 현재고 수량을 감산/가산 갱신하는 비즈니스 기준이 됩니다."
            },
            {
                "table_name": "tb_recipe_goods",
                "description": "레시피 구성 상품 및 원자재 상세 테이블. [조인 키: TB_RECIPE_GOODS.RECIPE_CD = TGOODSTB.RECIPE_CD] 제조 상품을 구성하는 개별 원부자재 코드(GOODS_CD 또는 대체 자재 REPLACE_GOODS_CD)와 배합 비율 수량(WEIGHT / RECIPE_WEIGHT)을 저장합니다. 제조 상품 판매/이동 확정 시, 이 테이블에 지정된 배합 수량만큼 개별 원부자재들의 IMCRIOTB.CUR_QTY 현재고를 실시간으로 가감 수불 처리하는 핵심적인 BOM(Bill of Materials) 매핑 데이터입니다."
            }
        ]

    # 7. IMDDIOTB MEMO AND RELATED TABLES
    imddiotb_memo = (
        "### 1. 테이블 개요\n"
        "일일 상품 수불 집계 테이블 (`IMDDIOTB`).\n"
        "매장별(`MS_NO`), 영업일자별(`CREATE_DATE`), 상품코드별(`GOODS_CD`)로 일일 모든 입출고 거래 종류(매입, 매출, 반품, 폐기, 조정, 이동입고, 이동출고, 기타입고, 기타출고 등)에 따른 수량과 원가 금액을 집계하여 누적 관리하는 일수불 마스터 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 수불 집계 흐름\n"
        "* **수불 실적 일일 집계**: 당일 발생한 입출고 상세 로그(`IMTRLGTB`) 데이터를 기반으로 마감 시점에 상품 및 점포별로 SUM 집계하여 `IMDDIOTB` 테이블에 `MERGE INTO` 처리합니다.\n"
        "* **월 마감 및 롤업(Roll-up)**: 매월 말 재고 마감 배치 실행 시, 이 일수불 데이터(`IMDDIOTB`)를 월 단위로 합산 집계하여 월별 수불 테이블(`IMMMIOTB`)의 당월 기초(`START_QTY`), 당월 입출고 합계, 당월 기말(`END_QTY`) 수치로 이관 적재합니다.\n"
        "* **재고 정합성 확인**: 현재고 테이블(`IMCRIOTB.CUR_QTY`)과 일수불의 누적 수치 정합성을 상호 비교 검증하는 데이터 정합성 대조 표준으로 사용됩니다."
    )

    data["tables"]["imddiotb"] = {
        "memo": imddiotb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "create_date": "수불 집계 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "goods_cd": "상품코드 (자재 코드)",
            "chain_ms_no": "체인본사 매장코드",
            "purch_qty": "당일 매입 수량 (정상 매입액)",
            "purch_cost": "당일 매입 원가 금액",
            "purch_extra_cost": "매입 부대 비용",
            "return_qty": "당일 매입반품 수량",
            "return_cost": "당일 매입반품 금액",
            "sale_qty": "당일 매출 수량",
            "sale_cost": "당일 매출 원가 금액",
            "sale_extra_cost": "매출 부대 비용",
            "in_qty": "당일 기타입고 수량",
            "in_cost": "당일 기타입고 금액",
            "out_qty": "당일 기타출고 수량",
            "out_cost": "당일 기타출고 금액",
            "disuse_qty": "당일 재고폐기 수량",
            "disuse_cost": "당일 재고폐기 금액",
            "adjust_qty": "당일 재고조정 수량",
            "adjust_cost": "당일 재고조정 금액",
            "tin_qty": "당일 이동(이전)입고 수량 (레시피/세트 변동분 포함)",
            "tin_cost": "당일 이동(이전)입고 금액",
            "tout_qty": "당일 이동(이전)출고 수량",
            "tout_cost": "당일 이동(이전)출고 금액",
            "returndis_qty": "반품 폐기 수량",
            "returndis_cost": "반품 폐기 금액",
            "move_in_qty": "당일 점포간 이동입고 수량",
            "move_in_cost": "당일 점포간 이동입고 금액",
            "move_out_qty": "당일 점포간 이동출고 수량",
            "move_out_cost": "당일 점포간 이동출고 금액",
            "wholesale_qty": "도매 수량",
            "wholesale_cost": "도매 금액",
            "wholesale_rt_qty": "도매 반품 수량",
            "wholesale_rt_cost": "도매 반품 금액"
        },
        "memo_c": "영업 마감 배치 프로세스 구동 시 당일 원천 로그를 집계하여 신규 등록됩니다.",
        "memo_u": "당일 추가 거래 발생 및 마감 조정 배치 연동 시 갱신됩니다.",
        "memo_d": "과거 수불 대장이므로 영구 삭제는 불가하며 데이터 보관 정책에 따라 보관됩니다.",
        "memo_r": "일별 재고 수불 대장 조회 화면 및 본사 매출/수불 추이 대시보드 조회 시 호출됩니다.",
        "related_tables": [
            {
                "table_name": "immmiotb",
                "description": "월별 상품 수불 집계 테이블. [조인 키: IMDDIOTB.MS_NO = IMMMIOTB.MS_NO AND IMDDIOTB.GOODS_CD = IMMMIOTB.GOODS_CD] 월간 마감 배치/프로시저 가동 시 해당 월의 일수불 데이터(IMDDIOTB)를 최종적으로 롤업(Roll-up) 집계하여 월별 수불 대장의 기초/기말 및 당월 누적 합계 수치를 생성하는 데 연계됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "[일별 재고 수불 대장 조회 화면] 재고 물류 수불의 주체가 되는 기준 상품 테이블입니다. 수불 테이블의 상품코드(goods_cd)를 기준으로 N:1 조인(imddiotb.goods_cd = tgoodstb.goods_cd)하여 상품의 명칭, 분류, 포장 단위 정보를 화면에 매핑 표출합니다."
            },
            {
                "table_name": "imtrlgtb",
                "description": "[일별 수불 실적 집계 배치] 재고의 실시간 상세 입출고 거래 로그를 보관하는 원천 정보입니다. 매 영업 마감 시 그날 적재된 상세 수불 이력(imtrlgtb)의 변동액을 상품/매장 단위로 SUM 집계하여 당일 날짜의 일수불(imddiotb) 실적으로 적재 처리하는 연동 관계를 지닙니다."
            },
            {
                "table_name": "mmembstb",
                "description": "[일별 점포 수불 분석 대시보드 화면] 일별 수불 실적이 누적되는 발원 점포의 마스터 테이블입니다. 점포코드(ms_no) 조인을 통해 본사에서 가맹점별 일별 수불 총량(매입량, 매출량 등)의 추이와 점포별 재고 흐름을 분석할 때 연동됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "현재고 정보 테이블. [조인 키: IMDDIOTB.MS_NO = IMCRIOTB.MS_NO AND IMDDIOTB.GOODS_CD = IMCRIOTB.GOODS_CD] 현재 보유 중인 물리 재고 실시간 수치와 대조하여 일수불 변동 이력과의 수량 정합성을 상호 검증 및 비교 대조하는 데 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. [조인 키: IMDDIOTB.MS_NO = MGOODSTB.MS_NO AND IMDDIOTB.GOODS_CD = MGOODSTB.GOODS_CD] 매장별 전용 취급 단가 및 상품 설정에 따른 일별 수불 통계를 개별 점포 조건에 맞춰 필터링 및 조회하기 위해 N:1 조인됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "무발주 입고 상세 테이블. [조인 키: IMDDIOTB.MS_NO = OBSLPDTB.MS_NO AND IMDDIOTB.GOODS_CD = OBSLPDTB.GOODS_CD] 가맹점 무발주 매입/입고 처리 시 당일 입고 확정된 수량과 원가가 일수불 테이블의 매입(purch_qty, purch_cost) 항목으로 집계 적재되는 원천 거래 정보입니다."
            },
            {
                "table_name": "mgmvdttb",
                "description": "점포 간 재고 이동 상세 테이블. [조인 키: IMDDIOTB.GOODS_CD = MGMVDTTB.GOODS_CD] 점포 간 이동 전표 확정(proc_fg = '2') 처리 시, 발생한 이동 수량이 일수불 테이블의 이동입고(move_in_qty) 및 이동출고(move_out_qty) 항목으로 가감 처리되는 데이터 원천입니다."
            },
            {
                "table_name": "imdusetb",
                "description": "매장 재고 폐기 테이블. [조인 키: IMDDIOTB.MS_NO = IMDUSETB.MS_NO AND IMDDIOTB.GOODS_CD = IMDUSETB.GOODS_CD] 매장 폐기 확정 처리 시, 발생한 손실 수량 및 금액이 일수불 테이블의 폐기(disuse_qty, disuse_cost) 수치로 일자별 누적 반영되는 직접적인 원천 정보입니다."
            },
            {
                "table_name": "stckiotb",
                "description": "재고 조정/이동 상세 테이블. [조인 키: IMDDIOTB.MS_NO = STCKIOTB.MS_NO AND IMDDIOTB.GOODS_CD = STCKIOTB.GOODS_CD] 매장 재고 조정(실사 차이 보정 등) 확정 시, 조정 수량과 금액이 일수불 테이블의 조정(adjust_qty, adjust_cost) 필드에 가감 반영되는 연동 대상 테이블입니다."
            },
            {
                "table_name": "imretptb",
                "description": "재고실사 임시 등록 테이블. [조인 키: IMDDIOTB.MS_NO = IMRETPTB.MS_NO AND IMDDIOTB.GOODS_CD = IMRETPTB.GOODS_CD] 재고 실사 마감 및 조정 과정에서 당일까지의 일수불 집계 데이터(IMDDIOTB)와 실사 임시 입력 정보(IMRETPTB)를 비교하여 수량 차이를 검증하고 재고 조정을 반영하기 위해 연계됩니다."
            },
            {
                "table_name": "mmembvtb",
                "description": "가맹점 상세 마스터(부가정보) 테이블. [조인 키: IMDDIOTB.MS_NO = MMEMBVTB.MS_NO] 각 매장의 매입 단가 정책 구분코드(USUPRICE_FG 등)를 확인하여 일수불 계산 시 낱개/묶음 단가 적용 여부를 규정하고, 일별 수불 단가 밸류에이션을 연산할 때 기준으로 참조됩니다."
            },
            {
                "table_name": "mmssrctb",
                "description": "매장별 상품 바코드 테이블. [조인 키: IMDDIOTB.GOODS_CD = MMSSRCTB.GOODS_CD AND IMDDIOTB.MS_NO = MMSSRCTB.MS_NO] 매장에서 일일 재고 수불 현황 조회 시, 스캔한 바코드 번호(SOURCE)를 상품코드(GOODS_CD)로 변환하여 해당하는 일수불 데이터를 매핑 조회하는 검색 인덱스로 연계 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "시스템 명칭 코드 마스터 테이블. [조인 키: TGOODSTB 단위를 통해 매칭] 일별 재고 수불 대장 조회 화면에서 각 품목의 수불 규격 단위(박스, 낱개, 용기 등) 한글 표준 명칭을 매핑하여 출력하는 용도의 코드 테이블입니다."
            },
            {
                "table_name": "tmssrctb",
                "description": "본사용 상품 바코드 테이블. [조인 키: IMDDIOTB.GOODS_CD = TMSSRCTB.GOODS_CD] 본사 백오피스 일별 수불 분석 및 리포트 조회 시 바코드 검색을 통해 상품별 일별 입출고 수량 흐름을 추적할 때 N:1 조인되어 연동됩니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. [조인 키: IMDDIOTB.GOODS_CD = TPRICETB.GOODS_CD] 일별로 발생하는 수불 내역(입고, 이전 등)의 단가 금액(UCOST)을 유효일자별로 환산하여 집계할 때, 기준 공급단가와 수수료율 등을 대조 조회하기 위해 연계됩니다."
            }
        ]
    }

    # 8. IMDUSETB MEMO AND RELATED TABLES
    imdusetb_memo = (
        "### 1. 테이블 개요\n"
        "매장 재고 폐기 등록 상세 테이블 (`IMDUSETB`).\n"
        "매장별(`MS_NO`), 폐기등록 번호(`IDX` 및 `DISUSE_SEQ`), 상품코드별(`GOODS_CD`)로 유통기한 만료, 제품 손상, 원료 변질 등의 폐기 수량(`DISUSE_QTY`)과 폐기 원가 금액(`DISUSE_COST`) 및 폐기 사유(`REASON_CD`)를 기록하고 관리하는 상세 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 재고/수불 반영 흐름\n"
        "* **폐기 확정 시 자동 수불 분기 (Trigger `IMDUSE_T01`)**:\n"
        "  - 일반 자재/상품 폐기 시: 해당 품목 자체에 대해 `SUB_IMTRLG_I`를 호출하여 재고수불이력(`IMTRLGTB`)에 폐기 유형(`PROC_FG = 'D'`)으로 적재됩니다.\n"
        "  - 제조(레시피) 상품(`SET_FG = '2'`) 폐기 시: 구성 원부자재 목록(`TB_RECIPE_GOODS`)을 폭발시켜, 구성 자재들의 배합량(`RECIPE_WEIGHT`)만큼 각각 개별 자재의 `IMTRLGTB` 폐기 처리를 자동으로 수행합니다.\n"
        "  - 세트 상품(`SET_FG = '3'`) 폐기 시: 세트 구성 상세(`TB_SET_GOODS`)에 정의된 하위 품목별 비율에 맞춰 각각 분할 폐기 수불을 기동합니다.\n"
        "* **실시간 재고 차감**: 수불이력(`IMTRLGTB`) 적재 시점과 연동되어 현재고 테이블(`IMCRIOTB.CUR_QTY` 및 `CUR_COST`)에서 실시간으로 폐기 수량/원가만큼 재고를 차감 갱신합니다.\n"
        "* **일수불/월수불 마감 집계**: 일 마감 시 일수불(`IMDDIOTB`), 월 마감 시 월수불(`IMMMIOTB`) 테이블의 당일/당월 폐기 누적 실적(`disuse_qty`, `disuse_cost`)으로 집계 적재됩니다.\n\n"
        "### 3. 연계 웹 화면 정보\n"
        "* **`st_stock_00003`** : [매장] [재고관리 > 조정/폐기/실사] 폐기등록 화면 (폐기 임시 저장, 삭제 및 확정 처리 실행)\n"
        "* **`st_stock_00004`** : [매장] [재고관리 > 조정/폐기/실사] 폐기현황 화면 (일자별, 사유별 폐기 이력 목록 조회)\n"
        "* **`hq_stock_00007`** : [본사] [재고관리 > 폐기관리] 본사 폐기등록 화면 (본사 재고 폐기 등록 및 마감 통제)\n"
        "* **`hq_stock_00008`** : [본사] [재고관리 > 폐기관리] 본사 폐기현황 화면 (전 매장 폐기 통계 및 이력 통합 리포팅)"
    )

    data["tables"]["imdusetb"] = {
        "memo": imdusetb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "idx": "폐기 등록 번호 (시퀀스 결합)",
            "ms_no": "매장코드 (점포 코드)",
            "goods_cd": "상품코드 (자재 코드)",
            "chain_ms_no": "체인본사 매장코드",
            "disuse_qty": "폐기 수량",
            "disuse_cost": "폐기 원가 금액",
            "create_dtime": "등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "등록자 ID",
            "remark": "비고 / 특이사항 내용",
            "proc_fg": "처리상태 구분 (0:등록, 1:확정, 2:미확정)",
            "create_fg": "등록구분 (W:웹 등록, H:핸디터미널 스캔등록)",
            "disuse_seq": "폐기 일련번호",
            "last_dtime": "최종 수정 일시",
            "last_id": "최종 수정자 ID",
            "div_fg": "반품폐기 구분 (0:일반폐기, 1:반품폐기)",
            "reason_cd": "폐기 사유 코드 (공통코드 902번 매핑)",
            "disuse_date": "폐기 일자 (YYYYMMDD)",
            "confirm_id": "확정/승인자 ID"
        },
        "memo_c": "웹 또는 핸디터미널을 통해 새로운 자재 폐기 전표를 임시 등록(proc_fg = '0')할 때 삽입됩니다.",
        "memo_u": "임시 상태의 전표 수정 및 최종 폐기 확정(proc_fg = '1') 처리 시 상태 값이 업데이트됩니다.",
        "memo_d": "확정 이전의 임시 등록 건에 한해 물리 삭제가 가능하며, 확정 이후에는 수불 정합성 유지를 위해 삭제가 불가합니다.",
        "memo_r": "점포 재고 폐기 등록 및 이력 조회 화면, 폐기 원가 리포트 화면 등에서 다각도로 조회 연계됩니다.",
        "related_tables": [
            {
                "table_name": "imtrlgtb",
                "description": "재고 수불 이력 테이블. 폐기 등록 확정(PROC_FG = '1') 시, 테이블 트리거(IMDUSE_T01)가 자동으로 동작하여 폐기 수량(DISUSE_QTY)과 원가 금액(DISUSE_COST)에 해당하는 수불 로그를 폐기 구분코드(PROC_FG = 'D')로 직접 삽입(Insert) 연동합니다."
            },
            {
                "table_name": "imcriotb",
                "description": "현재고 정보 테이블. 폐기 확정을 통해 IMTRLGTB에 적재된 폐기 수량만큼 실시간으로 EDB 물리 현재고(IMCRIOTB.CUR_QTY) 및 자재 원가 금액(CUR_COST)을 즉각 차감 업데이트 반영하는 직접적인 연계 대상입니다."
            },
            {
                "table_name": "imddiotb",
                "description": "일일 상품 수불 집계 테이블. 매일 마감 배치 가동 시 당일 확정된 폐기 품목과 수량/금액(DISUSE_QTY, DISUSE_COST)을 합산 집계하여 일수불 원장의 폐기 필드(disuse_qty, disuse_cost)에 누적 반영합니다."
            },
            {
                "table_name": "immmiotb",
                "description": "월별 상품 수불 집계 테이블. 월 마감 시 일수불 테이블(IMDDIOTB)에 기록된 일별 폐기 실적을 최종 취합하여 월 수불 대장의 당월 폐기 누계 수치로 저장/이관하는 연쇄 롤업 관계입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 폐기 등록 상세 화면 및 리포트 조회 시 폐기 상품코드에 대조하여 상품 한글 표준명(GOODS_NM), 규격, 바코드 분류 및 세트/레시피 구성 구분코드(SET_FG)를 매핑하기 위해 N:1 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 매장별로 취급 가능한 상품 마스터 설정을 참조하며, 폐기 등록 시 가맹점 전용 판매 상품인지 여부와 개별 세트/레시피 조립 정보를 확인하기 위해 사용됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 폐기 등록을 실행한 점포의 매장번호(MS_NO), 매장명(MS_NM) 및 해당 점포가 소속된 체인본사 식별코드(CHAIN_NO)를 매치하고 권한을 필터링하기 위해 연동 조인됩니다."
            },
            {
                "table_name": "mmembvtb",
                "description": "가맹점 상세 부가정보 테이블. 매장별 폐기 거래 원가 정산 시, 가맹점의 부가 정보 마스터에 기재된 특정 매입단가 적용 정책 및 영세율 구분코드 등을 조회하여 수불 회계 단가 집계 로직을 보정하는 데 활용됩니다."
            },
            {
                "table_name": "mmssrctb",
                "description": "매장별 상품 바코드 테이블. 매장 현장에서 휴대용 단말기(핸디터미널 create_fg = 'H')나 매장 웹을 통해 자재 폐기 등록 시, 바코드 스캔 값을 해당하는 로컬 자재/상품 코드로 빠르게 매핑 식별해 주는 역할을 담당합니다."
            },
            {
                "table_name": "tmssrctb",
                "description": "본사 기준 상품 바코드 마스터 테이블. 본사 백오피스 폐기 리포트 화면에서 표준 바코드로 폐기된 자재 품목을 조회/검색할 때 N:1 조인되어 인덱스 검색 매핑을 수행합니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. 폐기 발생 일자(DISUSE_DATE)에 유효한 본사 표준 공급단가 또는 견적단가를 판별하여, 폐기로 인한 매장 손실 원가 금액(DISUSE_COST)을 산정할 때 기준 단가 테이블로 조인 참조됩니다."
            },
            {
                "table_name": "mpricetb",
                "description": "매장별 상품 단가 마스터 테이블. 매장별로 자체 적용되는 매장 전용 유효 단가를 적용하여 개별 매장에 특화된 폐기 손실 금액(DISUSE_COST)을 계산 및 확정할 때 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 폐기 상세에 기록된 폐기사유코드(REASON_CD)에 대응하는 한글 명칭(예: 유통기한 경과, 파손, 변질 등 - 코드군 902)과 단위 구분 명칭을 화면에 매핑하여 출력하는 기준 데이터입니다."
            },
            {
                "table_name": "tb_recipe",
                "description": "레시피 마스터 테이블. 폐기 대상이 제조 상품(SET_FG = '2')인 경우, 실제 마감 처리 대상 레시피인지를 트리거에서 파악하여 연계된 하위 원자재 목록을 폭발(Explosion)시키기 위한 기본 관계 정보입니다."
            },
            {
                "table_name": "tb_recipe_goods",
                "description": "레시피 구성 자재 상세 테이블. 제조 상품 폐기 확정 시, 해당 상품을 만들기 위해 들어가는 개별 원부자재 코드와 배합량(RECIPE_WEIGHT)을 확인하여, 각 원부재료에 해당하는 자재 재고 수불(IMTRLGTB)을 배합 비율만큼 나누어 발생(차감)시키는 데 직접 연계됩니다."
            },
            {
                "table_name": "tb_set_goods",
                "description": "세트 구성 테이블. 폐기 대상 상품이 묶음/세트 상품(SET_FG = '3')인 경우, 세트 하위에 연결된 개별 일반 상품 및 제조용 원자재 구성 비율(SET_QTY)을 확인하여 자재별 분할 폐기 수불을 발생시키기 위해 조인 연계됩니다."
            },
            {
                "table_name": "imremstb",
                "description": "재고실사 마스터 테이블. 점포 실사 마감 확정 프로세스 진행 시, 실사일 이전까지 확정되지 않은 폐기 임시 내역(PROC_FG = '0')이 존재하는지 검증하고 실사 마감 이전에 미처리 폐기를 강제로 정리/제어하기 위해 연계됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 정보 테이블. 폐기를 최초 등록한 작업자(CREATE_ID) 및 최종 확정/승인한 책임자(CONFIRM_ID)의 한글 실명과 부서 직책을 화면에 출력하고 감사 로그를 추적할 때 조인됩니다."
            }
        ]
    }

    # 9. IMGMSTTB MEMO AND RELATED TABLES
    imgmsttb_memo = (
        "### 1. 테이블 개요\n"
        "이미지 마스터 테이블 (`IMGMSTTB`).\n"
        "매장에 등록되는 상품 이미지, 브랜드 이미지, 혹은 터치키 레이아웃 배치용 이미지 파일의 물리 경로(`IMAGE_PATH`)와 실제 저장 파일명(`IMAGE_FILE`)을 유니크한 이미지 코드 식별자(`IMAGE_IDX`)를 기준으로 등록하여 중앙 관리하는 이미지 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 이미지 매핑 반영 흐름\n"
        "* **터치키 이미지 등록 및 매핑**: 매장 터치키 이미지 등록 화면(`st_master_00014`)에서 신규 이미지를 업로드(Insert)하고, 매장 상품 마스터(`MGOODSTB`)의 이미지 코드(`IMAGE_IDX`)를 매핑 업데이트(`updatePluImage`)하여 POS의 터치 버튼 이미지로 표출시킵니다.\n"
        "* **업로드 파일 속성 동기화**: 서버에 파일 업로드 처리 시, 원본 파일명 및 상세 메타 정보(`FILEUPTB`)를 동적 연계하여 이미지 마스터 레코드와 정합성을 유지합니다.\n"
        "* **모바일 오더 및 POS 연동**: 이미지 마스터에 등록된 파일명과 경로는 모바일 앱 API 엔드포인트(`goodsimgUrl`) 및 POS 수신 배치 서비스를 통해 모바일 메뉴판 및 POS 화면에 이미지를 출력할 때 원천 주소로 호출됩니다.\n\n"
        "### 3. 연계 웹 화면 정보\n"
        "* **`st_master_00014`** : [매장] [POS마스터관리 > 터치키설정] 터치키 상품 이미지 등록 화면 (POS 터치키의 상품 버튼 이미지 파일 업로드 및 이미지 마스터 연동 등록/삭제 처리)\n"
        "* **모바일 오더 이미지 API (`/api/mobile/goodsimgUrl`)** : 모바일 주문 앱/웹 오더 화면에서 대표 상품 이미지를 스트리밍 출력하기 위해 이미지 마스터 정보를 참조하는 API 엔드포인트"
    )

    data["tables"]["imgmsttb"] = {
        "memo": imgmsttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "image_idx": "이미지 코드 (IMAGE_TYPE + 일련번호 9자리)",
            "image_type": "이미지 구분 (G: 상품 이미지, B: 브랜드 이미지 등)",
            "image_path": "서버 내 이미지 저장 디렉토리 상대 경로",
            "image_file": "물리 이미지 파일명 (구분+일련번호+타임스탬프+확장자)",
            "create_dtime": "등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "등록자 ID",
            "last_dtime": "최종 수정 일시",
            "last_id": "최종 수정자 ID"
        },
        "memo_c": "백오피스 터치키 이미지 등록 화면 등에서 신규 상품/터치키 버튼 이미지 업로드 시 인서트됩니다.",
        "memo_u": "동일 이미지 코드에 대한 파일 수정 업로드 시 이미지 파일 정보가 갱신됩니다.",
        "memo_d": "해당 이미지 코드를 참조하는 상품이나 터치키 배치가 전혀 존재하지 않을 경우에 한해 삭제가 가능합니다.",
        "memo_r": "POS 터치키 설정 화면, 모바일 주문 앱용 이미지 반환 API 등에서 이미지 경로를 조립하기 위해 수시로 조회됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [조인 키: TGOODSTB.IMAGE_IDX = IMGMSTTB.IMAGE_IDX] 본사에 등록된 상품별 표준 대표 이미지 정보를 연계하며, 상품 등록/수정 시 업로드된 이미지 코드를 상품 마스터 레코드에 매핑 저장합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. [조인 키: MGOODSTB.IMAGE_IDX = IMGMSTTB.IMAGE_IDX] 본사로부터 전송받은 매장별 개별 상품정보 상의 대표 이미지 코드를 보유하며, 모바일 주문 앱 이나 POS 터치키에서 표시할 상품의 이미지 경로를 참조할 때 조인 연계됩니다."
            },
            {
                "table_name": "fileuptb",
                "description": "파일 업로드 관리 테이블. [연계 키: IMGMSTTB.IMAGE_FILE = FILEUPTB.STORED_FILE_NM] 서버에 실제로 업로드되어 물리적으로 생성된 이미지 파일의 물리 경로, 바이트 크기, 원본 파일명 등의 시스템 상세 속성을 대조 조회하는 데 연계됩니다."
            },
            {
                "table_name": "mmcplktb",
                "description": "매장별 터치키 PLU 링크 테이블. [조인 키: MMCPLKTB.GOODS_CD = MGOODSTB.GOODS_CD] 매장 POS의 터치 키 배치 설정에 매핑된 상품에 대해, POS 터치 화면에 띄울 메뉴 이미지 파일 경로(IMAGE_PATH + IMAGE_FILE)를 화면에 매핑 표출하기 위해 3자 조인 연계됩니다."
            },
            {
                "table_name": "tmcplktb",
                "description": "본사 터치키 PLU 링크 테이블. [조인 키: TMCPLKTB.GOODS_CD = TGOODSTB.GOODS_CD] 본사에서 매장 POS로 내릴 표준 터치키 레이아웃 배치 등록 시, 개별 메뉴 버튼 위에 들어갈 이미지를 본사 표준 상품 이미지 마스터와 조인하여 관리합니다."
            },
            {
                "table_name": "mmcplutb",
                "description": "매장 터치키 그룹 PLU 테이블. 터치키 그룹별 상품 매핑 시, 포스에 전송할 상품 대표 이미지 주소를 추출하기 위해 상품 마스터를 거쳐 이미지 마스터와 간접 조인 연계됩니다."
            },
            {
                "table_name": "tmprgdtb",
                "description": "매장별 가격 등급 설정 테이블. 상품 대표 이미지 등록 화면(st_master_00014)에서 각 매장별 상품 목록을 조회하고 이미지 매핑을 업데이트할 때 매장 상품의 가격 등급 정보를 매치 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "tprcgdtb",
                "description": "체인 가격 등급 정의 테이블. 이미지 등록 대상인 매장별 상품의 단가 유형과 판매 단가 매칭 상태를 함께 대시보드로 표출하기 위해 이미지 마스터 및 상품 단가 정보와 함께 연관 조회됩니다."
            },
            {
                "table_name": "mpricetb",
                "description": "매장별 상품 단가 마스터 테이블. POS 터치키 이미지 등록 화면에서 메뉴 버튼에 들어갈 이미지와 함께 해당 상품의 현재 판매단가를 같이 렌더링하고 동시 설정할 때 조인됩니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. 본사 터치키 등록 및 이미지 단가 매핑 테이블 조회 시 유효 단가 정보와 본부 공급가를 매치 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 터치키 이미지 설정 권한을 제한하거나, 해당 매장에 등록된 터치키 상품 목록을 점포 단위로 분류 조회할 때 사용됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 이미지 유형 구분코드(G: 상품, B: 브랜드 등) 및 상품의 분류 한글 명칭을 이미지 매핑 정보와 매치하여 코드 라벨을 출력하는 용도로 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "백오피스 사용자 마스터 테이블. 이미지 마스터에 신규 이미지를 업로드하고 링크를 생성한 작업자(CREATE_ID, LAST_ID)의 실명과 계정 상태를 추적할 때 조인됩니다."
            },
            {
                "table_name": "tsubmntb",
                "description": "본사 부가메뉴 마스터 테이블. 사이드 메뉴나 옵션 메뉴(토핑 등)의 대표 이미지를 이미지 마스터에 등록하여 POS 및 모바일 키오스크 상의 옵션 선택 화면에 시각적으로 띄우기 위해 연관 조인됩니다."
            },
            {
                "table_name": "msubmntb",
                "description": "매장 부가메뉴 마스터 테이블. 매장 전용 옵션 메뉴들의 개별 대표 이미지를 매장별 이미지 마스터와 조인하여 모바일 오더 화면에 바인딩하기 위해 연계됩니다."
            }
        ]
    }

    # 10. IMMMIOTB MEMO AND RELATED TABLES
    immmiotb_memo = (
        "### 1. 테이블 개요\n"
        "월별 상품 수불 집계 테이블 (`IMMMIOTB`).\n"
        "매장별(`MS_NO`), 마감월별(`CREATE_MONTH`), 상품코드별(`GOODS_CD`)로 한 달 동안 발생한 모든 재고 수불 내역(기초, 기말, 매입, 매출, 폐기, 조정, 이동입고, 이동출고, 반품 등)의 누적 수량과 원가 평가 금액을 집계하여 최종 재고자산을 평가하는 월간 수불 대장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 재고/수불 마감 흐름\n"
        "* **월간 마감 및 수불 롤업(Roll-up)**: 매월 말 재고 마감 배치(`SUB_STOCK_FIFO_MAIN_P`) 가동 시 당월 1일부터 말일까지 적재된 일수불 데이터(`IMDDIOTB`)와 상세 로그(`IMTRLGTB`)를 월 단위로 합산 집계하여 당월 입출고 합계를 산출하고 `IMMMIOTB`에 저장합니다.\n"
        "* **원가 및 기말 재고 평가 (FIFO / 총평균법)**: 재고실사 확정 데이터(`IMREALTB`)와 월중 입고 내역을 대조하여 기말재고 수량(`END_QTY`) 및 기말 평가액(`END_COST`)을 산정하며, 선입선출 또는 총평균 알고리즘(`SUB_TOT_AVG_P`)을 통해 당월 매출원가와 월말 재고자산 가치를 평가합니다.\n"
        "* **차월 기초 자동 이월**: 마감 확정 시 당월의 기말 데이터가 다음 달의 기초 데이터(`START_QTY`, `START_COST`)로 자동 삽입(`insertNextImmmiotb`)되어 회계 연쇄성을 유지합니다."
    )

    data["tables"]["immmiotb"] = {
        "memo": immmiotb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "create_month": "수불 마감 년월 (YYYYMM)",
            "ms_no": "매장코드 (점포 코드)",
            "goods_cd": "상품코드 (자재 코드)",
            "chain_ms_no": "체인본사 매장코드",
            "start_qty": "당월 기초 재고 수량",
            "start_cost": "당월 기초 재고 금액",
            "purch_qty": "당월 총 매입 수량",
            "purch_cost": "당일 총 매입 원가 금액",
            "purch_extra_cost": "당월 매입 부대 비용",
            "return_qty": "당월 매입반품 수량",
            "return_cost": "당월 매입반품 금액",
            "sale_qty": "당월 총 매출 수량",
            "sale_cost": "당월 총 매출 원가 금액",
            "sale_extra_cost": "당월 매출 부대 비용",
            "in_qty": "당월 기타입고 수량",
            "in_cost": "당월 기타입고 금액",
            "out_qty": "당월 기타출고 수량",
            "out_cost": "당월 기타출고 금액",
            "disuse_qty": "당월 재고폐기 수량",
            "disuse_cost": "당월 재고폐기 금액",
            "adjust_qty": "당월 재고조정 수량",
            "adjust_cost": "당월 재고조정 금액",
            "tin_qty": "당월 이동(이전)입고 수량 (레시피/세트 변동분 포함)",
            "tin_cost": "당월 이동(이전)입고 금액",
            "tout_qty": "당월 이동(이전)출고 수량",
            "tout_cost": "당월 이동(이전)출고 금액",
            "end_qty": "당월 기말 재고 수량 (실재고 반영분)",
            "end_cost": "당월 기말 재고 원가 금액 (평가액)",
            "returndis_qty": "반품 폐기 수량",
            "returndis_cost": "반품 폐기 금액",
            "move_in_qty": "당월 점포간 이동입고 수량",
            "move_in_cost": "당월 점포간 이동입고 금액",
            "move_out_qty": "당월 점포간 이동출고 수량",
            "move_out_cost": "당월 점포간 이동출고 금액",
            "wholesale_qty": "도매 수량",
            "wholesale_cost": "도매 금액",
            "wholesale_rt_qty": "도매 반품 수량",
            "wholesale_rt_cost": "도매 반품 금액",
            "start_cost_totavg": "총평균 기초 금액",
            "end_cost_totavg": "총평균 기말 금액",
            "purch_gab_extra_cost": "매입 부대비용 정산 차액"
        },
        "memo_c": "매월 말 재고 마감 배치 또는 강제 이월 프로시저 실행 시 신규 년월 데이터가 자동 생성됩니다.",
        "memo_u": "재고실사 보정 및 평가 단가 재계산 배치 연동 시 집계 컬럼이 실시간 업데이트됩니다.",
        "memo_d": "회계 및 재무 보고용 마감 대장이므로 원천 삭제는 불가능합니다.",
        "memo_r": "가맹점 및 본사 월수불 대장, 월말 재고 리포트, 재고자산 대장 등 월간 통계 대화면에서 연동 조회됩니다.",
        "related_tables": [
            {
                "table_name": "imddiotb",
                "description": "일일 상품 수불 집계 테이블. [조인 키: IMMMIOTB.MS_NO = IMDDIOTB.MS_NO AND IMMMIOTB.GOODS_CD = IMDDIOTB.GOODS_CD] 월 수불 대장은 일별로 발생하여 적재된 일수불 데이터(IMDDIOTB)의 매입, 매출, 폐기, 조정 등의 월간 총합 수량을 롤업 집계(Roll-up)하여 당월 실적을 적재하는 부모-자식 관계입니다."
            },
            {
                "table_name": "imcriotb",
                "description": "현재고 정보 테이블. [조인 키: IMMMIOTB.MS_NO = IMCRIOTB.MS_NO AND IMMMIOTB.GOODS_CD = IMCRIOTB.GOODS_CD] 매 영업 마감 또는 월간 최종 재고조사 보정을 거쳐 확정된 IMMMIOTB 월말 기말 재고액과 실시간 수치인 현재고(IMCRIOTB.CUR_QTY)의 단수 차이를 대조 검증하고 원가 보정을 연계 처리합니다."
            },
            {
                "table_name": "imtrlgtb",
                "description": "재고 수불 이력 테이블. [조인 키: IMMMIOTB.MS_NO = IMTRLGTB.MS_NO AND IMMMIOTB.GOODS_CD = IMTRLGTB.GOODS_CD] 월 마감 마감 조정 프로시저(SUB_STOCK_FIFO_MAIN_P 및 SUB_STOCK_FIFO_AFTER_PROC_P) 가동 시 선입선출(FIFO) 또는 총평균 단가를 계산하기 위해 월중 발생한 개별 입출고 수량 거래 로그(IMTRLGTB) 데이터를 추출하여 단가를 업데이트하는 근거가 됩니다."
            },
            {
                "table_name": "imremstb",
                "description": "재고실사 마스터 테이블. [조인 키: IMMMIOTB.MS_NO = IMREMSTB.MS_NO] 매월 실사 마감 확정 처리 시, 실사 데이터와 연동하여 당월 수불을 가마감 처리하고 IMMMIOTB에 월말 최종 기말수량(END_QTY) 및 기말원가(END_COST)를 적재하는 상위 비즈니스 흐름 관계입니다."
            },
            {
                "table_name": "imrealtb",
                "description": "재고실사 확정 상세 테이블. [조인 키: IMMMIOTB.MS_NO = IMREALTB.MS_NO AND IMMMIOTB.GOODS_CD = IMREALTB.GOODS_CD] 월말 실사 조정을 거쳐 확정된 품목별 실사 실재고 데이터를 읽어와 월 수불 테이블의 기말재고 수량과 비교하고, 발생한 재고 조정 수량을 수불 대장에 최종 반영하기 위해 사용됩니다."
            },
            {
                "table_name": "stckiotb",
                "description": "재고 조정/이동 상세 테이블. [조인 키: IMMMIOTB.MS_NO = STCKIOTB.MS_NO AND IMMMIOTB.GOODS_CD = STCKIOTB.GOODS_CD] 월중 발생한 각종 재고 실사 차이 조정이나 강제 재고 조정 내역이 월간 합산되어 월수불 테이블의 조정 수량/금액(adjust_qty, adjust_cost) 필드에 반영되는 데이터 원천입니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "무발주 입고 상세 테이블. [조인 키: IMMMIOTB.MS_NO = OBSLPDTB.MS_NO AND IMMMIOTB.GOODS_CD = OBSLPDTB.GOODS_CD] 월간 가맹점 무발주 입고 실적을 합산 집계하여 월 수불 대장의 당월 매입 수량(purch_qty)과 매입 원가 금액(purch_cost)을 집계 형성하는 데이터 공급처입니다."
            },
            {
                "table_name": "mgmvdttb",
                "description": "점포 간 재고 이동 상세 테이블. [조인 키: IMMMIOTB.GOODS_CD = MGMVDTTB.GOODS_CD] 한 달 동안 타 점포로 출고되었거나 타 점포에서 입고된 이동 실적을 집계하여 월수불의 점포간 이동입고(move_in_qty) 및 이동출고(move_out_qty)를 구성하는 데이터 원천입니다."
            },
            {
                "table_name": "imdusetb",
                "description": "매장 재고 폐기 테이블. [조인 키: IMMMIOTB.MS_NO = IMDUSETB.MS_NO AND IMMMIOTB.GOODS_CD = IMDUSETB.GOODS_CD] 월간 점포에서 폐기 처리된 자재들의 손실 합계 수량 및 폐기 금액을 월수불 테이블의 폐기 수량/금액(disuse_qty, disuse_cost) 필드에 합산 반영하는 소스 테이블입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [조인 키: IMMMIOTB.GOODS_CD = TGOODSTB.GOODS_CD] 월수불 대장 및 조회 리포트 화면에서 각 상품코드에 매칭되는 본사 기준 상품명, 규격, 패키지 분류 구조를 결합 표출하기 위해 N:1 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. [조인 키: IMMMIOTB.MS_NO = MGOODSTB.MS_NO AND IMMMIOTB.GOODS_CD = MGOODSTB.GOODS_CD] 가맹점별로 상이하게 관리되는 세트상품/레시피 구성 속성 및 가맹점 로컬 사용 상태를 참조하여 매장 환경에 맞는 수불 현황을 필터링하기 위해 사용됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [조인 키: IMMMIOTB.MS_NO = MMEMBSTB.MS_NO] 월간 가맹점별 수불 현황 및 재고자산 현황 분석 리포트 화면에서 점포 정보(매장명, 매장 구분코드 등)를 조회하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmembvtb",
                "description": "가맹점 상세 마스터/부가정보 테이블. [조인 키: IMMMIOTB.MS_NO = MMEMBVTB.MS_NO] 월간 재고 마감 시 가맹점의 세부 과세 정보, 공급가 등급 정책을 읽어와 총평균/선입선출 회계 단가를 정밀 계산할 때 연동 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 월 수불 조회 화면 상에서 상품의 입수 단위 명칭(박스, 낱개 등) 및 마감 형태 구분명을 디코딩하여 표준 텍스트로 출력하기 위해 N:1 조인됩니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. [조인 키: IMMMIOTB.GOODS_CD = TPRICETB.GOODS_CD] 월말 기말 평가 단가를 선입선출법 등으로 갱신할 때 기준 거래 단가 내역을 역추적하기 위한 보조 데이터로 연동됩니다."
            },
            {
                "table_name": "mpricetb",
                "description": "매장별 상품 단가 마스터 테이블. [조인 키: IMMMIOTB.GOODS_CD = MPRICETB.GOODS_CD AND IMMMIOTB.MS_NO = MPRICETB.MS_NO] 매장별 가격 등급 및 전용 할인가를 적용하여 기말 월말 재고자산 가치 금액을 정밀 계산할 때 연동 조인됩니다."
            }
        ]
    }

    # 11. IMRETPTB MEMO AND RELATED TABLES
    imretptb_memo = (
        "### 1. 테이블 개요\n"
        "재고실사 임시 등록 테이블 (`IMRETPTB`).\n"
        "매장 실사 등록 화면에서 입력한 실사 정보 및 단품별 실재고 조사 수량을 정식 실사 데이터로 승인/확정하기 전에 임시로 적재하여 보관 및 편집하는 상세 버퍼용 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 실사 프로세스 흐름\n"
        "* **실사 임시 대조군 생성**: 가맹점이나 본부 관리자가 실사등록을 신규 생성(`fnCreateTempRealGoods`)하면, 시스템은 대상 품목들의 실시간 전산상 현재고(`IMCRIOTB.CUR_QTY`)를 추출하여 `IMRETPTB`의 현재고(`CUR_QTY`) 필드에 초기값으로 채워 넣습니다.\n"
        "* **실사 수량 편집 및 업로드**: 사용자가 웹 화면에서 직접 실사 수량을 수정 저장하거나 엑셀 업로드 모달을 통해 대량 업로드할 때 이 테이블의 실사수량(`SURVEY_QTY`) 값이 가감 업데이트됩니다.\n"
        "* **실재고 확정 이관**: 최종 검토 후 실사 전표를 '확정'(`proc_fg = '1'`) 처리하면, 임시 적재되었던 레코드들이 정식 실사 확정 테이블(`IMREALTB`)로 복사 이관되며, 원본 임시 테이블(`IMRETPTB`)의 임시 전표 내역은 후속 배치에 의해 정리 또는 갱신됩니다."
    )

    data["tables"]["imretptb"] = {
        "memo": imretptb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "survey_date": "실사 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "create_fg": "등록 구분 (WT: 웹 직접실사, HP: 핸디터미널 부분실사, HT: 핸디터미널 전체실사)",
            "survey_seq": "실사 일련번호 (Survey 일자별 유니크 키)",
            "line_no": "순번 라인 번호 (4자리)",
            "chain_ms_no": "체인본사 매장코드",
            "source_cd": "소스 코드 (핸디터미널 수신 파일명 등 연계 키)",
            "goods_cd": "상품코드 (실사 대상 단품)",
            "ucost": "단가 (조사 시점 기준 원가 또는 공급단가)",
            "cur_qty": "실사 등록 생성 시점의 시스템 현재고 수량",
            "survey_qty": "사용자가 직접 실사한 실제 창고고 수량",
            "proc_fg": "처리 상태 구분 (0: 임시등록, 1: 확정완료, 2: 마감처리)",
            "create_dtime": "최초 등록 일시",
            "create_id": "최초 등록 작업자 ID",
            "last_dtime": "최종 수정 일시",
            "last_id": "최종 수정 작업자 ID"
        },
        "memo_c": "매장 실사 등록 생성 또는 엑셀 실사 업로드 처리 시 해당 실사번호의 라인별로 인서트됩니다.",
        "memo_u": "웹 화면에서 실사 수량을 수동 수정하고 저장할 때 해당 라인의 실사수량(SURVEY_QTY)이 갱신됩니다.",
        "memo_d": "실사 전표 취소 시 해당 전표에 딸린 임시 라인 정보가 일괄 딜리트됩니다.",
        "memo_r": "실사 등록 화면 조회 시 임시 저장된 실사 수치와 차이 수량(실사수량 - 현재고수량)을 렌더링하기 위해 수시로 조회됩니다.",
        "related_tables": [
            {
                "table_name": "imremstb",
                "description": "재고실사 마스터 테이블. [조인 키: IMRETPTB.MS_NO = IMREMSTB.MS_NO AND IMRETPTB.SURVEY_SEQ = IMREMSTB.SURVEY_SEQ] 실사 번호별 매장 실사 기본 설정 및 마감 여부(CLOSE_YN), 승인 진행 상태를 관리하며, 마스터 생성 및 확정 단계에 맞춰 임시 상세(IMRETPTB)의 등록/수정/삭제 라이프사이클을 통제합니다."
            },
            {
                "table_name": "imrealtb",
                "description": "재고실사 확정 상세 테이블. [조인 키: IMRETPTB.MS_NO = IMREALTB.MS_NO AND IMRETPTB.SURVEY_SEQ = IMREALTB.SURVEY_SEQ AND IMRETPTB.LINE_NO = IMREALTB.LINE_NO] 실사 입력이 최종 승인/확정되면, 임시 테이블(IMRETPTB)에 보관되던 가집계 정보가 확정 테이블(IMREALTB)로 마이그레이션(이관 적재)되어 정식 수불 마감용 실사 실재고 데이터로 변환됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "현재고 정보 테이블. [조인 키: IMRETPTB.MS_NO = IMCRIOTB.MS_NO AND IMRETPTB.GOODS_CD = IMCRIOTB.GOODS_CD] 실사 등록을 생성(fnCreateTempRealGoods)하는 시점에 시스템상에 기록된 실시간 현재고 수량(CUR_QTY)을 읽어와 IMRETPTB.CUR_QTY 필드에 기초 시스템 재고값으로 저장하고 대조하는 데 사용됩니다."
            },
            {
                "table_name": "imtrlgtb",
                "description": "재고 수불 이력 테이블. 실사 임시 등록 후 최종 마감 확정 시, 실사 수량 차이에 따른 수량 조정 이력을 수불 로그(IMTRLGTB)의 조정 코드(A)로 인서트하여 현재고를 업데이트하는 데 기반이 됩니다."
            },
            {
                "table_name": "imddiotb",
                "description": "일일 상품 수불 집계 테이블. 실사 확정 이후 발생한 실사 보정 조정 실적이 당일 마감 배치를 통해 일수불의 조정 수량(adjust_qty) 및 금액(adjust_cost) 필드에 가감 반영되는 연동 대상입니다."
            },
            {
                "table_name": "immmiotb",
                "description": "월별 상품 수불 집계 테이블. 월말 실재고 확정 및 평가액 산정 시, 임시 실사 데이터에서 확정된 최종 수량을 월 수불 대장의 기말 수량(end_qty)으로 반영하여 당월 재고 금액 평가를 매듭짓는 기준 정보가 됩니다."
            },
            {
                "table_name": "imclbktb",
                "description": "수불 마감 백업 테이블. 월 마감 및 실재고 교정 시, 임시 실사 등록 정보와 이전 수불 데이터를 이중 백업하여 수불 롤백 및 데이터 복구 정합성을 기하는 안전 장치용 백업 테이블입니다."
            },
            {
                "table_name": "immmcltb",
                "description": "월 수불 마감 정보 테이블. 점포별 월별 수불 마감 상태를 통제하며, 임시 실사 등록이 미확정 상태로 남아 있는 경우 해당 월의 수불 마감(IMMMCLTB) 진행을 제어하는 관계입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [조인 키: IMRETPTB.GOODS_CD = TGOODSTB.GOODS_CD] 실사 등록 화면에서 품목을 검색 및 추가할 때 본부 표준 상품의 분류, 한글 명칭, 규격 및 사용유무 속성을 N:1 매치하여 가져옵니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. [조인 키: IMRETPTB.MS_NO = MGOODSTB.MS_NO AND IMRETPTB.GOODS_CD = MGOODSTB.GOODS_CD] 각 가맹점에 해당하는 개별 점포용 취급 상품 마스터를 참조하여 매장 단위의 실사 대상 품목을 구성하고 취급 단가 정보를 대조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [조인 키: IMRETPTB.MS_NO = MMEMBSTB.MS_NO] 실사 전표를 생성한 점포의 매장 한글명, 소속 본사 체인 식별코드(CHAIN_NO)를 매칭하여 보안 및 프랜차이즈 권한을 통제하는 조인 관계입니다."
            },
            {
                "table_name": "mmembvtb",
                "description": "가맹점 상세 마스터/부가정보 테이블. [조인 키: IMRETPTB.MS_NO = MMEMBVTB.MS_NO] 매장의 단가 정산 구분값(USUPRICE_FG 등)을 대조하여 실사 전표상에서 원가 계산 시 낱개/묶음 기준 단가 적용을 규정하는 보조 정보입니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 실사 등록 구분(WT, HP, HT 등)에 대한 표준 한글 명칭(웹 실사, 핸디 실사 등) 및 단위 구분 코드를 디코딩하여 화면에 매치 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. [조인 키: IMRETPTB.GOODS_CD = TPRICETB.GOODS_CD] 실사 등록 당시의 실사 유효 공급 단가를 매치하여 실사 차이로 인한 조정 금액을 산정하는 데 활용됩니다."
            }
        ]
    }

    # 12. IMTRBKTB MEMO AND RELATED TABLES
    imtrbktb_memo = (
        "### 1. 테이블 개요\n"
        "수불 트랜잭션 백업 로그 테이블 (`IMTRBKTB`).\n"
        "매출 수불 배치(`DmIMTR01`) 실행 시 미처리 재고 수불 로그(`IMTRLGTB`) 데이터를 읽어 현재고 및 일수불/월수불에 반영한 직후, 사후 선입선출(FIFO) 회계 단가 정산 및 수불 내역 백업/이력 보존을 위해 트랜잭션 단위로 1:1로 백업 저장하는 아카이브용 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 수불 마감/배치 흐름\n"
        "* **수불 트랜잭션 아카이빙**: 일일 점포 매출 또는 물류 거래 발생 시 적재된 `IMTRLGTB` 레코드를 매출 수불 배치 가동 시 읽어와 처리(PROC_YN = 'Y')함과 동시에 `IMTRBKTB` 테이블에 안전하게 복사 인서트(`insertIMTRBKTB`)합니다.\n"
        "* **선입선출(FIFO) 단가 정산 연계**: 월간 원가 계산 배치(`Sp_SUB_STOCK_FIFO_PROC_P`) 가동 시, 아직 마감 처리되지 않은 백업 로그(`IMTRBKTB.STOCK_YN = 'N'`)를 한 건씩 돌며 해당 품목의 매입단가, 매출원가 정산을 계산하여 선입선출 대장(`STCKHITB`)에 최종 갱신하고 `STOCK_YN = 'Y'`로 상태를 변경합니다.\n"
        "* **마감 롤백 및 재오픈 지원**: 마감월 재오픈이나 원가 재계산 배치(`Sp_SUB_STOCK_FIFO_MAIN_P`) 가동 시, 해당 월에 갱신되었던 `IMTRBKTB`의 마감 처리 플래그를 원상 복구(`STOCK_YN = 'Y' -> 'N'`)하여 선입선출 배치가 처음부터 재생성 및 재계산될 수 있도록 대기 처리합니다."
    )

    data["tables"]["imtrbktb"] = {
        "memo": imtrbktb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "rowid": "시스템 고유 로우 식별 시퀀스 키 (EDB Sequence)",
            "trbk_dtime": "수불 백업 로그 생성 일시 (YYYYMMDDHH24MISS)",
            "ms_no": "매장코드 (점포 코드)",
            "proc_fg": "수불 구분 코드 (P: 매입, S: 매출, R: 반품, A: 조정, F: 이동입고, T: 이동출고 등)",
            "trbk_seq": "로그 일련번호 (TRLG_SEQ 동일 매핑)",
            "proc_date": "실제 거래(수불) 처리 일자 (YYYYMMDD)",
            "chain_ms_no": "체인본사 매장코드",
            "goods_cd": "상품코드 (자재 코드)",
            "trbk_qty": "수불 수량 (입고 시 +, 출고 시 -)",
            "trbk_cost": "수불 금액 (원가 또는 매가 기준)",
            "proc_yn": "배치 연동 처리 상태 구분 (Y: 백업 완료)",
            "key_bill_no": "원천 거래 전표 번호 (매출번호, 입고번호, 조정번호 등)",
            "stock_yn": "선입선출 마감 평가 여부 플래그 (N: 대기, Y: 평가완료, S: 스킵)",
            "stock_dtime": "선입선출 마감 계산 처리 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "매출 수불 배치(DmIMTR01)에서 수불 이력(IMTRLGTB) 처리와 동시에 복사 인서트됩니다.",
        "memo_u": "선입선출 원가 배치(Sp_SUB_STOCK_FIFO_PROC_P) 실행 완료 시 마감플래그(STOCK_YN)가 'Y'로 갱신됩니다.",
        "memo_d": "원천 기록 보존용 회계 백업 로그이므로 시스템 내 딜리트가 제한됩니다.",
        "memo_r": "원가 계산 배치 및 마감 취소 배치(Sp_SUB_STOCK_FIFO_MAIN_P) 실행 시 STOCK_YN 플래그 갱신 및 롤백 처리를 위해 조회됩니다.",
        "related_tables": [
            {
                "table_name": "imtrlgtb",
                "description": "재고 수불 이력 테이블. 매출 수불 배치(DmIMTR01)가 미처리 수불 로그(IMTRLGTB)를 읽어와 현재고에 반영하는 즉시, 사후 원가 추적 및 이력 보존을 위해 IMTRBKTB에 1:1로 백업 복사합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고이력/재고평가 대장 테이블. FIFO 재고 평가 배치 실행 시, IMTRBKTB에 적재된 매입(P), 매출(S), 반품(R), 조정(A) 백업 로그를 바탕으로 개별 입고건별 잔여수량(END_QTY) 및 평가 단가를 실시간으로 계산하여 STCKHITB에 차감/합산 반영합니다."
            },
            {
                "table_name": "stcklgtb",
                "description": "수불 처리 상세 로그 테이블. IMTRBKTB에 보관된 거래 백업을 선입선출법으로 매칭 처리하면서 각 거래 내역이 어떤 입고 전표와 상계되었는지 상세 회계 정합성 추적 로그(STCKLGTB)를 기록 저장합니다."
            },
            {
                "table_name": "imcriotb",
                "description": "현재고 정보 테이블. 매출 수불 배치가 트랜잭션 백업 생성 시점에 매장의 실재고 수량과 원가를 실시간 증감 업데이트하여 동기화합니다."
            },
            {
                "table_name": "imddiotb",
                "description": "일일 상품 수불 집계 테이블. 수불 백업 로그가 생성되는 당일의 일수불 대장상 각 유형별(매입, 매출, 조정 등) 합계 수량 및 금액을 갱신하는 배치 연동 관계입니다."
            },
            {
                "table_name": "immmiotb",
                "description": "월별 상품 수불 집계 테이블. 월 마감 및 재계산 시, 월간 수불 백업 로그를 역조회하여 월 수불 대장의 당월 기초/기말 평가 원가 계산을 업데이트합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "무발주 입고 상세 테이블. 백업 로그의 원천 전표(KEY_BILL_NO)가 무발주 입고인 경우, 매입 부대비용(extra_cost)을 읽어와 선입선출 원가에 포함시키기 위해 조인합니다."
            },
            {
                "table_name": "stckmotb",
                "description": "재고 조정/이동 상세 테이블. 백업 로그에 담긴 거래 중 매장이동(F/T), 강제조정(A)의 원천이 되는 상세 조정 수량 및 배합 세트 구성 정보를 참조하여 분할 처리하기 위해 조인됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 취소 전표(C) 처리 시, 매출 취소에 따른 선입선출 원가 롤백(반품 처리)을 진행하기 위해 원천 매출 정보(STRNHDTB)를 확인하는 데 사용됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 백업 로그의 품목이 속한 본사 표준 브랜드 및 대/중/소 분류 정보를 매칭하여 통계 데이터를 추출할 때 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 가맹점 단위의 로컬 상품 취급 구분 및 사용 여부를 참조하여 수불 갱신 대상 여부를 판정합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점 체인 전체의 수불 및 원가 계산 배치를 일괄 실행할 때 대상 가맹점 목록을 드라이브하기 위해 조인됩니다."
            },
            {
                "table_name": "imremstb",
                "description": "재고실사 마스터 테이블. 해당 마감월의 마감 상태(CLOSE_YN)를 확인하여, 이미 마감 완료된 매장에 대해서는 백업 로그 갱신을 차단하거나 에러를 예방하기 위해 조인됩니다."
            }
        ]
    }

    # 13. MACCIOTB MEMO AND RELATED TABLES
    macciotb_memo = (
        "### 1. 테이블 개요\n"
        "계정별 입출금 내역 테이블 (`MACCIOTB`).\n"
        "매장별(`MS_NO`), 일자별(`ACCIO_DATE`)로 발생하는 수시 입금 및 출금 거래 내역(계정코드, 금액, 거래처, 적요 등)을 상세 기록하여 매장의 일일 지출 현황 및 수지 분석을 가능하게 하는 현금 입출금 관리 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 입출금 관리 흐름\n"
        "* **수시 입출금 직접 등록**: 매장 점주나 사용자가 백오피스 웹 화면(`st_cash_00001`/`00004`)에서 현금 지출 내역(식비, 잡비, 물품대금 등)을 수동으로 입력 및 저장할 때 인서트 처리됩니다.\n"
        "* **POS 시재 및 입출금 연동**: POS 단말기에서 영업 중 또는 마감 시 입력된 수시 입출금 데이터가 POS 배치(`DmSALT10`) 서비스를 거쳐 백오피스 DB인 `MACCIOTB`에 정기적으로 전송 및 연동됩니다.\n"
        "* **일일 마감 및 과부족 정산**: 매 영업 마감 정산(`MCLSCHTB`) 시, POS 매출액과 더불어 당일 발생한 입출금 금액(`ACNT_AMT`) 총합을 비교 분석하여 매장 시재의 과부족액을 정산 연계 산출합니다."
    )

    data["tables"]["macciotb"] = {
        "memo": macciotb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "accio_date": "입출금 발생 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "accio_no": "입출금 순번 일련번호 (Pos번호 2자리 + 일련번호 2자리)",
            "chain_no": "체인 본부 식별번호",
            "acnt_fg": "계정 구분 플래그 (0: 입금, 1: 출금)",
            "acnt_cd": "계정코드 (계정과목 코드)",
            "acnt_amt": "입출금 공급가액 금액 (부가세 제외)",
            "vat": "입출금 부가세 금액",
            "cust_cd": "거래처 코드 (MVENDRTB 또는 CUST_CD 매핑)",
            "remark": "상세 적요 내용",
            "delete_yn": "삭제 여부 플래그 (Y: 삭제완료, N: 미삭제)",
            "create_fg": "등록 구분 플래그 (0: 백오피스 Web 직접등록, 1: POS 단말기 수집등록)",
            "user_id": "등록/처리한 로그인 사용자 ID",
            "create_dtime": "최초 등록 일시",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 수정 일시",
            "last_id": "최종 수정자 ID"
        },
        "memo_c": "웹 입출금 내역 등록 화면에서 내역 추가 또는 POS 영업 마감 연동 배치 시 인서트됩니다.",
        "memo_u": "웹 화면에서 기존 등록된 입출금의 금액, 적요, 거래처를 변경하고 저장할 때 업데이트됩니다.",
        "memo_d": "내역 삭제 시 실제 레코드를 딜리트하지 않고 delete_yn = 'Y'로 수정하여 논리 삭제 처리합니다.",
        "memo_r": "매장별/계정별 입출금 현황 리포트 및 지출 내역조회 화면에서 월간 통계를 렌더링하기 위해 수시로 조회됩니다.",
        "related_tables": [
            {
                "table_name": "mmacnttb",
                "description": "가맹점 입출금 계정 과목 마스터 테이블. [조인 키: MACCIOTB.ACNT_CD = MMACNTTB.ACNT_CD] 가맹점/매장에서 사용하는 표준 입출금 계정 코드명(식비, 잡비, 거스름돈 등)을 조인하여 입출금 거래 내역에 한글 계정명을 매칭하는 1:1 필수 연계 테이블입니다."
            },
            {
                "table_name": "tmacnttb",
                "description": "본사 표준 입출금 계정 과목 테이블. [조인 키: MACCIOTB.ACNT_CD = TMACNTTB.ACNT_CD] 본부 표준 지출 및 입출금 계정 분류 코드를 바탕으로 가맹점들의 수집된 입출금 거래 금액을 전사 통합 집계 리포트 화면(hq_cash_00005 등)에서 대조할 때 연동 조인됩니다."
            },
            {
                "table_name": "mmacnctb",
                "description": "매장 계정 연결 설정 테이블. [조인 키: MACCIOTB.ACNT_CD = MMACNCTB.ACNT_CD AND MACCIOTB.MS_NO = MMACNCTB.MS_NO] 각 매장별로 입출금 계정 코드 사용 여부 및 특정 POS 계정 단추와의 연결 설정을 대조하여 매장 단말기 및 웹 화면에 노출될 계정 권한을 통제합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [조인 키: MACCIOTB.MS_NO = MMEMBSTB.MS_NO] 전점 계정별 현황이나 매장별 지출현황 화면에서 매장명(점포명), 소속 체인본부, 점주 정보 및 매장 사용 상태를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. [조인 키: MACCIOTB.CREATE_ID = MUSERSTB.USER_ID] 매장 웹 화면에서 수동으로 입출금 내역을 추가/수정한 작업자(CREATE_ID, LAST_ID)의 실명과 권한 등급을 추적 및 로깅하는 데 사용됩니다."
            },
            {
                "table_name": "mclschtb",
                "description": "매장 일일 정산 마감 마스터 테이블. [조인 키: MACCIOTB.MS_NO = MCLSCHTB.MS_NO AND MACCIOTB.ACCIO_DATE = MCLSCHTB.CLOSE_DATE] 일일 시재 정산 마감 시 POS에서 수집되거나 웹에서 수동 등록된 수시 입출금 금액(acnt_amt)을 최종 정산 결과(기타입금액, 기타출금액)에 산입하여 매장 시재 정합성(과부족)을 계산할 때 참조됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 매장 마감 시 당일 총 POS 카드/현금 매출 금액과 시재 입출금 내역을 대조하여 매장의 일별 현금 시재 총합계를 정밀 검증할 때 연관 분석용 데이터로 사용됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 수시 지출액 결제와 연계된 영업일자별 단품 매출 및 매장 일자별 현금 매가 회수 대장을 확인하기 위한 간접 분석 테이블입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 거래처 입출금 및 부자재 소모 관련 지출 내역을 기록할 때, 대상 거래 자재/상품의 한글 정보 등을 참고 조회하는 데 간접 연계될 수 있습니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. 거래처 지출 결제금액 산출 및 자재 매입 정산 금액(출금)의 타당성을 평가하기 위해 매입 지출건과 단가 데이터를 비교 분석할 때 연동됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 입출금 등록 구분코드(Web등록, POS등록 등) 및 삭제 여부 등의 라벨을 한글(Web등록, POS동기화 등)로 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "mvendrtb",
                "description": "거래처(매입처) 마스터 테이블. [조인 키: MACCIOTB.CUST_CD = MVENDRTB.VENDR_CD] 거래처 물품 대금 지급이나 특정 거래처로의 출금(결제) 거래 내역 등록 시 수납 대상 거래처명과 정산 사업자번호를 연동 표시하기 위해 조인됩니다."
            },
            {
                "table_name": "tmacnctb",
                "description": "본사 계정 연결 설정 테이블. [조인 키: MACCIOTB.ACNT_CD = TMACNCTB.ACNT_CD] 체인 전체 표준 계정 과목 중 본사 전용으로 통제할 지출 항목들을 본부 지출 현황 리포트 화면(hq_cash_00005)에 필터링하여 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "wfnenvtb",
                "description": "웹 환경 설정 테이블. 매장별 수시 입출금 등록 시 부가세(VAT) 자동 계산 비율이나 한도 금액 설정 정책을 웹에서 동적으로 가져오기 위해 참조됩니다."
            }
        ]
    }

    # 14. MBANKMTB MEMO AND RELATED TABLES
    mbankmtb_memo = (
        "### 1. 테이블 개요\n"
        "은행 코드 마스터 테이블 (`MBANKMTB`).\n"
        "국내 시중 은행 및 금융기관의 표준 은행 코드(`BANK_CD`), 은행명(`BANK_NM`), 연락처 정보 등을 등록하여 관리하는 기준정보 코드 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 계좌 관리 흐름\n"
        "* **정산 은행 및 송금 계좌 지정**: 가맹점 마스터(`MMEMBSTB`) 또는 거래처/협력사 마스터(`MVENDRTB`) 상의 대금 송금용 정산 계좌 정보를 신규 등록하거나 수정할 때 유효한 은행 코드를 조인 및 검증(FK 대조)하는 근거가 됩니다.\n"
        "* **매입금 지출 및 정산 이체**: 본사/매장에서 거래처에 물품 대금을 정산 이체하거나 가맹점 수수료 지급 시 해당 계좌의 수납 은행 한글명을 화면에 출력하고 이체 파일을 생성하는 용도로 조인됩니다."
    )

    data["tables"]["mbankmtb"] = {
        "memo": mbankmtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "bank_cd": "은행 코드 (시중 은행 식별용 3자리 문자열)",
            "bank_nm": "은행 한글 명칭",
            "tel_no": "해당 은행 대표 전화번호",
            "fax_no": "은행 대표 팩스 번호",
            "homepage": "은행 홈페이지 공식 URL"
        },
        "memo_c": "본사 기준 정보 관리자 또는 DB DDL을 통해 국내 표준 금융기관 코드가 사전 등록됩니다.",
        "memo_u": "은행의 명칭 변경, 연락처 수정이 발생할 경우 백오피스 기준정보 관리 프로세스에 의해 갱신됩니다.",
        "memo_d": "해당 은행 코드를 정산 계좌로 참조하는 매장이나 공급업체가 존재하지 않을 경우에 한해 삭제할 수 있습니다.",
        "memo_r": "가맹점 상세 조회, 거래처 등록 모달, 협력업체 정산 화면에서 계좌 은행명을 한글로 표출하기 위해 실시간 조회됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [조인 키: MMEMBSTB.BANK_CD = MBANKMTB.BANK_CD] 각 점포(가맹점)의 가맹비 환불, 수수료 정산 및 송금 계좌 정보에 등록된 은행 코드를 조인하여 은행 한글명을 출력하는 데 사용됩니다."
            },
            {
                "table_name": "mvendrtb",
                "description": "거래처(매입처) 마스터 테이블. [조인 키: MVENDRTB.BANK_CD = MBANKMTB.BANK_CD] 협력 물품 공급업체들의 매입 대금 자동 송금 및 정산 계좌 정보에 등록된 입금 은행을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "백오피스 사용자 마스터 테이블. 가맹점 또는 공급업체 계좌 정보와 결제용 은행 코드 마스터를 신규 등록/수정한 관리자 계정을 추적하는 데 사용됩니다."
            },
            {
                "table_name": "mmembvtb",
                "description": "가맹점 상세 마스터/부가정보 테이블. 정산 계좌의 소유주와 지급 일자 등 가맹점 은행 정산 세부 규칙을 대조 설정할 때 연동됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 금융 거래 구분코드 및 은행 관련 코드(일반 은행, 특수 금융기관 등)의 공통 라벨을 디코딩하기 위해 조인됩니다."
            },
            {
                "table_name": "macciotb",
                "description": "계정별 입출금 내역 테이블. 특정 은행을 통해 수납 또는 송금 지출이 처리되었을 때, 지출 내역 전표의 이체 은행 코드명을 확인하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 특정 거래처(은행 계좌 연동 공급사)에서 공급하는 상품의 원가를 정산할 때, 공급사 계좌의 이체 은행 한글 정보와 상품 매입 대장 정보를 대조 분석하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. 공급업체별 단가 및 수수료 정산 시, 결제용 등록 은행의 계좌 정보와 정산 단가 대장을 매칭하기 위해 간접 연관 조회됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "무발주 입고 상세 테이블. 가맹점에서 무발주로 매입한 거래처의 정산 및 계좌 송금 대상 은행을 대조 조회할 때 연계됩니다."
            },
            {
                "table_name": "imremstb",
                "description": "재고실사 마스터 테이블. 월간 마감 이후 공급사별 실재고 매입 대금 정산액을 은행 계좌로 송금하기 위한 회계 자료 검증 시 간접 매칭용으로 연동될 수 있습니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 매장별 전용 공급업체(거래처)의 정산용 은행 정보와 취급 자재 품목 데이터를 매치하는 용도로 간접 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "환경설정 공통코드 테이블. POS 및 백오피스 환경설정 공통코드 테이블. 입출금 및 이체 시 은행 계좌 유효성 검증 규칙이나 이체 방식에 대한 시스템 파라미터를 읽어오기 위해 조인됩니다."
            }
        ]
    }

    # 15. MCARDMTB MEMO AND RELATED TABLES
    mcardmtb_memo = (
        "### 1. 테이블 개요\n"
        "카드사 마스터 테이블 (`MCARDMTB`).\n"
        "국내외 신용카드 발급사 및 매입사들의 카드사 구분코드(`CARD_CO`), 카드사 명칭(`CARD_NM`), 대표 사업자등록번호(`BIZ_NO`) 및 연락처 등을 정의하여 관리하는 기준정보 카드사 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 정산 수수료 흐름\n"
        "* **카드 매출 디코딩 및 한글명 표출**: 점포 POS 단말기에서 승인 수집된 매출 데이터(`STRNCDTB`) 상의 카드사 코드를 조인하여, 매출일보/월보 및 카드 승인현황 화면 상에 한글 카드사명(예: 국민카드, 현대카드 등)을 디코딩 렌더링합니다.\n"
        "* **가맹 수수료 및 VAN사 연동**: 가맹점 마스터(`MMEMBSTB`/`MMEMBVTB`)와 연계하여 점포별 카드 수수료율과 가맹점 번호를 카드사별로 관리하고, VAN 카드사 설정(`MVANSTTB`) 정보를 통해 POS 결제 단말기 통신 승인 매핑을 라우팅 처리합니다.\n"
        "* **영수증 출력 및 청구 정산**: 영수증 상세 출력 모듈(`CommonModule_BillInfo`)에서 매입사/발급사 카드명을 디코딩하고, 카드 승인 정보 청구/입금 단계에서 금융 거래 정합성을 검증하는 근거가 됩니다."
    )

    data["tables"]["mcardmtb"] = {
        "memo": mcardmtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "card_co": "카드사 코드 (신용카드 매입/발급 식별용 3자리 문자열)",
            "card_nm": "카드사 한글 명칭",
            "biz_no": "카드사 사업자등록번호 (10자리)",
            "tel_no": "카드사 대표 고객센터 전화번호",
            "fax_no": "카드사 대표 팩스 번호",
            "homepage": "카드사 공식 홈페이지 URL",
            "create_dtime": "등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "등록자 ID",
            "last_dtime": "최종 수정 일시",
            "last_id": "최종 수정자 ID"
        },
        "memo_c": "본사 기준 정보 관리자 또는 DB DDL 마이그레이션을 통해 표준 카드사 코드가 사전 등록됩니다.",
        "memo_u": "카드사 합병, 대표 정보 변경, 연락처 수정 등이 발생할 경우 백오피스 마스터 등록 프로세스에 의해 업데이트됩니다.",
        "memo_d": "해당 카드사 코드를 결제 수단으로 참조하는 매출 데이터나 매장 계약 정보가 존재하지 않을 경우에 한해 삭제할 수 있습니다.",
        "memo_r": "영업일보/월보 신용카드 집계 탭, 카드 청구 승인내역 조회 화면, POS 영수증 재출력 모듈 등에서 상시 조회됩니다.",
        "related_tables": [
            {
                "table_name": "strncdtb",
                "description": "매출 신용카드 결제 상세 테이블. [조인 키: STRNCDTB.CARD_CO = MCARDMTB.CARD_CO] 매장에서 카드 결제 발생 시 POS로부터 수집된 결제 전표상 카드사 코드와 매칭하여, 매출일보/월보 및 카드 승인현황 화면에서 한글 카드사명(국민카드, 현대카드 등)을 디코딩 표출하기 위해 조인됩니다."
            },
            {
                "table_name": "mvansttb",
                "description": "VAN사 정산 거래처 테이블. [조인 키: MVANSTTB.STD_CARD_CD = MCARDMTB.CARD_CO] 개별 신용카드사와 VAN사 단말기 프로토콜 통신 시 사용하는 카드사별 고유 식별 코드를 표준 카드사 마스터 정보와 매핑하여 라우팅 처리합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포(가맹점)의 개별 카드사 제휴 가맹점 번호와 수수료 정산 및 송금 계좌 정보에 등록된 이체 은행/카드사 설정을 매핑 조회하는 데 사용됩니다."
            },
            {
                "table_name": "mmembvtb",
                "description": "가맹점 상세 마스터/부가정보 테이블. 가맹점별로 개별 카드사들과 체결한 신용카드 가맹점 번호(가맹점번호) 및 우대 수수료율 정책을 세부 매치하여 카드사별 예상 정산 수수료를 차감 산출하기 위해 조인됩니다."
            },
            {
                "table_name": "vanmsttb",
                "description": "VAN사 마스터 테이블. 카드 결제 승인 중계 대행사(NICE, KIS 등)와 카드사 간의 승인 수수료 매핑 데이터를 정의하고 조회할 때 표준 카드사 정보와 연관 참조됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 신용카드 가맹점 수수료 갱신이나 신규 카드사 수수료율 정책을 조율/입력한 관리자의 실명 및 이력을 감사 로깅하기 위해 연계됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 카드사 속성(체크, 신용, 해외카드 등)에 매핑된 명칭 공통 코드값 및 가맹 정산 상태 라벨을 한글로 디코딩하기 위해 조인됩니다."
            },
            {
                "table_name": "macciotb",
                "description": "계정별 입출금 내역 테이블. 카드사별 정산 대금이 매장 은행 계좌로 입금(acnt_fg = '0')되었을 때, 정산 전표상 수납 카드사와 대조하여 매출 매칭 상태를 검증하는 데 연관됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 신용카드사 제휴 할인 프로모션(특정 카드로 결제 시 특정 상품 할인) 등을 본사 행사 등록 화면에서 설정할 때 상품 정보 및 카드사 할인 비율 매치에 연계됩니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. 카드사 제휴 프로모션 적용에 따른 단가 차감액 정산 및 카드 매출 수수료 공제 후 실질 매가 단가 밸류에이션을 대조 분석하기 위해 간접 연동됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 총 매출 및 취소 거래 발생 시 카드 결제 전표의 무효화 상태를 체크하고, 카드사 승인 내역과 매칭 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "환경설정 공통코드 테이블. 카드 영수증 출력 서식(발급사명, 매입사명 표기 규정)이나 카드 단말기 통신 포트 규칙 관련 파라미터 매치에 참조됩니다."
            }
        ]
    }

    # 16. IMREALTB MEMO AND RELATED TABLES
    imrealtb_memo = (
        "### 1. 테이블 개요\n"
        "재고실사 확정 데이터 테이블 (`IMREALTB`).\n"
        "매장별(`MS_NO`), 실사번호별(`IDX`)로 생성된 최종 실사/조정 내역 중 '확정' 완료된 데이터(실사수량, 현재고 스냅샷, 조정수량, 조정금액, 조정사유 등)를 영구 기록하는 최종 실사 수불 내역 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 실사/조정 관리 흐름\n"
        "* **임시저장에서 최종확정으로의 이관**: 사용자가 등록 화면(`st_stock_00001`/`00005`)에서 실사 및 조정을 입력하는 동안에는 임시 테이블(`IMRETPTB`)에 보관되다가, 최종 '확정' 버튼을 클릭하는 순간 무결성 검증을 거친 후 `IMREALTB`로 INSERT 처리되고 임시 테이블은 비워집니다.\n"
        "* **현재고 및 수불 연동**: 실사 확정 처리 직후, 차이 수량(`MODIFY_QTY = SURVEY_QTY - CUR_QTY`) 및 차이 금액만큼 매장 현재고 테이블(`IMCRIOTB.CUR_QTY`)을 즉시 실시간 차감/합산 동기화합니다.\n"
        "* **선입선출 회계 처리 연계**: 월간 원가 정산 배치 가동 시, 확정된 실사/조정 손실량만큼 선입선출 대장(`STCKHITB`)의 남은 입고 잔여량을 순차적으로 차감하여 기말 재고 평가 금액을 최종 확정합니다."
    )

    data["tables"]["imrealtb"] = {
        "memo": imrealtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "idx": "실사번호 (전수/부분 실사 고유 식별 일련번호)",
            "ms_no": "매장코드 (점포 코드)",
            "grp_cd": "상품 대분류 또는 그룹 분류 코드 (00: 대분류 실사)",
            "goods_cd": "상품코드 (자재 코드)",
            "chain_ms_no": "체인 본부 매장코드",
            "cur_qty": "실사 등록 시점의 시스템 현재고 수량 (스냅샷)",
            "cur_cost": "실사 등록 시점의 시스템 현재고 원가 금액 (스냅샷)",
            "survey_qty": "실제 매장에서 카운팅한 실재고 수량",
            "survey_cost": "실제 실사 수량 기준 평가 금액",
            "modify_qty": "조정 수량 (실사수량 - 시스템재고수량)",
            "modify_cost": "조정 금액 (실사금액 - 시스템재고금액)",
            "remark": "상세 조정 및 특이사항 비고",
            "create_dtime": "최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID",
            "re_fg": "실사 구분 코드",
            "proc_fg": "처리 상태 플래그 (1: 확정완료, 2: 월수불 마감반영완료)",
            "create_fg": "등록 주체 코드 (WP: 웹 실사, HP: 핸디 실사 등)",
            "survey_fg": "실사 유형 구분",
            "survey_seq": "실사 일련번호",
            "last_dtime": "최종 수정 일시",
            "last_id": "최종 수정자 ID",
            "reason_cd": "조정 사유 코드 (MNAMEMTB.MAIN_CD = '901' 매핑)",
            "survey_date": "실제 실사를 수행한 기준 일자 (YYYYMMDD)",
            "proc_dtime": "최종 확정 처리 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "임시 실사/조정 테이블(IMRETPTB)에서 사용자가 '최종 확정' 실행 시 한 번에 인서트 이관됩니다.",
        "memo_u": "확정 완료된 실사 내역이므로 금액 및 수량의 임의 업데이트가 전면 차단됩니다.",
        "memo_d": "원천 수불 감사 로그이므로 삭제가 제한되며, 대기 상태에서 삭제 시에는 임시 테이블(IMRETPTB) 단계에서 지워집니다.",
        "memo_r": "조정/실사 현황 조회 화면 및 월간 재고 수불 분석 화면에서 조정 실적 조회를 위해 상시 조회됩니다.",
        "related_tables": [
            {
                "table_name": "imretptb",
                "description": "임시 실사/조정 내역 테이블. 매장이나 본사 웹 화면에서 실사 수량 임시저장(proc_fg = '0') 단계에 머무르다가, 최종 '확정'을 실행하면 검증 후 IMREALTB로 영구 복사 이관됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. [조인 키: IMREALTB.MS_NO = IMCRIOTB.MS_NO AND IMREALTB.GOODS_CD = IMCRIOTB.GOODS_CD] 실사 조정 확정 시 발생한 수량 차이(modify_qty)만큼 현재고 수량(CUR_QTY)을 실시간으로 차감 또는 합산 갱신합니다."
            },
            {
                "table_name": "imremstb",
                "description": "재고실사 마스터 테이블. [조인 키: IMREALTB.IDX = IMREMSTB.IDX] 진행 실사 번호의 대상 년월, 담당자, 마감 상태(CLOSE_YN)를 정의하고 상세 조정 확정 데이터들과 1:N으로 매핑 제어합니다."
            },
            {
                "table_name": "imtrlgtb",
                "description": "재고 수불 이력 테이블. 실사 확정에 의한 수량 변동을 수불 배치 엔진이 현재고에 적용할 때, 상세 조정 원천 전표(KEY_BILL_NO)로서 참조 연동 로그를 생성합니다."
            },
            {
                "table_name": "imtrbktb",
                "description": "수불 트랜잭션 백업 로그 테이블. 실사 확정에 의한 재고 증감 조정 트랜잭션을 선입선출(FIFO) 회계 원가 배치가 수행되기 직전 아카이브 로그에 안전하게 이관 보존하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고이력/재고평가 대장 테이블. 실사 조정을 통해 재고 감모(손실)가 발생했을 때, FIFO 규칙에 의거하여 기존에 입고되었던 잔여수량(END_QTY)을 차례대로 깎거나, 반대로 재고 증가 조정이 발생한 경우 신규 입고 단가 대장을 생성하여 회계 원가를 평가하는 연계 관계입니다."
            },
            {
                "table_name": "imddiotb",
                "description": "일일 상품 수불 집계 테이블. [조인 키: IMREALTB.MS_NO = IMDDIOTB.MS_NO AND IMREALTB.GOODS_CD = IMDDIOTB.GOODS_CD AND IMREALTB.SURVEY_DATE = IMDDIOTB.CREATE_DATE] 실사 확정 일자별로 조정 수량/금액(modify_qty, modify_cost)의 합계를 일별 수불 조정 필드에 누적 가산하여 일마감 대장을 동기화합니다."
            },
            {
                "table_name": "immmiotb",
                "description": "월별 상품 수불 집계 테이블. [조인 키: IMREALTB.MS_NO = IMMMIOTB.MS_NO AND IMREALTB.GOODS_CD = IMMMIOTB.GOODS_CD AND SUBSTR(IMREALTB.SURVEY_DATE, 1, 6) = IMMMIOTB.CREATE_MONTH] 월말 실사 마감 시, 해당 월의 전체 실사 조정 변동량을 합산하여 월별 재고 평가 리포트에 기말 실사 재고와 손실 원가 항목을 갱신하는 연계입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [조인 키: IMREALTB.GOODS_CD = TGOODSTB.GOODS_CD] 실사 대상 품목의 바코드, 상품명, 소속 브랜드 및 분류 코드 정보를 매칭하여 웹 화면에 조회/출력하기 위해 조인합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. [조인 키: IMREALTB.MS_NO = MGOODSTB.MS_NO AND IMREALTB.GOODS_CD = MGOODSTB.GOODS_CD] 특정 매장에서 해당 품목의 취급 구분(정상, 중지, 사입 등) 및 정상 사용 여부를 확인하여 실사 조정 대상 적합성을 판단할 때 사용됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [조인 키: IMREALTB.MS_NO = MMEMBSTB.MS_NO] 본사 조정/실사 현황 조회 화면(hq_stock_00006)에서 특정 매장의 이름, 주소, 점주 정보 및 매장 타입별 분류를 함께 렌더링하기 위해 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. [조인 키: IMREALTB.REASON_CD = MNAMEMTB.SUB_CD (WHERE MAIN_CD = '901')] 조정 시 선택한 조정 사유 코드(이유코드: 파손, 유통기한 경과, 도난 등)에 부합하는 한글 명칭 라벨을 매칭하여 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. [조인 키: IMREALTB.CREATE_ID = MUSERSTB.USER_ID] 실사를 수동으로 등록하고 '최종 확정'을 실행한 백오피스 사용자 ID의 계정명 및 이름 정보를 감사 및 이력 보존을 위해 조인합니다."
            }
        ]
    }

    # 17. MGMVDTTB MEMO AND RELATED TABLES
    mgmvdttb_memo = (
        "### 1. 테이블 개요\n"
        "매장이동 상세 테이블 (`MGMVDTTB`).\n"
        "가맹점 간의 상품/자재 이동(이체) 거래가 발생했을 때, 전표 단위의 개별 상세 품목 정보(이동 상품코드, 이송 단가, 신청/출고/입고 확인 수량 등)를 기록하는 점간 재고 이동 상세 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 수불/확정 흐름\n"
        "* **점간 이동 프로세스 단계 (`proc_fg`)**\n"
        "  - **`0` (등록)**: 보내는 매장(`send_ms_no`)이 웹 화면(`st_stock_00010`)에서 받는 매장(`receive_ms_no`)과 상품을 지정하여 이동 전표를 임시 등록한 상태\n"
        "  - **`1` (이출확정)**: 보내는 매장에서 출고 수량을 확정하여 이출 처리를 한 상태. 이 시점에 출고지 매장의 현재고(`IMCRIOTB.CUR_QTY`)가 차감되고, 출고 수불 로그(`IMTRLGTB.PROC_FG='T'`)가 기록됩니다.\n"
        "  - **`2` (이입확정)**: 받는 매장에서 배송된 물품을 검수하여 실제 입고된 수량을 입력 및 확정한 상태. 이 시점에 입고지 매장의 현재고(`IMCRIOTB.CUR_QTY`)가 가산되고, 입고 수불 로그(`IMTRLGTB.PROC_FG='F'`)가 기록됩니다.\n"
        "  - **`3` (본사확정)**: 본부 정산 마감 담당자가 최종적으로 가맹점 간의 거래 금액을 확인 및 확정하여 월간 정산 원장에 영구 고정하는 마감 단계\n"
        "* **선입선출 원가 이체 연계**: 매장이동 확정 프로시저 배치(`Sp_SUB_STOCK_MGMVHD_P`) 가동 시, 보내는 매장의 입고 단가 대장(`STCKHITB`)에서 수량을 차감하고, 이를 받는 매장의 신규 선입선출 입고이력(`STCKHITB`) 대장으로 단가 그대로 이전하는 가치 연동 흐름을 탑니다."
    )

    data["tables"]["mgmvdttb"] = {
        "memo": mgmvdttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 본부 식별번호",
            "send_date": "이동출고 등록 일자 (YYYYMMDD)",
            "send_ms_no": "보내는 매장코드 (출고지 점포)",
            "slip_no": "매장이동 전표 일련번호 (4자리)",
            "receive_ms_no": "받는 매장코드 (입고지 점포)",
            "proc_fg": "진행 단계 처리상태 (0: 등록, 1: 이출확정, 2: 이입확정, 3: 본사확정)",
            "goods_cd": "상품코드 (자재 코드)",
            "create_dtime": "최초 등록 일시",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 수정 일시",
            "last_id": "최종 수정자 ID",
            "delete_yn": "삭제 여부 플래그 (Y: 삭제완료, N: 정상)",
            "regi_confirm_qty": "이동 등록 신청 수량 (최초 신청량)",
            "move_confirm_qty": "출고지 점포에서 확정한 이동출고 수량",
            "in_confirm_qty": "입고지 점포에서 최종 수령 검수한 입고 수량",
            "regi_confirm_amt": "등록 신청 기준 금액",
            "move_confirm_amt": "이동출고 확정 기준 금액 (출고지 기준)",
            "in_confirm_amt": "이동입고 확정 기준 금액 (입고지 최종 정산금액)",
            "regi_confirm_vat": "등록 신청 기준 부가세",
            "move_confirm_vat": "이동출고 확정 기준 부가세",
            "in_confirm_vat": "이동입고 확정 기준 부가세",
            "ucost": "이송 거래 기준 공급단가 (원가 기준)",
            "in_qty": "입고 예정 수량"
        },
        "memo_c": "매장 점간이동 등록 화면에서 전표 작성 및 품목 추가 시 신규 등록(proc_fg='0')으로 인서트됩니다.",
        "memo_u": "출고/입고 매장에서 각각 이출 확정, 이입 확정을 클릭함에 따라 수량 정보 및 proc_fg 상태값이 업데이트됩니다.",
        "memo_d": "확정(proc_fg > '0')되기 전 단계에 한하여 사용자가 전표를 삭제할 때 delete_yn = 'Y'로 수정 처리됩니다.",
        "memo_r": "점간이동 현황 조회 화면 및 가맹점 간 정산 회계 리포트에서 입출고 실적 및 단가 대조를 위해 상시 조회됩니다.",
        "related_tables": [
            {
                "table_name": "mgmvhdtb",
                "description": "매장이동 헤더 테이블. [조인 키: MGMVDTTB.SEND_DATE = MGMVHDTB.SEND_DATE AND MGMVDTTB.SEND_MS_NO = MGMVHDTB.SEND_MS_NO AND MGMVDTTB.SLIP_NO = MGMVHDTB.SLIP_NO] 전표별 출고/입고 매장 정보, 총 이동 품목 수, 최종 확정 상태 및 일시 등 전표의 통합 마스터 메타데이터를 관리하는 1:N 매핑 테이블입니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 이동출고 확정(proc_fg = '1') 시 보내는 매장(send_ms_no)의 실재고 수량을 차감하고, 이동입고 확정(proc_fg = '2') 시 받는 매장(receive_ms_no)의 실재고 수량을 가산하여 점포별 재고 잔액을 실시간으로 업데이트합니다."
            },
            {
                "table_name": "imtrlgtb",
                "description": "재고 수불 이력 테이블. 이동 확정 시 출고 점포의 '이동출고(T)', 입고 점포의 '이동입고(F)' 유형에 해당하는 개별 수불 로그를 생성하여 추후 수불 원장 정산 및 감사 추적이 가능하게 기록합니다."
            },
            {
                "table_name": "imtrbktb",
                "description": "수불 트랜잭션 백업 로그 테이블. 매장 간의 이동 실적에 따른 수불 발생 정보를 선입선출 회계 배치가 읽어갈 수 있도록 백업 보관 처리하는 연계 관계입니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고이력/재고평가 대장 테이블. 이동출고 시 보내는 매장의 선입선출 대장에서 해당 자재 품목을 선입선출법에 따라 출고 처리(감소)하고, 이동입고 시 받는 매장의 선입선출 대장에 보낸 매장의 출고 단가를 근거로 신규 입고이력 레코드를 삽입하는 단가 이체 관계입니다."
            },
            {
                "table_name": "stcklgtb",
                "description": "수불 처리 상세 로그 테이블. 점간 이동을 통해 단가와 수량이 타 점포로 이체되는 과정에서, 어떤 전표의 재고가 어느 입고건과 매칭되어 이동하였는지 회계적 매칭 추적 데이터를 세부 기록합니다."
            },
            {
                "table_name": "imddiotb",
                "description": "일일 상품 수불 집계 테이블. 당일 발생한 매장이동 데이터를 합산하여 보내는 매장의 일일 이동출고량, 받는 매장의 일일 이동입고량 필드를 당일 마감 대장에 동기화 렌더링합니다."
            },
            {
                "table_name": "immmiotb",
                "description": "월별 상품 수불 집계 테이블. 월 재고 마감 시 당월 총 가맹점 간 재고 이동 실적(이동입고액, 이동출고액)을 월 수불 대장에 최종 취합하여 기말 재고 및 매출 원가 평가에 반영합니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [조인 키: MGMVDTTB.GOODS_CD = TGOODSTB.GOODS_CD] 이동 대상 품목의 표준 한글 상품명, 바코드, 대/중/소 분류 및 브랜드 정보를 결합 출력하여 화면에 매치하기 위해 조인합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 송수신 매장 각각이 해당 상품을 취급할 수 있도록 등록되어 있는지(취급 코드 적합성) 및 현재 사용 여부를 필터링하기 위해 연계 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [조인 키: MGMVDTTB.SEND_MS_NO = MMEMBSTB.MS_NO / RECEIVE_MS_NO = MMEMBSTB.MS_NO] 보내는 점포명, 받는 점포명, 점주 전화번호 및 소속 물류 센터를 대조 표시하기 위해 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 이동 상태 코드(proc_fg - 0:등록, 1:이출확정, 2:이입확정, 3:본사확정)에 해당하는 한글 상태 값을 매치하여 화면의 상태 컬럼에 보여주기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 점간이동 전표를 신규 등록하고(CREATE_ID), 출고 확정 및 입고 확정을 처리한 각 점포 담당자 사용자 정보를 로깅하고 대조하기 위해 조인됩니다."
            }
        ]
    }

    # 18. MGOODSTB MEMO AND RELATED TABLES
    mgoodstb_memo = (
        "### 1. 테이블 개요\n"
        "매장별 상품 마스터 테이블 (`MGOODSTB`).\n"
        "본사 표준 상품 마스터(`TGOODSTB`)로부터 각 개별 매장(`MS_NO`)에 취급 허가된 상품 정보를 상속받고, 매장 단위의 전용 공급단가, 판매단가, 수수료, 재고 관리 기준, 판매 상태 정보 등을 개별 관리하는 매장별 상품의 중앙 기준 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **본사-매장 마스터 실시간 동기화 (`Tr_TGOODS_T01`)**: 본사 상품 마스터(`TGOODSTB`)의 데이터가 변경(INSERT/UPDATE/DELETE)될 때, 해당 데이터가 특정 매장에 적용되거나 전체 매장으로 전파되는 로직을 트리거를 통해 실시간 동기화합니다.\n"
        "* **POS 및 웹 매출 검증**: 매장 계산대(POS)에서 판매가 일어난 개별 거래는 매출 상세 테이블(`STRNDDTB`)에 등록될 때, 면세/과세 여부(`tax_fg`), 세트 구성 여부(`set_fg`) 등의 마스터 정보와 대조 검증을 거칩니다.\n"
        "* **재고 및 매입 기준 제공**: 발주 및 매입 등록 시 입수량(`in_qty`) 및 매입단가(`ucost`)의 기준 규격이 되며, 선입선출 정산 배치 시 자재의 평가 속성을 제공합니다."
    )

    data["tables"]["mgoodstb"] = {
        "memo": mgoodstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "goods_cd": "상품코드 (자재 코드)",
            "goods_nm": "상품 한글 명칭",
            "goods_sub_nm": "상품 영문 및 보조 명칭",
            "goods_spec": "상품 규격",
            "lclass_cd": "대분류 코드",
            "mclass_cd": "중분류 코드",
            "sclass_cd": "소분류 코드",
            "uprice": "매장 판매가 (소비자가격)",
            "usuprice": "매장 공급가액",
            "ucost": "표준 매입원가",
            "vat_rate": "부가세율 (%)",
            "tax_fg": "과세 구분 (0: 면세, 1: 과세)",
            "goods_price_fg": "금액구분 (0: 일반PLU, 1: NON-PLU, 2: 오픈단가, 3: 포인트 등)",
            "goods_control_fg": "재고 통제 여부 (0: 미통제, 1: 통제)",
            "use_fg": "사용 제한 구분 (0: 일반사용, 1: 판매전용, 2: 매입전용)",
            "set_fg": "세트 상품 구분 (0: 일반단품, 1: 레시피 완제품, 2: 레시피 원자재, 3: 세트구성품)",
            "service_fg": "부가 메뉴 구분 (0: 일반상품, 1: 부가서비스 메뉴)",
            "ord_unit": "발주 단위 코드",
            "in_qty": "매입 포장 입수량 (예: 1박스당 낱개 개수)",
            "inv_unit": "재고 단위 코드",
            "inv_in_qty": "재고 입수량",
            "goods_unit": "상품 기본 단위 수량",
            "min_ord_qty": "최소 발주 제한 수량",
            "goods_point": "상품 적립 포인트",
            "safety_qty": "안전 재고 수량",
            "goods_use_fg": "상품 취급 여부 (0: 정상 사용, 1: 사용 일시중지/단종)",
            "tip_fg": "봉사료 적용 구분 (0: 미적용, 1: 적용)",
            "tax_control_fg": "부가세 통제 구분",
            "source_fg": "소스 코드 사용 여부",
            "goods_type": "상품 유형",
            "calory": "상품 칼로리 정보",
            "defcust_cnt": "적정 보관 일수",
            "origin_no": "원산지 코드 (MGORGMTB 매핑)",
            "product_no": "제조사 코드 (MGPRDMTB 매핑)",
            "grade_no": "상품 등급 코드 (MGRADMTB 매핑)",
            "income_no": "수입원 코드 (MGINCMTB 매핑)",
            "multi_biz_cd": "복수 사업자 코드",
            "create_fg": "등록 구분 (0: 매장직등록, 1: 본사 전송)",
            "create_dtime": "최초 등록 일시",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 수정 일시",
            "last_id": "최종 수정자 ID",
            "sub_group_cd": "부가메뉴 그룹 코드",
            "erp_goods_cd": "ERP 연동용 상품코드",
            "goods_brand_cd": "패션/의류 브랜드 코드",
            "goods_style_cd": "의류 스타일 코드",
            "goods_color_cd": "의류 컬러 코드",
            "goods_siz_cd": "의류 사이즈 코드",
            "recipe_cd": "기준 레시피 코드",
            "fictitious_yn": "가상/의제매입세 적용 여부 (Y/N)",
            "supply_yn": "납품 취급 여부 (Y/N)",
            "usuprice_vat": "공급가액 부가세",
            "set_cd": "세트 관계 코드",
            "purch_rate": "매입 수수료율",
            "delivery_type": "배송 유형 (0: 직송, 1: 센터배송)",
            "image_idx": "상품 이미지 코드 (IMGMSTTB 매핑)",
            "product_standard": "상품 표준 규격명",
            "size_gbn_cd": "사이즈 구분 코드",
            "good_size_cd": "상품 사이즈 코드",
            "menu_grp_cd": "식음료 메뉴 그룹 코드",
            "sale_type_cd": "판매 유형 코드",
            "fictitious_tax": "의제매입세율 정보",
            "store_stock_yn": "본사 직재고 관리 대상 여부",
            "store_stock_ucost": "본사 직재고 원가",
            "goods_dc_fg": "할인 적용 가능 여부 (0: 가능, 1: 불가)",
            "ucost_rate": "원가율",
            "goods_short_name": "상품 단축명 (영수증 출력용)",
            "join_vendor": "주거래처 코드 (MVENDRTB 매핑)",
            "dept_cd": "소속 부서 코드"
        },
        "memo_c": "본사에서 신규 상품 출시 및 가맹점 배포 시 동기화 절차에 의해 점포별로 삽입됩니다.",
        "memo_u": "매장 개별 단가 변경이나 상품 취급 상태(goods_use_fg) 변경 시 수정 처리되며, Tr_MGOODS_T01 트리거를 통해 이력이 로깅됩니다.",
        "memo_d": "데이터 참조 무결성을 위해 실질 삭제 대신 delete_yn 또는 goods_use_fg = '1'(중지)로 비활성화 처리를 권장합니다.",
        "memo_r": "POS 매출 결제, 물류 발주, 매입 등록, 재고 실사 등 HMS 백오피스 내 모든 핵심 데이터 조회 시 조인의 중추 역할을 수행합니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 가맹점 상품 마스터의 근간이 되는 테이블로, 상품코드, 규격, 바코드 등 기본 정보를 상속받고 동기화하기 위해 1:N 관계로 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 매장에서 판매 및 입출고를 개시하기 위해 상품 마스터에 등록된 상품별 실시간 물리 재고 잔량을 1:1로 매핑하여 제어합니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. 기간별 상품 공급단가(USUPRICE) 및 판매가(UPRICE)의 변동 이력을 매장별로 이력 관리하여 상품 마스터에 현재 적용 단가를 제공합니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매장 포스(POS)에서 판매 처리되어 올라온 개별 매출 건의 상품 단가, 할인액, 과세 여부 등을 검증하기 위해 상품 마스터와 조인됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점이 거래처로부터 납품받거나 발주할 때 상품의 포장 규격(IN_QTY), 거래 단가(ucost) 적합성을 마스터와 대조 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 상품별 입출고에 따른 재고 평가 시 자재 마스터 상의 표준 매입원가(ucost)와 과세 구분을 참조하여 입출고 금액을 환산하는 연계 관계입니다."
            },
            {
                "table_name": "imtrlgtb",
                "description": "재고 수불 로그 테이블. 매출, 매입, 조정, 반품 등의 거래 발생 시 상품 마스터에 정의된 규격 및 기본 단위 정보를 기반으로 수불 상세 레코드를 생성합니다."
            },
            {
                "table_name": "imretptb",
                "description": "임시 실사/조정 테이블. 실사 가입력 시 매장 상품 마스터에서 현재 취급 여부 및 정상 사용 여부(goods_use_fg = '0')를 대조 필터링하기 위해 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매장별 상품 분류 키 코드 체계 규격이나 면세/과세 세율 파라미터를 대조 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "imgmsttb",
                "description": "상품 이미지 마스터 테이블. 백오피스 상품 등록 화면이나 포스(POS) 터치키 화면에 표시할 상품 사진/이미지 파일 경로 및 해상도 메타 정보를 조인하여 가져옵니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 매장에서 취급하는 상품 마스터 정보임을 입증하기 위해 소속 가맹점 점포의 코드 및 관리구분을 조인합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 상품 구분(set_fg - 단품/세트), 발주단위(ord_unit), 재고단위(inv_unit) 등의 상태 값을 한글 라벨로 매핑 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 테이블. 매장 상품 마스터의 속성을 신규 등록하거나 수정한 점포 관리자 및 본사 담당자의 실명 정보를 감사 추적하기 위해 조인합니다."
            }
        ]
    }

    # 19. MMEMBSTB MEMO AND RELATED TABLES
    mmembstb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 마스터 테이블 (`MMEMBSTB`).\n"
        "체인 브랜드에 속한 모든 개별 가맹점 점포(`MS_NO`)의 기본 인적 정보(매장명, 대표자명, 사업자번호, 전화번호, 주소)와 POS 기기 설정, 영수증 꼬리말/머리말, 오픈/폐점 상태 정보를 관리하는 매장 정보의 최상위 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹점 차단 시 사용자 계정 실시간 차단 (`MMEMBS_T01` 트리거)**: 가맹점의 오픈구분(`open_fg`)이 `3` (Hold) 또는 `4` (폐점) 등으로 변경될 경우, 해당 매장에 소속된 시스템 사용자 계정(`MUSERSTB`)의 만료 여부(`ACCT_EXPIRE`)를 `'Y'`로 강제 업데이트하여 백오피스 사용 권한을 실시간으로 박탈/차단합니다. 상태가 해제되면 `'N'`으로 자동 환원합니다.\n"
        "* **중요 세무 정보 이력 감사 (`MMEMBS_T01` 트리거)**: 사업자번호(`biz_no`), 대표자명(`master_nm`), 가맹점명(`ms_nm`)이 변경될 때 변경 내역을 감사 로그 테이블(`MMEMLGTB`)에 안전하게 자동 아카이빙합니다.\n"
        "* **POS 실시간 데이터 전송 연계 (`MMEMBS_T01` 트리거)**: 영수증 메타 정보(상호명, 주소, 전화번호, 머리말/꼬리말 등)가 갱신될 때 실시간 전송 패키지 테이블(`SSMEMBTB` 및 `MMSLOGTB`)에 전송 데이터를 삽입하여 각 매장의 POS 단말기로 수정 내역을 즉시 밀어냅니다."
    )

    data["tables"]["mmembstb"] = {
        "memo": mmembstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "ms_nm": "매장명 (가맹점 한글 명칭)",
            "ms_eng_nm": "매장 영문 명칭",
            "chain_no": "체인 본부 식별번호 (0000: 독립가맹점)",
            "chain_hq_yn": "본부 여부 플래그 (Y: 본사/본부, N: 일반 매장)",
            "chain_area": "체인 지역 분류 코드",
            "biz_no": "사업자등록번호 (하이픈 제외 10자리)",
            "bs_type": "업태 (사업자등록증 상의 업태)",
            "bs_kind": "업종 (사업자등록증 상의 업종)",
            "master_nm": "대표자 실명",
            "tel_no": "매장 대표 전화번호",
            "hp_no": "점주 휴대폰 번호",
            "emg_no": "긴급 연락처 번호",
            "fax_no": "매장 팩스 번호",
            "homepage": "가맹점 홈페이지 URL",
            "zip_no": "우편번호 (5자리 또는 6자리)",
            "bill_addr": "영수증 명판 출력용 대표 주소",
            "address": "물리적 가맹점 도로명/지번 주소",
            "address_bunji": "세부 번지 주소",
            "bank_cd": "거래계좌 개설 은행코드 (MBANKMTB 매핑)",
            "acct_cd": "정산 입금용 계좌번호",
            "acct_nm": "예금주 명의",
            "use_yn": "가맹점 마스터 사용 여부 (Y/N)",
            "head_msg": "영수증 머리말 (인사말 등)",
            "tail_msg": "영수증 꼬리말 (환불 규정 등)",
            "open_fg": "영업 구분 (0: 오픈준비, 1: 예정, 2: 영업중, 3: 보류, 4: 폐점)",
            "open_date": "최초 오픈 일자 (YYYYMMDD)",
            "close_date": "폐업/해약 일자 (YYYYMMDD)",
            "shop_type": "매장 분류형태 (R: 식음료, F: 패션, C: 편의점, A: 복합매장 등)",
            "tax_type": "과세 유형 (0: 면세, 1: 과세)",
            "create_dtime": "가맹점 마스터 생성 일시",
            "create_id": "생성자 ID",
            "last_dtime": "최종 정보 수정 일시",
            "last_id": "최종 정보 수정자 ID",
            "excel_shop_code": "외부 엑셀 연동용 코드",
            "erp_cd": "본사 ERP 연동 점포코드",
            "erp_vat_cd": "ERP 세무 처리용 분류코드",
            "comm_rate": "가맹 계약 수수료율",
            "shop_sales_area": "매장 평수/면적 분류",
            "d_shop_code": "배달대행 연동 매장코드",
            "shop_lc_cd": "업태 대분류 코드",
            "shop_mc_cd": "업태 중분류 코드",
            "shop_sc_cd": "업태 소분류 코드",
            "master_eng_nm": "대표자 영문 성명",
            "eng_address": "가맹점 상세 영문 주소",
            "shop_wh_yn": "물류 창고 여부 플래그 (Y: 재고 전용 창고, N: 일반 매장)",
            "work_appr_yn": "가맹 계약 및 운영 승인 상태",
            "shop_brand_cd": "가맹점 취급 브랜드 코드",
            "mpoint_rate": "멤버십 포인트 적립 비율",
            "if_biz_cd": "외부 연동용 통합 사업자코드",
            "if_shop_cd": "외부 연동용 통합 매장코드",
            "if_reserve_amt": "점포 보증금/예치금 잔액",
            "if_return_reserve_amt": "반품 보증금 잔액",
            "if_blue_jos_no": "블루포인트 가맹계약 번호",
            "pre_purch_wh_ms_no": "입고 예정품 보관용 창고 매장코드"
        },
        "memo_c": "본사 매장관리 화면(hq_master_00004)에서 신규 가맹점이 승인되어 등록될 때 인서트됩니다.",
        "memo_u": "매장정보관리 화면(st_master_00001)에서 매장 상세 정보 수정 시 업데이트되며, 중요 정보 변경 시 트리거를 통해 이력 아카이빙 및 POS 전송 프로세스가 가동됩니다.",
        "memo_d": "데이터 참조 무결성을 위해 물리 삭제가 전면 방지되며, 해약 시 open_fg = '4'(폐점) 및 use_yn = 'N'으로 비활성화 처리됩니다.",
        "memo_r": "HMS 시스템 내의 모든 매장 단위 정보 조회, 수불, 매출, 매입 원장의 최상위 필터 마스터로서 상시 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 가맹점 마스터와 매칭되어 가맹점별로 취급 가능한 상품 목록을 배포하고 매입/매출 속성을 정의합니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. [트리거 MMEMBS_T01 연동] 가맹점의 오픈 상태(open_fg = 3:홀드, 4:폐점)에 따라 해당 매장에 속한 모든 시스템 사용자 계정의 계정 만료 여부(ACCT_EXPIRE)를 실시간으로 자동 차단/활성화 처리합니다."
            },
            {
                "table_name": "mmembvtb",
                "description": "가맹점 관리변수 마스터 테이블. [트리거 MMEMBS_T01 연동] 매장의 포인트 적립률, 키친프린터 그룹화 여부, 절사 단위 및 배달/배송 시스템 사용 여부 등 POS 연동용 상세 제어 변수를 가맹점 마스터와 연계 관리합니다."
            },
            {
                "table_name": "mmembptb",
                "description": "매장 POS 속성 마스터 테이블. 매장에 속한 개별 POS 단말기의 번호, 사용 용도(주문용, 계산용 등), 고객 디스플레이 표시 여부를 설정 제어합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMEMBS_T01 연동] 가맹점의 마스터 명칭, 사업자 정보 등이 수정될 때 포스(POS) 연동 서버로 전송할 변경 로그를 즉시 기록합니다."
            },
            {
                "table_name": "ssmembtb",
                "description": "POS 가맹점 마스터 송신 테이블. [트리거 MMEMBS_T01 연동] 가맹점 정보(대표자명, 전화번호, 영수증 머리말/꼬리말 등) 변경 시 해당 데이터를 POS 단말기로 전파하기 위해 전송 패키지로 구조화하여 대기시킵니다."
            },
            {
                "table_name": "mmemlgtb",
                "description": "가맹점 중요정보 로그 테이블. [트리거 MMEMBS_T01 연동] 가맹점의 사업자등록번호(BIZ_NO), 대표자명(MASTER_NM), 가맹점명(MS_NM) 등 세무 및 정산에 민감한 3대 메타데이터가 수정될 때 이전 값과 변경된 값을 감사용 로그로 개별 아카이빙합니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 특정 가맹점 점포에서 발생한 일자별 포스 매출 총액, 할인액, 카드사 전표 매칭 및 마감 실적을 가맹점 정보와 대조하기 위해 조인합니다."
            },
            {
                "table_name": "macciotb",
                "description": "가맹점 금전 수납 테이블. 매장별 시조, 시금, 중간입금 및 마감 시 입출금 정산 내역을 가맹점 정보와 매치하기 위해 조인됩니다."
            },
            {
                "table_name": "obslphtb",
                "description": "가맹점 매입/발주 마스터 테이블. 가맹점별 물류 본사 발주 및 거래처 매입 공급 대장을 가맹점 마스터의 배송 유형 및 사용 여부와 조인하여 물류 수주를 관리합니다."
            },
            {
                "table_name": "imcriotb",
                "description": "가맹점 재고 정보 테이블. 매장별로 취급 가능한 상품 품목들의 물리적인 재고 보유 잔량을 점포 정보와 매핑하여 백오피스 재고조회 화면에 연계 렌더링합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 타입별 부가세 절사 옵션이나 시스템 기본 통신 포트 규격 관련 파라미터 매치에 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 가맹점의 매장 타입(shop_type - 마트, 식음, 베이커리 등), 오픈 구분(open_fg), 배송 구분 등의 분류 코드를 한글 라벨로 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "mbankmtb",
                "description": "은행 코드 마스터 테이블. 가맹점 가입 시 등록한 계좌의 입출금 거래 은행 코드와 한글 정식 은행명칭을 매칭하기 위해 조인합니다."
            },
            {
                "table_name": "mcardmtb",
                "description": "카드사 마스터 테이블. 매장 포스(POS)에서 발생한 가맹점 고유 카드사 승인 번호 및 매입 승인 수수료율 설정을 매칭 관리하기 위해 조인됩니다."
            }
        ]
    }

    # 20. MMEMBVTB MEMO AND RELATED TABLES
    mmembvtb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 관리변수 마스터 테이블 (`MMEMBVTB`).\n"
        "매장별(`MS_NO`)로 가동되는 각종 시스템 환경 설정(포인트 적립 정책, 금액 끝전 절사 단위 및 처리 구분, 주방 프린터 연동 개수, 배달 시스템 사용 여부, 여신용도한도액 등)의 핵심 변수를 모아 정의하는 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **주방프린터 연동 조건에 따른 설정 초기화 (`MMEMBV_T01` 트리거)**: 가맹점 관리 변수에서 주방프린터 그룹화 여부(`KITCHEN_GROUP_YN`) 설정이 변경(`AFTER UPDATE`)되는 경우, 기존에 해당 매장으로 지정되어 있던 주방프린터 설정 테이블(`MKPRNTTB`)의 상세 매핑 레코드를 자동으로 일괄 삭제(`DELETE`) 처리하여 데이터 꼬임을 방지합니다.\n"
        "* **POS 실시간 환경설정 전파 (`MMEMBV_T01` 트리거)**: 포인트 적립 규격, 절사 정책, 주방주문 연동 유무 등 POS 환경 정보가 수정될 때 실시간 전송 대기열 테이블(`SSMEMBTB` 및 `MMSLOGTB`)로 패키지 로그를 인서트하여 매장 단말기에 실시간 환경설정 데이터 패키지를 배포합니다.\n"
        "* **매출/매입 정산 및 여신 차단**: 매장 마감 매출 정산 시 끝전 처리 규정에 맞춰 매출 전표의 계산 수치를 검증하며, 물류 발주 시 설정된 여신 한도(`credit_limit`)를 초과하는 발주 생성을 제어합니다."
    )

    data["tables"]["mmembvtb"] = {
        "memo": mmembvtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "chain_no": "체인 본부 식별번호",
            "cit_yn": "포스 매출 소수점 금액 취급 여부 (Y/N)",
            "point": "멤버십 기본 포인트 적립 비율 (%)",
            "point_unit": "멤버십 포인트 부여 단위액",
            "point_card_mask": "포인트 카드번호 마스킹 형식",
            "round_fg": "포인트 끝전 처리 구분",
            "kitchen_yn": "주방 주문서 인쇄 방식 (0: 미사용, 1: 주방구분인쇄, 2: 부서구분인쇄)",
            "delivery_yn": "배달 시스템 연동 여부 (0: 미연동, 1: 연동)",
            "demand_fg": "청구 대금 처리 방식 (0: HDC, 1: EDI)",
            "cust_mng_fg": "고객 정보 관리 구분 (0: 비관리, 1: 가맹점 개별관리)",
            "credit_limit": "가맹점 물류 발주 여신한도액 (원화 기준)",
            "vat_fg": "세금(부가세) 계산 방식 및 끝전 처리 플래그",
            "shop_area_cd": "점포 소속 행정 지역 코드",
            "shop_class_cd": "점포 분류 구분 코드",
            "emp_card_mask": "임직원 할인 카드 마스킹 형식",
            "goods_fg": "상품 코드 입력 방식 구분 (0: 수동PLU제한, 1: 자동)",
            "ucost_vat_fg": "매입 자재 공급원가의 부가세 포함 여부 처리 규칙",
            "plu_gu": "PLU 코드 관리 유형",
            "ocb_cat_id": "OK캐쉬백 가맹점 번호 (CAT ID)",
            "ocb_passwd": "OK캐쉬백 거래 비밀번호",
            "corp_fg": "법인/개인 가맹점 구분 (0: 개인, 1: 법인)",
            "ddc_yn": "가맹 계약 대금 자동이체 청구 방식 여부",
            "cost_fg": "매장 원가 계산 방식 (0: 표준원가, 1: 이동평균법, 2: 선입선출, 3: 총평균법)",
            "cost_s_yymm": "원가법 적용 시작 년월 (YYYYMM)",
            "usuprice_fg": "상품 공급단가 결정 방식 플래그",
            "ucost_fg": "상품 매입원가 결정 방식 플래그",
            "amt_round_pos": "금액 끝전 절사 위치 (0: 소수점 이하, 1: 소수첫째자리, 2: 1원 단위, 3: 10원 단위, 4: 100원 단위)",
            "amt_round_type": "금액 끝전 처리 방식 (0: 반올림, 1: 절사, 2: 올림)",
            "create_dtime": "환경 변수 최초 생성 일시",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 정보 수정 일시",
            "last_id": "최종 정보 수정자 ID",
            "kitchen_cnt": "주방 주문서 전송 대상 프린터 대수",
            "sale_del": "영수증 출력 시 할인 표기 마스킹 규정",
            "weight_unit": "중량 표시 기본 단위",
            "price_unit": "화폐 표시 기본 단위",
            "goodscd_len": "상품코드 표준 규격 자릿수",
            "scale_goodscd_len": "전자저울 바코드 연동 규격 자릿수",
            "kitchen_group_yn": "주방프린터 출력 그룹화 사용 여부 (0: 미사용, 1: 사용)",
            "order_fg": "발주/수주 제한 정책 플래그",
            "prt_v_margin": "영수증 상단 인쇄 수직 여백 설정 (mm)",
            "prt_h_margin": "영수증 좌우 인쇄 수평 여백 설정 (mm)"
        },
        "memo_c": "본사 매장관리 화면에서 매장 생성 시 기본 환경변수 템플릿 형태로 자동 생성 삽입됩니다.",
        "memo_u": "본사의 매장 운영항목 관리 모달(hq_master_00004_M04)에서 속성이 변경될 때 업데이트되며, 트리거를 통해 주방 설정 정리 및 POS 환경 전송 프로세스가 즉시 가동됩니다.",
        "memo_d": "가맹점 거래 원장과 직결된 정산 룰이므로 시스템 상에서의 물리 삭제가 엄격히 차단됩니다.",
        "memo_r": "POS 매출 마감 정산, 물류 발주 여신한도 초과 검사, 상품 단가 매핑 계산 시 기준 정책으로 수시 롤업 조회됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 기본 정보 마스터 테이블. 가맹점 관리 변수 마스터와 1:1 결합하여 점포의 인적 속성과 물리적 시스템 제어 변수를 원스톱 통합 관리합니다."
            },
            {
                "table_name": "mkprnttb",
                "description": "주방 프린터 설정 테이블. [트리거 MMEMBV_T01 연동] 가맹점 관리 변수에서 주방프린터 그룹화 구분(KITCHEN_GROUP_YN)이 수정될 때, 기존 주방프린터 포트 매핑 및 분류 설정 정보(MKPRNTTB)를 실시간으로 자동 초기화 삭제 처리합니다."
            },
            {
                "table_name": "mmembptb",
                "description": "매장 POS 속성 마스터 테이블. 매장의 관리변수에 설정된 영수증 절사 기준 및 주방 주문서 출력 여부 변수를 각 POS 단말기의 동작 옵션과 결합 제어합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMEMBV_T01 연동] 관리 변수 항목(포인트 적립률, 부가세 처리 기준, 절사 단위 등)이 갱신될 때 실시간 연동 서버로 전송할 변경 로그 패키지를 즉시 인서트합니다."
            },
            {
                "table_name": "ssmembtb",
                "description": "POS 가맹점 마스터 송신 테이블. [트리거 MMEMBV_T01 연동] 포인트 부여 규격 및 금액 절사 방식이 업데이트될 때 해당 정보를 POS 단말기에 즉각 배포 송신하기 위해 전송 대기열에 기록합니다."
            },
            {
                "table_name": "mmemlgtb",
                "description": "가맹점 중요정보 감사 로그 테이블. 대표 가맹점 변수의 정산 규정이나 보증금 기준 등이 수정될 때 감사 변경 이력을 로깅 보존합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 매장의 매입 원가 과세 구분(ucost_vat_fg) 및 판매가 관리 방식(usuprice_fg) 등 상품 마스터의 단가 계산 정책의 기준이 되는 환경 변수를 제공합니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "가맹점 매출 헤더 테이블. 매출 정산 시 매장별 금액 절사 처리 방식(amt_round_pos - 원 단위, 십 원 단위 절사 등)을 조회하여 매출 전표의 끝전 처리 및 최종 수납 금액을 대조 검증합니다."
            },
            {
                "table_name": "macciotb",
                "description": "가맹점 금전 수납 테이블. 매장 마감 정산 시 포인트 결제액 차감이나 임직원 카드 할인 한도 초과 규정을 검증하기 위해 점포 환경 설정 변수와 조인합니다."
            },
            {
                "table_name": "obslphtb",
                "description": "가맹점 매입/발주 마스터 테이블. 본사 발주 신청 시 매장별 여신용한도액(credit_limit)을 초과하여 발주하지 못하도록 차단하거나, 임시 매입 검수 시 원가 과세 계산 정책을 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 관리 변수 마스터의 절사 방식 및 포인트 단위 체계의 공통 파라미터 유효성을 매칭 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 관리 변수 상의 주방 설정 방식, 청구 방식(HDC, EDI 등) 및 절사 타입 등의 코드를 한글 라벨로 매핑하기 위해 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 테이블. 매장의 임직원 할인 카드 마스킹 패턴(emp_card_mask) 검증 및 관리 변수 변경을 감행한 등록/수정자 ID의 감사 추적을 위해 조인합니다."
            }
        ]
    }

    # 21. MPRILGTB MEMO AND RELATED TABLES
    mprilgtb_memo = (
        "### 1. 테이블 개요\n"
        "매장별 단가 변경 로그 테이블 (`MPRILGTB`).\n"
        "매장별 상품 판매가/공급가 등 단가 정보가 추가, 수정, 삭제될 때 모든 가맹점의 소급 적용 히스토리 및 예약 변경 일정을 기록하여 단가 감사 추적(Audit Trail)과 소급 계산을 가능하게 하는 이력 관리 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **매장 단가 변경 실시간 이력 로깅 (`MPRICE_T01` 트리거)**: 매장 개별 단가 마스터(`MPRICETB`)에 단가가 입력, 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)될 때, 이전 가격(`PRE_PRICE`)과 신규 가격(`PRICE`), 변경을 감행한 등록자 정보를 포함하여 `MPRILGTB`에 실시간으로 히스토리 레코드를 자동 생성합니다.\n"
        "* **본사 단가 변경 시 전 가맹점 단가이력 동기화 (`TPRICE_T01` 트리거)**: 본사의 전국 표준 단가 마스터(`TPRICETB`)가 변경되는 경우, 해당 체인 브랜드 하위의 영업 중인 가맹점(`MMEMBSTB.OPEN_FG` <> '4')을 대상으로 `MPRILGTB`에 단가 변동 지시 및 적용 이력을 일괄 생성/복구 처리합니다.\n"
        "* **소급 계산 및 POS 실시간 연계**: 과거 단가 입력 오류로 단가가 소급 수정되었을 때 소급 재계산 배치 프로시저를 통해 수불 원장을 보정하는 원천 기준 자료가 되며, 미래 예약 단가가 실제 활성화될 때 POS 기기로 단가 패키지를 전송하기 위한 데이터 스케줄 연계가 처리됩니다."
    )

    data["tables"]["mprilgtb"] = {
        "memo": mprilgtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_fg": "처리 구분 (A: 추가, U: 수정, D: 삭제, R: 복구)",
            "ms_no": "매장코드 (점포 코드)",
            "goods_cd": "상품코드 (자재 코드)",
            "price_fg": "단가 구분 (0: 일반소비자가/판매가, 1: 가맹점 공급가, 2: 특수단가)",
            "start_date": "단가 적용 시작 일자 (YYYYMMDD)",
            "end_date": "단가 적용 종료 일자 (YYYYMMDD)",
            "pre_price": "변동 이전 단가",
            "price": "변동 이후 신규 적용 단가",
            "raise_fg": "단가 등락 여부 (0: 인상, 1: 인하)",
            "goods_control_fg": "단가 통제 여부 (0: 미통제, 1: 통제)",
            "create_dtime": "단가 변경 최초 등록 일시",
            "create_id": "단가 변경 등록자 ID (운영자/가맹점주)",
            "last_dtime": "단가 변경 최종 수정 일시",
            "last_id": "단가 변경 최종 수정자 ID",
            "goods_brand_cd": "상품 브랜드 분류 코드",
            "goods_style_cd": "상품 스타일 분류 코드"
        },
        "memo_c": "매장별 단가 마스터(MPRICETB) 또는 본사 단가 마스터(TPRICETB) 변경 시 각각 MPRICE_T01, TPRICE_T01 트리거에 의해 자동으로 기록됩니다.",
        "memo_u": "단가 적용 스케줄(start_date/end_date) 및 변경 이력의 사후 검증이 완료되어 확정 처리될 때 수정됩니다.",
        "memo_d": "단가 소급 계산 및 세무 감사의 핵심 증빙 데이터이므로 시스템 상에서의 물리 삭제가 전면 제한됩니다.",
        "memo_r": "과거 매출의 단가 정밀 소급 정산, 미래 예약 단가 활성화 배치, 단가 변동 감사 보고서 출력 시 이력 원장으로 롤업 조회됩니다.",
        "related_tables": [
            {
                "table_name": "mpricetb",
                "description": "매장별 단가 마스터 테이블. [트리거 MPRICE_T01 연동] 매장별 상품의 개별 판매단가/공급단가 변경 행위 발생 시, 이전 단가(pre_price)와 신규 적용 단가(price)를 매핑하여 실시간 단가 변경 이력 로그로 쌓는 원천 테이블입니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 마스터 테이블. [트리거 TPRICE_T01 연동] 본사에서 지정한 전국 표준 공급가/판매가가 수정되면, 해당 체인 브랜드 하위의 모든 유효 가맹점에 단가 변동 내용을 전파하고 단가 변경 지시 로그를 생성시킵니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 단가가 변경된 상품의 규격, 과세 구분, 단가 구분 등의 기본 속성을 참조하기 위해 조인합니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 단가 변동이 가맹점 단가 이력으로 상속 동기화될 때, 본사 마스터에 존재하는 유효한 활성 상품 코드인지 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [트리거 TPRICE_T01 연동] 본사 단가 변경 내용을 배포할 때, 영업 구분(open_fg)이 4(폐점) 상태가 아닌 정상 운영 중인 가맹점들만 선별하여 단가 변경 로그를 발생시키는 유효성 검증에 사용됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 결제 시 적용된 상품 단가에 단가 오차가 존재하여 정산 단가 대조가 필요할 때, 해당 매출 일자 기준의 과거 단가 변경 변경 이력(MPRILGTB)을 역추적하여 적용 당시 단가의 적합성을 소급 검증하는 데 사용됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 포스 매출 결제 시 적용된 단가의 변동 여부와 금액 정합성을 단가 이력 대장과 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 단가 변경 이력에 등록된 미래 시점(예약 단가)의 시작일자가 도래하여 단가가 실제 적용될 때, 해당 단가를 포스 단말기로 실시간 다운로드 전송하기 위한 전송 큐 로그를 생성하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 특정 기간의 단가 변동이 입고 원가 및 매출 원가에 미친 재무적 영향을 정밀 평가할 때, 표준 매입원가의 소급 변동 로그로서 이 이력 테이블을 대조 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 단가 구분(price_fg - 0: 판매가, 1: 공급가) 및 처리 구분(proc_fg - A: 추가, U: 수정, D: 삭제)의 영문 약어 코드를 한글 라벨로 맵핑 출력하기 위해 조인합니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 매장별 또는 본사별 단가 개정 및 특별 단가 입력을 실행한 백오피스 운영자의 계정 실명 정보(create_id, last_id)를 감사 추적 보고서에 출력하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매장 분류별 단가 가중치나 통화(Currency) 소수점 절사 정책을 대조 조회하기 위해 연계됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 발주 또는 매입 등록 시 적용된 공급 단가가 단가 변경 이력상의 표준 공급가 및 계약가와 일치하는지 단가 검증 모듈에서 소급 검사하기 위해 조인 참조합니다."
            }
        ]
    }

    # 22. SGOODSTB MEMO AND RELATED TABLES
    sgoodstb_memo = (
        "### 1. 테이블 개요\n"
        "일별 매장 상품 실적 / 일별 상품 매출 실적 테이블 (`SGOODSTB`).\n"
        "각 가맹점 점포별(`MS_NO`)로 매일(`SALE_DATE`) 판매된 개별 상품(`GOODS_CD`)의 판매 수량, 총 판매액, 부가세, 실매출액 및 할인 형태별 금액(일반, 서비스, 제휴카드, 쿠폰, 멤버십 포인트 등)의 일 단위 누적 실적 데이터를 관리하는 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **매출 등록 시 실시간 일별 실적 집계 (`STRNDT_T01` 트리거 및 `SUB_SGOODS_P` 프로시저)**: 포스(POS)에서 판매 상세 결제 데이터(`STRNDTTB`)가 수신될 때, `STRNDT_T01` 트리거가 작동하여 `SUB_SGOODS_P` 프로시저를 호출합니다. 프로시저 내부에서는 해당 일자의 점포별/상품별 실적 레코드가 존재하면 판매 수량(`SALE_QTY`) 및 총매출액, 과세금액 등을 합산 업데이트(`UPDATE`)하고, 없는 경우 새 실적 레코드를 생성(`INSERT`)합니다.\n"
        "* **월별 매출 실적 동기화**: 일별 매출 집계가 수행될 때 동일한 트리거 체인 내에서 월별 매장 상품 실적 테이블(`SGOODMTB`)도 월별 누적 프로시저(`SUB_SGOODM_P`)를 가동하여 일별/월별 실적 정보를 일체화시킵니다.\n"
        "* **매출 분석 통계의 기본 원천**: 백오피스 분석 시스템 내의 모든 상품군 기간별/요일별/분류별 매출 현황 분석 화면에서 실시간 쿼리 조회의 주 데이터 소스(Data Source)로 활용됩니다."
    )

    data["tables"]["sgoodstb"] = {
        "memo": sgoodstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "sale_date": "매출 영업 일자 (YYYYMMDD)",
            "goods_cd": "상품코드 (자재 코드)",
            "lclass_cd": "대분류 코드",
            "mclass_cd": "중분류 코드",
            "sclass_cd": "소분류 코드",
            "chain_no": "체인 본부 식별번호",
            "chain_area": "체인 지역 분류 코드",
            "sale_qty": "당일 상품 판매 수량",
            "sale_tot": "당일 상품 판매 총액 (실매출액 + 할인합계액)",
            "sale_amt": "당일 상품 실 매출액 (할인 제외 순수 매출액)",
            "dc_amt": "당일 적용 총 할인 합계 금액",
            "vat_amt": "당일 판매 상품에 대한 부가세액",
            "norm_dc_amt": "일반/행사 할인 금액",
            "service_dc_amt": "서비스/프로모션 할인 금액",
            "card_dc_amt": "제휴/신용카드사 청구 할인 금액",
            "coupon_dc_amt": "쿠폰 적용 할인 금액",
            "cust_dc_amt": "고객 멤버십 포인트 차감 할인 금액",
            "emp_dc_amt": "사내 임직원 사원카드 할인 금액",
            "cash_dc_remant": "현금 영수증 끝전 및 기타 할인 보정액",
            "dept_dc_amt": "소속 부서/법인 할인액",
            "sale_vat": "내세 부가세액 (부가세 포함 판매 시 산출된 세액)",
            "net_sale_amt": "부가세 제외 순매출액"
        },
        "memo_c": "포스 매출 전송 시 매출 상세 트리거(STRNDT_T01)와 SUB_SGOODS_P 프로시저에 의해 매일 자동 생성/누적 처리됩니다.",
        "memo_u": "당일 판매가 추가로 들어오거나 매출 취소/반품 거래가 발생하여 상세 원장이 변경될 때 업데이트(차감) 처리됩니다.",
        "memo_d": "매장별 일자별 세무 및 손익 평가의 근간 자료이므로 인위적인 삭제가 전면 방지됩니다.",
        "memo_r": "기간별 상품 매출 현황, 카테고리별 매출 분석, 요일별 매출 보고서, 마트 매출 일보/주보 출력 시 최상위 실적 원장으로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. [트리거 STRNDT_T01 연동] 포스(POS)에서 상세 판매 결제가 완료되어 데이터가 적재될 때, 해당 거래의 매출액, 할인액, 수량 등이 일별 실적 테이블(SGOODSTB)로 이관/누적 업데이트됩니다."
            },
            {
                "table_name": "sgoodmtb",
                "description": "월별 매장 상품 실적 테이블. [트리거 STRNDT_T01 연동] 일별 매출 실적이 누적될 때 동일한 트리거 흐름에서 월별 실적 프로시저(SUB_SGOODM_P)도 가동하여 월간 실적 원장을 함께 동기화 처리합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 매출 실적 집계 대상 상품의 대/중/소분류 카테고리 정보 및 표준 판매단가, 과세 여부 매칭에 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 지역(chain_area)이나 특정 체인 본부(chain_no) 소속 매장들의 매출 실적을 그룹화하여 조회 분석할 때 조인됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일자별 총 결제 건수, 객수, 영수증 건당 구매액(객단가) 등 헤더 레벨의 실적과 상품별 개별 매출 실적의 총합 정합성을 검증하기 위해 조인합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 일별 매출 수량(sale_qty)만큼 선입선출법에 의해 재고를 출고 처리하고, 당일 매출에 대한 매출원가(COGS) 및 매출총이익을 평가하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 매일 마감 시 일별 매출 수량만큼 점포의 상품 현재고 실재고 수량을 차감 조율하기 위해 연동 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 대/중/소분류 코드 및 할인 코드 분류 등 실적 보고서에 출력할 분류 라벨명을 한글 정식 명칭으로 변환하기 위해 조인합니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 매출이 발생한 상품 코드에 대한 본사 표준 규격 및 바코드 정보를 매칭하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매출 실적 집계 시 적용할 소수점 절사 정책이나 세무 부가세 계산 방식 등의 기준 규칙 조회에 조인 참조됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 매출 취소 또는 특별 할인이 적용된 일별 매출 실적 대장을 조회할 때, 해당 거래를 승인/처리한 포스 근무자 계정 정보를 확인하기 위해 조인합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 일별 매출 실적과 매입 실적을 상호 대조하여 점포별 매출 대비 매입 비율(매입율) 및 적정 재고 보유 일수 분석 보고서를 추출할 때 연동 참조됩니다."
            }
        ]
    }

    # 23. SKTFDCTB MEMO AND RELATED TABLES
    sktfdctb_memo = (
        "### 1. 테이블 개요\n"
        "POS 제휴/KTF 카드 상품 할인율 테이블 (`SKTFDCTB`).\n"
        "가맹점별(`MS_NO`) 제휴 카드(통신사 멤버십 할인 등)의 상품별 할인율 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 구조화하여 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **할인율 정보 실시간 동기화 큐 적재 (`MKTFDC_T01` 트리거)**: 매장 제휴카드 상품 할인율 마스터 테이블(`MKTFDCTB`)에 신규 등록, 할인율 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MKTFDC_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg` - A/U/D), 매칭 상품코드, 할인율(`dc_rate`) 정보를 실시간으로 `SKTFDCTB` 큐에 인서트합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 변경 이력이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈이 해당 데이터를 가공하여 개별 가맹점의 POS 단말기 메모리로 즉시 전송 및 다운로드 반영시킵니다.\n"
        "* **매출 제휴 할인 적합성 소급 검증**: 포스 매출 결제 시 고객이 적용받은 제휴 할인액(`card_dc_amt`)이 해당 거래 시점에 POS 단말기에 다운로드된 할인율 정책(`dc_rate`, `round_fg`) 기준과 일치하게 연산되었는지 정합성을 사후 대조 검증하는 근거 데이터로 작동합니다."
    )

    data["tables"]["sktfdctb"] = {
        "memo": sktfdctb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "ktf_cd": "제휴사/카드 구분 코드 (예: KTF 기본, KTF VIP 등)",
            "goods_cd": "상품코드 (자재 코드)",
            "dc_rate": "제휴 할인율 (%)",
            "round_fg": "금액 절사 방식 구분 (0: 반올림, 1: 절사, 2: 올림)"
        },
        "memo_c": "매장 제휴카드 할인율 마스터(MKTFDCTB) 테이블의 변동 시 MKTFDC_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 제휴 할인 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 제휴 할인 데이터 배포 관리 모듈, 제휴사 카드 매출 일보/주보 조회 시 정산 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mktfdctb",
                "description": "매장 제휴카드 상품 할인율 마스터 테이블. [트리거 MKTFDC_T01 연동] 백오피스 또는 본사에서 제휴사 할인 마스터를 등록/수정/삭제 처리하면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SKTFDCTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 제휴사 할인이 적용되는 개별 자재/상품의 한글 명칭, 카테고리 분류, 상품 유형을 조회하고 매칭하기 위해 조인합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점 점포의 지역 코드 및 정상 사용 여부(use_yn)를 확인하여 해당 점포의 POS 기기로 제휴 할인 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 포스 매출 결제 시 적용된 통신사 제휴 할인액이 당일 시점의 할인율 정책(dc_rate, round_fg)대로 정교하게 산출되었는지 사후 대조 검증을 수행하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 제휴 할인 마스터의 변동 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 제휴사 제휴 할인율 한도 규정(예: 1회 최대 10%, 일일 최대 한도 등)의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 제휴사 구분 코드(ktf_cd - KTF 멤버십 등) 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 제휴 할인 상품 및 할인율을 등록/해제 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사에서 제휴사 할인 대상 품목의 기준 코드가 유효하게 존재하는 활성 자재인지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 제휴 할인 행사 품목의 매입 원장과 매출 대비 기여도 비율을 연계 정산 보고서로 분석할 때 비교용으로 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 제휴 할인 품목의 실시간 판매 추이와 남은 재고량을 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 제휴 할인 판매된 수량의 마진율을 평가하기 위해 상품 원가를 대조 조회하는 데 조인 연계됩니다."
            }
        ]
    }

    # 24. SKTFRTTB MEMO AND RELATED TABLES
    sktfrttb_memo = (
        "### 1. 테이블 개요\n"
        "POS 제휴/KTF 카드 기본 할인정보 테이블 (`SKTFRTTB`).\n"
        "가맹점별(`MS_NO`) 제휴 카드(통신사 멤버십 등)의 기본 프로모션 할인 규칙 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 구조화하여 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **기본 할인 프로모션 실시간 동기화 큐 적재 (`MKTFRT_T01` 트리거)**: 매장 제휴카드 기본 할인정보 마스터 테이블 (`MKTFRTTB`)에 신규 등록, 할인 규정 변경, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MKTFRT_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 카드명/프로모션명(`promotion_nm`), 유효기간(`valid_from_date` ~ `valid_to_date`), 할인율(`dc_rate`) 및 1회 한도액(`rist_dc_amt`) 정보를 실시간으로 `SKTFRTTB` 큐에 인서트합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 변경 이력이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈이 해당 데이터를 가공하여 개별 가맹점의 POS 단말기 메모리로 즉시 전송 및 다운로드 반영시킵니다.\n"
        "* **매출 제휴 할인 적합성 소급 검증**: 포스 매출 결제 시 고객이 적용받은 제휴 할인액(`card_dc_amt`)이 해당 거래 시점에 POS 단말기에 다운로드된 기본 할인/프로모션 정책 범위(1회 최대 한도액 `rist_dc_amt` 등) 내에서 계산되었는지 정합성을 사후 대조 검증하는 근거 데이터로 작동합니다."
    )

    data["tables"]["sktfrttb"] = {
        "memo": sktfrttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "ktf_cd": "제휴사/카드 구분 코드 (예: KTF 기본, KTF VIP 등)",
            "promotion_nm": "프로모션/카드 명칭",
            "valid_from_date": "프로모션 유효기간 시작 일자 (YYYYMMDD)",
            "valid_to_date": "프로모션 유효기간 종료 일자 (YYYYMMDD)",
            "good_proc_fg": "할인 적용 대상 구분 (0: 전체상품, 1: 일부특수품목제외)",
            "dc_rate": "제휴 기본 할인율 (%)",
            "rist_dc_amt": "1회 최대 할인 한도액 (0: 무제한)",
            "round_fg": "금액 절사 방식 구분 (0: 반올림, 1: 절사, 2: 올림)",
            "appr_fg": "제휴 승인 처리 여부 (0: 미승인, 1: 승인)",
            "appr_corp_cd": "제휴 승인 기관/회사 코드",
            "dc_amt": "고정 제휴 할인 금액 (정액 할인 시 적용)"
        },
        "memo_c": "매장 제휴카드 기본 할인 마스터(MKTFRTTB) 테이블의 변동 시 MKTFRT_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 제휴 할인 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 제휴 할인 데이터 배포 관리 모듈, 제휴사 카드 매출 일보/주보 조회 시 정산 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mktfrttb",
                "description": "매장 제휴카드 기본 할인 마스터 테이블. [트리거 MKTFRT_T01 연동] 백오피스 또는 본사에서 제휴사 카드 기본 할인 마스터를 등록/수정/삭제 처리하면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SKTFRTTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점 점포의 지역 코드 및 정상 사용 여부(use_yn)를 확인하여 해당 점포의 POS 기기로 제휴 할인 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 포스 매출 결제 시 적용된 통신사 제휴 할인액이 당일 시점의 할인 정책 범위(한도액 rist_dc_amt 등)대로 정교하게 산출되었는지 사후 대조 검증을 수행하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 제휴 할인 마스터의 변동 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 제휴사 제휴 할인율 한도 규정(예: 1회 최대 10%, 일일 최대 한도 등)의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 제휴사 구분 코드(ktf_cd - KTF 멤버십 등) 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 제휴 할인 상품 및 할인율을 등록/해제 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사에서 제휴사 할인 대상 품목의 기준 코드가 유효하게 존재하는 활성 자재인지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 제휴 할인 행사 품목의 매입 원장과 매출 대비 기여도 비율을 연계 정산 보고서로 분석할 때 비교용으로 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 제휴 할인 품목의 실시간 판매 추이와 남은 재고량을 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 제휴 할인 판매된 수량의 마진율을 평가하기 위해 상품 원가를 대조 조회하는 데 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 제휴 기본 할인 프로모션 대상이 특정 상품으로 제한된 경우, 해당 적용 대상 상품의 기본 속성을 매칭하기 위해 조인합니다."
            }
        ]
    }

    # 25. SMONTHTB MEMO AND RELATED TABLES
    smonthtb_memo = (
        "### 1. 테이블 개요\n"
        "월별 매장 매출 실적 테이블 (`SMONTHTB`).\n"
        "각 가맹점 점포별(`MS_NO`)로 월 단위(`SALE_MM`)로 마감된 총 매출액, 순매출액, 부가세, 결제 수단별 금액(현금, 신용카드, 제휴카드, 상품권, 포인트 등) 및 할인 형태별 누적 실적 통계를 정의하여 월간 손익 및 세무 평가의 기준을 제공하는 집계 실적 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **매출 헤더 등록 시 실시간 월별 실적 집계 (`STRNHD_T01` 트리거 및 `SUB_SMONTH_P` 프로시저)**: 포스(POS)에서 판매 마감 결제가 완료되어 매출 헤더(`STRNHDTB`)에 인서트될 때, `STRNHD_T01` 트리거가 실행되어 `SUB_SMONTH_P` 프로시저를 호출합니다. 프로시저 내부에서는 해당 월의 점포별 실적 행이 존재하면 판매 수량/금액, 현금/카드 승인액, 과세금액 등을 합산 업데이트(`UPDATE`)하고, 없는 경우 새 월별 실적 레코드를 생성(`INSERT`)합니다.\n"
        "* **매출 취소/망취소 소급 보정 (`SUB_SNETDT_P` 프로시저)**: 매출 취소나 전표 취소, 또는 통신 에러로 인한 망취소 발생 시, 해당 매출 월 실적 테이블의 수치 차감 및 보정 처리가 프로시저를 통해 자동으로 관리됩니다.\n"
        "* **메인 대시보드 및 통계 연동**: 백오피스 로그인 시 첫 화면인 본사/매장 메인 대시보드의 '월간 매출 추이 그래프' 및 '전월 대비 실적 증감' 통계 정보를 실시간으로 계산 출력하는 핵심 소스 원장입니다."
    )

    data["tables"]["smonthtb"] = {
        "memo": smonthtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "sale_mm": "매출 영업 년월 (YYYYMM)",
            "chain_no": "체인 본부 식별번호",
            "chain_area": "체인 지역 분류 코드",
            "sale_tot": "월간 매출 총액 (실매출액 + 할인합계액)",
            "sale_amt": "월간 실 매출액 (할인 제외 순수 매출액)",
            "dc_amt": "월간 적용 총 할인 금액 합계",
            "cash_amt": "월간 현금 결제 누적 금액",
            "card_amt": "월간 신용카드 결제 누적 금액",
            "etc_amt": "월간 기타 수단 결제 누적 금액",
            "bill_cnt": "월간 총 거래 건수 (영수증 발행 수)",
            "cash_cnt": "월간 현금 결제 거래 건수",
            "card_cnt": "월간 신용카드 결제 거래 건수",
            "etc_cnt": "월간 기타 결제 거래 건수",
            "cancel_cnt": "월간 매출 취소/반품 거래 건수",
            "cancel_tot": "월간 매출 취소/반품 총액",
            "c_cash_amt": "월간 현금 결제 취소 누적 금액",
            "c_card_amt": "월간 신용카드 결제 취소 누적 금액",
            "c_etc_amt": "월간 기타 결제 취소 누적 금액",
            "avg_amt": "월간 거래 건당 평균 매출액 (객단가)",
            "vat_amt": "월간 매출 부가세 누적액",
            "gift_amt": "월간 상품권 수납 누적 금액",
            "point_amt": "월간 멤버십 포인트 결제 누적 금액",
            "norm_dc_amt": "월간 일반/행사 할인 누적액",
            "service_dc_amt": "월간 서비스/프로모션 할인 누적액",
            "card_dc_amt": "월간 신용카드사 청구 할인 누적액",
            "coupon_dc_amt": "월간 쿠폰 할인 누적액",
            "cust_dc_amt": "월간 고객 멤버십 포인트 할인 누적액",
            "c_gift_amt": "월간 상품권 수납 취소 누적 금액",
            "c_point_amt": "월간 포인트 결제 취소 누적 금액",
            "native_cnt": "월간 내국인 고객 방문 건수",
            "foreign_cnt": "월간 외국인 고객 방문 건수",
            "tip_amt": "월간 봉사료 수납 누적 금액",
            "cash_re_amt": "월간 현금 반품/환불 누적 금액",
            "gift_re_amt": "월간 상품권 반품/환불 누적 금액",
            "weas_amt": "월간 외상 결제 누적 금액",
            "crediphone_amt": "월간 모바일 소액결제 누적 금액",
            "room_amt": "월간 룸/객실 차치 정산 누적 금액",
            "paid_card_amt": "월간 선불/기프트카드 결제 누적 금액",
            "net_amt": "월간 순매출 총액 (NET 금액)",
            "okcash_amt": "월간 OK캐쉬백 포인트 적립/사용 누적 금액",
            "gift_cnt": "월간 상품권 결제 건수",
            "point_cnt": "월간 포인트 결제 건수",
            "weas_cnt": "월간 외상 결제 건수",
            "paid_card_cnt": "월간 선불카드 결제 건수",
            "okcash_cnt": "월간 OK캐쉬백 적립/사용 건수",
            "gift_re_cnt": "월간 상품권 환불 건수",
            "cash_re_cnt": "월간 현금 환불 건수",
            "eco_amt": "월간 에코머니 포인트 수납 누적 금액",
            "eco_cnt": "월간 에코머니 결제 건수",
            "daum_myone_amt": "월간 다음 마이원 결제 누적액",
            "mtic_amt": "월간 엠틱 모바일 결제 누적액",
            "yawoori_amt": "월간 야우리 포인트 사용 누적액",
            "yawoori_cnt": "월간 야우리 결제 건수",
            "reward_amt": "월간 리워드 포인트 수납 누적액",
            "reward_cnt": "월간 리워드 결제 건수",
            "mobile_coupon_amt": "월간 모바일 쿠폰 수납 누적액",
            "mobile_coupon_cnt": "월간 모바일 쿠폰 결제 건수",
            "meme_point_amt": "월간 미미박스 포인트 수납 누적액",
            "meme_point_cnt": "월간 미미박스 결제 건수",
            "tax_free_amt": "월간 사후면세(Tax Free) 환급 누적액",
            "tax_free_cnt": "월간 사후면세 환급 처리 건수",
            "fun_mobile_amt": "월간 모바일 펀 쿠폰 누적액",
            "fun_mobile_cnt": "월간 모바일 펀 결제 건수",
            "support_amt": "월간 판촉 지원금 정산 누적액",
            "support_cnt": "월간 판촉 지원금 처리 건수",
            "invoice_amt": "월간 세금계산서 발행 누적 금액",
            "invoice_cnt": "월간 세금계산서 발행 건수",
            "dept_amt": "월간 부서별 외상/정산 누적액",
            "dept_cnt": "월간 부서 정산 건수",
            "blue_use_amt": "월간 블루멤버스 포인트 사용 누적액",
            "blue_use_amt_cnt": "월간 블루멤버스 결제 건수",
            "cash_dc_remant": "월간 현금 영수증 끝전 할인 누적액",
            "emp_dc_amt": "월간 사내 임직원 사원카드 할인 누적액",
            "play_amt": "월간 게임/오락기 결제 누적액",
            "play_cnt": "월간 게임기 결제 건수",
            "petty_amt": "월간 소액 현금 시금/정산 누적액",
            "petty_cnt": "월간 소액 정산 건수",
            "dept_dc_amt": "월간 부서 할인 적용 누적액",
            "coupon_amt": "월간 정액 쿠폰 사용 누적액",
            "coupon_cnt": "월간 쿠폰 결제 건수",
            "giftcard_amt": "월간 선불 기프트카드 매출 누적액",
            "giftcard_cnt": "월간 기프트카드 결제 건수",
            "mem_giftcard_amt": "월간 충전식 카드 사용 누적액",
            "mem_giftcard_cnt": "월간 충전식 카드 결제 건수"
        },
        "memo_c": "포스 매출 전송 시 매출 헤더 트리거(STRNHD_T01)와 SUB_SMONTH_P 프로시저에 의해 월 단위로 자동 누적 생성됩니다.",
        "memo_u": "매출 취소/망취소 발생 시 SUB_SNETDT_P 프로시저에 의해 실시간 차감 반영됩니다.",
        "memo_d": "가맹점별 세무 정산 및 이익 평가의 원장 자료이므로 시스템 상에서의 물리 삭제가 전면 방지됩니다.",
        "memo_r": "본사/매장 메인 대시보드 매출 그래프 및 년/월/일 판매&결제현황 보고서 조회 시 월간 실적 원장으로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. [트리거 STRNHD_T01 연동] 포스(POS)에서 판매 마감 결제가 완료될 때, 일별 집계뿐만 아니라 월별 매장 실적 테이블(SMONTHTB)로 총액, 과세액, 결제수단별 금액, 할인 형태별 정보가 누적 합산 업데이트됩니다."
            },
            {
                "table_name": "sdailytb",
                "description": "일별 매장 매출 실적 테이블. [트리거 STRNHD_T01 연동] 매출 헤더 트리거 가동 시 동일한 원천에서 일별 실적(SDAILYTB)과 월별 실적(SMONTHTB)이 병렬로 분기 집계 처리됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점의 브랜드 정보, 계약 분류, 사업자 번호 등을 매핑하여 법인별/체인별 월간 총매출 현황 및 수수료 정산 보고서를 추출할 때 연계 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 월별 상품 원가와 매출 총 이익률을 월말에 일괄 평가할 때, 월별 매출 총액(sale_tot) 및 실매출액(sale_amt) 대비 원가 비율(원가율)을 대조 평가하는 정산 관계입니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 매월 말일 재고 실사 마감 시 월간 매출 잔량 분석 및 불일치 감모 재고를 정산하기 위해 연계 대조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 결제 수단 구분, 결제 할인 구분 등의 통계용 명칭 라벨을 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "obslphtb",
                "description": "매입/발주 헤더 테이블. 매장별 월간 총매입액과 월간 총매출액을 비교하여 월별 매입 대비 매출 마진 추세를 분석할 때 조인 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 월별 매출 정산 및 카드 수수료율 정산에 필요한 세무 기준 및 수수료 가중치를 매치하기 위해 참조됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 월별 마감 매출 실적을 강제로 수동 보정하거나 이의 제기를 검토할 때, 마감 작업을 처리한 시스템 담당 사용자의 감사 추적을 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 월간 카테고리별 실적 분배 정산 시 본사 자재분류를 연계하기 위해 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 월별 매입 자재 단가 흐름과 월별 매출 변동량 추이를 월간 보고서로 매핑 조회하기 위해 간접 조인됩니다."
            }
        ]
    }

    # 26. STIMETB MEMO AND RELATED TABLES
    smtimetb_memo = (
        "### 1. 테이블 개요\n"
        "시간대별 매장 매출 실적 테이블 (`SMTIMETB`).\n"
        "각 가맹점 점포별(`MS_NO`)로 일자별(`SALE_DATE`) 24시간대(00시~23시)의 시간대별 실매출액, 영수증 발행 건수, 내/외국인 고객 수 실적 통계를 관리하여 매장의 피크 타임 분석 및 주중 시간대별 영업 밀도 평가의 기준을 제공하는 집계 실적 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **매출 발생 시 실시간 시간대별 실적 집계 (`STRNHD_T01` 트리거 및 `SUB_SMTIME_P` 프로시저)**: 포스(POS)에서 판매 마감 결제가 완료되어 매출 헤더(`STRNHDTB`)에 인서트될 때, `STRNHD_T01` 트리거가 실행되어 `SUB_SMTIME_P` 프로시저를 호출합니다. 프로시저 내부에서는 해당 영업일자의 점포별 실적 행이 존재하면 매출 결제 시각(시 정보)을 감지하여 해당하는 시간대의 매출액(`SALE_AMT_XX`) 및 건수(`BILL_CNT_XX`) 등을 합산 업데이트(`UPDATE`)하고, 없는 경우 새 일자별 실적 행을 생성(`INSERT`)합니다.\n"
        "* **시간대별 영업 추이 분석**: 백오피스 분석 시스템 내의 시간대별 현황 화면 및 매출 일보 화면에서 시간대별 피크 매출 분포를 시각화 및 차트화하여 출력하기 위한 핵심 소스로 활용됩니다."
    )

    data["tables"]["smtimetb"] = {
        "memo": smtimetb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "sale_date": "매출 영업 일자 (YYYYMMDD)",
            "chain_no": "체인 본부 식별번호",
            "chain_area": "체인 지역 분류 코드",
            "sale_amt_tot": "당일 누적 총 매출액 합계",
            "bill_cnt_tot": "당일 누적 총 거래 건수 합계",
            "sale_amt_00": "00시~01시 실매출액",
            "bill_cnt_00": "00시~01시 거래 건수",
            "native_cnt_00": "00시~01시 내국인 객수",
            "foreign_cnt_00": "00시~01시 외국인 객수",
            "sale_amt_01": "01시~02시 실매출액",
            "bill_cnt_01": "01시~02시 거래 건수",
            "native_cnt_01": "01시~02시 내국인 객수",
            "foreign_cnt_01": "01시~02시 외국인 객수",
            "sale_amt_02": "02시~03시 실매출액",
            "bill_cnt_02": "02시~03시 거래 건수",
            "native_cnt_02": "02시~03시 내국인 객수",
            "foreign_cnt_02": "02시~03시 외국인 객수",
            "sale_amt_03": "03시~04시 실매출액",
            "bill_cnt_03": "03시~04시 거래 건수",
            "native_cnt_03": "03시~04시 내국인 객수",
            "foreign_cnt_03": "03시~04시 외국인 객수",
            "sale_amt_04": "04시~05시 실매출액",
            "bill_cnt_04": "04시~05시 거래 건수",
            "native_cnt_04": "04시~05시 내국인 객수",
            "foreign_cnt_04": "04시~05시 외국인 객수",
            "sale_amt_05": "05시~06시 실매출액",
            "bill_cnt_05": "05시~06시 거래 건수",
            "native_cnt_05": "05시~06시 내국인 객수",
            "foreign_cnt_05": "05시~06시 외국인 객수",
            "sale_amt_06": "06시~07시 실매출액",
            "bill_cnt_06": "06시~07시 거래 건수",
            "native_cnt_06": "06시~07시 내국인 객수",
            "foreign_cnt_06": "06시~07시 외국인 객수",
            "sale_amt_07": "07시~08시 실매출액",
            "bill_cnt_07": "07시~08시 거래 건수",
            "native_cnt_07": "07시~08시 내국인 객수",
            "foreign_cnt_07": "07시~08시 외국인 객수",
            "sale_amt_08": "08시~09시 실매출액",
            "bill_cnt_08": "08시~09시 거래 건수",
            "native_cnt_08": "08시~09시 내국인 객수",
            "foreign_cnt_08": "08시~09시 외국인 객수",
            "sale_amt_09": "09시~10시 실매출액",
            "bill_cnt_09": "09시~10시 거래 건수",
            "native_cnt_09": "09시~10시 내국인 객수",
            "foreign_cnt_09": "09시~10시 외국인 객수",
            "sale_amt_10": "10시~11시 실매출액",
            "bill_cnt_10": "10시~11시 거래 건수",
            "native_cnt_10": "10시~11시 내국인 객수",
            "foreign_cnt_10": "10시~11시 외국인 객수",
            "sale_amt_11": "11시~12시 실매출액",
            "bill_cnt_11": "11시~12시 거래 건수",
            "native_cnt_11": "11시~12시 내국인 객수",
            "foreign_cnt_11": "11시~12시 외국인 객수",
            "sale_amt_12": "12시~13시 실매출액",
            "bill_cnt_12": "12시~13시 거래 건수",
            "native_cnt_12": "12시~13시 내국인 객수",
            "foreign_cnt_12": "12시~13시 외국인 객수",
            "sale_amt_13": "13시~14시 실매출액",
            "bill_cnt_13": "13시~14시 거래 건수",
            "native_cnt_13": "13시~14시 내국인 객수",
            "foreign_cnt_13": "13시~14시 외국인 객수",
            "sale_amt_14": "14시~15시 실매출액",
            "bill_cnt_14": "14시~15시 거래 건수",
            "native_cnt_14": "14시~15시 내국인 객수",
            "foreign_cnt_14": "14시~15시 외국인 객수",
            "sale_amt_15": "15시~16시 실매출액",
            "bill_cnt_15": "15시~16시 거래 건수",
            "native_cnt_15": "15시~16시 내국인 객수",
            "foreign_cnt_15": "15시~16시 외국인 객수",
            "sale_amt_16": "16시~17시 실매출액",
            "bill_cnt_16": "16시~17시 거래 건수",
            "native_cnt_16": "16시~17시 내국인 객수",
            "foreign_cnt_16": "16시~17시 외국인 객수",
            "sale_amt_17": "17시~18시 실매출액",
            "bill_cnt_17": "17시~18시 거래 건수",
            "native_cnt_17": "17시~18시 내국인 객수",
            "foreign_cnt_17": "17시~18시 외국인 객수",
            "sale_amt_18": "18시~19시 실매출액",
            "bill_cnt_18": "18시~19시 거래 건수",
            "native_cnt_18": "18시~19시 내국인 객수",
            "foreign_cnt_18": "18시~19시 외국인 객수",
            "sale_amt_19": "19시~20시 실매출액",
            "bill_cnt_19": "19시~20시 거래 건수",
            "native_cnt_19": "19시~20시 내국인 객수",
            "foreign_cnt_19": "19시~20시 외국인 객수",
            "sale_amt_20": "20시~21시 실매출액",
            "bill_cnt_20": "20시~21시 거래 건수",
            "native_cnt_20": "20시~21시 내국인 객수",
            "foreign_cnt_20": "20시~21시 외국인 객수",
            "sale_amt_21": "21시~22시 실매출액",
            "bill_cnt_21": "21시~22시 거래 건수",
            "native_cnt_21": "21시~22시 내국인 객수",
            "foreign_cnt_21": "21시~22시 외국인 객수",
            "sale_amt_22": "22시~23시 실매출액",
            "bill_cnt_22": "22시~23시 거래 건수",
            "native_cnt_22": "22시~23시 내국인 객수",
            "foreign_cnt_22": "22시~23시 외국인 객수",
            "sale_amt_23": "23시~00시 실매출액",
            "bill_cnt_23": "23시~00시 거래 건수",
            "native_cnt_23": "23시~00시 내국인 객수",
            "foreign_cnt_23": "23시~00시 외국인 객수"
        },
        "memo_c": "포스 매출 전송 시 매출 헤더 트리거(STRNHD_T01)와 SUB_SMTIME_P 프로시저에 의해 매일 자동 누적 생성됩니다.",
        "memo_u": "취소 및 반품 매출 발생 시 해당 시간대의 수치가 차감 업데이트됩니다.",
        "memo_d": "점포별 일일 시간대별 혼잡도 및 매출 집중도 감사 증빙이므로 물리 삭제가 전면 방지됩니다.",
        "memo_r": "시간대별 매출 현황, 마트 매출 일보/주보 출력 시 피크타임 매출 롤업 분석 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. [트리거 STRNHD_T01 연동] 포스(POS)에서 판매 거래가 확정 등록될 때, 매출 결제 시각의 시 정보를 기준으로 해당 시간대(00~23시)의 실매출액, 객수, 영수증 건수를 누적하여 시간대별 매출 테이블(SMTIMETB)로 합산 업데이트합니다."
            },
            {
                "table_name": "sdailytb",
                "description": "일별 매장 매출 실적 테이블. [트리거 STRNHD_T01 연동] 일별 마감 실적이 롤업될 때, 일별 실적(SDAILYTB)의 일 합계 매출 수치와 시간대별 실적(SMTIMETB)의 시간대 총합 금액이 일치하도록 함께 집계 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 시간대별 분석 시 매장의 지역적 위치, 면적 분류, 가맹점 계약 방식을 연계하여 지역별별 피크 타임 매출 밀도 분석 보고서를 추출하기 위해 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 시간대에 주로 판매된 식음료 메뉴군이나 패션 상품 카테고리를 추적하여 시간대별 맞춤형 터치키 메뉴판 배포를 제어하기 위해 사용됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 시간대(00~23시)의 한글 시간 라벨 표시 및 가맹 지역 명칭을 출력하기 위해 조인 사용됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 시간대별 매출 정산 분석 시 야간 할증 영업 시간 기준이나 부가세 정산 정책 매개변수 확인용으로 참조됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 야간/심야 등 특정 시간대의 매출 취소 및 정산 수동 보정을 감행한 백오피스 운영 사용자의 계정을 감사 추적하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "obslphtb",
                "description": "매입/발주 헤더 테이블. 일별 시간대별 매출 피크 타임 분석 자료와 매입 거래처의 배송 입고 시각을 비교하여 적정 물류 배송 타임라인을 구성하는 의사결정 자료로 간접 연계 참조됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 시간대별 매출 통계에서 완제품 분류 체계를 매핑하기 위해 간접 참조합니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매출 상세 거래에 매핑된 구체적인 개별 단품 판매 시각의 타당성을 시간대별 실적 원장과 비교 검증하기 위해 간접 조인합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 물류 입고 상세량과 시간대별 판매 회전율을 비교 평가할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 피크 시간대 판매 속도에 따른 실시간 안전재고 소진 위험도를 예측하는 재고 경보 시스템과 연동 참조됩니다."
            }
        ]
    }

    # 27. SORDIDTB MEMO AND RELATED TABLES
    sordidtb_memo = (
        "### 1. 테이블 개요\n"
        "주문원(근무자)별 상품 판매 실적 테이블 (`SORDIDTB`).\n"
        "각 가맹점 점포별(`MS_NO`)로 일자별(`SALE_DATE`)로 개별 상품(`GOODS_CD`)을 등록/판매한 포스 근무 사원(`ORDER_EMPID`)의 판매 수량, 총 판매액, 부가세, 실매출액 및 취소 건수/취소 금액 누적 통계를 제공하여 근무자별 매출 기여도 및 인센티브 정산의 기준으로 삼는 실적 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **매출 등록 시 실시간 근무자별 실적 집계 (`STRNDT_T01` 트리거 및 `SUB_SORDID_P` 프로시저)**: 포스(POS)에서 판매 상세 결제 데이터(`STRNDTTB`)가 수신될 때, `STRNDT_T01` 트리거가 작동하여 `SUB_SORDID_P` 프로시저를 호출합니다. 프로시저 내부에서는 해당 일자의 근무자별/상품별 실적 레코드가 존재하면 판매 수량(`SALE_QTY`) 및 실매출액, 취소 금액 등을 합산 업데이트(`UPDATE`)하고, 없는 경우 새 실적 행을 생성(`INSERT`)합니다.\n"
        "* **근무자 기여도 및 성과 분석**: 백오피스 상품 분석 내의 주문원별 상품 판매현황 화면에서 각 직원의 영업 성과 및 기간 단위 인센티브 배분을 정량적으로 평가하기 위한 원천 데이터로 사용됩니다."
    )

    data["tables"]["sordidtb"] = {
        "memo": sordidtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "sale_date": "매출 영업 일자 (YYYYMMDD)",
            "goods_cd": "상품코드 (자재 코드)",
            "lclass_cd": "대분류 코드",
            "mclass_cd": "중분류 코드",
            "sclass_cd": "소분류 코드",
            "order_empid": "주문 접수 사원/근무자 ID",
            "chain_no": "체인 본부 식별번호",
            "uprice": "판매 단품 단가 (판매가)",
            "sale_qty": "근무자가 판매한 누적 수량",
            "sale_tot": "근무자가 판매한 총 판매액 (실매출액 + 할인액)",
            "sale_amt": "근무자 기여 실 매출액 (할인 차감 순수액)",
            "dc_amt": "근무자가 적용한 총 할인 금액",
            "vat_amt": "판매 상품에 대한 부가세액",
            "cancel_qty": "근무자가 취소/반품 처리한 누적 수량",
            "cancel_amt": "근무자가 취소/반품 처리한 누적 실매출액",
            "create_dtime": "최초 등록 일시 (YYYYMMDDHH24MISS)",
            "last_dtime": "최종 수정 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "포스 매출 전송 시 매출 상세 트리거(STRNDT_T01)와 SUB_SORDID_P 프로시저에 의해 실시간 자동 생성/누적됩니다.",
        "memo_u": "동일 일자에 동일 주문원이 동일 상품을 추가 판매하거나 거래 취소/반품 등록 시 누적 가감 업데이트됩니다.",
        "memo_d": "근무자(주문원)별 정산 및 인센티브 지급 증빙이므로 물리적인 행 삭제가 방지됩니다.",
        "memo_r": "본사/매장의 주문원별 상품 판매현황 화면 조회 및 인사/급여 연계 인센티브 평가 시 원장으로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strndttb",
                "description": "포스 매출 상세 테이블. [트리거 STRNDT_T01 연동] 포스(POS)에서 판매 상품 결제 등록 시 해당 거래의 판매 수량, 금액, 부가세, 할인액이 주문을 직접 접수한 근무자 사원 코드(order_empid)와 연동되어 근무자별 실적 테이블(SORDIDTB)로 이관/누적 업데이트됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 근무자(주문원)별 매출 기여도 및 인센티브 정산 보고서를 추출할 때, 사원 코드(order_empid)에 대응하는 한글 성명 및 소속 부서 직급 정보를 조회하기 위해 조인 결합됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 주문원이 판매한 개별 상품의 명칭, 분류(대/중/소), 표준 판매가 및 상품 속성을 보고서에 출력하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점이나 특정 지역 체인군 전체의 근무자별 매출 랭킹 및 인센티브 분배 보고서를 출력할 때 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 상품 대/중/소분류의 한글 정식 라벨 및 사용자 직책 구분을 한글로 변환하기 위해 조인 결합됩니다."
            },
            {
                "table_name": "sdailytb",
                "description": "일별 매장 매출 실적 테이블. 점포의 당일 총 실적과 각 근무자별로 분배된 실적의 합계 정합성을 감사 검증하기 위해 조인 비교됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 근무자별 판매 인센티브 산정 시 공제할 할인액이나 부가세 처리의 계산 기준 규칙을 조회하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 주문 근무자가 판매한 바코드 및 품목 규격을 대조 조회하기 위해 간접 조인 참조합니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 특정 영수증 전표 거래를 최초 주문 접수한 사원과 최종 결제를 완료한 포스 캐셔의 기여도를 대조 분석할 때 조인 연동됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 근무자가 판매에 기여한 상품들의 평균 매입 단가를 매칭하여 순마진(GP) 기여도를 개별 평가할 때 연계됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 근무자가 담당 구역의 상품 판매를 등록할 때 재고 소진율과의 연관 관계를 분석하기 위해 연동 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 근무자별 실적의 매출원가(COGS)를 추적하여 직원에 따른 순이익률 성과 보고서를 도출할 때 간접 조인 연계됩니다."
            }
        ]
    }

    # 28. SPOSFTTB MEMO AND RELATED TABLES
    sposfttb_memo = (
        "### 1. 테이블 개요\n"
        "POS 기능 제어 키 테이블 (`SPOSFTTB`).\n"
        "가맹점별(`MS_NO`) 개별 POS 단말기(`POS_NO`)의 특수 기능(반품 차단, 영수증 재발행 통제, 수동 가격 개정 등)에 대한 동작 제어 및 사용 권한 정보를 실시간으로 다운로드 전송하기 위해 변경 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **기능 제어 키 실시간 동기화 큐 적재 (`MPOSFT_T01` 트리거)**: 매장 POS 기능 제어 마스터 테이블(`MPOSFTTB`)에 신규 기능 통제 규칙이 등록, 권한 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)될 때, `MPOSFT_T01` 트리거가 가동되어 변경 로그 일련번호(`log_seq`), 처리구분(`proc_fg`), 제어할 기능 코드(`function_cd`), 사용 여부(`use_fg`) 정보를 실시간으로 `SPOSFTTB` 큐에 인서트하고, 동시에 변경 감사 로그(`MMSLOGTB`)에도 상세 내역을 적재합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 권한 변경 이력이 등록되면, 대기 중이던 POS 연동 송수신 모듈(Telex M45/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 권한 데이터를 개별 매장의 해당 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 거래 감사 정합성 대조**: 단말기에서 반품이나 예외 거래가 발생했을 때, 당일 시점에 배포된 기능 제어 통제 규정을 통과했는지 사후 감사 검증을 수행할 때 참고하는 근거 이력으로 쓰입니다."
    )

    data["tables"]["sposfttb"] = {
        "memo": sposfttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "pos_no": "매장 소속 POS 단말기 번호",
            "function_cd": "POS 제어 대상 기능 코드 (예: 반품 통제, 가격 강제 개정 등)",
            "use_fg": "기능 사용 제한 여부 (0: 제한/불가, 1: 허용/사용)"
        },
        "memo_c": "매장 POS 기능 제어 마스터(MPOSFTTB) 테이블의 변동 시 MPOSFT_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 제휴 할인 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 제휴 할인 데이터 배포 관리 모듈, 제휴사 카드 매출 일보/주보 조회 시 정산 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mposfttb",
                "description": "매장 POS 기능 제어 마스터 테이블. [트리거 MPOSFT_T01 연동] 본사 또는 점포 관리 화면에서 특정 포스 번호의 기능 사용 여부를 변경하면, 트리거가 작동하여 변경 내역을 전송용 대기 큐인 SPOSFTTB로 실시간 인서트합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점의 영업 상태 및 점포 코드를 검증하여 정상 가동 중인 가맹점의 포스 기기에만 기능 제어 키 데이터를 전파하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MPOSFT_T01 연동] 포스 기능 키 제어 변동 시점의 상세 이전/이후 변경 감사 로그를 적재하고, 전송 데몬의 전송 완료 상태를 추적하기 위해 연계됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. POS 특수 제어 기능 코드(function_cd - 예: 0001: 반품차단, 0002: 영수증재발행 금지 등) 및 처리 구분(proc_fg)에 대응하는 정식 한글 명칭 라벨을 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매장 POS 기기에서 각 기능 키별로 지정할 수 있는 보안 등급 설정(예: 점장 승인 필요 여부 등)의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 포스의 기능 제어를 추가/수정하여 권한을 조정한 담당 사용자의 계정 실명 정보를 감사 추적하기 위해 조인됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. POS 단말기에서 반품이나 매출 취소 거래가 발생했을 때, 해당 시점에 SPOSFTTB 큐를 통해 배포된 기능 제어 규정을 준수하여 거래가 승인되었는지 거래 무결성 사후 대조를 위해 간접 연계 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. POS 기능 중 상품 할인 제한 정책이나 특정 주류/유통 상품 구매 제한 기능 제어와 연계하여 자재 코드를 조회할 때 간접 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 발주 및 매입 등록 시 모바일 포스(Tablet POS 등) 기능 제어 정책과 연동하여 사용 가능한 메뉴 버튼을 제어하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 실시간 재고 조회 기능 키 사용 권한이 부여된 단말기인지 검증하는 권한 로직에 간접 연동 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 원가 및 마진율 노출 방지를 위해 점포 POS 화면의 특정 정산 현황 기능 키 노출 권한을 필터링할 때 간접 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. POS 단말기의 임의 단가 수정 기능이나 특별 할인 기능 허용 시 상품 마스터의 단가 수정 가능 여부(uprice_change_yn)와 상호 연동하여 유효성을 검증하기 위해 조인됩니다."
            }
        ]
    }

    # 29. SPROGDTB MEMO AND RELATED TABLES
    sprogdtb_memo = (
        "### 1. 테이블 개요\n"
        "POS 프로모션 대상 상품 설정 테이블 (`SPROGDTB`).\n"
        "가맹점별(`MS_NO`) 프로모션 행사(년도별/코드별)에 참여 또는 제한할 개별 행사 대상 상품 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **프로모션 상품 변동 시 실시간 동기화 큐 적재 (`MPROGD_T01` 트리거)**: 매장 프로모션 대상 상품 설정 마스터 테이블 (`MPROGDTB`)에 신규 행사 품목이 지정(INSERT)되거나 삭제(DELETE)될 때, `MPROGD_T01` 트리거가 감지하여 변경 일련번호(`log_seq`), 처리구분(`proc_fg` - A/D), 해당 프로모션 키 및 할인율(`gen_dc`), 할인 금액(`gen_amt`) 정보를 실시간으로 `SPROGDTB` 큐에 인서트합니다. (참고: 프로모션 대상 상품의 중간 수정은 허용되지 않으므로 UPDATE 시 사용자 예외 처리가 발생합니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 프로모션 자재 매핑 정보가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M92/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 행사 상품 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **매출 프로모션 할인 적합성 소급 검증**: 포스 매출 결제 시 고객이 적용받은 행사 할인액이 당일 시점의 프로모션 할인 규칙(정액/정율) 범위 내에서 정확하게 산정되었는지 정합성을 사후 대조 검증하는 근거 데이터로 작동합니다."
    )

    data["tables"]["sprogdtb"] = {
        "memo": sprogdtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, D: 삭제)",
            "promotion_year": "프로모션 해당 연도 (YYYY)",
            "promotion_cd": "프로모션 행사 식별 코드",
            "goods_cd": "상품코드 (자재 코드)",
            "gen_dc_fg": "일반 행사 할인 종류 구분 (0: 정율 할인, 1: 정액 할인)",
            "gen_amt": "정액 프로모션 할인 금액",
            "gen_dc": "정율 프로모션 할인율 (%)",
            "goods_add_fg": "행사 상품 추가 속성 구분 (0: 기본, 1: 추가 증정/특별 품목)"
        },
        "memo_c": "매장 프로모션 대상 상품 마스터(MPROGDTB) 테이블의 변동 시 MPROGD_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다. (다만 비즈니스 로직 상 마스터 자체의 수정은 불가하며 삭제 후 재등록만 지원합니다.)",
        "memo_d": "가맹점별 실시간 매출 제휴 할인 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 프로모션 상품 데이터 배포 관리 모듈, 프로모션 판매 현황 보고서 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mprogdtb",
                "description": "매장 프로모션 대상 상품 설정 마스터 테이블. [트리거 MPROGD_T01 연동] 백오피스에서 프로모션별 행사 상품을 등록/삭제 처리하면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SPROGDTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 지역 분류 및 정상 사용 여부(use_yn)를 확인하여 해당 점포의 POS 기기로 프로모션 상품 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 프로모션이 적용되는 개별 자재/상품의 한글 명칭, 대/중/소분류, 정상 판매단가를 매칭하여 프로모션 할인가 산출 시 기준 판매가를 대조하기 위해 조인합니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 프로모션(행사) 할인을 적용한 경우, 매출 전표에 기록된 행사 할인액이 당일 시점의 프로모션 정책(할인액, 할인율) 범위대로 정확히 계산되었는지 사후 정합성 대조를 위해 간접 연계 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 프로모션 대상 상품 마스터의 변동 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 전송 에러가 발생한 연동 인터페이스 진행 과정을 추적 보관하는 로그 테이블입니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 프로모션 적용 우선순위 및 영수증 끝전 할인 규정의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 프로모션 행사 구분 코드 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 프로모션 행사 상품을 등록/제외 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사에서 행사 대상 품목의 기준 코드가 유효하게 존재하는 활성 자재인지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 프로모션 행사 품목의 매입 원장과 매출 대비 기여도 비율을 연계 정산 보고서로 분석할 때 비교용으로 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 프로모션 행사 품목의 실시간 판매 추이와 남은 재고량을 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 프로모션 할인 판매된 수량의 마진율을 평가하기 위해 상품 원가를 대조 조회하는 데 조인 연계됩니다."
            }
        ]
    }

    # 30. SPROSGTB MEMO AND RELATED TABLES
    sprosgtb_memo = (
        "### 1. 테이블 개요\n"
        "POS 프로모션 대상 제외 상품 설정 테이블 (`SPROSGTB`).\n"
        "가맹점별(`MS_NO`) 프로모션 행사(년도별/코드별)에 참여할 때 혜택 및 할인 대상에서 명시적으로 제외할 특수 비대상 상품(예: 담배, 쓰레기봉투 등 할인 예외 품목) 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **프로모션 제외 상품 변동 시 실시간 동기화 큐 적재 (`MPROSG_T01` 트리거)**: 매장 프로모션 대상 제외 상품 설정 마스터 테이블 (`MPROSGTB`)에 신규 제외 품목이 지정(INSERT)되거나 삭제(DELETE)될 때, `MPROSG_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg` - A/D), 해당 프로모션 키 및 제외할 상품코드(`goods_cd`) 정보를 실시간으로 `SPROSGTB` 큐에 인서트합니다. (참고: 프로모션 제외 상품 마스터도 수정은 불가하며 삭제 후 재등록만 허용됩니다.)\n"
        "* **본사 설정의 가맹점 전파 흐름**: 본사 마스터 설정(`TPROSGTB`)이 본사 화면(`hq_master_00019`)에 의해 변동될 때 `TPROSG_T01` 트리거가 작동하여 산하 매장 전체의 `MPROSGTB`로 데이터를 일괄 가공 복사하고, 이로 인해 `MPROSG_T01` 트리거가 최종적으로 이 `SPROSGTB` 전송 큐에 대기열을 생성합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 프로모션 제외 자재 매핑 정보가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M29/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 제외 상품 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다."
    )

    data["tables"]["sprosgtb"] = {
        "memo": sprosgtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, D: 삭제)",
            "promotion_year": "프로모션 해당 연도 (YYYY)",
            "promotion_cd": "프로모션 행사 식별 코드",
            "goods_cd": "프로모션 혜택 대상에서 제외할 상품코드"
        },
        "memo_c": "매장 프로모션 대상 제외 상품 마스터(MPROSGTB) 테이블의 변동 시 MPROSG_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다. (다만 비즈니스 로직 상 마스터 자체의 수정은 불가하며 삭제 후 재등록만 지원합니다.)",
        "memo_d": "가맹점별 실시간 매출 제휴 할인 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 프로모션 제외 상품 데이터 배포 관리 모듈, 프로모션 판매 현황 보고서 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mprosgtb",
                "description": "매장 프로모션 대상 제외 상품 설정 마스터 테이블. [트리거 MPROSG_T01 연동] 백오피스 또는 본사 마스터 변경에 의해 매장별 프로모션 제외 상품을 등록/삭제 처리하면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SPROSGTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 지역 분류 및 정상 사용 여부(use_yn)를 확인하여 해당 점포의 POS 기기로 프로모션 제외 상품 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 프로모션 혜택 대상에서 제외되는 개별 자재/상품의 한글 명칭, 대/중/소분류, 정상 판매단가를 매칭하여 POS 결제 시 행사 비대상 품목임을 시각화 표시하기 위해 조인합니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 프로모션(행사) 할인을 적용할 경우, 특정 영수증에 포함된 상품 중 제외 상품이 존재함에도 잘못 할인이 적용되었는지 사후 정합성 대조를 위해 간접 연계 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 프로모션 제외 상품 마스터의 변동 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 전송 에러가 발생한 연동 인터페이스 진행 과정을 추적 보관하는 로그 테이블입니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 프로모션 적용 및 제외 품목의 세무상 과세 구분 및 계산 규칙의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 프로모션 행사 구분 코드 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 프로모션 제외 상품을 등록/제외 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사에서 행사 제외 대상 품목의 기준 코드가 유효하게 존재하는 활성 자재인지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 프로모션 제외 품목의 매입 원장과 매출 대비 기여도 비율을 연계 정산 보고서로 분석할 때 비교용으로 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 프로모션 제외 품목의 실시간 판매 추이와 남은 재고량을 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 프로모션 제외 품목의 마진율을 평가하기 위해 상품 원가를 대조 조회하는 데 조인 연계됩니다."
            }
        ]
    }

    # 31. SRVLOGTB MEMO AND RELATED TABLES
    srvlogtb_memo = (
        "### 1. 테이블 개요\n"
        "백오피스 서비스/화면 호출 및 실행 로그 테이블 (`SRVLOGTB`).\n"
        "백오피스 웹 애플리케이션 프레임워크 상에서 모든 사용자들의 메뉴 화면 조회, 데이터 추가/수정/삭제/머지 등의 핵심 컨트롤러 및 서비스 API 호출 행위를 실시간으로 캡처하여 감사 및 보안 추적(Audit Trail)용으로 저장하는 원장 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **커스텀 프레임워크 AOP 로깅 인터셉터 연동 (`CustomAnnotationMapper.serviceLogWrite`)**: 백오피스 프레임워크 수준에서 커스텀 AOP 애노테이션(예: `@ServiceLog` 또는 `@AuditLog`)을 감지하여 컨트롤러/서비스 호출 시점(호출 메소드, 사용자 ID, 원격 IP, 호출 타입 등)에 대해 데이터베이스에 공통적으로 실시간 로깅 인서트 처리를 수행합니다.\n"
        "* **내부 통제 및 보안 감사 화면 조회**: 시스템 보안 정책에 따라 개인정보 노출 위험이 있거나 매출/재고/마감 등 주요 손익 지표에 수동 개입을 실행한 백오피스 운영 사용자의 세부 호출 로그를 보관하고, 관리자가 이를 날짜별/사용자별로 필터링 조회하는 증빙으로 사용됩니다."
    )

    data["tables"]["srvlogtb"] = {
        "memo": srvlogtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "log_seq": "로그 이력 순번 (시퀀스)",
            "user_id": "화면/서비스를 호출한 백오피스 사용자 ID",
            "remote_ip": "사용자 접속 원격 IP 주소",
            "service_menu": "호출된 백오피스 서비스 메뉴 (화면 경로/메뉴코드)",
            "service_name": "호출된 서비스 클래스 및 메소드 식별자",
            "service_type": "호출 유형 (SELECT: 조회, INSERT: 등록, UPDATE: 수정, DELETE: 삭제, MERGE: 병합)",
            "response_method": "응답을 처리한 컨트롤러/서비스 내부 메소드 정보",
            "create_dtime": "로그 생성/작동 일시 (YYYYMMDDHH24MISS)",
            "create_id": "로그 기록 생성자 ID (기본값: BACKOFFICE_SECURITY)"
        },
        "memo_c": "백오피스 웹 호출 발생 시 커스텀 AOP 인터셉터를 통해 공통 모듈에서 실시간 자동 생성 처리됩니다.",
        "memo_u": "감사 기록 특성 상 한 번 생성된 로그의 사후 변경 및 업데이트가 엄격히 차단됩니다.",
        "memo_d": "개인정보 보호 및 시스템 조작 감사 추적의 영구 증빙 자료이므로 임의 삭제가 전면 방지됩니다.",
        "memo_r": "본사/어드민 시스템 관리의 사용자 활동로그 화면 및 보안 분석 보고서 조회 시 주 원장으로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 보안 감사 로그 조회 시, 행위를 발생시킨 사용자 ID(user_id)에 대응하는 한글 성명, 소속 본부/매장 코드, 활성화 여부(use_yn)를 매치하여 추적 보고서에 출력하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점 관리자의 로그인 및 화면 사용 이력을 조회하거나, 특정 가맹점 소속 사용자 계정의 보안 이상 징후를 분류 조회할 때 사용자의 소속 매장 코드를 조인 연계합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. AOP 로그 로깅 시 예외적으로 로깅을 생략할 특정 IP 대역이나, 로그 보존 기간(예: 6개월, 1년 등) 등의 보안 환경설정 매개 변수를 매치하기 위해 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 호출된 서비스 타입(service_type - 예: SELECT, INSERT, UPDATE, DELETE 등)에 대응하는 한글 라벨(조회, 등록, 수정, 삭제)을 변환하기 위해 조인 결합됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 포스 전송 인터페이스 오류 및 에러 시 화면으로 전송 이력을 수동 재처리 조작한 백오피스 조작자의 행위를 감사 추적 대조하기 위해 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 특정 사용자가 과거 매출 데이터나 취소 내역을 민감하게 수동으로 변경하거나 삭제한 보안 사고 발생 시, 해당 시점의 화면 조작 로그와 매출 헤더의 수정 이력을 비교하기 위해 간접 연계 조인됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 발주 물량이나 단가를 변동시킨 백오피스 화면 호출 이력을 대조 추적하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 상품 코드 신규 등록 및 카테고리 단가 일괄 수정 작업을 진행한 사용자의 메뉴 실행 타임라인을 대조 분석하기 위해 간접 참조합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 매장별 특수 상품 정보 개정이나 단가 변동 화면을 호출한 근무자의 보안 승인 상태를 확인하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 매장 현재고를 수동으로 입출고 조정하거나 강제 재고 조정을 실행한 사용자의 조작 일시와 IP 주소를 대조 증빙하기 위해 조인합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 마감 단가 및 선입선출 수불 원장의 마감 보정 기능 메뉴를 가동한 관리자의 감사 추적 로그를 대조할 때 간접 연동됩니다."
            },
            {
                "table_name": "obslphtb",
                "description": "매입/발주 헤더 테이블. 매입 전표 확정 및 매입 취소 화면을 실행한 사용자의 조작 이력을 추적 증빙하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 32. SSACNCTB MEMO AND RELATED TABLES
    ssacnctb_memo = (
        "### 1. 테이블 개요\n"
        "POS 결제 수단/계정 마스터 동기화 및 로그 테이블 (`SSACNCTB`).\n"
        "가맹점별(`MS_NO`) 사용 가능한 결제 수단(현금, 신용카드, 제휴사 포인트, 간편결제, 외상 등) 분류 마스터 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **결제 수단 정보 실시간 동기화 큐 적재 (`MMACNC_T01` 트리거)**: 매장 결제 수단/계정 마스터 테이블(`MMACNCTB`)에 신규 결제 방식 등록, 결제 수단 한글명 변경, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MMACNC_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 계정구분 코드(`acnt_fg`), 결제수단명(`acnt_nm`) 정보를 실시간으로 `SSACNCTB` 큐에 인서트하고, 동시에 감사 로그(`MMSLOGTB`)에도 기록을 적재합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 결제 계정 정보가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M31/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 결제수단 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **매출 결제계정 사후 정합성 대조**: 포스 매출 결제 시 적용된 결제 수단별 승인 금액(카드, 현금 등)이 당일 시점에 POS 단말기에 설정된 결제 수단 종류 정책 범위 내에서 유효하게 처리되었는지 감사 대조하는 자료로 활용됩니다."
    )

    data["tables"]["ssacnctb"] = {
        "memo": ssacnctb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "acnt_fg": "결제수단 계정 구분 코드 (1: 현금, 2: 신용카드, 3: 상품권, 4: 외상 등)",
            "acnt_nm": "결제수단 한글 계정 명칭 (예: 온누리상품권, 포인트결제 등)"
        },
        "memo_c": "매장 결제 수단 마스터(MMACNCTB) 테이블의 변동 시 MMACNC_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 결제 수단 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 결제 설정 배포 모듈, 결제 계정관리 및 계정별 정산현황 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmacnctb",
                "description": "매장 결제 수단 마스터 테이블. [트리거 MMACNC_T01 연동] 백오피스 또는 본사에서 사용 가능한 결제 계정을 등록/수정/삭제 처리하면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSACNCTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 결제 계정 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMACNC_T01 연동] 결제 수단 마스터의 변동 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 포스에서 매출 영수증 결제 시 사용된 각 결제 금액이 해당 거래 시점에 POS 단말기에 다운로드 활성화된 결제수단 계정 코드 규정과 일치하는지 사후 대조 검증을 위해 간접 연계 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매장 결제 수단별로 적용할 한도 규정 및 영수증 끝전 할인 규정의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 결제 수단 계정 코드(acnt_fg) 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 결제 수단을 활성화/비활성화 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 결제 수단 중 특정 상품권이나 모바일 쿠폰 결제 시 적용 가능한 본사 표준 자재 품목 분류를 조회하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 외상 정산 시 결제 수단으로 외상 대금(weas_amt) 회수 내역과 매입 대금 상계 처리 내역을 연계 보고서로 대조할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 결제 수단 적용에 따른 실시간 판매 수량 차감 타당성을 대조 분석하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 결제 수단별 매출 마진율 및 현금 흐름의 가치를 평가하기 위해 원가를 대조 조회하는 데 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 특정 결제 수단 적용이 제한되는 상품 카테고리가 있는지 유효성을 검증하기 위해 조인됩니다."
            }
        ]
    }

    # 33. SSACNTTB MEMO AND RELATED TABLES
    ssacnttb_memo = (
        "### 1. 테이블 개요\n"
        "POS 결제 상세계정 마스터 동기화 및 로그 테이블 (`SSACNTTB`).\n"
        "가맹점별(`MS_NO`) 사용 가능한 상세 결제사/카드사 및 상품권 계정(현대카드, 삼성카드, 신세세계상품권, 온누리상품권 등) 마스터 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **결제 상세계정 정보 실시간 동기화 큐 적재 (`MMACNT_T01` 트리거)**: 매장 결제 상세계정 마스터 테이블(`MMACNTTB`)에 신규 신용카드/상품권 결제 코드 등록, 가맹점별 카드 수수료율 개정, 사용 유무 상태 변경(`AFTER INSERT/UPDATE/DELETE`)이 발생할 때, `MMACNT_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 계정구분 코드(`acnt_fg`), 상세 계정코드(`acnt_cd`), 계정명(`acnt_nm`) 정보를 실시간으로 `SSACNTTB` 큐에 인서트하고, 동시에 감사 로그(`MMSLOGTB`)에도 기록을 적재합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 상세 결제 계정 정보가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M06/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 결제수단 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **매출 카드사/상품권 정합성 사후 감사**: 포스 매출 결제 시 고객이 결제한 특정 신용카드사나 상품권 수납액이 해당 거래 시점에 POS 단말기에 설정된 계정 세부 규칙과 정밀하게 일치하게 처리되었는지 대조하는 자료로 활용됩니다."
    )

    data["tables"]["ssacnttb"] = {
        "memo": ssacnttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "acnt_fg": "결제수단 계정 구분 코드 (1: 현금, 2: 신용카드, 3: 상품권, 4: 외상 등)",
            "acnt_cd": "상세 결제사/카드사/상품권 식별 코드 (예: 0001: 국민카드, 0002: 신한카드 등)",
            "acnt_nm": "상세 결제계정 한글 명칭 (예: 현대카드, 신세계상품권 등)"
        },
        "memo_c": "매장 결제 상세계정 마스터(MMACNTTB) 테이블의 변동 시 MMACNT_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 결제 수단 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 결제 설정 배포 모듈, 결제 계정관리 및 계정별 정산현황 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmacnttb",
                "description": "매장 결제 상세계정 마스터 테이블. [트리거 MMACNT_T01 연동] 백오피스 또는 본사에서 상세 결제 카드사나 상품권 종류를 등록/수정/삭제 처리하면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSACNTTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 상세 결제 계정 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMACNT_T01 연동] 상세 결제 수단 마스터의 변동 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 결제수단별 결제 거래 승인 시, 특정 카드사 승인액이 해당 거래 시점에 POS 단말기에 다운로드된 카드사/상품권 계정 분류 규정과 일치하는지 사후 대조 검증을 위해 간접 연계 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매장 결제 수단별 수수료율 규정 및 영수증 끝전 할인 규정의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 상세 결제 계정 코드(acnt_cd) 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 상세 결제 계정을 활성화/비활성화 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 특정 신용카드사나 제휴 상품권 결제 시 구매 제한이 걸려 있는 상품 카테고리를 조회하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 신용카드 매입 대금 정산 및 수수료 내역과 물류 매입금 대조 정산 시 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 제휴 결제 수단 적용 시 재고 판매 가능 여부를 대조 분석하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 결제 수단별 매출 마진율 및 수수료 공제 후 실질 원가 평가 시 간접 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 특정 카드사나 제휴 결제 수단 적용 제한 상품이 마스터 상에 매칭되어 있는지 검증하기 위해 조인됩니다."
            }
        ]
    }

    # 34. SSBANKTB MEMO AND RELATED TABLES
    ssbanktb_memo = (
        "### 1. 테이블 개요\n"
        "POS 은행 마스터 동기화 및 로그 테이블 (`SSBANKTB`).\n"
        "가맹점별(`MS_NO`) 사용 가능한 국내 시중 금융기관 및 은행(국민은행, 신한은행, 우리은행, 하나은행 등) 마스터 코드가 추가/변경될 때, 변경 사항 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **은행 정보 실시간 동기화 큐 적재**: 공통 은행 마스터 테이블(`MBANKMTB`)에 신규 금융기관이 추가되거나 명칭/전화번호가 변경될 때, 시스템 관리자 또는 연계 API에 의해 변경 일련번호(`log_seq`), 처리구분(`proc_fg`), 은행코드(`bank_cd`), 은행명(`bank_nm`), 전화번호(`tel_no`) 정보가 실시간으로 `SSBANKTB` 큐에 동기화 인서트됩니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 은행 마스터 정보가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M30/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 은행 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **거래처 및 가맹점 계좌 사후 검증**: 백오피스 거래처 등록 관리(`Hq_Master_00015` 및 `Hq_Master_00016`) 시 입력된 은행 코드의 유효성을 검증하며, 가맹점의 일별 마감 송금 처리나 펌뱅킹 연동 정산 시 정합성 대조 기초 자료로 활용됩니다."
    )

    data["tables"]["ssbanktb"] = {
        "memo": ssbanktb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "bank_cd": "시중 은행/금융기관 식별 코드 (예: 004: 국민은행, 088: 신한은행 등)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "bank_nm": "금융기관 한글 명칭",
            "tel_no": "해당 금융기관 대표 전화번호"
        },
        "memo_c": "공통 은행 마스터(MBANKMTB) 정보의 변경 발생 시 시스템 연계 로직에 의해 동기화 기록이 생성됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 은행 정산 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 은행 정보 배포 모듈, 거래처 마스터 관리 및 가맹점 정산 송금 현황 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mbankmtb",
                "description": "공통 은행 마스터 테이블. 백오피스 또는 DBA에 의해 은행 종류가 추가/수정/삭제되면 변경 내역이 전송용 큐 테이블(SSBANKTB)에 로깅 및 보관되어 POS 단말기로 배포되는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 은행 코드 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mvndrmtb",
                "description": "거래처 마스터 테이블. 백오피스 거래처 등록 및 관리 화면에서 거래처 정산 계좌의 은행 명칭을 매핑 출력하기 위해 은행 코드 정보를 매치 참조합니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 포스에서 매출 마감 시 은행 입금 내역이나 임시 시송금 처리를 진행할 때 입금 대상 은행 코드의 유효성을 검증하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 은행 가맹점 결제 전송 및 펌뱅킹 연동 규칙의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 은행 분류 구분 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 거래처의 정산 은행 계좌 정보를 수정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 가맹점 매출 정산 시 특정 금융 상품이나 은행 계환 거래 대상에 지정된 본사 표준 자재 품목 분류를 조회하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점에서 은행 송금 결제를 통해 매입 대금을 송금 지급 정산 처리할 때 계좌 정보 대조를 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 은행 제휴 프로모션 적용에 따른 실시간 판매 수량 차감 타당성을 대조 분석하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 은행 송금 정산된 수량의 마진율 및 수수료 공제 후 실질 원가 평가 시 간접 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 은행 제휴 혜택이나 결제 조건이 특정 매장 상품 품목군에 한정하여 적용되는지 검증하기 위해 조인됩니다."
            }
        ]
    }

    # 35. SSBUMSTB MEMO AND RELATED TABLES
    ssbumstb_memo = (
        "### 1. 테이블 개요\n"
        "POS 상품 소그룹(분류) 마스터 동기화 및 로그 테이블 (`SSBUMSTB`).\n"
        "가맹점별(`MS_NO`) 관리하는 상품의 소분류 체계 코드가 추가/변경될 때, 변경 사항 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **소그룹 정보 실시간 동기화 큐 적재 (`MMBUMS_T01` 트리거)**: 매장 상품 소그룹(소분류) 마스터 테이블(`MMBUMSTB`)에 신규 분류가 등록, 소분류의 한글 명칭이 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)될 때, `MMBUMS_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 소분류 코드(`sub_group_cd`), 소분류 명칭(`sub_group_nm`) 정보를 실시간으로 `SSBUMSTB` 큐에 인서트하고, 감사 로그(`MMSLOGTB`)에도 기록을 남깁니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 상품 소분류 체계가 개정되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M16/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 소분류 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **상품 카테고리 매핑 정합성 검증**: POS 단말기에서 결제/판매 시 특정 상품이 올바른 분류 체계에 매핑되어 분류별 영수증 출력 및 매출 집계가 이루어지는지 보장하는 기초 규정으로 쓰입니다."
    )

    data["tables"]["ssbumstb"] = {
        "memo": ssbumstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "sub_group_cd": "상품 소분류 코드 (소그룹 코드)",
            "sub_group_nm": "상품 소분류 한글 명칭 (소그룹 명칭)"
        },
        "memo_c": "매장 상품 소그룹 마스터(MMBUMSTB) 테이블의 변동 시 MMBUMS_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드본을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 상품 분류 배포 모듈, 상품 소분류 설정 및 소분류별 매출 현황 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmbumstb",
                "description": "매장 상품 소그룹 마스터 테이블. [트리거 MMBUMS_T01 연동] 백오피스 또는 본사 마스터 변경에 의해 매장별 소분류가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSBUMSTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 소분류 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMBUMS_T01 연동] 상품 소분류 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 상품이 특정 소분류 코드(sub_group_cd)에 속해 있는 경우, 상품 마스터와 조인하여 해당 소분류의 한글 분류명칭을 대조 매칭 출력하기 위해 결합됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 소분류 카테고리별 마진율 통제 및 영수증 할인 적용 여부 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 상품 소분류 구분 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 소분류의 한글 명칭을 수정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 상품 마스터의 대분류, 중분류, 소분류 체계의 정합성을 매칭 조회하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 소분류 분류 단위별 매입 실적 및 원가 변동 추이를 분석 정산하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 소분류 카테고리별 실시간 재고 회전율 및 재고 잔량을 롤업 보고서에 출력하기 위해 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 소분류별 매출 마진율 및 수불 현황을 선입선출 원가 단위로 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객 결제 완료 시 발생한 단품별 판매 건수에 대해 소분류별 매출액 점유율 및 판매 추이 분석 보고서를 도출하기 위해 상품 마스터를 거쳐 소분류 코드 정보와 간접 연계 조인됩니다."
            }
        ]
    }

    # 36. SSCARDTB MEMO AND RELATED TABLES
    sscardtb_memo = (
        "### 1. 테이블 개요\n"
        "POS 제휴/신용 카드사 마스터 동기화 및 로그 테이블 (`SSCARDTB`).\n"
        "가맹점별 사용 가능한 신용카드 및 제휴 카드(할인/적립 등) 마스터 정보(국민카드, 신한카드, 현대카드 등)가 본사 차원에서 개정될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **카드사 정보 실시간 동기화 큐 적재 (`MCARDM_T01` 트리거)**: 매장 제휴/신용 카드사 마스터 테이블(`MCARDMTB`)에 신규 카드사 등록, 카드사 한글명칭 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MCARDM_T01` 트리거가 가동되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 카드사 코드(`card_co`), 카드사 명칭(`card_nm`) 정보를 실시간으로 `SSCARDTB` 큐에 인서트합니다. (참고: 전 가맹점 공통 배포이므로 매장코드(ms_no)는 '000000' 본사 기본 레코드로 생성됩니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 카드사 마스터가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M20/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 카드사 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **신용카드 승인 및 매입 정합성 사후 감사**: POS 단말기에서 결제 승인된 각 카드사 코드 규정이 당일 시점의 백오피스 카드사 설정 코드와 일치하는지 정합성을 대조하고 카드사별 매출 일보(`Hq_Sales_00011`) 조회를 위해 활용됩니다."
    )

    data["tables"]["sscardtb"] = {
        "memo": sscardtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (기본값: '000000' 본사 공통)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "card_co": "신용카드사 식별 코드 (예: 01: 현대, 02: 국민, 03: 신한 등)",
            "card_nm": "신용카드사 한글 명칭 (예: 현대카드, 국민카드 등)"
        },
        "memo_c": "매장 제휴/신용 카드사 마스터(MCARDMTB) 테이블의 변동 시 MCARDM_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 제휴 할인 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 신용카드사 정보 배포 모듈, 카드사별 매출 현황 및 신용카드 승인 내역 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mcardmtb",
                "description": "매장 제휴/신용 카드사 마스터 테이블. [트리거 MCARDM_T01 연동] 백오피스 또는 본사 마스터 변경에 의해 카드사 정보가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSCARDTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 카드사 마스터 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MCARDM_T01 연동] 카드사 마스터 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제할 때 신용카드를 사용한 경우, 결제 전표에 기록된 카드사 코드가 당일 시점에 POS 단말기에 다운로드된 카드사 규정과 일치하는지 정합성 대조를 위해 간접 연계 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 카드사별 결제 한도 및 영수증 끝전 할인 규정의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 카드사 구분 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 카드사의 가맹 계약 번호 및 상태를 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 카드사 제휴 할인 적용 시 특정 행사 품목 지정 및 구매 제한이 걸려 있는 상품 카테고리를 조회하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 신용카드 승인 및 매입 데이터 정산 시 거래처별 대금 상계 처리 내역과 비교 정산하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 카드사 제휴 프로모션 적용에 따른 실시간 판매 수량 차감 타당성을 대조 분석하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 카드사 매출 마진율 및 수수료율 공제 후 실질 원가 평가 시 간접 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 특정 카드사 혜택 적용 제한 상품이 마스터 상에 매칭되어 있는지 검증하기 위해 조인됩니다."
            }
        ]
    }

    # 37. SSCPLKTB MEMO AND RELATED TABLES
    sscplktb_memo = (
        "### 1. 테이블 개요\n"
        "POS PLU 단축키 설정 테이블 (`SSCPLKTB`).\n"
        "가맹점별(`MS_NO`) POS 화면에 출력될 간편 단축키(PLU 키)의 그룹 설정(`CLPLU_CD`), 키 버튼 번호 위치(`PLU_CD`), 실제 매핑 상품 코드(`GOODS_CD`) 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **단축키 정보 실시간 동기화 큐 적재 (`MMCPLK_T01` 트리거)**: 매장 PLU 단축키 설정 마스터 테이블(`MMCPLKTB`)에 신규 단축키 지정, 단축키 버튼 번호 수정, 매핑 상품 변경, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MMCPLK_T01` 트리거가 실행되어 변경 일련번호(`log_seq`), 처리구분(`proc_fg` - A/D), 단축키 그룹 코드(`clplu_cd`), 단축키 위치 코드(`plu_cd`), 상품코드(`goods_cd`) 정보를 실시간으로 `SSCPLKTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다. (참고: 단축키 번호나 위치가 바뀔 때 구 정보 삭제 후 신규 정보 삽입 동작을 지원합니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 단축키 설정 변경 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M04/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 단축키 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **단축키 매출 및 카테고리 기여도 정합성 검증**: POS 단말기에서 결제/판매 시 특정 단축키 터치를 통해 판매된 실적이 올바른 분류 체계와 매핑 상품 실적으로 롤업되어 분석 보고서에 반영되도록 유효성을 보장하는 기반으로 작동합니다."
    )

    data["tables"]["sscplktb"] = {
        "memo": sscplktb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "clplu_cd": "POS 단축키 분류/그룹 코드",
            "plu_cd": "POS 단축키 버튼 위치 번호 코드 (1~N번 위치)",
            "goods_cd": "해당 단축키 버튼에 매핑된 상품코드 (자재 코드)"
        },
        "memo_c": "매장 PLU 단축키 설정 마스터(MMCPLKTB) 테이블의 변동 시 MMCPLK_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 단축키 설정 배포 모듈, POS PLU 키 설정 및 매장 PLU 키 설정 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmcplktb",
                "description": "매장 PLU 단축키 설정 마스터 테이블. [트리거 MMCPLK_T01 연동] 백오피스 또는 본사 마스터 변경에 의해 단축키 매핑 정보가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSCPLKTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 단축키 레이아웃 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMCPLK_T01 연동] 단축키 설정 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 단축키에 매핑된 상품의 한글 상품명, 정상 판매단가 등을 매칭 출력하기 위해 조인합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 단축키 화면 레이아웃 및 폰트 크기 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 단축키 분류 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 단축키 배치를 변경 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 단축키에 매핑할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 단축키 등록 상품의 입고 및 매입 정산 데이터를 연계 보고서로 대조할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 단축키를 통해 신속 판매가 빈번히 이루어지는 신선식품 및 델리 품목의 실시간 재고를 대조 분석하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 단축키 등록 상품의 매출 마진율 및 수불 현황을 선입선출 원가 단위로 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 단축키(PLU Key)를 통해 간편 터치하여 판매 처리한 품목의 매출 총액 및 건수 정합성 분석 시 간접 참조됩니다."
            }
        ]
    }

    # 38. SSCPLUTB MEMO AND RELATED TABLES
    sscplutb_memo = (
        "### 1. 테이블 개요\n"
        "POS PLU 단축키 대분류(그룹) 설정 테이블 (`SSCPLUTB`).\n"
        "가맹점별(`MS_NO`) POS 화면에 출력될 간편 단축키(PLU 키)의 대분류(페이지 그룹) 번호 코드(`CLPLU_CD`), 해당 그룹 한글 명칭(`CLPLU_NM`) 정보를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **단축키 분류 정보 실시간 동기화 큐 적재 (`MMCPLU_T01` 트리거)**: 매장 PLU 단축키 대분류 마스터 테이블(`MMCPLUTB`)에 신규 분류 추가, 분류 한글명 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MMCPLU_T01` 트리거가 실행되어 변경 일련번호(`log_seq`), 처리구분(`proc_fg` - A/D), 단축키 그룹 코드(`clplu_cd`), 그룹 한글명(`clplu_nm`) 정보를 실시간으로 `SSCPLUTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다. (참고: 단축키 대분류 코드가 바뀔 때 구 분류 삭제 후 신규 분류 삽입 동작을 지원합니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 단축키 분류 설정 변경 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M03/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 분류 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **단축키 카테고리 기여도 정합성 검증**: POS 단말기에서 결제/판매 시 특정 대분류 그룹의 단축키가 올바른 분류 체계와 명칭을 띄고 화면에 렌더링되도록 유효성을 보장하는 기반으로 작동합니다."
    )

    data["tables"]["sscplutb"] = {
        "memo": sscplutb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "clplu_cd": "POS 단축키 대분류/페이지 그룹 코드",
            "clplu_nm": "POS 단축키 대분류 한글 명칭 (예: 분식류, 음료류 등)"
        },
        "memo_c": "매장 PLU 단축키 대분류 마스터(MMCPLUTB) 테이블의 변동 시 MMCPLU_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 단축키 대분류 설정 배포 모듈, POS PLU 키 설정 및 매장 PLU 키 설정 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmcplutb",
                "description": "매장 PLU 단축키 대분류 마스터 테이블. [트리거 MMCPLU_T01 연동] 백오피스 또는 본사 마스터 변경에 의해 단축키 그룹(페이지) 분류 정보가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSCPLUTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 단축키 대분류 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMCPLU_T01 연동] 단축키 대분류 설정 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 대분류에 매핑된 단품 상품 목록의 매출 수량 및 단가 정보를 소급 검증하기 위해 조인 결합됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 단축키 화면 레이아웃 및 폰트 크기 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 단축키 대분류 구분 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 단축키 분류 배치를 변경 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 단축키 대분류에 매핑할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 단축키 등록 상품의 입고 및 매입 정산 데이터를 연계 보고서로 대조할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 단축키 대분류에 매핑된 대표 상품들의 실시간 재고 회전율과 유통기한 대조를 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 단축키 등록 상품의 매출 마진율 및 수불 현황을 선입선출 원가 단위로 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 단축키(PLU Key) 대분류 카테고리를 터치하여 판매 처리한 품목의 매출 총액 및 건수 정합성 분석 시 간접 참조됩니다."
            }
        ]
    }

    # 39. SSDEPTTB MEMO AND RELATED TABLES
    ssdepttb_memo = (
        "### 1. 테이블 개요\n"
        "POS 부서/조직 마스터 동기화 및 로그 테이블 (`SSDEPTTB`).\n"
        "회사 본사 및 가맹 조직의 부서구조 마스터 정보가 본사 차원에서 추가/개정될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **부서 정보 실시간 동기화 큐 적재 (`TDEPTM_T01` 트리거)**: 본사 부서/조직 마스터 테이블 (`TDEPTMTB`)에 신규 조직/부서 등록, 부서 명칭 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `TDEPTM_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 부서 번호(`dept_no`), 부서 코드(`dept_cd`), 부서 명칭(`dept_nm`) 정보를 실시간으로 `SSDEPTTB` 큐에 인서트하고, 감사 로그(`MMSLOGTB`)에도 내역을 기록합니다.\n"
        "* **인사 시스템 인터페이스 연계**: 본부 인사(HR) 시스템으로부터 가맹 조직/부서 변경 사항이 수신되면 배치 프로그램(`DeptInterface`)이 기동되어 `TDEPTMTB` 원장을 동기화 갱신하고, 이에 따라 트리거가 연쇄 작동하여 `SSDEPTTB` 대기열에 변경 로그를 밀어 넣습니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 부서 변경 이력이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M05/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 부서 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다."
    )

    data["tables"]["ssdepttb"] = {
        "memo": ssdepttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "dept_no": "부서 고유 번호 (조직 내 일련번호)",
            "dept_cd": "부서 코드 (조직 분류 코드)",
            "dept_nm": "부서 한글 명칭 (예: 영업1본부, 가맹관리팀 등)"
        },
        "memo_c": "본사 부서 마스터(TDEPTMTB) 테이블의 변동 시 TDEPTM_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 부서 정보 배포 모듈, 본사 부서 마스터 설정 및 사용자 활동 보안 감사 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tdeptmtb",
                "description": "본사 부서/조직 마스터 테이블. 백오피스 또는 ERP 인사 시스템의 변경에 의해 부서 정보가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSDEPTTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점이 소속된 영업 부서 및 본부 조직을 판별하여 해당 점포의 POS 기기로 알맞은 부서 마스터 데이터를 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 TDEPTM_T01 연동] 부서 마스터 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 부서(예: 영업부, 식품부 등)에 한정된 상품 카테고리 매핑 및 통제를 검증하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 부서별 예산 한도 및 영수증 끝전 할인 규정의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 부서 성격 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 사용자 및 근무자의 소속 부서명(dept_nm)을 매칭 출력하고 사용자를 등록 조정한 조작자의 계정 감사 이력을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 특정 부서에서 취급 가능한 본사 표준 자재 품목 분류를 조회하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 부서별 매입 정산 실적 및 발주 처리 기여 비율을 연계 보고서로 분석할 때 비교용으로 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 영업 부서 단위별 재고 실사와 현재고 상태를 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 부서별 원가 배분 및 마진율 평가를 위해 상품 원가를 대조 조회하는 데 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 매출 상세에 기록된 판매/영업 근무자 계정의 소속 부서 정합성을 소급 검증할 때 간접 참조됩니다."
            }
        ]
    }

    # 40. SSGOODTB MEMO AND RELATED TABLES
    ssgoodtb_memo = (
        "### 1. 테이블 개요\n"
        "POS 매장 상품 마스터 동기화 및 로그 테이블 (`SSGOODTB`).\n"
        "가맹점별(`MS_NO`) 상품 마스터 정보(판매단가, 세부과세구분, 상품포인트, 세트상품 여부 등)가 추가되거나 변경/수정될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **매장 상품 변동 시 실시간 동기화 큐 적재 (`MGOODS_T01` 트리거)**: 매장별 상품 마스터 테이블(`MGOODSTB`)에 신규 상품 등록, 판매단가(`uprice`) 개정, 면세/과세 속성 개정, 사용 여부(`use_fg`) 변경(`AFTER INSERT/UPDATE/DELETE`)이 발생할 때, `MGOODS_T01` 트리거가 가동되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 한글상품명(`goods_nm`), 단가(`uprice`), 과세 여부(`tax_fg`), 대/중/소분류 등의 정보를 실시간으로 `SSGOODTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 남깁니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 상품 및 가격 변경 이력이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M10/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 상품 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 거래 승인 정합성 사후 검증**: 고객 결제 시 POS 단말기에서 인쇄된 품목의 가격과 부가세 과세 형태가 당일 백오피스에 설정된 상품 마스터 규정 범위 내에서 정확하게 부합하는지 매출 정합성을 사후 대조하는 기반 데이터로 사용됩니다."
    )

    data["tables"]["ssgoodtb"] = {
        "memo": ssgoodtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "goods_cd": "상품코드 (자재 코드)",
            "goods_nm": "상품 한글 명칭",
            "lclass_cd": "상품 대분류 코드",
            "mclass_cd": "상품 중분류 코드",
            "sclass_cd": "상품 소분류 코드",
            "uprice": "상품 기준 판매 단가",
            "print_fg": "주문서 출력 위치 구분",
            "goods_price_fg": "임의 단가변경 허용 여부 구분",
            "goods_point": "상품 구매 시 적립해줄 기본 포인트",
            "service_fg": "부가 메뉴 구분",
            "vat_rate": "부가세율 (%)",
            "tax_fg": "과세 종류 구분 (0: 과세, 1: 면세 등)",
            "set_fg": "세트상품 여부 (0: 일반, 1: 세트상품)",
            "tip_fg": "봉사료 부과 여부",
            "goods_type": "상품 상세 유형 구분 (0: 일반, 1: 세트, 2: 옵션 등)",
            "calory": "상품 칼로리 정보",
            "defcust_cnt": "메뉴 기본 인원수",
            "multi_biz_cd": "복수 사업자 지정 코드",
            "goods_sub_nm": "상품 영문/보조 명칭",
            "sub_group_cd": "옵션 메뉴 그룹 코드",
            "erp_goods_cd": "ERP 연동용 상품 표준 코드",
            "goods_style_cd": "상품 스타일 및 규격 번호",
            "goods_brand_cd": "상품 브랜드 식별 코드",
            "goods_dc_fg": "상품 자체 할인 적용 가능 여부 (0: 가능, 1: 불가)",
            "goods_short_name": "영수증 출력용 약식 단축 상품명"
        },
        "memo_c": "매장별 상품 마스터(MGOODSTB) 테이블의 변동 시 MGOODS_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 상품 마스터 정보 배포 모듈, 상품 관리 및 매장 상품 단가 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. [트리거 MGOODS_T01 연동] 백오피스 또는 본사 마스터 변경에 의해 매장 상품의 단가나 속성이 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSGOODTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 상품 마스터 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MGOODS_T01 연동] 상품 마스터 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 매출 상세에 기록된 단품 상품코드가 당일 거래 시점에 POS 단말기에 다운로드된 상품 규정 및 판매가와 일치하는지 정합성 대조를 위해 간접 연계 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 상품별 과세율 및 영수증 끝전 할인 규정의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 상품 대/중/소분류 구분 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 상품의 마스터 정보를 수정하거나 단가를 변경 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사에서 개정한 표준 자재 정보가 매장 상품 마스터 및 SSGOODTB 전송 큐로 올바르게 전파되었는지 상품 유효성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 상품별 매입 단가와 현재 매출 단가를 비교하여 실시간 마진율 분석 보고서를 출력할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 상품 마스터와 조인하여 소속 상품별 실시간 수불 재고와 현재고 상태를 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 매출 상품 수량의 원가를 선입선출법으로 추적 대조하여 품목별 매출이익을 평가할 때 조인 연계됩니다."
            },
            {
                "table_name": "mmacnttb",
                "description": "매장 결제 수단/계정 마스터 테이블. 특정 상품군에 대해 적용 제한이 걸린 결제 수단(상품권, 포인트 등) 정책 유효성 검증을 위해 간접 연계됩니다."
            }
        ]
    }

    # 41. SSKPRNTB MEMO AND RELATED TABLES
    sskprntb_memo = (
        "### 1. 테이블 개요\n"
        "POS 주방프린터 출력 설정 마스터 동기화 및 로그 테이블 (`SSKPRNTB`).\n"
        "가맹점별(`MS_NO`) 각 상품 주문 시 어느 주방 프린터로 주문서가 전송되고 출력될 것인지 주방프린터 연결 상태 및 상품별 주방 매핑 정보가 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **주방프린터 정보 실시간 동기화 큐 적재 (`MKPRNT_T01` 트리거)**: 매장 주방프린터 출력 설정 마스터 테이블(`MKPRNTTB`)에 신규 상품 주방프린터 할당, 프린터 번호 수정, 출력 사용 여부(`print_use_yn`) 개정, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MKPRNT_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 상품코드(`goods_cd`), 프린터번호(`print_no`), 출력매수 등의 정보를 실시간으로 `SSKPRNTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 주방프린터 설정 변경 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M21/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 주방프린터 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **주방 주문서 정합성 검증**: POS 단말기에서 결제/판매/주문 시 특정 식자재 품목이 올바른 주방 파트(예: 콜드 파트, 핫 파트, 음료 파트 등)로 실시간 분기 출력되어 주방 근무자가 차질 없이 음식을 준비할 수 있도록 정합성을 보장합니다."
    )

    data["tables"]["sskprntb"] = {
        "memo": sskprntb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "goods_cd": "대상 상품코드 (자재 코드)",
            "print_no": "주방 프린터 번호 (출력 목적지 번호)",
            "print_use_yn": "주방 프린터 출력 사용 여부 (Y/N)",
            "tbl_group_cd": "테이블 그룹 코드 (특정 구역 테이블 전담 여부)",
            "qty_print_yn": "상품 수량 개별 출력 여부 (Y/N)",
            "goods_print_cnt": "주문서 출력 매수 (기본값: '1')"
        },
        "memo_c": "매장 주방프린터 출력 설정 마스터(MKPRNTTB) 테이블의 변동 시 MKPRNT_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 주문 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 주방프린터 설정 배포 모듈, 매장 주방프린터 설정 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mkprnttb",
                "description": "매장 주방프린터 출력 설정 마스터 테이블. 백오피스 변경에 의해 상품별 주방프린터 번호, 테이블그룹, 출력 여부가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSKPRNTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 주방 프린터 설정 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MKPRNT_T01 연동] 주방프린터 설정 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 주방 프린터 출력 설정에 할당된 상품의 한글 상품명, 정상 판매단가 등을 매칭 출력하기 위해 조인합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 주방 프린터 드라이버 및 용지 사양 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 프린터 형식 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 주방 프린터 속성 및 연결 상태를 변경 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 주방 프린터에 매핑할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 주방 프린터 출력 설정에 매핑된 상품의 입고/발주 데이터를 연계 보고서로 대조할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 주방 주문 인쇄 시 실시간 식자재 재고 차감 타당성을 대조 분석하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 주방 주문 처리된 상품의 매출 마진율 및 수불 현황을 선입선출 원가 단위로 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 매출 상세에 기록된 주문 내역이 당일 주방 프린터에 전송된 주문서와 일치하는지 정합성 분석 시 간접 참조됩니다."
            }
        ]
    }

    # 42. SSLPLKTB MEMO AND RELATED TABLES
    sslplktb_memo = (
        "### 1. 테이블 개요\n"
        "POS 단말기별 PLU 단축키 설정 동기화 및 로그 테이블 (`SSLPLKTB`).\n"
        "가맹점 내부의 개별 단말기(`POS_NO`)별로 특수한 단축키(PLU 키) 레이아웃(분류 `CLPLU_CD`, 키 번호 `PLU_CD`, 매핑 상품 `GOODS_CD`)을 지정하여 직접 POS 상에서 조정한 이력이 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송/업로드 동기화하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **단말기별 단축키 정보 실시간 동기화 큐 적재 (`MMLPLK_T01` 트리거)**: 매장 POS별 PLU 단축키 설정 마스터 테이블(`MMLPLKTB`)에 신규 단축키 지정, 단축키 버튼 번호 수정, 매핑 상품 변경, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MMLPLK_T01` 트리거가 실행되어 변경 일련번호(`log_seq`), 처리구분(`proc_fg` - A/D), 단축키 그룹 코드(`clplu_cd`), 단축키 위치 코드(`plu_cd`), 상품코드(`goods_cd`) 정보를 실시간으로 `SSLPLKTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다. (참고: 단축키 번호나 위치가 바뀔 때 구 정보 삭제 후 신규 정보 삽입 동작을 지원합니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 단말기별 단축키 설정 변경 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M04/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 단축키 변경 데이터를 개별 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **가맹점 공통 단축키와의 분리 제어**: 가맹점 전체 공통 단축키 설정(`MMCPLKTB`)과 별개로 특정 POS 단말기(예: 주문 전용 POS, 반품 전용 POS 등)에 맞춘 특수 레이아웃을 통제하고 싱크를 보장하는 기반으로 작동합니다."
    )

    data["tables"]["sslplktb"] = {
        "memo": sslplktb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "pos_no": "개별 POS 단말기 식별 번호 (예: 01, 02 등)",
            "clplu_cd": "POS 단축키 분류/그룹 코드",
            "plu_cd": "POS 단축키 버튼 위치 번호 코드 (1~N번 위치)",
            "goods_cd": "해당 단축키 버튼에 매핑된 상품코드 (자재 코드)"
        },
        "memo_c": "매장 POS별 PLU 단축키 설정 마스터(MMLPLKTB) 테이블의 변동 시 MMLPLK_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 단축키 설정 배포 모듈, 개별 POS 단말기 단축키 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmlplktb",
                "description": "매장 POS별 PLU 단축키 설정 마스터 테이블. [트리거 MMLPLK_T01 연동] 개별 POS 단말기 단에서 단축키 설정이 조율되거나 수정되어 마스터 원장이 변경될 때, 트리거가 이를 감지하여 전송 큐 테이블(SSLPLKTB)에 이력을 밀어 넣습니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 단축키 레이아웃 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMLPLK_T01 연동] 단축키 설정 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 단축키에 매핑된 상품의 한글 상품명, 정상 판매단가 등을 매칭 출력하기 위해 조인합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 단축키 화면 레이아웃 및 폰트 크기 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 단축키 분류 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 단축키 배치를 변경 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 단축키에 매핑할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 단축키 등록 상품의 입고 및 매입 정산 데이터를 연계 보고서로 대조할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 단축키를 통해 신속 판매가 빈번히 이루어지는 신선식품 및 델리 품목의 실시간 재고를 대조 분석하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 단축키 등록 상품의 매출 마진율 및 수불 현황을 선입선출 원가 단위로 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 단축키(PLU Key)를 통해 간편 터치하여 판매 처리한 품목의 매출 총액 및 건수 정합성 분석 시 간접 참조됩니다."
            }
        ]
    }

    # 43. SSLPLUTB MEMO AND RELATED TABLES
    sslplutb_memo = (
        "### 1. 테이블 개요\n"
        "POS 단말기별 PLU 단축키 대분류(그룹) 설정 동기화 및 로그 테이블 (`SSLPLUTB`).\n"
        "가맹점 내부의 개별 단말기(`POS_NO`)별로 특수한 단축키(PLU 키)의 대분류(페이지 그룹) 번호 코드(`CLPLU_CD`), 해당 그룹 한글 명칭(`CLPLU_NM`) 정보를 POS 단말기로 실시간 다운로드 전송/업로드 동기화하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **단말기별 단축키 분류 정보 실시간 동기화 큐 적재 (`MMLPLU_T01` 트리거)**: 매장 POS별 PLU 단축키 대분류 설정 마스터 테이블(`MMLPLUTB`)에 신규 분류 추가, 분류 한글명 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MMLPLU_T01` 트리거가 실행되어 변경 일련번호(`log_seq`), 처리구분(`proc_fg` - A/D), 단축키 그룹 코드(`clplu_cd`), 그룹 한글명(`clplu_nm`) 정보를 실시간으로 `SSLPLUTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다. (참고: 단축키 대분류 코드가 바뀔 때 구 분류 삭제 후 신규 분류 삽입 동작을 지원합니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 단말기별 단축키 분류 설정 변경 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M03/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 분류 변경 데이터를 개별 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **가맹점 공통 단축키 대분류와의 분리 제어**: 가맹점 전체 공통 단축키 대분류 설정(`MMCPLUTB`)과 별개로 특정 POS 단말기(예: 주문 전용 POS, 반품 전용 POS 등)에 맞춘 특수 분류 레이아웃을 통제하고 싱크를 보장하는 기반으로 작동합니다."
    )

    data["tables"]["sslplutb"] = {
        "memo": sslplutb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "pos_no": "개별 POS 단말기 식별 번호 (예: 01, 02 등)",
            "clplu_cd": "POS 단축키 대분류/페이지 그룹 코드",
            "clplu_nm": "POS 단축키 대분류 한글 명칭 (예: 분식류, 음료류 등)"
        },
        "memo_c": "매장 POS별 PLU 단축키 대분류 마스터(MMLPLUTB) 테이블의 변동 시 MMLPLU_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 단축키 대분류 설정 배포 모듈, 개별 POS 단말기 단축키 대분류 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmlplutb",
                "description": "매장 POS별 PLU 단축키 대분류 마스터 테이블. [트리거 MMLPLU_T01 연동] 개별 POS 단말기 단에서 단축키 대분류 설정이 조율되거나 수정되어 마스터 원장이 변경될 때, 트리거가 이를 감지하여 전송 큐 테이블(SSLPLUTB)에 이력을 밀어 넣습니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 단축키 대분류 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMLPLU_T01 연동] 단축키 대분류 설정 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 대분류에 매핑된 단품 상품 목록의 매출 수량 및 단가 정보를 소급 검증하기 위해 조인 결합됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 단축키 화면 레이아웃 및 폰트 크기 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 단축키 대분류 구분 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 단축키 분류 배치를 변경 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 단축키 대분류에 매핑할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 단축키 등록 상품의 입고 및 매입 정산 데이터를 연계 보고서로 대조할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 단축키 대분류에 매핑된 대표 상품들의 실시간 재고 회전율과 유통기한 대조를 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 단축키 등록 상품의 매출 마진율 및 수불 현황을 선입선출 원가 단위로 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 단축키(PLU Key) 대분류 카테고리를 터치하여 판매 처리한 품목의 매출 총액 및 건수 정합성 분석 시 간접 참조됩니다."
            }
        ]
    }

    # 44. SSMEMBTB MEMO AND RELATED TABLES
    ssmembtb_memo = (
        "### 1. 테이블 개요\n"
        "POS 가맹점(매장) 마스터 동기화 및 로그 테이블 (`SSMEMBTB`).\n"
        "가맹점 기본 환경설정 정보(점포명, 대표자명, 전화번호, 영수증 헤더/테일 메시지, 끝전 올림/내림 처리방식, 부가세 적용 구분 등)가 백오피스 또는 ERP 연동을 통해 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹점 속성 변경 시 실시간 동기화 큐 적재 (`MMEMBS_T01` / `MMEMBV_T01` / `MMEMBP_T01` 트리거)**: 매장 기본 마스터 (`MMEMBSTB`), 가맹점 부가속성 (`MMEMBVTB`), 정산 및 포인트 설정 (`MMEMBPTB`) 원본 테이블 중 하나라도 수정되거나 등록되면 각각의 트리거가 자동 작동하여 가맹점의 모든 현재 속성을 결합 가공한 후 `SSMEMBTB` 큐에 실시간 레코드로 밀어 넣고 감사 로그(`MMSLOGTB`)에도 남깁니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 매장 환경설정 정보가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M40/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 매장 환경설정 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 결제/영수증 정합성 기준**: POS 단말기에서 결제 처리 시 단말기 끝전 절사 연산, 영수증 인쇄 양식, 부가세 과세/면세 연산 처리의 기초 매개 규정 역할을 보장합니다."
    )

    data["tables"]["ssmembtb"] = {
        "memo": ssmembtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "biz_no": "사업자 등록번호",
            "ms_nm": "매장 한글 명칭",
            "chain_nm": "가맹 체인 브랜드명",
            "master_nm": "가맹점 대표자명",
            "tel_no": "가맹점 대표 전화번호",
            "chain_fg": "체인 형태 구분 (0: 독립점, 1: 직영/가맹 등)",
            "address": "가맹점 도로명/지번 주소",
            "head_msg": "영수증 상단 인쇄 메시지 (헤더 메시지)",
            "tail_msg": "영수증 하단 인쇄 메시지 (테일 메시지)",
            "point": "기본 구매 적립 포인트율",
            "point_unit": "포인트 적립 단위 조건",
            "point_card_mask": "포인트 카드 승인 시 마스킹 패턴",
            "round_fg": "단수 절사 방식 구분 (끝전 올림/내림/반올림 설정)",
            "kitchen_yn": "주방 프린터 주문서 사용 여부 (Y/N)",
            "delivery_yn": "배달(딜리버리) 주문 연동 사용 여부 (Y/N)",
            "emp_card_mask": "임직원 할인 카드 마스킹 패턴",
            "vat_fg": "가맹점 부가세 계산 구분 규정",
            "ocb_cat_id": "오케이캐쉬백 가맹 단말기 ID",
            "ocb_passwd": "오케이캐쉬백 비밀번호",
            "zip_no": "우편번호",
            "amt_round_pos": "끝전 금액 처리 자리수 설정 (예: 2: 1원 단위 절사 등)",
            "amt_round_type": "금액 절사 연산 타입",
            "kitchen_cnt": "가맹점 내 연결 주방프린터 개수",
            "code_source_mask": "특수 코드 마스킹 포맷",
            "sale_del": "매출 취소 및 삭감 규정 코드",
            "weight_unit": "무게/중량 계량 단위 설정",
            "price_unit": "금액/통화 단위 설정",
            "kitchen_group_yn": "주방 프린터 그룹화 사용 여부",
            "master_eng_nm": "대표자 영문 명칭",
            "eng_address": "영문 주소",
            "shop_wh_yn": "매장 창고 운영 여부 (N: 일반, Y: 창고형)",
            "work_appr_yn": "근무 인원 근무 승인제 사용 여부",
            "shop_brand_cd": "가맹점 소속 브랜드 코드",
            "mpoint_rate": "멤버십 포인트 적립 비율",
            "if_biz_cd": "외부 연동 시스템 사업 영역 코드",
            "if_shop_cd": "외부 연동 시스템 점포 연계 코드"
        },
        "memo_c": "가맹점 마스터(MMEMBSTB) 또는 부가속성(MMEMBVTB) 테이블의 변동 시 MMEMBS_T01, MMEMBV_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 가맹점 환경 정보 배포 모듈, 매장 기본 정보 설정 및 정산/포인트 조건 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 원장 테이블. [트리거 MMEMBS_T01 연동] 백오피스 또는 본사 마스터 변경에 의해 가맹점 기본 정보(매장명, 사업자번호 등)가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSMEMBTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembvtb",
                "description": "가맹점 추가 속성 설정 마스터 테이블. [트리거 MMEMBV_T01 연동] 매장 부가 속성(부가세 구분, 끝전 처리방식, OCB 정보 등)의 변경 발생 시 트리거가 작동하여 SSMEMBTB에 적재하는 추가 마스터입니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMEMBS_T01/MMEMBV_T01 연동] 가맹점 정보 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 매장의 과세 형태(vat_fg) 및 판매 규칙에 따라 매장 단품 상품 마스터의 단가와 정합성을 대조하기 위해 조인 결합됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 단위별 매장 옵션 및 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 가맹점 형태 구분 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 마스터 정보를 등록/조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 가맹점별 매장 브랜드 코드(shop_brand_cd)에 따라 본사 표준 자재 정보 중 취급 가능한 품목의 유효성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 정보에 정의된 사업자 등록번호에 대응하는 매장 거래처 매입 정산 실적을 롤업 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 매장 마스터와 조인하여 해당 점포의 실시간 수불 재고와 현재고 상태를 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 가맹점의 선입선출법 적용 환경 유무에 따른 수불 마진율 평가를 위해 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 영수증에 인쇄된 가맹점 대표자명 및 전화번호 등 매장 정보의 정합성을 매출 상세 건별로 사후 검증할 때 간접 참조됩니다."
            }
        ]
    }

    # 45. SSMEMPTB MEMO AND RELATED TABLES
    ssmemptb_memo = (
        "### 1. 테이블 개요\n"
        "POS 단말기별 개별 환경설정 동기화 및 로그 테이블 (`SSMEMPTB`).\n"
        "가맹점의 각 개별 POS 단말기(`POS_NO`)별 승인 옵션, 디스플레이 옵션, MSR 카드 리더 사용 여부, 영수증 로고 인쇄 여부 및 MAC/IP 정보가 추가되거나 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 단말기 정보 실시간 동기화 큐 적재 (`MMEMBP_T01` 트리거)**: 매장 POS 단말기 마스터 테이블(`MMEMBPTB`)에 신규 POS 기기 추가, 허용 IP/MAC 주소 수정, 주변 하드웨어 승인 형태 변경, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MMEMBP_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 주문사용방식(`order_yn`), 디스플레이설정(`cust_disp_yn`), IP 및 MAC 주소 등의 정보를 실시간으로 `SSMEMPTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 남깁니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 개별 POS 환경 정보가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M47/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 단말기 환경설정 데이터를 개별 매장의 해당 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 단말기 부팅/로그인 허용 검증**: POS 단말기가 처음으로 구동하여 서버에 소켓 연결 및 로그인 요청 시, 단말기별로 할당된 허용 MAC/IP 주소(`mac_add_ip`) 규정에 적합한지 유효성을 검증하는 중추 역할을 담당합니다."
    )

    data["tables"]["ssmemptb"] = {
        "memo": ssmemptb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "매장 내부 개별 POS 단말기 번호 (01, 02 등)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "order_yn": "주문 형태 및 터치 방식 사용 구분",
            "cust_disp_yn": "고객 디스플레이 표시 장치 사용 여부 (Y/N)",
            "plu_fg": "PLU 단축키 화면 표현 속성",
            "auth_fg": "신용카드 대리점 승인 사용 구분",
            "cust_yn": "고객 관리 카드 리더(MSR/바코드) 사용 구분",
            "logo_yn": "영수증 상단 로고 이미지 인쇄 여부 (Y/N)",
            "jungsan_fg": "POS 마감 정산 연산 방식 구분",
            "mjungsan_fg": "복수 POS 정산 마감 방식 구분",
            "mac_add_ip": "POS 단말기 네트워크 MAC 주소 및 IP 주소 정보",
            "pos_mobile_type": "POS 기기 성격 구분 (0: 일반 데스크 POS, 1: 모바일 주문 POS)"
        },
        "memo_c": "매장 POS 단말기 마스터(MMEMBPTB) 테이블의 변동 시 MMEMBP_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 단말기별 개별 설정 배포 모듈, POS 관리 및 전체 단말기 목록 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmembptb",
                "description": "매장 POS 단말기 마스터 테이블. [트리거 MMEMBP_T01 연동] 백오피스 변경에 의해 POS 단말기 옵션(디스플레이 형태, 리더 설정, 프린터 연동 및 허용 IP/MAC 주소 등)이 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSMEMPTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 원장 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기별로 설정 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMEMBP_T01 연동] POS 단말기 설정 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 단말기 환경설정에 정의된 단축키 사용 유형에 부합하도록 매핑된 단품 상품 목록의 단가 및 속성 유효성을 검증하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 단위별 매장 옵션 및 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. POS 종류 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 POS 옵션을 등록/조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. POS 단말기 종류에 따른 화면 판매 상품 분류 제약 조건을 매칭 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점별 POS 기기 도입 현황에 따른 물류 설비 감가상각 및 매입 대금 정산 자료로 활용하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 POS 단말기에서 처리되는 실시간 재고 차감 및 실사 내역을 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. POS 단말기 결제 흐름과 연동되는 수불 마진율 평가를 위해 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 매출 상세 건이 어느 POS 단말기(pos_no)를 통해 입력되었는지 정합성을 사후 검증할 때 간접 참조됩니다."
            }
        ]
    }

    # 46. SSMSRCTB MEMO AND RELATED TABLES
    ssmsrctb_memo = (
        "### 1. 테이블 개요\n"
        "POS 상품 소스/원산지 마스터 동기화 및 로그 테이블 (`SSMSRCTB`).\n"
        "가맹점별(`MS_NO`) 각 상품에 들어가는 식자재 및 메뉴의 원산지 표기 문구(예: 쇠고기: 국내산 한우, 돼지고기: 미국산 등)가 추가되거나 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **원산지 정보 실시간 동기화 큐 적재 (`MMSSRC_T01` 트리거)**: 매장 상품 원산지 마스터 테이블(`MMSSRCTB`)에 신규 상품 원산지 할당, 한글 표기 문구 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MMSSRC_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 상품코드(`goods_cd`), 원산지 표기 내용(`source`) 정보를 실시간으로 `SSMSRCTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다. (참고: 원산지 정보 수정 시 구 레코드 삭제 후 신규 레코드를 삽입하는 정합성 큐 방식을 지원합니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 원산지 설정 변경 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M01/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 원산지 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **식품 위생 및 표시 의무 정합성 검증**: POS 단말기에서 주문 및 결제 영수증 출력 시 각 메뉴에 대응하는 원산지 정보가 정확하게 고객에게 공지 및 출력될 수 있도록 정합성을 보장합니다."
    )

    data["tables"]["ssmsrctb"] = {
        "memo": ssmsrctb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "goods_cd": "대상 상품코드 (자재 코드)",
            "source": "식자재/원료 원산지 정보 문구 (예: 국내산, 미국산 등)"
        },
        "memo_c": "매장 상품 원산지 마스터(MMSSRCTB) 테이블의 변동 시 MMSSRC_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 주문 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 원산지 설정 배포 모듈, 매장 상품 원산지 설정 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmssrctb",
                "description": "매장 상품 원산지 마스터 테이블. 백오피스 변경에 의해 상품 원산지 맵핑이 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSMSRCTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 원산지 동기화 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMSSRC_T01 연동] 원산지 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 원산지가 지정된 상품의 한글 상품명, 정상 판매단가 등을 매칭 출력하기 위해 조인합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 영수증 원산지 고지 의무 출력 유무 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 원산지 국가 코드 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 상품의 원산지를 수정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 원산지를 부여할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 매입 원재료 수급처의 원산지 품질 성적서 정보와 가맹점 원산지 설정을 연동 대조할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 원산지 식자재 재고 차감 및 실사 내역을 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 원산지별 자재 유통 단가 및 마진율 평가를 위해 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 매출 상세 건에 원산지 고지 상품이 포함되어 영수증에 정확히 출력되었는지 정합성을 사후 검증할 때 간접 참조됩니다."
            }
        ]
    }

    # 47. SSMTBLTB MEMO AND RELATED TABLES
    ssmtbltb_memo = (
        "### 1. 테이블 개요\n"
        "POS 테이블 배치 설정 동기화 및 로그 테이블 (`SSMTBLTB`).\n"
        "가맹점별(`MS_NO`) POS 화면에 기하학적으로 배치될 테이블의 위치 번호(`TABLE_NO`), 한글명(`TABLE_NM`), 활성화 여부(`TBL_USE_FG`), 속한 층/구역 그룹 코드(`TBL_GROUP_CD`), 화면 좌표 및 크기 정보가 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **테이블 배치 정보 실시간 동기화 큐 적재 (`MMSTBL_T01` 트리거)**: 매장 테이블 배치 마스터 테이블(`MMSTBLTB`)에 신규 테이블 추가, 테이블 버튼 위치(X, Y) 및 크기(너비, 높이) 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MMSTBL_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 테이블번호(`table_no`), 테이블명칭(`table_nm`), 그룹코드 및 해상도 정보를 실시간으로 `SSMTBLTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다. (참고: 테이블 구역 명칭 대조를 위해 층/구역 마스터인 `MMSFLRTB` 테이블을 연계 조회합니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 테이블 배치 변경 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M02/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 테이블 배치 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **테이블 매출 및 회전율 정합성 검증**: POS 단말기에서 결제/판매 시 특정 테이블 터치를 통해 발생한 매출이 매출 상세(`Strndttb`) 및 매출 헤더(`Strnhdtb`)의 테이블 번호 정보와 완벽히 결합 매치되어 테이블별 매출 일보(`St_Sales_00020`)를 구성하도록 지원합니다."
    )

    data["tables"]["ssmtbltb"] = {
        "memo": ssmtbltb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "tbl_group_cd": "테이블 소속 구역/층 코드 (MMSFLRTB 테이블 참조)",
            "tbl_group_nm": "테이블 소속 구역/층 한글 명칭 (예: 1층, 테라스 등)",
            "table_no": "테이블 고유 식별 번호 (예: 001, 002 등)",
            "table_nm": "테이블 한글 명칭 (예: 1번 테이블, 단체석 등)",
            "tbl_use_fg": "테이블 활성화 및 사용 여부 (0: 미사용, 1: 사용)",
            "tbl_page_seq": "테이블 페이지 순서 번호",
            "tbl_coor_x": "POS 화면상 테이블 GUI X 좌표 위치값",
            "tbl_coor_y": "POS 화면상 테이블 GUI Y 좌표 위치값",
            "tbl_width": "POS 화면상 테이블 GUI 버튼 가로 너비 크기",
            "tbl_height": "POS 화면상 테이블 GUI 버튼 세로 높이 크기",
            "screen_size": "POS 화면 크기 해상도 구분 (0: 800*600, 1: 1024*768)"
        },
        "memo_c": "매장 테이블 마스터(MMSTBLTB) 테이블의 변동 시 MMSTBL_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 주문 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 테이블 설정 배포 모듈, 테이블 배치 설정 및 테이블별 매출 분석 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmstbltb",
                "description": "매장 테이블 배치 마스터 테이블. 백오피스 변경에 의해 테이블 배치 속성(좌표 X/Y, 너비/높이, 해상도 등)이 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSMTBLTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 테이블 설정 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMSTBL_T01 연동] 테이블 설정 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 테이블별 매출 및 주문 연계 분석 보고서 작성 시 상품 단가 정보 등을 매칭하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 테이블 배치 해상도 기본값 및 최대 제한 개수 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 테이블 그룹(층/구역) 분류 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 매장의 테이블 배치 좌표를 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 테이블별 주문 상품 자재 분류 및 정합성 검증을 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 평당 테이블 효율 및 매입 자재 회전율을 비교 대조 분석 보고서로 도출할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 테이블 주문에 따라 실시간 주방 주문 인쇄 및 매핑 식자재 재고 차감 정합성을 대조 분석하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 테이블별 주문 품목의 매출 마진율 및 수불 현황을 선입선출 원가 단위로 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 매출 상세 건이 어느 테이블(table_no)에서 발생했는지 매출 정합성을 사후 검증할 때 간접 참조됩니다."
            }
        ]
    }

    # 48. SSNAMETB MEMO AND RELATED TABLES
    ssnametb_memo = (
        "### 1. 테이블 개요\n"
        "POS 공통 명칭 코드 마스터 동기화 및 로그 테이블 (`SSNAMETB`).\n"
        "시스템 전반에 활용되는 공통 명칭 코드 마스터(`MNAMEMTB`)가 백오피스 화면을 통해 등록, 수정, 삭제될 때, 변동된 코드를 가맹점별 POS 단말기로 실시간 다운로드 전파하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **명칭 정보 실시간 동기화 큐 적재 (`MNAMEM_T01` 트리거 및 백오피스 서비스)**: 백오피스 공통명칭 관리 화면에서 공통 명칭 코드(`mnamemtb`)를 변경 시, 시스템 감사 로그 `MMSLOGTB`가 자동 생성되며, POS 기기로의 명칭 데이터 실시간 동기화를 위해 변경된 명칭구분(`nm_fg`), 명칭코드(`nm_cd`), 대표명칭(`nm_rep`), 부명칭(`nm_sub`) 및 변경구분(`proc_fg`) 레코드가 `SSNAMETB`에 동기화 큐로 적재됩니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 명칭 코드 변경 레코드가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M28/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 명칭 코드 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 결제/화면의 다국어 및 명칭 매칭**: POS 단말기가 수신한 공통 명칭 데이터를 바탕으로, 화면상 결제 수단 명칭(카드, 현금, 간편결제), 거래 상태 명칭 및 영수증 하단 출력 코드의 한글 라벨 렌더링 정합성을 제공합니다."
    )

    data["tables"]["ssnametb"] = {
        "memo": ssnametb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (본사 및 프랜차이즈 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "nm_fg": "공통 명칭 대분류 구분 코드",
            "nm_cd": "공통 명칭 소분류 상세 코드",
            "nm_rep": "공통 명칭 한글 대표명 (라벨명)",
            "nm_sub": "공통 명칭 부가 속성 내용"
        },
        "memo_c": "공통 명칭 마스터(MNAMEMTB)의 백오피스 조율 변동 시 트랜잭션 단위로 동기화 큐에 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 주문 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 공통 명칭 설정 배포 모듈, 공통 코드/명칭 데이터 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. [트리거 MNAMEM_T01 연동] 백오피스 또는 본사 시스템에 의해 공통 명칭 코드 및 명칭이 등록/수정/삭제 처리되면, 이력이 남겨지고 전송 큐 테이블인 SSNAMETB를 통해 POS 단말기로 명칭 마스터 데이터를 전파 동기화합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 공통 명칭 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MNAMEM_T01 연동] 공통 명칭 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 상품 분류 명칭 및 과세/면세 구분 명칭을 공통 명칭 마스터에서 참조하여 결합하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 공통 명칭에 정의된 통화 단위 및 결제 구분 매개 변수와 대조하기 위해 시스템 환경설정 테이블과 연계됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 공통 명칭 코드를 개정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 기준 원재료 및 취급 분류 코드가 유효한 공통 명칭에 부합하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 매입 전표의 취급 명칭(예: 정산 구분, 입고 구분 등)을 한글 라벨로 매핑하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 창고 구분 및 재고 상태 구분 명칭을 한글로 조인 매칭 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 정산 유형 및 수불 상태 구분을 한글로 조인하여 매출 마진율과 비교 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 매출 상세 건에 기록되는 결제 수단 명칭(예: 카드, 현금, 간편결제 등)을 한글 라벨로 매핑 조회하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmlplktb",
                "description": "매장 POS별 PLU 단축키 설정 마스터 테이블. 단축키 분류 및 PLU 키에 대응하는 공통 명칭 정보를 매핑하여 POS 화면상에 렌더링하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 49. SSPRICTB MEMO AND RELATED TABLES
    ssprictb_memo = (
        "### 1. 테이블 개요\n"
        "POS 상품 단가/판매가 동기화 및 로그 테이블 (`SSPRICTB`).\n"
        "각 가맹점별(`MS_NO`) 각 상품(`GOODS_CD`)의 유효시작일(`START_DATE`), 유효종료일(`END_DATE`), 판매 단가 구분 및 판매가(`PRICE`) 정보가 추가되거나 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **상품 단가 정보 실시간 동기화 큐 적재 (`MPRICE_T01` 트리거)**: 매장별 상품 단가 마스터 테이블(`MPRICETB`)에 신규 단가 입력, 적용 시작일/종료일 기간 수정, 단가 금액 변동, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MPRICE_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 상품코드(`goods_cd`), 시작/종료일 및 판매 단가(`price`) 정보를 실시간으로 `SSPRICTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 상품 단가 변경 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M71/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 단가 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 실시간 결제 판매 정합성**: 고객이 POS 단말기 상에서 상품을 스캔 결제할 때 현재 시점(오늘 날짜)이 단가 유효 시작일(`start_date`)과 종료일(`end_date`) 범위 내에 존재하는 판매 단가(`price`)와 정확히 결부되어 올바른 매출 데이터가 형성되도록 보장합니다."
    )

    data["tables"]["ssprictb"] = {
        "memo": ssprictb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "goods_cd": "대상 상품코드 (자재 코드)",
            "start_date": "단가 적용 유효 시작 일자 (YYYYMMDD)",
            "end_date": "단가 적용 유효 종료 일자 (YYYYMMDD)",
            "price": "적용 상품 판매 단가 (판매 가격)"
        },
        "memo_c": "매장 상품 단가 마스터(MPRICETB) 테이블의 변동 시 MPRICE_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 상품 단가 배포 모듈, 매장별 상품 단가 관리 및 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mpricetb",
                "description": "매장별 상품 단가 마스터 테이블. 백오피스 변경에 의해 매장별 상품 단가(판매가, 시작/종료일 등)가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSPRICTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 단가 동기화 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MPRICE_T01 연동] 단가 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 단가가 변경된 상품의 한글 상품명, 규격, 바코드 등을 매칭 출력하기 위해 조인합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 소수점 단가 표시 기준 및 단가 강제 제어 유무 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 단가 구분(price_fg) 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 매장 단가를 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 단가를 부여할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 상품의 매입 단가와 현재 판매 단가(price)를 대조하여 상품별 마진율 시뮬레이션을 도출할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 상품의 재고 금액(재고 수량 * 단가)을 산출하고 재고 자산 평가서를 도출하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 선입선출법에 따른 입고 단가 흐름과 현재 적용 단가(price)를 비교 분석하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 적용된 실 매출 단가가 마스터 단가 동기화 테이블(SSPRICTB)에 정의된 유효기간의 판매가 규정과 부합하는지 정합성을 검증할 때 간접 참조됩니다."
            }
        ]
    }

    # 50. SSPROMTB MEMO AND RELATED TABLES
    sspromtb_memo = (
        "### 1. 테이블 개요\n"
        "POS 프로모션(행사/할인) 설정 동기화 및 로그 테이블 (`SSPROMTB`).\n"
        "가맹점별(`MS_NO`) 프로모션 할인/행사 정보(행사명, 할인 한도, 유효 기간 등)가 추가되거나 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **행사 설정 정보 실시간 동기화 큐 적재 (`MPROMA_T01` 트리거)**: 매장별 프로모션 마스터 테이블(`MPROMATB`)에 신규 프로모션 행사 추가, 할인 대상 품목 및 할인 조건(한도액, 할인율 등) 수정, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MPROMA_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 행사년도/코드(`promotion_year`/`promotion_cd`), 행사명칭(`promotion_nm`), 유효기간 및 한도/혜택 정보를 실시간으로 `SSPROMTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다. (참고: 프로모션 변경 시 구 레코드 삭제 후 신규 레코드를 삽입하는 정합성 큐 방식을 지원합니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 프로모션 변경 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M91/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 프로모션 행사 설정 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 결제 시 행사 할인 연산**: 고객 결제 시 단말기 로컬 메모리상에 적재된 프로모션 테이블(`Sspromtb`) 데이터를 조회하여 행사 유효 기간(`valid_from_date` ~ `valid_to_date`) 범위 내에 속하는 대상 품목의 금액/비율 할인을 차감 연산 처리합니다."
    )

    data["tables"]["sspromtb"] = {
        "memo": sspromtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "promotion_year": "프로모션 행사 적용 대상 년도 (YYYY)",
            "promotion_cd": "프로모션 행사 고유 식별 코드",
            "promotion_nm": "프로모션 행사 한글 명칭",
            "valid_from_date": "행사 적용 유효 시작 일자 (YYYYMMDD)",
            "valid_to_date": "행사 적용 유효 종료 일자 (YYYYMMDD)",
            "good_proc_fg": "할인 적용 대상 상품 분류 (0: 전체 품목, 1: 특정 품목 등)",
            "limit_type": "행사 구매/할인 한도 제한 방식 구분",
            "limit_amt": "행사 최대 제한 구매 금액 조건",
            "limit_qty": "행사 최대 제한 구매 수량 조건",
            "benefit_type": "행사 혜택 제공 방식 구분 (0: 정액 할인, 1: 정률 할인)",
            "benefit_amt": "혜택 적용 정액 할인 금액",
            "benefit_rate": "혜택 적용 정률 할인 비율 (예: 10.00% 등)",
            "rist_dc_amt": "행사 1회 적용 시 최대 수혜 가능 할인 한도액"
        },
        "memo_c": "매장 프로모션 마스터(MPROMATB) 테이블의 변동 시 MPROMA_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 프로모션 설정 배포 모듈, 매장별 프로모션 관리 및 행사 매출 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mpromatb",
                "description": "매장별 프로모션 마스터 테이블. 백오피스 변경에 의해 매장별 프로모션 행사 정보(행사명, 시작/종료일, 할인 유형 등)가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSPROMTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 프로모션 동기화 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MPROMA_T01 연동] 프로모션 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 프로모션 혜택 적용 대상 상품 품목들을 마스터에서 식별 대조하여 한글 상품명과 매칭하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 단위별 할인 최대 금액 제한 및 타 할인 수단(예: 임직원 할인, 통신사 제휴 등)과의 중복 적용 규칙 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 프로모션 혜택 구분(benefit_type), 행사 제한 구분(limit_type) 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 가맹점 프로모션 행사를 등록/조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 프로모션 대상에 맵핑할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 행사 진행 상품의 입고 매입 가격과 프로모션 할인가를 대조하여 행사 마진율을 사후 산정할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 행사로 인한 판매 급증 품목의 실시간 재고를 모니터링하고 발주 유도를 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 행사 기간 동안 판매된 자재의 선입선출 매입 원가를 평가하여 실질 프로모션 손익 분석 보고서를 구성하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 실제 적용된 프로모션 행사 할인 금액 및 결제 내역이 행사 동기화 테이블(SSPROMTB)에 정의된 유효 시작일/종료일 내의 조건과 부합하는지 정합성을 검증할 때 간접 참조됩니다."
            }
        ]
    }

    # 51. SSSCLSTB MEMO AND RELATED TABLES
    sssclstb_memo = (
        "### 1. 테이블 개요\n"
        "POS 매장별 상품 분류(대/중/소분류) 동기화 및 로그 테이블 (`SSSCLSTB`).\n"
        "각 가맹점의 상품 체계 분류(대분류 `LCLASS_CD`, 중분류 `MCLASS_CD`, 소분류 `SCLASS_CD`) 및 분류 한글명이 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **분류 체계 변경 시 실시간 동기화 큐 적재 (`MMLCLS_T01` / `MMMCLS_T01` / `MMSCLS_T01` 트리거)**: 매장 대분류 (`MMLCLSTB`), 매장 중분류 (`MMMCLSTB`), 매장 소분류 (`MMSCLSTB`) 원본 테이블 중 대/중/소분류의 명칭 및 코드가 추가, 수정, 삭제될 때 각각의 트리거가 자동 기동되어 부모 분류 명칭(대분류명, 중분류명)을 매핑 결합한 뒤 `SSSCLSTB` 큐에 실시간 레코드로 밀어 넣고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 분류 변경 레코드가 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M22/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 상품 분류 데이터셋을 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 상품 카테고리 트리 구축**: POS 단말기가 수신한 상품 분류 데이터를 바탕으로 화면상에 대/중/소분류 터치 버튼 및 상품 조회용 카테고리 트리 구조의 렌더링 정합성을 제공합니다."
    )

    data["tables"]["sssclstb"] = {
        "memo": sssclstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "lclass_cd": "상품 대분류 고유 코드",
            "lclass_nm": "상품 대분류 한글 명칭",
            "mclass_cd": "상품 중분류 고유 코드",
            "mclass_nm": "상품 중분류 한글 명칭",
            "sclass_cd": "상품 소분류 고유 코드",
            "sclass_nm": "상품 소분류 한글 명칭"
        },
        "memo_c": "대/중/소분류 마스터 테이블의 변동 시 MMLCLS_T01, MMMCLS_T01, MMSCLS_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 상품 분류 배포 모듈, 매장별 대/중/소분류 마스터 조회 및 상품 마스터 조인 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmlclstb",
                "description": "매장 대분류 마스터 테이블. 백오피스 변경에 의해 대분류 코드/명칭이 등록/수정/삭제 처리되면 트리거가 감지하여 변경 분을 SSSCLSTB 동기화 큐에 적재합니다."
            },
            {
                "table_name": "mmmclstb",
                "description": "매장 중분류 마스터 테이블. 백오피스 변경에 의해 중분류 코드/명칭이 등록/수정/삭제 처리되면 트리거가 감지하여 변경 분을 SSSCLSTB 동기화 큐에 적재합니다."
            },
            {
                "table_name": "mmsclstb",
                "description": "매장 소분류 마스터 테이블. 백오피스 변경에 의해 소분류 코드/명칭이 등록/수정/삭제 처리되면 트리거가 감지하여 변경 분을 SSSCLSTB 동기화 큐에 적재합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 원장 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 상품 분류 동기화 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MMSCLS_T01 연동] 상품 분류 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 분류에 매핑된 상품의 한글 상품명, 규격 등을 매칭 출력하기 위해 조인합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 상품 분류 최대 단계 및 자재 분류 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 상품 대분류 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 상품 대/중/소분류 체계를 수정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 상품 대/중/소분류에 매핑할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 각 상품 대/중/소분류별 매입/발주 실적 및 공급사 정산 금액을 대조 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 상품 대/중/소분류 카테고리별 실시간 수불 재고와 회전율을 대시보드에 매핑 출력하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 상품 분류별 입고 원가 흐름과 마진율 평가를 위해 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 매출 상세 건에 기록된 상품의 분류(대/중/소)별 매출 비중을 분석 및 통계 보고서로 도출할 때 간접 참조됩니다."
            }
        ]
    }

    # 52. SSSUBMTB MEMO AND RELATED TABLES
    sssubmtb_memo = (
        "### 1. 테이블 개요\n"
        "POS 부가메뉴(옵션/세트구성) 설정 동기화 및 로그 테이블 (`SSSUBMTB`).\n"
        "가맹점별(`MS_NO`) 상품에 부가되는 서브 메뉴 및 세트 선택 옵션 정보(분류 그룹 `SUB_GROUP_CD`, 부가메뉴 코드 `SUB_MENU_CD`, 추가 금액 `UPCHARGE_UPRICE`, 연계 상품 `GOODS_CD`)가 추가되거나 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **부가메뉴 설정 정보 실시간 동기화 큐 적재 (`MSUBMN_T01` 트리거)**: 매장별 부가메뉴 마스터 테이블 (`MSUBMNTB`)에 신규 서브 옵션/토핑/세트 선택 항목이 추가되거나 명칭, 표시순서, 단가 등이 수정/삭제(`AFTER INSERT/UPDATE/DELETE`)될 때, `MSUBMN_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 부가그룹/메뉴코드(`sub_group_cd`/`sub_menu_cd`), 명칭(`sub_menu_nm`), 추가금액(`upcharge_uprice`) 및 연계 상품코드(`goods_cd`) 정보를 실시간으로 `SSSUBMTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 부가메뉴 및 세트 선택 설정이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M13/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 부가메뉴 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 결제 시 옵션/세트 구성 처리**: 고객 결제 시 단말기 로컬 메모리에 적재된 부가메뉴 테이블(`Sssubmtb`)을 조회하여 얼음양/샷추가/사이드변경 등의 옵션 단가 연산 및 세트 결합 품목의 정상 판매 처리를 수행합니다."
    )

    data["tables"]["sssubmtb"] = {
        "memo": sssubmtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "sub_group_cd": "부가메뉴 소속 그룹 코드 (예: 샷추가 그룹, 토핑 그룹 등)",
            "sub_menu_cd": "부가메뉴 세부 옵션 코드",
            "sub_menu_nm": "부가메뉴 세부 옵션 한글 명칭",
            "display_order": "POS 화면상 표시 정렬 순서",
            "stock_fg": "부가메뉴 성격 구분 (1: 단순속성, 2: 추가금액적용, 3: 세트구성품)",
            "goods_cd": "부가메뉴에 매핑된 실제 자재/단품 상품코드",
            "upcharge_uprice": "부가메뉴 선택 시 부과되는 추가 금액 (Upcharge 단가)"
        },
        "memo_c": "매장 부가메뉴 마스터(MSUBMNTB) 테이블의 변동 시 MSUBMN_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 부가메뉴 및 세트 설정 배포 모듈, 매장별 부가옵션 설정 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "msubmntb",
                "description": "매장별 부가메뉴 마스터 테이블. 백오피스 변경에 의해 매장별 부가메뉴(옵션/추가메뉴 등)가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSSUBMTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 부가메뉴 동기화 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MSUBMN_T01 연동] 부가메뉴 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 부가메뉴/세트 구성품에 매핑된 상품의 한글 상품명, 규격, 바코드 등을 매칭 출력하기 위해 조인합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 부가메뉴 최대 수량 제한 및 옵션 화면 팝업 기동 조건 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 부가메뉴 형태(옵션, Upcharge, 세트메뉴 등) 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 매장 부가메뉴 배치를 변경 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 부가메뉴에 매핑할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 추가 금액(Upcharge)에 대한 원재료 매입 정산 실적을 롤업 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 부가 메뉴(예: 샷추가 원두 재고, 휘핑크림 등) 재고 감산과 유통기한 대조를 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 부가 메뉴의 마진율 및 수불 현황을 선입선출 원가 단위로 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 부가메뉴(옵션/Upcharge)를 추가 선택하여 결제 처리한 매출 상세 금액 정합성 분석 시 간접 참조됩니다."
            }
        ]
    }

    # 53. SSTOTMTB MEMO AND RELATED TABLES
    sstotmtb_memo = (
        "### 1. 테이블 개요\n"
        "POS 합산메뉴(콤보/묶음상품) 설정 동기화 및 로그 테이블 (`SSTOTMTB`).\n"
        "가맹점별(`MS_NO`) 상품에 부가되는 세트/콤보/묶음 메뉴 정보(합산메뉴 코드 `TOT_MENU_CD`, 합산메뉴 한글명 `TOT_MENU_NM`)가 추가되거나 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **합산메뉴 설정 정보 실시간 동기화 큐 적재 (`MTOTMN_T01` 트리거)**: 매장별 합산메뉴 마스터 테이블 (`MTOTMNTB`)에 신규 콤보/묶음 메뉴 항목이 추가되거나 명칭 등이 수정/삭제(`AFTER INSERT/UPDATE/DELETE`)될 때, `MTOTMN_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 합산메뉴코드(`tot_menu_cd`), 합산메뉴명칭(`tot_menu_nm`) 정보를 실시간으로 `SSTOTMTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 합산메뉴 구성 설정이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M14/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 합산메뉴 변경 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 결제 시 합산메뉴 처리**: 고객 결제 시 단말기 로컬 메모리에 적재된 합산메뉴 테이블 (`Sstotmtb`)을 조회하여 콤보/묶음 결합 상품의 정상 합산/분할 판매 처리를 수행합니다."
    )

    data["tables"]["sstotmtb"] = {
        "memo": sstotmtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "tot_menu_cd": "합산메뉴 (콤보/세트) 고유 식별 코드",
            "tot_menu_nm": "합산메뉴 (콤보/세트) 한글 명칭"
        },
        "memo_c": "매장 합산메뉴 마스터(MTOTMNTB) 테이블의 변동 시 MTOTMN_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 합산메뉴 및 콤보 구성 배포 모듈, 매장별 합산 메뉴 관리 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mtotmntb",
                "description": "매장별 합산메뉴 마스터 테이블. 백오피스 변경에 의해 매장별 합산메뉴(세트/콤보메뉴 등)가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSTOTMTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 합산메뉴 동기화 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MTOTMN_T01 연동] 합산메뉴 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 합산/콤보 구성품에 매핑된 개별 상품의 한글 상품명, 규격, 바코드 등을 매칭 출력하기 위해 조인합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 콤보/묶음 메뉴 최대 갯수 제한 및 합산 가격 분배 옵션 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 합산메뉴 구분 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 매장 합산메뉴 배치를 변경 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 합산 메뉴 내 구성품에 매핑할 상품 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 콤보 메뉴로 묶인 상품군의 원재료 매입 정산 실적을 롤업 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 합산 메뉴 판매 시 차감되는 단품 상품 재고 감산과 유통기한 대조를 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 합산/묶음 메뉴의 마진율 및 수불 현황을 선입선출 원가 단위로 평가하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 합산메뉴(콤보/묶음)를 추가 선택하여 결제 처리한 매출 상세 금액 정합성 분석 시 간접 참조됩니다."
            }
        ]
    }

    # 54. SSUSERTB MEMO AND RELATED TABLES
    ssusertb_memo = (
        "### 1. 테이블 개요\n"
        "POS 사용자/근무자 마스터 동기화 및 로그 테이블 (`SSUSERTB`).\n"
        "각 가맹점 내부에서 근무하는 사용자(사원, 캐셔 등)의 권한(`order_fg`), 사원 명칭(`user_nm`), 사원 번호(`emp_id`), MSR용 사원 로그인 카드 번호(`emp_card_no`) 및 사용 유무(`acct_enable`) 정보가 추가되거나 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **근무자 설정 정보 실시간 동기화 큐 적재 (`MUSERS_T01` 트리거)**: 가맹점 사용자/근무자 마스터 테이블 (`MUSERSTB`)에 신규 근무자 추가, 활성 여부 변경, 삭제(`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MUSERS_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 사원번호(`emp_id`), 사원명칭(`user_nm`), 카드번호(`emp_card_no`) 및 주문권한구분(`order_fg`) 정보를 실시간으로 `SSUSERTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다. (참고: 퇴사 등으로 사용자 계정이 비활성화되면 'D' 처리구분으로 POS 전파됩니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 근무자 권한 변경 내역이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M15/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 사원 로그인 및 권한 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 로그인 및 보안 등급 제어**: POS 단말기 기동 시 수신된 캐셔 사원 정보(`Ssusertb`) 및 MSR 사원카드 정보를 대조하여 본인 확인 로그인을 수행하고, 결제 취소나 할인 승인 시 해당 근무자가 권한 규정(`order_fg`)에 부합하는지 실시간 검증합니다."
    )

    data["tables"]["ssusertb"] = {
        "memo": ssusertb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제/퇴사)",
            "emp_id": "매장 근무 사원 고유 식별 번호 (4자리)",
            "user_nm": "근무 사원 한글 성명",
            "emp_card_no": "사원 로그인 MSR 카드번호",
            "order_fg": "주문/판매 처리 권한 구분 (0: 일반주문, 1: POS+웹, 2: POS만, 3: 웹만)",
            "user_type": "사용자 성격 유형 (POS 동기화 기본값: 0)"
        },
        "memo_c": "매장 근무자 마스터(MUSERSTB) 테이블의 변동 시 MUSERS_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 근무자 권한 배포 모듈, 매장 사원 등록 및 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "muserstb",
                "description": "가맹점 사용자/근무자 마스터 테이블. 백오피스 변경에 의해 매장 근무자(사원, 캐셔 등)가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSUSERTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 근무자 동기화 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MUSERS_T01 연동] 근무자 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 상품 배포 담당 캐셔의 권한 설정 여부를 대조하거나 사원 구매 혜택 상품 목록을 필터링하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 단말기 근무자 비밀번호 오류 횟수 제한 및 자동 로그아웃 시간 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 사용자 등급 구분(점장, 캐셔, 관리자 등) 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 특정 상품 카테고리를 관리하는 사원 담당 코드가 유효하게 존재하는지 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 발주 및 매입 처리를 주도한 현장 발주 사원의 실명 정보를 매칭하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 실사 재고를 카운트하여 재고 조정을 승인한 실사 담당 근무자의 식별 정보를 결합하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 선입선출 자재 입고 전표를 최종 승인 처리한 입고 책임 사원 정보를 매칭하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 결제할 때 POS를 조작한 판매 캐셔(emp_id) 정보를 매출 전표와 대조하여 캐셔별 정산액(시출금 대비 과부족액)의 정합성을 검증할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmlplktb",
                "description": "매장 POS별 PLU 단축키 설정 마스터 테이블. 사원별 맞춤 PLU 단축키 화면 레이아웃 권한을 동적 제어하기 위해 사원 정보와 연계됩니다."
            }
        ]
    }

    # 55. SSVANSTB MEMO AND RELATED TABLES
    ssvanstb_memo = (
        "### 1. 테이블 개요\n"
        "POS VAN 카드코드 - 표준 카드코드 매핑 동기화 및 로그 테이블 (`SSVANSTB`).\n"
        "각 VAN사(KICC, NICE 등) 별로 사용하는 신용카드 고유 코드 (`VAN_CARD_CD`)를 시스템 내부의 표준 신용카드 코드 (`STD_CARD_CD`, 예: BC카드, 국민카드 등)로 변환/매핑하는 데이터가 추가되거나 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐 (Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **카드 매핑 정보 실시간 동기화 큐 적재 (`MVANST_T01` 트리거)**: VAN사별 카드 매핑 마스터 테이블 (`MVANSTTB`)에 신규 매핑 룰 추가, 카드사 변동, 삭제 (`AFTER INSERT/UPDATE/DELETE`)가 발생할 때, `MVANST_T01` 트리거가 실행되어 일련번호 (`log_seq`), 처리구분 (`proc_fg`), VAN코드 (`van_cd`), VAN카드코드 (`van_card_cd`) 및 표준카드코드 (`std_card_cd`) 정보를 실시간으로 `SSVANSTB` 큐에 인서트하고 감사 로그 (`MMSLOGTB`)에도 기록을 보관합니다. (참고: 매핑 관계는 매장별 설정 사항이 아닌 공통 인프라 설정이므로 매장코드 기본값 '000000'으로 로깅됩니다.)\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 VAN 카드 매핑 룰이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈 (Telex M23/S10 Mapper)이 최종 전송 시퀀스 (`LastSeq`)와 비교하여 새로 큐에 쌓인 매핑 정보 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 카드 결제 처리 정합성**: 고객이 POS 단말기 상에서 IC 카드를 삽입/승인하여 수신된 VAN사의 카드사 식별 부호를 표준 신용카드 대조 원장 (`Ssvanstb`)을 참조해 표준 카드사명으로 한글 변환하고 매출 상세에 기록해 영수증을 출력합니다."
    )

    data["tables"]["ssvanstb"] = {
        "memo": ssvanstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (공통 설정 기본값: 000000)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "van_cd": "VAN사 식별 코드 (예: KICC, NICE 등)",
            "van_card_cd": "VAN사 전용 신용카드 식별 코드 (4자리)",
            "std_card_cd": "시스템 표준 신용카드사 식별 코드 (3자리)"
        },
        "memo_c": "VAN사별 카드 매핑 마스터(MVANSTTB) 테이블의 변동 시 MVANST_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 결제 카드사 매핑 배포 모듈, VAN 카드코드 매핑 관리 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mvansttb",
                "description": "VAN사별 카드 매핑 마스터 테이블. 백오피스 변경에 의해 VAN사 카드코드 매핑 설정이 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSVANSTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 카드 매핑 동기화 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MVANST_T01] 카드 매핑 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 제휴 카드로 결제 시 할인 적용 대상 품목군 유효성 필터링을 검증하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 승인 단말기의 다중 VAN 이중화 설정 및 은련(CUP)/해외 카드 표준 승인 설정 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 신용카드 표준 코드(BC, KB 등), VAN사 구분 코드 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 VAN 카드코드 매핑 룰을 변경 조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 해외 결제용 카드 매핑 시 본사 지정 표준 상품 정보와 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 물류 대금 수납 시 특정 카드 매입사를 활용해 자동 계좌이체하거나 카드 수수료율을 비교 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 제휴 카드 프로모션 할인에 따른 행사 품목의 재고 소진율을 사후 비교 평가하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 카드 매핑 유형에 따른 정산 주기와 입고 대금 결제 회전율을 조인하여 연계 평가하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객이 카드로 결제 승인을 진행할 때 영수증 매출 상세에 반환된 매입사 코드(van_card_cd)를 표준 신용카드 코드(std_card_cd)로 결합 가공하여 카드사별 실매출 실적 보고서를 도출할 때 조인 연계됩니다."
            }
        ]
    }

    # 56. SSVNDRTB MEMO AND RELATED TABLES
    ssvndrtb_memo = (
        "### 1. 테이블 개요\n"
        "POS 거래처(공급사) 마스터 동기화 및 로그 테이블 (`SSVNDRTB`).\n"
        "가맹점별(`MS_NO`) 거래를 맺고 물품을 직납받거나 정산하는 외부 거래처/협력업체(명칭 `VENDOR_NM`, 사업자번호 `BS_NO`, 주소 `BS_ADDR`, 계좌번호 `ACCOUNT_NO` 등)가 추가되거나 변경될 때, 변경 데이터를 POS 단말기로 실시간 다운로드 전송하기 위해 변경 사항 발생 이력을 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **거래처 정보 실시간 동기화 큐 적재 (`MVNDRM_T01` 트리거)**: 매장별 거래처 마스터 테이블 (`MVNDRMTB`)에 신규 거래처 추가, 사업자/주소 정보 수정, 삭제/사용중단(`AFTER INSERT/UPDATE/DELETE`)이 발생할 때, `MVNDRM_T01` 트리거가 실행되어 일련번호(`log_seq`), 처리구분(`proc_fg`), 거래처코드(`vendor`), 거래처명(`vendor_nm`), 대표자명(`president_nm`), 사업자등록번호(`bs_no`), 주소(`bs_addr`) 및 은행/계좌 정보(`bank_cd`/`account_no`) 등의 정보를 실시간으로 `SSVNDRTB` 큐에 인서트하고 감사 로그(`MMSLOGTB`)에도 기록을 보관합니다.\n"
        "* **POS 실시간 연동 연계**: 이 테이블에 신규 거래처 변동 사항이 입력되면, 대기 중이던 POS 전송 데몬 및 서버 인터페이스 모듈(Telex M39/S10 Mapper)이 최종 전송 시퀀스(`LastSeq`)와 비교하여 새로 큐에 쌓인 거래처 마스터 데이터를 개별 매장의 POS 단말기 메모리로 즉시 전송 반영시킵니다.\n"
        "* **POS 매입 및 원자재 검수 처리**: 가맹점 현장 근무자가 POS 단말기나 모바일 핸디 단말기 상에서 거래처로부터 직납받은 원자재나 식자재 매입 수량을 검수 등록할 때, 등록된 거래처 마스터 코드(`vendor`) 규정과 대조하여 올바른 거래처별 매입 전표가 생성되도록 보장합니다."
    )

    data["tables"]["ssvndrtb"] = {
        "memo": ssvndrtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제/사용안함)",
            "vendor": "거래처(공급사) 고유 식별 코드",
            "vendor_nm": "거래처 상호 및 한글 명칭",
            "president_nm": "거래처 대표자명",
            "corp_fg": "법인 구분 (0: 개인사업자, 1: 법인사업자 등)",
            "corp_no": "주민등록번호 또는 법인등록번호",
            "bs_no": "사업자 등록 번호 (10자리)",
            "chain_no": "체인 및 계열 본사 분류 코드",
            "bs_type": "거래처 업태 (예: 제조, 도소매 등)",
            "bs_kind": "거래처 종목 (예: 식료품, 자재 등)",
            "zip_no": "거래처 소재지 우편번호",
            "bs_addr": "거래처 사업장 주소 (기본 주소)",
            "bs_addr_bunji": "거래처 사업장 상세 주소 (번지/건물명 등)",
            "tel_no": "거래처 대표 전화번호",
            "fax_no": "거래처 팩스 번호",
            "hp_no": "거래처 담당자 휴대전화 번호",
            "e_mail": "전자세금계산서 수신 이메일 주소",
            "account_nm": "송금 수납 계좌 예금주명",
            "bank_cd": "거래 은행 기관 코드 (3자리)",
            "account_no": "송금 수납 계좌 번호",
            "remark": "거래처 관련 종합 비고 및 특이사항",
            "create_date": "거래처 최초 등록 일자 및 시간",
            "create_id": "거래처 최초 등록자 ID",
            "last_date": "최종 정보 수정 일자 및 시간",
            "last_id": "최종 정보 수정자 ID",
            "vendor_fg": "거래처 성격 구분 (0: 매입처, 1: 매출처 등)",
            "sub_inv_fg": "부가세 포함 여부 및 매입 형태 구분",
            "bns_tax_yn": "과세 사업자 여부 (Y/N)",
            "bur_bns_no": "소속 관할 세무서 코드",
            "contact_ps_nm": "거래처 실무 담당자 성명",
            "contact_phone_no": "실무 담당자 연락처",
            "tax_bill_fg": "세금계산서 발행 구분 (0: 종이, 1: 전자 등)",
            "ven_use_fg": "거래처 사용 여부 구분 (0: 사용안함, 1: 사용함)",
            "erp_if_info": "ERP 연동 상태 정보 및 인터페이스 매핑 키",
            "contact_tel_no": "담당자 비상 연락망 전화번호"
        },
        "memo_c": "매장 거래처 마스터(MVNDRMTB) 테이블의 변동 시 MVNDRM_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 매출 검증을 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 거래처 마스터 배포 모듈, 매장 거래처 등록 및 입고 정산 조회 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mvndrmtb",
                "description": "매장별 거래처 마스터 테이블. 백오피스 변경에 의해 매장별 거래처(공급사, 매입처 등)가 등록/수정/삭제 처리되면, 트리거가 감지하여 변경 분을 전송용 큐 테이블(SSVNDRTB)에 적재하는 원천 마스터입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 상태를 확인하여 해당 점포의 POS 기기로 거래처 동기화 데이터를 필터 배포하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MVNDRM_T01 연동] 거래처 변경 사항이 전송 큐를 통해 POS 단말기로 전송 완료되거나 에러가 발생한 연동 인터페이스의 이력을 추적 기록하는 테이블입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 상품의 주 공급처(기본 매입 거래처)를 지정하고, 발주서 작성 시 거래처명과 결합 매핑하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 직납 거래처의 마감 정산일(월말, 수시 등) 및 매입 세금 신고 옵션 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 거래처 유형 구분(물류 공급사, 경비 매입처 등) 및 처리 구분(proc_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 매장 거래처 대장을 등록/조정한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 지정 표준 상품의 OEM 제조사 및 본사 지정 매입 공급처 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점이 거래처를 지정하여 발주/입고 처리를 진행하고 최종 물류 정산 내역을 산출할 때, 해당 매입 거래처의 실명(상호명)을 매핑 조회하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 거래처로부터 납품받은 재고 금액의 정산 비율을 산출하고 재고 자산 평가서를 도출하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 선입선출법에 따른 입고 단가 흐름과 납품을 담당한 거래처의 공급 원가 변동 추이를 분석하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 거래처별 납품 상품의 실판매 성과 및 행사 기여도를 대조 분석하여 거래처별 판매 수수료를 정산 연산할 때 간접 참조됩니다."
            }
        ]
    }

    # 57. STABLETB MEMO AND RELATED TABLES
    stabletb_memo = (
        "### 1. 테이블 개요\n"
        "매장 일자별 테이블 매출 집계 테이블 (`STABLETB`).\n"
        "점포 내 개별 구역(층/그룹 `GROUP_ID`) 및 개별 테이블 번호(`TABLE_NO`)별로 특정 영업 조회 일자(`SALE_DATE`) 동안 발생한 건수, 금액, 할인, 세액 및 내/외국인 고객수 통계를 누적 합산하여 보관하는 일별 매출 집계 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **매출 발생 시 자동 집계 처리 (`STRNHD_T01` 트리거 및 `SUB_STABLE_P` 프로시저)**: 포스 승인에 의해 실시간 매출 거래가 완료되어 매출 헤더 원장(`STRNHDTB`)에 신규 데이터가 인서트(`AFTER INSERT`)되면, 연계된 `STRNHD_T01` 트리거가 가동되어 `SUB_STABLE_P` 프로시저를 직접 호출합니다.\n"
        "* **실시간 누적 연산**: 프로시저 내부에서는 해당 영업일자 및 테이블 번호 조건에 해당하는 `STABLETB` 레코드의 매출 합계(`sale_tot`), 순매출(`sale_amt`), 할인액(`dc_amt`), 부가세(`vat_amt`), 고객수(`native_cnt`/`foreign_cnt`) 등을 실시간으로 증감(`SET +=`) 시키고, 당일 최초 매출인 경우 레코드를 자동 신규 인서트(Upsert 구조) 처리합니다.\n"
        "* **테이블 영업 분석**: 백오피스 매출 현황판 및 대시보드 화면에서 테이블별 영업 효율성, 구역별 테이블 회전율, 특정 요일 및 일자별 테이블 매출 기여도를 한눈에 가독성 있게 시뮬레이션하고 비교하는 통계 소스로 사용됩니다."
    )

    data["tables"]["stabletb"] = {
        "memo": stabletb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "sale_date": "영업 대상 조회 일자 (YYYYMMDD)",
            "group_id": "매장 내부 구역/층 고유 식별 ID (기본값: 0)",
            "table_no": "매장 내부 테이블 번호 (기본값: 000)",
            "chain_no": "체인 및 계열사 분류 코드",
            "sale_cnt": "해당 테이블에서 발생한 총 결제/주문 건수",
            "sale_tot": "해당 테이블 일일 총 매출액 (과세 + 면세 + 부가세)",
            "sale_amt": "해당 테이블 일일 순 매출액 (총매출 - 할인 - 부가세 등)",
            "dc_amt": "해당 테이블 일일 총 할인 적용 금액",
            "native_cnt": "해당 테이블 일일 내국인 방문 고객수 합산",
            "foreign_cnt": "해당 테이블 일일 외국인 방문 고객수 합산",
            "vat_amt": "해당 테이블 일일 발생 부가세액 합계"
        },
        "memo_c": "매출 헤더(STRNHDTB)에 신규 매출 발생 시 STRNHD_T01 트리거가 SUB_STABLE_P 프로시저를 호출하여 자동 합산 생성합니다.",
        "memo_u": "영업일 인계마감 정정 및 당일 취소 전표 정산 처리에 의해 해당 일자 테이블 실적이 가감 업데이트됩니다.",
        "memo_d": "가맹점 일일 마감 정산 이력 증빙 원장이므로 임의 삭제가 원천 차단됩니다.",
        "memo_r": "테이블별 매출 현황 조회 및 테이블 회전 기여도 통계 보고서 작성 시 메인 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. [트리거 STRNHD_T01 연동] 포스에서 거래가 발생하여 매출 정보가 인서트되면, 트리거가 작동하여 SUB_STABLE_P 프로시저를 통해 매출 금액과 건수 정보를 테이블별 매출 집계 테이블(STABLETB)에 실시간으로 집계 및 누적 처리합니다."
            },
            {
                "table_name": "mmstbltb",
                "description": "매장 테이블 배치 설정 마스터. 실제 매장에 배치된 물리적인 테이블 번호 및 테이블 명칭을 매치하여 매출 집계가 유효한 테이블에서 발생했는지 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "mmsflrtb",
                "description": "매장 층/구역 마스터 테이블. 테이블이 소속된 구역명(예: 1층, 테라스석 등)을 매칭하여 구역 단위별 매출액 합산 조회를 처리하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 소속 정보(체인 번호)를 확인하여 본사 매출 롤업 및 가맹점 단위별 매출 통계를 집계할 때 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 테이블에서 주문된 품목들의 카테고리를 확인하여 테이블별 주력 소비 상품군(음료, 주류 등) 선호도 통계를 도출할 때 간접 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 테이블 배치 사용 유무 및 테이블 세부 서비스료(봉사료/팁) 부과 여부 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 테이블 그룹 성격 및 처리 상태 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 테이블 매출 정정 처리를 진행한 사원의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 테이블 매출 실적에 따른 원자재 소진액과 마진율 시뮬레이션을 도출할 때 자재 단가 비교용으로 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 테이블 점유 시간 동안 소모된 식자재 재고 차감액을 재고 금액으로 변환 대조할 때 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 선입선출 매입 원가를 대조하여 테이블별 순수 이익 금액을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 특정 테이블에서 주문된 세부 품목별 단가와 수량을 역추적하여 매출 상세 내역과 테이블 매출 집계 원장의 정합성을 사후 검증할 때 조인 연계됩니다."
            }
        ]
    }

    # 58. STCKHITB MEMO AND RELATED TABLES
    stckhitb_memo = (
        "### 1. 테이블 개요\n"
        "선입선출 입고대장 테이블 (`STCKHITB`).\n"
        "매장별 원부자재 및 상품의 선입선출(First-In-First-Out) 원가 평가를 위해 마감 대상 월(`STOCK_MONTH`), 매장코드(`MS_NO`), 입고일자(`PROC_DATE`), 상품코드(`GOODS_CD`), 입고단가(`COST`)별로 기초수량, 매입수량, 판매수량, 조정수량 및 기말잔여재고수량(`END_QTY`)을 월 단위로 보관 관리하는 선입선출 수불 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **매입 검수 확정 시 자동 입고 등록 (`OBSLPD_T02` 트리거)**: 가맹점에서 원자재 매입/검수 확정이 완료되어 매입/발주 상세 내역 테이블(`OBSLPDTB`)에 데이터가 추가/변경(`AFTER INSERT/UPDATE`)되면, `OBSLPD_T02` 트리거가 작동하여 해당 자재 품목, 입고 단가 및 매입 수량(`purch_qty`)을 `STCKHITB` 원장의 매입 레코드로 실시간 연계 적재합니다.\n"
        "* **선입선출 월 마감 처리 (`Sp_SUB_STOCK_FIFO_MAIN_P` / `Sp_SUB_STOCK_FIFO_PROC_P` 프로시저)**: 가맹점 월 마감 시 메인 배치 프로시저가 동작하여, 당월 발생한 매출 상세 레시피 소진량과 기타 폐기/조정 수량을 차감 연산하고, 선입선출 규칙에 따라 남은 이월 수량(`end_qty`)을 산출하여 다음 달 기초 수량(`start_qty`)으로 자동 이월 처리합니다.\n"
        "* **수불 및 마진 분석**: 선입선출 단가 평가를 거친 수량에 단가를 곱하여 월별 기말 재고 평가 금액을 확정하고, 매출 원가 및 가맹점 원가율 분석 레포트를 도출하는 기초 자료로 활용됩니다."
    )

    data["tables"]["stckhitb"] = {
        "memo": stckhitb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "rowid": "시스템 생성 고유 레코드 식별 행 일련번호",
            "stock_month": "선입선출 집계 대상 마감 년월 (YYYYMM)",
            "ms_no": "매장코드 (점포 코드)",
            "proc_date": "원부자재 입고 및 수불 처리 일자 (YYYYMMDD)",
            "goods_cd": "대상 원자재 및 상품코드",
            "cost": "원자재 입고 원가 단가 (추가 비용 제외)",
            "extra_cost": "원자재 입고 시 발생한 부대 추가 비용",
            "org_stock_month": "최초 입고 처리된 원천 마감 년월 (YYYYMM)",
            "obsl_key_bill_no": "매입 전표 연계 고유 거래 키 (주문일+매장+전표+라인 등)",
            "hit_seq": "입고 순번 식별자",
            "limit_qty": "선입선출 유효 제한 수량",
            "start_qty": "당월 기초 이월 재고 수량",
            "purch_qty": "당월 신규 매입 수량",
            "re_purch_qty": "당월 매입 반품/취소 수량",
            "sale_qty": "당월 판매(레시피 분해 소진) 수량",
            "re_sale_qty": "당월 판매 반품/환불 수량",
            "move_in_qty": "타 가맹점으로부터의 원자재 이동 입고 수량",
            "move_out_qty": "타 가맹점으로의 원자재 이동 출고 수량",
            "pl_adjust_qty": "재고실사에 따른 실사 증가(+) 조정 수량",
            "mi_adjust_qty": "재고실사에 따른 실사 감소(-) 조정 수량",
            "disuse_qty": "유통기한 경과 및 손실에 따른 폐기 수량",
            "end_qty": "당월 말 최종 잔여 이월 재고 수량 ( start + purch - sale ... )",
            "stock_yn": "마감 처리 구분 여부 (N: 일반, Y: 이월완료, A: 가마감)",
            "stock_remark": "선입선출 정산 관련 예외 처리 비고",
            "create_dtime": "레코드 최초 생성 일시 (YYYYMMDDHH24MISS)",
            "last_dtime": "레코드 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "use_price_yn": "원가 금액 수불 처리 활용 여부 (Y/N)",
            "trbk_dtime": "원격 백업 및 이관 연동 처리 일시"
        },
        "memo_c": "매입상세(OBSLPDTB) 확정 등록 시 OBSLPD_T02 트리거에 의해 실시간 매입분이 적재되거나 월 마감 프로시저 실행 시 자동 빌드됩니다.",
        "memo_u": "선입선출 월 마감 배치(Sp_SUB_STOCK_FIFO_MAIN_P) 및 실사재고 보정 입력에 의해 수불 항목 수량과 기말량이 업데이트됩니다.",
        "memo_d": "가맹점 선입선출 수불 이력 및 세무 증빙의 중추 장부이므로 임의 삭제가 영구 제한됩니다.",
        "memo_r": "수불대장 조회, 월 수불 총괄표 및 선입선출 기말 자산 평가서 작성 시 기초 데이터로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "obslpdtb",
                "description": "매장 매입/발주 상세 내역 테이블. [트리거 OBSLPD_T02 연동] 가맹점에서 원자재 발주/매입 검수 확정이 이루어지면, 트리거에 의해 해당 입고 상품과 단가 및 수량 정보가 선입선출 입고대장(STCKHITB)에 기초 매입분(purch_qty, cost)으로 자동 연계 적재됩니다."
            },
            {
                "table_name": "stckiotb",
                "description": "매장 재고 마감 처리 상태 원장 테이블. 월 마감 실행 시 당월 입고 원장의 가마감 및 최종 이월 처리 상태를 원격 통제 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "stckertb",
                "description": "재고 마감 에러 로그 테이블. 선입선출 배치 연산 과정 중 원가 단가 미지정이나 음수 재고 등의 결함 발생 시, 입고 대장의 해당 내역을 에러 로그와 대조 규명하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점 단위별 선입선출 환경 매개 변수를 확인하여 개별 점포의 기말 재고 평가 및 이월 정산 규칙을 적용할 때 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 입고된 자재 상품의 한글 명칭, 단위, 세액 구분 및 상품 카테고리를 결합하여 수불 보고서에 렌더링하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 선입선출 마감 허용 최소 수불 연수 및 이월 단가 반올림 소수점 자리 등의 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 입고 구분 및 마감 상태 플래그(stock_yn)에 대응하는 한글 상태 코드를 조인하여 매칭하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 월 마감 승인이나 실사 재고 보정 조정을 등록한 담당 사용자의 실명 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 입고 대장에 기록되는 원자재 코드가 본사에서 표준 등록한 규격 자재 정보에 부합하는지 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 월중 실시간 재고 대장과 선입선출 기말 재고 수량(end_qty) 간의 편차를 조정하고 재고 자산 평가 정합성을 일치시키기 위해 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매출 발생 시 판매된 단품 상품의 레시피 소진 규정에 근거하여, 입고대장(STCKHITB)에서 선입선출법에 따라 해당 원자재 재고 수량(sale_qty)을 차감하고 매출원가를 정산할 때 간접 연계됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 재고 강제 조정이나 월 마감 임의 정정 시 보안성 감사를 위해 감사 로그에 이력을 기록하고 연계됩니다."
            }
        ]
    }

    # 59. STCKERTB MEMO AND RELATED TABLES
    stckertb_memo = (
        "### 1. 테이블 개요\n"
        "재고 마감 오류/에러 로그 테이블 (`STCKERTB`).\n"
        "가맹점 선입선출(FIFO) 월 재고 마감 또는 취소 처리를 수행하는 도중 발생한 시스템 예외 오류, 데드락, 원가 불일치 예외 및 마감 취소 사유 등의 상세 텍스트 이력을 로그 식별번호(`PROC_SEQ`)와 대상 년월(`STOCK_MONTH`) 단위로 로깅 관리하는 장비/배치 오류 감사 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **오류/취소 발생 시 기록 적재 (`SUB_STOCK_FIFO_ERR_P` 프로시저)**: 본사/가맹점 월 재고 마감 배치 프로그램(`Sp_SUB_STOCK_FIFO_MAIN_P`)이나 취소 프로시저가 동작하는 중 에러가 발생하거나 사용자가 마감을 취소하면, `SUB_STOCK_FIFO_ERR_P` 프로시저가 호출됩니다.\n"
        "* **마감 상태 연계 갱신 및 로그 인서트**: 프로시저 내부에서는 마감 상태 원장(`STCKIOTB`)의 마감 처리 상태(`PROC_YN`)를 'E'(오류)로 갱신하고 오류 내역을 `PROC_REMARK`에 저장하는 동시에, `STCKERTB` 테이블에 작업자 ID(`proc_id`), 에러 구분(`error_yn`), 에러 사유 및 스택 트레이스 내용(`remark`), 취소 사유(`cancel_remark`)를 새 레코드로 인서트하여 영구 보관합니다.\n"
        "* **마감 복구 및 조치 관제**: 본사/어드민 시스템 마감 제어반 화면에서 선입선출 배치 연산 중 탈락한 가맹점들의 원인 분석과 에러 로그 분석을 위한 모니터링 자료로 사용됩니다."
    )

    data["tables"]["stckertb"] = {
        "memo": stckertb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "stock_month": "선입선출 마감 대상 년월 (YYYYMM)",
            "proc_seq": "마감 처리 고유 작업 순번 시퀀스 (3자리)",
            "proc_id": "마감/취소 처리를 주도한 프로그램 ID 또는 사용자 ID",
            "cancel_yn": "마감 작업 취소 처리 실행 여부 (Y/N)",
            "cancel_remark": "마감 작업 취소 시 입력된 사유 내용",
            "error_yn": "마감 오류 상태 구분 (E: 마감 에러, S: 시스템/취소 에러, Y: 성공)",
            "remark": "상세 예외 에러 메시지 및 DB 예외 로그 스택 트레이스",
            "create_date": "에러 로그 레코드 생성 일자 (YYYYMMDD)",
            "create_dtime": "에러 로그 레코드 생성 일시 (YYYYMMDDHH24MISS)",
            "chain_no": "체인 및 계열사 분류 코드"
        },
        "memo_c": "재고 마감 배치 실행 도중 예외 에러나 마감 취소 발생 시 SUB_STOCK_FIFO_ERR_P 프로시저에 의해 자동으로 생성 기록됩니다.",
        "memo_u": "동기화 피드백이나 에러 임시 상태 확인 등의 어드민 조율 시를 제외하고는 수정이 불가능합니다.",
        "memo_d": "시스템 마감 통제 로그이자 이력 감사 데이터이므로 임의 삭제가 전면 금지됩니다.",
        "memo_r": "어드민 마감 오류 모니터링 및 본사 월 마감 예외 복구 제어 조회 시 기초 감사 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "stckiotb",
                "description": "매장 재고 마감 처리 상태 원장 테이블. [프로시저 SUB_STOCK_FIFO_ERR_P 연동] 재고 월 마감 또는 취소 배치 구동 시, 성공/실패 상태를 기록하며 예외 실패 시 STCKERTB에 구체적인 오류 사유와 스택 트레이스를 기록합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 선입선출 배치 정산 시 원가 검증 과정에서 잔여 수량 음수값 예외나 입고 단가 누락 오류가 감지될 때 오류 추적용으로 간접 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 소속 체인을 매칭하여 체인 단위별 일괄 월 마감 통제 에러 통계를 집계할 때 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 재고 상품의 레시피 분해 과정에서 재고 소진 연산 에러가 발생한 문제 상품을 역추적할 때 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 선입선출 사용 유무 및 마감 가능 영업일 설정 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 에러 유형(E: 에러, S: 시스템 에러, Y: 성공)에 대응하는 한글 상태 코드를 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 월 마감 강제 취소 또는 예외 복구를 승인한 본사 담당자의 계정 실명 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 월 마감 대상 원자재 상품 정보의 유효성을 본사 기준 원장과 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 매입 전표 확정 누락 및 공급단가 0원 오류로 인해 월 마감 오류가 발생한 전표 이력을 규명할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 월 마감 오류 복구 후 정상 집계된 현재고 정보와 에러 시점의 불일치 수량을 대조하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 판매 레시피 분해(재고 감산 처리) 과정에서 발생한 상품 코드 불일치 및 수량 역추적 시 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 재고 마감 상태 제어 화면에서 강제 상태 정정을 실행한 담당자의 행위 이력을 감사용 로그로 기록 연계됩니다."
            }
        ]
    }

    # 60. STCKIOTB MEMO AND RELATED TABLES
    stckiotb_memo = (
        "### 1. 테이블 개요\n"
        "매장 재고 마감 처리 상태 원장 (`STCKIOTB`).\n"
        "가맹점별 월별 선입선출(FIFO) 재고 마감 처리 진행 상태(미처리, 마감완료, 에러, 가마감) 및 마감 취소 이력(취소자 ID, 사유, 일시)을 마감 월(`STOCK_MONTH`)과 시퀀스(`PROC_SEQ`)별로 관리 보관하는 재고 마감 마스터 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **재고 마감 시 상태 기록**: 가맹점이나 본사에서 월 재고 마감 처리(`st_stock_00008` 화면)를 요청하여 선입선출 정산 배치 프로그램(`Sp_SUB_STOCK_FIFO_MAIN_P`)이 구동되기 전, `STCKIOTB`에 실행자 ID(`proc_id`) 및 상태 `proc_yn = 'N'`(미처리)로 초기화 레코드가 적재됩니다.\n"
        "* **마감 진행 및 예외 갱신 (`SUB_STOCK_FIFO_ERR_P` 프로시저)**: 배치가 도중 오류 없이 정상적으로 수불 연산을 마치면 상태는 `proc_yn = 'Y'`(마감완료)로 업데이트됩니다. 반면, 배치 수행 중 에러가 유발되면 `SUB_STOCK_FIFO_ERR_P` 프로시저가 작동하여 `proc_yn = 'E'`(오류)로 변경하며 `proc_remark`에 상세 원인 텍스트를 로깅하고, 취소 요청 시에는 `cancel_yn = 'Y'`와 사유가 기재됩니다.\n"
        "* **가맹점 수불 마감 관제**: 본사/매장의 월 마감 통제 센터에서 마감 누락 매장을 스캔하고 마감 제한일을 차단 제어하는 데 중추 정보로 사용됩니다."
    )

    data["tables"]["stckiotb"] = {
        "memo": stckiotb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "stock_month": "선입선출 마감 대상 년월 (YYYYMM)",
            "proc_yn": "마감 진행 상태 구분 (N: 미처리, Y: 마감완료, E: 에러발생, C: 가마감완료)",
            "proc_seq": "마감 처리 고유 작업 순번 시퀀스 (3자리)",
            "proc_id": "마감 처리를 실행/등록한 사용자 ID",
            "proc_remark": "마감 처리 상태 관련 사유 및 에러 기록 비고",
            "proc_create_dtime": "마감 처리 최초 기동/요청 일시 (YYYYMMDDHH24MISS)",
            "proc_last_dtime": "마감 처리 상태 최종 변경 일시 (YYYYMMDDHH24MISS)",
            "cancel_yn": "마감 완료 건에 대한 취소 요청/승인 여부 (Y/N)",
            "cancel_id": "마감 취소를 요청/승인한 사용자 ID",
            "cancel_remark": "마감 취소 처리 사유 비고 내용",
            "cancel_create_dtime": "마감 취소 요청/처리 일시 (YYYYMMDDHH24MISS)",
            "chain_no": "체인 및 계열사 분류 코드 (점포 코드 매핑)"
        },
        "memo_c": "백오피스 재고 마감 화면에서 가맹점 마감 요청이 최초 접수될 때 신규 레코드로 생성됩니다.",
        "memo_u": "선입선출 월 마감 배치 성공(Sp_SUB_STOCK_FIFO_MAIN_P), 에러 발생(Sp_SUB_STOCK_FIFO_ERR_P) 및 마감 취소 승인에 의해 상태가 실시간 업데이트됩니다.",
        "memo_d": "가맹점별 마감 통제 감사 원장이므로 임의의 데이터 물리적 삭제가 차단됩니다.",
        "memo_r": "가맹점 월 마감 상태 현황판, 마감 제어 모듈, 마감 제한일 유효성 체크 시 핵심 기초 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 월 마감 실행 시 당월 입고 원장의 가마감 및 최종 이월 처리 상태를 원격 통제 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "stckertb",
                "description": "재고 마감 에러 로그 테이블. [프로시저 SUB_STOCK_FIFO_ERR_P 연동] 재고 월 마감 또는 취소 배치 구동 시, 성공/실패 상태를 기록하며 예외 실패 시 STCKERTB에 구체적인 오류 사유와 스택 트레이스를 기록합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점의 영업 점포 마스터 정보와 소속 체인을 매칭하여 월 마감 관제 화면에 매장명과 소속 브랜드를 출력할 때 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 마감 년월에 재고 마감이 보류되거나 오류가 발생한 점포의 상품 원가 기준을 대조 분석하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 수불 마감 마감 가능 시작일 설정 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 마감 진행 상태(proc_yn - N: 미처리, Y: 마감, E: 에러)에 대응하는 한글 상태 코드를 조인하여 매칭하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 월 마감 승인이나 실사 재고 보정 조정을 등록한 담당 사용자의 실명 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 표준 규격 원자재 품목 분류의 마감 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 월 마감 시 정산이 완료되지 않은 미확정 매입 전표 내역의 유무를 필터링 검증하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 월 마감 확정에 따른 실물 재고액과 장부상 기말 재고액의 최종 일치 상태를 동기화 제어하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매출 발생에 따른 소진 단가 산출 시, 월 마감 완료 상태를 체크하여 마감 월 이전 매출의 단가 수정을 통제하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 재고 마감 상태 제어 화면에서 강제 상태 정정을 실행한 담당자의 행위 이력을 감사용 로그로 기록 연계됩니다."
            }
        ]
    }

    # 61. STCKLGTB MEMO AND RELATED TABLES
    stcklgtb_memo = (
        "### 1. 테이블 개요\n"
        "선입선출 재고 수불 로그 대장 (`STCKLGTB`).\n"
        "점포별 원자재 및 상품의 개별 입출고 거래(매입, 매출소진, 반품, 이동, 조정, 폐기 등) 발생 시 선입선출법에 의거하여 매칭 단가(`COST`)와 차감 수량(`PROC_QTY`)을 일자별로 상세 기록 보존하는 감사 로그 및 이력 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **수불 상세 매칭 기록 적재 (`Sp_SUB_STOCK_FIFO_PROC_P` 프로시저)**: 가맹점 월 마감 배치 실행 시, 개별 품목 단위로 원자재 입고분과 매출 소진 및 기타 수불 흐름을 매칭하는 프로시저가 동작합니다. 이 과정에서 개별 거래가 어떤 입고 전표 단가와 매칭되어 처리되었는지 최종 결과 세부사항을 `STCKLGTB`에 실시간으로 인서트합니다.\n"
        "* **수불 원장 및 원가 롤업 (`Sp_SUB_STOCK_FIFO_AFTER_PROC_P` 프로시저)**: 마감 연산이 종료되면 `SUB_STOCK_FIFO_AFTER_PROC_P` 프로시저가 작동하여 `STCKLGTB` 테이블의 로그 레코드를 수량과 단가 조건으로 집계합니다. 이 값을 토대로 일별 자재 수불 원장(`IMDDIOTB`) 및 월별 자재 수불 원장(`IMMMIOTB`)의 매입원가, 매출원가, 폐기손실 및 이동 비용 등을 한꺼번에 갱신(Merge) 처리합니다.\n"
        "* **선입선출 수불 이력 조회**: 본사 백오피스 수불 이력 화면에서 특정 원자재 상품의 선입선출 단가 매칭 흐름이 정상적으로 연산되었는지 역추적하여 검증할 수 있는 핵심 이력 추적 대장입니다."
    )

    data["tables"]["stcklgtb"] = {
        "memo": stcklgtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "rowid": "시스템 생성 고유 레코드 식별 행 일련번호",
            "ms_no": "매장코드 (점포 코드)",
            "proc_date": "선입선출 정산 수불 처리 완료 일자 (YYYYMMDD)",
            "trbk_date": "실제 거래(매입, 매출 등)가 발생한 원천 일자 (YYYYMMDD)",
            "log_seq": "수불 로그 생성 순번 시퀀스 (8자리)",
            "goods_cd": "대상 원자재 및 상품코드",
            "key_bill_no": "매출/취소/이동 발생 원천 거래 전표 키 (매출 전표번호 등)",
            "obsl_key_bill_no": "매입 검수 발생 원천 거래 전표 키 (매입 전표번호 등)",
            "proc_fg": "수불 처리 구분 코드 (P: 매입, S: 매출소진, R: 매입반품, C: 매출반품, F: 이동출고, T: 이동입고, A: 조정, D: 폐기)",
            "stock_month": "선입선출 집계 대상 마감 년월 (YYYYMM)",
            "org_stock_month": "해당 수불분의 기초가 되는 원천 입고 마감 년월 (YYYYMM)",
            "cost": "해당 수불 건에 매칭되어 적용된 선입선출 원가 단가",
            "extra_cost": "해당 수불 건에 매칭 적용된 부대 비용",
            "trbk_qty": "원천 거래가 요청한 원시 처리 수량",
            "proc_qty": "선입선출법에 의해 실제 입고 배치에서 차감/매칭 완료된 정산 수량",
            "create_dtime": "수불 이력 레코드 생성 일시 (YYYYMMDDHH24MISS)",
            "stock_remark": "선입선출 수불 로그 관련 특이사항 비고",
            "use_price_yn": "금액 수불 반영 상태 구분 코드 (C: 반영완료, N: 미반영)",
            "price_work_date": "단가 정산 배치 작업 수행 일자"
        },
        "memo_c": "월 마감 배치(Sp_SUB_STOCK_FIFO_PROC_P) 실행 중 선입선출 매칭 결과에 따라 자동으로 생성 기록됩니다.",
        "memo_u": "선입선출 원가 재정산 배치나 감사 조정 작업에 의해 단가 및 수량이 가감 업데이트됩니다.",
        "memo_d": "가맹점 자산 평가 및 세무 세무 조사의 최종 증빙 백업 원장이므로 임의의 삭제가 원천 금지됩니다.",
        "memo_r": "본사 선입선출 수불 이력 상세 조회 및 상품별 매출원가 역추적 검증 시 핵심 감사 자료로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "imddiotb",
                "description": "일별 자재 수불 원장 테이블. [프로시저 SUB_STOCK_FIFO_AFTER_PROC_P 연동] 선입선출 수불 로그 대장(STCKLGTB)에 적재된 일자별 거래 유형별 단가와 처리 수량 곱셈 합계를 합산하여 일별 수불 자산 원장의 매입원가, 매출원가, 조정비용 등을 갱신 연동합니다."
            },
            {
                "table_name": "immmiotb",
                "description": "월별 자재 수불 원장 테이블. [프로시저 SUB_STOCK_FIFO_AFTER_PROC_P 연동] 선입선출 수불 로그 대장에 기록된 내용을 월 단위로 그룹 합계 롤업하여 월별 수불 자산 원장의 총원가 및 이월 금액을 합산 반영합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 입출고 거래에 의해 선입선출 입고대장에서 잔여 수량 차감 및 이월 처리가 완료되면, 해당 매칭 이력과 거래 단가 및 전표 매칭 로그를 STCKLGTB에 감사 로그로 적재합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 소속 정보를 대조하여 체인 또는 점포 단위별 선입선출 수불 이력을 필터링 조회할 때 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 수불 이력 조회 화면에서 각 로그 레코드의 자재 한글 상호명, 원부자재 분류 및 규격 정보를 매핑하여 렌더링하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 선입선출 수불 로그 백업 보관 연한 및 세부 원가 반올림 처리 소수점 자리 등의 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 수불 처리 구분(proc_fg - P: 매입, S: 매출소진, D: 폐기 등)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 수불 이력을 수동으로 보정 정정하거나 예외 조정을 처리한 관리자 사원의 실명 정보를 감사용으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 선입선출 로그 대상 상품의 규격 적합성 및 본사 분류군 코드 일치 여부를 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 매입 입고로 인해 수불 로그가 발생한 경우, 원천 매입 거래 단가 및 수량과 선입선출 로그의 정합성을 검증하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객 결제로 인해 원자재가 감산 소진된 경우, 해당 매출 전표번호(key_bill_no)의 매출 상세 데이터와 선입선출 소진 이력 로그의 수량을 상호 대조하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckiotb",
                "description": "매장 재고 마감 처리 상태 원장 테이블. 해당 수불 로그가 발생한 월 마감의 정상 확정 상태 여부를 판정하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 62. STCKMOTB MEMO AND RELATED TABLES
    stckmotb_memo = (
        "### 1. 테이블 개요\n"
        "선입선출 재고 강제 조정/수동 매핑 이력 테이블 (`STCKMOTB`).\n"
        "마감 오류 분석, 수량 불일치, 마이너스 재고 또는 특정 자재의 매입단가 오류가 발생했을 때 선입선출 정산 배치가 구동되기 전에 시스템 관리자나 개발자가 수동으로 특정 거래 전표(`KEY_BILL_NO`)의 단가(`SET_COST`)와 수량(`SET_QTY`)을 강제 강제 매핑/보정하기 위해 사용하는 수동 원가 조정 관리 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **수동 강제 매핑 및 대조 (`Sp_SUB_STOCK_FIFO_PROC_P` 프로시저)**: 가맹점 월 마감 배치 실행 시, 개별 원자재별로 매입, 매출, 조정, 이동 등을 선입선출 매칭하는 과정(`STOCK_P1`, `STOCK_A1`, `STOCK_T1` 등 커서)에서 `STCKMOTB`를 아우터 조인(`LEFT OUTER JOIN`)합니다. 수동 보정 데이터가 매치되는 경우, 원래 자재 수불 원시 트랜잭션(`IMTRBKTB`)에 기록된 기존 거래 수량 및 단가를 덮어쓰고(Override), 사용자가 설정한 단가(`set_cost`)와 수량(`set_qty`)을 기준으로 선입선출 정산 연산을 수행합니다.\n"
        "* **개발자/어드민 전용 제어**: 이 테이블은 백오피스 화면 상에서 일반 사용자가 접근하지 않으며, 정산 배치 에러 시 개발자 및 본사 최고 권한을 가진 어드민이 데이터베이스 스크립트나 특수 관리 터널을 통해 직접 수동 레코드를 삽입 제어합니다. (이동출고, 매입, 실사 등 입고 유형(수량이 늘어나는 수불)에 대해서만 단가 강제 매칭을 적용합니다.)"
    )

    data["tables"]["stckmotb"] = {
        "memo": stckmotb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "trbk_dtime": "원시 거래(매입 등) 발생 일시 (YYYYMMDDHH24MISS)",
            "ms_no": "매장코드 (점포 코드)",
            "proc_date": "원시 거래 처리 및 입고 일자 (YYYYMMDD)",
            "goods_cd": "조정 대상 원자재 및 상품코드",
            "proc_fg": "수불 처리 구분 코드 (P: 매입, A: 조정, F: 이동 등)",
            "key_bill_no": "대상 거래 전표 고유 식별 키 (매출/매입 전표번호 등)",
            "seq": "수동 조정 적용 순번 시퀀스 (동일 거래 내 순차 적용)",
            "set_cost": "선입선출 정산 시 강제로 적용시킬 보정 단위 원가 단가",
            "set_qty": "선입선출 정산 시 강제로 적용시킬 보정 처리 수량",
            "extra_cost": "조정 시 추가 반영할 부대비용",
            "create_dtime": "수동 조정 레코드 생성 일시 (YYYYMMDDHH24MISS)",
            "create_id": "수동 조정을 등록한 담당자 ID (개발자/어드민 계정)",
            "update_dtime": "수동 조정 레코드 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "update_id": "수동 조정을 수정한 담당자 ID",
            "remark": "수동 강제 매핑 사유 및 조정 근거 내역 설명 비고"
        },
        "memo_c": "정산 오류 및 원가 누락 복구를 위해 데이터베이스에 직접 또는 백오피스 내부 진단기를 통해 수동으로 레코드가 삽입됩니다.",
        "memo_u": "조정 단가 오류 및 정산 시뮬레이션 결과에 따라 담당 사용자가 갱신 업데이트할 수 있습니다.",
        "memo_d": "데이터 정합성 및 정산 오류 해결을 위한 수동 보정 감사 추적이므로 임의 삭제가 차단됩니다.",
        "memo_r": "월 마감 배치 구동 시 원시 거래(IMTRBKTB) 대조용으로 조인되며, 선입선출 정산 엔진의 예외 단가 분기점에서 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "imtrbktb",
                "description": "매장 자재 수불 트랜잭션 원장 테이블. [프로시저 Sp_SUB_STOCK_FIFO_PROC_P 연동] 선입선출 정산 배치 구동 시, 수동 매핑 설정(STCKMOTB)에 기록된 강제 단가 및 강제 수량 조건이 존재하면, IMTRBKTB의 원래 거래 내역(매입 단가, 수량 등)을 오버라이드하여 선입선출 정산을 강제 제어합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 강제 조정 설정에 의해 특정 입고 상품의 단가나 가동 수량을 수동 조정 처리하면, 이월되는 기말 재고(end_qty) 계산의 기초 자료로 활용됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 영업 점포 마스터 정보와 소속 체인을 매칭하여 해당 매장에 수동 원가 조정을 적용할 점포를 필터링 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 수동 매핑 조정된 자재의 실명 상호 및 규격 정보를 매칭 조회하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 선입선출 단가 수동 보정 기능 활성화 여부 및 조정 한도 한계 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 수불 조정 처리 유형(proc_fg - P: 매입, A: 조정, F: 이동 등)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 데이터베이스 상에서 수동 매핑 데이터 레코드 수정을 수행한 개발자/관리자의 실계정 ID 실명을 규명하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 수동 단가 조정 대상이 본사 표준 규격 원자재 품목 코드 체계에 부합하는지 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 매입 전표 입고단가 기입 오류나 정산 원가 누락 등의 유무를 수동 조정 전후로 비교 대조하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 강제 수동 조정 처리에 의해 기말 원가가 변동됨에 따라, 실시간 점포 재고의 자산 가액 변동 편차를 결합 평가하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매출 발생에 따른 소진 레시피 단가가 수동 조정에 의해 재산출될 때의 매출원가 변동률을 추적하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 중요 테이블인 수동 매핑 정보의 원격 인서트/정정 처리에 대해 보안 감사 이력을 추적 기록하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 63. STPRERTB MEMO AND RELATED TABLES
    stprertb_memo = (
        "### 1. 테이블 개요\n"
        "이동/반품 결산 작업 에러 로그 테이블 (`STPRERTB`).\n"
        "가맹점 간 재고 이송/이동 거래(`MGMVHDTB` 등) 발생 시 선입선출 규칙에 따라 송출 점포의 기말 단가를 입고 점포의 단가로 전이하는 결산 배치 실행 중 시스템 예외 오류, 단가 불일치 예외, 데드락 및 취소 사유 등의 상세 텍스트 이력을 로그 식별번호(`PROC_SEQ`)와 대상 년월(`STOCK_MONTH`) 단위로 로깅 관리하는 이송 결산 에러 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **이송 결산 에러/취소 발생 시 기록 적재 (`SUB_STOCK_MGMVHD_ERR_P` 프로시저)**: 가맹점간 재고 이송 정산 배치 프로그램(`Sp_SUB_STOCK_MGMVHD_P`)이나 취소 프로시저가 동작하는 중 에러가 발생하거나 사용자가 작업을 취소하면, `SUB_STOCK_MGMVHD_ERR_P` 프로시저가 호출됩니다.\n"
        "* **이송 결산 상태 연계 갱신 및 로그 인서트**: 프로시저 내부에서는 이송 처리 로그 대장(`STPRLGTB`)의 처리구분 상태(`PROC_YN`)를 'E'(오류)로 갱신하고 에러 내역을 `PROC_REMARK`에 저장하는 동시에, `STPRERTB` 테이블에 작업자 ID(`proc_id`), 에러 구분(`error_yn`), 에러 사유 및 스택 트레이스 내용(`remark`), 취소 사유(`cancel_remark`)를 새 레코드로 인서트하여 영구 보관합니다.\n"
        "* **이송 오류 복구 및 관제**: 본사 월 재고 마감 통제반 화면에서 가맹점 간의 재고 이동 단가 이전 연산 배치 중 발생한 이상값과 에러 원인 규명 및 조치 모니터링 자료로 사용됩니다."
    )

    data["tables"]["stprertb"] = {
        "memo": stprertb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "stock_month": "선입선출 마감 대상 년월 (YYYYMM)",
            "proc_seq": "이송 정산 처리 고유 작업 순번 시퀀스 (3자리)",
            "proc_id": "이송 정산/취소를 주도한 프로그램 ID 또는 사용자 ID",
            "cancel_yn": "이송 결산 작업 취소 처리 실행 여부 (Y/N)",
            "cancel_remark": "이송 결산 작업 취소 시 입력된 사유 내용",
            "error_yn": "이송 결산 오류 상태 구분 (E: 정산 에러, S: 시스템/취소 에러, Y: 성공)",
            "remark": "상세 예외 에러 메시지 및 DB 예외 로그 스택 트레이스",
            "create_date": "에러 로그 레코드 생성 일자 (YYYYMMDD)",
            "create_dtime": "에러 로그 레코드 생성 일시 (YYYYMMDDHH24MISS)",
            "chain_no": "체인 및 계열사 분류 코드"
        },
        "memo_c": "이송 정산 배치 실행 도중 예외 에러나 정산 취소 발생 시 SUB_STOCK_MGMVHD_ERR_P 프로시저에 의해 자동으로 생성 기록됩니다.",
        "memo_u": "동기화 피드백이나 에러 임시 상태 확인 등의 어드민 조율 시를 제외하고는 수정이 불가능합니다.",
        "memo_d": "시스템 이송 마감 통제 로그이자 이력 감사 데이터이므로 임의 삭제가 전면 금지됩니다.",
        "memo_r": "어드민 이송 결산 오류 모니터링 및 본사 가맹점 이송 정산 예외 복구 제어 조회 시 기초 감사 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "stprlgtb",
                "description": "매장간 재고 이동 처리 로그 상태 대장 테이블. [프로시저 SUB_STOCK_MGMVHD_ERR_P 연동] 재고 이송 정산 배치 구동 시, 성공/실패 상태를 기록하며 예외 실패 시 STPRERTB에 구체적인 오류 사유와 스택 트레이스를 기록합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 매장 간의 이동 입고 시, 송출 매장의 선입선출 기말 재고 단가가 인입 매장의 입고 단가로 정확히 이전되었는지 유효성 검증 과정에서 단가 불일치 예외를 추적할 때 조인 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 소속 체인을 매칭하여 가맹점 단위별 이송 정산 에러 통계를 집계할 때 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 재고 상품의 매장간 이동 과정에서 단가 정산 오류가 발생한 문제 상품을 역추적할 때 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매장 간 재고 이송 마감 통제 및 이송 단가 반올림 처리 소수점 자리 등의 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 에러 유형(E: 에러, S: 시스템 에러, Y: 성공)에 대응하는 한글 상태 코드를 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 이송 결산 강제 취소 또는 예외 복구를 승인한 본사 담당자의 계정 실명 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 이송 대상 상품 정보의 유효성을 본사 기준 원장과 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 매장간 이동 시 발생한 운반비 등의 추가 비용 또는 공급단가 누락 오류가 발생한 전표 이력을 규명할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 이송 오류 복구 후 정상 집계된 현재고 정보와 에러 시점의 불일치 수량을 대조하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매장 간 재고 이동 이후 발생한 판매 소진 과정에서 발생한 상품 코드 불일치 및 수량 역추적 시 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 재고 이동 마감 상태 제어 화면에서 강제 상태 정정을 실행한 담당자의 행위 이력을 감사용 로그로 기록 연계됩니다."
            }
        ]
    }

    # 64. STPRLGTB MEMO AND RELATED TABLES
    stprlgtb_memo = (
        "### 1. 테이블 개요\n"
        "매장간 재고 이동 처리 로그 상태 대장 (`STPRLGTB`).\n"
        "가맹점별 월별 매장간 재고 이송/이동 단가 결산 처리 진행 상태(미처리, 완료, 에러, 가결산) 및 취소 이력(취소자 ID, 사유, 일시)을 마감 월(`STOCK_MONTH`)과 시퀀스(`PROC_SEQ`)별로 관리 보관하는 재고 이동 정산 마스터 상태 대장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **재고 이동 결산 시 상태 기록**: 가맹점간 재고 이송 정산 처리(`hq_stock_00013` 화면)가 요청되어 이송 단가 매칭 배치 프로그램(`Sp_SUB_STOCK_MGMVHD_P`)이 구동되기 전, `STPRLGTB`에 실행자 ID(`proc_id`) 및 상태 `proc_yn = 'N'`(미처리)로 초기화 레코드가 적재됩니다.\n"
        "* **결산 진행 및 예외 갱신 (`SUB_STOCK_MGMVHD_ERR_P` 프로시저)**: 배치가 도중 오류 없이 정상적으로 송수신 매장 단가 매칭을 마치면 상태는 `proc_yn = 'Y'`(완료)로 업데이트됩니다. 반면, 배치 수행 중 에러가 유발되면 `SUB_STOCK_MGMVHD_ERR_P` 프로시저가 작동하여 `proc_yn = 'E'`(오류)로 변경하며 `proc_remark`에 상세 원인 텍스트를 로깅하고, 취소 요청 시에는 `cancel_yn = 'Y'`와 사유가 기재됩니다.\n"
        "* **매장간 이송 결산 관제**: 본사 월 재고 마감 통제반에서 가맹점 간의 이동 거래 정산 상태를 확인하고 이송 마감 정정을 실행하는 데 핵심 통제 데이터로 조회 활용됩니다."
    )

    data["tables"]["stprlgtb"] = {
        "memo": stprlgtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "stock_month": "선입선출 마감 대상 년월 (YYYYMM)",
            "proc_yn": "이송 결산 진행 상태 구분 (N: 미처리, Y: 완료, E: 에러발생, C: 가처리완료)",
            "proc_seq": "이송 결산 처리 고유 작업 순번 시퀀스 (3자리)",
            "proc_id": "이송 결산 처리를 실행/등록한 사용자 ID",
            "proc_remark": "이송 결산 처리 상태 관련 사유 및 에러 기록 비고",
            "proc_create_dtime": "이송 결산 처리 최초 기동/요청 일시 (YYYYMMDDHH24MISS)",
            "proc_last_dtime": "이송 결산 처리 상태 최종 변경 일시 (YYYYMMDDHH24MISS)",
            "cancel_yn": "이송 결산 완료 건에 대한 취소 요청/승인 여부 (Y/N)",
            "cancel_id": "이송 결산 취소를 요청/승인한 사용자 ID",
            "cancel_remark": "이송 결산 취소 처리 사유 비고 내용",
            "cancel_create_dtime": "이송 결산 취소 요청/처리 일시 (YYYYMMDDHH24MISS)",
            "chain_no": "체인 및 계열사 분류 코드 (점포 코드 매핑)"
        },
        "memo_c": "백오피스 가맹점 마감 통제 화면에서 이송 결산 요청이 최초 접수될 때 신규 레코드로 생성됩니다.",
        "memo_u": "이송 결산 배치 성공(Sp_SUB_STOCK_MGMVHD_P), 에러 발생(Sp_SUB_STOCK_MGMVHD_ERR_P) 및 결산 취소 승인에 의해 상태가 실시간 업데이트됩니다.",
        "memo_d": "가맹점별 재고 이동 통제 감사 원장이므로 임의의 데이터 물리적 삭제가 차단됩니다.",
        "memo_r": "가맹점 월 마감 상태 현황판, 매장간 이송 정산 제어 모듈, 이송 마감 유효성 체크 시 핵심 기초 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "stprertb",
                "description": "이동/반품 결산 작업 에러 로그 테이블. [프로시저 SUB_STOCK_MGMVHD_ERR_P 연동] 재고 이송 정산 배치 구동 중 예외 오류 발생 시, 상태 원격 추적을 위해 구체적인 로그 및 스택 트레이스 세부사항을 연계해 기록 보관합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 매장 간의 이동 입고 시, 송출 매장의 선입선출 기말 재고 단가가 인입 매장의 입고 단가로 정확히 이전되었는지 유효성 검증 과정에서 단가 불일치 예외를 추적할 때 조인 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점의 영업 점포 마스터 정보와 소속 체인을 매칭하여 월 마감 관제 화면에 매장명과 소속 브랜드를 출력할 때 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 특정 마감 년월에 이송 결산이 보류되거나 오류가 발생한 점포의 상품 원가 기준을 대조 분석하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 수불 이송 마감 가능 시작일 설정 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 이송 마감 진행 상태(proc_yn - N: 미처리, Y: 완료, E: 에러)에 대응하는 한글 상태 코드를 조인하여 매칭하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 이송 결산 승인이나 강제 취소를 등록한 담당 사용자의 실명 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 표준 규격 원자재 품목 분류의 이송 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 이송 정산 시 정산이 완료되지 않은 미확정 매입 전표 내역의 유무를 필터링 검증하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 이송 결산 확정에 따른 이송 수량과 실물 재고액의 최종 일치 상태를 동기화 제어하기 위해 점포 재고 대장과 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매출 발생에 따른 소진 단가 산출 시, 이송 마감 완료 상태를 체크하여 단가 수정을 통제하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 재고 이동 마감 상태 제어 화면에서 강제 상태 정정을 실행한 담당자의 행위 이력을 감사용 로그로 기록 연계됩니다."
            }
        ]
    }

    # 65. STRNBPTB MEMO AND RELATED TABLES
    strnbptb_memo = (
        "### 1. 테이블 개요\n"
        "매출 블루포인트(제휴 포인트) 결제/적립 상세 테이블 (`STRNBPTB`).\n"
        "고객이 POS 단말기 상에서 결제를 진행할 때 현대 블루멤버스 등 제휴 멤버십 포인트 카드를 이용해 대금을 차감 결제하거나 적립한 세부 실적(승인번호 `APPR_NO`, 사용금액 `BLUE_USE_AMT`, 적립포인트 `BLUE_SAVE_POINT`, 잔여액 `BLUE_AFTER_AMT` 등)을 영수증(`BILL_NO`)과 거래 순번 단위로 기록 보존하는 결제 상세 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 포인트 결제/적립 연동**: POS 단말기에서 고객이 결제 수단으로 포인트를 사용할 때 제휴망을 거쳐 승인받은 승인 내역 정보가 매출 헤더(`STRNHDTB`)에 링크되고 세부 내역이 `STRNBPTB`에 실시간으로 인서트됩니다. (매출 취소 시에는 `sale_fg = '1'`로 취소분이 연동됩니다.)\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 매출 결산 배치 실행 시, `STRNBPTB`에 기록된 제휴 포인트 사용 실적과 적립금을 롤업하여 본사가 대리 수납한 포인트 청구액 및 적립금 분개를 도출해 ERP 회계 장부로 송출 인터페이스를 전송합니다.\n"
        "* **승인 이력 및 매출 대조 조회**: 본사/매장 백오피스 결제 승인 확인반 화면에서 특정 포인트 거래의 진위 여부(카드번호 대조) 및 포인트 사용 금액 정합성을 매출 통계와 크로스 체크할 때 조인됩니다."
    )

    data["tables"]["strnbptb"] = {
        "memo": strnbptb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "bp_seq": "포인트 거래 승인/적립 상세 순번 (2자리)",
            "sale_fg": "매출 구분 코드 (0: 정상 매출/적립, 1: 취소/반품)",
            "type_fg": "거래 유형 구분 코드 (0: 포인트 적립, 1: 포인트 사용/결제)",
            "blue_point_no": "포인트 멤버십 회원 고유 식별 번호",
            "blue_use_amt": "금회 결제 시 사용한 포인트 결제 금액",
            "blue_save_amt": "금회 결제에 따른 포인트 적립 대상 거래 금액",
            "blue_save_point": "금회 적립된 포인트 점수 수치",
            "blue_after_amt": "거래 승인 직후 최종 잔여 가용 포인트 잔액",
            "appr_no": "제휴사 승인 센터에서 발급한 거래 승인 번호",
            "appr_date": "승인 처리 일자 (YYYYMMDD)",
            "org_appr_no": "반품/취소 시 대조할 원거래 승인 번호",
            "org_appr_date": "반품/취소 시 대조할 원거래 승인 일자 (YYYYMMDD)",
            "sale_vat": "포인트 결제액에 포함된 부가세액",
            "trade_serial_no": "제휴 통신 고유 거래 일련번호",
            "blue_check_no": "포인트 승인 확인 제어 번호",
            "blue_point_cardno": "고객이 제시한 제휴 멤버십 카드 실물 번호",
            "tax_free_amt": "포인트 거래 금액 중 면세 매출 대상액"
        },
        "memo_c": "POS 단말기에서 제휴 멤버십 카드 승인 완료 시 매출 원장 전송 패킷을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "반품 취소 및 고객 정보 마스킹, 거래망 일치화를 위한 배치 정산 처리 시 상태 변경 및 취소 정보가 업데이트됩니다.",
        "memo_d": "현금영수증 및 세무 지출증빙에 대응하는 중요 회계 결제 정보이므로 임의 삭제가 영구 제한됩니다.",
        "memo_r": "제휴 포인트 승인 조회, 포인트 결제 매출 보고서 작성, ERP 회계 마감 송신 시 핵심 정산 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제수단으로 제휴 포인트를 활용하거나 금액 적립을 수행하면, 매출 마스터 헤더(STRNHDTB)에 부가정보로 기록되고 세부 포인트 승인 원장으로 STRNBPTB에 상세 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 브랜드/체인을 확인하여 제휴포인트 가맹 할인 적용 대상 점포인지 유효성 확인을 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 특정 제휴 카드로 결제 시 할인 적용 대상 품목군 유효성 필터링을 검증하고, 품목별 포인트 적립 대상 제외품 설정 여부를 대조하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 포인트 결제 시 제외 품목(예: 담배, 서비스 품목 등)이 포함되어 있는지 유효성 검증을 위해 상품 카테고리를 연계 대조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 제휴 블루포인트 결제 허용 최소 금액 및 적립률(예: 0.1%, 1% 등) 등의 시스템 설정 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 포인트 적립/사용 구분 코드(type_fg), 매출/취소 구분 코드 및 포인트 제휴사 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 포인트 임의 보정 및 승인 취소 처리를 수행한 담당 사용자의 계정 실명 정보를 감사 목적으로 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 제휴사 공동 프로모션 대상 표준 품목의 단가 및 포인트 할인 상한률 유효성 검증을 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 포인트 정산 시 제휴 본사와의 포인트 대금 대리 정수 수납 수수료를 비교 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 제휴 포인트 프로모션 할인에 따른 행사 품목의 재고 소진율을 사후 비교 평가하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 제휴 포인트 할인율을 제외한 순수 매장 마진율을 원부자재 단가 기반으로 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 포인트 수동 정정이나 승인 전송 오류 연동의 이력을 감사 로그에 이력을 기록하고 연계합니다."
            }
        ]
    }

    # 66. STRNCDTB MEMO AND RELATED TABLES
    strncdtb_memo = (
        "### 1. 테이블 개요\n"
        "매출 신용카드 승인/결제 상세 테이블 (`STRNCDTB`).\n"
        "가맹점별 영업 중 발생한 모든 신용카드 결제 및 승인 거래 내역(승인금액 `APPR_AMT`, 승인번호 `APPR_NO`, 카드번호 `CARD_NO`, 카드사코드 `CARD_CO`, 할부개월 `INST_MCNT`, 가맹점번호 `CARD_JOIN_NO` 등)을 영수증(`BILL_NO`) 및 카드 거래 일련번호 단위로 상세하게 보관하는 매출의 핵심 신용카드 승인 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 카드 결제 승인 적재**: POS 단말기에서 신용카드 스와이프 결제 및 취소가 완료되면 승인 데이터가 수집되어 매출 헤더(`STRNHDTB`)에 총 신용카드 결제액으로 매핑되는 동시에, 세부 승인/매입 이력이 `STRNCDTB`에 실시간으로 인서트됩니다. (매출 취소/반품 시에는 `sale_fg = '1'`로 취소 승인이 연동 적재됩니다.)\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 카드사별 매출 청구 금액과 수수료(`card_fee_amt`)를 `STRNCDTB` 원장에서 자동으로 롤업하여 본사 ERP 재무 시스템으로 자동 분개 처리해 인터페이스를 전송합니다.\n"
        "* **백오피스 카드 정산 및 대사 관리**: 카드 승인 조회 및 카드사 미매입/미청구 불일치 점검, 수동 대사 처리 화면의 연동 데이터 원천으로, 카드 수수료율 차감에 따른 매장 순공급 가액과 실입금액의 차이를 비교 대조하여 정합성을 정정하는 데 사용됩니다."
    )

    data["tables"]["strncdtb"] = {
        "memo": strncdtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "card_seq": "카드 결제/승인 일련 순번 (2자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "chain_area": "체인 소속 지역 분류 번호",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품)",
            "card_no": "마스킹 처리된 신용카드 식별 번호 (16자리)",
            "card_data": "카드 마그네틱 트랙 데이터 정보 또는 암호화 카드 정보",
            "input_fg": "카드 정보 입력 방식 구분 코드 (0: IC/MS 리더기 스와이프, 1: 번호 키인 입력)",
            "appr_amt": "카드 승인 및 결제 원 거래 금액",
            "appr_no": "카드사 및 VAN사에서 발급한 고유 결제 승인 번호",
            "appr_date": "카드 승인 거래 일자 (YYYYMMDD)",
            "valid_term": "카드 유효기간 정보 (YYMM)",
            "inst_mcnt": "할부 개월 수 (0: 일시불, 2 이상: 할부 개월)",
            "card_co": "결제 카드사 구분 코드 (3자리)",
            "van_cd": "승인 통신망을 제공한 VAN사 식별 코드 (2자리)",
            "msg_cd": "카드 승인 단말기 응답 메시지 코드 (4자리)",
            "cancel_cd": "카드 승인 취소 시 전송된 취소 사유 코드 (4자리)",
            "org_appr_date": "취소/반품 거래 시 대조할 원거래 승인 일자 (YYYYMMDD)",
            "org_appr_no": "취소/반품 거래 시 대조할 원거래 승인 번호 (8자리)",
            "sale_dtime": "POS 매출 등록 완료 시스템 일시 (YYYYMMDDHH24MISS)",
            "appr_fg": "카드사 승인 진행 유형 구분 (0: 온라인 자동, 1: 수동/전화 승인 등)",
            "sale_type": "거래 승인 데이터 특성 매핑 필드",
            "cat_id": "POS 카드 단말기 VAN 단말기 등록 식별 번호 (CAT ID)",
            "card_rate": "해당 카드사에 지불할 카드 수수료율 (%)",
            "card_fee_amt": "해당 거래 승인에 대해 공제되는 카드사 결제 대행 수수료액",
            "demand_fg": "카드 청구 진행 구분 상태 코드 (0: 청구대기, 1: 청구완료, 2: 보류/반송)",
            "expect_date": "카드사로부터 정산 대금이 통장 입금될 예정 일자 (YYYYMMDD)",
            "demand_date": "카드사에 청구 배치 요청을 수행한 일자 (YYYYMMDD)",
            "in_date": "카드사 정산금 입금 처리 확인 일자 (YYYYMMDD)",
            "last_dtime": "청구 반송/오류 상태 최종 변경 일시 (YYYYMMDDHH24MISS)",
            "biz_no": "해당 가맹점 점포의 세무 등록 사업자번호 (10자리)",
            "issue_card_cd": "카드 발급사 식별 코드 (4자리)",
            "issue_card_nm": "카드 발급사 한글 명칭",
            "purch_card_cd": "카드 정산 매입 대행사 식별 코드 (4자리)",
            "purch_card_nm": "카드 정산 매입사 한글 명칭",
            "card_join_no": "해당 점포의 카드사별 가맹 계약 등록 번호",
            "ddc_co": "DDC 및 EDI 매입 구분 코드",
            "retn_fg": "정산 반송 처리 유형 구분",
            "easy_check": "간편결제/이지체크 식별 필드",
            "card_dc_amt": "카드사 제휴 자체 할인 혜택 적용액",
            "multi_biz_cd": "다중 사업자 분할 매출 식별 코드",
            "sign_pad_fg": "서명패드 서명 데이터 첨부 유무 (A: 일반, B: 면제 등)",
            "card_tip_amt": "카드 결제에 포함된 팁/봉사료 금액",
            "dc_appr_fg": "제휴 포인트 연동 카드 승인 구분 코드",
            "altercd_fg": "카드 대체 승인 거래 구분 (0: 일반, 1: 대체)",
            "sale_vat": "카드 결제 승인액 내에 포함된 부가세액",
            "net_sale_amt": "카드 결제 승인액 중 부가세를 제외한 공급가액 순매출액",
            "reward_card_fg": "리워드/포인트 매칭 카드 구분 (1: M포인트 등)",
            "mpoint_amt": "현대카드 M포인트 등 포인트 사용 처리 결제 승인액",
            "mpoint_divide": "M포인트 사용에 따른 카드사와 본사 비용 분할액",
            "appr_time": "카드 거래 승인 시각 (HH24MISS)",
            "pay_type": "결제 유형 구분 코드 (0: 일반 즉시승인, 1: 외상 대금 수납 정산)",
            "trade_serial_no": "VAN 통신 거래 고유 식별 일련번호",
            "mpoint_use": "M포인트 실 사용 포인트 점수 수치",
            "tax_free_amt": "카드 결제액 중 면세 상품 해당 공급가액"
        },
        "memo_c": "POS 단말기에서 신용카드 결제 및 취소 승인 완료 시 매출 패킷을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "카드 청구 배치 실행, 카드사 입금 확인(in_date) 및 수동 대사 정정 시 데이터가 업데이트됩니다.",
        "memo_d": "가맹점 매출 세무 지빙의 법적 효력을 가진 중요 회계 결제 정보이므로 임의 삭제가 영구 제한됩니다.",
        "memo_r": "신용카드 승인 이력 조회, 카드 정산 보고서 작성, ERP 카드 수수료 회계 마감 송신 시 최우선 정산 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제수단으로 신용카드를 이용하여 결제하면, 매출 마스터 헤더(STRNHDTB)의 카드 결제 합산액과 매핑되는 개별 승인 내역으로 STRNCDTB에 상세 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 카드 결제 승인 시 각 점포별 카드 가맹점 번호(card_join_no) 및 수수료 매칭 계약 정보를 대조 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 카드 결제 건의 세부 품목별 과세/면세 비율(tax_free_amt)과 공급 가액 내역의 정합성을 검증하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 카드 승인 내역의 품목별 부가세 공급가 세분화 계산 및 세무 정합성을 상품 분류 기준으로 비교 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 다중 사업자 연계 카드 승인 번호 및 단말기 서명패드 사용 여부(sign_pad_fg) 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 승인 카드사 코드(card_co), 입력 방법 구분(input_fg), 승인 유형 구분 등의 한글 명칭 라벨을 매핑 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 카드 수동 대사 화면에서 강제 청구 및 보류 상태 해제를 조작한 본사 정산 담당자의 신원 조회를 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 상품별 가맹 정산 시 카드 수수료율 차감에 따른 표준 마진 단가 변동 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 카드 청구 정산금 입금 내역과 원자재 구매 대금 매입 채무 상계 처리를 대조 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 카드사 제휴 할인 프로모션 행사에 따른 매장 잔여 재고 소진 추이를 비교 평가하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 카드 수수료 및 부가세를 차감한 순공급액 기준의 가맹점 순마진율을 선입선출 원가 기반으로 정밀 계산할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 카드 결제 승인 패킷 송수신 오류나 수동 청구 변경 이력을 보안 감사 로그에 추적 기록하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 67. STRNCHTB MEMO AND RELATED TABLES
    strnchtb_memo = (
        "### 1. 테이블 개요\n"
        "매출 현금영수증 승인/결제 상세 테이블 (`STRNCHTB`).\n"
        "가맹점별 영업 중 발생한 모든 현금 결제 건 중 현금영수증 발급을 수행한 거래 내역(승인금액 `SANCT_AMT`, 승인번호 `CASH_APPR_NO`, 신분확인식별번호 `IDENTIFY_NO`, 소득공제/지출증빙 거래구분 `TRADE_FG`, 승인일자 `CASH_APPR_DATE` 등)을 영수증(`BILL_NO`) 및 현금영수증 순번 단위로 상세하게 보관하는 매출 현금영수증 승인 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 현금영수증 승인 연동**: POS 단말기에서 고객이 현금으로 결제하며 휴대폰번호나 현금영수증 카드 등을 제시할 때, VAN 결제망을 통해 실시간으로 국세청에 승인받은 내역이 매출 헤더(`STRNHDTB`)에 현금결제 실적으로 링크되고 세부 승인 이력이 `STRNCHTB`에 실시간으로 인서트됩니다. (매출 취소/반품 시에는 `sale_fg = '1'`로 취소 승인이 연동 적재됩니다.)\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 현금 매출 시재 및 현금영수증 발행 실적을 `STRNCHTB` 원장에서 자동으로 롤업하여 본사 ERP 재무 시스템으로 자동 분개 처리해 인터페이스를 전송합니다.\n"
        "* **백오피스 현금영수증 및 정산 관리**: 현금영수증 승인 조회 및 어드민용 현금영수증 대사/미발행 관리 화면의 연동 데이터 원천으로, 현금 매출 대비 영수증 미발행 분에 대하여 국세청 기준 자진발급(`appr_fg = '1'`) 번호로 강제 소급 발행 처리하거나 정산 정합성을 대조하는 작업의 기반이 됩니다."
    )

    data["tables"]["strnchtb"] = {
        "memo": strnchtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "seq_no": "현금영수증 결제/승인 일련 순번 (2자리)",
            "cash_van_cd": "현금영수증 승인 통신망을 제공한 VAN사 식별 코드 (2자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "chain_area": "체인 소속 지역 분류 번호",
            "sale_fg": "매출 구분 코드 (0: 정상 매출/적립, 1: 취소/반품)",
            "input_fg": "신분식별번호 입력 방식 구분 코드 (0: MSR, 1: IC Card, 2: Key-in 입력)",
            "identify_fg": "인증 수단 식별 구분 코드 (휴대폰번호, 카드번호, 사업자번호 등)",
            "identify_no": "마스킹 처리된 현금영수증 인증 신분확인번호 (37자리)",
            "trade_fg": "거래 증빙 유형 구분 코드 (1: 개인 소득공제용, 2: 사업자 지출증빙용)",
            "sanct_amt": "현금영수증 거래 승인 및 발행 금액 (부가세 포함)",
            "cash_appr_no": "국세청 현금영수증 승인 센터에서 발급한 고유 승인 번호",
            "cash_appr_date": "국세청 현금영수증 거래 승인 일자 (YYYYMMDD)",
            "appr_time": "현금 거래 승인 시각 (HH24MISS)",
            "trade_appr_no": "VAN사에서 매칭 발급한 거래 승인 번호",
            "trade_appr_date": "VAN사 거래 승인 일자 (YYYYMMDD)",
            "sale_dtime": "POS 매출 등록 완료 시스템 일시 (YYYYMMDDHH24MISS)",
            "cancel_reason_fg": "현금영수증 승인 취소 시 전송된 취소 사유 구분 코드",
            "sale_vat": "현금영수증 발행액 내에 포함된 부가세액",
            "net_sale_amt": "현금영수증 발행액 중 부가세를 제외한 공급가액 순매출액",
            "appr_fg": "승인 진행 유형 구분 (0: 실시간 현금영수증 승인, 1: 자진발급, 2: 임의/대리 처리)",
            "appr_type": "현금 영수 결제 매체 구분 (0: 현금, 1: 자사상품권, 2: 타사상품권, 3: 기타)",
            "pay_type": "결제 유형 구분 코드 (0: 일반 즉시승인, 1: 외상 대금 수납 정산)",
            "trade_serial_no": "VAN 통신 거래 고유 식별 일련번호 (KSNET 등)",
            "tax_free_amt": "현금영수증 발행액 중 면세 상품 해당 공급가액"
        },
        "memo_c": "POS 단말기에서 현금영수증 발급 및 취소 승인 완료 시 매출 패킷을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "국세청 자진발급 강제 소급 발행 배치 수행 및 정산 수동 대사 정정 시 데이터가 업데이트됩니다.",
        "memo_d": "소비자 연말정산 및 가맹점 매출 증빙에 대응하는 국세청 전송용 중요 결제 정보이므로 임의 삭제가 영구 제한됩니다.",
        "memo_r": "현금영수증 승인 이력 조회, 현금영수증 발행 보고서 작성, ERP 현금 시재 회계 마감 송신 시 최우선 정산 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제수단으로 현금을 지불하고 현금영수증을 발급받으면, 매출 마스터 헤더(STRNHDTB)의 현금 결제 정보와 연계되는 세부 국세청 승인 내역으로 STRNCHTB에 상세 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 현금영수증 국세청 승인 시 가맹점 고유의 사업자번호(biz_no) 및 대리 가맹 계약 상태를 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 현금영수증 발급 건의 상세 과세/면세 품목 공급가액 비율(tax_free_amt) 정합성을 규명하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 현금영수증 발행 대상 제외 상품(예: 특정 바우처, 쿠폰 교환 품목 등)이 포함되어 있는지 상품 규격 매핑을 통해 대조 분석하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 현금영수증 의무 발행 기준 금액(예: 10만 원 이상 의무화) 및 자진발급 전화번호 등의 시스템 기본 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 거래 구분 코드(trade_fg - 1: 소득공제, 2: 지출증빙), 입력구분 및 승인 상태 한글 명칭 라벨을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 현금영수증 강제 자진발급 정산 작업을 수행한 관리자의 계정 ID를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 표준 규격 원자재 품목과 가맹점 현금 매출의 마진 구조를 정합성 차원에서 비교 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 일일 현금 시재 정산금과 본사 원자재 대금 매입 채무 상계 처리를 대조 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 현금 결제 프로모션 실적에 따른 매장 상품의 재고 감산율과 시재 정산 정합성을 대조하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 현금영수증 소득공제/지출증빙 혜택 제외 순수 매장 마진율을 원부자재 단가 기반으로 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 현금영수증 승인 통신망 오류에 따른 자진발급 보정이나 국세청 강제 전송 시퀀스 이력을 추적 보관하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 68. STRNCMTB MEMO AND RELATED TABLES
    strncmtb_memo = (
        "### 1. 테이블 개요\n"
        "매출 제휴사 할인/사원 할인/회사 할인 상세 테이블 (`STRNCMTB`).\n"
        "가맹점별 영업 중 발생한 매출 건 중 제휴 카드 할인, 임직원 복지 할인, 특별 회사 차감 할인 등을 적용한 구체적인 내역(할인적용 회사/제휴사 명칭 `COMP_NM`, 할인율 `COMP_DC_RATE`, 할인액 `COMP_DC_AMT`, 대상 사원번호 `EMP_NO` 등)을 영수증(`BILL_NO`) 및 할인 적용 순번별로 보관하는 상세 할인 적용 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 할인 적용 적재**: POS 단말기에서 결제 단계 중 임직원 사원 카드를 인식시키거나 특정 제휴처 할인 버튼을 선택하여 거래 금액을 경감시켰을 때, 매출 헤더(`STRNHDTB`)에 총 할인액으로 누적되는 동시에 세부 적용 할인 정보가 `STRNCMTB`에 실시간으로 기록됩니다. (매출 취소 시에는 `sale_fg = '1'`로 취소분이 연동됩니다.)\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 제휴사 할인 비용 및 복리후생 성격의 임직원 할인 보전액(`comp_dc_amt`)을 `STRNCMTB` 원장에서 자동으로 롤업하여 본사 비용(임직원 할인 분)과 제휴처 청구분 재무 분개를 작성해 ERP 회계 시스템으로 자동 인터페이스 송출합니다.\n"
        "* **백오피스 제휴/사원 할인 대사 관리**: 제휴사 할인 요율의 본사 부담분 대사 정산 보고서 작성, 임직원별 당월 할인 적용 누적 한도 계산의 원천 데이터로 사용되며, 한도 초과 오류 결제 시 수동으로 한도를 소급 변경 조정하는 작업의 기반이 됩니다."
    )

    data["tables"]["strncmtb"] = {
        "memo": strncmtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품)",
            "cm_seq": "할인 적용 상세 일련 순번 (2자리)",
            "comp_cd": "할인을 제공한 제휴사 또는 회사 고유 코드 (10자리)",
            "comp_nm": "할인을 제공한 제휴사 또는 회사 한글 명칭",
            "comp_dc_rate": "할인 거래에 적용된 할인율 (%)",
            "comp_dc_amt": "해당 제휴/사원 결제 승인에 의해 적용된 실제 할인금액",
            "emp_no": "임직원 할인을 적용받은 사원의 고유 사원번호 (임직원 카드 매핑)"
        },
        "memo_c": "POS 단말기에서 제휴사 할인 또는 임직원 복지 할인 적용 후 결제 완료 시 매출 원장 전송 패킷을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "임직원 정보 연동 변경, 제휴사별 할인 분담 비율 소급 계산 및 한도 조정 시 데이터가 업데이트됩니다.",
        "memo_d": "가맹점 세무상 에누리액 및 본사 임직원 복리후생 정산의 증빙 자료이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "제휴/사원 할인 실적 조회, 제휴사 정산 보고서 작성, ERP 회계 마감 송신 시 핵심 할인 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제 시 제휴 할인이나 임직원 사원 할인을 적용받으면, 매출 마스터 헤더(STRNHDTB)의 총 할인액과 연계되는 상세 할인 내역으로 STRNCMTB에 상세 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 할인 프로모션 참여 여부 및 매장별 제휴사 할인 요율 계약 관계를 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 제휴사 할인 제외 품목이 매출 건에 포함되어 있는지 품목별 할인 금액의 합산 정합성을 검증하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 할인 적용에서 제외되는 상품군(예: 프로모션 제외 품목, 담배 등) 분류 속성을 대조하고 할인 단가 정합성을 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 임직원 할인 월 최대 한도 설정 및 제휴사별 허용 시간대 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 할인 적용 회사/제휴사 구분 코드(comp_cd)에 대응하는 정식 한글 제휴사 상호를 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 임직원 사원 할인 한도 관리 화면에서 사원 한도 조정 처리를 수행한 담당자의 계정 사번 실명을 규명하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 할인 적용에 따른 행사 품목의 본사 공급 마진율 감소 편차를 규명하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 제휴사 정산 할인금 입금 대조 시 본사 매입 대금과의 대사 처리를 비교하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 제휴사/임직원 할인 프로모션 실적에 따른 매장 상품의 재고 소진 현황을 비교 대조하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 제휴/임직원 할인이 적용된 판매 단가를 차감한 가맹점 순마진율을 선입선출 원부자재 단가 기반으로 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 임직원 사원 할인 한도 조정이나 수동 제휴사 코드 보정 이력을 보안 감사 로그에 기록 보존하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 69. STRNCPTB MEMO AND RELATED TABLES
    strncptb_memo = (
        "### 1. 테이블 개요\n"
        "매출 쿠폰/모바일 상품권/선불 카드 결제 상세 테이블 (`STRNCPTB`).\n"
        "가맹점별 영업 중 발생한 매출 결제 건 중 KakaoTalk 모바일상품권, 선불충전카드, 할인 쿠폰 등을 사용해 대금을 치른 상세 이력(쿠폰명 `COUPON_NM`, 승인번호 `APPR_NO`, 결제금액 `COUPON_DC_AMT`, 잔액 `REMAIN_AMT`, 수수료 `FEE` 등)을 영수증(`BILL_NO`) 및 쿠폰 적용 순번 단위로 기록 보존하는 제휴 쿠폰/선불카드 결제 상세 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 쿠폰/상품권 승인 연동**: POS 단말기에서 모바일 상품권 핀번호 바코드나 선불카드를 스캔하고 제휴망 승인을 받으면, 매출 헤더(`STRNHDTB`)에 쿠폰 결제 실적으로 적재되는 것과 동시에 `STRNCPTB`에 실시간 인서트됩니다. (매출 취소 시에는 `sale_fg = '1'`로 취소 승인이 연동됩니다.)\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 모바일상품권/선불카드 결제금 및 수수료(`fee`), 분담금(`allotment_amt`) 등을 `STRNCPTB` 원장에서 자동으로 롤업하여 본사 회계 ERP 재무 시스템으로 미수금 분개를 작성해 인터페이스 송출합니다.\n"
        "* **백오피스 제휴 쿠폰 및 선불카드 정산 관리**: 모바일 상품권 사용 조회, 대행사 정산 보고서 작성, 선불카드 잔액 한도 예외 조정 화면의 연동 데이터 원천으로, 대행사 수수료를 제외한 본사 청구금 대사 및 가맹점 마진율 정밀 계산에 활용됩니다."
    )

    data["tables"]["strncptb"] = {
        "memo": strncptb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품)",
            "coup_seq": "쿠폰 적용 상세 일련 순번 (8자리)",
            "coupon_no": "쿠폰 일련번호 또는 모바일상품권 핀(PIN) 번호 (20자리)",
            "coupon_nm": "쿠폰 명칭 또는 모바일 상품권 상세 품목 한글명",
            "coupon_type": "쿠폰 유형 구분 코드 (0: 금액권/정액권, 1: 메뉴교환권/특정상품 교환권)",
            "appr_no": "제휴 대행사에서 발급한 고유 결제 승인 번호 (20자리)",
            "appr_date": "제휴사 승인 처리 일자 (YYYYMMDD)",
            "pay_code": "결제 연동 제휴사 구분 코드 (10자리)",
            "cust_code": "할인 정산 대상 거래처 또는 관리 부서 코드",
            "evi_type": "증빙용 분류 코드",
            "appr_amt": "쿠폰 및 모바일상품권의 원래 액면 권면 금액",
            "coupon_amt": "쿠폰 사용 전 잔여 사용 가능 총액",
            "coupon_dc_amt": "해당 매출 결제 시 쿠폰에 의해 실제 차감된 사용 결제액",
            "allotment_amt": "할인 적용에 따른 본사 및 대행사 측 비용 분담금액",
            "fee": "정산 결제 시 발생한 모바일 상품권 대행 수수료액",
            "remain_amt": "결제 승인 직후 쿠폰/상품권의 최종 잔여 가용 금액",
            "sale_amt": "판매 상품의 기준 정가 판매 금액",
            "supply_pirce": "쿠폰 결제액 중 부가세를 제외한 공급가액",
            "vat": "쿠폰 결제액에 포함된 부가세액",
            "miscellaneous": "기타 부대비용 필드",
            "discards": "소진/낙장 포인트 처리 금액",
            "org_appr_date": "취소/반품 거래 시 대조할 원거래 승인 일자 (YYYYMMDD)",
            "org_appr_no": "취소/반품 거래 시 대조할 원거래 승인 번호",
            "prepaid_no": "선불 충전식 결제 카드 번호",
            "prepaid_yn": "선불 카드 결제 여부 구분 (Y/N)"
        },
        "memo_c": "POS 단말기에서 모바일상품권 및 선불카드 승인 완료 시 매출 패킷을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "대행사 청구 배치 실행, 한도 초과 오류 수동 보정 및 취소 정산 시 데이터가 업데이트됩니다.",
        "memo_d": "가맹점 매출 세무 증빙의 법적 효력을 가진 중요 회계 결제 정보이므로 임의 삭제가 영구 제한됩니다.",
        "memo_r": "모바일상품권 승인 이력 조회, 정산 대사 보고서 작성, ERP 수납 대행 회계 마감 송신 시 최우선 정산 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제 시 모바일상품권이나 쿠폰, 선불카드로 결제하면 매출 마스터 헤더(STRNHDTB)의 총 쿠폰 결제액과 매핑되는 상세 승인 건으로 STRNCPTB에 상세 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 모바일 쿠폰 승인 시 각 점포별 쿠폰 정산 제외 설정 및 수수료 정산 관계를 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 메뉴 교환권인 경우 승인된 쿠폰 대상 상품명(coupon_nm)과 실제 POS 매출 단품 정보가 정상적으로 매치되었는지 유효성 검증을 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 교환권 품목의 분류군 적합성 및 해당 매장에서 판매 중인 대체 상품과의 단가 정합성을 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 쿠폰 중복 사용 허용 여부 및 모바일상품권 잔액 환불 기준 금액(예: 60% 이상 사용 시 잔액 환불) 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 쿠폰 유형 구분 코드(coupon_type - 0: 금액권, 1: 특정 상품 교환권) 및 제휴 대행사 한글 라벨명을 조인하여 매칭하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 쿠폰 강제 승인 또는 결제 보류 조정을 승인한 담당 조작자의 신원 조회를 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 제휴사 특정 메뉴 교환권 대상 표준 자재 공급단가와 본사 부담 정산 비율의 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 쿠폰 정산금 입금 내역과 가맹점 본사 발주 채무액 간의 상계 처리를 대사할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 제휴 모바일 쿠폰 교환 행사에 따른 행사 대상 품목의 실시간 재고 차감 현황을 추적하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 대행 수수료를 공제한 최종 쿠폰 정산액 대비 원부자재 선입선출 원가를 기반으로 가맹점 순마진율을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 쿠폰 승인 전문 전송 실패에 따른 강제 상태 변경이나 수동 대사 이력을 감사용 로그에 기록하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 70. STRNCSTB MEMO AND RELATED TABLES
    strncstb_memo = (
        "### 1. 테이블 개요\n"
        "매출 고객 성별/연령대별 고객수 집계 상세 테이블 (`STRNCSTB`).\n"
        "가맹점별 영업 중 발생한 매출 영수증(`BILL_NO`) 단위로 고객의 내/외국인 여부 및 연령대(10대~50대 이상), 성별(남성/여성) 분포 인원수 실적을 실시간으로 입력 보관하는 매출 세부 인구통계(Demographics) 대장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 고객 데이터 삽입 및 검증**: POS 단말기에서 결제 완료 시 캐셔가 입력하거나 테이블 오더/키오스크 등을 통해 수집된 성별, 연령대별 고객수가 매출 트랜잭션 수신 시 `STRNCSTB`에 인서트됩니다. 이 과정에서 `STRNCS_T01` 트리거가 실행되어 입력된 성별/연령별 인원수 세부 합계가 내국인수(`NATIVE_CNT`) 및 외국인수(`FOREIGN_CNT`)와 일치하는지 무결성을 우선 검증합니다.\n"
        "* **일별 고객 통계 실시간 집계 (`SUB_SDAYCS_P` 프로시저)**: 무결성 검증을 통과하면, 트리거 내에서 `SUB_SDAYCS_P` 프로시저를 호출하여 매출 실적(총매출, 순매출, 할인액)과 인원수를 영업일자, 시간대별 고객 성별/연령대 집계 원장(`SDAYCSTB`)에 실시간으로 가감 합산 반영합니다. (매출 취소 시에는 `sale_fg = '1'` 조건으로 합산된 인원수와 금액을 차감 처리합니다.)\n"
        "* **백오피스 고객 타겟 분석**: 본사/매장의 성별/연령대별 매출 기여도 분석 화면의 원천 데이터로 사용되며, 프랜차이즈 신제품 개발 및 시간대별 타겟 프로모션 효과를 모니터링할 때 조인됩니다."
    )

    data["tables"]["strncstb"] = {
        "memo": strncstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품)",
            "cs_seq": "고객 통계 상세 일련 순번 (2자리)",
            "native_cnt": "해당 거래에 참여한 총 내국인 고객 수 합계",
            "native_age_10_man_cnt": "내국인 10대 이하 남성 고객 수",
            "native_age_10_fm_cnt": "내국인 10대 이하 여성 고객 수",
            "native_age_20_man_cnt": "내국인 20대 남성 고객 수",
            "native_age_20_fm_cnt": "내국인 20대 여성 고객 수",
            "native_age_30_man_cnt": "내국인 30대 남성 고객 수",
            "native_age_30_fm_cnt": "내국인 30대 여성 고객 수",
            "native_age_40_man_cnt": "내국인 40대 남성 고객 수",
            "native_age_40_fm_cnt": "내국인 40대 여성 고객 수",
            "native_age_50_man_cnt": "내국인 50대 이상 남성 고객 수",
            "native_age_50_fm_cnt": "내국인 50대 이상 여성 고객 수",
            "foreign_cnt": "해당 거래에 참여한 총 외국인 고객 수 합계",
            "foreign_age_10_man_cnt": "외국인 10대 이하 남성 고객 수",
            "foreign_age_10_fm_cnt": "외국인 10대 이하 여성 고객 수",
            "foreign_age_20_man_cnt": "외국인 20대 남성 고객 수",
            "foreign_age_20_fm_cnt": "외국인 20대 여성 고객 수",
            "foreign_age_30_man_cnt": "외국인 30대 남성 고객 수",
            "foreign_age_30_fm_cnt": "외국인 30대 여성 고객 수",
            "foreign_age_40_man_cnt": "외국인 40대 남성 고객 수",
            "foreign_age_40_fm_cnt": "외국인 40대 여성 고객 수",
            "foreign_age_50_man_cnt": "외국인 50대 이상 남성 고객 수",
            "foreign_age_50_fm_cnt": "외국인 50대 이상 여성 고객 수"
        },
        "memo_c": "POS 결제 완료 시 캐셔 입력 또는 테이블 오더 연동 데이터 패킷을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "영수증 재출력이나 사후 마케팅 목적의 고객 정보 보정 시 일부 업데이트될 수 있으나 일반적으로는 수정하지 않습니다.",
        "memo_d": "가맹점별 고객 타겟 분석의 기초 트랜잭션 로그 정보이므로 임의 삭제가 영구 제한됩니다.",
        "memo_r": "성별/연령대별 매출 분석 보고서 작성, 일별 고객 분포 통계(SDAYCSTB) 롤업 및 CRM 고객 관리 모듈 구동 시 원천 자료로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객 분류 통계가 발생하면, 매출 마스터 헤더(STRNHDTB)의 매출액 및 할인액 등의 원천 데이터를 조회하여 일별 집계에 반영합니다."
            },
            {
                "table_name": "sdaycstb",
                "description": "일별 고객 연령/성별 집계 원장 테이블. [트리거 STRNCS_T01 및 프로시저 SUB_SDAYCS_P 연동] STRNCSTB에 기록된 내/외국인 및 연령/성별 세부 인원수를 영업일자별, 시간대별, 점포별로 누적 합산하여 실시간 집계합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점별 소속 브랜드를 매칭하여 체인 전체 또는 지역별 연령대별 고객 분포 통계를 롤업할 때 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 특정 연령대/성별 고객층이 주로 소비한 핵심 메뉴 및 인기 단품 선호도를 교차 분석할 때 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 고객 분류군별로 선호하는 카테고리나 베스트셀러 자재 상품의 한글 명칭과 규격을 매핑할 때 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 테이블 오더나 키오스크에서 고객 Demographic 정보(성별, 연령) 수집의 강제 여부 및 연령대 매핑(예: 10대 이하 분류법) 가이드 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 고객 성별 구분 코드 및 내/외국인 구분 한글 명칭 라벨을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 통계 화면에서 특정 날짜의 가맹점별 고객 분포 추이를 조회하는 정산 사용자의 소속 권한을 매핑 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 특정 연령층 선호 품목의 본사 마진 배분율을 비교 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 주 타겟 고객 연령층의 선호 자재 품목에 대해 선제적으로 물류 발주 안전 재고량을 예측하는 데 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 고객층 분포 통계에 따라 단기 소진이 예상되는 원부자재의 현재고 잔량을 경고 등급으로 관리하기 위해 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 주 소비 연령층에 해당하는 판매 품목의 선입선출 기반 마진 가액을 평가 분석할 때 간접 참조됩니다."
            }
        ]
    }

    # 71. STRNCTTB MEMO AND RELATED TABLES
    strncttb_memo = (
        "### 1. 테이블 개요\n"
        "매출 제휴 카드/자사 카드/법인 카드 승인 상세 테이블 (`STRNCTTB`).\n"
        "가맹점별 영업 중 발생한 매출 결제 건 중 현대카드 M포인트, 특정 대기업 제휴 복지 카드, 자사 패밀리 카드 등을 이용하여 대금을 치른 상세 승인 내역(승인금액 `APPR_AMT`, 승인번호 `APPR_NO`, 카드구분 `OPT_CARD_FG`, 할부개월 `INST_MCNT`, 카드번호 `CARD_NO` 등)을 영수증(`BILL_NO`) 및 승인 순번 단위로 상세하게 보존하는 제휴 카드 승인 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 제휴카드 결제 승인 적재**: POS 단말기에서 제휴/법인 복지 카드를 긁거나 모바일 멤버십 앱을 스캔하여 결제가 승인되면, `SUB_STRNCT_P` 프로시저를 통해 매출 헤더(`STRNHDTB`)에 총 제휴카드 결제액으로 매핑되는 동시에 세부 승인 이력이 `STRNCTTB`에 실시간으로 적재됩니다. (매출 취소/반품 시에는 `sale_fg = '1'`로 취소 승인이 연동 적재됩니다.)\n"
        "* **일일 카드사별 매출 집계 갱신 (`STRNCT_T01` 트리거)**: `STRNCTTB` 테이블에 신규 승인 데이터가 삽입될 때, 해당 영업일자의 제휴사별 총 매출 정액을 실시간 누적 합산하여 일일 카드사별 매출 집계 대장에 즉시 갱신합니다.\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 제휴사 포인트 공제 및 본사 자사 상품권/멤버십 보전금 재무 분개를 `STRNCTTB` 원장에서 자동으로 롤업하여 본사 ERP 재무 시스템으로 분개 전송을 수행합니다.\n"
        "* **백오피스 제휴카드 정산 및 대사 관리**: 제휴카드 승인 조회 및 제휴사 포인트 청구/매입 불일치 내역 점검 화면의 데이터 원천으로 활용되며, 제휴사 정산 수수료율 차감에 따른 매장 순공급 가액과 실입금액의 차이를 비교 대조하는 수동 대사에 사용됩니다."
    )

    data["tables"]["strncttb"] = {
        "memo": strncttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "seq": "제휴카드 결제/승인 일련 순번 (2자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "chain_area": "체인 소속 지역 분류 번호",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품)",
            "card_no": "마스킹 처리된 제휴/자사 카드 식별 번호 (16자리)",
            "appr_amt": "제휴/자사 카드 거래 승인 및 결제 금액 (부가세 포함)",
            "appr_no": "제휴 카드사 또는 VAN사에서 발급한 고유 결제 승인 번호",
            "appr_date": "제휴/자사 카드 승인 일자 (YYYYMMDD)",
            "valid_term": "카드 유효기간 정보 (YYMM)",
            "inst_mcnt": "할부 개월 수 (0: 일시불, 2 이상: 할부 개월)",
            "card_co": "제휴 카드사 구분 코드 (3자리)",
            "van_cd": "승인 통신망을 제공한 VAN사 식별 코드 (2자리)",
            "org_appr_date": "취소/반품 거래 시 대조할 원거래 승인 일자 (YYYYMMDD)",
            "org_appr_no": "취소/반품 거래 시 대조할 원거래 승인 번호",
            "create_fg": "데이터 생성 주체 구분 코드 (0: POS 실시간, 1: 백오피스 수동)",
            "create_dtime": "최초 등록 시스템 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 사원번호 또는 시스템 ID",
            "last_dtime": "최종 변경 시스템 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 변경자 사원번호 또는 시스템 ID",
            "opt_card_fg": "제휴 카드 구분 (1: 자사 패밀리카드, 2: 타사 제휴카드, 3: 일반 법인카드 등)",
            "sale_vat": "제휴 카드 결제 승인액 내에 포함된 부가세액",
            "temp_purchase_corp_no": "임시 매입사 고유 코드 (4자리)",
            "net_sale_amt": "제휴 카드 결제 승인액 중 부가세를 제외한 공급가액 순매출액",
            "temp_appr_no": "임시/대체 승인 번호 (30자리)",
            "temp_inst_mn": "임시/대체 할부개월 (2자리)",
            "tax_free_amt": "제휴 카드 결제액 중 면세 상품 해당 공급가액"
        },
        "memo_c": "POS 단말기에서 제휴사/자사 카드 결제 완료 시 매출 패킷을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "카드 청구 배치 실행, 제휴 포인트 대사 정정 및 수동 매입 조정 시 데이터가 업데이트됩니다.",
        "memo_d": "가맹점 제휴 마케팅 실적 및 세무 증빙의 법적 효력을 가진 중요 회계 결제 정보이므로 임의 삭제가 영구 제한됩니다.",
        "memo_r": "제휴/자사 카드 승인 이력 조회, 청구 대사 보고서 작성, ERP 제휴 수수료 회계 마감 송신 시 최우선 정산 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제수단으로 제휴/자사 카드를 이용하여 결제하면, 매출 마스터 헤더(STRNHDTB)의 제휴카드 결제 합산액과 매핑되는 개별 승인 내역으로 STRNCTTB에 상세 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 제휴 카드 승인 및 본사 보증 계약에 따른 점포별 제휴 정산 정책을 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 제휴/자사 카드를 통한 특정 프로모션 제품의 할인 단가 및 공급가액 정합성을 품목 수준에서 규명하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 제휴/자사 카드로 구매 가능한 할인 제외 품목(예: 일부 상품권 등)이 거래에 포함되어 있는지 체크하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 제휴/자사 카드 결제 시 서명패드 서명 생략 기준액(예: 5만원 이하 서명 면제) 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 카드사 구분 코드(card_co), 제휴 카드 구분(opt_card_fg), 승인 유형 구분 등의 한글 라벨을 매핑하여 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 제휴카드 불일치 대사 화면에서 수동 매입 처리를 강제로 승인 조작한 정산 담당자의 계정 사번을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 제휴 카드 수수료율 차감에 따른 표준 원자재 마진 변동 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 제휴카드 정산금 입고 확인 시 본사 발주 매입 채무와의 대사 처리를 비교하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 제휴 카드사 연계 단독 할인 행사에 따른 상품의 실시간 재고 차감 현황을 대조하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 제휴사 결제 대행사 공제액을 제외한 최종 정산액 대비 원가 기반 가맹점 순마진율을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 제휴 카드 결제 승인망 통신 오류에 따른 자진 복구 보정이나 수동 매입 변경 이력을 추적 보존하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 72. STRNDPTB MEMO AND RELATED TABLES
    strndptb_memo = (
        "### 1. 테이블 개요\n"
        "매출 부서 청구 / 외상 부서 결제 / 사내 부서별 외상 결제 상세 테이블 (`STRNDPTB`).\n"
        "가맹점별 영업 중 발생한 매출 결제 건 중 사내 특정 부서 장부 청구 및 임직원 소속 부서 외상 결제 등을 적용한 구체적인 내역(결제금액 `APPR_AMT`, 부서번호 `DEPT_NO`, 부서코드 `DEPT_CD`, 부서명 `DEPT_NM`, 결제 사원번호 `DEPT_EMP_NO` 등)을 영수증(`BILL_NO`) 및 부서 결제 순번별로 보관하는 외상/장부 상세 결제 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 부서 결제 적재**: POS 단말기에서 사내 식당/식음료 매장 결제 단계 중 사원증 태깅이나 부서 장부 선택을 통해 외상 결제 처리가 완료되면, 매출 헤더(`STRNHDTB`)에 총 외상/장부 결제액으로 매핑되는 동시에 세부 결제 정보가 `STRNDPTB`에 실시간으로 인서트됩니다. (매출 취소 시에는 `sale_fg = '1'` 취소 내역이 연동됩니다.)\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 각 부서별로 청구될 일일 외상 매출액(`appr_amt`)을 `STRNDPTB` 원장 기반으로 롤업 집계하여, 사내 정산 미수금 및 부서 비용 차감용 재무 분개를 작성해 ERP 회계 시스템으로 자동 인터페이스 송출합니다.\n"
        "* **백오피스 부서 장부 및 정산 관리**: 부서별 외상/장부 결제 실적 조회, 부서별 예산 한도 대비 월 사용 현황 점검, 부서별 사후 청구서/정산서 출력 화면의 데이터 원천으로 사용되며, 직제 개편이나 한도 조정 시 예산 값을 보정하는 작업의 기반이 됩니다."
    )

    data["tables"]["strndptb"] = {
        "memo": strndptb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "dept_seq": "부서 결제 적용 상세 일련 순번 (2자리)",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품)",
            "appr_amt": "해당 부서 외상으로 처리 승인된 결제 금액",
            "dept_no": "부서 관리 번호 또는 임직원 소속 부서 식별 번호",
            "dept_cd": "할인 및 결제 대상 부서 코드 (10자리)",
            "dept_nm": "할인 및 결제 대상 부서 한글 명칭",
            "dept_emp_no": "부서 외상 결제를 요청한 임직원의 고유 사원번호",
            "sale_vat": "부서 외상 결제액 내에 포함된 부가세액",
            "tax_free_amt": "부서 외상 결제액 중 면세 상품 해당 공급가액"
        },
        "memo_c": "POS 단말기에서 사내 부서 장부 및 외상 결제 처리 완료 시 매출 원장 패킷을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "사내 인사 정보 연동 변경, 부서별 월별 정산 및 미수금 입금 완료 시 데이터가 업데이트됩니다.",
        "memo_d": "사내 거래처 부서 간 비용 정산 및 가맹점 세무상 외상 대장 증빙 자료이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "부서별 외상 실적 조회, 부서 정산서 출력 보고서 작성, ERP 미수금 회계 마감 송신 시 최우선 외상 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제수단으로 부서 장부/외상 결제를 선택하여 거래하면, 매출 마스터 헤더(STRNHDTB)의 총 외상/장부 결제액과 매핑되는 개별 승인 내역으로 STRNDPTB에 상세 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별 사내 식당/매장 설정 및 부서 결제 청구 계약 정보를 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 부서 결제 적용 건의 상세 과세/면세 품목 공급가액 비율(tax_free_amt) 정합성을 규명하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 부서 결제 대상 제외 품목(예: 주류, 담배 등 회사 규정상 부서비 지원 불가 품목)이 포함되어 있는지 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 부서별 월간 외상 사용 한도 제한 설정 및 부서 결제 허용 시간대 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 부서 결제 유형 구분 코드 및 결제 상태 한글 라벨명을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 부서 한도 조정 화면에서 사외/사내 예산 강제 증액 작업을 수행한 정산 관리자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 부서 정산 할인 요율 적용에 따른 품목별 마진율 변동 상태를 정합성 차원에서 비교 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 부서 정산금 입금 대사 시 본사 원자재 대금 매입 채무와의 상계 정합성을 대조하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 부서 단체 주문 등 대량 결제 발생 시 관련 원부자재의 현재고 잔량을 대조하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 부서 외상 매출액에 대한 최종 입금예정액 대비 원부자재 선입선출 원가를 기반으로 가맹점 순마진율을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 부서 결제 한도 초과 오류 패킷이나 수동 한도 조정 이력을 감사용 로그에 기록하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 73. STRNDTTB MEMO AND RELATED TABLES
    strndttb_memo = (
        "### 1. 테이블 개요\n"
        "매출 상세 품목 판매 원장 테이블 (`STRNDTTB`).\n"
        "가맹점별 영업 중 발생한 매출 영수증(`BILL_NO`) 단위의 개별 판매 단품 품목 세부 정보(상품코드 `GOODS_CD`, 수량 `SALE_QTY`, 판매단가 `UPRICE`, 할인액 `DC_AMT`, 실판매금액 `SALE_AMT`, 부가세 `SALE_VAT`, 순공급가액 `NET_SALE_AMT` 등)를 순번(`LINE_NO`)별로 정밀 보관하는 매출의 핵심 품목 상세 거래 내역 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 판매 단품 내역 적재**: POS 단말기에서 결제 승인 완료 시 매출 패킷을 수신하여 매출 헤더(`STRNHDTB`) 마스터 레코드와 1:N 관계로 상세 품목 목록이 `STRNDTTB`에 실시간으로 생성 적재됩니다. (매출 취소 시에는 `sale_fg = '1'` 조건의 반품 데이터가 음수 수량/금액으로 적재됩니다.)\n"
        "* **일일 매출 상품별 집계 및 재고 차감 연계 (`STRNDT_T01` 트리거)**: `STRNDTTB`에 신규 품목 데이터가 인서트되면 `STRNDT_T01` 트리거가 가동되어 상품별 일일 매출 대장(`SGOODMTB` / `SDAYGDTB`)에 실시간 누적 합산하고, 재고 감산 프로시저(`SUB_STOCK_MGMVHD_P`)를 트리거하여 해당 점포의 현재고(`imcriotb`)를 레시피 소요량 기준으로 자동 차감 차감시킵니다.\n"
        "* **프로모션 혜택 검증 (`STRNPM_T01` 트리거)**: 판매 품목 중 행사 프로모션 해당 상품(`prom_good_fg = '1'`) 여부를 대조하여, 행사 분담 정산금을 연산하고 정합성을 적재합니다.\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점 일일 정산 마감 배치 실행 시, 품목별 순매출 및 과세/면세 비율 정보를 `STRNDTTB` 원장에서 자동으로 롤업하여 본사 ERP 재무 시스템으로 과세 유형별 매출 인터페이스를 전송합니다."
    )

    data["tables"]["strndttb"] = {
        "memo": strndttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "line_no": "영수증 내 판매 단품 품목 순번 (2자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "chain_area": "체인 소속 지역 분류 번호",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품)",
            "goods_cd": "매출 등록된 단품의 고유 상품코드 (20자리)",
            "pack_fg": "포장 구분 코드 (1: 테이크아웃 포장, 2: 매장 내 취식 등)",
            "uprice": "해당 상품의 단품 기준 표준 판매 가격 (정가)",
            "ucost": "해당 상품의 표준 제조 원단가 또는 가맹점 입고 원가",
            "sale_qty": "실제 판매 완료된 단품의 수량",
            "sale_tot": "수량 곱하기 단가의 정가 기준 판매 총액 합산액",
            "sale_amt": "할인 차감 후 최종 고객이 지불한 품목별 실거래 결제액",
            "dc_amt": "해당 단품에 적용된 전체 할인금액 총액",
            "point": "해당 단품 구매로 적립된 멤버십 적립 포인트 점수",
            "stock_fg": "재고 감산 처리 상태 구분 코드 (0: 일반 차감 완료, 1: 옵션/세트 하위구성 등)",
            "vat_amt": "해당 단품 결제액에 포함된 개별 부가세액",
            "norm_dc_amt": "단품에 적용된 일반 자체 할인금액",
            "service_dc_amt": "점포 서비스/프로모션 적용에 의한 할인금액",
            "card_dc_amt": "제휴/자사 카드 제휴 할인에 따른 공제금액",
            "coupon_dc_amt": "모바일/지류 쿠폰 사용에 따른 차감 할인액",
            "cust_dc_amt": "고객 멤버십 등급에 의해 할인 적용된 금액",
            "par_goods_cd": "세트 및 옵션 상품인 경우 상위(부모) 대표 상품코드",
            "sub_memu_cd": "사이드 메뉴 또는 세부 변경 옵션 코드",
            "sub_menu_nm": "사이드 메뉴 또는 세부 변경 옵션 명칭",
            "sale_type": "판매 특성 구분 매핑 코드 (0: 일반, 1: 서비스 등)",
            "order_empid": "주문을 입력 및 처리한 담당 캐셔/주문 직원 사원번호",
            "tip_fg": "봉사료/팁 청구 여부 (0: 없음, 1: 포함)",
            "prom_good_fg": "제휴 프로모션 및 본사 행사 상품 여부 구분 (Y/N)",
            "identify_no": "고객 식별 번호 (20자리)",
            "goods_sn": "상품 시리얼 번호 (스마트 기기 등 판매 시)",
            "eco_point": "그린카드 에코 포인트 점수",
            "spc_point": "그린카드 스페셜 포인트 점수",
            "sale_vat": "해당 단품 판매 실적의 세무 신고용 부가세액",
            "net_sale_amt": "해당 단품 판매 실적의 세무 신고용 순매출 공급가액",
            "support_amt": "본사 행사 보조금 정산금액",
            "dc_cpn_cd": "적용된 할인 쿠폰 식별 코드",
            "item_no": "아이템 일련 번호",
            "emp_dc_amt": "임직원 복지 카드 사용에 따른 사원 할인금액",
            "cash_dc_remant": "현금 결제 거스름돈 차감 보정금액",
            "dept_dc_amt": "사내 부서 장부 결제에 의한 부서 할인/청구금액",
            "pre_purch_fg": "선매입 입고 처리 여부 구분 (Y/N)"
        },
        "memo_c": "POS 결제 승인 완료 시 매출 원장 트랜잭션 전송을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "영수증 재출력이나 취소 거래 연동, 할인 구분 보정 시 데이터가 업데이트됩니다.",
        "memo_d": "가맹점 세무상 매출 공급가액 및 부가세 신고의 법적 원천 증빙 자료이므로 임의 삭제가 절대 불허됩니다.",
        "memo_r": "품목별 매출 실적 분석, 매장 원부자재 재고 차감 및 ERP 품목별 순매출 분개 송신 시 최우선 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객의 1회 주문 거래 건에 대한 총 결제 금액 마스터(STRNHDTB)와 세부 주문 품목별 판매 상세 데이터인 STRNDTTB 간의 1:N 마스터-상세 관계를 형성합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 매출이 발생한 상품 코드(goods_cd)에 대응하는 매장 판매 가격, 과세/면세 구분, 표준 조리 레시피 등을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. [프로시저 SUB_STOCK_MGMVHD_P 연동] 품목 판매 실적(STRNDTTB.sale_qty)에 해당하는 완제품 상품 재고 및 조리 레시피에 매핑된 원부자재 수량을 매장 현재고에서 즉시 차감 반영합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 점포별로 체인 가맹 형태에 따른 품목 공급 단가 및 표준 마진율을 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 매출 품목의 원가(ucost) 및 실판매액(sale_amt)을 대조하여, 선입선출법에 기반한 실시간 가맹점 매출 총이익(마진액)을 정밀 계산할 때 연계 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 서비스 메뉴 옵션 사용 정책 및 품목별 최대 할인율 상한선 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 포장 구분(pack_fg), 재고 처리 상태(stock_fg), 행사 상품 코드 등의 한글 명칭 라벨을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 주문을 등록한 POS 오퍼레이터 또는 서빙 사원번호(order_empid)의 권한과 이름을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사에서 관리하는 규격 단품 표준명칭 및 물류 공급 원가 정합성을 품목 수준에서 교차 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 매출 수량 추이에 따라 매장 원부자재 발주 소요량(MRP)을 지능형으로 예측하여 차기 발주 자동 생성 엔진을 구동할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 매출 품목 송수신 중 발생한 누락 오류나 수동 가격 변경 이력을 감사용 로그에 기록하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strncdtb",
                "description": "매출 신용카드 승인/결제 상세 테이블. 카드사 제휴 프로모션 상품 결제 시, 특정 단품의 결제 조건 충족 여부를 확인하기 위해 교차 조인 연계됩니다."
            }
        ]
    }

    # 74. STRNGCTB MEMO AND RELATED TABLES
    strngctb_memo = (
        "### 1. 테이블 개요\n"
        "매출 자사 기프트카드 / 충전식 선불카드 승인 및 결제 상세 테이블 (`STRNGCTB`).\n"
        "가맹점별 영업 중 발생한 매출 결제 건 중 자사 브랜드 기프트카드, 모바일 충전식 카드 등을 사용해 대금을 치르거나 카드를 충전한 상세 내역(결제/충전금액 `USED_AMOUNT`/`APPR_AMOUNT`, 카드번호 `GIFT_NO`, 승인번호 `APPR_NO`, 회원번호 `MEMBER_NO`, 거래 후 잔액 `BALANCE` 등)을 영수증(`BILL_NO`) 및 승인 순번 단위로 기록 보존하는 기프트카드 승인 상세 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 기프트카드 승인/충전 연동**: POS 단말기에서 자사 기프트카드를 긁거나 모바일 바코드를 인식시켜 결제 또는 충전을 수행하면, 실시간으로 자사 카드 서버 전문 연동을 거쳐 승인 데이터가 매출 헤더(`STRNHDTB`)의 카드/충전 거래 정보와 연계되는 동시에 `STRNGCTB`에 실시간 적재됩니다. (취소 시에는 `sale_fg = '1'`로 승인 취소 분이 음수 또는 보정 이력으로 적재됩니다.)\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 기프트카드 결제액 및 충전액(`STRNGCTB`)을 가맹점별로 자동 집계하여, 미수금 수납 처리 및 기프트카드 선수금 계정 대체 재무 분개를 작성해 ERP 회계 시스템으로 자동 인터페이스 송출합니다.\n"
        "* **백오피스 기프트카드 정산 및 환불 대사**: 가맹점 기프트카드 충전/사용 이력 대사, 카드 고유번호별 누적 잔액 검증, 기프트카드 환불 및 충전 취소 정합성 점검 화면의 데이터 원천으로 사용됩니다."
    )

    data["tables"]["strngctb"] = {
        "memo": strngctb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "sale_fg": "매출 구분 코드 (0: 정상 매출/충전, 1: 취소/반품/환불)",
            "seq_no": "기프트카드 결제/승인 일련 순번 (3자리)",
            "appr_no": "기프트카드 결제 서버에서 발급한 고유 결제 승인 번호 (12자리)",
            "appr_date": "기프트카드 승인 처리 일자 (YYYYMMDD)",
            "appr_time": "기프트카드 승인 거래 시각 (HH24MISS)",
            "appr_code": "기프트카드 승인 응답 상태 코드 (3자리)",
            "cancel_code": "취소 시 발생한 상세 취소 사유 코드 (1자리)",
            "org_appr_date": "취소/반품 거래 시 대조할 원거래 승인 일자 (12자리)",
            "master_seq": "선불카드 시스템 마스터 매핑 일련번호",
            "detail_seq": "선불카드 시스템 상세 매핑 일련번호",
            "gift_no": "자사 기프트카드 실물 및 바코드 식별 번호 (16자리)",
            "gift_name": "기프트카드 고유 명칭 (기프티카드 유형 분류 한글명)",
            "appr_amount": "해당 거래의 기프트카드 총 승인 및 충전 금액",
            "supply_price": "기프트카드 결제액 중 부가세를 제외한 공급가액",
            "vat": "기프트카드 결제액에 포함된 부가세액",
            "fee": "기프트카드 정산 시 공제하는 결제 제휴 수수료액",
            "evidence_code": "매출 증빙 분류 코드",
            "prepaid_no": "선불 결제 수단 번호 (18자리)",
            "trade_no": "VAN 통신 거래 고유 식별 일련번호",
            "face_amount": "해당 기프트카드의 원래 충전액/권면 금액",
            "used_amount": "이번 결제에 사용한 기프트카드 금액",
            "refund_amount": "기프트카드 거래 취소 및 환불 처리 완료 금액",
            "balance": "결제 또는 충전 직후 기프트카드의 최종 가용 잔액",
            "member_no": "기프트카드를 소지 또는 등록한 멤버십 회원의 고유 번호 (16자리)",
            "member_name": "기프트카드 등록 회원의 한글 이름",
            "appr_pay_seq": "결제 수단 승인 순번 (2자리)",
            "charging_date": "기프트카드 최근 충전 일자 (YYYYMMDD)",
            "charging_seq": "기프트카드 최근 충전 처리 일련 순번",
            "total_charged": "해당 기프트카드에 누적 등록된 총 충전 합산액",
            "total_used": "해당 기프트카드로 사용된 총 누적 결제액",
            "last_refunded_date": "최종 환불 처리 완료 일자 (YYYYMMDD)",
            "previous_charged": "이전 거래 시점까지의 누적 충전 금액",
            "previous_used": "이전 거래 시점까지의 누적 사용 금액",
            "total_refunded": "누적 환불 처리 완료된 총 환불 합산액"
        },
        "memo_c": "POS 단말기에서 기프트카드 결제 또는 충전 승인 완료 시 전문 연동을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "기프트카드 충전 취소, 미수금 정산 및 백오피스 수동 잔액 조정 시 데이터가 업데이트됩니다.",
        "memo_d": "자사 발행 기프트카드 선수금 채무 및 고객 자산 정보가 포함되므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "기프트카드 사용/충전 현황 조회, 대사 보고서 작성, ERP 회계 선수금 대체 송신 시 최우선 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제 시 자사 기프트카드/선불카드를 사용하여 결제하거나 매장에서 카드를 충전하면, 매출 마스터 헤더(STRNHDTB)의 결제/충전 거래 실적과 연계되는 상세 이력으로 STRNGCTB에 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별로 기프트카드 할인 정책 참여 상태 및 가맹계약 정보를 매치 참조하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 기프트카드로 교환 가능한 특정 패키지 상품이나 기프트 상품의 한도 수량을 검증하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 기프트카드 충전권 판매 시 충전 수수료 및 부가세 면세 비율 등을 비교 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 1회 최대 충전 가능 한도(예: 50만 원) 및 기프트카드 잔액 반환 의무 한도 비율 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 기프트카드 거래 구분 코드 및 승인 취소 사유 한글 라벨을 매핑 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 기프트카드 정산 화면에서 기프트카드 강제 충전 보정 또는 환불을 승인한 조작자의 계정 정보를 규명하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 표준 규격 기프트 상품 분류와 상품권 회수율을 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 일일 정산금 입금 처리 시 기프트카드 본사 회수 대금 상계 처리를 대조 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 발행된 세금계산서 가액 대비 원부자재 선입선출 매입단가 기반으로 가맹점 순마진율을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 국세청 전자세금계산서 송수신 패킷 전송 오류 이력 및 수동 취소 변경 사항을 보안 감사하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 77. STRNKTTB MEMO AND RELATED TABLES
    strnkttb_memo = (
        "### 1. 테이블 개요\n"
        "매출 통신사 제휴 멤버십 할인 승인 상세 테이블 (`STRNKTTB`).\n"
        "가맹점별 영업 중 발생한 매출 결제 건 중 이동통신사(SKT, KT, LGT 등) 멤버십 카드를 태깅하여 할인을 승인받은 상세 내역(대상금액 `FACE_SALE_AMT`, 승인할인액 `APPR_DC_AMT`, 통신사 제휴사코드 `KTF_CD`, 승인번호 `APPR_NO`, 할인율 `DC_RATE`, 멤버십 남은잔액 `APPR_REMAIN_AMT` 등)을 영수증(`BILL_NO`) 및 단말 거래 단위로 보관하는 통신사 제휴 할인 상세 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 통신사 승인/할인 연동**: POS 단말기에서 결제 단계 중 통신사 멤버십 카드를 긁거나 바코드를 스캔하면, 실시간으로 통신사 할인 승인망 전문 송수신 연동을 거쳐 승인 데이터가 매출 헤더(`STRNHDTB`)의 제휴카드 할인 총액과 매핑되는 동시에 `STRNKTTB`에 실시간 적재됩니다. (취소 시에는 `sale_fg = '1'` 취소 거래 계산서가 연동 적재됩니다.)\n"
        "* **제휴 할인 일일 집계 및 실시간 롤업 (`STRNKT_T01` 트리거)**: `STRNKTTB`에 신규 할인 마스터가 삽입되거나 취소 분이 인서트될 때, 해당 매장의 통신사 제휴 일별 할인 집계 원장(`SKTFDDTB` 등)에 통신사별 일일 누적 할인 실적과 거래 객수를 실시간 롤업 집계 처리합니다.\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 통신사 멤버십 할인액 및 통신사사별 본사 분담액 정보를 `STRNKTTB` 원장에서 자동으로 롤업하여 통신사 청구용 미수금 분개를 생성하고 본사 ERP 재무 시스템으로 전송합니다."
    )

    data["tables"]["strnkttb"] = {
        "memo": strnkttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "chain_area": "체인 소속 지역 분류 번호",
            "ktf_cd": "제휴 통신사 식별 코드 (KT, SKT, LGT 등 구분 코드)",
            "sale_fg": "매출 구분 코드 (0: 정상 매출/할인, 1: 취소/반품/할인취소)",
            "card_no": "마스킹 처리된 통신사 멤버십 카드 고유 번호 (16자리)",
            "input_fg": "멤버십 입력 형태 구분 코드 (0: Swipe 리더 인식, 1: Manual 수동 번호 입력)",
            "face_sale_amt": "통신사 할인 적용 대상이 되는 원 거래 품목 총액",
            "appr_dc_amt": "통신사 승인망을 통해 차감 확정된 실제 할인금액",
            "appr_no": "통신사 승인 서버에서 발급한 고유 제휴 승인 번호 (12자리)",
            "sale_dtime": "통신사 제휴 할인 거래 승인 처리 완료 시각 (YYYYMMDDHH24MISS)",
            "promotion_nm": "적용된 통신사 멤버십 프로모션 및 제휴 행사 명칭",
            "valid_from_date": "멤버십 카드 거래 유효 기간 시작 일자 (YYYYMMDD)",
            "valid_to_date": "멤버십 카드 거래 유효 기간 만료 일자 (YYYYMMDD)",
            "good_proc_fg": "할인 대상 상품 처리 구분 (0: 전체 표준 상품, 1: 특정 프로모션 제외 상품 등)",
            "dc_rate": "해당 제휴 계약에 의해 적용된 멤버십 할인 요율 (최대 100.00%)",
            "round_fg": "할인액 단수 처리 절사 구분 코드 (0: 반올림, 1: 절사, 2: 올림)",
            "appr_fg": "승인 상태 플래그 (0: 실시간 승인망 통과, 1: 오프라인 수동 강제 대체 승인)",
            "appr_corp_cd": "할인 처리를 대행한 VAN사 또는 제휴 승인 회사 코드",
            "net_sale_amt": "통신사 승인액 중 부가세를 제외한 공급가액",
            "appr_remain_amt": "할인 거래 적용 직후 고객 통신사 멤버십의 남은 잔여 포인트 액수",
            "valid_date": "멤버십 카드 유효기간 표시 (MMYY)"
        },
        "memo_c": "POS 단말기에서 통신사 제휴 할인 결제 완료 시 실시간 통신사 전문 승인 처리를 거쳐 생성 기록됩니다.",
        "memo_u": "통신사 할인 취소, 미수금 정산 보정 및 대사 불일치 보정 시 데이터가 업데이트됩니다.",
        "memo_d": "통신사 정산금 청구 및 가맹점 정산의 법적 회계 증빙 자료이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "통신사 제휴 할인 현황 조회, 통신사별 월간 한도 정산 보고서 작성, ERP 회계 정산 배치 송신 시 최우선 할인 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제 단계에서 통신사 멤버십 할인을 적용받으면, 매출 마스터 헤더(STRNHDTB)의 제휴카드 할인액과 매핑되는 개별 승인 내역으로 STRNKTTB에 상세 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별 통신사 제휴 프로모션 행사 참가 여부 및 본사/가맹점 할인 분담 요율 정책을 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 제휴 통신사별로 특정 상품 카테고리에 한해 추가 할인을 지원하는 경우, 세부 품목별 할인 매칭 정합성을 검증하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 통신사 제휴 할인 적용에서 제외되는 상품 분류(예: 타 프로모션 중복 제외 품목)가 거래에 포함되어 있는지 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 통신사 1일 최대 할인 적용 횟수 및 1회 최대 할인 적용 한도 기준 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 제휴 통신사 구분 코드(ktf_cd), 승인 절사 방식(round_fg), 승인 유형 한글 라벨명을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 통계 화면에서 특정 날짜의 가맹점별 통신사 제휴 마감 현황을 조회하는 정산 관리자의 권한을 매핑 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 통신사 할인에 따른 본사 공급 마진 요율의 변동 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 통신사 할인 비용에 대한 사후 보조 정산금 입금 처리 시 본사 발주 매입 채무와의 대사 처리를 비교하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 통신사 단독 할인 프로모션에 따른 인기 상품의 실시간 재고 차감 현황을 확인하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 통신사 할인 및 분담금을 차감한 순매출 단가 기준 가맹점 순마진율을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 통신사 승인망 연동 통신 실패에 따른 승인 지연나 수동 복구 이력을 보안 감사하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 75. STRNHDTB MEMO AND RELATED TABLES
    strnhdtb_memo = (
        "### 1. 테이블 개요\n"
        "매출 거래 마스터 헤더 원장 테이블 (`STRNHDTB`).\n"
        "가맹점별 영업 중 발생한 모든 주문 거래(정상 매출, 매출 취소/반품, 충전 등)의 총괄 마스터 정보(총매출액 `SALE_TOT`, 순매출액 `NET_SALE_AMT`, 부가세 `SALE_VAT`, 테이블번호 `TABLE_NO`, 영업일자 `SALE_DATE`, 결제수단별 지불총액, 고객수 등)를 영수증(`BILL_NO`) 단위로 보관하는 매출 시스템 최우선 핵심 원천 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 매출 마스터 수집**: POS 단말기에서 거래 결제가 완료되면 매출의 총 지불 내역과 가맹점 식별 데이터가 `STRNHDTB`에 최우선적으로 적재되며, 개별 상품 판매 목록(`STRNDTTB`) 및 각 지불 수단별 승인 상세 원장(`STRNCDTB`, `STRNCHTB` 등)을 1:N 자식 관계로 매핑하여 매출 트랜잭션을 완성합니다.\n"
        "* **일별/월별 매출 실시간 롤업 집계 (`STRNHD_T01`/`T02` 트리거)**: `STRNHDTB`에 신규 마스터가 삽입되거나 취소 분이 인서트될 때, 해당 매장의 일별 매출 집계 원장(`SDAILYTB`) 및 월별 매출 집계 원장(`SMONTHTB`)에 매출 총액과 결제수단별 객수를 실시간 누적 합산 또는 차감 처리하고, 포인트 적립 실적을 갱신합니다.\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 총매출액 및 수납 집계액(`STRNHDTB`)을 기준으로 본사 ERP 재무 마감 인터페이스 분개를 생성 및 송출합니다.\n"
        "* **선입선출 원가 배치 계산 (`SUB_STOCK_FIFO_MAIN_P` 프로시저)**: 매장 매출 트랜잭션(`STRNHDTB`) 정보를 기반으로 품목별 FIFO 원가와 매출 총이익율을 주기적으로 배치 계산합니다."
    )

    data["tables"]["strnhdtb"] = {
        "memo": strnhdtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "chain_ms_no": "체인 및 가맹 매장 고유 코드",
            "cust_card_no": "마스킹 처리된 고객 멤버십 포인트 카드 번호",
            "sale_point": "해당 매출 거래로 인해 발생 적립된 멤버십 포인트",
            "use_point": "해당 매출 결제에 사용 처리된 멤버십 포인트 점수",
            "first_fg": "거래 최초 구분 코드 (0: 일반 판매, 1: 최초 거래 취소 등)",
            "group_id": "단체/그룹 테이블 식별 ID",
            "table_no": "매장 내 테이블 식별 번호 (3자리)",
            "emp_id": "해당 영수증 결제를 승인 처리한 담당 캐셔/사원 ID",
            "native_cnt": "해당 영수증 거래에 참여한 총 내국인 객수",
            "foreign_cnt": "해당 영수증 거래에 참여한 총 외국인 객수",
            "gift_amt": "해당 거래에 지불 수단으로 사용된 총 지류 상품권 금액",
            "point_amt": "해당 거래에 지불 수단으로 사용된 총 포인트 결제 금액",
            "norm_dc_amt": "해당 거래에 적용된 총 일반 자체 할인 금액 합계",
            "service_dc_amt": "해당 거래에 적용된 총 서비스 프로모션 할인 금액",
            "card_dc_amt": "해당 거래에 적용된 총 제휴 카드 공제 할인 금액",
            "coupon_dc_amt": "해당 거래에 적용된 총 쿠폰 사용 할인 금액",
            "cust_dc_amt": "해당 거래에 적용된 총 회원 멤버십 등급 할인 금액",
            "forder_empid": "최초 주문을 입력한 서빙 담당자 사원 ID",
            "lorder_empid": "최종 주문 변경을 승인한 서빙 담당자 사원 ID",
            "order_date": "최초 주문 등록 영업 일자 (YYYYMMDD)",
            "order_time": "최초 주문 등록 시각 (HH24MISS)",
            "offer_date": "주문 상품 최초 제공(서빙) 일자 (YYYYMMDD)",
            "offer_time": "주문 상품 최초 제공(서빙) 시각 (HH24MISS)",
            "tip_amt": "고객이 지불하여 캐셔에 등록된 봉사료/팁 금액",
            "paid_card_amt": "신용카드 결제 수단으로 최종 지불된 실카드 결제 총액",
            "paid_card_no": "지불에 사용된 대표 신용카드 번호",
            "cash_re_amt": "현금 결제 후 거스름돈 환불액 또는 현금 반품 환불 총액",
            "gift_re_amt": "지류 상품권 결제 후 거스름돈으로 지급된 환불액",
            "opt_card_fg": "제휴 카드 구분 플래그 (1: 자사, 2: 타사, 3: 일반)",
            "opt_card_co": "제휴 카드사 코드",
            "opt_card_no": "제휴 카드 번호",
            "weas_amt": "외상/외상장부로 지불 승인된 외상 총액",
            "crediphone_amt": "모바일 간편 결제 수단 결제액",
            "room_amt": "객실 룸 차지 청구액",
            "cust_fg": "고객 유형 구분 플래그",
            "myone_fg": "마이원 제휴 구분 플래그",
            "okcash_amt": "OK캐쉬백 포인트 사용 지불액",
            "sex": "대표 결제자 성별 (남성: 0, 여성: 1)",
            "age": "대표 결제자 연령대 구분 (10대:0, 20대:1, 30대:2, 40대:3, 50대:4, 60대이상:5, 미분류:6)",
            "cust_cl_fg": "고객 상세 분류 코드",
            "return_cd": "반품/취소 사유 코드 (취소 영수증인 경우)",
            "corporation_fg": "법인/기업 결제 구분 코드 (0: 개인, 1: 법인)",
            "altercd_fg": "대체 거래 구분 플래그 (0: 일반, 1: 대체 거래)",
            "tmoney_amt": "티머니 선불교통카드 결제 총액",
            "eco_amt": "그린카드 결제 총액",
            "daum_myone_amt": "다음 마이원 결제 총액",
            "mtic_amt": "엠틱 결제 총액",
            "cashbee_amt": "캐시비 교통카드 결제 총액",
            "insert_dtime": "매출 서버에 최종 통신 전송 및 인서트 완료된 시각 (YYYYMMDDHH24MISS)",
            "yawoori_amt": "야우리 제휴 포인트 결제액",
            "purchase_code": "해당 신용카드 승인 매입용 고유 식별 번호 (15자리)",
            "reward_amt": "제휴 카드 리워드 포인트 사용액",
            "mobile_coupon_amt": "모바일 교환권/쿠폰 결제 총액",
            "meme_point_amt": "마이멤버십 포인트 결제액",
            "tax_free_amt": "해당 영수증 매출액 중 면세 상품 공급가액 합계",
            "sale_vat": "해당 영수증 매출의 전체 세무 부가세 총액",
            "cash_remnant": "단수 차액 보정 잔돈 금액",
            "net_sale_amt": "해당 영수증 매출의 전체 세무 공급가액 순매출 총액",
            "support_amt": "행사 보조금 정산 합계액",
            "fun_mobile_amt": "간편결제 모바일 지불액",
            "if_fg": "ERP 재무 회계 인터페이스 전송 상태 코드 (Y: 완료, N: 대기, E: 에러)",
            "invoice_amt": "매장 인보이스 매출 가액",
            "dept_amt": "사내 부서 장부 결제로 지불된 외상 총액",
            "blue_use_amt": "현대 블루멤버십 포인트 실 사용 지불액",
            "blue_save_point": "현대 블루멤버십 포인트 실 적립 포인트",
            "parking_fg": "무료 주차 등록 여부 플래그 (0: 미등록, 1: 등록 완료)",
            "cash_dc_remant": "현금 영수 결제 시 적용된 단수 할인 금액",
            "emp_dc_amt": "임직원 사원 복지 카드로 할인 적용된 할인 총액",
            "play_amt": "오락/엔터테인먼트 제휴 수납액",
            "petty_amt": "소액 결제용 수납 대행 금액",
            "dept_dc_amt": "사내 부서 장부 결제 시 할인 적용된 총 할인액",
            "coupon_amt": "모바일 상품권 및 선불 쿠폰 결제 총액",
            "car_no": "무료 주차 등록 고객 차량번호",
            "park_date": "주차 등록 일자 (YYYYMMDD)",
            "park_seq": "주차 등록 일련 순번",
            "giftcard_amt": "자사 발행 선불 기프트카드로 최종 지불된 결제 총액",
            "mem_giftcard_amt": "제휴사 발행 기프트카드로 지불된 결제 총액"
        },
        "memo_c": "POS 결제 승인 완료 시 매출 마스터 헤더 패킷 송신을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "일일 마감 마감 정정, 사후 주차 등록 또는 반품/취소 거래 연동 시 데이터가 업데이트됩니다.",
        "memo_d": "프랜차이즈 전체 세무 정산 및 법적 매출 증빙의 근본 마스터이므로 임의 삭제가 영구 불허됩니다.",
        "memo_r": "일보/월보 보고서 작성, 결제 수단별 세부 대사 보고서 작성, ERP 회계 송신 마감 배치 시 최우선 마스터 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 고객의 1회 주문 거래 건에 대한 총 결제 금액 마스터(STRNHDTB)와 세부 주문 품목별 판매 상세 데이터인 STRNDTTB 간의 1:N 마스터-상세 관계를 형성합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 매출이 발생한 점포의 소속 체인, 영업 상태 및 가맹점 정산 계약 정보를 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "sdailytb",
                "description": "일별 매출 집계 테이블. [트리거 STRNHD_T01 연동] STRNHDTB 매출 실시간 적재 시 점포별, 영업일자별, 시간대별 총 객수(bill_cnt), 결제수단별 매출액을 실시간 누적 집계합니다."
            },
            {
                "table_name": "smouthtb",
                "description": "월별 매출 집계 테이블. [트리거 STRNHD_T01 연동] 매출 마스터 헤더 적재 시 점포별 해당 영업 월의 누적 매출액과 객수 추이를 실시간 집계합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 매출 거래가 정상적인 상품 판매인지 또는 제휴 기프트카드나 포인트 상품권 구매 거래인지 상품 대분류 정합성을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 POS 마감 기준 시각 및 강제 셧다운 시간대, 영수증 출력 설정 정책 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 매출 구분(sale_fg), 영수증 최초구분(first_fg), 결제수단별 구분 코드 등의 한글 명칭 라벨을 매핑하여 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 해당 거래 매출을 최종 승인 마감한 POS 캐셔ID 또는 영수증 사후 보정을 조작한 정산 담당자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 가맹점 매출 단가와 본사 출하 표준 정가의 가격 편차 정합성을 규명하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 총매출 실적과 본사 발주 상품의 출하 대금(매입채무) 상계 처리를 대조 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 품목 판매에 따른 재고 자동 차감 로직 연계 시 전체 매출액 대비 재고 소진율의 상관 관계를 시뮬레이션할 때 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. [프로시저 SUB_STOCK_FIFO_MAIN_P 연동] 매출 헤더(STRNHDTB)의 총 공급가액 대비 선입선출 입고 단가를 대조하여 점포별 매출 총이익을 계산할 때 간접 참조됩니다."
            }
        ]
    }

    # 76. STRNIVTB MEMO AND RELATED TABLES
    strnivtb_memo = (
        "### 1. 테이블 개요\n"
        "매출 세금계산서 / 매출 인보이스 발행 상세 테이블 (`STRNIVTB`).\n"
        "가맹점별 영업 중 발생한 매출 결제 건 중 단체 연회, 기업 고객, 제휴 단체 등이 매출 세금계산서 또는 법인 청구 인보이스 발행을 요청한 거래 내역(인보이스 청구액 `APPR_AMT`, 부가세 `SALE_VAT`, 거래처 사업자등록번호 `VENDOR_BIZ_NO`, 상호명 `VENDOR_CORP_NM`, 대표자명 `VENDOR_REPN_NM`, 발행구분 `ISSUE_FG` 등)을 영수증(`BILL_NO`) 및 인보이스 순번 단위로 상세 보관하는 기업 매출 세무 증빙 상세 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 세금계산서/인보이스 발행 이력 적재**: POS 단말기에서 결제 단계 또는 사후 백오피스 재발행 화면을 통해 세금계산서가 발행되면, 매출 헤더(`STRNHDTB`) 마스터의 인보이스 금액(`invoice_amt`)과 링크되는 동시에 세부 사업자 증빙 이력이 `STRNIVTB`에 실시간으로 기록됩니다. (매출 취소 시에는 `sale_fg = '1'` 취소 거래 계산서가 연동 적재됩니다.)\n"
        "* **국세청 전자세금계산서 전송 배치 (`DmSALT60Service` 및 `DmSALT60_SQL`)**: 매일 마감 시점에 본 원장(`STRNIVTB`) 데이터를 자동 수집 및 검증하여, 국세청 전자세금계산서 표준 XML 전문 파일로 변환 가공해 국세청 전송 시스템으로 자동 배치 전송합니다.\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 인보이스 세금계산서 발행액과 부가세(`sale_vat`)를 `STRNIVTB` 원장에서 자동으로 롤업하여 본사 ERP 재무 시스템으로 세무 계산서 매출 분개를 작성해 인터페이스 전송을 수행합니다."
    )

    data["tables"]["strnivtb"] = {
        "memo": strnivtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "inv_seq": "인보이스 발행 상세 일련 순번 (2자리)",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품/마이너스 발행)",
            "issue_fg": "세금계산서 발행 시점 구분 (0: POS 즉시 발행, 1: 백오피스 사후 재발행)",
            "vendor_cd": "세금계산서 발행 대상 법인/개인 거래처 고유 코드 (10자리)",
            "appr_amt": "세금계산서 및 인보이스에 청구 표시된 공급가액 합산액",
            "vendor_biz_no": "거래처 사업자등록번호 (10자리 또는 식별번호)",
            "vendor_corp_nm": "거래처 공식 법인명 및 상호명",
            "vendor_repn_nm": "거래처 대표자 한글 실명",
            "sale_vat": "인보이스/세금계산서에 포함된 거래 부가세액",
            "pay_type": "수납 형태 구분 코드 (0: 일반 즉시결제 수납, 1: 외상 대금 대체 청구)"
        },
        "memo_c": "POS 단말기 결제 완료 시점의 인보이스 세금계산서 승인 요청 또는 백오피스 재발행 API 연동을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "국세청 전자세금계산서 신고 상태 피드백 업데이트 및 수동 세무 정정 시 일부 업데이트됩니다.",
        "memo_d": "대한민국 국세청 부가가치세법상 사업자 세무 증빙의 법적 원천 원장이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "세금계산서 발행 이력 조회, 국세청 전자세금계산서 송신 파일 생성, ERP 회계 마감 세무 송신 시 최우선 세무 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제 시 세금계산서/인보이스 발행을 요청하면, 매출 마스터 헤더(STRNHDTB)의 매출 실적과 연계되는 상세 사업자 증빙 이력으로 STRNIVTB에 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별로 세금계산서 직발행 가능 여부 및 매장 고유 사업자등록 정보를 대조 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 세금계산서 발행 시 세부 과세/면세 상품 품목 공급 가액 정합성을 확인하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 세금계산서 발행 제외 품목(예: 일부 상품권 등 부가세법상 계산서 발행이 불가능한 수납대행 품목)이 매출에 포함되어 있는지 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 수동 세금계산서 승인 권한 여부 및 국세청 자동 전송 시간대 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 계산서 발행 구분 코드(issue_fg), 결제수단 유형, 국세청 전송 상태 한글 라벨명을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 세금계산서를 수동으로 취소 및 재발행 처리한 세무 담당 조작자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 표준 과세 가이드라인에 따른 상품 규격 공급가 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 세금계산서 매출 정산 내역과 본사 물류 원자재 세금계산서 매입 채무 간의 상계 처리를 대사할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 인보이스로 대량 판매된 상품의 실시간 재고 차감율과 점포 보유 수량 밸런스를 검증하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 발행된 세금계산서 가액 대비 원부자재 선입선출 매입단가 기반으로 가맹점 순마진율을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 국세청 전자세금계산서 송수신 패킷 전송 오류 이력 및 수동 취소 변경 사항을 보안 감사하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 78. STRNMNTB MEMO AND RELATED TABLES
    strnmntb_memo = (
        "### 1. 테이블 개요\n"
        "매출 상세 부가 메뉴 / 세부 옵션 / 사이드 메뉴 선택 상세 테이블 (`STRNMNTB`).\n"
        "가맹점별 영업 중 발생한 매출 상품 결제 건 중, 상위 단품 품목(`LINE_NO`에 해당하는 상품)에 딸린 하위 사이드 옵션, 선택 토핑, 부가 메뉴 선택 정보(부가옵션그룹코드 `SUB_GROUP_CD`, 부가메뉴코드 `SUB_MENU_CD`, 추가 수량 `SUB_MENU_QTY` 등)를 영수증(`BILL_NO`) 및 품목 순번 단위로 기록 보존하는 단품 부가 옵션 선택 상세 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 부가 메뉴 및 토핑 선택 적재**: POS 단말기에서 결제 완료 시 매출 패킷을 수신하여 매출 상세(`STRNDTTB`) 레코드와 1:N 상위-하위 관계로 세부 옵션 목록이 `STRNMNTB`에 실시간으로 적재됩니다. (취소 시에는 `STRNDTTB`의 매출구분 상태에 동기화되어 취소/반품 처리가 연동됩니다.)\n"
        "* **옵션 품목 재고 차감 연동 (재고 연동 핵심)**: 부가 메뉴 판매 실적(`SUB_MENU_QTY`)에 매핑된 표준 조리 레시피에 따라, 에스프레소 샷, 시럽, 추가 치즈 등 해당 점포의 세부 원부자재 현재고(`imcriotb`)를 실시간 감산 처리하는 기초 데이터가 됩니다.\n"
        "* **일일 부가메뉴 롤업 집계 및 정산 배치 (`DmSALA11Service` 및 `DmSALA11_SQL` 배치)**: 매일 마감 시점에 점포별 부가 옵션 메뉴의 판매 수량 추이를 롤업 집계하여, 인기 토핑 매출 통계 보고서 및 ERP 원가 대체 인터페이스를 생성 및 전송합니다."
    )

    data["tables"]["strnmntb"] = {
        "memo": strnmntb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "line_no": "영수증 내 상위 메인 판매 단품 품목 순번 (2자리)",
            "sub_group_cd": "부가 옵션 및 세부 메뉴 그룹 코드 (2자리, 예: 샷추가, 시럽선택 등)",
            "sub_menu_cd": "선택된 부가 옵션 및 세부 메뉴 코드 (2자리)",
            "sub_menu_qty": "해당 부가 옵션 메뉴의 추가 선택 및 판매 수량"
        },
        "memo_c": "POS 단말기에서 부가 메뉴 또는 추가 토핑을 선택하여 결제 완료 시 실시간 매출 트랜잭션을 통해 생성 기록됩니다.",
        "memo_u": "영수증 재출력이나 취소 거래 연동, 할인 구분 보정 시 데이터가 업데이트됩니다.",
        "memo_d": "가맹점 원부자재 레시피 소요량 차감 및 세무 마진 분석 증빙 자료이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "부가메뉴별 매출 분석, 매장 원부자재 재고 차감 및 ERP 부가 옵션 정산 배치 시 최우선 옵션 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매출 품목 상세 원장(STRNDTTB)의 상위 단품 품목 순번(LINE_NO)에 연계되는 하위 사이드 옵션/토핑/세부 부가 메뉴 수량 정보를 연결하는 1:N 상위-하위 단품 관계를 맺습니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객 거래의 총괄 매출 일자 및 영수증 마스터와 부가 메뉴 상세 간의 식별 정보를 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별로 부가 메뉴(사이드 옵션) 가격 체계 및 제공 서비스 한도를 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 선택된 부가 메뉴 코드(sub_menu_cd)의 표준 판매가, 원가, 부가세 구분 및 완제품 재고 차감 여부를 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별로 단품당 최대 추가 가능한 부가 옵션 그룹 개수 제한(예: 최대 토핑 5개 제한) 등의 POS 시스템 작동 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 부가 옵션 그룹명(예: 샷추가, 시럽선택, 사이즈업 등) 및 한글 옵션 유형 라벨명을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 레시피 관리 화면에서 부가 메뉴별 매핑 원부자재 소요량을 등록/수정하는 상품 기획 담당자의 계정 권한을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 표준 규격 부가 옵션 분류와 가맹점 등록 옵션의 매칭 정합성을 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 부가 메뉴 판매 수량 추이에 따라 매장의 세부 원부자재(예: 파우더, 시럽, 포장재 등) 자동 발주 소요량을 산출할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. [재고 연계 핵심] 부가 메뉴(예: 샷추가, 치즈추가) 판매에 매핑된 조리 레시피 상의 세부 원부자재 실시간 현재고 수량을 매장에서 감산하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 부가 메뉴 추가에 따른 순마진율(정가 대비 원자재 원가비율)을 선입선출 매입단가 기반으로 정확히 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 부가 메뉴 전송 패킷의 누락 오류 및 메뉴 매칭 불일치 로그를 감사하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 79. STRNPMTB MEMO AND RELATED TABLES
    strnpmtb_memo = (
        "### 1. 테이블 개요\n"
        "매출 행사/프로모션 적용 및 정산 상세 테이블 (`STRNPMTB`).\n"
        "가맹점별 영업 중 발생한 매출 결제 건 중, 본사 주관 브랜드 프로모션, 제휴 이벤트, 마케팅 할인 행사 등을 적용하여 영수증 대금의 할인이 발생한 승인 상세 내역(프로모션코드 `PROMOTION_CD`, 프로모션명 `PROMOTION_NM`, 할인액 `DC_AMT`, 본사-가맹점 분담요율 `PROC_RATE`, 대상거래액 `FACE_SALE_AMT` 등)을 영수증(`BILL_NO`) 및 프로모션 적용 단위로 상세 기록하는 프로모션 정산 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 프로모션 적용 내역 수집**: POS 단말기에서 결제 단계 중 등록된 행사 바코드 인식 또는 카드사 제휴 프로모션 조건 충족 시, 승인망 전문 조회를 통해 프로모션 할인 정보가 매출 헤더(`STRNHDTB`)의 프로모션 할인 총액과 링크되는 동시에 `STRNPMTB`에 실시간 생성 적재됩니다. (취소 거래 시에는 `sale_fg = '1'` 취소분이 음수 보정으로 적재됩니다.)\n"
        "* **행사 실적 실시간 롤업 집계 (`STRNPM_T01` 트리거)**: `STRNPMTB`에 신규 할인 행사가 삽입되면 `STRNPM_T01` 트리거가 실행되어, 일별 프로모션 실적 대장(`SDAYPMTB`)에 해당 행사의 일일 누적 거래 객수(`bill_cnt`), 누적 할인 합계액(`sale_dc_tot`) 등을 실시간으로 업데이트 집계 처리합니다.\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점별 일일 결산 배치 실행 시, 각 프로모션 행사별 할인 분담 비율(`proc_rate`)을 `STRNPMTB` 원장에서 자동으로 읽어와 본사 부담금 및 가맹점 정산용 대차 분개를 작성하고 본사 ERP 재무 시스템으로 전송합니다."
    )

    data["tables"]["strnpmtb"] = {
        "memo": strnpmtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "sale_fg": "매출 구분 코드 (0: 정상 매출/행사할인, 1: 취소/반품/할인취소)",
            "promotion_year": "프로모션 및 행사 등록 기준 연도 (YYYY)",
            "promotion_cd": "프로모션 및 행사 관리 고유 코드 (4자리)",
            "promotion_nm": "프로모션 및 행사 공식 한글 명칭",
            "proc_fg": "프로모션 할인 비용의 정산 처리 상태 및 분류 코드",
            "dc_rate": "해당 제휴 행사 계약에 의해 적용된 요율 기준 할인 비율",
            "proc_rate": "본사 및 가맹점 간의 프로모션 할인 비용 분담 요율 (예: 50.00%)",
            "good_proc_fg": "행사 대상 상품 조건 구분 코드 (0: 전체 상품 대상, 1: 특정 행사 단품 지정 등)",
            "cust_card_no": "할인 적용에 매칭된 고객 신용카드 또는 제휴사 카드 번호",
            "face_sale_amt": "해당 프로모션이 적용되기 전 정가 기준의 원 상품 판매 가액",
            "dc_amt": "해당 거래에서 실제 프로모션 할인을 적용받아 감면된 금액 총액",
            "sale_point": "제휴 프로모션 승인에 의해 추가 적립된 제휴 포인트 점수",
            "sale_dtime": "프로모션 할인 거래 승인 처리 완료 시각 (YYYYMMDDHH24MISS)",
            "amt_rate": "금액 기준 할인 요율 매칭 비율",
            "promotion_kind": "프로모션 종류 구분 코드",
            "pm_kind": "행사 상세 분류 식별자"
        },
        "memo_c": "POS 결제 승인 완료 시 프로모션 할인 조건 검증 및 서버 승인을 거쳐 실시간으로 생성 기록됩니다.",
        "memo_u": "프로모션 정산 마감 정정, 본사 정산 분담 비율 조정 및 정산금 입금 완료 시 데이터가 업데이트됩니다.",
        "memo_d": "본사와 가맹점 간의 마케팅 비용 정산 분담 및 회계 감사 세무 증빙의 기준 자료이므로 임의 삭제가 영구 불허됩니다.",
        "memo_r": "프로모션 할인 실적 분석, 본사-가맹점 정산 수수료 대사 보고서 작성, ERP 회계 마감 세무 정산 송신 배치 시 최우선 프로모션 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제 단계에서 본사 주관 브랜드 프로모션이나 행사 할인을 적용받으면, 매출 마스터 헤더(STRNHDTB)의 프로모션 할인 총액과 매핑되는 개별 승인 내역으로 STRNPMTB에 상세 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별 프로모션 정산 참여 여부 및 본사/가맹점 간의 할인 비용 분담 요율을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. [트리거 STRNPM_T01 연동] 프로모션 행사 적용 대상 상품 플래그(PROM_GOOD_FG = '1') 여부를 대조하여, 상세 품목 단위의 공급가 및 할인 가액 정합성을 확인하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "sdaypmtb",
                "description": "일별 프로모션 실적 대장 테이블. [트리거 STRNPM_T01 연동] STRNPMTB에 신규 할인 행사가 적재되면, 프로모션별, 영업일자별 누적 거래 객수(bill_cnt), 할인 합계액(sale_dc_tot) 등을 실시간으로 업데이트 집계합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 프로모션 대상 품목(특정 단품 또는 카테고리) 및 행사 가격의 유효성을 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별로 동일 영수증 내 최대 프로모션 중복 적용 개수 제한 및 예산 임계치 등의 시스템 작동 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 프로모션 종류 구분 코드(promotion_kind), 처리 구분 코드(proc_fg), 제휴 카드 구분 한글 라벨명을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 행사 등록 화면에서 신규 브랜드 프로모션 마스터 및 가맹점 정산 분담 비율을 최초 등록/수정한 정산 관리자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 표준 규격 행사 대상 품목 명칭 및 본사 물류 출고 원가 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 행사 보조 정산금 입금 처리 시 본사 발주 상품 공급가 정산 채무와의 대사 처리를 비교하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 특정 프로모션 행사 단독 진행에 따른 상품 재고 소진율 및 원자재 레시피 소요량 대비 현재고 수량 밸런스를 검증하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 프로모션 할인 차감액 대비 본사 원부자재 선입선출 매입단가 기반으로 가맹점 순마진율을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 프로모션 승인 패킷 통신 오류 또는 수동 한도 조정 이력을 감사용 로그에 기록하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 80. STRNWETB MEMO AND RELATED TABLES
    strnwetb_memo = (
        "### 1. 테이블 개요\n"
        "매출 일반 외상 / 단체 외상 / 제휴사 수납대행 외상 결제 상세 테이블 (`STRNWETB`).\n"
        "가맹점별 영업 중 발생한 매출 결제 건 중, 외상 판매(거래처 외상 `WEAS_AMT`, 사내 부서 외상 `DEPT_AMT`, 또는 제휴 수납대행 외상 청구 등)를 적용한 구체적인 내역(외상금액 `WEAS_AMT`, 입금완료금액 `PAID_AMT`, 거래처코드 `VENDOR_CD`, 외상유형 `VENDOR_WE_TYPE`, 수납완료여부 `PROC_FG`, 수수료 `FEE` 등)을 영수증(`BILL_NO`) 및 외상 일련번호 단위로 보관하는 외상 매출/미수금 상세 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 외상 결제 적재**: POS 단말기에서 결제 수단으로 일반 외상이나 거래처 외상을 선택하여 승인 완료 시, 매출 헤더(`STRNHDTB`)의 총 외상 청구액(`weas_amt`)과 링크되는 동시에 외상 대상 거래처 정보가 `STRNWETB`에 실시간으로 생성 적재됩니다. (반품 취소 시에는 `sale_fg = '1'` 취소 거래가 연동 기록됩니다.)\n"
        "* **일일 수납 마감 및 정산 배치 (`DmSALA11Service` 및 `DmSALA11_SQL` 배치)**: 매일 밤 가맹점 결산 시점에, 당일 발생한 외상 매출을 정산 원장 및 수납 대사 테이블로 이관 처리하여 사후 수납 입금액(`paid_amt`)과의 매칭을 준비합니다.\n"
        "* **ERP 회계 연동 및 정산 처리 (`Sp_SUB_IF_HYDM_SEND_P` 프로시저)**: 가맹점 일일 정산 마감 배치 시, 외상 매출 및 미수금 현황을 `STRNWETB` 원장 기반으로 롤업하여 본사 ERP 재무 회계 시스템으로 외상 매출 미수금 대체 분개를 자동 생성해 전송합니다."
    )

    data["tables"]["strnwetb"] = {
        "memo": strnwetb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "line_no": "영수증 내 외상 결제 상세 일련 순번 (4자리)",
            "chain_no": "체인 및 계열사 분류 코드",
            "chain_area": "체인 소속 지역 분류 번호",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품/외상취소)",
            "emp_id": "해당 외상 결제를 처리한 POS 캐셔/담당 사원 ID",
            "weas_amt": "해당 거래처/제휴사 외상으로 청구 승인된 외상 총액",
            "remark": "외상 거래 시 입력한 상세 비고 및 거래처 참조 메모",
            "weas_fg": "외상 처리 유형 구분 코드 (0: 일반 외상, 1: 부서 외상, 2: 제휴사 위탁외상)",
            "paid_amt": "사후에 실입금 처리 완료된 외상 회수/수납 금액 누적액",
            "paid_cnt": "외상 입금/수납 처리 횟수 일련 카운트",
            "proc_dtime": "외상 거래 승인 처리 완료 시각 (YYYYMMDDHH24MISS)",
            "vendor_cd": "외상 주체가 되는 제휴사 및 고객 거래처 고유 코드 (13자리)",
            "sale_vat": "외상 청구 금액 내에 포함된 개별 부가세액",
            "net_sale_amt": "외상 청구 금액 중 부가세를 제외한 순공급가액",
            "vendor_we_type": "외상 결제 유형 분류 (0: 신용카드사, 1: 일반 거래처, 2: 부서대체)",
            "vendor_we_cd": "외상 결제 상세 매핑 연동 코드",
            "fee": "외상 제휴 결제 수수료 또는 위탁 공제 수수료액",
            "proc_fg": "외상 대금 최종 수납 완료 여부 플래그 (Y: 완료, N: 미결제/미수금)",
            "coal_no": "제휴 연합 연맹 번호 (5자리)",
            "coal_nm": "제휴 연합 연맹 공식 한글 명칭",
            "cust_cd": "할인 및 수납 대상 고객 거래처 고유 코드 (10자리)",
            "coal_stoa_mthd": "제휴사 정산 방식 및 조건 코드",
            "acsm_issu_clsf": "정산 청구서 및 계산서 발행 구분 코드",
            "stoa_clsf_cd": "정산 상세 대사 분류 코드",
            "fee_rt": "제휴 위탁 외상 수수료 요율",
            "tax_free_amt": "외상 결제 금액 중 면세 상품 해당 공급가액"
        },
        "memo_c": "POS 단말기 결제 완료 시 외상 결제 수단 승인을 통해 실시간으로 생성 기록됩니다.",
        "memo_u": "사후 외상 입금 완료, 본사 외상 정산 대사 완료 및 입금액 수동 보정 시 데이터가 업데이트됩니다.",
        "memo_d": "가맹점 미수금 회수 관리 및 회계/세무 정산 증빙 자료이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "외상 매출 현황 조회, 외상 정산 대사 보고서 작성, ERP 회계 정산 배치 송신 시 최우선 외상 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 고객이 결제 시 외상을 선택하면, 매출 마스터 헤더(STRNHDTB)의 외상 지불 총액(weas_amt 또는 dept_amt)과 연계되는 개별 외상 상세 내역으로 STRNWETB에 분할 저장됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별 외상 거래 계약 및 본사 보증 한도를 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 외상 판매 대상 품목의 단가, 과세 구분 및 공급가 비율을 확인하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 외상 거래 대상이 되는 특정 케이터링 또는 연회 상품 표준 단가를 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별로 외상 거래가 허용되는 바이어/거래처 한도 한계값 및 정산 주기 정책 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 외상 거래 구분 코드(weas_fg), 외상 유형(vendor_we_type), 수납 상태 한글 라벨명을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 외상 입금 정산 및 수납 마감 화면에서 수동 수납 승인 처리를 입력한 정산 조작자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 외상 거래에 매핑된 상품 단가의 표준 마진 변동을 본사 수준에서 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 외상 회입 정산금 수납 시 본사 원자재 출고 대금 채무와의 상계 정합성을 대조하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 외상으로 대량 주문/납품된 단품의 재고 차감 및 점포 잔량 관리를 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 외상 매출 수납 단가 대비 선입선출 매입단가 기반으로 가맹점 순마진율을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 외상 결제 시 가맹점 실시간 전송 패킷 통신 오류 또는 한도 조정 이력을 추적 감사하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 81. SVANCOTB MEMO AND RELATED TABLES
    svancotb_memo = (
        "### 1. 테이블 개요\n"
        "POS 단말기별 실시간 VAN사 승인 환경설정 동기화 큐 테이블 (`SVANCOTB`).\n"
        "각 가맹점의 POS 단말기 번호별로 할당된 신용카드 및 현금영수증 VAN사 설정(메인/서브 VAN사 IP `VAN_IP`/`SUB_VAN_IP`, 포트번호 `VAN_PORT_NO`, VAN사명, 단말기 식별 ID `CAT_ID`, 트래픽 분할 비율 `RATE` 등) 변경 내역을 실시간으로 보관하는 동기화용 트랜잭션 큐(Transaction Queue) 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **VAN 설정 변경 사항 실시간 적재 (`MVANCO_T01` 트리거)**: 백오피스 단말기 승인 관리 화면을 통해 가맹점별 POS 기기의 VAN사 정보, IP/포트 또는 CAT ID가 등록/수정/삭제(`MVANCOTB` 테이블 변동)되면, `MVANCO_T01` 트리거가 작동하여 `VANMSTTB` 마스터 설정을 참조해 최신 IP/Port 정보가 포함된 동기화 패킷을 `SVANCOTB`에 일련번호(`log_seq`) 및 처리구분(`proc_fg`)과 함께 인서트합니다.\n"
        "* **POS 실시간 동기화 전문 연동**: 대기 중이던 POS 통신 인터페이스 모듈(Telex M61/S10 Mapper)이 기동 시점 또는 주기적으로 본 큐(`SVANCOTB`)를 대조하여 새로 생성된 VAN 설정 변경 내역이 존재하면, 해당 가맹점 POS 단말기로 설정 데이터를 즉시 다운로드 전송하여 카드 단말기 설정을 실시간 재동기화 반영시킵니다."
    )

    data["tables"]["svancotb"] = {
        "memo": svancotb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "매장코드 (점포 코드)",
            "log_seq": "로그 식별 일련번호 (YYYYMMDD + 8자리 시퀀스)",
            "proc_dtime": "처리 등록 일시 (YYYYMMDDHH24MISS)",
            "proc_fg": "처리 구분 (A: 추가/등록, U: 수정, D: 삭제)",
            "van_cd": "메인 VAN사 식별 코드 (2자리)",
            "van_ip": "메인 VAN사 승인 서버 IP 주소",
            "van_port_no": "메인 VAN사 승인 서버 포트 번호",
            "van_name": "메인 VAN사 정식 한글 명칭",
            "van_fg": "VAN사 업무 구분 코드 (0: 신용카드 승인, 1: 현금영수증 승인)",
            "cat_id": "해당 단말기에 부여된 고유 VAN 가맹점 번호 (CAT ID, 10자리)",
            "pos_fg": "단말기 하드웨어 구분 코드 (0: POS 단말기, 1: 일반 유/무선 카드단말기)",
            "sub_van_fg": "예비(SUB) VAN사 적용 여부 구분 플래그 (0: 사용안함, 1: 사용)",
            "sub_van_cd": "예비 VAN사 식별 코드",
            "sub_van_ip": "예비 VAN사 승인 서버 IP 주소",
            "sub_van_port": "예비 VAN사 승인 서버 포트 번호",
            "sub_van_name": "예비 VAN사 정식 명칭",
            "sub_cat_id": "예비 VAN사용 가맹점 번호 (CAT ID)",
            "rate_fg": "VAN 승인 트래픽 분할(스플릿) 사용 여부 (0: 미사용, 1: 사용)",
            "rate": "메인 VAN사 처리 분담 요율 비율 (예: 60.00%)",
            "pos_no": "매장 내 POS 기기 식별 번호 (2자리)"
        },
        "memo_c": "백오피스 단말기 승인 관리 마스터(MVANCOTB) 변경 시 MVANCO_T01 트리거에 의해 실시간으로 자동 생성 기록됩니다.",
        "memo_u": "동기화 전송이 성공적으로 완료되어 POS 적용 완료 피드백을 기록하거나 이력 사후 관리를 위한 상태 조율 시 업데이트됩니다.",
        "memo_d": "가맹점별 실시간 승인 경로 동기화를 위한 동기화 대기 큐이자 이력 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS VAN 설정 배포 모듈, 매장별 VAN 단말기 상태 조회 및 승인 경로 모니터링 시 기초 자료로 롤업 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mvancotb",
                "description": "매장 단말기별 VAN 설정 테이블. 각 가맹점의 POS 단말기 번호별로 할당된 신용카드 및 현금영수증 VAN사 설정 마스터(MVANCOTB)와 동기화 변경 이력(SVANCOTB) 간의 1:1 대응 원천 마스터 관계를 형성합니다."
            },
            {
                "table_name": "vanmsttb",
                "description": "VAN사 정보 마스터 테이블. [트리거 MVANCO_T01 연동] 각 VAN사 코드에 해당하는 메인/서브 VAN사 서버 IP 주소, 통신 포트 번호, VAN사 한글 정식 명칭을 조회하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포의 소속 체인 및 프랜차이즈 계약 상태를 조회하여, 해당 매장의 POS 기기들에 실시간 VAN 설정을 배포 필터링할 때 조인됩니다."
            },
            {
                "table_name": "mvansttb",
                "description": "매장 공통 VAN 설정 테이블. 매장 단말기별 상세 개별 정보(svancotb)와 매장 단위 공통 VAN사 통신 설정을 비교 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 단위별 결제 승인 최대 재시도(Retry) 시간 및 타임아웃 기본 임계값 등의 시스템 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. VAN 구분 코드(van_fg), 처리 상태 코드(proc_fg), 단말기 구분 코드(pos_fg)에 대응하는 한글 라벨명을 조인하여 매치하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 단말기 승인 관리 화면에서 특정 가맹점의 VAN 단말기 식별 번호(CAT ID)나 트래픽 분할 비율(rate)을 변경한 담당자의 사번을 규명하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 특정 제휴 카드/VAN사 공동 할인 상품권 유효 기간 검증을 위해 본사 상품 속성과 매칭할 때 간접 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 카드 수수료 대사 및 실 수납금 정산 시 본사 발주 상품의 공급 정산 계정과 비교 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 실시간 통신 동기화 이력 관리의 간접 성격 테이블이므로 직접적인 재고 수량 연계는 없으나 점포 상태 대조를 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 카드 VAN사별 거래 수수료 공제 요율 변동에 따른 최종 정산액 대비 원부자재 선입선출 원가 기반 가맹점 순마진율을 시뮬레이션할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. [트리거 MVANCO_T01 연동] VAN 설정 동기화 전문이 POS 단말기로 전송 완료되거나 에러가 발생한 통신 이력을 감사 로그에 기록 보존하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 82. TB_COST MEMO AND RELATED TABLES
    tb_cost_memo = (
        "### 1. 테이블 개요\n"
        "본사 상품 물류/매입 표준 원가 변동 이력 원장 테이블 (`TB_COST`).\n"
        "본사에서 취급 및 가맹점에 유통 공급하는 개별 원부자재 및 완제품 상품(`GOODS_CD`)에 대한 표준 공급/매입 원가의 변동 내역(변경 후 원가 `UCOST`, 원가부가세 `UCOST_VAT`, 이전 원가 `PRE_UCOST`, 적용일자 `PROC_DATE`, 시퀀스 `SEQ` 등)을 체인별로 보존하는 물류 기준 원가 이력 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **원가 정보 입력 시 이전 이력 자동 추적 (`TB_COST_T01` 트리거)**: 본사 MD 및 정산 담당자가 신규 계약 또는 원재료 단가 인상/인하 등으로 신규 표준 원가를 등록(`INSERT`)하면, `TB_COST_T01` 트리거가 실행되어 본 테이블 내 직전 변동 이력을 조회한 후 이전 원가(`pre_ucost`)와 이전 원가 부가세(`pre_ucost_vat`)를 자동으로 대조 할당하여 삽입합니다.\n"
        "* **본사 상품 마스터 단가 갱신 연동 (Java Trigger Service)**: 원가 정보가 정상 등록되면, 동기화 자바 서비스(`Tr_TB_COST_T01_Service.java`) 또는 내부 프로시저가 동작하여 본사 상품 정보 마스터 테이블(`TGOODSTB`)의 현재 표준 원가(`ucost` 및 `ucost_vat`) 컬럼을 신규 공급 원가로 자동 동기화 갱신합니다.\n"
        "* **가맹점 손익 및 자산 평가 시뮬레이션**: 백오피스 물류 마진 분석 보고서, 매장 현재고의 자산 평가액(재고수량 * 표준 공급가) 산정 시 해당 변동 일자 기준의 유효 원가 단가를 매칭 참조하는 원천 자료가 됩니다."
    )

    data["tables"]["tb_cost"] = {
        "memo": tb_cost_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 계열사 분류 코드 (4자리)",
            "goods_cd": "원가 변동이 발생한 본사 취급 상품/원자재 코드 (20자리)",
            "seq": "해당 상품의 원가 변동 이력 일련번호 (15자리 시퀀스)",
            "proc_date": "신규 원가가 가맹점 유통 및 정산에 적용되기 시작하는 기준 영업일자 (YYYYMMDD)",
            "ucost": "해당 변동 차수에 새로 확정/적용된 표준 매입/공급 원단가",
            "ucost_vat": "해당 변동 표준 원단가에 포함된 부가세액",
            "pre_ucost": "원가 변동 적용 직전의 직전 차수 표준 매입 원가",
            "pre_ucost_vat": "직전 차수 표준 매입 원가 부가세액",
            "create_dtime": "원가 변경 등록 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "원가 정보를 최초 등록 승인한 담당자 사원번호/계정 ID",
            "last_dtime": "원가 정보 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "원가 정보를 최종 수정 승인한 담당자 ID"
        },
        "memo_c": "본사 구매/물류 원단가 계약 변경 시 백오피스 표준 단가 관리 모듈을 통해 신규 인서트됩니다.",
        "memo_u": "원가 적용 개시일자 조정 또는 오등록 단가 수정 승인 시 업데이트됩니다.",
        "memo_d": "프랜차이즈 물류 재고 자산 평가 및 매출 총이익 회계 감사의 기초 이력이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "본사 상품 마스터 최신 원가 갱신, 매장 입고 물류 단가 대조, 선입선출 손익 보고서 시뮬레이션 시 최우선 원가 이력으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [트리거 TB_COST_T01 연동] 신규 매입 원가가 등록되면 상품 마스터(TGOODSTB)의 현재 표준 원가(UCOST 및 UCOST_VAT) 컬럼을 최신으로 갱신하는 타깃 마스터 관계를 맺습니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점 체인 유형(chain_no)별 표준 물류 공급 원가 정책을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 본사에서 수정한 원단가 변동 내역이 각 가맹점 매장별 로컬 상품 단가와 마진 비율에 미치는 영향을 계산하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 판매 품목별 마진 분석 시, 매출 영수증 판매 시점의 표준 원가를 tb_cost 변동 이력에서 조회하여 품목별 매출총이익 정합성을 사후 대조할 때 간접 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 본사 원가 등록 시 최대 허용 단가 한계선 및 적용 개시일자 유효성 검증 규칙 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 상품 대/중/소 분류 및 제조 국가 코드, 원가 과세 구분 등 상품 속성의 한글 명칭 라벨을 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 신규 매입 표준 원가를 입력하고 최종 승인한 본사 구매/물류 정산 담당자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 원자재 발주 입고 시 본사 물류 표준 출고가(ucost) 정합성을 검증하기 위해 조인 참조합니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 매장 현재고 자산 금액 평가(재고 수량 * 표준 물류 원가)를 본사 원가 이력 기준으로 평가하여 자산 변동 보고서를 산정할 때 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 선입선출 매입단가 기록과 본사 표준 원가 이력(tb_cost)의 단가 흐름 추이를 상호 대조 분석하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 표준 원가 강제 변경 이력 및 오조작 수정 로그를 감사하고 보존하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 가맹점 총 공급가액 매출액과 표준 원가 기반 COGS(Cost of Goods Sold) 비율을 롤업하여 영업 총손익 시뮬레이션을 도출할 때 간접 참조됩니다."
            }
        ]
    }

    # 83. TB_IF_SA_POS_ACCOUNT_IO_CTNT MEMO AND RELATED TABLES
    tb_if_sa_pos_account_io_ctnt_memo = (
        "### 1. 테이블 개요\n"
        "POS 시출금/시재 입출금 연동 인터페이스 원장 테이블 (`TB_IF_SA_POS_ACCOUNT_IO_CTNT`).\n"
        "가맹점 POS 단말기에서 영업 근무 조별 시재금 등록, 준비금 보충, 중간 현금 수금(시출금), 교대 마감 시 발생한 시재금 입출금 거래 상세 데이터를 수신 일련번호(`PROC_SN`), 입출금 일자(`ACCIO_DATE`), 매장코드(`MS_NO`), POS번호(`POS_NO`), 저널 JSON 내용(`JOURNAL_CTNT`), 처리 플래그(`PROC_FG`) 등으로 구조화하여 임시 저장하는 인터페이스 staging 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 실시간 시재 거래 전송 수신**: POS에서 시재 입출금 이벤트 발생 시 관련 저널 전문 정보(입출금 유형, 금액, 캐셔 ID 등)가 JSON 문자열 포맷으로 직렬화(`journal_ctnt`)되어 `TB_IF_SA_POS_ACCOUNT_IO_CTNT`에 실시간 생성 적재됩니다. (수신 직후 `proc_fg = '0'` 대기 상태)\n"
        "* **일일 시재 인터페이스 동기화 배치 (`DmSALT10Service` 및 `DmSALT10_SQL` 배치)**: 일별 정산 가동 시, 동기화 배치 데몬이 본 테이블의 미처리 레코드(`proc_fg = '0'`)를 차례대로 읽어와 JSON 데이터를 구문 분석(Parsing)한 후, 코어 매장 시재 입출금 마스터 테이블(`MACCIOTB`)에 정식 회계 거래 내역으로 변환 삽입하고 본 레코드를 `proc_fg = '1'`(처리 완료) 상태로 갱신합니다. (오류 발생 시 `proc_fg = '9'` 및 에러 사유를 `proc_msg`에 기록)\n"
        "* **세무 감사 및 현금 과부족 대사**: 매장의 실제 금고 내 현금 잔액과 POS 마감 전송 현금액, 그리고 본 시재 입출금 인터페이스 원장 이력을 대조하여 가맹점 현금 분실 및 오입력 수납 불일치 원인을 역추적 감사하는 감정 원장 역할을 합니다."
    )

    data["tables"]["tb_if_sa_pos_account_io_ctnt"] = {
        "memo": tb_if_sa_pos_account_io_ctnt_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_sn": "시재 입출금 수신 인터페이스 고유 일련번호 (SQ_IF_SA_POS_ACCOUNT_IO_CTNT 시퀀스 사용)",
            "accio_date": "POS에서 실제 시재 입출금 거래를 승인/실행한 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "proc_fg": "인터페이스 처리 상태 코드 (0: 수신대기, 1: 처리완료, 9: 오류/실패)",
            "proc_msg": "인터페이스 처리 결과 상태 메시지 및 예외 에러 세부 로그",
            "journal_ctnt": "POS 시재 입출금 상세 내역을 담은 저널 원천 데이터 (JSON 포맷)",
            "regi_id": "최초 인터페이스 전문 수신 등록 처리 담당자/시스템 ID",
            "regi_dtime": "인터페이스 수신 레코드 최초 생성 등록 일시",
            "updt_id": "인터페이스 최종 처리 업데이트 담당자 ID",
            "updt_dtime": "인터페이스 최종 처리 완료 및 상태 갱신 일시"
        },
        "memo_c": "POS 단말기에서 시재금 변동, 준비금 보충, 중간 시출금 실행 시 연동 전문 수신을 통해 실시간 인서트됩니다.",
        "memo_u": "동기화 배치 처리 완료 시 처리 상태(proc_fg) 및 오류 내용이 업데이트됩니다.",
        "memo_d": "가맹점 일일 현금 흐름 및 정산 감사 추적의 원천 이력이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "일일 시재 정산 배치 서비스, 매장 현금 과부족 분석 보고서 조회, POS 마감 정합성 검증 배치 시 연동 큐로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "macciotb",
                "description": "매장 시재 입출금 마스터 테이블. [배치 DmSALT10Service 연동] tb_if_sa_pos_account_io_ctnt 인터페이스 원장의 JSON 데이터(journal_ctnt)를 파싱하여 실시간 매장 시재 입출금 대장(MACCIOTB)에 변환 적재하는 핵심 대상 마스터 관계입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 입출금 발생 점포의 체인 계약 속성 및 세무 마감 예외 여부를 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일일 매출 현금 시재 정산 시, POS에 보관 중인 마감 현금 잔액과 시재 입출금(TB_IF_SA_POS_ACCOUNT_IO_CTNT) 이력을 대조하여 현금 과부족(시재 불일치)을 규명하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 시재 시출금 거래 자체는 상품 판매가 아니므로 상품 마스터 조인은 발생하지 않으나, 상품권 교환 판매 등으로 현금 시재가 발생한 수납대행 상품과의 가격 검증을 위해 간접 대조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 POS 시작 시점의 교대 시재금(준비금) 기본 설정 금액 및 중간 시출금 권장 한도 등의 작동 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 시재 입출금 구분 코드(예: 시재 보충, 중간 시출금, 영업외 시출금 등) 및 처리 상태 코드(proc_fg)에 대응하는 한글 라벨명을 조인하여 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 시재 입출금을 입력 및 승인한 POS 캐셔 사번(regi_id)의 소속 점포 권한 및 실명을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 정산 지침에 따른 수납대행 상품권 시재금 대체 규정을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 소액 현금 시재로 긴급 현물 구매 처리(소모품 매입)한 영수증을 시재 입출금 이력과 대사 비교할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 시재금 변동 자체와 재고는 직접 연관되지 않으나, 현금 구매 상품의 재고 실사 변동 내역과 비교 감사할 때 간접 대조됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 매장 소액 시재금으로 현지 구매한 원자재의 원가 배부를 선입선출법에 수동 반영할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 시재 입력 시 통신 인터페이스 오류 이력이나 수동 시재 보정 로그를 보안 감사하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 84. TB_IF_SA_POS_ACCOUNT_IO_CTNT_LOG MEMO AND RELATED TABLES
    tb_if_sa_pos_account_io_ctnt_log_memo = (
        "### 1. 테이블 개요\n"
        "POS 시출금/시재 입출금 연동 인터페이스 완료 이력 로그 테이블 (`TB_IF_SA_POS_ACCOUNT_IO_CTNT_LOG`).\n"
        "가맹점 POS 단말기에서 전송된 시재 입출금 인터페이스 원천 레코드 중, 동기화 배치 프로그램(`DmSALT10Service`)에 의해 분석 및 처리가 성공적으로 완료(또는 영구 실패)되어 대기 큐에서 완료 이력 아카이브 보관소로 이관된 과거 시재 입출금 연동 데이터 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **동기화 배치 처리 완료 후 이관**: 일일 정산 가동 시, 동기화 배치 데몬이 `TB_IF_SA_POS_ACCOUNT_IO_CTNT` 테이블의 미처리 레코드(`proc_fg = '0'`)를 성공적으로 처리(매장 시재 입출금 마스터 `MACCIOTB`에 반영 완료)하면, 해당 레코드를 본 로그 테이블(`TB_IF_SA_POS_ACCOUNT_IO_CTNT_LOG`)로 복사 인서트한 후 원본 staging 테이블에서는 삭제하여 큐 테이블을 항상 슬림한 상태로 유지 관리합니다.\n"
        "* **과거 시재 변동 추적 및 영수증 대사**: POS 캐셔 교대 시 또는 일일 가맹점 마감 결산 시 현금 과부족(시재 불일치) 불일치가 발생할 경우, 사후 감사 및 역추적을 위해 이 테이블에 보관된 과거 시재금 변동 저널 로그(`journal_ctnt` JSON)를 조회하여 오입력 원인을 감사 분석하는 보조 원장 역할을 수행합니다."
    )

    data["tables"]["tb_if_sa_pos_account_io_ctnt_log"] = {
        "memo": tb_if_sa_pos_account_io_ctnt_log_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_sn": "시재 입출금 수신 인터페이스 완료 이력 고유 일련번호 (staging 테이블의 proc_sn과 동일)",
            "accio_date": "POS에서 실제 시재 입출금 거래를 실행했던 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "proc_fg": "최종 인터페이스 동기화 처리 상태 코드 (1: 처리완료, 9: 오류/실패)",
            "proc_msg": "최종 동기화 처리 결과 결과 상태 메시지 및 예외 에러 세부 로그",
            "journal_ctnt": "POS 시재 입출금 상세 내역을 담은 저널 원천 데이터 (JSON 포맷)",
            "regi_id": "최초 인터페이스 전문 수신 등록 처리 담당자/시스템 ID",
            "regi_dtime": "인터페이스 수신 레코드 최초 생성 등록 일시",
            "updt_id": "인터페이스 최종 완료 처리 업데이트 담당자 ID",
            "updt_dtime": "인터페이스 최종 완료 처리 및 상태 갱신 일시"
        },
        "memo_c": "동기화 배치 처리 완료 시, DmSALT10Service에 의해 staging 테이블(TB_IF_SA_POS_ACCOUNT_IO_CTNT)로부터 복사 생성됩니다.",
        "memo_u": "아카이브 완료 상태 로그 원장이므로 최초 이관 이후에는 원칙적으로 업데이트가 발생하지 않습니다.",
        "memo_d": "가맹점 과거 시재금 변동 추적 및 회계 감사 세무 증빙의 이력 로그 자료이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "과거 가맹점 현금 과부족 분석 보고서 조회, POS 마감 오차 사후 추적, 정산 감사 시스템 조회 시 이력 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_if_sa_pos_account_io_ctnt",
                "description": "POS 시재 연동 인터페이스 원장 테이블. [배치 DmSALT10Service 연동] 실시간 수신 인터페이스 대기열(TB_IF_SA_POS_ACCOUNT_IO_CTNT)에서 성공적으로 분석 및 동기화 처리가 끝난 레코드를 본 로그 테이블로 이관 후 staging 테이블에서 삭제 처리합니다."
            },
            {
                "table_name": "macciotb",
                "description": "매장 시재 입출금 마스터 테이블. 인터페이스 큐를 통해 최종 반영된 매장 시재금의 개별 원장 실 데이터 정합성을 추적 감사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 가맹점 마감 시 시재 오차 및 현금 과부족(시재 불일치) 사고 발생 시, 사후 원인 분석을 위해 과거 시재 변동 저널 로그(TB_IF_SA_POS_ACCOUNT_IO_CTNT_LOG)를 역추적 조인 참조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별 영업 구역 및 프랜차이즈 계열 계약의 이력 대조를 위해 점포코드(ms_no) 기준으로 매칭됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 가맹점 현금 시재 변동과 대치된 특수 교환/환불 상품의 가격 속성을 사후 감사하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 준비금 보충 한계값 변경 또는 중간 시출금 권장 금액 규정 변경 등의 역사적 변수 이력을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 입출금 구분 한글 명칭 및 배치 완료 처리 상태 코드(proc_fg) 명칭을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 과거 특정 시점에 시재 입출금을 등록한 POS 담당 캐셔 사번의 실명 및 퇴사 여부 등을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 수납대행 제휴사 정산금 시재 대체 이력을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 과거 시재금으로 현지 구매한 잡비 지출건의 물류 정산 매입 내역과 세무 증빙을 비교할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 시재 지출과 상품 재고 변동의 실사 일관성을 감사하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 시재 지출로 현지 조달한 부자재의 원가 흐름을 간접 분석하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 85. TB_IF_SA_POS_CNCL_BF_SA_CTNT MEMO AND RELATED TABLES
    tb_if_sa_pos_cncl_bf_sa_ctnt_memo = (
        "### 1. 테이블 개요\n"
        "POS 결제 전/직전 취소 전문 인터페이스 원장 테이블 (`TB_IF_SA_POS_CNCL_BF_SA_CTNT`).\n"
        "가맹점 POS 단말기에서 결제 도중 품목의 일괄 취소 또는 영수증 발행 직후 이루어진 직전 영수증 강제 취소 거래가 발생했을 때, 해당 거래의 연동 패킷 정보(일련번호 `PROC_SN`, 영업일자 `SALE_DATE`, 매장코드 `MS_NO`, POS번호 `POS_NO`, 취소일련번호 `CANCEL_NO`, 저널 JSON 정보 `JOURNAL_CTNT`, 처리 상태 `PROC_FG` 등)를 수집하여 보관하는 실시간 인터페이스 staging 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **직전취소 실시간 전문 적재**: POS 단말기에서 직전 영수증을 취소하거나 결제 단계 전반의 오작동 및 캐셔의 강제 취소 조작 시, 해당 취소 저널(품목 상세 및 취소 수납 내역 등)이 JSON 문자열 포맷으로 직렬화(`journal_ctnt`)되어 `TB_IF_SA_POS_CNCL_BF_SA_CTNT`에 실시간으로 생성 적재됩니다. (적재 직후 `proc_fg = '0'` 대기 상태)\n"
        "* **일일 취소 인터페이스 동기화 배치 (`DmSALT70Service` 및 `DmSALT70_SQL` 배치)**: 일별 정산 배치 구동 시, 동기화 데몬이 미처리 취소 레코드(`proc_fg = '0'`)를 차례대로 순독하여 JSON 데이터 구조를 해독한 후, 백오피스 결제 전 취소 헤더 테이블(`SCNLHDTB`) 및 상세 테이블(`SCNLDTTB`)로 데이터를 변환/분석 적재하고 본 큐를 `proc_fg = '1'`(처리 완료) 상태로 갱신합니다.\n"
        "* **백오피스 오조작 이상 거래 감시**: 영수증 발행 전후의 강제 품목 취소나 직전 영수증 취소는 캐셔의 부정 거래(현금 횡령 등)의 핵심 감사 포인트이므로, 백오피스 이상 거래 모니터링 화면에서 이 테이블 및 관련 직전 취소 원장을 조인하여 집중 감사하는 감정 근거 자료로 활용됩니다."
    )

    data["tables"]["tb_if_sa_pos_cncl_bf_sa_ctnt"] = {
        "memo": tb_if_sa_pos_cncl_bf_sa_ctnt_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_sn": "결제 전 취소 인터페이스 수신 고유 일련번호 (SQ_IF_SA_POS_CNCL_BF_SA_CTNT 시퀀스 사용)",
            "sale_date": "POS에서 실제 직전취소 거래가 실행된 기준 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "cancel_no": "해당 매장/POS/영업일 기준 직전취소 거래의 일련번호 (4자리)",
            "proc_fg": "인터페이스 처리 상태 코드 (0: 수신대기, 1: 처리완료, 9: 오류/실패)",
            "proc_msg": "인터페이스 처리 결과 상태 메시지 및 예외 에러 세부 로그",
            "journal_ctnt": "POS 직전취소 상세 내역을 담은 저널 원천 데이터 (JSON 포맷)",
            "regi_id": "최초 인터페이스 전문 수신 등록 처리 담당자/시스템 ID",
            "regi_dtime": "인터페이스 수신 레코드 최초 생성 등록 일시",
            "updt_id": "인터페이스 최종 처리 업데이트 담당자 ID",
            "updt_dtime": "인터페이스 최종 처리 완료 및 상태 갱신 일시"
        },
        "memo_c": "POS 단말기에서 직전 영수증 취소 또는 결제 진행 중 일괄 취소 시 연동 전문 수신을 통해 실시간 인서트됩니다.",
        "memo_u": "동기화 배치 처리 완료 시 처리 상태(proc_fg) 및 오류 내용이 업데이트됩니다.",
        "memo_d": "가맹점 오조작 부정 거래 감사 추적의 원천 이력이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "일일 취소 정산 배치 서비스, 매장 이상 거래 징후 감시 화면, POS 직전취소 보고서 조회 시 연동 큐로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "scnlhdtb",
                "description": "결제 전 직전취소 헤더 마스터. [배치 DmSALT70Service 연동] tb_if_sa_pos_cncl_bf_sa_ctnt 인터페이스 원장의 JSON 데이터(journal_ctnt)를 파싱하여 결제 전 직전취소 헤더 마스터(SCNLHDTB)에 변환 적재하는 핵심 대상 마스터 관계입니다."
            },
            {
                "table_name": "scnldttb",
                "description": "결제 전 직전취소 상세 내역. [배치 DmSALT70Service 연동] tb_if_sa_pos_cncl_bf_sa_ctnt 인터페이스 원장의 JSON 데이터(journal_ctnt)를 파싱하여 직전취소 상세 품목 내역(SCNLDTTB)에 변환 적재하는 핵심 대상 마스터 관계입니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. POS 직전취소 건이 실제 승인 거래의 반품인지 아니면 단순 입력 취소 거래인지를 검증하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 직전취소 발생 점포의 체인 유형 및 정산 방식을 조회하여 정상 거래 여부를 감사하기 위해 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 직전취소 처리된 상품의 유효성과 부가세 과세구분을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 POS에서 허용되는 연속 직전취소 임계 횟수 제한(예: 3회 연속 취소 발생 시 경고 발생) 등의 시스템 제어 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 취소 사유 코드(고객 변심, 입력 오류, 가격 불만 등) 및 처리 상태 코드(proc_fg)에 대응하는 한글 라벨명을 조인하여 매칭하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 직전취소를 실행한 POS 캐셔 사번(regi_id)의 권한 및 실명을 백오피스 이상 거래 모니터링 화면에서 규명하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 직전취소 대상 상품의 본사 표준 카테고리 정보 대조를 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 취소 상품의 본사 유통 공급 단가를 조회하여 매장 원자재 정산 대사에 미치는 영향을 평가할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 직전취소 처리로 인해 실제로 주방 레시피 및 재고 가감에 미친 영향이 없음을 검증(재고가 실제로 차감되지 않았는지 정합성 확인)하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 취소 거래의 간접 마진 왜곡 영향을 모니터링하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 직전취소 실행 시 통신 오류 로그 및 무단 취소 정황 감사를 위해 간접 연계됩니다."
            }
        ]
    }

    # 86. TB_IF_SA_POS_CNCL_BF_SA_CTNT_LOG MEMO AND RELATED TABLES
    tb_if_sa_pos_cncl_bf_sa_ctnt_log_memo = (
        "### 1. 테이블 개요\n"
        "POS 결제 전/직전 취소 전문 인터페이스 완료 이력 로그 테이블 (`TB_IF_SA_POS_CNCL_BF_SA_CTNT_LOG`).\n"
        "가맹점 POS 단말기에서 전송된 직전취소 인터페이스 원천 레코드 중, 동기화 배치 프로그램(`DmSALT70Service`)에 의해 분석 및 처리가 성공적으로 완료(또는 영구 실패)되어 대기 큐에서 완료 이력 아카이브 보관소로 이관된 과거 직전취소 연동 데이터 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **동기화 배치 처리 완료 후 이관**: 일일 정산 가동 시, 동기화 배치 데몬이 `TB_IF_SA_POS_CNCL_BF_SA_CTNT` 테이블의 미처리 레코드(`proc_fg = '0'`)를 성공적으로 처리(직전취소 헤더 `SCNLHDTB` 및 상세 `SCNLDTTB`에 반영 완료)하면, 해당 레코드를 본 로그 테이블(`TB_IF_SA_POS_CNCL_BF_SA_CTNT_LOG`)로 복사 인서트한 후 원본 staging 테이블에서는 삭제하여 큐 테이블을 항상 슬림한 상태로 유지 관리합니다.\n"
        "* **과거 직전취소 사후 추적 감사**: 영수증 발행 전후 캐셔의 무단 품목 강제 취소 조작은 금전 횡령 사고 등 부정 거래의 온상이 되기 쉬우므로, 사후 이상 징후 분석 시 본 로그 테이블에 보관된 과거 직전취소 저널 데이터(`journal_ctnt` JSON)를 파싱 및 역추적 조회하여 점포 내 도난 방지 및 정합성 검증을 위해 활용합니다."
    )

    data["tables"]["tb_if_sa_pos_cncl_bf_sa_ctnt_log"] = {
        "memo": tb_if_sa_pos_cncl_bf_sa_ctnt_log_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_sn": "직전취소 수신 인터페이스 완료 이력 고유 일련번호 (staging 테이블의 proc_sn과 동일)",
            "sale_date": "POS에서 실제 직전취소 거래를 실행했던 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "cancel_no": "해당 매장/POS/영업일 기준 직전취소 거래의 일련번호 (4자리)",
            "proc_fg": "최종 인터페이스 동기화 처리 상태 코드 (1: 처리완료, 9: 오류/실패)",
            "proc_msg": "최종 동기화 처리 결과 결과 상태 메시지 및 예외 에러 세부 로그",
            "journal_ctnt": "POS 직전취소 상세 내역을 담은 저널 원천 데이터 (JSON 포맷)",
            "regi_id": "최초 인터페이스 전문 수신 등록 처리 담당자/시스템 ID",
            "regi_dtime": "인터페이스 수신 레코드 최초 생성 등록 일시",
            "updt_id": "인터페이스 최종 완료 처리 업데이트 담당자 ID",
            "updt_dtime": "인터페이스 최종 완료 처리 및 상태 갱신 일시"
        },
        "memo_c": "동기화 배치 처리 완료 시, DmSALT70Service에 의해 staging 테이블(TB_IF_SA_POS_CNCL_BF_SA_CTNT)로부터 복사 생성됩니다.",
        "memo_u": "아카이브 완료 상태 로그 원장이므로 최초 이관 이후에는 원칙적으로 업데이트가 발생하지 않습니다.",
        "memo_d": "가맹점 과거 부정 거래 감사 추적 및 회계/정산 감사 증빙의 이력 로그 자료이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "과거 가맹점 직전취소 이력 보고서 조회, POS 이상 취소 거래 사후 추적, 정산 감사 시스템 조회 시 이력 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_if_sa_pos_cncl_bf_sa_ctnt",
                "description": "POS 직전취소 연동 인터페이스 원장 테이블. [배치 DmSALT70Service 연동] 실시간 수신 인터페이스 대기열(TB_IF_SA_POS_CNCL_BF_SA_CTNT)에서 성공적으로 분석 및 동기화 처리가 끝난 레코드를 본 로그 테이블로 이관 후 staging 테이블에서 삭제 처리합니다."
            },
            {
                "table_name": "scnlhdtb",
                "description": "결제 전 직전취소 헤더 마스터. 인터페이스 큐를 통해 최종 반영된 매장 결제 전 직전취소 마스터의 실 데이터 정합성을 추적 감사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "scnldttb",
                "description": "결제 전 직전취소 상세 내역. 인터페이스 큐를 통해 최종 반영된 매장 결제 전 직전취소의 상세 품목군 실 데이터 정합성을 추적 감사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 가맹점 결산 시 직전취소 오차 사고 발생 시, 사후 분석을 위해 과거 직전취소 저널 로그(TB_IF_SA_POS_CNCL_BF_SA_CTNT_LOG)를 역추적 조인 참조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별 영업 구역 및 프랜차이즈 계열 계약의 이력 대조를 위해 점포코드(ms_no) 기준으로 매칭됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 가맹점 직전취소 변동과 대치된 특수 상품의 가격 속성을 사후 감사하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 허용 연속 직전취소 임계값 등 시스템 작동 설정 이력을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 취소 사유 코드 한글 명칭 및 배치 완료 처리 상태 코드(proc_fg) 명칭을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 과거 특정 시점에 직전취소를 등록한 POS 담당 캐셔 사번의 실명 및 소속 권한을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 직전취소 대상 단품의 본사 표준 상품 분류 속성을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 취소 상품의 본사 물류 원가 분석 시 비교 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 직전취소 조작에 따른 실제 재고 자산 증감 왜곡 여부를 사후 검증할 때 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 취소 거래의 간접 마진 왜곡 영향을 모니터링하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 직전취소 오류 이력 및 무단 취소 정황 사후 규명을 위해 간접 연계됩니다."
            }
        ]
    }

    # 87. TB_IF_SA_POS_REGISTER_CTNT MEMO AND RELATED TABLES
    tb_if_sa_pos_register_ctnt_memo = (
        "### 1. 테이블 개요\n"
        "POS 근무 조 개설/마감(개설정산, 마감정산) 전문 인터페이스 원장 테이블 (`TB_IF_SA_POS_REGISTER_CTNT`).\n"
        "가맹점 POS 단말기에서 영업 근무 조별 기기 개설(준비금 등록 등) 및 교대 마감(수납 총액, 카드 승인액, 쿠폰 회수액, 현금 시재 정산 선언 등) 시점에 발생한 정산 데이터 수집 정보(일련번호 `PROC_SN`, 영업일자 `SALE_DATE`, 매장코드 `MS_NO`, POS번호 `POS_NO`, 저널 JSON 문자열 `JOURNAL_CTNT`, 처리 상태 `PROC_FG` 등)를 수집 보관하는 인터페이스 staging 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **개설 및 마감정산 실시간 전문 수집**: 가맹점 POS에서 조별 근무 개설 또는 교대/일일 마감 실행 시점의 현금 카운팅 내역과 결제 수단별 승인 롤업 저널 전문(`journal_ctnt` CLOB)이 생성되어 `TB_IF_SA_POS_REGISTER_CTNT`에 실시간 생성 적재됩니다. (적재 직후 `proc_fg = '0'` 대기 상태)\n"
        "* **일일 마감 인터페이스 동기화 배치 (`DmSALT40Service` 및 `DmSALT40_SQL` 배치)**: 일별 정산 가동 시, 동기화 데몬이 미처리 마감 레코드(`proc_fg = '0'`)를 차례대로 순독하여 JSON 데이터 구조를 해독한 후, 코어 매장 근무 조 개설/마감정산 마스터 테이블 (`SAREGITB`)에 실 데이터로 파싱/변환하여 적재하고 본 레코드를 `proc_fg = '1'`(처리 완료) 상태로 갱신합니다.\n"
        "* **가맹점 영업 실적 확정 및 수납 대사**: 교대 마감 정보는 당일 매장의 총 수납(카드사 대사, 상품권 수납, 현금 시재 과부족)을 본사 재무 회계로 이관하는 마스터 기점으로 활용되므로 가맹점 일일 결산 확정의 핵심 게이트웨이가 됩니다."
    )

    data["tables"]["tb_if_sa_pos_register_ctnt"] = {
        "memo": tb_if_sa_pos_register_ctnt_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_sn": "POS 개설/마감 정산 인터페이스 수신 고유 일련번호 (SQ_IF_SA_POS_REGISTER_CTNT 시퀀스 사용)",
            "sale_date": "POS에서 실제 개설/마감정산 거래를 실행한 기준 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "proc_fg": "인터페이스 처리 상태 코드 (0: 수신대기, 1: 처리완료, 9: 오류/실패)",
            "proc_msg": "인터페이스 처리 결과 상태 메시지 및 예외 에러 세부 로그",
            "journal_ctnt": "POS 개설/마감정산 상세 내역을 담은 CLOB 저널 원천 데이터 (JSON 포맷)",
            "regi_id": "최초 인터페이스 전문 수신 등록 처리 담당자/시스템 ID",
            "regi_dtime": "인터페이스 수신 레코드 최초 생성 등록 일시",
            "updt_id": "인터페이스 최종 처리 업데이트 담당자 ID",
            "updt_dtime": "인터페이스 최종 처리 완료 및 상태 갱신 일시"
        },
        "memo_c": "POS 단말기에서 기기 근무 조 개설 혹은 영업 최종 마감 정산 실행 시 연동 전문 수신을 통해 실시간 인서트됩니다.",
        "memo_u": "동기화 배치 처리 완료 시 처리 상태(proc_fg) 및 오류 내용이 업데이트됩니다.",
        "memo_d": "가맹점 일일 영업 및 매출 실적 확정의 정산 증빙 자료이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "일일 마감 동기화 배치 서비스, 본사 일일 매출 실적 보고서 조회, 신용카드사 수납 대사 보고서 작성 시 연동 큐로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "saregitb",
                "description": "POS 근무 조 개설/마감정산 마스터 원장. [배치 DmSALT40Service 연동] tb_if_sa_pos_register_ctnt 인터페이스 원장의 JSON 데이터(journal_ctnt)를 파싱하여 실시간 매장 근무 조별 개설/마감 실적 대장(SAREGITB)에 변환 적재하는 핵심 대상 마스터 관계입니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 특정 근무 조가 기동된 시간대 내에 속한 개별 영수증 결제 총액을 매출 헤더(STRNHDTB)와 매칭 대조하여 마감 보고서와 실제 영수증 정합성을 최종 검증할 때 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 개설/마감 점포의 계약 상태 및 영업 일정을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 교대 근무 중 발생한 단품별 매출 수량을 롤업하여 마감 단품 정합성을 확인하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 POS 교대 준비금 설정 범위 및 마감 허용 오차 금액의 기본값 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 근무 조 구분 코드(오전반, 오후반 등) 및 처리 상태 코드(proc_fg)에 대응하는 한글 라벨명을 조인하여 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 교대 마감 승인을 입력한 책임자 사번(regi_id)의 권한 및 실명을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 마감 품목 중 본사 통제 상품의 표준 단가를 비교 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 마감 시점의 물류 출고 채무 상계 처리를 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 근무 조 마감과 실시간 주방 원재료 소요 차감의 마감 정합성을 대조하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 교대 마감 시점의 자재 단가 마진 요율 시뮬레이션을 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 마감 전송 패킷의 통신 지연 및 누락 오류를 모니터링하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 88. TB_IF_SA_POS_REGISTER_CTNT_LOG MEMO AND RELATED TABLES
    tb_if_sa_pos_register_ctnt_log_memo = (
        "### 1. 테이블 개요\n"
        "POS 근무 조 개설/마감 전문 인터페이스 완료 이력 로그 테이블 (`TB_IF_SA_POS_REGISTER_CTNT_LOG`).\n"
        "가맹점 POS 단말기에서 전송된 개설/마감정산 인터페이스 원천 레코드 중, 동기화 배치 프로그램(`DmSALT40Service`)에 의해 분석 및 처리가 성공적으로 완료(또는 영구 실패)되어 대기 큐에서 완료 이력 아카이브 보관소로 이관된 과거 개설/마감정산 연동 데이터 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **동기화 배치 처리 완료 후 이관**: 일일 정산 가동 시, 동기화 배치 데몬이 `TB_IF_SA_POS_REGISTER_CTNT` 테이블의 미처리 레코드(`proc_fg = '0'`)를 성공적으로 처리(근무 조 개설/마감정산 마스터 `SAREGITB`에 반영 완료)하면, 해당 레코드를 본 로그 테이블(`TB_IF_SA_POS_REGISTER_CTNT_LOG`)로 복사 인서트한 후 원본 staging 테이블에서는 삭제하여 큐 테이블을 항상 슬림한 상태로 유지 관리합니다.\n"
        "* **과거 마감 정산 이력 추적 감사**: 일일 결산 오차 및 현금 과부족 정밀 감사 시, 사후 분석을 위해 과거 개설/마감정산 저널 로그(`journal_ctnt` JSON)를 조회하여 교대 마감 시점의 실제 수납(카드, 현금 등) 내역과 불일치 원인을 감사 분석하는 이력 로그 역할을 수행합니다."
    )

    data["tables"]["tb_if_sa_pos_register_ctnt_log"] = {
        "memo": tb_if_sa_pos_register_ctnt_log_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_sn": "POS 개설/마감 정산 인터페이스 완료 이력 고유 일련번호 (staging 테이블의 proc_sn과 동일)",
            "sale_date": "POS에서 실제 개설/마감정산 거래를 실행했던 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "proc_fg": "최종 인터페이스 동기화 처리 상태 코드 (1: 처리완료, 9: 오류/실패)",
            "proc_msg": "최종 동기화 처리 결과 결과 상태 메시지 및 예외 에러 세부 로그",
            "journal_ctnt": "POS 개설/마감정산 상세 내역을 담은 CLOB 저널 원천 데이터 (JSON 포맷)",
            "regi_id": "최초 인터페이스 전문 수신 등록 처리 담당자/시스템 ID",
            "regi_dtime": "인터페이스 수신 레코드 최초 생성 등록 일시",
            "updt_id": "인터페이스 최종 완료 처리 업데이트 담당자 ID",
            "updt_dtime": "인터페이스 최종 완료 처리 및 상태 갱신 일시"
        },
        "memo_c": "동기화 배치 처리 완료 시, DmSALT40Service에 의해 staging 테이블(TB_IF_SA_POS_REGISTER_CTNT)로부터 복사 생성됩니다.",
        "memo_u": "아카이브 완료 상태 로그 원장이므로 최초 이관 이후에는 원칙적으로 업데이트가 발생하지 않습니다.",
        "memo_d": "가맹점 과거 개설/마감 이력 및 회계/정산 감사 증빙의 이력 로그 자료이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "과거 가맹점 개설/마감 이력 보고서 조회, POS 마감 오차 사후 추적, 정산 감사 시스템 조회 시 이력 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_if_sa_pos_register_ctnt",
                "description": "POS 개설/마감 연동 인터페이스 원장 테이블. [배치 DmSALT40Service 연동] 실시간 수신 인터페이스 대기열(TB_IF_SA_POS_REGISTER_CTNT)에서 성공적으로 분석 및 동기화 처리가 끝난 레코드를 본 로그 테이블로 이관 후 staging 테이블에서 삭제 처리합니다."
            },
            {
                "table_name": "saregitb",
                "description": "POS 근무 조 개설/마감정산 마스터 원장. 인터페이스 큐를 통해 최종 반영된 매장 교대 마감 실적의 실 데이터 정합성을 추적 감사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 가맹점 결산 시 근무 조별 마감 오차 및 현금 과부족 사고 발생 시, 사후 원인 분석을 위해 과거 개설/마감 저널 로그(TB_IF_SA_POS_REGISTER_CTNT_LOG)를 역추적 조인 참조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별 영업 구역 및 프랜차이즈 계열 계약의 이력 대조를 위해 점포코드(ms_no) 기준으로 매칭됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 교대 근무 중 발생한 단품별 매출 수량을 과거 마감 이력 로그와 비교하여 분석하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 준비금 보충 한계값 변경 또는 교대 마감 오차 제한 규정 등의 역사적 변수 이력을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 근무 조 구분 한글 명칭 및 배치 완료 처리 상태 코드(proc_fg) 명칭을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 과거 특정 시점에 개설/마감을 승인한 점포 관리자 사번의 실명 및 소속 권한을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 통제 단품의 당시 표준 단가와 마감 정합성을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 과거 시점의 물류 출고 대금 채무를 대사 정산하기 위해 간접 참조합니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 근무 조 마감과 실시간 주방 원재료 소요 차감의 과거 정합성 이력을 역추적 감사하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 마감 시점의 입고 원가 마진 요율 시뮬레이션을 과거 이력 로그와 대조 분석하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 마감 전송 패킷의 과거 통신 오류 및 복구 완료 전문 수신 이력을 사후 규명하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 89. TB_IF_SA_POS_SALE_CTNT_LOG MEMO AND RELATED TABLES
    tb_if_sa_pos_sale_ctnt_log_memo = (
        "### 1. 테이블 개요\n"
        "POS 실시간 매출 전송 전문 인터페이스 완료 이력 로그 테이블 (`TB_IF_SA_POS_SALE_CTNT_LOG`).\n"
        "가맹점 POS 단말기에서 결제 승인 완료되어 실시간 전송된 영수증별 매출 전문 데이터 중, 동기화 배치 프로그램(`DmSALA11Service`)에 의해 분석 및 처리가 성공적으로 완료(또는 영구 실패, 중복거래 배제)되어 대기 큐에서 완료 이력 아카이브 보관소로 이관된 과거 매출 전문 연동 데이터 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **동기화 배치 처리 완료 후 이관**: 일일 정산 가동 시, 동기화 배치 데몬이 실시간 매출 전문 대기 큐인 `TB_IF_SA_POS_SALE_CTNT` 테이블의 미처리 레코드(`proc_fg = '0'`)를 성공적으로 처리(매출 헤더 `STRNHDTB`, 매출 상세 `STRNDTTB` 등 매출 원장에 반영 완료)하면, 해당 레코드를 본 로그 테이블(`TB_IF_SA_POS_SALE_CTNT_LOG`)로 복사 인서트한 후 원본 staging 테이블에서는 삭제하여 큐 테이블을 항상 슬림한 상태로 유지 관리합니다.\n"
        "* **과거 매출 전문 사후 복구 및 재처리**: POS와 서버 간의 전문 누락, 카드 승인 정보 불일치, 반품 취소 거래 매칭 오류 등이 발생하여 본사 정산 금액과 가맹점 전송액 간의 차이가 발생할 경우, 어드민 화면(`Admin_System_00015`)을 통해 본 로그 테이블에 보관된 과거 원천 저널 전문 JSON(`journal_ctnt`) 데이터를 직접 조회하고, 필요한 경우 강제 재전송 및 재처리 배치 처리를 가동할 수 있습니다."
    )

    data["tables"]["tb_if_sa_pos_sale_ctnt_log"] = {
        "memo": tb_if_sa_pos_sale_ctnt_log_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_sn": "POS 매출 전문 수신 완료 이력 고유 일련번호 (staging 테이블의 proc_sn과 동일)",
            "sale_date": "POS에서 실제 결제 완료 및 전송을 실행했던 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "영수증 일련번호 (4자리)",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품)",
            "org_sale_date": "반품/취소 시 취소 대상이 되는 원거래 영업 일자 (YYYYMMDD)",
            "org_ms_no": "취소 대상 원거래 매장코드",
            "org_pos_no": "취소 대상 원거래 POS 기기 식별 번호 (2자리)",
            "org_bill_no": "취소 대상 원거래 영수증 일련번호 (4자리)",
            "proc_fg": "최종 인터페이스 동기화 처리 상태 코드 (1: 처리완료, 9: 오류/실패, D: 중복 거래 배제)",
            "proc_msg": "최종 동기화 처리 결과 결과 상태 메시지 및 예외 에러 세부 로그",
            "journal_ctnt": "POS 매출 상세 내역 전체를 포함하는 저널 원천 데이터 (JSON 포맷)",
            "regi_id": "최초 인터페이스 전문 수신 등록 처리 담당자/시스템 ID",
            "regi_dtime": "인터페이스 수신 레코드 최초 생성 등록 일시",
            "updt_id": "인터페이스 최종 완료 처리 업데이트 담당자 ID",
            "updt_dtime": "인터페이스 최종 완료 처리 및 상태 갱신 일시"
        },
        "memo_c": "동기화 배치 처리 완료 시, DmSALA11Service에 의해 staging 테이블(TB_IF_SA_POS_SALE_CTNT)로부터 복사 생성됩니다.",
        "memo_u": "아카이브 완료 상태 로그 원장이므로 최초 이관 이후에는 원칙적으로 업데이트가 발생하지 않습니다.",
        "memo_d": "가맹점 매출 실적 정합성 검증 및 세무 감사/회계 감사의 근본 원천 증빙 자료이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "어드민 매출 전문 모니터링 화면(Admin_System_00015), 과거 가맹점 매출 이력 복구 분석, 영수증 불일치 사후 역추적 시 최우선 원천 로그로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_if_sa_pos_sale_ctnt",
                "description": "POS 실시간 매출 전송 전문 인터페이스 원장 테이블. [배치 DmSALA11Service 연동] 실시간 수신 인터페이스 대기열(TB_IF_SA_POS_SALE_CTNT)에서 성공적으로 분석 및 동기화 처리가 끝난 매출 레코드를 본 로그 테이블로 이관 후 staging 테이블에서 삭제 처리합니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 인터페이스 큐를 통해 최종 반영된 매장 결제 영수증 마스터 실 데이터 정합성을 추적 감사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 인터페이스 큐를 통해 최종 반영된 영수증별 세부 판매 품목군 실 데이터 정합성을 추적 감사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별 영업 구역 및 프랜차이즈 계열 계약의 이력 대조를 위해 점포코드 기준으로 매칭됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 매출 거래와 매치되는 판매 상품의 분류, 단가, 마진 요율의 역사적 정합성을 확인하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 단위별 일일 최대 영수증 처리 한계 및 중복 승인 배제 타임아웃 등의 시스템 파라미터 설정을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 매출 구분(정상, 반품), 배치 완료 처리 상태 코드(proc_fg) 및 전문 오류 유형 라벨을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 과거 특정 시점에 매출을 등록한 POS 담당 캐셔 사번의 실명 및 소속 권한을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 매출 대상 단품의 본사 표준 상품 분류 속성을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 매출과 연동되는 본사 물류 공급 원가 분석 시 비교 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 실시간 매출 변동에 따른 조리 레시피 자재 감산 결과와 비교 감사할 때 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 매출에 따른 원부자재 소요에 대한 선입선출 마진 분석 시 시뮬레이션용으로 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 매출 전문 전송 오류 이력 및 데이터 유실 사고 발생 시 세부 전문 흐름을 추적 감사하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 90. TB_IF_SA_POS_WEAS_CTNT MEMO AND RELATED TABLES
    tb_if_sa_pos_weas_ctnt_memo = (
        "### 1. 테이블 개요\n"
        "POS 외상 입금 정산 수납 전문 인터페이스 원장 테이블 (`TB_IF_SA_POS_WEAS_CTNT`).\n"
        "가맹점 POS 단말기에서 외상 고객 대금 회수(외상 입금 및 완납 정산 등) 거래 발생 시, 수신한 전문 연동 패킷 정보(일련번호 `PROC_SN`, 영업일자 `SALE_DATE`, 매장코드 `MS_NO`, POS번호 `POS_NO`, 영수증번호 `BILL_NO`, 저널 JSON 내용 `JOURNAL_CTNT`, 처리 상태 `PROC_FG` 등)를 수집하여 보관하는 실시간 인터페이스 staging 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **외상 수납 실시간 전문 수신**: POS에서 미수 외상 대금 수납 시 관련 저널 전문 정보(입금 수단, 입금 금액, 수납 대상 외상 거래처 고유 정보 등)가 JSON 포맷으로 직렬화(`journal_ctnt`)되어 `TB_IF_SA_POS_WEAS_CTNT`에 실시간 생성 적재됩니다. (수신 직후 `proc_fg = '0'` 대기 상태)\n"
        "* **일일 외상 입금 동기화 배치 (`DmSALT60Service` 및 DmSALT60_SQL 배치)**: 일별 정산 배치 구동 시, 동기화 데몬이 미처리 수납 레코드(`proc_fg = '0'`)를 차례대로 순독하여 JSON 데이터 구조를 해독한 후, 코어 매출 외상 상세 테이블(`STRNWETB`)의 해당 영수증에 대한 외상 입금 완료 금액(`paid_amt`), 수납 카운트(`paid_cnt`) 및 마감 여부(`proc_fg`) 등을 실시간으로 업데이트 갱신하고, 본 큐를 `proc_fg = '1'`(처리 완료) 상태로 업데이트합니다.\n"
        "* **가맹점 미수금 마감 및 ERP 대사**: 외상 수납은 점포 미수금 자산을 회수하고 본사 대차 대조를 맞추는 필수 정산 기준이 되므로, 가맹점별 월 마감 및 ERP 입금 회계 전송 시 최우선 입금 원천 자료로 감사 연동 처리됩니다."
    )

    data["tables"]["tb_if_sa_pos_weas_ctnt"] = {
        "memo": tb_if_sa_pos_weas_ctnt_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_sn": "외상 입금 수신 인터페이스 고유 일련번호 (SQ_IF_SA_POS_WEAS_CTNT 시퀀스 사용)",
            "sale_date": "POS에서 실제 외상 입금 수납을 처리한 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "proc_fg": "인터페이스 처리 상태 코드 (0: 수신대기, 1: 처리완료, 9: 오류/실패)",
            "proc_msg": "인터페이스 처리 결과 상태 메시지 및 예외 에러 세부 로그",
            "journal_ctnt": "POS 외상 입금 상세 내역을 담은 저널 원천 데이터 (JSON 포맷)",
            "regi_id": "최초 인터페이스 전문 수신 등록 처리 담당자/시스템 ID",
            "regi_dtime": "인터페이스 수신 레코드 최초 생성 등록 일시",
            "updt_id": "인터페이스 최종 처리 업데이트 담당자 ID",
            "updt_dtime": "인터페이스 최종 처리 완료 및 상태 갱신 일시"
        },
        "memo_c": "POS 단말기에서 외상 수동 입금 정산 및 수납 완료 시 연동 전문 수신을 통해 실시간 인서트됩니다.",
        "memo_u": "동기화 배치 처리 완료 시 처리 상태(proc_fg) 및 오류 내용이 업데이트됩니다.",
        "memo_d": "가맹점 미수금 대사 및 회계 정산 감사 증빙 자료이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "일일 외상 정산 배치 서비스, 매장 미수금 관리 보고서 조회, POS 외상 입금 수납 상세 대사 보고서 작성 시 연동 큐로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strnwetb",
                "description": "외상 결제 상세 테이블. [배치 DmSALT60Service 연동] tb_if_sa_pos_weas_ctnt 인터페이스 원장의 JSON 데이터(journal_ctnt)를 파싱하여, 원래 발생한 외상 미수금 내역의 사후 수납 완료액(PAID_AMT), 수납 처리 일련 카운트(PAID_CNT) 및 마감 여부(PROC_FG)를 업데이트 연동 처리하는 핵심 대상 마스터 관계입니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 외상 수납이 발생한 원 영수증의 매출 결제수단 및 총 결제금액 상태를 대조 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 외상 수납을 실행한 가맹점의 정산 계좌 상태 및 프랜차이즈 계약 분류를 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 외상 거래 대상이 되는 특정 케이터링 또는 연회 단품의 표준단가 및 수납 정합성을 위해 간접 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점별 외상 입금 정산 주기 설정 변수 및 정산 연체 임계치 등의 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 외상 거래 수납 구분(예: 부분 입금, 완납, 카드 수납 대체 등) 및 처리 상태 코드(proc_fg)에 대응하는 한글 라벨명을 조인하여 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 외상 입금 정산 및 수납 입력을 백오피스 또는 POS에서 처리한 조작자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 외상 거래와 결합된 표준 상품의 출고 및 매입 단가를 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 외상 대금 수납액과 본사 상품 공급 정산 채무의 대사 처리를 상호 비교하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 외상 수납 대상 거래에서 대량 공급된 단품의 재고 상태를 간접적으로 대조 검증하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 외상 매출 수납 완료 시점의 매입가 대비 실질 마진율 산정을 위해 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 외상 수납 및 입금 처리 시 발생한 통신 오류 또는 한도 조정 로그를 추적 감사하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 91. TB_IF_SA_POS_WEAS_CTNT_LOG MEMO AND RELATED TABLES
    tb_if_sa_pos_weas_ctnt_log_memo = (
        "### 1. 테이블 개요\n"
        "POS 외상 입금 정산 수납 전문 인터페이스 완료 이력 로그 테이블 (`TB_IF_SA_POS_WEAS_CTNT_LOG`).\n"
        "가맹점 POS 단말기에서 전송된 외상 입금 정산 수납 인터페이스 원천 레코드 중, 동기화 배치 프로그램(`DmSALT60Service`)에 의해 분석 및 처리가 성공적으로 완료(또는 영구 실패)되어 대기 큐에서 완료 이력 아카이브 보관소로 이관된 과거 외상 수납 연동 데이터 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **동기화 배치 처리 완료 후 이관**: 일일 정산 가동 시, 동기화 배치 데몬이 `TB_IF_SA_POS_WEAS_CTNT` 테이블의 미처리 레코드(`proc_fg = '0'`)를 성공적으로 처리(외상 결제 상세 `STRNWETB`에 수납액 및 마감 플래그 반영 완료)하면, 해당 레코드를 본 로그 테이블(`TB_IF_SA_POS_WEAS_CTNT_LOG`)로 복사 인서트한 후 원본 staging 테이블에서는 삭제하여 큐 테이블을 항상 슬림한 상태로 유지 관리합니다.\n"
        "* **과거 외상 수납 이력 추적 감사**: 일일 결산 수납 불일치 정밀 감사 및 외상 거래처 미수 대사 시, 사후 분석을 위해 과거 외상 수납 저널 로그(`journal_ctnt` JSON)를 조회하여 수납 조작 시점의 실제 수납(카드, 현금 등) 내역과 불일치 원인을 감사 분석하는 이력 로그 역할을 수행합니다."
    )

    data["tables"]["tb_if_sa_pos_weas_ctnt_log"] = {
        "memo": tb_if_sa_pos_weas_ctnt_log_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_sn": "외상 입금 수신 인터페이스 완료 이력 고유 일련번호 (staging 테이블의 proc_sn과 동일)",
            "sale_date": "POS에서 실제 외상 입금 수납을 실행했던 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "proc_fg": "최종 인터페이스 동기화 처리 상태 코드 (1: 처리완료, 9: 오류/실패)",
            "proc_msg": "최종 동기화 처리 결과 결과 상태 메시지 및 예외 에러 세부 로그",
            "journal_ctnt": "POS 외상 입금 상세 내역을 담은 저널 원천 데이터 (JSON 포맷)",
            "regi_id": "최초 인터페이스 전문 수신 등록 처리 담당자/시스템 ID",
            "regi_dtime": "인터페이스 수신 레코드 최초 생성 등록 일시",
            "updt_id": "인터페이스 최종 완료 처리 업데이트 담당자 ID",
            "updt_dtime": "인터페이스 최종 완료 처리 및 상태 갱신 일시"
        },
        "memo_c": "동기화 배치 처리 완료 시, DmSALT60Service에 의해 staging 테이블(TB_IF_SA_POS_WEAS_CTNT)로부터 복사 생성됩니다.",
        "memo_u": "아카이브 완료 상태 로그 원장이므로 최초 이관 이후에는 원칙적으로 업데이트가 발생하지 않습니다.",
        "memo_d": "가맹점 과거 외상 수납 이력 및 회계/정산 감사 증빙의 이력 로그 자료이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "과거 가맹점 외상 수납 이력 보고서 조회, POS 마감 오차 사후 추적, 정산 감사 시스템 조회 시 이력 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_if_sa_pos_weas_ctnt",
                "description": "POS 외상 입금 정산 수납 전문 인터페이스 원장 테이블. [배치 DmSALT60Service 연동] 실시간 수신 인터페이스 대기열(TB_IF_SA_POS_WEAS_CTNT)에서 성공적으로 분석 및 동기화 처리가 끝난 외상 수납 레코드를 본 로그 테이블로 이관 후 staging 테이블에서 삭제 처리합니다."
            },
            {
                "table_name": "strnwetb",
                "description": "외상 결제 상세 테이블. 인터페이스 큐를 통해 최종 반영된 외상 입금 정산 수납 완료액(PAID_AMT), 수납 처리 일련 카운트(PAID_CNT) 및 마감 여부(PROC_FG)의 실 데이터 정합성을 감사 분석하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 가맹점 결산 시 외상 수납 불일치 오차 사고 발생 시, 사후 원인 분석을 위해 과거 외상 수납 저널 로그(TB_IF_SA_POS_WEAS_CTNT_LOG)를 역추적 조인 참조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 점포별 영업 구역 및 프랜차이즈 계열 계약의 이력 대조를 위해 점포코드 기준으로 매칭됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 외상 수납 대상 거래에서 판매 완료된 품목의 표준 속성 확인을 위해 간접 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 준비금 보충 한계값 변경 또는 외상 입금 정산 주기 등의 역사적 변수 이력을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 외상 수납 상태 구분 한글 명칭 및 배치 완료 처리 상태 코드(proc_fg) 명칭을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 과거 특정 시점에 외상 입금을 수동 보정한 본사 정산 조작자의 사번 및 실명을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 외상 수납 대사 완료된 단품의 본사 표준 상품 분류 속성을 대조하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 외상 수납 정산금 수납 시 본사 상품 공급 정산 채무와의 대사 처리를 비교하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 외상으로 다량 유통 유입된 상품의 재고 감산 정합성을 대조하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 외상 수납 완료 단가 대비 선입선출 원가 기반으로 실질 가맹점 마진율을 사후 산정할 때 간접 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 외상 수납 승인 패킷 통신 오류 또는 한도 조정 이력을 사후에 추적 감사하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 92. TB_IMDDIO_COST MEMO AND RELATED TABLES
    tb_imddio_cost_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 상품 일별 수불 및 원가 집계/평가 이력 테이블 (`TB_IMDDIO_COST`).\n"
        "가맹점별 영업일 동안 발생한 개별 원부자재 및 완제품 상품(`GOODS_CD`)에 대한 모든 수불 내역(매입 `PURCH_QTY`/`PURCH_COST`, 매입반품 `RETURN_QTY`/`RETURN_COST`, 매출 `SALE_QTY`/`SALE_COST`, 기타입출고, 폐기 `DISUSE_QTY`, 재고조정 `ADJUST_QTY`, 매장간 이동, 도매판매 등)을 집계하고, 총평균법 재고 가치 평가액(`TOT_AVG_COST`), 표준 원단가(`UCOST`), 원재료 입고 편차(`GAP_UCOST`) 등을 일별로 기록 보존하는 상품 수불 및 원가 집계 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **일일 결산 배치 수불 집계 (`SUB_TOT_AVG_P` 프로시저)**: 매일 밤 가맹점 일일 정산 결산 배치 가동 시, 당일 발생한 입고/출고/매출/조정 등 수불 항목들을 취합하여 총평균단가를 산출하고 재고 자산 평가 결과를 `TB_IMDDIO_COST` 테이블에 계산 적재합니다.\n"
        "* **원가 편차 분석 및 재고 자산 평가**: 본사 상품 마스터(`TGOODSTB`)의 표준 매입가(`ucost`)와 가맹점 실입고가 간의 차이(`gap_ucost`)를 도출하여 가맹점 마진 변동의 요인을 추적 분석하며, 월말 자산 평가 및 결산 재무 보고서의 기본 데이터로 사용됩니다."
    )

    data["tables"]["tb_imddio_cost"] = {
        "memo": tb_imddio_cost_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "create_date": "수불 및 원가 집계가 실행된 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "goods_cd": "수불 및 원가 평가 대상 상품/원자재 코드 (20자리)",
            "chain_ms_no": "체인 소속 본사/대표 매장코드",
            "purch_qty": "당일 최종 물류 매입 입고된 상품 수량",
            "purch_cost": "당일 매입 입고된 상품의 매입 원가 총액",
            "return_qty": "당일 공급처로 반품 출고된 상품 수량",
            "return_cost": "당일 반품 출고된 상품의 매입 원가 차감 총액",
            "sale_qty": "당일 가맹점 POS 판매 및 도매로 출고된 상품 총수량",
            "sale_cost": "당일 판매 상품에 대응하는 총평균 매출원가(COGS) 총액",
            "in_qty": "기타 비정형 거래로 매장에 입고된 상품 수량",
            "in_cost": "기타 입고 상품의 평가 원가 총액",
            "out_qty": "기타 비정형 거래로 매장에서 출고된 상품 수량",
            "out_cost": "기타 출고 상품의 평가 원가 총액",
            "disuse_qty": "유통기한 만료, 파손 등으로 폐기 처리된 상품 수량",
            "disuse_cost": "폐기 상품의 매입 원가 손실 총액",
            "adjust_qty": "실사 재고 조사 결과 재고 차이 조정한 수량 (+ 또는 -)",
            "adjust_cost": "재고 실사 조정에 따른 자산 변동 평가 금액",
            "tin_qty": "타계정(사내 소비 등)에서 입고 대체된 상품 수량",
            "tin_cost": "타계정 입고 대체 상품의 평가 원가 총액",
            "tout_qty": "타계정으로 출고 대체(소모품 전환 등)된 상품 수량",
            "tout_cost": "타계정 출고 대체 상품의 평가 원가 총액",
            "returndis_qty": "반품 처리 후 현지 폐기 처리된 상품 수량",
            "returndis_cost": "반품 폐기 상품의 평가 금액 총액",
            "move_in_qty": "타 매장에서 양도 이동 입고된 상품 수량",
            "move_in_cost": "양도 이동 입고된 상품의 양수 평가 금액 총액",
            "move_out_qty": "타 매장으로 양도 이동 출고된 상품 수량",
            "move_out_cost": "양도 이동 출고된 상품의 양도 평가 금액 총액",
            "wholesale_qty": "도매 및 대량 특판 거래로 출고된 상품 수량",
            "wholesale_cost": "도매 출고 상품의 도매 원가 총액",
            "wholesale_rt_qty": "도매 매출 건 중 반품 취소된 상품 수량",
            "wholesale_rt_cost": "도매 반품 상품의 원가 차감 총액",
            "tot_avg_cost": "총평균법 알고리즘에 의해 최종 산출된 마감 재고 자산 평가 총액",
            "ucost": "상품 마스터에 등록된 표준 물류 원가 단가",
            "tgood_in_qty": "원부자재 및 상품의 당일 규격 총입고 수량",
            "ucost_in_qty": "입고단가 가중치 반영 입고금액 (단가 * 수량 소수점 처리금액)",
            "gap_ucost": "표준 원가 대비 실제 입고 총평균가와의 편차 발생 총액"
        },
        "memo_c": "일일 가맹점 마감 정산 배치(SUB_TOT_AVG_P 프로시저) 실행 시 당일 수불 기록을 롤업하여 일별로 자동 생성 기록됩니다.",
        "memo_u": "월말 수불 조정, 표준 원가 소급 적용 및 총평균단가 재계산 배치 구동 시 업데이트됩니다.",
        "memo_d": "가맹점 세무 신고, 본사 유통 마진 감사 및 재고 자산 평가 증빙이므로 임의 삭제가 차단됩니다.",
        "memo_r": "가맹점 상품 일별 수불 조회(Hq_Stock_00016), 월말 재고 자산 평가 보고서 작성, 세무 부가세 신고 검증 시 기초 수불 대장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 각 점포별로 판매되는 상품의 과세 구분 및 가구가격, 마진 설정을 대조하고 수불 집계 대상 매장 상품의 유효성을 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 수불 분석 시 가맹점 체인 구분 및 점포 관리 등급별 재고 마진 요율 시뮬레이션을 분석하기 위해 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 일별 수불 결과 산출된 당일 마감 재고 수량과 실시간 매장 현재고 원장의 수량 일치 여부를 교차 검증하고 재고 정합성을 확보하기 위해 연계됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 총평균법 원가 평가액(tot_avg_cost)과 선입선출 단가 평가액 간의 재고 자산 평가 차이(평가 손익 시뮬레이션)를 분석하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 일별 수불의 입고(purch_qty 및 purch_cost) 실적 집계 대상이 되는 당일 확정 물류 매입 입고 전표 목록을 검증 대사하기 위해 조인 참조합니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 당일 가맹점 매출 수량(sale_qty) 집계 대상이 되는 POS 전송 영수증 상세 판매 품목 수량을 취합 대조하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 일별 수불 마감 시 허용되는 재고 실사 오차 임계치 및 총평균 소수점 처리 규칙 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 수불 분류 코드, 과세구분 및 예외 처리 구분 한글 라벨명을 조인하여 명칭을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 일별 수불 강제 조정 마감 또는 총평균단가 재계산 배치를 수동 실행한 관리자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사에서 취급하는 표준 원부자재 규격 단가와 가맹점 실입고가 간의 차이(gap_ucost)를 분석하기 위해 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 수불 배치 실행 오류 로그 및 가맹점 원재료 입고 패킷 누락 정황을 추적 감사하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 가맹점 총 수납 매출액 대비 총평균 수불 원가 기반의 실제 매출 마진 금액의 최종 정합성을 대조 분석하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 93. TB_IMMMIO_COST MEMO AND RELATED TABLES
    tb_immmio_cost_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 상품 월별 수불 및 월말 재고 자산 평가/원가 집계 테이블 (`TB_IMMMIO_COST`).\n"
        "가맹점별 특정 영업월(YYYYMM) 동안 취급한 개별 원부자재 및 완제품 상품(`GOODS_CD`)에 대한 전체 월간 수불 집계 내역(기초이월 `START_QTY`/`START_COST`, 당월매입, 당월반품, 당월매출 `SALE_QTY`/`SALE_COST`, 월간 폐기/조정/이동, 기말재고 `END_QTY`/`END_COST`, 월 총평균단가 `TOT_AVG_COST` 등)을 취합 및 기록 보존하여 가맹점의 세무 신고 및 본사 월간 결산의 기초 재고 자산을 확정하는 결산 보고 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **월말 결산 배치 수불 집계 (`SUB_TOT_AVG_P` 및 `SUB_TOT_AVG_SINGLE_P` 프로시저)**: 가맹점별 월 마감 정산 배치 실행 시, 일별 수불 집계(`TB_IMDDIO_COST`) 데이터를 월 단위로 롤업하여 당월 총평균단가 및 기말 재고 평가 가액을 계산 및 적재합니다.\n"
        "* **수동 보정 및 월 재계산 처리 (`SUB_CALC_FIX_AMT_P` 프로시저)**: 정산 완료 후 재고 실사 차이 보정액(`fix_amt`)을 최종 반영하거나, 원가 불일치 등으로 월 총평균단가를 재계산/보정(`SUB_CALC_FIX_AMT_P`)할 때 데이터를 갱신하고 ERP 월 마감 전표 생성을 위한 기초 데이터로 제공합니다."
    )

    data["tables"]["tb_immmio_cost"] = {
        "memo": tb_immmio_cost_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "create_month": "수불 및 월말 원가 집계가 실행된 영업 월 (YYYYMM)",
            "ms_no": "매장코드 (점포 코드)",
            "goods_cd": "수불 및 원가 평가 대상 상품/원자재 코드 (20자리)",
            "chain_ms_no": "체인 소속 본사/대표 매장코드",
            "start_qty": "전월 말 기준 이월된 당월 기초 재고 수량",
            "start_cost": "이월된 당월 기초 재고 평가 금액 총액",
            "purch_qty": "당월 한 달간 물류 매입 입고된 상품 누적 수량",
            "purch_cost": "당월 매입 입고된 상품의 매입 원가 누적 총액",
            "return_qty": "당일 공급처로 반품 출고된 누적 상품 수량",
            "return_cost": "당월 반품 출고된 상품의 매입 원가 차감 누적 총액",
            "sale_qty": "당월 한 달간 가맹점 POS 판매 및 도매로 출고된 상품 누적 총수량",
            "sale_cost": "당월 판매 상품에 대응하는 총평균 매출원가(COGS) 누적 총액",
            "in_qty": "기타 입고(수동 보정 등)된 당월 누적 상품 수량",
            "in_cost": "기타 입고 상품의 평가 원가 누적 총액",
            "out_qty": "기타 출고(수동 보정 등)된 당월 누적 상품 수량",
            "out_cost": "기타 출고 상품의 평가 원가 누적 총액",
            "disuse_qty": "당월 한 달간 유통기한 만료 등으로 폐기 처리된 상품 누적 수량",
            "disuse_cost": "당월 폐기 상품의 매입 원가 손실 누적 총액",
            "adjust_qty": "당월 한 달간 실사 재고 조사 결과 수동 조정된 누적 수량",
            "adjust_cost": "당월 재고 실사 조정에 따른 자산 변동 누적 평가 금액",
            "tin_qty": "당월 한 달간 타계정에서 입고 대체된 누적 상품 수량",
            "tin_cost": "당월 타계정 입고 대체 상품의 평가 원가 누적 총액",
            "tout_qty": "당월 한 달간 타계정으로 출고 대체된 누적 상품 수량",
            "tout_cost": "당월 타계정 출고 대체 상품의 평가 원가 누적 총액",
            "end_qty": "당월 말 마감 기준 매장에 잔존하는 기말 실고 재고 수량",
            "end_cost": "당월 말 마감 기준 기말 재고 평가 금액 총액",
            "returndis_qty": "당월 반품 처리 후 현지 폐기 처리된 누적 상품 수량",
            "returndis_cost": "당월 반품 폐기 상품의 평가 금액 누적 총액",
            "move_in_qty": "당월 한 달간 매장 간 양도 이동 입고된 누적 상품 수량",
            "move_in_cost": "이동 입고된 상품의 양수 평가 금액 누적 총액",
            "move_out_qty": "당월 한 달간 매장 간 양도 이동 출고된 누적 상품 수량",
            "move_out_cost": "이동 출고된 상품의 양도 평가 금액 누적 총액",
            "wholesale_qty": "당월 도매 및 대량 특판 거래로 출고된 누적 상품 수량",
            "wholesale_cost": "도매 출고 상품의 도매 원가 누적 총액",
            "wholesale_rt_qty": "당월 도매 매출 건 중 반품 취소된 누적 상품 수량",
            "wholesale_rt_cost": "도매 반품 상품의 원가 차감 누적 총액",
            "tot_avg_cost": "월간 가중 총평균법 알고리즘에 의해 최종 산출된 월 마감 재고 단가",
            "fix_amt": "월말 수동 재고 실사 확정 시 입력한 실물 차이 보정 금액",
            "tot_qty": "당월 마감 기준 총 수량 (기초 + 당월 입고 누계)",
            "tot_amt": "당월 마감 기준 총 자산 금액 (기초 + 당월 입고 누계액)",
            "ucost": "상품 마스터에 등록된 표준 물류 원가 단가",
            "tgood_in_qty": "원부자재 및 상품의 당월 규격 누적 총입고 수량",
            "ucost_in_qty": "입고단가 가중치 반영 당월 입고누적 금액 (단가 * 수량 소수점 처리금액)",
            "gap_ucost": "표준 원가 대비 월 총평균 실제 입고 단가와의 편차 발생 누적 총액",
            "usuprice_vat": "월말 재고 평가 금액에 상응하는 표준 가맹점 공급가 부가세액"
        },
        "memo_c": "월말 가맹점 결산 배치(SUB_TOT_AVG_P 프로시저) 실행 시 일별 수불 기록을 당월 기준으로 통합 롤업하여 월 1회 자동 생성 기록됩니다.",
        "memo_u": "월말 실사 확정 보정, 표준 원가 마감 변경 적용 및 수동 단가 보정 프로시저(SUB_CALC_FIX_AMT_P) 가동 시 업데이트됩니다.",
        "memo_d": "프랜차이즈 재무 제표 작성, 가맹점 부가세/종합소득세 신고 및 마진율 세무 감사의 원천 증빙 자료이므로 임의 삭제가 영구히 불가합니다.",
        "memo_r": "가맹점 상품 월별 수불 조회(Hq_Stock_00016), 월말 재고 자산 평가서 조회(Hq_Stock_00017), 본사 월말 손익 산정 시 최우선 월간 수불 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_imddio_cost",
                "description": "가맹점 상품 일별 수불 및 원가 집계/평가 이력. [프로시저 SUB_TOT_AVG_P 연동] 한 달 동안 매일 발생한 일별 세부 수불 및 매입/매출 이력(TB_IMDDIO_COST)을 월 단위로 최종 롤업(Roll-up)하여 월별 마감 데이터로 이관 연계 처리합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 월말 기준 상품 표준 물류 원가 및 세무 상의 부가세 면세/과세 구분을 비교하고 점포별 월말 재고 자산 표준액을 평가하기 위해 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 월말 기말 마감 수량(end_qty)과 실시간 매장 현재고 원장의 수량 일치 여부를 교차 검증하고 재고 정합성을 확보하기 위해 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점 체인 구분 및 지역에 따른 월 정산 조건, 본사 여신 수수료 정산 관계를 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 선입선출 매입 기록 기반의 기말 재고 평가와 당월 총평균법 재고 평가 가액(tot_avg_cost * end_qty)을 교차 검증하고 자산 재평가 충당금을 계산하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 월간 가맹점 총 매입수량 및 매입단가 오차를 최종 마감할 때 매입 입고 전표 총액 정합성을 확인하기 위해 간접 참조합니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 월 총 매출 수량 및 판매 단품 수량을 롤업 대조하여 영업 손익 마진율을 검증하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 월말 재고 실사 차이 마감 보정액(fix_amt) 한도 초과 경고 설정 및 월 세무 결산 규칙 기본값 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 월말 수불 구분 한글 라벨명 및 당월 원가 계산 처리 성공 상태 구분을 조인하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 월 수불 수동 마감 보정 전표를 승인 처리하거나 총평균단가 재계산 배치 프로시저를 강제 조작한 정산 담당 관리자 ID의 소속 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 표준 원가 추이와 가맹점 월 총평균 실제 입고 단가의 차이(gap_ucost) 및 마진 정합성을 분석하기 위해 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 월말 정산 배치 구동 중 예외 에러 및 원부자재 단가 불일치 통보 패킷 통신 감사 로그를 확인하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 월간 가맹점 총 매출 매출액과 월 총평균 원가 기반 COGS 비율을 매칭하여 월 최종 손익 분석 보고서를 도출하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 94. TB_RECIPE MEMO AND RELATED TABLES
    tb_recipe_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 레시피 마스터 테이블 (`TB_RECIPE`).\n"
        "가맹점 또는 프랜차이즈 계열사 체인별(`CHAIN_NO`)로 등록 관리되는 완성품 메뉴 및 반제품 제조 레시피 기본 속성(레시피 코드 `RECIPE_CD`, 한글 레시피명 `RECIPE_NM`, 재고 관리 차감 대상 플래그 `STOCK_YN` 등)을 집중 통제하는 레시피 기준 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 매출 발생 시 실시간 재고 차감 전개 (`SUB_RECIPE_IO_P` 프로시저)**: 가맹점 POS 단말기에서 특정 완성품 식음료 메뉴가 판매 완료되면, 일 정산 또는 실시간 배치 동작 시 해당 메뉴 코드에 1:N으로 설계된 레시피 구성 원재료 구성 테이블(`TB_RECIPE_GOODS`)을 읽어와 가중 중량만큼 매장 현재고 원장(`IMCRIOTB`)의 원재료 재고를 자동 감산 차감합니다.\n"
        "* **세트 메뉴 및 반제품 다중 전개 (`SUB_SET_IO_P` 프로시저)**: 세트 품목 판매 시 또는 자체 생산 소스 등 반제품 폐기 시, 내부 레시피 전개 프로시저가 레시피 계층 구조를 다단계(Multi-level BOM)로 분해/전개하여 최하위 원천 원자재 단품 수준까지 수량 소모처리를 완벽하게 자동 처리해 줍니다."
    )

    data["tables"]["tb_recipe"] = {
        "memo": tb_recipe_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 계열사 분류 코드 (4자리)",
            "recipe_cd": "해당 완성품 메뉴 또는 반제품의 레시피 식별 코드 (8자리)",
            "recipe_nm": "레시피의 정식 한글 명칭 (예: 아이스 아메리카노 Tall)",
            "stock_yn": "해당 레시피 적용 상품 판매 시 원자재 실고 재고를 차감할지 여부 플래그 (Y: 차감/관리, N: 미차감)",
            "remark": "레시피 제조 주의사항 및 조리 팁 등의 비고 설명",
            "create_dtime": "레시피 최초 등록 승인 일시 (YYYYMMDDHH24MISS)",
            "create_id": "레시피를 최초 기획/등록한 본사 R&D 및 정산 담당자 ID",
            "last_dtime": "레시피 최종 변경 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "레시피를 최종 수정한 조작자 ID"
        },
        "memo_c": "본사 R&D 및 상품기획 정산 화면을 통해 새로운 신메뉴 조리법 설계 시 수동으로 승인 인서트됩니다.",
        "memo_u": "조리 레시피 변경(재고 관리 제외 여부 변경 등) 또는 한글 명칭 수정 시 업데이트됩니다.",
        "memo_d": "과거 판매 실적 기준의 소급 재고 수불 차감 및 마진 시뮬레이션의 원천 이력이므로 임의 삭제가 영구 방지됩니다.",
        "memo_r": "POS 판매 매출 확정에 따른 원재료 자동 차감 배치(SUB_RECIPE_IO_P), 세트 메뉴 구성 전개(SUB_SET_IO_P), 백오피스 레시피 관리 화면 조회 시 기준 마스터로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_recipe_goods",
                "description": "레시피 구성 원부자재 상세 마스터. 완성품 메뉴(recipe_cd) 하나를 제조하기 위해 투입되는 세부 원부자재 및 1회 제공량(g, ml, 개 등 소요량 NEED_QTY)을 1:N 관계로 지정 관리하는 매칭 원장입니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 매장에서 판매하는 메뉴 단품(goods_cd가 recipe_cd와 동일하게 매칭)의 상품 관리 여부 및 매출 단가를 비교하기 위해 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. [배치 SUB_RECIPE_IO_P 연동] POS 매출 판매 영수증이 서버에 전송되면, 본 레시피에 등재된 원부자재 목록(TB_RECIPE_GOODS)의 수량만큼 현재고 테이블(IMCRIOTB)의 원재료 재고량을 실시간 차감 반영합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점 체인 등급(chain_no)별로 다르게 책정 및 배포되는 레시피 공급 정책을 식별하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 레시피 전개에 따라 소모된 원자재의 출고 단가를 선입선출단가 기반으로 평가하여 제조원가를 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 발주 입고된 원부자재 단가와 레시피 상의 규격 중량이 정상 유통 단가 범위 내에 속하는지 대조하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 판매된 메뉴 영수증 목록을 읽어 레시피 전개 대상 트랜잭션을 추출하기 위해 매출 상세 테이블과 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 레시피 미등록 메뉴의 강제 재고 차감 허용 여부 플래그 및 원자재 자동 차감 단위 소수점 처리 임계값을 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 레시피 카테고리(음료, 베이커리, 소스류 등) 및 재고 관리 구분 한글 라벨명을 조인하여 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 레시피 관리 화면에서 신규 레시피를 설계하거나, 소요량 조작을 수동 수정한 본사 R&D/구매 조작자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 완성품 메뉴에 들어가는 개별 원부자재의 본사 표준 상품 코드 및 분류 정합성을 유지하기 위해 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 실시간 매출 전송 전문 분석 시 레시피 매핑 실패로 인한 재고 차감 누락 오류를 모니터링하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 가맹점 총 수납 매출액 대비 본 레시피를 통해 산출된 이론적 원재료 소요 총액의 COGS 비율을 도출하여 영업 총손익 마진율을 산정하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 95. TB_RECIPE_GOODS MEMO AND RELATED TABLES
    tb_recipe_goods_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 레시피 구성 원부자재 상세 마스터 테이블 (`TB_RECIPE_GOODS`).\n"
        "체인별(`CHAIN_NO`) 완성품 메뉴 레시피(`RECIPE_CD`)를 특정 매장(`MS_NO`)에서 실제 조리하거나 제조할 때 구성 성분이 되는 원재료 상품코드(`GOODS_CD`), 소요 중량/수량(`WEIGHT`), 대체 원재료(`REPLACE_GOODS_CD`), 대체 소요량(`REPLACE_WEIGHT`) 및 기본 재료 채택 플래그(`DEFAULT_YN`) 등을 가맹점 점포별로 1:N으로 기록하는 레시피 품목 상세 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹점별 레시피 커스터마이징 허용**: 본사 R&D에서 배포하는 표준 조리법 외에도, 개별 매장의 특수 상황(특정 원재료 품절로 인한 대체품 사용, 로컬 사급 식자재 매핑 등)에 맞게 매장코드(`ms_no`)별로 세부 원부자재 소요 내역을 유연하게 매핑 조절할 수 있습니다.\n"
        "* **판매 시점 재고 전개 수불 차감 (`SUB_RECIPE_IO_P` 프로시저)**: 일 정산 배치 구동 시, 당일 판매된 영수증의 단품 수량에 본 레시피 상세 중량(`weight`)을 곱하여 가맹점 실물 원재료 재고량을 차감(`IMCRIOTB`) 처리하며, 원재료의 구성 비율 변동 이력은 레시피 구성품 트리거(`TB_RECIPE_GOODS_T01`)에 의해 실시간 추적 감사됩니다."
    )

    data["tables"]["tb_recipe_goods"] = {
        "memo": tb_recipe_goods_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 계열사 분류 코드 (4자리)",
            "recipe_cd": "완성품 메뉴 또는 반제품의 레시피 식별 코드 (8자리)",
            "ms_no": "매장코드 (점포 코드)",
            "goods_cd": "레시피를 구성하는 세부 원부자재 상품코드 (20자리)",
            "weight": "해당 원부자재의 1회 조리 시 투입되는 표준 소요 중량/수량 (numeric 14,3)",
            "replace_goods_cd": "기본 원부자재 일시 품절 등 비상 시 대체 적용 가능한 대체 원자재 상품코드",
            "replace_weight": "대체 원부자재 투입 시 적용하는 대체 소요 중량/수량",
            "default_yn": "기본 원재료 채택 여부 플래그 (Y: 기본 재료 사용, N: 옵션/대체 재료 사용 가능)",
            "create_dtime": "레시피 상세 품목 최초 매핑 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "레시피 상세 품목 등록 조작자 ID",
            "last_dtime": "레시피 상세 품목 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "레시피 상세 품목 최종 수정 조작자 ID",
            "idx": "레시피 조리 순서 및 화면 정렬을 위한 인덱스 키"
        },
        "memo_c": "R&D 레시피 구성 화면에서 완성품 메뉴에 투입되는 세부 원부자재 소요량을 매핑하여 인서트합니다.",
        "memo_u": "대체 원자재 지정, 투입 중량 변경 또는 조리 순서(idx) 수정 시 업데이트되며, TB_RECIPE_GOODS_T01 트리거를 통해 이력이 추적됩니다.",
        "memo_d": "과거 판매 매출과 연계된 원자재 수불 차감 계산의 핵심 요율 자료이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 매출 대비 원재료 자동 차감 배치(SUB_RECIPE_IO_P), 세트 메뉴 구성 전개(SUB_SET_IO_P), 백오피스 레시피 구성 상세 화면 조회 시 소요량 마스터로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_recipe",
                "description": "가맹점 레시피 마스터. 본 레시피 세부 품목의 기준이 되는 완성품 메뉴명 및 재고 차감 유효성 설정(stock_yn) 정보를 식별하기 위해 1:1로 매핑됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 레시피 구성 성분 품목(goods_cd) 또는 대체 품목(replace_goods_cd)의 매장 내 유효성 및 원자재 취급 속성을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. [배치 SUB_RECIPE_IO_P 연동] POS 판매 시점 또는 폐기 등록 시점에 본 레시피에 배포된 원재료별 수불 중량(weight 또는 replace_weight)을 매칭하여 현재고 실고량을 차감합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 점포별로 다르게 로컬 사급 자재를 적용하는 예외 매장 레시피 세부 구성을 조회하기 위해 매장코드 기준으로 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 소모된 원자재 중량(weight)과 선입선출 입고 누적 대장의 단가를 조합하여 한 접시의 최종 이론 원가를 산출할 때 조인 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 발주 매입되는 실제 원재료의 포장 중량 대비 레시피 단위 중량의 원가 배부를 분석하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 판매 영수증 메뉴별로 레시피 소요량 구성 성분을 1:N으로 곱해 총 소요 자재량을 산출할 때 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 대체 재고 차감 허용 여부 플래그 및 레시피 구성품 한도 임계값 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 원부자재 분류 코드 및 기본 원재료 구분(default_yn) 코드의 한글 명칭을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 레시피 구성 상세 화면에서 특정 메뉴의 투입 원자재 중량을 변경 등록한 조작자 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 구성 품목의 본사 표준 원재료 상품 카테고리 정보와 매칭하기 위해 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 실시간 매출 전송 처리 시 본 레시피에 배포된 특정 대체 상품의 매핑 오류 및 누락 로그를 모니터링하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 가맹점 총 수납 매출액 대비 본 레시피 구성 중량을 통해 역산된 원자재 비용의 마진율을 검증하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 96. TB_RECIPE_GOODS_HISTORY MEMO AND RELATED TABLES
    tb_recipe_goods_history_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 레시피 구성 원부자재 상세 마스터 변경 이력 테이블 (`TB_RECIPE_GOODS_HISTORY`).\n"
        "가맹점별 레시피 세부 구성 성분(`TB_RECIPE_GOODS`)의 생성, 수정, 삭제(조리 중량 변경, 대체 자재 등록 등) 작업 발생 시, 해당 변경 트랜잭션의 원천 필드 상태 및 변경 유형(신규 등록 `A`, 수정 `U`, 삭제 `D`), 이력 로그 순번(`LOG_NO`) 등을 실시간으로 백업 기록하여 개정 히스토리를 감사 보존하는 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **트리거 자동 로깅 (`TB_RECIPE_GOODS_T01` 트리거)**: 백오피스의 가맹점/본사 레시피 관리 화면에서 원자재 소요 내역 변경이나 대체 품목 지정 작업 실행 시, 테이블 이벤트 감시 트리거(`TB_RECIPE_GOODS_T01`)가 이를 실시간 포착하여 변경 전/후 레코드를 로그 순번(`log_no`)과 함께 자동 인서트합니다.\n"
        "* **과거 제조원가 소급 및 조리법 개정 추적**: 특정 시점에 판매된 메뉴의 실제 소요량을 역사적으로 역산하여 정확한 일일/월말 수불 정합성을 규명하거나, R&D 조리 가이드라인의 버전 개정 역사를 추적 감사하기 위해 백오피스 변경 이력 조회 화면(`Hq_Master_00007`, `St_Master_00003`)에서 이 테이블을 원천 로그로 사용합니다."
    )

    data["tables"]["tb_recipe_goods_history"] = {
        "memo": tb_recipe_goods_history_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 계열사 분류 코드 (4자리)",
            "recipe_cd": "완성품 메뉴 또는 반제품의 레시피 식별 코드 (8자리)",
            "ms_no": "매장코드 (점포 코드)",
            "goods_cd": "레시피 구성 원부자재 상품코드 (20자리)",
            "log_no": "변경 이력에 대해 자동으로 순차 채번되는 이력 로그 고유 순번",
            "proc_fg": "레시피 정보 변경 유형 구분 코드 (A: 신규 등록, U: 수정 변경, D: 삭제)",
            "weight": "변경 발생 시점 기준 적용 표준 소요 중량/수량 (numeric 14,3)",
            "replace_goods_cd": "변경 발생 시점 기준 지정된 대체 원자재 상품코드",
            "replace_weight": "변경 발생 시점 기준 지정된 대체 원자재 소요 중량/수량",
            "create_dtime": "레시피 상세 품목 최초 매핑 등록 일시 (YYYYMMDD)",
            "create_id": "레시피 상세 품목 최초 매핑 등록자 ID",
            "last_dtime": "본 이력 로그 레코드가 생성 기록된 시점의 수정 일시 (YYYYMMDD)",
            "last_id": "본 이력 로그 생성을 야기한 변경 조작자 ID"
        },
        "memo_c": "레시피 구성 테이블(TB_RECIPE_GOODS)에 INSERT/UPDATE/DELETE 조작이 가해질 때 DB 트리거(TB_RECIPE_GOODS_T01)에 의해 자동 인서트됩니다.",
        "memo_u": "이력 아카이브 테이블이므로 최초 자동 생성 이후 데이터 수정은 영구 방지됩니다.",
        "memo_d": "과거 제조 원가 및 재고 소모 계산의 소급 정합성 규명을 위한 소중한 감사 증빙 자료이므로 임의 삭제가 불허됩니다.",
        "memo_r": "가맹점 레시피 변경 이력 분석(Hq_Master_00007), 매장별 조리법 개정 이력 조회(St_Master_00003), 과거 일자 재고 재계산 시 히스토리가 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_recipe_goods",
                "description": "가맹점 레시피 구성 원부자재 상세 마스터. [트리거 TB_RECIPE_GOODS_T01 연동] 실시간으로 원부자재 구성 성분의 투입량 및 대체 관계에 가해진 편집 변동(A/U/D)을 본 이력 테이블에 보관하는 대상 원천 마스터 테이블 관계입니다."
            },
            {
                "table_name": "tb_recipe",
                "description": "가맹점 레시피 마스터. 변경 이력이 기록된 원천 완성품 메뉴의 한글 명칭 및 재고 차감 규칙 상태를 매칭하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 과거 특정 시점에 적용되었던 원자재 단품의 성격 및 가격 유효 범위를 확인하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 과거 시점의 레시피 변경으로 인해 실고량 차감 비율 오차가 발생했을 때, 수불 복구 및 실사 재고 시뮬레이션을 역산하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 레시피 개정 이력이 발생한 가맹점 점포의 계열 유형을 판별하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 과거 시점에 적용된 원자재 중량 이력과 입고가 대장을 결합하여 레시피 히스토리컬 제조원가 변동 추이를 분석할 때 간접 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 과거 원자재 가격 변동 시기와 레시피 개정(대체 재고 적용 등) 시점을 연동 비교하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 과거 특정 일자의 영수증 매출에 대해 당시 유효했던 변경 이력 레시피를 매핑하여 소요량을 재추정할 때 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 레시피 개정 횟수 상한 및 본사 배포 로그 저장 기한 등의 기본 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 처리 구분 코드(A: 신규, U: 수정, D: 삭제) 및 상품 분류 등의 한글 명칭을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 레시피 품목을 최종 변경하여 본 이력 로그를 발생시킨 조작자 ID의 사번 및 실명을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 개정 대상 원재료의 본사 표준 상품 코드 및 정합성을 유지하기 위해 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 레시피 개정 배포 시 통신 에러 로그 또는 점포 적용 실패 상황을 모니터링하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 과거 특정 영업 기간 동안의 레시피 변경 전후의 마진 요율 변동 추이를 비교 분석하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 97. TB_SET_GOODS MEMO AND RELATED TABLES
    tb_set_goods_memo = (
        "### 1. 테이블 개요\n"
        "세트 메뉴 구성 상품 상세 마스터 테이블 (`TB_SET_GOODS`).\n"
        "가맹점 또는 체인별(`CHAIN_NO`)로 기획 배포된 세트 메뉴 상품코드(`SET_CD`)를 구성 단품 상품코드(`COMP_GOODS_CD`) 및 해당 구성 단품의 수량(`SET_QTY`)으로 정의하는 세트 메뉴 세부 매핑 통제 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **판매 시점 세트 분해 전개 (`SUB_SET_IO_P` 프로시저)**: 가맹점 POS에서 단체 세트메뉴 또는 콤보 팩이 매출 승인 완료되면, 정산 배치 구동 시 본 세트 구성 마스터(`TB_SET_GOODS`)를 전개하여 세트에 속한 개별 구성 단품들의 코드(`comp_goods_cd`) 및 수량(`set_qty`)을 각각 계산해 낸 후, 각 단품에 매핑된 최종 원부자재 레시피 소요량 차감(`SUB_RECIPE_IO_P`)을 연동해 줍니다.\n"
        "* **물류 공급 및 매장 간 양도 양수 전개 (`SUB_STOCK_MGMVHD_P` 프로시저)**: 본사에서 세트 패키지 물류 출고를 하거나 매장 간 자재 이동 시, 세트 상품 구성 품목을 자동으로 분해하여 출하 및 재고 이동을 처리해 줌으로써 정교한 재고 변동 정합성을 유지합니다."
    )

    data["tables"]["tb_set_goods"] = {
        "memo": tb_set_goods_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 계열사 분류 코드 (4자리)",
            "set_cd": "세트 메뉴의 대표 상품코드 (8자리, MGOODSTB의 세트 유형 코드와 매핑)",
            "comp_goods_cd": "세트를 구성하는 개별 단품 상품코드 (20자리)",
            "set_qty": "세트 메뉴 내에 포함된 해당 구성 단품의 개수 (numeric 11,2)",
            "create_dtime": "세트 구성 매핑 최초 등록 일시 (YYYYMMDD)",
            "create_id": "세트 구성을 등록 승인한 상품기획자 ID",
            "last_dtime": "세트 구성 최종 수정 변경 일시 (YYYYMMDD)",
            "last_id": "세트 구성을 수정한 최종 조작자 ID"
        },
        "memo_c": "본사 상품 기획 및 가맹점 세트 메뉴 구성 화면에서 세트 아이템을 구성 단품과 연결하여 인서트합니다.",
        "memo_u": "세트 메뉴 내 단품 구성비 수정, 수량(set_qty) 변경 또는 패키지 내용물 갱신 시 업데이트됩니다.",
        "memo_d": "과거 판매 실적 기준의 세트 분해 및 구성 단품별 가중 매출액 산정의 원천 요율이므로 임의 삭제가 차단됩니다.",
        "memo_r": "POS 세트 메뉴 매출 발생 시 단품 분해 배치(SUB_SET_IO_P), 본사 세트 자재 물류 이동 전개(SUB_STOCK_MGMVHD_P), 세트 구성별 마진 요율 배분 시 기준 마스터로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_recipe",
                "description": "가맹점 레시피 마스터. 세트 메뉴 자체가 가지고 있는 마스터 정의 및 세트 재고 관리 여부(stock_yn)를 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tb_recipe_goods",
                "description": "레시피 구성 원부자재 상세 마스터. [배치 SUB_SET_IO_P 연동] 세트에서 분해된 각 개별 구성 단품(comp_goods_cd)의 조리 시 투입되는 원재료 종류 및 소요 중량을 읽어오기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 세트 메뉴 상품 속성(세트 메뉴의 면세/과세 여부 및 가구가격) 및 구성품으로 설정된 단품들의 개별 판매 유효성을 판별하기 위해 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. [배치 SUB_SET_IO_P 연동] POS 세트 매출 확정 시, 세트 분해 구성 단품의 수량만큼 매장 현재고 테이블의 자재 실고량을 최종 차감 처리합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 체인 번호(chain_no) 및 가맹점 유형별로 상이한 세트 구성 정책 및 판촉 패키지 구성을 분석하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 세트 분해 구성 단품들의 입고 원가를 조합하여 세트 메뉴 하나의 실제 원가 및 마진율을 평가할 때 간접 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 세트 상품 입고에 대응하는 물류 매입 실적 검증 시 간접 참조됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 판매 완료된 세트 메뉴 영수증 목록을 매출 상세 테이블에서 읽어 세트 전개 프로시저의 처리 대상 모수로 활용합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 세트 메뉴 최대 구성품 갯수 제한 및 강제 분해 허용 여부 플래그 등의 제어 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 세트 메뉴 분류(예: 프로모션 세트, 디저트 콤보 등) 한글 라벨명을 조인하여 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 메뉴 관리 화면에서 신규 세트 구성을 설계 및 수동 수정한 조작자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 구성 품목들의 본사 표준 원재료 상품 카테고리 정보와 매칭하기 위해 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 매출 전송 전문 분석 시 세트 구성 매핑 오류로 인한 재고 차감 누락 에러 로그를 모니터링하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 가맹점 매출 수납 확정 시 세트 단위로 발생한 매출액과 세트 분해 이론 원가 대비 마진율을 분석하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 98. TB_SL_RECIPE_GOODS MEMO AND RELATED TABLES
    tb_sl_recipe_goods_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 매출 영수증 상품별 조리 레시피 소요 원재료 이력 테이블 (`TB_SL_RECIPE_GOODS`).\n"
        "가맹점 POS에서 실제 결제 완료 및 취소된 개별 영수증 품목 단위별로, 메뉴 조리 레시피(`TB_RECIPE_GOODS`) 혹은 세트 메뉴 세부 구성(`TB_SET_GOODS`)을 기준으로 매칭 전개하여, 매출 시점에 소요된 실제 구성 원재료 종류(`RECIPE_GOODS_CD`), 원재료명(`RECIPE_GOODS_NM`), 소요 이론량/중량(`RECIPE_WEIGHT`) 및 상위 세트코드(`SET_CD`) 등을 개별 영수증 라인 단위로 영구 기록 보존하는 매출-재고 상세 연결 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **영수증 건별 이론 재고 소요 전개 (`SUB_SL_RECIPE_GOODS_P` 프로시저)**: 일 정산 배치 동작 시, 당일 발생한 개별 매출 영수증 품목 상세(`STRNDTTB`) 데이터에 대해 가맹점 R&D 조리 레시피 구성을 1:N으로 폭넓게 곱하여, 판매된 메뉴 하나하나를 만들기 위해 소모된 이론적인 원자재 소요량을 산출하여 본 테이블에 적재합니다.\n"
        "* **실시간 반품/취소에 따른 자동 가감 (`STRNDT_T01` 트리거)**: 영업 시간 도중 POS 영수증의 캐셔 오작동, 고객 변심 등으로 품목 취소 및 반품 수정 전표(`STRNDTTB`)가 입력될 경우, 해당 영수증에 링크되어 있던 원자재 이력(`TB_SL_RECIPE_GOODS`)도 이벤트 감시 트리거(`STRNDT_T01`)에 의해 실시간으로 마이너스(-) 보정 처리되어 데이터 무결성을 유지합니다."
    )

    data["tables"]["tb_sl_recipe_goods"] = {
        "memo": tb_sl_recipe_goods_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "POS에서 매출 결제 승인이 발생한 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "line_no": "영수증 내 개별 매출 품목의 고유 라인 번호 (4자리)",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품/수정 전표)",
            "chain_no": "체인 및 계열사 분류 코드 (4자리)",
            "goods_cd": "POS에서 판매 등록한 매출 메뉴 상품코드 (20자리)",
            "goods_nm": "매출 메뉴의 한글 상품명",
            "sale_tot": "할인 전 매출 원금액 총액",
            "sale_amt": "실제 결제 승인된 순매출 금액",
            "dc_amt": "해당 매출 라인에 적용된 할인 금액 총액",
            "sale_qty": "해당 메뉴 품목의 판매 등록 수량",
            "recipe_cd": "소요량 계산의 기준이 된 원천 레시피 식별 코드 (8자리)",
            "idx": "레시피 구성원료의 정렬 인덱스 번호",
            "recipe_goods_cd": "해당 메뉴 제조를 위해 소모된 원부자재/원자재 상품코드 (20자리)",
            "recipe_goods_nm": "소모된 원부자재의 한글 상품명",
            "recipe_weight": "해당 영수증 라인 매출(수량)로 인해 소요된 원자재의 총 소요 중량 (numeric 13,2)",
            "recipe_inv_unit": "원부자재의 물류 재고 관리 단위 (g, ml, 개, box 등)",
            "set_cd": "매출 메뉴가 세트 품목의 구성원일 경우, 상위 세트메뉴의 대표 상품코드",
            "create_dtime": "영수증별 레시피 소요량 전개 기록 생성 일시 (YYYYMMDD)",
            "create_id": "본 이력을 생성한 시스템 또는 조작자 ID",
            "last_dtime": "레시피 소요량 최종 변경/수정 일시 (YYYYMMDD)",
            "last_id": "레시피 소요량 최종 변경/수정한 조작자 ID"
        },
        "memo_c": "일일 가맹점 마감 정산 배치(SUB_SL_RECIPE_GOODS_P 프로시저) 실행 시 매출 원장을 기반으로 자동 전개되어 대량 생성 적재됩니다.",
        "memo_u": "영수증 반품 및 수정 전표 발생 시 STRNDT_T01 트리거에 의해 해당 영수증에 연계된 원자재 소요 내역이 보정 업데이트됩니다.",
        "memo_d": "매출 거래와 재고 소비 흐름을 증빙하는 핵심 회계 및 세무 감사 로그이므로 임의 삭제가 영구히 금지됩니다.",
        "memo_r": "영수증별 레시피 소요 분석(Hq_Stock_00001), 재고 로스율 분석 보고서(Hq_Stock_00019), 매장 매출 소요 이론량 분석(St_Stock_00007), 차주 발주량 예측 분석(Hq_Vendor_00018) 시 핵심 원천 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_recipe_goods",
                "description": "가맹점 레시피 구성 원부자재 상세 마스터. [배치 SUB_SL_RECIPE_GOODS_P 연동] 매출된 메뉴에 설정된 매장별 1회 조리 당 표준 투입량 및 원부자재 기준 정보를 확인하는 대상 원천 마스터 관계입니다."
            },
            {
                "table_name": "tb_recipe",
                "description": "가맹점 레시피 마스터. 매출 품목의 레시피 한글 이름 및 재고 차감 유효성(stock_yn) 설정을 비교 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "tb_set_goods",
                "description": "세트 구성 마스터 테이블. 매출된 메뉴가 세트 구성품인 경우, 해당 단품을 포함하고 있던 대표 세트코드(set_cd)의 매핑 관계를 규명하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. [배치 SUB_SL_RECIPE_GOODS_P 연동] 실제 POS에서 결제 완료된 영수증의 메뉴 매출 실적(단가, 수량, 할인금액 등)을 가져와 본 레시피 소요량 이력을 생성하는 대상 매출 원천 테이블입니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 영수증 단위의 전체 매출 정상 승인 여부, 회원 할인 혜택 및 세금 정보를 대조 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 매출 상품 자체의 분류 속성과 세무 상의 부가세 과세/면세 설정을 비교하기 위해 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 가맹점 영수증별 조리 레시피 소요 원자재 이력(TB_SL_RECIPE_GOODS)의 누적량과 실제 재고 실사 변동량 간의 차이를 계산하여 재고 로스율 통계(Hq_Stock_00019)를 추출할 때 비교 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점 점포의 계열 유형별 매출원가 소모량과 수수료율 배분 정책을 비교 대사하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 영수증 매출 소모 이력에 기록된 원자재 중량(recipe_weight)에 선입선출 단가를 곱하여 개별 영수증 건별 정밀 매출원가(COGS)를 계산하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 실시간 소요 원자재 이력을 토대로 차주 원재료 소요량 예측 발주 통계(Hq_Vendor_00018)를 산출할 때 비교 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 영수증별 레시피 소요 이력 저장 기한 설정 및 소수점 중량 버림/반올림 처리 규칙 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 재고 관리 단위 한글 명칭 및 매출 구분 코드 한글 라벨명을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 영수증의 매출 전표를 취소 또는 임의 보정한 점포 캐셔 사번의 소속 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 레시피 구성 자재의 본사 표준 상품 코드 분류 체계를 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 매출 영수증 전송 지연 및 누락으로 인한 레시피 전개 오류 이력을 규명하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 99. TB_SL_SET_GOODS MEMO AND RELATED TABLES
    tb_sl_set_goods_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 매출 영수증 세트 구성 단품 분해 이력 테이블 (`TB_SL_SET_GOODS`).\n"
        "가맹점 POS에서 실제 결제 완료 및 취소된 개별 영수증 품목 단위별로, 세트 메뉴 상품(`GOODS_CD`)에 포함된 개별 단품 구성 요소(`COMP_GOODS_CD`), 세부 분해 판매 단가(`COMP_UPRICE`), 세부 분해 매입 원가(`COMP_UCOST`), 세부 분해 수량(`SET_QTY` 및 `COMP_IN_QTY`) 등을 매핑 전개하여, 세트 판매 건에 대해 개별 영수증 라인 단위로 영구 기록 보존하는 매출-단품 분해 상세 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **세트 영수증 건별 단품 분해 전개 (`SUB_SL_SET_GOODS_P` 프로시저)**: 일 정산 배치 동작 시, 당일 발생한 개별 매출 영수증 품목 상세(`STRNDTTB`) 데이터 중 세트 메뉴에 해당하는 거래에 대해 가맹점 세트 메뉴 구성 마스터(`TB_SET_GOODS`)를 1:N으로 폭넓게 곱하여, 판매된 세트를 구성 단품 자재 형태로 완전히 전개하고 판매대금 및 원가를 규정 요율로 배분하여 본 테이블에 적재합니다.\n"
        "* **재고 및 손익 대사의 사전 기점**: 본 테이블을 기반으로 세트 내부 단품들의 실제 조리법(`TB_SL_RECIPE_GOODS`)을 도출하며, 백오피스 공통 영수증 조회 팝업 모듈(`CommonModule_BillInfo`)에서 매출 영수증 내 세트 품목의 구성 내역과 분해 금액을 렌더링하기 위한 원천 로그로 활용됩니다."
    )

    data["tables"]["tb_sl_set_goods"] = {
        "memo": tb_sl_set_goods_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "POS에서 매출 결제 승인이 발생한 영업 일자 (YYYYMMDD)",
            "ms_no": "매장코드 (점포 코드)",
            "pos_no": "POS 기기 식별 번호 (2자리)",
            "bill_no": "POS 영수증 일련번호 (4자리)",
            "line_no": "영수증 내 개별 매출 품목의 고유 라인 번호 (4자리)",
            "sale_fg": "매출 구분 코드 (0: 정상 매출, 1: 취소/반품/수정 전표)",
            "chain_no": "체인 및 계열사 분류 코드 (4자리)",
            "goods_cd": "POS에서 판매 등록한 매출 대표 세트 상품코드 (20자리)",
            "goods_nm": "매출 대표 세트의 한글 상품명",
            "uprice": "매출 당시 세트 상품의 할인 적용 전 판매 단가",
            "ucost": "매출 당시 세트 상품에 할당된 표준 원가",
            "ucost_vat": "매출 당시 세트 상품 원가의 부가세액",
            "in_qty": "매출 당시 세트 상품의 판매 수량 (소모 수량)",
            "sale_tot": "할인 전 세트 매출 원금액 총액",
            "sale_amt": "실제 결제 승인된 세트 순매출 금액",
            "dc_amt": "해당 세트 매출 라인에 적용된 할인 금액 총액",
            "sale_qty": "해당 세트 품목의 판매 등록 수량",
            "set_cd": "세트 구성을 지시하는 세트 식별 코드 (8자리)",
            "comp_goods_cd": "세트 내에 포함되어 실제 출고 분해되는 개별 구성 단품 상품코드 (20자리)",
            "comp_goods_nm": "분해 구성 단품의 한글 상품명",
            "comp_uprice": "세트 판매액 중 해당 단품에 최종 배분된 배분 판매단가",
            "comp_ucost": "세트 원가 중 해당 단품에 최종 배분된 배분 매입원가",
            "comp_ucost_vat": "해당 단품 매입원가에 상응하는 부가세액",
            "comp_in_qty": "세트 1단위 판매 당 투입되는 해당 단품의 소요량 (구성 수량)",
            "set_fg": "세트 메뉴 구성 성격 구분 플래그",
            "set_qty": "세트 내 해당 단품의 구성 표준 요율 수량",
            "recipe_cd": "해당 단품의 조리 시 참조할 레시피 식별 코드 (8자리)",
            "create_dtime": "영수증별 세트 분해 기록 생성 일시 (YYYYMMDDHH24MISS)",
            "create_id": "본 이력을 생성한 시스템 또는 조작자 ID",
            "last_dtime": "세트 분해 기록 최종 변경/수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "세트 분해 기록 최종 변경/수정한 조작자 ID"
        },
        "memo_c": "일일 가맹점 마감 정산 배치(SUB_SL_SET_GOODS_P 프로시저) 실행 시 매출 원장을 기반으로 자동 전개되어 대량 생성 적재됩니다.",
        "memo_u": "영수증 반품 및 수정 전표 발생 시 정산 취소 프로세스에 의해 해당 영수증에 연계된 세트 분해 이력이 보정 업데이트됩니다.",
        "memo_d": "세트 매출 거래의 품목 분해 및 매출 배분 흐름을 증빙하는 핵심 회계 및 세무 감사 로그이므로 임의 삭제가 영구히 금지됩니다.",
        "memo_r": "어드민 공통 영수증 상세 조회 모듈(CommonModule_BillInfo), 영수증별 레시피 소요 분석(Hq_Stock_00001), 재고 로스율 분석 보고서(Hq_Stock_00019), 매장 매출 소요 이론량 분석(St_Stock_00007) 시 세트 전개 상세 내역 조회 원장으로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_set_goods",
                "description": "세트 구성 마스터 테이블. [배치 SUB_SL_SET_GOODS_P 연동] 매출된 세트 메뉴에 할당된 가맹점 R&D 구성 단품 종류 및 세트 콤보 규격 수량을 확인하기 위한 대상 원천 마스터 관계입니다."
            },
            {
                "table_name": "tb_recipe",
                "description": "가맹점 레시피 마스터. 매출 세트 메뉴 및 분해된 구성 단품들의 레시피 관리 적용 여부(stock_yn)를 비교 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tb_recipe_goods",
                "description": "레시피 상세 테이블. 세트 분해 이력(TB_SL_SET_GOODS)을 바탕으로 최하위 소요 원자재(원재료 중량)를 전개하기 위한 중간 브릿지로 활용됩니다."
            },
            {
                "table_name": "tb_sl_recipe_goods",
                "description": "영수증 레시피 소요 이력 테이블. 세트 분해 후 각 단품에 매핑된 원재료별 수불 감산 이력을 추적 감사할 때 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. [배치 SUB_SL_SET_GOODS_P 연동] POS 영수증의 매출 세트 품목 결제 승인 실적(단가, 수량, 할인금액)을 가져와 세트 분해 레코드를 생성하는 대상 원천 매출 상세 테이블입니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 영수증 단위의 전체 매출 취소 및 거래 정합성을 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장별 상품 마스터 테이블. 매출 세트 상품과 세트 내 단품들의 개별 과세 구분 및 가구가격, 상품 상태를 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 세트 분해 후 구성 단품 수량을 기준으로 점포 원자재 재고 차감을 유도하기 위한 간접 재고 연계 관계입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 점포의 가맹 계약 형태(프랜차이즈 계열)별 세트 프로모션 배분 마진 요율을 산출하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 세트 분해 이력에 기록된 구성품별 원가(comp_ucost)와 선입선출 입고 누적 대장의 매입가를 조합하여 세트 메뉴 개별 손익 원가를 정밀 대사하기 위해 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 세트 분해 단품 실적을 토대로 점포별 차주 발주량을 예측 정산하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 영수증별 세트 분해 이력 로그 저장 기한 및 단가 배분 소수점 절사 처리 파라미터를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 세트 구분 코드 및 매출 구분 코드 한글 라벨명을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스에서 특정 세트 영수증 매출을 취소 또는 임의 보정한 점포 캐셔 및 정산 조작자 ID의 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 세트 상품 및 구성 단품의 본사 표준 상품 코드 분류 체계를 대조하기 위해 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 세트 매출 영수증 전송 및 세트 분해 중 발생한 매핑 실패 오류 로그를 모니터링하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 100. TB_TOT_AVG_COST MEMO AND RELATED TABLES
    tb_tot_avg_cost_memo = (
        "### 1. 테이블 개요\n"
        "본사 기준 상품 월별 수불 및 월말 총평균 재고 자산 평가/원가 집계 테이블 (`TB_TOT_AVG_COST`).\n"
        "본사(HQ) 및 전사 가맹점 체인 계열(`CHAIN_NO`) 수준에서 월별(YYYYMM)로 발생한 개별 원부자재 및 상품의 전사 통합 수불(기초이월 `START_QTY`/`START_COST`, 당월총매입, 당월총반품, 당월총매출 `SALE_QTY`/`SALE_COST`, 기타입출고, 폐기, 재고조정, 도매판매 등) 내역을 집계하고, 본사 기준 총평균법 재고 평가 단가(`TOT_AVG_COST`), 표준 원가(`UCOST`), 표준대비 편차(`GAP_UCOST`) 등을 월별로 최종 확정 기록하는 본사 수불 결산 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **본사 월말 결산 및 재계산 배치 (`SUB_TOT_AVG_P` 및 `SUB_TOT_AVG_SINGLE_P` 프로시저)**: 매월 말 본사 재고 결산 가동 시, 점포별 수불 마스터(`TB_IMMMIO_COST`) 정보를 취합하고 본사 물류창고 입출고 데이터를 통합 롤업하여 전사 기준 총평균단가 및 전사 기말 재고 평가 가액을 계산 및 적재합니다.\n"
        "* **유통 마진 및 협력사 정산 대사**: 본사 물류창고에서 가맹점으로 공급한 유통 마진 및 편차 원가(`gap_ucost`)를 규명하여 협력사 정산 검증 화면(`St_Vendor_00003`, `St_Vendor_00004`, `St_Vendor_00005`)의 기본 회계 증빙으로 연동 제공됩니다."
    )

    data["tables"]["tb_tot_avg_cost"] = {
        "memo": tb_tot_avg_cost_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "create_month": "수불 및 본사 원가 집계가 실행된 영업 월 (YYYYMM)",
            "chain_no": "체인 및 계열사 분류 코드 (6자리)",
            "goods_cd": "수불 및 원가 평가 대상 상품/원자재 코드 (20자리)",
            "start_qty": "전월 말 기준 이월된 본사 기초 재고 수량",
            "start_cost": "이월된 본사 기초 재고 평가 금액 총액",
            "purch_qty": "당월 한 달간 본사 물류로 매입 입고된 상품 누적 수량",
            "purch_cost": "당월 매입 입고된 상품의 매입 원가 누적 총액",
            "return_qty": "당월 공급처로 매입 반품 출고된 누적 상품 수량",
            "return_cost": "당월 반품 출고된 상품의 매입 원가 차감 누적 총액",
            "sale_qty": "당월 한 달간 가맹점 공급 및 외부 도매로 출고된 상품 누적 총수량",
            "sale_cost": "당월 출고 상품에 대응하는 총평균 매출원가(COGS) 누적 총액",
            "in_qty": "기타 입고(수동 보정 등)된 당월 누적 상품 수량",
            "in_cost": "기타 입고 상품의 평가 원가 누적 총액",
            "out_qty": "기타 출고(수동 보정 등)된 당월 누적 상품 수량",
            "out_cost": "기타 출고 상품의 평가 원가 누적 총액",
            "disuse_qty": "당월 한 달간 본사 유통 과정 중 폐기 처리된 상품 누적 수량",
            "disuse_cost": "당월 폐기 상품의 매입 원가 손실 누적 총액",
            "adjust_qty": "당월 한 달간 본사 재고 조사 결과 수동 조정된 누적 수량",
            "adjust_cost": "당월 재고 실사 조정에 따른 자산 변동 누적 평가 금액",
            "tin_qty": "당월 한 달간 타계정에서 입고 대체된 누적 상품 수량",
            "tin_cost": "당월 타계정 입고 대체 상품의 평가 원가 누적 총액",
            "tout_qty": "당월 한 달간 타계정으로 출고 대체된 누적 상품 수량",
            "tout_cost": "당월 타계정 출고 대체 상품의 평가 원가 누적 총액",
            "returndis_qty": "당월 반품 처리 후 현지 폐기 처리된 누적 상품 수량",
            "returndis_cost": "당월 반품 폐기 상품의 평가 금액 누적 총액",
            "move_in_qty": "당월 한 달간 물류 센터 간 양도 이동 입고된 누적 상품 수량",
            "move_in_cost": "이동 입고된 상품의 양수 평가 금액 누적 총액",
            "move_out_qty": "당월 한 달간 물류 센터 간 양도 이동 출고된 누적 상품 수량",
            "move_out_cost": "이동 출고된 상품의 양도 평가 금액 누적 총액",
            "wholesale_qty": "당월 대량 특판 거래로 출고된 누적 상품 수량",
            "wholesale_cost": "도매 출고 상품의 도매 원가 누적 총액",
            "wholesale_rt_qty": "당월 도매 매출 건 중 반품 취소된 누적 상품 수량",
            "wholesale_rt_cost": "도매 반품 상품의 원가 차감 누적 총액",
            "end_qty": "당월 말 마감 기준 본사 창고에 잔존하는 기말 실고 재고 수량",
            "end_cost": "당월 말 마감 기준 기말 재고 평가 금액 총액",
            "tot_qty": "당월 마감 기준 총 수량 (기초 + 당월 입고 누계)",
            "tot_amt": "당월 마감 기준 총 자산 금액 (기초 + 당월 입고 누계액)",
            "tot_avg_cost": "본사 월간 가중 총평균법 알고리즘에 의해 최종 산출된 월 마감 재고 단가",
            "ucost": "상품 마스터에 등록된 표준 물류 원가 단가",
            "tgood_in_qty": "원부자재 및 상품의 당월 규격 누적 총입고 수량",
            "ucost_in_qty": "입고단가 가중치 반영 당월 입고누적 금액 (단가 * 수량 소수점 처리금액)",
            "gap_ucost": "표준 원가 대비 월 총평균 실제 입고 단가와의 편차 발생 누적 총액"
        },
        "memo_c": "월말 본사 결산 배치(SUB_TOT_AVG_P 프로시저) 실행 시 각 가맹점/창고별 수불 기록을 본사/체인 기준으로 통합 롤업하여 자동 생성 기록됩니다.",
        "memo_u": "월말 수동 정산 보정, 본사 표준 원가 마감 변경 적용 및 재계산 배치 프로시저 가동 시 업데이트됩니다.",
        "memo_d": "본사 법인 결산, 유통 세무 신고 및 협력사 정산의 최종 증빙 자료이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "협력사 월말 매입 단가 정산 대사(St_Vendor_00003), 협력사 월말 기말 자산 평가 조회(St_Vendor_00004), 협력사 공급 마진 대조(St_Vendor_00005) 시 최종 기준 원장으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_immmio_cost",
                "description": "가맹점 상품 월별 수불 및 월말 재고 자산 평가/원가 집계. 가맹점 단위별 기말 실재고 및 수불 실적을 본사/체인 기준 수불 테이블(TB_TOT_AVG_COST)과 대조/검증하여 전사 정합성을 확보하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 본사 표준 원재료 상품 대분류/중분류/소분류 체계 및 매입 면과세 설정을 매칭 조인하여 본사 재고 평가 분석용 품목 속성을 획득합니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 본사 표준 창고 및 유통 거점별 현재고 상태와 월 기말 재고(end_qty)의 차이를 대사하고 연계 검증할 때 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점 체인 유형(chain_no)별 물류 공급 규칙 및 전사 물류 배송 경로의 기준점을 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 본사 월 총평균단가(tot_avg_cost)와 물류창고 선입선출 단가를 매칭하여 본사 유통 마진 및 재고 자산 평가 손익 차액을 산정할 때 조인 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 협력업체로부터 본사 물류창고로 입고된 월간 총 매입량(purch_qty 및 purch_cost)의 세부 거래 내역을 검증 대사하기 위해 조인 참조합니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 본사 유통 판매 실적에 기반한 도매 매출량(wholesale_qty) 및 도매 반품 실적의 원천 거래 내역을 대사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 본사 재고 결산용 반올림 소수점 규칙 및 협력사 월 정산 마감 주기 파라미터를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 상품 대분류 명칭 및 면과세 구분, 거래처 등급 한글 라벨명을 조인하여 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 본사 수불을 월말 수동으로 마감 승인하거나 총평균단가를 보정 처리한 본사 재무/정산 담당자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 본사 물류 수불 배치 가동 시 발생한 에러 정보 및 ERP 결산 인터페이스 통신 상태를 모니터링하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 본사 공급망 도매 매출과 가맹점 최종 소매 매출액의 원가 대비 전사 마진 추세를 대조 분석하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 101. TB_TOT_AVG_COST_HISTORY MEMO AND RELATED TABLES
    tb_tot_avg_cost_history_memo = (
        "### 1. 테이블 개요\n"
        "본사 기준 상품 월별 수불 및 월말 총평균 재고 자산 평가/원가 변경 이력 테이블 (`TB_TOT_AVG_COST_HISTORY`).\n"
        "본사 및 체인별 월별 수불 원장(`TB_TOT_AVG_COST`) 테이블에 정산 보정, 수동 원가 단가 수정 또는 재계산 처리가 가해질 때, 변경 실행 이전 단계의 과거 수불 수량, 매입/출고 총액, 기말 자산 평가액 및 총평균단가 등의 원천 데이터를 이력 고유 순번(`IDX`)과 함께 백업 저장하여 수불 감사 추적을 보존하는 이력 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **재계산 전 백업 적재 (`SUB_TOT_AVG_P` 프로시저)**: 월간 정산 마감 후, 세무 조정 등으로 인해 본사 총평균단가를 재계산하는 배치 프로시저(`SUB_TOT_AVG_P`)가 실행될 때 기존 마감 완료 수불 행을 본 이력 테이블(`TB_TOT_AVG_COST_HISTORY`)에 복사 적재한 뒤, 원본 원장을 최신 계산값으로 업데이트 갱신합니다.\n"
        "* **결산 감사 및 원가 감사 대응**: 외부 회계 감사 또는 본사 원가 감사 시, 특정 월의 상품 재고 평가액이 변동된 원인과 이전 상태 수불 지표를 시점별로 대조 역산하기 위한 핵심 보존 증빙 로그로 활용됩니다."
    )

    data["tables"]["tb_tot_avg_cost_history"] = {
        "memo": tb_tot_avg_cost_history_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "idx": "이력 로그를 식별하는 고유 일련번호/인덱스 코드 (20자리)",
            "create_month": "수불 및 원가 집계가 실행되었던 대상 영업 월 (YYYYMM)",
            "chain_no": "체인 및 계열사 분류 코드 (6자리)",
            "goods_cd": "수불 및 원가 평가 대상 상품/원자재 코드 (20자리)",
            "start_qty": "이력 생성 시점의 기초 재고 수량",
            "start_cost": "이력 생성 시점의 기초 재고 평가 금액 총액",
            "purch_qty": "이력 생성 시점의 누적 물류 매입 입고 수량",
            "purch_cost": "이력 생성 시점의 누적 매입 원가 총액",
            "return_qty": "이력 생성 시점의 누적 매입 반품 출고 수량",
            "return_cost": "이력 생성 시점의 누적 반품 출고 매입 원가 차감 총액",
            "sale_qty": "이력 생성 시점의 누적 가맹점 공급 및 도매 출고 수량",
            "sale_cost": "이력 생성 시점의 누적 매출원가(COGS) 총액",
            "in_qty": "이력 생성 시점의 기타 입고 수량",
            "in_cost": "이력 생성 시점의 기타 입고 평가 총액",
            "out_qty": "이력 생성 시점의 기타 출고 수량",
            "out_cost": "이력 생성 시점의 기타 출고 평가 총액",
            "disuse_qty": "이력 생성 시점의 누적 폐기 수량",
            "disuse_cost": "이력 생성 시점의 누적 폐기 원가 총액",
            "adjust_qty": "이력 생성 시점의 누적 실사 재고 조정 수량",
            "adjust_cost": "이력 생성 시점의 누적 재고 실사 조정 평가 금액",
            "tin_qty": "이력 생성 시점의 누적 타계정 대체 입고 수량",
            "tin_cost": "이력 생성 시점의 누적 타계정 대체 입고 평가액",
            "tout_qty": "이력 생성 시점의 누적 타계정 대체 출고 수량",
            "tout_cost": "이력 생성 시점의 누적 타계정 대체 출고 평가액",
            "returndis_qty": "이력 생성 시점의 누적 반품 폐기 수량",
            "returndis_cost": "이력 생성 시점의 누적 반품 폐기 평가액",
            "move_in_qty": "이력 생성 시점의 누적 물류 센터 간 이동 입고 수량",
            "move_in_cost": "이력 생성 시점의 이동 입고 양수 평가 총액",
            "move_out_qty": "이력 생성 시점의 누적 물류 센터 간 이동 출고 수량",
            "move_out_cost": "이력 생성 시점의 이동 출고 양도 평가 총액",
            "wholesale_qty": "이력 생성 시점의 누적 도매/대량 판매 수량",
            "wholesale_cost": "이력 생성 시점의 누적 도매 판매 원가 총액",
            "wholesale_rt_qty": "이력 생성 시점의 누적 도매 반품 취소 수량",
            "wholesale_rt_cost": "이력 생성 시점의 누적 도매 반품 원가 차감 총액",
            "end_qty": "이력 생성 시점의 기말 재고 수량",
            "end_cost": "이력 생성 시점의 기말 재고 평가 금액 총액",
            "tot_qty": "이력 생성 시점의 총 수량 (기초 + 입고 누계)",
            "tot_amt": "이력 생성 시점의 총 자산 금액 (기초 + 입고 누계액)",
            "tot_avg_cost": "이력 생성 시점 산출되어 있던 월 총평균 재고 단가",
            "ucost": "상품 마스터에 등록된 표준 물류 원가 단가",
            "tgood_in_qty": "원부자재 및 상품의 당월 규격 누적 총입고 수량",
            "ucost_in_qty": "입고단가 가중치 반영 당월 입고누적 금액 (단가 * 수량 소수점 처리금액)",
            "gap_ucost": "표준 원가 대비 월 총평균 실제 입고 단가와의 편차 발생 누적 총액",
            "create_dtime": "본 이력 로그 레코드가 백업 생성 적재된 일시 (YYYYMMDDHH24MISS)",
            "create_id": "본 이력 로그 적재 배치를 실행 조작한 시스템 또는 관리자 ID"
        },
        "memo_c": "월말 본사 재결산 배치(SUB_TOT_AVG_P 프로시저) 재구동 시, 원본 데이터 업데이트 전에 기존 수불 정보가 자동으로 이관 백업 적재됩니다.",
        "memo_u": "이력 보존용 로그 테이블이므로 최초 자동 생성 이후 데이터 수정은 영구 방지됩니다.",
        "memo_d": "본사 유통 마진 및 법인 재고 자산 변동의 시점별 감사 이력이므로 임의 삭제가 영구히 불허됩니다.",
        "memo_r": "본사 총평균단가 재계산 이력 대조, 세무 감사 원가 변경 추적, 결산 수불 오차 규명 시 과거 시점 조회용 원장으로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_tot_avg_cost",
                "description": "본사 기준 상품 월별 수불 및 월말 총평균 재고 자산 평가/원가 집계. [프로시저 SUB_TOT_AVG_P 연동] 본사 기준 수불 단가 재계산 또는 수정 처리 전, 이전 상태의 수불 기록 및 총평균 자산 정보를 백업 적재하는 원천 대상 마스터 관계입니다."
            },
            {
                "table_name": "tb_immmio_cost",
                "description": "가맹점 상품 월별 수불 및 월말 재고 자산 평가/원가 집계. 가맹점별 수불과 본사 이력 로그 간의 원가 편차 규명 및 소급 원가 검증 시 간접 매칭 조인 참조됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 개정 이력이 발생한 원재료 품목의 표준 규격 및 세무 상의 면세/과세 구분을 비교 분석하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 과거 재고 자산 평가 내역 수정 시점의 실물 재고 변동량 추세를 시뮬레이션하기 위해 간접 참조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 체인 유형(chain_no)별 과거 수불 보정 규칙 및 전사 유통 경로의 기준점을 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 정산 테이블. 과거 원가 이력과 선입선출 원가 간의 재고 자산 평가액 추이 차이를 시계열로 분석하기 위해 간접 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 과거 시점의 물류 매입 입고 기록과 본사 재고 평가 이력의 시간적 정합성을 확인하기 위해 간접 참조합니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매출 시점의 과거 총평균원가와 실제 매출 원천 거래량을 대사하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 본사 재고 이력 로그 보존 연한 및 결산 보정 임계값 설정을 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 상품 대분류 명칭 및 면과세 구분, 거래처 등급 한글 라벨명을 조인하여 매핑하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 과거 특정 월에 총평균단가를 재계산하거나 본 이력을 발생시킨 본사 재무/정산 담당자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 본사 물류 수불 배치 가동 시 발생한 에러 정보 및 ERP 결산 인터페이스 통신 상태를 모니터링하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 본사 공급망 도매 매출과 가맹점 최종 소매 매출액의 원가 대비 전사 마진 추세를 대조 분석하기 위해 간접 참조됩니다."
            }
        ]
    }

    # 102. TB_USER_LAST_MENU MEMO AND RELATED TABLES
    tb_user_last_menu_memo = (
        "### 1. 테이블 개요\n"
        "사용자 최근 실행 메뉴/화면 이력 테이블 (`TB_USER_LAST_MENU`).\n"
        "백오피스 시스템을 이용하는 개별 사용자(`USER_ID`)가 마지막으로 접근 및 로드했던 메뉴 일련번호(`MENU_SEQ`)와 최종 접근 일시(`LAST_DTIME`)를 저장하여, 최근 접속 현황 모니터링, 개인별 대시보드 자주 쓰는 메뉴 구성 및 세션 끊김 시 마지막 화면 복구 등의 편의성을 제공하는 기능성 이력 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **화면 전환 시 실시간 업데이트**: 본사, 매장 및 전체 어드민 정산 관리 시스템에서 사용자가 특정 화면 메뉴를 클릭하여 컴포넌트가 로드될 때, 사용자 고유 사번 기준으로 최종 접근 일시(`last_dtime`) 및 실행한 메뉴 시퀀스(`menu_seq`)를 실시간으로 인서트 또는 업서트(Upsert) 처리합니다.\n"
        "* **최근 접속 현황 통계 분석**: 본사의 가맹점 관리 및 정산 대사 작업 도중, 특정 점포 관리자 혹은 본사 정산 담당자가 어떤 재고/정산 화면을 자주 보는지, 혹은 보안 상 불법적인 경로로 메뉴에 직접 접근했는지 여부를 감사 역추적할 때 연계 분석됩니다."
    )

    data["tables"]["tb_user_last_menu"] = {
        "memo": tb_user_last_menu_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "user_id": "시스템에 접속한 사용자 고유 식별 ID (로그인 사번 등)",
            "menu_seq": "해당 사용자가 최근에 실행/접근한 메뉴 화면 일련번호 (6자리)",
            "last_dtime": "해당 메뉴 화면에 최종 로드된 일시 (YYYYMMDDHH24MISS)",
            "last_id": "해당 레코드 최종 수정을 야기한 조작자 ID (접근자 본인)"
        },
        "memo_c": "백오피스 웹 애플리케이션 프레임워크 인터셉터(Interceptor) 또는 화면 전환 이벤트 발생 시 실시간 인서트/업서트됩니다.",
        "memo_u": "동일 사용자가 새로운 화면에 접근할 때마다 최근 실행 메뉴와 일시가 실시간으로 갱신 업데이트됩니다.",
        "memo_d": "시스템 탐색 흐름 분석 및 감사 로깅을 위한 기초 자료이므로 일정 보존 기간 동안 임의 삭제가 금지됩니다.",
        "memo_r": "어드민 사용자 사용이력 분석(Admin_Emp_00001), 본사 최근 접속 통계(Hq_Emp_00001), 매장 대시보드 최근 즐겨찾기(St_Emp_00001) 등 대시보드 및 통계 화면 작성 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 특정 메뉴를 마지막으로 실행한 사용자의 실명, 직급 및 접근 권한(본사, 매장, 어드민 등)을 확인하기 위해 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 사용자가 접속한 최근 실행 메뉴의 권한 분류 및 시스템 구분 명칭 한글 코드를 조인하여 명칭을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 사용자의 메뉴 탐색 트랜잭션 중 보안 상의 위반 시도나 비정상 접근 시 감사 로그를 역추적하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 최근 사용 메뉴 최대 보관 갯수(예: 최근 5개 또는 10개) 및 로그 자동 삭제 임계 시간 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 매장 사용자(user_id)가 소속되어 근무 중인 가맹점 점포의 계열 정보를 확인하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 103. TBE_EMP_INF MEMO AND RELATED TABLES
    tbe_emp_inf_memo = (
        "### 1. 테이블 개요\n"
        "본사 임직원 및 사원 정보 연동 인터페이스 원장 테이블 (`TBE_EMP_INF`).\n"
        "본사 및 계열사 ERP/HR 인사 시스템으로부터 전송 및 주기적 수집(인터페이스 전문 `IF_FB_303`)되는 임직원 기본 인사 정보(사원번호 `EE_NO`, 사원명 `EE_NM`, 회사코드 `COMP_CD`, 회사명 `COMP_NM`, 부서코드, 직급/직책코드 및 사용 여부 `USE_YN` 등)와 HMS 백오피스 사용자 계정 동기화 진행 상태(`POS_PROC_YN`, `POS_PROC_REMARK` 등)를 보존하는 실시간 인터페이스 staging 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **인사 전문 수신 및 대기**: ERP 인사 발령(입사, 퇴사, 부서 이동, 승진 등) 발생 시 실시간 텔렉스 수신 모듈(`P03_SqlMapper`)을 거쳐 `TBE_EMP_INF`에 수신 저장되며 최초 상태는 `pos_proc_yn = 'N'`(처리 대기) 상태가 됩니다.\n"
        "* **임직원 계정 동기화 배치 (`EmpInterface` 배치 서비스)**: HMS 배치 서버가 주기적으로 구동되어 미처리된 임직원 행(`pos_proc_yn = 'N'`)들을 취합하여, HMS 백오피스 및 POS 사용자 마스터 테이블(`MUSERSTB`)의 사원 정보(비밀번호 제외한 실명, 소속 부서, 가맹점 발령, 계정 활성화 유무 등)를 최종 싱크하고 동기화 성공 상태를 `Y`로 업데이트합니다."
    )

    data["tables"]["tbe_emp_inf"] = {
        "memo": tbe_emp_inf_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "rowid": "데이터베이스 행 식별용 고유 시스템 일련번호 (rowid_global_seq)",
            "comp_cd": "소속 법인 회사코드 (4자리)",
            "ee_no": "임직원 고유 사원번호 (HMS MUSERSTB의 USER_ID로 매핑)",
            "ee_nm": "임직원 성명 (실명)",
            "comp_nm": "소속 법인 회사명",
            "dept_cd": "소속 부서코드",
            "dept_nm": "소속 부서명",
            "job_pos_cd": "소속 직급코드",
            "job_pos_nm": "소속 직급명 (예: 대리, 과장, 부장 등)",
            "job_rsp_cd": "소속 직책코드",
            "job_rsp_nm": "소속 직책명 (예: 파트장, 팀장 등)",
            "use_yn": "임직원 인사 상의 재직 및 계정 사용 여부 플래그 (Y: 재직, N: 퇴사/정지)",
            "rgnr_id": "인사 데이터 수신 등록자 ID",
            "rgnr_dtm": "인사 데이터 최초 수신 및 등록 일시 (Timestamp)",
            "updr_id": "인사 데이터 최종 수정자 ID",
            "updr_dtm": "인사 데이터 최종 수정 및 상태 갱신 일시 (Timestamp)",
            "area_cd": "임직원 소속 근무 지역/지점 구분 코드",
            "pos_proc_date": "HMS 백오피스 배치 동기화 처리가 실행된 영업 일자 (YYYYMMDD)",
            "pos_proc_seq": "동일 영업일 내 동기화 처리 순번 시퀀스",
            "pos_proc_yn": "백오피스 동기화 처리 완료 여부 플래그 (Y: 반영완료, N: 미반영/대기, E: 에러)",
            "pos_proc_remark": "동기화 처리 과정 중 발생한 상세 메시지 및 예외 에러 메시지 로그",
            "pos_proc_create_dtime": "동기화 처리 최초 시도 일시 (YYYYMMDDHH24MISS)",
            "pos_proc_last_dtime": "동기화 처리 최종 상태 업데이트 완료 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "ERP/HR 시스템에서 주기적으로 인사 변동 사항 발생 시 텔렉스 전문 수신 모듈을 거쳐 실시간 인서트됩니다.",
        "memo_u": "동기화 배치 실행 완료 시 POS 처리 상태(pos_proc_yn) 및 최종 완료 시간 등이 업데이트됩니다.",
        "memo_d": "회사 임직원 권한 감사 및 인사 이동 증빙을 보존하는 staging 테이블이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "ERP 임직원 동기화 배치 Mapper(EmpInterface_SqlMapper), 텔렉스 수신전문 Mapper(P03_SqlMapper), 사용자 정보 일괄 감사 분석 시 인터페이스 원천열로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. [배치 EmpInterface 연동] ERP/HR에서 넘어온 임직원 정보(TBE_EMP_INF)를 기반으로 사원번호(ee_no)가 존재하는 HMS 백오피스 사용자 테이블의 사번명, 부서, 직급 정보를 최종 싱크/업데이트 처리하는 직접 연계 마스터 관계입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 가맹점 점포 근무 임직원들의 본사 소속 여부 및 점포 발령 관계를 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 직급 코드(job_pos_cd) 및 직책 코드(job_rsp_cd)에 매핑되는 한글 라벨명과 사용 여부(use_yn) 명칭을 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 임직원 전문 연동 오류(pos_proc_yn = 'E') 발생 시의 통신 패킷 에러 메시지 상세 내역 및 텔렉스 수신 실패 이력을 모니터링하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. ERP 임직원 동기화 주기 및 임직원 자동 비밀번호 초기화 규칙 등의 제어 변수를 매칭 참조합니다."
            }
        ]
    }

    # 104. TCALENTB MEMO AND RELATED TABLES
    tcalentb_memo = (
        "### 1. 테이블 개요\n"
        "영업 및 정산 기준 달력 테이블 (`TCALENTB`).\n"
        "회사 전체의 일별(`CAL_DATE`), 주차별(`WEEKS`), 월별(`CAL_YYMM`), 분기별(`QUARTER`) 날짜 정보와 각 날짜의 요일 속성(요일코드 `DAY_CD`, 요일명 `DAY_NAME`) 및 해당 주차의 시작일(`F_WEEKDAY`), 종료일(`T_WEEKDAY`) 등을 미리 계산하여 적재 보존하는 전사 공통 영업 달력 기준 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **다차원 매출 통계 집계의 기준 디멘션 (Dimension)**: 매출 상세(`STRNDTTB`), 매출 헤더(`STRNHDTB`) 등 대용량 데이터 조회 시 복잡한 날짜 연산 함수(TO_CHAR, EXTRACT 등)를 매번 수행하는 비효율을 제거하기 위해, 본 달력 테이블을 일자 기준으로 매핑 조인하여 요일별, 주차별, 분기별 매출 통계를 매우 신속하게 피벗 집계 및 집계 처리합니다.\n"
        "* **전사 영업 영업일 및 공휴일 통제**: 본사/매장의 대시보드 화면 및 공휴일 관리 화면(`Hq_Master_00023`, `St_Master_00015`)에서 특정 영업 예정일이나 정기 점검 휴무일을 캘린더 상에 설정 및 연동 통제하는 기준표 역할을 담당합니다."
    )

    data["tables"]["tcalentb"] = {
        "memo": tcalentb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "cal_date": "영업 및 정산의 기준이 되는 일자 (YYYYMMDD, PK)",
            "cal_year": "해당 일자의 연도 구분 (YYYY)",
            "cal_yymm": "해당 일자의 연월 구분 (YYYYMM)",
            "cal_month": "해당 일자의 월 구분 (MM)",
            "day_cd": "요일 구분 숫자 코드 (1: 일요일, 2: 월요일 ... 7: 토요일 등)",
            "day_nm": "요일 영문/한글 약어 표현 (예: MON, TUE)",
            "day_name": "요일 전체 명칭 표현 (예: Monday, Tuesday)",
            "days": "해당 연도의 1월 1일로부터 누적된 총 일수 (Day of Year)",
            "weeks": "해당 연도의 누적 주차 (Week of Year)",
            "f_weekday": "해당 주차(weeks)의 첫 번째 영업 요일 일자 (YYYYMMDD)",
            "t_weekday": "해당 주차(weeks)의 마지막 영업 요일 일자 (YYYYMMDD)",
            "quarter": "해당 일자가 속하는 분기 구분 코드 (1: 1분기, 2: 2분기, 3: 3분기, 4: 4분기)"
        },
        "memo_c": "시스템 최초 구축 시 또는 매년 연말에 다년치 달력 데이터를 수동 또는 프로시저로 대량 일괄 생성 적재합니다.",
        "memo_u": "국가 임시 공휴일 지정 또는 본사 정기 의무 휴업일 가맹점 달력 반영 시 일부 컬럼 속성이 업데이트됩니다.",
        "memo_d": "전사 다차원 통계 리포트, 일 마감 정산 쿼리의 근간이 되는 핵심 기준 달력이므로 임의 삭제가 영구 방지됩니다.",
        "memo_r": "본사/매장 대시보드(Hq_Dashboard, St_Dashboard), 공휴일 설정 화면(Hq_Master_00023, St_Master_00015), 일별/요일별/월별 매출 분석 통계 화면(Hq_Sales_00001~00030, St_Sales_00001~00030) 조회 시 기준 디멘션 테이블로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 매출 실적 통계 추출 시, 요일별/주차별/분기별 매출 추이를 피벗 집계하기 위해 매출 일자 기준으로 조인되는 핵심 관계입니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 일별 가맹점 전체 순매출액 및 영수증 결제 건수를 연월별, 분기별로 그룹핑하여 트렌드를 분석할 때 조인됩니다."
            },
            {
                "table_name": "tb_imddio_cost",
                "description": "가맹점 상품 일별 수불 및 원가 집계/평가 이력. 가맹점별 일일 재고 수불 및 총평균 자산 평가 실적을 특정 주차(weeks) 또는 분기(quarter) 단위로 롤업 분석하기 위해 조인됩니다."
            },
            {
                "table_name": "tb_immmio_cost",
                "description": "가맹점 상품 월별 수불 및 월말 재고 자산 평가/원가 집계. 가맹점 월말 재고 마감 평가서 및 월별 세무 통계를 대조하기 위해 월(cal_yymm) 기준으로 매칭 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점 개점일자 및 휴무 예정 캘린더 정합성을 전사 공휴일 설정과 비교하기 위해 간접 참조합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 선입선출 입고 일자를 기준으로 연도별/분기별 매입 자산 원가 분석 보고서를 작성할 때 조인 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 발주 매입 확정일자를 주차별로 그룹핑하여 본사 물류센터 주간 입고 예정량을 산정할 때 조인 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 회계 연도 시작월 설정 및 주차 채번 방식(ISO 표준 등) 기본 파라미터를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 요일 코드(1~7) 및 분기(1Q~4Q) 한글 명칭 라벨을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 달력 설정 화면에서 특정 일자를 임시 임직원 휴무일이나 판촉 특수일로 변경 등록한 어드민 조작자의 계정 정보를 조회하기 위해 조인됩니다."
            }
        ]
    }

    # 105. TCHAINTB MEMO AND RELATED TABLES
    tchaintb_memo = (
        "### 1. 테이블 개요\n"
        "체인 및 계열사 분류 정보 마스터 테이블 (`TCHAINTB`).\n"
        "프랜차이즈 및 유통 법인 산하의 브랜드 체인 사업부(예: 카페 브랜드, 베이커리 브랜드 등)의 마스터 정의(체인 코드 `CHAIN_NO`, 체인 명칭 `CHAIN_NM`, 소재지/본사구분 `PLACE`, 계열 구분 `AFFILIATE_COMPANY` 등)를 중앙에서 영구 통제하는 조직 체계 기준 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **권한 제어 및 브랜드 필터링의 핵심 앵커 (`UserAuth_Sql`)**: 백오피스 로그인 성공 시, 본 테이블의 체인 정보(`chain_no`)를 조회해와 해당 관리 계정의 세션 권한을 특정 브랜드로 즉시 귀속/제한하여 타 브랜드 매출이나 재고를 조회할 수 없도록 물리적 가드레일을 칩니다.\n"
        "* **점포 및 상품의 체인 귀속 통제 (`MMEMBS_T01` 트리거)**: 가맹점 마스터(`MMEMBSTB`)에 신규 가맹점이 입점하거나 정보가 변경될 때, `TCHAINTB`에 등재된 유효한 체인 번호인지 정합성 트리거를 통해 체크하고 귀속 계열사를 강제 싱크합니다."
    )

    data["tables"]["tchaintb"] = {
        "memo": tchaintb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 고유 식별 코드 (4자리, PK)",
            "chain_nm": "체인 브랜드 한글 명칭 (예: 백화점사업부, 물류사업부 등)",
            "place": "본사 및 영업 소재지 구분 코드 (공통명칭 NM_FG=063 매핑)",
            "affiliate_company": "귀속 계열 법인 구분 코드 (공통명칭 NM_FG=064 매핑)",
            "create_dtime": "체인 브랜드 최초 마스터 등록 승인 일시 (YYYYMMDDHH24MISS)",
            "create_id": "체인 마스터 등록자 ID",
            "last_dtime": "체인 마스터 최종 변경 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "체인 마스터 최종 변경 조작자 ID"
        },
        "memo_c": "최고 시스템 어드민 화면에서 새로운 브랜드 법인을 계열사에 편입 시킬 때 수동으로 영구 인서트됩니다.",
        "memo_u": "체인 한글 명칭 변경 또는 소재지 법인 개편 시에만 극히 제한적으로 업데이트됩니다.",
        "memo_d": "전사 가맹점, 매출, 재고 원장의 물리적 귀속 기준이 되는 테이블이므로 삭제가 영구 불가합니다.",
        "memo_r": "어드민 권한 관리(UserAuth), 공통 상품 분류 필터링(CommonModule_GoodsClass), 어드민 체인/계열사 설정(Admin_Master_00003~00005), 본사 가맹점/체인별 정보 설정(Hq_Master_00004~00021) 조회 시 최우선 기준 마스터로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [트리거 MMEMBS_T01 연동] 각 개별 점포 가맹점이 속해 있는 전사 체인 브랜드 및 계열 관계를 규명하기 위해 1:N으로 연결 조인됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 특정 체인 브랜드에서 취급하는 표준 원재료 및 완제품 카테고리 구성 체계를 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tb_recipe",
                "description": "가맹점 레시피 마스터 테이블. 특정 완성품 조리 레시피가 어느 체인 브랜드 공급 정책에 할당되어 있는지 기준을 잡기 위해 조인됩니다."
            },
            {
                "table_name": "tb_set_goods",
                "description": "세트 메뉴 구성 상품 상세 마스터 테이블. 프로모션 콤보 세트 구성 상품들이 어느 체인 패키지에 속하는지 정의하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 로그인 시, 본사/가맹점 직원의 접근 권한이 어느 체인/Affiliate 법인으로 제한되는지 필터링(UserAuth_Sql)하기 위해 사용자 마스터와 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 전사 브랜드 통합 매출 리포트를 생성하거나 계열사별 매출 추이를 피벗 집계할 때 조인됩니다."
            },
            {
                "table_name": "tb_tot_avg_cost",
                "description": "본사 기준 상품 월별 수불 및 월말 총평균 재고 자산 평가/원가 집계. 체인/법인 단위별로 월말 결산 원가를 마감하여 전사 재고 평가액을 별도로 산출하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 각 체인별로 설정되는 POS 화면 테마, 영수증 꼬리말 설정 및 ERP 전송 주기를 구분 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 체인 구분 영문/숫자 코드에 대응하는 본사/소재지(place, 063) 및 계열사(affiliate_company, 064) 한글 명칭 라벨을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 체인 간 데이터 이전 및 특정 브랜드 통신 장애 상황 모니터링 시 간접 연계됩니다."
            }
        ]
    }

    # 106. TCLOSETB MEMO AND RELATED TABLES
    tclosetb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 영업일 정산 마감 상태 관리 테이블 (`TCLOSETB`).\n"
        "체인별(`CHAIN_NO`) 각 가맹점 점포(`MS_NO`)가 매일 영업을 정상 종료하고 POS 및 백오피스 상의 일 정산 마감 처리를 완료한 영업일자(`CLOSE_DATE`)와 마감 확정 일시, 조작자 정보 등을 기록하고 락(Lock)을 거는 점포 일마감 기준 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **일 마감 프로세스 통제 및 락킹 (Locking)**: 매일 밤 점주가 POS 또는 백오피스 정산 화면(`St_Master_00015`)에서 최종 일 정산 마감 버튼을 클릭하면, 수납 금액 대사 후 본 테이블에 해당 일자 레코드가 인서트됩니다. 이 마감 행이 생성되면 해당 일자의 매출 상세(`STRNDTTB`) 및 입출고 데이터 수정/추가 조작이 시스템적으로 엄격하게 금지(Locking)됩니다.\n"
        "* **본사 정산 배치 및 마감 취소 통제**: 본사 정산 담당자는 모니터링 화면(`Hq_Master_00023`)을 통해 전사 가맹점의 마감 진척 상태를 모니터링하고, 가맹점의 수동 오류 수정 요청 시 특정 점포의 마감 데이터를 일시 삭제(마감 해제)하여 데이터를 보정할 수 있게 제어합니다."
    )

    data["tables"]["tclosetb"] = {
        "memo": tclosetb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 구분 코드 (4자리, PK)",
            "ms_no": "매장코드 (점포 코드, PK)",
            "close_date": "일 정산 마감이 완료 확정된 영업 일자 (YYYYMMDD, PK)",
            "ins_dtime": "일 마감 승인 확정이 실행된 최초 일시 (YYYYMMDDHH24MISS)",
            "ins_id": "일 마감 승인을 확정한 매장 근무자 혹은 점주 ID",
            "upd_dtime": "일 마감 상태가 최종 수정(마감 해제 등)된 일시 (YYYYMMDDHH24MISS)",
            "upd_id": "일 마감 상태를 수정한 조작자 ID (본사 관리자 등)"
        },
        "memo_c": "점포 영업 종료 후 백오피스 또는 POS 마감 확정 화면(St_Master_00015)에서 점주가 정산 승인 시 인서트됩니다.",
        "memo_u": "본사 정산 담당자가 가맹점의 재정산 요청을 받아 마감을 수동 보정 또는 취소 처리 시 업데이트 및 딜리트됩니다.",
        "memo_d": "정산이 마감된 과거 일자 매출/재고의 위변조 방지를 위한 법적/회계적 통제 기준선이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "본사 영업일 마감 현황 모니터링(Hq_Master_00023), 매장 일마감 통제/확정(St_Master_00015), 일별 수불 마감 및 매출원가 확정 배치 시 마감 유무 교차 참조용으로 조회됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 일마감을 수행한 매장의 이름, 소속 지역본부 및 현재 운영 여부를 대조 식별하기 위해 조인됩니다."
            },
            {
                "table_name": "strndttb",
                "description": "매출 상세 테이블. 점포의 일일 POS 매출 내역이 전부 수집되고 오류 전표가 없는지 검증한 후 일마감을 락(Lock)하기 위해 조인 대사합니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 마감일자(close_date)에 수납된 실제 신용카드, 현금, 포인트 총 수납금액과 POS 상의 영수증 마감 금액이 일치하는지 정합성을 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "tb_imddio_cost",
                "description": "가맹점 상품 일별 수불 및 원가 집계/평가 이력. 가맹점 일마감 확정(tclosetb 레코드 인서트)과 동시에 일별 수불 원가를 마감 락킹 처리하여 실물 재고 변동을 확정하기 위해 연동 참조됩니다."
            },
            {
                "table_name": "tcalentb",
                "description": "영업 및 정산 기준 달력 마스터 테이블. 특정 매장의 일마감이 누락된 일자가 요일별, 공휴일 여부와 관련이 있는지 통계 분석을 위해 조인 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 및 계열사 분류 정보 마스터. 브랜드 사업부 전체 매장의 일마감 진척률(일마감 완료 점포수 / 전체 점포수)을 모니터링하기 위해 조인됩니다."
            },
            {
                "table_name": "imcriotb",
                "description": "매장 현재고 정보 테이블. 매장의 일마감 시점 실재고 데이터가 전 영업일 기말 재고와 완벽히 맞아떨어지는지 검증하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 일마감 강제 승인 허용 정책, 강제 마감 취소 권한 범위 설정 등 통제 파라미터를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 일마감 처리 상태 구분 한글 라벨명을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 매장에서도 일마감을 누르고 수납 정산 처리를 확정한 점장 캐셔 계정 혹은 강제로 마감을 취소한 본사 담당자의 계정 정보를 조회하기 위해 조인됩니다."
            }
        ]
    }

    # 107. TCOMDCTB MEMO AND RELATED TABLES
    tcomdctb_memo = (
        "### 1. 테이블 개요\n"
        "본사 계열 협력 공급사 및 파트너 기업 그룹 마스터 테이블 (`TCOMDCTB`).\n"
        "프랜차이즈 가맹 본사에 원부재료, 포장 자재 등을 공급 납품하는 외부 협력 공급사 및 물류 파트너 거래처의 정보(거래처 그룹 코드 `COMP_CD`, 기업 그룹명 `COMP_NM`, 설명 `COMP_DC` 등)를 정의하고 관리하는 최상위 거래처 마스터 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **협력사 정보의 실시간 유동 반영**: ERP 거래처 원장 신규 등록 또는 변동 내역이 실시간 인터페이스 전문(`IF_FB_306` / `IF_FB_308` 전문)을 통해 텔렉스 연동 모듈(`M26_SqlMapper`)을 거쳐 `TCOMDCTB`로 인서트/업데이트됩니다.\n"
        "* **구매/물류 소싱의 연동점**: 본사 상품 마스터(`TGOODSTB`) 및 매장별 발주 매입 상세(`OBSLPDTB`)에 공급업체(`comp_cd`)로 지정 매핑되어 물류 공급망 및 월말 기말 매입 대사 업무의 기준 고리가 됩니다. 또한 협력사 직원의 로그인 세션 권한 부여 시 소속 분류 코드로 참조됩니다."
    )

    data["tables"]["tcomdctb"] = {
        "memo": tcomdctb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "comp_cd": "협력 공급사 및 파트너 기업 그룹 대표 코드 (20자리, PK)",
            "comp_nm": "협력 공급사의 공식 한글 상호명 (150자리)",
            "comp_dc": "협력사에 대한 비고 및 상세 취급 속성 설명",
            "create_dtime": "협력사 마스터 최초 수신 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록 생성자 ID (시스템 수신 또는 어드민 ID)",
            "last_dtime": "최종 정보 수정 변경 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 정보 수정 조작자 ID"
        },
        "memo_c": "ERP 거래처 동기화 인터페이스 전문 수신(M26_SqlMapper) 또는 어드민 협력업체 관리 화면(Admin_Master_00006)에서 신규 인서트됩니다.",
        "memo_u": "협력사 그룹 마스터 추가/변경 감시 트리거(TCOMDCTB_T01) 및 본사 협력업체 여신/등급 설정 화면(Hq_Master_00020)의 조작에 의해 업데이트됩니다.",
        "memo_d": "매입 거래 대장 및 물류 공급 공급처 소싱 정보의 근간이 되는 마스터이므로 임의 삭제가 영구 불허됩니다.",
        "memo_r": "어드민 협력업체 등록(Admin_Master_00006), 본사 협력업체 등급/여신 설정(Hq_Master_00020), 모바일 수주/발주(COMPANY), 텔렉스 수신전문 Mapper(M26_SqlMapper) 및 공급사 포탈 로그인 시 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점 점포가 식자재를 수주/발주할 때 연결할 로컬 사급/공급 협력사를 조회하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 각 개별 원자재 상품이 어떤 협력 공급사(comp_cd)를 통해 매입 및 유통되는지 소싱(Sourcing) 관계를 규명하기 위해 조인됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 또는 본사가 특정 협력사에 발주하여 매입된 상세 품목 거래 내역을 집계 대사할 때 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 협력사별로 공급한 입고 물류 대장의 선입선출 매입가 정합성을 검증하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "tb_tot_avg_cost",
                "description": "본사 상품 월별 수불 및 월말 총평균 재고 자산 평가/원가 집계. 협력사별 기말 매입 실적 및 공급 자산 평가액을 월말 정산 대사하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 협력사에 소속되어 백오피스의 납품 조회 및 정산 화면(St_Vendor_00003~5)을 이용하는 협력사 전용 웹 계정을 생성할 때 소속 회사 코드로 조인 매핑됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 협력사별 발주 마감 시간 규칙, 긴급 발주 허용 플래그 등 거래 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 협력사 분류 등급 한글 라벨명을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 협력사 전문 수신 연동 오류 시 텔렉스 통신 에러 메시지를 모니터링하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "strnhdtb",
                "description": "매출 헤더 테이블. 본사가 협력사에 지불할 매입 채무와 가맹점 매출 수납 대금을 상계 대사할 때 간접 참조됩니다."
            }
        ]
    }

    # 108. TDEPTMTB MEMO AND RELATED TABLES
    tdeptmtb_memo = (
        "### 1. 테이블 개요\n"
        "본사/체인 사업부 조직 부서 마스터 테이블 (`TDEPTMTB`).\n"
        "프랜차이즈 가맹 본사 및 전사 계열 브랜드의 행정 부서 및 조직 단위(부서 일련번호 `DEPT_NO`, 부서 코드 `DEPT_CD`, 부서명 `DEPT_NM` 등)를 정의 및 중앙 집중식으로 통제하는 공통 조직 구성 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **조직 정보의 정기 및 실시간 동기화**: 본사 ERP 시스템에 신규 부서가 생성되거나 조직 개편이 가해지면, 실시간 인터페이스 전문(`IF_FB_305` 전문)을 통해 텔렉스 수신 모듈(`M05_SqlMapper`)을 거쳐 `TDEPTMTB`에 자동 반영되며, 주기적 배치(`DeptInterface`)를 통해 ERP 조직도 정보와 상시 동기화 정합성을 유지합니다.\n"
        "* **계정 권한 및 업무 통제**: 시스템 사용자 마스터(`MUSERSTB`) 및 임직원 인사 원장(`TBE_EMP_INF`)과 부서 코드(`dept_cd`)로 결합되어, 로그인 직원의 부서 정보를 노출하고 부서별 업무 전용 화면 접근 권한을 분류하는 기본 차원으로 기능합니다."
    )

    data["tables"]["tdeptmtb"] = {
        "memo": tdeptmtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "dept_no": "부서 조직을 식별하는 고유 일련번호 (5자리, PK)",
            "dept_cd": "ERP 시스템 및 HMS 내부에서 통용되는 공식 부서코드 (10자리)",
            "dept_nm": "해당 부서의 공식 명칭 (예: 영남영업본부, R&D 개발팀 등)",
            "create_id": "부서 조직 데이터를 수신하거나 수동 등록한 생성자 ID",
            "create_dtime": "부서 데이터 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "last_id": "부서 정보를 최종 변경 수정한 수정자 ID",
            "last_dtime": "부서 정보 최종 변경 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "ERP 부서 마스터 연동 수신 전문(M05_SqlMapper) 또는 어드민 부서 조직 관리 화면(Admin_Master_00005)에서 조직 추가 시 자동 인서트됩니다.",
        "memo_u": "부서명 변경 또는 부서 코드 통합 시 ERP 변동 패킷 또는 어드민 조작에 의해 업데이트됩니다.",
        "memo_d": "인사 및 계정 권한 관리에 매핑된 핵심 조직 정보이므로 임의 삭제 시 권한 붕괴가 발생할 수 있어 삭제가 금지됩니다.",
        "memo_r": "어드민 부서 마스터 관리(Admin_Master_00005), 본사 조직도 및 영업본부 관리(Hq_Master_00006), 매장 부서 설정(St_Master_00002), 텔렉스 수신 Mapper(M05_SqlMapper) 및 사용자 정보 검색 시 소속 부서 조인용으로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 백오피스 사용자 계정별로 소속된 영업/정산/R&D 부서명(dept_nm)을 확인하고, 부서별 메뉴 접근 권한을 분류하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tbe_emp_inf",
                "description": "본사 임직원 및 사원 정보 연동 인터페이스 원장. ERP에서 수신된 임직원 데이터의 부서가 HMS 조직 마스터(TDEPTMTB) 상에 정상 등록된 유효 부서인지 유효성을 체크하기 위해 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 매장 소속 임직원의 점포 근무 부서와 가맹점 위치 관계를 분석하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 부서 성격 구분 및 영업본부 권한 한글 명칭 라벨을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 부서 정보 실시간 텔렉스 수신 동기화 오류(M05_SqlMapper 통신 장애 등) 시 패킷 로그를 모니터링하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. ERP 부서 동기화 주기 및 자동 생성되는 부서 권한 템플릿 제어 변수를 매칭 참조합니다."
            }
        ]
    }

    # 109. TESFRDTB MEMO AND RELATED TABLES
    tesfrdtb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 평수/규모별 초도 물품 공급 및 소요 기본량 표준 정보 테이블 (`TESFRDTB`).\n"
        "프랜차이즈 가맹점 신규 출점 시, 매장의 개설 규모/평형 등급(`ESTIM_TYPE_CD`, 예: 15평형, 30평형) 및 견적 품목 분류(`ESTIM_FROM_CD`, 예: 주방 기기, 가구 비품, 초도 원자재 물량)에 대응하여 투입되어야 하는 개별 상품/원자재(`ESTIM_GOODS_CD`), 규격 수량(`ESTIM_GOODS_QTY`), 기본 단가(`ESTIM_BAS_PRC`) 등의 개설 견적 표준 기준을 중앙에서 관리하는 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹 개발 견적서 자동 산출의 모체**: 본사 가맹개발 영업 부서에서 신규 가맹 계약 체결 및 견적 상담 시(`Hq_Esti_00003` 화면), 점포의 평형 유형만 선택하면 본 테이블(`TESFRDTB`)의 품목 템플릿 및 기준 수량을 1:N으로 복사해와 초도 견적서 총액을 1차 자동 생성해 줍니다.\n"
        "* **원가/마진 관리 및 설비 발주 연계**: 초도 견적 확정 후 실제 물류 발주(`Hq_Esti_00004`) 및 공급 완료 시, 본 테이블의 기본 견적 단가(`estim_bas_prc`)와 실제 입고된 물품의 선입선출 원가를 비교하여 가맹 개설 마진율을 시계열 분석하는 원천 데이터가 됩니다."
    )

    data["tables"]["tesfrdtb"] = {
        "memo": tesfrdtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "estim_type_cd": "점포 규모/평형 구분 등급 코드 (예: 010: 10평, 020: 20평 등, PK)",
            "estim_from_cd": "초도 견적 분류 형태 코드 (예: 01: 주방기기, 02: 인테리어, 03: 초도식자재 등, PK)",
            "estim_goods_cd": "견적 대상 본사 표준 상품/설비/자재 코드 (20자리, PK)",
            "estim_goods_spec": "해당 상품의 물류 및 본사 마스터 표준 규격 정보 (50자리)",
            "estim_ord_unit": "발주 단위 구분 코드 (공통명칭 NM_FG:121 매핑, 0: 본사, 1: 가맹점 등)",
            "estim_goods_qty": "해당 평형 등급 점포 개설 시 투입되는 기본 수량 (numeric 13,3)",
            "estim_bas_prc": "해당 품목의 개설 시점 기본 공급/매입 단가 (numeric 13,3)",
            "ins_dtime": "초도 물품 견적 마스터 등록 일시 (YYYYMMDDHH24MISS)",
            "ins_id": "초도 물품 견적 마스터 최초 등록자 ID",
            "upd_dtime": "초도 물품 견적 마스터 최종 변경 수정 일시 (YYYYMMDDHH24MISS)",
            "upd_id": "초도 물품 견적 마스터 최종 변경 조작자 ID"
        },
        "memo_c": "가맹개발 사업부에서 신규 평형대 매장 개설 정책을 수립하거나 품목군을 변경할 때 어드민 화면(Hq_Esti_00002)을 통해 수동 등록됩니다.",
        "memo_u": "설비 매입 단가 변동 및 본사 규격 사양 변경 적용 시 마스터 관리 화면 및 트리거(TESFRV_T01)를 거쳐 실시간 업데이트됩니다.",
        "memo_d": "과거 가맹점 개설 견적 총액 대사 및 계약서 원본 데이터의 정합성을 보증하는 기준 마스터이므로 임의 삭제가 금지됩니다.",
        "memo_r": "평형별 초도 물품 표준 설정(Hq_Esti_00002), 신규 점포 개설 견적서 생성(Hq_Esti_00003), 초도 설비 발주 및 검수(Hq_Esti_00004), 견적서 인터페이스 감사 시 최우선 마스터로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 초도 견적 표준 목록에 등록된 설비, 비품 및 초도 식자재의 최신 본사 표준 규격(PRODUCT_STANDARD), 세무 면과세 구분, 대표 단가를 비교 조인하기 위해 사용됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 어느 프랜차이즈 브랜드 사업부(예: 카페 vs 베이커리)의 가맹 개설 견적서 양식인지 브랜드를 매칭하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 신규 개점 예정인 가맹점의 실평수 및 계약 규모(estim_type_cd에 상응하는 점포 등급)를 확인하여 본 마스터 테이블의 수량 기준을 산출할 때 조인됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 개설 시 실제로 납품 완료된 초도 물량의 입출고 단가와 본 테이블의 표준 견적 단가(estim_bas_prc) 간의 단가 괴리율을 대사할 때 참조됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 견적서 생성 시점의 최신 선입선출 매입 원가를 대조하여 초도 설비 납품 시의 예상 본사 마진율을 평가할 때 간접 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 평형 등급(estim_type_cd, 예: 10평형, 20평형) 및 견적 품목 대분류(estim_from_cd, 예: 설비, 인테리어, 원부자재)의 한글 명칭 라벨과 발주 단위(estim_ord_unit, 121) 명칭을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 가맹 개발 표준 견적 단가를 보정하거나 신설 평형 기준을 입력한 본사 개설 담당자 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 초도 견적 생성 시 마진 요율 기본값 및 소수점 단가 반올림 처리 규칙 매개 변수를 매칭 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 신규 매장 초도 견적서 발주 내역을 본사 물류 시스템(WMS)으로 인터페이스 전송 시 발생하는 에러 로그를 모니터링하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 110. TESFRHTB MEMO AND RELATED TABLES
    tesfrhtb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 평수/규모별 초도 물품 분류 및 계약 조건 헤더 마스터 테이블 (`TESFRHTB`).\n"
        "프랜차이즈 가맹점 평형별 초도 물량 견적의 대분류(견적 구분 `ESTIM_FROM_CD`, 분류명 `ESTIM_FROM_NM`, 유효기간, 요구 적용일자 등) 및 견적서의 승인 사용 승인 유무 상태(`ESTIM_PROC_FG`)를 정의하고 관리하는 초도 물품 견적 마스터 헤더 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹 개발 견적의 버전 및 기간 통제**: 특정 평형 등급(예: 30평형)의 주방 설비 목록이 개편되거나 공급가가 일시 인상될 때, 이전 견적 헤더의 유효기간(`estim_to_date`)을 마감하고 신규 견적 헤더 레코드를 등록하여 견적서의 유효 차수를 통제합니다.\n"
        "* **하위 품목 상세와 유기적 동기화 (`TESFRH_T01` 트리거)**: 본 헤더 테이블의 처리 상태 플래그(`estim_proc_fg`)가 확정(`1`) 상태로 변경되면, 하위 품목 마스터(`TESFRDTB`) 내 모든 하위 물품들의 적용 유효 기간도 트리거에 의해 일괄 동기화 락킹 처리되어 가맹 개발 상담을 진행할 수 있도록 배포 승인됩니다."
    )

    data["tables"]["tesfrhtb"] = {
        "memo": tesfrhtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "estim_type_cd": "점포 규모/평형 구분 등급 코드 (예: 010: 10평, 020: 20평 등, PK)",
            "estim_from_cd": "초도 견적 분류 형태 코드 (예: 01: 주방기기, 02: 인테리어 등, PK)",
            "estim_from_nm": "초도 견적 분류 명칭 (예: 주방기기류, 냉장쇼케이스류, 매장가구비품류)",
            "estim_fr_date": "해당 견적 분류 및 조건의 적용 유효 시작일자 (YYYYMMDD)",
            "estim_to_date": "해당 견적 분류 및 조건의 적용 유효 종료일자 (YYYYMMDD)",
            "estim_req_fr_date": "견적 계약 체결이 시작 요구되는 조건 일자 (YYYYMMDD)",
            "estim_req_to_date": "견적 계약 체결이 종료 요구되는 조건 일자 (YYYYMMDD)",
            "estim_from_desc": "견적 분류 헤더의 적용 조건 및 예외사항에 대한 상세 설명 비고 (4000자)",
            "estim_proc_fg": "견적 처리 승인 상태 플래그 (0: 작성/등록, 1: 승인확정, 2: 비확정-단가미결)",
            "ins_dtime": "견적 마스터 헤더 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "ins_id": "견적 마스터 헤더 최초 등록자 ID",
            "upd_dtime": "견적 마스터 헤더 최종 변경 수정 일시 (YYYYMMDDHH24MISS)",
            "upd_id": "견적 마스터 헤더 최종 변경 조작자 ID"
        },
        "memo_c": "가맹개발 사업부에서 신규 평형대 매장 개설 정책을 수립하거나 품목군을 변경할 때 어드민 화면(Hq_Esti_00002)을 통해 수동 등록됩니다.",
        "memo_u": "설비 공급 기간 연장, 적용 요구일 보정 및 트리거(TESFRH_T01, TESFRH_T02)의 유효 마감 프로세스에 의해 업데이트됩니다.",
        "memo_d": "가맹 계약의 조건 및 설비 유효기간 기준을 감사 증빙하는 헤더 정보이므로 임의 삭제가 금지됩니다.",
        "memo_r": "평형별 초도 물품 표준 설정(Hq_Esti_00002), 신규 점포 개설 견적서 생성(Hq_Esti_00003), 초도 설비 발주 및 검수(Hq_Esti_00004), 협력사별 초도 정산 모니터링(Hq_Vendor_00001, St_Vendor_00001) 시 마스터 헤더 테이블로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tesfrdtb",
                "description": "초도 견적 상세 테이블. [트리거 TESFRH_T01 연동] 견적 분류에 포함되는 개별 기기, 비품, 상품 리스트와 표준 수량 정보를 담고 있는 1:N 하위 테이블 관계입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 견적서에 속한 품목들의 규격 및 과세 속성을 조회할 때 하위 상세 테이블과 조인 연계되는 기준 상품 마스터입니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 견적 템플릿이 속해 있는 브랜드(체인) 구분을 매핑 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 실평수 및 공사 계약에 링크된 유효 견적서를 매핑할 때 점포 정보를 참조하기 위해 조인됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 계약 조건 대비 실제 매입 입고된 설비 자재 대금을 정산 대사하기 위해 간접 조인 참조합니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 협력사 정산 보고서 작성 시 본사 마진 배산용 선입선출 매입가와 견적 단가를 대조하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 평형 구분 코드(estim_type_cd), 견적 처리구분 플래그(estim_proc_fg) 및 견적 적용 분류의 한글 구분을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 견적 마스터 헤더를 생성 및 최종 승인(estim_proc_fg = '1' 확정) 완료한 가맹 개발 책임자 사번의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 초도 견적 유효기간 기본 설정값 및 계약 해지 시 반환 보증금 처리 정책 규칙을 매칭 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 초도 견적 승인 시 ERP 자산 원장 연동 실패 로그를 모니터링하기 위해 간접 연계됩니다."
            }
        ]
    }

    # 111. TESFRVTB MEMO AND RELATED TABLES
    tesfrvtb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 초도 물품 분류 및 설비 공급사(협력업체) 매핑 관리 테이블 (`TESFRVTB`).\n"
        "체인별(`CHAIN_NO`), 평형 규모별(`ESTIM_TYPE_CD`), 견적 품목 분류(`ESTIM_FROM_CD`)에 대응하여 실제 기기/비품 납품 및 공사를 수행할 담당 협력 공급업체(`ESTIM_VENDOR`)를 매핑하고, 의뢰 메일 발송 결과(`ESTIM_SEND_YN`) 및 최종 견적 합의 수용 유무 상태(`ESTIM_SUG_YN`)를 관리하는 공급 계약 정산 매칭 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **공급처 의뢰서 발송 및 회신 검토 프로세스**: 가맹개발 담당자가 신규 출점 매장의 초도 견적을 작성한 뒤, 대분류별로 계약된 협력사들에게 메일로 견적 목록을 일괄 발송합니다(`Hq_Esti_00004` 화면 실행 시 `estim_send_yn = 'S'` 기록). 협력사가 이를 검토하여 수락하면 담당자가 본 테이블에 `estim_sugg_yn = 'Y'`(최종 합의)로 확정 기입하여 거래를 최종 낙찰 처리합니다.\n"
        "* **정보 변경 시 동기화 및 락킹 통제 (`TESFRV_T01` 트리거)**: 미정산 상태에서 공급사의 소속 이메일이나 담당 파트너가 변경되면, 데이터베이스 트리거에 의해 현재 진행 중인 미확정 견적서 행들의 이메일 수신 주소가 최신 정보로 자동 보정 갱신되어 전송 오류를 사전에 차단합니다."
    )

    data["tables"]["tesfrvtb"] = {
        "memo": tesfrvtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "estim_type_cd": "점포 규모/평형 구분 등급 코드 (예: 010: 10평, 020: 20평 등, PK)",
            "estim_from_cd": "초도 견적 분류 형태 코드 (예: 01: 주방기기, 02: 인테리어 등, PK)",
            "estim_vendor": "해당 견적 분류를 담당 납품하는 협력 공급사 코드 (TCOMDCTB의 COMP_CD 매핑, PK)",
            "estim_send_date": "협력 공급사 앞으로 최초 견적 발송 및 납품 의뢰를 요청한 일자 (YYYYMMDD)",
            "estim_send_yn": "의뢰 메일 전송 여부 상태 플래그 (N: 미전송, F: 전송실패, S: 메일 발송 완료)",
            "estim_send_mail_addr": "메일 의뢰 발송 시 수신된 협력 공급사 담당자의 메일 주소",
            "estim_sugg_yn": "의뢰 견적에 대한 협력사의 합의 수락 상태 구분 플래그 (N: 미결, K: 검토중, Y: 최종 합의확정)",
            "ins_dtime": "공급처 매핑 정보 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "ins_id": "공급처 매핑 정보 최초 등록자 ID",
            "upd_dtime": "공급처 매핑 정보 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "upd_id": "공급처 매핑 정보 최종 수정 조작자 ID"
        },
        "memo_c": "가맹개발부에서 특정 평형대 개설 정책 수립 시 품목 분류별 담당 공급업체를 지정(Hq_Esti_00002)할 때 인서트됩니다.",
        "memo_u": "의뢰 메일 발송 성공 시점 및 협력사 견적 조율 완료(sugg_yn = 'Y') 등록 처리 및 트리거(TESFRV_T01, TESFRH_T02) 구동 시 업데이트됩니다.",
        "memo_d": "가맹점 개설 납품 거래처 및 의뢰서 이메일 발송 사실을 보존하는 감사용 데이터이므로 임의 삭제가 금지됩니다.",
        "memo_r": "평형별 초도 물품 표준 설정(Hq_Esti_00002), 신규 점포 개설 견적서 생성(Hq_Esti_00003), 초도 설비 의뢰 메일 발송(Hq_Esti_00004), 협력사 피드백 회신 확인 및 정산(Hq_Esti_00005, Hq_Esti_00006) 시 매핑 마스터로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tcomdctb",
                "description": "협력사 마스터 테이블. 초도 설비/원재료 공급 계약을 맺은 협력 공급사의 상세 회사명, 대표 이메일, 담당 부서 연락처를 획득하기 위해 직접 조인되는 대상 마스터입니다."
            },
            {
                "table_name": "tesfrhtb",
                "description": "견적 분류 헤더 테이블. [트리거 TESFRH_T02 연동] 각 견적 대분류별로 의뢰 메일을 송신할 유효 견적서 헤더의 계약 기간 및 적용 대상을 비교 매칭하는 직접 마스터 관계입니다."
            },
            {
                "table_name": "tesfrdtb",
                "description": "견적 품목 상세 테이블. 견적 대분류 하위에 묶인 개별 세부 품목들의 예상 공급단가(estim_bas_prc) 총계를 계산하여 협력 공급사에게 일괄 의뢰서를 발송할 때 연동 참조됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 매핑 공급사가 제공할 의뢰 품목의 제조사 규격 및 면과세 여부를 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 프랜차이즈 브랜드별로 지정된 전문 식자재 유통 파트너사와 설비 업체를 분리 매칭하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 신규 개설되는 가맹점의 소재 지역 및 상권 정보를 토대로, 가장 인접한 로컬 공급사(estim_vendor)를 자동 추천/할당할 때 간접 연계됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 계약 마감 후 해당 공급처(estim_vendor)로 정식 입고 발주서가 정상 발행되었는지 대사하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 공급사가 납품한 초도 자재의 실제 매입 원가 내역을 정산 대사할 때 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 의뢰 메일 전송 여부 상태(estim_send_yn), 협력사 피드백 확정 상태(estim_sugg_yn) 등의 한글 명칭 라벨을 출력하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 공급업체와 견적 조율을 진행하고 최종 합의(estim_sugg_yn = 'Y') 처리를 입력한 가맹개발 담당자 계정 정보를 조회하기 위해 조인됩니다."
            }
        ]
    }

    # 112. TESHISTB MEMO AND RELATED TABLES
    teshistb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 평수/규모별 초도 물품 표준 단가 변경 이력 테이블 (`TESHISTB`).\n"
        "프랜차이즈 가맹 본사 가맹개발실에서 수립한 평형 규모별 설비 및 원재료의 견적 마스터가 갱신되거나 단가가 변경될 때, 변경 이전의 정보(기본 수량, 역사적 적용 단가 `ESTIM_ALY_PRC`, 유효 기간, 연장 승인 플래그 `ESTIM_EXTEND_YN` 등)를 일련의 변경 시퀀스(`ESTIM_SEQ`) 단위로 자동 이력 아카이빙 적재하는 이력 보존 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **자동 이력 트리거링 (`TESFRH_T01` 트리거)**: 가맹 개발 견적 마스터 화면(`Hq_Esti_00002`)을 통해 본사에서 특정 설비의 단가를 수정하여 저장하거나, 헤더(`TESFRHTB`)의 적용 만료 처리가 실행되는 순간, `TESFRH_T01` 트리거가 구동되어 이전 스냅샷 데이터를 본 이력 테이블(`TESHISTB`)에 시퀀스를 올려 자동 인서트(Insert) 처리합니다.\n"
        "* **과거 시점의 계약 검증 및 시계열 리포팅**: 가맹개발 담당자는 이력 조회 화면(`Hq_Esti_00007`)을 통해 가맹 개설 자재비 상승 및 자산 변동 추이를 리포팅받고, 과거 특정일자에 계약된 가맹 점포의 정산 분쟁 발생 시 계약 당시의 유효했던 단가(`estim_aly_prc`)를 대조 검증하기 위해 조회 활용합니다."
    )

    data["tables"]["teshistb"] = {
        "memo": teshistb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "estim_goods_cd": "이력이 기록된 본사 표준 상품/설비/자재 코드 (20자리, PK)",
            "estim_seq": "단가/수량 정보 변경 시 마다 순차 생성되는 일련 시퀀스 번호 (10자리, PK)",
            "estim_type_cd": "점포 규모/평형 구분 등급 코드 (예: 010: 10평, 020: 20평 등)",
            "estim_from_cd": "초도 견적 분류 형태 코드 (예: 01: 주방기기, 02: 인테리어 등)",
            "estim_fr_date": "해당 단가 정보가 과거에 유효했던 시작 일자 (YYYYMMDD)",
            "estim_to_date": "해당 단가 정보가 과거에 유효했던 종료 일자 (YYYYMMDD)",
            "estim_goods_spec": "과거 해당 상품의 본사 마스터 표준 규격 정보 (50자리)",
            "estim_ord_unit": "발주 단위 구분 코드 (공통명칭 NM_FG:121 매핑, 0: 본사, 1: 가맹점 등)",
            "estim_goods_qty": "변경 전 평형 등급 점포에 투입되던 기본 표준 수량 (numeric 13,3)",
            "estim_aly_prc": "과거 해당 시퀀스 당시 적용되었던 공급/매입 단가 (numeric 13,3)",
            "estim_extend_yn": "해당 견적 이력의 유효 기간을 연장 승인했는지 여부 (N: 미연장, Y: 연장)",
            "ins_dtime": "변경 이력이 자동 생성되어 저장된 등록 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "견적 마스터 헤더(TESFRHTB) 또는 상세(TESFRDTB) 정보가 변경/만료될 때 데이터베이스 트리거(TESFRH_T01)에 의해 백그라운드에서 자동 인서트됩니다.",
        "memo_u": "이력용 데이터이므로 보존 일관성을 위해 등록 완료 후 일체의 정보 수정(Update)이 엄격히 불허됩니다.",
        "memo_d": "과거 개설 점포의 회계 감사 및 계약 단가 정합성을 추적하는 법적 증빙 성격이므로 삭제가 영구 차단됩니다.",
        "memo_r": "평형별/자재별 초도 단가 및 수량 변동 이력 조회(Hq_Esti_00007, Hq_Esti_00008), 협력사별 초도 계약 대금 대사(Hq_Vendor_00001, St_Vendor_00001) 시 시점 대조용 이력 테이블로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tesfrdtb",
                "description": "초도 견적 상세 테이블. 본 테이블(TESHISTB)에 변경 이력 데이터를 발생시키고 공급단가(estim_bas_prc -> estim_aly_prc)를 밀어 넣는 직접적인 원천 테이블입니다."
            },
            {
                "table_name": "tesfrhtb",
                "description": "견적 분류 헤더 테이블. [트리거 TESFRH_T01 연동] 견적 조건 변경에 따른 만료 처리 시 이력 저장을 트리거링하는 헤더 마스터 관계입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 이력이 기록된 상품/설비의 한글 제품명, 기본 사양 정보를 매칭 조회하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tcomdctb",
                "description": "협력사 마스터 테이블. 과거 단가 이력 시점 당시의 공급 협력처 명칭과 등급 정보를 조회하기 위해 조인합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점 점포의 과거 개설 일자 기준에 맞물리는 최적의 견적 이력 시퀀스를 역추적하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 과거 개점 시점의 실제 입고 전표상 단가와 TESHISTB에 저장된 역사적 견적 표준 단가를 대사할 때 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 과거 시점의 물류 선입선출 매입가와 초도 견적 이력 단가를 대조하여 당시의 마진율을 복원 추적할 때 간접 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 평형 구분 코드(estim_type_cd), 발주 단위(estim_ord_unit) 및 연장 여부(estim_extend_yn) 한글 라벨 출력을 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 과거 단가 변경을 최종 승인하여 이력 저장을 야기한 조작자 계정을 식별하기 위해 간접 조인 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 초도 견적 단가 변동 로그 최대 보존 년한 및 백업 보존 정책 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 113. TESTYGTB MEMO AND RELATED TABLES
    testygtb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 평수/규모별 필수 강제 소급 원자재/상품 마스터 테이블 (`TESTYGTB`).\n"
        "프랜차이즈 가맹점 신규 개설 시, 매장 평형대 등급(`ESTIM_TYPE_CD`) 및 브랜드 체인(`CHAIN_NO`) 규칙에 근거하여 초도 납품 견적서 상에 반드시 포함되어야 하는 핵심 필수 강제 원재료 및 운영 비품 상품 코드(`ESTIM_GOODS_CD`)를 선별 관리하는 통제 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **초도 견적서 필수 제약 및 밸리데이션**: 가맹개발 담당자가 신규 점포의 초도 견적서 작성/편집 시(`Hq_Esti_00002` 화면), 본 테이블(`TESTYGTB`)에 등재된 필수 원부자재 및 초도 식자재 항목들은 점주 요구 등으로 임의 삭제하거나 견적 단가/수량을 정책상 최소 기준 이하로 하향 보정하는 조작이 프론트/백엔드에서 강력하게 제약됩니다.\n"
        "* **가맹 개설 의무 규정 준수**: 브랜드 계약 상 의무 공급 물품(매뉴얼, 전용 소스류, 본사 지정 초도 유니폼 등)의 납품 누락을 사전에 차단하여 전국 점포의 품질 표준성(Consistency)을 법적으로 보장하는 기준점이 됩니다."
    )

    data["tables"]["testygtb"] = {
        "memo": testygtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "estim_type_cd": "점포 규모/평형 구분 등급 코드 (예: 010: 10평, 020: 20평 등, PK)",
            "estim_goods_cd": "초도 개설 시 강제 소급 납품되는 필수 표준 상품/원자재 코드 (20자리, PK)",
            "ins_dtime": "필수 상품 지정 마스터 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "ins_id": "최초 등록자 ID",
            "upd_dtime": "필수 상품 지정 마스터 최종 변경 수정 일시 (YYYYMMDDHH24MISS)",
            "upd_id": "최종 변경 조작자 ID"
        },
        "memo_c": "가맹 계약 브랜드 법의 개정 및 본사 유통 소싱 정책에 의거하여 가맹개발 마스터 화면(Hq_Esti_00001)에서 수동 등록됩니다.",
        "memo_u": "필수 강제 상품 품목의 단종 또는 대체 원자재 교체 적용 시 마스터 관리 화면 조작에 의해 업데이트됩니다.",
        "memo_d": "전국 가맹점의 브랜드 통일성 및 본사 공급권 보장을 증빙하는 정책 마스터이므로 임의 삭제가 원천 금지됩니다.",
        "memo_r": "평형별 필수 강제 상품 매핑 마스터 관리(Hq_Esti_00001), 초도 견적서 생성 및 품목 편집(Hq_Esti_00002) 화면에서 필수 체크 제약용으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 필수 강제 초도 물품으로 등록된 자재의 표준 과세 유형, 규격, 소포장 가맹점 공급 단가를 매핑 조회하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tesfrdtb",
                "description": "초도 견적 상세 테이블. 본 필수 원재료가 평형별 초도 견적 템플릿상에 수량과 함께 등록되어 있는지 교차 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "tesfrhtb",
                "description": "견적 분류 헤더 테이블. 필수 물품이 속해 있는 대분류(estim_from_cd)가 활성화되어 가맹 개설 적용 기간에 속하는지 체크하기 위해 연동합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 새로 입점하는 가맹점 마스터 등록 시, 해당 점포의 실평수 유형에 누락된 필수 초도 물품이 없는지 WMS 발주 요청 시점에 간접 참조합니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 개설 납품 확정 시 필수 강제 품목이 누락 없이 정상 입고 되었는지 실매입 내역을 감사 대사할 때 조인 참조됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 필수 품목의 선입선출 매입 단가를 비교 분석하여 본사 정산 마진을 추출할 때 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 프랜차이즈 브랜드(체인)별로 의무 취급해야 하는 핵심 식자재의 범위가 다르므로 브랜드 기준으로 코드를 분리 필터링하기 위해 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 평형 구분 코드(estim_type_cd)의 한글 라벨(예: 30평형)을 매핑 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 필수 강제 소급 원재료 마스터를 추가 등록하거나 규칙을 수정한 본사 개발부 담당자 계정을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 개설 시 필수 원재료 단가 강제 보정 및 마진 보전 상한선 기준 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 114. TESTYMTB MEMO AND RELATED TABLES
    testymtb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 평형/규모 유형 구분 코드 기준 마스터 테이블 (`TESTYMTB`).\n"
        "프랜차이즈 가맹 본사 가맹개발실에서 신규 개점 및 매장 계약 설계를 진행할 때 적용할 수 있는 브랜드 체인별(`CHAIN_NO`) 점포 규모 및 평형 타입(평형 구분 코드 `ESTIM_TYPE_CD`, 한글 명칭 `ESTIM_TYPE_KOR_NM`, 영문명, 설명 비고 등)을 규정하는 최상위 평형 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹 설계 조직 체계의 근간**: 가맹개발 화면에서 신규 평형 코드 등록(`Hq_Esti_00001` 화면) 시 본 테이블에 신규 행이 인서트되며, 이는 견적 헤더(`TESFRHTB`), 견적 상세(`TESFRDTB`), 필수 강제 물품(`TESTYGTB`), 가격 변경 이력(`TESHISTB`) 등 가맹점 초도 설비 관련 모든 하위 마스터 테이블들의 `estim_type_cd` 참조 무결성(FK)을 보장하는 부모 테이블이 됩니다.\n"
        "* **가맹점 귀속 매칭**: 각 개별 가맹점 점포 마스터(`MMEMBSTB`)는 점포 개점 계약 내용에 기재된 실평수 및 설계 면적을 기준으로 본 테이블의 평형 코드를 귀속 매칭하여 초도 수주/발주 출고 대상 품목의 기준 앵커로 활용합니다."
    )

    data["tables"]["testymtb"] = {
        "memo": testymtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "estim_type_cd": "점포 규모/평형 구분 고유 코드 (예: 010: 10평, 020: 20평 등, PK)",
            "estim_type_kor_nm": "해당 평형 등급의 한글 공식 명칭 (예: 20평형 복층식, 30평형 카운터형)",
            "estim_type_eng_nm": "해당 평형 등급의 공식 영문 명칭",
            "estim_type_etc_nm": "해당 평형 등급에 대한 기타 추가 명칭 분류",
            "estim_bigo": "평형 설계 기준 및 특이사항에 대한 상세 설명 비고 (4000자)",
            "ins_dtime": "평형 마스터 코드 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "ins_id": "최초 등록자 ID",
            "upd_dtime": "평형 마스터 코드 최종 변경 수정 일시 (YYYYMMDDHH24MISS)",
            "upd_id": "최종 변경 조작자 ID"
        },
        "memo_c": "브랜드 기획 부서 및 영업 개발 본부에서 새로운 규격의 점포 타입을 신설할 때 어드민 화면(Hq_Esti_00001)에서 수동 인서트합니다.",
        "memo_u": "점포 평형 한글/영문 명칭 변경이나 비고 보정 시 마스터 화면 조작에 의해 업데이트됩니다.",
        "memo_d": "하위 초도 견적서(Header, Detail, required goods, history) 및 가맹점 마스터(MMEMBSTB)의 물리적 기준선이므로 삭제가 엄격히 제한됩니다.",
        "memo_r": "평형별 필수 강제 상품 매핑 관리(Hq_Esti_00001), 평형별 초도 물품 표준 설정(Hq_Esti_00002), 신규 점포 개설 견적서 생성(Hq_Esti_00003), 백오피스 공통 모듈 GoodsClass 검색 시 콤보박스 바인딩용 마스터로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tesfrhtb",
                "description": "견적 분류 헤더 테이블. 특정 평형 유형에 속하는 견적서 세부 버전을 구성하기 위해 1:N으로 연결되는 직접적인 마스터-디테일 관계입니다."
            },
            {
                "table_name": "tesfrdtb",
                "description": "초도 견적 상세 테이블. 특정 평형 규모에 투입되어야 하는 개별 주방 기기 및 식자재 품목들의 기준량을 묶어주는 외래키 관계입니다."
            },
            {
                "table_name": "tesfrvtb",
                "description": "공급처 매핑 테이블. 평형별 분류에 할당되는 최종 협력 공급사 정보를 관리하기 위한 연계 관계입니다."
            },
            {
                "table_name": "testygtb",
                "description": "필수 강제 품목 테이블. 특정 평형 규모의 가맹점 개설 시 무조건 포함시켜야 하는 강제 품목 규칙을 정의하기 위한 1:N 매핑 관계입니다."
            },
            {
                "table_name": "teshistb",
                "description": "단가 변경 이력 테이블. 과거 특정 평형 규모에 할당되었던 물품들의 가격 변동 히스토리를 대사하기 위한 관계입니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 평형 등급이 어떤 브랜드 사업부(예: 카페 vs 베이커리)에 적용되는 조직 기준선인지 조인 식별하기 위해 사용됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점의 실평수와 계약 매장 규모에 따라 어떤 평형 코드(estim_type_cd)가 귀속되어 영업을 개시했는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 평형별로 초도 공급 완료된 실제 자재비 총액과 본 표준 유형의 예상 견적가를 대조하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 가맹 브랜드별 신규 평형 코드를 생성 및 수정 등록한 가맹개발 부서 담당자의 계정 정보를 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 평형 규모별로 다르게 책정될 수 있는 점포 보증금 및 물류 긴급배송료 기준 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 115. TESVDUTB MEMO AND RELATED TABLES
    tesvdutb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 초도 물품 공급 협력사별 품목 단가 제안 상세 테이블 (`TESVDUTB`).\n"
        "프랜차이즈 가맹점 평형별 초도 물품 견적과 관련하여, 지정된 공급 협력사별(`ESTIM_VENDOR`)로 각 개별 상세 자재 품목(`ESTIM_GOODS_CD`)에 대한 본사 표준 단가(`ESTIM_BAS_PRC`), 협력사 최초 제안 단가(`ESTIM_SUG_PRC`), 최종 합의 확정 단가(`ESTIM_ALY_PRC`), 그리고 본사 단가 적용 승인 여부(`ESTIM_PRC_APPLY_YN`)를 관리하는 단가 절충 상세 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **공급가 협상 및 최종 컨펌 프로세스**: 협력업체별 제안 단가 화면(`Hq_Esti_00005`)에 협력사의 수동 견적 제안금(`estim_sug_prc`)이 입력된 뒤, 본사 승인 화면(`Hq_Esti_00006`)을 통해 본사 조율자가 최종 네고 단가(`estim_aly_prc`)를 확정 짓고 적용 여부 플래그(`estim_prc_apply_yn`)를 `Y`로 변경 승인하면, 이 확정 단가가 가맹점 개설 정산 단가 및 물류 발주 단가로 최종 공표됩니다.\n"
        "* **트리거 및 이력 적재 연동 (`TESFRV_T01` 등)**: 본 테이블의 최종 확정 단가가 수정 적용되는 시점에 `TESFRH_T01` 트리거가 유기적으로 작동하여, 단가 변동 변곡점의 이전 스냅샷을 이력 테이블(`TESHISTB`)에 히스토리로 기록함으로써 납품 단가의 투명성을 보장합니다."
    )

    data["tables"]["tesvdutb"] = {
        "memo": tesvdutb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "estim_type_cd": "점포 규모/평형 구분 등급 코드 (예: 010: 10평, 020: 20평 등, PK)",
            "estim_from_cd": "초도 견적 분류 형태 코드 (예: 01: 주방기기, 02: 인테리어 등, PK)",
            "estim_vendor": "해당 품목의 제안 단가를 제출한 협력 공급사 코드 (TCOMDCTB의 COMP_CD, PK)",
            "estim_goods_cd": "견적 대상 본사 표준 상품/설비/자재 코드 (20자리, PK)",
            "estim_goods_spec": "제안 상품의 제조사 규격 사양 (50자리)",
            "estim_ord_unit": "발주 단위 구분 코드 (공통명칭 NM_FG:121 매핑, 0: 본사, 1: 가맹점 등)",
            "estim_goods_qty": "해당 평형 등급에 투입되도록 합의된 표준 수량 (numeric 13,3)",
            "estim_bas_prc": "본사 기준 표준 개설 가액 (수정 불가 기준 단가, default 0)",
            "estim_sug_prc": "협력 공급사에서 최초 또는 조율 시 제안한 공급 제안가 (default 0)",
            "estim_aly_prc": "본사 검토자와 협력사가 네고 합의하여 최종 확정한 공급단가 (default 0)",
            "estim_prc_apply_yn": "최종 확정 공급 단가 사용 승인 여부 (N: 미적용/조율중, Y: 사용승인완료)",
            "ins_dtime": "제안 단가 상세 정보 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "ins_id": "최초 등록자 ID",
            "upd_dtime": "제안 단가 상세 정보 최종 승인/수정 일시 (YYYYMMDDHH24MISS)",
            "upd_id": "최종 승인/수정 조작자 ID"
        },
        "memo_c": "초도 견적 분류별 공급사 매핑(TESFRVTB) 정보가 생성될 때 품목 세부 제안서 작성을 위해 자동으로 복사 인서트됩니다.",
        "memo_u": "협력사 제안가 접수(Hq_Esti_00005) 및 본사 최종 확정 단가 합의 승인 처리(Hq_Esti_00006) 시 업데이트됩니다.",
        "memo_d": "가맹점 개설 납품 거래의 단가 변동 절충 과정을 입증하는 법적 증빙 상세 내역이므로 임의 삭제가 금지됩니다.",
        "memo_r": "협력업체별 제안 단가 입력(Hq_Esti_00005), 단가 제안 최종 검토 및 적용 승인(Hq_Esti_00006), 평형별 변동 단가 이력 조회(Hq_Esti_00007), 협력사 초도 대금 대사 및 정산(Hq_Vendor_00001, St_Vendor_00001) 시 코어 단가 조대 테이블로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tcomdctb",
                "description": "협력사 마스터 테이블. 제안 단가를 제공한 주체인 협력사 대표 코드와 공식 거래처명을 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tesfrvtb",
                "description": "공급처 매핑 테이블. 제안 단가 의뢰 메일 발송 플래그(estim_send_yn) 및 최종 합의 플래그(estim_sugg_yn)를 교차 대사하기 위해 1:N으로 연결되는 직접적인 부모 관계입니다."
            },
            {
                "table_name": "tesfrdtb",
                "description": "초도 견적 상세 테이블. 제안 대상 품목의 기준 요구 수량(estim_goods_qty) 및 본사 기준 공급단가를 확인하기 위해 조인되는 대상입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 제안된 설비 및 원재료의 규격, 한글 상품명, 대표 단가 속성을 대조 식별하기 위해 조인됩니다."
            },
            {
                "table_name": "teshistb",
                "description": "단가 변경 이력 테이블. 협력사 제안 단가가 수락 및 최종 적용(estim_prc_apply_yn = 'Y') 처리될 때, 과거 차수 이력을 아카이빙하기 위해 간접 조인 연동됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드별로 최적의 제안 단가 조율 권한 범위 및 부가세 계산 로직을 규정하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 신규 매장에 투입되는 자재비 정산 시, 본 테이블의 협상 확정 단가(estim_aly_prc)를 대입하여 개설 공급 청구서를 자동 발행할 때 참조됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 계약 마감 후 물류 시스템(WMS)으로 넘어간 설비 발품의 실제 매입 계약 단가와 본 제안 협상 단가의 일치 여부를 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 협력사 입고 당시의 선입선출 원가를 대조하여 최종 승인할 매입 단가의 한도를 내부 검증할 때 간접 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 단가 적용 여부(estim_prc_apply_yn) 및 발주 단위(estim_ord_unit, 121) 한글 명칭 출력을 위해 사용됩니다."
            }
        ]
    }

    # 116. TGOODSTB MEMO AND RELATED TABLES
    tgoodstb_memo = (
        "### 1. 테이블 개요\n"
        "본사 기준 전체 상품 마스터 테이블 (`TGOODSTB`).\n"
        "프랜차이즈 가맹 본사에서 유통, 판매, 관리하는 모든 자재, 원부재료, 비품, 설비 및 최종 가맹점 메뉴 상품의 기준 정보(상품코드 `GOODS_CD`, 상품명 `GOODS_NM`, 원가 `UCOST`, 공급가 `USUPRICE`, 과세구분 `TAX_FG` 등)를 정의하고 통제하는 전사 최상위 상품 기준 정보 카탈로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **전사 유통/판매 프로세스의 기점**: 본사 ERP 상품 원장 정보가 동기화 배치 또는 실시간 수신 모듈(`SUB_MASTER_P`)을 거쳐 `TGOODSTB`로 정기 이관/반영됩니다. 가맹점 상품 원장(`MGOODSTB`)은 본 테이블의 자식 테이블로서 점포별 맞춤 가격 및 노출 여부를 오버라이드하여 POS 판매에 적용합니다.\n"
        "* **재고 및 레시피 차감 통제**: 매출 발생 시 레시피 전개 프로시저(`SUB_SL_RECIPE_GOODS_P`)가 `TGOODSTB`의 레시피 코드(`recipe_cd`) 및 원부자재 과세 속성을 조회하여 이론 원재료 소요량을 뽑아내고 매장 현재고를 감산합니다. 또한 본사/가맹점 월말 총평균 수불 정산 배치(`SUB_TOT_AVG_P`) 구동 시 기초단가 및 월말 자산 평가액의 근간이 됩니다."
    )

    data["tables"]["tgoodstb"] = {
        "memo": tgoodstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "goods_cd": "본사 기준 고유 상품/자재/메뉴 코드 (20자리, PK)",
            "goods_nm": "공식 국문 상품 명칭 (120자리)",
            "goods_sub_nm": "상품 영문명 또는 보조 약식 명칭 (30자리)",
            "goods_spec": "상품 기본 포장 및 유통 단위 규격 (20자리)",
            "lclass_cd": "상품 대분류 코드 (4자리)",
            "mclass_cd": "상품 중분류 코드 (4자리)",
            "sclass_cd": "상품 소분류 코드 (4자리)",
            "uprice": "가맹점 최종 권장 소비자가/판매가 (default 0)",
            "usuprice": "본사에서 가맹점으로 출고하는 식자재 공급단가 (default 0)",
            "ucost": "본사가 협력사로부터 매입하는 최초 매입 원가 (default 0)",
            "vat_rate": "해당 상품의 부가세 요율 (%)",
            "tax_fg": "과세 여부 구분 코드 (0: 면세, 1: 과세, default '1')",
            "goods_price_fg": "가격 책정 형태 구분 (0: PLU 고정가, 1: NON-PLU 중량가 등)",
            "goods_control_fg": "수불 재고 통제 여부 (0: 미통제, 1: WMS 수량 감산 통제 대상)",
            "use_fg": "상품 사용 용도 분류 (0: 전체사용, 1: 판매전용, 2: 자재전용)",
            "set_fg": "세트 메뉴 성격 구분 플래그 (0: 일반상품, 1: 세트구성단품, 2: 원재료, 3: 세트메인상품)",
            "ord_unit": "발주 단위 구분 코드 (공통명칭 121 매핑, 0: 박스, 1: 낱개 등)",
            "in_qty": "유통 포장 상자 내 낱개 입수량 (default 1)",
            "inv_unit": "창고 재고 관리용 단위 구분 코드 (공통명칭 122 매핑)",
            "inv_in_qty": "재고 단위 환산 시의 입수 환산 계수 (default 1)",
            "goods_unit": "대표 상품 거래 기본 단위 수량 (default 1)",
            "min_ord_qty": "가맹점 발주 시 최소 주문 제한 수량 (default 1)",
            "safety_qty": "본사 창고의 안전 재고 유지 수량 (default 0)",
            "stage_goods_fg": "상품의 단종/단절 관리 상태 (0: 정상유통, 1: 유통중단)",
            "goods_use_fg": "상품의 웹/POS 전반 사용 여부 상태 (0: 사용중, 1: 사용중단)",
            "recipe_cd": "메뉴 조리에 연결되는 레시피 마스터 코드 (TB_RECIPE 연계)",
            "erp_goods_cd": "ERP 시스템 내의 매핑 상품 코드 (20자리)",
            "join_vendor": "해당 품목을 대표 매입하는 주 협력 공급사 코드 (TCOMDCTB의 COMP_CD 연계)",
            "product_standard": "상품의 물류/제조사 상세 표준 규격 (50자리)",
            "store_stock_yn": "매장에서 독자적으로 수급 및 재고를 관리하는 품목인지 여부 (Y/N)",
            "store_stock_ucost": "매장 자체 관리 품목의 개별 매입 원가"
        },
        "memo_c": "본사 ERP 상품 신설 데이터가 연동 배치 전문(SUB_MASTER_P)을 거쳐 신규 자동 인서트됩니다.",
        "memo_u": "ERP 단가 및 세무 속성 변동 전문 수신 또는 어드민 상품 수정 및 트리거(TGOODS_T01) 구동에 의해 업데이트됩니다.",
        "memo_d": "매장 매출 분해, 수불 정산 원장, 매입 발주 이력의 근본 마스터이므로 물리적 삭제가 전면 금지됩니다.",
        "memo_r": "본사 수불 배치(SUB_TOT_AVG_P), 가맹점 레시피 소요량 감산(SUB_RECIPE_IO_P), 세트 분해(SUB_SL_SET_GOODS_P), 초도 자재 셋업(Hq_Esti_00002) 등 전사 판매/재고/계약 쿼리에서 필수 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 본사 표준 상품 정보를 바탕으로 각 매장별 판매 가능 여부(use_fg), 점포 개별 변경 단가를 추가 정의하기 위한 1:1 대응 원장 관계입니다."
            },
            {
                "table_name": "tb_recipe",
                "description": "레시피 마스터 테이블. 판매 상품과 매핑된 조리용 레시피 원부를 1:1로 결합하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tb_recipe_goods",
                "description": "레시피 구성 자재 상세 테이블. 레시피 하위의 개별 소요 자재 품목(원자재, 부자재)의 상품 규격과 단가를 대조 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "tb_set_goods",
                "description": "세트 구성 테이블. 세트 메뉴에 속하는 개별 단품들의 공급 단가와 구성 분해 비율을 확인하기 위해 매치됩니다."
            },
            {
                "table_name": "obslpdtb",
                "description": "매입/발주 상세 테이블. 가맹점 및 본사가 입고 발주 처리한 개별 품목의 상품명, 입수량, 과세 구분을 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "stckhitb",
                "description": "선입선출 입고대장 테이블. 품목별로 입고된 자재의 선입선출 매입가 정합성을 검증하기 위한 직접 조인 관계입니다."
            },
            {
                "table_name": "tb_tot_avg_cost",
                "description": "본사 상품 월별 수불 및 월말 총평균 재고 자산 평가/원가 집계. 본사/체인 기준 상품별 기말 수불 및 총평균 자산 평가액을 정산하기 위해 조인됩니다."
            },
            {
                "table_name": "tb_immmio_cost",
                "description": "가맹점 상품 월별 수불 및 월말 총평균 재고 자산 평가/원가 집계. 가맹점별 상품 수불 대장을 월 정산 대사하기 위해 직접 조인 연계됩니다."
            },
            {
                "table_name": "tesfrdtb",
                "description": "초도 견적 자재 테이블. 신점 개설용 평형별 설비 및 자재 사양의 본사 표준 규격 정보를 맵핑하기 위해 조인됩니다."
            },
            {
                "table_name": "tcomdctb",
                "description": "협력사 마스터 테이블. 개별 원자재 상품의 대표 공급처 상호명 및 소싱 기업 명칭을 조회하기 위해 조인됩니다."
            }
        ]
    }

    # 117. TIFEMPTB MEMO AND RELATED TABLES
    tifemptb_memo = (
        "### 1. 테이블 개요\n"
        "ERP 수신 임직원 인사 원장 연동 인터페이스 테이블 (`TIFEMPTB`).\n"
        "본사 ERP 시스템으로부터 프랜차이즈 본사의 전사 사원/임직원 인사 변동 원장 내역을 전송받는 텔렉스 실시간 수신 전용 인터페이스 테이블(사원번호 `EE_NO`, 성명 `EE_NM`, 회사코드 `COMP_CD`, 부서코드 `DEPT_CD`, 직급/직책 및 재직구분 `USE_YN` 등)입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **인사 정보 실시간 수신 버퍼**: ERP 인사 마스터에 신규 입사 또는 인사 발령이 가해지면, 실시간 인터페이스 전문(`IF_FB_303` 전문)을 통해 텔렉스 통신 모듈(`P03_SqlMapper`)을 거쳐 본 테이블(`TIFEMPTB`)로 변동 내역이 즉각 인서트/업데이트됩니다.\n"
        "* **사원 마스터 이관 및 계정 권한 동기화**: 임직원 동기화 배치(`EmpInterface`)가 작동하여 본 인터페이스 수신 테이블의 사원 원장 데이터를 본사 사원 마스터 테이블(`TBE_EMP_INF`)로 정합성 검증 후 이관하며, 사용 구분(`use_yn`)이 퇴사('N') 등으로 변경된 경우 사용자 계정 테이블(`MUSERSTB`)의 로그인 상태를 즉각 차단(Lock) 처리합니다."
    )

    data["tables"]["tifemptb"] = {
        "memo": tifemptb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "comp_cd": "ERP 시스템에서 부여된 소속 법인 회사 코드 (4자리, PK)",
            "ee_no": "ERP 공식 사원번호/임직원 번호 (16자리, PK)",
            "ee_nm": "사원의 공식 한글 성명 (100자리)",
            "comp_nm": "소속 법인의 상호 명칭 (100자리)",
            "dept_cd": "소속 부서 코드 (16자리)",
            "dept_nm": "소속 부서 한글 명칭 (100자리)",
            "job_pos_cd": "직급 코드 (16자리)",
            "job_pos_nm": "직급 명칭 (예: 대리, 과장, 부장 등)",
            "job_rsp_cd": "직책 코드 (16자리)",
            "job_rsp_nm": "직책 명칭 (예: 팀장, 본부장, 점장 등)",
            "use_yn": "임직원 재직 상태 및 사용 여부 플래그 (Y: 재직, N: 휴직/퇴사)",
            "area_cd": "사원이 근무 소속된 리전/지역 코드 (20자리)",
            "create_id": "최초 연동 데이터를 적재한 생성자 ID (시스템 수신 코드)",
            "create_dtime": "연동 데이터 최초 적재 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 정보 변동을 기록한 수정자 ID",
            "last_dtime": "최종 정보 변동 수정 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "ERP 임직원 실시간 변동 수신 전문(IF_FB_303) 수신 시 텔렉스 Mapper(P03_SqlMapper)를 통해 자동으로 인서트됩니다.",
        "memo_u": "부서 이동, 직급 승진, 퇴사 처리 등 ERP 인사 정보 변동이 전송될 때 실시간 업데이트됩니다.",
        "memo_d": "백오피스 계정 권한 락킹 및 사원 정보 이관 대사의 원천 통신 버퍼 데이터이므로 임의 삭제가 영구 차단됩니다.",
        "memo_r": "임직원 정보 연동 배치(EmpInterface), 모바일 인증용 사원 검색(EMP_SqlMapper), 텔렉스 수신 Mapper(P03_SqlMapper) 및 백오피스 로그인 세션 유효성 검증 시 버퍼 테이블로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tbe_emp_inf",
                "description": "본사 사원 마스터 테이블. ERP 수신 연동 사원 원장(TIFEMPTB)으로부터 가공 정제된 정식 백오피스 임직원 데이터를 1:1 동기화 적재하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. ERP에서 신규 인사 등록이 수신되면, 백오피스에 로그인할 수 있는 임직원용 전용 웹 계정을 자동으로 생성 및 활성화 상태(use_yn)를 제어하기 위해 조인됩니다."
            },
            {
                "table_name": "tdeptmtb",
                "description": "부서 마스터 테이블. 수신된 사원의 소속 부서명이 HMS 내부 부서 체계에 일치하는지 데이터 유효성을 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 점포에 발령받아 신규 부임한 가맹점주 또는 현장 관리자인지 점포 근무지와 사원 정보 간의 연결 관계를 대조하기 위해 조인됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 직급(job_pos_cd), 직책(job_rsp_cd) 및 근무 지역(area_cd)의 한글 구분 라벨 출력을 위해 사용됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. IF_FB_303 임직원 수신 전문 통신 오류 발생 시 수신 패킷과 에러 메시지를 보관 및 관제하기 위해 간접 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. ERP 인사 정보 동기화 배치 실행 주기 및 자동 계정 생성 권한 그룹 템플릿 매개 변수를 매칭 참조합니다."
            }
        ]
    }

    # 118. TKTFDCTB MEMO AND RELATED TABLES
    tktfdctb_memo = (
        "### 1. 테이블 개요\n"
        "통신사 제휴 할인 제어 및 대상 상품 할인율 마스터 테이블 (`TKTFDCTB`).\n"
        "가맹점 POS 단말기에서 통신사 멤버십 제휴 카드(예: SKT T-Membership, KT 멤버십, LGU+ 멤버십)를 통해 결제 시 할인 혜택을 제공받을 수 있는 대상 상품 코드(`GOODS_CD`), 소속 통신사 코드(`KTF_CD`), 할인율(`DC_RATE`), 그리고 금액 단수 절사/반올림 기준(`ROUND_FG`) 등의 정책을 프랜차이즈 브랜드 사업부별(`CHAIN_NO`)로 설정 및 통제하는 제휴 프로모션 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 제휴 할인 적용의 기준**: 고객이 POS에서 결제 단계 시 통신사 카드를 리딩하면, POS 시스템은 본 할인 정책 데이터를 참조하여 해당 매장 판매 상품이 할인 적용 대상 품목인지 검증하고, 규정된 제휴 할인율(`dc_rate`)과 올림/버림/반올림 방식(`round_fg`)에 따라 할인 적용 금액을 즉각 계산하여 매출에 반영합니다.\n"
        "* **실시간 마스터 변경 및 POS 배포 연계 (`TKTFDC_T01` 트리거)**: 본사의 마케팅/영업 관리 화면(`Hq_Master_00018`)에서 제휴 카드 할인율이나 프로모션 대상 품목을 변경 등록 또는 삭제하는 순간, 데이터베이스 트리거 `TKTFDC_T01`이 자동으로 발화하여 관련 변동 정보를 매장 POS 연동 배포 대기열(`TMCPLK_T01` 등 연계)에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포합니다."
    )

    data["tables"]["tktfdctb"] = {
        "memo": tktfdctb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "ktf_cd": "제휴 통신사 식별 코드 (공통명칭 021 매핑, 예: KT, SKT, LGT 등, PK)",
            "goods_cd": "제휴 할인 대상 본사 표준 상품/메뉴 코드 (20자리, PK)",
            "dc_rate": "해당 상품에 적용될 통신사 제휴 할인 비율 (numeric 5,2, 예: 10.00 = 10%)",
            "round_fg": "할인 적용 가격 계산 시 절사/올림 적용 기준 구분 코드 (0: 반올림, 1: 버림, 2: 올림)",
            "create_dtime": "제휴 할인 대상 정책 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 마케팅 담당자)",
            "last_dtime": "제휴 할인 대상 정책 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID"
        },
        "memo_c": "ERP 제휴 프로모션 연동 전문 수신(SUB_MASTER_P) 또는 본사 마스터 제휴 카드 상품 관리 화면(Hq_Master_00018)에서 신규 프로모션 세팅 시 수동 등록됩니다.",
        "memo_u": "할인율 변동 또는 금액 계산 절차(round_fg) 변경 적용 시 마스터 관리 화면 및 트리거(TGOODS_T01, TKTFDC_T01)를 거쳐 실시간 업데이트됩니다.",
        "memo_d": "과거 가맹점 통신사 할인 매출 정산 및 제휴 수수료 대사 정합성을 입증하기 위한 세무용 기준 마스터이므로 임의 삭제가 금지됩니다.",
        "memo_r": "제휴 통신사별 상품 할인율 설정(Hq_Master_00018), 가맹점 POS 매출 결제 시 통신사 할인 밸리데이션 검사, 제휴 할인 전송 이벤트(TKTFDC_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 할인율 검증용으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 제휴 할인 대상 품목의 판매 단가(uprice)와 면과세 속성을 매칭하여 최종 제휴 카드 할인액(DC Amount)을 POS가 계산할 때 기준이 되는 상품 마스터입니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드 사업부별로 제휴를 맺은 통신사 할인 프로모션 카드가 다르게 노출되도록 제어하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 통신사 구분 코드(ktf_cd, 예: KT, SKT, LGT) 명칭 및 금액 반올림/절사 처리 유형(round_fg) 한글 라벨을 바인딩하기 위해 사용됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 특정 점포가 속해 있는 지자체 특수 규정 등으로 제휴 할인이 차단된 개별 상품 예외 규칙을 POS에서 판별하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 제휴 할인 매칭 POS 이벤트 발생 시, 해당 점포의 통신사 카드 리더기 연동 가부 매개 변수를 체크하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 단말기에서 통신사 멤버십 한도 부족 또는 통신 차단 에러 시 적재되는 실시간 로그 및 POS 배포 이력을 모니터링하기 위해 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 제휴 할인 적용 한도(일별/회당 최대 할인 금액) 및 통신 장애 시 오프라인 자동 할인 허용 여부 변수를 매칭 참조합니다."
            }
        ]
    }

    # 119. TKTFRTTB MEMO AND RELATED TABLES
    tktfrttb_memo = (
        "### 1. 테이블 개요\n"
        "통신사 제휴 카드 프로모션 기본 정책 마스터 테이블 (`TKTFRTTB`).\n"
        "프랜차이즈 가맹 본사와 통신사(예: KT, SKT, LGU+) 간의 멤버십 제휴 할인 계약에 따라 결제 시 적용되는 마스터 프로모션 정책(통신사 부담율 `KTF_RATE`, 프로모션명 `PROMOTION_NM`, 적용 시작/종료일, 상품 분류 방식 `GOOD_PROC_FG`, 전체 할인율 `DC_RATE`, 정액할인액 `DC_AMT`, 1회 할인한도 `RIST_DC_AMT`, 절사 방식 `ROUND_FG`, 본사 및 점포 부담 정산 방식 `APPR_FG` 등)을 체인별(`CHAIN_NO`)로 등록 관리하는 최상위 프로모션 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **제휴 결제 및 정산의 모체**: 가맹점 POS에서 멤버십 카드를 승인 처리할 때 결제 조건 밸리데이션(유효 기간, 1회 할인 한도 `rist_dc_amt`)을 검증하는 앵커 마스터 역할을 수행합니다. 또한 월말 본사/가맹점/통신사 간의 제휴 카드 수수료 대사 정산 리포트(`Hq_Sales_00016`) 작성 시 통신사 정납 요율(`ktf_rate`) 및 분담 방식(`appr_fg`)에 따라 정산 결제 보고서를 산출합니다.\n"
        "* **할인 대상 품목 필터링 및 실시간 배포 (`TKTFRT_T01` 트리거)**: 상품 분류 방식(`good_proc_fg`)이 특정 지정 상품 대상('1')일 경우, 하위 상세 마스터 테이블(`TKTFDCTB`)에 매핑된 품목에만 개별 할인율을 적용하도록 결제 로직이 필터링 작동합니다. 본 테이블 정보가 수정 등록 및 삭제되는 시점에 `TKTFRT_T01` 트리거가 실행되어, 해당 할인 정책 파일을 실시간 패키징하여 매장 POS 단말기로 전송 다운로드 이벤트를 배포합니다."
    )

    data["tables"]["tktfrttb"] = {
        "memo": tktfrttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "ktf_cd": "제휴 통신사 식별 코드 (공통명칭 021 매핑, 예: KT, SKT, LGT 등, PK)",
            "ktf_rate": "통신사에서 제휴 계약에 따라 본사에 부과하는 수수료/부담 요율 (numeric 11,2)",
            "ktf_tax_fg": "통신사 부과 수수료 세무 구분 플래그 (0: 면세 수수료, 1: 과세 수수료)",
            "promotion_nm": "통신사 제휴 프로모션 행사 명칭 (30자리)",
            "valid_from_date": "제휴 프로모션 행사 유효 적용 시작 일자 (YYYYMMDD)",
            "valid_to_date": "제휴 프로모션 행사 유효 적용 종료 일자 (YYYYMMDD)",
            "good_proc_fg": "프로모션 할인 적용 대상 상품 필터링 방식 (0: 전상품 일괄 할인, 1: 특정 지정 상품 한정 할인)",
            "dc_rate": "전상품 대상 일괄 할인 적용 시의 기본 할인율 (numeric 5,2, 예: 10.00 = 10%)",
            "rist_dc_amt": "제휴 결제 1회/1일당 최대 적용 가능한 제휴 할인 적용 한도 금액 (0: 한도 없음)",
            "round_fg": "할인 적용 가격 계산 시 절사/올림 적용 기준 구분 코드 (0: 반올림, 1: 버림, 2: 올림)",
            "appr_fg": "프로모션 수수료 정산 분담 주체 플래그 (0: 가맹점 전액 부담, 1: 통신사 및 본사 분담 정산)",
            "appr_corp_cd": "정산금 지급 및 청구 업무를 대행하는 통신 대행사 회사 코드 (4자리)",
            "promotion_etc": "프로모션 적용 예외 조건 및 특이사항 상세 비고 (500자)",
            "create_dtime": "제휴 프로모션 기본 정책 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 마케팅 담당자)",
            "last_dtime": "제휴 프로모션 기본 정책 최종 변경 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 변경 조작자 ID",
            "dc_amt": "정율이 아닌 고정 금액 할인 적용 시의 기본 할인 금액 (default 0)"
        },
        "memo_c": "ERP 제휴 정보 동기화 전문 수신(SUB_MASTER_P) 또는 본사 마스터 제휴 카드 정책 화면(Hq_Master_00018)에서 신규 제휴 계약 체결 시 등록됩니다.",
        "memo_u": "프로모션 적용 기간 변경, 요율 개정 또는 어드민 관리자 편집 및 트리거(TKTFRT_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "가맹점 제휴 카드 결제 정산 보고 및 통신사 제수수료 대사의 역사적 정합성을 대사해야 하므로 임의 삭제가 금지됩니다.",
        "memo_r": "제휴 통신사별 상품 할인 설정(Hq_Master_00018), 통신사 제휴 할인 정산/대사(Hq_Sales_00016, St_Sales_00016) 보고서, POS 결제 할인 밸리데이션 검사, 제휴 프로모션 전송 이벤트(TKTFRT_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tktfdctb",
                "description": "상품 제휴 할인 테이블. [직접적인 1:N 자식 관계] 특정 제휴 프로모션(TKTFRTTB)의 할인 적용 대상이 특정 상품으로 제한될 때(good_proc_fg = '1'), 해당 프로모션에 포함되는 개별 상품군과 할인율 명세를 담고 있는 테이블입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. 제휴 할인 금액 계산 시 상품 판매 가격과 면과세 속성을 매칭하여 최종 제휴 카드 할인액(DC Amount)을 POS가 계산할 때 기준이 되는 상품 마스터입니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드 사업부별로 제휴를 맺은 통신사 할인 프로모션 카드가 다르게 노출되도록 제어하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 통신사 구분 코드(ktf_cd, 예: KT, SKT, LGT) 명칭, 상품 분류 처리 방식(good_proc_fg), 금액 반올림/절사 처리 유형(round_fg) 한글 라벨을 바인딩하기 위해 사용됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 특정 점포가 속해 있는 지자체 특수 규정 등으로 제휴 할인이 차단된 개별 상품 예외 규칙을 POS에서 판별하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 제휴 할인 매칭 POS 이벤트 발생 시, 해당 점포의 통신사 카드 리더기 연동 가부 매개 변수를 체크하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 단말기에서 통신사 멤버십 한도 부족 또는 통신 차단 에러 시 적재되는 실시간 로그 및 POS 배포 이력을 모니터링하기 위해 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 제휴 할인 적용 한도(일별/회당 최대 할인 금액) 및 통신 장애 시 오프라인 자동 할인 허용 여부 변수를 매칭 참조합니다."
            }
        ]
    }

    # 120. TMACNCTB MEMO AND RELATED TABLES
    tmacnctb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 입금/출금 수수료 및 거래 계정 과목 구분 마스터 테이블 (`TMACNCTB`).\n"
        "프랜차이즈 가맹 본사 재무/자금팀에서 개별 가맹점을 대상으로 발생하는 수납 및 출금 거래 전표를 수동 등록할 때 적용하는 자금 계정 분류 정책(체인구분 `CHAIN_NO`, 계정 구분 코드 `ACNT_FG` [0: 입금, 1: 출금], 계정 명칭 `ACNT_NM` [가맹비, 계약보증금, 물류비상환 등])을 브랜드 체인별로 설정 관리하는 계정 과목 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹점 임의 입출금 거래 분류의 앵커**: 가맹 본사에서 특정 점포의 계약 보증금 수납이나 인테리어 잔금 납부 처리(`Hq_Cash_00004` 및 `Hq_Cash_00005` 화면) 시, 본 마스터 테이블의 계정 과목 명칭(`acnt_nm`)을 조회 바인딩하여 전표 데이터의 분류 정확성을 보장합니다.\n"
        "* **배포 및 연동 자동화 (`TMACNC_T01` 트리거)**: ERP 자금 시스템 또는 본사 백오피스를 통해 신규 수납용 계정 과목이 등록/수정/삭제되면, `TMACNC_T01` 트리거가 실행되어 변동 마스터 패키지를 가맹점 POS 배포 대기열(`TMCPLK_T01` 등 연계)에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포합니다."
    )

    data["tables"]["tmacnctb"] = {
        "memo": tmacnctb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "acnt_fg": "입금/출금 수납 거래 계정 구분 코드 (0: 입금/수납, 1: 출금/차감, PK)",
            "acnt_nm": "가맹점 입출금 계정 과목 상세 한글 명칭 (20자리, 예: 계약보증금, 로열티, 물류비상환 등)",
            "create_dtime": "계정 과목 마스터 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 자금 담당자)",
            "last_dtime": "계정 과목 마스터 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID"
        },
        "memo_c": "ERP 자금 과목 연동 전문 수신(SUB_MASTER_P) 또는 본사 자금 마스터 관리 화면에서 신규 전표 과목 신설 시 등록됩니다.",
        "memo_u": "계정 과목 명칭 보정이나 신규 코드 추가 및 트리거(TMACNC_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "가맹점 수납 전표와 수수료 대사의 원천 회계 계정이므로 과거 자산 정산 추적을 위해 임의 삭제가 금지됩니다.",
        "memo_r": "가맹점 자금 입금/수납 등록(Hq_Cash_00004), 가맹점 임의 출금/차감 등록(Hq_Cash_00005), POS 수납 전표 전송 이벤트(TMACNC_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 계정 과목 대조용으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "ttrans_cash_list",
                "description": "자금 거래 상세 원장. [직접적인 자식 관계] 가맹점별로 발생하는 입금(가맹비, 보증금 등) 및 출금(로열티, 비품 청구 등) 거래 내역이 어떤 계정 과목으로 수납되었는지 계정 명칭을 대조 조회하기 위해 1:N으로 조인 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드별로 회계상 관리하는 자금 계정 과목 체계(예: 커피 브랜드 vs 도넛 브랜드)를 분리 정의하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 자금 거래가 기록된 가맹점의 브랜드 체인코드가 본 계정 마스터의 유효 범위에 속하는지 체크하기 위해 연동됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 입출금 구분 코드(acnt_fg, 0: 입금, 1: 출금)의 표준 한글 명칭 라벨을 매핑 출력하기 위해 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 가맹점 자금 수납 및 출금 전표를 수동 등록하고 과목을 매핑 지정한 본사 재무/자금 담당자의 계정을 식별하기 위해 간접 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 입출금 마스터 정책의 변경 이벤트를 POS에 패키징 배포할 때 발생하는 전송 결과 및 장애 모니터링 로그를 조회하기 위해 연계 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 임의 입금/출금 수납 한도액 설정 및 승인 권한자 레벨 매개 변수를 매칭 참조합니다."
            }
        ]
    }

    # 121. TMACNTTB MEMO AND RELATED TABLES
    tmacnttb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 입금/출금 상세 거래 계정 세부 과목 마스터 테이블 (`TMACNTTB`).\n"
        "프랜차이즈 가맹 본사 재무/자금팀에서 개별 가맹점을 대상으로 발생하는 수납 및 출금 거래 전표 등록 시, 상위 분류 계정 구분(`ACNT_FG`, 0: 입금, 1: 출금) 하위에서 구체적인 세부 과목 명세(세부 과목 코드 `ACNT_CD`, 세부 계정명 `ACNT_NM`, 사용 여부 `USE_YN`)를 규정하고 통제하는 세부 과목 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹점 자금 수납 및 가상계좌 거래 매핑의 근간**: 가맹점 가상계좌 입금 거래 과목 매핑(`Hq_Cash_00001`) 및 세부 계정 마스터 관리 화면(`Hq_Cash_00003`)에서 수동 등록 및 변경되며, 가맹점주가 자금 송금 시 적용되는 회계 전표 상 세부 계정 과목 코드(`acnt_cd`)의 유효성을 검증하고 명칭을 조회하는 부모 마스터 역할을 수행합니다.\n"
        "* **배포 및 연동 자동화 (`TMACNT_T01` 트리거)**: ERP 회계계정 연동 전문 수신 배치(`SUB_MASTER_P`) 또는 본사 어드민 조작을 통해 세부 계정 과목이 등록/수정/삭제되면, `TMACNT_T01` 트리거가 실행되어 변동 마스터 패키지를 가맹점 POS 배포 대기열(`TMCPLK_T01` 등 연계)에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포합니다."
    )

    data["tables"]["tmacnttb"] = {
        "memo": tmacnttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "acnt_fg": "입금/출금 수납 거래 계정 구분 코드 (0: 입금/수납, 1: 출금/차감, PK)",
            "acnt_cd": "입출금 상세 세부 계정 과목 고유 코드 (4자리, PK)",
            "acnt_nm": "가맹점 입출금 세부 계정 과목 상세 한글 명칭 (20자리, 예: 가맹점 물류대출입금, 로열티 정기차감 등)",
            "create_dtime": "세부 계정 과목 마스터 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 자금 담당자)",
            "last_dtime": "세부 계정 과목 마스터 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID",
            "use_yn": "해당 세부 계정 과목 사용 가능 여부 상태 플래그 (Y: 사용중, N: 사용차단, default 'Y')"
        },
        "memo_c": "ERP 세부 회계 과목 연동 전문 수신(SUB_MASTER_P) 또는 본사 세부 계정 과목 관리 화면(Hq_Cash_00003)에서 신규 전표 과목 신설 시 등록됩니다.",
        "memo_u": "계정 과목명 수정, 사용 여부(use_yn) 변경 상태 수정 및 트리거(TMACNT_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "가맹점 자금 입출금 전표 및 가상계좌 입출 내역 대사의 원천 회계 계정이므로 과거 자산 정산 추적을 위해 임의 삭제가 금지됩니다.",
        "memo_r": "가맹점 가상계좌 입금 거래 과목 매핑(Hq_Cash_00001), 세부 계정 과목 마스터 관리(Hq_Cash_00003), 가맹점 자금 입금/수납 등록(Hq_Cash_00004), 가맹점 임의 출금/차감 등록(Hq_Cash_00005), POS 수납 전표 전송 이벤트(TMACNT_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 계정 과목 대조용으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "ttrans_cash_list",
                "description": "자금 거래 상세 원장. [직접적인 1:N 자식 관계] 가맹점별로 발생하는 입금 및 출금 거래 전표에 실제 기입되는 구체적인 세부 계정 코드와 세부 한글 명칭을 제공하여 수납 명세를 정밀 대사하게 돕습니다."
            },
            {
                "table_name": "tmacnctb",
                "description": "입출금 계정 대분류 마스터. [부모 테이블 관계] 본 세부 계정 과목 마스터(TMACNTTB)의 상위 분류 코드 및 기본 정의를 검증하는 연계 관계입니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드 사업부별로 다른 회계 감사용 세부 계정 과목 분류 기준을 지원하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 가맹점의 입금 내역 정산 시 해당 점포의 체인코드와 계정 과목의 사용 허가 범위(use_yn)를 교차 대조하기 위해 사용됩니다."
            },
            {
                "table_name": "mnamemtb",
                "description": "공통 명칭 코드 마스터 테이블. 대분류 입출금 구분(acnt_fg)의 대표 명칭 및 계정 코드의 내부 회계 속성을 식별하기 위해 사용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 자금 계정 과목 마스터를 등록하거나(Hq_Cash_00003), 개별 가맹점의 가상계좌 입금 거래 과목을 재정의한 본사 재무/자금 부서 승인자 계정을 식별하기 위해 조인 참조합니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 자금 계정 마스터 변동 내역이 매장 POS 단말기로 전송되는 실시간 배포 큐 로그를 모니터링하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 가맹점 자상계좌 자동 입금 매핑 처리 타임아웃 및 과목별 자동 분개 규칙 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 122. TMAREATB MEMO AND RELATED TABLES
    tmareatb_memo = (
        "### 1. 테이블 개요\n"
        "본사/체인별 가맹점 관리 지역 구분 마스터 테이블 (`TMAREATB`).\n"
        "프랜차이즈 가맹 본사에서 전국의 가맹점 영업망을 지리적 행정 구역 및 영업 지사 단위(지역 구분 코드 `AREA_CD`, 지역 한글 명칭 `AREA_NM` [예: 서울강북, 경기남부, 영남지사 등])로 분류하고, 이를 브랜드 체인별(`CHAIN_NO`)로 그룹핑하여 관리하는 최상위 지역 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹점 영업 지리 구획의 기준**: 가맹점 마스터(`MMEMBSTB`) 등록 시, 각 점포는 본 테이블에 등록된 지역 코드(`area_cd`) 중 하나에 매핑되어 관리됩니다. 이는 가맹 본사 영업본부의 지역별 실적 분석 및 슈퍼바이저(SV, `TBE_EMP_INF` 연계)의 매장 담당 지리적 구획 설정에 기초 데이터가 됩니다.\n"
        "* **코드 관리 및 관리자 통제**: 본사 어드민 관리 지역 코드 화면(`Hq_Master_00003`)에서 신규 지사 개설이나 행정 구역 통폐합에 따른 신규 지역 코드가 등록/수정/삭제되어 보정 관리됩니다."
    )

    data["tables"]["tmareatb"] = {
        "memo": tmareatb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "area_cd": "가맹점 관할 지사 및 영업 지리 관리 지역 고유 코드 (3자리, PK)",
            "area_nm": "가맹점 관리 지역 상세 한글 명칭 (30자리, 예: 영남지사, 서울강북, 경기남부 등)",
            "create_dtime": "지역 마스터 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 가맹개발팀)",
            "last_dtime": "지역 마스터 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID"
        },
        "memo_c": "본사 영업개발부 지역 조직 신설 시 가맹점 관리 지역 코드 설정 화면(Hq_Master_00003)에서 수동으로 신규 등록됩니다.",
        "memo_u": "지역 명칭 정정이나 담당 지역 병합 시 백오피스 어드민 마스터 화면 조작에 의해 업데이트됩니다.",
        "memo_d": "가맹점 마스터(MMEMBSTB) 및 인사 발령 데이터의 지리적 외래키(FK) 기준이므로 사용 중인 지역 코드의 물리적 삭제가 제한됩니다.",
        "memo_r": "가맹점 관리 지역 코드 설정(Hq_Master_00003), 가맹점 신규 등록(Hq_Memb_00001), 지역별 매출 및 수납 분석 조회, 담당 슈퍼바이저(SV) 매장 일괄 배정 시 영업 권역 조회 참조용 마스터로 사용됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [1:N 직접적인 매핑 관계] 개별 가맹점이 전국의 어느 지사/지역본부(서울, 경기, 영남 등) 관할 영역에 배정되어 영업하고 있는지 지리적 담당을 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드 사업부별로 다른 지역 영업 관리 체계 및 슈퍼바이저 배분 구역을 지정하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tbe_emp_inf",
                "description": "본사 사원 마스터 테이블. 특정 지역본부(TMAREATB)에 정식 임명 및 배치되어 가맹점 실사 순회 및 영업 감독을 수행하는 슈퍼바이저(SV)의 소속 근무지 코드를 교차 검증하기 위해 조인됩니다."
            },
            {
                "table_name": "tifemptb",
                "description": "ERP 인사 인터페이스 테이블. ERP로부터 사원 발령 정보 수신 시, 사원의 근무 지역 코드(area_cd)가 HMS 상의 유효한 영업 관리 지역 정보에 일치하는지 체크하기 위해 연동됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 지역별 가맹점 관리 마스터 코드를 생성 및 수정 등록한 가맹영업팀 본사 직원의 계정을 조회하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 지역본부별 물류 센터 배송비 보전 상한선 및 배송 가용 요일 설정을 매칭 참조합니다."
            }
        ]
    }

    # 123. TMBUMSTB MEMO AND RELATED TABLES
    tmbumstb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 세부 상품 부원료/토핑/사이드메뉴 그룹 마스터 테이블 (`TMBUMSTB`).\n"
        "프랜차이즈 가맹점 POS 결제 화면에서 메인 메뉴(예: 아메리카노) 주문 시 추가 선택할 수 있는 각종 부가 옵션, 토핑, 부원료, 사이드 메뉴(예: 샷 추가, 펄 추가, 시럽 추가 등)의 카테고리 대분류 그룹 정책(부원료 그룹 코드 `SUB_GROUP_CD`, 그룹명 `SUB_GROUP_NM`)을 브랜드 체인별(`CHAIN_NO`)로 규정 관리하는 메뉴 옵션 대분류 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **부메뉴/Modifier 연동 체계의 기점**: 가맹 본사 메뉴관리 부서에서 새로운 토핑이나 부원료 카테고리를 신설하고자 할 때 토핑 설정 화면(`Hq_Master_00006`)에서 신규 그룹을 추가합니다. 이렇게 생성된 부메뉴 그룹 코드(`sub_group_cd`)를 기준으로 개별 세부 상품 매핑 관리 화면(`Hq_Master_00007`)에서 실제 원부자재(상품 코드)들을 1:N으로 귀속 매치시킵니다.\n"
        "* **실시간 POS 동기화 배포 (`TMBUMS_T01` 트리거)**: 본 테이블에 등록된 토핑 그룹 정보가 신설/수정/삭제되면, `TMBUMS_T01` 트리거가 실행되어 변동 마스터 패키지를 가맹점 POS 배포 대기열(`TMCPLK_T01` 등 연계)에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포함으로써 결제 화면의 옵션 구성을 최신화합니다."
    )

    data["tables"]["tmbumstb"] = {
        "memo": tmbumstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "sub_group_cd": "부메뉴/부원료/토핑 대분류 그룹 고유 코드 (2자리, PK)",
            "sub_group_nm": "부메뉴/토핑 대분류 그룹 상세 한글 명칭 (120자리, 예: 샷추가, 펄추가, 시럽선택 등)",
            "create_dtime": "부메뉴 그룹 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 메뉴개발자)",
            "last_dtime": "부메뉴 그룹 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID"
        },
        "memo_c": "본사 상품 기획 부서에서 토핑 및 부원료 그룹 설정 화면(Hq_Master_00006)에서 수동으로 신규 등록됩니다.",
        "memo_u": "부메뉴 대분류 카테고리 명칭 변경 및 트리거(TMBUMS_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "하위 개별 토핑 상품 매핑(TMENU_GOODS_MAP) 및 본사 상품 원장(TGOODSTB)의 기준 마스터이므로 임의 삭제가 금지됩니다.",
        "memo_r": "토핑 및 부원료 그룹 설정(Hq_Master_00006), 부메뉴 개별 상품 매핑 관리(Hq_Master_00007), POS 결제 화면 구성용 콤보박스 바인딩, 부메뉴 전송 이벤트(TMBUMS_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [1:N 연계 관계] 상품 마스터에서 특정 원자재나 판매 옵션 상품이 어떤 토핑/부원료 그룹(sub_group_cd)에 분류되어 매장 POS에 Modifier 옵션으로 표시되는지 조회 참조됩니다."
            },
            {
                "table_name": "tmenu_goods_map",
                "description": "부메뉴 구성 상품 테이블. [직접적인 자식 1:N 관계] 특정 부메뉴 그룹 하위에 실제 판매 가능하게 묶여 있는 개별 토핑 상품들과 판매 단가 가중치를 대조하는 외래키 매핑 테이블입니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 프랜차이즈 브랜드 브랜드별로 다른 음료/푸드 부원료 메뉴판 구조를 제어하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 본사 표준 상품 마스터에 정의된 토핑/부원료 사용 가능 여부를 개별 매장 POS 단말기에서 사용 정지 또는 단절 오버라이드 처리할 때, 소속된 부원료 그룹과의 유효성을 대조하기 위해 사용됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 부원료/토핑 그룹 신설 및 수정사항이 각 점포 POS 단말기에 반영되도록 실시간 배포 이벤트를 발생시킬 때 전송 상태 및 통신 상태를 모니터링하기 위해 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 화면의 토핑/사이드 메뉴 선택 버튼 레이아웃 크기 및 중복 선택 허용 횟수 변수를 매칭 참조합니다."
            }
        ]
    }

    # 124. TMCPLKTB MEMO AND RELATED TABLES
    tmcplktb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 POS 터치키 상품 배치(PLU Key Map) 마스터 테이블 (`TMCPLKTB`).\n"
        "가맹점 POS 결제 단말기 화면에 터치키 형태로 배치되어 노출될 판매 상품 및 메뉴 레이아웃 정보(체인구분 `CHAIN_NO`, 터치키 대분류 탭 코드 `CLPLU_CD`, 개별 터치키 버튼 위치 인덱스 코드 `PLU_CD`, 배치된 본사 상품코드 `GOODS_CD`)를 브랜드 체인별로 설정 관리하는 POS 키패드 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹점 POS 판매 화면 구성의 근간**: 본사의 영업/IT 기획 부서에서 POS 터치키 배치 설정 화면(`St_Master_00011`)을 통해 판매 카테고리별 탭 위치와 개별 버튼 위치에 어떤 식음료 또는 MD 상품 단추를 매칭할지 설정하면 이 테이블에 최종 기입됩니다.\n"
        "* **실시간 POS 동기화 배포 (`TMCPLK_T01` 트리거)**: 본 테이블의 상품 배치 정보가 신설/수정/삭제되면, `TMCPLK_T01` 트리거가 실행되어 변동 마스터 패키지를 가맹점 POS 배포 대기열에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포함으로써 결제 화면의 키 레이아웃 구성을 최신화합니다."
    )

    data["tables"]["tmcplktb"] = {
        "memo": tmcplktb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "clplu_cd": "POS 터치키 대분류 화면 탭 코드 (2자리, PK)",
            "plu_cd": "터치키 대분류 탭 내의 개별 터치키 단추 위치 식별 코드 (3자리, PK)",
            "goods_cd": "해당 터치 단추 위치에 배치 매칭된 본사 표준 상품코드 (20자리)",
            "create_dtime": "터치키 배치 정보 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 시스템 관리자)",
            "last_dtime": "터치키 배치 정보 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID"
        },
        "memo_c": "ERP 키맵 정보 연동 전문 수신(SUB_MASTER_P) 또는 본사 POS 터치키 배치 설정 화면(St_Master_00011)에서 키패드 레이아웃 신규 등록 시 인서트됩니다.",
        "memo_u": "메뉴 개편 시 터치 버튼 매핑 품목 변경 및 트리거(TGOODS_T01, TMCPLK_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "매장 POS 주문 결제 화면 인터페이스 구성의 모체이므로 임의 삭제가 전면 금지됩니다.",
        "memo_r": "가맹점 POS 터치키 배치 설정(St_Master_00011), POS 단말기 결제 인터페이스 화면 버튼 렌더링, 키패드 변동 전송 이벤트(TMCPLK_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [1:N 연계 관계] POS 모니터 터치 키 버튼 하나하나에 매칭된 상품의 한글 명칭, 소비자가격, 면과세 여부를 매칭 출력하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tmcplutb",
                "description": "PLU 대분류 마스터. [부모 테이블 관계] 터치 키패드의 상위 탭 카테고리 명칭(예: 에스프레소, 티/음료, MD상품 등) 정보를 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드별로 다른 POS 터치 메뉴판 키패드 배치 레이아웃 구조를 분할 제공하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 특정 점포에서 일시 품절이나 사용 정지시킨 상품을 POS 화면 터치 키에서 어둡게 처리(비활성화)하거나 주문 차단하기 위해 실시간 연계 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 개별 점포의 업태 및 포스 단말기 수량(예: 주문 전용 포스, 결제 전용 포스)에 따라 맞춤 터치 메뉴판을 내려보낼 때 점포의 계약 형태를 대조하기 위해 간접 조인됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 터치 키 레이아웃 배치 데이터가 실시간 배포 큐(TMCPLK_T01 트리거 구동)를 통해 가맹점 POS로 전송될 때 발생하는 통신 전송 결과 및 장애 모니터링 로그를 모니터링하기 위해 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 터치 모니터의 해상도 가로/세로 키 배열 격자 규격(예: 4x5, 5x6 버튼 개수) 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 125. TMCPLUTB MEMO AND RELATED TABLES
    tmcplutb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 POS 터치키 대분류(화면 탭) 마스터 테이블 (`TMCPLUTB`).\n"
        "가맹점 POS 결제 단말기 판매 화면 상단에 탭(Tab) 카테고리 형태로 구성될 대분류 정보(체인구분 `CHAIN_NO`, 대분류 코드 `CLPLU_CD`, 대분류 한글 명칭 `CLPLU_NM` [예: 에스프레소, 티/에이드, 디저트, MD상품 등])를 브랜드 체인별로 설정 관리하는 터치키 분류 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **터치 키패드 구조의 앵커 마스터**: 본사의 메뉴 기획 및 포스 UI 설계 시, 각 상품군을 직관적으로 분류하여 배치할 상위 탭 목록을 규정하는 역할을 합니다. 본 대분류 마스터 정보는 하위의 개별 버튼 배치 테이블(`TMCPLKTB`) 및 POS 터치키 배치 설정 화면(`St_Master_00011`)의 탭 제목으로 연동 바인딩됩니다.\n"
        "* **실시간 POS 동기화 배포 (`TMCPLU_T01` 트리거)**: 본 테이블의 대분류 탭 정보가 신설/수정/삭제되면, `TMCPLU_T01` 트리거가 실행되어 변동 마스터 패키지를 가맹점 POS 배포 대기열에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포함으로써 결제 화면의 상단 카테고리 탭 구성을 최신화합니다."
    )

    data["tables"]["tmcplutb"] = {
        "memo": tmcplutb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "clplu_cd": "POS 터치키 대분류 화면 탭 고유 코드 (2자리, PK)",
            "clplu_nm": "POS 결제 화면 탭에 표기될 대분류 상세 한글 명칭 (20자리, 예: 에스프레소, 시즌한정, 베이커리 등)",
            "create_dtime": "대분류 탭 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 시스템 관리자)",
            "last_dtime": "대분류 탭 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID"
        },
        "memo_c": "ERP 키맵 그룹 정보 연동 전문 수신(SUB_MASTER_P) 또는 본사 POS 터치키 설정 화면에서 카테고리 탭 신규 등록 시 인서트됩니다.",
        "memo_u": "대분류 탭 명칭 수정 및 트리거(TMCPLU_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "하위 개별 터치 버튼 상품 매칭(TMCPLKTB)의 상위 앵커 마스터이므로 임의 삭제가 금지됩니다.",
        "memo_r": "가맹점 POS 터치키 배치 설정(St_Master_00011), POS 단말기 결제 인터페이스 화면의 카테고리 탭 렌더링, 키패드 대분류 변동 전송 이벤트(TMCPLU_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tmcplktb",
                "description": "POS 터치키 매핑 테이블. [직접적인 N:1 부모-자식 관계] 특정 터치키 대분류 탭 카테고리(TMCPLUTB) 아래에 노출되는 개별 터치 단추별 상품 정보들의 부모가 됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드 사업부별로 POS 결제기 화면의 상단 탭 메뉴 구성을 분리하여 제어하고 제공하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "상품 마스터 테이블. 터치 키패드 대분류에 속하는 상품들의 종류와 판매 속성을 분류 집계하기 위해 간접 연계 조인됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 특정 카테고리(예: 시즌 한정 메뉴 탭) 전체를 점포 사정상 노출 차단 또는 비활성 처리하는 데 대조 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 해당 점포의 POS 단말기 사양과 브랜드 가맹 계약 상태에 부합하는 터치키 카테고리 명칭 목록을 로딩하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. POS 터치키 대분류 탭 정보의 신설/명칭 변경 변동 정보가 실시간 배포 큐(TMCPLU_T01 트리거 구동)를 통해 매장 단말기로 다운로드 전송될 때의 이력 로그를 모니터링하기 위해 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 화면의 상단 탭 카테고리 표시 개수 제한 및 글꼴 크기 매개 변수를 매칭 참조합니다."
            }
        ]
    }

    # 126. TMLCLSTB MEMO AND RELATED TABLES
    tmlclstb_memo = (
        "### 1. 테이블 개요\n"
        "본사 상품 분류체계 - 대분류 코드 마스터 테이블 (`TMLCLSTB`).\n"
        "프랜차이즈 가맹 본사에서 취급하는 전사 상품 및 원부재료를 체계적으로 분류하기 위한 3단계 카테고리(대분류-중분류-소분류) 중 최상위의 대분류 기준 정책(대분류 코드 `LCLASS_CD` [예: '1000' 음료류, '2000' 푸드류 등], 대분류 한글 명칭 `LCLASS_NM`, 해당 대분류에 소속되어 생성된 상품 수 카운트 `GOODS_CREATE_CNT`)을 브랜드 체인별(`CHAIN_NO`)로 설정 관리하는 상품 분류 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **계층형 상품 분류 체계의 기점**: 본사의 상품기획팀에서 상품 대분류/중분류/소분류 통합 코드 관리 화면(`Hq_Master_00005`)을 통해 대분류 코드를 생성 및 수정 정의합니다. 신규 상품 등록 및 채번 처리 시, 지정한 대분류에 속하는 상품 등록 누적 수(`goods_create_cnt`)를 참조 및 카운트업하여 상품코드의 고유 번호를 생성하고 무결성을 유지합니다.\n"
        "* **실시간 POS 동기화 배포 (`TMLCLS_T01` 트리거)**: 본 테이블의 대분류 정보가 신설/수정/삭제되면, `TMLCLS_T01` 트리거가 실행되어 변동 마스터 패키지를 가맹점 POS 배포 대기열에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포함으로써 매장 결제 및 매출 집계 카테고리를 최신화합니다."
    )

    data["tables"]["tmlclstb"] = {
        "memo": tmlclstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "lclass_cd": "상품 대분류 고유 식별 코드 (4자리, PK, default 'T000')",
            "lclass_nm": "상품 대분류 상세 한글 명칭 (35자리, 예: 음료류, 베이커리류, MD상품 등)",
            "create_dtime": "상품 대분류 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 상품 기획자)",
            "last_dtime": "상품 대분류 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID",
            "goods_create_cnt": "해당 대분류 하위에 생성 등록된 총 누적 상품 수 (상품 코드 고유 일련번호 채번에 사용)"
        },
        "memo_c": "ERP 상품 대분류 연동 전문 수신(SUB_MASTER_P) 또는 본사 상품 분류 설정 화면(Hq_Master_00005)에서 카테고리 신설 시 인서트됩니다.",
        "memo_u": "대분류 명칭 수정, 상품 수 카운트 증가 업데이트 및 트리거(TMLCLS_T01, MMSCLS_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "하위 중분류(TMMCLSTB), 소분류(TMSCLSTB) 및 본사 상품 마스터(TGOODSTB)의 최상위 계층 외래키(FK)이므로 임의 삭제가 금지됩니다.",
        "memo_r": "상품 대/중/소분류 통합 코드 설정(Hq_Master_00005), 공통 상품 조회 필터 팝업(CommonModule_GoodsClass), 신상품 등록 및 코드 자동 채번(Hq_Master_00006), 대분류 변동 전송 이벤트(TMLCLS_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tmmclstb",
                "description": "상품 중분류 마스터. [1:N 직접적인 자식 관계] 대분류 하위에 소속되어 2단계 분류 기준을 정의하는 중분류 마스터 테이블입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [1:N 계층 관계] 신상품 등록 시 대분류 카테고리 코드를 부여받아 상품의 분류 기본 속성으로 조인 저장됩니다."
            },
            {
                "table_name": "tmsclstb",
                "description": "상품 소분류 마스터 테이블. [1:N 간접 계층 관계] 3단계 계층형 분류 체계를 완성하기 위해 중분류를 거쳐 연결되는 최하단 소분류 정보를 참조합니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드별로 상이한 상품 대분류 체계를 각각 독자적으로 구성하고 격리하여 관리할 수 있게 돕기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 가맹점 POS 주문 집계 시 카테고리별 매출 통계를 분류하거나, 본사 카테고리 정보를 점포 데이터와 대사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 대분류 분류 코드의 명칭 및 순서 변동 내역이 실시간 배포 큐(TMLCLS_T01 트리거 구동)를 통해 매장 단말기로 전송될 때의 이력 로그를 모니터링하기 위해 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 분류별 자동 주문 추천 시스템 임계치 및 매출 정산 요약 리포트 분류 노출 순서 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 127. TMMCLSTB MEMO AND RELATED TABLES
    tmmclstb_memo = (
        "### 1. 테이블 개요\n"
        "본사 상품 분류체계 - 중분류 코드 마스터 테이블 (`TMMCLSTB`).\n"
        "프랜차이즈 가맹 본사에서 취급하는 전사 상품 및 원부재료를 체계적으로 분류하기 위한 3단계 카테고리(대분류-중분류-소분류) 중 2단계에 해당하는 중분류 기준 정책(대분류 코드 `LCLASS_CD`, 중분류 코드 `MCLASS_CD` [예: '1010' 에스프레소류, '1020' 티/에이드류 등], 중분류 한글 명칭 `MCLASS_NM`)을 브랜드 체인별 (`CHAIN_NO`)로 설정 관리하는 상품 분류 중분류 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **계층형 상품 분류 체계의 중추**: 본사의 상품기획팀에서 상품 대/중/소분류 통합 코드 관리 화면(`Hq_Master_00005`)을 통해 대분류 하위에 귀속될 중분류 코드를 생성 및 수정 정의합니다. 신규 상품 등록 및 정보 수정 시(`Hq_Master_00006`), 상품 분류 필터 팝업(`CommonModule_GoodsClass`)을 통해 1단계 대분류에 이어 2단계 중분류를 선택하여 매핑해주는 드롭다운 바인딩 용도로 사용됩니다.\n"
        "* **실시간 POS 동기화 배포 (`TMMCLS_T01` 트리거)**: 본 테이블의 중분류 정보가 신설/수정/삭제되면, `TMMCLS_T01` 트리거가 실행되어 변동 마스터 패키지를 가맹점 POS 배포 대기열에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포함으로써 매장 결제 및 매출 집계 카테고리를 최신화합니다."
    )

    data["tables"]["tmmclstb"] = {
        "memo": tmmclstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "lclass_cd": "상위 상품 대분류 식별 코드 (4자리, PK)",
            "mclass_cd": "상품 중분류 고유 식별 코드 (4자리, PK)",
            "mclass_nm": "상품 중분류 상세 한글 명칭 (35자리, 예: 에스프레소류, 티/에이드, 브레드류 등)",
            "create_dtime": "상품 중분류 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 상품 기획자)",
            "last_dtime": "상품 중분류 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID"
        },
        "memo_c": "ERP 상품 중분류 연동 전문 수신(SUB_MASTER_P) 또는 본사 상품 분류 설정 화면(Hq_Master_00005)에서 중분류 신설 시 인서트됩니다.",
        "memo_u": "중분류 명칭 수정 및 트리거(TMMCLS_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "하위 소분류(TMSCLSTB) 및 본사 상품 마스터(TGOODSTB)의 2단계 계층 외래키(FK)이므로 임의 삭제가 금지됩니다.",
        "memo_r": "상품 대/중/소분류 통합 코드 설정(Hq_Master_00005), 공통 상품 조회 필터 팝업(CommonModule_GoodsClass), 신상품 등록 및 카테고리 매핑(Hq_Master_00006), 중분류 변동 전송 이벤트(TMMCLS_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tmsclstb",
                "description": "상품 소분류 마스터. [1:N 직접적인 자식 관계] 중분류 하위에 소속되어 3단계 최종 분류 기준을 정의하는 소분류 마스터 테이블입니다."
            },
            {
                "table_name": "tmlclstb",
                "description": "상품 대분류 마스터. [부모 테이블 관계] 상위 카테고리인 대분류 코드 정보를 대조 참조하는 관계입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [1:N 계층 관계] 신상품 등록 시 대분류에 이어 중분류 카테고리 속성을 부여받아 상품의 분류 정보로 조인 저장됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드별로 상이한 상품 중분류 체계를 각각 독자적으로 구성하고 격리하여 관리할 수 있게 돕기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 가맹점 POS 주문 집계 시 카테고리별 매출 통계를 분류하거나, 본사 카테고리 정보를 점포 데이터와 대사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 중분류 분류 코드의 명칭 및 순서 변동 내역이 실시간 배포 큐(TMMCLS_T01 트리거 구동)를 통해 매장 단말기로 전송될 때의 이력 로그를 모니터링하기 위해 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 분류별 자동 주문 추천 시스템 임계치 및 매출 정산 요약 리포트 분류 노출 순서 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 128. TMSCLSTB MEMO AND RELATED TABLES
    tmsclstb_memo = (
        "### 1. 테이블 개요\n"
        "본사 상품 분류체계 - 소분류 코드 마스터 테이블 (`TMSCLSTB`).\n"
        "프랜차이즈 가맹 본사에서 취급하는 전사 상품 및 원부재료를 체계적으로 분류하기 위한 3단계 카테고리(대분류-중분류-소분류) 중 최하단의 소분류 기준 정책(대분류 코드 `LCLASS_CD`, 중분류 코드 `MCLASS_CD`, 소분류 코드 `SCLASS_CD` [예: '1011' 에스프레소(Hot), '1012' 아이스 아메리카노 등], 소분류 한글 명칭 `SCLASS_NM`)을 브랜드 체인별 (`CHAIN_NO`)로 설정 관리하는 상품 분류 소분류 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **계층형 상품 분류 체계의 종착점**: 본사의 상품기획팀에서 상품 대/중/소분류 통합 코드 관리 화면(`Hq_Master_00005`)을 통해 중분류 하위에 귀속될 소분류 코드를 최종 생성 및 수정 정의합니다. 신규 상품 등록 및 정보 수정 시(`Hq_Master_00006`), 상품 분류 필터 팝업(`CommonModule_GoodsClass`)을 통해 1단계 대분류, 2단계 중분류 선택에 이어 최종 3단계 소분류를 선택하여 매핑해주는 드롭다운 바인딩 용도로 사용됩니다.\n"
        "* **실시간 POS 동기화 배포 (`TMSCLS_T01` 트리거)**: 본 테이블의 소분류 정보가 신설/수정/삭제되면, `TMSCLS_T01` 트리거가 실행되어 변동 마스터 패키지를 가맹점 POS 배포 대기열에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포함으로써 매장 결제 및 매출 집계 카테고리를 최신화합니다."
    )

    data["tables"]["tmsclstb"] = {
        "memo": tmsclstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "lclass_cd": "상위 상품 대분류 식별 코드 (4자리, PK)",
            "mclass_cd": "상위 상품 중분류 식별 코드 (4자리, PK)",
            "sclass_cd": "상품 소분류 고유 식별 코드 (4자리, PK)",
            "sclass_nm": "상품 소분류 상세 한글 명칭 (35자리, 예: 핫아메리카노, 시즌티, 식빵류 등)",
            "create_dtime": "상품 소분류 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 상품 기획자)",
            "last_dtime": "상품 소분류 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID"
        },
        "memo_c": "ERP 상품 소분류 연동 전문 수신(SUB_MASTER_P) 또는 본사 상품 분류 설정 화면(Hq_Master_00005)에서 소분류 신설 시 인서트됩니다.",
        "memo_u": "소분류 명칭 수정 및 트리거(TMSCLS_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "본사 상품 마스터(TGOODSTB)의 최종 계층 외래키(FK)이므로 임의 삭제가 금지됩니다.",
        "memo_r": "상품 대/중/소분류 통합 코드 설정(Hq_Master_00005), 공통 상품 조회 필터 팝업(CommonModule_GoodsClass), 신상품 등록 및 최종 카테고리 매핑(Hq_Master_00006), 소분류 변동 전송 이벤트(TMSCLS_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터 테이블. [1:N 계층 관계] 신상품 등록 시 대/중분류에 이어 최종 소분류 카테고리 속성을 부여받아 상품의 분류 기본 속성으로 조인 저장됩니다."
            },
            {
                "table_name": "tmmclstb",
                "description": "상품 중분류 마스터. [부모 테이블 관계] 본 소분류 마스터(TMSCLSTB)의 상위 카테고리인 중분류 코드 정의를 대조 참조하는 관계입니다."
            },
            {
                "table_name": "tmlclstb",
                "description": "상품 대분류 마스터. [부모 테이블 관계] 상위 1단계 카테고리인 대분류 코드를 대조 검증하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드별로 상이한 상품 소분류 체계를 각각 독자적으로 구성하고 격리하여 관리할 수 있게 돕기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 가맹점 POS 주문 집계 시 카테고리별 매출 통계를 분류하거나, 본사 카테고리 정보를 점포 데이터와 대사하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "가맹점 실시간 전송 로그 테이블. 소분류 분류 코드의 명칭 및 순서 변동 내역이 실시간 배포 큐(TMSCLS_T01 트리거 구동)를 통해 매장 단말기로 전송될 때의 이력 로그를 모니터링하기 위해 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 분류별 자동 주문 추천 시스템 임계치 및 매출 정산 요약 리포트 분류 노출 순서 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 129. TMSSRCTB MEMO AND RELATED TABLES
    tmssrctb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 판매 상품별 ERP 원부재료 소스 코드 매핑 마스터 테이블 (`TMSSRCTB`).\n"
        "가맹점 POS에서 실제로 판매되는 각각의 완제품 상품(상품코드 `GOODS_CD`)에 대하여, 물류 유통망 및 ERP 재고 수량 차감(Back-flushing)의 기준이 되는 ERP 소스 자재 코드(소스코드 `SOURCE` [자재 바코드 또는 품번 고유코드])를 매칭 규정하여 관리하는 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **판매와 물류 재고 차감의 징검다리**: 본사 상품 개발 및 물류 관리 부서에서 상품 마스터 설정 화면(`Hq_Master_00008` 등)을 통해 판매용 단품이 ERP 상의 어떤 자재(Source)와 연계되는지 등록합니다. 매장 POS에서 매출이 확정되면 본 테이블의 매핑 정보를 참조하여 해당 상품을 구성하는 소스 원자재의 재고를 실시간 차감 처리하는 근거 데이터가 됩니다.\n"
        "* **실시간 POS 동기화 배포 (`TMSSRC_T01` 트리거)**: 본 테이블의 상품별 소스 매핑 데이터가 신설/수정/삭제되면, `TMSSRC_T01` 트리거가 실행되어 변동 마스터 패키지를 가맹점 POS 배포 대기열에 즉각 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포함으로써 결제 화면 및 재고 차감 기준을 최신화합니다."
    )

    data["tables"]["tmssrctb"] = {
        "memo": tmssrctb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "goods_cd": "본사 표준 판매 상품 고유 식별 코드 (20자리, PK)",
            "source": "해당 판매 상품에 대응되는 ERP 원부자재 소스/품번 코드 (26자리)",
            "create_dtime": "소스 매핑 정보 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 물류/IT 담당자)",
            "last_dtime": "소스 매핑 정보 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID"
        },
        "memo_c": "ERP 자재 마스터 연동 전문 수신(SUB_MASTER_P) 또는 본사 상품 마스터 설정 화면(Hq_Master_00008)에서 자재 매핑 등록 시 인서트됩니다.",
        "memo_u": "연계 자재 코드 변경 및 트리거(TGOODS_T01, TMSSRC_T01) 구동에 의해 실시간 업데이트됩니다.",
        "memo_d": "가맹점 원부재료 실시간 수불 대사 및 소모량 역산(Back-flushing)의 핵심 기준키이므로 함부로 물리 삭제하는 것이 엄격히 제한됩니다.",
        "memo_r": "본사 원부자재 매핑(Hq_Master_00008), 물류 발주 관리(Hq_Stock_00005), 가맹점 재고 소모 계산, 상품 소스 전송 이벤트(TMSSRC_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터. [직접적인 1:1 부모 관계] 판매용 상품의 기본 정보(상품명, 소비자가격, 면과세 등)와 ERP 원자재 소스 코드를 교차 매핑하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tb_recipe",
                "description": "상품 레시피 테이블. [1:N 연계 관계] 완제품 상품 하나를 제조하기 위해 어떤 자재 원자재 소스(source)가 얼마만큼의 규격으로 혼합 소모되는지 레시피 배합 비율을 조회 정밀 대사하기 위해 연계됩니다."
            },
            {
                "table_name": "tb_tot_avg_cost",
                "description": "상품 원가 원장. [1:1 연계 관계] 원부자재 소스(source)의 입고 원가를 결합하여 해당 완제품 상품의 제조 원가율 및 마진율을 시뮬레이션하기 위해 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드 사업부별로 다른 물류 자재 품목 및 ERP 코드 체계를 분리 격리하여 연동하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "매장 상품 마스터 테이블. 개별 매장에서 판매된 POS 매출 건을 기준으로 소스 원자재의 감축 대상 원장을 식별하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "감사 로그 테이블. 상품 소스 매핑 및 원자재 비율 변동 정보가 실시간 배포 큐(TMSSRC_T01 트리거 구동)를 통해 매장 단말기로 전송될 때의 이력 로그를 모니터링하기 위해 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 매출 확정에 따른 가맹점 원부자재 실시간 재고 자동 차감(Back-flushing) 배치 연동 여부 및 차감 타임아웃 주기를 매칭 참조합니다."
            }
        ]
    }

    # 130. TOS_ENTLVC_INF MEMO AND RELATED TABLES
    tos_entlvc_inf_memo = (
        "### 1. 테이블 개요\n"
        "주차장 입출차 내역 연동 인터페이스 원장 테이블 (`TOS_ENTLVC_INF`).\n"
        "프랜차이즈 매장 및 입점 빌딩의 부설 주차 게이트 제어 솔루션(예: 아마노코리아 등)으로부터 수신받은 날짜별 입출차 명세 원시 정보(사업장코드 `BIZ_CD`, 주차영업일자 `PRK_DT`, 차량번호 `CAR_NO`, 주차고유순번 `PRK_SEQ`, 입차일시 `IPKL_DTM`, 출차일시 `OPKL_DTM`, 실제 주차 분수 `PRK_TIME`)를 관리하는 주차 연동 수신 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **외부 주차 연동 솔루션 수신**: 주차 게이트 제어 파트너사 서버로부터 주기적으로 API 및 전문을 수신하는 연동 프로시저(`PR_OS_TOS_IF_ENTLVC_INF`)가 작동하여 본 테이블에 실시간 입출차 리스트를 적재합니다.\n"
        "* **영수증 할인 대사 및 정산 검증**: 본사 회계 및 정산 시스템에서 정산 검증 프로시저(`PR_VRIFY_TOS_ENTLVC_INF`)가 구동되면, 고객이 매장에서 주문 결제하고 POS에 주차 할인 등록 처리한 내역(할인 바코드) 또는 무료 주차 제공 내역과 본 입출차 거래 정보를 상호 매칭 대사하여, 부정 사용이나 미등록 차량 우대 건을 색출 정산 보정합니다."
    )

    data["tables"]["tos_entlvc_inf"] = {
        "memo": tos_entlvc_inf_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "주차장이 소속된 가맹점/사업장 구분 코드 (2자리, PK)",
            "prk_dt": "주차 영업 및 입차 기준 일자 (YYYYMMDD, PK)",
            "car_no": "입출차 차량 번호 명세 (15자리, PK)",
            "prk_seq": "주차 관리 솔루션 측에서 발급한 차량별 입차 일련번호 (50자리, PK)",
            "ipkl_dtm": "차량 실제 게이트 진입 입차 일시 (YYYYMMDDHH24MISS)",
            "opkl_dtm": "차량 실제 게이트 통과 출차 일시 (YYYYMMDDHH24MISS)",
            "prk_time": "총 주차 소요 시간 (분 단위, 4자리)",
            "car_no_4": "차량 번호 뒤 4자리 (4자리, 신속 검색 필터용)",
            "rgnr_id": "최초 등록자 ID (시스템 수신 배치 ID)",
            "rgnr_dtm": "최초 등록 시스템 일시 (TIMESTAMP)",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 시스템 일시 (TIMESTAMP)"
        },
        "memo_c": "외부 주차 솔루션 입출차 이벤트 발생 시 인터페이스 수신 프로시저(PR_OS_TOS_IF_ENTLVC_INF)를 통해 실시간 자동 생성됩니다.",
        "memo_u": "출차 완료 시 출차 시각 및 주차 시간이 누적 업데이트되며, 관리자 화면 보정 시 수동 수정됩니다.",
        "memo_d": "가맹점 주차 할인 사후 대사 및 외부 정산업체 정산금 검증의 기초 원장이므로 임의의 로우 물리 삭제가 금지됩니다.",
        "memo_r": "주차 입출차 내역 조회, 매장 영수증 주차 등록 매칭 검증(PR_VRIFY_TOS_ENTLVC_INF), 주차 대사 불일치 내역 리포팅 화면 조회 시 참조됩니다.",
        "related_tables": [
            {
                "table_name": "if_os010_entlvc_inf",
                "description": "주차 원시 연동 테이블. [1:1 매핑 부모 관계] 외부 주차 대행 솔루션 게이트웨이로부터 실시간 전문으로 밀려들어오는 입출차 전문의 로우 원천 데이터를 담고 있는 원시 테이블입니다."
            },
            {
                "table_name": "tparking_settle",
                "description": "주차 정산 테이블. [1:N 연계 관계] 특정 입차 건에 대하여 매장 식음료 영수증으로 무료 주차 할인을 적용받았거나 신용카드로 추가 정산한 결제 명세와 결합 대사하는 주차 정산 원장입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 입출차가 발생한 주차장이 소속된 매장의 체인점 고유 속성 및 무료 주차 등록 가용 한도를 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsale_hdr",
                "description": "POS 매출 헤더 테이블. 고객이 영수증 바코드를 주차 사전정산기나 사전등록 태블릿에 태깅하여 무료 주차 등록 처리를 행했을 때, 영수증의 유효 금액 및 실매출 발생 여부를 교차 검증하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 주차 차단기 오동작으로 본사 주차관리자가 입출차 정보를 수동 강제 보정하거나 강제 출차 처리한 감사 로그 수정자를 추적하기 위해 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매장 영수증 금액구간별 무료 주차 제공 시간 규격(예: 1만원 이상 1시간, 3만원 이상 2시간 등) 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 131. TOS_IF_ENTLVC_INF MEMO AND RELATED TABLES
    tos_if_entlvc_inf_memo = (
        "### 1. 테이블 개요\n"
        "주차장 입출차 연동 전문 수신 임시 인터페이스 테이블 (`TOS_IF_ENTLVC_INF`).\n"
        "프랜차이즈 매장 및 입점 빌딩의 부설 주차 관리 시스템 서버로부터 EAI 인터페이스 컨트롤러(`Eai_If_EntlvcInf_Controller`)를 통해 전송되는 차량 입출차 각각의 트랜잭션 개별 레코드(사업장코드 `BIZ_CD`, 주차일자 `PRK_DT`, 차량번호 `CAR_NO`, 주차고유순번 `PRK_SEQ`, 입출차구분 `ENTLVC_CLSF` ['I': 입차, 'O': 출차], 이벤트 발생일시 `ENTLVC_DTM`)를 실시간 임시 보관하는 인터페이스 수신 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **EAI를 통한 원시 로그 파싱**: 외부 주차 시스템에서 입차 및 출차 이벤트가 개별 발생할 때마다 EAI JSON API 호출이 이뤄지며, 컨트롤러가 이를 받아 `TOS_IF_ENTLVC_INF`에 입출구분을 포함해 다이렉트로 인서트합니다.\n"
        "* **통합 정합성 정제 처리**: 본 테이블에 적재된 입차/출차 거래 명세를 매칭 정제 프로시저(`PR_OS_TOS_IF_ENTLVC_INF`)가 주기적으로 스캔하여 동일 차량(`car_no`)과 고유 순번(`prk_seq`) 기준으로 짝을 맞춰 하나의 완결된 주차 세트 레코드로 병합한 후, 상위 마스터 테이블인 `TOS_ENTLVC_INF`에 최종 데이터(입차 시각 및 출차 시각이 결합됨)로 가공 적재합니다."
    )

    data["tables"]["tos_if_entlvc_inf"] = {
        "memo": tos_if_entlvc_inf_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "주차장이 소속된 가맹점/사업장 구분 코드 (2자리, PK)",
            "prk_dt": "주차 기준 영업 일자 (YYYYMMDD, PK)",
            "car_no": "입출차 차량 번호 명세 (15자리, PK)",
            "prk_seq": "주차 솔루션 측에서 발급한 차량별 입차 고유 일련번호 (50자리, PK)",
            "entlvc_clsf": "입차/출차 구분 코드 (1자리, PK, 'I': 입차, 'O': 출차)",
            "entlvc_dtm": "개별 이벤트 실제 발생 일시 (YYYYMMDDHH24MISS)",
            "rgnr_id": "최초 등록자 ID (EAI 수신 ID)",
            "rgnr_dtm": "최초 등록 일시 (YYYYMMDDHH24MISS)",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "외부 주차 시스템 EAI 연동 컨트롤러(Eai_If_EntlvcInf_Controller)의 API 수신 핸들러에 의해 입/출차 발생 시 각각 즉각 생성됩니다.",
        "memo_u": "EAI 재전송 및 정정 패킷 유입 시 최종 타임스탬프가 업데이트됩니다.",
        "memo_d": "입출차 병합 프로시저(PR_OS_TOS_IF_ENTLVC_INF)의 원시 아카이브 자료이자 인터페이스 이력 검증의 근거이므로 인위적인 로우 삭제가 방지됩니다.",
        "memo_r": "EAI 주차 트랜잭션 수신 컨트롤러, 입출차 통합 가공 프로시저(PR_OS_TOS_IF_ENTLVC_INF), 할인 대사 및 정산 검증 프로시저(PR_VRIFY_TOS_ENTLVC_INF) 실행 시 원천 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tos_entlvc_inf",
                "description": "주차 입출차 병합 원장 테이블. [N:1 직접적인 부모-자식 관계] 본 임시 테이블에 수신된 입차 레코드와 출차 레코드가 매칭 병합 프로시저(PR_OS_TOS_IF_ENTLVC_INF)를 통해 단일 주차 거래 세트로 통합 정제되어 들어가는 목적지 테이블입니다."
            },
            {
                "table_name": "tparking_settle",
                "description": "주차 정산 테이블. 임시 연동 데이터가 완결된 후, 결제 영수증 할인이나 정산 완료 여부를 비교 검증하는 정산 마스터 테이블입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 외부 주차 전문에서 수신된 사업장코드(biz_cd)가 HMS 시스템 내에 유효하게 등록된 가맹점인지 코드를 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsale_hdr",
                "description": "POS 매출 헤더 테이블. 고객이 무료 주차 사전 정산을 신청한 경우, 유효 매출 내역을 검증하기 위해 간접 조인 연계됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "감사 로그 테이블. EAI 연동 인터페이스 컨트롤러를 통해 들어온 외부 호출 통신 로그 및 정산 완료 응답 처리 이력을 모니터링하기 위해 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 주차 전문 수신 대기 및 배치 락 타임아웃 주기를 매칭 참조합니다."
            }
        ]
    }

    # 132. TOS_IF_ENTLVC_INF_HIS MEMO AND RELATED TABLES
    tos_if_entlvc_inf_his_memo = (
        "### 1. 테이블 개요\n"
        "주차장 입출차 연동 배치 처리 실행 이력/로그 테이블 (`TOS_IF_ENTLVC_INF_HIS`).\n"
        "외부 주차 게이트웨이 전문을 수집 및 병합하여 통합 원장을 빌드하는 배치 프로시저(`PR_OS_TOS_IF_ENTLVC_INF`)가 동작할 때마다 발생하는 처리 결과, 수행 일자(`PROC_DATE`), 순번(`PROC_SEQ`), 대상 프로시저명(`PROC_NM`), 성공 여부 플래그(`ERR_FG`), 가공 처리된 레코드 개수(`PROC_CNT`), 오류 발생 시 상세 트레이스 로그(`ERR_MSG`)를 축적 기록하는 DB 배치 감사 로그 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **프로시저 수행 이력 트래킹**: 매장별 주차 인터페이스 가공 배치 스케줄러가 구동되면, `PR_OS_TOS_IF_ENTLVC_INF` 프로시저는 시작 및 종료 시점에 본 테이블에 트랜잭션 수행 요약(대상 로우 건수, 성공 로우 수)과 SQL 예외 발생 시 에러 메시지(`err_msg`)를 삽입합니다.\n"
        "* **인터페이스 모니터링 및 복구 제어**: 시스템 통합 관제 센터에서 주차 게이트 연동 장애 또는 배치 먹통 현상을 모니터링하기 위해 본 로그 이력을 상시 스캔합니다. 만약 `err_fg`에 에러 표시가 발생한 경우, 인프라 담당자는 오류 메시지를 판정하여 파트너사 전송 포맷 미스매치를 해결하고 재실행 배치를 구동하는 역할을 합니다."
    )

    data["tables"]["tos_if_entlvc_inf_his"] = {
        "memo": tos_if_entlvc_inf_his_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "proc_date": "배치 가공 및 수신 처리 실행 일자 (YYYYMMDD, PK)",
            "proc_seq": "일자별 처리 실행 고유 일련번호 (8자리, PK)",
            "proc_nm": "실행 처리된 주차 연동 대상 프로시저/배치 서비스 한글/영문 명칭 (50자리)",
            "err_fg": "배치 수행 최종 성공/실패 여부 식별 구분자 (10자리, 예: SUCCESS, ERROR)",
            "tot_cnt": "해당 회차에 처리 대상이 된 임시 수신 입출차 데이터 총 건수",
            "proc_cnt": "오류 없이 성공적으로 병합 정합성을 이뤄 통합 원장으로 가공 이관 완료된 총 건수",
            "err_msg": "예외 상황 및 장애 발생 시 데이터베이스 엔진이 반환한 에러 덤프/상세 메시지 (4000자리)",
            "create_dtime": "로그 레코드 생성 및 기록 완료 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "주차 입출차 병합 처리 프로시저(PR_OS_TOS_IF_ENTLVC_INF)의 트랜잭션 단위 실행 시 자동 생성 및 로그 레코드가 인서트됩니다.",
        "memo_u": "배치 최종 종료 시 성공 건수 계산 및 발생 에러 문자열 삽입에 의해 최종 수정 완료됩니다.",
        "memo_d": "데이터베이스 및 네트워크 연동 장애 여부를 기록하는 시스템 진단 이력이므로 임의 삭제를 허용하지 않습니다.",
        "memo_r": "데이터베이스 관리자(DBA) 관제 콘솔, 주차 인터페이스 상태 대시보드 화면, 주차 요금 정산 대사 장애 분석 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tos_if_entlvc_inf",
                "description": "주차 임시 인터페이스 테이블. [1:N 간접 감사 이력 관계] 이력 로그가 남을 때 처리 대상이 되었던 입출차 전문 데이터의 원천 테이블입니다."
            },
            {
                "table_name": "tos_entlvc_inf",
                "description": "주차 입출차 병합 원장 테이블. 본 이력에 기재된 proc_cnt(성공 건수)만큼 가공 처리되어 병합 인서트되는 최종 종착지 테이블입니다."
            },
            {
                "table_name": "tparking_settle",
                "description": "주차 정산 테이블. 정산 검증 시 주차 게이트 연동 장애가 있었는지 판정하기 위해 배치 성공 이력을 간접적으로 참조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 배치 오류가 특정 매장의 코드(오타 등) 유효성 때문에 발생했는지 진단할 때 가맹점 정보 조인용으로 간접 연계됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "감사 로그 테이블. EAI 호출 장애와 배치 솔루션 장애를 연합 모니터링하기 위해 시스템 장애 리포트에 함께 조인되어 확인될 수 있습니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 주차 연동 배치 자동 복구(Auto-retry) 실행 여부 및 최대 시도 횟수 한계값 변수를 매칭 참조합니다."
            }
        ]
    }

    # 133. TOS_IF_ENTLVC_INF_LOG MEMO AND RELATED TABLES
    tos_if_entlvc_inf_log_memo = (
        "### 1. 테이블 개요\n"
        "주차장 입출차 전문 수신 원천 트랙킹 로그 테이블 (`TOS_IF_ENTLVC_INF_LOG`).\n"
        "외부 주차 제어 시스템으로부터 수신된 개별 입출차 트랜잭션 원시 데이터(사업장코드 `BIZ_CD`, 주차영업일자 `PRK_DT`, 차량번호 `CAR_NO`, 주차고유순번 `PRK_SEQ`, 입출구분 `ENTLVC_CLSF`, 발생시각 `ENTLVC_DTM`)의 변경 이력 및 수신 아카이브 로그를 저장하는 이력 보존용 감사 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **수신 원천 데이터의 불변 보존**: `PR_OS_TOS_IF_ENTLVC_INF` 프로시저 구동 시, 입차/출차 매칭 완료되어 임시 버퍼 테이블(`TOS_IF_ENTLVC_INF`)에서 삭제되거나 변경되는 로우들의 원본 형태를 그대로 복제 보존함으로써 차후 주차 요금 시비나 정산 불일치 발생 시 추적할 수 있는 2차 백업 로그 역할을 합니다.\n"
        "* **로그 순번 기반 이력 관리**: 하나의 주차 순번(`prk_seq`)에 대하여 입차-출차 재전송이나 중복 수신 등이 발생할 경우, `log_seq`를 1씩 증가시키며 모든 기록을 누적하여 저장하므로, 통신 유실이나 중복 전송 정합성을 사후 판정하는 감사 자료로 쓰입니다."
    )

    data["tables"]["tos_if_entlvc_inf_log"] = {
        "memo": tos_if_entlvc_inf_log_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "주차장이 소속된 가맹점/사업장 구분 코드 (2자리, PK)",
            "prk_seq": "주차 관리 솔루션 측에서 발급한 차량별 입차 고유 일련번호 (50자리, PK)",
            "log_seq": "동일 주차 일련번호 내 누적 수신 및 변동 이력 순번 (PK, 1부터 순차 증가)",
            "prk_dt": "주차 기준 영업 일자 (YYYYMMDD)",
            "car_no": "입출차 차량 번호 명세 (15자리)",
            "entlvc_clsf": "입차/출차 구분 코드 (1자리, 'I': 입차, 'O': 출차)",
            "entlvc_dtm": "개별 주차 이벤트 실제 발생 일시 (YYYYMMDDHH24MISS)",
            "rgnr_id": "최초 등록자 ID (배치/EAI 세션 ID)",
            "rgnr_dtm": "최초 수신 및 로그 생성 일시 (YYYYMMDDHH24MISS)",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "주차 입출차 병합 처리 프로시저(PR_OS_TOS_IF_ENTLVC_INF) 구동 시, 임시 버퍼에서 원본 레코드를 백업 보존하기 위해 인서트합니다.",
        "memo_u": "동일 수신 데이터의 재처리 또는 시스템 수정 발생 시 변경 일시가 업데이트됩니다.",
        "memo_d": "원천 수신 로그에 해당하므로 데이터 보존 정책(Retention Policy)에 근거한 주기적 삭제 배치 외에 수동 물리 삭제가 일절 금지됩니다.",
        "memo_r": "주차 불일치 거래 감사 추적, 고객 이의제기 소명용 원천 패킷 내역 조회, EAI 인터페이스 정합성 대사 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tos_if_entlvc_inf",
                "description": "주차 임시 인터페이스 테이블. [1:1 복사 보존 관계] 수신된 원천 입출차 데이터가 처리된 후 삭제되거나 갱신되기 전에, 그 히스토리를 원시 상태 그대로 본 로그 테이블에 보관 이관합니다."
            },
            {
                "table_name": "tos_entlvc_inf",
                "description": "주차 입출차 병합 원장 테이블. 본 로그 테이블에 저장된 개별 이벤트(입차 또는 출차)들이 병합 처리되어 들어간 최종 결과 매핑 레코드를 담고 있습니다."
            },
            {
                "table_name": "tparking_settle",
                "description": "주차 정산 테이블. 정산 검증 배치 구동 및 주차권 오정산 소송 또는 이의제기 접수 시, 입출차 시각 원본 데이터와 무결성 판정을 위해 로그 원장을 조회합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 점포 주차장의 과거 수신 패킷 추적 시, 매장의 고유 정보 및 계열사 분류를 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "감사 로그 테이블. 시스템 트랜잭션의 송수신 정합성 감사 모니터링 시 연동 로그로 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 주차 임시 인터페이스 로그 보관 연한(예: 3개월, 1년 등 데이터 파티셔닝/삭제 주기) 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 134. TOS_IF_PRKDIS_RGN_INF MEMO AND RELATED TABLES
    tos_if_prkdis_rgn_inf_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 POS 주차 할인 등록 인터페이스 송신 원장 테이블 (`TOS_IF_PRKDIS_RGN_INF`).\n"
        "가맹점 POS 단말기에서 결제(영수증 매출 및 무료 주차 수동 등록) 또는 취소(반품) 거래가 체결될 때, 해당 차량번호에 무료 주차 혜택이나 할인 처리를 외부 주차장 관리 시스템(예: 아마노코리아 등)으로 송신 전송하기 위해 임시 적재 및 전송 결과를 기록하는 아웃바운드 인터페이스 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 매출 발생 감시 및 할인 트리거링**: POS 매출이 완료 및 확정(매출 원장 `TSALE_HDR`에 반영)되는 즉시, 매출 연동 트리거 `STRNHD_T02`가 구동되어 영수증 정보와 연동 주차 등록 할인 데이터를 파싱하여 본 테이블(`TOS_IF_PRKDIS_RGN_INF`)에 송신 대기('W') 상태로 적재합니다.\n"
        "* **Telex 모듈을 통한 외부 전송**: 통신 송신 데몬(Telex Q02, Q04 등)이 본 테이블을 상시 폴링하며 미전송 건에 대해 주차 시스템 할인등록 API 규격에 맞는 전문을 송신 전송합니다. 전송이 완료되면 `if_rslt`를 성공('Y') 또는 실패('N') 처리하고 실패 시 상세 사유(`if_err_msg`)를 보강 기입합니다. 만약 고객이 영수증을 취소 반품할 경우 거래구분 `bztc_clsf='1'`로 취소 전송 전문을 유발합니다."
    )

    data["tables"]["tos_if_prkdis_rgn_inf"] = {
        "memo": tos_if_prkdis_rgn_inf_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "주차장이 소속된 가맹점/사업장 구분 코드 (2자리, PK)",
            "shop_cd": "할인을 요청한 소속 가맹점 매장 고유 코드 (2자리, PK)",
            "amt_time_clsf": "할인 적용 기준 구분자 (1자리, PK, '1': 판매금액 비례, '2': 고정 할인시간)",
            "car_no": "할인 적용 대상 차량 번호 (15자리, PK)",
            "prk_dt": "주차 영업 일자 (YYYYMMDD, PK)",
            "prk_seq": "외부 주차 제어기 발급 주차 일련번호 (50자리, PK)",
            "pos_no": "매출이 발생한 점포 내 실물 POS 단말기 번호 (2자리, PK)",
            "bk_dt": "POS 매출 발생 영업 일자 (YYYYMMDD, PK)",
            "bztc_no": "영업일자별 POS 매출 고유 거래 일련번호 (7자리, PK)",
            "bztc_clsf": "거래 성격 구분 코드 (1자리, '0': 정상 적용, '1': 결제 취소에 따른 할인 취소)",
            "sale_amt": "판매금액 또는 할인 시간 데이터 값 (10자리, 예: '0120000'=12만원, '0000120'=120분)",
            "rgnr_id": "최초 등록자 ID (트리거 또는 POS 세션 ID)",
            "rgnr_dtm": "최초 등록 일시 (YYYYMMDDHH24MISS)",
            "updr_id": "최종 수정자 ID (Telex 송신 세션 ID)",
            "updr_dtm": "최종 수정 및 전송 처리 완료 일시 (YYYYMMDDHH24MISS)",
            "if_rslt": "외부 주차 서버 송신 전송 결과 플래그 (1자리, 'Y': 성공, 'N': 에러, 'W': 전송 대기)",
            "if_err_msg": "외부 주차 API 서버가 반환한 오류 통신 상세 메시지 (500자리)",
            "pos_key_bill_no": "매출 전표 고유 결합 키 영수증 식별자 (20자리, PK)"
        },
        "memo_c": "POS 매출 거래 확정(TSALE_HDR) 또는 주차 할인 수동 등록 시 트리거(STRNHD_T02)에 의해 자동으로 생성 적재됩니다.",
        "memo_u": "Telex 송신 데몬(Q02, Q04 등) 전송 결과에 의해 성공 플래그(if_rslt) 및 에러 로그(if_err_msg)가 실시간 업데이트됩니다.",
        "memo_d": "주차 할인 전송 성공 유무 추적 및 가맹점 정산 보정을 위해 임의 삭제가 제한됩니다.",
        "memo_r": "POS 매출 확정 주차 등록 연동(STRNHD_T02), Telex 실시간 송신 처리, 외부 API 전송 로그 에러 조회 시 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsale_hdr",
                "description": "POS 매출 헤더 테이블. [1:1 직접 연동 관계] 주차 할인 발생의 원천이 되는 영수증 매출 정보(총 판매금액, 취소 여부 등)를 매칭 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tos_entlvc_inf",
                "description": "주차 입출차 병합 원장 테이블. [N:1 연계 관계] POS에서 할인 신청한 대상 차량이 실제로 주차장에 게이트를 통과해 머물러 있는 차량인지 실시간으로 매칭 검증하기 위해 참조합니다."
            },
            {
                "table_name": "tparking_settle",
                "description": "주차 정산 테이블. 송신한 할인 내역이 외부 주차 정산기에 최종적으로 반영되어 요금 차감이 정상 완료되었는지 사후 대조하는 주차 정산 마스터 테이블입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 주차 할인 등록을 요청한 POS가 속한 브랜드 매장의 체인점 고유 속성 및 무료 주차 등록 가용 한도를 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmslogtb",
                "description": "감사 로그 테이블. Telex 모듈을 통한 주차 할인등록 전문 전송 중 발생한 네트워크 장애나 파트너사 API 서버의 타임아웃 오류 내역을 감사하기 위해 모니터링 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 영수증 1매당 적용할 수 있는 최대 무료 주차 시간 합산 상한선 및 취소 반품 시 주차 할인 자동 환수(Rollback) 여부 정책 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 135. TOS_REGST_CAR_INF MEMO AND RELATED TABLES
    tos_regst_car_inf_memo = (
        "### 1. 테이블 개요\n"
        "주차장 정기 등록 차량/직원 차량 관리 마스터 테이블 (`TOS_REGST_CAR_INF`).\n"
        "프랜차이즈 가맹점 및 본사 소속 임직원, 정기/장기 주차 이용 차량, 협력업체 차량에 대한 할인 등록 마스터 정보(일련번호 `SEQ`, 차량번호 `CAR_NO`, 사용자/임직원명 `EE_NM`, 유효기간 시작일 `STRT_DT`, 유효기간 종료일 `END_DT`)를 설정 관리하는 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **임직원 및 정기 차량 자동 할인 혜택 적용**: 외부 주차 시스템 연동 및 병합 프로시저(`PR_OS_TOS_IF_ENTLVC_INF`)가 매장 주차 입차 트랜잭션을 처리할 때, 본 마스터 테이블의 `CAR_NO` 정보를 대조하여 현재 주차 영업일자(`prk_dt`)가 지정된 유효기간(`strt_dt` ~ `end_dt`)에 포함되는지 검사합니다.\n"
        "* **요금 과금 면제 처리**: 본 마스터에 등록된 차량임이 확인될 경우, 주차 요금 부과 대상에서 자동 제외되도록 플래그를 마킹하여, POS 영수증 인증 없이도 무료 출차 또는 0원 정산 처리가 가능하도록 지원합니다."
    )

    data["tables"]["tos_regst_car_inf"] = {
        "memo": tos_regst_car_inf_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "seq": "정기 등록 차량 관리용 고유 내부 일련번호 (PK, Numeric)",
            "car_no": "정기 무료 혜택 부여 차량 번호 명세 (15자리, 복합 인덱스)",
            "ee_nm": "해당 차량을 이용하는 직원/소유주 상세 성명 (100자리)",
            "strt_dt": "정기 주차 혜택 유효 시작 일자 (YYYYMMDD, 복합 인덱스)",
            "end_dt": "정기 주차 혜택 유효 종료 일자 (YYYYMMDD, 복합 인덱스)"
        },
        "memo_c": "본사 임직원 관리자 화면 또는 정기권 등록 배치 연계를 통해 신규 정기 주차 차량 정보가 인서트됩니다.",
        "memo_u": "사원 퇴사, 유효기간 연장 및 차량 변경 시 관리자 수정 화면에 의해 업데이트됩니다.",
        "memo_d": "정기 주차 자동 면제 혜택 유효 검증을 위한 테이블이므로 임의 삭제 시 해당 차량에 주차 요금이 불합리하게 부과될 위험이 있습니다.",
        "memo_r": "주차 입출차 병합 및 요금 면제 판정 프로시저(PR_OS_TOS_IF_ENTLVC_INF), 임직원 차량 등록 상태 조회 화면 작동 시 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tos_entlvc_inf",
                "description": "주차 입출차 병합 원장 테이블. [1:N 계층 관계] 외부에서 수신된 차량 정보가 정기 등록 차량 마스터와 매칭되는지 확인하여 주차 요금 부과에서 자동 면제 처리하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tparking_settle",
                "description": "주차 정산 테이블. 정기 등록 차량(직원 차량 등)에 대해서 주차 차감액이 면제 처리(0원 정산)되었는지 결합 확인하는 마스터 테이블입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 매장 소속 직원들의 등록 내역이 본사에 등록된 소속 가맹점 마스터와 유효한 범위에 있는지 간접 대조됩니다."
            },
            {
                "table_name": "tsale_hdr",
                "description": "POS 매출 헤더 테이블. 직원 차량이 물건을 구매하고 영수증으로 이중 등록했는지 또는 직원 차량에 대한 예외 처리가 성립하는지 교차 분석 시 활용됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 직원 정기 차량 등록을 신청/승인한 본사 또는 매장 관리자 계정 정보를 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매장/사업장별로 등록 가능한 정기 차량(임원, 직원, 협력사) 수 상한값(Threshold) 및 차량 유효기간 연장 갱신 규칙 변수를 매칭 참조합니다."
            }
        ]
    }

    # 136. TPRICETB MEMO AND RELATED TABLES
    tpricetb_memo = (
        "### 1. 테이블 개요\n"
        "본사 상품 단가 및 판가/공급가 히스토리 마스터 테이블 (`TPRICETB`).\n"
        "프랜차이즈 가맹 본사에서 각 상품별(상품코드 `GOODS_CD`)로 가격 유형(단가구분 `PRICE_FG` ['0': 판매가(소비자가), '1': 공급가(가맹점 매입원가)])을 다르게 하여, 유효 기간별(시작일자 `START_DATE`, 종료일자 `END_DATE`) 및 매장 그룹별(`CHAIN_MS_NO`)로 표준 단가 이력을 보관 설정하는 마스터 원장입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **기간별 가격 정책 예약 및 자동 반영**: ERP에서 자재 매입 단가나 제품 소비자 가격 변동 시 연동 프로시저(`SUB_MASTER_P`)에 의해 인서트되거나 본사 영업 마스터 관리 화면(`Hq_Master_00006`)에서 등록합니다. 시작일자(`start_date`) 조건에 근거하여 유효시점이 도래하면 적용됩니다.\n"
        "* **실시간 POS 동기화 배포 (`TPRICE_T01` 트리거)**: 본 테이블의 단가가 변동(Insert/Update/Delete)되면, `TPRICE_T01` 트리거가 실행되어 가맹점 가격 배포 대기열에 패키지를 적재하고 각 가맹점 POS 및 가맹점 마스터(`MGDPRCTB`)에 신속 갱신 동기화합니다."
    )

    data["tables"]["tpricetb"] = {
        "memo": tpricetb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "goods_cd": "본사 표준 판매 상품/자재 고유 식별 코드 (20자리, PK)",
            "price_fg": "단가 구분 코드 (1자리, PK, '0': 소비자 판매판가, '1': 가맹점 공급매입가)",
            "start_date": "단가 가격 정책 적용 시작 영업 일자 (YYYYMMDD, PK)",
            "end_date": "단가 가격 정책 적용 종료 영업 일자 (YYYYMMDD)",
            "chain_ms_no": "가맹점 유형 또는 지역별 가격 차등 적용을 위한 점포유형코드 (6자리)",
            "pre_price": "가격 변경 직전의 과거 단가 금액 (Numeric, size=12,3)",
            "price": "현재 유효한 확정 단가 금액 (Numeric, size=12,3)",
            "raise_fg": "단가 인상 및 인하 변동 구분 플래그 (1자리, '0': 인상, '1': 인하)",
            "goods_control_fg": "해당 기간 내 상품 단품의 판매 통제 상태 (1자리, '0': 정상판매, '1': 일시품절/판매정지)",
            "create_dtime": "단가 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 MD/영업기획자)",
            "last_dtime": "단가 최종 수정 및 갱신 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 처리자 ID",
            "goods_brand_cd": "상품 브랜드 계열사 구분 코드 (5자리)",
            "goods_style_cd": "상품 스타일 및 하위 규격 속성 코드 (20자리)"
        },
        "memo_c": "ERP 단가 연동 전문 수신(SUB_MASTER_P) 또는 본사 상품 등록 화면(Hq_Master_00006)에서 기간별 단가 정보 입력 시 인서트됩니다.",
        "memo_u": "단가 재조정 및 배포 트리거(TPRICE_T01) 구동에 의해 실시간 업데이트 처리됩니다.",
        "memo_d": "가맹점 발주 대금 정산 및 POS 매출 결제 단가 대사의 기준 자료이므로 물리 삭제가 통제됩니다.",
        "memo_r": "상품 단가 및 공급가 조회, 레시피 구성 자재원가 가중치 계산(SUB_RECIPE_IO_P), 수불 자재이동 평가(SUB_STOCK_MGMVHD_P), 실시간 가격 동기화 배포(TPRICE_T01) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터. [직접적인 1:N 부모 관계] 판매 상품의 고유 속성(상품명, 과세여부, 브랜드 등)을 담고 있으며, 단가 정보가 어떤 상품에 귀속되는지 조회하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tb_recipe",
                "description": "상품 레시피 테이블. 레시피 구성 자재의 개별 단가(TPRICETB.PRICE_FG = '1')를 조합하여 완제품 상품 1단위를 제조할 때 소요되는 가공원가를 동적으로 연산하기 위해 조인됩니다."
            },
            {
                "table_name": "tb_tot_avg_cost",
                "description": "상품 원가 원장. [1:N 연계 관계] 공급 단가 변동 흐름과 실제 입고 수량을 결합하여 이동평균 단가 및 기간별 매출 원가율을 분석하기 위해 조인됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드 사업부 및 매장 유형별로 가격 정책을 다르게 운영할 수 있도록 격리하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgdprctb",
                "description": "매장 판매단가 테이블. 본사 단가 테이블(TPRICETB)의 변동 데이터가 실시간 배포 트리거(TPRICE_T01)를 거쳐 개별 점포 POS 단말기에 반영된 점포별 실제 판매가 원장입니다."
            },
            {
                "table_name": "tsale_dtl",
                "description": "POS 매출 상세 테이블. 판매된 매출 시점의 실거래 가격(할인금액 차감 후)이 본사에서 지정한 표준 소비자가격(tpricetb)과 얼마나 괴리가 있는지 마진 분석(대사) 리포트 조회 시 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 판매가 인상 시 가맹점 자동 알림 여부 및 공급가 변동 시 미배송 발주건 자동 단가 갱신 적용 정책 여부를 매칭 참조합니다."
            }
        ]
    }

    # 137. TPROGDTB MEMO AND RELATED TABLES
    tprogdtb_memo = (
        "### 1. 테이블 개요\n"
        "본사 프로모션 대상 상품 설정 마스터 테이블 (`TPROGDTB`).\n"
        "프랜차이즈 가맹 본사에서 특정 마케팅 캠페인/프로모션(프로모션 년도 `PROMOTION_YEAR`, 프로모션 코드 `PROMOTION_CD`)이 집행될 때, 할인 적용 대상이 되는 구체적인 상품 정보(상품코드 `GOODS_CD`) 및 일반 할인 구분(`GEN_DC_FG` ['0': 할인율(%), '1': 고정할인금액]), 상세 할인 금액 및 할인율(`GEN_AMT`, `GEN_DC`)을 설정 지정하는 세부 프로모션 상품 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **행사 대상 상품 지정 및 마진 시뮬레이션**: 본사 마케팅/기획팀에서 프로모션 대상 상품 등록 화면(`Hq_Master_00019`)을 통해 해당 캠페인 기간 동안 할인 판매할 상품 리스트와 할인 폭을 최종 저장 정의합니다. 본 정보는 점포 영업 매출 집계 및 원가 대사 시 참조됩니다.\n"
        "* **실시간 POS 동기화 배포 (`TPROGD_T01` 트리거)**: 본 테이블의 프로모션 연계 상품 정보가 신설/수정/삭제되면, `TPROGD_T01` 트리거가 실행되어 변동 행사 상품 패키지를 가맹점 POS 배포 대기열에 적재 및 각 가맹점 POS 단말기로 실시간 다운로드 배포함으로써 매장 행사 상품 할인 결제 처리가 즉각 수행될 수 있도록 돕습니다."
    )

    data["tables"]["tprogdtb"] = {
        "memo": tprogdtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "promotion_year": "프로모션 적용 연도 (4자리, PK, YYYY)",
            "promotion_cd": "프로모션 정책 고유 식별 코드 (4자리, PK)",
            "goods_cd": "할인 대상 본사 표준 상품 식별 코드 (20자리, PK)",
            "create_dtime": "프로모션 상품 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 마케팅 기획자)",
            "last_dtime": "프로모션 상품 최종 수정 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정 조작자 ID",
            "gen_dc_fg": "일반 행사 상품 할인 형식 구분자 (1자리, '0': 할인율 비율 적용, '1': 할인금액 고정 적용)",
            "gen_amt": "할인 적용할 최종 고정 원화 금액 (Numeric)",
            "gen_dc": "할인 적용할 비율 수치 (Numeric, size=5,2 [예: 10.00 = 10%])",
            "goods_add_fg": "프로모션 적용 외에 추가적인 사은품이나 옵션 품목 매치 식별 여부 플래그 (1자리)"
        },
        "memo_c": "본사 프로모션 기획 화면(Hq_Master_00019) 또는 연동 전문 배치(SUB_MASTER_P) 구동 시 프로모션별 대상 품목 지정에 의해 인서트됩니다.",
        "memo_u": "프로모션 도중 할인 폭 정정 또는 배포 트리거(TPROGD_T01) 구동에 의해 업데이트됩니다.",
        "memo_d": "가맹점 매출 실적 정산 및 행사 할인 보전금 계산의 원천 매칭 기준이므로 행사가 완료되기 전에는 삭제가 엄격히 제한됩니다.",
        "memo_r": "프로모션 대상 상품 조회 및 등록(Hq_Master_00019), 가맹점 POS 가격 정책 배포(TPROGD_T01), 본사 마스터 동기화 프로시저(SUB_MASTER_P) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tprogmtb",
                "description": "프로모션 정책 마스터. [직접적인 N:1 부모 관계] 프로모션의 기본 운영 정보(캠페인 명칭, 행사 시작일자, 종료일자, 행사 구분 등)를 매칭하여 상품별 할인율을 활성화하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터. [1:1 부모 관계] 프로모션 적용 대상이 되는 개별 단품의 품목명 및 표준 단가를 매칭 조회하기 위해 조인 연계됩니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 테이블. 프로모션 할인율(%) 또는 할인금액이 적용되기 전의 순수 기본 판매 소비자 가격을 조회하여 최종 프로모션 적용 판가를 계산하기 위해 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드 사업부 단위로 개별적으로 기획 및 집행되는 가격 할인 캠페인을 분리 격리하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgdprctb",
                "description": "가맹점 실제 판매단가 테이블. 본사의 프로모션 할인 결정에 따라 매장 단말기 및 점포 마스터에 세일 단가가 실시간 갱신 적용되도록 트리거(TPROGD_T01) 연동으로 활용됩니다."
            },
            {
                "table_name": "tsale_dtl",
                "description": "POS 매출 상세 테이블. 행사 상품이 판매되었을 때, POS에서 실제 할인 적용된 할인액(Promotion Discount)과 본사의 기준 금액이 적합하게 정산 대사되었는지 교차 정밀 분석 시 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 프로모션 할인 혜택의 중복 적용(예: 멤버십 할인 + 카드 프로모션 할인 동시 적용 여부) 한계 정책 변수를 매칭 참조합니다."
            }
        ]
    }

    # 138. TPRILGTB MEMO AND RELATED TABLES
    tprilgtb_memo = (
        "### 1. 테이블 개요\n"
        "본사 상품 단가 및 판가/공급가 변동 이력 로그 테이블 (`TPRILGTB`).\n"
        "본사의 상품 단가 마스터 테이블(`TPRICETB`)에 신설, 수정, 삭제 등의 트랜잭션이 발생할 때마다, 변동 처리 구분(처리구분 `PROC_FG` ['A': 신설, 'U': 수정, 'D': 삭제]), 변동 전 단가와 변동 후 단가(`PRE_PRICE`, `PRICE`), 변경 조작 정보 등을 타임스탬프 일련번호(로그일련번호 `LOG_SEQ` [YYYYMMDD + 8자리 순번]) 기반으로 축적하는 DB 단가 감사 이력 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **트리거 감시를 통한 단가 히스토리 자동 적재**: 본사 단가 테이블 `TPRICETB`에 변경 작업이 수행되면, 단가 감시 트리거 `TPRICE_T01`이 자동으로 발화하여 직전 단가 필드(`pre_price`)와 신규 지정 단가 필드(`price`)를 캡처해 `TPRILGTB`에 적재합니다.\n"
        "* **가맹점 배포 추적 및 감사 증적**: 가격 변동에 따른 매장 배포 핸들러(`Tr_TPRICE_T01_Service` 등)는 본 이력 로그 테이블의 기록들을 순차적으로 스캔 및 가공하여 개별 매장 POS 단말기로 갱신 배포 패키지를 큐잉 전송하는 자료원으로 활용합니다. 사후 가맹점 대금 정산 분쟁이나 가격 오적용 소송 발생 시 최종 백업 증적으로 활용됩니다."
    )

    data["tables"]["tprilgtb"] = {
        "memo": tprilgtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "log_seq": "단가 변동 로그 기록용 고유 복합 일련번호 (16자리, PK, YYYYMMDD + 8자리 순번)",
            "proc_fg": "단가 변동 처리 구분 플래그 (1자리, 'A': 신규 등록, 'U': 가격 정정 변경, 'D': 가격 정책 삭제)",
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리)",
            "goods_cd": "단가 변동이 일어난 본사 표준 상품 코드 (20자리, 복합 인덱스)",
            "price_fg": "단가 가격 유형 구분자 (1자리, 복합 인덱스, '0': 소비자 판매가, '1': 가맹점 공급가)",
            "start_date": "해당 단가 정책의 적용 시작 일자 (YYYYMMDD, 복합 인덱스)",
            "end_date": "해당 단가 정책의 적용 종료 일자 (YYYYMMDD)",
            "chain_ms_no": "가격 차등 적용 점포유형코드 (6자리)",
            "pre_price": "단가 변경 조작이 가해지기 직전의 과거 가격 수치 (Numeric, size=12,3)",
            "price": "조작 완료 후 최종 확정된 신규 단가 수치 (Numeric, size=12,3)",
            "raise_fg": "단가 가격 인상 및 인하 상태 구분자 (1자리, '0': 인상, '1': 인하)",
            "goods_control_fg": "상품 단품의 판매 통제 상태 플래그 (1자리, '0': 정상판매, '1': 판매중지)",
            "create_dtime": "단가 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (MD/영업기획자)",
            "last_dtime": "단가 최종 수정 및 로그 생성 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 조작 처리자 ID",
            "goods_brand_cd": "상품 브랜드 계열사 구분 코드 (5자리)",
            "goods_style_cd": "상품 스타일 및 하위 규격 속성 코드 (20자리)"
        },
        "memo_c": "본사 단가 마스터(TPRICETB)에 신설, 수정, 삭제 등의 변동 트랜잭션 발생 시 단가 감시 트리거(TPRICE_T01)에 의해 자동으로 생성 적재됩니다.",
        "memo_u": "단가 변동 이력 로그의 특성상 불변(Immutable) 감사 아카이브이므로 적재 이후의 수정(Update)이 엄격히 차단됩니다.",
        "memo_d": "과거 가격 정책 소급 대사 및 법적 증적 자료이므로 임의의 데이터 물리 삭제가 통제됩니다.",
        "memo_r": "단가 변동 흐름 조회, 단가 배포 서비스(Tr_TPRICE_T01_Service), 가맹점 발주 대금 정산 오류 및 가격 오적용 사후 감사 대사 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tpricetb",
                "description": "본사 상품 단가 마스터. [1:N 원천-로그 관계] 본 테이블에 적재되는 모든 단가 변동 행위의 원천이 되는 본사 단가 마스터 테이블입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터. [1:1 부모 관계] 단가 이력이 남은 대상 상품의 기본 속성(상품명, 소비세 면과세 구분 등)을 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 특정 브랜드 사업부에서 조정한 단가 인상/인하 행위를 격리하여 분석하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tb_tot_avg_cost",
                "description": "상품 원가 원장. 과거 특정 시점에 공급 단가가 갑자기 변동하여 매장 매입 단가 왜곡이 발생했는지 추적 검증 시 본 이력 로그와 대조 참조합니다."
            },
            {
                "table_name": "mgdprctb",
                "description": "매장 판매단가 테이블. 본사 단가 변동 이력(tprilgtb)이 가맹점 POS 시스템 및 매장 단가 마스터에 누락 없이 정상 적용되었는지 무결성 비교(배포 동기화 완료 여부 판정) 시 활용됩니다."
            },
            {
                "table_name": "tsale_dtl",
                "description": "POS 매출 상세 테이블. 매출이 일어난 시점에 매장 POS에서 올바른 가격으로 계산되었는지, 혹은 단가 업데이트 지연으로 오류 가격이 적용되었는지 사후 진단할 때 시점 비교를 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 단가 변동 로그 유지보수 보관 정책 기간(예: 1년, 5년 등 소송 대사용 데이터 보존 연한) 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 139. TPROMATB MEMO AND RELATED TABLES
    tpromatb_memo = (
        "### 1. 테이블 개요\n"
        "본사 프로모션 기본 정책/행사 정의 마스터 테이블 (`TPROMATB`).\n"
        "프랜차이즈 가맹 본사에서 매년 기획 집행하는 가격 할인 및 사은품 행사 등 각종 마케팅 프로모션 캠페인의 기본 규칙(체인코드 `CHAIN_NO`, 프로모션 연도 `PROMOTION_YEAR`, 프로모션 코드 `PROMOTION_CD`, 캠페인명 `PROMOTION_NM`, 유효기간 `VALID_FROM_DATE` ~ `VALID_TO_DATE`, 적용범위 `GOOD_PROC_FG`, 한도 설정 및 혜택 내역)을 통합 설정 관리하는 핵심 프로모션 정책 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **행사 기본 룰 설정 및 실적 집계**: 본사 마케팅 부서에서 새로운 이벤트를 기획하여 프로모션 마스터 관리 화면(`Hq_Master_00019`)에 행사 조건(수량/금액 한도, 할인 방식)을 입력하여 확정하면 본 테이블에 등록됩니다. 프로모션 진행 및 종료 후 본사 실적 분석 화면(`Hq_Sales_00018`)에서 가맹점별 행사 매출 수량과 총 할인금액을 집계 대조합니다.\n"
        "* **가맹점 배포 연동 (`TPROMA_T01` 트리거)**: 본 테이블에 프로모션 정책 마스터 정보가 C.U.D 처리되면, 정책 배포 트리거 `TPROMA_T01`이 발화하여 변동 가격/행사 팩을 가맹점 큐에 적재하고 전국 가맹점 POS 및 점포 시스템에 원격 배포하여 행사 기간 동안 점포 결제 시 해당 프로모션 할인 룰이 적용될 수 있게 합니다."
    )

    data["tables"]["tpromatb"] = {
        "memo": tpromatb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "promotion_year": "프로모션 적용 연도 (4자리, PK, YYYY)",
            "promotion_cd": "프로모션 정책 고유 식별 코드 (4자리, PK)",
            "promotion_nm": "고객 및 점주용 프로모션 공식 행사 명칭 (30자리)",
            "promotion_scheme": "프로모션의 상세 기획 의도, 적용 조건 및 비즈니스 매커니즘 설명 (2000자리)",
            "promotion_result": "프로모션 행사 진행에 따른 예상/실제 매출 성과 및 기안자 종합 작성 의견 (2000자리)",
            "promotion_etc": "기타 프로모션과 관련한 중요 참고사항 비고 (500자리)",
            "valid_from_date": "프로모션 행사 정식 개시 및 가격 적용 시작 일자 (YYYYMMDD)",
            "valid_to_date": "프로모션 행사 정식 종료 및 가격 적용 마감 일자 (YYYYMMDD)",
            "good_proc_fg": "할인 적용 대상 범위 코드 (1자리, '0': 매장 내 전품목 적용, '1': 지정된 특정 상품만 적용)",
            "limit_type": "할인 제공 시 한도(Cap) 조건 구분자 (1자리, '0': 특정 수량 한도, '1': 특정 금액 한도, '2': 특정 메뉴 한도)",
            "limit_amt": "프로모션 총액 혹은 거래 1회당 적용 가능한 최대 금액 한도 (Numeric)",
            "limit_qty": "거래 1회당 최대 할인 적용 수량 제한값 (Numeric)",
            "benefit_type": "할인 혜택 지급 방식 구분자 (1자리, '0': 할인율(%) 적용, '1': 할인금액(원) 차감 적용)",
            "benefit_amt": "할인 혜택 고정 적용 시 차감할 원화 금액 수치 (Numeric)",
            "benefit_rate": "할인 혜택 비율 적용 시의 퍼센티지 값 (Numeric)",
            "create_dtime": "프로모션 기획 최초 생성 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 기획 등록자 ID",
            "last_dtime": "프로모션 기획 최종 변경/승인 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 조작자 ID",
            "rist_dc_amt": "동일 거래당 고객에게 제공 가능한 누적 최대 할인 한도액 (Numeric, size=11,2)"
        },
        "memo_c": "본사 프로모션 기획 화면(Hq_Master_00019) 또는 ERP 연동 배치(SUB_MASTER_P) 구동에 의해 신규 프로모션 기획 승인 시 인서트됩니다.",
        "memo_u": "행사 기간 연장, 한도액 조정 및 배포 트리거(TPROMA_T01) 실행 시 수정 업데이트됩니다.",
        "memo_d": "가맹점 매출 실적 정산 대사 및 행사 할인 정합성 검증의 근거 마스터이므로 진행 중인 행사는 삭제가 엄격히 불허됩니다.",
        "memo_r": "프로모션 기획 설정(Hq_Master_00019), 프로모션 실적/대비 매출 분석(Hq_Sales_00018), 실시간 매장 정책 배포(TPROMA_T01) 실행 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tprogdtb",
                "description": "프로모션 대상 상품 설정 마스터. [1:N 계층 관계] 본 테이블에서 정의한 프로모션의 혜택 및 유효기간 범주 안에서 구체적으로 할인 적용을 받을 수 있게 지정된 상세 상품 매핑 테이블입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터. 프로모션이 전상품 적용(good_proc_fg='0')인지, 혹은 특정 개별 상품군 적용(good_proc_fg='1')인지 가려내기 위해 조인 연계되는 상품 마스터 테이블입니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 테이블. 프로모션 적용 전 표준 소비자가격과 비교하여 할인율 기여 효과 및 할인 원부자재 원가를 시뮬레이션 산정할 때 조인 연계됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 특정 브랜드 체인(예: 커피 사업부, 베이커리 사업부 등)별 프로모션 캠페인을 상호 격리 관리하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgdprctb",
                "description": "매장 판매단가 테이블. 본사 프로모션 정책 마스터(tpromatb)가 배포 트리거(TPROMA_T01)를 통해 매장 단말기로 동기화 배포되어, 매장별 실제 프로모션 할인 단가로 렌더링되게 만듭니다."
            },
            {
                "table_name": "tsale_dtl",
                "description": "POS 매출 상세 테이블. 고객 결제 완료 시 적용된 할인 구분이 본 프로모션의 혜택 금액(benefit_amt) 및 혜택 비율(benefit_rate) 정책 한도 내에서 정확하게 작동했는지 정산 검증(대사)할 때 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 동일 점포 내에서 복수의 활성화된 프로모션이 겹칠 경우 우선순위 판정 로직 및 가맹점 프로모션 비용 본사-대리점 분담율 기본값 설정을 매칭 참조합니다."
            }
        ]
    }

    # 140. TPROSGTB MEMO AND RELATED TABLES
    tprosgtb_memo = (
        "### 1. 테이블 개요\n"
        "본사 프로모션 대상 제외 상품 설정 테이블 (`TPROSGTB`).\n"
        "본사 마케팅 부서에서 기획한 프로모션 행사 정책 중 전사/전상품 적용 기준(`GOOD_PROC_FG = '0'`)에서 부득이하게 할인 적용이 배제/제외되어야 하는 특정 예외 상품 정보(체인코드 `CHAIN_NO`, 프로모션 연도 `PROMOTION_YEAR`, 프로모션 코드 `PROMOTION_CD`, 제외대상 상품코드 `GOODS_CD`)를 설정 관리하는 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **특정 상품 프로모션 제외 룰 처리**: 전사 10% 가격 할인 행사 등 대규모 캠페인 시, 법적 규제 품목(담배, 종량제 봉투)이나 본사 저마진 특정 상품(특수 위탁 상품 등)을 프로모션 대상 제외 상품 관리 화면(`Hq_Master_00019`)에 제외 상품으로 기입하여 할인을 원천 차단합니다.\n"
        "* **실시간 가맹점 POS 배포 (`TPROSG_T01` 트리거)**: 본 테이블에 프로모션 제외 상품 매핑이 변경(Insert/Update/Delete)되면, `TPROSG_T01` 트리거가 실행되어 가맹점 가격 배포 대기열에 실시간 변동 이벤트를 적재하고 가맹점 POS 단말기로 최신 제외 목록을 다운로드 처리하여 매장 결제 시 행사 제외 검증 필터로 사용되게 제어합니다."
    )

    data["tables"]["tprosgtb"] = {
        "memo": tprosgtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "체인 및 브랜드 사업부 구분 코드 (4자리, PK)",
            "promotion_year": "프로모션 적용 연도 (4자리, PK, YYYY)",
            "promotion_cd": "프로모션 정책 고유 식별 코드 (4자리, PK)",
            "goods_cd": "할인 적용에서 제외 및 배제될 본사 표준 상품 식별 코드 (20자리, PK)",
            "create_dtime": "제외 상품 지정 최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (본사 마케팅 기획자)",
            "last_dtime": "제외 상품 지정 최종 변경 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 조작 조작자 ID"
        },
        "memo_c": "본사 프로모션 기획 관리 화면(Hq_Master_00019)에서 프로모션별 행사 제외 상품 추가 시 인서트됩니다.",
        "memo_u": "제외 상품 리스트 변경 및 배포 트리거(TPROSG_T01) 실행 시 수정 업데이트됩니다.",
        "memo_d": "행사 기간 도중 가맹점 POS에서 비대상 품목의 오할인을 차단하는 법적/정산적 통제 자료이므로 인위적인 삭제가 제한됩니다.",
        "memo_r": "프로모션 기획 설정 및 제외 상품 등록(Hq_Master_00019), 가맹점 POS 정책 실시간 배포(TPROSG_T01) 구동 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tpromatb",
                "description": "프로모션 정책 마스터. [N:1 계층 관계] 본 프로모션의 혜택(전체 적용 등)에 포함되지 않고 배제 처리될 상품 예외 조건을 관리하기 위해 부모 테이블과 조인 참조됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "본사 상품 마스터. [1:1 부모 관계] 프로모션 행사 적용에서 누락/배제될 개별 품목의 품명과 표준 속성을 매칭 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tpricetb",
                "description": "상품 단가 테이블. 특정 상품이 제외 대상으로 지정될 경우 본사 마진 보전이 필요한 고가/저마진 품목인지 여부를 대조 평가하기 위해 참조됩니다."
            },
            {
                "table_name": "tchaintb",
                "description": "체인 마스터 테이블. 브랜드별 가격 프로모션 캠페인의 예외 상품 정책을 상호 격리 관리하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgdprctb",
                "description": "매장 판매단가 테이블. 본사 제외 상품 마스터(tprosgtb)의 설정이 배포 트리거(TPROSG_T01)를 거쳐 매장 단말기로 동기화 배포되어, 매장 POS에서 해당 메뉴를 스캔하더라도 프로모션 할인이 절대 적용되지 않도록 제어합니다."
            },
            {
                "table_name": "tsale_dtl",
                "description": "POS 매출 상세 테이블. 매출 정산 및 정합성 검증 시, 프로모션 제외 상품으로 명시된 품목에 불합리하게 할인이 가해진 트랜잭션이 없는지 대사 분석할 때 조인 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 프로모션 비대상 품목(담배, 종량제 봉투 등 공공성 재화) 자동 제외 리스트 매칭 룰 정책을 설정 참조합니다."
            }
        ]
    }

    # 141. TSM_BOND_STOA_PARR_INF MEMO AND RELATED TABLES
    tsm_bond_stoa_parr_inf_memo = (
        "### 1. 테이블 개요\n"
        "제휴 파트너 결제 외상채권 정산지급 연동 인터페이스 원장 테이블 (`TSM_BOND_STOA_PARR_INF`).\n"
        "매장에서 가맹점 POS 결제 시 모바일상품권, 제휴 카드사 포인트, 스마트 쿠폰 등 다양한 외부 제휴 수단으로 매출이 체결될 때, 해당 제휴 결제에 대한 수수료 차감 정보 및 본사 정산 지급 거래 명세(사업장코드 `BIZ_CD`, 매장코드 `SHOP_CD`, 지급일자 `PYMT_DT`, 거래번호 `BZTC_NO`, 지급순번 `PYMT_SEQ`, 공급가액 `SUPR_PRIC`, 부가세 `VAT`, 제휴수수료 `FEE`)를 수신 기록하는 EAI 인터페이스 연동 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **POS 제휴 결제 전송 및 정산 정보 적재**: 매장 POS에서 모바일 쿠폰이나 제휴 할인 결제가 확정되는 즉시, Telex 결제 전송 모듈(`P08_SqlMapper.xml`)이 구동되어 본 인터페이스 원장에 지급 대기('N') 상태의 수수료 계산 명세 레코드를 인서트합니다.\n"
        "* **외상 매출금 대사 및 정산 처리**: 정산 기획팀 및 대사 분석 모듈이 본 인터페이스 원장에 누적된 제휴사별 정산 대상 금액(`stoa_subj_amt`)과 실매출 데이터를 대조하여 수수료율 적합 여부를 확인하고, 회수할 채권을 `tsm_bond_settle` 마스터 원장에 매핑하여 외상 대금을 청구 회수하는 정산 기본 자료로 활용합니다."
    )

    data["tables"]["tsm_bond_stoa_parr_inf"] = {
        "memo": tsm_bond_stoa_parr_inf_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "정산이 소속된 법인/사업장 구분 코드 (2자리, PK)",
            "shop_cd": "지급 거래가 일어난 개별 가맹점 점포 코드 (2자리, PK)",
            "pymt_dt": "제휴사 정산금 지급 및 발생 일자 (YYYYMMDD, PK)",
            "bztc_no": "매출 영수증 식별용 고유 거래번호 명세 (20자리, PK, YYYYMMDD + 점포번호 + POS번호 + 매출일련번호 결합)",
            "pymt_seq": "개별 결제 수단별 세부 지급 구분 일련번호 (PK, Numeric)",
            "cncl_clsf_cd": "거래 정상 처리 및 승인 취소 여부 구분자 (1자리, PK, '0': 정상승인, '1': 결제취소)",
            "coal_mst_no": "쿠폰/상품권을 발행한 연합 제휴사 고유 마스터 번호 (Numeric)",
            "resrv_dt": "예약 상품 연동 시의 원천 예약 일자 (YYYYMMDD)",
            "resrv_seq": "원천 예약 일련 순번 (Numeric)",
            "utz_dt": "실제 고객이 쿠폰/서비스를 이용 및 소진한 실사용 일자 (YYYYMMDD)",
            "utz_cpsn": "서비스 이용 고객 실물 인원수 (Numeric)",
            "utz_summ": "고객 이용 명세에 대한 한글 적요 설명문 (300자리)",
            "utz_amt": "고객이 사용 처리한 제휴 결제 총 원화 금액 (Numeric)",
            "disc_amt": "제휴 프로모션에 따라 추가 공제된 순수 할인액 (Numeric)",
            "stoa_knd_cd": "세부 정산 지급 처리 유형 구분 코드 (2자리, 예: '31', '9')",
            "stoa_subj_amt": "수수료 및 정산 산정 기준이 되는 대상 원화 금액 (Numeric)",
            "supr_pric": "정산 대상 금액에 대한 순수 공급가액 수치 (Numeric)",
            "vat": "정산 대상 금액에 부과된 매출 부가가치세 수치 (Numeric)",
            "rfud_fee": "고객 환불 조치 시 제휴사에서 차감한 환불 수수료액 (Numeric)",
            "rfud_amt": "환불 최종 승인 완료된 환불 원화 금액 (Numeric)",
            "fee": "제휴 대행사에서 부과한 최종 정산 수수료 총액 (Numeric)",
            "fee_supr_pric": "정산 수수료에 대한 순수 공급가액 수치 (Numeric)",
            "fee_vat": "정산 수수료에 부과된 부가가치세 수치 (Numeric)",
            "stoa_rgn_yn": "가맹점 정산 원장 최종 반영 완료 여부 플래그 (1자리, 'Y': 반영완료, 'N': 미반영)",
            "stoa_rgn_dt": "가맹점 정산 원장에 등록 처리된 실적 반영 일자 (YYYYMMDD)",
            "stoa_rgn_seq": "당일 정산 등록 처리 순번 (Numeric)",
            "rgnr_id": "최초 등록자 ID (Telex 포트/세션 ID)",
            "rgnr_dtm": "최초 통신 수신 및 로그 생성 일시",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 정산 처리 및 수정 일시"
        },
        "memo_c": "POS 제휴 결제 승인 완료 시 Telex 통신 데몬(P08_SqlMapper.xml)에 의해 자동으로 생성 인서트됩니다.",
        "memo_u": "가맹점 정산 마감 및 본사 회수금 매치 시 반영 여부(stoa_rgn_yn) 및 정산등록일자가 업데이트됩니다.",
        "memo_d": "가맹점 수수료 대사 및 제휴 대금 정산 감사 증적이므로 사후 삭제가 제한됩니다.",
        "memo_r": "제휴사 정산지급 조회, Telex 실시간 결제 정보 송수신 처리, 가맹점 외상 채권 및 정산 대사 리포트 출력 시 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsale_hdr",
                "description": "POS 매출 헤더 테이블. POS 제휴사 승인 매출 거래 내역과 본 정산 인터페이스 수신 레코드의 원천 영수증을 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsale_pay",
                "description": "POS 결제 상세 테이블. [1:N 연계 관계] POS 결제 수단 중 제휴결제(모바일상품권, 제휴포인트 등)로 분류되어 정산 대상이 된 실거래 결제 정보와 대조하기 위해 참조합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [1:1 매칭 관계] 수신된 정산 전문의 가맹점 번호를 바탕으로 본사의 고유 BIZ_CD와 SHOP_CD를 식별 매칭하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tb_partner_master",
                "description": "제휴사 마스터 테이블. [N:1 관계] 쿠폰/상품권 발행 제휴 파트너사의 마스터 정보(수수료율, 정산 주기 등)를 조회하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_bond_settle",
                "description": "외상 채권 정산 테이블. 본 인터페이스로 들어온 제휴사 정산지급 상세 내역을 수집/매칭하여 가맹점 수수료 정산 및 본사 채권 회수액 확정 처리를 수행하는 정산 마스터 테이블입니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 제휴사 정산지급 시 적용되는 기본 부가세 계산법 및 정산 대기 기간 만료 규칙 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 142. TSM_CARC_MST MEMO AND RELATED TABLES
    tsm_carc_mst_memo = (
        "### 1. 테이블 개요\n"
        "신용카드사 및 제휴사 마스터 테이블 (`TSM_CARC_MST`).\n"
        "가맹점 카드 결제 및 제휴 정산의 표준 기준이 되는 국내 신용카드사 고유 코드 정보(카드사코드 `CARC_CD`, 카드사명 `CARC_NM`, 카드사약어 `CARC_SHRTNM`, 카드매입사 `BYGC_CD`, 포인트가용 플래그 `PNT_USE_YN`, KVP연계코드 `KVP_CARC_CD`)를 EAI 연동 인터페이스를 통해 일괄 수신 저장하는 카드 마스터 버퍼 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **카드사 마스터 정보 일괄 수신**: 카드사 마스터 연동 배치 스케줄러(Job `CardInterface`)가 기동되면, ERP 카드 정보가 본 테이블(`TSM_CARC_MST`)에 인서트된 후 수신 처리 프로시저(`SUB_IF_HYDM_RECV_P`)를 호출하여 수신 데이터의 유효성을 검사합니다.\n"
        "* **POS 동기화 및 가맹점 정산 기준 배포**: 수신 프로시저 처리가 성공적으로 완결되면 `pos_proc_yn = 'Y'`로 최종 갱신되고, 본사의 표준 신용카드 마스터 정보(`TCARDTB`)를 최신화하여 가맹점 수수료율 계산 및 POS 신용카드 거래 승인 데이터 분류의 원천 코드로 작용하게 합니다."
    )

    data["tables"]["tsm_carc_mst"] = {
        "memo": tsm_carc_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "rowid": "데이터베이스 행 고유 물리적 식별 고유키 (PK, Bigint, 자동 시퀀스)",
            "carc_cd": "국내 신용카드사 고유 2자리 발급 코드 (2자리, 복합 인덱스)",
            "carc_nm": "국내 신용카드사 공식 한글 명칭 (50자리)",
            "carc_shrtnm": "보고서 및 단말기 출력용 카드사 공식 축약 한글 명칭 (30자리)",
            "bygc_cd": "카드 전표 매입 업무를 대행하는 카드 매입사 식별 코드 (6자리)",
            "onl_stl_mthdz": "PG사 연계 온라인 카드 결제 시 가동되는 온라인 결제 수단 명세 (100자리)",
            "onl_stl_parm": "온라인 결제 승인 API 호출 시 동반되는 부가 파라미터 규격 설정 (100자리)",
            "pnt_use_yn": "해당 신용카드 결제 시 포인트 복합 사용 차감 가용 여부 플래그 (1자리, 'Y'/'N')",
            "rgnr_id": "최초 연동 등록자 ID (배치 세션 ID)",
            "rgnr_dtm": "최초 마스터 수신 일시",
            "updr_id": "최종 마스터 정보 갱신 처리자 ID",
            "updr_dtm": "최종 정보 갱신 처리 일시",
            "del_yn": "해당 카드사의 결제 지원 종료/삭제 플래그 (1자리, 'Y': 지원안함, 'N': 정상사용)",
            "kvp_carc_cd": "스마트폰 카드 간편 결제 규격(KVP) 전용 매핑용 4자리 카드 코드",
            "pos_proc_date": "카드 마스터 배치 연동 일자 (YYYYMMDD, 복합 인덱스)",
            "pos_proc_seq": "카드 마스터 배치 일자별 고유 실행 시퀀스 번호 (8자리, 복합 인덱스)",
            "pos_proc_yn": "배치 및 프로시저(SUB_IF_HYDM_RECV_P) 정상 처리 완료 및 반영 여부 플래그 (1자리, 'Y': 성공, 'N': 대기/실패)",
            "pos_proc_remark": "연동 처리 중 장애나 통신 불합리 발생 시 적재되는 배치 예외 사유 메시지 (4000자리)",
            "pos_proc_create_dtime": "배치 연동 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)",
            "pos_proc_last_dtime": "배치 연동 트랜잭션 최종 갱신 완료 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "신용카드 마스터 수신 배치(CardInterface_SqlMapper.xml)가 실행될 때 ERP 가격 수신 명세를 본 테이블에 배치 인서트합니다.",
        "memo_u": "수신 가공 프로시저(SUB_IF_HYDM_RECV_P)의 최종 성공 복구 여부에 따라 pos_proc_yn 플래그가 최종 업데이트됩니다.",
        "memo_d": "POS 신용카드 결제 거래 내역 분류의 과거 대사 이력 기준 마스터이므로 임의 삭제가 통제됩니다.",
        "memo_r": "신용카드사 목록 조회, 카드사 마스터 수신 배치(CardInterface), 수신 연동 프로시저(SUB_IF_HYDM_RECV_P), 신용카드 매출 정산 수수료 대사 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_card_issuer",
                "description": "카드사 기본 정보 마스터. [1:1 매칭 관계] EAI 연동으로 수신된 최신 신용카드 카드사 코드 및 매입사 정보를 본사 정산 결제용 카드 마스터에 반영하기 위해 매칭 참조합니다."
            },
            {
                "table_name": "tsale_pay",
                "description": "POS 결제 상세 테이블. 매장에서 고객이 신용카드로 결제했을 때, 승인된 카드 코드가 본 마스터에 등록된 유효한 카드사 코드(carc_cd)와 정합성을 이루는지 정산 대사 시 참조됩니다."
            },
            {
                "table_name": "if_recpsvtb",
                "description": "인터페이스 수신 이력 테이블. [1:1 매칭 감사 관계] 카드사 마스터 수신 배치(IF_FB_206)가 수행된 전체 처리 건수, 성공 여부, 장애 트레이스 메시지를 기록 관리합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 카드사별 가맹점 수수료율 설정이나 신용카드사별 가맹점 번호(가맹점-카드사 계약 관계)를 관리하는 매핑 정보의 기준 테이블로 연계됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. POS 단말기 신용카드 결제 처리 시 카드 번호 첫 6자리(Card BIN) 기준의 자동 카드사 분류 룰 및 KVP 결제 처리 옵션 변수를 매칭 참조합니다."
            }
        ]
    }

    # 143. TSM_CASH_PVO_MST MEMO AND RELATED TABLES
    tsm_cash_pvo_mst_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 예비비/소액 현금 지급 마스터 테이블 (`TSM_CASH_PVO_MST`).\n"
        "본사 재경팀에서 각 가맹점에 지급한 영업 준비금 및 예비비 발생 명세(사업장코드 `BIZ_CD`, 매장코드 `SHOP_CD`, 지급일자 `PVO_DT`, 지급순번 `PVO_SEQ`, 예비비 구분 `PRST_CLSF_CD` [11: 영업준비금, 12: 반품준비금 등], 지급액 `PVO_AMT`, 지급자 `PVOR`, 수령부서/지급처 `PWTI`)를 수신 저장하는 예비비 인터페이스 마스터 버퍼 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **예비비 수신 및 익일 준비금 반영**: 준비금 인터페이스 배치 스케줄러(Job `CashReadyInterface`)가 구동되면 ERP의 준비금 발생 데이터가 본 테이블(`TSM_CASH_PVO_MST`)에 등록된 후 수신 완결 프로시저(`SUB_IF_HYDM_RECV_P`)에 의해 처리됩니다.\n"
        "* **가맹점 준비금 한도 및 일마감 동기화**: 연동 처리가 완료(pos_proc_yn = 'Y')되면, 가맹점 마스터(`MMEMBSTB`)의 준비금 정보(`if_reserve_amt` 등)를 강제 갱신하고, 가맹점 일 마감 원장(`IFSLRETB`)의 익일 준비금(`NEXT_RESERVE_AMT`)에 동기화 반영하여 매장 POS 단말기의 기초 시재금 설정에 대입 처리되도록 제어합니다."
    )

    data["tables"]["tsm_cash_pvo_mst"] = {
        "memo": tsm_cash_pvo_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "rowid": "데이터베이스 행 고유 물리 식별자 (PK, Bigint, 자동 시퀀스)",
            "biz_cd": "예비비가 지급된 가맹점 소속 법인/사업장 코드 (2자리, 복합 인덱스)",
            "shop_cd": "예비비를 지급받은 매장 고유 코드 (2자리, 복합 인덱스)",
            "pvo_dt": "본사 예비비 지급 및 발생 처리 일자 (YYYYMMDD, 복합 인덱스)",
            "pvo_seq": "당일 예비비 지급 일련 순번 (Numeric, 복합 인덱스)",
            "prst_clsf_cd": "예비비 용도 분류 코드 (2자리, '11': 매장 영업개시 준비금, '12': 반품 환불용 준비금)",
            "pvo_amt": "지급 및 지원 처리된 실물 예비비 현금 총액 (Numeric)",
            "pvor": "본사 예비비 지급 처리 조작자/지급인 사원 ID (30자리)",
            "pwti": "예비비 수치 매장 담당자 또는 현금 수령 부서 ID (30자리)",
            "rmrk": "예비비 지급 건에 대한 구체적 한글 비고 설명 (100자리)",
            "del_yn": "해당 예비비 거래의 취소 및 삭제 처리 여부 (1자리, 'Y'/'N')",
            "rgnr_id": "최초 마스터 연동 등록자 ID (배치 프로그램 ID)",
            "rgnr_dtm": "최초 마스터 수신 등록 일시",
            "updr_id": "최종 마스터 수정자 ID",
            "updr_dtm": "최종 마스터 수정 및 완료 일시",
            "pos_proc_date": "예비비 마스터 배치 연동 일자 (YYYYMMDD, 복합 인덱스)",
            "pos_proc_seq": "예비비 배치 일자별 고유 실행 시퀀스 번호 (8자리, 복합 인덱스)",
            "pos_proc_yn": "배치 및 수신 프로시저(SUB_IF_HYDM_RECV_P) 정상 처리 완료 및 반영 여부 플래그 (1자리, 'Y': 성공, 'N': 대기/실패)",
            "pos_proc_remark": "연동 처리 중 장애 발생 시 적재되는 에러 로그 설명 (4000자리)",
            "pos_proc_create_dtime": "배치 연동 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)",
            "pos_proc_last_dtime": "배치 연동 트랜잭션 최종 갱신 완료 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "예비비 지급 마스터 수신 배치(CashReadyInterface_SqlMapper.xml) 작동 시 신규 현금 지급 건을 본 테이블에 배치 인서트합니다.",
        "memo_u": "가맹점 화면 수동 처리 또는 프로시저(SUB_IF_HYDM_RECV_P) 정상 가공 완료 시 pos_proc_yn 상태가 업데이트됩니다.",
        "memo_d": "가맹점 금전 등록 및 시재 검사(Cash Audit) 시의 핵심 감사 데이터이므로 인위적 삭제가 제한됩니다.",
        "memo_r": "매장 준비금 조회 및 변경 화면(Hq_Sysif_00002), 준비금 수신 배치(CashReadyInterface), 가맹점 마감 시재 과부족 대사 처리 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [1:1 연계 관계] 수신된 매장 영업 준비금(prst_clsf_cd='11') 및 반품 준비금(prst_clsf_cd='12') 금액을 가맹점 마스터의 실시간 준비금 잔액 정보(IF_RESERVE_AMT, IF_RETURN_RESERVE_AMT)에 갱신 마킹하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "ifslretb",
                "description": "가맹점 일 영업마감 정산 원장. [1:N 연계 관계] 가맹점의 일 영업 마감 시점에 본 테이블의 예비비 지급 명세를 대조하여, 익일 매장 준비금(NEXT_RESERVE_AMT) 상태값에 누적 설정해주기 위해 업데이트 및 조회 연계됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 예비비 지급 요청을 승인한 본사 관리자(pvor) 및 해당 가맹점의 인수 담당 점주/지배인(pwti) 계정을 실명으로 조인 매칭하기 위해 참조합니다."
            },
            {
                "table_name": "tsale_hdr",
                "description": "POS 매출 헤더 테이블. 일 영업 마감 시점의 실제 현금 매출액과 본 예비비 지급액을 대조하여 현금 과부족(Cash Discrepancy)이 발생했는지 비교 감사하기 위해 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매장 규모별 또는 브랜드별로 상한 설정된 표준 기초 준비금 한도액 및 예비비 현금 과부족 처리 예외 허용 범위 변수를 매칭 참조합니다."
            }
        ]
    }

    # 144. TSM_CASH_PVO_MST_BK MEMO AND RELATED TABLES
    tsm_cash_pvo_mst_bk_memo = (
        "### 1. 테이블 개요\n"
        "백업/임시 가맹점 예비비지급 마스터 테이블 (`TSM_CASH_PVO_MST_BK`).\n"
        "가맹점 예비비지급 실 운영 마스터 테이블(`TSM_CASH_PVO_MST`)의 과거 구버전 Tibero 레거시 데이터 보존 및 연동 테스트(Shadow Run) 목적으로 설계된 이관 백업 테이블로, 실제 영업 트랜잭션 흐름과는 분리 격리되어 작동하는 백업용 마스터 원장입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **레거시 이관 및 쉐도우 테스트 대조**: Tibero 연동 모듈(`Tibero_CashInterface_Sql.xml`)에서 신구 시스템 병행 운영 기간 동안 실시간 데이터 싱크 유무를 검증할 때 임시 셀렉트 대상(주석 해제 조작 등)으로 활용되었습니다.\n"
        "* **과거 이력 감사**: 운영 데이터베이스에 부하를 주지 않고 과거 3~5년 전의 가맹점 준비금 지원 이력을 대사하거나 정산 정합성을 검증하기 위해 보조 감사용으로 조회 사용됩니다."
    )

    data["tables"]["tsm_cash_pvo_mst_bk"] = {
        "memo": tsm_cash_pvo_mst_bk_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "백업된 가맹점 소속 법인/사업장 코드 (2자리)",
            "shop_cd": "백업된 예비비 지급 가맹점 점포 코드 (2자리)",
            "pvo_dt": "본사 예비비 지급 및 발생 처리 백업 일자 (YYYYMMDD)",
            "pvo_seq": "당일 예비비 지급 일련 순번 (Numeric)",
            "prst_clsf_cd": "예비비 용도 분류 코드 (2자리, '11': 영업개시 준비금, '12': 반품용 준비금)",
            "pvo_amt": "백업된 실물 예비비 현금 금액 (Numeric)",
            "pvor": "백업 당시의 본사 예비비 지급 처리 조작자 ID (30자리)",
            "pwti": "백업 당시의 현금 수령자 또는 매장 수령 담당자 ID (30자리)",
            "rmrk": "예비비 지급 건에 대한 백업된 비고 상세 내용 (100자리)",
            "del_yn": "해당 예비비 거래의 백업된 삭제/취소 플래그 (1자리)",
            "rgnr_id": "최초 백업 등록자 ID",
            "rgnr_dtm": "최초 백업 수신 등록 일시",
            "updr_id": "최종 백업 수정자 ID",
            "updr_dtm": "최종 백업 수정 및 완료 일시"
        },
        "memo_c": "Tibero DB 병행 연동 또는 과거 가맹점 시재 데이터 이관 작업 시 임시 데이터 적재 스크립트에 의해 인서트됩니다.",
        "memo_u": "이력용 테이블이므로 적재 이후의 수정이 거의 발생하지 않으며 정합성 보정에 의해서만 업데이트됩니다.",
        "memo_d": "과거 데이터 유실 복원용 백업 테이블이므로 정식 보존 기한이 지나기 전까지는 임의 삭제하지 않는 것이 권장됩니다.",
        "memo_r": "과거 준비금 정산 이력 정합성 대조, 구 Tibero DB 연동 모듈(Tibero_CashInterface_Sql) 이관 검증 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_cash_pvo_mst",
                "description": "가맹점 예비비 마스터. [1:1 대칭 관계] 본 백업 테이블의 기준이 되는 원천 운영 거래 원장으로, 이관 데이터 무결성 검증 시 1:1 대조 조인됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 과거 수집된 예비비 내역이 정당한 가맹점에 귀속되어 이관되었는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_cash_rcps_mst_bk",
                "description": "예비비 수납 백업 테이블. [1:1 대칭 관계] 본사에서 지급한 예비비 백업분(tsm_cash_pvo_mst_bk)이 가맹점에서 누락 없이 수납 처리되었는지 쌍방 대조하는 백업 매칭 테이블입니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 테이블. 백업 이력 내에 존재하는 과거 지급자(pvor) 및 수령자(pwti)의 사원 ID 유효성을 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."
            }
        ]
    }

    # 145. TSM_CASH_RCPS_MST MEMO AND RELATED TABLES
    tsm_cash_rcps_mst_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 예비비/현금 수납 및 입금 정보 마스터 테이블 (`TSM_CASH_RCPS_MST`).\n"
        "가맹점 POS 단말기 또는 본사 수납 관리자 화면에서 예비비의 실제 수령 확인 및 수납금 입금 처리( remittence / cash receipt ) 시 발생하는 정보(사업장코드 `BIZ_CD`, 매장코드 `SHOP_CD`, 발생일자 `OCCU_DT`, 구분코드 `PRST_CLSF_CD` [11: 영업준비금, 12: 반품준비금, 21: 일반입금, 70: 가맹점 송금 등], 수납액 `RCPS_AMT`, 수납인 `RCPSP`, 수납증 인쇄여부 `RCPS_PRNT_YN`, 본사확인여부 `COFM_YN`)를 저장하는 핵심 가맹점 재무 수금 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **예비비 수납 및 송금 확인**: 가맹점 POS에서 예비비 발생에 대해 실물 수납(`Pos_CashInterface_Sql.xml`)을 확정하면 본 테이블에 등록되며 본사 승인 컬럼(`cofm_yn = 'Y'`)으로 처리됩니다. 또한 매장이 일일 영업 매출을 마감하여 본사 통장에 실송금 처리 시 송금 액수가 인서트되며, 본사 확인자 ID(`chkr_id`)가 승인 처리합니다.\n"
        "* **본사 ERP 재무 회계 연동 (`SUB_IF_HYDM_SEND_P` 프로시저)**: 본 테이블에 기록된 일일 송금 및 수납 처리 명세는 송금 전송 연동 전문 프로시저(`SUB_IF_IF_HYDM_SEND_P` [전문 ID: `IF_FB_001` - 일송금])를 통해 최종 ERP 회계 장부로 인터페이스 전송되어 전사 원장과 대사 싱크를 마칩니다."
    )

    data["tables"]["tsm_cash_rcps_mst"] = {
        "memo": tsm_cash_rcps_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "수납이 귀속된 본사/법인 사업장 고유 코드 (2자리, PK)",
            "shop_cd": "수납/송금 처리가 수행된 가맹점 매장 코드 (2자리, PK)",
            "occu_dt": "수납 및 입금 발생 일자 (YYYYMMDD, PK)",
            "prst_clsf_cd": "수납 및 예비비 상세 용도 구분 코드 (2자리, PK, '11': 준비금, '12': 반품준비금, '21': 일반입금, '51': 준비금반환, '70': 송금)",
            "rcps_seq": "당일 수납 및 입금 발생 고유 일련 순번 (Numeric, PK)",
            "rcps_amt": "실제 입금 및 수납 처리된 실물 현금 총액 (Numeric)",
            "rcpsp": "수납 처리 조작자/입금자 사원 ID (30자리)",
            "rmrk": "수납 명세에 관한 상세 비고 설명 문구 (200자리)",
            "rcps_prnt_yn": "가맹점 수납 처리 완료 후 영수증/수납증 출력 여부 플래그 (1자리, 'Y'/'N')",
            "prnt_dtm": "수납증 영수증 최종 출력 일시",
            "chkr_id": "수납 처리를 대조 및 최종 승인한 본사 재경 담당자 ID (30자리)",
            "cofm_yn": "본사 수납 데이터 승인 및 최종 확정 여부 플래그 (1자리, 'Y': 확정완료, 'N': 승인대기)",
            "cofm_dtm": "본사 최종 확정 및 승인 처리 일시",
            "rgnr_id": "최초 등록자 ID (POS 사번/백오프 사용자 사번)",
            "rgnr_dtm": "최초 등록 처리 일시",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 처리 일시",
            "pos_send_seq": "ERP 전송 배치 기동을 위한 전문 송신 고유 일련번호 (8자리, PK)",
            "pos_send_yn": "ERP 일송금 전송(SUB_IF_HYDM_SEND_P) 연동 완료 여부 플래그 (1자리, 'Y': 전송성공, 'N': 미전송/대기)",
            "pos_send_remark": "ERP 전송 실패 시 적재되는 EAI 통신 예외 에러 메시지 (4000자리)",
            "pos_send_create_dtime": "ERP 전송 전문 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "가맹점 POS 영업 준비금 수령(Pos_CashInterface_Sql.xml) 또는 백오프 가맹점 준비금 승인 시 신규 수납 로우가 인서트됩니다.",
        "memo_u": "본사 재경팀의 일일 수금 승인 대사 처리 및 ERP 전송 데몬(SUB_IF_HYDM_SEND_P) 정상 수행 완료 시 업데이트됩니다.",
        "memo_d": "가맹점 회계 마감 및 시재 과부족 원장 대사 대사 검증의 원천 영수증이므로 물리 삭제가 불허됩니다.",
        "memo_r": "가맹점 수납 조회 및 확인(Hq_Sysif_00002), ERP 일송금 전문 송신(SUB_IF_HYDM_SEND_P), 가맹점 일영업마감 대사 및 준비금 한도 정산 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_cash_pvo_mst",
                "description": "가맹점 예비비 마스터. [1:1 대칭 매칭 관계] 본사 지급 건(tsm_cash_pvo_mst)에 대응하여 가맹점 POS에서 실제 수령 확인 및 수납처리(insertCashRcps)를 수행할 때 지급 이력 상태를 동시 업데이트(updatePvo)하기 위해 상호 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [1:1 연계 관계] 가맹점 POS에서 수납 처리된 금액을 기준으로 가맹점 마스터의 실시간 준비금 잔액 상태(IF_RESERVE_AMT, IF_RETURN_RESERVE_AMT)를 보정 업데이트하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "ifslretb",
                "description": "가맹점 일 영업마감 정산 원장. 가맹점 마감 시 실제 금고 시재 수납 금액과 본사 통장에 송금 처리된 전송 금액의 대사 내역을 최종 검증하기 위해 조회 조인됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 마스터 테이블. 예비비를 인수 수납한 현장 매장 담당자 ID와 수령 내역을 최종 확인한 지배인/본사 재경 Checker 사번을 실명 조인 매칭하기 위해 참조합니다."
            },
            {
                "table_name": "tsale_hdr",
                "description": "POS 매출 헤더 테이블. 일 영업 마감 시점의 실제 현금 매출액과 본 예비비 지급액을 대조하여 현금 과부족(Cash Discrepancy)이 발생했는지 비교 감사하기 위해 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 준비금 반환 및 송금 시각 통제 범위 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 146. TSM_CASH_RCPS_MST_BK MEMO AND RELATED TABLES
    tsm_cash_rcps_mst_bk_memo = (
        "### 1. 테이블 개요\n"
        "백업/임시 가맹점 예비비수납 및 입금 마스터 테이블 (`TSM_CASH_RCPS_MST_BK`).\n"
        "가맹점 예비비수납 및 입금 실 운영 테이블(`TSM_CASH_RCPS_MST`)의 과거 구버전 Tibero 레거시 데이터 백업 및 연동 테스트(Shadow Run) 목적으로 사용되는 백업용 이력 테이블로, 실제 시재금 정산 영업에는 직접 영향을 주지 않는 보조 아카이빙 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **레거시 이관 및 쉐도우 테스트 대조**: Tibero 연동 모듈(`Tibero_CashInterface_Sql.xml`)에서 가맹점 수납 내역 조회 로직의 정합성을 검증할 때 임시 데이터 소스로 매칭 활용되었습니다.\n"
        "* **과거 이력 감사**: 가맹점 준비금 반환 및 수금 확인 이력을 백업 본에서 비교 조인하여 이관 누락이나 데이터 왜곡 유무를 교차 검증하는 감사 자료로 사용됩니다."
    )

    data["tables"]["tsm_cash_rcps_mst_bk"] = {
        "memo": tsm_cash_rcps_mst_bk_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "백업된 가맹점 소속 법인/사업장 코드 (2자리)",
            "shop_cd": "백업된 수납/송금 발생 가맹점 매장 코드 (2자리)",
            "occu_dt": "백업된 수납 및 입금 발생 일자 (YYYYMMDD)",
            "prst_clsf_cd": "수납 구분 코드 (2자리, '11': 준비금, '12': 반품준비금, '70': 송금 등)",
            "rcps_seq": "당일 수납 및 입금 발생 고유 일련 순번 (Numeric)",
            "rcps_amt": "백업된 실물 수납/송금 처리 현금 총액 (Numeric)",
            "rcpsp": "백업 당시의 수납 처리 조작자 ID (30자리)",
            "rmrk": "백업된 비고 상세 내용 (200자리)",
            "rcps_prnt_yn": "백업된 수납증 출력 여부 플래그 (1자리)",
            "prnt_dtm": "백업된 수납증 최종 출력 일시",
            "chkr_id": "백업 당시의 수납 승인자 ID (30자리)",
            "cofm_yn": "백업 당시의 본사 승인 확정 플래그 (1자리)",
            "cofm_dtm": "백업 당시의 본사 승인 처리 일시",
            "rgnr_id": "최초 백업 등록자 ID",
            "rgnr_dtm": "최초 백업 수신 등록 일시",
            "updr_id": "최종 백업 수정자 ID",
            "updr_dtm": "최종 백업 수정 및 완료 일시"
        },
        "memo_c": "과거 Tibero DB 데이터 이관 작업 또는 백업 동기화 스크립트 실행 시 백업 레코드가 인서트됩니다.",
        "memo_u": "이력용 테이블이므로 적재 이후의 수정이 거의 발생하지 않으며 데이터 정비 시에만 정정 처리됩니다.",
        "memo_d": "데이터 복원 및 소급 감사용 백업 테이블이므로 정식 보존 기한이 경과하기 전까지는 삭제가 제한됩니다.",
        "memo_r": "구 Tibero DB 연동 모듈(Tibero_CashInterface_Sql) 이관 검증 및 과거 가맹점 입금 대사 이력 대조 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_cash_rcps_mst",
                "description": "가맹점 예비비 수납 마스터. [1:1 대칭 관계] 본 백업 테이블의 기준이 되는 원천 운영 거래 원장으로, 이관 데이터 무결성 검증 시 1:1 대조 조인됩니다."
            },
            {
                "table_name": "tsm_cash_pvo_mst_bk",
                "description": "예비비 지급 백업 테이블. [1:1 대칭 관계] 백업된 본사 지급 내역(tsm_cash_pvo_mst_bk)과 가맹점 수납 내역(tsm_cash_rcps_mst_bk)을 조인 대조하여 이관 누락이 없는지 감사 정합성을 매칭 검증하기 위해 연계됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 과거 수집된 수납 내역이 정당한 가맹점에 귀속되어 이관되었는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 테이블. 백업 이력 내에 존재하는 과거 수납자(rcpsp) 및 확인자(chkr_id)의 사원 ID 유효성을 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."
            }
        ]
    }

    # 147. TSM_CTY_BUY_DTL MEMO AND RELATED TABLES
    tsm_cty_buy_dtl_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 원부재료/물품 매입 상세 원장 테이블 (`TSM_CTY_BUY_DTL`).\n"
        "가맹점/점포에서 발주 및 사입 처리된 개별 원부자재, 물품 및 부재료의 품목별 매입 명세(사업장코드 `BIZ_CD`, 매장코드 `SHOP_CD`, 매입관리번호 `BUY_MGMT_NO`, 매입일자 `BUY_DT`, 매입전표순번 `BUY_SLIP_SEQ`, 물품코드 `CTY_CD`, 물품명 `CTY_NM`, 매입수량 `QTY`, 매입단가 `BUY_UNP`, 매입공급가 `BUY_SUPR_PRIC`, 매입부가세 `BUY_VAT`, 합계금액 `SUM_AMT`)를 일별 수집 및 임시 보관하는 연동 상세 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **일별 물품 매입 상세 적재**: 매장 시스템에서 일별로 납품받은 물품 인수증 전표 상세를 취합하여 백오프 매입 처리 모듈이 본 테이블에 품목별 수량과 공급가액을 인서트합니다.\n"
        "* **본사 ERP 매입 송신 연동 (`ObslInterface` 배치)**: 매입 송신 배치 스케줄러(Job `ObslInterface`)가 실행되면, 헤더 원장(`TSM_CTY_BUY_MST`)과 조인 및 송금 전송 프로시저(`SUB_IF_HYDM_SEND_P` [인터페이스 ID: `'OBSL'`])를 작동시켜 `pos_send_yn = 'N'` 상태의 매입 상세 로우들을 ERP 매입 장부로 전송하고 송신 완료 상태(`pos_send_yn = 'Y'`)로 갱신하여 정산 및 매입 단가 대사를 종결합니다."
    )

    data["tables"]["tsm_cty_buy_dtl"] = {
        "memo": tsm_cty_buy_dtl_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "매입이 소속된 법인/사업장 구분 코드 (2자리, PK)",
            "shop_cd": "매입 거래가 일어난 가맹점 매장 코드 (2자리, PK)",
            "buy_mgmt_no": "매입 거래 건별로 발급된 고유 매입관리번호 (20자리, PK)",
            "buy_dt": "실제 물품 매입 및 납품 완료 일자 (YYYYMMDD, PK)",
            "buy_slip_seq": "매입전표 내 개별 품목별 일련 순번 (Numeric, PK)",
            "cty_cd": "본사 표준 물품/원부자재 고유 식별 코드 (13자리)",
            "cty_nm": "물품/원부재료 명칭 (100자리)",
            "qty": "매입 및 입고 처리된 품목 수량 (Numeric, size=15,3)",
            "buy_unp": "매입 품목 단위당 단가 수치 (Numeric, size=16,2)",
            "buy_supr_pric": "해당 품목의 순수 매입 공급가액 (Numeric)",
            "buy_vat": "해당 품목 매입 시 부과된 매입 부가가치세 (Numeric)",
            "sum_amt": "공급가와 부가세를 합산한 품목별 총 매입액 (Numeric)",
            "taxn_type_cd": "매입 품목 과세 유형 구분자 (1자리, '0': 면세물품, '1': 과세물품)",
            "del_yn": "해당 매입 품목의 거래 취소 및 삭제 여부 플래그 (1자리, 'Y'/'N')",
            "rgnr_id": "최초 등록자 ID (매입 등록자/배치 프로그램 ID)",
            "rgnr_dtm": "최초 매입 등록 일시",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 일시",
            "pos_send_seq": "ERP 전송 배치 기동을 위한 전문 송신 고유 일련번호 (8자리, PK)",
            "pos_send_yn": "ERP 매입 송신(SUB_IF_HYDM_SEND_P) 연동 완료 여부 플래그 (1자리, 'Y': 전송성공, 'N': 미전송/대기)",
            "pos_send_remark": "ERP 매입 전송 실패 시 적재되는 EAI 통신 예외 에러 메시지 (4000자리)",
            "pos_send_create_dtime": "ERP 전송 전문 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "일별 매장 사입 및 매입 등록 모듈에 의해 신규 매입 상세 내역이 본 테이블에 인서트됩니다.",
        "memo_u": "ERP 매입 전송 배치(ObslInterface_SqlMapper.xml) 정상 가동에 의해 pos_send_yn 플래그가 최종 업데이트됩니다.",
        "memo_d": "가맹점 원부재료 수불 대사 및 본사 물류 정산 매입 세금계산서 발행의 증적이므로 데이터 삭제가 제한됩니다.",
        "memo_r": "매장 매입 상세 내역 조회, ERP 일매입 전문 송신(ObslInterface), 가맹점 물품 재고 수불 분석 및 원가율 시뮬레이션 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_cty_buy_mst",
                "description": "매입 헤더 마스터. [N:1 부모 관계] 가맹점 매입 거래 단위별 전체 요약 정보(매입합계금액, 매입사코드, 세금구분 등)를 관리하는 부모 헤더 테이블입니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "상품 마스터 테이블. 매입된 원부자재/물품의 상품 분류 및 품명 표준 정합성을 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 매입 내역이 올라온 실물 가맹점의 브랜드 및 운영 주체를 분리 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "if_sedpsvtb",
                "description": "인터페이스 송신 이력 테이블. [1:1 매칭 감사 관계] 매입 연동 배치(OBSL)가 ERP로 상세 내역을 송신한 전체 레코드 무결성 및 통신 처리 결과를 감사 기록합니다."
            },
            {
                "table_name": "tsale_dtl",
                "description": "POS 매출 상세 테이블. 가맹점의 원부자재 매입량 대비 실제 POS 상품 판매 수량을 대조 분석하여 재고 소진율 및 원부재료 손실율(Loss Rate)을 시뮬레이션 계산할 때 대조 조인됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매입 단가 계산 시 부가세 단수 처리 절사 옵션 정책을 매칭 참조합니다."
            }
        ]
    }

    # 148. TSM_CTY_BUY_DTL_BK MEMO AND RELATED TABLES
    tsm_cty_buy_dtl_bk_memo = (
        "### 1. 테이블 개요\n"
        "백업/임시 가맹점 원부재료/물품 매입 상세 원장 테이블 (`TSM_CTY_BUY_DTL_BK`).\n"
        "가맹점 매입 상세 원장 실 운영 테이블(`TSM_CTY_BUY_DTL`)의 과거 구버전 Tibero 레거시 데이터 백업 및 연동 테스트(Shadow Run) 목적으로 사용되는 백업용 이력 테이블로, 실제 매입 집계 및 EAI 전송 영업 프로세스와는 분리 격리된 백업 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **레거시 이관 및 쉐도우 테스트 대조**: Tibero 연동 모듈(`ObslInterface_Tibero_SqlMapper.xml`)에서 가맹점 매입 상세 수집 쿼리의 정합성을 검증할 때 임시 데이터 인서트/셀렉트 대상으로 활용되었습니다.\n"
        "* **과거 이력 감사**: 과거 특정 연도의 품목별 매입 수량과 공급가액 백업 데이터를 비교 대조하여, 데이터 이관 작업 시의 손실이나 단가 오차를 교차 검증하는 감사 자료로 사용됩니다."
    )

    data["tables"]["tsm_cty_buy_dtl_bk"] = {
        "memo": tsm_cty_buy_dtl_bk_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "백업된 가맹점 소속 법인/사업장 코드 (2자리)",
            "shop_cd": "백업된 매입 발생 가맹점 매장 코드 (2자리)",
            "buy_mgmt_no": "백업된 고유 매입관리번호 (20자리)",
            "buy_dt": "백업된 물품 매입 및 납품 일자 (YYYYMMDD)",
            "buy_slip_seq": "매입전표 내 개별 품목별 백업된 일련 순번 (Numeric)",
            "cty_cd": "백업된 본사 표준 물품 식별 코드 (13자리)",
            "cty_nm": "백업된 물품 명칭 (100자리)",
            "qty": "백업된 매입 및 입고 수량 (Numeric)",
            "buy_unp": "백업된 매입 단가 수치 (Numeric)",
            "buy_supr_pric": "백업된 순수 매입 공급가액 (Numeric)",
            "buy_vat": "백업된 매입 부가가치세 (Numeric)",
            "sum_amt": "백업된 총 매입액 합계금액 (Numeric)",
            "taxn_type_cd": "백업된 매입 품목 과세 구분자 (1자리)",
            "del_yn": "해당 매입 품목의 백업된 삭제/취소 플래그 (1자리)",
            "rgnr_id": "최초 백업 등록자 ID",
            "rgnr_dtm": "최초 백업 수신 등록 일시",
            "updr_id": "최종 백업 수정자 ID",
            "updr_dtm": "최종 백업 수정 및 완료 일시"
        },
        "memo_c": "과거 Tibero DB 데이터 이관 작업 또는 백업 동기화 스크립트 실행 시 백업 레코드가 인서트됩니다.",
        "memo_u": "이력용 테이블이므로 적재 이후의 수정이 거의 발생하지 않으며 정합성 보정에 의해서만 업데이트됩니다.",
        "memo_d": "데이터 복원 및 소급 감사용 백업 테이블이므로 정식 보존 기한이 경과하기 전까지는 삭제가 제한됩니다.",
        "memo_r": "구 Tibero DB 연동 매퍼(ObslInterface_Tibero_SqlMapper) 이관 검증 및 과거 가맹점 매입 대사 이력 대조 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_cty_buy_dtl",
                "description": "가맹점 매입 상세 마스터. [1:1 대칭 관계] 본 백업 테이블의 기준이 되는 원천 운영 거래 원장으로, 이관 데이터 무결성 검증 시 1:1 대조 조인됩니다."
            },
            {
                "table_name": "tsm_cty_buy_mst_bk",
                "description": "매입 헤더 백업 테이블. [N:1 관계] 백업된 개별 매입 거래 단위의 요약 정보를 관리하는 부모 헤더 백업 테이블입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 과거 수집된 매입 내역이 정당한 가맹점에 귀속되어 이관되었는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tgoodstb",
                "description": "상품 마스터 테이블. 백업 이력 내의 과거 매입 물품 코드(cty_cd)가 표준 상품 규격 코드와 일치하는지 무결성 검사 시 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."
            }
        ]
    }

    # 149. TSM_CTY_BUY_MST MEMO AND RELATED TABLES
    tsm_cty_buy_mst_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 원부재료/물품 매입 헤더 원장 테이블 (`TSM_CTY_BUY_MST`).\n"
        "가맹점 점포에서 발주 사입된 일별 원부자재, 물품 매입 거래의 총괄 요약 전표 정보(사업장코드 `BIZ_CD`, 매장코드 `SHOP_CD`, 매입관리번호 `BUY_MGMT_NO`, 매입일자 `BUY_DT`, 매입거래처코드 `BYGD_CD`, 공급가액 합계 `BUY_SUPR_PRIC`, 부가가치세 합계 `BUY_VAT`, 총 매입합계금액 `SUM_AMT`, 본사확인여부 `COFM_YN`, 계정코드 `ACC_CD`, 전표생성여부 `SLIP_CREA_YN`)를 저장 및 송신 제어하는 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **매입 총괄 요약 원장 관리**: 가맹점 매입 처리 모듈에서 매입 인수증에 대한 검수를 거쳐 수합된 일별 거래 요약 명세를 본 테이블에 저장하며, 본사 재경팀의 감사 승인 완료 시 `cofm_yn = 'Y'` 및 확인자 ID(`fxrv_id`)가 업데이트됩니다.\n"
        "* **ERP 재무 전표 연동 (`ObslInterface` 배치)**: 매입 송신 배치 스케줄러(Job `ObslInterface`)가 구동되면, 미전송 상태(`pos_send_yn = 'N'`)의 매입 헤더 건들을 수집한 뒤 송신 연동 프로시저(`SUB_IF_HYDM_SEND_P` [전문 ID: `'OBSL'`])를 실행하여 ERP의 매입 채무 장부 및 재무 회계 모듈에 자동으로 싱크 전송하고 전송 완료 상태(`pos_send_yn = 'Y'`)로 업데이트하여 회계 전표 처리를 마칩니다."
    )

    data["tables"]["tsm_cty_buy_mst"] = {
        "memo": tsm_cty_buy_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "매입이 소속된 법인/사업장 구분 코드 (2자리, PK)",
            "shop_cd": "매입 거래가 일어난 가맹점 매장 코드 (2자리, PK)",
            "buy_mgmt_no": "매입 거래 건별로 발급된 고유 매입관리번호 (20자리, PK)",
            "buy_dt": "실제 물품 매입 및 납품 완료 일자 (YYYYMMDD, PK)",
            "bygd_cd": "물품을 납품한 매입처/공급 사업자 고유 코드 (10자리)",
            "buy_supr_pric": "해당 매입 전표의 총 순수 공급가액 합계 (Numeric)",
            "buy_vat": "해당 매입 전표의 총 부가가치세 합계 (Numeric)",
            "sum_amt": "공급가와 부가세를 합산한 전표 총 매입액 합계 (Numeric)",
            "cofm_yn": "본사 수납/매입 데이터 승인 및 최종 확정 여부 플래그 (1자리, 'Y': 승인확정, 'N': 승인대기)",
            "fxrv_id": "매입 전표 내역을 대조하여 최종 확인 승인한 본사 재경 담당자 ID (30자리)",
            "inp_clsf_cd": "매입 전표 입력 방식 구분 코드 (1자리, '1': POS 자동 전송, '2': 백오프스 수동 등록 등)",
            "tax_rcv_clsf_cd": "세금계산서 발행 및 수취 방식 구분 코드 (1자리, SM045)",
            "acc_cd": "회계 전표 매핑용 본사 계정과목 표준 코드 (200자리, SM055)",
            "vat_cd": "세율 형태에 따른 부가세 구분 코드 (1자리, SM056)",
            "rmrk": "매입 전표 전체에 대한 한글 비고 설명문 (200자리)",
            "del_yn": "해당 매입 전표 전체의 취소 및 삭제 여부 플래그 (1자리, 'Y'/'N')",
            "if_slip_serl": "ERP 연동 시 매핑용 인터페이스 전표 일련번호 (10자리)",
            "slip_crea_yn": "ERP 회계 전표 자동 생성 및 기재 여부 플래그 (1자리, 'Y': 생성완료, 'N': 미생성)",
            "rgnr_id": "최초 등록자 ID (매입 전표 최초 작성자)",
            "rgnr_dtm": "최초 매입 등록 일시",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 일시",
            "slip_dt": "ERP 전표 처리 기준 일자 (YYYYMMDD)",
            "pos_send_seq": "ERP 전송 배치 기동을 위한 전문 송신 고유 일련번호 (8자리, PK)",
            "pos_send_yn": "ERP 매입 송신(SUB_IF_HYDM_SEND_P) 연동 완료 여부 플래그 (1자리, 'Y': 전송성공, 'N': 미전송/대기)",
            "pos_send_remark": "ERP 매입 전송 실패 시 적재되는 EAI 통신 예외 에러 메시지 (4000자리)",
            "pos_send_create_dtime": "ERP 전송 전문 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "일별 가맹점 사입 검수 완료 및 매입 거래 마감 시 요약 헤더가 본 테이블에 인서트됩니다.",
        "memo_u": "본사 재경팀의 매입 승인 확정 처리 또는 ERP 매입 전송 배치(ObslInterface_SqlMapper.xml) 성공 시 업데이트됩니다.",
        "memo_d": "ERP 매입 채무 장부 및 정산 매입 대사의 증적이므로 물리적 테이블 삭제가 통제됩니다.",
        "memo_r": "가맹점 매입 총괄 현황 조회, ERP 일매입 전문 송신(ObslInterface), 가맹점 물품 재고 수불 분석 및 공급업체 세금계산서 발행 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_cty_buy_dtl",
                "description": "매입 상세 테이블. [1:N 자식 관계] 해당 매입 관리 전표 내에 포함된 품목별 구체적 매입 수량과 공급가액, 부가세 상세를 연계 관리하는 자식 테이블입니다."
            },
            {
                "table_name": "tvendor_master",
                "description": "거래처 마스터 테이블. [N:1 관계] 물품을 사입/납품해 준 외부 유통 벤더사 및 공급 사업체의 기본 정보를 조회하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 매입 전표가 귀속되는 실 가맹점 명칭 및 세부 관리 속성을 매칭하기 위해 참조합니다."
            },
            {
                "table_name": "if_sedpsvtb",
                "description": "인터페이스 송신 이력 테이블. [1:1 매칭 감사 관계] 매입 송신 배치(OBSL)가 ERP로 전표 내역을 보낸 결과를 기록 관리합니다."
            },
            {
                "table_name": "muserstb",
                "description": "시스템 사용자 테이블. 매장에서 수동 입력 및 인수한 매입 건을 확인/확정한 본사 관리자 사번의 실명을 조인 매칭하기 위해 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 일별 매입 마감 승인 시간 통제 룰 및 매입 전표 자동 생성 옵션 정책을 매칭 참조합니다."
            }
        ]
    }

    # 150. TSM_CTY_BUY_MST_BK MEMO AND RELATED TABLES
    tsm_cty_buy_mst_bk_memo = (
        "### 1. 테이블 개요\n"
        "백업/임시 가맹점 원부재료/물품 매입 헤더 원장 테이블 (`TSM_CTY_BUY_MST_BK`).\n"
        "가맹점 매입 헤더 원장 실 운영 테이블(`TSM_CTY_BUY_MST`)의 과거 구버전 Tibero 레거시 데이터 백업 및 연동 테스트(Shadow Run) 목적으로 설계된 이관 백업 테이블로, 실제 매입 회계 마감 및 기재 프로세스에는 관여하지 않는 아카이브성 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **레거시 이관 및 쉐도우 테스트 대조**: Tibero 연동 매퍼(`ObslInterface_Tibero_SqlMapper.xml`)에서 가맹점 매입 정보 수집 로직의 정합성을 검증할 때 임시 데이터 인서트/셀렉트 대상으로 활용되었습니다.\n"
        "* **과거 이력 감사**: 과거 특정 연도의 매입 거래 건별 총합금액과 세금 계산서 발행 이력을 백업 본에서 비교 조인하여, 데이터 마이그레이션 도중 누락된 매입 전표가 있는지 여부를 교차 검증하는 감사 자료로 사용됩니다."
    )

    data["tables"]["tsm_cty_buy_mst_bk"] = {
        "memo": tsm_cty_buy_mst_bk_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "백업된 가맹점 소속 법인/사업장 코드 (2자리)",
            "shop_cd": "백업된 매입 발생 가맹점 매장 코드 (2자리)",
            "buy_mgmt_no": "백업된 고유 매입관리번호 (20자리)",
            "buy_dt": "백업된 물품 매입 및 납품 일자 (YYYYMMDD)",
            "bygd_cd": "백업된 매입 거래처/공급 사업자 코드 (10자리)",
            "buy_supr_pric": "백업된 총 매입 공급가액 합계 (Numeric)",
            "buy_vat": "백업된 총 매입 부가가치세 합계 (Numeric)",
            "sum_amt": "백업된 총 매입 합계금액 (Numeric)",
            "cofm_yn": "백업 당시의 본사 승인 확정 플래그 (1자리)",
            "fxrv_id": "백업 당시의 매입 최종 승인자 ID (30자리)",
            "inp_clsf_cd": "백업 당시의 매입 전표 입력 방식 구분자 (1자리)",
            "tax_rcv_clsf_cd": "백업 당시의 세금계산서 발행 구분 코드 (1자리)",
            "acc_cd": "백업 당시의 계정과목 코드 (200자리)",
            "vat_cd": "백업 당시의 부가세 구분 코드 (1자리)",
            "rmrk": "백업된 매입 비고 설명 (200자리)",
            "del_yn": "해당 매입 전표의 백업된 삭제/취소 플래그 (1자리)",
            "if_slip_serl": "백업 당시의 인터페이스 전표 일련번호 (10자리)",
            "slip_crea_yn": "백업 당시의 ERP 회계 전표 자동 생성 여부 (1자리)",
            "rgnr_id": "최초 백업 등록자 ID",
            "rgnr_dtm": "최초 백업 수신 등록 일시",
            "updr_id": "최종 백업 수정자 ID",
            "updr_dtm": "최종 백업 수정 및 완료 일시",
            "slip_dt": "백업 당시의 ERP 전표 처리 기준 일자 (YYYYMMDD)"
        },
        "memo_c": "과거 Tibero DB 데이터 이관 작업 또는 백업 동기화 스크립트 실행 시 백업 레코드가 인서트됩니다.",
        "memo_u": "이력용 테이블이므로 적재 이후의 수정이 거의 발생하지 않으며 데이터 정비 시에만 정정 처리됩니다.",
        "memo_d": "데이터 복원 및 소급 감사용 백업 테이블이므로 정식 보존 기한이 경과하기 전까지는 삭제가 제한됩니다.",
        "memo_r": "구 Tibero DB 연동 매퍼(ObslInterface_Tibero_SqlMapper) 이관 검증 및 과거 가맹점 매입 대사 이력 대조 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_cty_buy_mst",
                "description": "가맹점 매입 헤더 마스터. [1:1 대칭 관계] 본 백업 테이블의 기준이 되는 원천 운영 거래 원장으로, 이관 데이터 무결성 검증 시 1:1 대조 조인됩니다."
            },
            {
                "table_name": "tsm_cty_buy_dtl_bk",
                "description": "매입 상세 백업 테이블. [1:N 관계] 백업된 개별 매입 거래 내역 내에 포함된 품목별 구체적 매입 상세 목록을 관리하는 자식 테이블입니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 과거 수집된 매입 내역이 정당한 가맹점에 귀속되어 이관되었는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tvendor_master",
                "description": "거래처 마스터 테이블. 백업 이력 내의 과거 매입 거래처가 실 거래처 마스터 정보와 일치하는지 정합성 검사 시 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."
            }
        ]
    }

    # 151. TSM_CUST_MST MEMO AND RELATED TABLES
    tsm_cust_mst_memo = (
        "### 1. 테이블 개요\n"
        "ERP 거래처 마스터 인터페이스 원장 테이블 (`TSM_CUST_MST`).\n"
        "본사 ERP 시스템으로부터 전사 유통 공급업체 및 사입 거래처 마스터(거래처코드 `CUST_CD`, 거래처명 `CUST_NM`, 거래처구분 `CUST_CLSF_CD`, 사업자등록번호 `BIZU_RGN_NO`, 대표번호 `CUST_TEL_NO`, 대표자명 `REPN_NM`, 담당자명 `CRGR_NM`, 담당자연락처, 이메일, 주소, 업태, 종목 등)를 EAI 연동 인터페이스를 통해 배치 수신 보관하는 마스터 버퍼 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **전사 거래처 마스터 연동 수신**: 거래처 수신 배치 스케줄러(Job `CustInterface`)가 기동되면 ERP의 거래처 데이터가 본 테이블(`TSM_CUST_MST`)에 인서트된 후 수신 완결 프로시저(`SUB_IF_HYDM_RECV_P` [전문 ID: `'IF_FB_201'`])를 실행합니다.\n"
        "* **본사 매입처 데이터 싱크 및 유효성 정합**: 수신 처리가 성공(pos_proc_yn = 'Y')하면 본사의 정적 물류/구매 거래처 마스터 테이블(`TVENDOR_MASTER` / `TCOMP_MST` 등)에 실시간 병합되어, 가맹점 물품 사입 및 공급 전표 검수 시의 승인 및 조회 대사 기준 데이터로 배포 적용됩니다."
    )

    data["tables"]["tsm_cust_mst"] = {
        "memo": tsm_cust_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "rowid": "데이터베이스 행 고유 물리적 식별자 (PK, Bigint, 자동 시퀀스)",
            "cust_cd": "ERP에서 수신된 10자리 고유 거래처 코드 (복합 인덱스)",
            "cust_nm": "유통 공급 사업체/거래처 공식 상호명 (100자리)",
            "cust_clsf_cd": "거래처 업종/속성별 구분 코드 (2자리, SM035)",
            "bizu_rgn_no": "세무 신고용 10자리 사업자등록번호",
            "cust_tel_no": "거래처 대표 전화번호 (30자리)",
            "repn_nm": "거래처 대표자 한글 실명 (50자리)",
            "crgr_nm": "정산 및 납품 실무 담당자 한글 실명 (50자리)",
            "crgr_hp1": "담당자 휴대폰 앞 3자리",
            "crgr_hp2": "담당자 휴대폰 중간 3/4자리",
            "crgr_hp3": "담당자 휴대폰 끝 4자리",
            "crgr_eml_frt": "담당자 이메일 계정 ID 앞부분 (20자리)",
            "crgr_eml_rear": "담당자 이메일 도메인 주소 뒷부분 (30자리)",
            "zip": "거래처 소재지 우편번호 (6자리)",
            "addr1": "거래처 기본 소재지 도로명/지번 주소 (100자리)",
            "addr2": "거래처 상세 건물/호실 주소 (100자리)",
            "bzcn": "사업자등록증 상 기재된 공식 업태 종류 (100자리)",
            "aitm": "사업자등록증 상 기재된 공식 업종 종목 명칭 (100자리)",
            "use_yn": "해당 거래처의 거래 가동 여부 플래그 (1자리, 'Y': 가동, 'N': 일시중지/폐업)",
            "pos_proc_date": "거래처 마스터 배치 연동 일자 (YYYYMMDD, 복합 인덱스)",
            "pos_proc_seq": "거래처 배치 일자별 고유 실행 시퀀스 번호 (8자리, 복합 인덱스)",
            "pos_proc_yn": "배치 및 수신 프로시저(SUB_IF_HYDM_RECV_P) 정상 처리 완료 및 반영 여부 플래그 (1자리, 'Y': 성공, 'N': 대기/실패)",
            "pos_proc_remark": "연동 처리 중 장애나 데이터 이상 발생 시 적재되는 예외 설명 메시지 (4000자리)",
            "pos_proc_create_dtime": "배치 연동 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)",
            "pos_proc_last_dtime": "배치 연동 트랜잭션 최종 갱신 완료 일시 (YYYYMMDDHH24MISS)",
            "repn_hp1": "대표자 휴대폰 앞 3자리",
            "repn_hp2": "대표자 휴대폰 중간 3/4자리",
            "repn_hp3": "대표자 휴대폰 끝 4자리"
        },
        "memo_c": "거래처 마스터 수신 배치(CustInterface_SqlMapper.xml)가 실행될 때 본 테이블에 배치 인서트합니다.",
        "memo_u": "수신 가공 프로시저(SUB_IF_HYDM_RECV_P)의 처리 상태에 따라 pos_proc_yn 플래그가 최종 업데이트됩니다.",
        "memo_d": "매장 매입 거래 이력 조회 및 부재료 정산 세무 증빙의 기준 데이터이므로 데이터 임의 삭제가 금지됩니다.",
        "memo_r": "구매 거래처 목록 조회, 거래처 마스터 수신 배치(CustInterface), 매입 전표 검수 및 사입비 정산 조회 시 기준 데이터로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tvendor_master",
                "description": "본사 거래처 마스터. [1:1 매칭 관계] 수신된 최신 거래처 정보(사업자 번호, 주소, 대표자 연락처 등)를 가맹점 물품 공급처 및 본사 매입 거래처 마스터에 동기화 반영하기 위해 참조 조인됩니다."
            },
            {
                "table_name": "tsm_cty_buy_mst",
                "description": "매입 헤더 테이블. 매장 물품 매입 거래에서 전표에 기재된 매입처(bygd_cd) 정보가 유효하게 등록된 거래처인지 확인하고, 거래처 연락처 및 세무 신고용 사업자 번호를 매칭하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "if_recpsvtb",
                "description": "인터페이스 수신 이력 테이블. [1:1 매칭 감사 관계] 거래처 마스터 수신 배치(IF_FB_201)가 수행한 전체 처리 건수, 성공 여부, 장애 상세 비고를 기록 관리합니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점별로 배정된 주 공급처 및 물류 유통 사업자의 계약 관계를 매핑/수립하기 위한 기준 코드로 간접 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 거래처 구분 코드 분류 체계 및 거래처 사업자번호 포맷 유효성 체크 정규식 설정을 매칭 참조합니다."
            }
        ]
    }

    # 152. TSM_DEPT_MST MEMO AND RELATED TABLES
    tsm_dept_mst_memo = (
        "### 1. 테이블 개요\n"
        "ERP 부서 마스터 인터페이스 원장 테이블 (`TSM_DEPT_MST`).\n"
        "본사 ERP 시스템으로부터 전사 부서 기준 정보(부서일련번호 `DEPT_NO`, 부서코드 `DEPT_CD`, 부서명 `DEPT_NM`, 효력시작일 `EFECT_STRT_DAY`, 효력종료일 `EFECT_FNH_DAY`, 직원위탁여부 `EMP_TUST_YN`)를 EAI 연동 인터페이스를 통해 수신 보관하는 부서 버퍼 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **부서 마스터 정보 배치 수신**: 부서 수신 배치 스케줄러(Job `DeptInterface`)가 기동되면 ERP 부서 원본 레코드가 본 테이블에 인서트된 후 수신 완결 프로시저(`SUB_IF_HYDM_RECV_P` [전문 ID: `'IF_FB_202'`])를 실행합니다.\n"
        "* **전사 부서 기준 코드 싱크**: 수신 처리가 성공(pos_proc_yn = 'Y')하면 본사의 표준 부서 마스터 테이블(`TB_DEPT` / `TDEPT_MST` 등)에 머지되어, 본사 사용자 마스터(`TUSERSTB`)의 인사 정보 및 백오프 화면의 담당 부서 분류 체계의 기본 코드로 적용됩니다."
    )

    data["tables"]["tsm_dept_mst"] = {
        "memo": tsm_dept_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "rowid": "데이터베이스 행 고유 물리적 식별자 (PK, Bigint, 자동 시퀀스)",
            "dept_no": "ERP에서 수신된 5자리 고유 부서 일련번호 (복합 인덱스)",
            "dept_cd": "부서 식별을 위한 고유 문자 코드 (10자리)",
            "dept_nm": "수신된 공식 부서 명칭 (50자리)",
            "efect_strt_day": "해당 부서 조직이 활성화되는 효력 시작 일자 (YYYYMMDD)",
            "efect_fnh_day": "해당 부서 조직이 폐쇄/만료되는 효력 종료 일자 (YYYYMMDD)",
            "emp_tust_yn": "직원 위탁 및 파견 근무 대상 여부 플래그 (1자리)",
            "rmrk": "부서 생성 및 변경에 대한 상세 비고 문구 (50자리)",
            "del_yn": "부서 전체의 삭제 여부 플래그 (1자리, 'Y'/'N')",
            "rgnr_id": "최초 등록자 ID (부서 수신 처리 프로그램 ID)",
            "rgnr_dtm": "최초 등록 일시",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 일시",
            "pos_proc_date": "부서 마스터 배치 연동 일자 (YYYYMMDD, 복합 인덱스)",
            "pos_proc_seq": "부서 배치 일자별 고유 실행 시퀀스 번호 (8자리, 복합 인덱스)",
            "pos_proc_yn": "배치 및 수신 프로시저(SUB_IF_HYDM_RECV_P) 정상 처리 완료 및 반영 여부 플래그 (1자리, 'Y': 성공, 'N': 대기/실패)",
            "pos_proc_remark": "연동 처리 중 장애 발생 시 적재되는 에러 상세 문구 (4000자리)",
            "pos_proc_create_dtime": "배치 연동 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)",
            "pos_proc_last_dtime": "배치 연동 트랜잭션 최종 갱신 완료 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "부서 마스터 수신 배치(DeptInterface_SqlMapper.xml)가 실행될 때 본 테이블에 배치 인서트합니다.",
        "memo_u": "수신 가공 프로시저(SUB_IF_HYDM_RECV_P)의 처리 상태에 따라 pos_proc_yn 플래그가 최종 업데이트됩니다.",
        "memo_d": "조직 이력 감사 및 전사 사원/가맹점 귀속 정보의 기준점이므로 데이터 임의 삭제가 통제됩니다.",
        "memo_r": "본사 조직도 및 부서 조회, 부서 마스터 수신 배치(DeptInterface), 사원 인사 정보 연동 시 소속 부서 기준 코드로 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tb_dept",
                "description": "본사 부서 마스터. [1:1 매칭 관계] 수신된 최신 부서 정보(부서코드, 부서명, 효력 시작/종료일 등)를 본사 및 가맹점 점포 소속 부서 기준 마스터에 동기화 반영하기 위해 참조 조인됩니다."
            },
            {
                "table_name": "torgtb",
                "description": "본사 조직 마스터. 부서 마스터가 갱신될 때 본사의 상위 부서-하위 부서 트리 구조 조직망을 최신화하고 배치하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tuserstb",
                "description": "시스템 사용자 마스터. [1:N 관계] 사원 및 점포 관리자의 인사 소속 부서가 최신 부서 코드로 자동 갱신 및 유지되도록 참조합니다."
            },
            {
                "table_name": "if_recpsvtb",
                "description": "인터페이스 수신 이력 테이블. [1:1 매칭 감사 관계] 부서 마스터 수신 배치(IF_FB_202)가 수행한 전체 처리 건수, 성공 여부, 장애 상세 비고를 기록 관리합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 부서 마스터의 효력 종료 여부 판정 로직의 자동 만료 스케줄러 정책 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 153. TSM_SALS_AGG_MST MEMO AND RELATED TABLES
    tsm_sals_agg_mst_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 일별 매출 집계 마스터 테이블 (`TSM_SALS_AGG_MST`).\n"
        "각 가맹점 점포별로 영업일 하루 동안 발생한 매출의 정상 및 반품/취소 요약 합계액(사업장코드 `BIZ_CD`, 매장코드 `SHOP_CD`, 발생일자 `OCCU_DT`, 매출구분 `CNCL_CLSF_CD` ['0': 정상, '1': 취소], 총매출액 `TOT_SALS_AMT`, 할인액 `DISC_AMT`, 순매출액 `NET_SALS_AMT`, 객수 `VSTR_CNTS`)을 정밀 집계하여 ERP로 송신하기 전 임시 보관하는 집계 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹점 마감 시 매출 총량 집계**: 점포가 일 영업 마감(Daily Closing)을 POS 단말기에서 확정하면, 백오프 매출 인터페이스 모듈이 가맹점 거래 데이터(`STRNHDTB`)를 기반으로 일자별 매출 통계를 생성하여 본 테이블에 인서트합니다.\n"
        "* **전사 ERP 매출 연동 송신 (`SUB_IF_HYDM_SEND_P` 프로시저)**: 매출 정산 송신 배치 및 화면단 전송 로직(`Pos_SaleInterface_Sql.xml`)이 실행되면, 본 테이블에 기록된 일별 가맹점 매출 요약 명세를 송금/매출 전송 연동 전문 프로시저(`SUB_IF_HYDM_SEND_P` [전문 ID: `'IF_FB_002'`])를 작동시켜 전사 ERP 재무 장부로 송신 및 완결 처리(pos_send_yn = 'Y')를 거칩니다."
    )

    data["tables"]["tsm_sals_agg_mst"] = {
        "memo": tsm_sals_agg_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "가맹점이 속한 본사 사업장/법인 구분 코드 (2자리, PK)",
            "shop_cd": "매출이 발생한 가맹점/점포 코드 (2자리, PK)",
            "occu_dt": "매출 거래가 발생한 영업일자 (YYYYMMDD, PK)",
            "cncl_clsf_cd": "매출 및 반품 취소 거래 구분 코드 (1자리, PK, '0': 정상 매출, '1': 반품/취소 매출)",
            "tot_sals_amt": "해당 매장/일자/구분별 총 매출 공급 및 부가세 합산액 (Numeric)",
            "disc_amt": "제휴/포인트/프로모션 적용에 의한 총 할인 합계액 (Numeric)",
            "net_sals_amt": "총매출액에서 할인을 공제한 실제 매출 순액 (Numeric)",
            "vstr_cnts": "해당 영업일 동안 결제를 수행한 총 영수증 발생 수/방문객 수 (Numeric)",
            "rgnr_id": "최초 등록자 ID (매출 집계 처리 모듈/배치 실행 ID)",
            "rgnr_dtm": "최초 매출 집계 생성 일시",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 및 완료 일시",
            "pos_send_seq": "ERP 전송 배치 기동을 위한 전문 송신 고유 일련번호 (8자리, PK)",
            "pos_send_yn": "ERP 매출 송신(SUB_IF_HYDM_SEND_P) 연동 완료 여부 플래그 (1자리, 'Y': 전송성공, 'N': 미전송/대기, 'E': 에러)",
            "pos_send_remark": "ERP 전송 실패 시 적재되는 EAI 연동 에러 메시지 (4000자리)",
            "pos_send_create_dtime": "ERP 전송 전문 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "점포 일마감(Pos_SaleInterface_Sql.xml) 또는 매출 마감 정산 데몬 기동 시 매출 총액 요약이 집계 인서트됩니다.",
        "memo_u": "ERP 매출 송신 완료 또는 전송 오류 상황(SaleInterface_SalesAggListDto) 발생 시 전송 결과 상태가 업데이트됩니다.",
        "memo_d": "점포 매출 세무 신고 및 가맹점 정산 수수료 대사의 원천 통계 자료이므로 물리 삭제가 금지됩니다.",
        "memo_r": "가맹점 일별 매출 현황 조회, ERP 일매출 송신(SUB_IF_HYDM_SEND_P), 점포 매출 마감 정합성 검증 및 재무 재산표 작성 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_mst",
                "description": "매출 트랜잭션 헤더 테이블. 가맹점 단위의 상세 개별 영수증 승인 내역의 합산 금액이 본 집계 마스터(TSM_SALS_AGG_MST)의 일자별 정상/취소 매출 총합과 정확히 대치하는지 감사/정합성을 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_shop_daycls_mst",
                "description": "일영업 마감 마스터. 가맹점 일영업 마감이 완료(JOBS_CLS_YN = 'Y')된 날짜에 매칭하여 본 일별 매출 집계가 ERP로 송신 가능한 완결 상태인지 체크하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 매출이 발생한 가맹점 점포의 소속 법인 정보 및 ERP 연동 코드를 매칭하여 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "ifslretb",
                "description": "일 영업마감 정산 테이블. 본 매출 집계에서 합산된 가맹점 현금/카드 매출 총액(tot_sals_amt, net_sals_amt)이 실제 본사 수납 마감 정산액과 대조적으로 정당하게 정산되었는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "if_sedpsvtb",
                "description": "인터페이스 송신 이력 테이블. [1:1 매칭 감사 관계] 매출 집계 송신 배치/프로시저가 ERP(IF_FB_002)로 송신한 전체 건수 및 EAI 통신 결과 로그를 감사 기록합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 매출 집계 단위에서 공제되는 제휴 할인 및 적립금 차감 연산 룰 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 154. TSM_SALS_AGG_MST_BK MEMO AND RELATED TABLES
    tsm_sals_agg_mst_bk_memo = (
        "### 1. 테이블 개요\n"
        "백업/임시 가맹점 일별 매출 집계 마스터 테이블 (`TSM_SALS_AGG_MST_BK`).\n"
        "가맹점 일별 매출 집계 마스터 실 운영 테이블 (`TSM_SALS_AGG_MST`)의 과거 구버전 Tibero 레거시 데이터 백업 및 연동 테스트(Shadow Run) 목적으로 설계된 이관 백업 테이블로, 정식 EAI 매출 전송 프로세스에는 간섭하지 않는 독립된 백업 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **레거시 이관 및 쉐도우 테스트 대조**: Tibero 연동 매퍼(`Tibero_SaleInterface_Sql.xml`)에서 가맹점 매출 요약 통계를 검증하거나, 데이터 마이그레이션 모듈 수행 시의 대조 소스로 활용되었습니다.\n"
        "* **과거 이력 감사**: 과거 특정 영업일의 가맹점별 합산 순매출액(`net_sals_amt`) 및 할인 금액을 본사 정산 백업 데이터와 교차 검증하여, 마이그레이션 정합성을 판별하는 용도로 사용됩니다."
    )

    data["tables"]["tsm_sals_agg_mst_bk"] = {
        "memo": tsm_sals_agg_mst_bk_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "백업된 가맹점 법인/사업장 구분 코드 (2자리)",
            "shop_cd": "백업된 매장 코드 (2자리)",
            "occu_dt": "백업된 매출 발생 영업일자 (YYYYMMDD)",
            "cncl_clsf_cd": "백업된 취소 구분자 (1자리, '0': 정상, '1': 반품)",
            "tot_sals_amt": "백업된 총매출액 합계 (Numeric)",
            "disc_amt": "백업된 총할인액 합계 (Numeric)",
            "net_sals_amt": "백업된 순매출액 합계 (Numeric)",
            "rgnr_id": "최초 백업 등록자 ID",
            "rgnr_dtm": "최초 백업 수신 등록 일시",
            "updr_id": "최종 백업 수정자 ID",
            "updr_dtm": "최종 백업 수정 및 완료 일시"
        },
        "memo_c": "과거 Tibero DB 데이터 이관 작업 또는 백업 동기화 스크립트 실행 시 백업 레코드가 인서트됩니다.",
        "memo_u": "이력용 테이블이므로 적재 이후의 수정이 거의 발생하지 않으며 정합성 보정에 의해서만 업데이트됩니다.",
        "memo_d": "데이터 복원 및 소급 감사용 백업 테이블이므로 정식 보존 기한이 경과하기 전까지는 삭제가 제한됩니다.",
        "memo_r": "구 Tibero DB 연동 매퍼(Tibero_SaleInterface_Sql) 이관 검증 및 과거 가맹점 매출 대사 이력 대조 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_sals_agg_mst",
                "description": "가맹점 매출 집계 마스터. [1:1 대칭 관계] 본 백업 테이블의 기준이 되는 원천 운영 거래 원장으로, 이관 데이터 무결성 검증 시 1:1 대조 조인됩니다."
            },
            {
                "table_name": "tsm_tran_mst_bk",
                "description": "매출 헤더 백업 테이블. 백업된 가맹점별 상세 영수증 매출 정보의 하루 합계액이 본 집계 백업 테이블과 정확히 대치하는지 감사 및 이관 무결성을 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_shop_daycls_mst_bk",
                "description": "일영업 마감 백업 테이블. 과거 일마감 처리가 성공 완료되었던 가맹점 내역과 본 일별 매출 백업본을 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 백업 데이터가 정상적인 가맹점 매장 코드로 귀속되었는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."
            }
        ]
    }

    # 155. TSM_SALS_DAYCLS_MST_BK MEMO AND RELATED TABLES
    tsm_sals_daycls_mst_bk_memo = (
        "### 1. 테이블 개요\n"
        "백업/임시 법인별 일자별 매출 마감 마스터 테이블 (`TSM_SALS_DAYCLS_MST_BK`).\n"
        "법인별 매출 마감 마스터 실 운영 테이블 (`TSM_SALS_DAYCLS_MST`)의 과거 구버전 Tibero 레거시 데이터 백업 및 연동 테스트(Shadow Run) 목적으로 사용되는 임시 백업 테이블로, 실제 법인 단위의 일 영업 마감 프로세스와 격리된 단순 백업용 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **레거시 이관 및 쉐도우 테스트 대조**: Tibero 연동 매퍼(`Tibero_SaleInterface_Sql.xml`)에서 법인 전체 마감 여부(`cls_yn`) 조회의 신뢰도를 검증할 때 임시 조회 처리에 매핑되어 검증되었습니다.\n"
        "* **과거 이력 감사**: 데이터 마이그레이션 및 정산 검증 시 특정 법인(`biz_cd`) 소속 점포들의 특정 일자 마감 이력 누락 여부를 확인하는 복원용 정합성 대조 원천으로 참조됩니다."
    )

    data["tables"]["tsm_sals_daycls_mst_bk"] = {
        "memo": tsm_sals_daycls_mst_bk_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "백업된 법인/사업장 고유 코드 (10자리)",
            "cls_dt": "백업된 매출 마감 기준 일자 (YYYYMMDD)",
            "cls_yn": "백업 당시의 법인 매출 마감 완료 여부 플래그 (1자리, 'Y'/'N')"
        },
        "memo_c": "과거 Tibero DB 데이터 이관 작업 또는 백업 동기화 스크립트 실행 시 백업 레코드가 인서트됩니다.",
        "memo_u": "이력용 테이블이므로 적재 이후의 수정이 거의 발생하지 않으며 데이터 정합 보정 시에만 정정 처리됩니다.",
        "memo_d": "데이터 복원 및 소급 감사용 백업 테이블이므로 정식 보존 기한이 경과하기 전까지는 삭제가 제한됩니다.",
        "memo_r": "구 Tibero DB 연동 매퍼(Tibero_SaleInterface_Sql) 이관 검증 및 과거 가맹점 매출 마감 대사 이력 대조 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_sals_daycls_mst",
                "description": "법인별 매출 마감 마스터. [1:1 대칭 관계] 본 백업 테이블의 기준이 되는 원천 운영 거래 원장으로, 이관 데이터 무결성 검증 시 1:1 대조 조인됩니다."
            },
            {
                "table_name": "tsm_shop_daycls_mst_bk",
                "description": "일영업 마감 백업 테이블. [1:N 관계] 특정 법인 내에 소속된 개별 가맹점들의 일마감 백업 상태를 연계 조회하고 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_sals_agg_mst_bk",
                "description": "일별 매출 집계 백업 테이블. [1:N 관계] 법인 단위 매출 마감이 수행된 영업일자의 가맹점별 매출 요약 백업 데이터를 추적하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 법인코드(biz_cd) 아래 귀속되는 가맹점들의 영업 및 브랜드 권역을 파악하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."
            }
        ]
    }

    # 156. TSM_SALS_MONCLS_MST MEMO AND RELATED TABLES
    tsm_sals_moncls_mst_memo = (
        "### 1. 테이블 개요\n"
        "ERP 법인별 월 매출 마감 수신 원장 테이블 (`TSM_SALS_MONCLS_MST`).\n"
        "본사 ERP 시스템으로부터 법인별 월 단위 최종 매출 정산 및 세무 마감 확정 정보(법인코드 `BIZ_CD`, 마감월 `CLS_MONTH`, 마감여부 `CLS_YN` ['Y': 월마감완료, 'N': 미마감/해제])를 EAI 연동 인터페이스를 통해 배치 수신 보관하는 월마감 통제 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **법인별 월 영업 정산 마감 제어**: 본사 ERP에서 재무 결산 및 세무 부가세 신고용 월 마감이 완료되면 월마감 수신 배치(Job `CloseInterface`)를 통해 본 테이블로 상태가 수신 인서트되며, 수신 완결 프로시저(`SUB_IF_HYDM_RECV_P` [전문 ID: `'IF_FB_006'`])를 실행하여 상태 변경(pos_proc_yn = 'Y')을 완결합니다.\n"
        "* **영업일 소급 및 신규 입력 통제**: 본 테이블에 특정 법인/월에 대해 `cls_yn = 'Y'`로 상태가 수신 적재되면, 해당 법인 산하 모든 가맹점 점포들의 해당 마감월 내 일자별 매출 및 영수증 신규 입력, 수정, 취소(소급 처리) 처리가 시스템적으로 전면 차단/제한됩니다."
    )

    data["tables"]["tsm_sals_moncls_mst"] = {
        "memo": tsm_sals_moncls_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "rowid": "데이터베이스 행 고유 물리적 식별자 (PK, Bigint, 자동 시퀀스)",
            "biz_cd": "ERP에서 수신된 2자리 고유 법인/사업장 코드 (복합 인덱스)",
            "cls_month": "매출 마감이 설정된 기준 년월 (YYYYMM, 6자리, 복합 인덱스)",
            "cls_yn": "ERP 월 매출 결산 마감 확정 플래그 (1자리, 'Y': 마감 완료 및 소급제한, 'N': 마감 대기/미완료)",
            "pos_proc_date": "월 마감 배치 연동 일자 (YYYYMMDD, 복합 인덱스)",
            "pos_proc_seq": "월 마감 배치 일자별 고유 실행 시퀀스 번호 (8자리, 복합 인덱스)",
            "pos_proc_yn": "배치 및 수신 프로시저(SUB_IF_HYDM_RECV_P) 정상 처리 완료 및 반영 여부 플래그 (1자리, 'Y': 성공, 'N': 대기/실패)",
            "pos_proc_remark": "연동 처리 과정에서 마감 연산 예외 발생 시 적재되는 에러 상세 문구 (4000자리)",
            "pos_proc_create_dtime": "배치 연동 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)",
            "pos_proc_last_dtime": "배치 연동 트랜잭션 최종 갱신 완료 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "월 마감 수신 배치(CloseInterface_SqlMapper.xml)가 실행될 때 본 테이블에 배치 인서트합니다.",
        "memo_u": "수신 가공 프로시저(SUB_IF_HYDM_RECV_P)의 처리 상태에 따라 pos_proc_yn 플래그가 최종 업데이트됩니다.",
        "memo_d": "매출 마감 잠금(Locking)의 법적 증적이므로 데이터 삭제가 완전 통제됩니다.",
        "memo_r": "법인별 월 매출 마감 여부 조회, 마감 통제 배치(CloseInterface), 매출 등록 화면의 월 마감 소급 제한 여부 검증 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_sals_daycls_mst",
                "description": "일마감 마스터 테이블. 법인 단위 월마감 처리가 수행될 때, 해당 월의 전체 일영업 마감 상태가 완결되었는지 검증 및 소급 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_sals_agg_mst",
                "description": "일별 매출 집계 마스터. 월 마감 확정 상태(cls_yn = 'Y')가 갱신되면 해당 마감월 내 가맹점 매출 합계 및 정산 잔액을 잠금 제어(Locking)하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 본사에서 수신된 월 마감 정책을 산하 점포들의 브랜드/법인 소속별 정산 마감에 배포 식별하기 위해 참조합니다."
            },
            {
                "table_name": "if_recpsvtb",
                "description": "인터페이스 수신 이력 테이블. [1:1 매칭 감사 관계] 월 마감 플래그 수신 배치(IF_FB_006)가 수행한 연동 총 건수 및 에러 상세를 기록 보관합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 월 영업 정산 마감 기한 설정(예: 익월 5일 영업일 마감 통제 등) 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 157. TSM_SHOP_DAYCLS_MST MEMO AND RELATED TABLES
    tsm_shop_daycls_mst_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 영업일영업 마감 정보 마스터 테이블 (`TSM_SHOP_DAYCLS_MST`).\n"
        "가맹점 점포에서 전송되는 일영업 마감 상태(사업장코드 `BIZ_CD`, 마감일자 `CLS_DT`, 매장코드 `SHOP_CD`, 영업마감여부 `JOBS_CLS_YN`, 정산마감여부 `PLCMNT_CLS_YN`)를 저장 및 관리하며, ERP로 마감 완료를 연동 송신하는 송신 제어용 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **점포 일영업 마감 완결 기록**: 매장이 당일 영업 종료 후 정산 처리를 완결하면 `jobs_cls_yn = 'Y'` 및 `plcmnt_cls_yn = 'Y'`로 데이터가 생성/업데이트되어 당일 영업 매출 집계가 잠금 처리됩니다.\n"
        "* **ERP 일마감 통보 연동 (`SUB_IF_HYDM_SEND_P` 실행)**: 매출 마감 송신 모듈(`Pos_SaleInterface_Sql.xml`)이 기동되면, 본 테이블에서 미전송 상태(`pos_send_yn = 'N'`)인 마감 플래그들을 추출하여 ERP 송신 프로시저(`SUB_IF_HYDM_SEND_P` [전문 ID: `'IF_FB_004'`])를 실행하고 전송 성공 시 `pos_send_yn = 'Y'`로 상태를 변경하여 ERP와의 결산 싱크를 마칩니다."
    )

    data["tables"]["tsm_shop_daycls_mst"] = {
        "memo": tsm_shop_daycls_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "가맹점이 소속된 법인/사업장 구분 코드 (2자리, PK)",
            "cls_dt": "마감 처리가 수행된 기준 영업일자 (YYYYMMDD, PK)",
            "shop_cd": "마감을 확정한 가맹점 매장 코드 (2자리, PK)",
            "jobs_cls_yn": "가맹점 일영업 마감 완료 여부 플래그 (1자리, 'Y': 마감완료, 'N': 영업중)",
            "plcmnt_cls_yn": "가맹점 금전 수납 및 배치 정산 마감 완료 여부 플래그 (1자리, 'Y': 마감완료, 'N': 정산중)",
            "rgnr_id": "최초 등록자 ID (마감 승인 처리 모듈/배치 실행 ID)",
            "rgnr_dtm": "최초 일마감 등록 일시",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 마감 수정 및 완료 일시",
            "pos_send_seq": "ERP 전송 배치 기동을 위한 전문 송신 고유 일련번호 (8자리, PK)",
            "pos_send_yn": "ERP 일마감 송신(SUB_IF_HYDM_SEND_P) 연동 완료 여부 플래그 (1자리, 'Y': 전송성공, 'N': 미전송/대기, 'E': 에러)",
            "pos_send_remark": "ERP 전송 실패 시 적재되는 EAI 연동 에러 메시지 (4000자리)",
            "pos_send_create_dtime": "ERP 전송 전문 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "점포 일마감 확정(Pos_SaleInterface_Sql.xml) 시 해당 점포의 마감 정보 레코드가 본 테이블에 인서트됩니다.",
        "memo_u": "ERP 일마감 전송 완료 또는 전송 오류 상황(SaleInterface_DailyCloseListDto) 발생 시 전송 결과 상태가 업데이트됩니다.",
        "memo_d": "법인 결산 마감 및 가맹점 정산 기산점 기준이므로 임의 삭제 및 수정이 차단됩니다.",
        "memo_r": "가맹점 일마감 현황 조회, ERP 일마감 송신(SUB_IF_HYDM_SEND_P), 일일 매출 집계 정합성 대조 및 가맹점 정산 자료 생성 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_sals_agg_mst",
                "description": "일별 매출 집계 마스터. [1:1 매칭 관계] 매장 마감일자와 동일한 영업일의 정상/취소 매출 집계 내역이 정상 연동 송신(pos_send_yn = 'Y') 가능한 상태인지 판정 조인합니다."
            },
            {
                "table_name": "tsm_tran_mst",
                "description": "매출 트랜잭션 헤더 테이블. 일마감 처리 시 당일 거래된 상세 영수증 매출 정보 수집이 완료되었는지 확인하고 대사하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "ifslretb",
                "description": "일 영업마감 정산 테이블. POS 마감 시의 현금 과부족액(OVER_AMT) 및 예치금 정산 결과와 해당 매장의 일마감 플래그 상태를 크로스 체크합니다."
            },
            {
                "table_name": "tsm_sals_moncls_mst",
                "description": "월마감 통제 마스터. 본 테이블의 일마감 데이터가 포함된 해당 월이 이미 월마감 완료(CLS_YN = 'Y') 상태인지 판정하여 일마감의 해제(Rollback) 및 재마감을 엄격히 차단하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 일마감 정보가 귀속되는 실 가맹점 명칭 및 세부 관리 속성을 조회 매칭합니다."
            },
            {
                "table_name": "if_sedpsvtb",
                "description": "인터페이스 송신 이력 테이블. [1:1 매칭 감사 관계] 일마감 송신 배치/프로시저가 ERP(IF_FB_004)로 송신한 전체 건수 및 EAI 통신 결과 로그를 감사 기록합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 일마감 처리 시 소급 가능한 백일자 허용 한도 정책 파라미터를 매칭 참조합니다."
            }
        ]
    }

    # 158. TSM_SHOP_DAYCLS_MST_BK MEMO AND RELATED TABLES
    tsm_shop_daycls_mst_bk_memo = (
        "### 1. 테이블 개요\n"
        "백업/임시 가맹점 영업일영업 마감 정보 마스터 테이블 (`TSM_SHOP_DAYCLS_MST_BK`).\n"
        "가맹점 영업일마감 정보 마스터 실 운영 테이블 (`TSM_SHOP_DAYCLS_MST`)의 과거 구버전 Tibero 레거시 데이터 백업 및 연동 테스트(Shadow Run) 목적으로 사용되는 백업용 임시 테이블로, 실제 영업 마감 및 회계 상신과는 무관한 격리 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **레거시 이관 및 쉐도우 테스트 대조**: Tibero 연동 매퍼(`Tibero_SaleInterface_Sql.xml`)에서 개별 가맹점의 일자별 마감 여부(`jobs_cls_yn`, `plcmnt_cls_yn`) 수집 정확도를 병행 검증하는 임시 테이블로 사용되었습니다.\n"
        "* **과거 이력 감사**: 마이그레이션 도중 누락되거나 이관이 비정상 종료된 점포의 마감 정보 상태를 감사 및 소급 대사하는 백업 용도로 참조됩니다."
    )

    data["tables"]["tsm_shop_daycls_mst_bk"] = {
        "memo": tsm_shop_daycls_mst_bk_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "백업된 가맹점 소속 법인/사업장 코드 (2자리)",
            "cls_dt": "백업된 일마감 기준 영업일자 (YYYYMMDD)",
            "shop_cd": "백업된 가맹점 매장 코드 (2자리)",
            "jobs_cls_yn": "백업 당시의 가맹점 영업 마감 완료 플래그 (1자리)",
            "plcmnt_cls_yn": "백업 당시의 가맹점 정산/배치 마감 완료 플래그 (1자리)",
            "rgnr_id": "최초 백업 등록자 ID",
            "rgnr_dtm": "최초 백업 수신 등록 일시",
            "updr_id": "최종 백업 수정자 ID",
            "updr_dtm": "최종 백업 수정 및 완료 일시"
        },
        "memo_c": "과거 Tibero DB 데이터 이관 작업 또는 백업 동기화 스크립트 실행 시 백업 레코드가 인서트됩니다.",
        "memo_u": "이력용 테이블이므로 적재 이후의 수정이 거의 발생하지 않으며 정합성 보정에 의해서만 업데이트됩니다.",
        "memo_d": "데이터 복원 및 소급 감사용 백업 테이블이므로 정식 보존 기한이 경과하기 전까지는 삭제가 제한됩니다.",
        "memo_r": "구 Tibero DB 연동 매퍼(Tibero_SaleInterface_Sql) 이관 검증 및 과거 가맹점 영업 마감 대사 이력 대조 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_shop_daycls_mst",
                "description": "가맹점 일영업 마감 마스터. [1:1 대칭 관계] 본 백업 테이블의 기준이 되는 원천 운영 거래 원장으로, 이관 데이터 무결성 검증 시 1:1 대조 조인됩니다."
            },
            {
                "table_name": "tsm_sals_agg_mst_bk",
                "description": "일별 매출 집계 백업 테이블. [1:1 매칭 관계] 마감일자와 동일한 영업일의 정상/취소 매출 집계 내역 백업 데이터를 조회 및 대사하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_tran_mst_bk",
                "description": "매출 헤더 백업 테이블. 일마감 백업 처리 시 당일 거래된 상세 영수증 매출 정보 수집 백업본이 존재하고 일치하는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 백업된 일마감 데이터가 정상적인 가맹점 매장 코드로 귀속되었는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."
            }
        ]
    }

    # 159. TSM_TRAN_DTL MEMO AND RELATED TABLES
    tsm_tran_dtl_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 매출 거래 결제 상세 정보 테이블 (`TSM_TRAN_DTL`).\n"
        "각 가맹점 점포의 POS 단말기에서 결제 승인된 건별 결제 수단 상세 내역(사업장코드 `BIZ_CD`, 매장코드 `SHOP_CD`, 영업일자 `OCCU_DT`, 영수증일련번호 `BZTC_NO`, 결제순번 `BZTC_SEQ`, 카드/현금 구분코드 `BZTC_TYPE_CD`, 결제분류코드 `STL_CLSF_CD`, 승인번호 `APPR_NO`, 카드사코드 `CARC_CD`, 승인금액 `APPR_AMT`, 부가세 `VAT` 등)을 ERP 송신 전 임시 보관하는 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **결제 수단별 세부 승인 기록**: 가맹점 POS에서 실시간 혹은 마감 처리 시 카드 승인, 현금 영수증 발행, 포인트 차감 등의 개별 결제 발생 내역이 본 테이블에 적재됩니다.\n"
        "* **ERP 결제 상세 연동 송신 (`SUB_IF_HYDM_SEND_P` 실행)**: 매출 마감 송신 모듈(`Pos_SaleInterface_Sql.xml`)이 기동될 때 미송신 레코드(`pos_send_yn = 'N'`)를 EAI 연동 공통 프로시저(`SUB_IF_HYDM_SEND_P` [전문 ID: `'IF_FB_003'` / 결제 상세])를 호출하여 ERP 회계 원장 및 카드 정산 장부로 송신하며, 완료 시 `pos_send_yn = 'Y'`로 갱신됩니다."
    )

    data["tables"]["tsm_tran_dtl"] = {
        "memo": tsm_tran_dtl_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "가맹점 소속 법인/사업장 고유 코드 (2자리, PK)",
            "shop_cd": "거래가 발생한 매장 코드 (2자리, PK)",
            "occu_dt": "거래가 발생한 영업일자 (YYYYMMDD, PK)",
            "bztc_no": "매출 영수증 고유 일련번호 (20자리, PK)",
            "cncl_clsf_cd": "취소 여부 플래그 (1자리, PK, '0': 정상 매출, '1': 반품/취소 매출)",
            "bztc_seq": "단일 영수증 내의 결제 수단별 고유 일련번호 (PK, Numeric)",
            "bztc_type_cd": "결제수단구분코드 (카드, 현금, 포인트 등)",
            "stl_clsf_cd": "결제 세부 분류 코드 (2자리, SM006)",
            "stl_chan_cd": "결제 승인 채널 코드 (1자리, SM007)",
            "affr_clsf_cd": "제휴 구분 코드 (2자리, SM019)",
            "evi_type_cd": "세무 세액 증빙 유형 코드 (2자리, SM027)",
            "cust_cd": "매출 대상 고객/거래처 고유 코드 (10자리)",
            "dpn_bizu_clsf_cd": "대표 가맹점 번호 귀속 코드 (4자리)",
            "stl_mthd_no": "결제 매체 식별 정보 (마스킹된 카드번호/계좌번호 등, 25자리)",
            "appr_no": "카드사/승인기관 발행 8~20자리 고유 승인 번호",
            "vali_trm": "승인 카드 유효기간 (MMYY, 4자리)",
            "istm_mnts": "할부 개월 수 (2자리, '00': 일시불)",
            "appr_dt": "승인 처리 일자 (YYYYMMDD)",
            "appr_hms": "승인 처리 시간 (HHMMSS)",
            "appr_bztc_no": "VAN사/승인망 고유 거래 추적 번호 (15자리)",
            "jos_no": "가맹점 카드사 등록 가맹점 번호 (20자리)",
            "appr_amt": "승인 요청 및 승인된 총 금액 (Numeric)",
            "disc_occu_amt": "결제 수단 적용에 따른 할인 공제액 (Numeric)",
            "disc_asgw_amt": "할인 행사에 대한 가맹점 분담금 (Numeric)",
            "bygc_cd": "매입 카드사/금융기관 코드 (6자리, SM011)",
            "bygc_nm": "매입 카드사 한글 명칭 (30자리)",
            "carc_cd": "발급 카드사 코드 (6자리)",
            "carc_nm": "발급 카드사 한글 명칭 (50자리)",
            "rcvd_cd": "카드 대금 입금 금융기관 코드 (2자리, SM012)",
            "rcvd_nm": "카드 대금 입금 금융기관 한글 명칭 (30자리)",
            "manu_appr_yn": "단말기 수동 입력/승인 여부 플래그 (1자리)",
            "orig_occu_dt": "반품/취소 시 원거래가 발생한 최초 영업일자 (YYYYMMDD)",
            "orig_shop_cd": "반품/취소 시 원거래 발생 매장 코드 (2자리)",
            "orig_stl_clsf_cd": "반품/취소 시 원거래 결제 수단 분류 코드 (2자리)",
            "orig_bztc_no": "반품/취소 시 원거래 영수증 일련번호 (20자리)",
            "orig_bztc_seq": "반품/취소 시 원거래 결제 수단 순번",
            "orig_appr_amt": "반품/취소 시 원거래의 최초 승인액 (Numeric)",
            "cncl_fee": "결제 승인 취소 시 발생 수수료 (Numeric)",
            "rfud_amt": "고객 환불 금액 (Numeric)",
            "bizu_rgn_no": "가맹점 사업자등록번호 (10자리)",
            "def_no": "카드 단말기 식별 고유번호 (18자리)",
            "tax_no": "가맹점 세무 등록 식별번호 (20자리)",
            "rcps_parr_rgn_dt": "카드 매출 대금 입금 예정일자 (YYYYMMDD)",
            "rcps_parr_rgn_seq": "입금 정산 대조 일련번호",
            "blue_pcrs_no": "블루멤버스 포인트 카드 승인번호 (50자리)",
            "zertx_amt": "부가세 영세 적용 금액 (Numeric)",
            "txfr_amt": "부가세 면세 적용 금액 (Numeric)",
            "sals_patt_yn": "매출 연동 패턴 구분 플래그 (1자리)",
            "supp_dt": "공급 처리 일자 (YYYYMMDD)",
            "supp_shop_cd": "실제 공급이 수행된 점포 코드 (2자리)",
            "sals_amt": "매출 산출 금액 (Numeric)",
            "crd_knd_cd": "신용/체크/해외카드 등 카드 세부 속성 코드 (1자리, SM062)",
            "supr_pric": "부가세를 제외한 순수 공급가액 (Numeric)",
            "vat": "매출 부가가치세 세액 (Numeric)",
            "msce": "봉사료/팁 금액 (Numeric)",
            "exnt_amt": "기타 소모품 공제 금액 (Numeric)",
            "avp_def_no": "VAN사 연동 단말 가맹점 번호 (18자리)",
            "fee": "결제 대행 및 카드사 정산 수수료 총액 (Numeric)",
            "fee_supr_pric": "수수료 공급가액 (Numeric)",
            "fee_vat": "수수료 부가세 세액 (Numeric)",
            "fee_vat_stoa_dt": "수수료 정산 반영 예정일자 (YYYYMMDD)",
            "bond_st_cd": "채권 정산 상태 코드 (2자리)",
            "rgnr_id": "최초 등록자 ID (POS 연동 수신 모듈)",
            "rgnr_dtm": "최초 거래 데이터 적재 일시",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 및 완료 일시",
            "pos_slip_seq": "POS 영수증 슬립 일련번호 (2자리)",
            "pos_org_tb_slip": "POS 원본 거래 테이블 식별 키",
            "pos_send_seq": "ERP 전송 배치 기동을 위한 전문 송신 고유 일련번호 (8자리, PK)",
            "pos_send_yn": "ERP 결제 상세 송신(SUB_IF_HYDM_SEND_P) 연동 완료 여부 플래그 (1자리, 'Y': 전송성공, 'N': 미전송/대기, 'E': 에러)",
            "pos_send_remark": "ERP 전송 실패 시 적재되는 EAI 연동 에러 메시지 (4000자리)",
            "pos_send_create_dtime": "ERP 전송 전문 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "가맹점 일마감 확정(Pos_SaleInterface_Sql.xml) 또는 매출 마감 정산 데몬 기동 시 매출 총액 요약이 집계 인서트됩니다.",
        "memo_u": "ERP 매출 송신 완료 또는 전송 오류 상황(SaleInterface_SalesAggListDto) 발생 시 전송 결과 상태가 업데이트됩니다.",
        "memo_d": "점포 매출 세무 신고 및 가맹점 정산 수수료 대사의 원천 통계 자료이므로 물리 삭제가 금지됩니다.",
        "memo_r": "가맹점 일별 매출 현황 조회, ERP 일매출 송신(SUB_IF_HYDM_SEND_P), 점포 매출 마감 정합성 검증 및 재무 재산표 작성 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_mst",
                "description": "매출 트랜잭션 헤더 테이블. [1:N 관계] 매출 영수증 하나에 귀속되는 결제 수단별 세부 금액(카드 결제, 현금 영수증, OCB 포인트 등)을 매칭하여 총 합산액의 정합성을 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_sals_agg_mst",
                "description": "일별 매출 집계 마스터. 가맹점 단위의 매출 마감 통계를 산출할 때, 본 테이블의 결제 금액 합계가 집계 마스터의 매출 합산액과 정확히 교차 일치하는지 감사 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_shop_daycls_mst",
                "description": "일영업 마감 마스터. 해당 영업일자의 일마감이 완료(JOBS_CLS_YN = 'Y') 처리되어 결제가 완료되었고 더 이상 결제 내역의 수정이 발생하지 않는 잠금 상태인지 판정하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 결제가 발생한 점포의 법인 구분 및 ERP 전송 코드 체계를 조회 매칭하기 위해 참조합니다."
            },
            {
                "table_name": "if_sedpsvtb",
                "description": "인터페이스 송신 이력 테이블. [1:1 매칭 감사 관계] 결제 상세 송신 배치가 ERP로 데이터를 송신하고 갱신한 EAI 통신 성공 여부 및 결과 비고 로그를 추적하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "POS 및 ERP 환경설정 테이블. 각 결제 수단별 세무 증빙(현금영수증, 신용카드 영수증 등) 식별번호 마스킹 및 출력 규격 정의를 매칭 참조합니다."
            }
        ]
    }

    # 160. TSM_TRAN_DTL_BK MEMO AND RELATED TABLES
    tsm_tran_dtl_bk_memo = (
        "### 1. 테이블 개요\n"
        "백업/임시 가맹점 매출 거래 결제 상세 정보 테이블 (`TSM_TRAN_DTL_BK`).\n"
        "가맹점 매출 거래 결제 상세 정보 실 운영 테이블 (`TSM_TRAN_DTL`)의 과거 구버전 Tibero 레거시 데이터 백업 및 연동 테스트(Shadow Run) 목적으로 설계된 이관 백업 테이블로, 정식 EAI 매출 전송 프로세스에는 간섭하지 않는 독립된 백업 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **레거시 이관 및 쉐도우 테스트 대조**: Tibero 연동 매퍼(`Tibero_SaleInterface_Sql.xml`)에서 개별 가맹점의 일자별 상세 결제 승인 내역 수집 정확도를 병행 검증하는 임시 테이블로 사용되었습니다.\n"
        "* **과거 이력 감사**: 마이그레이션 도중 누락되거나 이관이 비정상 종료된 점포의 카드사 매입사별 승인 대금 및 수수료 정산 내역 백업본을 추적하고 소급 대사하는 백업 용도로 참조됩니다."
    )

    data["tables"]["tsm_tran_dtl_bk"] = {
        "memo": tsm_tran_dtl_bk_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "백업된 가맹점 소속 법인/사업장 코드 (2자리)",
            "shop_cd": "백업된 매장 코드 (2자리)",
            "occu_dt": "백업된 매출 발생 영업일자 (YYYYMMDD)",
            "bztc_no": "백업된 영수증 일련번호 (20자리)",
            "cncl_clsf_cd": "백업된 취소 구분자 (1자리, '0': 정상, '1': 반품)",
            "bztc_seq": "백업된 결제수단 일련번호",
            "bztc_type_cd": "백업된 결제수단 구분코드 (카드, 현금 등)",
            "stl_clsf_cd": "백업된 결제 분류 코드 (2자리)",
            "stl_chan_cd": "백업된 결제 채널 코드 (1자리)",
            "affr_clsf_cd": "백업된 제휴 구분 코드 (2자리)",
            "evi_type_cd": "백업된 증빙 유형 코드 (2자리)",
            "cust_cd": "백업된 고객/거래처 코드 (10자리)",
            "dpn_bizu_clsf_cd": "백업된 가치구분코드",
            "stl_mthd_no": "백업된 마스킹 결제번호 (25자리)",
            "appr_no": "백업된 승인번호 (20자리)",
            "vali_trm": "백업된 유효기간 (4자리)",
            "istm_mnts": "백업된 할부개월수 (2자리)",
            "appr_dt": "백업된 승인일자 (YYYYMMDD)",
            "appr_hms": "백업된 승인시간 (HHMMSS)",
            "appr_bztc_no": "백업된 VAN 거래번호 (15자리)",
            "jos_no": "백업된 가맹점번호 (20자리)",
            "appr_amt": "백업된 승인금액 (Numeric)",
            "stl_amt": "백업된 결제금액 (Numeric)",
            "disc_occu_amt": "백업된 할인금액 (Numeric)",
            "disc_asgw_amt": "백업된 할인분담금 (Numeric)",
            "bygc_cd": "백업된 매입카드사 코드 (6자리)",
            "bygc_nm": "백업된 매입카드사 명칭 (30자리)",
            "carc_cd": "백업된 발급카드사 코드 (6자리)",
            "carc_nm": "백업된 발급카드사 명칭 (50자리)",
            "rcvd_cd": "백업된 입금처 금융기관 코드 (2자리)",
            "rcvd_nm": "백업된 입금처 명칭 (30자리)",
            "manu_appr_yn": "백업된 수동승인여부 (1자리)",
            "orig_occu_dt": "반품/취소 시 백업된 원거래 발생일자 (YYYYMMDD)",
            "orig_shop_cd": "반품/취소 시 백업된 원거래 매장 코드 (2자리)",
            "orig_stl_clsf_cd": "반품/취소 시 백업된 원거래 결제분류 (2자리)",
            "orig_bztc_no": "반품/취소 시 백업된 원거래 영수증번호 (20자리)",
            "orig_bztc_seq": "반품/취소 시 백업된 원거래 결제순번",
            "orig_appr_amt": "반품/취소 시 백업된 원거래 승인금액 (Numeric)",
            "cncl_fee": "백업된 취소 수수료 (Numeric)",
            "rfud_amt": "백업된 환불금액 (Numeric)",
            "bizu_rgn_no": "백업된 사업자등록번호 (10자리)",
            "def_no": "백업된 단말기 고유식별번호 (18자리)",
            "tax_no": "백업된 세무식별번호 (20자리)",
            "rcps_parr_rgn_dt": "백업된 대금 입금 예정일자 (YYYYMMDD)",
            "rcps_parr_rgn_seq": "백업된 입금정산 대조 순번",
            "blue_pcrs_no": "백업된 블루멤버스 포인트 승인번호 (50자리)",
            "zertx_amt": "백업된 영세 적용금액 (Numeric)",
            "txfr_amt": "백업된 면세 적용금액 (Numeric)",
            "sals_patt_yn": "백업된 매출 연동 구분 (1자리)",
            "supp_dt": "백업된 공급 처리 일자 (YYYYMMDD)",
            "supp_shop_cd": "백업된 공급 점포 코드 (2자리)",
            "sals_amt": "백업된 매출 금액 (Numeric)",
            "crd_knd_cd": "백업된 카드종류 구분코드 (1자리)",
            "supr_pric": "백업된 공급가액 (Numeric)",
            "vat": "백업된 부가가치세 세액 (Numeric)",
            "msce": "백업된 봉사료 (Numeric)",
            "exnt_amt": "백업된 소모품 공제금액 (Numeric)",
            "avp_def_no": "백업된 PG 가맹점번호 (18자리)",
            "fee": "백업된 카드사 수수료 (Numeric)",
            "fee_supr_pric": "백업된 수수료 공급가액 (Numeric)",
            "fee_vat": "백업된 수수료 부가세 (Numeric)",
            "fee_vat_stoa_dt": "백업된 수수료 정산일자 (YYYYMMDD)",
            "rgnr_id": "최초 백업 등록자 ID",
            "rgnr_dtm": "최초 백업 수신 등록 일시",
            "updr_id": "최종 백업 수정자 ID",
            "updr_dtm": "최종 백업 수정 및 완료 일시",
            "bond_st_cd": "백업된 채권 정산 상태 코드 (2자리)"
        },
        "memo_c": "과거 Tibero DB 데이터 이관 작업 또는 백업 동기화 스크립트 실행 시 백업 레코드가 인서트됩니다.",
        "memo_u": "이력용 테이블이므로 적재 이후의 수정이 거의 발생하지 않으며 정합성 보정에 의해서만 업데이트됩니다.",
        "memo_d": "데이터 복원 및 소급 감사용 백업 테이블이므로 정식 보존 기한이 경과하기 전까지는 삭제가 제한됩니다.",
        "memo_r": "구 Tibero DB 연동 매퍼(Tibero_SaleInterface_Sql) 이관 검증 및 과거 가맹점 영업 마감 대사 이력 대조 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_dtl",
                "description": "가맹점 매출 거래 결제 상세. [1:1 대칭 관계] 본 백업 테이블의 원본 데이터가 되는 실 운영 결제 상세 테이블로, 마이그레이션 교차 대사 시 1:1 조인 대조됩니다."
            },
            {
                "table_name": "tsm_tran_mst_bk",
                "description": "매출 헤더 백업 테이블. [1:N 관계] 백업된 매출 영수증 하나에 포함된 세부 수단별 금액 결제 내역과 총 영수증 금액의 일치 여부를 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_sals_agg_mst_bk",
                "description": "일별 매출 집계 백업 테이블. 가맹점 단위 일자별 마감 검증 시 본 백업 상세 금액의 합계가 마감 매출 집계 백업 데이터와 상응하는지 감사하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_shop_daycls_mst_bk",
                "description": "일영업 마감 백업 테이블. 해당 일자의 마감 상태 백업본을 추적하여 이관 데이터 완결성을 판정하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 백업 데이터가 유효한 가맹점 소속 및 코드로 귀속되었는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."
            }
        ]
    }

    # 161. TSM_TRAN_MST MEMO AND RELATED TABLES
    tsm_tran_mst_memo = (
        "### 1. 테이블 개요\n"
        "가맹점 매출 트랜잭션 헤더 마스터 테이블 (`TSM_TRAN_MST`).\n"
        "각 가맹점 점포의 POS 단말기에서 결제 승인되어 발생한 영수증 단위 매출 거래 헤더 요약 정보(사업장코드 `BIZ_CD`, 매장코드 `SHOP_CD`, 영업일자 `OCCU_DT`, 영수증일련번호 `BZTC_NO`, 취소구분코드 `CNCL_CLSF_CD` ['0': 정상, '1': 취소], 총 결제액 `STL_AMT`, 공급가액 `SUPR_PRIC`, 부가세 `VAT` 등)를 ERP 송신 전 임시 보관하는 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **영수증별 매출 헤더 승인 기록**: 가맹점 POS에서 실시간 거래 승인 시 생성되는 개별 영수증 건별 전체 매출 총액 요약이 본 테이블에 적재됩니다.\n"
        "* **ERP 매출 헤더 연동 송신 (`SUB_IF_HYDM_SEND_P` 실행)**: 매출 마감 송신 모듈(`Pos_SaleInterface_Sql.xml`)이 기동될 때 미송신 레코드(`pos_send_yn = 'N'`)를 EAI 연동 공통 프로시저(`SUB_IF_HYDM_SEND_P` [전문 ID: `'IF_FB_003'` / 거래 헤더])를 호출하여 ERP 회계 원장 및 카드 정산 장부로 송신하며, 완료 시 `pos_send_yn = 'Y'`로 갱신됩니다."
    )

    data["tables"]["tsm_tran_mst"] = {
        "memo": tsm_tran_mst_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "가맹점 소속 법인/사업장 고유 코드 (2자리, PK)",
            "shop_cd": "거래가 발생한 매장 코드 (2자리, PK, '10': 식당, '20': 숍, '30': 키친 등)",
            "occu_dt": "거래가 발생한 영업일자 (YYYYMMDD, PK)",
            "bztc_no": "매출 영수증 고유 일련번호 (20자리, PK)",
            "cncl_clsf_cd": "취소 여부 플래그 (1자리, PK, '0': 정상 매출, '1': 반품/취소 매출)",
            "appr_amt": "승인 요청 및 승인된 총 금액 (Numeric)",
            "stl_amt": "할인을 제외한 실제 고객 최종 결제금액 (Numeric)",
            "disc_amt": "영수증 단위 제휴/프로모션 적용에 의한 총 할인 합계액 (Numeric)",
            "asgw_amt": "할인 행사에 대한 가맹점 분담금 (Numeric)",
            "sals_amt": "공급원가 매출액 (Numeric)",
            "supr_pric": "부가세를 제외한 순수 공급가액 (Numeric)",
            "vat": "매출 부가가치세 세액 (Numeric)",
            "msce": "봉사료/팁 금액 (Numeric)",
            "exnt_amt": "기타 소모품 공제 금액 (Numeric)",
            "pgm_no": "매출 등록에 사용된 POS 프로그램 번호 (10자리)",
            "rgnr_id": "최초 등록자 ID (POS 연동 수신 모듈)",
            "rgnr_dtm": "최초 거래 데이터 적재 일시",
            "updr_id": "최종 수정자 ID",
            "updr_dtm": "최종 수정 및 완료 일시",
            "zertx_amt": "부가세 영세 적용 금액 (Numeric)",
            "pos_send_seq": "ERP 전송 배치 기동을 위한 전문 송신 고유 일련번호 (8자리, PK)",
            "pos_send_yn": "ERP 매출 헤더 송신(SUB_IF_HYDM_SEND_P) 연동 완료 여부 플래그 (1자리, 'Y': 전송성공, 'N': 미전송/대기, 'E': 에러)",
            "pos_send_remark": "ERP 전송 실패 시 적재되는 EAI 연동 에러 메시지 (4000자리)",
            "pos_send_create_dtime": "ERP 전송 전문 트랜잭션 최초 생성 일시 (YYYYMMDDHH24MISS)"
        },
        "memo_c": "가맹점 일마감 확정(Pos_SaleInterface_Sql.xml) 또는 매출 마감 정산 데몬 기동 시 매출 총액 요약이 집계 인서트됩니다.",
        "memo_u": "ERP 매출 송신 완료 또는 전송 오류 상황(SaleInterface_SalesAggListDto) 발생 시 전송 결과 상태가 업데이트됩니다.",
        "memo_d": "점포 매출 세무 신고 및 가맹점 정산 수수료 대사의 원천 통계 자료이므로 물리 삭제가 금지됩니다.",
        "memo_r": "가맹점 일별 매출 현황 조회, ERP 일매출 송신(SUB_IF_HYDM_SEND_P), 점포 매출 마감 정합성 검증 및 재무 재산표 작성 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_dtl",
                "description": "매출 거래 결제 상세. [1:N 관계] 영수증 거래 헤더 하위에 귀속되는 결제 수단별 세부 결제 내역(신용카드 승인, 현금 영수증 발행 등)을 매칭하여 정합성을 상호 감사하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_sals_agg_mst",
                "description": "일별 매출 집계 마스터. 가맹점 단위 영업일자별 매출 통계 원장으로, 본 영수증 헤더들의 당일 합산 금액(stl_amt, disc_amt 등)이 집계 테이블의 총량 매출액과 일치하는지 정합성을 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_shop_daycls_mst",
                "description": "일영업 마감 마스터. 해당 영업일자의 점포 마감이 완료(JOBS_CLS_YN = 'Y')되었는지 여부를 매칭하여, 마감 상태의 신규 영수증 생성 및 오입력을 통제하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 원장. 매출이 일어난 점포의 본사 소속 법인 및 매장 명칭, 브랜드 유형을 식별하기 위해 참조합니다."
            },
            {
                "table_name": "if_sedpsvtb",
                "description": "인터페이스 송신 이력 테이블. [1:1 매칭 감사 관계] 매출 헤더 송신 배치/프로시저가 ERP(IF_FB_003)로 송신한 전체 건수 및 EAI 통신 결과 로그를 감사 기록합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. POS에서 승인된 신용카드/결제 수단 거래 건별 카드사, 승인번호 및 금액 정보의 정합성을 대조하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 162. TSM_TRAN_MST_BK MEMO AND RELATED TABLES
    tsm_tran_mst_bk_memo = (
        "### 1. 테이블 개요\n"
        "백업/임시 가맹점 매출 트랜잭션 헤더 마스터 테이블 (`TSM_TRAN_MST_BK`).\n"
        "가맹점 매출 트랜잭션 헤더 마스터 실 운영 테이블 (`TSM_TRAN_MST`)의 과거 구버전 Tibero 레거시 데이터 백업 및 연동 테스트(Shadow Run) 목적으로 설계된 이관 백업 테이블로, 정식 EAI 매출 전송 프로세스에는 간섭하지 않는 독립된 백업 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **레거시 이관 및 쉐도우 테스트 대조**: Tibero 연동 매퍼(`Tibero_SaleInterface_Sql.xml`)에서 개별 가맹점의 일자별 매출 거래 승인 총액 및 과세/면세 집계 수집 정확도를 병행 검증하는 임시 테이블로 사용되었습니다.\n"
        "* **과거 이력 감사**: 마이그레이션 도중 누락되거나 이관이 비정상 종료된 점포의 영수증별 승인 금액 정산 내역 백업본을 추적하고 소급 대사하는 백업 용도로 참조됩니다."
    )

    data["tables"]["tsm_tran_mst_bk"] = {
        "memo": tsm_tran_mst_bk_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "biz_cd": "백업된 가맹점 소속 법인/사업장 코드 (2자리)",
            "shop_cd": "백업된 매장 코드 (2자리, '10': 식당, '20': 숍 등)",
            "occu_dt": "백업된 매출 발생 영업일자 (YYYYMMDD)",
            "bztc_no": "백업된 영수증 일련번호 (20자리)",
            "cncl_clsf_cd": "백업된 취소 구분자 (1자리, '0': 정상, '1': 반품)",
            "appr_amt": "백업된 승인요청 금액 (Numeric)",
            "stl_amt": "백업된 실 결제금액 (Numeric)",
            "disc_amt": "백업된 할인 총액 (Numeric)",
            "asgw_amt": "백업된 할인분담금 (Numeric)",
            "sals_amt": "백업된 매출 금액 (Numeric)",
            "supr_pric": "백업된 공급가액 (Numeric)",
            "vat": "백업된 부가가치세 세액 (Numeric)",
            "msce": "백업된 봉사료 (Numeric)",
            "exnt_amt": "백업된 면세 적용금액 (Numeric)",
            "rgnr_id": "최초 백업 등록자 ID",
            "rgnr_dtm": "최초 백업 수신 등록 일시",
            "updr_id": "최종 백업 수정자 ID",
            "updr_dtm": "최종 백업 수정 및 완료 일시"
        },
        "memo_c": "과거 Tibero DB 데이터 이관 작업 또는 백업 동기화 스크립트 실행 시 백업 레코드가 인서트됩니다.",
        "memo_u": "이력용 테이블이므로 적재 이후의 수정이 거의 발생하지 않으며 정합성 보정에 의해서만 업데이트됩니다.",
        "memo_d": "데이터 복원 및 소급 감사용 백업 테이블이므로 정식 보존 기한이 경과하기 전까지는 삭제가 제한됩니다.",
        "memo_r": "구 Tibero DB 연동 매퍼(Tibero_SaleInterface_Sql) 이관 검증 및 과거 가맹점 영업 마감 대사 이력 대조 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_mst",
                "description": "매출 트랜잭션 헤더. [1:1 대칭 관계] 본 백업 테이블의 원본 데이터가 되는 실 운영 거래 헤더 테이블로, 마이그레이션 교차 대사 시 1:1 조인 대조됩니다."
            },
            {
                "table_name": "tsm_tran_dtl_bk",
                "description": "결제 상세 백업 테이블. [1:N 관계] 영수증 거래 헤더 백업 하위에 귀속되는 결제 수단별 세부 결제 내역 백업본을 추적하고 대사하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_sals_agg_mst_bk",
                "description": "일별 매출 집계 백업 테이블. 가맹점 단위 영업일자별 매출 통계 원장 백업으로, 본 백업 영수증 헤더들의 당일 합산 금액이 집계 백업 테이블의 총량 매출액과 일치하는지 정합성을 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_shop_daycls_mst_bk",
                "description": "일영업 마감 백업 테이블. 해당 일자의 마감 상태 백업본을 추적하여 이관 데이터 완결성을 판정하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 백업 데이터가 유효한 가맹점 소속 및 코드로 귀속되었는지 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 이관된 과거 카드 승인 거래 데이터와의 교차 대사를 위해 조인 참조됩니다."
            }
        ]
    }

    # 163. TSUBMNTB MEMO AND RELATED TABLES
    tsubmntb_memo = (
        "### 1. 테이블 개요\n"
        "세부 서브메뉴(옵션/추가메뉴) 속성 정보 마스터 테이블 (`TSUBMNTB`).\n"
        "브랜드 체인별로 설정 가능한 서브메뉴(추가 옵션/사이드 메뉴)들의 세부 데이터(체인번호 `CHAIN_NO`, 서브그룹코드 `SUB_GROUP_CD`, 서브메뉴코드 `SUB_MENU_CD`, 서브메뉴명 `SUB_MENU_NM`, 재고/옵션 구분 `STOCK_FG`, 연계상품코드 `GOODS_CD`, 추가 금액 `UPCHARGE_UPRICE` 등)를 정의하는 브랜드 메인 메뉴의 옵션 마스터 원장입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **서브메뉴(옵션) 마스터 정의**: 백오피스 상품/메뉴 관리 화면에서 메인 상품에 귀속시킬 옵션 그룹(예: '음료 선택', '토핑 추가' 등)을 정의하고, 해당 그룹에 포함될 세부 옵션명과 가산 금액(Upcharge)을 본 테이블에 등록합니다.\n"
        "* **POS 화면 노출 및 주문 연동**: POS 단말기 로그인 및 메뉴 마스터 수신 시 본 서브메뉴 마스터 데이터가 다운로드되어 화면에 옵션 선택 팝업으로 표출됩니다. 주문이 완료되면 선택된 서브메뉴의 상품코드(`goods_cd`) 및 추가 금액(`upcharge_uprice`)이 매출 영수증 및 정산에 누적 연계 처리됩니다."
    )

    data["tables"]["tsubmntb"] = {
        "memo": tsubmntb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "본사 브랜드 체인 고유 번호 (4자리, PK)",
            "sub_group_cd": "상위 옵션/서브메뉴 그룹코드 (2자리, PK)",
            "sub_menu_cd": "서브메뉴 그룹 내 세부 서브메뉴 식별 순번/코드 (2자리, DISPLAY_ORDER와 매치, PK)",
            "sub_menu_nm": "고객 화면 및 영수증에 출력되는 서브메뉴/옵션 명칭 (120자리)",
            "display_order": "POS 및 키오스크 화면 상의 옵션 노출 정렬 순서 (2자리)",
            "stock_fg": "재고 및 옵션 연동 구분 플래그 (1자리, '1': 재고속성/필수선택, '2': Upcharge/추가선택, '3': 일반메뉴 등)",
            "goods_cd": "서브메뉴 선택 시 연계되어 차감/등록되는 실 상품코드 (20자리)",
            "upcharge_uprice": "옵션 추가 선택 시 메인 메뉴 가격에 추가로 가산되는 단가 금액 (Numeric)",
            "create_dtime": "최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 갱신 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 갱신자 ID"
        },
        "memo_c": "백오피스 메뉴 관리 화면에서 신규 서브메뉴/추가 옵션을 등록할 때 본 테이블에 레코드가 생성됩니다.",
        "memo_u": "옵션명 수정 및 추가금액(Upcharge) 변경 시 백오피스 메뉴 수정을 통해 업데이트됩니다.",
        "memo_d": "과거 판매된 영수증 및 주문 로그의 옵션 참조 무결성을 위해 사용 중인 서브메뉴 옵션의 임의 삭제가 제어됩니다.",
        "memo_r": "POS 메뉴 마스터 동기화, 키오스크 메뉴 구성 조회 및 영수증 주문 옵션 검증 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsubmgtb",
                "description": "서브메뉴 그룹코드 테이블. [N:1 관계] 상위 옵션/서브메뉴 그룹 정의를 참조하여 어떤 메인 메뉴들에 이 옵션 세트가 노출되는지 제어합니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "상품 마스터 테이블. [N:1 관계] 옵션(서브메뉴) 추가 선택 시 실제 차감되는 원천 상품 원장(상품명, 과세구분 등)을 조인 참조합니다."
            },
            {
                "table_name": "mchain_mst",
                "description": "브랜드 체인 마스터. 해당 옵션 메뉴 구성이 적용되는 가맹 브랜드 체인 카테고리를 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 서브메뉴 옵션 템플릿이 배포되는 체인별 매장들의 운영 현황을 조회하기 위해 조인 참조합니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 서브메뉴(옵션) 추가에 따른 카드 승인 금액 변동 정합성을 검증하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 164. TTAXMSTB MEMO AND RELATED TABLES
    ttaxmstb_memo = (
        "### 1. 테이블 개요\n"
        "외국인 사후 면세 환급 연동 마스터 테이블 (`TTAXMSTB`).\n"
        "외국인 관광객이 가맹점에서 구매한 내역에 대해 사후 면세(Tax Refund) 환급 처리를 해 주는 VAN/EDI 연동용 마스터 테이블로, 각 점포별 면세 대행사(글로벌텍스프리 등)의 접속정보(매장번호 `MS_NO`, IP/PORT `TAX_REFD_IP`/`TAX_REFD_PORT`, 환급 가맹번호 `TAX_REFD_NO`, 환급사코드 `REFUND_CD`)를 보관합니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **사후면세 통신 설정 관리**: 점포에서 외국인 사후 면세 환급 전용 영수증을 발행하거나 전송 모듈을 기동할 때, 본 테이블의 IP/Port 및 가맹 번호 정보를 참조하여 면세 대행사(Global Tax Free 등)의 전문 송수신 서버로 승인 연동 처리를 수행합니다.\n"
        "* **여권 스캔 여부 통제**: `passport_fg` 설정을 기반으로 POS 단말기에서 여권 리더기 작동을 강제하거나 수동 입력 화면을 분기 제어하는 정책 관리 용도로 활용됩니다."
    )

    data["tables"]["ttaxmstb"] = {
        "memo": ttaxmstb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "가맹점 고유 매장 번호 (6자리, PK)",
            "tax_refd_ip": "사후 면세 환급 통신 중계 서버 IP 주소",
            "tax_refd_port": "사후 면세 환급 통신 중계 서버 접속 포트 번호 (6자리)",
            "tax_refd_no": "사후 면세 대행사 등록 가맹점 환급 고유번호 (PK)",
            "create_dtime": "최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 갱신 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 갱신자 ID",
            "refund_cd": "사후 면세 환급 대행사 구분 코드 (PK, '01': GTF 등)",
            "gtf_edi": "GTF EDI 연동 구분 코드",
            "passport_fg": "여권 스캐너 사용 여부 플래그 (1자리, '1': 여권스캔 필수)",
            "edi_vs": "EDI 전문 버전 식별 코드",
            "user_name": "대행사 연동 시스템 로그인 계정명",
            "passwd": "대행사 연동 시스템 비밀번호",
            "shop_id": "면세 대행사에 등록된 매장 ID"
        },
        "memo_c": "신규 외국인 사후 면세 가맹 계약 체결 시 백오피스 환경설정에서 대행사 정보가 인서트됩니다.",
        "memo_u": "통신 IP/Port 변경 및 대행사 계약 정보(가맹 번호) 갱신 시 업데이트됩니다.",
        "memo_d": "과거 발행된 사후면세 영수증의 이력 대사를 위해 점포 폐점 전까지는 삭제가 보류됩니다.",
        "memo_r": "POS 단말기의 사후면세 환급 전문 발송 모듈 기동, 여권 리더기 연동 여부 판정 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [N:1 관계] 외국인 사후 면세 환급 단말기 및 전송 가맹 번호 설정을 매장의 실제 가맹점 명칭 및 운영 상태와 매칭하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_tran_mst",
                "description": "매출 트랜잭션 헤더. 사후면세 대상 매출 건에 대해 승인 영수증 거래와 면세 가맹점 연동 번호를 매핑하여 환급 전송 이력을 감사하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "상품 마스터 테이블. 사후면세 환급 대상 거래 내에 포함된 개별 상품이 면세(Tax Free) 혜택 적용이 가능한 면세/과세 상품 카테고리에 속하는지 판정하기 위해 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 사후 면세 환급 대상 카드 매출 승인 내역의 카드 번호 및 승인 금액을 검증하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 165. TVNDRGTB MEMO AND RELATED TABLES
    tvndrgtb_memo = (
        "### 1. 테이블 개요\n"
        "협력업체별 취급 상품 마스터 테이블 (`TVNDRGTB`).\n"
        "체인 브랜드별로 등록된 각 협력업체(거래처)가 공급하는 취급 대상 품목 매핑 정보(체인코드 `CHAIN_NO`, 거래처코드 `VENDOR`, 상품코드 `GOODS_CD`, 주협력업체 구분 `MAIN_VND_FG`, 연계거래처 `JOIN_VENDOR`)를 정의하는 유통 공급망 마스터 원장입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **거래처 품목 매핑 관리**: 백오피스 상품 구매/발주 관리 화면에서 협력업체별 공급 계약 품목들을 등록 및 설정합니다. 단일 상품에 대해 복수의 협력업체가 공급 가능할 경우, `main_vnd_fg = '1'` 플래그를 가진 거래처가 최우선 기본 발주 거래처로 지정됩니다.\n"
        "* **발주 및 매입 단가 연동**: 가맹점/본사 발주 등록 배치 또는 화면에서 특정 협력업체를 선택하여 주문서를 생성할 때 본 테이블에 정의된 취급 상품 목록만 발주 대상으로 조회 제어되며, 매입 정산 및 거래 명세서 생성의 기준 정보가 됩니다."
    )

    data["tables"]["tvndrgtb"] = {
        "memo": tvndrgtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "본사 브랜드 체인 고유 번호 (4자리, PK)",
            "vendor": "물류/자재를 공급하는 협력업체(거래처) 고유 코드 (13자리, PK)",
            "goods_cd": "거래처가 취급/공급하는 마스터 상품코드 (20자리, PK)",
            "create_dtime": "최초 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 갱신 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 갱신자 ID",
            "main_vnd_fg": "해당 품목의 주 공급처(기본 발주 대상 거래처) 여부 플래그 (1자리, '1': 주 거래처)",
            "join_vendor": "해당 협력업체의 통합/정산 대행용 주거래 협력업체 코드 (13자리)"
        },
        "memo_c": "백오피스 거래처/상품 연계 관리에서 협력업체 공급 품목을 신규 등록할 때 레코드가 생성됩니다.",
        "memo_u": "주협력업체 여부 변경 및 공급망 구조 개선에 따른 대행 거래처 수정 시 업데이트됩니다.",
        "memo_d": "미정산 잔액 및 과거 발주 내역과의 일치성(참조 무결성)을 지키기 위해 사용 중인 공급 매핑 레코드는 물리 삭제가 통제됩니다.",
        "memo_r": "점포 발주 요청 화면, 본사 입고 검수 및 매수 거래처 원장 대사 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mgoodstb",
                "description": "상품 마스터 테이블. [N:1 관계] 협력업체가 취급하는 상품의 고유 분류 속성, 과세 여부 및 기준가 정보를 매칭 조회하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mvndrmst",
                "description": "협력업체 마스터 테이블. [N:1 관계] 상품 공급처의 상호명, 사업자 번호, 대금 정산 주기 및 여신 한도를 조회 매칭하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mchain_mst",
                "description": "브랜드 체인 마스터. 협력업체별 취급 상품 관계가 적용되는 브랜드 카테고리를 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 특정 점포의 소속 체인을 매칭하여, 해당 점포에서 취급 가능한 발주 대상 협력업체 목록을 조회할 때 간접 필터링 용도로 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 협력업체 공급 물품 거래 대금 중 카드 결제 처리 건의 정합성을 감사하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 166. TVNDRMTB MEMO AND RELATED TABLES
    tvndrmtb_memo = (
        "### 1. 테이블 개요\n"
        "협력업체/거래처 마스터 정보 테이블 (`TVNDRMTB`).\n"
        "회사 산하 브랜드 체인점에 식자재, 소모품 및 자재를 납품하는 모든 거래처/협력업체의 상세 법인 정보 및 거래 정보(체인번호 `CHAIN_NO`, 거래처코드 `VENDOR`, 협력업체명 `VENDOR_NM`, 대표자명 `PRESIDENT_NM`, 사업자번호 `BS_NO`, 거래처구분 `VENDOR_FG`, 지급 계좌정보 `ACCOUNT_NO` 및 erp 연동용 고객사코드 `ERP_IF_INFO`)를 저장하는 기준정보 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **납품망 및 정산 기준정보 수립**: 백오피스 물류/거래처 관리 화면에서 가맹점에 물품을 공급하는 신규 거래처를 등록하고, 세금계산서 발행 구분(`tax_bill_fg`) 및 과세 여부(`bns_tax_yn`) 정책을 수립합니다.\n"
        "* **본사 매입 채무 및 ERP 연동**: 가맹점 발주에 따라 거래처가 자재를 매장에 배송/입고하면, 본 테이블의 거래처 코드 및 ERP 연동 코드(`erp_if_info` = ERP `CUST_CD`)를 기반으로 매입 정산 확정 전표가 ERP 회계 시스템으로 자동 인터페이스되어 대금 송금 프로세스가 기동됩니다."
    )

    data["tables"]["tvndrmtb"] = {
        "memo": tvndrmtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "chain_no": "본사 브랜드 체인 고유 번호 (4자리, PK)",
            "vendor": "물류/자재를 공급하는 협력업체(거래처) 고유 코드 (13자리, PK)",
            "vendor_nm": "거래처 관리용 공식 상호명 (60자리)",
            "president_nm": "거래처 대표자 성명 (30자리)",
            "corp_fg": "거래처 사업자 구분 플래그 ('1': 법인, '2': 개인)",
            "corp_no": "거래처 주민번호 또는 법인등록번호 (13자리)",
            "bs_no": "국세청 사업자등록번호 (10자리)",
            "bs_type": "사업자 등록증 상의 업태 정보 (80자리)",
            "bs_kind": "사업자 등록증 상의 종목 정보 (80자리)",
            "zip_no": "우편번호 (6자리)",
            "bs_addr": "기본 사업장 주소 (80자리)",
            "bs_addr_bunji": "상세 사업장 번지 주소 (80자리)",
            "tel_no": "대표 사무실 전화번호 (15자리)",
            "fax_no": "대표 팩스 번호 (15자리)",
            "hp_no": "대표 휴대폰 번호 (15자리)",
            "e_mail": "거래처 대표 또는 세금계산서 수신용 이메일 (30자리)",
            "account_nm": "정산 대금 입금용 예금주명 (30자리)",
            "bank_cd": "정산 대금 송금 대상 금융기관 은행코드 (3자리)",
            "account_no": "정산 대금 송금 대상 계좌번호 (30자리)",
            "remark": "기타 특이사항 기재란 (100자리)",
            "create_date": "최초 거래처 등록 일자 (YYYYMMDD)",
            "create_id": "최초 등록자 ID",
            "last_date": "최종 정보 수정 일자 (YYYYMMDD)",
            "last_id": "최종 수정자 ID",
            "vendor_fg": "거래처 성격 구분 코드 (0: 매입, 1: 매출, 2: 매입+매출, 3: 본사, 4: 일반 등)",
            "sub_inv_fg": "부자재 매입 통제 구분 플래그",
            "bns_tax_yn": "거래처 공급 품목 면세 여부 플래그 (1자리, 'Y': 면세, 'N': 과세)",
            "bur_bns_no": "관할 세무서 식별 코드 (4자리)",
            "contact_ps_nm": "주요 연락 대상 담당자 이름 (30자리)",
            "contact_phone_no": "담당자 휴대폰 번호 (11자리)",
            "erp_if_info": "본사 전사 ERP 시스템의 고객사/거래처 연동 코드 (30자리, CUST_CD 매핑)",
            "tax_bill_fg": "전자세금계산서 발행 유형 구분자 (0: 건별, 1: 월합산 등)",
            "sub_yn": "부자재 거래처 여부 플래그 (Y/N)",
            "vendor_nm_sub": "웹 백오피스 표기용 요약 거래처명 (60자리)",
            "ven_use_fg": "거래처 사용 중단 여부 플래그 (1자리, '0': 미사용/거래정지, '1': 정상사용)",
            "ven_top_fg": "대표 공급사 여부 구분 코드 (0: 일반, 1: 대표)",
            "top_vendor": "상위 통합 본사 거래처 코드 (13자리)",
            "contact_tel_no": "담당자 유선 연락처 (15자리)"
        },
        "memo_c": "신규 자재 납품 협력업체 계약 체결 시 백오피스 거래처 등록 화면을 통해 레코드가 인서트됩니다.",
        "memo_u": "거래처 계좌번호 변경, 담당자 수정, 또는 사용 여부(ven_use_fg) 차단 시 백오피스에서 업데이트됩니다.",
        "memo_d": "매입 전표 세무 마감 무결성을 위해 실 거래 이력이 누적된 거래처는 삭제가 불가능하며 사용 플래그를 미사용('0')으로 전환합니다.",
        "memo_r": "가맹점 발주 화면, 자재 수불 정산 리포트, ERP 회계 마감 세금계산서 발행 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tvndrgtb",
                "description": "협력업체 취급 상품 테이블. [1:N 관계] 협력업체 마스터 정보에 정의된 공급업체가 취급 및 공급하는 개별 원부자재 및 상품 목록을 조회 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mgoodstb",
                "description": "상품 마스터 테이블. 특정 품목의 거래처 및 공급업체 정보를 갱신할 때 본 테이블의 유효한 협력업체 코드가 조인 매칭됩니다."
            },
            {
                "table_name": "mchain_mst",
                "description": "브랜드 체인 마스터. [N:1 관계] 협력업체 계약이 어떤 브랜드 사업군에 귀속되어 자재 공급망을 형성하는지 관리하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 가맹점별로 거래하는 로컬 협력업체 또는 전국망 공동 물류 공급처의 대금 지급 계좌 및 사업자 번호를 조회할 때 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. 협력업체 정산 대금 중 신용카드 결제 및 매입 청구 거래 내역을 매칭하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 167. VANMSTTB MEMO AND RELATED TABLES
    vanmsttb_memo = (
        "### 1. 테이블 개요\n"
        "VAN사 IP/PORT 통신 마스터 테이블 (`VANMSTTB`).\n"
        "가맹점 단말기 및 POS 결제 연동에서 사용되는 신용카드 승인 및 현금영수증 발행용 VAN(Value Added Network) 서비스사들의 통신 파라미터(VAN코드 `VAN_CD`, 구분 `VAN_FG`, IP주소 `VAN_IP`, 포트번호 `VAN_PORT_NO`, VAN사명 `VAN_NAME`)를 관리하는 기준 통신 마스터 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **VAN 통신 연동 라우팅**: POS 단말기가 결제 거래(신용카드, 현금영수증 등) 승인을 시도할 때 본 테이블에서 지정한 IP와 포트 번호 정보를 실시간으로 질의하여 소켓 통신을 연결하고 전문을 송수신합니다.\n"
        "* **다중 VAN사 관리**: 동일 VAN사 코드 내에서도 카드 승인(`van_fg = '0'`)과 현금 영수증(`van_fg = '1'`) 발행 전송 서버 IP와 포트를 다르게 설정하여 처리 효율 및 트래픽 분기를 보장합니다."
    )

    data["tables"]["vanmsttb"] = {
        "memo": vanmsttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "van_cd": "VAN 서비스사 식별 코드 (2자리, PK, '01': KIS, '02': JTNET, '03': NICE 등)",
            "van_fg": "VAN 서비스 기능 구분자 (1자리, PK, '0': 신용카드 승인, '1': 현금영수증 발행)",
            "van_ip": "VAN사 승인 중계 서버 IP 주소 (20자리)",
            "van_port_no": "VAN사 승인 중계 서버 통신 포트 번호 (5자리)",
            "van_name": "VAN 서비스 업체 공식 명칭 (20자리)",
            "create_dtime": "최초 통신 설정 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 통신 설정 변경 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 변경자 ID"
        },
        "memo_c": "신규 VAN사 연동 추가 또는 승인 단말망 변경 시 백오피스 환경설정에서 통신 IP/Port 레코드가 생성됩니다.",
        "memo_u": "VAN사의 서버 이전, 통신 프로토콜 변경 또는 포트 업데이트 시 백오피스에서 수정 적용됩니다.",
        "memo_d": "과거 발행된 영수증 승인 내역의 소급 조회 및 거래 정합성 대사를 위해 물리 삭제가 통제됩니다.",
        "memo_r": "POS 결제 승인 모듈 기동, VAN 소켓 통신 에러 발생 시 장애 대응 관리 화면에서 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_dtl",
                "description": "가맹점 매출 거래 결제 상세. 승인 영수증에 포함된 개별 결제 수단의 승인 VAN사 정보와 연동하여 정합성을 상호 감사하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 각 가맹점 점포가 계약 및 사용 중인 카드 단말기 VAN 대행 정보와 본 통신 포트 설정을 대조하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 거래 내역 테이블. [N:1 관계] 카드 승인 내역에 적재된 VAN사 코드를 기반으로 승인 중계 통신 채널을 검증하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 168. WEASCDTB MEMO AND RELATED TABLES
    weascdtb_memo = (
        "### 1. 테이블 개요\n"
        "외상매출 카드 승인 거래 내역 테이블 (`WEASCDTB`).\n"
        "가맹점 POS 단말기에서 신용카드 및 외상 거래 결제 시 발생하는 모든 카드 승인 전문 및 거래 내역(매출일자 `SALE_DATE`, 매장번호 `MS_NO`, POS번호 `POS_NO`, 영수증번호 `BILL_NO`, 승인금액 `APPR_AMT`, 승인번호 `APPR_NO`, 카드번호 `CARD_NO`, 카드사코드 `CARD_CO`, VAN사코드 `VAN_CD` 등)을 기록하는 카드 결제 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **카드 승인 내역 저장**: POS 단말기에서 카드 단말기 연동 또는 수동 KEY-IN을 통해 카드 승인을 완료하면, 승인번호(`appr_no`) 및 승인 일시, 발급사/매입사 정보와 함께 본 테이블에 결제 데이터가 적재됩니다.\n"
        "* **카드사 매입 청구 및 수수료 정산**: 본 테이블의 원장 데이터를 기준으로 전사 재무 시스템에서 카드사별 청구(DDC/EDI)를 기동하고, 승인액 대비 실제 카드 수수료(`card_fee_amt`)를 제외한 대금 입금 예정일을 계산 및 통제합니다."
    )

    data["tables"]["weascdtb"] = {
        "memo": weascdtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "거래가 발생한 영업일자 (YYYYMMDD, PK)",
            "ms_no": "거래가 발생한 매장 고유 번호 (6자리, PK)",
            "pos_no": "결제를 진행한 POS 단말기 번호 (2자리, PK)",
            "bill_no": "매출 영수증 일련번호 (4자리, PK)",
            "card_seq": "단일 영수증 내 다중 카드 결제 시 발급되는 카드 거래 순번 (2자리, PK)",
            "chain_no": "본사 브랜드 체인 고유 번호 (4자리)",
            "chain_area": "브랜드 체인 지역/지사 분류 코드 (3자리)",
            "sale_fg": "매출 구분 플래그 (1자리, '0': 정상 승인, '1': 승인 취소/반품)",
            "card_no": "결제에 사용된 신용카드 번호 (16자리, 마스킹 처리)",
            "card_data": "카드 마그네틱/IC칩 리딩 풀 데이터",
            "input_fg": "카드 번호 입력 방식 플래그 (1자리, '0': SWIPE/MSR 리딩, '1': KEY-IN 수동입력)",
            "appr_amt": "카드 승인 완료된 총 결제 금액 (Numeric)",
            "appr_no": "카드사/VAN사에서 발급한 승인 고유번호 (8자리)",
            "appr_date": "실제 카드사 승인 일자 (YYYYMMDD)",
            "valid_term": "카드 유효기간 (YYMM)",
            "inst_mcnt": "할부개월수 (0: 일시불, 그 외 할부 개월 수)",
            "card_co": "결제 카드사 분류 코드 (3자리)",
            "van_cd": "승인 처리를 수행한 VAN사 코드 (2자리)",
            "msg_cd": "통신 응답 메시지 코드 (4자리)",
            "cancel_cd": "취소 사유 및 구분 코드 (4자리)",
            "org_appr_date": "취소 시 대조 대상이 되는 원거래 승인 일자 (YYYYMMDD)",
            "org_appr_no": "취소 시 대조 대상이 되는 원거래 승인 번호 (8자리)",
            "sale_dtime": "카드 승인 전문 최종 송수신 완료 일시 (YYYYMMDDHH24MISS)",
            "appr_fg": "승인 상태 구분 플래그 ('0': 승인완료, '1': 승인대기 등)",
            "sale_type": "데이터 연동 전송 타입 구분자 (2자리)",
            "cat_id": "신용카드 단말기 고유 다운로드 번호 (CAT_ID, 10자리)",
            "card_rate": "카드 승인 수수료율 (Numeric)",
            "card_fee_amt": "카드 승인 수수료 금액 (Numeric)",
            "demand_fg": "카드사 청구 여부 플래그 (1자리, '0': 청구대기, '1': 청구완료, '9': 에러/보류)",
            "expect_date": "카드 대금 입금 예정 영업일자 (YYYYMMDD)",
            "demand_date": "카드 청구 작업 일자 (YYYYMMDD)",
            "in_date": "카드사 대금 실제 입금 완료 일자 (YYYYMMDD)",
            "last_dtime": "최종 정보 수정 및 청구 리턴 수신 일시 (YYYYMMDDHH24MISS)",
            "biz_no": "가맹점 사업자등록번호 (10자리)",
            "issue_card_cd": "카드 발급사 고유 코드 (4자리)",
            "issue_card_nm": "카드 발급사 명칭 (30자리)",
            "purch_card_cd": "카드 매입사 고유 코드 (4자리)",
            "purch_card_nm": "카드 매입사 명칭 (30자리)",
            "card_join_no": "카드사 계약 가맹점 번호 (15자리)",
            "ddc_co": "DDC 매입 대행사 구분 코드",
            "retn_fg": "카드 청구 반송 구분자",
            "easy_check": "간편결제 승인 여부 플래그",
            "card_dc_amt": "카드 제휴사 즉시 할인 적용 금액 (Numeric)",
            "multi_biz_cd": "복수 사업장 구분 고유 코드 (2자리)",
            "sign_pad_fg": "서명패드 사용 및 서명 데이터 수집 여부 플래그 (1자리, 'A': 서명패드 자동)",
            "card_tip_amt": "봉사료 팁 승인 금액 (Numeric)",
            "dc_appr_fg": "카드사 프로모션 할인 승인 구분 플래그",
            "altercd_fg": "대체 정산 구분 코드",
            "sale_vat": "카드 승인금액에 포함된 부가가치세 세액 (Numeric)",
            "net_sale_amt": "부가세를 제외한 순수 카드 승인 공급금액 (Numeric)",
            "reward_card_fg": "카드 포인트/리워드 사용 플래그",
            "mpoint_amt": "현대카드 M포인트 등 포인트 승인 금액 (Numeric)",
            "mpoint_divide": "포인트 분담 결제액 (Numeric)",
            "appr_time": "실제 카드사 승인 시간 (HH22MISS)",
            "pay_type": "결제 유형 구분 플래그 (1자리, '0': 일반 고객결제, '1': 외상대금 결제)"
        },
        "memo_c": "가맹점 POS 단말기에서 실시간 카드 결제 승인 완료 시 결제 건이 인서트됩니다.",
        "memo_u": "카드사 대금 매입 청구 결과 피드백 수신 또는 정산 완료 시 청구상태 및 입금일자가 업데이트됩니다.",
        "memo_d": "가맹점 카드 수수료 대사 및 전사 부가세 매출 신고의 핵심 증빙 원장이므로 임의 삭제가 절대 금지됩니다.",
        "memo_r": "영수증별 카드 정산 현황 조회, 카드사 매입 청구(DDC/EDI) 연동 모듈, 일별 카드 입금 대사 조회 시 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_dtl",
                "description": "매출 거래 결제 상세. [1:1 매칭 관계] POS에서 발생한 신용카드/결제 수단 상세 내역과 본 카드 승인 원장의 결제금액 및 승인번호 정합성을 1:1 대조 및 감사하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_tran_mst",
                "description": "매출 트랜잭션 헤더. 카드 결제가 발생한 원천 영수증 거래의 취소 여부(cncl_clsf_cd) 및 총 결제금액 정합성을 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [N:1 관계] 카드 결제가 일어난 매장의 사업자등록번호(biz_no) 및 소속 체인 브랜드를 식별하여 카드사 가맹번호 매칭 시 조인 참조됩니다."
            },
            {
                "table_name": "vanmsttb",
                "description": "VAN사 마스터 테이블. [N:1 관계] 결제 승인을 중계한 VAN사 정보(NICE, KIS 등)를 매칭하여 통신 장애 이력 분석 시 조인 참조됩니다."
            }
        ]
    }

    # 169. WEASCHTB MEMO AND RELATED TABLES
    weaschtb_memo = (
        "### 1. 테이블 개요\n"
        "외상매출 현금영수증 승인 거래 내역 테이블 (`WEASCHTB`).\n"
        "가맹점 POS 단말기에서 현금 및 외상거래 수납 후 발생하는 모든 국세청 현금영수증 발행 전문 및 거래 내역(매출일자 `SALE_DATE`, 매장번호 `MS_NO`, POS번호 `POS_NO`, 영수증번호 `BILL_NO`, 승인금액 `SANCT_AMT`, 현금영수증 승인번호 `CASH_APPR_NO`, 식별자 `IDENTIFY_NO`, 소득공제/지출증빙 구분 `TRADE_FG`, 현금 VAN사코드 `CASH_VAN_CD` 등)을 기록하는 현금영수증 결제 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **현금영수증 승인 및 발행**: POS 단말기에서 고객이 현금영수증 발행을 요청하여 승인 요청이 기동되면, 지정된 현금영수증 VAN사(`cash_van_cd`)를 통해 국세청 승인을 취득하여 승인번호(`cash_appr_no`)를 본 테이블에 적재합니다.\n"
        "* **세무 신고 및 정합성 검증**: 당일 발행된 현금영수증 정상 매출액 및 취소액을 집계하여 국세청 전송용 마감 전표와 1:1 대사하며, 본사 세무 신고 자료의 기초 데이터가 됩니다."
    )

    data["tables"]["weaschtb"] = {
        "memo": weaschtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "거래가 발생한 영업일자 (YYYYMMDD, PK)",
            "ms_no": "거래가 발생한 매장 고유 번호 (6자리, PK)",
            "pos_no": "결제를 진행한 POS 단말기 번호 (2자리, PK)",
            "bill_no": "매출 영수증 일련번호 (4자리, PK)",
            "seq_no": "단일 영수증 내 다중 현금 결제/발행 시 발급되는 현금 거래 순번 (2자리, PK)",
            "cash_van_cd": "현금영수증 승인 처리를 수행한 VAN사 코드 (2자리)",
            "chain_no": "본사 브랜드 체인 고유 번호 (4자리)",
            "chain_area": "브랜드 체인 지역/지사 분류 코드 (3자리)",
            "sale_fg": "매출 구분 플래그 (1자리, '0': 정상 발행, '1': 발행 취소/반품)",
            "input_fg": "현금영수증 인증 정보 입력 방식 구분자 (0: MSR, 1: IC Card, 2: Key-In)",
            "identify_fg": "인증 수단 분류 플래그 (휴대폰번호, 카드번호, 사업자번호 등)",
            "identify_no": "현금영수증 발급용 국세청 등록 인증 번호 (37자리, 마스킹 처리)",
            "trade_fg": "현금영수증 발행 목적 구분 코드 ('1': 개인소득공제용, '2': 법인지출증빙용)",
            "sanct_amt": "현금영수증 발행 대상 총 승인 금액 (Numeric)",
            "cash_appr_no": "국세청/VAN사에서 발급한 현금영수증 승인 고유번호 (12자리)",
            "cash_appr_date": "실제 현금영수증 국세청 승인 일자 (YYYYMMDD)",
            "appr_time": "실제 현금영수증 국세청 승인 시간 (HH24MISS)",
            "trade_appr_no": "국세청 승인과 연계된 내부 거래 고유 승인번호 (12자리)",
            "trade_appr_date": "내부 거래 승인 일자 (YYYYMMDD)",
            "sale_dtime": "현금영수증 통신 전문 최종 완료 일시 (YYYYMMDDHH24MISS)",
            "cancel_reason_fg": "현금영수증 승인 취소 사유 코드 (1자리)",
            "sale_vat": "현금영수증 승인금액에 포함된 부가가치세 세액 (Numeric)",
            "net_sale_amt": "부가세를 제외한 순수 현금영수증 공급가액 (Numeric)",
            "appr_fg": "승인 상태 분류 플래그 ('0': 현금영수증 정상, '1': 단순 현금 거래)",
            "appr_type": "결제 수단 세부 분류 ('0': 현금, '1': 회사 자사 상품권, '2': 제휴 타사 상품권, '3': 기타)",
            "pay_type": "결제 유형 구분 플래그 (1자리, '0': 일반 고객결제, '1': 외상대금 결제)"
        },
        "memo_c": "가맹점 POS 단말기에서 실시간 현금영수증 발행 및 현금 승인 완료 시 결제 건이 인서트됩니다.",
        "memo_u": "현금영수증 승인 취소 또는 반품 처리에 따른 금액 갱신 시 업데이트됩니다.",
        "memo_d": "전사 부가세 자진 신고 및 세무 감사 증빙의 기초 원장이므로 임의 삭제가 원천 금지됩니다.",
        "memo_r": "영수증별 현금영수증 발행 현황 조회, 국세청 현금영수증 승인 내역 대사 및 세출 결산 조회 시 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_dtl",
                "description": "매출 거래 결제 상세. [1:1 매칭 관계] POS에서 발행된 현금영수증 및 현금 결제 수단 상세 내역과 본 현금영수증 승인 내역의 승인번호 및 금액 정합성을 1:1 대조 감사하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_tran_mst",
                "description": "매출 트랜잭션 헤더. 현금영수증 거래가 포함된 원천 영수증의 매출 정상/반품 구분 및 공급가액 정합성을 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 현금영수증 발급 주체인 가맹점 매장의 사업자등록번호(biz_no) 및 상호를 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "vanmsttb",
                "description": "VAN사 마스터 테이블. [N:1 관계] 현금영수증 발행을 대행한 VAN사의 통신 채널 장애 감사 및 라우팅 상태 조회를 위해 조인 참조됩니다."
            }
        ]
    }

    # 170. WEASDTTB MEMO AND RELATED TABLES
    weasdttb_memo = (
        "### 1. 테이블 개요\n"
        "외상대금 수납/입고 결제 상세 테이블 (`WEASDTTB`).\n"
        "점포에서 외상 거래(Credit Sales)로 누적된 외상 채권에 대해 사후 대금 수납 및 입금(현금, 신용카드, 세금계산서 정산 등) 처리가 발생할 때, 해당 수납 거래 상세 내역(매출일자 `SALE_DATE`, 매장번호 `MS_NO`, POS번호 `POS_NO`, 영수증번호 `BILL_NO`, 라인번호 `LINE_NO`, 수납금액 `PAID_AMT`, 수납수단별 금액 `CASH_AMT`/`CARD_AMT`/`INVOICE_AMT`, 원거래 외상 영수증번호 `ORG_BILL_NO` 등)을 기록하는 외상대금 정산 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **외상 채권 수납 처리**: 외상 고객(단체 회원 또는 거래처)이 방문하거나 계좌이체 등을 통해 밀린 외상대금을 변제하면 POS 단말기에서 '외상대금 수납' 거래를 등록합니다. 이 때 원거래 영수증번호(`org_bill_no`)와 조인 매칭되어 외상 채권 잔액이 수납금액(`paid_amt`)만큼 실시간 차감 처리됩니다.\n"
        "* **다양한 결제수단 연동**: 수납 시 현금 수납(`cash_amt`), 신용카드 수납(`card_amt`), 세금계산서 수납(`invoice_amt`) 등 각 수단별로 대금이 나뉘어 기록되며, 각각 현금영수증 승인 원장(`WEASCHTB`) 및 카드 승인 원장(`WEASCDTB`)의 개별 트랜잭션과 조인되어 정합성이 상호 검증됩니다."
    )

    data["tables"]["weasdttb"] = {
        "memo": weasdttb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "외상대금 수납 거래가 발생한 당일 영업일자 (YYYYMMDD, PK)",
            "ms_no": "수납을 진행한 매장 고유 번호 (6자리, PK)",
            "pos_no": "수납 거래를 입력한 POS 단말기 번호 (2자리, PK)",
            "bill_no": "수납 영수증 일련번호 (4자리, PK)",
            "line_no": "단일 수납 영수증 내 다중 분할 수납 시 발행되는 라인번호 (2자리, PK)",
            "paid_date": "실제 외상대금이 본사/점포에 수납/입금된 일자 (YYYYMMDD)",
            "chain_no": "본사 브랜드 체인 고유 번호 (4자리)",
            "sale_fg": "매출 구분 플래그 (1자리, '0': 정상 수납, '1': 수납 취소)",
            "weas_fg": "외상 채권 수납 처리 상태 코드 (0: 미납/정상 수납, 1: 부도/미수, 2: 대손상각 등)",
            "paid_amt": "금번 수납 처리된 총 외상대금 (Numeric)",
            "emp_id": "수납 거래를 처리한 담당 직원/사원 ID (4자리)",
            "cash_amt": "외상대금 중 현금으로 수납된 금액 (Numeric)",
            "card_amt": "외상대금 중 신용카드로 승인/수납된 금액 (Numeric)",
            "invoice_amt": "외상대금 중 세금계산서 발행 및 이체 등으로 수납된 금액 (Numeric)",
            "org_bill_no": "수납 대상이 되는 원본 외상매출 전표/영수증 번호 (20자리, PK index)",
            "slip_cnt": "수납과 연계된 매출 슬립 전표 수 (Numeric)",
            "deposit_dtime": "수납 대금 최종 입금완료 일시 (YYYYMMDDHH24MISS)",
            "opt_card_co": "수납 시 사용된 신용카드사 분류 코드 (3자리)",
            "opt_card_no": "수납 시 사용된 신용카드 번호 (16자리)",
            "create_dtime": "최초 수납 정보 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID",
            "last_dtime": "최종 수납 정보 변경 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정자 ID"
        },
        "memo_c": "가맹점 POS 단말기 또는 백오피스 미수금 관리 화면에서 외상대금 수납 확정 시 레코드가 생성됩니다.",
        "memo_u": "오입력에 따른 수납 취소 또는 정산 상태 변경 시 업데이트됩니다.",
        "memo_d": "미수 채권 관리 및 세무 회계상의 채권 회수 증빙 원장이므로 임의 삭제가 통제됩니다.",
        "memo_r": "외상 매출 정산 및 미수금 현황 보고서 조회, 고객사별 외상 원장 대사 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_dtl",
                "description": "매출 거래 결제 상세. [1:1 매칭 관계] 외상대금 수납 거래가 발생한 영수증 내 개별 결제 상세 수단(현금, 카드 등)과 본 수납 원장의 결제 수단별 실입금 정합성을 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_tran_mst",
                "description": "매출 트랜잭션 헤더. 외상 수납 처리가 일어난 당일의 정산 영수증 헤더와 매출액 정합성을 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 외상 수납 거래를 발생시킨 매장의 정보와 본사 소속 체인을 매핑하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weascdtb",
                "description": "외상매출 카드 승인 내역. [1:N 관계] 외상대금 수납 수단 중 카드 수납이 발생한 경우, 해당 거래에 매핑되는 개별 신용카드 승인 고유 상세 정보를 조회하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weaschtb",
                "description": "외상매출 현금영수증 승인 내역. [1:N 관계] 외상대금 수납 수단 중 현금영수증 수납이 발생한 경우, 해당 거래에 매핑되는 개별 현금영수증 승인 상세 정보를 조회하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 171. WEASIVTB MEMO AND RELATED TABLES
    weasivtb_memo = (
        "### 1. 테이블 개요\n"
        "외상대금 세금계산서 수납 거래 내역 테이블 (`WEASIVTB`).\n"
        "점포에서 외상 거래로 발생한 미수 대금에 대해 고객사(기업/거래처)에 세금계산서를 역발행하거나 증빙을 발급하여 외상금을 수납 정산할 때, 계산서 승인 상세 내역(매출일자 `SALE_DATE`, 매장번호 `MS_NO`, POS번호 `POS_NO`, 영수증번호 `BILL_NO`, 체인번호 `CHAIN_NO`, 계산서순번 `INV_SEQ`, 매출구분 `SALE_FG`, 계산서유형 `ISSUE_FG`, 고객사코드 `VENDOR_CD`, 세금계산서 공급금액 `APPR_AMT`, 사업자번호 `VENDOR_BIZ_NO` 및 세액 `SALE_VAT`)을 관리하는 회계 정산 원장 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **기업 거래처 외상 계산서 발행 수납**: 법인/단체 등 외상 거래처가 월말에 외상 대금 정산을 위해 세금계산서 발행을 요청하면, POS 또는 백오피스에서 정산 계산서 레코드를 생성합니다. 이 때 국세청 전자세금계산서 연동 모듈 또는 수동 증빙 처리로 이관되어 세무 신고용 계산서 파일이 매칭 발행됩니다.\n"
        "* **수납 원장과의 정합성 통제**: 세금계산서 발행액(`appr_amt` 및 `sale_vat`)은 외상대금 수납 상세 테이블(`WEASDTTB`)의 계산서 수납액(`invoice_amt`) 및 거래처 마스터 정보(`TVNDRMTB`)와 실시간 조인 대사되어 법인 명의 및 사업자등록번호의 무결성을 교차 감사합니다."
    )

    data["tables"]["weasivtb"] = {
        "memo": weasivtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "sale_date": "외상대금 세금계산서 수납 거래가 발생한 영업일자 (YYYYMMDD, PK)",
            "ms_no": "거래를 처리한 매장 고유 번호 (6자리, PK)",
            "pos_no": "수납 거래를 입력한 POS 단말기 번호 (2자리, PK)",
            "bill_no": "수납 영수증 일련번호 (4자리, PK)",
            "chain_no": "본사 브랜드 체인 고유 번호 (4자리)",
            "inv_seq": "단일 영수증 내 계산서 분할 발행 시 발급되는 일련번호 (2자리, PK)",
            "sale_fg": "매출 구분 플래그 (1자리, '0': 정상 발행, '1': 발행 취소/반품)",
            "issue_fg": "세금계산서 발행 방식 구분 코드 (1자리, '0': 수동/종이발행, '1': 국세청 전자세금계산서)",
            "vendor_cd": "정산 대상 법인 거래처/회원 고유 코드 (10자리)",
            "appr_amt": "세금계산서에 명시된 부가세 제외 순수 공급가액 (Numeric)",
            "vendor_biz_no": "거래처 법인 사업자등록번호 (20자리)",
            "vendor_corp_nm": "거래처 공식 법인/상호명 (50자리)",
            "vendor_repn_nm": "거래처 대표자 성명 (50자리)",
            "sale_vat": "세금계산서에 명시된 부가가치세 세액 (Numeric)",
            "pay_type": "결제 유형 구분 플래그 (1자리, '0': 일반 고객결제, '1': 외상대금 결제)"
        },
        "memo_c": "백오피스 외상대금 정산 화면 또는 가맹점 POS에서 세금계산서 수납 발행 완료 시 레코드가 생성됩니다.",
        "memo_u": "세금계산서 발행 취소, 국세청 승인 번호 피드백 반영 시 업데이트됩니다.",
        "memo_d": "세무 신고용 전자세금계산서 국세청 전송 증빙 자료이므로 임의 삭제가 절대 불가능합니다.",
        "memo_r": "외상대금 정산 현황 보고서, 매출 세금계산서 합계표 출력, 국세청 세무 마감 감사 시 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "tsm_tran_dtl",
                "description": "매출 거래 결제 상세. [1:1 매칭 관계] 외상수납 매출 거래 중 세금계산서 정산 결제 수단으로 분류된 결제액과 본 계산서 승인 공급액의 정합성을 1:1 교차 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tsm_tran_mst",
                "description": "매출 트랜잭션 헤더. 세금계산서 발행 대상 원천 영수증의 매출 상태 및 당일 정산 마감 정보를 매칭하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. 계산서 발급 공급자(매장)의 사업자등록번호(biz_no) 및 상호를 식별하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "weasdttb",
                "description": "외상대금 수납 상세. [1:N 관계] 외상대금 수납 거래의 세금계산서 수납 수단별 집계 상세 내역(invoice_amt)을 검증하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tvndrmtb",
                "description": "협력업체 마스터 테이블. 외상 거래처의 공식 등록 정보(상호, 대표자, 업태)와 계산서 발행 시 입력된 거래처 실 정보의 정합성을 상호 검증하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 172. WFNENVTB MEMO AND RELATED TABLES
    wfnenvtb_memo = (
        "### 1. 테이블 개요\n"
        "가맹점별 웹 기능 사용 및 환경설정 제어 테이블 (`WFNENVTB`).\n"
        "체인점 관리 및 모바일/스마트 백오피스 웹 연동 시, 각 점포별로 허용되는 전용 기능의 사용 여부 및 연동 옵션(매장번호 `MS_NO`, 체인번호 `CHAIN_NO`, 기능구분코드 `WFUNCTION` [시스템 공통코드 NM_FG='007' 매칭], 활성화 설정값 `WENV`)을 저장하는 가맹점 웹 솔루션 옵션 제어 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **가맹점별 맞춤형 솔루션 배포**: 매장별 스마트 오더 연동, 모바일 매출 통계 웹 화면 열람 권한, 기프티콘 사용 여부 등 백오피스 웹과 연계되는 개별 기능들에 대해 본 테이블의 `wenv` 값을 기준으로 가맹점의 조작 권한 및 UI 활성화를 실시간 제어합니다.\n"
        "* **POS 단말 및 ERP 설정 다운로드**: 가맹점 POS 프로그램이 부팅되거나 웹 백오피스 로그인 시, 본 테이블에 설정된 매장별 허용 기능 리스트(`wfunction`)를 쿼리하여 점포 단말의 특정 연동 모듈을 구동할지 최종 판정합니다."
    )

    data["tables"]["wfnenvtb"] = {
        "memo": wfnenvtb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "ms_no": "기능 설정을 적용할 가맹점 매장 고유 번호 (6자리, PK)",
            "chain_no": "본사 브랜드 체인 고유 번호 (4자리)",
            "wfunction": "제어 대상이 되는 웹 연동 기능 고유 코드 (2자리, PK, 공통코드 NM_FG='007' 참조)",
            "wenv": "해당 기능의 가맹점 활성화 여부 값 (1자리, '0': 미사용/비활성, '1': 사용/활성)",
            "create_dtime": "최초 기능 설정 및 권한 부여 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (8자리)",
            "last_dtime": "최종 기능 설정 변경 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 수정자 ID (8자리)"
        },
        "memo_c": "백오피스 가맹점별 부가기능 계약 등록 화면에서 신규 솔루션(예: Kiosk 오더, 배달앱 연동 등) 권한 부여 시 레코드가 생성됩니다.",
        "memo_u": "가맹점 요청에 의한 웹 기능의 중단, 사용 정지 또는 재기동 시 백오피스에서 환경설정 값을 수정합니다.",
        "memo_d": "가맹점별 히스토리 추적 및 사용 권한 정합성을 위해 기능 이력이 존재하면 삭제하지 않고 비활성('0') 처리하는 것을 권장합니다.",
        "memo_r": "점포 모바일 백오피스 시스템 로그인, POS 단말 부팅 시 가맹점별 사용 가능 모듈 권한 검증용으로 조회 참조됩니다.",
        "related_tables": [
            {
                "table_name": "mmembstb",
                "description": "가맹점 마스터 테이블. [N:1 관계] 기능 설정을 조정한 특정 점포의 운영 상태, 본사 소속 체인 및 점주 계정 유효성을 확인하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mchain_mst",
                "description": "브랜드 체인 마스터. 브랜드 단위로 신규 웹 기능을 일괄 사용 통제하거나 공통 정책을 전파할 때 체인 매칭 용도로 조인 참조됩니다."
            },
            {
                "table_name": "wposmstb",
                "description": "POS 단말 마스터. 웹 기능 설정(모바일 예약 연동, 테이블 오더 연동 등) 변경 시 해당 설정 데이터를 POS 단말기로 연계 다운로드하기 위해 조인 참조됩니다."
            }
        ]
    }

    # 173. MENUMCTB MEMO AND RELATED TABLES
    menumctb_memo = (
        "### 1. 테이블 개요\n"
        "웹/백오피스 메뉴 중분류 관리 테이블 (`MENUMCTB`).\n"
        "통합 웹 백오피스 및 점주 포털 사이트의 사이드바 메뉴 구조를 구성할 때 대분류 메뉴(`MENULCTB`)와 상세 실행 화면(`MENUMMTB`) 사이를 연결해 주는 카테고리 계층 정보(대분류코드 `MENU_LCLASS_CD`, 중분류코드 `MENU_MCLASS_CD`, 중분류명 `MENU_MCLASS_NM`, 정렬순서 `MCLASS_PERIOD`, 메뉴유형 `MENU_TYPE`, 시스템구분 `SYSTEM_TYPE` 등)를 보관하는 백오피스 메뉴 기준정보 테이블입니다.\n\n"
        "### 2. 비즈니스 로직 및 연계 관리 흐름\n"
        "* **동적 사이드바 렌더링**: 관리자 또는 점주가 웹 백오피스에 로그인하면, 소속 시스템 유형(`HQ`: 본사 관리자, `ST`: 가맹점주)에 해당하는 대분류 및 중분류 카테고리를 쿼리하여 메뉴 네비게이션 트리를 동적으로 생성합니다.\n"
        "* **메뉴 정렬 및 맵핑 통제**: `mclass_period` 우선순위 값을 기준으로 화면상 노출 순서를 정렬하고, `menu_type`이 메뉴 링크('M')인 경우 매핑 일련번호(`mapp_menu_seq`)를 통해 상세 실행 뷰 파일과 직접 맵핑하여 라우팅 경로를 연동합니다."
    )

    data["tables"]["menumctb"] = {
        "memo": menumctb_memo,
        "starred": True,
        "color": "none",
        "columns": {
            "menu_lclass_cd": "메뉴 트리 최상위 대분류 카테고리 식별 코드 (4자리, PK)",
            "menu_mclass_cd": "대분류 하위의 중분류 카테고리 식별 코드 (4자리, PK)",
            "menu_mclass_nm": "화면에 표기될 공식 중분류 메뉴 명칭 (120자리)",
            "mclass_period": "웹 화면 상의 메뉴 렌더링 우선순위 및 정렬 순서 (Numeric)",
            "menu_type": "메뉴 항목의 성격 구분 코드 (10자리, 'C': 하위 메뉴를 가지는 카테고리, 'M': 화면 링크 최종 메뉴)",
            "system_type": "적용 대상 시스템 서비스 영역 구분 코드 (10자리, 'HQ': 본사 관리자, 'ST': 가맹점 파탈)",
            "remark": "기타 설정 사항 및 메뉴 설명 비고란 (120자리)",
            "mapp_menu_seq": "최종 메뉴 실행 링크 매핑 시 적용되는 상세 화면 고유 일련번호 (6자리, MENU_TYPE='M'일 때 매칭)",
            "create_dtime": "최초 메뉴 생성 등록 일시 (YYYYMMDDHH24MISS)",
            "create_id": "최초 등록자 ID (45자리)",
            "last_dtime": "최종 메뉴 정보 변경 일시 (YYYYMMDDHH24MISS)",
            "last_id": "최종 변경자 ID (45자리)"
        },
        "memo_c": "신규 웹 백오피스 서비스 카테고리 개발 및 추가 시 메뉴 관리 화면에서 레코드가 인서트됩니다.",
        "memo_u": "메뉴 명칭 수정, 표시 순서(`mclass_period`) 변경 또는 시스템 유형 전환 시 백오피스에서 업데이트됩니다.",
        "memo_d": "하위 상세 화면 매핑 테이블(`MENUMMTB`)의 참조 정합성을 위해 하위 노드 정보가 있으면 삭제가 제한됩니다.",
        "memo_r": "본사 직원 및 점포 웹 포털 기동 시, 로그인 계정의 권한 등급별 사이드바 메뉴 렌더링을 위해 실시간 조회됩니다.",
        "related_tables": [
            {
                "table_name": "menulctb",
                "description": "웹 메뉴 대분류 테이블. [N:1 관계] 상위 카테고리인 대분류 메뉴 그룹(예: 물류관리, 매출관리, 시스템관리 등) 정보 및 정렬 순서를 상속받기 위해 조인 참조됩니다."
            },
            {
                "table_name": "menummtb",
                "description": "웹 메뉴 상세/화면 매핑 테이블. [1:N 관계] 특정 중분류 카테고리 하위에 속해 실제 실행 및 뷰 링크를 담당하는 개별 상세 화면(JSP/View 파일명) 목록을 매핑하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "tb_user_last_menu",
                "description": "사용자 최근 방문 메뉴 이력. 사용자가 최근 열어본 상세 화면(menu_seq)이 소속된 대분류 및 중분류 카테고리를 역추적하여 뷰 경로를 브레드크럼(Breadcrumb) 형태로 표시하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "usermltb",
                "description": "사용자별 메뉴 권한 매핑 테이블. [N:N 관계] 로그인 사용자(user_id)에게 허가된 메뉴(menu_seq) 목록을 조회하여 대분류/중분류 네비게이션 트리를 동적으로 렌더링하기 위해 조인 참조됩니다."
            },
            {
                "table_name": "mroledtb",
                "description": "롤별 메뉴 권한 매핑 테이블. [N:N 관계] 시스템 역할 등급 코드(role_cd)별로 허용된 메뉴 목록을 조회하고, 권한 관리 화면에서 롤별 대/중/상세 메뉴 할당 리스트를 표시하기 위해 조인 참조됩니다."
            }
        ]
    }

    # Restore user state (starred and color) to prevent overwriting user modifications
    if "tables" in data:
        for t_name, t_info in data["tables"].items():
            if t_name in user_states:
                t_info["starred"] = user_states[t_name]["starred"]
                t_info["color"] = user_states[t_name]["color"]

    try:
        with open(memos_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Successfully updated table_memos.json with all detailed custom memos!")
    except Exception as e:
        print(f"Failed to write json: {e}")

if __name__ == '__main__':
    update_all_memos()
