# Hq_Master_00004 — 매장관리 단위 테스트케이스

> **화면**: [HQ] 본부관리 > 매장관리  
> **URL Prefix**: `POST /backoffice/data/hq/master/hq_master_00004`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **외부 연동**: `Tr_MMCARD_T01_Service` (TriggerUtil 카드 계약 트리거)
> **DB 트리거 영향도**: MMEMBPTB, MMCARDTB, MMEMBVTB, MVANCOTB, MMEMBSTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 |
| `ID` | `7249525SHOP` | 로그인 사용자 ID |

---

## 엔드포인트 목록 (22개)

| # | URL | 기능 | Type | 관련 테이블 |
|---|---|---|---|---|
| 1 | `/search` | 매장 목록 조회 (페이징) | SELECT | MMEMBSTB<br>MMEMBVTB<br>MNAMEMTB<br>TCHAINTB  |
| 2 | `/msInsert` | 매장 등록 (chainHqYn 3분기) | INSERT | IF_BIZ_CD<br>IF_BLUE_JOS_NO<br>IF_SHOP_CD<br>MMEMBPTB<br>MMEMBSTB<br>MMEMBVTB<br>MSNDNOTB<br>TCHAINTB<br>WFNENVTB  |
| 3 | `/msInfoSelect` | 매장 상세정보 조회 | SELECT | IF_BIZ_CD<br>IF_BLUE_JOS_NO<br>IF_SHOP_CD<br>MMEMBSTB  |
| 4 | `/msInfoUpdate` | 매장 정보 수정 | UPDATE | IF_BIZ_CD<br>IF_BLUE_JOS_NO<br>IF_SHOP_CD<br>MMEMBSTB  |
| 5 | `/getOpenFg` | 오픈구분 조회 | SELECT | MMEMBSTB  |
| 6 | `/saveOpenFg` | 오픈구분 수정 | UPDATE | MMEMBSTB  |
| 7 | `/getSystemList` | 환경설정 조회 (KITCHEN_YN/CNT 분기) | SELECT | MKITCHTB<br>MMEMBVTB  |
| 8 | `/saveSystemInfo` | 환경설정 수정 (msEnvCnt 분기 + kitchenNoArr 배열) | INSERT/UPDATE  MKITCHTB<br>MMEMBVTB |
| 9 | `/posEnvListSelect` | 포스 장비설정 조회 (ModelAndView) | SELECT | MMEMBPTB  |
| 10 | `/insertMsPosEnv` | 포스 장비 등록 (posMobileType 분기, 최대값 체크) | INSERT | MMEMBPTB  |
| 11 | `/updateMsPosEnv` | 포스 장비 수정 (@RequestParam 배열) | UPDATE | MMEMBPTB  |
| 12 | `/deleteMsPosEnv` | 포스 장비 삭제 | DELETE | MMEMBPTB  |
| 13 | `/getVanPosList` | VAN(POS) 목록 조회 | SELECT | MVANCOTB<br>VANMSTTB  |
| 14 | `/getVanDanList` | VAN(단말기) 목록 조회 | SELECT | MVANCOTB<br>VANMSTTB  |
| 15 | `/contractNumList` | 카드계약 모달 8종 동시 조회 | SELECT | MCARDMTB<br>MMCARDTB<br>MMEMBPTB<br>MMSCOMTB<br>MNAMEMTB<br>MVANCOTB<br>VANMSTTB  |
| 16 | `/getPosDanGbnList` | VAN사별 단말기 구분 조회 | SELECT | VANMSTTB  |
| 17 | `/saveVanPos` | VAN(POS) 등록 (4단계 중복체크 + addFg 분기) | INSERT | MMEMBSTB<br>MVANCOTB  |
| 18 | `/updateVanPos` | VAN(POS) 수정 (계약번호 중복 체크) | UPDATE | MVANCOTB  |
| 19 | `/deletePosVan` | VAN(POS) 삭제 | DELETE | MVANCOTB  |
| 20 | `/saveVanDan` | VAN(단말기) 등록 (중복체크 3단계) | INSERT | MMEMBSTB<br>MVANCOTB  |
| 21 | `/updateVanDan` | VAN(단말기) 수정 (계약번호 체크 후 UPDATE) | UPDATE | MVANCOTB  |
| 22 | `/deleteVanDan` | VAN(단말기) 삭제 | DELETE | MVANCOTB  |
| 23 | `/getCardContract` | Card 계약번호 조회 | SELECT | MMCARDTB<br>MNAMEMTB  |
| 24 | `/saveCardContract` | Card 계약번호 등록 (TriggerUtil 연동) | MERGE  MMCARDTB |

---

## 1. `/search` — 매장 목록 조회 (페이징)

**컨트롤러**: `offset`, `limit` → `startCount`, `endCount` 변환

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 1-1 | chainNo=`C001` | 매장 10건 존재 | `{"offset":0,"limit":10}` | `{"total":10,"rows":[...]}` |
| 1-2 | chainNo=`C001` | - | `{"offset":10,"limit":10}` | startCount=11, endCount=20 |
| 1-3 | chainNo=`C001` | - | `{"offset":0,"limit":10,"searchMsNm":"강남점"}` | 이름 필터 결과 |
| 1-4 | chainNo=`C001` | - | `{}` (offset 없음) | Integer.valueOf(null) → **NPE/NumberFormatException** |
| 1-5 | limit 없음 | `{"offset":0}` | 70번 `limit.toString()` → **NPE → 500** ★ |

---

## 2. `/msInsert` — 매장 등록

**컨트롤러 분기 3단계**:
```
1) 영수증 billAddr 조합: billAddr02 != "" → "addr01||addr02" / "" → "addr01"
2) headMsg01~05, tailMsg01~05: 빈값 아니면 앞에 "||" 붙여 연결
3) chainHqYn 체크:
   "Y" → checkChainHqYn > 0 → "headOfficeExist" 반환 (중단)
   "N" → checkChainHqYn == 0 → "noHeadOffice" 반환 (중단)
4) openDate, closeDate: "-" 제거 (20260101 형식)
5) insertMs() → "success" 반환
```

**서비스 insertMs() 5단계**:
```
getShopBrandCd() → insertMs() → insertWebEnv() → insertSendNo() → insertMsDefaultEnv() → insertMsDefaultPosEnv()
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 2-1 | ID=`7249525SHOP` | 체인 본부 없음 | `{"chainHqYn":"Y","chainNo":"C001","msNm":"강남본부","openDate":"2026-01-01","closeDate":"2099-12-31","billAddr01":"서울시 강남구","billAddr02":"","headMsg01":"환영합니다","headMsg02":"","headMsg03":"","headMsg04":"","headMsg05":"","tailMsg01":"감사합니다","tailMsg02":"","tailMsg03":"","tailMsg04":"","tailMsg05":"","prePurchWhmsNo":"NC0001"}` | `"success"`, msNo="NC"+채번, 5개 연쇄 INSERT |
| 2-2 | ID=`7249525SHOP` | **본부 이미 존재** | `{"chainHqYn":"Y",...}` | `"headOfficeExist"` (DB 변경 없음) |
| 2-3 | ID=`7249525SHOP` | 본부 없음 | `{"chainHqYn":"N",...}` | `"noHeadOffice"` (DB 변경 없음) |
| 2-4 | ID=`7249525SHOP` | 본부 존재 | `{"chainHqYn":"N","chainNo":"C001",...}` | `"success"`, 가맹점 등록 |
| 2-5 | ID=`7249525SHOP` | - | billAddr02 있음 | `billAddr = "addr01||addr02"` DB 저장 확인 |
| 2-6 | ID=`7249525SHOP` | - | headMsg02,03,04,05 모두 있음 | `headMsg = "msg01||msg02||msg03||msg04||msg05"` |
| 2-7 | ID=`7249525SHOP` | - | `{"openDate":"2026-01-01"}` | openDate=`"20260101"` ("-" 제거) |
| 2-8 | prePurchWhmsNo 미전송 | body에 prePurchWhmsNo 키 없음 | 112번 **NPE → 500** ★ |

---

## 3~4. `/msInfoSelect`, `/msInfoUpdate` — 매장 상세/수정

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 3-1 | - | NC0001 존재 | `{"msNo":"NC0001"}` | 매장 상세 Map |
| 3-2 | - | NC9999 미존재 | `{"msNo":"NC9999"}` | null 또는 빈 Map |
| 4-1 | ID=`7249525SHOP` | NC0001 존재 | `{"msNo":"NC0001","msNm":"강남본부(수정)","billAddr01":"서울시","billAddr02":"강남구","headMsg01":"안녕","headMsg02":"","headMsg03":"","headMsg04":"","headMsg05":"","tailMsg01":"","tailMsg02":"","tailMsg03":"","tailMsg04":"","tailMsg05":"","openDate":"2026-01-01","closeDate":"2099-12-31"}` | UPDATE 건수 (int) |

---

## 5~6. `/getOpenFg`, `/saveOpenFg` — 오픈구분

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 5-1 | - | NC0001 존재 | `{"msNo":"NC0001"}` | openFg Map |
| 6-1 | ID=`7249525SHOP` | NC0001 존재 | `{"msNo":"NC0001","openFg":"O"}` | 수정 건수 (int) |

---

## 7. `/getSystemList` — 환경설정 조회

**분기: KITCHEN_YN + KITCHEN_CNT**
```
systemList != null
AND KITCHEN_YN != "0"
AND KITCHEN_CNT != "0"
→ getKitchenList() 추가 조회 → systemList에 "kitchenList" 추가
그 외 → kitchenList=[] 반환
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 7-1 | - | KITCHEN_YN=1, KITCHEN_CNT=3 | `{"msNo":"NC0001"}` | systemList + kitchenList(3건) |
| 7-2 | - | KITCHEN_YN=0 | `{"msNo":"NC0001"}` | systemList + kitchenList=[] |
| 7-3 | - | KITCHEN_CNT=0 | `{"msNo":"NC0001"}` | kitchenList=[] |
| 7-4 | msNo 없거나 DB에 환경설정 없음 | `getSystemList()` → null 반환 | 319번 `systemList.put()` → **NPE → 500** ★ |

---

## 8. `/saveSystemInfo` — 환경설정 저장

**분기: getMsEnvCnt > 0 → updateMsEnv / = 0 → insertMsEnv + kitchenNoArr 배열 저장**

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 8-1 | ID=`7249525SHOP` | 환경설정 **없음** | `{"msNo":"NC0001","kitchenNoArr":["01","02"],"kitchenNmArr":["주방1","주방2"],...}` | insertMsEnv + saveKitchenPrint 2건 |
| 8-2 | ID=`7249525SHOP` | 환경설정 **있음** | 동일 | updateMsEnv + saveKitchenPrint 2건 |
| 8-3 | ID=`7249525SHOP` | - | `{"msNo":"NC0001","kitchenNoArr":[],"kitchenNmArr":[]}` | insertMsEnv/updateMsEnv + kitchenPrint 저장 없음 |
| 8-4 | kitchenNoArr 미전송 | body에 kitchenNoArr 키 없음 | 355번 **NPE → 500** ★ |
| 8-5 | kitchenNoArr/kitchenNmArr 크기 불일치 | `kitchenNoArr=["01"]`, `kitchenNmArr=[]` | 360번 `kitchenNmList.get(i)` → **IndexOutOfBoundsException → 500** ★ |

---

## 10. `/insertMsPosEnv` — 포스 장비 등록

**분기: posMobileType**
```
posMobileType = "0" (일반 POS)
  chkMaxPosNo == "79" → "maxPosNo" 반환
  그 외 → getNewPosNo() → insertMsPosEnv()

posMobileType != "0" (모바일 POS)
  chkMaxMobilePosNo == "99" → "maxMobilePosNo" 반환
  그 외 → getNewMobilePosNo() → insertMsPosEnv()
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 10-1 | ID=`7249525SHOP` | posNo 최대 10개 | `{"msNo":"NC0001","posMobileType":"0"}` | `"success"` |
| 10-2 | ID=`7249525SHOP` | **posNo 79개** | `{"msNo":"NC0001","posMobileType":"0"}` | `"maxPosNo"` (DB 변경 없음) |
| 10-3 | ID=`7249525SHOP` | **mobile posNo 99개** | `{"msNo":"NC0001","posMobileType":"1"}` | `"maxMobilePosNo"` |

---

## 11. `/updateMsPosEnv` — 포스 장비 수정 (@RequestParam 배열)

**특이사항**: `@RequestBody` 아님 — `@RequestParam` 다중 배열 (form-data 방식)

| No | 세션 조건 | DB 선행상태 | Request (form-param) | 예상값 |
|----|----------|------------|----------------------|-------|
| 11-1 | ID=`7249525SHOP` | POS 2대 존재 | `posSettingFormMsNo=NC0001&posSettingFormPosNo[]=01&posSettingFormPosNo[]=02&posSettingCustYn[]=Y&posSettingCustYn[]=Y&...` | `"success"` |
| 11-2 | ID=`7249525SHOP` | - | `macAddIp[]` 미포함 | macAddIp=`" "` (공백) 처리 |
| 11-3 | ID=`7249525SHOP` | - | `dPosCd[]` 빈값 | dPosCd=`" "` (공백) 처리 |

---

## 17. `/saveVanPos` — VAN(POS) 등록

**4단계 중복 체크 분기**:
```
checkBizNo > 0 → "BizDup"
checkBizNo = 0
  checkVanCnt > 0 → "VanDup"
  checkVanCnt = 0
    vanFg = "1" (현금) → checkVanCardCnt = 0 → "vanCardNull"
    addFg = "Y" → insertVanPosCard + insertVanPosCash (2건)
    addFg ≠ "Y" → insertVanPosCard (1건)
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 17-1 | ID=`7249525SHOP` | BizNo 중복 | `{"msNo":"NC0001","vanFg":"0","addFg":"N",...}` | `"BizDup"` |
| 17-2 | ID=`7249525SHOP` | VAN사 중복 | biz 정상 | `"VanDup"` |
| 17-3 | ID=`7249525SHOP` | vanFg=1, 카드등록 없음 | vanFg=`"1"` | `"vanCardNull"` |
| 17-4 | ID=`7249525SHOP` | 정상 | `{"vanFg":"0","addFg":"Y",...}` | insertVanPosCard + insertVanPosCash 2건 |
| 17-5 | ID=`7249525SHOP` | 정상 | `{"vanFg":"0","addFg":"N",...}` | insertVanPosCard 1건만 |

---

## 18. `/updateVanPos` — VAN(POS) 수정

```
checkCon == 0 → dup="" (중복 없음)
checkCon > 0  → dup="ConDup"
updatePosVan() 항상 실행 (ConDup여도)
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 18-1 | ID=`7249525SHOP` | 계약번호 없음 | `{"msNo":"NC0001","vanCd":"V01",...}` | `""` + updatePosVan 실행 |
| 18-2 | ID=`7249525SHOP` | **계약번호 중복** | 동일 | `"ConDup"` + **updatePosVan 여전히 실행** ★ |

---

## 20. `/saveVanDan` — VAN(단말기) 등록

```
checkBizNo > 0 → "BizDup"
checkDanVan > 0 → "VanDup"
checkCatId != 0 → "CatDup"
그 외 → insertVanDan
```
**saveVanPos와 차이**: CatDup을 주석처리 없이 실제 반환함

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 20-1 | ID=`7249525SHOP` | 정상 | `{"msNo":"NC0001","vanCd":"V01","catId":"CAT001",...}` | `""` + insertVanDan |
| 20-2 | ID=`7249525SHOP` | CatId 중복 | - | `"CatDup"` (saveVanPos와 다름) |

---

## 21. `/updateVanDan` — VAN(단말기) 수정

```
checkVanCon == 0 → updateVanDan() 실행
checkVanCon > 0  → "ConDup" 반환, updateVanDan 미실행
```
**updateVanPos와 차이**: ConDup이면 UPDATE 자체 안 함

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 21-1 | ID=`7249525SHOP` | 계약번호 없음 | `{"msNo":"NC0001","danCd":"D01",...}` | `""` + updateVanDan 실행 |
| 21-2 | ID=`7249525SHOP` | **계약번호 중복** | - | `"ConDup"` + **updateVanDan 미실행** ★ |

---

## 24. `/saveCardContract` — Card 계약번호 등록 (TriggerUtil)

**서비스 로직 (Tr_MMCARD_T01_Service 연동)**:
```
1) selectCardContract() → 기존 계약번호 목록
2) 각 건에 TriggerUtil.setTriggerParam("D", map) → getOldValues → processTrigger (DELETE 트리거)
3) deleteCardContract() → 기존 전체 삭제
4) cardCoArr / contractNoArr 병렬 배열 순회
   → mergeMmcard(map) → TriggerUtil.setTriggerParam("A", map) → getOldValues
   → old가 비어있지 않으면 procFg="U" (UPDATE 처리)
   → processTrigger (ADD/UPDATE 트리거)
```

| No | 세션 조건 | DB 선행상태 | RequestBody | 예상값 |
|----|----------|------------|-------------|-------|
| 24-1 | ID=`7249525SHOP` | 기존 계약번호 2건 | `{"msNo":"NC0001","cardCoArr":["BC","KB"],"contractNoArr":["123","456"]}` | D트리거 2건 → deleteCardContract → A트리거 2건 (mergeMmcard) |
| 24-2 | ID=`7249525SHOP` | **기존 없음** | `{"msNo":"NC0001","cardCoArr":["BC"],"contractNoArr":["789"]}` | deleteCardContract(0건) → mergeMmcard 1건 |
| 24-3 | ID=`7249525SHOP` | 기존 1건 | `{"msNo":"NC0001","cardCoArr":[],"contractNoArr":[]}` | D트리거 1건 → deleteCardContract → 신규 INSERT 없음 |
| 24-4 | ID=`7249525SHOP` | 기존=신규 동일 | `{"cardCoArr":["BC"],"contractNoArr":["123"]}` | old가 있으므로 procFg="U" → processTrigger UPDATE |
| 24-5 | - | - | `{}` (cardCoArr 없음) | **NPE** (null cast) |
| 24-6 | - | - | @Transactional: processTrigger 오류 | 전체 롤백 |
| 24-7 | saveCardContract 성공 응답 | 정상 처리 | HTTP 200 + **빈 바디** ★ |

---

## 서비스 핵심 분기 요약

```
msInsert
├── chainHqYn="Y", headOfficecount>0 → "headOfficeExist"
├── chainHqYn="N", headOfficecount=0 → "noHeadOffice"
└── 통과 → insertMs (5단계 연쇄)

insertMsPosEnv
├── posMobileType="0" → chkMaxPosNo="79" → "maxPosNo"
└── 그 외 → chkMaxMobilePosNo="99" → "maxMobilePosNo"

saveVanPos (4단계)
BizDup → VanDup → vanCardNull(현금) → addFg=Y(카드+현금) / addFg≠Y(카드만)

updateVanPos: ConDup이어도 updatePosVan 실행
updateVanDan: ConDup이면 updateVanDan 미실행 ★ 차이점

saveCardContract
└── 기존건 D트리거 → deleteCardContract → 신규건 mergeMmcard + A트리거
    → old 존재 시 procFg="U" (UPDATE 경로)
```

---

## PowerShell 테스트 명령 (주요 케이스)

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/master/hq_master_00004"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1. 매장 목록 조회
Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10}'

# 2-1. 매장 등록 (신규 본부)
Invoke-RestMethod -Uri "$base/msInsert" -Method POST -Headers $h -WebSession $session `
  -Body '{"chainHqYn":"Y","chainNo":"C001","msNm":"강남본부","openDate":"2026-01-01","closeDate":"2099-12-31","billAddr01":"서울시 강남구","billAddr02":"","headMsg01":"환영합니다","headMsg02":"","headMsg03":"","headMsg04":"","headMsg05":"","tailMsg01":"감사합니다","tailMsg02":"","tailMsg03":"","tailMsg04":"","tailMsg05":"","prePurchWhmsNo":"NC0001"}'
# 예상: "success"

# 2-2. 본부 중복 체크
Invoke-RestMethod -Uri "$base/msInsert" -Method POST -Headers $h -WebSession $session `
  -Body '{"chainHqYn":"Y","chainNo":"C001",...}'
# 예상: "headOfficeExist"

# 17-4. VAN(POS) 등록 (addFg=Y)
Invoke-RestMethod -Uri "$base/saveVanPos" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"NC0001","vanCd":"V01","vanFg":"0","addFg":"Y","catId":"CAT001"}'
# 예상: "" (insertVanPosCard + insertVanPosCash 2건)

# 24-1. 카드 계약번호 등록 (TriggerUtil)
Invoke-RestMethod -Uri "$base/saveCardContract" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"NC0001","cardCoArr":["BC","KB"],"contractNoArr":["123","456"]}'
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `MMEMBSTB` | 매장 목록 (NC0001 본부) |
| `MMCHATB` | chainNo=C001 |
| `MMENVSETTB` | 매장 환경설정 |
| `MMPOSENVTB` | 포스 환경설정 |
| `MMVANSETTB` | VAN(POS) 설정 |
| `MMVANDANTB` | VAN(단말기) 설정 |
| `MMCARDTB` | 카드 계약번호 |
| Tr_MMCARD_T01 | 트리거 서비스 정상 기동 |

---

## 주요 검증 포인트

```
□ msInsert — billAddr, headMsg, tailMsg "||" 조합 문자열 DB 저장 확인
□ msInsert — openDate "-" 제거 (20260101) 저장 확인
□ saveVanPos — updateVanPos와 달리 ConDup이어도 UPDATE 실행 여부 확인 (★ 비일관성)
□ updateVanDan — ConDup이면 UPDATE 미실행 (updateVanPos와 반대)
□ saveCardContract — TriggerUtil D/A 순서, procFg="U" 분기
□ getSystemList — KITCHEN_YN/CNT "0" 문자열 비교 (숫자 0 아님) 주의
□ insertMsPosEnv — maxPosNo "79" 문자열 비교 주의
□ @Transactional — saveCardContract 트리거 실패 시 전체 롤백
```

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
