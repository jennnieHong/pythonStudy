# HMS 개발자를 위한 Python 실전 연습 문제집 (총 700제)

> [!TIP]
> **학습 상태 기록 및 대시보드 지원**: 본 문제집의 각 카테고리/문항별 진척도는 동일 폴더 내 [python_learning_progress.json](./python_learning_progress.json) 파일에 저장되며, **[📊 실시간 진척도 대시보드(Python_Learning_Progress.md)](./Python_Learning_Progress.md)**에서 진행 바와 합격 유무를 눈으로 보며 시각적으로 관리할 수 있습니다.
> * 상태 업데이트: [update_progress.py](./update_progress.py) 스크립트를 통해 쉽게 토글합니다. (예: `python update_progress.py Cat1 Q5 True`)


본 문제집은 파이썬 기초부터 고급 실무 연동 스크립트 작성 기술까지 총 7개 카테고리로 나누어 각 100문제씩, **총 700개의 연습 문제**를 수록한 종합 문제 은행입니다.

각 카테고리 링크를 클릭하여 세부 문제집으로 이동하여 학습할 수 있습니다. 각 문항 하단의 **정답 접기/펴기**를 클릭해 모범 정답 코드를 대조해 볼 수 있습니다.

---

## 📚 카테고리별 실전 문제집 (각 100제)

### 1. [카테고리 1: 기초 문법 및 변수 (100제)](./Python_Exercise_Book_Cat1.md)
* 파이썬 기본 출력, 변수 할당, 사칙 연산, 자료형 변환, 기본 문자열 인덱싱 및 슬라이싱, 포맷팅 규칙.

### 2. [카테고리 2: 조건문과 반복문 (100제)](./Python_Exercise_Book_Cat2.md)
* `if-elif-else` 조건 판단문, 짝수/홀수 판별, 윤년 판별, `for` 및 `while` 루프 제어, `break`/`continue` 분기, 리스트 내포(List Comprehension) 및 `enumerate` 순회 기법.

### 3. [카테고리 3: 자료구조 (리스트, 튜플, 딕셔너리, 세트) (100제)](./Python_Exercise_Book_Cat3.md)
* 동적 리스트 다루기(정렬, 원소 추가/삭제), 불변 튜플과 언패킹, 키-값 쌍 딕셔너리 조작(items/get 메소드), 세트를 활용한 중복 요소 제거 및 교집합/합집합 계산, 람다 정렬 기준 바인딩.

### 4. [카테고리 4: 함수 및 람다 (100제)](./Python_Exercise_Book_Cat4.md)
* 파라미터 기본값 설정, 가변 인자(`*args`, `**kwargs`), 함수 다중 반환, 람다 익명 식 설계, `map`과 `filter`를 활용한 리스트 일괄 변환, 재귀(Recursion) 함수, 변수 Scope 제어.

### 5. [카테고리 5: 클래스와 객체 지향 (100제)](./Python_Exercise_Book_Cat5.md)
* 클래스 선언과 생성자(`__init__`), 상속 관계 구현과 `super()`, 클래스 변수 vs 인스턴스 변수 차이, 정보 은닉(Private `__` 변수), 특수 메소드(`__str__`), 정적 메소드(`@staticmethod`), 다형성 및 깊은/얕은 복사.

### 6. [카테고리 6: 예외 처리 및 파일 입출력 (100제)](./Python_Exercise_Book_Cat6.md)
* `try-except-finally` 구조, 예외 강제 발생(`raise`), 커스텀 예외 정의, `with` 구문을 통한 파일 자동 열기/닫기, 텍스트 및 CSV 파일 읽기/쓰기, 디렉토리 생성 및 삭제, 대용량 로그 파일 내 특정 키워드 실시간 필터링.

### 7. [카테고리 7: 실무 라이브러리 및 정규식, DB 연동 (100제)](./Python_Exercise_Book_Cat7.md)
* 날짜 및 시간 계산(`datetime`), 디렉토리 내 파일 스캔(`glob`/`os`), JSON 파일 직렬화/역직렬화, 정규표현식(`re`)을 이용한 대괄호 속 키값 정교 추출 및 문자열 정밀 분산 처리, `psycopg2` 모듈을 이용한 EDB DB 커넥션 맺기, 데이터 조회 및 삽입 처리, 트랜잭션 커밋 제어 등 실무 종합 스크립트 작성 기법.

### 8. [부록: 파이썬 엑셀(Excel) 핸들링 실전 문제집 (45제)](./Python_Excel_Exercise_Book.md)
* `openpyxl` 및 `pandas` 라이브러리를 활용한 엑셀 입출력 기초, 서식 및 스타일 지정, 엑셀 수식 활용, 다중 시트 가공, 엑셀 정산 데이터 정제 유효성 검사 및 EDB 데이터베이스 벌크 연동 기법.

### 9. [부록: 파이썬 & Web API JSON 연동 실전 문제집 (20제)](./Python_JSON_Web_Exercise_Book.md)
* 로컬 JSON 데이터 직렬화/역직렬화(dumps, loads, dump, load), 예외 처리, 중첩 딕셔너리 구조 제어, 파이썬 http.server API 수신 및 CORS 허용 헤더 처리, 프론트엔드 비동기 fetch() API JSON 전송 기법.

### 10. [부록: 터미널(CLI) 검색 명령어 실전 문제집 (150제)](./CMD_Search_Exercise_Book.md)
* 윈도우 기본 CMD(`findstr`), 현대식 PowerShell(`Select-String`), 리눅스/유닉스 서버 환경(`grep` / `zgrep`)을 이용한 대량 로그 스캔, 정규식 매칭, 특정 시간대 필터링 및 쿼리 매퍼 코드 고속 탐색 기법.


