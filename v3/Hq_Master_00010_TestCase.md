# Hq_Master_00010 — 본사 POS 터치키 상품 등록 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > POS 터치키 상품 등록  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00010`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 일부 = `@RequestBody` / 일부 = `@RequestParam`
> **DB 트리거 영향도**: MMCPLUTB, MMCPLKTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## ⚠️ 반복 버그 패턴 (컨트롤러 + 서비스 공통)

```java
// setZeroValue(0, num) → "0" 반환 (기대값 "00" 또는 "000") ★★
if(value == 0) return "0";

// 이후 참조 비교(==)로 보정 시도하지만 항상 false ★★★
if(clplu_cd == "0") clplu_cd = "00";   // == 비교 → 절대 true 되지 않음

// moveGoodsCategory — movePluCdList 1개만 전달 시
movePluCdList.get(1)  // → IndexOutOfBoundsException ★★★
```

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | searchApplyShop, applyShop, applyCategoryShop, goodsKeySearch, TreeGoodsClass |
| `ID` | `I000449` | updateCategoryNm, moveGoodsCategory, applyShop, applyCategoryShop, regiGoodsKey, removeGoodsKey, moveGoodsKey, moveCategory |

---

## 엔드포인트 목록 (13개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 터치키 분류 목록 조회 | `@RequestBody` | `Map` (cnt+list) | SELECT | MGOODSTB<br>MMCPLKTB<br>MMEMBSTB<br>MPRICETB |
| 2 | `/updateCategoryNm` | 분류 명칭 저장 (insert/update 분기) | `@RequestParam` | `String` | UPDATE | MMCPLUTB |
| 3 | `/moveGoodsCategory` | 분류 이동 (swap, 6단계) | `@RequestBody` | `String` | UPDATE | MMCPLKTB<br>MMCPLUTB |
| 4 | `/removeGoodsCategory` | 분류 삭제 (하위상품키 포함) | `@RequestBody` | `String` | DELETE | MMCPLKTB<br>MMCPLUTB |
| 5 | `/searchApplyShop` | 매장반영 대상 매장 조회 | `@RequestBody` | `List` | SELECT | MMEMBSTB |
| 6 | `/applyShop` | 터치키 분류+상품 매장 반영 (8단계) | `@RequestParam` 배열 | `String` | INSERT | MMCPLKTB<br>MMCPLUTB<br>MMEMBSTB |
| 7 | `/searchCategory` | 분류 콤보 조회 | `@RequestParam` | `List` | SELECT | MMCPLUTB |
| 8 | `/applyCategoryShop` | 분류별 매장 반영 (4단계) | `@RequestParam` 배열 | `String` | UPDATE | MMCPLKTB<br>MMCPLUTB |
| 9 | `/goodsKeySearch` | 상품키 목록 조회 | `@RequestParam` | `Map` | SELECT | MGOODSTB<br>MMCPLKTB<br>MPRICETB |
| 10 | `/searchGoodsList` | 상품키 등록용 상품 조회 | `@RequestParam` | `ModelAndView` | SELECT | MGOODSTB<br>MMCPLKTB<br>MPRICETB |
| 11 | `/regiGoodsKey` | 상품키 등록 | `@RequestParam` | `String` | INSERT | MMCPLKTB |
| 12 | `/removeGoodsKey` | 상품키 삭제 (배열) | `@RequestParam` 배열 | `String` | DELETE | MMCPLKTB |
| 13 | `/moveGoodsKey` | 상품키 이동 (3단계, movePluCd[0]/[1]) | `@RequestParam` 배열 | `String` | UPDATE | MMCPLKTB |
| 14 | `/moveCategory` | 상품키 분류 이동 | `@RequestParam` 배열 | `String` | UPDATE | MMCPLKTB |
| 15 | `/TreeGoodsClass` | 상품분류 jstree 데이터 조회 | `@RequestBody` | `List` | SELECT | TMLCLSTB<br>TMMCLSTB<br>TMSCLSTB |

---

## 1. `/search` — 터치키 분류 조회

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 1-1 | `{"msNo":"MS001","startKey":"1","lastKey":"20"}` | 분류 목록 + cnt |
| 1-2 | `{}` | msNo/startKey/lastKey null → 전체 또는 빈 목록 |

---

## 2. `/updateCategoryNm` — 분류 명칭 저장

**서비스**: `chkDulpCategoryNm()` > 0 → `"dupl"` / formFg="U" → update / 그 외 → insert

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | ID=`I000449` | `searchPluCd=01&pluNm=분류A&selectMsNo=MS001&formFg=I` | `"insert"` |
| 2-2 | (동일) | `formFg=U` (기존 pluCd) | `"update"` |
| 2-3 | (동일) | 중복된 pluNm | `"dupl"` |
| 2-4 | - | `searchPluCd` 없음 | 400 (@NotBlank) |
| 2-5 | - | `pluNm` 21자 이상 | 400 (@Size max=20) |
| 2-6 | updateCategoryNm 감사 타입 확인 | MMSLOGTB 조회 후 TYPE 컬럼 | `SELECT`로 기록됨 (오분류) ★ |

---

## 3. `/moveGoodsCategory` — 분류 이동

**★ movePluCd 1개 전달**: `movePluCdList.get(1)` → **IndexOutOfBoundsException** ★★★  
**★ `pluCdStr0 == "0"` 참조 비교**: 절대 true 아님 → "00" 보정 불가 ★★★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | ID=`I000449` | `{"movePluCd":["1","2"],"msNo":"MS001"}` | 6단계 swap → `"move"` |
| 3-2 | (동일) | `{"movePluCd":["0","1"],"msNo":"MS001"}` | setZeroValue(0,2)→"0", `"0"=="0"` false → pluCdStr="0" ★★★ |
| 3-3 | (동일) | `{"movePluCd":["1"],"msNo":"MS001"}` | `get(1)` → **IndexOutOfBoundsException** ★★★ |
| 3-4 | (동일) | movePluCd 없음 | `(List)null` → `null.get(0)` → **NPE** ★★★ |
| 3-5 | movePluCd[1]=0 케이스 | `{"movePluCd":["1","0"],...}` | pluCdStr1="0" 서비스 전달 (버그: "00" 이어야 함) ★★ |

---

## 4. `/removeGoodsCategory` — 분류 삭제

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 4-1 | `{"msNo":"MS001","removePluCd":"01"}` | 하위 상품키 삭제 → 분류 삭제 → `"remove"` |

---

## 5. `/applyShop` — 매장 반영 (8단계)

**서비스**: deleteCategoryBk → deleteGoodsKeyBk → insertCategoryBk → insertGoodsKeyBk → deleteCategoryApplyShop → deleteGoodsKeyApplyShop → insertCategoryApplyShop → insertGoodsKeyApplyShop  
**★ list.get(0)**: list가 비어있으면 **IndexOutOfBoundsException** ★★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 5-1 | chainNo=`C001`, ID=`I000449` | `applyMsNo[]=MS002&selectedMsNo=MS001` | 8단계 실행 → `"applyShop"` |
| 5-2 | (동일) | `applyMsNo[]` 없음 | 400 (required=true) |
| 5-3 | searchApplyShop 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 9. `/goodsKeySearch` — 상품키 조회

**★ clpluCd 숫자 아님**: `Integer.parseInt(clpluCd)` → **NumberFormatException** ★★  
**★ `clplu_cd == "0"` 참조 비교**: 항상 false → "00" 보정 불가 ★★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 9-1 | chainNo=`C001` | `com_selectMsNo=MS001&startKey=1&lastKey=20&clpluCd=1` | 상품키 목록 + cnt |
| 9-2 | (동일) | `clpluCd=0` | setZeroValue(0,2)→"0", `"0"=="0"` false → clplu_cd="0" 로 조회 ★★★ |
| 9-3 | (동일) | `clpluCd=abc` | `Integer.parseInt("abc")` → **NumberFormatException** ★★ |
| 9-4 | - | `com_selectMsNo` 없음 | 400 (@NotBlank) |
| 9-5 | goodsKeySearch 감사 타입 확인 | MMSLOGTB 조회 후 TYPE 컬럼 | `UPDATE`로 기록됨 (오분류) ★ |

---

## 11. `/regiGoodsKey` — 상품키 등록

**★ pluCd=0**: setZeroValue(0,3)→"0", `"0"=="0"` false → pluCd="0" 로 INSERT ★★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 11-1 | ID=`I000449` | `goodsCd=G001&clpluCd=1&pluCd=5&selectedMsNo=MS001` | `"insertGoodsKey"` |
| 11-2 | (동일) | `pluCd=0` | pluCdStr="0" (기대값 "000") → 잘못된 PK ★★★ |
| 11-3 | clpluCd 문자 전달 | `clpluCd=abc` | int 파싱 실패 → **400** ★ |
| 11-4 | clpluCd 미전송 | clpluCd 없음 | required=true + int 타입 → **400** ★ |

---

## 13. `/moveGoodsKey` — 상품키 이동

**컨트롤러**: for(int i=0; i<2; i++) 루프에서 `commandMap = new HashMap` 재생성  
→ 루프 마지막 실행(i=1)의 값만 남음 (정상, movePluCd[0]/[1] 모두 put)  
**★ movePluCd[] 1개만 전달**: `movePluCd[1]` → **ArrayIndexOutOfBoundsException** ★★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 13-1 | ID=`I000449` | `clpluCd=1&movePluCd[]=3&movePluCd[]=5&msNo=MS001` | 3단계 이동 → `"moveGoodsKey"` |
| 13-2 | (동일) | `movePluCd[]=3` (1개만) | `movePluCd[1]` → **ArrayIndexOutOfBoundsException** ★★★ |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00010"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 분류 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001","startKey":"1","lastKey":"20"}'

# 3-3. movePluCd 1개 → IndexOutOfBounds
Invoke-RestMethod -Uri "$base/moveGoodsCategory" -Method POST -Headers $h -WebSession $session `
  -Body '{"movePluCd":["1"],"msNo":"MS001"}'
# 예상: 500

# 9-3. clpluCd 문자 → NumberFormatException
Invoke-RestMethod -Uri "$base/goodsKeySearch" -Method POST -ContentType $f -WebSession $session `
  -Body "com_selectMsNo=MS001&startKey=1&lastKey=20&clpluCd=abc"
# 예상: 500

# 13-2. movePluCd 1개 → ArrayIndexOutOfBounds
Invoke-RestMethod -Uri "$base/moveGoodsKey" -Method POST -ContentType $f -WebSession $session `
  -Body "clpluCd=1&movePluCd[]=3&msNo=MS001"
# 예상: 500
```

---

## 주요 검증 포인트

```
□ setZeroValue(0,n) → "0" 반환 + `"0"=="0"` 참조비교 false → 보정 실패 ★★★ (컨트롤러+서비스 공통)
□ moveGoodsCategory — movePluCdList 1개 → get(1) IndexOutOfBoundsException ★★★
□ moveGoodsCategory — movePluCdList null → NPE ★★★
□ goodsKeySearch/regiGoodsKey — clpluCd/pluCd=0 → "0" 로 DB 저장 ★★★
□ goodsKeySearch — clpluCd 숫자 아님 → NumberFormatException ★★
□ moveGoodsKey — movePluCd 1개 → movePluCd[1] ArrayIndexOutOfBoundsException ★★★
□ applyShop — list.get(0) → list 비어있으면 IndexOutOfBoundsException ★★★
□ moveCategory 서비스 — newPluCd=="0" 참조비교 false → 보정 실패 ★★★
□ applyShop 서비스 — 8단계 원자성 (rollbackFor Exception)
□ moveGoodsCategory 서비스 — 6단계 swap 원자성 (rollbackFor Exception)
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
