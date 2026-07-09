# St_Master_00011 — POS 부가메뉴 등록 단위 테스트케이스

> **화면**: [ST] 마스터관리 > POS 부가메뉴 등록  
> **URL Prefix**: `POST /backoffice/data/st/master/st_master_00011`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식**: 전부 `@RequestParam` (조회도 동일)
> **DB 트리거 영향도**: TSUBMNTB, TMBUMSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## `setZeroValue(value, num)` 공통 버그 (00010과 동일)

```java
if(value == 0) return "0";       // 0 → "0" 반환
if(str == "0") str = "00";       // 참조비교 → 항상 false ★★
// 결과: value=0 → "0" (기대값 "00")
```

**추가 발견**: `moveCategory` 서비스에서 `userId = "astems000"` **하드코딩** ★★

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `msNo` | `MS001` | search, goodsKeySearch |
| `chainNo` | `C001` | updateCategoryNm, removeGoodsCategory, moveGoodsCategory, searchSubGoodsList, selectSubGoodsList, regiGoodsKey, removeGoodsKey, moveGoodsKey, searchMoveCategory, moveCategory |
| `ID` | `I000449s` | updateCategoryNm, moveGoodsCategory, regiGoodsKey, moveGoodsKey |

---

## 엔드포인트 목록 (11개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 부가메뉴 분류 조회 | `@RequestParam` | `Map` (goodsCategoryList+cnt) | SELECT | MMBUMSTB |
| 2 | `/goodsKeySearch` | 상품키 조회 (groupCd 패딩) | `@RequestParam` | `Map` (goodsKeyList+cnt) | SELECT | MNAMEMTB<br>MSUBMNTB |
| 3 | `/updateCategoryNm` | 분류명 저장 (중복체크 → insert/update) | `@RequestParam` | `String` | CUD | TMBUMSTB |
| 4 | `/removeGoodsCategory` | 분류 삭제 (int[] 배열, 패딩 후 루프) | `@RequestParam` | `String` | DELETE | TMBUMSTB<br>TSUBMNTB |
| 5 | `/moveGoodsCategory` | 분류코드 이동 (for 루프 2회 버그) | `@RequestParam` | `String` | UPDATE | TMBUMSTB<br>TSUBMNTB |
| 6 | `/searchSubGoodsList` | 부가 상품 조회 | `@RequestParam` | `List` | SELECT | TCLASSVW |
| 7 | `/selectSubGoodsList` | drag용 상품 조회 (stockFg 뷰 분기) | `@RequestParam` | `ModelAndView` | SELECT | TGOODSTB<br>TMSCLSTB<br>TPRICETB |
| 8 | `/regiGoodsKey` | 상품키 등록 (삭제 후 재등록, pluCd/clpluCd 패딩) | `@RequestParam` | `String` | CUD | TSUBMNTB |
| 9 | `/removeGoodsKey` | 상품키 삭제 (배열 루프) | `@RequestParam` 배열 | `Map` | DELETE | TSUBMNTB |
| 10 | `/moveGoodsKey` | 상품키 이동 (for 루프 2회 버그) | `@RequestParam` | `String` | UPDATE | TSUBMNTB |
| 11 | `/searchMoveCategory` | 분류이동 모달용 분류 조회 | `@RequestParam` | `List` | SELECT | TMBUMSTB<br>TSUBMNTB |
| 12 | `/moveCategory` | 상품키 분류 이동 (userId 하드코딩) | `@RequestParam` | `Map` | UPDATE | TSUBMNTB |

---

## 1. `/search` — 분류 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 1-1 | msNo=`MS001` | `startKey=01&lastKey=99` | 분류 목록 + cnt |
| 1-2 | - | `startKey` 없음 | 400 (required=true) |

---

## 2. `/goodsKeySearch` — 상품키 조회

**`setZeroValue` 버그**: groupCd=0 → "0" → 참조비교 false → group_cd="0" ★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | msNo=`MS001` | `startKey=01&lastKey=99&groupCd=01` | 해당 분류 상품키 목록 |
| 2-2 | msNo=`MS001` | `groupCd=0` | setZeroValue→"0"→참조비교 false→"0" ★★ |
| 2-3 | - | `groupCd=abc` | `Integer.parseInt("abc")` → **NumberFormatException** ★★ |

---

## 3. `/updateCategoryNm` — 분류명 저장

**St_Master_00010 대비 차이**: `msNo` 파라미터로 직접 전달 (세션 아님), `selectMsNo` 파라미터명

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 3-1 | ID=`I000449s`, chainNo=`C001` | `searchPluCd=01&pluNm=음료&selectMsNo=MS001&formFg=I` | `"insert"` |
| 3-2 | ID=`I000449s`, chainNo=`C001` | `formFg=U` | `"update"` |
| 3-3 | ID=`I000449s`, chainNo=`C001` | `pluNm=기존명` | 중복 → `"dupl"` |
| 3-4 | - | `pluNm` 121자 이상 | 400 (@Size max=120) |
| 3-5 | - | `selectMsNo` 없음 | 400 (@NotBlank) |

---

## 4. `/removeGoodsCategory` — 분류 삭제

**타입 주의**: `int[]` 배열 — Spring이 자동 변환, 숫자 아니면 400

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 4-1 | chainNo=`C001` | `removePluCd[]=1` | 패딩("01") 후 삭제 → `"remove"` |
| 4-2 | chainNo=`C001` | `removePluCd[]=1&removePluCd[]=2` | 2건 루프 삭제 |
| 4-3 | chainNo=`C001` | `removePluCd[]=0` | setZeroValue→"0"→참조비교→"0" ★★ |
| 4-4 | - | `removePluCd[]` 없음 | 400 |

---

## 5. `/moveGoodsCategory` — 분류코드 이동

**for 루프 2회 버그** (St_Master_00010과 동일):
```java
for(int i = 0; i < 2; i++) {
    commandMap = new HashMap<>();   // 새 map 생성
    pluCdStr0 = setZeroValue(movePluCd[0],2);  // movePluCd.length < 2 → ArrayIndexOutOfBounds ★★★
    pluCdStr1 = setZeroValue(movePluCd[1],2);
    commandMap = new HashMap<>();   // 또 새 map (첫 map 버려짐)
    commandMap.put(...);
}
// 루프 종료 후 userId, chainNo 추가
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 5-1 | ID=`I000449s`, chainNo=`C001` | `movePluCd[]=1&movePluCd[]=2` | 3단계 swap → `"move"` |
| 5-2 | - | `movePluCd[]=1` (1개) | `movePluCd[1]` → **ArrayIndexOutOfBoundsException** ★★★ |
| 5-3 | - | `movePluCd[]` 없음 | 400 |

---

## 6. `/searchSubGoodsList` — 부가 상품 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 6-1 | chainNo=`C001` | (파라미터 없음, 기본값 "") | 전체 부가메뉴 상품 |
| 6-2 | chainNo=`C001` | `lClassCd=L01&mClassCd=M01` | 분류 필터 |

---

## 7. `/selectSubGoodsList` — drag용 상품 조회

**stockFg 분기**: "2" → T07 뷰 / "3" → T08 뷰 / 그 외 → setViewName 미호출 → null 뷰 ★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 7-1 | chainNo=`C001` | `stockFg=2` | T07 뷰 |
| 7-2 | chainNo=`C001` | `stockFg=3` | T08 뷰 |
| 7-3 | chainNo=`C001` | `stockFg=1` (그 외) | setViewName 미호출 → null ★ |
| 7-4 | - | `stockFg` 없음 | 400 (required=true) |

---

## 8. `/regiGoodsKey` — 상품키 등록

**서비스**: `deleteGoodsKey()` → `insertGoodsKey()` (삭제 후 재등록)  
**stockFg != "2"** → price = "0" 강제 세팅

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 8-1 | ID=`I000449s`, chainNo=`C001` | `goodsCd=G001&clpluCd=1&pluCd=1&stockFg=1` | delete→insert → `"insertGoodsKey"`, price="0" |
| 8-2 | ID=`I000449s`, chainNo=`C001` | `stockFg=2&price=500` | price=500 그대로 |
| 8-3 | ID=`I000449s`, chainNo=`C001` | `pluCd=0` | setZeroValue→"0"→"0" ★★ |

---

## 9. `/removeGoodsKey` — 상품키 삭제

**배열 길이 불일치**: removeClpluCd 2개, removePluCd 1개 → `removeClpluCd[1]` → **ArrayIndexOutOfBoundsException** ★★★  
**반환**: `{"chkFg":"removeGoodsKey","selectedClpluCd":removeClpluCd[0]}`

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 9-1 | chainNo=`C001` | `removeClpluCd[]=01&removePluCd[]=001` | `{"chkFg":"removeGoodsKey","selectedClpluCd":"01"}` |
| 9-2 | chainNo=`C001` | 배열 길이 불일치 | **ArrayIndexOutOfBoundsException** ★★★ |

---

## 10. `/moveGoodsKey` — 상품키 이동 (for 루프 버그)

```java
for(int i = 0; i < 2; i++) {
    commandMap = new HashMap<>();  // 루프마다 새 map
    commandMap.put("movePluCd0", movePluCd[0]);  // movePluCd.length < 2 → ArrayIndexOutOfBounds ★★★
    commandMap.put("movePluCd1", movePluCd[1]);
}
// 루프 2회 → 두 번째 결과만 남음 (첫 번째 버려짐)
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 10-1 | ID=`I000449s`, chainNo=`C001` | `clpluCd=1&movePluCd[]=001&movePluCd[]=002` | `"moveGoodsKey"` |
| 10-2 | - | `movePluCd[]=001` (1개) | **ArrayIndexOutOfBoundsException** ★★★ |

---

## 11. `/searchMoveCategory` — 분류이동 모달 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 11-1 | chainNo=`C001` | `startKey=01&lastKey=99` | 분류 목록 |

---

## 12. `/moveCategory` — 분류 이동

**서비스 하드코딩**: `String userId = "astems000"` ★★  
**setZeroValue 버그**: newClpluCd=0 → "0" → 참조비교 → "0" ★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 12-1 | chainNo=`C001` | `newClpluCd=2&clpluCd=01&pluCd[]=001` | moveCategory → `{"newClpluCd":2,"chkFg":"moveCategory"}` (userId="astems000" 하드코딩) |
| 12-2 | chainNo=`C001` | `newClpluCd=0` | setZeroValue→"0"→참조비교→"0" ★★ |
| 12-3 | - | `pluCd[]` 없음 | 400 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/master/st_master_00011"
$f = "application/x-www-form-urlencoded"

# 1. 분류 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -ContentType $f -WebSession $session `
  -Body "startKey=01&lastKey=99"

# 3-1. 분류명 등록
Invoke-RestMethod -Uri "$base/updateCategoryNm" -Method POST -ContentType $f -WebSession $session `
  -Body "searchPluCd=01&pluNm=테스트&selectMsNo=MS001&formFg=I"

# 5-2. 분류이동 1개 배열 → ArrayIndexOutOfBounds
Invoke-RestMethod -Uri "$base/moveGoodsCategory" -Method POST -ContentType $f -WebSession $session `
  -Body "movePluCd[]=1"
# 예상: 500

# 8-1. 상품키 등록
Invoke-RestMethod -Uri "$base/regiGoodsKey" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCd=G001&clpluCd=1&pluCd=1&stockFg=1"
```

---

## 주요 검증 포인트

```
□ setZeroValue(0, n) → "0" + 참조비교 false → 보정 미작동 ★★ (컨트롤러+서비스 공통)
□ moveGoodsCategory/moveGoodsKey — movePluCd 1개 시 [1] → ArrayIndexOutOfBoundsException ★★★
□ moveGoodsCategory — for 루프 2회 commandMap 재생성 → 첫 번째 결과 버려짐 ★
□ moveGoodsKey — 동일한 for 루프 버그 ★
□ removeGoodsKey — removeClpluCd/removePluCd 길이 불일치 → ArrayIndexOutOfBoundsException ★★★
□ selectSubGoodsList — stockFg "2"/"3" 외 → setViewName 미호출 → null ★
□ moveCategory — userId = "astems000" 하드코딩 (세션 무시) ★★★
□ goodsKeySearch — groupCd 숫자 아님 → NumberFormatException ★★
□ @Validated 있음 — @NotBlank, @Size 위반 시 400
□ @Transactional rollbackFor Exception — regiGoodsKey(delete→insert), moveCategory rollback 보장
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] TMBUMSTB (CUD 작업)
│   └── (Trigger) Tr_TMBUMS_T01
└── [테이블] TSUBMNTB (CUD 작업)
    └── (Trigger) Tr_TSUBMN_T01
```
