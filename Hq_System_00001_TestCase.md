# Hq_System_00001 — POS 버전 등록/배포 단위 테스트케이스

> **화면**: [HQ] 시스템 > POS 버전 등록/배포  
> **URL Prefix**: `POST /backoffice/data/hq/system/hq_system_00001`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 조회 3개 = `@RequestBody` / CUD 6개 = `@RequestParam` (배열 포함) + Multipart
> **DB 트리거 영향도**: 없음 (단순 조회 화면이거나 트리거가 없는 테이블만 조작함)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | searchMs, searchVersionUpload |
| `ID` | `I000449` | saveVersionUpload, saveMsList |

---

## 엔드포인트 목록 (9개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/searchVersion` | 버전 리스트 조회 | `@RequestBody` | `List` | SELECT | MUSERSTB<br>MVERSNTB  |
| 2 | `/searchMs` | 매장 리스트 조회 | `@RequestBody` | `List` | SELECT | MMEMBPTB<br>MMEMBSTB<br>MVERSMTB<br>TCHAINTB  |
| 3 | `/searchVersionUpload` | 버전 업로드 리스트 조회 | `@RequestBody` | `List` | SELECT | MMEMBSTB<br>MNAMEMTB<br>MVERSMTB<br>MVERSNTB  |
| 4 | `/unusedVersion` | 버전 미사용 처리 | `@RequestBody` | `int` | UPDATE | MVERSNTB  |
| 5 | `/deleteVersion` | 버전 삭제 (확정 여부 체크 선행) | `@RequestBody` | `int` | DELETE | MVERSMTB<br>MVERSNTB  |
| 6 | `/saveVersionUpload` | 버전 파일 업로드 (`.zip` 전용) | Multipart + `@RequestParam` | `void` | INSERT | MVERSNTB  |
| 7 | `/saveMsList` | 매장 버전 배포 저장 (이중 루프, insert/update 분기) | `@RequestParam` 배열 | `int` | INSERT | MVERSMTB<br>MVERSNTB  |
| 8 | `/confirmVersionUpload` | 버전 배포 확정 (이중 루프 update) | `@RequestParam` 배열 | `int` | UPDATE | MVERSMTB  |
| 9 | `/deleteVersionUpload` | 버전 배포 취소/삭제 | `@RequestParam` 배열 | `int` | DELETE | MVERSMTB  |

---

## 1. `/searchVersion` — 버전 리스트 조회

**특이사항**: 세션 주입 없이 `commandMap`을 그대로 서비스에 전달

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 1-1 | `{}` | 전체 버전 리스트 |
| 1-2 | `{"posHwFg":"1"}` | 구분 필터 |
| 1-3 | `{"newVersionName":"v2.0"}` | 버전명 필터 |

---

## 2. `/searchMs` — 매장 리스트 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 2-1 | chainNo=`C001` | `{}` | chainNo=C001 기준 전체 매장 |
| 2-2 | chainNo=`C001` | `{"msNm":"테스트"}` | 매장명 필터 |
| 2-3 | searchMs 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 3. `/searchVersionUpload` — 버전 업로드 리스트 조회

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 3-1 | chainNo=`C001` | `{}` | 전체 배포 내역 |
| 3-2 | chainNo=`C001` | `{"msNo":"MS001","verSeq":"VER001"}` | 특정 매장+버전 필터 |
| 3-3 | searchVersionUpload 감사 미기록 | 호출 후 MMSLOGTB 확인 | 로그 없음 ★ |

---

## 4. `/unusedVersion` — 버전 미사용 처리

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 4-1 | `{"verSeq":"VER001"}` | update 1건 → 반환 `1` |
| 4-2 | `{"verSeq":"INVALID"}` | 해당 없음 → `0` |
| 4-3 | `{}` (verSeq 없음) | Mapper SQL 처리 (WHERE verSeq=null → 0건) |

---

## 5. `/deleteVersion` — 버전 삭제 (확정 여부 체크)

**서비스 로직**:
```
checkVersionConfirm(commandMap)
  > 0 → return 0  (확정 버전 → 삭제 불가)
  = 0 → deleteVersionList(commandMap) → return 삭제건수
```

| No | DB 선행상태 | RequestBody | 예상값 |
|----|------------|-------------|-------|
| 5-1 | 미확정 버전 | `{"verSeq":"VER001"}` | deleteVersionList → `1` |
| 5-2 | 확정된 버전 (checkVersionConfirm>0) | `{"verSeq":"VER001"}` | `0` (삭제 불가) |
| 5-3 | - | `{}` | verSeq=null → checkVersionConfirm 0건 → deleteVersionList(0건) |

---

## 6. `/saveVersionUpload` — 버전 파일 업로드

**처리 순서**:
```
1. getVersionSeq()                        ← 버전 SEQ 채번
2. fileStreamConfig.getProperty(FILE_UPLOAD_POS_VERSION)  ← 업로드 경로
3. commonModuleService.getFileInfo()      ← fileIdx, newFileNm 채번
4. while(iterator.hasNext()):
   → 확장자 검증: ".zip" 아니면 throw Exception("file extention type invalid")
   → multipartFile.transferTo(file)       ← 파일 저장
   → commandMap에 verSeq, newVersionName, posHwFg 등 세팅
5. commonModuleService.insertFileUpload() ← 파일 업로드 테이블 저장
6. insertVersionUpload()                  ← 버전 테이블 저장

★ 파일이 없으면(iterator.hasNext()=false):
   → while 루프 미진입 → commandMap에 verSeq/fileNm 등 미세팅
   → insertFileUpload(빈 commandMap) + insertVersionUpload(빈 commandMap)
   → DB insert null값 가능 ★★
```

| No | 세션 조건 | 파일/파라미터 | 예상값 |
|----|----------|-------------|-------|
| 6-1 | ID=`I000449` | `.zip` 파일 + `newVersionName=v2.0.1&posHwFg=1` | 파일 저장 → insertFileUpload → insertVersionUpload |
| 6-2 | ID=`I000449` | `.exe` 파일 + `newVersionName=v2.0.1&posHwFg=1` | `Exception("file extention type invalid")` → rollback |
| 6-3 | ID=`I000449` | 파일 없음 (multipart 미첨부) | iterator.hasNext()=false → commandMap 미세팅 → **null insert** ★★ |
| 6-4 | - | `newVersionName` 없음 (defaultValue="") | `@NotBlank` → 400 |
| 6-5 | - | `posHwFg="AB"` (2자) | `@Size(min=1,max=1)` → 400 |
| 6-6 | - | `posHwFg` 없음 (defaultValue="") | `@NotBlank` → 400 |

---

## 7. `/saveMsList` — 매장 버전 배포 저장

**서비스 이중 루프 로직**:
```
checkedVersionList 순회:
  selectVersionData(verSeq) → versionDataList 누적

checkedPosNoList 순회 (i):
  posNo = checkedPosNoList[i]
  msNo  = checkedMsNoList[i]      ← 배열 불일치 위험 ★
  chainNo = checkedChainNoList[i] ← 배열 불일치 위험 ★

  versionDataList 순회 (j):
    getProgressFg() > 0 → updateMsList  (update)
    else              → insertMsList   (insert)

반환: reault (마지막 실행 결과만, 누적 X)
```

| No | 세션 조건 | Request (form-param) | 예상값 |
|----|----------|----------------------|-------|
| 7-1 | ID=`I000449` | `checkedVersionList[]=VER001&checkedPosNoList[]=POS01&checkedMsNoList[]=MS001&checkedChainNoList[]=C001` | insert 또는 update 1건 |
| 7-2 | ID=`I000449` | 2개 버전 × 2개 POS (2×2=4건) | insertMsList/updateMsList 4건 순회 |
| 7-3 | ID=`I000449` | `checkedPosNoList[]=POS01&checkedPosNoList[]=POS02&checkedMsNoList[]=MS001` (길이 불일치) | `checkedMsNoList[1]` → **ArrayIndexOutOfBoundsException** ★★★ |
| 7-4 | ID=`I000449` | 배열 미전달 (defaultValue="") | `checkedVersionList=[""]` → `selectVersionData("")` → versionDataList 비어 있음, 외부 루프 `[""].length=1` 실행 |
| 7-5 | ID=`I000449` | `versionData.get("VER_SEQ")` null | `.toString()` → **NPE** ★★ |

---

## 8. `/confirmVersionUpload` — 버전 배포 확정

**서비스 이중 루프 로직**:
```
checkedVerSeqList 순회 (i):
  verSeq = checkedVerSeqList[i]
  msNo   = checkedMsNoList[i]    ← 배열 불일치 위험 ★
  
  getVerId(verSeq, msNo)
  getSeqList(verSeq, msNo, verId)
  
  seqList 순회 (j):
    seq.get("SEQ").toString()    ← SEQ null 시 NPE ★
    updateVersionUpload(commandMap)
```

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 8-1 | `checkedVerSeqList[]=VER001&checkedMsNoList[]=MS001` | seqList 순회 → updateVersionUpload |
| 8-2 | `checkedVerSeqList[]=VER001` (checkedMsNoList 미전달) | `checkedMsNoList=[""]` → `msNo=""` |
| 8-3 | 배열 길이 불일치 | `checkedMsNoList[i]` → **ArrayIndexOutOfBoundsException** ★★★ |
| 8-4 | seqList 비어 있음 | 내부 루프 미실행 → `reault=0` 반환 |
| 8-5 | `seq.get("SEQ")=null` | `.toString()` → **NPE** ★★ |

---

## 9. `/deleteVersionUpload` — 버전 배포 취소/삭제

**서비스 루프 로직**:
```
checkedVerSeqList 순회 (i):
  verSeq = checkedVerSeqList[i]
  msNo   = checkedMsNoList[i]  ← 배열 불일치 위험 ★
  deleteVersionUpload(commandMap)
```

| No | Request (form-param) | 예상값 |
|----|----------------------|-------|
| 9-1 | `checkedVerSeqList[]=VER001&checkedMsNoList[]=MS001` | delete 1건 → `1` |
| 9-2 | 2건 선택 | delete 2건 순회 → 마지막 결과 반환 |
| 9-3 | 배열 길이 불일치 | **ArrayIndexOutOfBoundsException** ★★★ |
| 9-4 | 배열 미전달 (defaultValue="") | `checkedVerSeqList=[""]`, `checkedMsNoList=[""]` → delete(""/"") → 0건 |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449&password=0000" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/hq/system/hq_system_00001"
$h = @{"Content-Type"="application/json"}
$f = "application/x-www-form-urlencoded"

# 1-1. 버전 리스트 조회
Invoke-RestMethod -Uri "$base/searchVersion" -Method POST -Headers $h -WebSession $session `
  -Body '{}'

# 2-1. 매장 리스트 조회
Invoke-RestMethod -Uri "$base/searchMs" -Method POST -Headers $h -WebSession $session `
  -Body '{}'

# 4-1. 미사용 처리
Invoke-RestMethod -Uri "$base/unusedVersion" -Method POST -Headers $h -WebSession $session `
  -Body '{"verSeq":"VER001"}'
# 예상: 1

# 5-1. 버전 삭제 (미확정)
Invoke-RestMethod -Uri "$base/deleteVersion" -Method POST -Headers $h -WebSession $session `
  -Body '{"verSeq":"VER001"}'

# 5-2. 버전 삭제 (확정됨 → 0 반환)
Invoke-RestMethod -Uri "$base/deleteVersion" -Method POST -Headers $h -WebSession $session `
  -Body '{"verSeq":"VER_CONFIRMED"}'

# 6-1. 버전 파일 업로드 (.zip)
$zipFile = "C:\test\pos_v2.0.1.zip"
$form = @{ newVersionName = "v2.0.1"; posHwFg = "1"; file = Get-Item $zipFile }
Invoke-RestMethod -Uri "$base/saveVersionUpload" -Method POST -WebSession $session -Form $form

# 6-2. 잘못된 확장자 (.exe)
$exeFile = "C:\test\pos_setup.exe"
$form2 = @{ newVersionName = "v2.0.1"; posHwFg = "1"; file = Get-Item $exeFile }
Invoke-RestMethod -Uri "$base/saveVersionUpload" -Method POST -WebSession $session -Form $form2
# 예상: 500 Exception("file extention type invalid")

# 7-1. 매장 버전 배포
Invoke-RestMethod -Uri "$base/saveMsList" -Method POST -ContentType $f -WebSession $session `
  -Body "checkedVersionList[]=VER001&checkedPosNoList[]=POS01&checkedMsNoList[]=MS001&checkedChainNoList[]=C001"

# 8-1. 배포 확정
Invoke-RestMethod -Uri "$base/confirmVersionUpload" -Method POST -ContentType $f -WebSession $session `
  -Body "checkedVerSeqList[]=VER001&checkedMsNoList[]=MS001"

# 9-1. 배포 취소
Invoke-RestMethod -Uri "$base/deleteVersionUpload" -Method POST -ContentType $f -WebSession $session `
  -Body "checkedVerSeqList[]=VER001&checkedMsNoList[]=MS001"
```

---

## 주요 검증 포인트

```
□ saveVersionUpload — .zip이 아닌 파일 → Exception rollback (파일 디렉토리 생성 후 롤백이므로 물리 파일 잔류 확인)
□ saveVersionUpload — 파일 미첨부 → while 미실행 → insertFileUpload/insertVersionUpload에 null 필드 insert ★★
□ saveMsList — checkedPosNoList/checkedMsNoList/checkedChainNoList 길이 불일치 → ArrayIndexOutOfBounds ★★★
□ saveMsList — versionData.get("VER_SEQ") null → toString() NPE ★★
□ saveMsList — 반환값: 마지막 insert/update 결과만 (누적 X) — UI에서 성공 여부 판단 주의
□ confirmVersionUpload — checkedVerSeqList/checkedMsNoList 길이 불일치 → ArrayIndexOutOfBounds ★★★
□ confirmVersionUpload — seq.get("SEQ") null → toString() NPE ★★
□ deleteVersionUpload — checkedVerSeqList/checkedMsNoList 길이 불일치 → ArrayIndexOutOfBounds ★★★
□ deleteVersion — checkVersionConfirm > 0 → return 0 (삭제 불가, 예외 미발생) — UI에서 0 체크 필요
□ @Transactional rollbackFor Exception — saveVersionUpload 파일 저장 후 Exception 시 DB rollback (물리 파일 미rollback)
□ searchVersion — 세션 주입 없음 — 모든 chainNo 버전 조회 가능 여부 확인
```

---

---

