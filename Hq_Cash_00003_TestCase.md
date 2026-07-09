# Hq_Cash_00003 — 계정별 전점현황 단위 테스트케이스

> **화면**: [HQ] 입출금관리 > 입출금관리 > 계정별 전점현황  
> **URL Prefix**: `POST /backoffice/data/hq/cash/hq_cash_00003`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **공통 전제**: 모든 요청은 HQ 권한 계정으로 **로그인된 세션** 필요
> **DB 트리거 영향도**: 본 화면은 조회 전용(SELECT)이므로 직접적인 CUD 유발은 없음. 단, 타 화면(`hq_cash_00001`, `hq_cash_00004` 등)에서 `TMACNTTB`에 가한 변경이 `TMACNT_T01` 트리거를 통해 `MMACNTTB`에 정상 동기화되어 있어야 계정 목록 및 입출금 실적이 연계 노출됨.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 테스트 체인 번호 (자동주입) |
| `ID` | `shopadmin` | 로그인 사용자 ID (자동주입) |

> 세션 없이 호출 시 → Spring Security가 **302 redirect** 처리

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | ServiceType | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/selectAcntCd` | 입출금 계정 콤보박스 조회 | SELECT | TMACNTTB |
| 2 | `/searchList` | 계정별 전점현황 목록 조회 | SELECT | MACCIOTB, MMACNTTB, MMEMBSTB |

---

## 1. `/selectAcntCd` — 입출금 계정 콤보박스 조회

**서비스 로직**: 세션 chainNo 및 파라미터 `acntFg` 수신 → `selectAcntCd()` (TMACNTTB 조회하여 `acntCdList` 반환)  
**RequestBody**: `{"acntFg": "0"}` (0=입금, 1=출금)

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 1-1 | 입금 계정 콤보 조회 | chainNo=`C001` | `{"acntFg":"0"}` | 입금 관련 계정 코드 목록 반환 ('전체' 포함) |
| 1-2 | 출금 계정 콤보 조회 | chainNo=`C001` | `{"acntFg":"1"}` | 출금 관련 계정 코드 목록 반환 ('전체' 포함) |
| 1-3 | 필수 파라미터 `acntFg` 누락 | chainNo=`C001` | `{}` | `acntFg = null`로 쿼리 실행, UNION 전반부('전체')만 1건 또는 빈 결과 반환 |
| 1-4 | 미존재 체인 조회 | chainNo=`C999` | `{"acntFg":"0"}` | '전체' 콤보 1건만 반환 (가맹점 등록 데이터 없음) |
| 1-5 | 미인증 접근 | 세션 없음 | `{"acntFg":"0"}` | 302 redirect |

---

## 2. `/searchList` — 계정별 전점현황 목록 조회

**서비스 로직**: 세션 chainNo, 파라미터 `searchFromDate`, `searchEndDate`, `acntFg`, `acntCd` 수신 → `selectList()` 실행  
**RequestBody**: `{"searchFromDate": "20260601", "searchEndDate": "20260611", "acntFg": "0", "acntCd": " "}`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 2-1 | 전체 계정 정상 조회 (acntCd 공백/전체) | chainNo=`C001` | `{"searchFromDate":"20260601","searchEndDate":"20260611","acntFg":"0","acntCd":" "}` | 지정된 기간 내 chainNo에 해당하는 매장별 입금 합계 금액 및 부가세 목록 반환 |
| 2-2 | 특정 계정 상세 필터 조회 | chainNo=`C001` | `{"searchFromDate":"20260601","searchEndDate":"20260611","acntFg":"0","acntCd":"10"}` | `acntCd='10'`인 입금 실적만 필터링되어 반환 |
| 2-3 | 실적이 없는 기간 조회 | chainNo=`C001` | `{"searchFromDate":"20000101","searchEndDate":"20000102","acntFg":"0","acntCd":" "}` | `[]` 빈 목록 반환 |
| 2-4 | 날짜 키 누락 (동적 쿼리) | chainNo=`C001` | `{"acntFg":"0","acntCd":" "}` | `searchFromDate` 및 `searchEndDate`가 `null`이 되어 SQL WHERE 조건절에서 생략되거나 오류 발생 여부 확인 |
| 2-5 | 미인증 접근 | 세션 없음 | `{"searchFromDate":"20260601", ...}` | 302 redirect |

---

## PowerShell 테스트 명령

```powershell
# 세션 로그인 (선행 필수 — shopadmin 계정)
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/cash/hq_cash_00003"
$h = @{"Content-Type"="application/json"}

# 1. 입금 계정 콤보박스 조회
Invoke-RestMethod -Uri "$base/selectAcntCd" -Method POST `
  -Body '{"acntFg":"0"}' -Headers $h -WebSession $session

# 2. 계정별 전점현황 전체 조회
Invoke-RestMethod -Uri "$base/searchList" -Method POST `
  -Body '{"searchFromDate":"20260601","searchEndDate":"20260611","acntFg":"0","acntCd":" "}' -Headers $h -WebSession $session
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `TMACNTTB` | chainNo=C001의 계정 코드 데이터 존재 (콤보박스 로딩용) |
| `MACCIOTB` | chainNo=C001에 속한 매장의 2026-06-01 ~ 2026-06-11 입출금 실적 데이터 존재 |
| `MMEMBSTB` | chainNo=C001에 속한 가맹점 마스터 데이터 존재 (MS_NO, MS_NM) |
| `MMACNTTB` | 가맹점 입출금 계정 관계 맵핑 데이터 존재 |

---

## 주요 검증 포인트

```
□ 조회기간 선택 필수 검증 — 시작일/종료일 누락 시 JavaScript단에서 경고(bootbox.alert) 노출 여부 확인
□ 계정구분 변경 시 이벤트 발생 — 계정구분이 입금/출금으로 바뀔 때 'selectAcntCd' 비동기 요청이 발생하여 계정명 콤보박스가 리프레시되는지 검증
□ 금액 필드 포맷터 작동 확인 — 금액(ACNT_AMT)과 부가세(VAT) 필드에 천단위 콤마(,) 포맷터(numberFormatter)가 올바르게 적용되어 표시되는지 검증
□ DataTable 합계 표시 검증 — 그리드 하단 Footer 영역에 금액 및 부가세의 컬럼 총합계(footerSumFormatter)가 정확하게 집계되는지 검증
```
