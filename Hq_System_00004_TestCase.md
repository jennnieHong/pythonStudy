# Hq_System_00004 — VAN사 정보 설정 단위 테스트케이스

> **화면**: [HQ] 시스템 > 기초코드관리 > VAN사 정보 설정  
> **URL Prefix**: `POST /backoffice/data/hq/system/hq_system_00004`  
> **@Transactional**: rollbackFor = {RuntimeException, Exception}  
> **요청 방식**: `@RequestBody` 기반 JSON  
> **DB 트리거 영향도**: CUD 조작 시 `Tr_VANMST_T01_Service` 실행되어 `SVANCOTB` 시스템 설정 동기화 이력 저장 및 `MMSLOGTB` 저장

---

## 세션 공통 선행 조건

| 세션 키 | 값 예시 | 사용 엔드포인트 |
|---------|---------|---------------|
| `ID` | `shopadmin` | save |

---

## 엔드포인트 목록 (3개)

| # | URL | 기능 | 요청 방식 | 반환 | Type | 관련 테이블 |
|---|---|---|---|---|---|---|
| 1 | `/search` | VAN사 마스터 조회 | `@RequestBody` | `List` | SELECT | VANMSTTB |
| 2 | `/save` | VAN사 등록/수정 분기 | `@RequestBody` | `String` | MERGE | VANMSTTB<br>SVANCOTB<br>MMSLOGTB |
| 3 | `/delete` | VAN사 삭제 전 검증 및 삭제 | `@RequestBody` | `String` | DELETE | MVANCOTB<br>VANMSTTB<br>SVANCOTB<br>MMSLOGTB |

---

## 1. `/search` — VAN사 마스터 조회

**처리 순서**:
```
Hq_System_00004_Service.selectVanMasterList(commandMap)
```

| No | RequestBody | 예상값 |
|----|-------------|-------|
| 1-1 | `{}` | 전체 VAN사 리스트 (VAN_CD, VAN_FG 정렬) |

---

## 2. `/save` — VAN사 마스터 등록/수정

**서비스 분기 로직**:
```
ID 세션 세팅 -> userId
if commandMap.get("procFg") == "update":
  updateVanMaster()
else:
  getVanMasterCnt() > 0 ? return "vanExist"
  else insertVanMaster()
return ""
```

**DB 연쇄 (Tr_VANMST_T01)**:
- insert: `SVANCOTB` 인서트(VAN/SUB_VAN), `MMSLOGTB` 기록 (A)
- update: `SVANCOTB` 인서트(VAN/SUB_VAN), `MMSLOGTB` 값 변경 내역 비교 기록 (U)

| No | DB 선행상태 | RequestBody | 예상값 |
|----|------------|-------------|-------|
| 2-1 | 해당 밴사 없음 | `{"procFg":"insert","vanCd":"V01","vanFg":"1","vanIp":"127.0.0.1","vanPortNo":"8080","vanName":"테스트"}` | 등록 완료, `""` 반환, 연쇄동기화 발생 |
| 2-2 | 동일 코드 존재 | `{"procFg":"insert","vanCd":"V01","vanFg":"1"}` | `getVanMasterCnt` > 0 → `"vanExist"` 반환 |
| 2-3 | 해당 밴사 존재 | `{"procFg":"update","vanCd":"V01","vanFg":"1","vanIp":"127.0.0.1","vanPortNo":"9090","vanName":"테스트_수정"}` | 수정 완료, `""` 반환, 연쇄동기화 발생 |
| 2-4 | 세션 ID 누락 | `{...}` (로그인 없이 호출 시) | `NullPointerException` (보안 인터셉터에서 차단됨) |

---

## 3. `/delete` — VAN사 삭제 검증 및 삭제

**서비스 분기 로직**:
```
getVanCoCnt(vanCd) > 0 ? return "vanCoExist"
else deleteVanMaster()
return ""
```

| No | DB 선행상태 | RequestBody | 예상값 |
|----|------------|-------------|-------|
| 3-1 | 매장 사용중 아님 (`MVANCOTB` 0건) | `{"vanCd":"V01","vanFg":"1"}` | 정상 삭제 완료, `""` 반환, 로그 발생 |
| 3-2 | 특정 매장에서 사용중 (`MVANCOTB` 존재) | `{"vanCd":"V01","vanFg":"1"}` | `getVanCoCnt` > 0 → `"vanCoExist"` 반환 (삭제 방어) |

---

## 주요 검증 포인트

```
□ save (insert) — 이미 동일한 코드가 존재할 경우 vanExist 문자열 반환 여부 검증
□ delete — MVANCOTB (VAN사 매장 설정) 테이블에 사용 이력이 있는 경우 vanCoExist 문자열 반환하여 무결성 오류 방어 검증
□ save (update) — 변경된 항목이 1개라도 있을 시 SVANCOTB 매장 동기화 이력이 정상적으로 쌓이는지 검증
□ SYSDATE 치환 검증 — insert, update 시 PostgreSQL의 NOW() 함수가 잘 적용되어 timestamp 필드에 반영되는지 검증
□ Tr_VANMST_T01 — MMSLOGTB 로그 기록 시 StringBuilder append가 정상 작동하여 전체 수정항목 이력이 누적되는지 검증
```

---
