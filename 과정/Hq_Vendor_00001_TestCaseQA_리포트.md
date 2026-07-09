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

> 💡 **참고**: 테스트 진행 시 shopadmin 계정으로 로그인하여 화면 내 구매의뢰 내역(Request Header) 및 상품 상세(Request Detail) 조회를 검증했습니다.

---

## 3. 관련 테이블 및 프로시저/트리거 매핑 내역

Hq_Vendor_00001 모듈에서 CUD 작업이 발생하는 테이블과 DDL상의 실행조건(트리거) 분석 결과입니다.

| 발생 로직 (API) | 조작 타입 | 연관 테이블 | DDL 트리거 유무 | 비고 |
|-----------------|-----------|-------------|-----------------|------|
| `saveRequest`, `deleteRequestHeader` 등 | INSERT/UPDATE/DELETE | `OBREQHTB` | **없음 (False)** | 트리거 연쇄 작용 없음 |
| `addRequestGoods`, `deleteRequestGoods` 등 | MERGE/INSERT/DELETE | `OBREQDTB` | **없음 (False)** | 트리거 연쇄 작용 없음 |

> ✅ **분석 결과**: 해당 화면이 조작하는 핵심 테이블(`OBREQHTB`, `OBREQDTB`)에는 DDL 스크립트(`HMSFNB.sql`) 상 **DB 트리거가 존재하지 않습니다.** 따라서 Depth 1, 2, 3으로 이어지는 트리거 연쇄작용(Cascading)이나 프로시저 호출 확인 대상이 아닙니다.

---

## 4. 정적 코드 분석 결과 (트리거/고아 및 문법 호환성)

### 4.1 트리거/고아 코드 결함 (Bypass)
해당 화면은 트리거를 사용하지 않는 테이블을 다루므로, Java Service 계층에서 수동으로 `TriggerUtil` 등을 호출해야 하는 부담이 없습니다. 고아 코드도 발견되지 않았습니다.

### 4.2 SQL Mapper 호환성 결함 (Oracle -> PostgreSQL)
`Hq_Vendor_00001_Sql.xml` 분석 결과, PostgreSQL 환경에서 Runtime Exception을 유발하는 치명적인 타입 캐스팅 오류와 ANSI 비표준 문법이 발견되었습니다.

**[수정 완료] PSQLException 오류 조치**
* **발생 메서드**: `getReqGoodsList`
* **오류 내역**: `org.postgresql.util.PSQLException: ERROR: operator does not exist: text - integer`
* **원인**: `LPAD(MAX(ESTIM_SEQ) - 1, 10, '0') AS ESTIM_SEQ` 구문에서 문자열 타입(text)에 숫자 1(integer)을 빼는 산술 연산을 시도하여 발생했습니다. (Oracle에서는 암시적 형변환이 되나 PostgreSQL에서는 엄격한 타입 검사로 인해 오류 발생)
* **조치 내용**: 
  ```sql
  -- 수정 전
  LPAD(MAX(ESTIM_SEQ) - 1, 10, '0') AS ESTIM_SEQ
  
  -- 수정 후
  LPAD(CAST(COALESCE(MAX(CAST(ESTIM_SEQ AS INTEGER)), 0) - 1 AS TEXT), 10, '0') AS ESTIM_SEQ
  ```
  명시적인 `CAST AS INTEGER` 및 `CAST AS TEXT`를 추가하여 소스 파일 업데이트를 완료했습니다.

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` |
| 로그인 | 성공 (shopadmin) |
| 화면 경로 | `/backoffice/view/main/hq/vendor/hq_vendor_00001` |
| 화면 로딩 | 정상 |

### 5.2 화면 구성 확인

- **상단 패널**: 조회 조건 (매장코드, 의뢰번호, 일자 등)
- **메인 좌측 그리드**: 구매의뢰 전표 목록 (Header)
- **메인 우측 패널**: 구매의뢰 마스터 등록 폼 (매장선택, 의뢰명칭, 계획일자) 및 저장/초기화 버튼
- **하단 좌측 그리드**: 상품 검색 및 추가 리스트
- **하단 우측 그리드**: 선택된 구매의뢰 상세 품목 (Detail)

### 5.3 기능별 테스트 결과

| 기능 | 엔드포인트명 | 코드 구현 | 화면 UI | 판정 |
|------|-----------|---------|---------|------|
| 전표 조회 | `/getReqHdList` | 구현 완료 | 메인 그리드 표시 | **PASS** |
| 전표 상세 조회 | `/getReqGoodsList` | **수정 완료 (500 에러 해결)** | 우측 및 하단 그리드 바인딩 | **PASS** |
| 마스터 등록(초기화/저장) | `/saveRequest` | 구현 완료 | 우측 입력 폼 | **PASS** |
| 상품 조회 | `/getNotReqGoodsList` | 구현 완료 | 하단 좌측 그리드 | **PASS** |
| 상품 품목 추가 | `/addRequestGoods` | 구현 완료 | 수량 입력 후 추가 | **PASS** |
| 전표 삭제/확정 | `/deleteRequest...` | 구현 완료 | 삭제 버튼 작동 | **PASS** |

---

## 6. SQL Mapper 검토 사항
### 6.1 Oracle (+) 외부조인 잔존 확인

| 쿼리 ID | Oracle(+) 사용 여부 | 영향 |
|---------|-------------------|------|
| `getReqGoodsList` | 부분 사용 (`TE.ESTIM_GOODS_CD(+)`, `NM.NM_CD(+)`) | EPAS 환경에서 임시 호환되나 표준화 필요 |
| `getNotReqGoodsList` | 부분 사용 (`NM.NM_CD(+)`) | EPAS 환경에서 임시 호환되나 표준화 필요 |

> ⚠️ **현재 EPAS 환경에서는 정상 동작하나, 향후 순수 PostgreSQL 전환을 대비해 ANSI `LEFT JOIN`으로 변환이 권고됩니다.**

---

## 7. 검증 항목 체크리스트

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 어노테이션 | ✅ 정상 | - |
| Mapper 메서드 일치 여부 | ✅ 정상 | Interface와 XML 일치 |
| 타입 캐스팅 에러 수정 적용 | ✅ 정상 | `getReqGoodsList` 내 `ESTIM_SEQ` 텍스트-숫자 연산 수정 완 |
| DB 트리거 연쇄작용 유무 | ✅ 정상 | 해당 없음 (`OBREQHTB`, `OBREQDTB`에 트리거 없음) |
| `SYSDATE` 구문 호환 여부 | ⚠️ Info | EPAS 호환으로 정상 동작 (`NOW()` 권장) |

---

## 8. 발견된 이슈 및 권고사항

### 🔴 Critical (즉시 처리 필요)
- 없음 (텍스트-숫자 연산 에러 기 조치 완료)

### 🟡 Warning (마이그레이션 후 처리 필요)
1. **Oracle(+) 외부조인 다수 잔존** (`getReqGoodsList`, `getNotReqGoodsList`)  
   👉 PostgreSQL 환원 시 `LEFT OUTER JOIN` 구문으로 교체 권장.
2. **`SYSDATE` 무분별 사용** (INSERT/UPDATE 구문)  
   👉 데이터 일관성을 위해 `NOW()` 또는 `CURRENT_TIMESTAMP`로 일괄 치환 권장.

---

## 9. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 | ✅ PASS |
| 전표 목록 및 상세 조회 | ✅ PASS (SQL 에러 조치 후) |
| 마스터 INSERT/UPDATE 로직 | ✅ PASS |
| 품목 추가(MERGE) 로직 | ✅ PASS |
| 트리거/프로시저 오류 유무 | ✅ PASS (해당 로직 없음) |
| **종합** | **✅ PASS** |

---
*본 리포트는 코드베이스 정적 분석 + 브라우저 E2E 테스트 기반으로 작성되었습니다.*
