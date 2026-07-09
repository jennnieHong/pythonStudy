# St_Vendor_00014 — 매장 의제매입 공제현황 단위 테스트케이스

> **화면**: [Store] 매입발주 > 매입현황 > 의제매입 공제현황  
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00014`  
> **@Transactional**: 선언됨 (`rollbackFor = {RuntimeException.class, Exception.class}`) [Service L28] ✅  
> **요청 방식**: `/search` = JSON `@RequestBody` [Controller L56]  
> **@ServiceLog**: 선언됨 (menu="의제매입공제현황", name="의제매입공제현황 내역 조회", type=ServiceType.SELECT) [Controller L54] ✅  
> **DB 트리거 영향도**: 없음 (단순 조회 SELECT 전용 화면)  

---

## ⚠️ 서비스 핵심 이슈
* **Pure SELECT 화면**: 화면 및 데이터 흐름 전반에서 추가, 수정, 삭제 등의 CUD 트랜잭션이 전혀 발생하지 않으므로 데이터 변형 결함 및 트리거 연쇄 반응 위험이 발생하지 않습니다.
* **AsIs 기능 동일성 확인 필요 (운영 대조 필요)**
  * **반품 합계금액 연산**: `St_Vendor_00014_Sql.xml` L21 내 반품 합계(`PURCH_SUM`) 연산 시 괄호 누락으로 인해 플러스 양수로 처리되는 동작이 기존 AsIs 환경과 동일한 의도인지 대조 확인 필요.
  * **수량 및 금액 포맷팅**: `st_vendor_00014_bt.js` L214 내 `parseInt(value) > 0` 정수형 절사 조건으로 인해, 반품(마이너스) 수량 및 금액 또는 1 미만의 실수(소수점 수량)가 `0`으로 표출되는 동작이 기존 AsIs 기획과 동일한 스펙인지 확인 필요.
* **SQL 호환성 검증**: 기존 Oracle 전용 아우터 조인 문법(`(+)`)은 개발 데이터베이스 엔진인 EDB PostgreSQL에서 자체 오라클 호환 구문으로 정상 지원하므로, 불필요한 변경을 지양하고 소스 코드 원형을 그대로 유지하여 정상 작동함을 검증했습니다. [SQL Mapper L82~83] ✅

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 비고 |
|---------|---------|------|
| `chainNo` | `C001` | 본사 C001 계정 로그인 정보 |
| `msNo` | `NC0018` | 가맹점 AI Registration Test (I000311b) 계정 로그인 세션 정보 |

---

## 엔드포인트 목록 (1개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | @ServiceLog | 관련 테이블 |
|---|---|---|---|---|---|---|---|
| 1 | `/search` | 의제매입공제현황 내역 조회 | `@RequestBody` | `List` (매장 의제매입 DTO) | SELECT | ✅ SELECT | OBSLPHTB (입고마스터)<br>OBSLPDTB (입고상세)<br>MGOODSTB (상품)<br>MNAMEMTB (코드명)<br>MVNDRMTB (거래처) |

---

## 1. `/search` — 의제매입공제현황 내역 조회

**Mapper 호출**: `getList`  

| No | 세션 조건 | RequestBody (JSON) | 예상값 |
|----|----------|-------------------|-------|
| 1-1 | chainNo=`C001`, msNo=`NC0018` | `{"searchFromDate":"20260601","searchEndDate":"20260630","taxFg":"1"}` | NC0018 매장의 과세 매입 내역 2건 반환 (수량 -1, 공급가 -31818 및 수량 -2, 공급가 -7455) |
| 1-2 | chainNo=`C001`, msNo=`NC0018` | `{"searchFromDate":"20260601","searchEndDate":"20260630","taxFg":"0"}` | 의제매입 데이터가 없는 매장이므로 빈 배열 `[]` 반환 |
| 1-3 | - | (RequestBody 누락) | 400 Bad Request (`@RequestBody` 누락 에러) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=I000311b&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/vendor/st_vendor_00014"
$h = @{"Content-Type"="application/json"}

# 1-1. 의제매입현황 조회 (가맹점 NC0018 & 과세구분)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260601","searchEndDate":"20260630","taxFg":"1"}'

# 1-2. 의제매입현황 조회 (가맹점 NC0018 & 의제구분)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260601","searchEndDate":"20260630","taxFg":"0"}'
```

---

## 주요 검증 포인트

```
□ @Transactional rollbackFor={RuntimeException.class, Exception.class} 지정 확인 [Service L28] ✅
□ @ServiceLog(menu="의제매입공제현황", name="의제매입공제현황 내역 조회", type=ServiceType.SELECT) 적용 여부 [Controller L54] ✅
□ SQL Mapper 내 Oracle (+) 외부조인 문법 원형 유지 및 EDB 자체 호환 작동 검증 [SQL Mapper L82~83] ✅
□ Controller 및 Service 단의 파라미터 매핑 상태 검증  ✅
□ 반품 전표 처리 시 SQL 연산 및 괄호 처리 현상 AsIs 대조 검증 대상 표시 ✅
□ st_vendor_00014_bt.js 포맷터 내 음수/소수점 절사 현상 AsIs 동일성 확인 대상 표시 ✅
```
