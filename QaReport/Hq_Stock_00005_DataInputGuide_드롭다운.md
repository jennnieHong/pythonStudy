# 본사 재고 조정등록 (`hq_stock_00005`) 드롭다운 목록 데이터 세팅 가이드

본 문서는 본사 재고 조정 등록 화면([hq_stock_00005.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/stock/hq_stock_00005/hq_stock_00005.jsp)) 및 등록 팝업 모달([hq_stock_00005_M01.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/stock/hq_stock_00005/modal/hq_stock_00005_M01.jsp))에서 사용되는 모든 드롭다운(Dropbox/Combo Box) 목록에 대한 백엔드 호출 매커니즘, 참조 데이터베이스 테이블/컬럼 명세 및 데이터 세팅을 위한 SQL 스크립트 가이드라인입니다.

---

## 1. 드롭다운 목록 개요 및 로더 매핑

해당 화면 및 모달에서 자바스크립트 모듈([js/hq_stock_00005.js](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/stock/hq_stock_00005/js/hq_stock_00005.js))의 `$(document).ready` 시점에 초기화되는 공통 콤보박스 정보는 다음과 같습니다.

| 화면 엘리먼트 ID | 목록 구분 | 공통 JS 초기화 함수 | 호출 API URL | 관련 DB 테이블 |
| :--- | :--- | :--- | :--- | :--- |
| `selectMsPos` | 매장선택 | `fn_com_msNoPosNoInit` | `/backoffice/data/common/condition/selectMsPos` | `MMEMBSTB`, `MNAMEMTB` |
| `com_goodsClass` | 상품분류 | `fn_com_goodsClassInit` | `/backoffice/data/common/condition/selectgoodsclass` | `TMLCLSTB`, `TMMCLSTB`, `TMSCLSTB` |
| `selectFg` | 상품구분 | `fn_com_comboBoxInit(..., '124')` | `/backoffice/data/common/condition/selectName` | `MNAMEMTB` |
| `modifyReason` | 조정사유 | `fn_com_comboBoxInit(..., '901')` | `/backoffice/data/common/condition/selectName` | `MNAMEMTB` |
| `modal_selectMsPos` | [팝업] 매장선택 | `fn_com_msNoPosNoInit` | `/backoffice/data/common/condition/selectMsPos` | `MMEMBSTB`, `MNAMEMTB` |
| `com_goodsModal_goodsClass` | [팝업] 상품분류 | `fn_com_goodsClassInit` | `/backoffice/data/common/condition/selectgoodsclass` | `TMLCLSTB`, `TMMCLSTB`, `TMSCLSTB` |

---

## 2. 드롭다운별 데이터 세팅 상세 가이드

각 드롭다운이 데이터를 조회해오는 내부 쿼리 조건과 드롭다운 값이 비어있거나 누락되었을 때 DB에 데이터를 적재하는 방법입니다. (SQL Mapper: [CommonModule_GoodsClass_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/common/CommonModule_GoodsClass_Sql.xml) 참고)

### 📌 2.1 매장선택 (`selectMsPos`, `modal_selectMsPos`)
* **설명**: 본사 관리자가 재고를 조정할 대상 가맹점 테이블(`hmsfns.MMEMBSTB`)을 선택하는 드롭다운 목록입니다.
* **조회 쿼리 ID**: `selectMemberList`
* **조회 논리**:
  * 로그인 정보의 체인 코드(`chainNo`, 예: `'C001'`)에 소속된 가맹점 중 본사 매장을 제외한 가맹점 테이블(`hmsfns.MMEMBSTB`, 필드: `CHAIN_HQ_YN = 'N'`) 목록을 반환합니다.
  * 매장 명칭 앞에 명칭 테이블(`hmsfns.MNAMEMTB`)에서 매장 운영 상태 구분 코드 테이블(`hmsfns.MNAMEMTB`, 필드: `NM_FG = '130'`, 예: `OPEN_FG`가 `'1'`이면 `'[정상]'`)를 조합하여 표시합니다. (예: `"[정상] KITCHEN"`)
* **DB 세팅 SQL**:
  ```sql
  -- 1) 가맹점 기본 정보 등록 (hmsfns.MMEMBSTB)
  INSERT INTO hmsfns.MMEMBSTB (
      CHAIN_NO, MS_NO, MS_NM, CHAIN_HQ_YN, OPEN_FG
  ) VALUES (
      'C001',     -- 본인 체인코드 (C001: Shop, C002: F&B)
      'NC0006',   -- 가맹점코드
      'KITCHEN',  -- 가맹점명
      'N',        -- 본사 여부 (N: 가맹점, Y: 본사)
      '1'         -- 운영 구분 코드
  );

  -- 2) 매장 운영 상태 명칭 공통코드 등록 (hmsfns.MNAMEMTB - NM_FG: '130')
  INSERT INTO hmsfns.MNAMEMTB (
      CHAIN_NO, NM_FG, NM_CD, NM_REP
  ) VALUES (
      'C001',   -- 체인코드
      '130',    -- 명칭 구분 코드 (130: 매장 운영 상태)
      '1',      -- 명칭 코드 (OPEN_FG)
      '정상'    -- 노출 명칭
  );
  ```

---

### 📌 2.2 상품분류 (`com_goodsClass`, `com_goodsModal_goodsClass`)
* **설명**: 대분류 테이블(`hmsfns.TMLCLSTB`) ➔ 중분류 테이블(`hmsfns.TMMCLSTB`) ➔ 소분류 테이블(`hmsfns.TMSCLSTB`)로 연동되는 3단 필터 상품 분류 드롭다운입니다.
* **조회 쿼리 ID**: `selectGoodsLclass` (대), `selectGoodsMclass` (중), `selectGoodsSclass` (소)
* **조회 논리**:
  * **대분류**: 체인에 매핑된 대분류 테이블(`hmsfns.TMLCLSTB`)을 조회합니다.
  * **중분류**: 대분류 선택 이벤트 감지 후, 체인 및 선택된 대분류코드(`LCLASS_CD`)에 속한 중분류 테이블(`hmsfns.TMMCLSTB`)을 필터링 조회합니다.
  * **소분류**: 중분류 선택 이벤트 감지 후, 체인, 대분류, 중분류코드(`MCLASS_CD`)에 속한 소분류 테이블(`hmsfns.TMSCLSTB`)을 필터링 조회합니다.
* **DB 세팅 SQL**:
  ```sql
  -- 1) 대분류 등록 (hmsfns.TMLCLSTB)
  INSERT INTO hmsfns.TMLCLSTB (CHAIN_NO, LCLASS_CD, LCLASS_NM) 
  VALUES ('C001', '01', '식품');

  -- 2) 중분류 등록 (hmsfns.TMMCLSTB)
  INSERT INTO hmsfns.TMMCLSTB (CHAIN_NO, LCLASS_CD, MCLASS_CD, MCLASS_NM) 
  VALUES ('C001', '01', '01', '식자재');

  -- 3) 소분류 등록 (hmsfns.TMSCLSTB)
  INSERT INTO hmsfns.TMSCLSTB (CHAIN_NO, LCLASS_CD, MCLASS_CD, SCLASS_CD, SCLASS_NM) 
  VALUES ('C001', '01', '01', '001', '치즈/유제품');
  ```

---

### 📌 2.3 상품구분 (`selectFg`)
* **설명**: 상품 구성 유형(일반, 레시피, 세트)에 따라 필터링하기 위한 드롭다운입니다. (상품 테이블(`hmsfns.TGOODSTB` / `hmsfns.MGOODSTB`)의 `SET_FG` 필드와 매핑)
* **조회 쿼리 ID**: `selectNameList` (파라미터 `nmFg = '124'`)
* **조회 논리**:
  * 명칭 마스터 테이블(`hmsfns.MNAMEMTB`)에서 `NM_FG = '124'`에 해당하는 명칭 코드(`NM_CD`) 및 명칭(`NM_REP`)을 조회합니다.
* **DB 세팅 SQL**:
  ```sql
  -- 상품구분 공통코드(124) 명칭 정보 세팅 (hmsfns.MNAMEMTB)
  INSERT INTO hmsfns.MNAMEMTB (CHAIN_NO, NM_FG, NM_CD, NM_REP) VALUES ('C001', '124', '0', '일반');
  INSERT INTO hmsfns.MNAMEMTB (CHAIN_NO, NM_FG, NM_CD, NM_REP) VALUES ('C001', '124', '2', '레시피');
  INSERT INTO hmsfns.MNAMEMTB (CHAIN_NO, NM_FG, NM_CD, NM_REP) VALUES ('C001', '124', '3', '세트');
  ```

---

### 📌 2.4 조정사유 (`modifyReason`)
* **설명**: 메인 조회 그리드 내의 조정 상품별 조정 사유 항목을 일괄 또는 개별 선택하기 위한 공통사유 코드 목록입니다. (재고 실사/조정 슬립 테이블(`hmsfns.IMREALTB`)의 `REASON_CD` 필드에 저장됨)
* **조회 쿼리 ID**: `selectNameList` (파라미터 `nmFg = '901'`)
* **조회 논리**:
  * 명칭 마스터 테이블(`hmsfns.MNAMEMTB`)에서 `NM_FG = '901'`에 해당하는 명칭 코드(`NM_CD`, 예: `'003'`) 및 명칭(`NM_REP`, 예: `'기타조정'`)을 조회합니다.
* **DB 세팅 SQL**:
  ```sql
  -- 조정사유 공통코드(901) 명칭 정보 세팅 (hmsfns.MNAMEMTB)
  INSERT INTO hmsfns.MNAMEMTB (CHAIN_NO, NM_FG, NM_CD, NM_REP) VALUES ('C001', '901', '001', '본사폐기');
  INSERT INTO hmsfns.MNAMEMTB (CHAIN_NO, NM_FG, NM_CD, NM_REP) VALUES ('C001', '901', '002', '매장실사');
  INSERT INTO hmsfns.MNAMEMTB (CHAIN_NO, NM_FG, NM_CD, NM_REP) VALUES ('C001', '901', '003', '기타조정');
  ```

---

## 3. 세션 체인 코드(`chainNo`) 매핑 확인

공통 조회조건 쿼리는 로그인 세션(`SecurityUserInformation`)의 **`chainNo`**에 의존하여 해당 체인 데이터만 필터링합니다.

* **세팅 불일치 주의**:
  * 만약 테스트하고 있는 로그인 계정(예: `fnbadmin`)의 소속 체인코드(예: `'C002'`)와 위에서 `INSERT`한 데이터의 `CHAIN_NO` 설정값(예: `'C001'`)이 일치하지 않는 경우, **드롭다운 항목이 정상적으로 채워지지 않고 빈 목록으로 표출**됩니다.
  * 따라서 SQL 스크립트 작성 시 테스트하려는 로그인 사용자 매장에 맞는 체인코드(`CHAIN_NO`)를 정확히 확인하고 적재해야 합니다.

* **사용자 정보 조회 및 매장 체인코드 확인 쿼리**:
  ```sql
  -- 로그인한 사용자 테이블(hmsfns.MUSERSTB) 및 가맹점 테이블(hmsfns.MMEMBSTB) 조인하여 체인코드 정보 조회
  SELECT A.USER_ID
       , A.MS_NO
       , B.MS_NM
       , B.CHAIN_NO
    FROM hmsfns.MUSERSTB A
    JOIN hmsfns.MMEMBSTB B ON A.MS_NO = B.MS_NO
   WHERE A.USER_ID = 'fnbadmin';
  ```
