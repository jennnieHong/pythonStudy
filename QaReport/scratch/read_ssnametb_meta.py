import json

with open("d:\\workspace\\hmotors\\workspace_hms20260326\\table_meta.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for k in data.keys():
    if k.lower() == "ssnametb":
        print(k, ":", json.dumps(data[k], indent=2, ensure_ascii=False))
