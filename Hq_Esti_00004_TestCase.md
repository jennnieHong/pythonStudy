# Hq_Esti_00004 — 견적서 전송관리 단위 테스트케이스

> **화면**: [HQ] 견적관리 > 견적서 전송관리  
> **URL Prefix**: `POST /backoffice/data/hq/estimate/hq_esti_00004`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **외부 연동**: `Pos_MailInterface_Service`, `Tibero_MailInterface_Service`
> **DB 트리거 영향도**: TESFRVTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 |
| `msNo` | `NC0001` | 본부 매장번호 |
| `msNm` | `현대백화점본점` | 매장명 |
| `ID` | `shopadmin` | 로그인 사용자 ID |
| `NAME` | `홍길동` | 로그인 사용자 이름 |
| `cEmail` | `shopadmin@hyundai.com` | 발송자 이메일 |

---

## 엔드포인트 목록 (6개)

| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 견적요청서 목록 조회 | SELECT | TESTYMTB |
| 2 | `/detailSearch` | 견적요청서 상세 조회 | SELECT | TESFRHTB |
| 3 | `/print` | 인쇄/이메일 미리보기 (printType 4분기, ModelAndView) | SELECT | TESFRHTB<br>TESTYMTB |
| 4 | `/excelDownload` | 엑셀 다운로드 (2시트, XSSF POI) | SELECT | TESFRHTB<br>TESTYMTB |
| 5 | `/sendEmail` | 이메일 전송 (dataArr 배열 + Tibero 연동) | UPDATE | IF_DTIME<br>IF_RTMS_MAILQUEUE<br>IF_YN<br>RTMS_MAILQUEUE  |

---

## 1. `/search` — 견적요청서 목록 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{}` | 전체 견적요청서 List |
| 1-2 | chainNo=`C001` | `{"searchEstimTypeCd":"E001","searchEstimFromCd":"F001"}` | 필터 결과 |
| 1-3 | chainNo=`C001` | `{"searchEstimSendYn":"Y"}` | 메일전송 완료 건만 |
| 1-4 | chainNo=`C001` | `{"searchEstimSendYn":"N"}` | 미전송 건만 |

---

## 2. `/detailSearch` — 견적요청서 상세 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001","estimVendor":"V001"}` | 거래처별 상품 상세 List |
| 2-2 | chainNo=`C001` | `{}` | chainNo 조건만, 전체 상세 |

---

## 3. `/print` — 인쇄/이메일 미리보기

**컨트롤러 분기: printType 4가지**
```
printType = "E" → getList()    → mav.viewName = "hq_esti_00004_estiPrint"    (견적서 인쇄)
printType = "G" → getDetailList() → mav.viewName = "hq_esti_00004_goodsPrint"   (품목 인쇄)
printType = "M" → getDetailList() → mav.viewName = "hq_esti_00004_sendEmail"    (이메일 발송 뷰)
printType = "V" → getDetailList() → mav.viewName = "hq_esti_00004_previewEmail" (이메일 미리보기)
그 외           → ModelAndView 빈 객체 반환 (viewName 미설정)
```
**반환**: `ModelAndView` → JSP 렌더링 (HTML Fragment)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"printType":"E","estimTypeCd":"E001","estimFromCd":"F001"}` | `hq_esti_00004_estiPrint` JSP + printList(getList 결과) |
| 3-2 | chainNo=`C001` | `{"printType":"G","estimTypeCd":"E001","estimFromCd":"F001"}` | `hq_esti_00004_goodsPrint` JSP + printList(getDetailList 결과) |
| 3-3 | chainNo=`C001` | `{"printType":"M","estimTypeCd":"E001","estimFromCd":"F001"}` | `hq_esti_00004_sendEmail` JSP |
| 3-4 | chainNo=`C001` | `{"printType":"V","estimTypeCd":"E001","estimFromCd":"F001"}` | `hq_esti_00004_previewEmail` JSP |
| 3-5 | chainNo=`C001` | `{"printType":"X"}` | 어떤 분기도 타지 않음, 빈 ModelAndView 반환 |
| 3-6 | chainNo=`C001` | `{}` (printType 없음) | `commandMap.get("printType").equals(...)` → **NPE** |
| 3-7 | print 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 4. `/excelDownload` — 엑셀 다운로드

**Content-Type**: `application/x-www-form-urlencoded` (`@RequestParam`)  
**서비스 로직**: 2개 시트 생성
- 시트1 "견적전송대상": `getList()` → 8컬럼 (견적유형명, 견적서양식명, 거래처명, 시작일자, 종료일자, 휴대폰번호, 이메일정보, 메일전송여부)
- 시트2 "거래처 품목리스트": `getDetailList()` → 6컬럼 (No, 상품코드, 상품명, 규격, 구매단위, 수량)

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 4-1 | chainNo=`C001` | `excelEstimTypeCd=E001&excelEstimFromCd=F001&excelEstimVendor=V001&excelEstimSendYn=Y` | xlsx 다운로드, 2시트, Content-Disposition 헤더 확인 |
| 4-2 | chainNo=`C001` | `excelEstimTypeCd=E001&excelEstimFromCd=F001&excelEstimVendor=&excelEstimSendYn=` | 빈값 허용 (required=true지만 @NotBlank 없음) |
| 4-3 | chainNo=`C001` | 데이터 0건 조건 | 헤더행만 있는 xlsx 반환 |
| 4-4 | - | `excelEstimTypeCd=` (빈값) | 400 (@NotBlank) |
| 4-5 | - | `excelEstimFromCd=` (빈값) | 400 (@NotBlank) |
| 4-6 | excelDownload 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |
| 4-7 | 응답 처리 방식 확인 | `Invoke-RestMethod` 사용 | 바이너리 데이터 → 파일 저장 실패 가능 ★ (`-OutFile` 사용 필수) |
| 4-8 | workbook close 확인 | 정상 다운로드 후 | `workbook.close()` 192번 실행 → 리소스 정상 해제 ✅ |

---

## 5. `/sendEmail` — 이메일 전송

**서비스 로직**:
```
dataArr 배열 순회 (i)
  1. getEmailSeq() → mId 시퀀스 채번
  2. map에 chainNo, userId, mId, sName, sMail, sId, msNm, rName, rMail 주입
  3. query = SELECT '이메일' AS RMAIL, '수신자명' AS RNAME, '1' AS RID FROM DUAL
  4. insertEstiEmail(map) → 발송 메일 DB 저장
  5. estimSendYn == "N" → updateEstiEmail(map) (발송여부 업데이트)
  반환: midList (mId 목록)

컨트롤러 (서비스 이후)
  selectMailList(midMap) → Pos DB에서 발송 메일 정보 조회
  mailList 순회:
  ├── Tibero_MailInterface_Service.insertMail(mail) 성공 → map.put("flag", "Y")
  └── 실패 → map.put("flag", "E"), result = "N"
  → Pos_MailInterface_Service.updateMail(map)
최종 반환: "Y" (전체 성공) 또는 "N" (1건 이상 실패)
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | chainNo=`C001`, ID=`shopadmin`, NAME=`홍길동`, cEmail=`shopadmin@hyundai.com`, msNm=`현대백화점` | `{"dataArr":[{"estimSendMailAddr":"vendor@test.com","presidentNm":"김대표","estimSendYn":"Y","estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001"}]}` | `"Y"` (전체 성공) |
| 5-2 | 세션 동일 | **estimSendYn="N"** | insertEstiEmail + updateEstiEmail 추가 실행 |
| 5-3 | 세션 동일 | `{"dataArr":[...거래처 3건...]}` | mId 3건 채번, 3건 각각 insertEstiEmail |
| 5-4 | 세션 동일 | `{"dataArr":[]}` | 반복 없음, midList=[], selectMailList=[] → `"Y"` 반환 |
| 5-5 | 세션 동일 | `{}` (dataArr 없음) | **NPE** |
| 5-6 | 세션 동일 | **Tibero 연동 오류** | `flag="E"`, result=`"N"`, Pos updateMail은 실행 |
| 5-7 | 세션 동일 | estimSendMailAddr=null | query 문자열에 null 포함, insertEstiEmail 오류 가능 |
| 5-8 | **Tibero 실패 시 DB 롤백 여부** | Tibero 연동 오류 | `insertEstiEmail` DB 저장은 **롤백 안 됨** ★ (catch로 흡수) |
| 5-9 | **cEmail 세션 없음** | 세션에 cEmail 미존재 | `getUserInfo("cEmail")` null → `.toString()` → **NPE → 500** ★ |

---

## 서비스 핵심 분기 요약

```
print (ModelAndView 분기)
├── printType = "E" → getList + estiPrint JSP
├── printType = "G" → getDetailList + goodsPrint JSP
├── printType = "M" → getDetailList + sendEmail JSP
├── printType = "V" → getDetailList + previewEmail JSP
└── 그 외            → 빈 ModelAndView (viewName 미설정)
주의: printType 키 없으면 NPE

sendEmail
├── dataArr 배열 순회 → getEmailSeq + insertEstiEmail
│   └── estimSendYn = "N" → updateEstiEmail 추가
└── midList로 Pos selectMailList → Tibero insertMail
    ├── 성공 → flag="Y"
    └── 실패 → flag="E", result="N"
최종: "Y" 또는 "N"
```

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/estimate/hq_esti_00004"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Body '{}' -Headers $h -WebSession $session

# 2. 상세 조회
Invoke-RestMethod -Uri "$base/detailSearch" -Method POST -Headers $h -WebSession $session `
  -Body '{"estimTypeCd":"E001","estimFromCd":"F001"}'

# 3-1. 견적서 인쇄 (printType=E)
Invoke-RestMethod -Uri "$base/print" -Method POST -Headers $h -WebSession $session `
  -Body '{"printType":"E","estimTypeCd":"E001","estimFromCd":"F001"}'
# 예상: HTML (JSP 렌더링 결과) 반환, 응답 콘텐츠 길이 > 0 확인

# 3-6. printType 없음 NPE
Invoke-RestMethod -Uri "$base/print" -Method POST -Body '{}' -Headers $h -WebSession $session
# 예상: 500 (NPE)

# 4. 엑셀 다운로드 (form-param)
Invoke-WebRequest -Uri "$base/excelDownload" -Method POST -ContentType $f `
  -Body "excelEstimTypeCd=E001&excelEstimFromCd=F001&excelEstimVendor=V001&excelEstimSendYn=Y" `
  -WebSession $session -OutFile "C:\test\esti_download.xlsx"
# 예상: xlsx 파일 저장, 2시트 확인

# 5-1. 이메일 전송
Invoke-RestMethod -Uri "$base/sendEmail" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[{"estimSendMailAddr":"vendor@test.com","presidentNm":"김대표","estimSendYn":"Y","estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001"}]}'
# 예상: "Y"

# 5-2. estimSendYn=N 포함
Invoke-RestMethod -Uri "$base/sendEmail" -Method POST -Headers $h -WebSession $session `
  -Body '{"dataArr":[{"estimSendMailAddr":"vendor@test.com","presidentNm":"김대표","estimSendYn":"N","estimTypeCd":"E001","estimFromCd":"F001","estimVendorCd":"V001"}]}'
# 예상: "Y", DB에 updateEstiEmail 추가 실행 확인
```

---

## 사전 조건 (Test Data)

| 테이블 / 시스템 | 필요 데이터 |
|----------------|-----------|
| `HESTIMASTTB` | 견적요청서 마스터 (E001/F001) |
| `HESTIGOODSTB` | 견적 대상 상품 |
| `HESTIVNDRTB` | 거래처 정보 (V001, estimSendMailAddr 포함) |
| `HEMAILSNDTB` | 이메일 발송 이력 테이블 |
| POS DB | `MailInterface_MailInfo` 조회 가능 상태 |
| Tibero | `insertMail` 연동 가능 상태 (또는 Mock) |

---

## 주요 검증 포인트

```
□ print — printType 4종 각각 올바른 JSP viewName 반환 확인
□ print — printType 키 없을 시 NPE → 500 발생
□ excelDownload — 2시트 (견적전송대상, 거래처품목리스트) 각 헤더/데이터 확인
□ excelDownload — excelEstimVendor, excelEstimSendYn은 @NotBlank 없음 → 빈값 허용
□ sendEmail — estimSendYn="N" → updateEstiEmail 추가 실행 여부
□ sendEmail — Tibero 오류 시 result="N" 반환, Pos updateMail은 계속 실행
□ sendEmail — dataArr 없을 시 NPE
□ @Transactional — sendEmail 내 insertEstiEmail 일부 실패 시 롤백 범위
```

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
└── [테이블] TESFRVTB (CUD 작업)
    └── (Trigger) Tr_TESFRV_T01
```
