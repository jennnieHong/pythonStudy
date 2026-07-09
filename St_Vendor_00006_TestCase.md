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
| 8 | `/cancelSlip` | 무발주입고 취소 (화면 미제공 & 트리거 차단) | `@RequestParam` 배열 | `String` | UPDATE (차단) | OBSLPDTB<br>OBSLPHTB  |
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

## 8. `/cancelSlip` — 무발주입고 취소 (화면 미제공 & 트리거 차단)

**정책**: 화면상 "입고취소" 버튼이 주석 처리되어 접근 불가하며, 자바 가상 트리거 `Tr_OBSLPD_T02_Service` 내 Validation 1(`new.PROC_FG = '5'` 일 때 에러)이 활성화되어 백엔드에서도 변경을 차단합니다.

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 8-1 | chainHqYn=`Y` | `orderDate[]=20260526&slipNo[]=SL001&purchDate[]=20260526&msNo[]=MS001` | **500 (OBSLPD_T02 : PROC_FG ERROR!!)** ★★★ |
| 8-2 | (동일) | 다중: `orderDate[]` 2개 + 나머지 1개 | `slipNo[1]` → **ArrayIndexOutOfBoundsException** 또는 **트리거 차단** |
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

# 8-1. 취소 (가상 트리거 작동으로 500 에러 발생 기대)
Invoke-RestMethod -Uri "$base/cancelSlip" -Method POST -ContentType $f -WebSession $session `
  -Body "orderDate[]=20260526&slipNo[]=SL001&purchDate[]=20260526&msNo[]=MS001"
# 예상: 500 Internal Server Error (OBSLPD_T02 : PROC_FG ERROR!!)
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
□ cancelSlip — 가상 트리거 `Tr_OBSLPD_T02_Service` 활성화로 인한 `PROC_FG = '5'` 변경 에러 차단 ★★★
□ updateGoodsList — cnt==goodsCd.length 전체 삭제 vs 부분 삭제 분기 로직 확인
□ saveVendorOrder — flag="add": slipNo 미채번, flag 그 외: insertOrdPurchSlip 후 slipNo 채번
□ cancelSlip 서비스 — Dt 취소 루프 완료 후 Hd 취소 (2개 루프 순서 보장) ✓
□ @Transactional rollbackFor Exception — insertOrder(3단계), confirmOrdPurch(2단계), cancelSlip(트리거 오류 시) rollback 보장
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
