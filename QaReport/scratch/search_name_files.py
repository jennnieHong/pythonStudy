import glob

files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\*name*", recursive=True)
for f in files[:50]:
    print(f.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', ''))
