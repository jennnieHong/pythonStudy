# QA Report: Hq_Sales_00021 본사 POS 정산내역

**작성일**: 2026-06-26  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 본사 매출분석 > POS > POS 정산내역 (hq_sales_00021)  
**테스트 환경**: localhost:8080 (로컬 개발 서버)  
**접속 계정/PW**: `shopadmin` / `0000` (본사 관리자 계정)  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `backoffice/hyundai-backoffice-webapp/.../controller/hq/sales/Hq_Sales_00021_Controller.java` |
| Service | `backoffice/hyundai-backoffice-layer-service/.../service/hq/sales/Hq_Sales_00021_Service.java` |
| Mapper (Interface) | `backoffice/hyundai-backoffice-layer-persistence/.../dao/hq/sales/Hq_Sales_00021_Mapper.java` |
| SQL XML | `backoffice/hyundai-backoffice-webapp/.../sqlmapper/sales/Hq_Sales_00021_Sql.xml` |
| DTO | `backoffice/hyundai-backoffice-layer-domain/.../dto/hq/sales/Hq_Sales_00021_RegiListDto.java` |

### 1.2 시스템 아키텍처 및 데이터 흐름

<div class="mermaid-wrapper" style="position: relative; margin-bottom: 20px;">
  <button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText); alert('Mermaid 코드가 복사되었습니다.');" style="position: absolute; right: 10px; top: 10px; z-index: 100; background: #2563EB; color: white; border: none; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">코드 복사</button>

```text
sequenceDiagram
    autonumber
    actor User as 본사 사용자 (shopadmin)
    participant UI as 브라우저 UI (hq_sales_00021)
    participant Ctrl as Controller (Hq_Sales_00021_Controller)
    participant Svc as Service (Hq_Sales_00021_Service)
    participant Map as Mapper (Hq_Sales_00021_Mapper)
    database DB as EDB PostgreSQL (192.168.10.206)

    User->>UI: 매장코드(NC0003), 조회일자(2026-06-02) 설정 후 조회 클릭
    UI->>Ctrl: POST /searchRegiList {searchDate: "20260602", msNo: "NC0003"}
    Note over Ctrl: 세션에서 chainNo 취득
    Ctrl->>Svc: searchRegiList(CommandMap)
    Svc->>Map: searchRegiList(Map)
    Map->>DB: SELECT FROM SAREGITB (체인 산하 매장 정산 목록)
    DB-->>UI: 결과 데이터 로딩 및 그리드(t01) 렌더링
    
    User->>UI: 그리드 '매장' 셀(table-onclick) 클릭
    UI->>Ctrl: POST /searchRegiDetailList {saleDate: "20260602", msNo: "NC0003", posNo: "01"}
    Ctrl->>Svc: searchRegiDetailList(CommandMap)
    Svc->>Map: searchRegiDetailList(Map)
    Map->>DB: SELECT FROM SAREGITB (POS 상세 정산 내역)
    DB-->>UI: 결과 반환 및 상세 내역 모달(detailSearchModal) 표시
```

```mermaid
sequenceDiagram
    autonumber
    actor User as 본사 사용자 (shopadmin)
    participant UI as 브라우저 UI (hq_sales_00021)
    participant Ctrl as Controller (Hq_Sales_00021_Controller)
    participant Svc as Service (Hq_Sales_00021_Service)
    participant Map as Mapper (Hq_Sales_00021_Mapper)
    database DB as EDB PostgreSQL (192.168.10.206)

    User->>UI: 매장코드(NC0003), 조회일자(2026-06-02) 설정 후 조회 클릭
    UI->>Ctrl: POST /searchRegiList {searchDate: "20260602", msNo: "NC0003"}
    Note over Ctrl: 세션에서 chainNo 취득
    Ctrl->>Svc: searchRegiList(CommandMap)
    Svc->>Map: searchRegiList(Map)
    Map->>DB: SELECT FROM SAREGITB (체인 산하 매장 정산 목록)
    DB-->>UI: 결과 데이터 로딩 및 그리드(t01) 렌더링
    
    User->>UI: 그리드 '매장' 셀(table-onclick) 클릭
    UI->>Ctrl: POST /searchRegiDetailList {saleDate: "20260602", msNo: "NC0003", posNo: "01"}
    Ctrl->>Svc: searchRegiDetailList(CommandMap)
    Svc->>Map: searchRegiDetailList(Map)
    Map->>DB: SELECT FROM SAREGITB (POS 상세 정산 내역)
    DB-->>UI: 결과 반환 및 상세 내역 모달(detailSearchModal) 표시
```
</div>

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/sales/hq_sales_00021
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog | Type | 관련 테이블 |
|-----------|------|------|------------|------|------------|
| `/searchRegiList` | POST | POS 정산내역 요약 조회 | SELECT | SELECT | `hmsfns.SAREGITB`<br>`hmsfns.MMEMBSTB`<br>`hmsfns.MMEMBVTB` |
| `/searchRegiDetailList` | POST | POS별 상세 정산정보 모달 조회 | SELECT | SELECT | `hmsfns.SAREGITB` |

---

## 3. 서비스 로직 및 트랜잭션 분석

- **트랜잭션 설정**: 클래스 레벨에 `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})`이 명시되어 있어 예외 발생 시 안전하게 롤백이 가능하도록 선언되어 있습니다.
- **CUD 유무**: 해당 화면은 본사 관리자가 산하 가맹점의 POS 정산내역을 조회하기만 하는 **SELECT-only(단순 조회) 화면**입니다. INSERT, UPDATE, DELETE 구문은 코드베이스에 존재하지 않습니다.
- **권한 제약**:
  - `/searchRegiList` 호출 시 본사 관리자는 본인이 소속된 체인의 `chainNo`를 세션(`SecurityUserInformation`)으로부터 강제 적용받아 타 체인의 매장은 조회가 불가능합니다.
  - 본사 관리자는 체인 내의 특정 매장(`msNo`)을 직접 선택하거나 전체 매장을 통합하여 조회할 수 있는 파라미터 유연성을 제공합니다.

---

## 4. DB 트리거 → 코드베이스 연쇄 분석

- **트리거 및 프로시저 영향도**: **없음**
  - 조회만 하는 SELECT 쿼리로 구성되어 있으며, 데이터를 변경하거나 가공하는 DML operations가 존재하지 않습니다.
  - `SAREGITB` 테이블에는 관련된 DB 트리거나 연쇄 반응 프로시저가 전혀 존재하지 않음을 데이터베이스를 통해 확인하였습니다.
  - 따라서 Depth 3 연쇄 작용 검증은 해당 사항이 없습니다.

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080/backoffice` ✅ |
| 로그인 ID / PW | `shopadmin` / `0000` (본사 관리자 계정) ✅ |
| 화면 경로 | 매출분석 > POS > POS 정산내역 ✅ |
| 화면 로딩 | 정상 로딩 및 그리드(`#hq_sales_00021_t01`) 렌더링 완료 ✅ |

### 5.2 화면 구성 및 테스트 진행

1. **조회 조건 설정**:
   - 매장코드 셀렉트박스를 클릭하여 대상 매장인 **`NC0003` (고양 Shop)**을 선택하였습니다.
   - `조회일자` 데이트피커를 클릭하여 데이터가 존재하는 **`2026-06-02`**로 설정하였습니다.
2. **목록 조회**:
   - 조회 클릭 후 `hq_sales_00021_t01` 테이블에 **매장: 현대 Shop / POS: 01 / 영수증: 0001 / 총매출: 460,000원**의 데이터가 올바르게 렌더링되었습니다.
3. **상세 조회 (모달 팝업)**:
   - 그리드의 '매장' 컬럼 셀(`td.table-onclick`)을 클릭하였습니다.
   - 정산 상세 내역 모달(`#detailSearchModal`)이 정상적으로 오픈되며 총매출액(460,000원), 현금매출액(460,000원), 고객수(1명) 등의 정산 수치가 성공적으로 바인딩되었습니다.

### 5.3 기능별 테스트 결과

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI | 판정 |
|------|-----------|---------|---------|------|
| POS 정산내역 조회 | `/searchRegiList` | ✅ 구현 완료 | ✅ 데이터 정상 표시 | **PASS** |
| 정산 상세내역 조회 | `/searchRegiDetailList` | ✅ 구현 완료 | ✅ 상세 팝업 모달 출력 | **PASS** |

---

## 6. SQL Mapper 검증 (Oracle -> PostgreSQL 호환성)

### 6.1 Oracle (+) 외부조인 잔존 이슈

`Hq_Sales_00021_Sql.xml` 내 `searchRegiList` 쿼리에서 아래와 같이 Oracle 외부조인 표기법인 `(+)`가 여전히 사용되고 있습니다.

```sql
SELECT ...
  FROM hmsfns.SAREGITB SA
     , hmsfns.MMEMBSTB MM
     , hmsfns.MMEMBVTB MV
 WHERE SA.MS_NO = MM.MS_NO
   AND SA.MS_NO = MV.MS_NO(+)  -- ⚠️ Oracle 전용 외부조인 문법 잔존
```

- **영향도**: 개발 DB인 EDB PostgreSQL은 Oracle 호환 모드 기능이 내장되어 있어 본 쿼리가 정상 실행되지만, 향후 호환 기능이 없는 표준 PostgreSQL 환경으로 이전될 경우 **구문 오류(Syntax Error)**가 발생합니다.
- **개선 권고사항**: ANSI 표준 조인 문법인 `LEFT OUTER JOIN`으로 변경이 필요합니다.

---

## 7. 검증 항목 체크리스트

| [체크 항목] | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 어노테이션 | ✅ 정상 | rollbackFor에 Exception.class 포함 |
| MyBatis Mapper Interface ↔ XML 매핑 | ✅ 정상 | Mapper.java와 XML ID가 완벽히 일치 |
| 세션 로그인 강제 적용 | ✅ 정상 | 세션에서 chainNo를 가져와 타 체인 조회 차단 |
| 상세 내역 모달 데이터 수치 대조 | ✅ 정상 | DB 데이터와 모달 매핑 값 일치 확인 |
| Oracle (+) 외부조인 잔존 여부 | ⚠️ 잔존 | EDB PostgreSQL 환경에서 작동되나 리팩토링 권장 |

---

## 8. 발견된 이슈 및 권고사항

### 🔴 Critical (즉시 조치 필요)
- 없음

### 🟡 Warning (마이그레이션 및 이식성 관련)
1. **Oracle (+) 외부조인 구문 잔존**:
   - `Hq_Sales_00021_Sql.xml` L36 라인의 `MV.MS_NO(+)`는 표준 SQL이 아닙니다. 이식성을 높이기 위해 `LEFT OUTER JOIN` 구문으로 리팩토링할 것을 권고합니다.

---

## 9. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 및 레이아웃 | ✅ PASS |
| POS 정산내역 요약 조회 | ✅ PASS |
| POS별 정산 상세내역 조회 (모달) | ✅ PASS |
| **종합 판정** | **✅ PASS (EDB 환경 기준)** |

---

## 10. 첨부 (테스트 실행 증적 스크린샷)

````carousel
![조회 결과 화면](C:/Users/uoshj/.gemini/antigravity-ide/brain/fa617e6c-1b0e-4b1e-82ac-761085b03884/hq_sales_00021_search.png)
<!-- slide -->
![상세 팝업 모달 화면](C:/Users/uoshj/.gemini/antigravity-ide/brain/fa617e6c-1b0e-4b1e-82ac-761085b03884/hq_sales_00021_detail.png)
````

---
*본 리포트는 코드베이스 정적 분석 및 Playwright 브라우저 E2E 자동화 검증을 기반으로 작성되었습니다.*
