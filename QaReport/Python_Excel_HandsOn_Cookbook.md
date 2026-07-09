# Python 엑셀(Excel) 핸들링 5분 완성 실습북 (Hands-on Cookbook)

본 실습북은 파이썬으로 엑셀 파일을 읽고, 작성하고, 꾸미고, 대량 데이터를 다루는 법을 **단 5분 만에 단계별로 직접 실행하며 학습**할 수 있는 실무 실습 가이드입니다.

실습 준비: 터미널에서 아래 패키지들을 먼저 설치해 줍니다.
```bash
pip install openpyxl pandas
```

---

## 💻 실습 순서 요약

```text
[Step 1] openpyxl로 엑셀 리포트 쓰기 ──► [Step 2] openpyxl로 엑셀 데이터 읽기 ──► [Step 3] pandas로 고속 엑셀 가공 및 저장
```

---

## 1단계 [Step 1]: openpyxl로 디자인된 엑셀 쓰기 (`excel_step1_write.py`)

셀 배경색, 글꼴 굵기, 정렬 및 엑셀 수식을 포함하는 정교한 매출 보고서 엑셀 파일을 생성합니다.

### 1.1 소스코드 작성
아래 코드를 복사하여 **`excel_step1_write.py`** 파일로 저장하세요.
```python
# excel_step1_write.py
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# 1. 신규 워크북 생성 및 활성 시트 가져오기
wb = Workbook()
ws = wb.active
ws.title = "매출현황"

# 2. 데이터 등록
ws.append(["매장코드", "매장명", "금일매출"])  # 헤더행
ws.append(["NC0002", "본사_SHOP", 5200000])
ws.append(["NC0007", "CAFE", 3800000])

# 3. 스타일 지정 (제목 헤더 행 꾸미기)
header_font = Font(name="맑은 고딕", size=11, bold=True, color="FFFFFF")
blue_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
center_align = Alignment(horizontal="center", vertical="center")
thin_border = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC')
)

# A1, B1, C1 헤더 셀 스타일 적용
for col in ["A1", "B1", "C1"]:
    ws[col].font = header_font
    ws[col].fill = blue_fill
    ws[col].alignment = center_align
    ws[col].border = thin_border

# 4. 수식 대입 및 숫자 서식 지정
ws["A4"] = "총 합계"
ws["C4"] = "=SUM(C2:C3)"  # 엑셀 SUM 수식 기입
ws["C4"].font = Font(bold=True)

# 금액 표시 천 단위 콤마 서식
ws["C2"].number_format = '#,##0'
ws["C3"].number_format = '#,##0'
ws["C4"].number_format = '#,##0'

# 5. 열 너비 수동 넓히기
ws.column_dimensions["A"].width = 15
ws.column_dimensions["B"].width = 15
ws.column_dimensions["C"].width = 18

# 6. 파일 저장
wb.save("hms_sales.xlsx")
print("성공: hms_sales.xlsx 파일이 서식 스타일을 포함하여 생성되었습니다!")
```

### 1.2 실행하기
```bash
python excel_step1_write.py
```
* **결과 확인**: 폴더 내에 `hms_sales.xlsx` 파일이 생겼는지 확인하고, 엑셀 프로그램 등으로 열어서 파란색 헤더와 콤마 포맷, 합계 수식이 들어갔는지 확인합니다.

---

## 2단계 [Step 2]: openpyxl로 수식 결과 및 셀 값 읽기 (`excel_step2_read.py`)

기존 엑셀 파일을 읽어오되, 수식(`=SUM(C2:C3)`)이 적힌 셀의 단순 수식 문자열이 아닌 **엑셀 계산 결과 수치값(9000000)**을 정확히 로드해 출력합니다.

### 2.1 소스코드 작성
아래 코드를 복사하여 **`excel_step2_read.py`** 파일로 저장하세요.
```python
# excel_step2_read.py
from openpyxl import load_workbook

# 1. 파일 읽기 (data_only=True로 지정하여 계산 결과 수치를 직접 획득)
wb = load_workbook("hms_sales.xlsx", data_only=True)
ws = wb["매출현황"]

# 2. 특정 셀 값 가져오기
total_sales = ws["C4"].value
print(f"C4 셀의 합계 연산 결과: {total_sales:,}원\n")

# 3. 행별 데이터 순회 출력
print("--- 매장별 개별 매출 데이터 ---")
for r in range(2, ws.max_row + 1):
    store_code = ws.cell(row=r, column=1).value
    store_name = ws.cell(row=r, column=2).value
    sales = ws.cell(row=r, column=3).value
    
    # 총 합계 라인은 필터에서 제외
    if store_code and store_code != "총 합계":
        print(f"매장코드: {store_code} | 매장명: {store_name} | 매출: {sales:,}원")
```

### 2.2 실행하기
```bash
python excel_step2_read.py
```
* **출력 결과 예시**:
  ```text
  C4 셀의 합계 연산 결과: 9,000,000원
  
  --- 매장별 개별 매출 데이터 ---
  매장코드: NC0002 | 매장명: 본사_SHOP | 매출: 5,200,000원
  매장코드: NC0007 | 매장명: CAFE | 매출: 3,800,000원
  ```

---

## 3단계 [Step 3]: pandas로 고속 데이터 로드 및 엑셀 내보내기 (`excel_step3_pandas.py`)

대용량 가공 시 필수적인 `pandas` 라이브러리를 사용해 엑셀을 읽어들이고, 매출이 400만 원 이상인 우수 매장만 필터링해 별도의 엑셀 파일로 출력합니다.

### 3.1 소스코드 작성
아래 코드를 복사하여 **`excel_step3_pandas.py`** 파일로 저장하세요.
```python
# excel_step3_pandas.py
import pandas as pd

# 1. pandas로 엑셀 데이터프레임 고속 로드
df = pd.read_excel("hms_sales.xlsx", sheet_name="매출현황")

# 2. 총 합계 행 제외 (정제)
df = df[df["매장코드"] != "총 합계"]

print("--- Pandas 로드 원본 데이터프레임 ---")
print(df)

# 3. 조건부 필터링: 금일매출이 4,000,000원 이상인 매장 추출
vip_stores = df[df["금일매출"] >= 4000000]

print("\n--- 매출 400만원 이상 필터링 결과 ---")
print(vip_stores)

# 4. 필터링된 결과만 새 엑셀 파일로 출력 내보내기
vip_stores.to_excel("vip_sales_report.xlsx", index=False)
print("\n성공: vip_sales_report.xlsx 파일로 내보내기가 완료되었습니다!")
```

### 3.2 실행하기
```bash
python excel_step3_pandas.py
```
* **결과 확인**: 새 엑셀 파일 `vip_sales_report.xlsx`를 열어보면, 매출 520만 원인 `NC0002` 매장 데이터만 필터링되어 깔끔하게 저장된 것을 볼 수 있습니다.
