path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\master\St_Master_00010_Sql.xml"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "LPLK" in line.upper() or "PLU" in line.upper():
        print(f"{idx+1}: {line.strip()}")
