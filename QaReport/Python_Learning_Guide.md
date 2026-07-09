# HMS 영업정보시스템 개발자를 위한 Python 핵심 학습 가이드

본 가이드는 Java/JSP 기반의 HMS 영업정보시스템 개발자가 현업에서 자주 쓰이는 Python 자동화 스크립트(DB 적재, 파일 파싱, HTML 생성 등)를 빠르게 이해하고 작성할 수 있도록 기획된 실전형 학습 가이드입니다.

---

## 1. Python 시작하기 및 특징

Python은 간결하고 가독성이 높은 문법을 지닌 인터프리터 언어입니다. Java와 비교하여 다음과 같은 특징이 있습니다.

* **동적 타이핑 (Dynamic Typing)**: 변수의 타입을 선언하지 않으며, 실행 시점에 자동으로 결정됩니다.
* **인덴트(들여쓰기) 강제**: 블록 구분을 중괄호 `{}` 대신 **들여쓰기(공백 4칸)**로 구분하므로 일관성 있는 코드가 유지됩니다.
* **풍부한 표준 라이브러리**: 데이터 처리, 정규식 파싱, 파일 입출력, DB 연동 등을 기본 모듈로 쉽게 수행할 수 있습니다.

---

## 2. 핵심 기초 문법 (Core Syntax)

### 2.1 변수 및 데이터 타입
```python
# 1. 숫자형 및 문자열
count = 10                  # int (정수형)
price = 5000.0              # float (실수형)
store_name = "NC0007 매장"  # str (문자열)

# 2. 불리언 (Boolean)
is_active = True            # Java의 true/false와 달리 첫 글자가 대문자임
is_locked = False
```

### 2.2 제어문 (Control Flow)
```python
# 1. 조건문 (if-elif-else)
fail_cnt = 5

if fail_cnt >= 5:
    print("계정이 잠금 상태입니다.")
elif fail_cnt > 0:
    print(f"로그인 실패 횟수: {fail_cnt}")
else:
    print("정상 로그인 상태")

# 2. 반복문 (for, while)
stores = ["NC0002", "NC0007", "NC0005"]
for store in stores:
    print(f"처리 대상 매장코드: {store}")
```

### 2.3 함수 정의 (Functions)
```python
def calculate_growth_rate(today_sale, last_week_sale):
    """
    매출 증가율을 계산하여 반환하는 함수
    """
    if last_week_sale == 0:
        return 0.0
    rate = ((today_sale - last_week_sale) / last_week_sale) * 100
    return round(rate, 2)

# 함수 호출
rate_result = calculate_growth_rate(5200000, 4800000)
print(f"전주 대비 증가율: {rate_result}%") # 출력: 전주 대비 증가율: 8.33%
```

---

## 3. 강력한 내장 자료구조 (Data Structures)

### 3.1 리스트 (List) - Java의 ArrayList와 유사
```python
items = ["빵", "커피", "주스"]
items.append("도넛")      # 원소 추가
print(items[0])          # 인덱싱 (빵)
print(items[1:3])        # 슬라이싱 (['커피', '주스'])
```

### 3.2 딕셔너리 (Dictionary) - Java의 HashMap과 유사
```python
store_info = {
    "store_code": "NC0007",
    "store_name": "CAFE",
    "chain_no": "C001"
}
print(store_info["store_name"])  # 값 조회 (CAFE)
store_info["manager"] = "홍길동"  # 신규 키-값 추가
```

---

## 4. HMS 실무 스크립트에 사용되는 필수 모듈 및 라이브러리

HMS 현업 자동화 툴(`generate_screens_directory.py` 등)에 핵심적으로 사용되는 표준 및 외장 라이브러리들입니다.

### 4.1 `os` 및 `sys` (파일 및 경로 제어)
```python
import os

path = r"D:\hmTest\backoffice\QaReport"
# 특정 경로 밑에 있는 파일 목록 순회
for file_name in os.listdir(path):
    if file_name.endswith("_TestCase.md"):
        full_path = os.path.join(path, file_name)
        print(f"발견한 테스트케이스 파일: {full_path}")
```

### 4.2 `re` (정규표현식 파싱)
마크다운 테이블을 읽어 화면 정보 목록을 정적 파싱할 때 핵심적으로 작동합니다.
```python
import re

line = "| 대시보드 | hq_dashboard | 대시보드 (본사) | dashboard |"
# 정규식을 이용해 파이프(|) 기호 사이의 텍스트 추출
columns = [col.strip() for col in re.split(r'\|', line) if col.strip()]
print(columns) # ['대시보드', 'hq_dashboard', '대시보드 (본사)', 'dashboard']
```

### 4.3 `json` (설정 및 데이터 가공)
```python
import json

# JSON 파일 읽기
with open("hms_screens_progress.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 특정 키의 데이터 제어
data["hq_dashboard"]["complete"] = True

# JSON 파일 쓰기
with open("hms_screens_progress.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

### 4.4 `psycopg2` (PostgreSQL / EDB 데이터베이스 연동)
```python
import psycopg2

try:
    # 1. DB 커넥션 맺기
    conn = psycopg2.connect(
        host="192.168.10.206",
        database="edb",
        user="hmsfns_was",
        password="YOUR_PASSWORD",
        port="5432"
    )
    cursor = conn.cursor()
    
    # 2. 쿼리 실행
    cursor.execute("SELECT MS_NO, MS_NM FROM hmsfns.MMEMBSTB WHERE CHAIN_NO = %s", ('C001',))
    
    # 3. 결과 페치
    rows = cursor.fetchall()
    for row in rows:
        print(f"매장코드: {row[0]}, 매장명: {row[1]}")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"데이터베이스 오류: {e}")
```

---

## 5. 실전 예제 분석 (HMS 현황판 제네레이터 원리)

현황판을 갱신하는 [generate_screens_directory.py](file:///D:/hmTest/backoffice/QaReport/generate_screens_directory.py)의 주요 데이터 처리 로직을 축약한 예시입니다.

```python
import os
import json

def generate_hms_report():
    # 1. JSON 진척도 정보 로드
    json_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
    with open(json_path, "r", encoding="utf-8") as f:
        progress_data = json.load(f)
    
    # 2. 마크다운 테이블 파싱 (가상 처리)
    md_path = r"D:\hmTest\backoffice\QaReport\All_HMS_Screens.md"
    screens = []
    
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("|") and "물리 파일명" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 7:
                    # 화면 메타데이터 매핑
                    screen_id = parts[3]    # 예: hq_dashboard
                    file_name = parts[5]    # 예: hq_dashboard
                    
                    # 진척도 정보 결합
                    progress = progress_data.get(screen_id, {})
                    screens.append({
                        "id": screen_id,
                        "name": parts[4],
                        "file": file_name,
                        "complete": progress.get("complete", False),
                        "memo": progress.get("memo", "")
                    })
                    
    # 3. HTML 템플릿에 데이터 바인딩
    html_template = """
    <html>
    <body>
        <h1>HMS 화면 진척도 목록</h1>
        <ul>
            {list_items}
        </ul>
    </body>
    </html>
    """
    
    list_items = ""
    for s in screens:
        status = "✅ 완료" if s["complete"] else "❌ 미완"
        list_items += f"<li>{s['id']} ({s['name']}) - {status} | 비고: {s['memo']}</li>\n"
        
    final_html = html_template.format(list_items=list_items)
    
    # 4. 파일 쓰기
    with open("HMS_Sample_Report.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    print("성공적으로 샘플 리포트를 작성했습니다.")

if __name__ == "__main__":
    generate_hms_report()
```

---

## 6. 추가 심화 가이드

실무에서 대량의 정산 보고서 작성이나 업로드/다운로드 로직 작성을 위한 엑셀 제어법 및 JSON 웹 API 연동법은 아래 심화 가이드를 참고하세요.
* **[HMS 파이썬 엑셀 핸들링 실무 가이드](./Python_Excel_Handling_Guide.md)**
* **[Python & JS 기반 JSON 파일/웹 API 연동 실무 마스터 가이드](./Python_JSON_Web_Integration_Guide.md)**
* **[Python & Web API 기반 학습 진도 관리 시스템 구축 A to Z 풀 튜토리얼](./Python_JSON_Progress_Manager_Tutorial.md)**
* **[Python & Web JSON 연동 5분 완성 실습북 (Hands-on Cookbook)](./Python_JSON_Web_HandsOn_Cookbook.md)**
* **[Python 엑셀(Excel) 핸들링 5분 완성 실습북 (Hands-on Cookbook)](./Python_Excel_HandsOn_Cookbook.md)**
* **[파이썬 엑셀 데이터 가공 및 변환 10단계 마스터 실습북 (Hands-on Cookbook)](./Python_Excel_Data_Cleansing_Cookbook.md)**
* **[터미널 및 파이썬 파일 경로(Path) 규칙 완벽 가이드](./Terminal_And_Python_Path_Guide.md)**







