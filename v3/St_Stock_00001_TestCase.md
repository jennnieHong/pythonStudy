# St_Stock_00001 — 매장 재고 조정 등록 단위 테스트케이스

> **URL Prefix**: `POST /backoffice/data/st/stock/st_stock_00001`  
> **@Transactional**: 적용됨 (`@Transactional` on `St_Stock_00001_Service`)  
> **외부 트리거 (마이그레이션 포팅)**: `Tr_IMREAL_T01_Service` (단, 현재 저장 로직 내에서 명시적 호출 누락됨 - 고아코드 상태)
> **DB 프로시저/함수 연쇄**: `SP_SUB_IMTRLG_I` (수불부 갱신 프로시저, 트리거 서비스 내에서 호출되도록 포팅됨)
> **DB 트리거 영향도**: TPRICETB, MNAMEMTB, IMREALTB, TGOODSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 엔드포인트 목록 (10개)

| # | URL | 기능 | Type | 쿼리 ID  관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 매장 조정 내역 조회 (페이징) | SELECT | `getModifyList`, `getTotalCnt`  IMCRIOTB<br>IMREALTB<br>MCLASSVW<br>MGOODSTB<br>MMSSRCTB<br>MNAMEMTB<br>TB_RECIPE_GOODS<br>TGOODSTB<br>TPRICETB |
| 2 | `/addGoodsSearch` | 조정 등록 팝업 상품 조회 | SELECT | `getAddGoodsList`  IMCRIOTB<br>MGOODSTB<br>MNAMEMTB |
| 3 | `/addGoodsModify` | 선택 상품을 조정 내역 임시 등록 | INSERT | `insertImreal`  CHKIMTRLGTB<br>IMCRIOTB<br>IMREALTB<br>IMTRLGTB<br>MGOODSTB<br>TB_RECIPE_GOODS<br>TGOODSTB<br>TPRICETB |
| 4 | `/getWongaFg` | 매장 원가 구분 조회 | SELECT | `getWongaFg`  MMEMBVTB |
| 5 | `/updtReal` | 조정 내역 메인 그리드 저장 (단가/사유) | UPDATE | `updtReal`  IMCRIOTB<br>IMREALTB<br>MGOODSTB<br>TGOODSTB |
| 6 | `/deleteReal` | 조정 내역 삭제 | DELETE | `deleteReal`  IMREALTB |
| 7 | `/confirmReal` | 조정 내역 확정 처리 | UPDATE | `confirmReal`  IMREALTB |
| 8 | `/modifyReasonSearch` | 조정 사유 목록 조회 | SELECT | `modifyReasonSearch`  MNAMEMTB |
| 9 | `/addModifyReason` | 신규 조정 사유 등록 | INSERT | `addModifyReason`  MNAMEMTB |
| 10 | `/deleteModifyReason` | 조정 사유 삭제 | DELETE | `deleteModifyReason`  MNAMEMTB |

---

## 1. `/search` — 매장 조정 내역 조회

**서비스 로직**: 파라미터로 넘어온 Map 데이터를 기반으로 `getTotalCnt` 실행 후 `getModifyList` 호출 (페이징 offset 필수)  
**직접영향테이블**: `IMREALTB`(조정내역), `MGOODSTB`(상품마스터), `IMCRIOTB`(기초재고) 조인 조회

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 1-1 | 정상 조회 | `{"offset":0,"limit":10, "msNo":"A0001", "surveyDate":"20260528"}` | `{"total":N,"rows":[...]}` |
| 1-2 | offset 누락 (예외 발생) | `{"limit":10}` | 백엔드 `.toString()` 호출 시 **NPE 발생** (500 Error) |
| 1-3 | 데이터 없음 | `{"msNo":"ZZZZZ"}` | `{"total":0,"rows":[]}` |

---

## 3. `/addGoodsModify` — 선택 상품 조정 내역 임시 등록

**서비스 분기**:
- `chkImtrlgtb` (재고 수불 완료 체크) > 0 → `"later"` 반환
- 수불 미완료 → 전달받은 `goodsCdArr` 배열을 for문으로 순회
  - `getModifyChk` > 0 (이미 존재) → `fail` 카운트 증가
  - 미존재 시 → `insertImreal` 실행 → `success` 카운트 증가

**직접영향테이블**: `IMREALTB` (INSERT)

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 3-1 | 신규 상품 단건 추가 | `goodsCdArr=["T0000001"]` | `{"success":1, "fail":0, "status":""}` |
| 3-2 | 신규 다건 추가 | `goodsCdArr=["T1","T2"]` | `{"success":2, "fail":0, "status":""}` |
| 3-3 | 중복 상품 추가 | 이미 추가된 `goodsCd` | `{"success":0, "fail":1, "status":""}` |
| 3-4 | 수불 마감 시기 | 수불 마감일자 이후 | `{"success":0, "fail":0, "status":"later"}` |

---

## 5. `/updtReal` — 조정 내역 저장 (단가/수량/사유 갱신)

**서비스 로직**: 
화면 그리드의 배열 데이터(`idxArr`, `goodsCdArr`, `surveyQtyArr`, `remarkArr`, `reasonCdArr`, `ucostArr`)를 받아 `idxArr.length` 만큼 for문을 순회하며 UPDATE 쿼리(`updtReal`) 수행.  
**직접영향테이블**: `IMREALTB` (수량, 사유, 단가 갱신)  
**연쇄확인테이블**: 기존 Oracle 환경에선 `IMREALTB` UPDATE 후 **`IMREAL_T01` 트리거**가 작동하여 `SP_SUB_IMTRLG_I` 호출 및 `IMTRLGTB`(수불부)가 연쇄 갱신되었으나, 현재 Java 코드 상 단절됨(호출 부재).

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 5-1 | 단건 저장 | `idxArr=["1"], surveyQtyArr=["10"]` | DB `IMREALTB` 1건 정상 갱신 |
| 5-2 | **파라미터 누락 (NPE/OutOfBounds)** | `idxArr=["1","2"]` 이나 `reasonCdArr=["01"]` 길이 불일치 | 배열 인덱스 초과로 **500 에러 다운** |
| 5-3 | 연쇄 트리거 작동 여부 | 정상 저장 수행 | `IMTRLGTB` 갱신 여부 확인 (현재 버그로 미갱신) |

---

## 7. `/confirmReal` — 조정 내역 확정 처리

**서비스 로직**: `idxArr` 배열 순회하며 확정자 ID와 수정일시(`confirmReal` 쿼리) 반영.
**직접영향테이블**: `IMREALTB` (PROC_FG 등 갱신)

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 7-1 | 정상 확정 | `idxArr=["1"]` | 확정 처리 완료 및 상태 변경 |
| 7-2 | 미저장 상태 확정 시도 | 수량 미기입 및 저장 안된 상태 | UI 단 Validation으로 튕김 ("저장 후 확정 요망") |

---

## 9. `/addModifyReason` — 신규 조정 사유 등록

**서비스 로직**: `chkNmFg` 쿼리로 중복 사유명 조회 → 존재하면 `"dulp"` 반환, 없으면 `addModifyReason` INSERT 수행
**직접영향테이블**: `MNAMEMTB` (공통 코드 명칭 마스터 테이블)

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 9-1 | 신규 사유 등록 | 새로운 사유명 | 정상 INSERT 후 `""` 반환 |
| 9-2 | 중복 사유 등록 | 기존 존재하는 사유명 입력 | `"dulp"` 문자열 반환 |

---

## 서비스 핵심 분기 요약

```text
addGoodsModify (상품 추가)
├── chkImtrlgtb > 0 (수불 마감) → "later"
└── 수불 진행중
    └── goodsCdArr 반복 순회
        ├── 중복(getModifyChk > 0) → fail 카운트 증가
        └── 신규 → insertImreal 수행 → success 카운트 증가

updtReal (조정내역 저장)
└── idxArr 반복 순회
    ├── 배열 길이 초과/부족 (reasonCdArr 등) 시 → Exception (방어 로직 부재)
    ├── updtReal (IMREALTB UPDATE)
    └── ⚠️ (누락된 트리거 분기 - 복원 필요 시)
        └── Tr_IMREAL_T01_Service 호출 (수불/레시피 비용 계산)
            ├── 세트상품 여부 (SetFg == 2 / 3) 
            │   └── 레시피 비율/세트 구성 분배 후 SubImtrlgI 호출
            └── 일반상품
                └── 단가 연산 후 SubImtrlgI 호출
```

---

## 사전 조건 (Test Data)

본 테스트 수행을 위해 다음 마스터 및 기초 데이터 테이블의 선행 값이 필요합니다.

| 분류 | 테이블명 | 설명 (필요 데이터) |
|------|-----------|--------------------|
| 마스터 | `MGOODSTB` | 상품 마스터 (상품군, 단위, 입수량 데이터 필요) |
| 마스터 | `MNAMEMTB` | 조정 사유 구분을 위한 공통코드(`NM_FG='121'`, `'122'` 등) 데이터 필요 |
| 기준 | `MMEMBSTB` | 가맹점/체인 마스터 데이터 (권한 조회용) |
| 재고 | `IMCRIOTB` | 기초 재고 데이터 (수불 여부 및 기초수량 계산 시 참조) |
| 재고 | `IMREALTB` | 이전 조정 내역 등 실사 데이터 (저장/삭제/확정 테스트용) |
| 재고 연쇄 | `IMTRLGTB` | 재고 수불부 (트리거 연쇄 복원 후 데이터 적재 검증용) |



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] IMREALTB (CUD 작업)
│   └── (Trigger) Tr_IMREAL_T01
├── [테이블] MNAMEMTB (CUD 작업)
│   └── (Trigger) Tr_MNAMEM_T01
├── [테이블] TGOODSTB (CUD 작업)
│   └── (Trigger) Tr_TGOODS_T01
├── [테이블] TPRICETB (CUD 작업)
│   └── (Trigger) Tr_TPRICE_T01
└── [공통 영향 테이블 및 호출]
    ├── MMGLOGTB [MGOODSTB WEB 수정 LOG]
    ├── MMSLOGTB [MASTER LOG]
    ├── MMSPOSTB [매장별 POS MASTER]
    ├── MPRICETB [매장별 단가 관리 MASTER]
    ├── MPRILGTB [매장별 단가 관리 LOG]
    ├── MSUBMNTB [매장별 부가주문내역]
    ├── SSGOODTB [POS와의 상품 MASTER 응답]
    ├── SSMEMBTB [POS와의 명판(매장) MASTER 응답]
    ├── SSMSETTB [POS와의 코스상품  MASTER 응답]
    ├── SSMSRCTB [POS와의 소스 MASTER 응답]
    ├── TB_COST [원가변경관리]
    ├── TB_RECIPE_GOODS_HISTORY [레시피 구성 상품마스터 이력관리]
    ├── TPRILGTB [단가 관리 MASTER]
    ├── TSUBMNTB [본부 부가주문 내역 Master]
    ├── [FUNCTION] F_GET_AVG_MONTH_UCOST (TGOODSTB)
    ├── [FUNCTION] F_GET_AVG_UCOST (TGOODSTB)
    ├── [FUNCTION] F_GET_CUR_INFO (IMCRIOTB)
    ├── [FUNCTION] F_GET_CUR_INFO (MNAMEMTB)
    ├── [FUNCTION] F_GET_MPRICE (MPRICETB)
    ├── [FUNCTION] F_GET_MPRICE_2 (MPRICETB)
    ├── [FUNCTION] F_GET_MPRICE_3 (MPRICETB)
    ├── [FUNCTION] F_GET_NETAMT (MGOODSTB)
    ├── [FUNCTION] F_GET_NETAMT (MMEMBVTB)
    ├── [FUNCTION] F_GET_SALE_NETAMT (MGOODSTB)
    ├── [FUNCTION] F_GET_SALE_NETAMT (MMEMBVTB)
    ├── [FUNCTION] F_GET_SPC_MPRICE (MPRICETB)
    ├── [FUNCTION] F_GET_SPC_TPRICE (TPRICETB)
    ├── [FUNCTION] F_GET_TPRICE (TPRICETB)
    ├── [FUNCTION] F_GET_TPRICE_2 (TPRICETB)
    ├── [FUNCTION] F_GET_USUPRICE_VAT (MMEMBVTB)
    ├── [FUNCTION] F_GET_USUPRICE_VAT (TGOODSTB)
    ├── [FUNCTION] GET_UCOST_F01 (MGOODSTB)
    ├── [FUNCTION] IGET_CUR_F01 (IMCRIOTB)
    ├── [PROCEDURE] P_MACOST_B (MGOODSTB)
    ├── [PROCEDURE] P_TACOST_B (MGOODSTB)
    ├── [PROCEDURE] SUB_CUSTCL_P (TGOODSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MGOODSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_IMTRLG_I (IMTRLGTB)
    ├── [PROCEDURE] SUB_MASTER_P (MGOODSTB)
    ├── [PROCEDURE] SUB_MMSSET_P (IMTRLGTB)
    ├── [PROCEDURE] SUB_MMSSET_P (MGOODSTB)
    ├── [PROCEDURE] SUB_MRECIP_P (IMTRLGTB)
    ├── [PROCEDURE] SUB_MRECIP_P (MGOODSTB)
    ├── [PROCEDURE] SUB_RECIPE_IO_P (TB_RECIPE_GOODS)
    ├── [PROCEDURE] SUB_RECIPE_IO_P (TGOODSTB)
    ├── [PROCEDURE] SUB_SET_IO_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SET_IO_P (TB_RECIPE_GOODS)
    ├── [PROCEDURE] SUB_SET_IO_P (TGOODSTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (TB_RECIPE_GOODS)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (TGOODSTB)
    ├── [PROCEDURE] SUB_SL_SET_GOODS_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SL_SET_GOODS_P (TGOODSTB)
    ├── [PROCEDURE] SUB_SNETDT_P (MGOODSTB)
    ├── [PROCEDURE] SUB_SNETDT_P (MMEMBVTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_MAIN_P (IMCRIOTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_PROC_P (TGOODSTB)
    ├── [PROCEDURE] SUB_STOCK_MGMVHD_P (TGOODSTB)
    ├── [PROCEDURE] SUB_TEMP2GD_P (MGOODSTB)
    ├── [PROCEDURE] SUB_TEMP2GD_P (MMEMBVTB)
    ├── [PROCEDURE] SUB_TEMPGD_P (MGOODSTB)
    ├── [PROCEDURE] SUB_TEMPGD_P (MMEMBVTB)
    ├── [PROCEDURE] SUB_TMPRGD_P01 (MGOODSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_P (TGOODSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_SINGLE_P (TGOODSTB)
    └── [PROCEDURE] SUB_VDORDER_P (TGOODSTB)
```
