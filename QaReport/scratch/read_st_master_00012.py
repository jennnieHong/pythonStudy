path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\master\St_Master_00012_Sql.xml"

try:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    print("=== St_Master_00012 ===")
    print(content[:2000])
except Exception as e:
    print(f"Error: {e}")
