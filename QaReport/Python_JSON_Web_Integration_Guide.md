# Python & JS 기반 JSON 파일/웹 API 연동 실무 마스터 가이드

본 가이드는 백오피스 시스템 개발자를 위해 **1) 로컬 JSON 파일 제어**, **2) 파이썬 내장 HTTP 웹 서버 API 구축**, **3) 프론트엔드 AJAX(fetch) 통신**까지 데이터가 순환되는 일련의 E2E(End-to-End) 연동 원리를 완벽하게 분석하고 마스터할 수 있도록 돕는 실전 기술 가이드입니다.

---

## 1. E2E 데이터 연동 흐름 아키텍처

우리가 구축한 화면 진척도 관리도 아래와 같은 4단계 데이터 순환 아키텍처를 기반으로 작동합니다.

```text
[프론트엔드 브라우저 (HTML/JS)] 
      │ 
      ├── 1. 체크박스 클릭 / 입력 수정 이벤트 발생
      ├── 2. fetch() API 호출 (Method: POST, Payload: JSON 문자열)
      ▼ 
[파이썬 웹 API 서버 (http.server / Python Backend)]
      │
      ├── 3. POST 요청 수신 및 Header의 Content-Length 파싱
      ├── 4. JSON 수신 바이트 복호화 (decode('utf-8')) 후 dictionary 변환
      ├── 5. 비즈니스 로직 처리 및 파일 입출력 (JSON 쓰기/읽기)
      ▼
[데이터 스토리지 (hms_screens_progress.json)]
      │
      └── 6. 로컬 JSON 파일에 영구 기록 적재 (DB 대용)
```

---

## 2. 1단계: 파이썬 로컬 JSON 파일 제어 (I/O)

파이썬의 표준 라이브러리인 `json` 모듈을 사용하면 딕셔너리(`dict`) 객체와 JSON 텍스트 간의 직렬화 및 역직렬화를 매우 간편하게 다룰 수 있습니다.

### 2.1 JSON 파일 읽기 및 가공
```python
import json
import os

json_file = "progress.json"

# 1. 파일이 있으면 읽어오고, 없으면 기본 딕셔너리로 시작
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)  # 파일 포인터로부터 직접 JSON 로드
else:
    data = {"screens": {}}

# 2. 파이썬 딕셔너리처럼 값 추가 및 수정
data["screens"]["hq_dashboard"] = {
    "complete": True,
    "memo": "정산 마감 로직 연동 완료"
}

# 3. 변경 사항을 파일에 다시 저장 (직렬화)
with open(json_file, "w", encoding="utf-8") as f:
    # indent: 들여쓰기 지정 (가독성 향상)
    # ensure_ascii=False: 한글 깨짐 방지
    json.dump(data, f, indent=4, ensure_ascii=False)
```

---

## 3. 2단계: 파이썬 경량 웹 API 서버 구축

별도의 무거운 프레임워크(Django, Flask 등) 설치 없이 파이썬 기본 표준 라이브러리인 `http.server` 모듈만으로도 RESTful API 서비스를 제공하는 경량 웹 서버를 빌드할 수 있습니다.

### 3.1 HTTP POST API 핸들러 구현 코드
```python
import http.server
import socketserver
import json

PORT = 8000

class MyApiHandler(http.server.SimpleHTTPRequestHandler):
    
    # CORS (Cross-Origin Resource Sharing) 허용 응답 헤더 공통 유틸리티
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*') # 모든 도메인 접속 허용
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    # 프론트엔드가 POST 요청을 보내기 전 안전 여부를 묻는 사전 요청(Preflight) 처리
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    # 실제 데이터 저장 처리 POST 핸들러
    def do_POST(self):
        if self.path == "/api/save":
            try:
                # 1. HTTP 요청 바디 크기 획득
                content_length = int(self.headers['Content-Length'])
                
                # 2. 바디 영역 바이너리 읽기 및 디코딩 후 딕셔너리 변환
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode('utf-8'))
                
                # 3. 비즈니스 데이터 처리
                file_key = payload.get("file_key")
                complete = payload.get("complete", False)
                print(f"[API SERVER] 요청 감지 - 키: {file_key}, 완료: {complete}")
                
                # [여기에 파일 저장/DB 인서트 로직 연동]
                
                # 4. 성공 응답 전송
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                
                response_json = json.dumps({"status": "success", "message": "저장 완료"})
                self.wfile.write(response_json.encode('utf-8'))
                
            except Exception as e:
                # 에러 발생 시 500 내부 서버 에러 반환
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                
                err_json = json.dumps({"status": "error", "message": str(e)})
                self.wfile.write(err_json.encode('utf-8'))

# API 서버 시작 실행부
if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), MyApiHandler) as httpd:
        print(f"[API 서버 구동 중] http://localhost:{PORT}")
        httpd.serve_forever()
```

---

## 4. 3단계: 프론트엔드 브라우저 비동기(AJAX) 통신

HTML 페이지 내에서 jQuery 또는 최신 표준 비동기 API인 `fetch`를 사용하여 파이썬 API 서버에 비동기 데이터 전송을 수행합니다.

### 4.1 JavaScript Fetch API 활용 예제
```html
<button id="save-btn" onclick="saveProgress('hq_dashboard', true)">저장하기</button>

<script>
function saveProgress(fileKey, isComplete) {
    const serverUrl = "http://localhost:8000/api/save";
    
    // 1. 서버로 보낼 JSON 페이로드 객체 정의
    const payload = {
        file_key: fileKey,
        complete: isComplete,
        memo: "대시보드에서 체크됨"
    };

    // 2. 비동기 HTTP POST 호출 실행
    fetch(serverUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload) // 딕셔너리를 JSON 문자열로 직렬화하여 패싱
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("서버 응답 오류");
        }
        return response.json();
    })
    .then(data => {
        if (data.status === "success") {
            alert("학습 진도가 성공적으로 저장되었습니다!");
            // 화면 UI 갱신 등 추가 액션
        } else {
            alert("저장 중 오류 발생: " + data.message);
        }
    })
    .catch(error => {
        console.error("통신 실패:", error);
        alert("API 서버가 켜져 있는지 확인해 주세요.");
    });
}
</script>
```

---

## 5. 실무 마스터 핵심 체크 리스트

1. **포트 충돌 해결 (`Address already in use`)**:
   * 서버 소켓이 닫힐 때 포트가 커널에 점유된 상태가 유지될 수 있습니다. `socketserver.TCPServer.allow_reuse_address = True` 옵션을 주어 즉시 바인딩을 허용하세요.
2. **CORS 에러 발생 대처**:
   * 브라우저 도메인(예: `localhost:8080` 또는 파일 실행 주소)과 파이썬 API 서버 도메인(`localhost:8000`)의 포트가 다르면 보안 거부(CORS)가 일어납니다. 반드시 API 서버 헤더에 `Access-Control-Allow-Origin: *`을 실어 돌려주어야 합니다.
3. **요청 바디 수집 주의점**:
   * 파이썬 `http.server`는 데이터의 끝을 자동으로 인식하지 못하므로, 수신 헤더 내의 `Content-Length` 값을 토대로 읽을 바이트 수를 정확히 지정하여 `self.rfile.read(length)` 해야 대기 정체 현상 없이 정상 작동합니다.
