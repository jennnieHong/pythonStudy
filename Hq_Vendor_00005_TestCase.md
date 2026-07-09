# Hq_Vendor_00005 — 발주관리(본사) 단위 테스트케이스

> **화면**: [HQ] 거래처 > 발주관리  
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00005`  
> **@Transactional**: rollbackFor = {RuntimeException.class, Exception.class}  
> **요청 방식**: 
>   - 조회 API = `@RequestBody` 또는 파라미터 없음 (URL 바인딩)
>   - CUD 등록/추가 = `@RequestParam` 다중 배열 및 폼 파라미터
>   - CUD 확정/삭제/일괄저장 = `@RequestBody` List 또는 Map (JSON 형식)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | 전 엔드포인트 |
| `msNo` | `NC0007` | getVatFg, selectVendorOrderList, selectVendorGoodsList, saveVendorOrder, updateVendorOrder |
| `ID` | `shopadmin` | saveVendorOrder, updateVendorOrder, confirmVendorOrder |

---

## 엔드포인트 목록 (11개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getVatFg` | 부가세 포함 여부 조회 | (파라미터 없음) | `String` | SELECT | MMEMBVTB  |
| 2 | `/selectVendorOrderList` | 발주관리 등록 전표 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, TVNDRMTB  |
| 3 | `/selectVendorOrderDetailList` | 발주관리 등록 전표 상세내역 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, TGOODSTB, MNAMEMTB, TMSCLSTB, IMCRIOTB  |
| 4 | `/selectVendorGoodsList` | 발주등록 : 발주상품 조회 | `@RequestBody` | `List` | SELECT | IMCRIOTB, TMSCLSTB, TGOODSTB, TVNDRGTB, MNAMEMTB  |
| 5 | `/getCloseYn` | 마감 여부 조회 | (파라미터 없음) | `String` | SELECT | IMREMSTB  |
| 6 | `/saveVendorOrder` | 발주등록 : 발주상품등록 | `@RequestParam` 다중 배열 | `String` | INSERT | OBSLPHTB, OBSLPDTB  |
| 7 | `/updateVendorOrder` | 상품추가 : 발주상품추가 | `@RequestParam` 다중 배열 | `String` | INSERT | OBSLPDTB, OBSLPHTB  |
| 8 | `/confirmVendorOrder` | 확정 | `@RequestBody` | `String` | UPDATE | OBSLPHTB, OBSLPDTB  |
| 9 | `/deleteVendorOrder` | 삭제 | `@RequestBody` | `String` | DELETE | OBSLPHTB, OBSLPDTB  |
| 10 | `/updateRemark` | 비고적용 : 매입요청사항 저장 | `@RequestBody` | `String` | UPDATE | OBSLPHTB  |
| 11 | `/saveVendorOrderGoods` | 일괄저장 : 발주상품 일괄 저장 | `@RequestBody` | `String` | UPDATE/DELETE | OBSLPDTB, OBSLPHTB  |

---

## 1. `/getVatFg` — 부가세 포함 여부 조회

| No | 세션 조건 | 예상값 |
|----|----------|-------|
| 1-1 | chainNo=`C001`, msNo=`NC0007` | `"Y"` 또는 `"N"` |
| 1-2 | 세션 없음 (미로그인) | NullPointerException 또는 401 |

---

## 2. `/selectVendorOrderList` — 발주관리 등록 전표 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001`, msNo=`NC0007` | `{"searchFromDate":"20260616","searchEndDate":"20260616"}` | 해당 기간 내의 미확정(`PROC_FG = '0'`) 일반 발주(`SLIP_FG = '0'`) 전표 목록 |
| 2-2 | chainNo=`C001`, msNo=`NC0007` | `{"searchFromDate":"20260616","searchEndDate":"20260616","vendorCd":"000002"}` | 특정 거래처 필터링 적용 조회 |

---

## 3. `/selectVendorOrderDetailList` — 발주관리 등록 전표 상세내역 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"orderDate":"20260616","msNo":"NC0007","slipNo":"0004"}` | 해당 전표의 상세 상품 라인 목록 및 상품명, 단가, 수량 등 정보 |

---

## 4. `/selectVendorGoodsList` — 발주등록 : 발주상품 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`, msNo=`NC0007` | `{"com_selectVendorCd":"000002","orderDate":"20260616","slipNo":"0004"}` | 해당 거래처에서 공급 가능한 발주 대상 상품 목록 (이미 전표에 추가된 상품 제외) |

---

## 5. `/getCloseYn` — 마감 여부 조회

| No | 세션 조건 | 예상값 |
|----|----------|-------|
| 5-1 | msNo=`NC0007` | 현재 월이 마감되었을 경우 `"closed"`, 미마감 시 `""` |

---

## 6. `/saveVendorOrder` — 발주등록 (본사 화면 비활성)

**특이사항**: 본사 화면(`hq_vendor_00005.js`)의 `fnAddVendorOrder`가 차단되어 있으나 백엔드 API 자체는 노출 상태.

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 6-1 | ID=`shopadmin` | `orderDate=20260616&deliveryDate=20260617&vendor=000002&vatFg=Y&goodsCd[]=T0000002&inQty[]=1&orderQty[]=10&orderEaQty[]=10&usuprice[]=1000&orderVat[]=100&orderAmt[]=10000` | `"registerVendorOrder"` (정상 등록) |
| 6-2 | ID=`shopadmin` | `deliveryDate`가 오늘보다 이전 날짜인 경우 | `"failDeliveryDate"` (저장 실패) |

---

## 7. `/updateVendorOrder` — 상품추가 (본사 화면 비활성)

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 7-1 | ID=`shopadmin` | `orderDate=20260616&slipNo=0004&goodsCd[]=T0000002&inQty[]=1&orderQty[]=5&orderEaQty[]=5&usuprice[]=1000&orderVat[]=100&orderAmt[]=5000` | `"registerVendorOrderGoods"` (상품 추가 성공) |

---

## 8. `/confirmVendorOrder` — 확정

**서비스 핵심 흐름**:
1. 헤더 `PROC_FG` = `'2'`(발주확정) 업데이트.
2. 디테일 `PROC_FG` = `'2'` 업데이트.
3. 디테일 트리거 `Tr_OBSLPD_T01_Service` 및 `T02_Service` 기동.
   * **수불 연쇄 제외 검증**: 발주확정 상태(`PROC_FG = '2'`)는 수량 실시간 가감 대상이 아니므로 `IMTRLGTB` 및 `obslplog`에 데이터가 적재되지 않는 것이 정상 비즈니스 룰입니다.

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 8-1 | ID=`shopadmin` | `[{"orderDate":"20260616","msNo":"NC0007","slipNo":"0004","slipFg":"0"}]` | `"success"` (전표 및 상세 행 상태 `2`로 변동) |

---

## 9. `/deleteVendorOrder` — 삭제

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 9-1 | `[{"orderDate":"20260616","msNo":"NC0007","slipNo":"0004","slipFg":"0"}]` | `"success"` (HD 및 DT 레코드 DELETE 수행) |

---

## 10. `/updateRemark` — 비고적용

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 10-1 | `{"orderDate":"20260616","msNo":"NC0007","slipNo":"0004","remark":"본사 요청사항 기재"}` | `"success"` (OBSLPHTB의 REMARK 업데이트) |

---

## 11. `/saveVendorOrderGoods` — 일괄저장

**수량 분기 로직**:
* 발주수량 `purchQty` = `0` 이거나 빈값인 경우: 디테일 행 삭제 (`deleteVendorOrderGoods`) + 트리거 `D` 기동.
* 발주수량이 있는 경우: 디테일 행 정보 업데이트 (`updateVendorOrderGoodsDt`) + 트리거 `U` 기동.
* 만약 전표 내 모든 상품의 발주수량이 0이 되면 전표 자체가 삭제됩니다 (`deleteVendorOrderSlip`).

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 11-1 | `[{"orderDate":"20260616","msNo":"NC0007","slipNo":"0004","lineNo":"0001","goodsCd":"T0000002","purchQty":5,"purchUcost":1000,"purchAmt":5000,"purchVat":500,"inQty":1,"purchTot":5500}]` | 특정 행 수량 수정 반영 및 헤더 합계 갱신 |
| 11-2 | `[{"orderDate":"20260616","msNo":"NC0007","slipNo":"0004","lineNo":"0001","goodsCd":"T0000002","purchQty":0}]` | 수량 0 지정 시 해당 상품 라인 삭제 |

---

## PowerShell 테스트 검증 명령

```powershell
# 1. 로그인 수행 (shopadmin / 0000)
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/vendor/hq_vendor_00005"
$h = @{"Content-Type"="application/json"}

# 2. 전표 목록 조회
Invoke-RestMethod -Uri "$base/selectVendorOrderList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260616","searchEndDate":"20260616"}'

# 3. 상세내역 조회
Invoke-RestMethod -Uri "$base/selectVendorOrderDetailList" -Method POST -Headers $h -WebSession $session `
  -Body '{"orderDate":"20260616","msNo":"NC0007","slipNo":"0004"}'
```
