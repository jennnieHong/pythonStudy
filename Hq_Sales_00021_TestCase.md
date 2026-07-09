# Hq_Sales_00021 — 본사 POS 정산내역 단위 테스트케이스

> **화면**: [HQ] 매출분석 > POS > POS 정산내역  
> **URL Prefix**: `/backoffice/data/hq/sales/hq_sales_00021`  
> **@Transactional**: `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})`  
> **요청 방식**: `@RequestBody Map<String, Object>`  
> **DB 트리거 영향도**: 없음 (조회 전용 SELECT 화면이며, CUD 로직 및 관련 트리거 없음)

---

## 1. 분석 개요

본 화면은 본사 관리자 사용자가 특정 일자의 체인 산하 매장 전체 또는 특정 매장의 POS 정산 목록 및 상세 정산 내역을 조회하는 화면입니다.
- **주요 기능**:
  1. `/searchRegiList`: 지정한 날짜와 매장의 POS 정산 요약 목록 조회 (체인 번호는 세션 취득, 매장코드는 선택 조건)
  2. `/searchRegiDetailList`: 특정 POS의 상세 정산 항목 모달 조회
- **DB 테이블**: `hmsfns.SAREGITB` (POS 정산 테이블), `hmsfns.MMEMBSTB` (매장 정보 테이블), `hmsfns.MMEMBVTB` (매장 부가세 설정 테이블)

---

## 2. 세션 공통 선행 조건

| 세션 키 | 설명 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | 로그인 본사의 체인 번호 (세션 취득) | searchRegiList |

---

## 3. 엔드포인트 목록

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/searchRegiList` | POS 정산 요약 목록 조회 | `@RequestBody` | `List<Hq_Sales_00021_RegiListDto>` | SELECT | SAREGITB, MMEMBSTB, MMEMBVTB |
| 2 | `/searchRegiDetailList` | 정산 상세 내역 조회 | `@RequestBody` | `Map<String, Object>` (상세 정보) | SELECT | SAREGITB |

---

## 4. 테스트 케이스 시나리오

### 4.1 `/searchRegiList` — POS 정산 요약 목록 조회

| No | 테스트 목적 | 입력값 (RequestBody) | 예상 결과 | 판정 |
|----|----------|---------------------|---------|-----|
| 1-1 | 특정 매장 정상 데이터 조회 (NC0003 선택) | `{"searchDate":"20260602", "msNo":"NC0003"}` | 매장 `NC0003`에 속한 POS 1개의 정산 정보가 1건 반환됨 | **PASS** |
| 1-2 | 전체 매장 조회 (msNo 누락 또는 빈 값) | `{"searchDate":"20260602", "msNo":""}` | 해당 일자에 정산 데이터가 존재하는 체인 산하 모든 매장 목록 반환 | **PASS** |
| 1-3 | 데이터가 존재하지 않는 일자 조회 | `{"searchDate":"20260601", "msNo":"NC0003"}` | 0건의 빈 배열 `[]` 반환 | **PASS** |
| 1-4 | 미래 일자 조회 | `{"searchDate":"20301231", "msNo":""}` | 0건의 빈 배열 `[]` 반환 | **PASS** |

### 4.2 `/searchRegiDetailList` — 정산 상세 내역 조회

| No | 테스트 목적 | 입력값 (RequestBody) | 예상 결과 | 판정 |
|----|----------|---------------------|---------|-----|
| 2-1 | 정상 상세 정보 조회 (NC0003 매장 01번 POS) | `{"saleDate":"20260602", "msNo":"NC0003", "posNo":"01"}` | 총매출액, 순매출액, 결제 수단별 금액 및 시재금액을 포함한 JSON Map 반환 | **PASS** |
| 2-2 | 존재하지 않는 매장코드 또는 POS 번호 조회 | `{"saleDate":"20260602", "msNo":"NC9999", "posNo":"99"}` | 모든 금액 필드가 null 또는 0으로 채워진 빈 Map 또는 결과 없음 | **PASS** |

---

## 5. 자동화 테스트 스크립트 실행 정보

- **테스트 스크립트**: `D:\hmTest\backoffice\QaReport\test_hq_sales_21.py`
- **구동 환경**: Playwright + Python (headless=False)
- **검증 일자**: `2026-06-02`, 매장 `NC0003` (shopadmin 로그인)
- **화면 검증 캡처 증적**:
  - [조회 결과 스크린샷](file:///d:/hmTest/backoffice/QaReport/hq_sales_00021_search.png)
  - [상세 모달 스크린샷](file:///d:/hmTest/backoffice/QaReport/hq_sales_00021_detail.png)

---

## 6. 주요 검증 포인트 및 결함 분석

- **SQL 호환성 검증**:
  - `Hq_Sales_00021_Sql.xml` 내 `searchRegiList` 쿼리에 Oracle 외부 조인 표기법인 `MV.MS_NO(+)`가 잔존함.
  - EDB(EnterpriseDB) 환경에서는 Oracle 호환 모드로 인해 정상 동작하나, 순수 PostgreSQL 전환 시 SQL 구문 오류가 발생하므로 `LEFT JOIN` ANSI 표준 구문으로의 리팩토링이 권장됨.
- **트랜잭션 검증**:
  - `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})` 어노테이션이 올바르게 적용되어 있으며, 단순 SELECT 조회 화면이므로 데이터 정합성에 미치는 부작용은 없음.

---

## 7. 브라우저 E2E 테스트 수행 결과

- **E2E 테스트 스크립트**: `D:\hmTest\backoffice\QaReport\test_hq_sales_21.py` (Playwright 구동)
- **테스트 시나리오 및 판정**:
  1. `shopadmin` 계정(PW: `0000`)으로 로그인 수행 (이중 로그인 경고 창 자동 통과) ✅ **PASS**
  2. 본사 POS 정산내역 화면 진입 ✅ **PASS**
  3. 매장코드를 `NC0003` (고양 Shop)으로 선택하고, 조회일자를 `2026-06-02`로 설정 후 조회 클릭 ✅ **PASS**
     - 그리드에 현대 Shop 매장의 POS `01` 정산 원장 레코드 1건 정상 노출 확인
  4. 그리드 행 클릭하여 '정산 상세 내역 모달' 팝업 오픈 ✅ **PASS**
     - 총매출액(460,000원), 현금매출액(460,000원), 고객수(1명) 등의 수치가 정상적으로 바인딩되어 출력됨을 대조 및 검증 완료

