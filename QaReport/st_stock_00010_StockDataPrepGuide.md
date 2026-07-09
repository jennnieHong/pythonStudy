# HMS 점간이동(st_stock_00010) 테스트용 사전 데이터 구축 가이드

본 문서는 HMS 영업정보시스템의 **점간이동 등록/확정(st_stock_00010)** 화면에서 양수 재고를 세팅하고 E2E 프로세스를 정상 테스트하기 위한 EDB(PostgreSQL) 사전 데이터 구축 절차를 안내합니다.

---

## 1. 사전 필수 확인 사항 (매장 및 사용자)

점간이동 전표등록 시, **보내는 매장(이출)**과 **받는 매장(이입)**의 속성이 일치하지 않거나 권한이 맞지 않으면 저장되지 않습니다.

* **매장 창고 속성 (`MMEMBSTB.SHOP_WH_YN`)**:
  * 보내는 매장과 받는 매장의 `SHOP_WH_YN` (선매입 매장여부) 속성이 동일해야 합니다.
  * 보내는 매장이 선매입 매장(`SHOP_WH_YN = 'Y'`)인 경우, 받는 매장도 반드시 선매입 매장(`SHOP_WH_YN = 'Y'`)이어야 합니다. 그렇지 않으면 `fnChkPrePurchMs` 검증 로직에서 에러가 납니다.
* **로그인 계정**:
  * **보내는 매장 계정 (이출)**: `fnbcafe` (매장코드: `NC0007`) - *이출 등록/확정용*
  * **받는 매장 계정 (이입)**: `shopbrand` (매장코드: `NC0003`) - *이입(입고) 확정용*

---

## 2. 사전 데이터 구축 4단계 SQL

DBeaver 등 DB 툴을 통해 EDB 데이터베이스(`edb`, 스키마: `hmsfns`)에 접속한 후 아래 쿼리들을 실행하여 재고 및 마스터 정보를 세팅합니다.

### 1단계: 글로벌 상품 마스터 (`TGOODSTB`) 확인
해당 체인(`C001`)에 상품이 존재하고 활성화되어 있는지 확인합니다. (예: `T0000033` 상품)
```sql
SELECT chain_no, goods_cd, goods_nm, use_fg, goods_use_fg 
  FROM hmsfns.tgoodstb 
 WHERE goods_cd = 'T0000033' AND chain_no = 'C001';
```

### 2단계: 매장별 상품 마스터 (`MGOODSTB`) 등록
상품이 글로벌 마스터에 있어도, **보내는 매장과 받는 매장 양쪽의 매장 상품 마스터(`MGOODSTB`)에 모두 등록**되어 있어야 화면에서 검색 및 전표 저장이 가능합니다.

> [!IMPORTANT]
> **받는 매장(이입 매장)의 상품 및 카테고리 등록 필수성**
> 1. **상품 마스터 등록**: 보내는 매장뿐만 아니라, 수령할 **받는 매장(이입)의 `MGOODSTB`**에도 해당 상품 코드(`goods_cd`)가 등록(`use_fg = '0'`)되어 있어야 합니다.
> 2. **매장 분류(카테고리) 마스터 등록**: 해당 상품에 지정된 대/중/소분류(`001`/`009`/`001` 등) 정보가 받는 매장의 **매장 분류 마스터(`MMLCLSTB`, `MMMCLSTB`, `MMSCLSTB`)**에도 등록되어 있어야 합니다.
>    * 현재고 조회 시 분류 테이블과 내부 조인(Inner Join)을 수행하기 때문에, 매장 분류 매핑이 누락되면 `MGOODSTB`에 상품이 있더라도 **조회 화면에서 해당 상품이 검색되지 않는 현상**이 발생합니다.
>    * 받는 매장(`NC0003` 등) 마스터에 상품과 분류가 등록되지 않은 상태에서 입고 확정을 처리하면, 재고 수불 원장 데이터 정합성 오류가 발생할 수 있습니다.

```sql
-- 1. 매장별 등록 여부 조회
SELECT ms_no, goods_cd, use_fg 
  FROM hmsfns.mgoodstb 
  WHERE goods_cd = 'T0000033' AND ms_no IN ('NC0003', 'NC0006', 'NC0007');

-- 2. 미등록 매장에 상품 마스터 추가 (예: NC0003 매장에 추가할 경우)
INSERT INTO hmsfns.mgoodstb (
    ms_no, goods_cd, goods_nm, use_fg, create_fg, 
    create_id, create_dtime, last_id, last_dtime
) VALUES (
    'NC0003', 'T0000033', '(Food)대바트_대', '0', '1', 
    'admin', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'admin', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS')
);
```

### 3단계: 현재고 테이블 (`IMCRIOTB`) 재고 수량/금액 설정
화면 우측의 품목 검색 팝업에서 조회되는 현재고(`CUR_QTY`) 수량은 **`hmsfns.imcriotb`** 테이블에서 실시간 조회하여 반환합니다. 보내는 매장에 정상적인 양수 재고를 세팅해 줍니다.
```sql
-- EDB/PostgreSQL 호환 MERGE 쿼리
MERGE INTO hmsfns.imcriotb A
USING (
  SELECT 'NC0007' AS ms_no,           -- 보내는 매장 코드 (예: fnbcafe 매장)
         'T0000033' AS goods_cd,      -- 대상 상품 코드
         'C001NC0007' AS chain_ms_no,  -- 체인코드 + 매장코드 조합
         100.0 AS cur_qty,            -- 세팅할 현재고 수량 (예: 100개)
         400000.0 AS cur_cost         -- 세팅할 현재고 금액 (예: 400,000원)
) B
ON (A.ms_no = B.ms_no AND A.goods_cd = B.goods_cd)
WHEN MATCHED THEN
  UPDATE SET A.cur_qty = B.cur_qty, A.cur_cost = B.cur_cost
WHEN NOT MATCHED THEN
  INSERT (ms_no, goods_cd, chain_ms_no, cur_qty, cur_cost)
  VALUES (B.ms_no, B.goods_cd, B.chain_ms_no, B.cur_qty, B.cur_cost);
```

### 4단계: 월수불 원가 테이블 (`TB_IMMMIO_COST` & `IMMMIOTB`) 수불 레코드 초기화
받는 매장에서 최종 확정(`PROC_FG = '2'`)할 때, 수불 원가 연동 연산(`Sp_SUB_TOT_AVG_SINGLE_P`)이 구동됩니다. 이때 당월(예: 2026년 6월 $\rightarrow$ `'202606'`) 기초 수불 정보가 없는 경우 에러가 발생하므로 수불 기초 레코드를 생성해 줍니다.
```sql
-- 1. 당월 수불 원가 레코드 존재 여부 확인
SELECT * FROM hmsfns.tb_immmio_cost 
 WHERE ym = '202606' AND ms_no = 'NC0007' AND goods_cd = 'T0000033';

-- 2. 존재하지 않는 경우 기초 데이터 등록 (당월 기준 수량 0, 단가 0으로 세팅)
INSERT INTO hmsfns.tb_immmio_cost (
    ym, chain_no, ms_no, goods_cd, start_qty, start_cost, start_cost_totavg
) VALUES (
    '202606', 'C001', 'NC0007', 'T0000033', 0, 0, 0
);
```

---

## 3. 요약 및 팁
* 화면 우측 품목 검색 팝업에서 특정 상품이 아예 조회되지 않는다면 **2단계 (`MGOODSTB` 매장 등록)**를 점검해야 합니다.
* 상품은 보이지만 현재고가 0이거나 마이너스로 보인다면 **3단계 (`IMCRIOTB` 재고 설정)** 쿼리를 실행하여 강제로 수량을 할당한 뒤 테스트를 수행하세요.

---

## 4. [참고] 화면별 현재고 조회 방식 차이 (데이터 불일치 원인)

**점간이동 등록/확정(st_stock_00010) 화면**과 **현재고조회(st_stock_00007) 화면**의 현재고 수량이 서로 다르게 조회되는 경우가 있습니다. (예: `st_stock_00010`에서는 50개인데 `st_stock_00007`에서는 0개로 표시됨) 

이는 두 화면이 재고 데이터를 조회하고 계산하는 방식이 서로 다르기 때문입니다.

### ① 점간이동 등록/확정 (`st_stock_00010`) - 품목 검색 팝업
* **조회 대상 테이블**: 실시간 현재고 테이블인 **`hmsfns.IMCRIOTB`**의 `CUR_QTY` 필드를 직접 조회합니다.
* **특징**: DB에 직접 등록/수정한 현재고 상태가 **실시간으로 즉시 반영**되어 노출됩니다.

### ② 현재고조회 (`st_stock_00007`)
* **조회 대상 테이블**: 실시간 테이블을 보지 않고, **월수불 테이블(`IMMMIOTB`)과 일수불 테이블(`IMDDIOTB`)**의 데이터를 합산하여 동적으로 계산합니다.
* **재고 계산 공식**:
  $$\text{현재고} = \text{전월 말 마감재고 (MM\_QTY)} + \text{당월 1일부터 조회일까지의 일수불 변동량 합계 (DD\_QTY)}$$
  * `MM_QTY`: `IMMMIOTB`에서 조회 월의 이전 달 데이터 중 최신 월의 이월 재고(`END_QTY`).
  * `DD_QTY`: `IMDDIOTB`에서 당월 1일부터 조회일까지의 모든 변동량(`PURCH_QTY`, `SALE_QTY`, `MOVE_IN_QTY`, `MOVE_OUT_QTY` 등)의 합산.
* **데이터 차이 원인**:
  * 테스트 매장(예: `NC0007`)에 특정 상품(`T0000033`)의 이전 달 수불 마감 레코드(`IMMMIOTB`에서 조회 시점의 전월 이하 데이터)가 없거나 값이 0이고, 당월 일수불 변동 기록(`IMDDIOTB`)도 없는 상태이기 때문에 `0`으로 계산되는 것입니다.

### ③ 데이터 동기화 방법 (일치시키기)
* **재고반영 배치 실행**: 확정 처리된 점간이동 데이터는 재고반영 배치(`DmIMTR01Job`)가 구동되는 시점에 `IMDDIOTB`(일수불) 및 `IMMMIOTB`(월수불)에 정상 반영됩니다. 배치가 정상적으로 완료되면 두 화면의 재고 수량이 일치하게 됩니다.

