# Hq_Master_00009 — POS 부가메뉴(터치키) 등록 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > 상품관리 > POS 부가메뉴 등록  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00009`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식**: 전 엔드포인트 `@RequestParam` (form-data)  
> **공통 파라미터**: `msNo` — 매장번호 (세션 아닌 **파라미터**로 전달)  
> **핵심 유틸**: `setZeroValue(int value, int num)` — 0 입력 시 `"0"` 반환 (=="0" 비교로 `"00"` 치환)
> **DB 트리거 영향도**: MSUBMNTB, MMBUMSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `ID` | `shopadmin` | updateCategoryNm, moveGoodsCategory, regiGoodsKey, moveGoodsKey |

> **주의**: `chainNo`는 이 컨트롤러에서 **세션에서 주입하지 않음** — `msNo`를 파라미터로 직접 수신

---

## setZeroValue 로직 (공통 유틸)

```
setZeroValue(value, num):
  value == 0 → "0"  ← "00"이 아님!
  value < 10, num=2 → "0" + value  (예: 1 → "01", 9 → "09")
  value >= 10       → value 그대로  (예: 10 → "10")

컨트롤러/서비스에서:
  if(result == "0") result = "00"  ← == 비교 (참조 비교) → 문자열 리터럴 "0"이면 참, new String("0")이면 거짓
  (자바에서 == 문자열 비교는 위험하나, 리터럴 반환이므로 정상 동작)
```

---

## 엔드포인트 목록 (11개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/search` | 분류 터치키 조회 (list + cnt) | `Map` | SELECT | MGOODSTB<br>MMCPLKTB<br>MPRICETB<br>MSUBMNTB |
| 2 | `/goodsKeySearch` | 상품 터치키 조회 (list + cnt, groupCd 변환) | `Map` | SELECT | MNAMEMTB<br>MSUBMNTB |
| 3 | `/updateCategoryNm` | 분류 명칭 저장 (formFg=U→update, 그외→insert) | `String` | MMBUMSTB |
| 4 | `/removeGoodsCategory` | 분류 삭제 (하위 상품키 + 분류키) | `String` | DELETE | MMBUMSTB<br>MSUBMNTB |
| 5 | `/moveGoodsCategory` | 분류 이동 (3단계 스왑: MMCPLUTB + MMCPLKTB) | `String` | UPDATE | MMBUMSTB<br>MSUBMNTB |
|6|`/searchSubGoodsList`|부가 상품 조회 (분류 필터)|`List`|SELECT| 공통 모듈/동적 쿼리 (추적 불가) |
| 7 | `/selectSubGoodsList` | drag용 상품 조회 (stockFg → 뷰 분기) | `ModelAndView` | SELECT | MGOODSTB<br>MPRICETB |
| 8 | `/regiGoodsKey` | 상품키 등록 (delete → insert, stockFg≠2면 price=0) | `String` | INSERT | MSUBMNTB |
| 9 | `/removeGoodsKey` | 상품키 삭제 + selectedClpluCd[0] 반환 | `Map` | DELETE | MSUBMNTB |
| 10 | `/moveGoodsKey` | 상품키 이동 (3단계 스왑: MMCPLKTB) | `String` | UPDATE | MSUBMNTB |
| 11 | `/searchMoveCategory` | 분류이동 모달 조회 | `List` | SELECT | MSUBMNTB |
| 12 | `/moveCategory` | 분류 이동 (maxPluCd 기반 재채번) | `Map` | UPDATE | MSUBMNTB |

---

## 1. `/search` — 분류 터치키 조회

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 1-1 | `startKey=1&lastKey=10&msNo=MS001` | `{"goodsCategoryList":[...],"cnt":"5"}` |
| 1-2 | `startKey=1&lastKey=1&msNo=MS001` | 1건 조회 |
| 1-3 | `startKey` 없음 | 400 (@NotBlank) |
| 1-4 | `msNo` 없음 | 400 (@NotBlank) |

---

## 2. `/goodsKeySearch` — 상품 터치키 조회

**groupCd 변환**: `Integer.parseInt(groupCd)` → `setZeroValue(n,2)` → `"00"` 치환

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 2-1 | `startKey=1&lastKey=10&groupCd=1&msNo=MS001` | groupCd=`"01"` → 해당 그룹 상품키 |
| 2-2 | `startKey=1&lastKey=10&groupCd=0&msNo=MS001` | setZeroValue(0,2)=`"0"` → `"00"` → groupCd=`"00"` |
| 2-3 | `startKey=1&lastKey=10&groupCd=10&msNo=MS001` | setZeroValue(10,2)=`"10"` → groupCd=`"10"` |
| 2-4 | `groupCd=abc` | **NumberFormatException** (`Integer.parseInt(groupCd)`) |
| 2-5 | `groupCd` 없음 | 400 (required=true) |
| 2-6 | goodsKeySearch 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 3. `/updateCategoryNm` — 분류 명칭 저장

**서비스 분기**:
```
chkDulpCategoryNm() = 0 (중복 없음)
  formFg = "U" → updateCategoryNm → "update"
  그 외          → insertCategoryNm → "insert"
중복 있음 → "dupl"
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 3-1 | ID=`shopadmin` | 중복 없음 | `searchPluCd=01&pluNm=신규분류&formFg=I&msNo=MS001` | `"insert"` |
| 3-2 | ID=`shopadmin` | 분류 존재 | `searchPluCd=01&pluNm=수정분류&formFg=U&msNo=MS001` | `"update"` |
| 3-3 | ID=`shopadmin` | **동일 pluNm 존재** | `searchPluCd=02&pluNm=기존분류명&formFg=I&msNo=MS001` | `"dupl"` |
| 3-4 | - | - | `pluNm=` (빈값) | 400 (@NotBlank) |
| 3-5 | - | - | `pluNm=` 121자 초과 | 400 (@Size max=120) |

---

## 4. `/removeGoodsCategory` — 분류 삭제

**컨트롤러**: `removePluCd[]` (int 배열) → `setZeroValue` 변환 → list  
**서비스**: `deleteGoodsKeyCategory(list)` → `deleteGoodsCategory(list)` 순서

| No | DB 선행상태 | Request (form-param) | 예상값 |
|----|------------|----------------------|-------|
| 4-1 | 분류 01 존재 (하위 상품키 있음) | `removePluCd[]=1&msNo=MS001` | 하위 상품키 삭제 + 분류 삭제 → `"remove"` |
| 4-2 | 분류 01, 02 존재 | `removePluCd[]=1&removePluCd[]=2&msNo=MS001` | 2건 일괄 삭제 |
| 4-3 | 분류 없음 | `removePluCd[]=99&msNo=MS001` | delete 0건 → `"remove"` (오류 없음) |
| 4-4 | - | `removePluCd[]=0&msNo=MS001` | setZeroValue(0,2)=`"0"` → `"00"` → groupCd=`"00"` 삭제 |
| 4-5 | - | `removePluCd[]` 없음 | 400 (required=true) |

---

## 5. `/moveGoodsCategory` — 분류 이동

**컨트롤러**: `movePluCd[]` 2개 → 루프 2회 (실제 마지막 값만 유효), `pluCdStr0/1` 세팅  
**서비스 6단계 스왑** (MMCPLUTB + MMCPLKTB 각각):
```
1. clplu_cd[0] → '-' (임시)
2. clplu_cd[1] → clplu_cd[0]
3. '-' → clplu_cd[1]
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 5-1 | ID=`shopadmin` | 분류 01, 02 존재 | `movePluCd[]=1&movePluCd[]=2&msNo=MS001` | 01↔02 위치 스왑 → `"move"` |
| 5-2 | ID=`shopadmin` | - | `movePluCd[]=1` (1개만) | movePluCd[1] **ArrayIndexOutOfBoundsException** ★ |
| 5-3 | - | - | `movePluCd[]` 없음 | 400 (required=true) |
| 5-4 | movePluCd[1]=0 이동 | `movePluCd[]=1&movePluCd[]=0` | **pluCdStr1="0"** 으로 서비스 전달 (버그: "00"이어야 함) ★★ |

---

## 6. `/searchSubGoodsList` — 부가 상품 조회

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 6-1 | `msNo=MS001` | 전체 부가 상품 List |
| 6-2 | `msNo=MS001&lClassCd=L01&mClassCd=M01&sClassCd=S01` | 분류 필터 결과 |
| 6-3 | `msNo` 없음 | 400 (required=true) |
| 6-4 | searchSubGoodsList 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 7. `/selectSubGoodsList` — drag용 상품 조회 (ModelAndView)

**뷰 분기**:
```
stockFg = "2" → hq_master_00009_T04
stockFg = "3" → hq_master_00009_T05
그 외          → setViewName 없음 → 기본 뷰 또는 오류
```

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 7-1 | `stockFg=2&msNo=MS001` | ModelAndView → T04 뷰 |
| 7-2 | `stockFg=3&msNo=MS001` | ModelAndView → T05 뷰 |
| 7-3 | `stockFg=1&msNo=MS001` | setViewName 없음 → **뷰 미설정** (오류 또는 null 뷰) ★ |
| 7-4 | `stockFg` 없음 | 400 (@NotBlank) |
| 7-5 | selectSubGoodsList 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 8. `/regiGoodsKey` — 상품키 등록

**특이사항**: `stockFg ≠ "2"` 이면 price를 강제로 `"0"` 처리  
**서비스**: `deleteGoodsKey(commandMap)` → `insertGoodsKey(commandMap)` (delete + insert, MERGE 아님)

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 8-1 | ID=`shopadmin` | `goodsCd=G001&goodsNm=아메리카노&clpluCd=1&pluCd=1&stockFg=1&price=5000&msNo=MS001` | price=`"0"` (stockFg≠2) → deleteGoodsKey → insertGoodsKey → `"insertGoodsKey"` |
| 8-2 | ID=`shopadmin` | `stockFg=2&price=3000` (나머지 동일) | price=`"3000"` 그대로 → `"insertGoodsKey"` |
| 8-3 | ID=`shopadmin` | `clpluCd=0&pluCd=0` | setZeroValue(0,2)=`"0"` → `"00"` → clpluCd=`"00"`, pluCd=`"00"` |
| 8-4 | - | `goodsNm=` 121자 초과 | 400 (@Size max=120) |
| 8-5 | clpluCd 미전송 | clpluCd 없이 요청 | `defaultValue=""` → int 변환 실패 → **400** ★ |
| 8-6 | pluCd=abc 문자 | `pluCd=abc` | int 파싱 실패 → **400** ★ |

---

## 9. `/removeGoodsKey` — 상품키 삭제

**반환**: `{"chkFg":"removeGoodsKey","selectedClpluCd":removeClpluCd[0]}`

| No | DB 선행상태 | Request (form-param) | 예상값 |
|----|------------|----------------------|-------|
| 9-1 | 상품키 존재 | `removeClpluCd[]=01&removePluCd[]=01&msNo=MS001` | deleteGoodsKeys → `{"chkFg":"removeGoodsKey","selectedClpluCd":"01"}` |
| 9-2 | 다건 삭제 | `removeClpluCd[]=01&removePluCd[]=01&removeClpluCd[]=01&removePluCd[]=02` | 2건 삭제, selectedClpluCd=`removeClpluCd[0]` = `"01"` |
| 9-3 | - | `removePluCd[]` 없음 | 400 (required=true) |

---

## 10. `/moveGoodsKey` — 상품키 이동

**3단계 스왑** (MMCPLKTB):
```
1. plu_cd[0] → '-' (임시)
2. plu_cd[1] → plu_cd[0]
3. '-' → plu_cd[1]
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 10-1 | ID=`shopadmin` | 상품키 2건 존재 | `clpluCd=1&movePluCd[]=01&movePluCd[]=02&msNo=MS001` | 스왑 → `"moveGoodsKey"` |
| 10-2 | - | - | `movePluCd[]=01` (1개만) | movePluCd[1] **ArrayIndexOutOfBoundsException** ★ |

---

## 12. `/moveCategory` — 분류 이동

**서비스 핵심**:
```
selectMaxPluCd(list.get(0)) → maxPluCd (이동 대상 분류의 현재 최대 pluCd)
for each item:
  newPluCdNum = maxPluCd + i
  newPluCd = setZeroValue(newPluCdNum, 2)
  if(newPluCd=="0") newPluCd="00"
  → updateMoveCategory(addList)

userId = "astems000"  ← 하드코딩! 세션 사용 안 함 ★
```

| No | DB 선행상태 | Request (form-param) | 예상값 |
|----|------------|----------------------|-------|
| 12-1 | 분류 01→02 이동 | `newClpluCd=2&clpluCd=01&pluCd[]=01&msNo=MS001` | maxPluCd + 0 → newPluCd 재채번 → `{"newClpluCd":2,"chkFg":"moveCategory"}` |
| 12-2 | 다건 이동 | `pluCd[]=01&pluCd[]=02` (2개) | newPluCd = maxPluCd+0, maxPluCd+1 순서 |
| 12-3 | - | `pluCd[]` 없음 | 400 (required=true) |
| 12-4 | - | userId 검증 | `userId = "astems000"` (하드코딩) → 이력 컬럼에 항상 `"astems000"` 기록 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00009"
$f = "application/x-www-form-urlencoded"

# 1. 분류 터치키 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -ContentType $f -WebSession $session `
  -Body "startKey=1&lastKey=10&msNo=MS001"

# 2. 상품 터치키 조회 (groupCd=0 → "00")
Invoke-RestMethod -Uri "$base/goodsKeySearch" -Method POST -ContentType $f -WebSession $session `
  -Body "startKey=1&lastKey=10&groupCd=0&msNo=MS001"

# 3-1. 분류 명칭 신규 등록 (formFg=I)
Invoke-RestMethod -Uri "$base/updateCategoryNm" -Method POST -ContentType $f -WebSession $session `
  -Body "searchPluCd=01&pluNm=신규분류&formFg=I&msNo=MS001"
# 예상: "insert"

# 3-2. 분류 명칭 수정 (formFg=U)
Invoke-RestMethod -Uri "$base/updateCategoryNm" -Method POST -ContentType $f -WebSession $session `
  -Body "searchPluCd=01&pluNm=수정분류&formFg=U&msNo=MS001"
# 예상: "update"

# 4. 분류 삭제 (1건)
Invoke-RestMethod -Uri "$base/removeGoodsCategory" -Method POST -ContentType $f -WebSession $session `
  -Body "removePluCd[]=1&msNo=MS001"
# 예상: "remove"

# 5-2. 분류 이동 (movePluCd 1개만 → ArrayIndexOutOfBoundsException 확인)
Invoke-RestMethod -Uri "$base/moveGoodsCategory" -Method POST -ContentType $f -WebSession $session `
  -Body "movePluCd[]=1&msNo=MS001"

# 7. drag용 조회 stockFg=2
Invoke-RestMethod -Uri "$base/selectSubGoodsList" -Method POST -ContentType $f -WebSession $session `
  -Body "stockFg=2&msNo=MS001"

# 8-1. 상품키 등록 (stockFg=1 → price 강제 0)
Invoke-RestMethod -Uri "$base/regiGoodsKey" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCd=G001&goodsNm=아메리카노&clpluCd=1&pluCd=1&stockFg=1&price=5000&msNo=MS001"
# 예상: "insertGoodsKey", price="0"으로 처리

# 9. 상품키 삭제
Invoke-RestMethod -Uri "$base/removeGoodsKey" -Method POST -ContentType $f -WebSession $session `
  -Body "removeClpluCd[]=01&removePluCd[]=01&msNo=MS001"
# 예상: {"chkFg":"removeGoodsKey","selectedClpluCd":"01"}

# 12. 분류 이동
Invoke-RestMethod -Uri "$base/moveCategory" -Method POST -ContentType $f -WebSession $session `
  -Body "newClpluCd=2&clpluCd=01&pluCd[]=01&msNo=MS001"
# 예상: {"newClpluCd":2,"chkFg":"moveCategory"}
```

---

## 주요 검증 포인트

```
□ msNo — 세션에서 가져오지 않고 @RequestParam으로 수신 (클라이언트에서 직접 전달)
□ setZeroValue(0,2) = "0" → =="0" 비교로 "00" 치환 — value=0 케이스 필수 테스트
□ goodsKeySearch groupCd — Integer.parseInt() → 숫자 아닌 문자열 시 500
□ moveGoodsCategory/moveGoodsKey — movePluCd[] 1개만 전달 시 [1] 접근 ArrayIndexOutOfBounds
□ updateCategoryNm formFg — "U"이면 update, 그 외 전부 insert (명시적 "I" 체크 없음)
□ regiGoodsKey — stockFg≠"2" 이면 price 강제 "0" (서비스가 아닌 컨트롤러에서 처리)
□ regiGoodsKey — deleteGoodsKey 후 insertGoodsKey (기존 키 덮어쓰기, MERGE 아님)
□ selectSubGoodsList stockFg — "2","3" 외 값 입력 시 setViewName 미설정 → null 뷰 오류
□ moveCategory userId — "astems000" 하드코딩, 실제 로그인 ID 기록 안 됨 ★
□ removeGoodsCategory — deleteGoodsKeyCategory(하위 상품키) 먼저, 이후 deleteGoodsCategory
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] MMBUMSTB (CUD 작업)
│   └── (Trigger) Tr_MMBUMS_T01
└── [테이블] MSUBMNTB (CUD 작업)
    └── (Trigger) Tr_MSUBMN_T01
```
