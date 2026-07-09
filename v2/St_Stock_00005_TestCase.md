# St_Stock_00005 — 매장 전수실사 등록 단위 테스트케이스

> **화면**: [ST] 재고관리 > 전수실사 등록  
> **URL Prefix**: `POST /backoffice/data/st/stock/st_stock_00005`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 조회/CUD = `@RequestBody` / 엑셀업로드 = `multipart/form-data`
> **DB 트리거 영향도**: MMEMBVTB, TPRICETB, IMREALTB, TGOODSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## ⚠️ 서비스 핵심 버그

```java
// addGoodsTempList() 서비스 내 maxLine 이중 증가 ★★★
if(surveyGoodsCnt > 0) {
    saveTempRealGoods(map);    // 기존 상품 수정
} else {
    addGoodsTempList(map);     // 새 상품 추가
    maxLine++;                 // 1. 새 상품 시 maxLine++
}
maxLine++;                     // 2. 루프마다 무조건 maxLine++ → 기존 상품도 maxLine 증가 → lineNo 간격 발생 ★★★
```

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | getTempRealList, getFormDownGoodsList, goodsSelect, tempRealExcelUpload, confirmTempRealList, addGoodsTempList, createTempRealGoods, print |
| `chainMsNo` | `NC0001` | tempRealExcelUpload, addGoodsTempList, createTempRealGoods |
| `msNo` | `MS001` | 전체 |
| `ID` | `I000449s` | tempRealExcelUpload, saveTempRealGoods, deleteTempRealGoods, confirmTempRealList, addGoodsTempList, createTempRealGoods |

---

## 엔드포인트 목록 (9개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getTempRealList` | 전수실사 내역 조회 (페이징 주석처리) | `@RequestBody` | `Map` (total+rows) | SELECT | IMDDIOTB<br>IMMMIOTB<br>MNAMEMTB<br>TGOODSTB<br>TPRICETB |
| 2 | `/getFormDownGoodsList` | 양식 다운로드용 상품 조회 | `@RequestBody` | `List` | SELECT | IMDDIOTB |
| 3 | `/goodsSelect` | 상품 추가 모달 조회 (페이징 있음) | `@RequestBody` | `Map` (total+rows) | SELECT | IMDDIOTB<br>IMMMIOTB<br>IMRETPTB<br>MMEMBVTB<br>MNAMEMTB<br>TGOODSTB<br>TPRICETB |
| 4 | `/tempRealExcelUpload` | 엑셀 업로드 (기존삭제→채번→업로드) | `multipart/form-data` | `void` | INSERT | IMDDIOTB<br>IMMMIOTB<br>IMRETPTB<br>MMEMBVTB<br>TGOODSTB<br>TPRICETB |
| 5 | `/saveTempRealGoods` | 실사 수량 저장 (ArrayList JSON) | `@RequestBody` | `void` | UPDATE | IMRETPTB |
|6|`/deleteTempRealGoods`|실사 상품 삭제 (ArrayList JSON)|`@RequestBody`|`void`|DELETE| 공통 모듈/동적 쿼리 (추적 불가) |
| 7 | `/confirmTempRealList` | 실사 확정 (IMTRLG 존재 시 예외) | `@RequestBody` | `void` | UPDATE | IMRETPTB |
| 8 | `/addGoodsTempList` | 실사 상품 추가 (lineNo 이중증가 버그) | `@RequestBody` | `void` | INSERT | IMDDIOTB<br>IMMMIOTB<br>IMRETPTB<br>MMEMBVTB<br>TGOODSTB<br>TPRICETB |
| 9 | `/createTempRealGoods` | 전수실사 일괄 생성 (기존삭제→채번→생성) | `@RequestBody` | `void` | INSERT | IMDDIOTB<br>IMMMIOTB<br>IMRETPTB<br>MMEMBVTB<br>TGOODSTB<br>TPRICETB |
| 10 | `/print` | 전수실사 인쇄 (surveyDate substring) | `@RequestBody` | `ModelAndView` | SELECT | IMDDIOTB<br>IMMMIOTB<br>MMEMBVTB<br>MNAMEMTB<br>TGOODSTB<br>TPRICETB |

---

## 1. `/getTempRealList` — 전수실사 내역 조회

**특이사항**: 페이징(`startCount`/`endCount`) 주석 처리 → **전체 조회** ★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001`, msNo=`MS001` | `{"surveyDate":"20260526"}` | 해당 날짜 전수실사 내역 (priceFg 조회 후 필터) |
| 1-2 | (동일) | `{}` | 전체 조회 (날짜 필터 없음) |
| 1-3 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 2. `/getFormDownGoodsList` — 양식 다운로드용 상품 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001`, msNo=`MS001` | `{}` | 전체 상품 |
| 2-2 | (동일) | `{"exceptAllColumns":true}` | 컬럼 제외 조건 반영 |

---

## 3. `/goodsSelect` — 상품 추가 모달 조회

**★ offset 미전달**: `(int)map.get("offset")` → **ClassCastException 또는 NPE** ★★★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001`, msNo=`MS001` | `{"offset":0,"limit":10,"surveyDate":"20260526"}` | 상품 목록 + total |
| 3-2 | (동일) | `{}` (offset 없음) | `(int)map.get("offset")` → **NPE** ★★★ |
| 3-3 | (동일) | `{"offset":"abc","limit":10}` | `(int)"abc"` → **ClassCastException** ★★ |

---

## 4. `/tempRealExcelUpload` — 엑셀 업로드

**처리 흐름**:
```
deleteTempRealList()       → 기존 내역 전체 삭제
getNewSurveySeq()          → SEQ 채번
surveySeq = surveyDate + "WT" + surveySeq
tempRealExcelUpload(file)  → 엑셀 파싱 후 row별 INSERT
```
**★ non-multipart 요청**: `(MultipartHttpServletRequest)req` → **ClassCastException** ★★

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 4-1 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | `surveyDate=20260526` + xlsx 파일 | 기존삭제→채번→업로드 → void |
| 4-2 | (동일) | `surveyDate=20260526` + 파일 없음 | iterator.hasNext()=false → list 비어있음 → INSERT 없음 |
| 4-3 | (동일) | `Content-Type: application/json` | **ClassCastException** ★★ |
| 4-4 | - | `surveyDate` 없음 | 400 (@NotBlank) |
| 4-5 | - | `surveyDate=` (빈 문자열) | 400 (@NotBlank) |

---

## 5. `/saveTempRealGoods` — 실사 수량 저장

**서비스**: `@RequestBody` JSON → goodsCdArr/surveyQtyArr → `ArrayList<String>` 캐스팅  
**★ surveyQtyArr 길이 < goodsCdArr.size()**: `surveyQtyArr.get(i)` → **IndexOutOfBoundsException** ★★★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | msNo=`MS001`, ID=`I000449s` | `{"surveySeq":"20260526WT001","goodsCdArr":["G001"],"surveyQtyArr":["10"]}` | void |
| 5-2 | (동일) | goodsCdArr 2개, surveyQtyArr 1개 | **IndexOutOfBoundsException** ★★★ |
| 5-3 | (동일) | `{"surveySeq":"20260526WT001","goodsCdArr":null}` | `goodsCdArr=null` → `null.size()` → **NPE** ★★★ |

---

## 6. `/deleteTempRealGoods` — 실사 상품 삭제

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 6-1 | msNo=`MS001`, ID=`I000449s` | `{"surveySeq":"20260526WT001","goodsCdArr":["G001"]}` | void |
| 6-2 | (동일) | `{"goodsCdArr":null}` | **NPE** ★★★ |

---

## 7. `/confirmTempRealList` — 실사 확정

**서비스 처리**:
```
confirmTempRealList()         → 임시 데이터 확정
getImtrlgCnt() > 0           → throw new Exception("IMTRLG DATA EXIST!!")
getChainMsNo()               → chainMsNo 조회
getMsEnvInfo()               → priceFg 조회
getSurveyIdx()               → idx 채번
insertImrealtb()             → 실사 마스터 INSERT
confirmRealList()            → 실사 데이터 최종 확정
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 7-1 | chainNo=`C001`, msNo=`MS001`, ID=`I000449s` | `{"surveySeq":"20260526WT001"}` | void (6단계 처리) |
| 7-2 | (동일) | IMTRLG 데이터 있는 날짜 | `throw new Exception("IMTRLG DATA EXIST!!")` → 500 ★ |
| 7-3 | (동일) | `{}` (surveySeq 없음) | surveySeq=null → Mapper 처리 |

---

## 8. `/addGoodsTempList` — 실사 상품 추가

**lineNo 이중 증가 버그**:
```java
if(surveyGoodsCnt > 0) {
    saveTempRealGoods(map);  // 기존 존재 → 업데이트
} else {
    addGoodsTempList(map);
    maxLine++;               // 신규 → +1
}
maxLine++;                   // 항상 +1 → 기존 상품도 증가 ★★★
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 8-1 | 세션 전체 | `{"surveyDate":"20260526","goodsCdArr":["G001"],"surveyQtyArr":["5"]}` | lineNo 정상 채번 (신규) |
| 8-2 | (동일) | goodsCdArr 3개 (1개 기존+2개 신규) | lineNo 간격 발생 (기존에도 maxLine++) ★★★ |
| 8-3 | (동일) | `{"goodsCdArr":null}` | **NPE** ★★★ |

---

## 9. `/createTempRealGoods` — 일괄 생성

**`createTempRealGoods()` 서비스**: `maxLine-1` 로 lineNo 산정 → 초기 maxLine=0이면 `-1` 형태 `"-001"` 가능 ★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 9-1 | 세션 전체 | `{"surveyDate":"20260526"}` | 기존삭제→채번→일괄INSERT → void |
| 9-2 | (동일) | `{}` (surveyDate 없음) | `map.get("surveyDate")` → null → surveySeq = "null"+"WT"+SEQ ★★ |

---

## 10. `/print` — 인쇄

**★ surveyDate null**: `map.get("surveyDate").toString()` → **NPE** ★★★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 10-1 | chainNo=`C001`, msNo=`MS001` | `{"surveyDate":"20260526"}` | ModelAndView (year=2026, month=05) |
| 10-2 | (동일) | `{}` (surveyDate 없음) | `null.toString()` → **NPE** ★★★ |
| 10-3 | (동일) | `{"surveyDate":"2026"}` (4자 미만) | `substring(4,6)` → **StringIndexOutOfBoundsException** ★★★ |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/stock/st_stock_00005"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 전수실사 내역 조회
Invoke-RestMethod -Uri "$base/getTempRealList" -Method POST -Headers $h -WebSession $session `
  -Body '{"surveyDate":"20260526"}'

# 3-2. offset 없음 → NPE
Invoke-RestMethod -Uri "$base/goodsSelect" -Method POST -Headers $h -WebSession $session `
  -Body '{"surveyDate":"20260526"}'
# 예상: 500 NPE

# 5-2. 배열 길이 불일치 → IndexOutOfBounds
Invoke-RestMethod -Uri "$base/saveTempRealGoods" -Method POST -Headers $h -WebSession $session `
  -Body '{"surveySeq":"20260526WT001","goodsCdArr":["G001","G002"],"surveyQtyArr":["10"]}'
# 예상: 500

# 10-2. surveyDate 없음 → NPE
Invoke-RestMethod -Uri "$base/print" -Method POST -Headers $h -WebSession $session `
  -Body '{}'
# 예상: 500 NPE

# 10-3. surveyDate 4자 → StringIndexOutOfBounds
Invoke-RestMethod -Uri "$base/print" -Method POST -Headers $h -WebSession $session `
  -Body '{"surveyDate":"2026"}'
# 예상: 500
```

---

## 주요 검증 포인트

```
□ goodsSelect — offset 미전달 → (int)map.get("offset") → NPE ★★★
□ print — surveyDate null → null.toString() → NPE ★★★
□ print — surveyDate 8자 미만 → substring(4,6) → StringIndexOutOfBoundsException ★★★
□ tempRealExcelUpload — non-multipart 요청 → ClassCastException ★★
□ saveTempRealGoods/deleteTempRealGoods — goodsCdArr null → NPE ★★★
□ saveTempRealGoods — surveyQtyArr 길이 < goodsCdArr.size() → IndexOutOfBoundsException ★★★
□ addGoodsTempList — maxLine 이중 증가 → lineNo 간격 발생 ★★★
□ createTempRealGoods — maxLine=0 초기 시 maxLine-1 → 음수 lineNo "-001" 가능 ★
□ confirmTempRealList — IMTRLG 존재 시 Exception throw → @Transactional rollback
□ createTempRealGoods — surveyDate null → "null"+"WT"+SEQ 형태 surveySeq ★★
□ @Transactional rollbackFor Exception — confirmTempRealList 6단계 원자성 보장
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅ (10/10)

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/search` | ✅ SELECT (소스 66번) |
| `/goodsSearch` | ✅ SELECT (소스 111번) |
| `/addGoodsSearch` | ✅ SELECT (소스 144번) |
| `/tempRealExcelUpload` | ✅ INSERT (소스 192번) |
| `/saveTempRealGoods` | ✅ UPDATE (소스 241번) |
| `/deleteTempRealGoods` | ✅ DELETE (소스 271번) |
| `/confirmTempReal` | ✅ UPDATE (소스 300번) |
| `/addTempRealGoods` | ✅ INSERT (소스 330번) |
| `/createTempRealGoods` | ✅ INSERT (소스 364번) |
| `/printSearch` | ✅ SELECT (소스 403번) |

**`@Validated` 클래스 레벨 적용** ✅ (소스 46번) — TC 전체 정확 ✅


## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] IMREALTB (CUD 작업)
│   └── (Trigger) Tr_IMREAL_T01
├── [테이블] MMEMBVTB (CUD 작업)
│   └── (Trigger) Tr_MMEMBV_T01
├── [테이블] TGOODSTB (CUD 작업)
│   └── (Trigger) Tr_TGOODS_T01
└── [테이블] TPRICETB (CUD 작업)
    └── (Trigger) Tr_TPRICE_T01
```
