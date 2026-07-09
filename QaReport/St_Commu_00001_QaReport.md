# QA Report: St_Commu_00001 가맹점 공지사항 조회

**작성일**: 2026-06-29  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 가맹점 백오피스 > 커뮤니케이션 > 공지사항 > 공지사항 (st_commu_00001)  
**테스트 환경**: http://localhost:8080 (로컬 개발 서버)  
**접속ID/PW**: `fnbcafe / 0000` (F&B 매장 계정)  

---

## 1. 분석 개요

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | [St_Commu_00001_Controller.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/java/com/hyundai/backoffice/webapp/controller/st/communication/St_Commu_00001_Controller.java) |
| Service | [St_Commu_00001_Service.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-service/src/main/java/com/hyundai/backoffice/webapp/service/st/communication/St_Commu_00001_Service.java) |
| Mapper (Interface) | [St_Commu_00001_Mapper.java](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-layer-persistence/src/main/java/com/hyundai/backoffice/webapp/dao/st/communication/St_Commu_00001_Mapper.java) |
| SQL XML | [St_Commu_00001_Sql.xml](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/resources/sqlmapper/communication/St_Commu_00001_Sql.xml) |

---

## 2. 엔드포인트 분석

### 2.1 Base URL
```
POST /backoffice/data/st/communication/st_commu_00001/{endpoint}
```

### 2.2 엔드포인트 목록

| 엔드포인트 | HTTP | 기능 | ServiceLog | 관련 테이블 |
|-----------|------|------|------------|-----------|
| `/selectNoticeList` | POST | 공지사항 목록 조회 (페이징 포함) | SELECT | `BBSNTCTB`, `BBSLOGTB` |
| `/noticeDetailView` | POST | 공지사항 상세 조회 및 조회수 증가 | SELECT | `BBSNTCTB`, `BBSLOGTB`, `BBSNTUTB`, `FILEUPTB` |

---

## 3. 서비스 로직 분석 (코드베이스 변환 검증)

### 3.1 공지사항 상세 조회 및 조회수 가산 흐름 (`noticeDetailView`)

가맹점 공지사항 조회는 본사 조회 화면과 다르게 **해당 가맹점이 실제로 열람 가능한 공지사항인지 권한 체크(`checkNotice`)를 선행**합니다.

```
[Controller] detailView
  ├─ checkNotice()                     → 수신처에 매장번호(msNo) 또는 체인번호(chainNo)가 매핑되는지 검증
  ├─ [분기] cnt > 0 일 때만 실행:
  │    ├─ increaseNoticeHits()         → 조회수 증가 처리 (Transactional)
  │    │    ├─ updateHitsLog()        → BBSLOGTB MERGE INTO (조회 로그 적재)
  │    │    └─ updateNoticeHits()     → BBSNTCTB HITS + 1 (조회수 가산)
  │    └─ getNoticeDetailData()        → 공지 상세 본문 및 첨부파일 정보 로딩
  │         ├─ getNoticeDetailContents()
  │         └─ getNoticeDetailFiles()
  └─ CHECK_FLAG: "success" / "fail" 반환
```

---

## 4. DB 트리거 → 코드베이스 연쇄 분석

### 4.1 트리거 및 프로시저 영향도 검증 (Depth 3)
* **결과**: **`BBSNTCTB` 및 `BBSLOGTB` 테이블과 관련하여 적재/수정 시 동작하는 DB 트리거 및 Stored Procedure는 운영 DDL 분석 결과 전혀 존재하지 않는 것으로 판명되었습니다.**
* 따라서 이 모듈은 데이터의 연쇄 흐름을 갖지 않으며, MyBatis 매퍼를 통한 단순 직접 DML(`UPDATE` 및 `MERGE INTO`)로직만 구동됩니다.

### 4.2 EPAS 형변환 결함 분석 (Numeric 형변환 에러 검토)
* **검토 대상**: `/noticeDetailView` 시 발생하는 조회수 증가 및 로그 누적 파라미터.
* **분석 결과**:
  * `updateNoticeHits` 쿼리는 파라미터를 사용하지 않고 내부적으로 `HITS = HITS + 1` 처리를 직접 수식으로 갱신합니다.
  * `updateHitsLog` 쿼리는 가맹점의 단순 조회 횟수를 누적하기 위해 `A.HIT_COUNT = HIT_COUNT + 1` 수식을 사용하거나, 최초 적재 시 고정값 `1`을 대입합니다.
  * **즉, 빈 문자열(`''`)을 `numeric` 타입으로 변환하려고 시도하여 형변환 오류가 발생할 수 있는 매개변수 바인딩 컬럼이 본 화면의 CUD 쿼리에는 전혀 존재하지 않습니다.** 따라서 해당 유형의 결함으로부터 안전합니다.

---

## 5. 브라우저 화면 테스트 결과

### 5.1 화면 접속 현황

| 항목 | 결과 |
|------|------|
| 서버 접속 URL | `http://localhost:8080` |
| 로그인 ID / PW | `fnbcafe / 0000` (F&B 가맹점 권한) |
| 화면 경로 | 거래처관리 > 커뮤니케이션 > 공지사항 > 공지사항 |
| 화면 로딩 여부 | 정상 (데이터 조회 및 레이아웃 정상 표시 확인) |

### 5.2 상세 E2E 검증 결과

* **테스트 진행 방법**: Playwright 자동화 엔진을 사용하여 로그인부터 해당 화면 이동, 테이블 데이터 로딩 대기, 행 클릭에 의한 상세 정보 모달 팝업 및 DB 갱신 검증을 완료했습니다.
* **상세 결과 데이터**:
  * 테이블 로딩 완료 시 첫 번째로 표시된 공지사항 일련번호(`IDX`): **`99838`** (제목: `629 - 3`)
  * **조회수 증가 검증**:
    * 상세 모달 오픈 전 `BBSNTCTB.HITS` 값: **`6`** (앞서 가산된 상태)
    * 첫 번째 공지사항 상세 모달 클릭 후 `BBSNTCTB.HITS` 값: **`7`** (정상 가산 확인 ✅)
  * **조회 로그 적재 검증**:
    * `BBSLOGTB` 조회 결과 가맹점 번호 (DB 실제값 `NC0007`, 엑셀 정의 `NC0002`)에 대해 `IDX = 99838`로 열람 횟수 누적 및 최초/최종 열람 시간이 적재 완료된 것을 데이터베이스에서 확인했습니다. (정상 적재 확인 ✅)

### 5.3 기능별 테스트 판정

| 기능 | 엔드포인트 | 코드 구현 | 화면 UI 및 결과 | 판정 |
|------|-----------|---------|----------------|------|
| 공지사항 목록 조회 | `/selectNoticeList` | 구현 완료 | ✅ 데이터 그리드 테이블 정상 로딩 | **PASS** |
| 공지사항 상세 조회 | `/noticeDetailView` | 구현 완료 | ✅ 상세 팝업 모달 정상 팝업 | **PASS** |
| 조회수 가산 업데이트 | `updateNoticeHits` | 구현 완료 | ✅ 데이터베이스 HITS 수치 가산 확인 | **PASS** |
| 조회이력 머지/로그 적재 | `updateHitsLog` | 구현 완료 | ✅ 데이터베이스 BBSLOGTB 로그 적재 확인 | **PASS** |

---

## 6. SQL Mapper 검증 및 정렬 결함 해결

### 6.1 공지사항 생성일자 정렬(오름차순 ➡️ 내림차순) 수정 내역 (Critical ✅)
* **결과**: 기존 `selectNoticeList` 쿼리는 페이징 처리를 위해 서브쿼리 내부에서 `ROW_NUMBER() OVER (ORDER BY A.CREATE_DTIME DESC) AS RNUM` (내림차순)과 `ROW_NUMBER() OVER (ORDER BY A.CREATE_DTIME) AS RNUM1` (오름차순)을 동시에 연산하고 있었습니다.
* 하지만 **가장 바깥쪽 메인 쿼리에 명시적인 `ORDER BY` 절이 누락**되어 있어, PostgreSQL/EDB 쿼리 컴파일러가 최종 결과를 인덱스 탐색 및 `RNUM1` 정렬 흐름에 의한 **생성일자 오름차순(오래된 공지부터 노출)**으로 출력하는 오류를 발생시켰습니다.
* **조치 내용**: 가맹점/본사의 공지사항 목록 쿼리(`/selectNoticeList`) XML 내에 명시적인 **`ORDER BY T.RNUM`** 구문을 삽입하여 최신 등록된 공지사항이 상단에 내림차순 정렬로 노출되도록 보정 완료했습니다.

### 6.2 Oracle 호환 문법 잔존 여부 (PostgreSQL 마이그레이션 점검)
현재 개발 디렉토리 상의 `St_Commu_00001_Sql.xml` 쿼리는 다음과 같습니다.
1. **`(+)` 아우터 조인 문법 잔존**: 
   * `selectNoticeList` 쿼리에서 `WHERE B.MS_NO(+) = #{msNo} AND B.IDX(+) = A.IDX`와 같이 Oracle 전용 아우터 조인 기호가 그대로 사용되고 있습니다.
   * **영향도**: 개발 EDB(PostgreSQL)의 경우 Oracle 문법 호환성이 매우 우수하여 현재 쿼리로 정상 동작하지만, 표준 PostgreSQL로 완전 전환 시에는 표준 `LEFT JOIN` 구문으로 명시적 변환이 필수적입니다.
2. **`TO_NUMBER` 단일 매개변수 사용**:
   * `T.RNUM BETWEEN TO_NUMBER(#{startCount}) AND TO_NUMBER(#{endCount})` 구문이 사용되었습니다. EDB 상에서는 단일 인자 함수가 지원되어 동작하지만, 표준 PostgreSQL에서는 두 번째 인자(포맷)가 요구되므로 `::integer` 형태로 캐스팅하는 편이 권장됩니다.

---

## 7. 검증 항목 체크리스트

### 7.1 코드베이스 변환 정합성

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| `@RestController`, `@RequestMapping` 어노테이션 | ✅ 정상 | `/backoffice/data/st/communication/st_commu_00001` |
| `@Transactional` 주입 및 롤백 규칙 설정 | ✅ 정상 | `rollbackFor = {RuntimeException.class, Exception.class}` |
| 상세 조회 시 권한 선행 확인 (`checkNotice`) | ✅ 정상 | 권한 일치 시에만 Hits 가산 및 본문 노출 |
| `@ServiceLog` 어노테이션 누락 여부 | ✅ 정상 | 목록 조회 및 상세 내용 조회에 올바르게 적용됨 |
| MyBatis Mapper 매핑 및 XML 구현 정합성 | ✅ 정상 | 인터페이스 선언과 XML 쿼리 ID가 1:1 대응됨 |

---

## 8. 발견된 이슈 및 권고사항

### 🔴 Critical (즉시 처리 필요)
* 없음 (공지 정렬 이상 결함 조치 완료)

### 🟡 Warning (향후 완전 마이그레이션 시 변환 권고)
1. **Oracle 아우터 조인 `(+)` 문법 잔존**: 
   * `St_Commu_00001_Sql.xml` 내 `selectNoticeList` 쿼리의 `(+)` 조인을 표준 ANSI `LEFT JOIN` 형식으로 리팩토링할 것을 권장합니다.
2. **`TO_NUMBER` 단일 매개변수 호출**: 
   * 페이징 조건의 `TO_NUMBER` 호출 부분을 `::numeric` 혹은 `::integer` 명시적 타입 캐스팅으로 개선할 것을 권장합니다.

---

## 9. 종합 판정

| 구분 | 결과 |
|------|------|
| 화면 로딩 | ✅ PASS |
| 공지사항 목록 조회 및 최신 정렬 | ✅ PASS (정렬 패치 완료) |
| 상세 정보 확인 모달 | ✅ PASS |
| 조회수 가산 및 로그 MERGE | ✅ PASS |
| **종합 판정** | **✅ PASS** |

---

## 10. 첨부 (E2E 테스트 캡처화면)
* **공지사항 목록 화면**:
  ![가맹점 공지 목록](file:///D:/hmTest/backoffice/QaReport/st_commu_00001_1_list.png)
* **공지사항 상세 조회 모달 화면**:
  ![가맹점 공지 상세 모달](file:///D:/hmTest/backoffice/QaReport/st_commu_00001_2_detail_modal.png)
