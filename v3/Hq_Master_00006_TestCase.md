# Hq_Master_00006 — 상품 등록/조회 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > 상품관리 > 상품 등록/조회  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00006`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 주의**: `search`, `recpSearch`, `setUnitSearch` = `@RequestBody`, 나머지 = `@RequestParam` (form-data)
> **DB 트리거 영향도**: TMSSRCTB, TVNDRGTB, TPRICETB, TGOODSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 (컬럼명: `chain_no`) |
| `chainMsNo` | `NC0001` | 체인 본부 매장번호 |
| `msNo` | `MS001` | 본인 매장번호 |
| `ID` | `7249525SHOP` | 로그인 사용자 ID |

---

## 엔드포인트 목록 (13개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | 요청 방식 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/search` | 상품 목록 조회 (페이징, deliveryType 맵핑) | `@RequestBody` | SELECT | TGOODSTB |
| 2 | `/modalSearch` | 상품 상세조회 (setFg 분기: 레시피/세트) | `@RequestParam` | SELECT | MMEMBSTB<br>MNAMEMTB<br>OBSLPDTB<br>OBSLPHTB<br>TCHAINTB<br>TGOODSTB<br>TMBUMSTB<br>TPRICETB |
| 3 | `/getRecipe` | 레시피 조회 | `@RequestParam` | SELECT | MNAMEMTB<br>TPRICETB |
| 4 | `/getSet` | 세트 구성상품 조회 | `@RequestParam` | SELECT | TGOODSTB |
| 5 | `/getAllRecipe` | 원부재료 → 레시피 상품 전체 조회 | `@RequestParam` | SELECT | MMEMBSTB |
| 6 | `/delete` | 상품 삭제 (imcCnt/sgdCnt 2단계 체크) | `@RequestParam` | DELETE | TGOODSTB<br>TPRICETB |
| 7 | `/getExtra` | 부가메뉴 조회 | (no body) | SELECT | TMBUMSTB |
| 8 | `/recpSearch` | 레시피 검색 (페이징) | `@RequestBody` | SELECT | TGOODSTB |
|9|`/getSpecInfo`|레시피 리스트 상세 (구성상품)|`@RequestParam`|SELECT| 공통 모듈/동적 쿼리 (추적 불가) |
| 10 | `/setUnitSearch` | 세트 구성상품 추가시 검색 (hid_alry_recpUnit split) | `@RequestBody` | SELECT | TGOODSTB |
| 11 | `/update` | 상품 수정 (바코드 중복 다단계 + 세트 + 협력사) | `@RequestParam` | UPDATE | TPRICETB |
| 12 | `/insert` | 상품 등록 (MsErr/BcdDup + 브랜드샵 바코드 자동채번) | `@RequestParam` | INSERT | TGOODSTB |
| 13 | `/getShopBrandCd` | 브랜드샵 여부 조회 | (no body) | SELECT | TCHAINTB |
| 14 | `/getPartnerList` | 협력사 목록 조회 | (no body) | SELECT | TVNDRMTB |
| 15 | `/getDeptList` | 부서 목록 조회 | (no body) | SELECT | TDEPTMTB |

---

## 1. `/search` — 상품 목록 조회

**특이사항**: `selectGoodsList` → `getDeliveryType()`으로 배송 유형 코드 맵핑 (중첩 for문)

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainNo=`C001` | 상품 5건 | `{"offset":0,"limit":10}` | `{"total":5,"rows":[...]}` (deliveryTypeNm 맵핑 포함) |
| 1-2 | chainNo=`C001` | - | `{"offset":0,"limit":10,"lclassCd":"L01","useFg":"1"}` | 분류/사용여부 필터 |
| 1-3 | chainNo=`C001` | - | `{"offset":0,"limit":10,"goodsNm":"아메리카노"}` | 이름 검색 결과 |
| 1-4 | - | - | `{}` (offset 없음) | **ClassCastException** (`(int)map.get("offset")` → null) |

---

## 2. `/modalSearch` — 상품 상세조회

**분기**: `getModalList()` → `setFg` 값으로 레시피/세트 추가 조회

```
setFg = "2" → getRecipe() 추가
setFg = "3" → getSetList() 추가
그 외       → recipeList=[], setUnitList=[] 반환
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 2-1 | chainNo=`C001` | G001 (setFg=`1`, 일반) | `goodsCd=G001` | modalList + extraSubList + recipeList=[] + setUnitList=[] |
| 2-2 | chainNo=`C001` | G002 (setFg=`2`, 레시피) | `goodsCd=G002` | modalList + extraSubList + **recipeList 조회** + setUnitList=[] |
| 2-3 | chainNo=`C001` | G003 (setFg=`3`, 세트) | `goodsCd=G003` | modalList + extraSubList + recipeList=[] + **setUnitList 조회** |
| 2-4 | chainNo=`C001` | - | `goodsCd=` (빈값, defaultValue="") | getModalList null → `recp_cd`, `set_cd` getRecipeCd() **NPE** ★ |

---

## 3~5. 레시피/세트 조회

| No | URL | Request (form-param) | 예상값 |
|----|-----|----------------------|-------|
| 3-1 | `/getRecipe` | `recpCd=R001` | 레시피 구성 List |
| 3-2 | `/getRecipe` | `recpCd` 없음 | 400 (required=true) |
| 4-1 | `/getSet` | `goodsCd=G003&setCd=S001` | 세트 구성상품 List |
| 4-2 | `/getSet` | `goodsCd` 없음 | 400 (required=true) |
| 5-1 | `/getAllRecipe` | `goodsCd=G001` | G001을 원부재료로 사용하는 레시피 상품 List |
| 5-2 | `/getAllRecipe` | `goodsCd` 없음 | 400 (required=true) |

---

## 6. `/delete` — 상품 삭제

**2단계 체크 (주의: if-else 아니고 if-if)**:
```
chkImcriotb(수불이력) > 0 → chkFg = "imcro1"
chkSgoodmtb(매출이력) > 0 → chkFg = "sgood1"  ← 덮어쓰기
chkFg == ""             → deleteGoods()
```

**deleteGoods 내부**:
```
getSaveSetCd() != null && != "" → delTbSetGoods()
deleteGoods()
deleteTprice()
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 6-1 | chainNo=`C001` | 수불이력/매출이력 없음 | `goodsCd=G001` | `""` + delTbSetGoods + deleteGoods + deleteTprice |
| 6-2 | chainNo=`C001` | **수불이력 있음** | `goodsCd=G001` | `"imcro1"` (삭제 없음) |
| 6-3 | chainNo=`C001` | **매출이력 있음** | `goodsCd=G001` | `"sgood1"` (삭제 없음) |
| 6-4 | chainNo=`C001` | 수불이력 있음, 매출이력 있음 | `goodsCd=G001` | `"sgood1"` (**매출이력이 수불이력 덮어쓰기** ★) |
| 6-5 | - | - | `goodsCd=` (빈값) | 400 (@NotBlank) |

---

## 10. `/setUnitSearch` — 세트 구성상품 검색

**특이사항**: `hid_alry_recpUnit` 콤마 split → List 변환

```java
String[] arr = String.valueOf(map.get("hid_alry_recpUnit")).split(",");
for(int i=0; i < arr.length; i++) list.add(arr[i]);
commandMap.put("list", list);
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 10-1 | chainNo=`C001` | - | `{"hid_alry_recpUnit":"G001,G002","offset":0,"limit":10}` | G001, G002 제외한 상품 List |
| 10-2 | - | - | `{"hid_alry_recpUnit":"","offset":0,"limit":10}` | `""`.split(",") → `[""]` List → 필터 없음 |
| 10-3 | - | - | `{}` (offset 없음) | ClassCastException (**NPE**) |
| 10-4 | 콘솔 출력 확인 | setUnitSearch 호출 후 서버 콘솔 확인 | commandMap 전체 내용 stdout 출력 ★ (제거 대상) |

---

## 11. `/update` — 상품 수정

**서비스 로직 (updateGoods) 핵심 분기**:
```
goods_use_fg = "0"
  └── goodsCdDupChk = "0" (상품코드 미존재)
        └── source 있음 → barCdDupChk=null → instTMSSRCTB (바코드 신규)
                       → barCdDupChk 있음 → "BcdDup"
      goodsCdDupChk ≠ "0" (상품코드 존재)
        └── source 있음 → barCdDupChk=null → updTMSSRCTB (바코드 update)
                       → barCdDupChk(bcd=같고 gds≠현재) → "BcdDup"
                       → barCdDupChk(bcd=다름) → 정상
            source 없음 → delTMSSRCTB (바코드 delete)

set_fg = "3", setUnit_list 있음
  └── hid_set_cd = "" → getSetCd() 채번 → instTbSetGoods (신규 세트)
      hid_set_cd 있음 → delTbSetGoods → instTbSetGoods (세트 재구성)

vendorCd 변경 (hid_vendorCd ≠ vendorCd)
  → deleteVendorGoods (기존 협력사 거래처 상품 삭제)

vendorCd 있음 → instVendorGoods

storeStockYn = "N"
  → getPriceInfo → CNT=0: instTpricetbUcost / CNT>0: updateGoodsUcost

→ updTgoodstb (상품 UPDATE)
```

| No | 세션 조건 | DB 선행상태 | 핵심 조건 | 예상값 |
|----|----------|------------|----------|-------|
| 11-1 | chainNo=`C001`, ID=`7249525SHOP` | G001 존재 (일반) | set_fg=`1`, source=``, vendorCd=`` | updTgoodstb 실행, `""` |
| 11-2 | chainNo=`C001` | G001, barcode 없음 | source=`8801234567890` (신규) | instTMSSRCTB + updTgoodstb |
| 11-3 | chainNo=`C001` | G001, 다른 상품에 barcode 등록됨 | source=`8801234567890` | `"BcdDup"` |
| 11-4 | chainNo=`C001` | G001, 세트상품 | set_fg=`3`, setUnitGoodsCdArr=`G002,G003`, hid_set_cd=`` | getSetCd → instTbSetGoods |
| 11-5 | chainNo=`C001` | G001, 기존 세트 재구성 | set_fg=`3`, hid_set_cd=`S001` | delTbSetGoods → instTbSetGoods |
| 11-6 | chainNo=`C001` | G001, vendorCd 변경 | hid_vendorCd=`V001`, vendorCd=`V002` | deleteVendorGoods(V001) + instVendorGoods(V002) |
| 11-7 | chainNo=`C001` | G001, storeStockYn=`N` | storeStockYn=`N`, 원가정보 없음 | instTpricetbUcost |
| 11-8 | - | - | required lclsCd 없음 | 400 (@NotBlank) |

---

## 12. `/insert` — 상품 등록

**서비스 로직 (insertGoods) 핵심 흐름**:
```
1. getGoodscdLen() = "" → "MsErr" (매장 환경설정 없음)
2. getGoodsCd() → goods_cd 채번
3. 브랜드샵(shopBrandCd="1") AND source="" → getSourceCd() 자동 채번
   (880 + T를 제거한 상품코드 7자리 + 숫자 3자리)
4. 바코드 중복 체크 (updateGoods와 동일 로직)
5. setRegiYn="Y" AND set_fg="3" → getSetCd() → instTbSetGoods
6. vendorCd 있음 → instVendorGoods
7. instTGOODSTB → instTPRICETB_0 → instTPRICETB_1
8. storeStockYn="N" → instTpricetbUcost
→ "insert"
```

| No | 세션 조건 | DB 선행상태 | 핵심 조건 | 예상값 |
|----|----------|------------|----------|-------|
| 12-1 | chainNo=`C001`, ID=`7249525SHOP` | 환경설정 **없음** | (any) | `"MsErr"` |
| 12-2 | chainNo=`C001` | 환경설정 정상 | 일반상품, source=`` | `"insert"` + instTGOODSTB + 2×instTPRICETB |
| 12-3 | chainNo=`C001` | 브랜드샵, source=`` | shopBrandCd=`"1"`, source=`` | 바코드 자동채번 `880+goodsCd[1:8]+숫자3` |
| 12-4 | chainNo=`C001` | 바코드 이미 타 상품에 등록 | source=`8801234567890` | `"BcdDup"` |
| 12-5 | chainNo=`C001` | - | set_fg=`3`, setUnitGoodsCdArr=`G002,G003` | getSetCd → instTbSetGoods → "insert" |
| 12-6 | chainNo=`C001` | - | vendorCd=`V001` | instVendorGoods (topVendor 조회 후) |
| 12-7 | chainNo=`C001` | - | storeStockYn=`N` | instTpricetbUcost |
| 12-8 | chainNo=`C001` | - | storeStockYn=`Y` | instTpricetbUcost **미실행** |
| 12-9 | - | - | lclass_cd 없음 (required=true) | 400 |
| 12-10 | goods_price_fg 미전송 | body에 modalselGoodsPriceFg 없음 | `goods_price_fg=null` → 서비스 조건문 처리 방식 확인 ★ |

---

## 서비스 핵심 분기 요약

```
selectGoodsList
└── getDeliveryType() → deliveryList로 goodsList 각 건의 deliveryTypeNm 맵핑

modalSearch
└── setFg="2" → getRecipe() / "3" → getSetList() / 그 외 → 빈 리스트

delete
└── imcCnt > 0 → chkFg="imcro1"
    sgdCnt > 0 → chkFg="sgood1" (if-if 순서로 덮어쓰기 주의)
    chkFg="" → deleteGoods(setGoods+goods+tprice)

updateGoods
└── goods_use_fg="0" → 바코드 4분기
    set_fg="3" + setUnit_list not empty → 세트코드 처리
    vendorCd 변경 → deleteVendorGoods + instVendorGoods
    storeStockYn="N" → 원가 CNT분기(insert/update)
    → updTgoodstb

insertGoods
└── getGoodscdLen="" → "MsErr"
    브랜드샵 + source="" → 자동 바코드 채번
    → 바코드 4분기
    → setRegiYn="Y" + set_fg="3" → 세트
    → vendorCd → instVendorGoods
    → instTGOODSTB + 2×instTPRICETB + (storeStockYn="N" → ucost)
```

---

## PowerShell 테스트 명령 (주요 케이스)

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00006"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 상품 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'

# 2. 상품 상세 조회 (일반상품)
Invoke-RestMethod -Uri "$base/modalSearch" -Method POST -ContentType $f `
  -Body "goodsCd=G001" -WebSession $session

# 6-1. 상품 삭제 (이력 없는 경우)
Invoke-RestMethod -Uri "$base/delete" -Method POST -ContentType $f `
  -Body "goodsCd=G001" -WebSession $session
# 예상: ""

# 6-4. 수불+매출 동시 → sgood1 (매출이 덮어씀)
Invoke-RestMethod -Uri "$base/delete" -Method POST -ContentType $f `
  -Body "goodsCd=G999" -WebSession $session
# 예상: "sgood1"

# 12-1. 환경설정 없는 매장에서 상품등록 → MsErr
Invoke-RestMethod -Uri "$base/insert" -Method POST -ContentType $f `
  -Body "com_goodsClass_m01_l_select=L01&com_goodsClass_m01_m_select=M01&com_goodsClass_m01_s_select=S01&modalselSetFg=1&modalselUseFg=1" -WebSession $session
# 예상: "MsErr"

# 12-2. 정상 등록
Invoke-RestMethod -Uri "$base/insert" -Method POST -ContentType $f `
  -Body "com_goodsClass_m01_l_select=L01&com_goodsClass_m01_m_select=M01&com_goodsClass_m01_s_select=S01&modalselSetFg=1&modalselUseFg=1&modalinputGoodsNm=테스트상품&modalinputUprice=5000" -WebSession $session
# 예상: "insert"
```

---

## 주요 검증 포인트

```
□ delete — if-if 구조: imcro1 이후 sgood1이 덮어씀 (if-else 아님) ★
□ modalSearch — goodsCd="" 빈값 시 getModalList()=null → NPE 위험
□ setUnitSearch — hid_alry_recpUnit="" → split(",") → [""] → IN 조건 확인
□ updateGoods — goods_use_fg="0" 일 때만 바코드 로직 실행 (="1"이면 바코드 처리 없이 updTgoodstb)
□ updateGoods — hid_set_cd 있으면 del→inst, 없으면 새 세트코드 채번
□ insertGoods — getGoodscdLen=""(MsErr) / 브랜드샵 바코드 자동채번 / storeStockYn 분기
□ search — offset/limit 없으면 ClassCastException (int 캐스팅)
□ @Transactional — insertGoods 중 실패 시 instTGOODSTB 포함 전체 롤백
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] TGOODSTB (CUD 작업)
│   └── (Trigger) Tr_TGOODS_T01
├── [테이블] TMSSRCTB (CUD 작업)
│   └── (Trigger) Tr_TMSSRC_T01
├── [테이블] TPRICETB (CUD 작업)
│   └── (Trigger) Tr_TPRICE_T01
└── [테이블] TVNDRGTB (CUD 작업)
    └── (Trigger) Tr_TVNDRG_T01
```
