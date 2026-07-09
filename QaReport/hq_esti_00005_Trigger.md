# hq_esti_00005 견적서 업로드 관리 - DB 트리거 & UPD_ID 기록 분석

본 문서는 `hq_esti_00005` 화면 작업 중 발생한 `TESVDUTB` (견적서 거래처 대상상품) 테이블의 데이터 수정자 ID (`UPD_ID`) 기록 및 연동 트리거의 동작 분석 결과입니다.

---

## 🔍 이슈 현상 및 질문
* **현상**: 오늘 `TESVDUTB` 테이블에 적재된 데이터를 확인한 결과, 동일한 상품/견적에 대해 아래와 같이 `UPD_ID`와 `ESTIM_VENDOR`가 다르게 들어간 데이터가 공존함.
  * `UPD_ID = 'TESFRV_T01'` / `ESTIM_VENDOR = '12585445653'`
  * `UPD_ID = 'fnbadmin'` / `ESTIM_VENDOR = '000001'`

---

## ⚙️ 분석 결과 및 원인

`TESVDUTB` 테이블의 `UPD_ID` 값은 **데이터가 생성 및 수정된 경로**에 따라 분기됩니다.

### 1. 자동 복사 적재 경로 (트리거 동작)
* **UPD_ID**: `TESFRV_T01`
* **ESTIM_VENDOR**: `12585445653` (신규로 지정된 거래처)
* **발생 원인**:
  * 사용자가 견적 양식 관리 화면(예: `hq_esti_00003` 견적요청서 일괄등록)에서 특정 견적서 양식에 **새로운 거래처를 연결하고 저장**했을 때 작동한 **데이터베이스 트리거 서비스(`Tr_TESFRV_T01_Service`)**의 결과입니다.
* **상세 로직**:
  * 거래처 지정 테이블(`TESFRVTB`)에 데이터가 입력(`INSERT`)되면, 자바 트리거 서비스인 `Tr_TESFRV_T01_Service`가 호출되어 `Tr_TESFRV_T01_Sql.xml`의 `insertTesvdutb` 쿼리를 실행합니다.
  * 이 쿼리는 원본 양식 상품 마스터(`TESFRDTB`)로부터 상품 정보를 조회하여 해당 거래처 전용 테이블인 `TESVDUTB`로 **자동 복사 적재**합니다.
  * 이때 시스템(트리거)에 의해 자동 적재되었음을 식별하기 위해 `INS_ID` 및 `UPD_ID`에 하드코딩된 트리거명인 **`'TESFRV_T01'`**이 저장됩니다.

```xml
/* Tr_TESFRV_T01_Sql.xml - insertTesvdutb 쿼리 일부 */
INSERT INTO hmsfns.TESVDUTB ( ... , INS_ID, UPD_DTIME, UPD_ID)
SELECT ...
     , 'TESFRV_T01'                         AS INS_ID
     , TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')  AS UPD_DTIME
     , 'TESFRV_T01'                         AS UPD_ID
  FROM hmsfns.TESFRDTB A
```

---

### 2. 사용자 직접 수정/업로드 경로
* **UPD_ID**: `fnbadmin` (현재 로그인한 세션 사용자 ID)
* **ESTIM_VENDOR**: `000001` (직접 단가를 입력한 거래처)
* **발생 원인**:
  * 로그인한 사용자(`fnbadmin`)가 `hq_esti_00005` (견적서 업로드 관리) 화면의 그리드에서 직접 견적 단가를 입력한 후 **"저장"** 버튼을 클릭했거나, **엑셀 업로드**를 통해 단가를 업데이트했기 때문입니다.
* **상세 로직**:
  * 화면 또는 엑셀 업로드 저장 시 `Hq_Esti_00005_Mapper.updateEstiGoods`가 실행되면서, 업데이트를 수행한 실제 사용자 계정 세션 정보(`#{userId}`)인 **`'fnbadmin'`**이 `UPD_ID`에 기록됩니다.

```xml
/* Hq_Esti_00005_Sql.xml - updateEstiGoods 쿼리 일부 */
UPDATE hmsfns.TESVDUTB
   SET ESTIM_SUG_PRC     = NVL(#{estimSugPrc}, 0)
     , UPD_DTIME         = TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS')
     , UPD_ID            = #{userId}
 WHERE CHAIN_NO          = #{chainNo}
   AND ESTIM_VENDOR      = #{estimVendor}
```

---

## 💡 요약 및 결론
* **`TESFRV_T01`**: 신규 거래처 추가 시 견적 대상 품목 리스트를 생성하기 위해 **백엔드 트리거가 자동 실행되어 적재한 최초 상태의 값**입니다.
* **`fnbadmin`**: 거래처 등록 이후 사용자가 **직접 화면에서 단가를 저장하거나 엑셀로 일괄 업로드하여 수정한 최종 변경자 값**입니다.
