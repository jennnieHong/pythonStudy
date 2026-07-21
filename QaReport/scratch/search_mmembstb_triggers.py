import glob
import os

files = (
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\trigger\*.sql", recursive=True) +
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\sqlmapper\trigger\*.xml", recursive=True) +
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\procedure\*.sql", recursive=True) +
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\sqlmapper\procedure\*.xml", recursive=True)
)

for path in files:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    if "MMEMBSTB" in content.upper():
        print(f"File: {path.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', '')}")
