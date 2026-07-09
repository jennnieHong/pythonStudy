# QA Report: Hq_Vendor_00008 부대비용 등록관리
**작성일**: 2026-06-17  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 매입발주 > 매입관리 > 부대비용 등록관리 (hq_vendor_00008)  
**테스트 환경**: localhost:8080 (로컬 개발 서버)  
**접속ID/PW**: shopadmin / 0000  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/hq/vendor/Hq_Vendor_00008_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/hq/vendor/Hq_Vendor_00008_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/hq/vendor/Hq_Vendor_00008_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../sqlmapper/vendor/Hq_Vendor_00008_Sql.xml` |
| JS (Business Logic) | `hyundai-backoffice-webapp/.../js/hq_vendor_00008.js` |
| JS (Table Init) | `hyundai-backoffice-webapp/.../js/hq_vendor_00008_bt.js` |
| JSP | `hyundai-backoffice-webapp/.../hq_vendor_00008.jsp` |
| 트리거 서비스 | `hyundai-api/.../service/trigger/Tr_OBSLPD_T01_Service.java` (수불 트리거) |
| 트리거 서비스 | `hyundai-api/.../service/trigger/Tr_OBSLPD_T02_Service.java` (유효성 검증 트리거) |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/vendor/hq_vendor_00008/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
|-----------|------|------|------------|
| `/selectVendorOrderList` | POST | 입고전표 목록 조회 | SELECT |
| `/selectVendorOrderDetailList` | POST | 전표 상세 품목 내역 조회 | SELECT |
| `/updateExtraCostAmt` | POST | 부대비용 금액 배분 적용 및 저장 | UPDATE |

---

## 3. 서비스 로직 분석 (코드베이스 변환 검증)

### 3.1 부대비용 적용 흐름 (`updateExtraCostAmt`)

```
[UI] 부대비용적용 버튼 클릭
  └─ [Controller] updateExtraCostAmt 호출
       ├─ chkExtraCostYn()                → 이미 재고 반영된 전표(GOODS_EXTRA_COST_YN = 'Y')가 있는지 사전 검사
       │    └─ 존재 시 "closed" 조기 반환 (차단)
       └─ [Service] updateExtraCostAmt
            ├─ tr_OBSLPD_T02_Service.getValueList() → CUD 수행 전 상세 레코드 OLD 파라미터 백업
            ├─ [분기 1] procFg = '0' (금액기준):
            │    └─ updateAmtExtraCostAmtDt()     → (금액 비율 배분) OBSLPDTB 업데이트
            ├─ [분기 2] procFg = '1' (수량기준):
            │    └─ updateQtyExtraCostAmtDt()     → (수량 비율 배분) OBSLPDTB 업데이트
            ├─ 루프 처리 (각 상세 품목별):
            │    ├─ tr_OBSLPD_T02_Service.getValues() → 업데이트 후 NEW 파라미터 로드
            │    ├─ Tr_OBSLPD_T02_Service.processTrigger() → (검증) Tr_OBSLPD_T02 작동
            │    └─ Tr_OBSLPD_T01_Service.processTrigger() → (수불) Tr_OBSLPD_T01 작동 (수불배제 분기 작동)
            └─ updateExtraCostAmtHd()             → OBSLPHTB 부대비용 합계 갱신
```

---

## 4. DB 트리거 및 코드베이스 연쇄 분석 (Depth 3)

### 4.1 부대비용 적용 시 트리거 동작 메커니즘
- **Tr_OBSLPD_T02_Service (검증 트리거):**
  - 업데이트(`U`) 발생 시 변경 전후의 부대비용 여부(`goodsExtraCostYn`) 및 금액(`goodsExtraCostAmt`) 변경 사항을 검증합니다.
  - 만약 이미 `'Y'` 상태로 확정된 부대비용의 금액을 변경하려고 시도하거나, 수불에 기 반영된 내역을 변경할 시 `RuntimeException` 에러를 발생시켜 데이터가 임의로 오염되는 것을 엄격히 차단합니다.
- **Tr_OBSLPD_T01_Service (수불 트리거):**
  - 부대비용 등록관리 화면의 기능은 전표의 진행상태 코드(`procFg`)를 변동시키지 않고 오직 부대비용 금액(`goodsExtraCostAmt`) 및 플래그(`goodsExtraCostYn = 'R'`)만 업데이트합니다.
  - 트리거 구현부 상 `cProcFg.equals(oldProcFg)` 분기 조건을 타게 되어, 실제 재고 수량 가감(`Sp_SUB_IMTRLG_I` 등) 및 `obslplog` 로그 생성이 발생하지 않고 **즉시 Bypass(리턴) 처리**됩니다.
  - 이로써 부대비용 배분 적용 시에는 매장의 수불이 흔들리지 않고 순수 비용 계산만 안전하게 진행되는 구조를 만족합니다.

### 4.2 연쇄 영향 요약 테이블

| 원본 테이블 | 1차 연쇄 | 2차 연쇄 | 로그 테이블 | 검증 결과 |
|-----------|---------|---------|-----------|-----------|
| `OBSLPDTB` | `goods_extra_cost_amt` 업데이트 | `Tr_OBSLPD_T02_Service` / `Tr_OBSLPD_T01_Service` | 없음 | **수불 배제 정상 작동** |
| `OBSLPHTB` | `slip_extra_cost_amt` 합계 업데이트 | - | - | **정상 갱신** |
| `IMTRLGTB` | 없음 | 없음 | 없음 | **영향 없음 (수불배제 정상)** |
| `obslplog` | 없음 | 없음 | 없음 | **영향 없음 (로그배제 정상)** |

### 4.3 EDB PostgreSQL 적합성 및 형변환 결함(RATIO_TO_REPORT) 검토
- **발견된 결함**: 
  - `Hq_Vendor_00008_Sql.xml` 의 `updateAmtExtraCostAmtDt` 및 `updateQtyExtraCostAmtDt` 쿼리에서 오라클 전용 함수인 `RATIO_TO_REPORT`를 사용하고 있습니다.
  - EDB PostgreSQL은 해당 함수를 네이티브 지원하지 않아 `PSQLException: ERROR: function ratio_to_report(numeric) does not exist` 예외를 발생시키며 저장 처리가 모두 중단되는 결함이 발견되었습니다.
- **수정 조치**: 
  - `RATIO_TO_REPORT` 윈도우 함수를 표준 나눗셈 수식인 `val / NULLIF(SUM(val) OVER(), 0)` 형태로 수정 패치 완료하여 EDB 데이터베이스 호환 정합성을 확보하였습니다.

---

## 5. 브라우저 화면 테스트 결과

Playwright E2E 스크립트(`test_hq_vendor_00008.py`)를 기동하여 본사 관리자(`shopadmin`) 계정으로 부대비용 배분 적용 및 저장이 정상 동작함을 실증 완료하였습니다.

````carousel
![1. 부대비용 등록관리 초기 화면](/C:/Users/uoshj/.gemini/antigravity-ide/brain/a6eb74d7-4237-4316-bd5d-fbf2d71150e6/hq_vendor_00008_1_initial.png)
<!-- slide -->
![2. 기간 조회 후 대상 매입전표 확인](/C:/Users/uoshj/.gemini/antigravity-ide/brain/a6eb74d7-4237-4316-bd5d-fbf2d71150e6/hq_vendor_00008_2_searched.png)
<!-- slide -->
![3. 부대비용 20,000원 배분 적용 및 저장 완료](/C:/Users/uoshj/.gemini/antigravity-ide/brain/a6eb74d7-4237-4316-bd5d-fbf2d71150e6/hq_vendor_00008_3_applied.png)
````

### 5.1 시나리오 흐름
1. **로그인**: `shopadmin` 계정으로 정상 로그인 수행.
2. **조회**: 조회 기간을 `2026-06-01` ~ `2026-06-30`으로 지정한 후 NC0007 매장 대상 조회하여, 배분 가능한 매입 전표 목록이 정상 로출됨을 확인 (대상 전표: `slipNo = 0003`, `purchAmt = 477,273원`).
3. **부대비용 입력 및 적용**: 부대비용 금액 `20,000원`을 입력하고 배분 구분을 `0` (금액 기준)으로 설정한 뒤 적용하여 팝업 승인 후 성공 API 응답(`sucess`)을 확인.
4. **저장 상태 확인**: 목록 재조회 시, 해당 전표의 부대비용 금액이 `20,000원`으로 업데이트되고 부대비용 배분 여부 플래그가 `N`에서 `R`(배분 완료)로 정상 갱신됨을 확인.

---

## 6. DB 적재 및 검증 상세 로그

부대비용 적용 직후 DB의 실제 변경 레코드를 실측 검증한 상세 결과는 다음과 같습니다.

### 6.1 매입전표 헤더 (`OBSLPHTB`) 갱신 내역
```sql
SELECT order_date, ms_no, slip_no, slip_extra_cost_amt, slip_extra_cost_create_date
FROM hmsfns.OBSLPHTB
WHERE order_date = '20260615' AND ms_no = 'NC0007' AND slip_no = '0003';
```
- **결과**: `slip_extra_cost_amt` = `20,000.000` / `slip_extra_cost_create_date` = `20260617` (정상 갱신)

### 6.2 매입전표 상세 (`OBSLPDTB`) 배분 내역
```sql
SELECT order_date, line_no, goods_cd, purch_qty, purch_ucost, goods_extra_cost_amt, goods_extra_cost_yn, goods_extra_cost_create_date
FROM hmsfns.OBSLPDTB
WHERE order_date = '20260615' AND ms_no = 'NC0007' AND slip_no = '0003';
```
- **결과**:
  - `goods_extra_cost_amt` = `20,000.000`
  - `goods_extra_cost_yn` = `'R'` (배분 완료)
  - `goods_extra_cost_create_date` = `'20260617'`
  - 단일 품목 전표이므로 부대비용 20,000원 전액이 해당 라인에 100% 분배 완료됨을 확인.

### 6.3 수불 영향도 및 트리거 연쇄 반응 실측 (Depth 3)
1. **수불 대장 (`IMTRLGTB`) 변동 여부**:
   - 수불 대장 내 해당 매장/일자의 재고 가감 건수 변동 없음 (`IMTRLGTB count = 1`, 기존과 동일).
   - 이유: 부대비용 배분 시에는 전표의 진행상태 코드(`procFg`)가 변동되지 않으므로 `Tr_OBSLPD_T01_Service`가 기동되어도 내부 `cProcFg.equals(oldProcFg)` 구문에 의해 수불 대장(`IMTRLGTB`) 가감이 배제되는 로직 작동 확인.
2. **수불 로그 (`obslplog`) 생성 여부**:
   - 추가 생성된 수불 변경 히스토리 로그 없음 (`obslplog count = 8`, 기존과 동일).
   - 수불 가감이 불필요한 비용 배분 프로세스의 특성에 맞게 수불 및 로그 발생이 완전 배제되었음을 최종 증명함.

---

## 7. 검증 항목 체크리스트

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 어노테이션 | ✅ 정상 | rollbackFor 포함 확인 |
| RATIO_TO_REPORT 함수 호환성 결함 패치 | ✅ 정상 | SQL XML 표준 함수로 대체 완료 |
| 부대비용 금액 배분 등록 및 저장 동작 | ✅ 정상 | 20,000원 배분 및 API 호출 정상 확인 |
| 수불대장(`IMTRLGTB`) 영향 배제 검증 | ✅ 정상 | DB 실측 결과 수불 변동 차단 확인 |

---

## 8. 발견된 이슈 및 권고사항

### 🔴 Critical (즉시 처리 필요)
1. **MyBatis XML 내 RATIO_TO_REPORT 함수 미전환 결함 (조치 완료)**
   - 부대비용 금액 배분 쿼리에 사용된 오라클 함수가 EDB PostgreSQL과 호환되지 않아 서비스 전체 에러를 냅니다. 수정 적용이 필수적이었으며, 표준 윈도우 함수 `val / NULLIF(SUM(val) OVER(), 0)` 형태로 수정 패치를 적용 완료하여 정상 동작함을 E2E를 통해 실증하였습니다.

---

## 9. 종합 판정

### **판정: PASS**
- **근거**:
  - EDB PostgreSQL 상에서 비호환 함수 `RATIO_TO_REPORT`로 인한 저장 오류 결함을 완벽히 패치하고 검증 완료하였습니다.
  - 부대비용 배분 기능 호출 시, 헤더 및 디테일 테이블의 금액과 플래그(`goods_extra_cost_yn = 'R'`)가 완벽히 저장됨을 확인하였습니다.
  - 서비스 코드 기반 수불 배제 분기가 설계 사양에 맞춰 정확히 동작하여, 수불 데이터(`IMTRLGTB`)와 수불 로그(`obslplog`)가 일절 오염되지 않는 무영향 상태(Depth 3)를 실측 확인하였습니다.
