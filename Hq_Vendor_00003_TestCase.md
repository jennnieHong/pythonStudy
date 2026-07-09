# Hq_Vendor_00003 — 발주전송관리(본사) 단위 테스트케이스

> **화면**: [HQ] 거래처 > 발주전송관리  
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00003`  
> **@Transactional**: rollbackFor = {RuntimeException.class, Exception.class}  
> **요청 방식**: 
>   - 조회 API = `@RequestBody` 또는 폼 데이터 (JSON 형식)
>   - 인쇄 및 미리보기 = `@RequestBody` JSON 형식
>   - 이메일 전송 = `@RequestBody` 다중 배열 및 폼 파라미터 (JSON 형식)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | 전 엔드포인트 |
| `chainMsNo` | `NC0002` | print |
| `msNo` | `NC0007` | sendEmail |
| `msNm` | `본사` | sendEmail |
| `ID` | `shopadmin` | sendEmail |
| `NAME` | `본사관리자` | sendEmail |
| `hpNo` | `010-0000-0000` | sendEmail |
| `cEmail` | `admin@hms.com` | sendEmail |

---

## 엔드포인트 목록 (4개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getOrderList` | 발주 내역 조회 | `@RequestBody` | `Map<String, Object>` | SELECT | OBSLPHTB, MMEMBSTB, TVNDRMTB, OBREQHTB |
| 2 | `/getOrderDetailList` | 발주 내역 상세 조회 | `@RequestBody` | `List<Hq_Vendor_00003_OrderDetailListDto>` | SELECT | OBSLPDTB, TGOODSTB, MNAMEMTB, OBREQDTB |
| 3 | `/print` | 데이터 인쇄 / 미리보기 / 메일 뷰 처리 | `@RequestBody` | `ModelAndView` | SELECT | OBSLPHTB, MMEMBSTB, TVNDRMTB, OBREQHTB, OBSLPDTB, TGOODSTB |
| 4 | `/sendEmail` | 거래처 이메일 전송 처리 | `@RequestBody` | `Map<String, Object>` | INSERT/UPDATE | IF_RTMS_MAILQUEUE, OBSLPHTB |

---

## 1. `/getOrderList` — 발주 내역 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"msNo":"NC0007","vendor":"","searchFromDate":"20240201","searchEndDate":"20240201","offset":0,"limit":100}` | 해당 날짜 및 조건에 부합하는 `NC0007` 매장의 발주 전표 헤더 정보 목록 (`OBSLPHTB` 조인 조회 결과) |
| 1-2 | chainNo=`C001` | `{"msNo":"","vendor":"000001","searchFromDate":"20240201","searchEndDate":"20240201","offset":0,"limit":100}` | 특정 거래처(`000001`) 조건으로 필터링된 전체 매장의 발주 목록 |

---

## 2. `/getOrderDetailList` — 발주 내역 상세 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"orderDate":"20240201","msNo":"NC0007","slipNo":"0001","slipFg":"0"}` | 해당 전표의 상세 품목 리스트, 수량, 단가, 세액구분, 규격 정보 (`OBSLPDTB` 등 조인 결과) |

---

## 3. `/print` — 데이터 인쇄 및 미리보기 처리

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001`, chainMsNo=`NC0002` | `{"printType":"V","orderDate":"20240201","msNo":"NC0007","slipNo":"0001","slipFg":"0"}` | 메일 미리보기 뷰 (`/backoffice/main/contents/hq/vendor/hq_vendor_00003/eMail/hq_vendor_00003_previewEmail` 리턴) |
| 3-2 | chainNo=`C001`, chainMsNo=`NC0002` | `{"printType":"P","dataArr":[{"orderDate":"20240201","msNo":"NC0007","slipNo":"0001","slipFg":"0"}]}` | 발주서 출력 뷰 (`/backoffice/main/contents/hq/vendor/hq_vendor_00003/print/hq_vendor_00003_printOrder` 리턴) |

---

## 4. `/sendEmail` — 거래처 이메일 전송 처리

**서비스 핵심 흐름 & 비즈니스 룰**:
1. `IF_RTMS_MAILQUEUE` 테이블에 신규 행 적재 (`INSERT` 발생).
2. 만약 기존 전송 여부(`purchSendYn`)가 `'N'`이었을 경우, `OBSLPHTB` 테이블의 `PURCH_SEND_YN` = `'S'`, `PURCH_SEND_DATE` = 오늘날짜, `PURCH_SEND_MAIL_ADDR` = 거래처 메일 주소로 업데이트 수행 (`UPDATE` 발생).
3. **트리거 연쇄 배제**: 해당 이메일 전송 처리는 재고 및 매입 수량에 직접적인 영향을 주지 않으므로, Java 레벨의 후행 트리거 서비스(예: `Tr_OBSLPH_T01_Service` 등)는 기동되지 않고 수불 대장(`IMTRLGTB`)에도 로그가 적재되지 않는 것이 정상 비즈니스 규칙입니다.

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`, msNo=`NC0007`, userId=`shopadmin`, userNm=`본사관리자`, userEmail=`admin@hms.com`, hpNo=`010-0000-0000` | `{"orderDateArr":["20240201"],"msNoArr":["NC0007"],"slipNoArr":["0001"],"slipFgArr":["0"],"presidentNmArr":["Ｚ丮"],"vendorEmailArr":["test@example.com"],"purchSendYnArr":["N"],"vendorNmArr":["Ｚ丮"],"usePlanDateArr":["2024-02-01"],"msNmArr":["테스트매장"],"contactPsNmArr":["담당자"]}` | `{"midList":["..."],"returnDataList":[{"orderDate":"20240201",...}]}` 리턴 및 메일 대기큐 적재 완료 |

---

## PowerShell 테스트 검증 명령

```powershell
# 1. 로그인 수행 (shopadmin / 0000)
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/vendor/hq_vendor_00003"
$h = @{"Content-Type"="application/json"}

# 2. 발주 전표 목록 조회
Invoke-RestMethod -Uri "$base/getOrderList" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"NC0007","vendor":"","searchFromDate":"20240201","searchEndDate":"20240201","offset":0,"limit":100}'

# 3. 상세 내역 조회
Invoke-RestMethod -Uri "$base/getOrderDetailList" -Method POST -Headers $h -WebSession $session `
  -Body '{"orderDate":"20240201","msNo":"NC0007","slipNo":"0001","slipFg":"0"}'

# 4. 이메일 미리보기
Invoke-RestMethod -Uri "$base/print" -Method POST -Headers $h -WebSession $session `
  -Body '{"printType":"V","orderDate":"20240201","msNo":"NC0007","slipNo":"0001","slipFg":"0"}'
```
