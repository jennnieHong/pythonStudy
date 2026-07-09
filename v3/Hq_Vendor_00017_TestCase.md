# Hq_Vendor_00017 — 거래처별 입고집계표 단위 테스트케이스

> **화면**: [HQ] 거래처 > 거래처별 입고집계표  
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00017`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception} (SELECT only — 사실상 영향 없음)  
> **요청 방식**: 전 엔드포인트 `@RequestBody`
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, print |
| `chainNm` | `테스트체인` | print (ModelAndView에 추가) |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/search` | 거래처별 입고집계표 조회 | `List` | SELECT | OBSLPHTB |
| 2 | `/print` | 거래처별 입고집계표 출력 (ModelAndView) | `ModelAndView` | SELECT | OBSLPHTB |

---

## `goodsCdArr` 분기 로직 (search/print 공통)

```java
// 컨트롤러에서 직접 처리
if(!commandMap.get("goodsCdArr").equals("ALL")     ← goodsCdArr null → NPE ★★★
   && !(commandMap.get("goodsCdArr").toString().trim()).isEmpty())
{
    String[] array = commandMap.get("goodsCdArr").toString().split(",");
    commandMap.put("goodsCdList", array);           // CSV → 배열 변환
}
// "ALL" 이거나 빈 문자열이면 goodsCdList 미세팅 → Mapper SQL 전체 조회
```

| `goodsCdArr` 값 | 동작 |
|----------------|------|
| `null` 미전달 | `commandMap.get("goodsCdArr")` → **NPE** ★★★ |
| `"ALL"` | 조건 미진입 → 전체 상품 조회 |
| `""` (빈 문자열) | `.trim().isEmpty()=true` → 전체 조회 |
| `"G001"` | goodsCdList=`["G001"]` |
| `"G001,G002,G003"` | goodsCdList=`["G001","G002","G003"]` |
| `" "` (공백) | `.trim().isEmpty()=true` → 전체 조회 |

---

## 1. `/search` — 거래처별 입고집계표 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":"ALL"}` | goodsCdList 미세팅 → 전체 상품 집계 |
| 1-2 | chainNo=`C001` | `{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":"G001,G002"}` | goodsCdList=`["G001","G002"]` → 필터 집계 |
| 1-3 | chainNo=`C001` | `{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":""}` | 빈 문자열 → 전체 조회 |
| 1-4 | chainNo=`C001` | `{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":"G001"}` | 단일 상품 필터 |
| 1-5 | chainNo=`C001` | `{"searchFromDate":"20260501","searchEndDate":"20260531"}` (goodsCdArr 없음) | `commandMap.get("goodsCdArr")` → **NPE** ★★★ |
| 1-6 | chainNo=`C001` | `{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":"ALL","vendor":"VND001"}` | 거래처 필터 추가 |
| 1-7 | chainNo=`C001` | `{"goodsCdArr":"ALL"}` (날짜 없음) | searchFromDate/searchEndDate = null → Mapper SQL 조건 처리 확인 |
| 1-8 | chainNo=`C001` | `{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":"ALL","msNo":"MS001"}` | 매장 필터 |
| 1-9 | chainNo=`C001` | 데이터 없는 기간 | `[]` 빈 리스트 |

---

## 2. `/print` — 거래처별 입고집계표 출력 (ModelAndView)

**특이사항**:
- `@RestController`임에도 `ModelAndView` 반환 → 브라우저 직접 확인 필요
- `mav.addObject("chainNm", securityUserInformation.getUserInfo("chainNm").toString())` → `chainNm` 세션 없으면 **NPE** ★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001`, chainNm=`테스트체인` | `{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":"ALL"}` | View 렌더링 (hq_vendor_00017_printOrder), printList/searchFromDate/searchEndDate/chainNm 전달 |
| 2-2 | chainNo=`C001`, chainNm=`테스트체인` | `{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":"G001,G002"}` | goodsCdList=`["G001","G002"]` 필터 후 출력 |
| 2-3 | chainNm 세션 없음 | 유효 파라미터 | `getUserInfo("chainNm").toString()` → **NPE** ★★ |
| 2-4 | chainNo=`C001`, chainNm=`테스트체인` | `{"searchFromDate":"20260501","searchEndDate":"20260531"}` (goodsCdArr 없음) | **NPE** ★★★ |
| 2-5 | chainNo=`C001`, chainNm=`테스트체인` | 데이터 없는 기간 | printList=`[]` → 빈 출력 화면 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/vendor/hq_vendor_00017"
$h = @{"Content-Type"="application/json"}

# 1-1. 전체 조회 (ALL)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":"ALL"}'

# 1-2. 상품코드 CSV 필터
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":"G001,G002"}'

# 1-3. 빈 문자열 (= ALL과 동일)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchEndDate":"20260531","goodsCdArr":""}'

# 1-5. goodsCdArr 없음 → NPE
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260501","searchEndDate":"20260531"}'
# 예상: 500 NullPointerException

# 1-7. 날짜 없음
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"goodsCdArr":"ALL"}'
# 예상: 전체 또는 Mapper SQL null 처리 결과
```

---

## 주요 검증 포인트

```
□ goodsCdArr 미전달 → commandMap.get("goodsCdArr").equals("ALL") → NPE ★★★ (search/print 공통)
□ goodsCdArr="ALL" → goodsCdList 미세팅 → Mapper SQL 전체 조회 정상 여부
□ goodsCdArr="G001,G002" → split(",") → ["G001","G002"] → Mapper SQL IN 조건 정상 여부
□ print — chainNm 세션 없으면 NPE ★★
□ print — @RestController인데 ModelAndView → REST 클라이언트 테스트 불가 (브라우저 필요)
□ searchFromDate/searchEndDate null → Mapper BETWEEN null → 빈 결과 또는 전체 조회 확인
□ 서비스 단순 위임 (getList 1개) — 비즈니스 로직 전부 컨트롤러에 집중 (goodsCdArr 분기)
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/search` | ✅ SELECT |
| `/print` | ✅ SELECT |

### 소스 확인 사항

**소스 39번**: `@Validated` ✅ 클래스 레벨 정상 적용

**소스 66번** (`/search`): `commandMap.get("goodsCdArr").equals("ALL")` — `goodsCdArr` key 없으면 **NPE** (TC 1-5 ✅ 정확)

**소스 95번** (`/print`): 동일 패턴 → `goodsCdArr` 없으면 **NPE** (TC 2-4 ✅ 정확)

**소스 106번** (`/print`): `securityUserInformation.getUserInfo("chainNm").toString()` — `chainNm` 세션 없으면 **NPE** (TC 2-3 ✅ 정확)

**양 엔드포인트 동일 서비스 호출**: `hq_Vendor_00017_Service.getList(commandMap)` → 단일 Mapper에 goodsCdList 유무로 분기 처리됨 (TC 130번 ✅ 정확)

**goodsCdArr 분기 소스 정확성 확인**:
- `"ALL"` → 분기 미진입 → goodsCdList 미세팅 ✅
- `""` → `.trim().isEmpty()=true` → 분기 미진입 ✅
- `"G001,G002"` → split(",") → `["G001","G002"]` → goodsCdList 세팅 ✅
