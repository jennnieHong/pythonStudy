# Hq_Vendor_00008 — 부대비용 등록관리 단위 테스트케이스

> **화면**: 본사 > 매입발주 > 매입관리 > 부대비용 등록관리
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00008`
> **@Transactional**: 적용됨 (RuntimeException, Exception rollback 대상)
> **요청 방식 혼용**: `@RequestBody HashMap<String, Object>` 형태 활용
> **DB 트리거 영향도**: 있음 (부대비용 적용 시 매입상세 `OBSLPDTB`에 대해 후행 Java 트리거 서비스 `Tr_OBSLPD_T02_Service` 및 `Tr_OBSLPD_T01_Service` 연쇄 기동)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | 전 엔드포인트 |
| `ID`      | `shopadmin` | `updateExtraCostAmt` |

---

## 엔드포인트 목록 (3개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/selectVendorOrderList` | 발주/입고 전표 목록 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, TVNDRMTB, MMEMBSTB |
| 2 | `/selectVendorOrderDetailList` | 전표 상세 품목 내역 조회 | `@RequestBody` | `List` | SELECT | OBSLPHTB, OBSLPDTB, TGOODSTB, MNAMEMTB, OBREQDTB |
| 3 | `/updateExtraCostAmt` | 부대비용 금액 배분 적용 및 저장 | `@RequestBody` | `String` | UPDATE | OBSLPHTB, OBSLPDTB |

---

## 1. `/selectVendorOrderList` — 발주/입고 전표 목록 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"msNo":"NC0007","vendorCd":"","searchFromDate":"20260601","searchEndDate":"20260630"}` | 조건에 부합하는 입고확정('4') 또는 발주확정('3') 상태이며, NO_ORDER_YN='N'인 전표 목록 반환 |
| 1-2 | chainNo=`C001` | `{"msNo":"","vendorCd":"000001","searchFromDate":"20260601","searchEndDate":"20260630"}` | 특정 거래처에 대해 동일 조건 전표 목록 반환 |

---

## 2. `/selectVendorOrderDetailList` — 전표 상세 품목 내역 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"orderDate":"20260615","msNo":"NC0007","slipNo":"0003"}` | 전표에 포함된 상세 품목 목록 및 기존 입력된 부대비용액(`GOODS_EXTRA_COST_AMT`) 반환 |

---

## 3. `/updateExtraCostAmt` — 부대비용 금액 배분 적용 및 저장

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | ID=`shopadmin` | `{"extraCostAmt":"20000","procFg":"0","list":[{"orderDate":"20260615","msNo":"NC0007","slipNo":"0003"}]}` | **[금액 기준 배분]** 선택된 전표의 상세 품목별 구매액(수량*단가) 비율대로 부대비용이 소수점 반올림(`ROUND`) 처리되어 배분 업데이트되고, 헤더 합계가 정상 갱신됨. 반환값: `"sucess"` |
| 3-2 | ID=`shopadmin` | `{"extraCostAmt":"20000","procFg":"1","list":[{"orderDate":"20260615","msNo":"NC0007","slipNo":"0003"}]}` | **[수량 기준 배분]** 선택된 전표의 상세 품목별 구매 수량 비율대로 부대비용이 소수점 반올림 배분 업데이트되고, 헤더 합계가 정상 갱신됨. 반환값: `"sucess"` |
| 3-3 | ID=`shopadmin` | `{"extraCostAmt":"20000","procFg":"0","list":[{"orderDate":"20260615","msNo":"NC0007","slipNo":"0003"}]}` *(이미 재고 반영 완료된 전표에 재배분 시)* | `chkExtraCostYn` 체크에 의해 이미 확정된 상태이므로 업데이트가 수행되지 않고 `"closed"` 반환 |

---

## 주요 검증 포인트

```
□ /updateExtraCostAmt — RATIO_TO_REPORT 함수 호환성 결함 및 수정
   - Oracle 호환 쿼리인 RATIO_TO_REPORT(...) OVER() 형식이 EDB PostgreSQL 환경에서 "function ratio_to_report(...) does not exist" 에러를 발생시킵니다.
   - 따라서 val / NULLIF(SUM(val) OVER(), 0) 문법으로 이식하여, 분배 비율 계산 시 오류 없이 정상 부대비용 적용 및 DB 저장이 수행되도록 검증 완료.

□ 트리거 연쇄 반응 (Depth 3) 및 수불 영향 배제 검증
   - 부대비용 적용(U) 시, Tr_OBSLPD_T02_Service (검증) 및 Tr_OBSLPD_T01_Service (수불) 트리거 서비스가 호출됩니다.
   - Tr_OBSLPD_T01_Service는 업데이트(U) 시점에 전표 진행상태(procFg)가 변경되지 않은 경우 수불 및 재고 가감 로직을 타지 않고 즉시 Bypass 처리하도록 Java 소스 코드가 설계되어 있습니다.
   - 따라서 부대비용 등록 후 실제 수불대장(IMTRLGTB) 추가 행 및 obslplog 누적 건수가 0건으로 유지되는 정합성(수불 배제)을 실측 검증합니다.
```

---

## DB 트리거 및 프로시저 연관관계도

```text
API Endpoint 호출 (updateExtraCostAmt)
├── [테이블] OBSLPDTB (goods_extra_cost_amt 금액 계산 및 업데이트)
│   ├── (Trigger Service) Tr_OBSLPD_T02_Service 기동 (비즈니스 룰 유효성 체크 및 검증)
│   └── (Trigger Service) Tr_OBSLPD_T01_Service 기동 (수불 트리거)
│         └── [조건 분기] proc_fg 상태값 변경이 없으므로 수불(IMTRLGTB) 및 변경로그(obslplog) 적재 배제 (Bypass)
└── [테이블] OBSLPHTB (slip_extra_cost_amt 헤더 금액 합계 업데이트)
```

> **결론**: 본 화면은 부대비용을 적용할 때 상세 데이터(`OBSLPDTB`)를 업데이트하며 후행 Java 트리거 서비스(`Tr_OBSLPD_T02_Service`, `Tr_OBSLPD_T01_Service`)를 거치는 깊이 3 수준의 연쇄 구조를 내포하고 있습니다. EDB PostgreSQL의 SQL 문법 오류를 해결하고, 트리거 시뮬레이션에서도 정상적으로 수불 배제 및 유효성 룰이 완벽히 검증됨을 확인하였습니다.
