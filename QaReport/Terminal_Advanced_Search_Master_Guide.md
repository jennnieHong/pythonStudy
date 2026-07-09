# 터미널(CLI) 고급 검색 마스터 가이드

터미널(CMD, PowerShell, Linux 셸)을 사용하여 **파일명, 폴더명, 파일 내용**을 구분하여 정밀 검색하고, 로그 파일 내에서 **동일 행 또는 특정 범위(멀티 라인 구간) 내에 여러 단어가 함께 등장하는 복잡한 조건**을 검색하는 실무 비법을 정리합니다.

---

## 1. 파일명 vs 폴더명 vs 파일 내용 구분 검색

내가 원하는 검색 범위를 명확히 설정하여 속도와 정확도를 획득하는 방법입니다.

### 1.1 파일명 및 폴더명 검색
텍스트 알맹이가 아닌, 디렉토리 트리 내의 **이름 자체**를 기준으로 검색합니다.

#### 윈도우 CMD (`dir`)
```cmd
# 1. 파일명에 'Mapper'가 들어가는 모든 파일 찾기 (/S: 하위폴더 포함, /B: 경로명만 간결히 출력)
dir /S /B *Mapper.java

# 2. 폴더명(디렉토리)에 'estimate'가 들어가는 모든 폴더 찾기 (/A:D 옵션으로 폴더만 필터링)
dir /A:D /S /B *estimate*
```

#### 윈도우 PowerShell (`Get-ChildItem`)
```powershell
# 1. 파일명에 '00005'가 포함된 파일만 찾기 (-File 옵션)
Get-ChildItem -Recurse -File -Filter "*00005*"

# 2. 폴더명에 'sales'가 포함된 폴더만 찾기 (-Directory 옵션)
Get-ChildItem -Recurse -Directory -Filter "*sales*"
```

#### 리눅스/유닉스 (`find`)
```bash
# 1. 파일명에 'Sql'이 들어가는 파일 찾기 (-type f)
find . -type f -name "*Sql*"

# 2. 폴더명에 'master'가 들어가는 폴더 찾기 (-type d)
find . -type d -name "*master*"
```

---

### 1.2 특정 폴더/특정 파일 형식을 지정한 파일 내용 검색
**"어느 폴더 밑에 있는 어떤 확장자 파일 내에서만 검색하겠다"**는 조건 지정 방법입니다.

#### 윈도우 CMD (`findstr`)
```cmd
# D:\workspace 하위의 모든 XML 파일(*.xml) 내에서 'MGOODSTB' 검색
findstr /S /I /N "MGOODSTB" D:\workspace\*.xml
```

#### 윈도우 PowerShell (`Select-String`)
```powershell
# Get-ChildItem으로 경로와 파일 형식을 명확히 필터링한 후 파이프로 넘겨 내용 검색
Get-ChildItem -Path "D:\workspace" -Recurse -Include *.xml | Select-String -Pattern "MGOODSTB"
```

#### 리눅스/유닉스 (`grep`)
```bash
# --include 옵션을 활용해 특정 파일 형식 내에서만 검색
grep -rn --include="*.xml" "MGOODSTB" /var/log/
```

---

## 2. '한 줄(Single Line)'의 컴퓨터적 정의와 대용량 텍스트 검색 팁 💡

터미널 검색 명령어는 기본적으로 **줄 단위(Line-by-Line)**로 텍스트를 처리합니다. 이때 컴퓨터 과학에서 '한 줄'을 인식하는 기준과 예외적인 상황을 명확히 이해해야 오류를 막을 수 있습니다.

### 2.1 물리적 개행(Line Break) vs 시각적 자동 줄바꿈(Word Wrap)
* **물리적 개행 (컴퓨터가 인식하는 '한 줄')**:
  * 텍스트 내에 보이지 않는 개행 기호인 `\n` (Line Feed) 또는 `\r\n` (Carriage Return + Line Feed)이 들어가기 전까지는 글자 수가 10만 자이든 100만 자이든 **물리적으로 정확히 하나의 행(Single Line)**입니다.
* **시각적 자동 줄바꿈 (사람이 눈으로 보는 '여러 줄')**:
  * 에디터(VS Code, 메모장 등)의 설정에 의해 너비에 맞춰 꺾여 보이는 것은 가상 줄바꿈일 뿐, 파일 내부적으로는 여전히 한 줄로 이어져 있습니다.

### 2.2 대용량 한 줄 텍스트(예: JSON 로그) 검색 시의 결함
대부분의 검색 유틸리티(`grep`, `findstr` 등)는 줄 내에 검색 대상 단어가 하나라도 포함되면 **그 긴 한 줄 전체를 터미널 콘솔창에 그대로 다 출력**합니다.
* **위험성**: 개행 없이 가로로 수만 자 이상 늘어진 압축 JSON 로그 파일 등에서 검색을 무심코 수행하면, 화면이 터질 듯한 텍스트 폭탄이 쏟아져 **터미널이 마비(Freezing)되는 치명적인 결과**를 초래할 수 있습니다.

### 2.3 대용량 한 줄 텍스트 안전 검색 비법

#### ① 매칭된 결과 단어 부분만 잘라서 출력하기 (Only Match)
줄 전체가 아닌, 정확히 일치한 검색어 부분만 쏙 빼내어 안전하게 조회합니다.
* **Linux/Unix**: `grep -o "ERROR" app.log`
* **Windows PowerShell**: `(Select-String "ERROR" app.log).Matches.Value`

#### ② 임의의 기호(쉼표 등)를 개행문자로 치환해 검색하기 (tr 연계)
**`tr`**은 **Translate(치환/변환)** 명령어의 약어이며, **"tr 연계"**란 `tr` 명령어와 `grep` 검색 명령어를 파이프라인(`|`) 기호로 연결해 사용하는 것을 의미합니다.

* **동작 기법**: 가로로 한 줄짜리인 거대한 텍스트 데이터를 `tr` 명령어로 줄바꿈 처리하여 임시로 여러 줄로 쪼갠 뒤, `grep`으로 안전하게 라인 검색을 수행합니다.
* **Linux/Unix**: `cat one_line.json | tr ',' '\n' | grep "ERROR"`
* **Windows PowerShell**: `(Get-Content one_line.json) -split ',' | Select-String "ERROR"`

> [!NOTE]
> **Linux `tr` 연계 동작 예시 및 단계별 흐름**
>
> 대상 파일(`one_line.json`): `{"id":"admin","status":"ERROR","ip":"192.168.10.1","msg":"fail"}` (줄바꿈이 없는 한 줄 구조)
>
> 1. **`cat one_line.json`**: 파일의 긴 1줄 텍스트 전체를 읽어 다음 명령으로 넘깁니다.
> 2. **`| tr ',' '\n'`**: 쉼표(`,`)를 줄바꿈(`\n`) 문자로 치환하여 아래와 같이 여러 줄의 가상 데이터로 분리합니다.
>    ```text
>    {"id":"admin"
>    "status":"ERROR"
>    "ip":"192.168.10.1"
>    "msg":"fail"}
>    ```
> 3. **`| grep "ERROR"`**: 쪼개진 행들 중 오직 "ERROR"가 포함된 유효한 행만 쏙 빼내어 화면에 표시합니다.
>    ```text
>    # 최종 터미널 화면 출력 결과
>    "status":"ERROR"
>    ```

---


## 3. 한 줄(Single Line) 내 다중 단어 검색 (AND / OR 조건)


한 행 안에서 여러 단어 조건들이 만나는 상황을 쿼리하는 방법입니다.

### 2.1 AND 조건 (단어 A와 단어 B가 동시에 한 줄에 존재)
파이프라인(`|`) 기호로 검색 엔진을 2번 엮는 기법이 가장 강력하고 직관적입니다.

* **Windows CMD**: `findstr "단어A" log.txt | findstr "단어B"`
* **PowerShell**: `Select-String -Path log.txt -Pattern "단어A" | Select-String -Pattern "단어B"`
* **Linux/Unix**: `grep "단어A" log.txt | grep "단어B"`

### 2.2 OR 조건 (단어 A 또는 단어 B 둘 중 하나라도 존재)
* **Windows CMD**: `findstr "단어A 단어B" log.txt` (공백으로 분리하면 기본적으로 OR 조건 검색이 됩니다.)
* **PowerShell**: `Select-String -Path log.txt -Pattern "단어A", "단어B"`
* **Linux/Unix**: `grep -E "단어A|단어B" log.txt`

---

## 3. 특정 구간/범위(Multi-Line Range) 내 다중 단어 검색 💡

실무 로그 분석의 꽃이라고 할 수 있는 기능입니다. **"에러 코드(단어 A)가 터진 뒤 10줄 이내의 범위에 특정 DB 커넥션(단어 B)이 있는지 확인"**하는 시나리오에 쓰입니다.

### 3.1 맥락 보기(Context) 기능을 응용한 간접 검색
검색어 전후 라인을 덤프한 후, 그 덤프 내에서 두 번째 단어를 찾는 기법입니다.

#### 윈도우 PowerShell (최고의 실무 팁)
`Select-String`의 `-Context` 옵션을 사용해 매칭행 아래 10줄을 끌고 온 뒤, 그 후속 맥락 10줄 안에 `"database"`가 들어있는 라인을 가려냅니다.
```powershell
# 'ERROR'가 터진 행 기준 아래 10줄($_.Context.PostContext) 내에 'database'가 포함되었는지 필터링
Select-String -Path "app.log" -Pattern "ERROR" -Context 0,10 | Where-Object { $_.Context.PostContext -match "database" }
```

#### 리눅스/유닉스 (`grep -A`)
```bash
# 'ERROR' 발견 줄 아래 10줄을 함께 출력(-A 10)한 후, 그 안에서 'database'가 들어있는지 재검색
grep -A 10 "ERROR" app.log | grep "database"
```

---

### 3.2 텍스트 범위 패턴 매칭 (`sed` / `awk` / `정규식` 활용)
단어 A가 등장하는 지점부터 단어 B가 등장하는 지점까지의 **텍스트 블록 전체를 도려내어 검색**하는 고난도 기법입니다.

#### 리눅스/유닉스 (`awk` / `sed`)
* **기본 구조**: `awk '/시작패턴/,/종료패턴/' 파일명`
```bash
# 1. 로그에서 "ERROR" 발생 시점부터 다음 "SUCCESS"가 나타날 때까지의 전 구간을 추출
awk '/ERROR/,/SUCCESS/' app.log

# 2. 추출된 에러 블록 구간 내부에서 'NullPointerException'이 발생했는지 최종 판별
awk '/ERROR/,/SUCCESS/' app.log | grep "NullPointerException"
```

#### 리눅스 정규식 확장 (`pcregrep`)
기본 grep은 한 줄 단위로만 정규식을 돌리지만, `pcregrep`을 쓰면 **개행 문자(`\n`)를 포함한 멀티라인 매칭**이 가능합니다.
```bash
# ERROR 단어 뒤에 줄바꿈이 발생하더라도 500자 범위 내에 database가 출현하는 블록 전체 출력
pcregrep -M "ERROR(.|\n){0,500}database" app.log
```

---

### 💡 실무 요약 카드

| 상황 | Windows CMD | Windows PowerShell | Linux / Unix |
| :--- | :--- | :--- | :--- |
| **파일명만 찾기** | `dir /S /B *Name*` | `Get-ChildItem -File -Filter *Name*` | `find . -type f -name "*Name*"` |
| **폴더명만 찾기** | `dir /A:D /S /B *Name*` | `Get-ChildItem -Directory -Filter *Name*` | `find . -type d -name "*Name*"` |
| **특정 파일 형식 내용 검색** | `findstr /S "Word" *.xml` | `gci -Recurse *.xml \| sls "Word"` | `grep -rn --include="*.xml" "Word"` |
| **한 줄 AND 검색** | `findstr A file \| findstr B` | `sls A file \| sls B` | `grep A file \| grep B` |
| **에러 줄 아래 10줄 내 단어 검색** | N/A (스크립트 필요) | `sls A -Context 0,10 \| ? { $_.Context.PostContext -match B }` | `grep -A 10 A file \| grep B` |
