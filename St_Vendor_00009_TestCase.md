# St_Vendor_00009 — 매장 매입발주현황 단위 테스트케이스

> **화면**: [ST] 매입발주 > 매입현황 > 매입발주현황  
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00009`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않아 실제 트리거가 직접 기동하지는 않습니다. 다만, 진행상태 및 입출고 금액 등의 실적 데이터의 정합성을 위해 상위 테이블(`OBSLPHTB`, `OBSLPDTB` 등)에 대한 CUD 발생 시 기동하는 트리거(`Tr_OBSLPH_T01_Service`, `Tr_OBSLPD_T01_Service` 등)의 백엔드 실행 정합성이 선행되어야 합니다.

---

## ⚠️ 서비스 핵심 소스 분석 및 잠재적 버그

### 1. `/search` API 호출 시 `com_procFg` 파라미터 누락에 따른 `NullPointerException` (★★★)
* **소스 분석 (`St_Vendor_00009_Controller.java` L69~80)**:
  * 컨트롤러 단에서 RequestBody로 전달받은 `commandMap`에서 `com_procFg`를 체크할 때, `commandMap.get("com_procFg").equals("")` 형태로 검사합니다.
  * **결과**: 클라이언트가 `/search` 요청 시 `com_procFg` 파라미터를 누락(null 상태)하여 전송할 경우, `commandMap.get("com_procFg")`가 `null`이 되므로 **`NullPointerException` (500 에러)**이 즉각 발생합니다.
  * **예외 케이스**: 단, 프론트엔드 UI(`st_vendor_00009.js`) 상에서는 검색 시 초기값으로 `""` (전체)를 할당하여 보내거나 항상 콤보박스 값을 송신하므로 화면 상의 일반적인 동작 시에는 에러가 발생하지 않으나, 외부 API 호출이나 조작된 요청 시 백엔드 단에서 NPE가 발생할 취약점을 가지고 있습니다.

### 2. 상세 조회 `/detailSearch` 시 `orderDate` 누락에 따른 `NullPointerException` (★★★)
* **소스 분석 (`St_Vendor_00009_Controller.java` L104)**:
  * 컨트롤러 단에서 `commandMap.get("orderDate").toString().replaceAll("-", "")`를 호출하여 날짜 포맷을 변환합니다.
  * **결과**: 만약 상세조회 모달을 띄우는 요청에서 `orderDate` 파라미터가 누락되거나 null인 경우, `null.toString()` 호출 시점에 즉각 **`NullPointerException` (500 에러)**이 발생합니다.

### 3. 프론트엔드 Bootstrap Table 클릭 이벤트 바인딩 매개변수 불일치 (🟢 Info)
* **소스 분석 (`st_vendor_00009_bt.js` L468)**:
  * Bootstrap Table의 공식 `click-cell.bs.table` 이벤트 매개변수 시그니처는 `function (event, field, value, row, $element)` 입니다.
  * 하지만 해당 JS 소스코드에서는 `function (row, $element, field, value)` 순서로 잘못 정의하고 선언해 쓰고 있습니다.
  * **결과**: JS가 동적 타입 매칭을 사용하기 때문에, 첫 번째 변수인 `row`에 실제로는 `event` 객체가 들어오고, `$element` 위치에 `field` 문자열이 들어가고, `value` 위치에 `row` 객체가 들어갑니다. 이에 맞춰 코드 내부에서 `value.orderDate`나 `$element == 'slipNo'` 형태로 속성을 추출하여 다행히 오류 없이 기동하고는 있으나, 매개변수 선언이 원 표준과 뒤바뀌어 있으므로 라이브러리 버전 업데이트 시 작동이 중단될 잠재적 리스크가 있어 매개변수 선언부의 순서 교정을 제안합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, detailSearch, getAffiliateCompany |
| `chainMsNo` | `NC0002` | search, detailSearch |
| `msNo` | `NC0007` (매장코드) | search, detailSearch |

---

## 엔드포인트 목록 (3개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 매입발주현황 전표 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, MVNDRMTB, MMEMBSTB |
| 2 | `/detailSearch` | 전표별 상품 매입발주 상세 내역 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, MGOODSTB |
| 3 | `/getAffiliateCompany` | 체인별 제휴사 구분 코드 조회 (F&B / 브랜드) | `POST` | `String` | SELECT | TCHAINTB |

---

## 1. `/search` — 매입발주현황 전표 목록 조회

| No | 세션 및 파라미터 분기 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 1-1 | F&B 매장 세션 (`chainNo`=C001)<br>진행구분: 전체 (`com_procFg`="")<br>일자구분: 입고일자 (`com_inqDateType`="P") | 해당 매장에 2024-02-01 일자 입고 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_inqDateType":"P","com_procFg":"","com_searchVendr":""}` | - 진행구분 빈값일 때 `PROC_FG`가 '1', '2', '3', '4' 범위 내 전표 모두 검색.<br>- 주문(`SLIP_FG='0'`) 및 반품(`SLIP_FG='1'`) 상태 전표 정상 반환.<br>- 금액 항목(`ORDER_AMT`, `PURCH_AMT`)에 부가세가 가산되어 합산 출력. |
| 1-2 | 진행구분: 발주확정 (`com_procFg`="1")<br>일자구분: 발주일자 (`com_inqDateType`="O") | 2024-02-01 일자에 발주확정 상태의 주문 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_inqDateType":"O","com_procFg":"1","com_searchVendr":""}` | - 컨트롤러 로직에 의해 `slipFg`가 `"0"`으로 자동 분기 매핑됨.<br>- 발주확정(`PROC_FG='1'`) 상태의 주문 전표 목록 정상 반환. |
| 1-3 | 진행구분: 반품확정 (`com_procFg`="6") | 2024-02-01 일자에 반품확정 상태의 반품 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_inqDateType":"P","com_procFg":"6","com_searchVendr":""}` | - 컨트롤러 로직에 의해 `com_procFg`가 `"4"`, `slipFg`가 `"1"`로 분기 매핑됨.<br>- 최종 입고완료단계(`PROC_FG='4'`)의 반품(`SLIP_FG='1'`) 전표 목록 정상 반환. |
| 1-4 | 특정 거래처 코드 필터링 조회 | 해당 거래처 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_inqDateType":"P","com_procFg":"","com_searchVendr":"000001"}` | - `VM.VENDOR = '000001'` 조건이 적용되어 특정 거래처 데이터만 정상 필터링 조회. |
| 1-5 | **com_procFg 누락** (NPE 유발) ★ | - | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_inqDateType":"P"}` | - `commandMap.get("com_procFg")`가 null 상태이므로 **500 NullPointerException** 예외 발생. |

---

## 2. `/detailSearch` — 전표별 상품 매입발주 상세 내역 조회

| No | 세션 및 파라미터 분기 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 2-1 | 주문 전표 상세 조회 (`slipFg`="0") | 해당 전표의 상세 품목(`OBSLPDTB`) 존재 | `{"orderDate":"2024-02-01","msNo":"NC0007","slipFg":"0","slipNo":"0001"}` | - 하이픈(`-`)이 포함된 `orderDate`가 `20240201`로 포맷 변경되어 바인딩됨.<br>- 주문 전표이므로 `ORDER_QTY` 및 `ORDER_AMT` 정상 출력.<br>- `PROC_FG`가 `4`(입고확정)인 경우 입고 수량(`PURCH_QTY`/`PURCH_AMT`) 정상 출력, 아닐 시 `0`으로 분기 처리. |
| 2-2 | 반품 전표 상세 조회 (`slipFg`="1") | 해당 반품 전표의 상세 품목 존재 | `{"orderDate":"2024-02-01","msNo":"NC0007","slipFg":"1","slipNo":"9001"}` | - 반품 전표이므로 발주 수량/금액은 `0`으로 출력.<br>- 입고완료(`PROC_FG='4'`) 상태인 반품 수량이 반품 컬럼(`CANCEL_PURCH_QTY`/`CANCEL_PURCH_AMT`)으로 정상 분리 출력. |
| 2-3 | **orderDate 누락** (NPE 유발) ★ | - | `{"msNo":"NC0007","slipFg":"0","slipNo":"0001"}` | - `commandMap.get("orderDate")`가 null 상태이므로 **500 NullPointerException** 예외 발생. |

---

## 3. `/getAffiliateCompany` — 제휴사 구분 코드 조회

| No | 세션 및 파라미터 분기 | DB 선행 상태 | 요청 방식 및 바디 | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 3-1 | F&B 매장 계정 세션 (`chainNo`="C001") | TCHAINTB에 `AFFILIATE_COMPANY` = '0' 세팅 | (파라미터 없음, 세션 사용) | `"0"` 반환 (화면에서 F&B 기준 콤보박스 동적 렌더링). |
| 3-2 | 브랜드샵 매장 계정 세션 (`chainNo`="C002") | TCHAINTB에 `AFFILIATE_COMPANY` = '1' 세팅 | (파라미터 없음, 세션 사용) | `"1"` 반환 (화면에서 브랜드샵 기준 콤보박스 동적 렌더링). |

---

## PowerShell 테스트 명령

아래 스크립트를 통해 로컬 톰캣 서버에서 API 구동 상태와 잠재적 에러 발생 지점(NPE)을 검증할 수 있습니다.

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# [선행] 매장 계정(fnbcafe)으로 로그인 세션 생성 및 획득
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/vendor/st_vendor_00009"
$h = @{"Content-Type"="application/json"}

Write-Host "=================== 1. 제휴사 구분 코드 조회 검증 ==================="
$affiliate = Invoke-RestMethod -Uri "$base/getAffiliateCompany" -Method POST -WebSession $session
Write-Host "Affiliate Company Code: $affiliate"

Write-Host "`n=================== 2. 매입발주현황 전표 목록 조회 검증 ==================="
$searchBody = '{"searchFromDate":"20240201","searchEndDate":"20240201","com_inqDateType":"P","com_procFg":"","com_searchVendr":""}'
$list = Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session -Body $searchBody
$list | Format-Table -Property orderDate, slipNo, slipFg, vendorNm, orderAmt, purchAmt, procFg

Write-Host "`n=================== 3. 전표별 상세 상품 목록 조회 검증 ==================="
if ($list.Count -gt 0) {
    $firstSlip = $list[0]
    $detailBody = @{
        orderDate = $firstSlip.orderDate
        msNo      = $firstSlip.msNo
        slipFg    = $firstSlip.slipFg
        slipNo    = $firstSlip.slipNo
    } | ConvertTo-Json
    
    $details = Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session -Body $detailBody
    $details | Format-Table -Property orderDate, goodsCd, goodsNm, orderQty, orderAmt, purchQty, purchAmt, cancelPurchQty
} else {
    Write-Host "조회된 전표 데이터가 없어 상세 조회를 건너뜁니다."
}

Write-Host "`n=================== 4. API 에러 취약점 검증 (NPE 발생 확인) ==================="
try {
    # 4-1. com_procFg 누락 시 search 호출
    Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
      -Body '{"searchFromDate":"20240201","searchEndDate":"20240201","com_inqDateType":"P"}'
} catch {
    Write-Host "NPE 발생 성공 (com_procFg 누락): $_"
}

try {
    # 4-2. orderDate 누락 시 detailSearch 호출
    Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
      -Body '{"msNo":"NC0007","slipFg":"0","slipNo":"0001"}'
} catch {
    Write-Host "NPE 발생 성공 (orderDate 누락): $_"
}
```

---

## 주요 검증 포인트

```
□ getAffiliateCompany — 로그인한 사용자의 체인에 따라 제휴사 코드('0' 또는 '1')가 정상적으로 조회되는지 확인
□ search — com_procFg가 비어있을 때 IN ('1','2','3','4') 조건이 쿼리에 정상적으로 매핑되는지 검증
□ search — com_procFg가 '6'(반품확정)일 때 slipFg='1' / procFg='4'로 매핑 변환되는 백엔드 분기 로직 검증
□ search — DECODE(BH.PROC_FG, 4, BH.PURCH_AMT + BH.PURCH_VAT) 구문이 EDB 호환 레이어에서 정상 집계되는지 확인
□ detailSearch — 클라이언트가 'YYYY-MM-DD' 날짜 포맷으로 요청하더라도 백엔드에서 하이픈(-)이 제거되어 정상 쿼리 바인딩되는지 검증
□ detailSearch — 주문전표('0') 시 발주/입고 필드만 활성화되고 반품필드는 0으로 노출되는지 검증
□ detailSearch — 반품전표('1') 시 발주/입고 필드는 0으로 렌더링되고 반품필드에만 수치 데이터가 바인딩되는지 검증
□ Validation — com_procFg 또는 orderDate 누락 시 백엔드 단에서 적절한 예외 처리나 유효성 검증 없이 500 NPE로 전도되는 취약점 확인
```
