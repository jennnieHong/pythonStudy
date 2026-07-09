# QA Report: Hq_Stock_00013 선입선출 월말마감처리

**작성일**: 2026-07-02  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 본사관리 > 재고관리 > 월말마감처리 (`hq_stock_00013`)  
**테스트 환경**: localhost:8080 (로컬 개발 WAS)  
**접속ID/PW**: `shopadmin` / `0000` (FST_LOGIN_PW_CHANGE='Y', ACCT_ENABLE='Y')  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
| :--- | :--- |
| Controller | `backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/hq/stock/Hq_Stock_00013_Controller.java` |
| Service | `backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/hq/stock/Hq_Stock_00013_Service.java` |
| Mapper (Interface) | `backoffice/hyundai-backoffice-layer-persistence/src/main/java/com/hyundai/backoffice/webapp/dao/hq/stock/Hq_Stock_00013_Mapper.java` |
| SQL XML | `backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/stock/Hq_Stock_00013_Sql.xml` |
| DTO | `backoffice/hyundai-backoffice-layer-domain/src/main/java/com/hyundai/backoffice/webapp/dto/hq/stock/Hq_Stock_00013_MonthCloseListDto.java` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/stock/hq_stock_00013/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
| :--- | :--- | :--- | :--- |
| `/getMonthCloseList` | POST | 월마감 내역 목록 조회 | SELECT |
| `/getInstockCloseList` | POST | 선입고 마감 내역 목록 조회 | SELECT |
| `/excuteMonthClose` | POST | 월마감 실행 | UPDATE |
| `/reDoMonthClose` | POST | 재마감 실행 | UPDATE |
| `/inStockMonthClose` | POST | 선입고 월마감 실행 | UPDATE |

---

## 3. 서비스 로직 및 DB 영향도 분석 (CUD / 트리거 연쇄 반응)

### 3.1 CUD 발생 여부 검증
*   **분석 결과**: 본 화면은 특정 월의 가맹점 전체 수불(입출고/매출/조정 등) 및 단가 정보를 최종 확정하는 **마감 처리 전용 화면**입니다.
*   **영향도 테이블**:
    1.  `hmsfns.STCKIOTB` (마감 이력 및 진행 구분 적재)
    2.  `hmsfns.STCKERTB` (마감 중 에러 발생 시 로그 저장)
    3.  `hmsfns.IMMMIOTB` (선입선출법 계산 결과에 따른 당월 재고 요약 및 금액 수정)

### 3.2 DB 트리거 및 프로시저 영향성
*   **SP 호출 연쇄**:
    *   마감 실행 시 자바 프로시저 서비스(`Sp_SUB_STOCK_FIFO_MAIN_P_Service`)를 호출합니다.
    *   내부적으로 `PROC_P`, `AFTER_PROC_P`, `ERR_P` 서비스가 순차 기동하며 `STCKIOTB` 테이블에 데이터를 인서트하고, 실패 시 `ERR_P_Service`를 통해 `STCKERTB`에 예외 로그를 롤백과 무관하게 영구 적재합니다.

---

## 4. 데이터베이스 및 쿼리 흐름

### 4.1 선입선출 마감 연산 흐름
```
  [STCKLGTB] (일별 수불 원장) ──┐
                                │
                                ├─► [mergeImmmiotb] ──► [IMMMIOTB] (당월 기초수량 및 임시합계)
  [IMMMIOTB] (이전월 이월 재고) ──┘
                                │
                                ├─► [Sp_SUB_STOCK_FIFO_PROC_P] (선입선출 단가 연산 및 매출원가 확정)
                                │
                                ├─► [Sp_SUB_STOCK_FIFO_AFTER_PROC_P] (이후 모든 미래월 기초이월 동시 전파)
                                │
                                └──► [STCKIOTB] (최종 마감 완료 PROC_YN = 'Y' 인서트)
```

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 및 E2E 테스트 현황

| 항목 | 결과 |
| :--- | :--- |
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 권한 | 성공 (`shopadmin` / `0000`, 체인 `C001`) ✅ |
| 화면 경로 | 본사관리 > 재고관리 > 월말마감처리 ✅ |
| 화면 로딩 | 정상 로딩 및 조건부 마감/재마감 제어 완료 ✅ |

### 5.2 E2E 시나리오 테스트 내역 및 결과
*   **시나리오 1**: 미마감월(`2026-06`)에 대해 **[마감 실행]**을 수행하여 계산된 선입선출 결과를 수불집계 테이블(`IMMMIOTB`)에 정상 확정 처리 완료.
*   **시나리오 2**: 이미 마감 완료된 연월에 대해 중복 마감 시도를 수행하여 **[중복 차단 알림 모달]**이 출력되고, DB 에러 이력(`STCKERTB`)에 `-20506 MONTHS STOCK EXISTS!!`가 정상 보존되는지 확인.
*   **시나리오 3**: **[재마감]**을 실행하여 기존의 마감 행을 캔슬(`CANCEL_YN = 'Y'`) 처리하고 원복 후 최신 실적을 반영하여 새로운 마감 데이터를 정상 재생성함을 확인.

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI | 판정 |
| :--- | :--- | :---: | :---: | :---: |
| 마감내역 조회 | `/getMonthCloseList` | ✅ 구현 완료 | ✅ 데이터 표시 | **PASS** |
| 선입고내역 조회 | `/getInstockCloseList` | ✅ 구현 완료 | ✅ 데이터 표시 | **PASS** |
| 월마감 실행 | `/excuteMonthClose` | ✅ 구현 완료 | ✅ 데이터 반영 | **PASS** |
| 재마감 실행 | `/reDoMonthClose` | ✅ 구현 완료 | ✅ 데이터 반영 | **PASS** |
| 선입고마감 실행 | `/inStockMonthClose` | ✅ 구현 완료 | ✅ 데이터 반영 | **PASS** |

---

## 6. 검증 항목 체크리스트

### 6.1 코드베이스 변환 정합성

| 검증 항목 | 상태 | 비고 |
| :--- | :--- | :--- |
| `@Service`, `@Transactional` 어노테이션 정의 | ✅ 정상 | 마감 실패 시 안전한 롤백 보장 |
| @org.springframework.beans.factory.annotation.Qualifier("dataSource-POS") 적용 | ✅ 정상 | 마감 관련 DB 커넥션 분리 및 지정 |
| `@ServiceLog` 어노테이션 누락 여부 | ✅ 정상 | 월마감/재마감 로그 지정 완료 |

---

## 7. 종합 판정

| 구분 | 결과 |
| :--- | :--- |
| 화면 로딩 | ✅ PASS |
| 데이터 마감 및 계산 기능 | ✅ PASS |
| 중복 마감 예외 처리 | ✅ PASS |
| 재마감 복구 기능 | ✅ PASS |
| **종합 판정** | **✅ PASS** |

---

## 8. 첨부 (E2E 테스트 스크린샷)

*   **최초 화면 접속 (`hq_stock_00013_initial.png`)**:
    ![최초접속](/C:/Users/uoshj/.gemini/antigravity-ide/brain/5b781763-17f9-44c1-92ff-e431cff8ecde/hq_stock_00013_initial.png)
*   **마감 실행 완료 (`hq_stock_00013_closed.png`)**:
    ![마감완료](/C:/Users/uoshj/.gemini/antigravity-ide/brain/5b781763-17f9-44c1-92ff-e431cff8ecde/hq_stock_00013_closed.png)
*   **중복 마감 오류 검출 (`hq_stock_00013_dup_error.png`)**:
    ![중복오류](/C:/Users/uoshj/.gemini/antigravity-ide/brain/5b781763-17f9-44c1-92ff-e431cff8ecde/hq_stock_00013_dup_error.png)
*   **재마감(Redo) 처리 완료 (`hq_stock_00013_redo.png`)**:
    ![재마감](/C:/Users/uoshj/.gemini/antigravity-ide/brain/5b781763-17f9-44c1-92ff-e431cff8ecde/hq_stock_00013_redo.png)

---
*본 리포트는 코드베이스 정적 분석 + Playwright E2E 브라우저 검증을 기반으로 작성되었습니다.*
