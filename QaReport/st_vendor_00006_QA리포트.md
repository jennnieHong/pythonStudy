# QA Report: St_Vendor_00006 무발주 입고/취소
**작성일**: 2026-05-28
**작성자**: AI QA Agent (Antigravity)
**대상 화면**: 매입발주 > 매입관리 > 무발주 입고/취소 (st_vendor_00006)
**테스트 환경**: localhost:8080 (로컬 개발 서버)
**접속ID/PW**: fnbcafe / 0000

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/st/vendor/St_Vendor_00006_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/st/vendor/St_Vendor_00006_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/st/vendor/St_Vendor_00006_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../sqlmapper/vendor/St_Vendor_00006_Sql.xml` |
| 트리거 서비스 | `hyundai-api/.../service/trigger/Tr_OBSLPD_T01_Service.java` |
| 테스트케이스 | `Z:/97.프롬프트정리/AI화면별테스트/기타/backoffice/v2/St_Vendor_00006_TestCase.md` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/st/vendor/st_vendor_00006/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
|-----------|------|------|------------|
| `/getVatFg` | POST | 부가세 포함 여부 조회 | - |
| `/search` | POST | 무발주입고 헤더 목록 조회 | SELECT |
| `/detailSearch` | POST | 무발주입고 디테일 조회 | SELECT |
| `/selectVendorGoodsList` | POST | 상품 조회 (페이징 분기) | - (확인 필요) |
| `/insertOrder` | POST | 무발주입고 등록 (배열 루프) | INSERT |
| `/updateGoodsList` | POST | 무발주입고 수정 | UPDATE |
| `/confirmOrdPurch` | POST | 무발주입고 확정 | UPDATE |
| `/cancelSlip` | POST | 무발주입고 취소 | UPDATE |
| `/deleteSlip` | POST | 전표 삭제 | DELETE |

---

## 3. 서비스 로직 분석 (코드베이스 변환 검증)

### 3.1 무발주입고 등록 흐름 (`insertOrder`)
```
[Controller] insertOrder
  └─ [Service] saveVendorOrder
       ├─ flag="add" 일 경우 기존 slipNo 재사용
       ├─ flag != "add" 일 경우 selectSlipNo() 채번
       ├─ insertOrdPurchSlip() (OBSLPHTB INSERT)
       ├─ setZeroValue() 유틸 오류 내포 (0 전달 시 "0000"이 아닌 "0" 반환)
       ├─ insertOrdPurchGoods() (OBSLPDTB 배열 INSERT)
       └─ updateOrdPurchHd() (OBSLPHTB 금액 정보 UPDATE)
```

### 3.2 무발주입고 수정 흐름 (`updateGoodsList`)
```
[Controller] updateGoodsList
  └─ [Service] updateGoodsList
       ├─ orderQty > 0 항목과 = 0 항목을 분리
       ├─ 전체 삭제인 경우: deleteGoodsDtList + deleteGoodsHdList
       └─ 부분 삭제/수정인 경우: updateGoodsDtList + deleteGoodsDtList 후 updateGoodsHd()
```

---

## 4. DB 트리거 → 코드베이스 연쇄 분석

### 4.1 트리거 고아 코드 결함 (Bypass) **[CRITICAL]**
Legacy Oracle에서는 `OBSLPDTB`, `OBSLPHTB` 테이블에 CUD(Insert/Update/Delete) 발생 시 각각 `Tr_OBSLPD_T01`, `Tr_OBSLPH_T01` 트리거가 연쇄 동작하여 수많은 프로시저(`SUB_STOCK_FIFO_MAIN_P`, `SUB_VDORDER_P` 등)를 호출하여 데이터 동기화를 수행하도록 설계되었습니다.

하지만 마이그레이션된 Java 서비스 로직(`St_Vendor_00006_Service.java`) 점검 결과, 아래와 같은 치명적인 트리거 단절 결함이 식별되었습니다.

- `insertOrder`, `updateGoodsList`, `deleteSlip` 등의 메서드 내에 `Tr_OBSLPD_T01_Service` 등의 호출(예: `TriggerUtil.setTriggerParam`) 로직이 **전혀 존재하지 않습니다**.
- 즉, 무발주 입고 처리를 하더라도 후속 재고 반영 및 정산 연동 등의 마스터/로그 데이터 동기화가 이루어지지 않는 심각한 "고아(Orphan)" 상태입니다.

### 4.2 SQL Mapper 호환성 결함 (Oracle -> PostgreSQL) **[CRITICAL]**
`St_Vendor_00006_Sql.xml` 파일 분석 결과, PostgreSQL 환경에서 500 오류를 유발하는 레거시 문법이 다수 발견되었습니다.
- **아우터 조인 `(+)`**: `selectVendorGoodsList`, `getDetailList` 쿼리에서 `CR.MS_NO (+) = #{msNo}` 등 Oracle 전용 문법이 사용 중입니다.
- **Oracle 전용 함수 및 연산**: `SYSDATE`, `NVL`, `DECODE`, `ROWNUM` 등이 다수 사용되어 마이그레이션 호환성을 위협하고 있습니다.

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080/backoffice/login` ✅ |
| 로그인 | 성공 (ID: fnbcafe / PW: 0000) ✅ |
| 화면 경로 | 매입발주 > 매입관리 > 무발주 입고/취소 ✅ |
| 화면 로딩 | 정상 ✅ |

### 5.2 기능별 테스트 결과 및 버그 재현

| 기능 | 결과 및 세부사항 | 판정 |
|------|-----------------|------|
| **헤더 조회 (search)** | `searchFromDate` 및 `searchToDate` 기본값 기반으로 정상적으로 호출되나 "조회된 데이터가 없습니다." 노출. | **PASS** |
| **무발주입고 수정체크** | 조회된 데이터 없이 '상품추가' 클릭 시 "수정할 전표번호를 선택해 주시기 바랍니다." 검증 얼럿 정상 동작. | **PASS** |
| **상품 조회 (selectVendorGoodsList)** | [무발주 입고 등록] 모달에서 '삼성웰스토리' 선택 후 상품조회 시 **500 Internal Server Error** 발생. <br/> - 에러로 인해 상품을 추가할 수 없어 **등록/수정 CUD 플로우 전체 블록**. <br/> - 화면에 `??? ????? ??? ??` 형태로 깨진 시스템 오류 팝업 발생. | **FAIL** |

> **원인 분석**: `selectVendorGoodsList` 쿼리 내의 `(+)` 아우터 조인 문법 및 `ROWNUM`, `SYSDATE` 등의 비호환 문법이 PostgreSQL 런타임 에러를 발생시킨 것으로 판단됩니다.

---

## 6. SQL Mapper 검증 상세

| 쿼리 ID | Oracle(+) 사용 / 비호환 문법 | 영향 |
|---------|-----------------------|------|
| `getDetailList` | ✅ 사용 (`E.CHAIN_NO(+) = C.CHAIN_NO`, `NVL`, `F.GOODS_CD(+)`) | PostgreSQL 에러 발생 |
| `selectVendorGoodsList` | ✅ 사용 (`CR.MS_NO(+) = #{msNo}`, `SYSDATE`, `ROWNUM`) | PostgreSQL 에러 발생 (500 Error 유발점) |
| `selectMaxLineNo` | `NVL` 함수 | 호환성 경고 |
| `selectSlipNo` | `LPAD`, `NVL`, `TO_CHAR` | 호환성 경고 |
| `getPrePurchWhMsNoYn` | `DECODE` 함수 | 호환성 경고 |
| `updateGoodsDtList` | `ROUND` | - |

---

## 7. 발견된 이슈 및 권고사항

### 🔴 Critical (즉시 처리 필요)
1. **DB 트리거 바이패스 결함 (고아 로직)**
   - `St_Vendor_00006_Service`의 CUD 메서드(`saveVendorOrder`, `updateGoodsList`, `deleteSlip` 등)에 `Tr_OBSLPD_T01_Service` 및 `Tr_OBSLPH_T01_Service` 호출 로직이 누락되어 있습니다.
   - 레거시 트리거의 `OLD`, `NEW` 값을 전달하여 후속 재고 프로시저(`SUB_STOCK_FIFO_MAIN_P` 등)가 정상 연동되도록 긴급 반영해야 합니다.
2. **`selectVendorGoodsList` 500 서버 에러 (SQL 호환성)**
   - Oracle `(+)` 아우터 조인 문법이 존재하여 쿼리 실행이 실패하고 UI 플로우가 블록됩니다.
   - `LEFT OUTER JOIN` ANSI 표준 문법으로 변환해야 합니다.

### 🟡 Warning (마이그레이션 시 처리 필요)
1. **Java Service 내부 `setZeroValue()` 버그**
   - 테스트 문서에도 기재된 내용으로, `setZeroValue(0, 4)` 호출 시 "0000"을 기대하나 "0"이 반환되어 PK 자리수(`LINE_NO`) 오류를 유발할 수 있습니다. 로직 수정이 권장됩니다.
2. **Oracle 전용 함수 변환**
   - `NVL` → `COALESCE`
   - `SYSDATE` → `NOW()` 또는 `CURRENT_TIMESTAMP`
   - `DECODE` → `CASE WHEN` 으로의 전면적인 전환이 요구됩니다.

### 🟢 Info (참고 사항)
- 배열 처리 중 길이가 맞지 않을 시 `ArrayIndexOutOfBoundsException` 예방을 위한 컨트롤러/서비스 단의 방어 로직 강화가 필요합니다.

---

## 8. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 및 기초 검증 | ✅ PASS |
| 데이터 단순 조회 | ✅ PASS |
| 에러 핸들링 (얼럿) | ✅ PASS |
| 상품 조회 (`selectVendorGoodsList`) | ❌ **FAIL** (500 Error - SQL 문법 오류) |
| INSERT(등록) 로직 연계 | ❌ **FAIL** (상품 조회 불가로 진행 불가) |
| 트리거 연쇄 및 동기화 | ❌ **FAIL** (서비스 로직 내 트리거 호출 누락) |
| **종합 판정** | **❌ FAIL (CRITICAL BUG 발견)** |

---

## 9. 첨부 증빙
- 에러 팝업 및 화면 스크린샷: `scratchpad_kmi3hosn.md` 참조 
- 에러 로그 경로: `C:\Users\uoshj\.gemini\antigravity\brain\086f4634-11bb-45e2-b235-f99a9265536c\`
