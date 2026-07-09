# Hq_Sysif_00002 — 현금 시재 입출금 등록 단위 테스트케이스

> **화면**: [HQ] 재고관리 > 마감관리 > 현금 시재 입출금 등록  
> **URL Prefix**: `/backoffice/data/hq/systeminterface/hq_sysif_00002/`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: POST  
> **DB 트리거 영향도**: 확정 시 `Tr_MMEMBS_T01_Service`가 기동하여 하위 가맹점 정보 동기화(`SSMEMBTB`) 및 트리거 로그(`MMSLOGTB`, `MMEMLGTB`) 연쇄 처리를 수행합니다. (현재 Java 소스 상의 매개변수 누락 버그로 인해 기본 구동은 우회(Bypass)되는 상태입니다.)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | getCashInterList (매장 소속 체인코드 매핑) |
| `ID` | `shopadmin` | CashInterface (확정자 ID로 매핑) |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `getCashInterList` | Tibero DB로부터 현금 시재 입출금 목록 조회 | `@RequestBody` JSON | `List<Hq_Sysif_00002_CashInterListDto>` | SELECT | hmsfns.HMSADM.TSM_CASH_RCPS_MST (Tibero)<br>hmsfns.MUSERSTB (User 매핑용) |
| 2 | `CashInterface` | 선택된 시재 내역 확정 처리 | `@RequestParam` Form-data | `String` ('Y' or 'E') | UPDATE | hmsfns.HMSADM.TSM_CASH_RCPS_MST (Tibero)<br>hmsfns.MMEMBSTB (EDB)<br>hmsfns.IFSLRETB (EDB) |

---

## 1. `getCashInterList` — 현금 시재 입출금 목록 조회

**특이사항**:
* 이 API는 외부 연동 Tibero DB에서 현금 시재 입금 내역(`COFM_YN` 확정 상태와 무관하게 조회 기간 내 모든 내역)을 가져옵니다.
* 로컬 개발망 등 외부 Tibero DB (`10.7.138.179`) 접속이 불가능한 네트워크 환경에서는 소켓 커넥션 타임아웃 예외가 발생합니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 1-1 | chainNo=`C001` | Tibero DB 정상 연결 가능 및 데이터 존재 | `{"msNo":"NC0003"}` | `List` 객체 반환, 매장(`NC0003`)의 금년도 1월 1일부터 오늘까지 발생한 시재 입금 내역 리스트 출력 |
| 1-2 | chainNo=`C001` | Tibero DB 접속 불가 (네트워크 단절) | `{"msNo":"NC0011"}` | `500 Internal Server Error` 또는 `SQLException` (Connection Timeout) 발생 |

---

## 2. `CashInterface` — 선택된 시재 내역 확정 처리

**특이사항**:
* `@RequestParam` 형식으로 다수의 체크된 배열 파라미터(`Arr[]`)들을 전달받아 확정을 진행합니다.
* EDB 내 가맹점 마스터(`MMEMBSTB`)의 준비금 및 가맹점 마감 테이블(`IFSLRETB`)의 익일 준비금을 업데이트합니다.
* 확정 처리는 트랜잭션 단위로 진행되며, Tibero DB 업데이트가 먼저 성공해야 EDB 업데이트 및 Java 트리거가 수행됩니다.

| No | 세션 조건 | EDB/Tibero 선행상태 | Request Parameter (Form Data) | 예상값 / 검증 포인트 |
|----|----------|-------------------|-------------------|--------------------|
| 2-1 | ID=`shopadmin` | Tibero DB 정상 기동 및 EDB 가맹점 존재 | `bizCdArr[]=01`<br>`shopCdArr[]=20`<br>`occuDtArr[]=20260605`<br>`rcpsSeqArr[]=1`<br>`prstClsfCdArr[]=11`<br>`rcpsAmtArr[]=150000`<br>`msNo=NC0003` | `'Y'` 반환 (확정 성공)<br>1. Tibero `TSM_CASH_RCPS_MST.COFM_YN` = 'Y'<br>2. EDB `MMEMBSTB.IF_RESERVE_AMT` = 150000 갱신<br>3. `IFSLRETB` 최종 마감일의 `NEXT_RESERVE_AMT` = 150000 갱신 |
| 2-2 | ID=`shopadmin` | Tibero DB 접속 불가 (네트워크 단절) | `bizCdArr[]=01`<br>`shopCdArr[]=20`<br>`occuDtArr[]=20260605`<br>`rcpsSeqArr[]=1`<br>`prstClsfCdArr[]=11`<br>`rcpsAmtArr[]=150000`<br>`msNo=NC0011` | `'E'` 반환 (예외 catch)<br>Tibero DB 커넥션 실패에 의한 트랜잭션 롤백 및 에러 반환 |

---

## PowerShell API 테스트 스크립트

개발 및 검증 단계에서 API를 직접 호출할 수 있도록 제공되는 PowerShell 스크립트 템플릿입니다.

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/systeminterface/hq_sysif_00002"
$hJson = @{"Content-Type"="application/json"}
$hForm = @{"Content-Type"="application/x-www-form-urlencoded"}

# 1. 현금 시재 입출금 내역 조회 (Tibero DB 접속 가능 상태 전제)
try {
    $records = Invoke-RestMethod -Uri "$base/getCashInterList" -Method POST -Headers $hJson -WebSession $session `
      -Body '{"msNo":"NC0003"}'
    Write-Host "조회 성공: " $records
} catch {
    Write-Host "조회 실패 (예상된 네트워크 제약사항): " $_.Exception.Message
}

# 2. 현금 시재 확정 처리 (Tibero DB 접속 가능 상태 전제)
try {
    $result = Invoke-RestMethod -Uri "$base/CashInterface" -Method POST -Headers $hForm -WebSession $session `
      -Body "bizCdArr[]=01&shopCdArr[]=20&occuDtArr[]=20260605&rcpsSeqArr[]=1&prstClsfCdArr[]=11&rcpsAmtArr[]=150000&msNo=NC0003"
    Write-Host "확정 결과: " $result
} catch {
    Write-Host "확정 실패 (예상된 네트워크 제약사항): " $_.Exception.Message
}
```
