# St_Emp_00002 — 비밀번호 관리 단위 테스트케이스

> **화면**: [ST] 직원 > 비밀번호 관리  
> **URL Prefix**: `POST /backoffice/data/st/emp/st_emp_00002`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: `userInfo`, `getUserSecure` = 파라미터 없음 / `updatePW` = `@RequestParam`
> **DB 트리거 영향도**: MUSERSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `msNo` | `MS001` | userInfo, updatePW |
| `ID` | `I000449s` | userInfo, updatePW |
| `PASSWORD` | BCrypt 해시 | updatePW (현재 비밀번호 검증) |

---

## 엔드포인트 목록 (3개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/userInfo` | 로그인 유저 정보 조회 | (파라미터 없음) | `CommonModule_UserListDto` | SELECT | MMEMBSTB<br>MUSERSTB  |
| 2 | `/updatePW` | 비밀번호 변경 (정책 검증 + BCrypt 대조) | `@RequestParam` | `Map` | UPDATE | MUSERSTB<br>UPDATEUSERSTB  |
|3|`/getUserSecure`|보안 정책 조회|(파라미터 없음)|`SecureDto`|SELECT| 공통 모듈/동적 쿼리 (추적 불가) |

---

## 1. `/userInfo` — 로그인 유저 정보 조회

**특이사항**: 파라미터 없이 세션에서 `msNo`, `ID` 자동 주입

> **[v2 보완]** **소스 68~69번** (`/userInfo`): `msNo`, `ID` 세션 주입 → 미로그인 시 NPE → TC 1-2 ✅ 정확

| No | 세션 조건 | 예상값 |
|----|----------|-------|
| 1-1 | msNo=`MS001`, ID=`I000449s` | `CommonModule_UserListDto` (사원정보 DTO) |
| 1-2 | 세션 없음 (미로그인) | `securityUserInformation.getUserInfo()` → 401 또는 NPE |

---

## 2. `/updatePW` — 비밀번호 변경

**서비스 처리 순서**:
```
getPasswordChk(upassWd):
  0: 정상
  1: 길이 오류
  2: 특수문자 오류
  3: 숫자 길이 오류
  4: 영문 길이 오류

chk != 0 → returnMap.put("chkFg", chk) → return (DB 미반영)

chk == 0:
  encodedPassword = securityUserInformation.getUserInfo("PASSWORD") ← 세션 BCrypt 해시
  bCryptEncoder.matches(userPW, encodedPassword):
    true  → encode(upassWd) → updateUsersTb() → returnMap 빈 Map {}
    false → returnMap.put("chkFg", 5)  (기존 비밀번호 불일치)
```

> **[v2 보완]** **소스 92~93번** (`/updatePW`): `userPW`, `upassWd` — `required=true`만 있고 **`@NotBlank` 없음**  

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 2-1 | ID=`I000449s`, PASSWORD=BCrypt(`pass01!A`) | - | `userPW=pass01!A&upassWd=NewPass1!` | 정책 통과 + 현재PW 일치 → `{}` (성공) |
| 2-2 | ID=`I000449s`, PASSWORD=BCrypt(`pass01!A`) | - | `userPW=wrongPass&upassWd=NewPass1!` | BCrypt 불일치 → `{"chkFg":5}` |
| 2-3 | ID=`I000449s` | - | `userPW=pass01!A&upassWd=short` | 길이 오류 → `{"chkFg":1}` |
| 2-4 | ID=`I000449s` | - | `userPW=pass01!A&upassWd=NoSpecial1` | 특수문자 없음 → `{"chkFg":2}` |
| 2-5 | ID=`I000449s` | - | `userPW=pass01!A&upassWd=NoNumbers!A` | 숫자 부족 → `{"chkFg":3}` |
| 2-6 | ID=`I000449s` | - | `userPW=pass01!A&upassWd=noletters1!` | 영문 부족 → `{"chkFg":4}` |
| 2-7 | - | - | `userPW` 없음 | 400 (required=true) |
| 2-8 | - | - | `upassWd` 없음 | 400 (required=true) |
| 2-9 | ID=`I000449s`, PASSWORD=BCrypt(`pass01!A`) | - | `userPW=pass01!A&upassWd=NewPass1!` (정상 성공 후 재실행) | updateUsersTb → DB PW 변경 확인 |

---

## 3. `/getUserSecure` — 보안 정책 조회

**특이사항**: `userService.selectSecureInfo()` 위임 — 세션/파라미터 무관

> **[v2 보완]** **소스 127번** (`/getUserSecure`): `userService.selectSecureInfo()` → 세션/commandMap 미사용 → 미로그인 접근 시 Spring Security 인터셉터 여부만 의존 (TC 3-2 ✅ 확인 필요)

| No | 예상값 |
|----|-------|
| 3-1 | `SecureDto` (비밀번호 정책: 최소길이, 특수문자 규칙 등) |
| 3-2 | 미로그인 상태에서도 반환 여부 확인 (세션 미사용) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/emp/st_emp_00002"
$f = "application/x-www-form-urlencoded"

# 1. 유저 정보 조회
Invoke-RestMethod -Uri "$base/userInfo" -Method POST -ContentType $f -WebSession $session

# 2-1. 비밀번호 변경 (정상)
Invoke-RestMethod -Uri "$base/updatePW" -Method POST -ContentType $f -WebSession $session `
  -Body "userPW=pass01!A&upassWd=NewPass1!"
# 예상: {} (성공)

# 2-2. 기존 PW 불일치
Invoke-RestMethod -Uri "$base/updatePW" -Method POST -ContentType $f -WebSession $session `
  -Body "userPW=wrongPass&upassWd=NewPass1!"
# 예상: {"chkFg":5}

# 2-3. 길이 오류
Invoke-RestMethod -Uri "$base/updatePW" -Method POST -ContentType $f -WebSession $session `
  -Body "userPW=pass01!A&upassWd=Sh1!"
# 예상: {"chkFg":1}

# 3. 보안 정책 조회
Invoke-RestMethod -Uri "$base/getUserSecure" -Method POST -ContentType $f -WebSession $session
```

---

## 주요 검증 포인트

```
□ updatePW — chkFg 코드 의미: 0=정상, 1=길이, 2=특수문자, 3=숫자, 4=영문, 5=기존PW불일치
□ updatePW — 성공 시 returnMap = {} (빈 Map) → UI에서 빈 Map으로 성공 판단 여부 확인
□ updatePW — BCrypt 검증은 세션 PASSWORD 필드 의존 → 세션 만료 시 NPE ★
□ updatePW — 성공 후 세션 PASSWORD 갱신 여부 확인 (미갱신 시 재로그인 전까지 구 PW 유지)
□ getUserSecure — 세션 무관 (userService 직접 위임) → 미로그인 접근 가능 여부 확인
□ @Validated 있음 — required=true 파라미터 누락 시 400
□ @Transactional rollbackFor Exception — updateUsersTb rollback 보장
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
