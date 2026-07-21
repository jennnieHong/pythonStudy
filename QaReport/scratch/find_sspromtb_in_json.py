import subprocess
import json

# Get previous git version of table_memos.json
cmd = ["git", "show", "HEAD:QaReport/table_memos.json"]
res = subprocess.run(cmd, cwd=r"D:\hmTest\backoffice", capture_output=True, text=True, encoding="utf-8", errors="ignore")

if res.returncode == 0:
    data = json.loads(res.stdout)
    if "tables" in data and "sspromtb" in data["tables"]:
        print(json.dumps(data["tables"]["sspromtb"], indent=2, ensure_ascii=False))
    else:
        print("sspromtb not found in HEAD:table_memos.json")
else:
    print("Failed to run git show:", res.stderr)
