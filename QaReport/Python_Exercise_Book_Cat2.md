# Python 실전 연습 문제집 - [카테고리 2] 조건문과 반복문 (100제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"Cat2"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py Cat2 Q1 True` (Q1 문제를 완료로 변경)


본 문제집은 파이썬의 조건문(`if`, `elif`, `else`), 다양한 반복문(`for`, `while`), 루프 제어(`break`, `continue`), 리스트 컴프리헨션(List Comprehension) 등 프로그램의 제어 흐름에 관한 100문제와 해설식 정답을 수록하고 있습니다.

---

### Q1 ~ Q25: 조건문 (if-elif-else) 기초 및 응용
### Q1. 단순 if 조건문
변수 `score = 85`가 80 이상이면 "우수"를 출력하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>score = 85
if score >= 80:
    print("우수")</pre>
</details>

### Q2. if-else 구조
변수 `score = 75`가 80 이상이면 "합격", 그렇지 않으면 "불합격"을 출력하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>score = 75
if score >= 80:
    print("합격")
else:
    print("불합격")</pre>
</details>

### Q3. 다중 분기 (if-elif-else)
변수 `num = 0`이 양수인지, 음수인지, 혹은 0인지 판별하여 각각 "양수", "음수", "0"을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>num = 0
if num > 0:
    print("양수")
elif num < 0:
    print("음수")
else:
    print("0")</pre>
</details>

### Q4. 짝수 홀수 판별
정수 `n = 13`이 짝수인지 홀수인지 `%` 연산자를 사용해 판별 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>n = 13
if n % 2 == 0:
    print("짝수")
else:
    print("홀수")</pre>
</details>

### Q5. 배수 판별
정수 `n = 15`가 3의 배수이면서 동시에 5의 배수인지 판별하는 조건문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>n = 15
if n % 3 == 0 and n % 5 == 0:
    print("3과 5의 공배수")</pre>
</details>

### Q6. 문자열 조건문 비교
권한 `role = "ROLE_HQ"`가 `"ROLE_ADMIN"` 혹은 `"ROLE_HQ"`에 해당하는 경우 "진입 허용", 그 외에는 "거부"를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>role = "ROLE_HQ"
if role == "ROLE_ADMIN" or role == "ROLE_HQ":
    print("진입 허용")
else:
    print("거부")</pre>
</details>

### Q7. 대소문자 무시 조건문 비교
입력받은 문자열 `answer = "Yes"`가 대소문자 구분 없이 `"yes"`에 해당하면 "승인"을 출력하세요. (힌트: `.lower()`)

<details><summary><b>정답 보기</b></summary>
<pre>answer = "Yes"
if answer.lower() == "yes":
    print("승인")</pre>
</details>

### Q8. 중첩 조건문 (Nested If)
`score = 92`, `attendance = 90` 일 때, `score`가 90 이상이고 `attendance`도 90 이상인 경우에만 "최우수"를 출력하는 중첩 조건문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>score, attendance = 92, 90
if score >= 90:
    if attendance >= 90:
        print("최우수")</pre>
</details>

### Q9. 리스트에 값 존재 여부 판단 (in)
매장코드 `code = "NC0007"`이 리스트 `stores = ["NC0002", "NC0007"]` 안에 있으면 "매장 발견"을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>code = "NC0007"
stores = ["NC0002", "NC0007"]
if code in stores:
    print("매장 발견")</pre>
</details>

### Q10. 리스트에 값 부재 판단 (not in)
사용자명 `user = "temp_user"`가 활성 사용자 딕셔너리 `active_users = {"admin": True}`에 존재하지 않는지 확인하는 조건식을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>user = "temp_user"
active_users = {"admin": True}
if user not in active_users:
    print("비활성 사용자")</pre>
</details>

### Q11. 학점 평점 분기
학점 `gpa = 3.8`에 대해 4.0 이상이면 "A", 3.0 이상 4.0 미만이면 "B", 그 외에는 "C"를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>gpa = 3.8
if gpa >= 4.0:
    print("A")
elif gpa >= 3.0:  # 3.0 이상 4.0 미만
    print("B")
else:
    print("C")</pre>
</details>

### Q12. 숫자 범위 동시 비교
변수 `x = 15`가 10 초과 20 미만인 조건을 파이썬 특유의 동시 비교식 `10 < x < 20` 형태로 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>x = 15
if 10 < x < 20:
    print("범위 내 존재")</pre>
</details>

### Q13. Boolean의 암묵적 평가
비어 있는 리스트 `arr = []`가 거짓(`False`)으로 평가됨을 이용해, 리스트가 비어 있을 때 "리스트가 비어 있습니다."를 출력하는 if문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = []
if not arr:
    print("리스트가 비어 있습니다.")</pre>
</details>

### Q14. 문자열 존재 여부 간결 판단
문자열 `s = "hello"`가 비어 있지 않은 참(`True`) 상태인지 `if s:` 문으로 확인하여 "문자열 있음"을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "hello"
if s:
    print("문자열 있음")</pre>
</details>

### Q15. 정수 0 평가
정수 `x = 0`일 때 `if x:`와 `if not x:` 중 어떤 블록이 동작하는지 테스트해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>x = 0
if not x:
    print("0은 거짓(False)으로 평가되므로 not x가 실행됩니다.")</pre>
</details>

### Q16. 3의 배수 및 짝수 판단
정수 `n`이 3의 배수이거나 짝수인지 판별하는 복합 조건문(`or`)을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>n = 9
if n % 3 == 0 or n % 2 == 0:
    print("3의 배수이거나 짝수")</pre>
</details>

### Q17. 삼항 연산자를 이용한 홀짝 출력
한 줄짜리 삼항 연산식 형태로 `n = 10` 일 때 `"Even"` 혹은 `"Odd"`를 출력하게 하세요.

<details><summary><b>정답 보기</b></summary>
<pre>n = 10
print("Even" if n % 2 == 0 else "Odd")</pre>
</details>

### Q18. 비밀번호 보안 강도 분기
`pwd_len = 10`, `has_special = True` 일 때, 패스워드 길이가 8 이상이고 특수문자가 포함된 경우 "강함", 그렇지 않으면 "약함"을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>pwd_len, has_special = 10, True
if pwd_len >= 8 and has_special:
    print("강함")
else:
    print("약함")</pre>
</details>

### Q19. 문자열 특정 문자 포함 여부 분기
파일명 `file = "invoice.pdf"`에 `"invoice"`가 들어있으면 "결제 청구서", 그렇지 않으면 "일반 문서"를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>file = "invoice.pdf"
if "invoice" in file:
    print("결제 청구서")
else:
    print("일반 문서")</pre>
</details>

### Q20. 윤년 체크 알고리즘
연도 `year = 2026`이 윤년인지 평년인지 판단하는 if-else 문을 구현하세요. (4로 나눠지고 100으로 안나눠지거나, 400으로 나눠짐)

<details><summary><b>정답 보기</b></summary>
<pre>year = 2026
if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
    print("윤년")
else:
    print("평년")</pre>
</details>

### Q21. None 변수 조건문
변수 `data = None` 일 때, `is` 키워드를 사용해 `data`가 `None`인지 판단하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = None
if data is None:
    print("데이터가 비어 있습니다.")</pre>
</details>

### Q22. 변수 타입 조건 검사
변수 `x = 100`이 정수형(`int`)인지 `type()` 비교문으로 검증하여 "정수"를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>x = 100
if type(x) is int:
    print("정수")</pre>
</details>

### Q23. 나이대별 요금 분기
나이 `age = 15` 일 때, 8세 미만 "무료", 8세~19세 "청소년 요금", 20세 이상 "일반 요금"을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>age = 15
if age < 8:
    print("무료")
elif 8 <= age <= 19:
    print("청소년 요금")
else:
    print("일반 요금")</pre>
</details>

### Q24. 리스트 요소 개수 비교
리스트 `log_list = ["a", "b", "c"]`의 크기(길이)가 3 이상이면 "로그 버퍼 경고"를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>log_list = ["a", "b", "c"]
if len(log_list) >= 3:
    print("로그 버퍼 경고")</pre>
</details>

### Q25. 딕셔너리 특정 키 값 유효성 체크
딕셔너리 `user = {"lock": "Y"}`일 때, `"lock"` 키에 해당하는 값이 `"Y"` 이면 "계정 잠김"을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>user = {"lock": "Y"}
if user.get("lock") == "Y":
    print("계정 잠김")</pre>
</details>

---

### Q26 ~ Q60: while 반복문 및 루프 제어 (break, continue)
### Q26. 1부터 5까지 출력 (while)
while 반복문을 사용하여 1부터 5까지 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>i = 1
while i <= 5:
    print(i)
    i += 1</pre>
</details>

### Q27. 5부터 1까지 역순 출력 (while)
while 반복문을 사용하여 5부터 1까지 카운트다운을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>i = 5
while i > 0:
    print(i)
    i -= 1</pre>
</details>

### Q28. 1부터 100까지 홀수의 합 (while)
while 루프를 사용하여 1부터 100까지 정수 중 홀수들의 총합을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>i = 1
total = 0
while i <= 100:
    if i % 2 != 0:
        total += i
    i += 1
print(total)</pre>
</details>

### Q29. 10의 배수 출력 (while)
10부터 50까지 10 단위로 증가시키며 값을 출력하는 while 루프를 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>i = 10
while i <= 50:
    print(i)
    i += 10</pre>
</details>

### Q30. 무한 루프 탈출 (break)
while True 무한 루프에서 `count`를 1씩 증가시키다가 `count == 5`가 되는 순간 루프를 중단(break)하고 빠져나오세요.

<details><summary><b>정답 보기</b></summary>
<pre>count = 1
while True:
    print(count)
    if count == 5:
        break
    count += 1</pre>
</details>

### Q31. 홀수만 건너뛰기 (continue)
while 루프 내에서 1부터 10까지 돌리되, 홀수인 경우 `continue`를 사용하여 출력하지 않고 짝수만 출력되게 하세요.

<details><summary><b>정답 보기</b></summary>
<pre>i = 0
while i < 10:
    i += 1
    if i % 2 != 0:
        continue
    print(i)</pre>
</details>

### Q32. 로그인 비밀번호 입력 시뮬레이션
올바른 비밀번호 `"qazwsx"`가 입력될 때까지 키보드로부터 비밀번호를 무한히 입력받고(input), 올바르게 입력되면 `"로그인 성공"` 출력 후 탈출하는 while 루프를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>correct_pw = "qazwsx"
while True:
    pwd = input("비밀번호 입력: ")
    if pwd == correct_pw:
        print("로그인 성공")
        break</pre>
</details>

### Q33. 리스트 pop을 이용한 순회
리스트 `jobs = ["task1", "task2", "task3"]`가 빌 때까지 `pop(0)`을 사용하여 원소를 하나씩 꺼내고 출력하는 while 루프를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>jobs = ["task1", "task2", "task3"]
while jobs:
    current = jobs.pop(0)
    print("처리:", current)</pre>
</details>

### Q34. 특정 조건을 만날 때까지 누적합
사용자로부터 정수를 계속 입력받아 누적하다가 `0`을 입력하는 순간 지금까지 더한 총합을 출력하고 탈출하는 코드를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>total = 0
while True:
    n = int(input("더할 수 입력 (0 입력시 종료): "))
    if n == 0:
        break
    total += n
print("최종 합:", total)</pre>
</details>

### Q35. 리스트 요소 제거 while 루프
리스트 `data = [1, 2, 3, 2, 4, 2]`에 들어있는 모든 `2`를 while문과 remove() 함수를 결합해 전부 제거하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = [1, 2, 3, 2, 4, 2]
while 2 in data:
    data.remove(2)
print(data) # [1, 3, 4]</pre>
</details>

### Q36. 1부터 10까지 3의 배수를 제외한 합
while 루프에서 1부터 10까지 정수 중 3의 배수를 제외하고 합산하는 코드를 continue를 사용해 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>i = 0
total = 0
while i < 10:
    i += 1
    if i % 3 == 0:
        continue
    total += i
print(total)</pre>
</details>

### Q37. 두 수의 최대공약수 (while)
유클리드 호제법을 사용해 `a = 48`, `b = 18` 의 최대공약수를 while문을 이용하여 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 48, 18
while b != 0:
    a, b = b, a % b
print("최대공약수:", a) # 6</pre>
</details>

### Q38. 피보나치 수열 기초 (while)
피보나치 수열의 첫 10개 항(0, 1, 1, 2, 3, 5, 8...)을 while 루프를 통해 차례대로 계산하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a, b = 0, 1
count = 0
while count < 10:
    print(a, end=" ")
    a, b = b, a + b
    count += 1</pre>
</details>

### Q39. 루프 정상 종료 확인 (while-else)
while-else 문을 사용하여 1부터 5까지 정상 종료했을 때 `"루프 완수"`가 출력되게 하세요. (break 미작동 시 else블록 수행)

<details><summary><b>정답 보기</b></summary>
<pre>i = 1
while i <= 5:
    print(i)
    i += 1
else:
    print("루프 완수")</pre>
</details>

### Q40. 문자열 탐색 및 문자 개수 제한 루프
문자열 `s = "abcde"`를 앞에서부터 한 글자씩 출력하다가 모음(`a`, `e`, `i`, `o`, `u`)의 등장 횟수가 2개가 넘으면 중단하는 while 루프를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "abcde"
idx = 0
vowel_cnt = 0
while idx < len(s):
    char = s[idx]
    if char in "aeiou":
        vowel_cnt += 1
    print(char)
    if vowel_cnt >= 2:
        break
    idx += 1</pre>
</details>

### Q41. 입력받은 단어 뒤집기 루프
사용자가 `"exit"`을 입력할 때까지 문자열을 계속 입력받아, 입력받은 단어를 역순으로 출력해주는 대화식 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>while True:
    word = input("단어 입력 (exit 종료): ")
    if word == "exit":
        break
    print("역순:", word[::-1])</pre>
</details>

### Q42. 1부터 10까지 곱 (while)
while 루프를 사용하여 1부터 10까지 모든 수의 누적 곱(Factorial 10)을 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>i = 1
result = 1
while i <= 10:
    result *= i
    i += 1
print(result)</pre>
</details>

### Q43. 특정 원소 인덱스 검색 (while)
리스트 `arr = ["A", "B", "C", "D"]`에서 `"C"`가 위치한 인덱스를 `while`문과 인덱스 번호를 1씩 증가시키는 탐색 코드로 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = ["A", "B", "C", "D"]
idx = 0
found_idx = -1
while idx < len(arr):
    if arr[idx] == "C":
        found_idx = idx
        break
    idx += 1
print("위치:", found_idx)</pre>
</details>

### Q44. 자릿수 더하기
정수 `n = 12345`가 주어졌을 때 while 루프와 `% 10` 연산 기법을 이용해 각 자릿수의 합(1+2+3+4+5)을 계산하세요.

<details><summary><b>정답 보기</b></summary>
<pre>n = 12345
total = 0
while n > 0:
    total += n % 10
    n = n // 10
print(total) # 15</pre>
</details>

### Q45. 이진 탐색 시뮬레이션 while 루프 조건
이진 탐색 알고리즘을 수행할 때 while 루프를 제어하는 일반적인 인덱스 크기 비교 조건 범위를 기술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># low <= high 일 때 동안 반복하도록 while low &lt;= high: 형태로 구성합니다.</pre>
</details>

### Q46. 3으로 계속 나누기
정수 `n = 100`이 1보다 클 동안 계속 3으로 나눈 몫으로 업데이트하고 그 과정을 출력하는 while 루프를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>n = 100
while n > 1:
    n = n // 3
    print(n)</pre>
</details>

### Q47. 난수 생성 맞추기 게임 기초 (while)
숫자 `7`을 정답으로 지정하고, 사용자가 입력한 수가 정답보다 크면 "Down", 작으면 "Up", 정답을 맞추면 "정답!" 출력 후 브레이크를 거는 게임 루프를 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>ans = 7
while True:
    guess = int(input("맞출 숫자 입력: "))
    if guess == ans:
        print("정답!")
        break
    elif guess > ans:
        print("Down")
    else:
        print("Up")</pre>
</details>

### Q48. 리스트 합산 100 초과 break
숫자 리스트 `arr = [10, 20, 30, 45, 5, 60]`의 값을 앞에서부터 하나씩 더하다가, 누적합이 100을 초과하는 순간 루프를 중지하고 당시의 누적합을 콘솔에 출력하는 while 루프를 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [10, 20, 30, 45, 5, 60]
idx = 0
total = 0
while idx < len(arr):
    total += arr[idx]
    if total > 100:
        break
    idx += 1
print("100 초과 시점 합:", total)</pre>
</details>

### Q49. 특정 패턴 문자열만 건너뛰기
리스트 `data = ["OK", "WARN", "OK", "ERROR", "OK"]`를 순회하며 `"ERROR"`가 등장하면 출력하지 않고 건너뛰는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = ["OK", "WARN", "OK", "ERROR", "OK"]
idx = 0
while idx < len(data):
    val = data[idx]
    idx += 1
    if val == "ERROR":
        continue
    print(val)</pre>
</details>

### Q50. 2의 거듭제곱 증가 루프
1부터 시작하여 2를 계속 곱해가며 `val`이 1000보다 작을 때까지 출력하는 while 루프를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>val = 1
while val < 1000:
    print(val)
    val *= 2</pre>
</details>

---

### Q51 ~ Q80: for 반복문 및 range 함수 활용
### Q51. 1부터 10까지 출력 (for)
`range()` 함수와 for문을 사용하여 1부터 10까지 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>for i in range(1, 11):
    print(i)</pre>
</details>

### Q52. 리스트 순회 (for)
리스트 `colors = ["red", "green", "blue"]`의 모든 요소를 for문으로 하나씩 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>colors = ["red", "green", "blue"]
for c in colors:
    print(c)</pre>
</details>

### Q53. range 간격 설정
1부터 10까지의 숫자 중 홀수만 for문과 range 간격 지정을 통해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>for i in range(1, 11, 2):
    print(i)</pre>
</details>

### Q54. range 역순 카운트다운
10부터 1까지 역순으로 카운트다운 숫자를 range()를 활용해 for문으로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>for i in range(10, 0, -1):
    print(i)</pre>
</details>

### Q55. 문자열 한 글자씩 스캔 (for)
문자열 `s = "HMS"`의 각 문자를 한 줄에 한 문자씩 순서대로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "HMS"
for char in s:
    print(char)</pre>
</details>

### Q56. 1부터 100까지 정수의 총합 (for)
for문을 사용하여 1부터 100까지 모든 수의 누적 합을 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>total = 0
for i in range(1, 101):
    total += i
print(total)</pre>
</details>

### Q57. 짝수만 합산하기 (for)
1부터 50까지 정수 중 짝수들의 총합만 구하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>total = 0
for i in range(2, 51, 2):
    total += i
print(total)</pre>
</details>

### Q58. 리스트 내부 원소들의 문자 길이 출력
리스트 `words = ["apple", "go", "banana"]`에서 각 단어의 길이를 구하여 차례대로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>words = ["apple", "go", "banana"]
for w in words:
    print(len(w))</pre>
</details>

### Q59. 튜플로 구성된 리스트 순회
튜플 리스트 `pairs = [(1, "A"), (2, "B"), (3, "C")]`를 for문으로 순회하며 인자 두 개를 각각 분리 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>pairs = [(1, "A"), (2, "B"), (3, "C")]
for num, char in pairs:
    print(f"숫자: {num}, 문자: {char}")</pre>
</details>

### Q60. 딕셔너리 키 순회 (for)
딕셔너리 `d = {"a": 10, "b": 20}`의 Key 목록을 루프를 돌며 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 10, "b": 20}
for k in d:
    print(k)</pre>
</details>

### Q61. 딕셔너리 값 순회 (for)
Q60의 딕셔너리 `d`에서 모든 Value 목록을 루프 돌며 출력하세요. (힌트: `.values()`)

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 10, "b": 20}
for val in d.values():
    print(val)</pre>
</details>

### Q62. 구구단 5단 출력
for문을 사용하여 구구단 5단 전체 식을 콘솔에 렌더링하세요.

<details><summary><b>정답 보기</b></summary>
<pre>for i in range(1, 10):
    print(f"5 x {i} = {5 * i}")</pre>
</details>

### Q63. 리스트에서 최댓값 직접 찾기
`max()` 내장 함수를 쓰지 않고, for문을 사용해 리스트 `nums = [17, 92, 5, 33, 56]` 내 최대값을 구하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>nums = [17, 92, 5, 33, 56]
max_val = nums[0]
for num in nums:
    if num > max_val:
        max_val = num
print("최대값:", max_val)</pre>
</details>

### Q64. 리스트에서 특정 값 개수 세기
`count()` 내장 메소드를 쓰지 않고, for문과 조건식을 사용해 리스트 `arr = [1, 2, 3, 2, 4, 2]` 에서 `2`가 몇 번 등장하는지 세어보세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [1, 2, 3, 2, 4, 2]
cnt = 0
for val in arr:
    if val == 2:
        cnt += 1
print("개수:", cnt)</pre>
</details>

### Q65. 리스트 요소들의 누적 곱 (Product)
리스트 `factors = [2, 3, 5, 7]`의 모든 원소를 곱한 곱셈 총액을 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>factors = [2, 3, 5, 7]
result = 1
for f in factors:
    result *= f
print(result)</pre>
</details>

### Q66. 2차원 리스트 플래팅 (Flatting)
중첩 리스트 `nested = [[1, 2], [3, 4], [5, 6]]`을 이중 for문을 사용해 1차원 리스트 `[1, 2, 3, 4, 5, 6]`으로 가공하세요.

<details><summary><b>정답 보기</b></summary>
<pre>nested = [[1, 2], [3, 4], [5, 6]]
flat = []
for sublist in nested:
    for item in sublist:
        flat.append(item)
print(flat)</pre>
</details>

### Q67. 인덱스와 값을 동시 출력 (enumerate)
리스트 `names = ["김", "이", "박"]`를 출력하되, "0번: 김", "1번: 이" 처럼 인덱스와 값을 동시에 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>names = ["김", "이", "박"]
for idx, val in enumerate(names):
    print(f"{idx}번: {val}")</pre>
</details>

### Q68. 두 리스트 병렬 순회 (zip)
두 리스트 `keys = ["ID", "PW"]`, `vals = ["admin", "123"]`을 병렬로 동시에 순회하며 "ID = admin"과 같이 출력하세요. (힌트: `zip`)

<details><summary><b>정답 보기</b></summary>
<pre>keys = ["ID", "PW"]
vals = ["admin", "123"]
for k, v in zip(keys, vals):
    print(f"{k} = {v}")</pre>
</details>

### Q69. 거꾸로 순회 (reversed)
리스트 `arr = [10, 20, 30]`의 원본을 바꾸지 않고, 역순으로 거꾸로 루프를 도는 내장 함수를 사용해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [10, 20, 30]
for x in reversed(arr):
    print(x)</pre>
</details>

### Q70. 정렬 상태로 순회 (sorted)
리스트 `unsorted = [4, 1, 3]`를 정렬된 상태로 임시 순회하는 내장 함수를 사용해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>unsorted = [4, 1, 3]
for x in sorted(unsorted):
    print(x)</pre>
</details>

### Q71. 3차원 리스트 평탄화 이중 루프
리스트 `data = [[1], [2, 3], [4]]`에서 단일 원소들만 꺼내 합산하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = [[1], [2, 3], [4]]
total = 0
for sub in data:
    for num in sub:
        total += num
print(total) # 10</pre>
</details>

### Q72. for-else 구문
for문과 else문을 함께 사용하여, 5번 루프를 도는 도중 break가 걸리지 않고 완전히 끝났을 때 `"성공"`을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>for i in range(5):
    print(i)
else:
    print("성공")</pre>
</details>

### Q73. 딕셔너리 역참조 스캔
딕셔너리 `mapping = {"NC0002": "본사_SHOP", "NC0007": "CAFE"}`에서 값(Value)이 `"CAFE"`인 항목의 키(Key)를 루프를 돌며 찾으세요.

<details><summary><b>정답 보기</b></summary>
<pre>mapping = {"NC0002": "본사_SHOP", "NC0007": "CAFE"}
target_key = None
for k, v in mapping.items():
    if v == "CAFE":
        target_key = k
        break
print("찾은 키:", target_key) # NC0007</pre>
</details>

### Q74. 리스트 컴프리헨션으로 홀수 필터링
리스트 컴프리헨션 문법을 사용해 1부터 20 사이의 정수 중 홀수 리스트를 한 줄 코드로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>odds = [x for x in range(1, 21) if x % 2 != 0]
print(odds)</pre>
</details>

### Q75. 3의 배수를 제외한 리스트 컴프리헨션
1부터 15까지의 정수 중 3의 배수를 제외한 리스트를 리스트 컴프리헨션으로 생성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = [x for x in range(1, 16) if x % 3 != 0]
print(lst)</pre>
</details>

### Q76. 리스트 안의 음수 제거 컴프리헨션
리스트 `data = [10, -5, 22, -3, 0]`에서 양수 및 0만 필터링하는 리스트 컴프리헨션을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = [10, -5, 22, -3, 0]
positives = [x for x in data if x >= 0]
print(positives)</pre>
</details>

### Q77. 문자열 리스트 길이 변환 컴프리헨션
단어 리스트 `words = ["A", "BC", "DEF"]`를 각 단어의 길이를 담은 숫자 리스트 `[1, 2, 3]`으로 컴프리헨션 변환하세요.

<details><summary><b>정답 보기</b></summary>
<pre>words = ["A", "BC", "DEF"]
lengths = [len(w) for w in words]
print(lengths)</pre>
</details>

### Q78. 소문자 필터링 컴프리헨션
문자열 `s = "HmsSystem"`에서 대문자만 걸러내어 `['H', 'S']` 리스트를 만드는 컴프리헨션을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "HmsSystem"
uppers = [char for char in s if char.isupper()]
print(uppers)</pre>
</details>

### Q79. 중복 리스트를 세트 컴프리헨션으로 처리
중괄호 `{}`와 컴프리헨션을 함께 사용해 중복이 제거되는 세트 컴프리헨션을 통해 리스트 `[1, 1, 2, 2, 3]`을 `{1, 2, 3}`으로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = [1, 1, 2, 2, 3]
unique_set = {x for x in lst}
print(unique_set)</pre>
</details>

### Q80. 딕셔너리 컴프리헨션
리스트 `keys = ["A", "B"]`와 임의의 값들을 매핑하여 `{"A": 1, "B": 2}` 딕셔너리를 딕셔너리 컴프리헨션 문법으로 생성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>keys = ["A", "B"]
new_dict = {k: idx + 1 for idx, k in enumerate(keys)}
print(new_dict)</pre>
</details>

---

### Q81 ~ Q100: 다중 루프 및 2차 종합 실습
### Q81. 별 계단식 출력
이중 for문을 사용하여 다음과 같이 계단 모양으로 별을 출력하세요.
```text
*
**
***
****
```

<details><summary><b>정답 보기</b></summary>
<pre>for i in range(1, 5):
    print("*" * i)</pre>
</details>

### Q82. 역방향 별 계단식 출력
위 Q81 모양과 반대로 정렬된 역직각삼각형 모양으로 별을 출력하세요.
```text
****
***
**
*
```

<details><summary><b>정답 보기</b></summary>
<pre>for i in range(4, 0, -1):
    print("*" * i)</pre>
</details>

### Q83. 피라미드 모양 별 찍기
가운데 정렬된 3층 높이 피라미드 별을 출력하세요.
```text
  *  
 *** 
*****
```

<details><summary><b>정답 보기</b></summary>
<pre>for i in range(1, 4):
    space = " " * (3 - i)
    stars = "*" * (2 * i - 1)
    print(space + stars)</pre>
</details>

### Q84. 구구단 가로로 출력하기
각 단(2~9단)을 세로가 아닌, 가로 방향으로 나란히 출력하는 이중 루프를 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>for i in range(1, 10):
    for dan in range(2, 10):
        print(f"{dan}x{i}={dan*i:2d}", end="  ")
    print()</pre>
</details>

### Q85. 2차원 좌표쌍 만들기
x좌표 `[1, 2]`와 y좌표 `[1, 2]`를 조합하여 가능한 모든 2차원 좌표쌍 `(x, y)`를 출력하는 다중 루프를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>for x in [1, 2]:
    for y in [1, 2]:
        print(f"({x}, {y})")</pre>
</details>

### Q86. 소수 판별기 (for-else)
특정 수 `n = 17`이 소수인지 판별할 때, 2부터 `n-1`까지 나누어 떨어지는 수가 없어서 루프가 브레이크 없이 종료되었을 때 "소수"를 출력하게 for-else 구문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>n = 17
for i in range(2, n):
    if n % i == 0:
        print("합성수")
        break
else:
    print("소수")</pre>
</details>

### Q87. 리스트의 최댓값 인덱스 찾기
for문을 사용해 리스트 `nums = [10, 50, 99, 45, 80]`의 최대값 원소가 들어있는 정확한 **인덱스 번호**를 찾아 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>nums = [10, 50, 99, 45, 80]
max_idx = 0
max_val = nums[0]
for idx, val in enumerate(nums):
    if val > max_val:
        max_val = val
        max_idx = idx
print("최대값 위치 인덱스:", max_idx) # 2</pre>
</details>

### Q88. 특정 개수 이하까지만 리스트 축소
정수 리스트 `nums = [1, 2, 3, 4, 5]`의 앞에서부터 누적합을 구하되, 홀수를 더한 횟수가 2번을 초과하면 합산을 중지(break)하는 루프를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>nums = [1, 2, 3, 4, 5]
total = 0
odd_cnt = 0
for n in nums:
    if n % 2 != 0:
        odd_cnt += 1
    total += n
    if odd_cnt >= 2:
        break
print("합계:", total)</pre>
</details>

### Q89. 문자열 리스트 내 특정 철자 빈도 계산
리스트 `words = ["apple", "banana", "cherry"]` 안에 들어있는 모든 알파벳 중 `'a'`의 개수의 총합을 for문으로 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>words = ["apple", "banana", "cherry"]
total_a_count = 0
for w in words:
    total_a_count += w.count("a")
print("총 'a' 개수:", total_a_count) # 4</pre>
</details>

### Q90. 3D 리스트 중첩 루프 순회
3차원 리스트 `cube = [[[1, 2]], [[3, 4]]]`의 모든 숫자를 차례대로 출력하는 3중 for 루프를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>cube = [[[1, 2]], [[3, 4]]]
for layer in cube:
    for row in layer:
        for val in row:
            print(val)</pre>
</details>

### Q91. 딕셔너리 내부 리스트 순회
딕셔너리 `data = {"NC0002": [10, 20], "NC0007": [30, 40]}`의 모든 리스트 속 원소들의 평균값을 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = {"NC0002": [10, 20], "NC0007": [30, 40]}
total = 0
count = 0
for vals in data.values():
    for v in vals:
        total += v
        count += 1
print("평균:", total / count) # 25.0</pre>
</details>

### Q92. 두 인덱스 차이 계산 이중 루프
리스트 `arr = [1, 2, 3]`에서 임의의 두 원소 `(x, y)`를 순서대로 매핑하되, `x != y` 인 경우만 출력하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [1, 2, 3]
for x in arr:
    for y in arr:
        if x != y:
            print(x, y)</pre>
</details>

### Q93. 대각선 성분만 출력하기
이차원 리스트 `grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]`에서 대각선상의 숫자 `1`, `5`, `9` 만을 출력하는 단일 for문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
for i in range(len(grid)):
    print(grid[i][i])</pre>
</details>

### Q94. 문자열 자릿수 교차 합산
문자열 `s = "1A2B3C4D"`에서 숫자만 추출해 누적 합산을 진행하는 루프 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = "1A2B3C4D"
total = 0
for char in s:
    if char.isdigit():
        total += int(char)
print("합계:", total) # 10</pre>
</details>

### Q95. 딕셔너리 밸류 조건 필터링 컴프리헨션
딕셔너리 `scores = {"A": 85, "B": 70, "C": 90}`에서 80점 이상인 학생들만 걸러낸 새 딕셔너리를 딕셔너리 컴프리헨션으로 생성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>scores = {"A": 85, "B": 70, "C": 90}
high_scores = {k: v for k, v in scores.items() if v &gt;= 80}
print(high_scores)</pre>
</details>

### Q96. 3의 배수이거나 5의 배수인 수의 합 (Project Euler 1선 시뮬레이션)
1부터 1000 미만의 자연수 중에서 3의 배수이거나 5의 배수인 수들의 총합을 for문으로 계산하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>total = 0
for i in range(1, 1000):
    if i % 3 == 0 or i % 5 == 0:
        total += i
print(total)</pre>
</details>

### Q97. 리스트의 순서 거꾸로 바꾸기 (for)
for문을 사용하여 리스트 `arr = [1, 2, 3, 4]`의 순서를 반대로 교체하여 새로운 리스트 `[4, 3, 2, 1]`을 만드세요 (slice 활용 금지).

<details><summary><b>정답 보기</b></summary>
<pre>arr = [1, 2, 3, 4]
reversed_arr = []
for i in range(len(arr)-1, -1, -1):
    reversed_arr.append(arr[i])
print(reversed_arr)</pre>
</details>

### Q98. 2차원 리스트 열(Column) 합산
`matrix = [[1, 2, 3], [4, 5, 6]]`에서 각 열(첫번째 열: 1+4, 두번째 열: 2+5, 세번째 열: 3+6)의 합들을 요소로 갖는 리스트 `[5, 7, 9]`를 이중 루프로 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>matrix = [[1, 2, 3], [4, 5, 6]]
cols = len(matrix[0])
col_sums = []
for c in range(cols):
    total = 0
    for r in range(len(matrix)):
        total += matrix[r][c]
    col_sums.append(total)
print(col_sums)</pre>
</details>

### Q99. 문자열 리스트 내 가장 긴 단어 찾기
리스트 `words = ["cat", "elephant", "dog", "hippopotamus"]`에서 가장 문자 길이가 긴 단어를 for 루프로 찾아 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>words = ["cat", "elephant", "dog", "hippopotamus"]
longest = words[0]
for w in words:
    if len(w) > len(longest):
        longest = w
print("가장 긴 단어:", longest)</pre>
</details>

### Q100. 카테고리 2 종합 문제
숫자 리스트 `data = [3, 7, 12, 18, 20, 23, 30]`에 들어있는 모든 원소를 탐색하며,
1. 짝수인 경우에는 값을 2로 나눈 결과값을 출력하고,
2. 홀수인 경우에는 값에 2를 곱한 결과를 출력하되,
3. 결과값이 40 이상이 되는 최초의 원소가 발견되면 그 시점에 루프를 강제 종료(break)하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = [3, 7, 12, 18, 20, 23, 30]
for x in data:
    if x % 2 == 0:
        res = x // 2
    else:
        res = x * 2
        
    print(f"원래값: {x} -&gt; 결과값: {res}")
    
    if res &gt;= 40:
        print(f"종료 조건 만족 (결과값 {res} &gt;= 40). 루프를 중지합니다.")
        break</pre>
</details>
