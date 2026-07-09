# Admin_System_00006 (사용자 보안정책) 데이터 흐름 가이드

본 문서는 관리자 전용 화면인 **사용자 보안정책 (`admin_system_00006`)**에서 설정하는 보안 관련 정책 설정 데이터가 백엔드 시스템 및 데이터베이스에서 어떻게 저장되고 소비(소요)되는지 분석한 흐름 정보입니다.

---

## 1. 대상 데이터베이스 테이블 (`hmsfns.SECURETB`)

사용자 보안정책 화면에서 설정을 변경하고 저장하면 **`hmsfns.SECURETB`** 테이블의 단일 레코드가 업데이트(UPDATE)됩니다.

---

## 2. 컬럼별 데이터 소비 및 비즈니스 로직 연동 현황

보안정책 테이블의 컬럼들은 성격에 따라 **인증 실패 처리(Spring Security)**, **비밀번호 복잡도 유효성 검사**, 또는 **추후 확장/미사용 설정**으로 나뉘어 소비됩니다.

### 2.1 로그인 인증 실패 및 계정 잠금 정책 (Spring Security 연동)

이 영역의 설정값은 사용자가 로그인 시도를 실패했을 때 `LoginFailureHandler.java` 클래스에서 실시간으로 참조하여 계정을 잠그는 로직에 소비됩니다.

| 컬럼명 | 데이터 타입 | 설명 | 실제 소비/사용되는 곳 (Java / SQL) |
| :--- | :--- | :--- | :--- |
| **`LOGIN_FAIL_LOCK_USE`** | `VARCHAR2(1)` | 로그인 실패 임계치 도달 시 계정 잠금 여부 (Y/N) | `LoginFailureHandler.java` 에서 잠금 기능 작동 여부를 판별하는 데 사용. |
| **`LOGIN_FAIL_LOCK_CNT`** | `NUMBER(8)` | 계정을 잠그기 전 허용되는 최대 로그인 실패 횟수 | `LoginFailureHandler.java` 에서 현재 실패 횟수(`AUTH_FAILURE_CNT`)와 비교하여 초과 시 `setAccountLock`을 호출하여 `MUSERSTB.ACCT_LOCK = 'Y'` 처리함. |
| **`LOCK_AUTO_RELEASE_USE`** | `VARCHAR2(1)` | 잠금 자동 해제 기능 사용 여부 (Y/N) | *[미소비]* DTO(`SecureDto.java`)에는 로드되나, 현재 자바 로그인 핸들러나 DB 트리거 내 실제 해제 로직은 동작하지 않음. |
| **`LOCK_AUTO_RELEASE_MIN`** | `NUMBER(8)` | 자동 해제 대기 시간 (분 단위) | *[미소비]* DTO에는 로드되나, 자바 로그인 핸들러 내 실제 타이머/해제 로직은 동작하지 않음. |

### 2.2 미접속 차단 정책

| 컬럼명 | 데이터 타입 | 설명 | 실제 소비/사용되는 곳 (Java / SQL) |
| :--- | :--- | :--- | :--- |
| **`UNCONNECT_DISABLE_USE`** | `VARCHAR2(1)` | 장기 미접속 사용자 계정 비활성화 여부 (Y/N) | *[미소비]* DTO에는 로드되나, 실제 Java 로그인 차단 필터나 DB 배치 프로시저에서 계정을 비활성화(`ACCT_ENABLE = 'N'`)하는 추가 로직은 부재함. |
| **`UNCONNECT_DISABLE_DATE`** | `NUMBER(8)` | 비활성화 처리 기준 미접속 일수 | *[미소비]* DTO에는 로드되나, 실제 배치 작업 등에 활용되지 않음. |

### 2.3 비밀번호 작성 규칙 및 복잡도 검증 정책 (비밀번호 변경/가입 연동)

이 영역의 설정값은 사용자가 비밀번호를 신규 생성하거나 변경할 때 비밀번호의 강도와 규칙을 강제하기 위한 서버 및 DB 검증 로직에서 소비됩니다.

| 컬럼명 | 데이터 타입 | 설명 | 실제 소비/사용되는 곳 (Java / SQL) |
| :--- | :--- | :--- | :--- |
| **`PW_MIN_LENGTH_USE`** | `VARCHAR2(1)` | 비밀번호 최소 길이 규칙 사용 여부 (Y/N) | `UserAuth_Sql.xml` 의 `getPasswordChk` 쿼리 및 DB 함수 `F_PASSWORD_CHK` 내 비밀번호 검증에 사용. |
| **`PW_MIN_LENGTH`** | `NUMBER(8)` | 비밀번호 최소 자릿수 제한값 | 비밀번호 변경 컨트롤러(`Hq_Emp_00002_Controller.java`, `St_Emp_00002_Controller.java`)의 입력 패스워드 길이 검증에 사용. |
| **`PW_SPECIAL_CHAR_USE`** | `VARCHAR2(1)` | 특수문자 필수 포함 여부 (Y/N) | 패스워드 특수문자 규칙 사용 여부 판별에 사용. |
| **`PW_SPECIAL_CHAR_MIN_LENGTH`** | `NUMBER(8)` | 필수 포함 특수문자 최소 개수 | 패스워드 검증 쿼리 `getPasswordChk` 내 특수문자 정규식(`REGEXP_COUNT(pwd, '[[:punct:]]')`) 비교값으로 소비. |
| **`PW_NUMBER_USE`** | `VARCHAR2(1)` | 숫자 필수 포함 여부 (Y/N) | 패스워드 숫자 규칙 사용 여부 판별에 사용. |
| **`PW_NUMBER_MIN_LENGTH`** | `NUMBER(8)` | 필수 포함 숫자 최소 개수 | 패스워드 검증 쿼리 `getPasswordChk` 내 숫자 정규식(`REGEXP_COUNT(pwd, '[[:digit:]]')`) 비교값으로 소비. |
| **`PW_ENG_CHAR_USE`** | `VARCHAR2(1)` | 영문자 필수 포함 여부 (Y/N) | 패스워드 영문자 규칙 사용 여부 판별에 사용. |
| **`PW_ENG_CHAR_MIN_LENGTH`** | `NUMBER(8)` | 필수 포함 영문자 최소 개수 | 패스워드 검증 쿼리 `getPasswordChk` 내 영문자 정규식(`REGEXP_COUNT(pwd, '[[:alpha:]]')`) 비교값으로 소비. |
| **`PW_CHANGE_DATE_USE`** | `VARCHAR2(1)` | 비밀번호 정기 변경 주기 규칙 사용 여부 (Y/N) | *[미소비]* DTO에는 로드되나, 현재 자바 비밀번호 변경 안내 필터 등에서 실제 변경 권고일 계산에 소비되지 않음. |
| **`PW_CHANGE_DATE`** | `NUMBER(8)` | 비밀번호 정기 변경 주기 (일 단위) | *[미소비]* DTO에는 로드되나, 실제 강제 변경 연동은 구현되어 있지 않음. |

---

## 3. 전체 데이터 가공 및 소요 흐름 다이어그램

```text
[admin_system_00006 (보안정책 설정 화면)]
           │
           ▼ (수정 및 저장 요청)
[Admin_System_00006_Controller / Service]
           │
           ▼ (MyBatis updateSecure 실행)
┌──────────────────────────────────────────────┐
│            DB Table: HMSFNB.SECURETB         │
└──────────────────────┬───────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       ▼ (MyBatis selectSecureInfo)    ▼ (MyBatis getPasswordChk / F_PASSWORD_CHK)
[SecureDto (보안설정 메모리 객체)]     [비밀번호 복잡도 유효성 검사 로직]
       │                                       ▲
       ├────────────────────────┐              │
       ▼                        ▼              │ (비밀번호 변경 요청 시)
[LoginFailureHandler.java]   [미소비/확장예정 필드] [Hq_Emp_00002_Service / St_Emp_00002_Service]
 - 계정 잠금 여부 체크         - 잠금 자동 해제
 - 계정 잠금 임계치 도달 처리    - 장기 미접속 차단
                               - 패스워드 주기 변경
```
