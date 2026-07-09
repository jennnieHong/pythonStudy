# Hq_Stock_00005 — 조정 등록 단위 테스트케이스

> **화면**: [HQ] 재고 > 조정 등록  
> **URL Prefix**: `POST /backoffice/data/hq/stock/hq_stock_00005`  
> **@Transactional**: 기본값 (rollbackFor 미명시)  
> **요청 방식 혼용**: `search`, `addGoodsSearch` = `@RequestBody` / 나머지 = `@RequestParam`
> **DB 트리거 영향도**: TPRICETB, MNAMEMTB, IMREALTB, TGOODSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, addGoodsSearch, addGoodsModify, updtReal, deleteReal, confirmReal |
| `chainMsNo` | `NC0001` | addGoodsModify, updtReal |
| `ID` | `1162190` | addGoodsModify, updtReal, confirmReal, addModifyReason |

---

## 엔드포인트 목록 (9개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 조정 내역 조회 (페이징, 다중 필터) | `@RequestBody` | `Map` (total+rows) | SELECT | MNAMEMTB |
| 2 | `/addGoodsSearch` | 상품 등록 모달 조회 | `@RequestBody` | `List` | SELECT | IMCRIOTB<br>MNAMEMTB<br>TGOODSTB |
| 3 | `/addGoodsModify` | 상품 선택 등록 (중복 체크 + insert) | `@RequestParam` | `Map` (success/fail/status) | INSERT | IMCRIOTB<br>IMREALTB<br>IMTRLGTB<br>TGOODSTB<br>TPRICETB |
| 4 | `/getWongaFg` | 매장 원가 조건 조회 | `@RequestParam` | `Map` | SELECT | MMEMBVTB |
| 5 | `/updtReal` | 조정 저장 (배열 순회 update) | `@RequestParam` 배열 | `void` | UPDATE | IMCRIOTB<br>IMREALTB<br>TGOODSTB |
| 6 | `/deleteReal` | 조정 삭제 (배열 순회 delete) | `@RequestParam` 배열 | `void` | DELETE | IMREALTB |
| 7 | `/confirmReal` | 조정 확정 (배열 순회 update) | `@RequestParam` 배열 | `void` | UPDATE | IMREALTB |
| 8 | `/modifyReasonSearch` | 조정 사유 조회 | (파라미터 없음) | `List` | SELECT | MNAMEMTB |
| 9 | `/addModifyReason` | 사유 추가 (중복 체크) | `@RequestParam` | `String` | INSERT | MNAMEMTB |
| 10 | `/deleteModifyReason` | 사유 삭제 | `@RequestParam` | `void` | DELETE | MNAMEMTB |

---

## 1. `/search` — 조정 내역 조회

**특이사항**: `offset`/`limit` → `Integer.valueOf(reqMap.get("offset").toString())` 변환  
**null 방어**: `containsKey` 체크 후 `""` 기본값 세팅 (lClass/mClass/sClass/goodsCd/goodsNm/setFg/reasonCd/tBarcode)

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainNo=`C001` | 조정 데이터 5건 | `{"surveyDate":"20260522","msNo":"MS001","offset":0,"limit":10}` | `{"total":5,"rows":[...]}` |
| 1-2 | chainNo=`C001` | - | `{"surveyDate":"20260522","msNo":"MS001","offset":0,"limit":10,"lClass":"L01","goodsNm":"커피"}` | 분류+이름 필터 |
| 1-3 | chainNo=`C001` | - | `{"surveyDate":"20260522","msNo":"MS001","offset":0,"limit":10,"reasonCd":"R01","tBarcode":"880123"}` | 사유+바코드 필터 |
| 1-4 | chainNo=`C001` | - | `{"surveyDate":"20260522","msNo":"MS001","offset":10,"limit":10}` | 2페이지 (startIdx=11, endIdx=20) |
| 1-5 | - | - | `{"surveyDate":"20260522","msNo":"MS001"}` (offset/limit 없음) | `reqMap.get("offset").toString()` → **NPE** ★★★ |

---

## 2. `/addGoodsSearch` — 상품 등록 모달 조회

**특이사항**: `containsKey` 방어 (`lClass`, `mClass`, `sClass`, `goodsCd`, `goodsNm`)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"surveyDate":"20260522","msNo":"MS001"}` | 전체 상품 리스트 |
| 2-2 | chainNo=`C001` | `{"surveyDate":"20260522","msNo":"MS001","goodsNm":"아메리카노"}` | 이름 필터 |
| 2-3 | chainNo=`C001` | `{"surveyDate":"20260522","msNo":"MS001","lClass":"L01","mClass":"M01","sClass":"S01"}` | 분류 필터 |
| 2-4 | addGoodsSearch 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 3. `/addGoodsModify` — 상품 선택 등록

**서비스 핵심 로직**:
```
chkImtrlgtb(commandMap) > 0
  → status = "later" (이미 확정된 조정 존재 → 등록 불가)
else:
  for goodsCdArr[i]:
    getModifyChk(map) > 0 → fail++  (이미 등록된 상품)
    else → insertImreal(map) + success++
→ {"success": N, "fail": M, "status": ""}

★ maxIdx = getMaxIdx(commandMap) → 모든 상품에 동일 idx 사용 (루프 밖에서 1회 조회)
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 3-1 | chainNo=`C001`, ID=`1162190` | 확정 없음, G001 미등록 | `surveyDate=20260522&msNo=MS001&wongaFg=Y&goodsCdArr[]=G001` | success=1, fail=0, status="" |
| 3-2 | chainNo=`C001` | G001 이미 등록됨 | `goodsCdArr[]=G001` | success=0, fail=1, status="" |
| 3-3 | chainNo=`C001` | 확정 존재 (chkImtrlgtb>0) | `goodsCdArr[]=G001` | status="later", success=0, fail=0 |
| 3-4 | chainNo=`C001` | G001 미등록, G002 등록됨 | `goodsCdArr[]=G001&goodsCdArr[]=G002` | success=1, fail=1 |
| 3-5 | - | - | `surveyDate` 없음 | 400 (@NotBlank) |
| 3-6 | - | - | `wongaFg` 없음 | 400 (@NotBlank) |

---

## 4. `/getWongaFg` — 매장 원가 조건 조회

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 4-1 | `msNo=MS001` | `{"wongaFg":"Y"}` (또는 "N") |
| 4-2 | `msNo` 없음 | 400 (@NotBlank) |
| 4-3 | `msNo=INVALID` | 존재하지 않는 매장 → `{}` 또는 null 반환 |
| 4-4 | getWongaFg 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 5. `/updtReal` — 조정 저장

**서비스 핵심 로직**:
```
for i in idxArr.length:
  remarkArr.length > i  → remarkArr[i]  / else → ""
  reasonCdArr.length > i → reasonCdArr[i] / else → ""
  ucostArr[i] 직접 접근 (방어 없음 → 배열 불일치 시 ArrayIndexOutOfBounds ★)
  updtReal(map)
```

> **[v2 보완]** **소스 207~212번** (`/updtReal`): `goodsCdArr[]`, `surveyTotArr[]`, `remarkArr[]`, `reasonCdArr[]`, `idxArr[]`, `ucostArr[]` 모두 `required=false`, `defaultValue` 없음  

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 5-1 | chainNo=`C001`, ID=`1162190` | 조정 존재 | `msNo=MS001&surveyDate=20260522&wongaFg=Y&goodsCdArr[]=G001&idxArr[]=1&surveyTotArr[]=10&remarkArr[]=메모&reasonCdArr[]=R01&ucostArr[]=500` | updtReal 1건 실행 |
| 5-2 | chainNo=`C001` | - | `remarkArr[]` 미전달 (null) | `remarkArr.length > i` → **NPE** (null.length) ★★★ |
| 5-3 | chainNo=`C001` | - | `goodsCdArr[]=G001&goodsCdArr[]=G002&idxArr[]=1&idxArr[]=2&ucostArr[]=500` | ucostArr[1] 없음 → **ArrayIndexOutOfBounds** ★★ |
| 5-4 | - | - | `msNo` 없음 | 400 (@NotBlank) |
| 5-5 | - | - | `idxArr[]` null → `idxArr.length` | **NPE** (루프 조건) ★★★ |

---

## 6. `/deleteReal` — 조정 삭제

**서비스**: `idxArr.length` 순회 → `goodsCdArr[i]` 접근 (방어 없음)

> **[v2 보완]** **소스 256~257번** (`/deleteReal`): `goodsCdArr[]`, `idxArr[]` 모두 `required=false`  

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 6-1 | chainNo=`C001` | 조정 1건 존재 | `msNo=MS001&surveyDate=20260522&goodsCdArr[]=G001&idxArr[]=1` | deleteReal 1건 |
| 6-2 | chainNo=`C001` | 2건 존재 | `goodsCdArr[]=G001&goodsCdArr[]=G002&idxArr[]=1&idxArr[]=2` | deleteReal 2건 |
| 6-3 | chainNo=`C001` | - | `idxArr[]` null, `goodsCdArr[]` null | `idxArr.length` → **NPE** ★★★ |
| 6-4 | chainNo=`C001` | - | `goodsCdArr[]` null (idxArr 있음) | `goodsCdArr[i]` → **NPE** ★★ |
| 6-5 | - | - | `msNo` 없음 | 400 (@NotBlank) |
| 6-6 | deleteReal 감사 name 오표기 | MMSLOGTB 조회 | `name="조정 상품 저장"` (DELETE인데 저장으로 기록) ★ |

---

## 7. `/confirmReal` — 조정 확정

**서비스**: `idxArr.length` 순회 → `goodsCdArr[i]` 접근 (deleteReal과 동일 패턴)

> **[v2 보완]** **소스 292~293번** (`/confirmReal`): 동일 패턴  

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 7-1 | chainNo=`C001`, ID=`1162190` | 조정 1건 (미확정) | `msNo=MS001&surveyDate=20260522&goodsCdArr[]=G001&idxArr[]=1` | confirmReal 1건 |
| 7-2 | chainNo=`C001` | 이미 확정된 건 | `goodsCdArr[]=G001&idxArr[]=1` | DB 상태에 따라 update 0건 또는 정상 |
| 7-3 | chainNo=`C001` | - | `idxArr[]` null | **NPE** ★★★ |

---

## 9. `/addModifyReason` — 사유 추가

**서비스**: `chkNmFg(commandMap) > 0 → "dulp"` / else → `addModifyReason + ""`

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 9-1 | ID=`1162190` | nmCd=`A01` 없음 | `nmCd=A01&nmRep=파손` | addModifyReason → `""` |
| 9-2 | ID=`1162190` | nmCd=`A01` 이미 존재 | `nmCd=A01&nmRep=파손` | `"dulp"` |
| 9-3 | - | - | `nmCd` 없음 | 400 (@NotBlank) |
| 9-4 | - | - | `nmCd=ABCD` (4자) | 400 (@Size max=3) |
| 9-5 | - | - | `nmRep` 121자 초과 | 400 (@Size max=120) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=1162190&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/stock/hq_stock_00005"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 조정 내역 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"surveyDate":"20260522","msNo":"MS001","offset":0,"limit":10}'

# 1-5. offset/limit 없음 → NPE
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"surveyDate":"20260522","msNo":"MS001"}'

# 2-1. 상품 모달 조회
Invoke-RestMethod -Uri "$base/addGoodsSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"surveyDate":"20260522","msNo":"MS001"}'

# 3-1. 상품 등록 (신규)
Invoke-RestMethod -Uri "$base/addGoodsModify" -Method POST -ContentType $f -WebSession $session `
  -Body "surveyDate=20260522&msNo=MS001&wongaFg=Y&goodsCdArr[]=G001"
# 예상: {"success":1,"fail":0,"status":""}

# 4-1. 원가 조건 조회
Invoke-RestMethod -Uri "$base/getWongaFg" -Method POST -ContentType $f -WebSession $session `
  -Body "msNo=MS001"

# 5-1. 조정 저장
Invoke-RestMethod -Uri "$base/updtReal" -Method POST -ContentType $f -WebSession $session `
  -Body "msNo=MS001&surveyDate=20260522&wongaFg=Y&goodsCdArr[]=G001&idxArr[]=1&surveyTotArr[]=10&remarkArr[]=메모&reasonCdArr[]=R01&ucostArr[]=500"

# 6-1. 조정 삭제
Invoke-RestMethod -Uri "$base/deleteReal" -Method POST -ContentType $f -WebSession $session `
  -Body "msNo=MS001&surveyDate=20260522&goodsCdArr[]=G001&idxArr[]=1"

# 7-1. 조정 확정
Invoke-RestMethod -Uri "$base/confirmReal" -Method POST -ContentType $f -WebSession $session `
  -Body "msNo=MS001&surveyDate=20260522&goodsCdArr[]=G001&idxArr[]=1"

# 8. 사유 조회
Invoke-RestMethod -Uri "$base/modifyReasonSearch" -Method POST -ContentType $f -WebSession $session

# 9-1. 사유 추가
Invoke-RestMethod -Uri "$base/addModifyReason" -Method POST -ContentType $f -WebSession $session `
  -Body "nmCd=A01&nmRep=파손"

# 10. 사유 삭제
Invoke-RestMethod -Uri "$base/deleteModifyReason" -Method POST -ContentType $f -WebSession $session `
  -Body "nmCd=A01"
```

---

## 주요 검증 포인트

```
□ search — offset/limit 없으면 reqMap.get("offset").toString() → NPE ★★★
□ search — containsKey 방어 (lClass~tBarcode) — key 없어도 ""로 안전 처리
□ addGoodsModify — chkImtrlgtb > 0 시 status="later" (확정 존재)
□ addGoodsModify — maxIdx는 루프 밖에서 1회 조회 → 모든 상품이 동일 idx 공유
□ updtReal — idxArr/goodsCdArr/surveyQtyArr/ucostArr null 시 .length → NPE ★★★
□ updtReal — remarkArr, reasonCdArr는 length 체크로 방어 / ucostArr는 방어 없음 ★★
□ deleteReal/confirmReal — idxArr null 시 .length → NPE / goodsCdArr null → NPE
□ addModifyReason — 중복 nmCd → "dulp" / 신규 → "" (빈 문자열, 명시적 "ok" 아님)
□ @Transactional 기본값 — RuntimeException만 롤백 (Exception 미롤백)
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] IMREALTB (CUD 작업)
│   └── (Trigger) Tr_IMREAL_T01
├── [테이블] MNAMEMTB (CUD 작업)
│   └── (Trigger) Tr_MNAMEM_T01
├── [테이블] TGOODSTB (CUD 작업)
│   └── (Trigger) Tr_TGOODS_T01
└── [테이블] TPRICETB (CUD 작업)
    └── (Trigger) Tr_TPRICE_T01
```
