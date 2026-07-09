# Hq_Stock_00001 — 현재고 조회 단위 테스트케이스

> **화면**: [HQ] 재고 > 재고조회 > 현재고 조회  
> **URL Prefix**: `POST /backoffice/data/hq/stock/hq_stock_00001`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않아 **실제 트리거가 직접 기동하지는 않습니다.** 다만, 조회 대상인 상품 정보(`TGOODSTB`) 및 매장 정보(`MGOODSTB`)에 변경을 발생시키는 타 마스터 관리 화면 등에서 CUD가 발생 시 `Tr_TGOODS_T01_Service` 등이 기동하여 하위 재고 및 마스터 데이터를 연쇄 처리하므로 간접 영향 트리거로 명시합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, searchStock, searchStockTot |
| `ID` | `NC0005` (fnb 본사 관리자) | 공통 세션 및 권한 체크 |

---

## 엔드포인트 목록 (3개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 현재고 목록 및 총 건수 조회 | `@RequestBody` | `Map` (total+rows) | SELECT | MGOODSTB<br>IMMMIOTB<br>IMDDIOTB<br>MMSSRCTB<br>MMEMBSTB |
| 2 | `/searchStock` | 특정 매장/상품 상세 수불/판매 내역 조회 | `@RequestBody` | `Map` (stockList, stockTotList, recipeSaleList) | SELECT | IMDDIOTB<br>IMMMIOTB<br>TB_SL_RECIPE_GOODS |
| 3 | `/searchStockTot` | 총 수불 요약 조회 | `@RequestBody` | `List` (stockTotList) | SELECT | IMDDIOTB<br>IMMMIOTB |

---

## 1. `/search` — 현재고 목록 조회

**특이사항**:
* `offset` 및 `limit` 값을 파싱하여 내부에서 `startIdx = offset + 1`, `endIdx = offset + limit` 로 1-indexed 페이징 범위 계산.
* `msNo` 가 `ALL`이 아닌 경우 쉼표(`,`)로 분할하여 `msNoArr` 배열로 MyBatis `<foreach>` 파라미터 바인딩 처리.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 1-1 | chainNo=`C001` | 재고 데이터 존재 | `{"searchDate":"20250623","msNo":"ALL","offset":0,"limit":10}` | `{"total": 24, "rows": [...]}` (전체 매장 기준 페이징 조회) |
| 1-2 | chainNo=`C001` | 특정 매장 재고 존재 | `{"searchDate":"20250623","msNo":"NC0001,NC0002","offset":0,"limit":10}` | 지정한 매장 정보만 필터링되어 출력 (`msNoArr` 바인딩 검증) |
| 1-3 | chainNo=`C001` | 분류 데이터 존재 | `{"searchDate":"20250623","msNo":"ALL","offset":0,"limit":10,"lclassCd":"001","mclassCd":"001","sclassCd":"001"}` | 대/중/소분류 카테고리 필터링 조회 |
| 1-4 | chainNo=`C001` | 상품 정보 존재 | `{"searchDate":"20250623","msNo":"ALL","offset":0,"limit":10,"goodsCdNm":"test"}` | 상품명/상품코드 LIKE 검색 정상 동작 여부 |
| 1-5 | chainNo=`C001` | 바코드 매핑 존재 | `{"searchDate":"20250623","msNo":"ALL","offset":0,"limit":10,"barcode":"880"}` | `MMSSRCTB` 조인을 통한 바코드 검색 동작 여부 |
| 1-6 | chainNo=`C001` | - | `{"searchDate":"20250623","msNo":"ALL"}` (offset/limit 누락) | **NullPointerException** 또는 형변환 예외 (컨트롤러 L63~64 방어 코드 누락 여부 확인) |

---

## 2. `/searchStock` — 특정 매장/상품 상세 수불 및 판매 내역 조회

**특이사항**:
* 팝업 원장용 상세 정보 조회. 일수불 내역(`stockList`), 총 수불 요약(`stockTotList`), 레시피 판매내역(`recipeSaleList`)을 동시에 조회하여 Map으로 반환.
* 메인 화면의 그리드가 매장별로 분할 표시되므로 `row.msNo`가 명확히 존재해 단수 매장코드(`#{msNo}`)를 바인딩하여 쿼리함.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 2-1 | chainNo=`C001` | 일수불, 월수불, 판매내역 존재 | `{"msNo":"NC0001","goodsCd":"T0000295","startDate":"20250601","endDate":"20250623"}` | `stockList`, `stockTotList`, `recipeSaleList` 키를 포함한 Map 객체 반환 |
| 2-2 | chainNo=`C001` | 재고 거래 내역 없음 | `{"msNo":"NC0001","goodsCd":"T0000999","startDate":"20250601","endDate":"20250623"}` | 빈 리스트(Empty List) 및 기초재고 0 출력 확인 |
| 2-3 | - | - | `{"msNo":"","goodsCd":"T0000295"}` | 필수 파라미터 누락 시 Mapper의 외부 조인 혹은 SQL 내 오류 대응 확인 |

---

## 3. `/searchStockTot` — 총 수불 요약 조회

**특이사항**:
* 단독 호출로 총 월수불/일수불 집계 합산 데이터를 List 형태로 리턴.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 3-1 | chainNo=`C001` | 재고 데이터 존재 | `{"msNo":"NC0001","goodsCd":"T0000295","startDate":"20250601","endDate":"20250623"}` | 기초 재고와 누적 수불 수량(매입, 매출, 폐기, 조정 등) 합계 객체 반환 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/stock/hq_stock_00001"
$h = @{"Content-Type"="application/json"}

# 1-1. 본사 현재고 조회 (전체 매장)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchDate":"20250623","msNo":"ALL","offset":0,"limit":10}'

# 1-2. 본사 현재고 조회 (특정 다중 매장)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchDate":"20250623","msNo":"NC0001,NC0002","offset":0,"limit":10}'

# 2-1. 상세 수불/판매 내역 조회 (원장 팝업)
Invoke-RestMethod -Uri "$base/searchStock" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"NC0001","goodsCd":"T0000295","startDate":"20250601","endDate":"20250623"}'

# 3-1. 총 수불 요약 조회
Invoke-RestMethod -Uri "$base/searchStockTot" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"NC0001","goodsCd":"T0000295","startDate":"20250601","endDate":"20250623"}'
```

---

## 주요 검증 포인트

* **[Paging] 페이징 범위 수식**: `offset`과 `limit`을 활용해 도출한 `startIdx`, `endIdx`가 MyBatis 쿼리(`ROWNUM` 처리 범위) 내에 정확히 매핑되는지 검증.
* **[Filter] 상세조회 매장 필터 연동 검증**: 메인 현재고 목록 그리드 클릭 시 매장 정보(`row.msNo`)가 상세조회 API(`searchStock`)로 연동 전달되어 해당 매장 하나의 이력만 정확히 로딩되는지 검증.
* **[Trigger Bypass] 상품 정보 동기화 단절 검증**: 본사 상품 등록/수정 시 Java 트리거 서비스가 기동되지 않아 발생하는 현재고 조회상의 정합성 단절 유무 확인.
* **[Math] 나눗셈 0 방어 코드 검증**: 입수(`IN_QTY`) 마스터 데이터가 0 또는 NULL일 때 `division by zero` 런타임 에러가 발생하지 않는지, 향후 보완 조치 여부 검증.

---

## DB 트리거 및 데이터 연관관계도 (코드베이스 전환용)

```text
상품 정보 변경 (TGOODSTB CUD)
  └── Tr_TGOODS_T01_Service.processTrigger()
        ├── [매장 상품 동기화] MGOODSTB Upsert / Delete
        │     └── Tr_MGOODS_T01_Service.processTrigger()
        │           ├── TSUBMNTB (서브메뉴) 연쇄 CUD
        │           ├── TMCPLKTB (컵링크) 연쇄 CUD
        │           ├── TMSSRCTB (바코드) 연쇄 CUD
        │           └── TKTFDCTB (티켓요율) 연쇄 CUD
        └── [재고 데이터 연쇄 정리 - Delete 시]
              ├── IMCRIOTB (현재고현황 테이블) 연쇄 삭제
              ├── IMDDIOTB (일수불 테이블) 연쇄 삭제
              └── IMMMIOTB (월수불 테이블) 연쇄 삭제
```
