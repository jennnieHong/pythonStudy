# Hq_Esti_00003 — 견적요청서 일괄등록 단위 테스트케이스

> **화면**: [HQ] 견적관리 > 견적요청서 일괄등록  
> **URL Prefix**: `POST /backoffice/data/hq/estimate/hq_esti_00003`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}
> **DB 트리거 영향도**: TESFRVTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 (자동주입) |
| `ID` | `shopadmin` | 로그인 사용자 ID (자동주입) |

---

## 엔드포인트 목록 (5개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 견적요청서 목록 조회 | SELECT | TESFRHTB<br>TESFRVTB |
| 2 | `/vendorSearch` | 미대상 거래처 조회 | SELECT | TESFRVTB<br>TVNDRMTB |
| 3 | `/detailSearch` | 상세 조회 (상품+거래처+미대상 3종 동시) | SELECT | TESFRHTB<br>TESFRVTB<br>TVNDRMTB |
| 4 | `/save` | 거래처 일괄 등록 (vendorArr 배열) | INSERT | TESFRVTB |
|5|`/delete`|거래처 일괄 삭제 (masterArr 배열)|DELETE| 공통 모듈/동적 쿼리 (추적 불가) |

---

## 1. `/search` — 견적요청서 목록 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{}` | 견적요청서 List |
| 1-2 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001"}` | 특정 유형/양식 필터 결과 |
| 1-3 | chainNo=`C001` (등록 없음) | `{}` | `[]` |
| 1-4 | 세션 없음 | `{}` | 302 redirect |

---

## 2. `/vendorSearch` — 미대상 거래처 조회

**서비스 로직**: `getVendorList()` — 해당 견적요청서에 아직 등록되지 않은 거래처 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001"}` | 미등록 거래처 List |
| 2-2 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001"}` (모두 등록됨) | `[]` |
| 2-3 | chainNo=`C001` | `{}` | chainNo 조건만 적용된 전체 거래처 |
| 2-4 | vendorSearch 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 3. `/detailSearch` — 상세 조회 (3종 동시)

**서비스 로직**: 단일 commandMap으로 3개 서비스 동시 호출
```
getDetailGoodsList(commandMap) → goodsList
getDetailVendorList(commandMap) → vendorList
getVendorList(commandMap)      → detailList (미대상 거래처)

returnMap = {
  "goodsList"  : [...],
  "vendorList" : [...],
  "detailList" : [...]
}
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001"}` | `{"goodsList":[...],"vendorList":[...],"detailList":[...]}` 3키 모두 존재 |
| 3-2 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001"}` (상품/거래처 없음) | `{"goodsList":[],"vendorList":[],"detailList":[...]}` |
| 3-3 | chainNo=`C001` | `{}` | 3종 모두 chainNo 조건만으로 조회 |
| 3-4 | detailSearch 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |
| 3-5 | vendorList vs detailList 분리 | 동일 요청 반복 조회 | `vendorList` ≠ `detailList` (중복 없이 분리) ★ |

---

## 4. `/save` — 거래처 일괄 등록

**서비스 로직**: `vendorArr` 배열 → 각 거래처 건별 `insertEstiMaster`

```
vendorArr 배열 반복 (j)
  vendorMap에 chainNo, userId 주입
  → insertEstiMaster(vendorMap)
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`, ID=`shopadmin` | `{"vendorArr":[{"vendorCd":"V001","estimTypeCd":"E001","estimFromCd":"F001"}]}` | 1건 INSERT |
| 4-2 | chainNo=`C001`, ID=`shopadmin` | `{"vendorArr":[{"vendorCd":"V001"},{"vendorCd":"V002"},{"vendorCd":"V003"}]}` | 3건 각각 INSERT |
| 4-3 | chainNo=`C001` | `{"vendorArr":[]}` | 반복 없음, 정상 종료 (void) |
| 4-4 | chainNo=`C001` | `{}` (vendorArr 없음) | **NPE** (null cast) |
| 4-5 | - | @Transactional: 2번째 INSERT 중 오류 | 1번째 INSERT 롤백 |
| 4-6 | save 성공 응답 | 정상 등록 | HTTP 200 + 빈 바디 ★ |

---

## 5. `/delete` — 거래처 일괄 삭제

**서비스 로직**: `masterArr` 배열 → 각 건별 `deleteEstiVendor`

```
masterArr 배열 반복 (i)
  map에 chainNo 주입
  → deleteEstiVendor(map)
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | chainNo=`C001` | `{"masterArr":[{"vendorCd":"V001","estimTypeCd":"E001","estimFromCd":"F001"}]}` | 1건 DELETE |
| 5-2 | chainNo=`C001` | `{"masterArr":[{"vendorCd":"V001"},{"vendorCd":"V002"}]}` | 2건 각각 DELETE |
| 5-3 | chainNo=`C001` | `{"masterArr":[]}` | 반복 없음, 정상 종료 |
| 5-4 | chainNo=`C001` | `{}` (masterArr 없음) | **NPE** (null cast) |
| 5-5 | chainNo=`C001` | `{"masterArr":[{"vendorCd":"XXXXX"}]}` | 0건 DELETE, 오류 없음 (void) |
| 5-6 | - | @Transactional: DELETE 중 오류 | 이전 건 롤백 |
| 5-7 | delete 성공 응답 | 정상 삭제 | HTTP 200 + 빈 바디 ★ |

---

## 서비스 핵심 분기 요약

```
detailSearch (3종 동시 조회)
└── 동일 commandMap으로 3개 Mapper 호출
    getDetailGoodsList + getDetailVendorList + getVendorList
    → returnMap { goodsList, vendorList, detailList }

save (거래처 일괄 등록)
└── vendorArr 배열 순회 → 건별 insertEstiMaster
    주의: vendorArr 없으면 NPE

delete (거래처 일괄 삭제)
└── masterArr 배열 순회 → 건별 deleteEstiVendor
    주의: masterArr 없으면 NPE
```

---

## Hq_Esti 시리즈 비교

| 화면 | 마스터 코드 | 등록 단위 | 특이사항 |
|------|-----------|----------|---------|
| Hq_Esti_00001 | `estimTypeCd` | 상품 개별(`goodsCd_arr`) | 전체등록(`goodsSaveAll`) |
| Hq_Esti_00002 | `estimFromCd` | 상품 Map배열(`goodsArr`) | 복사(`estimFromCp`), 엑셀 업로드 |
| Hq_Esti_00003 | — | **거래처 배열(`vendorArr`)** | 3종 동시 조회(`detailSearch`) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/estimate/hq_esti_00003"
$h = @{"Content-Type"="application/json"}

# 1. 견적요청서 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Body '{}' -Headers $h -WebSession $session

# 2. 미대상 거래처 조회
Invoke-RestMethod -Uri "$base/vendorSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","estimFromCd":"F001"}'

# 3. 상세 조회 (3종 동시)
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","estimFromCd":"F001"}'
# 예상: {"goodsList":[...],"vendorList":[...],"detailList":[...]}

# 4-1. 거래처 1건 등록
Invoke-RestMethod -Uri "$base/save" -Method POST -Headers $h -WebSession $session `
  -Body '{"vendorArr":[{"vendorCd":"V001","estimTypeCd":"E001","estimFromCd":"F001"}]}'

# 4-2. 거래처 다건 등록
Invoke-RestMethod -Uri "$base/save" -Method POST -Headers $h -WebSession $session `
  -Body '{"vendorArr":[{"vendorCd":"V002","estimTypeCd":"E001","estimFromCd":"F001"},{"vendorCd":"V003","estimTypeCd":"E001","estimFromCd":"F001"}]}'

# 5-1. 거래처 1건 삭제
Invoke-RestMethod -Uri "$base/delete" -Method POST -Headers $h -WebSession $session `
  -Body '{"masterArr":[{"vendorCd":"V001","estimTypeCd":"E001","estimFromCd":"F001"}]}'

# 4-NPE. vendorArr 미포함 NPE 테스트
Invoke-RestMethod -Uri "$base/save" -Method POST -Body '{}' -Headers $h -WebSession $session
# 예상: 500 (NPE)
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `HESTIMASTTB` | 견적요청서 마스터 (estimTypeCd=E001, estimFromCd=F001) |
| `HESTIGOODSTB` | 견적 대상 상품 |
| `HESTIVNDRTB` | 거래처 등록 데이터 (V001, V002 등) |
| `MVNDRSTB` | 거래처 마스터 |
| `MMCHATB` | chainNo=C001 |

---

## 주요 검증 포인트

```
□ detailSearch — 3종(goodsList, vendorList, detailList) 응답 키 모두 존재 확인
□ detailSearch — vendorList(등록된 거래처) vs detailList(미등록 거래처) 중복 없이 분리 확인
□ save — vendorArr 없을 시 NPE → 500 발생
□ delete — masterArr 없을 시 NPE → 500 발생
□ save @Transactional — 다건 중 중간 실패 시 전체 롤백
□ delete @Transactional — 다건 중 중간 실패 시 전체 롤백
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
└── [테이블] TESFRVTB (CUD 작업)
    └── (Trigger) Tr_TESFRV_T01
```
