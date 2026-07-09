# Hq_Esti_00001 — 견적유형마스터 단위 테스트케이스

> **화면**: [HQ] 견적관리 > 견적유형마스터  
> **URL Prefix**: `POST /backoffice/data/hq/estimate/hq_esti_00001`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}
> **DB 트리거 영향도**: 연관 테이블(TESTYMTB, TESTYGTB) 관련 DB 수준 트리거 및 프로시저 영향도 없음 (Java Service단에서 CUD 처리)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C002` | 체인 번호 (자동주입) |
| `ID` | `shopadmin` | 로그인 사용자 ID (자동주입) |

---

## 엔드포인트 목록 (8개)

| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 견적유형 목록 조회 | SELECT | TESTYMTB, MUSERSTB |
| 2 | `/detailSearch` | 견적유형 대상 상품 조회 | SELECT | TESTYMTB, TESTYGTB, TGOODSTB, MNAMEMTB |
| 3 | `/goodsSearch` | 등록 가능 상품 조회 (페이징 적용) | SELECT | TGOODSTB, MNAMEMTB, TESTYGTB |
| 4 | `/save` | 견적유형 등록/수정 (estimTypeCd 분기) | INSERT / UPDATE | TESTYMTB |
| 5 | `/delete` | 견적유형 삭제 (마스터 및 대상상품 연쇄 삭제) | DELETE | TESTYMTB, TESTYGTB |
| 6 | `/goodsSave` | 대상 상품 등록 (goodsCd_arr 배열) | INSERT | TESTYGTB |
| 7 | `/goodsSaveAll` | 대상 상품 전체 등록 (조회 조건 적용) | INSERT | TESTYGTB, TGOODSTB |
| 8 | `/goodsDelete` | 대상 상품 삭제 (goodsCd_arr 배열) | DELETE | TESTYGTB |

---

## 1. `/search` — 견적유형 목록 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C002` | `{}` | 견적유형 List 전체 |
| 1-2 | chainNo=`C002` | `{"searchEstimTypeCd":"001"}` | 특정 견적유형 코드 필터링 조회 |
| 1-3 | chainNo=`C002` | `{"searchEstimTypeNm":"Auto"}` | 특정 견적유형 명칭 필터링 조회 (대소문자 무관) |
| 1-4 | chainNo=`C002` (등록 없음) | `{}` | `[]` (빈 리스트 반환) |

---

## 2. `/detailSearch` — 견적유형 대상 상품 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C002` | `{"estimTypeCd":"001"}` | 해당 유형에 매핑된 상품 상세 목록 |
| 2-2 | chainNo=`C002` | `{"estimTypeCd":"XXX"}` | `[]` |
| 2-3 | chainNo=`C002` | `{}` (estimTypeCd 누락) | 비어있는 맵 키에 따른 결과 없거나 예외 |

---

## 3. `/goodsSearch` — 등록 가능 상품 조회 (페이징)

**세션 주입**: `chainNo`
**파라미터 필수값**: `offset` (int), `limit` (int), `estimTypeCd` (String)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C002` | `{"offset":0,"limit":100,"estimTypeCd":"001"}` | 001 유형에 추가 가능한 전체 상품 100건 페이징 조회 |
| 3-2 | chainNo=`C002` | `{"offset":0,"limit":100,"estimTypeCd":"001","goodsCd":"T0000004"}` | 특정 상품코드 필터링 적용 조회 |
| 3-3 | chainNo=`C002` | `{"offset":0,"limit":100,"estimTypeCd":"001","goodsNm":"우유"}` | 특정 상품명 필터링 적용 조회 |
| 3-4 | chainNo=`C002` | `{"limit":100,"estimTypeCd":"001"}` (offset 누락) | ClassCastException 또는 `null` 접근 에러 → 500 |
| 3-5 | chainNo=`C002` | `{"offset":0,"limit":100}` (estimTypeCd 누락) | `estimTypeCd` null 매핑으로 쿼리 조건 불일치 |

---

## 4. `/save` — 견적유형 등록/수정

**서비스 분기**: `estimTypeCd` 비어있음 여부
```
estimTypeCd == "" → 신규 등록
  └── getNewTypeCd() → 자동채번 (MAX+1 형식)
  └── insertEstiMaster()

estimTypeCd != "" → 수정
  └── updateEstiMaster()
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C002`, ID=`shopadmin` | `{"estimTypeCd":"","estimTypeKrNm":"신규유형","estimTypeEnNm":"NewType","estimBigo":"비고내용"}` | 신규 등록 성공, 자동채번된 estimTypeCd가 포함된 Map 반환 |
| 4-2 | chainNo=`C002`, ID=`shopadmin` | `{"estimTypeCd":"004","estimTypeKrNm":"수정유형","estimTypeEnNm":"UpdateType","estimBigo":"수정비고"}` | 수정 성공 (updateEstiMaster 실행) |
| 4-3 | chainNo=`C002` | `{}` (estimTypeCd 누락) | `param.get("estimTypeCd").toString()` → **NPE** |
| 4-4 | chainNo=`C002` | `{"estimTypeCd":null}` | **NPE** |

---

## 5. `/delete` — 견적유형 삭제

**서비스 로직**: `masterArr` 배열을 돌며 `deleteEstiMaster` (TESTYMTB 삭제) 및 `deleteEstiGoods` (TESTYGTB 매핑 상품 일괄 삭제) 호출.

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | chainNo=`C002` | `{"masterArr":[{"estimTypeCd":"004"}]}` | 004 유형 및 매핑 상품 연쇄 삭제 성공 |
| 5-2 | chainNo=`C002` | `{"masterArr":[{"estimTypeCd":"004"},{"estimTypeCd":"005"}]}` | 다중 유형 일괄 삭제 성공 |
| 5-3 | chainNo=`C002` | `{"masterArr":[]}` | 정상 종료 (아무 동작 없음) |
| 5-4 | - | `{}` (masterArr 누락) | **NPE** |

---

## 6. `/goodsSave` — 대상 상품 등록

**서비스 로직**: `goodsCd_arr` 배열 루프 → `insertEstiGoods` 호출 (TESTYGTB에 저장)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 6-1 | chainNo=`C002`, ID=`shopadmin` | `{"estimTypeCd":"004","goodsCd_arr":["T0000004","T0000005"]}` | 2건 상품 매핑 INSERT 성공 |
| 6-2 | chainNo=`C002` | `{"estimTypeCd":"004","goodsCd_arr":[]}` | 정상 종료 (동작 없음) |
| 6-3 | chainNo=`C002` | `{"estimTypeCd":"004"}` (goodsCd_arr 누락) | **NPE** |

---

## 7. `/goodsSaveAll` — 대상 상품 전체 등록

**서비스 로직**: 조건 필터(대/중/소분류, 상품명 등)를 받아 `insertEstiAllGoods`를 수행하여, 아직 매핑되지 않은 조회 조건 하의 모든 상품을 일괄 복사 삽입.

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 7-1 | chainNo=`C002`, ID=`shopadmin` | `{"estimTypeCd":"004","lclassCd":"","mclassCd":"","sclassCd":"","goodsCd":"","goodsNm":""}` | 해당 체인 하의 미매핑 전체 상품 일괄 추가 성공 |
| 7-2 | chainNo=`C002`, ID=`shopadmin` | `{"estimTypeCd":"004","lclassCd":"001","mclassCd":"","sclassCd":"","goodsCd":"","goodsNm":""}` | 대분류 '001' 기준 미매핑 상품 일괄 추가 성공 |
| 7-3 | chainNo=`C002` | `{}` (필수 파라미터 누락) | 쿼리 및 서비스 단에서 null/빈값 바인딩 처리로 전체 추가 실행 가능하나 데이터 상태 확인 필요 |

---

## 8. `/goodsDelete` — 대상 상품 삭제

**서비스 로직**: `goodsCd_arr` 배열 루프 → `deleteEstiGoods` 호출 (TESTYGTB 매핑 해제)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 8-1 | chainNo=`C002` | `{"estimTypeCd":"004","goodsCd_arr":["T0000004","T0000005"]}` | 2건 매핑 해제 DELETE 성공 |
| 8-2 | chainNo=`C002` | `{"estimTypeCd":"004","goodsCd_arr":[]}` | 정상 종료 |
| 8-3 | chainNo=`C002` | `{"estimTypeCd":"004"}` (goodsCd_arr 누락) | **NPE** |

---

## 서비스 핵심 분기 요약

```
save (견적유형 등록/수정)
├── estimTypeCd == "" → getNewTypeCd() + insertEstiMaster()
└── estimTypeCd != "" → updateEstiMaster()
주의: estimTypeCd 키 없거나 null → NPE

goodsSaveAll (대상상품 전체등록)
├── lclassCd/mclassCd/sclassCd/goodsCd/goodsNm 필터 수신
└── hmsfns.TGOODSTB 에서 미매핑 상품(NOT EXISTS)을 select-insert 일괄 처리
```

---

## Hq_Esti_00001 vs Hq_Esti_00002 차이점

| 항목 | Hq_Esti_00001 (견적유형) | Hq_Esti_00002 (견적양식) |
|------|------------------------|------------------------|
| 마스터 코드 키 | `estimTypeCd` | `estimFromCd` |
| 신규 채번 | `getNewTypeCd()` | `getNewFromCd()` |
| 복사 기능 | 없음 | `estimFromCp` → `copyEstiGoods()` |
| goodsSearch 필터 | 없음 | `goodsCdArr` → IN 조건 |
| goodsSave 배열 키 | `goodsCd_arr` (String/Object) | `goodsArr` (Map 배열) |
| 엑셀 업로드 | 없음 | `/goodsUpload` (POI) |
| DB 트리거 연쇄 | 없음 (연쇄 트리거 없음) | 있음 (TPRICETB, TESVDUTB 등 연쇄 동작) |

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `TESTYMTB` | 견적유형마스터 |
| `TGOODSTB` | 마스터 상품 테이블 |
| `MUSERSTB` | 처리자 사용자 정보 (shopadmin) |

---

## 브라우저 E2E 테스트 수행 결과 (Playwright)

* **테스트 구동 스크립트**: [test_hq_esti_01.py](file:///D:/hmTest/backoffice/QaReport/test_hq_esti_01.py)
* **테스트 구동 환경**: Local Tomcat (localhost:8080)
* **테스트 계정**: `shopadmin` (비밀번호 임시 `0000` 설정 후 원복)
* **테스트 일자**: 2026-06-26
* **결과**: **PASS**
* **상세 진행 흐름**:
  1. `shopadmin` 로그인 성공.
  2. 견적유형 등록: `Auto_QA_Type_01` (한글명), `AutoQAType01` (영문명) 저장 -> `004` 코드로 자동 채번.
  3. 상세 조회 및 바인딩: 유형 코드 `004`를 그리드 1에서 정확히 클릭(td.table-onclick)하여 우측 상세 폼 바인딩 및 맵핑 상품(그리드 3) 정상 연동 검증.
  4. 대상 상품 매핑 추가: 그리드 2에서 상위 2건 체크 추가 및 전체 상품(556건) 일괄 추가 연쇄 검증.
  5. 대상 상품 일부 매핑 해제: 그리드 3에서 2건 선택 삭제 및 해제 검증.
  6. 견적유형 삭제: 그리드 1에서 신규 유형 체크박스 선택 후 상단 삭제 버튼 클릭 -> `TESTYMTB` 마스터 및 `TESTYGTB` 매핑 데이터가 일괄 삭제 완료됨을 최종 교차 검증 (Master/Goods Exist: False).
* **증적 스크린샷**: [hq_esti_00001_search.png](file:///D:/hmTest/backoffice/QaReport/hq_esti_00001_search.png)
