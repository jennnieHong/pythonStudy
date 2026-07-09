# Hq_Esti_00007 — 본사 견적 현황 단위 테스트케이스

> **화면**: [HQ] 견적관리 > 견적관리 > 견적현황  
> **URL Prefix**: `/backoffice/data/hq/estimate/hq_esti_00007`  
> **@Transactional**: `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})`  
> **요청 방식**: `@RequestBody Map<String, Object>`  
> **DB 트리거 영향도**: 없음 (조회 전용 SELECT 화면이며, CUD 로직 및 관련 트리거 없음)

---

## 1. 분석 개요

본 화면은 본사 관리자가 특정 견적 조건(유형, 차수, 적용기간, 상품 등)에 속한 가맹점들의 견적 상세 단가를 여러 거래처별로 동적 피벗하여 일괄 대조 조회하는 화면입니다.
- **주요 기능**:
  1. `/searchVendorCnt`: 조건에 부합하는 견적 거래처 리스트 조회 (그리드 동적 피벗 컬럼 형성을 위한 사전 조회)
  2. `/search`: 해당 조건의 거래처별 견적 단가 및 증감 내역 목록 조회 (MyBatis `PIVOT XML` 및 `EXTRACTVALUE` 구문 사용)
- **DB 테이블**: 
  * `hmsfns.TESVDUTB` (견적 대상 상세 테이블)
  * `hmsfns.TESFRHTB` (견적 요청 헤더 테이블)
  * `hmsfns.TVNDRMTB` (거래처 마스터 테이블)
  * `hmsfns.TGOODSTB` (상품 마스터 테이블)
  * `hmsfns.MNAMEMTB` (명칭 마스터 테이블 - 구매단위 매핑)
  * `hmsfns.TESHISTB` (견적 이력 테이블 - 최근입고단가 매핑)

---

## 2. 세션 공통 선행 조건

| 세션 키 | 설명 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | 로그인 본사의 체인 번호 (세션 취득) | searchVendorCnt, search |

---

## 3. 엔드포인트 목록

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/searchVendorCnt` | 견적 대상 거래처 조회 | `@RequestBody` | `Map<String, Object>` (vendorList) | SELECT | TESVDUTB, TVNDRMTB |
| 2 | `/search` | 견적 단가 피벗 목록 조회 | `@RequestBody` | `List<HashMap<String, Object>>` | SELECT | TESVDUTB, TGOODSTB, MNAMEMTB, TESHISTB, TVNDRMTB, TESFRHTB |

---

## 4. 테스트 케이스 시나리오

### 4.1 `/searchVendorCnt` — 견적 대상 거래처 조회

| No | 테스트 목적 | 입력값 (RequestBody) | 예상 결과 | 판정 |
|----|----------|---------------------|---------|-----|
| 1-1 | 정상 조건 조회 (거래처 존재 데이터) | `{"searchEstimTypeCd":"001", "searchEstimFromCd":"0002"}` | 체인 `C002`에 매핑된 견적 거래처 목록 1건 이상 반환 | **PASS** |
| 1-2 | 존재하지 않는 견적유형 조회 | `{"searchEstimTypeCd":"999", "searchEstimFromCd":"0002"}` | 빈 배열 `[]` 또는 빈 목록 반환 | **PASS** |
| 1-3 | 특정 거래처 코드 검색 조건 추가 | `{"searchEstimTypeCd":"001", "searchEstimFromCd":"0002", "searchEstimVendor":"000001"}` | 해당 거래처 `000001` 1건만 필터링되어 반환 | **PASS** |

### 4.2 `/search` — 견적 단가 피벗 목록 조회

| No | 테스트 목적 | 입력값 (RequestBody) | 예상 결과 | 판정 |
|----|----------|---------------------|---------|-----|
| 2-1 | 정상 조건 조회 (적용기간 포함) | `{"searchEstimTypeCd":"001", "searchEstimFromCd":"0002", "searchFromDate":"20230601", "searchEndDate":"20231231"}` | 거래처별 단가 피벗을 포함한 상품별 단가 내역 리스트 반환 | **PASS** |
| 2-2 | 특정 상품 검색 필터링 적용 | `{"searchEstimTypeCd":"001", "searchEstimFromCd":"0002", "goodsCdArr":"T0000063", "goodsCdList":["T0000063"]}` | 상품 `T0000063`에 해당하는 레코드 1건만 정확히 필터링 조회 | **PASS** |
| 2-3 | 적용기간 시작일 누락 상태 조회 | `{"searchEstimTypeCd":"001", "searchEstimFromCd":"0002", "searchEndDate":"20231231"}` | 화면 레벨 체크 작동 - "조회기간 시작일을 올바르게 입력해 주세요." 경고 발생 | **PASS** |

---

## 5. 자동화 테스트 스크립트 실행 정보

- **테스트 스크립트**: `D:\hmTest\backoffice\QaReport\test_hq_esti_07.py`
- **구동 환경**: Playwright + Python (headless=False)
- **검증 일자**: 적용기간 `2023-06-01` ~ `2023-12-31`, 체인 `C002` (`shopadmin` 로그인)
- **화면 검증 캡처 증적**:
  - [조회 결과 스크린샷](file:///D:/hmTest/backoffice/QaReport/hq_esti_00007_search.png)

---

## 6. 주요 검증 포인트 및 결함 분석

- **MyBatis SQL XML 호환성 분석**:
  * `Hq_Esti_00007_Sql.xml`의 기존 `getList` 쿼리는 Oracle 전용 구문인 `PIVOT XML` 및 `EXTRACTVALUE`를 사용하고 있었으나, EDB PostgreSQL 및 표준 PostgreSQL 호환성을 높이기 위해 SQL에서는 Flat select로 데이터를 조회하도록 수정했습니다.
  * 그리고 Java Service(`Hq_Esti_00007_Service.java`)단에서 상품코드 및 거래처별로 동적 피벗 가공을 처리하도록 리팩토링을 완료하여 SQL 구문 결함을 영구적으로 해결했습니다.
- **트랜잭션 분석**:
  * `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})` 어노테이션이 활성화되어 있으나, 본 화면은 단순 조회용 화면으로 CUD 동작이 존재하지 않아 데이터 변경 롤백 부작용 위험은 없습니다.
