# St_Cash_00004 — 월간지출 내역 등록 단위 테스트케이스

> **화면**: [ST] 현금 > 월간지출 내역 등록  
> **URL Prefix**: `POST /backoffice/data/st/cash/st_cash_00004`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식**: 전 엔드포인트 `@RequestBody`  
> **특이사항**: `@Validated` 없음 — Bean Validation 미적용
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## St_Cash_00001 vs St_Cash_00004 비교

| 항목 | St_Cash_00001 (입출금 내역) | St_Cash_00004 (월간지출 내역) |
|------|--------------------------|---------------------------|
| 계정 콤보 | `selectAcntCd` (1개) | `selectAcntFg` + `selectAcntCd` **(2개)** |
| cashSave 파라미터 | vatFg/vat/custCd 포함 | **vatFg/vat/custCd 없음** (월간지출 특성) |
| cashUpdate 파라미터 | vat/custCd 포함 | **vat/custCd 없음** |
| cashDel 서비스 구조 | 루프 내 list 누적 (버그) | **accioNoList 한 번에 IN절 삭제** (개선됨) ★ |
| 세션 `chainNo` | cashSave | cashSave 동일 |

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `msNo` | `MS001` | selectAcntFg, selectAcntCd, selectMmaList, cashSave, cashUpdate, cashDel |
| `chainNo` | `C001` | cashSave |
| `ID` | `I000449s` | cashSave, cashUpdate, cashDel |

---

## 엔드포인트 목록 (6개)

| # | URL | 기능 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/selectAcntFg` | 월간지출 계정 구분(FG) 콤보 조회 | `HashMap` (acntFgList) | SELECT | MMACNCTB  |
| 2 | `/selectAcntCd` | 월간지출 계정 코드(CD) 콤보 조회 | `HashMap` (acntCdList) | SELECT | MMACNTTB  |
| 3 | `/selectMmaList` | 월간지출 내역 조회 | `List<Map>` | SELECT | MACCIOTB<br>MMACNCTB<br>MMACNTTB  |
| 4 | `/cashSave` | 월간지출 내역 등록 (건수 제한 99건) | `int` | INSERT | MACCIOTB  |
| 5 | `/cashUpdate` | 월간지출 내역 수정 | `int` | UPDATE | MACCIOTB  |
| 6 | `/cashDel` | 월간지출 내역 삭제 (IN절 일괄 삭제) | `Map` | DELETE | MACCIOTB  |

---

## 1. `/selectAcntFg` — 계정 구분 콤보 조회

**서비스**: `LinkedHashMap` → `{"acntFgList": [...]}`  
**세션**: `msNo` 자동 주입 (St_Cash_00001의 `chainNo`와 달리 `msNo` 사용)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | msNo=`MS001` | `{}` | `{"acntFgList":[...]}` 전체 구분 목록 |
| 1-2 | msNo=`MS001` | `{"acntFg":"OUT"}` | 출금 구분 필터 (Mapper SQL 조건 여부 확인) |
| 1-3 | selectAcntFg 감사 미기록 | MMSLOGTB 확인 | 로그 없음 ★ |

---

## 2. `/selectAcntCd` — 계정 코드 콤보 조회

**서비스**: `LinkedHashMap` → `{"acntCdList": [...]}`

> **[v2 보완]** **소스 62~63번** (`/selectAcntFg`), **87~88번** (`/selectAcntCd`): 불필요 `returnMap = new HashMap<>()` 초기화 후 덮어씀 — St_Cash_00001 동일 패턴 (기능 영향 없음)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | msNo=`MS001` | `{}` | `{"acntCdList":[...]}` 전체 코드 목록 |
| 2-2 | msNo=`MS001` | `{"acntFg":"OUT"}` | 구분에 따른 코드 필터 |
| 2-3 | selectAcntCd 감사 미기록 | MMSLOGTB 확인 | 로그 없음 ★ |

---

## 3. `/selectMmaList` — 월간지출 내역 조회

**특이사항**: `accioDate` → `containsKey` 방어 후 `""` 기본값

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | msNo=`MS001` | `{"accioDate":"202605"}` | 해당 월 지출 내역 (월간이므로 YYYYMM 형식 가능성) |
| 3-2 | msNo=`MS001` | `{}` (accioDate 없음) | accioDate=`""` → 전체 또는 조건 무효 |
| 3-3 | msNo=`MS001` | `{"accioDate":"20260522"}` | 일별 전달 시 Mapper SQL 처리 방식 확인 |

---

## 4. `/cashSave` — 월간지출 내역 등록

**서비스 로직** (St_Cash_00001과 동일 구조):
```
getAccioNo()      → MAX_ID 조회
selectChkCnt()    → 해당 날짜 등록 건수
count > 98 → return 0 (일 99건 제한)
else       → insertCash() → return 1

★ St_Cash_00001 대비 vat/custCd 파라미터 없음
```

> **[v2 보완]** **소스 137~141번** (`/cashSave`): St_Cash_00001 대비 `vat`, `custCd`, `vatFg` containsKey 없음 확인 ✅ (TC 90~91번 정확)

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 4-1 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | 해당일 0건 | `{"accioDate":"20260522","acntFg":"OUT","acntCd":"B001","anctAmt":30000,"remark":"임대료"}` | `1` |
| 4-2 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | 해당일 99건 | `{"accioDate":"20260522","acntFg":"OUT","acntCd":"B001","anctAmt":30000}` | `0` (등록 불가) |
| 4-3 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | 해당일 98건 (경계값) | 유효 파라미터 | `98 > 98` = false → insertCash → `1` |
| 4-4 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | - | `{}` (accioDate 없음) | accioDate=`""` → getAccioNo(빈 날짜) → MAX_ID 조회 결과 확인 |
| 4-5 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | - | `{"accioDate":"20260522","acntFg":"OUT","acntCd":"B001","anctAmt":30000}` (remark 없음) | remark=`""` → insert 정상 |

---

## 5. `/cashUpdate` — 월간지출 내역 수정

**St_Cash_00001 대비 차이**: `vat`, `custCd` 파라미터 없음

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 5-1 | msNo=`MS001`, ID=`I000449s` | accioNo=`ACC001` 존재 | `{"accioDate":"20260522","accioNo":"ACC001","anctAmt":35000,"remark":"수정"}` | `1` |
| 5-2 | msNo=`MS001`, ID=`I000449s` | - | `{"accioDate":"20260522","accioNo":"INVALID","anctAmt":35000}` | `0` (update 0건) |
| 5-3 | msNo=`MS001`, ID=`I000449s` | - | `{}` (accioNo 없음) | accioNo=`""` → WHERE accioNo='' → 전 건 업데이트 위험 ★ |

---

## 6. `/cashDel` — 월간지출 내역 삭제

**St_Cash_00001 `cashDel` 대비 개선된 구조**:
```java
// St_Cash_00001: 루프 내 list 누적 → 중복 삭제 버그
// St_Cash_00004: accioNoList에 배열 전달 → Mapper IN절 한 번에 삭제 (개선)

List<String> array = (List<String>) map.get("delAccioNoArr");
// → null 시 addMap.put("accioNoList", null) → Mapper IN 조건 null ★

addMap.put("accioNoList", array);
St_Cash_00004_Mapper.deleteYnUpdate(addMap);  ← 1회 호출 (루프 없음)
```

> **[v2 보완]** **소스 189번** (`/cashDel`): `map.put("userId", ...)` **St_Cash_00001 대비 추가** ★  

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 6-1 | msNo=`MS001`, ID=`I000449s` | ACC001 존재 | `{"accioDate":"20260522","delAccioNoArr":["ACC001"]}` | 1건 삭제 → `{}` |
| 6-2 | msNo=`MS001`, ID=`I000449s` | ACC001, ACC002 존재 | `{"accioDate":"20260522","delAccioNoArr":["ACC001","ACC002"]}` | IN절로 2건 한 번에 삭제 → `{}` |
| 6-3 | msNo=`MS001`, ID=`I000449s` | - | `{"accioDate":"20260522","delAccioNoArr":null}` | `(List<String>) null` → `addMap.put("accioNoList", null)` → Mapper IN null ★★ |
| 6-4 | msNo=`MS001`, ID=`I000449s` | - | `{"accioDate":"20260522"}` (delAccioNoArr 없음) | `(List<String>) null` → Mapper IN null ★★ |
| 6-5 | msNo=`MS001`, ID=`I000449s` | - | `{"accioDate":"20260522","delAccioNoArr":"ACC001"}` (단일 String) | `(List<String>) String` → **ClassCastException** ★★ |
| 6-6 | msNo=`MS001`, ID=`I000449s` | - | `{"accioDate":"20260522","delAccioNoArr":[]}` (빈 배열) | accioNoList=[] → IN절 비어있음 → Mapper SQL 처리 확인 ★ |

---

## St_Cash_00004 `cashDel` vs St_Cash_00001 비교

| 항목 | St_Cash_00001 | St_Cash_00004 |
|------|--------------|--------------|
| 삭제 방식 | 루프 내 `list.add()` + `deleteYnUpdate(list)` 반복 | `accioNoList` 배열 → **IN절 1회 삭제** |
| 중복 삭제 버그 | **있음** (i=0→[A], i=1→[A,B]) | **없음** |
| null 처리 | `array.size()` → **NPE** | `put("accioNoList", null)` → Mapper null |
| 주석 처리된 구버전 코드 | 없음 | **`/* ... */` 블록으로 구버전 보존** |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/cash/st_cash_00004"
$h = @{"Content-Type"="application/json"}

# 1. 계정 구분 콤보
Invoke-RestMethod -Uri "$base/selectAcntFg" -Method POST -Headers $h -WebSession $session `
  -Body '{}'

# 2. 계정 코드 콤보
Invoke-RestMethod -Uri "$base/selectAcntCd" -Method POST -Headers $h -WebSession $session `
  -Body '{}'

# 3-1. 월간지출 내역 조회
Invoke-RestMethod -Uri "$base/selectMmaList" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"202605"}'

# 4-1. 등록 (정상)
Invoke-RestMethod -Uri "$base/cashSave" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522","acntFg":"OUT","acntCd":"B001","anctAmt":30000,"remark":"임대료"}'
# 예상: 1

# 5-1. 수정
Invoke-RestMethod -Uri "$base/cashUpdate" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522","accioNo":"ACC001","anctAmt":35000,"remark":"수정"}'

# 6-1. 삭제 (1건)
Invoke-RestMethod -Uri "$base/cashDel" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522","delAccioNoArr":["ACC001"]}'
# 예상: {}

# 6-2. 삭제 (2건 IN절)
Invoke-RestMethod -Uri "$base/cashDel" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522","delAccioNoArr":["ACC001","ACC002"]}'

# 6-5. 단일 String → ClassCastException
Invoke-RestMethod -Uri "$base/cashDel" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522","delAccioNoArr":"ACC001"}'
# 예상: 500 ClassCastException
```

---

## 주요 검증 포인트

```
□ cashDel — delAccioNoArr 단일 String → ClassCastException ★★ (00001과 동일 취약점)
□ cashDel — delAccioNoArr null/미전달 → accioNoList=null → Mapper IN null 처리 확인 ★
□ cashDel — 빈 배열 → accioNoList=[] → MyBatis foreach empty 처리 확인 ★
□ cashDel — 00001 대비 루프 중복 삭제 버그 없음 (IN절 개선) ✓
□ cashSave — count > 98 경계: 98건 → insert 가능, 99건 → return 0
□ cashUpdate — accioNo="" → WHERE 조건 무효 → 전 건 업데이트 위험 ★
□ selectAcntFg vs selectAcntCd — 세션 주입 `msNo` (00001은 `chainNo`) 차이 확인
□ cashSave — vat/custCd 파라미터 없음 (00001 대비) — DB 컬럼 기본값 의존
□ @Transactional rollbackFor Exception 포함 — 전 메서드 rollback 보장
```

---

---

