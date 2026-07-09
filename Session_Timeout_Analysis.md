# 📝 백오피스 및 모바일 API 세션 타임아웃 분석 보고서

본 보고서는 프로젝트 내 백오피스(`backoffice`) 및 모바일 API(`mobile-api`) 모듈의 세션 타임아웃 설정 현황, 작동 방식, 그리고 실제 소스 코드 상에서의 세션 활용 여부를 분석한 결과입니다.

---

## 1. 모듈별 세션 설정 및 분석 요약

| 모듈명 | 세션 타임아웃 설정 | 실제 세션 사용 여부 | 인증 및 로그인 유지 방식 |
|---|---|---|---|
| **백오피스 (`backoffice`)** | **30분** (`web.xml` 기준) | **사용 (Active)** ⭕ | **Stateful Session**: 브라우저의 Cookie(`JSESSIONID`)와 Spring Security Context 기반 세션 동기화 |
| **모바일 API (`mobile-api`)** | **10분** (`web.xml` 기준) | **미사용 (Bypass)** ❌ | **Stateless API**: 세션을 생성하지 않으며 로그인 성공 시 반환되는 User Parameter를 매 요청마다 전달 |

---

## 2. 백오피스 (backoffice) 세션 상세 분석

### 2.1 세션 설정 파일 (`web.xml`)
* **경로**: [hyundai-backoffice-webapp/.../WEB-INF/web.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/web.xml#L69-L72)
* **설정 내용**:
  ```xml
  <!-- Session time out setup (unit : minute) -->
  <session-config>
      <session-timeout>30</session-timeout>
  </session-config>
  ```
  * 단위는 **분(Minute)**이며, 마지막 요청 시간으로부터 **30분 동안 추가적인 요청이 없으면 세션이 만료**됩니다.

### 2.2 소스 코드 상의 연동
* **Spring Security 연동**:
  스프링 시큐리티 필터 체인(`springSecurityFilterChain`)이 모든 요청을 가로채 세션 유효성을 체크합니다.
* **로그인 정보 조회 방식**:
  컨트롤러 단에서 사용자 세션 정보를 조회할 때 다음과 같이 공통 시큐리티 모듈을 사용합니다:
  ```java
  // Hq_Vendor_00019_Controller.java L62
  String chainNo = securityUserInformation.getUserInfo("chainNo").toString();
  ```
  이 메서드는 톰캣이 관리하는 `HttpSession`의 `SecurityContext`에서 현재 세션 정보를 파싱하므로, 톰캣 세션 설정(30분)이 정상 적용됩니다.

---

## 3. 모바일 API (mobile-api) 세션 상세 분석

### 3.1 세션 설정 파일 (`web.xml`)
* **경로**: [mobile-api/.../WEB-INF/web.xml](file:///d:/workspace/hmotors/workspace_hms20260326/mobile-api/target/ROOT/WEB-INF/web.xml#L61-L64)
* **설정 내용**:
  ```xml
  <!-- Session time out setup (unit : minute) -->
  <session-config>
      <session-timeout>10</session-timeout>
  </session-config>
  ```

### 3.2 소스 코드 정밀 분석 및 세션 미사용 증명
모바일 API의 소스 코드를 전수 분석한 결과, **세션 객체(`HttpSession`)를 사용하는 로직이 전무**하여 위 10분 설정은 런타임에 아무런 영향을 미치지 않는 **보일러플레이트(잔재) 설정**입니다.

#### ① 로그인 시점 ([LOGIN_Controller.java](file:///d:/workspace/hmotors/workspace_hms20260326/mobile-api/src/main/java/com/hyundai/api/mobile/login/LOGIN_Controller.java))
```java
@RequestMapping(value="/login", produces = "application/json; charset="+Constants.RES_ENCODING)
@ResponseBody
public Map<String, Object> LOGIN( HttpServletRequest request 
                                , HttpServletResponse response
                                , @RequestBody Map<String, Object> Jsonmap ) throws Exception {
    FileLogger filelog = new FileLogger();
    Map<String, Object> responseData = LOGIN_Service.LOGIN(Jsonmap);
    filelog.FileWrite(request, "LOGIN", Jsonmap, responseData);
    
    return responseData;
}
```
* 로그인 성공 시 `request.getSession()` 등을 호출하여 세션을 생성하거나 쿠키를 발행하는 동작이 없으며, 단순히 로그인 성공 결과(`RESULT_CD: "0000"`)와 사용자 권한 맵(`resultMap`)을 응답 바디로 전송하고 끝납니다.

#### ② 서비스 비즈니스 요청 시점 ([COMPANY_Controller.java](file:///d:/workspace/hmotors/workspace_hms20260326/mobile-api/src/main/java/com/hyundai/api/mobile/company/COMPANY_Controller.java))
```java
@RequestMapping(value="/company", produces = "application/json; charset="+Constants.RES_ENCODING)
@ResponseBody
public Map<String,Object> COMPANY ( HttpServletRequest request 
                                  , HttpServletResponse response
                                  , @RequestBody Map<String, Object> Jsonmap ) throws Exception {
    FileLogger fileLog = new FileLogger();
    Map<String,Object> responseData = COMPANY_Service.COMPANY(Jsonmap);
    fileLog.FileWrite(request, "COMPANY", Jsonmap, responseData);
    
    return responseData;
}
```
* `/api/mobile/company` 등 일반 비즈니스 요청 시에도 스프링 인터셉터나 필터가 동작하여 세션을 검증하는 로직이 없으며, 전달된 `Jsonmap` 파라미터만 가지고 비즈니스 로직을 처리하는 **Stateless(무상태) 구조**입니다.

---

## 4. 실무 가이드 및 권고사항

### 4.1 백오피스 세션 연동
* **정상 동작**: 백오피스는 현재 설정된 30분 세션 타임아웃을 기반으로 정상 작동 중입니다.
* **추가 조치**: 만약 세션 만료 경고(예: 만료 5분 전 연장 팝업)가 UI 상에 필요하다면 프론트엔드 공통 JS에 타이머 구현을 추가해야 합니다.

### 4.2 모바일 API 세션 구조 개선 제안
모바일 기기는 네트워크 유실 및 IP 변경이 잦으므로 톰캣 세션을 사용하지 않는 현재의 **무상태(Stateless) 아키텍처는 타당한 선택**입니다. 
다만, 보안을 보완하기 위해 다음과 같은 개선을 권장합니다.

1. **Token 기반 인증 도입 권장 (JWT / OAuth2)**:
   * 현재처럼 단순히 `USER_ID`, `MS_NO` 파라미터를 요청 바디에 넣어 통신하는 방식은 파라미터 위변조 및 도청에 매우 취약합니다.
   * 로그인 성공 시 암호화된 짧은 수명의 **Access Token**과 긴 수명의 **Refresh Token**을 발급하여 보안성과 사용자 편의성(자동 로그인)을 동시에 챙기는 방향으로 리팩토링할 것을 권장합니다.
2. **Boilerplate 설정 정리**:
   * 혼선을 방지하기 위해 `mobile-api` 모듈의 `web.xml` 내 `<session-config>` 영역은 제거하거나 관련 주석을 달아 무의미한 설정임을 가이드하는 것이 좋습니다.
