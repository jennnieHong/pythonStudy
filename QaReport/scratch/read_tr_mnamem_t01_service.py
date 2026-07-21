path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\java\com\hyundai\api\service\trigger\Tr_MNAMEM_T01_Service.java"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print("=== Tr_MNAMEM_T01_Service.java ===")
print(content[:2000])
if len(content) > 2000:
    print(content[2000:4000])
