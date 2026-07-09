# St_Master_00014 — 터치키 상품 이미지 등록 단위 테스트케이스

> **화면**: [ST] 마스터관리 > 터치키 상품 이미지 등록  
> **URL Prefix**: `POST /backoffice/data/st/master/st_master_00014`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식 혼용**: 조회 = `@RequestBody` / 이미지 등록 = `multipart/form-data` + `@RequestParam`
> **DB 트리거 영향도**: MMCPLKTB 등 CUD 발생으로 관련 트리거 연쇄 동작함 (상세 하단 참조)

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `chainNo` | `C001` | searchClPlu, savePluImage, deletePluImage |
| `msNo` | `MS001` | searchClPlu |
| `ID` | `I000449s` | savePluImage, deletePluImage |

---

## 엔드포인트 목록 (4개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/searchClPlu` | 터치키 분류 조회 (세션 chainNo/msNo) | `@RequestBody` | `List<ClPluListDto>` | SELECT | MMCPLUTB |
| 2 | `/searchPlu` | 터치키 상품 조회 (reqMap 기반) | `@RequestBody` | `List<PluListDto>` | SELECT | MMCPLKTB |
| 3 | `/savePluImage` | 터치키 상품 이미지 등록 (multipart) | `multipart/form-data` | `void` | INSERT | IMGMSTTB<br>MMCPLKTB |
| 4 | `/deletePluImage` | 터치키 상품 이미지 삭제 | `@RequestBody` | `void` | DELETE | MMCPLKTB |

---

## 1. `/searchClPlu` — 터치키 분류 조회

**특이사항**: `reqMap`(@RequestBody)을 받지만 실제로 **전혀 사용하지 않음** → 세션 값만 사용 ★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 1-1 | chainNo=`C001`, msNo=`MS001` | `{}` | 해당 매장 터치키 분류 목록 |
| 1-2 | chainNo=`C001`, msNo=`MS001` | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 2. `/searchPlu` — 터치키 상품 조회

**특이사항**: 세션 미사용 — `reqMap`의 `msNo`, `clPluCd`만 사용

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 2-1 | `{"msNo":"MS001","clPluCd":"01"}` | 해당 분류 상품 목록 |
| 2-2 | `{"msNo":"MS001"}` (clPluCd 없음) | `commandMap.put("clPluCd", null)` → Mapper null 처리 |
| 2-3 | `{}` (msNo/clPluCd 없음) | 둘 다 null → 전체 또는 빈 목록 |
| 2-4 | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## 3. `/savePluImage` — 이미지 등록

**서비스 처리 흐름**:
```
getImageSeq()                → idx (이미지 SEQ 채번)
fileStreamConfig.getProperty(...)  → filePath (서버 설정 기반 경로)
commonModuleService.getFileInfo()  → fileIdx(FILE_SEQ), newFileNm(FILE_NM)

while(iterator.hasNext()):
  multipartFile.transferTo(new File(filePath + newFileNm))  ← 실제 파일 저장
  insertImage():
    st_master_00014_mapper.insertImage()    → 이미지 마스터 INSERT
    st_master_00014_mapper.updatePluImage() → PLU 테이블 이미지 컬럼 UPDATE
  commonModuleService.insertFileUpload()   → 파일 업로드 공통 테이블 INSERT

★ multipartFile 없음(빈 요청) → iterator.hasNext() = false → 아무 처리 없음 (void)
★ filePath null(설정 미등록) → new File(null) → NullPointerException ★★★
★ (MultipartHttpServletRequest) 캐스팅 → multipart 아닌 요청 → ClassCastException ★★
```

| No | 세션 조건 | Request | 예상값 |
|----|----------|---------|-------|
| 3-1 | chainNo=`C001`, ID=`I000449s` | `msNo=MS001&clPluCd=01&pluCd=001` + 이미지 파일 | insertImage + updatePluImage + insertFileUpload 실행 → void |
| 3-2 | chainNo=`C001`, ID=`I000449s` | 파일 없이 form-data만 | iterator.hasNext()=false → void (아무 처리 없음) |
| 3-3 | chainNo=`C001`, ID=`I000449s` | `Content-Type: application/json` (non-multipart) | `(MultipartHttpServletRequest) req` → **ClassCastException** ★★ |
| 3-4 | chainNo=`C001`, ID=`I000449s` | 파일 있음, `msNo` 없음 (defaultValue="") | msNo="" → updatePluImage SQL WHERE msNo='' 처리 |
| 3-5 | chainNo=`C001`, ID=`I000449s` | 파일 2개 업로드 | while 루프 2회 → 2번째 파일로 idx/fileIdx 재사용 → 1번째 DB 기록과 충돌 가능 ★ |
| 3-6 | - | filePath 설정 미등록 | `fileStreamConfig.getProperty(...)` → null → **NullPointerException** ★★★ |

---

## 4. `/deletePluImage` — 이미지 삭제

**특이사항**: `void` 반환 — 성공/실패 구분 없음 ★

| No | 세션 조건 | RequestBody | 예상값 |
|----|----------|-------------|-------|
| 4-1 | chainNo=`C001`, ID=`I000449s` | `{"msNo":"MS001","clPluCd":"01","pluCd":"001"}` | deletePluImage → void |
| 4-2 | chainNo=`C001`, ID=`I000449s` | `{"msNo":"MS001"}` (clPluCd/pluCd 없음) | null 조건 → 의도치 않은 대량 삭제 가능 ★★★ |
| 4-3 | chainNo=`C001`, ID=`I000449s` | `{}` | 모든 조건 null → 전체 이미지 삭제 가능 ★★★ |
| 4-4 | - | (Body 없음) | 400 (`@RequestBody` 필수) |

---

## PowerShell 테스트 명령

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "http://localhost:18080/backoffice/login" `
  -Method POST -Body "username=I000449s&password=pass01!A" `
  -ContentType "application/x-www-form-urlencoded" `
  -SessionVariable session | Out-Null

$base = "http://localhost:18080/backoffice/data/st/master/st_master_00014"
$h = @{"Content-Type"="application/json"}

# 1-1. 분류 조회
Invoke-RestMethod -Uri "$base/searchClPlu" -Method POST -Headers $h -WebSession $session `
  -Body '{}'
# 예상: 터치키 분류 목록

# 2-1. 상품 조회
Invoke-RestMethod -Uri "$base/searchPlu" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001","clPluCd":"01"}'

# 3-3. non-multipart → ClassCastException
Invoke-RestMethod -Uri "$base/savePluImage" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001"}'
# 예상: 500 ClassCastException

# 3-1. 이미지 등록 (multipart)
$boundary = [System.Guid]::NewGuid().ToString()
$filePath = "C:\test_image.jpg"
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)
$body = "--$boundary`r`n"
$body += "Content-Disposition: form-data; name=`"msNo`"`r`n`r`nMS001`r`n"
$body += "--$boundary`r`n"
$body += "Content-Disposition: form-data; name=`"clPluCd`"`r`n`r`n01`r`n"
$body += "--$boundary`r`n"
$body += "Content-Disposition: form-data; name=`"pluCd`"`r`n`r`n001`r`n"
$body += "--$boundary`r`n"
$body += "Content-Disposition: form-data; name=`"file`"; filename=`"test_image.jpg`"`r`n"
$body += "Content-Type: image/jpeg`r`n`r`n"
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body) + $fileBytes + [System.Text.Encoding]::UTF8.GetBytes("`r`n--$boundary--")
Invoke-RestMethod -Uri "$base/savePluImage" -Method POST -WebSession $session `
  -ContentType "multipart/form-data; boundary=$boundary" -Body $bodyBytes

# 4-1. 이미지 삭제
Invoke-RestMethod -Uri "$base/deletePluImage" -Method POST -Headers $h -WebSession $session `
  -Body '{"msNo":"MS001","clPluCd":"01","pluCd":"001"}'

# 4-3. 조건 전체 null → 전체 삭제 위험
Invoke-RestMethod -Uri "$base/deletePluImage" -Method POST -Headers $h -WebSession $session `
  -Body '{}'
# 예상: void (대량 삭제 발생 가능 ★★★)
```

---

## 주요 검증 포인트

```
□ savePluImage — non-multipart 요청 → (MultipartHttpServletRequest) 캐스팅 → ClassCastException ★★
□ savePluImage — filePath 설정 미등록 → null → new File(null) → NullPointerException ★★★
□ savePluImage — 파일 2개 업로드 → while 루프 내 idx/fileIdx 재사용 → 두 번째 파일 덮어씀 ★
□ deletePluImage — 조건 null(msNo/clPluCd/pluCd 미전달) → 전체 이미지 삭제 가능 ★★★
□ deletePluImage — void 반환 → 성공/실패 클라이언트 구분 불가 ★
□ searchClPlu — @RequestBody 받지만 reqMap 미사용 → 불필요한 Body 의무화
□ searchPlu — 세션 미사용 → msNo를 Body에서 받음 → 타 매장 데이터 조회 가능 ★★
□ savePluImage — insertImage 내부: insertImage + updatePluImage 2단계 → 중간 실패 시 rollback 보장
□ @Transactional rollbackFor Exception — insertImage/deletePluImage rollback 보장
□ @Validated 있음 — @RequestParam required=false, defaultValue="" → 400 미발생
```

---

## ✅ v2 보완 — 소스 1:1 대조 결과

### @ServiceLog 현황 — 전체 정상 ✅

| 엔드포인트 | @ServiceLog |
|-----------|------------|
| `/getTouchKeyList` | ✅ SELECT (소스 64번) |
| `/getTouchKeyGoodsList` | ✅ SELECT (소스 91번) |
| `/saveImage` | ✅ INSERT (소스 115번) |
| `/deleteImage` | ✅ DELETE (소스 202번) |

**`@Validated` 클래스 레벨 적용** ✅ (소스 37번) — TC 전체 정확 ✅


## DB 트리거 및 프로시저 연관관계도 (코드베이스 전환용)

```text
API Endpoint 호출 (Service Logic)
└── [테이블] MMCPLKTB (CUD 작업)
    └── (Trigger) Tr_MMCPLK_T01
```
