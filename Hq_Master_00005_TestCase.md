# Hq_Master_00005 — 상품분류관리 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > 상품관리 > 상품분류관리  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00005`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **외부 연동**: `Tr_TMLCLS_T01_Service` (대), `Tr_TMMCLS_T01_Service` (중), `Tr_TMSCLS_T01_Service` (소)  
> **요청 방식 주의**: 조회(lClassList) = `@RequestBody`, 나머지 = `@RequestParam` (form-data)
> **DB 트리거 영향도**: TMMCLSTB, TMSCLSTB, TMLCLSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 |
| `chainHqYn` | `Y` | 본부 여부 (`Y`=본부, `N`=가맹점) |
| `ID` | `7249525SHOP` | 로그인 사용자 ID (CUD 시 필요) |

---

## 엔드포인트 목록 (7개)

| # | URL | 기능 | 요청 방식 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/lClassList` | 대분류 조회 | `@RequestBody` | SELECT | MMLCLSTB<br>TMLCLSTB |
| 2 | `/mClassList` | 중분류 조회 | `@RequestParam` | SELECT | MMMCLSTB<br>TMMCLSTB |
| 3 | `/sClassList` | 소분류 조회 | `@RequestParam` | SELECT | MMSCLSTB<br>TMSCLSTB |
| 4 | `/clsUpdateCheck` | 명칭 수정 전 중복 체크 | `@RequestParam` | SELECT | TGOODSTB |
| 5 | `/clsUpdate` | 분류 명칭 수정 (clsStatusFg 3분기) | `@RequestParam` | UPDATE | TGOODSTB |
| 6 | `/deleteClsCd` | 분류 삭제 (clsCdArr 길이로 분기) | `@RequestParam` | DELETE | TMLCLSTB |
| 7 | `/clsSave` | 분류 저장 (clsStatusFg 3분기) | `@RequestParam` | INSERT | TMLCLSTB<br>TMMCLSTB<br>TMSCLSTB |

---

## 1. `/lClassList` — 대분류 조회 (`@RequestBody`)

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainNo=`C001`, chainHqYn=`Y` | 대분류 3건 | `{}` | 대분류 List 3건 |
| 1-2 | chainNo=`C001`, chainHqYn=`N` | 대분류 3건 | `{}` | chainHqYn=N 조건 적용 결과 |
| 1-3 | chainNo=`C001` | 대분류 없음 | `{}` | `[]` |
| 1-4 | body 없는 POST 요청 | Content-Type=application/json, body 없음 | `@RequestBody` 파싱 실패 → **400** ★ |

---

## 2. `/mClassList` — 중분류 조회 (`@RequestParam`, `lclsCd` 필수)

**제약**: `lclsCd` — `@NotBlank` + `@Size(min=3, max=3)`

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 2-1 | chainNo=`C001`, chainHqYn=`Y` | 중분류 3건 | `lclsCd=L01` | 중분류 List |
| 2-2 | chainNo=`C001` | 중분류 없음 | `lclsCd=L01` | `[]` |
| 2-3 | - | - | `lclsCd=` (빈값) | 400 (@NotBlank) |
| 2-4 | - | - | `lclsCd=LO` (2자리) | 400 (@Size min=3) |
| 2-5 | - | - | `lclsCd=LONG` (4자리) | 400 (@Size max=3) |
| 2-6 | - | - | `lclsCd` 없음 | 400 (required=true) |

---

## 3. `/sClassList` — 소분류 조회 (`@RequestParam`, `lclsCd`+`mclsCd` 필수)

**제약**: `lclsCd`, `mclsCd` 각각 `@NotBlank` + `@Size(min=3, max=3)`

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 3-1 | chainNo=`C001`, chainHqYn=`Y` | 소분류 3건 | `lclsCd=L01&mclsCd=M01` | 소분류 List |
| 3-2 | - | - | `mclsCd=` (빈값) | 400 (@NotBlank) |
| 3-3 | - | - | `mclsCd=MO` (2자리) | 400 (@Size) |

---

## 4. `/clsUpdateCheck` — 명칭 수정 전 중복 체크

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 4-1 | chainNo=`C001`, chainHqYn=`Y` | clsNm 중복 없음 | `clsStatusFg=lcls&clsCd=L01&clsNm=새분류명` | `0` |
| 4-2 | chainNo=`C001` | clsNm 중복 있음 | `clsStatusFg=mcls&clsCd=M01&clsNm=기존명칭&lclaCd=L01` | `> 0` |
| 4-3 | - | - | `clsStatusFg=` (빈값) | 400 (@NotBlank) |
| 4-4 | - | - | `clsNm=` (빈값) | 400 (@NotBlank) |
| 4-5 | clsUpdateCheck 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 5. `/clsUpdate` — 분류 명칭 수정

**서비스 로직 (`updateClsCd` switch)**:
```
clsStatusFg = "mcls" (중분류)
  lclassCd=lclaCd, mclassCd=clsCd, mclassNm=clsNm
  → TriggerUtil "U" → tr_TMMCLS_T01 → updateMclassCd → processTrigger

clsStatusFg = "scls" (소분류)
  lclassCd=lclaCd, mclassCd=mclaCd, sclassCd=clsCd, sclassNm=clsNm
  → TriggerUtil "U" → tr_TMSCLS_T01 → updateSclassCd → processTrigger

default (대분류)
  lclassCd=clsCd, lclassNm=clsNm
  → TriggerUtil "U" → tr_TMLCLS_T01 → updateClsCd → processTrigger
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 5-1 | chainNo=`C001`, ID=`7249525SHOP`, chainHqYn=`Y` | L01 대분류 존재 | `clsStatusFg=lcls&clsCd=L01&clsNm=수정대분류` | TMLCLS 트리거 + updateClsCd |
| 5-2 | chainNo=`C001`, ID=`7249525SHOP` | M01 중분류 존재 | `clsStatusFg=mcls&clsCd=M01&clsNm=수정중분류&lclaCd=L01` | TMMCLS 트리거 + updateMclassCd |
| 5-3 | chainNo=`C001`, ID=`7249525SHOP` | S01 소분류 존재 | `clsStatusFg=scls&clsCd=S01&clsNm=수정소분류&lclaCd=L01&mclaCd=M01` | TMSCLS 트리거 + updateSclassCd |
| 5-4 | - | - | `clsStatusFg=` (빈값) | 400 (@NotBlank) |
| 5-5 | - | - | `clsNm=` (빈값) | 400 (@NotBlank) |
| 5-6 | - | - | `clsNm=` 31자 초과 | 400 (@Size max=30) |
| 5-7 | - | - | clsStatusFg=`scls`, clsCd=빈값 (`defaultValue=""`) | @NotBlank but required=false → 400 확인 필요 ★ |
| 5-8 | clsUpdate 성공 응답 | 정상 처리 | HTTP 200 + **빈 바디** (void 반환) ★ |

---

## 6. `/deleteClsCd` — 분류 삭제

**서비스 로직 (`deleteClsCd` switch — clsCdArr 배열 길이 기준)**:
```
clsCdArr.length = 2 (중분류 삭제)
  clsCdArr[0]=lclassCd, clsCdArr[1]=mclassCd
  → TriggerUtil "D" → tr_TMMCLS_T01.getOldValues → deleteMclassCd → processTrigger

clsCdArr.length = 3 (소분류 삭제)
  clsCdArr[0]=lclassCd, clsCdArr[1]=mclassCd, clsCdArr[2]=sclassCd
  → TriggerUtil "D" → tr_TMSCLS_T01.getOldValues → deleteSclassCd → processTrigger

default (대분류 삭제, length=1 또는 기타)
  clsCdArr[0]=lclassCd
  → TriggerUtil "D" → tr_TMLCLS_T01.getOldValues → deleteClsCd → processTrigger
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 6-1 | chainNo=`C001`, chainHqYn=`Y` | L01 대분류 존재 | `clsCdArr[]=L01` (1건) | TMLCLS 트리거 + deleteClsCd(대) |
| 6-2 | chainNo=`C001` | L01/M01 존재 | `clsCdArr[]=L01&clsCdArr[]=M01` (2건) | TMMCLS 트리거 + deleteMclassCd |
| 6-3 | chainNo=`C001` | L01/M01/S01 존재 | `clsCdArr[]=L01&clsCdArr[]=M01&clsCdArr[]=S01` (3건) | TMSCLS 트리거 + deleteSclassCd |
| 6-4 | chainNo=`C001` | L01 하위에 중/소분류 있음 | `clsCdArr[]=L01` | 하위 존재 시 DB 제약 오류 가능 |
| 6-5 | - | - | `clsCdArr[]` 없음 | 400 (@NotEmpty) |
| 6-6 | - | - | @Transactional: processTrigger 오류 | delete 롤백 |
| 6-7 | deleteClsCd 성공 응답 | 정상 삭제 | HTTP 200 + **빈 바디** (void) ★ |

---

## 7. `/clsSave` — 분류 저장

**서비스 로직 3단계 (clsStatusFg switch 3회)**:
```
1. maxClsCd(commandMap, clsStatusFg)  → 채번
   mcls: maxMclassCd / scls: maxSclassCd / default: maxClsCd

2. chkClsCd(commandMap, clsStatusFg) → 중복 체크
   > 0 → chkFg="dupl" 반환

3. insertClsCd(commandMap, clsStatusFg) → 삽입 + 트리거
   mcls: TMMCLS A트리거 + insertMclassCd
   scls: TMSCLS A트리거 + insertSclassCd
   default: TMLCLS A트리거 + insertClsCd
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 7-1 | chainNo=`C001`, ID=`7249525SHOP`, chainHqYn=`Y` | 대분류 없음 | `clsStatusFg=lcls&clsNm=신규대분류` | `""` + TMLCLS 트리거 + insertClsCd |
| 7-2 | chainNo=`C001`, ID=`7249525SHOP` | L01 존재 | `clsStatusFg=mcls&clsNm=신규중분류&lclaCd=L01` | `""` + TMMCLS 트리거 + insertMclassCd |
| 7-3 | chainNo=`C001`, ID=`7249525SHOP` | L01/M01 존재 | `clsStatusFg=scls&clsNm=신규소분류&lclaCd=L01&mclaCd=M01` | `""` + TMSCLS 트리거 + insertSclassCd |
| 7-4 | chainNo=`C001` | **동일 분류명 이미 존재** | `clsStatusFg=lcls&clsNm=기존대분류` | `"dupl"` (삽입 없음) |
| 7-5 | - | - | @Transactional: processTrigger 오류 | insertClsCd 롤백 |

---

## clsStatusFg — 분류 구분 키 정리

| clsStatusFg | 대상 | Mapper | 트리거 서비스 |
|-------------|------|--------|-------------|
| `"lcls"` (default) | 대분류 | `insertClsCd`, `updateClsCd`, `deleteClsCd` | `Tr_TMLCLS_T01_Service` |
| `"mcls"` | 중분류 | `insertMclassCd`, `updateMclassCd`, `deleteMclassCd` | `Tr_TMMCLS_T01_Service` |
| `"scls"` | 소분류 | `insertSclassCd`, `updateSclassCd`, `deleteSclassCd` | `Tr_TMSCLS_T01_Service` |

---

## deleteClsCd clsCdArr 배열 길이 → 분기 정리

| clsCdArr 길이 | 의미 | 트리거 |
|--------------|------|--------|
| 1 (default) | 대분류 삭제 | Tr_TMLCLS_T01 |
| 2 | 중분류 삭제 | Tr_TMMCLS_T01 |
| 3 | 소분류 삭제 | Tr_TMSCLS_T01 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00005"
$h  = @{"Content-Type"="application/json"}
$f  = "application/x-www-form-urlencoded"

# 1. 대분류 조회 (@RequestBody)
Invoke-RestMethod -Uri "$base/lClassList" -Method POST -Body '{}' -Headers $h -WebSession $session

# 2. 중분류 조회 (@RequestParam)
Invoke-RestMethod -Uri "$base/mClassList" -Method POST -ContentType $f `
  -Body "lclsCd=L01" -WebSession $session

# 2-3. lclsCd 빈값 → 400
Invoke-RestMethod -Uri "$base/mClassList" -Method POST -ContentType $f `
  -Body "lclsCd=" -WebSession $session

# 6-1. 대분류 삭제 (clsCdArr 1건 → TMLCLS 트리거)
Invoke-RestMethod -Uri "$base/deleteClsCd" -Method POST -ContentType $f `
  -Body "clsCdArr[]=L01" -WebSession $session

# 6-2. 중분류 삭제 (clsCdArr 2건 → TMMCLS 트리거)
Invoke-RestMethod -Uri "$base/deleteClsCd" -Method POST -ContentType $f `
  -Body "clsCdArr[]=L01&clsCdArr[]=M01" -WebSession $session

# 7-1. 대분류 신규 등록
Invoke-RestMethod -Uri "$base/clsSave" -Method POST -ContentType $f `
  -Body "clsStatusFg=lcls&clsNm=신규대분류" -WebSession $session
# 예상: "" (성공) 또는 "dupl" (중복)

# 7-2. 중분류 신규 등록
Invoke-RestMethod -Uri "$base/clsSave" -Method POST -ContentType $f `
  -Body "clsStatusFg=mcls&clsNm=신규중분류&lclaCd=L01" -WebSession $session

# 5-1. 대분류 명칭 수정
Invoke-RestMethod -Uri "$base/clsUpdate" -Method POST -ContentType $f `
  -Body "clsStatusFg=lcls&clsCd=L01&clsNm=수정대분류" -WebSession $session
```

---

## 주요 검증 포인트

```
□ lClassList — @RequestBody (JSON), 나머지 7개 — @RequestParam (form-data) 혼용 구조
□ mClassList / sClassList — lclsCd, mclsCd 정확히 3자리 (@Size(min=3,max=3))
□ deleteClsCd — clsCdArr 배열 길이로 대/중/소 분기 (length=1→대, 2→중, 3→소)
□ clsUpdate.clsCd — required=false지만 @NotBlank 동시 선언 → 빈값 가능 여부 테스트 필요 ★
□ clsSave — maxClsCd → chkClsCd → insertClsCd 3단계 switch 순차 실행
□ 트리거 연동 — 대/중/소별 별도 Trigger 서비스 (TMLCLS/TMMCLS/TMSCLS) 연동 확인
□ @Transactional — 트리거 processTrigger 실패 시 insert/delete 롤백
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] TMLCLSTB (CUD 작업)
│   └── (Trigger) Tr_TMLCLS_T01
├── [테이블] TMMCLSTB (CUD 작업)
│   └── (Trigger) Tr_TMMCLS_T01
└── [테이블] TMSCLSTB (CUD 작업)
    └── (Trigger) Tr_TMSCLS_T01
```
