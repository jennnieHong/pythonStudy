# HMS 개발자를 위한 터미널 검색 실무 연습 문제집 (총 150제)

본 문제집은 서버 내 대량의 로그 파일을 추적하거나 프로젝트 소스 코드 폴더에서 특정 자바 클래스, SQL Mapper 쿼리문 등을 즉각 탐색할 때 활용하는 **터미널(CLI) 검색 명령어 실무 연습 문제집**입니다. 

윈도우 기본 CMD(`findstr`), 현대식 PowerShell(`Select-String`), 리눅스/유닉스 서버 환경(`grep`)을 나누어 총 3개 카테고리별로 50문제씩, **총 150개의 실습 문제**를 제공합니다.

> [!TIP]
> **학습 상태 기록 및 대시보드 연동**: 각 문항별 진척도는 동일 폴더 내 [python_learning_progress.json](./python_learning_progress.json) 파일에 저장되며, **[📊 실시간 진척도 대시보드(Python_Learning_Progress.md)](./Python_Learning_Progress.md)**에서 진행 바와 합격 유무를 눈으로 보며 시각적으로 관리할 수 있습니다.
> * 상태 업데이트: [update_progress.py](./update_progress.py) 스크립트를 통해 쉽게 토글합니다. (예: `python update_progress.py CmdCat1 Q5 True`)

---

## 📚 카테고리별 터미널 검색 실전 문제집 (각 50제)

### 1. [카테고리 1: Windows CMD `findstr` 검색 (50제)](./CMD_Search_Exercise_Book_CmdCat1.md)
* 윈도우 커맨드 창에서 `findstr`을 활용한 파일 탐색 기초, 대소문자 무시 검색, 하위 폴더 재귀 탐색, 줄 번호 출력, 다중 단어 검색 및 정규식 메칭 기법.

### 2. [카테고리 2: Windows PowerShell `Select-String` 검색 (50제)](./CMD_Search_Exercise_Book_CmdCat2.md)
* 파워셸의 파일 스캔 파이프라인 연계, `Get-ChildItem` 연동, 와일드카드 필터링, 정규표현식 매칭, 특정 라인 전후 출력, 대량 파일 고속 스캔 및 결과 텍스트 추출.

### 3. [카테고리 3: Linux/Unix `grep` 및 실무 로그 분석 (50제)](./CMD_Search_Exercise_Book_CmdCat3.md)
* 운영 서버 리눅스 터미널의 필수 기능인 `grep`, `egrep` 활용법. 로그 파일에서 특정 시간대 검색, 에러 카운팅, 에러 줄 앞뒤 맥락 라인 출력(`-A`, `-B`, `-C`), 파이프라인(`|`)과 조합한 프로세스 필터링 및 실무 압축 로그(`.gz`) 고속 스캔(`zgrep`).

---

### 💡 실습 팁
각 문제집 하단의 **[정답 보기]**를 펼치면, 별도의 파이썬 설치 없이 윈도우 명령창(CMD), 파워셸(PowerShell), 혹은 리눅스 셸에서 즉시 복사해서 실행할 수 있는 명령어 예제가 수록되어 있습니다.

---

### 📘 추천 연계 가이드
더 깊이 있는 터미널 검색 실무 비법은 아래 가이드를 학습하세요.
* **[터미널(CLI) 고급 검색 마스터 가이드 (파일명/폴더명 구분 및 멀티라인 범위 검색)](./Terminal_Advanced_Search_Master_Guide.md)**
* **[실무 개발자의 로그 관리 및 검색 결과 문서화 가이드 (리다이렉션 및 중앙 로그 시스템)](./Terminal_Search_Log_Management_Guide.md)**


