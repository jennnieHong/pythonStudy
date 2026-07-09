# Hq_Vendor_00009 — 무발주 입고/취소 단위 테스트케이스

> **화면**: [HQ] 거래처 > 무발주 입고/취소  
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00009`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 조회 4개 = `@RequestBody` 또는 파라미터 없음 / CUD 5개 = `@RequestParam` 배열
> **DB 트리거 영향도**: OBSLPDTB, OBSLPHTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | 전 엔드포인트 |
| `msNo` | `MS001` | getVatFg |
| `ID` | `7249525SHOP` | insertOrder, confirmOrdPurch |

---

## 엔드포인트 목록 (9개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getVatFg` | 부가세 포함 여부 조회 | (파라미터 없음) | `String` | SELECT | MMEMBVTB  |
| 2 | `/search` | 무발주 입고 헤더 목록 조회 | `@RequestBody` | `List` | SELECT | MMEMBSTB<br>OBSLPDTB<br>OBSLPHTB<br>TVNDRMTB  |
| 3 | `/detailSearch` | 무발주 입고 상세 조회 | `@RequestBody` | `List` | SELECT | IMCRIOTB<br>MNAMEMTB<br>OBSLPDTB<br>OBSLPHTB<br>TGOODSTB<br>TMSCLSTB  |
| 4 | `/selectVendorGoodsList` | 상품 조회 (affiliateCompany 분기, 페이징) | `@RequestBody` | `Map` (total+rows) | SELECT | IMCRIOTB<br>MMEMBSTB<br>MNAMEMTB<br>OBSLPDTB<br>TCHAINTB<br>TGOODSTB<br>TPRICETB<br>TVNDRGTB  |
| 5 | `/insertOrder` | 무발주 입고 등록 (신규/추가 분기) | `@RequestParam` 다중 배열 | `String` | INSERT | OBSLPDTB<br>OBSLPHTB  |
| 6 | `/updateGoodsList` | 무발주 입고 상품 수정 (수량 0→삭제 분기) | `@RequestParam` 배열 | `String` | UPDATE | OBSLPDTB<br>OBSLPHTB  |
| 7 | `/confirmOrdPurch` | 무발주 입고 확정 | `@RequestParam` | `String` | UPDATE | OBSLPDTB<br>OBSLPHTB  |
| 8 | `/cancelSlip` | 무발주 입고 취소 (화면 미제공 & 트리거 차단) | `@RequestParam` 배열 | `String` | UPDATE (차단) | OBSLPDTB<br>OBSLPHTB  |
| 9 | `/deleteSlip` | 전표 삭제 (HD→DT 삭제) | `@RequestParam` 배열 | `String` | DELETE | OBSLPDTB<br>OBSLPHTB  |

---

## 1. `/getVatFg` — 부가세 포함 여부 조회

**특이사항**: `@RequestBody` 없음, 세션에서 `chainNo`+`msNo` 자동 주입

| No | 세션 조건 | 예상값 |
|----|----------|-------|
| 1-1 | chainNo=`C001`, msNo=`MS001` | `"Y"` 또는 `"N"` |
| 1-2 | 세션 없음 (미로그인) | 401 / securityUserInformation NPE |

---

## 2. `/search` — 무발주 입고 헤더 목록 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"searchFromDate":"20260501","searchToDate":"20260531"}` | 기간 내 헤더 목록 |
| 2-2 | chainNo=`C001` | `{"searchFromDate":"20260501","searchToDate":"20260531","vendor":"VND001","msNo":"MS001"}` | 거래처+매장 필터 |
| 2-3 | chainNo=`C001` | `{}` | 조건 없이 전체 (또는 빈 결과) |

---

## 3. `/detailSearch` — 무발주 입고 상세 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"slipNo":"SLP001","orderDate":"20260522","msNo":"MS001"}` | 해당 전표 상세 목록 |
| 3-2 | chainNo=`C001` | `{}` | 조건 없음 → 전체 또는 빈 결과 |

---

## 4. `/selectVendorGoodsList` — 상품 조회

**affiliateCompany 분기 로직**:
```
affiliateCompany = getAffiliateCompany(chainNo)
  "1" (F&B) → getPrePurchWhMsNoYn() 추가 조회 → prePurchWhMsNoYn 세팅
  else       → 브랜드샵 → prePurchWhMsNoYn 미세팅

★ goodsCdArr — containsKey 방어: 없으면 new ArrayList() 세팅
★ offset 미전달 시: (int)map.get("offset") → NPE/ClassCastException ★★★
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`(F&B, affiliateCompany=`"1"`) | `{"msNo":"MS001","orderDate":"20260522","vendor":"VND001","offset":0,"limit":10}` | prePurchWhMsNoYn 세팅 후 조회 |
| 4-2 | chainNo=`C002`(브랜드샵, affiliateCompany≠`"1"`) | 동일 | prePurchWhMsNoYn 미세팅 조회 |
| 4-3 | chainNo=`C001` | `{"msNo":"MS001","vendor":"VND001","offset":0,"limit":10,"goodsCdArr":["G001","G002"]}` | 상품코드 배열 필터 |
| 4-4 | chainNo=`C001` | `{}` (offset 없음) | `(int)map.get("offset")` → **NPE** ★★★ |
| 4-5 | chainNo=`C001` | 유효 파라미터 | `{"total":N,"rows":[...]}` |

---

## 5. `/insertOrder` — 무발주 입고 등록

**서비스 핵심 분기 (flag 기준)**:
```
flag == "add" → chkFg = "add"  (기존 전표에 상품 추가)
flag != "add" → selectSlipNo() → insertOrdPurchSlip() → chkFg = "insert"

공통:
  maxLine = selectMaxLineNo()
  loop i in goodsCd:
    maxLineNo_str = setZeroValue(maxLineNo, 4)
    ficVatAmt[i]  ← ficVatAmt 배열 (required=false, defaultValue="")
                  → 1건이면 ficVatAmt=[""]
                  → 2건 이상이면 ficVatAmt[1] → ArrayIndexOutOfBounds ★
  insertOrdPurchGoods(addList)
  updateOrdPurchHd(map)

setZeroValue(value=0, 4) → "0" (0이면 패딩 없이 "0" 반환)
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 5-1 | ID=`7249525SHOP` | - | `orderDate=20260522&purchDate=20260522&vendor=VND001&vatFg=Y&msNo=MS001&goodsCd[]=G001&ordPurchQty[]=10&usuprice[]=500&orderVat[]=50&orderAmt[]=5500&inQty[]=10&orderEaQty[]=10&ficVat[]=Y&ficVatAmt[]=500` | **신규 전표** (flag 미전달="") → insert |
| 5-2 | ID=`7249525SHOP` | 기존 전표 `SLP001` | 동일 + `flag=add&slipNo=SLP001` | **추가** → chkFg="add" |
| 5-3 | ID=`7249525SHOP` | - | 2개 상품 + `ficVatAmt[]` 미전달 | `ficVatAmt=[""]` → `ficVatAmt[1]` → **ArrayIndexOutOfBoundsException** ★★★ |
| 5-4 | - | - | `orderDate` 없음 | 400 (@NotBlank) |
| 5-5 | ID=`7249525SHOP` | maxLine=0 | goodsCd[]=G001 | `setZeroValue(0,4)` → `"0"` (패딩 없음, "0001"이 아님) ★ |

---

## 6. `/updateGoodsList` — 무발주 입고 상품 수정

**수량 분기 로직**:
```
orderDate = orderDate.replaceAll("-", "")
purchDate = purchDate.replaceAll("-", "")

for i in goodsCd:
  Float.parseFloat(orderQty[i]) > 0 → list (update 대상)
  else                              → deleteList + cnt++

cnt == goodsCd.length → deleteGoodsDtList + deleteGoodsHdList (전체 삭제)
else → updateGoodsList(list) + deleteGoodsDtList(deleteList if size>0)
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 6-1 | - | `orderDate=2026-05-22&purchDate=2026-05-22&msNo=MS001&slipNo=SLP001&goodsCd[]=G001&lineNo[]=0001&orderQty[]=5&ordPurchUcost[]=500&orderAmt[]=2500&orderVat[]=250&inQty[]=5&orderInQty[]=5` | orderDate 하이픈 제거 → update |
| 6-2 | - | 동일, `orderQty[]=0` | deleteList → cnt==length → deleteGoodsDtList + deleteGoodsHdList |
| 6-3 | - | 2상품: G001(qty=5), G002(qty=0) | list에 G001, deleteList에 G002 → updateGoodsList + deleteGoodsDtList |
| 6-4 | - | `orderQty[]=abc` | `Float.parseFloat("abc")` → **NumberFormatException** ★★ |
| 6-5 | - | `slipNo` 없음 | 400 (@NotBlank) |

---

## 7. `/confirmOrdPurch` — 무발주 입고 확정

```
chain_hq_yn = "Y" (하드코딩)
updateConfirmHd → updateConfirmDt → chkFg = "confirm"
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 7-1 | ID=`7249525SHOP` | `orderDate=20260522&msNo=MS001&slipNo=SLP001&purchDate=20260522` | chkFg=`"confirm"` |
| 7-2 | - | `slipNo` 없음 | 400 (@NotBlank) |
| 7-3 | ID=`7249525SHOP` | 이미 확정된 전표 | updateConfirmHd 0건 (SQL WHERE 조건에 따라) |

---

## 8. `/cancelSlip` — 무발주 입고 취소 (화면 미제공 & 트리거 차단)

**정책**: 화면상 "입고취소" 버튼이 주석 처리되어 접근 불가하며, 자바 가상 트리거 `Tr_OBSLPD_T02_Service` 내 Validation 1(`new.PROC_FG = '5'` 일 때 에러)이 활성화되어 백엔드에서도 변경을 차단합니다.

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 8-1 | `orderDate[]=20260522&slipNo[]=SLP001&purchDate[]=20260522&msNo[]=MS001` | **500 (OBSLPD_T02 : PROC_FG ERROR!!)** ★ |
| 8-2 | 2건 선택 | **500 (트리거 차단)** |
| 8-3 | `orderDate[]` 없음 | 빈 배열 → 루프 0번 → `"cancel"` 반환 (오류 없음) |
| 8-4 | `orderDate[]=20260522&slipNo[]=SLP001` (purchDate, msNo 미전달) | **500 (트리거 차단)** |

---

## 9. `/deleteSlip` — 전표 삭제

**서비스**: `for each map → deleteGoodsHd(HD 삭제) → deleteGoodsDt(DT 삭제)` (건별 HD→DT 순)

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 9-1 | `orderDate[]=20260522&slipNo[]=SLP001&msNo[]=MS001` | 1건 HD+DT 삭제, `"delete"` |
| 9-2 | 2건 선택 | 2건 각각 HD→DT 삭제 |
| 9-3 | 빈 배열 | 루프 0번 → `"delete"` 반환 |

---

## `setZeroValue` 특이사항

```java
setZeroValue(value=0, num=4):
  if(value == 0) return "0"   ← "0001"이 아닌 "0" 반환 ★★
  // lineNo="0"이 DB에 저장됨 → 발주 상품 lineNo 중복 가능성 확인 필요
```

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/vendor/hq_vendor_00009"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. VAT 여부 조회
Invoke-RestMethod -Uri "$base/getVatFg" -Method POST -ContentType $f -WebSession $session

# 2. 무발주 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchToDate":"20260531"}'

# 4-1. 상품 조회 (F&B, offset/limit 필수)
Invoke-RestMethod -Uri "$base/selectVendorGoodsList" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001","vendor":"VND001","orderDate":"20260522","offset":0,"limit":10}'

# 5-1. 무발주 입고 신규 등록
Invoke-RestMethod -Uri "$base/insertOrder" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate=20260522&purchDate=20260522&vendor=VND001&vatFg=Y&msNo=MS001&goodsCd[]=G001&ordPurchQty[]=10&usuprice[]=500&orderVat[]=50&orderAmt[]=5500&inQty[]=10&orderEaQty[]=10&ficVat[]=Y&ficVatAmt[]=500"
# 예상: "insert"

# 6-1. 상품 수정
Invoke-RestMethod -Uri "$base/updateGoodsList" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate=2026-05-22&purchDate=2026-05-22&msNo=MS001&slipNo=SLP001&goodsCd[]=G001&lineNo[]=0001&orderQty[]=5&ordPurchUcost[]=500&orderAmt[]=2500&orderVat[]=250&inQty[]=5&orderInQty[]=5"

# 7-1. 입고 확정
Invoke-RestMethod -Uri "$base/confirmOrdPurch" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate=20260522&msNo=MS001&slipNo=SLP001&purchDate=20260522"
# 예상: "confirm"

# 8-1. 취소 (가상 트리거 작동으로 500 에러 발생 기대)
Invoke-RestMethod -Uri "$base/cancelSlip" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate[]=20260522&slipNo[]=SLP001&purchDate[]=20260522&msNo[]=MS001"
# 예상: 500 Internal Server Error (OBSLPD_T02 : PROC_FG ERROR!!)

# 9-1. 삭제
Invoke-RestMethod -Uri "$base/deleteSlip" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate[]=20260522&slipNo[]=SLP001&msNo[]=MS001"
# 예상: "delete"
```

---

## 주요 검증 포인트

```
□ selectVendorGoodsList — offset 미전달 → (int)map.get("offset") NPE ★★★
□ insertOrder — ficVatAmt[] 2건 이상 미전달 → ficVatAmt=[""] → ficVatAmt[1] ArrayIndexOutOfBounds ★★★
□ setZeroValue(0, 4) → "0" 반환 (기대값 "0001" 아님) → lineNo 중복 가능성 ★★
□ updateGoodsList — orderQty "abc" → Float.parseFloat → NumberFormatException ★★
□ updateGoodsList — orderDate/purchDate 하이픈 포함 → replaceAll("-","") 처리 정상 확인
□ insertOrder — flag="add" → slipNo 필수 (slipNo="" defaultValue → 기존 전표 추가 실패)
□ cancelSlip — 가상 트리거 `Tr_OBSLPD_T02_Service` 활성화로 인한 `PROC_FG = '5'` 변경 에러 차단 ★★★
□ cancelSlip — 2루프 (DT 전체 → HD 전체): 가상 트리거 활성화로 인해 원천 차단되며, 트랜잭션 예외 시 자동 롤백
□ deleteSlip — 건별 HD→DT 순: HD 삭제 후 DT 삭제 실패 시 HD만 삭제된 고아 DT 잔류 ★
□ affiliateCompany — "1" (F&B)이면 getPrePurchWhMsNoYn() 추가 호출 — affiliateCompany null 가능성 확인
□ @Transactional rollbackFor Exception — saveVendorOrder/cancelSlip(트리거 오류 시)/deleteSlip 전체 rollback 보장
```

---

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
무발주 입고 API 호출 (St_Vendor_00006 / Hq_Vendor_00009)
├── [직접 CUD 테이블]
│   ├── OBSLPHTB (무발주입고 헤더)
│   └── OBSLPDTB (무발주입고 상세)
├── [자바 가상 트리거]
│   ├── Tr_OBSLPD_T01_Service (수불 이력 생성)
│   ├── Tr_OBSLPD_T02_Service (PROC_FG 검증 - '5' 차단)
│   └── Tr_OBSLPH_T01_Service (매입로그 및 이력 관리)
├── [트리거 연쇄 CUD 테이블]
│   ├── IMTRLGTB (수불로그 - Sp_SUB_IMTRLG_I_Service 수불 서비스 호출을 통해 적재)
│   └── OBSLPLOG (매입로그 - 확정 시 매입이력 적재)
├── [배치 업데이트 연동 테이블]
│   └── IMCRIOTB (현재고 - 배치 DmIMTR01Service 실행 시 IMTRLGTB 로그 기반으로 주기적 갱신)
└── [단순 참조(SELECT) 테이블]
    ├── TGOODSTB (상품 마스터)
    ├── TVNDRMTB (거래처 마스터)
    ├── MMEMBSTB (매장 마스터)
    ├── TCHAINTB (체인 마스터)
    ├── TPRICETB / MPRICETB (단가 마스터)
    └── MNAMEMTB (명칭코드 마스터)
```
```
