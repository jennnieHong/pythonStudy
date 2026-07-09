# Hq_Emp_00002 — 비밀번호 관리 단위 테스트케이스

> **화면**: [HQ] 인사관리 > 비밀번호 관리 (내 정보 / PW 변경)  
> **URL Prefix**: `POST /backoffice/data/hq/emp/hq_emp_00002`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}
> **DB 트리거 영향도**: MUSERSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `msNo` | `NC0001` | 로그인 사용자 매장번호 (user_ms_no) |
| `ID` | `7249525SHOP` | 로그인 사용자 ID |
| `PASSWORD` | BCrypt 해시값 | 현재 비밀번호 BCrypt (updatePW 인증용) |

---

## 엔드포인트 목록 (3개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/userInfo` | 로그인 유저 정보 조회 | SELECT | MMEMBSTB<br>MUSERSTB  |
| 2 | `/updatePW` | 비밀번호 변경 (유효성+BCrypt 인증) | UPDATE | MUSERSTB<br>UPDATEUSERSTB  |
|3|`/getUserSecure`|보안 정책 조회|SELECT| 공통 모듈/동적 쿼리 (추적 불가) |

---

## 1. `/userInfo` — 로그인 유저 정보 조회

**서비스 로직**: 세션 `msNo` + `ID` → `getUserInfo()` → `CommonModule_UserListDto` 반환  
**RequestBody 없음** (파라미터 전부 세션에서 주입)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | msNo=`NC0001`, ID=`7249525SHOP` | `{}` | 로그인 사용자 상세 정보 DTO 반환 |
| 1-2 | msNo=`NC0001`, ID=`7249525SHOP` (DB에 존재) | `{}` | userId, userNm, userFg, email 등 포함 |
| 1-3 | 세션 없음 | - | 302 redirect |
| 1-4 | userInfo 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |
| 1-5 | body 없이 호출 | Content-Type 미설정, body 없음 | 정상 200 응답 ★ (body 무관) |
| 1-6 | JSON body 전송 | `{"anyKey":"anyVal"}` | 무시되고 정상 응답 ★ |

---

## 2. `/updatePW` — 비밀번호 변경

**서비스 이중 분기**:

```
1단계: getPasswordChk(upassWd) — 새 비밀번호 유효성
  ├── 0 → 정상 (2단계 진행)
  ├── 1 → 길이 오류          → returnMap.put("chkFg", 1)
  ├── 2 → 특수문자 오류      → returnMap.put("chkFg", 2)
  ├── 3 → 숫자 길이 오류     → returnMap.put("chkFg", 3)
  └── 4 → 영문 길이 오류     → returnMap.put("chkFg", 4)

2단계 (chk==0): BCrypt 현재 PW 인증
  ├── bCryptEncoder.matches(userPW, 세션PASSWORD) 일치
  │   → encode(upassWd) → updateUsersTb() → returnMap = {}
  └── 불일치 → returnMap.put("chkFg", 5)
```

**파라미터**:
- `userPW`: 현재 비밀번호 (BCrypt 검증용)
- `upassWd`: 새 비밀번호 (유효성 + 저장)

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 2-1 | ID=`7249525SHOP`, PW=BCrypt(`0000`) | `userPW=0000&upassWd=NewPass1!` | `{}` (변경 성공, returnMap 비어있음) |
| 2-2 | **현재PW 불일치** | `userPW=wrongPW&upassWd=NewPass1!` | `{"chkFg":5}` (기존 PW 불일치) |
| 2-3 | **새PW 길이 오류** (chk=1) | `userPW=0000&upassWd=Ab1!` | `{"chkFg":1}` (BCrypt 검증 전에 차단) |
| 2-4 | **새PW 특수문자 없음** (chk=2) | `userPW=0000&upassWd=NewPass1234` | `{"chkFg":2}` |
| 2-5 | **새PW 숫자 부족** (chk=3) | `userPW=0000&upassWd=NewPassAbc!` | `{"chkFg":3}` |
| 2-6 | **새PW 영문 부족** (chk=4) | `userPW=0000&upassWd=12345678!` | `{"chkFg":4}` |
| 2-7 | ID=`7249525SHOP` | `userPW=` (빈값) | 400 (@NotBlank) |
| 2-8 | ID=`7249525SHOP` | `upassWd=` (빈값) | 400 (@NotBlank) |
| 2-9 | ID=`7249525SHOP` | `userPW` 4001자 초과 | 400 (@Size max=4000) |
| 2-10 | 세션 없음 | `userPW=0000&upassWd=NewPass1!` | 302 redirect |
| 2-11 | ID=`7249525SHOP` | 정상 변경 후 재확인 | DB `updateUsersTb` 실행 확인, BCrypt 저장 확인 |
| 2-12 | upassWd 4001자 초과 | `upassWd=` + 4001자 문자열 | 400 (`@Size` 위반) ★ |
| 2-13 | **유효성 검사 우선순위** | `userPW=`(빈값), `upassWd=`(빈값) 동시 전송 | 400 — `@NotBlank` 어느 것이 먼저 걸리는지 확인 |

---

## 3. `/getUserSecure` — 보안 정책 조회

**서비스 로직**: `userService.selectSecureInfo()` → `SecureDto` 반환  
**세션/파라미터 없음** (순수 시스템 보안 설정 조회)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | 로그인됨 | `{}` | `SecureDto` (PW 길이, 특수문자 정책 등) |
| 3-2 | 세션 없음 | `{}` | 302 redirect |
| 3-3 | getUserSecure 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 서비스 핵심 분기 요약

```
updatePW (updateUsersTb)
├── getPasswordChk(새PW) ≠ 0 → chkFg=1/2/3/4 즉시 반환 (BCrypt 검증 미실행)
└── getPasswordChk(새PW) = 0
    ├── BCrypt.matches(현재PW, 세션PW) 일치 → encode 후 UPDATE, returnMap={}
    └── 불일치 → chkFg=5 반환

chkFg 코드 정리
  0 (또는 returnMap={}) : 변경 성공
  1 : 새PW 길이 오류
  2 : 새PW 특수문자 오류
  3 : 새PW 숫자 부족
  4 : 새PW 영문 부족
  5 : 현재PW 불일치 (BCrypt 검증 실패)
```

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/emp/hq_emp_00002"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 로그인 유저 정보 조회
Invoke-RestMethod -Uri "$base/userInfo" -Method POST -Body '{}' -Headers $h -WebSession $session

# 3. 보안 정책 조회
Invoke-RestMethod -Uri "$base/getUserSecure" -Method POST -Body '{}' -Headers $h -WebSession $session

# 2-1. 정상 PW 변경
Invoke-RestMethod -Uri "$base/updatePW" -Method POST -ContentType $f `
  -Body "userPW=0000&upassWd=NewPass1!" -WebSession $session
# 예상: {} (빈 Map = 성공)

# 2-2. 현재PW 불일치
Invoke-RestMethod -Uri "$base/updatePW" -Method POST -ContentType $f `
  -Body "userPW=wrongPW&upassWd=NewPass1!" -WebSession $session
# 예상: {"chkFg":5}

# 2-3. 새PW 길이 오류 (너무 짧음)
Invoke-RestMethod -Uri "$base/updatePW" -Method POST -ContentType $f `
  -Body "userPW=0000&upassWd=Ab1!" -WebSession $session
# 예상: {"chkFg":1}

# 2-4. 새PW 특수문자 없음
Invoke-RestMethod -Uri "$base/updatePW" -Method POST -ContentType $f `
  -Body "userPW=0000&upassWd=NewPass1234" -WebSession $session
# 예상: {"chkFg":2}

# 2-5. 새PW 숫자 부족
Invoke-RestMethod -Uri "$base/updatePW" -Method POST -ContentType $f `
  -Body "userPW=0000&upassWd=NewPassAbc!" -WebSession $session
# 예상: {"chkFg":3}

# 2-6. 새PW 영문 부족
Invoke-RestMethod -Uri "$base/updatePW" -Method POST -ContentType $f `
  -Body "userPW=0000&upassWd=12345678!" -WebSession $session
# 예상: {"chkFg":4}
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `MUSERSTB` | 7249525SHOP 계정, BCrypt PW(`0000`), msNo=`NC0001` |
| `MSECURETB` | 보안정책 설정 (PW 최소길이, 특수문자 등) |
| `MMEMBSTB` | NC0001 매장 존재 |

---

## 주요 검증 포인트

```
□ updatePW — getPasswordChk 호출 순서 (BCrypt 전에 먼저 유효성 검증)
□ updatePW — chkFg=0 성공 시 returnMap이 완전히 빈 Map({}) 반환 확인
□ updatePW — 변경 성공 후 새 PW로 재로그인 가능 여부 확인
□ getUserSecure — SecureDto 반환값이 getPasswordChk 정책과 일치하는지 확인
□ userInfo — 반환 DTO에 PASSWORD 해시값이 노출되지 않는지 보안 확인
```

---

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] MUSERSTB (CUD 작업)
│   ├── (Trigger) Tr_MUSERS_T01
└── [공통 영향 테이블 및 호출]
    ├── MMEMLGTB [매장정보변경 HISTORY]
    ├── MMSLOGTB [MASTER LOG]
    ├── SSMEMBTB [POS와의 명판(매장) MASTER 응답]
    ├── SSUSERTB [POS와의 사원  MASTER 응답]
    ├── [FUNCTION] GET_SMS_CHAIN (MMEMBSTB)
    ├── [PROCEDURE] CNTPROC (MMEMBSTB)
    ├── [PROCEDURE] P_INITCOST (MUSERSTB)
    ├── [PROCEDURE] P_MACOST_B (MUSERSTB)
    ├── [PROCEDURE] P_TACOST_B (MUSERSTB)
    ├── [PROCEDURE] SUB_CALC_FIX_AMT_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_COUPON_NEW_SHOP_P_TEMP (MMEMBSTB)
    ├── [PROCEDURE] SUB_COUPON_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_CUSTCL_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_EMSWRK_P (MUSERSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_RECV_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_IMTRLG_I (MMEMBSTB)
    ├── [PROCEDURE] SUB_MASTER_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_NEWCUSTMSG_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_RECIPE_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SET_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_AFTER_PROC_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_MAIN_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_PROC_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_MGMVHD_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_TMPRGD_P01 (MMEMBSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_SINGLE_P (MMEMBSTB)
    └── [PROCEDURE] SUB_VDORDER_P (MMEMBSTB)
```
