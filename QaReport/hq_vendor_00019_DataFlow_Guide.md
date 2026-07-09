# Hq_Vendor_00019 (일자별 입고현황) 조회조건 셀렉트박스 데이터 기준 가이드

본 가이드는 **일자별 입고현황** (`hq_vendor_00019`) 화면의 상단 조회조건 영역에 나열되는 셀렉트박스(매장선택, 거래처, 상품분류, 과세구분)들이 어떤 데이터베이스 테이블과 쿼리를 기준으로 바인딩되는지 설명합니다.

---

## 1. 조회조건 바인딩 아키텍처 (요약)

```
[화면: hq_vendor_00019]
  ├─ 매장선택  ──➔  selectMsPos API ──➔ MMEMBSTB (매장 마스터, chainNo 기준)
  ├─ 거래처    ──➔  selectVendor API ──➔ TVNDRMTB (본사 거래처, chainNo 기준)
  ├─ 상품분류  ──➔  selectgoodsclass ──➔ TMLCLSTB / TMMCLSTB / TMSCLSTB (대/중/소)
  └─ 과세구분  ──➔  JSP 정적 하드코딩 ──➔ All / 의제 / 과세 (정적 매핑)
```

---

## 2. 셀렉트박스별 세부 데이터 소스 및 기준

### 2.1 매장선택 (Store Selection)
* **JS 호출**: `fn_com_msNoPosNoInit('selectMsPos', '0');`
* **API 엔드포인트**: `POST /backoffice/data/common/condition/selectMsPos`
* **백엔드 매핑**: `CommonModuleController.selectMsPos` ➔ `CommonModuleService.getMsPosList` ➔ `CommonModule_GoodsClass_Mapper.selectMemberList`
* **조회 대상 테이블**: `hmsfns.MMEMBSTB` (매장 마스터), `hmsfns.MNAMEMTB` (공통 명칭 정의)
* **주요 SQL Query (`CommonModule_GoodsClass_Sql.xml:selectMemberList`)**:
  ```sql
  SELECT MS_NO
       , '[' || (SELECT NM_REP FROM hmsfns.MNAMEMTB WHERE NM_FG = '130' AND NM_CD = OPEN_FG) || '] ' || MS_NM AS MS_NM
       , OPEN_FG
       , SHOP_SALES_AREA
    FROM hmsfns.MMEMBSTB  
   WHERE CHAIN_NO = #{chainNo}
     AND CHAIN_HQ_YN = 'N'  -- 본사 제외 매장만 노출
   ORDER BY MS_NO
  ```
* **데이터 필터 기준**:
  1. 로그인 세션의 `chainNo` (체인 번호) 조건에 속한 매장만 조회합니다.
  2. `CHAIN_HQ_YN = 'N'` 조건을 통해 본사(HQ) 노드는 제외하고 실제 매장만 목록에 노출합니다.
  3. 명칭 테이블(`MNAMEMTB`)의 `NM_FG = '130'` (매장 운영상태 구분)과 아우터 조인하여, 매장명 앞에 `[개점]`, `[폐점]` 등의 한글 상태를 조합하여 노출합니다.

---

### 2.2 거래처 (Vendor Selection)
* **JS 호출**: `fn_com_vendorInit('searchVendr');`
* **API 엔드포인트**: `POST /backoffice/data/common/condition/selectVendor`
* **백엔드 매핑**: `CommonModuleController.selectVendor` ➔ `CommonModuleService.getVendorList` ➔ `CommonModule_GoodsClass_Mapper.selectVendorList`
* **조회 대상 테이블**: `hmsfns.TVNDRMTB` (본사 거래처 마스터)
* **주요 SQL Query (`CommonModule_GoodsClass_Sql.xml:selectVendorList`)**:
  ```sql
  SELECT A.VENDOR
       , A.VENDOR_NM
       , A.VENDOR_FG
       , A.ERP_IF_INFO
    FROM hmsfns.TVNDRMTB A
   WHERE A.CHAIN_NO = #{chainNo}
     AND A.VENDOR_FG != '5'  -- 물류사 제외
   ORDER BY A.VENDOR
  ```
* **데이터 필터 기준**:
  1. 현재 본사 로그인(`chainHqYn == 'Y'`) 상태이므로, 체인에 매핑된 전체 본사 거래처 마스터 `TVNDRMTB`를 조회합니다.
  2. 파라미터 `flag = '0'`이 전달되므로, 물류사(`VENDOR_FG = '5'`)를 배제하고 실매입처(`VENDOR_FG != '5'`)만 필터링하여 노출합니다.

---

### 2.3 상품분류 (Goods Category Selection)
* **JS 호출**: `fn_com_goodsClassInit('com_goodsClass_main');`
* **API 엔드포인트**: `POST /backoffice/data/common/condition/selectgoodsclass`
* **백엔드 매핑**: `CommonModuleController.selectGoodsClass` ➔ `CommonModuleService.getGoodsClass` ➔ `CommonModule_GoodsClass_Mapper` (대/중/소 쿼리)
* **조회 대상 테이블**: `hmsfns.TMLCLSTB` (대분류), `hmsfns.TMMCLSTB` (중분류), `hmsfns.TMSCLSTB` (소분류)
* **데이터 필터 기준**:
  * **대분류 (`selectGoodsLclass`)**:
    ```sql
    SELECT A.LCLASS_CD, A.LCLASS_NM FROM hmsfns.TMLCLSTB A WHERE A.CHAIN_NO = #{chainNo} ORDER BY A.LCLASS_CD
    ```
  * **중분류 (`selectGoodsMclass`)**:
    대분류가 선택되면 이벤트 리스너가 동작하여 선택된 `lclassCd` 기준으로 하위 중분류를 동적 로드합니다.
    ```sql
    SELECT A.MCLASS_CD, A.MCLASS_NM FROM hmsfns.TMMCLSTB A WHERE A.CHAIN_NO = #{chainNo} AND A.LCLASS_CD = #{lclassCd}
    ```
  * **소분류 (`selectGoodsSclass`)**:
    중분류가 선택되면 동일하게 `lclassCd`, `mclassCd` 기준으로 하위 소분류를 동적 로드합니다.
    ```sql
    SELECT A.SCLASS_CD, A.SCLASS_NM FROM hmsfns.TMSCLSTB A WHERE A.CHAIN_NO = #{chainNo} AND A.LCLASS_CD = #{lclassCd} AND A.MCLASS_CD = #{mclassCd}
    ```

---

### 2.4 과세구분 (Tax Type Selection)
* **JSP 하드코딩 구현**:
  별도의 DB API를 호출하지 않으며, JSP 템플릿 파일([hq_vendor_00019.jsp](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/vendor/hq_vendor_00019/hq_vendor_00019.jsp#L94-L98)) 내에 정적으로 구현되어 있습니다.
* **옵션 및 기준**:
  * **All (`""`)**: 세부 분류 필터 없이 전체 데이터를 조회합니다.
  * **의제 (`"Y"`)**: 의제매입 대상 상품만 조회합니다. (SQL 단에서 `TAX_FG = '0' AND FICTITIOUS_YN = 'Y'` 필터 추가 작동)
  * **과세 (`"N"`)**: 일반 면세 대상 상품만 조회합니다. (SQL 단에서 `TAX_FG = '0'` 필터 추가 작동)
