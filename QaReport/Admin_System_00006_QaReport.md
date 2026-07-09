# QA Report: 사용자 보안정책 관리 (Admin_System_00006)

## 1. 테스트 목적 및 개요
시스템 관리자 권한으로 사용자 보안정책 설정 화면(`admin_system_00006`)을 테스트하여 계정 잠김 기준 및 비밀번호 난이도 등 보안정책 데이터 조회, 변경 저장 기능의 정합성을 검증합니다.

## 2. 테스트 환경 및 계정 정보
* **테스트 URL**: `http://localhost:8080/backoffice/view/main/admin/system/admin_system_00006`
* **접속 ID/PW**: `admin2` / `0000` (시스템 관리자 권한)
* **테스트 일시**: 2026년 06월 29일 14시 13분
* **대상 데이터베이스**: `192.168.10.206 / edb` (schema: `hmsfns`)
* **대상 테이블**: `hmsfns.SECURETB` (단일 행 저장)

---

## 3. 프로그램 분석 및 소스 코드 검토
1. **Java & XML 매퍼 연동**:
   * `Admin_System_00006_Controller.java`에서 `/selectSecure` 및 `/updateSecure` API를 정의합니다.
   * `Admin_System_00006_Sql.xml` 매퍼 쿼리를 호출하여 `hmsfns.SECURETB` 테이블을 SELECT 및 UPDATE 합니다.
2. **트리거 및 프로시저 영향도 검증**:
   * 데이터베이스 스키마 검색 결과, `hmsfns.SECURETB` 테이블에는 **연동된 어떠한 DB 트리거(Trigger)나 내장 프로시저(Stored Procedure)도 존재하지 않습니다**.
   * 따라서 해당 보안정책 변경 시 타 테이블로의 연쇄 반응(Depth 2 ~ Depth 3)은 발생하지 않는 단순 설정 관리 스펙임을 확인했습니다.
3. **형변환 결함 에러 체크**:
   * UI 단에서 전송되는 숫자형 항목들은 `int` 또는 `numeric` 타입 컬럼에 맞춰 MyBatis 파라미터가 유기적으로 매핑되어 있어, 빈 문자열로 인한 숫자 형변환 에러 위험이 없는 안정적인 쿼리 형태로 동작하고 있음을 확인했습니다.
4. **F_PASSWORD_CHK 함수 대체 및 검증**:
   * 기존 레거시 데이터베이스(Tibero)의 패스워드 유효성 검사 내장 함수(`F_PASSWORD_CHK`)는 EDB PostgreSQL 포팅 과정에서 **MyBatis XML 매퍼 내 표준 SQL 구문으로 완전히 이관 대체**되었습니다.
   * `UserAuth_Sql.xml`의 `getPasswordChk` 쿼리(Line 333)에서 `hmsfns.SECURETB`에 저장된 규칙값(`PW_MIN_LENGTH`, `PW_SPECIAL_CHAR_MIN_LENGTH` 등)을 서브쿼리 조인으로 조회하여, `REGEXP_COUNT`와 정규식 패턴(`[[:punct:]]`, `[[:digit:]]`, `[[:alpha:]]`)을 사용해 실시간으로 유효성을 리턴값(`0`~`4`)으로 판정합니다.
   * 해당 로직은 Java 서비스 레벨의 비밀번호 변경 로직인 `Hq_Emp_00002_Service.java` 및 `St_Emp_00002_Service.java`에서 성공적으로 호출되어 입력된 비밀번호가 설정된 보안 정책 규격에 부합하는지 안전하게 사전 필터링합니다.

---

## 4. E2E 테스트 시나리오 및 결과

### 4.1 기본 데이터 조회 및 노출 기능 검증
* **동작**: `admin2` 계정으로 로그인 후 `admin_system_00006` 화면으로 이동하여 기존 저장된 설정값을 화면의 각 컴포넌트(SelectPicker, Input)에 정상적으로 바인딩하여 노출했습니다.
* **상세 결과 데이터**:
  * 데이터베이스의 기존 `SECURETB.LOGIN_FAIL_LOCK_CNT` 값: **`5`**
  * 화면 상의 '잠김 실패횟수' 입력 란 초기 노출값: **`5`** (정상 일치 확인 ✅)

### 4.2 데이터 변경 및 저장 기능 검증
* **동작**:
  1. 화면 상에서 '잠김 실패횟수' 입력값을 `5` ➡️ **`8`**로 수정 입력했습니다.
  2. 우측 상단의 [저장] 버튼을 클릭했습니다.
  3. 나타난 Bootbox Confirm 확인 대화창에서 [확인]을 눌러 저장 요청(AJAX POST)을 전송했습니다.
* **검증 결과**:
  * 데이터베이스 `hmsfns.SECURETB` 테이블의 `LOGIN_FAIL_LOCK_CNT` 컬럼 값이 실시간으로 **`8`**로 정상 업데이트되었습니다. (저장 및 동기화 확인 ✅)
  * E2E 검증 시나리오 완료 후, 테스트 대상 행의 `LOGIN_FAIL_LOCK_CNT` 값을 원본 값인 **`5`**로 완벽하게 롤백(원복) 처리하였습니다.

### 4.3 스크린샷 검증
* **수정 전 화면**:
  ![Admin System Before Update](file:///D:/hmTest/backoffice/QaReport/admin_system_00006_1_list.png)
* **저장 성공 완료 화면**:
  ![Admin System After Save](file:///D:/hmTest/backoffice/QaReport/admin_system_00006_2_saved.png)

---

## 5. 결론 및 종합 의견
* 시스템 관리자 권한(`admin2`)을 통한 사용자 보안정책 설정 조회 및 저장 기능이 비즈니스 요구사항에 부합하게 정상 작동함을 검증했습니다.
* DB 수준에서 트리거 연쇄 반응이 없는 설정 단순 수정 화면으로, 데이터 롤백까지 안전하게 수행되어 최종 판정 **PASS** 처리합니다. (최종 판정: **PASS** ✅)
