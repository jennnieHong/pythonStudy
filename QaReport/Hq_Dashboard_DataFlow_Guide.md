# Hq_Dashboard 대시보드 (본사) 데이터 흐름 가이드
**작성일**: 2026-07-06  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: [HQ] 대시보드 (hq_dashboard)

본 문서는 본사 대시보드가 로드될 때 각 컴포넌트 간 데이터 이동(Data Flow) 및 관련 데이터베이스 테이블 구조를 도식화한 문서입니다.

---

## 1. 데이터 흐름도 (Data Flow Diagram)

본사 대시보드는 로그인 세션 정보의 `chainNo`와 `msNo`를 기반으로 작동하며, 아래와 같은 순서로 데이터를 입출력합니다.

```text
[1단계: 웹 컨트롤러] 로그인 세션 정보 파싱 (WebPageTransition.java)
  │
  ├─ 사용자 세션 ➔ chainNo = 'C001', msNo = 'NC0002'
  ▼
[2단계: 서비스 비즈니스 로직] Hq_Dashboard_Service 호출
  │
  ├─ selectDailySalesData (금일 매출 요약 정보 조회)
  ├─ selectGoodsRankData (금일 상위 판매 상품 순위 조회)
  └─ selectNoticeData (본사 등록 공지사항 최신 5건 조회)
  ▼
[3단계: 데이터베이스 쿼리 수행] Hq_Dashboard_Sql.xml 호출
  │
  ├─ SDAILYTB (매출 일집계) ➔ 당일 매출액, 객수, 객단가 집계
  ├─ SDAILYTB + MGOODSTB ➔ 상품별 매출 순위 5개 상품 조회
  └─ TNOTICETB (공지사항 마스터) ➔ 공지사항 최신 5건 조회
  ▼
[4단계: 뷰 렌더링] WebPageTransition.java가 mav 모델 전달 ➔ main.jsp 로드 ➔ hq/dashboard.jsp 완성
```

---

## 2. 참조 데이터베이스 테이블 상세

### 2.1 SDAILYTB (매출 일집계 테이블)
* **목적**: 당일 매출액 추이 및 상품 판매 집계 데이터의 원천이 됩니다.
* **사용 컬럼**:
  - `CHAIN_NO`: 체인 번호 (조회 조건)
  - `SALE_DATE`: 영업 일자 (당일 일자 조회 조건)
  - `SALE_AMT`: 매출 금액 (합계 계산)
  - `NATIVE_CNT`, `FOREIGN_CNT`: 내장객수 (합계 계산)

### 2.2 MGOODSTB (상품 마스터 테이블)
* **목적**: 상품 판매 순위 리스트에서 상품 코드에 해당하는 한글 상품명을 매핑하기 위해 사용됩니다.
* **사용 컬럼**:
  - `GOODS_CD`: 상품 코드
  - `GOODS_NM`: 상품명

### 2.3 TNOTICETB (공지사항 마스터 테이블)
* **목적**: 대시보드 공지사항 알림판에 최신 공지 목록을 노출하기 위해 사용됩니다.
* **사용 컬럼**:
  - `NOTICE_NO`: 공지 일련번호
  - `TITLE`: 공지사항 제목
  - `REG_DATE`: 등록 일자
