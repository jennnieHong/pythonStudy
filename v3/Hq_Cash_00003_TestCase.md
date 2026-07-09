# Hq_Cash_00003 — 계정별 전점현황 (월간지출내역조회) 단위 테스트케이스

> **화면**: [HQ] 현금 > 계정별 전점현황  
> **URL Prefix**: `POST /backoffice/data/hq/cash/hq_cash_00003`  
> **@Transactional**: rollbackFor = {RuntimeException.class, Exception.class}  
> **요청 방식**: 전 엔드포인트 `@RequestBody`  
> **DB 트리거 영향도**: 없음 (단순 조회 전용 화면)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | searchList, selectAcntCd |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/searchList` | 기간별 매장 계정별 집계 조회 | `List<Map>` | SELECT | MACCIOTB, MMACNTTB, MMEMBSTB |
| 2 | `/selectAcntCd` | 특정 계정구분 하위 계정코드 콤보 조회 | `Map` (acntCdList) | SELECT | TMACNTTB |

---

## 1. `/searchList` — 기간별 전 가맹점 계정 집계 조회

**파라미터 방어**: `searchFromDate` 및 `searchEndDate` 유효성 검증 (빈 문자열 체크)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"searchFromDate":"20260629","searchEndDate":"20260629","acntFg":"0","acntCd":""}` | 해당 일자 체인 소속 가맹점 입금 집계 목록 리턴 |
| 1-2 | chainNo=`C001` | `{"searchFromDate":"","searchEndDate":"20260629","acntFg":"0"}` | JS 단에서 "시작일을 선택해 주세요" 얼럿 노출 후 중단 |

---

## 2. `/selectAcntCd` — 계정코드 콤보 목록 조회

**파라미터 방어**: `acntFg` 값에 따른 필터링 및 본사 계정코드 마스터 `TMACNTTB` 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"acntFg":"0"}` | 입금(`acntFg=0`) 콤보 아이템 목록 리턴 (`acntCdList`) |
| 2-2 | chainNo=`C001` | `{"acntFg":"1"}` | 출금(`acntFg=1`) 콤보 아이템 목록 리턴 (`acntCdList`) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/cash/hq_cash_00003"
$h = @{"Content-Type"="application/json"}

# 1-1. 기간별 전 가맹점 집계 조회
Invoke-RestMethod -Uri "$base/searchList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260629","searchEndDate":"20260629","acntFg":"0","acntCd":""}'

# 2-1. 계정 콤보 목록 조회
Invoke-RestMethod -Uri "$base/selectAcntCd" -Method POST -Headers $h -WebSession $session `
  -Body '{"acntFg":"0"}'
```

---

## 주요 검증 포인트

```
□ 조회 전용 스펙 — CUD 로직이 존재하지 않아 DB 트리거/프로시저 연쇄 및 형변환 예외 리스크 원천 배제됨 확인
□ 계정구분 필터링 — acntFg(0/1) 선택 변경에 따라 fnAcntCdSelect가 기동되어 하위 콤보박스 데이터 정상 갱신 확인
□ 매장명 매핑 — MACCIOTB의 MS_NO를 MMEMBSTB와 조인하여 가맹점명(MS_NM) 정확하게 매핑 검증
```
