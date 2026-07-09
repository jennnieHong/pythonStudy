# 본사 현재고 조회 (`hq_stock_00001`) 데이터 처리 및 연산 가이드

본 문서는 본사 현재고 조회 화면([hq_stock_00001.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/stock/hq_stock_00001/hq_stock_00001.jsp))에서 표시되는 현재 재고 수량의 연산 공식, 상세 팝업(일수불 대장, 레시피 판매이력)의 데이터 집계 로직 및 관련 데이터베이스 테이블 구조를 설명하는 개발/QA 가이드라인입니다.

---

## 1. 실시간 현재고 연산 공식 및 데이터 소스

본 화면에서 상품별로 보여주는 **현재고 수량(CUR_QTY)** 및 **현재고 금액(CUR_UPRICE)**은 현재고 원장 테이블(`hmsfns.IMCRIOTB`)을 직접 조회하지 않고, **전월말 기말재고와 당월의 누적 변동량을 실시간 합산**하여 동적으로 계산해 냅니다. ([Hq_Stock_00001_Sql.xml - selectCurQtyList](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/stock/Hq_Stock_00001_Sql.xml#L49-L186) 쿼리 참조)

### 📌 현재고 수량 계산 공식 (CUR_QTY)
$$현재고\ 수량(CUR\_QTY) = 전월말\ 기말재고(X.END\_QTY) + 당월\ 일별\ 누적\ 변동량(C.DD\_QTY)$$

1. **전월말 기말재고 (`X.END_QTY`)**:
   - 대상 테이블: 월수불 테이블 (`hmsfns.IMMMIOTB` X)
   - 조건: 조회하려는 기준일자(`searchDate`, YYYYMMDD) 기준 **직전월(`CREATE_MONTH = searchDate - 1 month`)**의 기말재고량(`END_QTY`)을 가져옵니다.
2. **당월 일별 누적 변동량 (`C.DD_QTY`)**:
   - 대상 테이블: 일수불 테이블 (`hmsfns.IMDDIOTB` C)
   - 조건: 당월 1일부터 조회 기준일자(`searchDate`) 사이의 모든 변동 이력을 합산합니다.
   - **변동량 상세 연산식**:
     $$DD\_QTY = \sum (PURCH\_QTY - RETURN\_QTY - SALE\_QTY + IN\_QTY - OUT\_QTY + ADJUST\_QTY - DISUSE\_QTY + MOVE\_IN\_QTY - MOVE\_OUT\_QTY - RETURNDIS\_QTY + WHOLESALE\_QTY)$$

### 📌 변동량 구성 항목 세부 내역
| 컬럼명 | 설명 | 부호 | 관련 화면/트랜잭션 발생원 |
| :--- | :--- | :---: | :--- |
| `PURCH_QTY` | 매입 수량 | `+` | 매장 입고/발주 확정 등록 |
| `RETURN_QTY` | 반품 수량 | `-` | 매장 반품 등록 |
| `SALE_QTY` | 매출 수량 | `-` | POS 매출 확정 (수불 분해 트리거 적용) |
| `IN_QTY` | 기타 입고 | `+` | 본사/매장 기타 입고 등록 |
| `OUT_QTY` | 기타 출고 | `-` | 본사/매장 기타 출고 등록 |
| `ADJUST_QTY` | 재고 조정 | `+` | 본사/매장 재고조정등록 (`hq_stock_00005` / `st_stock_00001`) |
| `DISUSE_QTY` | 재고 폐기 | `-` | 본사/매장 재고폐기등록 (`hq_stock_00007` / `st_stock_00004`) |
| `MOVE_IN_QTY` | 점간 이동 입고 | `+` | 매장간 재고 이동 (입고점) |
| `MOVE_OUT_QTY` | 점간 이동 출고 | `-` | 매장간 재고 이동 (출고점) |
| `RETURNDIS_QTY` | 반품 폐기 | `-` | 반품 후 폐기 처리 수량 |
| `WHOLESALE_QTY` | 사입 입고 | `+` | 로컬 가맹점의 본사외 사입 입고 수량 |

---

## 2. 상세 팝업 데이터 처리 로직

### 📌 2.1 일별 수불 대장 조회 (`selectStockList`)
* **기능**: 현재고 조회 그리드 행을 더블클릭할 시 기동되며, 해당 매장/상품의 지정 기간 동안 일자별 수불 변동 명세를 출력합니다.
* **대상 테이블**: 일수불 테이블 (`hmsfns.IMDDIOTB` ID), 월수불 테이블 (`hmsfns.IMMMIOTB` IM), 상품 마스터 (`hmsfns.MGOODSTB` GV)
* **집계 원리**:
  * 해당 월의 월수불 레코드(`IMMMIOTB`)에서 당월 기초재고 수량(`START_QTY`)을 가져와 시작점으로 표시합니다.
  * 일수불 테이블(`IMDDIOTB`)의 각 일자별 레코드를 날짜 오름차순으로 스캔하여, 수불 구분별 수량과 원가를 그리드에 일자별 라인으로 매핑합니다.

### 📌 2.2 원부자재 레시피 판매 내역 조회 (`getRecipeSaleList`)
* **기능**: 현재고 조회 상품이 레시피/원부재료일 경우, 해당 재료가 사용되어 차감된 메뉴 판매 상세 이력을 조회합니다.
* **대상 테이블**: 레시피 판매 로그 (`hmsfns.TB_SL_RECIPE_GOODS`), 세트 판매 로그 (`hmsfns.TB_SL_SET_GOODS`), 매장 정보 (`hmsfns.MMEMBSTB`)
* **집계 원리**:
  * 판매된 레시피 상품의 매출 이력(`TB_SL_RECIPE_GOODS`)을 기준으로 판매수량(`SALE_QTY`)과 레시피 설정상 단위 중량(`RECIPE_WEIGHT`)을 곱하여 실제 소모된 원부자재의 환산 사용 중량(`USED_WEIGHT`)을 실시간 역산하여 출력합니다.

---

## 3. 야간 배치를 통한 현재고 물리 테이블(`IMCRIOTB`) 동기화

조회 화면은 `IMMMIOTB` + `IMDDIOTB` 구조로 실시간 동적인 합산을 수행하지만, 신규 상품 등록 모달 팝업 등에서 **현재 재고량 기준 필터링**을 수행하거나 타 화면의 원장 검증을 진행할 때는 가맹점 실시간 현재고 원장 테이블인 **`hmsfns.IMCRIOTB`**를 직접 조회합니다.

이 `IMCRIOTB` 테이블은 아래와 같이 야간에 가동되는 배치 혹은 수동 시뮬레이션 쿼리를 통해 동기화됩니다.

```sql
-- [야간 배치 시동 시 동기화 DML 흐름 모사]

-- 1) 실시간 현재고 테이블 (IMCRIOTB) 업데이트
UPDATE hmsfns.IMCRIOTB I
   SET I.CUR_QTY  = I.CUR_QTY  + #{trlgQty}
     , I.CUR_COST = I.CUR_COST + #{trlgCost}
 WHERE I.MS_NO    = #{msNo}
   AND I.GOODS_CD = #{goodsCd};

-- 2) 일수불 누적 테이블 (IMDDIOTB) 업데이트
UPDATE hmsfns.IMDDIOTB
   SET ADJUST_QTY  = ADJUST_QTY  + #{trlgQty}
     , ADJUST_COST = ADJUST_COST + #{trlgCost}
 WHERE CREATE_DATE = #{procDate}
   AND MS_NO       = #{msNo}
   AND GOODS_CD    = #{goodsCd};

-- 3) 월수불 누적 테이블 (IMMMIOTB) 업데이트
UPDATE hmsfns.IMMMIOTB
   SET ADJUST_QTY  = ADJUST_QTY  + #{trlgQty}
     , ADJUST_COST = ADJUST_COST + #{trlgCost}
     , END_QTY     = END_QTY     + #{trlgQty}
     , END_COST    = END_COST    + #{trlgCost}
 WHERE CREATE_MONTH = SUBSTR(#{procDate}, 1, 6)
   AND MS_NO        = #{msNo}
   AND GOODS_CD     = #{goodsCd};
```
