import glob
import os

jsp_files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\views\backoffice\**\*.jsp", recursive=True)

found = []
for path in jsp_files:
    if "QaReport" in path or "scratch" in path:
        continue
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "POSFT" in content.upper() or "기능키" in content or "기능 제어" in content:
            found.append(path.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', ''))
    except Exception as e:
        pass

for p in found[:30]:
    print(p)
