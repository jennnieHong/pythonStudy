# Python 실전 연습 문제집 - [카테고리 1] 기초 문법 및 변수 (100제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"Cat1"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py Cat1 Q1 True` (Q1 문제를 완료로 변경)


본 문제집은 파이썬의 가장 기초적인 문법, 출력, 기본 변수 연산, 문자열 조작, 데이터 타입 변환 및 포맷팅에 관한 100문제와 해설식 정답을 수록하고 있습니다.

---

### Q1 ~ Q10: 기초 화면 출력 및 주석
### Q1. "Python" 출력하기
"Python"을 출력하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print("Python")</pre>
</details>

### Q2. 줄바꿈 출력
두 줄에 걸쳐 "Hello"와 "World"를 각각 출력하는 단일 print문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print("Hello\nWorld")</pre>
</details>

### Q3. 구분자를 포함한 출력
세 단어 "A", "B", "C"를 하이픈(-)으로 연결하여 "A-B-C"로 출력하세요. (힌트: sep)

<details><summary><b>정답 보기</b></summary>
<pre>print("A", "B", "C", sep="-")</pre>
</details>

### Q4. 개행 없이 출력
두 개의 print문을 사용하되, 첫 번째 print문 뒤에 줄바꿈 없이 한 줄로 이어서 출력되게 하세요. (힌트: end)

<details><summary><b>정답 보기</b></summary>
<pre>print("Hello", end=" ")
print("World")</pre>
</details>

### Q5. 따옴표가 포함된 문자열 출력
화면에 'Python is "very" easy' 라고 큰따옴표가 포함된 문장을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print('Python is "very" easy')</pre>
</details>

### Q6. 한 줄 주석
코드 내에 "이것은 주석입니다"라는 한 줄 주석을 작성해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre># 이것은 주석입니다</pre>
</details>

### Q7. 여러 줄 주석
여러 줄 주석을 작성하는 기호 세 쌍을 활용해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>"""
여러 줄
주석입니다
"""</pre>
</details>

### Q8. 구분 기호가 들어간 경로 출력
"C:\Windows\System32" 처럼 역슬래시(\)가 깨지지 않고 그대로 출력되게 하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print("C:\\Windows\\System32")
# 또는 raw string 사용
print(r"C:\Windows\System32")</pre>
</details>

### Q9. 여러 번 문자열 반복 출력
문자열 "HMS"를 곱셈 기호를 활용하여 5번 연속해서 한 줄로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print("HMS" * 5)</pre>
</details>

### Q10. 빈 줄 출력
아무것도 출력하지 않고 한 줄 띄우는 print문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print()</pre>
</details>

---

### Q11 ~ Q30: 변수 선언 및 기본 대입 연산
### Q11. 변수 선언
변수 `x`에 정수 10을, `y`에 정수 20을 대입하고 두 변수의 합을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>x = 10
y = 20
print(x + y)</pre>
</details>

### Q12. 동시 선언 (Multiple Assignment)
두 변수 `a`와 `b`에 각각 100과 200을 한 줄의 코드로 대입해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 100, 200</pre>
</details>

### Q13. 변수 값 교환 (Swap)
`a = 5`, `b = 10` 일 때 임시 변수를 쓰지 않고 두 변수의 값을 서로 바꾸는 파이썬 전용 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 5, 10
a, b = b, a
print(a, b) # 10 5</pre>
</details>

### Q14. 누적 대입 연산자
변수 `score`에 50을 대입한 후, 10을 더하는 복합 대입 연산자 `+=`를 사용하여 값을 60으로 업데이트하세요.

<details><summary><b>정답 보기</b></summary>
<pre>score = 50
score += 10
print(score)</pre>
</details>

### Q15. 변수 삭제
변수 `temp = "data"`를 메모리에서 제거(삭제)하는 키워드를 작성하세요. (힌트: del)

<details><summary><b>정답 보기</b></summary>
<pre>temp = "data"
del temp</pre>
</details>

### Q16. 정수형 변수 선언
변수 `age`에 본인의 나이를 정수형으로 저장하고 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>age = 30
print(age)</pre>
</details>

### Q17. 실수형 변수 선언
변수 `height`에 본인의 키를 실수형으로 저장하고 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>height = 175.5
print(height)</pre>
</details>

### Q18. 논리형 변수 선언
변수 `is_open`에 참(`True`) 값을 저장하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>is_open = True
print(is_open)</pre>
</details>

### Q19. 변수의 타입 변경
정수형 변수 `x = 10`에 문자열 `"hello"`를 대입한 뒤 타입을 확인하세요. (파이썬의 동적 타입 특징 확인)

<details><summary><b>정답 보기</b></summary>
<pre>x = 10
x = "hello"
print(type(x)) # &lt;class 'str'&gt;</pre>
</details>

### Q20. 상수 선언 관례
파이썬에는 별도의 상수가 없습니다. 개발자 간의 약속으로 상수를 나타낼 때 변수명을 어떻게 명명하는지 관례를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># 변수명을 모두 대문자(예: MAX_CONNECTION = 10)로 작성하여 상수를 표기합니다.</pre>
</details>

### Q21. None 값 선언
아직 값이 결정되지 않은 변수 `result`에 빈 상태를 뜻하는 값을 대입하세요.

<details><summary><b>정답 보기</b></summary>
<pre>result = None
print(result)</pre>
</details>

### Q22. 문자열 결합 후 대입
`first = "Hyundai"`, `second = "Motors"`를 합쳐 변수 `full_name`을 만들고 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>first = "Hyundai"
second = "Motors"
full_name = first + " " + second
print(full_name)</pre>
</details>

### Q23. 변수 여러 개 곱하기
`width = 10`, `height = 5`를 정의하고 면적 `area`를 구하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>width, height = 10, 5
area = width * height
print(area)</pre>
</details>

### Q24. 변수를 이용한 몫 계산
`total_apple = 23`, `box_size = 5`일 때 상자당 들어가는 사과 개수(몫)를 `//` 연산자로 계산하여 변수 `apples_per_box`에 넣으세요.

<details><summary><b>정답 보기</b></summary>
<pre>total_apple, box_size = 23, 5
apples_per_box = total_apple // box_size
print(apples_per_box)</pre>
</details>

### Q25. 변수를 이용한 나머지 계산
Q24에서 남은 사과 개수(나머지)를 `%` 연산자로 계산하여 변수 `remains`에 넣으세요.

<details><summary><b>정답 보기</b></summary>
<pre>total_apple, box_size = 23, 5
remains = total_apple % box_size
print(remains)</pre>
</details>

### Q26. 소수점 나누기
`a = 5`, `b = 2` 일 때 소수점까지 나누는 `/` 연산 결과를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 5, 2
print(a / b) # 2.5</pre>
</details>

### Q27. 문자열 변수의 반복 덧셈
`star = "*"` 일 때 `star`를 10번 연속해서 출력하는 연산식을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>star = "*"
print(star * 10)</pre>
</details>

### Q28. 복합 대입 연산자 (-=)
변수 `balance = 10000`에서 2500을 빼는 복합 연산자 `-=`를 사용하여 최종 잔액을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>balance = 10000
balance -= 2500
print(balance)</pre>
</details>

### Q29. 복합 대입 연산자 (*=)
변수 `base = 3`에 5를 곱해 나가는 복합 연산자 `*=`를 적용해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>base = 3
base *= 5
print(base)</pre>
</details>

### Q30. 변수 바인딩 주소 확인 (id)
변수 `a = 10`과 `b = 10`이 가리키는 메모리 주소값(id)을 비교하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = 10
b = 10
print(id(a) == id(b)) # True (파이썬 소형 정수 캐싱)</pre>
</details>

---

### Q31 ~ Q55: 연산자 및 자료형 변환 (Type Casting)
### Q31. 정수로 형변환
실수 `x = 5.9`를 정수로 형변환하고 그 값을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>x = 5.9
print(int(x)) # 5 (소수점 이하 절사)</pre>
</details>

### Q32. 실수를 문자열로 변환
실수 `y = 12.34`를 문자열로 형변환하고 그 타입을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>y = 12.34
y_str = str(y)
print(type(y_str)) # &lt;class 'str'&gt;</pre>
</details>

### Q33. 문자열을 정수로 변환
문자열 `"123"`을 정수 `123`으로 형변환하여 변수 `num`에 저장하세요.

<details><summary><b>정답 보기</b></summary>
<pre>num = int("123")</pre>
</details>

### Q34. 문자열을 실수로 변환
문자열 `"3.1415"`를 실수로 형변환하여 변수 `pi`에 저장하세요.

<details><summary><b>정답 보기</b></summary>
<pre>pi = float("3.1415")</pre>
</details>

### Q35. 소수 정수 올림/내림 모듈 호출
실수 `x = 4.2`를 정수형 올림(5) 및 내림(4) 처리를 하기 위해 `math` 모듈의 함수를 호출하여 각각 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import math
x = 4.2
print(math.ceil(x))  # 올림: 5
print(math.floor(x)) # 내림: 4</pre>
</details>

### Q36. 논리형 변환 (Boolean Casting)
정수 `0`, 빈 문자열 `""`, 그리고 비어 있지 않은 문자열 `"abc"`를 각각 `bool()` 함수로 변환했을 때 결과를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(bool(0))      # False
print(bool(""))     # False
print(bool("abc"))  # True</pre>
</details>

### Q37. 반올림 함수 (round)
실수 `pi = 3.141592`를 소수점 셋째 자리까지 반올림하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>pi = 3.141592
print(round(pi, 3)) # 3.142</pre>
</details>

### Q38. 절대값 함수 (abs)
변수 `val = -45`를 절대값으로 변환하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>val = -45
print(abs(val)) # 45</pre>
</details>

### Q39. 거듭제곱 계산 (pow)
`pow()` 함수를 사용하여 2의 5제곱 값을 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(pow(2, 5)) # 32</pre>
</details>

### Q40. 비교 연산자 (같다, 다르다)
`a = 10`, `b = 20` 일 때 `a`와 `b`가 같지 않음을 뜻하는 비교 연산자를 활용한 Boolean 값을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 10, 20
print(a != b) # True</pre>
</details>

### Q41. 크기 비교 연산자
`a = 15`, `b = 15` 일 때 `a`가 `b`보다 크거나 같음을 비교하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 15, 15
print(a &gt;= b) # True</pre>
</details>

### Q42. 논리 연산자 AND
`x = True`, `y = False` 일 때 두 값이 모두 참인지 확인하는 논리 연산 코드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>x, y = True, False
print(x and y) # False</pre>
</details>

### Q43. 논리 연산자 OR
`x = True`, `y = False` 일 때 두 값 중 하나 이상이 참인지 확인하는 코드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>x, y = True, False
print(x or y) # True</pre>
</details>

### Q44. 논리 부정 NOT
`flag = True` 일 때 이 값을 반전(부정)시켜 출력하는 코드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>flag = True
print(not flag) # False</pre>
</details>

### Q45. 문자열을 리스트로 변환
문자열 `s = "HMS"`를 각 글자 단위 리스트 `['H', 'M', 'S']`로 변환하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "HMS"
print(list(s))</pre>
</details>

### Q46. 숫자형 변환 오류 대처 (ValueError)
문자열 `"abc"`를 정수로 변환 시도할 때 일어나는 예외(Exception)명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># ValueError 예외가 발생합니다.</pre>
</details>

### Q47. 사용자 입력(input) 데이터 타입 확인
`input()` 함수를 통해 사용자가 정수 `5`를 입력했을 때 저장되는 실제 데이터 타입은 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># 'str' (문자열) 타입으로 입력됩니다. 사칙연산을 수행하려면 int()로 변환해야 합니다.</pre>
</details>

### Q48. 입력된 숫자 문자열 합산
두 번의 input() 입력을 받아 각 문자열 숫자를 정수형으로 형변환하여 덧셈 결과를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>n1 = int(input("첫번째 숫자: "))
n2 = int(input("두번째 숫자: "))
print(n1 + n2)</pre>
</details>

### Q49. 실수 나눗셈 후 정수 변환
`a = 7`, `b = 3` 일 때 나눈 몫(실수형 결과)을 정수형으로 변환하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 7, 3
print(int(a / b)) # 2</pre>
</details>

### Q50. 몫과 나머지를 동시 계산 (divmod)
`divmod()` 함수를 사용하여 17을 5로 나눴을 때의 몫과 나머지를 튜플로 한 번에 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(divmod(17, 5)) # (3, 2)</pre>
</details>

### Q51. 삼항 연산자(Ternary Operator)
`score = 85` 일 때, 80점 이상이면 `"Pass"`, 아니면 `"Fail"` 문자열을 변수 `result`에 대입하는 한 줄 조건식을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>score = 85
result = "Pass" if score &gt;= 80 else "Fail"
print(result)</pre>
</details>

### Q52. 비트 연산자 AND (&amp;)
`a = 5` (이진수 0101), `b = 3` (이진수 0011) 일 때 비트 AND 연산 결과를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 5, 3
print(a &amp; b) # 1 (이진수 0001)</pre>
</details>

### Q53. 비트 연산자 OR (|)
Q52의 `a`와 `b`에 대해 비트 OR 연산 결과를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 5, 3
print(a | b) # 7 (이진수 0111)</pre>
</details>

### Q54. 16진수 문자열 변환
정수 `255`를 16진수 소문자 문자열(예: '0xff')로 변환하는 내장 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(hex(255)) # '0xff'</pre>
</details>

### Q55. 2진수 문자열 변환
정수 `10`을 2진수 문자열(예: '0b1010')로 변환하는 내장 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(bin(10)) # '0b1010'</pre>
</details>

---

### Q56 ~ Q80: 문자열 조작 및 연산
### Q56. 문자열 곱하기 연산
대시보드 하단 테두리를 그리기 위해 문자열 `"-"`을 50번 출력하는 연산식을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>print("-" * 50)</pre>
</details>

### Q57. 특정 인덱스 문자 추출
문자열 `s = "HMS_Sales"`에서 4번째 글자인 `'S'`를 추출해 출력하세요 (0부터 시작).

<details><summary><b>정답 보기</b></summary>
<pre>s = "HMS_Sales"
print(s[4])</pre>
</details>

### Q58. 문자열 뒷부분 슬라이싱
문자열 `file_name = "hq_sales_00005_TestCase.md"`에서 확장자 뒤 12글자인 `_TestCase.md`를 양수 슬라이싱 혹은 음수 슬라이싱으로 추출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>file_name = "hq_sales_00005_TestCase.md"
print(file_name[-12:])</pre>
</details>

### Q59. 문자열 앞부분 자르기
문자열 `code = "hq_dashboard"`에서 앞부분 `"hq"`를 추출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>code = "hq_dashboard"
print(code[0:2])</pre>
</details>

### Q60. 문자열 건너뛰며 슬라이싱
문자열 `s = "123456789"`에서 홀수 자릿수 문자 `"13579"`만 슬라이싱 문법을 사용해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "123456789"
print(s[::2])</pre>
</details>

### Q61. 문자열 뒤집기
문자열 `s = "REVERSE"`를 슬라이싱을 이용해 역순인 `"ESREVER"`로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "REVERSE"
print(s[::-1])</pre>
</details>

### Q62. 문자열 내 검색 (find)
문자열 `s = "Hq_Sales_00005_TestCase.md"`에서 `TestCase` 문자열이 시작하는 인덱스를 찾으세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "Hq_Sales_00005_TestCase.md"
print(s.find("TestCase")) # 15</pre>
</details>

### Q63. 없는 문자열 검색 시 find 반환값
`find()` 함수 사용 시 찾는 대상이 문자열 내에 존재하지 않는 경우 반환하는 값은 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># -1 을 반환합니다.</pre>
</details>

### Q64. 문자열 내 검색 (index)
`index()` 함수를 사용해 문자열 `s = "HMS"`에서 `'M'`의 위치를 찾으세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "HMS"
print(s.index("M")) # 1</pre>
</details>

### Q65. 없는 문자열 검색 시 index 결과
`index()` 함수 사용 시 찾는 대상이 존재하지 않을 경우 발생하는 파이썬 예외는 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># ValueError 예외가 발생합니다. (find와 가장 큰 차이)</pre>
</details>

### Q66. 문자열 시작 비교 (startswith)
매장코드 `code = "NC0007"`이 `"NC"`로 시작하는지 판단하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>code = "NC0007"
print(code.startswith("NC")) # True</pre>
</details>

### Q67. 문자열 종료 비교 (endswith)
파일명 `file = "Hq_Sales_TestCase.md"`가 `"_TestCase.md"`로 끝나는지 판단하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>file = "Hq_Sales_TestCase.md"
print(file.endswith("_TestCase.md")) # True</pre>
</details>

### Q68. 알파벳 유무 판단 (isalpha)
문자열 `s = "Admin"`이 알파벳으로만 구성되어 있는지 판단하는 메서드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "Admin"
print(s.isalpha()) # True</pre>
</details>

### Q69. 숫자 유무 판단 (isdigit)
문자열 `s = "12345"`가 정수형 숫자로만 구성되어 있는지 판단하는 메서드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "12345"
print(s.isdigit()) # True</pre>
</details>

### Q70. 대문자 판단 (isupper)
문자열 `s = "HMS"`가 전부 대문자인지 확인하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "HMS"
print(s.isupper()) # True</pre>
</details>

### Q71. 소문자 변환 (lower)
문자열 `s = "HQ_DASHBOARD"`를 소문자로 변환하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "HQ_DASHBOARD"
print(s.lower()) # hq_dashboard</pre>
</details>

### Q72. 첫 글자 대문자화 (capitalize)
소문자 단어 `word = "python"`의 첫 문자만 대문자로 변환하여 `"Python"`으로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>word = "python"
print(word.capitalize())</pre>
</details>

### Q73. 문자열 결합 (join)
리스트 `parts = ["hq", "sales", "00005"]`를 언더바(`_`) 기호로 합쳐 `"hq_sales_00005"` 문자열을 생성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>parts = ["hq", "sales", "00005"]
print("_".join(parts))</pre>
</details>

### Q74. 개행 단위 분할 (splitlines)
여러 줄의 문자열 `text = "Line1\nLine2\nLine3"`을 줄 단위로 분할하여 리스트를 만드는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>text = "Line1\nLine2\nLine3"
print(text.splitlines()) # ['Line1', 'Line2', 'Line3']</pre>
</details>

### Q75. 특정 문자 개수 세기 (count)
문자열 `log = "ERROR: info, ERROR: warning"`에서 `"ERROR"`가 등장하는 횟수를 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>log = "ERROR: info, ERROR: warning"
print(log.count("ERROR")) # 2</pre>
</details>

### Q76. 오른쪽 공백만 제거 (rstrip)
문자열 `data = "NC0007  \n"`에서 우측의 공백과 개행문자만 골라 제거하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = "NC0007  \n"
print(data.rstrip())</pre>
</details>

### Q77. 문자열 포매팅 (format 함수)
`"매장명: {}, 코드: {}"` 문자열에 `"본사_SHOP"`, `"NC0002"`를 매핑하는 `.format()` 구문을 사용해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>print("매장명: {}, 코드: {}".format("본사_SHOP", "NC0002"))</pre>
</details>

### Q78. format 함수 내 인덱스 및 키 활용
`"{1}의 매출액은 {0}원"` 포맷에 `5200000`과 `"NC0002"`를 매핑하여 "NC0002의 매출액은 5200000원"이 출력되게 하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print("{1}의 매출액은 {0}원".format(5200000, "NC0002"))</pre>
</details>

### Q79. f-string 소수점 자릿수 정밀 포매팅
실수 `rate = 8.33333`를 f-string 문법을 사용해 소수점 둘째 자리까지만 나타내어 `"8.33%"` 형식으로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>rate = 8.33333
print(f"{rate:.2f}%")</pre>
</details>

### Q80. 문자열 결합 시 TypeError 피하기
문자열 `"매출액: "`과 숫자 `5200000`을 형변환 연산자를 사용하여 안전하게 하나로 연결해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>sales = 5200000
print("매출액: " + str(sales))</pre>
</details>

---

### Q81 ~ Q100: 문자열 응용 및 1차 종합 문제
### Q81. 영수증 자릿수 맞추기 (zfill)
정수 `45`를 5자리 문자열로 만들되, 빈자리만큼 왼쪽에 0이 채워지도록 `"00045"`로 가공하세요.

<details><summary><b>정답 보기</b></summary>
<pre>num = 45
print(str(num).zfill(5))</pre>
</details>

### Q82. 문자열 정렬 및 공백 채우기 (rjust)
문자열 `"NC0002"`를 총 10자리 공간 안에서 우측 정렬하고, 나머지 빈 공간은 공백으로 둔 문자열을 반환하는 메소드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "NC0002"
print(s.rjust(10))</pre>
</details>

### Q83. 문자열 내 공백을 한글로 치환
문자열 `s = "A B C"`의 모든 공백을 없애서 `"ABC"`로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "A B C"
print(s.replace(" ", ""))</pre>
</details>

### Q84. 파일 확장자 검사 논리 OR
파일명 `file = "data.csv"`가 `".csv"` 혹은 `".xlsx"`로 끝나는지 endswith의 튜플 속성을 이용해 한 번에 판별하세요.

<details><summary><b>정답 보기</b></summary>
<pre>file = "data.csv"
print(file.endswith((".csv", ".xlsx"))) # True</pre>
</details>

### Q85. 아스키(ASCII) 코드 문자 변환 (chr)
정수 `65`를 대응하는 아스키 대문자 `'A'`로 변환하는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(chr(65)) # A</pre>
</details>

### Q86. 문자를 아스키 코드로 변환 (ord)
문자 `'a'`를 대응하는 정수 아스키 값 `97`로 변환하는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(ord('a')) # 97</pre>
</details>

### Q87. 문자열 중복 제거 (순서 보존 없는 세트 기법)
문자열 `s = "aaabbbccc"` 내 알파벳들의 중복을 없애고 고유 알파벳 집합 문자열을 만드세요 (순서는 보관하지 않아도 됨).

<details><summary><b>정답 보기</b></summary>
<pre>s = "aaabbbccc"
print("".join(set(s)))</pre>
</details>

### Q88. 문자열 존재 유무 논리 판단 (in)
텍스트 `"success"`가 문자열 `response = "Login success. welcome."` 내에 포함되어 있는지 판단하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>response = "Login success. welcome."
print("success" in response) # True</pre>
</details>

### Q89. 문자열 미포함 논리 판단 (not in)
텍스트 `"ERROR"`가 문자열 `log = "[INFO] Connection OK"` 에 포함되어 있지 않은지 판단하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>log = "[INFO] Connection OK"
print("ERROR" not in log) # True</pre>
</details>

### Q90. 문자열 곱셈을 이용한 라인 만들기
대시보드 구분을 위해 `"="`가 30개로 늘어선 문자열을 print문으로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print("=" * 30)</pre>
</details>

### Q91. 문자열 내의 특정 문자 존재 위치 복수 탐색
문자열 `s = "abaca"` 내에서 `'a'`의 개수를 세고, 첫 번째 `'a'`의 인덱스를 반환하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "abaca"
print("개수:", s.count("a"))  # 3
print("인덱스:", s.find("a")) # 0</pre>
</details>

### Q92. 문자열 슬라이싱 범위를 넘었을 때의 결과
문자열 `s = "HMS"`가 있을 때 `s[0:100]` 처럼 실제 인덱스 길이를 한참 넘은 범위를 지정하면 에러가 발생하는가요?

<details><summary><b>정답 보기</b></summary>
<pre># 에러가 발생하지 않고 전체 문자열 "HMS"를 안전하게 반환합니다.</pre>
</details>

### Q93. 여러 개의 변수 포맷 출력
`year = 2026`, `month = 7`, `day = 6` 일 때 f-string을 활용하여 `"2026-07-06"`으로 변환하되, 월과 일에 2자리 빈공간 0을 채우는 형식 코드를 작성하세요. (힌트: `:02d`)

<details><summary><b>정답 보기</b></summary>
<pre>year, month, day = 2026, 7, 6
print(f"{year}-{month:02d}-{day:02d}") # 2026-07-06</pre>
</details>

### Q94. 문자열 안의 모든 특수기호 유무 판단 (isalnum)
문자열 `s = "NC0007!"`이 알파벳 혹은 숫자로만 구성되어 있고 특수문자가 없는지 확인하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "NC0007!"
print(s.isalnum()) # False (느낌표 특수기호 포함)</pre>
</details>

### Q95. 문자열 슬라이싱 간격 역방향 지정
문자열 `s = "ABCDE"`에서 `s[4:1:-1]` 슬라이싱 결과를 주석으로 예측하고 실행하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "ABCDE"
print(s[4:1:-1]) # EDC (인덱스 4, 3, 2 역방향 스캔)</pre>
</details>

### Q96. 문자열 분해 후 결합 응용
날짜 문자열 `"2026/07/06"`에서 슬래시(`/`)를 대시(`-`) 기호로 변경하여 출력하세요 (replace 사용 제외).

<details><summary><b>정답 보기</b></summary>
<pre>date = "2026/07/06"
print("-".join(date.split("/")))</pre>
</details>

### Q97. 임의 자료형의 문자열 덤프 (repr)
문자열 `s = "Line1\nLine2"`를 이스케이프 개행 기호가 가시적으로 노출되는 상태(`'Line1\nLine2'`)로 덤프하여 출력하는 내장 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "Line1\nLine2"
print(repr(s))</pre>
</details>

### Q98. 복합 데이터 대입 연산
`a = b = c = 0` 과 같은 멀티 초기화 대입 방식을 사용해 변수를 초기화하고 3개 값을 한 줄로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = b = c = 0
print(a, b, c)</pre>
</details>

### Q99. 문자열 타입 여부 검증 (isinstance)
변수 `x = "HMS"`가 실제로 `str` 클래스의 인스턴스(문자열형)인지 확인하는 Boolean 내장 함수 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>x = "HMS"
print(isinstance(x, str)) # True</pre>
</details>

### Q100. 카테고리 1 종합 문제
사용자로부터 두 개의 숫자 문자열 `"150"`과 `"250"`을 입력받아(input 시뮬레이션), 둘을 정수로 변환하여 곱한 값에 천 단위 콤마를 붙여 `"곱한 금액: 37,500원"` 포맷 문자열로 최종 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>num1 = int("150")
num2 = int("250")
mult_result = num1 * num2
print(f"곱한 금액: {mult_result:,}원")</pre>
</details>
