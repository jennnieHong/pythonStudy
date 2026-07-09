# Admin_Emp_00001 — 사원관리(어드민) 단위 테스트케이스 v2

> **화면코드**: `Admin_Emp_00001`  
> **URL Prefix**: `POST /backoffice/data/admin/employee/admin_emp_00001`  
> **권한**: ADMIN 세션 필요  
> **서비스**: `Admin_Emp_00001_Service`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`
> **DB 트리거 영향도**: MMEMBSTB, MUSERSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## ⚠️ 구조 주의사항

```
adminUserUpdate — userRole 파라미터 없음 → role 수정 분기 절대 실행 안 됨 ★
copyMenu 서비스 — Mapper 호출 순서:
  [대상사원 루프] delTempMenuList → instTempMenuList (반복)
  [루프 완료 후] delMenuList (1회) → copyMenuList (1회)
typeChk flag=1 — 소스에 주석 처리됨 (사용 안 함)
deleteUserTb — hqYn 이 "hq"/"shop" 아닌 값 → ms_no_list 미설정
```

---

## 엔드포인트 목록 (16개)

| # | URL | 기능 | 요청방식 | ServiceType | 연관 트리거 (대상 테이블)  관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/search/hq` | 본사 사원 목록 조회 | RequestBody | SELECT | - | MMEMBSTB<br>MNAMEMTB |
| 2 | `/search/store` | 매장 사원 목록 조회 | RequestBody | SELECT | - | MNAMEMTB<br>MUSERSTB |
| 3 | `/searchDetail/hq` | 본사 사원 상세 조회 | RequestParam | SELECT | - | MMEMBSTB<br>MNAMEMTB |
| 4 | `/searchDetail/shop` | 매장 사원 상세 조회 | RequestParam | SELECT | - | MNAMEMTB<br>MUSERSTB |
| 5 | `/idDupChk` | ID 중복 체크 | RequestParam | - | - | MUSERSTB  |
| 6 | `/userSave` | 사용자 등록 (일반) | RequestParam | INSERT | `MUSERS_T01` (MUSERSTB : INSERT)  MMEMBSTB<br>MROLEDTB<br>MROLEHTB<br>MUSERSTB<br>USERMLTB |
| 7 | `/userAdminSave` | Admin 사용자 등록 | RequestParam | INSERT | `MUSERS_T01` (MUSERSTB : INSERT)  MUSERSTB |
| 8 | `/IDDelete` | 사용자 삭제 | RequestParam | DELETE | `MUSERS_T01` (MUSERSTB : DELETE)  DELETEMLTB<br>MUSERSTB<br>USERMLTB |
| 9 | `/userUpdate` | 사원 정보 수정 | RequestParam | UPDATE | `MUSERS_T01` (MUSERSTB : UPDATE)  MROLEDTB<br>MROLEHTB<br>MUSERSTB<br>USERMLTB |
| 10 | `/adminUserUpdate` | Admin 사원 수정 (userRole 없음) | RequestParam | UPDATE | `MUSERS_T01` (MUSERSTB : UPDATE)  MROLEDTB<br>MROLEHTB<br>MUSERSTB<br>USERMLTB |
| 11 | `/pwReset` | 비밀번호 초기화 | RequestParam | UPDATE | `MUSERS_T01` (MUSERSTB : UPDATE)  MUSERSTB |
| 12 | `/moveEmp` | 사원 매장 이동 | RequestParam | UPDATE | `MUSERS_T01` (MUSERSTB : UPDATE)  GETUSERMLTB<br>MUSERSTB<br>TB_USER_LAST_MENU<br>USERMLTB |
| 13 | `/searchUser` | 메뉴복사용 사원 조회 | RequestBody | SELECT | - | MMEMBSTB<br>MUSERSTB  |
| 14 | `/copyMenu` | 사원 메뉴 복사 | RequestParam | UPDATE | - | MUSERSTB<br>TB_USER_LAST_MENU<br>USERMLTB  |
| 15 | `/selectRole` | 권한별 메뉴 조회 | RequestParam | SELECT | - | MROLEHTB  |
| 16 | `/unlock` | 계정 잠금 해제 | RequestParam | UPDATE | `MUSERS_T01` (MUSERSTB : UPDATE)  MUSERSTB |

---

## 1. `/search/hq` — 본사 사원 목록 조회

**서비스**: `selectHqEmpList()` → `getHqUserFgNmList()` → userType 코드→명칭 매핑  
**요청**: `@RequestBody` (세션에서 userId 자동 주입)

| No | TC | 예상값 | 비고 |
|----|----|-------|------|
| 1-1 | 정상 조회 | List, userTypeNm 매핑 포함 | getUserType() != null 분기 |
| 1-2 | USER_FG=NULL 사원 | userTypeNm=null, 나머지 정상 | null 스킵 분기 |
| 1-3 | userType 코드 매핑 확인 | userTypeNm='본사' 등 | GETUSERMLTB nmCd→nmRep |
| 1-4 | 미인증 접근 | 302 redirect 또는 401 | Spring Security |
| 1-5 | 결과 없음 | `[]` 빈 리스트 | |

---

## 2. `/search/store` — 매장 사원 목록 조회

**서비스**: 세션에서 `chainNo`, `chain_ms_no` 자동 주입  
**요청**: `@RequestBody`

| No | TC | 예상값 | 비고 |
|----|----|-------|------|
| 2-1 | 정상 조회 | 해당 체인 소속 매장 사원 목록 | MMEMBSTB 체인 기준 필터 |
| 2-2 | USER_FG=NULL 매장사원 | userTypeNm=null 허용 | |
| 2-3 | 체인 소속 매장 없음 | `[]` | |
| 2-4 | 미인증 접근 | 302 | |

---

## 3. `/searchDetail/hq` — 본사 사원 상세 조회

**요청방식**: `@RequestParam` (form-data, NOT RequestBody)  
**파라미터**: `addUserId` (required, @NotBlank, @Size max=45)

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 3-1 | 정상 조회 | `addUserId=user1` | 단건 상세 정보, userTypeNm 매핑 |
| 3-2 | addUserId 빈값 | `addUserId=` | 400 (@NotBlank) |
| 3-3 | addUserId 46자 | 46자 문자열 | 400 (@Size max=45) |
| 3-4 | 존재하지 않는 ID | `addUserId=NOTEXIST` | `[]` 빈 리스트 |
| 3-5 | userType 매핑 | USER_FG 유효값 | userTypeNm 정상 세팅 |

---

## 4. `/searchDetail/shop` — 매장 사원 상세 조회

**파라미터**: `addUserId` (required, @NotBlank), `selectMsNo` (optional, defaultValue="")

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 4-1 | msNo 없음 | `addUserId=store_user1` | com_selectMsNo="" → 전체 |
| 4-2 | msNo 있음 | `addUserId=store_user1&selectMsNo=NC0007` | 특정 매장 소속 상세 |
| 4-3 | addUserId 빈값 | `addUserId=` | 400 (@NotBlank) |
| 4-4 | 존재하지 않는 매장코드 | `selectMsNo=XXXXX` | `[]` |

---

## 5. `/idDupChk` — ID 중복 체크

**서비스**: `dupIdchk()` → count > 0 → "dupl" / count=0 → "" 반환

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 5-1 | 중복 ID | `addUserId=admin` | `"dupl"` |
| 5-2 | 신규 ID | `addUserId=newuser_20260526` | `""` (빈 문자열) |
| 5-3 | addUserId 빈값 | `addUserId=` | 400 (@NotBlank) |
| 5-4 | idDupChk 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 6. `/userSave` — 사용자 등록 (일반)

**서비스 흐름**:
```
getEmpiId() → EMP_ID 채번
BCrypt encode("HMS" + yyyyMMdd + "!")
insertUser()
userRole != "" → insertUserRole() 추가 실행
```
**필수**: `addUserId, userNm, useYn, userFg, hqYn, orderFg, email`  
**선택**: `msNo, telNo, userRole, chainNo`

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 6-1 | 정상 등록 (userRole 없음) | `addUserId=newuser1&userNm=홍길동&useYn=Y&userFg=ST&hqYn=N&orderFg=0&email=t@t.com` | `{"hqYn":"N"}`, insertUserRole 미실행 |
| 6-2 | 정상 등록 (userRole 있음) | `...&userRole=ROLE_STORE` | insertUser + insertUserRole 실행 |
| 6-3 | addUserId 누락 | `addUserId=` | 400 (@NotBlank) |
| 6-4 | userNm 151자 | 151자 문자열 | 400 (@Size max=150) |
| 6-5 | 중복 addUserId | 이미 존재하는 ID | DB PK 오류, @Transactional 롤백 |
| 6-6 | 초기 PW 확인 | 등록 후 "HMS+오늘날짜+!" 로그인 | 로그인 성공 |
| 6-7 | getEmpiId null 반환 | EMP_ID Mapper 0건 반환 시 | EMP_ID=null로 INSERT → DB 제약 오류 확인 |

---

## 7. `/userAdminSave` — Admin 사용자 등록

**서비스**: `getAdminEmpiId()` → BCrypt PW → `insertAdminUser()`  
**필수**: `addUserId(@Size max=45), userNm(@Size max=150), email, userFg`  
**선택**: `telNo`  
**⚠️ userRole 파라미터 없음 → insertUserRole 분기 없음 (일반 userSave와 차이)**

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 7-1 | 정상 등록 | `addUserId=adminuser1&userNm=관리자&email=admin@t.com&userFg=ADMIN` | void (200 OK), DB 확인 |
| 7-2 | telNo 선택 포함 | `...&telNo=010-1234-5678` | void, telNo 저장 확인 |
| 7-3 | email 빈값 | `email=` | 400 (@NotBlank) |
| 7-4 | userNm 151자 | 151자 | 400 (@Size max=150) |
| 7-5 | 중복 addUserId | 기존 존재 ID | DB 오류, 롤백 |
| 7-6 | userRole 전달해도 무시 | `...&userRole=ROLE_ADMIN` | 파라미터 무시, insertUserRole 미실행 ★ |

---

## 8. `/IDDelete` — 사용자 삭제

**서비스 흐름**:
```
BCrypt.matches(입력PW, 세션PASSWORD)
  true  → hqYn="hq"  → ms_no_list = chain_ms_no (세션)
           hqYn="shop"→ ms_no_list = ms_no (파라미터)
           기타값     → ms_no_list 미설정 ★
           deleteUserTb(list) + deleteMlTb(list)
  false → chkFg="notcorr"
반환: returnMap에 hqYn 항상 추가
```
**필수**: `deluserId(@NotBlank), passWd(@NotBlank), hqYnDel(@NotBlank)`  
**선택**: `msNo`

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 8-1 | 본사 사원 삭제 (PW 일치) | `deluserId=user1&passWd=올바른PW&hqYnDel=hq` | `{"hqYn":"hq"}`, 삭제 확인 |
| 8-2 | 매장 사원 삭제 (PW 일치) | `deluserId=store1&passWd=올바른PW&hqYnDel=shop&msNo=NC0007` | `{"hqYn":"shop"}`, 삭제 확인 |
| 8-3 | **PW 불일치** | `passWd=틀린PW` | `{"chkFg":"notcorr","hqYn":"hq"}` |
| 8-4 | 다중 사원 삭제 | `deluserId=user1,user2,user3` | 3명 모두 삭제 (split(",") 반복) |
| 8-5 | 존재하지 않는 userId | `deluserId=NOTEXIST` | 200 OK (0건 삭제) |
| 8-6 | deluserId 빈값 | `deluserId=` | 400 (@NotBlank) |
| 8-7 | hqYn 이외값 | `hqYnDel=other` | ms_no_list 미설정 → Mapper WHERE 동작 확인 ★ |
| 8-8 | @Transactional 롤백 | deleteMlTb 중 오류 | deleteUserTb도 롤백 |

---

## 9. `/userUpdate` — 사원 정보 수정

**서비스 흐름**:
```
BCrypt.matches(passWd, 세션PASSWORD)
  true  → userUpdate() 실행
           userRole != "" → deleteUserMl() + updateUserRole()
  false → chkFg="notcorr"
```
**필수**: `editUserId(@Size max=45), chkpassWd, editNm(@Size max=150), edtuserFg, edtUseYn, hqYnEdit, orderFg, email`  
**선택**: `edtVendorCd, telNo, userRole`

> **[v2 보완]** **소스 344~345번** (`/userUpdate`): `passWd`와 `chkpassWd` 동일 값 이중 put ★  

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 9-1 | 정상 수정 (PW 일치, role 없음) | `editUserId=user1&chkpassWd=올바른PW&...&userRole=` | `{"hqYn":"..."}`, role 수정 안함 |
| 9-2 | 정상 수정 (PW 일치, role 있음) | `...&userRole=ROLE_STORE` | deleteUserMl + updateUserRole 실행 |
| 9-3 | **PW 불일치** | `chkpassWd=틀린PW` | `{"chkFg":"notcorr","hqYn":"..."}` |
| 9-4 | editUserId 빈값 | `editUserId=` | 400 (@NotBlank) |
| 9-5 | editNm 151자 | 151자 | 400 (@Size max=150) |
| 9-6 | 존재하지 않는 editUserId | `editUserId=NOTEXIST` | 200, 0건 UPDATE |

---

## 10. `/adminUserUpdate` — Admin 사원 수정

**서비스**: `userUpdate()` 호출 (9번과 동일 서비스)  
**컨트롤러 차이**:
- `orderFg` 항상 `"0"` 하드코딩 (파라미터로 받지 않음)
- `userRole` 파라미터 **없음** → `commandMap에 userRole 미설정` → `userUpdate()` 서비스 내 `"".equals(userRole)` → **role 수정 분기 절대 실행 안 됨** ★★
- `edtVendorCd` 파라미터 없음

**필수**: `editUserId(@Size max=45), chkpassWd, editNm(@Size max=150), edtuserFg, edtUseYn, email`  
**선택**: `telNo`

> **[v2 보완]** **소스 393번** (`/adminUserUpdate`): `commandMap.put("orderFg", "0")` 하드코딩 → TC 10-4 ✅ 정확  

> **[v2 보완]** **소스 386~396번** (`/adminUserUpdate`): `userRole` key 자체 미세팅 → `userUpdate()` 서비스 내 userRole 체크 분기 미실행 → TC 10-3 ✅ 정확

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 10-1 | 정상 수정 (PW 일치) | `editUserId=admin1&chkpassWd=올바른PW&editNm=관리자2&edtuserFg=ADMIN&edtUseYn=Y&email=a@a.com` | returnMap (hqYn 없음), DB UPDATE |
| 10-2 | **PW 불일치** | `chkpassWd=틀린PW` | `{"chkFg":"notcorr"}` |
| 10-3 | **userRole 전달해도 무시** | `...&userRole=ROLE_ADMIN` | 파라미터 무시, role 수정 미실행 ★ |
| 10-4 | orderFg 고정 확인 | `orderFg=999` 전달 | commandMap.orderFg="0" 고정 (파라미터 무시) ★ |

---

## 11. `/pwReset` — 비밀번호 초기화

**서비스**: BCrypt encode("HMS"+yyyyMMdd+"!") → resetPw() UPDATE → 원문 반환  
**필수**: `editUserId(@NotBlank)`

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 11-1 | 정상 초기화 | `editUserId=user1` | `"HMS20260526!"` (오늘 날짜) |
| 11-2 | 초기화 후 로그인 | 반환된 PW로 로그인 | 로그인 성공 |
| 11-3 | editUserId 빈값 | `editUserId=` | 400 (@NotBlank) |
| 11-4 | 존재하지 않는 userId | `editUserId=NOTEXIST` | 200 OK (0건 UPDATE) |
| 11-5 | 날짜 경계 | 23:59:59 초기화 후 00:00:01 로그인 | 날짜 바뀌면 PW 불일치 ★ |

---

## 12. `/moveEmp` — 사원 매장 이동

**서비스 흐름**:
```
getUsermltb()
  null     → instTempMenuList() (1회)
  not null → delTempMenuList() → instTempMenuList()
delEmpMenuList()
updEmp()
```
**컨트롤러 분기**: `selectStoreCd != "All"` → commandMap에 ms_no 추가  
**필수**: `moveUserId(@NotBlank), selectStoreCd(@NotBlank), nowStoreCd(@NotBlank), copyYn, tempCode`

> **[v2 보완]** **소스 458번** (`/moveEmp`): `!ms_no.equals("All")` → `ms_no`="All" 아니면 commandMap에 ms_no 추가 → TC 12-3 ✅ 정확

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 12-1 | 정상 이동 (임시메뉴 없음) | `moveUserId=user1&selectStoreCd=NC0007&nowStoreCd=NC0001&copyYn=N&tempCode=T001` | void, instTempMenuList 1회 |
| 12-2 | 정상 이동 (임시메뉴 있음) | 동일 | void, del→inst 순서 실행 |
| 12-3 | **selectStoreCd="All"** | `selectStoreCd=All` | commandMap에 ms_no 미추가 ★ |
| 12-4 | 특정 매장으로 이동 | `selectStoreCd=NC0007` | commandMap에 ms_no=NC0007 추가 |
| 12-5 | moveUserId 빈값 | `moveUserId=` | 400 (@NotBlank) |
| 12-6 | @Transactional 롤백 | updEmp() 오류 | delEmpMenuList()도 롤백 |

---

## 13. `/searchUser` — 메뉴복사용 사원 조회

**요청**: `@RequestBody`  
**containsKey 방어**: user_id, user_nm, ms_no 키 없으면 "" 처리

| No | TC | RequestBody | 예상값 |
|----|----|------------|-------|
| 13-1 | 전체 조회 | `{"flag":"all"}` | 전체 사원 목록 (user_id/user_nm/ms_no="") |
| 13-2 | user_id 필터 | `{"flag":"search","user_id":"user1"}` | user1 정보 |
| 13-3 | ms_no 필터 | `{"flag":"search","ms_no":"NC0007"}` | NC0007 소속 사원 |
| 13-4 | 키 없는 경우 | `{"flag":"all"}` (user_id 키 자체 없음) | containsKey false → "" 처리 (NPE 없음) |
| 13-5 | searchUser 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 14. `/copyMenu` — 사원 메뉴 복사

**서비스 실제 흐름 (typeChk=0 시)**:
```
[대상사원 수만큼 루프]
  delTempMenuList(commandMap with user_id=각 대상)
  instTempMenuList(commandMap)
[루프 완료 후 1회]
  delMenuList(commandMap)
  copyMenuList(commandMap)
```
**typeChk 분기**:
- 0 → copyMenu() 실행
- 2 → chkFg="Hq" (sType=HQ, tType≠HQ)
- 3 → chkFg="Admin" (sType=ADMIN, tType≠ADMIN)
- 4 → chkFg="Ms" (sType=기타, tType≠ST)
- flag=1 → **주석 처리됨, 사용 안 함**

**필수**: `sUserChk(@NotBlank), tUserChk[](required)`

> **[v2 보완]** **소스 515번** (`/copyMenu`): `tUserChk[]` → `required=true` → 미전달 시 **400** 발생  

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 14-1 | 정상 복사 (HQ→HQ) | `sUserChk=hq_user1&tUserChk[]=hq_user2` | `{"chkFg":""}`, 복사 완료 |
| 14-2 | 정상 복사 (ADMIN→ADMIN) | `sUserChk=admin1&tUserChk[]=admin2` | `{"chkFg":""}` |
| 14-3 | 정상 복사 (ST→ST) | `sUserChk=store1&tUserChk[]=store2` | `{"chkFg":""}` |
| 14-4 | **HQ→비HQ 오류** | `sUserChk=hq_user&tUserChk[]=store_user` | `{"chkFg":"Hq"}` |
| 14-5 | **ADMIN→비ADMIN 오류** | `sUserChk=admin_user&tUserChk[]=hq_user` | `{"chkFg":"Admin"}` |
| 14-6 | **ST→비ST 오류** | `sUserChk=store_user&tUserChk[]=hq_user` | `{"chkFg":"Ms"}` |
| 14-7 | 다수 대상 (1명 타입불일치) | `tUserChk[]=user2&tUserChk[]=hq_user` (2번째 타입 불일치) | break → `{"chkFg":"Ms"}` (나머지 미검사) ★ |
| 14-8 | 다수 대상 (모두 일치) | `tUserChk[]=store2&tUserChk[]=store3` | `{"chkFg":""}`, 2명 복사 |
| 14-9 | sUserChk 빈값 | `sUserChk=` | 400 (@NotBlank) |
| 14-10 | Mapper 순서 확인 | 대상 2명 복사 시 | delTemp→instTemp 2회, delMenu→copyMenu 1회 순서 검증 ★ |
| 14-11 | tUserChk[] 미전달 | `sUserChk=user1` (tUserChk 없음) | **400** (required=true) ★ |

---

## 15. `/selectRole` — 권한별 메뉴 조회

**파라미터**: `chainNo`(optional, ""), `hqYn`(optional, "")

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 15-1 | chainNo+hqYn=Y | `chainNo=C000&hqYn=Y` | HQ 권한 메뉴 목록 |
| 15-2 | chainNo 빈값 | `chainNo=` | 전체 반환 또는 빈 리스트 (defaultValue="") |
| 15-3 | hqYn=N | `hqYn=N` | 매장 권한 메뉴 |
| 15-4 | selectRole 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 16. `/unlock` — 계정 잠금 해제

**서비스**: `updateUnLock()` → ACCT_LOCK='N', AUTH_FAILURE_CNT=0  
**파라미터**: `userId`(optional, defaultValue=""), 세션에서 `loginUserId` 자동 주입

| No | TC | Request | 예상값 |
|----|----|---------|-------|
| 16-1 | 정상 해제 | `userId=locked_user` | void, ACCT_LOCK='N' 확인 |
| 16-2 | 이미 해제된 계정 | `userId=normal_user` | void, 0건 UPDATE |
| 16-3 | 존재하지 않는 userId | `userId=NOTEXIST` | void, 0건 UPDATE |
| 16-4 | userId 빈값 | `userId=` | void (defaultValue="") — 전체 해제 위험 확인 ★ |
| 16-5 | 해제 후 로그인 | 잠금 해제 → 로그인 | 로그인 성공 |
| 16-6 | unlock 감사 미기록 | 계정 해제 후 MMSLOGTB 확인 | 로그 없음 ★★ (보안 민감) |

---

## 서비스 핵심 분기 요약

```
deleteUserTb / userUpdate
├── BCrypt.matches(입력PW, 세션PW) == true
│   ├── 삭제/수정 실행
│   │   └── (userRole != "") → 역할 추가 처리 [userUpdate만 해당]
│   └── hqYn 분기 [deleteUserTb만 해당]
│       ├── "hq"   → ms_no_list = chain_ms_no (세션)
│       ├── "shop" → ms_no_list = ms_no (파라미터)
│       └── 기타   → ms_no_list 미설정 ★
└── false → chkFg="notcorr"

adminUserUpdate → userUpdate() 호출하지만 userRole 미전달 → role 수정 불가 ★

copyMenu (typeChk)
├── 0 → [대상사원 루프] delTemp→instTemp / [1회] delMenu→copyMenu
├── 2 → chkFg="Hq"
├── 3 → chkFg="Admin"
└── 4 → chkFg="Ms"

moveEmp
├── getUsermltb() == null → instTempMenuList (1회)
└── not null → delTempMenuList → instTempMenuList
    + selectStoreCd="All" → ms_no commandMap 미설정
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `MUSERSTB` | 로그인용 ADMIN 계정 (BCrypt PW), 삭제/수정 대상 계정, 잠금 계정 |
| `GETUSERMLTB` | USER_FG 코드→명칭 매핑, userRole 데이터 |
| `MMEMBSTB` | 체인/매장 기본 데이터 (NC0007 등) |
| `SECURETB` | 보안 정책 (잠금 임계치 등) |

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] MMEMBSTB (CUD 작업)
│   └── (Trigger) Tr_MMEMBS_T01
├── [테이블] MUSERSTB (CUD 작업)
│   └── (Trigger) Tr_MUSERS_T01
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
