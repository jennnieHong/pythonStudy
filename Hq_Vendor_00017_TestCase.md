# Hq_Vendor_00017 — 거래처별 입고집계표 단위 테스트케이스 (v2)

> **대상 화면**: [HQ] 매입발주 > 매입현황 > 거래처별 입고집계표 (`hq_vendor_00017`)  
> **API Base URL**: `POST /backoffice/data/hq/vendor/hq_vendor_00017`  
> **트랜잭션 설정**: `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})` (SELECT 전용)  
> **데이터 수신 방식**: `@RequestBody Map<String, Object> commandMap` (전 엔드포인트 공통)  
> **DB 영향도**: 단순 데이터 조회 화면으로 CUD/트리거 연쇄 영향 없음 (Depth 3 Side Effect 없음)

---

## 1. 테스트 선행 및 세션 조건

| 세션 변수명 | 필요성 | 데이터 예시 | 비고 |
| :--- | :--- | :--- | :--- |
| `chainNo` | **필수** | `C001` (HMS F&B 체인) | 권한별 조회 필터의 기준 (Mapper 바인딩) |
| `chainNm` | **필수 (출력용)** | `HYUNDAI MOTORSTUDIO` | `/print` ModelAndView 빌드 시 사용 |

> [!WARNING]
> **권한 격리 주의**: 본 화면은 소속 체인의 데이터만 조회할 수 있습니다. 
> 예를 들어, `NC0007` 매장 데이터는 `C001` 권한 계정(`shopadmin`)으로만 조회 가능하며, 타 체인 계정(`7249525SHOP` 등)으로 조회 시 세션의 `chainNo` 불일치로 빈 결과가 리턴됩니다.

---

## 2. 엔드포인트 명세 및 쿼리 매핑

| # | URL 엔드포인트 | HTTP Method | 기능 요약 | 데이터 반환 | 연관 테이블 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | `/search` | POST | 거래처별 입고집계 목록 조회 | `List<Hq_Vendor_00017_GetListDto>` | `OBSLPHTB`, `OBSLPDTB`, `MGOODSTB`, `TVNDRMTB` |
| 2 | `/print` | POST | 거래처별 입고집계 출력 렌더링 | `ModelAndView` (`hq_vendor_00017_printOrder`) | `OBSLPHTB`, `OBSLPDTB`, `MGOODSTB`, `TVNDRMTB` |

---

## 3. 소스코드 정적 분석 기반 핵심 결함 포인트

### 🔴 3.1 `goodsCdArr` 누락에 의한 NullPointerException (NPE)
*   **발생 위치**: `Hq_Vendor_00017_Controller.java` (L66, L95)
*   **원인**: 컨트롤러에서 `goodsCdArr` 파라미터가 API 요청에 누락되거나 null로 송신되는 경우, null 객체에 대해 바로 `.equals()`를 수행하여 서버 500 에러를 터뜨립니다.
    ```java
    // 방어 코드 결여로 인한 NPE 유발 코드
    if (!commandMap.get("goodsCdArr").equals("ALL") && ...) { ... }
    ```
*   **해결책**: `if (commandMap.get("goodsCdArr") != null && !"ALL".equals(commandMap.get("goodsCdArr").toString()))` 로 Null-Safe하게 변경해야 합니다.

### 🔴 3.2 `chainNm` 세션 누락에 의한 NullPointerException (NPE)
*   **발생 위치**: `Hq_Vendor_00017_Controller.java` (L106 - `/print`)
*   **원인**: 출력(/print) 서비스 요청 시 로그인한 사용자의 세션 정보 중 `chainNm` 값이 누락되어 있을 경우 `.toString()` 호출 과정에서 서버가 즉사합니다.
    ```java
    mav.addObject("chainNm", securityUserInformation.getUserInfo("chainNm").toString());
    ```

### 🟡 3.3 출력(/print) 화면 렌더링 시 404 리소스 바인딩 오류
*   **현상**: E2E 테스트 및 브라우저 검증 중 인쇄 미리보기 화면 로딩 시 아래 리소스 404 경고가 발생합니다.
    ```
    GET http://localhost:8080/backoffice/assets/main/contents////css/.css?v=202606091326 -> 404 Not Found
    ```
*   **원인**: 출력용 JSP 내부의 스타일시트 바인딩 중 경로 변수가 비어 `.css` 파일을 강제 로드하려는 리소스 주소 누락 결함입니다.

---

## 4. 상세 테스트케이스 (Unit & E2E)

### 4.1 `/search` — 거래처별 입고집계표 조회

| TC ID | 테스트 시나리오 | 입력 데이터 (JSON Body) | 세션 조건 | 기대 결과 | 판정 기준 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-101** | 전 기간 & 전체 상품 조회 (정상) | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL"}` | `chainNo="C001"` | HTTP 200, 전 거래처의 입고 데이터 목록 반환 | `List.size() > 0` |
| **TC-102** | 상품코드 CSV 필터 조회 (정상) | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"T0000033,T0000034"}` | `chainNo="C001"` | 해당 상품코드 리스트에 매핑되는 입고 정보만 필터링 | `goodsCdList` 배열 파싱 |
| **TC-103** | `goodsCdArr` 빈 값 처리 (정상) | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":""}` | `chainNo="C001"` | 빈 값 입력 시 "ALL"과 동일하게 전체 상품 목록 집계 | `isEmpty() == true` 분기 |
| **TC-104** | **`goodsCdArr` 누락 시 결함 검증** | `{"searchFromDate":"20240201","searchEndDate":"20240201"}` | `chainNo="C001"` | **HTTP 500 (Internal Server Error)** 발생 | **`NullPointerException`** |
| **TC-105** | 데이터가 없는 기간 조회 (정상) | `{"searchFromDate":"19990101","searchEndDate":"19990101","goodsCdArr":"ALL"}` | `chainNo="C001"` | HTTP 200, 빈 배열 반환 | `[]` 반환 |
| **TC-106** | 권한 밖의 타 체인 조회 (차단) | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL"}` | `chainNo='C001'` | `C001` 매장 정보가 집계에서 배제되어 빈 배열 반환 | `[]` 반환 |
| **TC-107** | 특정 거래처 및 매장 필터 조회 | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL","vendor":"RWTA","msNo":"NC0007"}` | `chainNo="C001"` | 매장 `NC0007`, 거래처 `RWTA` 조건에 부합하는 정밀 집계 | 1건 집계 완료 |

<br>

### 4.2 `/print` — 거래처별 입고집계표 출력 렌더링

| TC ID | 테스트 시나리오 | 입력 데이터 (JSON Body) | 세션 조건 | 기대 결과 | 판정 기준 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-201** | 정상 인쇄 화면 출력 | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL"}` | `chainNo="C001"`, `chainNm="HMS"` | HTTP 200, ModelAndView 객체 리턴 및 인쇄 JSP 바인딩 | `printList` 데이터 포함 |
| **TC-202** | **`goodsCdArr` 누락 시 인쇄 요청** | `{"searchFromDate":"20240201","searchEndDate":"20240201"}` | `chainNo="C001"`, `chainNm="HMS"` | **HTTP 500** 발생 | **`NullPointerException`** |
| **TC-203** | **`chainNm` 세션 누락 시 인쇄 요청** | `{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL"}` | `chainNo="C001"`, **`chainNm` 없음** | **HTTP 500** 발생 | **`NullPointerException`** |

---

## 5. SQL 마이그레이션 호환성 체크리스트 (Warning 요소)

본 화면의 MyBatis Mapper [Hq_Vendor_00017_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/vendor/Hq_Vendor_00017_Sql.xml) 쿼리 내 오라클 전용 문법 검사항목입니다.

- [ ] **Oracle (+) 아우터 조인 식별 (L105)**: `A.VENDOR = B.VENDOR(+)` $\rightarrow$ ANSI 표준인 `LEFT OUTER JOIN` 구문으로 교체 필요.
- [ ] **오라클 ADD_MONTHS 날짜 연산 (L81)**: `ADD_MONTHS(TO_DATE(#{searchFromDate}, 'YYYYMMDD'), -1)` $\rightarrow$ PostgreSQL 표준인 `INTERVAL '-1 month'` 형식으로 리팩토링 필요.
- [ ] **Oracle DECODE 함수 잔존 (L23)**: `DECODE(A.SLIP_FG, '0', ...)` $\rightarrow$ `CASE WHEN` 구문으로 변환 필요.
- [ ] **Oracle NVL 함수 잔존 (L23)**: `NVL(B.PRE_TOT_AMT, 0)` $\rightarrow$ `COALESCE` 함수로 치환 필요.

---

## 6. CLI 자동화 테스트 스크립트 (PowerShell)

아래 스크립트를 통해 API 엔드포인트 동작과 NPE 예외 지점을 즉각 모니터링할 수 있습니다.

```powershell
# 1. 테스트용 세션 로그인 (shopadmin 계정 권한 획득)
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$baseUrl = "http://localhost:8080/backoffice/data/hq/vendor/hq_vendor_00017"
$headers = @{"Content-Type"="application/json"}

# Test 1: 정상 전체 조회 (TC-101)
print "--- Running TC-101 (Normal ALL Search) ---"
Invoke-RestMethod -Uri "$baseUrl/search" -Method POST -Headers $headers -WebSession $session `
  -Body '{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"ALL"}'

# Test 2: 정상 상품 필터 조회 (TC-102)
print "--- Running TC-102 (Normal Goods Code Filter) ---"
Invoke-RestMethod -Uri "$baseUrl/search" -Method POST -Headers $headers -WebSession $session `
  -Body '{"searchFromDate":"20240201","searchEndDate":"20240201","goodsCdArr":"T0000033"}'

# Test 3: goodsCdArr 파라미터 누락에 따른 NPE 유도 (TC-104)
print "--- Running TC-104 (NPE Trigger via missing goodsCdArr) ---"
try {
    Invoke-RestMethod -Uri "$baseUrl/search" -Method POST -Headers $headers -WebSession $session `
      -Body '{"searchFromDate":"20240201","searchEndDate":"20240201"}'
} catch {
    Write-Host "Caught expected HTTP 500 error due to NPE: " $_.Exception.Message -ForegroundColor Red
}
```
