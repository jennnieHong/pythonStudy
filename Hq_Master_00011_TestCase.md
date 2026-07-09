# Hq_Master_00011 — 본사 판매가 변경 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > 가격관리 > 판매가 변경  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00011`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: `/searchArea02` = `@RequestBody` / `/saveGoodsPrice` = `@RequestParam` 배열
> **DB 트리거 영향도**: TPRICETB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## ⚠️ 서비스 핵심 NPE 위험

```java
// saveGoodsPrice() 서비스 내
Map<String,Object> priceInfo = Hq_Master_00011_Mapper.getPriceInfo(map);

map.put("raiseFg" , priceInfo.get("RAISE_FG").toString());  // priceInfo null → NPE ★★★
map.put("prePrice", priceInfo.get("PRE_PRICE").toString());  // priceInfo null → NPE ★★★
```
→ `getPriceInfo()` 결과가 null인 경우 (해당 상품 가격 정보 없음) **NPE** 발생

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | searchArea02, saveGoodsPrice |
| `chainMsNo` | `NC0001` | saveGoodsPrice |
| `ID` | `7249525SHOP` | saveGoodsPrice |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/searchArea02` | 상품 목록 조회 (페이징) | `@RequestBody` | `Map` (total+rows) | SELECT | TGOODSTB<br>TPRICETB |
| 2 | `/saveGoodsPrice` | 판매가 일괄 변경 (insert/update 분기) | `@RequestParam` 배열 | `void` | TPRICETB |

---

## 1. `/searchArea02` — 상품 조회

**★ offset 미전달**: `(int)map.get("offset")` → **NPE** ★★★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"offset":0,"limit":10}` | 상품 목록 + total |
| 1-2 | (동일) | `{"offset":0,"limit":10,"selectGoodsNm":"커피"}` | 상품명 필터 |
| 1-3 | (동일) | `{}` (offset 없음) | `(int)map.get("offset")` → **NPE** ★★★ |
| 1-4 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 2. `/saveGoodsPrice` — 판매가 변경 저장

**처리 흐름**:
```
goodsCd_arr 루프:
  getPriceInfo(map)            → 기존 가격 정보 조회
  priceInfo.get("RAISE_FG")   → null이면 NPE ★★★
  priceInfo.get("CNT")=="0"   → insertGoodsPrice
  else                        → updateGoodsPrice
```

**★ price_arr 길이 < goodsCd_arr.length**: `price_arr[i]` → **ArrayIndexOutOfBoundsException** ★★★  
**★ defaultValue=""**: `goodsCd_arr=[""]` → 빈 문자열 1개 배열 처리 주의

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | chainNo=`C001`, chainMsNo=`NC0001`, ID=`7249525SHOP` | `startDate=2026-05-26&goodsCd_arr[]=G001&price_arr[]=5500` | insert 또는 update → void |
| 2-2 | (동일) | `startDate=2026-05-26&endDate=2026-12-31&goodsCd_arr[]=G001&price_arr[]=5500` | endDate 포함 → `replaceAll("-","")` → `"20261231"` |
| 2-3 | (동일) | 다중: goodsCd_arr[] 2개, price_arr[] 1개 | `price_arr[1]` → **ArrayIndexOutOfBoundsException** ★★★ |
| 2-4 | (동일) | 가격 정보 없는 goodsCd (getPriceInfo null 반환) | `null.get("RAISE_FG")` → **NPE** ★★★ |
| 2-5 | (동일) | `goodsCd_arr` 미전달 (defaultValue="") | `goodsCd_arr=[""]` → 빈 문자열 처리 (Mapper WHERE 조건 확인) |
| 2-6 | - | `startDate` 없음 | 400 (@NotBlank) |
| 2-7 | - | `startDate=` (빈 문자열) | 400 (@NotBlank) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00011"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 상품 조회
Invoke-RestMethod -Uri "$base/searchArea02" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'

# 1-3. offset 없음 → NPE
Invoke-RestMethod -Uri "$base/searchArea02" -Method POST -Headers $h -WebSession $session `
  -Body '{}'
# 예상: 500 NPE

# 2-1. 판매가 저장 (정상)
Invoke-RestMethod -Uri "$base/saveGoodsPrice" -Method POST -ContentType $f -WebSession $session `
  -Body "startDate=2026-05-26&goodsCd_arr[]=G001&price_arr[]=5500"

# 2-3. 배열 길이 불일치 → ArrayIndexOutOfBounds
Invoke-RestMethod -Uri "$base/saveGoodsPrice" -Method POST -ContentType $f -WebSession $session `
  -Body "startDate=2026-05-26&goodsCd_arr[]=G001&goodsCd_arr[]=G002&price_arr[]=5500"
# 예상: 500

# 2-6. startDate 없음 → 400
Invoke-RestMethod -Uri "$base/saveGoodsPrice" -Method POST -ContentType $f -WebSession $session `
  -Body "goodsCd_arr[]=G001&price_arr[]=5500"
```

---

## 주요 검증 포인트

```
□ searchArea02 — offset 미전달 → (int)map.get("offset") → NPE ★★★
□ saveGoodsPrice — getPriceInfo null 반환 → priceInfo.get(...).toString() → NPE ★★★
□ saveGoodsPrice — price_arr.length < goodsCd_arr.length → ArrayIndexOutOfBoundsException ★★★
□ saveGoodsPrice — goodsCd_arr defaultValue="" → 빈 배열[""] 로 루프 1회 실행 → Mapper 처리
□ saveGoodsPrice — startDate.replaceAll("-","") → "2026-05-26" → "20260526" ✓
□ saveGoodsPrice — CNT=="0" 분기 → insert / 그 외 → update 로직 정상 확인
□ @Transactional rollbackFor Exception — saveGoodsPrice 루프 내 예외 시 전체 rollback
□ @NotBlank(startDate) — 빈 문자열 → 400
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/searchArea02` | ✅ SELECT |
| `/saveGoodsPrice` | ✅ INSERT |

### 소스 확인 사항

**소스 74번**: `(int)map.get("offset")` — `offset` null → **NPE** (TC 1-3 ✅ 정확)

**소스 101~102번**: `goodsCd_arr[]`, `price_arr[]` — `required=false`, `defaultValue=""`  
→ 미전송 시 `[""]` (빈 문자열 1개짜리 배열) → 루프 1회 실행 → 빈 goodsCd로 Mapper 조회 (TC 2-5 ✅)

**소스 113~123번**: 루프 내 `commandMap = new CommandMap()` 재생성 후 `.getMap()`으로 list 추가  
→ `goods_list`는 각 루프 별 독립 Map 객체 보유 — 정상 패턴 ✅

**소스 120번**: `price_arr[i]` — `price_arr.length < goodsCd_arr.length` 시 **ArrayIndexOutOfBoundsException** (TC 2-3 ✅ 정확)

**소스 104~105번**: `startDate.replaceAll("-","")`, `endDate.replaceAll("-","")` — String 메서드 호출이므로 null 아닌 빈값("") 도 정상 처리 (`defaultValue=""` 덕분에 NPE 없음 ✅)


## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
└── [테이블] TPRICETB (CUD 작업)
    └── (Trigger) Tr_TPRICE_T01
```
