# Hq_Vendor_00001 단위테스트 및 마이그레이션 QA 리포트

## 1. 테스트 개요

| 항목 | 내용 |
|------|------|
| 테스트 일자 | 2026-06-02 |
| 대상 화면 | hq_vendor_00001 (구매의뢰요청관리) |
| 담당자 | AI Assistant (Antigravity) |
| 마이그레이션 환경 | Oracle -> PostgreSQL (EPAS) |
| 테스트 목적 | 화면 정상 로딩, CUD 기능 검증, Oracle 종속 구문 및 트리거 로직 마이그레이션 점검 |
| DB 접속 정보 | **IP**: 192.168.10.206 / **Port**: 5432 <br> **DB**: edb <br> **User**: hmsfns_was / **PW**: astems3! |

---

## 2. 권한 및 계정 정보 검증

`Backoffice_Screen_TestAccount_v2.xlsx` 매트릭스 검증 완료.

| 시스템 | 분류 | 화면 ID | 계정명 | 비밀번호 | 권한 등급 |
|--------|------|---------|--------|----------|-----------|
| 본사 | POS/구매 | hq_vendor_00001 | shopadmin | 0000 | ROLE_USER |

> 💡 **참고**: 테스트 진행 시 shopadmin 계정으로 로그인하여 브라우저 E2E 테스트(조회, 저장, 복사, 확정, 삭제, 출력)를 완벽하게 완주했습니다.

---

## 3. 관련 테이블 및 프로시저/트리거 매핑 내역

| 발생 로직 (API) | 조작 타입 | 연관 테이블 | DDL 트리거 유무 | 비고 |
|-----------------|-----------|-------------|-----------------|------|
| `saveRequest`, `deleteRequest` 등 | INSERT/UPDATE/DELETE | `OBREQHTB` | **없음 (False)** | DB 트리거 및 프로시저 호출 없음 |
| `addRequestGoods`, `deleteRequestGoods` 등 | MERGE/INSERT/DELETE | `OBREQDTB` | **없음 (False)** | DB 트리거 및 프로시저 호출 없음 |

> ✅ **DB 오브젝트 분석 결과**: 해당 화면에서 사용하는 테이블(`OBREQHTB`, `OBREQDTB`)에는 연결된 **DB 트리거가 일절 존재하지 않습니다.** 또한 Java Service 레이어 및 SQL Mapper 쿼리 상에서도 **별도의 DB 프로시저(Procedure)나 스토어드 펑션(Function)을 호출하는 로직이 없음을 최종 확인**했습니다. 따라서 마이그레이션 시 트리거 누락이나 프로시저 호환성 문제로부터 완전히 자유로운 모듈입니다.

---

## 4. 실제 문제 수정 내역 및 기술적 결함 조치

### 4.1 SQL Mapper 호환성 결함 조치 (Oracle -> PostgreSQL)
`Hq_Vendor_00001_Sql.xml` 및 동일 패턴이 존재하는 `St_Vendor_00001_Sql.xml` 분석 결과, PostgreSQL 환경에서 Runtime Exception을 유발하는 치명적인 타입 캐스팅 오류 3건을 발견 및 픽스했습니다.

**[수정 완료 1] 텍스트-숫자 연산 (text - integer) 에러**
* **발생 위치**: `getReqGoodsList` (상세 품목 로드)
* **오류 내역**: `ERROR: operator does not exist: text - integer`
* **조치 내용**: `LPAD(CAST(COALESCE(MAX(CAST(ESTIM_SEQ AS INTEGER)), 0) - 1 AS TEXT), 10, '0')` 로 수정 완료.

**[수정 완료 2] 수량 및 단가 산술 연산 (character varying * double precision) 에러**
* **발생 위치**: `addRequestGoods` (상품 추가 저장)
* **오류 내역**: `ERROR: operator does not exist: character varying * double precision`
* **조치 내용**: 
  ```sql
  -- 수정 전
  DT.PURCH_AMT  = #{requestQty} * #{price},
  -- 수정 후
  DT.PURCH_AMT  = CAST(#{requestQty} AS NUMERIC) * CAST(#{price} AS NUMERIC),
  ```

**[수정 완료 3] 전표 복사(채번) 시 산술 연산 (text + integer) 에러**
* **발생 위치**: `getNewReqNo` ('복사' 버튼 클릭 시 신규 채번)
* **오류 내역**: `ERROR: operator does not exist: text + integer`
* **원인**: `SUBSTR(PURCH_REQ_NO, 11, 2) + 1` 구문 오류
* **조치 내용**: 
  ```sql
  -- 수정 후
  NVL(LPAD(CAST(MAX(CAST(SUBSTR(PURCH_REQ_NO, 11, 2) AS INTEGER))+1 AS TEXT), '2', '0'), '01')
  ```

### 4.2 자바 백엔드 시스템 결함 (GlobalExceptionHandler) 조치
**[수정 완료] StringIndexOutOfBoundsException 버그 픽스**
* **발생 위치**: `GlobalExceptionHandler.java:247`
* **오류 내역**: 에러 메시지가 2000바이트 이하일 때 무조건 `.substring(0, 2000)`을 호출하여 발생. 원래 띄워야 할 진짜 원인 에러 메시지를 삼키고 자체적으로 예외를 발생시켜 서버 팝업 렌더링을 멈추게 한 주범입니다.
* **조치 내용**: `errorTrace.length() > 2000 ? errorTrace.substring(0, 2000) : errorTrace` 처럼 삼항 연산자를 이용해 문자열 길이에 따른 방어 코드를 작성하여 자바 모듈 공통 패치를 완료했습니다.

---

## 5. 브라우저 최종 E2E (End-to-End) 테스트 결과

위 4번 항목의 이슈 패치 후, Tomcat을 재구동하고 브라우저 에이전트를 통해 아래와 같이 테스트 절차를 수행 및 패스하였습니다.

### 5.1 테스트 진행 절차
1. `/backoffice/view/main/hq/vendor/hq_vendor_00001` 경로에 `shopadmin`으로 접속.
2. [조회] 클릭하여 전표 목록 확인.
3. [초기화] 클릭 후, 새 전표에 매장코드('[오픈] CAFE') 할당.
4. 좌측 하단 상품 검색에서 `T0000555` 조회 후, 수량 '2'개로 체크하여 우측 하단 상세품목 리스트로 [추가].
5. 우상단 [저장] 버튼 클릭하여 신규 전표 발행 및 성공 확인(HTTP 200).
6. 발행된 전표를 선택 후 [복사] 클릭하여 신규 전표로 복제됨을 확인(`getNewReqNo` 정상 작동).
7. 복사된 전표를 선택 후 [확정] 클릭하여 상태값 변경 확인.
8. 최초 발행했던 테스트 전표를 선택 후 [삭제] 버튼 클릭하여 DB에서 정상 삭제.
9. [출력] 버튼 클릭으로 팝업 오픈 확인.

### 5.2 테스트 판정
| 기능 | 엔드포인트명 | 상태코드 | 동작 및 UI 렌더링 | 판정 |
|------|-----------|---------|---------|------|
| 전표 목록 조회 | `/getReqHdList` | 200 OK | 정상 표시 | **PASS** |
| 전표 상세 로드 | `/getReqGoodsList` | 200 OK | 정상 로드 (500 에러 해결) | **PASS** |
| 마스터 추가/저장 | `/saveRequest` | 200 OK | 정상 저장 | **PASS** |
| 상품 품목 추가 | `/addRequestGoods` | 200 OK | 정상 삽입 (500 에러 해결) | **PASS** |
| 전표 복사 | `/copyRequest` | 200 OK | 정상 채번 및 복제 (500 에러 해결) | **PASS** |
| 전표 확정/삭제 | `/confirm...` 등 | 200 OK | 정상 삭제/확정 반영 | **PASS** |

---

## 6. 결론 및 종합 판정
| 구분 | 결과 |
|------|------|
| DB 트리거 유무 및 검증 | ✅ PASS (트리거 없음 확인) |
| DB 프로시저 연동 여부 | ✅ PASS (프로시저 호출 없음 확인) |
| SQL 호환성 결함 조치 | ✅ PASS (PostgreSQL 산술 타입 캐스팅 오류 3종 모두 수정 완) |
| 자바 모듈 버그 조치 | ✅ PASS (GlobalExceptionHandler 예외 은닉 현상 완벽 조치 완) |
| 브라우저 기능 테스트 | ✅ PASS (모든 버튼 및 E2E CRUD 사이클 구동 완) |
| **최종 상태** | **✅ 마이그레이션 QA 완료** |
