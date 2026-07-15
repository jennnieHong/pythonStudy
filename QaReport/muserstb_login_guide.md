# MUSERSTB 로그인 및 메인 대시보드 진입오류(500) 해결 가이드

사용자 계정으로 로그인 후 메인 대시보드 화면(`/backoffice/view/main`)에 진입할 때 **HTTP 500 (Internal Server Error)** 에러가 발생하는 경우, 데이터베이스 내 사용자 정보와 매장 정보 매핑 누락으로 인해 발생합니다.

---

## 1. 에러 발생 원인

서버 컨텍스트의 페이지 트랜지션 모듈(`WebPageTransition.java`)에서 사용자의 인증 세션 내 세 가지 필수 정보(`systemType`, `chainNo`, `msNo`)를 호출할 때 `.toString()` 처리를 수행합니다.

```java
// WebPageTransition.java
String systemType = securityUserInformation.getUserInfo("systemType").toString();
String chainNo    = securityUserInformation.getUserInfo("chainNo").toString();
String msNo       = securityUserInformation.getUserInfo("msNo").toString();
```

만약 이 세 항목 중 하나라도 데이터베이스 쿼리를 통해 조회되지 않아 `null` 상태가 되면 **`NullPointerException`**이 발생하며 500 오류 페이지가 표시됩니다.

---

## 2. 해결을 위한 데이터베이스 점검 요건 (MUSERSTB & MMEMBSTB)

오류를 해결하기 위해 아래 5가지 체크포인트를 데이터베이스에서 조회하여 조치해야 합니다.

### ① 사용자 계정 활성화 여부 점검
* **테이블**: `hmsfns.MUSERSTB`
* **대상 컬럼**: `ACCT_ENABLE` (Enabled)
* **요건**: `'Y'` 값이어야 로그인이 허용됩니다.

### ② 비밀번호 초기 로그인 변경상태 점검
* **테이블**: `hmsfns.MUSERSTB`
* **대상 컬럼**: `FST_LOGIN_PW_CHANGE`
* **요건**: `'Y'` 값이어야 임시 비밀번호 변경 단계를 건너뛰고 대시보드로 바로 진입합니다.

### ③ 시스템 타입 설정 점검
* **테이블**: `hmsfns.MUSERSTB`
* **대상 컬럼**: `SYSTEM_TYPE`
* **요건**: `null` 값이 아니어야 하며, 본사(`'HQ'`) 또는 매장(`'ST'`) 등 올바른 시스템 권한 구분이 명시되어야 합니다.

### ④ 매장 코드 설정 점검
* **테이블**: `hmsfns.MUSERSTB`
* **대상 컬럼**: `MS_NO`
* **요건**: 사용자가 소속된 매장 코드 정보가 채워져 있어야 합니다 (`null` 불가).

### ⑤ 가맹점 마스터 매핑 여부 점검 (가장 중요)
* **테이블**: `hmsfns.MMEMBSTB` (매장 마스터)
* **요건**: `MUSERSTB.MS_NO`에 기록된 매장코드가 `MMEMBSTB.MS_NO`에 **실제로 존재**해야 합니다.
* **상세**: 사용자의 체인 번호(`CHAIN_NO`)를 로드하기 위해 아래 서브쿼리가 동작합니다.
  ```sql
  SELECT X.CHAIN_NO
    FROM hmsfns.MMEMBSTB X
   WHERE X.MS_NO = MUSERSTB.MS_NO
  ```
  `MUSERSTB`에는 매장코드가 들어가 있지만 `MMEMBSTB` 마스터 테이블에 해당 매장이 등록되어 있지 않다면 `CHAIN_NO`가 `null`이 반환되어 500 에러를 유발합니다.

---

## 3. SQL 조치 예시

해당 사용자의 정보가 올바르게 매핑되어 있는지 확인하고 보정하는 쿼리 샘플입니다.

### 계정 정보 및 매장 매핑 정합성 조회
```sql
SELECT A.USER_ID
     , A.ACCT_ENABLE
     , A.SYSTEM_TYPE
     , A.MS_NO
     , B.CHAIN_NO
  FROM hmsfns.MUSERSTB A
  LEFT OUTER JOIN hmsfns.MMEMBSTB B ON A.MS_NO = B.MS_NO
 WHERE A.USER_ID = 'I000034b';
```
* 위 쿼리를 실행했을 때 `MS_NO` 혹은 `CHAIN_NO`가 `null`로 나온다면 해당 정보를 업데이트해 주어야 합니다.

### 유효하지 않은 매장 코드 보정 예시 (예: MS_NO = 'NC0011')
```sql
-- 1. MUSERSTB의 매장코드 정보를 실제 존재하는 매장으로 변경
UPDATE hmsfns.MUSERSTB 
   SET MS_NO = 'NC0011' 
 WHERE USER_ID = 'I000034b';

-- 2. 해당 매장코드가 MMEMBSTB(매장 마스터)에 없는 상태라면 마스터 정보 추가 또는 매장 테이블 동기화 확인 필요
```
