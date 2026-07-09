# St_Master_00002 — 매장 상품 조회 단위 테스트케이스

> **화면**: [ST] 마스터관리 > 상품관리 > 상품조회  
> **URL Prefix**: `POST /backoffice/data/st/master/st_master_00002`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 페이징 조회 = `@RequestBody` / 단건 조회/삭제 = `@RequestParam`
> **DB 트리거 영향도**: TMSSRCTB, TPRICETB, TGOODSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | 전 엔드포인트 |
| `chainMsNo` | `NC0001` | modalSearch, getRecipe, delete |
| `msNo` | `MS001` | modalSearch, delete, getShopBrandCd |
| `ID` | `I000449s` | modalSearch, delete |

---

## 엔드포인트 목록 (11개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 상품 목록 조회 (페이징, 배송유형 매핑) | `@RequestBody` | `Map` (total+rows) | SELECT | TGOODSTB |
| 2 | `/modalSearch` | 상품 상세 조회 (setFg 분기, 레시피/세트) | `@RequestParam` | `Map` | SELECT | MNAMEMTB<br>TCHAINTB<br>TGOODSTB<br>TMBUMSTB<br>TPRICETB |
| 3 | `/getRecipe` | 레시피 조회 | `@RequestParam` | `List` | SELECT | MNAMEMTB |
| 4 | `/getSet` | 세트 구성 상품 조회 | `@RequestParam` | `List` | SELECT | TGOODSTB |
| 5 | `/getAllRecipe` | 원부재료 기준 전체 레시피 조회 | `@RequestParam` | `List` | SELECT | MMEMBSTB |
| 6 | `/delete` | 상품 삭제 (수불/매출 체크 선행) | `@RequestParam` | `String` | DELETE | IMCRIOTB<br>MMEMBSTB<br>SGOODMTB<br>TGOODSTB<br>TPRICETB |
| 7 | `/getExtra` | 부가메뉴 조회 | (파라미터 없음) | `List` | SELECT | TMBUMSTB |
| 8 | `/recpSearch` | 레시피 목록 조회 (페이징) | `@RequestBody` | `Map` (total+rows) | SELECT | TGOODSTB |
|9|`/getSpecInfo`|레시피 구성상품 조회|`@RequestParam`|`List`|SELECT| 공통 모듈/동적 쿼리 (추적 불가) |
| 10 | `/setUnitSearch` | 세트 구성 상품 추가 조회 (hid_alry_recpUnit CSV 파싱) | `@RequestBody` | `Map` (total+rows) | SELECT | TGOODSTB |
| 11 | `/getShopBrandCd` | 브랜드샵 여부 조회 | (파라미터 없음) | `String` | SELECT | TCHAINTB |
| 12 | `/getDeptList` | 부서 목록 조회 | (파라미터 없음) | `List` | SELECT | TDEPTMTB |

---

## 1. `/search` — 상품 목록 조회

**서비스**: `getDeliveryType()` 전체 조회 후 이중 루프로 `deliveryTypeNm` 매핑  
**★ offset 미전달**: `(int)map.get("offset")` → **NPE** ★★★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"offset":0,"limit":10}` | 전체 상품 목록 + deliveryTypeNm 매핑 |
| 1-2 | chainNo=`C001` | `{"lclassCd":"L01","mclassCd":"M01","offset":0,"limit":10}` | 분류 필터 |
| 1-3 | chainNo=`C001` | `{"goodsNm":"커피","offset":0,"limit":10}` | 이름 검색 |
| 1-4 | chainNo=`C001` | `{"offset":0,"limit":10,"setFg":"2"}` | 레시피 상품 필터 |
| 1-5 | chainNo=`C001` | `{}` (offset 없음) | **NPE** ★★★ |

---

## 2. `/modalSearch` — 상품 상세 조회

**서비스 처리**:
```
getModalList()         → 상세 DTO (setFg, recipeCd, setCd 포함)
getExtraSubList()      → 부가메뉴 목록
getShopBrandCd()       → 브랜드샵 여부

setFg == "2" → getRecipe()   (레시피 상품)
setFg == "3" → getSetList()  (세트 상품)
else         → recipeList=[], setUnitList=[]

★ getModalList() null 반환 시:
  master_00002_modalList.getSetFg() → NPE ★★★
  master_00002_modalList.getRecipeCd() → NPE
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | chainNo=`C001`, msNo=`MS001` | `goodsCd=G001` (일반 상품, setFg=1) | modalList + extraSubList, recipeList=[], setUnitList=[] |
| 2-2 | chainNo=`C001`, msNo=`MS001` | `goodsCd=G002` (레시피 상품, setFg=2) | + recipeList 조회 |
| 2-3 | chainNo=`C001`, msNo=`MS001` | `goodsCd=G003` (세트 상품, setFg=3) | + setUnitList 조회 |
| 2-4 | chainNo=`C001`, msNo=`MS001` | `goodsCd=INVALID` (없는 코드) | getModalList() → null → **NPE** ★★★ |
| 2-5 | chainNo=`C001`, msNo=`MS001` | 파라미터 없음 (defaultValue="") | goodsCd="" → 전체 중 첫 번째 또는 null 반환 |

---

## 3. `/getRecipe` — 레시피 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 3-1 | chainNo=`C001`, chainMsNo=`NC0001` | `recpCd=RECP001&goodsCd=G001` | 레시피 구성 상품 목록 |
| 3-2 | - | `recpCd` 없음 | 400 (@NotBlank) |

---

## 4. `/getSet` — 세트 구성 상품 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 4-1 | chainNo=`C001` | `goodsCd=G003&setCd=SET001` | 세트 구성 상품 목록 |
| 4-2 | - | `goodsCd` 없음 | 400 (@NotBlank) |

---

## 5. `/getAllRecipe` — 원부재료 기준 레시피 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 5-1 | chainNo=`C001` | `goodsCd=G001` | 해당 상품을 원부재료로 사용하는 레시피 목록 |
| 5-2 | - | `goodsCd` 없음 | 400 (required=true, @NotBlank 없음) → Spring 처리 |

---

## 6. `/delete` — 상품 삭제

**서비스 처리**:
```
chkImcriotb() > 0 → chkFg = "imcro1"  (수불 이력 존재)
chkSgoodmtb() > 0 → chkFg = "sgood1"  (매출 이력 존재)
chkFg == ""   → deleteGoods():
  getSaveSetCd() → set_cd 조회
  set_cd != null && set_cd != "" → delTbSetGoods
  deleteGoods → deleteTprice

★ set_cd != "" 비교: == "" 와 .equals("") 혼용 → != "" 는 참조 비교 → 항상 true 가능 ★★
```

| No | 세션 조건 | DB 선행상태 | Request | 예상값 |
|----|----------|------------|---------|-------|
| 6-1 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | 수불/매출 이력 없음 | `goodsCd=G001` | deleteGoods → `""` |
| 6-2 | chainNo=`C001`, msNo=`MS001` | 수불 이력 있음 | `goodsCd=G001` | `"imcro1"` |
| 6-3 | chainNo=`C001`, msNo=`MS001` | 매출 이력 있음 | `goodsCd=G001` | `"sgood1"` |
| 6-4 | chainNo=`C001`, msNo=`MS001` | 수불+매출 모두 있음 | `goodsCd=G001` | `"sgood1"` (sgood1이 마지막으로 덮어씀) |
| 6-5 | chainNo=`C001`, msNo=`MS001` | 세트상품 (set_cd 있음) | `goodsCd=G003` | `set_cd != ""` 참조비교 → delTbSetGoods 실행 여부 확인 ★★ |

---

## 7. `/getExtra` — 부가메뉴 조회

| No | 세션 조건 | 예상값 |
|----|----------|-------|
| 7-1 | chainNo=`C001` | 전체 부가메뉴 목록 |

---

## 8. `/recpSearch` — 레시피 목록 조회 (페이징)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 8-1 | chainNo=`C001` | `{"offset":0,"limit":10}` | 전체 레시피 목록 |
| 8-2 | chainNo=`C001` | `{"recp_nm":"라떼","offset":0,"limit":10}` | 이름 필터 |
| 8-3 | chainNo=`C001` | `{}` (offset 없음) | **NPE** ★★★ |

---

## 9. `/getSpecInfo` — 레시피 구성상품 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 9-1 | chainNo=`C001` | `recp_cd=RECP001` | 레시피 구성 원부재료 목록 |
| 9-2 | - | `recp_cd` 없음 | 400 (@NotBlank) |

---

## 10. `/setUnitSearch` — 세트 구성 상품 추가 조회

**`hid_alry_recpUnit` 처리**:
```java
String[] arr = String.valueOf(map.get("hid_alry_recpUnit")).split(",");
// map.get("hid_alry_recpUnit") = null → String.valueOf(null) = "null" → arr=["null"]
// → list=["null"] → Mapper IN("null") 조건 → 유효 상품코드가 아닌 "null" 문자열 ★
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 10-1 | chainNo=`C001` | `{"hid_alry_recpUnit":"G001,G002","offset":0,"limit":10}` | G001, G002 제외한 상품 목록 |
| 10-2 | chainNo=`C001` | `{"hid_alry_recpUnit":"","offset":0,"limit":10}` | split("") → `[""]` → Mapper IN 처리 |
| 10-3 | chainNo=`C001` | `{"offset":0,"limit":10}` (hid_alry_recpUnit 없음) | `String.valueOf(null)="null"` → list=["null"] ★ |
| 10-4 | chainNo=`C001` | `{}` (offset 없음) | **NPE** ★★★ |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/master/st_master_00002"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 상품 목록
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'

# 2-1. 상품 상세
Invoke-RestMethod -Uri "$base/modalSearch" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCd=G001"

# 6-1. 삭제 (이력 없음)
Invoke-RestMethod -Uri "$base/delete" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCd=G001"
# 예상: "" (성공)

# 8-1. 레시피 검색
Invoke-RestMethod -Uri "$base/recpSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'

# 10-3. setUnitSearch hid_alry_recpUnit 없음 → "null" 문자열
Invoke-RestMethod -Uri "$base/setUnitSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'
```

---

## 주요 검증 포인트

```
□ search/recpSearch/setUnitSearch — offset 미전달 → (int)map.get("offset") NPE ★★★
□ modalSearch — getModalList() null → .getSetFg() NPE ★★★ (없는 goodsCd 전달 시)
□ setUnitSearch — hid_alry_recpUnit 미전달 → String.valueOf(null)="null" → IN("null") ★★
□ delete — set_cd != "" 참조 비교 → .equals("") 와 혼용 → 항상 true 가능 (set_cd="" 미삭제 가능) ★★
□ delete — imcro1/sgood1 동시 해당 시 sgood1이 덮어씀 (imcro1 소실)
□ updateGoods/insertGoods — 서비스에 있지만 컨트롤러에 엔드포인트 없음 → 다른 경로로 호출되거나 미사용 확인
□ modalSearch — setFg 분기: "2"=레시피, "3"=세트, 나머지=빈 목록
□ @Validated 있음 — @NotBlank 위반 시 400
□ @Transactional rollbackFor Exception — deleteGoods rollback 보장
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] TGOODSTB (CUD 작업)
│   └── (Trigger) Tr_TGOODS_T01
├── [테이블] TMSSRCTB (CUD 작업)
│   └── (Trigger) Tr_TMSSRC_T01
└── [테이블] TPRICETB (CUD 작업)
    └── (Trigger) Tr_TPRICE_T01
```
