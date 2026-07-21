import glob
import os

files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\trigger\*MMEMB*.sql", recursive=True)

for path in files:
    print(f"Trigger file: {path.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', '')}")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    print(content[:1000])
    print("\n" + "="*50 + "\n")
