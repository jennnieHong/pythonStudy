with open(r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\STRNDT_T01.sql", "r", encoding="utf-8", errors="ignore") as f:
    strndt = f.read()

with open(r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\OBSLPD_T01.sql", "r", encoding="utf-8", errors="ignore") as f:
    obslpd = f.read()

with open(r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\MGMVHD_T01.sql", "r", encoding="utf-8", errors="ignore") as f:
    mgmvhd = f.read()

print("=== STRNDT_T01 MGOODSTB lines ===")
for line in strndt.split("\n"):
    if "MGOODS" in line.upper():
        print(line.strip())

print("\n=== OBSLPD_T01 MGOODSTB lines ===")
for line in obslpd.split("\n"):
    if "MGOODS" in line.upper():
        print(line.strip())

print("\n=== MGMVHD_T01 MGOODSTB lines ===")
for line in mgmvhd.split("\n"):
    if "MGOODS" in line.upper():
        print(line.strip())
