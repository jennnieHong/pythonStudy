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
        if "PRICE" in content.upper() or "UPRICE" in content.upper():
            # If path contains 'goods' or 'master'
            if "goods" in path.lower() or "price" in path.lower():
                found.append(path.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', ''))
    except Exception as e:
        pass

for p in found[:30]:
    print(p)
