# St_Sales_00004 — 매장 기간평균 매출현황 단위 테스트케이스

> **화면**: [ST] 매출분석 > 일/월/시간 > 기간평균 매출현황  
> **URL Prefix**: `POST /backoffice/data/st/sales/st_sales_00004`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 전부 `@RequestBody` JSON 통신  
> **DB 트리거 영향도**: 본 화면은 순수 조회(SELECT) 화면으로 자체 로직 내에서는 CUD가 발생하지 않습니다.

---

## ⚠️ 서비스 핵심 소스 분석 및 잠재적 버그

### 1. 요일별 집계 시 요일 추출 포맷 검증 리스크 (★★)
* **소스 분석 (`St_Sales_00004_Sql.xml` L18~24)**:
  * `selectAvgSaleList` 쿼리는 요일별 매출 집계를 위해 `TO_CHAR(TO_DATE(A.SALE_DATE, 'YYYYMMDD'), 'D')` 결과가 1(일) ~ 7(토)인지 체크하여 합산합니다.
  * **결과**: PostgreSQL 이기종 전환 시 `TO_CHAR`의 `'D'` 반환값은 로케일 설정에 영향을 받을 수 있으며, 표준 `EXTRACT(DOW FROM ...)` (0 = 일요일)로 리팩토링할 경우 요일 매핑 정합성을 신중히 확인해야 합니다.

### 2. 차트 조회 시 Oracle 외부 조인 `(+)` 문법 잔재 (★★★)
* **소스 분석 (`St_Sales_00004_Sql.xml` L55~58)**:
  * `selectDateChartData` 쿼리 내에 `A.CHAIN_NO (+) = #{chainNo}`, `A.SALE_DATE (+) = B.CAL_DATE` 등 Oracle 고유의 외부 조인 표기법이 대거 사용되고 있습니다.
  * **결과**: EDB Postgres 호환 기능 외에 표준 PostgreSQL 환경 마이그레이션 시 즉각 구문 에러를 발생시키며 작동이 중단됩니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | selectAvgSaleList, selectChartData |
| `msNo` | `NC0007` | selectAvgSaleList, selectChartData |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | @ServiceLog 선언 현황 | 관련 테이블 |
|---|---|---|---|---|---|---|---|
| 1 | `/selectAvgSaleList` | 기간평균 매출 목록 조회 | `@RequestBody` | `List` | SELECT | ✅ SELECT (컨트롤러 L56) | SDAILYTB, MMEMBSTB |
| 2 | `/selectChartData` | 요일별 전체 순매출 차트 데이터 조회 | `@RequestBody` | `Map` | SELECT | ⚠️ 누락 (컨트롤러 L81 - 호출 로그 검토 필요) | SDAILYTB, TCALENTB |

---

## 1. `/selectAvgSaleList` — 기간평균 매출 목록 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 1-1 | 정상 조건 조회 | 세션 소속 가맹점에 기간 내 매출(SDAILYTB) 존재 | `{"searchFromDate":"20260401","searchEndDate":"20260630"}` | - 가맹점 기준 일자별 요일 평균 매출액 반환.<br>- 렌더링을 위한 DTO 리스트가 반환됨. |
| 1-2 | 매출 데이터 없음 | 기간 내 매출 데이터 부재 | `{"searchFromDate":"20200101","searchEndDate":"20200101"}` | - 빈 리스트 `[]` 반환.<br>- 그리드 내 '조회된 데이터가 없습니다.' 메세지 출력. |

---

## 2. `/selectChartData` — 요일별 전체 순매출 차트 데이터 조회

| No | 파라미터 분기 및 조건 | DB 선행 상태 | RequestBody (JSON) | 예상 결과 (Expectation) |
|----|--------------------|------------|---------------------|----------------------|
| 2-1 | 정상 차트 조회 | 캘린더 마스터(TCALENTB) 정보 및 매출 존재 | `{"searchFromDate":"20260401","searchEndDate":"20260630"}` | - 요일명(DAY_NAME), 요일코드(DAY_CD)별 집계된 순매출 반환.<br>- Chart01에 바인딩 가능한 맵 리스트 리턴. |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=H000051cafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/sales/st_sales_00004"
$h = @{"Content-Type"="application/json"}

# 1-1. 기간평균 매출 목록 조회
Invoke-RestMethod -Uri "$base/selectAvgSaleList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"2026-04-01","searchEndDate":"2026-06-30"}'

# 2-1. 차트 데이터 조회
Invoke-RestMethod -Uri "$base/selectChartData" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"2026-04-01","searchEndDate":"2026-06-30"}'
```

---

## 주요 검증 포인트

```
□ selectAvgSaleList — 세션 msNo, chainNo가 SQL Mapper 조건으로 정상 주입 및 바인딩되는지 여부
□ selectChartData — TCALENTB 조인 시 Oracle 외부조인(+) 적용에 따른 EDB 쿼리 실행 안정성
□ selectAvgSaleList — DECODE/ROUND 함수를 사용한 요일별 매출 합산 및 일평균순매출 계산식 정합성
```

---

## 🔍 프론트엔드(JSP/JS) - 백엔드 파라미터 교차 분석

### 1. 일자 지정 유효성 체크
* **프론트엔드 구현 (`st_sales_00004.js` L24-27)**:
  ```javascript
  if($("#searchFromDate").val() == "" || $("#searchEndDate").val() == ""){
      bootbox.alert('조회일자를 입력해 주십시오.');
      return false;
  }
  ```
* **교차 분석**: 프론트엔드 단에서 일자가 유실되거나 공백 상태로 요청이 나가는 시나리오를 사전에 차단하도록 Validation이 완벽하게 구현되어 있습니다. 이에 따라 서버 런타임에서의 날짜 포맷 파싱 에러 리스크는 매우 낮습니다.
