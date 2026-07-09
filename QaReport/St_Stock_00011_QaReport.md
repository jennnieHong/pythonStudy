# QA Report: St_Stock_00011 매장 점간이동 현황
**작성일**: 2026-06-09  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 재고관리 > 점간이동 > 점간이동 현황 (st_stock_00011)  
**테스트 환경**: http://localhost:8080/backoffice (로컬 WAS)  
**접속ID/PW**: 
* 매장 관리자: `shopbrand` / `0000` (NC0003) 또는 `fnbcafe` / `0000` (NC0007)

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/st/stock/St_Stock_00011_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/st/stock/St_Stock_00011_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/st/stock/St_Stock_00011_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../sqlmapper/stock/St_Stock_00011_Sql.xml` |
| DTO | `hyundai-backoffice-layer-domain/.../dto/st/stock/St_Stock_00011_MoveListDto.java`<br>`St_Stock_00011_MoveGoodsListDto.java` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/st/stock/st_stock_00011/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | Type | 쿼리 ID / 관련 테이블 |
|-----------|------|------|------|-----------------------|
| `/selectMoveList` | POST | 점간이동 전표 목록 조회 | SELECT | `selectMoveList` / MGMVHDTB, MGMVDTTB, MMEMBSTB, TGOODSTB |
| `/selectMoveGoodsList` | POST | 점간이동 전표 상세내역 조회 | SELECT | `selectMoveGoodsList` / MGMVDTTB, TGOODSTB, TMLCLSTB, TMMCLSTB, TMSCLSTB |

---

## 3. SQL Mapper 검증 (PostgreSQL 전환 검증)

`St_Stock_00011_Sql.xml`에 구현된 SQL 쿼리에 대해 PostgreSQL 호환 여부 및 Oracle 특화 문법 잔존 여부를 확인한 결과입니다.

### 3.1 쿼리 상세 분석
1. **`selectMoveList`**
   * **기능**: 선택된 조건(날짜, 전표구분, 보내는/받는 매장, 전표상태)에 해당하는 점간이동 전표 목록을 요약하여 합산합니다.
   * **집계 로직**: `PROC_FG` 상태값별로 집계 대상 수량 및 금액 정보를 `DECODE` 함수를 사용하여 연산합니다.
     * `PROC_FG` = `'0'` 또는 `'1'`: `REGI_CONFIRM_QTY` 및 `REGI_CONFIRM_AMT` 집계
     * `PROC_FG` = `'2'`: `MOVE_CONFIRM_QTY` 및 `MOVE_CONFIRM_AMT` 집계
     * `PROC_FG` = `'3'`: `IN_CONFIRM_QTY` 및 `IN_CONFIRM_AMT` 집계
2. **`selectMoveGoodsList`**
   * **기능**: 특정 전표(`sendDate`, `sendMsNo`, `slipNo`)의 상품 상세 정보를 규격, 소분류 정보와 함께 조회합니다.
   * **단가 조회**: 함수 대신 인라인 서브쿼리(`SELECT UCOST FROM hmsfns.TGOODSTB WHERE ...`)를 사용하여 원가를 조회합니다.
   * **수량 변환**: `FLOOR`와 `MOD` 함수를 사용하여 이동총수량을 Box수량(`MOVE_BOX_QTY`) 및 Ea수량(`MOVE_EA_QTY`)으로 나누어 반환합니다.

### 3.2 PostgreSQL 호환 검증 결과
* **`DECODE`**: EDB EPAS 엔진이 `DECODE`를 지원하므로 정상 작동하지만, 표준 PostgreSQL 전환을 위해 향후 `CASE WHEN` 구문으로 리팩토링할 것을 권장합니다.
* **`MOD`, `FLOOR`**: 표준 SQL 함수로 PostgreSQL에서 완벽하게 호환됩니다.
* **`ROWNUM` / `SYSDATE`**: 해당 SQL 파일에는 Oracle 특화인 `ROWNUM`이나 `SYSDATE`가 사용되지 않아 PostgreSQL 및 EDB 환경에서 아무런 수정 없이 완벽하게 호환됩니다.

### 3.3 DB 트리거 및 프로시저 영향도 분석
* **직접적인 영향 없음 (Read-only)**: 본 화면(`st_stock_00011`)은 매장 간의 점간이동 전표 목록 및 품목 리스트를 SELECT 문으로 단순히 **조회만 하는 기능(Inquiry-only)**을 수행합니다. 
* 따라서 전표의 추가, 수정, 삭제, 또는 확정과 같은 DML 작업이 발생하지 않으므로, **DB 트리거 및 stored procedure(예: `Tr_MGMVHD_T01_Service`, `Sp_SUB_IMTRLG_I_Service` 등)가 직접 호출되거나 영향을 주지 않습니다**.
* **간접적 연관성 (데이터 소비)**: 단, 이 화면에서 조회되는 전표 데이터(`MGMVHDTB`, `MGMVDTTB`)는 본사 등록/확정 화면(`hq_stock_00011`) 및 매장 등록/확정 화면(`st_stock_00010`)에서 호출한 트리거/프로시저에 의해 가공되고 수신완료 처리된 결과물입니다.

---

## 4. 브라우저 화면 테스트 결과

### 4.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 | 성공 (매장 관리자 `shopbrand` / 0000) ✅ |
| 화면 경로 | 재고관리 > 점간이동 > 점간이동 현황 ✅ |
| 화면 로딩 | 정상 ✅ |

### 4.2 E2E 시나리오 테스트 과정 (Playwright 자동화)

1. **[PHASE 1] 매장 로그인 및 화면 진입**:
   * 매장 점주(`shopbrand`) 계정으로 로그인 후 `st_stock_00011` 화면에 정상 진입하여 그리드가 렌더링되는 것을 확인했습니다.
2. **[PHASE 2] 기간 설정 및 조회**:
   * 조회조건의 등록일자를 `2026-06-01` ~ `2026-06-30`로 입력하고 [조회] 버튼을 클릭했습니다.
   * 보내는 매장 및 받는 매장 기준의 점간이동 목록(`t01`) 데이터가 정상 표출되었습니다.
3. **[PHASE 3] 상세 내역 조회**:
   * 점간이동 전표 목록 중 첫 번째 전표의 **전표번호(Link)**를 클릭하여 상세 내역 이벤트(`fnMoveGoodsList`)를 호출했습니다.
   * 하단 그리드(`t02`)에 해당 전표의 상세 상품정보(상품명, 규격, 소분류, 이동수량, 단가 등)가 정상 조회되는 것을 확인했습니다.

---

## 5. 검증 항목 체크리스트

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| 매장별 점간이동 목록 조회 | ✅ PASS | 날짜 범위 내 이입/이출 전표 목록 정상 노출 |
| 상세 내역 로딩 연동 | ✅ PASS | 전표번호 클릭 시 하단 그리드 `t02`에 상세 내역 실시간 바인딩 완료 |
| 수량 수치(Box/Ea) 연산 | ✅ PASS | `FLOOR`, `MOD` 연산 결과가 화면의 박스/낱개 단위에 정상 매핑됨 |
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
![1. 등록일자 조회 목록 출력](/d/hmTest/backoffice/QaReport/st_stock_00011_search.png)
<!-- slide -->
![2. 전표 상세 내역 로드](/d/hmTest/backoffice/QaReport/st_stock_00011_detail.png)
````

---
*본 리포트는 자바 소스 분석, EDB PostgreSQL 데이터베이스 호환성 검증 및 Playwright 브라우저 E2E 테스트를 종합하여 작성되었습니다.*
