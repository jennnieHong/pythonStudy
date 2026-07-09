# HMS 지출 및 시재 관리 모듈 데이터 흐름 가이드 (Cash & Expense Data Flow Guide)

**작성일**: 2026-06-29  
**작성자**: AI QA Agent (Antigravity)  

HMS의 현금/시재 관리 체계는 크게 **일반입출금관리(일별 시재)**와 **월간지출관리(월별 지출)**의 두 가지 서브 모듈로 이원화되어 작동하며, 동일한 트랜잭션 테이블(`hmsfns.MACCIOTB`)을 공유하면서도 계정 구분코드(`ACNT_FG`)를 통해 논리적으로 철저히 격리됩니다.

---

## 1. 지출 및 시재 관리 아키텍처 및 데이터 흐름

<div class="mermaid-wrapper" style="position: relative; margin-bottom: 20px;">
  <button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText); alert('Mermaid 코드가 복사되었습니다.');" style="position: absolute; right: 10px; top: 10px; z-index: 100; background: #2563EB; color: white; border: none; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">코드 복사</button>

```text
flowchart TD
    subgraph A. 일반입출금관리 (일별 시재) [ACNT_FG = '0' 입금 / '1' 출금]
        ST_REG_1[매장 입출금 등록<br/>st_cash_00001] -->|CUD| DB_TX_1[(hmsfns.MACCIOTB)]
        DB_TX_1 --> ST_STAT_1[매장 입출금 현황<br/>st_cash_00002]
        DB_TX_1 --> HQ_VIEW_1[본사 계정별 전점현황<br/>hq_cash_00003]
    end

    subgraph B. 월간지출관리 (월별 지출) [ACNT_FG NOT IN ('0', '1') 즉, 2~9 지출코드]
        HQ_M_CUD[본사 지출계정 설정<br/>hq_cash_00004] -->|Level 1 HQ| DB_HQ_M[(TMACNCTB / TMACNTTB)]
        HQ_M_CUD -->|Level 2 Java Trigger| DB_ST_M[(MMACNCTB / MMACNTTB)]
        HQ_M_CUD -->|Level 3 Sync & Log| DB_SYNC[(SSACNCTB / SSACNTTB)]
        HQ_M_CUD -->|Level 3 Audit| DB_AUDIT[(MMSLOGTB)]

        DB_ST_M -->|지출 코드 드롭다운 참조| ST_REG_2[매장 월간지출 등록<br/>st_cash_00004]
        ST_REG_2 -->|CUD| DB_TX_2[(hmsfns.MACCIOTB)]
        DB_TX_2 --> ST_STAT_2[매장 월간지출 조회<br/>st_cash_00003]
        DB_TX_2 --> HQ_VIEW_2[본사 월간지출 현황<br/>hq_cash_00005]
    end
```

```mermaid
flowchart TD
    subgraph A. 일반입출금관리 (일별 시재) [ACNT_FG = '0' 입금 / '1' 출금]
        ST_REG_1[매장 입출금 등록<br/>st_cash_00001] -->|CUD| DB_TX_1[(hmsfns.MACCIOTB)]
        DB_TX_1 --> ST_STAT_1[매장 입출금 현황<br/>st_cash_00002]
        DB_TX_1 --> HQ_VIEW_1[본사 계정별 전점현황<br/>hq_cash_00003]
    end

    subgraph B. 월간지출관리 (월별 지출) [ACNT_FG NOT IN ('0', '1') 즉, 2~9 지출코드]
        HQ_M_CUD[본사 지출계정 설정<br/>hq_cash_00004] -->|Level 1 HQ| DB_HQ_M[(TMACNCTB / TMACNTTB)]
        HQ_M_CUD -->|Level 2 Java Trigger| DB_ST_M[(MMACNCTB / MMACNTTB)]
        HQ_M_CUD -->|Level 3 Sync & Log| DB_SYNC[(SSACNCTB / SSACNTTB)]
        HQ_M_CUD -->|Level 3 Audit| DB_AUDIT[(MMSLOGTB)]

        DB_ST_M -->|지출 코드 드롭다운 참조| ST_REG_2[매장 월간지출 등록<br/>st_cash_00004]
        ST_REG_2 -->|CUD| DB_TX_2[(hmsfns.MACCIOTB)]
        DB_TX_2 --> ST_STAT_2[매장 월간지출 조회<br/>st_cash_00003]
        DB_TX_2 --> HQ_VIEW_2[본사 월간지출 현황<br/>hq_cash_00005]
    end
```
</div>

---

## 2. 모듈별 상세 특징 및 데이터 연계

### 2.1 일반입출금관리 (일별 시재)
* **대상 화면**: `st_cash_00001` (등록), `st_cash_00002` (현황), `hq_cash_00001` (본사 등록), `hq_cash_00002` (매장별 현황), `hq_cash_00003` (계정별 전점현황)
* **계정 구분**: `ACNT_FG`가 항상 `'0'` (입금) 또는 `'1'` (출금)로 고정됩니다.
* **비즈니스 흐름**:
  * 매장 사용자가 매일 발생하는 소액 현금 시재의 입금/출금 실거래 내역을 등록합니다.
  * 프론트엔드 및 백엔드에서 과세 구분 확인 후 **부가세(VAT = 공급가액의 10%)가 자동 산출**되어 거래 테이블(`MACCIOTB`)에 합산 저장됩니다.
  * 매장 및 본사에서는 이 데이터를 일자별 시재 잔액 통계 및 시각화 차트로 실시간 조회합니다.

### 2.2 월간지출관리 (월별 지출)
* **대상 화면**: `hq_cash_00004` (본사 계정관리), `hq_cash_00005` (본사 지출현황), `st_cash_00003` (매장 지출조회), `st_cash_00004` (매장 지출등록)
* **계정 구분**: `ACNT_FG`가 `'0'` 및 `'1'` 이외의 값(`2`~`9` 등 본사에서 추가 정의한 지출 계정 분류, 예: 급여, 수도광열비 등)을 가집니다.
* **비즈니스 흐름**:
  * **본사 통제**: 본사(`hq_cash_00004`)에서 정의한 계정 분류 및 상세 코드가 **Java 트랜잭션 트리거 연쇄(Depth 3)**를 작동시켜 가맹점용 마스터(`MMACNCTB`/`MMACNTTB`) 및 감사 로그(`MMSLOGTB`)로 전파 복제됩니다.
  * **매장 등록**: 매장(`st_cash_00004`)은 복제된 매장용 지출 마스터 테이블 정보를 로드하여 드롭다운을 구성하며, 월 단위 지출 거래액을 등록합니다. (부가세는 기본 `0`으로 처리)
  * **집계 조회**: 매장(`st_cash_00003`) 및 본사(`hq_cash_00005`)에서는 월별로 집계된 가맹점 지출 현황 및 원천 거래 이력을 조회합니다.

---

## 3. 핵심 무결성 및 시스템 제약 조건

1. **테이블 논리 격리 규칙**:
   * 동일한 `MACCIOTB` 테이블을 활용하지만, 일반 시재 조회 쿼리는 `ACNT_FG IN ('0','1')` 조건을, 월간 지출 조회 쿼리는 `ACNT_FG NOT IN ('0','1')` 조건을 적용하여 연산 대상 데이터를 엄격히 분리합니다.
2. **참조 무결성 (Foreign Key & Delete Cascades)**:
   * 본사 월간지출계정관리(`hq_cash_00004`)에서 분류 코드 삭제 시, 해당 분류에 매핑된 하위 상세 코드가 존재하면 데이터 무결성을 보호하기 위해 삭제가 예외 차단됩니다. 상세 코드가 모두 소거된 후에만 분류 코드가 삭제됩니다.
3. **가맹점 데이터 접근 통제**:
   * 매장 단위 화면(`st_cash_*`)은 사용자 세션의 매장코드(`msNo`) 필터링을 통해 격리된 범위만 DML/SELECT를 수행할 수 있으며, 본사 화면(`hq_cash_*`)은 소속 체인코드(`chainNo = 'C001'`) 기준 전 매장의 데이터를 집계 제어합니다.
