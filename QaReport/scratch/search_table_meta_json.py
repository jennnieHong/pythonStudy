import json

with open("d:\\workspace\\hmotors\\workspace_hms20260326\\table_meta.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for t in data:
    if t.get("table_name", "").lower() == "ssnametb":
        print(json.dumps(t, indent=2, ensure_ascii=False))
