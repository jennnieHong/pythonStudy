# Hq_Esti_00006 — 견적서 단가 결정관리 단위 테스트케이스

> **화면**: [HQ] 견적관리 > 견적서 단가 결정관리  
> **URL Prefix**: `POST /backoffice/data/hq/estimate/hq_esti_00006`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **오타 주의**: 엔드포인트명 `/applyPrcie` (Price 오타, 수정 불가)
> **DB 트리거 영향도**: TESFRHTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 (자동주입) |
| `ID` | `shopadmin` | 로그인 사용자 ID (자동주입) |

---

## 엔드포인트 목록 (3개)

| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/searchVendorCnt` | 견적 거래처 목록 조회 | SELECT | TESVDUTB |
| 2 | `/search` | 견적서 단가 내역 조회 (vendorList 선행 조회 후 IN 조건 적용) | SELECT | TESFRHTB<br>TESVDUTB |
| 3 | `/applyPrcie` | 최종 단가 확정 (dataArr 배열 + i==0 headerMap) | UPDATE | TESFRHTB<br>TESVDUTB |

---

## 1. `/searchVendorCnt` — 거래처 목록 조회

**서비스 로직**: `getVendorList()` → `{"vendorList":[...]}` 반환

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainNo=`C001` | 거래처 3건 존재 | `{"estimTypeCd":"E001","estimFromCd":"F001"}` | `{"vendorList":[V001, V002, V003]}` |
| 1-2 | chainNo=`C001` | 거래처 없음 | `{"estimTypeCd":"E001","estimFromCd":"F001"}` | `{"vendorList":[]}` |
| 1-3 | chainNo=`C001` | - | `{}` | chainNo 조건만, 전체 거래처 |
| 1-4 | 세션 없음 | - | `{}` | 302 redirect |
| 1-5 | searchVendorCnt 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 2. `/search` — 견적서 단가 내역 조회

**서비스 로직 (2단계)**:
```
1단계: getVendorList(param) → vendorList (거래처 목록)
2단계: param.put("vendorList", vendorList)   ← vendorList를 파라미터에 주입
3단계: getList(param) → Mapper에서 vendorList를 IN 조건으로 활용
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 2-1 | chainNo=`C001` | 거래처 V001/V002, 단가 데이터 존재 | `{"estimTypeCd":"E001","estimFromCd":"F001"}` | vendorList IN 조건 적용된 단가 내역 List |
| 2-2 | chainNo=`C001` | **거래처 없음** | `{"estimTypeCd":"E001","estimFromCd":"F001"}` | vendorList=[] → getList IN 조건이 빈 배열 → `[]` |
| 2-3 | chainNo=`C001` | 거래처 1건 존재 | `{}` | chainNo 조건만 적용 |

---

## 3. `/applyPrcie` — 최종 단가 확정

**서비스 로직 (핵심 분기)**:
```
dataArr 배열 순회 (i)
  → updateApplyPrice(map)     ← 상품별 단가 확정 UPDATE (매 건)

  if(i == 0) {                ← 첫 번째 건에서만
    headerMap 구성:
      chainNo, chainMsNo, userId
      estimTypeCd, estimFromCd  ← 첫 번째 건에서 추출
  }

→ updateHeader(headerMap)     ← 반복 종료 후 1회만 실행
```

**주의**: `estimTypeCd`, `estimFromCd`는 **첫 번째 배열 건(i=0)**에서만 추출 → 다건 처리 시 배열의 첫 항목 값 기준으로 헤더 UPDATE

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 3-1 | chainNo=`C001`, ID=`shopadmin` | G001 단가 미확정 | `{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimGoodsCd":"G001","applyPrice":5000}]}` | updateApplyPrice 1건 + updateHeader 1회 (headerMap estimTypeCd=E001) |
| 3-2 | chainNo=`C001` | G001, G002 미확정 | `{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimGoodsCd":"G001","applyPrice":5000},{"estimTypeCd":"E001","estimFromCd":"F001","estimGoodsCd":"G002","applyPrice":3000}]}` | updateApplyPrice 2건 + updateHeader 1회 (i==0 기준) |
| 3-3 | **i==0 estimTypeCd 누락** | - | `{"dataArr":[{"estimGoodsCd":"G001","applyPrice":5000},{"estimTypeCd":"E001","estimFromCd":"F001","estimGoodsCd":"G002"}]}` | headerMap에 estimTypeCd=null → updateHeader null 조건 |
| 3-4 | chainNo=`C001` | - | `{"dataArr":[]}` | updateApplyPrice 미실행, headerMap 빈 맵으로 updateHeader 실행 |
| 3-5 | chainNo=`C001` | - | `{}` (dataArr 없음) | **NPE** (null cast) |
| 3-6 | chainNo=`C001` | G001, G002 이미 확정됨 | 동일 RequestBody | 재확정 — 덮어쓰기 동작 확인 |
| 3-7 | - | - | @Transactional: updateApplyPrice 2번째 오류 | 1번째 + updateHeader 롤백 |
| 3-8 | applyPrcie 성공 응답 | 정상 처리 | HTTP 200 + 빈 바디 ★ |
| 3-9 | chainMsNo 실제 주입 경로 | applyPrcie 호출 후 Mapper SQL 확인 | 컨트롤러 미주입 → 서비스/Mapper 처리 방식 확인 ★ |

---

## 서비스 핵심 분기 요약

```
search (단가 내역 조회)
└── getVendorList() → vendorList 추출
    → param.put("vendorList", vendorList) 주입
    → getList() (vendorList IN 조건 적용)
    주의: vendorList=[] 일 때 IN 조건 처리 방식 확인

applyPrcie (단가 확정)
└── dataArr 배열 순회
    → updateApplyPrice() (매 건 실행)
    → i==0 일 때만 headerMap 구성
        (estimTypeCd, estimFromCd는 첫 번째 건에서만 추출)
→ updateHeader(headerMap) (1회만 실행, 배열 외부)

핵심 위험:
  dataArr 없으면 NPE
  dataArr 빈 배열([]) → headerMap 미구성 상태로 updateHeader 실행
  dataArr 첫 번째 건에 estimTypeCd 없으면 headerMap.get("estimTypeCd")=null
```

---

## Hq_Esti 시리즈 최종 비교

| 화면 | 기능 | 핵심 특이사항 |
|------|------|-------------|
| 00001 | 견적유형 마스터 | estimTypeCd 신규채번, NPE |
| 00002 | 견적양식 작성 | estimFromCp 복사, 엑셀 업로드 |
| 00003 | 요청서 일괄등록 | 3종 동시 조회, 거래처 배열 |
| 00004 | 전송관리 | printType 4분기, Tibero 메일 연동 |
| 00005 | 업로드 관리 | receipt/confirm 순서, goodsSave 재조회 반환 |
| **00006** | **단가 결정관리** | **search 2단계 조회, applyPrcie i==0 헤더** |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/estimate/hq_esti_00006"
$h = @{"Content-Type"="application/json"}

# 1. 거래처 목록 조회
Invoke-RestMethod -Uri "$base/searchVendorCnt" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","estimFromCd":"F001"}'
# 예상: {"vendorList":[...]}

# 2. 단가 내역 조회 (vendorList IN 조건)
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","estimFromCd":"F001"}'
# 예상: vendorList 선행조회 후 IN 조건 적용된 단가 List

# 3-1. 단가 확정 (1건)
Invoke-RestMethod -Uri "$base/applyPrcie" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimGoodsCd":"G001","applyPrice":5000}]}'
# 예상: updateApplyPrice 1건 + updateHeader 1회

# 3-2. 단가 확정 (다건)
Invoke-RestMethod -Uri "$base/applyPrcie" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimGoodsCd":"G001","applyPrice":5000},{"estimTypeCd":"E001","estimFromCd":"F001","estimGoodsCd":"G002","applyPrice":3000}]}'
# 예상: updateApplyPrice 2건 + updateHeader 1회 (첫번째 건 기준)

# 3-4. 빈 배열 테스트
Invoke-RestMethod -Uri "$base/applyPrcie" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[]}'
# 예상: updateHeader(빈 headerMap) 실행

# 3-5. dataArr 없음 NPE 테스트
Invoke-RestMethod -Uri "$base/applyPrcie" -Method POST -Body '{}' -Headers $h -WebSession $session
# 예상: 500 (NPE)
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `HESTIMASTTB` | 견적요청서 헤더 (E001/F001) |
| `HESTIGOODSTB` | 견적 대상 상품 + 단가 (G001, G002) |
| `HESTIVNDRTB` | 거래처 정보 (V001, V002) |
| `MMCHATB` | chainNo=C001 |

---

## 주요 검증 포인트

```
□ search — vendorList 선행조회 후 param에 주입 → getList IN 조건 확인
□ search — vendorList=[] 일 때 getList 쿼리의 IN([]) 처리 방식 (Oracle: IN에 빈 배열 오류 가능)
□ applyPrcie — 엔드포인트 오타 (/applyPrcie, Price 오타) 확인
□ applyPrcie — i==0 에서만 headerMap 구성 → 첫 번째 건 estimTypeCd/estimFromCd 기준
□ applyPrcie — dataArr=[] → updateHeader(빈 headerMap) 실행 → DB 영향 확인
□ applyPrcie — dataArr 없으면 NPE
□ @Transactional — updateApplyPrice 실패 시 updateHeader 미실행 (롤백)
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
└── [테이블] TESFRHTB (CUD 작업)
    ├── (Trigger) Tr_TESFRH_T01
    └── (Trigger) Tr_TESFRH_T02
```
