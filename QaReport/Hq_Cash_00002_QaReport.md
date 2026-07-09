# QA Report: Hq_Cash_00002 매장별 입출금현황
**작성일**: 2026-06-15  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 입출금관리 > 입출금관리 > 매장별 입출금현황 (hq_cash_00002)  
**테스트 환경**: localhost:8080 (로컬 개발 서버)  
**접속ID/PW**: shopadmin / 0000 (본사 관리자 권한)  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | [Hq_Cash_00002_Controller.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/hq/cash/Hq_Cash_00002_Controller.java) |
| Service | [Hq_Cash_00002_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/hq/cash/Hq_Cash_00002_Service.java) |
| Mapper (Interface) | [Hq_Cash_00002_Mapper.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-persistence/src/main/java/com/hyundai/backoffice/webapp/dao/hq/cash/Hq_Cash_00002_Mapper.java) |
| SQL XML | [Hq_Cash_00002_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/cash/Hq_Cash_00002_Sql.xml) |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/cash/hq_cash_00002/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
|-----------|------|------|------------|
| `/searchList` | POST | 매장별 입출금현황 요약 목록 조회 | SELECT |
| `/selectDtList` | POST | 특정 계정의 입출금 상세내역 조회 | SELECT |

---

## 3. 서비스 로직 분석 (코드베이스 변환 검증)

### 3.1 CUD 로직 및 트리거 서비스 검증
* **화면 내 CUD 발생 여부**: 
  > ℹ️ **본 화면(hq_cash_00002)에서는 데이터의 추가/수정/삭제가 발생하지 않는 순수 SELECT 기능만 존재합니다.**
* **테이블 및 트리거 연계**:
  * 연관 테이블인 `MMACNTTB`는 `AFTER INSERT OR UPDATE OR DELETE` 시 POS 연동을 수행하는 `MMACNT_T01` 트리거가 존재하나, 백오피스 소스코드 내에서는 `MMACNTTB` 테이블에 CUD를 직접 수행하는 로직이 아예 존재하지 않습니다.
  * 따라서 백오피스 자바 소스코드 상에 트리거 연쇄용 서비스(`Tr_MMACNT_T01_Service` 등) 호출이 배제되어 있는 것은 의도적인 설계로 판단됩니다.

---

## 4. DB 트리거 → 코드베이스 연쇄 분석

본 화면에서는 단순 SELECT 조회를 수행하므로 연쇄 트리거 로직을 직접 실행하지 않습니다. 다만, 데이터 입수 원천이 되는 타 화면(`st_cash_00001` 일일입출금등록, `st_cash_00004` 월간지출내역등록)에서 실적 데이터인 `MACCIOTB`에 CUD DML이 일어날 때의 관계는 다음과 같습니다.

### 4.1 데이터 흐름 연쇄 맵

```text
[입출금등록 st_cash_00001]
  └─ [DML] MACCIOTB (INSERT/UPDATE/DELETE)
       └─ (영향 테이블 없음, 단독 실적 적재)

[매장별 입출금현황 hq_cash_00002]
  ├─ [SELECT] MACCIOTB (입출금 거래 실적 데이터)
  └─ [SELECT] MMACNTTB (매장별 계정 기준 마스터 데이터)
```

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 | 성공 (shopadmin / 0000) ✅ |
| 화면 경로 | 입출금관리 > 입출금관리 > 매장별 입출금현황 ✅ |
| 화면 로딩 | 정상 ✅ |

> ⚠️ **테스트 계정 정정 사항**:
> 엑셀 파일에는 테스트 계정으로 `fnbadmin`이 기재되어 있었으나, 실제 EDB 개발 DB(`MUSERSTB` 테이블) 확인 결과 해당 계정이 등록되어 있지 않았습니다. 따라서 동일 본사 권한을 가지는 `shopadmin` 계정으로 대체하여 테스트를 진행하였습니다. (패스워드는 0000으로 동일 세팅됨을 DB 해시 검증을 통해 확인 완료)

### 5.2 화면 구성 및 조회 결과 (NC0007 매장)

* **조회 조건**:
  * 매장 선택: `[오픈] CAFE - NC0007` (DB 실적이 존재하는 매장)
  * 조회 기간: `2026-02-01` ~ `2026-06-15`

* **조회 결과 데이터 (그리드 출력)**:
  * **계정구분**: `[0] 입금`
  * **계정명**: `[01] 기타입금`
  * **금액**: `334,323`원

* **상세 내역 모달 팝업 결과 (그리드 셀 클릭 시)**:
  * 모달 데이터 3건 표출 정상 확인:
    1. `2026-02-02` / `기타입금` / 금액 `50,000` / 부가세 `5,000` / 등록자 `fnbcafe`
    2. `2026-02-02` / `기타입금` / 금액 `50,000` / 부가세 `5,000` / 등록자 `fnbcafe`
    3. `2026-06-04` / `기타입금` / 금액 `234,323` / 부가세 `3,232` / 등록자 `fnbcafe`
    * **합계 금액**: `334,323` / **부가세 합계**: `13,232`

→ **데이터 정합성이 DB 실적(`hmsfns.MACCIOTB`)과 100% 일치함** ✅

---

## 6. SQL Mapper 검증

### 6.1 Oracle 잔존 함수 분석

| 쿼리 ID | 테이블 | 오라클 전용 구문 | 비고 / 수정안 |
|---------|--------|-----------------|---------------|
| `selectDetailMMaList` | MACCIOTB | `NVL(IO.CUST_CD, '')` | PostgreSQL 호환을 위해 `COALESCE` 권장 |
| `selectDetailMMaList` | MACCIOTB | `NVL(IO.REMARK, '')` | PostgreSQL 호환을 위해 `COALESCE` 권장 |
| `selectDetailMMaList` | MACCIOTB | `TO_DATE(ACCIO_DATE, 'YYYYMMDD')` | PostgreSQL 이관 시 표준 `TO_TIMESTAMP` 권장 |

---

## 7. 검증 항목 체크리스트

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 어노테이션 | ✅ 정상 | rollbackFor 포함 |
| Mapper 메서드 일치 여부 | ✅ 정상 | Interface ↔ XML 일치 |
| `@ServiceLog` 어노테이션 매핑 | ✅ 정상 | `/searchList`, `/selectDtList` 적용 완료 |
| 중복 로그인 다이얼로그 우회 | ✅ 정상 | `bootbox-accept` 클릭 제어 성공 |
| 데이터 정합성 일치 여부 | ✅ 정상 | DB 값과 화면 출력값 교차 검증 완료 |

---

## 8. 발견된 이슈 및 권고사항

### 🟡 Warning (마이그레이션 시 처리 필요)
1. **오라클 `NVL` 및 `TO_DATE` 형변환 잔존**
   * PostgreSQL 마이그레이션 시 표준 SQL 함수인 `COALESCE` 및 PostgreSQL 표준 날짜 연산(`TO_TIMESTAMP` 등)으로 변환할 필요가 있음.
2. **테스트 가이드 계정 미등록**
   * 엑셀 계정 정보 상의 `fnbadmin`이 DB에 미등록되어 있어 UI 인수 테스트 진행이 불가하므로, DB 스크립트에 테스트용 insert 구문을 보강하거나 엑셀 지침을 `shopadmin`으로 통일할 필요가 있음.

---

## 9. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 | ✅ PASS |
| 매장별 입출금현황 조회 | ✅ PASS |
| 상세내역 팝업 조회 | ✅ PASS |
| 데이터 정합성 (DB 연계) | ✅ PASS |
| **종합** | **✅ PASS** |

---

## 10. 첨부

* **조회 화면 결과**: `![조회화면](file:///C:/Users/uoshj/.gemini/antigravity-ide/brain/a6eb74d7-4237-4316-bd5d-fbf2d71150e6/hq_cash_00002_shopadmin.png)`
* **상세 내역 모달 팝업**: `![모달팝업](file:///C:/Users/uoshj/.gemini/antigravity-ide/brain/a6eb74d7-4237-4316-bd5d-fbf2d71150e6/hq_cash_00002_shopadmin_modal.png)`
