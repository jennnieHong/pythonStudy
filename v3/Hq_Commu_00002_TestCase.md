# Hq_Commu_00002 — 공지사항 등록 관리 단위 테스트케이스

> **화면**: [HQ] 커뮤니케이션 > 공지사항 등록 관리  
> **URL Prefix**: `POST /backoffice/data/hq/communication/hq_commu_00002`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **공통 전제**: HQ 권한 계정으로 로그인된 세션 필요
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 설명 |
|---------|---------|------|
| `chainNo` | `C001` | 체인 번호 (자동주입) |
| `msNo` | `NC0001` | 본부 매장번호 (자동주입) |
| `ID` | `7249525SHOP` | 로그인 사용자 ID (자동주입) |
| `NAME` | `홍길동` | 로그인 사용자 이름 (자동주입) |

---

## 엔드포인트 목록 (8개)

| # | URL | 기능 | ServiceType  관련 테이블 |
|---|---|---|---|
| 1 | `/selectNoticeList` | 공지사항 목록 조회 (페이징) | SELECT | BBSLOGTB<br>BBSNTCTB  |
| 2 | `/insertNewNoticeContents` | 새 글쓰기 등록 | INSERT | BBSNTCTB  |
| 3 | `/insertNewNoticeFiles` | 새 글쓰기 첨부파일 업로드 | INSERT | BBSNTUTB  |
| 4 | `/insertModifyNoticeFile` | 상세보기 첨부파일 추가 업로드 | INSERT | BBSNTUTB  |
| 5 | `/deleteModifyNoticeFile` | 첨부파일 단건 삭제 | DELETE | BBSNTUTB  |
| 6 | `/modifyNoticeDetailView` | 상세내용 조회 (수정권한 체크) | SELECT | BBSNTCTB<br>BBSNTUTB<br>FILEUPTB  |
| 7 | `/saveNoticeContents` | 상세보기 내용 수정 | UPDATE | BBSNTCTB  |
| 8 | `/deleteNotice` | 게시글 삭제 (첨부파일 포함) | DELETE | BBSNTCTB<br>BBSNTUTB<br>FILEUPTB  |
| 9 | `/readingYn` | 매장 열람 여부 조회 | SELECT | BBSLOGTB<br>BBSNTCTB<br>MMEMBSTB  |

---

## 1. `/selectNoticeList` — 공지사항 목록 조회

**서비스 로직**: `selectNoticeList()` + `getTotalCnt()` → 페이징 목록 반환  
**세션 주입**: `chainNo`, `msNo`  
**방어 처리**: `confFg`, `searchTerms`, `searchContents` — containsKey 없으면 `""`

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001`, msNo=`NC0001` | `{"offset":0,"limit":10}` | `{"total":N,"rows":[...]}` |
| 1-2 | chainNo=`C001` | `{"offset":10,"limit":10}` | 2페이지 목록, startCount=11, endCount=20 |
| 1-3 | chainNo=`C001` | `{"offset":0,"limit":10,"confFg":"1"}` | confFg=1 필터링된 목록 |
| 1-4 | chainNo=`C001` | `{"offset":0,"limit":10,"searchTerms":"공지","searchContents":"내용"}` | 제목/내용 검색 결과 |
| 1-5 | chainNo=`C001` | `{"offset":0,"limit":10}` (confFg 키 없음) | confFg=`""` 처리, 전체 조회 |
| 1-6 | chainNo=`C001` | `{"limit":10}` (offset 키 없음) | NPE/ClassCastException → 500 |
| 1-7 | 세션 없음 | `{"offset":0,"limit":10}` | 302 redirect |

---

## 2. `/insertNewNoticeContents` — 새 글쓰기 등록

**서비스 로직**: `insertNoticeContents()` → DB INSERT 후 생성된 `idx` 반환  
**세션 주입**: `chainNo`, `userId`, `userName`  
**방어 처리**: `selectMsNo`, `searchFromDate`, `searchEndDate`, `toFg`, `nAuthor`, `nTitle`, `nContents` — 키 없으면 `""`

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001`, ID=`7249525SHOP`, NAME=`홍길동` | `{"toFg":"A","nTitle":"전체공지 테스트","nContents":"내용입니다","nAuthor":"홍길동","searchFromDate":"2026-05-01","searchEndDate":"2026-05-31","selectMsNo":""}` | 생성된 `idx` 문자열 반환 (예: `"101"`) |
| 2-2 | chainNo=`C001` | `{"toFg":"S","selectMsNo":"NC0007","nTitle":"특정매장 공지","nContents":"내용"}` | idx 반환, DB에 R_MS_NO=NC0007 저장 |
| 2-3 | chainNo=`C001` | `{"nTitle":""}` (nContents 키 없음) | nContents=`""` 저장 |
| 2-4 | chainNo=`C001` | `{}` (nTitle, nContents 등 키 전부 없음) | 모든 필드 `""` 저장, idx 반환 |
| 2-5 | 세션 없음 | `{"nTitle":"공지"}` | 302 redirect |

---

## 3. `/insertNewNoticeFiles` — 새 글쓰기 첨부파일 업로드

**Content-Type**: `multipart/form-data`  
**서비스 로직**:
1. 악성 확장자 체크 (`isMaliciousFile`) — 해당 시 즉시 반환
2. `files.isEmpty()` 체크
3. `commonModuleService.getFileInfo()` → FILE_SEQ 채번, 서버저장명 생성
4. `commonModuleService.insertFileUpload()` → FILEUPTB INSERT
5. `Mapper.insertNoticeFile()` → BBSNTUTB INSERT
6. `Files.write()` → 서버 파일 저장

**악성 확장자 블랙리스트**: `.jsp .php .exe .sh .bat .asp .aspx .cgi .js`

| No | 세션 조건 | Request (multipart) | 예상값 |
|----|----------|---------------------|-------|
| 3-1 | ID=`7249525SHOP` | `files-insert-notice=test.pdf`, `idx=101` | `{"success":true}`, DB 2곳 INSERT, 서버 파일 저장 |
| 3-2 | ID=`7249525SHOP` | `files-insert-notice=report.xlsx`, `idx=101` | `{"success":true}` |
| 3-3 | **악성 확장자 .jsp** | `files-insert-notice=shell.jsp`, `idx=101` | `{"success":false,"maliciousFile":true}`, 저장 안 됨 |
| 3-4 | **악성 확장자 .exe** | `files-insert-notice=virus.exe`, `idx=101` | `{"success":false,"maliciousFile":true}` |
| 3-5 | **악성 확장자 .js** | `files-insert-notice=script.js`, `idx=101` | `{"success":false,"maliciousFile":true}` |
| 3-6 | ID=`7249525SHOP` | `files-insert-notice=` (빈 파일), `idx=101` | `files.isEmpty()=true` → 저장 안 됨, `{"success":false}` |
| 3-7 | ID=`7249525SHOP` | 파일명=`null` | `isMaliciousFile(null)=true` → `{"success":false,"maliciousFile":true}` |
| 3-8 | ID=`7249525SHOP` | 다중 파일 `[a.pdf, b.docx]`, `idx=101` | 2건 모두 저장, `{"success":true}` |
| 3-9 | ID=`7249525SHOP` | 다중 파일 `[a.pdf, b.jsp]`, `idx=101` | b.jsp에서 차단, `{"success":false,"maliciousFile":true}`, a.pdf도 저장 안 됨 |
| 3-10 | 파일 업로드 DB 오류 | insertNoticeFiles 내부 예외 | `{"success":"파일 업로드 중 오류 발생: ..."}` — boolean false 아님 ★ |

---

## 4. `/insertModifyNoticeFile` — 상세보기 첨부파일 추가

**서비스 로직**: 3번과 동일하게 `insertNoticeFiles()` 호출  
**버그 주의**: 컨트롤러에서 `req.getFiles("files-insert-notice")` (오타: `files-modify-notice`가 아님)

| No | 세션 조건 | Request (multipart) | 예상값 |
|----|----------|---------------------|-------|
| 4-1 | ID=`7249525SHOP` | `files-modify-notice=추가파일.pdf`, `idx=101` | `{"success":true}` |
| 4-2 | **악성 확장자** | `files-modify-notice=hack.php`, `idx=101` | `{"success":false,"maliciousFile":true}` |
| 4-3 | **버그 확인** | `files-modify-notice=추가파일.pdf` | req.getFiles("files-insert-notice") 로 파일 로드 → fileList가 빈 리스트일 수 있음 |
| 4-4 | **정상 파일 업로드 시도** | `files-modify-notice=추가파일.pdf`, idx=101 | `success:true` 반환되나 **DB/서버에 파일 미저장** ★ (현재 버그) |
| 4-5 | **악성 파일 차단 불가** | `files-modify-notice=hack.php` | fileList 빈 리스트 → 악성체크 루프 미실행 → `success:true` ★ 보안 취약 |

---

## 5. `/deleteModifyNoticeFile` — 첨부파일 단건 삭제

**서비스 로직**:
1. `commonModuleService.selectFileInfo(fileIdx)` → 파일 경로/이름 조회
2. `Mapper.deleteNoticeFile()` → BBSNTUTB 삭제
3. `commonModuleService.deleteFileUpload()` → FILEUPTB 삭제여부 업데이트
4. 서버 파일 `File.delete()` 실행 (파일 존재 시)

**파라미터**: `@RequestParam` 방식 (RequestBody 아님)

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 5-1 | 로그인됨 | `idx=101&key=5` | `{"success":true}`, DB 2곳 삭제, 서버 파일 삭제 |
| 5-2 | 로그인됨 | 서버에 파일이 없는 경우 `idx=101&key=5` | DB는 삭제, 파일 없음 로그만 (`file.exists()=false`), `{"success":true}` |
| 5-3 | 로그인됨 | 존재하지 않는 `key=9999` | selectFileInfo null 가능 → NPE 위험 |
| 5-4 | 세션 없음 | `idx=101&key=5` | 302 redirect |
| 5-5 | **존재하지 않는 key** | `key=9999` (DB에 없음) | deleteNoticeFile 0건 UPDATE → 예외 없음 → `success:true` ★ (실패인데 성공 반환) |

---

## 6. `/modifyNoticeDetailView` — 상세내용 조회 (수정권한 체크)

**서비스 분기: USER_ID 일치 여부**

```
getNoticeDetailData(commandMap)
  → returnMap.get("USER_ID") 와 세션 ID 비교
  ├── 일치 → returnMap.put("EDIT_YN", "Y")  (전체 데이터 반환)
  └── 불일치 → returnMap.clear() → returnMap.put("EDIT_YN", "N")  (데이터 없이 N만)
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 6-1 | ID=`7249525SHOP` (작성자) | `{"idx":"101"}` (fnbadmin이 작성한 글) | `{..전체데이터.., "EDIT_YN":"Y"}` |
| 6-2 | **ID=`other01` (타인)** | `{"idx":"101"}` (fnbadmin이 작성한 글) | `{"EDIT_YN":"N"}` (데이터 clear 후 N만 반환) |
| 6-3 | ID=`7249525SHOP` | `{}` (idx 키 없음) | idx=`""` 처리, getNoticeDetailContents에 idx="" → 0건 또는 null |
| 6-4 | ID=`7249525SHOP` | `{"idx":"9999"}` (없는 게시글) | contentsMap null → NPE 위험 |
| 6-5 | ID=`7249525SHOP` | `{"idx":"101"}` (첨부파일 있는 글) | FILE_INFO_LIST, FILE_PREVIEW_LIST 포함 반환 |
| 6-6 | ID=`7249525SHOP` | `{"idx":"102"}` (첨부파일 없는 글) | FILE_INFO_LIST=`""`, FILE_PREVIEW_LIST=`""` |
| 6-7 | **없는 게시글(idx=9999)** | DB 0건 → getNoticeDetailData null 반환 | NPE → 500 ★ (현재 버그) |
| 6-8 | **USER_ID 컬럼 null** | USER_ID가 null인 게시글 | `returnMap.get("USER_ID")` null → equals NPE ★ |

---

## 7. `/saveNoticeContents` — 상세보기 내용 수정

**서비스 로직**: `updateNoticeContents()` 단순 UPDATE  
**세션 주입**: `chainNo`, `userId`, `userName`  
**방어 처리**: `idx`, `targetMsNo`, `fromDate`, `toDate`, `toFg`, `author`, `title`, `contents` — 키 없으면 `""`

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 7-1 | ID=`7249525SHOP` | `{"idx":"101","title":"수정된제목","contents":"수정내용","toFg":"A","fromDate":"2026-05-01","toDate":"2026-05-31","author":"홍길동","targetMsNo":""}` | `{"success":true}`, DB UPDATE 확인 |
| 7-2 | ID=`7249525SHOP` | `{"idx":"101","title":"제목만수정"}` (나머지 키 없음) | 나머지 필드 `""` 로 덮어씌워짐 주의 |
| 7-3 | ID=`7249525SHOP` | `{}` (idx 키 없음) | idx=`""` 처리, 0건 UPDATE |
| 7-4 | ID=`7249525SHOP` | `{"idx":"9999"}` (없는 글) | 0건 UPDATE, `{"success":true}` (오류 미발생) |
| 7-5 | 세션 없음 | `{"idx":"101"}` | 302 redirect |

---

## 8. `/deleteNotice` — 게시글 삭제

**서비스 로직** (첨부파일 → 게시글 순서 삭제):
```
1. getNoticeDetailFiles() → 첨부파일 목록 조회
   ├── 파일 있음 → 각 파일에 대해:
   │   ├── commonModuleService.selectFileInfo()
   │   ├── Mapper.deleteNoticeFile() → BBSNTUTB 삭제
   │   ├── commonModuleService.deleteFileUpload() → FILEUPTB 업데이트
   │   └── File.delete() → 서버 파일 삭제
   └── 파일 없음 → 스킵
2. Mapper.deleteNoticeContents() → 본문 삭제
3. Mapper.deleteNoticeFiles() → 파일 목록 삭제
```

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 8-1 | ID=`7249525SHOP` | `{"idx":"101"}` (첨부파일 없는 글) | `{"success":true}`, 본문만 삭제 |
| 8-2 | ID=`7249525SHOP` | `{"idx":"102"}` (첨부파일 2건 있는 글) | 파일 2건 서버삭제 + DB삭제 → 본문삭제, `{"success":true}` |
| 8-3 | ID=`7249525SHOP` | `{"idx":"103"}` (서버에 파일 없는 경우) | file.exists()=false → 로그만, DB는 정상 삭제 |
| 8-4 | ID=`7249525SHOP` | `{}` (idx 없음) | idx=`""`, 0건 삭제, `{"success":true}` |
| 8-5 | ID=`7249525SHOP` | `{"idx":"9999"}` (없는 글) | 파일목록=0, 0건 삭제, `{"success":true}` |
| 8-6 | **@Transactional** | 파일 삭제 중 DB 오류 | deleteNoticeContents도 롤백, 서버 파일은 이미 삭제됨 (비일관성 주의) |

---

## 9. `/readingYn` — 매장 열람 여부 조회

**파라미터**: `idx`, `toFg` (RequestBody에서 직접 get)  
**세션 주입 없음** (체인 필터 없이 조회)

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 9-1 | 로그인됨 | `{"idx":"101","toFg":"A"}` | 매장별 열람 여부 List |
| 9-2 | 로그인됨 | `{"idx":"101","toFg":"S"}` | 특정 매장 열람 List |
| 9-3 | 로그인됨 | `{"idx":"9999"}` (없는 글) | `[]` |

---

## 서비스 핵심 분기 요약

```
insertNewNoticeFiles / insertModifyNoticeFile (파일 업로드)
├── isMaliciousFile(파일명) → true  → {"success":false,"maliciousFile":true} 즉시 반환
├── files.isEmpty()         → true  → 저장 안 함, {"success":false}
└── 정상 → getFileInfo() → insertFileUpload() → insertNoticeFile() → Files.write()

modifyNoticeDetailView (수정권한)
├── 세션 ID == DB USER_ID → EDIT_YN="Y", 전체 데이터 반환
└── 세션 ID != DB USER_ID → returnMap.clear() → EDIT_YN="N" 만 반환

deleteNotice (첨부파일 연쇄 삭제)
├── 첨부파일 있음 → 파일별 BBSNTUTB삭제 + FILEUPTB업데이트 + 서버파일삭제
└── deleteNoticeContents + deleteNoticeFiles (항상 실행)
```

---

## PowerShell 테스트 명령

```powershell
# 로그인
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=7249525SHOP&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/communication/hq_commu_00002"
$h = @{"Content-Type"="application/json"}

# 1. 목록 조회
Invoke-RestMethod -Uri "$base/selectNoticeList" -Method POST `
  -Body '{"offset":0,"limit":10}' -Headers $h -WebSession $session

# 2. 새 글 등록
$newIdx = Invoke-RestMethod -Uri "$base/insertNewNoticeContents" -Method POST `
  -Body '{"toFg":"A","nTitle":"테스트공지","nContents":"내용","nAuthor":"홍길동","searchFromDate":"2026-05-01","searchEndDate":"2026-05-31","selectMsNo":""}' `
  -Headers $h -WebSession $session
Write-Host "생성된 idx: $newIdx"

# 3. 파일 업로드 (pdf)
$form = @{ "files-insert-notice" = Get-Item "C:\test\sample.pdf"; "idx" = $newIdx }
Invoke-RestMethod -Uri "$base/insertNewNoticeFiles" -Method POST `
  -Form $form -WebSession $session
# 예상: {"success":true}

# 3-악성. 악성 파일 업로드 차단 테스트
$form2 = @{ "files-insert-notice" = Get-Item "C:\test\shell.jsp"; "idx" = $newIdx }
Invoke-RestMethod -Uri "$base/insertNewNoticeFiles" -Method POST `
  -Form $form2 -WebSession $session
# 예상: {"success":false,"maliciousFile":true}

# 6. 상세 조회 (작성자 본인)
Invoke-RestMethod -Uri "$base/modifyNoticeDetailView" -Method POST `
  -Body "{`"idx`":`"$newIdx`"}" -Headers $h -WebSession $session
# 예상: {..전체데이터.., "EDIT_YN":"Y"}

# 7. 내용 수정
Invoke-RestMethod -Uri "$base/saveNoticeContents" -Method POST `
  -Body "{`"idx`":`"$newIdx`",`"title`":`"수정제목`",`"contents`":`"수정내용`",`"toFg`":`"A`",`"fromDate`":`"2026-05-01`",`"toDate`":`"2026-05-31`",`"author`":`"홍길동`",`"targetMsNo`":`"`"}" `
  -Headers $h -WebSession $session
# 예상: {"success":true}

# 8. 게시글 삭제
Invoke-RestMethod -Uri "$base/deleteNotice" -Method POST `
  -Body "{`"idx`":`"$newIdx`"}" -Headers $h -WebSession $session
# 예상: {"success":true}
```

---

## 사전 조건 (Test Data)

| 테이블 | 필요 데이터 |
|--------|-----------|
| `BBSNTICOTB` | 공지사항 본문 (idx, USER_ID, TITLE, CONTENT 등) |
| `BBSNTUTB` | 공지사항 첨부파일 연결 |
| `FILEUPTB` | 파일 업로드 통합 관리 |
| `MUSERSTB` | 7249525SHOP, other01 계정 |
| `MMEMBSTB` | 체인 매장 정보 (readingYn 조회용) |
| 서버 디렉토리 | `Constants.FILE_UPLOAD_BOARD_NOTICE` 경로 존재 및 쓰기 권한 |

---

## 주요 검증 포인트

```
□ insertNewNoticeFiles — 악성 확장자 9종 블랙리스트 각각 차단 확인
□ insertModifyNoticeFile — req.getFiles("files-insert-notice") 오타 버그 → 파일 미저장 가능성
□ modifyNoticeDetailView — 타인 접근 시 returnMap.clear() 동작, EDIT_YN=N만 반환
□ deleteNotice @Transactional — 서버 파일 삭제 후 DB 오류 시 비일관성 (파일은 삭제됐는데 DB는 롤백)
□ saveNoticeContents — 키 누락 시 "" 덮어쓰기, 특히 title/contents 공백화 위험
□ selectNoticeList — offset 키 누락 시 NPE 발생 여부
```

---

