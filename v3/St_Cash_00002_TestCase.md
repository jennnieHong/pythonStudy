# St_Cash_00002 — 입출금 내역현황 단위 테스트케이스

> **화면**: [ST] 현금 > 입출금 내역현황  
> **URL Prefix**: `POST /backoffice/data/st/cash/st_cash_00002`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식**: 전 엔드포인트 `@RequestBody`  
> **DB 트리거 영향도**: 없음 (단순 조회 전용 화면)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `msNo` | `NC0022` | searchList, selectDtList |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/searchList` | 기간별 매장 입출금 현황 집계 조회 | `List<Map>` | SELECT | MACCIOTB, MMACNTTB |
| 2 | `/selectDtList` | 계정별 입출금 상세 내역 조회 | `List<Map>` | SELECT | MACCIOTB, MMACNTTB |

---

## 1. `/searchList` — 기간별 입출금 현황 집계 조회

**파라미터 방어**: `searchFromDate` 및 `searchEndDate` 유효성 검증 (빈 문자열 체크)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | msNo=`NC0022` | `{"searchFromDate":"20260629","searchEndDate":"20260629"}` | 계정별 집계 금액 목록 리턴 |
| 1-2 | msNo=`NC0022` | `{"searchFromDate":"","searchEndDate":"20260629"}` | JS 단에서 "시작일을 선택해 주세요" 얼럿 노출 후 중단 |
| 1-3 | msNo=`NC0022` | `{"searchFromDate":"20260629","searchEndDate":""}` | JS 단에서 "종료일을 선택해 주세요" 얼럿 노출 후 중단 |

---

## 2. `/selectDtList` — 계정별 입출금 상세 내역 조회

**파라미터 방어**: `acntFg` 및 `acntCd` 선택값에 따른 동적 MyBatis XML 조건 분기 필터링

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | msNo=`NC0022` | `{"searchFromDate":"20260629","searchEndDate":"20260629","acntFg":"0","acntCd":"01"}` | 입금(`acntFg=0`) 및 외상매출금(`acntCd=01`) 상세 항목 리턴 |
| 2-2 | msNo=`NC0022` | `{"searchFromDate":"20260629","searchEndDate":"20260629","acntFg":"","acntCd":""}` | 계정 구분/코드 무관 전체 상세 내역 리턴 (MyBatis `<if>` 비활성화) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=I000034sb&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/cash/st_cash_00002"
$h = @{"Content-Type"="application/json"}

# 1-1. 기간별 집계 조회
Invoke-RestMethod -Uri "$base/searchList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260629","searchEndDate":"20260629"}'

# 2-1. 특정 계정 상세 내역 조회
Invoke-RestMethod -Uri "$base/selectDtList" -Method POST -Headers $h -WebSession $session `
  -Body '{"searchFromDate":"20260629","searchEndDate":"20260629","acntFg":"0","acntCd":"01"}'
```

---

## 주요 검증 포인트

```
□ 조회 전용 스펙 — CUD 로직이 존재하지 않아 DB 트리거/프로시저 연쇄 및 형변환 예외 리스크 원천 배제됨 확인
□ click-cell.bs.table — 핸들러 매개변수 선언부 순서 역바인딩 식별 (row ↔ event, $element ↔ field, value ↔ row)
□ ApexCharts 연동 — 집계 데이터를 parsing하여 입금/출금용 매출현황 그래프 2개 정상 렌더링 검증
```
