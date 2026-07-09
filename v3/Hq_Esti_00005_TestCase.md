# Hq_Esti_00005 — 견적서 업로드 관리 단위 테스트케이스

> **화면**: [HQ] 견적관리 > 견적서 업로드 관리 (거래처 견적 단가 수신/처리)  
> **URL Prefix**: `POST /backoffice/data/hq/estimate/hq_esti_00005`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}
> **DB 트리거 영향도**: TESFRVTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 (자동주입) |
| `ID` | `shopadmin` | 로그인 사용자 ID (자동주입) |

---

## 엔드포인트 목록 (6개)

| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 견적요청서 목록 조회 | SELECT | TESTYMTB |
| 2 | `/detailSearch` | 견적요청서 상세 조회 | SELECT | TESVDUTB |
| 3 | `/goodsSave` | 대상 상품 수량 저장 → 상세 재조회 반환 | UPDATE | TESVDUTB |
| 4 | `/goodsUpload` | 엑셀 업로드 → 상품 수량 일괄 UPDATE | UPDATE | TESVDUTB |
| 5 | `/receipt` | 견적서 접수 처리 (dataArr 배열) | UPDATE | TESFRVTB |
| 6 | `/confirm` | 견적서 확정 처리 (dataArr 배열) | UPDATE | TESFRVTB |

---

## 1. `/search` — 견적요청서 목록 조회

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainNo=`C001` | 견적요청서 3건 존재 | `{}` | List 3건 |
| 1-2 | chainNo=`C001` | 데이터 없음 | `{}` | `[]` |
| 1-3 | chainNo=`C001` | - | `{"estimTypeCd":"E001","estimFromCd":"F001","estimVendor":"V001"}` | 거래처별 필터 결과 |
| 1-4 | 세션 없음 | - | `{}` | 302 redirect |

---

## 2. `/detailSearch` — 견적요청서 상세 조회

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 2-1 | chainNo=`C001` | F001/V001 상품 등록됨 | `{"estimTypeCd":"E001","estimFromCd":"F001","estimVendor":"V001"}` | 상품 상세 List |
| 2-2 | chainNo=`C001` | 상품 없음 | `{"estimTypeCd":"E001","estimFromCd":"F001","estimVendor":"V001"}` | `[]` |

---

## 3. `/goodsSave` — 대상 상품 수량 저장

**서비스 로직**: `dataArr` 배열 → 각 건 `updateEstiGoods`  
**컨트롤러 특이사항**: 저장 후 `getDetailList()` 재조회 → List 반환 (void가 아님)

```
goodsSave(commandMap) → updateEstiGoods(dataArr 각 건)
→ getDetailList(commandMap) → 반환
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 3-1 | chainNo=`C001`, ID=`shopadmin` | G001 상품 존재 | `{"estimTypeCd":"E001","estimFromCd":"F001","estimVendor":"V001","dataArr":[{"estimGoodsCd":"G001","estimGoodsQty":5}]}` | updateEstiGoods 후 최신 detailList 반환 |
| 3-2 | chainNo=`C001` | G001, G002 존재 | `{"dataArr":[{"estimGoodsCd":"G001","estimGoodsQty":3},{"estimGoodsCd":"G002","estimGoodsQty":7}]}` | 2건 UPDATE 후 상세 List 반환 |
| 3-3 | chainNo=`C001` | - | `{"dataArr":[]}` | UPDATE 없음, 빈 dataArr 기준 detailList 반환 |
| 3-4 | chainNo=`C001` | - | `{}` (dataArr 없음) | **NPE** (null cast) |
| 3-5 | chainNo=`C001` | G001 없는 코드 | `{"dataArr":[{"estimGoodsCd":"XXXXX","estimGoodsQty":5}]}` | 0건 UPDATE, detailList 반환 (오류 없음) |

---

## 4. `/goodsUpload` — 엑셀 업로드

**Content-Type**: `multipart/form-data`  
**파라미터**: `estimTypeCd` (@NotBlank), `estimFromCd` (@NotBlank), `estimVendor` (@NotBlank), 파일  
**서비스 로직**: `getExcelUploadList()` (POI 파싱) → 각 행 `updateEstiGoods`

| No | 세션 조건 | DB 선행상태 | Request (multipart) | 예상값 |
|----|----------|------------|---------------------|-------|
| 4-1 | chainNo=`C001`, ID=`shopadmin` | G001, G002 존재 | 정상 xlsx + `estimTypeCd=E001&estimFromCd=F001&estimVendor=V001` | 엑셀 행 수만큼 updateEstiGoods 실행 |
| 4-2 | ID=`shopadmin` | - | 빈 엑셀 (0행) | 반복 없음, 정상 종료 |
| 4-3 | ID=`shopadmin` | - | 파일 없음 (iterator.hasNext()=false) | file=null → getExcelUploadList(null) NPE 가능 |
| 4-4 | - | - | `estimTypeCd=` | 400 (@NotBlank) |
| 4-5 | - | - | `estimFromCd=` | 400 (@NotBlank) |
| 4-6 | - | - | `estimVendor=` | 400 (@NotBlank) |
| 4-7 | ID=`shopadmin` | - | 손상된 xlsx | POI 예외 → 롤백 |
| 4-8 | **multipart 아닌 요청** | Content-Type=application/json | **ClassCastException → 500** ★ |

---

## 5. `/receipt` — 견적서 접수 처리

**서비스 로직**: `dataArr` 배열 → 각 건 `updateEstiReceipt`

```
dataArr 배열 순회 (i)
  map에 chainNo, chainMsNo, userId 주입
  → updateEstiReceipt(map)
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 5-1 | chainNo=`C001`, ID=`shopadmin` | V001 미접수 상태 | `{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001"}]}` | updateEstiReceipt 1건, 접수상태로 변경 |
| 5-2 | chainNo=`C001` | V001 **이미 접수됨** | 동일 RequestBody | 재접수 (이미 접수 상태에서의 중복 처리 방식 확인) |
| 5-3 | chainNo=`C001` | V001, V002 미접수 | `{"dataArr":[{"estimVendorCd":"V001"},{"estimVendorCd":"V002"}]}` | 2건 각각 updateEstiReceipt |
| 5-4 | chainNo=`C001` | - | `{"dataArr":[]}` | 반복 없음, 정상 종료 (void) |
| 5-5 | chainNo=`C001` | - | `{}` (dataArr 없음) | **NPE** |
| 5-6 | - | - | @Transactional: 2번째 UPDATE 오류 | 1번째 rollback |
| 5-7 | chainMsNo 실제 주입 여부 | receipt 호출 후 Mapper SQL 확인 | `chainMsNo` 조건이 Mapper SQL에 있다면 null 처리 방식 확인 ★ |

---

## 6. `/confirm` — 견적서 확정 처리

**서비스 로직**: `dataArr` 배열 → 각 건 `updateEstiConfirm`  
(receipt와 구조 동일, Mapper 메서드만 다름)

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 6-1 | chainNo=`C001`, ID=`shopadmin` | V001 접수완료 상태 | `{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001"}]}` | updateEstiConfirm 1건, 확정상태로 변경 |
| 6-2 | chainNo=`C001` | V001 **미접수 상태** | 동일 RequestBody | 접수 없이 확정 → 데이터 정합성 문제 가능 |
| 6-3 | chainNo=`C001` | V001 **이미 확정됨** | 동일 RequestBody | 중복 확정 처리 방식 확인 |
| 6-4 | chainNo=`C001` | - | `{"dataArr":[]}` | 반복 없음, 정상 종료 |
| 6-5 | chainNo=`C001` | - | `{}` (dataArr 없음) | **NPE** |
| 6-6 | chainMsNo 실제 주입 여부 | confirm 호출 후 Mapper SQL 확인 | 동일 확인 ★ |

---

## 서비스 핵심 분기 요약

```
goodsSave (수량 저장)
└── dataArr 배열 → updateEstiGoods (각 건)
    → 저장 후 getDetailList 자동 재조회 → 반환 (void 아님!)
    주의: dataArr 없으면 NPE

goodsUpload (엑셀 업로드)
└── getExcelUploadList(POI) → 각 행 updateEstiGoods
    주의: 파일 null → NPE 가능

receipt (접수 처리)
└── dataArr 배열 → updateEstiReceipt (각 건)

confirm (확정 처리)
└── dataArr 배열 → updateEstiConfirm (각 건)

처리 순서 이슈:
  미접수 상태에서 confirm 직접 호출 가능 → 비즈니스 정합성 체크 필요
```

---

## Hq_Esti_00004 vs Hq_Esti_00005 차이점

| 항목 | Hq_Esti_00004 (전송관리) | Hq_Esti_00005 (업로드 관리) |
|------|------------------------|--------------------------|
| 주요 역할 | 견적서 발송 (메일 전송) | 견적서 수신/처리 |
| 핵심 메서드 | `sendEmail` + Tibero 연동 | `receipt`, `confirm` |
| goodsSave 반환 | void | **detailList 재조회 반환** |
| 엑셀 | 다운로드 (POI 생성) | **업로드** (POI 파싱) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/estimate/hq_esti_00005"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Body '{}' -Headers $h -WebSession $session

# 2. 상세 조회
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","estimFromCd":"F001","estimVendor":"V001"}'

# 3-1. 수량 저장 (저장 후 detailList 자동 반환)
Invoke-RestMethod -Uri "$base/goodsSave" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","estimFromCd":"F001","estimVendor":"V001","dataArr":[{"estimGoodsCd":"G001","estimGoodsQty":5}]}'
# 예상: 최신 detailList 반환 (void 아님)

# 4. 엑셀 업로드
$form = @{
  "file" = Get-Item "C:\test\esti_upload.xlsx"
  "estimTypeCd" = "E001"
  "estimFromCd" = "F001"
  "estimVendor" = "V001"
}
Invoke-RestMethod -Uri "$base/goodsUpload" -Method POST -Form $form -WebSession $session

# 5-1. 접수 처리
Invoke-RestMethod -Uri "$base/receipt" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001"}]}'

# 6-1. 확정 처리
Invoke-RestMethod -Uri "$base/confirm" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[{"estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001"}]}'

# NPE 테스트 (dataArr 없음)
Invoke-RestMethod -Uri "$base/goodsSave" -Method POST -Body '{}' -Headers $h -WebSession $session
# 예상: 500 (NPE)
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `HESTIMASTTB` | 견적요청서 마스터 (E001/F001/V001) |
| `HESTIGOODSTB` | 견적 대상 상품 (G001, G002 등) |
| `HESTIVNDRTB` | 거래처 견적 상태 (미접수/접수/확정 상태) |
| `MMCHATB` | chainNo=C001 |
| 엑셀 파일 | 상품코드, 단가 컬럼 포함 xlsx |

---

## 주요 검증 포인트

```
□ goodsSave — UPDATE 후 자동 getDetailList 재조회 반환 (List<Dto>)
□ goodsSave — dataArr 없으면 NPE → 500
□ receipt → confirm 순서 — 미접수 상태에서 confirm 직접 호출 가능 여부 체크
□ receipt 중복 호출 — 이미 접수된 거래처 재접수 시 동작 확인
□ confirm 중복 호출 — 이미 확정된 거래처 재확정 시 동작 확인
□ goodsUpload — 파일 미포함 시 null → NPE 발생 여부
□ @Transactional — receipt/confirm 다건 중 실패 시 전체 롤백
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
└── [테이블] TESFRVTB (CUD 작업)
    └── (Trigger) Tr_TESFRV_T01
```
