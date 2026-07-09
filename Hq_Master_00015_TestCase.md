# Hq_Master_00015 — 본사 거래처 관리 단위 테스트케이스

> **화면**: [HQ] 마스터관리 > 거래처 관리  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00015`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식**: 전 엔드포인트 `@RequestBody` JSON  
> **⚠️ 클래스 레벨 `@Validated` 없음** — Bean Validation(`@NotBlank`, `@Size` 등) 미동작 ★
> **DB 트리거 영향도**: TVNDRMTB, TVNDRGTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | 전체 |
| `chainHqYn` | `Y` | searchVendorGoods |
| `ID` | `7249525SHOP` | regiVendorGoods |

---

## 엔드포인트 목록 (6개)

| # | URL | 기능 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/searchHqVendor` | 거래처 목록 조회 (필터 조건 포함) | `List` | SELECT | TVNDRMTB |
| 2 | `/searchHqVendorDetail` | 거래처 상세 정보 조회 | `List` | SELECT | TVNDRMTB |
| 3 | `/updateHqVendor` | 거래처 수정 (containsKey 방어 처리) | `String` | UPDATE | TVNDRMTB |
| 4 | `/searchVendorGoods` | 거래처 상품 조회 (등록/미등록 분리) | `Map` | SELECT | TMSCLSTB<br>TVNDRGTB |
| 5 | `/regiVendorGoods` | 거래처 상품 추가 (중복 체크 후 insert) | `String` | INSERT | TVNDRGTB |
| 6 | `/removeVendorGoods` | 거래처 상품 삭제 (배열 루프) | `void` | DELETE | TVNDRGTB |

---

## 1. `/searchHqVendor` — 거래처 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{}` | 전체 거래처 목록 |
| 1-2 | chainNo=`C001` | `{"vendor":"테스트거래처","vendorFg":"1"}` | 필터 결과 |
| 1-3 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 2. `/searchHqVendorDetail` — 거래처 상세 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"vendor":"V001"}` | 해당 거래처 상세 정보 List |
| 2-2 | chainNo=`C001` | `{}` | vendor null → Mapper WHERE 조건 미적용 → 전체 또는 빈 List |

---

## 3. `/updateHqVendor` — 거래처 수정

**`reqMap.containsKey()` 삼항 처리** (소스 123~136번):
- `telNo`, `faxNo`, `zipNo`, `bsAddr`, `bsAddrBunji`, `accountNm`, `bankCd`, `accountNo`, `remark` — 키 미존재 시 `""` 적용 ✅ null 안전

**미보호 필드** (containsKey 없이 직접 `reqMap.get()` 사용):
- `erpIfInfo`, `contactPsNm`, `contactPhoneNo`, `email`, `hpNo`, `contactTelNo` → null 가능하나 Mapper에서 null 허용 시 정상

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"erpIfInfo":"ERP001","contactPsNm":"홍길동","contactPhoneNo":"010-1234-5678","email":"test@test.com","hpNo":"01012345678","contactTelNo":"02-1234-5678"}` | 수정 성공 → `String` 반환 |
| 3-2 | chainNo=`C001` | `{}` (telNo 등 선택 필드 없음) | containsKey 삼항 → `""` 적용 → 수정 성공 |
| 3-3 | - | (Body 없음) | 400 |

---

## 4. `/searchVendorGoods` — 거래처 상품 조회

**반환**: `{"notVendorGoodsList":[...], "vendorGoodsList":[...]}`

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`, chainHqYn=`Y` | `{"vendor":"V001"}` | notVendorGoodsList + vendorGoodsList |
| 4-2 | chainNo=`C001`, chainHqYn=`N` | `{"vendor":"V001"}` | chainHqYn=N 분기 결과 확인 |
| 4-3 | - | (Body 없음) | 400 |

---

## 5. `/regiVendorGoods` — 거래처 상품 추가

**처리 흐름**:
```
addGoodsCdArr 루프:
  selectChkDuplAddGoodsChain() → "0" 아니면 dupFg="dup" → break
  "0" 이면 insertVendorGoodsChain()
→ dupFg="dup" → "dupVendorGoods"
→ 그 외    → "insertVendorGoods"
```

**★★★ `addGoodsCdArr` 미전달/null 시 NPE**: `null.size()` → **NullPointerException**  
**★ 중복 첫 건 발견 시 즉시 break** — 이후 상품은 insert되지 않음

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | chainNo=`C001`, ID=`7249525SHOP` | `{"vendor":"V001","addGoodsCdArr":["G001","G002"]}` | 중복 없으면 `"insertVendorGoods"` |
| 5-2 | (동일) | `{"vendor":"V001","addGoodsCdArr":["G001"]}` (이미 등록된 G001) | `"dupVendorGoods"` |
| 5-3 | (동일) | `{"vendor":"V001","addGoodsCdArr":["G001","G002"]}` (G001 중복) | G001에서 break → G002 미처리, `"dupVendorGoods"` ★ |
| 5-4 | (동일) | `{"vendor":"V001"}` (addGoodsCdArr 없음) | `null.size()` → **NPE** ★★★ |
| 5-5 | (동일) | `{"vendor":"V001","addGoodsCdArr":[]}` (빈 배열) | 루프 0회 → `"insertVendorGoods"` |
| 5-6 | - | (Body 없음) | 400 |

---

## 6. `/removeVendorGoods` — 거래처 상품 삭제

**★★★ `removeGoodsCdArr` 미전달/null 시 NPE**: `null.size()` → **NullPointerException**  
**반환**: `void` — HTTP 200 + 빈 바디

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 6-1 | chainNo=`C001` | `{"vendor":"V001","removeGoodsCdArr":["G001"]}` | 삭제 성공 → `void` (HTTP 200) |
| 6-2 | (동일) | `{"vendor":"V001","removeGoodsCdArr":["G001","G002"]}` | 2건 순차 삭제 |
| 6-3 | (동일) | `{"vendor":"V001"}` (removeGoodsCdArr 없음) | `null.size()` → **NPE** ★★★ |
| 6-4 | (동일) | `{"vendor":"V001","removeGoodsCdArr":[]}` (빈 배열) | 루프 0회 → 정상 (HTTP 200) |
| 6-5 | - | (Body 없음) | 400 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00015"
$h = @{"Content-Type"="application/json"}

# 1-1. 거래처 전체 조회
Invoke-RestMethod -Uri "$base/searchHqVendor" -Method POST -Headers $h -WebSession $session `
  -Body '{}'

# 4-1. 거래처 상품 조회
Invoke-RestMethod -Uri "$base/searchVendorGoods" -Method POST -Headers $h -WebSession $session `
  -Body '{"vendor":"V001"}'

# 5-1. 상품 추가 (정상)
Invoke-RestMethod -Uri "$base/regiVendorGoods" -Method POST -Headers $h -WebSession $session `
  -Body '{"vendor":"V001","addGoodsCdArr":["G001","G002"]}'
# 예상: "insertVendorGoods"

# 5-4. addGoodsCdArr 없음 → NPE
Invoke-RestMethod -Uri "$base/regiVendorGoods" -Method POST -Headers $h -WebSession $session `
  -Body '{"vendor":"V001"}'
# 예상: 500 NullPointerException

# 6-1. 상품 삭제
Invoke-RestMethod -Uri "$base/removeVendorGoods" -Method POST -Headers $h -WebSession $session `
  -Body '{"vendor":"V001","removeGoodsCdArr":["G001"]}'
# 예상: HTTP 200 빈 바디

# 6-3. removeGoodsCdArr 없음 → NPE
Invoke-RestMethod -Uri "$base/removeVendorGoods" -Method POST -Headers $h -WebSession $session `
  -Body '{"vendor":"V001"}'
# 예상: 500 NullPointerException
```

---

## 주요 검증 포인트

```
□ @Validated 클래스 레벨 없음 → Bean Validation 미동작 ★ (@RequestBody 파라미터에 @NotBlank 등 적용 불가)
□ regiVendorGoods — addGoodsCdArr null → null.size() → NPE ★★★
□ removeVendorGoods — removeGoodsCdArr null → null.size() → NPE ★★★
□ regiVendorGoods — 중복 첫 건 발견 시 break → 이후 상품 미처리 (부분 삽입 발생 가능) ★
□ updateHqVendor — containsKey 삼항 처리 → 선택 필드 null 안전 ✅
□ removeVendorGoods 반환 void → HTTP 200 + 빈 바디
□ searchVendorGoods — chainHqYn 세션 값 → Mapper 분기 확인
□ @Transactional rollbackFor Exception — regiVendorGoods/removeVendorGoods 루프 내 예외 시 rollback 여부
```


## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] TVNDRGTB (CUD 작업)
│   └── (Trigger) Tr_TVNDRG_T01
└── [테이블] TVNDRMTB (CUD 작업)
    └── (Trigger) Tr_TVNDRM_T01
```
