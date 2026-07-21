path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sqlmapper\trigger\Tr_MNAMEM_T01_Sql.xml"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print("=== Tr_MNAMEM_T01_Sql.xml ===")
print(content[:2000])
