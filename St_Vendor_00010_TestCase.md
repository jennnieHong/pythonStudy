# St_Vendor_00010 — 매장 전표별 입고/반품 현황 단위 테스트케이스

> **화면**: [ST] 매입발주 > 매입현황 > 전표별 입고/반품 현황  
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00010`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않아 실제 트리거가 직접 기동하지는 않습니다.

---

## ⚠️ 서비스 핵심 소스 분석 및 잠재적 버그

### 1. `com_procFg` 및 `com_slipFg` 누락 시 NullPointerException 취약점 (★★★)
* **소스 분석 (`St_Vendor_00010_Controller.java` L69, L83)**:
  * 컨트롤러 단에서 RequestBody 파라미터 `com_procFg` 및 `com_slipFg`를 체크할 때, `if(!(commandMap.get("com_procFg").equals(""))` 코드를 가동합니다.
  * **결과**: 만약 클라이언트가 해당 파라미터를 전송하지 않거나 null이 전달되면, `.get(...)`은 `null`을 반환하므로 즉각 **`NullPointerException` (500 에러)**이 발생합니다.
  * **대처**: 조회 조건을 선택하지 않은 상태에서도 반드시 프론트엔드는 `"com_procFg": ""` 및 `"com_slipFg": ""` 처럼 빈 문자열을 JSON 데이터에 담아서 전송해야 안전합니다.

### 2. `/detailSearch` 상세 조회 시 orderDate 누락 NPE 취약점 (★★★)
* **소스 분석 (`St_Vendor_00010_Controller.java` L115)**:
  * 상세조회 시 전달받은 `orderDate` 파라미터에 대해 `.toString().replaceAll("-", "")`를 호출하여 날짜 포맷을 변환합니다.
  * **결과**: `orderDate` 누락 시 즉시 **`NullPointerException` (500 에러)**이 유발됩니다.

### 3. MyBatis XML 내 오라클 레거시 아웃조인 `(+)` 잔재 (★)
* **소스 분석 (`St_Vendor_00010_Sql.xml` L56)**:
  * 쿼리 `getList` 내 조인 조건 L56에 **`AND OH.ORDER_FG = MN.NM_CD(+)`** 가 작성되어 있습니다.
  * **호환성 검증**: EDB Postgres Advanced Server (EPAS)의 오라클 호환 기능(Oracle Compatibility) 덕분에 `(+)` 아웃조인 구문이 런타임에 에러 없이 정상 실행됩니다. 오늘 수행한 E2E 조회 테스트에서도 에러 없이 캡처가 완료되었습니다.
  * **권고사항**: 다만, 호환 설정을 사용하지 않는 순수 PostgreSQL이나 타 표준 DB와의 호환성을 확보하기 위해, 명시적인 ANSI SQL `LEFT OUTER JOIN` 구문으로 리팩토링하는 것을 장기 권장사항으로 분류합니다.

### 4. `com_procFg`에 따른 slipFg/procFg 동적 연계 로직 (★★)
* **소스 분석 (`St_Vendor_00010_Controller.java` L69~80)**:
  * 진행구분(`com_procFg`) 입력값에 따라 맵 내부 파라미터를 동적으로 재할당합니다.
    * `procFg = 5` (반품등록) ➡️ `com_procFg = '1'`, `slipFg = '1'`
    * `procFg = 6` (반품확정) ➡️ `com_procFg = '4'`, `slipFg = '1'`
    * `0 <= procFg <= 4` (매입등록~입고확정) ➡️ `slipFg = '0'`
  * **결과**: 하나의 인풋 파라미터가 백엔드에서 전표구분(`slipFg`) 조건과 진행상태(`procFg`)로 쪼개져 쿼리에 인입되므로, 각 정수형 케이스별 분기 테스트가 정확하게 동작하는지 검증해야 합니다.

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
| 1 | `/search` | 전표별 입고/반품 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, MVNDRMTB, MMEMBSTB, MGOODSTB, MNAMEMTB |
| 2 | `/detailSearch` | 전표별 입고/반품 상세 내역 조회 | `@RequestBody` | `List` | SELECT | OBSLPDTB, MGOODSTB, MMSCLSTB, MNAMEMTB |
| 3 | `/getAffiliateCompany` | 체인 제휴사 구분 조회 | POST | `String` | SELECT | TCHAINTB |

---

## 1. `/search` — 전표별 입고/반품 목록 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 1-1 | 정상 조건 조회 | 매입 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_procFg":"","com_slipFg":""}` | - EPAS 오라클 호환성 덕분에 에러 없이 정상 조회 완료.<br>- 전표 헤더 리스트 반환. |
| 1-2 | **com_procFg 누락** ★ | - | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_slipFg":""}` | `commandMap.get("com_procFg").equals` 시점에 **NullPointerException** (500) |
| 1-3 | **com_slipFg 누락** ★ | - | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_procFg":""}` | `commandMap.get("com_slipFg").equals` 시점에 **NullPointerException** (500) |
| 1-4 | 반품확정 필터 조회 (`com_procFg = "6"`) | 반품확정 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_procFg":"6","com_slipFg":""}` | 백엔드 맵에 `slipFg="1"`, `com_procFg="4"`가 설정되어 반품 확정 데이터만 필터링 조회. |

---

## 2. `/detailSearch` — 전표별 입고/반품 상세조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 2-1 | 정상 상세조회 | 해당 전표 상세이력 존재 | `{"orderDate":"2024-02-01","msNo":"NC0007","slipFg":"0","slipNo":"SLIP01"}` | - 하이픈 제거되어 바인딩 성공.<br>- 전표 내 상품별 출고/입고 상세 리스트 반환. |
| 2-2 | **orderDate 누락** ★ | - | `{"msNo":"NC0007","slipFg":"0","slipNo":"SLIP01"}` | `commandMap.get("orderDate").toString()` 호출 시 **NullPointerException** (500) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/vendor/st_vendor_00010"
$h = @{"Content-Type"="application/json"}

# 1-1. 전표별 입고/반품 목록 조회 (정상 구조 전송)
try {
  Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
    -Body '{"searchFromDate":"20240201","searchEndDate":"20240201","com_procFg":"","com_slipFg":""}'
} catch {
  Write-Host "오라클 조인(+) 문법 에러 확인 요망: $_"
}

# 1-2. com_procFg 누락 시 500 NPE 에러 검증
try {
  Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
    -Body '{"searchFromDate":"20240201","searchEndDate":"20240201","com_slipFg":""}'
} catch {
  Write-Host "NPE 발생 성공: $_"
}

# 2-1. 특정 전표 상세 조회
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"orderDate":"2024-02-01","msNo":"NC0007","slipFg":"0","slipNo":"SLIP01"}'
```

---

## 주요 검증 포인트

```
□ search — MyBatis XML 내 (+) 아웃조인 오라클 레거시 문법의 EPAS 호환 정상 동작 확인 완료 (표준 이식성을 위해 명시적 LEFT JOIN 리팩토링 권장)
□ search — com_procFg, com_slipFg 누락 시 발생하는 NPE 취약성 대응 방안 설계 검증
□ detailSearch — orderDate 파라미터 유실 시 .toString() 호출에 의한 NPE 방어 조치 확인
□ search — com_procFg="6"(반품확정) 인입 시 slipFg="1", com_procFg="4"로 맵 변환되어 MyBatis 쿼리에 올바르게 매핑되는지 검증
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅ (2/2)

| 엔드포인트 | @ServiceLog 선언 현황 |
|-----------|---------------------|
| `/search` (목록 조회) | ✅ SELECT (컨트롤러 L57) |
| `/detailSearch` (상세 조회) | ✅ SELECT (컨트롤러 L106) |

---

## 🔍 프론트엔드(JSP/JS) - 백엔드 파라미터 교차 분석

사용자가 화면(UI)을 통해서만 본 기능을 조작하더라도, **파라미터가 유실되거나 null/undefined가 전송되어 서버 런타임 에러(500 NPE)를 유발할 수 있는 시나리오가 코드 상에서 명확히 증명**됩니다.

### 1. `/search` 목록 조회 시 NPE 누락 가능성 (실제 존재)
* **백엔드 리스크**: `com_procFg` 또는 `com_slipFg` 값이 누락되거나 null이면 `equals("")` 비교 시점에 즉각 **NullPointerException(500)**이 발생합니다.
* **프론트엔드 구현 교차 대조**:
  1. **초기 로딩 시점의 리스크**:
     * 화면 상의 진행구분 셀렉트박스는 비동기 함수 `selectBoxLoad()` 내의 `/getAffiliateCompany` AJAX 콜백을 통해서만 동적으로 추가(`append`) 및 초기화(`selectpicker()`) 처리됩니다.
     * 만약 최초 화면 렌더링 도중 네트워크 지연이나 스크립트 실행 지연으로 인해 `selectBoxLoad()`가 아직 완료되지 않은 상태(또는 에러로 실행 중단된 상태)에서 사용자가 조회 버튼을 즉시 누르게 되면, `queryParams` 함수가 실행됩니다.
     * 이때 `$("#com_procFg").val()`을 가져오는 로직은 DOM에 해당 엘리먼트가 존재하지 않기 때문에 `undefined`를 반환하게 되며, 이로 인해 서버 전송 시 `com_procFg` 필드가 JSON 바디에서 아예 누락되거나 null 상태로 전송되어 백엔드 컨트롤러 L69에서 NPE 에러가 즉시 터지게 됩니다.

### 2. `/detailSearch` 상세 조회 시 NPE 누락 가능성 (실제 존재)
* **백엔드 리스크**: `orderDate` 값이 누락되거나 null이면 `toString()`에 의해 즉각 **NullPointerException(500)**이 발생합니다.
* **프론트엔드 구현 교차 대조**:
  1. **잘못된 이벤트 핸들러 선언 (`st_vendor_00010_bt.js` L727-740)**:
     ```javascript
     $('#st_vendor_00010_t01').on('click-cell.bs.table', function (row, $element, field, value) { ... });
     ```
     * Bootstrap Table의 공식 `click-cell.bs.table` 이벤트 매개변수 시그니처는 `function (event, field, value, row, $element)` 입니다.
     * JS 소스코드에서는 `(row, $element, field, value)` 순서로 잘못 선언되어 있습니다. 
     * 라이브러리 버전업 또는 브라우저 환경에 따라 매개변수 파싱에 오동작을 일으킬 시, 세 번째 인자인 `orderDate` 등이 정상적으로 읽히지 않아 상세 팝업 오픈이 실패하거나 에러를 유발할 수 있는 구조적인 위험이 있습니다.
  2. **사용자 조작에 의한 날짜 파라미터 유실**:
     * 상세 조회 함수 `fnDetail(orderDate, msNo, slipFg, slipNo, procFg, vendorNm)`는 셀 클릭 시 현재 화면 상의 `value.orderDate`(실제로는 `row.orderDate`) 값을 읽어서 상세조회 AJAX 요청을 전송합니다.
     * 만약 데이터 마이그레이션 오류나 그리드 렌더링 실패로 인해 테이블 내 특정 로우의 `orderDate` 필드 값이 null이거나 빈 값으로 노출된 상태에서 전표번호 셀을 클릭하면, `orderDate` 변수에는 빈 문자열 `""` 혹은 `undefined`가 할당됩니다.
     * 프론트엔드 `fnDetail()` 내에는 날짜 입력 누락에 대한 **자체 Validation(유효성 검증) 로직이 전혀 없습니다**.
     * 결국 빈 문자열 `""`이나 `undefined` 상태의 파라미터가 서버 `/detailSearch`로 전달되면, 백엔드 컨트롤러 L115에서 `.toString()`을 수행할 때 `null` 또는 문자열 객체에 대한 런타임 예외가 터지며 서버 오류가 발생하게 됩니다.
