# QA Report: Hq_System_00008 명칭코드관리
**작성일**: 2026-06-11  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 시스템관리 > 영업정보시스템 > 명칭코드관리 (hq_system_00008)  
**테스트 환경**: http://localhost:8080 (로컬 개발 서버)  
**접속ID/PW**: shopadmin / 0000 (본사 관리자 권한)

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/hq/system/Hq_System_00008_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/hq/system/Hq_System_00008_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/hq/system/Hq_System_00008_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../resources/sqlmapper/system/Hq_System_00008_Sql.xml` |
| 트리거 서비스 | `hyundai-api/.../service/trigger/Tr_MNAMEM_T01_Service.java` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/system/hq_system_00008
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
|-----------|------|------|------------|
| `/search/nameCd` | POST | 분류 코드 목록 조회 | SELECT (명칭 조회) |
| `/search/nameDt` | POST | 상세 코드 목록 조회 | SELECT (명칭 조회) |
| `/insert/nameCd` | POST | 분류 코드 신규 등록 | INSERT (명칭 생성) |
| `/insert/nameDt` | POST | 상세 코드 신규 등록 | INSERT (명칭 생성) |
| `/save/nameCd` | POST | 분류 코드 수정 | UPDATE (명칭 수정) |
| `/save/nameDt` | POST | 상세 코드 수정 | UPDATE (명칭 수정) |
| `/delete/nameCd` | POST | 분류 코드 삭제 (하위 상세 코드 포함) | DELETE (명칭 삭제) |
| `/delete/nameDt` | POST | 상세 코드 삭제 | DELETE (명칭 삭제) |

---

## 3. 서비스 로직 분석 (코드베이스 변환 검증)

### 3.1 분류 코드 생성 흐름 (`insertNameCd`)
```
[Controller] save (searchId="nameCd")
  └─ [Service] insertNameCd
       ├─ Mapper.getMenuCdChk()       → 코드 중복 체크
       ├─ Mapper.insertNameCd()       → MNAMEMTB 분류코드 INSERT
       └─ Tr_MNAMEM_T01_Service       → TriggerUtil.PROG_FG_A 호출
            └─ commonService.insertMmslogtb("000000", "MNAMEMTB", "A", key, "공통명칭마스터")
```

### 3.2 상세 코드 생성 흐름 (`insertNameDt`)
```
[Controller] save (searchId="nameDt")
  └─ [Service] insertNameDt
       ├─ Mapper.getMenuDtChk()       → 상세코드 중복 체크
       ├─ Mapper.insertNameDt()       → MNAMEMTB 상세코드 INSERT
       └─ Tr_MNAMEM_T01_Service       → TriggerUtil.PROG_FG_A 호출
            └─ commonService.insertMmslogtb("000000", "MNAMEMTB", "A", key, "공통명칭마스터")
```

### 3.3 분류/상세 코드 수정 흐름 (`save/nameCd`, `save/nameDt`)
```
[Controller] updateMenuClass
  └─ [Service] updateNameCd / updateNameDt
       ├─ Tr_MNAMEM_T01_Service       → 선행 getValues() 로 OLD 데이터 캡처
       ├─ Mapper.updateNameCd() / updateNameDt()
       └─ Tr_MNAMEM_T01_Service       → TriggerUtil.PROG_FG_U 호출
            └─ commonService.diffCheck() 확인 후 차이점을 MMSLOGTB에 UPDATE 로깅
```

### 3.4 분류 코드 일괄 삭제 흐름 (`delete/nameCd`)
```
[Controller] deleteMenuClass (searchId="nameCd")
  └─ [Service] deleteNameCd
       ├─ Tr_MNAMEM_T01_Service       → 하위 상세코드 리스트(oldParamList) 선행 로드
       ├─ Mapper.deleteNameDtList()   → 하위 상세코드 일괄 DELETE
       ├─ Tr_MNAMEM_T01_Service       → 하위 상세코드 건별로 TriggerUtil.PROG_FG_D 호출 (MMSLOGTB D 로깅)
       ├─ Tr_MNAMEM_T01_Service       → 대분류 oldParamMap 로드
       ├─ Mapper.deleteNameCd()       → 대분류 코드 DELETE
       └─ Tr_MNAMEM_T01_Service       → 대분류 TriggerUtil.PROG_FG_D 호출 (MMSLOGTB D 로깅)
```

---

## 4. DB 트리거 → 코드베이스 연쇄 분석

### 4.1 명칭 코드 연쇄 체인 (Tr_MNAMEM_T01_Service)
```
MNAMEMTB [I/U/D]
  └─ Tr_MNAMEM_T01_Service.processTrigger()
       ├─ [UPDATE 분기] commonService.diffCheck() 수행 (NM_REP, NM_SUB 변경분 확인)
       └─ commonService.insertMmslogtb() 실행 (MMSLOGTB 적재)
```

### 4.2 연쇄 요약 테이블 (직접 영향 테이블)

| 원본 테이블 | 1차 연쇄 | 2차 연쇄 | 로그 테이블 |
|-----------|---------|---------|-----------|
| MNAMEMTB | 없음 | 없음 | MMSLOGTB |

> [!NOTE]
> **연쇄 분석 결과**: `MNAMEMTB` 테이블 자체는 조회용 기준 코드 테이블이므로, CUD 발생 시 가맹점 등으로 하위 데이터가 복제되거나 전파되는 트리거 연쇄 체인은 존재하지 않습니다. 다만, 관리상 변경 이력 추적을 위해 `MMSLOGTB`에 변경 내용을 쌓는 Java 마이그레이션 트리거가 올바르게 작동함을 검증하였습니다.

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 | 성공 (shopadmin / 0000) ✅ |
| 화면 경로 | 시스템관리 > 영업정보시스템 > 명칭코드관리 ✅ |
| 화면 로딩 | 정상 ✅ |

### 5.2 화면 구성 확인

- **명칭분류 테이블 (좌측)**: No., 분류코드, 분류명, 길이, 비고, 시스템 타입(수정/삭제) 컬럼 ✅
- **명칭상세 테이블 (우측)**: No., 코드, 코드명, 코드서브명, 비고, 수정/삭제 컬럼 ✅
- **기능 버튼**: 분류추가, 코드추가, 조회, 초기화 버튼 존재 ✅

### 5.3 E2E 기능별 테스트 결과

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI | 판정 |
|------|-----------|---------|---------|------|
| 분류 목록 조회 | `/search/nameCd` | ✅ 구현 완료 | ✅ 데이터 표시 | **PASS** |
| 상세 목록 조회 | `/search/nameDt` | ✅ 구현 완료 | ✅ 데이터 표시 | **PASS** |
| 분류 신규 등록 | `/insert/nameCd` | ✅ 구현 완료 | ✅ 분류추가 팝업 및 저장 | **PASS** |
| 상세 신규 등록 | `/insert/nameDt` | ✅ 구현 완료 | ✅ 코드추가 팝업 및 저장 | **PASS** |
| 분류 정보 수정 | `/save/nameCd` | ✅ 구현 완료 | ✅ 수정 팝업 및 저장 | **PASS** |
| 상세 정보 수정 | `/save/nameDt` | ✅ 구현 완료 | ✅ 수정 팝업 및 저장 | **PASS** |
| 상세 코드 삭제 | `/delete/nameDt` | ✅ 구현 완료 | ✅ 삭제 작동 | **PASS** |
| 분류 코드 삭제 | `/delete/nameCd` | ✅ 구현 완료 | ✅ 삭제 작동 (하위 일괄삭제) | **PASS** |

---

## 6. SQL Mapper 검증

### 6.1 형변환 결함(Numeric) 평가
- 대상 테이블 `hmsfns.MNAMEMTB` 내에는 `numeric` 속성 컬럼이 존재하지 않습니다.
- 분류코드 길이 속성인 `CD_LEN` 컬럼 역시 DB schema 상 `character varying(1)` 타입으로 설정되어 있어, 빈 문자열(`''`) 유입 시 형변환 결함 에러가 발생하지 않고 안전하게 처리됩니다.

### 6.2 SQL 정합성 (PostgreSQL)
- `Hq_System_00008_Sql.xml` 내 모든 INSERT/UPDATE 쿼리는 PostgreSQL에 호환되는 표준 SQL 및 `TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS')`로 마이그레이션이 잘 이루어져 에러 없이 수행되었습니다.
- 단, Oracle (+) 외부 조인은 존재하지 않아 쿼리 변환 결함 이슈는 없습니다.

---

## 7. 검증 항목 체크리스트

### 7.1 코드베이스 변합 정합성

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 어노테이션 | ✅ 정상 | rollbackFor 포함 |
| `@Autowired` 트리거 서비스 주입 | ✅ 정상 | `Tr_MNAMEM_T01_Service` 주입 확인 |
| `TriggerUtil` 변수 바인딩 | ✅ 정상 | PROG_FG_A / U / D 정상 분기 |
| `getValues()` 및 `processTrigger()` 호출 | ✅ 정상 | CUD 전후 데이터 캡처 및 전달 |

---

## 8. 발견된 이슈 및 권고사항

### 🟢 Info (참고 및 권장 사항)
1. **분류코드 목록 operate 헤더 불일치**  
   - 좌측 분류코드 목록의 수정/삭제 버튼 헤더가 `수정/삭제`가 아닌 `시스템 타입`으로 잘못 표기되어 있습니다. UI 일관성을 위해 차후 `수정/삭제` 혹은 `관리` 로 헤더 타이틀을 수정하는 것을 권장합니다.
2. **분류 및 상세 코드 비고란 입력 길이 제한 누락 (조치 완료)**  
   - 분류코드 등록 팝업 및 상세코드 등록 팝업 내 `비고(remark)` 필드에 입력 길이 제한(`maxlength`)이 누락되어 있어, DB 컬럼 크기(4000자) 이상의 과도한 문자열이 수신될 시 DB 오류가 유발되는 결함이 존재했습니다.  
   - JSP 파일(`hq_system_00008_M01.jsp`, `hq_system_00008_M02.jsp`)의 비고 input 태그에 `maxlength="4000"` 속성을 부여하여 초과 입력되지 않도록 조치하였습니다.

---

## 9. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 | ✅ PASS |
| 분류/상세 조회 | ✅ PASS |
| 분류/상세 등록 | ✅ PASS |
| 분류/상세 수정 | ✅ PASS |
| 분류/상세 삭제 | ✅ PASS |
| 트리거 연쇄 및 DB 로깅 | ✅ PASS |
| **종합** | **✅ PASS** |

---

## 10. 첨부 (E2E 테스트 스크린샷)

- **조회 결과**: ![조회 결과](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_search.png)
- **분류코드 등록 팝업**: ![등록 팝업](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_class_add_modal.png)
- **분류코드 추가 완료**: ![추가 완료](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_added.png)
- **상세코드 등록 팝업**: ![상세코드 팝업](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_detail_add_modal.png)
- **상세코드 추가 완료**: ![상세코드 완료](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_detail_added.png)
- **상세코드 수정 팝업**: ![상세코드 수정](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_detail_modify_modal.png)
- **상세코드 수정 완료**: ![상세코드 수정완료](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_detail_modified.png)
- **분류코드 수정 팝업**: ![분류코드 수정](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_class_modify_modal.png)
- **분류코드 수정 완료**: ![분류코드 수정완료](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_class_modified.png)
- **상세코드 삭제 완료**: ![상세코드 삭제](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_detail_deleted.png)
- **분류코드 삭제 완료**: ![분류코드 삭제](file:///D:/hmTest/backoffice/QaReport/hq_system_00008_class_deleted.png)
