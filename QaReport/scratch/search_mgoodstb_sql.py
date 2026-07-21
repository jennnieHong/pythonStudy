import glob
import os

mappers = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\**\*.xml", recursive=True)

for m in mappers:
    with open(m, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    if "MGOODSTB" in content.upper():
        print(f"Mapped file: {os.path.basename(m)}")
