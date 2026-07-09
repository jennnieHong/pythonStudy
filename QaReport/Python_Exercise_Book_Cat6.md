# Python 실전 연습 문제집 - [카테고리 6] 예외 처리 및 파일 입출력 (100제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"Cat6"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py Cat6 Q1 True` (Q1 문제를 완료로 변경)


본 문제집은 파이썬의 **오류 예외 처리(try-except-finally)**, **예외 강제 발생(raise)**, **커스텀 예외정의**, **with 구문을 활용한 리소스 제어**, **파일 읽기/쓰기(CRUD)**, **CSV/텍스트 파일 분석**, **디렉토리 생성/제거** 등에 관한 100문제와 해설식 정답을 수록하고 있습니다.

---

### Q1 ~ Q30: 예외 처리 (try-except-finally) 기초 및 제어
### Q1. 예외 처리 기본 골격
에러 발생 시 비정상 종료를 예방하는 가장 기초적인 try-except 구문 형식을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    # 에러 위험 코드
    pass
except Exception:
    # 에러 처리 코드
    pass</pre>
</details>

### Q2. 0 나눗셈 예외 처리 (ZeroDivisionError)
숫자를 0으로 나눌 때 일어나는 예외인 `ZeroDivisionError`를 특정 처리하는 except 블록을 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    val = 10 / 0
except ZeroDivisionError as e:
    print("0으로 나눌 수 없습니다:", e)</pre>
</details>

### Q3. 숫자 변환 예외 처리 (ValueError)
텍스트 `"abc"`를 int()로 바꾸다 생기는 `ValueError`를 받아 안전하게 경고 출력하는 try-except 문을 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    num = int("abc")
except ValueError:
    print("형변환 에러")</pre>
</details>

### Q4. 없는 인덱스 접근 예외 처리 (IndexError)
리스트 `arr = [1, 2]`의 5번 인덱스를 출력하려 할 때 발생하는 `IndexError`를 대처하는 예외 처리를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>arr = [1, 2]
try:
    print(arr[5])
except IndexError:
    print("인덱스 범위를 초과했습니다.")</pre>
</details>

### Q5. 없는 딕셔너리 키 접근 예외 처리 (KeyError)
딕셔너리 `d = {"a": 1}`에서 `d["z"]`를 읽다 발생하는 `KeyError` 예외를 처리하는 블록을 만드세요.

<details><summary><b>정답 보기</b></summary>
<pre>d = {"a": 1}
try:
    print(d["z"])
except KeyError:
    print("존재하지 않는 키입니다.")</pre>
</details>

### Q6. 타입 불일치 연산 예외 처리 (TypeError)
문자열과 숫자를 더하려 할 때 발생하는 `TypeError`를 대처하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    res = "HMS" + 100
except TypeError:
    print("타입이 맞지 않아 연산할 수 없습니다.")</pre>
</details>

### Q7. 선언되지 않은 변수 참조 예외 처리 (NameError)
선언한 적 없는 변수 `unregistered_var`를 사용하려 할 때 발생하는 `NameError`를 잡는 구문을 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    print(unregistered_var)
except NameError:
    print("정의되지 않은 변수 호출 감지")</pre>
</details>

### Q8. 다중 예외 처리 (Multiple Except Blocks)
하나의 try 절 밑에 `ValueError`와 `TypeError`를 순서대로 적어 별도의 에러 메시지를 출력하게 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    # 연산
    pass
except ValueError:
    print("값 오류")
except TypeError:
    print("타입 오류")</pre>
</details>

### Q9. 예외 객체 메시지 출력 (as 키워드)
예외 객체를 `as e`로 지정하여 시스템이 던져주는 영어 원본 에러 메시지를 화면에 출력하는 방식을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    1 / 0
except ZeroDivisionError as e:
    print("에러원인:", e)</pre>
</details>

### Q10. finally 블록의 무조건 실행 속성
에러가 터지든 안 터지든 함수 리턴 직전에 반드시 실행하고 메모리에서 소거해야 하는 핵심 정리문을 기술하는 블록명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># finally 블록</pre>
</details>

### Q11. try-except-else 구조
try문에서 에러가 전혀 발생하지 않고 정상 성공적으로 끝났을 때만 추가 실행되는 블록 예약어 명칭을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># else 블록 (except 절 밑에 배치됩니다.)</pre>
</details>

### Q12. else 블록 구현 예제
`try: 10 / 2` 코드가 성공했을 때 else문을 타게 하여 `"나눗셈 성공"`을 출력하게 하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    res = 10 / 2
except ZeroDivisionError:
    print("오류")
else:
    print("나눗셈 성공:", res)</pre>
</details>

### Q13. 모든 예외를 잡는 최상위 클래스
파이썬의 거의 모든 시스템 예외를 일괄로 묶어 잡기 위해 except 절 뒤에 배치하는 부모 예외 클래스명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>except Exception as e:</pre>
</details>

### Q14. 예외를 그냥 흘려보내기 (pass)
에러가 나도 전혀 로깅이나 방해를 하지 않고 무시한 채 다음 코드로 통과시키기 위해 except 절 아래에 기재하는 키워드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    1 / 0
except ZeroDivisionError:
    pass</pre>
</details>

### Q15. 인위적 예외 유발 (raise)
개발자가 원할 때 조건 검사 후 시스템 에러를 강제로 발동시키는 예약어를 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>raise ValueError("개발자 강제 예외")</pre>
</details>

### Q16. 음수 수량 차단 raise 예제
전달된 매장 판매 수량 `qty`가 0보다 작으면 `ValueError("음수 수량 금지")`를 터트리는 함수를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def sell(qty):
    if qty < 0:
        raise ValueError("음수 수량 금지")
    print("판매 완료")</pre>
</details>

### Q17. 커스텀 예외 클래스 정의
`Exception`을 상속받아 사용자 고유 예외 `HmsDataError` 클래스를 한 줄 선언으로 설계해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>class HmsDataError(Exception):
    pass</pre>
</details>

### Q18. 커스텀 예외 내 에러 메시지 초기화
Q17의 `HmsDataError` 생성자에서 상세 원인을 받아 부모에게 super() 전달하는 형식 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class HmsDataError(Exception):
    def __init__(self, msg):
        super().__init__(f"[HMS DATA ERROR] {msg}")</pre>
</details>

### Q19. 최상위 시스템 강제 종료 예외 (SystemExit)
코드 진행 도중 `sys.exit()` 함수를 만나 시스템이 강제 다운될 때 발생하는 내부 특수 예외명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre># SystemExit 예외 (Exception 클래스로 잡히지 않고 BaseException 상위 계열에 속함)</pre>
</details>

### Q20. 키보드 인터럽트 예외 (KeyboardInterrupt)
사용자가 터미널 실행 도중 Ctrl + C 단축키를 눌러 프로세스를 강제 중지시켰을 때 포착되는 예외명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre># KeyboardInterrupt 예외</pre>
</details>

### Q21. try문 내부의 return과 finally 작동 순서
try 블록 안에서 return문을 만나 함수를 바로 탈출할 때, 그 아래 소속된 finally 블록은 무시되는지 여부를 기술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 무시되지 않습니다. return을 지시하더라도 CPU는 반드시 finally 블록을 마저 실행한 뒤 함수 제어권을 완전히 호출부에 돌려줍니다.</pre>
</details>

### Q22. 중첩 try-except문
try문 내부의 except 절 안에 또 다른 try-except 구문을 두어, 예외 복구 시도 시 일어날 2차 에러까지 안전하게 커버하는 구조를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    val = 10 / 0
except ZeroDivisionError:
    try:
        # 백업 복구 로직
        val = 10 / 1
    except Exception:
        print("2차 에러")</pre>
</details>

### Q23. 예외 전파 (Exception Propagation)
함수 A에서 에러가 터졌으나 A 내부에 try-except가 없습니다. 이 에러는 프로그램이 바로 중단되나요? 아니면 A를 호출한 상위 함수로 전파되나요?

<details><summary><b>정답 보기</b></summary>
<pre># 호출 스택을 거슬러 상위 호출 함수(Caller)로 에러가 계속 전파(Propagation)되며, 최상위 메인 쓰레드에서도 잡히지 않으면 최종 비정상 종료됩니다.</pre>
</details>

### Q24. 에러 추적 Traceback 모듈 로깅
발생한 에러의 정확한 소스코드 몇 번째 라인에서 꼬여서 유발되었는지 스택 흔적을 고스란히 덤프해 출력하는 표준 라이브러리명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>import traceback
try:
    1 / 0
except ZeroDivisionError:
    traceback.print_exc() # 상세 스택 트레이스 출력</pre>
</details>

### Q25. assert 단언문 기초
코드 내 조건 검사 결과가 무조건 참이어야 함을 단언하며, 거짓일 시 즉각 AssertionError를 유발해 버그를 초기에 조기 경보해주는 디버깅 예약어를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>x = 10
assert x > 0, "x는 반드시 양수여야 합니다."</pre>
</details>

### Q26. AssertionError 예외 처리
assert 단언문이 터졌을 때 발생하는 `AssertionError`를 try-except 문으로 포획해 경고 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    assert 1 == 2, "틀림"
except AssertionError as e:
    print("단언 오류 포착:", e)</pre>
</details>

### Q27. 예외 객체의 인자 속성 (__args__)
`raise ValueError("에러코드 400", "잘못된 파라미터")` 처럼 복수의 인자를 던졌을 때, 이 튜플 인자 목록을 꺼내오는 예외 객체 변수명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    raise ValueError("E400", "Invalid Parameter")
except ValueError as e:
    print(e.args) # ('E400', 'Invalid Parameter')</pre>
</details>

### Q28. 이중 예외 묶어서 처리
동일한 예외 핸들링을 적용하기 위해 `ValueError`와 `TypeError` 두 개의 에러를 한 except 절에서 묶어 잡는 튜플 지정 구문을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>except (ValueError, TypeError) as e:</pre>
</details>

### Q29. 빈 Exception 발생과 메시지 생략
메시지가 생략된 일반 `raise` 선언을 단독으로 try-except 바깥에 쓰면 어떤 에러가 나는지 여부를 기술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># catch 중인 except 블록 내부가 아닌 곳에서 단독으로 매개변수 없는 raise를 수행하면 RuntimeError: No active exception to reraise 오류가 유발됩니다. (받아 올릴 현재 진행형 예외가 없기 때문)</pre>
</details>

### Q30. 사용자 정의 예외의 활용 이점
실무 비즈니스 로직(예: 재고 부족, 로그인 차단 등)에서 시스템 일반 Exception 대신 사용자 정의 예외 클래스를 개별 선언해 사용하면 얻는 아키텍처적 장점을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 비즈니스 예외와 시스템 결함 예외를 명확히 격리할 수 있으며, 호출 클래스에서 비즈니스 케이스별 에러 처리 분기를 보다 안전하고 명시적으로 구현할 수 있게 도와줍니다.</pre>
</details>

---

### Q31 ~ Q70: 파일 입출력 (File I/O) 기본 연산
### Q31. 파일 열기 기본 함수 (open)
파일을 읽거나 쓰기 위해 가장 먼저 호출해야 하는 파이썬 빌트인 내장 함수명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>open()</pre>
</details>

### Q32. 파일 쓰기 모드 (Write Mode)
파일을 새로 생성하여 내용을 기록하되, 기존 파일이 있다면 그 내용을 전부 초기화하고 새로 덮어쓰는 오픈 모드 문자 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>"w"</pre>
</details>

### Q33. 파일 쓰기 예제
`"test.txt"` 파일을 열어 `"Hello"` 문자열을 쓰고 닫는 가장 기본 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>f = open("test.txt", "w", encoding="utf-8")
f.write("Hello")
f.close()</pre>
</details>

### Q34. 파일 닫기 누락 시 문제점
파일 쓰기를 마쳤으나 `f.close()`를 누락하여 리소스가 계속 열려 있을 때 윈도우 OS 시스템에서 발생할 수 있는 부작용을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 메모리 리소스 누수(Leak)가 일어나고, 다른 프로세스나 편집기에서 해당 파일에 락(Lock)이 걸려 읽기/수정/삭제가 불가능해지는 현상이 초래됩니다.</pre>
</details>

### Q35. With 구문을 이용한 파일 자동 닫기
Q33 코드를 close() 호출이 생략되도록 `with` 블록을 사용한 안전한 코드로 변경해 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("test.txt", "w", encoding="utf-8") as f:
    f.write("Hello")</pre>
</details>

### Q36. 파일 추가 쓰기 모드 (Append Mode)
기존 파일의 내용을 그대로 둔 상태에서 파일 꼬리 부분에 새로운 줄을 덧붙여 나가는 오픈 모드 기호를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>"a"</pre>
</details>

### Q37. 추가 기록 구현
`"test.txt"` 파일 끝에 줄바꿈 기호와 `"World"` 문장을 추가로 대입하는 appending 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("test.txt", "a", encoding="utf-8") as f:
    f.write("\nWorld")</pre>
</details>

### Q38. 파일 전체 읽기 모드 (Read Mode)
기존 파일을 읽어오기 위한 기본 모드 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>"r"</pre>
</details>

### Q39. 파일 전체 텍스트 수집 (read)
`"test.txt"` 전체 텍스트 데이터를 한 번에 하나의 문자열로 통째로 가져오는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)</pre>
</details>

### Q40. 파일 줄 단위 리스트 수집 (readlines)
파일의 각 행들을 하나의 문자열 요소로 취급하여 리스트 형태로 반환해 주는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("test.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    print(lines) # ['Hello\n', 'World']</pre>
</details>

### Q41. 대용량 파일을 위한 버퍼 순회 (for line in f)
수기가 기가바이트(GB)에 달하는 로그 파일을 readlines()로 읽으면 메모리 아웃(OOM)이 발생합니다. 메모리를 낭비하지 않고 한 줄씩 순차 로드하는 반복문 기법을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("large_server.log", "r", encoding="utf-8") as f:
    for line in f:
        # 버퍼에 한 줄씩만 올라와 스캔 진행
        print(line.strip())</pre>
</details>

### Q42. 파일 한 줄씩 순차 읽기 (readline)
루프를 돌지 않고 딱 한 줄의 행만 읽어와 포인터를 다음 행으로 넘겨주는 순차 읽기 메소드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("test.txt", "r", encoding="utf-8") as f:
    line1 = f.readline()
    print(line1)</pre>
</details>

### Q43. 한글 깨짐 방지 인코딩 속성 지정
윈도우 환경에서 저장한 한국어 텍스트 파일을 올바르게 부르기 위해 open 함수의 세 번째 매개변수로 선언하는 속성 명칭과 예시값을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre># encoding="utf-8" 또는 encoding="cp949"</pre>
</details>

### Q44. 바이너리 파일 쓰기 모드 (Binary Write)
이미지 파일이나 pickle 등의 객체 원형 데이터를 저장할 때 사용하는 바이너리 쓰기 모드 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>"wb"</pre>
</details>

### Q45. 바이너리 파일 읽기 모드 (Binary Read)
바이너리 데이터를 읽어오기 위한 모드 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>"rb"</pre>
</details>

### Q46. 파일 내부 위치 제어 (tell)
현재 파일 객체가 텍스트의 몇 번째 바이트 위치를 가리키며 읽고 있는지 마크 포인터 인덱스를 반환하는 메소드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># f.tell()</pre>
</details>

### Q47. 파일 내부 읽기 위치 강제 이동 (seek)
파일 포인터의 위치를 파일 맨 처음(0번 바이트) 위치로 강제 초기화하여 되돌려주는 메소드를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># f.seek(0)</pre>
</details>

### Q48. 파일 객체 닫힘 상태 검사 (closed)
현재 파일 스트림 `f`가 완전히 닫혀 무력화되었는지 Boolean으로 자가 체크하는 속성 변수명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("test.txt", "r") as f:
    pass
print(f.closed) # True</pre>
</details>

### Q49. 파일 존재 여부 선제 체크 (os.path)
파일을 open하기 전, 해당 경로에 파일이 실제로 물리 배치되어 있는지 검증하는 os 모듈 내 함수 호출문을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
print(os.path.exists("test.txt"))</pre>
</details>

### Q50. 파일명 및 확장자 격리 분리 (os.path.split)
경로 문자열 `"D:\QaReport\data.csv"`에서 디렉토리 경로와 파일명 `"data.csv"`를 한 줄로 분리해 주는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
dir_path, file_name = os.path.split(r"D:\QaReport\data.csv")
print(dir_path, file_name)</pre>
</details>

### Q51. 확장자만 단독 추출 (os.path.splitext)
파일명 `"invoice.pdf"`에서 확장자명 `".pdf"`만 안전하게 격리 추출해 내는 os 모듈 내 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
name, ext = os.path.splitext("invoice.pdf")
print(ext) # .pdf</pre>
</details>

### Q52. 파일 물리 복사 (shutil)
파일 복사를 수행하기 위해 임포트하여 사용하는 파이썬 표준 쉘 유틸리티 모듈명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import shutil
# shutil.copy("src.txt", "dest.txt")</pre>
</details>

### Q53. 파일 물리 이동/이름변경 (shutil.move)
임시 폴더의 파일을 실제 리포트 디렉토리로 옮기는 파일 이동 함수 호출 방식을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import shutil
# shutil.move("temp.txt", "D:\\QaReport\\temp.txt")</pre>
</details>

### Q54. 파일 강제 삭제 (os.remove)
임시 생성했던 파일 `"temp.txt"`를 디스크에서 즉각 삭제하는 os 모듈 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
# os.remove("temp.txt")</pre>
</details>

### Q55. 디렉토리 내부 파일 목록 조회 (os.listdir)
특정 경로 디렉토리 직속 부하인 모든 파일 및 폴더 이름 목록을 리스트로 뽑아내어 출력하는 함수를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
print(os.listdir(r"D:\hmTest\backoffice\QaReport"))</pre>
</details>

### Q56. os.walk를 이용한 하위 경로 재귀 탐색
지정한 루트 경로 아래에 속한 모든 하위 폴더와 파일 목록을 폴더 깊숙이 재귀 순회 탐색해 주는 os 모듈의 반복 제너레이터 함수명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
for root, dirs, files in os.walk("D:\\hmTest"):
    pass</pre>
</details>

### Q57. 디렉토리 단일 생성 (os.mkdir)
지정한 임시 폴더 하나만을 물리 생성하는 함수를 호출하세요 (부모 폴더가 없으면 에러남).

<details><summary><b>정답 보기</b></summary>
<pre>import os
# os.mkdir("temp")</pre>
</details>

### Q58. 하위 디렉토리까지 다중 생성 (os.makedirs)
부모 경로가 비어있더라도 `"D:\temp\sub1\sub2"` 처럼 명시한 계층 구조 전체를 일괄 강제 생성하는 안전한 폴더 생성 함수를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
# os.makedirs(r"D:\temp\sub1\sub2", exist_ok=True)</pre>
</details>

### Q59. 빈 디렉토리 제거 (os.rmdir)
비어 있는 특정 폴더 하나를 제거하는 함수를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
# os.rmdir("temp")</pre>
</details>

### Q60. 파일이 든 디렉토리 일괄 삭제 (shutil.rmtree)
내부에 여러 파일과 하위 서브 폴더가 잔뜩 채워진 폴더 전체를 에러 발생 없이 일괄 완전 강제 소거하는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import shutil
# shutil.rmtree("D:\\temp")</pre>
</details>

### Q61. 현재 작업 경로 조회 (os.getcwd)
현재 이 파이썬 스크립트 엔진이 명령을 실행 중인 물리 기본 경로(Current Working Directory)를 받아오는 함수를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
print(os.getcwd())</pre>
</details>

### Q62. 작업 경로 변경 (os.chdir)
스크립트 가동 중 실행 기본 경로를 다른 드라이브/폴더로 변경하는 함수를 쓰세요 (단, Antigravity 룰상 코드 내 제어 시에만 사용).

<details><summary><b>정답 보기</b></summary>
<pre>import os
# os.chdir(r"D:\hmTest")</pre>
</details>

### Q63. 경로 결합 유틸리티 (os.path.join)
운영체제(Windows `\` vs Linux `/`) 특성에 구애받지 않고, 폴더 경로와 파일명을 올바른 구분 문자로 병합해 주는 안전 경로 결합 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
full_path = os.path.join("D:\\QaReport", "data.csv")
print(full_path)</pre>
</details>

### Q64. 파일 크기 바이트 확인
지정한 파일의 실용 바이트 크기를 구하는 함수 호출 방식을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
print(os.path.getsize("test.txt"))</pre>
</details>

### Q65. 절대 경로로 전환 (os.path.abspath)
상대 경로 표기인 `".\test.txt"`를 운영체제 표준 절대 경로 문자열로 자동 보정하여 돌려받는 함수를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
print(os.path.abspath("test.txt"))</pre>
</details>

### Q66. 파일 여부 검증 (os.path.isfile)
해당 경로의 대상이 폴더가 아닌 순수 실제 '파일'이 맞는지 검증하는 Boolean 함수를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
print(os.path.isfile("test.txt"))</pre>
</details>

### Q67. 디렉토리 여부 검증 (os.path.isdir)
지정한 타겟이 파일이 아닌 실제 '폴더'가 맞는지 확인하는 함수를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
print(os.path.isdir("D:\\hmTest"))</pre>
</details>

### Q68. 파일 생성/수정 시간 획득 (os.path.getmtime)
파일의 최종 갱신(수정) 시간 에포크 값을 획득하는 함수를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
epoch_time = os.path.getmtime("test.txt")
print(epoch_time)</pre>
</details>

### Q69. 여러 문자열 라인 한 줄씩 일괄 쓰기 (writelines)
리스트 `lines = ["Line1\n", "Line2\n"]` 를 파일에 일괄 스트림 분출하여 기록하는 메소드를 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>lines = ["Line1\n", "Line2\n"]
with open("test.txt", "w") as f:
    f.writelines(lines)</pre>
</details>

### Q70. 파일 포인터의 개행 문자 자동 제거 습관
readlines()를 루프 돌 때 글자 끝단에 잔류하는 `\n` 개행을 깔끔히 자르기 위해 문자열 변수 뒤에 엮어 호출하는 빌트인 함수명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre># strip() 또는 rstrip()</pre>
</details>

---

### Q71 ~ Q100: 예외 처리와 파일 I/O 융합 실무형 문제
### Q71. 파일 열기 예외 대처 구조
존재하지 않는 파일을 읽으려 할 때 터지는 FileNotFoundError를 try-except 문으로 잡아 예외 상황 복구 메시지를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    with open("missing.txt", "r") as f:
        data = f.read()
except FileNotFoundError:
    print("해당 경로에 파일이 존재하지 않아 스킵합니다.")</pre>
</details>

### Q72. 쓰기 권한 부족 에러 포획 (PermissionError)
윈도우 시스템 파일 영역 등 읽기전용 속성이 지정된 파일에 강제 쓰기를 시도하다 발생하는 `PermissionError`를 핸들링해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>try:
    with open("C:\\protected.txt", "w") as f:
        f.write("test")
except PermissionError:
    print("쓰기 권한이 잠겨 있는 파일입니다.")</pre>
</details>

### Q73. CSV 파일의 행 개수 카운팅 함수
CSV 파일 경로를 입력받아, 데이터 총 레코드 라인수(헤더 라인 제외)를 계산하여 정수로 리턴하는 함수 `count_csv_rows(path)`를 안전 예외처리를 덧붙여 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def count_csv_rows(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return max(0, len(lines) - 1) # 헤더 1줄 차감
    except FileNotFoundError:
        return 0</pre>
</details>

### Q74. 파일 데이터 내 특정 키워드 카운팅
텍스트 파일 내에 `"ERROR"` 문자열이 최종 몇 번 써졌는지 검색 집계하여 리턴하는 함수를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def count_errors(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            return content.count("ERROR")
    except Exception:
        return 0</pre>
</details>

### Q75. 백업 파일 생성 자동화
원본 `"data.txt"` 내용을 읽어 완전히 동일한 내용의 복사본 `"data.txt.bak"` 파일을 새로 복제 저장하는 스크립트를 작성하세요 (shutil 미사용).

<details><summary><b>정답 보기</b></summary>
<pre>try:
    with open("data.txt", "r", encoding="utf-8") as src:
        content = src.read()
    with open("data.txt.bak", "w", encoding="utf-8") as dest:
        dest.write(content)
except Exception as e:
    print("백업 실패:", e)</pre>
</details>

### Q76. 빈 파일 임시 생성 터치 (Touch)
용량이 0바이트인 빈 텍스트 파일 `"empty.txt"`를 물리 생성하고 닫는 유틸리티 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("empty.txt", "w") as f:
    pass</pre>
</details>

### Q77. 파일 크기가 지정 수치를 넘을 때 백업 후 리셋
`"log.txt"` 파일 크기가 1MB(1,048,576 Bytes)를 초과하면 해당 파일을 `"log.txt.old"`로 이름 변경해 격리하고 새롭게 빈 `"log.txt"`를 생성하는 조건부 파일 핸들러를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
log_file = "log.txt"
if os.path.exists(log_file):
    if os.path.getsize(log_file) > 1048576:
        os.rename(log_file, "log.txt.old")
        with open(log_file, "w") as f:
            f.write("[System Reset]\n")</pre>
</details>

### Q78. 텍스트 파일 내 특정 행 치환 후 저장
`"config.txt"` 내용 중 `"TIMEOUT=30"` 라인을 찾아 `"TIMEOUT=60"`으로 글자를 변경하여 원본 파일에 그대로 업데이트 덮어쓰는 스크립트를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>config_file = "config.txt"
# 1. 읽기
with open(config_file, "r", encoding="utf-8") as f:
    lines = f.readlines()
# 2. 치환
new_lines = [line.replace("TIMEOUT=30", "TIMEOUT=60") for line in lines]
# 3. 덮어쓰기
with open(config_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)</pre>
</details>

### Q79. 예외 처리를 겸비한 임시 디렉토리 생성기
디렉토리 `"D:\temp"` 생성 시, 이미 해당 폴더가 존재하여 `FileExistsError` 에러가 발생하는 상황을 방지하도록 하는 try-except 처리 구조를 작성하세요 (exist_ok=True 옵션 미사용).

<details><summary><b>정답 보기</b></summary>
<pre>import os
try:
    os.mkdir("D:\\temp")
except FileExistsError:
    print("이미 폴더가 존재합니다. 생성을 건너뜁니다.")</pre>
</details>

### Q80. 파일 한 줄씩 번호 붙여 출력
`"test.txt"` 파일을 읽어 각 줄 앞에 행 번호 `"1: ", "2: "`를 접두어로 엮어서 출력하는 순회 루프를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("test.txt", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, start=1):
        print(f"{idx}: {line.strip()}")</pre>
</details>

### Q81. 다중 텍스트 파일 병합 스크립트
`"file1.txt"`와 `"file2.txt"` 두 파일의 텍스트 본문 내용을 차례대로 읽어 하나의 단일 파일 `"merged.txt"`로 연속 저장하는 합산 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>files_to_merge = ["file1.txt", "file2.txt"]
with open("merged.txt", "w", encoding="utf-8") as outfile:
    for fname in files_to_merge:
        try:
            with open(fname, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n") # 구분 개행
        except FileNotFoundError:
            pass</pre>
</details>

### Q82. 임의 데이터 문자열을 CSV 형태로 파일 내 저장
딕셔너리 리스트 `data = [{"id": "admin", "cnt": 1}, {"id": "shop1", "cnt": 3}]`를 CSV 구조 규격 텍스트 행으로 직렬화해 `"output.csv"`로 저장하세요.

<details><summary><b>정답 보기</b></summary>
<pre>data = [{"id": "admin", "cnt": 1}, {"id": "shop1", "cnt": 3}]
with open("output.csv", "w", encoding="utf-8") as f:
    f.write("id,cnt\n") # 헤더
    for item in data:
        f.write(f"{item['id']},{item['cnt']}\n")</pre>
</details>

### Q83. 특정 확장자 파일 일괄 삭제 자동화
임시 작업 대상 디렉토리 내에 있는 모든 `*.tmp` 확장자 파일을 찾아 자동으로 스캔 소거해 주는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
target_dir = "."
for fname in os.listdir(target_dir):
    if fname.endswith(".tmp"):
        os.remove(os.path.join(target_dir, fname))</pre>
</details>

### Q84. CSV 데이터 한 열의 총합계 연산
콤마 구분 구조인 CSV 데이터 파일에서 3번째 컬럼(매출 필드) 수치 데이터를 정수로 파싱하여 총합계를 구하는 함수를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def sum_sales_column(csv_path):
    total = 0
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            next(f) # 첫 헤더 라인 건너뛰기
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    total += int(parts[2])
    except Exception:
        pass
    return total</pre>
</details>

### Q85. 파일 입출력 모드 "x"의 특징
`open("data.txt", "x")` 모드를 실행할 때 기존에 이미 동일한 `"data.txt"` 파일이 컴퓨터에 자리 잡고 있으면 어떻게 동작하나요?

<details><summary><b>정답 보기</b></summary>
<pre># FileExistsError 예외를 의도적으로 터트려, 기존 중요 원본 파일의 불필요한 강제 덮어쓰기 파괴 현상을 원천 방어해 줍니다.</pre>
</details>

### Q86. os.rename의 이름 변경 범위
`os.rename("a.txt", "b.txt")`는 단순히 이름만 바꾸는 것에 한정되나요, 아니면 경로가 포함되어 있을 시 다른 폴더로의 파일 강제 이동 효과까지 동시 수행하는가요?

<details><summary><b>정답 보기</b></summary>
<pre># 다른 폴더 경로(예: os.rename("a.txt", "D:\\temp\\b.txt"))를 입력하면 이동(Move) 효과까지 동시에 발휘해 줍니다.</pre>
</details>

### Q87. 텍스트 파일 뒤에서부터 N줄 읽기 (Tail 기능 구현)
용량이 크지 않은 텍스트 파일의 하단 최종 3줄만 라인을 따와 콘솔에 출력하는 코드를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("test.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines[-3:]:
        print(line.strip())</pre>
</details>

### Q88. 인코딩 에러 무시하고 읽기 (errors="ignore")
텍스트 파일 로드 도중 간헐적으로 섞인 깨진 바이너리 찌꺼기 문자로 인해 UnicodeDecodeError 발생으로 실행이 멈추는 것을 막기 위해 open 함수 옵션으로 줄 수 있는 속성을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre># open("data.txt", "r", errors="ignore")</pre>
</details>

### Q89. 대량의 파일 복사 시 시간 소요 예외 처리
파일 복사를 수행하다 취소 단축키 시그널 등으로 인터럽트가 걸리더라도 복사 시도 중이던 미완성 임시 생성 타겟 파일을 말끔히 지우도록 보장하는 finally 블록을 작성해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os, shutil
src, dest = "large_src.dat", "large_dest.dat"
try:
    shutil.copy(src, dest)
except KeyboardInterrupt:
    print("복사 취소됨")
    if os.path.exists(dest):
        os.remove(dest)</pre>
</details>

### Q90. 텍스트 라인 데이터 내 공백 줄 걸러내어 저장
`"data.txt"` 내부 텍스트 행 중 아무 글자도 없이 엔터만 쳐진 공백 행들을 걸러내고 알짜 정보 라인들만 정제하여 `"cleaned.txt"`에 모으세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("data.txt", "r", encoding="utf-8") as infile:
    lines = infile.readlines()

valid_lines = [line for line in lines if line.strip()]

with open("cleaned.txt", "w", encoding="utf-8") as outfile:
    outfile.writelines(valid_lines)</pre>
</details>

### Q91. JSON 형식 데이터 텍스트 파일 저장
딕셔너리 구조를 문자열로 수동 변환해 일반 텍스트 파일에 라이팅하여 덤프하는 코드를 구현하세요 (json 모듈 사용 없이 str 캐스팅 기준).

<details><summary><b>정답 보기</b></summary>
<pre>data = {"role": "ADMIN", "locked": "N"}
with open("state.txt", "w", encoding="utf-8") as f:
    f.write(str(data))</pre>
</details>

### Q92. 텍스트 파일에서 읽은 문자열 사전 복원
Q91에서 수동으로 문자로 덤프하여 저장한 파일 데이터를 다시 읽어와 파이썬 딕셔너리 데이터 타입 객체로 복원(역직렬화)하는 내장 함수를 호출하세요. (힌트: `eval()`)

<details><summary><b>정답 보기</b></summary>
<pre>with open("state.txt", "r", encoding="utf-8") as f:
    content = f.read()
    recovered_dict = eval(content)
print(type(recovered_dict), recovered_dict["role"])</pre>
</details>

### Q93. 쓰기 전용 + 신규 생성 모드 조합 "w+"
쓰기와 읽기를 동시에 수행하기 위해 open 모드에 추가 지정하는 `+` 기호 모드 종류 중 `"w+"` 모드의 위험성을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 읽기 작업도 병행 가능하지만, 오픈하는 그 순간 w 속성으로 인해 기존 원본 파일 내용이 백그라운드에서 완전히 초기화되어 0바이트로 파괴되어 버립니다.</pre>
</details>

### Q94. 기존 내용 보존 + 읽기/쓰기 모드 조합 "r+"
Q93과 달리 기존에 이미 들어있는 텍스트 데이터를 그대로 유지한 채로 원하는 포인터 위치로 이동해 쓰거나 읽어올 수 있게 만드는 안전 병행 모드 기호를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>"r+"</pre>
</details>

### Q95. 텍스트 파일 특정 단어 검색 줄 번호 로깅
`"server.log"` 파일 내에서 `"FATAL"` 단어가 들어있는 행을 찾아 해당 행의 텍스트 정보와 실제 **줄 번호(1부터 시작)**를 묶어 화면에 보고하는 코드를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("server.log", "r", encoding="utf-8") as f:
    for num, line in enumerate(f, start=1):
        if "FATAL" in line:
            print(f"[{num}번째 줄] {line.strip()}")</pre>
</details>

### Q96. 지정 경로 아래 모든 파일 정보 딕셔너리 수집
특정 폴더 아래에 속한 파일들의 파일명과 파일 크기(Byte) 정보를 키와 값 쌍으로 수집한 딕셔너리를 빌드하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
target = "."
file_sizes = {}
for name in os.listdir(target):
    full = os.path.join(target, name)
    if os.path.isfile(full):
        file_sizes[name] = os.path.getsize(full)
print(file_sizes)</pre>
</details>

### Q97. 예외 처리를 이용한 안전한 디렉토리 삭제
지정한 디렉토리가 비어있지 않거나 권한이 없어서 삭제에 실패할 때 발생하는 시스템 예외를 받아 안전 스킵하는 구조를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
try:
    os.rmdir("temp_dir")
except OSError as e:
    print("디렉토리 삭제 실패 (비어있지 않음 등):", e)</pre>
</details>

### Q98. 텍스트 파일의 첫 줄(헤더)만 분리 스캔
CSV 리포트 파일 `"report.csv"` 에서 컬럼 명칭들이 줄지어 기술되어 있는 최상단 1열 헤더 문자열 라인만 따서 출력하고 즉각 파일을 닫는 구문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>with open("report.csv", "r", encoding="utf-8") as f:
    header = f.readline().strip()
print("컬럼 헤더 정보:", header)</pre>
</details>

### Q99. 파일 쓰기 중 디스크 꽉 참 예외 대비
파일 쓰기 작업 도중 하드 디스크 용량 한계로 쓰기에 완전히 실패하여 뻗어버릴 때 터지는 운영체제 연동 표준 예외명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># OSError 예외(디스크 부족 등 포함)가 발생합니다.</pre>
</details>

### Q100. 카테고리 6 종합 문제
다음 시나리오를 충실히 따르는 파일 처리 프로그램을 구현하세요.
1. `"D:\hmTest\backoffice\QaReport"` 디렉토리 내에 `"progress.log"` 텍스트 파일을 open 모드로 엽니다.
2. 파일이 아예 존재하지 않는 오류(`FileNotFoundError`) 발생 시, 자동으로 해당 경로에 빈 파일을 자동 신규 생성하고 `"[LOG START]\n"` 문자열을 최초 기록해 방어 조치합니다.
3. 파일 로드에 성공하면 파일 하단에 현재 연도-월-일 시각 로그 정보인 `"2026-07-06 18:00 - Config Applied\n"` 문자열을 추가로 덧붙여 기록하고 안전하게 마무리 닫기 처리하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os

dir_path = r"D:\hmTest\backoffice\QaReport"
file_path = os.path.join(dir_path, "progress.log")

try:
    # 1. 파일 기존 읽기 시도
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    print("기존 로그 파일 확인 완료")
except FileNotFoundError:
    # 2. 파일이 없으면 상위 폴더까지 일괄 강제 생성 후 최초 쓰기 기동
    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("[LOG START]\n")
    print("로그 파일을 신규 생성했습니다.")

# 3. 마지막 단계: 추가 데이터 Appending 진행
with open(file_path, "a", encoding="utf-8") as f:
    f.write("2026-07-06 18:00 - Config Applied\n")
print("로그 덧붙이기 완료")</pre>
</details>
