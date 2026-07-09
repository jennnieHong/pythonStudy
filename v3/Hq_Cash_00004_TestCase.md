# Hq_Cash_00004 — 월간지출계정관리 단위 테스트케이스

> **화면**: [HQ] 현금 > 월간지출계정관리  
> **URL Prefix**: `POST /backoffice/data/hq/cash/hq_cash_00004`  
> **@Transactional**: rollbackFor = {RuntimeException.class, Exception.class}  
> **요청 방식**: 전 엔드포인트 `@RequestBody`  
> **자바 트리거 연쇄**: 계정분류(TMACNCTB) 및 계정코드(TMACNTTB)의 CUD 발생 시 가맹점 전파(MMACNCTB/MMACNTTB) 및 로깅 연쇄(Depth 3) 수행됨

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | selectCodeList, selectDetailCodeList, codeSave, codeUpdate, codeDel, codeDtSave, codeDtUpdate, codeDtDel |

---

## 엔드포인트 목록 (8개)

| # | URL | 기능 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/selectCodeList` | 본사 기준 계정분류 목록 조회 | `List<Map>` | SELECT | TMACNCTB, TMACNTTB |
| 2 | `/codeSave` | 신규 계정분류 등록 | `int` | INSERT | TMACNCTB ➡️ MMACNCTB ➡️ SSACNCTB, MMSLOGTB |
| 3 | `/codeUpdate` | 계정분류 수정 | `int` | UPDATE | TMACNCTB ➡️ MMACNCTB ➡️ SSACNCTB, MMSLOGTB |
| 4 | `/codeDel` | 계정분류 삭제 | `int` | DELETE | TMACNCTB ➡️ MMACNCTB ➡️ SSACNCTB, MMSLOGTB |
| 5 | `/selectDetailCodeList` | 하위 계정코드 목록 조회 | `List<Map>` | SELECT | TMACNTTB |
| 6 | `/codeDtSave` | 신규 계정코드 등록 | `int` | INSERT | TMACNTTB ➡️ MMACNTTB ➡️ SSACNTTB, MMSLOGTB |
| 7 | `/codeDtUpdate` | 계정코드 수정 | `int` | UPDATE | TMACNTTB ➡️ MMACNTTB ➡️ SSACNTTB, MMSLOGTB |
| 8 | `/codeDtDel` | 계정코드 삭제 | `int` | DELETE | TMACNTTB ➡️ MMACNTTB ➡️ SSACNTTB, MMSLOGTB |

---

## 1. `/codeSave` — 신규 계정분류 등록

**파라미터 방어**: `acntFg`는 `2~9` 범위 이내의 문자 및 분류명 중복 검사 (`selectChkCode`)

| No | RequestBody | 예상값 | 자바 트리거 전파 결과 |
|----|-------------|-------|----------------------|
| 1-1 | `{"acntFg":"9","acntNm":"E2E Category"}` | `1` (성공) | TMACNCTB에 1건 삽입, 체인 C001 소속 매장에 MMACNCTB 복제(14건), SSACNCTB 전송로그 및 MMSLOGTB 감사 로그 생성 |
| 1-2 | `{"acntFg":"9","acntNm":"E2E Category"}` | `0` (중복 코드) | 중복 분류 검출되어 저장 실패 |
| 1-3 | `{"acntFg":"","acntNm":""}` | JS 예외 중단 | JS 단에서 "분류코드를 입력해주시기 바랍니다" 얼럿 출력 후 차단 |

---

## 2. `/codeDtSave` — 신규 계정코드 등록

**파라미터 방어**: `acntCd`는 `01~50` 범위 이내의 2자리 숫자형 문자, 코드 중복 검사 (`selectChkDtCode`)

| No | RequestBody | 예상값 | 자바 트리거 전파 결과 |
|----|-------------|-------|----------------------|
| 2-1 | `{"dtacntFg":"9","acntCd":"09","acntCdNm":"E2E Code","msDtUseFg":"Y"}` | `1` (성공) | TMACNTTB에 1건 삽입, 체인 C001 소속 매장에 MMACNTTB 복제(14건), SSACNTTB 전송로그 및 MMSLOGTB 감사 로그 생성 |
| 2-2 | `{"dtacntFg":"9","acntCd":"09","acntCdNm":"E2E Code","msDtUseFg":"Y"}` | `0` (중복 코드) | 중복 코드 검출되어 저장 실패 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/cash/hq_cash_00004"
$h = @{"Content-Type"="application/json"}

# 1. 분류 등록
Invoke-RestMethod -Uri "$base/codeSave" -Method POST -Headers $h -Body '{"acntFg":"9","acntNm":"AI분류"}' -WebSession $session

# 2. 코드 등록
Invoke-RestMethod -Uri "$base/codeDtSave" -Method POST -Headers $h -Body '{"dtacntFg":"9","acntCd":"09","acntCdNm":"AI코드","msDtUseFg":"Y"}' -WebSession $session

# 3. 코드 삭제
Invoke-RestMethod -Uri "$base/codeDtDel" -Method POST -Headers $h -Body '{"acntFg":"9","acntCd":"09"}' -WebSession $session

# 4. 분류 삭제
Invoke-RestMethod -Uri "$base/codeDel" -Method POST -Headers $h -Body '{"acntFg":"9"}' -WebSession $session
```

---

## 주요 검증 포인트

```
□ 자바 서비스 트리거 연쇄 작동 확인 — TMACNCTB/TMACNTTB CUD 수행 후 Tr_TMACNC_T01 / Tr_TMACNT_T01 서비스가 정상 실행되어 MMACNCTB/MMACNTTB 및 SSACNCTB/SSACNTTB, MMSLOGTB 테이블에 정상 도달 및 누적 확인 (Depth 3 만족)
□ 하위 데이터 검출 잠금 — 분류삭제 시 하위 코드가 잔존할 경우 deleteChk를 통해 삭제 요청 차단 확인
□ 형변환 무결성 — 전 필드가 문자열 바인딩 타입 구조로 구성되어 캐스팅 예외 안전함 확인
```
