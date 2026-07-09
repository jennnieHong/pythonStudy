# SAREGITB (POS 정산 테이블) 데이터 수집 및 소모 흐름 가이드

본 문서는 매장의 실물 POS(Point of Sale) 단말기에서 발생한 마감 정산 데이터가 서버 데이터베이스의 `SAREGITB` 테이블에 **적재(Ingestion)**되고, 이를 웹 백오피스 및 외부 시스템 연동 과정에서 어떻게 **소모(Consumption)**하는지 그 데이터 흐름을 상세하게 기술합니다.

---

## 1. SAREGITB 테이블 개요

`hmsfns.SAREGITB`는 각 매장별/POS별 일일 영업 마감 시점에 정산된 원장 데이터를 누적 관리하는 테이블입니다.

### 1.1 주요 핵심 컬럼

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `SALE_DATE` | `VARCHAR(8)` | **[PK]** 영업 일자 (YYYYMMDD) |
| `MS_NO` | `VARCHAR(10)` | **[PK]** 매장 코드 |
| `POS_NO` | `VARCHAR(2)` | **[PK]** POS 단말기 번호 |
| `REGI_TYPE` | `VARCHAR(1)` | **[PK]** 정산 종류 (예: `0` - 일마감 정산) |
| `BILL_NO` | `VARCHAR(4)` | 마감 영수증 번호 (0001 ~ 9999) |
| `SALE_TOT` | `NUMERIC(12,0)` | 총 매출액 |
| `SALE_AMT` | `NUMERIC(12,0)` | 순 매출액 |
| `ADDED_TAX` | `NUMERIC(12,0)` | 부가세액 |
| `CASH_AMT` | `NUMERIC(12,0)` | 현금 매출액 |
| `CARD_AMT1` ~ `CARD_AMT4` | `NUMERIC(12,0)` | 카드사별/승인수단별 카드 매출 및 취소액 |
| `DC_AMT` | `NUMERIC(12,0)` | 총 할인 금액 |
| `CANCEL_TOT` | `NUMERIC(12,0)` | 반품(취소) 총액 |
| `CLOSE_STOCK` | `NUMERIC(12,0)` | 마감 현금 시재금 |
| `CASH_LOSS` | `NUMERIC(12,0)` | 현금 과부족(시재 차이) |

---

## 2. 전체 데이터 흐름도 (Data Life Cycle)

<div class="mermaid-wrapper" style="position: relative; margin-bottom: 20px;">
  <button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText); alert('Mermaid 코드가 복사되었습니다.');" style="position: absolute; right: 10px; top: 10px; z-index: 100; background: #2563EB; color: white; border: none; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">코드 복사</button>

```text
graph TD
    %% 데이터 적재 단계
    subgraph Ingestion [1. 데이터 적재 단계]
        POS[매장 실물 POS 단말기] -->|1. 일영업 종료 후 마감 정산 실행| IF[POS 마감 수집 인터페이스 Agent]
        IF -->|2. TCP/IP 소켓 또는 API 통신| IngestAPI[인터페이스 파싱 및 수집 서버]
        IngestAPI -->|3. INSERT INTO SAREGITB| DB[(EDB / PostgreSQL Database)]
    end

    %% 데이터 소모 단계 (백오피스)
    subgraph Backoffice [2. 웹 백오피스 소모 단계 (SELECT)]
        DB -->|SELECT /searchRegiList| Admin[어드민 POS 정산내역 <br> admin_sales_00005]
        DB -->|SELECT /searchList| Hq[본사 POS 정산내역 <br> hq_sales_00021]
        DB -->|SELECT /searchList| Store[매장 POS 정산내역 <br> st_sales_00021]
    end

    %% 데이터 소모 단계 (외부 연동)
    subgraph Interface [3. 외부 시스템 연동 소모 단계]
        DB -->|SELECT hmsfns.SAREGITB| Proc[DB 프로시저 <br> SUB_IF_HYDM_SEND_P]
        DB -->|SELECT via Hq_Sysif_00001_Sql| Sysif[대외 연동 인터페이스 모듈]
        Proc -->|배치 전송| ExtSystem[그룹사 / 백화점 정산 시스템]
        Sysif -->|대외 전송| CardVAN[외부 카드사 / VAN 연동망]
    end

    classDef ingest fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef backoffice fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    classDef interface fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    
    class POS,IF,IngestAPI,Ingestion ingest;
    class Admin,Hq,Store,Backoffice backoffice;
    class Proc,Sysif,ExtSystem,CardVAN,Interface interface;
```

```mermaid
graph TD
    %% 데이터 적재 단계
    subgraph Ingestion [1. 데이터 적재 단계]
        POS[매장 실물 POS 단말기] -->|1. 일영업 종료 후 마감 정산 실행| IF[POS 마감 수집 인터페이스 Agent]
        IF -->|2. TCP/IP 소켓 또는 API 통신| IngestAPI[인터페이스 파싱 및 수집 서버]
        IngestAPI -->|3. INSERT INTO SAREGITB| DB[(EDB / PostgreSQL Database)]
    end

    %% 데이터 소모 단계 (백오피스)
    subgraph Backoffice [2. 웹 백오피스 소모 단계 (SELECT)]
        DB -->|SELECT /searchRegiList| Admin[어드민 POS 정산내역 <br> admin_sales_00005]
        DB -->|SELECT /searchList| Hq[본사 POS 정산내역 <br> hq_sales_00021]
        DB -->|SELECT /searchList| Store[매장 POS 정산내역 <br> st_sales_00021]
    end

    %% 데이터 소모 단계 (외부 연동)
    subgraph Interface [3. 외부 시스템 연동 소모 단계]
        DB -->|SELECT hmsfns.SAREGITB| Proc[DB 프로시저 <br> SUB_IF_HYDM_SEND_P]
        DB -->|SELECT via Hq_Sysif_00001_Sql| Sysif[대외 연동 인터페이스 모듈]
        Proc -->|배치 전송| ExtSystem[그룹사 / 백화점 정산 시스템]
        Sysif -->|대외 전송| CardVAN[외부 카드사 / VAN 연동망]
    end

    classDef ingest fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef backoffice fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    classDef interface fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    
    class POS,IF,IngestAPI,Ingestion ingest;
    class Admin,Hq,Store,Backoffice backoffice;
    class Proc,Sysif,ExtSystem,CardVAN,Interface interface;
```
</div>

---

## 3. 세부 단계별 흐름 분석

### 3.1 적재 (Ingestion) 단계
1. **영업 마감**: 가맹점에서 하루 영업을 종료한 뒤 POS 단말기에서 **"일마감 정산"**을 최종 진행합니다.
2. **원장 생성**: POS 단말기는 당일 결제 정보들을 집계하여 1건의 마감 정산 원장(영수증 건수, 결제수단별 합계, 마감 시재 등)을 파일 또는 메모리에 빌드합니다.
3. **인터페이스 전송**: POS 내부에 탑재된 통신 Agent가 해당 마감 원장을 본사 수집 서버로 전송합니다.
4. **DB 적재**: 수집 서버는 수신한 원장 JSON/전문 데이터를 파싱하여 DB의 `hmsfns.SAREGITB` 테이블에 `INSERT` 쿼리를 수행합니다.
   * **특징**: 이 과정은 백오피스 웹 페이지의 등록 화면을 거치지 않으며, 백오피스 자바 소스코드 내에는 해당 테이블을 `INSERT` 하거나 `UPDATE` 하는 CUD 로직이 존재하지 않습니다 (B2B POS 전송 전용 데이터).

---

### 3.2 백오피스 소모 (Web Consumption) 단계
적재된 정산 데이터는 점주, 본사 관리자, 시스템 관리자의 대사(대조 검증) 작업을 위해 사용되며, 모두 **단순 조회(SELECT)** 전용으로 소비됩니다.

* **어드민 POS 정산내역 (`admin_sales_00005`)**
  * 시스템 관리자가 특정 일자(`searchDate`)에 정산된 전체 매장의 POS별 정산 요약을 일괄 모니터링합니다.
* **본사 POS 정산내역 (`hq_sales_00021`)**
  * 본사 관리자가 소속 체인의 매장별 정산 데이터를 비교 분석합니다.
* **매장 POS 정산내역 (`st_sales_00021`)**
  * 가맹점 점주가 자기 매장의 POS 장비별 정산 시재금액 및 과부족(시재 차이)을 조회하여 일일 정산 마무리를 확인합니다.

---

### 3.3 대외/외부 연동 소모 (External Consumption) 단계
본사로 수집된 각 가맹점의 정산 원장은 정기적인 배치 작업을 통해 타 시스템으로 이관 및 전송됩니다.

1. **DB 프로시저 호출 (`SUB_IF_HYDM_SEND_P`)**
   * 매장의 정산 내역이 최종 확정되면 배치 스케줄러가 `SUB_IF_HYDM_SEND_P` 프로시저를 실행합니다.
   * 이 프로시저는 `SAREGITB` 테이블로부터 매출 및 정산 내역을 SELECT 한 후, 정해진 인터페이스 규격에 맞춰 현대백화점/그룹사 기간계 정산 시스템으로 데이터를 송신(SEND)하기 위한 인터페이스 임시 테이블에 적재합니다.
2. **대외 인터페이스 모듈 (`Hq_Sysif_00001_Sql.xml`)**
   * 정산 내역을 바탕으로 카드사 대사 데이터 혹은 모바일 머니, 블루포인트 정산 등을 처리하기 위해 `SAREGITB`를 참조하여 연동 파일 및 전문을 생성하는 데 사용됩니다.

---

## 4. 데이터 흐름 무결성 관리 규칙
* **`REGI_TYPE = '0'` 필터링**:
  * POS 정산 상세내역을 조회할 때(`searchRegiDetailList`) 항상 `REGI_TYPE = '0'` 조건으로 필터링합니다. 이는 중간 정산(교대 마감 등) 이력을 제외한 **최종 일마감 정산 원장**만 정확하게 추출하기 위한 규칙입니다.
* **영수증 일관성**:
  * 테이블의 `BILL_NO`는 당일 정산 시 발행된 마감 영수증 번호이며, 매출 내역 테이블(`SADAYLTB` 등)과 영수증 번호 수준에서 크로스 체크를 진행하여 매출 정합성을 대조하는 기준 키 역할을 수행합니다.
