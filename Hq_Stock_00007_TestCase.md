# Hq_Stock_00007 — 본사 폐기등록 단위 테스트케이스

> **화면**: [HQ] 재고 > 조정폐기관리 > 폐기등록  
> **URL Prefix**: `/backoffice/data/hq/stock/hq_stock_00007`  
> **@Transactional**: `rollbackFor = {RuntimeException.class, Exception.class}`  
> **요청 방식**: `@RequestBody` JSON (일부 `/insertList`, `/updateList`는 `@RequestParam` form-data 형식)  
> **DB 트리거 영향도**: 확정 시 `Tr_IMDUSE_T01_Service`가 기동하여 하위 수불 로그(`IMTRLGTB`) 및 분해 연산을 수행하는 연쇄 반응이 직접 발생합니다.

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | search, searchM01T01, insertList, updateList |
| `ID` | `shopadmin` | 공통 세션 및 등록/수정/확정자 ID로 매핑 |
| `chainMsNo` | `NC0002` | insertList, updateList (본사 대표매장 매핑) |

---

## 엔드포인트 목록 (6개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | 미확정 폐기 목록 조회 | `@RequestBody` | `List` | SELECT | IMDUSETB<br>TGOODSTB<br>IMCRIOTB |
| 2 | `/searchM01T01` | 폐기 등록용 매장 상품 조회 | `@RequestBody` | `List` | SELECT | TGOODSTB<br>MGOODSTB<br>IMCRIOTB |
| 3 | `/insertList` | 팝업 내 선택 상품 폐기 전표 등록 | `@RequestParam` | `int` (성공건수) | INSERT | IMDUSETB |
| 4 | `/updateList` | 수량 및 폐기 사유 수정 저장 | `@RequestParam` | `String` ('success') | UPDATE | IMDUSETB |
| 5 | `/deleteList` | 선택한 미확정 폐기 전표 삭제 | `@RequestBody` | `int` (성공건수) | DELETE | IMDUSETB |
| 6 | `/confirmList` | 선택한 폐기 전표 최종 확정 처리 | `@RequestBody` | `int` (성공건수 또는 -1) | UPDATE | IMDUSETB<br>IMTRLGTB |

---

## 1. `/search` — 미확정 폐기 목록 조회

**특이사항**:
* `searchFromDate` 및 `searchToDate` 날짜는 하이픈(`-`)을 제거한 `YYYYMMDD` 포맷으로 변환되어 전달됩니다.
* `PROC_FG = '0'`인 미확정(등록 대기) 상태의 전표 데이터만 노출됩니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 1-1 | chainNo=`C001` | 폐기 대기 데이터 존재 | `{"msNo":"NC0003","searchFromDate":"20260605","searchToDate":"20260605"}` | `List` 객체 반환, 오늘 추가된 미확정 전표(dUseQty, reasonCd 등) 리스트 출력 |
| 1-2 | chainNo=`C001` | - | `{"msNo":"NC0003","searchFromDate":"20260605","searchToDate":"20260605","lClass":"001","mClass":"001"}` | 대분류/중분류 필터링 검색 정상 적용 여부 |
| 1-3 | chainNo=`C001` | - | `{"msNo":"NC0003","searchFromDate":"20260605","searchToDate":"20260605","goodsNm":"포니"}` | 상품명(goodsNm) LIKE 검색 정상 적용 여부 |

---

## 2. `/searchM01T01` — 폐기 등록용 매장 상품 조회

**특이사항**:
* 폐기등록 팝업(M01) 내에서 상품을 골라 등록하기 위해, 해당 매장에 입점된 현재고가 존재하는 상품 마스터 목록을 조회합니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 2-1 | chainNo=`C001` | 매장 상품 마스터 존재 | `{"msNo":"NC0003","goodsNm":"","goodsCd":""}` | 해당 매장(`NC0003`)에서 취급하는 폐기 대상 상품 리스트 반환 |

---

## 3. `/insertList` — 선택 상품 폐기 전표 등록

**특이사항**:
* `@RequestParam` 형식으로 폼 전송을 진행합니다.
* 최초 등록 시 폐기수량(DISUSE_QTY)=0, 폐기원가(DISUSE_COST)=0, 상태코드(PROC_FG)='0' (대기)으로 적재됩니다.

| No | 세션 조건 | Request Parameter (Form Data) | 예상값 / 검증 포인트 |
|----|----------|--------------------------------|--------------------|
| 3-1 | chainNo=`C001`<br>userId=`shopadmin`<br>chainMsNo=`NC0002` | `msNo=NC0003`<br>`dUseDate=20260605`<br>`goodsCdArr[]=T0000291` | `1` 반환 (데이터 삽입 성공)<br>DB `IMDUSETB` 테이블 내 신규 행 생성 확인 |
| 3-2 | - | `msNo=` (매장 코드 누락) | `400 Bad Request` 또는 예외 반환 (Required 파라미터 체크) |

---

## 4. `/updateList` — 수량 및 폐기 사유 수정 저장

**특이사항**:
* `@RequestParam` 형식으로 폼 전송을 진행합니다.
* 사용자가 직접 입력한 총 폐기수량과 계산된 원가, 폐기 사유코드를 매치하여 `IMDUSETB`에 갱신합니다.

| No | 세션 조건 | Request Parameter (Form Data) | 예상값 / 검증 포인트 |
|----|----------|--------------------------------|--------------------|
| 4-1 | chainNo=`C001`<br>userId=`shopadmin` | `msNo=NC0003`<br>`goodsCdArr[]=T0000291`<br>`dUseTotArr[]=5`<br>`dUseCostArr[]=24000`<br>`reasonCdArr[]=C01`<br>`idxArr[]=00000000069509` | `'success'` 문자열 반환<br>`IMDUSETB` 내 수량 `5.00` 및 사유 `C01`로 갱신 확인 |

---

## 5. `/deleteList` — 선택한 미확정 폐기 전표 삭제

**특이사항**:
* 확정하기 전 대기 상태의 불필요한 폐기 로우를 물리 삭제 처리합니다.

| No | 세션 조건 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|---------------------|--------------------|
| 5-1 | - | `{"dataList":[{"idx":"00000000069509","msNo":"NC0003","goodsCd":"T0000291"}]}` | `1` 반환 (물리 삭제 완료)<br>DB `IMDUSETB` 내 해당 로우 삭제 확인 |

---

## 6. `/confirmList` — 선택한 폐기 전표 최종 확정 처리

**특이사항**:
* 확정 시 `IMTRLGTB` (수불 로그) 테이블에 폐기 구분('D') 수불 이력이 적재되는 연쇄 트리거 `Tr_IMDUSE_T01_Service`가 기동합니다.
* PostgreSQL/EDB `ROWNUM` 호환성 교정(`ROWNUM <= 1`) 반영 여부를 검증합니다.

| No | 세션 조건 | DB 선행상태 | RequestBody (JSON) | 예상값 / 검증 포인트 |
|----|----------|------------|---------------------|--------------------|
| 6-1 | userId=`shopadmin` | 미확정 폐기 존재 (idx:00000000069509) | `{"dataList":[{"idx":"00000000069509","msNo":"NC0003","goodsCd":"T0000291"}]}` | `1` 반환 (확정 성공)<br>1. `IMDUSETB.PROC_FG`가 `'1'`로 갱신<br>2. `IMTRLGTB`에 실시간 수불 데이터 삽입 확인 |
| 6-2 | userId=`shopadmin` | 수불 로그에 동일 매장 미처리 건 존재 | `{"dataList":[{"idx":"00000000069509","msNo":"NC0003","goodsCd":"T0000291"}]}` | `-1` 반환 (수불 테이블 락/지연 알림 분기) |

---

## PowerShell API 테스트 스크립트

개발 및 검증 단계에서 API를 직접 호출할 수 있도록 제공되는 PowerShell 스크립트 템플릿입니다.

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=shopadmin&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/hq/stock/hq_stock_00007"
$hJson = @{"Content-Type"="application/json"}
$hForm = @{"Content-Type"="application/x-www-form-urlencoded"}

# 1. 팝업창 내 매장 상품 조회
Invoke-RestMethod -Uri "$base/searchM01T01" -Method POST -Headers $hJson -WebSession $session `
  -Body '{"msNo":"NC0003","goodsNm":"","goodsCd":""}'

# 2. 신규 폐기상품 등록 (Qty=0)
Invoke-RestMethod -Uri "$base/insertList" -Method POST -Headers $hForm -WebSession $session `
  -Body "msNo=NC0003&dUseDate=20260605&goodsCdArr[]=T0000291"

# 3. 미확정 폐기전표 조회
$records = Invoke-RestMethod -Uri "$base/search" -Method POST -Headers $hJson -WebSession $session `
  -Body '{"msNo":"NC0003","searchFromDate":"20260605","searchToDate":"20260605"}'
$targetIdx = $records[0].idx

# 4. 수량 5개 및 사유 C01 수정 저장
Invoke-RestMethod -Uri "$base/updateList" -Method POST -Headers $hForm -WebSession $session `
  -Body "msNo=NC0003&goodsCdArr[]=T0000291&dUseTotArr[]=5&dUseCostArr[]=24000&reasonCdArr[]=C01&idxArr[]=$targetIdx"

# 5. 최종 확정 처리 (수불 전파 트리거 작동)
Invoke-RestMethod -Uri "$base/confirmList" -Method POST -Headers $hJson -WebSession $session `
  -Body "{`"dataList`":[{`"idx`":`"$targetIdx`",`"msNo`":`"NC0003`",`"goodsCd`":`"T0000291`"}]}"
```
