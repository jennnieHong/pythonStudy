# Admin_System_00012 — 배치 로그 조회 단위 테스트케이스

> **대상 화면**: 시스템관리 > 영업정보시스템 > 배치 로그 조회 (`admin_system_00012`)  
> **API Base URL**: `POST /backoffice/data/admin/system/admin_system_00012`  
> **트랜잭션 설정**: `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})`  
> **데이터 수신 방식**: `@RequestBody Map<String, Object> map`  
> **DB 영향도**: 단순 SELECT 전용. 관련 CUD 테이블 및 DB 트리거/프로시저 없음.

---

## 1. 테스트 선행 및 세션 조건

- **로그인 ID**: `admin2` (비밀번호: `0000`)
- **권한 유형**: 시스템 관리자 (SYSTEM_TYPE = HQ)
- **대상 테이블**: `hmsfns.BATHRSTB` (배치 실행 결과 로그)

---

## 2. 엔드포인트 명세 및 쿼리 매핑

| # | URL 엔드포인트 | HTTP Method | 기능 요약 | 데이터 반환 | 연관 테이블 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | `/searchBatchLogList` | POST | 배치 로그 목록 및 전체 건수 조회 | `Map<String, Object>` (total, rows) | `hmsfns.BATHRSTB` |

---

## 3. 로직 및 데이터 흐름 구조

### 3.1 배치 로그 조회 흐름
```mermaid
sequenceDiagram
    actor User as 시스템 관리자 (admin2)
    participant UI as Browser Grid
    participant Ctrl as Admin_System_00012_Controller
    participant Svc as Admin_System_00012_Service
    participant DB as EDB PostgreSQL
    
    User->>UI: 조건(기간, API ID, 성공여부) 입력 후 [조회] 클릭
    UI->>Ctrl: POST /searchBatchLogList (searchFromDate, searchEndDate, apiId, successYn, offset, limit)
    Ctrl->>Svc: searchBatchLogList(CommandMap) 및 getTotalCnt(CommandMap) 호출
    Svc->>DB: Mapper.getTotalCnt(Map) 실행 (전체 건수 카운트)
    DB-->>Svc: total count 반환
    Svc->>DB: Mapper.searchBatchLogList(Map) 실행 (페이징 데이터 조회)
    DB-->>Svc: List<Admin_System_00012_BatchLogListDto> 반환
    Svc-->>Ctrl: total 및 rows 데이터 세트
    Ctrl-->>UI: HTTP 200 (rows, total) JSON 반환
    UI-->>User: 결과 그리드 렌더링 및 페이징 블록 갱신
```

---

## 4. 소스코드 정적 분석 기반 핵심 검증 포인트

### 🟢 4.1 빈 문자열 수신 시 숫자 형변환 에러 (NumberFormatException) - 해당 없음
*   **분석**: 본 화면은 CUD 저장/수정 로직이 전혀 없이 데이터베이스 `BATHRSTB` 테이블로부터 조회만 수행하는 **단순 Select 화면**입니다.
*   **결과**: 사용자 입력값 중 숫자 필드가 없으며, 날짜 및 ID 매칭만 문자열 비교로 이루어지므로 형변환 오류가 발생할 요지가 없습니다.

### 🔴 4.2 SQL Mapper 호환성 결함 (Oracle -> PostgreSQL)
*   **분석**: `Admin_System_00012_Sql.xml` 내의 `searchBatchLogList` 쿼리에 아직 Oracle 전용 페이징 문법인 `ROWNUM ROW_NO`가 사용되고 있습니다.
*   **영향**: EDB Oracle Compatibility 모드가 활성화되어 있지 않은 순수 PostgreSQL 엔진에서는 문법 에러가 발생하게 됩니다.
*   **조치 권고사항**: `ROW_NUMBER() OVER()` 함수를 사용하거나 MyBatis 표준 `LIMIT` / `OFFSET` 구문으로 변경이 권장됩니다.

---

## 5. 상세 테스트 시나리오 (E2E)

| TC ID | 테스트 시나리오 | 입력 데이터 (JSON Body) | 기대 결과 | 판정 기준 |
| :--- | :--- | :--- | :--- | :---: |
| **TC-101** | 배치 로그 목록 전체 조회 | `{"offset":0, "limit":10, "searchFromDate":"", "searchEndDate":"", "apiId":"", "successYn":""}` | HTTP 200, 전체 15건 데이터 셋 및 total=15 반환 | `total == 15` |
| **TC-102** | 실행 일자 기간 필터 조회 | `{"offset":0, "limit":10, "searchFromDate":"20260610", "searchEndDate":"20260612", "apiId":"", "successYn":""}` | HTTP 200, 2026년 6월 10일~12일 사이의 로그만 필터링 반환 | `rows.every(row => row.procDate >= '20260610')` |
| **TC-103** | API ID 부분 일치 매칭 조회 | `{"offset":0, "limit":10, "searchFromDate":"", "searchEndDate":"", "apiId":"CloseStore", "successYn":""}` | HTTP 200, API 코드가 'CloseStore'인 배치 로그 목록 반환 | `rows.every(row => row.ifApi.includes('CloseStore'))` |
| **TC-104** | 성공 여부(SUCCESS_YN) 필터 조회 | `{"offset":0, "limit":10, "searchFromDate":"", "searchEndDate":"", "apiId":"", "successYn":"0"}` | HTTP 200, 성공여부 코드가 '0' (성공)인 로그만 반환 | `rows.every(row => row.successYn == '0')` |
| **TC-105** | 페이징 오프셋 이동 조회 | `{"offset":10, "limit":10, "searchFromDate":"", "searchEndDate":"", "apiId":"", "successYn":""}` | HTTP 200, 11번째 행부터 15번째 행까지 총 5건 반환 | `rows.length == 5` |
