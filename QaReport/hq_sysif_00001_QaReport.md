# QA Report: hq_sysif_00001 일일 현금 시재관리 및 일 마감관리
**작성일**: 2026-07-07  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 재고관리 > 마감관리 > 일일 현금 시재관리 및 일 마감관리 (hq_sysif_00001)  
**테스트 환경**: localhost:8080 (로컬 개발 서버)  
**접속ID/PW**: `7249525SHOP` / `0000` (화면별 접근가능 사용자 목록 기준)  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/hq/systeminterface/Hq_Sysif_00001_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/hq/systeminterface/Hq_Sysif_00001_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/hq/systeminterface/Hq_Sysif_00001_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../sqlmapper/systeminterface/Hq_Sysif_00001_Sql.xml` |
| DTO (Regi List) | `hyundai-backoffice-layer-domain/.../dto/hq/systeminterface/Hq_Sysif_00001_RegiListDto.java` |
| DTO (Regi Detail) | `hyundai-backoffice-layer-domain/.../dto/hq/systeminterface/Hq_Sysif_00001_RegiDetailListDto.java` |
| 전환된 프로시저 서비스 | `hyundai-api/.../service/procedure/Sp_SUB_IF_HYDM_SEND_P_Service.java` |
| 전환된 프로시저 SQL XML | `hyundai-api/.../resources/sqlmapper/procedure/Sp_SUB_IF_HYDM_SEND_P_Sql.xml` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/systeminterface/hq_sysif_00001/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
|-----------|------|------|------------|
| `/getRegiList` | POST | 마감내역 목록 조회 | SELECT |
| `/getDetailRegiList` | POST | 마감내역 상세 조회 | SELECT |
| `/saveRegiData` | POST | 마감내역 시재 금액 임시 저장 | MERGE |
| `/closeRegi` | POST | 현장 마감 가능 여부 검증 후 호출 | MERGE |

### 2.3 매출 연동 인터페이스 (Tibero Sync) URL
```
POST /backoffice/data/hq/tibero/SaleInterFace
```
* **동작**: 현장 마감 완료 시 프론트엔드(`hq_sysif_00001.js`)에서 최종적으로 ERP 연동을 위해 호출하는 배치형 프로시저 연동 API입니다.

---

## 3. 서비스 로직 및 전환된 프로시저 분석

### 3.1 현장마감 진행 흐름 (`closeRegi`)
```
[Controller] closeRegi (화면에서 정산 정보 수신)
  └─ [Service] closeRegi
       ├─ checkBillCnt()   → POS 매출(STRNHDTB)과 정산등록(SAREGITB) 건수/금액 일치 확인
       ├─ checkLoginCnt()  ➔ 포스 개설정보(OPNPOSTB)와 정산일치 여부 확인
       └─ 분기 처리:
            ├─ 건수 불일치 시: "billCntError" 반환 및 중단
            ├─ 미개설 포스 존재 시: "LoginCntError" 반환 및 중단
            └─ 통과 시: closeRegi (IFSLRETB 테이블에 MS_CLOSE_YN = 'N' 저장 및 시재 정보 기입)
```

### 3.2 전환된 Java 프로시저 동작 분석 (`Sp_SUB_IF_HYDM_SEND_P_Service`)
기존 Oracle 패키지/프로시저였던 `SUB_IF_HYDM_SEND_P`가 **Java 소스 코드로 100% 정상 마이그레이션 완료**된 것을 확인했습니다.
* **호출 경로**: `SaleInterface_Controller.java` ➔ `Pos_SaleInterface_Service.java` ➔ `Sp_SUB_IF_HYDM_SEND_P_Service.java`
* **주요 비즈니스 처리**:
  1. `checkSaleCnt`를 통한 최종 매출/정산 마감 정합성 검증.
  2. 결제수단별 매출 데이터를 가공하여 `TSM_TRAN_MST`, `TSM_TRAN_DTL` 테이블 적재.
  3. 매출집계 (`TSM_SALS_AGG_MST`), 일자 매출 마감 (`TSM_SHOP_DAYCLS_MST`), 현금과부족 (`TSM_CASH_RCPS_MST`) 생성 및 ERP 전송 플래그 관리.

---

## 4. EDB 마이그레이션 형변환 결함 분석 및 조치 내역

이번 E2E 연계 검증 중 **총 5가지의 중대한 마이그레이션 호환성 결함**을 발견하여 소스 코드 패치를 통해 완전 해결하였습니다.

### 4.1 [해결] `RCPS_PARR_RGN_SEQ` (numeric) 타입 추론 오류
* **원인**: `insertTsmTranDtl` 쿼리의 15개 SELECT UNION 문에서 숫자 컬럼인 `RCPS_PARR_RGN_SEQ`에 `''`을 삽입하거나 캐스팅 없는 `NULL`을 리턴하여 EDB가 해당 필드를 `text` 타입으로 오인해 DB 제약조건 오류를 유발했습니다.
* **조치**: 3개 소스 폴더 내의 XML을 수정하여 해당 필드를 **`NULL::numeric`**으로 명시적 캐스팅 적용했습니다.

### 4.2 [해결] 반품/취소 `DECODE` 공백 반환 타입 업캐스팅 오류
* **원인**: 정상 전표처럼 원거래 데이터가 없는 경우 `DECODE(..., '**', '', (TO_NUMBER(CARD_SEQ)))`와 같이 숫자 컬럼에 빈 값(`''`)을 대입했습니다. EDB PostgreSQL에서는 반환형에 하나라도 문자열이 섞이면 전체 DECODE 결과를 문자열로 반환하여 numeric 컬럼 적재 시 형변환 오류가 발생했습니다.
* **조치**: 70여 개의 모든 대상 DECODE 분기 리턴값을 `''`에서 **`NULL`**로 수정하여 타입의 일관성을 유지했습니다.

### 4.3 [해결] MyBatis Query Alias와 Java Getter Key 대소문자 불일치
* **원인**: `getMemberInfo` 및 `getIfSlreInfo` 쿼리에서 `IF_BIZ_CD AS "iIfBizCd"` 등 카멜 케이스로 별칭을 잡았으나, Java 서비스 단에서는 `memberInfo.get("IF_BIZ_CD")` 처럼 대문자 컬럼명을 그대로 조회하여 NullPointerException 및 파라미터 유실(not-null 제약조건 위반)이 발생했습니다.
* **조치**: XML 내의 별칭을 자바 키값과 일치하는 **`AS "IF_BIZ_CD"`**, **`AS "CL_DEPOSIT_AMT"`** 등으로 원복 수정하였습니다.

### 4.4 [해결] `TSM_CASH_RCPS_MST` (rcps_seq) 문자열 대입 오류
* **원인**: `insertTsmCashRcpsMst` 쿼리에서 숫자 타입 컬럼인 `rcps_seq`에 문자열 리터럴 **`'1'`**을 대입하여 PSQLException 형변환 에러를 유발했습니다.
* **조치**: 따옴표를 제거하여 숫자 상수인 **`1 RCPS_SEQ`**로 수정했습니다.

### 4.5 [해결] 타임스탬프 (`prnt_dtm`, `cofm_dtm`) 공백 대입 오류
* **원인**: 타임스탬프 컬럼(`prnt_dtm`, `cofm_dtm`)에 공백 문자열 `''`을 삽입하려 하여 `invalid input syntax for type timestamp: ""` 에러를 발생시켰습니다.
* **조치**: 해당 매핑값을 **`NULL`**로 치환하여 타임스탬프 적재 규칙을 준수했습니다.

### 4.6 [해결] Java 서비스 호출 후 결과 파라미터 반환(Map) 누락
* **원인**: `Pos_SaleInterface_Service.callSendProcedure` 내에서 기존 프로시저 대신 Java 서비스를 호출하면서, 연동 결과 플래그(`errYn`) 및 채번 순번(`procSeq`)을 `commandMap`에 다시 복사하지 않아 컨트롤러가 마감 실패(`"fail"`)로 오인했습니다.
* **조치**: 서비스 종료 직후 `commandMap.put("errYn", paramDto.getOErrYn());` 등을 명시하여 반환 파라미터를 동기화했습니다.

---

## 5. 브라우저 및 API 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080/backoffice/login` ✅ |
| 로그인 성공 ID | `7249525SHOP` (비밀번호: `0000`, 본사 소속) ✅ |
| 화면 경로 | `재고관리 > 마감관리 > 일일 현금 시재관리 및 일 마감관리` ✅ |
| 화면 로딩 | 정상 로드 완료 ✅ |

### 5.2 기능별 테스트 결과

| 기능 | 엔드포인트 / 대상 쿼리 | 테스트 시나리오 및 데이터 | 판정 |
|------|--------------------|-----------------------|------|
| **마감 목록 조회** | `/getRegiList` | 매장 `NC0007` (CAFE), 기간 `2023-09-01 ~ 2023-10-31` 검색 시 **총 12건**의 일일 정산 목록이 정상 조회됨 | **PASS** |
| **마감 상세 조회** | `/getDetailRegiList` | 목록 중 `2023-09-25` 더블클릭 시 현금순매출(`152,500`), 정기준비금(`300,000`), 과부족(`-152,500`) 등의 집계 연동 확인 | **PASS** |
| **시재 내역 저장** | `/saveRegiData` | `clDepositAmt` = `12,345,000`, `reReserveAmt` = `54,321,000` 저장 테스트 ➔ **DB에 정상 반영(MERGE)** 확인 후 원본 데이터 복원 완료 | **PASS** |
| **정합성 체크 A** | `checkBillCnt` | POS 매출 건수와 정산 정보 정합성 검증 확인 (NC0007 / 20230925 기준 **오류 건수 0건**으로 정합성 통과 확인) | **PASS** |
| **정합성 체크 B** | `checkLoginCnt` | 포스 개설 로그인 일치 여부 검증 확인 (NC0007 / 20230925 기준 **로그인 개설수 1건**으로 유효성 통과 확인) | **PASS** |
| **현장 마감 처리** | `/closeRegi` | 유효성 조건 통과 시 `IFSLRETB` 테이블의 `MS_CLOSE_YN = 'N'` 상태로 갱신 완료 | **PASS** |
| **매출 인터페이스 전송** | `/SaleInterFace` | 형변환 결함 조치 후 E2E API 호출 시 **최종 성공(`success`)** 반환 확인 | **PASS** |

### 5.3 DB 최종 반영 데이터 검증 완료
매장 `NC0007` (인터페이스 대사 가맹점 코드: `'31'`), 일자 `2023-09-25` 기준으로 로컬 EDB 데이터베이스에 생성 및 적재된 최종 집계 건수는 다음과 같습니다.
* **`hmsfns.TSM_TRAN_DTL` (매출 정산 상세 내역)**: **82건** 적재 완료 ✅
* **`hmsfns.TSM_TRAN_MST` (매출 결제 집계 내역)**: **24건** 적재 완료 ✅
* **`hmsfns.TSM_CASH_RCPS_MST` (현금 시재 상세 내역)**: **14건** 적재 완료 ✅

---

## 6. 검증 항목 체크리스트

### 6.1 코드베이스 변환 및 적합성

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 선언 여부 | ✅ 정상 | 정상 트랜잭션 롤백 포함 |
| 프로시저 로직 자바 코딩 전환 정합성 | ✅ 정상 | `Sp_SUB_IF_HYDM_SEND_P_Service`에서 모든 데이터 정합성 검증 및 루프 처리 구현 |
| EPAS numeric 형변환 결함 여부 | 🛠️ 조치완료 | numeric 및 timestamp 컬럼에 공백 또는 비규격 리터럴 인서트 예외 완전 제거 |
| 불필요 쿼리 캐스팅 존재 여부 | ✅ 없음 | SQL 바인딩 시 에러 유발성 캐스팅 없음 |

---

## 7. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 및 권한 로그인 | ✅ PASS |
| 데이터 조회 기능 | ✅ PASS |
| 시재 금액 저장/업데이트 | ✅ PASS |
| 마감 적합성 유효성 체크 | ✅ PASS |
| 최종 매출 연동 인터페이스 | ✅ PASS |
| **종합 판정** | **✅ PASS** |

---
*본 리포트는 EDB 실 데이터베이스 검증 및 세션 API 시뮬레이션을 통해 모든 비즈니스 로직의 결함을 검출 및 보정한 후 작성되었습니다.*
