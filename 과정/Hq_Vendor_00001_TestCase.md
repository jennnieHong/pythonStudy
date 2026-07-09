# Hq_Vendor_00001 단위테스트 및 마이그레이션 QA 리포트

## 1. 테스트 개요

| 항목 | 내용 |
|------|------|
| 테스트 일자 | 2026-06-02 |
| 대상 화면 | hq_vendor_00001 (구매의뢰요청관리) |
| 담당자 | AI Assistant (Antigravity) |
| 마이그레이션 환경 | Oracle -> PostgreSQL (EPAS) |
| 테스트 목적 | 화면 정상 로딩, CUD 기능 검증, Oracle 종속 구문 및 트리거 로직 마이그레이션 점검 |

---

## 2. 권한 및 계정 정보 검증

`Backoffice_Screen_TestAccount_v2.xlsx` 매트릭스 검증 완료.

| 시스템 | 분류 | 화면 ID | 계정명 | 비밀번호 | 권한 등급 |
|--------|------|---------|--------|----------|-----------|
| 본사 | POS/구매 | hq_vendor_00001 | shopadmin | 0000 | ROLE_USER |

---

## 3. 관련 테이블 및 프로시저/트리거 매핑 내역

| 발생 로직 (API) | 조작 타입 | 연관 테이블 | DDL 트리거 유무 | 비고 |
|-----------------|-----------|-------------|-----------------|------|
| `saveRequest`, `deleteRequestHeader` 등 | INSERT/UPDATE/DELETE | `OBREQHTB` | **없음 (False)** | 트리거 연쇄 작용 없음 |
| `addRequestGoods`, `deleteRequestGoods` 등 | MERGE/INSERT/DELETE | `OBREQDTB` | **없음 (False)** | 트리거 연쇄 작용 없음 |

> ✅ **분석 결과**: `OBREQHTB`, `OBREQDTB` 테이블에는 트리거가 없습니다. Depth 1, 2, 3 트리거 추적 대상이 아닙니다.

---

## 4. 정적 코드 분석 결과 (트리거/고아 및 문법 호환성)

### 4.1 SQL Mapper 호환성 결함 (Oracle -> PostgreSQL)
`Hq_Vendor_00001_Sql.xml` 및 `St_Vendor_00001_Sql.xml` 공통 분석 결과, PostgreSQL 환경에서 Runtime Exception을 유발하는 다수의 타입 캐스팅 오류를 발견 및 수정했습니다.

**[수정 완료 1] 텍스트-숫자 연산 (text - integer) PSQLException**
* **발생 메서드**: `getReqGoodsList`
* **오류 내역**: `ERROR: operator does not exist: text - integer` (Oracle 자동형변환 실패)
* **조치 내용**: 
  ```sql
  -- 수정 후
  LPAD(CAST(COALESCE(MAX(CAST(ESTIM_SEQ AS INTEGER)), 0) - 1 AS TEXT), 10, '0') AS ESTIM_SEQ
  ```

**[수정 완료 2] 수량 및 단가 산술 연산 (character varying * double) PSQLException**
* **발생 메서드**: `addRequestGoods` (상품 추가 시)
* **오류 내역**: `ERROR: operator does not exist: character varying * double precision`
* **조치 내용**: 
  ```sql
  -- 수정 후
  DT.PURCH_AMT  = CAST(#{requestQty} AS NUMERIC) * CAST(#{price} AS NUMERIC),
  ```

**[수정 완료 3] 전표 복사(채번) 시 산술 연산 (text + integer) PSQLException**
* **발생 메서드**: `getNewReqNo` ('복사' 버튼 클릭 시 채번 로직)
* **오류 내역**: `ERROR: operator does not exist: text + integer`
* **원인**: `SUBSTR(PURCH_REQ_NO, 11, 2) + 1` 구문 오류
* **조치 내용**: 
  ```sql
  -- 수정 후
  NVL(LPAD(CAST(MAX(CAST(SUBSTR(PURCH_REQ_NO, 11, 2) AS INTEGER))+1 AS TEXT), '2', '0'), '01')
  ```

### 4.2 자바 백엔드 시스템 결함 (GlobalExceptionHandler)
**[수정 완료] StringIndexOutOfBoundsException 조치**
* **발생 위치**: `GlobalExceptionHandler.java:247`
* **오류 내역**: 에러 메시지가 2000바이트 이하일 때 `.substring(0, 2000)`을 호출하여, 최초 발생한 SQL 에러를 덮어쓰고 서버 에러 팝업 렌더링을 완전히 무너뜨리는 버그 발견.
* **조치 내용**: 삼항 연산자를 이용해 문자열 길이에 따른 안전한 `substring` 사용하도록 자바 소스 파일 공통 예외 처리 모듈 패치 완료. (`errorTrace.length() > 2000 ? errorTrace.substring(0, 2000) : errorTrace`)

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황
| 항목 | 결과 |
|------|------|
| 화면 로딩 | 정상 |
| 로그인 | 정상 (shopadmin) |

### 5.2 기능별 E2E 테스트 결과
| 기능 | 엔드포인트명 | 코드 구현 | 화면 UI | 판정 |
|------|-----------|---------|---------|------|
| 전표 목록 조회 | `/getReqHdList` | 구현 완료 | 메인 그리드 | **PASS** |
| 전표 상세 로드 | `/getReqGoodsList` | **500 에러 해결** | 우측/하단 | **PASS** |
| 마스터 추가/저장 | `/saveRequest` | 구현 완료 | 입력 폼 | **PASS** |
| 상품 품목 추가 | `/addRequestGoods` | **500 에러 해결** | 수량 입력 | **PASS** |
| 전표 복사 | `/copyRequest` | **500 에러 해결** | 복사 버튼 | **PASS** |
| 전표 확정/삭제 | `/confirmRequest...` | 구현 완료 | 확정 버튼 | **PASS** |

---

## 6. SQL Mapper 검토 사항
* **Oracle(+) 외부조인 다수 잔존** (`getReqGoodsList`, `getNotReqGoodsList`)
  👉 향후 순수 PostgreSQL 전환 대비 ANSI `LEFT JOIN`으로 교체 권장.
* **SYSDATE 무분별 사용** 
  👉 `NOW()` 또는 `CURRENT_TIMESTAMP`로 일괄 치환 권장.

---

## 7. 종합 판정
| 구분 | 결과 |
|------|------|
| DB 트리거/고아 | ✅ PASS (해당 없음) |
| SQL 호환성 에러 | ✅ PASS (3건의 PSQLException 조치 완료) |
| E2E CRUD 작동 | ✅ PASS (조회, 추가, 복사, 확정 등 500에러 소거) |
| 시스템 예외 모듈 | ✅ PASS (GlobalExceptionHandler 버그 픽스) |
| **최종 상태** | **✅ 기능 검증 및 마이그레이션 결함 조치 완료** |
