import glob

files = (
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\*prom*.jsp", recursive=True) +
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\**\*prom*.xml", recursive=True)
)
for f in files[:40]:
    print(f.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', ''))
