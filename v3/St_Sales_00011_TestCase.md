# St_Sales_00011 — 영업 일보 단위 테스트케이스

> **화면**: [ST] 영업관리 > 영업 일보  
> **URL Prefix**: `POST /backoffice/data/st/sales/st_sales_00011`  
> **@Transactional**: `@Transactional` (rollbackFor 미지정 — 기본값 RuntimeException만)  
> **요청 방식**: `/search` = `@RequestBody` / `/excelDownload` = `@RequestParam`
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## ⚠️ 중요 서비스 설계 결함

```java
// @Service 싱글톤 빈에 인스턴스 변수 선언 ★★★
XSSFWorkbook workbook;   // 동시 요청 시 공유됨
CellStyle cellStyle;     // 동시 요청 시 공유됨
int rowCnt;              // 동시 요청 시 공유됨 → 행 위치 오염
```
→ 동시 Excel 다운로드 요청 시 **rowCnt 값 오염** → 잘못된 행에 데이터 기록 ★★★

**추가 버그**: `excelHeaderTimeMaker` 내 셀(8) 헤더 값이 "석식" 아닌 **"중식(10:00 ~ 16:59"** 로 중복 기재 ★

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, excelDownload |
| `msNo` | `MS001` | search, excelDownload |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 영업일보 7개 목록 조회 (당일/누적/할인/분류/시간대/종류/카드) | `@RequestBody` | `Map` | SELECT | MCARDMTB<br>SDAILYTB<br>SGOODSTB<br>SMTIMETB<br>STRNCDTB<br>STRNHDTB |
| 2 | `/excelDownload` | 영업일보 Excel 다운로드 (7섹션 시트) | `@RequestParam` | `void` (xlsx 스트림) | SELECT | MCARDMTB<br>SDAILYTB<br>SGOODSTB<br>SMTIMETB<br>STRNCDTB<br>STRNHDTB |

---

## 1. `/search` — 영업일보 조회

**7개 쿼리 순차 실행**:
```
getToDaySaleList()          → 당일매출
getToDaySaleSumList()       → 누적매출
getToDaySaleDcList()        → 할인매출
getToDaySaleGoodsClassList()→ 상품분류별 매출
getToDaySaleTimeList()      → 시간대별 매출
getToDaySaleKindList()      → 매출종류(VAT포함)
getToDaySaleCardList()      → 신용카드
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001`, msNo=`MS001` | `{"searchDate":"20260526"}` | 7개 리스트 포함 Map |
| 1-2 | chainNo=`C001`, msNo=`MS001` | `{}` (searchDate 없음) | `reqMap.get("searchDate")=null` → Mapper SQL null 처리 (당일 또는 오류) |
| 1-3 | chainNo=`C001`, msNo=`MS001` | `{"searchDate":"99991299"}` (미래 날짜) | 7개 리스트 빈 목록 반환 |
| 1-4 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 2. `/excelDownload` — Excel 다운로드

**서비스 처리 흐름**:
```
rowCnt = 0  (★ 인스턴스 변수 공유 위험)
createSheet("일별보고")
헤더1: 조회일자 매출 → excelList1 (8컬럼)
헤더2: 누적 매출    → excelList2 (8컬럼)
헤더3: 할인 매출   → excelList3 (7컬럼)
헤더4: 매출종류    → excelList4 (3컬럼) + 합계행
헤더5: 신용카드    → excelList5 (4컬럼) + 합계행
헤더6: 상품분류별  → excelList6 (6컬럼) + 합계행
헤더7: 시간대별   → excelList7 (12컬럼)

★ excelHeaderTimeMaker 셀(8): "중식(10:00 ~ 16:59" 로 오기재 (석식 헤더여야 함)
★ rowCnt @Service 인스턴스변수 → 동시요청 시 행 오염
★ workbook close(): getOutputStream() → flush 보장 필요
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | chainNo=`C001`, msNo=`MS001` | `excelSearchDate=20260526` | xlsx 파일 다운로드 (7섹션) |
| 2-2 | chainNo=`C001`, msNo=`MS001` | `excelSearchDate=20260526` (동시 2요청) | rowCnt 공유 → 행 오염 → 데이터 겹침 ★★★ |
| 2-3 | chainNo=`C001`, msNo=`MS001` | `excelSearchDate=99991299` | 전 섹션 데이터 0건 → 헤더만 있는 xlsx |
| 2-4 | - | `excelSearchDate` 없음 | 400 (@NotBlank) |
| 2-5 | chainNo=`C001`, msNo=`MS001` | `excelSearchDate=` (빈 문자열) | 400 (@NotBlank) |
| 2-6 | chainNo=`C001`, msNo=`MS001` | `excelSearchDate=20260526` | 다운로드 파일명 확인: `excelDownload_yyyyMMddHHmmss.xlsx` |

---

## Excel 섹션별 컬럼 검증

| 섹션 | 헤더 배열 | 컬럼 수 | 비고 |
|------|---------|---------|-----|
| 조회일자 매출 | 총매출,할인액,순매출,NET매출,영수건수,영수단가,고객수,객단가 | 8 | |
| 누적 매출 | (동일) | 8 | |
| 할인 매출 | 통합쿠폰,임직원,프로모션,제휴할인,부서비,현금잔전,전체DC | 7 | |
| 매출종류(VAT) | 구분,건수,금액 | 3 | 합계행 포함 |
| 신용카드 | 구분,POS승인금액,임의등록금액,합계금액 | 4 | 합계행 포함 |
| 상품분류별 | 대분류,중분류,총건수,총매출액,순매출액,부가세 | 6 | 합계행 포함 |
| 시간대별 | 조식(0열)/중식(4열)/석식헤더오기재(8열) 각 4컬럼 | 12 | ★ 헤더 버그 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/sales/st_sales_00011"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 영업일보 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchDate":"20260526"}'

# 1-2. searchDate 없음
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{}'

# 2-1. 엑셀 다운로드
Invoke-WebRequest -Uri "$base/excelDownload" -Method POST -ContentType $f -WebSession $session `
  -Body "excelSearchDate=20260526" -OutFile "C:\Temp\sales_report.xlsx"
Write-Host "다운로드 완료"

# 2-4. excelSearchDate 없음 → 400
Invoke-RestMethod -Uri "$base/excelDownload" -Method POST -ContentType $f -WebSession $session `
  -Body ""
# 예상: 400

# 2-2. 동시 요청 (rowCnt 공유 테스트)
1..3 | ForEach-Object {
    Start-Job {
        $s = New-Object Microsoft.PowerShell.Commands.WebRequestSession
        Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
          -Method POST -Body "username=I000449s&password=pass01!A" `
          -ContentType "application/x-www-form-urlencoded" -SessionVariable s | Out-Null
        Invoke-WebRequest -Uri "http://localhost:18080/backoffice/data/st/sales/st_sales_00011/excelDownload" `
          -Method POST -ContentType "application/x-www-form-urlencoded" -WebSession $s `
          -Body "excelSearchDate=20260526" -OutFile "C:\Temp\sales_$_.xlsx"
    }
}
Get-Job | Wait-Job
# 결과: 3개 파일 rowCnt 오염 여부 확인
```

---

## 주요 검증 포인트

```
□ @Service 인스턴스변수 rowCnt/cellStyle/workbook → 동시요청 데이터 오염 ★★★ (최우선 수정)
□ excelHeaderTimeMaker — 셀(8) 헤더 "중식(10:00 ~ 16:59" → "석식(17:00 ~ 23:59"로 수정 필요 ★
□ @Transactional 기본값 — rollbackFor 미지정 → RuntimeException만 rollback
□ excelDownload — workbook.close() 후 getOutputStream() flush → 브라우저 수신 완전성 확인
□ searchDate null → Mapper SQL 처리 방식 확인 (SYSDATE 기본값 또는 전체 조회)
□ search — 7개 쿼리 독립 실행 → 일부 쿼리 실패 시 나머지 결과 정상 반환 여부
□ @NotBlank — excelSearchDate 빈 문자열 → 400
```

---

