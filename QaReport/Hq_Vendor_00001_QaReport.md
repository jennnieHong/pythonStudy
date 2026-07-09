# Hq_Vendor_00001 (구매의뢰요청관리) 수동 QA 검증 보고서

본 문서는 본사 > 매입발주 > 매입관리 > 구매의뢰요청관리 화면의 수동 검증 과정에서 도출된 유효성 검증(Validation) 누락 사항 및 테스트 가이드입니다.

---

## 1. 📌 입력 폼 길이 제약 불균형 및 검증 누락
* **관련 파일**: 
  * [hq_vendor_00001.js](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/vendor/hq_vendor_00001/js/hq_vendor_00001.js) (`saveRequest()` 함수)
* **발견 사항**:
  1. **상세설명 (`useRemark`)**: JavaScript 레벨에서 줄바꿈 문자를 처리하여 최대 400 Byte 제한 검증(`replaceObjValue.getByte() > 400`)이 정상 적용되어 있습니다.
  2. **구매의뢰명칭 (`purReqNm`)**: 단순히 빈 값 여부(`purReqNm == ""`)만 체크할 뿐, **최대 입력 길이에 대한 유효성 검증(Validation)이 누락**되어 있습니다. (DB 물리 컬럼 `OBREQHTB.PUR_REQ_NM`의 크기는 **`VARCHAR(50)`** 입니다.)
* **잠재적 영향도**:
  * 사용자가 구매의뢰명칭에 50자를 초과하는 텍스트를 입력하고 저장을 시도할 경우, 백엔드로 그대로 전송되어 DB 저장 단계에서 문자열 절단 오류(Data truncation / PSQLException)가 발생합니다.
* **조치 현황 및 결과**:
  * **조치 완료**: 본사 화면([hq_vendor_00001.js](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/vendor/hq_vendor_00001/js/hq_vendor_00001.js)) 및 매장 화면([st_vendor_00001.js](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/st/vendor/st_vendor_00001/js/st_vendor_00001.js))의 `saveRequest()` 및 `copyRequest()` 함수 내에 구매의뢰명칭이 50 Byte를 초과하는지 여부를 검증하고 차단하는 스크립트 패치를 완료했습니다.
