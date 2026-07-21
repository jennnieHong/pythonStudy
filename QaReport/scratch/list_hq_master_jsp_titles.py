import glob
import os
import re

jsp_files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\backup\ROOT\WEB-INF\views\backoffice\main\contents\hq\master\**\*.jsp", recursive=True)

for path in jsp_files:
    fname = os.path.basename(path)
    if "modal" in path.lower() or not fname.endswith(".jsp"):
        continue
    
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    breadcrumbs = re.findall(r'<li[^>]*class="breadcrumb-item[^>]*>(.*?)</li>', content)
    active_breadcrumb = re.search(r'<li[^>]*class="[^"]*active[^"]*"[^>]*>(.*?)</li>', content)
    
    b_str = " > ".join([b.strip() for b in breadcrumbs])
    if active_breadcrumb:
        b_str += " > " + active_breadcrumb.group(1).strip()
    
    b_str = re.sub(r'<[^>]+>', '', b_str)
    print(f"JSP: {fname} | Breadcrumb: {b_str.strip()}")
