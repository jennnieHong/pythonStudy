import glob
import os

files = (
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\*.sql", recursive=True) +
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\*.xml", recursive=True) +
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\*.java", recursive=True)
)

found = []
for path in files:
    if "QaReport" in path or "scratch" in path or "table_memos" in path:
        continue
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "STRNPMTB" in content.upper():
            found.append(path.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', ''))
    except Exception as e:
        pass

for p in found[:50]:
    print(p)
