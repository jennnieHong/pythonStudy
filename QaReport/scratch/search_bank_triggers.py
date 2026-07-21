import glob
import os

trigger_files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\sql\trigger\*.sql", recursive=True)

found = []
for path in trigger_files:
    if "QaReport" in path or "scratch" in path:
        continue
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "BANK" in content.upper() or "BANK" in path.upper():
            found.append(path.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', ''))
    except Exception as e:
        pass

for p in found[:30]:
    print(p)
