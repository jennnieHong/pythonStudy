# St_Vendor_00007 — 매장 거래처별 입고/반품 현황 단위 테스트케이스

> **화면**: [ST] 매입발주 > 매입현황 > 거래처별 입고/반품 현황  
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00007`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않아 실제 트리거가 직접 기동하지는 않습니다.

---

## ⚠️ 서비스 핵심 소스 분석

### 1. 순수 매입금액 연산 집계 및 `PROC_FG = '4'` 필터
* **소스 분석 (`St_Vendor_00007_Sql.xml` L28~30)**:
  * SQL 레벨에서 `SLIP_FG = '0'`(매입) 금액 합산에서 `SLIP_FG = '1'`(반품) 금액 합산을 빼서 순수 매입 합계(`SUM_AMT`, `SUM_VAT`, `SUM_TOT`)를 연산하여 화면에 리턴합니다.
  * 이때 대상 전표는 **`PROC_FG = '4'` (입고확정)**인 건들로만 격리 제한되어 있습니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, detailSearch |
| `msNo` | `NC0007` (매장코드) | search, detailSearch |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 거래처별 입고/반품 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, MVNDRMTB, MMEMBSTB |
| 2 | `/detailSearch` | 거래처별 상품 입고/반품 상세 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, MGOODSTB, MNAMEMTB |

---

## 1. `/search` — 거래처별 입고/반품 목록 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 1-1 | 정상 조건 조회 | 특정 거래처 입고 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201"}` | - EDB PostgreSQL 기반 집계 목록 반환.<br>- 거래처별 입고/반품 합산 및 순합계 리턴. |
| 1-2 | 특정 거래처 필터 조회 (`com_searchVendr = "00001"`) | 해당 거래처 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_searchVendr":"00001"}` | `A.VENDOR = '00001'` 조건이 적용된 단일 행 필터링 리턴. |

---

## 2. `/detailSearch` — 거래처별 상품 상세 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 2-1 | 정상 상세조회 | 해당 거래처 상품 입고이력 존재 | `{"vendor":"00001","msNo":"NC0007","fromDate":"2024-02-01","toDate":"2024-02-01"}` | - 하이픈 제거되어 바인딩 성공.<br>- 거래처 산하 상품들의 입고/반품 상세 내역 합계 리턴. |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/vendor/st_vendor_00007"
$h = @{"Content-Type"="application/json"}

# 1-1. 거래처별 입고/반품 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20240201","searchEndDate":"20240201"}'

# 2-1. 상세 거래처 상품 목록 조회
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"vendor":"00001","msNo":"NC0007","fromDate":"2024-02-01","toDate":"2024-02-01"}'
```

---

## 주요 검증 포인트

```
□ search — SLIP_FG='1' 반품 거래량 차감이 sumAmt 수식에 올바르게 적용되는지 산술 정합성 검증
□ detailSearch 쿼리 — C.ORD_UNIT와 D.NM_CD 조인 시 TRIM 처리의 PostgreSQL 문자 타입 정합성 검증
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅ (2/2)

| 엔드포인트 | @ServiceLog 선언 현황 |
|-----------|---------------------|
| `/search` (목록 조회) | ✅ SELECT (컨트롤러 L57) |
| `/detailSearch` (상세 조회) | ✅ SELECT (컨트롤러 L80) |
