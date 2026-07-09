# Trigger Detail: Hq_System_00004 VAN사 정보 설정 트리거 연쇄 및 동기화 상세 분석

본 화면(`hq_system_00004`) 및 매장 계약 매핑 화면(`hq_master_00004`)에서 연동되는 데이터베이스 테이블들은 **본사 웹 시스템(백오피스)과 실시간 매장 POS 단말기 간의 데이터 동기화**를 안정적으로 처리하기 위해 유기적으로 설계되어 있습니다.

---

## 1. 관련 테이블 정의 및 도입 목적 (왜 사용하는가?)

| 테이블명 | 테이블 한글명 | 역할 및 목적 (정의) | 도입 목적 및 사용 이유 (Why) |
|---|---|---|---|
| **`VANMSTTB`** | VAN사 정보 마스터 | 전 가맹점이 공통으로 사용하는 카드/현금영수증 결제 중계 대행업체(VAN사)의 전역 서버 설정 정보 테이블 | 매장 POS 단말기가 결제 승인을 요청할 중계 서버의 **IP 주소, PORT 번호, VAN사 명칭** 등을 본사에서 중앙 집중식으로 제어하기 위해 사용합니다. |
| **`MVANCOTB`** | 매장별 VAN사 계약/매핑 | 특정 매장(`MS_NO`)의 개별 POS 단말기(`POS_NO`) 단위로 어떤 VAN사와 계약을 맺고 어떤 가맹점번호(TID - `CAT_ID`)를 사용하는지 연결해 주는 테이블 | 매장별, 혹은 POS 기기별로 승인용 TID가 다르고 계약된 대행업체가 다르기 때문에, **각 단말기 기기별 1:1 맞춤형 VAN사 계약 관계**를 정의하고 저장하기 위해 사용합니다. |
| **`SVANCOTB`** | 매장별 VAN사 설정 동기화 | 매장별 POS 단말기로 전송할 설정 상태의 **변경 이력 및 전송 대기 큐(Queue)** 역할을 하는 테이블 | 웹에서 변경된 설정이 네트워크 단절, POS 꺼짐 등의 이유로 POS 기기에 즉시 반영되지 못할 수 있으므로, 변경 이력을 일련번호(`LOG_SEQ`)와 상태값(`proc_fg`)으로 쌓아두고 **POS 기기가 켜질 때/주기적으로 서버에 API를 찔러 최신 설정을 내려받기 위한 완충 버퍼**로 사용합니다. |
| **`MMSLOGTB`** | 시스템 감사 로그 | 데이터의 등록(`A`), 수정(`U`), 삭제(`D`) 시 구체적으로 어떤 세부 컬럼이 어떻게 변경되었는지 기록하는 공통 이력 테이블 | 데이터에 오류가 생기거나 누군가 임의로 연동 설정을 조작했을 때, **어느 사용자(USER_ID)가 언제 어떤 기존값에서 어떤 변경값으로 바꿨는지 추적 및 역추적(Audit)**하기 위한 증적 확보용으로 사용합니다. |

---

## 2. 트리거 작동 및 SVANCOTB 삽입을 위한 5가지 세부 조건

`Tr_VANMST_T01_Service` 트리거 로직 상, `SVANCOTB`에 동기화 레코드가 연쇄 삽입되기 위해서는 다음 **5단계 세부 조건**이 모두 만족되어야 합니다.

1. **DML 작업 구분 체크 (Java Service)**
   - 오직 수정(`UPDATE`) 작업일 때만 작동합니다. (신규 등록이나 삭제 시에는 동기화하지 않고 바로 로깅 단계로 이동)
2. **실제 연동값 변경 확인 (Java Service)**
   - `VAN_CD`, `VAN_FG`, `VAN_IP`, `VAN_PORT_NO`, `VAN_NAME` 필드 중 하나라도 기존값과 달라진 필드가 존재해야 합니다. (모든 값이 동일하면 트리거 서비스는 그 즉시 종료됩니다)
3. **주(Primary) VAN사 계약 매핑 확인 (SQL Join - MVANCOTB)**
   - `MVANCOTB` 테이블에서 변경된 VAN사 코드를 **주 VAN사(`VAN_CD`)**로 설정하여 계약을 맺고 있는 매장을 선별합니다.
4. **부(Secondary) VAN사 계약 매핑 확인 (SQL Join - MVANCOTB)**
   - 또는, `MVANCOTB` 테이블에서 해당 VAN사 코드를 **서브 VAN사(`SUB_VAN_CD`)**로 설정하여 부가 계약을 맺고 있는 매장도 함께 선별합니다.
5. **기존 전송 이력 매칭 검증 (SQL Join - SVANCOTB)**
   - 3~4단계에서 선별된 매장들 중, **`SVANCOTB`에 기존 전송 이력(기존에 발급받은 `LOG_SEQ` 데이터)이 이미 존재하는 매장**만 최종 삽입 대상이 됩니다.
   - *이유: 트리거 SQL문 내부적으로 기존 최신 설정 레코드를 `SELECT`하여 가져온 뒤, 바뀐 마스터 정보(IP, Port 등)만 덮어써서 새로운 `LOG_SEQ`로 `INSERT`하기 때문입니다.*

---

## 2. 화면별 트리거 작동 시나리오 및 구체적 조작 가이드

### 💡 시나리오 A: 최초 매장별 VAN사 계약 등록 시 (신규 동기화 데이터 생성)
* **조작 화면**: 본사시스템 > 가맹점관리 > **매장 등록관리** ([hq_master_00004](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/master/hq_master_00004/hq_master_00004.jsp))
* **조작 방법**:
  1. 매장 목록에서 동기화 대상 매장(예: `NC0018`)을 검색하여 선택합니다.
  2. 우측 상단 또는 상세 영역의 **[계약번호 등록]** 버튼을 클릭하여 모달을 엽니다.
  3. 등록하고자 하는 VAN사(예: `KSNET` 등)를 선택하고 가맹점번호(TID), 단말기구분 등의 정보를 입력한 뒤 **저장**합니다.
* **트리거 동작**:
  - `MVANCOTB` 테이블에 매핑 데이터가 추가(`INSERT`) 또는 변경(`UPDATE`)됩니다.
  - 이 시점에 `Tr_MVANCO_T01` 트리거가 실행되어, 해당 VAN사의 세부 정보(IP, Port, Name 등)를 `VANMSTTB` 마스터에서 조회해 온 뒤, `SVANCOTB`에 최초 동기화 레코드(`proc_fg = 'A'`)를 생성합니다.

### 💡 시나리오 B: 기존 VAN사의 네트워크/연동 정보 변경 시 (매핑된 매장 일괄 동기화 업데이트)
* **조작 화면**: 본사시스템 > 기초코드관리 > **VAN사 정보 설정** ([hq_system_00004](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/system/hq_system_00004/hq_system_00004.jsp))
* **조작 방법**:
  1. 조회된 VAN사 목록에서 수정하고자 하는 VAN사(예: `KSNET`)를 더블클릭하거나 선택합니다.
  2. IP, PORT 번호 또는 VAN사 명칭을 변경합니다.
  3. **저장** 버튼을 누릅니다.
* **트리거 동작**:
  - `VANMSTTB` 마스터 테이블에 `UPDATE`가 일어납니다.
  - 이 시점에 `Tr_VANMST_T01` 트리거가 실행되어, **시나리오 A를 통해 이 VAN사에 현재 매핑되어 있는 모든 매장 정보(MVANCOTB)**를 찾습니다.
  - 매핑된 각 매장에 대해 새로 변경된 IP/Port 설정값으로 `SVANCOTB`에 동기화 레코드(`proc_fg = 'U'`)를 일괄 생성합니다.

### 💡 시나리오 C: 신규 VAN사 최초 등록 시 (동기화 레코드 생성 없음)
* **조작 화면**: 본사시스템 > 기초코드관리 > **VAN사 정보 설정** ([hq_system_00004](file:///d:/workspace/hmotors/workspace_hms20260326/backoffice/hyundai-backoffice-webapp/src/main/webapp/WEB-INF/views/backoffice/main/contents/hq/system/hq_system_00004/hq_system_00004.jsp))
* **조작 방법**:
  1. **[추가]** 또는 등록 폼에서 새로운 VAN사 코드와 명칭, IP, PORT를 입력하고 **저장**합니다.
* **트리거 동작**:
  - `VANMSTTB` 마스터 테이블에 `INSERT`가 일어납니다.
  - 트리거(`Tr_VANMST_T01`)가 동작하지만, **아직 이 신규 VAN사에 매핑된 매장이 존재하지 않기 때문에** `SVANCOTB`에는 연쇄 전송 데이터가 작성되지 않습니다. (이후 시나리오 A를 통해 매장 등록관리 화면에서 매핑을 잡는 순간 데이터가 생성됩니다)
