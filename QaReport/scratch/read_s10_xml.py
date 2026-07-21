path = r"d:\workspace\hmotors\workspace_hms20260326\telex\src\main\resources\sqlmapper\S10_SqlMapper.xml"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print("=== S10_SqlMapper.xml ===")
lines = content.splitlines()
for idx, line in enumerate(lines):
    if "SSNAMETB" in line.upper():
        print(f"Line {idx+1}: {line}")
        # print around the line
        for offset in range(-5, 6):
            if 0 <= idx + offset < len(lines):
                print(f"  {idx+offset+1}: {lines[idx+offset]}")
