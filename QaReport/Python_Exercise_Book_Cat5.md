# Python 실전 연습 문제집 - [카테고리 5] 클래스와 객체 지향 (100제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"Cat5"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py Cat5 Q1 True` (Q1 문제를 완료로 변경)


본 문제집은 파이썬의 클래스 모델링 기법, 생성자 `__init__`, 멤버/인스턴스 변수, 정보 은닉(Private), 상속과 `super()`, 스페셜 메소드(`__str__` 등), 스태틱 메소드(`@staticmethod`), 다형성 및 메모리 깊은/얕은 복사 등에 관한 100문제와 해설식 정답을 수록하고 있습니다.

---

### Q1 ~ Q30: 클래스 기초 정의 및 속성
### Q1. 클래스 선언 기본 키워드
파이썬에서 클래스 구조체를 정의하는 키워드와 작명 규칙(CamelCase)을 간단한 예시 코드로 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>class HmsSystem:
    pass</pre>
</details>

### Q2. 생성자 함수 정의
객체 생성 시 자동 호출되어 초기 멤버 변수를 바인딩해 주는 생성자 메소드명을 정확한 문법 형태로 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __init__(self):
    pass</pre>
</details>

### Q3. Self 인자의 정체 및 역할
파이썬 클래스 내 모든 인스턴스 메소드의 첫 번째 인자로 반드시 전달되어야 하는 `self` 인자의 역할을 기술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># self는 현재 호출된 인스턴스(객체) 자기 자신을 가리키는 포인터 변수입니다.</pre>
</details>

### Q4. 멤버 변수 등록 초기화
이름 `name`을 받아 객체 내 멤버 변수 `self.name`에 초기 바인딩하는 생성자를 포함한 `User` 클래스를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class User:
    def __init__(self, name):
        self.name = name</pre>
</details>

### Q5. 인스턴스 생성 및 접근
Q4의 `User` 클래스 인스턴스 `u`를 이름 `"홍길동"`으로 생성하고, 멤버 변수를 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>u = User("홍길동")
print(u.name)</pre>
</details>

### Q6. 인스턴스 메소드 정의 및 호출
`User` 클래스 내에 `"안녕하세요, [이름]입니다."` 문장을 출력하는 `introduce(self)` 메소드를 추가하고 실행하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class User:
    def __init__(self, name):
        self.name = name
    def introduce(self):
        print(f"안녕하세요, {self.name}입니다.")

u = User("홍길동")
u.introduce()</pre>
</details>

### Q7. 동적 속성 추가 (Dynamic Attribute)
파이썬에서는 클래스 정의에 없더라도 생성된 객체 외부에 변수를 강제 주입해 사용할 수 있습니다. u 객체에 임의로 `u.age = 20`을 추가한 후 출력해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>u = User("홍길동")
u.age = 20
print(u.age)</pre>
</details>

### Q8. 인스턴스 변수 수정
u 객체의 `u.name` 변수 값을 `"임꺽정"`으로 수정한 후 u.introduce()를 다시 호출하세요.

<details><summary><b>정답 보기</b></summary>
<pre>u = User("홍길동")
u.name = "임꺽정"
u.introduce() # 안녕하세요, 임꺽정입니다.</pre>
</details>

### Q9. 클래스 변수 (Class Variables) 선언
모든 매장 객체가 공유하는 고유 회사명 `company = "HMS"` 클래스 변수를 포함한 `Store` 클래스를 정의하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Store:
    company = "HMS" # 클래스 변수
    def __init__(self, code):
        self.code = code # 인스턴스 변수</pre>
</details>

### Q10. 클래스 변수 접근 기법
Q9의 `Store` 클래스 변수 `company`를 객체 생성 없이 바로 출력하는 구문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(Store.company) # HMS</pre>
</details>

### Q11. 클래스 변수 수정의 영향 범위
`Store.company = "HYUNDAI"` 로 클래스 변수를 갱신하면, 기존에 생성되어 있던 매장 객체들의 `company` 변수값도 일괄 변하나요?

<details><summary><b>정답 보기</b></summary>
<pre># 네, 모든 객체가 공유하는 주소 공간이므로 일괄 수정 적용됩니다.</pre>
</details>

### Q12. 빈 클래스 생성 후 속성 조작
본문이 pass로 선언된 빈 클래스 `Empty`의 인스턴스를 만들고, 동적으로 변수를 주입하는 테스트를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Empty:
    pass

e = Empty()
e.val = 100
print(e.val)</pre>
</details>

### Q13. 매개변수가 여러 개인 생성자
매장코드 `code`, 매출액 `sales`를 받아 초기화하고, 부가세 10%를 계산하여 멤버 변수 `self.vat`에 자동 바인딩하는 생성자를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Shop:
    def __init__(self, code, sales):
        self.code = code
        self.sales = sales
        self.vat = int(sales * 0.1)</pre>
</details>

### Q14. 클래스 소멸자 (__del__)
객체가 가비지 컬렉터에 의해 소멸되는 시점에 `"객체 소멸"` 문구를 찍어주는 스페셜 메서드명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __del__(self):
    print("객체 소멸")</pre>
</details>

### Q15. 인스턴스 메소드 내에서 다른 메소드 호출
클래스 내 `A(self)` 메소드가 `B(self)` 메소드를 내부에서 호출하고 싶을 때 사용하는 구문을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># self.B() 형태로 self 포인터를 명시하여 호출합니다.</pre>
</details>

### Q16. 클래스의 인스턴스 검증 (isinstance)
`isinstance(obj, ClassName)` 함수를 사용해 u 객체가 `User` 클래스의 실체인지 확인하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(isinstance(u, User)) # True</pre>
</details>

### Q17. 클래스 타입 확인 (type)
u 객체의 실제 소속 클래스명을 문자열 타입 정보로 확인 출력해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(type(u)) # &lt;class '__main__.User'&gt;</pre>
</details>

### Q18. 객체 속성 사전 조회 (__dict__)
u 객체 내부의 모든 속성 변수명과 바인딩 데이터 값들의 딕셔너리 지도를 보여주는 내장 변수명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(u.__dict__)</pre>
</details>

### Q19. 디폴트 매개변수를 지닌 생성자
사원의 급여 정보를 받되, 전송이 생략되면 기본으로 `300`만 원으로 채우는 생성자를 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Emp:
    def __init__(self, name, salary=300):
        self.name = name
        self.salary = salary</pre>
</details>

### Q20. 가변 인자를 수용하는 생성자
`*args`를 전달받아 `self.items` 리스트에 튜플로 한 번에 초기 대입 저장하는 생성자를 지닌 `Cart` 클래스를 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Cart:
    def __init__(self, *args):
        self.items = list(args)</pre>
</details>

### Q21. 객체 속성 존재 체크 (hasattr)
`hasattr(obj, "age")` 함수를 사용하여 u 객체에 `"age"` 변수가 존재하는지 유무를 Boolean으로 확인하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(hasattr(u, "age"))</pre>
</details>

### Q22. 객체 속성 제거 (delattr)
`delattr(obj, "age")` 함수를 사용하여 u 객체 내의 `"age"` 속성을 동적으로 영구 삭제해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>delattr(u, "age")</pre>
</details>

### Q23. 클래스 이름 문자열 구하기 (__name__)
`User` 클래스로부터 문자열 클래스명 `"User"`를 얻기 위해 호출하는 내장 특수 변수명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(User.__name__)</pre>
</details>

### Q24. 인스턴스 메소드에서 클래스 변수 호출
인스턴스 메소드 내부에서 클래스 변수 `company`를 self가 아닌 클래스명을 통해 참조하는 관례적인 이유를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># self.company로 불러올 수도 있으나, Store.company와 같이 호출함으로써 인스턴스 고유 변수가 아닌 모든 클래스가 공유하는 정적 변수임을 코드상으로 명확히 표현하기 위해서입니다.</pre>
</details>

### Q25. 객체의 주소값 비교 (is)
두 참조 변수 `a`와 `b`가 완전히 동일한 주소의 객체를 가리키고 있는지 판별하는 비교 예약어 키워드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># is 키워드를 사용합니다. (예: a is b)</pre>
</details>

### Q26. 객체의 내용값 비교 (==)
두 객체 내부 데이터 내용이 논리적으로 같은지 비교하기 위해 사용하는 연산자를 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># == 연산자를 사용합니다. (클래스 내 __eq__ 연동)</pre>
</details>

### Q27. 클래스 내 정적 문자열 상수의 정의
클래스 레벨에서 선언하는 상수들은 대문자 작명 관례를 따른다는 점을 코드로 표시하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Config:
    MAX_RETRY = 5</pre>
</details>

### Q28. 속성 바인딩 함수 (setattr)
`setattr()` 함수를 사용하여 u 객체의 `"salary"` 속성 값을 `500`으로 동적 생성/대입하는 문장을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>setattr(u, "salary", 500)</pre>
</details>

### Q29. 속성 값 조회 함수 (getattr)
`getattr()` 함수를 사용하여 u 객체의 `"salary"` 속성 값을 가져오되, 없는 속성일 시 `0`이 반환되도록 기본값을 매핑하세요.

<details><summary><b>정답 보기</b></summary>
<pre>val = getattr(u, "salary", 0)
print(val)</pre>
</details>

### Q30. 클래스 내부 변수 리스트화
`dir()` 내장 함수를 클래스에 대입하여 클래스가 품고 있는 모든 특수 함수 및 메소드 목록을 스캔해 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(dir(User))</pre>
</details>

---

### Q31 ~ Q50: 클래스 상속 (Inheritance) 및 메소드 오버라이딩
### Q31. 자식 클래스 상속 선언
부모 클래스 `Parent`를 자식 클래스 `Child`가 상속받는 기본 클래스 정의부 괄호 문법을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Child(Parent):
    pass</pre>
</details>

### Q32. 부모 생성자 명시적 호출 (super)
자식 클래스 생성자 내에서 부모 클래스의 생성자(`__init__`)를 안정적으로 상속 호출해 주는 파이썬 내장 대행어 키워드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>super().__init__()</pre>
</details>

### Q33. 부모 필드 상속 초기화 응용
부모 `User` 클래스가 `id`를 받습니다. 자식 `Admin` 클래스는 `id`와 `level`을 매개변수로 받아 부모 필드를 super()로 채우고 `level`을 별도 초기화하는 생성자를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class User:
    def __init__(self, id):
        self.id = id

class Admin(User):
    def __init__(self, id, level):
        super().__init__(id)
        self.level = level</pre>
</details>

### Q34. 메소드 재정의 (Method Overriding)
부모 클래스의 `work(self)` 메소드는 `"기본 업무"`를 출력합니다. 자식 클래스에서 이를 덮어써서 `"관리 업무"`를 출력하게 상속 오버라이딩을 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Parent:
    def work(self):
        print("기본 업무")

class Child(Parent):
    def work(self):
        print("관리 업무")</pre>
</details>

### Q35. 다중 상속 선언 문법
자식 클래스가 두 개의 부모 클래스 `A`, `B`를 동시 다중 상속받는 클래스 머리 부분 문법을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Child(A, B):
    pass</pre>
</details>

### Q36. 상속 계층의 인스턴스 확인 (issubclass)
`issubclass(Child, Parent)` 함수를 사용하여 `Child` 클래스가 `Parent` 클래스의 서브(자식) 상속형인지 판별하세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(issubclass(Child, Parent)) # True</pre>
</details>

### Q37. 오버라이딩 상태에서 부모 메소드 강제 호출
자식 클래스 오버라이딩 메소드 내부에서, 이미 재정의된 부모 클래스의 원본 `work()` 메소드를 강제로 호출하는 super() 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Child(Parent):
    def work(self):
        super().work() # 부모 원본 실행
        print("추가 관리 업무")</pre>
</details>

### Q38. 다중 상속 시의 메소드 탐색 순서 MRO (Method Resolution Order)
다중 상속 시 어떤 부모의 메소드를 먼저 실행할지 결정하는 메소드 탐색 우선순위(MRO) 경로 리스트를 출력해 주는 클래스 속성을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>print(Child.__mro__)
# 또는
print(Child.mro())</pre>
</details>

### Q39. 상속 관계에서의 클래스 변수 덮어쓰기
부모 클래스의 클래스 변수 `company = "HMS"`를 자식 클래스 내부에서 `company = "HMS_ST"`로 선언하면 어떻게 동작하나요?

<details><summary><b>정답 보기</b></summary>
<pre># 자식 클래스 및 그 인스턴스들의 company 값은 "HMS_ST"로 오버라이드되며, 부모 클래스 원본 객체의 company는 "HMS"로 온전히 보존됩니다.</pre>
</details>

### Q40. 자바와 파이썬 다중상속 차이점
Java와 달리 Python은 여러 클래스를 동시에 다중 상속(Multiple Inheritance)하는 것을 기본 허용하나요?

<details><summary><b>정답 보기</b></summary>
<pre># 네, 파이썬은 다중 상속을 완전 지원합니다. 이로 인해 생기는 죽음의 다이아몬드 문제는 C3 선형화 알고리즘(MRO 탐색 순서)으로 내부 해결됩니다.</pre>
</details>

### Q41. 다중 상속 시 중복 메소드 해결 우선권
`class Child(A, B):` 로 정의되어 있고 두 부모가 모두 `process()`를 가질 때, `Child` 인스턴스가 `process()`를 부르면 어느 쪽이 먼저 실행되나요?

<details><summary><b>정답 보기</b></summary>
<pre># 괄호 왼쪽에 먼저 나열된 부모 A 클래스의 메소드가 우선권을 갖고 실행됩니다.</pre>
</details>

### Q42. 상속 불가 클래스 디자인
파이썬에는 Java의 final class처럼 상속을 원천 차단하는 예약어가 없습니다. 통상적으로 상속하지 말 것을 의미하는 변수 작명 관례는 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># 관례상 언더바 2개(__)를 붙여 정보은닉하거나 주석 또는 TypeHint(typing.final 데코레이터)를 사용하여 명시적으로 상속 불가함을 알립니다.</pre>
</details>

### Q43. 부모 클래스 필드 강제 업데이트
자식 메소드 내에서 부모로부터 상속받은 변수 `self.id` 값을 갱신하는 코드를 안전하게 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Child(Parent):
    def update_id(self, new_id):
        self.id = new_id</pre>
</details>

### Q44. 추상 클래스 기초 (abc 모듈)
추상 메서드 `@abstractmethod`를 명시하고 이를 강제 재정의하게 만드는 파이썬의 표준 패키지명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># abc (Abstract Base Classes) 모듈을 사용합니다.</pre>
</details>

### Q45. 추상 클래스 상속 구현
`ABC`를 상속받고 `@abstractmethod`로 선언된 `calc()` 추상 메소드를 포함하는 부모 클래스 `Base`를 골격 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from abc import ABC, abstractmethod

class Base(ABC):
    @abstractmethod
    def calc(self):
        pass</pre>
</details>

### Q46. 추상 메소드 미구현 시 발생하는 런타임 오류
추상 클래스를 상속받은 자식이 추상 메소드를 오버라이딩하지 않고 인스턴스를 생성하려 할 때 파이썬 인터프리터가 던지는 예외를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># TypeError 예외가 발생하여 객체 생성이 원천 차단됩니다.</pre>
</details>

### Q47. 추상 클래스 활용 다형성
추상 베이스 상속 객체 `b`의 추상 메소드를 오버라이딩하여 자식 클래스를 완전히 실체 구현하는 코드를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Child(Base):
    def calc(self):
        print("실제 연산 수행")

c = Child()
c.calc()</pre>
</details>

### Q48. 인스턴스 속성(Attribute) 동적 제한 (__slots__)
새로운 멤버 변수를 외부에서 주입해 마음대로 늘려 나갈 수 있는 파이썬의 동적 바인딩 특징을 차단하고, 오직 지정한 변수명(`name`, `age`)들만 사용하도록 성능 최적화 잠금을 거는 특수 클래스 선언 키워드를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>class LockedClass:
    __slots__ = ["name", "age"]  # 이외의 속성 추가 시도 시 AttributeError 발생</pre>
</details>

### Q49. slots 적용 시 이점
Q48의 slots 속성을 부여했을 때 성능상/메모리상 생기는 핵심 이점을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 각 객체별로 속성 사전을 보관하는 무거운 __dict__ 객체가 내부적으로 생성되지 않으므로, 메모리 오버헤드가 극적으로 줄어들고 속성 참조 속도가 빨라집니다.</pre>
</details>

### Q50. 상속받은 slots 변수 확장성
부모 클래스에 slots가 선언되었을 때, 자식 클래스에서 slots 속성을 상속받아 사용하려면 자식 클래스에서도 slots를 명시해야 하는가요?

<details><summary><b>정답 보기</b></summary>
<pre># 네, 자식 클래스에서도 __slots__ = () 처럼 빈 튜플 형태로 선언이라도 해두어야 부모의 속성 사전 배제 기능이 유지됩니다. 그렇지 않으면 자식은 다시 __dict__를 생성하게 됩니다.</pre>
</details>

---

### Q51 ~ Q75: 정보 은닉 (Private) 및 프로퍼티, 스페셜 메소드
### Q51. Private 멤버 변수 선언
클래스 밖에서 직접 변수에 접근하는 것을 차단(캡슐화)하기 위해 변수명 앞에 붙이는 기호 두 개를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 언더스코어 2개 (__)를 변수명 앞에 붙여 Private로 선언합니다. (예: self.__salary)</pre>
</details>

### Q52. 네임 맹글링 (Name Mangling) 원리
파이썬은 private로 선언한 `__salary`를 컴파일 단계에서 `_클래스명__salary` 형태로 이름을 강제 변환하여 보호합니다. 이러한 은닉화 작동 방식을 가리키는 기법명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 네임 맹글링 (Name Mangling) 또는 이름 변형 기법입니다.</pre>
</details>

### Q53. Getter / Setter 메소드 기본
Private 변수 `self.__age`를 안전하게 반환하고 유효성 검사 후 변경하는 getter/setter 구조를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Person:
    def __init__(self, age):
        self.__age = age
    def get_age(self):
        return self.__age
    def set_age(self, age):
        if age > 0:
            self.__age = age</pre>
</details>

### Q54. 프로퍼티 데코레이터 (@property)
메소드를 마치 변수 속성처럼 `obj.age` 형태로 접근하여 값을 안전하게 Getter 처리할 수 있게 꾸며주는 데코레이터명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>@property</pre>
</details>

### Q55. 프로퍼티 세터 지정 (@property.setter)
Q54의 프로퍼티 속성에 값을 대입할 때(`obj.age = 25`) 실행되는 Setter 데코레이터 지정 형식을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>@age.setter</pre>
</details>

### Q56. @property를 활용한 캡슐화 완성
`Person` 클래스의 Private 변수 `self.__age`를 getter/setter 프로퍼티 데코레이터 방식으로 구현하여 대입/조회 테스트를 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Person:
    def __init__(self, age):
        self.__age = age
        
    @property
    def age(self):
        return self.__age
        
    @age.setter
    def age(self, value):
        if value > 0:
            self.__age = value

p = Person(20)
p.age = 25  # setter 실행
print(p.age)  # getter 실행</pre>
</details>

### Q57. 클래스 정보 출력 스페셜 메소드 (__str__)
사용자가 `print(obj)`를 하거나 `str(obj)`로 문자열 변환을 시도할 때 반환할 사용자 친화적 가독 정보를 정의하는 특수 메소드명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __str__(self):
    return "설명"</pre>
</details>

### Q58. 개발용 디버깅 정보 출력 스페셜 메소드 (__repr__)
코드 디버깅이나 REPL 셸 환경에서 객체의 원형 상태 정보를 가식적으로 정확하게 리턴해 주는 개발용 특수 메소드명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __repr__(self):
    return "클래스명(파라미터들)"</pre>
</details>

### Q59. __str__과 __repr__의 우선권 관계
클래스 내에 `__str__`과 `__repr__`이 동시에 정의되어 있고 `print(obj)`를 수행했을 때, 파이썬이 우선순위를 두고 가져오는 메소드는 무엇인가요?

<details><summary><b>정답 보기</b></summary>
<pre># __str__ 이 우선권을 갖고 호출됩니다. __str__이 없으면 대안으로 __repr__ 결과가 출력됩니다.</pre>
</details>

### Q60. 객체를 함수처럼 호출 가능하게 만드는 스페셜 메소드 (__call__)
생성된 인스턴스 객체에 괄호를 붙여 `obj(10, 20)` 과 같이 마치 일반 함수인 것처럼 실행시키는 기능을 제공하는 내장 스페셜 메소드명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Calc:
    def __call__(self, x, y):
        return x + y

c = Calc()
print(c(5, 5)) # 10 (__call__ 내부 실행됨)</pre>
</details>

### Q61. 객체의 덧셈 연산 오버로딩 (__add__)
두 객체를 더하는 연산(`obj1 + obj2`)이 가동되도록 덧셈 산술 연산자를 클래스 레벨에서 재정의하는 메소드명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __add__(self, other):
    pass</pre>
</details>

### Q62. 객체의 뺄셈 연산 오버로딩 (__sub__)
두 객체의 뺄셈 연산(`obj1 - obj2`)을 정의하는 내장 특수 메소드명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __sub__(self, other):
    pass</pre>
</details>

### Q63. 객체의 동등성 비교 재정의 (__eq__)
두 객체의 데이터 내용이 같음을 비교하는 `==` 연산자의 상세 비교 로직을 정의하는 스페셜 메소드명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __eq__(self, other):
    # 인스턴스 간 특정 멤버 변수 값이 같으면 True를 리턴하도록 재정의
    pass</pre>
</details>

### Q64. 객체 크기 크다 비교 재정의 (__gt__)
두 객체의 대소 관계 `obj1 > obj2` 연산 시 작동되는 크다(Greater Than) 비교 메소드명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __gt__(self, other):
    pass</pre>
</details>

### Q65. 객체의 길이값 재정의 (__len__)
`len(obj)` 함수를 호출했을 때, 객체가 보유한 컬렉션의 크기를 정수로 계산해 돌려주도록 재정의하는 특수 메소드명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __len__(self):
    return 0</pre>
</details>

### Q66. 객체 내부 속성 접근 차단자 (__getattr__)
객체 내에 존재하지 않는 속성에 접근하려 할 때(`obj.non_exist`), AttributeError를 내지 않고 특정 대체 문구를 동적으로 반환해주는 특수 스크립트 메소드명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __getattr__(self, name):
    return f"속성 {name}은 존재하지 않습니다."</pre>
</details>

### Q67. 인스턴스 메소드 vs 클래스 메소드 vs 스태틱 메소드
메소드 종류를 결정짓는 데코레이터 없이 첫 인자로 self를 기본 바인딩받아 인스턴스 고유 정보와 통신하는 정규 메소드 명칭을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># 인스턴스 메소드 (Instance Method)</pre>
</details>

### Q68. 클래스 메소드 (@classmethod)
첫 번째 인자로 객체 인스턴스가 아닌 클래스 자체(`cls`)를 바인딩받도록 제어하며, 팩토리 패턴 등을 설계할 때 사용되는 데코레이터명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>@classmethod</pre>
</details>

### Q69. 클래스 메소드의 cls 인자 역할
`cls` 인자를 통해 함수 내에서 클래스 생성자나 클래스 변수 등에 접근할 수 있나요?

<details><summary><b>정답 보기</b></summary>
<pre># 네, cls는 클래스 자체의 정보이므로 cls(args)를 호출해 신규 객체를 찍어내거나 클래스 변수를 바로 가공할 수 있습니다.</pre>
</details>

### Q70. 스태틱 메소드 (@staticmethod)
`self`나 `cls` 같은 첫 번째 매개변수 바인딩 없이, 일반 독자 함수와 성격이 완전히 같으나 논리적 그룹화를 위해 클래스 내부에 봉인 보관하는 정적 메소드 데코레이터를 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>@staticmethod</pre>
</details>

### Q71. 스태틱 메소드와 클래스 메소드의 상속 시 작동 차이점
부모 클래스의 정적 메소드를 자식 클래스에서 상속받아 호출할 때, 호출하는 주체 자식 클래스(`cls`)의 정보가 연동되어 다형성있게 변경된 클래스 속성을 타게 만드는 메소드 유형은 어느 것인가요?

<details><summary><b>정답 보기</b></summary>
<pre># 클래스 메소드(@classmethod)입니다. cls 파라미터가 호출한 클래스 컨텍스트를 동적으로 주입받기 때문입니다. 스태틱 메소드는 이를 알지 못합니다.</pre>
</details>

### Q72. 단일 객체 인스턴스 보장 (싱글톤 패턴)
프로그램 전역에서 오직 단 하나의 클래스 인스턴스만 생성되어 공유되도록 강제하는 디자인 패턴명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># 싱글톤 (Singleton) 패턴</pre>
</details>

### Q73. 싱글톤 패턴 파이썬 구현 (__new__)
객체 초기화 생성자(`__init__`) 작동 이전에 실제 메모리에 객체를 최초 할당해 리턴해 주는 `__new__` 메소드를 오버라이딩하여 싱글톤 패턴을 파이썬식으로 구현해 보세요.

<details><summary><b>정답 보기</b></summary>
<pre>class SingletonClass:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance</pre>
</details>

### Q74. 정보 은닉을 적용한 계좌 계정 정보 클래스
잔액 `__balance` 속성을 private로 두고 입금 `deposit()` 과 출금 `withdraw()` 기능만 열어두되, 직접 잔액을 조작하려 하면 예외를 던지는 계좌 클래스 골격을 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Account:
    def __init__(self, balance):
        self.__balance = balance
        
    def deposit(self, amount):
        self.__balance += amount
        
    def withdraw(self, amount):
        if self.__balance >= amount:
            self.__balance -= amount
        else:
            raise ValueError("잔액 부족")</pre>
</details>

### Q75. 프로퍼티를 읽기 전용(Read-Only)으로 선언하는 방법
어떤 멤버 변수 속성의 변경을 원천 차단하고 오직 조회만 되도록 property 데코레이터로 유도하는 방식을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># @property 데코레이터만 선언하고, 그에 상응하는 @property.setter를 정의해두지 않으면 읽기 전용(Read-Only) 속성이 됩니다.</pre>
</details>

---

### Q76 ~ Q100: 다형성 및 메모리 복사, 종합 실무 설계 문제
### Q76. 다형성 (Polymorphism)의 실무적 정의
동일한 메시지 호출 규격(인터페이스)에 대해, 서로 다른 타입의 객체가 각각 고유한 개성대로 작동(메소드 처리)하는 객체지향 특징을 무엇이라 하나요?

<details><summary><b>정답 보기</b></summary>
<pre># 다형성 (Polymorphism) 입니다.</pre>
</details>

### Q77. 덕 타이핑 (Duck Typing)의 개념
"오리처럼 걷고 오리처럼 운다면 그것은 오리다" 라는 말에서 유래한, 명시적 상속 구조가 아니더라도 특정 메소드를 가지고만 있다면 동일한 타입군으로 동적 바인딩해 처리해 버리는 파이썬 고유의 동적 다형성 기법명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># 덕 타이핑 (Duck Typing) 기법입니다.</pre>
</details>

### Q78. 덕 타이핑 구현 예시
`Duck` 클래스와 `Person` 클래스가 공통 상속 관계없이 모두 `quack(self)` 메소드를 지니고 있습니다. 이를 순회하며 일괄로 quack()을 실행시키는 다형성 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Duck:
    def quack(self):
         print("꽥꽥")

class Person:
    def quack(self):
         print("사람이 오리 소리를 냅니다.")

def make_it_quack(obj):
    obj.quack() # 덕 타이핑 적용

for x in [Duck(), Person()]:
    make_it_quack(x)</pre>
</details>

### Q79. 복사 연산과 객체 복제 (Shallow vs Deep)
파이썬에서 단순 대입연산자(`=`) 복사는 객체를 복제하는 것이 아니라 객체의 참조(주소)만 복사한다는 성질을 주석으로 기술하세요.

<details><summary><b>정답 보기</b></summary>
<pre># 대입 연산자는 새로운 메모리 객체를 생성하지 않고 동일한 객체를 가리키는 포인터 변수만 늘릴 뿐입니다.</pre>
</details>

### Q80. 얕은 복사 (Shallow Copy)의 한계
`copy` 모듈의 `copy()`를 이용해 얕은 복사를 수행할 때, 리스트 내에 또 리스트가 중첩된 구조(2차원 배열 등)인 경우 하위 중첩 리스트의 주소값까지 완전히 분리 복사해 주지 못하는 한계 상황을 주석으로 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre># 얕은 복사는 최상위 껍데기 객체만 복제하고, 그 내부의 멤버 주소 참조들은 원본과 동일한 주소 참조를 공유하므로 내부 변경이 상호 오염될 위험이 있습니다.</pre>
</details>

### Q81. 깊은 복사 (Deep Copy)의 해결책
객체 내부의 중첩 구조까지 완벽하게 재귀적으로 추적하여 독립적인 사본 객체로 복사해 오염을 차단하는 모듈 함수명을 적으세요.

<details><summary><b>정답 보기</b></summary>
<pre>import copy
# copy.deepcopy(obj)</pre>
</details>

### Q82. 깊은 복사 구현 테스트
이중 리스트 `data = [[1, 2], [3, 4]]`를 deepcopy하여 사본을 만들고 사본 값을 수정해도 원본에 영향이 없음을 검증하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import copy
data = [[1, 2], [3, 4]]
data_copy = copy.deepcopy(data)
data_copy[0][0] = 99
print(data[0][0]) # 1 (오염 안 됨)</pre>
</details>

### Q83. 객체 직렬화 덤프 (Pickle)
파이썬 객체 인스턴스를 디스크 파일에 바이너리 파일 형태로 상태 통째로 보관/저장(Serialize)하기 위해 사용하는 표준 모듈명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre># pickle 모듈을 사용합니다.</pre>
</details>

### Q84. pickle 객체 저장하기 (dump)
`pickle.dump()`를 사용해 객체 `obj`를 바이너리 파일 `"obj.pickle"`에 쓰는 코드를 작성하세요. (w가 아닌 wb 모드)

<details><summary><b>정답 보기</b></summary>
<pre>import pickle
# wb: Write Binary
with open("obj.pickle", "wb") as f:
    pickle.dump(obj, f)</pre>
</details>

### Q85. pickle 객체 복원하기 (load)
바이너리 파일 `"obj.pickle"`로부터 저장되어 있던 원래 객체를 그대로 복원 로드해오는 코드를 작성하세요. (rb 모드)

<details><summary><b>정답 보기</b></summary>
<pre>import pickle
with open("obj.pickle", "rb") as f:
    recovered_obj = pickle.load(f)</pre>
</details>

### Q86. 클래스 변수 상속 충돌
부모 `class A:`가 클래스 변수 `x = 1`을 지닙니다. 자식 `class B(A):`는 별도로 `x`를 선언하지 않았습니다. 이때 `B.x`는 무엇을 참조하나요?

<details><summary><b>정답 보기</b></summary>
<pre># 부모 A 클래스의 클래스 변수인 1을 상속 참조합니다.</pre>
</details>

### Q87. 인스턴스별 유일 아이디 주입
매장 객체를 생성할 때마다 클래스 변수 `__counter`를 1씩 증가시켜 각 객체의 멤버 변수 `self.id`에 순차적 일련번호(`1`, `2`, `3`...)를 자동 부여하는 클래스를 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class SequenceShop:
    __counter = 0
    def __init__(self):
        SequenceShop.__counter += 1
        self.id = SequenceShop.__counter</pre>
</details>

### Q88. 스페셜 메소드 중 크기 작다 판별자 (__lt__)
객체 간 정렬 sorted()가 가동되려면 객체 간 작다(`<`) 비교가 정의되어야 합니다. 작다 비교 연산자 기능을 오버로딩하는 특수 메소드를 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __lt__(self, other):
    pass</pre>
</details>

### Q89. 객체 간 크기 비교 연계 정렬
`Store` 클래스 객체를 매출액(`sales`) 속성 기준으로 자동 크기 비교하여 정렬할 수 있도록 `__lt__`를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Store:
    def __init__(self, code, sales):
        self.code = code
        self.sales = sales
    def __lt__(self, other):
        return self.sales < other.sales</pre>
</details>

### Q90. 다중 상속 시 super()의 동작 원리
다중 상속 계층 구조에서 `super()`는 단순 직계 부모 클래스 하나만 지칭하지 않고, MRO 체인의 다음 순서 클래스를 찾아 차례대로 상위 생성자 체이닝을 유도하는 기전임을 주석으로 요약하세요.

<details><summary><b>정답 보기</b></summary>
<pre># super()는 부모뿐만 아니라 MRO(Method Resolution Order) 선형화 리스트 상에서 다음 순번에 위치한 클래스를 찾아 실행하므로 다중 상속 체인에서 누수 없이 전체 초기화를 가능하게 만듭니다.</pre>
</details>

---

### Q91 ~ Q100: 클래스 응용 설계 실습
### Q91. 팩토리 메소드 패턴 구현
클래스 메소드 `@classmethod`를 사용해 매장코드 `"NC"`로 시작하면 `NCOfflineShop` 객체를, 그 외에는 `GeneralShop` 객체를 판단 생성하여 리턴해주는 팩토리 생성 메소드를 클래스 내에 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class ShopFactory:
    @classmethod
    def create_shop(cls, code):
        if code.startswith("NC"):
            return NCOfflineShop(code)
        return GeneralShop(code)</pre>
</details>

### Q92. 사용자 리스트 클래스 래핑
`list` 자료형을 상속받아, 새로운 요소를 추가할 때마다 추가 내용을 자동으로 로깅 출력해 주는 커스텀 리스트 클래스 `LoggedList`를 설계하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class LoggedList(list):
    def append(self, item):
        print(f"로그: {item} 추가됨")
        super().append(item)</pre>
</details>

### Q93. 연산자 오버로딩 곱셈 (__mul__)
객체 간의 곱셈 기호 `*`가 만났을 때 가동될 곱하기 연산 오버로딩 메소드명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __mul__(self, other):
    pass</pre>
</details>

### Q94. 컨테이너 포함 여부 판단 스페셜 메소드 (__contains__)
`if item in obj:` 조건문이 가동될 때 내부적으로 포함 관계를 커스텀 판단하게 만들어주는 스페셜 메소드명을 기재하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __contains__(self, item):
    pass</pre>
</details>

### Q95. 딕셔너리처럼 대괄호 접근 허용 (__getitem__)
생성된 객체를 리스트나 딕셔너리처럼 대괄호 인덱싱(`obj[key]`) 형태로 호출해 내부에 접근할 수 있게 열어주는 맵 형식 특수 메소드명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __getitem__(self, key):
    return self.data[key]</pre>
</details>

### Q96. 대괄호 대입문 허용 (__setitem__)
객체를 `obj[key] = value` 형태로 대입 수정할 수 있게 지원하는 특수 메소드명을 쓰세요.

<details><summary><b>정답 보기</b></summary>
<pre>def __setitem__(self, key, value):
    self.data[key] = value</pre>
</details>

### Q97. 클래스 타입 문자열을 이용한 동적 객체 생성
문자열 클래스 이름 `"Store"`를 읽어 해당하는 클래스 객체를 동적으로 취득하고 생성하는 빌트인 함수 조합을 쓰세요. (힌트: `globals()`)

<details><summary><b>정답 보기</b></summary>
<pre>class Store:
    pass

# globals() 사전에서 클래스 객체 동적 추출
class_ref = globals()["Store"]
instance = class_ref()
print(type(instance)) # &lt;class '__main__.Store'&gt;</pre>
</details>

### Q98. 클래스 내부 속성 존재 검사 간결화
객체 `u`에 `"role"` 변수가 존재하지 않으면 `"ROLE_USER"`로 강제 초기 세팅 대입해 두는 setattr/getattr 연계 조건문을 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>if not hasattr(u, "role"):
    setattr(u, "role", "ROLE_USER")</pre>
</details>

### Q99. 복합 다형성 다이렉트 호출 예제
두 자식 클래스 `HqStore`, `StStore`가 부모 `Store`를 상속하며, 각각 `close_proc(self)`를 오버라이딩하고 있습니다. 이들을 다형적으로 순회 처리하는 클래스 결합을 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class Store:
    def close_proc(self):
        pass

class HqStore(Store):
    def close_proc(self):
        print("본사 정산 마감")

class StStore(Store):
    def close_proc(self):
        print("매장 일일 마감")

for s in [HqStore(), StStore()]:
    s.close_proc()</pre>
</details>

### Q100. 카테고리 5 종합 문제
다음 요구사항을 만족하는 `SecurePolicy` 클래스를 설계하세요.
1. 생성자에서 로그인 실패 제한 횟수 `__lock_limit` 속성을 private으로 입력받아 초기화합니다.
2. 이 속성에 대해 외부에서 직접 쓰기는 불가하게 차단하고 오직 값만 조회(Getter)되도록 프로퍼티 `@property` 처리합니다.
3. 클래스 정보 출력 스페셜 메소드 `__str__`을 구현하여 `print(객체)` 수행 시 `"보안정책: 실패잠금한도 [횟수]회"` 형식으로 문자열이 리턴되도록 완성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class SecurePolicy:
    def __init__(self, lock_limit):
        self.__lock_limit = lock_limit
        
    @property
    def lock_limit(self):
        return self.__lock_limit
        
    def __str__(self):
        return f"보안정책: 실패잠금한도 {self.__lock_limit}회"

policy = SecurePolicy(5)
# print(policy.__lock_limit) -> 에러 발생 (Private 보호)
print(policy.lock_limit)      # 5 출력 (Property Getter)
print(policy)                 # 보안정책: 실패잠금한도 5회 출력 (__str__)</pre>
</details>
