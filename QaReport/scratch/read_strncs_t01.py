path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\STRNCS_T01.sql"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print("=== STRNCS_T01 Trigger ===")
print(content[:2000])
