# 발주전송관리 (Hq_Vendor_00003) 데이터 적재 및 메일 발송 아키텍처 가이드

본 문서는 본사 발주전송관리(`hq_vendor_00003`) 화면의 테스트 데이터 적재 방법 및 메일 발송/연동 프로세스를 상세하게 정리하여, 향후 QA 테스트 및 유지보수 시 활용할 수 있도록 돕습니다.

---

## 1. 데이터 조회 연동 구조 및 테이블 관계

화면 목록에서 특정 날짜 조건으로 발주 내역이 조회되려면, 영업시스템 DB(EDB PostgreSQL) 내의 4개 핵심 테이블이 정상적으로 조인 관계를 맺어야 합니다.

### 1.1 테이블 조인 관계도

```
 [hmsfns.MMEMBSTB (매장 마스터)]           [hmsfns.TVNDRMTB (거래처 마스터)]
       MS_NO = 'NC0007'                     VENDOR = '000001'
    CHAIN_NO = 'C001'  <--- (조인) --->   CHAIN_NO = 'C001'
           │                                      │
           │ (MS_NO 조인)                           │ (VENDOR 조인)
           ▼                                      ▼
 [hmsfns.OBSLPHTB (발주서 헤더)] <----------------------------------------
   - ORDER_DATE (발주일자)
   - MS_NO      (매장코드)
   - SLIP_NO    (전표번호)
   - SLIP_FG    = '0' (발주전표 의미)
   - NO_ORDER_YN = 'N' (정상 발주)
   - PURCH_REQ_NO (구매의뢰요청번호) <--- (핵심 조인 키)
           ▲
           │ (PURCH_REQ_NO 조인)
           ▼
 [hmsfns.OBREQHTB (구매의뢰서 헤더)]
   - PURCH_REQ_NO (구매의뢰요청번호)
   - REQ_DATE     <=== ★ 화면의 [시작일] ~ [종료일] 일자 검색 필터 대상 칼럼
```

### 1.2 핵심 실패 원인 및 해결 포인트
- **증상**: 최근 날짜로 발주 전표가 생성되어 `OBSLPHTB` 테이블에 데이터가 들어갔으나 화면 조회에서 나타나지 않음.
- **원인**: 해당 전표의 `PURCH_REQ_NO`에 대칭되는 `OBREQHTB` (구매의뢰 헤더) 레코드가 생성되어 있지 않아, `OBREQHTB.REQ_DATE`가 `Null`로 평가되어 날짜 필터링 범위에 걸려 필터링됩니다.
- **해결**: 테스트 데이터를 밀어 넣을 때 반드시 `OBREQHTB`에 동일한 `PURCH_REQ_NO`로 `REQ_DATE`를 채워 넣어야 합니다.

---

## 2. 테스트용 데이터 적재 SQL 가이드

아래 SQL을 실행하면 지정한 날짜(예: `20260617`)에 해당하는 발주 데이터와 상세 품목이 화면에 정상적으로 로드됩니다.

```sql
-- 1. 구매의뢰서 헤더 적재 (날짜 필터 만족을 위한 필수 조건)
INSERT INTO hmsfns.OBREQHTB (
    PURCH_REQ_NO, 
    REQ_DATE, 
    USE_PLAN_DATE
) VALUES (
    '260617000701',  -- PURCH_REQ_NO (포맷: YYMMDD + MS_NO_뒤4자리 + 순번2자리)
    '20260617',      -- REQ_DATE (화면 조회 타깃 날짜)
    '2026-06-18'     -- USE_PLAN_DATE (사용예정일)
);

-- 2. 매입발주서 헤더 적재
INSERT INTO hmsfns.OBSLPHTB (
    ORDER_DATE, 
    MS_NO, 
    SLIP_NO, 
    SLIP_FG, 
    PURCH_REQ_NO, 
    VENDOR, 
    NO_ORDER_YN, 
    PROC_FG, 
    PURCH_SEND_YN, 
    ORDER_AMT, 
    ORDER_VAT
) VALUES (
    '20260617',      -- ORDER_DATE
    'NC0007',        -- MS_NO
    '0001',          -- SLIP_NO
    '0',             -- SLIP_FG ('0': 발주)
    '260617000701',  -- PURCH_REQ_NO (위 OBREQHTB와 일치)
    '000001',        -- VENDOR (거래처코드)
    'N',             -- NO_ORDER_YN ('N': 정규발주)
    '1',             -- PROC_FG ('1': 확정 상태)
    'N',             -- PURCH_SEND_YN ('N': 미전송 상태로 세팅)
    100000.000,      -- ORDER_AMT
    10000.000        -- ORDER_VAT
);

-- 3. 매입발주서 디테일 적재 (그리드 클릭 시 하단 상세 목록 조회용)
INSERT INTO hmsfns.OBSLPDTB (
    ORDER_DATE, 
    MS_NO, 
    SLIP_NO, 
    SLIP_FG, 
    LINE_NO, 
    GOODS_CD, 
    ORDER_QTY, 
    ORDER_UCOST, 
    ORDER_AMT, 
    ORDER_VAT
) VALUES (
    '20260617', 
    'NC0007', 
    '0001', 
    '0', 
    '0001', 
    'T0000001',      -- GOODS_CD (실제 존재하는 상품코드)
    10.000,          -- ORDER_QTY
    10000.000,       -- ORDER_UCOST
    100000.000,      -- ORDER_AMT
    10000.000        -- ORDER_VAT
);

-- 4. 거래처 이메일 정보 최종 점검
-- 거래처의 E_MAIL이 비어 있으면 JS 단에서 얼럿 창을 띄우고 발송 프로세스를 중단합니다.
UPDATE hmsfns.TVNDRMTB 
   SET E_MAIL = 'vendor_test@example.com' 
 WHERE VENDOR = '000001' AND CHAIN_NO = 'C001';
```

---

## 3. 메일 발송 및 연동 아키텍처 (비동기 통신)

화면에서의 메일 전송은 성능 확보 및 장애 내구성 강화를 위해 **이기종 DB 간의 실시간 분산 연동 및 백그라운드 비동기 처리 방식**으로 수행됩니다.

### 3.1 메일 연동 시퀀스 구조

```
[화면: 메일전송 클릭]
  │
  ├─ 1단계: 로컬 큐 적재 API 호출 (/sendEmail)
  │    ├─ 로컬 DB(EDB)의 IF_RTMS_MAILQUEUE 테이블에 대기 레코드 삽입 (IF_YN='N')
  │    └─ 로컬 DB(EDB)의 OBSLPHTB.PURCH_SEND_YN = 'S' (임시 전송 처리)
  │
  └─ 2단계: 실시간 연동 인터페이스 API 호출 (/MailInterface)
       ├─ 로컬 DB(EDB)에서 대기 상태(IF_YN='N') 데이터를 select
       ├─ 다른 데이터소스인 외부 Tibero DB의 RTMS_MAILQUEUE 테이블에 직접 insert 시도
       │
       ├─ [CASE 1: 연동 성공]
       │    └─ 로컬 DB(EDB)의 IF_RTMS_MAILQUEUE.IF_YN = 'Y'로 확정
       │
       └─ [CASE 2: 연동 실패 (예외 발생)]
            ├─ 로컬 DB(EDB)의 IF_RTMS_MAILQUEUE.IF_YN = 'E' (에러) 업데이트
            └─ 로컬 DB(EDB)의 OBSLPHTB.PURCH_SEND_YN = 'E' (전송오류 복구 갱신)
```

- **웹 애플리케이션의 성공 기준**: 수신인의 실제 메일함 도달 여부가 아니라, **"외부 메일 연동 DB(Tibero)의 발송 대기 큐 테이블에 이관(INSERT)에 성공한 것"**을 의미합니다.
- **실제 메일 발송**: 이관 성공 이후, 서버 상에 독자적으로 가동 중인 상용 **메일 에이전트 데몬(Mail SMTP Daemon)**이 Tibero DB의 큐 테이블을 주기적으로 감시(Polling)하며 실제 이메일 발송을 백그라운드로 수행하고 최종 전송 결과(`STATUS`)를 변경해줍니다.

---

## 4. 프로젝트 내 관련 소스파일

1. **로컬 발송 큐 적재**:
   - `Hq_Vendor_00003_Service.java`의 `sendEmail()` 메서드
   - `Hq_Vendor_00003_Sql.xml`의 `insertPurchEmail` 쿼리
2. **실시간 이기종 인터페이스**:
   - `MailInterface_Controller.java`의 `MailInterface()` 메서드
   - `Tibero_MailInterface_Service.java`의 `insertMail()` 메서드 (Tibero 데이터소스 전용 트랜잭션 매니저 기동)
   - `Tibero_MailInterface_Sql.xml`의 `insertMail` 쿼리 (Tibero DB의 `RTMS_MAILQUEUE` 테이블 INSERT)
3. **반송/실패 모니터링 배치**:
   - `ReturnMailService.java`의 `returnMail()` 메서드 (Quartz Scheduler에 의해 가동되며, Tibero DB의 발송 에러를 체크하여 원래 담당자에게 "발송 실패 안내 메일"을 역적재 해주는 후속 배치 프로그램)
