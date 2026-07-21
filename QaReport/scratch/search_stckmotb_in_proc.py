path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\procedure\SUB_STOCK_FIFO_PROC_P.sql"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "STCKMOTB" in line.upper():
        print(f"--- Line {i+1} ---")
        start = max(0, i - 15)
        end = min(len(lines), i + 20)
        for j in range(start, end):
            print(f"{j+1}: {lines[j]}", end="")
