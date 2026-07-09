# Python 실전 연습 문제집 - [카테고리 7] 실무 라이브러리 및 정규식, DB 연동 (100제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"Cat7"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py Cat7 Q1 True` (Q1 문제를 완료로 변경)


본 문제집은 파이썬의 표준/외장 유틸리티 라이브러리인 **날짜/시간(datetime)**, **파일 수집(glob)**, **JSON 파싱 및 직렬화**, **정규표현식(re)**, 그리고 **EDB/PostgreSQL 데이터베이스 연동(psycopg2)**에 관한 실무형 100문제와 해설식 정답을 수록하고 있습니다.

---

### Q1 ~ Q25: 날짜 및 시간 처리 (datetime)
### Q1. 현재 시스템 시간 획득
현재 시스템의 오늘 날짜와 정확한 시각을 나타내는 datetime 객체를 획득하는 구문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from datetime import datetime
now = datetime.now()
print(now)</pre>
</details>

### Q2. 날짜 객체에서 연/월/일 개별 추출
Q1의 datetime 객체 `now`에서 연도, 월, 일을 정수형 속성으로 각각 추출해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(now.year, now.month, now.day)</pre>
</details>

### Q3. 날짜 객체에서 시/분/초 추출
Q1의 `now` 객체에서 시간, 분, 초를 정수로 추출해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(now.hour, now.minute, now.second)</pre>
</details>

### Q4. 특정 일시 수동 정의 생성
"2026년 7월 6일 18시 30분"을 가리키는 datetime 객체 `dt`를 수동 생성해 대입하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from datetime import datetime
dt = datetime(2026, 7, 6, 18, 30)
print(dt)</pre>
</details>

### Q5. 날짜 객체를 문자열로 포맷 출력 (strftime)
datetime 객체를 `"2026-07-06 18:30:00"` 형식의 문자열로 변환하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
print(formatted)</pre>
</details>

### Q6. 날짜 객체를 압축 날짜 형식 YYYYMMDD로 출력
오늘 날짜를 DB 적재용 8자리 문자열 `"20260706"` 형식으로 만들어 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>today_str = datetime.now().strftime("%Y%m%d")
print(today_str)</pre>
</details>

### Q7. 날짜 문자열을 날짜 객체로 역변환 (strptime)
날짜 문자열 `"2026/07/06"`을 대응하는 datetime 객체로 파싱하여 되돌리는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>parsed_dt = datetime.strptime("2026/07/06", "%Y/%m/%d")
print(parsed_dt)</pre>
</details>

### Q8. 날짜 차이 및 가감 계산 (timedelta)
오늘로부터 정확히 15일 뒤의 날짜를 계산하는 timedelta 수식을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from datetime import datetime, timedelta
future = datetime.now() + timedelta(days=15)
print(future.strftime("%Y-%m-%d"))</pre>
</details>

### Q9. 날짜 빼기 계산
오늘 날짜로부터 정확히 30일 전의 과거 날짜를 구하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>past = datetime.now() - timedelta(days=30)
print(past.strftime("%Y-%m-%d"))</pre>
</details>

### Q10. 두 날짜 사이의 차이 일수 계산 (Days)
`d1 = datetime(2026, 7, 6)` 과 `d2 = datetime(2026, 6, 6)` 사이의 정확한 차이 일수를 정수형 `30`으로 획득하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d1 = datetime(2026, 7, 6)
d2 = datetime(2026, 6, 6)
delta = d1 - d2
print(delta.days) # 30</pre>
</details>

### Q11. 요일 획득 숫자 구하기 (weekday)
특정 날짜가 무슨 요일인지 월요일(0) ~ 일요일(6) 사이의 정수로 알려주는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>dt = datetime(2026, 7, 6) # 월요일
print(dt.weekday()) # 0</pre>
</details>

### Q12. 요일을 한글 텍스트로 치환 출력
Q11의 weekday 결과를 사용해 한글 요일 명칭인 `"월요일"`, `"화요일"`... 등을 얻을 수 있도록 한글 요일 리스트 매핑 코드를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>week_days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
idx = datetime.now().weekday()
print("금일 요일:", week_days[idx])</pre>
</details>

### Q13. 타임스탬프 정수 변환 (timestamp)
현재 시각을 Unix Epoch 초 단위 정수값으로 변환해 리턴하는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(int(datetime.now().timestamp()))</pre>
</details>

### Q14. 타임스탬프로부터 날짜 객체 복원 (fromtimestamp)
Unix 타임스탬프 초 정수인 `1780735200`을 다시 datetime 객체로 복원하는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>dt = datetime.fromtimestamp(1780735200)
print(dt)</pre>
</details>

### Q15. 날짜 포맷 기호 %H와 %I의 차이점
시간을 포매팅할 때 사용하는 `%H`와 `%I` 기호의 출력 자릿수/범위 차이를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># %H는 24시간 형식(00~23)으로 출력하고, %I는 12시간 형식(01~12)으로 시간을 표현합니다.</pre>
</details>

### Q16. 날짜 포맷 기호 %M와 %m의 차이점
포맷 문자열 내에 위치하는 대문자 `%M`과 소문자 `%m`의 의미적 구분을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 대문자 %M은 분(Minute, 00~59)을 뜻하고, 소문자 %m은 월(Month, 01~12)을 나타냅니다. 혼동 주의!</pre>
</details>

### Q17. timedelta 시간/분 가감
현재 시각으로부터 3시간 30분 뒤의 정확한 시점을 가감 연산하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>future_time = datetime.now() + timedelta(hours=3, minutes=30)
print(future_time)</pre>
</details>

### Q18. 윤년 연도 여부 판별 (calendar 모듈 연동)
파이썬 표준 `calendar` 모듈의 `isleap` 함수를 사용해 연도 `2026`이 윤년인지 판별하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import calendar
print(calendar.isleap(2026)) # False</pre>
</details>

### Q19. 특정 월의 마지막 날짜(말일) 구하기
`calendar.monthrange(year, month)` 함수가 리턴하는 두 개의 값(시작요일, 당월일수) 중 두 번째 값을 사용하여 2026년 2월의 마지막 일자를 정수로 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import calendar
first_day_weekday, last_day = calendar.monthrange(2026, 2)
print("2월 말일:", last_day) # 28</pre>
</details>

### Q20. 날짜의 오전/오후 구별 출력 (%p)
현재 시각을 한글 또는 영어 AM/PM 지시자를 포함하여 `"PM 06:30"` 과 같은 문자열 형식으로 변환 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(datetime.now().strftime("%p %I:%M"))</pre>
</details>

### Q21. 날짜 범위 검사 조건식
특정 거래 일자 변수 `sale_date = "20260706"`이 정산 시작일 `"20260701"`과 종료일 `"20260710"` 사이에 포함되는지 3단 비교문으로 간결히 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>sale_date = "20260706"
if "20260701" <= sale_date <= "20260710":
    print("정산 기간 내 거래")</pre>
</details>

### Q22. ISO 표준 날짜 포맷 문자열 획득 (isoformat)
현재 시각을 ISO 8601 표준 포맷 문자열(예: `"2026-07-06T18:30:00.123456"`)로 변환 출력해 주는 내장 함수를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(datetime.now().isoformat())</pre>
</details>

### Q23. 두 날짜의 선후 관계 판단
`dt1 = datetime(2026, 7, 6)` 이 `dt2 = datetime(2026, 7, 7)` 보다 과거(이전 날짜) 인지 비교 연산자로 확인해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>dt1 = datetime(2026, 7, 6)
dt2 = datetime(2026, 7, 7)
print(dt1 < dt2) # True</pre>
</details>

### Q24. 날짜 간의 세부 마이크로초 차이 계산
두 날짜의 차이 델타 객체 `delta = dt1 - dt2` 로부터 일자 단위가 아닌 순수 소요 초(Seconds)를 누적 실수값으로 가져오는 메소드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>delta = dt2 - dt1
print(delta.total_seconds()) # 86400.0</pre>
</details>

### Q25. 연도와 주차(Week Number) 획득 (isocalendar)
오늘이 2026년도의 몇 번째 주차(1~53주)에 해당하고 무슨 요일인지 튜플 정보로 반환해주는 메소드를 쓰세요. (힌트: isocalendar)

<details><summary><b>정답 보기</b></summary>
<pre>year, week_num, day_of_week = datetime.now().isocalendar()
print(f"연도: {year}, 주차: {week_num}주차, 요일번호: {day_of_week}")</pre>
</details>

---

### Q26 ~ Q50: glob 및 파일 검색, JSON 처리
### Q26. 파일 검색 모듈 (glob) 기본 매칭
`glob` 모듈을 임포트하여 현재 작업 디렉토리 내 모든 `.txt` 확장자 파일 리스트를 수집하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import glob
txt_files = glob.glob("*.txt")
print(txt_files)</pre>
</details>

### Q27. glob의 재귀적 하위 폴더 탐색 옵션 (recursive)
`"D:\hmTest"` 하위의 모든 서브 디렉토리를 깊이 탐색하며 파일명이 `"generate"`로 시작하는 모든 파이썬 스크립트(`*.py`) 목록을 찾아내는 glob 스캔 경로 와일드카드 작성법을 쓰세요 (recursive=True 적용 필수).

<details><summary><b>정답 보기</b></summary>
<pre>import glob
matched = glob.glob("D:\\hmTest\\**\\generate*.py", recursive=True)
print(matched)</pre>
</details>

### Q28. 파일 단일 와일드카드 문자 매칭
`"data?.csv"` 에서 물음표(`?`) 기호 와일드카드의 의미 매칭 범위를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 글자수 딱 1글자의 임의 문자가 들어오는 자리를 의미합니다. (예: data1.csv, dataA.csv 등 매칭)</pre>
</details>

### Q29. 대괄호를 활용한 특정 문자 범위 매칭
`"data[0-9].csv"` 와일드카드 경로가 매칭시키는 파일명 범위 예시를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># data 뒤에 0부터 9 사이의 숫자가 딱 1자리 오는 파일명들만 매칭합니다 (예: data2.csv는 매칭, dataA.csv는 탈락).</pre>
</details>

### Q30. JSON 모듈 임포트
파이썬에서 JSON 데이터를 다루기 위해 기본 임포트하는 내장 모듈명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json</pre>
</details>

### Q31. JSON 직렬화 (Serialize / dump)
파이썬 딕셔너리 데이터를 JSON 파일 `"config.json"`에 쓰기(라이팅) 저장하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json
data = {"port": 5432, "host": "localhost"}
with open("config.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)</pre>
</details>

### Q32. JSON 역직렬화 (Deserialize / load)
`"config.json"` 파일을 읽어서 파이썬 딕셔너리 객체로 환원 복원하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json
with open("config.json", "r", encoding="utf-8") as f:
    config_dict = json.load(f)
print(type(config_dict), config_dict["port"])</pre>
</details>

### Q33. 메모리 내 JSON 문자열 변환 (dumps)
딕셔너리 객체 `d = {"status": "OK"}`를 파일 쓰기 없이 단순 메모리 상에서 텍스트형 문자열 `{"status": "OK"}`로 변환하는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>json_str = json.dumps(d)
print(type(json_str), json_str)</pre>
</details>

### Q34. 메모리 내 JSON 문자열 파싱 (loads)
JSON 텍스트 포맷 문자열 `json_str = '{"complete": true}'`를 파이썬 딕셔너리 객체로 번역해 주는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = json.loads(json_str)
print(data["complete"])</pre>
</details>

### Q35. JSON 한글 깨짐 방지 옵션 (ensure_ascii)
`json.dumps()` 또는 `json.dump()` 사용 시 한글 텍스트 문자열이 유니코드 기호(`\uac00`)로 변환되어 저장되는 것을 강제 방어하는 옵션을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># ensure_ascii=False 옵션을 부여합니다.</pre>
</details>

### Q36. JSON 보기 좋은 들여쓰기 출력 옵션 (indent)
JSON 문자열로 추출할 때, 일렬 텍스트가 아닌 계층 구조별로 4칸의 공백 인덴트를 주어 이쁘게 포맷팅되도록 보장하는 옵션을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre># indent=4 옵션을 지정합니다.</pre>
</details>

### Q37. JSON 파싱 시 키 누락 방지 기법
JSON 로드 데이터 `data = {"a": 1}`에서 키 `"b"`가 들어있는지 안전하게 확인하며 가져오기 위해 딕셔너리의 어떤 메소드를 연계 호출해야 하나요?

<details><summary><b>정답 보기</b></summary>
<pre># data.get("b", "default_val")</pre>
</details>

### Q38. JSON 저장 시 딕셔너리 키 정렬 옵션 (sort_keys)
JSON 파일로 딕셔너리를 저장할 때, 무작위 순서인 키값들을 알파벳 정렬 순서대로 정리하여 파일에 저장시키는 정렬 활성화 옵션을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># sort_keys=True 옵션을 부여합니다.</pre>
</details>

### Q39. JSON 디코딩 에러 대처 (JSONDecodeError)
잘못된 쉼표나 괄호 누락이 발생한 찌그러진 JSON 텍스트를 파싱하려 할 때 뿜어내는 json 모듈 전용 예외 클래스명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># json.JSONDecodeError 예외가 발생합니다.</pre>
</details>

### Q40. 복합 JSON 배열 리스트 추출 순회
`[{"id": "a"}, {"id": "b"}]` 형태의 JSON 텍스트 리스트를 파싱하고, 각 아이디를 루프 돌며 순차 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>json_list_str = '[{"id": "a"}, {"id": "b"}]'
users = json.loads(json_list_str)
for u in users:
    print(u["id"])</pre>
</details>

### Q41. 파이썬 datetime 객체를 JSON으로 직렬화할 때의 에러
`{"date": datetime.now()}` 와 같은 딕셔너리를 그대로 `json.dumps()` 하려 할 때 던지는 TypeError 원인을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># JSON 표준 규격에는 datetime 객체 형식 타입이 정의되어 있지 않으므로 직렬화 불가능 에러가 터집니다. 문자열로 변환하여 넘기거나 커스텀 인코더 클래스를 만들어야 합니다.</pre>
</details>

### Q42. datetime 커스텀 JSON 인코더 구현
Q41 문제를 극복하기 위해 `json.JSONEncoder`를 상속받아 datetime을 문자열로 자동 변환 처리해 주는 인코더 클래스를 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)

# json.dumps(data, cls=DateEncoder) 로 호출 가능</pre>
</details>

### Q43. JSON과 딕셔너리의 표기법 차이 (Boolean, None)
파이썬 딕셔너리의 `True`, `False`, `None` 값이 json.dumps를 거치면 최종 문자열 포맷 안에서 각각 어떻게 기호 변환되는지 기술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># True -> true
# False -> false
# None -> null (소문자화 및 JavaScript 형식 단어로 치환됨)</pre>
</details>

### Q44. glob 검색 결과 정렬 상태
`glob.glob()` 메소드를 통해 탐색 반환된 파일명 리스트들의 내부 정렬 순서는 보장되나요?

<details><summary><b>정답 보기</b></summary>
<pre># 보장되지 않습니다. OS 파일 시스템 스캔 상태에 따라 무작위로 나오므로, 순차 처리가 중요할 시 list.sort() 또는 sorted()로 감싸 정렬을 강제해야 합니다.</pre>
</details>

### Q45. 특정 문자열 포함 파일 찾기 융합
glob으로 `*.log` 파일 목록을 구하고, 각 파일을 열어 내부에 `"ERROR"` 텍스트가 써진 행이 있는 파일의 경로명들만 리스트로 모아 출력하는 실무형 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import glob, os
error_files = []
for path in glob.glob("*.log"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            if "ERROR" in f.read():
                error_files.append(path)
    except Exception:
         pass
print("에러 발견 파일 목록:", error_files)</pre>
</details>

### Q46. JSON 파일 내 속성 추가 갱신 로드 구조
`"config.json"` 파일을 열어 값을 읽고, `"max_retry": 5` 라는 속성을 딕셔너리에 추가 대입한 후, 다시 동일한 파일에 덮어쓰기 저장하는 온전한 갱신 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>config_path = "config.json"
# 1. 로드
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
# 2. 추가
config["max_retry"] = 5
# 3. 세이브
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)</pre>
</details>

### Q47. glob 와일드카드 문자 탈출 (escape)
파일명 내에 실제로 `*`이나 `?` 같은 와일드카드 특수기호 문자가 물리적으로 박혀있는 경우, 이를 와일드카드로 작동시키지 않고 일반 문자로 취급하여 정확히 glob 매칭 스캔하는 이스케이프 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import glob
escaped_path = glob.escape("data*file.csv")
print(escaped_path) # 'data[*]file.csv'</pre>
</details>

### Q48. 지정 파일 제외 스캔 리스트 컴프리헨션
`glob.glob("*.md")` 결과에서 특정 매뉴얼 파일 `"Readme.md"` 만은 리스트에서 빼버리는 정제 코드를 컴프리헨션으로 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>matched = glob.glob("*.md")
filtered = [path for path in matched if os.path.basename(path) != "Readme.md"]
print(filtered)</pre>
</details>

### Q49. JSON 파일 깨짐 방지 try-except 구조
구조가 깨져 파싱 실패 위험이 있는 외부 연동 API JSON 문자열 `raw_data`를 안정적으로 파싱 처리하는 try-except 예외 처리 감싸기 구문을 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>raw_data = "{invalid_json}"
try:
    data = json.loads(raw_data)
except json.JSONDecodeError:
    data = {} # 빈 객체 대체 안전 조치
    print("API 응답 JSON 파싱 실패")</pre>
</details>

### Q50. glob 대괄호 부정 패턴 매칭 (Not Matching)
숫자 1글자가 붙은 파일 중 `data1.csv`, `data2.csv` 등은 제외하고 오직 숫자가 들어가지 않은 형태들만 매칭하도록 유도하는 부정 패턴 기호를 쓰세요. (힌트: `!`)

<details><summary><b>정답 보기</b></summary>
<pre># glob.glob("data[!0-9].csv")</pre>
</details>

---

### Q51 ~ Q75: 정규표현식 (Regular Expressions) 파싱 기법
### Q51. 정규표현식 표준 모듈 임포트
파이썬에서 정규식을 활용하기 위해 들여와 사용하는 표준 라이브러리명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>import re</pre>
</details>

### Q52. 패턴 매칭 컴파일 (compile)
정규식 패턴 문자열을 미리 컴파일하여 재사용 속도를 향상시켜 주는 클래스 획득 메소드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>pattern = re.compile(r'\d+')</pre>
</details>

### Q53. 첫 부분 매칭 검사 (match)
문자열의 **시작 부분**부터 패턴이 일치하는지 단독 비교 판단하는 함수명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># re.match()</pre>
</details>

### Q54. 문자열 전체 검색 (search)
문자열 전체를 훑으며 패턴과 일치하는 부분이 최초로 등장하는 지점을 찾아주는 탐색 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>match_obj = re.search(r'\d+', "sales 120 and cost 50")
print(match_obj.group()) # 120 (최초 발견 정수)</pre>
</details>

### Q55. 전체 매칭 목록 추출 (findall)
문자열 내에서 정규식 패턴과 일치하는 모든 부분 텍스트들을 리스트 형태로 일괄 반환해 주는 함수를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>numbers = re.findall(r'\d+', "sales 120 and cost 50")
print(numbers) # ['120', '50']</pre>
</details>

### Q56. 매칭 목록 반복자 반환 (finditer)
findall과 유사하나, 매칭된 상세 객체들을 이터레이터 반복자 형태로 차례대로 던져주어 대량 문자열 매칭 시 메모리를 아끼는 함수를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>matches = re.finditer(r'\d+', "10 20 30")
for m in matches:
    print(m.group())</pre>
</details>

### Q57. 패턴 치환 함수 (sub)
문자열 내에서 정규식 패턴에 매칭된 모든 텍스트들을 지정한 대체 문자열로 강제 치환하는 함수를 작성하세요 (replace의 정규식 버전).

<details><summary><b>정답 보기</b></summary>
<pre># re.sub(패턴, 치환할문자, 원본문자열)
cleaned = re.sub(r'\s+', " ", "A   B   C")
print(cleaned) # A B C</pre>
</details>

### Q58. 정규식 룰: 숫자 1글자 지시 기호
0부터 9 사이의 숫자 단 1글자만을 가리키는 대표 이스케이프 정규식 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>r'\d'</pre>
</details>

### Q59. 정규식 룰: 공백 문자 지시 기호
엔터 개행, 탭, 스페이스 등 모든 공백 문자 1칸을 가리키는 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>r'\s'</pre>
</details>

### Q60. 정규식 룰: 문자 및 숫자 지시 기호
알파벳 대소문자, 숫자, 언더바(_)를 포함한 단어 문자 1글자를 지칭하는 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>r'\w'</pre>
</details>

### Q61. 정규식 룰: 0회 이상 반복 수량자
앞선 패턴이 0번 이상 무한히 반복 등장할 수 있음을 나타내는 수량자 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>*</pre>
</details>

### Q62. 정규식 룰: 1회 이상 반복 수량자
앞선 패턴이 반드시 최소 1번 이상 등장해야 함을 나타내는 수량자 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>+</pre>
</details>

### Q63. 정규식 룰: 등장 유무 옵션 수량자
앞선 패턴이 있거나 없을 수 있음을 가리키는 0회 혹은 1회 반복 수량자 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>?</pre>
</details>

### Q64. 정규식 룰: 임의의 한 문자
줄바꿈 기호(\n)를 제외한 이 세상의 모든 단일 문자 딱 1글자를 대변하는 만능 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>.</pre>
</details>

### Q65. 그룹 캡처 (Grouping)
정규식 매칭 결과 중 소괄호 `()` 로 감싼 특정 서브 매칭 영역의 텍스트만 쏙 빼내어 획득하는 기법명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 그룹화 (Grouping) 및 캡처 그룹 기법입니다.</pre>
</details>

### Q66. 캡처 그룹 번호 추출 (group)
정규식 패턴 `r'(\w+): (\d+)'`에 대해 매치 객체 `m`의 두 번째 소괄호 그룹인 정수 부분만 가져오기 위해 괄호 안에 지정하는 그룹 번호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># m.group(2) (0번은 매칭 전체 문자열을 가져옵니다.)</pre>
</details>

### Q67. 비탐욕적 매칭 (Non-Greedy Match)
수량자 기호 뒤에 물음표 `?`를 덧붙여(예: `.*?`), 매칭을 최대한 길게 잡으려는 탐욕(Greedy) 성질을 억제하고 가장 짧은 구간에서 일찍 끊어 종결 매칭을 시도하게 만드는 기법명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 비탐욕적(Non-Greedy) 매칭 또는 최소 매칭 기법입니다.</pre>
</details>

### Q68. 비탐욕적 매칭을 통한 대괄호 속 문자 추출 실전
텍스트 `"[HQ] Sales"`에서 대괄호 안의 `"HQ"` 만을 추출하는 비탐욕적 그룹 캡처 정규식 형태를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "[HQ] Sales"
match = re.search(r'\[(.*?)\]', s)
if match:
    print(match.group(1)) # HQ</pre>
</details>

### Q69. 메일 주소 형식 검증 정규식
임의의 문자열이 올바른 이메일 주소 포맷인지 확인하는 간단한 이메일 매칭 정규식 형태를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>email = "test@hyundai.com"
is_valid = re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)
print(bool(is_valid)) # True</pre>
</details>

### Q70. 정규식을 이용한 문자열 분할 (split)
콤마(`,`), 콜론(`:`), 세미콜론(`;`)이 무작위로 섞여있는 구분 기호 문자열 `"A,B:C;D"`를 정규식 패턴을 사용해 일괄 쪼개는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "A,B:C;D"
parts = re.split(r'[,:;]', s)
print(parts) # ['A', 'B', 'C', 'D']</pre>
</details>

### Q71. 정규식 룰: 줄의 시작 표시
정규식 패턴 안에서 해당 패턴이 반드시 문장의 맨 첫머리에 위치해야만 매칭을 인정해주는 앵커 기호를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>^</pre>
</details>

### Q72. 정규식 룰: 줄의 끝 표시
정규식 패턴 안에서 해당 패턴이 반드시 문장의 맨 끄트머리에 매칭되어 끝나야만 유효 처리해주는 앵커 기호를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>$</pre>
</details>

### Q73. 정규식 룰: 지정 문자 범위 설정
알파벳 대문자 `'A'`부터 `'Z'`까지 중 단 1글자만 허용함을 뜻하는 대괄호 설정 형식을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>[A-Z]</pre>
</details>

### Q74. 정규식 룰: 지정 문자 제외 범위 설정
Q73 대괄호 안에서 첫 칸에 꺾쇠 기호를 명시하여 `"대문자 A부터 Z를 제외한 모든 문자"`를 뜻하게 반전시키는 기호를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>[^A-Z]</pre>
</details>

### Q75. 정규식 룰: 소괄호 이스케이프
정규식 패턴 내에서 그룹 캡처의 소괄호 역할이 아닌, 실제 수학식 괄호 기호 문자 `(` 자체를 찾고 매칭하고 싶을 때 괄호 앞에 붙여야 하는 특수 이스케이프 기호를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>\(</pre>
</details>

---

### Q76 ~ Q100: psycopg2 EDB/PostgreSQL 연동 및 실무 통합
### Q76. psycopg2 설치 커맨드
파이썬 환경에서 EDB/PostgreSQL DB 연동 라이브러리를 설치하기 위해 터미널에 내리는 pip 커맨드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>pip install psycopg2-binary</pre>
</details>

### Q77. DB 접속 커넥션 객체 획득 (connect)
`psycopg2.connect()` 메소드 호출 시 필요한 5가지 주요 접속 매개변수 속성명을 나열하세요.

<details><summary><b>정답 보기</b></summary>
<pre># host, port, database (또는 dbname), user, password</pre>
</details>

### Q78. 쿼리 실행을 위한 커서 객체 생성 (cursor)
커넥션 `conn`이 연결된 후, SQL 질의 실행 통로가 되는 커서 객체를 획득하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>cursor = conn.cursor()</pre>
</details>

### Q79. SQL 실행 함수 (execute)
커서 객체 `cursor`를 사용해 데이터베이스에 `"SELECT * FROM hmsfns.MUSERSTB"` 질의를 실행시키는 명령어를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>cursor.execute("SELECT * FROM hmsfns.MUSERSTB")</pre>
</details>

### Q80. 조회 데이터 전체 가져오기 (fetchall)
실행된 쿼리의 모든 결과 행(Rows)들을 한꺼번에 튜플 리스트 형태로 메모리로 긁어오는 메소드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>rows = cursor.fetchall()</pre>
</details>

### Q81. 조회 데이터 한 행씩 가져오기 (fetchone)
메모리 절약을 위해 현재 결과 버퍼 위치에서 오직 단 하나의 행(Row)만 튜플로 획득하고 포인터를 넘기는 메소드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>row = cursor.fetchone()</pre>
</details>

### Q82. 파라미터화 쿼리 바인딩 기법 (SQL Injection 방지)
execute 실행 시 직접 문자열 더하기로 쿼리를 조립하지 않고, 파이썬이 권장하는 포맷 기호 `%s`를 사용하는 쿼리 파라미터 매핑 튜플 패싱 형식을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 튜플 뒤에 콤마를 붙여 안전한 튜플 패싱 보장
cursor.execute("SELECT * FROM table WHERE id = %s", (user_id,))</pre>
</details>

### Q83. DB 트랜잭션 수동 커밋 (commit)
INSERT / UPDATE / DELETE 쿼리 수행 후 데이터베이스 디스크 파일에 영구 기록이 반영되도록 커넥션 수준에서 지시하는 메소드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>conn.commit()</pre>
</details>

### Q84. DB 트랜잭션 롤백 (rollback)
에러 발생 시 실행한 쿼리 행위들을 모두 취소하고 이전 상태로 되돌리는 메소드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>conn.rollback()</pre>
</details>

### Q85. 커서 및 커넥션 리소스 안전 해제
연동 처리를 다 마치고 반드시 수동으로 닫아주어야 하는 2개의 객체에 대한 close() 메소드를 순서대로 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>cursor.close()
conn.close()</pre>
</details>

### Q86. execute 호출 시 튜플 전달 누락 에러
`cursor.execute("SELECT * FROM tbl WHERE x = %s", ("data"))` 로 호출하면 왜 에러가 발생하는지 설명하세요.

<details><summary><b>정답 보기</b></summary>
<pre># ("data") 는 괄호만 쳐진 일반 문자열형 변수로 평가되어 에러가 납니다. 반드시 요소가 하나인 튜플형태를 갖추도록 ("data",) 로 작성하여 우측 콤마를 명시해야 합니다.</pre>
</details>

### Q87. DB 커넥션 예외 처리 구조 (DatabaseError)
접속 거부나 쿼리 실패 시 발생하는 `psycopg2.DatabaseError`를 try-except 문으로 묶어 rollback 처리하는 안전 골격을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import psycopg2
try:
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    cursor.execute("INSERT ...")
    conn.commit()
except psycopg2.DatabaseError as e:
    if conn:
        conn.rollback()
    print("DB 트랜잭션 에러 유발 롤백 처리:", e)
finally:
    if conn:
        conn.close()</pre>
</details>

### Q88. 다량의 데이터 일괄 삽입 (executemany)
루프를 돌며 개별 execute를 무수히 반복 호출하는 대신, 튜플 목록 리스트를 한 줄의 배치 명령어로 일괄 처리하는 효율적 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data_list = [("NC0002", 10), ("NC0007", 20)]
cursor.executemany("INSERT INTO tbl VALUES (%s, %s)", data_list)</pre>
</details>

### Q89. With 구문을 통한 커넥션 커밋 자동화
psycopg2의 커넥션을 with문으로 감싸 사용할 때 블록이 무사히 끝나면 자동으로 커밋(commit)이 작동한다는 특징을 설명하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with conn:
    with conn.cursor() as cur:
        cur.execute("UPDATE ...")
# with conn 블록을 탈출 시 내부적으로 에러가 없었으면 자동 commit이 실행되며, 예외가 있었다면 자동 rollback됩니다.</pre>
</details>

### Q90. 쿼리 결과 컬럼 헤더 이름 획득 (description)
조회 결과의 실제 DB 테이블 컬럼명 리스트를 가져오기 위해 커서 객체 내부의 description 속성을 참조하는 컴프리헨션 구문을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>colnames = [desc[0] for desc in cursor.description]
print(colnames)</pre>
</details>

### Q91. JSON 텍스트 파싱 후 DB 데이터 업데이트 연계
JSON 파일로부터 읽어온 딕셔너리 정보인 `config = {"lock_cnt": 5}`를 데이터베이스 `SECURETB` 테이블에 `%s` 쿼리 바인딩으로 반영 업데이트하는 연동 코드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json, psycopg2

# 1. JSON 로드
config = json.loads('{"lock_cnt": 5}')
limit_cnt = config["lock_cnt"]

# 2. DB 반영 (가상 접속)
# cursor.execute("UPDATE hmsfns.SECURETB SET LOGIN_FAIL_LOCK_CNT = %s", (limit_cnt,))
# conn.commit()</pre>
</details>

### Q92. 정규식으로 마크다운 테이블 컬럼 추출 후 DB 적재 연동
마크다운 테이블 라인 `line = "| hq_dashboard | 대시보드 |"` 에서 대괄호나 파이프 기호 정규식 분할을 적용하고, 결과 요소를 DB 쿼리로 적재하는 구조를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import re
line = "| hq_dashboard | 대시보드 |"
# 정규식 분할 정제
fields = [f.strip() for f in re.split(r'\|', line) if f.strip()]
if len(fields) >= 2:
    scr_id, scr_nm = fields[0], fields[1]
    # cursor.execute("INSERT INTO hmsfns.SCREENTB(SCR_ID, SCR_NM) VALUES (%s, %s)", (scr_id, scr_nm))</pre>
</details>

### Q93. EDB Oracle 호환 펑션 호출 기법
EDB 데이터베이스에 빌트인 생성되어 있는 Oracle 호환 함수 `F_PASSWORD_CHK`를 파이썬 SELECT 쿼리로 호출해 리턴값을 받아오는 코드를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>cursor.execute("SELECT hmsfns.F_PASSWORD_CHK(%s) FROM DUAL", ("my_password123!",))
chk_result = cursor.fetchone()[0]
print("비밀번호 검증 등급:", chk_result)</pre>
</details>

### Q94. EDB 데이터 생성일 정렬 최종 1건 획득
최근 등록한 사용자의 정보 1건을 조회하기 위해 쿼리 맨 끝단에 부여하는 표준 SQL 제한 명령 키워드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># "SELECT * FROM hmsfns.MUSERSTB ORDER BY CREATE_DTIME DESC LIMIT 1" 의 LIMIT 1 기법을 활용합니다.</pre>
</details>

### Q95. EDB 오토커밋 설정 (autocommit)
명시적인 `commit()` 지시 없이도 매 execute마다 자동으로 트랜잭션이 영구 커밋되도록 커넥션 객체 시작 시 활성화 설정하는 속성 지정 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>conn = psycopg2.connect(...)
conn.autocommit = True</pre>
</details>

### Q96. 날짜 객체를 EDB 타임스탬프 필드로 직접 바인딩
파이썬의 `datetime.now()` 객체를 EDB의 TIMESTAMP(또는 VARCHAR2 날짜 컬럼)에 대입할 때, psycopg2 드라이버가 문자 변환 필요 없이 자동 형변환 처리해 주는지 기술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 네, psycopg2 드라이버는 파이썬의 datetime 객체를 데이터베이스의 TIMESTAMP 형식으로 내부에서 안전하게 직렬화 매핑해 주므로 형변환 없이 파라미터로 바로 전달 가능합니다.</pre>
</details>

### Q97. DB 커넥션 최대 대기 타임아웃 옵션
데이터베이스 장애 등으로 커넥션 시도가 영구히 멈춰 시스템 전체가 블록 상태에 빠지는 것을 예방하기 위해 connect() 인수 내에 지정하는 옵션을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre># connect_timeout=10 (초 단위 지정)</pre>
</details>

### Q98. 정규식 룰: 이메일 유무 판별 sub 활용 마스킹
텍스트 내에 존재하는 이메일 주소 영역을 개인정보 보호를 위해 `"***@***.***"` 문자열로 일괄 마스킹 치환하는 re.sub 코드를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import re
text = "담당자 메일은 master@hms.com 입니다."
masked = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', "***@***.***", text)
print(masked) # 담당자 메일은 ***@***.*** 입니다.</pre>
</details>

### Q99. glob으로 다중 수집한 파일명을 DB에 기록하기
glob으로 수집한 텍스트 파일명 목록을 DB에 일괄 저장하는 시나리오 구조를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import glob, psycopg2
files = glob.glob(r"D:\QaReport\*_TestCase.md")
data_pairs = [(f,) for f in files]
# cur.executemany("INSERT INTO hmsfns.REPORTS(FILE_PATH) VALUES (%s)", data_pairs)</pre>
</details>

### Q100. 카테고리 7 종합 실무 마스터 문제
다음 실무 종합 시나리오를 완벽하게 구동하는 파이썬 스크립트의 골격을 작성하세요.
1. `"D:\hmTest\backoffice\QaReport"` 경로 아래에 놓여있는 모든 `*_TestCase.md` 파일을 glob으로 수집 정렬합니다.
2. 수집된 각 파일에서 정규표현식을 사용해 파일 본문 첫 줄에 기재되어 있을 `"# [화면ID]"` 형태의 화면 ID 값을 그룹 캡처(`re.search`)해 추출합니다.
3. 추출에 성공한 파일 경로명과 화면 ID 정보를 EDB(PostgreSQL)의 `hmsfns.TC_LOG_TABLE` 테이블에 파라미터화 쿼리 `%s` 매핑으로 안전하게 INSERT하고 최종 트랜잭션 커밋(`commit`)을 제어해 마무리하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import glob
import os
import re
import psycopg2

def run_integration():
    # 1. glob 파일 스캔 및 정렬
    search_path = r"D:\hmTest\backoffice\QaReport\*_TestCase.md"
    files = sorted(glob.glob(search_path))
    
    insert_data = []
    
    # 2. 파일 스캔 및 정규식 추출
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                # 예: "# [hq_dashboard] 메인 화면" 매칭
                match = re.search(r'# \[(.*?)\]', first_line)
                if match:
                    screen_id = match.group(1)
                    file_name = os.path.basename(file_path)
                    insert_data.append((screen_id, file_name))
        except Exception as e:
            print(f"파일 처리 오류 ({file_path}): {e}")
            
    if not insert_data:
        print("적재할 유효 데이터가 없습니다.")
        return
        
    # 3. 데이터베이스 적재 트랜잭션
    conn = None
    try:
        conn = psycopg2.connect(
            host="192.168.10.206", database="edb", user="hmsfns_was", password="password", port="5432"
        )
        cursor = conn.cursor()
        
        # executemany 로 일괄 안전 적재
        query = "INSERT INTO hmsfns.TC_LOG_TABLE (SCR_ID, FILE_NM) VALUES (%s, %s)"
        cursor.executemany(query, insert_data)
        
        # 트랜잭션 커밋
        conn.commit()
        print(f"성공적으로 {len(insert_data)}건의 데이터를 DB에 적재 완료했습니다.")
        cursor.close()
    except psycopg2.DatabaseError as db_err:
        if conn:
            conn.rollback()
        print("데이터베이스 오류 발생 롤백:", db_err)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_integration()</pre>
</details>
