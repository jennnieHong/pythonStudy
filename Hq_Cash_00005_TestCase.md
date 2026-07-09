# Hq_Cash_00005 — 월간지출내역현황 단위 테스트케이스

> **화면**: [HQ] 입출금관리 > 월간지출관리 > 월간지출내역현황 (hq_cash_00005)  
> **URL Prefix**: `POST /backoffice/data/hq/cash/hq_cash_00005`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **공통 전제**: 모든 요청은 HQ 권한 계정으로 **로그인된 세션** 필요 (`shopadmin` / `0000` 또는 `7249525SHOP` / `0000`)
> **DB 트리거 영향도**: 단순 조회 화면으로 변경(CUD)이 없으므로 관련 트리거/프로시저 연쇄 반응 없음 (CUD 없음)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 테스트 체인 번호 (자동주입) |
| `ID` | `shopadmin` | 로그인 사용자 ID (자동주입) |

---

## 엔드포인트 목록 (2개)

| # | URL | 기능 | ServiceType | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/searchList` | 월간지출내역현황 집계 목록 조회 | SELECT | MACCIOTB, TMACNCTB, TMACNTTB, MMEMBSTB |
| 2 | `/selectDtList` | 월간지출내역 상세 조회 | SELECT | MACCIOTB, TMACNTTB, MMEMBSTB |

---

## 1. `/searchList` — 월간지출내역현황 집계 목록 조회

**서비스 로직**: 파라미터 selectMsNo, searchFromDate, searchEndDate → `selectMmaList()` (ACNT_FG NOT IN('0','1') 조건 쿼리)  
**RequestBody**: `{"selectMsNo": "NC0003", "searchFromDate": "20260629", "searchEndDate": "20260629"}`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 1-1 | 정상 조회 | chainNo=`C001`, 지출 실적 1건 이상 존재 | `{"selectMsNo": "NC0003", "searchFromDate": "20260629", "searchEndDate": "20260629"}` | 월간 지출 집계 내역 List 반환 |
| 1-2 | 실적 없는 기간 조회 | chainNo=`C001` | `{"selectMsNo": "NC0003", "searchFromDate": "19990101", "searchEndDate": "19990101"}` | `[]` 빈 리스트 |
| 1-3 | 미인증 접근 | 세션 없음 | `{"selectMsNo": "NC0003", "searchFromDate": "20260629", "searchEndDate": "20260629"}` | 302 redirect |

---

## 2. `/selectDtList` — 월간지출내역 상세 조회

**서비스 로직**: 파라미터 selectMsNo, acntFg, acntCd, searchFromDate, searchEndDate → `selectDetailMMaList()`  
**RequestBody**: `{"selectMsNo": "NC0003", "acntFg": "2", "acntCd": "01", "searchFromDate": "20260629", "searchEndDate": "20260629"}`

| No | 케이스 | 세션 조건 | RequestBody | 예상값 |
|----|--------|----------|-------------|-------|
| 2-1 | 정상 상세 조회 | chainNo=`C001`, acntFg=`2`, acntCd=`01` | `{"selectMsNo": "NC0003", "acntFg": "2", "acntCd": "01", "searchFromDate": "20260629", "searchEndDate": "20260629"}` | 일자별 상세 트랜잭션 List 반환 |
| 2-2 | 상세 내역 없는 조건 조회 | chainNo=`C001` | `{"selectMsNo": "NC0003", "acntFg": "9", "acntCd": "99", "searchFromDate": "20260629", "searchEndDate": "20260629"}` | `[]` 빈 리스트 |

---

## DB 트리거 연쇄 및 동기화 (CUD 없음)

* 본 화면은 단순 조회용 화면으로, 데이터베이스의 테이블을 직접 변경(CUD)하지 않습니다.
* 따라서 데이터 무결성에 영향을 주는 DB 트리거 및 프로시저 연쇄 동작이 작동하지 않는 **무영향(Select-Only) 화면**입니다.
