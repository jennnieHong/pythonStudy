# Hq_Sales_00005 — 본사 대비기간매출 단위 테스트케이스

> **화면**: [HQ] 매출분석 > 일/월/시간 > 대비기간매출  
> **URL Prefix**: `POST /backoffice/data/hq/sales/hq_sales_00005`  
> **요청 방식**: `/search` = JSON `@RequestBody` [Controller L59]  
> **@ServiceLog**: 선언됨 (menu = "대비기간매출", name = "대비기간 매출 조회", type = ServiceType.SELECT) [Controller L57] ✅  
> **DB 트리거 영향도**: 없음 (단순 조회 SELECT 전용 화면)  

---

## ⚠️ 서비스 핵심 이슈
* **Pure SELECT 화면**: 추가, 수정, 삭제 등의 CUD 트랜잭션이 전혀 발생하지 않으므로 데이터 변형 결함 및 트리거 연쇄 반응 위험이 존재하지 않는 조회 전용 화면입니다.
* **SQL 나눗셈 분모 0 에러 리스크**: 
  - SQL Mapper 내에서 두 기간의 성장률을 계산할 때 `A.SALE_AMT/B.C_SALE_AMT` 공식을 사용합니다.
  - 만약 대비기간의 순매출액(`B.C_SALE_AMT`)이 0 또는 NULL인 경우, EDB Postgres 환경에서 `division by zero` 예외를 발생시키며 서버 에러가 발생할 가능성이 존재합니다.
  - 안전을 위해 `COALESCE(NULLIF(B.C_SALE_AMT, 0), 1)` 또는 `DECODE`/`CASE`를 활용하여 분모가 0이 되는 것을 방지하는 리팩토링이 필요합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 비고 |
|---------|---------|------|
| `chainNo` | `C001` | 본사 계정 로그인 세션 정보 |

---

## 엔드포인트 목록 (1개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | @ServiceLog | 관련 테이블 |
|---|---|---|---|---|---|---|---|
| 1 | `/search` | 대비기간 매출 데이터 조회 | `@RequestBody` | `List<Hq_Sales_00005_ContrastSaleListDto>` | SELECT | ✅ SELECT | SDAILYTB (매출 일집계)<br>MMEMBSTB (매장마스터) |

---

## 1. `/search` — 대비기간 매출 데이터 조회

**Mapper 호출**: `getContrastSaleList`  

| No | 세션 조건 | RequestBody (JSON) | 예상값 |
|----|----------|-------------------|-------|
| 1-1 | chainNo=`C001` | `{"fromDate":"20260601","toDate":"20260630","confromDate":"20260501","contoDate":"20260531","msNo":"","shopType":""}` | C001 소속 전 가맹점의 6월 매출과 5월 대비 매출 비교 데이터 정상 로드 |
| 1-2 | chainNo=`C001` | `{"fromDate":"20260601","toDate":"20260630","confromDate":"20260501","contoDate":"20260531","msNo":"NC0007","shopType":""}` | NC0007 매장의 대비기간 매출 비교 데이터 필터링 조회 성공 |
| 1-3 | chainNo=`C001` | `{"fromDate":"20260630","toDate":"20260601","confromDate":"20260501","contoDate":"20260531","msNo":"","shopType":""}` | 날짜 선후 관계 검증 (화면 스크립트 단에서 팝업으로 조회 차단) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=H1216020&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/sales/hq_sales_00005"
$h = @{"Content-Type"="application/json"}

# 1-1. 전점 대비기간 매출 조회 (2026년 6월 vs 5월)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"fromDate":"20260601","toDate":"20260630","confromDate":"20260501","contoDate":"20260531","msNo":"","shopType":""}'

# 1-2. NC0007 매장 필터링 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"fromDate":"20260601","toDate":"20260630","confromDate":"20260501","contoDate":"20260531","msNo":"NC0007","shopType":""}'
```

---

## 주요 검증 포인트

```
□ @ServiceLog(menu="대비기간매출", name="대비기간 매출 조회", type=ServiceType.SELECT) 적용 여부 [Controller L57] ✅
□ Mapper 인터페이스와 MyBatis SQL XML 연동 상태 검증 [Mapper L29] ✅
□ PostgreSQL division_by_zero 에러 가능성 파악 및 방어 코드 수립 권고 ✅
```
