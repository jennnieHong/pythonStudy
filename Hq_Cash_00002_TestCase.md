# Hq_Cash_00002 — 매장별 입출금현황 단위 테스트케이스
> **화면코드**: `hq_cash_00002`  
> **URL Prefix**: `POST /backoffice/data/hq/cash/hq_cash_00002`  
> **권한**: HQ 본사 세션 필요  
> **서비스**: `Hq_Cash_00002_Service`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`
> **DB 트리거 영향도**: MMACNTTB에 트리거(MMACNT_T01)가 존재하지만 본 화면은 단순 SELECT만 수행하므로 무영향.

---

## ⚠️ 구조 주의사항

* **순수 조회 전용 화면**: 본 화면은 CUD가 발생하지 않고 단순 SELECT만 수행하는 화면입니다.
* **조회 조건 필수값 방어**:
  * `searchFromDate` 및 `searchEndDate`(조회기간) 미입력 시 `bootbox.alert` 호출 후 포커스 이동 처리.
  * `selectMsNo`(매장 선택) 미입력 시 `bootbox.alert` 호출 후 포커스 이동 처리.
* **상세 팝업 호출 분기**:
  * 요약 테이블의 `ACNT_FG`(계정구분) 셀 클릭 시 계정코드를 빈값(`''`)으로 보내 해당 구분의 전체 상세 내역을 조회함.
  * 요약 테이블의 `ACNT_NM`(계정명) 셀 클릭 시 특정 계정코드를 파라미터로 매핑하여 조회함.

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청방식 | ServiceType | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/searchList` | 매장별 입출금현황 요약 목록 조회 | RequestBody | SELECT | MMACNTTB<br>MACCIOTB |
| 2 | `/selectDtList` | 특정 계정의 입출금 상세내역 조회 | RequestBody | SELECT | MMACNTTB<br>MACCIOTB |

---

## 1. `/searchList` — 매장별 입출금현황 요약 목록 조회

**서비스**: `selectMmaList()`  
**요청**: `@RequestBody` (searchFromDate, searchEndDate, selectMsNo)  

| No | TC | Request | 예상값 | 비고 |
|----|----|---------|-------|------|
| 1-1 | 정상 조회 | `selectMsNo=NC0007&searchFromDate=20260201&searchEndDate=20260615` | 계정구분별 집계 금액 리스트 반환 | DB `MACCIOTB` 원장 집계와 일치 |
| 1-2 | 조회 기간 내 실적 없음 | `selectMsNo=NC0007&searchFromDate=19990101&searchEndDate=19991231` | `[]` (빈 리스트) 반환 | 화면에 "조회된 데이터가 없습니다." 표시 |
| 1-3 | 필수 파라미터 누락 | `searchFromDate=""` | JS 단에서 alert 팝업 후 중단 | `hq_cash_00002_t01_queryParams` 검증 |
| 1-4 | 미인증 접근 | 세션 만료 상태 호출 | 302 redirect (로그인 페이지) | Spring Security |

---

## 2. `/selectDtList` — 특정 계정의 입출금 상세내역 조회

**서비스**: `selectDetailMMaList()`  
**요청**: `@RequestBody` (selectMsNo, searchFromDate, searchEndDate, acntFg, acntCd)  

| No | TC | Request | 예상값 | 비고 |
|----|----|---------|-------|------|
| 2-1 | 계정구분 클릭 시 전체 조회 | `selectMsNo=NC0007&acntFg=0&acntCd=` (계정코드 빈값) | 해당 매장의 모든 입금(0) 상세 내역 리스트 반환 | 일자별 정렬 (`ORDER BY ACCIO_DATE`) |
| 2-2 | 계정명 클릭 시 특정 계정 조회 | `selectMsNo=NC0007&acntFg=0&acntCd=01` | 해당 매장의 특정 입금 계정(01) 상세 내역만 반환 | 필터링 동작 검증 |
| 2-3 | 상세 데이터 없음 | `acntCd=9999` (존재하지 않는 계정) | `[]` (빈 리스트) 반환 | 상세 모달 내 그리드 빈 상태 |

---

## 3. SQL Mapper 호환성 검토 (Oracle -> PostgreSQL / EDB)

* **`NVL` 함수 잔존**: `selectDetailMMaList` 쿼리에 `NVL(IO.CUST_CD, '')`, `NVL(IO.REMARK, '')` 오라클 함수 잔존. PostgreSQL 이관 시 `COALESCE`로 변경 필요.
* **`TO_DATE` 형변환**: `TO_CHAR(TO_DATE(ACCIO_DATE,'YYYYMMDD'),'YYYY-MM-DD')` 구문은 PostgreSQL 환경 호환성을 위해 `TO_CHAR(TO_TIMESTAMP(ACCIO_DATE, 'YYYYMMDD'), 'YYYY-MM-DD')`로 전환 권장.
