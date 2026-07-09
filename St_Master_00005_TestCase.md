# St_Master_00005 — 매장 바코드 관리 단위 테스트케이스

> **화면**: [ST] 마스터관리 > 상품관리 > 바코드 관리  
> **URL Prefix**: `POST /backoffice/data/st/master/st_master_00005`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: `/search` = `@RequestBody` / `/barcodePrint` = `@RequestParam` 배열
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `msNo` | `MS001` | search, barcodePrint |
| `chainNo` | `C001` | search, barcodePrint |

---

## 엔드포인트 목록 (2개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 상품 목록 조회 (바코드 관리용, 페이징) | `@RequestBody` | `Map` (total+rows) | SELECT | MMSSRCTB<br>MPRICETB |
|2|`/barcodePrint`|바코드 출력 (상품명 절단, 가격 포맷, 인쇄 수량 반복)|`@RequestParam` 배열|`ModelAndView`|SELECT| 공통 모듈/동적 쿼리 (추적 불가) |

---

## 1. `/search` — 상품 목록 조회

**★ offset 미전달**: `(int)map.get("offset")` → **NPE** ★★★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | msNo=`MS001`, chainNo=`C001` | `{"offset":0,"limit":10}` | 전체 상품 목록 (페이징) |
| 1-2 | msNo=`MS001`, chainNo=`C001` | `{"com_goodsClass_main_l_select":"L01","offset":0,"limit":10}` | 대분류 필터 |
| 1-3 | msNo=`MS001`, chainNo=`C001` | `{"selectGoodsNm":"커피","offset":0,"limit":10}` | 상품명 검색 |
| 1-4 | msNo=`MS001`, chainNo=`C001` | `{"inputBarcode":"8801234","offset":0,"limit":10}` | 바코드 검색 |
| 1-5 | msNo=`MS001`, chainNo=`C001` | `{"goodsUseYn":"Y","offset":0,"limit":10}` | 사용 여부 필터 |
| 1-6 | msNo=`MS001`, chainNo=`C001` | `{}` (offset 없음) | `(int)map.get("offset")` → **NPE** ★★★ |

---

## 2. `/barcodePrint` — 바코드 출력

**서비스 핵심 로직**:
```java
for(int i = 0; i < barcodeArr.length; i++) {
    for(int j = 0; j < Integer.parseInt(printCntArr[i]); j++) {

        // 상품명 절단 로직
        if(goodsNmArr[i].length() > 14) {
            map.put("goodsNm",  goodsNmArr[i].substring(0, 14));
            if(goodsNmArr[i].length() > 28)
                map.put("goodsNm2", goodsNmArr[i].substring(14, 28));
            else
                map.put("goodsNm2", goodsNmArr[i].substring(14, len));
        } else {
            map.put("goodsNm",  goodsNmArr[i]);
            map.put("goodsNm2", null);
        }

        // 가격 포맷: "₩ 1,500"
        map.put("uprice", Currency.getInstance(Locale.KOREA).getSymbol()
                          + " " + formatter.format(Integer.parseInt(upriceArr[i])));
        // upriceArr[i] 숫자 아니면 NumberFormatException ★
        // printCntArr[i] 숫자 아니면 NumberFormatException ★

        map.put("barcode", barcodeArr[i]);
    }
}

★ barcodeArr/goodsNmArr/upriceArr/printCntArr 길이 불일치 시
  → goodsNmArr[i] 또는 upriceArr[i] → ArrayIndexOutOfBoundsException ★★★
```

**특이사항**: `@RestController`임에도 `ModelAndView` 반환 → 브라우저 직접 확인 필요

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 2-1 | chainNo=`C001`, msNo=`MS001` | `goodsCdArr[]=G001&goodsNmArr[]=커피&upriceArr[]=3000&barcodeArr[]=8801234&printCntArr[]=1` | 1장 바코드 스티커 출력 |
| 2-2 | chainNo=`C001`, msNo=`MS001` | `printCntArr[]=3` | 동일 바코드 3장 출력 (inner loop 3회) |
| 2-3 | chainNo=`C001`, msNo=`MS001` | 2개 상품 선택 (배열 2개) | 각각 인쇄 수량만큼 반복 |
| 2-4 | chainNo=`C001`, msNo=`MS001` | `goodsNmArr[]=가나다라마바사아자차카타파하` (14자) | goodsNm=14자, goodsNm2=null |
| 2-5 | chainNo=`C001`, msNo=`MS001` | `goodsNmArr[]=가나다라마바사아자차카타파하ABCD` (16자) | goodsNm=14자, goodsNm2=2자 |
| 2-6 | chainNo=`C001`, msNo=`MS001` | `goodsNmArr[]=` + 29자 이상 | goodsNm=14자, goodsNm2=substring(14,28)=14자 (초과분 절단) |
| 2-7 | chainNo=`C001`, msNo=`MS001` | `upriceArr[]=abc` | `Integer.parseInt("abc")` → **NumberFormatException** ★★ |
| 2-8 | chainNo=`C001`, msNo=`MS001` | `printCntArr[]=0` | 내부 루프 0회 → 바코드 미출력 |
| 2-9 | chainNo=`C001`, msNo=`MS001` | `printCntArr[]=abc` | `Integer.parseInt("abc")` → **NumberFormatException** ★★ |
| 2-10 | - | 배열 길이 불일치 (`goodsNmArr` 1개, `barcodeArr` 2개) | `goodsNmArr[1]` → **ArrayIndexOutOfBoundsException** ★★★ |
| 2-11 | - | `goodsCdArr[]` 없음 | 400 (required=true) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/master/st_master_00005"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 상품 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'

# 1-6. offset 없음 → NPE
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{}'
# 예상: 500 NullPointerException

# 2-1. 바코드 출력 (1장)
Invoke-RestMethod -Uri "$base/barcodePrint" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCdArr[]=G001&goodsNmArr[]=커피&upriceArr[]=3000&barcodeArr[]=8801234&printCntArr[]=1"
# 예상: ModelAndView → 브라우저 확인 필요

# 2-7. 가격 숫자 오류
Invoke-RestMethod -Uri "$base/barcodePrint" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCdArr[]=G001&goodsNmArr[]=커피&upriceArr[]=abc&barcodeArr[]=8801234&printCntArr[]=1"
# 예상: 500 NumberFormatException

# 2-10. 배열 길이 불일치
Invoke-RestMethod -Uri "$base/barcodePrint" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCdArr[]=G001&goodsCdArr[]=G002&goodsNmArr[]=커피&upriceArr[]=3000&barcodeArr[]=8801234&barcodeArr[]=8801235&printCntArr[]=1&printCntArr[]=1"
# 예상: 500 ArrayIndexOutOfBoundsException (goodsNmArr 1개뿐)
```

---

## 주요 검증 포인트

```
□ search — offset 미전달 → (int)map.get("offset") NPE ★★★
□ barcodePrint — upriceArr/printCntArr 숫자 아닌 값 → NumberFormatException ★★
□ barcodePrint — 5개 배열 길이 불일치 → ArrayIndexOutOfBoundsException ★★★
□ barcodePrint — printCntArr="0" → 내부 루프 0회 → 해당 상품 바코드 미출력
□ barcodePrint — goodsNmArr 14자 초과/28자 초과 절단 로직 정상 여부 확인
□ barcodePrint — @RestController ModelAndView 반환 → REST 클라이언트 테스트 불가
□ barcodePrint — 다수 상품 × 다수 인쇄 시 returnList 크기 = sum(printCntArr[i]) 확인
□ @Validated 있음 — required=true 배열 미전달 시 400
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/search` | ✅ SELECT (소스 57번) |
| `/barcodePrint` | ✅ SELECT (소스 100번) |

**`@Validated` 클래스 레벨 적용** ✅ (소스 40번)

**TC 전체 정확** ✅ — barcodePrint printCntArr ArrayIndexOutOfBounds, ModelAndView REST 반환 불가, goodsNmArr 배열 길이 불일치 등 소스 확인됨
