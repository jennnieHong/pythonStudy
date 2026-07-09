# Admin_System_00001 — POS 버전 등록/배포 단위 테스트케이스

> **화면코드**: `admin_system_00001`  
> **URL Prefix**: `POST /backoffice/data/admin/system/admin_system_00001`  
> **권한**: ADMIN 세션 (admin2)  
> **서비스**: `Admin_System_00001_Service`  
> **DB 트리거 영향도**: `MVERSNTB`, `MVERSMTB` 대상 CUD 발생 (단, 운영 DDL 기준 명시적 트리거 로직은 발견되지 않음)

---

## 엔드포인트 목록 (9개)

| # | URL | 기능 | 요청방식 | ServiceType | 관련 테이블 |
|---|---|---|---|---|---|
| 1 | `/searchVersion` | 버전 리스트 조회 | RequestBody | SELECT | `MVERSNTB`, `MUSERSTB` |
| 2 | `/searchMs` | 매장 리스트 조회 | RequestBody | SELECT | `MMEMBSTB`, `MMEMBPTB`, `MVERSMTB`, `TCHAINTB` |
| 3 | `/searchVersionUpload` | 버전 업로드 리스트 조회 | RequestBody | SELECT | `MVERSMTB`, `MMEMBSTB`, `MVERSNTB`, `MNAMEMTB` |
| 4 | `/unusedVersion` | 버전 미사용 처리 | RequestBody | UPDATE | `MVERSNTB` (DELETE_FG = '1') |
| 5 | `/deleteVersion` | 버전 삭제 | RequestBody | DELETE | `MVERSMTB`(확정체크), `MVERSNTB` |
| 6 | `/saveVersionUpload` | 버전 업로드 (파일 포함) | Multipart | INSERT | `MVERSNTB`, (파일업로드 테이블) |
| 7 | `/saveMsList` | 매장 버전배포 저장 | RequestParam | INSERT | `MVERSMTB` |
| 8 | `/confirmVersionUpload`| 매장 버전배포 확정 | RequestParam | UPDATE | `MVERSMTB` (CONFIRM_FG = '1') |
| 9 | `/deleteVersionUpload` | 매장 버전배포 취소 | RequestParam | DELETE | `MVERSMTB` (CONFIRM_FG = '0' 인 건) |

---

## 1. `/searchVersion` — 버전 리스트 조회

**서비스**: `getVersionList()`  
**요청**: `@RequestBody HashMap<String,Object> commandMap`

| No | TC | Request | 예상값 | 비고 |
|----|----|---------|-------|------|
| 1-1 | 전체 조회 | `{}` | 버전 목록 `List<Admin_System_00001_VersionListDto>` | POS_HW_FG_NM 디코딩 포함 |
| 1-2 | 버전명 검색 | `{"versionName": "1.0"}` | 조건에 맞는 버전 목록 | MVERSNTB.VER_NM like 검색 |

---

## 2. `/saveVersionUpload` — 버전 업로드 (마스터 저장)

**서비스 흐름**:
1. `getVersionSeq()` → `VER_SEQ` 채번 (Oracle `LPAD(NVL(MAX(VER_SEQ)+1,1),8,'0')`)
2. 첨부파일 유효성 검증 (`.zip` 확장자) 및 물리적 저장
3. 공통 파일업로드 테이블 이력 저장
4. `insertVersionUpload()` → `MVERSNTB` 에 데이터 INSERT

**요청**: Multipart (파일 첨부), `newVersionName`, `posHwFg`

| No | TC | Request | 예상값 | 비고 |
|----|----|---------|-------|------|
| 2-1 | 정상 저장 | 파일첨부, `newVersionName=v1.1`, `posHwFg=0` | DB `MVERSNTB` 저장 확인 | `VER_SEQ` 채번 정상 처리 여부 |
| 2-2 | zip 확장자 아님 | `.txt` 파일 첨부 | Exception 발생 | "file extention type invalid" |
| 2-3 | 파라미터 누락 | `newVersionName` 빈값 | 400 Bad Request | `@NotBlank` 제약 조건 |

---

## 3. `/deleteVersion` — 버전 삭제

**서비스 흐름**:
1. `checkVersionConfirm()` → `MVERSMTB` 에서 `CONFIRM_FG = '1'` 인 매장배포건 존재 여부 확인
2. 존재하면 `0` 반환 후 삭제 중단
3. 존재하지 않으면 `deleteVersionList()` → `MVERSNTB` 삭제

| No | TC | Request | 예상값 | 비고 |
|----|----|---------|-------|------|
| 3-1 | 정상 삭제 | `{"verSeq": ["00000001"]}` (미확정 상태) | `1` (삭제 성공) | |
| 3-2 | 배포 확정된 버전 | `{"verSeq": ["00000002"]}` (확정 상태) | `0` 반환 (삭제 중단) | 무결성 보호 |

---

## 4. `/saveMsList` — 매장 버전배포 저장

**서비스 흐름**:
파라미터로 넘어온 버전과 매장 목록을 루핑하여 `MVERSMTB`에 INSERT

| No | TC | Request | 예상값 | 비고 |
|----|----|---------|-------|------|
| 4-1 | 정상 저장 | 매장 목록, 버전 목록 전달 | `MVERSMTB` 다건 INSERT | 기존 진행건(`CONFIRM_FG=0`)은 UPDATE |

---

## 5. `/confirmVersionUpload` — 매장 버전배포 확정

**서비스 흐름**:
1. `getVerId()` → `VER_ID` 채번
2. `updateVersionUpload()` → `MVERSMTB` 의 `CONFIRM_FG = '1'` 로 업데이트

| No | TC | Request | 예상값 | 비고 |
|----|----|---------|-------|------|
| 5-1 | 정상 확정 | 미확정 상태의 시퀀스 목록 | `CONFIRM_FG = '1'` 로 변경 | |

---

## DB 구조 분석 (Oracle -> PostgreSQL 전환 주의점)

1. **채번 로직**: `Admin_System_00001_Sql.xml` 의 `getVersionSeq` 등 쿼리에 Oracle 전용 함수인 `NVL()`, `TO_NUMBER()` 사용.
2. **날짜 삽입**: INSERT 구문에 `SYSDATE` 를 문자열 포맷팅(`TO_CHAR`)하여 넣는 로직 산재.
3. **외부 조인**: `getMsList` 에서 `D.MS_NO(+) = A.MS_NO` 와 같이 Oracle 고유의 외부 조인 `(+)` 문법 사용. PostgreSQL에서는 `LEFT JOIN` 으로 구조적 변경 필수.
