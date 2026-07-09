# St_Sales_00012 — 매장 영업월보 단위 테스트케이스

> **화면**: [ST] 영업관리 > 영업월보  
> **URL Prefix**: `POST /backoffice/data/st/sales/st_sales_00012`  
> **Hq_Sales_00012(본사 영업월보) 대비 차이점**:
> - `msNo`: 세션에서 자동 획득 (RequestBody 불필요)  
> - `/excelDownload`: `excelMsNo` 파라미터 **없음** — 세션 msNo 사용  
> - `/search`: `@ServiceLog` 없음 (감사 로그 미기록) ★
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 |
|---------|---------|
| `chainNo` | `C001` |
| `msNo` | `MS001` |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 영업월보 7개 섹션 조회 (`@ServiceLog` 없음) | `@RequestBody` | `Map` (7개 리스트) | SELECT | MCARDMTB<br>SDAILYTB<br>SGOODSTB<br>SMTIMETB<br>STRNCDTB<br>STRNHDTB |
| 2 | `/excelDownload` | 영업월보 엑셀 (msNo 세션, excelMsNo 없음) | `@RequestParam` (2개 필수) | `void` | SELECT | MCARDMTB<br>SDAILYTB<br>SGOODSTB<br>SMTIMETB<br>STRNCDTB<br>STRNHDTB |

---

## 1. `/search` — 영업월보 조회

**★ Hq 대비**: msNo가 세션에서 자동 주입 → RequestBody에 msNo 없어도 정상 동작  
**★ @ServiceLog 없음**: 감사 로그(ServiceLog) 미기록 — 보안 감사 누락 ★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001`, msNo=`MS001` | `{"searchFromDate":"20260501","searchEndDate":"20260531"}` | 7개 리스트 Map |
| 1-2 | (동일) | `{}` | 날짜 null → 전체 또는 빈 목록 |
| 1-3 | - | (Body 없음) | 400 |

---

## 2. `/excelDownload` — 엑셀 다운로드

**★ Hq_Sales_00012 대비**: `excelMsNo` 파라미터 없음 → 세션 msNo 사용  
**필수 파라미터**: `excelSearchFromDate`, `excelSearchEndDate` (2개)

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | chainNo=`C001`, msNo=`MS001` | `excelSearchFromDate=20260501&excelSearchEndDate=20260531` | xlsx 다운로드 |
| 2-2 | - | `excelSearchFromDate` 없음 | 400 (@NotBlank) |
| 2-3 | - | `excelSearchEndDate` 없음 | 400 (@NotBlank) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/sales/st_sales_00012"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 월보 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchEndDate":"20260531"}'

# 2-1. 엑셀 다운로드
Invoke-WebRequest -Uri "$base/excelDownload" -Method POST -ContentType $f -WebSession $session `
  -Body "excelSearchFromDate=20260501&excelSearchEndDate=20260531" `
  -OutFile "C:\Temp\st_sales_00012.xlsx"

# 2-2. excelSearchFromDate 없음
Invoke-RestMethod -Uri "$base/excelDownload" -Method POST -ContentType $f -WebSession $session `
  -Body "excelSearchEndDate=20260531"
```

---

## Hq vs St 비교표

| 항목 | Hq_Sales_00012 | St_Sales_00012 |
|------|---------------|---------------|
| msNo 획득 | RequestBody | 세션 자동 |
| excelMsNo 파라미터 | 필수 (@NotBlank) | 없음 (세션 사용) |
| @ServiceLog(/search) | 있음 | **없음** ★ |
| 감사 로그 | 기록됨 | **미기록** ★ |

---

## 주요 검증 포인트

```
□ /search @ServiceLog 없음 → 감사 로그 미기록 ★
□ excelDownload — msNo 세션에서 획득 → excelMsNo 파라미터 불필요 (Hq와 차이)
□ saleEtcList, salePurList 주석 처리 → 응답 미포함 확인
□ 서비스 인스턴스 변수 동시성 위험 (서비스 코드 별도 확인 필요)
□ @NotBlank(excelSearchFromDate, excelSearchEndDate) — 빈 문자열 → 400
```

---

