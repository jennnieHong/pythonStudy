import json

with open("d:\\workspace\\hmotors\\workspace_hms20260326\\table_meta.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Type of data:", type(data))
if isinstance(data, dict):
    print("Keys count:", len(data))
    print("Some keys:", list(data.keys())[:10])
    if "ssnametb" in data:
        print("ssnametb:", data["ssnametb"])
elif isinstance(data, list):
    print("Items count:", len(data))
    print("First item:", data[0])
    for item in data:
        if isinstance(item, str) and "ssnametb" in item.lower():
            print("Found str:", item)
        elif isinstance(item, dict) and item.get("table_name", "").lower() == "ssnametb":
            print("Found dict:", item)
