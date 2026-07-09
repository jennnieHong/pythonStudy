# HMS 개발자를 위한 Python 엑셀(Excel) 핸들링 실무 가이드

본 가이드는 백오피스 업무 자동화, 배치 정산 가공, 엑셀 업로드/다운로드 스크립트 작성 시 파이썬을 활용하여 엑셀 파일(`.xlsx`)을 다루는 핵심 표준 라이브러리(`openpyxl`, `pandas`)의 실무 활용법을 정리한 가이드입니다.

---

## 1. 엑셀 핸들링 핵심 라이브러리 요약

파이썬에서 엑셀을 제어하는 도구는 크게 두 가지 영역으로 나뉩니다.

1. **`openpyxl` (디테일한 셀 제어 및 서식 지정)**:
   * 특정 셀의 폰트, 테두리, 배경색 지정 등 **시각적 스타일 지정**이 필요할 때 적합.
   * 엑셀 수식 작성, 셀 병합, 이미지 삽입 및 시트 구조 추가/삭제 가능.
2. **`pandas` (대용량 데이터 수집 및 연산)**:
   * 엑셀 시트에 채워진 수만 행의 로우 데이터를 단 몇 줄로 읽어 **데이터 정제/필터링/DB 적재**할 때 최상의 속도 발휘.

---

## 2. openpyxl을 이용한 상세 엑셀 조작

먼저 설치 커맨드는 다음과 같습니다.
```bash
pip install openpyxl
```

### 2.1 엑셀 파일 신규 생성 및 쓰기 (Write)
```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

# 1. 워크북 및 활성 시트 선언
wb = Workbook()
ws = wb.active
ws.title = "매출정산"

# 2. 기본 데이터 셀 대입
ws["A1"] = "매장코드"
ws["B1"] = "매장명"
ws["C1"] = "금일매출"

# 3. 행(Row) 단위로 한꺼번에 데이터 추가
ws.append(["NC0002", "본사_SHOP", 5200000])
ws.append(["NC0007", "CAFE", 3800000])

# 4. 스타일 지정 (제목행 서식)
bold_font = Font(name="맑은 고딕", size=11, bold=True, color="FFFFFF")
blue_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
center_align = Alignment(horizontal="center", vertical="center")

# 테두리 스타일 설정
thin_border = Border(
    left=Side(style='thin', color='D3D3D3'),
    right=Side(style='thin', color='D3D3D3'),
    top=Side(style='thin', color='D3D3D3'),
    bottom=Side(style='thin', color='D3D3D3')
)

for col in ["A1", "B1", "C1"]:
    ws[col].font = bold_font
    ws[col].fill = blue_fill
    ws[col].alignment = center_align
    ws[col].border = thin_border

# 5. 수식(Formula) 적용 및 셀 서식 (천 단위 표시)
ws["A4"] = "합계"
ws["C4"] = "=SUM(C2:C3)"  # 엑셀 기본 SUM 수식 적용
ws["C4"].font = Font(bold=True)
ws["C2"].number_format = '#,##0'
ws["C3"].number_format = '#,##0'
ws["C4"].number_format = '#,##0'

# 6. 파일 저장
wb.save("HMS_Sales_Report.xlsx")
```

### 2.2 기존 엑셀 파일 읽기 (Read)
```python
from openpyxl import load_workbook

# 1. 파일 로드
wb = load_workbook("HMS_Sales_Report.xlsx", data_only=True) 
# data_only=True로 설정해야 수식이 걸린 셀의 연산 결과값을 직접 읽어옵니다. (False 지정 시 "=SUM(C2:C3)" 문자열 자체를 읽음)

ws = wb["매출정산"]

# 2. 특정 셀 값 개별 읽기
print("A2 셀 값:", ws["A2"].value) # NC0002
print("C4 (합계) 결과값:", ws["C4"].value) # 9000000

# 3. 전체 시트 영역 루프 순회
for r in range(2, ws.max_row + 1):
    store_code = ws.cell(row=r, column=1).value
    store_name = ws.cell(row=r, column=2).value
    sales = ws.cell(row=r, column=3).value
    if store_code:
        print(f"[{store_code}] {store_name} -> 매출: {sales:,}원")
```

---

## 3. pandas를 이용한 고속 데이터 분석 및 연동

대량의 엑셀 파일을 가공하여 DB에 집계 적재해야 하거나, DB의 수십만 개 레코드를 엑셀로 한 번에 추출할 때 강점을 보입니다.
```bash
pip install pandas openpyxl
```

### 3.1 엑셀을 DataFrame으로 고속 로드하여 정제하기
```python
import pandas as pd

# 1. 엑셀 읽기 (첫 행을 컬럼 헤더로 자동 빌드)
df = pd.read_excel("HMS_Sales_Report.xlsx", sheet_name="매출정산")

# 2. 데이터 가공 및 필터링
# 금일매출이 4,000,000원 이상인 매장만 필터링
high_sales_df = df[df["금일매출"] >= 4000000]

print("--- 우수 매출 매장 필터링 결과 ---")
print(high_sales_df)
```

### 3.2 Pandas를 이용한 초고속 엑셀 내보내기 (Export)
```python
import pandas as pd

# 1. 적재할 데이터 딕셔너리 생성
data = {
    "매장코드": ["NC0002", "NC0007", "NC0005"],
    "매장명": ["본사_SHOP", "CAFE", "NC_DELI"],
    "금일매출": [5200000, 3800000, 2400000]
}

# 2. DataFrame 생성
df_new = pd.DataFrame(data)

# 3. 엑셀 파일로 바로 출력 세이브 (인덱스 열 제외)
df_new.to_excel("HMS_Bulk_Export.xlsx", index=False)
print("엑셀 벌크 저장 완료.")
```

---

## 4. 실무 응용 시나리오 (엑셀 데이터를 읽어 EDB DB 적재하기)

가맹점주가 엑셀 정산 파일을 업로드했을 때, 파이썬 배치 백엔드가 이를 파싱하여 데이터베이스에 일관 트랜잭션으로 적재하는 가장 표준적인 예제 코드입니다.

```python
import os
import pandas as pd
import psycopg2

def upload_excel_to_db(file_path):
    # 1. 파일 존재 여부 검사
    if not os.path.exists(file_path):
        print(f"오류: {file_path} 파일이 존재하지 않습니다.")
        return

    # 2. Pandas로 엑셀 데이터프레임 로드
    try:
        df = pd.read_excel(file_path, sheet_name=0) # 0번 첫번째 시트 읽기
    except Exception as e:
        print(f"엑셀 읽기 실패: {e}")
        return

    # 3. 데이터 적재 정보 가공 (튜플 리스트화)
    # 데이터프레임의 행들을 순회하여 튜플 형태로 수집
    insert_rows = []
    for index, row in df.iterrows():
        # 엑셀 헤더명: 매장코드, 매장명, 금일매출
        store_code = str(row["매장코드"]).strip()
        sales_amt = int(row["금일매출"])
        
        # 합계 등 데이터 정제 대상은 거름
        if store_code and store_code != "합계":
            insert_rows.append((store_code, sales_amt))

    # 4. EDB DB 적재 실행
    conn = None
    try:
        conn = psycopg2.connect(
            host="192.168.10.206",
            database="edb",
            user="hmsfns_was",
            password="YOUR_PASSWORD",
            port="5432"
        )
        cursor = conn.cursor()
        
        # executemany를 활용한 벌크 인서트
        query = """
            INSERT INTO hmsfns.SDAILYTB (MS_NO, SALE_AMT, SALE_DATE) 
            VALUES (%s, %s, TO_CHAR(SYSDATE, 'YYYYMMDD'))
        """
        cursor.executemany(query, insert_rows)
        
        # 트랜잭션 정상 커밋
        conn.commit()
        print(f"성공: {len(insert_rows)}건의 매출 데이터가 DB에 정상 적재되었습니다.")
        cursor.close()
    except Exception as db_err:
        if conn:
            conn.rollback()
        print("데이터베이스 적재 에러 롤백 감행:", db_err)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    upload_excel_to_db("HMS_Sales_Report.xlsx")
```
