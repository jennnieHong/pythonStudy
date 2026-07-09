# QA Report: Hq_Esti_00008 계약이월

**작성일**: 2026-07-03  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 견적관리 > 견적관리 > 계약이월 (hq_esti_00008)  
**테스트 환경**: localhost:8080 (로컬 개발 서버)  
**접속ID/PW**: fnbadmin / 0000 (본사 관리자 계정)  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/hq/estimate/Hq_Esti_00008_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/hq/estimate/Hq_Esti_00008_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/hq/estimate/Hq_Esti_00008_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../sqlmapper/estimate/Hq_Esti_00008_Sql.xml` |
| 트리거 서비스 (Depth 2) | `hyundai-api/.../service/trigger/Tr_TESFRH_T01_Service.java` |
| 트리거 서비스 (Depth 2/3) | `hyundai-api/.../service/trigger/Tr_TPRICE_T01_Service.java` |
| 트리거 서비스 (Depth 3) | `hyundai-api/.../service/trigger/Tr_MPRICE_T01_Service.java` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/estimate/hq_esti_00008/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
|-----------|------|------|------------|
| `/search` | POST | 계약이월 대상 견적 목록 조회 | SELECT |
| `/extendDate` | POST | 선택된 견적 계약 기간 연장 및 이월 처리 | INSERT / UPDATE |

---

## 3. 서비스 로직 분석 (코드베이스 변환 검증)

### 3.1 계약이월 조회 흐름 (`/search`)
1. Controller에서 사용자 세션의 `chainNo` 정보를 수집하여 `Hq_Esti_00008_Service.getList` 호출.
2. Mapper를 통해 `TESVDUTB`, `TGOODSTB`, `TVNDRMTB`, `TESFRHTB` 테이블들을 조인하여 계약 적용이 완료되었으나(`ESTIM_PRC_APPLY_YN = 'Y'`, `ESTIM_PROC_FG = '1'`) 이월되지 않은 견적 목록 조회.

### 3.2 계약이월 처리 흐름 (`/extendDate`)
```
[Controller] extendDate (JSON 데이터 수신)
  └─ [Service] extendDate
       ├─ [Loop: Selected Items]
       │    ├─ insertExtendDate(TPRICETB)         ← Depth 1: 신규 단가 데이터 생성
       │    ├─ insertExtendDateHistory(TESHISTB)  ← 이월 히스토리 생성
       │    └─ tr_TPRICE_T01_Service.processTrigger("A") ← Depth 2: 단가 트리거 호출
       └─ updateHeader(TESFRHTB)                  ← Depth 1: 기존 견적종료일 연장 업데이트
            └─ tr_TESFRH_T01_Service.processTrigger("U") ← Depth 2: 견적헤더 트리거 호출
```

---

## 4. DB 트리거 → 코드베이스 연쇄 분석 (Depth 3 Cascading)

Legacy Oracle 트리거가 Java 코드베이스 서비스로 성공적으로 이식되었으며, 계약이월 실행 시 다음과 같이 연쇄 동작합니다.

### 4.1 Depth 1: 견적 연장 처리
- `Hq_Esti_00008_Service.extendDate`가 실행되어 `TPRICETB`에 신규 단가 데이터를 추가하고, `TESFRHTB`의 적용기간을 수정합니다.

### 4.2 Depth 2: 단가 및 헤더 트리거 동작
- **Tr_TESFRH_T01_Service (헤더 수정)**:
  - `estimProcFg`가 `'1'`(확정)인 상태에서 적용기간이 수정되면 실행되어 `TPRICETB` 및 `TESHISTB`에 변경 내역을 업데이트/인서트합니다.
- **Tr_TPRICE_T01_Service (단가 변경)**:
  - 단가(`TPRICETB`)가 인서트/업데이트/삭제되면 실행되어 변경 전후 상태를 `TPRILGTB` 로그 테이블에 기록하고, 해당 상품의 가격통제구분(`goodsControlFg`)이 `'0'`(본부통제)일 경우 매장 단가 마스터인 `MPRICETB`를 연동 업데이트/인서트합니다.

### 4.3 Depth 3: 매장 단가 마스터 연쇄 동작
- **Tr_MPRICE_T01_Service (매장 단가 변경)**:
  - `Tr_TPRICE_T01_Service` 내부에서 `MPRICETB`에 대한 변경 작업을 수행한 직후 호출됩니다.
  - `priceFg`가 `'0'`(판매가)일 경우 `SSPRICTB` 및 `MPRILGTB`에 연쇄 인서트를 수행합니다.
  - *참고*: 계약이월에서는 `priceFg`가 `'2'`(공급가/예정가)로 생성되므로 `Tr_MPRICE_T01_Service` 조건 분기에 따라 `SSPRICTB`로의 다운스트림 전파는 바이패스되지만, 호출 단계 자체는 Depth 3 체인의 최하단까지 안전하게 도달합니다.

### 4.4 연쇄 요약 테이블 (직접영향테이블)

| 1차 연쇄 (Depth 1) | 2차 연쇄 (Depth 2) | 3차 연쇄 (Depth 3) | 로그 및 히스토리 |
|-------------------|-------------------|-------------------|-----------------|
| `TESFRHTB` (수정)  | `TPRICETB` (수정)  | `MPRICETB` (인서트/수정) | `TESHISTB`, `TPRILGTB` |

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 | 성공 (fnb 본사 관리자 `fnbadmin` / NC0005) ✅ |
| 화면 경로 | 견적관리 > 견적관리 > 계약이월 ✅ |
| 화면 로딩 | 정상 ✅ |

### 5.2 화면 구성 확인
- **조회조건 패널**: 견적유형(콤보), 거래처(콤보), 적용기간(달력), 초기화/조회 버튼 존재 ✅
- **계약이월 패널**: 연장기간(달력), 이월 버튼 존재 ✅
- **데이터 테이블**: 견적서양식명, 적용시작일, 적용종료일, 거래처명, 상품명, 규격, 단위, 수량, 이전단가, 적용단가 컬럼 정상 표시 ✅

### 5.3 기능별 테스트 결과

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI 및 동작 | 판정 |
|------|-----------|---------|----------------|------|
| 견적형태 로딩 | `/selectEstimType` | ✅ 구현 완료 | ✅ 대분류/중분류 드롭다운 목록 자동 로딩 | **PASS** |
| 견적 목록 조회 | `/search` | ✅ 구현 완료 | ✅ 조회 조건에 맞는 미이월 견적 상품 목록 표출 | **PASS** |
| 계약이월 실행 | `/extendDate` | ✅ 구현 완료 | ✅ 연장기간 설정 후 "이월" 클릭 시 확인 모달 표출 및 완료 처리 | **PASS** |

---

## 6. SQL Mapper 검증

### 6.1 Oracle (+) 외부조인 잔존 여부
- `getList` 쿼리에서 `A.CHAIN_NO = B.CHAIN_NO(+)` 형태의 레거시 Oracle 아우터 조인 문법이 일부 존재합니다.
- *권장*: PostgreSQL/EPAS 호환성을 보장하기 위해 ANSI `LEFT JOIN` 문법으로의 점진적 변환이 필요합니다.

### 6.2 Oracle 전용 함수 사용 여부
- `NVL()`, `LPAD()`, `TO_CHAR(SYSDATE, ...)` 등이 사용되고 있습니다. EPAS PostgreSQL에서는 해당 내장 함수들을 기본적으로 호환 모드로 지원하지만, 향후 순수 PostgreSQL 드라이버 표준 준수를 위해 `COALESCE()`, `LPAD()`, `TO_CHAR(NOW(), ...)` 등으로 변환할 것을 권장합니다.

### 6.3 EPAS Numeric Type Casting 결함 점검
- 본 화면 관련 마이퍼 XML(`Hq_Esti_00008_Sql.xml`) 내의 모든 `INSERT` 및 `UPDATE` 구문은 DB 테이블 칼럼 값들로부터 직접 조회하여 처리하는 `SELECT-INSERT` 방식을 취하고 있어, 화면 단에서 넘어오는 빈 문자열(`''`) 변수가 숫자 형식(`NUMERIC`) 칼럼에 바인딩되어 형변환 에러를 유발하는 결함은 존재하지 않는 것으로 확인되었습니다.

---

## 7. 검증 항목 체크리스트

### 7.1 코드베이스 변환 정합성

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 선언 | ✅ 정상 | 예외 발생 시 Rollback 설정 완료 |
| `@Autowired` Mapper 및 트리거 서비스 주입 | ✅ 정상 | `Tr_TESFRH_T01_Service`, `Tr_TPRICE_T01_Service` 정상 호출 |
| DML 실행 전 OLD 데이터 조회 | ✅ 정상 | 트리거 서비스 내부에서 선행 캐싱 |
| DML 실행 후 `processTrigger` 호출 | ✅ 정상 | 상태값 변화에 따른 트리거 정상 전파 |

### 7.2 트리거 연쇄 로직 정합성

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `TPRICETB` 인서트 동작 | ✅ 정상 | 계약이월 시 가격구분 `'2'`로 인서트 확인 |
| `TESHISTB` 히스토리 생성 | ✅ 정상 | `ESTIM_EXTEND_YN = 'Y'`로 이력 인서트 확인 |
| `TPRILGTB` 로그 생성 (Depth 2) | ✅ 정상 | 95건 로그 생성 확인 |
| `MPRICETB` 동기화 (Depth 3) | ✅ 정상 | 본부통제 상품 95건에 대해 매장 단가 테이블 생성 확인 |

---

## 8. 발견된 이슈 및 권고사항

### 🔴 Critical (즉시 처리 필요)
- 없음.

### 🟡 Warning (향후 마이그레이션 시 권장)
1. **Oracle (+) 외부조인 존재**
   - `Hq_Esti_00008_Sql.xml` 내 `getList` 쿼리에서 `A.CHAIN_NO = B.CHAIN_NO(+)` 형식의 조인이 잔존하므로 ANSI `LEFT JOIN` 표준 문법으로의 변경을 권장합니다.
2. **Oracle 전용 함수 및 키워드**
   - `NVL()`, `SYSDATE` 등의 문법을 PostgreSQL 표준인 `COALESCE()`, `NOW()` 등으로 표준화할 것을 권장합니다.

---

## 9. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 | ✅ PASS |
| 견적유형 조회 | ✅ PASS |
| 견적 목록 조회 | ✅ PASS |
| 계약이월 실행 | ✅ PASS |
| 트리거 연쇄 (Depth 3) | ✅ PASS |
| **종합 판정** | **✅ PASS** |

---

## 10. 첨부 (E2E 테스트 실행 화면)

- **초기 접속 화면**: `hq_esti_00008_1_initial.png`
- **조회 결과 화면**: `hq_esti_00008_2_searched.png`
- **이월 확인 창**: `hq_esti_00008_3_confirm_dialog.png`
- **이월 완료 화면**: `hq_esti_00008_4_finished.png`

---
*본 리포트는 E2E 브라우저 자동화 시나리오 수행 및 데이터베이스 상태 변경 검증을 기반으로 작성되었습니다.*
