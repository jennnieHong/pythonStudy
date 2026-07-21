import glob
import os

files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\*", recursive=True)

found = []
for path in files:
    if os.path.isdir(path):
        continue
    if "QaReport" in path or "scratch" in path or "table_memos" in path or ".git" in path or "build" in path or "bin" in path or "target" in path:
        continue
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "SSNAMETB" in content.upper():
            found.append(path.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', ''))
    except Exception as e:
        pass

for p in found:
    print(p)
