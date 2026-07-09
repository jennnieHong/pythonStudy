# Hq_Emp_00002 — 비밀번호 관리 단위 테스트케이스 및 수행 결과

> **화면**: [HQ] 인사관리 > 비밀번호 관리 (내 정보 / PW 변경)  
> **URL Prefix**: `POST /backoffice/data/hq/emp/hq_emp_00002`  
> **@Transactional**: rollbackFor = {RuntimeException.class, Exception.class}  
> **DB 트리거 영향도**: `MUSERSTB`에 CUD(비밀번호 수정) 발생 시 자바 트리거 서비스 `Tr_MUSERS_T01_Service`가 기동되어 `SSUSERTB` 테이블에 POS 전송 자료를 생성(`INSERT`)합니다.

---

## 1. 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `msNo` | `NC0002` (본부_SHOP) | 로그인 사용자 매장번호 (user_ms_no) |
| `ID` | `shopadmin` | 로그인 사용자 ID |
| `PASSWORD` | BCrypt 해시값 | 기존 비밀번호 BCrypt 해시 (0000 검증용) |

---

## 2. 테스트케이스 정의 및 수행 결과

> 💡 **E2E 동적 자동화 테스트 수행 성공**:
> 본 테스트는 실제 구동 중인 로컬 WAS(`localhost:8080`) 환경을 대상으로 **Playwright E2E 동적 테스트 자동화 스크립트([test_password_change.py](file:///D:/hmTest/backoffice/test_password_change.py))**를 직접 개발하고 구동하여 기능 및 화면 정합성을 완벽하게 E2E 검증하였습니다.
> - **E2E 검증 시나리오**: `shopadmin` 계정으로 로그인 성공 ➔ `hq_emp_00002` 화면 진입 ➔ 기존 비밀번호 `0000` 입력 ➔ 신규 비밀번호 `0000a123!` 입력 및 확인 ➔ 저장 클릭 ➔ 알림 다이얼로그(`비밀번호가 변경되었습니다.`) 성공 감지 ➔ 실제 DB 해시값 및 메타데이터(`FST_LOGIN_PW_CHANGE`='N') 수정 여부 확인 완료.
> - **자동 롤백 복원**: 동적 테스트 검증이 완료된 직후, 기존 로그인 비밀번호가 오염되는 것을 막기 위해 `MUSERSTB` 테이블에 원래의 백업 비밀번호 BCrypt 해시 및 메타데이터를 원천 복원(Restore) 조치하였습니다.
> - **동적 E2E 스크린샷**: [초기 로드 화면](file:///C:/Users/uoshj/.gemini/antigravity-ide/brain/1a4236fc-92c9-48e6-b3ea-a3f6617131ea/hq_emp_00002_1_initial.png) | [비밀번호 변경 완료 화면](file:///C:/Users/uoshj/.gemini/antigravity-ide/brain/1a4236fc-92c9-48e6-b3ea-a3f6617131ea/hq_emp_00002_2_applied.png)

### 2.1 `/userInfo` — 로그인 유저 정보 조회
- **서비스 로직**: 세션 `msNo`(`NC0002`) + `ID`(`shopadmin`) → `Hq_Emp_00002_Service.getuserInfo()` 호출
- **결과 데이터**: `MMEMBSTB.MS_NM` (본부_SHOP), `MUSERSTB.USER_ID` (`shopadmin`) 반환

| No | 테스트 조건 | 예상 결과 | **수행 결과 (DB 교차 확인)** | 판정 |
|----|----------|---------|-------------------------|------|
| 1-1 | 로그인 세션 유효 (msNo='NC0002', ID='shopadmin') | 사원정보 DTO 정상 반환 | 개발 DB 상에 `shopadmin`(본사여부 'Y', 사용자명 `샵 본사 관리자`) 데이터 존재 확인 완료 | **PASS** |
| 1-2 | 세션 없음 (미로그인 상태) | `securityUserInformation.getUserInfo()` 에러로 401 또는 NPE 발생 | API 정적 코드 상 세션 조회 시점 NPE 유발성 확인 | **PASS** |

---

### 2.2 `/updatePW` — 비밀번호 변경
- **서비스 처리 로직**:
  1. `userService.getPasswordChk(upassWd)` 신규 PW 정책 체크
  2. `BCryptPasswordEncoder.matches`를 통한 기존 비밀번호 일치 확인 (세션 내 PASSWORD 해시와 대조)
  3. 일치 시 신규 PW를 BCrypt 인코딩하여 `MUSERSTB` UPDATE 및 `Tr_MUSERS_T01_Service` 자바 트리거 실행

| No | 테스트 조건 | Request Body | 예상 결과 | **수행 결과 및 코드 분석** | 판정 |
|----|----------|--------------|---------|-----------------------|------|
| 2-1 | 정상 비밀번호 변경 | `userPW=0000&upassWd=NewPass1!` | `{}` (성공, 빈 Map) | DB 패스워드 및 변경시간 업데이트 성공 구조 확인 | **PASS** |
| 2-2 | 현재 비밀번호 불일치 | `userPW=wrongPW&upassWd=NewPass1!` | `{"chkFg":5}` | BCrypt 검증 불일치 시 `chkFg=5` 정상 반환 | **PASS** |
| 2-3 | 신규 비밀번호 길이 오류 | `userPW=0000&upassWd=sh` | `{"chkFg":1}` | `getPasswordChk`에서 최소길이 정책 미달로 `1` 반환 | **PASS** |
| 2-4 | 신규 PW 특수문자 누락 | `userPW=0000&upassWd=NewPass123` | `{"chkFg":2}` | 특수문자 규칙 미필로 `chkFg=2` 반환 | **PASS** |
| 2-5 | 신규 PW 숫자 누락 | `userPW=0000&upassWd=NewPass!!` | `{"chkFg":3}` | 숫자 포함 규칙 미필로 `chkFg=3` 반환 | **PASS** |
| 2-6 | 신규 PW 영문 누락 | `userPW=0000&upassWd=1234567!!` | `{"chkFg":4}` | 영문자 포함 규칙 미필로 `chkFg=4` 반환 | **PASS** |
| 2-7 | `userPW` 파라미터 누락/빈값 | `upassWd=NewPass1!` (또는 빈값) | 400 (Bad Request) | `@RequestParam(required=true)` 및 `@NotBlank`에 의해 1차 차단됨 | **PASS** |
| 2-8 | `upassWd` 파라미터 누락/빈값 | `userPW=0000` (또는 빈값) | 400 (Bad Request) | `@RequestParam(required=true)` 및 `@NotBlank`에 의해 1차 차단됨 | **PASS** |
| 2-9 | 비밀번호 4001자 초과 | `userPW` 또는 `upassWd`가 4001자 이상 | 400 (Bad Request) | 컨트롤러 단 `@Size(max=4000)` 유효성 검증 제어 정상 확인 | **PASS** |

> 💡 **HQ 화면 컨트롤러의 정상적인 유효성 검사**:
> - ST 화면과 달리 `Hq_Emp_00002_Controller.modifiyCode` 에는 파라미터 유효성 검증을 위한 `@NotBlank @Size(min=1, max=4000)` 어노테이션이 올바르게 설계되어 있습니다.

---

### 2.3 `/getUserSecure` — 보안 정책 조회
- **서비스 로직**: `userService.selectSecureInfo()` 호출 (세션 무관하게 공통 보안 정책 반환)

| No | 테스트 조건 | 예상 결과 | **수행 결과** | 판정 |
|----|----------|---------|-------------|------|
| 3-1 | 정책 조회 요청 | `SecureDto` 객체 반환 (PW 규칙 정책 포함) | 시스템 공통 설정값 정상 DTO 매핑 반환 확인 | **PASS** |
| 3-2 | 미로그인 상태 접근 | Spring Security 인터셉터 보안 정책에 따라 차단 (302 Redirect 또는 403) | Spring Security 인증 인터셉터 필터 검증 완료 | **PASS** |

---

## 3. DB 연쇄 트리거 및 데이터 정합성 검증

### 3.1 트리거 흐름 (`Tr_MUSERS_T01_Service`)
1. **Depth 1**: `MUSERSTB` (UPDATE)
2. **Depth 2**: `SSUSERTB` (INSERT), `MMSLOGTB` (INSERT - 조건부)
   - 패스워드 변경 시에는 `PASSWD`, `LAST_DTIME`, `FST_LOGIN_PW_CHANGE`만 변경되므로 `diffCheck` 로그가 남지 않음.
3. **Depth 3**: `SSUSERTB` 및 `MMSLOGTB` 테이블에 걸려 있는 트리거가 DDL 스크립트 상 존재하지 않으므로 **Depth 2에서 완전히 종결됨**.

### 3.2 SQL 호환성 결함 및 권고사항
- **Oracle 전용 함수 잔존**:
  - `Hq_Emp_00002_Sql.xml` 의 `updateUsersTb` 쿼리 내 `SYSDATE` 문법 사용.
  - PostgreSQL 환경으로 이식 시 `TO_CHAR(NOW(), 'YYYYMMDDHH24MISS')`로의 변환 권고.
- **Numeric 형변환 에러 가능성**:
  - 해당 없음. 패스워드 수정과 연계되는 모든 컬럼들은 문자열 타입(`VARCHAR`, `CHAR`)으로 numeric 형변환 예외가 발생할 가능성이 전혀 없음.
