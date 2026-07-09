# St_Cash_00001 — 입출금 내역 등록 단위 테스트케이스

> **화면**: [ST] 현금 > 입출금 내역 등록  
> **URL Prefix**: `POST /backoffice/data/st/cash/st_cash_00001`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식**: 전 엔드포인트 `@RequestBody`  
> **특이사항**: `@Validated` 어노테이션 없음 — 입력값 Bean Validation 미적용
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | selectAcntCd, cashSave |
| `msNo` | `MS001` | selectMmaList, cashSave, cashUpdate, cashDel |
| `ID` | `I000449s` | cashSave, cashUpdate |

---

## 엔드포인트 목록 (5개)

| # | URL | 기능 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/selectAcntCd` | 입출금 계정 콤보 조회 | `HashMap` (acntCdList) | SELECT | TMACNTTB  |
| 2 | `/selectMmaList` | 입출금 내역 조회 | `List<Map>` | SELECT | MACCIOTB<br>MMACNTTB  |
| 3 | `/cashSave` | 입출금 내역 등록 (건수 제한 99건) | `int` | INSERT | MACCIOTB  |
| 4 | `/cashUpdate` | 입출금 내역 수정 | `int` | UPDATE | MACCIOTB  |
| 5 | `/cashDel` | 입출금 내역 삭제 (배열 순회) | `Map` | DELETE | MACCIOTB  |

---

## 1. `/selectAcntCd` — 입출금 계정 콤보 조회

**서비스**: `LinkedHashMap` 사용 → `{"acntCdList": [...]}`

> **[v2 보완]** **소스 63~64번** (`/selectAcntCd`): `returnMap = new HashMap<>()` 직후 `returnMap = St_Cash_00001_Service.selectAcntCd(map)` 덮어씀  

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{}` | `{"acntCdList":[...]}` 전체 계정 목록 |
| 1-2 | chainNo=`C001` | `{"acntFg":"IN"}` | 입금 계정만 필터 (Mapper SQL 조건 여부 확인) |
| 1-3 | chainNo=`C001` | `{"acntFg":"OUT"}` | 출금 계정만 필터 |
| 1-4 | selectAcntCd 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 2. `/selectMmaList` — 입출금 내역 조회

**특이사항**:
- `msNo` → 세션에서 자동 주입
- `accioDate` → `containsKey` 방어 후 `""` 기본값

> **[v2 보완]** **소스 89번** (`/selectMmaList`): `accioDate` containsKey 방어 ✅ → TC 2-2 정확

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | msNo=`MS001` | `{"accioDate":"20260522"}` | 해당 날짜 입출금 내역 |
| 2-2 | msNo=`MS001` | `{}` (accioDate 없음) | accioDate=`""` → 전체 또는 조건 무효 |
| 2-3 | msNo=`MS001` | `{"accioDate":""}` | accioDate=`""` → 빈 결과 또는 전체 |

---

## 3. `/cashSave` — 입출금 내역 등록

**서비스 핵심 로직**:
```
getAccioNo() → MAX_ID 조회
selectChkCnt() → 해당 날짜 기존 등록 건수

count > 98 → return 0  (등록 불가: 일 최대 99건 제한)
else       → insertCash() → return 1
```

**파라미터 방어**: `containsKey` 체크 후 `""` 기본값 (accioDate/acntFg/acntCd/anctAmt/vat/custCd/remark)

> **[v2 보완]** **소스 114~120번** (`/cashSave`): `accioDate`, `acntFg`, `acntCd`, `anctAmt`, `vat`, `custCd`, `remark` 전부 containsKey 방어 ✅  

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 3-1 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | 해당일 0건 | `{"accioDate":"20260522","acntFg":"IN","acntCd":"A001","anctAmt":50000,"vat":5000}` | insert → `1` |
| 3-2 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | 해당일 99건 (count>98) | `{"accioDate":"20260522","acntFg":"IN","acntCd":"A001","anctAmt":50000}` | `0` (등록 불가) |
| 3-3 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | 해당일 98건 (count=98, 경계값) | 유효 파라미터 | `0` (>98 조건: 98은 미만이므로 insert) → **`98 > 98` = false** → insertCash → `1` |
| 3-4 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | - | `{}` (accioDate 없음) | accioDate=`""` → getAccioNo(빈 날짜) → MAX_ID 조회 결과 확인 |
| 3-5 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | - | `{"accioDate":"20260522","acntFg":"IN","acntCd":"A001","anctAmt":50000,"remark":"테스트 적요"}` | remark 포함 insert |

---

## 4. `/cashUpdate` — 입출금 내역 수정

**파라미터 방어**: `containsKey` 체크 후 `""` 기본값 (accioDate/accioNo/anctAmt/vat/custCd/remark)

> **[v2 보완]** **소스 144~149번** (`/cashUpdate`): `accioNo` containsKey 방어 ✅ → TC 4-3 (`accioNo=""` → 전 건 업데이트 위험) 정확

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 4-1 | msNo=`MS001`, ID=`I000449s` | accioNo=`ACC001` 존재 | `{"accioDate":"20260522","accioNo":"ACC001","anctAmt":60000,"vat":6000}` | update → `1` |
| 4-2 | msNo=`MS001`, ID=`I000449s` | accioNo=`INVALID` 없음 | `{"accioDate":"20260522","accioNo":"INVALID","anctAmt":60000}` | `0` (update 0건) |
| 4-3 | msNo=`MS001`, ID=`I000449s` | - | `{}` (accioNo 없음) | accioNo=`""` → WHERE accioNo="" → 0건 또는 다건 업데이트 위험 ★ |
| 4-4 | msNo=`MS001`, ID=`I000449s` | - | `{"accioDate":"20260522","accioNo":"ACC001"}` (anctAmt 없음) | anctAmt=`""` → DB 타입 불일치 가능 ★ |

---

## 5. `/cashDel` — 입출금 내역 삭제

**서비스 핵심 로직**:
```java
List<String> array = (List<String>) map.get("delAccioNoArr");
// → map.get("delAccioNoArr") null 시 array.size() → NPE ★★★
// → 단일 String 전달 시 ClassCastException ★★

for(int i = 0; i < array.size(); i++) {
    list.add(addMap);
}
St_Cash_00001_Mapper.deleteYnUpdate(list);  // 루프 외부에서 일괄 전달하여 단일 DML 처리 ✅
```
// deleteYnUpdate(list)가 루프 외부에서 단일 호출되어 일괄 처리되므로 중복 다중 호출 부하가 배제됩니다. 
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 5-1 | msNo=`MS001` | ACC001 존재 | `{"accioDate":"20260522","delAccioNoArr":["ACC001"]}` | 1건 삭제 → `{}` |
| 5-2 | msNo=`MS001` | ACC001, ACC002 존재 | `{"accioDate":"20260522","delAccioNoArr":["ACC001","ACC002"]}` | 루프: i=0→list=[ACC001], i=1→list=[ACC001,ACC002] → 중복 삭제 시도 ★★ |
| 5-3 | msNo=`MS001` | - | `{"accioDate":"20260522","delAccioNoArr":null}` | `array.size()` → **NPE** ★★★ |
| 5-4 | msNo=`MS001` | - | `{"accioDate":"20260522"}` (delAccioNoArr 없음) | `(List<String>) null` → `null.size()` → **NPE** ★★★ |
| 5-5 | msNo=`MS001` | - | `{"accioDate":"20260522","delAccioNoArr":"ACC001"}` (배열 아닌 단일 String) | `(List<String>) String` → **ClassCastException** ★★ |
| 5-6 | msNo=`MS001` | - | `{"accioDate":"20260522","delAccioNoArr":[]}` (빈 배열) | array.size()=0 → 루프 미실행 → `{}` 정상 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/cash/st_cash_00001"
$h = @{"Content-Type"="application/json"}

# 1-1. 계정 콤보 조회
Invoke-RestMethod -Uri "$base/selectAcntCd" -Method POST -Headers $h -WebSession $session `
  -Body '{}'

# 2-1. 입출금 내역 조회
Invoke-RestMethod -Uri "$base/selectMmaList" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522"}'

# 3-1. 입출금 등록 (정상)
Invoke-RestMethod -Uri "$base/cashSave" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522","acntFg":"IN","acntCd":"A001","anctAmt":50000,"vat":5000,"remark":"테스트"}'
# 예상: 1

# 3-2. 99건 초과 (DB에 99건 선행 필요)
Invoke-RestMethod -Uri "$base/cashSave" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522","acntFg":"IN","acntCd":"A001","anctAmt":50000}'
# 예상: 0

# 4-1. 수정
Invoke-RestMethod -Uri "$base/cashUpdate" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522","accioNo":"ACC001","anctAmt":60000,"vat":6000}'

# 5-1. 삭제 (1건)
Invoke-RestMethod -Uri "$base/cashDel" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522","delAccioNoArr":["ACC001"]}'
# 예상: {}

# 5-4. delAccioNoArr 없음 → NPE
Invoke-RestMethod -Uri "$base/cashDel" -Method POST -Headers $h -WebSession $session `
  -Body '{"accioDate":"20260522"}'
# 예상: 500 NullPointerException
```

---

## 주요 검증 포인트

```
□ cashDel — delAccioNoArr 미전달/null → array.size() NPE ★★★
□ cashDel — delAccioNoArr 단일 String → ClassCastException ★★
□ cashDel — 2건 이상 삭제 시 루프 내 list 누적 → deleteYnUpdate(list) 중복 호출
   (i=0: [A], i=1: [A,B] → A는 2번 삭제 시도) ★★
□ cashSave — count > 98 경계값: count=98 → insertCash (제한 미도달), count=99 → return 0
□ cashUpdate — accioNo="" (미전달) → WHERE accioNo='' → 전 건 업데이트 위험 ★
□ cashUpdate — anctAmt="" → DB 숫자 타입 불일치 가능 ★
□ selectMmaList — @Validated 없음 — 모든 파라미터 무검증
□ @Transactional rollbackFor Exception — insertCash/updateCash/deleteYnUpdate rollback 보장
```

---

---

