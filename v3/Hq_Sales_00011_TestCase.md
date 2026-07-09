# Hq_Sales_00011 — 본사 영업일보 단위 테스트케이스

> **화면**: [HQ] 영업관리 > 영업일보  
> **URL Prefix**: `POST /backoffice/data/hq/sales/hq_sales_00011`  
> **@Transactional**: 선언만 있음 (`rollbackFor` 미지정 → **RuntimeException만 rollback**) ★  
> **요청 방식 혼용**: `/search` = `@RequestBody` / `/excelDownload` = `@RequestParam`
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## ⚠️ 서비스 핵심 이슈

```java
// 서비스 인스턴스 변수 — @Service 싱글톤 공유 위험 ★★★
XSSFWorkbook workbook;  // 인스턴스 변수
CellStyle cellStyle;    // 인스턴스 변수
int rowCnt;             // 인스턴스 변수 → 동시 요청 시 데이터 오염

// excelHeaderTimeMaker — 헤더 문자열 오류 (석식 라벨이 중식으로 잘못됨)
headerCell.setCellValue("중식(10:00 ~ 16:59");  // 석식(17:00~) 이어야 함 ★
```

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 |
|---------|---------|
| `chainNo` | `C001` |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 영업일보 7개 섹션 일괄 조회 | `@RequestBody` | `Map` (7개 리스트) | SELECT | MCARDMTB<br>SDAILYTB<br>SGOODSTB<br>SMTIMETB<br>STRNCDTB<br>STRNHDTB |
| 2 | `/excelDownload` | 영업일보 엑셀 다운로드 (7섹션 시트) | `@RequestParam` | `void` (response stream) | SELECT | MCARDMTB<br>SDAILYTB<br>SGOODSTB<br>SMTIMETB<br>STRNCDTB<br>STRNHDTB |

---

## 1. `/search` — 영업일보 조회

**7개 Mapper 호출**: getToDaySaleList, getToDaySaleSumList, getToDaySaleDcList, getToDaySaleGoodsClassList, getToDaySaleTimeList, getToDaySaleKindList, getToDaySaleCardList  
**주석 처리된 항목**: getSaleEtcList, getSalePurList → 응답에 포함 안 됨 (확인 필요)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"searchDate":"20260526","msNo":"MS001"}` | 7개 리스트 포함 Map |
| 1-2 | (동일) | `{"searchDate":"20260526"}` (msNo 없음) | msNo=null → 전체 매장 조회 가능 |
| 1-3 | (동일) | `{}` (searchDate 없음) | searchDate=null → 전체 또는 빈 목록 |
| 1-4 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 2. `/excelDownload` — 엑셀 다운로드

**서비스 처리**:
```
getListExcel() 내:
  rowCnt = 0 (인스턴스 변수 초기화) → 동시 요청 시 rowCnt 오염 ★★★
  7개 섹션 헤더+데이터 순차 기입
  excelHeaderTimeMaker — 석식 헤더 "중식(10:00~16:59" 로 잘못 표기 ★
  workbook.write(response.getOutputStream())
  workbook.close()
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | chainNo=`C001` | `excelSearchDate=20260526&excelMsNo=MS001` | xlsx 파일 다운로드 (7섹션) |
| 2-2 | (동일) | `excelSearchDate=20260526&excelMsNo=MS001` 동시 2개 요청 | rowCnt 인스턴스 변수 오염 → 행 위치 오류 ★★★ |
| 2-3 | (동일) | 석식 헤더 라벨 확인 | `"중식(10:00 ~ 16:59"` (실제 석식 라벨이어야 함) ★ |
| 2-4 | - | `excelSearchDate` 없음 | 400 (@NotBlank) |
| 2-5 | - | `excelMsNo` 없음 | 400 (@NotBlank) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/sales/hq_sales_00011"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 영업일보 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchDate":"20260526","msNo":"MS001"}'

# 2-1. 엑셀 다운로드
Invoke-WebRequest -Uri "$base/excelDownload" -Method POST -ContentType $f -WebSession $session `
  -Body "excelSearchDate=20260526&excelMsNo=MS001" `
  -OutFile "C:\Temp\hq_sales_00011.xlsx"

# 2-4. excelSearchDate 없음 → 400
Invoke-RestMethod -Uri "$base/excelDownload" -Method POST -ContentType $f -WebSession $session `
  -Body "excelMsNo=MS001"

# 동시 요청 → rowCnt 오염 테스트
$job1 = Start-Job { Invoke-WebRequest -Uri "http://localhost:18080/backoffice/data/hq/sales/hq_sales_00011/excelDownload" -Method POST -ContentType "application/x-www-form-urlencoded" -Body "excelSearchDate=20260526&excelMsNo=MS001" -OutFile "C:\Temp\excel1.xlsx" }
$job2 = Start-Job { Invoke-WebRequest -Uri "http://localhost:18080/backoffice/data/hq/sales/hq_sales_00011/excelDownload" -Method POST -ContentType "application/x-www-form-urlencoded" -Body "excelSearchDate=20260526&excelMsNo=MS002" -OutFile "C:\Temp\excel2.xlsx" }
Wait-Job $job1, $job2
```

---

## 주요 검증 포인트

```
□ @Transactional rollbackFor 미지정 → RuntimeException만 rollback, Checked Exception 미rollback ★
□ rowCnt 인스턴스 변수 — 동시 요청 시 행 위치 오염 → 잘못된 xlsx 생성 ★★★
□ cellStyle 인스턴스 변수 — 동시 요청 시 스타일 오염 ★★★
□ excelHeaderTimeMaker — 석식 헤더 라벨 "중식(10:00~16:59" 오표기 ★
□ search — 주석된 saleEtcList, salePurList 응답 미포함 확인
□ excelDownload — workbook.close() 정상 호출 → OOM 방지 확인
□ @NotBlank(excelSearchDate, excelMsNo) — 빈 문자열 → 400
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

**소스 98~102번**: `getSaleEtcList`, `getSalePurList` 주석 처리 확정 → 응답 Map에 미포함 (TC 1-4 항목 확인 ✅)

**소스 133번**: `XSSFWorkbook workbook = hq_Sales_00011_Service.getListExcel(commandMap)` — 컨트롤러는 **로컬 변수**로 수신  
→ 컨트롤러 레벨 인스턴스 변수 오염 없음 ✅  
→ 서비스(`getListExcel`) 내부의 `rowCnt`, `cellStyle`, `workbook` 인스턴스 변수가 오염 원인 (TC 정확 ✅)

**소스 144~145번**: `workbook.write()` 후 `workbook.close()` 호출 ✅ — 정상 종료 (OOM 방지)

**소스 123~124번**: `required=true` + `@NotBlank` → 빈값·미전송 모두 400 ✅ (TC 2-4, 2-5 정확)
