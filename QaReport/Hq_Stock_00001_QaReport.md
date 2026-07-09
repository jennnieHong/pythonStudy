# QA Report: Hq_Stock_00001 현재고 조회
**작성일**: 2026-06-04  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 본사 > 재고관리 > 재고조회 > 현재고 조회 (hq_stock_00001)  
**테스트 환경**: localhost:8080 (로컬 개발 WAS)  
**접속ID/PW**: shopadmin / 0000  

---

## 1. 분석 개요

### 1.1 화면 기능 정의 및 성격
* **화면 성격**: 본 화면(`hq_stock_00001` - 현재고 조회)은 데이터의 추가, 수정, 삭제(CUD) 기능이 전무한 **순수 조회(SELECT) 전문 화면**입니다.
* **주요 기능**:
  1. 지정일 기준 매장별/상품별 현재고 현황 조회 (`SELECT`)
  2. 특정 상품 클릭 시 일수불 내역(시점재고, 매출, 매입 등) 상세 조회 (`SELECT`)
  3. 수불 누적 합계 요약 정보 조회 (`SELECT`)

### 1.2 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | [Hq_Stock_00001_Controller.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/hq/stock/Hq_Stock_00001_Controller.java) |
| Service | [Hq_Stock_00001_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/hq/stock/Hq_Stock_00001_Service.java) |
| Mapper (Interface) | [Hq_Stock_00001_Mapper.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-persistence/src/main/java/com/hyundai/backoffice/webapp/dao/hq/stock/Hq_Stock_00001_Mapper.java) |
| SQL XML | [Hq_Stock_00001_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/stock/Hq_Stock_00001_Sql.xml) |
| DTO (현재고 목록) | `Hq_Stock_00001_CurQtyListDto.java` |
| DTO (수불 내역) | `Hq_Stock_00001_StockListDto.java` |
| 트리거 서비스 | [Tr_TGOODS_T01_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-api/src/main/java/com/hyundai/api/service/trigger/Tr_TGOODS_T01_Service.java) |
| 트리거 서비스 | `Tr_MGOODS_T01_Service.java` |
| 트리거 서비스 | `Tr_MGOODS_T02_Service.java` |
| 트리거 서비스 | `Tr_MGOODS_T03_Service.java` |
| 트리거 서비스 | `Tr_TPRICE_T01_Service.java` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/stock/hq_stock_00001/{endpoint}
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
       ├─ Hq_Stock_00001_Mapper.selectCurQtyTotCnt() → 총 건수 쿼리 실행
       └─ Hq_Stock_00001_Mapper.selectCurQtyList() → 페이징 적용 목록 쿼리 실행
```

### 3.2 수불 및 레시피 판매 내역 상세 조회 흐름 (`/searchStock`)
```
[Controller] searchStock (HashMap commandMap)
  ├─ SecurityUserInformation 에서 chainNo 추출 후 세팅
  └─ [Service] 수불 정보 다중 조회
       ├─ Hq_Stock_00001_Mapper.selectStockList(commandMap) → 특정 기간 내 일수불 목록(IMDDIOTB)
       ├─ Hq_Stock_00001_Mapper.selectTotalStock(commandMap) → 기초재고 및 누적 수불 합계
       └─ Hq_Stock_00001_Mapper.getRecipeSaleList(commandMap) → 원부자재 포함 레시피 상품 시점 판매 내역(TB_SL_RECIPE_GOODS)
```
> [!NOTE]  
> `hq_stock_00019`와 달리 본 화면의 메인 테이블 그리드는 매장별로 로우가 분리되어 노출되므로, 특정 상품 클릭 시 `row.msNo` 단일 매장 코드가 명확하게 존재합니다. 따라서 서비스단에서 `msNoArr` 배열 전처리 처리가 불필요하며, 단일 매장 코드(`#{msNo}`)를 사용해 바인딩합니다.

---

## 4. DB 트리거 → 코드베이스 연쇄 분석

> [!NOTE]  
> **트리거 작동 범위 안내**: 본 화면(`hq_stock_00001`)은 순수 조회(SELECT) 전문 화면이므로, 화면 내부의 컨트롤러 및 서비스 동작 시에는 **실제 CUD 트랜잭션이 발생하지 않으며 트리거 서비스도 기동되지 않습니다.**  
> 다만, 본 화면의 조회 대상인 상품 정보(`TGOODSTB`) 및 매장 상품 마스터(`MGOODSTB`), 단가 정보(`TPRICETB`) 데이터에 변경(CUD)이 일어나는 **타 상품 마스터 관리 화면(본사 상품 등록/관리 등)**에서 트리거 서비스가 기동되며, 이는 본 조회 화면의 데이터 정합성에 영향을 주므로 관련 연쇄 구조를 정적 분석하여 기술합니다.

### 4.1 상품 마스터 변경/삭제 (`TGOODSTB` CUD) 연쇄 체인
```
TGOODSTB [I/U/D]
  └─ Tr_TGOODS_T01_Service.processTrigger()
       ├─ [Insert / Update] processGradeAndUpsert()
       │    ├─ MGOODSTB에 매장별 상품 정보 추가/수정 (mapper.insertMgoodstb/updateMgoodstb)
       │    │    └─ Tr_MGOODS_T01_Service.processTrigger() 호출 (1차 연쇄)
       │    │    └─ Tr_MGOODS_T03_Service.processTrigger() 호출 (1차 연쇄)
       │    └─ MPRICETB에 매장별 상품 단가 추가/수정 (mapper.insertMpricetb/updateMpricetb)
       │         └─ Tr_MPRICE_T01_Service.processTrigger() 호출 (1차 연쇄)
       ├─ [Delete] 물리 삭제 시 연쇄 동작
       │    ├─ MGOODSTB 삭제 및 Tr_MGOODS_T02_Service, Tr_MGOODS_T01_Service, Tr_MGOODS_T03_Service 연쇄 기동
       │    ├─ TVNDRGTB 삭제 및 Tr_TVNDRG_T01_Service.processTrigger() 연쇄 (매입거래처 연쇄)
       │    ├─ TMCPLKTB 삭제 및 Tr_TMCPLK_T01_Service.processTrigger() 연쇄 (컵링크 연쇄)
       │    ├─ TSUBMNTB 삭제 및 Tr_TSUBMN_T01_Service.processTrigger() 연쇄 (서브메뉴 연쇄)
       │    ├─ TMSSRCTB 삭제 및 Tr_TMSSRC_T01_Service.processTrigger() 연쇄 (바코드 연쇄)
       │    ├─ TKTFDCTB 삭제 및 Tr_TKTFDC_T01_Service.processTrigger() 연쇄 (티켓 요율 연쇄)
       │    ├─ [재고 데이터 연쇄 삭제] - 현재고 조회 화면에 직접적 영향
       │    │    ├─ IMCRIOTB (현재고현황) 삭제 (mapper.deleteImcriotb)
       │    │    ├─ IMDDIOTB (일수불) 삭제 (mapper.deleteImddiotb)
       │    │    └─ IMMMIOTB (월수불) 삭제 (mapper.deleteImmmiotb)
       ├─ MMSLOGTB 에 상품 변경/삭제 내역 로깅 (commonService.insertMmslogtb)
       └─ TB_COST 삭제/수정 (mapper.insertTbCost/deleteTbCost)
```

### 4.2 연쇄 요약 테이블 (직접 영향 테이블)

| 원본 테이블 | 1차 연쇄 (마스터 동기화) | 2차 연쇄 (재고 삭제) | 로그 및 이력 테이블 |
|-----------|---------|---------|-----------|
| **TGOODSTB** | `MGOODSTB` (upsert)<br>`MPRICETB` (upsert)<br>`TVNDRGTB` (delete)<br>`TMCPLKTB` (delete)<br>`TSUBMNTB` (delete)<br>`TMSSRCTB` (delete)<br>`TKTFDCTB` (delete) | `IMCRIOTB` (물리삭제)<br>`IMDDIOTB` (물리삭제)<br>`IMMMIOTB` (물리삭제) | `MMSLOGTB` (로깅)<br>`TB_COST` (원가 관리) |

### 4.3 정적 코드 분석 결과 (트리거 고아 및 마이그레이션 누락 결함)

> [!WARNING]
> **트리거 연동 누락 (Trigger Bypass) 결함**:  
> 본사 상품 관리 서비스인 `Hq_Master_00006_Service.java` 및 매장 상품 관리인 `St_Master_00002_Service.java` 코드를 점검한 결과, 상품 신규 등록(`instTGOODSTB`) 및 수정(`updTgoodstb`) 시 마이그레이션된 Java 트리거 서비스인 `Tr_TGOODS_T01_Service`를 명시적으로 호출하는 로직이 **전부 누락(Bypass)**되어 있습니다.  
> 이로 인해 웹화면에서 상품 마스터를 등록하거나 변경하더라도, 매장 상품 마스터(`MGOODSTB`) 및 재고/단가 연쇄 작용이 일어나지 않아 **현재고 조회 화면(`hq_stock_00001`)에서 신규 상품이나 변경 단가가 정상적으로 반영되지 못하고 데이터 정합성이 단절되는 중대한 시스템적 결함**이 식별되었습니다.

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080/backoffice` ✅ |
| 로그인 계정 | shopadmin (0000) ✅ |
| 화면 경로 | 본사 > 재고관리 > 재고조회 > 현재고 조회 ✅ |
| 화면 로딩 | 정상 로딩 완료 ✅ |

### 5.2 기능별 테스트 결과

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI 및 동작 | 판정 |
|------|-----------|---------|----------------|------|
| 현재고 목록 조회 | `/search` | ✅ 구현 완료 | ✅ 지정일자(2025-06-23) 기준 매장별 현재고 정상 노출 | **PASS** |
| 수불/상세 조회 | `/searchStock` | ✅ 구현 완료 | ✅ 상품코드 클릭 시 수불 모달창 정상 기동 및 일수불 내역 노출 | **PASS** |
| 총 수불 요약 | `/searchStockTot` | ✅ 구현 완료 | ✅ 모달창 내 전체 재고 요약 테이블 정상 로딩 | **PASS** |

---

## 6. SQL Mapper 검증 및 결함 항목

### 6.1 PostgreSQL/EDB 나눗셈 0 에러 (Division by zero) 취약점 (미조치)
* **이슈**: `Hq_Stock_00001_Sql.xml` 내의 아래 쿼리들에서 입수(`A.IN_QTY`, `GV.IN_QTY`) 단위를 분모로 사용하는 나눗셈 연산이 직접 수행되고 있습니다.
  * **`selectCurQtyList` 쿼리**:
    * `FLOOR((NVL(X.END_QTY,0) + NVL(C.DD_QTY,0)) / A.IN_QTY) AS ORD_UNIT_QTY`
    * `MOD((NVL(X.END_QTY,0) + NVL(C.DD_QTY,0)), A.IN_QTY) AS INV_UNIT_QTY`
    * `(NVL(X.END_QTY,0) + NVL(C.DD_QTY,0)) * A.UCOST / A.IN_QTY AS CUR_UPRICE`
  * **`selectStockList` 쿼리**:
    * `SELECT UCOST ... / GV.IN_QTY * ID.PURCH_QTY PURCH_COST` 외 총 11개 연산부
* **위험**: 마스터 정보의 입수(`IN_QTY`) 값이 `0` 또는 `null`인 비정상 데이터가 존재할 경우, PostgreSQL/EDB 환경에서는 즉시 `division by zero` 런타임 예외가 발생하여 **현재고 조회 목록 및 수불 상세 팝업 로딩이 완전히 실패**하게 됩니다.
* **조치 권고**: `hq_stock_00019`에 적용한 것과 동일하게, 분모를 `NULLIF(IN_QTY, 0)`로 감싸고 나눗셈 식 전체를 `COALESCE(..., 0)`로 처리하도록 Mapper SQL 수정이 시급합니다.

### 6.2 Oracle (+) 외부조인 잔존 현황 (마이그레이션 대상)
SQL XML 파일 내에 ANSI SQL 표준 조인으로 변환되지 않은 Oracle 전용 외부 조인(`(+)`)이 다수 잔존하고 있습니다. 순수 PostgreSQL 환경 이식을 위해 조인 구조 리팩토링이 필요합니다.

| 쿼리 ID | Oracle(+) 사용 위치 | 영향 |
|---------|---------------------|------|
| `selectCurQtyTotCnt` | `A.GOODS_CD = E.GOODS_CD(+)`, `A.MS_NO = E.MS_NO(+)` | LEFT JOIN 변환 필요 |
| `selectCurQtyList` | `A.GOODS_CD = E.GOODS_CD(+)`, `A.GOODS_CD = X.GOODS_CD(+)` 등 다수 | LEFT JOIN 변환 필요 |
| `selectStockList` | `IM.GOODS_CD (+)= ID.GOODS_CD` | LEFT JOIN 변환 필요 |
| `getRecipeSaleList` | `RG.SALE_DATE = SG.SALE_DATE(+)` 외 다중 외부조인 | LEFT JOIN 변환 필요 |

### 6.3 Oracle 전용 함수 및 페이징 구조
* `TO_CHAR`, `ADD_MONTHS`, `TO_DATE`, `NVL`, `DECODE` 등의 함수가 잔존하여 표준 SQL 이식이 권장됩니다.
* `selectCurQtyList` 내 ROWNUM 페이징 처리 역시 Oracle 3중 서브쿼리에 의존하고 있으므로 PostgreSQL `LIMIT / OFFSET` 구조로의 전환을 권장합니다.

---

## 7. 검증 항목 체크리스트

### 7.1 코드베이스 변환 정합성

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 어노테이션 | ✅ 정상 | 정상 작동 및 Exception Rollback |
| 컨트롤러 엔드포인트 맵핑 | ✅ 정상 | `/search`, `/searchStock`, `/searchStockTot` 매핑 일치 |
| `@ServiceLog` 매핑 적용 | ⚠️ 일부 누락 | `/searchStockTot` 엔드포인트에 서비스 로그 어노테이션 누락됨 |
| Mapper 인터페이스와 XML 바인딩 | ✅ 정상 | Namespace 및 Id 일치 |

---

## 8. 발견된 이슈 및 권고사항

### 🔴 Critical (즉시 처리 필요)
1. **나눗셈 0 에러 (Division by Zero) 방어 코드 부재**: 
   * `IN_QTY`가 0 또는 null인 데이터가 발생할 시 화면 전체가 런타임 에러로 뻗어버릴 수 있습니다. `COALESCE(val / NULLIF(IN_QTY, 0), 0)`로의 방어 처리가 필요합니다.
2. **상품 마스터 CUD 시 트리거 연동 누락 (Trigger Bypass)**:
   * `Hq_Master_00006_Service` 등의 상품 생성/수정/삭제 로직에서 `Tr_TGOODS_T01_Service` 호출이 완전히 누락되어 있어 하위 매장 상품 마스터(`MGOODSTB`) 및 재고/단가 동기화가 불가능한 시스템 결함 상태입니다.

### 🟡 Warning (마이그레이션 시 처리 필요)
1. **Oracle 아우터 조인 문법 (+) 잔존**: PostgreSQL 완전 호환을 위해 `LEFT OUTER JOIN` 표준 ANSI 구조로 변경을 권고합니다.
2. **Oracle 전용 함수 및 ROWNUM 의존**: `DECODE`, `NVL` 등은 `CASE WHEN`, `COALESCE`로 변경하고 페이징은 `LIMIT/OFFSET`으로 변환할 것을 권장합니다.

### 🟢 Info (조치 완료 사항)
1. **조회 Input 및 모달 Input 길이 제한(maxlength) 적용**:
   * **현재고 조회 화면 (`hq_stock_00001.jsp`)**:
     * 상품명/코드 (`#searchGoodsNmCd`) -> DB `TGOODSTB.goods_nm` 컬럼 크기에 맞춰 `maxlength="120"` 지정.
     * 바코드 (`#searchBarcode`) -> DB `TMSSRCTB.source` 컬럼 크기에 맞춰 `maxlength="26"` 지정.
   * **매장조회 팝업 모달 (`Com_StoreModalM01.jsp`)**:
     * 매장코드 (`#addGoodsModal_StoreCd`) -> DB `MGOODSTB.ms_no` 컬럼 크기에 맞춰 `maxlength="20"` 지정.
     * 매장명 (`#addGoodsModal_StoreNm`) -> DB `MGOODSTB.ms_nm` 컬럼 크기에 맞춰 `maxlength="50"` 지정.

---

## 9. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 | ✅ PASS |
| 현재고 목록 조회 | ✅ PASS (마스터 입수가 1 이상인 조건하에 작동) |
| 상품별 수불상세 조회 | ✅ PASS |
| 총 수불 요약 조회 | ✅ PASS |
| **종합** | **⚠️ 부분 PASS (CUD 트리거 단절 결함 및 zero-division 잠재 결함 존재)** |

---

## 10. 첨부

* **현재고 조회 화면**: [hq_stock_00001_search.png](file:///D:/hmTest/backoffice/QaReport/hq_stock_00001_search.png)
* **수불 상세 정보 모달**: [hq_stock_00001_detail_modal.png](file:///D:/hmTest/backoffice/QaReport/hq_stock_00001_detail_modal.png)

---
*본 리포트는 코드베이스 정적 분석 + Playwright 브라우저 자동화 테스트를 기반으로 정밀하게 작성되었습니다.*
