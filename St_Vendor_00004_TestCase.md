# St_Vendor_00004 — 매장 입고관리 단위 테스트케이스

> **화면**: [ST] 매입발주 > 매입관리 > 입고관리  
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00004`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: `OBSLPDTB`, `OBSLPHTB` 업데이트에 따라 실시간 트리거(`Tr_OBSLPH_T01`, `Tr_OBSLPD_T01` 등) 연쇄 동작함.

---

## ⚠️ 서비스 핵심 소스 분석 및 잠재적 비즈니스 분기

### 1. 입고 물량 오류 시 사유 미입력 차단 분기 (★★★)
* **소스 분석 (`St_Vendor_00004_Service.java` L117~170)**:
  * 입고 확정 시, 시스템은 발주수량과 실제 매입입고수량이 일치하는지 `selectReasonYn`을 통해 대조합니다.
  * 수량이 달라 사유 입력이 필수(`REASON_YN = 'Y'`)인데 사유 내용이 공백인 경우(`REASON_MSG = 'N'`), 변수 `reasonWFg`를 증가시킵니다.
  * **결과**: `reasonWFg > 0`인 경우 확정 프로세스를 중단하고 화면으로 `"chkReasonMsg"`를 리턴하여 **"물량 오류 사유를 입력하십시오."** 경고를 띄웁니다.

### 2. 다중 전표 확정 루프 내 NullPointerException 취약점 (★★★)
* **소스 분석 (`St_Vendor_00004_Service.java` L121~123)**:
  * 서비스 단의 `confirmVendorOrder`는 리스트 루프를 돌며 각 맵에서 `orderDate`, `msNo`, `slipNo` 값을 강제로 꺼냅니다.
  * **결과**: 만약 팝업이나 API 호출 시 리스트 내의 특정 맵 오브젝트에 필수 필드(`orderDate` 등)가 유실되어 들어오면, `toString()` 호출 시점에 즉각 **`NullPointerException`**이 발생하며 트랜잭션이 전체 롤백됩니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | getVatFg, selectVendorOrderList, selectVendorOrderDetailList, getCloseYn, confirmVendorOrder, saveVendorOrderGoods |
| `msNo` | `NC0007` (매장코드) | getVatFg, selectVendorOrderList, confirmVendorOrder |
| `ID` | `fnbcafe` | confirmVendorOrder, saveVendorOrderGoods (최종 수정자 주입용) |

---

## 엔드포인트 목록 (6개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getVatFg` | 부가세 포함 여부 조회 | (파라미터 없음) | `String` | SELECT | WFNENVTB |
| 2 | `/selectVendorOrderList` | 입고 대상 전표 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, MVNDRMTB |
| 3 | `/selectVendorOrderDetailList` | 전표 상세 상품 내역 조회 | `@RequestBody` | `List` | SELECT | OBSLPDTB, TGOODSTB |
| 4 | `/getCloseYn` | 원가 마감 여부 조회 | (파라미터 없음) | `String` | SELECT | TSM_SALS_DAYCLS_MST |
| 5 | `/saveVendorOrderGoods` | 수량 및 물량오류 사유 임시 저장 | `@RequestBody` | `String` | UPDATE | OBSLPDTB, OBSLPHTB |
| 6 | `/confirmVendorOrder` | 입고 최종 확정 (재고 차감 트리거 가동) | `@RequestBody` | `String` | UPDATE | OBSLPDTB, OBSLPHTB |

---

## 1. 조회 계열 엔드포인트 테스트 케이스

| No | URL | 세션 및 파라미터 분기 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|---|---|------------|---------------------|----------------------|
| 1-1 | `/getVatFg` | 정상 세션 바인딩 | 매장 설정 존재 | N/A (GET 변환) | `"1"` 또는 `"0"` 부가세 플래그 반환 |
| 1-2 | `/selectVendorOrderList` | msNo=`NC0007` | 입고 대기 전표 존재 | `{"searchFromDate":"20240201","searchToDate":"20240201"}` | NC0007 매장의 당일 미확정 입고 대상 목록 반환 |
| 1-3 | `/selectVendorOrderDetailList` | 정상 chainNo 세션 | 해당 전표 디테일 존재 | `{"slipNo":"SL2024020101"}` | 전표 내 상세 상품 목록, 발주 및 매입수량 반환 |
| 1-4 | `/getCloseYn` | 정상 마감 상태 | 당일 마감 미완료 | N/A | `""` (공백 리턴하여 확정 프로세스 진행 가능) |
| 1-5 | `/getCloseYn` | 정상 마감 상태 | 당일 마감 완료 | N/A | `"closed"` (확정 버튼 비활성화) |

---

## 2. 저장/확정 계열 엔드포인트 테스트 케이스

| No | URL | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|---|---|------------|---------------------|----------------------|
| 2-1 | `/saveVendorOrderGoods` | 정상 임시 저장 | 미확정 전표 존재 | `[{"orderDate":"20240201","msNo":"NC0007","slipNo":"SL2024020101","goodsCd":"T0000001","purchQty":10,"reasonCd":"01","reasonMsg":"납품부족"}]` | `"save"` 반환 및 DB `OBSLPDTB` 내 임시수량/사유 업데이트 완료 |
| 2-2 | `/confirmVendorOrder` | 수량 정합성 일치 (오류 없음) | 임시저장 상태 | `[{"orderDate":"20240201","msNo":"NC0007","slipNo":"SL2024020101","purchDate":"20240201"}]` | `"confirm"` 리턴 및 `PROC_FG = '4'` 변경, 현재고 증가 트리거 작동 |
| 2-3 | `/confirmVendorOrder` | **물량오류 발생 + 사유 미입력** ★ | 발주량(10) != 입고량(5) | `[{"orderDate":"20240201","msNo":"NC0007","slipNo":"SL2024020101","purchDate":"20240201"}]` | **`"chkReasonMsg"`** 반환 및 확정 프로세스 차단 검증 |
| 2-4 | `/confirmVendorOrder` | 물량오류 발생 + 사유 입력 완료 | 사유 임시저장 완료 상태 | `[{"orderDate":"20240201","msNo":"NC0007","slipNo":"SL2024020101","purchDate":"20240201"}]` | `"confirm"` 리턴 및 확정 처리 완료 |
| 2-5 | `/confirmVendorOrder` | **필수 파라미터 누락** ★ | - | `[{"msNo":"NC0007"}]` (orderDate 누락) | `orderDate.toString()` 호출 시 **NullPointerException** (500) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/vendor/st_vendor_00004"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 입고 대상 목록 조회
Invoke-RestMethod -Uri "$base/selectVendorOrderList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20240201","searchToDate":"20240201"}'

# 2. 임시저장 테스트
Invoke-RestMethod -Uri "$base/saveVendorOrderGoods" -Method POST -Headers $h -WebSession $session `
  -Body '[{"orderDate":"20240201","msNo":"NC0007","slipNo":"SL001","goodsCd":"T0000001","purchQty":10,"reasonCd":"01","reasonMsg":"정상납품"}]'

# 3. 확정 테스트 (물량 상이로 chkReasonMsg 리턴 기대 테스트)
Invoke-RestMethod -Uri "$base/confirmVendorOrder" -Method POST -Headers $h -WebSession $session `
  -Body '[{"orderDate":"20240201","msNo":"NC0007","slipNo":"SL001","purchDate":"20240201"}]'
```

---

## 주요 검증 포인트

```
□ confirmVendorOrder — 발주수량 != 입고수량일 때 사유(REASON_MSG) 검증을 거쳐 chkReasonMsg를 리턴하는지 확인
□ confirmVendorOrder — 파라미터 맵 객체 누락 시 루프 내 toString()에 의한 NPE 검증 및 Transactional 롤백 확인
□ confirmVendorOrder — 확정 성공 후 tr_OBSLPH_T01 및 tr_OBSLPD_T01 트리거 서비스가 연달아 가동되는지 확인
□ saveVendorOrderGoods — 수량 변경 저장 시 Hd와 Dt 순차 업데이트 무결성 및 'save' 리턴 확인
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅ (4/4)

| 엔드포인트 | @ServiceLog 선언 현황 |
|-----------|---------------------|
| `/selectVendorOrderList` | ✅ SELECT (컨트롤러 L84) |
| `/selectVendorOrderDetailList` | ✅ SELECT (컨트롤러 L109) |
| `/saveVendorOrderGoods` | ✅ UPDATE (컨트롤러 L192) |
| `/confirmVendorOrder` | ✅ UPDATE (컨트롤러 L161) |
