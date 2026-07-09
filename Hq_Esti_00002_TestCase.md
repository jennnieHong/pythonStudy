# Hq_Esti_00002 — 견적서 양식작성 단위 테스트케이스

> **화면**: [HQ] 견적관리 > 견적서 양식작성  
> **URL Prefix**: `POST /backoffice/data/hq/estimate/hq_esti_00002`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}
> **DB 트리거 영향도**: TPRICETB, TESFRHTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 (자동주입) |
| `msNo` | `NC0001` | 본부 매장번호 (자동주입) |
| `ID` | `7249525SHOP` | 로그인 사용자 ID (자동주입) |

---

## 엔드포인트 목록 (10개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 견적양식 목록 조회 | SELECT | TESFRHTB<br>TESFRVTB |
| 2 | `/detailSearch` | 견적양식 대상 상품 조회 | SELECT | TESFRHTB |
| 3 | `/goodsSearch` | 등록 가능 상품 조회 (페이징 + goodsCdArr 필터) | SELECT | TESFRDTB<br>TESTYMTB |
| 4 | `/selectEstiGoodsList` | 견적유형 신규 상품 조회 | SELECT | TESTYGTB<br>TGOODSTB |
| 5 | `/save` | 견적양식 등록/수정 (estimFromCd 분기 + estimFromCp 복사) | TESFRDTB<br>TESFRHTB |
|6|`/delete`|견적양식 삭제 (배열 연쇄)|DELETE| 공통 모듈/동적 쿼리 (추적 불가) |
| 7 | `/goodsSave` | 대상 상품 등록 (goodsArr 배열) | INSERT | TESFRDTB |
| 8 | `/goodsSaveAll` | 대상 상품 전체 등록 (goodsCdArr 필터) | INSERT | TESFRDTB<br>TESTYMTB<br>TPRICETB |
| 9 | `/goodsUpdate` | 대상 상품 수정 (goodsArr 배열) | UPDATE | TESFRDTB |
|10|`/goodsDelete`|대상 상품 삭제 (goodsCd_arr 배열)|DELETE| 공통 모듈/동적 쿼리 (추적 불가) |
| 11 | `/goodsUpload` | 상품 수량 엑셀 업로드 (POI) | UPDATE | TESFRDTB |

---

## 1. `/search` — 견적양식 목록 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001` | `{}` | 견적양식 List |
| 1-2 | chainNo=`C001` | `{"estimTypeCd":"E001"}` | 특정 견적유형 양식만 |
| 1-3 | chainNo=`C001` (등록 없음) | `{}` | `[]` |

---

## 2. `/detailSearch` — 견적양식 대상 상품 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{"estimFromCd":"F001"}` | 해당 양식 대상 상품 List |
| 2-2 | chainNo=`C001` | `{"estimFromCd":"XXXXX"}` | `[]` |

---

## 3. `/goodsSearch` — 등록 가능 상품 조회 (페이징)

**컨트롤러 분기: goodsCdArr 필터링**
```
goodsCdArr != "ALL" AND goodsCdArr.trim() != ""
├── true  → split(",") → goodsCdList 배열로 변환, 쿼리 IN 조건 적용
└── false → goodsCdList 미세팅, 전체 조회
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{"offset":0,"limit":10,"goodsCdArr":"ALL"}` | 전체 상품 조회 (goodsCdList 미세팅) |
| 3-2 | chainNo=`C001` | `{"offset":0,"limit":10,"goodsCdArr":"G001,G002,G003"}` | G001,G002,G003만 조회 (IN 조건) |
| 3-3 | chainNo=`C001` | `{"offset":0,"limit":10,"goodsCdArr":""}` | 전체 조회 (trim 빈값 → 필터 미적용) |
| 3-4 | chainNo=`C001` | `{"offset":0,"limit":10,"goodsCdArr":"G001"}` | G001 단건 조회 |
| 3-5 | chainNo=`C001` | `{"limit":10}` (offset 없음) | ClassCastException → 500 |
| 3-6 | chainNo=`C001` | `{"offset":0,"limit":10}` (goodsCdArr 없음) | `commandMap.get("goodsCdArr")` → **NPE** |
| 3-7 | goodsSearch 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 4. `/selectEstiGoodsList` — 신규 상품 조회

**세션 주입**: `chainNo`, `msNo`

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`, msNo=`NC0001` | `{"estimTypeCd":"E001"}` | 견적유형 기준 신규 상품 List |
| 4-2 | chainNo=`C001`, msNo=`NC0001` | `{}` | 전체 신규 상품 또는 `[]` |
| 4-3 | selectEstiGoodsList 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 5. `/save` — 견적양식 등록/수정

**서비스 분기 ①: estimFromCd 비어있음 여부**
```
estimFromCd == "" → 신규 등록
  └── getNewFromCd() → 자동채번
  └── insertEstiMaster()
  └── estimFromCp != "" → copyEstiGoods() (기존 양식 상품 복사)

estimFromCd != "" → 수정
  └── updateEstiMaster()
```

**서비스 분기 ②: estimFromCp (복사 여부)**
```
신규 등록 시에만 적용
estimFromCp != "" → copyEstiGoods() 실행 (다른 양식 상품 복사)
estimFromCp == "" → 빈 양식으로 등록
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 5-1 | chainNo=`C001`, ID=`7249525SHOP` | `{"estimFromCd":"","estimFromNm":"배달양식","estimTypeCd":"E001","estimFromCp":""}` | 신규 등록, 자동채번 estimFromCd 포함 commandMap 반환 |
| 5-2 | chainNo=`C001`, ID=`7249525SHOP` | `{"estimFromCd":"","estimFromNm":"복사양식","estimTypeCd":"E001","estimFromCp":"F001"}` | 신규 등록 + F001 상품 복사 (copyEstiGoods) |
| 5-3 | chainNo=`C001`, ID=`7249525SHOP` | `{"estimFromCd":"F002","estimFromNm":"수정양식","estimTypeCd":"E001","estimFromCp":""}` | 수정 (updateEstiMaster만 실행) |
| 5-4 | chainNo=`C001` | `{}` (estimFromCd 없음) | `param.get("estimFromCd").toString()` → **NPE** |
| 5-5 | chainNo=`C001` | `{"estimFromCd":null}` | **NPE** |
| 5-6 | chainNo=`C001` | `{"estimFromCd":"","estimFromCp":null}` | 신규 이후 `estimFromCp.toString()` → **NPE** |

---

## 6. `/delete` — 견적양식 삭제

**서비스 로직**: `masterArr` 배열 → 각 건 `deleteEstiMaster + deleteEstiGoods`

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 6-1 | chainNo=`C001` | `{"masterArr":[{"estimFromCd":"F001","estimTypeCd":"E001"}]}` | F001 양식 + 대상상품 연쇄 삭제 |
| 6-2 | chainNo=`C001` | `{"masterArr":[{"estimFromCd":"F001"},{"estimFromCd":"F002"}]}` | 2건 순차 삭제 |
| 6-3 | chainNo=`C001` | `{"masterArr":[]}` | 반복 없음, 정상 종료 |
| 6-4 | - | `{}` (masterArr 없음) | **NPE** (null 캐스팅) |

---

## 7. `/goodsSave` — 대상 상품 등록 (goodsArr 배열)

**Hq_Esti_00001과 다른 점**: 배열 키가 `goodsArr` (Map 배열), Esti_00001은 `goodsCd_arr` (String 배열)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 7-1 | chainNo=`C001`, ID=`7249525SHOP` | `{"estimTypeCd":"E001","estimFromCd":"F001","goodsArr":[{"estimGoodsCd":"G001","qty":10}]}` | 1건 INSERT |
| 7-2 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001","goodsArr":[{"estimGoodsCd":"G001"},{"estimGoodsCd":"G002"}]}` | 2건 각각 INSERT |
| 7-3 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001","goodsArr":[]}` | 반복 없음, 정상 종료 |
| 7-4 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001"}` (goodsArr 없음) | **NPE** |

---

## 8. `/goodsSaveAll` — 대상 상품 전체 등록

**컨트롤러 분기: goodsCdArr 필터 (goodsSearch와 동일 로직)**
```
goodsCdArr != "ALL" AND !trim().isEmpty() → split(",") → goodsCdList
그 외 → goodsCdList 미세팅 (전체 등록)
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 8-1 | chainNo=`C001`, ID=`7249525SHOP` | `{"estimTypeCd":"E001","estimFromCd":"F001","goodsCdArr":"ALL"}` | 전체 상품 일괄 INSERT |
| 8-2 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001","goodsCdArr":"G001,G002"}` | G001,G002만 등록 (IN 필터) |
| 8-3 | chainNo=`C001` | `{}` (goodsCdArr 없음) | `commandMap.get("goodsCdArr")` → **NPE** |

---

## 9. `/goodsUpdate` — 대상 상품 수정 (goodsArr 배열)

**서비스 로직**: `goodsArr` 배열 → 각 건 `updateEstiGoods`

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 9-1 | chainNo=`C001`, ID=`7249525SHOP` | `{"estimTypeCd":"E001","estimFromCd":"F001","goodsArr":[{"estimGoodsCd":"G001","qty":20}]}` | 1건 UPDATE |
| 9-2 | chainNo=`C001` | `{"goodsArr":[]}` | 반복 없음, 정상 종료 |
| 9-3 | chainNo=`C001` | `{}` (goodsArr 없음) | **NPE** |

---

## 10. `/goodsDelete` — 대상 상품 삭제

**서비스 로직**: `goodsCd_arr` 배열 → 각 건 `deleteEstiGoods`  
(**goodsArr와 다름** — String/Object 배열 키 이름 확인)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 10-1 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001","goodsCd_arr":["G001"]}` | 1건 DELETE |
| 10-2 | chainNo=`C001` | `{"estimTypeCd":"E001","estimFromCd":"F001","goodsCd_arr":["G001","G002"]}` | 2건 DELETE |
| 10-3 | chainNo=`C001` | `{"goodsCd_arr":[]}` | 반복 없음, 정상 종료 |
| 10-4 | chainNo=`C001` | `{}` (goodsCd_arr 없음) | **NPE** |

---

## 11. `/goodsUpload` — 상품 수량 엑셀 업로드

**Content-Type**: `multipart/form-data`  
**파라미터**: `estimTypeCd` (@NotBlank), `estimFromCd` (@NotBlank), 파일  
**서비스 로직**:
1. `commonModuleService.getExcelUploadList()` → POI로 엑셀 파싱 → List<Map> 생성
2. 각 행에 `chainNo`, `userId`, `estimTypeCd`, `estimFromCd` 주입
3. `updateEstiGoods(map)` 건별 실행

| No | 세션 조건 | Request (multipart) | 예상값 |
|----|----------|---------------------|-------|
| 11-1 | chainNo=`C001`, ID=`7249525SHOP` | 정상 xlsx 파일 + `estimTypeCd=E001&estimFromCd=F001` | 엑셀 행 수만큼 updateEstiGoods 실행 |
| 11-2 | ID=`7249525SHOP` | xls (구버전) 파일 | HSSFWorkbook 처리 (POI 분기) |
| 11-3 | ID=`7249525SHOP` | 빈 엑셀 (0행) | 반복 없음, 정상 종료 |
| 11-4 | ID=`7249525SHOP` | 파일 없음 (iterator.hasNext()=false) | file=null → getExcelUploadList(null) → NPE 또는 처리 |
| 11-5 | - | `estimTypeCd=` | 400 (@NotBlank) |
| 11-6 | - | `estimFromCd=` | 400 (@NotBlank) |
| 11-7 | - | 손상된 엑셀 파일 | POI 파싱 예외 → @Transactional 롤백 |
| 11-8 | **multipart 아닌 요청** | Content-Type=application/json | 309번 **ClassCastException → 500** ★ |
| 11-9 | **파일 첨부 없이 요청** | multipart 요청이지만 파일 미첨부 | iterator.hasNext()=false → file=null → 서비스 **NPE → 500** ★ |

---

## 서비스 핵심 분기 요약

```
save (견적양식 등록/수정)
├── estimFromCd == "" → getNewFromCd() + insertEstiMaster()
│   └── estimFromCp != "" → copyEstiGoods() (기존 양식 상품 복사)
└── estimFromCd != "" → updateEstiMaster()
주의: estimFromCd/estimFromCp 키 없거나 null → NPE

goodsSearch / goodsSaveAll (goodsCdArr 분기)
├── "ALL" 또는 빈값 → 전체 조회/등록 (goodsCdList 미세팅)
└── 콤마 구분 값 → split(",") → goodsCdList 배열, IN 조건 적용
주의: goodsCdArr 키 자체 없으면 NPE

배열 처리 키 이름 혼재 주의
  goodsSave / goodsUpdate : "goodsArr"  (Map 배열)
  goodsDelete             : "goodsCd_arr" (String/Object 배열)
```

---

## Hq_Esti_00001 vs Hq_Esti_00002 차이점

| 항목 | Hq_Esti_00001 (견적유형) | Hq_Esti_00002 (견적양식) |
|------|------------------------|------------------------|
| 마스터 코드 키 | `estimTypeCd` | `estimFromCd` |
| 신규 채번 | `getNewTypeCd()` | `getNewFromCd()` |
| 복사 기능 | 없음 | `estimFromCp` → `copyEstiGoods()` |
| goodsSearch 필터 | 없음 | `goodsCdArr` → IN 조건 |
| goodsSave 배열 키 | `goodsCd_arr` | `goodsArr` (Map 배열) |
| 엑셀 업로드 | 없음 | `/goodsUpload` (POI) |

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `HESTIMASTTB` | 견적유형(E001), 견적양식(F001) 마스터 |
| `HESTIGOODSTB` | 견적 대상 상품 |
| `MGOODSTB` | 등록 가능 상품 목록 |
| `MMCHATB` | chainNo=C001 체인 마스터 |
| 엑셀 파일 | 상품코드, 수량 컬럼 포함 xlsx/xls |

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] TESFRHTB (CUD 작업)
│   ├── (Trigger) Tr_TESFRH_T01
│   └── (Trigger) Tr_TESFRH_T02
└── [테이블] TPRICETB (CUD 작업)
    └── (Trigger) Tr_TPRICE_T01
```
