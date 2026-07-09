# QA Report: Hq_Stock_00019 본사 현재고(매장합계)
**작성일**: 2026-06-04  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 본사 > 재고관리 > 현재고(매장합계) (hq_stock_00019)  
**테스트 환경**: localhost:8080 (로컬 개발 WAS)  
**접속ID/PW**: shopadmin / 0000  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | [Hq_Stock_00019_Controller.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/hq/stock/Hq_Stock_00019_Controller.java) |
| Service | [Hq_Stock_00019_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/hq/stock/Hq_Stock_00019_Service.java) |
| Mapper (Interface) | [Hq_Stock_00019_Mapper.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-persistence/src/main/java/com/hyundai/backoffice/webapp/dao/hq/stock/Hq_Stock_00019_Mapper.java) |
| SQL XML | [Hq_Stock_00019_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/stock/Hq_Stock_00019_Sql.xml) |
| DTO (현재고 목록) | `Hq_Stock_00019_CurQtyListDto.java` |
| DTO (수불 내역) | `Hq_Stock_00019_StockListDto.java` |
| 트리거 서비스 | [Tr_TGOODS_T01_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-api/src/main/java/com/hyundai/api/service/trigger/Tr_TGOODS_T01_Service.java) |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/stock/hq_stock_00019/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
|-----------|------|------|------------|
| `/search` | POST | 본사 현재고 목록 및 총 건수 조회 (페이징 적용) | SELECT (현재고 조회) |
| `/searchStock` | POST | 특정 상품 클릭 시 수불 및 시점판매내역 상세 조회 | SELECT (수불 내역 조회) |
| `/searchStockTot` | POST | 총 수불 조회 (누적 요약 조회) | - |

---

## 3. 서비스 로직 분석 (코드베이스 변환 검증)

### 3.1 현재고 조회 흐름 (`/search`)
```
[Controller] search (HashMap commandMap)
  ├─ SecurityUserInformation 에서 chainNo 추출 후 세팅
  ├─ offset, limit 값을 파싱하여 startIdx, endIdx 계산 (1-indexed 페이징)
  └─ [Service] getCurQtyTotCnt & getCurQtyList
       ├─ msNo가 "ALL"이 아닌 경우 split(",")을 실행하여 msNoArr 배열로 바인딩
       ├─ Hq_Stock_00019_Mapper.selectCurQtyTotCnt() → 총 건수 쿼리 실행
       └─ Hq_Stock_00019_Mapper.selectCurQtyList() → 페이징 적용 목록 쿼리 실행
```

### 3.2 수불 및 레시피 판매 내역 상세 조회 흐름 (`/searchStock`)
```
[Controller] searchStock (HashMap commandMap)
  ├─ SecurityUserInformation 에서 chainNo 추출 후 세팅
  └─ [Service] 수불 정보 다중 조회
       ├─ setupMsNoArr 호출로 msNo를 msNoArr 배열로 전처리 적용 ✅ (추가됨)
       ├─ Hq_Stock_00019_Mapper.selectStockList(commandMap) → 특정 기간 내 일수불 목록(IMDDIOTB)
       ├─ Hq_Stock_00019_Mapper.selectTotalStock(commandMap) → 기초재고 및 누적 수불 합계
       └─ Hq_Stock_00019_Mapper.getRecipeSaleList(commandMap) → 원부자재 포함 레시피 상품 시점 판매 내역(TB_SL_RECIPE_GOODS)
```

---

## 4. DB 트리거 → 코드베이스 연쇄 분석

> [!NOTE]  
> **트리거 작동 범위 안내**: 본 화면(`hq_stock_00019`)은 순수 조회(SELECT) 전문 화면이므로, 화면 내부의 컨트롤러 및 서비스 동작 시에는 **실제 CUD 트랜잭션이 발생하지 않으며 트리거 서비스도 기동되지 않습니다.**  
> 다만, 본 화면의 조회 대상인 상품 정보(`TGOODSTB`) 데이터에 변경(CUD)이 일어나는 **타 상품 마스터 관리 화면(본사/매장 상품 관리 등)**에서 `Tr_TGOODS_T01_Service` 등의 트리거 서비스가 기동되며, 이는 본 조회 화면의 데이터 정합성에 영향을 주므로 관련 연쇄 구조를 정적 분석하여 기술합니다.

### 4.1 상품 삭제 (`D`) 연쇄 체인
```
TGOODSTB [DELETE]
  └─ Tr_TGOODS_T01_Service.processTrigger(procFg="D")
       ├─ [Loop: 가맹점 목록 조회]
       │    ├─ Tr_MGOODS_T02_Service.processTrigger(D) 호출 (매장 상품 삭제 전처리)
       │    ├─ Tr_MGOODS_T01_Service.processTrigger(D) 호출 (매장 상품 삭제 및 연쇄)
       │    │    ├─ Tr_MSUBMN_T01_Service 호출 (서브메뉴 연쇄)
       │    │    ├─ Tr_MMCPLK_T01_Service 호출 (컵링크 연쇄)
       │    │    ├─ Tr_MMSSRC_T01_Service 호출 (바코드 연쇄)
       │    │    └─ Tr_MKTFDC_T01_Service 호출 (티켓 요율 연쇄)
       │    ├─ Tr_MGOODS_T03_Service.processTrigger(D) 호출
       │    └─ MGOODSTB 물리 삭제 (mapper.deleteMgoodstb)
       ├─ TVNDRGTB 삭제 및 Tr_TVNDRG_T01_Service.processTrigger(D) 연쇄 호출 (매입거래처 연쇄)
       ├─ TMCPLKTB 삭제 및 Tr_TMCPLK_T01_Service.processTrigger(D) 연쇄 호출 (컵링크 연쇄)
       ├─ TSUBMNTB 삭제 및 Tr_TSUBMN_T01_Service.processTrigger(D) 연쇄 호출 (서브메뉴 연쇄)
       ├─ TMSSRCTB 삭제 및 Tr_TMSSRC_T01_Service.processTrigger(D) 연쇄 호출 (바코드 연쇄)
       ├─ TKTFDCTB 삭제 및 Tr_TKTFDC_T01_Service.processTrigger(D) 연쇄 호출 (티켓 요율 연쇄)
       ├─ [재고 데이터 연쇄 삭제] - 핵심
       │    ├─ IMCRIOTB (현재고현황) 삭제 (mapper.deleteImcriotb)
       │    ├─ IMDDIOTB (일수불) 삭제 (mapper.deleteImddiotb)
       │    └─ IMMMIOTB (월수불) 삭제 (mapper.deleteImmmiotb)
       └─ MMSLOGTB 에 상품 삭제 내역 로깅 (commonService.insertMmslogtb)
```

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080/backoffice` ✅ |
| 로그인 계정 | shopadmin (0000) ✅ |
| 화면 경로 | 본사 > 재고관리 > 현재고(매장합계) ✅ |
| 화면 로딩 | 정상 로딩 완료 ✅ |

### 5.2 기능별 테스트 결과

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI 및 동작 | 판정 |
|------|-----------|---------|----------------|------|
| 현재고 조회 | `/search` | ✅ 구현 완료 | ✅ 지정일자(2025-06-23) 기준 정상 검색 데이터 노출 | **PASS** |
| 수불/상세 조회 | `/searchStock` | ✅ 구현 완료 | ✅ 첫 번째 상품 클릭 시 현재고현황 팝업 및 일수불 내역 노출 | **PASS** |
| 총 수불 요약 | `/searchStockTot` | ✅ 구현 완료 | ✅ 팝업 하단에 월수불/일수불 요약 정보 정상 반영 | **PASS** |

---

## 6. SQL Mapper 검증 및 버그 조치

### 6.1 EDB/PostgreSQL 집계 함수 버그 조치 (완료)
* **이슈**: 기존 `selectCurQtyTotCnt` 쿼리 내부에 `ORDER BY A.LCLASS_CD, A.MCLASS_CD, A.SCLASS_CD, A.GOODS_CD`가 포함되어 있어, PostgreSQL/EDB 환경에서 `COUNT(*)` 쿼리에 GROUP BY 없이 non-aggregated 컬럼으로 정렬을 수행할 수 없는 문법 오류(`BadSqlGrammarException`)가 발생함.
* **조치**: `Hq_Stock_00019_Sql.xml` 의 `selectCurQtyTotCnt` 쿼리에서 불필요한 `ORDER BY` 구문을 완전히 제거함. 정량적인 데이터 건수 세기 쿼리이므로 성능과 문법을 모두 해결함.

### 6.2 상세조회 매장 필터 바인딩 및 Front-End 연계 조치 (완료)
* **이전 문제점 (현상)**: 메인 화면에서 복수 매장을 선택해 총 300건의 재고 목록이 조회되었을 때, 임의의 상품을 클릭하여 수불 상세 팝업(일수불/총수불/레시피 판매내역)을 열면 메인 검색의 매장 조건이 유실되었습니다. 이로 인해 팝업 내 상세 데이터는 **전체 매장 기준으로 조회되어 300건이 아닌 훨씬 더 많은 전체 데이터가 노출**되는 정합성 오류가 존재했습니다.
* **원인 분석**:
  1. **Frontend**: 메인 현재고 그리드 조회 결과에 개별 행(`row`)의 `msNo` 컬럼이 포함되지 않아, 상품 클릭 시 `row.msNo`가 `undefined`로 파라미터화되어 상세조회 API(`searchStock`)로 전송되었습니다.
  2. **Backend**: 상세 수불 내역 조회(`getStockList`), 총 수불 조회(`getStockTotList`), 레시피 판매내역 조회(`getRecipeSaleList`)의 Service 단에서 매장 코드(`msNo`)를 MyBatis가 파싱 가능한 `msNoArr` 배열로 변환하는 `setupMsNoArr(param)` 전처리 호출이 누락되어 있었습니다. 이로 인해 MyBatis XML 내의 `<if test="msNoArr != null and msNoArr.length > 0">` 필터링 구문이 작동하지 못하고 생략되었습니다.
* **조치 내용**:
  * **Frontend**: `hq_stock_00019.js`의 `fn_searchStockModal` 함수에서 행 데이터에 `msNo`가 없거나 빈 값일 경우, 메인 검색 조건의 매장 값(`$('#selectMsPos_msNo_Input').val()`)을 Fallback 기본값으로 설정하여 호출하도록 수정하였습니다.
  * **Backend**: `Hq_Stock_00019_Service.java` 내의 모든 수불 상세 및 레시피 판매 조회 메서드에 `setupMsNoArr(param)` 공통 헬퍼 메서드 호출을 추가하여 `msNo` 필터 전처리를 일원화하였습니다.

### 6.3 Division by zero (나눗셈 0 에러) 가능성 방어 조치 (완료)
* **이슈**: 입수단위(`A.IN_QTY`, `GV.IN_QTY`) 마스터 데이터가 비정상적으로 `0` 또는 `null`로 세팅되어 있을 경우, 재고 금액(`CUR_UPRICE`) 및 원장 팝업의 각종 원가 관련 수식(/ `GV.IN_QTY` 연산) 계산 중 PostgreSQL에서 `division by zero` 런타임 에러가 발생할 가능성이 있었습니다.
* **조치**: `Hq_Stock_00019_Sql.xml` 내의 나눗셈을 유발하는 모든 연산부(`selectCurQtyList`, `selectStockList` 내 총 13개 연산 식)에 대해 `NULLIF(IN_QTY, 0)`를 사용하여 피분수를 NULL화한 후, `COALESCE(..., 0)`를 통해 최종 결과가 `0`으로 반환되도록 완벽히 에러 차단 방어막을 구축하였습니다.

### 6.4 Oracle (+) 외부조인 잔존 현황 (마이그레이션 대상)
SQL XML 파일 내에 ANSI SQL 표준 조인으로 변환되지 않은 Oracle 전용 외부 조인(`(+)`)이 잔존하고 있습니다. EDB 환경은 이를 허용할 수 있으나 순수 PostgreSQL 호환성을 위해 아래 쿼리들의 변환이 요구됩니다.

| 쿼리 ID | Oracle(+) 사용 위치 | 영향 |
|---------|---------------------|------|
| `selectCurQtyTotCnt` | `A.GOODS_CD = B.GOODS_CD(+)`, `A.GOODS_CD = C.GOODS_CD(+)` | LEFT JOIN 변환 권장 |
| `selectCurQtyList` | `A.GOODS_CD = B.GOODS_CD(+)`, `A.GOODS_CD = C.GOODS_CD(+)` | LEFT JOIN 변환 권장 |
| `selectStockList` | `IM.GOODS_CD (+)= ID.GOODS_CD` | LEFT JOIN 변환 권장 |
| `getRecipeSaleList` | `RG.SALE_DATE = SG.SALE_DATE(+)` 외 다중 조인 | LEFT JOIN 변환 권장 |

### 6.5 Oracle 전용 함수 및 페이징 구조
* `TO_CHAR`, `TO_DATE`, `ADD_MONTHS`, `SUBSTR`, `DECODE`, `NVL` 등 Oracle 계열 전용 함수가 복잡하게 얽혀 있습니다.
* `selectCurQtyList` 의 페이징 처리가 Oracle의 `ROWNUM`에 종속되어 있어 순수 PostgreSQL 변환 시 `LIMIT / OFFSET` 구조로 리팩토링할 필요가 있습니다.

---

## 7. 검증 항목 체크리스트

### 7.1 코드베이스 변환 정합성

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 어노테이션 | ✅ 정상 | 정상 작동 및 Exception Rollback |
| 컨트롤러 엔드포인트 맵핑 | ✅ 정상 | `/search`, `/searchStock`, `/searchStockTot` 매핑 일치 |
| `@ServiceLog` 매핑 적용 | ✅ 정상 | `/search`, `/searchStock` 에 서비스 로그 어노테이션 적용됨 |
| Mapper 인터페이스와 XML 바인딩 | ✅ 정상 | Namespace 및 Id 일치 |

### 7.2 트리거 연쇄 로직 정합성

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| TGOODSTB 삭제 시 하위 매장 매핑 삭제 | ✅ 정상 | `mapper.deleteMgoodstb` 정상 호출 |
| 매장 상품 트리거 연쇄 호출 | ✅ 정상 | `Tr_MGOODS_T01_Service` 외 2건 호출 |
| 거래처, 컵링크, 서브메뉴, 바코드 등 연쇄 | ✅ 정상 | 하위 삭제 쿼리 및 트리거 호출 무결성 확인 |
| **재고 테이블 연쇄 삭제** | ✅ 정상 | `IMCRIOTB`, `IMDDIOTB`, `IMMMIOTB` 일괄 연쇄 삭제 |

---

## 8. 발견된 이슈 및 권고사항

### 🔴 Critical (즉시 처리 필요)
* **없음** (PostgreSQL/EDB 비호환 정렬 오류 및 복수 매장 300건 조회 시 상세 필터 유실 에러, Division by zero 에러 방어 코드를 모두 반영하여 정상 동작함)

### 🟡 Warning (마이그레이션 시 처리 필요)
1. **Oracle 아우터 조인 문법 잔존**: 다수의 쿼리에서 `(+)` 문법을 사용 중이며, ANSI 표준 `LEFT OUTER JOIN`으로 리팩토링할 것을 권고합니다.
2. **Oracle 전용 함수 사용**: `ADD_MONTHS`, `DECODE`, `NVL` 등의 함수는 표준 SQL 함수로 이식할 것을 권고합니다.
3. **ROWNUM 페이징 의존**: Oracle의 3중 중첩 서브쿼리 + `ROWNUM` 구조를 `LIMIT` 와 `OFFSET` 으로 단일화하여 쿼리 가독성을 높일 수 있습니다.

### 🟢 Info (조치 완료 사항)
1. **조회 Input 길이 제한(maxlength) 적용**:
   * 상품명/코드 (`#searchGoodsNmCd`) -> DB `TGOODSTB.goods_nm` 컬럼 크기(120)에 맞춰 `maxlength="120"` 지정.
   * 바코드 (`#searchBarcode`) -> DB `TMSSRCTB.source` 컬럼 크기(26)에 맞춰 `maxlength="26"` 지정.

---

## 9. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 | ✅ PASS |
| 현재고(매장합계) 조회 | ✅ PASS (EDB 패치 적용) |
| 상품별 수불상세 조회 | ✅ PASS (매장 연동 및 zero-division 방어막 작동) |
| 총 수불 요약 조회 | ✅ PASS |
| 트리거 연쇄 구현 | ✅ PASS |
| **종합** | **✅ PASS** |

---

## 10. 첨부

* **현재고 조회 화면**: [hq_stock_00019_search.png](file:///D:/hmTest/backoffice/QaReport/hq_stock_00019_search.png)
* **수불 상세 정보 모달**: [hq_stock_00019_detail_modal.png](file:///D:/hmTest/backoffice/QaReport/hq_stock_00019_detail_modal.png)
