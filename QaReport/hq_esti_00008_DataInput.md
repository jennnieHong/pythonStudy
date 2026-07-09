# Hq_Esti_00008 — 계약 이월 사전 데이터 가공 및 화면 구성 가이드

본 가이드는 계약 이월(`hq_esti_00008`) 테스트를 정상적으로 수행하기 위한 사전 조건(견적 유형, 양식, 품목 단가 적용 상태)을 DB 직접 가공 방식과 화면 UI 상에서 수동으로 구성하는 방식 두 가지로 구분하여 정리합니다.

---

## 1. 개요 및 화면 흐름 요약

계약 이월 화면(`hq_esti_00008`)은 다음 조건을 만족하는 견적 양식 데이터를 대상으로 조회 및 이월을 수행합니다.
1. **견적헤더 확정 상태**: `TESFRHTB.ESTIM_PROC_FG = '1'` (확정 상태)
2. **거래처 단가 적용 완료**: `TESVDUTB.ESTIM_PRC_APPLY_YN = 'Y'` (본부 단가 적용 완료)
3. **만료되지 않았거나 미이월 상태**: 특정 기간의 단가가 정상 매핑되어 있으며 이월 테이블(`TPRICETB` 가격구분 `'2'`)로 전파할 대상이 있는 상태.

---

## 2. 화면 UI 기반 수동 구성 방법 (DB 직접 입력 대체)

DB 테이블에 직접 SQL DML을 날리지 않고, 웹 브라우저 화면 상에서 유기적인 흐름에 따라 사전 데이터를 구성하는 순서는 다음과 같습니다.

### Step 1. 본사 권한 매장 및 세션 검증 (`hq_master_00004` 매장관리)
- 로그인한 계정의 기본 매장(예: `NC0005`)이 해당 체인(예: `C002`)의 **본사(HQ)** 권한을 가지고 있어야 본사 견적 메뉴에 접근할 수 있습니다.
- **처리 방법**: [본사] 매장관리(`hq_master_00004`) 화면에서 해당 가맹점의 상세 탭에 들어가 `본사여부`를 **'Y' (본사)**로 수정하여 저장합니다.

### Step 2. 견적 유형 및 상품 매핑 (`hq_esti_00001` 견적유형마스터)
- 계약이월의 대분류 기준이 될 견적 유형을 새로 정의하고 대상 상품들을 지정합니다.
- **처리 방법**:
  1. `[본사] 견적유형마스터` 화면으로 이동합니다.
  2. 신규 등록 버튼을 누르고 견적유형코드(예: `001`) 및 한글명(예: `TEST_230105`)을 입력 후 저장합니다.
  3. 우측의 '유형별 상품 매핑' 그리드에서 이월 테스트를 수행할 대상 상품(예: `T0000018`, `T0000021` 등)을 추가하고 저장합니다.

### Step 3. 견적서 양식 및 거래처 매핑 (`hq_esti_00002` 견적서 양식작성)
- 정의된 견적 유형 하위에 실무용 상세 양식을 개설하고 거래처별 상품을 설정합니다.
- **처리 방법**:
  1. `[본사] 견적서 양식작성` 화면으로 이동합니다.
  2. 조회조건에서 방금 등록한 견적유형(예: `001`)을 선택 후 조회합니다.
  3. 신규 양식 등록 버튼을 클릭하여 양식코드(예: `0002`)와 양식명(예: `TEST_230116`)을 생성합니다.
  4. '양식 상품 매핑' 그리드에 Step 2에서 정의한 상품들을 추가하고, 각 상품별 주거래처(예: `V001`)를 지정하여 저장합니다.

### Step 4. 견적 단가 등록 및 확정 (`hq_esti_00006` 견적서 적용)
- 계약이월 화면은 **단가 적용이 완료되어 확정된 견적 양식**만 노출합니다.
- **처리 방법**:
  1. `[본사] 견적서 적용` 화면으로 이동하여 유형(`001`) 및 양식(`0002`)을 조회합니다.
  2. 매핑된 상품들의 적용단가(예: `600`, `70` 등)를 그리드에 수동 기입합니다.
  3. 상단의 **[단가 확정 / 적용]** 버튼을 클릭합니다.
     - 이 과정이 정상 수행되면 DB 내부적으로 `TESVDUTB.ESTIM_PRC_APPLY_YN`이 `'Y'`로 바뀌고, `TESFRHTB.ESTIM_PROC_FG`가 `'1'`(확정)로 업데이트됩니다.
  4. 이제 `[본사] 계약이월(hq_esti_00008)` 화면에서 조회 시 해당 양식(`0002`)이 이월 대상 목록에 활성화되어 나타납니다.

---

## 3. DB 직접 입력을 통한 고속 테스트 구성 SQL

E2E 스크립트 실행 등 자동화 테스트를 위해 데이터베이스에 직관적으로 사전 데이터를 밀어 넣는 쿼리 모음입니다.

### 3.1 기본 매장 본사 및 체인 업데이트
`fnbadmin` 계정의 기본 매장인 `NC0005`를 `C002` 체인의 본사 권한으로 설정합니다.
```sql
UPDATE hmsfns.MMEMBSTB 
   SET chain_no    = 'C002', 
       chain_hq_yn = 'Y' 
 WHERE ms_no = 'NC0005';
```

### 3.2 견적 유형 마스터 데이터 삽입 (`TESTYMTB`)
```postgres
INSERT INTO hmsfns.TESTYMTB (chain_no, estim_type_cd, estim_type_kor_nm, ins_dtime, ins_id, upd_dtime, upd_id)
VALUES ('C002', '001', 'TEST_230105', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'fnbadmin', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'fnbadmin')
ON CONFLICT (chain_no, estim_type_cd) DO NOTHING;
```

### 3.3 견적서 양식 헤더 데이터 삽입 (`TESFRHTB`)
종료일이 만료 직전이거나 이전 날짜인 상태로 헤더를 구성하여 이월 대상이 되도록 만듭니다.
```postgres
INSERT INTO hmsfns.TESFRHTB (chain_no, estim_type_cd, estim_from_cd, estim_fr_date, estim_to_date, estim_proc_fg, ins_dtime, ins_id, upd_dtime, upd_id)
VALUES ('C002', '001', '0002', '20230101', '20231231', '1', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'fnbadmin', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'fnbadmin')
ON CONFLICT (chain_no, estim_type_cd, estim_from_cd) 
DO UPDATE SET estim_fr_date = '20230101', estim_to_date = '20231231', estim_proc_fg = '1';
```

### 3.4 견적서 거래처별 적용 단가 삽입 (`TESVDUTB`)
단가 적용 여부(`ESTIM_PRC_APPLY_YN`)를 `'Y'`로 세팅합니다.
```postgres
-- 예시 상품 T0000018에 대해 거래처 V001의 단가 매핑
INSERT INTO hmsfns.TESVDUTB (chain_no, estim_type_cd, estim_from_cd, estim_goods_cd, estim_vendor, estim_prc_apply_yn, estim_ucost, ins_dtime, ins_id, upd_dtime, upd_id)
VALUES ('C002', '001', '0002', 'T0000018', 'V001', 'Y', 600.00, TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'fnbadmin', TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'), 'fnbadmin')
ON CONFLICT (chain_no, estim_type_cd, estim_from_cd, estim_goods_cd, estim_vendor) 
DO UPDATE SET estim_prc_apply_yn = 'Y', estim_ucost = 600.00;
```

### 3.5 테스트 결과 원복 및 클린업 SQL
이월 테스트 수행 후 생성된 연장 단가 및 이력을 청소하고 만료일 정보를 리셋합니다.
```sql
-- 1. 이월 생성 단가 삭제
DELETE FROM hmsfns.TPRICETB WHERE price_fg='2' AND start_date='20260801';

-- 2. 이월 히스토리 로그 삭제
DELETE FROM hmsfns.TESHISTB WHERE estim_type_cd='001' AND estim_from_cd='0002' AND estim_fr_date='20260801';

-- 3. 원본 헤더 적용일자 2023년 상태로 원복
UPDATE hmsfns.TESFRHTB 
   SET estim_fr_date='20230101', 
       estim_to_date='20231231' 
 WHERE chain_no='C002' AND estim_type_cd='001' AND estim_from_cd='0002';
```
