# 터미널 및 파이썬 파일 경로(Path) 규칙 완벽 가이드

컴퓨터 터미널(CMD, PowerShell, Linux 셸)과 프로그래밍 언어(Python, Java 등)에서 파일이나 폴더의 위치를 가리키는 **경로(Path)의 기본 개념과 절대경로/상대경로의 작동 규칙**을 아주 알기 쉽게 설명해 드립니다.

---

## 1. 핵심 개념: "현재 내 작업 폴더 (Working Directory)"

터미널이나 파이썬 프로그램은 항상 **"내가 지금 서 있는 위치"**가 존재합니다. 이를 **작업 디렉토리(Working Directory)** 또는 **현재 폴더**라고 부릅니다.

* **CMD에서 현재 위치 확인**: 명령창 맨 왼쪽에 적힌 문자열 (예: `C:\Users\User>`)
* **PowerShell에서 현재 위치 확인**: `pwd` 입력 후 엔터
* **Linux에서 현재 위치 확인**: `pwd` 입력 후 엔터

> [!WARNING]
> **초보자가 가장 많이 하는 오해**:
> 파이썬 프로그램이 파일(`open("data.txt")`)을 열 때, **스크립트 파일(`.py`)이 저장된 위치가 아니라 "터미널 명령어를 입력하고 실행한 위치"가 기준**이 됩니다!
> * 예: 내 터미널이 `C:\Users`에 있고, `D:\Test\app.py`를 실행하면, 파이썬은 `D:\Test`가 아니라 `C:\Users`에서 `data.txt`를 찾습니다.

---

## 2. 절대 경로 (Absolute Path)

**"우리 집 주소: 서울특별시 마포구 아현동 100번지"** 처럼, 내 현재 위치가 지구 어디든 상관없이 **항상 동일한 파일 위치를 가리키는 고유한 주소**입니다.

### 2.1 절대 경로의 특징
* 항상 드라이브 문자(`C:\`, `D:\`) 또는 리눅스의 최상위 루트 기호(`/`)로 시작합니다.
* 경로가 매우 명확하여 오류가 나지 않지만, 주소가 길고 다른 컴퓨터로 코드 파일을 옮기면 주소가 맞지 않아 실행되지 않을 수 있습니다.

### 2.2 운영체제별 예시
* **Windows 절대경로**: `D:\hmTest\backoffice\QaReport\dirty_sales.xlsx`
  * 하이픈이나 역슬래시(`\`) 기호로 디렉토리 단계를 나눕니다.
* **Linux/Unix 절대경로**: `/var/log/hyundai/app.log`
  * 항상 슬래시(`/`) 기호 하나로 시작하는 루트(Root)에서 출발합니다.

---

## 3. 상대 경로 (Relative Path)

**"우리 집 주소: 여기서 오른쪽으로 돌아서 3번째 건물"** 처럼, **현재 내가 서 있는 폴더 위치(Working Directory)를 기준으로 삼아 파일의 위치를 상대적으로 나타내는 주소**입니다.

### 3.1 상대 경로 단축 기호
* **`.` (마침표 하나)**: **현재 내가 서 있는 폴더**를 의미합니다.
* **`..` (마침표 두 개)**: **나를 감싸고 있는 바로 위 부모 폴더**로 한 단계 위로 올라감을 뜻합니다.
* **`/` 또는 `\`**: 아래 폴더로 진입할 때 쓰는 구분 기호입니다.

### 3.2 현재 내 위치가 `D:\hmTest\backoffice\QaReport` 일 때의 상대 경로 매핑 예시

```text
📂 D:\ (드라이브)
└── 📂 hmTest
    └── 📂 backoffice
        ├── 📂 QaReport (★ 현재 내 위치)
        │   ├── 📄 dirty_sales.xlsx
        │   └── 📄 update_progress.py
        └── 📂 mapper
            └── 📄 hq_esti_Sql.xml
```

1. **현재 폴더의 `dirty_sales.xlsx`를 가리킬 때**:
   * 기호 표현: `./dirty_sales.xlsx` (또는 단순히 `./` 생략하고 `dirty_sales.xlsx`)
2. **바로 위 부모 폴더인 `backoffice` 폴더를 가리킬 때**:
   * 기호 표현: `..`
3. **부모 폴더 하위의 `mapper` 폴더 안의 `hq_esti_Sql.xml`을 가리킬 때**:
   * 먼저 한 단계 위로 이동(`..`) 한 다음, `mapper` 폴더로 들어가서(`\mapper`), 파일명을 적습니다.
   * 기호 표현: `..\mapper\hq_esti_Sql.xml`
4. **두 단계 위인 `hmTest` 폴더를 가리킬 때**:
   * 기호 표현: `..\..` (부모의 부모)

---

## 4. 파이썬(Python) 실무에서의 안전한 경로 제어 팁

터미널 실행 위치에 구애받지 않고, **"내 실행 파일(`.py`)이 위치한 물리 폴더를 기준"으로 항상 안전하게 상대 경로를 계산하여 파일 입출력을 처리하는 가장 완벽한 파이썬 패턴 코드**입니다.

```python
import os

# 1. __file__ 변수는 현재 실행 중인 파이썬 스크립트 파일의 절대경로를 담고 있습니다.
#    os.path.dirname(__file__)는 그 파일이 담긴 폴더의 경로를 뜻합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
print("이 실행 파일의 폴더 위치:", current_dir)

# 2. os.path.join을 쓰면 윈도우(\)와 리눅스(/) 구분 기호 차이를 알아서 자동 계산해서 주소를 병합해 줍니다.
#    이 방식대로 경로를 정의하면 터미널이 어디에 서 있든지 항상 스크립트 파일 옆의 'data.json'을 열게 됩니다.
target_json_path = os.path.join(current_dir, "python_learning_progress.json")

with open(target_json_path, "r", encoding="utf-8") as f:
    print("성공적으로 파일 오픈 완료!")
```

---

## 5. 터미널 폴더 이동 명령어 (`cd`)

내가 원하는 폴더(작업 디렉토리)로 나의 발걸음을 옮기는 명령어가 바로 **`cd` (Change Directory)** 입니다.

* **절대경로로 한 번에 이동**:
  ```powershell
  cd D:\hmTest\backoffice\QaReport
  ```
* **바로 위 폴더로 탈출**:
  ```powershell
  cd ..
  ```
* **하위 폴더로 진입**:
  ```powershell
  # 현재 위치 하위에 mapper 폴더가 있을 경우
  cd mapper
  ```
* **윈도우 CMD에서 드라이브 교체**:
  * 윈도우 CMD는 `cd`만으로 드라이브(C에서 D로)를 바꿀 수 없으므로 드라이브 기호를 먼저 쳐서 전환해야 합니다.
  ```cmd
  D:
  cd hmTest\backoffice\QaReport
  ```
