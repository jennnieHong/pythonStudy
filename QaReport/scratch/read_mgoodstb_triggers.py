import glob
import os

trigger_sql_files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\*.sql")

for path in trigger_sql_files:
    fname = os.path.basename(path)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    print(f"=== Trigger: {fname} ===")
    # Print first 60 lines
    for line in lines[:80]:
        print(line.rstrip())
    print("\n")
