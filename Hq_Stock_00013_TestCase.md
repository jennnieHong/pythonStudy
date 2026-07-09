# Hq_Stock_00013 — 선입선출 월말마감처리 단위 테스트케이스

> **대상 화면**: [HQ] 재고관리 > 마감관리 > 월말마감처리 (`hq_stock_00013`)  
> **API Base URL**: `POST /backoffice/data/hq/stock/hq_stock_00013`  
> **트랜잭션 설정**: `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})` (마감 연산 실패 시 롤백 수행)  
> **데이터 수신 방식**: `@RequestBody Map<String, Object> map` (전 엔드포인트 공통)  
> **DB 영향도**: 선입선출법 단가 계산 및 월별 수불 요약 수정 (`IMMMIOTB`), 마감 이력 적재 (`STCKIOTB`, `STCKERTB`)  

---

## 1. 테스트 선행 및 세션 조건

| 세션 변수명 | 필요성 | 데이터 예시 | 비고 |
| :--- | :--- | :--- | :--- |
| `chainNo` | **필수** | `C001` (HMS F&B 체인) | 권한별 조회 및 마감 필터의 기준 (Mapper 바인딩) |
| `ID` | **필수** | `shopadmin` | 본사 로그인 사용자 ID (마감 등록자 ID 매핑) |

> [!WARNING]
> **권한 격리 주의**: 본 화면은 소속 체인의 데이터만 마감 및 조회할 수 있습니다.
> 타 체인 계정으로 조회 시 세션의 `chainNo` 불일치로 해당 체인 가맹점 정보가 제외되거나 에러가 발생합니다.

---

## 2. 엔드포인트 명세 및 쿼리 매핑

| # | URL 엔드포인트 | HTTP Method | 기능 요약 | 데이터 반환 | 연관 테이블 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | `/getMonthCloseList` | POST | 월마감 내역 목록 조회 | `List<Hq_Stock_00013_MonthCloseListDto>` | `STCKIOTB`, `MMEMBSTB` |
| 2 | `/getInstockCloseList` | POST | 선입고 마감 내역 목록 조회 | `List<Hq_Stock_00013_MonthCloseListDto>` | `STCKIOTB`, `MMEMBSTB` |
| 3 | `/excuteMonthClose` | POST | 월마감 처리 실행 | `void` (HTTP 200) | `IMMMIOTB`, `STCKIOTB`, `STCKERTB`, `STCKLGTB` |
| 4 | `/reDoMonthClose` | POST | 재마감 처리 실행 | `void` (HTTP 200) | `IMMMIOTB`, `STCKIOTB`, `STCKERTB`, `STCKLGTB` |
| 5 | `/inStockMonthClose` | POST | 선입고 월마감 처리 실행 | `void` (HTTP 200) | `IMMMIOTB`, `STCKIOTB`, `STCKERTB`, `STCKLGTB` |

---

## 3. 소스코드 및 SQL 마이그레이션 호환성 체크리스트

MyBatis Mapper 및 Java 코드 내의 PostgreSQL/Tibero 호환 분석사항입니다.

- [ ] **Oracle/Tibero Outer Join 식별**: MyBatis XML 및 프로시저 내 표준 ANSI JOIN 구조 적용 여부 확인.
- [ ] **에러 테이블 로깅 트랜잭션 분리**: `STCKERTB` 로깅 시 메인 트랜잭션 롤백에 휩쓸리지 않도록 별도의 트랜잭션 전파 속성(`REQUIRES_NEW`) 정상 동작 검증.

---

## 4. 상세 테스트케이스 (Unit & E2E)

### 4.1 `/getMonthCloseList` — 월마감 내역 조회

**파라미터**: `searchFromMonth` (조회시작월 YYYYMM, 필수), `searchEndMonth` (조회종료월 YYYYMM, 필수)  
**RequestBody 예시**: `{"searchFromMonth":"202601","searchEndMonth":"202606"}`

| TC ID | 테스트 시나리오 | 입력 데이터 (JSON Body) | 세션 조건 | 기대 결과 | 판정 기준 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-101** | 특정 기간 전체 목록 조회 (정상) | `{"searchFromMonth":"202601","searchEndMonth":"202606"}` | `chainNo="C001"` | HTTP 200, 2026년 1월 ~ 6월 마감 목록 반환 | `List.size() >= 0` |
| **TC-102** | 조회월 미지정 시 | `{"searchFromMonth":"","searchEndMonth":""}` | `chainNo="C001"` | HTTP 200, 비어있거나 전체 내역 반환 | `List.size() >= 0` |

### 4.2 `/excuteMonthClose` — 월마감 처리 실행

**파라미터**: `closeMonth` (마감 연월 YYYYMM, 필수)  
**RequestBody 예시**: `{"closeMonth":"202606"}`

| TC ID | 테스트 시나리오 | 입력 데이터 (JSON Body) | 세션 조건 | 기대 결과 | 판정 기준 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-201** | 미마감월 마감 최초 실행 (정상) | `{"closeMonth":"202606"}` | `chainNo="C001"`, `userId="shopadmin"` | HTTP 200, 선입선출 단가 계산 완료, `STCKIOTB`에 마감완료 `PROC_YN = 'Y'` 기록 | `PROC_YN == "Y"` |
| **TC-202** | 기마감월 중복 마감 차단 (예외) | `{"closeMonth":"202606"}` | `chainNo="C001"`, `userId="shopadmin"` | HTTP 500 예외 반환, `STCKERTB` 에러 테이블에 `-20506 MONTHS STOCK EXISTS!!` 로그 적재 | 에러 테이블 적재 확인 |
| **TC-203** | 마감 불가 연월(202512 이전) 실행 | `{"closeMonth":"202511"}` | `chainNo="C001"`, `userId="shopadmin"` | HTTP 500 예외 반환 (CANNOT RUN BEFORE 202512 !!) | 예외 메시지 검출 |

### 4.3 `/reDoMonthClose` — 재마감 처리 실행

**파라미터**: `closeMonth` (마감 연월 YYYYMM, 필수)  
**RequestBody 예시**: `{"closeMonth":"202606"}`

| TC ID | 테스트 시나리오 | 입력 데이터 (JSON Body) | 세션 조건 | 기대 결과 | 판정 기준 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-301** | 기존 마감 취소 및 재마감 실행 (정상) | `{"closeMonth":"202606"}` | `chainNo="C001"`, `userId="shopadmin"` | HTTP 200, 기존 마감 행 `CANCEL_YN = 'Y'` 업데이트 후 신규 마감 레코드 재생성 | `STCKIOTB` 재마감 성공 |
