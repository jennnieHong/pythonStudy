import re
import os

workspace_dir = r"d:\workspace\hmotors\workspace_hms20260326"
file_path = os.path.join(workspace_dir, r"backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\auth\UserAuth_Sql.xml")

if os.path.exists(file_path):
    print("=" * 60)
    print(f"File: UserAuth_Sql.xml")
    print("=" * 60)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    queries = re.findall(r'<select\s+[^>]*id="([^"]+)"[^>]*>([\s\S]*?)</select>', content, re.IGNORECASE)
    for qid, sql_text in queries:
        sql_lower = sql_text.lower()
        if "menumctb" in sql_lower or "menulctb" in sql_lower or "menummtb" in sql_lower:
            print(f"Query ID: {qid}")
            # print all lines
            for line in sql_text.splitlines():
                print(f"    {line}")
            print("-" * 40)
