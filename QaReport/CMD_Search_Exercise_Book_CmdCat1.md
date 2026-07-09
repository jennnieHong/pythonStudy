# 터미널 검색 실무 연습 문제집 - [카테고리 1] Windows CMD findstr 검색 (50제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"CmdCat1"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py CmdCat1 Q1 True` (Q1 문제를 완료로 변경)

본 문제집은 윈도우 기본 명령 프롬프트(CMD) 창에서 기본 설치 프로그램인 `findstr` 명령어를 활용하여 파일 내 문자열을 검색하고 정규식 매칭을 적용하는 실무형 50문제를 수록하고 있습니다.

---

### Q1 ~ Q15: findstr 기본 사용법 및 매칭 옵션
### Q1. 단일 파일 내 단순 문자열 검색
`app.log` 파일에서 `"ERROR"`라는 문자열을 포함하는 행들을 찾아 출력하는 기본 CMD 명령어를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "ERROR" app.log</pre>
</details>

### Q2. 대소문자 구분 없이 검색
대소문자 구별 없이(즉, `Error`, `error`, `ERROR` 모두 매칭) `app.log` 파일에서 검색하는 옵션을 적용하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /I "error" app.log</pre>
</details>

### Q3. 매치된 행 번호 함께 표시
`app.log` 파일에서 `"ERROR"`가 매칭된 행들의 소스 위치 파악을 위해 왼쪽에 **줄 번호(1-indexed)**를 함께 출력하는 옵션을 적용하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /N "ERROR" app.log</pre>
</details>

### Q4. 현재 폴더의 모든 텍스트 파일 검색
현재 디렉토리에 있는 모든 `.txt` 확장자 파일 내에서 `"FAIL"` 문자열을 포함하는 행을 찾아내는 명령어를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "FAIL" *.txt</pre>
</details>

### Q5. 띄어쓰기가 들어간 여러 단어 중 하나라도 일치하는 행 검색 (OR 조건)
`app.log` 파일에서 `"ERROR"` 또는 `"WARNING"` 둘 중 하나라도 포함하는 행을 공백 구분자로 지정해 검색하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "ERROR WARNING" app.log</pre>
</details>

### Q6. 띄어쓰기가 포함된 단일 문구 검색 (공백 포함 통문자 매칭)
띄어쓰기 OR 조건이 아니라, `"SQL Error"`라는 한 덩어리의 문구 자체를 검색하도록 강제하는 `/C` 옵션을 적용해 명령어를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /C:"SQL Error" app.log</pre>
</details>

### Q7. 매칭되는 단어가 들어있는 파일명만 출력하기
`app.log` 내부 매칭 행 본문을 출력하지 않고, 단지 해당 문자열 `"Exception"`이 포함된 파일들의 경로명 리스트만 깔끔하게 가져오는 옵션을 적용하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /M "Exception" *.log</pre>
</details>

### Q8. 단어가 존재하지 않는 행만 출력 (부정 검색 - NOT)
`app.log` 파일에서 `"INFO"` 문자열이 포함되어 있지 **않은** 행들만 필터링하여 출력하는 옵션을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /V "INFO" app.log</pre>
</details>

### Q9. 단어 단위로만 완전 매치하는 옵션
단어의 일부(예: `error_code`)에 걸리는 것은 버리고, 단어가 오직 공백이나 문장 기호로 분리되어 완벽하게 일치하는 경우(예: `error` 단독)만 잡는 옵션을 기재하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /Y "error" app.log</pre>
</details>

### Q10. 파일의 맨 처음 시작 글자 매칭 (줄바꿈 시작점)
줄의 맨 첫 칸이 특정 단어 `"START"`로만 시작하는 행들을 골라내는 기호(`^`)를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "^START" app.log</pre>
</details>

### Q11. 줄의 맨 끝단 단어 매칭
줄의 맨 마지막 부분이 특정 단어 `"END"`로 끝나는 행들을 골라내는 기호(`$`)를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "END$" app.log</pre>
</details>

### Q12. 특정 텍스트 파일에 지정된 검색어 목록 불러오기
여러 개의 검색 키워드를 매번 타이핑하지 않고, `keywords.txt` 파일에 한 줄씩 써둔 후 그에 해당하는 키워드를 불러와 검색하는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /G:keywords.txt app.log</pre>
</details>

### Q13. 검색할 대상 파일 경로 목록 파일 불러오기
검색할 대상이 되는 소스 파일 목록들을 적어둔 `files.txt` 파일을 참조하여, 그 안에 기재된 파일들을 대상으로만 단어 `"MUSERSTB"`를 스캔하게 하는 옵션을 적용하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /F:files.txt "MUSERSTB"</pre>
</details>

### Q14. 정확한 문자 그대로 매칭 설정 (정규식 비활성화)
마침표(`.`)나 별표(`*`) 같은 정규식 제어 문자를 패턴으로 삼지 않고 일반 기호 텍스트로 보아 문자 그대로의 `"A.B.C"`를 검색하게 활성화하는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /L "A.B.C" app.log</pre>
</details>

### Q15. 정규표현식(Regex)을 이용한 매칭 활성화 옵션
기본적인 와일드카드 문자 등을 정규표현식 엔진이 해석하여 수행하게 만드는 옵션을 명시하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "N[0-9]" app.log</pre>
</details>

---

### Q16 ~ Q35: 하위 폴더 탐색 및 상세 실무 필터링
### Q16. 하위 디렉토리 전체 순회 검색 (Recursive)
현재 폴더뿐만 아니라 모든 서브 폴더들을 재귀적으로 뒤져서 모든 자바 소스파일(`*.java`) 내에 적힌 `"CustomAuthenticationProvider"` 단어를 출력하는 명령어를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /S "CustomAuthenticationProvider" *.java</pre>
</details>

### Q17. 특정 디렉토리 내의 XML 매퍼 파일 내 쿼리문 탐색
`D:\hmTest\backoffice` 및 하위 폴더의 모든 XML 파일(`*.xml`) 내에서 테이블명 `"MGOODSTB"`이 쓰인 위치를 줄번호와 함께 찾는 최적의 실무 조합 명령을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /S /N /I "MGOODSTB" D:\hmTest\backoffice\*.xml</pre>
</details>

### Q18. 매치되지 않은 파일 목록만 출력
어느 자바 파일에 `"CustomAuthenticationProvider"`가 적용되어 있지 않은지(누락되었는지) 식별하기 위해, 해당 단어가 포함되지 **않은** 파일 경로 목록만 출력하는 옵션을 조합해 보세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /S /V /M "CustomAuthenticationProvider" *.java</pre>
</details>

### Q19. 임의의 한 문자 매칭 기호
정규식 옵션을 켜고, 문자 `"A"`와 `"B"` 사이에 딱 1글자의 임의 문자가 들어오는 형태(예: `"AXB"`, `"A5B"`)를 매칭시키는 기호를 기입하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "A.B" app.log</pre>
</details>

### Q20. 0개 이상의 반복 매칭 기호
앞선 문자가 0번 이상 반복될 수 있음을 나타내는 수량자 정규식 와일드카드를 써서 `"AB"`, `"ABB"`, `"ABBB"` 등을 일괄 매칭하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "AB*" app.log</pre>
</details>

### Q21. 임의 문자 전체 매칭 조합
기본 텍스트 `"ERROR"`로 시작해서 뒤에 어떤 기호나 글자가 와도 좋으니 줄 마지막까지 매치시키는 정규식 기호 조합법을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "ERROR.*" app.log</pre>
</details>

### Q22. 대괄호 내 단일 문자 매칭 (Character Class)
`"N"` 뒤에 숫자 `1`, `2`, `3` 중 딱 하나가 오는 것(예: `"N1"`, `"N2"`, `"N3"`)만 걸러내는 대괄호 범위를 사용해 패턴을 완성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "N[123]" app.log</pre>
</details>

### Q23. 지정한 알파벳 범위 문자 매칭
`"a"`부터 `"z"` 사이의 소문자 알파벳 1글자가 들어간 행을 매칭시키는 범위를 대괄호 안에 작성해 넣으세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "[a-z]" app.log</pre>
</details>

### Q24. 지정 범위 제외 매칭 (Negated Character Class)
대괄호 첫머리에 캐럿(`^`)을 배치하여 `"N"` 뒤에 숫자가 오지 **않는** 문자 조합들만 걸러내는 정규식을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "N[^0-9]" app.log</pre>
</details>

### Q25. 공백 라인(Empty Line) 전체 찾기
어떤 텍스트도 들어있지 않고 줄바꿈 개행문자만 덩그러니 들어있는 공백행들을 식별하는 정규식을 시작(`^`)과 끝(`$`) 앵커 기호의 결합으로 구현하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "^$" app.log</pre>
</details>

### Q26. 단어의 시작 경계 앵커 매칭
`"admin"`으로만 온전히 시작하는 단어(예: `admin`은 통과, `badadmin`은 탈락)를 명시하기 위해 단어 시작단에 붙이는 경계 매칭 기호(`\<`)를 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "\<admin" app.log</pre>
</details>

### Q27. 단어의 끝 경계 앵커 매칭
특정 문자열 `"port"`로 끝나는 단어(예: `export`는 매치, `portal`은 탈락)를 골라내기 위해 단어 끄트머리에 붙이는 경계 기호(`\>`)를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "port\>" app.log</pre>
</details>

### Q28. 여러 파일에서 대소문자 없는 완전 매칭 종합
현재 폴더 하위의 모든 `.properties` 설정 파일 내에서 대소문자 관계없이 `"host"`가 완전 일치하는 단어로 쓰인 행을 줄번호와 함께 검색하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /S /N /I /Y "host" *.properties</pre>
</details>

### Q29. findstr의 다중 경로 패턴 지정
두 개의 상이한 디렉토리인 `D:\logs\sys` 와 `D:\logs\app` 아래의 모든 `.log` 파일을 단 하나의 커맨드라인에서 조회해 오는 작성법을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "ERROR" D:\logs\sys\*.log D:\logs\app\*.log</pre>
</details>

### Q30. 시스템 날짜 포맷 형태 검색
`"2026-07-06"` 이라는 날짜 기호 패턴을 감지하는 정규식을 숫자의 범위 조합 `[0-9]`를 사용해 findstr 규격에 맞춰 완성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]" app.log</pre>
</details>

---

### Q31 ~ Q50: 다중 필터링 및 파이프라인 연계 실무
### Q31. 파이프(`|`) 기호와 조합한 특정 프로세스 검색
작업 관리 명령어인 `tasklist` 결과에서 오직 파이썬 서버 프로세스 명칭인 `"python"`이 들어간 행들만 걸러내는 파이프 연계 필터링 구문을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>tasklist | findstr /I "python"</pre>
</details>

### Q32. 특정 포트 점유 중인 프로세스 PID 확인
네트워크 연결 확인 명령어인 `netstat -ano` 명령어 결과 출력에서 포트번호 `9000`번을 바인딩하고 있는 라인만 뽑아내는 findstr 조합을 완성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>netstat -ano | findstr "9000"</pre>
</details>

### Q33. 2중 findstr 결합을 이용한 AND 조건 필터링
`app.log` 파일에서 한 행 내에 `"ERROR"`와 `"database"` 두 단어가 **동시에** 포함되어 있는 행만을 필터링하는 파이프라인 연계 구문을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "ERROR" app.log | findstr "database"</pre>
</details>

### Q34. 3중 findstr 결합을 이용한 AND/NOT 조합 필터링
`app.log`에서 `"ERROR"`와 `"user"`는 포함하지만, 디버그 데이터인 `"debug_info"`는 포함되어 있지 **않은** 최종 정제 데이터 행을 가공하는 파이프 조합을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "ERROR" app.log | findstr "user" | findstr /V "debug_info"</pre>
</details>

### Q35. 디렉토리 구조 출력 명령어와 조합한 특정 폴더만 확인
디렉토리 트리 출력 명령어인 `tree /F`와 조합하여 파일 목록 트리 중 `"QaReport"` 라는 단어가 들어간 부분만 추려서 보여주게끔 하세요.
<details><summary><b>정답 보기</b></summary>
<pre>tree /F | findstr "QaReport"</pre>
</details>

### Q36. 특정 자바 클래스 내 'Select' 쿼리 아이디 선언 위치 검색
소스 폴더 하위의 모든 `.xml` 파일에서 `select` 속성 쿼리문 선언부 패턴 `id="query_id"` 형식을 findstr 정규식으로 대소문자 구분 없이 찾는 문장을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /S /N /I "id=[a-zA-Z0-9_]*select" *.xml</pre>
</details>

### Q37. findstr 출력 결과를 다른 텍스트 파일로 저장 (Redirect)
`app.log`에서 `"FATAL"` 문자열이 포함된 모든 결과를 화면에 출력하지 않고 `"fatal_summary.txt"` 파일로 출력 전환(Redirect) 저장시키는 기호(`>`)를 연결하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "FATAL" app.log > fatal_summary.txt</pre>
</details>

### Q38. findstr 결과 파일 덧붙이기 (Append Redirect)
기존에 생성된 `"fatal_summary.txt"` 파일을 리셋해 날리지 않고, 새로 조회한 `"CRITICAL"` 에러 결과 행을 그 파일의 맨 아래에 덧붙여 누적 저장하는 기호(`>>`)를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "CRITICAL" app.log >> fatal_summary.txt</pre>
</details>

### Q39. 대괄호 이스케이프가 없는 findstr 제약 처리 방법
findstr 정규식에서는 대괄호 기호 자체 `[` 나 `]` 문자를 일반 기호로 보아 `\[` 이스케이프 처리하여 찾는 기능이 제한됩니다. 이 경우 이 기호들을 이스케이프하여 매치할 수 있는 일반 텍스트 옵션(`/L`)을 켜서 `"["` 기호를 찾는 명령을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /L "[" app.log</pre>
</details>

### Q40. findstr 정규식 내의 백슬래시 문자 검색 방법
`app.log`에서 디렉토리 표시 기호인 백슬래시(`\`) 자체를 매칭하기 위해 정규식 옵션(`/R`) 하에서 연속으로 입력해야 하는 기호 형식을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "\\" app.log</pre>
</details>

### Q41. 특정 IP 주소 대역의 정규식 검색
`app.log`에서 `"192.168.10.X"` 대역에 해당하는 IP의 로그를 findstr 정규식으로 찾는 명령어를 완성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "192\.168\.10\.[0-9]" app.log</pre>
</details>

### Q42. 지정한 여러 개의 단어 포함 파일명 리스트 종합
현재 폴더 및 하위 폴더의 모든 자바 파일 중 `"insert"` 나 `"update"` 혹은 `"delete"` 라는 단어가 단 하나라도 포함된 모든 파일명 목록만 `/M`과 OR 검색을 조합하여 한 줄로 획득하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /S /M /I "insert update delete" *.java</pre>
</details>

### Q43. findstr이 에러 코드값을 리턴하는 특성 (ERRORLEVEL)
명령 프롬프트에서 findstr을 실행한 후 매칭 결과물이 있으면 `ERRORLEVEL` 시스템 변수에 저장되는 숫자값은 무엇이고, 매칭 결과가 없으면 저장되는 값은 각각 무엇인가요?
<details><summary><b>정답 보기</b></summary>
<pre># 매칭되는 텍스트를 찾았으면 0을 반환하고, 찾지 못했으면 1을 반환합니다. (배치 스크립트 작성 시 조건 분기로 사용됨)</pre>
</details>

### Q44. ERRORLEVEL 값을 명령 프롬프트에서 직접 확인
방금 전 수행한 findstr 명령의 검색 성공 여부 코드(`0` 또는 `1`)를 CMD 터미널 화면에 에코로 찍어보는 명령을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>echo %ERRORLEVEL%</pre>
</details>

### Q45. 특정 쿼리 ID가 들어가지 않은 SQL 파일 선별
`D:\hmTest\backoffice\mapper` 폴더의 모든 `.xml` 파일 중, 공통 감사 필드 쿼리 영역인 `"CommonAuditSql"` 문자열을 포함하지 않는(누락시킨) 불량 파일들의 이름 리스트를 검색하는 구문을 완성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /S /M /V "CommonAuditSql" D:\hmTest\backoffice\mapper\*.xml</pre>
</details>

### Q46. 특정 환경 설정 주석행 필터 탈락 처리
`hms.properties` 설정 파일에서 샵 기호(`#`)로 시작하는 모든 주석행과 공백 라인을 제외한 유효 설정 코드 라인만 추려 화면에 출력해 주는 명령어 파이프 결합을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /V "^#" hms.properties | findstr /V "^$"</pre>
</details>

### Q47. findstr 정규식 내 마침표 문자 검색 방법
정규식 모드(`/R`) 하에서 마침표 기호(`.`)는 임의의 한 문자 대변 기호입니다. 실제 기호 마침표 문자 자체를 검색하기 위해 취해야 하는 정규식 기호 작성법을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R "\." app.log</pre>
</details>

### Q48. 영어 단어가 들어가지 않은 순수 숫자 행 찾기
`app.log`에서 알파벳 문자 `[a-zA-Z]`가 전혀 포함되지 않은 순수 수치/기호 행만을 골라내기 위한 부정 조합 정규식을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /R /V "[a-zA-Z]" app.log</pre>
</details>

### Q49. 파일 경로명을 검색 경로 인자로 다중 지정
현재 위치가 아닌 부모 폴더의 상위 설정 파일인 `..\config.properties` 와 `..\..\app.properties` 두 파일에 대해 동시에 단어 `"db_password"`를 스캔하도록 여러 경로를 이어 적어 명령어를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr "db_password" ..\config.properties ..\..\app.properties</pre>
</details>

### Q50. findstr 종합 마스터 문제
명령 프롬프트(CMD) 환경에서 다음 작업을 원스톱으로 처리하는 한 줄 명령어를 완성하세요.
1. `"D:\hmTest\backoffice"` 폴더 및 모든 서브 폴더 내의 모든 자바 소스 파일(`*.java`)을 훑습니다.
2. 대소문자 구분 없이 `"session"` 이라는 단어를 포함하고, `"filter"` 라는 단어도 동시에 포함하는 줄번호를 수집합니다.
3. 수집된 결과 행들을 바탕으로 바탕화면의 `"session_filter_report.txt"` 결과 파일에 덮어쓰기 저장하세요.
<details><summary><b>정답 보기</b></summary>
<pre>findstr /S /N /I "session" D:\hmTest\backoffice\*.java | findstr /I "filter" > %USERPROFILE%\Desktop\session_filter_report.txt</pre>
</details>
