# Hq_Vendor_00018 — 월단위 원가율 현황 단위 테스트케이스

> **대상 화면**: [HQ] 매입발주 > 매입현황 > 월단위 원가율 현황 (`hq_vendor_00018`)  
> **API Base URL**: `POST /backoffice/data/hq/vendor/hq_vendor_00018`  
> **트랜잭션 설정**: `@Transactional(rollbackFor = {RuntimeException.class, Exception.class})` (SELECT 전용)  
> **데이터 수신 방식**: `@RequestBody Map<String, Object> commandMap` (전 엔드포인트 공통)  
> **DB 영향도**: 단순 데이터 조회 화면으로 CUD/트리거 연쇄 영향 없음 (Depth 3 Side Effect 없음)

---

## 1. 테스트 선행 및 세션 조건

| 세션 변수명 | 필요성 | 데이터 예시 | 비고 |
| :--- | :--- | :--- | :--- |
| `chainNo` | **필수** | `C001` (HMS F&B 체인) | 권한별 조회 필터의 기준 (Mapper 바인딩) |
| `ID` | **필수** | `shopadmin` | 본사 로그인 사용자 ID |

> [!WARNING]
> **권한 격리 주의**: 본 화면은 소속 체인의 데이터만 조회할 수 있습니다. 
> 예를 들어, `NC0003` 매장 데이터는 `C001` 권한 계정(`shopadmin`)으로만 조회 가능하며, 타 체인 계정(`shopadmin` 등)으로 조회 시 세션의 `chainNo` 불일치로 빈 결과가 리턴됩니다.

---

## 2. 엔드포인트 명세 및 쿼리 매핑

| # | URL 엔드포인트 | HTTP Method | 기능 요약 | 데이터 반환 | 연관 테이블 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| 1 | `/search` | POST | 월단위 원가율 현황 목록 조회 | `List<Hq_Vendor_00018_MonthUcostRateListDto>` | `STRNDTTB`, `TGOODSTB`, `MGOODSTB`, `IMMMIOTB`, `MMEMBSTB`, `MNAMEMTB` |

---

## 3. 소스코드 및 SQL 마이그레이션 호환성 체크리스트 (Warning 요소)

본 화면의 MyBatis Mapper [Hq_Vendor_00018_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/vendor/Hq_Vendor_00018_Sql.xml) 쿼리 내 오라클 전용 문법 검사항목입니다.

- [ ] **Oracle (+) 아우터 조인 식별**: `GD.MS_NO = RG.MS_NO(+)` $\rightarrow$ ANSI 표준인 `LEFT OUTER JOIN` 구문으로 교체 필요.
- [ ] **Oracle DECODE 함수 잔존**: `DECODE(RG.SALE_FG, 0, 1, -1)` $\rightarrow$ `CASE WHEN` 구문으로 변환 필요.
- [ ] **Oracle NVL 함수 잔존**: `NVL(SUM(DD.START_COST), 0)` $\rightarrow$ `COALESCE` 함수로 치환 필요.

---

## 4. 상세 테스트케이스 (Unit & E2E)

### 4.1 `/search` — 월단위 원가율 현황 조회

**파라미터**: `searchMonth` (조회월 YYYYMM, 필수), `msNo` (매장코드, 선택), `saleType` (매출유형코드, 선택)  
**RequestBody 예시**: `{"searchMonth":"202606","msNo":"NC0003","saleType":""}`

| TC ID | 테스트 시나리오 | 입력 데이터 (JSON Body) | 세션 조건 | 기대 결과 | 판정 기준 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-101** | 특정 월 전체 매장 조회 (정상) | `{"searchMonth":"202606","msNo":"","saleType":""}` | `chainNo="C001"` | HTTP 200, 2026년 6월 원가율 현황 목록 반환 | `List.size() > 0` |
| **TC-102** | 특정 매장 필터 조회 (정상) | `{"searchMonth":"202606","msNo":"NC0003","saleType":""}` | `chainNo="C001"` | 고양 Shop 매장의 원가율 집계 정보만 필터링 반환 | `msNo == "NC0003"` |
| **TC-103** | 특정 매출 유형 필터 조회 | `{"searchMonth":"202606","msNo":"","saleType":"01"}` | `chainNo="C001"` | 매출 유형이 `'01'`에 해당하는 상품군만 필터 집계 | `saleTypeCd == "01"` |
| **TC-104** | 실적 데이터 없는 월 조회 | `{"searchMonth":"199901","msNo":"","saleType":""}` | `chainNo="C001"` | HTTP 200, 빈 배열 반환 | `[]` 반환 |
| **TC-105** | 조회월 미지정 시 (UI 차단) | `{"searchMonth":"","msNo":"","saleType":""}` | `chainNo="C001"` | UI 단에서 '조회 월을 선택하여 주시기 바랍니다.' 얼럿 노출 | `bootbox.alert` 감지 |
| **TC-106** | 권한 외의 타 체인 조회 (차단) | `{"searchMonth":"202606","msNo":"","saleType":""}` | `chainNo='C001'` | `C001` 소속 매장의 실적이 집계에서 제외되어 빈 배열 반환 | `[]` 반환 |
| **TC-107** | 미인증 접근 시 | `{"searchMonth":"202606","msNo":"","saleType":""}` | 세션 없음 | HTTP 302 / 로그인 화면 리다이렉트 | 302 Redirect |
