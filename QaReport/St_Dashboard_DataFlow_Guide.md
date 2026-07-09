# St_Dashboard 대시보드 (매장) 데이터 흐름 가이드
**작성일**: 2026-07-06  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: [ST] 대시보드 (st_dashboard)

본 문서는 매장 대시보드가 로드될 때 각 컴포넌트 간 데이터 이동(Data Flow) 및 관련 데이터베이스 테이블 구조를 도식화한 문서입니다.

---

## 1. 데이터 흐름도 (Data Flow Diagram)

매장 대시보드는 로그인 세션 정보의 `msNo`(가맹점 코드)를 통해 해당 가맹점의 매출 데이터만 격리 조회합니다.

```text
[1단계: 웹 컨트롤러] 로그인 세션 정보 파싱 (WebPageTransition.java)
  │
  ├─ 사용자 세션 ➔ chainNo = 'C001', msNo = 'NC0007' (로그인한 매장번호)
  ▼
[2단계: 서비스 비즈니스 로직] St_Dashboard_Service 호출
  │
  ├─ selectDailySalesData (해당 가맹점 금일 매출 요약 조회)
  ├─ selectGoodsRankData (해당 가맹점 금일 상위 판매 상품 순위 조회)
  └─ selectNoticeData (본사 등록 공지사항 중 전체/매장 대상 최신 5건 조회)
  ▼
[3단계: 데이터베이스 쿼리 수행] St_Dashboard_Sql.xml 호출
  │
  ├─ SDAILYTB (매출 일집계) ➔ WHERE MS_NO = #{msNo} (타 매장 데이터 격리)
  ├─ SDAILYTB + MGOODSTB ➔ WHERE MS_NO = #{msNo} 상품 판매 순위 5개 상품 조회
  └─ TNOTICETB (공지사항 마스터) ➔ 공지사항 최신 5건 조회
  ▼
[4단계: 뷰 렌더링] WebPageTransition.java가 mav 모델 전달 ➔ main.jsp 로드 ➔ st/dashboard.jsp 완성
```

---

## 2. 참조 데이터베이스 테이블 상세

### 2.1 SDAILYTB (매출 일집계 테이블)
* **목적**: 로그인한 개별 매장(`MS_NO = #{msNo}`)의 당일 매출 집계 원천 데이터.
* **사용 컬럼**:
  - `CHAIN_NO`: 체인 번호 (조회 조건)
  - `MS_NO`: 가맹점 번호 (매장별 격리 조회 필수 조건)
  - `SALE_DATE`: 영업 일자 (당일 일자 조회 조건)
  - `SALE_AMT`: 매출 금액 (합계 계산)
  - `NATIVE_CNT`, `FOREIGN_CNT`: 내장객수 (합계 계산)

### 2.2 MGOODSTB (상품 마스터 테이블)
* **목적**: 상품 판매 순위 리스트에서 상품코드의 상품명 매핑용.
* **사용 컬럼**:
  - `GOODS_CD`: 상품 코드
  - `GOODS_NM`: 상품명

### 2.3 TNOTICETB (공지사항 마스터 테이블)
* **목적**: 본사에서 작성한 최신 공지사항 연동.
* **사용 컬럼**:
  - `NOTICE_NO`: 공지 일련번호
  - `TITLE`: 공지사항 제목
  - `REG_DATE`: 등록 일자
