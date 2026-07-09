# St_Vendor_00006 — 매장 무발주 입고/취소 단위 테스트케이스

> **화면**: [ST] 거래처관리 > 무발주 입고/취소  
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00006`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 조회 = `@RequestBody` / CUD = `@RequestParam` 배열
> **DB 트리거 영향도**: OBSLPDTB, OBSLPHTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## `setZeroValue(value, num)` 버그 — 서비스에도 동일

```java
if(value == 0) return "0";   // 0 → "0" (기대값 "0000") ★★
// ★ value=0 → lineNo = "0" → DB 저장 시 "0000" 이어야 하는 PK 오류 가능
```

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | getVatFg, search, selectVendorGoodsList, insertOrder, confirmOrdPurch, cancelSlip |
| `chainHqYn` | `Y` | updateGoodsList, confirmOrdPurch, cancelSlip |
| `msNo` | `MS001` | getVatFg, search, selectVendorGoodsList, insertOrder, updateGoodsList, confirmOrdPurch |
| `ID` | `I000449s` | insertOrder, confirmOrdPurch |

---

## 엔드포인트 목록 (8개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getVatFg` | 부가세 포함 여부 조회 | (파라미터 없음) | `String` | SELECT | MMEMBVTB  |
| 2 | `/search` | 무발주입고 헤더 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPDTB<br>OBSLPHTB<br>TVNDRMTB  |
| 3 | `/detailSearch` | 무발주입고 디테일 조회 | `@RequestBody` | `List` | SELECT | IMCRIOTB<br>MNAMEMTB<br>OBSLPDTB<br>OBSLPHTB<br>TGOODSTB<br>TMSCLSTB  |
| 4 | `/selectVendorGoodsList` | 상품 조회 (페이징, affiliateCompany 분기) | `@RequestBody` | `Map` (total+rows) | SELECT | IMCRIOTB<br>MMEMBSTB<br>MNAMEMTB<br>OBSLPDTB<br>TCHAINTB<br>TGOODSTB<br>TPRICETB<br>TVNDRGTB  |
| 5 | `/insertOrder` | 무발주입고 등록 (배열 루프, slipNo 채번) | `@RequestParam` 배열 | `String` | INSERT | OBSLPDTB<br>OBSLPHTB  |
| 6 | `/updateGoodsList` | 무발주입고 수정 (qty=0이면 삭제 분기) | `@RequestParam` 배열 | `String` | UPDATE | OBSLPDTB<br>OBSLPHTB  |
| 7 | `/confirmOrdPurch` | 무발주입고 확정 | `@RequestParam` | `String` | UPDATE | OBSLPDTB<br>OBSLPHTB  |
| 8 | `/cancelSlip` | 무발주입고 취소 (배열, Dt→Hd 순) | `@RequestParam` 배열 | `String` | UPDATE | OBSLPDTB<br>OBSLPHTB  |
| 9 | `/deleteSlip` | 전표 삭제 (배열, Hd→Dt 순) | `@RequestParam` 배열 | `String` | DELETE | OBSLPDTB<br>OBSLPHTB  |

---

## 1. `/getVatFg` — 부가세 여부 조회

| No | 세션 조건 | 예상값 |
|----|----------|-------|
| 1-1 | chainNo=`C001`, msNo=`MS001` | `"1"` 또는 `"0"` |

---

## 2. `/search` — 헤더 목록 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001`, msNo=`MS001` | `{"searchFromDate":"20260501","searchToDate":"20260526"}` | 무발주입고 전표 목록 |
| 2-2 | (동일) | `{}` | searchFromDate/searchToDate null → 전체 조회 가능 ★ |
| 2-3 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 3. `/detailSearch` — 디테일 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"slipNo":"SL001","orderDate":"20260526"}` | 해당 전표 상품 목록 |
| 3-2 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 4. `/selectVendorGoodsList` — 상품 조회

**★ offset 미전달**: `(int)map.get("offset")` → **NPE/ClassCastException** ★★★  
**affiliateCompany="1"** → `getPrePurchWhMsNoYn()` 추가 호출

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`, msNo=`MS001` | `{"offset":0,"limit":10,"orderDate":"20260526"}` | 상품 목록 + total |
| 4-2 | (동일) | `{}` (offset 없음) | `(int)map.get("offset")` → **NPE** ★★★ |
| 4-3 | chainNo=`C001`(affiliateCompany=`1`) | `{"offset":0,"limit":10}` | prePurchWhMsNo 추가 조회 후 목록 |

---

## 5. `/insertOrder` — 무발주입고 등록

**서비스 처리**:
```
flag="add" → slipNo는 기존 것 사용, chkFg="add"
flag 그 외 → selectSlipNo() 채번 → insertOrdPurchSlip() → chkFg="insert"
→ setZeroValue(maxLineNo, 4) → maxLineNo=0 → "0" (기대값 "0000") ★★
→ insertOrdPurchGoods(addList) → updateOrdPurchHd(map) → 3단계
```

**배열 길이 불일치**: `goodsCd.length`로 루프 시 다른 배열 짧으면 **ArrayIndexOutOfBoundsException** ★★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 5-1 | msNo=`MS001`, ID=`I000449s` | `orderDate=20260526&purchDate=20260526&vendor=V001&vatFg=1&goodsCd[]=G001&ordPurchQty[]=10&usuprice[]=500&orderVat[]=50&orderAmt[]=5000&inQty[]=10&orderEaQty[]=10&ficVat[]=Y&ficVatAmt[]=50` | `"insert"` |
| 5-2 | (동일) | flag=`add` + slipNo=`SL001` | `"add"` (기존 전표에 추가) |
| 5-3 | (동일) | goodsCd[] 2개, ordPurchQty[] 1개 | **ArrayIndexOutOfBoundsException** ★★★ |
| 5-4 | (동일) | maxLineNo=0 (초기) | setZeroValue→"0" → lineNo="0" ★★ |
| 5-5 | - | `orderDate` 없음 | 400 (@NotBlank) |
| 5-6 | - | `goodsCd[]` 없음 | 400 (required=true) |

---

## 6. `/updateGoodsList` — 무발주입고 수정

**분기 로직**:
```java
float.parseFloat(orderQty[i]) > 0 → list (update 대상)
else → deleteList + cnt++

cnt == goodsCd.length → deleteGoodsDtList + deleteGoodsHdList (전체 삭제)
else → updateGoodsList + deleteGoodsDtList(일부 삭제)
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 6-1 | chainHqYn=`Y`, msNo=`MS001` | `orderDate=20260526&slipNo=SL001&purchDate=20260526&lineNo[]=0001&orderQty[]=5&goodsCd[]=G001&ordPurchUcost[]=500&orderAmt[]=2500&orderVat[]=250&inQty[]=5&orderInQty[]=5` | `"update"` |
| 6-2 | (동일) | `orderQty[]=0` (전체 0) | deleteGoodsDtList + deleteGoodsHdList → `""` |
| 6-3 | (동일) | orderQty 혼합 (일부 0) | update+delete 혼합 |
| 6-4 | (동일) | `Float.parseFloat("abc")` → **NumberFormatException** ★★ |
| 6-5 | - | `orderDate` 없음 | 400 (@NotBlank) |

---

## 7. `/confirmOrdPurch` — 무발주입고 확정

**서비스**: `updateConfirmHd()` → `updateConfirmDt()` → `"confirm"` 반환

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 7-1 | chainHqYn=`Y`, msNo=`MS001`, ID=`I000449s` | `orderDate=20260526&slipNo=SL001&purchDate=20260526` | `"confirm"` |
| 7-2 | (동일) | 이미 확정된 slipNo | Mapper WHERE 조건에 따라 0건 update 또는 중복 오류 |
| 7-3 | - | `orderDate` 없음 | 400 (@NotBlank) |

---

## 8. `/cancelSlip` — 무발주입고 취소

**서비스**: for루프1(cancelSlipDt) → for루프2(cancelSlipHd) — Dt 먼저 취소 후 Hd 취소

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 8-1 | chainHqYn=`Y` | `orderDate[]=20260526&slipNo[]=SL001&purchDate[]=20260526&msNo[]=MS001` | `"cancel"` |
| 8-2 | (동일) | 다중: `orderDate[]` 2개 + 나머지 1개 | `slipNo[1]` → **ArrayIndexOutOfBoundsException** ★★★ |
| 8-3 | - | `orderDate[]` 없음 | 400 (required=true) |

---

## 9. `/deleteSlip` — 전표 삭제

**서비스**: for-each → `deleteGoodsHd(map)` → `deleteGoodsDt(map)` 순 (Hd 먼저 삭제)

| No | Request | 예상값 |
|----|---------|-------|
| 9-1 | `orderDate[]=20260526&slipNo[]=SL001&msNo[]=MS001` | `"delete"` |
| 9-2 | 다중 배열 길이 불일치 | **ArrayIndexOutOfBoundsException** ★★★ |
| 9-3 | `orderDate[]` 없음 | 400 (required=true) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/vendor/st_vendor_00006"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 부가세 여부 조회
Invoke-RestMethod -Uri "$base/getVatFg" -Method POST -ContentType $f -WebSession $session -Body ""

# 2-1. 무발주입고 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchToDate":"20260526"}'

# 4-2. offset 없음 → NPE
Invoke-RestMethod -Uri "$base/selectVendorGoodsList" -Method POST -Headers $h -WebSession $session `
  -Body '{"orderDate":"20260526"}'
# 예상: 500 NPE

# 5-1. 무발주입고 등록
Invoke-RestMethod -Uri "$base/insertOrder" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate=20260526&purchDate=20260526&vendor=V001&vatFg=1&goodsCd[]=G001&ordPurchQty[]=10&usuprice[]=500&orderVat[]=50&orderAmt[]=5000&inQty[]=10&orderEaQty[]=10&ficVat[]=Y&ficVatAmt[]=50"

# 6-4. orderQty 숫자 아님 → NumberFormatException
Invoke-RestMethod -Uri "$base/updateGoodsList" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate=20260526&slipNo=SL001&purchDate=20260526&lineNo[]=0001&orderQty[]=abc&goodsCd[]=G001&ordPurchUcost[]=500&orderAmt[]=2500&orderVat[]=250&inQty[]=5&orderInQty[]=5"
# 예상: 500

# 7-1. 확정
Invoke-RestMethod -Uri "$base/confirmOrdPurch" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate=20260526&slipNo=SL001&purchDate=20260526"

# 8-1. 취소
Invoke-RestMethod -Uri "$base/cancelSlip" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate[]=20260526&slipNo[]=SL001&purchDate[]=20260526&msNo[]=MS001"
```

---

## 주요 검증 포인트

```
□ selectVendorGoodsList — offset 미전달 → (int)map.get("offset") → NPE ★★★
□ setZeroValue(0, 4) → "0" → lineNo="0" (기대값 "0000") → PK 오류 가능 ★★
□ insertOrder — 배열 길이 불일치 → ArrayIndexOutOfBoundsException ★★★
□ insertOrder — ficVatAmt required=false, defaultValue="" → 배열 기본값 처리 주의
□ updateGoodsList — Float.parseFloat(orderQty) 숫자 아님 → NumberFormatException ★★
□ cancelSlip/deleteSlip — 배열 길이 불일치 → ArrayIndexOutOfBoundsException ★★★
□ updateGoodsList — cnt==goodsCd.length 전체 삭제 vs 부분 삭제 분기 로직 확인
□ saveVendorOrder — flag="add": slipNo 미채번, flag 그 외: insertOrdPurchSlip 후 slipNo 채번
□ cancelSlip 서비스 — Dt 취소 루프 완료 후 Hd 취소 (2개 루프 순서 보장) ✓
□ @Transactional rollbackFor Exception — insertOrder(3단계), confirmOrdPurch(2단계) rollback 보장
□ @NotBlank/@Size(max=50) — deliveryRemark 50자 초과 시 400
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅ (7/9 — 조회 2개 확인 필요)

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/search` (헤더 조회) | ✅ SELECT (소스 89번) |
| `/detailSearch` (상세 조회) | ✅ SELECT (소스 117번) |
| `/selectVendorGoodsList` | ❌ **없음** 또는 다른 엔드포인트 — 소스 내 @ServiceLog 7개만 확인 ★ |
| `/insertOrder` | ✅ INSERT (소스 207번) |
| `/updateGoodsList` | ✅ UPDATE (소스 294번) |
| `/confirmOrdPurch` | ✅ UPDATE (소스 379번) |
| `/cancelSlip` | ✅ UPDATE (소스 419번) |
| `/deleteSlip` | ✅ DELETE (소스 460번) |

**`@Validated` 클래스 레벨 적용** ✅ (소스 44번)

**TC 전체 정확** ✅ — ficVatAmt ArrayIndexOutOfBounds, setZeroValue(0,4)="0" 등 소스 확인됨

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] OBSLPDTB (CUD 작업)
│   ├── (Trigger) Tr_OBSLPD_T01
│   └── (Trigger) Tr_OBSLPD_T02
├── [테이블] OBSLPHTB (CUD 작업)
│   └── (Trigger) Tr_OBSLPH_T01
└── [공통 영향 테이블 및 호출]
    ├── MGOODSTB [매장별 상품]
    ├── MMEMLGTB [매장정보변경 HISTORY]
    ├── MMSCLSTB [매장별 상품소분류]
    ├── MMSLOGTB [MASTER LOG]
    ├── MMSPOSTB [매장별 POS MASTER]
    ├── MPRICETB [매장별 단가 관리 MASTER]
    ├── MPRILGTB [매장별 단가 관리 LOG]
    ├── MUSERSTB
    ├── MVNDRGTB [거래선 취급상품 MASTER]
    ├── MVNDRMTB [거래선 MASTER]
    ├── OBSLPLOG
    ├── SSMEMBTB [POS와의 명판(매장) MASTER 응답]
    ├── TB_COST [원가변경관리]
    ├── TPRILGTB [단가 관리 MASTER]
    ├── TSUBMNTB [본부 부가주문 내역 Master]
    ├── [FUNCTION] F_GET_AVG_MONTH_UCOST (TGOODSTB)
    ├── [FUNCTION] F_GET_AVG_UCOST (TGOODSTB)
    ├── [FUNCTION] F_GET_CUR_INFO (IMCRIOTB)
    ├── [FUNCTION] F_GET_MPRICE (MPRICETB)
    ├── [FUNCTION] F_GET_MPRICE_2 (MPRICETB)
    ├── [FUNCTION] F_GET_MPRICE_3 (MPRICETB)
    ├── [FUNCTION] F_GET_NETAMT (MGOODSTB)
    ├── [FUNCTION] F_GET_NETAMT (MMEMBVTB)
    ├── [FUNCTION] F_GET_ORDER_VENDOR (OBSLPDTB)
    ├── [FUNCTION] F_GET_ORDER_VENDOR (OBSLPHTB)
    ├── [FUNCTION] F_GET_SALE_NETAMT (MGOODSTB)
    ├── [FUNCTION] F_GET_SALE_NETAMT (MMEMBVTB)
    ├── [FUNCTION] F_GET_SPC_MPRICE (MPRICETB)
    ├── [FUNCTION] F_GET_SPC_TPRICE (TPRICETB)
    ├── [FUNCTION] F_GET_TPRICE (TPRICETB)
    ├── [FUNCTION] F_GET_TPRICE_2 (TPRICETB)
    ├── [FUNCTION] F_GET_USUPRICE_VAT (MMEMBVTB)
    ├── [FUNCTION] F_GET_USUPRICE_VAT (TGOODSTB)
    ├── [FUNCTION] F_GET_VENDOR (TVNDRGTB)
    ├── [FUNCTION] GET_SMS_CHAIN (MMEMBSTB)
    ├── [FUNCTION] GET_UCOST_F01 (MGOODSTB)
    ├── [FUNCTION] IGET_CUR_F01 (IMCRIOTB)
    ├── [PROCEDURE] CLS_DEL (TMSCLSTB)
    ├── [PROCEDURE] CNTPROC (MMEMBSTB)
    ├── [PROCEDURE] P_INITCOST (MUSERSTB)
    ├── [PROCEDURE] P_MACOST_B (MGOODSTB)
    ├── [PROCEDURE] P_MACOST_B (MUSERSTB)
    ├── [PROCEDURE] P_TACOST_B (MGOODSTB)
    ├── [PROCEDURE] P_TACOST_B (MUSERSTB)
    ├── [PROCEDURE] SUB_CALC_FIX_AMT_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_COUPON_NEW_SHOP_P_TEMP (MMEMBSTB)
    ├── [PROCEDURE] SUB_COUPON_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_CUSTCL_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_CUSTCL_P (TGOODSTB)
    ├── [PROCEDURE] SUB_EMSWRK_P (MUSERSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_RECV_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_RECV_P (TVNDRMTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MGOODSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MVNDRMTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (OBSLPDTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (OBSLPHTB)
    ├── [PROCEDURE] SUB_IMTRLG_I (MMEMBSTB)
    ├── [PROCEDURE] SUB_MASTER_P (MGOODSTB)
    ├── [PROCEDURE] SUB_MASTER_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_MASTER_P (MVNDRMTB)
    ├── [PROCEDURE] SUB_MMSSET_P (MGOODSTB)
    ├── [PROCEDURE] SUB_MRECIP_P (MGOODSTB)
    ├── [PROCEDURE] SUB_NEWCUSTMSG_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_RECIPE_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_RECIPE_IO_P (TGOODSTB)
    ├── [PROCEDURE] SUB_SET_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SET_IO_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SL_SET_GOODS_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SNETDT_P (MGOODSTB)
    ├── [PROCEDURE] SUB_SNETDT_P (MMEMBVTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_AFTER_PROC_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_MAIN_P (IMCRIOTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_MAIN_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_MAIN_P (OBSLPDTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_MAIN_P (OBSLPHTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_PROC_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_PROC_P (OBSLPDTB)
    ├── [PROCEDURE] SUB_STOCK_MGMVHD_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_MGMVHD_P (TGOODSTB)
    ├── [PROCEDURE] SUB_TEMP2GD_P (MGOODSTB)
    ├── [PROCEDURE] SUB_TEMP2GD_P (MMEMBVTB)
    ├── [PROCEDURE] SUB_TEMPCLS2_P_CHAIN (TMSCLSTB)
    ├── [PROCEDURE] SUB_TEMPGD_P (MGOODSTB)
    ├── [PROCEDURE] SUB_TEMPGD_P (MMEMBVTB)
    ├── [PROCEDURE] SUB_TMPRGD_P01 (MGOODSTB)
    ├── [PROCEDURE] SUB_TMPRGD_P01 (MMEMBSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_P (TGOODSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_SINGLE_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_SINGLE_P (TGOODSTB)
    ├── [PROCEDURE] SUB_VDORDER_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_VDORDER_P (OBSLPDTB)
    └── [PROCEDURE] SUB_VDORDER_P (OBSLPHTB)
```
