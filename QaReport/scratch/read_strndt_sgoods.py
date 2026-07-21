path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\STRNDT_T01.sql"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

lines = content.split("\n")
print("=== STRNDT_T01 lines containing SGOODS ===")
for i, line in enumerate(lines):
    if "SGOODS" in line.upper() or "SUB_SGOODS_P" in line.upper():
        print(f"--- Line {i+1} ---")
        start = max(0, i-5)
        end = min(len(lines), i+15)
        for j in range(start, end):
            print(f"{j+1}: {lines[j].rstrip()}")
        print("\n" + "="*40 + "\n")
