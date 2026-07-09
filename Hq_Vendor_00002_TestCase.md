# Hq_Vendor_00002 — 발주품의작성 단위 테스트케이스

> **화면**: 본사 > 매입발주 > 매입관리 > 발주품의작성
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00002`
> **@Transactional**: 적용됨 (RuntimeException, Exception rollback 대상)
> **요청 방식 혼용**: `@RequestBody Map<String, Object>` 형태 활용
> **DB 트리거 영향도**: 있음 (발주 확정/취소 시 매입전표인 `OBSLPHTB`, `OBSLPDTB`에 대해 후행 Java 트리거 서비스 `Tr_OBSLPD_T01_Service`, `Tr_OBSLPD_T02_Service` 연쇄 기동)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | 전 엔드포인트 |
| `ID`      | `shopadmin` | `saveRequest`, `confirmRequest`, `cancelRequest`, `confirmSupply`, `cancelSupply` |

---

## 엔드포인트 목록 (6개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getReqList` | 발주 품의내역 및 거래처 리스트 조회 | `@RequestBody` | `List` | SELECT | OBREQHTB, OBREQDTB, MMEMBSTB, TVNDRMTB, OBSLPHTB |
| 2 | `/saveRequest` | 발주 품의서 수정사항(단가/수량/거래처) 저장 | `@RequestBody` | `void` | UPDATE | OBREQDTB |
| 3 | `/confirmRequest` | 품의 확정 (의뢰확정 -> 품의완료) | `@RequestBody` | `void` | UPDATE | OBREQHTB |
| 4 | `/cancelRequest` | 품의 취소 (품의완료 -> 품의취소) | `@RequestBody` | `void` | UPDATE | OBREQHTB |
| 5 | `/confirmSupply` | 최종 발주 확정 (매입전표 생성 및 트리거 연쇄) | `@RequestBody` | `void` | INSERT/UPDATE | OBREQHTB, OBREQDTB, OBSLPHTB, OBSLPDTB |
| 6 | `/cancelSupply` | 발주 취소 (매입전표 삭제 및 롤백) | `@RequestBody` | `void` | DELETE/UPDATE | OBREQHTB, OBREQDTB, OBSLPHTB, OBSLPDTB |

---

## 1. `/getReqList` — 발주 품의내역 및 거래처 리스트 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"msNo":"NC0007","procFg":"","searchFromDate":"20260618","searchEndDate":"20260618"}` | 조건에 부합하는 구매의뢰 목록 및 거래처 마스터 리스트 반환 |
| 1-2 | chainNo=`C001` | `{"msNo":"","procFg":"5","searchFromDate":"20260618","searchEndDate":"20260618"}` | 매장 전체에 대한 의뢰확정 상태 전표 목록 반환 |

---

## 2. `/saveRequest` — 발주 품의서 수정사항 저장

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | ID=`shopadmin` | `{"reqNoArr":["240201000701"],"goodsCdArr":["T0000011"],"vendorCdArr":["000001"],"requestQtyArr":["5.0"],"unitPrcArr":["25000.0"]}` | `OBREQDTB`에 확정수량, 확정단가, 확정거래처가 정상 업데이트됨 (`void`) |
| 2-2 | ID=`shopadmin` | `{"reqNoArr":[],"goodsCdArr":[],"vendorCdArr":[],"requestQtyArr":[],"unitPrcArr":[]}` | 루프가 돌지 않고 예외 없이 정상 종료 (`void`) |

---

## 3. `/confirmRequest` — 품의 확정

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | ID=`shopadmin` | `{"reqNoArr":["240201000701"]}` | `OBREQHTB.proc_fg` 상태가 `'1'`(품의완료)로 변경되고 확정일자 기록 (`void`) |

---

## 4. `/cancelRequest` — 품의 취소

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | ID=`shopadmin` | `{"reqNoArr":["240201000701"]}` | `OBREQHTB.proc_fg` 상태가 `'2'`(품의취소)로 변경됨 (`void`) |

---

## 5. `/confirmSupply` — 최종 발주 확정 (매입전표 생성)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | chainNo=`C001`, ID=`shopadmin`, `ms_no`가 `NC0007`로 바인딩됨 | `{"reqNoArr":["240201000701"]}` | `OBREQHTB.proc_fg` 상태가 `'3'`(발주확정)으로 변경. 신규 매입전표번호가 채번되어 `OBSLPHTB`, `OBSLPDTB`가 생성되고 후행 Java 트리거 기동 (`void`) |

---

## 6. `/cancelSupply` — 발주 취소 (매입전표 삭제)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 6-1 | chainNo=`C001`, ID=`shopadmin` | `{"reqNoArr":["240201000701"]}` | `OBREQHTB.proc_fg`가 `'4'`(발주취소)로 업데이트되고, 생성되었던 `OBSLPHTB`, `OBSLPDTB` 데이터가 물리적 삭제됨 (`void`) |

---

## 주요 검증 포인트

```
□ /getReqList — 수치형(Numeric) 컬럼 NVL 처리 결함
   - Oracle 호환 쿼리인 NVL(MAX(PURCH_UCOST), '') 형식이 EDB PostgreSQL 환경에서 "invalid input syntax for type numeric" 에러를 발생시킵니다.
   - 따라서 NVL(MAX(PURCH_UCOST), 0)으로 명시적 수치 대체값을 바인딩하도록 수정 후 검증 완료.

□ /confirmSupply — 수불 배제 비즈니스 룰 준수
   - 발주 확정 시 생성되는 매입전표의 proc_fg 상태는 '1'(검수대기/발주확정)입니다.
   - 후행 트리거 Tr_OBSLPD_T01_Service가 동작하지만, '4'(입고확정) 또는 '5'(의뢰확정) 상태가 아니므로 수불 가감(IMTRLGTB) 및 변경로그(obslplog) 적재가 원천 배제되어야 합니다. (적재 수량 0건 확인 완료)

□ /confirmSupply — 부가세 및 의제세액 계산식
   - 과세구분(tax_fg) 및 매장 부가세 적용 환경설정(ucost_vat_fg)에 따른 사칙연산 계산식(ROUND, CEIL, FLOOR)이 EDB PostgreSQL 환경에서도 오차 없이 정상 소수점 계산 및 절사 처리되는지 정합성을 검증합니다.
```

---

## DB 트리거 및 프로시저 연관관계도

```text
API Endpoint 호출 (confirmSupply / cancelSupply)
├── [테이블] OBREQHTB / OBREQDTB (proc_fg 상태 갱신)
├── [테이블] OBSLPHTB / OBSLPDTB (매입전표 CUD 동작)
│   ├── (Trigger Service) Tr_OBSLPD_T02_Service 기동 (검증 트리거)
│   └── (Trigger Service) Tr_OBSLPD_T01_Service 기동 (수불 트리거)
│         └── [조건 분기] proc_fg = '1' -> 수불대장(IMTRLGTB), obslplog 적재 배제
```

> **결론**: 본 화면은 발주 확정 시 자동으로 매입전표를 생성하여 후행 Java 트리거 서비스(`Tr_OBSLPD_T01_Service`, `Tr_OBSLPD_T02_Service`)를 호출하는 깊이 3 수준의 연쇄 구조를 가지고 있습니다. EDB PostgreSQL 환경에서도 의도한 수불 배제 비즈니스 룰 및 Numeric 대체 처리 패치가 정상적으로 유효함을 검증 완료하였습니다.
