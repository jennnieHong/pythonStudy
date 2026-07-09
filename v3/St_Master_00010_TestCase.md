# St_Master_00010 — POS 상품 터치키 등록 단위 테스트케이스

> **화면**: [ST] 마스터관리 > POS 터치키 등록  
> **URL Prefix**: `POST /backoffice/data/st/master/st_master_00010`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 조회 = `@RequestBody` / CUD = `@RequestParam`
> **DB 트리거 영향도**: MMCPLUTB, MMCPLKTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## `setZeroValue(value, num)` 공통 버그

컨트롤러와 서비스 양쪽에 동일하게 존재:
```java
if(value == 0) return "0";   // 0이면 "0" 반환 (패딩 안 됨)
// 이후 코드: if(pluCdStr == "0") ... → 참조 비교 → 항상 false ★★
// 따라서 value=0 → "0" 반환 후 보정 코드가 동작 안 함
// 결과: plu_cd = "0" (기대값 "000" 또는 "00") → DB PK 오류 가능
```

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `msNo` | `MS001` | search, updateCategoryNm, goodsKeySearch, searchCategory, moveCategory |
| `chainNo` | `C001` | searchApplyShop, applyShop, applyCategoryShop, TreeGoodsClass |
| `ID` | `I000449s` | updateCategoryNm, moveGoodsCategory, applyShop, applyCategoryShop, regiGoodsKey, moveGoodsKey |

---

## 엔드포인트 목록 (14개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 상품 터치키 분류 조회 | `@RequestBody` | `Map` (cnt+goodsCategoryList) | SELECT | MGOODSTB<br>MMCPLKTB<br>MMEMBSTB<br>MPRICETB |
| 2 | `/updateCategoryNm` | 분류명 저장 (중복체크 → insert/update 분기) | `@RequestParam` | `String` | MMCPLUTB |
| 3 | `/moveGoodsCategory` | 분류코드 이동 (3단계 swap) | `@RequestBody` | `String` | UPDATE | MMCPLKTB<br>MMCPLUTB |
| 4 | `/removeGoodsCategory` | 분류 삭제 (하위 상품키 포함) | `@RequestBody` | `String` | DELETE | MMCPLKTB<br>MMCPLUTB |
| 5 | `/searchApplyShop` | 매장반영 대상 매장 조회 | `@RequestBody` | `List` | SELECT | MMEMBSTB |
| 6 | `/applyShop` | 매장 터치키 반영 (BK 저장 → 삭제 → 재삽입) | `@RequestParam` 배열 | `String` | MMCPLKTB<br>MMCPLUTB<br>MMEMBSTB |
| 7 | `/searchCategory` | 분류 콤보 조회 (세션 msNo 사용) | (파라미터 없음) | `List` | SELECT | MMCPLUTB |
| 8 | `/applyCategoryShop` | 분류별 매장 반영 | `@RequestParam` 배열 | `String` | MMCPLKTB<br>MMCPLUTB |
| 9 | `/goodsKeySearch` | 상품키 조회 (clpluCd 패딩) | `@RequestParam` | `Map` | SELECT | MGOODSTB<br>MMCPLKTB<br>MPRICETB |
| 10 | `/st_master_00010/searchGoodsList` | 상품키 등록용 상품 조회 | `@RequestParam` | `ModelAndView` | SELECT | MGOODSTB<br>MMCPLKTB<br>MPRICETB |
| 11 | `/regiGoodsKey` | 상품키 등록 (pluCd/clpluCd 패딩) | `@RequestParam` | `String` | INSERT | MMCPLKTB |
| 12 | `/removeGoodsKey` | 상품키 삭제 (배열 루프) | `@RequestParam` 배열 | `String` | DELETE | MMCPLKTB |
| 13 | `/moveGoodsKey` | 상품키 이동 (for 루프 2회 버그) | `@RequestParam` | `String` | UPDATE | MMCPLKTB |
| 14 | `/TreeGoodsClass` | 상품분류 Tree 조회 (3중 루프) | `@RequestBody` | `List` | SELECT | TMLCLSTB<br>TMMCLSTB<br>TMSCLSTB |

---

## 1. `/search` — 분류 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | msNo=`MS001` | `{"startKey":"01","lastKey":"99"}` | 터치키 분류 목록 + cnt |
| 1-2 | msNo=`MS001` | `{}` (startKey/lastKey 없음) | null 전달 → Mapper SQL 처리 확인 |

---

## 2. `/updateCategoryNm` — 분류명 저장

**서비스**: `chkDulpCategoryNm()` → 중복 → "dupl" / `formFg="U"` → update / else → insert

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | msNo=`MS001`, ID=`I000449s` | `searchPluCd=01&pluNm=음료&formFg=I` | 중복 없음 → `"insert"` |
| 2-2 | msNo=`MS001`, ID=`I000449s` | `searchPluCd=01&pluNm=음료&formFg=U` | 중복 없음 → `"update"` |
| 2-3 | msNo=`MS001`, ID=`I000449s` | `searchPluCd=01&pluNm=기존분류명&formFg=I` | 중복 → `"dupl"` |
| 2-4 | - | `pluNm` 없음 | 400 (@NotBlank) |
| 2-5 | - | `pluNm` 21자 | 400 (@Size max=20) |

---

## 3. `/moveGoodsCategory` — 분류코드 이동

**컨트롤러 버그**:
```java
pluCdStr0 = setZeroValue(Integer.parseInt(movePluCdList.get(0)),2);
pluCdStr1 = setZeroValue(Integer.parseInt(movePluCdList.get(1)),2);
if(pluCdStr0 == "0") pluCdStr0 = "00";  // 참조비교 → 항상 false ★★
else if(pluCdStr1 == "0") pluCdStr0 = "00";  // 같은 문제 + pluCdStr0 덮어씌움 ★
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | ID=`I000449s` | `{"movePluCd":["01","02"],"msNo":"MS001"}` | 3단계 swap → `"move"` |
| 3-2 | - | `{"movePluCd":["0","02"],"msNo":"MS001"}` | value=0 → setZeroValue → "0" → 참조비교 false → pluCd="0" → DB 오류 ★★ |
| 3-3 | - | `{"movePluCd":null}` | `movePluCdList.get(0)` → **NPE** ★★★ |
| 3-4 | - | `{"movePluCd":["01"]}` (1개만) | `movePluCdList.get(1)` → **IndexOutOfBoundsException** ★★★ |

---

## 4. `/removeGoodsCategory` — 분류 삭제

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 4-1 | `{"msNo":"MS001","removePluCd":"01"}` | 하위 상품키 삭제 → 분류 삭제 → `"remove"` |
| 4-2 | `{"msNo":"MS001","removePluCd":"INVALID"}` | 0건 삭제 → `"remove"` |

---

## 5. `/searchApplyShop` — 매장 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | chainNo=`C001` | `{"selectedMsNo":"MS001"}` | 체인 내 매장 목록 |
| 5-2 | chainNo=`C001` | `{}` (selectedMsNo 없음) | `reqMap.get("selectedMsNo")=null` → Mapper null 처리 |

---

## 6. `/applyShop` — 매장 터치키 반영

**서비스**: BK 삭제 → BK 삽입 → 기존 삭제 → 재삽입 (6단계)  
**컨트롤러**: selectedMsNo와 applyMsNo[i]가 같으면 `applyMsNo` 미세팅

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 6-1 | ID=`I000449s`, chainNo=`C001` | `applyMsNo[]=MS002&selectedMsNo=MS001` | MS001→MS002 반영 → `"applyShop"` |
| 6-2 | ID=`I000449s`, chainNo=`C001` | `applyMsNo[]=MS001&selectedMsNo=MS001` | 동일 매장 → applyMsNo 미세팅 → 자기 자신에 반영 확인 |
| 6-3 | - | `applyMsNo[]` 없음 | 400 (required=true) |

---

## 7. `/searchCategory` — 분류 콤보

| No | 세션 조건 | 예상값 |
|----|----------|-------|
| 7-1 | msNo=`MS001` | 해당 매장 분류 목록 |

---

## 8. `/applyCategoryShop` — 분류별 매장 반영

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 8-1 | ID=`I000449s`, chainNo=`C001` | `applyMsNo[]=MS002&selectedMsNo=MS001&selectedClpluCd=01` | 분류 반영 → `"applyCategory"` |
| 8-2 | - | `selectedClpluCd` 없음 | 400 (required=true) |

---

## 9. `/goodsKeySearch` — 상품키 조회

**`setZeroValue(clpluCdToInt,2)` 버그**: clpluCd="0" → "0" 반환 → `if(clplu_cd == "0")` 참조비교 → false → clplu_cd="0" ★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 9-1 | msNo=`MS001`, chainNo=`C001` | `startKey=01&lastKey=99&clpluCd=01` | 해당 분류 상품키 목록 + cnt |
| 9-2 | msNo=`MS001`, chainNo=`C001` | `clpluCd=0` | setZeroValue → "0" → 참조비교 false → clplu_cd="0" ★★ |
| 9-3 | - | `clpluCd=abc` | `Integer.parseInt("abc")` → **NumberFormatException** ★★ |
| 9-4 | - | `clpluCd` 없음 | 400 (required=true) |

---

## 10. `/st_master_00010/searchGoodsList` — 상품키 등록용 상품 조회

**특이사항**: URL에 prefix 중복 (`/backoffice/data/st/master/st_master_00010/st_master_00010/searchGoodsList`) ★

| No | Request | 예상값 |
|----|---------|-------|
| 10-1 | `msNo=MS001` | ModelAndView → 상품 목록 |
| 10-2 | `msNo` 없음 | 400 (required=true) |

---

## 11. `/regiGoodsKey` — 상품키 등록

**`setZeroValue` 버그**: pluCd=0 → "0" → 참조비교 false → pluCd="0" ★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 11-1 | ID=`I000449s` | `goodsCd=G001&clpluCd=1&pluCd=1&selectedMsNo=MS001` | `"insertGoodsKey"` |
| 11-2 | ID=`I000449s` | `pluCd=0` | setZeroValue → "0" → DB PK 오류 가능 ★★ |
| 11-3 | - | `goodsCd` 없음 | 400 (required=true) |

---

## 12. `/removeGoodsKey` — 상품키 삭제

**배열 길이 불일치**: removeClpluCd 2개, removePluCd 1개 → `removeClpluCd[1]` → **ArrayIndexOutOfBoundsException** ★★★

| No | Request | 예상값 |
|----|---------|-------|
| 12-1 | `removeClpluCd[]=01&removePluCd[]=001&msNo=MS001` | `"removeGoodsKey"` |
| 12-2 | 배열 길이 불일치 | **ArrayIndexOutOfBoundsException** ★★★ |
| 12-3 | `removeClpluCd[]` 없음 | 400 (required=true) |

---

## 13. `/moveGoodsKey` — 상품키 이동

**컨트롤러 버그**:
```java
for(int i = 0; i < 2; i++) {
    commandMap = new HashMap<>();   // ← 루프마다 새 map → 첫 번째 put 버려짐
    commandMap.put("movePluCd0", movePluCd[0]);
    commandMap.put("movePluCd1", movePluCd[1]);  // movePluCd 길이 < 2 → ArrayIndexOutOfBounds ★★★
}
// 최종 commandMap = 2번째 이터레이션 결과 (동일 내용으로 덮어씀)
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 13-1 | ID=`I000449s` | `clpluCd=1&movePluCd[]=001&movePluCd[]=002&msNo=MS001` | `"moveGoodsKey"` |
| 13-2 | ID=`I000449s` | `movePluCd[]=001` (1개만) | `movePluCd[1]` → **ArrayIndexOutOfBoundsException** ★★★ |

---

## 14. `/TreeGoodsClass` — 상품분류 Tree 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 14-1 | chainNo=`C001` | `{}` | 대/중/소 분류 3중 루프 Tree 구조 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/master/st_master_00010"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 분류 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"startKey":"01","lastKey":"99"}'

# 2-1. 분류명 저장 (insert)
Invoke-RestMethod -Uri "$base/updateCategoryNm" -Method POST -ContentType $f -WebSession $session `
  -Body "searchPluCd=01&pluNm=음료&formFg=I"
# 예상: "insert"

# 3-4. movePluCd 1개만 → IndexOutOfBoundsException
Invoke-RestMethod -Uri "$base/moveGoodsCategory" -Method POST -Headers $h -WebSession $session `
  -Body '{"movePluCd":["01"],"msNo":"MS001"}'
# 예상: 500

# 9-3. clpluCd 숫자 아님 → NumberFormatException
Invoke-RestMethod -Uri "$base/goodsKeySearch" -Method POST -ContentType $f -WebSession $session `
  -Body "startKey=01&lastKey=99&clpluCd=abc"
# 예상: 500

# 11-1. 상품키 등록
Invoke-RestMethod -Uri "$base/regiGoodsKey" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCd=G001&clpluCd=1&pluCd=1&selectedMsNo=MS001"
```

---

## 주요 검증 포인트

```
□ setZeroValue(0, n) → "0" 반환 후 == "0" 참조비교 → 항상 false → 보정 미작동 ★★ (컨트롤러+서비스 공통)
□ moveGoodsCategory — movePluCd 1개 시 get(1) IndexOutOfBoundsException ★★★
□ moveGoodsCategory — else if(pluCdStr1=="0") pluCdStr0="00" → pluCdStr0 덮어씌움 버그 ★
□ moveGoodsKey — for(i<2) 루프 내 commandMap 재생성 → 첫 번째 이터레이션 결과 버려짐 ★
□ moveGoodsKey — movePluCd[1] 참조 → 배열 1개 시 ArrayIndexOutOfBoundsException ★★★
□ goodsKeySearch — clpluCd 숫자 아님 → NumberFormatException ★★
□ searchGoodsList — URL 중복 경로 확인 필요
□ applyShop — 6단계 DB 조작: BK삭제→BK삽입→기존삭제→재삽입 → 중간 실패 시 @Transactional rollback 보장
□ removeGoodsKey — removeClpluCd/removePluCd 길이 불일치 → ArrayIndexOutOfBoundsException ★★★
□ @Validated 있음 — @NotBlank, @Size 위반 시 400
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] MMCPLKTB (CUD 작업)
│   └── (Trigger) Tr_MMCPLK_T01
└── [테이블] MMCPLUTB (CUD 작업)
    └── (Trigger) Tr_MMCPLU_T01
```
