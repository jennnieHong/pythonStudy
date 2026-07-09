# Tibero_Connection_Test — Tibero DB 커넥션 테스트 단위 테스트케이스

> **화면**: 내부 유틸리티 — Tibero DB 연결 상태 확인용  
> **URL Prefix**: `GET or POST /backoffice/tibero`  
> **@Transactional**: `transactionManager = "transactionManager-Tibero"` (전용 TM)  
> **특이사항**: 세션 인증 불필요 여부 확인 필요 — `@ServiceLog` 없음, `SecurityUserInformation` 없음 ★

---

## 구조 분석

```java
// 컨트롤러 — GET/POST 구분 없음 (@RequestMapping만)
@RequestMapping(value = "/backoffice/tibero/connection")
public void testTiberoConnection(...) {
    String testResult = tibero_Connection_Test_Service.selectFromDualTibero();
    log.info("Tibero database connection test result - " + testResult);
    // ★ 응답 body 없음 — void 반환, response에 아무것도 쓰지 않음
}

// 서비스 — 예외 catch 후 실패 메시지 반환 (예외 미전파)
try {
    String connResult = tibero_Connection_Test_Mapper.selectFromDualTibero(); // SELECT 1 FROM DUAL
    sResult = connResult;
} catch (Exception e) {
    sResult = "Tibero database connection failed. " + e.getMessage(); // 예외 삼킴 ★
}
```

---

## 엔드포인트 목록 (1개)

| # | URL | 기능 | 요청 방식 | 반환 | Type |
|---|-----|------|----------|------|------|
| 1 | `/connection` | Tibero DUAL SELECT 커넥션 테스트 | GET/POST (제한 없음) | `void` (log만) | SELECT |

---

## 1. `/connection` — DB 커넥션 테스트

| No | 조건 | 예상값 |
|----|------|-------|
| 1-1 | Tibero DB 정상 | 응답 body 없음 (204), 로그: `"Tibero database connection test result - 1"` |
| 1-2 | Tibero DB 다운 | 응답 body 없음 (204), 로그: `"Tibero database connection test result - Tibero database connection failed. ..."` |
| 1-3 | 세션 없음 (비인증) | 인증 필터 적용 여부에 따라 200 또는 302(로그인 리다이렉트) ★ |
| 1-4 | GET 요청 | `@RequestMapping` method 미지정 → GET/POST 모두 허용 ★ |

---

## PowerShell 테스트 명령

```powershell
# 인증 없이 직접 접근 (세션 불필요 여부 확인)
Invoke-RestMethod -Uri "http://localhost:18080/backoffice/tibero/connection" -Method GET
# 예상: 204 (응답 body 없음) 또는 302 (인증 리다이렉트)

# 인증 후 접근
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=fnbadmin&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

Invoke-WebRequest -Uri "http://localhost:18080/backoffice/tibero/connection" `
  -Method GET -WebSession $session
# 예상: 200 (body 없음), 서버 로그에서 결과 확인
```

---

## 주요 검증 포인트

```
□ 응답 body 없음 (void) — 클라이언트에서 결과 확인 불가, 로그로만 확인 ★
□ 예외 catch 후 삼킴 — DB 연결 실패 시 500 아닌 200 반환 → 모니터링 누락 ★★
□ @RequestMapping method 미지정 → GET/POST 모두 허용 — 운영 환경 보안 주의 ★
□ 인증 필터 적용 여부 — 비인증 접근 가능 시 DB 정보 노출 위험 ★★
□ transactionManager-Tibero — Tibero 전용 TM 사용 (PostgreSQL TM 아님) 확인
□ @ServiceLog 없음 — 감사 로그 미기록
□ SELECT 1 FROM DUAL — Oracle/Tibero 문법 (PostgreSQL 이관 시 SELECT 1로 변경 필요)
```
