# 터미널 검색 실무 연습 문제집 - [카테고리 3] Linux/Unix grep 및 로그 검색 (50제)

> [!NOTE]
> **진척도 기록**: 이 카테고리의 학습 상태는 [python_learning_progress.json](./python_learning_progress.json) 내의 `"CmdCat3"` 키에 기록됩니다.
> * 상태 업데이트 명령: `python update_progress.py CmdCat3 Q1 True` (Q1 문제를 완료로 변경)

본 문제집은 운영 및 검증 리눅스(Linux/Unix) 서버 터미널 환경에서 대량의 시스템 로그 파일(`.log`, `.out`, `.gz` 압축파일)을 고속 검색하고 정밀 스캔할 때 필수로 다루는 `grep` 및 `zgrep` 명령어 실무형 50문제를 수록하고 있습니다.

---

### Q1 ~ Q15: grep 기본 조작 및 필수 옵션
### Q1. 로그 파일 내 단순 문자열 검색
`system.log` 파일에서 `"ERROR"` 라는 단어가 포함된 모든 행들을 찾아 화면에 출력하는 리눅스 기본 명령을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "ERROR" system.log</pre>
</details>

### Q2. 대소문자 무시 검색 (Case Insensitive)
대소문자 구별 없이(즉, `Error`, `error`, `ERROR` 모두 포함) `system.log` 파일에서 찾도록 지시하는 옵션을 적용하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -i "error" system.log</pre>
</details>

### Q3. 매칭된 행 번호 함께 표시
`system.log` 파일 내에서 에러가 발생한 위치를 소스 줄 단위로 파악하도록 매치된 행 번호를 왼쪽에 띄워 보여주는 옵션을 적용하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -n "ERROR" system.log</pre>
</details>

### Q4. 매치된 행들의 총 개수(Count) 구하기
매칭된 개별 행 본문들을 화면에 쏟아내어 채우지 않고, 오직 매칭 성공한 줄이 총 몇 개가 들어있었는지 **정수 개수 숫자**만 즉시 보여주는 카운팅 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -c "ERROR" system.log</pre>
</details>

### Q5. 하위 디렉토리 전체 순회 검색 (Recursive)
현재 폴더 하위에 있는 모든 파일 및 서브 디렉토리를 깊이 탐색하며 문자열 `"CustomAuthenticationProvider"`를 색인하는 재귀적 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -r "CustomAuthenticationProvider" .</pre>
</details>

### Q6. 매칭되는 파일명 리스트만 깔끔하게 출력
`system.log` 파일 본문은 출력하지 않고, 단지 해당 문자열 `"Exception"`을 포함하는 파일들의 경로명 이름 목록만 획득하는 옵션을 지정하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -l "Exception" *.log</pre>
</details>

### Q7. 매칭되지 않은 파일명 리스트만 출력 (반전 파일 리스트)
특정 단어 `"CommonAuditSql"`를 포함하고 있지 **않은** 설정/쿼리 파일 리스트만 모아서 출력해 주는 부정 파일 탐색 옵션을 적용하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -L "CommonAuditSql" *.xml</pre>
</details>

### Q8. 단어 단위 완전 매치 (Whole Word Match)
검색어 뒤에 다른 문자열이 붙은 형태(예: `error_code`, `system_error`)는 제외하고, 오직 독립된 단어로만 떨어져 완전 일치하는 형태(예: `error` 단독)만 감지하는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -w "error" system.log</pre>
</details>

### Q9. 제외 검색 (NOT 필터링)
로그 중에서 정보성 로그 문자열인 `"INFO"` 가 포함된 줄들을 모조리 제외해 버리고(Not Match), 나머지 줄들만 출력해 주는 반전 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -v "INFO" system.log</pre>
</details>

### Q10. 행의 맨 첫 머리글자 비교
줄의 시작 부분에 특정 단어 `"START"`가 박혀있는 로그 행들만 골라내는 기호(`^`)를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "^START" system.log</pre>
</details>

### Q11. 행의 맨 마지막 끄트머리 비교
줄의 맨 마지막 끝에 특정 단어 `"END"` 로 끝맺음 처리된 행들만 골라내는 기호(`$`)를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "END$" system.log</pre>
</details>

### Q12. 검색할 여러 패턴을 텍스트 파일로 지정해 불러오기
`patterns.txt` 파일에 한 줄씩 적어둔 검색 키워드 목록(예: `ERROR`, `FATAL`, `CRITICAL` 등)을 참조하여 대상 로그를 일괄 색인하는 매개변수를 적용하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -f patterns.txt system.log</pre>
</details>

### Q13. 확장 정규표현식(Extended Regex) 활성화 옵션
더 다양한 정규식 메타기호(예: `|` (OR), `+` 등)를 역슬래시 이스케이프 기호 없이 온전히 사용 가능하게 열어주는 옵션(E)을 기재하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -E "ERROR|FATAL" system.log</pre>
</details>

### Q14. 매치된 문자열 영역만 추출 출력 (Only Matching)
매칭된 라인 전체를 다 가져오지 않고, 오직 매칭 성공 조건에 걸린 물리적 단어 조각 정보(예: `"IP: 192.168.10.206"`)만 발췌하여 출력하는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -o "192\.168\.10\.[0-9]\+" system.log</pre>
</details>

### Q15. 여러 파일 검색 시 파일 경로/이름 출력 억제
다량의 로그 파일(예: `*.log`)들을 대량 조회할 때, 각 매칭 행 앞에 출력되는 접두사 파일 이름 기호를 가려서 깔끔하게 데이터 내용만 보여주게 하는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -h "ERROR" *.log</pre>
</details>

---

### Q16 ~ Q35: 맥락 스캔 (Context) 및 압축 로그 검색 (zgrep)
### Q16. 에러 라인의 바로 다음 행 출력 (After Context)
에러가 터진 라인의 바로 뒤 상황을 보기 위해, `"ERROR"` 문자열이 발생한 줄과 **바로 뒤로 이어지는 3줄**의 로그 내용을 함께 묶어 출력하는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -A 3 "ERROR" system.log</pre>
</details>

### Q17. 에러 라인의 바로 직전 행 출력 (Before Context)
어떤 요청을 보내서 에러가 났는지 알 수 있게 `"ERROR"` 라인 **바로 위에 적힌 2줄**의 로그를 함께 묶어 출력하는 옵션을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -B 2 "ERROR" system.log</pre>
</details>

### Q18. 에러 라인의 앞뒤를 감싸는 맥락 주변 출력 (Context)
가장 표준적인 디버그 추적 기법으로, `"Exception"` 발생 행의 **위로 3줄, 아래로 3줄**의 주변 흐름 정보를 일괄 묶어 출력하는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -C 3 "Exception" system.log</pre>
</details>

### Q19. 압축된 로그 파일 내 검색 (zgrep)
서버 공간 관리를 위해 날짜가 지난 이전 로그 파일은 `.gz` 압축 형태로 아카이빙 처리됩니다. 이 `system.log.2026-07-06.gz` 압축 파일을 풀지 않고 압축 상태 그대로 고속으로 단어 `"ERROR"`를 검색하는 리눅스 명령어를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>zgrep "ERROR" system.log.2026-07-06.gz</pre>
</details>

### Q20. 특정 패턴 2차 필터링 파이프 연계 (AND 조건)
`system.log` 에서 문자열 `"ERROR"` 가 포함되어 있으면서, 한 줄 내에 동시에 `"SDAILYTB"` 라는 DB 테이블명이 함께 적혀 있는 행만을 필터링하는 파이프 조합을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "ERROR" system.log | grep "SDAILYTB"</pre>
</details>

### Q21. 대량 로그 파일 목록을 병렬로 고속 검색하는 유틸리티 연동 (xargs)
`find` 명령어로 찾은 다량의 로그 파일 목록들(`*.log`)을 받아 프로세서 병렬 파이프라인으로 `grep`을 고속 작동시켜 단어 `"FATAL"`을 스캔하게 하는 연계 조합을 기재하세요.
<details><summary><b>정답 보기</b></summary>
<pre>find . -name "*.log" | xargs grep "FATAL"</pre>
</details>

### Q22. 바이너리 파일 무시 옵션
검색 범위에 바이너리 실행 파일이나 컴파일된 자바 클래스 파일(`.class`)이 포함되어 있을 때, 해당 바이너리 파일을 텍스트 스캔에서 무시하거나 에러를 내뿜지 않고 텍스트 형태로 강제 간주 검색하거나 Skip하는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -I "MUSERSTB" *.class
# 또는 바이너리 제외
grep -r --binary-files=without-match "MUSERSTB" .</pre>
</details>

### Q23. 심볼릭 링크 파일 추적 검색 허용 옵션
디렉토리 내에 물리 파일이 아닌 가상 바로가기 링크 파일(Symbolic Link)이 있을 때, 재귀 검색 시 해당 링크의 링크 원본 디렉토리까지 진입하여 문자열을 찾도록 허용하는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -R "ERROR" . (소문자 -r 대신 대문자 -R을 주면 심볼릭 링크까지 따라가 탐색합니다.)</pre>
</details>

### Q24. 대괄호 및 특수기호 매칭 이스케이프
로그에서 에러 코드 대괄호 묶음 `"[ERROR]"`를 정확히 패턴 기호 대괄호가 아닌 실제 물리적 대괄호 문자로 매칭하기 위한 백슬래시 이스케이프 정규식을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "\[ERROR\]" system.log</pre>
</details>

### Q25. 특정 환경 설정 주석행 필터 탈락
`application.properties` 설정 파일에서 샵 기호(`#`)로 시작하는 모든 주석 라인을 제거하고, 유효한 설정 구문이 있는 줄만 필터링해 가져오는 반전 검색을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -v "^#" application.properties</pre>
</details>

### Q26. 공백 행 전체 제외 제거 (Empty Line Filter)
텍스트 파일에서 개행 개행이 반복되어 빈 줄로 보이는 모든 행들을 날려버리고 알맹이 텍스트 내용만 추려 출력해 주는 부정 검색 조합을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -v "^$" system.log</pre>
</details>

### Q27. 특정 IP 주소 대역 스캔 정규식
`system.log` 로그에서 `"192.168.10.X"` 대역에 속하는 IP 주소(예: `192.168.10.206`)를 가진 로그 줄을 찾아내기 위해 마침표를 이스케이프한 정규식 grep 문장을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "192\.168\.10\.[0-9]\+" system.log</pre>
</details>

### Q28. 검색어에 매칭되는 행의 바이트 오프셋 위치 출력
각 검색 성공 라인 맨 앞에 파일 내 시작 지점으로부터 몇 번째 바이트 위치에 들어있는 줄인지 물리적 바이트 위치 정수를 함께 보여주는 옵션을 적용하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -b "ERROR" system.log</pre>
</details>

### Q29. 다중 디렉토리 경로 지정 검색
현재 디렉토리와 상위 백업 디렉토리인 `/var/log/backup` 두 경로에서 동일하게 문자열 `"DB_FAIL"`을 동시에 스캔해 오는 대상 나열 경로 작성법을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "DB_FAIL" . /var/log/backup/*</pre>
</details>

### Q30. 정규식 확장: 1회 이상 연속 매칭 기호
정규식 모드 하에서 앞선 문자나 숫자 패턴이 최소 1번 이상 등장해야 함을 나타내는 수량자 기호(`+`)를 이스케이프 조합(`\+`)으로 나타내어 여러 자릿수 연속 숫자를 매칭하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "[0-9]\+" system.log</pre>
</details>

---

### Q31 ~ Q50: 실무 셸 파이프라인 및 시스템 모니터링 연동
### Q31. 특정 포트(9000번) 점유 프로세스의 PID 및 프로세스 명칭 실시간 확인
네트워크 연결 모니터링 명령어인 `netstat -nap` 결과 출력 중에서 포트번호 `9000`번을 점유 바인딩하고 대기(LISTEN)하는 프로세스 ID와 이름을 골라내는 grep 필터링을 완성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>netstat -nap | grep "9000" | grep "LISTEN"</pre>
</details>

### Q32. 실시간 구동 로그파일 미러링 모니터링 조합 (tail -f)
실시간 로그 모니터링 명령어인 `tail -f system.log`와 조합하여, 서버가 구동되면서 실시간으로 뿜어내는 로그들 중 `"FATAL"` 단어가 들어오는 줄만 즉시 실시간으로 잡아 화면에 분출시키는 모니터 파이프를 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>tail -f system.log | grep "FATAL"</pre>
</details>

### Q33. 특정 메모리 점유가 높은 프로세스 필터링 (ps aux)
시스템 프로세스 현황 명령어인 `ps aux` 실행 결과에서 파이썬 데몬 프로세스인 `"python"`이 가동 중인 행들만 뽑아내는 grep 조합을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>ps aux | grep "python"</pre>
</details>

### Q34. 매칭 결과 줄 수의 카운팅 집계 연계 (wc -l)
grep의 `-c` 옵션 외에, 다른 가공 파이프 출력 결과를 받아 최종적으로 걸러진 결과 라인 수가 정확히 몇 줄인지 카운트해 주는 리눅스 유틸리티 명령어 `wc -l` 을 파이프라인 끝에 조합해 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "ERROR" system.log | wc -l</pre>
</details>

### Q35. 검색 결과 리다이렉트 저장
`system.log`에서 일자별 통계 지시 문자열인 `"STATISTICS"`가 박힌 행들만 추려내어 화면에 띄우지 않고 `"daily_report.txt"` 새 텍스트 파일에 라이팅 저장시키는 기호(`>`)를 이어 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "STATISTICS" system.log > daily_report.txt</pre>
</details>

### Q36. 특정 시간 범위의 로그만 필터링 검색
로그의 각 행이 `"08:45:12"` 와 같은 시각으로 시작할 때, `08:30`분부터 `08:59`분까지(즉, 08시 30분대에서 50분대 영역) 발생한 로그만 정규표현식 범위를 이용해 매치해 출력하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -E "^08:[3-5][0-9]:" system.log</pre>
</details>

### Q37. 디렉토리 검색 범위 중 특정 폴더 제외 옵션 (--exclude-dir)
서브 디렉토리를 깊이 탐색하되, 임시 파일 보관이나 빌드 관련 폴더인 `node_modules` 이나 `target` 폴더 내부는 검색 대상에서 아예 누락하여 스캔 속도를 단축시키는 옵션을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -r --exclude-dir={node_modules,target} "ERROR" .</pre>
</details>

### Q38. 디렉토리 검색 범위 중 특정 파일 패턴 제외 옵션 (--exclude)
재귀 검색 시 용량이 너무 큰 백업 로그 파일 확장자 `*.bak` 나 `*.tmp` 파일 내부는 텍스트 스캔에서 배제하여 스킵 처리하는 옵션을 기재하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -r --exclude=*.{bak,tmp} "ERROR" .</pre>
</details>

### Q39. 매칭 텍스트 주변의 고유 헤더 및 라벨 포함 출력 (정규식 OR 조합)
`system.log` 스캔 시 `"ERROR"` 라인뿐만 아니라, 그 에러가 정확히 어느 모듈 소속인지 파악하기 위해 모듈 헤더 키워드인 `"MODULE_HEADER"` 가 박힌 라인도 함께 추출되도록 정규식 OR(`|`) 조건으로 묶으세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -E "ERROR|MODULE_HEADER" system.log</pre>
</details>

### Q40. grep 실행 시 리턴하는 상태 코드 확인 (exit code)
리눅스 셸 상에서 grep을 실행해 특정 키워드를 찾는 데 성공했을 때 셸 시스템 특수 변수 `$?` 에 담겨 나오는 코드 정수값은 무엇인가요?
<details><summary><b>정답 보기</b></summary>
<pre># 성공적으로 찾았으면 0을 리턴하고, 찾지 못했으면 1을 리턴합니다. (쉘 스크립트 작성 시 if 조건문으로 활용)</pre>
</details>

### Q41. 쉘 특수 변수를 이용한 직전 검색 성공 여부 출력
방금 전 기동시킨 grep 명령어의 종료 성공 여부 코드(`0` 또는 `1`)를 셸 화면에 에코로 프린트해 보는 명령을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>echo $?</pre>
</details>

### Q42. 특정 검색어 제외 필터링으로 로그 모니터링 정제
`tail -f system.log`로 들어오는 실시간 로그 스트림 중, 과도하게 화면을 지저분하게 만드는 하트비트 체크 문자열 `"HEARTBEAT"` 라인은 콘솔 모니터 화면 출력에서 완전 걸러내 배제하는 실시간 필터링을 구성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>tail -f system.log | grep -v "HEARTBEAT"</pre>
</details>

### Q43. 검색 범위 지정 중 특정 파일만 지정 (--include)
재귀 스캔 시 오직 환경 속성 설정 파일 규격인 `*.properties` 파일 내부만 조회하여 환경 변수 `"db_url"`을 추적하게 하는 include 파일 타겟 옵션을 사용해 보세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -r --include=*.properties "db_url" .</pre>
</details>

### Q44. 정규식 내의 마디 문자 기호 자체 매칭
정규식 모드 하에서 실제 글자 점(`.`) 기호 자체를 검색 패턴으로 잡기 위해 부착하는 이스케이프 백슬래시 작성법을 쓰세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep "\." system.log</pre>
</details>

### Q45. ORA-XXXXX 형태의 모든 에러 번호 리스트 추출
`oracle_alert.log` 파일 내에서 발생하는 모든 오라클 에러 코드 번호 줄을 중복을 배제하여 정렬한 상태로 모으는 파이프라인 조합(sort 및 uniq 명령어 결합)을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -o "ORA-[0-9]\+" oracle_alert.log | sort | uniq</pre>
</details>

### Q46. 특정 디렉토리 내의 XML 매퍼 파일 내 쿼리문 탐색
`D:\hmTest\backoffice` 및 하위 폴더의 모든 XML 파일(`*.xml`) 내에서 테이블명 `"MGOODSTB"`이 쓰인 위치를 줄번호와 함께 찾는 최적의 실무 조합 명령을 적으세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -rn --include=*.xml "MGOODSTB" D:\hmTest\backoffice/</pre>
</details>

### Q47. 단어의 완전 매칭 판단 2차 논리 검사
`grep` 결과물 중, 에러 로그 본문에 `"Connection"` 이 들어있는지 여부만 True/False로 신속 판별해주는 논리 반환 구문을 작성하세요.
<details><summary><b>정답 보기</b></summary>
<pre>if grep -q "Connection" system.log; then echo "True"; else echo "False"; fi</pre>
</details>

### Q48. 텍스트 라인 중 알파벳을 배제한 숫자 전용 라인 수집
대소문자 알파벳 `[a-zA-Z]`가 전혀 섞여 있지 않고 순수 숫자로만 구성되어 기록된 통계 데이터 줄들만 정규식으로 감지해 보세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -v "[a-zA-Z]" system.log</pre>
</details>

### Q49. 파일 명칭에 특정 단어가 들어간 파일들에 대해 한정하여 검색
파일의 풀 패스 경로에 `"hq"` 또는 `"estimate"` 키워드가 포함된 경우만 매핑 필터링하여 그 소스 내에서 테이블 명칭 `"MUSERSTB"`를 쫓아가 찾는 파이프라인 구문을 구현하세요.
<details><summary><b>정답 보기</b></summary>
<pre>find . -name "*.xml" | grep -E "hq|estimate" | xargs grep "MUSERSTB"</pre>
</details>

### Q50. Linux grep 종합 마스터 문제
리눅스 서버 셸 환경에서 다음 모든 단계를 일괄 가동하는 한 줄 파이프라인을 완성하세요.
1. `/var/log/hyundai` 및 모든 하위 경로의 모든 로그 파일 중, 파일명이 `app_`으로 시작하고 `.log`로 끝나는 파일들을 훑습니다.
2. 각 로그 파일 소스 내에서 대소문자 없이 `"SqlSession"` 혹은 `"SqlMapClient"` 라는 단어가 발견되는 라인을 찾아내어, 
3. 해당 라인의 실제 파일 절대경로, 발견된 줄 번호, 그리고 텍스트 본문 내용을 바탕화면의 `"sql_client_recent.csv"` 테이블 파일로 깨끗이 변환 저장하세요.
<details><summary><b>정답 보기</b></summary>
<pre>grep -rn --include="app_*.log" -E "SqlSession|SqlMapClient" /var/log/hyundai/ > ~/Desktop/sql_client_recent.csv</pre>
</details>
