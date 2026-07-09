# Hq_Master_00014 — 본사 원가 변경 현황 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > 가격관리 > 원가 변경 현황  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00014`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **구조 특이사항**: Hq_Master_00012(판매가 변경 현황)와 구조 완전 동일 — 원가(usuprice) 버전  
> **요청 방식**: `/searchChangeList` = `@RequestBody` JSON
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | searchChangeList |

---

## 엔드포인트 목록 (1개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/searchChangeList` | 원가 변경내역 조회 (페이징, goodsCdArr 조건 분기) | `@RequestBody` | `Map` (total+rows) | SELECT | TPRICETB |

---

## 1. `/searchChangeList` — 원가 변경내역 조회

**핵심 분기 (소스 64번 — 00012와 동일 패턴)**:
```java
if(!map.get("goodsCdArr").equals("ALL") && !(map.get("goodsCdArr").toString().trim()).isEmpty()) {
    String[] array = map.get("goodsCdArr").toString().split(",");
    commandMap.put("goodsCdList", array);
}
```

**★★★ `goodsCdArr` null 시 NPE** — `null.equals("ALL")` → **NullPointerException**  
**★★★ `offset` null 시 NPE** — `(int)null` → **NullPointerException**

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"offset":0,"limit":10,"goodsCdArr":"ALL"}` | 전체 원가 변경내역 (total+rows) |
| 1-2 | chainNo=`C001` | `{"offset":0,"limit":10,"goodsCdArr":"G001,G002"}` | `["G001","G002"]` IN 조건 조회 |
| 1-3 | chainNo=`C001` | `{"offset":0,"limit":10,"goodsCdArr":"   "}` (공백) | `trim().isEmpty()=true` → goodsCdList 미설정 → 전체 조회 |
| 1-4 | chainNo=`C001` | `{"offset":0,"limit":10}` (goodsCdArr 없음) | `null.equals("ALL")` → **NPE** ★★★ |
| 1-5 | chainNo=`C001` | `{"goodsCdArr":"ALL"}` (offset 없음) | `(int)null` → **NPE** ★★★ |
| 1-6 | chainNo=`C001` | `{"offset":0,"limit":10,"goodsCdArr":"ALL","searchFromDate":"20260101","searchEndDate":"20260531"}` | 기간 필터 결과 |
| 1-7 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00014"
$h = @{"Content-Type"="application/json"}

# 1-1. 전체 조회
Invoke-RestMethod -Uri "$base/searchChangeList" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10,"goodsCdArr":"ALL"}'

# 1-2. 상품코드 필터 조회
Invoke-RestMethod -Uri "$base/searchChangeList" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10,"goodsCdArr":"G001,G002"}'

# 1-4. goodsCdArr 없음 → NPE
Invoke-RestMethod -Uri "$base/searchChangeList" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'
# 예상: 500 NullPointerException

# 1-5. offset 없음 → NPE
Invoke-RestMethod -Uri "$base/searchChangeList" -Method POST -Headers $h -WebSession $session `
  -Body '{"goodsCdArr":"ALL"}'
# 예상: 500 NullPointerException
```

---

## 주요 검증 포인트

```
□ goodsCdArr 미전달 → null.equals("ALL") → NPE ★★★ (TC 1-4)
□ offset 미전달 → (int)null → NPE ★★★ (TC 1-5)
□ goodsCdArr="ALL" → goodsCdList 미설정 → 전체 조회 확인
□ goodsCdArr="G001,G002" → split(",") → IN 조건 쿼리 확인
□ @ServiceLog SELECT 정상 등록 ✅
□ @Transactional — SELECT only, 실질 rollback 대상 없음
□ 00012(판매가 변경 현황)와 로직 동일 — 동일 패턴 버그 공유
```

---

## ✅ v2 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/searchChangeList` | ✅ SELECT |

### 소스 확인 사항 (00012와 동일 패턴)

**소스 64번**: `map.get("goodsCdArr")` null 체크 없이 `.equals()` 호출 → **goodsCdArr 미전송 시 NPE** ★★★  
**소스 75번**: `(int)map.get("offset")` — offset null → unboxing NPE ★★★  
**메서드명**: `SearchChangeList` (대문자 S) — 소스 57번, Java 컨벤션 위반이나 Spring MVC URL 매핑에는 영향 없음  
**엔드포인트 수**: 소스 기준 1개 ✅
