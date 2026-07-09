# St_Commu_00001 — 매장 공지사항 단위 테스트케이스

> **화면**: [ST] 거래처관리 > 커뮤니케이션 > 공지사항  
> **URL Prefix**: `POST /backoffice/data/st/communication/st_commu_00001`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식**: `@RequestBody` JSON 파라미터 매핑
> **DB 영향도**: `BBSNTCTB` (조회수 가산 UPDATE), `BBSLOGTB` (조회 이력 MERGE INSERT/UPDATE)

---

## 1. 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | selectNoticeList, noticeDetailView |
| `msNo` | `MS0001` | selectNoticeList, noticeDetailView |
| `ID` | `fnbcafe` | noticeDetailView |

---

## 2. 엔드포인트 목록

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/selectNoticeList` | 공지사항 목록 조회 (페이징) | `@RequestBody` | `Map` (total+rows) | SELECT | BBSNTCTB<br>BBSLOGTB |
| 2 | `/noticeDetailView` | 공지사항 상세 조회 (권한 검증 및 조회수 증가 포함) | `@RequestBody` | `Map` | SELECT/CUD | BBSNTCTB<br>BBSLOGTB<br>BBSNTUTB<br>FILEUPTB |

---

## 3. 상세 테스트 시나리오

### 3.1 `/selectNoticeList` — 공지사항 목록 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001`, msNo=`MS0001` | `{"offset":0,"limit":10,"toFg":"C","searchTerms":"","searchContents":""}` | 매장 권한에 부합하는 공지사항 목록 반환 |
| 1-2 | (동일) | `{"offset":0,"limit":10,"toFg":"C","searchTerms":"0","searchContents":"공지"}` | 제목 검색어 적용 목록 반환 |
| 1-3 | 세션 정보 없음 | `{}` | securityUserInformation NPE 발생 (500 Error) |

### 3.2 `/noticeDetailView` — 공지사항 상세보기

매장용 공지사항 상세 열람은 본사 화면과 다르게 **`checkNotice`**를 통한 권한 확인이 선행됩니다.
가맹점/매장의 열람 권한이 존재할 때(`cnt > 0`)만 HITS 증가 및 로그 머지를 진행하고 상세 내역을 로딩합니다.

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001`, msNo=`MS0001`, ID=`fnbcafe` | `{"idx": 1}` (열람 권한 있는 공지) | `CHECK_FLAG = "success"`, 상세 데이터 반환 및 `HITS` 증가 |
| 2-2 | (동일) | `{"idx": 9999}` (열람 권한 없는 공지) | `CHECK_FLAG = "fail"`, 빈 상세 데이터 반환, HITS 증가 생략 |

---

## 4. PowerShell 테스트 명령 예시

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:8080/backoffice/login" `
  -Method POST -Body "username=fnbcafe&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:8080/backoffice/data/st/communication/st_commu_00001"
$h = @{"Content-Type"="application/json"}

# 1. 목록 조회
Invoke-RestMethod -Uri "$base/selectNoticeList" -Method POST -Headers $h -WebSession $session `
  -Body '{"offset":0,"limit":10,"toFg":"C","searchTerms":"","searchContents":""}'

# 2. 상세 조회 및 HITS 가산 (권한 체크 통과 시)
Invoke-RestMethod -Uri "$base/noticeDetailView" -Method POST -Headers $h -WebSession $session `
  -Body '{"idx": 1}'
```

---

## 5. 브라우저 E2E 테스트 수행 결과 (Playwright)

### 5.1 E2E 테스트 개요
* **수행 도구**: Playwright (Async Python API)
* **테스트 스크립트**: [test_notice_playwright.py](file:///C:/Users/uoshj/.gemini/antigravity-ide/scratch/test_notice_playwright.py)
* **수행 일시**: 2026-06-29
* **주요 검증 동작**:
  1. `fnbcafe` 계정 자동 로그인 처리 (패스워드 `'0000'` 동적 변경 후 수행)
  2. 매장 공지사항 조회 화면 이동 (`st_commu_00001`). *데이터베이스 시드상 `fnbcafe` 계정의 메뉴 권한 매핑(`USERMLTB`)이 유실되어 있어 테스트 시점에 `000182` 메뉴에 대한 권한 매핑 레코드를 DB 상에 주입 후 진행.*
  3. 공지사항 테이블 그리드 `#st_commu_00001_t01` 로딩 대기 및 목록 화면 캡처 (`st_commu_00001_1_list.png`)
  4. 테이블 최상단 행(IDX = `99838`)의 상세 조회 모달 팝업 실행 및 화면 캡처 (`st_commu_00001_2_detail_modal.png`)
  5. DB 상에서 `BBSNTCTB.HITS` count가 정상 가산(4 ➡️ 5)됨을 확인
  6. DB 상의 `BBSLOGTB` 에 가맹점 번호(DB 실제값 `NC0007`, 엑셀 정의 `NC0002`) 기준의 열람 이력이 정상 생성됨을 교차 검증 완료
  7. 세션 로그아웃 및 로그인 자격증명 복구

### 5.2 최종 판정 및 증적
* **E2E 테스트 판정**: **PASS**
* **테스트 증적 스크린샷**: 
  * [st_commu_00001_1_list.png](file:///D:/hmTest/backoffice/QaReport/st_commu_00001_1_list.png)
  * [st_commu_00001_2_detail_modal.png](file:///D:/hmTest/backoffice/QaReport/st_commu_00001_2_detail_modal.png)
