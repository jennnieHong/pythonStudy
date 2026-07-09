# QA Report: Hq_Stock_00012 본사 점간이동 현황
**작성일**: 2026-06-09  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 재고관리 > 점간이동 > 점간이동 현황 (hq_stock_00012)  
**테스트 환경**: http://localhost:8080/backoffice (로컬 WAS)  
**접속ID/PW**: 
* 본사 관리자: `shopadmin` / `0000`

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/hq/stock/Hq_Stock_00012_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/hq/stock/Hq_Stock_00012_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/hq/stock/Hq_Stock_00012_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../sqlmapper/stock/Hq_Stock_00012_Sql.xml` |
| DTO | `hyundai-backoffice-layer-domain/.../dto/hq/stock/Hq_Stock_00012_MoveListDto.java`<br>`Hq_Stock_00012_MoveGoodsListDto.java` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/stock/hq_stock_00012/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | Type | 쿼리 ID / 관련 테이블 |
|-----------|------|------|------|-----------------------|
| `/selectMoveList` | POST | 점간이동 전표 목록 조회 | SELECT | `selectMoveList` / MGMVHDTB, MGMVDTTB, MMEMBSTB, TGOODSTB |
| `/selectMoveGoodsList` | POST | 점간이동 전표 상세내역 조회 | SELECT | `selectMoveGoodsList` / MGMVHDTB, MGMVDTTB, TGOODSTB, TCLASSVW |

---

## 3. SQL Mapper 검증 (PostgreSQL 전환 검증)

`Hq_Stock_00012_Sql.xml`에 구현된 SQL 쿼리에 대해 PostgreSQL 호환 여부 및 Oracle 특화 문법 잔존 여부를 확인한 결과입니다.

### 3.1 쿼리 상세 분석
1. **`selectMoveList`**
   * **기능**: 본사 관점에서 모든 매장간 점간이동 전표 요약 목록을 조회합니다.
   * **검색 조건**: 날짜 범위와 함께 보내는 매장, 받는 매장, 상태 구분(`procFg`: `'1'` 이출확정, `'2'` 이입확정, `'3'` 본사확정) 및 특정 상품명/코드(`goodsNmCd`)를 조건 검색할 수 있습니다.
   * **집계 로직**: `PROC_FG`에 따라 이동 수량 및 금액 정보를 합산 렌더링합니다.
2. **`selectMoveGoodsList`**
   * **기능**: 특정 점간이동 전표의 상세 품목 목록을 조회합니다.
   * **조인 형태**: `CommonModule_GoodsClass_Mapper.tclassvw` 공통 뷰를 조인하여 상품의 소분류명(`SCLASS_NM`)을 함께 로딩합니다.
   * **검색 조건**: 상세 품목 그리드 내에서 개별 상품명/코드(`goodsCdNm`)로 추가 필터링이 가능하도록 서브 쿼리가 설계되었습니다.

### 3.2 PostgreSQL 호환 검증 결과
* **`DECODE`**: EDB EPAS 엔진이 `DECODE`를 지원하므로 정상 작동하지만, 표준 PostgreSQL 전환을 위해 향후 `CASE WHEN` 구문으로 리팩토링할 것을 권장합니다.
* **`MOD`, `FLOOR`**: 표준 SQL 함수로 PostgreSQL에서 완벽하게 호환됩니다.
* **`ROWNUM` / `SYSDATE`**: 해당 SQL 파일에는 Oracle 특화인 `ROWNUM`이나 `SYSDATE`가 사용되지 않아 PostgreSQL 및 EDB 환경에서 아무런 수정 없이 완벽하게 호환됩니다.

### 3.3 DB 트리거 및 프로시저 영향도 분석
* **직접적인 영향 없음 (Read-only)**: 본 화면(`hq_stock_00012`)은 본사 관점에서 전체 매장 간의 점간이동 전표 목록 및 품목 리스트를 SELECT 문으로 단순히 **조회만 하는 기능(Inquiry-only)**을 수행합니다. 
* 따라서 전표의 추가, 수정, 삭제, 또는 확정과 같은 DML 작업이 발생하지 않으므로, **DB 트리거 및 stored procedure(예: `Tr_MGMVHD_T01_Service`, `Sp_SUB_IMTRLG_I_Service` 등)가 직접 호출되거나 영향을 주지 않습니다**.
* **간접적 연관성 (데이터 소비)**: 단, 이 화면에서 조회되는 전표 데이터(`MGMVHDTB`, `MGMVDTTB`)는 본사 등록/확정 화면(`hq_stock_00011`) 및 매장 등록/확정 화면(`st_stock_00010`)에서 호출한 트리거/프로시저에 의해 가공되고 수신완료 처리된 결과물입니다.

---

## 4. 브라우저 화면 테스트 결과

### 4.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 | 성공 (본사 관리자 `shopadmin` / 0000) ✅ |
| 화면 경로 | 재고관리 > 점간이동 > 점간이동 현황 ✅ |
| 화면 로딩 | 정상 ✅ |

### 4.2 E2E 시나리오 테스트 과정 (Playwright 자동화)

1. **[PHASE 1] 본사 로그인 및 화면 진입**:
   * 본사 관리자(`shopadmin`) 계정으로 로그인 후 `hq_stock_00012` 화면에 정상 진입하여 그리드가 렌더링되는 것을 확인했습니다.
2. **[PHASE 2] 기간 및 조건 설정 후 조회**:
   * 등록일자를 `2026-06-01` ~ `2026-06-30`로 입력하고 [조회] 버튼을 클릭했습니다.
   * 모든 매장에서 발생한 점간이동 내역(`t01`) 데이터가 전표별로 요약 집계되어 정상 조회되었습니다.
3. **[PHASE 3] 상세 내역 조회**:
   * 점간이동 전표 목록 중 첫 번째 전표의 **전표번호(Link)**를 클릭하여 상세 내역 이벤트(`fnMoveGoodsList`)를 호출했습니다.
   * 하단 그리드(`t02`)에 해당 전표의 상세 상품정보(보내는/받는 매장 정보, 상품명, 규격, 소분류, 이동총수량, 공급가, VAT, 합계 등)가 정상 조회되는 것을 확인했습니다.

---

## 5. 검증 항목 체크리스트

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| 본사 전체 매장간 전표 조회 | ✅ PASS | 날짜 범위 내 모든 점포의 이입/이출 전표 목록 정상 노출 |
| 상품 코드/명 필터 검색 | ✅ PASS | 검색 조건 내 상품명 입력 시 해당 상품이 포함된 전표만 필터링 완료 |
| 상세 내역 로딩 연동 | ✅ PASS | 전표번호 클릭 시 하단 그리드 `t02`에 상세 내역 실시간 바인딩 완료 |
| EDB PostgreSQL 호환 | ✅ PASS | 쿼리 컴파일 및 데이터 반환 오류 없음 |

---

## 6. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 진입 및 매장 로딩 | ✅ PASS |
| 등록일자별 목록 조회 | ✅ PASS |
| 전표별 상세 내역 로딩 | ✅ PASS |
| DB SQL 호환성 검증 | ✅ PASS |
| **종합** | **✅ PASS** |

---

## 7. 첨부 (E2E 테스트 스크린샷 카러셀)

다음은 Playwright E2E 브라우저 테스트 중 캡처한 단계별 증적 자료입니다.

````carousel
![1. 등록일자 조회 목록 출력](/d/hmTest/backoffice/QaReport/hq_stock_00012_search.png)
<!-- slide -->
![2. 전표 상세 내역 로드](/d/hmTest/backoffice/QaReport/hq_stock_00012_detail.png)
````

---
*본 리포트는 자바 소스 분석, EDB PostgreSQL 데이터베이스 호환성 검증 및 Playwright 브라우저 E2E 테스트를 종합하여 작성되었습니다.*
