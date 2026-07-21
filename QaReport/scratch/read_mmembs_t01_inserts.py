path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\MMEMBS_T01.sql"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

lines = content.split("\n")
print("=== SQL statements in MMEMBS_T01 ===")
for line in lines:
    upper_line = line.upper().strip()
    if any(keyword in upper_line for keyword in ["INSERT INTO", "UPDATE ", "DELETE FROM", "MERGE INTO"]):
        print(line.strip())
