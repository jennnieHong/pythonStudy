# Hq_Vendor_00011 — 본사 거래처별 입고/반품 현황 단위 테스트케이스

> **화면**: [HQ] 매입발주 > 매입현황 > 거래처별 입고/반품 현황  
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00011`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않습니다.

---

## ⚠️ 서비스 핵심 소스 분석

### 1. 본사 체인 권한 격리 및 매장 필터링
* **소스 분석 (`Hq_Vendor_00011_Sql.xml` L38~40)**:
  * 본사 하위 매장의 거래처 입고 실적을 합계 집계하기 위해 `B.CHAIN_NO = #{chainNo}` 조인 구조를 취하고 있습니다.
  * 매장 필터 `com_selectMsNo` 파라미터 유무에 따라 특정 매장의 거래처 데이터만 동적으로 조회할 수 있습니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, detailSearch |

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
| 1-1 | 정상 조건 조회 | 본사 하위 매장에 입고 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201"}` | - EDB PostgreSQL 기반 집계 목록 반환.<br>- 본사 산하 전 매장의 거래처 합산 금액 리턴. |
| 1-2 | 특정 매장 필터 조회 (`com_selectMsNo = "NC0007"`) | NC0007 매장 전표 존재 | `{"searchFromDate":"20240201","searchEndDate":"20240201","com_selectMsNo":"NC0007"}` | `A.MS_NO = 'NC0007'` 조건만 조인되어 조회됨. |

---

## 2. `/detailSearch` — 거래처별 상품 상세 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 2-1 | 정상 상세조회 | 해당 매장 거래처 입고이력 존재 | `{"vendor":"00001","msNo":"NC0007","fromDate":"2024-02-01","toDate":"2024-02-01"}` | - 날짜 하이픈 제거되어 바인딩 성공.<br>- 매장 거래처별 상품 상세 목록 리턴. |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/vendor/hq_vendor_00011"
$h = @{"Content-Type"="application/json"}

# 1-1. 본사 거래처별 입고/반품 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20240201","searchEndDate":"20240201"}'

# 2-1. 상세 거래처 상품 목록 조회
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"vendor":"00001","msNo":"NC0007","fromDate":"2024-02-01","toDate":"2024-02-01"}'
```

---

## 주요 검증 포인트

```
□ search — com_selectMsNo 매장 조건이 걸릴 때 MVNDRMTB 테이블 조인 기준 msNo가 정상 작동하는지 확인
□ detailSearch 쿼리 — A.VENDOR 파라미터 바인딩과 A.PROC_FG='4' 조건의 DB 인덱스 스캔 적합성 검증
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅ (2/2)

| 엔드포인트 | @ServiceLog 선언 현황 |
|-----------|---------------------|
| `/search` (목록 조회) | ✅ SELECT (컨트롤러 L57) |
| `/detailSearch` (상세 조회) | ✅ SELECT (컨트롤러 L79) |
