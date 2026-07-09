# Hq_Master_00008 — 본사 바코드 관리 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > 상품관리 > 바코드 관리  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00008/`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: `/search` = `@RequestBody` / `/barcodePrint` = `@RequestParam` 배열
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, barcodePrint |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 바코드 상품 목록 조회 (페이징) | `@RequestBody` | `Map` (total+rows) | SELECT | TMSSRCTB<br>TPRICETB |
| 2 | `/barcodePrint` | 바코드 출력 (배열 루프 → ModelAndView) | `@RequestParam` 배열 | `ModelAndView` | SELECT | TMSSRCTB<br>TPRICETB |

---

## 1. `/search` — 상품 조회

**★ offset 미전달**: `(int)map.get("offset")` → **NPE/ClassCastException** ★★★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"offset":0,"limit":10}` | 전체 상품 목록 + total |
| 1-2 | (동일) | `{"offset":0,"limit":10,"selectGoodsNm":"커피"}` | 상품명 필터 |
| 1-3 | (동일) | `{"offset":0,"limit":10,"goodsUseYn":"Y"}` | 사용여부 필터 |
| 1-4 | (동일) | `{}` (offset 없음) | `(int)map.get("offset")` → **NPE** ★★★ |
| 1-5 | (동일) | `{"offset":"abc","limit":10}` | `(int)"abc"` → **ClassCastException** ★★ |
| 1-6 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 2. `/barcodePrint` — 바코드 출력

**서비스 핵심 로직**:
```java
for(int i = 0; i < barcodeArr.length; i++) {
    for(int j = 0; j < Integer.parseInt(printCntArr[i]); j++) {
        // goodsNm 14자 초과 시 substring(0,14) 분리
        // goodsNm 28자 초과 시 substring(14,28)
        // uprice: Integer.parseInt(upriceArr[i]) → 숫자 아니면 NumberFormatException ★★
        // printCntArr[i]: 숫자 아니면 NumberFormatException ★★
    }
}
// ★ 배열 길이 불일치: printCntArr.length < barcodeArr.length → ArrayIndexOutOfBoundsException ★★★
// ★ upriceArr.length < barcodeArr.length → ArrayIndexOutOfBoundsException ★★★
// ★ goodsNmArr.length < barcodeArr.length → ArrayIndexOutOfBoundsException ★★★
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | chainNo=`C001` | `goodsCdArr[]=G001&goodsNmArr[]=커피라떼&upriceArr[]=4500&barcodeArr[]=880000001234&printCntArr[]=2` | ModelAndView (barcodeList 2개) |
| 2-2 | (동일) | goodsNm 14자 이하 | goodsNm2=null |
| 2-3 | (동일) | goodsNm 15~28자 | goodsNm=14자, goodsNm2=나머지 |
| 2-4 | (동일) | goodsNm 29자 이상 | goodsNm=14자, goodsNm2=substring(14,28) |
| 2-5 | (동일) | `barcodeArr[]` 2개, `printCntArr[]` 1개 | `printCntArr[1]` → **ArrayIndexOutOfBoundsException** ★★★ |
| 2-6 | (동일) | `upriceArr[]` 2개, `barcodeArr[]` 3개 | `upriceArr[2]` → **ArrayIndexOutOfBoundsException** ★★★ |
| 2-7 | (동일) | `upriceArr[]=abc` (문자) | `Integer.parseInt("abc")` → **NumberFormatException** ★★ |
| 2-8 | (동일) | `printCntArr[]=0` | 내부 j 루프 0회 → returnList에 항목 없음 |
| 2-9 | (동일) | `printCntArr[]=-1` | `Integer.parseInt("-1")` 가능 → j<-1 → 루프 미실행 |
| 2-10 | - | `goodsCdArr[]` 없음 | 400 (required=true) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00008"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 상품 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'

# 1-4. offset 없음 → NPE
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{}'
# 예상: 500 NPE

# 2-1. 바코드 출력 (정상)
Invoke-RestMethod -Uri "$base/barcodePrint" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCdArr[]=G001&goodsNmArr[]=커피라떼&upriceArr[]=4500&barcodeArr[]=880000001234&printCntArr[]=2"

# 2-5. 배열 길이 불일치 → ArrayIndexOutOfBounds
Invoke-RestMethod -Uri "$base/barcodePrint" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCdArr[]=G001&goodsCdArr[]=G002&goodsNmArr[]=커피라떼&goodsNmArr[]=아메리카노&upriceArr[]=4500&upriceArr[]=3500&barcodeArr[]=8800001&barcodeArr[]=8800002&printCntArr[]=2"
# 예상: 500 ArrayIndexOutOfBoundsException (printCntArr[1] 없음)

# 2-7. uprice 문자 → NumberFormatException
Invoke-RestMethod -Uri "$base/barcodePrint" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCdArr[]=G001&goodsNmArr[]=커피&upriceArr[]=abc&barcodeArr[]=8800001&printCntArr[]=1"
# 예상: 500 NumberFormatException
```

---

## 주요 검증 포인트

```
□ search — offset 미전달 → (int)map.get("offset") → NPE ★★★
□ barcodePrint — printCntArr/upriceArr/goodsNmArr 길이 < barcodeArr.length → ArrayIndexOutOfBoundsException ★★★
□ barcodePrint — Integer.parseInt(upriceArr[i]) 숫자 아님 → NumberFormatException ★★
□ barcodePrint — Integer.parseInt(printCntArr[i]) 숫자 아님 → NumberFormatException ★★
□ barcodePrint — goodsNm substring 경계값 (14자, 28자) 정상 분리 확인
□ barcodePrint — printCntArr[]=0 → returnList 항목 없음 (빈 바코드 출력 페이지)
□ @Transactional rollbackFor Exception 적용 (SELECT만 있어 실질 rollback 대상 없음)
□ URL Prefix 끝에 `/` 포함 — `/backoffice/data/hq/master/hq_master_00008/` → 요청 경로 슬래시 주의
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/search` | ✅ SELECT |
| `/barcodePrint` | ✅ SELECT |

### 소스 확인 사항

**소스 41번**: `@RequestMapping(value="/backoffice/data/hq/master/hq_master_00008/")` — 끝 슬래시 포함  
**소스 58번**: `@RequestMapping(value="search")` — 슬래시 없음  
→ 실제 경로: `/hq_master_00008/search` (TC 정확 ✅)

**소스 74번**: `(int)map.get("offset")` — `offset` 키 없으면 null → unboxing → **NPE** (TC 1-4 ✅)

**소스 103~107번**: `goodsCdArr[]`, `goodsNmArr[]`, `upriceArr[]`, `barcodeArr[]`, `printCntArr[]` 모두 `required=true`  
→ 하나라도 없으면 **400** (TC 2-10 ✅)

**소스 119번**: 배열 처리 로직은 **서비스**에서 실행 — 컨트롤러는 배열을 그대로 commandMap에 담아 전달  
→ ArrayIndexOutOfBoundsException, NumberFormatException은 **서비스 계층**에서 발생 (TC 정확 ✅)
