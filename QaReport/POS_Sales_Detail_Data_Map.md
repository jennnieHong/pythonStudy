# POS 정산 데이터 명세 및 매핑 가이드 (POS Settlement Data Dictionary)

본 문서는 POS 정산내역 조회 화면(`st_sales_00021`, `hq_sales_00021`, `admin_sales_00005`)에서 사용되는 **그리드 요약 데이터**와 **팝업 상세 데이터**의 데이터베이스 칼럼 매핑 규칙, 세부 산출식, 비즈니스 의미를 상세히 기술합니다.

---

## 1. 개요 및 대상 테이블

POS 정산과 관련된 모든 거래 집계 및 시재 정보는 `hmsfns.SAREGITB` (POS 정산 마스터 테이블)에 1일 1개 POS당 1개의 레코드로 적재됩니다.

### 1.1 주요 대상 테이블

* **`hmsfns.SAREGITB` (POS 정산 테이블)**: 판매일자, 매장번호, POS번호별로 마감 시점의 매출 총액, 반품액, 할인구분별 금액, 결제 수단별 금액, 시재 권종 수량 및 금액 정보를 기록합니다.
* **`hmsfns.MMEMBSTB` (매장 마스터 테이블)**: 매장코드(`MS_NO`)에 대응하는 매장 한글 명칭(`MS_NM`) 및 소속 체인 번호(`CHAIN_NO`)를 참조합니다.
* **`hmsfns.MMEMBVTB` (매장 부가세 설정 테이블)**: 매장의 부가세 과세구분(`VAT_FG`) 정보를 참조합니다.

---

## 2. 쿼리 로직 구조 비교

그리드 목록을 불러오는 쿼리(`searchRegiList`)와 팝업 내역을 불러오는 쿼리(`searchRegiDetailList`)는 데이터의 필터 범위와 조인 여부에서 큰 차이가 있습니다.

### 2.1 메인 그리드 조회 쿼리 (`searchRegiList`)
* **목적**: 특정 날짜의 체인/매장 산하 모든 POS의 정산 요약을 그리드 리스트 형태로 다중 조회
* **조인(Join)**: 3개 테이블 조인 (`SAREGITB` ⟝ `MMEMBSTB` ⟝ `MMEMBVTB`)
* **필터 조건**:
  ```sql
  WHERE SA.MS_NO = MM.MS_NO
    AND SA.MS_NO = MV.MS_NO(+)  -- Oracle 아우터 조인 사용
    AND MM.CHAIN_NO  = #{chainNo}
    AND SA.SALE_DATE = #{searchDate}
    -- 매장 사용자 화면은 세션 msNo 강제 적용, 본사/어드민은 선택 파라미터 적용
  ```

### 2.2 팝업 상세 조회 쿼리 (`searchRegiDetailList`)
* **목적**: 특정 일자, 특정 매장의 특정 POS 1대에 대한 상세 정산 시재 명세를 단일 건 조회
* **조인(Join)**: 없음 (`SAREGITB` 단일 테이블 조회)
* **필터 조건**:
  ```sql
  WHERE MS_NO     = #{msNo} 
    AND SALE_DATE = #{saleDate}
    AND POS_NO    = #{posNo}
    AND REGI_TYPE = '0'  -- '0' (일반 포스 마감 정산 데이터만 추출)
  ```

---

## 3. 데이터 매핑 및 산식 명세 (그리드 vs 팝업)

> [!NOTE]
> 팝업 매핑 상세 표 내의 **슬래시(`/`) 기호는 금액 정보와 건수(수량) 정보를 구분하는 구분자**입니다. (산술 연산인 나누기를 의미하지 않습니다.)
> * 예: `detailCancelTot / Cnt` -> 금액 매핑 ID: `detailCancelTot` / 건수 매핑 ID: `detailCancelCnt`
> * 예: `CANCEL_TOT / CANCEL_TOT_CNT` -> 금액 SQL: `CANCEL_TOT` / 건수 SQL: `CANCEL_TOT_CNT`

### 3.1 메인 그리드 칼럼 매핑 명세

| 화면 컬럼명 | DTO 필드명 | DB 추출 SQL 및 산출식 | 설명 |
| :--- | :--- | :--- | :--- |
| **No** | (순번) | `row_number()` / bootstrapTable auto-number | 그리드 순번 |
| **매장** | `msNm` | `MM.MS_NM` | 조인된 매장 마스터 한글 명칭 |
| **POS** | `posNo` | `SA.POS_NO` | POS 번호 (예: '01') |
| **영수증** | `billNo` | `SA.BILL_NO` | 해당 POS에서 마지막으로 발행된 영수증 일련번호 |
| **손님수** | `custTot` | `(SA.NATION_AMT_CNT + SA.FOREIGN_AMT_CNT)` | 내국인 영수건수 + 외국인 영수건수 (총 고객수) |
| **총매출** | `saleTot` | `SA.SALE_TOT` | 총 판매 금액 (할인 전 금액) |
| **부가세** | `addedTax` | `SA.ADDED_TAX` | 매출 발생 총 부가세액 |
| **순매출** | `saleAmt` | `SA.SALE_AMT` | 총 매출액에서 에누리/반품이 조율된 결제 기준 순매출 |
| **현금매출** | `cashAmt` | `SA.CASH_AMT` | 현금 결제수단 금액 |
| **카드매출** | `cardAmt` | `((SA.CARD_AMT1-SA.CARD_AMT3) + (SA.CARD_AMT2-SA.CARD_AMT4))` | (일시불 정상 - 일시불 취소) + (할부 정상 - 할부 취소) |
| **블루포인트** | `bluePointUseAmt`| `SA.BLUE_POINT_USE_AMT` | 현대 블루멤버스 포인트 사용금액 |
| **할인** | `dcAmt` | `SA.DC_AMT` | 쿠폰, 제휴, 프로모션 등을 포함한 총 할인 합계액 |
| **반품** | `cancelTot` | `SA.CANCEL_TOT` | 당일 취소/반품 처리된 총 누적 금액 |
| **현금과부족** | `cashLoss` | `SA.CASH_LOSS` | 전산 현금잔액과 실제 금고 시재 차이 금액 |
| **기타** | `etcAmt` | `SA.DEPARTMENT_AMT + SA.INVOICE_NEW_AMT + SA.PLAY_AMT + SA.CANCEL_AMT` | 부서비 + 세금계산서 청구액 + 교구매출액 + 외상액 합산 |

---

### 3.2 팝업 상세 내역 탭별 세부 매핑 (Exhaustive Map)

#### [탭 1] 전체 매출 내역 (All Sales Summary)

| 화면 항목 | 매핑 ID (금액 / 건수) | SQL SELECT 표현식 (금액 / 건수) | 데이터 형식 | 산출 논리 및 특이사항 |
| :--- | :--- | :--- | :--- | :--- |
| **총매출액** | `detailTotAmt` | `TOT_AMT` | Numeric(12,2) | 매출 총합 (할인 적용 전 원시 금액) |
| **반품매출액** | `detailCancelTot / Cnt` | `CANCEL_TOT / CANCEL_TOT_CNT` | Numeric / Int | 반품(환불) 총액 및 건수 |
| **반품할인매출액**| `detailCancelDcTot / Cnt` | `ETC_1 / ETC_1_CNT` | Numeric / Int | 반품 취소 시 같이 복원된 할인 금액/건수 |
| **총 매출액** | `detailSaleTot / Cnt` | `SALE_TOT / SALE_TOT_CNT` | Numeric / Int | 반품 처리가 차감된 실 판매 총액 및 건수 |
| **할인금액** | `detailDcAmt / Cnt` | `DC_AMT / DC_AMT_CNT` | Numeric / Int | 전체 할인 합계액 및 건수 |
| **통합쿠폰** | `detailCouponDcAmt` | `COUPON_DC_AMT` | Numeric(12,2) | 쿠폰 할인 금액 |
| **임직원** | `detailEmpDcAmt` | `EMP_DC_AMT` | Numeric(12,2) | 임직원 특별 할인 금액 |
| **프로모션** | `detailNormDcAmt` | `REGULAR_DC_AMT` | Numeric(12,2) | 프로모션/행사 할인 금액 |
| **제휴할인** | `detailAfcardDcAmt` | `AFCARD_DC_AMT` | Numeric(12,2) | 카드사 및 통신사 제휴 할인 금액 |
| **순매출액** | `detailSaleAmt` | `SALE_AMT` | Numeric(12,2) | 최종 정산 기준 순매출액 |
| **NET 매출액** | `detailNetAmt` | `ROUND((SALE_AMT/1.1))` | Numeric(12,0) | 순매출액에서 부가세를 제외한 공급가액 (1.1 나눈 후 반올림) |
| **부가세** | `detailAddedTax` | `ADDED_TAX` | Numeric(12,2) | 순매출액에 포함된 부과세 |
| **현금 잔액** | `detailTotSaleAmt` | `CASH_AMT + PRE_AMT + DEPOSIT_AMT + CASH_PAY - PAY_AMT + GIFT_CANCEL_TOT` | Numeric(12,2) | **[시재 공식]** 현금매출액 + 준비금 + 예치금입금액 + 외상입금 - 영업중지출액 + 상품권환불액 |

#### [탭 2] 순 매출 내역 (Net Sales Details)

| 화면 항목 | 매핑 ID (금액 / 건수) | SQL SELECT 표현식 (금액 / 건수) | 데이터 형식 | 산출 논리 및 특이사항 |
| :--- | :--- | :--- | :--- | :--- |
| **현금매출액** | `detailCashAmt` | `CASH_AMT` | Numeric(12,2) | 순수 현금 수납액 |
| **카드(일시불)** | `detailOneCardAmt / Cnt` | `(CARD_AMT1 - CARD_AMT3) / (CARD_AMT1_CNT - CARD_AMT3_CNT)` | Numeric / Int | 일시불 신용카드 결제 (정상승인액 - 승인취소액) |
| **카드(할부)** | `detailParCardAmt / Cnt` | `(CARD_AMT2 - CARD_AMT4) / (CARD_AMT2_CNT - CARD_AMT4_CNT)` | Numeric / Int | 할부 신용카드 결제 (할부승인액 - 승인취소액) |
| **세금계산서** | `detailInvoiceAmt / Cnt` | `INVOICE_NEW_AMT / INVOICE_NEW_CNT` | Numeric / Int | 매출 증빙용 세금계산서 발행액 및 건수 |
| **부서비** | `detailDeptAmt / Cnt` | `DEPARTMENT_AMT / DEPARTMENT_CNT` | Numeric / Int | 부서 운영비 카드 사용액 및 건수 |
| **교구매출** | `detailPlayAmt / Cnt` | `PLAY_AMT / PLAY_CNT` | Numeric / Int | 티켓 및 체험 교구 판매액 및 건수 |
| **블루포인트** | `detailBluePointUseAmt / Cnt` | `BLUE_POINT_USE_AMT / BLUE_POINT_USE_CNT` | Numeric / Int | 현대 블루멤버스 포인트 결제액 및 건수 |
| **외상** | `detailWeasAmt / Cnt` | `CANCEL_AMT / CANCEL_AMT_CNT` | Numeric / Int | **[칼럼 특이사항]** 외상 매출 데이터는 DB 상 `CANCEL_AMT` 칼럼에 로깅됨 |
| **Gift카드** | `detailGiftCardAmt / Cnt` | `HD_GIFT_CARD_AMT / HD_GIFT_CARD_CNT` | Numeric / Int | 자사 발행 기프트 카드 사용 결제 정보 |
| **멤버십카드** | `detailMembershipCardAmt / Cnt`| `HD_MEM_GIFT_CARD_AMT / HD_MEM_GIFT_CARD_CNT`| Numeric / Int | 자사 멤버십 적립 카드 사용 결제 정보 |
| **현금 시재** | `detailCloseStock` | `CLOSE_STOCK` | Numeric(12,2) | 최종 영업 마감 후 금고에 보관된 실물 현금 총합 |

#### [탭 3] 매출 외 현금 내역 및 기타사항 (Non-Sales & Others)

| 화면 항목 | 매핑 ID (금액(수량) / 건수) | SQL SELECT 표현식 (금액(수량) / 건수) | 데이터 형식 | 산출 논리 및 특이사항 |
| :--- | :--- | :--- | :--- | :--- |
| **영업중 입/출금**| `detailInputOutput` | `(DEPOSIT_AMT - PAY_AMT)` | Numeric(12,2) | 영업 시간 내 수동 입출금 처리의 누적 차액 |
| **입금액** | `detailDepositAmt` | `DEPOSIT_AMT` | Numeric(12,2) | 금고 현금 추가 입금 (예: 환전액 보충) |
| **출금액** | `detailPayAmt` | `PAY_AMT` | Numeric(12,2) | 현금 지출 (예: 소모품 직접 구매 등) |
| **준비금** | `detailPreAmt` | `PRE_AMT` | Numeric(12,2) | POS 오픈 시 기본 셋팅된 거스름돈용 준비금 |
| **Gift카드환불액**| `detailGiftCardRefAmt` | `HD_GIFT_CARD_REFUND_AMT` | Numeric(12,2) | 기프트카드 사용 취소/잔액 환불 총액 |
| **멤버십카드환불액**| `detailMembershipCardRefAmt` | `HD_MEM_GIFT_CARD_REFUND_AMT` | Numeric(12,2) | 멤버십카드 사용 취소/잔액 환불 총액 |
| **자사카드 임의등록**| `detailTmpCardAmt1 / Cnt` | `TMP_CARD_AMT1 / TMP_CARD_AMT1_CNT` | Numeric / Int | VAN사 통신 장애 시 임의 키인 등록 카드 정보 |
| **타사카드 임의등록**| `detailTmpCardAmt2 / Cnt` | `TMP_CARD_AMT2 / TMP_CARD_AMT2_CNT` | Numeric / Int | VAN사 통신 장애 시 임의 키인 등록 카드 정보 |
| **총 고객수** | `detailCustTot` | `(NATION_AMT_CNT + FOREIGN_AMT_CNT)` | Int | 내국인 고객 수 + 외국인 고객 수 합산 |
| **객 단가** | `detailCustAmt` | `CASE WHEN (NATION_AMT_CNT+FOREIGN_AMT_CNT) > 0 THEN SALE_AMT / (NATION_AMT_CNT+FOREIGN_AMT_CNT) ELSE 0 END` | Numeric(12,2) | 총 고객수가 1명 이상일 경우 `순매출액 / 총고객수` 계산, 0명인 경우 0원 처리 |
| **현금 과부족** | `detailCloseLoss` | `CASH_LOSS` | Numeric(12,2) | 마감 전산 시재금액과 실제 시재(`CLOSE_STOCK`) 입력 간의 차액 |

#### [탭 4] 마감 시 현금시재 내역 (Closing Cash Details)

* **수표 합계 건수 (`detailCheckCntTot`)**: 전 수표 권종 입력 건수 합산
* **수표 합계 금액 (`detailCheckTot`)**: 전 수표 권종 입력 금액 합산

| 권종구분 | 수량 매핑 ID | 금액 매핑 ID | 수량 SQL 칼럼 | 금액 SQL 칼럼 |
| :--- | :--- | :--- | :--- | :--- |
| **기타수표** | `detailEtcCheckCnt` | `detailEtcCheck` | `ETC_CHECK_CNT` | `ETC_CHECK` |
| **십만원권** | `detailCheck1Cnt` | `detailCheck1` | `CHECK_1_CNT` | `CHECK_1` |
| **오만원권** | `detailEtcCheck1Cnt` | `detailEtcCheck1` | `CHECK_ETC1_CNT` | `CHECK_ETC1` |
| **일만원권** | `detailCheck2Cnt` | `detailCheck2` | `CHECK_2_CNT` | `CHECK_2` |
| **오천원권** | `detailCheck3Cnt` | `detailCheck3` | `CHECK_3_CNT` | `CHECK_3` |
| **일천원권** | `detailCheck4Cnt` | `detailCheck4` | `CHECK_4_CNT` | `CHECK_4` |
| **오백원화** | `detailCheck5Cnt` | `detailCheck5` | `CHECK_5_CNT` | `CHECK_5` |
| **일백원화** | `detailCheck6Cnt` | `detailCheck6` | `CHECK_6_CNT` | `CHECK_6` |
| **오십원화** | `detailCheck7Cnt` | `detailCheck7` | `CHECK_7_CNT` | `CHECK_7` |
| **일십원화** | `detailCheck8Cnt` | `detailCheck8` | `CHECK_8_CNT` | `CHECK_8` |

---

## 4. 데이터베이스 및 쿼리상 특이 결함 검토

### 4.1 Oracle (+) 외부조인 표기 잔존
MyBatis Mapper SQL 파일 (`Hq_Sales_00021_Sql.xml`, `St_Sales_00021_Sql.xml`, `Admin_Sales_00005_Sql.xml`)의 L36 라인 부근에서 레거시 Oracle 조인 표기법인 `MV.MS_NO(+)`가 여전히 하드코딩되어 있습니다. EDB PostgreSQL 컴파일러는 호환 래퍼에 의해 자동 변환하여 쿼리를 수행하나, 다른 표준 PostgreSQL DBMS 환경에서는 문법 에러를 유발하므로 아래와 같이 변환하는 리팩토링이 강력히 필요합니다.

* **AS-IS (현 소스)**:
  ```sql
  FROM hmsfns.SAREGITB SA, hmsfns.MMEMBSTB MM, hmsfns.MMEMBVTB MV
  WHERE SA.MS_NO = MM.MS_NO
    AND SA.MS_NO = MV.MS_NO(+)
  ```
* **TO-BE (권고안)**:
  ```sql
  FROM hmsfns.SAREGITB SA
  JOIN hmsfns.MMEMBSTB MM ON SA.MS_NO = MM.MS_NO
  LEFT OUTER JOIN hmsfns.MMEMBVTB MV ON SA.MS_NO = MV.MS_NO
  ```

### 4.2 자바 소스 내 계산식 동기화
일부 정산액 계산 logic(`NET_AMT` 산출의 ROUND 연산, `TOT_SALE_AMT` 시재 산출 등)은 자바 비즈니스 로직 Service가 아닌 **데이터베이스 SQL Query 내부에서 SELECT 연산**으로 연산되어 리턴됩니다. 이는 마이그레이션 도중 자바 소스로 별도 변경되지 않았으나, 단순 조회 서비스 구조이므로 데이터 정합성 면에서는 일관성을 유지하고 있습니다.
