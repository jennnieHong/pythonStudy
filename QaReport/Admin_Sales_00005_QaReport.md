# QA Report: Admin_Sales_00005 POS 정산내역
**작성일**: 2026-06-26  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: [ADMIN] 매출분석 > POS > POS 정산내역 (admin_sales_00005)  
**테스트 환경**: `http://localhost:8080` (로컬 개발 서버)  
**접속 ID/PW**: `admin2` / `0000` (화면별_접근가능_사용자_목록.xlsx 기준, ACCT_ENABLE='Y', FST_LOGIN_PW_CHANGE='Y')  

---

## 1. 분석 개요

본 화면은 어드민 시스템에서 각 체인의 매장별 POS 정산 정보 및 요약 데이터를 조회하고, 상세 내역을 팝업 형태로 확인하는 기능입니다. 

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/admin/sales/Admin_Sales_00005_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/admin/sales/Admin_Sales_00005_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/admin/sales/Admin_Sales_00005_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../sqlmapper/sales/Admin_Sales_00005_Sql.xml` |
| DTO | `hyundai-backoffice-layer-domain/.../dto/admin/sales/Admin_Sales_00005_RegiListDto.java` |
| JSP | `hyundai-backoffice-webapp/.../admin/sales/admin_sales_00005/admin_sales_00005.jsp` |
| JavaScript (메인) | `hyundai-backoffice-webapp/.../admin/sales/admin_sales_00005/js/admin_sales_00005.js` |
| JavaScript (그리드) | `hyundai-backoffice-webapp/.../admin/sales/admin_sales_00005/js/admin_sales_00005_bt.js` |
| JSP (모달) | `hyundai-backoffice-webapp/.../admin/sales/admin_sales_00005/modal/admin_sales_00005_M01.jsp` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/admin/sales/admin_sales_00005
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog Type | 관련 테이블 |
|-----------|------|------|-----------------|-------------|
| `/searchRegiList` | POST | POS 정산 요약 목록 조회 | `ServiceType.SELECT` | `SAREGITB`, `MMEMBSTB`, `MMEMBVTB` |
| `/searchRegiDetailList` | POST | POS 정산 상세 팝업 조회 | `ServiceType.SELECT` | `SAREGITB` |

---

## 3. 서비스 로직 및 DB 연쇄 분석 (코드베이스 변환 검증)

### 3.1 서비스 조회 흐름도 (SELECT 전용)

<div class="mermaid-wrapper" style="position: relative; margin-bottom: 20px;">
  <button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText); alert('Mermaid 코드가 복사되었습니다.');" style="position: absolute; right: 10px; top: 10px; z-index: 100; background: #2563EB; color: white; border: none; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">코드 복사</button>

```text
sequenceDiagram
    participant UI as Browser (admin_sales_00005)
    participant Ctrl as Admin_Sales_00005_Controller
    participant Svc as Admin_Sales_00005_Service
    participant Mapper as Admin_Sales_00005_Mapper
    participant DB as Database (PostgreSQL/EDB)

    Note over UI, DB: 1. POS 정산 요약 목록 조회 (/searchRegiList)
    UI->>Ctrl: POST /searchRegiList (chainNo, searchDate, msNo)
    Ctrl->>Svc: searchRegiList(commandMap)
    Svc->>Mapper: searchRegiList(map)
    Mapper->>DB: SELECT from SAREGITB & MMEMBSTB & MMEMBVTB
    DB-->>UI: Return List<Admin_Sales_00005_RegiListDto>

    Note over UI, DB: 2. 정산 상세내역 조회 (/searchRegiDetailList)
    UI->>Ctrl: POST /searchRegiDetailList (saleDate, msNo, posNo)
    Ctrl->>Svc: searchRegiDetailList(commandMap)
    Svc->>Mapper: searchRegiDetailList(map)
    Mapper->>DB: SELECT from SAREGITB (where REGI_TYPE='0')
    DB-->>UI: Return Map<String, Object> (상세 금액 및 건수)
```

```mermaid
sequenceDiagram
    participant UI as Browser (admin_sales_00005)
    participant Ctrl as Admin_Sales_00005_Controller
    participant Svc as Admin_Sales_00005_Service
    participant Mapper as Admin_Sales_00005_Mapper
    participant DB as Database (PostgreSQL/EDB)

    Note over UI, DB: 1. POS 정산 요약 목록 조회 (/searchRegiList)
    UI->>Ctrl: POST /searchRegiList (chainNo, searchDate, msNo)
    Ctrl->>Svc: searchRegiList(commandMap)
    Svc->>Mapper: searchRegiList(map)
    Mapper->>DB: SELECT from SAREGITB & MMEMBSTB & MMEMBVTB
    DB-->>UI: Return List<Admin_Sales_00005_RegiListDto>

    Note over UI, DB: 2. 정산 상세내역 조회 (/searchRegiDetailList)
    UI->>Ctrl: POST /searchRegiDetailList (saleDate, msNo, posNo)
    Ctrl->>Svc: searchRegiDetailList(commandMap)
    Svc->>Mapper: searchRegiDetailList(map)
    Mapper->>DB: SELECT from SAREGITB (where REGI_TYPE='0')
    DB-->>UI: Return Map<String, Object> (상세 금액 및 건수)
```
</div>

### 3.2 CUD 로직 및 트리거 영향도 검증
* **CUD 존재 여부**: **해당 없음** (본 화면은 단순 조회를 전용으로 하는 화면으로, 데이터의 삽입(INSERT), 수정(UPDATE), 삭제(DELETE) 로직이 전무함).
* **DB 트리거/프로시저 연쇄 반응**: **해당 없음** (조회 쿼리만 수행하므로 `pg_trigger` 또는 Oracle 마이그레이션 다운스트림 연동 대상 테이블에 영향을 주지 않음).
* **numeric 형변환 결함 가능성**: **해당 없음** (CUD가 수반되지 않으므로 empty string(`''`) 전송에 따른 numeric 변환 에러 유발 가능성이 존재하지 않음).

---

## 4. SQL Mapper 검증

### 4.1 SQL 호환성 정적 검증

`Admin_Sales_00005_Sql.xml` 내의 `searchRegiList` 쿼리에 아래와 같이 **오라클 레거시 아우터 조인 표기법(`(+)`)이 잔존**하고 있는 사실을 확인하였습니다.

```xml
              FROM hmsfns.SAREGITB SA
                 , hmsfns.MMEMBSTB MM
                 , hmsfns.MMEMBVTB MV
             WHERE SA.MS_NO = MM.MS_NO
               AND SA.MS_NO = MV.MS_NO(+)
```

#### **[이슈 및 개선 방안]**
* **현재 상태**: EDB(EnterpriseDB)의 Oracle 호환성 레이어가 적용되어 있어, 호환 모드로 인해 현재 쿼리 실행 시 에러가 발생하지 않고 조회가 정상 작동하고 있습니다.
* **마이그레이션 권고사항**: 향후 순수 PostgreSQL이나 호환 모드가 지원되지 않는 오픈소스 DB로 이관되는 경우, 해당 구문은 Syntax Error를 유발합니다. 따라서 아래와 같이 **ANSI 표준 `LEFT JOIN` 구문으로 리팩토링**할 것을 강력히 권장합니다.

```sql
             FROM hmsfns.SAREGITB SA
             JOIN hmsfns.MMEMBSTB MM ON SA.MS_NO = MM.MS_NO
        LEFT JOIN hmsfns.MMEMBVTB MV ON SA.MS_NO = MV.MS_NO
            WHERE SA.SALE_DATE = #{searchDate}
```

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 계정 | 성공 (`admin2` / `0000`) ✅ |
| 화면 경로 | 매출분석 > POS > POS 정산내역 ✅ |
| 화면 로딩 | 정상 로딩 및 조회 필터 활성화 완료 ✅ |

### 5.2 기능별 E2E 테스트 검증 결과 (Playwright 자동화)

* **테스트 스크립트**: `D:\hmTest\backoffice\QaReport\test_admin_sales_05.py`
* **테스트 결과 (100% PASS)**:
  * **[1] 로그인 및 페이지 진입**: `admin2` 계정으로 정상 로그인 후 비밀번호 만료 모달 차단 및 화면 로딩을 정상 수행하였습니다.
  * **[2] POS 정산 요약 목록 조회 (`/searchRegiList`)**: 
    * 조회 일자 `2026-06-02`, 체인 `C001`, 매장 `NC0003`을 지정하여 조회를 실행하였습니다.
    * 조회 완료 후 그리드(bootstrapTable)에 `MS_NM`="오픈 고양 Shop", `POS_NO`="01", `BILL_NO` 등 정산 데이터 1건이 정확하게 로딩되었습니다. ✅ **PASS**
  * **[3] 정산 상세내역 조회 (`/searchRegiDetailList`)**:
    * 그리드 내의 매장명 셀(`td.table-onclick`)을 클릭하여 상세 내역 모달(`#detailSearchModal`)을 성공적으로 팝업시켰습니다.
    * 모달 내에 총매출, 순매출, 카드매출, 시재 등 데이터가 정상 표출됨을 확인하였습니다. ✅ **PASS**

---

## 6. 검증 항목 체크리스트

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 어노테이션 | ✅ 정상 | rollbackFor={RuntimeException.class, Exception.class} 적용 |
| `@Autowired` 매퍼 인터페이스 주입 | ✅ 정상 | `Admin_Sales_00005_Mapper` 정상 연동 |
| `@ServiceLog` 로그 어노테이션 누락 여부 | ✅ 정상 | `/searchRegiList`, `/searchRegiDetailList` 모두 `SELECT`로 설정됨 |
| numeric 형변환 결함 여부 | ✅ 안전 | CUD 로직 미보유로 에러 위험 없음 |
| SQL 호환성 결함 여부 | ⚠️ 주의 | `searchRegiList`에 `(+)` 아우터 조인 잔존 (ANSI JOIN 변환 권장) |

---

## 7. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 | ✅ PASS |
| POS 정산 목록 조회 | ✅ PASS |
| 정산 상세 모달 조회 | ✅ PASS |
| SQL 호환성 | ⚠️ WARNING (Oracle 전용 구문 잔존) |
| **종합** | **✅ PASS (Oracle 호환 모드 기준)** |

---

## 8. 첨부

* **조회 결과 스크린샷**: [admin_sales_00005_search.png](file:///D:/hmTest/backoffice/QaReport/admin_sales_00005_search.png)
* **상세 모달 스크린샷**: [admin_sales_00005_detail.png](file:///D:/hmTest/backoffice/QaReport/admin_sales_00005_detail.png)

---
*본 리포트는 소스코드 정적 분석 및 Playwright 브라우저 E2E 자동 테스트 수행 결과를 바탕으로 사실에 근거하여 신뢰성 있게 작성되었습니다.*
