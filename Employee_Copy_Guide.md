# 백오피스(BackOffice) 사원 계정 복사 및 권한 설정 가이드

본 문서는 백오피스 시스템 내에서 기존 사원 계정(예: `admin2`, `fnbcafe`)의 권한과 정보를 기반으로 복사 계정을 생성하고, 로그인 오류(500 에러) 없이 정상적으로 작동시키기 위한 데이터베이스(DB) 작업 프로세스를 정리한 가이드입니다.

---

## 1. 500 에러 발생 원인 분석
백오피스 메인 화면(`/backoffice/view/main`)에 진입 시 500 에러(NullPointerException)가 발생했던 주요 원인은 **존재하지 않는 가상의 매장 코드(예: `NC0001`)를 사용했기 때문**입니다.

### [원인 흐름]
1. `MUSERSTB`(사용자 마스터) 테이블은 **매장 코드(`MS_NO`)**와 **사원 ID(`EMP_ID`)**의 **복합 유니크 제약조건(Index: `musersx1`)**을 가지고 있습니다.
2. 단순히 동일 매장 내 중복을 피하기 위해 임의의 가상 매장 코드(`NC0001`)를 부여하여 계정을 생성할 경우, `MUSERSTB` 인서트는 성공합니다.
3. 하지만, 사용자가 로그인할 때 Spring Security 인증 과정에서 `UserAuth_Sql.xml`의 `selectUserInfo` 쿼리가 실행됩니다. 이 쿼리는 로그인 유저의 `MS_NO`를 기준으로 `hmsfns.MMEMBSTB`(매장 테이블)과 아우터 조인하여 **체인 번호(`CHAIN_NO`)**, **체인명(`CHAIN_NM`)**, **본부 소속 여부(`CHAIN_HQ_YN`)** 등의 유저 세션 정보를 조회합니다.
4. `MMEMBSTB` 테이블에 `NC0001` 매장이 등록되어 있지 않으므로, 세션 객체(`CustomUserDetails`) 내의 매장/체인 관련 정보들이 모두 `null`로 세팅됩니다.
5. 이후 메인 화면 및 공통 모듈에서 `SecurityUserInformation.getUserInfo("chainNo").toString()`과 같이 세션 정보를 꺼내어 사용할 때 **`NullPointerException`**이 발생하며 화면이 멈추고 500 에러를 반환하게 됩니다.

---

## 2. 올바른 사원 계정 복사 및 생성 프로세스

안전하게 사원 계정을 복사하기 위해서는 **원본 계정의 소속 매장 코드(`MS_NO`)를 그대로 유지**하되, 해당 매장 내에서 **중복되지 않는 고유한 사원 ID(`EMP_ID`)**를 가산하여 부여해야 합니다.

### Step 1. 원본 사용자의 정보 및 매장 코드 확인
먼저 복사할 원본 사용자 계정의 매장 코드를 조회합니다.
```sql
SELECT USER_ID, MS_NO, PASSWD, USER_TYPE, ACCT_ROLE, SYSTEM_TYPE 
FROM hmsfns.MUSERSTB 
WHERE USER_ID = 'fnbcafe'; -- 원본 ID
```
* 예: `fnbcafe` 계정의 실제 소속 매장은 `NC0007`(CAFE) 임을 확인.

### Step 2. 소속 매장의 현재 최대 사원 ID(EMP_ID) 조회
`EMP_ID`는 4자리 문자열(`varchar(4)`) 형식입니다. 동일 매장(`MS_NO = 'NC0007'`) 내의 유니크 제약조건을 피하기 위해, 현재 해당 매장에 소속된 사원들의 `EMP_ID` 중 숫자형 값의 최대값을 구합니다.
> [!IMPORTANT]
> `admin2` 등 일부 시스템 관리자 계정은 `EMP_ID`에 `9999`와 같은 임의 더미 값이 지정되어 있을 수 있습니다. 최대값을 조회할 때 이러한 더미 값은 반드시 제외해 주어야 자릿수 초과(`10000`) 에러를 방지할 수 있습니다.

```sql
SELECT MAX(TO_NUMBER(EMP_ID)) 
FROM hmsfns.MUSERSTB 
WHERE MS_NO = 'NC0007'                  -- 원본 매장 코드
  AND EMP_ID ~ '^[0-9]+$'               -- 숫자 형식인 경우만
  AND EMP_ID != '9999';                 -- 더미 관리자 사번 제외
```
* 조회 결과 최대값이 `0067`인 경우, 신규 생성할 계정들은 `0068`부터 순차적으로 부여합니다.

### Step 3. 신규 사용자 계정 등록 (MUSERSTB)
확인된 정보와 순차 가산한 `EMP_ID`를 이용하여 신규 사용자를 추가합니다.
> [!TIP]
> **`FST_LOGIN_PW_CHANGE`** 컬럼은 최초 로그인 시 비밀번호 변경 여부를 판단합니다. 이 값이 `'N'`일 경우 로그인하자마자 비밀번호 재설정 모달 팝업이 강제로 표시되므로, 테스트 편의를 위해 이 값을 **`'Y'`**(비밀번호 이미 변경 완료 상태)로 입력합니다.

```sql
INSERT INTO hmsfns.MUSERSTB (
    USER_ID, PASSWD, USER_NM, USER_TYPE, MS_NO, EMP_ID, EMP_NO, ACCT_ROLE, SYSTEM_TYPE,
    ACCT_ENABLE, ACCT_LOCK, AUTH_FAILURE_CNT, FST_LOGIN_PW_CHANGE, CREATE_ID, LAST_ID
) VALUES (
    'fnbcafe2',                          -- 신규 ID
    '[원본비밀번호해시값]',              -- 원본 패스워드 복사
    '카페 매니저_2',                     -- 사용자명
    'SHOP',                              -- 원본 USER_TYPE
    'NC0007',                            -- 원본 실제 매장 코드
    '0068',                              -- 가산된 고유 EMP_ID (4자리 포맷)
    'CAF02',                             -- EMP_NO
    'fnbcafe',                           -- ACCT_ROLE
    'S',                                 -- SYSTEM_TYPE
    'Y', 'N', 0, 'Y', 'admin2', 'admin2' -- 네번째 값인 FST_LOGIN_PW_CHANGE를 'Y'로 설정하여 팝업 차단
);
```

### Step 4. 화면 및 메뉴 권한 복사 (USERMLTB)
원본 사용자가 가진 모든 메뉴 권한(`USERMLTB`)을 그대로 복사하여 신규 계정에 매핑합니다.
```sql
INSERT INTO hmsfns.USERMLTB (USER_ID, MENU_SEQ, FAVORITES_YN, EVENT_ROLE, CREATE_ID, LAST_ID)
SELECT 
    'fnbcafe2' AS USER_ID,               -- 신규 ID
    MENU_SEQ, 
    FAVORITES_YN, 
    EVENT_ROLE, 
    'admin2', 
    'admin2'
FROM hmsfns.USERMLTB
WHERE USER_ID = 'fnbcafe';               -- 원본 ID
```

### Step 5. 최종 접속 메뉴 정보 동기화 (TB_USER_LAST_MENU)
메인 화면 진입 시 마지막으로 접근한 메뉴 정보가 세션 구성에 사용되므로, 이 데이터도 복사해 둡니다.
```sql
INSERT INTO hmsfns.TB_USER_LAST_MENU (USER_ID, MENU_SEQ, LAST_ID)
SELECT 
    'fnbcafe2' AS USER_ID,               -- 신규 ID
    MENU_SEQ, 
    'admin2'
FROM hmsfns.TB_USER_LAST_MENU
WHERE USER_ID = 'fnbcafe';               -- 원본 ID
```

---

## 3. Python 자동화 스크립트 예시 (참고)
수동 쿼리 작업이 번거로울 경우 아래와 같은 Python 스크립트를 사용하여 대량의 테스트용 다중 아이디(`admin3`~`admin10`, `fnbcafe2`~`fnbcafe10`)를 일괄 생성 및 동기화할 수 있습니다.

```python
import psycopg2

conn_params = {
    "host": "192.168.10.206",
    "port": 5432,
    "database": "edb",
    "user": "hmsfns_was",
    "password": "astems3!"
}

def copy_permissions(source_user, target_prefix, start_num, end_num, emp_prefix):
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    target_users = [f"{target_prefix}{i}" for i in range(start_num, end_num + 1)]
    
    try:
        # 1. 원본 유저 정보 조회
        cursor.execute("SELECT passwd, user_nm, user_type, acct_role, system_type, ms_no FROM hmsfns.MUSERSTB WHERE USER_ID = %s", (source_user,))
        res = cursor.fetchone()
        if not res:
            print(f"Source user '{source_user}' not found.")
            return
        passwd, user_nm, user_type, acct_role, system_type, source_ms_no = res

        # 2. 원본 권한 조회
        cursor.execute("SELECT menu_seq, favorites_yn, event_role FROM hmsfns.USERMLTB WHERE USER_ID = %s", (source_user,))
        permissions = cursor.fetchall()

        # 3. 기존 타겟 데이터 초기화 (재실행 시 꼬임 방지)
        for target in target_users:
            cursor.execute("DELETE FROM hmsfns.USERMLTB WHERE USER_ID = %s", (target,))
            cursor.execute("DELETE FROM hmsfns.TB_USER_LAST_MENU WHERE USER_ID = %s", (target,))
            cursor.execute("DELETE FROM hmsfns.MUSERSTB WHERE USER_ID = %s", (target,))

        # 4. 해당 매장 내 최대 EMP_ID 구하기 (9999 더미 제외)
        cursor.execute("SELECT MAX(TO_NUMBER(EMP_ID)) FROM hmsfns.MUSERSTB WHERE MS_NO = %s AND EMP_ID ~ '^[0-9]+$' AND EMP_ID != '9999'", (source_ms_no,))
        max_emp_val = cursor.fetchone()[0]
        current_max_id = int(max_emp_val) if max_emp_val else 0

        # 5. 순차 등록
        for target in target_users:
            current_max_id += 1
            new_emp_id = f"{current_max_id:04d}"
            
            # MUSERSTB 등록
            cursor.execute("""
                INSERT INTO hmsfns.MUSERSTB (
                    USER_ID, PASSWD, USER_NM, USER_TYPE, MS_NO, EMP_ID, EMP_NO, ACCT_ROLE, SYSTEM_TYPE,
                    ACCT_ENABLE, ACCT_LOCK, AUTH_FAILURE_CNT, FST_LOGIN_PW_CHANGE, CREATE_ID, LAST_ID
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Y', 'N', 0, 'Y', 'admin2', 'admin2')
            """, (target, passwd, f"{user_nm}_{target[-1] if target[-1] != '0' else '10'}", user_type, source_ms_no, new_emp_id, f"{emp_prefix}{target[-2:] if target[-1]=='0' else '0'+target[-1]}", acct_role, system_type))
            
            # 권한 복사
            for perm in permissions:
                cursor.execute("""
                    INSERT INTO hmsfns.USERMLTB (USER_ID, MENU_SEQ, FAVORITES_YN, EVENT_ROLE, CREATE_ID, LAST_ID)
                    VALUES (%s, %s, %s, %s, 'admin2', 'admin2')
                """, (target, perm[0], perm[1], perm[2]))

        conn.commit()
        print(f"[SUCCESS] Copied {source_user} to {target_prefix} {start_num}~{end_num}")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()
```
