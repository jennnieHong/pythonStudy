# St_Vendor_00001 — 구매요청(매장) 단위 테스트케이스

> **화면**: 매점/매장 시스템 > 매입발주 > 매입관리 > 구매요청
> **URL Prefix**: `POST /backoffice/data/st/vendor/st_vendor_00001`
> **@Transactional**: 적용됨 (RuntimeException, Exception rollback 대상)
> **요청 방식 혼용**: `@RequestBody Map<String, Object>` 형태 활용
> **DB 트리거 영향도**: 없음 (해당 화면의 주요 테이블 `OBREQHTB`, `OBREQDTB`에는 트리거가 설정되어 있지 않아 연쇄 동작 없음)

---

## 본사(HQ) vs 매장(ST) 로직적 주요 차이점
1. **의뢰 매장코드(`msNo`) 강제 주입**:
   * 본사 화면은 여러 매장의 전표를 대행 및 관리하므로 화면 파라미터(`RequestBody`)로 `msNo`를 직접 수신받아 처리합니다.
   * 매장 화면은 로그인한 세션의 매장 정보로 필터링되어야 하므로, 프론트엔드 UI에 매장 선택 필드가 없으며, Controller 단에서 세션의 `msNo`를 강제로 주입하여 `getReqHdList`, `saveRequest`, `copyRequest` 등의 쿼리를 실행합니다.
2. **미의뢰 상품 조회 시 선입고 창고 필터링 (`getPrePurchWhMsNoYn`)**:
   * 매장 화면은 상품 조회 시 매장이 속한 체인 유형 및 선입고 창고 매장 여부(`getPrePurchWhMsNoYn` 쿼리 활용)에 따라 상품 리스트(T02)가 동적으로 필터링됩니다.
3. **전표 확정 (`confirmRequest`) 기능의 UI 제약**:
   * 매장 화면은 구매의뢰를 '요청'하는 화면이므로, 자신이 작성한 전표의 처리 단계를 승인하는 '확정' 버튼이 JSP UI 단에서 주석 처리되어 있습니다. (백엔드 API는 존재하나 매장 권한 접근 제어 대상)
4. **전표 수정/삭제의 조건 범위 제한**:
   * 매장은 본사에 의해 확정(`PROC_FG != '0'`)된 전표는 목록 조회 및 조작이 불가능하며, 오직 작성 중인 대기(`PROC_FG = '0'`) 상태의 전표만 조회하고 수정/삭제할 수 있습니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|:---|:---|:---|
| `chainNo` | `C001` | 전 엔드포인트 |
| `msNo` | `CAFE` 또는 `고양 Shop 매장코드` | 전 엔드포인트 (세션 필터링용) |
| `ID` | `shopbrand` 또는 `fnbcafe` | `saveRequest`, `addRequestGoods`, `copyRequest`, `confirmRequest` |

---

## 엔드포인트 목록 (10개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getReqHdList` | 매장 구매 요청 전표 리스트 조회 | `@RequestBody` | `List` | SELECT | OBREQHTB, MMEMBSTB |
| 2 | `/saveRequest` | 매장 구매 요청 전표 마스터 저장 | `@RequestBody` | `void` | MERGE | OBREQHTB |
| 3 | `/getReqGoodsList` | 매장 구매 요청 전표 상세내역(상품) 조회 | `@RequestBody` | `List` | SELECT | OBREQDTB, MGOODSTB, MNAMEMTB, TESHISTB |
| 4 | `/getNotReqGoodsList` | 매장 구매의뢰 상품 검색 (미등록 상품 조회) | `@RequestBody` | `Map` | SELECT | MGOODSTB, MVNDRGTB, OBREQDTB, TPRICETB, MNAMEMTB |
| 5 | `/addRequestGoods` | 상품 품목 추가 | `@RequestBody` | `void` | MERGE/INSERT | OBREQDTB, TESFRHTB, TESVDUTB, OBSLPHTB, OBSLPDTB, TVNDRGTB |
| 6 | `/deleteRequestGoods` | 상품 품목 개별 삭제 | `@RequestBody` | `void` | DELETE | OBREQDTB |
| 7 | `/copyRequest` | 전표 복사 (헤더 및 디테일) | `@RequestBody` | `void` | INSERT | OBREQHTB, OBREQDTB |
| 8 | `/deleteRequest` | 전표 삭제 (헤더 및 디테일 일괄) | `@RequestBody` | `void` | DELETE | OBREQHTB, OBREQDTB |
| 9 | `/printRequest` | 전표 인쇄 팝업 조회 | `@RequestBody` | `ModelAndView` | SELECT | OBREQHTB, OBREQDTB |
| 10 | `/confirmRequest` | 전표 등록 확정 | `@RequestBody` | `void` | UPDATE | OBREQHTB |

---

## 1. `/getReqHdList` — 매장 구매 요청 전표 리스트 조회

* **참고**: `msNo`는 RequestBody로 받지 않고 세션에서 강제 자동 맵핑됩니다.

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 1-1 | chainNo=`C001`, msNo=`CAFE` | `{"purReqNm":""}` | 해당 매장(`CAFE`)에 속한 대기 전표 목록 반환 |
| 1-2 | chainNo=`C001`, msNo=`CAFE` | `{"purReqNm":"과일"}` | 전표명에 "과일"이 포함된 매장 전표 목록 반환 |

---

## 2. `/saveRequest` — 매장 구매 요청 전표 마스터 저장

* **참고**: `msNo`는 세션 값으로 강제 오버라이딩됩니다.

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 2-1 | chainNo=`C001`, msNo=`CAFE`, ID=`fnbcafe` | `{"reqNo":"","purReqNm":"매장과일요청","usePlanDate":"20260605","useRemark":"내일용"}` | 신규 전표 번호 생성 후 `OBREQHTB` INSERT (`void`) |
| 2-2 | chainNo=`C001`, msNo=`CAFE`, ID=`fnbcafe` | `{"reqNo":"260605CAFE01","purReqNm":"수정의뢰명"}` | 기존 전표 `OBREQHTB` UPDATE (`void`) |

---

## 3. `/getReqGoodsList` — 전표 상세내역 조회

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 3-1 | chainNo=`C001`, msNo=`CAFE` | `{"reqNo":"260605CAFE01"}` | 전표에 속한 매장 품목 리스트 반환 |

---

## 4. `/getNotReqGoodsList` — 상품 검색 (선입고 매장 필터링 포함)

* **참고**: `getPrePurchWhMsNoYn` 쿼리를 타며 매장의 선입고 여부에 부합하는 상품 리스트를 가져옵니다.

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 4-1 | chainNo=`C001`, msNo=`CAFE` | `{"reqNo":"260605CAFE01","offset":0,"limit":100}` | 전표에 미등록된 해당 매장 취급 상품 페이징 목록 반환 |
| 4-2 | chainNo=`C001`, msNo=`CAFE` | `{"reqNo":"260605CAFE01","goodsCdNm":"아메리카노"}` | 상품명/코드로 필터링된 상품 목록 반환 |

---

## 5. `/addRequestGoods` — 상품 품목 추가

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 5-1 | chainNo=`C001`, msNo=`CAFE`, ID=`fnbcafe` | `{"reqNo":"260605CAFE01", "reqDate":"20260605", "goodsCdArr":["G001"], "requestQtyArr":[5], "requestGoodsPrArr":[1500], "requestGoodsOrdUnitArr":["0"], "requestGoodsPrdStdArr":["500ml"]}` | 지정된 상품이 `OBREQDTB` 상세 테이블에 MERGE(INSERT) 처리됨 |

---

## 6. `/deleteRequestGoods` — 상품 품목 개별 삭제

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 6-1 | - | `{"reqNo":"260605CAFE01", "goodsCdArr":["G001"]}` | 상세 테이블(`OBREQDTB`)에서 지정된 상품 데이터 제거됨 |

---

## 7. `/copyRequest` — 전표 복사

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 7-1 | chainNo=`C001`, msNo=`CAFE`, ID=`fnbcafe` | `{"reqNo":"260605CAFE01", "purReqNm":"복사본전표", "usePlanDate":"20260606"}` | 신규 전표 번호 채번 후 헤더/상세 일괄 복사 및 신규 생성 |

---

## 8. `/deleteRequest` — 전표 삭제

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 8-1 | - | `{"reqNoArr":["260605CAFE01"]}` | 전표 마스터(`OBREQHTB`)와 디테일(`OBREQDTB`) 데이터 일괄 삭제 |

---

## 9. `/printRequest` — 전표 인쇄 팝업 조회

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 9-1 | chainNo=`C001`, msNo=`CAFE` | `{"reqNo":"260605CAFE01"}` | 매장 인쇄용 HTML 마크업 및 데이터 바인딩 ModelAndView 반환 |

---

## 10. `/confirmRequest` — 전표 등록 확정 (매장 권한 직접 호출)

* **참고**: 화면 UI 상의 버튼은 비활성화되어 있으나 백엔드 컨트롤러 엔드포인트는 존재합니다.

| No | 세션 조건 | RequestBody | 예상값 |
|:---|:---|:---|:---|
| 10-1 | ID=`fnbcafe` | `{"reqNoArr":["260605CAFE01"]}` | 전표의 상태(PROC_FG)가 확정 상태('5')로 정상 업데이트됨 |

---

## 주요 검증 포인트

```
□ /getNotReqGoodsList — getPrePurchWhMsNoYn의 ORDER BY 절 삭제 확인 (PostgreSQL GROUP BY 에러 방지 완결 여부)
□ /saveRequest — 세션의 msNo가 DML 연산 시 올바르게 주입되어 OBREQHTB.MS_NO 에 정상 적재되는지 검증
□ UI / JavaScript 바이트 검증 — 구매의뢰명칭(50 Byte), 상세설명(400 Byte) 입력 오버플로우 방지 유효성 검증
□ /copyRequest — getNewReqNo 내부 OBSLPHTB 및 OBREQHTB UNION 쿼리 상의 PostgreSQL 연산 적합성
□ Oracle (+) 아우터 조인 사용 — 향후 표준 ANSI LEFT JOIN 으로 전환 고려
```
