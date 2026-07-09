# Python 실전 연습 문제집 - [카테고리 4] 함수 및 람다 (100제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"Cat4"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py Cat4 Q1 True` (Q1 문제를 완료로 변경)


본 문제집은 파이썬의 핵심 실행 단위인 **함수 정의**, **매개변수 기본값**, **가변 매개변수(*args, **kwargs)**, **람다(Lambda) 익명 함수**, **map/filter 함수 활용**, **재귀 호출** 등에 관한 100문제와 해설식 정답을 수록하고 있습니다.

---

### Q1 ~ Q30: 함수 정의 및 기본 매개변수
### Q1. 함수 정의 키워드
파이썬에서 함수를 정의하기 위해 사용하는 예약어(키워드)를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def</pre>
</details>

### Q2. 기본 매개변수 함수
인자 없이 호출하면 "Hello"를 출력하는 함수 `greet()`를 작성하고 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def greet():
    print("Hello")

greet()</pre>
</details>

### Q3. 파라미터 전달 함수
문자열 `name`을 인자로 전달받아 "Hello, [이름]"을 출력하는 함수 `greet_user(name)`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def greet_user(name):
    print(f"Hello, {name}")

greet_user("홍길동")</pre>
</details>

### Q4. 값 반환 함수 (return)
두 수 `x`, `y`를 받아 더한 합을 리턴하는 함수 `add(x, y)`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def add(x, y):
    return x + y

res = add(10, 20)
print(res)</pre>
</details>

### Q5. 다중 값 반환 (Multiple Returns)
두 수 `x`, `y`를 받아 합과 차를 튜플 형태로 동시에 반환하는 함수 `calc(x, y)`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def calc(x, y):
    return x + y, x - y

s, d = calc(10, 5)
print(s, d) # 15 5</pre>
</details>

### Q6. 기본값 매개변수 (Default Argument)
메시지 `msg`를 출력하되, 인자 전달이 없으면 디폴트 문자열 `"No message"`를 출력하는 함수 `show(msg="No message")`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def show(msg="No message"):
    print(msg)

show()</pre>
</details>

### Q7. 매개변수 기본값 선언 순서 주의점
`def func(a=1, b):` 와 같이 기본값이 있는 파라미터를 기본값이 없는 파라미터보다 먼저 앞에 배치해 선언할 때 일어나는 문법 오류를 주석으로 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># SyntaxError: non-default argument follows default argument 오류가 발생합니다. 기본값 파라미터는 반드시 뒤쪽에 몰아서 배치해야 합니다.</pre>
</details>

### Q8. Docstring 선언
함수 본문 바로 하단에 함수 설명(Documentation)을 여러 줄 문자열 형식으로 달아두는 기법(Docstring)을 작성해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>def process():
    """
    이 함수는 HMS 마감 처리를 진행하는
    실무 핵심 유틸리티 함수입니다.
    """
    pass</pre>
</details>

### Q9. 리스트를 리턴하는 함수
정수 `n`을 입력받아 1부터 `n`까지 담긴 리스트를 리턴하는 함수 `make_list(n)`을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def make_list(n):
    return list(range(1, n+1))

print(make_list(5)) # [1, 2, 3, 4, 5]</pre>
</details>

### Q10. Pass 키워드 활용
함수의 뼈대 구조만 정의해 두고 본문은 빈 칸으로 비워 에러를 방지할 때 사용하는 구문 예약어를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>def future_function():
    pass</pre>
</details>

### Q11. 키워드 인자 지정 호출 (Keyword Arguments)
`def info(name, age):` 함수를 호출할 때 순서를 바꿔 `info(age=30, name="김대리")` 처럼 호출하는 호출방식 기법명을 기술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 키워드 인수(Keyword Arguments) 전달 방식입니다. 인자 전달 시 순서 오류를 예방해 줍니다.</pre>
</details>

### Q12. 홀수 짝수 판별 함수
정수 `n`을 입력받아 짝수이면 `True`, 홀수이면 `False`를 리턴하는 함수 `is_even(n)`을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def is_even(n):
    return n % 2 == 0</pre>
</details>

### Q13. 평균 계산 함수
리스트를 인자로 받아 원소들의 평균값을 계산하여 리턴하는 함수 `avg_list(lst)`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def avg_list(lst):
    if not lst:
        return 0.0
    return sum(lst) / len(lst)</pre>
</details>

### Q14. 문자열 쪼개기 변환 함수
문자열 `"A,B,C"`를 받아 콤마 단위로 분리된 리스트를 반환하는 함수 `split_csv(s)`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def split_csv(s):
    return s.split(",")</pre>
</details>

### Q15. 리스트 중복 제거 반환 함수
리스트를 인자로 받아 중복이 제거된 정렬 상태의 리스트를 반환하는 함수 `unique_sorted(lst)`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def unique_sorted(lst):
    return sorted(list(set(lst)))</pre>
</details>

### Q16. 매개변수로 전달받은 딕셔너리 안전 읽기
딕셔너리 `d`와 키 `k`를 인자로 받아 안전하게 get() 연산을 적용해 출력하는 함수를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def read_key(d, k):
    print(d.get(k, "없음"))</pre>
</details>

### Q17. 세 수 중 최댓값 구하기 함수
세 수 `a`, `b`, `c`를 매개변수로 전달받아 가장 큰 수를 반환하는 함수 `max_of_three(a, b, c)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def max_of_three(a, b, c):
    return max(a, b, c)</pre>
</details>

### Q18. 문자 횟수 계산 함수
문자열 `s`와 찾을 철자 `char`를 인자로 받아 해당 철자가 등장한 빈도 개수를 리턴하는 함수 `char_count(s, char)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def char_count(s, char):
    return s.count(char)</pre>
</details>

### Q19. 특정 범위 정수 리스트 필터링 함수
정수 리스트 `lst`를 받아 5 이상 15 이하의 수들만 리스트 컴프리헨션으로 필터링해 반환하는 함수 `filter_range(lst)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def filter_range(lst):
    return [x for x in lst if 5 <= x <= 15]</pre>
</details>

### Q20. 비밀번호 최소 길이 만족 판단 함수
패스워드 문자열 `pwd`를 전달받아 길이가 8자리 이상이면 `True`, 아니면 `False`를 리턴하는 함수 `check_pw_len(pwd)`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def check_pw_len(pwd):
    return len(pwd) >= 8</pre>
</details>

### Q21. 리스트 요소 제곱 변환 함수
숫자 리스트 `lst`를 받아 각 원소를 제곱한 새로운 리스트를 반환하는 함수 `square_list(lst)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def square_list(lst):
    return [x**2 for x in lst]</pre>
</details>

### Q22. 나이에 따른 소인 판단
나이 `age`를 입력받아 20세 이상이면 `"Adult"`, 그렇지 않으면 `"Minor"` 문자열을 리턴하는 함수 `get_age_group(age)`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def get_age_group(age):
    return "Adult" if age >= 20 else "Minor"</pre>
</details>

### Q23. 화폐 단위 환산 함수
금액 `won`을 받아 천 단위 콤마가 붙은 문자열로 변환하고 끝에 `"원"`을 붙여 리턴하는 함수 `format_currency(won)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def format_currency(won):
    return f"{won:,}원"</pre>
</details>

### Q24. 소수점 강제 반올림 자릿수 지정
실수 `val`과 소수점 자릿수 `digits`를 받아 반올림해 리턴하는 함수 `round_val(val, digits=2)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def round_val(val, digits=2):
    return round(val, digits)</pre>
</details>

### Q25. 팩토리얼 기본 반복 함수
반복문을 사용하여 1부터 `n`까지 누적해서 곱한 값을 반환하는 함수 `factorial_iterative(n)`을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def factorial_iterative(n):
    res = 1
    for i in range(1, n+1):
        res *= i
    return res</pre>
</details>

### Q26. 소수(Prime) 유무 판별 함수
입력 수 `n`이 소수이면 `True`, 아니면 `False`를 리턴하는 함수 `is_prime(n)`을 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True</pre>
</details>

### Q27. 공통 원소 확인 함수
두 리스트 `lst1`, `lst2`를 매개변수로 받아 두 리스트에 공통으로 들어있는 원소들의 리스트를 반환하는 함수 `find_commons(lst1, lst2)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def find_commons(lst1, lst2):
    return list(set(lst1) & set(lst2))</pre>
</details>

### Q28. 2차원 리스트의 전체 합산 함수
2차원 리스트 `grid`를 전달받아 그 안의 모든 숫자의 총합을 계산해 리턴하는 함수 `sum_grid(grid)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def sum_grid(grid):
    return sum(sum(row) for row in grid)</pre>
</details>

### Q29. 대문자 치환 카운팅 리턴
문자열 `s`를 인자로 받아 전부 대문자로 변경한 값과, 기존 문자열 내 소문자 알파벳의 개수를 튜플 쌍으로 리턴하는 함수 `upper_info(s)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def upper_info(s):
    lower_cnt = sum(1 for c in s if c.islower())
    return s.upper(), lower_cnt</pre>
</details>

### Q30. 윤년 판단 연계 함수
연도 `year`를 입력받아 윤년이면 `True`, 평년이면 `False`를 반환하는 함수 `is_leap_year(year)`를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)</pre>
</details>

---

### Q31 ~ Q55: 가변 매개변수 (*args, **kwargs) 활용
### Q31. 위치 가변 매개변수 선언
전달받는 인자의 개수 제한 없이 튜플 형태로 취합하는 파라미터 선언 기호 `*`를 포함한 가변 매개변수 명칭을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># *args (Asterisk 기호를 변수명 앞에 붙입니다.)</pre>
</details>

### Q32. 가변 인자 합산기
인자로 정수를 임의 개수 전달받아 모두 더해주는 함수 `sum_args(*args)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def sum_args(*args):
    return sum(args)

print(sum_args(1, 2, 3, 4)) # 10</pre>
</details>

### Q33. 가변 인자 중 최댓값 구하기
여러 실수를 인자로 전달받아 그 중 가장 큰 값을 반환하는 함수 `max_args(*args)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def max_args(*args):
    if not args:
        return None
    return max(args)</pre>
</details>

### Q34. 키워드 가변 매개변수 선언
전달받는 인자들을 키-값(Key-Value) 쌍의 딕셔너리 형태로 덤프 취합하는 파라미터 선언 기호를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># **kwargs (Double Asterisk 기호를 변수명 앞에 붙입니다.)</pre>
</details>

### Q35. 키워드 인자 출력 함수
딕셔너리 형태로 인자를 전달받아 줄 단위로 "key: value" 형식으로 콘솔에 출력하는 함수 `show_kwargs(**kwargs)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def show_kwargs(**kwargs):
    for k, v in kwargs.items():
        print(f"{k}: {v}")</pre>
</details>

### Q36. 필수 매개변수와 가변 매개변수의 혼용
첫 번째 인자는 무조건 필수 매개변수 `title`로 받고, 두 번째부터는 가변 매개변수 `*args`로 받아 본문 내용을 출력하는 함수를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def print_report(title, *args):
    print(f"[{title}]")
    for item in args:
        print("-", item)</pre>
</details>

### Q37. 혼용 선언 시 순서 관계
`def func(**kwargs, *args):` 처럼 키워드 가변 인자 기호를 일반 가변 인자 기호보다 앞에 두면 실행 시 에러가 나는지 여부를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 에러가 발생합니다. 반드시 *args가 **kwargs보다 앞에 정의되어야 합니다.</pre>
</details>

### Q38. 호출 시 튜플 언패킹 전달 (*)
튜플 `t = (1, 2, 3)`을 함수 `def func(a, b, c):` 에 각각 매핑되도록 호출부에서 언패킹하여 전달하는 기호를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>t = (1, 2, 3)
# func(*t) 형태로 호출합니다.</pre>
</details>

### Q39. 호출 시 딕셔너리 언패킹 전달 (**)
딕셔너리 `d = {"a": 1, "b": 2}`를 함수 `def func(a, b):`에 매핑되도록 호출부에서 언패킹 기호를 붙여 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1, "b": 2}
# func(**d) 형태로 호출합니다.</pre>
</details>

### Q40. 가변 인자의 평균 구하기
전달되는 인자의 평균값을 계산해 리턴하되, 전달 인자가 없으면 0.0을 리턴하는 함수 `mean_args(*args)`를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def mean_args(*args):
    if not args:
        return 0.0
    return sum(args) / len(args)</pre>
</details>

### Q41. 키워드 가변 인자 내 특정 키 값 검색
`**kwargs`를 받아 내부 딕셔너리에 `"port"` 키가 들어있으면 그 값을 리턴하고, 없으면 기본 포트 `5432`를 리턴하는 함수 `get_port(**kwargs)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def get_port(**kwargs):
    return kwargs.get("port", 5432)</pre>
</details>

### Q42. 가변 인수 문자열 필터 결합
가변 문자열 인자 `*args`들을 전달받아 단어 길이가 5자 이상인 것들만 콤마로 연결해 하나의 대문자 문자열로 반환하는 함수를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def join_long_words(*args):
    longs = [w.upper() for w in args if len(w) >= 5]
    return ", ".join(longs)</pre>
</details>

### Q43. 딕셔너리 형태의 설정을 문자열 환경설정으로 출력
`**kwargs`로 속성들을 받아 `key=value` 형태의 데이터 라인들을 지닌 텍스트로 합쳐 리턴하는 함수를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def make_config_lines(**kwargs):
    lines = [f"{k}={v}" for k, v in kwargs.items()]
    return "\n".join(lines)</pre>
</details>

### Q44. 모든 종류 매개변수 결합 골격
일반 인자 `x`, 기본값 인자 `y=1`, 가변 인자 `*args`, 키워드 가변 인자 `**kwargs`가 한 함수에 선언되는 올바른 순서를 나열하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def complex_func(x, y=1, *args, **kwargs):
    pass</pre>
</details>

### Q45. args의 빈 가변인수 자료형 타입
호출 시 인자를 아무것도 넘기지 않았을 때, `*args` 매개변수가 받아들이는 빈 컨테이너의 실제 자료형 종류는 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># 빈 튜플(Tuple) 자료형인 () 이 바인딩됩니다.</pre>
</details>

### Q46. kwargs의 빈 가변인수 자료형 타입
호출 시 키워드 인자를 아무것도 넘기지 않았을 때, `**kwargs`가 가지는 빈 컨테이너 자료형 종류는 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># 빈 딕셔너리(Dict) 자료형인 {} 가 바인딩됩니다.</pre>
</details>

### Q47. 전달받은 튜플 인자 개수 카운팅 함수
`*args`로 인자들을 받아 총 전달된 인자의 종류 개수를 리턴하는 함수를 한 줄로 선언하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def count_args(*args):
    return len(args)</pre>
</details>

### Q48. 키워드 인수들의 키(Key) 정렬 목록 반환
`**kwargs`로 옵션을 받아 들어온 인자들의 키(Key)명을 알파벳순으로 정렬한 리스트를 리턴하는 함수를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def get_sorted_keys(**kwargs):
    return sorted(kwargs.keys())</pre>
</details>

### Q49. 특정 필수 키워드 지정 매개변수 (Keyword-Only Arguments)
일반 매개변수들 뒤에 `*` 단독 기호를 선언하고 그 뒤에 배치된 파라미터들은 반드시 키명을 명시해서만 호출 가능하도록 제어하는 함수 구조를 테스트하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def connection(host, *, timeout=30):
    print(host, timeout)

# connection("localhost", 10) -> 에러 발생
connection("localhost", timeout=10) # 정상 실행</pre>
</details>

### Q50. 가변 인자의 중복 원소 제거 집합 반환
`*args` 정수 여러 개를 받아 중복이 없는 고유 값들의 세트(Set) 집합을 리턴하는 함수 `unique_args(*args)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def unique_args(*args):
    return set(args)</pre>
</details>

---

### Q51 ~ Q75: 람다(Lambda) 및 map/filter/reduce 함수
### Q51. 람다 함수 선언
두 수를 받아 더한 값을 반환하는 익명 함수(lambda) 식을 작성하고 실행해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>add_lambda = lambda x, y: x + y
print(add_lambda(10, 20)) # 30</pre>
</details>

### Q52. 람다 단일 인수 제곱식
인수 `x`를 받아 제곱한 값을 리턴하는 람다식을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>square = lambda x: x**2</pre>
</details>

### Q53. 람다 삼항 조건식
인수 `n`을 받아 0 이상이면 `"Positive"`, 그렇지 않으면 `"Negative"`를 리턴하는 람다식을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>check_num = lambda n: "Positive" if n >= 0 else "Negative"</pre>
</details>

### Q54. map 함수를 이용한 리스트 원소 형변환
실수 리스트 `floats = [1.5, 2.7, 3.9]`의 모든 원소를 정수형으로 일괄 형변환하는 map 내장 함수 구문을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>floats = [1.5, 2.7, 3.9]
ints = list(map(int, floats))
print(ints) # [1, 2, 3]</pre>
</details>

### Q55. map과 람다식을 결합한 가공
리스트 `nums = [1, 2, 3]`의 각 원소에 10을 곱해 새로운 리스트 `[10, 20, 30]`을 한 줄로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>nums = [1, 2, 3]
res = list(map(lambda x: x * 10, nums))
print(res)</pre>
</details>

### Q56. filter 함수를 이용한 양수 필터링
리스트 `nums = [1, -2, 3, -4]`에서 양수만 걸러내어 리스트를 재생성하는 filter와 lambda 구문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>nums = [1, -2, 3, -4]
positives = list(filter(lambda x: x > 0, nums))
print(positives) # [1, 3]</pre>
</details>

### Q57. filter를 이용한 짝수 필터링
1부터 20까지 숫자 리스트에서 짝수만 filter 구문으로 수집하세요.

<details><summary><b>정답 보기</b></summary>
<pre>evens = list(filter(lambda x: x % 2 == 0, range(1, 21)))
print(evens)</pre>
</details>

### Q58. sorted 정렬 키에 람다식 매핑 (1차 기준)
튜플 리스트 `scores = [("김", 80), ("이", 95), ("박", 70)]`가 있을 때 점수가 낮은 사람순으로 정렬하는 sorted 구문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>scores = [("김", 80), ("이", 95), ("박", 70)]
sorted_list = sorted(scores, key=lambda x: x[1])
print(sorted_list)</pre>
</details>

### Q59. sorted 정렬 키에 람다식 매핑 (내림차순)
Q58의 `scores` 리스트를 점수가 높은 사람순(내림차순)으로 람다식 키를 사용해 정렬하세요.

<details><summary><b>정답 보기</b></summary>
<pre>scores = [("김", 80), ("이", 95), ("박", 70)]
sorted_list_desc = sorted(scores, key=lambda x: x[1], reverse=True)
print(sorted_list_desc)</pre>
</details>

### Q60. 누적 집계 계산 함수 (reduce)
`functools` 모듈의 `reduce` 함수를 호출하여 리스트 `[1, 2, 3, 4]`의 모든 원소를 누적 곱한 값(`24`)을 한 줄로 계산해 내세요.

<details><summary><b>정답 보기</b></summary>
<pre>from functools import reduce
nums = [1, 2, 3, 4]
prod = reduce(lambda x, y: x * y, nums)
print(prod) # 24</pre>
</details>

### Q61. 문자열 리스트 내 대문자 변환 map
리스트 `words = ["hq", "st"]`를 모두 대문자로 변경하는 map 구문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>words = ["hq", "st"]
uppers = list(map(lambda x: x.upper(), words))
print(uppers)</pre>
</details>

### Q62. 문자열 리스트 공백 제거 map
단어 리스트 `words = ["  A ", " B  ", " C "]`의 좌우 공백을 일괄 strip() 치환하는 map 구문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>words = ["  A ", " B  ", " C "]
cleaned = list(map(lambda x: x.strip(), words))
print(cleaned)</pre>
</details>

### Q63. 특정 단어가 포함된 문자열 필터
리스트 `logs = ["[INFO] OK", "[ERROR] Null", "[INFO] Success"]`에서 `"[INFO]"`가 들어간 로그들만 filter 함수로 걸러내세요.

<details><summary><b>정답 보기</b></summary>
<pre>logs = ["[INFO] OK", "[ERROR] Null", "[INFO] Success"]
infos = list(filter(lambda x: "[INFO]" in x, logs))
print(infos)</pre>
</details>

### Q64. 두 개의 리스트 원소 덧셈 map
두 개의 리스트 `a = [1, 2, 3]`, `b = [10, 20, 30]`의 대응되는 자릿수 원소끼리 더하여 `[11, 22, 33]`을 만드는 map 문장을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = [1, 2, 3]
b = [10, 20, 30]
res = list(map(lambda x, y: x + y, a, b))
print(res)</pre>
</details>

### Q65. 빈 문자열 필터링
문자열 리스트 `data = ["A", "", "B", " ", "C"]`에서 공백을 제외하고 유의미한 알파벳이 들어있는 문자열만 filter로 걸러내세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = ["A", "", "B", " ", "C"]
filtered = list(filter(lambda x: x.strip() != "", data))
print(filtered) # ['A', 'B', 'C']</pre>
</details>

---

### Q66 ~ Q80: 변수 Scope (지역/전역) 및 고급 함수 기법
### Q66. 전역 변수와 지역 변수의 개념
함수 바깥에 정의된 변수와 함수 내부에 정의된 변수의 가시성(Scope) 범위의 명칭을 각각 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 전역 변수(Global Variable)와 지역 변수(Local Variable)입니다.</pre>
</details>

### Q67. 함수 안에서 전역 변수 직접 읽기
함수 내부에서 바깥의 전역 변수 `global_var = 10`을 특별한 키워드 선언 없이 단순히 출력할 수 있나요?

<details><summary><b>정답 보기</b></summary>
<pre># 네, 읽기(Read) 작업은 키워드 선언 없이 전역 변수를 바로 가져와 호출할 수 있습니다.</pre>
</details>

### Q68. 전역 변수 수정 키워드 (global)
함수 내에서 전역 변수 `count = 0` 값을 1씩 증가시키려고 누적 연산을 할 때, 함수 선언 맨 윗부분에 명시해야 하는 전역 호출 키워드는 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># global count 와 같이 전역 변수임을 선언해야 합니다. 선언 없이 대입 연산을 시도하면 로컬 변수로 오인되어 에러가 납니다.</pre>
</details>

### Q69. 중첩 함수 내 중간 Scope 변수 제어 (nonlocal)
함수 내부의 중첩 함수(Inner Function)에서 부모 함수(Outer Function)의 지역 변수를 직접 갱신하려 할 때 선언하는 중간 수준 Scope 키워드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># nonlocal 키워드를 변수명 앞에 붙여 선언합니다.</pre>
</details>

### Q70. 클로저 (Closure) 개념
부모 함수의 실행이 종료된 후에도, 부모 함수 내부 지역 변수들의 상태 정보를 그대로 기억하고 참조 상태를 유지할 수 있는 중첩 함수 구조를 가리키는 프로그래밍 기법명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 클로저 (Closure) 기법입니다.</pre>
</details>

### Q71. 클로저를 활용한 카운터 함수
숫자 카운트를 1씩 늘려가며 반환하는 클로저 함수 골격을 구현해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>def make_counter():
    cnt = 0
    def counter():
        nonlocal cnt
        cnt += 1
        return cnt
    return counter

my_counter = make_counter()
print(my_counter()) # 1
print(my_counter()) # 2</pre>
</details>

### Q72. 일급 객체 (First-Class Object)로서의 함수
파이썬에서 함수는 변수에 대입하거나 다른 함수의 인자로 전달하고 리턴값으로 사용할 수 있습니다. 이러한 속성을 지닌 객체 단어를 무엇이라 하나요?

<details><summary><b>정답 보기</b></summary>
<pre># 일급 객체 (First-Class Object) 또는 일급 함수라고 부릅니다.</pre>
</details>

### Q73. 데코레이터 (Decorator) 기초
데코레이터 문법을 사용하여 본래 함수가 실행되기 전 `"--- Start ---"`, 실행 후 `"--- End ---"` 문을 꾸며서 일괄 출력해주는 함수 래퍼 구조를 작성해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>def my_decorator(func):
    def wrapper():
        print("--- Start ---")
        func()
        print("--- End ---")
    return wrapper

@my_decorator
def core_job():
    print("핵심 비즈니스 로직 실행")

core_job()</pre>
</details>

### Q74. 람다식 다중 매핑 조건 정렬
리스트 `data = [{"code": "A", "price": 10}, {"code": "B", "price": 5}]`가 있을 때 단가 `price`가 큰 순서대로 내림차순 정렬하는 sorted 구문을 람다로 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = [{"code": "A", "price": 10}, {"code": "B", "price": 5}]
res = sorted(data, key=lambda x: x["price"], reverse=True)
print(res)</pre>
</details>

### Q75. None 리턴 함수
return문 없이 연산만 수행하고 마치는 함수가 내부적으로 호출부로 돌려주는 반환 자료형 값은 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># None 값을 암묵적으로 반환합니다.</pre>
</details>

---

### Q76 ~ Q100: 재귀 함수 및 실무 함수 디자인 문제
### Q76. 재귀 함수 (Recursion) 기본 개념
함수가 함수 본문 내부에서 자기 자신을 다시 호출하여 반복적인 문제를 해결하는 프로그래밍 정의 기법을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 재귀 함수 (Recursive Function) 입니다.</pre>
</details>

### Q77. 재귀 함수 필수 기저 조건 (Base Case)
재귀 함수를 구현할 때 무한 루프에 빠져서 StackOverflow(파이썬은 RecursionError)가 발생하는 것을 막기 위해 반드시 설계해야 하는 탈출 지점을 가리키는 용어를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 기저 조건 (Base Case 또는 기저 대입 조건) 이라고 합니다.</pre>
</details>

### Q78. 재귀 함수를 이용한 팩토리얼 계산
재귀 호출을 사용하여 정수 `n` 팩토리얼 값을 구하는 함수 `factorial(n)`을 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)</pre>
</details>

### Q79. 재귀 함수를 이용한 피보나치 수열
재귀 호출을 사용하여 피보나치 수열의 `n`번째 항 값을 반환하는 함수 `fibonacci(n)`을 설계하세요 (1번째 항: 1, 2번째 항: 1).

<details><summary><b>정답 보기</b></summary>
<pre>def fibonacci(n):
    if n <= 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)</pre>
</details>

### Q80. 재귀 함수를 이용한 리스트 원소 총합 구하기
재귀 호출을 사용하여 숫자 리스트 `lst` 내부 모든 원소의 합을 구하는 함수 `sum_recursive(lst)`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def sum_recursive(lst):
    if not lst:
        return 0
    return lst[0] + sum_recursive(lst[1:])</pre>
</details>

### Q81. 재귀 함수의 최대 호출 한계 설정 확인
파이썬의 기본 최대 재귀 호출 깊이 한계값을 조회하기 위해 `sys` 모듈에서 호출하는 메소드명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import sys
print(sys.getrecursionlimit())</pre>
</details>

### Q82. 최대 호출 깊이 강제 상향 설정
기본 1000회 내외로 묶여 있는 파이썬 재귀 한계를 임의로 5000회로 확대 설정하는 sys 모듈의 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import sys
sys.setrecursionlimit(5000)</pre>
</details>

### Q83. 재귀를 이용한 이진수 변환 함수
10진수 정수를 입력받아 2진수 형태의 문자열로 변환하여 반환하는 재귀 함수 `dec_to_bin(n)`을 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def dec_to_bin(n):
    if n == 0:
        return ""
    return dec_to_bin(n // 2) + str(n % 2)</pre>
</details>

### Q84. 파일 디렉토리 트리 순회와 재귀 관계
컴퓨터 디스크 폴더 밑의 모든 하위 폴더와 파일 목록을 순차적으로 끝까지 파고들어 전수 스캔할 때 재귀 함수가 주로 사용되는 논리적 타당성을 설명하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 폴더 구조는 트리(Tree) 계층 구조 형태를 띠므로, 자식 디렉토리 목록을 다시 부모 디렉토리 검색용 함수에 전달하여 반복 탐색하는 재귀 호출 형태가 논리적으로 가장 간결하고 정확하게 동작합니다.</pre>
</details>

### Q85. 람다식 다차원 정렬 2차 연계
튜플 리스트 `students = [("김", 3, 90), ("이", 2, 95), ("박", 3, 85)]`가 있을 때 1차 기준 학년(2번 필드) 오름차순, 2차 기준 성적(3번 필드) 내림차순으로 정렬하는 구문을 람다로 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>students = [("김", 3, 90), ("이", 2, 95), ("박", 3, 85)]
res = sorted(students, key=lambda x: (x[1], -x[2]))
print(res)</pre>
</details>

### Q86. filter를 이용한 None/빈값 일괄 정제
리스트 `lst = ["OK", None, "WARN", ""]`에서 유효하지 않은 `None`과 빈 문자열을 filter의 lambda 조건문을 사용하지 않고 단독으로 정제하여 `['OK', 'WARN']`을 만드는 간결한 팁을 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = ["OK", None, "WARN", ""]
# None을 filter의 함수 인자로 전달하면 원소의 Truthy 여부만 평가하여 참인 값만 살려냅니다.
cleaned = list(filter(None, lst))
print(cleaned) # ['OK', 'WARN']</pre>
</details>

### Q87. 가변 인자의 인자 분배 패싱
함수 `outer(*args)` 가 전달받은 가변인수들을 다른 함수 `inner(a, b)`에 낱개 인자로 그대로 해체 전달하고자 할 때, `inner` 호출문에 적용하는 인수 전달 방식을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># inner(*args) 와 같이 별표 기호를 매개변수 앞에 붙여 호출합니다.</pre>
</details>

### Q88. 람다식 문자 필터링
문자열 리스트 `data = ["NC0002", "NC0007", "HQ0001"]`에서 `"NC"`로 시작하는 매장코드들만 filter와 람다를 사용해 추출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = ["NC0002", "NC0007", "HQ0001"]
nc_shops = list(filter(lambda x: x.startswith("NC"), data))
print(nc_shops)</pre>
</details>

### Q89. 딕셔너리 값들의 합계를 구하는 함수
딕셔너리를 인자로 받아 내부 수치 데이터 밸류들의 합계를 리턴하는 함수 `sum_dict_values(d)`를 한 줄짜리 함수로 선언해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>def sum_dict_values(d):
    return sum(d.values())</pre>
</details>

### Q90. 문자열 자릿수들의 숫자 판별 람다식
텍스트 `"123a"`가 전부 숫자로 이루어졌는지 검증하여 Boolean을 반환하는 익명 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>is_numeric = lambda s: s.isdigit()
print(is_numeric("123a")) # False</pre>
</details>

### Q91. 람다식을 이용한 특정 자릿수 패딩
정수 `n`을 인자로 받아 3자리 0 패딩 문자열(예: `5` $\rightarrow$ `"005"`)을 만들어주는 람다식을 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>pad3 = lambda n: str(n).zfill(3)
print(pad3(5)) # 005</pre>
</details>

### Q92. 람다식을 이용한 두 값 크기 비교
두 수 `x`, `y`를 받아 더 큰 값을 리턴하는 람다식을 삼항 연산자와 조합해 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>get_max = lambda x, y: x if x > y else y
print(get_max(15, 22)) # 22</pre>
</details>

### Q93. map 함수를 활용한 리스트 일괄 반올림
실수형 리스트 `rates = [0.123, 0.456, 0.789]`의 원소들을 모두 소수점 둘째 자리까지 반올림 가공하는 map 문장을 람다식과 결합해 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>rates = [0.123, 0.456, 0.789]
rounded = list(map(lambda x: round(x, 2), rates))
print(rounded)</pre>
</details>

### Q94. map 함수를 활용한 딕셔너리 리스트 키 값 변환
리스트 `users = [{"name": "A"}, {"name": "B"}]`에서 이름값만 일괄 추출하여 문자 리스트 `['A', 'B']`로 가공하는 map 구문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>users = [{"name": "A"}, {"name": "B"}]
names = list(map(lambda x: x["name"], users))
print(names)</pre>
</details>

### Q95. 람다식 문자 결합
두 단어를 입력받아 하이픈(-)으로 이어주는 람다식을 작성해 테스트해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>join_hyphen = lambda w1, w2: f"{w1}-{w2}"
print(join_hyphen("admin", "system"))</pre>
</details>

### Q96. 팩토리얼 재귀 한계 오류 대책
재귀 호출 팩토리얼 함수에서 대단히 큰 수(예: 100000)를 전달 시 `RecursionError`가 발생해 실행이 뻗어버릴 때 사용할 수 있는 대체 구현 원리는 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># 재귀 호출 대신 반복문(for/while)으로 구현하여 스택 오버플로우를 예방하거나, 메모이제이션(Dynamic Programming) 기법을 사용해 연산 횟수를 줄입니다.</pre>
</details>

### Q97. 리스트 내 원소들의 글자 길이에 따른 필터링
단어 리스트 `words = ["hq", "sales", "dashboard", "st"]`에서 글자 길이가 3 초과 7 미만인 단어들만 걸러내는 filter 식을 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>words = ["hq", "sales", "dashboard", "st"]
res = list(filter(lambda w: 3 < len(w) < 7, words))
print(res) # ['sales']</pre>
</details>

### Q98. 복합 람다 정렬 사전 대소문자 무시
단어 리스트 `words = ["Apple", "banana", "Cherry"]`를 대소문자 구분 없이 순수 사전적 알파벳 순서대로 정렬하는 sorted 구문을 람다와 함께 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>words = ["Apple", "banana", "Cherry"]
res = sorted(words, key=lambda x: x.lower())
print(res) # ['Apple', 'banana', 'Cherry']</pre>
</details>

### Q99. 재귀 호출로 리스트 원소 역순 출력
리스트 `[1, 2, 3]`을 인자로 받아 뒤에서부터 역순인 `3`, `2`, `1` 순서로 재귀적으로 출력하는 함수 `print_reverse(lst)`를 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def print_reverse(lst):
    if not lst:
        return
    print(lst[-1])
    print_reverse(lst[:-1])</pre>
</details>

### Q100. 카테고리 4 종합 문제
사용자 정보 리스트 `users = [{"id": "admin", "fail": 2}, {"id": "shop1", "fail": 5}, {"id": "shop2", "fail": 1}]`가 있습니다.
1. 로그인 실패 횟수 `fail` 수치가 3 이상인 사용자들을 filter와 람다를 사용해 걸러낸 리스트를 수집하고,
2. 수집된 대상자들의 아이디(`id`) 명칭 목록만을 map과 람다를 활용해 리스트로 최종 변환 출력하는 코드를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>users = [{"id": "admin", "fail": 2}, {"id": "shop1", "fail": 5}, {"id": "shop2", "fail": 1}]

# 1단계: fail >= 3 인 사용자들 수집
filtered_users = list(filter(lambda x: x["fail"] >= 3, users))

# 2단계: 해당 사용자들의 id만 추출
target_ids = list(map(lambda x: x["id"], filtered_users))

print(target_ids) # ['shop1']</pre>
</details>
