# Test Case: Hq_Stock_00011 & St_Stock_00010 점간이동 E2E 통합 테스트

**대상 화면**: 
* 본사: 재고관리 > 점간이동 > 본사 점간이동 등록/확정 (`hq_stock_00011`)
* 매장: 재고관리 > 점간이동 > 점간이동 등록/확정 (`st_stock_00010`)
**연계 매장 정보**:
* 보내는 매장: `NC0003` (고양 Shop) - 사용자 계정: `shopbrand`
* 받는 매장: `NC0007` (고양 모터스튜디오) - 사용자 계정: `fnbcafe`
**작성일**: 2026-06-09  
**작성자**: AI QA Agent (Antigravity)  

---

## 1. 테스트 기본 정보
* **테스트 목적**: 본사에서 등록한 매장 간 재고 이동 전표가 보내는 매장의 출고 내역에 연동되고, 받는 매장에서 입고 확인 후 최종 수신 확정(`PROC_FG = '2'`)되어 양쪽 매장의 재고 수불이 연동 처리되는 전체 E2E 비즈니스 흐름을 검증한다.
* **사용 계정 및 비밀번호**: 
  - 본사 관리자: `shopadmin` / `0000`
  - 보내는 매장(`NC0003`): `shopbrand` / `0000`
  - 받는 매장(`NC0007`): `fnbcafe` / `0000`
* **테스트 대상 일자**: 오늘 (실시간 등록/확정 검증)
* **테스트 상품**: `T0000033` (이동 수량: `5`)

---

## 2. 통합 E2E 테스트케이스 시나리오 (UI 및 기능 검증)

| TC ID | 테스트 단계 | 테스트 수행 절차 | 입력 데이터 | 예상 결과 (Expected Result) | 판정 |
|---|---|---|---|---|---|
| **TC_INT_011_01** | **[PHASE 1]** 본사 전표 추가 및 이출 확정 | 1. 본사 관리자 계정(`shopadmin`)으로 로그인<br>2. `Hq_Stock_00011` 진입 후 `[전표추가]` 클릭<br>3. 보내는 매장(`NC0003`), 받는 매장(`NC0007`) 및 상품 정보 입력 후 저장<br>4. 저장된 전표 선택 후 `[확정]` 클릭 (송신 확정) | 보내는매장: `NC0003`<br>받는매장: `NC0007`<br>상품: `T0000033`<br>수량: `5`<br>비고: `Playwright E2E 3-Store Test` | 1. 신규 전표가 채번되어 `MGMVHDTB`에 상태코드 `'0'`(등록)으로 임시 저장된다.<br>2. 송신 확정 시 상태코드가 `'1'`(이출확정)로 변경되고 본사 출고가 승인된다. | **PASS** |
| **TC_INT_011_02** | **[PHASE 2]** 보내는 매장 출고 확인 | 1. 보내는 매장 계정(`shopbrand` - NC0003)으로 로그인<br>2. `St_Stock_00010` (매장 점간이동) 진입<br>3. `전표등록` 탭에서 `[조회]` 클릭하여 이출 확정된 전표 리스트 확인 | N/A (로그인 세션 기반) | 1. 본사에서 `NC0003` 매장 출고로 발행한 점간이동 전표가 정상 조회된다.<br>2. 해당 전표의 상태가 `이출확정`으로 정상 표출된다. | **PASS** |
| **TC_INT_011_03** | **[PHASE 3]** 받는 매장 입고/수신 확정 | 1. 받는 매장 계정(`fnbcafe` - NC0007)으로 로그인<br>2. `St_Stock_00010` (매장 점간이동) 진입<br>3. `입고확정` 탭으로 전환 후 `[조회]` 클릭<br>4. 이출 확정된 전표 체크박스 선택 후 `[확정]` 클릭 | N/A (로그인 세션 기반) | 1. 수신 대기 상태인 전표가 정상 조회된다.<br>2. 입고 확정 처리 모달(`M02`)이 열리고 `[확정]` 승인 시 최종 상태코드가 `'2'`(이입확정)로 변경된다.<br>3. `IMTRLGTB` 및 `TB_IMMMIO_COST` 테이블에 수불 정보가 연동 처리된다. | **PASS** |
| **TC_INT_011_04** | **[PHASE 4]** 본사 최종 연계 상태 검증 | 1. 본사 관리자(`shopadmin`) 재로그인<br>2. `Hq_Stock_00011` 진입 후 `[조회]` 클릭하여 전표 상태 확인 | N/A | 1. 매장 간 이동이 최종 종결되어 해당 전표의 진행 상태가 `이입확정`(수신완료) 상태로 조회된다. | **PASS** |

---

## 3. DB 연쇄 작용 검증 (Depth 3)

| TC ID | 테스트 대분류 | 테스트 시나리오 / 수행 절차 | 입력 데이터 | 예상 결과 (Expected Result) | 판정 |
|---|---|---|---|---|---|
| **TC_DB_011_05** | DB 트리거/프로시저 연쇄 작용 | 1. 매장 최종 확정(`PROC_FG = '2'`) 수행 완료 후 DB 수불 대기 및 마감 원가 테이블 조회 | `MGMVHDTB.PROC_FG = '2'` | 1. `MGMVHD_T01` 트리거에 의해 `IMTRLGTB` 테이블에 **보내는 매장(`NC0003`, PROC_FG='F')**과 **받는 매장(`NC0007`, PROC_FG='T')**의 수불 기록이 각각 1건씩 복식 부기로 생성된다.<br>2. `SUB_IMTRLG_I` 자바 트리거와 프로시저가 연쇄 호출되어 `TB_IMMMIO_COST` 및 `IMMMIOTB` 테이블의 당월 수불 수량 및 총평균단가가 오차 없이 성공적으로 갱신된다. | **PASS** |

---

## 4. E2E 통합 테스트 증적 자료 (Screenshots)

자동화 테스트 스크립트([test_hq_stock_11.py](file:///d:/hmTest/backoffice/QaReport/test_hq_stock_11.py)) 실행 결과 생성된 각 단계별 증적 자료입니다.

* **[1] 본사 전표 임시 등록 완료 (hq_stock_00011_saved.png)**
  ![1. 본사 임시 등록](file:///D:/hmTest/backoffice/QaReport/hq_stock_00011_saved.png)
  
* **[2] 본사 송신(이출) 확정 (hq_stock_00011_hq_dispatched.png)**
  ![2. 본사 송신 확정](file:///D:/hmTest/backoffice/QaReport/hq_stock_00011_hq_dispatched.png)
  
* **[3] 보내는 매장(NC0002) 출고 내역 조회 확인 (st_stock_00010_sender_verified.png)**
  ![3. 출고 매장 검증](file:///D:/hmTest/backoffice/QaReport/st_stock_00010_sender_verified.png)
  
* **[4] 받는 매장(NC0007) 입고/수신 확정 (st_stock_00010_recv_store_confirmed.png)**
  ![4. 입고 매장 확정](file:///D:/hmTest/backoffice/QaReport/st_stock_00010_recv_store_confirmed.png)
  
* **[5] 본사 최종 연계 상태 확인 - 이입확정 (hq_stock_00011_final_received.png)**
  ![5. 최종 연계 완료](file:///D:/hmTest/backoffice/QaReport/hq_stock_00011_final_received.png)
