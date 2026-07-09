# St_Vendor_00012 — 매장 구매품의발주 현황 단위 테스트케이스

> **화면**: [Store] 매입발주 > 매입현황 > 구매품의발주 현황  
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00012`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않습니다.

---

## ⚠️ 서비스 핵심 소스 분석 및 잠재적 버그

### 1. 세션 정보 (`chainNo`, `msNo`) 참조 시 NullPointerException 취약성 (★★)
* **소스 분석 (`St_Vendor_00012_Controller.java` L63, L64, L88, L89)**:
  * 매장 로그인 세션 정보에서 `chainNo`와 `msNo` 값을 가져와 `.toString()`을 호출합니다.
  * **결과**: 만약 세션이 존재하지 않거나 해당 파라미터가 누락된 사용자가 API를 직접 실행하는 경우 즉시 **`NullPointerException` (500 에러)**이 발생합니다.

### 2. EDB PostgreSQL 마이그레이션 호환성 및 외부조인 (+) 문법 (★★★)
* **소스 분석 (`St_Vendor_00012_Sql.xml` L27, L29, L30, L31, L76, L77, L78, L79, L87)**:
  * SQL XML 내 쿼리에서 Oracle 전용 아우터 조인 문법 `(+)`을 다수 사용하고 있습니다:
    * `HD.PURCH_REQ_NO = OH.PURCH_REQ_NO(+)`
    * `HD.MS_NO = OH.MS_NO(+)`
    * `DT.SLIP_NO = OH.SLIP_NO(+)`
    * `DT.SLIP_NO = OD.SLIP_NO(+)`
  * EDB PostgreSQL 환경에서는 ANSI SQL 문법인 `LEFT OUTER JOIN`으로 변경되어 호출되어야 호환성 오류가 없습니다. 소스 파일상에서는 `(+)` 문법이 유지되고 있으나 실제 애플리케이션 빌드/마이그레이션 레이어에서 정상적으로 변환 처리되는지 최종 검증해야 합니다.

### 3. Oracle 전용 함수 (`NVL`) 사용 (★★)
* **소스 분석 (`St_Vendor_00012_Sql.xml` L15, L62, L63, L64, L65)**:
  * `NVL(SUBSTR(HD.PURCH_REQ_CONF_DATE, 0, 4) || ...)` 및 `NVL(SUM(OD.ORDER_QTY), 0)` 등의 Oracle 함수를 사용하고 있습니다.
  * PostgreSQL 환경에서 정상 기동을 위해 `COALESCE` 또는 해당 데이터베이스 벤더 호환 레이어가 제대로 작동하는지 확인이 필요합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` (본부_SHOP) | `/search`, `/detailSearch` |
| `msNo` | `NC0003` (고양 Shop) 또는 `NC0007` (CAFE) | `/search`, `/detailSearch` |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 구매품의발주 현황 목록 조회 | `@RequestBody` | `List` | SELECT | OBREQHTB, OBSLPHTB, MMEMBSTB, MUSERSTB |
| 2 | `/detailSearch` | 구매품의발주 현황 상세 목록 조회 | `@RequestBody` | `List` | SELECT | OBREQHTB, OBREQDTB, OBSLPHTB, OBSLPDTB, MMEMBSTB, MVNDRMTB, MGOODSTB, MNAMEMTB |

---

## 1. `/search` — 구매품의발주 현황 목록 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 1-1 | 정상 조건 조회 (전체) | 해당 매장에 품의 건 존재 | `{"fromDate":"20260604","toDate":"20260604"}` | - EDB PostgreSQL 기반 집계 목록 반환.<br>- 해당 매장(세션의 `msNo`)의 구매요청번호 및 발주일자, 금액이 표시됨. |
| 1-2 | 구분 필터 조회 (`procFg = "0"`) | 구매요청등록 상태 건 존재 | `{"fromDate":"20260604","toDate":"20260604","procFg":"0"}` | `HD.PROC_FG = '0'` 조건이 적용되어 '구매요청등록' 상태의 건들만 조회. |

---

## 2. `/detailSearch` — 구매품의발주 현황 상세 목록 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 2-1 | 정상 상세조회 | 해당 품의번호에 속한 상세 품목 내역 존재 | `{"purchReqNo":"PR202606040001"}` | - 품목코드, 품목명, 거래처명, 구매/발주 수량 및 금액 목록 반환. |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopbrand&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/vendor/st_vendor_00012"
$h = @{"Content-Type"="application/json"}

# 1-1. 구매품의발주 현황 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"fromDate":"20260604","toDate":"20260604"}'

# 2-1. 상세 정보 조회
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"purchReqNo":"PR202606040001"}'
```

---

## 주요 검증 포인트

```
□ search — 로그인 세션의 msNo가 쿼리에 바인딩되어 타 매장의 품의 내역 유출이 차단되는지 확인
□ detailSearch — 수량 및 금액 계산 시 곱셈 연산(DT.SUPPLY_QTY * DT.PURCH_UNIT_PRC) 및 NVL 처리 정상 작동 여부
□ SQL Mapper 쿼리 — Oracle (+) 아우터 조인 구문의 PostgreSQL LEFT JOIN 변환 정합성 검증
```

---

## ✅ @ServiceLog 선언 현황 — 전체 정상 ✅ (2/2)

| 엔드포인트 | @ServiceLog 선언 현황 |
|-----------|---------------------|
| `/search` (목록 조회) | ✅ SELECT (컨트롤러 L55) |
| `/detailSearch` (상세 조회) | ✅ SELECT (컨트롤러 L81) |
