# 월 마감내역 조회(Hq_Stock_00014)를 위한 월마감 연동 워크플로우 가이드

본 가이드는 본사 재고관리의 **월 마감내역 조회 ([hq_stock_00014](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/stock/hq_stock_00014/hq_stock_00014.jsp))** 화면에서 재고 수불 데이터를 조회하기 위해, 선행 작업인 **월마감 관리 ([hq_stock_00013](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/stock/hq_stock_00013/hq_stock_00013.jsp))** 처리 시 필요한 데이터베이스 상태 및 처리 플래그 설정 방법을 안내합니다.

---

## 1. 개요 및 데이터 적재 원리

* **조회 대상 원장**: `hq_stock_00014` 화면은 재고 로그 테이블인 `hmsfns.STCKLGTB` 및 `hmsfns.TGOODSTB`, `hmsfns.MMEMBSTB`를 조인하여 조회합니다.
* **배치 적재 방식**: `STCKLGTB` 테이블은 매출/매입입고 발생 시 실시간으로 적재되는 것이 아니라, **[월마감 관리 (hq_stock_00013)](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/hq/stock/Hq_Stock_00013_Controller.java) 화면에서 월마감 배치를 수행한 시점**에 일괄 계산 및 적재됩니다.
* **연동 서비스**: 월마감 진행 시 내부적으로 선입선출(FIFO) 평가 및 마감 연산을 처리하는 [Sp_SUB_STOCK_FIFO_MAIN_P_Service](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-api/src/main/java/com/hyundai/api/service/procedure/Sp_SUB_STOCK_FIFO_MAIN_P_Service.java)가 기동됩니다.

---

## 2. 월마감 성공을 위한 핵심 플래그 및 비즈니스 룰

월마감 배치 서비스가 오류 없이 완료되어 `STCKLGTB`에 정상적으로 수불 데이터를 밀어 넣기 위해서는 다음 조건들이 충족되어야 합니다.

### ① 제휴사 업태 플래그 (`hmsfns.TCHAINTB.AFFILIATE_COMPANY`)
* **설정 방식**: 대상 체인의 `AFFILIATE_COMPANY` 플래그 값이 **브랜드샵(즉, `'0'`이 아닌 값, 예: `'1'`)**으로 설정되어 있어야 합니다.
* **상세**:
  * `'0'`(F&B)인 경우: 시스템 내에서 총평균 마감(`excuteTotAvg`) 로직이 구동되는데, 해당 자바 소스코드 내에 `throw new RuntimeException("SUB_TOT_AVG_P Error")` 코드가 하드코딩되어 강제로 예외가 발생합니다.
  * `'1'`(브랜드샵)인 경우: 선입선출(FIFO) 마감(`excuteMonthClose`) 로직이 구동되어 정상적으로 배치가 기동됩니다.

### ② 마감 이력 상태 플래그 (`hmsfns.STCKIOTB.PROC_YN`)
* **설정 방식**: 마감 처리 시 해당 마감월(`closeMonth`)에 대해 최종적으로 **`PROC_YN` 값이 `'Y'`**로 완료 상태가 되어야 합니다.
* **상세**:
  * 월마감 기동 시 `STCKIOTB` 테이블에 대상 월 레코드가 최초 생성(Insert)됩니다.
  * FIFO 연산 및 수불 내역 적재가 모두 정상 완료되면, `mapper.updateStckiotbSuccess`를 통해 `PROC_YN = 'Y'`로 최종 업데이트되며 마감이 확정됩니다.
  * 만약 이 단계에서 오류가 발생하면 트랜잭션이 전체 롤백되고 상태값은 `'Y'`가 되지 못합니다.

### ③ 마감 대상 월 기준 (`closeMonth`)
* **설정 방식**: 마감 처리하려는 대상 월은 **최소 `202601` (2026년 01월) 이후**여야 합니다.
* **상세**:
  * 소스코드의 안전 장치로 인해 `cEndMonth <= '202512'` 조건에 걸릴 경우 `"CANNOT RUN BEFORE 202512 !!"` 예외를 던지며 강제 종료됩니다.

### ④ 재마감/마감 취소 플래그 (`cCancelYn`)
* **설정 방식**: 기존에 이미 마감이 완료된 월에 대해 재테스트를 위해 다시 마감을 돌릴 경우, **`cCancelYn`을 `'Y'`**로 전달해야 합니다.
* **상세**:
  * `cCancelYn = 'Y'`가 전달되면, 기존에 `STCKLGTB` 및 `STCKHITB`에 쌓여 있던 데이터가 먼저 삭제(Delete)되고 기존 마감 정보가 취소 상태로 변경된 후 재생성 프로세스로 진행됩니다.

---

## 3. 전체 수불유형(`PROC_FG`) 데이터 적재 및 변경 프로세스

월마감 배치 구동 시 원장 테이블 `STCKLGTB`에 적재되는 총 11가지의 수불유형(`PROC_FG`)에 대한 화면 조작 경로, 데이터 생성 방법, 그리고 상태 변경 흐름은 아래와 같습니다.

### 11가지 수불유형 요약 및 매핑 규칙
| 코드 | 수불유형 명칭 (화면 표시) | 생성 액션 / 웹 화면 경로 | 데이터 생성 주입 쿼리 / 방식 |
| :---: | :--- | :--- | :--- |
| **S** | 매출 | POS 상품 결제 완료 | POS 전송을 통한 `IMTRLGTB` 자동 인서트 (테스트 시 SQL 수동 주입) |
| **C** | 매출취소 | POS 결제 취소 / 반품 완료 | POS 전송을 통한 `IMTRLGTB` 자동 인서트 (테스트 시 SQL 수동 주입) |
| **P** | 매입입고 | `매장업무 > 매입관리 > 무발주 입고` [st_vendor_00006](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/vendor/st_vendor_00006/st_vendor_00006.jsp) | 전표 신규 등록 후 **[확정]** 처리 |
| **R** | 매입반품 | `매장업무 > 매입관리 > 반품등록/확정` | 반품 전표 등록 후 **[확정]** 처리 |
| **D** | 폐기 | `매장업무 > 재고 > 폐기등록` [st_stock_00003](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/stock/st_stock_00003/st_stock_00003.jsp) | 폐기 전표 등록 후 **[확정]** 처리 |
| **A** | 조정 | `매장업무 > 재고 > 조정등록` [st_stock_00001](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/stock/st_stock_00001/st_stock_00001.jsp) | 조정 내역 입력 후 **[확정]** 처리 |
| **T** | 점간이동 입고 | `매장업무 > 재고 > 점간이동 > 이동입고등록/확정` | 이동 전표 접수 후 **[확정]** 처리 |
| **F** | 점간이동 출고 | `매장업무 > 재고 > 점간이동 > 이동출고등록/확정` | 이동 전표 신규 등록 후 **[확정]** 처리 |
| **M** | 부대비용 적용 | 본사/매장 매입 정산 관리 | 월마감 배치(`Sp_SUB_STOCK_FIFO_MAIN_P_Service`) 연산 중 자동 생성 |
| **V** | 부대비용 적용 증가 | 본사/매장 매입 정산 관리 | 월마감 배치(`Sp_SUB_STOCK_FIFO_MAIN_P_Service`) 연산 중 자동 생성 |
| **U** | 부대비용 적용 차감 | 본사/매장 매입 정산 관리 | 월마감 배치(`Sp_SUB_STOCK_FIFO_MAIN_P_Service`) 연산 중 자동 생성 |

---

### 유형별 데이터 주입 가이드

#### ① 매출 (`S`) 및 매출취소 (`C`)
* **웹 화면 조작**: 백오피스 웹 페이지 내에는 매출을 직접 입력/확정하는 기능이 없습니다. POS 단말기 결제 송신을 거쳐야 합니다.
* **수동 주입 방법 (SQL)**:
  ```sql
  -- 매출(S) 수불 로그 생성
  INSERT INTO hmsfns.IMTRLGTB (TRLG_DTIME, MS_NO, PROC_FG, TRLG_SEQ, PROC_DATE, CHAIN_MS_NO, GOODS_CD, TRLG_QTY, TRLG_COST, PROC_YN)
  VALUES (TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'NC0007', 'S', 1, '20260621', 'NC0007', 'T0000291', 2, 25000, 'N');
  
  -- 매출취소(C) 수불 로그 생성 (수량 음수 처리)
  INSERT INTO hmsfns.IMTRLGTB (TRLG_DTIME, MS_NO, PROC_FG, TRLG_SEQ, PROC_DATE, CHAIN_MS_NO, GOODS_CD, TRLG_QTY, TRLG_COST, PROC_YN)
  VALUES (TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'NC0007', 'C', 1, '20260621', 'NC0007', 'T0000291', -2, 25000, 'N');
  ```

#### ② 매입입고 (`P`) 및 매입반품 (`R`)
* **웹 화면 조작**:
  * **매입입고**: `매장업무 > 매입관리 > 무발주 입고` ([st_vendor_00006](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/vendor/st_vendor_00006/st_vendor_00006.jsp)) 화면에서 신규 등록 후 **[확정]** 처리합니다.
  * **매입반품**: `매장업무 > 매입관리 > 반품등록/확정` 화면에서 반품 목록 추가 및 금액 조정 후 **[확정]** 처리합니다.
* **동작 원리**: 확정 처리 시, 백엔드 공통 API인 `Sp_SUB_IMTRLG_I_Service`에 의해 `IMTRLGTB` 테이블에 `PROC_FG = 'P'` 또는 `'R'` 형태로 즉시 적재됩니다.

#### ③ 폐기 (`D`) 및 조정 (`A`)
* **웹 화면 조작**:
  * **폐기**: `매장업무 > 재고 > 폐기등록` ([st_stock_00003](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/stock/st_stock_00003/st_stock_00003.jsp)) 화면에서 상품 추가 및 사유 지정 후 **[확정]** 처리합니다.
  * **조정**: `매장업무 > 재고 > 조정등록` ([st_stock_00001](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/stock/st_stock_00001/st_stock_00001.jsp)) 화면에서 조정 수량을 실사 대조 입력한 뒤 **[확정]** 처리합니다.
* **동작 원리**: 폐기 및 조정을 확정하면 각각 `Tr_IMDUSE_T01_Service`와 `Sp_SUB_IMTRLG_I_Service`가 호출되어 `IMTRLGTB` 테이블에 `PROC_FG = 'D'` 또는 `'A'` 로 실시간 수불 로그가 쌓이게 됩니다.

#### ④ 점간이동 입고 (`T`) 및 점간이동 출고 (`F`)
* **웹 화면 조작**:
  * **이동출고(F)**: 보내는 매장에서 `점간이동 > 이동출고등록/확정` 화면을 통해 타 매장으로 재고 출고 전표를 작성하고 **[확정]** 처리합니다.
  * **이동입고(T)**: 받는 매장에서 `점간이동 > 이동입고등록/확정` 화면을 조회하여 송신된 전표를 대조하고 **[확정]** 처리합니다.
* **동작 원리**: 전표 확정 시 각각 `IMTRLGTB`에 `PROC_FG = 'F'` 및 `PROC_FG = 'T'` 로 이력이 적재됩니다.

#### ⑤ 부대비용 관련 유형 (`M`, `V`, `U`)
* **동작 원리**: 해당 유형들은 사용자가 화면 상에서 별개 전표로 저장/확정하는 대상이 아닙니다. 
* **자동 생성**: 매입 건에 배부된 운송비/수수료 등의 부대비용 데이터를 기초로 하여, **월마감 배치 스크립트(`Sp_SUB_STOCK_FIFO_MAIN_P_Service`)가 구동되는 시점**에 선입선출 차액을 계산하여 `STCKLGTB` 테이블에 직업 주입(Insert)됩니다.

---

### 수불 구분 플래그(`PROC_FG`)의 생명주기 및 상태 변경 과정

```
[각 영업/물류 화면]           [실시간 로그 생성]              [월마감 배치 기동]            [최종 조회 렌더링]
 전표 등록 및 확정  ======>  hmsfns.IMTRLGTB  ======>  hmsfns.STCKLGTB  ======>  hq_stock_00014
 (S, C, P, R, D, A, etc)   (PROC_YN = 'N')           (PROC_YN = 'Y')          (DECODE 한글 치환)
```

1. **실시간 트랜잭션 수집 (`IMTRLGTB` 적재)**:
   * 각 업무 화면(입고, 폐기 등)에서 확정이 완료되면 즉시 공통 적재 서비스가 실행됩니다.
   * `hmsfns.IMTRLGTB` (수불대장 대기 로그)에 영문 상태값(`PROC_FG`)이 기록되며, 이관 처리 상태값인 `PROC_YN`은 **`'N'` (미처리)**으로 설정됩니다.
2. **배치 연산 및 원장 이관 (`STCKLGTB` 갱신)**:
   * 본사 **월마감 관리 (hq_stock_00013)** 화면에서 마감을 돌리면 배치 서비스가 수행됩니다.
   * 배치 도중 `PROC_YN = 'N'` 상태인 `IMTRLGTB` 데이터를 바탕으로 선입선출(FIFO) 매칭 및 금액 재연산이 돌며, 연산된 결과물이 **`hmsfns.STCKLGTB` (재고로그 원장)**에 인서트됩니다.
   * 이때 기존 영문 플래그(`PROC_FG`) 값이 그대로 원장 테이블로 복사 및 유지됩니다.
   * 작업이 끝나면 `IMTRLGTB` 데이터의 `PROC_YN`은 `'Y'`로 업데이트됩니다.
3. **화면 표시 치환**:
   * [월 마감내역 조회 (hq_stock_00014)] 화면에서 쿼리를 던질 때, `MyBatis` 내의 `DECODE` 처리를 통해 영문 코드들을 사용자용 한글(예: `'매출'`, `'매입입고'`)로 치환하여 그리드에 최종 렌더링하게 됩니다.
