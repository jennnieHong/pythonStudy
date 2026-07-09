# 본사 재고 조정 반영 및 배치 시뮬레이션 가이드 (`Hq_Stock_00001_DataInputGuide_조정재고`)

본 문서는 본사 재고조정등록 화면([hq_stock_00005.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/stock/hq_stock_00005/hq_stock_00005.jsp))에서 재고 조정 확정 처리를 진행했을 때, 현재고 조회 화면([hq_stock_00001.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/stock/hq_stock_00001/hq_stock_00001.jsp))에 즉시 재고량이 연동되지 않는 원인과, 이를 강제로 반영하기 위해 파이썬(Python)으로 배치를 모사하여 트랜잭션을 실행하는 방법 및 테스트 변수 수정 가이드를 정리한 자료입니다.

---

## 1. 재고 조정 미반영 원인 분석 (화면 vs 배치)

### 📌 비동기 배치 연동 구조
* **화면 처리 (`hq_stock_00005`)**: 
  조정 수량을 입력하고 저장(확정)하면, 시스템은 즉시 물리적인 현재고 원장(`IMCRIOTB`)이나 일수불(`IMDDIOTB`)/월수불(`IMMMIOTB`) 테이블의 수량을 직접 수정하지 않습니다. 
  대신, **수불 로그 적재 테이블인 `hmsfns.IMTRLGTB`**에 상태 값 `PROC_YN = 'N'` (미처리)으로 로그 레코드만을 적재(DML Insert)합니다.
* **배치 처리 (`DmIMTR01`)**: 
  매일 새벽에 구동되는 수불 야간 배치 프로그램이 `IMTRLGTB` 테이블에서 `PROC_YN = 'N'`인 미처리 수불 로그를 읽어와 순차적으로 대상 상품/매장의 현재고(`IMCRIOTB`), 일수불(`IMDDIOTB`), 월수불(`IMMMIOTB`) 테이블의 재고 수량/금액을 증감시킨 후, 처리 완료된 로그를 백업 테이블(`hmsfns.IMTRBKTB`)로 이관하고 원본 로그 테이블(`IMTRLGTB`)에서 삭제 처리합니다.
* **결론**: 
  따라서 수동 배치 모사 스크립트를 수행하거나 야간 배치가 정상 동작하기 전까지는, `IMTRLGTB`에만 데이터가 머물러 있게 되므로 **실시간 합산 기반의 현재고 조회 화면(`hq_stock_00001`)에는 조정량이 즉시 반영되지 않고 0개(혹은 이전 상태)로 표시**됩니다.

---

## 2. Python 강제 배치 시뮬레이션 스크립트 원문

아래 파이썬 코드는 야간 배치 프로그램(`DmIMTR01`)의 DML 수행 로직을 단계별로 모사하여, 특정 매장/상품에 대해 입력된 수불 로그 데이터를 물리 테이블로 밀어 넣고 처리 로그를 백업 및 삭제하는 일련의 과정을 단일 트랜잭션으로 처리하는 스크립트입니다.

```python
import psycopg2

try:
    # 1. PostgreSQL (EDB) 데이터베이스 연결 설정
    conn = psycopg2.connect(
        host='192.168.10.206', 
        port='5432', 
        database='edb', 
        user='hmsfns_adm', 
        password='astems2!'
    )
    cur = conn.cursor()
    
    print("=== [시작] 야간 배치 모사 DML 실행 ===")
    
    # ----------------------------------------------------
    # [설정 변수 정의] - 테스트 목적에 따라 이 값을 수정하여 적용합니다.
    # ----------------------------------------------------
    target_ms_no      = 'NC0006'     # 대상 매장 코드
    target_goods_cd   = 'T0000001'   # 대상 상품 코드
    target_chain_ms   = 'NC0002'     # 본사/체인 매장 코드
    target_date       = '20260605'   # 작업 기준 일자 (YYYYMMDD)
    target_month      = '202606'     # 작업 기준 월 (YYYYMM)
    adjust_qty        = 10           # 조정 수량 (+/- 가능)
    adjust_cost       = 350000       # 조정 금액 (수량 * 단가 등)
    # ----------------------------------------------------
    
    # 1단계: IMCRIOTB (실시간 현재고 원장) 반영
    # - 해당 매장/상품 레코드가 없으면 신규 INSERT, 있으면 기존 수량에 누적 UPDATE
    cur.execute("SELECT COUNT(*) FROM hmsfns.IMCRIOTB WHERE MS_NO = %s AND GOODS_CD = %s", (target_ms_no, target_goods_cd))
    if cur.fetchone()[0] == 0:
        print(f"IMCRIOTB에 {target_ms_no} / {target_goods_cd} 레코드가 없어 신규 INSERT합니다.")
        cur.execute("""
            INSERT INTO hmsfns.IMCRIOTB (MS_NO, GOODS_CD, CHAIN_MS_NO, CUR_QTY, CUR_COST)
            VALUES (%s, %s, %s, %s, %s)
        """, (target_ms_no, target_goods_cd, target_chain_ms, adjust_qty, adjust_cost))
    else:
        print("IMCRIOTB에 레코드가 존재하여 수량을 UPDATE합니다.")
        cur.execute("""
            UPDATE hmsfns.IMCRIOTB 
               SET CUR_QTY = CUR_QTY + %s, CUR_COST = CUR_COST + %s 
             WHERE MS_NO = %s AND GOODS_CD = %s
        """, (adjust_qty, adjust_cost, target_ms_no, target_goods_cd))
        
    # 2단계: IMDDIOTB (일수불 누적 원장) 반영
    # - 해당 일자/매장/상품 레코드가 없으면 신규 INSERT, 있으면 기존 조정 수량에 누적 UPDATE
    cur.execute("""
        SELECT COUNT(*) FROM hmsfns.IMDDIOTB 
         WHERE CREATE_DATE = %s AND MS_NO = %s AND GOODS_CD = %s
    """, (target_date, target_ms_no, target_goods_cd))
    
    if cur.fetchone()[0] == 0:
        print(f"IMDDIOTB에 {target_date} 레코드가 없어 신규 INSERT합니다.")
        cur.execute("""
            INSERT INTO hmsfns.IMDDIOTB (
                CREATE_DATE, MS_NO, GOODS_CD, CHAIN_MS_NO, 
                PURCH_QTY, PURCH_COST, RETURN_QTY, RETURN_COST, 
                SALE_QTY, SALE_COST, IN_QTY, IN_COST, OUT_QTY, OUT_COST, 
                DISUSE_QTY, DISUSE_COST, ADJUST_QTY, ADJUST_COST, 
                TIN_QTY, TIN_COST, TOUT_QTY, TOUT_COST
            ) VALUES (
                %s, %s, %s, %s,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, %s, %s, 
                0, 0, 0, 0
            )
        """, (target_date, target_ms_no, target_goods_cd, target_chain_ms, adjust_qty, adjust_cost))
    else:
        print("IMDDIOTB에 레코드가 존재하여 조정수량을 누적 UPDATE합니다.")
        cur.execute("""
            UPDATE hmsfns.IMDDIOTB 
               SET ADJUST_QTY = ADJUST_QTY + %s, ADJUST_COST = ADJUST_COST + %s 
             WHERE CREATE_DATE = %s AND MS_NO = %s AND GOODS_CD = %s
        """, (adjust_qty, adjust_cost, target_date, target_ms_no, target_goods_cd))
        
    # 3단계: IMMMIOTB (월수불 누적 원장) 반영
    # - 해당 월/매장/상품 레코드가 없으면 신규 INSERT, 있으면 기존 조정 및 기말 수량에 누적 UPDATE
    cur.execute("""
        SELECT COUNT(*) FROM hmsfns.IMMMIOTB 
         WHERE CREATE_MONTH = %s AND MS_NO = %s AND GOODS_CD = %s
    """, (target_month, target_ms_no, target_goods_cd))
    
    if cur.fetchone()[0] == 0:
        print(f"IMMMIOTB에 {target_month} 레코드가 없어 신규 INSERT합니다.")
        cur.execute("""
            INSERT INTO hmsfns.IMMMIOTB (
                CREATE_MONTH, MS_NO, GOODS_CD, CHAIN_MS_NO, 
                START_QTY, START_COST, PURCH_QTY, PURCH_COST, RETURN_QTY, RETURN_COST, 
                SALE_QTY, SALE_COST, IN_QTY, IN_COST, OUT_QTY, OUT_COST, 
                DISUSE_QTY, DISUSE_COST, ADJUST_QTY, ADJUST_COST, TIN_QTY, TIN_COST, TOUT_QTY, TOUT_COST,
                END_QTY, END_COST
            ) VALUES (
                %s, %s, %s, %s,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, %s, %s, 0, 0, 0, 0,
                %s, %s
            )
        """, (target_month, target_ms_no, target_goods_cd, target_chain_ms, adjust_qty, adjust_cost, adjust_qty, adjust_cost))
    else:
        print("IMMMIOTB에 레코드가 존재하여 조정수량/기말재고를 누적 UPDATE합니다.")
        cur.execute("""
            UPDATE hmsfns.IMMMIOTB 
               SET ADJUST_QTY = ADJUST_QTY + %s, ADJUST_COST = ADJUST_COST + %s,
                   END_QTY = END_QTY + %s, END_COST = END_COST + %s
             WHERE CREATE_MONTH = %s AND MS_NO = %s AND GOODS_CD = %s
        """, (adjust_qty, adjust_cost, adjust_qty, adjust_cost, target_month, target_ms_no, target_goods_cd))
        
    # 4단계: IMTRLGTB (미처리 수불 로그) 백업 및 삭제 처리
    # - PROC_YN = 'N' 상태인 조정 내역을 백업 테이블(IMTRBKTB)로 이관(PROC_YN='Y' 처리) 후 원본 삭제
    print("IMTRLGTB 로그를 IMTRBKTB 백업 테이블로 이관하고 삭제합니다.")
    cur.execute("""
        INSERT INTO hmsfns.IMTRBKTB (
            TRBK_DTIME, MS_NO, PROC_FG, TRBK_SEQ, PROC_DATE, 
            CHAIN_MS_NO, GOODS_CD, TRBK_QTY, TRBK_COST, PROC_YN
        )
        SELECT TRLG_DTIME, MS_NO, PROC_FG, TRLG_SEQ, PROC_DATE, 
               CHAIN_MS_NO, GOODS_CD, TRLG_QTY, TRLG_COST, 'Y'
          FROM hmsfns.IMTRLGTB
         WHERE MS_NO     = %s
           AND PROC_DATE = %s
           AND PROC_FG   = 'A'
           AND GOODS_CD  = %s
    """, (target_ms_no, target_date, target_goods_cd))
    
    cur.execute("""
        DELETE FROM hmsfns.IMTRLGTB
         WHERE MS_NO     = %s
           AND PROC_DATE = %s
           AND PROC_FG   = 'A'
           AND GOODS_CD  = %s
    """, (target_ms_no, target_date, target_goods_cd))
    
    # 트랜잭션 정상 완료 시 커밋
    conn.commit()
    print("=== [완료] 데이터 커밋 성공 ===")
    
    # 5단계: 반영 후 현재고 조회 화면 쿼리 기준 값 즉시 검증
    print("\n=== [검증] 현재고 조회 쿼리(selectCurQtyList) 모사 결과 ===")
    cur.execute("""
        SELECT A.MS_NO, A.GOODS_CD, A.GOODS_NM, NVL(X.END_QTY,0) AS PREV_END_QTY, NVL(C.DD_QTY,0) AS CUR_DD_QTY, (NVL(X.END_QTY,0) + NVL(C.DD_QTY,0)) AS FINAL_CUR_QTY
          FROM (SELECT MS_NO, GOODS_CD, GOODS_NM FROM hmsfns.MGOODSTB WHERE MS_NO = %s AND GOODS_CD = %s) A
          LEFT OUTER JOIN hmsfns.IMMMIOTB X ON A.GOODS_CD = X.GOODS_CD AND A.MS_NO = X.MS_NO AND X.CREATE_MONTH = '202605'
          LEFT OUTER JOIN (
              SELECT GOODS_CD, MS_NO, SUM(PURCH_QTY - RETURN_QTY - SALE_QTY + IN_QTY - OUT_QTY + ADJUST_QTY - DISUSE_QTY + MOVE_IN_QTY - MOVE_OUT_QTY - RETURNDIS_QTY + WHOLESALE_QTY) AS DD_QTY
                FROM hmsfns.IMDDIOTB
               WHERE CREATE_DATE BETWEEN '20260601' AND %s
               GROUP BY GOODS_CD, MS_NO
          ) C ON A.GOODS_CD = C.GOODS_CD AND A.MS_NO = C.MS_NO
    """, (target_ms_no, target_goods_cd, target_date))
    
    row = cur.fetchone()
    if row:
        print(f"매장: {row[0]}, 상품: {row[1]}, 상품명: {row[2]}")
        print(f"  - 5월 이월 기말재고 (X.END_QTY): {row[3]}")
        print(f"  - 6월 누적 변동량 (C.DD_QTY): {row[4]}")
        print(f"  - 최종 계산된 현재고 (CUR_QTY): {row[5]}")
    else:
        print("조회 결과 없음 (상품 매핑 오류 가능성)")
        
    cur.close()
    conn.close()
except Exception as e:
    print("배치 시뮬레이션 중 오류 발생:", e)
```

---

## 3. 화면 테스트 시 직접 수정하여 적용할 변수 가이드

다른 상품코드나 매장, 다른 일자, 다른 재고 조정 수량으로 화면 검증 및 데이터 연동 테스트를 진행하고자 할 때, 위 파이썬 코드 상에서 **수정해야 할 핵심 변수들**은 다음과 같습니다.

### 📌 3.1 주요 파라미터 값 매핑 가이드 (코드 내 17~25라인)

| 변수명 | 의미 | 수정 예시 및 주의사항 |
| :--- | :--- | :--- |
| `target_ms_no` | **조정 대상 매장 코드** | 화면 상단 `매장선택`에서 선택한 매장 코드입니다. (예: `'NC0006'`) |
| `target_goods_cd` | **조정 대상 상품 코드** | 화면 그리드에 추가하여 수량을 입력한 상품 코드입니다. (예: `'T0000001'`) |
| `target_chain_ms` | **본사/체인 매장 코드** | 상품 마스터에 지정된 관리 체인 매장 코드입니다. (보통 `'NC0002'` 본사 매장 등) |
| `target_date` | **수불 처리 기준 일자** | 재고조정 화면에서 선택/저장된 조정 일자(YYYYMMDD)입니다. (예: `'20260605'`) |
| `target_month` | **수불 처리 기준 월** | 위 기준 일자가 속한 월(YYYYMM)입니다. 월수불(`IMMMIOTB`) 반영 시 사용됩니다. (예: `'202606'`) |
| `adjust_qty` | **재고 조정 수량** | 화면에 입력했던 조정 수량입니다. **(양수 `+` 입력 시 증가, 음수 `-` 입력 시 재고 감소)** |
| `adjust_cost` | **재고 조정 금액** | 조정 수량에 따른 원가 합산액입니다. `(조정수량 * 단가)` 등으로 계산해서 직접 대입합니다. |

> [!WARNING]
> **날짜 정보 일치 중요**
> `target_date`와 `target_month`는 실제로 **현재고 조회 화면(`hq_stock_00001`)에서 조회하는 기준 일자 범위(당월 1일 ~ 현재일)**에 반드시 속해야 합니다. 만약 조회 화면 기준월과 일치하지 않는 과거/미래 날짜를 지정하면, 일수불 변동량 합산 조건(`CREATE_DATE BETWEEN ...`)에 포함되지 않아 조회 화면상에서는 수량 변화가 보이지 않게 됩니다.

### 📌 3.2 5단계 (검증 쿼리 부분) 수정 팁 (코드 내 115라인 부근)
* 테스트하는 월(Month)이 변경될 경우(예: 6월이 아닌 7월 테스트 시):
  * 코드 115라인의 `X.CREATE_MONTH = '202605'`(직전월) 부분을 `'202606'`으로 변경해야 올바르게 기말 재고가 이월 합산됩니다.
  * 코드 119라인의 `CREATE_DATE BETWEEN '20260601' AND ...`의 시작 구간 날짜를 당월 1일인 `'20260701'` 등으로 동시 수정해야 당월 일수불 누적이 정확하게 검증됩니다.
