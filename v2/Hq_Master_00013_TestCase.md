# Hq_Master_00013 — 본사 원가 변경 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > 가격관리 > 원가 변경  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00013`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **구조 특이사항**: Hq_Master_00011(판매가 변경)과 구조 동일 — 원가(usuprice) 버전  
> **요청 방식 혼용**: `/search` = `@RequestBody` / `/saveGoodsPrice` = `@RequestParam` 배열
> **DB 트리거 영향도**: TPRICETB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## ⚠️ 서비스 핵심 NPE (00011과 동일 패턴)

```java
Map<String,Object> priceInfo = Hq_Master_00013_Mapper.getPriceInfo(map);

map.put("raiseFg" , priceInfo.get("RAISE_FG").toString());  // priceInfo null → NPE ★★★
map.put("prePrice", priceInfo.get("PRE_PRICE").toString());  // priceInfo null → NPE ★★★
```

**00011(판매가)과의 차이점**: 컨트롤러에서 `startDate.replaceAll("-","")` 호출 **없음** → 하이픈 형태 그대로 Mapper 전달 가능 ★

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 |
|---------|---------|
| `chainNo` | `C001` |
| `chainMsNo` | `NC0001` |
| `ID` | `7249525SHOP` |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 상품 목록 조회 (페이징) | `@RequestBody` | `Map` (total+rows) | SELECT | TGOODSTB<br>TPRICETB |
| 2 | `/saveGoodsPrice` | 원가 일괄 변경 (insert/update 분기) | `@RequestParam` 배열 | `void` | TGOODSTB<br>TPRICETB |

---

## 1. `/search` — 상품 조회

**★ offset 미전달**: `(int)map.get("offset")` → **NPE** ★★★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"offset":0,"limit":10}` | 상품 목록 + total |
| 1-2 | (동일) | `{"offset":0,"limit":10,"selectGoodsNm":"커피"}` | 상품명 필터 |
| 1-3 | (동일) | `{}` (offset 없음) | **NPE** ★★★ |
| 1-4 | - | (Body 없음) | 400 |

---

## 2. `/saveGoodsPrice` — 원가 변경 저장

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | 세션 전체 | `startDate=20260526&goodsCd_arr[]=G001&price_arr[]=1500` | insert 또는 update → void |
| 2-2 | (동일) | `startDate=2026-05-26` (하이픈 형태) | replaceAll 없음 → DB 형식 불일치 가능 ★ |
| 2-3 | (동일) | goodsCd_arr[] 2개, price_arr[] 1개 | **ArrayIndexOutOfBoundsException** ★★★ |
| 2-4 | (동일) | 원가 정보 없는 goodsCd | `priceInfo null` → **NPE** ★★★ |
| 2-5 | (동일) | `goodsCd_arr` 미전달 (defaultValue="") | `[""]` → 빈 문자열 루프 1회 |
| 2-6 | - | `startDate` 없음 | 400 (@NotBlank) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00013"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-3. offset 없음 → NPE
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session -Body '{}'

# 2-1. 원가 저장 정상
Invoke-RestMethod -Uri "$base/saveGoodsPrice" -Method POST -ContentType $f -WebSession $session `
  -Body "startDate=20260526&goodsCd_arr[]=G001&price_arr[]=1500"

# 2-2. 하이픈 날짜 → DB 형식 불일치 확인
Invoke-RestMethod -Uri "$base/saveGoodsPrice" -Method POST -ContentType $f -WebSession $session `
  -Body "startDate=2026-05-26&goodsCd_arr[]=G001&price_arr[]=1500"

# 2-3. 배열 불일치 → 500
Invoke-RestMethod -Uri "$base/saveGoodsPrice" -Method POST -ContentType $f -WebSession $session `
  -Body "startDate=20260526&goodsCd_arr[]=G001&goodsCd_arr[]=G002&price_arr[]=1500"
```

---

## 주요 검증 포인트

```
□ search — offset 미전달 → NPE ★★★
□ saveGoodsPrice — getPriceInfo null → NPE ★★★
□ saveGoodsPrice — price_arr 길이 < goodsCd_arr.length → ArrayIndexOutOfBoundsException ★★★
□ saveGoodsPrice — startDate replaceAll 미적용 → 하이픈 형태 DB 전달 ★ (00011 대비 차이점)
□ @Transactional rollbackFor Exception — 루프 중 예외 시 전체 rollback
□ chain_no (언더스코어) vs chainNo — Mapper SQL alias 정합성 확인
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/search` | ✅ SELECT |
| `/saveGoodsPrice` | ✅ INSERT |

### 소스 확인 사항

**소스 73번**: `(int)map.get("offset")` — offset null → **NPE** (TC 1-3 ✅ 정확)

**소스 72번**: `commandMap.put("chain_no", chain_no)` — `chain_no` 언더스코어 사용 (00011의 `chainNo`와 다름)  
→ Mapper SQL에서 `#{chain_no}` 파라미터 바인딩 정합성 확인 필요 ★

**소스 103~122번**: `startDate.replaceAll("-","")` **없음** ✅ 확정  
→ `startDate=2026-05-26` 그대로 Mapper 전달 → DB DATE 비교 형식 불일치 위험 (TC 2-2 ✅ 정확)

**소스 115번**: `price_arr[i]` — `price_arr.length < goodsCd_arr.length` 시 **ArrayIndexOutOfBoundsException** (TC 2-3 ✅ 정확)

**소스 100~101번**: `goodsCd_arr[]`, `price_arr[]` — `defaultValue=""` → 미전송 시 `[""]` → 루프 1회 실행 (TC 2-5 ✅ 정확)


## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
└── [테이블] TPRICETB (CUD 작업)
    └── (Trigger) Tr_TPRICE_T01
```
