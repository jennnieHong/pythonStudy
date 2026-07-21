mprice_path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\MPRICE_T01.sql"
tprice_path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\TPRICE_T01.sql"

def analyze_insert(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    print(f"=== Insert statements in {os.path.basename(path)} ===")
    for i, line in enumerate(lines):
        if "MPRILGTB" in line.upper():
            print(f"--- Line {i+1} ---")
            start = max(0, i-5)
            end = min(len(lines), i+15)
            for j in range(start, end):
                print(f"{j+1}: {lines[j].rstrip()}")
            print("\n" + "="*40 + "\n")

import os
analyze_insert(mprice_path)
analyze_insert(tprice_path)
