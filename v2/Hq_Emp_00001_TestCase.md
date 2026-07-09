# Hq_Emp_00001 — 사원관리(본사) 단위 테스트케이스

> **화면**: [HQ] 인사관리 > 사원관리  
> **URL Prefix**: `POST /backoffice/data/hq/employee/hq_emp_00001`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}
> **DB 트리거 영향도**: MUSERSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 |
| `msNo` | `NC0001` | 본부 매장번호 (chain_ms_no) |
| `ID` | `7249525SHOP` | 로그인 사용자 ID |
| `PASSWORD` | BCrypt 해시값 | BCrypt PW 검증에 사용 |

---

## 엔드포인트 목록 (13개)

| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search/hq` | 본부 사원 목록 조회 | SELECT | MNAMEMTB<br>MUSERSTB |
| 2 | `/search/store` | 매장 사원 목록 조회 | SELECT | MNAMEMTB<br>MUSERSTB |
| 3 | `/searchDetail/hq` | 본부 사원 상세 조회 | SELECT | MNAMEMTB<br>MUSERSTB |
| 4 | `/searchDetail/shop` | 매장 사원 상세 조회 | SELECT | MNAMEMTB<br>MUSERSTB |
| 5 | `/idDupChk` | ID 중복 체크 | SELECT | MUSERSTB  |
| 6 | `/userSave` | 사원 등록 (BCrypt 초기PW) | INSERT | MROLEDTB<br>MROLEHTB<br>MUSERSTB<br>USERMLTB  |
| 7 | `/IDDelete` | 사원 삭제 (BCrypt PW 인증) | DELETE | DELETEMLTB<br>MUSERSTB<br>USERMLTB  |
| 8 | `/userUpdate` | 사원 수정 (BCrypt PW 인증) | UPDATE | MROLEDTB<br>MROLEHTB<br>MUSERSTB<br>USERMLTB  |
| 9 | `/pwReset` | 비밀번호 초기화 | UPDATE | MUSERSTB  |
| 10 | `/moveEmp` | 사원 이동 (임시메뉴 연동) | UPDATE | GETUSERMLTB<br>MUSERSTB<br>TB_USER_LAST_MENU<br>USERMLTB  |
| 11 | `/searchUser` | 사원 검색 (메뉴복사용) | SELECT | MMEMBSTB<br>MUSERSTB  |
| 12 | `/copyMenu` | 메뉴 복사 (typeChk 분기) | UPDATE | MUSERSTB<br>TB_USER_LAST_MENU<br>USERMLTB  |
| 13 | `/selectRole` | 권한별 메뉴 조회 | SELECT | MROLEHTB  |

---

## 1~2. `/search/hq`, `/search/store` — 사원 목록 조회

**서비스 로직**: `selectHqEmpList()` + `getHqUserFgNmList()` → userType 코드→명칭 매핑

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001`, ID=`7249525SHOP`, msNo=`NC0001` | `{}` | 본부 사원 List, userTypeNm 세팅 |
| 1-2 | chainNo=`C001` | `{"searchNm":"홍길동"}` | 이름 검색 결과 |
| 1-3 | chainNo=`C001` | `{}` (userType=null 사원 있음) | userTypeNm 미세팅 (null 유지), 오류 없음 |
| 2-1 | chainNo=`C001`, msNo=`NC0001` | `{}` | 매장 사원 List, storeUserFgNm 코드 매핑 |
| 2-2 | chainNo=`C001` | `{"selectMsNo":"NC0007"}` | 특정 매장 사원만 |

---

## 3~4. `/searchDetail/hq`, `/searchDetail/shop` — 사원 상세 조회

**파라미터 방식**: `@RequestParam` (form-data)

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 3-1 | chainNo=`C001`, msNo=`NC0001` | `addUserId=user01` | 본부 사원 상세 List, userTypeNm 세팅 |
| 3-2 | - | `addUserId=` (빈값) | 400 (@NotBlank) |
| 3-3 | - | `addUserId=XXXXXXX` (없는 ID) | `[]` |
| 4-1 | chainNo=`C001`, msNo=`NC0001` | `addUserId=user02&selectMsNo=NC0007` | 매장 사원 상세 |
| 4-2 | - | `addUserId=user02` (selectMsNo 없음) | selectMsNo=`""` (defaultValue) |

---

## 5. `/idDupChk` — ID 중복 체크

**서비스 분기**: `dupIdchk() > 0` → `"dupl"` / `= 0` → `""`

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 5-1 | 로그인됨 | `addUserId=user01` (존재함) | `"dupl"` |
| 5-2 | 로그인됨 | `addUserId=newuser99` (미존재) | `""` (빈 문자열) |
| 5-3 | 로그인됨 | `addUserId=` (빈값) | 400 (@NotBlank) |
| 5-4 | idDupChk 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 6. `/userSave` — 사원 등록

**서비스 로직**:
1. `getEmpiId()` → EMP_ID 채번
2. BCrypt 암호화: `"HMS" + yyyyMMdd + "!"` (오늘 날짜)
3. `insertUser()` INSERT
4. `userRole != ""` → `insertUserRole()` 추가 INSERT

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 6-1 | msNo=`NC0001`, ID=`7249525SHOP` | `addUserId=newuser&userNm=홍길동&useYn=Y&userFg=HQ&hqYn=Y&orderFg=1&email=test@test.com&msNo=NC0002` | 등록 성공, `{"hqYn":"Y"}`, 초기PW=`0000` |
| 6-2 | msNo=`NC0001` | `userRole=ROLE_ADMIN` 포함 | insertUser + insertUserRole 2건 INSERT |
| 6-3 | msNo=`NC0001` | `userRole=` (빈값) | insertUser만 (insertUserRole 미호출) |
| 6-4 | - | `addUserId=` (빈값) | 400 (@NotBlank, @Size) |
| 6-5 | - | `addUserId` 46자 이상 | 400 (@Size max=45) |
| 6-6 | - | `email=` (빈값) | 400 (@NotBlank) |
| 6-7 | msNo=`NC0001` | VendorCd, telNo 미포함 | defaultValue=`""` 처리, 정상 등록 |
| 6-8 | - | **@Transactional**: insertUserRole 중 오류 | insertUser도 롤백 |

---

## 7. `/IDDelete` — 사원 삭제

**서비스 분기: BCrypt PW 인증**
```
bCryptEncoder.matches(입력PW, 세션PASSWORD)
├── 일치 → deluserId 콤마 분리 배열 순회 → deleteUserTb + deleteMlTb
│   ├── hqYn="hq"   → ms_no_list = chain_ms_no (세션)
│   └── hqYn="shop" → ms_no_list = ms_no (파라미터)
└── 불일치 → chkFg="notcorr" 반환, 삭제 안 함
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 7-1 | ID=`7249525SHOP`, PW=BCrypt(`0000`) | `deluserId=user01&passWd=0000&hqYnDel=hq` | 삭제 성공, `{"hqYn":"hq"}` |
| 7-2 | **PW 불일치** | `deluserId=user01&passWd=wrongPW&hqYnDel=hq` | `{"chkFg":"notcorr","hqYn":"hq"}` |
| 7-3 | PW 일치 | `deluserId=user01,user02&passWd=0000&hqYnDel=hq` | 2명 동시 삭제 (콤마 분리) |
| 7-4 | PW 일치, hqYn=shop | `deluserId=user03&hqYnDel=shop&msNo=NC0007&passWd=0000` | ms_no_list=NC0007로 삭제 |
| 7-5 | - | `deluserId=` | 400 (@NotBlank) |
| 7-6 | - | `passWd=` | 400 (@NotBlank) |

---

## 8. `/userUpdate` — 사원 수정

**서비스 분기: BCrypt PW 인증**
```
bCryptEncoder.matches(chkpassWd, 세션PASSWORD)
├── 일치 → userUpdate() → userRole != "" → deleteUserMl() + updateUserRole()
└── 불일치 → chkFg="notcorr"
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 8-1 | ID=`7249525SHOP`, PW=BCrypt(`0000`) | `editUserId=user01&chkpassWd=0000&editNm=홍길동(수정)&edtuserFg=HQ&edtUseYn=Y&hqYnEdit=Y&orderFg=1&email=new@test.com` | 수정 성공, `{"hqYn":"Y"}` |
| 8-2 | **PW 불일치** | `chkpassWd=wrongPW` | `{"chkFg":"notcorr","hqYn":"..."}` |
| 8-3 | PW 일치 | `userRole=ROLE_ADMIN` 포함 | deleteUserMl + updateUserRole 실행 |
| 8-4 | PW 일치 | `userRole=` (빈값) | userUpdate만, 권한 수정 안 함 |
| 8-5 | - | `editUserId=` | 400 (@NotBlank) |
| 8-6 | - | `editNm` 151자 이상 | 400 (@Size max=150) |
| 8-7 | BCrypt 인증 키 확인 | userUpdate 호출 | 서비스에서 `commandMap.get("passWd")` 또는 `"chkpassWd"` 중 어느 것으로 인증하는지 확인 |

---

## 9. `/pwReset` — 비밀번호 초기화

**서비스 로직**: BCrypt encode(`"HMS" + yyyyMMdd + "!"`) → resetPw() UPDATE → 평문 반환

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 9-1 | 로그인됨 | `editUserId=user01` | `"0000"` (오늘날짜 포함 초기PW) 반환, DB는 BCrypt |
| 9-2 | 로그인됨 | `editUserId=XXXXX` (없는 ID) | 0건 UPDATE, 초기PW 문자열 반환 |
| 9-3 | - | `editUserId=` | 400 (@NotBlank) |

---

## 10. `/moveEmp` — 사원 이동

**서비스 로직 (임시메뉴 연동)**:
```
getUsermltb() → id 존재 여부
├── id == null → instTempMenuList() (신규 임시메뉴 저장)
└── id != null → delTempMenuList() → instTempMenuList() (교체)

→ delEmpMenuList() (기존 메뉴권한 삭제)
→ updEmp() (사원 매장 변경)
```

**컨트롤러 특이사항**: `selectStoreCd="All"` → commandMap에 ms_no 미세팅

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 10-1 | ID=`7249525SHOP` | `moveUserId=user01&selectStoreCd=NC0007&nowStoreCd=NC0001&copyYn=N&tempCode=T001` | 정상 이동, 임시메뉴 연동 |
| 10-2 | ID=`7249525SHOP` | **임시메뉴 없는 사원**: getUsermltb=null | instTempMenuList만 실행 |
| 10-3 | ID=`7249525SHOP` | **임시메뉴 있는 사원**: getUsermltb=기존ID | delTempMenuList → instTempMenuList 순서 |
| 10-4 | ID=`7249525SHOP` | `selectStoreCd=All` | ms_no commandMap 미세팅 (All 처리) |
| 10-5 | - | `moveUserId=` | 400 (@NotBlank) |
| 10-6 | 정상 이동 응답 확인 | moveEmp 정상 완료 | HTTP 200, 바디 없음(null/빈 문자열) ★ |
| 10-7 | 예외 시 응답 | DB 오류 발생 | HTTP 500, 바디 없음 (성공 여부 구분 불가) |

---

## 11. `/searchUser` — 사원 검색 (메뉴복사용)

**파라미터**: `flag` (필수), `user_id`, `user_nm`, `ms_no` (선택, containsKey 방어)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 11-1 | chainNo=`C001` | `{"flag":"hq","user_id":"user01"}` | 해당 사원 List |
| 11-2 | chainNo=`C001` | `{"flag":"store","user_nm":"홍길동","ms_no":"NC0007"}` | 매장 사원 검색 |
| 11-3 | chainNo=`C001` | `{"flag":"hq"}` (user_id 키 없음) | user_id=`""` 처리 |
| 11-4 | searchUser 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 12. `/copyMenu` — 메뉴 복사

**서비스 분기: typeChk (4단계)**
```
sGetType(s_user_id) → sUserType
tGetType(t_user_id) → tUserType (대상자별 반복)

sUserType="HQ"    → tUserType="HQ"    → flag=0 (복사 가능)
                  → tUserType≠"HQ"   → flag=2 → "Hq" 반환
sUserType="ADMIN" → tUserType="ADMIN" → flag=0
                  → tUserType≠"ADMIN"→ flag=3 → "Admin" 반환
그 외(ST)         → tUserType="ST"    → flag=0
                  → tUserType≠"ST"   → flag=4 → "Ms" 반환

flag=0 → copyMenu() 실행
```

**copyMenu 로직**: 대상자별 delTempMenuList → instTempMenuList → delMenuList → copyMenuList

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 12-1 | ID=`7249525SHOP` | `sUserChk=hqUser1&tUserChk[]=hqUser2` (HQ→HQ) | `{"chkFg":""}`, 복사 성공 |
| 12-2 | **타입 불일치** | `sUserChk=hqUser1&tUserChk[]=storeUser1` (HQ→ST) | `{"chkFg":"Hq"}` |
| 12-3 | **ADMIN→비ADMIN** | sUserType=ADMIN, tUserType=HQ | `{"chkFg":"Admin"}` |
| 12-4 | **ST→비ST** | sUserType=ST, tUserType=HQ | `{"chkFg":"Ms"}` |
| 12-5 | ID=`7249525SHOP` | 다중 대상: `tUserChk[]=hqUser2&tUserChk[]=hqUser3` | typeChk 통과 후 2명 복사 |
| 12-6 | ID=`7249525SHOP` | 다중 대상 중 타입 불일치 포함 | 첫 불일치에서 break → 전체 복사 안 함 |
| 12-7 | - | `sUserChk=` | 400 (@NotBlank) |

---

## 13. `/selectRole` — 권한별 메뉴 조회

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 13-1 | chainNo=`C001` | `hqYn=Y` | 본부 권한 메뉴 List |
| 13-2 | chainNo=`C001` | `hqYn=N` | 매장 권한 메뉴 List |
| 13-3 | - | `hqYn=` | 400 (@NotBlank) |
| 13-4 | selectRole 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 서비스 핵심 분기 요약

```
insertUser (userSave)
└── userRole != "" → insertUserRole 추가 / "" → 미호출

deleteUserTb (IDDelete)
├── BCrypt 불일치 → chkFg="notcorr", 삭제 안 함
└── 일치 → 콤마 분리 다건 삭제
    ├── hqYn="hq"   → ms_no_list = 세션 chain_ms_no
    └── hqYn="shop" → ms_no_list = 파라미터 ms_no

userUpdate
├── BCrypt 불일치 → chkFg="notcorr"
└── 일치 → userUpdate() → userRole!="" → deleteUserMl+updateUserRole

moveEmp
├── getUsermltb=null → instTempMenuList (신규)
└── getUsermltb≠null → del+inst (교체)
→ delEmpMenuList → updEmp (항상 실행)

typeChk (copyMenu)
├── sType=HQ,    tType≠HQ    → flag=2 "Hq"
├── sType=ADMIN, tType≠ADMIN → flag=3 "Admin"
└── sType=기타,  tType≠ST    → flag=4 "Ms"
flag=0 → copyMenu 실행
```

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/employee/hq_emp_00001"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 본부 사원 조회
Invoke-RestMethod -Uri "$base/search/hq" -Method POST -Body '{}' -Headers $h -WebSession $session

# 5. ID 중복 체크
Invoke-RestMethod -Uri "$base/idDupChk" -Method POST -Body "addUserId=newuser99" -ContentType $f -WebSession $session

# 6. 사원 등록
Invoke-RestMethod -Uri "$base/userSave" -Method POST -ContentType $f `
  -Body "addUserId=testuser01&userNm=테스트사원&useYn=Y&userFg=HQ&hqYn=Y&orderFg=1&email=test@test.com&msNo=NC0002" `
  -WebSession $session

# 7. 사원 삭제 (PW 정상)
Invoke-RestMethod -Uri "$base/IDDelete" -Method POST -ContentType $f `
  -Body "deluserId=testuser01&passWd=0000&hqYnDel=hq" -WebSession $session

# 7-PW오류. 사원 삭제 (PW 불일치)
Invoke-RestMethod -Uri "$base/IDDelete" -Method POST -ContentType $f `
  -Body "deluserId=user01&passWd=wrongPW&hqYnDel=hq" -WebSession $session
# 예상: {"chkFg":"notcorr","hqYn":"hq"}

# 9. PW 초기화
Invoke-RestMethod -Uri "$base/pwReset" -Method POST -ContentType $f `
  -Body "editUserId=user01" -WebSession $session
# 예상: "0000"

# 12. 메뉴 복사 (타입 일치)
Invoke-RestMethod -Uri "$base/copyMenu" -Method POST -ContentType $f `
  -Body "sUserChk=hqUser1&tUserChk[]=hqUser2" -WebSession $session
# 예상: {"chkFg":""}

# 12. 메뉴 복사 (타입 불일치)
Invoke-RestMethod -Uri "$base/copyMenu" -Method POST -ContentType $f `
  -Body "sUserChk=hqUser1&tUserChk[]=storeUser1" -WebSession $session
# 예상: {"chkFg":"Hq"}
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `MUSERSTB` | HQ/ADMIN/ST 유형 사원 각 1명 이상, BCrypt PW 저장 |
| `MMLTB` | 메뉴 권한 데이터 (copyMenu, moveEmp 테스트) |
| `MTEMPMLTB` | 임시메뉴 테이블 (moveEmp 분기 확인) |
| `MROLESTB` | 권한 코드 테이블 |
| `MMCHATB` | chainNo=C001 체인 마스터 |
| `MMEMBSTB` | NC0001 본부, NC0007 일반 매장 |

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
    ├── MVNDRMTB [거래선 MASTER]
    ├── SSMEMBTB [POS와의 명판(매장) MASTER 응답]
    ├── SSUSERTB [POS와의 사원  MASTER 응답]
    ├── SSVNDRTB [거래선 MASTER]
    ├── [FUNCTION] F_GET_CUR_INFO (MNAMEMTB)
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
    ├── [PROCEDURE] SUB_IF_HYDM_RECV_P (TVNDRMTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_IMTRLG_I (MMEMBSTB)
    ├── [PROCEDURE] SUB_MASTER_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_MASTER_P (MVNDRMTB)
    ├── [PROCEDURE] SUB_NEWCUSTMSG_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_RECIPE_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SET_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SET_IO_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SL_SET_GOODS_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_AFTER_PROC_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_MAIN_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_PROC_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_MGMVHD_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_TMPRGD_P01 (MMEMBSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_SINGLE_P (MMEMBSTB)
    └── [PROCEDURE] SUB_VDORDER_P (MMEMBSTB)
```
