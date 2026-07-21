with open(r"D:\hmTest\backoffice\QaReport\update_memos_json.py", "r", encoding="utf-8") as f:
    content = f.read()

for i, line in enumerate(content.split("\n")):
    if "strn" in line.lower():
        print(f"Line {i+1}: {line.strip()}")
