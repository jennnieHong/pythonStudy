# 터미널 검색 실무 연습 문제집 - [카테고리 2] Windows PowerShell Select-String 검색 (50제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"CmdCat2"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py CmdCat2 Q1 True` (Q1 문제를 완료로 변경)

본 문제집은 현대적인 Windows PowerShell 환경에서 텍스트 패턴 분석을 수행하는 핵심 cmdlet인 `Select-String` (단축 명령 `sls`)을 다루고, 파워셸 특유의 객체 파이프라인 연계 및 정밀 스크립팅 필터링을 조작하는 실무형 50문제를 수록하고 있습니다.

---

### Q1 ~ Q15: Select-String 기본 사용법 및 매칭 패턴
### Q1. 단일 파일 문자열 기본 매칭
`app.log` 파일에서 `"ERROR"` 라는 단어를 포함하는 행들을 찾아 출력하는 기본 PowerShell 명령을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "ERROR"</pre>
</details>

### Q2. 대소문자 명확한 구별 매칭 (CaseSensitive)
PowerShell의 `Select-String`은 기본적으로 대소문자를 구분하지 않습니다. 대소문자를 엄격하게 구별하여 오직 소문자 `"error"` 인 것만 매칭하는 옵션을 지정하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "error" -CaseSensitive</pre>
</details>

### Q3. 파워셸 별칭 단축키(Alias) 호출
`Select-String` 명령어의 공식 짧은 단축어 별명(Alias)을 사용해 `app.log`에서 `"FAIL"`을 찾는 명령을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>sls -Path "app.log" -Pattern "FAIL"</pre>
</details>

### Q4. 파이프라인(`|`)을 통한 파일 조회 연계
`Get-Content` 명령어로 `app.log` 내용을 로드한 후, 파이프 기호(`|`)를 통해 `Select-String`으로 넘겨 `"Exception"`을 필터링해 출력하는 한 줄 명령을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-Content "app.log" | Select-String -Pattern "Exception"</pre>
</details>

### Q5. 특정 확장자 모든 파일 대상 검색 (와일드카드)
현재 폴더 내의 모든 로그 파일(`*.log`) 내에서 `"WARNING"` 문자열을 포함하는 행들을 찾아내는 구문을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "*.log" -Pattern "WARNING"</pre>
</details>

### Q6. 다중 검색 패턴 지정 (OR 조건)
`app.log` 파일에서 `"ERROR"` 또는 `"FATAL"` 단어 중 하나라도 포함된 줄을 쉼표 배열 패턴으로 한 번에 필터링하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "ERROR", "FATAL"</pre>
</details>

### Q7. 부정 일치 검색 (NOT 매칭)
`app.log` 파일에서 `"INFO"` 가 포함되어 있지 **않은** 행들만 뒤집어서 필터링해 가져오는 반전 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "INFO" -NotMatch</pre>
</details>

### Q8. 단순 텍스트 패턴 매칭 강제 (정규식 비활성화)
패턴 문자열 내에 포함된 마침표(`.`)나 물음표(`?`)를 정규식 기호가 아닌 일반 문자 그대로 매칭하도록 지시하는 단순 문자 매칭 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "192.168.10.1" -SimpleMatch</pre>
</details>

### Q9. 검색 매치 결과의 일치 텍스트만 추출 (Matches)
매칭된 라인 전체를 다 가져오지 않고, 매치 성공한 대상 물리적 단어(예: `"ERROR_123"`) 값만 추출하여 출력하도록 속성 매핑을 이용해 보세요.
<details><summary><b>정답 보기</b></summary>
<pre>(Select-String -Path "app.log" -Pattern "ERROR_\d+").Matches.Value</pre>
</details>

### Q10. 인코딩 형식 지정 (Encoding)
한글 설정이 깨지지 않고 올바르게 검색되도록, 검색 타겟 파일의 문자 인코딩 형식을 `utf8`으로 강제 명시해 불러오는 옵션을 기재하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "오류" -Encoding utf8</pre>
</details>

### Q11. 단어 시작 위치 매칭 정규식 (PowerShell 규격)
줄바꿈 시작점이 아닌, 특정 글자 덩어리(단어)의 맨 처음 시작 부분 경계를 앵커링하는 파워셸 정규식 기호(`\b`)를 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "\berror"</pre>
</details>

### Q12. 매칭되는 단어가 존재하는 파일의 절대 경로 목록 확인
매칭 텍스트 행이 아닌, 매치 성공 파일들의 물리 하드웨어 절대 경로(Path) 문자열 리스트만 중복 없이 가져오는 파이프 파싱을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>(Select-String -Path "*.log" -Pattern "ERROR").Path | Select-Object -Unique</pre>
</details>

### Q13. 매칭 성공 행의 줄 번호 정수 획득
`app.log`에서 `"Exception"`이 발견된 행의 줄 번호(LineNumber) 값들만 정수 배열 형태로 쏙 뽑아내는 문장을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>(Select-String -Path "app.log" -Pattern "Exception").LineNumber</pre>
</details>

### Q14. 특정 텍스트 제외 규칙 정형화 (Exclude)
`*.log` 전체 파일 중 파일명 끝에 `_debug.log` 가 붙는 파일은 제외하고 나머지 로그 파일들만 대상으로 삼아 `"FATAL"` 단어를 조회하는 필터링 파일 제외 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "*.log" -Pattern "FATAL" -Exclude "*_debug.log"</pre>
</details>

### Q15. 특정 파일명 패턴 포함 규칙 정형화 (Include)
`/logs` 디렉토리 전체에서 오직 `App_` 시작 단어가 결합한 파일명들만 골라서 문자열 `"DB_FAIL"`을 스캔하게 유도하는 옵션을 기재하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "D:\logs\*" -Pattern "DB_FAIL" -Include "App_*"</pre>
</details>

---

### Q16 ~ Q35: 파이프라인 연계 및 맥락 행 출력 (Context)
### Q16. 하위 폴더 전체 재귀 탐색 연동 (Get-ChildItem)
PowerShell의 `Get-ChildItem -Recurse` 명령어와 파이프라인을 결합하여, 하위 폴더의 모든 자바 소스파일(`*.java`) 내에 적힌 `"CustomAuthenticationProvider"` 단어를 출력하는 구문을 완성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-ChildItem -Recurse -Filter *.java | Select-String -Pattern "CustomAuthenticationProvider"</pre>
</details>

### Q17. 매칭 행의 위/아래 주변 맥락 라인 출력 (Context)
에러 원인을 파악하기 위해 `"ERROR"`가 발생한 줄의 **위로 2줄, 아래로 3줄**의 주변 내용을 맥락적으로 묶어서 함께 출력해 주는 Context 옵션을 지정하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "ERROR" -Context 2,3</pre>
</details>

### Q18. 매칭 행 아래의 후속 맥락 내용만 출력
특정 예외가 잡힌 라인 바로 다음 내용이 중요하므로, `"Exception"` 발생 행의 **아래로만 5줄**을 추가 노출시키는 Context 매개변수 단독 호출 형식을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "Exception" -Context 0,5</pre>
</details>

### Q19. 파일 크기가 10MB 이상인 로그 파일들만 대상으로 검색
`Get-ChildItem` 과 `Where-Object` 파이프를 활용해 크기가 10MB(10MB = 10 * 1024 * 1024) 이상인 `.log` 대용량 파일만 선별하여 `"FATAL"` 단어를 색인하는 파워셸 구문을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-ChildItem -Filter *.log | Where-Object { $_.Length -gt 10MB } | Select-String -Pattern "FATAL"</pre>
</details>

### Q20. 2개 이상의 정규식 패턴 AND 필터링 연계
`app.log`에서 한 행 내에 `"ERROR"`도 들어있고 `"SDAILYTB"`도 들어있는 두 키워드 AND 매칭 결과를 파이프 2회 결합으로 달성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "ERROR" | Select-String -Pattern "SDAILYTB"</pre>
</details>

### Q21. 특정 날짜 시간 패턴 감지 정규식 매칭
`"[2026-07-06 18:30:12]"` 처럼 대괄호 안에 날짜 시각 구조가 들어있는 로그의 시작부를 파워셸 정규식으로 감지해 출력하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]"</pre>
</details>

### Q22. 매칭 결과를 GridView 창으로 시각적 테이블 출력 (Out-GridView)
윈도우에서 `Select-String` 검색 결과 텍스트를 마우스 클릭과 정렬이 가능한 GUI 테이블 팝업창으로 바로 띄워 확인하도록 하는 파워셸 후속 필터링 명령어를 연결하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "*.log" -Pattern "ERROR" | Out-GridView</pre>
</details>

### Q23. 매칭된 전체 개수(Count) 산출
`app.log` 내부에서 `"WARNING"` 단어가 전체 몇 번 등장하는지 숫자 개수 정수만 화면에 출력하는 파이프 속성 획득 식을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>(Select-String -Path "app.log" -Pattern "WARNING").Count</pre>
</details>

### Q24. 최근 수정된 파일 순서대로 검색 순위 부여
`Get-ChildItem` 검색 시 최근 수정된 날짜(`LastWriteTime`)가 최신인 순서대로 정렬하여 `Select-String`으로 패싱하게 유도하는 정렬 파이프를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-ChildItem -Filter *.log | Sort-Object LastWriteTime -Descending | Select-String -Pattern "ERROR"</pre>
</details>

### Q25. 검색어 매칭 파일 경로와 파일명 구분 추출
`Select-String`이 뱉는 결과물 객체에서 파일 전체 경로가 아닌 순수 파일명(Filename) 정보만 추출해 내는 속성을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>(Select-String -Path "*.log" -Pattern "ERROR").Filename</pre>
</details>

### Q26. 텍스트 파일 내 이메일 포맷 패턴 추출 정규식
로그 내 고객정보 노출 탐지를 위해 일반적인 이메일 형식 패턴을 감지하는 정규식을 `Select-String`에 연결해 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"</pre>
</details>

### Q27. 숫자 금액대 검색 정규식 (3자리 단위 콤마 포함)
`"5,200,000"` 이나 `"3,800,000"` 처럼 콤마 기호가 찍힌 7자리 백만 단위 이상 정수 금액대를 잡는 정규식 매칭을 파워셸로 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "\d{1,3}(,\d{3})+"</pre>
</details>

### Q28. 검색 결과 개체 목록 중 첫 5행만 수집 (Select-Object)
에러가 너무 많아 가독성을 위해 처음 매칭된 5행의 결과 정보만 슬라이싱 수집해 보여주는 파이프라인(`select -first`)을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "ERROR" | Select-Object -First 5</pre>
</details>

### Q29. 검색 결과 개체 목록 중 마지막 3행만 수집 (Select-Object)
로그의 가장 마지막 하단부 에러 상황 3개만 역순으로 잘라서 수집하는 파이프라인(`select -last`)을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "ERROR" | Select-Object -Last 3</pre>
</details>

### Q30. 특정 예외 객체 포함 소스 파일만 바탕화면 CSV로 추출
`Select-String` 결과를 CSV 테이블로 파일 변환하여 저장할 수 있게 해주는 파워셸 변환 내보내기 명령어(`Export-Csv`)를 파일 경로와 연계해 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "*.xml" -Pattern "MGOODSTB" | Export-Csv -Path "$HOME\Desktop\xml_match.csv" -NoTypeInformation -Encoding utf8</pre>
</details>

---

### Q31 ~ Q50: 고급 파이프라인 결합 및 정규식 그룹 캡처 응용
### Q31. 특정 포트(9000번) 점유 프로세스의 상세 Name 알아내기
`Get-NetTCPConnection` 명령어로 로컬 포트 `9000`번의 점유 커넥션을 가져와, 해당 프로세스 ID(PID) 정보에 매핑되는 프로세스 정보를 `Get-Process`로 연결해 출력하는 한 줄 파이프라인을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-NetTCPConnection -LocalPort 9000 | ForEach-Object { Get-Process -Id $_.OwningProcess }</pre>
</details>

### Q32. XML 파일 내 쿼리 ID 속성 텍스트만 청소하여 수집
`.xml` 소스 내 쿼리 선언 줄 `id="query_name"`에서 쿼리 이름값인 `"query_name"` 단어 영역만 정규식 캡처 그룹으로 추출하여 화면에 출력하는 파워셸 스크립트를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "*.xml" -Pattern 'id="([^"]+)"' | ForEach-Object { $_.Matches.Groups[1].Value }</pre>
</details>

### Q33. 특정 문자열 포함 줄을 뺀 내용으로 덮어쓰기 저장 (파일 데이터 제거)
`db.config` 파일에서 `"db_password"` 단어가 들어있는 줄만 쏙 빼내고(NotMatch), 나머지 보안이 깨끗한 줄들로만 동일 파일 명칭에 덮어쓰기 갱신 저장하는 파워셸 파이프라인을 완성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>(Get-Content "db.config" | Select-String -Pattern "db_password" -NotMatch) | Out-File "db.config" -Encoding utf8</pre>
</details>

### Q34. 로그 파일 내 ORA 에러 유형별 빈도 카운팅 집계
`app.log` 내부에서 발생하는 오라클 DB 에러(`"ORA-XXXXX"` 구조) 문자열 패턴을 감지하여, 각 ORA 에러 기호 종류별로 몇 번씩 터졌는지 집계 요약해 주는 `Group-Object` 파이프를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "ORA-\d{5}" | Group-Object -Property Matches | Select-Object Name, Count</pre>
</details>

### Q35. 특정 폴더 하위 파일 중 검색어 포함된 고유 파일 개수 세기
D:\hmTest\backoffice 하위의 모든 파일 중 `"ERROR"`가 기재된 **서로 다른 파일의 총 개수**를 숫자로 구하세요.
<details><summary><b>정답 보기</b></summary>
<pre>(Get-ChildItem -Recurse D:\hmTest\backoffice\* | Select-String -Pattern "ERROR" | Select-Object Path -Unique).Count</pre>
</details>

### Q36. 특정 시간 범위 이후의 로그 행 검색 (파워셸 Where 연계)
각 로그 행 시작이 `"2026-07-06 18:30:00"` 처럼 적혀 있을 때, 특정 시간인 18시 30분 이후의 로그 행만 비교 연산하여 가져오는 파워셸 Where 람다 필터를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-Content "app.log" | Where-Object { $_ -match "^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})" -and [datetime]$Matches[1] -gt [datetime]"2026-07-06 18:30:00" }</pre>
</details>

### Q37. 자바 소스 내 public 메서드 선언 영역만 추출
프로젝트 서브 자바 파일 내에서 `"public "` 키워드가 붙고 반환 타입과 괄호가 조합된 정형적 메서드 라인을 정규식 매칭으로 찾아내는 sls 명령을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>sls -Path "*.java" -Pattern "public\s+\w+\s+\w+\(.*?\)"</pre>
</details>

### Q38. 검색 결과에서 행별 파일명, 라인번호, 본문 내용 엑셀형 표 제작
`Select-String` 결과 개체 목록을 가독성을 높이기 위해 `Path`, `LineNumber`, `Line` 속성만 선택적으로 포매팅하여 파워셸 콘솔창에 표 형태로 그리게 만드는 출력 포맷터(`Format-Table` 혹은 `ft`) 파이프를 덧붙이세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "*.log" -Pattern "ERROR" | Select-Object Path, LineNumber, Line | Format-Table -AutoSize</pre>
</details>

### Q39. 특정 IP 대역 기재 파일 찾아 복사하기
로그 및 설정 파일 중에서 `"192.168.10.206"` IP 주소가 적힌 물리 파일들을 감지하여, 백업을 위해 해당 파일들을 D:\backup 폴더 아래로 카피해 이동시키는 파이프 연계 명령을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "*.properties", "*.xml" -Pattern "192\.168\.10\.206" | ForEach-Object { Copy-Item $_.Path -Destination "D:\backup\" -Force }</pre>
</details>

### Q40. 파일 확장자가 2종류 이상인 다중 검색 필터 지정
`Get-ChildItem`을 사용해 `.properties` 설정 파일과 `.xml` 쿼리 맵핑 파일 단 2가지 형식 파일들만 가져와 그 안에서 비밀번호 관련 환경 키워드인 `"password"`를 찾아내게 유도하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-ChildItem -Recurse -Include *.properties, *.xml | Select-String -Pattern "password"</pre>
</details>

### Q41. 텍스트 라인 중 주석 및 빈 라인 완전 제외 유효 라인 카운팅
파워셸 상에서 특정 파일의 주석(# 이나 //)행과 공백 라인을 모조리 날려버린 후 실제로 돌아가는 순수 유효 설정 라인 수만 카운팅하는 식을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>(Get-Content "app.config" | Where-Object { $_ -notmatch '^\s*(#|//|$)' }).Count</pre>
</details>

### Q42. 오류 로그 아래 3줄에 쓰인 상세 예외 스택 확인
`app.log`에서 `"FATAL"` 단어가 들어있는 줄과 그 **바로 아래로 흘러나오는 3줄**의 스택 에러 행을 바인딩해 출력하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "FATAL" -Context 0,3</pre>
</details>

### Q43. 파일 수정 날짜 범위 한정하여 검색 대상 한정
오늘 하루 동안(즉, 현재 시간에서 1일 전인 `(Get-Date).AddDays(-1)`) 동안 새로 수정 기록된 로그 파일들만 대상으로 삼아 에러를 검색하는 파워셸 조합을 완성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-ChildItem -Filter *.log | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) } | Select-String -Pattern "ERROR"</pre>
</details>

### Q44. 정규식 특수기호 마침표 문자 자체 매칭
정규식 모드 하에서 IP 구분점 등으로 쓰인 일반 기호 마침표(`.`) 문자 자체를 검색 패턴으로 잡기 위해 마침표 앞에 부착하는 이스케이프 기호를 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "192\.168\.10\.206"</pre>
</details>

### Q45. 특정 쿼리 ID가 누락된 파일 검출
하위 폴더의 모든 XML 파일 중 정산 매출 등록용 쿼리 영역인 `"insertDailySales"` 문자열이 포함되어 있지 **않아서** 배치 정산에서 제외 위험이 있는 쿼리 파일 경로 리스트를 획득하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-ChildItem -Recurse -Filter *.xml | ForEach-Object { if (!(Select-String -Path $_.FullName -Pattern "insertDailySales" -SimpleMatch)) { $_.FullName } }</pre>
</details>

### Q46. 특정 IP 패턴이 감지된 파일 수량 카운팅
`"192.168.10."` 대역의 IP를 소스 코드 내에 하드코딩해 둔 유니크한 파일이 전체 몇 개나 등록되어 있는지 파일 수량을 출력하세요.
<details><summary><b>정답 보기</b></summary>
<pre>(Select-String -Path "*.java", "*.xml" -Pattern "192\.168\.10\.\d+").Path | Select-Object -Unique | Measure-Object | Select-Object -ExpandProperty Count</pre>
</details>

### Q47. 매치된 행 정보 중 특정 단어 포함 여부 2차 논리 검사
`sls` 결과물 중, 에러 로그 본문에 `"Connection"` 이 들어있는지 여부만 True/False로 신속 판별해주는 논리 반환 구문을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>[bool](Select-String -Path "app.log" -Pattern "ERROR" | Select-String -Pattern "Connection")</pre>
</details>

### Q48. 텍스트 라인 중 알파벳을 배제한 숫자 전용 라인 수집
대소문자 알파벳 `[a-zA-Z]`가 전혀 섞여 있지 않고 순수 숫자로만 구성되어 기록된 통계 데이터 줄들만 정규식으로 감지해 보세요.
<details><summary><b>정답 보기</b></summary>
<pre>Select-String -Path "app.log" -Pattern "^[^a-zA-Z]+$"</pre>
</details>

### Q49. 파일 명칭에 특정 단어가 들어간 파일들에 대해 한정하여 검색
파일의 풀 패스 경로에 `"hq"` 또는 `"estimate"` 키워드가 포함된 경우만 매핑 필터링하여 그 소스 내에서 테이블 명칭 `"MUSERSTB"`를 쫓아가 찾는 파이프라인 구문을 구현하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-ChildItem -Recurse -Filter *.xml | Where-Object { $_.FullName -match "hq|estimate" } | Select-String -Pattern "MUSERSTB"</pre>
</details>

### Q50. PowerShell Select-String 종합 마스터 문제
파워셸 환경에서 다음 모든 단계를 일괄 가동하는 한 줄 파이프라인을 완성하세요.
1. `"D:\hmTest\backoffice"` 하위 경로의 모든 자바 소스 파일(`*.java`) 중, 최근 7일 내에 수정(`LastWriteTime -gt (Get-Date).AddDays(-7)`)된 소스 목록을 가져옵니다.
2. 각 소스 내에서 대소문자 없이 `"SqlSession"` 혹은 `"SqlMapClient"` 라는 단어가 발견되는 라인을 찾아내어, 
3. 해당 라인의 실제 파일 절대경로, 발견된 줄 번호, 그리고 텍스트 본문 내용을 바탕화면의 `"sql_client_recent.csv"` 테이블 파일로 깨끗이 변환 저장하세요.
<details><summary><b>정답 보기</b></summary>
<pre>Get-ChildItem -Recurse D:\hmTest\backoffice\*.java | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) } | Select-String -Pattern "SqlSession", "SqlMapClient" | Select-Object Path, LineNumber, Line | Export-Csv -Path "$HOME\Desktop\sql_client_recent.csv" -NoTypeInformation -Encoding utf8</pre>
</details>
