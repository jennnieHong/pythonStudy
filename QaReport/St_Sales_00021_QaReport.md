# QA Report: St_Sales_00021 매장 POS 정산내역
**작성일**: 2026-06-26  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: [매장] 매출분석 > POS > POS 정산내역 (st_sales_00021)  
**테스트 환경**: `http://localhost:8080` (로컬 개발 서버)  
**접속 ID/PW**: `shopbrand` / `0000` (화면별_접근가능_사용자_목록.xlsx 기준, ACCT_ENABLE='Y', FST_LOGIN_PW_CHANGE='Y')  

---

## 1. 분석 개요

본 화면은 개별 매장의 점주/직원 권한으로 당일 또는 특정 과거 일자의 POS 정산 내역 및 원장 데이터를 조회하고, 상세 내역을 팝업 형태로 확인하는 기능입니다. 세션의 매장 정보(`msNo`)가 백엔드 파라미터로 자동 주입되는 특징이 있습니다.

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `hyundai-backoffice-webapp/.../controller/st/sales/St_Sales_00021_Controller.java` |
| Service | `hyundai-backoffice-layer-service/.../service/st/sales/St_Sales_00021_Service.java` |
| Mapper (Interface) | `hyundai-backoffice-layer-persistence/.../dao/st/sales/St_Sales_00021_Mapper.java` |
| SQL XML | `hyundai-backoffice-webapp/.../sqlmapper/sales/St_Sales_00021_Sql.xml` |
| DTO | `hyundai-backoffice-layer-domain/.../dto/st/sales/St_Sales_00021_RegiListDto.java` |
| JSP | `hyundai-backoffice-webapp/.../st/sales/st_sales_00021/st_sales_00021.jsp` |
| JavaScript (메인) | `hyundai-backoffice-webapp/.../st/sales/st_sales_00021/js/st_sales_00021.js` |
| JavaScript (그리드) | `hyundai-backoffice-webapp/.../st/sales/st_sales_00021/js/st_sales_00021_bt.js` |
| JSP (모달) | `hyundai-backoffice-webapp/.../st/sales/st_sales_00021/modal/st_sales_00021_M01.jsp` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/st/sales/st_sales_00021
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog Type | 관련 테이블 |
|-----------|------|------|-----------------|-------------|
| `/searchRegiList` | POST | POS 정산 요약 목록 조회 (msNo 세션 주입) | `ServiceType.SELECT` | `SAREGITB`, `MMEMBSTB`, `MMEMBVTB` |
| `/searchRegiDetailList` | POST | POS 정산 상세 팝업 조회 | `ServiceType.SELECT` | `SAREGITB` |

---

## 3. 서비스 로직 및 DB 연쇄 분석 (코드베이스 변환 검증)

### 3.1 서비스 조회 흐름도 (SELECT 전용)

<div class="mermaid-wrapper" style="position: relative; margin-bottom: 20px;">
  <button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText); alert('Mermaid 코드가 복사되었습니다.');" style="position: absolute; right: 10px; top: 10px; z-index: 100; background: #2563EB; color: white; border: none; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">코드 복사</button>

```text
sequenceDiagram
    participant UI as Browser (st_sales_00021)
    participant Ctrl as St_Sales_00021_Controller
    participant Svc as St_Sales_00021_Service
    participant Mapper as St_Sales_00021_Mapper
    participant DB as Database (PostgreSQL/EDB)

    Note over UI, DB: 1. 매장 POS 정산 요약 목록 조회 (/searchRegiList)
    UI->>Ctrl: POST /searchRegiList (searchDate, msNo)
    Ctrl->>Svc: searchRegiList(commandMap)
    Svc->>Mapper: searchRegiList(map)
    Mapper->>DB: SELECT from SAREGITB & MMEMBSTB & MMEMBVTB (where msNo=#{msNo})
    DB-->>UI: Return List<St_Sales_00021_RegiListDto>

    Note over UI, DB: 2. 정산 상세내역 조회 (/searchRegiDetailList)
    UI->>Ctrl: POST /searchRegiDetailList (saleDate, msNo, posNo)
    Ctrl->>Svc: searchRegiDetailList(commandMap)
    Svc->>Mapper: searchRegiDetailList(map)
    Mapper->>DB: SELECT from SAREGITB (where msNo=#{msNo} and REGI_TYPE='0')
    DB-->>UI: Return Map<String, Object> (상세 금액 및 건수)
```

```mermaid
sequenceDiagram
    participant UI as Browser (st_sales_00021)
    participant Ctrl as St_Sales_00021_Controller
    participant Svc as St_Sales_00021_Service
    participant Mapper as St_Sales_00021_Mapper
    participant DB as Database (PostgreSQL/EDB)

    Note over UI, DB: 1. 매장 POS 정산 요약 목록 조회 (/searchRegiList)
    UI->>Ctrl: POST /searchRegiList (searchDate, msNo)
    Ctrl->>Svc: searchRegiList(commandMap)
    Svc->>Mapper: searchRegiList(map)
    Mapper->>DB: SELECT from SAREGITB & MMEMBSTB & MMEMBVTB (where msNo=#{msNo})
    DB-->>UI: Return List<St_Sales_00021_RegiListDto>

    Note over UI, DB: 2. 정산 상세내역 조회 (/searchRegiDetailList)
    UI->>Ctrl: POST /searchRegiDetailList (saleDate, msNo, posNo)
    Ctrl->>Svc: searchRegiDetailList(commandMap)
    Svc->>Mapper: searchRegiDetailList(map)
    Mapper->>DB: SELECT from SAREGITB (where msNo=#{msNo} and REGI_TYPE='0')
    DB-->>UI: Return Map<String, Object> (상세 금액 및 건수)
```
</div>

### 3.2 CUD 로직 및 트리거 영향도 검증
* **CUD 존재 여부**: **해당 없음** (본 화면은 단순 조회용 화면으로 CUD 로직이 일절 없음).
* **DB 트리거/프로시저 연쇄 반응**: **해당 없음** (조회 트랜잭션만 수행하므로 하위 트리거 동작 및 DB 이력 변동이 일어나지 않음).
* **numeric 형변환 결함 가능성**: **해당 없음** (CUD 작업이 존재하지 않아 numeric 필드에 빈 문자열이 전송될 여지가 없음).

---

## 4. SQL Mapper 검증

### 4.1 SQL 호환성 정적 검증

`St_Sales_00021_Sql.xml` 내의 `searchRegiList` 쿼리에 아래와 같이 **오라클 레거시 아우터 조인 표기법(`(+)`)이 잔존**하고 있습니다.

```xml
              FROM hmsfns.SAREGITB SA
                 , hmsfns.MMEMBSTB MM
                 , hmsfns.MMEMBVTB MV
             WHERE SA.MS_NO = MM.MS_NO
               AND SA.MS_NO = MV.MS_NO(+)
```

#### **[이슈 및 개선 방안]**
* **현재 상태**: EDB Oracle 호환 모드가 켜진 환경에서는 구문 오류 없이 정상적으로 실행됩니다.
* **마이그레이션 권고사항**: 순수 PostgreSQL 이행 시 해당 구문은 즉시 오류가 발생하므로, 표준 SQL `LEFT JOIN` 구문으로 다음과 같이 수정을 완료해야 합니다.

```sql
             FROM hmsfns.SAREGITB SA
             JOIN hmsfns.MMEMBSTB MM ON SA.MS_NO = MM.MS_NO
        LEFT JOIN hmsfns.MMEMBVTB MV ON SA.MS_NO = MV.MS_NO
            WHERE MM.CHAIN_NO  = #{chainNo}
              AND SA.SALE_DATE = #{searchDate}
              AND SA.MS_NO     = #{msNo}
```

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 계정 | 성공 (`shopbrand` / `0000`) ✅ |
| 화면 경로 | 매출분석 > POS > POS 정산내역 ✅ |
| 화면 로딩 | 정상 로딩 완료 ✅ |

### 5.2 기능별 E2E 테스트 검증 결과 (Playwright 자동화)

* **테스트 스크립트**: `D:\hmTest\backoffice\QaReport\test_st_sales_21.py`
* **테스트 결과 (100% PASS)**:
  * **[1] 로그인 및 페이지 진입**: `shopbrand` 계정으로 정상 로그인 완료 및 패스워드 만료 팝업 우회 확인.
  * **[2] 매장 POS 정산 목록 조회 (`/searchRegiList`)**: 
    * 조회 일자 `2026-06-02`을 선택 후 조회 버튼을 클릭하였습니다. (체인과 매장은 세션 정보에 의해 `C001` 및 `NC0003`으로 자동 필터링됨)
    * 그리드 테이블(`#st_sales_00021_t01`)에 POS `01`, 영수증 번호, 총매출액 등 정산 원장 레코드 1건이 성공적으로 로드되었습니다. ✅ **PASS**
  * **[3] 정산 상세내역 조회 (`/searchRegiDetailList`)**:
    * 그리드 내의 매장명 셀(`td.table-onclick`)을 클릭하여 상세 내역 모달(`#detailSearchModal`)이 정상 팝업되었습니다.
    * 모달 팝업 결과 카드매출, 부서비정산, 시재 현금 등의 금액 및 카운트 수치가 정확하게 표출되었습니다. ✅ **PASS**

---

## 6. 검증 항목 체크리스트

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@Service`, `@Transactional` 어노테이션 | ✅ 정상 | rollbackFor={RuntimeException.class, Exception.class} 적용 |
| `@Autowired` 매퍼 인터페이스 주입 | ✅ 정상 | `St_Sales_00021_Mapper` 주입 완료 |
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

## 8. 첨부 (테스트 실행 증적 스크린샷)

````carousel
![조회 결과 화면](C:/Users/uoshj/.gemini/antigravity-ide/brain/fa617e6c-1b0e-4b1e-82ac-761085b03884/st_sales_00021_search.png)
<!-- slide -->
![상세 팝업 모달 화면](C:/Users/uoshj/.gemini/antigravity-ide/brain/fa617e6c-1b0e-4b1e-82ac-761085b03884/st_sales_00021_detail.png)
````


---
*본 리포트는 소스코드 정적 분석 및 Playwright 브라우저 E2E 자동 테스트 수행 결과를 바탕으로 사실에 근거하여 신뢰성 있게 작성되었습니다.*
