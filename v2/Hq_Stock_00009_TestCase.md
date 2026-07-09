# Hq_Stock_00009 — 전수실사 등록 단위 테스트케이스

> **화면**: [HQ] 재고관리 > 조정/폐기/실사 > 전수실사 등록  
> **URL Prefix**: `POST /backoffice/data/hq/stock/hq_stock_00009`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 대부분 `@RequestBody` / `tempRealExcelUpload` = Multipart + `@RequestParam`
> **DB 트리거 영향도**: MMEMBVTB, TPRICETB, IMREALTB, TGOODSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | getTempRealList, getFormDownGoodsList, goodsSelect, confirmTempRealList, addGoodsTempList, createTempRealGoods, print |
| `chainMsNo` | `NC0001` | tempRealExcelUpload, addGoodsTempList, createTempRealGoods |
| `ID` | `7249525SHOP` | saveTempRealGoods, deleteTempRealGoods, confirmTempRealList, addGoodsTempList, createTempRealGoods |

---

## 엔드포인트 목록 (9개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getTempRealList` | 전수실사 내역 조회 (priceFg 분기) | `@RequestBody` | `Map` (total+rows) | SELECT | IMDDIOTB<br>IMMMIOTB<br>MNAMEMTB<br>TGOODSTB<br>TPRICETB |
| 2 | `/getFormDownGoodsList` | 양식 다운로드용 상품 조회 | `@RequestBody` | `List` | SELECT | IMDDIOTB |
| 3 | `/goodsSelect` | 상품 추가 모달 조회 (페이징+priceFg 분기) | `@RequestBody` | `Map` (total+rows) | SELECT | IMDDIOTB<br>IMMMIOTB<br>IMRETPTB<br>MMEMBVTB<br>MNAMEMTB<br>TGOODSTB<br>TPRICETB |
| 4 | `/tempRealExcelUpload` | 엑셀 업로드 (기존삭제→채번→insert) | Multipart + `@RequestParam` | `void` | INSERT | IMDDIOTB<br>IMMMIOTB<br>IMRETPTB<br>MMEMBVTB<br>TGOODSTB<br>TPRICETB |
| 5 | `/saveTempRealGoods` | 실사 수량 저장 (ArrayList 순회) | `@RequestBody` | `void` | UPDATE | IMRETPTB |
|6|`/deleteTempRealGoods`|실사 상품 삭제 (ArrayList 순회)|`@RequestBody`|`void`|DELETE| 공통 모듈/동적 쿼리 (추적 불가) |
| 7 | `/confirmTempRealList` | 실사 확정 (7단계 처리) | `@RequestBody` | `void` | UPDATE | IMRETPTB |
| 8 | `/addGoodsTempList` | 실사 상품 추가 (존재 여부 분기 insert/update) | `@RequestBody` | `void` | INSERT | IMDDIOTB<br>IMMMIOTB<br>IMRETPTB<br>MMEMBVTB<br>TGOODSTB<br>TPRICETB |
| 9 | `/createTempRealGoods` | 전수실사 상품 일괄 생성 (기존삭제→채번→insert) | `@RequestBody` | `void` | INSERT | IMDDIOTB<br>IMMMIOTB<br>IMRETPTB<br>MMEMBVTB<br>TGOODSTB<br>TPRICETB |
| 10 | `/print` | 실사 내역 출력 (ModelAndView) | `@RequestBody` | `ModelAndView` | SELECT | IMDDIOTB<br>IMMMIOTB<br>MMEMBSTB<br>MMEMBVTB<br>MNAMEMTB<br>TGOODSTB<br>TPRICETB |

---

## 1. `/getTempRealList` — 전수실사 내역 조회

**priceFg 분기 로직**:
```
chainMsNo = getChainMsNo(commandMap)     ← DB 조회
msEnvInfo = getMsEnvInfo(commandMap)     ← DB 조회

if(map.get("msNo").equals(chainMsNo))    ← map.get("msNo") null 위험
    priceFg = msEnvInfo.get("UCOST_FG")
else
    priceFg = msEnvInfo.get("USUPRICE_FG")

★ 주석 처리: startCount/endCount (페이징 없음)
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainNo=`C001` | 실사 데이터 존재 | `{"msNo":"MS001","surveyDate":"20260522"}` | `{"total":N,"rows":[...]}`, priceFg=UCOST_FG (본부매장) |
| 1-2 | chainNo=`C001` | - | `{"msNo":"MS002","surveyDate":"20260522"}` (비본부 매장) | priceFg=USUPRICE_FG |
| 1-3 | chainNo=`C001` | - | `{"msNo":"MS001","surveyDate":"20260522","lclassCd":"L01","curQtyCheck":"Y"}` | 분류+재고수량 필터 |
| 1-4 | chainNo=`C001` | msEnvInfo 없음 | `{"msNo":"MS001","surveyDate":"20260522"}` | `msEnvInfo.get("UCOST_FG")` → null → priceFg=null ★ |
| 1-5 | chainNo=`C001` | - | `{}` (msNo 없음) | `map.get("msNo").equals(chainMsNo)` → **NPE** ★★★ |
| 1-6 | chainNo=`C001` | 데이터 없음 | 유효 파라미터 | `{"total":0,"rows":[]}` |

---

## 2. `/getFormDownGoodsList` — 양식 다운로드용 상품 조회

**파라미터**: lclassCd/mclassCd/sclassCd/goodsCd/goodsNm/exceptAllColumns 모두 `null` 방어 없이 `map.get()` 직접

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"msNo":"MS001"}` | 전체 상품 리스트 |
| 2-2 | chainNo=`C001` | `{"msNo":"MS001","goodsNm":"커피","exceptAllColumns":"Y"}` | 이름+전체컬럼 제외 필터 |
| 2-3 | chainNo=`C001` | `{}` (msNo 없음) | msNo=null → Mapper SQL 처리 확인 |

---

## 3. `/goodsSelect` — 상품 추가 모달 조회 (페이징)

**페이징**: `(int)map.get("offset") + 1` → offset 미전달 시 **ClassCastException** ★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"msNo":"MS001","surveyDate":"20260522","offset":0,"limit":10}` | `{"total":N,"rows":[...]}` |
| 3-2 | chainNo=`C001` | `{}` (offset 없음) | `(int)map.get("offset")` → **NPE/ClassCastException** ★★★ |
| 3-3 | chainNo=`C001` | `{"msNo":"MS001","surveyDate":"20260522","offset":0,"limit":10}` (priceFg 분기) | msNo=chainMsNo → UCOST_FG, 아니면 USUPRICE_FG |

---

## 4. `/tempRealExcelUpload` — 엑셀 업로드

**처리 순서**:
```
1. deleteTempRealList(commandMap)       ← 기존 내역 전체 삭제
2. getNewSurveySeq(commandMap)          ← 신규 seq 채번
3. commandMap.put("surveySeq", surveyDate+"WT"+surveySeq)
4. tempRealExcelUpload(file, commandMap)
   → commonModuleService.getExcelUploadList()  ← 엑셀 파싱
   → selectMaxLineNo()
   → loop: tempRealExcelUpload(map)   ← 행별 insert
```

| No | 세션 조건 | 파일/파라미터 | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`, chainMsNo=`NC0001`, ID=`7249525SHOP` | `.xlsx` 파일, `surveyDate=20260522&msNo=NC0002` (본부) | chainMsNoYn=`"Y"` 세팅 후 insert |
| 4-2 | chainNo=`C001` | `.xlsx` 파일, `surveyDate=20260522&msNo=MS001` (비본부) | chainMsNoYn 미세팅 (commandMap에 null) |
| 4-3 | chainNo=`C001` | 파일 없음, `surveyDate=20260522&msNo=MS001` | `iterator.hasNext()=false` → `file=null` → `commonModuleService.getExcelUploadList(dto, null)` → **NPE 또는 서비스 처리** ★ |
| 4-4 | chainNo=`C001` | 빈 `.xlsx` 파일 | list.size()=0 → 루프 미실행 → deleteTempRealList 후 신규 데이터 없음 |
| 4-5 | chainNo=`C001` | surveyDate="" (defaultValue) | surveySeq = `""+"WT"+seq` → `"WT001"` 형태 |

---

## 5. `/saveTempRealGoods` — 실사 수량 저장

**서비스**: `goodsCdArr`/`surveyQtyArr` → `ArrayList<String>` 캐스팅 후 순회

```java
// RequestBody로 전달되는 JSON Array → Jackson이 ArrayList로 역직렬화
// surveyQtyArr.get(i) → goodsCdArr.size()로만 순회, surveyQtyArr 길이 미검증 ★
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | ID=`7249525SHOP` | `{"msNo":"MS001","surveySeq":"20260522WT001","goodsCdArr":["G001","G002"],"surveyQtyArr":["10","5"]}` | 2건 update |
| 5-2 | ID=`7249525SHOP` | `{"goodsCdArr":["G001","G002"],"surveyQtyArr":["10"]}` | `surveyQtyArr.get(1)` → **IndexOutOfBoundsException** ★★ |
| 5-3 | ID=`7249525SHOP` | `{"goodsCdArr":null}` | `goodsCdArr.size()` → **NPE** ★★★ |

---

## 6. `/deleteTempRealGoods` — 실사 상품 삭제

**서비스**: `goodsCdArr` → `ArrayList<String>` 캐스팅 후 순회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 6-1 | ID=`7249525SHOP` | `{"msNo":"MS001","surveySeq":"20260522WT001","goodsCdArr":["G001"]}` | 1건 delete |
| 6-2 | ID=`7249525SHOP` | `{"goodsCdArr":null}` | **NPE** ★★★ |

---

## 7. `/confirmTempRealList` — 실사 확정 (7단계)

**서비스 처리 순서**:
```
1. confirmTempRealList()     ← 임시 데이터 확정 update
2. getImtrlgCnt()            ← IMTRLGTB count 조회
3. imtrlgCnt > 0 → throw new Exception("IMTRLG DATA EXIST!!")
   → @Transactional rollback ← RuntimeException.class AND Exception.class 포함
4. getChainMsNo()
5. getMsEnvInfo()  → priceFg 분기
6. getSurveyIdx()  → idx 채번
7. insertImrealtb() + confirmRealList()
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 7-1 | chainNo=`C001`, ID=`7249525SHOP` | 임시 데이터 존재, IMTRLG 없음 | `{"msNo":"MS001","surveySeq":"20260522WT001"}` | 7단계 정상 확정, rollback 없음 |
| 7-2 | chainNo=`C001` | IMTRLG 데이터 존재 (imtrlgCnt>0) | `{"msNo":"MS001","surveySeq":"20260522WT001"}` | `Exception("IMTRLG DATA EXIST!!")` → **전체 rollback** ★★ |
| 7-3 | chainNo=`C001` | msEnvInfo null | 유효 파라미터 | priceFg = null → Mapper SQL 처리 확인 |

---

## 8. `/addGoodsTempList` — 실사 상품 추가

**서비스 핵심 분기**:
```
getSurveyCount() > 0 → getSurveySeq() (기존 seq 사용)
               else  → getNewSurveySeq() (신규 seq 채번)

loop i in goodsCdArr:
  closeMonth  = surveySeq.substring(0, 6)  ← 6자리 연월
  surveyDate  = surveySeq.substring(0, 8)  ← 8자리 연월일

  checkGoodsTempList() > 0 → saveTempRealGoods() (update)
                      else → addGoodsTempList() + maxLine++
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 8-1 | chainNo=`C001`, ID=`7249525SHOP` | surveyCount=0 (신규) | `{"msNo":"MS001","surveyDate":"20260522","goodsCdArr":["G001"],"surveyQtyArr":["10"]}` | getNewSurveySeq → addGoodsTempList |
| 8-2 | chainNo=`C001` | surveyCount>0 (기존 seq) | 동일 | getSurveySeq → 기존 seq 사용 |
| 8-3 | chainNo=`C001` | 상품 이미 존재 (checkGoodsTempList>0) | `{"goodsCdArr":["G001"],"surveyQtyArr":["10"]}` | saveTempRealGoods (update) |
| 8-4 | chainNo=`C001` | - | `{"goodsCdArr":null}` | `goodsCdArr.size()` → **NPE** ★★★ |

---

## 9. `/createTempRealGoods` — 전수실사 상품 일괄 생성

**처리 순서**:
```
deleteTempRealList()   ← 기존 내역 전체 삭제
getNewSurveySeq()      ← 신규 seq 채번
commandMap.put("surveySeq", surveyDate+"WT"+surveySeq)

createTempRealGoods():
  maxLine = selectMaxLineNo() - 1  ← maxLine-1 주의 (0 → -1 → "%04d"=-001?) ★
  closeMonth = surveySeq.substring(0,6)
  surveyDate = surveySeq.substring(0,8)
  createTempRealGoods(map)
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 9-1 | chainNo=`C001`, ID=`7249525SHOP` | 기존 데이터 있음 | `{"msNo":"MS001","surveyDate":"20260522"}` | 기존 삭제 → 신규 seq → 일괄 생성 |
| 9-2 | chainNo=`C001` | 기존 데이터 없음 (selectMaxLineNo=0) | `{"msNo":"MS001","surveyDate":"20260522"}` | maxLine = 0-1 = **-1** → `String.format("%04d",-1)` = `"-001"` ★★ |

---

## 10. `/print` — 실사 내역 출력 (ModelAndView)

**특이사항**:
- `@RestController`임에도 `ModelAndView` 반환 → 브라우저 렌더링 필요
- `map.get("surveyDate").toString().substring(0,4)` → surveyDate null 시 **NPE** ★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 10-1 | chainNo=`C001` | `{"msNo":"MS001","surveyDate":"20260522"}` | View 렌더링 (hq_stock_00009_print) |
| 10-2 | chainNo=`C001` | `{}` (msNo 없음) | `map.get("msNo").equals(chainMsNo)` → **NPE** ★★★ |
| 10-3 | chainNo=`C001` | `{}` (surveyDate 없음) | `map.get("surveyDate").toString()` → **NPE** ★★★ |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/stock/hq_stock_00009"
$h = @{"Content-Type"="application/json"}

# 1-1. 전수실사 내역 조회
Invoke-RestMethod -Uri "$base/getTempRealList" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001","surveyDate":"20260522"}'

# 1-5. msNo 없음 → NPE
Invoke-RestMethod -Uri "$base/getTempRealList" -Method POST -Headers $h -WebSession $session `
  -Body '{}'

# 3-1. 상품 모달 조회
Invoke-RestMethod -Uri "$base/goodsSelect" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001","surveyDate":"20260522","offset":0,"limit":10}'

# 5-1. 수량 저장
Invoke-RestMethod -Uri "$base/saveTempRealGoods" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001","surveySeq":"20260522WT001","goodsCdArr":["G001","G002"],"surveyQtyArr":["10","5"]}'

# 7-1. 실사 확정
Invoke-RestMethod -Uri "$base/confirmTempRealList" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001","surveySeq":"20260522WT001"}'

# 9-1. 일괄 생성
Invoke-RestMethod -Uri "$base/createTempRealGoods" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001","surveyDate":"20260522"}'

# 4-1. 엑셀 업로드 (multipart)
$excelFile = "C:\test\survey_template.xlsx"
$form = @{ surveyDate = "20260522"; msNo = "MS001"; file = Get-Item $excelFile }
Invoke-RestMethod -Uri "$base/tempRealExcelUpload" -Method POST -WebSession $session `
  -Form $form
```

---

## 주요 검증 포인트

```
□ getTempRealList/goodsSelect/print — map.get("msNo") null → .equals() NPE ★★★
□ getTempRealList/print — surveyDate null → .toString().substring() NPE ★★★
□ goodsSelect — offset/limit 없으면 (int)map.get("offset") → NPE ★★★
□ saveTempRealGoods — surveyQtyArr 길이 < goodsCdArr → IndexOutOfBoundsException ★★
□ confirmTempRealList — imtrlgCnt > 0 → throw Exception → rollback (Step1 포함) ★★
□ createTempRealGoods — maxLine=0-1=-1 → lineNo="-001" (negativeNumber format) ★★
□ tempRealExcelUpload — file=null (파일 미전달) → commonModuleService NPE ★
□ addGoodsTempList — surveySeq.substring(0,6) → seq 형식이 "YYYYMMWT###"이면 closeMonth 추출 오류 가능 ★
□ @Transactional rollbackFor Exception.class 포함 → confirmTempRealList throw Exception → rollback 정상
□ print — @RestController에서 ModelAndView 반환 → REST 클라이언트로 테스트 불가, 브라우저 직접 확인 필요
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/getTempRealList` | ✅ SELECT |
| `/getFormDownGoodsList` | ✅ SELECT |
| `/goodsSelect` | ✅ SELECT |
| `/tempRealExcelUpload` | ✅ INSERT |
| `/saveTempRealGoods` | ✅ UPDATE |
| `/deleteTempRealGoods` | ✅ DELETE |
| `/confirmTempRealList` | ✅ UPDATE |
| `/addGoodsTempList` | ✅ INSERT |
| `/createTempRealGoods` | ✅ INSERT |
| `/print` | ✅ SELECT |

### 소스 확인 사항

**소스 211번** (`/tempRealExcelUpload`): `(MultipartHttpServletRequest)req` **직접 캐스팅** ★★★  
→ `multipart/form-data`가 아닌 일반 요청으로 호출 시 **ClassCastException → 500**  
→ TC 4-3 (파일 미전달)과는 별개 위험 경로: 요청 타입 자체가 multipart 아닐 때

**소스 90번** (`getTempRealList`): `map.get("msNo").equals(chainMsNo)` — `msNo` null → **NPE** (TC 1-5 ✅ 정확)  
**소스 175번** (`goodsSelect`): 동일 패턴 (TC 3-2 ✅ 정확)  
**소스 437번** (`print`): 동일 패턴 (TC 10-2 ✅ 정확)

**소스 446~447번** (`print`): `map.get("surveyDate").toString().substring(0,4)` — `surveyDate` null → **NPE** (TC 10-3 ✅ 정확)

**소스 391번** (`createTempRealGoods`): `(HashMap<String,Object>)commandMap.getMap()` 다운캐스팅  
→ `CommandMap.getMap()` 반환 타입이 `HashMap`이어야 정상, 아니면 **ClassCastException** ★

**소스 395번** (`createTempRealGoods`): `commandMap.put("surveySeq", map.get("surveyDate")+"WT"+surveySeq)`  
→ `surveyDate` null 시 `"nullWT001"` 형태로 surveySeq 세팅됨 ★


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
