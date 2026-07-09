# St_Vendor_00008 — 매장 거래처별 상품 입고현황 단위 테스트케이스

> **화면**: [ST] 매입발주 > 매입현황 > 거래처별 상품 입고현황  
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00008`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않아 실제 트리거가 직접 기동하지는 않습니다.

---

## ⚠️ 서비스 핵심 소스 분석 및 잠재적 버그

### 1. `chainHqYn = "Y"` (본사 권한) 검색 시 SQL Syntax Error 위험 (★)
* **소스 분석 (`St_Vendor_00008_Sql.xml` L49~69)**:
  * 본사 권한이 아닐 때(`chainHqYn = "N"`)에만 `FROM` 절에 거래처 서브쿼리인 `F`를 조인하도록 동적 SQL이 작성되어 있습니다.
  * 그러나 `WHERE` 절 L100~101(`AND A.MS_NO = F.MS_NO AND A.VENDOR = F.VENDOR`) 및 `GROUP BY`/`SELECT` 절에서는 `F` 테이블을 조건 없이 상시 참조하고 있습니다.
  * **보안 통제 분석**: 실제 UI 상에서는 본사 권한 계정(`shopadmin`)으로 `st_vendor_00008` (매장 전용) 화면 주소 접근 시 스프링 시큐리티 필터에 의해 `302 accessDenied`로 튕기기 때문에, 일반 사용자가 이 오류를 겪을 확률은 없습니다. 다만, 쿼리 상의 미사용 레거시 복사/붙여넣기 조건문 잔재이므로 SQL 정리와 혹시 모를 API 위조 호출 방지를 위해 수정을 권고합니다.
  * **결과**: 만약 임의로 세션 권한을 우회하여 백엔드 `/search` API에 본사 세션으로 직접 POST 요청을 위조 송신할 경우, From절에 `F` 테이블이 누락되므로 **`Relation "f" does not exist` (SQL 런타임 에러)**가 발생하게 됩니다.

### 2. 상세 조회 `/detailSearch` 시 NullPointerException 취약점 (★★★)
* **소스 분석 (`St_Vendor_00008_Controller.java` L91~92)**:
  * 컨트롤러 단에서 RequestBody로 전달받은 `fromDate` 및 `toDate` 파라미터에 대해 `.toString().replaceAll("-", "")`를 호출하여 날짜 포맷을 변환합니다.
  * **결과**: 만약 클라이언트가 상세 조회 요청 시 `fromDate` 또는 `toDate` 파라미터를 누락하거나 null로 보내면, 해당 객체가 null이 되므로 **`NullPointerException` (500 에러)**이 발생합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, detailSearch |
| `chainHqYn` | `N` | search (동적 SQL 분기용) |
| `chainMsNo` | `NC0002` | search |
| `msNo` | `NC0007` (매장코드) | search, detailSearch |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 거래처별 상품 입고현황 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, MGOODSTB, MNAMEMTB, MMSCLSTB, MVNDRMTB |
| 2 | `/detailSearch` | 상품별 매입 상세정보 조회 (원장 팝업) | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, MMEMBSTB, MGOODSTB, MVNDRMTB |

---

## 1. `/search` — 거래처별 상품 입고현황 조회

| No | 세션 및 파라미터 분기 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 1-1 | chainHqYn=`N`<br>wenvValFg=`1` (매장설정) | 매입입고 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201"}` | `chainMsNo` 기준으로 매장 거래처(`MVNDRMTB`) 정보가 조인되어 정상 목록 반환 (입고수량, 입고금액 합산됨) |
| 1-2 | chainHqYn=`N`<br>wenvValFg=`0` (또는 null) | 매입입고 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201"}` | `msNo` 기준으로 매장 거래처 정보가 조인되어 정상 목록 반환 |
| 1-3 | **chainHqYn=`Y`** (본사권한) ★ | 매입입고 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201"}` | 화면 레벨 접근 불가 (302 accessDenied로 차단). API 단독 요청 시 **500 SQL Error** (From절 F 테이블 누락). |
| 1-4 | com_searchVendr 필터 추가 | 특정 거래처 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_searchVendr":"000001"}` | 특정 거래처 코드에 해당하는 입고 데이터만 필터링 조회 |
| 1-5 | lclass/mclass/sclass 필터 | 특정 카테고리 상품 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","lclassCd":"01","mclassCd":"01","sclassCd":"01"}` | 상품 소분류 카테고리 조인을 통한 상품 필터링 정상 조회 |
| 1-6 | msNo 누락 (세션 끊김) | - | `{"searchFromDate":"20240201"}` | `param.get("msNo").toString()` 호출 시 **NullPointerException** (500) |

---

## 2. `/detailSearch` — 상품별 매입 상세정보 조회

| No | 세션 및 파라미터 분기 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 2-1 | 정상 세션 및 파라미터 | 해당 상품 입고이력 존재 | `{"goodsCd":"T0000001","fromDate":"2024-02-01","toDate":"2024-02-01"}` | - 날짜의 `-` 하이픈이 정상 제거되어 쿼리 바인딩됨.<br>- 상품별 일자별 입고 상세 리스트 반환. |
| 2-2 | **fromDate 누락** ★ | - | `{"goodsCd":"T0000001","toDate":"2024-02-01"}` | `commandMap.get("fromDate").toString()` 호출 시 **NullPointerException** (500) |
| 2-3 | 존재하지 않는 상품코드 | - | `{"goodsCd":"99999999","fromDate":"2024-02-01","toDate":"2024-02-01"}` | 데이터 정합성에 의해 빈 배열(`[]`) 정상 리턴 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/vendor/st_vendor_00008"
$h = @{"Content-Type"="application/json"}

# 1-1. 거래처x상품별 입고현황 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20240201","searchEndDate":"20240201"}'

# 2-1. 특정 상품 입고 상세 정보 조회 (모달 데이터)
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"goodsCd":"T0000001","fromDate":"2024-02-01","toDate":"2024-02-01"}'

# 2-2. fromDate 누락 시 500 NPE 에러 검증
try {
  Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
    -Body '{"goodsCd":"T0000001","toDate":"2024-02-01"}'
} catch {
  Write-Host "NPE 발생 성공: $_"
}
```

---

## 주요 검증 포인트

```
□ search — chainHqYn="Y" (본사권한) 일 때 SQL Syntax Error (Relation f does not exist) API 우회 호출 테스트
□ security — 본사 계정이 매장 화면 접근 시 302 accessDenied 리다이렉트 필터 작동 확인 완료
□ detailSearch — fromDate/toDate 누락 시 commandMap.get("fromDate").toString()에 의한 NPE 검증
□ getList 쿼리 — DECODE 문법이 EDB 호환 레이어에서 오동작 없이 올바른 통계치를 집계해 오는지 검증
□ getList 쿼리 — 매장 설정(wenvValFg="1")에 따른 MVNDRMTB 조인 시 chainMsNo 바인딩 정합성 검증
□ detailSearch 쿼리 — TO_DATE(A.PURCH_DATE, 'YYYYMMDD') 포맷팅이 PostgreSQL 표준과 호환되는지 확인
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅ (2/2)

| 엔드포인트 | @ServiceLog 선언 현황 |
|-----------|---------------------|
| `/search` (목록 조회) | ✅ SELECT (컨트롤러 L57) |
| `/detailSearch` (상세 조회) | ✅ SELECT (컨트롤러 L82) |

---

## 🔍 프론트엔드(JSP/JS) - 백엔드 파라미터 교차 분석

사용자가 화면(UI)을 통해서만 본 기능을 조작하더라도, **파라미터가 유실되거나 null/undefined가 전송되어 서버 런타임 에러(500 NPE)를 유발할 수 있는 시나리오가 코드 상에서 명확히 증명**됩니다.

### 1. `/detailSearch` 상세 조회 시 NPE 누락 가능성 (실제 존재)
* **백엔드 리스크**: `fromDate`, `toDate` 값 중 하나라도 존재하지 않거나 null이면 `toString()`에 의해 즉각 **NullPointerException(500)**이 발생합니다.
* **프론트엔드 구현 교차 대조**:
  1. **잘못된 이벤트 핸들러 선언 (`st_vendor_00008_bt.js` L630-639)**:
     ```javascript
     $('#st_vendor_00008_t01').on('click-cell.bs.table', function (row, $element, field, value) { ... });
     ```
     * Bootstrap Table의 공식 `click-cell.bs.table` 이벤트 매개변수 시그니처는 `function (event, field, value, row, $element)` 입니다.
     * 그러나 JS 소스코드에서는 `(row, $element, field, value)` 순서로 잘못 선언되어 있습니다. 
     * 다행히 매핑 구조상 `$element` 위치에 `field` 문자열이 들어가고, `value` 위치에 `row` 객체가 할당되어 비정상적으로 동작하지는 않는 것처럼 보이지만, 라이브러리 버전업 또는 브라우저 환경에 따라 매개변수 파싱에 오동작을 일으켜 `value`가 `undefined`로 떨어질 위험이 매우 큽니다.
  2. **사용자 조작에 의한 날짜 파라미터 유실**:
     * 상세 조회 함수 `fnDetail(fromDate, toDate, goodsCd, ...)`는 셀 클릭 시 현재 화면 상의 input 엘리먼트 값인 `$("#searchFromDate").val()`과 `$("#searchEndDate").val()`을 읽어서 AJAX로 서버에 쏩니다.
     * 메인 조회(`/search`)를 수행한 이후, 사용자가 날짜 입력 필드(`#searchFromDate` 또는 `#searchEndDate`)의 날짜 값을 지우거나(Clear), 임의로 백스페이스 등을 통해 빈 값으로 변경한 뒤 상품코드 셀을 클릭하면, `fromDate` 또는 `toDate` 변수에는 빈 문자열 `""` 혹은 `undefined`가 할당됩니다.
     * 프론트엔드 `fnDetail()` 내에는 날짜 입력 누락에 대한 **자체 Validation(유효성 검증) 로직이 전혀 없습니다**.
     * 결국 빈 문자열 `""`이나 `undefined` 상태의 파라미터가 서버 `/detailSearch`로 전달되면, 백엔드 컨트롤러 L91-92에서 `.toString()`을 수행할 때 `null` 또는 문자열 객체에 대한 런타임 예외가 터지며 서버 오류가 발생하게 됩니다.

