# Hq_Vendor_00013 — 본사 상품별 입고/반품 현황 단위 테스트케이스

> **화면**: [HQ] 매입발주 > 매입현황 > 상품별 입고/반품 현황  
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00013`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않습니다.

---

## ⚠️ 서비스 핵심 소스 분석 및 잠재적 버그

### 1. `/detailSearch` 상세 조회 시 NullPointerException 취약점 (★★★)
* **소스 분석 (`Hq_Vendor_00013_Controller.java` L87~88)**:
  * 상세조회 시 파라미터 `searchFromDate`, `searchEndDate`에 대해 `.toString().replaceAll("-", "")`를 호출합니다.
  * **결과**: `searchFromDate` 또는 `searchEndDate`가 누락되거나 null이 전달되면 즉시 **`NullPointerException` (500 에러)**이 발생합니다.

### 2. 본사 체인 소속 매장 데이터 합산 및 매장 필터링 (★★)
* **소스 분석 (`Hq_Vendor_00013_Sql.xml` L64~67)**:
  * 쿼리 `getList`는 본사 로그인 세션의 `chainNo` 하위에 존재하는 모든 매장 데이터를 로드합니다 (`MM.CHAIN_NO = #{chainNo}`).
  * 매장 필터 `com_selectMsNo` 파라미터가 있을 때만 동적으로 특정 매장의 입고 전표를 필터링합니다.
  * **결과**: 권한 및 데이터 격리 검증 시 타 본사 체인의 매장 정보가 조회되지 않는지, 그리고 매장 필터 선택 시 정상적으로 동작하는지 검증이 필수적입니다.

### 3. `PROC_FG` 문자열 상호 비교 호환성 검증 (★★)
* **소스 분석 (`Hq_Vendor_00013_Sql.xml` L25~28, L113~116)**:
  * 본사 XML 쿼리에서는 `DECODE(OH.PROC_FG, '4', ...)`와 같이 문자열 `'4'` 리터럴 조건을 비교 집계하고 있습니다.
  * 매장 화면(`st_vendor_00011`) 쿼리에서 `DECODE(OH.PROC_FG, 4, ...)`로 숫자로 비교하는 것과 상이하므로 EDB PostgreSQL 마이그레이션 적합성 검토 시 해당 타입 매칭 오류가 없는지 테스트해야 합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, detailSearch, getAffiliateCompany |

---

## 엔드포인트 목록 (3개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 상품별 입고/반품 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, MGOODSTB, MMSCLSTB, MMEMBSTB, MNAMEMTB |
| 2 | `/detailSearch` | 상품별 입고/반품 상세 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, MMEMBSTB, MGOODSTB |
| 3 | `/getAffiliateCompany` | 체인 제휴사 구분 조회 | POST | `String` | SELECT | TCHAINTB |

---

## 1. `/search` — 상품별 입고/반품 목록 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 1-1 | 정상 조건 조회 | 본사 산하 매장에 매입 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201"}` | - EDB PostgreSQL 기반 집계 목록 반환.<br>- 본사 권한 전체 매장의 입고 정보 조회됨. |
| 1-2 | 특정 매장 필터 조회 (`com_selectMsNo = "NC0007"`) | NC0007 매장 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_selectMsNo":"NC0007"}` | `OH.MS_NO = 'NC0007'` 조건이 동적으로 적용되어 특정 매장 데이터만 필터링 조회. |
| 1-3 | 진행구분 필터 조회 (`com_procFg = "2"`) | 발주/검수확정 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_procFg":"2"}` | `OH.PROC_FG = '2'` 조건이 적용되어 조회. |

---

## 2. `/detailSearch` — 상품별 입고/반품 상세조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 2-1 | 정상 상세조회 | 해당 상품 입고 전표 존재 | `{"goodsCd":"T0000001","searchFromDate":"2024-02-01","searchEndDate":"2024-02-01"}` | - 하이픈이 제거되어 바인딩 성공.<br>- 매장별 상세 입고 리스트 리턴. |
| 2-2 | **searchFromDate 누락** ★ | - | `{"goodsCd":"T0000001","searchEndDate":"2024-02-01"}` | `commandMap.get("searchFromDate").toString()` 호출 시 **NullPointerException** (500) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/vendor/hq_vendor_00013"
$h = @{"Content-Type"="application/json"}

# 1-1. 본사 상품별 입고/반품 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20240201","searchEndDate":"20240201"}'

# 2-1. 특정 상품 상세 조회
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"goodsCd":"T0000001","searchFromDate":"2024-02-01","searchEndDate":"2024-02-01"}'

# 2-2. searchFromDate 누락 시 500 NPE 에러 검증
try {
  Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
    -Body '{"goodsCd":"T0000001","searchEndDate":"2024-02-01"}'
} catch {
  Write-Host "NPE 발생 성공: $_"
}
```

---

## 주요 검증 포인트

```
□ detailSearch — searchFromDate/searchEndDate 누락 시 NPE 검증 및 서버 사이드 예외 방지책 확인
□ search — com_selectMsNo 매장 선택 필터에 따른 본사 소속 매장 데이터 격리/보안 무결성 검증
□ getList 쿼리 — DECODE(OH.PROC_FG, '4', ...) 문자 리터럴 조건 비교의 EDB 마이그레이션 정합성 검증
□ detailSearch 쿼리 — DECODE(OH.PROC_FG, '4', TO_CHAR(...), '') 분기 구문 호환성 확인
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅ (2/2)

| 엔드포인트 | @ServiceLog 선언 현황 |
|-----------|---------------------|
| `/search` (목록 조회) | ✅ SELECT (컨트롤러 L57) |
| `/detailSearch` (상세 조회) | ✅ SELECT (컨트롤러 L79) |

---

## 🔍 프론트엔드(JSP/JS) - 백엔드 파라미터 교차 분석

사용자가 화면(UI)을 통해서만 본 기능을 조작하더라도, **파라미터가 유실되거나 null/undefined가 전송되어 서버 런타임 에러(500 NPE)를 유발할 수 있는 시나리오가 코드 상에서 명확히 증명**됩니다.

### 1. `/detailSearch` 상세 조회 시 NPE 누락 가능성 (실제 존재)
* **백엔드 리스크**: `searchFromDate`, `searchEndDate` 값 중 하나라도 존재하지 않거나 null이면 `toString()`에 의해 즉각 **NullPointerException(500)**이 발생합니다.
* **프론트엔드 구현 교차 대조**:
  1. **잘못된 이벤트 핸들러 선언 (`hq_vendor_00013_bt.js` L709-719)**:
     ```javascript
     $('#hq_vendor_00013_t01').on('click-cell.bs.table', function (row, $element, field, value) { ... });
     ```
     * Bootstrap Table의 공식 `click-cell.bs.table` 이벤트 매개변수 시그니처는 `function (event, field, value, row, $element)` 입니다.
     * 그러나 JS 소스코드에서는 `(row, $element, field, value)` 순서로 잘못 선언되어 있습니다. 
     * 라이브러리 버전업 또는 브라우저 환경에 따라 매개변수 파싱에 오동작을 일으킬 시, 세 번째 인자인 `goodsCd` 등이 정상적으로 읽히지 않아 상세 팝업 오픈이 실패하거나 에러를 유발할 수 있는 구조적인 위험이 있습니다.
  2. **사용자 조작에 의한 날짜 파라미터 유실**:
     * 상세 조회 함수 `fnDetail(fromDate, toDate, goodsCd, goodsNm)`는 셀 클릭 시 현재 화면 상의 input 엘리먼트 값인 `$("#searchFromDate").val()`과 `$("#searchEndDate").val()`을 읽어서 상세조회 AJAX 요청을 전송합니다.
     * 메인 조회(`/search`)를 수행한 이후, 사용자가 날짜 입력 필드(`#searchFromDate` 또는 `#searchEndDate`)의 날짜 값을 지우거나(Clear), 임의로 백스페이스 등을 통해 빈 값으로 변경한 뒤 상품명 셀을 클릭하면, `searchFromDate` 또는 `searchEndDate` 변수에는 빈 문자열 `""` 혹은 `undefined`가 할당됩니다.
     * 프론트엔드 `fnDetail()` 내에는 날짜 입력 누락에 대한 **자체 Validation(유효성 검증) 로직이 전혀 없습니다**.
     * 결국 빈 문자열 `""`이나 `undefined` 상태의 파라미터가 서버 `/detailSearch`로 전달되면, 백엔드 컨트롤러 L87-88에서 `.toString()`을 수행할 때 `null` 또는 문자열 객체에 대한 런타임 예외가 터지며 서버 오류가 발생하게 됩니다.
