# Hq_Sales_00004 — 본사 기간평균 매출현황 단위 테스트케이스

> **화면**: [HQ] 매출분석 > 일/월/시간 > 기간평균 매출현황  
> **URL Prefix**: `POST /backoffice/data/hq/sales/hq_sales_00004`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않습니다.

---

## ⚠️ 서비스 핵심 소스 분석 및 잠재적 버그

### 1. 요일별 집계 시 요일 추출 포맷 검증 리스크 (★★)
* **소스 분석 (`Hq_Sales_00004_Sql.xml` L18~24)**:
  * `selectAvgSaleList` 쿼리는 요일별 매출 집계를 위해 `TO_CHAR(TO_DATE(A.SALE_DATE, 'YYYYMMDD'), 'D')` 결과가 1(일) ~ 7(토)인지 체크하여 합산합니다.
  * **결과**: PostgreSQL 이기종 전환 시 요일 코드 추출 로케일 설정 및 `EXTRACT(DOW FROM ...)` (0 = 일요일)로 리팩토링할 경우의 정합성을 점검해야 합니다.

### 2. 차트 조회 시 Oracle 외부 조인 `(+)` 문법 잔재 (★★★)
* **소스 분석 (`Hq_Sales_00004_Sql.xml` L62~69)**:
  * `selectDateChartData` 쿼리 내에 `A.CHAIN_NO (+) = #{chainNo}`, `A.SALE_DATE (+) = B.CAL_DATE`, `A.MS_NO (+) IN ...` 등 Oracle 고유의 외부 조인 표기법이 다수 잔존하고 있습니다.
  * **결과**: EDB Postgres 호환 기능 외에 표준 PostgreSQL 환경 마이그레이션 시 즉각 구문 에러를 발생시키며 작동이 중단됩니다.

### 3. 매출 순위 산정 시 ROWNUM 조건 호환성 (★★)
* **소스 분석 (`Hq_Sales_00004_Sql.xml` L108)**:
  * `selectRankChartData` 쿼리는 상위 5개 가맹점 매출 순위 조회를 위해 인라인뷰 바깥에서 `WHERE ROWNUM <= 5` 조건을 사용하고 있습니다.
  * **결과**: PostgreSQL 환경에서는 ROWNUM을 사용할 수 없으므로 문법 에러가 발생하며, `LIMIT 5` 표준 문법으로의 변경이 요구됩니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | selectAvgSaleList, selectChartData |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | @ServiceLog 선언 현황 | 관련 테이블 |
|---|---|---|---|---|---|---|---|
| 1 | `/selectAvgSaleList` | 본사 소속 매장별 기간평균 매출 목록 조회 | `@RequestBody` | `List` | SELECT | ✅ SELECT (컨트롤러 L56) | SDAILYTB, MMEMBSTB |
| 2 | `/selectChartData` | 요일별 및 매장별 순위 차트 데이터 조회 | `@RequestBody` | `Map` | SELECT | ⚠️ 누락 (컨트롤러 L78 - 호출 로그 검토 필요) | SDAILYTB, TCALENTB, MMEMBSTB |

---

## 1. `/selectAvgSaleList` — 기간평균 매출 목록 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 1-1 | 전체 매장 조회 (msNoArr 누락) | 본사 산하 매장에 매출 정보(SDAILYTB) 존재 | `{"searchFromDate":"20260401","searchEndDate":"20260630"}` | - 본사 권한 전체 매장들의 일자별 요일 평균 매출액 반환.<br>- 렌더링을 위한 DTO 리스트가 반환됨. |
| 1-2 | 특정 매장 필터 조회 (`msNoArr = ["NC0007"]`) | NC0007 매장 전표 존재 | `{"searchFromDate":"20260401","searchEndDate":"20260630","msNoArr":["NC0007"]}` | - `msNoArr` 리스트 내의 매장 코드 조건만 IN 절로 동적 쿼리에 결합되어 조회. |
| 1-3 | 매출 데이터 없음 | 기간 내 매출 데이터 부재 | `{"searchFromDate":"20200101","searchEndDate":"20200101"}` | - 빈 리스트 `[]` 반환. |

---

## 2. `/selectChartData` — 요일별 및 매장별 순위 차트 데이터 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 2-1 | 전체 차트 데이터 조회 | 캘린더 마스터 정보 및 매출 존재 | `{"searchFromDate":"20260401","searchEndDate":"20260630"}` | - `dateChartData` (요일별 순매출) 및 `rankChartData` (매장별 매출 순위 TOP 5) 정보가 담긴 단일 Map 객체 반환. |
| 2-2 | 특정 매장 필터 차트 조회 | NC0007 매장 매출 존재 | `{"searchFromDate":"20260401","searchEndDate":"20260630","msNoArr":["NC0007"]}` | - 선택된 매장에 대해서만 차트 데이터 집계 결과가 포함되어 반환. |
| 2-3 | 매출 데이터 없음 | 기간 내 매출 데이터 부재 | `{"searchFromDate":"20200101","searchEndDate":"20200101"}` | - 요일별 합계가 0이고 순위 목록이 비어있는 차트 데이터 반환. |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/sales/hq_sales_00004"
$h = @{"Content-Type"="application/json"}

# 1-1. 기간평균 매출 목록 조회 (전체)
Invoke-RestMethod -Uri "$base/selectAvgSaleList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"2026-04-01","searchEndDate":"2026-06-30"}'

# 1-2. 특정 매장 필터 조회
Invoke-RestMethod -Uri "$base/selectAvgSaleList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"2026-04-01","searchEndDate":"2026-06-30","msNoArr":["NC0007"]}'

# 2-1. 요일 및 순위 차트 데이터 조회
Invoke-RestMethod -Uri "$base/selectChartData" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"2026-04-01","searchEndDate":"2026-06-30"}'
```

---

## 주요 검증 포인트

```
□ selectAvgSaleList — 세션 chainNo가 동적 가맹점 목록 조건에 정상 바인딩되는지 여부
□ selectChartData — TCALENTB 조인 시 Oracle 외부조인(+) 적용에 따른 EDB 쿼리 실행 안정성
□ selectRankChartData — 가맹점 매출 합계 계산 및 ROWNUM <= 5 필터에 따른 정상 출력 검증
```

---

## 🔍 프론트엔드(JSP/JS) - 백엔드 파라미터 교차 분석

### 1. 일자 지정 유효성 체크
* **프론트엔드 구현 (`hq_sales_00004.js` L24-27)**:
  ```javascript
  if($("#searchFromDate").val() == "" || $("#searchEndDate").val() == ""){
      bootbox.alert('조회일자를 입력해 주십시오.');
      return false;
  }
  ```
* **교차 분석**: 프론트엔드 단에서 일자가 유실되거나 공백 상태로 요청이 나가는 시나리오를 사전에 차단하도록 Validation이 완벽하게 구현되어 있습니다. 이에 따라 서버 런타임에서의 날짜 포맷 파싱 에러 리스크는 매우 낮습니다.
