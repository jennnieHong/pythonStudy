# 명칭코드마스터 길이(CD_LEN) 컬럼 정의 및 활용 분석 가이드

본 문서는 명칭코드 마스터 테이블(`hmsfns.MNAMEMTB`)의 **길이(`CD_LEN`)** 속성에 대한 데이터베이스 설계상 정의, 코드베이스 내 실제 제약 조건 동작 여부, 그리고 최근 UI 결함 수정 조치 내역을 기록하기 위해 작성되었습니다.

---

## 1. DB 스키마 설계상 정의

### 1.1 컬럼 정의 및 코멘트
* **컬럼명**: `CD_LEN` (`character varying(1)`)
* **물리 DDL 정의 (Oracle/PostgreSQL)**:
  ```sql
  -- hmsfns.MNAMEGTB 및 MNAMEMTB 정의
  "CD_LEN" VARCHAR2(1 BYTE)
  COMMENT ON COLUMN "hmsfns"."MNAMEGTB"."CD_LEN" IS '코드 자릿수 ';
  ```
* **의미**: 해당 분류코드(Category) 하위에 매핑되어 속할 자식 상세코드들(Detail Codes)이 규격상 가져야 하는 **자릿수(Digit Count / Length)**를 나타냅니다.

### 1.2 실제 데이터 예시
* **길이 = 1**: 분류코드 `122` (재고단위) 하위의 상세코드들이 `C`, `E` 등 **1자리 단일문자** 형태로 이루어져 있음을 명시.
* **길이 = 3**: 분류코드 `061` (매장형태) 하위의 상세코드들이 `001`, `002` 등 **3자리 숫자** 형태로 이루어져 있음을 명시.

---

## 2. 소스코드 정적 분석 및 검증 결과

> [!IMPORTANT]
> **실제 코드 제약 조건 동작 여부: 미사용 (Pure Metadata)**
> 분석 결과, 입력한 `CD_LEN`의 크기 값을 가져와서 실제 상세코드 입력 시 문자 길이를 실시간 검증하거나 입력을 제한하는 **강제성 비즈니스 로직(Validation)은 소스코드(Java/JS) 및 DB(프로시저) 전반에 걸쳐 존재하지 않습니다.**

### 2.1 Front-end (JavaScript) 검증 생략
* 상세코드 등록 함수인 `fnSaveRegiDtCode()`에서는 오직 필수 입력 여부(Null check)만 검증하며, 선택된 대분류의 `cdLen` 값을 대조하여 입력값을 검증하는 로직이 생략되어 있습니다.
* 상세코드 입력 필드는 HTML 구조상 `maxlength="3"`으로 고정되어 자릿수가 제한됩니다.

### 2.2 Back-end (Java) 및 DB 프로시저 검증 생략
* Controller 및 Service 단에서도 중복여부만 검증할 뿐 `cdLen` 데이터는 단순 파라미터 전달 및 CRUD 업데이트 대상일 뿐 비즈니스 규칙 제어용으로 사용되지 않습니다.
* 타 모듈의 상품코드 자동 채번 자릿수 기능인 `GOODSCD_LEN`과 달리, 명칭코드의 `CD_LEN`은 **단순 설명 및 참조용 메타데이터 속성**으로 역할하고 있습니다.

---

## 3. UI 결함 조치 사항 (2026-06-11)

### 3.1 비고(Remark)란 입력 길이 제한 결함 해결
* **문제점**: 분류코드 및 상세코드 등록/수정 모달창 내 비고(`remark`) 필드에 글자 수 제한(`maxlength`)이 지정되지 않아, DB 필드 크기(4000자)를 초과해 입력할 시 SQL 예외 오류(데이터 잘림 또는 버퍼 오버플로우)가 유발될 가능성이 존재했습니다.
* **조치 내용**: JSP 파일의 비고 input 태그에 `maxlength="4000"`을 적용하여 브라우저에서 강제 차단하도록 수정 완료하였습니다.

| 대상 파일 | 수정 타겟 엘리먼트 | 반영 속성 |
|-----------|-------------------|-----------|
| `hq_system_00008_M01.jsp` | `#remark` (분류 비고) | `maxlength="4000"` 추가 |
| `hq_system_00008_M02.jsp` | `#dtRemark` (상세 비고) | `maxlength="4000"` 추가 |
| `admin_system_00008_M01.jsp` | `#remark` (분류 비고) | `maxlength="4000"` 추가 |
| `admin_system_00008_M02.jsp` | `#dtRemark` (상세 비고) | `maxlength="4000"` 추가 |

### 3.2 Admin 화면 라벨 오류 수정
* **대상 파일**: [admin_system_00008_M01.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/admin_system_00008/modal/admin_system_00008_M01.jsp#L43)
* **내용**: 길이(`cdLen`)를 입력받는 폼 라벨의 한글 텍스트가 **"분류코드"**로 오기재되어 있던 것을 본사와 일치하게 **"길이"**로 수정 조치 완료했습니다.
