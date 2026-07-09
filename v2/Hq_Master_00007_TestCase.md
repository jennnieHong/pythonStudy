# Hq_Master_00007 — 레시피 조회/등록 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > 상품관리 > 레시피 조회/등록  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00007`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **외부 의존**: `CommonModuleService.getExcelUploadList()` (POI 엑셀 파싱)  
> **요청 방식**: 대부분 `@RequestBody` JSON / 엑셀 업로드는 `multipart/form-data`
> **DB 트리거 영향도**: TB_RECIPE_GOODS, TGOODSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 |
| `chainMsNo` | `NC0001` | 체인 본부 매장번호 |
| `msNo` | `MS001` | 본인 매장번호 |
| `ID` | `shopadmin` | 로그인 사용자 ID |

---

## 엔드포인트 목록 (10개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | 요청 방식 | Type | 관련 테이블 |
|---|---|---|---|---|---|
|1|`/recpSearch`|레시피 목록 조회 (페이징)|`@RequestBody`|SELECT| 공통 모듈/동적 쿼리 (추적 불가) |
| 2 | `/recpDetail` | 레시피 상세 조회 | `@RequestBody` | SELECT | MMEMBSTB<br>TGOODSTB |
|3|`/updateRecp`|레시피 수정 (기존 삭제 + 신규 일괄 INSERT)|`@RequestBody`|UPDATE| 공통 모듈/동적 쿼리 (추적 불가) |
| 4 | `/history` | 레시피 히스토리 조회 (헤더+구성상품 2종) | `@RequestBody` | SELECT | MNAMEMTB |
| 5 | `/modalSearch` | 레시피 적용 상품 상세 조회 | `@RequestParam` | SELECT | MMEMBSTB<br>MNAMEMTB<br>TGOODSTB<br>TPRICETB |
| 6 | `/getExtra` | 부가메뉴 조회 | (no body) | SELECT | TMBUMSTB |
| 7 | `/goodsSearch` | 레시피 상품 추가 시 상품 검색 (페이징) | `@RequestBody` | SELECT | MNAMEMTB<br>TGOODSTB |
|8|`/saveRecp`|레시피 신규 저장 (코드채번 → 헤더 → 구성상품)|`@RequestBody`|INSERT| 공통 모듈/동적 쿼리 (추적 불가) |
| 9 | `/deleteRecp` | 레시피 삭제 (3단계: 헤더+구성+상품매핑 null) | `@RequestBody` | DELETE | TGOODSTB |
|10|`/excelUploadRecipe`|레시피 마스터 엑셀 업로드|`multipart/form-data`|INSERT| 공통 모듈/동적 쿼리 (추적 불가) |
|11|`/excelUploadRecipeGoods`|레시피 구성상품 엑셀 업로드|`multipart/form-data`|UPDATE| 공통 모듈/동적 쿼리 (추적 불가) |

---

## 1. `/recpSearch` — 레시피 목록 조회

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainNo=`C001` | 레시피 5건 | `{"offset":0,"limit":10}` | `{"total":5,"rows":[...]}` |
| 1-2 | chainNo=`C001` | - | `{"offset":0,"limit":10,"recp_nm":"아메리카노","stock_yn":"Y"}` | 필터 결과 |
| 1-3 | chainNo=`C001` | - | `{"offset":0,"limit":10,"searchFromDate":"20260101","searchToDate":"20260531"}` | 기간 필터 |
| 1-4 | - | - | `{}` (offset 없음) | **ClassCastException** (int 캐스팅) |

---

## 2. `/recpDetail` — 레시피 상세 조회

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 2-1 | chainNo=`C001` | R001 존재 | `{"recpCd":"R001"}` | 레시피 구성상품 List |
| 2-2 | chainNo=`C001` | R999 미존재 | `{"recpCd":"R999"}` | `[]` |
| 2-3 | - | - | `{}` (recpCd 없음) | `recpCd=null` → 전체 조회 또는 빈 결과 |

---

## 3. `/updateRecp` — 레시피 수정

**컨트롤러**: `getRegiGoodsList()` → `regiGoodsList` 세팅 후 `updateRecp()` 호출  

**서비스 로직 (updateRecp)**:
```
1. updtRecp(헤더 수정: stockYn, remark, recpNm)
2. delNotUpdtRecpGoods(기존 구성상품 전체 삭제)
3. goodsCdArr 순회:
   → updtRecpGoods(goodsCd, weight 개별 MERGE/INSERT)
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 3-1 | chainNo=`C001`, ID=`shopadmin` | R001 구성상품 3건 | `{"recpCd":"R001","recpNm":"수정레시피","stockYn":"Y","remark":"비고","goodsCdArr":["G001","G002"],"weightArr":[100.0,200.0]}` | updtRecp + delNotUpdtRecpGoods + updtRecpGoods×2 |
| 3-2 | chainNo=`C001` | R001 구성상품 있음 | `{"recpCd":"R001","goodsCdArr":[],"weightArr":[]}` | updtRecp + delNotUpdtRecpGoods + updtRecpGoods 없음 (전체 삭제만) |
| 3-3 | chainNo=`C001` | - | `{"recpCd":"R001","goodsCdArr":["G001"],"weightArr":[100.0,200.0]}` | goodsCdArr.size(1) < weightArr → 인덱스 out-of-bounds |
| 3-4 | - | - | `{}` (goodsCdArr 없음) | **NPE** (null cast to ArrayList) |
| 3-5 | - | - | @Transactional: updtRecpGoods 실패 | updtRecp + delNotUpdtRecpGoods 롤백 |
| 3-6 | updateRecp 성공 응답 | 정상 수정 | HTTP 200 + **빈 바디** ★ |

---

## 4. `/history` — 레시피 히스토리 조회

**2종 동시 조회**: `getRecpHeader()` + `histRecpMainGoods()`

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 4-1 | chainNo=`C001` | R001 히스토리 존재 | `{"recpCd":"R001"}` | `{"recipeHeader":[...],"histRecpGoodsList":[...]}` |
| 4-2 | chainNo=`C001` | 히스토리 없음 | `{"recpCd":"R001"}` | `{"recipeHeader":[],"histRecpGoodsList":[]}` |

---

## 5. `/modalSearch` — 레시피 적용 상품 상세 조회

**컨트롤러 흐름**:
```
getModalList(goodsCd) → dto.getRecipeCd() → recp_cd 추출
→ getRecipe(recp_cd) → recipeList
→ getShopBrandCd()
```

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 5-1 | chainNo=`C001` | G001 존재 (레시피 있음) | `goodsCd=G001` | modalList + recipeList(구성상품) + brandShopCd |
| 5-2 | chainNo=`C001` | G002 (레시피 없음) | `goodsCd=G002` | modalList + recipeList=[] |
| 5-3 | chainNo=`C001` | - | `goodsCd=` (빈값, defaultValue="") | getModalList null → `getRecipeCd()` **NPE** ★ |

---

## 7. `/goodsSearch` — 레시피 상품 추가 검색

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 7-1 | chainNo=`C001` | 상품 10건 | `{"offset":0,"limit":10,"goodsCdArr":["G001","G002"]}` | G001, G002 제외 상품 List (goodsCdArr IN 제외 조건) |
| 7-2 | chainNo=`C001` | - | `{"offset":0,"limit":10}` (goodsCdArr null) | IN 조건 없이 전체 |
| 7-3 | - | - | `{}` (offset 없음) | ClassCastException |

---

## 8. `/saveRecp` — 레시피 신규 저장

**컨트롤러**: `goodsCdArr/weightArr` → `list` (goodsCd, weight, idx) 변환 후 저장  
**서비스 로직**:
```
1. getRecpCd() → recpCd 채번 (8자리, 예: "00000001")
2. saveRecp(헤더: chainNo, msNo, stockYn, remark, recpNm, recpCd)
3. saveRecpGoods(구성상품 list: goodsCd, weight, idx)
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 8-1 | chainNo=`C001`, ID=`shopadmin`, msNo=`MS001` | - | `{"recpNm":"신규레시피","stockYn":"Y","remark":"비고","goodsCdArr":["G001","G002"],"weightArr":[100.0,50.0]}` | getRecpCd + saveRecp + saveRecpGoods(idx=1,2) |
| 8-2 | chainNo=`C001` | - | `{"recpNm":"레시피","goodsCdArr":[],"weightArr":[]}` | getRecpCd + saveRecp + saveRecpGoods(빈 list) |
| 8-3 | - | - | `{}` (goodsCdArr 없음) | **NPE** (null cast to List) |
| 8-4 | - | - | @Transactional: saveRecpGoods 실패 | saveRecp 롤백 |
| 8-5 | saveRecp 성공 응답 | 정상 저장 | HTTP 200 + **빈 바디** ★ |

---

## 9. `/deleteRecp` — 레시피 삭제

**서비스 3단계**:
```
1. delRecp(recpCdArr → TB_RECIPE 삭제)
2. delRecpGoods(recpCdArr → TB_RECIPE_GOODS 삭제)
3. updtTgoodstb(recpCdArr → TGOODSTB.recp_cd = NULL)
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 9-1 | chainNo=`C001` | R001 존재 (상품 G001에 매핑) | `{"recpCdArr":["R001"]}` | delRecp + delRecpGoods + updtTgoodstb(G001.recp_cd=null) |
| 9-2 | chainNo=`C001` | R001, R002 존재 | `{"recpCdArr":["R001","R002"]}` | 2건 일괄 삭제 + 상품 매핑 null |
| 9-3 | chainNo=`C001` | R999 미존재 | `{"recpCdArr":["R999"]}` | delRecp(0건) + delRecpGoods(0건) + updtTgoodstb(0건) |
| 9-4 | - | - | `{}` (recpCdArr 없음) | recpCdArr=null → IN 조건 전체 삭제 가능성 ★ |
| 9-5 | - | - | @Transactional: updtTgoodstb 실패 | delRecp + delRecpGoods 롤백 |
| 9-6 | deleteRecp 성공 응답 | 정상 삭제 | HTTP 200 + **빈 바디** ★ |

---

## 10. `/excelUploadRecipe` — 레시피 마스터 엑셀 업로드

**서비스 로직**:
```
CommonModuleService.getExcelUploadList(Dto, file) → list 파싱
getRecpCd() → maxRecpCd (정수 파싱: "00000005" → 5)
for each row:
  recipeCd = String.format("%08d", maxRecpCd)  ← 8자리 포맷
  saveRecp(map)
  maxRecpCd++
```

| No | 세션 조건 | DB 선행상태 | Request | 예상값 |
|----|----------|------------|---------|-------|
| 10-1 | chainNo=`C001`, msNo=`MS001` | 레시피 5건 | Excel 파일 (3행) | getRecpCd=5 → "00000005","00000006","00000007" 순서로 저장 |
| 10-2 | chainNo=`C001` | - | 빈 Excel 파일 (0행) | list.size()=0 → saveRecp 없음, getRecpCd 만 조회 |
| 10-3 | chainNo=`C001` | - | 잘못된 형식 Excel | getExcelUploadList 파싱 오류 → **Exception** |
| 10-4 | chainNo=`C001` | - | 파일 없이 전송 | `iterator.hasNext()=false` → file=null → **NPE** |
| 10-5 | - | - | @Transactional: saveRecp 실패 (3번째 행) | 1~2번째 saveRecp 롤백 |

---

## 11. `/excelUploadRecipeGoods` — 레시피 구성상품 엑셀 업로드

**서비스 로직**:
```
CommonModuleService.getExcelUploadList(Dto, file) → list 파싱
for each row:
  updtRecpGoodsExcel(map + chainNo, chainMsNo, userId)  ← UPDATE만
```
**특이사항**: `saveRecp`와 달리 코드 채번 없음 — 기존 레시피 코드로 UPDATE

| No | 세션 조건 | DB 선행상태 | Request | 예상값 |
|----|----------|------------|---------|-------|
| 11-1 | chainNo=`C001`, chainMsNo=`NC0001` | R001 구성상품 존재 | Excel (R001/G001/100g 등) | updtRecpGoodsExcel 건별 실행 |
| 11-2 | chainNo=`C001` | **R999 미존재 레시피** | Excel (R999/G001) | updtRecpGoodsExcel 0건 (오류 없이 통과) |
| 11-3 | chainNo=`C001` | - | 파일 없이 전송 | file=null → **NPE** |
| 11-4 | - | - | @Transactional: updtRecpGoodsExcel 실패 | 이전 행 롤백 |

---

## 서비스 핵심 분기 요약

```
updateRecp
├── updtRecp (헤더 수정)
├── delNotUpdtRecpGoods (기존 전체 삭제)
└── goodsCdArr 순회 → updtRecpGoods (개별 INSERT)
    주의: goodsCdArr와 weightArr 크기 불일치 시 ArrayIndexOutOfBoundsException

saveRecp
├── getRecpCd() 채번
├── saveRecp (헤더)
└── saveRecpGoods (구성상품 list, idx=1~N)

deleteRecp (3단계 연쇄)
├── delRecp (헤더)
├── delRecpGoods (구성상품)
└── updtTgoodstb (상품 매핑 null)
    주의: recpCdArr=null 이면 IN() → 전체 영향 가능 ★

excelUploadRecipe
├── getExcelUploadList() 파싱
├── getRecpCd() → 정수 시작값
└── 행마다 String.format("%08d", maxRecpCd++) → saveRecp
    주의: file=null → NPE (iterator.hasNext()=false 체크 있으나 file 자체 미처리)

excelUploadRecipeGoods
└── getExcelUploadList() 파싱 → 행마다 updtRecpGoodsExcel (채번 없음)
    차이: excelUploadRecipe(INSERT) vs excelUploadRecipeGoods(UPDATE)
```

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00007"
$h = @{"Content-Type"="application/json"}

# 1. 레시피 목록 조회
Invoke-RestMethod -Uri "$base/recpSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'

# 2. 레시피 상세 조회
Invoke-RestMethod -Uri "$base/recpDetail" -Method POST -Headers $h -WebSession $session `
  -Body '{"recpCd":"R001"}'

# 3-1. 레시피 수정
Invoke-RestMethod -Uri "$base/updateRecp" -Method POST -Headers $h -WebSession $session `
  -Body '{"recpCd":"R001","recpNm":"수정레시피","stockYn":"Y","remark":"비고","goodsCdArr":["G001","G002"],"weightArr":[100.0,200.0]}'

# 4. 레시피 히스토리 조회
Invoke-RestMethod -Uri "$base/history" -Method POST -Headers $h -WebSession $session `
  -Body '{"recpCd":"R001"}'

# 8-1. 레시피 신규 저장
Invoke-RestMethod -Uri "$base/saveRecp" -Method POST -Headers $h -WebSession $session `
  -Body '{"recpNm":"신규레시피","stockYn":"Y","remark":"비고","goodsCdArr":["G001","G002"],"weightArr":[100.0,50.0]}'
# 예상: getRecpCd 채번 → saveRecp → saveRecpGoods(2건, idx=1,2)

# 9-1. 레시피 삭제
Invoke-RestMethod -Uri "$base/deleteRecp" -Method POST -Headers $h -WebSession $session `
  -Body '{"recpCdArr":["R001"]}'
# 예상: delRecp + delRecpGoods + updtTgoodstb(recp_cd=null)

# 10. 레시피 엑셀 업로드 (multipart)
$filePath = "C:\test\recipe_upload.xlsx"
$boundary = [System.Guid]::NewGuid().ToString()
Invoke-RestMethod -Uri "$base/excelUploadRecipe" -Method POST -WebSession $session `
  -ContentType "multipart/form-data; boundary=$boundary" `
  -InFile $filePath
```

---

## 주요 검증 포인트

```
□ updateRecp — goodsCdArr / weightArr 크기 불일치 → ArrayIndexOutOfBoundsException
□ updateRecp — goodsCdArr=[] → delNotUpdtRecpGoods (전체 삭제) + updtRecpGoods 없음 (레시피 빈 상태)
□ deleteRecp — recpCdArr=null → IN(null) → 전체 삭제 가능 ★ (Mapper SQL 확인 필수)
□ modalSearch — goodsCd=빈값 → getModalList=null → getRecipeCd() NPE
□ excelUploadRecipe — file=null (첨부파일 없음) → getExcelUploadList NPE
□ excelUploadRecipe vs excelUploadRecipeGoods: INSERT vs UPDATE, 세션키 차이 (msNo vs chainMsNo)
□ excelUploadRecipe — getRecpCd() 반환값 파싱: Integer.parseInt() → 숫자 형식 아니면 NumberFormatException
□ @Transactional — 엑셀 다건 중 중간 실패 시 전체 롤백 (이미 처리된 행 포함)
```

---

## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] TB_RECIPE_GOODS (CUD 작업)
│   └── (Trigger) Tr_TB_RECIPE_GOODS_T01
└── [테이블] TGOODSTB (CUD 작업)
    └── (Trigger) Tr_TGOODS_T01
```
