# Hq_Sales_00012 — 본사 영업월보 단위 테스트케이스

> **화면**: [HQ] 영업관리 > 영업월보  
> **URL Prefix**: `POST /backoffice/data/hq/sales/hq_sales_00012`  
> **@Transactional**: Hq_Sales_00011_Service와 동일 구조 (rollbackFor 미지정 가능성 확인 필요)  
> **Hq_Sales_00011(영업일보) 대비 차이점**:
> - 조회 파라미터: `searchDate` (1개) → `searchFromDate` + `searchEndDate` (범위 조회)  
> - 엑셀 파라미터: `excelSearchDate` → `excelSearchFromDate` + `excelSearchEndDate` (2개 필수)  
> - msNo: RequestBody에서 받음 (St와 달리 세션에서 안 받음)
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 |
|---------|---------|
| `chainNo` | `C001` |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 영업월보 7개 섹션 일괄 조회 | `@RequestBody` | `Map` (7개 리스트) | SELECT | MCARDMTB<br>SDAILYTB<br>SGOODSTB<br>SMTIMETB<br>STRNCDTB<br>STRNHDTB |
| 2 | `/excelDownload` | 영업월보 엑셀 다운로드 | `@RequestParam` (3개 필수) | `void` | SELECT | MCARDMTB<br>SDAILYTB<br>SGOODSTB<br>SMTIMETB<br>STRNCDTB<br>STRNHDTB |

---

## 1. `/search` — 영업월보 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"searchFromDate":"20260501","searchEndDate":"20260531","msNo":"MS001"}` | 7개 리스트 Map |
| 1-2 | (동일) | `{"searchFromDate":"20260501","searchEndDate":"20260531"}` (msNo 없음) | msNo=null → 전체 매장 |
| 1-3 | (동일) | `{}` | 날짜 null → 전체 또는 빈 목록 |
| 1-4 | - | (Body 없음) | 400 |

---

## 2. `/excelDownload` — 엑셀 다운로드

**Hq_Sales_00011 대비 차이**: `excelMsNo` 별도 파라미터 필요 (Hq_Sales_00011은 `excelMsNo` 필수, 00012도 동일)  
**서비스 인스턴스 변수 동시성 위험** (00011과 동일 패턴 확인 필요)

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | chainNo=`C001` | `excelSearchFromDate=20260501&excelSearchEndDate=20260531&excelMsNo=MS001` | xlsx 다운로드 |
| 2-2 | - | `excelSearchFromDate` 없음 | 400 (@NotBlank) |
| 2-3 | - | `excelSearchEndDate` 없음 | 400 (@NotBlank) |
| 2-4 | - | `excelMsNo` 없음 | 400 (@NotBlank) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/sales/hq_sales_00012"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 월보 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchEndDate":"20260531","msNo":"MS001"}'

# 2-1. 엑셀 다운로드
Invoke-WebRequest -Uri "$base/excelDownload" -Method POST -ContentType $f -WebSession $session `
  -Body "excelSearchFromDate=20260501&excelSearchEndDate=20260531&excelMsNo=MS001" `
  -OutFile "C:\Temp\hq_sales_00012.xlsx"

# 2-2. excelSearchFromDate 없음
Invoke-RestMethod -Uri "$base/excelDownload" -Method POST -ContentType $f -WebSession $session `
  -Body "excelSearchEndDate=20260531&excelMsNo=MS001"
```

---

## 주요 검증 포인트

```
□ search — msNo 없음(null) → 전체 매장 조회 여부 확인
□ excelDownload — 3개 @NotBlank 파라미터 모두 필수
□ 서비스 인스턴스 변수 rowCnt/cellStyle 동시성 위험 (00011과 동일 패턴 여부 서비스 코드 확인)
□ saleEtcList, salePurList 주석 처리 → 응답 미포함 확인
□ 엑셀 석식 헤더 오표기 여부 (00011과 동일 서비스 공유 시)
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/search` | ✅ SELECT |
| `/excelDownload` | ✅ SELECT |

### 소스 확인 사항

**소스 45번**: `@Validated` ✅ 클래스 레벨 정상 적용

**소스 99~103번**: `getSaleEtcList`, `getSalePurList` 주석 처리 확정 → 응답 Map에 미포함 (TC 90번 ✅ 정확)

**소스 124~126번**: 엑셀 파라미터 3개 모두 `required=true` + `@NotBlank` → 하나라도 없으면 **400** (TC 2-2~2-4 ✅ 정확)

**서비스 분리**: `Hq_Sales_00012_Service` — 00011 서비스와 **별도 클래스** (소스 41번)  
→ 인스턴스 변수 오염은 00012 서비스 내부를 별도 확인 필요 ★

**소스 147~148번**: `workbook.write()` → `workbook.close()` ✅ OOM 방지 정상

**00011 vs 00012 파라미터 차이 확정**:

| 항목 | 00011 (일보) | 00012 (월보) |
|------|------------|------------|
| search | `searchDate` (단일) | `searchFromDate` + `searchEndDate` |
| excel | `excelSearchDate` (1개) | `excelSearchFromDate` + `excelSearchEndDate` (2개) |
| msNo | 필수 @NotBlank | 필수 @NotBlank |
