# Hq_Dashboard 대시보드 (본사) 데이터 보정 가이드

본 문서는 본사 대시보드 화면에 다채롭고 아름다운 차트 및 지표 데이터를 로드하기 위해 데이터베이스에 수동으로 모의 데이터를 적재(INSERT/UPDATE)하는 방법과 쿼리를 설명합니다.

---

## 1. 대상 데이터베이스 테이블 및 목적

대시보드는 다음 5개 핵심 집계 테이블을 참조합니다.

1. **`SDAILYTB` (일매출집계)**: 금일 매출 카드(매출총액, 주문건수, 취소액) 및 지난주 대비 성장률 지표 로드.
2. **`SMONTHTB` (월매출집계)**: 올해 1월~12월까지의 월별 매출추이 꺾은선 그래프 및 매장 매출 TOP 5 순위 렌더링.
3. **`SGOODMTB` (상품월매출집계)**: 당월 상품 매출 순위 TOP 5(삼립단팥빵 등) 및 금액/수량 바인딩.
4. **`STRNBPTB` (블루멤버스결제)**: 결제수단별 매출 분포(도넛 차트) 내 블루멤버스 포인트 결제액 합산.
5. **`STRNCMTB` (임직원할인결제)**: 결제수단별 매출 분포(도넛 차트) 내 임직원 법인 할인 결제액 합산.

---

## 2. 모의 데이터 적재 SQL 스크립트

아래 SQL 스크립트를 데이터베이스 클라이언트(pgAdmin, DBeaver 등)에서 실행하여 모의 데이터를 주입할 수 있습니다. 
*(체인코드: `C001`, 오늘 날짜: `YYYYMMDD`, 이번 달: `YYYYMM` 형식으로 변환하여 사용)*

### 2.1 일매출 집계 데이터 적재 (`SDAILYTB`)
```sql
-- 금일 매출 데이터 (오늘 날짜가 '20260706'인 경우 예시)
INSERT INTO hmsfns.SDAILYTB (CHAIN_NO, CHAIN_AREA, MS_NO, SALE_DATE, SALE_AMT, BILL_CNT, CANCEL_CNT, CANCEL_TOT, NATIVE_CNT, FOREIGN_CNT)
VALUES 
('C001', '000', 'NC0002', '20260706', 5200000, 150, 5, 120000, 145, 5),
('C001', '000', 'NC0007', '20260706', 3800000, 120, 3, 80000, 115, 5),
('C001', '000', 'NC0005', '20260706', 2400000, 80, 2, 40000, 78, 2);

-- 지난주 대비 성장률용 데이터 (오늘-7일 날짜가 '20260629'인 경우 예시)
INSERT INTO hmsfns.SDAILYTB (CHAIN_NO, CHAIN_AREA, MS_NO, SALE_DATE, SALE_AMT, BILL_CNT, CANCEL_CNT, CANCEL_TOT, NATIVE_CNT, FOREIGN_CNT)
VALUES 
('C001', '000', 'NC0002', '20260629', 4800000, 140, 4, 100000, 136, 4),
('C001', '000', 'NC0007', '20260629', 3500000, 110, 2, 60000, 108, 2),
('C001', '000', 'NC0005', '20260629', 2200000, 75, 2, 30000, 73, 2);
```

### 2.2 연간 월매출 데이터 적재 (`SMONTHTB`)
1월부터 12월까지 순차적으로 증가하는 연간 매출 추이용 데이터입니다.
```sql
-- NC0007 매장의 2026년 1월 ~ 12월 예시 데이터
INSERT INTO hmsfns.SMONTHTB (CHAIN_NO, CHAIN_AREA, MS_NO, SALE_MM, SALE_AMT, CASH_AMT, CARD_AMT)
VALUES 
('C001', '000', 'NC0007', '202601', 10000000, 3000000, 7000000),
('C001', '000', 'NC0007', '202602', 12000000, 3600000, 8400000),
('C001', '000', 'NC0007', '202603', 15000000, 4500000, 10500000),
('C001', '000', 'NC0007', '202604', 18000000, 5400000, 12600000),
('C001', '000', 'NC0007', '202605', 22000000, 6600000, 15400000),
('C001', '000', 'NC0007', '202606', 25000000, 7500000, 17500000),
('C001', '000', 'NC0007', '202607', 28000000, 8400000, 19600000),
('C001', '000', 'NC0007', '202608', 30000000, 9000000, 21000000),
('C001', '000', 'NC0007', '202609', 27000000, 8100000, 18900000),
('C001', '000', 'NC0007', '202610', 29000000, 8700000, 20300000),
('C001', '000', 'NC0007', '202611', 31000000, 9300000, 21700000),
('C001', '000', 'NC0007', '202612', 35000000, 10500000, 24500000);
```

### 2.3 당월 인기 상품 TOP 5 적재 (`SGOODMTB`)
```sql
-- 이번달이 2026년 7월('202607')인 경우 예시
INSERT INTO hmsfns.SGOODMTB (CHAIN_NO, CHAIN_AREA, MS_NO, SALE_MM, GOODS_CD, LCLASS_CD, MCLASS_CD, SCLASS_CD, SALE_AMT, SALE_QTY)
VALUES 
('C001', '000', 'NC0007', '202607', 'T0000011', '100', '101', '102', 12000000, 1500),
('C001', '000', 'NC0007', '202607', 'T0000555', '100', '101', '102', 8500000, 1100),
('C001', '000', 'NC0007', '202607', 'T0000291', '100', '101', '102', 6200000, 450),
('C001', '000', 'NC0007', '202607', 'T0000292', '100', '101', '102', 4800000, 320),
('C001', '000', 'NC0007', '202607', 'T0000293', '100', '101', '102', 3100000, 210);
```

### 2.4 블루멤버스 및 임직원 할인 트랜잭션 적재 (`STRNBPTB`, `STRNCMTB`)
```sql
-- 블루멤버스 실 결제금액 (250,000원)
INSERT INTO hmsfns.STRNBPTB (CHAIN_NO, MS_NO, SALE_DATE, BILL_NO, POS_NO, BP_SEQ, SALE_FG, TYPE_FG, BLUE_POINT_NO, BLUE_USE_AMT, BLUE_SAVE_AMT, BLUE_SAVE_POINT, BLUE_AFTER_AMT, APPR_NO, APPR_DATE, SALE_VAT, TRADE_SERIAL_NO, BLUE_CHECK_NO)
VALUES ('C001', 'NC0007', '20260706', '0001', '01', '01', '0', '1', '1234567890', 250000, 0, 0, 0, '999999', '20260706', 0, 'ABC123XYZ', '9999');

-- 임직원 할인 금액 (180,000원)
INSERT INTO hmsfns.STRNCMTB (CHAIN_NO, MS_NO, SALE_DATE, BILL_NO, POS_NO, SALE_FG, CM_SEQ, COMP_CD, COMP_NM, COMP_DC_RATE, COMP_DC_AMT, EMP_NO)
VALUES ('C001', 'NC0007', '20260706', '0001', '01', '0', '01', '001', 'TEST_COMP', '10', 180000, 'EMP001');
```

### 2.5 상품 마스터 테이블 적재 (`TGOODSTB` 및 `MGOODSTB`)
* **목적**: 대시보드의 상품 판매 순위 쿼리는 본사 상품 마스터(`TGOODSTB`)의 한글 상품명(`GOODS_NM`)을 매핑합니다. (또한 가맹점 상품 마스터인 `MGOODSTB`에도 매핑 등록이 필요합니다.)
* **설명**: 기본 마스터 데이터이므로 기존에 적재된 상품 코드를 사용하는 것이 권장되나, 만약 신규 테스트용 상품을 등록하여 대시보드에 노출시키고자 하는 경우에는 아래와 같이 두 마스터 테이블에 데이터를 주입해야 합니다.
```sql
-- 1. 본사 상품 마스터 (TGOODSTB) 등록
INSERT INTO hmsfns.TGOODSTB (CHAIN_NO, GOODS_CD, GOODS_NM, LCLASS_CD, MCLASS_CD, SCLASS_CD, UPRICE, USUPRICE, TAX_FG, USE_FG, CREATE_FG, CREATE_DTIME, CREATE_ID, LAST_DTIME, LAST_ID)
VALUES ('C001', 'T9999999', '대시보드테스트상품', '100', '101', '102', 5000, 4500, '1', 'Y', '1', '20260706120000', 'admin', '20260706120000', 'admin');

-- 2. 가맹점 상품 마스터 (MGOODSTB) 등록 (NC0007 매장 예시)
INSERT INTO hmsfns.MGOODSTB (MS_NO, GOODS_CD, GOODS_NM, LCLASS_CD, MCLASS_CD, SCLASS_CD, UPRICE, USUPRICE, UCOST, TAX_FG, GOODS_PRICE_FG, GOODS_CONTROL_FG, USE_FG, SET_FG, SERVICE_FG, ORD_UNIT, IN_QTY, INV_UNIT, INV_IN_QTY, GOODS_UNIT, MIN_ORD_QTY, GOODS_POINT, SAFETY_QTY, GOODS_USE_FG, TAX_CONTROL_FG, GOODS_TYPE, CREATE_FG, CREATE_DTIME, CREATE_ID, LAST_DTIME, LAST_ID, FICTITIOUS_YN, SUPPLY_YN, USUPRICE_VAT, FICTITIOUS_TAX, STORE_STOCK_YN, STORE_STOCK_UCOST, GOODS_DC_FG, UCOST_RATE)
VALUES ('NC0007', 'T9999999', '대시보드테스트상품', '100', '101', '102', 5000, 4500, 4000, '1', '1', '1', 'Y', 'N', 'N', 'EA', 1, 'EA', 1, 1, 1, 0, 0, 'Y', '1', '1', '1', '20260706120000', 'admin', '20260706120000', 'admin', 'N', 'Y', 4950, 0, 'N', 0, '1', 0);
```

### 2.6 공지사항 마스터 테이블 적재 (`BBSNTCTB`)
* **목적**: 대시보드 우측 영역의 공지사항 최신 알림판에 노출되는 데이터의 원천입니다. (시스템에 `TNOTICETB`라는 테이블은 존재하지 않으며, 실제 공지사항 테이블명은 **`BBSNTCTB`**입니다.)
* **설명**: 공지사항 제목(`TITLE`), 작성자(`NAME`), 내용(`CONTENT`), 노출기간(`FROM_DATE` ~ `TO_DATE`) 등을 아래와 같이 주입하면 대시보드에 즉각 연동됩니다.
```sql
INSERT INTO hmsfns.BBSNTCTB (
    IDX, HITS, CONFIRM_FG, TO_FG, FROM_DATE, TO_DATE, R_CHAIN_NO, R_MS_NO, 
    USER_ID, NAME, TITLE, CONTENT, CREATE_DTIME, CREATE_ID, LAST_DTIME, LAST_ID
)
VALUES (
    9999, 0, '1', 'C', '20260701', '20261231', 'C001', NULL,
    'shopadmin', '본사관리자', '대시보드 연동 긴급 공지사항', '본사 대시보드 데이터 연동 테스트 공지입니다.',
    '20260706120000', 'shopadmin', '20260706120000', 'shopadmin'
);
```

---

## 3. UI 화면에서 순차적으로 데이터를 처리하는 방법 및 연동 트리거/프로시저

직접 DB에 SQL을 날리지 않고 **HMS 영업정보시스템의 UI 화면**을 통해 대시보드 데이터를 최종적으로 가공 및 생성(마감)하려는 경우, 아래 순서대로 화면을 거쳐야 하며 각 단계에서 백엔드 트리거 및 프로시저가 연동됩니다.

```text
[1단계: POS 또는 연동 수신] 개별 매출 거래 데이터 적재
  └─ 데이터: POS 매출이 수신되면 STRNBPTB(블루멤버스), STRNCMTB(할인) 등 개별 트랜잭션 테이블에 입력됨
        ▼
[2단계: 본사 일마감 처리] 일 매출 데이터를 SDAILYTB에 요약 적재
  └─ 화면: [HQ] 시스템인터페이스 > 일마감 (hq_sysif_00003)
  └─ 연동 프로시저: SUB_SNETDT_P
  └─ 설명: 해당 화면에서 대상 영업일자를 선택하고 [마감실행]을 클릭하면, SUB_SNETDT_P 프로시저가 호출되어 
            당일의 개별 거래 내역을 모두 합산해 SDAILYTB(일매출집계) 테이블에 요약 로우(Row)를 자동 생성(INSERT)합니다.
        ▼
[3단계: 본사 월마감 처리] 월 매출 및 상품 판매 순위 데이터 생성
  └─ 화면: [HQ] 시스템인터페이스 > 월마감 (hq_sysif_00005)
  └─ 연동 프로시저: P_MACOST_B 및 월마감 전용 프로시저
  └─ 설명: 대상 월을 선택하고 [월마감실행]을 클릭하면, SDAILYTB의 일일 집계 데이터를 한 달 치로 병합하여 
            SMONTHTB(월매출집계) 및 SGOODMTB(상품월매출집계) 테이블에 데이터를 자동 생성합니다.
```

### 3.1 대시보드 지표별 테이블 및 UI 등록 화면 매핑 정보

| 대시보드 표시 영역 | 대상 데이터베이스 테이블 | UI 데이터 생성/등록 화면 경로 |
| :--- | :--- | :--- |
| **당일 매출 현황 카드**<br>(당일 매출액, 주문 건수, 취소액) | `SDAILYTB` (일매출집계)<br>`STRNBPTB` / `STRNCMTB` | **[본사] 시스템인터페이스 > 일마감** ([hq_sysif_00003](file:///D:/hmTest/backoffice/QaReport/All_HMS_Screens.html)) 에서 일마감 실행 시 집계<br>*(원천 거래는 POS 결제 수신 시 적재)* |
| **연간 월별 매출 추이 차트** | `SMONTHTB` (월매출집계) | **[본사] 시스템인터페이스 > 월마감** ([hq_sysif_00005](file:///D:/hmTest/backoffice/QaReport/All_HMS_Screens.html)) 에서 월마감 실행 시 집계 |
| **상위 판매 상품 TOP 5 목록** | `SGOODMTB` (상품월매출집계)<br>`TGOODSTB` (본사상품마스터)<br>`MGOODSTB` (매장상품마스터) | 1. **[본사] 마스터관리 > 상품관리 > 상품 등록/조회** ([hq_master_00006](file:///D:/hmTest/backoffice/QaReport/All_HMS_Screens.html)) 에서 마스터 등록<br>2. **[본사] 시스템인터페이스 > 월마감** ([hq_sysif_00005](file:///D:/hmTest/backoffice/QaReport/All_HMS_Screens.html)) 실행 시 판매 수량/금액 집계 |
| **결제수단별 매출 분포 차트** | `STRNBPTB` (블루포인트 내역)<br>`STRNCMTB` (임직원할인 내역) | 가맹점 POS 기기에서 블루멤버스 포인트 결제 및 임직원 사원인증 할인 결제 시 실시간 인터페이스 자동 수신 적재 |
| **최신 공지사항 알림판** | `BBSNTCTB` (공지사항 테이블) | **[본사] 커뮤니케이션 > 공지사항 > 공지사항 등록 관리** ([hq_commu_00002](file:///D:/hmTest/backoffice/QaReport/All_HMS_Screens.html)) 에서 신규 공지 등록 시 즉각 반영 |

---

## 4. 본사(HQ) vs 매장(ST) 대시보드 데이터 조회 범위 차이점

두 대시보드는 **조회하는 대상 물리 테이블(Table Schema) 목록이 100% 동일**하지만, 권한에 따른 **필터 조건(Where clause) 및 집계의 범위**에 아래와 같은 차이가 존재합니다.

1. **조회 필터 기준**:
   * **본사(HQ) 대시보드**: 로그인 사용자 정보에 할당된 체인 번호(`CHAIN_NO = #{chainNo}`)를 기준으로 조회하여 체인 전체 가맹점의 데이터를 조회/합산합니다.
   * **매장(ST) 대시보드**: 로그인 사용자 정보에 할당된 고유 매장 번호(`MS_NO = #{msNo}`)를 기준으로 필터링하여 오직 해당 매장의 단일 실적 데이터만 조회합니다.
2. **화면 지표 표현 범위**:
   * **당일/연간/상품 매출**: 본사는 소속 매장 전체의 누적 합산값(`SUM()`)을 보여주는 반면, 매장 대시보드는 본인 매장의 순수 실적만 표현됩니다.
3. **추가/제외 컴포넌트**:
   * **매장 매출 TOP 5 순위**: 본사 대시보드에만 표출되는 영역으로, 동일한 `SMONTHTB` 테이블에서 체인 전체 매장을 매출액 내림차순 정렬하여 상위 5개를 출력합니다. (매장 대시보드에는 본인 매장 정보만 보므로 해당 순위표가 노출되지 않습니다.)


