# QA Report: Hq_Sales_00025 외상 매출 및 입금내역조회 (본사)
**작성일**: 2026-07-07  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 본사 매출분석 > 결제관리 > 외상 매출 및 입금내역조회 (hq_sales_00025)  
**테스트 환경**: localhost:8080 (로컬 개발 서버)  
**접속 ID/PW**: `shopadmin` / `0000` (본사 관리자 권한 로그인 완료)

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
| :--- | :--- |
| **Controller** | `backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/hq/sales/Hq_Sales_00025_Controller.java` |
| **Service** | `backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/hq/sales/Hq_Sales_00025_Service.java` |
| **Mapper (Interface)** | `backoffice/hyundai-backoffice-layer-persistence/src/main/java/com/hyundai/backoffice/webapp/dao/hq/sales/Hq_Sales_00025_Mapper.java` |
| **SQL XML** | `backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/sales/Hq_Sales_00025_Sql.xml` |
| **DTO** | `backoffice/hyundai-backoffice-layer-domain/src/main/java/com/hyundai/backoffice/webapp/dto/hq/sales/Hq_Sales_00025_WeasSaleListDto.java` |

---

## 2. 엔드포인트 및 SQL 구조 분석

### 2.1 Base URL
```text
POST /backoffice/data/hq/sales/hq_sales_00025/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP Method | 기능 | ServiceLog 구분 | 연관 쿼리 ID |
| :--- | :---: | :--- | :---: | :--- |
| `/search` | POST | 외상 매출 및 입금내역 조회 | `SELECT` | `getTotalCnt`, `searchWeasList` |

### 2.3 CUD 및 트리거 연쇄 검증
* **조회 전용 분석**: 본 화면은 CUD(저장, 수정, 삭제)가 전혀 없이 데이터 조회를 주로 하는 **순수 SELECT 조회 전용 화면**입니다.
* **트리거 및 연쇄 반응**: 관련 테이블 `STRNWETB` 및 `WEASDTTB` 테이블에 설정된 DB 트리거 및 프로시저가 전혀 존재하지 않음을 확인했습니다. (Depth 3 영향도 분석 대상 없음)
* **형변환 결함(Numeric Empty Casting)**: CUD 저장이 발생하지 않으므로, 숫자 컬럼 공백 결함은 발생하지 않습니다.

---

## 3. DB 테이블 스키마 및 실데이터 검증 (EDB PostgreSQL)

개발 EDB 데이터베이스 (`192.168.10.206:5432`)에 접속하여 연동 테이블 5종의 적재 상태를 직접 검증한 결과입니다.

### 3.1 테이블 건수 확인

1. **`hmsfns.STRNWETB`** (외상 매출 테이블) — 로우 수: **9건**
2. **`hmsfns.WEASDTTB`** (외상 입금 상세 테이블) — 로우 수: **1건**
3. **`hmsfns.MMEMBSTB`** (매장 마스터 테이블) — 로우 수: **4건**
4. **`hmsfns.MVNDRMTB`** (거래처 마스터 테이블) — 로우 수: **11건**
5. **`hmsfns.MUSERSTB`** (사용자 마스터 테이블) — 로우 수: **254건**

### 3.2 DB 적재 데이터 분석 결과
* **외상매출 (`STRNWETB`) 실데이터 샘플 (NC0007 매장)**:

| SALE_DATE | MS_NO | POS_NO | BILL_NO | VENDOR_CD | WEAS_AMT | PAID_AMT |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `20230925` | `NC0007` | `01` | `0006` | `C002` | `75500.00` | `0.00` |
| `20251027` | `NC0007` | `01` | `0002` | `C002` | `10000.00` | `0.00` |
| `20251028` | `NC0007` | `01` | `0002` | `C002` | `10000.00` | `0.00` |

---

## 4. SQL Mapper 검증 및 호환성 경고 ⚠️

`Hq_Sales_00025_Sql.xml` 파일 내에 다음과 같은 Oracle 전용 구문 및 비표준 문법이 다수 포함되어 있습니다.

1. **Oracle Outer Join 기법 `(+)` 다수 사용**:
   ```sql
   AND WE.SALE_DATE = WD.ORD_SALE_DATE(+)
   AND WE.MS_NO     = WD.ORD_MS_NO(+)
   ```
   * **영향**: EDB Oracle Compatibility 모드에서는 해석되나 표준 PostgreSQL 엔진에서는 문법 오류가 발생합니다.
   * **조치 권고사항**: ANSI 표준 `LEFT OUTER JOIN` 구문으로 명시적 리팩토링할 것을 권고합니다.
2. **`SUBSTR(A.ORG_BILL_NO, 0, 8)`**:
   * **영향**: Oracle `SUBSTR`은 0과 1을 동일하게 다루어 정상 해석되나, 표준 SQL 표준 인덱스는 1부터 시작합니다.
   * **조치 권고사항**: `SUBSTR(A.ORG_BILL_NO, 1, 8)`로 변경 권고합니다.
3. **`ROWNUM RNUM` 및 `TO_NUMBER`를 이용한 페이징 처리**:
   * **조치 권고사항**: 표준 PostgreSQL 규격의 `LIMIT` 및 `OFFSET` 구문으로 전환을 권고합니다.

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 및 권한 현황

| 항목 | 결과 |
| :--- | :--- |
| **서버 접속 URL** | `http://localhost:8080` ✅ |
| **로그인 사용자** | `shopadmin` (비밀번호: `0000`) ✅ |
| **화면 경로** | 매출분석 > 결제관리 > 외상 매출 및 입금내역조회 (hq_sales_00025) ✅ |
| **특이사항** | `shopadmin` 본사 권한으로 접속 시 모든 매장(NC0007, NC0008 등)의 외상 매출 및 입금 내역을 오류 없이 성공적으로 조회 완료. |

### 5.2 기능별 테스트 결과

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI | 판정 |
| :--- | :--- | :--- | :--- | :---: |
| **외상 내역 조회** | `/search` | ✅ 구현 완료 | ✅ 데이터 표출 정상 (9건) | **PASS** |
| **매장별 필터** | `/search` | ✅ 구현 완료 | ✅ 필터링 정상 (NC0007) | **PASS** |
| **거래처명 검색** | `/search` | ✅ 구현 완료 | ✅ 거래처 부분 매칭 성공 | **PASS** |

---

## 6. 검증 항목 체크리스트

| 검증 항목 | 상태 | 비고 |
| :--- | :--- | :--- |
| `@RestController`, `@Validated` | ✅ 정상 | 정상 작동 확인 |
| `@ServiceLog` 설정 여부 | ✅ 정상 | menu="외상 매출 및 입금내역 조회", type=SELECT 적용 |
| CUD 및 관련 트리거 로직 | ✅ 해당 없음 | 단순 조회(SELECT) 화면으로 로직 전이 없음 |
| EDB PostgreSQL 데이터 정합성 | ✅ 정상 | `STRNWETB` 등 테이블 데이터 연계 일치 |
| Numeric 컬럼 공백 결함 | ✅ 해당 없음 | CUD가 발생하지 않아 공백 캐스팅 대상 아님 |

---

## 7. 종합 판정

| 구분 | 결과 |
| :--- | :--- |
| **화면 로딩 및 그리드 바인딩** | ✅ PASS |
| **조회 및 필터 기능 (SELECT)** | ✅ PASS |
| **결함 항목 (Oracle 전용 문법)** | ⚠️ Warning (PostgreSQL 마이그레이션 대비 변환 권고) |
| **종합** | **✅ PASS (현재 EDB Oracle 호환 환경 기준)** |

---
*본 리포트는 DDL 스크립트 정적 스캔, Java/XML 코드베이스 1:1 대조 및 psycopg2를 통한 EDB 데이터베이스 연동 분석 결과를 취합하여 사실대로 작성되었습니다.*
