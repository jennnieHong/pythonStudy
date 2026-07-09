# Hq_Vendor_00016 — 본사 의제매입 공제현황 단위 테스트케이스

> **화면**: [HQ] 매입발주 > 매입현황 > 의제매입 공제현황  
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00016`  
> **@Transactional**: 선언됨 (`rollbackFor = {RuntimeException.class, Exception.class}`) [Service L17] ✅  
> **요청 방식**: `/search` = JSON `@RequestBody` [Controller L54]  
> **@ServiceLog**: 선언됨 (menu="의제매입공제현황", name="의제매입공제 현황 조회", type=ServiceType.SELECT) [Controller L52] ✅  
> **DB 트리거 영향도**: 없음 (단순 조회 SELECT 전용 화면)  

---

## ⚠️ 서비스 핵심 이슈
* **Pure SELECT 화면**: 화면 및 데이터 흐름 전반에서 추가, 수정, 삭제 등의 CUD 트랜잭션이 전혀 발생하지 않으므로 데이터 변형 결함 및 트리거 연쇄 반응 위험이 발생하지 않습니다.
* **SQL 호환성 검증 완료**: 기존 Oracle 전용 아우터 조인 문법(`(+)`)은 개발 데이터베이스 엔진인 EDB PostgreSQL에서 자체 오라클 호환 구문으로 정상 지원하므로, 불필요한 변경을 지양하고 소스 코드 원형을 그대로 유지하여 정상 작동함을 검증했습니다. [SQL Mapper L87~90] ✅

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 비고 |
|---------|---------|------|
| `chainNo` | `C001` | 본사 C001 (shopadmin) 계정 로그인 세션 정보 |

---

## 엔드포인트 목록 (1개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | @ServiceLog | 관련 테이블 |
|---|---|---|---|---|---|---|---|
| 1 | `/search` | 의제매입공제 현황 조회 | `@RequestBody` | `List` (본사 의제매입 DTO) | SELECT | ✅ SELECT | OBSLPHTB (입고마스터)<br>OBSLPDTB (입고상세)<br>MGOODSTB (상품)<br>MNAMEMTB (코드명)<br>MVNDRMTB (거래처)<br>MMEMBSTB (매장) |

---

## 1. `/search` — 의제매입공제 현황 조회

**Mapper 호출**: `getList`  

| No | 세션 조건 | RequestBody (JSON) | 예상값 |
|----|----------|-------------------|-------|
| 1-1 | chainNo=`C001` | `{"searchFromDate":"20230301","searchEndDate":"20230331","msNo":"NC0007","taxFg":"0"}` | NC0007 매장의 의제매입 공제 내역 1건 반환 (수량 2, 공급가 10000) |
| 1-2 | chainNo=`C001` | `{"searchFromDate":"20230301","searchEndDate":"20230331","msNo":"","taxFg":"0"}` | 전체 매장 중 NC0007 매장 데이터 1건 동일하게 반환 |
| 1-3 | chainNo=`C001` | `{"searchFromDate":"20230301","searchEndDate":"20230331","msNo":"NC9999","taxFg":"0"}` | 데이터가 없는 매장이므로 빈 배열 `[]` 반환 |
| 1-4 | - | (RequestBody 누락) | 400 Bad Request (`@RequestBody` 누락 에러) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/vendor/hq_vendor_00016"
$h = @{"Content-Type"="application/json"}

# 1-1. 의제매입 현황 조회 (특정 매장 NC0007 & 의제구분)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20230301","searchEndDate":"20230331","msNo":"NC0007","taxFg":"0"}'

# 1-2. 의제매입 현황 조회 (전체 매장 & 의제구분)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20230301","searchEndDate":"20230331","msNo":"","taxFg":"0"}'

# 1-3. 데이터가 없는 매장 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20230301","searchEndDate":"20230331","msNo":"NC9999","taxFg":"0"}'
```

---

## 주요 검증 포인트

```
□ @Transactional rollbackFor={RuntimeException.class, Exception.class} 지정 확인 [Service L17] ✅
□ @ServiceLog(menu="의제매입공제현황", name="의제매입공제 현황 조회", type=ServiceType.SELECT) 적용 여부 [Controller L52] ✅
□ SQL Mapper 내 Oracle (+) 외부조인 문법 원형 유지 및 EDB 자체 호환 작동 검증 [SQL Mapper L87~90] ✅
□ Controller 및 Service 단의 파라미터 매핑 상태 검증 ✅
```
