path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\MMEMBS_T01.sql"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

lines = content.split("\n")
for i, line in enumerate(lines):
    if "MUSERSTB" in line.upper():
        print(f"--- Line {i+1} ---")
        start = max(0, i-3)
        end = min(len(lines), i+8)
        for j in range(start, end):
            print(f"{j+1}: {lines[j]}")
