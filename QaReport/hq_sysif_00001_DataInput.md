# hq_sysif_00001 일일 현금 시재관리 및 일 마감관리 데이터 가공 및 테스트 방법

본 문서는 **일일 현금 시재관리 및 일 마감관리 (`hq_sysif_00001`)** 화면의 QA 테스트를 위해 수행한 데이터 가공 및 실제 테스트 검증 절차를 기술한 백업용 데이터 셋업 리포트입니다.

---

## 1. 실제 QA 테스트 대상 데이터 정보

* **대상 매장 (MS_NO)**: `NC0007` (현대모터스튜디오 카페점)
  * MMEMBSTB 테이블의 인터페이스 가행점 대사 코드: **`'31'`**
* **대상 영업일자 (SALE_DATE)**: `2023-09-25` (`20230925`)
* **접속 권한 계정**: `7249525SHOP` / `0000` (매장 권한 계정)

---

## 2. 테스트 수행 단계별 데이터 가공 상세

### 2.1 마감 및 정산 데이터 정합성 사전 검증 (동일 건 대조)
* **상태**: EDB 데이터베이스에 이미 `20230925` 일자의 POS 거래 매출 내역과 마감 정산 내역이 정합성에 맞게 미리 적재되어 있는 상태였습니다.
  * **매출 원장 (`STRNHDTB` / `STRNCHTB` 등)**: 영수증 19건, 정상 거래액 합계 `152,500원`
  * **정산 마감 (`SAREGITB`)**: 마감 정산 건수 `19건`, 정산 금액 합계 `152,500원`
* **검증 결과**: 두 데이터의 총액과 건수가 완벽히 일치하여 `/closeRegi` 호출 시 수행되는 **`checkBillCnt`** 및 **`checkLoginCnt`** 정합성 검사에서 에러(0건) 없이 마감 전단계 유효성을 통과했습니다.

### 2.2 임의 시재 금액 가공 및 저장 테스트
화면상에서 시재 조정을 수정 입력하여 DB에 가공 데이터가 정확하게 병합(MERGE) 반영되는지 검증을 실행했습니다.

1. **시재금 수정 입력 (가공)**:
   * 백오피스 웹 UI 화면 상세 패널의 **`마감입금`** 필드에 **`12,345,000`** 입력
   * **`준비금반환`** 필드에 **`54,321,000`** 입력
2. **저장 API 호출 및 쿼리 검증**:
   * 화면의 **[저장]** 버튼을 클릭하여 `saveRegiData` 실행
   * EDB DB `hmsfns.IFSLRETB` 테이블의 `NC0007` - `20230925` 레코드의 `CL_DEPOSIT_AMT`와 `RE_RESERVE_AMT`가 수정한 가공 수치(`12345000` / `54321000`)로 MERGE UPDATE 완료됨을 쿼리로 확인.
3. **환경 복원**:
   * 테스트 완료 후 원본 데이터 정합성을 유지하기 위해 수치를 원래대로 복원 완료했습니다.

### 2.3 매출 연동 인터페이스 최종 연계 테스트
* **수행 내용**: 마감 완료 상태에서 `/SaleInterFace` 연동 API를 최종 기동하여 Java로 전환된 프로시저(`Sp_SUB_IF_HYDM_SEND_P_Service`)가 롤백이나 예외 없이 데이터 적재를 완료하는지 검증했습니다.
* **최종 성공 결과**:
  * API 호출 결과 **`success`** 반환 확인.
  * 로컬 EDB 데이터베이스의 연동 최종 집계 테이블 조회 결과:
    * **`hmsfns.TSM_TRAN_DTL`**: **82건** 적재 성공 ✅
    * **`hmsfns.TSM_TRAN_MST`**: **24건** 적재 성공 ✅
    * **`hmsfns.TSM_CASH_RCPS_MST`**: **14건** 적재 성공 ✅

---

## 3. 실제 DB 가공 및 수동 수정 쿼리 이력

QA 과정에서 환경 호환성 문제 해결 및 기능 테스트를 수행하기 위해 데이터베이스에서 실제 동작/가공한 SQL 쿼리 목록입니다.

### 3.1 취소 거래 원장의 불량 데이터 보정 SQL
EDB 마이그레이션 환경에서 취소 영수증 테이블의 원본 영수증 번호(`ORG_BILL_NO`) 컬럼에 비정상적인 값(`'0'`)이 세팅되어 타임스탬프 캐스팅 오류가 발생했던 건을 수동 보정했습니다.
```sql
-- 원본 영수증 번호가 '0'으로 잘못 기입된 매출 원장 데이터를 안전하게 NULL로 강제 보정
UPDATE hmsfns.STRNHDTB 
   SET ORG_BILL_NO = NULL 
 WHERE MS_NO = 'NC0007' 
   AND SALE_DATE = '20230925' 
   AND ORG_BILL_NO = '0';
```

### 3.2 화면 시재 임시 저장 시 실행된 MERGE SQL
상세 화면에서 마감 시재 금액 가공 후 **[저장]** 실행 시 내부적으로 기동되어 EDB 마감 테이블(`IFSLRETB`)에 데이터를 반영한 SQL입니다.
```sql
MERGE INTO hmsfns.IFSLRETB A
     USING DUAL
        ON ( A.MS_NO     = 'NC0007'
         AND A.SALE_DATE = '20230925' )
      WHEN NOT MATCHED THEN
           INSERT 
           (   A.MS_NO          , A.SALE_DATE          , A.CL_DEPOSIT_AMT     , A.RE_RESERVE_AMT
             , A.CREATE_DTIME                          , A.CREATE_ID
             , A.LAST_DTIME                            , A.LAST_ID
           )
           VALUES
           (   'NC0007'         , '20230925'           , 12345000             , 54321000
             , TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')     , '7249525SHOP'
             , TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')     , '7249525SHOP'
           )
      WHEN MATCHED THEN
           UPDATE
              SET A.CL_DEPOSIT_AMT = 12345000
                , A.RE_RESERVE_AMT = 54321000
                , A.LAST_DTIME     = TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS')
                , A.LAST_ID        = '7249525SHOP';
```

### 3.3 최종 매출 연동 인터페이스 시 실행된 마감 확정 SQL
마감 확정이 승인되어 Tibero ERP 연동이 시작될 때 로컬 마감 테이블(`IFSLRETB`)의 마감구분을 `'Y'`로 승인 처리한 SQL입니다.
```sql
MERGE INTO hmsfns.IFSLRETB A
     USING DUAL
        ON ( A.MS_NO     = 'NC0007'
         AND A.SALE_DATE = '20230925' )
      WHEN NOT MATCHED THEN
           INSERT
           (   A.MS_NO                  , A.SALE_DATE            , A.MS_CLOSE_YN         , A.CL_DEPOSIT_AMT   , A.RE_RESERVE_AMT
             , A.SALE_CAHS_DEPOSIT_AMT  , A.RETURN_RESERVE_AMT   , A.NEXT_RESERVE_AMT    , A.OVER_AMT         , A.REMARK
             , A.CREATE_DTIME           , A.CREATE_ID
             , A.LAST_DTIME             , A.LAST_ID
           )
           VALUES
           (   'NC0007'                 , '20230925'             , 'Y'                   , 152500             , 0
             , 152500                   , 0                      , 100000                , 0                  , 'Interface Success'
             , TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')               , '7249525SHOP'
             , TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')               , '7249525SHOP'
           )
      WHEN MATCHED THEN
           UPDATE
              SET A.MS_CLOSE_YN           = 'Y'
                , A.CL_DEPOSIT_AMT        = 152500
                , A.RE_RESERVE_AMT        = 0
                , A.SALE_CAHS_DEPOSIT_AMT = 152500
                , A.RETURN_RESERVE_AMT    = 0
                , A.NEXT_RESERVE_AMT      = 100000
                , A.OVER_AMT              = 0
                , A.REMARK                = 'Interface Success'
                , A.LAST_DTIME            = TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS')
                , A.LAST_ID               = '7249525SHOP';
```

---

## 4. 직접 테스트 시 준비 및 자동 업데이트되는 전체 테이블 요약

수동으로 매출 마감 E2E 테스트 환경을 구축하고 검증할 때 관리해야 하는 전체 테이블의 역할과 조작 방식(Insert/Update/Select)을 요약한 맵입니다.

### 4.1 직접 사전에 가공(Insert/Update)해두어야 하는 POS 기초 테이블
포스 단말기 기기 없이 백오피스 단독으로 마감 테스트를 진행하려면, 아래 3개 테이블에 반드시 **정합성이 맞는 기초 정보**가 존재해야 합니다.

| 테이블명 | 테이블 설명 | 주요 검증 컬럼 및 매칭 규칙 | 테스트 시 가공 방향 |
| :--- | :--- | :--- | :--- |
| **`hmsfns.OPNPOSTB`** | POS 개설정보 마스터 | `OPEN_DATE`, `MS_NO`, `POS_NO`<br>(당일 개설된 포스 기기 목록 조회용) | 테스트 대상 일자/매장/포스의 개설 레코드 `Insert` |
| **`hmsfns.STRNHDTB`** | POS 판매 거래 헤더 | `SALE_DATE`, `MS_NO`, `POS_NO`, `BILL_NO`<br>(실제 포스 영수증 거래액/건수 합산용) | 테스트 매출 거래 원장 데이터 `Insert` <br>(취소 거래 시 `ORG_BILL_NO`는 `NULL`) |
| **`hmsfns.SAREGITB`** | POS 정산 결과 마감 | `SALE_DATE`, `MS_NO`, `POS_NO`, `BILL_NO`, `SALE_AMT`<br>(매장에서 마감 시 정산한 수치) | `STRNHDTB`의 건수/합계와 **100% 동일**하게 `Insert` 또는 `Update` 수정 |

---

### 4.2 화면 조작 및 로컬 마감 진행 시 업데이트되는 로컬 테이블

| 테이블명 | 테이블 설명 | 수정 시점 및 플래그 변화 | 비고 |
| :--- | :--- | :--- | :--- |
| **`hmsfns.IFSLRETB`** | 매출 마감 연동 마스터 | 1. **시재 상세 저장 시**: `CL_DEPOSIT_AMT` 등 보정 금액 업데이트<br>2. **현장 마감 클릭 시**: `MS_CLOSE_YN = 'N'` (미송신 마감 완료)<br>3. **연동 성공 시**: `MS_CLOSE_YN = 'Y'` (인터페이스 완료) | E2E 마감 상태의 핵심 상태 플래그를 관리하는 제어판 역할 |

---

### 4.3 매출 연동 인터페이스(`SaleInterFace`) 성공 시 적재/업데이트되는 인터페이스 테이블
연동 실행 시 로컬 EDB에서 데이터 수집 프로시저에 의해 자동으로 데이터가 Insert되고, Tibero ERP 전송 성공 시 전송 플래그가 **`'N'` ➔ `'Y'`**로 자동 변경(Update)되는 대상 목록입니다.

| 테이블명 | 테이블 설명 | 주요 관리 컬럼 및 상태값 | 연동 성공 시 적재/수정 방향 |
| :--- | :--- | :--- | :--- |
| **`hmsfns.TSM_TRAN_MST`** | 매출일건 Header | `SHOP_CD`, `OCCU_DT`, `POS_SEND_YN` | ERP 전송 대기 정보가 `Insert` 되며, 전송 완료 시 `POS_SEND_YN = 'Y'` 갱신 |
| **`hmsfns.TSM_TRAN_DTL`** | 매출일건 Detail | `SHOP_CD`, `OCCU_DT`, `POS_SEND_YN` | 카드/현금 등 결제 수단별 세부 내역 `Insert` 및 `POS_SEND_YN = 'Y'` 갱신 |
| **`hmsfns.TSM_CASH_RCPS_MST`** | 현금 시재 입출금 마스터 | `SHOP_CD`, `OCCU_DT`, `POS_SEND_YN` | 현금 과부족 정보가 `Insert` 되며, 전송 성공 시 `POS_SEND_YN = 'Y'` 갱신 |
| **`hmsfns.TSM_SALS_AGG_MST`** | 매출 집계 마스터 | `SHOP_CD`, `OCCU_DT`, `POS_SEND_YN` | 영업일 매출 최종 요약 집계 `Insert` 및 `POS_SEND_YN = 'Y'` 갱신 |
| **`hmsfns.TSM_SHOP_DAYCLS_MST`**| 매장 일 마감 마스터 | `SHOP_CD`, `CLS_DT`, `POS_SEND_YN` | 일자별 최종 배치 마감 결과 `Insert` 및 `POS_SEND_YN = 'Y'` 갱신 |


