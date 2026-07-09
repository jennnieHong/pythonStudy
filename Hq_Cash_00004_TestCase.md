# Hq_Cash_00004 — 월간지출계정관리 단위 테스트케이스

> **화면**: [HQ] 입출금관리 > 월간지출관리 > 월간지출계정관리 (hq_cash_00004)  
> **URL Prefix**: `POST /backoffice/data/hq/cash/hq_cash_00004`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **공통 전제**: 모든 요청은 HQ 권한 계정으로 **로그인된 세션** 필요 (`shopadmin` / `0000`)
> **DB 트리거 영향도**: TMACNCTB, TMACNTTB CUD 발생으로 관련 트리거 연쇄 동작함 (Depth 3 연쇄 전파)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `0008` | 테스트 체인 번호 (자동주입) |
| `ID` | `shopadmin` | 로그인 사용자 ID (자동주입) |

---

## 엔드포인트 목록 (8개)

| # | URL | 기능 | ServiceType | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/selectCodeList` | 계정 분류 목록 조회 | SELECT | TMACNCTB |
| 2 | `/selectDetailCodeList` | 계정 코드 목록 조회 | SELECT | TMACNTTB |
| 3 | `/codeSave` | 계정 분류 등록 | INSERT | TMACNCTB |
| 4 | `/codeUpdate` | 계정 분류 수정 | UPDATE | TMACNCTB |
| 5 | `/codeDel` | 계정 분류 삭제 (하위코드 체크) | DELETE | TMACNCTB |
| 6 | `/codeDtSave` | 계정 코드 등록 | INSERT | TMACNTTB |
| 7 | `/codeDtUpdate` | 계정 코드 수정 | UPDATE | TMACNTTB |
| 8 | `/codeDtDel` | 계정 코드 삭제 (사용 여부 체크) | DELETE | TMACNTTB |

---

## 1. `/selectCodeList` — 계정 분류 목록 조회

**서비스 로직**: 세션 chainNo → `selectCodeList()` (분류 acntFg NOT IN('0','1') 조건 쿼리)  
**RequestBody**: `{}`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 1-1 | 정상 조회 | chainNo=`0008`, 분류 2건 이상 존재 | `{}` | 계정 분류 List 반환 |
| 1-2 | 계정 미등록 체인 | chainNo=`9999` | `{}` | `[]` 빈 리스트 |
| 1-3 | 미인증 접근 | 세션 없음 | `{}` | 302 redirect |

---

## 2. `/selectDetailCodeList` — 계정 코드 목록 조회

**서비스 로직**: 세션 chainNo, acntFg → `selectDetailCodeList()`  
**RequestBody**: `{"acntFg":"2"}`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 2-1 | 정상 조회 | chainNo=`0008`, acntFg=`2` | `{"acntFg":"2"}` | 해당 분류의 하위 계정 코드 List 반환 |
| 2-2 | 코드가 없는 분류 조회 | chainNo=`0008`, acntFg=`9` | `{"acntFg":"9"}` | `[]` 빈 리스트 |

---

## 3. `/codeSave` — 계정 분류 등록

**서비스 로직**: 
```
selectChkCode(chainNo + acntFg)
├── codeChk > 0 → 중복 → return 0 (INSERT 미실행)
└── codeChk = 0 → 신규 → insertCodeList() → processTrigger() → return 1
```

**세션 주입**: `chainNo`, `userId`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 3-1 | 정상 신규 분류 등록 | chainNo=`0008` | `{"acntFg":"9","acntNm":"AI테스트분류"}` | `1` (저장 성공) |
| 3-2 | **acntFg 중복 등록** | chainNo=`0008` | `{"acntFg":"9","acntNm":"AI테스트분류"}` | `0` (중복 실패) |
| 3-3 | 2~9 범위를 벗어난 코드 등록 시도 | chainNo=`0008` | `{"acntFg":"1","acntNm":"테스트"}` | UI 단에서 차단 (`2~9번 이내의 코드로 등록하실 수 있습니다`) |

---

## 4. `/codeUpdate` — 계정 분류 수정

**서비스 로직**: `updateCodeList()` -> `processTrigger(U)` 실행  
**세션 주입**: `chainNo`, `userId`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 4-1 | 정상 분류명 수정 | chainNo=`0008` | `{"acntFg":"9","acntNm":"AI테스트분류_수정"}` | `1` (1건 UPDATE) |
| 4-2 | 존재하지 않는 acntFg | chainNo=`0008` | `{"acntFg":"8","acntNm":"없는코드"}` | `0` (0건 UPDATE) |

---

## 5. `/codeDel` — 계정 분류 삭제

**서비스 로직**:
```
deleteChk(chainNo + acntFg) -> 하위코드 수 조회
├── deleteChk > 0 → 하위코드 존재 → return 0 (DELETE 미실행)
└── deleteChk = 0 → deleteCodeList() → processTrigger(D) → return 1
```

**세션 주입**: `chainNo`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 5-1 | 정상 분류 삭제 | chainNo=`0008`, 하위코드 없음 | `{"acntFg":"9"}` | `1` (삭제 성공) |
| 5-2 | **하위코드 존재 시 삭제 시도** | chainNo=`0008`, 하위코드 1건 이상 | `{"acntFg":"9"}` | `0` (삭제 실패, 계정 코드를 먼저 삭제 필요) |

---

## 6. `/codeDtSave` — 계정 코드 등록

**서비스 로직**:
```
selectChkDtCode(chainNo + dtacntFg + acntCd)
├── codeChk > 0 → 중복 → return 0 (INSERT 미실행)
└── codeChk = 0 → insertDtCodeList() → processTrigger() → return 1
```

**세션 주입**: `chainNo`, `userId`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 6-1 | 정상 신규 코드 등록 | chainNo=`0008` | `{"dtacntFg":"9","acntCd":"49","acntCdNm":"AI코드테스트","msDtUseFg":"Y"}` | `1` (저장 성공) |
| 6-2 | **acntCd 중복 등록** | chainNo=`0008` | `{"dtacntFg":"9","acntCd":"49","acntCdNm":"AI코드테스트","msDtUseFg":"Y"}` | `0` (중복 실패) |

---

## 7. `/codeDtUpdate` — 계정 코드 수정

**서비스 로직**: `updateDtCodeList()` -> `processTrigger(U)` 실행  
**세션 주입**: `chainNo`, `userId`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 7-1 | 정상 코드명/사용여부 수정 | chainNo=`0008` | `{"dtacntFg":"9","acntCd":"49","acntCdNm":"AI코드테스트_수정","msDtUseFg":"Y"}` | `1` (1건 UPDATE) |

---

## 8. `/codeDtDel` — 계정 코드 삭제

**서비스 로직**:
```
deleteDtChk(chainNo + acntFg + acntCd) -> 전표/출납 등 내역에서 사용 중인지 조회 (MACCIOTB)
├── deleteDtChk > 0 → 사용 내역 있음 → return 0 (DELETE 미실행)
└── deleteDtChk = 0 → deleteDtCodeList() → processTrigger(D) → return 1
```

**세션 주입**: `chainNo`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 8-1 | 정상 코드 삭제 | chainNo=`0008`, 사용 내역 없음 | `{"acntFg":"9","acntCd":"49"}` | `1` (삭제 성공) |
| 8-2 | **사용 내역 존재 시 삭제 시도** | chainNo=`0008`, MACCIOTB에 내역 존재 | `{"acntFg":"9","acntCd":"49"}` | `0` (삭제 실패, 사용 중이어서 삭제 불가) |

---

## DB 트리거 연쇄 및 동기화 (Depth 3)

```
[계정 분류 CUD]
TMACNCTB (CUD)
  └─ Tr_TMACNC_T01_Service (1차 연쇄) -> 각 가맹점에 대해 MMACNCTB upsert/delete 실행
       └─ Tr_MMACNC_T01_Service (2차 연쇄) -> SSACNCTB 전송로그 INSERT (3차 연쇄)
            └─ MMSLOGTB (변경 로그 기록)

[계정 코드 CUD]
TMACNTTB (CUD)
  └─ Tr_TMACNT_T01_Service (1차 연쇄) -> 각 가맹점에 대해 MMACNTTB upsert/delete 실행
       └─ Tr_MMACNT_T01_Service (2차 연쇄) -> SSACNTTB 전송로그 INSERT (3차 연쇄)
            └─ MMSLOGTB (변경 로그 기록)
```
