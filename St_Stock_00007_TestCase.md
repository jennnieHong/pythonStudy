# St_Stock_00007 — 매장 현재고 조회 단위 테스트케이스

> **화면**: [ST] 재고 > 재고조회 > 현재고 조회  
> **URL Prefix**: `POST /backoffice/data/st/stock/st_stock_00007`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않아 **실제 트리거가 직접 기동하지는 않습니다.** 다만, 다른 화면(매장 상품 마스터 CUD 등)에서 발생하는 변경 사항이 재고 테이블(`IMMMIOTB`, `IMDDIOTB`)에 연쇄적으로 기동되어 조회 결과에 영향을 줄 수 있습니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, searchStock, searchStockTot |
| `msNo` | `NC0001` (카페매장 - fnbcafe 계정의 소속 매장) | search, searchStock, searchStockTot (컨트롤러에서 세션 값을 강제 주입함) |
| `ID` | `fnbcafe` (카페 매장 관리자) | 공통 세션 및 권한 체크 |

---

## 엔드포인트 목록 (3개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 매장 현재고 목록 및 총 건수 조회 | `@RequestBody` | `Map` (total+rows) | SELECT | MGOODSTB<br>IMMMIOTB<br>IMDDIOTB<br>MMSSRCTB |
| 2 | `/searchStock` | 특정 상품 상세 수불/판매 내역 조회 | `@RequestBody` | `Map` (stockList, stockTotList, recipeSaleList) | SELECT | IMDDIOTB<br>IMMMIOTB<br>TB_SL_RECIPE_GOODS |
| 3 | `/searchStockTot` | 총 수불 요약 조회 | `@RequestBody` | `List` (stockTotList) | SELECT | IMDDIOTB<br>IMMMIOTB |

---

## 1. `/search` — 매장 현재고 목록 조회

**특이사항**:
* `offset` 및 `limit` 값을 파싱하여 내부에서 `startIdx = offset + 1`, `endIdx = offset + limit` 로 1-indexed 페이징 범위 계산.
* 세션의 `msNo` 및 `chainNo`를 강제 주입하므로, RequestBody에 매장코드를 전달하더라도 컨트롤러에서 무시되고 로그인된 사용자의 매장 정보만 조회됩니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 1-1 | msNo=`NC0001` | 재고 데이터 존재 | `{"searchDate":"20250623","offset":0,"limit":10}` | `{"total": 24, "rows": [...]}` (로그인 매장 기준 페이징 조회) |
| 1-2 | msNo=`NC0001` | 분류 데이터 존재 | `{"searchDate":"20250623","offset":0,"limit":10,"lclassCd":"001","mclassCd":"001","sclassCd":"001"}` | 대/중/소분류 카테고리 필터링 조회 |
| 1-3 | msNo=`NC0001` | 상품 정보 존재 | `{"searchDate":"20250623","offset":0,"limit":10,"goodsCdNm":"아메리카노"}` | 상품명/상품코드 LIKE 검색 정상 동작 여부 |
| 1-4 | msNo=`NC0001` | 바코드 매핑 존재 | `{"searchDate":"20250623","offset":0,"limit":10,"barcode":"880"}` | `MMSSRCTB` 조인을 통한 바코드 검색 동작 여부 |
| 1-5 | msNo=`NC0001` | - | `{"searchDate":"20250623"}` (offset/limit 누락) | **NullPointerException** 또는 형변환 예외 (컨트롤러 L65~66 방어 코드 누락 여부 확인) |

---

## 2. `/searchStock` — 특정 상품 상세 수불 및 판매 내역 조회

**특이사항**:
* 팝업 원장용 상세 정보 조회. 일수불 내역(`stockList`), 총 수불 요약(`stockTotList`), 레시피 판매내역(`recipeSaleList`)을 동시에 조회하여 Map으로 반환.
* 세션의 `msNo`를 강제 적용하므로, 로그인한 매장 내부의 재고 원장 이력만 노출됩니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 2-1 | msNo=`NC0001` | 일수불, 월수불, 판매내역 존재 | `{"goodsCd":"000011","startDate":"20250601","endDate":"20250623"}` | `stockList`, `stockTotList`, `recipeSaleList` 키를 포함한 Map 객체 반환 |
| 2-2 | msNo=`NC0001` | 재고 거래 내역 없음 | `{"goodsCd":"999999","startDate":"20250601","endDate":"20250623"}` | 빈 리스트(Empty List) 및 기초재고 0 출력 확인 |

---

## 3. `/searchStockTot` — 총 수불 요약 조회

**특이사항**:
* 단독 호출로 총 월수불/일수불 집계 합산 데이터를 List 형태로 리턴.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 3-1 | msNo=`NC0001` | 재고 데이터 존재 | `{"goodsCd":"000011","startDate":"20250601","endDate":"20250623"}` | 기초 재고와 누적 수불 수량(매입, 매출, 폐기, 조정 등) 합계 객체 반환 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/stock/st_stock_00007"
$h = @{"Content-Type"="application/json"}

# 1-1. 매장 현재고 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchDate":"20250623","offset":0,"limit":10}'

# 2-1. 상세 수불/판매 내역 조회 (원장 팝업)
Invoke-RestMethod -Uri "$base/searchStock" -Method POST -Headers $h -WebSession $session `
  -Body '{"goodsCd":"000011","startDate":"20250601","endDate":"20250623"}'

# 3-1. 총 수불 요약 조회
Invoke-RestMethod -Uri "$base/searchStockTot" -Method POST -Headers $h -WebSession $session `
  -Body '{"goodsCd":"000011","startDate":"20250601","endDate":"20250623"}'
```

---

## 주요 검증 포인트

* **[Paging] 페이징 범위 수식**: `offset`과 `limit`을 활용해 도출한 `startIdx`, `endIdx`가 MyBatis 쿼리(`ROWNUM` 처리 범위) 내에 정확히 매핑되는지 검증.
* **[Filter] 매장 자동 바인딩 검증**: 로그인한 매장코드(`msNo`)가 백엔드 세션에서 강제 주입되어, 타 매장의 재고 데이터에 접근하는 보안 취약성이 차단되어 있는지 검증.
* **[Math] 나눗셈 0 방어 코드 검증**: 입수(`IN_QTY`) 마스터 데이터가 0 또는 NULL일 때 `division by zero` 런타임 에러가 발생하지 않는지, 향후 보완 조치 여부 검증.
