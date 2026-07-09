# QA Report: Hq_Vendor_00004 검수관리
**작성일**: 2026-06-11  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 매입발주 > 매입관리 > 검수관리 (hq_vendor_00004)  
**테스트 환경**: localhost:8080 (로컬 개발 서버)
**접속ID/PW**: shopadmin / 0000 (NC0007 매장 검수 확인용)

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | [Hq_Vendor_00004_Controller.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/hq/vendor/Hq_Vendor_00004_Controller.java) |
| Service | [Hq_Vendor_00004_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/hq/vendor/Hq_Vendor_00004_Service.java) |
| Mapper (Interface) | [Hq_Vendor_00004_Mapper.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-persistence/src/main/java/com/hyundai/backoffice/webapp/dao/hq/vendor/Hq_Vendor_00004_Mapper.java) |
| SQL XML | [Hq_Vendor_00004_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/vendor/Hq_Vendor_00004_Sql.xml) |
| JSP | [hq_vendor_00004.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/vendor/hq_vendor_00004/hq_vendor_00004.jsp) |
| JS | [hq_vendor_00004.js](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/vendor/hq_vendor_00004/js/hq_vendor_00004.js) |
| 트리거 서비스 | [Tr_OBSLPD_T01_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-api/src/main/java/com/hyundai/api/service/trigger/Tr_OBSLPD_T01_Service.java) |
| 트리거 서비스 | [Tr_OBSLPD_T02_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-api/src/main/java/com/hyundai/api/service/trigger/Tr_OBSLPD_T02_Service.java) |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/vendor/hq_vendor_00004/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
|-----------|------|------|------------|
| `/getCheckHeaderList` | POST | 발주 내역 조회 | SELECT |
| `/getCheckDetailList` | POST | 발주 내역 상세 조회 | SELECT |
| `/saveCheck` | POST | 검수내역 저장 (검수수량 및 금액 계산 저장) | UPDATE |
| `/confirmCheck` | POST | 검수 확정 (PROC_FG: '1' -> '2') | UPDATE |
| `/cancelCheck` | POST | 검수 취소 (PROC_FG: '2' -> '1') | UPDATE |

---

## 3. 서비스 로직 및 트리거 연쇄 분석

### 3.1 서비스 로직 흐름

#### 3.1.1 검수 저장 (`saveCheck`)
- Controller에서 파라미터 수신 및 `Hq_Vendor_00004_Service.saveCheck` 호출.
- 각 detail 행 마다 루프를 돌며 `Hq_Vendor_00004_Mapper.saveCheckDetail` 실행.
- 이후 전표 합계를 계산하기 위해 `Hq_Vendor_00004_Mapper.saveCheckHeader` 호출하여 `OBSLPHTB`의 총 금액 정보 업데이트.

#### 3.1.2 검수 확정 (`confirmCheck`)
- `Hq_Vendor_00004_Mapper.confirmCheck` 및 `confirmCheckDetail`을 수행하여 `OBSLPHTB`, `OBSLPDTB` 테이블의 `PROC_FG` 상태값을 `'2'`로 갱신.
- `CHECK_DATE`를 현재 날짜로 저장하고 `CHECK_CANCEL_DATE`를 `NULL` 처리.

#### 3.1.3 검수 취소 (`cancelCheck`)
- `Hq_Vendor_00004_Mapper.cancelCheck` 및 `cancelCheckDetail`을 수행하여 `OBSLPHTB`, `OBSLPDTB` 테이블의 `PROC_FG` 상태값을 `'1'`로 롤백.
- `CHECK_DATE`를 `NULL` 처리하고 `CHECK_CANCEL_DATE`를 현재 날짜로 기록.

---

## 4. DB 트리거 → 코드베이스 연쇄 분석 (Depth 3)

### 4.1 트리거 동작 구조
`OBSLPDTB` 테이블에는 DML 발생 시 연쇄 처리를 진행하기 위한 `Tr_OBSLPD_T01_Service` 및 `Tr_OBSLPD_T02_Service` 트리거가 매핑되어 있습니다.
- **Tr_OBSLPD_T01_Service**: 입고확정 (`PROC_FG = '4'`) 또는 매입취소 (`PROC_FG = '5'`) 상태 변화 시 가맹점 수불 정보(`MGOODSTB` 등)에 실질적인 현재고 및 입고 수량을 변경하는 연쇄 로직입니다.
- **Tr_OBSLPD_T02_Service**: 마찬가지로 수불 로그 및 가맹점 마스터 변동 내역을 누적 처리하는 트리거 연쇄 체인입니다.

### 4.2 연쇄 분석
- 검수관리 화면의 상태 천이는 `PROC_FG` 기준 `'1'` (발주확정/검수대기)과 `'2'` (검수확정) 사이의 전환에 불과합니다.
- 따라서 트리거 내부의 분기 조건(`PROC_FG IN ('4', '5')`)에 의해 실제 가맹점 수불 및 현재고 변경 연쇄 동작은 실행되지 않고 Bypass 처리됩니다.
- 이는 Legacy Oracle 환경의 Trigger 로직과 완전히 동일하게 구현된 것으로 파악되었습니다.

---

## 5. SQL Mapper 검증 및 변환 사항

### 5.1 타입 캐스팅 예방 패치 (Null-Safety)
화면으로부터 빈 문자열(`""`) 등이 수신될 때 발생할 수 있는 숫자형 데이터 변환 에러(`NumberFormatException`)를 방지하기 위해 `saveCheckDetail` SQL 내 숫자 바인딩 필드에 PostgreSQL 타입 세이프 캐스팅 코드를 추가하였습니다.
- **적용 위치**: `saveCheckDetail` 쿼리
- **변경 예시**:
  ```xml
  CHECK_QTY = COALESCE(NULLIF(#{checkQty, jdbcType=VARCHAR}::text, ''), '0')::numeric
  ```

### 5.2 SQL Mapper 내 Oracle 전용 구문 현황
- **ROWNUM**: `getCheckHeaderList` 쿼리 페이징 처리를 위해 Oracle ROWNUM이 사용 중입니다. (EDB 호환 환경에서 작동)
- **DECODE**: `PROC_FG_NM` 문자열 맵핑을 위해 `DECODE`가 사용 중입니다.
- **(+) 아우터 조인**: `getCheckDetailList` 쿼리 내 `TG.ORD_UNIT = NM.NM_CD(+)`가 사용 중입니다.

---

## 6. 브라우저 화면 테스트 결과

### 6.1 화면 접속 및 제한 조건 적용
- **서버 접속**: `http://localhost:8080/backoffice` 접속 및 `shopadmin` 계정으로 로그인 완료.
- **길이제한 검증**: 
  - 데이터베이스의 컬럼 크기인 `purch_req_no` (varchar 12자리) 및 `slip_no` (varchar 4자리) 스펙에 맞추어 `hq_vendor_00004.jsp` 내 발주번호 및 전표번호 검색 입력 엘리먼트에 `maxlength` 속성을 적용하였습니다.
  - **발주번호**: `maxlength="12"` 적용 ✅
  - **전표번호**: `maxlength="4"` 적용 ✅

### 6.2 E2E 시나리오 테스트 내역 및 스크린샷

1. **검수관리 화면 진입 및 조회**
   - 입고예정일 `2024-02-01` 및 매장 `NC0007` 조건으로 정상 조회.
   ![조회 결과](D:/hmTest/backoffice/QaReport/hq_vendor_00004_search.png)

2. **발주 상세 조회**
   - 조회된 발주 건의 상세 내용을 그리드에 정상 로딩.
   ![상세 로드](D:/hmTest/backoffice/QaReport/hq_vendor_00004_detail.png)

3. **검수 저장**
   - 검수 수량 `3` 입력 후 저장 버튼 클릭 및 Bootbox 확인 모달 승인 처리 완료.
   ![검수 저장 완료](D:/hmTest/backoffice/QaReport/hq_vendor_00004_saved.png)

4. **검수 확정 및 취소(롤백)**
   - 체크박스 선택 후 검수 확정 처리 및 다시 검수 취소 처리를 수행하여 정상적으로 롤백 완료.
   ![검수 확정 완료](D:/hmTest/backoffice/QaReport/hq_vendor_00004_confirmed.png)

---

## 7. 종합 판정

| 구분 | 결과 | 비고 |
|------|------|------|
| 화면 접속 및 로그인 | ✅ PASS | shopadmin 계정 로그인 |
| 발주 내역 조회 | ✅ PASS | 2024-02-01 일자 조회 검증 |
| 검수수량 저장 | ✅ PASS | type-casting Null-Safety 동작 확인 |
| 검수 확정 | ✅ PASS | 상태값 '2' 업데이트 |
| 검수 취소 | ✅ PASS | 상태값 '1' 복원 (롤백 성공) |
| 입력 길이 제한 | ✅ PASS | 발주번호 12자 / 전표번호 4자 제한 적용 |
| **종합 판정** | **✅ PASS** | |
