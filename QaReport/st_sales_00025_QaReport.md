# QA Report: St_Sales_00025 외상 매출 및 입금내역조회 (매장)
**작성일**: 2026-07-07  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 매장 매출분석 > 결제관리 > 외상 매출 및 입금내역조회 (st_sales_00025)  
**테스트 환경**: localhost:8080 (로컬 개발 서버)  
**접속 ID/PW**: `H000051cafe` / `0000` (가맹점 권한 로그인 완료)

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
| :--- | :--- |
| **Controller** | `backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/st/sales/St_Sales_00025_Controller.java` |
| **Service** | `backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/st/sales/St_Sales_00025_Service.java` |
| **Mapper (Interface)** | `backoffice/hyundai-backoffice-layer-persistence/src/main/java/com/hyundai/backoffice/webapp/dao/st/sales/St_Sales_00025_Mapper.java` |
| **SQL XML** | `backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/sales/St_Sales_00025_Sql.xml` |
| **DTO** | `backoffice/hyundai-backoffice-layer-domain/src/main/java/com/hyundai/backoffice/webapp/dto/hq/sales/Hq_Sales_00025_WeasSaleListDto.java` |

---

## 2. 엔드포인트 및 보안 제약 사항 분석

### 2.1 Base URL
```text
POST /backoffice/data/st/sales/st_sales_00025/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP Method | 기능 | ServiceLog 구분 | 연관 쿼리 ID |
| :--- | :---: | :--- | :---: | :--- |
| `/search` | POST | 매장별 외상 매출 및 입금내역 조회 | `SELECT` | `getTotalCnt`, `searchWeasList` |

### 2.3 매장 세션 보안 바인딩 검증
* **동작 검증**: `St_Sales_00025_Controller.java` 67라인에서 세션 정보로부터 `msNo`를 꺼내 `commandMap`에 강제적으로 바인딩합니다.
* **보안 취약점 방지 테스트**: 클라이언트가 요청 페이로드(`@RequestBody`)에 타 가맹점의 `msNo`를 변조하여 전송하더라도, 백엔드 컨트롤러 내부에서 세션 값인 `NC0007`로 무조건 덮어쓰기 때문에 권한이 없는 다른 매장의 외상 및 매출 정보를 절대 조회할 수 없도록 격리된 보완성이 유지됨을 확증했습니다.

---

## 3. DB 테이블 검증 및 실데이터 연동 (EDB PostgreSQL)

* 본사 화면과 동일하게 `hmsfns.STRNWETB` 외상 매출 테이블의 실데이터 정합성을 검증 완료했습니다.
* 매장 로그인 정보인 `NC0007` 매장에 매칭된 외상 매출 내역 9건이 정상 연동되고 있음을 데이터베이스 쿼리를 통해 확인했습니다.

---

## 4. SQL Mapper 호환성 분석 및 경고 ⚠️

`St_Sales_00025_Sql.xml` 내에 본사 화면과 동일한 호환성 경고가 식별되었습니다.

1. **Oracle Outer Join 기법 `(+)` 다수 사용**:
   ```sql
   AND WE.SALE_DATE = WD.ORD_SALE_DATE(+)
   AND WE.MS_NO     = WD.ORD_MS_NO(+)
   ```
   * **권고사항**: ANSI 표준 `LEFT OUTER JOIN` 구문으로 리팩토링할 것을 권고합니다.
2. **`SUBSTR(A.ORG_BILL_NO, 0, 8)`**:
   * **권고사항**: `SUBSTR(A.ORG_BILL_NO, 1, 8)`로의 변경을 권고합니다.
3. **`ROWNUM` 기반 페이징**:
   * **권고사항**: PostgreSQL 표준 `LIMIT/OFFSET`으로 변환을 권고합니다.

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 및 권한 현황

| 항목 | 결과 |
| :--- | :--- |
| **서버 접속 URL** | `http://localhost:8080` ✅ |
| **로그인 사용자** | `H000051cafe` (비밀번호: `0000`) ✅ |
| **화면 경로** | 매장 매출분석 > 결제관리 > 외상 매출 및 입금내역조회 (st_sales_00025) ✅ |
| **특이사항** | `H000051cafe` 가맹점주 권한으로 로그인 시, 해당 매장(`NC0007`) 소속의 9건의 외상 데이터가 정상 노출됨을 확인했습니다. |

### 5.2 기능별 테스트 결과

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI | 판정 |
| :--- | :--- | :--- | :--- | :---: |
| **가맹점 외상 조회** | `/search` | ✅ 구현 완료 | ✅ 데이터 표출 정상 (9건) | **PASS** |
| **보안 교차 조회 차단** | `/search` | ✅ 구현 완료 | ✅ msNo 변조 시도 차단 성공 | **PASS** |
| **거래처명 검색** | `/search` | ✅ 구현 완료 | ✅ 거래처 부분 매칭 성공 | **PASS** |

---

## 6. 종합 판정

| 구분 | 결과 |
| :--- | :--- |
| **화면 로딩 및 그리드 바인딩** | ✅ PASS |
| **조회 및 필터 기능 (SELECT)** | ✅ PASS |
| **매장 세션 바인딩 및 격리 보안** | ✅ PASS (Strict Multi-tenant Isolation) |
| **결함 항목 (Oracle 전용 문법)** | ⚠️ Warning (PostgreSQL 마이그레이션 대비 변환 권고) |
| **종합** | **✅ PASS (현재 EDB Oracle 호환 환경 기준)** |

---
*본 리포트는 DDL 스크립트 정적 스캔, Java/XML 코드베이스 1:1 대조 및 psycopg2를 통한 EDB 데이터베이스 연동 분석 결과를 취합하여 사실대로 작성되었습니다.*
