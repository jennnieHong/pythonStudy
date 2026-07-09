# St_Stock_00004 — 매장 폐기현황 조회 단위 테스트케이스

> **화면**: [ST] 재고 > 조정/폐기/실사 > 폐기현황  
> **URL Prefix**: `POST /backoffice/data/st/stock/st_stock_00004`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않아 **실제 트리거가 직접 기동하지는 않습니다.** 다만, 다른 화면(매장 폐기등록 `st_stock_00003` 등)에서 폐기 확정이 발생하면 DB 트리거 `IMDUSE_T01` (Java 서비스: `Tr_IMDUSE_T01_Service`)이 기동되어 `IMDUSETB` 테이블에 데이터가 생성 및 변경되고, 결과적으로 본 화면의 조회 데이터에 영향을 미치게 됩니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | selectDisuseList, selectDisuseDetailList |
| `msNo` | `NC0001` (카페매장 - fnbcafe 계정의 소속 매장) | selectDisuseList, selectDisuseDetailList (컨트롤러에서 세션 값을 강제 주입함) |
| `ID` | `fnbcafe` (카페 매장 관리자) | 공통 세션 및 권한 체크 |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/selectDisuseList` | 폐기현황 요약 목록 조회 | `@RequestBody` | `List` (DisuseListDto) | SELECT | IMDUSETB<br>MGOODSTB<br>MMEMBSTB<br>MNAMEMTB |
| 2 | `/selectDisuseDetailList` | 폐기현황 상세내역 조회 | `@RequestBody` | `List` (DisuseDetailListDto) | SELECT | IMDUSETB<br>MGOODSTB<br>MUSERSTB<br>MPRICETB |

---

## 1. `/selectDisuseList` — 폐기현황 요약 목록 조회

**특이사항**:
* `com_selectGijun` 값에 따라 SELECT 절과 GROUP BY 절이 동적으로 변경됩니다.
  * `com_selectGijun = 'D'`: 일자별 조회 (TITLE_NM = YYYY-MM-DD 형식 일자, TITLE_CD = YYYYMMDD 일자코드)
  * `com_selectGijun = 'R'`: 사유별 조회 (TITLE_NM = MNAMEMTB 공통코드 902 매핑명칭, TITLE_CD = 사유코드)
* 세션의 `msNo` 및 `chainNo`를 강제 주입하므로 로그인된 매장 내부의 폐기 실적만 요약 출력됩니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 1-1 | msNo=`NC0001` | 폐기 확정 건 존재 | `{"searchFromDate":"20250601","searchToDate":"20250630","com_selectGijun":"D"}` | 일자별 폐기 건수/수량/금액 요약 리스트 반환 |
| 1-2 | msNo=`NC0001` | 폐기 확정 건 존재 | `{"searchFromDate":"20250601","searchToDate":"20250630","com_selectGijun":"R"}` | 사유별 폐기 건수/수량/금액 요약 리스트 반환 |
| 1-3 | msNo=`NC0001` | 특정사유 폐기 존재 | `{"searchFromDate":"20250601","searchToDate":"20250630","com_selectGijun":"D","com_selReason":"01"}` | 특정 폐기사유에 대한 데이터 필터링 |
| 1-4 | msNo=`NC0001` | 상품 정보 존재 | `{"searchFromDate":"20250601","searchToDate":"20250630","com_selectGijun":"D","txt_goodsNmCd":"아메리카노"}` | 상품코드 또는 상품명 LIKE 필터 적용 확인 |
| 1-5 | msNo=`NC0001` | 바코드 정보 존재 | `{"searchFromDate":"20250601","searchToDate":"20250630","com_selectGijun":"D","txt_barcode":"880"}` | `MMSSRCTB` EXISTS 조인을 통한 바코드 검색 필터 동작 |

---

## 2. `/selectDisuseDetailList` — 폐기현황 상세내역 조회

**특이사항**:
* 요약 목록에서 특정 행을 클릭하면 호출되는 API로, 선택된 기준키(`paramdate`)에 해당하는 상세 전표 내역을 반환합니다.
* 쿼리 내에서 특정 상품의 판매가/매입원가를 비교하여 **마진율(MARGIN)**을 동적으로 계산합니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 2-1 | msNo=`NC0001` | `2025-06-23` 폐기 상세 존재 | `{"searchFromDate":"20250601","searchToDate":"20250630","com_selectGijun":"D","paramdate":"20250623"}` | 일자(`20250623`) 기준 상세 폐기 상품 목록 반환 (처리시간, 원가, 마진율 등 포함) |
| 2-2 | msNo=`NC0001` | 사유코드 `01` 폐기 상세 존재 | `{"searchFromDate":"20250601","searchToDate":"20250630","com_selectGijun":"R","paramdate":"01"}` | 사유(`01`) 기준 상세 폐기 상품 목록 반환 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/stock/st_stock_00004"
$h = @{"Content-Type"="application/json"}

# 1-1. 폐기현황 요약 목록 조회 (일자별)
Invoke-RestMethod -Uri "$base/selectDisuseList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20250601","searchToDate":"20250630","com_selectGijun":"D"}'

# 2-1. 폐기현황 상세내역 조회 (특정일자 선택)
Invoke-RestMethod -Uri "$base/selectDisuseDetailList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20250601","searchToDate":"20250630","com_selectGijun":"D","paramdate":"20250623"}'
```

---

## 주요 검증 포인트

* **[Filter] 매장 보안 바인딩 검증**: 로그인한 매장코드(`msNo`)가 백엔드 세션에서 강제 주입되어 다른 매장의 폐기 실적이나 상세 원장을 침해하지 못하는지 확인.
* **[Math] 나눗셈 0 방어 코드 검증**:
  * 백엔드 트리거 서비스(`Tr_IMDUSE_T01_Service`)에서 원가 계산 시 상품 마스터 입수가 0일 경우 발생할 수 있는 `division by zero` 런타임 에러 방어 여부 점검 (`inQty = BigDecimal.ONE` 강제 치환 검증).
  * 프론트엔드 포맷터(`calcurCostFormatter`)에서 `row.inQty` 또는 `row.invInQty`가 0일 때 화면에 `Infinity` 또는 `NaN`이 노출되지 않고 안전하게 처리되는지 확인.
