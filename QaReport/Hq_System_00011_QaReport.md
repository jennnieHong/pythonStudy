# QA Report: Hq_System_00011 웹 서비스 이벤트 로그 조회 (HQ)
**작성일**: 2026-06-12  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 시스템관리 > 영업정보시스템 > 웹 서비스 이벤트 로그 조회 (본사용: `hq_system_00011`)  
**테스트 환경**: http://localhost:8080 (로컬 개발 Tomcat 서버)  
**데이터베이스**: 192.168.10.206:5432/edb (EDB Postgres 개발 DB)  
**접속 ID/PW**: shopadmin / 0000 (본사 관리자 권한)

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/hq/system/Hq_System_00011_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/hq/system/Hq_System_00011_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/hq/system/Hq_System_00011_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../resources/sqlmapper/system/Hq_System_00011_Sql.xml` |
| DTO | `hyundai-backoffice-layer-domain/.../dto/hq/system/Hq_System_00011_ServiceLogListDto.java` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/system/hq_system_00011
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
|-----------|------|------|------------|
| `/searchServiceLogList` | POST | 웹 서비스 이벤트 로그 목록 조회 및 페이징 | SELECT (웹 서비스 이벤트 로그 조회) |

---

## 3. SQL Mapper 호환성 개선 사항 (Oracle -> PostgreSQL)

기존 XML 매퍼 파일에 존재하던 Oracle 전용 비표준 문법을 PostgreSQL(EDB) 및 표준 ANSI SQL 규격에 맞춰 현대화 및 개선하였습니다.

### 3.1 아우터 조인 `(+)` 문법 변환
- **기존 문법 (Oracle 전용)**:
  `WHERE SR.USER_ID = MU.USER_ID(+) AND MU.MS_NO = MB.MS_NO(+)`
- **변환 문법 (ANSI 표준)**:
  `FROM hmsfns.SRVLOGTB SR LEFT OUTER JOIN hmsfns.MUSERSTB MU ON SR.USER_ID = MU.USER_ID LEFT OUTER JOIN hmsfns.MMEMBSTB MB ON MU.MS_NO = MB.MS_NO`

### 3.2 ROWNUM 페이징 및 순번 표시 방식 보완
- **기존 문법 (Oracle ROWNUM 페이징)**:
  중첩 3단계 서브쿼리에서 `ROWNUM ROW_NO`를 추출해 페이징하고, `ROW_NUMBER() OVER (ORDER BY SR.LOG_SEQ) RNUM`을 반환하여 화면에 내림차순 절대 인덱스(전체 건수 기준 역순 순번)를 표시.
- **변환 문법 (PostgreSQL 2-Window-Function)**:
  PostgreSQL 및 ANSI 표준을 준수하면서 화면의 절대 인덱스 표현 방식을 100% 동일하게 유지하기 위해 두 개의 ROW_NUMBER() 함수를 사용하였습니다.
  1) `ROW_NUMBER() OVER (ORDER BY SR.LOG_SEQ) RNUM`: 원래 화면처럼 전체 건수 기준 내림차순 절대 순번 매핑.
  2) `ROW_NUMBER() OVER (ORDER BY SR.LOG_SEQ DESC) ROW_NO`: 페이징 처리를 위한 최신순 인덱스로서 `WHERE ROW_NO >= #{startCount} AND ROW_NO <= #{endCount}` 조건에서 필터링 하도록 성능 최적화 완료.

### 3.3 `getTotalCnt` 카운팅 쿼리 성능 개선
- 기존에는 `ROW_NUMBER()` 윈도우 함수 및 모든 컬럼을 조회하는 무거운 서브쿼리를 감싸서 `COUNT(1)`을 하던 비효율적 방식에서, 서브쿼리를 제거하고 테이블 조인과 검색 조건만을 대상으로 하는 직관적이고 가벼운 `COUNT(1)` 형태로 최적화 완료하였습니다.

---

## 4. DB 로그 연동 검증

대상 화면(`hq_system_00011`)은 조회(SELECT) 화면으로 데이터베이스 내 수동 CUD 변경사항은 없으나, Spring AOP 설정(@ServiceLog)에 의하여 화면 진입 및 조회 시 자동으로 `hmsfns.SRVLOGTB`에 접근 로그가 기록됩니다.

### 4.1 Playwright E2E 실행 중 발생한 최신 로그 검증
- **검색 조건**: `USER_ID = 'shopadmin'`  
- **정렬 조건**: `CREATE_DTIME DESC, LOG_SEQ DESC`  
- **DB 조회 결과**:
```
LOG_SEQ   | USER_ID   | REMOTE_IP       | SERVICE_MENU                 | SERVICE_NAME                 | TYPE   | CREATE_DTIME
----------|-----------|-----------------|------------------------------|------------------------------|--------|---------------
1295684   | shopadmin | 0:0:0:0:0:0:0:1 | 웹 서비스 이벤트 로그 조회  | 웹 서비스 이벤트 로그 조회  | SELECT | 20260612165900
1295683   | shopadmin | 0:0:0:0:0:0:0:1 | 웹 서비스 이벤트 로그 조회  | 웹 서비스 이벤트 로그 조회  | SELECT | 20260612165857
```
- E2E 테스트 동작을 수행하는 과정에서 `shopadmin`이 호출한 이벤트 로그가 DB에 누락 없이 정확하게 자동 인서트 됨을 검증 완료했습니다. ✅

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 (HQ) | 성공 (`shopadmin` / `0000`) ✅ |
| 화면 경로 | 시스템관리 > 영업정보시스템 > 웹 서비스 이벤트 로그 조회 ✅ |
| 화면 로딩 및 데이터 바인딩 | 정상 작동 ✅ |

### 5.2 기능별 테스트 결과

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI | 판정 |
|------|-----------|---------|---------|------|
| **로그 목록 조회** | `/searchServiceLogList` | ✅ 구현 완료 | ✅ 데이터 표출 정상 | **PASS** |
| **조건 검색 (일자/ID/IP)** | `/searchServiceLogList` | ✅ 필터 필터링 정상 | ✅ Bootstrap-table 바인딩 | **PASS** |
| **초기화 버튼** | `clearFields` | ✅ 정상 작동 | ✅ 검색폼 초기화 완료 | **PASS** |

---

## 6. 종합 판정

| 구분 | 결과 |
|------|------|
| **SQL Mapper 표준 변환** | **✅ PASS (LEFT JOIN & ROW_NUMBER 페이징)** |
| **Tomcat 빌드 및 배포** | **✅ PASS** |
| **Playwright E2E UI 시나리오** | **✅ PASS** |
| **Spring AOP @ServiceLog 로깅** | **✅ PASS (DB 인서트 완벽 일치)** |
| **최종 판정** | **✅ PASS** |

---

## 7. 첨부 스크린샷 (HQ)

- **HQ - 기본 조회**: ![HQ - 기본 조회](file:///D:/hmTest/backoffice/QaReport/hq_system_00011_search.png)
- **HQ - ID 검색**: ![HQ - ID 검색](file:///D:/hmTest/backoffice/QaReport/hq_system_00011_search_id.png)
- **HQ - IP 검색**: ![HQ - IP 검색](file:///D:/hmTest/backoffice/QaReport/hq_system_00011_search_ip.png)
- **HQ - 초기화 완료**: ![HQ - 초기화 완료](file:///D:/hmTest/backoffice/QaReport/hq_system_00011_reset.png)
