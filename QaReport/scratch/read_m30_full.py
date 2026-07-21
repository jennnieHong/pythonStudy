path = r"d:\workspace\hmotors\workspace_hms20260326\telex\src\main\resources\sqlmapper\M30_SqlMapper.xml"

try:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    print("=== M30_SqlMapper full ===")
    print(content)
except Exception as e:
    print(f"Error: {e}")
