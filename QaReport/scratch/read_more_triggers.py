import os

files = [
    r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\OBSLPD_T01.sql",
    r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\STRNDT_T01.sql",
    r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\MGMVHD_T01.sql",
]

for path in files:
    if os.path.exists(path):
        print(f"=== File: {os.path.basename(path)} ===")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        print(content[:1500])
        print("\n" + "="*50 + "\n")
    else:
        print(f"Not found: {path}")
