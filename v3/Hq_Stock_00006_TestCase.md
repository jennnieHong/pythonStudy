# Hq_Stock_00006 — 조정 현황 단위 테스트케이스

> **화면**: [HQ] 재고 > 조정 현황  
> **URL Prefix**: `POST /backoffice/data/hq/stock/hq_stock_00006`  
> **@Transactional**: 기본값 (rollbackFor 미명시)  
> **요청 방식**: 전 엔드포인트 `@RequestBody`  
> **서비스 특이사항**: `selectModifyDtList` — Stream `.map()` 으로 DTO에 `chainHqYn` 세팅 후 반환
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 00005 (조정 등록) vs 00006 (조정 현황) 비교

| 항목 | Hq_Stock_00005 | Hq_Stock_00006 |
|------|---------------|---------------|
| 기능 | 조정 등록/수정/삭제/확정 | **조정 현황 조회만** (CUD 없음) |
| 엔드포인트 수 | 10개 | **2개** |
| 요청 방식 | 혼용 | **전부 RequestBody** |
| 세션 `chainHqYn` | 미사용 | **사용** (본사/가맹 구분) |
| 세션 `msNo` | 미사용 | **사용** (userMsNo — 사용자 매장) |
| 날짜 파라미터 | `surveyDate` (단일) | `searchFromDate` + `searchToDate` (기간) |
| 페이징 | offset/limit | **없음** (전체 반환) |

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainHqYn` | `Y` (본사) / `N` (가맹점) | search, searchDt |
| `chainNo` | `C001` | search, searchDt |
| `msNo` | `MS001` | search, searchDt (`userMsNo`로 매핑) |
| `chainMsNo` | `NC0001` | searchDt |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/search` | 조정 현황 목록 조회 (기간 + 다중 필터) | `List` | SELECT | IMREALTB<br>MMSSRCTB<br>MNAMEMTB<br>TMSSRCTB |
| 2 | `/searchDt` | 조정 현황 상세 조회 (Stream으로 chainHqYn 주입) | `List` | SELECT | IMREALTB<br>MMSSRCTB<br>MNAMEMTB<br>MPRICETB<br>TMSSRCTB<br>TPRICETB |

---

## 1. `/search` — 조정 현황 목록 조회

**파라미터 처리**:
- `searchFromDate`, `searchToDate`, `gijun` — null 방어 없음 (reqMap.get() 직접)
- `reasonCd`, `gubun`, `lclassCd`, `mclassCd`, `sclassCd`, `barcode`, `goodsCd`, `setFg`, `msNo` — `containsKey` 방어 후 `""` 기본값

**`chainHqYn` 역할**: Mapper SQL에서 본사(Y)이면 전 매장, 가맹(N)이면 `userMsNo` 필터

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainHqYn=`Y`, chainNo=`C001` | 조정 데이터 존재 | `{"searchFromDate":"20260501","searchToDate":"20260531","gijun":"1"}` | 전 매장 조정 목록 |
| 1-2 | chainHqYn=`N`, msNo=`MS001` | - | `{"searchFromDate":"20260501","searchToDate":"20260531","gijun":"1"}` | userMsNo=MS001 필터 목록 |
| 1-3 | chainHqYn=`Y` | - | `{"searchFromDate":"20260501","searchToDate":"20260531","gijun":"1","reasonCd":"R01","gubun":"IN"}` | 사유+구분 필터 |
| 1-4 | chainHqYn=`Y` | - | `{"searchFromDate":"20260501","searchToDate":"20260531","gijun":"1","lclassCd":"L01","mclassCd":"M01","sclassCd":"S01"}` | 분류 필터 |
| 1-5 | chainHqYn=`Y` | - | `{"searchFromDate":"20260501","searchToDate":"20260531","gijun":"1","barcode":"8801234","goodsCd":"G001"}` | 바코드+상품코드 필터 |
| 1-6 | chainHqYn=`Y` | - | `{"searchFromDate":"20260501","searchToDate":"20260531","gijun":"1","msNo":"MS001"}` | 특정 매장 필터 |
| 1-7 | chainHqYn=`Y` | - | `{"searchToDate":"20260531","gijun":"1"}` (searchFromDate 없음) | `reqMap.get("searchFromDate")` = null → Mapper SQL에서 null 처리 여부 확인 |
| 1-8 | chainHqYn=`Y` | - | `{}` (searchFromDate/searchToDate/gijun 모두 없음) | 모두 null → Mapper SQL 동작 확인 |
| 1-9 | chainHqYn=`Y` | 데이터 없음 | `{"searchFromDate":"20200101","searchToDate":"20200131","gijun":"1"}` | `[]` 빈 리스트 |

---

## 2. `/searchDt` — 조정 현황 상세 조회

**서비스 핵심 로직**:
```java
selectModifyDtList(commandMap)
  → Mapper 조회 후 Stream.map()으로 각 DTO에
    mapper.setChainHqYn(commandMap.get("chainHqYn")) 주입
  → Collectors.toList()

※ Mapper 결과가 빈 리스트이면 Stream map 미실행 → 빈 리스트 반환 (정상)
※ chainHqYn 주입은 서비스에서 처리 (Mapper SQL이 아님)
```

**필수 파라미터** (null 방어 없음): `searchFromDate`, `searchToDate`, `paramDate`, `msNo`, `surveySeq`, `gijun`, `goodsCd`  
**선택 파라미터** (containsKey 방어): `lclassCd`, `mclassCd`, `sclassCd`, `reasonCd`, `setFg`, `gubun`, `barcode`

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 2-1 | chainHqYn=`Y`, chainNo=`C001`, msNo=`MS001`, chainMsNo=`NC0001` | 상세 데이터 존재 | `{"searchFromDate":"20260501","searchToDate":"20260531","paramDate":"20260522","msNo":"MS001","surveySeq":"1","gijun":"1","goodsCd":"G001"}` | DTO 리스트 (각 항목에 chainHqYn=`"Y"` 세팅됨) |
| 2-2 | chainHqYn=`N`, msNo=`MS001` | - | 동일 | DTO 리스트 (chainHqYn=`"N"` 세팅) |
| 2-3 | chainHqYn=`Y` | 데이터 없음 | 유효 파라미터 | `[]` (Stream map 미실행) |
| 2-4 | chainHqYn=`Y` | - | `{"searchFromDate":"20260501","searchToDate":"20260531","gijun":"1","lclassCd":"L01","reasonCd":"R01"}` + 나머지 필수 | 분류+사유 필터 + chainHqYn 주입 |
| 2-5 | chainHqYn=`Y` | - | 필수 파라미터(`paramDate`) 없음 | `reqMap.get("paramDate")` = null → Mapper SQL 조건 확인 |
| 2-6 | chainHqYn=`Y` | - | `goodsCd` 없음 | `reqMap.get("goodsCd")` = null |

---

## chainHqYn 동작 분기 상세

```
search 엔드포인트:
  chainHqYn = 세션에서 직접 주입 → commandMap "chainHqYn"
  Mapper SQL에서 chainHqYn='Y' 이면 전 매장 조회
               chainHqYn='N' 이면 userMsNo 기준 필터

searchDt 엔드포인트:
  chainHqYn = Mapper SQL 조건으로 전달
  + 서비스에서 Stream.map()으로 DTO의 chainHqYn 필드에도 세팅
    → DTO에 chainHqYn 필드가 있어야 정상 동작
```

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/stock/hq_stock_00006"
$h = @{"Content-Type"="application/json"}

# 1-1. 조정 현황 목록 (본사 계정)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchToDate":"20260531","gijun":"1"}'

# 1-3. 사유+구분 필터
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchToDate":"20260531","gijun":"1","reasonCd":"R01","gubun":"IN"}'

# 1-7. searchFromDate 없음 (null 처리 확인)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchToDate":"20260531","gijun":"1"}'

# 2-1. 조정 현황 상세 조회
Invoke-RestMethod -Uri "$base/searchDt" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchToDate":"20260531","paramDate":"20260522","msNo":"MS001","surveySeq":"1","gijun":"1","goodsCd":"G001"}'
# 예상: DTO 리스트, 각 항목 chainHqYn 필드 확인

# 2-3. 데이터 없는 경우 (빈 리스트 확인)
Invoke-RestMethod -Uri "$base/searchDt" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20200101","searchToDate":"20200131","paramDate":"20200115","msNo":"MS001","surveySeq":"1","gijun":"1","goodsCd":"G999"}'
# 예상: []
```

---

## 주요 검증 포인트

```
□ search — chainHqYn='Y' vs 'N' 분기 → 전 매장 vs userMsNo 필터 동작 확인
□ search — searchFromDate/searchToDate/gijun null 방어 없음 → Mapper SQL BETWEEN null 처리 확인
□ search — containsKey 방어 파라미터(reasonCd 등) 미전달 시 "" 기본값 → SQL WHERE 조건 무효화
□ searchDt — Stream.map()으로 chainHqYn 주입 → DTO 클래스에 setChainHqYn() 메서드 필요
□ searchDt — Mapper 결과 빈 리스트 → Stream 정상 처리 (NPE 없음)
□ searchDt — paramDate, msNo, surveySeq, goodsCd null 방어 없음 → Mapper SQL 조건 확인
□ 페이징 없음 — 대량 데이터 조회 시 전체 반환 → 성능 주의
□ @Transactional 기본값 — SELECT only이므로 사실상 영향 없음
□ 메서드명 오류 — searchDt의 메서드명 "HqStock0204DetailList" (00006이 아닌 0204 명칭) 확인
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/search` | ✅ SELECT |
| `/searchDt` | ✅ SELECT |

### 소스 확인 사항

**소스 38번**: `@Validated` ✅ 클래스 레벨 정상 적용

**소스 71~76번** (`/search`): `searchFromDate`, `searchToDate`, `gijun` — `containsKey` 없이 직접 `reqMap.get()` → null 전달 → Mapper null 처리 확인 필요 (TC 1-7, 1-8 ✅ 정확)

**소스 77~85번** (`/search`): `reasonCd`, `gubun`, `lclassCd`, `mclassCd`, `sclassCd`, `barcode`, `goodsCd`, `setFg`, `msNo` — `containsKey` 방어 ✅ `""` 기본값

**소스 106번**: 메서드명 `HqStock0204DetailList` — 네이밍 오류 (TC 158번 ✅ 이미 명시)

**소스 123~127번** (`/searchDt`): `paramDate`, `msNo`, `surveySeq`, `gijun`, `goodsCd` — `containsKey` 없이 직접 `reqMap.get()` → null 전달 (TC 2-5, 2-6 ✅ 정확)

**소스 128~134번** (`/searchDt`): `lclassCd`, `mclassCd`, `sclassCd`, `reasonCd`, `setFg`, `gubun`, `barcode` — `containsKey` 방어 ✅

**소스 136번**: `hq_Stock_00006_Service.selectModifyDtList(commandMap)` — 서비스 내 Stream.map()으로 chainHqYn 주입 (TC 2-1 chainHqYn 주입 확인 ✅)
