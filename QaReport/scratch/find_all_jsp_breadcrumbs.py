import glob
import os
import re

jsp_files = glob.glob(r"d:\workspace\hmotors\workspace_hms20260326\backup\ROOT\WEB-INF\views\backoffice\main\contents\**\*.jsp", recursive=True)

for path in jsp_files:
    fname = os.path.basename(path)
    if not fname.endswith(".jsp") or "_" not in fname or "modal" in path.lower():
        continue
    
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Try to find breadcrumbs
    # Example: <li class="breadcrumb-item" ...>마스터관리</li>
    # <li class="breadcrumb-item active" ...>매장정보관리</li>
    breadcrumbs = re.findall(r'<li[^>]*class="breadcrumb-item[^>]*>(.*?)</li>', content)
    active_breadcrumb = re.search(r'<li[^>]*class="[^"]*active[^"]*"[^>]*>(.*?)</li>', content)
    
    breadcrumb_str = " > ".join([b.strip() for b in breadcrumbs])
    if active_breadcrumb:
        breadcrumb_str += " > " + active_breadcrumb.group(1).strip()
        
    # Strip HTML tags
    breadcrumb_str = re.sub(r'<[^>]+>', '', breadcrumb_str)
    
    # Check if "단가" or "가격" is in the breadcrumb or body
    if "단가" in breadcrumb_str or "단가" in content:
        print(f"Screen: {os.path.splitext(fname)[0]} | Breadcrumb: {breadcrumb_str.strip()} | Path: {path.replace('d:\\workspace\\hmotors\\workspace_hms20260326\\', '')}")
