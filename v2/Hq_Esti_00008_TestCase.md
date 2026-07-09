# Hq_Esti_00008 — 계약 이월 단위 테스트케이스

> **화면**: [HQ] 견적관리 > 계약 이월  
> **URL Prefix**: `POST /backoffice/data/hq/estimate/hq_esti_00008`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}
> **DB 트리거 영향도**: TPRICETB, TESFRHTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 |
| `chainMsNo` | `NC0001` | 체인 본부 매장번호 |
| `ID` | `shopadmin` | 로그인 사용자 ID |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 계약 이월 대상 견적요청서 조회 | SELECT | TESHISTB<br>TESVDUTB |
| 2 | `/extendDate` | 계약 이월 처리 (배열 + i==0 headerMap) | TESHISTB<br>TESVDUTB<br>TPRICETB |

---

## 1. `/search` — 이월 대상 견적요청서 조회

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainNo=`C001` | 이월 대상 3건 존재 | `{}` | 이월 대상 List |
| 1-2 | chainNo=`C001` | - | `{"estimTypeCd":"E001","estimFromCd":"F001"}` | 유형/양식 필터 결과 |
| 1-3 | chainNo=`C001` | 이월 대상 없음 | `{}` | `[]` |
| 1-4 | 세션 없음 | - | `{}` | 302 redirect |

---

## 2. `/extendDate` — 계약 이월 처리

**서비스 로직 (applyPrcie와 동일 패턴, 더 많은 필드)**:
```
dataArr 배열 순회 (i)
  → insertExtendDate(map)          ← 이월 데이터 INSERT (매 건)
  → insertExtendDateHistory(map)   ← 이월 이력 INSERT (매 건)

  if(i == 0) {
    headerMap 구성:
      chainNo, chainMsNo, userId
      estimTypeCd, estimFromCd     ← 첫 번째 건에서만 추출
      extendFromDate               ← 이월 시작일 (첫 번째 건)
      extendEndDate                ← 이월 종료일 (첫 번째 건)
  }

→ updateHeader(headerMap)          ← 반복 종료 후 1회만
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 2-1 | chainNo=`C001`, chainMsNo=`NC0001`, ID=`shopadmin` | V001 이월 미처리 | `{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001","extendFromDate":"20260601","extendEndDate":"20260630"}]}` | insertExtendDate 1건 + insertExtendDateHistory 1건 + updateHeader 1회 |
| 2-2 | chainNo=`C001` | V001, V002 미처리 | `{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001","extendFromDate":"20260601","extendEndDate":"20260630"},{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V002","extendFromDate":"20260601","extendEndDate":"20260630"}]}` | insertExtendDate×2 + insertExtendDateHistory×2 + updateHeader 1회 (V001 기준) |
| 2-3 | chainNo=`C001` | V001 **이미 이월됨** | 동일 RequestBody | 중복 INSERT → 중복 키 오류 또는 허용 확인 |
| 2-4 | chainNo=`C001` | - | `{"dataArr":[{"estimVendorCd":"V001"}]}` (i=0, estimTypeCd 없음) | headerMap.estimTypeCd=null → updateHeader null 조건 주의 |
| 2-5 | chainNo=`C001` | - | `{"dataArr":[]}` | 반복 없음, 빈 headerMap으로 updateHeader 실행 |
| 2-6 | chainNo=`C001` | - | `{}` (dataArr 없음) | **NPE** (null cast) |
| 2-7 | - | - | @Transactional: insertExtendDateHistory 오류 | insertExtendDate + updateHeader 롤백 |

---

## 서비스 핵심 분기 요약

```
extendDate (계약 이월)
└── dataArr 배열 순회
    → insertExtendDate(map)        (매 건)
    → insertExtendDateHistory(map) (매 건, 이력 동시 INSERT)
    if(i==0) → headerMap 구성
      (estimTypeCd, estimFromCd, extendFromDate, extendEndDate)
→ updateHeader(headerMap)          (1회만)

Hq_Esti_00006 applyPrcie와 동일 패턴:
  차이: updateApplyPrice 1개 → insertExtendDate + insertExtendDateHistory 2개
  차이: headerMap에 extendFromDate, extendEndDate 추가
```

---

## Hq_Esti_00006 vs Hq_Esti_00008 비교

| 항목 | Hq_Esti_00006 (`applyPrcie`) | Hq_Esti_00008 (`extendDate`) |
|------|------------------------------|------------------------------|
| 배열 처리 | `updateApplyPrice` 1개 | `insertExtendDate` + `insertExtendDateHistory` 2개 |
| i==0 headerMap | `estimTypeCd`, `estimFromCd` | `estimTypeCd`, `estimFromCd`, `extendFromDate`, `extendEndDate` |
| header 마무리 | `updateHeader` | `updateHeader` |
| 세션 추가 키 | — | `chainMsNo` |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/estimate/hq_esti_00008"
$h = @{"Content-Type"="application/json"}

# 1. 이월 대상 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Body '{}' -Headers $h -WebSession $session

# 2-1. 이월 처리 (1건)
Invoke-RestMethod -Uri "$base/extendDate" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001","extendFromDate":"20260601","extendEndDate":"20260630"}]}'
# 예상: insertExtendDate×1 + insertExtendDateHistory×1 + updateHeader×1

# 2-2. 이월 처리 (다건)
Invoke-RestMethod -Uri "$base/extendDate" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001","extendFromDate":"20260601","extendEndDate":"20260630"},{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V002","extendFromDate":"20260601","extendEndDate":"20260630"}]}'
# 예상: insertExtendDate×2 + insertExtendDateHistory×2 + updateHeader×1 (V001 기준)

# 2-5. 빈 배열
Invoke-RestMethod -Uri "$base/extendDate" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[]}'
# 예상: 반복 없음, 빈 headerMap으로 updateHeader 실행 → DB 영향 확인

# 2-6. dataArr 없음 NPE
Invoke-RestMethod -Uri "$base/extendDate" -Method POST -Body '{}' -Headers $h -WebSession $session
# 예상: 500 (NPE)
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `HESTIMASTTB` | 견적요청서 헤더 (E001/F001) |
| `HESTIVNDRTB` | 거래처 데이터 (V001, V002) |
| `HESTIEXTENDTB` | 계약 이월 테이블 (insertExtendDate 대상) |
| `HESTIEXTENDHISTTB` | 이월 이력 테이블 (insertExtendDateHistory 대상) |
| `MMCHATB` | chainNo=C001, chainMsNo=NC0001 |

---

## 주요 검증 포인트

```
□ extendDate — 건별로 insertExtendDate + insertExtendDateHistory 쌍으로 실행 확인
□ extendDate — i==0 기준 headerMap (extendFromDate, extendEndDate 포함) → updateHeader
□ extendDate — dataArr 빈 배열 → 빈 headerMap으로 updateHeader 실행 → DB 영향 확인
□ extendDate — 이미 이월된 거래처 재처리 시 중복 INSERT 오류 여부
□ @Transactional — insertExtendDateHistory 실패 시 insertExtendDate도 롤백
□ chainMsNo — Hq_Esti_00006과 달리 세션에서 chainMsNo도 주입됨 (extendDate 확인)
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/search` | ✅ SELECT |
| `/extendDate` | ✅ UPDATE |

### chainMsNo 주입 확인 ✅

**소스 84~86번**: `chainNo` + `chainMsNo` + `userId` 모두 정상 주입  
→ TC 156번 검증 포인트 (`chainMsNo 주입됨`) **정확** — Hq_Esti_00006 미주입과 명확히 다름

### 2-보완. `/extendDate` — `void` 반환 ★

| No | TC | 조건 | 예상값 |
|----|----|------|-------|
| 2-8 | extendDate 성공 응답 | 정상 이월 처리 | HTTP 200 + **빈 바디** ★ |


## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] TESFRHTB (CUD 작업)
│   ├── (Trigger) Tr_TESFRH_T01
│   └── (Trigger) Tr_TESFRH_T02
└── [테이블] TPRICETB (CUD 작업)
    └── (Trigger) Tr_TPRICE_T01
```
