import re
import os

workspace_dir = r"d:\workspace\hmotors\workspace_hms20260326"
xml_files = [
    r"backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\auth\UserAuth_Sql.xml",
    r"backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\master\Admin_Master_00001_Sql.xml",
    r"backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\master\Admin_Master_00002_Sql.xml",
    r"backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\master\Hq_Master_00001_Sql.xml",
    r"backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\master\Hq_Master_00002_Sql.xml",
    r"backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\master\Hq_Master_00022_Sql.xml",
    r"backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\system\Admin_System_00007_Sql.xml",
    r"backoffice\hyundai-backoffice-webapp\src\main\resources\sqlmapper\system\Hq_System_00007_Sql.xml"
]

for rel_path in xml_files:
    full_path = os.path.join(workspace_dir, rel_path)
    if not os.path.exists(full_path):
        continue
    print("=" * 60)
    print(f"File: {rel_path}")
    print("=" * 60)
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Let's find XML select/insert/update/delete tags
    queries = re.findall(r'<select\s+[^>]*id="([^"]+)"[^>]*>([\s\S]*?)</select>', content, re.IGNORECASE)
    for qid, sql_text in queries:
        sql_lower = sql_text.lower()
        if "menumctb" in sql_lower or "menulctb" in sql_lower or "menummtb" in sql_lower:
            print(f"Query ID: {qid}")
            # Clean up print
            lines = sql_text.splitlines()
            for line in lines:
                l_strip = line.strip()
                if any(x in l_strip.lower() for x in ["from", "join", "where", "menulctb", "menumctb", "menummtb"]):
                    print(f"    {l_strip}")
            print("-" * 40)
