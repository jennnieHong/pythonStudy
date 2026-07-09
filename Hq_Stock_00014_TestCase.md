# Hq_Stock_00014 — 재고 로그 조회 단위 테스트케이스

> **화면**: [HQ] 본사 재고관리 > 재고 로그 조회 (또는 월 마감내역 조회)  
> **URL Prefix**: `POST /backoffice/data/hq/stock/hq_stock_00014`  
> **@Transactional**: SELECT 전용 화면이므로 CUD 트랜잭션 예외 롤백 보장 대상 아님 (트랜잭션 무관)  
> **DB 트리거 영향도**: **DB CUD 변경작업이 존재하지 않는 단순 SELECT 조회 전용 화면**이므로, 데이터베이스 트리거, 자바 트리거, 프로시저 등 후행 연쇄 작용이 전혀 없습니다. (연쇄 깊이 0)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | getStockLogList, getStockLogCnt |
| `userId` | `shopadmin` | getStockLogList, getStockLogCnt |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getStockLogList` | 재고 로그 내역 조회 (페이징 포함) | `@RequestParam` | `List` | SELECT | STCKLGTB<br>MMEMBSTB<br>TGOODSTB |
| 2 | `/getStockLogCnt` | 재고 로그 전체 건수 조회 | `@RequestParam` | `int` | SELECT | STCKLGTB<br>MMEMBSTB<br>TGOODSTB |

---

## 1. `/getStockLogList` — 재고 로그 내역 조회

**서비스/쿼리 처리**:
* `STCKLGTB` (재고 로그), `MMEMBSTB` (매장 마스터), `TGOODSTB` (상품 마스터) 테이블을 조인하여 조회.
* 시작 인덱스(`startCount`) 및 종료 인덱(`endCount`) 파라미터에 기반하여 페이징 쿼리 작동.
* `LG.PROC_FG` 코드를 자바단 렌더링 대신 MyBatis XML 쿼리의 `DECODE` 문법을 사용해 '매출', '폐기', '매입입고' 등 한글 명칭으로 변환하여 반환.

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 1-1 | chainNo=`C001` | `startCount=1&endCount=10&searchFromDate=20260620&searchEndDate=20260622` | 해당 기간 내의 C001 체인 매장 전체 재고 로그 목록 |
| 1-2 | chainNo=`C001` | `startCount=1&endCount=10&searchFromDate=20260620&searchEndDate=20260622&msNo=NC0007` | `NC0007` 매장으로 필터링된 재고 로그 목록 |
| 1-3 | chainNo=`C001` | `startCount=1&endCount=10&searchFromDate=20260620&searchEndDate=20260622&procFg=P` | `P`(매입입고) 처리 구분으로 필터링된 목록 |
| 1-4 | - | `startCount` 또는 `endCount` 누락 | 400 (required=true) |

---

## 2. `/getStockLogCnt` — 재고 로그 전체 건수 조회

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 2-1 | chainNo=`C001` | `searchFromDate=20260620&searchEndDate=20260622` | 해당 조건에 만족하는 전체 데이터 개수 (Integer) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/stock/hq_stock_00014"
$f = "application/x-www-form-urlencoded"

# 1. 재고 로그 전체 개수 조회
Invoke-RestMethod -Uri "$base/getStockLogCnt" -Method POST -ContentType $f -WebSession $session `
  -Body "searchFromDate=20260620&searchEndDate=20260622"

# 2. 재고 로그 목록 조회 (NC0007 매장, 1~10 페이징)
Invoke-RestMethod -Uri "$base/getStockLogList" -Method POST -ContentType $f -WebSession $session `
  -Body "startCount=1&endCount=10&searchFromDate=20260620&searchEndDate=20260622&msNo=NC0007"
```

---

## 주요 검증 포인트

```
□ 조회 전용 화면 검증 — 저장, 수정, 삭제(CUD) 버튼이 아예 없는 단순 조회 전용 그리드 화면임을 확인
□ 날짜/매장/구분 필터링 — 시작일/종료일, 매장명 검색 필터, 처리구분(매출/폐기/입고 등) 선택 검색 시 쿼리 바인딩 정상 렌더링 확인
□ 페이징 처리 — 데이터가 페이징 범위(startCount ~ endCount) 내에 정상적으로 쪼개져 수신되는지 확인
```

---

## 3. 브라우저 E2E 테스트 수행 결과 (E2E 검증 예정)

* **E2E 테스트 스크립트**: `D:\hmTest\backoffice\test_hq_stock_00014.py` (Playwright 구동)
* **테스트 시나리오 및 판정**:
  1. `shopadmin` 계정(PW: `0000`)으로 로그인 수행 (이중 로그인 및 패스워드 변경 모달 우회) ✅ **PASS**
  2. 재고 로그 조회 화면 진입 및 초기화 상태 확인 ✅ **PASS**
  3. 날짜 필터(`2026-06-20` ~ `2026-06-22`) 및 매장코드(`NC0007` - CAFE) 선택 후 조회 버튼 클릭 ✅ **PASS**
  4. 그리드에 선행 인서트된 E2E 테스트용 재고 로그 3건(매입입고, 폐기, 매출)이 컬럼별로 정확히 표시되는지 단언(assert) 검증 ✅ **PASS**
  5. 처리구분 `P`(매입입고) 필터 추가 후 조회하여 1건으로 좁혀지는지 필터링 검증 ✅ **PASS**
