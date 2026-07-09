# QA Report: Hq_System_00003 POS 기능 권한 제어
**작성일**: 2026-06-01  
**작성자**: AI QA Agent (Antigravity)  
**대상 화면**: 시스템관리 > POS > POS 기능 권한 제어 (hq_system_00003)  
**테스트 환경**: localhost:8080 (로컬 개발 서버), EPAS DB (192.168.10.206:5432 / edb)  
**접속ID/PW**: shopadmin / 0000  

---

## 1. 분석 개요

본 화면은 특정 매장(NC0007 등) 및 POS 기기별로 사용 가능한 기능(권한)을 제어(체크박스 형태로 On/Off)하고 저장하는 화면입니다.

### 1.1 분석 대상 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| Controller | `.../controller/hq/system/Hq_System_00003_Controller.java` |
| Service | `.../service/hq/system/Hq_System_00003_Service.java` |
| Mapper (Interface) | `.../dao/hq/system/Hq_System_00003_Mapper.java` |
| SQL XML | `.../sqlmapper/system/Hq_System_00003_Sql.xml` |

---

## 2. 발생한 주요 이슈 및 조치 내역 (Critical)

### 🔴 2.1 POS 콤보박스 `undefined` 표출 (LinkedHashMap 대소문자 매핑 이슈)
- **증상**: 브라우저 화면 접속 후 체인과 매장(NC0007)을 선택하면, 세 번째 'POS 선택' 드롭다운 목록에 POS 번호 대신 `undefined` 가 여러 개 노출되는 심각한 프론트엔드 버그 발생.
- **원인**: 
  - 공통 모듈인 `CommonModule_GoodsClass_Sql.xml`의 `selectMemberPosList` 쿼리 반환 타입이 DTO가 아닌 `java.util.LinkedHashMap`입니다.
  - Oracle에서는 컬럼명이 기본 대문자(`POS_NO`)로 Key가 생성되지만, EPAS(PostgreSQL)에서는 별도의 Alias 처리가 없으면 기본 소문자(`pos_no`)로 Key가 생성됩니다.
  - 프론트엔드 JS(`backoffice.module.condition.js`)에서 `value.POS_NO`로 접근하려다 값을 찾지 못해 `undefined`를 반환했습니다.
- **해결 (사용자 분석 일치)**: `SELECT MS_NO AS "MS_NO", POS_NO AS "POS_NO"` 와 같이 쌍따옴표를 씌운 대문자 Alias를 부여하여 EPAS가 강제로 대문자 Key를 생성하도록 조치 완료.

### 🟡 2.2 표준 SQL 문법 전환 (권고사항 적용)
- **수정 내역**: `Hq_System_00003_Sql.xml` 
  - 비록 EPAS 호환 모드가 `(+)` 조인과 `NVL`, `SYSDATE`를 정상 처리하지만, 보다 완벽한 PostgreSQL 표준화를 위해 코드를 마이그레이션 했습니다.
  - `(+)` → `LEFT OUTER JOIN`
  - `NVL(MF.USE_FG,'0') USE_FG` → `COALESCE(MF.USE_FG,'0') AS USE_FG`
  - `SYSDATE` → `NOW()`

---

## 3. 기능 검증 상세 (브라우저 E2E)

### 3.1 조회 (Search)
- **엔드포인트**: `/search`
- **조치 결과**: 콤보박스 픽스 후 매장/POS(예: 01) 선택 후 '조회' 시 에러 없이 기능 목록과 현재 권한 부여 상태(체크박스) 정상 로딩 확인.

### 3.2 저장 (Save: Delete & Insert)
- **엔드포인트**: `/save`
- **로직 흐름**: 
  1. `deleteFunc`: 해당 POS에 부여된 기존 권한(`MPOSFTTB`) 일괄 삭제 (`DELETE`)
  2. `insertFunc`: 체크된 기능에 대해 `USE_FG` 플래그와 함께 재등록 (`INSERT`)
- **조치 결과**: `insertFunc`의 날짜 함수를 `NOW()`로 수정 후 정상적으로 MyBatis 에러 없이 커밋(Commit) 완료됨을 확인.

---

## 4. 종합 판정

| 검증 항목 | 상태 | 비고 |
|----------|------|------|
| 공통 콤보박스 (매장/POS 조회) | ✅ PASS | LinkedHashMap 대소문자 Alias 강제 지정 적용 완료 |
| 데이터 조회 (SELECT) | ✅ PASS | LEFT JOIN 구조로 표준화 후 정상 작동 |
| 권한 저장 로직 (DELETE/INSERT) | ✅ PASS | 트랜잭션 정상 및 데이터베이스 정합성 확인 |

- **종합 결론**: **✅ 완벽 동작 (이슈 해결 완료)**
- 사용자님께서 짚어주신 "리스트 Alias 미존재" 문제가 가장 핵심적인 블로커였으며, 이 부분을 정확히 공략하여 공통 XML을 수정한 결과 연쇄적인 UI 에러를 완벽히 해결하였습니다.
