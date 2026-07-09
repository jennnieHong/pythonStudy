# Hq_Esti_00001 — 견적유형 마스터 단위 테스트케이스

> **화면**: [HQ] 견적관리 > 견적유형 마스터  
> **URL Prefix**: `POST /backoffice/data/hq/estimate/hq_esti_00001`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}
> **DB 트리거 영향도**: TGOODSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 (자동주입) |
| `ID` | `shopadmin` | 로그인 사용자 ID (자동주입) |

---

## 엔드포인트 목록 (8개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 견적유형 목록 조회 | SELECT | TESTYMTB |
| 2 | `/detailSearch` | 견적유형별 대상 상품 조회 | SELECT | TESTYMTB |
| 3 | `/goodsSearch` | 등록 가능 상품 조회 (페이징) | SELECT | TESTYGTB<br>TGOODSTB |
| 4 | `/save` | 견적유형 등록/수정 (estimTypeCd 분기) | TESTYMTB |
|5|`/delete`|견적유형 삭제 (배열, 연쇄 삭제)|DELETE| 공통 모듈/동적 쿼리 (추적 불가) |
| 6 | `/goodsSave` | 대상 상품 개별 등록 (배열) | INSERT | TESTYGTB |
| 7 | `/goodsSaveAll` | 대상 상품 전체 등록 | INSERT | TESTYGTB<br>TGOODSTB |
|8|`/goodsDelete`|대상 상품 삭제 (배열)|DELETE| 공통 모듈/동적 쿼리 (추적 불가) |

---

## 1. `/search` — 견적유형 목록 조회

**서비스 로직**: 세션 chainNo → `getList()` 단순 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{}` | 견적유형 List |
| 1-2 | chainNo=`C001` | `{"searchNm":"배달"}` | 이름 필터 결과 |
| 1-3 | chainNo=`C001` (등록 없음) | `{}` | `[]` |
| 1-4 | 세션 없음 | `{}` | 302 redirect |

---

## 2. `/detailSearch` — 견적유형 대상 상품 조회

**서비스 로직**: `getDetailList()` — estimTypeCd 기준 상품 목록

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"estimTypeCd":"E001"}` | 해당 견적유형 대상 상품 List |
| 2-2 | chainNo=`C001` | `{"estimTypeCd":"XXXXX"}` (미존재) | `[]` |
| 2-3 | chainNo=`C001` | `{}` (estimTypeCd 없음) | 전체 또는 `[]` (쿼리 조건 확인) |

---

## 3. `/goodsSearch` — 등록 가능 상품 조회 (페이징)

**서비스 로직**: offset/limit → startCount/endCount 변환 → `getGoodsList()` + `getTotalCnt()`

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"offset":0,"limit":10}` | `{"total":N,"rows":[...]}` |
| 3-2 | chainNo=`C001` | `{"offset":10,"limit":10}` | startCount=11, endCount=20 |
| 3-3 | chainNo=`C001` | `{"offset":0,"limit":10,"goodsNm":"아메리카노"}` | 상품명 필터 결과 |
| 3-4 | chainNo=`C001` | `{"limit":10}` (offset 없음) | ClassCastException/NPE → 500 |
| 3-5 | goodsSearch 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |
| 3-6 | limit 키 누락 | `{"offset":0}` | 112번 `(int)commandMap.get("limit")` → **NPE → 500** ★ |

---

## 4. `/save` — 견적유형 등록/수정

**서비스 분기: estimTypeCd 비어있음 여부**
```
estimTypeCd == "" → 신규 등록
  └── getNewTypeCd() → 자동채번 → insertEstiMaster()
estimTypeCd != "" → 수정
  └── updateEstiMaster()
반환: commandMap 자체 (저장된 파라미터 전부)
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`, ID=`shopadmin` | `{"estimTypeCd":"","estimTypeNm":"배달견적","useYn":"Y"}` | 신규 등록, 자동채번 코드 포함한 commandMap 반환 |
| 4-2 | chainNo=`C001`, ID=`shopadmin` | `{"estimTypeCd":"E001","estimTypeNm":"배달견적(수정)","useYn":"Y"}` | 수정, commandMap 반환 |
| 4-3 | chainNo=`C001` | `{}` (estimTypeCd 키 없음) | `param.get("estimTypeCd").toString()` → **NPE 발생** |
| 4-4 | chainNo=`C001` | `{"estimTypeCd":null}` | `null.toString()` → **NPE 발생** |
| 4-5 | ID=`shopadmin` | 정상 신규 후 목록 재조회 | `getNewTypeCd()` 채번 결과 DB 저장 확인 |
| 4-6 | - | @Transactional: insertEstiMaster 오류 | 롤백 |
| 4-7 | save 수정 시 감사 로그 타입 | estimTypeCd 있는 수정 호출 후 MMSLOGTB 확인 | INSERT 타입으로 기록됨 (UPDATE가 아님) ★ |

---

## 5. `/delete` — 견적유형 삭제 (배열, 연쇄)

**서비스 로직**: `masterArr` 배열 순회 → 각 건에 `deleteEstiMaster` + `deleteEstiGoods` 연쇄 삭제

```
masterArr 배열 반복 (i)
  각 map에 chainNo 주입
  → deleteEstiMaster(map)   (견적유형 본체)
  → deleteEstiGoods(map)    (해당 유형의 대상상품 전체)
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | chainNo=`C001` | `{"masterArr":[{"estimTypeCd":"E001"}]}` | E001 본체 + 대상상품 모두 삭제 |
| 5-2 | chainNo=`C001` | `{"masterArr":[{"estimTypeCd":"E001"},{"estimTypeCd":"E002"}]}` | 2건 연쇄 삭제 |
| 5-3 | chainNo=`C001` | `{"masterArr":[]}` (빈 배열) | 반복 없음, 정상 종료 (void) |
| 5-4 | chainNo=`C001` | `{"masterArr":[{"estimTypeCd":"XXXXX"}]}` | deleteEstiMaster 0건, deleteEstiGoods 0건 (오류 없음) |
| 5-5 | - | @Transactional: deleteEstiGoods 오류 | deleteEstiMaster도 롤백 |
| 5-6 | delete 성공 응답 | 정상 삭제 | HTTP 200 + 빈 바디 (null) ★ |

---

## 6. `/goodsSave` — 대상 상품 개별 등록 (배열)

**서비스 로직**: `goodsCd_arr` 배열 순회 → 각 상품 건별 `insertEstiGoods`

```
goodsCd_arr 배열 반복 (i)
  map = { chainNo, estimTypeCd, estimGoodsCd: goodsCd_arr[i], userId }
  → insertEstiGoods(map)
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 6-1 | chainNo=`C001`, ID=`shopadmin` | `{"estimTypeCd":"E001","goodsCd_arr":["G001"]}` | 1건 INSERT |
| 6-2 | chainNo=`C001`, ID=`shopadmin` | `{"estimTypeCd":"E001","goodsCd_arr":["G001","G002","G003"]}` | 3건 각각 INSERT |
| 6-3 | chainNo=`C001` | `{"estimTypeCd":"E001","goodsCd_arr":[]}` | 반복 없음, 정상 종료 |
| 6-4 | chainNo=`C001` | `{"estimTypeCd":"E001"}` (goodsCd_arr 없음) | `param.get("goodsCd_arr")` null → **NullPointerException** |
| 6-5 | - | @Transactional: 2번째 INSERT 오류 | 1번째 INSERT도 롤백 |
| 6-6 | goodsSave 성공 응답 | 정상 등록 | HTTP 200 + 빈 바디 ★ |

---

## 7. `/goodsSaveAll` — 대상 상품 전체 등록

**서비스 로직**: 배열 반복 없이 `insertEstiAllGoods()` 단일 호출 (Mapper에서 전체 처리)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 7-1 | chainNo=`C001`, ID=`shopadmin` | `{"estimTypeCd":"E001"}` | 해당 체인 전체 상품 일괄 INSERT |
| 7-2 | chainNo=`C001` | `{"estimTypeCd":"E001"}` (이미 전체 등록됨) | 중복 키 오류 또는 MERGE 처리 확인 |
| 7-3 | - | `{}` (estimTypeCd 없음) | 쿼리 조건 누락으로 전체 등록 가능성 확인 |
| 7-4 | goodsSaveAll 성공 응답 | 정상 등록 | HTTP 200 + 빈 바디 ★ |

---

## 8. `/goodsDelete` — 대상 상품 삭제 (배열)

**서비스 로직**: `goodsCd_arr` 배열 순회 → 각 건별 `deleteEstiGoods`

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 8-1 | chainNo=`C001` | `{"estimTypeCd":"E001","goodsCd_arr":["G001"]}` | 1건 DELETE |
| 8-2 | chainNo=`C001` | `{"estimTypeCd":"E001","goodsCd_arr":["G001","G002"]}` | 2건 각각 DELETE |
| 8-3 | chainNo=`C001` | `{"estimTypeCd":"E001","goodsCd_arr":[]}` | 반복 없음, 정상 종료 |
| 8-4 | chainNo=`C001` | `{"estimTypeCd":"E001"}` (goodsCd_arr 없음) | **NullPointerException** (goodsSave와 동일 위험) |
| 8-5 | chainNo=`C001` | 존재하지 않는 estimGoodsCd | 0건 DELETE, 오류 없음 |
| 8-6 | goodsDelete 성공 응답 | 정상 삭제 | HTTP 200 + 빈 바디 ★ |

---

## 서비스 핵심 분기 요약

```
save (견적유형 등록/수정)
├── estimTypeCd == "" → getNewTypeCd() + insertEstiMaster() (신규)
└── estimTypeCd != "" → updateEstiMaster() (수정)
주의: estimTypeCd 키 없거나 null → NPE 발생

delete (연쇄 삭제)
└── masterArr 배열 순회: deleteEstiMaster + deleteEstiGoods (건별)

goodsSave / goodsDelete
└── goodsCd_arr 배열 순회: 건별 INSERT/DELETE
주의: goodsCd_arr 키 없으면 null → NPE 발생

goodsSaveAll
└── 배열 없이 insertEstiAllGoods 단일 호출 (Mapper에서 전체 처리)
```

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/estimate/hq_esti_00001"
$h = @{"Content-Type"="application/json"}

# 1. 견적유형 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Body '{}' -Headers $h -WebSession $session

# 4-1. 신규 등록 (estimTypeCd 빈값)
Invoke-RestMethod -Uri "$base/save" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"","estimTypeNm":"배달견적","useYn":"Y"}'
# 예상: 자동채번된 estimTypeCd 포함 commandMap 반환

# 4-2. 수정 (estimTypeCd 있음)
Invoke-RestMethod -Uri "$base/save" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","estimTypeNm":"배달견적(수정)","useYn":"Y"}'

# 2. 상세 조회
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001"}'

# 3. 상품 조회 (페이징)
Invoke-RestMethod -Uri "$base/goodsSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'

# 6. 대상 상품 개별 등록
Invoke-RestMethod -Uri "$base/goodsSave" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","goodsCd_arr":["G001","G002"]}'

# 7. 전체 상품 등록
Invoke-RestMethod -Uri "$base/goodsSaveAll" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001"}'

# 8. 대상 상품 삭제
Invoke-RestMethod -Uri "$base/goodsDelete" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","goodsCd_arr":["G001"]}'

# 5. 견적유형 삭제 (연쇄)
Invoke-RestMethod -Uri "$base/delete" -Method POST -Headers $h -WebSession $session `
  -Body '{"masterArr":[{"estimTypeCd":"E001"}]}'
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `HESTIMASTTB` | 견적유형 마스터 (E001 등) |
| `HESTIGOODSTB` | 견적유형 대상 상품 |
| `MGOODSTB` | 상품 목록 (goodsSearch 조회용) |
| `MMCHATB` | chainNo=C001 체인 마스터 |

---

## 주요 검증 포인트

```
□ save — estimTypeCd 키 자체가 없거나 null인 경우 NPE 방어 필요
□ goodsSave / goodsDelete — goodsCd_arr 키 없을 시 NPE 방어 필요
□ delete — masterArr 각 건에 deleteEstiMaster + deleteEstiGoods 순서 확인
□ goodsSaveAll — 이미 전체 등록된 경우 중복 처리 방식 확인 (INSERT vs MERGE)
□ goodsSearch — offset 키 없을 시 ClassCastException → 500 발생
□ save 반환값 — 저장된 commandMap 전체 반환 (estimTypeCd 포함 여부 확인)
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
└── [테이블] TGOODSTB (CUD 작업)
    └── (Trigger) Tr_TGOODS_T01
```
