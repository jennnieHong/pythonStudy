# Hq_Vendor_00001 — 구매의뢰요청관리 단위 테스트케이스

> **화면**: 본사 > 매입발주 > 매입관리 > 구매의뢰요청관리
> **URL Prefix**: `POST /backoffice/data/hq/vendor/hq_vendor_00001`
> **@Transactional**: 적용됨 (RuntimeException, Exception rollback 대상)
> **요청 방식 혼용**: `@RequestBody Map<String, Object>` 형태 활용
> **DB 트리거 영향도**: 없음 (해당 화면의 주요 테이블 `OBREQHTB`, `OBREQDTB`에는 트리거가 설정되어 있지 않아 연쇄 동작 없음)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | 전 엔드포인트 |
| `ID`      | `shopadmin` | `saveRequest`, `addRequestGoods`, `copyRequest`, `confirmRequest` |

---

## 엔드포인트 목록 (10개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/getReqHdList` | 구매 요청 전표 리스트 조회 | `@RequestBody` | `List` | SELECT | OBREQHTB, MMEMBSTB |
| 2 | `/saveRequest` | 구매 요청 전표 마스터 저장 | `@RequestBody` | `void` | MERGE | OBREQHTB |
| 3 | `/getReqGoodsList` | 구매 요청 전표 상세내역(상품) 조회 | `@RequestBody` | `List` | SELECT | OBREQDTB, TGOODSTB, MNAMEMTB, TESHISTB |
| 4 | `/getNotReqGoodsList` | 구매의뢰 상품 검색 (미등록 상품 조회) | `@RequestBody` | `Map` (total+rows) | SELECT | TGOODSTB, TVNDRGTB, OBREQDTB, TPRICETB, MNAMEMTB |
| 5 | `/addRequestGoods` | 상품 품목 추가 | `@RequestBody` | `void` | MERGE/INSERT | OBREQDTB, TESFRHTB, TESVDUTB, OBSLPHTB, OBSLPDTB, TVNDRGTB |
| 6 | `/deleteRequestGoods` | 상품 품목 개별 삭제 | `@RequestBody` | `void` | DELETE | OBREQDTB |
| 7 | `/copyRequest` | 전표 복사 (헤더 및 디테일) | `@RequestBody` | `void` | INSERT | OBREQHTB, OBREQDTB |
| 8 | `/deleteRequest` | 전표 삭제 (헤더 및 디테일 일괄) | `@RequestBody` | `void` | DELETE | OBREQHTB, OBREQDTB |
| 9 | `/printRequest` | 전표 인쇄 팝업 조회 | `@RequestBody` | `ModelAndView` | SELECT | OBREQHTB, OBREQDTB |
| 10 | `/confirmRequest` | 전표 등록 확정 | `@RequestBody` | `void` | UPDATE | OBREQHTB |

---

## 1. `/getReqHdList` — 구매 요청 전표 리스트 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{"msNo":"MS001","purReqNm":""}` | 해당 매장의 전표 목록 반환 |
| 1-2 | chainNo=`C001` | `{"msNo":"MS001","purReqNm":"테스트"}` | 명칭으로 필터링된 목록 반환 |

---

## 2. `/saveRequest` — 구매 요청 전표 마스터 저장

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001`, ID=`shopadmin` | `{"reqNo":"","msNo":"MS001","purReqNm":"의뢰명"}` | 신규 전표 번호 생성 후 INSERT (`void`) |
| 2-2 | chainNo=`C001`, ID=`shopadmin` | `{"reqNo":"2026...","msNo":"MS001"}` | 기존 전표 UPDATE (`void`) |

---

## 3. `/getReqGoodsList` — 전표 상세내역 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"reqNo":"20260602..."}` | 전표에 속한 품목 리스트 반환 |
| 3-2 | chainNo=`C001` | `{"reqNo":""}` | 빈 배열 또는 전체 조회 방지 |

---

## 4. `/getNotReqGoodsList` — 상품 검색

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001` | `{"reqNo":"...","lclassCd":"","offset":0,"limit":20}` | 전표에 포함되지 않은 상품 목록 (페이징) |
| 4-2 | chainNo=`C001` | `{"reqNo":"...","goodsCdNm":"커피"}` | 상품명/코드로 검색 |

---

## 5. `/addRequestGoods` — 상품 품목 추가

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | chainNo=`C001`, ID=`shopadmin` | `{"msNo":"MS001","reqNo":"...", "goodsCdArr":["G01"], "requestQtyArr":[2]}` | 지정된 상품과 수량이 상세 테이블에 삽입됨 |

---

## 6. `/deleteRequestGoods` — 상품 품목 개별 삭제

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 6-1 | ID=`shopadmin` | `{"reqNo":"2026...", "goodsCdArr":["G01"]}` | 상세 테이블(`OBREQDTB`)에서 지정된 상품 데이터 삭제됨 |

---

## 7. `/copyRequest` — 전표 복사

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 7-1 | chainNo=`C001`, ID=`shopadmin` | `{"msNo":"MS001","reqNo":"20260602..."}` | `getNewReqNo`로 신규 채번 후 마스터/디테일 일괄 복사 |

---

## 8. `/deleteRequest` — 전표 삭제

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 8-1 | ID=`shopadmin` | `{"reqNoArr":["20260602..."]}` | 전표 마스터(`OBREQHTB`)와 디테일(`OBREQDTB`) 데이터 일괄 삭제 |

---

## 9. `/printRequest` — 전표 인쇄 팝업 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 9-1 | chainNo=`C001` | `{"reqNo":"20260602..."}` | 인쇄용 HTML 마크업 및 데이터 바인딩 ModelAndView 반환 |

---

## 10. `/confirmRequest` — 전표 등록 확정

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 10-1 | ID=`shopadmin` | `{"reqNoArr":["20260602..."]}` | 전표의 상태(PROC_FG)가 확정 상태('5')로 업데이트 |

---

## 주요 검증 포인트

```
□ /getNotReqGoodsList — offset 미전달 시 (int)map.get("offset") 형변환 NPE 위험 
□ /addRequestGoods — 배열 파라미터 (goodsCdArr 등) 길이 불일치 또는 미전달 시 Exception
□ /copyRequest — getNewReqNo 내부 서브쿼리 채번 시 text와 integer간 산술 연산 오류 검증 필수
□ /getReqGoodsList — ESTIM_SEQ 등 문자열 뺄셈(-) 시 PSQLException 방지 처리 필수
□ SYSDATE 함수 사용 여부 — EPAS 호환 여부 점검 (NOW() 등 권장)
□ Oracle (+) 아우터 조인 사용 — 향후 표준 ANSI LEFT JOIN 으로 전환 고려
```

---

## DB 트리거 및 프로시저 연관관계도

```text
API Endpoint 호출 (Service Logic)
├── [테이블] OBREQHTB (CUD 작업)
│   └── (Trigger) 없음 (연쇄 동작 미발생)
├── [테이블] OBREQDTB (CUD 작업)
│   └── (Trigger) 없음 (연쇄 동작 미발생)
```

> **결론**: 본 화면은 CUD 조작이 일어나는 핵심 테이블에 데이터베이스 트리거 또는 프로시저가 연결되어 있지 않습니다. 따라서 트랜잭션 도중 트리거로 인해 다른 테이블 데이터를 암묵적으로 변경하는 부작용(Side Effect) 및 성능 저하 요소가 일절 존재하지 않음을 확인했습니다.
