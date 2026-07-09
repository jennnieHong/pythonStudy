# Hq_Cash_00001 — 입출금계정 관리 단위 테스트케이스

> **화면**: [HQ] 현금관리 > 입출금계정 관리  
> **URL Prefix**: `POST /backoffice/data/hq/cash/hq_cash_00001`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **공통 전제**: 모든 요청은 HQ 권한 계정으로 **로그인된 세션** 필요
> **DB 트리거 영향도**: TMACNTTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 테스트 체인 번호 (자동주입) |
| `ID` | `7249525SHOP` | 로그인 사용자 ID (자동주입) |

> 세션 없이 호출 시 → Spring Security가 **302 redirect** 처리

---

## 엔드포인트 목록 (5개)

| # | URL | 기능 | ServiceType  관련 테이블 |
|---|---|---|---|
| 1 | `/selectCodeList` | 입금 계정 목록 조회 | SELECT | TMACNTTB  |
| 2 | `/selectCodeList2` | 출금 계정 목록 조회 | SELECT | TMACNTTB  |
| 3 | `/codeSave` | 계정 등록 (중복 체크 포함) | INSERT | TMACNTTB  |
| 4 | `/codeUpdate` | 계정 수정 | UPDATE | TMACNTTB  |
| 5 | `/codeDel` | 계정 삭제 (사용중 체크, 다건) | DELETE | MACCIOTB<br>TMACNTTB  |

---

## 1. `/selectCodeList` — 입금 계정 조회

**서비스 로직**: 세션 chainNo → `selectCodeList()` (입금 acntFg 조건 쿼리)  
**RequestBody**: 없음 (body는 `{}` 전송, 실제 파라미터는 세션에서만 주입)

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 1-1 | 정상 조회 | chainNo=`C001`, 입금계정 3건 등록됨 | `{}` | 입금 계정 List 3건 반환 |
| 1-2 | 계정 미등록 체인 | chainNo=`C999` (계정 없음) | `{}` | `[]` 빈 리스트 |
| 1-3 | 미인증 접근 | 세션 없음 | `{}` | 302 redirect |
| 1-4 | body 없이 호출 | Content-Type 없음, body 미전달 | 400 오류 ★ |

---

## 2. `/selectCodeList2` — 출금 계정 조회

**서비스 로직**: 세션 chainNo → `selectCodeList2()` (출금 acntFg 조건 쿼리)  
**RequestBody**: 없음 (body `{}`)

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 2-1 | 정상 조회 | chainNo=`C001`, 출금계정 2건 등록됨 | `{}` | 출금 계정 List 2건 반환 |
| 2-2 | 입금/출금 교차 검증 | chainNo=`C001` | selectCodeList vs selectCodeList2 | 각각 다른 acntFg 데이터 반환하는지 확인 |
| 2-3 | 계정 미등록 체인 | chainNo=`C999` | `{}` | `[]` |
| 2-4 | body 없이 호출 | 동일 | 400 오류 ★ |
| 2-5 | 감사 로그 미기록 | selectCodeList2 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 3. `/codeSave` — 계정 등록

**서비스 분기**:
```
dupCdChk(chainNo + acntFg + acntCd)
├── codeChk > 0 → 중복 → return 0 (INSERT 미실행)
└── codeChk = 0 → 신규 → insertCodeList() → return 1
```

**파라미터 방어 처리**: `map.containsKey(key) ? map.get(key) : ""`  
**세션 주입**: `chainNo`, `userId`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 3-1 | 정상 신규 등록 | chainNo=`C001`, ID=`7249525SHOP` | `{"acntFg":"0","acntCd":"A001","acntNm":"현금입금","statusFg":"Y"}` | `1` |
| 3-2 | **acntCd 중복 등록** | chainNo=`C001`, A001 이미 존재 | `{"acntFg":"0","acntCd":"A001","acntNm":"현금입금","statusFg":"Y"}` | `0` (INSERT 미실행) |
| 3-3 | 동일 acntCd, 다른 acntFg | chainNo=`C001`, acntCd=A001이 acntFg=0으로 존재 | `{"acntFg":"1","acntCd":"A001","acntNm":"현금출금","statusFg":"Y"}` | `1` (별도 계정으로 등록 성공) |
| 3-4 | **acntFg 키 미포함** | chainNo=`C001` | `{"acntCd":"A002","acntNm":"기타입금","statusFg":"Y"}` | acntFg=`""` 처리, dupCdChk에 `""` 조건 적용 |
| 3-5 | **acntNm 키 미포함** | chainNo=`C001` | `{"acntFg":"0","acntCd":"A003","statusFg":"Y"}` | acntNm=`""` 로 INSERT (이름 없이 저장) |
| 3-6 | **acntCd 키 미포함** | chainNo=`C001` | `{"acntFg":"0","acntNm":"테스트"}` | acntCd=`""` → dupCdChk 대상 `""`, 정상 등록 또는 중복 |
| 3-7 | @Transactional 롤백 | chainNo=`C001` | DB 제약조건 위반값 입력 | insertCodeList 오류 → 롤백 |

---

## 4. `/codeUpdate` — 계정 수정

**서비스 로직**: 중복 체크 없이 단순 `updateCodeList()` 실행  
**세션 주입**: `chainNo`, `userId`  
**파라미터 방어 처리**: `map.containsKey()` 동일하게 적용

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 4-1 | 정상 명칭 수정 | chainNo=`C001`, A001 존재 | `{"acntFg":"0","acntCd":"A001","acntNm":"현금입금(수정)"}` | `1` (1건 UPDATE) |
| 4-2 | 존재하지 않는 acntCd | chainNo=`C001` | `{"acntFg":"0","acntCd":"XXXXX","acntNm":"없는코드"}` | `0` (0건 UPDATE) |
| 4-3 | **acntNm 키 미포함** | chainNo=`C001`, A001 존재 | `{"acntFg":"0","acntCd":"A001"}` | acntNm=`""` 로 덮어씌워짐 (의도치 않은 이름 삭제 위험) |
| 4-4 | 다른 체인의 계정 수정 시도 | chainNo=`C001` (세션) | `{"acntFg":"0","acntCd":"B001"}` (C002 체인 계정) | `0` (체인 조건 불일치, UPDATE 안 됨) |

---

## 5. `/codeDel` — 계정 삭제

**서비스 분기** (배열 내 건별 독립 처리):
```
delAcntCdArr 배열 순회
  각 acntCd[i] 에 대해:
  ├── useCdChk(chainNo + acntFg + acntCd[i]) > 0 → 사용중 → fail++
  └── useCdChk = 0 → deleteCode([addMap]) → succ++
반환: {"fail": N, "succ": M}
```

**세션 주입**: `chainNo`  
**RequestBody 필드**: `delAcntCdArr` (List<String>), `acntFg`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 5-1 | 단건 정상 삭제 | chainNo=`C001`, A001 미사용 | `{"delAcntCdArr":["A001"],"acntFg":"0"}` | `{"fail":0,"succ":1}`, 본사 및 가맹점 MMACNTTB 동시 전파 삭제 완료 (조회 후 삭제 순서 오류 해결) |
| 5-2 | **단건 사용중 삭제 시도** | chainNo=`C001`, A001 현재 입출금 내역 있음 | `{"delAcntCdArr":["A001"],"acntFg":"0"}` | `{"fail":1,"succ":0}`, DB 삭제 안 됨 |
| 5-3 | 다건 전체 미사용 | chainNo=`C001`, A001·A002 미사용 | `{"delAcntCdArr":["A001","A002"],"acntFg":"0"}` | `{"fail":0,"succ":2}` |
| 5-4 | **다건 혼합 (일부 사용중)** | A001=미사용, A002=사용중 | `{"delAcntCdArr":["A001","A002"],"acntFg":"0"}` | `{"fail":1,"succ":1}`, A001만 삭제 |
| 5-5 | 다건 전체 사용중 | A001·A002 모두 사용중 | `{"delAcntCdArr":["A001","A002"],"acntFg":"0"}` | `{"fail":2,"succ":0}` |
| 5-6 | 존재하지 않는 코드 삭제 | chainNo=`C001` | `{"delAcntCdArr":["XXXXX"],"acntFg":"0"}` | useCdChk=0 → deleteCode 실행 (0건), `{"fail":0,"succ":1}` |
| 5-7 | 빈 배열 | chainNo=`C001` | `{"delAcntCdArr":[],"acntFg":"0"}` | 순회 없음, `{"fail":0,"succ":0}` |
| 5-8 | **@Transactional 롤백** | chainNo=`C001` | deleteCode 내부 오류 유발 | 해당 건 롤백, succ로 카운트된 이전 건도 롤백 여부 확인 |
| 5-9 | **delAcntCdArr 키 누락** | `{"acntFg":"0"}` | NPE → 500 ★ (현재 버그) |
| 5-10 | **acntFg 키 누락** | `{"delAcntCdArr":["A001"]}` | `map.get("acntFg")` → null → addMap에 null 주입 |
| 5-11 | **다건 삭제 (3건) [해결 완료]** | `["A001","A002","A003"]` 모두 미사용 | succ=3이고 deleteCode(list) 1회만 벌크로 실행되어 루프 내 중복 쿼리 없음 |
| 5-12 | 단건 삭제 | `["A001"]` | list=1건, deleteCode 1회 → 정상 |

---

## 서비스 핵심 분기 요약

```
codeSave (insertCodeList)
├── dupCdChk(chainNo + acntFg + acntCd) > 0 → return 0 (중복)
└── dupCdChk = 0 → insertCodeList() → return 1

codeDel (deleteCode) — 다건 벌크 처리
├── useCdChk > 0 → fail++ (사용중, 삭제 안 함)
└── useCdChk = 0 → list.add 및 조회 백업 후 루프 밖에서 deleteCode(list) 실행 ➔ succ++
반환: {"fail": N, "succ": M}
```

---

## PowerShell 테스트 명령

```powershell
# 세션 로그인 (선행 필수 — chainNo=C001 체인 admin 계정)
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/cash/hq_cash_00001"
$h = @{"Content-Type"="application/json"}

# 1. 입금 계정 목록 조회
Invoke-RestMethod -Uri "$base/selectCodeList" -Method POST `
  -Body '{}' -Headers $h -WebSession $session

# 2. 출금 계정 목록 조회
Invoke-RestMethod -Uri "$base/selectCodeList2" -Method POST `
  -Body '{}' -Headers $h -WebSession $session

# 3-1. 신규 등록
Invoke-RestMethod -Uri "$base/codeSave" -Method POST `
  -Body '{"acntFg":"0","acntCd":"TEST01","acntNm":"테스트입금","statusFg":"Y"}' `
  -Headers $h -WebSession $session
# 예상: 1

# 3-2. 중복 등록 (동일 body 재전송)
Invoke-RestMethod -Uri "$base/codeSave" -Method POST `
  -Body '{"acntFg":"0","acntCd":"TEST01","acntNm":"테스트입금","statusFg":"Y"}' `
  -Headers $h -WebSession $session
# 예상: 0 (중복)

# 4-1. 계정 명칭 수정
Invoke-RestMethod -Uri "$base/codeUpdate" -Method POST `
  -Body '{"acntFg":"0","acntCd":"TEST01","acntNm":"수정입금"}' `
  -Headers $h -WebSession $session
# 예상: 1

# 4-3. acntNm 키 미포함 (이름 공백 덮어씌워짐 위험)
Invoke-RestMethod -Uri "$base/codeUpdate" -Method POST `
  -Body '{"acntFg":"0","acntCd":"TEST01"}' `
  -Headers $h -WebSession $session
# 예상: 1, DB에서 acntNm="" 확인 필요

# 5-1. 미사용 계정 단건 삭제
Invoke-RestMethod -Uri "$base/codeDel" -Method POST `
  -Body '{"delAcntCdArr":["TEST01"],"acntFg":"0"}' `
  -Headers $h -WebSession $session
# 예상: {"fail":0,"succ":1}

# 5-2. 사용중 계정 삭제 시도 (INUSE01은 입출금 내역 있는 코드)
Invoke-RestMethod -Uri "$base/codeDel" -Method POST `
  -Body '{"delAcntCdArr":["INUSE01"],"acntFg":"0"}' `
  -Headers $h -WebSession $session
# 예상: {"fail":1,"succ":0}

# 5-4. 혼합 삭제 (TEST01=미사용, INUSE01=사용중)
Invoke-RestMethod -Uri "$base/codeDel" -Method POST `
  -Body '{"delAcntCdArr":["TEST01","INUSE01"],"acntFg":"0"}' `
  -Headers $h -WebSession $session
# 예상: {"fail":1,"succ":1}
```
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `MCASHATNSTB` | chainNo=C001의 입금(acntFg=0) / 출금(acntFg=1) 계정 각 2건 이상 |
| `MCASHIOITB` | 사용중 계정 1건 이상 (useCdChk 체크용, INUSE01) |
| `MMCHATB` | chainNo=C001 체인 마스터 |
| `MUSERSTB` | 7249525SHOP 계정 (BCrypt PW: 0000) |

---

## 주요 검증 포인트

```
□ selectCodeList vs selectCodeList2 — 각각 입금/출금 acntFg만 반환하는지 교차 검증
□ codeSave — 3중 키(chainNo+acntFg+acntCd) 기준 중복 체크 확인
□ codeSave containsKey — 키 누락 시 "" 기본값 저장, 의도치 않은 빈값 INSERT 주의
□ codeUpdate — 중복 체크 없음, acntNm 키 누락 시 "" 덮어쓰기 위험
□ codeDel — 혼합 결과(fail+succ 동시) 반환 확인, UI에서 메시지 처리 검증
□ codeDel @Transactional — 롤백 범위 확인 (이전 succ 건 포함 여부)
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] TMACNTTB (CUD 작업)
│   ├── (Trigger) Tr_TMACNT_T01
└── [공통 영향 테이블 및 호출]
    ├── MMACNTTB [가맹점 입출금 계정]
    ├── MMSLOGTB [MASTER LOG]
    └── [PROCEDURE] SUB_MASTER_P (MMACNTTB)
```

---

## 6. 브라우저 E2E 테스트 수행 결과

- **E2E 테스트 스크립트**: `D:\hmTest\backoffice\test_hq_cash_00001.py` (Playwright 구동)
- **테스트 시나리오 및 판정**:
  1. `shopadmin` 계정(PW: `0000`)으로 로그인 수행 (이중 로그인 경고 창 자동 통과) ✅ **PASS**
  2. 입출금계정 관리 화면 진입 -> '계정추가' 버튼 클릭 -> 신규 계정 코드 `99` 및 명칭 `테스트입금` 등록 ✅ **PASS**
     - **DB 검증 (Depth 3 동기화)**:
       - [1] `TMACNTTB` (본사) 레코드 정상 등록 확인 ✅
       - [2] 트리거 `Tr_TMACNT_T01` 연쇄 동작으로 `MMACNTTB` (가맹점) 레코드들 정상 복사 확인 ✅
       - [3] `SSACNTTB` (가맹점 전송용)에 전송 로그 `PROC_FG = 'A'` 등록 확인 ✅
       - [4] `MMSLOGTB` (로깅)에 마스터 변경 로그 정상 적재 확인 ✅
  3. 계정 정보 수정 (그리드에서 `테스트입금` 행 클릭 -> 명칭 `수정입금` 변경 후 저장) ✅ **PASS**
     - *주의*: 한글 글자당 3바이트로 계산하는 프론트엔드 바이트 체크 규칙에 의해, 20Byte 한계를 넘지 않도록 `테스트입금`(15Byte) 및 `수정입금`(12Byte) 명칭을 사용하여 유효성 검증 우회.
     - **DB 검증 (Depth 3 동기화)**:
       - [1] `TMACNTTB` (본사) 레코드의 명칭이 `수정입금`으로 정상 UPDATE 확인 ✅
       - [2] `MMACNTTB` (가맹점)의 계정명이 `수정입금`으로 정상 UPDATE 확인 ✅
       - [3] `SSACNTTB` (가맹점 전송용)에 전송 로그 `PROC_FG = 'U'` 등록 확인 ✅
       - [4] `MMSLOGTB` (로깅)에 마스터 변경 로그 정상 적재 확인 ✅
  4. 계정 삭제 (목록 체크박스 선택 -> '계정삭제' 버튼 클릭 -> 확인 모달 승인하여 삭제 완료) ✅ **PASS**
     - **DB 검증 (Depth 3 동기화)**:
       - [1] `TMACNTTB` (본사) 레코드 삭제 완료 확인 ✅
       - [2] `MMACNTTB` (가맹점) 레코드 삭제 완료 확인 (조회 후 삭제 순서 버그 해결 검증) ✅
       - [3] `SSACNTTB` (가맹점 전송용)에 전송 로그 `PROC_FG = 'D'` 등록 확인 ✅
       - [4] `MMSLOGTB` (로깅)에 마스터 변경 로그 정상 적재 확인 ✅

- **특이사항 및 DB 무결성 제약**:
  - `hmsfns.MACCIOTB` (현금 시재 입출금 및 지출 전표 실적 테이블)에 이력이 존재하는 코드는 무결성 제약 조건(`useCdChk` 룰)에 의해 삭제가 불가능하게 차단되는 사양이 정상 적용되어 있습니다. (실제 사용 중인 계정 삭제 시 `fail: 1, succ: 0` 결과 반환 확인)

