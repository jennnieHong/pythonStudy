# Python 실전 연습 문제집 - [카테고리 3] 자료구조 (100제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"Cat3"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py Cat3 Q1 True` (Q1 문제를 완료로 변경)


본 문제집은 파이썬의 동적 컨테이너인 **리스트(List)**, **튜플(Tuple)**, **딕셔너리(Dictionary)**, **세트(Set)**의 CRUD 연산 및 활용법 100문제와 해설식 정답을 수록하고 있습니다.

---

### Q1 ~ Q30: 리스트 (List) 데이터 다루기
### Q1. 빈 리스트 선언
아무 요소도 들어있지 않은 빈 리스트를 생성하는 2가지 선언 기법을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst1 = []
lst2 = list()</pre>
</details>

### Q2. 리스트 원소 추가 (append)
리스트 `arr = [1, 2]`에 새로운 숫자 `3`을 꼬리부분에 추가하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [1, 2]
arr.append(3)
print(arr) # [1, 2, 3]</pre>
</details>

### Q3. 리스트 중간 삽입 (insert)
리스트 `arr = [1, 3]`의 첫 번째 인덱스(1번 위치) 자리에 숫자 `2`를 삽입하여 `[1, 2, 3]`으로 만드는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [1, 3]
arr.insert(1, 2)
print(arr) # [1, 2, 3]</pre>
</details>

### Q4. 리스트 병합 확장 (extend)
리스트 `a = [1, 2]` 뒤에 다른 리스트 `b = [3, 4]`의 모든 원소를 결합하여 확장(`extend`)해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = [1, 2]
b = [3, 4]
a.extend(b)
print(a) # [1, 2, 3, 4]</pre>
</details>

### Q5. 대입 연산자를 이용한 결합
위 Q4의 두 리스트 결합을 `+` 연산자를 사용하여 생성 후 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = [1, 2]
b = [3, 4]
c = a + b
print(c)</pre>
</details>

### Q6. 특정 값 기준으로 삭제 (remove)
리스트 `lst = ["hq", "st", "admin"]`에서 `"st"`를 값을 기준으로 찾아 제거하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = ["hq", "st", "admin"]
lst.remove("st")
print(lst) # ['hq', 'admin']</pre>
</details>

### Q7. 인덱스 기준으로 삭제 (pop)
리스트 `lst = [10, 20, 30]`의 마지막 원소를 안전하게 꺼내어(`pop`) 변수 `val`에 담으세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = [10, 20, 30]
val = lst.pop()
print(val, lst) # 30 [10, 20]</pre>
</details>

### Q8. 특정 인덱스 원소 제거 (del)
리스트 `lst = [100, 200, 300]`의 인덱스 1번 원소 `200`을 `del` 예약어로 삭제하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = [100, 200, 300]
del lst[1]
print(lst) # [100, 300]</pre>
</details>

### Q9. 리스트 내부 비우기 (clear)
리스트 `lst = [1, 2, 3]`의 모든 요소를 제거하여 빈 리스트 상태로 리셋하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = [1, 2, 3]
lst.clear()
print(lst) # []</pre>
</details>

### Q10. 리스트 원소 존재 횟수 계산 (count)
리스트 `arr = [1, 2, 2, 3, 2]` 에서 숫자 `2`가 몇 개인지 세어 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [1, 2, 2, 3, 2]
print(arr.count(2)) # 3</pre>
</details>

### Q11. 리스트 원소 정렬 (sort)
리스트 `scores = [90, 70, 85, 95]`를 제자리에서(In-place) 오름차순 정렬하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>scores = [90, 70, 85, 95]
scores.sort()
print(scores)</pre>
</details>

### Q12. 리스트 원소 역정렬 (sort desc)
Q11의 리스트 `scores`를 내림차순으로 제자리 정렬해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>scores = [90, 70, 85, 95]
scores.sort(reverse=True)
print(scores)</pre>
</details>

### Q13. 임시 정렬 반환 (sorted)
원본 리스트 `arr = [3, 1, 2]`의 상태는 보존하면서, 정렬된 사본 리스트를 얻는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [3, 1, 2]
new_arr = sorted(arr)
print(arr, new_arr) # [3, 1, 2] [1, 2, 3]</pre>
</details>

### Q14. 리스트 좌우 뒤집기 (reverse)
리스트 `arr = ["A", "B", "C"]`를 정렬 기준 없이 단순 역순 `["C", "B", "A"]`로 뒤집으세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = ["A", "B", "C"]
arr.reverse()
print(arr)</pre>
</details>

### Q15. 리스트 내 값 위치 인덱스 찾기 (index)
리스트 `arr = ["Apple", "Banana", "Cherry"]`에서 `"Banana"`의 정확한 인덱스 값을 찾는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = ["Apple", "Banana", "Cherry"]
print(arr.index("Banana")) # 1</pre>
</details>

### Q16. 슬라이싱 기법으로 리스트 카피
리스트 `origin = [1, 2, 3]`를 얕은 복사 방식으로 새로운 리스트 `copy_list`에 슬라이싱 문법(`[:]`)을 사용해 대입하세요.

<details><summary><b>정답 보기</b></summary>
<pre>origin = [1, 2, 3]
copy_list = origin[:]
print(copy_list)</pre>
</details>

### Q17. 리스트의 곱셈 복사
리스트 `zero = [0]`에 정수 곱하기 연산을 적용하여 0이 10개 들어있는 리스트를 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>zeros = [0] * 10
print(zeros)</pre>
</details>

### Q18. 리스트 내 최소/최대값 탐색
리스트 `data = [55, 12, 99, 43, 7]`의 최소값과 최대값을 단일 내장 함수로 가각 추출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = [55, 12, 99, 43, 7]
print(min(data), max(data))</pre>
</details>

### Q19. 리스트 요소 총합계
정수 리스트 `nums = [1, 2, 3, 4, 5]`의 모든 원소 합계를 내장 함수로 계산해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>nums = [1, 2, 3, 4, 5]
print(sum(nums)) # 15</pre>
</details>

### Q20. 리스트 슬라이싱 범위 건너뛰기
리스트 `lst = [10, 20, 30, 40, 50]`에서 `[20, 40]` 처럼 1번 인덱스부터 시작해서 한 칸씩 건너뛰며 값을 슬라이싱하는 문법을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = [10, 20, 30, 40, 50]
print(lst[1::2]) # [20, 40]</pre>
</details>

### Q21. 리스트 슬라이싱 역방향
리스트 `lst = [1, 2, 3, 4, 5]`에서 `[4, 3, 2]` 부분만 역방향 인덱싱 슬라이싱을 이용해 추출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = [1, 2, 3, 4, 5]
print(lst[3:0:-1]) # [4, 3, 2]</pre>
</details>

### Q22. 리스트의 참/거짓 판단 기준
if문 조건에서 리스트가 비어 있으면 `False`로 판단됩니다. 리스트 `arr`이 비어 있지 않을 경우에만 작동하는 조건식을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [1]
if arr:
    print("원소가 있습니다.")</pre>
</details>

### Q23. 리스트 컴프리헨션 기본
1부터 5까지 숫자를 곱한 값들 `[1, 4, 9, 16, 25]`를 단 한 줄의 컴프리헨션 코드로 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>squares = [x**2 for x in range(1, 6)]
print(squares)</pre>
</details>

### Q24. 리스트 컴프리헨션 조건 추가
1부터 10까지 숫자 중 홀수만 제곱한 리스트를 리스트 컴프리헨션으로 생성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>odd_squares = [x**2 for x in range(1, 11) if x % 2 != 0]
print(odd_squares)</pre>
</details>

### Q25. 2차원 리스트 생성
3행 3열의 0으로 채워진 2차원 리스트 `[[0, 0, 0], [0, 0, 0], [0, 0, 0]]`를 리스트 컴프리헨션을 사용하여 안전하게 생성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>grid = [[0 for _ in range(3)] for _ in range(3)]
print(grid)</pre>
</details>

### Q26. 리스트 안의 모든 요소를 문자열로 변환
리스트 `int_list = [1, 2, 3]`을 문자열 리스트 `['1', '2', '3']`으로 일괄 변환하는 컴프리헨션을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>int_list = [1, 2, 3]
str_list = [str(x) for x in int_list]
print(str_list)</pre>
</details>

### Q27. 리스트 원소 위치 삽입 시 인덱스 에러 방지
원소가 3개 있는 리스트의 100번 인덱스 자리에 insert로 값을 삽입하려 하면 파이썬은 어떻게 대처하나요?

<details><summary><b>정답 보기</b></summary>
<pre># 에러가 나지 않고 맨 마지막 꼬리 인덱스에 값을 안전하게 추가(append)해 줍니다.</pre>
</details>

### Q28. 중첩 리스트의 특정 인덱스 제거
`nested = [[1, 2], [3, 4]]` 에서 `3`을 삭제해 `[[1, 2], [4]]`로 만드는 `del` 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>nested = [[1, 2], [3, 4]]
del nested[1][0]
print(nested)</pre>
</details>

### Q29. 리스트 문자 결합 (join)
문자 리스트 `['H', 'M', 'S']`를 하나의 문자열 `"HMS"`로 합치기 위해 문자열 조인 메소드를 사용하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = ['H', 'M', 'S']
print("".join(lst))</pre>
</details>

### Q30. 다중 복사 대입 주소 체크
리스트 `list1 = [1, 2]`, `list2 = list1` 일 때, `list2.append(3)`을 수행한 뒤 `list1`을 출력하면 값은 어떻게 변하나요?

<details><summary><b>정답 보기</b></summary>
<pre># 두 변수가 같은 객체의 주소를 공유(얕은 대입)하므로 list1 역시 [1, 2, 3]으로 똑같이 변합니다.</pre>
</details>

---

### Q31 ~ Q45: 튜플 (Tuple)의 특성과 제어
### Q31. 단일 원소 튜플 선언 주의점
원소가 오직 정수 `5` 하나만 있는 튜플을 선언할 때 뒤에 콤마(`,`)를 붙여야 하는 문법적 이유를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>t = (5,) # 콤마가 없으면 파이썬은 이를 단순 괄호가 쳐진 정수형(int) 변수로 인식합니다.</pre>
</details>

### Q32. 튜플 값 가져오기
튜플 `t = ("A", "B", "C")`에서 인덱스 2번 값을 인덱싱하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>t = ("A", "B", "C")
print(t[2]) # C</pre>
</details>

### Q33. 튜플 변경 시도 시 예외
튜플 `t = (1, 2)`의 값을 수정하려 할 때 파이썬 에러 로그에 등장하는 에러 타입명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre># TypeError 예외가 발생합니다. (TypeError: 'tuple' object does not support item assignment)</pre>
</details>

### Q34. 두 튜플 결합
`t1 = (1, 2)`, `t2 = (3, 4)`를 결합해 신규 튜플 `t3`을 만드는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>t1 = (1, 2)
t2 = (3, 4)
t3 = t1 + t2
print(t3) # (1, 2, 3, 4)</pre>
</details>

### Q35. 튜플을 리스트로 변환
불변의 튜플 `t = (1, 2, 3)`을 수정이 가능한 리스트 객체로 형변환하세요.

<details><summary><b>정답 보기</b></summary>
<pre>t = (1, 2, 3)
lst = list(t)
print(type(lst)) # &lt;class 'list'&gt;</pre>
</details>

### Q36. 리스트를 튜플로 변환
리스트 `lst = [10, 20]`을 튜플로 형변환하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = [10, 20]
t = tuple(lst)
print(type(t)) # &lt;class 'tuple'&gt;</pre>
</details>

### Q37. 튜플 내 원소 위치 index 구하기
튜플 `t = ("apple", "banana")`에서 `"banana"`의 인덱스를 반환하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>t = ("apple", "banana")
print(t.index("banana")) # 1</pre>
</details>

### Q38. 튜플 내 특정 원소 개수 (count)
튜플 `t = (1, 1, 2, 3, 1)`에서 숫자 `1`이 들어있는 개수를 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>t = (1, 1, 2, 3, 1)
print(t.count(1)) # 3</pre>
</details>

### Q39. 튜플 언패킹 1
튜플 `t = ("admin2", "NC0007")`을 언패킹하여 `user_id`와 `store_code` 변수로 각각 꺼내는 코드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>t = ("admin2", "NC0007")
user_id, store_code = t
print(user_id, store_code)</pre>
</details>

### Q40. 튜플 언패킹 별표(*) 기법
튜플 `t = (1, 2, 3, 4, 5)`를 언패킹하되 첫 번째 원소는 `a`, 맨 마지막 원소는 `b`에 담고, 나머지 중간 모든 원소들은 리스트형으로 `middle` 변수에 한꺼번에 담기게 하세요.

<details><summary><b>정답 보기</b></summary>
<pre>t = (1, 2, 3, 4, 5)
a, *middle, b = t
print(a, middle, b) # 1 [2, 3, 4] 5</pre>
</details>

### Q41. 함수 다중 리턴 값의 기본 자료형
함수가 `return a, b` 처럼 여러 개의 값을 한 번에 콤마로 구분하여 리턴할 때, 호출부에서 수신받는 실제 결합 자료형은 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># 튜플(Tuple) 형태로 결합하여 반환받습니다.</pre>
</details>

### Q42. 튜플 곱셈 연산
튜플 `t = ("A",)`를 3배 연산하여 `("A", "A", "A")` 튜플을 생성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>t = ("A",)
print(t * 3)</pre>
</details>

### Q43. 튜플 크기 비교 방식
`t1 = (1, 2, 3)`, `t2 = (1, 2, 4)` 일 때 `t1 < t2` 가 참(`True`)이 되는 파이썬의 튜플 크기 비교 메커니즘을 설명하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 첫 번째 원소부터 순차적으로 크기를 비교하며, 인덱스 2번에서 3 &lt; 4 이므로 t1 &lt; t2는 참(True)이 됩니다.</pre>
</details>

### Q44. 튜플을 딕셔너리 키로 쓸 수 있는 이유
리스트는 딕셔너리의 Key로 사용 시 에러가 나지만, 튜플은 Key로 쓸 수 있는 근본적 성질 차이를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 딕셔너리의 키는 변경 불가능(Immutable)해야 하는 해시 속성을 가집니다. 리스트는 가변형(Mutable)이라 안 되지만, 튜플은 불변형(Immutable)이므로 키로 사용이 가능합니다.</pre>
</details>

### Q45. 튜플 내의 리스트 값 수정
`t = (1, 2, [3, 4])`가 주어졌을 때, `t[2][0] = 99` 연산이 성공하는가요? 아니면 에러가 나는가요?

<details><summary><b>정답 보기</b></summary>
<pre># 성공합니다. 튜플이 가리키는 리스트 참조 주소값은 불변이지만, 리스트 내용물은 가변적(Mutable)이기 때문에 리스트 내부 요소를 수정하는 것은 허용됩니다.</pre>
</details>

---

### Q46 ~ Q75: 딕셔너리 (Dictionary) CRUD 연산
### Q46. 빈 딕셔너리 생성
빈 딕셔너리 객체를 생성하는 2가지 방법을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>d1 = {}
d2 = dict()</pre>
</details>

### Q47. Key-Value 등록
딕셔너리 `d = {}`에 키 `"id"`, 값 `"admin2"` 한 쌍을 입력 등록하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {}
d["id"] = "admin2"
print(d)</pre>
</details>

### Q48. 데이터 수정
딕셔너리 `d = {"id": "admin"}`의 `"id"` 값을 `"new_admin"`으로 변경하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"id": "admin"}
d["id"] = "new_admin"
print(d)</pre>
</details>

### Q49. 특정 키 제거 (del)
딕셔너리 `d = {"a": 1, "b": 2}`에서 키 `"b"`와 그 값을 삭제하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1, "b": 2}
del d["b"]
print(d)</pre>
</details>

### Q50. 안전한 키 제거 및 값 반환 (pop)
딕셔너리 `d = {"id": "admin2", "role": "ADMIN"}`에서 키 `"role"`에 해당하는 값을 꺼내오며 삭제하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"id": "admin2", "role": "ADMIN"}
role_val = d.pop("role")
print(role_val, d) # ADMIN {'id': 'admin2'}</pre>
</details>

### Q51. 딕셔너리 키 존재 여부 확인 (in)
딕셔너리 `d = {"a": 1}`에 키 `"b"`가 들어있는지 유무를 Boolean 값으로 확인하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1}
print("b" in d) # False</pre>
</details>

### Q52. 안전하게 데이터 반환 (get)
딕셔너리 `d = {"a": 1}`에서 키 `"b"` 값을 꺼내오되, 에러를 내지 않고 안전하게 `None`이 반환되도록 하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1}
print(d.get("b")) # None</pre>
</details>

### Q53. get 함수 디폴트 지정
Q52에서 키 `"b"`가 없을 경우 임의로 정의한 디폴트 값 `"No Key"`가 반환되도록 설정하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1}
print(d.get("b", "No Key")) # No Key</pre>
</details>

### Q54. 딕셔너리 모든 키 목록 가져오기 (keys)
딕셔너리 `d = {"a": 1, "b": 2}`의 모든 키 목록을 가져오는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1, "b": 2}
print(d.keys()) # dict_keys(['a', 'b'])</pre>
</details>

### Q55. 딕셔너리 키 리스트 변환
Q54의 keys() 반환값은 온전한 리스트형이 아닙니다. 이를 실제 인덱싱이 가능한 `list`형으로 캐싱 변환하는 코드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1, "b": 2}
k_list = list(d.keys())
print(k_list[0]) # 'a'</pre>
</details>

### Q56. 딕셔너리 모든 값 목록 가져오기 (values)
딕셔너리 `d = {"a": 1, "b": 2}`의 모든 Value값들만 추출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1, "b": 2}
print(d.values())</pre>
</details>

### Q57. 딕셔너리 키-값 쌍 가져오기 (items)
딕셔너리 `d = {"a": 1, "b": 2}`의 키와 값 쌍 전체를 튜플 쌍 형태로 뽑아내는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1, "b": 2}
print(d.items()) # dict_items([('a', 1), ('b', 2)])</pre>
</details>

### Q58. 딕셔너리 병합 일괄 업데이트 (update)
딕셔너리 `d1 = {"a": 1}`에 다른 딕셔너리 `d2 = {"b": 2, "a": 99}`를 덮어쓰며 병합(`update`)하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d1 = {"a": 1}
d2 = {"b": 2, "a": 99}
d1.update(d2)
print(d1) # {'a': 99, 'b': 2}</pre>
</details>

### Q59. 딕셔너리 크기 확인 (len)
딕셔너리 `d = {"a": 1, "b": 2}`의 등록 키 쌍의 개수를 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1, "b": 2}
print(len(d)) # 2</pre>
</details>

### Q60. 딕셔너리 데이터 리셋 (clear)
딕셔너리 `d = {"id": 1}`의 모든 항목을 지우고 빈 상태로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"id": 1}
d.clear()
print(d) # {}</pre>
</details>

### Q61. 딕셔너리 키 기본값 설정 및 가져오기 (setdefault)
딕셔너리 `d = {"a": 1}`에서 키 `"b"`가 존재하지 않으면 `"b": 100`을 자동 삽입하고 그 값을 리턴해주는 메소드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1}
val = d.setdefault("b", 100)
print(val, d) # 100 {'a': 1, 'b': 100}</pre>
</details>

### Q62. 키 리스트로부터 딕셔너리 일괄 선언 (fromkeys)
키 목록 `keys = ["a", "b", "c"]`에 대해 모든 디폴트 값을 `0`으로 대입한 완성형 딕셔너리를 생성하는 클래스 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>keys = ["a", "b", "c"]
d = dict.fromkeys(keys, 0)
print(d) # {'a': 0, 'b': 0, 'c': 0}</pre>
</details>

### Q63. 중첩 딕셔너리 선언 및 접근
중첩 딕셔너리 `data = {"NC0007": {"owner": "홍길동", "sales": 380}}`에서 매출액 `380` 값을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = {"NC0007": {"owner": "홍길동", "sales": 380}}
print(data["NC0007"]["sales"])</pre>
</details>

### Q64. 딕셔너리 루프 key 순회
딕셔너리 `d = {"A": 1, "B": 2}`에서 키들만 뽑아 for 반복문으로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"A": 1, "B": 2}
for k in d.keys():
    print(k)</pre>
</details>

### Q65. 딕셔너리 루프 value 순회
딕셔너리 `d = {"A": 1, "B": 2}`에서 값들만 순서대로 for 반복문으로 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"A": 1, "B": 2}
for v in d.values():
    print(v)</pre>
</details>

### Q66. 딕셔너리 루프 items 구조 분해
딕셔너리 `d = {"A": 1, "B": 2}`의 모든 쌍을 for 루프로 돌며 변수 `key`와 `val`에 구조 분해 할당하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"A": 1, "B": 2}
for key, val in d.items():
    print(key, val)</pre>
</details>

### Q67. 딕셔너리 키 정렬 결과 리스트화
딕셔너리 `d = {"c": 3, "a": 1, "b": 2}`의 키 목록을 가나다순으로 정렬한 리스트 `['a', 'b', 'c']`로 가져오세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"c": 3, "a": 1, "b": 2}
print(sorted(d.keys()))</pre>
</details>

### Q68. 딕셔너리 키-값 쌍 리스트로부터 딕셔너리 재생성
튜플 쌍 리스트 `pairs = [("a", 1), ("b", 2)]`를 단 한 줄의 캐스팅 함수로 `{"a": 1, "b": 2}` 딕셔너리로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>pairs = [("a", 1), ("b", 2)]
print(dict(pairs))</pre>
</details>

### Q69. 딕셔너리 내 최댓값의 키 찾기
딕셔너리 `data = {"A": 50, "B": 99, "C": 70}`에서 가장 값(Value)이 큰 항목의 **Key**인 `"B"`를 구하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = {"A": 50, "B": 99, "C": 70}
max_key = max(data, key=data.get)
print(max_key) # B</pre>
</details>

### Q70. 딕셔너리 컴프리헨션 기초
리스트 `[1, 2, 3]`을 가지고 `{1: 1, 2: 4, 3: 9}` 처럼 정수와 정수의 제곱 매핑 딕셔너리를 컴프리헨션으로 생성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {x: x**2 for x in [1, 2, 3]}
print(d)</pre>
</details>

### Q71. 딕셔너리 컴프리헨션 조건절
원본 딕셔너리 `data = {"a": 1, "b": 10, "c": 3}`에서 값이 5보다 큰 항목만 필터링한 신규 딕셔너리를 컴프리헨션으로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = {"a": 1, "b": 10, "c": 3}
filtered = {k: v for k, v in data.items() if v > 5}
print(filtered) # {'b': 10}</pre>
</details>

### Q72. 딕셔너리 얕은 복사 (copy)
딕셔너리 `d = {"a": 1}`를 얕은 복사 방식으로 새로운 메모리 독립 객체 `d_copy`로 복제하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1}
d_copy = d.copy()
d_copy["a"] = 99
print(d["a"]) # 1 (영향 없음)</pre>
</details>

### Q73. 두 개의 리스트를 딕셔너리로 결합 (zip)
`keys = ["ko", "en"]`, `vals = ["한국어", "영어"]`를 결합하여 `{"ko": "한국어", "en": "영어"}`를 한 줄로 선언하세요.

<details><summary><b>정답 보기</b></summary>
<pre>keys = ["ko", "en"]
vals = ["한국어", "영어"]
print(dict(zip(keys, vals)))</pre>
</details>

### Q74. 딕셔너리 내 특정 키 삭제 시 에러 방지
딕셔너리 `d = {"a": 1}`에서 없는 키 `"z"`를 del로 지우면 KeyError가 납니다. 에러 없이 지우기 위해 pop() 함수에 지정할 수 있는 옵션은 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1}
# pop의 두 번째 인자에 디폴트 값을 전달하면 키가 없더라도 에러 없이 해당 값을 반환합니다.
d.pop("z", None)</pre>
</details>

### Q75. 정수 키와 문자열 키 구분
딕셔너리 `d = {1: "one", "1": "str_one"}` 일 때 `d[1]`과 `d["1"]`은 서로 별개의 키로 분리되는가요?

<details><summary><b>정답 보기</b></summary>
<pre># 네, 숫자형 1과 문자열 '1'은 서로 다르게 해싱되므로 별개의 고유 키로 취급됩니다.</pre>
</details>

---

### Q76 ~ Q90: 세트 (Set) 자료 구조 활용
### Q76. 빈 세트 생성 주의점
빈 세트(Set)를 생성할 때 `s = {}`로 선언하면 왜 안 되는지 설명하고 올바른 생성 방식을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre># s = {} 로 선언하면 파이썬은 빈 딕셔너리(dict)로 인식합니다. 빈 세트는 반드시 s = set() 으로 선언해야 합니다.</pre>
</details>

### Q77. 세트 원소 추가 (add)
세트 `s = {1, 2}`에 숫자 `3`을 추가하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = {1, 2}
s.add(3)
print(s)</pre>
</details>

### Q78. 세트 여러 원소 추가 (update)
세트 `s = {1, 2}`에 다른 컨테이너 `[3, 4, 5]`의 여러 값들을 한꺼번에 병합 삽입하는 메소드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = {1, 2}
s.update([3, 4, 5])
print(s) # {1, 2, 3, 4, 5}</pre>
</details>

### Q79. 세트 원소 안전 삭제 (discard)
세트 `s = {1, 2}`에서 존재하지 않는 원소 `9`를 삭제하더라도 에러가 나지 않도록 차단하는 소거 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = {1, 2}
s.discard(9) # 에러 없이 무시됨 (remove는 KeyError 유발)</pre>
</details>

### Q80. 세트 교집합 연산
두 세트 `a = {1, 2, 3}`, `b = {3, 4, 5}`의 공통 원소 집합 `{3}`을 구하는 연산자 및 메소드를 각각 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = {1, 2, 3}
b = {3, 4, 5}
print(a & b)
print(a.intersection(b))</pre>
</details>

### Q81. 세트 합집합 연산
두 세트 `a = {1, 2}`, `b = {2, 3}`의 전체 합집합 `{1, 2, 3}`을 구하는 연산자 및 메소드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = {1, 2}
b = {2, 3}
print(a | b)
print(a.union(b))</pre>
</details>

### Q82. 세트 차집합 연산
세트 `a = {1, 2, 3}`에서 `b = {3, 4}`를 제외한 차집합 `{1, 2}`를 구하는 연산자 및 메소드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = {1, 2, 3}
b = {3, 4}
print(a - b)
print(a.difference(b))</pre>
</details>

### Q83. 대칭차집합 연산
두 집합에서 공통된 부분을 제외한 나머지 합집합(대칭차집합) `{1, 2, 4, 5}`를 구하는 기호를 쓰세요. (힌트: `^`)

<details><summary><b>정답 보기</b></summary>
<pre>a = {1, 2, 3}
b = {3, 4, 5}
print(a ^ b) # {1, 2, 4, 5}</pre>
</details>

### Q84. 세트의 중복 제거 응용
리스트 `lst = [1, 1, 2, 2, 3, 3]`을 중복이 없는 단일 리스트 `[1, 2, 3]`으로 한 줄의 코드로 가공하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lst = [1, 1, 2, 2, 3, 3]
unique_list = list(set(lst))
print(unique_list)</pre>
</details>

### Q85. 부분 집합 판단 (issubset)
세트 `a = {1, 2}`가 세트 `b = {1, 2, 3}`의 완전한 부분 집합인지 확인하는 Boolean 반환 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = {1, 2}
b = {1, 2, 3}
print(a.issubset(b)) # True</pre>
</details>

### Q86. 상위 집합 판단 (issuperset)
세트 `a = {1, 2, 3}`가 세트 `b = {1, 2}`를 완전히 포함하는 상위 집합인지 확인하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = {1, 2, 3}
b = {1, 2}
print(a.issuperset(b)) # True</pre>
</details>

### Q87. 서로소 집합 판단 (isdisjoint)
두 세트 `a = {1, 2}`, `b = {3, 4}`가 공통 원소를 전혀 갖지 않는 관계(서로소)인지 확인하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>a = {1, 2}
b = {3, 4}
print(a.isdisjoint(b)) # True</pre>
</details>

### Q88. 세트의 원소 추가/삭제 속도 성능적 이점
리스트에서 `in` 연산자로 특정 원소를 검색하는 것에 비해, 세트(Set)에서 `in` 연산자를 수행하는 것이 훨씬 빠른 이유를 시간복잡도(Big-O) 관점에서 기술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 리스트는 순차 탐색(O(N))을 하지만, 세트는 내부적으로 해시 테이블(Hash Table)을 사용하여 값을 관리하기 때문에 평균 O(1)의 매우 빠른 시간 내에 원소 존재 여부를 탐색해 냅니다.</pre>
</details>

### Q89. 세트 컴프리헨션
문자열 `"banana"`로부터 고유 알파벳 철자들만 걸러내는 세트 컴프리헨션 식을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>unique_chars = {char for char in "banana"}
print(unique_chars) # {'b', 'a', 'n'}</pre>
</details>

### Q90. 세트의 변경 불가능 가공형 (frozenset)
세트도 가변 객체입니다. 세트 내부 요소를 임의로 수정/추가할 수 없도록 완전히 동결(Immutable)시키는 파이썬 빌트인 자료형 변환 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>frozen = frozenset([1, 2, 3])
# frozen.add(4) -> 에러 발생</pre>
</details>

---

### Q91 ~ Q100: 복합 자료 구조 및 정렬 응용
### Q91. 2차원 딕셔너리 구조 분해
중첩 자료구조 `data = {"users": [{"name": "김", "age": 30}]}`에서 `"김"` 이름을 꺼내 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = {"users": [{"name": "김", "age": 30}]}
print(data["users"][0]["name"])</pre>
</details>

### Q92. 딕셔너리 값을 기준으로 오름차순 정렬
딕셔너리 `d = {"A": 30, "B": 10, "C": 20}`가 있을 때, 값(Value)들을 기준으로 오름차순 정렬된 튜플 쌍 리스트 `[('B', 10), ('C', 20), ('A', 30)]`를 구하세요. (힌트: `sorted`, `key=lambda`)

<details><summary><b>정답 보기</b></summary>
<pre>d = {"A": 30, "B": 10, "C": 20}
sorted_pairs = sorted(d.items(), key=lambda x: x[1])
print(sorted_pairs)</pre>
</details>

### Q93. 딕셔너리 값을 기준으로 내림차순 정렬
Q92의 딕셔너리 `d`를 값(Value) 기준 내림차순 정렬된 튜플 리스트로 변환하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"A": 30, "B": 10, "C": 20}
sorted_pairs_desc = sorted(d.items(), key=lambda x: x[1], reverse=True)
print(sorted_pairs_desc)</pre>
</details>

### Q94. 두 딕셔너리의 공통 키 찾기 (Set 연산 연계)
두 딕셔너리 `d1 = {"a": 1, "b": 2}`, `d2 = {"b": 10, "c": 3}`의 공통된 키 집합을 구하세요.

<details><summary><b>정답 보기</b></summary>
<pre>d1 = {"a": 1, "b": 2}
d2 = {"b": 10, "c": 3}
common_keys = set(d1.keys()) & set(d2.keys())
print(common_keys) # {'b'}</pre>
</details>

### Q95. 리스트 내부 딕셔너리 키 값 유무 정렬
리스트 `users = [{"id": "a", "fail": 2}, {"id": "b", "fail": 0}, {"id": "c", "fail": 5}]`가 있을 때 실패 횟수(`fail`)가 큰 순서대로 내림차순 정렬하세요.

<details><summary><b>정답 보기</b></summary>
<pre>users = [{"id": "a", "fail": 2}, {"id": "b", "fail": 0}, {"id": "c", "fail": 5}]
users.sort(key=lambda x: x["fail"], reverse=True)
print(users)</pre>
</details>

### Q96. 딕셔너리에서 특정 값 이상인 키 목록 수집
딕셔너리 `db_pool = {"conn1": 10, "conn2": 45, "conn3": 5}`에서 값(커넥션 사용량)이 15 이상인 키명만 추출한 리스트를 한 줄짜리 리스트 컴프리헨션으로 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>db_pool = {"conn1": 10, "conn2": 45, "conn3": 5}
warn_conns = [k for k, v in db_pool.items() if v >= 15]
print(warn_conns) # ['conn2']</pre>
</details>

### Q97. 리스트 요소 빈도수 카운터 사전 만들기
리스트 `data = ["a", "b", "a", "c", "b", "a"]`를 바탕으로 각 철자가 몇 번 등장했는지 기록한 빈도 딕셔너리 `{"a": 3, "b": 2, "c": 1}`을 단일 루프로 직접 구축해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = ["a", "b", "a", "c", "b", "a"]
counter = {}
for item in data:
    counter[item] = counter.get(item, 0) + 1
print(counter)</pre>
</details>

### Q98. 복합 리스트 내포 분해
문자열 리스트 `data = ["1,2", "3,4", "5,6"]`에 콤마가 포함되어 있습니다. 이를 분할 및 정수화하여 하나의 리스트 `[1, 2, 3, 4, 5, 6]`으로 플래팅하는 리스트 컴프리헨션을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = ["1,2", "3,4", "5,6"]
flat_ints = [int(num) for item in data for num in item.split(",")]
print(flat_ints)</pre>
</details>

### Q99. 세트 데이터 리스트 정렬 후 반환
세트 `s = {10, 5, 99, 1}`을 정렬하여 순서가 보장된 리스트 `[1, 5, 10, 99]`로 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>s = {10, 5, 99, 1}
sorted_list = sorted(list(s))
print(sorted_list)</pre>
</details>

### Q100. 카테고리 3 종합 문제
매장 정보 리스트 `stores = [{"code": "NC0002", "active": True}, {"code": "NC0007", "active": False}, {"code": "NC0005", "active": True}]`가 주어졌을 때,
1. 활성 상태(`active`가 `True`)인 매장들만 리스트 컴프리헨션으로 필터링하여,
2. 매장 코드(`code`)값들을 추출한 뒤 세트(Set) 집합 형태로 만들고,
3. 해당 세트에 신규 코드 `"NC0009"`를 결합한 최종 세트 집합을 출력하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>stores = [{"code": "NC0002", "active": True}, {"code": "NC0007", "active": False}, {"code": "NC0005", "active": True}]

# 1, 2단계: active인 매장의 code로 구성된 세트 생성
active_set = {s["code"] for s in stores if s["active"]}

# 3단계: NC0009 추가
active_set.add("NC0009")

print(active_set) # {'NC0002', 'NC0005', 'NC0009'}</pre>
</details>
