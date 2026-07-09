# Python 엑셀(Excel) 핸들링 실전 연습 문제집

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"Excel"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py Excel Q1 True` (Q1 문제를 완료로 변경)


본 문제집은 파이썬을 활용해 엑셀 파일을 읽고 쓰고 제어하며, 스타일을 가공하고 데이터베이스와 연동하는 실무 역량을 점검하기 위한 기초-중급-심화 연습 문제입니다. 각 문항 하단의 **정답 보기**를 통해 정답 코드를 확인할 수 있습니다.

---

## 목차
1. [기초 문제 (Q1 ~ Q15): openpyxl & pandas 입출력 기본](#basic)
2. [중급 문제 (Q16 ~ Q30): 셀 서식 스타일링, 병합, 수식 및 시트 조작](#intermediate)
3. [심화 문제 (Q31 ~ Q45): 멀티시트, 대용량 데이터 가공, DB 벌크 연동 및 검증](#advanced)

---

<a name="basic"></a>
## 1. 기초 문제 (Q1 ~ Q15): openpyxl & pandas 입출력 기본

### Q1. openpyxl 워크북 생성
메모리에 새로운 빈 엑셀 워크북(Workbook) 객체를 생성하고 활성 시트를 가져오는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from openpyxl import Workbook
wb = Workbook()
ws = wb.active
print(ws.title) # 기본 시트명인 'Sheet' 출력</pre>
</details>

### Q2. 시트 타이틀 이름 변경
활성화된 기본 시트의 이름을 `"매출통계"`로 변경하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws.title = "매출통계"</pre>
</details>

### Q3. 단일 셀에 값 기록하기
A1 셀에 `"매장코드"`, B1 셀에 `"매장명"` 문자열을 각각 대입하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws["A1"] = "매장코드"
ws["B1"] = "매장명"
# 또는
ws.cell(row=1, column=1, value="매장코드")
ws.cell(row=1, column=2, value="매장명")</pre>
</details>

### Q4. 행(Row) 단위 데이터 추가 (append)
리스트 `data = ["NC0007", "CAFE", 3800000]`를 시트의 다음 비어있는 행에 자동으로 덧붙여 쓰는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws.append(["NC0007", "CAFE", 3800000])</pre>
</details>

### Q5. 엑셀 파일 저장하기 (save)
작성 중인 워크북을 현재 경로에 `"sales_report.xlsx"` 파일명으로 디스크에 저장하고 닫으세요.

<details><summary><b>정답 보기</b></summary>
<pre>wb.save("sales_report.xlsx")</pre>
</details>

### Q6. 기존 엑셀 파일 로드 (load_workbook)
디스크의 `"sales_report.xlsx"` 파일을 가져오는 코드를 작성하세요. (단, 수식 결과값을 문자열이 아닌 연산 결과 수치로 가져오게 하세요.)

<details><summary><b>정답 보기</b></summary>
<pre>from openpyxl import load_workbook
wb = load_workbook("sales_report.xlsx", data_only=True)</pre>
</details>

### Q7. 특정 시트 선택하기
Q6에서 불러온 워크북에서 `"매출통계"` 시트를 가져와 변수 `ws`에 대입하세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws = wb["매출통계"]</pre>
</details>

### Q8. 셀 값 읽어와 출력하기
`ws` 시트의 A2 셀에 들어있는 값을 읽어 출력하는 코드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>val = ws["A2"].value
print(val)</pre>
</details>

### Q9. 최대 행 및 최대 열 크기 확인
현재 시트에 데이터가 입력되어 있는 최대 행(Row) 수와 최대 열(Column) 수를 구하는 시트 속성을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>print("최대 행:", ws.max_row)
print("최대 열:", ws.max_column)</pre>
</details>

### Q10. range 범위를 이용한 특정 영역 순회
A1부터 C3 영역에 해당하는 셀들을 이중 for문으로 순회하며 각 셀의 값을 출력하는 코드를 작성하세요. (행: 1~3, 열: 1~3)

<details><summary><b>정답 보기</b></summary>
<pre>for r in range(1, 4):
    for c in range(1, 4):
        print(ws.cell(row=r, column=c).value, end=" ")
    print()</pre>
</details>

### Q11. Pandas를 이용한 엑셀 파일 읽기 (read_excel)
Pandas 라이브러리를 임포트하여 `"sales_report.xlsx"`를 읽어 데이터프레임 `df`로 변환하는 한 줄 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import pandas as pd
df = pd.read_excel("sales_report.xlsx")
print(df.head())</pre>
</details>

### Q12. Pandas 엑셀 내보내기 (to_excel)
딕셔너리 데이터를 기반으로 데이터프레임을 만들고 `"export_output.xlsx"`로 내보내되, 인덱스 열(0, 1, 2...)은 출력에서 제외하고 저장하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import pandas as pd
data = {"이름": ["김", "이"], "부서": ["영업", "마케팅"]}
df = pd.DataFrame(data)
df.to_excel("export_output.xlsx", index=False)</pre>
</details>

### Q13. 특정 열 데이터만 추출 (Pandas)
Q11의 데이터프레임 `df`에서 `"금일매출"` 열만 선택하여 시리즈(Series) 객체로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>sales_col = df["금일매출"]
print(sales_col)</pre>
</details>

### Q14. 엑셀 특정 열의 기술 통계량 요약
Pandas 데이터프레임 `df`에서 수치형 데이터가 들어있는 전체 데이터프레임의 합계, 평균, 최댓값 등을 요약해서 보여주는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(df.describe())</pre>
</details>

### Q15. 시트 이름 전체 확인 (sheetnames)
`load_workbook`으로 연 `wb` 인스턴스에 포함된 모든 시트 이름 목록을 리스트로 확인하는 속성을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(wb.sheetnames) # 예: ['매출통계', 'Sheet2']</pre>
</details>

---

<a name="intermediate"></a>
## 2. 중급 문제 (Q16 ~ Q30): 셀 서식 스타일링, 병합, 수식 및 시트 조작

### Q16. 폰트(Font) 스타일 적용
A1 셀의 글꼴을 `"맑은 고딕"`, 크기 `12`, 진하게(`bold`), 글자색 흰색(`FFFFFF`)으로 설정하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from openpyxl.styles import Font
ws["A1"].font = Font(name="맑은 고딕", size=12, bold=True, color="FFFFFF")</pre>
</details>

### Q17. 셀 배경색(Fill) 칠하기
A1 셀의 배경색을 진한 파란색(Hex코드: `1F4E78`)의 솔리드 패턴으로 채우는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from openpyxl.styles import PatternFill
ws["A1"].fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")</pre>
</details>

### Q18. 정렬(Alignment) 지정
A1 셀의 텍스트가 가로 및 세로 기준 모두 정중앙에 정렬되도록 지정하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from openpyxl.styles import Alignment
ws["A1"].alignment = Alignment(horizontal="center", vertical="center")</pre>
</details>

### Q19. 테두리(Border) 스타일 선언
Side 객체와 Border 객체를 활용해 A1 셀의 상하좌우에 얇은 실선(색상 `D3D3D3`) 테두리를 그리는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from openpyxl.styles import Border, Side
thin = Side(border_style="thin", color="D3D3D3")
ws["A1"].border = Border(left=thin, right=thin, top=thin, bottom=thin)</pre>
</details>

### Q20. 셀 병합 (Merge Cells)
A1부터 C1까지의 셀을 하나로 병합하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws.merge_cells("A1:C1")</pre>
</details>

### Q21. 병합된 셀에 값 대입하기
병합된 셀 `"A1:C1"` 영역에 타이틀 문자열 `"2026년 정산 리포트"`를 올바르게 적용하여 대입하는 기준 셀 위치와 문법을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 셀이 병합된 경우, 반드시 병합 영역의 좌측 최상단 셀(A1)에 값을 대입해야 엑셀에서 올바르게 노출됩니다.
ws["A1"] = "2026년 정산 리포트"</pre>
</details>

### Q22. 셀 병합 해제 (Unmerge Cells)
병합되어 있던 `"A1:C1"` 셀 병합을 다시 원상 복구 해제하는 메소드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws.unmerge_cells("A1:C1")</pre>
</details>

### Q23. 열 너비 자동/수동 조절
A열의 열 너비(Width)를 `20`으로 넓혀서 텍스트 잘림을 예방하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws.column_dimensions["A"].width = 20</pre>
</details>

### Q24. 행 높이 조절
1행의 높이(Height)를 `30`으로 조절하는 코드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws.row_dimensions[1].height = 30</pre>
</details>

### Q25. 엑셀 기본 수식(Formula) 기재
C5 셀에 C2부터 C4까지의 합계를 연산하는 엑셀 SUM 함수 수식 텍스트를 기재하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws["C5"] = "=SUM(C2:C4)"</pre>
</details>

### Q26. 천 단위 콤마 넘버 포맷 지정
C2 셀의 수치 출력 서식을 1,000 단위마다 콤마가 붙고 소수점이 없는 포맷(`#,##0`)으로 변경하세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws["C2"].number_format = "#,##0"</pre>
</details>

### Q27. 백분율(퍼센트) 넘버 포맷 지정
D2 셀의 수치 데이터를 소수점 둘째 자리까지 표시하는 퍼센트 포맷(`0.00%`)으로 변경하세요. (예: 0.1234 -> 12.34%)

<details><summary><b>정답 보기</b></summary>
<pre>ws["D2"].number_format = "0.00%"</pre>
</details>

### Q28. 워크북 내 신규 시트 추가 (create_sheet)
기존 시트들 맨 마지막 위치에 `"정산로그"` 라는 이름의 신규 시트를 생성 삽입하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>ws_log = wb.create_sheet(title="정산로그")</pre>
</details>

### Q29. 워크북 내 시트 삭제 (remove)
워크북에서 `"Sheet"` 라는 이름의 필요 없는 기본 시트를 삭제하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre># wb.remove(wb["Sheet"]) 형태로 시트 객체를 전달하여 삭제합니다.
if "Sheet" in wb.sheetnames:
    wb.remove(wb["Sheet"])</pre>
</details>

### Q30. 데이터 셀 좌표를 엑셀 좌표 문자열로 변환
숫자 행번호 5, 열번호 3을 문자열 좌표인 `"C5"`로 변환해 반환하는 openpyxl 유틸리티 모듈 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from openpyxl.utils import get_column_letter
col_letter = get_column_letter(3)  # 'C'
cell_coord = f"{col_letter}5"      # 'C5'
print(cell_coord)</pre>
</details>

---

<a name="advanced"></a>
## 3. 심화 문제 (Q31 ~ Q45): 멀티시트, 대용량 데이터 가공, DB 벌크 연동 및 검증

### Q31. 모든 시트의 첫 번째 행 데이터만 수집
워크북 `wb` 내 모든 시트를 순회하며 각 시트의 A1 셀 값(헤더명)을 모아 출력하는 스크립트를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>for sheet_name in wb.sheetnames:
    current_sheet = wb[sheet_name]
    print(f"[{sheet_name}] 헤더 A1: {current_sheet['A1'].value}")</pre>
</details>

### Q32. 특정 텍스트가 들어있는 셀 검색 및 색상 강조
시트 전체 영역을 돌며 값에 `"오류"` 또는 `"ERROR"` 단어가 포함된 셀이 있다면, 배경색을 빨간색(`FFC7CE`)으로 강조 표시하는 스크립트를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from openpyxl.styles import PatternFill
red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
    for cell in row:
        if cell.value and isinstance(cell.value, str):
            if "오류" in cell.value or "ERROR" in cell.value:
                cell.fill = red_fill</pre>
</details>

### Q33. Pandas를 이용한 멀티 엑셀 시트 로드
`pd.read_excel()`의 `sheet_name` 매개변수 속성을 `None`으로 설정하여, 엑셀 파일 내의 모든 시트를 시트명을 Key로 하고 DataFrame을 Value로 하는 딕셔너리로 한꺼번에 로드하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import pandas as pd
all_sheets_dict = pd.read_excel("sales_report.xlsx", sheet_name=None)
# sheet_name=None 지정시 전체 시트 딕셔너리가 반환됩니다.
for sheet_name, df in all_sheets_dict.items():
    print(f"시트명: {sheet_name}, 데이터 행수: {len(df)}")</pre>
</details>

### Q34. 엑셀 업로드 유효성 검사 (Null 체크)
엑셀에서 데이터를 가져왔을 때, 필수 컬럼인 `"매장코드"` 열에 빈값(NaN 또는 None)이 있는 로우를 찾아내어 경고를 보내고 해당 로우를 정제 드롭하는 Pandas 코드를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre># NaN이 포함된 행 제거
df_clean = df.dropna(subset=["매장코드"])
# 혹은 빈 행 개수 세기
null_count = df["매장코드"].isnull().sum()
if null_count > 0:
    print(f"누락된 매장코드 행 {null_count}건 감지! 자동 제외합니다.")</pre>
</details>

### Q35. Pandas 데이터를 이용한 조건부 집계 계산
데이터프레임 `df`에서 `"체인코드"`가 `"C001"`인 매장들의 `"금일매출"` 총합을 Pandas 수식으로 한 줄로 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>c001_total = df[df["체인코드"] == "C001"]["금일매출"].sum()
print("C001 총 매출:", c001_total)</pre>
</details>

### Q36. 두 개의 엑셀 데이터 병합 (Merge/Join)
매출 테이블 데이터프레임 `df_sales`와 매장 정보 데이터프레임 `df_info`가 있습니다. 두 데이터프레임을 `"매장코드"` 공통 열 기준으로 SQL Left Join 형태로 결합하는 Pandas 함수를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre># how="left" 지정
merged_df = pd.merge(df_sales, df_info, on="매장코드", how="left")</pre>
</details>

### Q37. 대용량 데이터를 다중 시트로 분할 작성 (ExcelWriter)
Pandas의 `ExcelWriter` 객체를 활용해 동일한 파일 `"split_sales.xlsx"` 내에 `df_hq`는 `"본사"` 시트로, `df_store`는 `"매장"` 시트로 각각 라이팅하여 완성 저장하는 코드를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import pandas as pd
with pd.ExcelWriter("split_sales.xlsx") as writer:
    df_hq.to_excel(writer, sheet_name="본사", index=False)
    df_store.to_excel(writer, sheet_name="매장", index=False)</pre>
</details>

### Q38. 날짜 컬럼 형식 통일화 (Pandas)
엑셀 내 날짜 열 데이터가 어떤 행은 `"2026-07-06"`, 어떤 행은 `"2026/07/06"`로 난잡하게 표기되어 있습니다. 이를 `"YYYYMMDD"` 포맷 텍스트로 일괄 정제 변환하는 Pandas 식을 선언하세요.

<details><summary><b>정답 보기</b></summary>
<pre># datetime 변환 후 YYYYMMDD 포맷 문자열 처리
df["날짜"] = pd.to_datetime(df["날짜"]).dt.strftime("%Y%m%d")</pre>
</details>

### Q39. 엑셀 업로드 유효성 검사 (매장코드 포맷)
엑셀 파일의 매장코드 컬럼 값이 `"NC"`로 시작하는 6자리 정규식 패턴(예: `NC\d{4}`)을 따르는지 순회 검사하여, 틀린 형식이 있으면 오류 리스트에 담는 스크립트를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import re
invalid_rows = []
for index, row in df.iterrows():
    code = str(row["매장코드"])
    if not re.match(r'^NC\d{4}$', code):
        invalid_rows.append((index + 2, code)) # 엑셀 실제 행번호(index + 2)</pre>
</details>

### Q40. 엑셀 데이터를 DB SDAILYTB에 Insert하기 (psycopg2 벌크)
엑셀에서 읽어들인 튜플 목록 `data_rows = [("NC0002", 5200000), ("NC0007", 3800000)]`을 데이터베이스 `hmsfns.SDAILYTB` 테이블에 psycopg2의 executemany와 트랜잭션 커밋으로 안전하게 적재하는 함수를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import psycopg2

def insert_bulk_data(data_rows):
    try:
        conn = psycopg2.connect(host="192.168.10.206", dbname="edb", user="hmsfns_was", password="pw", port="5432")
        cur = conn.cursor()
        query = "INSERT INTO hmsfns.SDAILYTB (MS_NO, SALE_AMT) VALUES (%s, %s)"
        cur.executemany(query, data_rows)
        conn.commit()
        cur.close()
        conn.close()
        print("벌크 인서트 완료")
    except Exception as e:
        print("오류 발생 롤백:", e)</pre>
</details>

### Q41. DB 테이블 데이터를 조회해 엑셀 파일로 출력하기
psycopg2로 `SELECT MS_NO, SALE_AMT FROM hmsfns.SDAILYTB` 조회한 결과를 Pandas DataFrame으로 변환하고 곧바로 엑셀 `"db_export.xlsx"`로 자동 저장하는 지름길 코드를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import pandas as pd
import psycopg2

conn = psycopg2.connect(host="192.168.10.206", dbname="edb", user="hmsfns_was", password="pw", port="5432")
# pandas의 read_sql 함수 활용 시 SQL 결과를 데이터프레임으로 자동 변환해 줍니다.
df = pd.read_sql("SELECT MS_NO, SALE_AMT FROM hmsfns.SDAILYTB", conn)
df.to_excel("db_export.xlsx", index=False)
conn.close()</pre>
</details>

### Q42. openpyxl을 이용한 시트 숨기기 (Hidden Sheet)
관리용 비밀 원본 데이터가 저장된 `"SECRET_DATA"` 시트를 일반 사용자에게 보이지 않도록 숨김 처리(Hidden)하는 속성 코드를 대입하세요.

<details><summary><b>정답 보기</b></summary>
<pre># state 속성에 "hidden" 대입
wb["SECRET_DATA"].sheet_state = "hidden"</pre>
</details>

### Q43. openpyxl 수식 결과값과 수식 원본 구별 로드 에러 처리
load_workbook 사용 시 `data_only=True`로 로드했으나 엑셀 파일 내 수식 셀 값이 None으로 출력되는 현상이 있습니다. 이 현상이 왜 발생하는지, 조치 방법을 서술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 파이썬 openpyxl 엔진은 직접 수식 계산기가 내장되어 있지 않으므로, 엑셀 파일 내 캐시된 연산 결과를 읽어옵니다. 엑셀 프로그램 등으로 한 번도 열어서 저장(Recalculated)하지 않은 채 수식만 써진 원본 파일인 경우 계산 캐시가 없어 None이 반환됩니다. 한 번 엑셀로 열어 저장하거나 xlsxwriter 등으로 새로 수식 결과 캐시를 채워주어야 합니다.</pre>
</details>

### Q44. openpyxl 특정 셀 영역 클리어 (Clear Data Only)
A2부터 C10 영역 내의 폰트 스타일이나 배경색 테두리는 그대로 둔 채, 셀 안에 기록된 **데이터 값(value)**만 일괄 `None`으로 지워 리셋하는 함수를 루프로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>for row in ws["A2:C10"]:
    for cell in row:
        cell.value = None</pre>
</details>

### Q45. 카테고리 8 종합 실무 시험 문제
다음 실무 정산 처리를 자동으로 수행하는 파이썬 통합 스크립트 골격을 완성하세요.
1. `"HMS_Sales_Report.xlsx"` 파일을 Pandas 데이터프레임으로 읽어옵니다.
2. `"금일매출"` 열의 값이 비어있거나 누락된(Null) 행이 있으면 기본값 `0`으로 일괄 치환(fillna) 적용합니다.
3. 정산일자 컬럼 `"2026/07/06"` 처럼 대시 또는 슬래시가 혼합된 텍스트 날짜 데이터를 정규식 치환을 쓰거나 날짜 처리를 연동하여 깨끗한 8자리 문자형 `"20260706"` 데이터로 일괄 클리닝 정제하세요.
4. 클리닝 처리가 완료된 깨끗한 정산 정보 데이터프레임을 신규 엑셀 파일 `"Cleaned_HMS_Report.xlsx"`로 내보내기하고 마감 결과를 프린트하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import pandas as pd
import re

def process_hms_excel(file_path):
    # 1. 로드
    df = pd.read_excel(file_path)
    
    # 2. 누락매출 0원 치환
    if "금일매출" in df.columns:
        df["금일매출"] = df["금일매출"].fillna(0).astype(int)
        
    # 3. 날짜 클리닝 (정규식 또는 datetime 치환 활용)
    def clean_date(date_val):
        date_str = str(date_val).strip()
        # 모든 숫자 이외 문자(-, /, 공백 등) 제거
        cleaned = re.sub(r'[^0-9]', '', date_str)
        return cleaned[:8] # YYYYMMDD 크기 제한
        
    if "정산일자" in df.columns:
        df["정산일자"] = df["정산일자"].apply(clean_date)
        
    # 4. 저장
    output_path = "Cleaned_HMS_Report.xlsx"
    df.to_excel(output_path, index=False)
    print(f"정산 데이터 정제 완료. 출력파일: {output_path}")

if __name__ == "__main__":
    process_hms_excel("HMS_Sales_Report.xlsx")</pre>
</details>
