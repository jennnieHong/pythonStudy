# St_Appr_00001 — 매장 당일 승인현황 단위 테스트케이스

> **화면**: [STORE] 승인관리 > 승인조회 > 당일 승인현황  
> **URL Prefix**: `POST /backoffice/data/st/approval/st_appr_00001`  
> **@Transactional**: 선언됨 (`rollbackFor = {RuntimeException.class, Exception.class}`) [Service L28] ✅  
> **요청 방식**: `/search` = JSON `@RequestBody` [Controller L56]  
> **@ServiceLog**: 선언됨 (menu = "당일 승인현황", name = "승인현황 조회", type = ServiceType.SELECT) [Controller L54] ✅  
> **DB 트리거 영향도**: 없음 (단순 조회 SELECT 전용 화면)  

---

## ⚠️ 서비스 핵심 이슈
* **Pure SELECT 화면**: 추가, 수정, 삭제 등의 CUD 트랜잭션이 전혀 발생하지 않으므로 데이터 변형 결함 및 트리거 연쇄 반응 위험이 존재하지 않는 조회 전용 화면입니다.
* **SQL 호환성 마이그레이션 권고**: SQL Mapper 내에서 Oracle 날짜 변환 함수 `TO_DATE(NVL(TRIM(A.APPR_DATE),'19900101'),'YYYYMMDD')`를 사용하고 있으며, PostgreSQL 환경에서 빈 문자열(`''`) 전달 시 날짜 형변환 예외가 발생할 수 있습니다. `TO_DATE(COALESCE(NULLIF(TRIM(A.APPR_DATE), ''), '19900101'), 'YYYYMMDD')` 구문으로 리팩토링할 것을 강력히 권장합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 비고 |
|---------|---------|------|
| `chainNo` | `C001` | 매장 소속 체인 C001 |
| `msNo` | `NC0003` | 로그인 매장코드 NC0003 (I000034a) 계정 로그인 세션 정보 |

---

## 엔드포인트 목록 (1개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | @ServiceLog | 관련 테이블 |
|---|---|---|---|---|---|---|---|
| 1 | `/search` | 매장 당일 신용카드 승인 목록 조회 | `@RequestBody` | `List` (승인 DTO) | SELECT | ✅ SELECT | STRNCDTB (신용카드상세)<br>STRNCTTB (신용카드간이)<br>MMEMBSTB (매장마스터)<br>MCARDMTB (카드사마스터) |

---

## 1. `/search` — 매장 당일 신용카드 승인 목록 조회

**Mapper 호출**: `selectCardApprList`  

| No | 세션 조건 | RequestBody (JSON) | 예상값 |
|----|----------|-------------------|-------|
| 1-1 | chainNo=`C001`<br>msNo=`NC0003` | `{"searchDate":"20260602","selectPosNo":"","apprFg":"","payFg":"","apprNo":""}` | 로그인 세션(`NC0003`)의 2026-06-02 카드 승인/취소 거래 내역 5건 반환 (총 5행) |
| 1-2 | chainNo=`C001`<br>msNo=`NC0003` | `{"searchDate":"20260602","selectPosNo":"01","apprFg":"0","payFg":"0","apprNo":""}` | `NC0003` 매장의 01번 POS, 정상 승인, 신용카드(PAY_FG=0) 내역 조회 |
| 1-3 | chainNo=`C001`<br>msNo=`NC0003` | `{"searchDate":"20260602","selectPosNo":"","apprFg":"","payFg":"","apprNo":"9999"}` | 존재하지 않는 승인번호 조회 시 빈 배열 `[]` 반환 |
| 1-4 | - | (RequestBody 누락) | 400 Bad Request (`@RequestBody` 누락 에러) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=I000034a&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/approval/st_appr_00001"
$h = @{"Content-Type"="application/json"}

# 1-1. 매장 당일 승인현황 목록 조회 (2026-06-02, 세션 매장 NC0003)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchDate":"20260602","selectPosNo":"","apprFg":"","payFg":"","apprNo":""}'

# 1-2. 필터링 조회 (POS 01, 정상 승인)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchDate":"20260602","selectPosNo":"01","apprFg":"0","payFg":"0","apprNo":""}'

# 1-3. 데이터 없는 경우 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchDate":"20260602","selectPosNo":"","apprFg":"","payFg":"","apprNo":"9999"}'
```

---

## 주요 검증 포인트

```
□ @Transactional rollbackFor={RuntimeException.class, Exception.class} 지정 확인 [Service L28] ✅
□ @ServiceLog(menu="당일 승인현황", name="승인현황 조회", type=ServiceType.SELECT) 적용 여부 [Controller L54] ✅
□ Mapper 인터페이스와 MyBatis SQL XML 연동 상태 검증 [Mapper L44] ✅
□ Controller 및 Service 단의 파라미터 매핑 상태 검증 (매장 정보 세션 자동 주입 확인) ✅
□ PostgreSQL 날짜 형변환 비호환 리스크 존재 파악 및 리팩토링 권고 ✅
```
