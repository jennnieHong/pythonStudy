# St_Reserve_00001 — 예약일정관리 단위 테스트케이스

> **화면**: [ST] 예약관리 > 예약일정관리  
> **URL Prefix**: `POST /backoffice/data/st/reserve/st_reserve_00001`  
> **@Transactional**: rollbackFor = {RuntimeException.class, Exception.class}  
> **DB 트리거 영향도**: 연쇄 DB 트리거 및 자바 트리거 없음 (단일 테이블 CUD로 종결)
> **결함 상태**: SMS/MMS 발송 테이블(`TBLMESSAGE`, `MMS_MSG`)의 EDB 내 부재로 인한 SMS 발송 기능 장애 (재테스트 시 500 에러 발생)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `msNo` | `NC0007` | searchReserveDate, searchReserve, insert, delete, update, searchReserveDt |
| `userId` | `H000051cafe` | insert, update |

---

## 엔드포인트 목록 (8개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/searchReserveDate` | 예약 날짜 목록 조회 (FullCalendar) | `@RequestParam` | `List` | SELECT | EMSRESTB |
| 2 | `/searchReserve` | 특정 일자 예약 목록 조회 | `@RequestParam` | `List` | SELECT | EMSRESTB |
| 3 | `/insert` | 예약 등록 및 저장 | `@RequestParam` | `String` | INSERT | EMSRESTB |
| 4 | `/delete` | 예약 내역 삭제 | `@RequestParam` | `String` | DELETE | EMSRESTB |
| 5 | `/update` | 예약 내역 수정 및 저장 | `@RequestParam` | `String` | UPDATE | EMSRESTB |
| 6 | `/searchReserveDt` | 예약 조건별 상세 검색 | `@RequestParam` | `List` | SELECT | EMSRESTB |
| 7 | `/searchReservePrint` | 예약 내역 인쇄용 데이터 조회 | `@RequestParam` | `ModelAndView` | SELECT | EMSRESTB |
| 8 | `/smsSend` | SMS 또는 MMS 발송 | `@RequestParam` | `String` | INSERT | TBLMESSAGE (삭제)<br>MMS_MSG (삭제) |

---

## 1. `/searchReserveDate` — 예약 날짜 목록 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 1-1 | msNo=`NC0007` | `startDate=20260601&endDate=20260630` | 해당 기간의 예약 날짜 목록 반환 |
| 1-2 | - | `startDate` 누락 | 400 (required=true) |

---

## 2. `/searchReserve` — 특정 일자 예약 목록 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 2-1 | msNo=`NC0007` | `reserveDate=20260624` | 해당 일자의 테이블 매핑 예약 정보 리스트 |
| 2-2 | - | `reserveDate` 누락 | 400 (required=true) |

---

## 3. `/insert` — 예약 등록 및 저장

**서비스 처리**:
```
reserveChk() 중복 체크 -> 중복 시 "dulp" 반환
getReserveMaxSeq() 최대 시퀀스 채번
insertReserve() 실행 -> "success" 반환
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 3-1 | msNo=`NC0007`, userId=`H000051cafe` | `reserveDate=20260624&reserveTime=1230&tableGroup=1&table1=1&table2=1&custNm=TestCustomer&telNo=01012345678&reserveNm=TestReserve&reserveInwon=4&reserveMenu=Coffee&reserveSpecial=Window` | `"success"` 반환 및 DB 적재 |
| 3-2 | msNo=`NC0007` | 동일한 테이블 시간 및 날짜로 중복 예약 시도 | `"dulp"` 반환 (중복 검증) |
| 3-3 | - | `reserveDate` 누락 | 400 (required=true) |

---

## 4. `/delete` — 예약 내역 삭제

**서비스 처리**:
```
deleteReserve() -> "success" 반환
(seqArr 파라미터는 콤마로 결합된 시퀀스들을 받아 MyBatis <foreach>로 일괄 삭제)
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 4-1 | msNo=`NC0007` | `reserveDate=20260624&seqArr=1` | `"success"` 반환 및 DB 삭제 완료 |
| 4-2 | msNo=`NC0007` | `reserveDate=20260624&seqArr=1,2,3` | 복수 데이터 삭제 성공 |

---

## 5. `/update` — 예약 내역 수정 및 저장

**서비스 처리**:
```
reserveUpdateChk() 중복 체크 -> 중복 시 "dulp" 반환
getReserveMaxSeq() 신규 일련번호 채번
updateReserve() -> "success" 반환
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 5-1 | msNo=`NC0007`, userId=`H000051cafe` | `reserveDate=20260624&currentSeq=1&reserveTime=1230&tableGroup=1&table1=1&table2=1&custNm=TestCustomer&telNo=01012345678&reserveNm=TestReserve&reserveInwon=4&reserveMenu=SpecialCoffee&reserveSpecial=VIP` | `"success"` 반환 및 시퀀스 재채번 수정 완료 |
| 5-2 | msNo=`NC0007` | 타 예약과 겹치도록 시간/테이블 수정 시도 | `"dulp"` 반환 |

---

## 6. `/searchReserveDt` — 예약 조건별 상세 검색

> **[버그 조치 완료]** `AND CUST_NM LIKE '%' || #{reserveNm} || '%'` (오타) -> `#{custNm}`으로 패치 완료.

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 6-1 | msNo=`NC0007` | `searchFromDate=20260624&searchToDate=20260624&custNm=TestCustomer` | 정확히 예약자명 조건 매핑되어 목록 검색 성공 |
| 6-2 | msNo=`NC0007` | `searchFromDate=20260624&searchToDate=20260624&reserveNm=TestReserve` | 예약제목 조건 매핑 검색 성공 |

---

## 7. `/searchReservePrint` — 예약 내역 인쇄용 데이터 조회

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 7-1 | msNo=`NC0007` | `reserveDate=20260624` | `ModelAndView` (st/reserve/st_reserve_00001_print.jsp) 데이터가 매핑되어 반환 |

---

## 8. `/smsSend` — SMS 또는 MMS 발송

> **[결함 지속 상태]** 개발 DB(EPAS)에서 `TBLMESSAGE`, `MMS_MSG` 테이블이 DROP 되었으므로 이 API 호출 시 **서버 500 SQL 에러**가 발생합니다.

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 8-1 | `smsFg=0&sendHpNo=010-1234-5678&destHpNo=01011112222&sendText=E2ETest` | **500 Internal Server Error** (SQL Error: relation "tblmessage" does not exist) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=H000051cafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/reserve/st_reserve_00001"
$f = "application/x-www-form-urlencoded"

# 1. 예약 조회 (특정일자)
Invoke-RestMethod -Uri "$base/searchReserve" -Method POST -ContentType $f -WebSession $session `
  -Body "reserveDate=20260624"

# 2. 예약 등록
Invoke-RestMethod -Uri "$base/insert" -Method POST -ContentType $f -WebSession $session `
  -Body "reserveDate=20260624&reserveTime=1230&tableGroup=1&table1=1&table2=1&custNm=TestCustomer&telNo=01012345678&reserveNm=TestReserve&reserveInwon=4&reserveMenu=Coffee&reserveSpecial=Window"

# 3. SMS 전송 시도 (오류 발생 정상)
try {
    Invoke-RestMethod -Uri "$base/smsSend" -Method POST -ContentType $f -WebSession $session `
      -Body "smsFg=0&sendHpNo=010-1234-5678&destHpNo=01011112222&sendText=TestText"
} catch {
    Write-Host "SMS Send Failed (Expected Error): $_"
}
```

---

## 주요 검증 포인트

```
□ 특이사항 저장 방어 — reserveSpecial (SPECIAL_NOTE) 컬럼이 insertReserve 및 updateReserve SQL에서 정상 바인딩 및 수정 적재되는지 검증
□ 숫자 필터링 검증 — 주문 예약 팝업 내 숫자 입력란(인원수, 연락처)에 문자가 원천적으로 걸러지는지 검증
□ SMS 결함 상태 보존 — DB의 SMS 발송 대기 테이블들이 무결하게 DROP된 상태에서 예외 발생 및 UI 우회 처리 검증
```

---

## 9. 브라우저 E2E 테스트 수행 결과

* **E2E 테스트 스크립트**: `D:\hmTest\backoffice\test_reserve_management.py` (Playwright 구동)
* **테스트 시나리오 및 판정**:
  1. `H000051cafe` 계정(PW: `0000`)으로 로그인 수행 (이중 로그인 및 패스워드 변경 모달 우회) ✅ **PASS**
  2. 예약 일정 관리 화면 진입 후 신규 예약 생성 (`custNm='TestCustomer'`) ✅ **PASS**
  3. 예약 수정 (메뉴 및 특이사항 `SPECIAL_NOTE` 컬럼 변경 저장 및 DB 적재 검증) ✅ **PASS**
  4. 예약 상세 조건 검색 (오타 수정된 `custNm` 상세 조건에 의해 정상 필터링 확인) ✅ **PASS**
  5. 인쇄 기능 데이터 연동 검증 (Mock printModule 함수 호출 가로채기 방식 검증) ✅ **PASS**
  6. SMS 전송 기능 실행 (전송 버튼 클릭 및 확인 단계 수행) ❌ **FAIL (테이블 부재로 인한 Ajax 실패 감지 및 모달 강제 Hide 예외처리)**
  7. 예약 내역 다중 선택 및 삭제 (그리드 체크 후 최종 삭제 및 DB 삭제 단언 확인) ✅ **PASS**
