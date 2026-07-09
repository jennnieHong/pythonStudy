# HMS 점간이동 등록/확정(hq_stock_00011) 테스트용 사전 데이터 구축 가이드

본 문서는 HMS 영업정보시스템의 **점간이동 등록/확정(hq_stock_00011)** 화면에서 테스트를 위해 양수 재고를 세팅하고 E2E 프로세스를 정상적으로 수행하기 위한 EDB(PostgreSQL) 사전 데이터 구축 절차를 안내합니다.

---

## 1. 사전 필수 확인 사항 (매장 및 사용자)

점간이동 전표 등록 시, **보내는 매장(이출)**과 **받는 매장(이입)**의 선입고(선매입) 창고 속성이 맞지 않거나 권한이 다르면 저장 또는 확정이 되지 않습니다.

* **매장 창고 속성 (`MMEMBSTB.SHOP_WH_YN`)**:
  * 보내는 매장과 받는 매장의 `SHOP_WH_YN` (선매입 매장여부) 속성이 동일해야 합니다.
  * 본 가이드 및 E2E 테스트에서는 브랜드숍 체인(`C001`) 소속 매장인 **보내는 매장: `NC0006` (KITCHEN)**과 **받는 매장: `NC0007` (CAFE)**을 조합으로 사용합니다.
* **로그인 계정**:
  * **본사/브랜드숍 관리자 계정**: `shopadmin` (패스워드: `0000`)
  * 본 계정은 체인 `C001` 권한을 가지고 있으며 가맹점 간 점간이동 등록 및 확정을 모두 수행할 수 있습니다.

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
상품이 글로벌 마스터에 존재하더라도, **보내는 매장과 받는 매장 양쪽의 매장 상품 마스터(`MGOODSTB`)에 모두 등록**되어 있어야 화면에서 검색 및 전표 저장이 가능합니다.

> [!IMPORTANT]
> **이입/이출 매장 양쪽의 상품 마스터 및 분류 등록 필수**
> 1. **상품 마스터 등록**: 보내는 매장(`NC0006`)뿐만 아니라, 수령할 **받는 매장(`NC0007`)의 `MGOODSTB`**에도 해당 상품 코드(`goods_cd`)가 등록(`use_fg = '0'`)되어 있어야 합니다.
> 2. **매장 분류(카테고리) 마스터 등록**: 해당 상품에 지정된 대/중/소분류 정보가 받는 매장의 **매장 분류 마스터(`MMLCLSTB`, `MMMCLSTB`, `MMSCLSTB`)**에도 등록되어 있어야 정상적으로 목록에 매핑됩니다.

```sql
-- 1. 매장별 등록 여부 조회
SELECT ms_no, goods_cd, use_fg 
  FROM hmsfns.mgoodstb 
 WHERE goods_cd = 'T0000033' AND ms_no IN ('NC0006', 'NC0007');

-- 2. 미등록 매장에 상품 마스터 추가 (예: NC0007 매장에 추가할 경우)
INSERT INTO hmsfns.mgoodstb (
    ms_no, goods_cd, goods_nm, use_fg, create_fg, 
    create_id, create_dtime, last_id, last_dtime
) VALUES (
    'NC0007', 'T0000033', '(Food)식전바게트_마더스오븐', '0', '1', 
    'admin', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'admin', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS')
);
```

### 3단계: 현재고 테이블 (`IMCRIOTB`) 재고 수량/금액 설정
화면 우측의 품목 검색 팝업에서 조회되는 현재고(`CUR_QTY`) 수량은 **`hmsfns.imcriotb`** 테이블에서 실시간 조회하여 반환합니다. 보내는 매장(`NC0006`)에 양수 재고를 세팅해 줍니다.
```sql
-- EDB/PostgreSQL 호환 MERGE 쿼리 (NC0006 매장에 재고 100개 할당)
MERGE INTO hmsfns.imcriotb A
USING (
  SELECT 'NC0006' AS ms_no,           -- 보내는 매장 코드
         'T0000033' AS goods_cd,      -- 대상 상품 코드
         'C001NC0006' AS chain_ms_no,  -- 체인코드 + 매장코드 조합
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
받는 매장에서 최종 확정(`PROC_FG = '2'`)할 때, 수불 원가 연동 연산(`Sp_SUB_TOT_AVG_SINGLE_P`)이 구동됩니다. 이때 당월(예: 2026년 6월 $\rightarrow$ `'202606'`) 기초 수불 정보가 없는 경우 에러가 발생하므로 수불 기초 레코드를 생성해 줍니다. (보내는 매장과 받는 매장 양쪽 모두 필요)
```sql
-- 1. 당월 수불 원가 레코드 존재 여부 확인
SELECT * FROM hmsfns.tb_immmio_cost 
 WHERE ym = '202606' AND ms_no IN ('NC0006', 'NC0007') AND goods_cd = 'T0000033';

-- 2. 존재하지 않는 경우 기초 데이터 등록 (당월 기준 수량 0, 단가 0으로 세팅)
INSERT INTO hmsfns.tb_immmio_cost (
    ym, chain_no, ms_no, goods_cd, start_qty, start_cost, start_cost_totavg
) VALUES 
('202606', 'C001', 'NC0006', 'T0000033', 0, 0, 0),
('202606', 'C001', 'NC0007', 'T0000033', 0, 0, 0);
```

---

## 3. 요약 및 팁
* 화면 우측 품목 검색 팝업에서 특정 상품이 아예 조회되지 않는다면 **2단계 (`MGOODSTB` 매장 등록)** 및 분류 체계 연동을 점검해야 합니다.
* 상품은 보이지만 현재고가 0이거나 마이너스로 보인다면 **3단계 (`IMCRIOTB` 재고 설정)** 쿼리를 실행하여 강제로 수량을 할당한 뒤 테스트를 수행하세요.
* 확정 처리를 누를 때 원가 수불 테이블 처리 에러가 발생한다면 **4단계 (`TB_IMMMIO_COST` 기초 레코드)**가 올바른 조회 월(YM)에 맞춰 생성되었는지 확인해 보시기 바랍니다.
