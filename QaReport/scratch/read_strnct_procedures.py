p1 = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\trigger\STRNCT_T01.sql"
p2 = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\procedure\SUB_STRNCT_P.sql"

try:
    with open(p1, "r", encoding="utf-8", errors="ignore") as f:
        print("=== STRNCT_T01 Trigger ===")
        print(f.read()[:1500])
except Exception as e:
    print(f"Error p1: {e}")

try:
    with open(p2, "r", encoding="utf-8", errors="ignore") as f:
        print("=== SUB_STRNCT_P Procedure ===")
        print(f.read()[:1500])
except Exception as e:
    print(f"Error p2: {e}")
