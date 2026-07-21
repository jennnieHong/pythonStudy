path = r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-api\src\main\resources\sql\procedure\SUB_STOCK_FIFO_ERR_P.sql"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print("=== SUB_STOCK_FIFO_ERR_P Procedure ===")
print(content[:2000])
if len(content) > 2000:
    print(content[2000:4000])
