path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\MMCPLU_T01.sql"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print("=== MMCPLU_T01 Trigger ===")
print(content[:2000])
if len(content) > 2000:
    print(content[2000:4000])
