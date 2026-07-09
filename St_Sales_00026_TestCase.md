# St_Sales_00026 — 매장 당일매출 단위 테스트케이스

> **화면**: [STORE] 매장 매출분석 > 일/월/시간 > 당일매출  
> **URL Prefix**: `POST /backoffice/data/st/sales/st_sales_00026`  
> **@Transactional**: 선언됨 (`rollbackFor = {RuntimeException.class, Exception.class}`) [Service L28] (내부 위임 구조로 트랜잭션 기본 롤백 포함) ✅  
> **요청 방식**: `/searchSaleList` = JSON `@RequestBody` [Controller L64]  
> **@ServiceLog**: 선언됨 (menu = "당일매출", name = "당일매출 조회", type = ServiceType.SELECT) [Controller L59] ✅  
> **DB 트리거 영향도**: 없음 (단순 조회 SELECT 전용 화면)  

---

## ⚠️ 서비스 핵심 이슈
* **Pure SELECT 화면**: 추가, 수정, 삭제 등의 CUD 트랜잭션이 전혀 발생하지 않으므로 데이터 변형 결함 및 트리거 연쇄 반응 위험이 존재하지 않는 조회 전용 화면입니다.
* **SQL 호환성 마이그레이션 권고**: SQL Mapper 내에서 Oracle 날짜시간 변환 함수 `TO_DATE(B.SALE_DTIME,'YYYYMMDDHH24MISS')` 및 `DECODE`/`NVL` 함수를 사용하고 있습니다. PostgreSQL/EPAS 환경에서의 예외 발생 방지 및 표준 호환을 위해 `TO_DATE(NULLIF(TRIM(B.SALE_DTIME), ''), 'YYYYMMDDHH24MISS')` 및 `CASE WHEN`, `COALESCE` 로 리팩토링할 것을 권장합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 비고 |
|---------|---------|------|
| `chainNo` | `C001` | 매장 소속 체인 C001 |
| `msNo` | `NC0007` | 로그인 매장코드 NC0007 (H1240961C) 계정 로그인 세션 정보 |

---

## 엔드포인트 목록 (1개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | @ServiceLog | 관련 테이블 |
|---|---|---|---|---|---|---|---|
| 1 | `/searchSaleList` | 매장 당일 매출 합계 및 목록 조회 | `@RequestBody` | `Map` (합계 리스트 + 목록 리스트) | SELECT | ✅ SELECT | STRNDTTB (매출상세)<br>STRNHDTB (매출헤더)<br>MGOODSTB (상품마스터)<br>MMEMBSTB (매장마스터)<br>STRNCHTB (현금상세) |

---

## 1. `/searchSaleList` — 매장 당일 매출 합계 및 목록 조회

**Mapper 호출**: `searchDaySaleTotList`, `searchDaySaleList`  

| No | 세션 조건 | RequestBody (JSON) | 예상값 |
|----|----------|-------------------|-------|
| 1-1 | chainNo=`C001`<br>msNo=`NC0003` | `{"searchFromDate":"20260602","searchEndDate":"20260602","posNo":""}` | 로그인 세션(`NC0003`)의 2026-06-02 정상 매출 1건, 반품 매출 3건에 대한 합계 요약(3행) 및 상세 목록(4행)을 담은 맵 리턴 |
| 1-2 | chainNo=`C001`<br>msNo=`NC0003` | `{"searchFromDate":"20260602","searchEndDate":"20260602","posNo":"01"}` | `NC0003` 매장의 01번 POS 매출 정보 필터링 조회 성공 |
| 1-3 | chainNo=`C001`<br>msNo=`NC0003` | `{"searchFromDate":"20260602","searchEndDate":"20260602","posNo":"99"}` | 존재하지 않는 POS 번호 조회 시 빈 리스트 `{"daySaleTotList":[],"daySaleList":[]}` 반환 |
| 1-4 | - | (RequestBody 누락) | 400 Bad Request (`@RequestBody` 누락 에러) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=H1240961C&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/sales/st_sales_00026"
$h = @{"Content-Type"="application/json"}

# 1-1. 매장 당일매출 현황 조회 (2026-06-02, 세션 매장 NC0003)
Invoke-RestMethod -Uri "$base/searchSaleList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260602","searchEndDate":"20260602","posNo":""}'

# 1-2. 필터링 조회 (POS 01)
Invoke-RestMethod -Uri "$base/searchSaleList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260602","searchEndDate":"20260602","posNo":"01"}'

# 1-3. 데이터 없는 경우 조회
Invoke-RestMethod -Uri "$base/searchSaleList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260602","searchEndDate":"20260602","posNo":"99"}'
```

---

## 주요 검증 포인트

```
□ @Transactional(rollbackFor={Exception.class}) 지정 확인 (기본 설정 상속) [Service L28] ✅
□ @ServiceLog(menu="당일매출", name="당일매출 조회", type=ServiceType.SELECT) 적용 여부 [Controller L59] ✅
□ Mapper 인터페이스와 MyBatis SQL XML 연동 상태 검증 [Mapper L73, L74] ✅
□ Controller 및 Service 단의 파라미터 매핑 상태 검증 (매장 정보 세션 자동 주입 확인) ✅
□ PostgreSQL 날짜시간 형변환 비호환 리스크 존재 파악 및 리팩토링 권고 ✅
```
