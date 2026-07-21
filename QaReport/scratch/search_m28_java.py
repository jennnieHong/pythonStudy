import glob

files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\*.java", recursive=True)
for f in files:
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
        if "M28" in content:
            print(f.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', ''))
    except Exception as e:
        pass
