# Admin_Sales_00005 — 어드민 POS 정산내역 단위 테스트케이스

> **화면**: [ADMIN] 매출분석 > POS > POS 정산내역  
> **URL Prefix**: `/backoffice/data/admin/sales/admin_sales_00005`  
> **@Transactional**: `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})`  
> **요청 방식**: `@RequestBody Map<String, Object>`  
> **DB 트리거 영향도**: 없음 (조회 전용 SELECT 화면이며, CUD 로직 및 관련 트리거 없음)

---

## 1. 분석 개요

본 화면은 시스템 관리자가 전체 체인의 매장별 POS 정산 목록 및 상세 정산 내역을 조회하는 화면입니다.
- **주요 기능**:
  1. `/searchRegiList`: 지정한 날짜와 체인, 매장의 POS 정산 요약 목록 조회 (체인 번호와 매장코드는 선택 조건이며 세션 제약 없음)
  2. `/searchRegiDetailList`: 특정 POS의 상세 정산 항목 모달 조회
- **DB 테이블**: `hmsfns.SAREGITB` (POS 정산 테이블), `hmsfns.MMEMBSTB` (매장 정보 테이블), `hmsfns.MMEMBVTB` (매장 부가세 설정 테이블)

---

## 2. 세션 공통 선행 조건

- 어드민 권한 로그인 계정으로 접속하므로 세션 내 체인이나 매장 정보에 제한되지 않고 자유롭게 조회가 가능합니다.

---

## 3. 엔드포인트 목록

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/searchRegiList` | POS 정산 요약 목록 조회 | `@RequestBody` | `List<Admin_Sales_00005_RegiListDto>` | SELECT | SAREGITB, MMEMBSTB, MMEMBVTB |
| 2 | `/searchRegiDetailList` | 정산 상세 내역 조회 | `@RequestBody` | `Map<String, Object>` (상세 정보) | SELECT | SAREGITB |

---

## 4. 테스트 케이스 시나리오

### 4.1 `/searchRegiList` — POS 정산 요약 목록 조회

| No | 테스트 목적 | 입력값 (RequestBody) | 예상 결과 | 판정 |
|----|----------|---------------------|---------|-----|
| 1-1 | 특정 체인 및 매장 정상 조회 (C001, NC0003 선택) | `{"searchDate":"20260602", "chainNo":"C001", "msNo":"NC0003"}` | 매장 `NC0003`에 속한 POS 1개의 정산 정보가 1건 반환됨 | **PASS** |
| 1-2 | 특정 체인 산하 전체 매장 조회 (msNo 누락) | `{"searchDate":"20260602", "chainNo":"C001", "msNo":""}` | C001 체인에 속하는 매장 중 해당 날짜에 정산이 완료된 모든 POS 정산 데이터 반환 | **PASS** |
| 1-3 | 전체 조회 (chainNo, msNo 모두 빈 값) | `{"searchDate":"20260602", "chainNo":"", "msNo":""}` | 해당 날짜에 정산이 완료된 모든 체인 및 매장의 POS 정산 데이터 반환 | **PASS** |
| 1-4 | 데이터가 존재하지 않는 일자 조회 | `{"searchDate":"20260601", "chainNo":"C001", "msNo":""}` | 0건의 빈 배열 `[]` 반환 | **PASS** |
| 1-5 | 미래 일자 조회 | `{"searchDate":"20301231", "chainNo":"", "msNo":""}` | 0건의 빈 배열 `[]` 반환 | **PASS** |

### 4.2 `/searchRegiDetailList` — 정산 상세 내역 조회

| No | 테스트 목적 | 입력값 (RequestBody) | 예상 결과 | 판정 |
|----|----------|---------------------|---------|-----|
| 2-1 | 정상 상세 정보 조회 (NC0003 매장 01번 POS) | `{"saleDate":"20260602", "msNo":"NC0003", "posNo":"01"}` | 총매출액, 순매출액, 결제 수단별 금액 및 시재금액을 포함한 JSON Map 반환 | **PASS** |
| 2-2 | 존재하지 않는 매장코드 또는 POS 번호 조회 | `{"saleDate":"20260602", "msNo":"NC9999", "posNo":"99"}` | 모든 금액 필드가 null 또는 0으로 채워진 빈 Map 또는 결과 없음 | **PASS** |

---

## 5. 자동화 테스트 스크립트 실행 정보

- **테스트 스크립트**: `D:\hmTest\backoffice\QaReport\test_admin_sales_05.py`
- **구동 환경**: Playwright + Python (headless=False)
- **검증 일자**: `2026-06-02`, 매장 `NC0003` (admin2 로그인)
- **화면 검증 캡처 증적**:
  - [조회 결과 스크린샷](file:///d:/hmTest/backoffice/QaReport/admin_sales_00005_search.png)
  - [상세 모달 스크린샷](file:///d:/hmTest/backoffice/QaReport/admin_sales_00005_detail.png)

---

## 6. 주요 검증 포인트 및 결함 분석

- **SQL 호환성 검증**:
  - `Admin_Sales_00005_Sql.xml` 내 `searchRegiList` 쿼리에 Oracle 외부 조인 표기법인 `MV.MS_NO(+)`가 잔존함.
  - EDB(EnterpriseDB) 환경에서는 Oracle 호환 모드로 인해 정상 동작하나, 순수 PostgreSQL 전환 시 SQL 구문 오류가 발생하므로 `LEFT JOIN` ANSI 표준 구문으로의 리팩토링이 권장됨.
- **트랜잭션 검증**:
  - `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})` 어노테이션이 올바르게 적용되어 있으며, 단순 SELECT 조회 화면이므로 트랜잭션 롤백 부작용 위험은 없음.

---

## 7. 브라우저 E2E 테스트 수행 결과

- **E2E 테스트 스크립트**: `D:\hmTest\backoffice\QaReport\test_admin_sales_05.py` (Playwright 구동)
- **테스트 시나리오 및 판정**:
  1. `admin2` 계정(PW: `0000`)으로 로그인 수행 (이중 로그인 경고 창 자동 통과) ✅ **PASS**
  2. POS 정산내역 화면 진입 -> '비밀번호 만료 모달' `#passwordsModal` 자동 해제 및 닫기 확인 ✅ **PASS**
  3. 조회일자 `#searchDate`에 `2026-06-02` 입력, 체인 드롭다운에서 `C001` 선택, 매장코드 드롭다운에서 `NC0003` 선택 ✅ **PASS**
  4. '조회' 버튼 `#admin_sales_00005_search_btn` 클릭 및 그리드 데이터 로딩 완료 대기 ✅ **PASS**
     - **화면 검증**: 그리드 테이블 `#admin_sales_00005_t01`에 매장명 `[오픈] 고양 Shop`, POS `01`, 영수증 건수, 총매출 등 정산 요약 레코드 1건이 표출되는 것을 확인. (증적 캡처: [조회 결과 스크린샷](file:///d:/hmTest/backoffice/QaReport/admin_sales_00005_search.png))
  5. 그리드의 매장명 셀(`td.table-onclick`) 클릭 및 상세 정산 항목 모달 `#detailSearchModal` 팝업 대기 ✅ **PASS**
     - **화면 검증**: 모달 내에 총매출액, 순매출액, 결제 수단별 금액 및 시재금액이 올바른 수치로 표출됨을 확인. (증적 캡처: [상세 모달 스크린샷](file:///d:/hmTest/backoffice/QaReport/admin_sales_00005_detail.png))
  6. 상세 정산 모달 닫기 및 DB 임시 권한 원본 상태로 복구 완료 ✅ **PASS**

