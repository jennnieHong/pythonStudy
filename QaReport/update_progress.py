import sys
import os
import json
from datetime import datetime

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
        "Excel": "부록: 파이썬 엑셀(Excel) 핸들링 (45제)",
        "CmdCat1": "터미널 검색: Windows CMD findstr (50제)",
        "CmdCat2": "터미널 검색: Windows PowerShell Select-String (50제)",
        "CmdCat3": "터미널 검색: Linux/Unix grep & 로그 검색 (50제)"
    }
    
    total_q = 0
    total_c = 0
    stats = {}
    
    for cat, qs in data.items():
        if cat not in cat_names:
            continue
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
    
    md = []
    md.append("# 📊 파이썬 & 터미널 검색 학습 진척도 대시보드")
    md.append(f"\n*최종 갱신 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Overall Progress Bar
    bar_width = 30
    filled = int(round((overall_pct / 100) * bar_width))
    bar = "█" * filled + "░" * (bar_width - filled)
    
    md.append("\n## 📈 전체 학습 진척률")
    md.append(f"**전체 완료:** `{total_c}` / `{total_q}` 문항")
    md.append(f"\n`[{bar}] {overall_pct}%` 완료\n")
    
    # Category Table
    md.append("## 📁 카테고리별 세부 진척 현황\n")
    md.append("| 카테고리 | 완료 문항수 | 진척률 | 진행 바 |")
    md.append("| :--- | :---: | :---: | :--- |")
    
    for cat, name in cat_names.items():
        s = stats.get(cat, {"completed": 0, "total": 0, "pct": 0.0})
        cat_bar_width = 15
        cat_filled = int(round((s["pct"] / 100) * cat_bar_width))
        cat_bar = "█" * cat_filled + "░" * (cat_bar_width - cat_filled)
        
        if cat.startswith("Cat"):
            file_link = f"./Python_Exercise_Book_{cat}.md"
        elif cat == "Excel":
            file_link = "./Python_Excel_Exercise_Book.md"
        elif cat.startswith("CmdCat"):
            file_link = f"./CMD_Search_Exercise_Book_{cat}.md"
        else:
            file_link = "#"
            
        md.append(f"| [{name}]({file_link}) | `{s['completed']}` / `{s['total']}` | **{s['pct']}%** | `[{cat_bar}]` |")
        
    md.append("\n## 📝 세부 문항별 완료 현황 (클릭 시 펼치기)\n")
    
    for cat, name in cat_names.items():
        if cat not in data:
            continue
        qs = data[cat]
        md.append(f"<details><summary><b>🔍 {name} - 자세히 보기</b></summary>\n")
        
        md.append("| " + " | ".join(f"Col {col+1}" for col in range(10)) + " |")
        md.append("|" + "|".join(":---:" for _ in range(10)) + "|")
        
        row_items = []
        sorted_qs = sorted(qs.keys(), key=lambda x: int(x[1:]))
        
        for q_key in sorted_qs:
            completed = qs[q_key]["completed"]
            box = "✅" if completed else "⬜"
            
            if cat.startswith("Cat"):
                fname = f"Python_Exercise_Book_{cat}.md"
            elif cat == "Excel":
                fname = "Python_Excel_Exercise_Book.md"
            elif cat.startswith("CmdCat"):
                fname = f"CMD_Search_Exercise_Book_{cat}.md"
            else:
                fname = ""
                
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
        
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

def update_status(json_path, md_path, cat, q_num, completed):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if cat not in data:
        print(f"Error: Category not found ({cat})")
        return False
        
    if q_num not in data[cat]:
        print(f"Error: Question not found ({q_num})")
        return False
        
    data[cat][q_num]["completed"] = completed
    data[cat][q_num]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if completed else ""
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    generate_progress_md(json_path, md_path)
    
    status_text = "Completed" if completed else "Todo"
    print(f"Success: [{cat}] {q_num} status updated to -> {status_text}")
    print("Dashboard (Python_Learning_Progress.md) updated.")
    return True

def run_interactive_mode(json_path, md_path):
    print("==================================================")
    print("  HMS Study Progress Tracker (Interactive)  ")
    print("==================================================")
    print("Category Menu:")
    print("  [1] Cat1 - Basic Grammar & Variables")
    print("  [2] Cat2 - Conditionals & Loops")
    print("  [3] Cat3 - Data Structures")
    print("  [4] Cat4 - Functions & Lambda")
    print("  [5] Cat5 - Classes & OOP")
    print("  [6] Cat6 - Exceptions & File I/O")
    print("  [7] Cat7 - Standard Libs & DB Integration")
    print("  [8] Excel - Excel Handling")
    print("  [9] CmdCat1 - Windows CMD findstr")
    print("  [10] CmdCat2 - Windows PowerShell")
    print("  [11] CmdCat3 - Linux/Unix grep log")
    
    while True:
        try:
            choice = input("\nSelect Category (Number or Code, Exit: q): ").strip()
            if choice.lower() in ["q", "exit", "quit"]:
                print("Exiting progress manager.")
                break
                
            cat_map = {
                "1": "Cat1", "2": "Cat2", "3": "Cat3", "4": "Cat4",
                "5": "Cat5", "6": "Cat6", "7": "Cat7", "8": "Excel",
                "9": "CmdCat1", "10": "CmdCat2", "11": "CmdCat3",
                "cat1": "Cat1", "cat2": "Cat2", "cat3": "Cat3", "cat4": "Cat4",
                "cat5": "Cat5", "cat6": "Cat6", "cat7": "Cat7", "excel": "Excel",
                "cmdcat1": "CmdCat1", "cmdcat2": "CmdCat2", "cmdcat3": "CmdCat3"
            }
            
            cat = cat_map.get(choice.lower())
            if not cat:
                print("Invalid selection. Try again.")
                continue
                
            q_num_input = input("Enter Question Number (e.g. 5, 23): ").strip()
            if not q_num_input.isdigit():
                print("Question number must be digits.")
                continue
                
            q_num = f"Q{q_num_input}"
            
            status_input = input("Have you completed this? (y/n): ").strip().lower()
            completed = status_input in ["y", "yes", "true", "t", "1"]
            
            update_status(json_path, md_path, cat, q_num, completed)
            
        except KeyboardInterrupt:
            print("\nCancelled.")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    json_path = os.path.join(os.path.dirname(__file__), "python_learning_progress.json")
    md_path = os.path.join(os.path.dirname(__file__), "Python_Learning_Progress.md")
    
    if not os.path.exists(json_path):
        print("Error: python_learning_progress.json not found.")
        return
        
    if len(sys.argv) < 2:
        run_interactive_mode(json_path, md_path)
        return
        
    if len(sys.argv) < 4:
        print("Usage (CLI): python update_progress.py [Category] [QuestionNumber] [True/False]")
        print("Usage (Interactive): python update_progress.py")
        return
        
    cat = sys.argv[1]
    q_num = sys.argv[2]
    status_str = sys.argv[3].lower()
    
    completed = status_str in ["true", "t", "y", "yes", "1"]
    update_status(json_path, md_path, cat, q_num, completed)

if __name__ == "__main__":
    main()
