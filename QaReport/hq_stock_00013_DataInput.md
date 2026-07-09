# Hq_Stock_00013 선입선출 월말마감 E2E 테스트 사전 데이터 가공 가이드

본 마감 화면(`hq_stock_00013`)의 E2E 테스트 및 정상 동작을 위해 사전에 준비(가공)되어야 하는 데이터 요건입니다.
각 요건별로 **필요한 테이블/필드, SQL 처리 방법, 시스템 화면 처리 방법**을 일목요연하게 매핑하여 정리했습니다.

---

## 1. 사전 데이터 요구사항 요약 (Table Checklist)

| 연번 | 사전 작업 대상 | 대상 테이블 | 필수 상태/필드값 | SQL 주입 방법 (2장 참조) | 화면(UI) 처리 방법 (3장 참조) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **전월 재고 이월 데이터** | `hmsfns.IMMMIOTB`<br>(월별 재고 요약) | `CREATE_MONTH = '202606'`<br>`START_QTY` = 전월 기말재고<br>`START_COST` = 전월 기말단가 | 전월(`202605`) 기말 데이터를 복사하여 당월 기초 데이터로 복제 주입 | `hq_stock_00013` (월말마감처리) 화면에서 직전월인 **`2026-05`**를 조회하여 마감 실행 완료 |
| **2** | **당월 신규 거래 상품 기초 행** | `hmsfns.IMMMIOTB`<br>(월별 재고 요약) | `CREATE_MONTH = '202606'`<br>`START_QTY = 0`<br>`START_COST = 0.00` | 당월 일별 재고(`IMDDIOTB`)에 거래가 있으나 이월이 없는 신규 상품의 요약 행 사전 등록 | 무발주입고(`hq_vendor_00009`/`st_vendor_00006`)나 당일매출등록(`st_sales_00004`) 등으로 거래를 발생시킴 |
| **3** | **오버플로우 금액 오류 방지** | `hmsfns.OBSLPDTB`<br>(매입발주상세) | `EXTRA_COST < 10^11`<br>(정수 11자리 미만 제약) | 정산 부대비용 필드(`numeric(14,3)`)의 1,000억 원 이상 잘못된 값 제거 | `hq_vendor_00008` (부대비용 등록관리) 화면에서 해당 전표의 부대비용 단가를 정상 수치로 수정 후 저장 |
| **4** | **체인 본사-가맹점 상점 매핑** | `hmsfns.MMEMBSTB`<br>(매장 마스터) | `CHAIN_NO = 'C001'`<br>`USE_YN = 'Y'` | 상점의 `ms_no`와 체인 본사의 `chain_ms_no`가 상호 일치되도록 설정 | `admin_master_00004` (매장관리) 화면에서 매장 상세정보 등록 및 사용유무 설정 |

---

## 2. SQL 쿼리를 이용한 데이터 가공 방법 (Database API)

DB에 직접 접속하여 테스트 환경을 빠르게 세팅하고자 할 때 사용하는 SQL 가이드입니다.

### 2.1 [1번 대상] 전월 이월(Carry Over) 데이터 적재
전월(`202605`)의 기말 수량/단가를 당월(`202606`)의 기초 재고 정보로 이월 복사합니다.
```sql
INSERT INTO hmsfns.IMMMIOTB (
    create_month, ms_no, goods_cd, chain_ms_no,
    start_qty, start_cost,
    purch_qty, purch_cost, purch_extra_cost,
    return_qty, return_cost,
    sale_qty, sale_cost, sale_extra_cost,
    in_qty, in_cost,
    out_qty, out_cost,
    disuse_qty, disuse_cost,
    adjust_qty, adjust_cost,
    tin_qty, tin_cost,
    tout_qty, tout_cost,
    end_qty, end_cost,
    returndis_qty, returndis_cost,
    move_in_qty, move_in_cost,
    move_out_qty, move_out_cost,
    wholesale_qty, wholesale_cost,
    wholesale_rt_qty, wholesale_rt_cost,
    start_cost_totavg, end_cost_totavg,
    purch_gab_extra_cost
)
SELECT 
    '202606', ms_no, goods_cd, chain_ms_no,
    end_qty, end_cost,
    0, 0, 0,
    0, 0,
    0, 0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    end_qty, end_cost,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0
FROM hmsfns.IMMMIOTB
WHERE CREATE_MONTH = '202605';
```

### 2.2 [2번 대상] 당월 신규 거래 상품의 기초 정보 동적 등록
전월에는 이월 재고 정보가 없었지만, 당월(`202606`) 일별 거래 정보(`IMDDIOTB`)가 있는 새로운 가공 상품에 대해 기초 재고 `0`, 단가 `0`인 요약 레코드를 사전 등록해 줍니다.
```sql
INSERT INTO hmsfns.IMMMIOTB (
    create_month, ms_no, goods_cd, chain_ms_no,
    start_qty, start_cost,
    purch_qty, purch_cost, purch_extra_cost,
    return_qty, return_cost,
    sale_qty, sale_cost, sale_extra_cost,
    in_qty, in_cost,
    out_qty, out_cost,
    disuse_qty, disuse_cost,
    adjust_qty, adjust_cost,
    tin_qty, tin_cost,
    tout_qty, tout_cost,
    end_qty, end_cost,
    returndis_qty, returndis_cost,
    move_in_qty, move_in_cost,
    move_out_qty, move_out_cost,
    wholesale_qty, wholesale_cost,
    wholesale_rt_qty, wholesale_rt_cost,
    start_cost_totavg, end_cost_totavg,
    purch_gab_extra_cost
)
SELECT DISTINCT
    '202606', L.ms_no, L.goods_cd,
    COALESCE((SELECT chain_ms_no FROM hmsfns.IMMMIOTB WHERE ms_no = L.ms_no LIMIT 1), 'NC0002'),
    0, 0,
    0, 0, 0,
    0, 0,
    0, 0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0, 0,
    0
FROM hmsfns.IMDDIOTB L
WHERE L.CREATE_DATE LIKE '202606%'
  AND L.MS_NO IN (SELECT MS_NO FROM hmsfns.MMEMBSTB WHERE CHAIN_NO = 'C001')
  AND NOT EXISTS (
      SELECT 1 FROM hmsfns.IMMMIOTB X
      WHERE X.CREATE_MONTH = '202606'
        AND X.MS_NO = L.MS_NO
        AND X.GOODS_CD = L.GOODS_CD
  );
```

### 2.3 [3번 대상] 오버플로우 금액 오류 방지 (더미 정산데이터 제거)
금액 필드 자릿수 초과로 인한 마감 연산 롤백을 방지하기 위해 1,000억 원 이상의 비정상 데이터 행을 삭제합니다.
```sql
DELETE FROM hmsfns.OBSLPDTB WHERE EXTRA_COST >= 10000000000;
```

---

## 3. 시스템 화면(UI)을 통한 데이터 가공 및 오류 조치 방법 (UI Workflows)

DB 직접 쿼리 제어가 불가능하거나 백오피스 UI 상에서 표준적인 비즈니스 흐름으로 데이터를 준비하려는 경우의 가이드입니다.

### 3.1 [1번 대상] 전월 재고 이월 데이터 생성
* **메뉴 경로**: 본사관리 > 재고관리 > **월말마감처리** (`hq_stock_00013`)
* **수행 방법**:
  1. 본사 계정(`shopadmin` / `0000`)으로 로그인하여 해당 화면에 진입합니다.
  2. 마감 연월을 당월의 직전월인 **`2026-05`**로 선택하고 **[조회]** 후 **[마감 실행]**을 클릭합니다.
  3. 전월 마감이 성공하면 시스템 내부적으로 당월(`202606`) 기초 재고(`start_qty`, `start_cost`)가 자동 이월되어 적재됩니다.

### 3.2 [2번 대상] 당월 신규 거래 등록 (원천 트랜잭션 축적)
당월에 첫 입고되는 신규 상품들의 입출고 및 매출 실적을 생성하여 기초 요약 행의 매핑 대상을 확보합니다.
* **매입(입고) 등록**: 
  * **메뉴**: 본사관리 > 매입관리 > **본사무발주입고등록** (`hq_vendor_00009`)
  * **방법**: 로그인 후 마감 대상월(2026년 6월 내 일자)로 가맹점을 지정하고, 대상 상품의 입고 수량/단가를 기입한 뒤 **[확정]** 버튼을 클릭합니다.
* **매출 등록**: 
  * **메뉴**: 매장관리 > 영업정보 > **당일매출등록/조회** (`st_sales_00004` 등)
  * **방법**: 매장 계정(`fnbcafe`) 로그인 후 당월 일자로 매출 상품과 수량을 수동 입력하여 **[저장]**을 완료합니다.

### 3.3 [3번 대상] 오버플로우 금액 오류 해제
* **메뉴 경로**: 본사관리 > 매입관리 > **부대비용 등록관리** (`hq_vendor_00008`)
* **수행 방법**:
  1. 본사 계정(`shopadmin`)으로 로그인하여 해당 화면에 진입합니다.
  2. 조회 범위 내에서 부대비용 총액이 수십~수백 억 원 이상으로 매우 크게 잡혀 있는 매입 전표(더미 전표)를 찾아 더블클릭합니다.
  3. 상세 팝업창에서 해당 전표에 배분된 부대비용 단가(`EXTRA_COST`) 값을 정상 수치(예: `0` 또는 현실적인 실비 금액)로 수정한 뒤 **[저장]**을 클릭하여 오류를 해제합니다.
