# St_Emp_00001 — 사원 관리 단위 테스트케이스

> **화면**: [ST] 직원 > 사원 관리  
> **URL Prefix**: `POST /backoffice/data/st/employee/st_emp_00001`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 조회 = `@RequestBody` / CUD = `@RequestParam`
> **DB 트리거 영향도**: MUSERSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search/store |
| `msNo` | `MS001` | search/store, searchDetail/store, userSave |
| `ID` | `I000449s` | search/store, searchDetail/store, IDDelete, userUpdate, moveEmp, copyMenu |
| `PASSWORD` | BCrypt 해시 | IDDelete, userUpdate |

---

## 엔드포인트 목록 (9개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search/store` | 매장 사원 목록 조회 (userType 매핑) | `@RequestBody` | `List` | SELECT | MNAMEMTB<br>MUSERSTB |
| 2 | `/searchDetail/store` | 매장 사원 상세 조회 | `@RequestParam` | `List` | SELECT | MNAMEMTB<br>MUSERSTB |
| 3 | `/idDupChk` | 아이디 중복 체크 | `@RequestParam` | `String` | SELECT | MUSERSTB  |
| 4 | `/userSave` | 사원 등록 (초기PW = HMS+날짜+!) | `@RequestParam` | `Map` | INSERT | MUSERSTB  |
| 5 | `/IDDelete` | 사원 삭제 (BCrypt 본인인증 후 CSV 파싱) | `@RequestParam` | `Map` | DELETE | DELETEMLTB<br>MUSERSTB<br>USERMLTB  |
| 6 | `/userUpdate` | 사원 수정 (BCrypt 본인인증 후 update) | `@RequestParam` | `Map` | UPDATE | MUSERSTB  |
| 7 | `/pwReset` | 비밀번호 초기화 (HMS+날짜+! 평문 반환) | `@RequestParam` | `String` | UPDATE | MUSERSTB  |
| 8 | `/moveEmp` | 사원 이동 (temp 메뉴권한 보관 후 이동) | `@RequestParam` | `void` | UPDATE | GETUSERMLTB<br>MUSERSTB<br>TB_USER_LAST_MENU<br>USERMLTB  |
| 9 | `/searchUser` | 메뉴 복사 대상 사원 조회 | `@RequestBody` | `List` | SELECT | MUSERSTB  |
| 10 | `/copyMenu` | 메뉴 복사 (typeChk 분기 후 copyMenu) | `@RequestParam` | `Map` | UPDATE | MUSERSTB<br>TB_USER_LAST_MENU<br>USERMLTB  |

---

## 1. `/search/store` — 매장 사원 목록 조회

**서비스**: `selectStoreEmpList` + `getStoreUserFgNmList` → for 루프로 `userTypeNm` 매핑

> **[v2 보완]** **소스 68번** (`/search/store`): `smAdminYn = "N"` 하드코딩 → 동일 패턴

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | `{}` | `smAdminYn=N` 기준 사원 목록 + userTypeNm 매핑 |
| 1-2 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | `{"userNm":"홍길동"}` | 이름 필터 |
| 1-3 | chainNo=`C001`, msNo=`MS001` | `{}` | userType null인 사원 → `userTypeNm` 미세팅 (null 방어 있음) |

---

## 2. `/searchDetail/store` — 매장 사원 상세 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | `addUserId=user01` | 해당 사원 상세 정보 |
| 2-2 | - | `addUserId` 없음 | 400 (required=true) |
| 2-3 | 추가 | `addUserId=` (빈값) | **400 아님** — required=true이나 @NotBlank 없음 → 빈값 통과 ★ |

---

## 3. `/idDupChk` — 아이디 중복 체크

| No | Request | 예상값 |
|----|---------|-------|
| 3-1 | `addUserId=existUser` | count>0 → `"dupl"` |
| 3-2 | `addUserId=newUser` | count=0 → `""` (빈 문자열) |
| 3-3 | `addUserId` 없음 | 400 (required=true) |

---

## 4. `/userSave` — 사원 등록

**서비스 처리**:
```
getEmpiId() → EMP_ID 채번
초기PW = BCrypt.encode("HMS" + today + "!")  (예: "0000")
insertUser()
반환: {"hqYn": hqYn}
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 4-1 | msNo=`MS001`, ID=`I000449s` | `addUserId=newEmp&userNm=홍길동&useYn=Y&userFg=1&hqYn=shop&orderFg=1&email=test@test.com` | `{"hqYn":"shop"}` |
| 4-2 | msNo=`MS001`, ID=`I000449s` | + `VendorCd=VND001&telNo=010-0000-0000` | VendorCd/telNo 포함 등록 |
| 4-3 | - | `addUserId` 없음 | 400 (@NotBlank) |
| 4-4 | - | `email` 없음 | 400 (@NotBlank) |
| 4-5 | msNo=`MS001`, ID=`I000449s` | `addUserId` 길이 46자 | @Size(max=45) → 400 |

---

## 5. `/IDDelete` — 사원 삭제

**서비스 처리**:
```
deluserId → String.valueOf().split(",") → CSV 복수 삭제 가능
BCrypt.matches(passWd, session.PASSWORD):
  true  → deleteUserTb(list) + deleteMlTb(list)
  false → returnMap.put("chkFg", "notcorr")

hqYn == "hq"   → ms_no_list = commandMap.get("chain_ms_no")  ← commandMap에 없음 시 null ★
hqYn == "shop" → ms_no_list = commandMap.get("ms_no")        ← msNo 파라미터 값
```

> **[v2 보완]** **소스 206번** (`/IDDelete`): `hqYnDel` — **`@NotBlank` 없음** (required=true만) → 빈값 통과  

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 5-1 | ID=`I000449s`, PASSWORD=BCrypt(`pass01!A`) | `deluserId=emp01&passWd=pass01!A&hqYnDel=shop&msNo=MS001` | BCrypt 일치 → 삭제 → `{"hqYn":"shop"}` |
| 5-2 | ID=`I000449s`, PASSWORD=BCrypt(`pass01!A`) | `deluserId=emp01,emp02&passWd=pass01!A&hqYnDel=shop&msNo=MS001` | CSV 2건 → 2건 삭제 |
| 5-3 | ID=`I000449s`, PASSWORD=BCrypt(`pass01!A`) | `deluserId=emp01&passWd=wrongPass&hqYnDel=shop` | `{"chkFg":"notcorr","hqYn":"shop"}` |
| 5-4 | ID=`I000449s`, PASSWORD=BCrypt(`pass01!A`) | `deluserId=emp01&passWd=pass01!A&hqYnDel=hq` | `ms_no_list = commandMap.get("chain_ms_no")` → null (파라미터 미전달) ★ |
| 5-5 | - | `deluserId` 없음 | 400 (@NotBlank) |

---

## 6. `/userUpdate` — 사원 수정

**서비스**: BCrypt 본인인증 후 update  
**반환**: 성공 → `{"hqYn": hqYn}` / 실패 → `{"chkFg":"notcorr", "hqYn": hqYn}`

> **[v2 보완]** **소스 254~256번** (`/userUpdate`): `passWd`/`chkpassWd` 이중 put — Admin_Emp_00001과 동일 코드 품질 이슈

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 6-1 | ID=`I000449s`, PASSWORD=BCrypt(`pass01!A`) | `editUserId=emp01&chkpassWd=pass01!A&editNm=홍길동&edtuserFg=1&edtUseYn=Y&hqYnEdit=shop&orderFg=1&email=t@t.com` | `{"hqYn":"shop"}` |
| 6-2 | ID=`I000449s`, PASSWORD=BCrypt(`pass01!A`) | 동일 + `chkpassWd=wrongPass` | `{"chkFg":"notcorr","hqYn":"shop"}` |
| 6-3 | - | `editUserId` 없음 | 400 (@NotBlank) |

---

## 7. `/pwReset` — 비밀번호 초기화

**보안 주의**:
```
enPasswd = BCrypt.encode("HMS" + today + "!")
resetPw() → DB 업데이트
return "HMS" + today + "!"  ← 평문 비밀번호 HTTP 응답에 포함 ★★
```

| No | Request | 예상값 |
|----|---------|-------|
| 7-1 | `editUserId=emp01` | `"0000"` (평문 반환) |
| 7-2 | `editUserId` 없음 | `commandMap.put("editUserId", null)` → Mapper SQL 처리 확인 |
| 7-3 | 추가 | `editUserId=` (빈값) | 빈값 통과 → `commandMap.put("editUserId", "")` → resetPw("") ★ |

---

## 8. `/moveEmp` — 사원 이동

**서비스 처리**:
```
getUsermltb() → id null 여부 분기
  id == null → instTempMenuList
  id != null → delTempMenuList → instTempMenuList

delEmpMenuList()
updEmp()

selectStoreCd == "All" → ms_no 미세팅 (commandMap에 ms_no 없음)
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 8-1 | ID=`I000449s` | `moveUserId=emp01&selectStoreCd=MS002&nowStoreCd=MS001&copyYn=N&tempCode=TEMP01` | 이동 처리 (void) |
| 8-2 | ID=`I000449s` | `selectStoreCd=All&...` | ms_no 미세팅 → Mapper SQL All 처리 |
| 8-3 | - | `moveUserId` 없음 | 400 (@NotBlank) |

---

## 9. `/searchUser` — 메뉴 복사 대상 사원 조회

**특이사항**: `smAdminYn = "N"` 하드코딩 — `if(smAdminYn.equals("N"))` → 항상 true

> **[v2 보완]** **소스 354~357번** (`/searchUser`): `smAdminYn = "N"` 하드코딩 → `if("N".equals("N"))` 항상 true → TC 165번 ✅ 정확

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 9-1 | `{"flag":"copy"}` | smAdminYn=N 기준 전체 사원 |
| 9-2 | `{"flag":"copy","user_id":"emp01","ms_no":"MS001"}` | 필터 조회 |
| 9-3 | `{}` (flag 없음) | `reqMap.put("flag", null)` → Mapper SQL null 처리 |

---

## 10. `/copyMenu` — 메뉴 복사

**typeChk 반환값**:
```
0: 정상 → copyMenu 실행
1: 타입 없음 (sUserType==9) → "noType"
2: HQ 타입 불일치 (sUserType==0, tUserType!=0) → "Hq"
3: Vendor 불일치 (sUserType==3, tUserType!=3) → "Vendor"
4: 매장 불일치 → "Ms"

★ 버그: if(sUserType == 9 || sUserType == 9) → 조건 동일, OR 의미 없음
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 10-1 | ID=`I000449s` | `sUserChk=empSrc&tUserChk[]=empDst1` | typeChk=0 → copyMenu → `{"chkFg":""}` |
| 10-2 | ID=`I000449s` | 소스/대상 userType 불일치 | `{"chkFg":"Hq"}` or `"Vendor"` or `"Ms"` |
| 10-3 | - | `sUserChk` 없음 | 400 (@NotBlank) |
| 10-4 | - | `tUserChk[]` 없음 | 400 (required=true) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/employee/st_emp_00001"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 사원 목록
Invoke-RestMethod -Uri "$base/search/store" -Method POST -Headers $h -WebSession $session -Body '{}'

# 2. 상세 조회
Invoke-RestMethod -Uri "$base/searchDetail/store" -Method POST -ContentType $f -WebSession $session `
  -Body "addUserId=emp01"

# 3. 중복 체크
Invoke-RestMethod -Uri "$base/idDupChk" -Method POST -ContentType $f -WebSession $session `
  -Body "addUserId=newEmp"

# 4. 사원 등록
Invoke-RestMethod -Uri "$base/userSave" -Method POST -ContentType $f -WebSession $session `
  -Body "addUserId=newEmp&userNm=홍길동&useYn=Y&userFg=1&hqYn=shop&orderFg=1&email=test@test.com"

# 5. 삭제 (본인 PW 필요)
Invoke-RestMethod -Uri "$base/IDDelete" -Method POST -ContentType $f -WebSession $session `
  -Body "deluserId=newEmp&passWd=pass01!A&hqYnDel=shop&msNo=MS001"

# 7. 비밀번호 초기화 (평문 응답 확인)
Invoke-RestMethod -Uri "$base/pwReset" -Method POST -ContentType $f -WebSession $session `
  -Body "editUserId=emp01"
# 예상: "0000" (평문 노출 ★★)
```

---

## 주요 검증 포인트

```
□ pwReset — 초기화 비밀번호 평문("HMS+날짜+!") HTTP 응답 반환 → 보안 취약점 ★★★
□ IDDelete — hqYn="hq" → chain_ms_no 파라미터 없음 → ms_no_list=null → 삭제 조건 null ★★
□ typeChk — sUserType==9 조건 버그 (||로 동일 조건 반복 → flag=2/3/4 도달 불가) ★★
□ copyMenu — t_user_id[] → (String[]) commandMap.get("t_user_id") → typeChk/copyMenu 동일 배열 공유
□ IDDelete/userUpdate — BCrypt 검증은 세션 PASSWORD 필드 의존 → 세션 만료 시 NPE ★
□ insertUser — 초기PW = "HMS" + today + "!" (BCrypt 인코딩) → 날짜 변경 시 PW 예측 가능 ★
□ search/store — userType null 방어 있음 (if != null 체크) → 정상 처리
□ moveEmp — selectStoreCd="All" → ms_no 미세팅 → Mapper SQL ALL 처리 의도 확인
□ @Validated 있음 — @NotBlank, @Size 위반 시 400
□ @Transactional rollbackFor Exception — insertUser/deleteUserTb/userUpdate/moveEmp/copyMenu rollback 보장
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
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_IMTRLG_I (MMEMBSTB)
    ├── [PROCEDURE] SUB_MASTER_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_NEWCUSTMSG_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_RECIPE_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SET_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (MMEMBSTB)
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
