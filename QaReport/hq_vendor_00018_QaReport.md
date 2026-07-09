# QA Report: Hq_Vendor_00018 월단위 원가율 현황

**작성일**: 2026-07-02  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 매입발주 > 매입현황 > 월단위 원가율 현황 (`hq_vendor_00018`)  
**테스트 환경**: localhost:8080 (로컬 개발 WAS)  
**접속ID/PW**: `shopadmin` / `0000` (FST_LOGIN_PW_CHANGE='Y', ACCT_ENABLE='Y')  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
| :--- | :--- |
| Controller | `backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/hq/vendor/Hq_Vendor_00018_Controller.java` |
| Service | `backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/hq/vendor/Hq_Vendor_00018_Service.java` |
| Mapper (Interface) | `backoffice/hyundai-backoffice-layer-persistence/src/main/java/com/hyundai/backoffice/webapp/dao/hq/vendor/Hq_Vendor_00018_Mapper.java` |
| SQL XML | `backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/vendor/Hq_Vendor_00018_Sql.xml` |
| DTO | `backoffice/hyundai-backoffice-layer-domain/src/main/java/com/hyundai/backoffice/webapp/dto/hq/vendor/Hq_Vendor_00018_MonthUcostRateListDto.java` |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/hq/vendor/hq_vendor_00018/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog |
| :--- | :--- | :--- | :--- |
| `/search` | POST | 월단위 원가율 현황 목록 조회 | SELECT |

---

## 3. 서비스 로직 및 DB 영향도 분석 (CUD / 트리거 무영향 검증)

### 3.1 CUD 발생 여부 검증
*   **분석 결과**: 본 화면은 가맹점의 재고 및 매출 실적 데이터를 조합하여 마진율 및 원가율을 모니터링하는 **단순 데이터 조회(Select-Only) 전용 화면**입니다.
*   소스코드 정적 분석 상 컨트롤러(`Hq_Vendor_00018_Controller`) 및 서비스(`Hq_Vendor_00018_Service`)에 `INSERT`, `UPDATE`, `DELETE`를 유발하는 어떠한 비즈니스 로직이나 메소드도 존재하지 않음을 확인했습니다.

### 3.2 DB 트리거 및 프로시저 영향성
*   DML 연산이 전혀 발생하지 않는 조회 화면이므로, 데이터베이스 상의 트리거 작동 및 프로시저 호출 연쇄 반응(Depth 3 등)이 발생하지 않아 **DB 마스터 데이터 및 가맹점 단말 정보에 미치는 사이드 이펙트는 전혀 없습니다.**

---

## 4. 데이터베이스 및 쿼리 흐름

### 4.1 데이터 집계 및 계산 흐름
```
 [STRNDTTB] (매출 데이터) ──┐
                            ├─► [Inline View RG] (월별/상품별 매출 합산) ──┐
 [TGOODSTB] (상품 마스터) ──┘                                              │
                                                                            ├─► [OUTER JOIN] ──► [원가율 산출 및 출력]
 [IMMMIOTB] (월간 수불) ────┐                                              │   (UCOST_RATE = MONTH_USE_COST / SALE_AMT)
                            ├─► [Inline View IM] (월별/상품별 수불 합산) ──┘
 [MGOODSTB] (가맹점 상품) ──┘
```

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 및 E2E 테스트 현황

| 항목 | 결과 |
| :--- | :--- |
| 서버 접속 URL | `http://localhost:8080` ✅ |
| 로그인 권한 | 성공 (`shopadmin` / `0000`, 체인 `C001`, 매장 `NC0002` 권한) ✅ |
| 화면 경로 | [HQ] 매입발주 > 매입현황 > 월단위 원가율 현황 ✅ |
| 화면 로딩 | 정상 로딩 및 조건부 레이아웃 표출 완료 ✅ |

### 5.2 E2E 시나리오 테스트 내역 및 결과
*   **조회 조건**:
    *   **조회일자**: `2026-06` (2026년 6월)
    *   **매장선택**: `[오픈] 고양 Shop` (`NC0003`)
    *   **매출 유형코드**: 전체
*   **테스트 결과**:
    *   조회 버튼 클릭 시 **총 6개의 그리드 로우**가 로드되며 정상 작동하는 것을 확인했습니다.
    *   가맹점 매장코드(`NC0003`) 및 매장명(`고양 Shop`), 입고합계, 당월재고, 사용 원가 및 매출액 수치가 정상적으로 집계 바인딩되었습니다.
    *   Bootstrap Table의 천단위 쉼표 표출기(`numberFormatter`) 및 하단 합계 라인이 정상적으로 마운트되었습니다.

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI | 판정 |
| :--- | :--- | :---: | :---: | :---: |
| 원가율 현황 조회 | `/search` | ✅ 구현 완료 | ✅ 데이터 표시 | **PASS** |

---

## 6. SQL Mapper 검증 및 오라클 호환성 체크

MyBatis Mapper XML 내의 쿼리에서 검출된 오라클 전용 구문 분석 결과입니다:

| 구분 | 쿼리 ID 및 코드 위치 | Legacy Oracle 문법 | PostgreSQL 전환 권고안 | 호환성 판정 |
| :--- | :--- | :--- | :--- | :---: |
| **(+) Outer Join** | `getList` (L93-96, L104, L106) | `GD.MS_NO = RG.MS_NO(+)`, `GD.GOODS_CD = IM.GOODS_CD(+)` | `LEFT OUTER JOIN` 표준 구문으로 쿼리 재설계 필요 | ⚠️ (EPAS 호환) |
| **DECODE** | `getList` (L24, L37) | `DECODE(SUM(RG.SALE_AMT), 0, NULL...)` | `CASE WHEN` 표준 조건 구문으로 변경 필요 | ⚠️ (EPAS 호환) |
| **NVL** | `getList` (L24, L62-68) | `NVL(SUM(DD.START_COST), 0)` | `COALESCE` 표준 함수로 치환 필요 | ⚠️ (EPAS 호환) |

> *참고*: 현재 개발 DB 환경은 **EDB Postgres Advanced Server (EPAS)**의 Oracle 호환성 레이어가 적용되어 있어 위 오라클 전용 쿼리들이 수정 없이 구동되나, 향후 순수 오픈소스 PostgreSQL로 전면 마이그레이션할 때에는 상기 권고안에 맞춰 ANSI SQL 형태로 변환해야 합니다.

---

## 7. 검증 항목 체크리스트

### 7.1 코드베이스 변환 정합성

| 검증 항목 | 상태 | 비고 |
| :--- | :--- | :--- |
| `@Service`, `@Transactional` 어노테이션 정의 | ✅ 정상 | 롤백 대상 클래스 지정 완료 |
| Controller ↔ Service ↔ Mapper 명세 일치 | ✅ 정상 | 데이터 전송 규격(DTO) 맵핑 일치 |
| `@ServiceLog` 어노테이션 누락 여부 | ✅ 정상 | `SEARCH` 로그 타입 지정 완료 |

---

## 8. 발견된 이슈 및 권고사항

### 🔴 Critical (즉시 처리 필요 결함)
*   **없음** (Select-Only 화면으로 예외 없음)

### 🟡 Warning (마이그레이션 시 변환 필요)
1.  **Oracle (+) 외부 조인 7건 잔존**: SQL XML 내 전체 조인 구조의 ANSI `LEFT OUTER JOIN` 표준화가 권장됩니다.
2.  **DECODE, NVL 함수 다수 사용**: 순수 PostgreSQL 드라이버 호환을 위해 `CASE WHEN`, `COALESCE` 구문으로 점진적 리팩토링이 필요합니다.

---

## 9. 종합 판정

| 구분 | 결과 |
| :--- | :--- |
| 화면 로딩 | ✅ PASS |
| 데이터 조회 기능 | ✅ PASS |
| CUD 및 사이드 이펙트 부재 | ✅ PASS (무영향 확인) |
| **종합 판정** | **✅ PASS** |

---

## 10. 첨부 (E2E 테스트 스크린샷)

*   **최초 화면 접속 (`hq_vendor_00018_initial.png`)**:
    ![최초접속](/C:/Users/uoshj/.gemini/antigravity-ide/brain/5b781763-17f9-44c1-92ff-e431cff8ecde/hq_vendor_00018_initial.png)
*   **조회 조건 입력 (`hq_vendor_00018_conditions.png`)**:
    ![조건설정](/C:/Users/uoshj/.gemini/antigravity-ide/brain/5b781763-17f9-44c1-92ff-e431cff8ecde/hq_vendor_00018_conditions.png)
*   **조회 결과 표출 (`hq_vendor_00018_results.png`)**:
    ![조회결과](/C:/Users/uoshj/.gemini/antigravity-ide/brain/5b781763-17f9-44c1-92ff-e431cff8ecde/hq_vendor_00018_results.png)

---
*본 리포트는 코드베이스 정적 분석 + Playwright E2E 브라우저 검증을 기반으로 작성되었습니다.*
