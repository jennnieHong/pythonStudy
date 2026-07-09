# Admin_Master_00005 — 상품조회(어드민) 단위 테스트케이스

> **화면**: [ADMIN] 마스터관리 > 상품관리 > 상품조회  
> **URL Prefix**: `POST /backoffice/data/admin/master/admin_master_00005`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **특이사항**: SELECT 전용 화면 (CUD 없음), setFg 분기로 레시피/세트 조회 결정
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 엔드포인트 목록 (9개)

> **💡 특이사항**: 일부 API(공통 모듈 및 동적 쿼리 사용)는 백엔드 정적 분석으로 연관 테이블 추적이 불가하여 별도 표기함.


| # | URL | 기능 | ServiceType  관련 테이블 |
|---|---|---|---|
| 1 | `/search` | 상품 목록 조회 (페이징 + 필터) | SELECT | MNAMEMTB<br>TGOODSTB<br>TPRICETB |
| 2 | `/modalSearch` | 상품 상세 조회 (setFg 분기) | SELECT | MMEMBSTB<br>MNAMEMTB<br>TCHAINTB<br>TGOODSTB<br>TMBUMSTB<br>TPRICETB |
| 3 | `/getRecipe` | 레시피 조회 | SELECT | MNAMEMTB |
|4|`/getSet`|세트 구성상품 조회|SELECT| 공통 모듈/동적 쿼리 (추적 불가) |
| 5 | `/getAllRecipe` | 구성상품 기준 레시피 전체 조회 | SELECT | MMEMBSTB |
| 6 | `/getExtra` | 부가메뉴 조회 | SELECT | TMBUMSTB |
|7|`/getSpecInfo`|레시피 상세 구성상품 조회|SELECT| 공통 모듈/동적 쿼리 (추적 불가) |
| 8 | `/getShopBrandCd` | 브랜드샵 여부 조회 | SELECT | TCHAINTB |
| 9 | `/getDeptList` | 부서 목록 조회 | SELECT | TDEPTMTB |

---

## 1. `/search` — 상품 목록 조회

**서비스 로직**: `selectGoodsList()` → `getDeliveryType()` → deliveryType 코드→명칭 매핑 (이중 for 루프)

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 1-1 | 전체 조회 (1페이지) | `{"offset":0,"limit":10,"chain_no":"C001"}` | `{"total":N,"rows":[...]}`, deliveryTypeNm 세팅 |
| 1-2 | 2페이지 | `{"offset":10,"limit":10}` | startCount=11, endCount=20 |
| 1-3 | 분류 필터 | `{"lclassCd":"L01","mclassCd":"M01","sclassCd":"S01"}` | 해당 분류 상품만 반환 |
| 1-4 | 사용여부 필터 | `{"useFg":"1"}` | 사용중 상품만 |
| 1-5 | 세트구분 필터 | `{"setFg":"2"}` | 레시피 상품만 |
| 1-6 | 상품코드/명 검색 | `{"goodsCdNm":"아메리카노"}` | 이름 포함 상품 |
| 1-7 | 바코드 검색 | `{"barcode":"880012345678"}` | 해당 바코드 상품 |
| 1-8 | **deliveryType NULL 상품** | DB DELIVERY_TYPE=NULL 상품 존재 | deliveryTypeNm 미세팅 (null 허용), 오류 없음 |
| 1-9 | **deliveryType 코드 매핑** | DELIVERY_TYPE='01' 상품 | NmCd 매칭 → deliveryTypeNm 세팅 |
| 1-10 | 결과 없음 | `{"goodsCdNm":"ZZZZZ"}` | `{"total":0,"rows":[]}` |
| 1-11 | offset 누락 | `{"limit":10}` (offset 없음) | ClassCastException/NPE → 500 |
| 1-12 | 미인증 접근 | 세션 없음 | 302 redirect |
| 1-13 | offset을 String으로 전달 | `{"offset":"0","limit":10}` | ClassCastException → 500 ★ |
| 1-14 | chain_no 키 누락 | `{"offset":0,"limit":10}` (chain_no 없음) | `map.get("chain_no")` → null → Mapper null 조건으로 실행 |

---

## 2. `/modalSearch` — 상품 상세 조회 (핵심 분기)

**서비스 로직**:
1. `getChainMsNo(chainNo)` → chain_ms_no 조회 (간접 조회)
2. `getModalList()` → 상품 기본 정보 (setFg, recipeCd, setCd 포함)
3. `getExtraSubList()` → 부가메뉴 목록
4. `getShopBrandCd()` → 브랜드샵 여부
5. **setFg 분기**:
   - `setFg=2` → `getRecipe()` 실행 (레시피 상품)
   - `setFg=3` → `getSetList()` 실행 (세트 상품)
   - 그 외 → recipeList=[], setUnitList=[] 반환

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 2-1 | 일반 상품 조회 (setFg≠2,3) | `chainNo=C000&goodsCd=G001` | `recipeList:[]`, `setUnitList:[]` |
| 2-2 | **레시피 상품 (setFg=2)** | goodsCd가 레시피 상품 | `recipeList:[...]` (레시피 구성), `setUnitList:[]` |
| 2-3 | **세트 상품 (setFg=3)** | goodsCd가 세트 상품 | `recipeList:[]`, `setUnitList:[...]` |
| 2-4 | chainNo로 chain_ms_no 간접 조회 | `chainNo=C000` | getChainMsNo 호출 → chain_ms_no 세팅 |
| 2-5 | 존재하지 않는 goodsCd | `goodsCd=ZZZZZ` | getModalList → null → NPE 위험 |
| 2-6 | chainNo 빈값 | `chainNo=` (defaultValue="") | chain_ms_no=null 또는 "" |
| 2-7 | 브랜드샵 체인 | brandShopCd가 있는 체인 | `brandShopCd:"B001"` 포함 |
| 2-8 | 일반 체인 | brandShopCd 없는 체인 | `brandShopCd:""` 또는 null |
| 2-9 | **존재하지 않는 goodsCd** | getModalList 0건 → null 반환 | NPE → 500 발생 ★ (현재 버그) |
| 2-10 | 응답 키 검증 | 정상 요청 | `master_00005_recipeList` 키 확인 (기존 `recipeList` 아님) |
| 2-11 | 응답 키 검증 | 정상 요청 | `master_00005_setUnitList` 키 확인 (기존 `setUnitList` 아님) |

---

## 3. `/getRecipe` — 레시피 조회

**필수**: `recpCd` (@NotBlank)  
**선택**: `chainNo`, `goodsCd`  
**서비스**: `getChainMsNo(chainNo)` 간접 조회 후 getRecipe

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 3-1 | 정상 조회 | `chainNo=C000&goodsCd=G001&recpCd=R001` | 레시피 구성 List |
| 3-2 | **recpCd 빈값** | `recpCd=` | 400 (@NotBlank) |
| 3-3 | 존재하지 않는 recpCd | `recpCd=RRRRR` | `[]` 빈 리스트 |
| 3-4 | goodsCd 빈값 허용 | `goodsCd=` (defaultValue="") | 정상 처리 |
| 3-5 | 파라미터 키 확인 | `goodsCd=G001` 전달 | Mapper에 `goods_cd`로 주입됨 (카멜→스네이크 변환 확인) |

---

## 4. `/getSet` — 세트 구성상품 조회

**필수**: `chainNo`, `goodsCd` (@NotBlank)  
**선택**: `setCd`

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 4-1 | 정상 조회 | `chainNo=C000&goodsCd=G001&setCd=S001` | 세트 구성상품 List |
| 4-2 | setCd 빈값 허용 | `setCd=` (defaultValue="") | 전체 세트 또는 빈 리스트 |
| 4-3 | **chainNo 빈값** | `chainNo=` | 400 (@NotBlank) |
| 4-4 | **goodsCd 빈값** | `goodsCd=` | 400 (@NotBlank) |
| 4-5 | 존재하지 않는 setCd | `setCd=SSSSS` | `[]` |
| 4-6 | chain_ms_no 필요 여부 | Mapper SQL에서 chain_ms_no 참조 여부 | null 조건 처리 또는 오류 확인 |

---

## 5. `/getAllRecipe` — 구성상품 기준 레시피 전체 조회

**기능**: 특정 원부재료 상품을 사용하는 모든 레시피 조회  
**필수**: `chainNo`, `goodsCd` (@NotBlank)

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 5-1 | 정상 조회 | `chainNo=C000&goodsCd=G001` | 해당 상품을 원부재료로 쓰는 레시피 List |
| 5-2 | 어떤 레시피에도 미사용 | `goodsCd=미사용상품` | `[]` |
| 5-3 | **chainNo 빈값** | `chainNo=` | 400 (@NotBlank) |
| 5-4 | **goodsCd 빈값** | `goodsCd=` | 400 (@NotBlank) |

---

## 6. `/getExtra` — 부가메뉴 조회

**필수**: `chainNo` (@NotBlank)

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 6-1 | 정상 조회 | `chainNo=C000` | 부가메뉴 List (MnameDto) |
| 6-2 | 부가메뉴 없음 | 미등록 체인 | `[]` |
| 6-3 | **chainNo 빈값** | `chainNo=` | 400 (@NotBlank) |

---

## 7. `/getSpecInfo` — 레시피 상세 구성상품 조회

**필수**: `chainNo`, `recp_cd` (@NotBlank)  
**서비스**: `recpSpec()` — 레시피 코드로 구성 원부재료 상세 조회

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 7-1 | 정상 조회 | `chainNo=C000&recp_cd=R001` | 레시피 구성상품 상세 List |
| 7-2 | 존재하지 않는 recp_cd | `recp_cd=RRRRR` | `[]` |
| 7-3 | **recp_cd 빈값** | `recp_cd=` | 400 (@NotBlank) |
| 7-4 | **chainNo 빈값** | `chainNo=` | 400 (@NotBlank) |

---

## 8. `/getShopBrandCd` — 브랜드샵 여부 조회

**필수**: `chainNo` (@NotBlank)

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 8-1 | 브랜드샵 체인 | `chainNo=C000` (브랜드샵) | `"B001"` (브랜드샵코드) |
| 8-2 | 일반 체인 | `chainNo=C000` (일반) | `""` 또는 null |
| 8-3 | **chainNo 빈값** | `chainNo=` | 400 (@NotBlank) |

---

## 9. `/getDeptList` — 부서 목록 조회

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 9-1 | 정상 조회 | `{}` | 부서 List |
| 9-2 | 부서 없음 | - | `[]` |

---

## 서비스 핵심 분기 요약

```
selectGoodsList (배송유형 매핑)
├── deliveryType != null → NmCd 매칭 → deliveryTypeNm 세팅
└── deliveryType == null → 매핑 스킵 (null 유지)

modalSearch (setFg 분기)
├── setFg = "2" → getRecipe() 호출, setUnitList=[]
├── setFg = "3" → getSetList() 호출, recipeList=[]
└── 그 외 → recipeList=[], setUnitList=[] (둘 다 빈 리스트)

modalSearch (chain_ms_no 간접 조회)
└── chainNo → getChainMsNo() → chain_ms_no 주입
    (세션에서 직접 가져오지 않고 DB 조회)
```

---

