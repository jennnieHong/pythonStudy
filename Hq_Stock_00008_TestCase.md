# Hq_Stock_00008 — 본사 폐기현황 조회 단위 테스트케이스

> **화면**: [HQ] 재고 > 조정폐기관리 > 폐기현황  
> **URL Prefix**: `POST /backoffice/data/hq/stock/hq_stock_00008`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않아 **실제 트리거가 직접 기동하지는 않습니다.** 다만, 가맹점 폐기등록([st_stock_00003](file:///D:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/stock/st_stock_00003/st_stock_00003.jsp))에서 [IMDUSETB](file:///D:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/stock/Hq_Stock_00008_Sql.xml#L33) 테이블의 폐기 전표가 확정될 때 `Tr_IMDUSE_T01_Service` 가동을 통해 수불 대장(`IMTRLGTB`)이 생성되고, 재고 반영 배치(`DmIMTR01`)가 수행되어 원장이 갱신된 내역이 최종 조회 대상이 됩니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | /search, /searchDetail |
| `ID` | `shopadmin` (샵 본사 관리자) | 공통 세션 및 권한 체크 |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 본사 폐기현황 요약 목록 조회 | `@RequestBody` | `List<Hq_Stock_00008_SelectListDto>` | SELECT | IMDUSETB<br>TGOODSTB<br>MMEMBSTB<br>MNAMEMTB |
| 2 | `/searchDetail` | 본사 폐기현황 상세내역 조회 | `@RequestBody` | `List<Hq_Stock_00008_SelectListDetailDto>` | SELECT | IMDUSETB<br>TGOODSTB<br>MUSERSTB<br>MPRICETB |

---

## 1. `/search` — 본사 폐기현황 요약 조회

**특이사항**:
* `selectGijun` 파라미터 값에 따라 요약 집계 기준이 다르게 바인딩됩니다.
  - `selectGijun = "D"` (일자별): `DISUSE_DATE`를 기준으로 날짜 포맷(`YYYY-MM-DD`)을 출력합니다.
  - `selectGijun = "R"` (사유별): 공통코드 `902`를 조회하여 폐기사유 한글명(`NM_REP`)을 출력합니다.
* 특정 매장을 지정할 경우 `msNo` 조건을 추가합니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 1-1 | chainNo=`C001` | 확정 상태(`PROC_FG='1'`)의 폐기 데이터 존재 | `{"fromDate":"20260601","toDate":"20260610","selectGijun":"D","msNo":"","reasonCd":""}` | 날짜별로 그룹화된 건수(`SUM_CNT`), 총수량(`SUM_QTY`), 총금액(`SUM_COST`) 리스트 반환 |
| 1-2 | chainNo=`C001` | 확정 상태(`PROC_FG='1'`)의 폐기 데이터 존재 | `{"fromDate":"20260601","toDate":"20260610","selectGijun":"R","msNo":"","reasonCd":""}` | 폐기사유별로 그룹화된 요약 리스트 반환 (공통코드 `902` 바인딩 검증) |
| 1-3 | chainNo=`C001` | 특정 매장 폐기 데이터 존재 | `{"fromDate":"20260601","toDate":"20260610","selectGijun":"D","msNo":"NC0007"}` | `NC0007` 매장의 폐기 건만 필터링되어 반환 |
| 1-4 | chainNo=`C001` | 상품 정보 존재 | `{"fromDate":"20260601","toDate":"20260610","selectGijun":"D","goodsCd":"T0000291"}` | 특정 상품코드로 필터링된 폐기 요약 정보 반환 |
| 1-5 | chainNo=`C001` | 상품 정보 존재 | `{"fromDate":"20260601","toDate":"20260610","selectGijun":"D","goodsNm":"포니"}` | 상품명 LIKE 검색 조건이 적용되어 필터링된 결과 반환 |

---

## 2. `/searchDetail` — 본사 폐기현황 상세내역 조회

**특이사항**:
* 요약 그리드에서 클릭한 로우의 고유 키값(`TITLE_CD`)이 `paramDate`로 전달되어 해당 날짜 또는 사유에 맞는 상세 데이터를 가져옵니다.
* 마진율 계산을 위해 해당 가맹점의 판매가 테이블(`MPRICETB`) 또는 체인 마스터 가격 테이블(`TPRICETB`)에서 실시간으로 `PRICE_FG = '0'` 조건의 가격을 서브쿼리로 매칭합니다. (가격이 없을 경우 0 처리 및 마진 0% 계산)

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 2-1 | chainNo=`C001` | 일자 기준 폐기 데이터 존재 | `{"msNo":"NC0007","searchFromDate":"20260601","searchToDate":"20260610","selectGijun":"D","paramDate":"20260605"}` | `2026-06-05`에 폐기된 상세 내역 목록(상품명, 매입가, 판매가, 마진율 등) 반환 |
| 2-2 | chainNo=`C001` | 사유 기준 폐기 데이터 존재 | `{"msNo":"NC0007","searchFromDate":"20260601","searchToDate":"20260610","selectGijun":"R","paramDate":"내부미팅"}` | 해당 폐기사유에 매핑되는 상세 폐기 건 반환 |
| 2-3 | chainNo=`C001` | 판매 단가 미등록 상태 (PRICE_FG='0' 없음) | `{"msNo":"NC0007","searchFromDate":"20260601","searchToDate":"20260610","selectGijun":"D","paramDate":"20260605"}` | 판매가 `0`, 마진율 `0%`, 매가금액 `0`으로 정상 반환 (서브쿼리 `NULL` 방어 처리 확인) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/stock/hq_stock_00008"
$h = @{"Content-Type"="application/json"}

# 1-1. 일자별 요약 조회 (전체 매장)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"fromDate":"20260601","toDate":"20260610","selectGijun":"D","msNo":"","reasonCd":"","setFg":"","lClass":"","mClass":"","sClass":"","tBarcode":"","goodsCd":"","goodsNm":""}'

# 1-2. 사유별 요약 조회 (전체 매장)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"fromDate":"20260601","toDate":"20260610","selectGijun":"R","msNo":"","reasonCd":"","setFg":"","lClass":"","mClass":"","sClass":"","tBarcode":"","goodsCd":"","goodsNm":""}'

# 2-1. 일자별 상세 내역 조회 (NC0007 매장의 2026-06-05일 폐기 내역)
Invoke-RestMethod -Uri "$base/searchDetail" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"NC0007","searchFromDate":"20260601","searchToDate":"20260610","selectGijun":"D","paramDate":"20260605","reasonCd":"","setFg":"","lClass":"","mClass":"","sClass":"","tBarcode":"","goodsCd":"","goodsNm":""}'
```

---

## 주요 검증 포인트

* **[Dynamic Query] 기준값 분기**: `selectGijun` 값에 따라 요약 목록의 기준값(`TITLE_NM`, `TITLE_CD`)이 동적으로 일자 혹은 사유 한글명으로 변환 바인딩되는지 검증.
* **[Realtime Price] 실시간 단가 서브쿼리**: 상세 그리드의 판매가(`UPRICE`)는 조회 시점의 `MPRICETB` (또는 체인 마스터 `TPRICETB`)의 `PRICE_FG = '0'` 조건 기준 유효 판매 단가를 실시간 조회하여 계산되는지 검증.
* **[Security] 본사 체인 격리**: 세션의 `chainNo`가 쿼리에 강제 주입되어 타 체인(예: F&B) 본사 데이터 및 타 소속 점포 데이터가 노출되지 않는지 권한 격리 확인.
* **[Division by Zero] 나눗셈 0 방어**: 단가 데이터가 등록되지 않았을 때 SQL 중첩 `DECODE`에 의해 마진율 계산 중 `Division by Zero` 에러가 터지지 않고 정상 조회되는지 확인.
