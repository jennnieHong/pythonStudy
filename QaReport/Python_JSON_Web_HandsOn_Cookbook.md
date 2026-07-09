# Python & Web JSON 연동 5분 완성 실습북 (Hands-on Cookbook)

본 실습북은 이론 학습을 마치고, 파이썬을 이용한 JSON 제어 및 웹 비동기 연동을 **단 5분 만에 직접 실습하여 눈으로 확인**해 볼 수 있는 단계별 실습 가이드입니다. 

준비물: 파이썬이 설치된 PC와 웹 브라우저(Chrome 등).

---

## 💻 실습 순서 요약

```text
[Step 1] JSON 파일 쓰기 ──► [Step 2] JSON 파일 읽기 ──► [Step 3] 초경량 웹 서버 켜기 ──► [Step 4] 웹 브라우저로 API 호출 테스트
```

---

## 1단계 [Step 1]: 파이썬으로 JSON 파일 생성하기 (`step1_write.py`)

로컬 경로에 `student.json` 파일을 생성하고 학습 정보 딕셔너리를 저장하는 파이썬 코드를 작성하고 실행합니다.

### 1.1 소스코드 작성
아래 코드를 복사하여 동일 폴더 내 **`step1_write.py`** 파일로 저장하세요.
```python
# step1_write.py
import json

# 1. 저장할 데이터 정의
learning_data = {
    "name": "HMS_Developer",
    "subject": "Python_JSON_Web",
    "completed": True,
    "score": 100
}

# 2. JSON 파일 쓰기
with open("student.json", "w", encoding="utf-8") as f:
    json.dump(learning_data, f, indent=4, ensure_ascii=False)

print("성공: student.json 파일이 정상적으로 생성되었습니다!")
```

### 1.2 실행하기
터미널에서 아래 명령어로 스크립트를 구동하세요.
```bash
python step1_write.py
```
* **결과 확인**: 폴더 내에 `student.json` 파일이 정상적으로 생성되었는지 확인하고, 텍스트 에디터로 열어봅니다.

---

## 2단계 [Step 2]: 생성된 JSON 파일 읽고 갱신하기 (`step2_read.py`)

1단계에서 저장된 `student.json` 파일을 불러와 값을 수정(점수를 100에서 105로 변경)한 후 다시 저장해 봅니다.

### 2.1 소스코드 작성
아래 코드를 복사하여 **`step2_read.py`** 파일로 저장하세요.
```python
# step2_read.py
import json

# 1. JSON 파일 로드
with open("student.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"로드된 학생명: {data['name']}, 기존 점수: {data['score']}")

# 2. 데이터 수정
data["score"] = 105
data["memo"] = "보너스 점수 추가 적용"

# 3. 갱신된 데이터를 파일에 재저장
with open("student.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("성공: student.json 파일이 105점으로 갱신되었습니다!")
```

### 2.2 실행하기
```bash
python step2_read.py
```
* **결과 확인**: `student.json` 파일의 `score` 항목이 `105`로 바뀌고 `memo` 속성이 신규 추가되었는지 메모장에서 확인하세요.

---

## 3단계 [Step 3]: 초경량 웹 API 서버 만들기 (`step3_server.py`)

이제 브라우저의 비동기 요청을 받아 `student.json` 파일의 내용을 화면으로 쏘아보내 주는 9090번 포트 웹 서버를 실행합니다.

### 3.1 소스코드 작성
아래 코드를 복사하여 **`step3_server.py`** 파일로 저장하세요.
```python
# step3_server.py
import http.server
import socketserver
import json
import os

PORT = 9090
JSON_FILE = "student.json"

class SimpleApiHandler(http.server.SimpleHTTPRequestHandler):
    
    # 브라우저 도메인이 달라도 통신을 허용해주는 CORS 헤더
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    # 브라우저가 GET 호출을 보냈을 때의 처리 핸들러
    def do_GET(self):
        if self.path == "/api/student":
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    student_data = json.load(f)
                
                # 200 OK 응답 전송
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                
                # JSON 데이터 응답 분출
                self.wfile.write(json.dumps(student_data).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SimpleApiHandler) as httpd:
        print(f"🚀 [임시 API 서버] 구동 중 -> http://localhost:{PORT}/api/student")
        httpd.serve_forever()
```

### 3.2 실행하기
```bash
python step3_server.py
```
* **결과 확인**: 터미널에 `[임시 API 서버] 구동 중...` 메시지가 뜨며 대기 모드로 들어갑니다. (서버를 켠 채로 4단계로 진행하세요.)

---

## 4단계 [Step 4]: 웹 브라우저로 API 호출 확인하기 (`step4_client.html`)

이제 브라우저에서 버튼을 눌렀을 때, 9090번 파이썬 서버로부터 JSON 데이터를 비동기로 통신 수집하여 경고창(Alert)으로 뿌려주는 HTML을 만듭니다.

### 4.1 소스코드 작성
아래 코드를 복사하여 **`step4_client.html`** 파일로 저장하세요.
```html
<!-- step4_client.html -->
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>JSON API 비동기 수신 실습</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 100px; }
        button { padding: 15px 30px; font-size: 16px; font-weight: bold; background-color: #007bff; color: #white; border: none; border-radius: 5px; cursor: pointer; color: white; }
        button:hover { background-color: #0056b3; }
        #result-box { margin-top: 30px; font-size: 18px; color: #28a745; font-weight: bold; }
    </style>
</head>
<body>

    <h2>⚡ 파이썬 API 서버 비동기 데이터 획득 실습</h2>
    <button onclick="fetchStudentInfo()">학생 정보 가져오기</button>
    <div id="result-box"></div>

    <script>
        function fetchStudentInfo() {
            const url = "http://localhost:9090/api/student";

            // 브라우저 내장 fetch API를 이용해 비동기 연동
            fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error("서버 응답 오류");
                }
                return response.json(); // 응답 바이너리를 JSON 오브젝트로 변환
            })
            .then(data => {
                // 화면의 result-box 영역에 텍스트 갱신 출력
                document.getElementById("result-box").innerText = 
                    `이름: ${data.name} | 과목: ${data.subject} | 최종점수: ${data.score}점 (${data.memo})`;
            })
            .catch(error => {
                alert("연동 실패! step3_server.py 웹 서버가 구동 중인지 확인해 보세요.");
                console.error(error);
            });
        }
    </script>
</body>
</html>
```

### 4.2 실행 및 확인하기
1. 탐색기에서 `step4_client.html` 파일을 더블 클릭하여 크롬 등 웹 브라우저로 실행합니다.
2. 화면 중앙의 **[학생 정보 가져오기]** 버튼을 클릭합니다.
3. 브라우저 화면 하단에 **`이름: HMS_Developer | 과목: Python_JSON_Web | 최종점수: 105점 (보너스 점수 추가 적용)`** 문장이 1초의 지연도 없이 실시간으로 비동기 호출 출력되는 경이로운 광경을 목격하실 수 있습니다!
