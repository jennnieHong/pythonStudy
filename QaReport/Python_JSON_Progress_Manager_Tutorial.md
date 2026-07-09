# Python & Web API 기반 학습 진도 관리 시스템 구축 A to Z 풀 튜토리얼

> [!NOTE]
> **초보자를 위한 핵심 웹/API 기본 개념 사전**
> 
> * **JSON (JavaScript Object Notation)**: 데이터를 키와 값의 쌍(예: `{"이름": "개발자"}`)으로 저장하는 표준 텍스트 포맷입니다. 자바의 `Map<String, Object>`과 매우 유사하며, 모든 프로그래밍 언어에서 공통으로 인식 가능합니다.
> * **웹 API (Application Programming Interface)**: 브라우저가 특정 주소(예: `/api/save`)로 데이터를 던지면 백엔드 서버가 이를 접수해 처리해주는 통신 약속 창구입니다.
> * **포트 (Port)**: 서버 프로그램이 열어두는 통신 통로 번호입니다. 본 실습에서는 파이썬 서버가 `9000`번 포트를 점유하여 대기합니다.
> * **CORS (Cross-Origin Resource Sharing)**: 브라우저에서 실행된 HTML 파일(도메인이 없거나 포트가 없음)이 9000번 포트로 데이터를 보내려 할 때, 브라우저 보안 필터가 해킹으로 간주해 통신을 차단하는 현상입니다. 이를 막기 위해 파이썬 서버 헤더에 "허용하겠다(`Access-Control-Allow-Origin: *`)"는 선언을 넣어주어야 합니다.
> * **비동기 fetch()**: 브라우저 화면 전체를 새로고침(F5)하지 않고, 백그라운드 상에서 서버와 조용히 데이터를 주고받아 화면의 일부 색상이나 텍스트만 실시간으로 갈아끼우는 브라우저 내장 자바스크립트 함수입니다.

---

본 튜토리얼은 **로컬 JSON 데이터베이스 설계부터 파이썬 스크립트 코딩, 마크다운 대시보드 자동 빌드, 경량 REST API 서버 구축 및 웹 브라우저 프론트엔드 연동**까지, 학습 진도 관리 프로그램을 바닥(A)부터 완성(Z)까지 누락 없이 직접 만들 수 있도록 친절히 설명하는 종합 실무 교육 문서입니다.

---

## 1. [A단계] 데이터베이스 설계: `python_learning_progress.json`

가장 먼저 학습 상태를 영구 저장할 JSON 데이터베이스 구조를 정의합니다.
* **Cat1~Cat7**: 7대 기본 카테고리. 각 카테고리 내부에는 `Q1`부터 `Q100`까지의 문제 키를 생성합니다.
* **Excel**: 부록 카테고리. `Q1`부터 `Q45`까지의 키를 가집니다.
* **completed**: `true`(완료) / `false`(미완료) Boolean 값.
* **date**: 완료 처리된 시점의 타임스탬프 문자열 (예: `"2026-07-06 18:30:00"`).

### 1.1 초기화 파일 자동 생성 스크립트 (`init_db.py`)
이 스크립트를 최초 한 번 실행하면 745문항 전체가 `"completed": false`로 세팅된 깨끗한 JSON 파일이 물리 생성됩니다.

```python
# 파일명: init_db.py
import json

def initialize_database():
    progress_db = {}

    # 1. 7개 카테고리 생성 (각 100문제)
    for i in range(1, 8):
        cat_key = f"Cat{i}"
        progress_db[cat_key] = {}
        for q in range(1, 101):
            progress_db[cat_key][f"Q{q}"] = {
                "completed": False,
                "date": ""
            }

    # 2. 엑셀 카테고리 생성 (45문제)
    progress_db["Excel"] = {}
    for q in range(1, 46):
        progress_db["Excel"][f"Q{q}"] = {
            "completed": False,
            "date": ""
        }

    # 3. JSON 파일로 디스크 쓰기
    with open("python_learning_progress.json", "w", encoding="utf-8") as f:
        # indent=2: 들여쓰기 2칸, ensure_ascii=False: 한글 유니코드 깨짐 방지
        json.dump(progress_db, f, indent=2, ensure_ascii=False)

    print("성공: python_learning_progress.json 초기화 완료!")

if __name__ == "__main__":
    initialize_database()
```

---

## 2. [B단계] 상태 제어 스크립트 코딩: `update_progress.py`

사용자가 터미널에서 특정 문제를 완료했음을 알리는 명령어(CLI)를 가동할 때 백엔드 처리를 담당하는 핵심 스크립트입니다.

### 2.1 주요 기능 메커니즘
1. 로컬 `python_learning_progress.json` 파일이 있는지 확인 후 오픈(`json.load`).
2. 입력받은 카테고리(예: `Cat1`) 및 문제 번호(예: `Q5`)가 실제로 유효한 키인지 검증.
3. 해당 키의 값을 사용자 요청대로 변경하고 완료 시 시간 기록(`datetime.now()`).
4. 변경 사항을 파일에 다시 저장(`json.dump`).
5. **비주얼 대시보드 마크다운 파일(`Python_Learning_Progress.md`)**을 실시간 재생성하는 메소드를 자동 호출.

### 2.2 전체 소스코드 (`update_progress.py`)
```python
# 파일명: update_progress.py
import sys
import os
import json
from datetime import datetime

# 3단계에서 구현할 마크다운 빌드 함수를 결합합니다.
def generate_progress_md(json_path, md_path):
    if not os.path.exists(json_path):
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    cat_names = {
        "Cat1": "기초 문법 및 변수 (100제)",
        "Cat2": "조건문과 반복문 (100제)",
        "Cat3": "자료구조 (리스트, 튜플, 딕셔너리, 세트) (100제)",
        "Cat4": "함수 및 람다 (100제)",
        "Cat5": "클래스와 객체 지향 (100제)",
        "Cat6": "예외 처리 및 파일 입출력 (100제)",
        "Cat7": "실무 라이브러리 및 정규식, DB 연동 (100제)",
        "Excel": "부록: 파이썬 엑셀(Excel) 핸들링 (45제)"
    }
    
    total_q = 0
    total_c = 0
    stats = {}
    
    # 1. 수치 데이터 집계 연산
    for cat, qs in data.items():
        cat_total = len(qs)
        cat_comp = sum(1 for q in qs.values() if q["completed"])
        stats[cat] = {
            "total": cat_total,
            "completed": cat_comp,
            "pct": round((cat_comp / cat_total) * 100, 1) if cat_total > 0 else 0.0
        }
        total_q += cat_total
        total_c += cat_comp
        
    overall_pct = round((total_c / total_q) * 100, 1) if total_q > 0 else 0.0
    
    # 2. 마크다운 문자열 조립
    md = []
    md.append("# 📊 파이썬 학습 진척도 대시보드")
    md.append(f"\n*최종 갱신 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # 전체 진행 바 드로잉 (30글자 척도)
    bar_width = 30
    filled = int(round((overall_pct / 100) * bar_width))
    bar = "█" * filled + "░" * (bar_width - filled)
    
    md.append("\n## 📈 전체 학습 진척률")
    md.append(f"**전체 완료:** `{total_c}` / `{total_q}` 문항")
    md.append(f"\n`[{bar}] {overall_pct}%` 완료\n")
    
    # 카테고리 테이블 빌드
    md.append("## 📁 카테고리별 세부 진척 현황\n")
    md.append("| 카테고리 | 완료 문항수 | 진척률 | 진행 바 |")
    md.append("| :--- | :---: | :---: | :--- |")
    
    for cat, name in cat_names.items():
        s = stats[cat]
        cat_bar_width = 15
        cat_filled = int(round((s["pct"] / 100) * cat_bar_width))
        cat_bar = "█" * cat_filled + "░" * (cat_bar_width - cat_filled)
        
        file_link = f"./Python_Exercise_Book_{cat}.md" if cat.startswith("Cat") else "./Python_Excel_Exercise_Book.md"
        md.append(f"| [{name}]({file_link}) | `{s['completed']}` / `{s['total']}` | **{s['pct']}%** | `[{cat_bar}]` |")
        
    md.append("\n## 📝 세부 문항별 완료 현황 (클릭 시 펼치기)\n")
    
    # 각 카테고리별 아코디언 드롭다운 그리드 그리기
    for cat, name in cat_names.items():
        qs = data[cat]
        md.append(f"<details><summary><b>🔍 {name} - 자세히 보기</b></summary>\n")
        
        # 10열 그리드 헤더 정의
        md.append("| " + " | ".join(f"Col {col+1}" for col in range(10)) + " |")
        md.append("|" + "|".join(":---:" for _ in range(10)) + "|")
        
        row_items = []
        sorted_qs = sorted(qs.keys(), key=lambda x: int(x[1:]))
        
        for q_key in sorted_qs:
            completed = qs[q_key]["completed"]
            box = "✅" if completed else "⬜"
            fname = f"Python_Exercise_Book_{cat}.md" if cat.startswith("Cat") else "Python_Excel_Exercise_Book.md"
            anchor = q_key.lower()
            
            row_items.append(f"[{box} {q_key}](./{fname}#{anchor})")
            
            if len(row_items) == 10:
                md.append("| " + " | ".join(row_items) + " |")
                row_items = []
                
        if row_items:
            while len(row_items) < 10:
                row_items.append("")
            md.append("| " + " | ".join(row_items) + " |")
            
        md.append("\n</details>\n")
        
    # 물리적 마크다운 파일 쓰기
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

# CLI 인수 기반 실행 및 갱신 비즈니스 로직
def main():
    json_path = "python_learning_progress.json"
    md_path = "Python_Learning_Progress.md"
    
    if not os.path.exists(json_path):
        print("에러: python_learning_progress.json 파일이 존재하지 않습니다. 먼저 init_db.py를 실행하세요.")
        return
        
    if len(sys.argv) < 4:
        print("사용법: python update_progress.py [카테고리] [문제코드] [True/False]")
        print("예시: python update_progress.py Cat1 Q5 True")
        return
        
    cat = sys.argv[1]
    q_num = sys.argv[2]
    status_str = sys.argv[3].lower()
    completed = status_str in ["true", "t", "y", "yes", "1"]
    
    # 1. 파일 오픈 로드
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 2. 키값 검증
    if cat not in data:
        print(f"오류: 존재하지 않는 카테고리명 ({cat})")
        return
    if q_num not in data[cat]:
        print(f"오류: 존재하지 않는 문제 코드 ({q_num})")
        return
        
    # 3. 데이터 갱신
    data[cat][q_num]["completed"] = completed
    data[cat][q_num]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if completed else ""
    
    # 4. 파일 쓰기
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    # 5. 비주얼 대시보드 마크다운 생성 호출
    generate_progress_md(json_path, md_path)
    print(f"성공: [{cat}] {q_num} 상태 변경 -> {completed}. 대시보드가 성공적으로 리프레시되었습니다!")

if __name__ == "__main__":
    main()
```

---

## 3. [C단계] 웹 서버 연동: 파이썬 REST API 서버 (`progress_server.py`)

로컬 PC의 명령창이 아닌, 웹 브라우저상의 대화형 화면에서 체크박스를 조작할 때 비동기 통신을 접수하고 디스크의 JSON에 저장해주는 소형 API 웹 서버입니다.

### 3.1 주요 기능 메커니즘
1. **OPTIONS 처리**: 브라우저의 사전 CORS 유효검사에 200 통과 응답 전송.
2. **POST 수신**: `/api/save_progress` 주소로 전송된 JSON 텍스트 수신 및 바이트 복호화.
3. **업데이트 및 재생성**: `update_progress.py` 핵심 업데이트 로직을 호출하여 JSON 업데이트 및 `Python_Learning_Progress.md` 빌드.
4. **성공 JSON 반환**: 클라이언트에 `{"status": "success"}`를 반환하여 화면 단에서 즉시 체크마크 완료 색상이 활성화되도록 유도.

### 3.2 전체 소스코드 (`progress_server.py`)
```python
# 파일명: progress_server.py
import http.server
import socketserver
import json
import os
from datetime import datetime

# 앞서 작성한 B단계 마크다운 자동 갱신 함수 임포트
from update_progress import generate_progress_md

PORT = 9000
JSON_FILE = "python_learning_progress.json"
MD_FILE = "Python_Learning_Progress.md"

class ProgressApiHandler(http.server.SimpleHTTPRequestHandler):
    
    # 1. CORS(Cross-Origin Resource Sharing) 허용 공통 헤더
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')  # 브라우저 포트 달라도 호출 가능
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    # 2. CORS 사전 검증(OPTIONS) 응답
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    # 3. 비동기 저장 요청(POST) 접수 처리
    def do_POST(self):
        if self.path == "/api/save_progress":
            try:
                # HTTP 바디의 크기만큼 정확하게 바이트 수집 (정체 현상 예방)
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # 수신 텍스트 UTF-8 복호화 후 파이썬 딕셔너리로 언패킹
                payload = json.loads(post_data.decode('utf-8'))
                
                cat = payload.get("cat")        # 예: Cat1
                q_num = payload.get("q_num")    # 예: Q5
                completed = payload.get("completed", False)
                
                # JSON 로드
                if not os.path.exists(JSON_FILE):
                    raise FileNotFoundError("DB 파일이 없습니다.")
                    
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    db = json.load(f)
                    
                # 갱신 처리
                if cat in db and q_num in db[cat]:
                    db[cat][q_num]["completed"] = completed
                    db[cat][q_num]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if completed else ""
                    
                # JSON 저장
                with open(JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)
                    
                # 비주얼 마크다운 대시보드 파일 재생성
                generate_progress_md(JSON_FILE, MD_FILE)
                
                # 브라우저로 최종 성공 응답 반환
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                print(f"[API SERVER] 갱신 성공 - {cat} {q_num} -> {completed}")
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ProgressApiHandler) as httpd:
        print(f"🚀 [API SERVER] 포트 {PORT}에서 정상 구동 중...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[API SERVER] 서버가 안전하게 종료되었습니다.")
```

---

## 4. [D단계] 프론트엔드 연동: 인터랙티브 웹 대시보드 (`Dashboard.html`)

마크다운 뷰어를 넘어서, 사용자가 브라우저에서 직접 예쁘게 렌더링된 그리드의 체크박스들을 보며 클릭하면 즉각 파이썬 백엔드로 전송 저장되는 반응형 단일 페이지 애플리케이션(SPA)입니다.

### 4.1 전체 소스코드 (`Dashboard.html`)
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>파이썬 학습 진도 인터랙티브 대시보드</title>
    <style>
        body {
            font-family: '맑은 고딕', sans-serif;
            background-color: #f5f7fa;
            color: #333;
            margin: 40px;
        }
        h1 {
            color: #1f4e78;
            border-bottom: 3px solid #1f4e78;
            padding-bottom: 10px;
        }
        .section {
            background-color: #fff;
            padding: 20px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(10, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .q-card {
            background-color: #f1f3f5;
            padding: 10px;
            text-align: center;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s ease;
            user-select: none;
            border: 1px solid #dee2e6;
        }
        .q-card:hover {
            background-color: #e9ecef;
            transform: translateY(-2px);
        }
        .q-card.completed {
            background-color: #2b8a3e;
            color: #fff;
            border-color: #2b8a3e;
        }
        .q-card.completed:hover {
            background-color: #237032;
        }
        .cat-title {
            font-size: 1.2em;
            color: #495057;
            margin-bottom: 5px;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <h1>📊 HMS 파이썬 학습 진도 인터랙티브 대시보드</h1>
    <p>클릭하여 각 문항의 완료 상태를 바로 토글하고 보관할 수 있습니다. (로컬 API 서버 작동 필요)</p>

    <!-- 카테고리 1 영역 -->
    <div class="section">
        <div class="cat-title">📁 카테고리 1: 기초 문법 및 변수 (100제)</div>
        <div class="grid-container" id="cat1-grid"></div>
    </div>

    <!-- 엑셀 부록 영역 -->
    <div class="section">
        <div class="cat-title">📊 부록: 파이썬 엑셀(Excel) 핸들링 (45제)</div>
        <div class="grid-container" id="excel-grid"></div>
    </div>

    <script>
        const API_URL = "http://localhost:9000/api/save_progress";

        // 화면 로딩 시 그리드 생성기
        function buildGrid(gridId, catKey, count) {
            const grid = document.getElementById(gridId);
            for (let i = 1; i <= count; i++) {
                const qNum = "Q" + i;
                const card = document.createElement("div");
                card.className = "q-card";
                card.id = `${catKey}-${qNum}`;
                card.innerText = qNum;
                
                // 클릭 시 백엔드 API 연동 함수 연결
                card.onclick = () => toggleQuestion(catKey, qNum, card);
                
                grid.appendChild(card);
            }
        }

        // 비동기 API 통신 및 토글 갱신 비즈니스 함수
        function toggleQuestion(catKey, qNum, element) {
            // 현재 활성 색상 상태 확인을 통해 반전값 설정
            const isCompleted = element.classList.contains("completed");
            const targetStatus = !isCompleted;

            const payload = {
                cat: catKey,
                q_num: qNum,
                completed: targetStatus
            };

            // Fetch POST 전송
            fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            })
            .then(res => {
                if (!res.ok) throw new Error("서버 응답 거부");
                return res.json();
            })
            .then(data => {
                if (data.status === "success") {
                    // 성공 시 UI 색상 클래스 토글 적용
                    if (targetStatus) {
                        element.classList.add("completed");
                    } else {
                        element.classList.remove("completed");
                    }
                } else {
                    alert("저장 실패: " + data.message);
                }
            })
            .catch(err => {
                console.error("통신 에러:", err);
                alert("API 서버가 켜져 있는지 확인하세요. (python progress_server.py 구동 필요)");
            });
        }

        // 페이지 기동 시 초기화
        window.onload = () => {
            // 카테고리 1 (100문항) 및 엑셀 (45문항) 그리드 렌더링
            buildGrid("cat1-grid", "Cat1", 100);
            buildGrid("excel-grid", "Excel", 45);

            // [추가 확장 기능]: 필요시 서버로부터 현재 저장상태를 GET 호출하여 
            // 완성 상태인 요소들에 .completed 클래스를 기동 시점에 일괄 추가(classList.add)해 줄 수 있습니다.
        };
    </script>
</body>
</html>
```

---

## 5. [E단계] 최종 실행 및 운영 시나리오

개발이 끝난 후 전체 시스템을 구동시키는 실무 순서입니다.

1. **DB 파일 최초 초기화**:
   ```bash
   python init_db.py
   ```
   * 실행 결과 폴더 내에 `python_learning_progress.json` 파일이 물리 생성됩니다.
2. **웹 API 백엔드 서버 기동**:
   ```bash
   python progress_server.py
   ```
   * 서버가 포트 `9000`번을 열고 데이터 수신 대기 상태에 들어갑니다.
3. **HTML 브라우저 화면 연동**:
   * 브라우저에서 `Dashboard.html` 파일을 더블 클릭하여 엽니다.
   * 그리드 속 버튼들을 클릭하면 포트 `9000`의 파이썬 백엔드로 비동기 `fetch` 요청이 실시간 전달됩니다.
   * 백엔드는 JSON을 갱신하고 동시에 `Python_Learning_Progress.md` 비주얼 마크다운 파일을 재생성합니다.
   * 마크다운 뷰어에 들어가서 새로고침하시면 진행 상태 바와 체크박스가 아름답게 즉시 동기화되어 있음을 볼 수 있습니다.
