# Test Case: St_Stock_00002 매장 재고 조정 현황

**대상 화면**: 재고관리 > 조정/실사 현황 (`st_stock_00002`)  
**연계 화면**: [조정등록] (`st_stock_00001`), [현재고조회] (`st_stock_00007`)  
**작성일**: 2026-06-05  
**작성자**: AI QA Agent (Antigravity)  

---

## 1. 테스트 기본 정보
* **테스트 계정**: `fnbcafe` / `0000` (매장 코드: `NC0007`, HMS SHOP CAFE)
* **사전 데이터 입력 원천**: [조정등록 (st_stock_00001)](file:///D:/hmTest/backoffice/St_Stock_00001_TestCase.md) 화면에서 확정(Confirm) 처리하여 테이블 `hmsfns.IMREALTB`에 영구 저장된 데이터
* **테스트 대상 일자**: 2025-01-01 ~ 오늘 (2026-06-05)

---

## 2. 테스트케이스 정의서 (UI 및 기능 검증)

| TC ID | 테스트 대분류 | 테스트 시나리오 / 수행 절차 | 입력 데이터 | 예상 결과 (Expected Result) | 판정 |
|---|---|---|---|---|---|
| **TC_ST_002_01** | 화면 진입 | 1. `fnbcafe` 계정 로그인<br>2. `재고관리 > 조정/실사 현황` 메뉴 진입 | N/A | 화면이 에러 없이 로딩되며, 기본 조회 기간(시작일: 당월 1일, 종료일: 오늘)이 자동으로 세팅된다. | **PASS** |
| **TC_ST_002_02** | 기간별 조건 검색 | 1. 조회 기간 시작일을 `2025-01-01`로 수정<br>2. 조정구분 '전체', 조정기준 '조정일자별' 선택 후 `[조회]` 버튼 클릭 | 기간: `2025-01-01` ~ `오늘` | 1. HTTP 200 응답 수집 완료.<br>2. 마스터 그리드(`#st_stock_00002_t01`)에 해당 기간 매장 `NC0007`에서 확정한 **3건의 조정 요약 정보**가 정상 리스팅된다. | **PASS** |
| **TC_ST_002_03** | 마스터-디테일 연동 | 1. 마스터 그리드에서 첫 번째 행(2026/06/04, 부분실사, 1건) 마우스 클릭 | N/A | 1. 클릭 시 Javascript 이벤트 핸들러가 가동되며 `#input_surveySeq` 등 hidden 파라미터가 정상 업데이트된다.<br>2. 상세 내역 그리드(`#st_stock_00002_t02`)에 해당 조정 전표의 상세 상품정보(상품코드 `T0000001`, 단가, 원가, 조정 수량 등)가 비동기 바인딩된다. | **PASS** |
| **TC_ST_002_04** | Read-Only 검증 | 1. 마스터 그리드 및 상세 그리드 필드 더블클릭 및 텍스트 수정 시도 | N/A | 현황 조회 화면이므로 그리드의 모든 컬럼 및 셀은 읽기 전용 상태이며, 어떠한 CUD 입력 이벤트도 차단된다. | **PASS** |

---

## 3. 테스트케이스 정의서 (DB 호환성 및 오라클 함수 전환 검증)

| TC ID | 테스트 대분류 | 테스트 시나리오 / 수행 절차 | 입력 데이터 | 예상 결과 (Expected Result) | 판정 |
|---|---|---|---|---|---|
| **TC_ST_002_05** | 레거시 함수 대체<br>(`F_GET_MPRICE`) | 1. MyBatis Mapper `St_Stock_00002_Sql.xml` 내 매장단가 대체 서브쿼리 확인<br>2. `F_GET_MPRICE` DDL과 조건식 대조 | `MPRICETB` 조인 | 매장단가를 가져오는 오라클 함수 `F_GET_MPRICE`가 `MPRICETB`에 대한 inline subquery(시작/종료일 오늘 기준 필터링 및 ROWNUM = 1)로 정확하게 치환되어 작동한다. | **PASS** |
| **TC_ST_002_06** | 레거시 함수 대체<br>(`F_GET_TPRICE`) | 1. MyBatis Mapper 내 본사단가 대체 서브쿼리 확인<br>2. `F_GET_TPRICE` DDL과 조건식 대조 | `TPRICETB` 조인 | 체인/본사단가를 조회하는 오라클 함수 `F_GET_TPRICE`가 `TPRICETB`에 대한 inline subquery로 완벽히 치환되어 본사 기준 상품 단가를 정확히 표출한다. | **PASS** |
| **TC_ST_002_07** | DB 트리거 영향도 | 1. 본 화면 조회 쿼리 실행 후 PostgreSQL/EDB 로그 확인 | `IMREALTB` SELECT | 조회(Select-Only) 쿼리이므로 `IMREALTB`에 걸린 DB 트리거(`IMREAL_T01`)가 트리거링되지 않으며, 데이터 정합성 변동이 없다 (사이드 이펙트 0건). | **PASS** |

---

## 4. 특이사항 및 검증 결과 코멘트

### 4.1 SQL Mapper 오라클 전용 문법 마이그레이션 권고 (Warning)
MyBatis Mapper 파일([St_Stock_00002_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/stock/St_Stock_00002_Sql.xml))을 분석한 결과, EDB의 Oracle 호환 모드가 아닌 표준 PostgreSQL 환경으로의 최종 마이그레이션 진행 시, 아래와 같은 비표준 오라클 전용 문법에 대한 리팩토링이 권장됩니다.
1. **`DECODE` 함수**: `DECODE(#{wongaFg}, '0', 1, GD.IN_QTY)` 구문 등은 PostgreSQL과의 완벽한 호환을 위해 `CASE WHEN` 문으로 변경해야 합니다.
2. **`NVL` 함수**: PostgreSQL 호환을 위해 `COALESCE` 함수로 치환이 권장됩니다.
3. **`ROWNUM = 1`**: 서브쿼리 내 단일 레코드 추출 로직은 PostgreSQL 표준인 `LIMIT 1` 또는 `FETCH FIRST 1 ROWS ONLY`로 치환되어야 합니다.
4. **`SYSDATE`**: 시간 획득 구문인 `TO_CHAR(SYSDATE, 'YYYYMMDD')`는 PostgreSQL의 `TO_CHAR(NOW(), 'YYYYMMDD')`로의 이식이 요구됩니다.

### 4.2 E2E 테스트 스크린샷 증적 자료

* **[1] 마스터 조회 및 조정 현황 요약 화면 (st_stock_00002_search.png)**
  ![마스터 조회 화면](file:///D:/hmTest/backoffice/QaReport/st_stock_00002_search.png)
* **[2] 첫 번째 행 클릭 후 하단 조정 상세 목록 화면 (st_stock_00002_detail.png)**
  ![디테일 연동 화면](file:///D:/hmTest/backoffice/QaReport/st_stock_00002_detail.png)
