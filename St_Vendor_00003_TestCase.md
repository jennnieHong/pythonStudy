# St_Vendor_00003 — 매장 발주관리 단위 테스트케이스

> **화면**: [ST] 매입발주 > 매입관리 > 발주관리  
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00003`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식**: 혼용 (조회 = `@RequestBody` / CUD = `@RequestParam` 배열 및 `@RequestBody` 혼용)  
> **DB 트리거 영향도**: OBSLPDTB, OBSLPHTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (확정 시 IMTRLGTB 영향 없음)

---

## 1. 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `NC0007` | getVatFg, selectVendorGoodsList, getCloseYn, saveVendorOrder, updateVendorOrder, getAffiliateCompany |
| `msNo` | `NC0007` | getVatFg, selectVendorOrderList, selectVendorOrderDetailList, selectVendorGoodsList, saveVendorOrder, updateVendorOrder, getAffiliateCompany |
| `ID` (userId) | `fnbcafe` | saveVendorOrder, confirmVendorOrder |

---

## 2. 엔드포인트 목록 (11개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getVatFg` | 부가세 포함 여부 조회 | (파라미터 없음) | `String` | SELECT | MMEMBVTB  |
| 2 | `/selectVendorOrderList` | 발주전표 헤더 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, MVNDRMTB  |
| 3 | `/selectVendorOrderDetailList`| 발주전표 상세 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, MGOODSTB, MNAMEMTB, MMSCLSTB, IMCRIOTB |
| 4 | `/selectVendorGoodsList` | 발주용 상품 목록 조회 | `@RequestBody` | `List` | SELECT | IMCRIOTB, MMSCLSTB, MGOODSTB, MVNDRGTB, MNAMEMTB |
| 5 | `/getCloseYn` | 가맹점 마감 여부 조회 | `@RequestBody` | `String` | SELECT | TB_TOT_AVG_COST |
| 6 | `/saveVendorOrder` | 발주 전표 신규 저장 (Header + Detail) | `@RequestParam` | `String` | INSERT | OBSLPHTB, OBSLPDTB |
| 7 | `/updateVendorOrder` | 발주 전표에 상품 추가 | `@RequestParam` | `String` | INSERT | OBSLPDTB |
| 8 | `/confirmVendorOrder` | 발주 전표 확정 (상태 '2' 변경) | `@RequestBody` | `String` | UPDATE | OBSLPHTB, OBSLPDTB |
| 9 | `/deleteVendorOrder` | 발주 전표 삭제 | `@RequestBody` | `String` | DELETE | OBSLPHTB, OBSLPDTB |
| 10| `/updateRemark` | 매입요청 비고 내용 수정 | `@RequestBody` | `String` | UPDATE | OBSLPHTB |
| 11| `/saveVendorOrderGoods` | 상세 발주상품 일괄 수정 (수량0이면 삭제) | `@RequestBody` | `String` | UPDATE/DELETE | OBSLPHTB, OBSLPDTB |

---

## 3. 엔드포인트별 테스트케이스 상세

### 3.1. `/getVatFg` — 부가세 여부 조회
* **선행조건**: 세션 내 `chainNo`, `msNo` 바인딩 필요.
* **테스트 케이스**:
  - **3.1-1**: `chainNo = 'NC0007'`, `msNo = 'NC0007'` 조회 시 가맹점의 부가세구분 값 `"0"`, `"1"` 등 정상 반환.

### 3.2. `/selectVendorOrderList` — 발주전표 헤더 조회
* **조회 정책**: `SLIP_FG = '0'`(발주), `PROC_FG = '0'`(미확정) 상태인 전표만 노출.
* **테스트 케이스**:
  - **3.2-1**: 조회 시작일(`searchFromDate`), 종료일(`searchEndDate`)을 파라미터로 전달하여 해당 기간 내 미확정 발주 전표만 정상 노출되는지 검증.
  - **3.2-2**: 특정 거래처(`vendorCd`)를 지정해 필터링 정상 적용 확인.

### 3.3. `/selectVendorOrderDetailList` — 상세 품목 조회
* **테스트 케이스**:
  - **3.3-1**: 특정 전표 정보 `orderDate`, `slipNo`를 지정하여 하단 그리드에 해당 발주 전표의 상품 목록이 바인딩되는지 확인.

### 3.4. `/selectVendorGoodsList` — 발주용 상품 목록 조회
* **분기 조건**: 세션 체인구분 `affiliateCompany = '1'`(브랜드숍)인 경우 `getPrePurchWhMsNoYn()` 추가 확인.
* **테스트 케이스**:
  - **3.4-1**: 모달창 오픈 시 거래처 코드(`com_selectVendorCd`)를 필수로 전송하여 발주 가능한 상품들이 정상 노출되는지 검증.

### 3.5. `/getCloseYn` — 가맹점 마감 여부 조회
* **판정**: 마감 월 기준 `TB_TOT_AVG_COST`에 레코드가 1건 이상 존재하면 `"closed"`를 반환하여 발주 등록/확정을 제어.
* **테스트 케이스**:
  - **3.5-1**: 마감되지 않은 월에 대해 `getCloseYn`을 호출하여 빈 문자열 `""`이 반환되는지 확인.
  - **3.5-2**: 마감된 월에 대해 호출하여 `"closed"` 문자가 리턴되어 저장/확정이 차단되는지 검증.

### 3.6. `/saveVendorOrder` — 발주 전표 신규 저장 (Header + Detail)
* **주의 결함**: EDB 마이그레이션 중 numeric 빈 문자열 유입 시 캐스팅 에러 방지를 위해 safe casting (`COALESCE(NULLIF(..., ''), '0')::numeric`) 검증 완료.
* **테스트 케이스**:
  - **3.6-1**: 납품예정일이 오늘 날짜보다 이전일 경우 `"failDeliveryDate"` 반환 검증.
  - **3.6-2**: 정상 납품예정일과 다중 상품 배열을 전송하여 신규 전표 헤더(`OBSLPHTB`) 및 디테일(`OBSLPDTB`)이 생성되고 `"registerVendorOrder"`가 반환되는지 확인.

### 3.7. `/updateVendorOrder` — 발주 전표에 상품 추가
* **테스트 케이스**:
  - **3.7-1**: 이미 등록된 전표(`slipNo`)를 지정하고 추가 상품 정보 배열을 전송하여 디테일 테이블에 추가 적재되고 헤더 합계금액이 갱신되는지 확인 (`"registerVendorOrderGoods"` 반환).

### 3.8. `/confirmVendorOrder` — 발주 전표 확정
* **동작 방식**: `OBSLPHTB` 및 `OBSLPDTB`의 `PROC_FG` 상태값을 `'2'`(발주확정)로 업데이트.
* **트리거 검증**: 확정 처리 시 가상 트리거 `Tr_OBSLPD_T01`에 의해 수불로그 적재 여부 추적 -> 발주 단계(`slipFg = 0`, `procFg = 2`)에서는 실시간 수불로그(`IMTRLGTB`)가 생성되지 않는 정상 비즈니스 룰 검증.
* **테스트 케이스**:
  - **3.8-1**: 미확정 전표를 선택해 확정 완료 시, 전표 진행 상태가 `'2'`로 갱신되고, 화면 그리드(PROC_FG='0'만 노출)에서 즉시 사라지는지 검증 (`"success"` 반환).

### 3.9. `/deleteVendorOrder` — 발주 전표 삭제
* **테스트 케이스**:
  - **3.9-1**: 미확정 전표를 선택해 삭제 처리 시 헤더 및 디테일 테이블에서 레코드가 물리적으로 DELETE 처리되는지 검증 (`"success"` 반환).

### 3.10. `/updateRemark` — 매입요청 비고 내용 수정
* **테스트 케이스**:
  - **3.10-1**: 비고란 수정 후 저장 시 헤더 테이블 `REMARK` 컬럼에 내용이 실시간 갱신되는지 확인.

### 3.11. `/saveVendorOrderGoods` — 상세 발주상품 일괄 수정
* **분기 조건**: 발주 수량이 `0`이거나 빈값으로 수정된 상품은 디테일 테이블에서 물리 삭제(`deleteVendorOrderGoods`)되며, 모든 상품 수량이 0이 되면 전표 자체가 삭제(`deleteVendorOrderSlip`)됨.
* **테스트 케이스**:
  - **3.11-1**: 일부 상품의 수량을 수정 후 일괄저장 시 `updateVendorOrderGoodsDt` 정상 가동 확인.
  - **3.11-2**: 특정 상품 수량을 `0`으로 지정해 저장 시 해당 상세 행만 삭제되는지 검증.
  - **3.11-3**: 모든 상품 수량을 `0`으로 지정해 저장 시 전표 헤더 및 디테일이 통째로 삭제되는지 검증.

---

## 4. PowerShell API 검증 스크립트 예제

로컬 개발 서버에서 세션을 맺은 후 각 API의 응답을 수동 검증하기 위한 PowerShell 명령어 셋입니다.

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
# 0. 세션 로그인 수행
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/vendor/st_vendor_00003"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 부가세 구분 조회
Invoke-RestMethod -Uri "$base/getVatFg" -Method POST -ContentType $f -WebSession $session -Body "msNo=NC0007&chainNo=NC0007"

# 2. 발주 전표 목록 조회
Invoke-RestMethod -Uri "$base/selectVendorOrderList" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"NC0007","searchFromDate":"20260616","searchEndDate":"20260616"}'

# 3. 마감 여부 조회 (평소에는 공백 반환 확인)
Invoke-RestMethod -Uri "$base/getCloseYn" -Method POST -Headers $h -WebSession $session `
  -Body '{"orderDate":"20260616","chainNo":"NC0007"}'
```
