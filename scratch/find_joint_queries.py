import os
import re

def search_co_occurrence(workspace_dir):
    mapper_dirs = [
        os.path.join(workspace_dir, "backoffice", "hyundai-backoffice-webapp", "src", "main", "resources", "sqlmapper"),
        os.path.join(workspace_dir, "hyundai-batch", "batchServer", "src", "main", "resources", "mapper")
    ]
    
    found_any = False
    
    for mapper_dir in mapper_dirs:
        if not os.path.exists(mapper_dir):
            continue
        for root, _, files in os.walk(mapper_dir):
            for file in files:
                if file.lower().endswith(".xml"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        # Find all query statement blocks
                        statements = re.findall(r'<(select|insert|update|delete)\s+[^>]*\bid="([^"]+)"[^>]*>([\s\S]*?)</\1>', content, re.IGNORECASE)
                        for tag, stmt_id, sql_text in statements:
                            sql_lower = sql_text.lower()
                            if "sdaypmtb" in sql_lower and "strnchtb" in sql_lower:
                                print(f"Match found in: {file} (ID: {stmt_id})")
                                found_any = True
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
                        
    if not found_any:
        print("No query block contains both sdaypmtb and strnchtb in the entire codebase.")

if __name__ == '__main__':
    search_co_occurrence(r"d:\workspace\hmotors\workspace_hms20260326")
