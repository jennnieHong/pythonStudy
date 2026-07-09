# Hq_Vendor_00019 — 본사 매장별 입고현황 단위 테스트케이스

> **화면**: [HQ] 매입발주 > 매입현황 > 일자별 입고 현황 / 매장별 입고 현황  
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00019`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않습니다.

---

## ⚠️ 서비스 핵심 소스 분석 및 잠재적 버그

### 1. `goodsCdArr` 누락 시 NullPointerException 취약점 (★★★)
* **소스 분석 (`Hq_Vendor_00019_Controller.java` L65)**:
  * 컨트롤러 단에서 RequestBody 파라미터 `goodsCdArr`에 대해 `.equals("ALL")` 및 `.toString()`을 바로 호출하여 문자열 파싱을 수행합니다.
  * **결과**: 만약 클라이언트가 `goodsCdArr` 키 값을 누락하거나 null로 전송하면, 해당 필드가 null이 되므로 호출 즉시 **`NullPointerException` (500 에러)**이 발생합니다.
  * **대처**: 상품코드 필터링을 사용하지 않을 때에도 반드시 클라이언트는 `"goodsCdArr": "ALL"` 형태로 호출해주어야 안전합니다.

### 2. `DATE_NUM`, `VENDOR_NUM` 윈도우 함수를 활용한 그리드 가독성 제어 (★★)
* **소스 분석 (`Hq_Vendor_00019_Sql.xml` L11~38)**:
  * EDB SQL 내에서 `ROW_NUMBER() OVER(PARTITION BY PURCH_DATE ...)` 함수를 사용해 행 번호(`DATE_NUM`, `VENDOR_NUM`)를 계산합니다.
  * 최외곽 SELECT 절에서 `DECODE(DATE_NUM, '1', PURCH_DATE)`를 호출하여, 동일한 일자의 데이터가 여러 건 있을 때 **가장 첫 번째 로우에만 날짜와 거래처명을 찍고 나머지는 공백으로 치환**해 줍니다.
  * **결과**: 그리드의 첫 행에만 그룹 레이블이 노출되고 나머지는 비어 보이게 되므로, UI 렌더링 시 이 디코딩된 값이 누락 없이 올바르게 매칭되는지 확인해야 합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search |

---

## 엔드포인트 목록 (1개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 일자별/매장별 입고 현황 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, MMEMBSTB, TGOODSTB, TVNDRMTB, MNAMEMTB |

---

## 1. `/search` — 일자별/매장별 입고 현황 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|---|------------|---------------------|----------------------|
| 1-1 | 정상 조건 조회<br>(goodsCdArr = "ALL") | 입고 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL"}` | - EDB PostgreSQL 기반 정상 집계 목록 반환.<br>- 첫 로우에만 일자와 거래처명이 출력되고 나머지는 공백 처리됨. |
| 1-2 | **goodsCdArr 누락** ★ | - | `{"searchFromDate":"20240201","searchEndDate":"20240201"}` | `equals("ALL")` 호출 시점에 **NullPointerException** (500) |
| 1-3 | 다중 상품코드 필터링 | 해당 상품 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"T0000001,T0000002"}` | 콤마(`,`)로 split된 `goodsCdList` 배열 조건이 MyBatis `<foreach>`에 매핑되어 해당 상품만 필터 조회됨. |
| 1-4 | 의제매입 대상만 조회 (`ficFg = "Y"`) | 의제매입 상품 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL","ficFg":"Y"}` | `TAX_FG = '0' AND FICTITIOUS_YN = 'Y'` 조건이 적용되어 면세/의제매입 대상 상품만 필터링 조회. |
| 1-5 | 일반 면세 대상 조회 (`ficFg = "N"`) | 면세 상품 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL","ficFg":"N"}` | `TAX_FG = '0'` 조건이 동적으로 적용되어 면세 상품 전체 조회. |
| 1-6 | 카테고리 및 매장 필터 조회 | 분류 데이터 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL","msNo":"NC0007","lclassCd":"01"}` | `HD.MS_NO = 'NC0007'` 및 대분류 코드 조건에 해당하는 입고 내역만 필터 조회. |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/vendor/hq_vendor_00019"
$h = @{"Content-Type"="application/json"}

# 1-1. 정상 입고현황 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL"}'

# 1-3. 다중 상품 필터링 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"T0000001,T0000002"}'

# 1-2. goodsCdArr 누락으로 인한 500 NPE 에러 검증
try {
  Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
    -Body '{"searchFromDate":"20240201","searchEndDate":"20240201"}'
} catch {
  Write-Host "NPE 발생 성공: $_"
}
```

---

## 주요 검증 포인트

```
□ search — goodsCdArr 누락 시 컨트롤러 단 equals("ALL")에 의한 NPE 검증 및 방어 방안 마련
□ search — 다중 상품코드 콤마 파싱 및 MyBatis foreach 조건 바인딩 무결성 검증
□ search — ficFg 조건 변경에 따른 의제매입(TAX_FG=0 & FICTITIOUS_YN=Y) 동적 쿼리 분기 작동 검증
□ 롤업 뷰 — DATE_NUM 및 VENDOR_NUM 윈도우 함수 동작 시 PostgreSQL/EDB 호환성 검증
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅ (1/1)

| 엔드포인트 | @ServiceLog 선언 현황 |
|-----------|---------------------|
| `/search` | ✅ SELECT (컨트롤러 L56) |

---

## 🔍 프론트엔드(JSP/JS) - 백엔드 파라미터 교차 분석

사용자가 화면(UI)을 통해서만 본 기능을 조작하더라도, **파라미터가 유실되거나 null/undefined가 전송되어 서버 런타임 에러(500 NPE)를 유발할 수 있는 시나리오가 코드 상에서 명확히 증명**됩니다.

### 1. `/search` 목록 조회 시 `goodsCdArr` 누락 및 NPE 발생 시나리오
* **백엔드 리스크**: `goodsCdArr` 파라미터가 null인 경우 `commandMap.get("goodsCdArr").equals("ALL")` 코드에서 예외 처리 없이 즉각 **NullPointerException(500)**이 발생합니다.
* **프론트엔드 구현 교차 대조**:
  1. **동적 DOM 생성에 따른 유실 위험**:
     * 화면 상의 상품 선택 입력 필드는 JSP 내에 정적으로 존재하지 않고, JS 로딩 시 공통 초기화 함수인 `fn_com_goodsSearchInit('searchGoods', '2')`를 통해 `#searchGoods` div 내부에 비동기/동적으로 생성됩니다:
       ```javascript
       $selectDiv.append("<input type='text' class='form-control' id='searchGoods_goosCd_Input' readonly />");
       ```
     * 만약 공통 JS 스크립트(`backoffice.module.condition.js`)가 네트워크 불안정으로 인해 로드되지 못하거나, 브라우저 스크립트 엔진 오류로 인해 초기화 함수 실행 중 에러가 나면 해당 DOM 객체가 생성되지 않습니다.
     * 이 경우, 조회(`/search`) 이벤트 시 호출되는 `hq_vendor_00019_t01_queryParams` 함수는 생성되지 않은 엘리먼트에 접근하게 됩니다:
       ```javascript
       params.goodsCdArr = $("#searchGoods_goosCd_Input").val();
       ```
     * DOM에 존재하지 않는 엘리먼트에 대해 jQuery `.val()`을 호출하면 `undefined`를 반환하며, 이는 JSON 데이터 패키징 과정에서 아예 키가 누락되거나 null 상태로 백엔드로 전송됩니다.
     * 백엔드는 프론트엔드에서 공통 컴포넌트가 항상 성공적으로 로드되어 `goodsCdArr`이 무조건 전송될 것이라 보장하는 구조(Validation 부재)이므로, 즉각 NPE 예외가 발생해 화면이 뻗어버리게 됩니다.

