# Admin_Master_00004 — 매장관리(어드민) 단위 테스트케이스

> **URL Prefix**: `POST /backoffice/data/admin/master/admin_master_00004`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **외부 트리거**: `Tr_MMCARD_T01_Service` (saveCardContract 호출 시)
> **DB 트리거 영향도**: MMEMBPTB, MMCARDTB, MMEMBVTB, MVANCOTB, MMEMBSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 엔드포인트 목록 (24개)

| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 매장 목록 조회 (페이징) | SELECT | MMEMBSTB<br>MMEMBVTB<br>MNAMEMTB<br>TCHAINTB  |
| 2 | `/msInsert` | 매장 등록 | INSERT | IF_BIZ_CD<br>IF_BLUE_JOS_NO<br>IF_SHOP_CD<br>MMEMBPTB<br>MMEMBSTB<br>MMEMBVTB<br>MSNDNOTB<br>TCHAINTB<br>WFNENVTB  |
| 3 | `/msInfoSelect` | 매장 상세 조회 | SELECT | IF_BIZ_CD<br>IF_BLUE_JOS_NO<br>IF_SHOP_CD<br>MMEMBSTB  |
| 4 | `/msInfoUpdate` | 매장 정보 수정 | UPDATE | IF_BIZ_CD<br>IF_BLUE_JOS_NO<br>IF_SHOP_CD<br>MMEMBSTB  |
| 5 | `/getOpenFg` | 오픈구분 조회 | SELECT | MMEMBSTB  |
| 6 | `/saveOpenFg` | 오픈구분 수정 | UPDATE | MMEMBSTB  |
| 7 | `/getSystemList` | 환경설정 조회 | SELECT | MKITCHTB<br>MMEMBVTB  |
| 8 | `/saveSystemInfo` | 환경설정 저장 | UPDATE/INSERT  MKITCHTB<br>MMEMBVTB |
| 9 | `/posEnvListSelect` | 포스 장비설정 조회 | SELECT | MMEMBPTB  |
| 10 | `/insertMsPosEnv` | 포스 장비 등록 | INSERT | MMEMBPTB  |
| 11 | `/updateMsPosEnv` | 포스 장비 수정 | UPDATE | MMEMBPTB  |
| 12 | `/deleteMsPosEnv` | 포스 장비 삭제 | DELETE | MMEMBPTB  |
| 13 | `/getVanPosList` | VAN(POS) 목록 | SELECT | MVANCOTB<br>VANMSTTB  |
| 14 | `/getVanDanList` | VAN(단말기) 목록 | SELECT | MVANCOTB<br>VANMSTTB  |
| 15 | `/contractNumList` | 카드등록 통합 조회 | SELECT | MCARDMTB<br>MMCARDTB<br>MMEMBPTB<br>MMSCOMTB<br>MNAMEMTB<br>MVANCOTB<br>VANMSTTB  |
| 16 | `/getPosDanGbnList` | VAN사별 단말기구분 목록 | SELECT | VANMSTTB  |
| 17 | `/saveVanPos` | VAN(POS) 등록 | INSERT | MMEMBSTB<br>MVANCOTB  |
| 18 | `/updateVanPos` | VAN(POS) 수정 | UPDATE | MVANCOTB  |
| 19 | `/deletePosVan` | VAN(POS) 삭제 | DELETE | MVANCOTB  |
| 20 | `/saveVanDan` | VAN(단말기) 등록 | INSERT | MMEMBSTB<br>MVANCOTB  |
| 21 | `/updateVanDan` | VAN(단말기) 수정 | UPDATE | MVANCOTB  |
| 22 | `/deleteVanDan` | VAN(단말기) 삭제 | DELETE | MVANCOTB  |
| 23 | `/getCardContract` | 카드 계약번호 조회 | SELECT | MMCARDTB<br>MNAMEMTB  |
| 24 | `/saveCardContract` | 카드 계약번호 저장 | MERGE+TRIGGER  MMCARDTB |

---

## 1. `/search` — 매장 목록 조회 (페이징)

**서비스 로직**: offset/limit → startCount/endCount 변환 → getTotalCnt + selectMsList

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 1-1 | 정상 조회 | `{"offset":0,"limit":10}` | `{"total":N,"rows":[...]}` |
| 1-2 | 2페이지 | `{"offset":10,"limit":10}` | startCount=11, endCount=20 |
| 1-3 | 검색 필터 | `{"offset":0,"limit":10,"msNm":"테스트"}` | 이름 포함 매장만 |
| 1-4 | 결과 없음 | `{"offset":0,"limit":10,"msNm":"ZZZZZ"}` | `{"total":0,"rows":[]}` |
| 1-5 | offset 누락 | `{"limit":10}` (offset 없음) | NPE 또는 500 오류 |
| 1-6 | 미인증 | 세션 없음 | 302 redirect |

---

## 2. `/msInsert` — 매장 등록

**서비스 분기**:
- `chainHqYn=Y` + headOfficecount>0 → `"headOfficeExist"`
- `chainHqYn=Y` + headOfficecount==0 → 정상 등록
- `chainHqYn=N` + headOfficecount==0 → `"noHeadOffice"`
- `chainHqYn=N` + headOfficecount>0 → 정상 등록

**등록 시**: insertMs → insertWebEnv → insertSendNo → insertMsDefaultEnv → insertMsDefaultPosEnv  
**영수증 headMsg/tailMsg**: 빈값 아니면 `"||"` 접미사 추가 후 합산  
**날짜**: openDate/closeDate의 `-` 제거

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 2-1 | 본부 정상 등록 | `chainHqYn=Y`, 해당 체인에 본부 없음 | `"success"`, 5개 INSERT 실행 |
| 2-2 | **본부 중복** | `chainHqYn=Y`, 이미 본부 존재 | `"headOfficeExist"` |
| 2-3 | 가맹점 정상 등록 | `chainHqYn=N`, 체인에 본부 있음 | `"success"` |
| 2-4 | **본부 없이 가맹점 등록** | `chainHqYn=N`, 본부 없음 | `"noHeadOffice"` |
| 2-5 | headMsg01 값 있음 | `headMsg01=안녕하세요` | `"안녕하세요\|\|"` 로 저장 |
| 2-6 | headMsg 전체 빈값 | 모든 headMsg="", tailMsg="" | `"||"` 없이 저장 |
| 2-7 | 날짜 포맷 | `openDate=2026-05-22` | DB에 `20260522` 저장 |
| 2-8 | msNo 자동채번 | 신규 등록 | `"NC" + getNewMsNo()` 형식 |
| 2-9 | @Transactional 롤백 | insertWebEnv 중 오류 | insertMs도 롤백 |

---

## 3. `/msInfoSelect` — 매장 상세 조회

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 3-1 | 정상 조회 | `{"msNo":"NC0007"}` | 매장 상세 Map 반환 |
| 3-2 | 존재하지 않는 msNo | `{"msNo":"XXXXX"}` | null 또는 빈 Map |

---

## 4. `/msInfoUpdate` — 매장 정보 수정

**서비스 로직**: headMsg/tailMsg `"||"` 접미사 처리 + 날짜 `-` 제거 → updateMsInfo

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 4-1 | 정상 수정 | `{"msNo":"NC0007","msNm":"수정매장","headMsg01":"안녕","openDate":"2026-01-01","billAddr01":"서울","billAddr02":"강남"}` | int 1 (1건 UPDATE) |
| 4-2 | billAddr 조합 | `billAddr01=서울, billAddr02=강남` | DB에 `서울\|\|강남` 저장 |
| 4-3 | 날짜 포맷 | `openDate=2026-05-22` | `20260522` 저장 |
| 4-4 | headMsg 일부만 값 | `headMsg01=안녕, headMsg02=` | `안녕\|\|` + `""` = `"안녕\|\|"` |
| 4-5 | 존재하지 않는 msNo | `{"msNo":"XXXXX"}` | int 0 |

---

## 5. `/getOpenFg` + 6. `/saveOpenFg`

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 5-1 | 오픈구분 조회 | `{"msNo":"NC0007"}` | OPEN_FG 포함 Map |
| 5-2 | 없는 msNo | `{"msNo":"XXXXX"}` | null |
| 6-1 | 오픈구분 수정 | `{"msNo":"NC0007","openFg":"1"}` | int 1 |
| 6-2 | 없는 msNo | `{"msNo":"XXXXX"}` | int 0 |

---

## 7. `/getSystemList` — 환경설정 조회

**서비스 분기**: KITCHEN_YN≠0 && KITCHEN_CNT≠0 → getKitchenList 추가 호출

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 7-1 | 정상 조회 (주방프린트 없음) | `{"msNo":"NC0007"}` | systemList + `kitchenList:[]` |
| 7-2 | **주방프린트 있음** | KITCHEN_YN=1, KITCHEN_CNT=3 | kitchenList에 3개 약식명칭 포함 |
| 7-3 | KITCHEN_CNT=0 | KITCHEN_YN=1, KITCHEN_CNT=0 | getKitchenList 미호출 |
| 7-4 | systemList null | 환경설정 미등록 매장 | NPE 위험 → null 처리 확인 |
| 7-5 | **환경설정 미등록 매장** | MMENVTB에 해당 msNo 없음 | NPE → 500 오류 발생 ★ (현재 버그) |

---

## 8. `/saveSystemInfo` — 환경설정 저장

**서비스 분기**: getMsEnvCnt > 0 → updateMsEnv / ==0 → insertMsEnv  
**추가 처리**: kitchenNoArr/kitchenNmArr 배열 반복 → saveKitchenPrint

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 8-1 | **환경설정 신규** | getMsEnvCnt=0 | insertMsEnv 실행, int 반환 |
| 8-2 | **환경설정 수정** | getMsEnvCnt>0 | updateMsEnv 실행 |
| 8-3 | 주방프린트 저장 | `kitchenNoArr=["01","02"], kitchenNmArr=["주방A","주방B"]` | saveKitchenPrint 2회 호출 |
| 8-4 | 배열 빈 경우 | kitchenNoArr=[] | 반복 없이 result만 반환 |
| 8-5 | @Transactional | saveKitchenPrint 도중 오류 | updateMsEnv도 롤백 |
| 8-6 | **kitchenNoArr 키 누락** | RequestBody에 kitchenNoArr 없음 | NPE → 500 ★ |
| 8-7 | **배열 길이 불일치** | `kitchenNoArr=["01","02"]`, `kitchenNmArr=["주방A"]` | IndexOutOfBounds → 500 ★ |
| 8-8 | kitchenNoArr 빈 배열 | `kitchenNoArr=[]` | 루프 0회, result만 반환 (정상) |

---

## 10. `/insertMsPosEnv` — 포스 장비 등록

**서비스 분기**:
- `posMobileType=0` (일반POS): chkMaxPosNo == "79" → `"maxPosNo"` / 아니면 getNewPosNo → INSERT
- `posMobileType≠0` (모바일): chkMaxMobilePosNo == "99" → `"maxMobilePosNo"` / 아니면 getNewMobilePosNo → INSERT

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 10-1 | 일반POS 정상 등록 | `posMobileType=0`, 현재 최대PosNo<79 | `"success"` |
| 10-2 | **일반POS 최대 초과** | posMobileType=0, 최대PosNo=79 | `"maxPosNo"` |
| 10-3 | 모바일POS 정상 등록 | `posMobileType=1`, 최대<99 | `"success"` |
| 10-4 | **모바일POS 최대 초과** | posMobileType=1, 최대=99 | `"maxMobilePosNo"` |

---

## 11. `/updateMsPosEnv` — 포스 장비 수정

**서비스 로직**: macAddIp/dPosCd 빈값이면 `" "` (공백 한칸) 저장

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 11-1 | 정상 수정 (1대) | 1개 POS 배열 | `"success"` |
| 11-2 | 다중 POS 수정 | 3대 POS 배열 | updateMsPosEnv 3회 호출 |
| 11-3 | **macAddIp 빈값** | `macAddIp[0]=""` | DB에 `" "` (공백) 저장 |
| 11-4 | **dPosCd 빈값** | `dPosCd[0]=""` | DB에 `" "` 저장 |
| 11-5 | 빈 배열 | list.size()==0 | updateMsPosEnv 미호출, `""` 반환 |
| 11-6 | **macAddIp 미전달 + POS 2대** | `posSettingFormPosNo[]=01&posSettingFormPosNo[]=02`, macAddIp 파라미터 없음 | ArrayIndexOutOfBounds → 500 ★ |
| 11-7 | macAddIp 미전달 + POS 1대 | 동일, POS 1대 | length=1이므로 `[0]` 접근 OK (정상) |

---

## 17. `/saveVanPos` — VAN(POS) 등록

**서비스 분기** (다단계):
```
checkBizNo
├── biz_cnt>0 → "BizDup"
└── biz_cnt==0
    ├── checkVanCnt
    │   ├── van_cnt>0 → "VanDup"
    │   └── van_cnt==0
    │       ├── vanFg=1(현금) → checkVanCardCnt==0 → "vanCardNull"
    │       └── addFg=Y → insertVanPosCard + insertVanPosCash (2건)
    │           addFg≠Y → insertVanPosCard (1건)
└── return ""(성공)
```

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 17-1 | **사업자번호 중복** | biz_cnt>0 | `"BizDup"` |
| 17-2 | **VAN사 중복** | biz_cnt=0, van_cnt>0 | `"VanDup"` |
| 17-3 | **현금VAN+카드 미등록** | vanFg=1, vanCard_cnt=0 | `"vanCardNull"` |
| 17-4 | 정상 등록 (카드단독) | biz=0, van=0, addFg=N | insertVanPosCard 1회, `""` |
| 17-5 | **현금+카드 동시 등록** | biz=0, van=0, vanFg=1, addFg=Y | insertVanPosCard + insertVanPosCash 2회 |

---

## 18. `/updateVanPos` — VAN(POS) 수정

**분기**: checkCon==0 → `""` / >0 → `"ConDup"` (단, updatePosVan은 항상 실행)

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 18-1 | 계약번호 중복 없음 | con_cnt=0 | `""`, updatePosVan 실행 |
| 18-2 | **계약번호 중복** | con_cnt>0 | `"ConDup"`, updatePosVan도 실행됨 |

---

## 20. `/saveVanDan` — VAN(단말기) 등록

**분기**: BizDup → VanDup → **CatDup**(단말기는 CAT_ID 중복 차단) → insertVanDan

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 20-1 | **사업자 중복** | biz_cnt>0 | `"BizDup"` |
| 20-2 | **VAN단말기 중복** | van_cnt>0 | `"VanDup"` |
| 20-3 | **CAT_ID 중복** | cat_cnt>0 | `"CatDup"` (POS와 달리 차단) |
| 20-4 | 정상 등록 | biz=0, van=0, cat=0 | `""`, insertVanDan 실행 |

> **주의**: `/saveVanPos`는 CAT_ID 중복이어도 저장 허용, `/saveVanDan`은 CatDup 차단. 이 차이를 반드시 검증.

---

## 21. `/updateVanDan` — VAN(단말기) 수정

**분기**: checkVanCon==0 → updateVanDan 실행 / >0 → `"ConDup"`, **UPDATE 미실행**

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 21-1 | 정상 수정 | con_cnt=0 | `""`, DB UPDATE |
| 21-2 | **계약번호 중복** | con_cnt>0 | `"ConDup"`, UPDATE 미실행 |

> `/updateVanPos`와 차이: updateVanPos는 중복이어도 UPDATE 실행, updateVanDan은 중복이면 UPDATE 미실행.

---

## 24. `/saveCardContract` — 카드 계약번호 저장 (가장 복잡)

**서비스 로직**:
1. 기존 카드계약 조회 → 각 건에 `Tr_MMCARD_T01_Service.processTrigger("D")` 호출
2. `deleteCardContract` (기존 삭제)
3. cardCoArr 반복 → `mergeMmcard` + `Tr_MMCARD_T01_Service.processTrigger("A"/"U")` 호출

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 24-1 | 신규 카드계약 등록 | `cardCoArr=["BC"],contractNoArr=["1234567890"]` | mergeMmcard 1건, triggerA 1회 |
| 24-2 | 기존 계약 전체 교체 | 기존 2건 + 신규 3건 | trigger D 2회 → delete → merge+triggerA 3회 |
| 24-3 | **old 존재 시 procFg=U** | old 값이 있는 카드사 | `paramMap.put("procFg","U")` 확인 |
| 24-4 | 빈 배열로 전체 삭제 | `cardCoArr=[]` | 기존 전체 삭제, 신규 없음 |
| 24-5 | **@Transactional 롤백** | mergeMmcard 중 오류 | deleteCardContract도 롤백, 기존 데이터 보존 |
| 24-6 | trigger 호출 순서 | - | getOldValues → processTrigger 순서 반드시 확인 |
| 24-7 | **ediFg 고정 확인** | 모든 신규 등록 | DB에 `EDIT_FG='Y'` 저장 확인 |
| 24-8 | **msCardNo 동일값** | contractNo="1234567890" | `MSCARD_NO='1234567890'` 저장 확인 |
| 24-9 | **procFg A→U 전환** | MMCARDTB에 동일 카드사 기존 데이터 있음 | `getOldValues` old 맵 비어있지 않음 → `procFg="U"` |
| 24-10 | procFg A 유지 | 신규 카드사 (기존 데이터 없음) | old 빈 맵 → `procFg="A"` 유지 |

---

## 서비스 핵심 분기 요약

```
msInsert (chainHqYn)
├── Y + 본부 있음 → "headOfficeExist"
├── Y + 본부 없음 → 정상 등록 (5개 INSERT)
├── N + 본부 없음 → "noHeadOffice"
└── N + 본부 있음 → 정상 등록

insertMsPosEnv (posMobileType)
├── 0 (일반POS): maxPosNo==79 → "maxPosNo"
└── 기타 (모바일): maxMobilePosNo==99 → "maxMobilePosNo"

saveSystemInfo (getMsEnvCnt)
├── >0 → updateMsEnv
└── ==0 → insertMsEnv

saveVanPos (다단계)
BizDup → VanDup → vanCardNull(현금) → addFg=Y(2건) or N(1건)

saveVanDan vs saveVanPos 차이
└── CAT_ID 중복: VanPos=허용, VanDan=차단(CatDup)

updateVanPos vs updateVanDan 차이
└── ConDup 시: VanPos=UPDATE실행+ConDup반환, VanDan=UPDATE미실행+ConDup반환

saveCardContract
└── 전체삭제+재등록 + Tr_MMCARD_T01_Service 트리거 호출 (D→A/U)
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `MMEMBSTB` | 체인/매장 기본 데이터 |
| `MMCHATB` | 체인 마스터 (chainHqYn 체크용) |
| `MMEMBPTB` | POS 단말기 (posEnv 관련) |
| `MMENVTB` | 환경설정 테이블 |
| `MVANCOTB` | VAN 계약 |
| `MMCARDTB` | 카드사 계약 (saveCardContract) |
| `MVENWTB` | WebEnv 테이블 |

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
├── [테이블] MMCARDTB (CUD 작업)
│   └── (Trigger) Tr_MMCARD_T01
├── [테이블] MMEMBPTB (CUD 작업)
│   └── (Trigger) Tr_MMEMBP_T01
├── [테이블] MMEMBSTB (CUD 작업)
│   └── (Trigger) Tr_MMEMBS_T01
├── [테이블] MMEMBVTB (CUD 작업)
│   └── (Trigger) Tr_MMEMBV_T01
├── [테이블] MVANCOTB (CUD 작업)
│   └── (Trigger) Tr_MVANCO_T01
└── [공통 영향 테이블 및 호출]
    ├── MMEMLGTB [매장정보변경 HISTORY]
    ├── MMSLOGTB [MASTER LOG]
    ├── MMSPOSTB [매장별 POS MASTER]
    ├── MUSERSTB
    ├── SSCARDTB [POS와 표준카드사 MASTER 응답]
    ├── SSMEMBTB [POS와의 명판(매장) MASTER 응답]
    ├── SSMEMPTB [매장 포스별 환경 설정 마스타 LOG]
    ├── SVANCOTB [POS와의 가맹점과 VAN사 계약번호 응답]
    ├── [FUNCTION] F_GET_CUR_INFO (MNAMEMTB)
    ├── [FUNCTION] F_GET_NETAMT (MMEMBVTB)
    ├── [FUNCTION] F_GET_SALE_NETAMT (MMEMBVTB)
    ├── [FUNCTION] F_GET_USUPRICE_VAT (MMEMBVTB)
    ├── [FUNCTION] F_SALE_FG (MCARDMTB)
    ├── [FUNCTION] GET_SMS_CHAIN (MMEMBSTB)
    ├── [PROCEDURE] CNTPROC (MMEMBSTB)
    ├── [PROCEDURE] P_INITCOST (MUSERSTB)
    ├── [PROCEDURE] P_MACOST_B (MUSERSTB)
    ├── [PROCEDURE] P_TACOST_B (MUSERSTB)
    ├── [PROCEDURE] SUB_CALC_FIX_AMT_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_COUPON_NEW_SHOP_P_TEMP (MMEMBSTB)
    ├── [PROCEDURE] SUB_COUPON_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_CUSTCL_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_EMSWRK_P (MUSERSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_RECV_P (MCARDMTB)
    ├── [PROCEDURE] SUB_IF_HYDM_RECV_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MMCARDTB)
    ├── [PROCEDURE] SUB_IF_HYDM_SEND_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_IMTRLG_I (MMEMBSTB)
    ├── [PROCEDURE] SUB_MASTER_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_NEWCUSTMSG_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_RECIPE_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SET_IO_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SET_IO_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_SL_RECIPE_GOODS_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SL_SET_GOODS_P (MNAMEMTB)
    ├── [PROCEDURE] SUB_SNETDT_P (MMEMBVTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_AFTER_PROC_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_MAIN_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_FIFO_PROC_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_STOCK_MGMVHD_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_TEMP2GD_P (MMEMBVTB)
    ├── [PROCEDURE] SUB_TEMPGD_P (MMEMBVTB)
    ├── [PROCEDURE] SUB_TMPRGD_P01 (MMEMBSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_P (MMEMBSTB)
    ├── [PROCEDURE] SUB_TOT_AVG_SINGLE_P (MMEMBSTB)
    └── [PROCEDURE] SUB_VDORDER_P (MMEMBSTB)
```
