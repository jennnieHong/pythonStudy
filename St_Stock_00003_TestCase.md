# St_Stock_00003 — 매장 폐기등록 단위 테스트케이스

> **화면**: [ST] 재고 > 조정/폐기/실사 > 폐기등록  
> **URL Prefix**: `POST /backoffice/data/st/stock/st_stock_00003`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: 
> * `/selectDisuseList`, `/goodsSelect`, `/deleteDisuse`, `/getCloseYn`, `/confirmDisuse`: `@RequestBody` JSON 통신
> * `/saveDisuse`, `/updateDisuse`: Form Data (`application/x-www-form-urlencoded` 또는 쿼리 파라미터) 통신
> **DB 트리거 영향도**: 본 화면은 폐기 전표의 수정 및 확정을 수행합니다.
> * `/updateDisuse` 및 `/confirmDisuse` 시 DB 트리거 `IMDUSE_T01` (Java 서비스: `Tr_IMDUSE_T01_Service`)이 기동되어 `IMTRLGTB` (수불로그) 테이블에 데이터가 생성 및 변경되고, 이는 최종적으로 배치 스케줄러 (`DmIMTR01Job`)에 의해 일수불(`IMDDIOTB`) 및 월수불(`IMMMIOTB`) 재고 수량의 연쇄 차감으로 처리됩니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | selectDisuseList, goodsSelect, saveDisuse, updateDisuse |
| `msNo` | `NC0001` (카페매장) | selectDisuseList, goodsSelect, saveDisuse, updateDisuse, deleteDisuse, getCloseYn, confirmDisuse |
| `ID` | `fnbcafe` (카페 매장 관리자) | 공통 세션 및 권한 체크 |
| `chainMsNo` | `NC0001` | saveDisuse, updateDisuse |

---

## 엔드포인트 목록 (7개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/selectDisuseList` | 폐기등록 전표조회 | `@RequestBody` | `Map` (total, rows) | SELECT | IMDUSETB, TGOODSTB, MMEMBSTB, MNAMEMTB, IMCRIOTB |
| 2 | `/goodsSelect` | 폐기등록 모달 상품조회 | `@RequestBody` | `List` (GoodsListDto) | SELECT | TGOODSTB, MMEMBSTB, MNAMEMTB, IMCRIOTB |
| 3 | `/saveDisuse` | 폐기전표 등록 (추가) | Form Parameter | `int` | INSERT | IMDUSETB |
| 4 | `/updateDisuse` | 폐기전표 수정 (저장) | Form Parameter | `String` | UPDATE/MERGE | IMDUSETB |
| 5 | `/deleteDisuse` | 폐기전표 삭제 | `@RequestBody` | `int` | DELETE | IMDUSETB |
| 6 | `/getCloseYn` | 마감여부 조회 | `@RequestBody` | `String` | SELECT | IMREMSTB |
| 7 | `/confirmDisuse` | 폐기확정 | `@RequestBody` | `String` | UPDATE | IMDUSETB |

---

## 1. `/selectDisuseList` — 폐기등록 전표조회

* 대기(`PROC_FG = '0'`) 및 폐기(`DIV_FG = '0'`) 상태인 폐기등록 전표만 조회합니다.
* **[중요]** 확정 처리(`PROC_FG = '1'`)가 완료되면 본 화면의 목록에서 사라지며, **`st_stock_00004` (폐기현황)** 화면에서 조회할 수 있게 됩니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 1-1 | msNo=`NC0001` | 미확정 폐기 건 존재 | `{"searchFromDate":"20260601","searchToDate":"20260610","offset":0,"limit":100}` | 미확정 폐기 전표 요약 및 상세 정보 반환 |
| 1-2 | msNo=`NC0001` | 확정 상태 전표만 존재 | `{"searchFromDate":"20260601","searchToDate":"20260610","offset":0,"limit":100}` | `total: 0`, 빈 `rows` 배열 반환 (대기 상태만 조회되므로 확정건은 미출력) |
| 1-3 | msNo=`NC0001` | 해당 일자 폐기 없음 | `{"searchFromDate":"20200601","searchToDate":"20200610","offset":0,"limit":100}` | `total: 0`, 빈 `rows` 배열 반환 |

---

## 2. `/goodsSelect` — 폐기등록 모달 상품조회

* 폐기 등록을 위한 모달 팝업 내에서 폐기 가능한 상품을 조회합니다. 세트상품(`SET_FG = '3'`)은 제외됩니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 2-1 | msNo=`NC0001` | 상품 정보 존재 | `{"order":"asc","lclassCd":"","mclassCd":"","sclassCd":"","goodsCd":"","goodsNm":"","goodsCdArr":[]}` | 폐기 가능한 상품 목록 반환 |
| 2-2 | msNo=`NC0001` | 상품코드 필터링 | `{"order":"asc","lclassCd":"","mclassCd":"","sclassCd":"","goodsCd":"T0000291","goodsNm":"","goodsCdArr":[]}` | 특정 상품코드(`T0000291`)만 필터링되어 반환 |

---

## 3. `/saveDisuse` — 폐기전표 등록 (추가)

* 모달창에서 상품을 선택하고 추가를 누를 때 호출됩니다. `IMDUSETB` 테이블에 `PROC_FG = '0'` (대기) 상태의 초기 레코드를 생성합니다.

| No | 세션 조건 | parameters (Form Data) | 예상값 / 검증 포인트 |
|----|----------|------------------------|--------------------|
| 3-1 | msNo=`NC0001`, userId=`fnbcafe` | `goodsCdArr[]=T0000291&dUseDate=20260605` | `IMDUSETB`에 초기 폐기 행 등록 완료 및 `1` (성공 카운트) 반환 |

---

## 4. `/updateDisuse` — 폐기전표 수정 (저장)

* 수량, 사유, 비고 등을 입력하고 저장할 때 호출됩니다.
* 이 단계에서 트리거 서비스 `Tr_IMDUSE_T01_Service`가 호출되지만, 아직 확정이 아니므로 (`PROC_FG = '0'`) 연쇄 재고 차감은 일어나지 않습니다.

| No | 세션 조건 | parameters (Form Data) | 예상값 / 검증 포인트 |
|----|----------|------------------------|--------------------|
| 4-1 | msNo=`NC0001`, userId=`fnbcafe` | `goodsCdArr[]=T0000291&dUseTotArr[]=2&remarkArr[]=테스트비고&reasonCdArr[]=M01&idxArr[]=00000000000001&dUseCostArr[]=9600` | 수량(`2`), 사유(`M01`), 비고가 업데이트되고 `"success"` 반환 |

---

## 5. `/deleteDisuse` — 폐기전표 삭제

* 대기 상태인 폐기 항목을 선택하여 삭제 처리합니다.

| No | 세션 조건 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|--------------------|--------------------|
| 5-1 | msNo=`NC0001` | `{"list":[{"idx":"00000000000001","goodsCd":"T0000291"}]}` | 전표 삭제 성공 및 `1` (성공 카운트) 반환 |

---

## 6. `/getCloseYn` — 마감여부 조회

* 해당 월의 재고 마감 여부를 확인합니다. 마감되었으면 추가 등록/수정/확정이 불가능합니다.

| No | 세션 조건 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|--------------------|--------------------|
| 6-1 | msNo=`NC0001` | `{"disuseDate":"20260605"}` | 마감되지 않은 경우 빈 값 `""`, 마감된 경우 `"closed"` 반환 |

---

## 7. `/confirmDisuse` — 폐기확정

* 대기 중인 폐기 전표를 최종 확정(`PROC_FG = '1'`) 처리합니다.
* 이 시점에 `Tr_IMDUSE_T01_Service.processTrigger()`가 구동되어 `IMTRLGTB` 수불로그 생성 및 재고 연쇄 차감(Depth 3)이 최종 실행됩니다.
* **[중요]** 로컬 개발 환경에서는 실시간 트리거 대신 배치 스케줄러 `DmIMTR01Job`이 비동기로 재고 차감을 수행하므로, 확정 직후 `IMTRLGTB`에 적재된 로그의 `PROC_YN` 상태가 `'N'`(미처리)임을 대조 검증합니다.

| No | 세션 조건 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|--------------------|--------------------|
| 7-1 | msNo=`NC0001`, userId=`fnbcafe` | `{"list":[{"idx":"00000000000001","goodsCd":"T0000291"}]}` | `"now"` (또는 이미 처리된 경우 `"later"`) 반환, DB에 수불로그 등록 및 `PROC_YN = 'N'` 기록 확인 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/stock/st_stock_00003"
$h_json = @{"Content-Type"="application/json"}
$h_form = @{"Content-Type"="application/x-www-form-urlencoded"}

# 1. 폐기등록 모달 상품조회
Invoke-RestMethod -Uri "$base/goodsSelect" -Method POST -Headers $h_json -WebSession $session `
  -Body '{"order":"asc","lclassCd":"","mclassCd":"","sclassCd":"","goodsCd":"","goodsNm":"","goodsCdArr":[]}'

# 2. 폐기전표 임시 등록 (T0000291 상품 추가)
Invoke-RestMethod -Uri "$base/saveDisuse" -Method POST -Headers $h_form -WebSession $session `
  -Body "goodsCdArr[]=T0000291&dUseDate=20260605"

# 3. 등록된 전표 목록 조회 (생성된 idx 확인용)
$res = Invoke-RestMethod -Uri "$base/selectDisuseList" -Method POST -Headers $h_json -WebSession $session `
  -Body '{"searchFromDate":"20260601","searchToDate":"20260610","offset":0,"limit":100}'
$idx = $res.rows[0].idx

# 4. 폐기전표 수정 (수량 2, 사유 M01 입력)
Invoke-RestMethod -Uri "$base/updateDisuse" -Method POST -Headers $h_form -WebSession $session `
  -Body "goodsCdArr[]=T0000291&dUseTotArr[]=2&remarkArr[]=TestRemark&reasonCdArr[]=M01&idxArr[]=$idx&dUseCostArr[]=9600"

# 5. 폐기 확정
Invoke-RestMethod -Uri "$base/confirmDisuse" -Method POST -Headers $h_json -WebSession $session `
  -Body "{`"list`":[{`"idx`":`"$idx`",`"goodsCd`":`"T0000291`"}]}"
```

---

## 주요 검증 포인트

* **조회 소멸 및 이동**: `/confirmDisuse`로 확정 처리된 전표가 더 이상 `/selectDisuseList`에서 조회되지 않고 `st_stock_00004` 화면으로 이동하는지 검증.
* **비동기 배치 스케줄러 연동**: 확정 처리 직후 `IMTRLGTB`에 `PROC_YN = 'N'`으로 수불 로그가 정상 적재되는지 검증.
* **보안 세션 주입**: 컨트롤러 내에서 `msNo` 및 `chainNo` 세션 주입을 통하여 매장 간 권한 침범이 차단되는지 검증.
