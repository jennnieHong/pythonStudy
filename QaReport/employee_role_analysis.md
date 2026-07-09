# 사원관리 권한(Role) 시스템 분석 보고서

이 문서는 사원 정보 등록 및 수정 팝업에서 설정하는 권한(Role)이 데이터베이스에 저장되는 방식, 관련 테이블 구성, 그리고 매장 권한 제어 방식에 대한 소스코드 분석 결과를 정리한 보고서입니다.

---

## 1. 권한 시스템 설계 개요
시스템 내에서 사원별 권한(Role)은 사용자 마스터 테이블의 특정 컬럼에 1:1로 직접 저장되지 않는 **'풀어쓰는 방식'**으로 설계되어 있습니다.

* **동작 방식**: 
  1. 사원 등록/수정 팝업에서 특정 **권한 그룹(Role)**을 지정합니다.
  2. 시스템은 해당 권한 그룹에 포함된 모든 **메뉴 번호(MENU_SEQ)** 목록을 조회합니다.
  3. 사원의 사용자 ID와 개별 메뉴 번호들을 1:N 관계로 매핑하여 **사용자별 메뉴 권한 테이블(`USERMLTB`)**에 여러 레코드로 저장(인서트)합니다.

---

## 2. 관련 데이터베이스 테이블 구조

모든 권한 정보는 동일한 스키마(`hmsfns`) 내의 아래 4개 테이블을 통해 관리되고 참조됩니다.

| 테이블명 | 테이블 의미 | 주요 컬럼 | 설명 |
| :--- | :--- | :--- | :--- |
| **`hmsfns.MROLEHTB`** | 권한 마스터 헤더 | `ROLE_CD` (PK)<br>`ROLE_NM`<br>`SYSTEM_TYPE`<br>`CHAIN_NO` | 권한 그룹 자체를 정의하는 마스터 테이블 (본사 권한과 매장 권한 모두 여기서 통합 관리됨) |
| **`hmsfns.MROLEDTB`** | 권한 마스터 상세 | `ROLE_CD` (PK)<br>`MENU_SEQ` (PK) | 특정 권한 그룹(`ROLE_CD`)에 어떤 메뉴 권한들(`MENU_SEQ`)이 매핑되어 있는지 정의하는 상세 테이블 |
| **`hmsfns.USERMLTB`** | 사용자별 메뉴 권한 | `USER_ID` (PK)<br>`MENU_SEQ` (PK)<br>`CREATE_ID`<br>`CREATE_DTIME` | **[최종 저장처]** 특정 사용자가 접근할 수 있는 개별 메뉴 목록을 갖는 실질적인 권한 테이블 |
| **`hmsfns.MUSERSTB`** | 사용자 마스터 | `USER_ID` (PK)<br>`USER_NM`<br>`SYSTEM_TYPE` | 사용자 기본 정보 마스터 테이블 |

---

## 3. 사원 정보 수정 시 처리 프로세스

사원 정보 수정 팝업에서 권한을 변경하여 저장할 때, Java 서비스 레이어와 MyBatis XML 매퍼는 다음과 같이 동작합니다.

### A. Java Service 호출 흐름
[Admin_Emp_00001_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/admin/employee/Admin_Emp_00001_Service.java#L267-L296) 의 `userUpdate` 메서드:
```java
String userRole = (String) commandMap.get("userRole"); // 화면에서 넘겨받은 권한 코드 (ROLE_CD)
if(!"".equals(userRole)) {
    // 1. 기존 권한 데이터 삭제
    Admin_Emp_00001_Mapper.deleteUserMl(commandMap);
    // 2. 신규 권한에 따른 메뉴 맵핑 복사 및 저장
    Admin_Emp_00001_Mapper.updateUserRole(commandMap);
}
```

### B. MyBatis SQL 매핑 쿼리
[Admin_Emp_00001_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/employee/Admin_Emp_00001_Sql.xml) 내의 관련 쿼리:

* **기존 권한 삭제 (`deleteUserMl`)**
  ```sql
  DELETE FROM hmsfns.USERMLTB
   WHERE USER_ID = #{editUserId}
  ```
  
* **새로운 메뉴 권한 등록 (`updateUserRole`)**
  ```sql
  INSERT INTO hmsfns.USERMLTB
  SELECT #{editUserId}
       , B.MENU_SEQ
       , 'N'
       , ''
       , TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS')
       , #{userId}
       , TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS')
       , #{userId}
   FROM hmsfns.MROLEHTB A
      , hmsfns.MROLEDTB B
  WHERE A.ROLE_CD = B.ROLE_CD
    AND A.ROLE_CD = #{userRole} /* 선택된 권한 코드 */
  ```

---

## 4. 매장(Store) 권한 제어 방식 및 필터 규칙

매장 사원의 권한 설정은 각 사원관리 화면의 목적과 접근 범위에 따라 다르게 처리되고 있습니다.

### A. 매장 전용 사원관리 화면 (`st_emp_00001`)
* **결론: 권한 설정 및 변경 불가 (UI 없음)**
* **설명**: 
  * 매장 사용자가 접속하는 화면에서는 권한 수정 오남용을 방지하기 위해 등록 모달([st_emp_00001_M01.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/employee/st_emp_00001/modal/st_emp_00001_M01.jsp)) 및 수정 모달([st_emp_00001_M03.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/employee/st_emp_00001/modal/st_emp_00001_M03.jsp))에 권한 선택 UI(콤보박스)가 아예 존재하지 않습니다.
  * 자바스크립트 파일([st_emp_00001.js](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/employee/st_emp_00001/js/st_emp_00001.js)) 내 저장 및 수정 요청 시에도 `userRole` 파라미터는 전송되지 않습니다.

### B. 본사 사원관리 (`hq_emp_00001`) & 어드민 사원관리 (`admin_emp_00001`) 화면
* **결론: 권한 설정 가능하나, 매장용 권한만 나오도록 시스템 필터 적용**
* **설명**:
  * 본사 및 어드민 사원관리에서는 매장 사원 탭에서 사원 등록/수정 시 권한 콤보박스가 렌더링됩니다.
  * 이때 권한 목록을 조회하는 API에서 **`SYSTEM_TYPE = 'ST'`**인 권한 그룹만 나오도록 강하게 필터링을 걸어 둡니다. 
  * 따라서 매장 사원에게는 `MROLEHTB`에 등록된 권한 그룹 중 매장 전용 권한(예: 매장 관리자, 매장 사용자)만 조회되고 매핑할 수 있습니다.

---

## 5. 권한 그룹 자체의 정의 및 관리 (`Hq_Master_00022`)
* 권한 그룹(`ROLE_CD`) 및 그룹별 허용 메뉴 목록(`MROLEDTB`)은 **"메뉴권한 마스터"** 화면인 **`Hq_Master_00022`**에서 관리합니다.
* 해당 화면의 SQL 매퍼 파일([Hq_Master_00022_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/master/Hq_Master_00022_Sql.xml))을 통해 `MROLEHTB` 테이블에 데이터를 인서트하거나 지우는 등의 관리가 이루어집니다.
