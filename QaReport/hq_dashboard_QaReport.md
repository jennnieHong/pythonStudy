# QA Report: Hq_Dashboard 대시보드 (본사)
**작성일**: 2026-07-06  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: [HQ] 대시보드 (hq_dashboard)  
**테스트 환경**: localhost:8080 (로컬 개발 서버)  
**접속 ID/PW**: `shopadmin` / `0000` (체인번호: `C001`, 매장번호: `NC0002`)  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Layout JSP | `hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/main.jsp` |
| View JSP | `hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/dashboard/dashboard.jsp` |
| Page Controller | `hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/WebPageTransition.java` |
| Data Controller | `hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/hq/dashboard/Hq_Dashboard_Controller.java` |
| Service | `hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/hq/dashboard/Hq_Dashboard_Service.java` |
| SQL XML | `hyundai-backoffice-webapp/src/main/resources/sqlmapper/dashboard/Hq_Dashboard_Sql.xml` |

---

## 2. 엔드포인트 및 흐름 분석

### 2.1 진입 URL 및 데이터 로드
* **호출 경로**: `GET /backoffice/view/main`
* **동작 방식**: 
  1. 로그인 성공 후 최초 진입 시 `WebPageTransition.java` 컨트롤러로 접근.
  2. 본사(`hq`) 권한 세션에 맞춰 대시보드 관련 기초 데이터(`dailySalesData`, `goodsRankData`, `noticeData`)를 사전에 조회하여 JSP 모델에 담아 전송.
  3. `main.jsp` 내에서 `${systemDir}/${categoryDir}/${contentPage}/${contentPage}.jsp` 표현식에 의해 `hq/dashboard/dashboard.jsp`가 동적 인클루드됨.

---

## 3. 서비스 로직 및 DB 트리거 영향도

* **CUD 여부**: **단순 SELECT** (CUD 트랜잭션 없음)
* **DB 트리거 영향도**: 트랜잭션이 발생하지 않는 조회 전용 페이지로, 데이터베이스 트리거 연쇄 반응 리스크가 존재하지 않음.

---

## 4. 브라우저 화면 E2E GUI 테스트 결과

| NO | 기능 테스트 유형 | E2E GUI 시나리오 세부 내용 | 실행 결과 (PASS/WARNING/FAIL) |
|----|-----------------|-----------------------------|--------------------------|
| 1 | **로그인 리다이렉션** | `shopadmin` 로그인 성공 후 자동으로 대시보드로 리다이렉트 완료 | **정상 (PASS)** |
| 2 | **레이아웃 결합** | LNB(좌측메뉴), GNB(상단헤더) 및 대시보드 본문이 깨짐 없이 렌더링됨 | **정상 (PASS)** |
| 3 | **데이터 바인딩** | 금일 매출 집계 데이터, 상위 판매 상품 목록, 공지사항 목록이 정상 노출됨 | **정상 (PASS)** |

---

## 5. SQL Mapper 및 Postgres 형변환/나눗셈 결함 분석
* **분석 결과**: 본사 대시보드 SQL(`Hq_Dashboard_Sql.xml`)에 작성된 조회 쿼리들은 집계 및 순위 조회로 구성되어 있으며, 나눗셈 분모 0 리스크나 PostgreSQL 형변환 관련 오류를 유발할 만한 취약점은 발견되지 않았습니다.

---

## 6. 검증 항목 체크리스트

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 정의 | ✅ 정상 | 롤백 정책 적용 확인 |
| `@ServiceLog` 적용 확인 | ✅ 정상 | type = ServiceType.SELECT 정의 완료 |
| PostgreSQL 형변환 정합성 | ✅ 정상 | 특이사항 없음 |

---

## 7. 종합 판정

| 구분 | 결과 |
|------|------|
| **첫 진입 로드** | ✅ **PASS** |
| **대시보드 데이터 조회** | ✅ **PASS** |
| **종합 판정** | ✅ **PASS** |

---

## 8. 데이터 수치 정합성 검증 방법 (Database Cross-Check)

대시보드 화면에 노출되는 주요 지표와 그래프 수치의 정합성을 데이터베이스 조회 결과를 통해 크로스 체크(교차 검증)하는 SQL 쿼리 가이드입니다.

### 8.1 금일 매출 요약 카드 (Daily Sales Summary)
* **대조 화면 지표**: 당일 매출액, 주문 건수, 취소 금액
* **DB 검증 SQL**:
  ```sql
  SELECT NVL(SUM(B.SALE_AMT), 0)                     AS SALE_AMT   -- 금일 매출액
       , NVL(SUM(B.BILL_CNT + B.CANCEL_CNT), 0)        AS BILL_CNT   -- 금일 주문건수
       , NVL(SUM(B.CANCEL_TOT), 0)                   AS CANCEL_AMT -- 금일 취소액
    FROM hmsfns.MMEMBSTB A
       , hmsfns.SDAILYTB B
   WHERE A.CHAIN_NO   = 'C001' -- 검증 대상 체인번호
     AND B.MS_NO      = A.MS_NO
     AND B.SALE_DATE  = TO_CHAR(CURRENT_DATE, 'YYYYMMDD');
  ```

### 8.2 상품 매출 TOP 5 순위 목록
* **대조 화면 지표**: 당월 매출 기준 상위 판매 상품 1~5위 리스트
* **DB 검증 SQL**:
  ```sql
  SELECT B.GOODS_CD
       , C.GOODS_NM
       , SUM(B.SALE_AMT) AS SALE_AMT
    FROM hmsfns.MMEMBSTB A
       , hmsfns.SGOODMTB B
       , hmsfns.TGOODSTB C
   WHERE A.CHAIN_NO = 'C001'
     AND B.MS_NO    = A.MS_NO
     AND B.SALE_MM  = TO_CHAR(CURRENT_DATE, 'YYYYMM')
     AND C.CHAIN_NO = A.CHAIN_NO
     AND C.GOODS_CD = B.GOODS_CD
   GROUP BY B.GOODS_CD, C.GOODS_NM
   ORDER BY SALE_AMT DESC
   LIMIT 5;
  ```

### 8.3 결제 수단별 매출 분포 (도넛 차트)
* **대조 화면 지표**: 현금, 카드, 블루멤버스 사용액, 임직원 할인액 비율
* **DB 검증 SQL (현금/카드)**:
  ```sql
  SELECT SUM(B.CASH_AMT) AS CASH_AMT
       , SUM(B.CARD_AMT) AS CARD_AMT
    FROM hmsfns.MMEMBSTB A
       , hmsfns.SMONTHTB B
   WHERE A.CHAIN_NO = 'C001'
     AND B.MS_NO    = A.MS_NO
     AND B.SALE_MM  = TO_CHAR(CURRENT_DATE, 'YYYYMM');
  ```

