import glob
import os
import re

jsp_files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\backup\ROOT\WEB-INF\views\backoffice\main\contents\**\*sales*.jsp", recursive=True)
# Or let's scan all JSPs in hq/sales and st/sales

sales_jsps = (
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\backup\ROOT\WEB-INF\views\backoffice\main\contents\hq\sales\**\*.jsp", recursive=True) +
    glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\backup\ROOT\WEB-INF\views\backoffice\main\contents\st\sales\**\*.jsp", recursive=True)
)

for path in sales_jsps:
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
