path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\STRNDT_T01.sql"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print("=== STRNDT_T01 Full ===")
print(content[:3000]) # Print first 3000 chars of trigger
