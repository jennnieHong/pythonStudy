path = r"d:\workspace\hmotors\workspace_hms20260326\telex\src\main\resources\sqlmapper\M45_SqlMapper.xml"

try:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    print("=== M45_SqlMapper ===")
    print(content[:2000])
except Exception as e:
    print(f"Error: {e}")
