path = r"d:\workspace\hmotors\workspace_hms20260326\telex\src\main\resources\sqlmapper\M28_SqlMapper.xml"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print("=== M28_SqlMapper.xml ===")
print(content[:2000])
