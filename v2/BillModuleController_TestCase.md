# BillModuleController — 영수증 공통 모듈 단위 테스트케이스

## 이 컨트롤러의 성격

> **별도 화면이 없습니다.** `@Controller` (RestController 아님) + `ModelAndView` 반환  
> → **JSP 프래그먼트(fragment)** 를 렌더링하여 HTML을 반환하는 **공통 컴포넌트 모듈**

### 어디서 호출되나?

여러 화면의 **영수증 팝업/테이블 영역**에서 AJAX로 호출됩니다:

```
매출 조회 화면들 (Hq_Sales_*, St_Sales_*) 에서
  ↓ 영수증 클릭 이벤트
  ↓ AJAX POST → /backoffice/data/common/getBillInfo
  ↓ JSP fragment (comBillT01) HTML 반환
  ↓ 화면 내 팝업/테이블에 삽입
```

| 호출 화면 | 호출 엔드포인트 |
|---------|--------------|
| 매출조회 영수증 클릭 | `/getBillInfo` |
| 외상입금 영수증 클릭 | `/getCreditBillInfo` |
| 세트/부가메뉴 구성 클릭 | `/goodsDetailList` |

### 반환 형태
- `@RestController`가 아닌 `@Controller` → JSON이 아닌 **HTML (JSP 렌더링)**
- 반환 ViewName:
  - `/getBillInfo` → `comBillT01` (일반 영수증 테이블)
  - `/getCreditBillInfo` → `comBillT02` (외상입금 영수증 테이블)
  - `/goodsDetailList` → `Com_BillInfoModalM02` (세트/부가메뉴 모달)

---

## 엔드포인트 목록 (3개)

| # | URL | 기능 | 반환 |
|---|-----|------|------|
| 1 | `/getBillInfo` | 일반 영수증 정보 조회 | ModelAndView → comBillT01 JSP |
| 2 | `/getCreditBillInfo` | 외상입금 영수증 조회 | ModelAndView → comBillT02 JSP |
| 3 | `/goodsDetailList` | 세트/부가메뉴 구성 매출 조회 | ModelAndView → BillInfoModalM02 JSP |

---

## 1. `/getBillInfo` — 일반 영수증 정보

**핵심 분기 ①: DETAIL_CNT / SLIP_CNT**

```
getDetSlpCnt()
├── DETAIL_CNT="0" AND SLIP_CNT="1" → 전표전용 (슬립)
│   └── goodstbName 세팅만, 이후 쿼리 미실행
└── 그 외 → 일반 영수증 처리 (12개 서비스 순차 호출)
```

**핵심 분기 ②: goodstbName (테이블 선택)**

```
userMsNo == msNo AND chainHqYn == "Y"
├── true  → goodstbName = "TGOODSTB" (임시상품 테이블, 본부 체인 매장)
└── false → goodstbName = "MGOODSTB" (일반 상품 테이블)
```

**핵심 분기 ③: tempCardAmt (복합결제)**

```
getCardInfo() → 각 카드 APPR_AMT 합산 → tempCardAmt
tempCardAmt > 0 → getMultiCardImInfo() 추가 호출
tempCardAmt = 0 → multiCardImInfo = []
```

**핵심 분기 ④: setOrSubGroupYn**

```
setOrSubGroupYn != "" → getSetOrSubGroupCnt() 호출, mav에 추가
setOrSubGroupYn == "" → setOrSubGroupCnt 미조회
```

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 1-1 | 정상 일반 영수증 | `saleDate=20260522&msNo=NC0007&posNo=01&billNo=0001` | comBillT01 HTML, 12개 model 포함 |
| 1-2 | **SLIP만 있는 영수증** | DETAIL_CNT=0, SLIP_CNT=1 인 billNo | goodstbName만 세팅, billInfo02 등 쿼리 미실행 |
| 1-3 | **DETAIL_CNT>0 정상** | DETAIL_CNT=3, SLIP_CNT=1 | 전체 12개 서비스 호출 |
| 1-4 | **본부매장 (goodstbName=TGOODSTB)** | userMsNo=msNo, chainHqYn=Y | goodstbName="TGOODSTB" |
| 1-5 | **일반매장 (goodstbName=MGOODSTB)** | userMsNo≠msNo 또는 chainHqYn=N | goodstbName="MGOODSTB" |
| 1-6 | **카드합산 > 0 (복합결제)** | APPR_AMT 합계 > 0 | multiCardImInfo 추가 조회 |
| 1-7 | **카드합산 = 0** | 카드 결제 없는 영수증 | multiCardImInfo=[] |
| 1-8 | **setOrSubGroupYn 있음** | `setOrSubGroupYn=Y` | setOrSubGroupCnt mav에 추가 |
| 1-9 | setOrSubGroupYn 없음 | `setOrSubGroupYn=` | setOrSubGroupCnt 미조회 |
| 1-10 | 날짜 포맷 변환 | `saleDate=2026-05-22` | commandMap에 `"20260522"` 저장 |
| 1-11 | 날짜 슬래시 포맷 | `saleDate=2026/05/22` | `"20260522"` 저장 |
| 1-12 | 존재하지 않는 billNo | `billNo=9999` | DETAIL_CNT=0, SLIP_CNT=0 → 빈 영수증 |
| 1-13 | msNo 누락 | `msNo` 파라미터 없음 | 400 (required=true) |
| 1-14 | 미인증 접근 | 세션 없음 | 302 redirect |
| 1-15 | **DETAIL_CNT=0 슬립 영수증** | DB에서 DETAIL_CNT=0, SLIP_CNT=1 | 슬립전용 분기 진입 확인 (goodstbName만 세팅) |
| 1-16 | DETAIL_CNT Integer 반환 시 | Mapper 반환타입 Integer인 경우 | `equals("0")` false → 일반 분기 진입 ★ 버그 |
| 1-17 | enterInfo 확인 | 정상 영수증 조회 | `enterInfo` = `{}` (빈 Map, 서비스 미호출) ★ |
| 1-18 | custTransInfo 확인 | 정상 영수증 조회 | `custTransInfo` = `[]` (빈 List, 서비스 미호출) ★ |

---

## 2. `/getCreditBillInfo` — 외상입금 영수증

**핵심 분기: optFg 값 (6가지)**

```
optFg
├── "2" → getCreditBillCardInfo()    (신용카드 정상)
├── "1" → getCreditBillCardImInfo()  (신용카드 임의등록)
├── "3" → getCreditBillCashInfo()    (현금영수증)
├── "4" → getCreditBillPpCardInfo()  (선불카드)
├── "5" → getCreditBillPpCardImInfo()(선불카드 임의등록)
├── "6" → getCreditBillGiftInfo()    (상품권)
└── 그 외("") → 추가 조회 없음 (getCreditBillGaryInfo만 실행)
```

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 2-1 | **optFg=2 (신용카드)** | `optFg=2` + 유효 영수증 | creditBillCardInfo mav에 추가 |
| 2-2 | **optFg=1 (신용카드 임의)** | `optFg=1` | creditBillCardImInfo mav에 추가 |
| 2-3 | **optFg=3 (현금영수증)** | `optFg=3` | creditBillCashInfo mav에 추가 |
| 2-4 | **optFg=4 (선불카드)** | `optFg=4` | creditBillPpCardInfo mav에 추가 |
| 2-5 | **optFg=5 (선불카드임의)** | `optFg=5` | creditBillPpCardImInfo mav에 추가 |
| 2-6 | **optFg=6 (상품권)** | `optFg=6` | creditBillGiftInfo mav에 추가 |
| 2-7 | optFg 빈값 | `optFg=` (defaultValue="") | garyInfo만 조회, 나머지 빈 리스트 |
| 2-8 | paidDate 포맷 | `paidDate=2026-05-22` | `"20260522"` 저장 |
| 2-9 | paidDate 빈값 | `paidDate=` | `""` (replaceAll 처리 후 빈문자) |
| 2-10 | 존재하지 않는 영수증 | `billNo=9999` | 빈 Map/List |
| 2-11 | saleDate 누락 | 파라미터 없음 | 400 (required=true) |
| 2-12 | **optFg 값 콘솔 출력** | 모든 getCreditBillInfo 호출 | 서버 콘솔에 `optFg:2` 출력 — 운영 제거 필요 ★ |
| 2-13 | billInfo01 확인 | 유효한 외상 영수증 조회 | `billInfo01` = `{}` (항상 빈 Map) ★ |

---

## 3. `/goodsDetailList` — 세트/부가메뉴 구성 매출

**핵심 분기: goodsInfoList 반복 → SET_CD / SUB_GROUP_CD 존재 여부**

```
getGoodsInfo() → goodsInfoList 반복
  각 상품(i)에 대해:
  ├── SET_CD != null && != "" → getSetGoodsDetailList() → setGoodsList에 추가
  └── SUB_GROUP_CD != null && != "" → 3개 서비스 호출:
      ├── selectGoodsSalesList()      → subGroupHdList에 추가
      ├── getSubGroupGoodsDetailList()→ subGroupList에 추가
      └── getSubGroupInfo()           → subGroupInfoList에 추가
```

| No | 케이스 | 테스트값 | 예상값 |
|----|--------|---------|-------|
| 3-1 | **세트 상품만 있는 영수증** | SET_CD 있음, SUB_GROUP_CD 없음 | setGoodsList 데이터, subGroupHdList=[] |
| 3-2 | **부가메뉴만 있는 영수증** | SUB_GROUP_CD 있음, SET_CD 없음 | setGoodsList=[], subGroupHdList/List 데이터 |
| 3-3 | **세트+부가메뉴 혼합** | 둘 다 있는 영수증 | 양쪽 모두 데이터 |
| 3-4 | **일반 상품만** | SET_CD=null, SUB_GROUP_CD=null | 4개 리스트 모두 빈 리스트 |
| 3-5 | SET_CD="" 처리 | `SET_CD=""` (빈문자) | getSetGoodsDetailList 미호출 |
| 3-6 | 다중 세트 상품 | goodsInfoList에 3개 세트 상품 | setGoodsList에 3개 세트 구성 addAll |
| 3-7 | 다중 부가메뉴 | goodsInfoList에 2개 부가메뉴 | subGroupInfoList 2건, 반복 누적 |
| 3-8 | 존재하지 않는 영수증 | `billNo=9999` | goodsInfoList=[] → 4개 리스트 모두 빈 리스트 |
| 3-9 | msNo 누락 | 파라미터 없음 | 400 (required=true) |
| 3-10 | **GOODS_CD=null 상품** | goodsInfoList에 GOODS_CD=null 행 존재 | NPE → 500 ★ (현재 버그) |
| 3-11 | SET_CD=null 처리 | SET_CD null 상품 | setCd="" → getSetGoodsDetailList 미호출 (정상) |

---

## 테스트 방법

### 방법 1: 화면 통해 간접 테스트 (권장)
```
1. http://localhost:18080/backoffice 로그인
2. [HQ] 또는 [ST] 매출조회 화면 진입
   예: /backoffice/view/main/hq/sales/hq_sales_00001
3. 날짜 조회 → 영수증 행 클릭
4. 팝업/테이블에 comBillT01 HTML 정상 렌더링 확인
```

### 방법 2: PowerShell 직접 호출
```powershell
# 세션 쿠키 먼저 획득 (로그인)
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# 1. 로그인
$login = Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body @{username="admin";password="admin123"} `
  -SessionVariable session

# 2. 일반 영수증 조회
$result = Invoke-WebRequest -Uri "http://localhost:18080/backoffice/data/common/getBillInfo" `
  -Method POST `
  -Body "saleDate=20260522&msNo=NC0007&posNo=01&billNo=0001" `
  -ContentType "application/x-www-form-urlencoded" `
  -WebSession $session
# HTML 반환 여부 확인
$result.Content.Length   # 0이면 오류, >0이면 HTML 렌더링 성공
$result.StatusCode       # 200 이어야 함

# 3. 외상입금 영수증 (optFg=2 신용카드)
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/data/common/getCreditBillInfo" `
  -Method POST `
  -Body "saleDate=20260522&msNo=NC0007&posNo=01&billNo=0001&optFg=2" `
  -ContentType "application/x-www-form-urlencoded" `
  -WebSession $session

# 4. 세트/부가메뉴 구성 조회
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/data/common/goodsDetailList" `
  -Method POST `
  -Body "saleDate=20260522&msNo=NC0007&posNo=01&billNo=0001" `
  -ContentType "application/x-www-form-urlencoded" `
  -WebSession $session
```

### 방법 3: 응답 HTML 검증 포인트
```
# /getBillInfo 응답 HTML에서 확인할 요소
□ <table> 태그 존재 (comBillT01 렌더링)
□ 영수증 번호, 날짜, 매장명 표시
□ 카드정보 영역 (tempCardAmt > 0일 때만)
□ 세트/부가메뉴 링크 (setOrSubGroupCnt > 0일 때만)
□ 반품사유 영역 (displayVoidContents 있을 때)
```

---

## 서비스 핵심 분기 요약

```
getBillInfo
├── DETAIL_CNT=0 AND SLIP_CNT=1 → 슬립전용, 12개 쿼리 미실행
├── goodstbName: userMsNo=msNo AND chainHqYn=Y → TGOODSTB, 그 외 → MGOODSTB
└── tempCardAmt > 0 → multiCardImInfo 추가 호출

getCreditBillInfo (optFg)
├── "1" → 신용카드 임의등록
├── "2" → 신용카드 정상
├── "3" → 현금영수증
├── "4" → 선불카드
├── "5" → 선불카드 임의등록
├── "6" → 상품권
└── ""  → garyInfo만 (추가 조회 없음)

goodsDetailList (SET_CD vs SUB_GROUP_CD)
├── SET_CD 있음 → setGoodsDetailList 1개 서비스
└── SUB_GROUP_CD 있음 → 3개 서비스 (HD, DT, Info)
    (둘 다 있으면 각각 독립 실행)
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `STRNCMTB` | 테스트용 영수증 (일반/슬립/외상) |
| `STRNCDTB` | 영수증 상세 (DETAIL_CNT 확인) |
| `STRNCARDTB` | 카드 결제 데이터 (APPR_AMT) |
| `STRNCASTB` | 현금영수증 데이터 |
| `STRNGIFTTB` | 상품권 데이터 |
| `MGOODSTB` | 일반 상품 (goodstbName=MGOODSTB) |
| `TGOODSTB` | 임시 상품 (본부 체인 매장) |
| `MMEMBSTB` | 매장 정보 (chainHqYn 확인) |

---



## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```mermaid
flowchart TD
  subgraph ServiceLogic[Service Logic]
    API[API Endpoint]
  end
  subgraph DB_Tables[Database Tables]
    MGOODSTB[MGOODSTB]
    TGOODSTB[TGOODSTB]
    STRNCDTB[STRNCDTB]
    MMEMBSTB[MMEMBSTB]
  end
  subgraph Triggers[Legacy Triggers (To be converted)]
    MGOODS_T01[MGOODS_T01 : INSERT OR UPDATE OR DELETE]
    MGOODS_T02[MGOODS_T02 : DELETE]
    MGOODS_T03[MGOODS_T03 : INSERT OR UPDATE OR DELETE]
    MMEMBS_T01[MMEMBS_T01 : INSERT OR UPDATE OR DELETE]
    STRNCD_T01[STRNCD_T01 : INSERT]
    TGOODS_T01[TGOODS_T01 : INSERT OR UPDATE OR DELETE]
  end
  API -->|CUD Operations| DB_Tables
  MGOODSTB -.->|Triggered by INSERT OR UPDATE OR DELETE| MGOODS_T01
  MGOODSTB -.->|Triggered by DELETE| MGOODS_T02
  MGOODSTB -.->|Triggered by INSERT OR UPDATE OR DELETE| MGOODS_T03
  MMEMBSTB -.->|Triggered by INSERT OR UPDATE OR DELETE| MMEMBS_T01
  STRNCDTB -.->|Triggered by INSERT| STRNCD_T01
  TGOODSTB -.->|Triggered by INSERT OR UPDATE OR DELETE| TGOODS_T01
```
