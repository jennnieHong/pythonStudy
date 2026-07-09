# Python & Web API JSON 연동 실전 연습 문제집

본 문제집은 파이썬을 활용해 JSON 형식의 데이터를 제어하고, 로컬 설정 파일 관리 프로그램을 구축하며, 브라우저(JavaScript)와 파이썬 웹 서버 간 API 통신을 구현하는 실무 역량을 점검하기 위한 연습 문제 모음입니다. 각 문항 하단의 **정답 보기**를 통해 모범 정답 코드를 확인할 수 있습니다.

---

## 목차
1. [기초 문제 (Q1 ~ Q8): JSON 기초 직렬화/역직렬화 및 파일 I/O](#basic)
2. [중급 문제 (Q9 ~ Q15): 중첩 데이터 갱신, 집계 및 실시간 파일 갱신](#intermediate)
3. [심화 문제 (Q16 ~ Q20): REST Web API 연동, CORS 및 Fetch AJAX 통신](#advanced)

---

<a name="basic"></a>
## 1. 기초 문제 (Q1 ~ Q8): JSON 기초 직렬화/역직렬화 및 파일 I/O

### Q1. 딕셔너리를 JSON 문자열로 변환 (dumps)
파이썬 딕셔너리 `data = {"user_id": "admin", "login_count": 3}`을 JSON 포맷 텍스트 문자열로 직렬화하여 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json
data = {"user_id": "admin", "login_count": 3}
json_str = json.dumps(data)
print(json_str) # '{"user_id": "admin", "login_count": 3}'</pre>
</details>

### Q2. JSON 문자열을 딕셔너리로 복원 (loads)
JSON 형식 문자열 `json_str = '{"complete": true, "score": 95}'`를 파이썬 딕셔너리 객체로 변환하여 점수(`score`) 값을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json
json_str = '{"complete": true, "score": 95}'
data = json.loads(json_str)
print(data["score"]) # 95</pre>
</details>

### Q3. 한글 깨짐 방지 dumps 옵션 (ensure_ascii)
딕셔너리 `user = {"name": "홍길동"}`을 JSON 문자열로 변환하되, 한글이 유니코드 기호(`\uac00`)로 변환되지 않고 한글 그대로 보이도록 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json
user = {"name": "홍길동"}
json_str = json.dumps(user, ensure_ascii=False)
print(json_str) # '{"name": "홍길동"}'</pre>
</details>

### Q4. 딕셔너리를 JSON 파일로 저장 (dump)
딕셔너리 `config = {"db_host": "192.168.10.206", "port": 5432}`를 파일 `"db_config.json"`에 가독성 들여쓰기 4칸(`indent=4`) 옵션을 주어 저장하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json
config = {"db_host": "192.168.10.206", "port": 5432}
with open("db_config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4)</pre>
</details>

### Q5. JSON 파일에서 데이터 읽기 (load)
Q4에서 저장한 `"db_config.json"` 파일을 읽어서 파이썬 딕셔너리로 받아온 뒤, `"db_host"` 값을 출력하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json
with open("db_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
print(config["db_host"]) # 192.168.10.206</pre>
</details>

### Q6. JSONDecodeError 예외 처리
구조가 깨져 파싱되지 않는 불완전한 문자열 `bad_json = "{'id': 'admin'"` (키가 쌍따옴표가 아닌 홀따옴표로 선언됨)을 파싱하려 할 때 발생하는 `json.JSONDecodeError` 예외를 try-except 문으로 잡아 처리하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json
bad_json = "{'id': 'admin'"
try:
    data = json.loads(bad_json)
except json.JSONDecodeError as e:
    print("JSON 파싱 에러 포착:", e)</pre>
</details>

### Q7. 딕셔너리 키 정렬하여 JSON 저장 (sort_keys)
딕셔너리 `data = {"z": 3, "a": 1, "m": 2}`의 키들을 알파벳 정렬된 상태로 JSON 파일 `"sorted.json"`에 저장하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json
data = {"z": 3, "a": 1, "m": 2}
with open("sorted.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, sort_keys=True)</pre>
</details>

### Q8. 파일 존재 여부 검사를 동반한 안전한 JSON 로딩
`"history.json"` 파일이 디스크에 실제 있을 때만 JSON을 읽고, 없으면 빈 딕셔너리 `{}`를 반환하는 함수를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import os
import json

def load_safety(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}</pre>
</details>

---

<a name="intermediate"></a>
## 2. 중급 문제 (Q9 ~ Q15): 중첩 데이터 갱신, 집계 및 실시간 파일 갱신

### Q9. 중첩 딕셔너리 구조 내 특정 속성 업데이트
중첩 JSON 딕셔너리 `progress = {"Cat1": {"Q1": {"completed": False}}}`가 있을 때, `"Cat1"`의 `"Q1"` 밑에 있는 `"completed"` 속성을 `True`로 변경하고 완료시간 `"date"` 속성에 현재 시각을 문자열로 추가하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from datetime import datetime
progress = {"Cat1": {"Q1": {"completed": False}}}

progress["Cat1"]["Q1"]["completed"] = True
progress["Cat1"]["Q1"]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(progress)</pre>
</details>

### Q10. JSON 데이터 내 완료 개수 합산 및 집계
아래와 같은 학습 진척도 딕셔너리에서 `"completed"`가 `True`인 문제의 총 개수를 구하는 코드를 작성하세요.
```python
data = {
    "Cat1": {
        "Q1": {"completed": True},
        "Q2": {"completed": False},
        "Q3": {"completed": True}
    }
}
```

<details><summary><b>정답 보기</b></summary>
<pre>data = {
    "Cat1": {
        "Q1": {"completed": True},
        "Q2": {"completed": False},
        "Q3": {"completed": True}
    }
}
comp_count = sum(1 for q in data["Cat1"].values() if q["completed"])
print("완료 개수:", comp_count) # 2</pre>
</details>

### Q11. JSON 파일 내용 동적 치환
`"progress.json"` 파일의 내용 중 `"NC0007"` 매장의 진척도 값이 `"complete": false`인 것을 찾아 `"complete": true`로 치환한 뒤 파일에 다시 저장(Overwrite)하는 전체 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json

# 1. 파일 읽기
with open("progress.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. 값 갱신
if "NC0007" in data.get("screens", {}):
    data["screens"]["NC0007"]["complete"] = True

# 3. 다시 쓰기
with open("progress.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)</pre>
</details>

### Q12. 딕셔너리 키 존재 체크 후 신규 삽입
딕셔너리 `data = {"Cat1": {}}`에서 키 `"Q1"`이 존재하는지 확인한 후, 없으면 `"Q1": {"completed": False}`를 삽입하는 코드를 작성하세요. (setdefault 메서드 활용)

<details><summary><b>정답 보기</b></summary>
<pre>data = {"Cat1": {}}
data["Cat1"].setdefault("Q1", {"completed": False})
print(data)</pre>
</details>

### Q13. 특정 JSON 데이터 제거
`"progress.json"` 파일 데이터의 `"screens"` 내부 항목 중 임시 화면 키값인 `"temp_screen_01"`을 찾아 안전하게 제거(`pop` 또는 `del`)하고 파일을 갱신하는 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json

with open("progress.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 안전하게 삭제
if "screens" in data and "temp_screen_01" in data["screens"]:
    data["screens"].pop("temp_screen_01")

with open("progress.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)</pre>
</details>

### Q14. JSON 파일 백업 복구 검증
`"progress.json"`이 만약 문법 오류 등으로 인해 읽기에 실패(`JSONDecodeError`)할 경우, 백업 파일인 `"progress.json.bak"`을 읽어와 복구시키는 예외 처리 구조를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import json

try:
    with open("progress.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    print("메인 파일 로드 실패. 백업본에서 복구합니다.")
    with open("progress.json.bak", "r", encoding="utf-8") as f:
        data = json.load(f)</pre>
</details>

### Q15. datetime 객체가 포함된 딕셔너리 직렬화 오류 대처
`{"update_time": datetime.now()}` 데이터를 `json.dumps()`로 변환하려 할 때 발생하는 TypeError를 우회하기 위해, 날짜 값을 문자열로 미리 변경하여 덤프하는 코드를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>from datetime import datetime
import json

data = {"update_time": datetime.now()}
# 직렬화 전 문자열 포맷 변환
data["update_time"] = data["update_time"].strftime("%Y-%m-%d %H:%M:%S")

json_str = json.dumps(data)
print(json_str)</pre>
</details>

---

<a name="advanced"></a>
## 3. 심화 문제 (Q16 ~ Q20): REST Web API 연동, CORS 및 Fetch AJAX 통신

### Q16. http.server 기반의 POST API 엔드포인트 수신부 구현
파이썬 내장 `http.server.SimpleHTTPRequestHandler` 내에서 `self.path`가 `"/api/update"`일 때, 전송된 POST Body 크기(`Content-Length` 헤더 기준)만큼 바이너리를 읽어 디코딩하는 핵심 `do_POST` 메소드 구조를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import http.server
import json

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/update":
            # 1. 헤더에서 읽어올 바이트 수 획득
            content_length = int(self.headers['Content-Length'])
            # 2. 바디 데이터 수집 및 디코딩 후 json 로드
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode('utf-8'))
            print("전송받은 데이터:", payload)</pre>
</details>

### Q17. CORS 허용 응답 헤더 추가
타 도메인의 브라우저에서 보낸 API 요청에 응답할 수 있도록, Response Header에 CORS 필수 삼총사 헤더(`Access-Control-Allow-Origin: *`, `Methods`, `Headers`)를 설정해 응답을 전송하는 파이썬 코드를 작성하세요.

<details><summary><b>정답 보기</b></summary>
<pre>def send_cors_headers(handler):
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')</pre>
</details>

### Q18. HTTP OPTIONS 사전 요청(Preflight) 핸들링
브라우저가 보안상 본 요청을 보내기 전 안전 여부를 판단하기 위해 보내는 OPTIONS 요청에 대해, HTTP 상태 코드 200번과 CORS 헤더를 보낸 뒤 헤더를 닫는 `do_OPTIONS` 메소드를 구현하세요.

<details><summary><b>정답 보기</b></summary>
<pre>class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()</pre>
</details>

### Q19. JavaScript fetch API 비동기 JSON 전송
웹 페이지에서 `save_data = {"score": 100}` 객체를 `http://localhost:8000/api/update` API 서버로 비동기 POST 전송하는 JavaScript fetch 코드를 완성하세요. (인자는 JSON 문자열로 변환하여 보내고 요청 헤더는 application/json으로 명시하세요.)

<details><summary><b>정답 보기</b></summary>
<pre>&lt;script&gt;
function sendJsonData() {
    const url = "http://localhost:8000/api/update";
    const save_data = { score: 100 };
    
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(save_data) // 직렬화
    })
    .then(response =&gt; response.json())
    .then(result =&gt; console.log("서버 결과:", result))
    .catch(err =&gt; console.error("통신 실패:", err));
}
&lt;/script&gt;</pre>
</details>

### Q20. E2E 종합 통합 문제
다음 E2E 연동 프로세스를 완전히 충족하는 파이썬 웹 API 서버 코드를 구현하세요.
1. 포트 `9000`번에서 대기하는 HTTP 웹 서버를 켭니다.
2. POST `/api/progress` 요청이 들어오면 클라이언트가 보낸 JSON 문자열 `{"cat": "Cat1", "q": "Q5", "done": true}`를 수집 및 파싱합니다.
3. 동일 폴더 내의 `"progress.json"` 파일을 로드한 후, 해당 카테고리와 문제의 완료 여부(`completed`)를 클라이언트가 보낸 데이터 값으로 갱신하여 저장합니다.
4. 성공 결과 메시지 `{"status": "success"}`를 CORS 헤더를 실어서 클라이언트로 응답 반환하세요.

<details><summary><b>정답 보기</b></summary>
<pre>import http.server
import socketserver
import json
import os

PORT = 9000
JSON_PATH = "progress.json"

class ProgressServer(http.server.SimpleHTTPRequestHandler):
    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/progress":
            try:
                # 1. POST 데이터 수집
                length = int(self.headers['Content-Length'])
                raw = self.rfile.read(length)
                payload = json.loads(raw.decode('utf-8'))
                
                cat = payload.get("cat")
                q = payload.get("q")
                done = payload.get("done", False)
                
                # 2. JSON 로드
                if os.path.exists(JSON_PATH):
                    with open(JSON_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = {}
                    
                # 3. 데이터 업데이트
                if cat not in data:
                    data[cat] = {}
                data[cat][q] = {"completed": done}
                
                # 4. 저장
                with open(JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                    
                # 5. 응답
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_cors()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_cors()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ProgressServer) as server:
        print(f"API Server running on port {PORT}")
        server.serve_forever()</pre>
</details>
