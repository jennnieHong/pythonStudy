# Test Case: St_Stock_00010 매장 점간이동 등록/확정

**대상 화면**: 재고관리 > 점간이동 > 점간이동 등록/확정 (`st_stock_00010`)  
**연계 화면**: [조정등록] (`st_stock_00001`), [현재고조회] (`st_stock_00007`)  
**작성일**: 2026-06-08  
**작성자**: AI QA Agent (Antigravity)  

---

## 1. 테스트 기본 정보
* **테스트 계정**: `fnbcafe` / `0000` (매장 코드: `NC0007`, HMS SHOP CAFE, 체인 코드: `C001`)
* **사전 데이터 입력 원천**: 매장 `NC0006`과 `NC0007` 간의 점간이동 전표 및 관련 마스터 테이블 정보 (`MGMVHDTB`, `MGMVDTTB`, `IMCRIOTB`)
* **테스트 대상 일자**: 2024-01-01 ~ 오늘 (2026-06-08)

---

## 2. 테스트케이스 정의서 (UI 및 기능 검증)

| TC ID | 테스트 대분류 | 테스트 시나리오 / 수행 절차 | 입력 데이터 | 예상 결과 (Expected Result) | 판정 |
|---|---|---|---|---|---|
| **TC_ST_010_01** | 화면 진입 | 1. `fnbcafe` 계정 로그인<br>2. `재고관리 > 점간이동 > 점간이동 등록/확정` 메뉴 진입 | N/A | 화면이 에러 없이 로딩되며, 기본 조회 기간(시작일: 당월 1일, 종료일: 오늘)이 자동으로 세팅된다. | **PASS** |
| **TC_ST_010_02** | 보내는매장 검색 | 1. 조회 기간 시작일을 `2024-01-01`로 수정<br>2. `[조회]` 버튼 클릭 | 기간: `2024-01-01` ~ `오늘` | 1. HTTP 200 응답 수집 완료.<br>2. 점간이동 등록 목록 그리드(`#st_stock_00010_t01`)에 해당 기간의 점간이동 전표 내역이 정상 리스팅된다. | **PASS** |
| **TC_ST_010_03** | 전표 추가 및 저장 | 1. `[전표추가]` 버튼 클릭<br>2. 보내는 매장 및 받는 매장 선택<br>3. `[행추가]` 후 상품 선택 후 이동 수량 입력<br>4. `[저장]` 버튼 클릭 | 보내는매장: `NC0006`<br>받는매장: `NC0007`<br>상품: `T0000033`<br>수량: `3.0` | 1. 새로운 점간이동 전표번호가 채번되어 `MGMVHDTB`와 `MGMVDTTB`에 '등록(0)' 상태로 저장된다.<br>2. 성공 안내 메시지(Snackbar)가 표출된다. | **PASS** |
| **TC_ST_010_04** | 보내는 매장 확정 | 1. 전표 등록 목록 그리드에서 전표 행 선택<br>2. `[확정]` 버튼 클릭<br>3. 확정 모달 팝업 내부에서 내용 확인 후 `[확정]` 클릭 | N/A | 1. 전표 상태가 '이출확정(1)'으로 갱신된다.<br>2. 확정일 및 확정자가 기록된다. | **PASS** |
| **TC_ST_010_05** | 입고확정 내역 연동 | 1. '입고확정' 탭 클릭<br>2. 등록일자 검색 조건 설정 후 `[조회]` 클릭<br>3. 목록에서 특정 전표 행 선택 후 **전표번호 링크** 클릭 | N/A | 1. 하단 상세 내역 그리드(`#st_stock_00010_t03`)에 해당 전표의 상품 목록과 이동 수량 데이터가 정상 바인딩된다. | **PASS** |
| **TC_ST_010_06** | 입고 수량 수정 | 1. 입고확정 상세 그리드에서 입고수량(Box/EA) 변경 입력<br>2. `[수정]` 버튼 클릭 및 승인 | 수정 수량: `3.0` | 1. 입고수량 및 원가 정보가 정상적으로 변경 반영된다.<br>2. 성공 메시지가 표출된다. | **PASS** |
| **TC_ST_010_07** | 받는 매장 확정 | 1. 입고확정 전표 목록에서 전표 행 선택<br>2. `[확정]` 버튼 클릭 후 모달 내부에서 `[확정]` 클릭 | N/A | 1. 전표 상태가 '이입확정(2)'으로 최종 변경된다.<br>2. 입고확정 성공 메시지가 화면 하단에 표출된다. | **PASS** |

---

## 3. 테스트케이스 정의서 (DB 호환성 및 연쇄 작용 검증)

| TC ID | 테스트 대분류 | 테스트 시나리오 / 수행 절차 | 입력 데이터 | 예상 결과 (Expected Result) | 판정 |
|---|---|---|---|---|---|
| **TC_ST_010_08** | DB 트리거/프로시저 연쇄 작용 (Depth 3) | 1. 받는 매장의 최종 입고확정 수행<br>2. DB `IMTRLGTB`, `TB_IMMMIO_COST`, `IMMMIOTB` 데이터 변경 관찰 | `MGMVHDTB.PROC_FG = '2'` | 1. `MGMVHD_T01` 자바 트리거 실행 $\rightarrow$ `IMTRLGTB`에 이출('F'), 이입('T') 행 삽입.<br>2. `SUB_IMTRLG_I` 자바 트리거 실행 $\rightarrow$ `Sp_SUB_TOT_AVG_SINGLE_P_Service` 호출.<br>3. `TB_IMMMIO_COST` 및 `IMMMIOTB` 테이블의 당월 수불 수량/금액 및 총평균단가 정보가 에러 없이 성공적으로 갱신된다. | **PASS** |
| **TC_ST_010_09** | 비고(Remark) 입력 길이 제한 | 1. 전표 추가 및 확정 모달 내의 비고 필드에 50자 이상의 문자 입력 시도 | 50자 초과 문자열 | `remark_M01` 및 `remark_M02` input 태그에 `maxlength="50"`이 적용되어 50자를 넘는 문자 입력 자체가 차단된다 (DB 컬럼 자릿수 오류 사전 방지). | **PASS** |

---

## 4. 특이사항 및 검증 결과 코멘트

### 4.1 SQL Mapper 파라미터 바인딩 오류 수정 내역
* **문제 상황**: MyBatis Mapper `Sp_SUB_TOT_AVG_SINGLE_P_Mapper.java` 파일에 `@Param("item")` 어노테이션이 누락되어 차월 이월 처리를 위한 `mergeNextMonthStartCostTotavg` 호출 시 `create_month` 등이 `null`로 입력되어 데이터베이스 `immmiotb` 테이블의 제약 조건 오류가 발생했던 것을 해결했습니다.
* **해결 내용**: 
  - `backoffice` 및 `telex` 모듈에 정의된 [Sp_SUB_TOT_AVG_SINGLE_P_Mapper.java (backoffice)](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-api/src/main/java/com/hyundai/api/mapper/procedure/Sp_SUB_TOT_AVG_SINGLE_P_Mapper.java) 및 [Sp_SUB_TOT_AVG_SINGLE_P_Mapper.java (telex)](file:///d:/workspace/hmotors/workspace_hms20260326/telex/hyundai-api/src/main/java/com/hyundai/api/mapper/procedure/Sp_SUB_TOT_AVG_SINGLE_P_Mapper.java) 파일의 메소드 시그니처에 `@Param("item")` 어노테이션을 부착함으로써 파라미터 바인딩 버그를 패치하고 트랜잭션이 성공적으로 수행되도록 조치 완료하였습니다.

### 4.2 E2E 테스트 스크린샷 증적 자료
* **[1] 보내는 매장 전표등록 화면 (st_stock_00010_send.png)**
  ![전표등록 화면](file:///D:/hmTest/backoffice/QaReport/st_stock_00010_send.png)
* **[2] 받는 매장 입고확정 화면 (st_stock_00010_recv.png)**
  ![입고확정 화면](file:///D:/hmTest/backoffice/QaReport/st_stock_00010_recv.png)
* **[3] 입고확정 상세내역 그리드 바인딩 화면 (st_stock_00010_recv_detail.png)**
  ![상세내역 화면](file:///D:/hmTest/backoffice/QaReport/st_stock_00010_recv_detail.png)
* **[4] 최종 입고확정 모달 팝업 화면 (st_stock_00010_recv_modal.png)**
  ![확정 모달 화면](file:///D:/hmTest/backoffice/QaReport/st_stock_00010_recv_modal.png)
* **[5] 최종 입고확정 완료 처리 성공 화면 (st_stock_00010_recv_confirmed.png)**
  ![확정 완료 화면](file:///D:/hmTest/backoffice/QaReport/st_stock_00010_recv_confirmed.png)
