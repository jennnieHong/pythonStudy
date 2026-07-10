import psycopg2
import json
import os
import re

def read_file_with_encodings(file_path):
    for enc in ["utf-8", "cp949", "euc-kr"]:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def parse_screen_names(controller_dir):
    screen_names = {}
    if not os.path.exists(controller_dir):
        return screen_names
    for root, dirs, files in os.walk(controller_dir):
        for file in files:
            if file.endswith("Controller.java") or file.endswith("_Controller.java"):
                screen_id = file
                for suffix in ["_Controller.java", "Controller.java"]:
                    if screen_id.endswith(suffix):
                        screen_id = screen_id[:-len(suffix)]
                        break
                screen_id = screen_id.upper()
                
                file_path = os.path.join(root, file)
                try:
                    content = read_file_with_encodings(file_path)
                    match = re.search(r'@ServiceLog\s*\([^)]*\bmenu\s*=\s*"([^"]+)"', content)
                    if match:
                        screen_names[screen_id] = match.group(1).strip()
                except Exception as e:
                    pass
    return screen_names

def parse_batch_names(service_dir):
    batch_names = {}
    if not os.path.exists(service_dir):
        return batch_names
    for root, dirs, files in os.walk(service_dir):
        for file in files:
            if file.endswith("Service.java"):
                batch_id = file
                if batch_id.endswith("Service.java"):
                    batch_id = batch_id[:-12]
                batch_id = batch_id.upper()
                
                file_path = os.path.join(root, file)
                try:
                    content = read_file_with_encodings(file_path)
                    class_name = file.replace(".java", "")
                    pattern = rf"(/\*\*[\s\S]*?\*/)\s*(?:@[a-zA-Z0-9_]+(?:\([^)]*\))?\s*)*public\s+class\s+{class_name}"
                    match = re.search(pattern, content)
                    if match:
                        javadoc = match.group(1)
                        lines = javadoc.split("\n")
                        for line in lines:
                            cleaned = line.strip().lstrip("/* \t*")
                            if cleaned and not cleaned.startswith("@") and not cleaned.lower().startswith("created"):
                                cleaned = cleaned.split("*/")[0].strip()
                                batch_names[batch_id] = cleaned
                                break
                except Exception as e:
                    pass
    return batch_names

def analyze_mappers(mapper_dir, table_names, is_batch):
    mapping = {}
    if not os.path.exists(mapper_dir):
        print(f"Mapper directory not found: {mapper_dir}")
        return mapping
        
    for root, dirs, files in os.walk(mapper_dir):
        for file in files:
            if file.lower().endswith(".xml"):
                if is_batch:
                    screen_id = file.replace("_SQL.xml", "").replace("_Sql.xml", "").replace("_sql.xml", "").upper()
                else:
                    screen_id = file.replace("_Sql.xml", "").replace("_SQL.xml", "").replace("_sql.xml", "").upper()
                
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                    
                    content_words = set(re.findall(r'[a-z0-9_]+', content))
                    for tname in table_names:
                        tname_lower = tname.lower()
                        if tname_lower in content_words:
                            if tname not in mapping:
                                mapping[tname] = []
                            if screen_id not in mapping[tname]:
                                mapping[tname].append(screen_id)
                except Exception as e:
                    pass
    return mapping

def get_auto_relations(workspace_dir, table_names):
    relations = {}
    table_names_set = set(t.lower() for t in table_names)
    
    mapper_dirs = [
        os.path.join(workspace_dir, "backoffice", "hyundai-backoffice-webapp", "src", "main", "resources", "sqlmapper"),
        os.path.join(workspace_dir, "hyundai-batch", "batchServer", "src", "main", "resources", "mapper")
    ]
    
    for mapper_dir in mapper_dirs:
        if not os.path.exists(mapper_dir):
            continue
        for root, _, files in os.walk(mapper_dir):
            for file in files:
                if file.lower().endswith(".xml"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        statements = re.findall(r'<(select|insert|update|delete)\s+[^>]*\bid="([^"]+)"[^>]*>([\s\S]*?)</\1>', content, re.IGNORECASE)
                        for tag, stmt_id, sql_text in statements:
                            sql_lower = sql_text.lower()
                            words = set(re.findall(r'[a-z0-9_]+', sql_lower))
                            found_tables = words.intersection(table_names_set)
                            
                            if len(found_tables) > 1:
                                stmt_info = f"{file} ({stmt_id})"
                                for t1 in found_tables:
                                    for t2 in found_tables:
                                        if t1 != t2:
                                            if t1 not in relations:
                                                relations[t1] = {}
                                            if t2 not in relations[t1]:
                                                relations[t1][t2] = set()
                                            relations[t1][t2].add(stmt_info)
                    except Exception:
                        pass
    return relations

def main():
    print("Connecting to EDB PostgreSQL...")
    try:
        conn = psycopg2.connect(
            host='192.168.10.206', 
            port='5432', 
            dbname='edb', 
            user='hmsfns_adm', 
            password='astems2!'
        )
        cur = conn.cursor()
    except Exception as e:
        print("Failed to connect to database:", e)
        return

    # 1. Fetch tables and comments
    print("Fetching tables...")
    cur.execute("""
        SELECT c.relname AS table_name,
               obj_description(c.oid, 'pg_class') AS comment
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'hmsfns' AND c.relkind = 'r'
        ORDER BY c.relname;
    """)
    tables = cur.fetchall()

    # 2. Fetch columns
    print("Fetching columns...")
    cur.execute("""
        SELECT c.relname AS table_name,
               a.attname AS column_name,
               pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
               a.attnotnull AS not_null,
               pg_catalog.pg_get_expr(d.adbin, d.adrelid) AS default_value,
               col_description(a.attrelid, a.attnum) AS comment
        FROM pg_attribute a
        JOIN pg_class c ON c.oid = a.attrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
        WHERE n.nspname = 'hmsfns'
          AND c.relkind = 'r'
          AND a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY c.relname, a.attnum;
    """)
    columns_raw = cur.fetchall()

    # 3. Fetch indexes
    print("Fetching indexes...")
    cur.execute("""
        SELECT t.relname AS table_name,
               i.relname AS index_name,
               pg_get_indexdef(ix.indexrelid) AS index_def
        FROM pg_index ix
        JOIN pg_class t ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        WHERE n.nspname = 'hmsfns'
        ORDER BY t.relname, i.relname;
    """)
    indexes_raw = cur.fetchall()

    cur.close()
    conn.close()

    # Organize data
    db_data = {}
    for tname, comment in tables:
        db_data[tname] = {
            "table_name": tname,
            "comment": comment or "",
            "columns": [],
            "indexes": []
        }

    for tname, col_name, dtype, not_null, default_val, comment in columns_raw:
        if tname in db_data:
            db_data[tname]["columns"].append({
                "column_name": col_name,
                "data_type": dtype,
                "nullable": "YES" if not not_null else "NO",
                "default_value": default_val or "",
                "comment": comment or ""
            })

    for tname, idx_name, idx_def in indexes_raw:
        if tname in db_data:
            db_data[tname]["indexes"].append({
                "index_name": idx_name,
                "index_def": idx_def
            })

    # 4. Load custom memos from table_memos.json if it exists
    memo_path = r"D:\hmTest\backoffice\QaReport\table_memos.json"
    memos = {}
    if os.path.exists(memo_path):
        try:
            with open(memo_path, "r", encoding="utf-8") as f:
                memos = json.load(f)
            print(f"Loaded custom memos from: {memo_path}")
        except Exception as e:
            print("Failed to read memos:", e)

    # 5. Analyze mapper files for screen and batch relationships
    workspace_dir = r"d:\workspace\hmotors\workspace_hms20260326"
    backoffice_mapper_dir = os.path.join(workspace_dir, "backoffice", "hyundai-backoffice-webapp", "src", "main", "resources", "sqlmapper")
    batch_mapper_dir = os.path.join(workspace_dir, "hyundai-batch", "batchServer", "src", "main", "resources", "mapper")

    table_names = list(db_data.keys())
    
    print("Analyzing backoffice screen relationships...")
    backoffice_relations = analyze_mappers(backoffice_mapper_dir, table_names, is_batch=False)
    
    print("Analyzing batch job relationships...")
    batch_relations = analyze_mappers(batch_mapper_dir, table_names, is_batch=True)

    print("Parsing screen names from controllers...")
    controller_dir = os.path.join(workspace_dir, "backoffice", "hyundai-backoffice-webapp", "src", "main", "java", "com", "hyundai", "backoffice", "webapp", "controller")
    screen_names = parse_screen_names(controller_dir)

    print("Parsing batch names from batch services...")
    service_dir = os.path.join(workspace_dir, "hyundai-batch", "batchServer", "src", "main", "java", "com", "hyundai", "batch", "service")
    batch_names = parse_batch_names(service_dir)

    print("Analyzing query-based related tables...")
    auto_relations = get_auto_relations(workspace_dir, table_names)

    # Merge all into db_data
    print("Scanning markdown files for table and column relations...")
    qa_report_dir = r"D:\hmTest\backoffice\QaReport"
    table_to_mds = {t: [] for t in table_names}
    table_col_to_mds = {}
    COMMON_COLUMNS = {"ms_no", "create_dtime", "create_id", "modify_dtime", "modify_id", "use_yn", "update_dtime", "update_id", "sort_order", "remark"}
    
    if os.path.exists(qa_report_dir):
        for filename in os.listdir(qa_report_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(qa_report_dir, filename)
                try:
                    content = read_file_with_encodings(filepath).lower()
                    content_words = set(re.findall(r'[a-z0-9_]+', content))
                    filename_lower = filename.lower()
                    
                    for tname in table_names:
                        tname_lower = tname.lower()
                        if (tname_lower in filename_lower) or (tname_lower in content_words):
                            if filename not in table_to_mds[tname]:
                                table_to_mds[tname].append(filename)
                            for col in db_data[tname]["columns"]:
                                cname = col["column_name"].lower()
                                if cname in COMMON_COLUMNS or len(cname) < 3:
                                    continue
                                if cname in content_words:
                                    key_pair = (tname_lower, cname)
                                    if key_pair not in table_col_to_mds:
                                        table_col_to_mds[key_pair] = []
                                    if filename not in table_col_to_mds[key_pair]:
                                        table_col_to_mds[key_pair].append(filename)
                except Exception as e:
                    print(f"Error scanning {filename}: {e}")

    table_memos = memos.get("tables", {})
    for tname, tdata in db_data.items():
        # Add relations
        raw_screens = backoffice_relations.get(tname, [])
        tdata["screens"] = [{"id": scr, "name": screen_names.get(scr, "")} for scr in raw_screens]
        
        raw_batches = batch_relations.get(tname, [])
        tdata["batches"] = [{"id": bat, "name": batch_names.get(bat, "")} for bat in raw_batches]
        
        # Add guides
        tdata["guides"] = table_to_mds.get(tname, [])
        
        # Add/Merge memos
        tdata["custom_memo"] = ""
        tdata["manual_guide"] = ""
        tdata["memo_c"] = ""
        tdata["memo_u"] = ""
        tdata["memo_d"] = ""
        tdata["memo_r"] = ""
        tdata["starred"] = False
        tdata["color"] = "none"
        tdata["sort_order"] = 9999
        
        custom_related = []
        if tname in table_memos:
            tinfo = table_memos[tname]
            tdata["custom_memo"] = tinfo.get("memo", "")
            tdata["manual_guide"] = tinfo.get("guide", "")
            tdata["memo_c"] = tinfo.get("memo_c", "")
            tdata["memo_u"] = tinfo.get("memo_u", "")
            tdata["memo_d"] = tinfo.get("memo_d", "")
            tdata["memo_r"] = tinfo.get("memo_r", "")
            tdata["starred"] = tinfo.get("starred", False)
            tdata["color"] = tinfo.get("color", "none")
            custom_related = tinfo.get("related_tables", [])
            
            merged_relations = {}
            for rel in custom_related:
                if isinstance(rel, dict) and "table_name" in rel:
                    merged_relations[rel["table_name"]] = rel.get("description", "")
                elif isinstance(rel, str):
                    merged_relations[rel] = ""
                    
            auto_list = auto_relations.get(tname, {})
            for rel_tbl, stmt_set in auto_list.items():
                if rel_tbl not in merged_relations:
                    stmt_list = sorted(list(stmt_set))
                    desc = f"[자동 분석] {', '.join(stmt_list[:2])} 등의 쿼리에서 공동 사용됨"
                    merged_relations[rel_tbl] = desc
                    
            tdata["related_tables"] = [
                {"table_name": k, "description": v} for k, v in sorted(merged_relations.items())
            ]
            
            # sortOrder can be a string or number
            sort_order_val = tinfo.get("sortOrder", "9999")
            try:
                tdata["sort_order"] = int(sort_order_val)
            except:
                tdata["sort_order"] = 9999
                
            if not tdata["comment"] and tdata["custom_memo"]:
                # Use the first line of custom memo as the short comment
                tdata["comment"] = tdata["custom_memo"].split('\n')[0].strip()
            
            col_memos = tinfo.get("columns", {})
            for col in tdata["columns"]:
                cname = col["column_name"]
                col_info = col_memos.get(cname, "")
                manual_memo = ""
                manual_guide = ""
                if isinstance(col_info, dict):
                    manual_memo = col_info.get("memo", "")
                    manual_guide = col_info.get("guide", "")
                else:
                    manual_memo = col_info
                
                col["custom_memo"] = manual_memo
                col["manual_guide"] = manual_guide
                col["guides"] = table_col_to_mds.get((tname.lower(), cname.lower()), [])
                
                if not col["comment"] and col["custom_memo"]:
                    col["comment"] = col["custom_memo"]
        else:
            for col in tdata["columns"]:
                col["custom_memo"] = ""
                col["manual_guide"] = ""
                col["guides"] = table_col_to_mds.get((tname.lower(), col["column_name"].lower()), [])
                
            merged_relations = {}
            auto_list = auto_relations.get(tname, {})
            for rel_tbl, stmt_set in auto_list.items():
                stmt_list = sorted(list(stmt_set))
                desc = f"[자동 분석] {', '.join(stmt_list[:2])} 등의 쿼리에서 공동 사용됨"
                merged_relations[rel_tbl] = desc
                
            tdata["related_tables"] = [
                {"table_name": k, "description": v} for k, v in sorted(merged_relations.items())
            ]

    # Convert to sorted list
    table_list = [db_data[t] for t in sorted(db_data.keys())]
    
    html_content = get_html_template(table_list)
    
    # Load table_memos.json content to embed directly inside HTML
    raw_memos_str = "{}"
    if os.path.exists(memo_path):
        try:
            with open(memo_path, "r", encoding="utf-8") as f:
                raw_memos_str = json.dumps(json.load(f), ensure_ascii=False)
        except Exception as e:
            print("Failed to embed memos:", e)
            
    html_content = html_content.replace("/*EMBEDDED_MEMOS_PLACEHOLDER*/", raw_memos_str)
    
    output_path = r"D:\hmTest\backoffice\QaReport\hms_db_dictionary.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Database Dictionary HTML successfully generated at: {output_path}")

def get_html_template(table_list):
    table_list_json = json.dumps(table_list, ensure_ascii=False)
    
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HMS 데이터베이스 테이블 명세서</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  :root {{
    --primary: #1e3a8a;
    --primary-light: #eff6ff;
    --primary-accent: #2563eb;
    --text-main: #1e293b;
    --text-muted: #64748b;
    --bg-main: #f8fafc;
    --bg-card: #ffffff;
    --border: #e2e8f0;
    --highlight: #fef08a;
    --highlight-text: #854d0e;
    --badge-key: #f59e0b;
    --badge-type: #10b981;
    --badge-null: #ef4444;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    font-family: 'Inter', 'Noto Sans KR', sans-serif;
    background-color: var(--bg-main);
    color: var(--text-main);
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}

  header {{
    background: linear-gradient(135deg, var(--primary), var(--primary-accent));
    color: white;
    padding: 16px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    z-index: 10;
  }}

  header h1 {{
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.025em;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  header .sub-title {{
    font-size: 12px;
    opacity: 0.8;
    background: rgba(255,255,255,0.15);
    padding: 4px 10px;
    border-radius: 20px;
  }}

  #wrapper {{
    display: flex;
    flex: 1;
    overflow: hidden;
    position: relative;
    height: calc(100vh - 56px);
  }}

  /* 왼쪽 사이드바 (테이블 리스트) */
  #sidebar {{
    width: 380px;
    background: var(--bg-card);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    height: 100%;
    z-index: 5;
  }}

  .search-box {{
    padding: 16px;
    border-bottom: 1px solid var(--border);
    background: #fff;
  }}

  .search-input-wrapper {{
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}

  .input-field {{
    width: 100%;
    padding: 10px 12px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    font-size: 13.5px;
    outline: none;
    transition: all 0.2s ease;
    color: var(--text-main);
  }}

  .input-field:focus {{
    border-color: var(--primary-accent);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
  }}

  .search-options {{
    display: flex;
    gap: 12px;
    font-size: 12px;
    color: var(--text-muted);
  }}

  .search-options label {{
    display: flex;
    align-items: center;
    gap: 5px;
    cursor: pointer;
  }}

  .search-options input[type="checkbox"] {{
    accent-color: var(--primary-accent);
    cursor: pointer;
  }}

  #table-list-container {{
    flex: 1;
    overflow-y: auto;
    padding: 8px 0;
  }}

  .table-item {{
    padding: 10px 14px;
    cursor: pointer;
    border-bottom: 1px solid #f1f5f9;
    transition: all 0.15s ease;
    display: flex;
    align-items: center;
    gap: 8px;
    overflow: hidden;
  }}

  .table-item:hover {{
    background-color: #f8fafc;
  }}

  .table-item.active {{
    background-color: var(--primary-light);
    border-left: 4px solid var(--primary-accent);
    padding-left: 10px;
  }}

  .table-item .t-name {{
    font-family: monospace;
    font-size: 13.5px;
    font-weight: 700;
    color: var(--primary);
    flex-shrink: 0;
  }}

  .table-item.active .t-name {{
    color: var(--primary-accent);
  }}

  .table-item .t-desc {{
    font-size: 11.5px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex-grow: 1;
    font-weight: normal;
  }}

  .table-count {{
    padding: 10px 16px;
    font-size: 12px;
    color: var(--text-muted);
    background: #f8fafc;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
  }}

  /* 오른쪽 상세 영역 */
  #content {{
    flex: 1;
    background: var(--bg-main);
    padding: 24px 32px;
    height: 100%;
    overflow: hidden;
  }}

  #no-selection {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted);
    gap: 12px;
  }}

  #no-selection svg {{
    width: 64px;
    height: 64px;
    stroke: var(--text-muted);
    opacity: 0.5;
  }}

  .detail-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
  }}

  .detail-header {{
    background: #fff;
    padding: 20px 24px;
    border-bottom: 1.5px solid var(--border);
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex-shrink: 0;
  }}

  .detail-header .title-row {{
    display: flex;
    align-items: baseline;
    gap: 12px;
  }}

  .detail-header h2 {{
    font-family: monospace;
    font-size: 22px;
    font-weight: 700;
    color: var(--primary);
  }}

  .detail-header .comment {{
    font-size: 14px;
    color: var(--text-muted);
    font-weight: 500;
    white-space: pre-wrap;
    margin-top: 4px;
    line-height: 1.5;
  }}

  .markdown-content h1 {{ font-size: 1.5em; margin: 12px 0 6px 0; color: #78350f; font-weight: 700; border-bottom: 2px solid #fde68a; padding-bottom: 4px; }}
  .markdown-content h2 {{ font-size: 1.3em; margin: 12px 0 6px 0; color: #78350f; font-weight: 700; border-bottom: 1.5px solid #fde68a; padding-bottom: 3px; }}
  .markdown-content h3 {{ font-size: 1.1em; margin: 12px 0 6px 0; color: #78350f; font-weight: 700; border-bottom: 1px solid #fde68a; padding-bottom: 2px; }}
  .markdown-content p {{ margin-bottom: 10px; line-height: 1.6; }}
  .markdown-content ul, .markdown-content ol {{ margin-left: 20px; margin-bottom: 10px; }}
  .markdown-content li {{ margin-bottom: 4px; line-height: 1.5; }}
  .markdown-content code {{ font-family: monospace; background-color: rgba(245, 158, 11, 0.1); padding: 2px 5px; border-radius: 4px; font-size: 0.9em; color: #b45309; font-weight: bold; }}
  .markdown-content pre {{ background-color: #1e293b; color: #f8fafc; padding: 12px 16px; border-radius: 8px; margin: 12px 0; overflow-x: auto; font-family: monospace; }}
  .markdown-content pre code {{ background-color: transparent; color: inherit; padding: 0; font-size: 0.9em; font-weight: normal; }}

  .detail-body {{
    padding: 24px;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
  }}

  .section-title {{
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .table-container {{
    flex: 1;
    overflow-y: auto;
    min-height: 0;
    border: 1px solid var(--border);
    border-radius: 8px;
    background-color: #fff;
  }}

  /* 테이블 스타일 */
  table {{
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    margin-bottom: 0;
  }}

  th {{
    background-color: #f1f5f9;
    color: var(--text-muted);
    font-weight: 600;
    padding: 10px 14px;
    font-size: 12.5px;
    border-bottom: 1.5px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 2;
  }}

  td {{
    padding: 12px 14px;
    font-size: 13.5px;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
  }}

  tr:last-child td {{
    border-bottom: none;
  }}

  tr.highlight-row {{
    background-color: #fffbeb;
  }}

  tr.highlight-row td {{
    border-bottom: 1px solid #fde68a;
  }}

  .col-name {{
    font-family: monospace;
    font-weight: 700;
    color: #0f172a;
  }}

  .col-type {{
    font-family: monospace;
    color: #0284c7;
  }}

  .badge {{
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10.5px;
    font-weight: 600;
    text-transform: uppercase;
  }}

  .badge.pk {{
    background-color: #fef3c7;
    color: #d97706;
    border: 1px solid #fde68a;
  }}

  .badge.nn {{
    background-color: #fee2e2;
    color: #ef4444;
    border: 1px solid #fca5a5;
  }}

  .badge.fk {{
    background-color: #e0f2fe;
    color: #0284c7;
    border: 1px solid #bae6fd;
  }}

  .badge.special {{
    background-color: #f3e8ff;
    color: #7e22ce;
    border: 1px solid #e9d5ff;
  }}

  .badge.screen-id {{
    background-color: #f0fdf4;
    color: #166534;
    border: 1px solid #bbf7d0;
    text-transform: none;
    font-size: 11px;
  }}

  .badge.batch-id {{
    background-color: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
    text-transform: none;
    font-size: 11px;
  }}

  .memo-container {{
    background-color: #fffbeb;
    border: 1px dashed #fde68a;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 12px;
  }}

  .memo-container-mini {{
    background-color: #fffbeb;
    border: 1px dashed #fde68a;
    border-radius: 8px;
    padding: 8px 12px;
    width: 320px;
    flex-shrink: 0;
  }}

  .memo-title {{
    font-size: 13px;
    font-weight: 700;
    color: #854d0e;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .memo-edit-btn {{
    padding: 2px 8px;
    font-size: 11px;
    background: transparent;
    border: 1px solid #d97706;
    color: #d97706;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }}

  .memo-edit-btn:hover {{
    background: #d97706;
    color: #fff;
  }}

  .memo-content {{
    font-size: 13px;
    color: #78350f;
    white-space: pre-wrap;
    line-height: 1.5;
  }}

  /* Custom horizontal scrollbars for relation badges */
  .relation-row div::-webkit-scrollbar {{
    height: 5px;
  }}
  .relation-row div::-webkit-scrollbar-track {{
    background: transparent;
  }}
  .relation-row div::-webkit-scrollbar-thumb {{
    background: #cbd5e1;
    border-radius: 10px;
  }}
  .relation-row div::-webkit-scrollbar-thumb:hover {{
    background: #94a3b8;
  }}

  .default-val {{
    font-family: monospace;
    color: #64748b;
    font-size: 12px;
  }}

  .col-comment {{
    line-height: 1.45;
  }}

  .index-card {{
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    font-family: monospace;
    font-size: 12.5px;
    color: #334155;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    cursor: pointer;
    transition: all 0.2s ease;
  }}

  .index-card:hover {{
    background-color: #f1f5f9;
    border-color: #cbd5e1;
  }}

  .index-card.active {{
    background-color: #e0f2fe;
    border-color: #0284c7;
    color: #0369a1;
  }}

  .index-card .idx-name {{
    font-weight: 700;
    color: var(--primary-accent);
  }}

  .index-card.active .idx-name {{
    color: #0284c7;
  }}

  tr.index-highlight-row {{
    background-color: #e0f2fe !important;
  }}

  tr.index-highlight-row td {{
    border-bottom: 1.5px solid #7dd3fc !important;
  }}

  mark.search-match {{
    background-color: var(--highlight);
    color: var(--highlight-text);
    padding: 0 2px;
    border-radius: 2px;
    font-weight: 600;
  }}

  /* Side details drawer & overlay style */
  .drawer-overlay {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    z-index: 998;
    display: none;
    opacity: 0;
    transition: opacity 0.3s ease;
  }}

  .drawer {{
    position: fixed;
    top: 0;
    right: -1120px;
    width: 1100px;
    height: 100%;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(25px);
    border-left: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: -10px 0 40px rgba(0, 0, 0, 0.06);
    z-index: 999;
    transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 40px 30px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }}

  .drawer.open {{
    right: 0;
  }}

  .drawer-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    padding-bottom: 20px;
  }}

  .drawer-header h2 {{
    font-size: 20px;
    font-weight: 700;
    color: var(--primary);
  }}

  .close-btn {{
    background: rgba(0, 0, 0, 0.03);
    border: 1px solid var(--border-color);
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.2s ease;
  }}

  .close-btn:hover {{
    background: rgba(0, 0, 0, 0.06);
    color: #000000;
  }}

  .drawer-content {{
    display: flex;
    flex-direction: column;
    gap: 20px;
  }}

  .detail-group {{
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}

  .detail-label {{
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
  }}

  .detail-value {{
    font-size: 14px;
    color: var(--text-main);
    background: rgba(0, 0, 0, 0.01);
    border: 1px solid rgba(0, 0, 0, 0.04);
    padding: 12px 16px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .detail-value.code-val {{
    font-family: monospace;
    font-size: 13px;
  }}

  /* Toast notification */
  .toast {{
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translate(-50%, 100px);
    background: rgba(30, 58, 138, 0.95);
    color: #FFFFFF;
    padding: 12px 24px;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 600;
    z-index: 1001;
    box-shadow: 0 4px 15px rgba(30, 58, 138, 0.25);
    transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    pointer-events: none;
  }}

  .toast.show {{
    transform: translate(-50%, 0);
  }}

  .color-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }}
  .color-dot.color-red {{ background-color: #ef4444; }}
  .color-dot.color-orange {{ background-color: #f97316; }}
  .color-dot.color-yellow {{ background-color: #eab308; }}
  .color-dot.color-green {{ background-color: #22c55e; }}
  .color-dot.color-blue {{ background-color: #3b82f6; }}
  .color-dot.color-purple {{ background-color: #a855f7; }}

  /* Tab Navigation */
  .detail-tabs {{
    display: flex;
    border-bottom: 2px solid var(--border);
    margin-bottom: 16px;
    gap: 8px;
    flex-shrink: 0;
  }}

  .tab-btn {{
    padding: 10px 20px;
    border: none;
    background: none;
    font-family: inherit;
    font-weight: 600;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 13.5px;
    border-bottom: 3px solid transparent;
    transition: all 0.2s ease;
    margin-bottom: -2px;
  }}

  .tab-btn:hover {{
    color: var(--primary-accent);
    background-color: var(--primary-light);
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
  }}

  .tab-btn.active {{
    font-weight: 700;
    color: var(--primary-accent);
    border-bottom-color: var(--primary-accent);
  }}

  .tab-content {{
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }}

  .guides-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
    width: 100%;
    padding: 4px 2px;
  }}

  .guide-card {{
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 16px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  }}

  .guide-card:hover {{
    border-color: var(--primary-accent);
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(37, 99, 235, 0.08);
  }}

  .guide-card-btn {{
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background-color: var(--primary-light);
    color: var(--primary-accent);
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 700;
    border: 1px solid #bfdbfe;
    transition: all 0.2s ease;
  }}

  .guide-card-btn:hover {{
    background-color: var(--primary-accent);
    color: white;
    border-color: var(--primary-accent);
  }}
</style>
</head>
<body>

<header>
  <h1>HMS 데이터베이스 테이블 명세서 (hmsfns 스키마)</h1>
  <div style="display: flex; align-items: center; gap: 16px;">
    <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: white;">
      <span>경로:</span>
      <input type="text" id="export-filepath" value="D:\\hmTest\\backoffice\\QaReport" style="padding: 4px 8px; font-size: 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.3); outline: none; width: 220px; background: rgba(255,255,255,0.1); color: white;">
      <span>파일명:</span>
      <input type="text" id="export-filename" value="table_memos.json" style="padding: 4px 8px; font-size: 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.3); outline: none; width: 150px; background: rgba(255,255,255,0.1); color: white;">
    </div>
    <button onclick="exportMemos()" style="background: rgba(255,255,255,0.15); color: white; border: 1px solid rgba(255,255,255,0.3); padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: all 0.2s; font-family: inherit;" onmouseover="this.style.background='rgba(255,255,255,0.25)'" onmouseout="this.style.background='rgba(255,255,255,0.15)'">사용자 메모 백업 (JSON)</button>
    <button onclick="importMemos()" style="background: rgba(255,255,255,0.15); color: white; border: 1px solid rgba(255,255,255,0.3); padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: all 0.2s; font-family: inherit;" onmouseover="this.style.background='rgba(255,255,255,0.25)'" onmouseout="this.style.background='rgba(255,255,255,0.15)'">사용자 메모 복원 (JSON)</button>
    <button onclick="clearLocalMemos()" style="background: rgba(239,68,68,0.20); color: #fecaca; border: 1px solid rgba(239,68,68,0.40); padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: all 0.2s; font-family: inherit;" onmouseover="this.style.background='rgba(239,68,68,0.35)'" onmouseout="this.style.background='rgba(239,68,68,0.20)'">로컬 캐시 초기화</button>
    <input type="file" id="import-memos-file" style="display: none;" accept=".json" onchange="handleImportFile(event)">
    <div class="sub-title">총 <span id="header-total-tables">0</span>개 테이블</div>
  </div>
</header>

<div id="wrapper">
  <!-- 왼쪽 사이드바 -->
  <div id="sidebar">
    <div class="search-box">
      <div class="search-input-wrapper">
        <input type="text" id="search" class="input-field" placeholder="테이블명, 설명, 컬럼명 검색..." autocomplete="off">
        <div class="search-options" style="flex-wrap: wrap; gap: 8px 12px;">
          <label><input type="checkbox" id="chk-all-search" checked> 전체</label>
          <span style="color:var(--border); user-select: none; margin: 0 -2px;">|</span>
          <label><input type="checkbox" id="chk-table-search" checked> 테이블명/설명</label>
          <label><input type="checkbox" id="chk-column-search" checked> 컬럼명/설명</label>
          <label><input type="checkbox" id="chk-memo-search" checked> 메모</label>
          <label><input type="checkbox" id="chk-relation-search" checked> 연관화면/배치</label>
          <label><input type="checkbox" id="chk-guide-search" checked> 연관가이드</label>
        </div>
        <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 6px; font-size: 12px; border-top: 1px solid var(--border); padding-top: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: var(--text-muted); font-weight: 600;">다중 정렬 조건 (클릭 시 순차 적용/해제):</span>
            <button onclick="clearSortQueue()" style="background: none; border: none; color: var(--primary-accent); font-size: 11px; cursor: pointer; padding: 0; font-weight: 700;">초기화</button>
          </div>
          <div id="sort-queue-container" style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 2px;">
            <!-- JS dynamically inserts sort option badges here -->
          </div>
        </div>
      </div>
    </div>
    
    <div id="table-list-container">
      <!-- 테이블 목록 바인딩 -->
    </div>
    
    <div class="table-count">
      <span>검색 결과: <strong id="filter-count">0</strong>개</span>
      <span>전체 테이블: <strong id="total-count">0</strong>개</span>
    </div>
  </div>

  <!-- 오른쪽 상세 영역 -->
  <div id="content">
    <div id="no-selection">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
      </svg>
      <p>조회할 테이블을 왼쪽 목록에서 선택해 주세요.</p>
    </div>
  </div>
</div>

<!-- Side details drawer -->
<div class="drawer-overlay" id="drawer-overlay"></div>
<div class="drawer" id="detail-drawer">
  <div class="drawer-header">
    <h2>테이블 메모 및 상세 정보</h2>
    <button class="close-btn" id="close-drawer">닫기</button>
  </div>
  <div class="drawer-content" style="display: grid; grid-template-columns: 420px 1fr; gap: 24px; align-items: start;">
    <!-- Left Info Column -->
    <div style="display: flex; flex-direction: column; gap: 16px; min-width: 0;">
      <div class="detail-group">
        <div class="detail-label">테이블명 (Table Name)</div>
        <div class="detail-value code-val" id="drawer-table-name" style="font-weight: 700; color: var(--primary);"></div>
      </div>
      <div class="detail-group">
        <div class="detail-label">테이블 설명 (Comment)</div>
        <div class="detail-value" id="drawer-table-comment" style="font-weight: 500; line-height: 1.45;"></div>
      </div>
      <div class="detail-group">
        <div class="detail-label">연관 화면 (Screens)</div>
        <div class="detail-value" id="drawer-table-screens" style="display: block; overflow-y: auto; max-height: 150px; line-height: 1.6;"></div>
      </div>
      <div class="detail-group">
        <div class="detail-label">연관 배치 (Batches)</div>
        <div class="detail-value" id="drawer-table-batches" style="display: block; overflow-y: auto; max-height: 150px; line-height: 1.6;"></div>
      </div>
    </div>
    
    <!-- Right Memo Column -->
    <div style="display: flex; flex-direction: column; gap: 16px; height: 100%; min-height: 0; overflow-y: auto; padding-right: 4px;">
      <div class="detail-group" style="background: rgba(30, 58, 138, 0.04); border: 1px dashed rgba(30, 58, 138, 0.2); padding: 20px; border-radius: 12px; display: flex; flex-direction: column; gap: 12px;">
        <div class="detail-label" style="color: var(--primary); font-weight: 700; display: flex; justify-content: space-between; align-items: center;">
          <span>테이블 메모 (기본설명)</span>
        </div>
        <textarea id="drawer-table-memo-txt" style="width: 100%; min-height: 100px; padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13px; resize: vertical; outline: none;" placeholder="테이블 관련 메모를 입력하세요..."></textarea>
        
        <!-- C -->
        <div class="detail-label" style="color: #c2410c; font-weight: 700; margin-top: 8px;">Create (생성 시점) 메모</div>
        <textarea id="drawer-c-memo-txt" style="width: 100%; min-height: 80px; padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13px; resize: vertical; outline: none;" placeholder="데이터 생성(Insert) 시점의 특징, 조건 등을 기록하세요..."></textarea>

        <!-- U -->
        <div class="detail-label" style="color: #15803d; font-weight: 700; margin-top: 8px;">Update (수정) 메모</div>
        <textarea id="drawer-u-memo-txt" style="width: 100%; min-height: 80px; padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13px; resize: vertical; outline: none;" placeholder="데이터 수정(Update) 시점의 비즈니스 조건을 기록하세요..."></textarea>

        <!-- D -->
        <div class="detail-label" style="color: #b91c1c; font-weight: 700; margin-top: 8px;">Delete (삭제) 메모</div>
        <textarea id="drawer-d-memo-txt" style="width: 100%; min-height: 80px; padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13px; resize: vertical; outline: none;" placeholder="데이터 삭제(Delete/Delete flag) 시점의 조건을 기록하세요..."></textarea>

        <!-- R -->
        <div class="detail-label" style="color: #1d4ed8; font-weight: 700; margin-top: 8px;">Read (조회) 메모</div>
        <textarea id="drawer-r-memo-txt" style="width: 100%; min-height: 80px; padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13px; resize: vertical; outline: none;" placeholder="조회(Select) 시점의 주요 정합성 기준이나 읽기 시나리오를 기록하세요..."></textarea>

        <div style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px;">
          <span id="drawer-save-status" style="font-size: 11px; color: var(--text-muted); align-self: center; margin-right: auto;">포커스 아웃 시 자동 저장</span>
          <button id="drawer-save-btn" class="action-btn btn-primary" style="padding: 8px 18px; font-size: 13px; border-radius: 6px; cursor: pointer; background: var(--primary-accent); color: white; border: none;">저장</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Toast Notification -->
<div class="toast" id="toast-msg">자동 저장되었습니다.</div>

<script>
const TABLES = {table_list_json};

TABLES.forEach(tbl => {{
  tbl.starred = localStorage.getItem("star:table:" + tbl.table_name) === "true" || tbl.starred || false;
  tbl.color = localStorage.getItem("color:table:" + tbl.table_name) || tbl.color || "none";
  const localSortOrder = localStorage.getItem("sortOrder:table:" + tbl.table_name);
  if (localSortOrder !== null && localSortOrder !== "") {{
    const parsed = parseInt(localSortOrder);
    tbl.sort_order = isNaN(parsed) ? 9999 : parsed;
  }} else if (tbl.sort_order === undefined) {{
    tbl.sort_order = 9999;
  }}
  
  // Load CUDR memos from server to localStorage (always overwrite to show latest SQL-parsed source-based details)
  if (tbl.memo_c) localStorage.setItem("memo:c:table:" + tbl.table_name, tbl.memo_c);
  if (tbl.memo_u) localStorage.setItem("memo:u:table:" + tbl.table_name, tbl.memo_u);
  if (tbl.memo_d) localStorage.setItem("memo:d:table:" + tbl.table_name, tbl.memo_d);
  if (tbl.memo_r) localStorage.setItem("memo:r:table:" + tbl.table_name, tbl.memo_r);
}});

// Initialize sort queue on page load
document.addEventListener("DOMContentLoaded", () => {{
  renderSortQueueUI();
}});

let currentTable = null;
let searchKeyword = "";
let includeTableSearch = true;
let includeColumnSearch = true;
let includeMemoSearch = true;
let includeRelationSearch = true;
let includeGuideSearch = true;

// 중요 컬럼명 정의 (하이라이트 표시)
const SPECIAL_COLUMNS = ["SET_FG", "PROC_FG", "RETURN_FG", "PROC_YN", "STOCK_YN"];

function escHtml(str) {{
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}}

function renderMarkdown(text) {{
  if (!text) return "";
  try {{
    return marked.parse(text);
  }} catch (e) {{
    return escHtml(text)
      .replace(/\\\\\\\\n/g, "<br>")
      .replace(/### (.*)/g, "<h3>$1</h3>")
      .replace(/## (.*)/g, "<h2>$1</h2>")
      .replace(/# (.*)/g, "<h1>$1</h1>")
      .replace(/`(.*?)`/g, "<code>$1</code>");
  }}
}}

// 텍스트 매칭 하이라이트 함수
function highlight(text, keyword) {{
  if (!keyword) return escHtml(text);
  const escapedKeyword = keyword.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
  const regex = new RegExp(`(${{escapedKeyword}})`, 'gi');
  return escHtml(text).replace(regex, '<mark class="search-match">$1</mark>');
}}

// 왼쪽 테이블 목록 렌더링
function renderTableList() {{
  const container = document.getElementById("table-list-container");
  container.innerHTML = "";
  
  const kw = searchKeyword.toLowerCase().trim();
  let filterCount = 0;
  let firstMatch = null;
  let isCurrentTableMatched = false;
  
  const matchedTables = [];
  
  TABLES.forEach(tbl => {{
    const tName = (tbl.table_name || "").toLowerCase();
    const tComment = (tbl.comment || "").toLowerCase();
    
    let isMatch = !kw;
    
    if (kw) {{
      // 테이블명 & 테이블 설명 매칭
      if (includeTableSearch && (tName.includes(kw) || tComment.includes(kw))) {{
        isMatch = true;
      }}
      
      // 테이블 메모 매칭
      if (!isMatch && includeMemoSearch) {{
        const tMemo = (localStorage.getItem("memo:table:" + tbl.table_name) || tbl.custom_memo || "").toLowerCase();
        if (tMemo.includes(kw)) {{
          isMatch = true;
        }}
      }}
      
      // 컬럼명 / 컬럼 설명 / 컬럼 메모 매칭
      if (!isMatch) {{
        isMatch = tbl.columns.some(col => {{
          let colMatch = false;
          if (includeColumnSearch) {{
            colMatch = (col.column_name || "").toLowerCase().includes(kw) || (col.comment || "").toLowerCase().includes(kw);
          }}
          if (!colMatch && includeMemoSearch) {{
            const cMemo = (localStorage.getItem("memo:col:" + tbl.table_name + ":" + col.column_name) || col.custom_memo || "").toLowerCase();
            colMatch = cMemo.includes(kw);
          }}
          return colMatch;
        }});
      }}

      // 연관 화면 배 연관 배치 매칭
      if (!isMatch && includeRelationSearch) {{
        const screenMatch = tbl.screens && tbl.screens.some(scr => 
          (scr.id || "").toLowerCase().includes(kw) || 
          (scr.name && scr.name.toLowerCase().includes(kw))
        );
        const batchMatch = tbl.batches && tbl.batches.some(bat => 
          (bat.id || "").toLowerCase().includes(kw) || 
          (bat.name && bat.name.toLowerCase().includes(kw))
        );
        isMatch = screenMatch || batchMatch;
      }}
      
      // 연관 가이드 매칭
      if (!isMatch && includeGuideSearch) {{
        const tableGuideKey = "guide:table:" + tbl.table_name;
        const currentTableGuideStr = localStorage.getItem(tableGuideKey) || tbl.manual_guide || "";
        const mGuides = currentTableGuideStr ? currentTableGuideStr.split(",").map(x => x.trim()).filter(Boolean) : [];
        const hasTableGuideMatch = mGuides.some(g => g.toLowerCase().includes(kw)) || 
                                   (tbl.guides && tbl.guides.some(g => g.toLowerCase().includes(kw)));
        
        if (hasTableGuideMatch) {{
          isMatch = true;
        }} else {{
          isMatch = tbl.columns.some(col => {{
            const colGuideKey = "guide:col:" + tbl.table_name + ":" + col.column_name;
            const currentColGuide = localStorage.getItem(colGuideKey) || col.manual_guide || "";
            return currentColGuide.toLowerCase().includes(kw) || 
                   (col.guides && col.guides.some(g => g.toLowerCase().includes(kw)));
          }});
        }}
      }}
    }}
    
    if (isMatch) {{
      matchedTables.push(tbl);
    }}
  }});

  // Sort matchedTables with multi-sort queue
  let sortQueue = [];
  try {{
    sortQueue = JSON.parse(localStorage.getItem("sortQueue"));
  }} catch(e) {{}}
  if (!Array.isArray(sortQueue)) {{
    sortQueue = ["custom", "starred"];
  }}
  
  matchedTables.sort((a, b) => {{
    for (let criterion of sortQueue) {{
      if (criterion === "starred") {{
        const aStar = a.starred ? 1 : 0;
        const bStar = b.starred ? 1 : 0;
        if (aStar !== bStar) return bStar - aStar;
      }} else if (criterion === "custom") {{
        const aOrder = a.sort_order !== undefined ? a.sort_order : 9999;
        const bOrder = b.sort_order !== undefined ? b.sort_order : 9999;
        if (aOrder !== bOrder) return aOrder - bOrder;
      }} else if (criterion === "color") {{
        const colorOrder = {{ "red": 1, "orange": 2, "yellow": 3, "green": 4, "blue": 5, "purple": 6, "none": 7 }};
        const aColorOrder = colorOrder[a.color || "none"] || 7;
        const bColorOrder = colorOrder[b.color || "none"] || 7;
        if (aColorOrder !== bColorOrder) return aColorOrder - bColorOrder;
      }}
    }}
    return a.table_name.localeCompare(b.table_name);
  }});

  matchedTables.forEach(tbl => {{
    filterCount++;
    if (!firstMatch) firstMatch = tbl;
    if (currentTable && currentTable.table_name === tbl.table_name) {{
      isCurrentTableMatched = true;
    }}
    
    const tMemo = localStorage.getItem("memo:table:" + tbl.table_name) || tbl.custom_memo || "";
    const div = document.createElement("div");
    div.className = "table-item";
    div.dataset.tableName = tbl.table_name;
    div.title = tbl.table_name + (tbl.comment ? " - " + tbl.comment : "") + (tMemo ? " [메모: " + tMemo + "]" : "");
    if (currentTable && currentTable.table_name === tbl.table_name) {{
      div.classList.add("active");
    }}
    
    let descParts = [];
    if (tbl.comment) {{
      descParts.push(highlight(tbl.comment, searchKeyword));
    }} else {{
      descParts.push('<span style="color:#cbd5e1;">설명 없음</span>');
    }}
    if (tMemo) {{
      descParts.push(`<span class="sidebar-memo-btn" style="cursor: pointer; text-decoration: underline; color: #b45309; font-weight: 500;" onclick="event.stopPropagation(); openDrawerByName('${{tbl.table_name}}')">📝 ${{highlight(tMemo, searchKeyword)}}</span>`);
    }}
    const highlightedComment = `(${{descParts.join(' | ')}})`;

    // Star character
    const starChar = tbl.starred ? '<span style="color:#f59e0b; margin-right:4px;">★</span>' : '';
    // Color indicator dot
    const colorDot = tbl.color && tbl.color !== "none" 
      ? `<span class="color-dot color-${{tbl.color}}"></span>`
      : '';
    
    div.innerHTML = `
      <div style="display:flex; align-items:center; gap:4px; flex-shrink:0;">
        ${{colorDot}}
        ${{starChar}}
      </div>
      <span class="t-name">${{highlight(tbl.table_name, searchKeyword)}}</span>
      <span class="t-desc">${{highlightedComment}}</span>
    `;
    
    div.onclick = () => selectTable(tbl, true, false);
    container.appendChild(div);
  }});
  
  document.getElementById("filter-count").textContent = filterCount;

  function openDrawerByName(tname) {{
    const tbl = TABLES.find(x => x.table_name === tname);
    if (tbl) {{
      selectTable(tbl, true, true);
    }}
  }}
  window.openDrawerByName = openDrawerByName;

  function toggleStar(tname) {{
    const tbl = TABLES.find(x => x.table_name === tname);
    if (tbl) {{
      tbl.starred = !tbl.starred;
      localStorage.setItem("star:table:" + tname, tbl.starred);
      
      const starBtn = document.getElementById("star-btn-" + tname);
      if (starBtn) {{
        starBtn.style.color = tbl.starred ? '#f59e0b' : '#cbd5e1';
        starBtn.textContent = tbl.starred ? '★' : '☆';
      }}
      
      renderTableList();
      showToast(tbl.starred ? "중요 테이블로 등록되었습니다." : "중요 테이블 등록이 해제되었습니다.");
    }}
  }}
  window.toggleStar = toggleStar;

  function changeColor(tname, color) {{
    const tbl = TABLES.find(x => x.table_name === tname);
    if (tbl) {{
      tbl.color = color;
      localStorage.setItem("color:table:" + tname, color);
      renderTableList();
      showToast("그룹 색상이 변경되었습니다.");
    }}
  }}
  window.changeColor = changeColor;

  function changeSortOrder(tname, val) {{
    const tbl = TABLES.find(x => x.table_name === tname);
    if (tbl) {{
      const parsed = parseInt(val);
      const num = isNaN(parsed) ? 9999 : parsed;
      tbl.sort_order = num;
      localStorage.setItem("sortOrder:table:" + tname, val);
      renderTableList();
      showToast("정렬 순서가 업데이트되었습니다.");
    }}
  }}
  window.changeSortOrder = changeSortOrder;

  function renderSortQueueUI() {{
    const container = document.getElementById("sort-queue-container");
    if (!container) return;
    
    let sortQueue = [];
    try {{
      sortQueue = JSON.parse(localStorage.getItem("sortQueue"));
    }} catch(e) {{}}
    if (!Array.isArray(sortQueue)) {{
      sortQueue = ["custom", "starred"];
      localStorage.setItem("sortQueue", JSON.stringify(sortQueue));
    }}
    
    const allOptions = [
      {{ id: "custom", name: "사용자지정" }},
      {{ id: "starred", name: "즐겨찾기" }},
      {{ id: "color", name: "색상그룹" }}
    ];
    
    container.innerHTML = "";
    
    // Render active options in queue order
    sortQueue.forEach((qId, index) => {{
      const opt = allOptions.find(o => o.id === qId);
      if (opt) {{
        const badge = document.createElement("span");
        badge.className = "sort-queue-badge active";
        badge.style.cssText = "display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: var(--primary-accent); color: white; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; user-select: none; transition: all 0.15s ease;";
        badge.innerHTML = `${{opt.name}} <span style="background: rgba(255,255,255,0.3); color: white; font-size: 10px; width: 14px; height: 14px; display: inline-flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 700;">${{index + 1}}</span>`;
        badge.onclick = () => toggleSortQueue(qId);
        container.appendChild(badge);
      }}
    }});
    
    // Render inactive options
    allOptions.forEach(opt => {{
      if (!sortQueue.includes(opt.id)) {{
        const badge = document.createElement("span");
        badge.className = "sort-queue-badge";
        badge.style.cssText = "display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: #f1f5f9; color: var(--text-muted); border: 1px solid var(--border); border-radius: 6px; font-size: 11px; font-weight: 500; cursor: pointer; user-select: none; transition: all 0.15s ease;";
        badge.innerHTML = `${{opt.name}}`;
        badge.onclick = () => toggleSortQueue(opt.id);
        container.appendChild(badge);
      }}
    }});
  }}
  window.renderSortQueueUI = renderSortQueueUI;
  
  function toggleSortQueue(qId) {{
    let sortQueue = [];
    try {{
      sortQueue = JSON.parse(localStorage.getItem("sortQueue"));
    }} catch(e) {{}}
    if (!Array.isArray(sortQueue)) sortQueue = [];
    
    if (sortQueue.includes(qId)) {{
      sortQueue = sortQueue.filter(id => id !== qId);
    }} else {{
      sortQueue.push(qId);
    }}
    localStorage.setItem("sortQueue", JSON.stringify(sortQueue));
    renderSortQueueUI();
    renderTableList();
  }}
  window.toggleSortQueue = toggleSortQueue;
  
  function clearSortQueue() {{
    localStorage.setItem("sortQueue", JSON.stringify([]));
    renderSortQueueUI();
    renderTableList();
  }}
  window.clearSortQueue = clearSortQueue;
  
  document.getElementById("filter-count").textContent = filterCount;
  
  // 현재 선택된 테이블이 필터링 결과에 매칭되는지 확인 후 자동 선택란은/갱신 처리
  if (kw) {{
    if (isCurrentTableMatched && currentTable) {{
      // 현재 선택된 테이블을 다시 렌더링하여 하이라이트를 즉시 업데이트
      selectTable(currentTable, false);
    }} else if (firstMatch) {{
      // 현재 선택된 테이블이 필터링 결과에 없다면 처 번째 매치된 테이블 자동 선택란은 배 스크롤
      selectTable(firstMatch, true);
    }} else {{
      // 검색 결과가 없는 경우 비 안내 메시지 출력
      document.getElementById("content").innerHTML = `
        <div id="no-selection">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p>검색 결과 일치하는 테이블이 없습니다.</p>
        </div>
      `;
      currentTable = null;
    }}
  }} else {{
    // 검색어가 비 경우
    if (currentTable) {{
      selectTable(currentTable, false);
    }} else if (firstMatch) {{
      selectTable(firstMatch, false);
    }}
  }}
}}

// 인덱스 섹션 토글
function toggleIndexSection() {{
  const content = document.getElementById("index-section-content");
  const arrow = document.getElementById("index-toggle-arrow");
  if (content.style.display === "none") {{
    content.style.display = "block";
    arrow.textContent = "접기";
  }} else {{
    content.style.display = "none";
    arrow.textContent = "펼치기";
  }}
}}

// 테이블 상세 조회
function selectTable(tbl, shouldScroll = true, openDrawerFlag = false) {{
  currentTable = tbl;

  if (openDrawerFlag) {{
    openDrawer(tbl);
  }}
  
  // 사이드바 active 상태 갱신
  document.querySelectorAll(".table-item").forEach(item => {{
    if (item.dataset.tableName === tbl.table_name) {{
      item.classList.add("active");
    }} else {{
      item.classList.remove("active");
    }}
  }});

  const content = document.getElementById("content");
  content.innerHTML = "";

  // 기본 정보 카드
  const detailCard = document.createElement("div");
  detailCard.className = "detail-card";
  
  // 컬럼 바인딩
  const colRows = tbl.columns.map(col => {{
    const isSpecial = SPECIAL_COLUMNS.includes(col.column_name.toUpperCase());
    const isPk = tbl.indexes.some(idx => idx.index_name.toLowerCase().includes('pk') && idx.index_def.toLowerCase().includes(col.column_name.toLowerCase()));
    
    let badges = "";
    if (isPk) badges += '<span class="badge pk">PK</span> ';
    if (col.nullable === 'NO') badges += '<span class="badge nn">NOT NULL</span> ';
    if (isSpecial) badges += `<span class="badge special">${{col.column_name}}</span> `;

    // 컬럼 설명에 강조 단어가 있는 경우 처리 (예: SET_FG 설명 등)
    let formattedComment = escHtml(col.comment);
    if (col.column_name.toUpperCase() === "SET_FG") {{
      formattedComment = "<b>상품 구분</b> (0: 일반 단품, 2: 레시피 원자재 분해 대상, 3: 세트 구성품 분해 대상) " + formattedComment;
    }} else if (col.column_name.toUpperCase() === "PROC_FG") {{
      formattedComment = "<b>진행 상태</b> (0: 등록/반려, 1: 입출확정, 2: 이입확정/최종확정, 3: 본사확정) " + formattedComment;
    }}

    const rowClass = isSpecial ? 'class="highlight-row"' : '';

    const colMemoKey = "memo:col:" + tbl.table_name + ":" + col.column_name;
    const currentColMemo = localStorage.getItem(colMemoKey) || col.custom_memo || "";

    const memoBoxHtml = `
      <div class="col-memo-box" style="margin-top: 6px; padding-top: 4px; border-top: 1px dotted var(--border); font-size: 12px; color: var(--text-muted);">
        <span style="font-weight: 600;">메모:</span>
        <span id="memo-col-val-${{col.column_name}}" style="cursor: pointer; text-decoration: underline dotted;" onclick="editColMemo('${{tbl.table_name}}', '${{col.column_name}}')">${{currentColMemo || '작성 필요...'}}</span>
      </div>
    `;

    // 연관 가이드 확인
    const colGuideKey = "guide:col:" + tbl.table_name + ":" + col.column_name;
    const currentColGuide = localStorage.getItem(colGuideKey) || col.manual_guide || "";
    
    const allColGuides = [];
    if (currentColGuide) {{
      allColGuides.push(currentColGuide);
    }}
    if (col.guides) {{
      col.guides.forEach(g => {{
        if (!allColGuides.includes(g)) allColGuides.push(g);
      }});
    }}

    const guideBadgesHtml = allColGuides.map(g => {{
      const cleanName = g.replace("_QaReport.md", "").replace("_DataInput.md", "").replace("_DataFlow_Guide.md", "").replace(".md", "");
      return `<a href="file:///D:/hmTest/backoffice/QaReport/${{g}}" class="badge" style="background-color: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; font-size: 11px; text-transform: none; text-decoration: none; display: inline-block; margin-bottom: 4px; padding: 3px 6px; border-radius: 4px; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${{g}}" target="_blank">${{cleanName}}</a>`;
    }}).join(' ');

    return `
      <tr ${{rowClass}} data-column-name="${{col.column_name.toLowerCase()}}">
        <td class="col-name">${{highlight(col.column_name, searchKeyword)}}</td>
        <td>${{badges}}</td>
        <td class="col-type">${{escHtml(col.data_type)}}</td>
        <td class="default-val">${{escHtml(col.default_value)}}</td>
        <td class="col-comment">
          ${{highlight(formattedComment, searchKeyword)}}
          ${{memoBoxHtml}}
        </td>
      </tr>
    `;
  }}).join('');

  // 인덱스 카드 바인딩
  const indexHtml = tbl.indexes.length
    ? tbl.indexes.map(idx => `
        <div class="index-card" onclick="toggleIndexHighlight(this)" data-index-def="${{escHtml(idx.index_def)}}">
          <span class="idx-name">${{escHtml(idx.index_name)}}</span>
          <span style="color:#64748b">${{escHtml(idx.index_def)}}</span>
        </div>
      `).join('')
    : '<div class="empty">정의된 인덱스가 없습니다.</div>';

  // 화면 배 배치 링크 구성
  const screenBadges = tbl.screens && tbl.screens.length
    ? tbl.screens.map(scr => `<span class="badge screen-id" title="백오피스 화면: ${{scr.name || ''}}">${{scr.id}}${{scr.name ? ` (${{scr.name}})` : ''}}</span>`).join(' ')
    : '<span style="color:var(--text-muted);font-size:12px;">연관 화면 없음</span>';

  const batchBadges = tbl.batches && tbl.batches.length
    ? tbl.batches.map(bat => `<span class="badge batch-id" title="배치 작업: ${{bat.name || ''}}">${{bat.id}}${{bat.name ? ` (${{bat.name}})` : ''}}</span>`).join(' ')
    : '<span style="color:var(--text-muted);font-size:12px;">연관 배치 없음</span>';

  // 테이블 레벨 가이드 구성
  const tableGuideKey = "guide:table:" + tbl.table_name;
  const currentTableGuideStr = localStorage.getItem(tableGuideKey) || tbl.manual_guide || "";
  const manualGuides = currentTableGuideStr ? currentTableGuideStr.split(",").map(x => x.trim()).filter(Boolean) : [];
  
  const allTableGuides = [];
  manualGuides.forEach(g => {{
    if (!allTableGuides.includes(g)) allTableGuides.push(g);
  }});
  if (tbl.guides) {{
    tbl.guides.forEach(g => {{
      if (!allTableGuides.includes(g)) allTableGuides.push(g);
    }});
  }}

  const tableGuideBadges = allTableGuides.length
    ? allTableGuides.map(g => {{
        const cleanName = g.replace("_QaReport.md", "").replace("_DataInput.md", "").replace("_DataFlow_Guide.md", "").replace(".md", "");
        return `<a href="file:///D:/hmTest/backoffice/QaReport/${{g}}" class="badge" style="background-color: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; font-size: 11px; text-transform: none; text-decoration: none; padding: 3px 6px; border-radius: 4px; display: inline-block;" title="${{g}}" target="_blank">${{cleanName}}</a>`;
      }}).join(' ')
    : '<span style="color:var(--text-muted);font-size:12px;">연관 가이드 없음</span>';

  // Load custom table memo from localStorage or fallback
  const tableMemoKey = "memo:table:" + tbl.table_name;
  const currentTableMemo = localStorage.getItem(tableMemoKey) || tbl.custom_memo || "";
  const currentCMemo = localStorage.getItem("memo:c:table:" + tbl.table_name) || "";
  const currentUMemo = localStorage.getItem("memo:u:table:" + tbl.table_name) || "";
  const currentDMemo = localStorage.getItem("memo:d:table:" + tbl.table_name) || "";
  const currentRMemo = localStorage.getItem("memo:r:table:" + tbl.table_name) || "";

  const cudrMemosHtml = `
    <div style="background: white; border: 1px solid var(--border); border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); width: 100%;">
      <div style="font-weight: 700; color: var(--primary); font-size: 15px; margin-bottom: 16px; border-bottom: 2px solid var(--border); padding-bottom: 8px; display: flex; align-items: center; gap: 8px;">
        CUDR 시점별 상세 메모 한눈에 보기
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; width: 100%;">
        <!-- Create Card -->
        <div style="background: #fff7ed; border: 1px solid #fdba74; border-radius: 8px; padding: 16px; display: flex; flex-direction: column; min-height: 250px; max-height: 350px;">
          <div style="font-weight: 700; color: #c2410c; font-size: 14px; border-bottom: 1px solid #fed7aa; padding-bottom: 6px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;">
            <span>Create (생성 시점)</span>
            <button onclick="openDrawer(currentTable)" style="padding: 2px 8px; font-size: 11px; background: transparent; border: 1px solid #c2410c; color: #c2410c; border-radius: 4px; cursor: pointer;">편집</button>
          </div>
          <div id="c-memo-val-tab-${{tbl.table_name}}" style="font-size: 12.5px; color: #9a3412; white-space: pre-wrap; line-height: 1.5; overflow-y: auto; flex-grow: 1;">${{currentCMemo || '등록된 메모가 없습니다.'}}</div>
        </div>
        
        <!-- Update Card -->
        <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 16px; display: flex; flex-direction: column; min-height: 250px; max-height: 350px;">
          <div style="font-weight: 700; color: #15803d; font-size: 14px; border-bottom: 1px solid #bbf7d0; padding-bottom: 6px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;">
            <span>Update (수정 시점)</span>
            <button onclick="openDrawer(currentTable)" style="padding: 2px 8px; font-size: 11px; background: transparent; border: 1px solid #15803d; color: #15803d; border-radius: 4px; cursor: pointer;">편집</button>
          </div>
          <div id="u-memo-val-tab-${{tbl.table_name}}" style="font-size: 12.5px; color: #166534; white-space: pre-wrap; line-height: 1.5; overflow-y: auto; flex-grow: 1;">${{currentUMemo || '등록된 메모가 없습니다.'}}</div>
        </div>
        
        <!-- Delete Card -->
        <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 16px; display: flex; flex-direction: column; min-height: 250px; max-height: 350px;">
          <div style="font-weight: 700; color: #b91c1c; font-size: 14px; border-bottom: 1px solid #fecaca; padding-bottom: 6px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;">
            <span>Delete (삭제 시점)</span>
            <button onclick="openDrawer(currentTable)" style="padding: 2px 8px; font-size: 11px; background: transparent; border: 1px solid #b91c1c; color: #b91c1c; border-radius: 4px; cursor: pointer;">편집</button>
          </div>
          <div id="d-memo-val-tab-${{tbl.table_name}}" style="font-size: 12.5px; color: #991b1b; white-space: pre-wrap; line-height: 1.5; overflow-y: auto; flex-grow: 1;">${{currentDMemo || '등록된 메모가 없습니다.'}}</div>
        </div>
        
        <!-- Read Card -->
        <div style="background: #eff6ff; border: 1px solid #93c5fd; border-radius: 8px; padding: 16px; display: flex; flex-direction: column; min-height: 250px; max-height: 350px;">
          <div style="font-weight: 700; color: #1d4ed8; font-size: 14px; border-bottom: 1px solid #bfdbfe; padding-bottom: 6px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;">
            <span>Read (조회 시점)</span>
            <button onclick="openDrawer(currentTable)" style="padding: 2px 8px; font-size: 11px; background: transparent; border: 1px solid #1d4ed8; color: #1d4ed8; border-radius: 4px; cursor: pointer;">편집</button>
          </div>
          <div id="r-memo-val-tab-${{tbl.table_name}}" style="font-size: 12.5px; color: #1e40af; white-space: pre-wrap; line-height: 1.5; overflow-y: auto; flex-grow: 1;">${{currentRMemo || '등록된 메모가 없습니다.'}}</div>
        </div>
      </div>
    </div>
  `;

  const isStarred = tbl.starred;
  const color = tbl.color;
  const sortOrder = tbl.sort_order !== undefined && tbl.sort_order !== 9999 ? tbl.sort_order : "";

  let memoHtml = "";
  if (currentTableMemo) {{
    memoHtml = `
      <div class="memo-markdown-container" style="background-color: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 16px 20px; font-size: 14px; line-height: 1.6; color: #451a03;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1.5px solid #fde68a; padding-bottom: 6px;">
          <span style="font-weight: 700; font-size: 14px; color: #b45309; display: flex; align-items: center; gap: 6px;">테이블 상세 메모 및 관계도</span>
          <button class="memo-edit-btn" onclick="openDrawer(currentTable)" style="padding: 2px 8px; font-size: 11px; background: transparent; border: 1px solid #d97706; color: #d97706; border-radius: 4px; cursor: pointer;">편집하기</button>
        </div>
        <div class="markdown-content">${{renderMarkdown(currentTableMemo)}}</div>
      </div>
    `;
  }}

  const guideCardsHtml = allTableGuides.length
    ? allTableGuides.map(g => {{
        const cleanName = g.replace("_QaReport.md", "").replace("_DataInput.md", "").replace("_DataFlow_Guide.md", "").replace(".md", "");
        const isManual = manualGuides.includes(g);
        return `
          <div class="guide-card">
            <div style="display: flex; justify-content: space-between; align-items: start; gap: 12px; width: 100%;">
              <div style="display: flex; align-items: start; gap: 12px; min-width: 0;">
                <span style="font-size: 24px; line-height: 1;">📄</span>
                <div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;">
                  <span style="font-weight: 700; color: var(--text-main); font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${{g}}">${{cleanName}}</span>
                  <span style="font-size: 11.5px; color: var(--text-muted); font-family: monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${{g}}</span>
                </div>
              </div>
              ${{isManual ? `
                <button onclick="removeTableGuide('${{tbl.table_name}}', '${{g}}')" style="background: transparent; border: none; color: #ef4444; cursor: pointer; padding: 4px; display: inline-flex; align-items: center; justify-content: center; font-size: 16px; border-radius: 4px; transition: all 0.15s ease;" title="연관 가이드 링크 제거" onmouseover="this.style.backgroundColor='#fee2e2'" onmouseout="this.style.backgroundColor='transparent'">
                  제거
                </button>
              ` : ''}}
            </div>
            <div style="display: flex; justify-content: flex-end; border-top: 1px solid #f1f5f9; padding-top: 12px; margin-top: 4px;">
              <a href="file:///D:/hmTest/backoffice/QaReport/${{g}}" target="_blank" class="guide-card-btn">
                가이드 열기
              </a>
            </div>
          </div>
        `;
      }}).join('')
    : `
      <div style="grid-column: 1 / -1; color: var(--text-muted); font-size: 13px; text-align: center; padding: 48px 0; border: 1px dashed var(--border); border-radius: 8px; background: white;">
        등록되었거나 검색된 연관 가이드가 없습니다.
      </div>
    `;

  const activeTab = localStorage.getItem("activeTab") || "fields";

  const relatedTablesList = tbl.related_tables || [];
  let relatedRowsHtml = "";
  if (relatedTablesList.length === 0) {{
    relatedRowsHtml = `
      <tr>
        <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 32px; background: white;">
          등록된 관련 테이블이 없습니다. 상단 탭을 이용하여 관련 테이블을 추가해 보세요.
        </td>
      </tr>
    `;
  }} else {{
    relatedRowsHtml = relatedTablesList.map(rel => {{
      const relTblObj = TABLES.find(t => t.table_name === rel.table_name);
      const dbComment = relTblObj ? (relTblObj.comment || '') : '';
      return `
        <tr style="border-bottom: 1px solid var(--border); background: white;">
          <td style="padding: 10px 12px; font-family: monospace; font-weight: 600;">
            <a href="#" onclick="selectTableByName('${{rel.table_name}}'); return false;" style="color: var(--primary-accent); text-decoration: none;">${{rel.table_name.toUpperCase()}}</a>
          </td>
          <td style="padding: 10px 12px; color: var(--text-muted);">${{escHtml(dbComment)}}</td>
          <td style="padding: 6px 12px;">
            <textarea onchange="updateRelatedTableDesc('${{tbl.table_name}}', '${{rel.table_name}}', this.value)" oninput="this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px';" style="width: 100%; min-height: 38px; padding: 6px 8px; border: 1px solid transparent; background: transparent; border-radius: 4px; font-size: 12.5px; font-family: inherit; line-height: 1.45; resize: vertical; outline: none; box-sizing: border-box; display: block; overflow-y: hidden;" onfocus="this.style.border='1px solid var(--primary-accent)'; this.style.background='white';" onblur="this.style.border='1px solid transparent'; this.style.background='transparent';">${{escHtml(rel.description || '')}}</textarea>
          </td>
          <td style="padding: 10px 12px; text-align: center;">
            <button onclick="deleteRelatedTable('${{tbl.table_name}}', '${{rel.table_name}}')" style="background: #fee2e2; color: #ef4444; border: 1px solid #fecaca; padding: 4px 10px; border-radius: 6px; font-size: 11.5px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.backgroundColor='#fca5a5'" onmouseout="this.style.backgroundColor='#fee2e2'">삭제</button>
          </td>
        </tr>
      `;
    }}).join('');
  }}

  detailCard.innerHTML = `
    <div class="detail-header">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 24px; width: 100%;">
        <div class="title-row" style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px;">
          <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
            <h2 style="font-family: monospace; font-size: 22px; font-weight: 700; color: var(--primary);">${{highlight(tbl.table_name, searchKeyword)}}</h2>
            
            <button onclick="toggleStar('${{tbl.table_name}}')" id="star-btn-${{tbl.table_name}}" style="background: none; border: none; font-size: 20px; color: ${{isStarred ? '#f59e0b' : '#cbd5e1'}}; cursor: pointer; outline: none; padding: 0 4px; display: inline-flex; align-items: center;" title="중요 테이블 즐겨찾기">
              ${{isStarred ? '★' : '☆'}}
            </button>
            
            <div style="display: inline-flex; align-items: center; gap: 4px; margin-left: 8px;">
              <span style="font-size: 11px; color: var(--text-muted); font-weight: 600;">그룹 색상:</span>
              <select onchange="changeColor('${{tbl.table_name}}', this.value)" style="font-size: 11.5px; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border); outline: none; background: white; cursor: pointer;">
                <option value="none" ${{color === 'none' ? 'selected' : ''}}>없음</option>
                <option value="red" ${{color === 'red' ? 'selected' : ''}} style="color:#ef4444; font-weight:bold;">빨강</option>
                <option value="orange" ${{color === 'orange' ? 'selected' : ''}} style="color:#f97316; font-weight:bold;">주황</option>
                <option value="yellow" ${{color === 'yellow' ? 'selected' : ''}} style="color:#eab308; font-weight:bold;">노랑</option>
                <option value="green" ${{color === 'green' ? 'selected' : ''}} style="color:#22c55e; font-weight:bold;">초록</option>
                <option value="blue" ${{color === 'blue' ? 'selected' : ''}} style="color:#3b82f6; font-weight:bold;">파랑</option>
                <option value="purple" ${{color === 'purple' ? 'selected' : ''}} style="color:#a855f7; font-weight:bold;">보라</option>
              </select>
            </div>
            
            <div style="display: inline-flex; align-items: center; gap: 4px; margin-left: 8px;">
              <span style="font-size: 11px; color: var(--text-muted); font-weight: 600;">정렬 순서:</span>
              <input type="number" value="${{sortOrder}}" onchange="changeSortOrder('${{tbl.table_name}}', this.value)" style="width: 50px; font-size: 11.5px; padding: 2px 4px; border-radius: 4px; border: 1px solid var(--border); outline: none; text-align: center;" min="0" max="9999" title="사용자 지정 순서 정렬을 위한 각가중치 (낮을수록 상단)">
            </div>
          </div>
          <span class="comment" style="display: block; margin-top: 4px;">${{highlight(tbl.comment || '테이블 설명 없음', searchKeyword)}}</span>
        </div>
        <div id="table-memo-container" class="memo-container-mini" style="cursor: pointer; width: 260px; height: 56px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between;" onclick="openDrawer(currentTable)">
          <div class="memo-title" style="display: flex; justify-content: space-between; align-items: center; gap: 8px; font-weight: 700; color: #854d0e; font-size: 11px; margin-bottom: 2px;">
            <span>📝 테이블 메모</span>
            <button class="memo-edit-btn" style="padding: 1px 4px; font-size: 10px;" onclick="event.stopPropagation(); openDrawer(currentTable)">편집</button>
          </div>
          <div class="memo-content" id="table-memo-val-${{tbl.table_name}}" style="font-size: 11.5px; color: #78350f; max-height: 36px; overflow-y: auto; white-space: pre-wrap; line-height: 1.3;">${{currentTableMemo || '등록된 메모가 없습니다.'}}</div>
        </div>
      </div>
    </div>
    
    <div class="detail-body">
      <!-- 탭 네비게이션 -->
      <div class="detail-tabs">
        <button id="tab-btn-fields" class="tab-btn ${{activeTab === 'fields' ? 'active' : ''}}" onclick="switchTab('fields')">📋 필드 및 인덱스 명세</button>
        <button id="tab-btn-related" class="tab-btn ${{activeTab === 'related' ? 'active' : ''}}" onclick="switchTab('related')">🔗 관련 테이블 (${{tbl.related_tables ? tbl.related_tables.length : 0}})</button>
        <button id="tab-btn-memo" class="tab-btn ${{activeTab === 'memo' ? 'active' : ''}}" onclick="switchTab('memo')">📝 상세 메모 및 연관 관계</button>
        <button id="tab-btn-cudrmemos" class="tab-btn ${{activeTab === 'cudrmemos' ? 'active' : ''}}" onclick="switchTab('cudrmemos')">💾 CUDR 시점별 메모</button>
        <button id="tab-btn-guides" class="tab-btn ${{activeTab === 'guides' ? 'active' : ''}}" onclick="switchTab('guides')">📄 연관 가이드 (${{allTableGuides.length}})</button>
      </div>

      <!-- 탭 콘텐츠 1: 필드 명세 -->
      <div id="tab-fields-content" class="tab-content" style="display: ${{activeTab === 'fields' ? 'flex' : 'none'}};">
        <div class="section-title" onclick="toggleIndexSection()" style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; user-select: none; margin-bottom: 8px; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 6px;">
          <span style="display: flex; align-items: center; gap: 6px;">
            <svg style="width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m0 0a2 2 0 01-2 2m2-2a2 2 0 00-2-2m0 0a2 2 0 00-2 2m2 0a2 2 0 01-2 2m0 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"></path>
            </svg>
            인덱스 명세 (Indexes)
          </span>
          <span id="index-toggle-arrow" style="font-size: 11px; color: var(--text-muted);">펼치기</span>
        </div>
        <div id="index-section-content" style="display: none; margin-bottom: 12px;">
          ${{indexHtml}}
        </div>

        <div class="section-title" style="margin-top: 8px; margin-bottom: 8px; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 6px;">
          <svg style="width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
          </svg>
          테이블 필드 명세 (Fields)
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th style="width: 20%">필드(컬럼)명</th>
                <th style="width: 15%">제약조건</th>
                <th style="width: 15%">데이터 타입</th>
                <th style="width: 10%">기본값</th>
                <th style="width: 40%">설명 (Comment)</th>
              </tr>
            </thead>
            <tbody>
              ${{colRows}}
            </tbody>
          </table>
        </div>
      </div>

      <!-- 탭 콘텐츠 1.5: 관련테이블 -->
      <div id="tab-related-content" class="tab-content" style="display: ${{activeTab === 'related' ? 'flex' : 'none'}}; flex-direction: column; overflow-y: auto; gap: 16px; padding-bottom: 20px;">
        <div style="font-size: 13.5px; color: var(--text-muted); font-weight: 500; display: flex; flex-direction: column; width: 100%; gap: 12px;">
          <span>이 테이블과 업무적/데이터베이스상 연관된 테이블 목록입니다. 테이블명을 클릭하면 해당 테이블 명세로 바로 이동합니다.</span>
          
          <!-- 관련 테이블 추가 탭 -->
          <div style="display: flex; gap: 8px; width: 100%; align-items: center; background: #f8fafc; border: 1px solid var(--border); padding: 12px; border-radius: 8px; flex-wrap: wrap;">
            <span style="font-weight: 700; font-size: 13px; color: var(--text-main); margin-right: 4px;">연관 테이블 추가:</span>
            <select id="add-related-select" class="input-field" style="width: 220px; font-size: 13px; padding: 6px; border-radius: 6px; border: 1px solid var(--border);">
              <option value="">-- 테이블 선택란은 --</option>
              ${{TABLES.filter(t => t.table_name !== tbl.table_name).map(t => `<option value="${{t.table_name}}">${{t.table_name.toUpperCase()}} (${{t.comment || ''}})</option>`).join('')}}
            </select>
            <input type="text" id="add-related-desc" class="input-field" style="flex: 1; min-width: 200px; font-size: 13px; padding: 6px; border-radius: 6px; border: 1px solid var(--border);" placeholder="연관 관계 배 설명 입력...">
            <button onclick="addRelatedTable('${{tbl.table_name}}')" style="background: var(--primary-accent); color: white; border: none; padding: 6px 16px; border-radius: 6px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#1d4ed8'" onmouseout="this.style.background='var(--primary-accent)'">추가</button>
          </div>
        </div>

        <!-- 관련 테이블 목록 표 -->
        <div style="overflow-x: auto; width: 100%;">
          <table class="grid-table" style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; border: 1px solid var(--border);">
            <thead>
              <tr style="background: #f1f5f9; border-bottom: 2px solid var(--border);">
                <th style="padding: 10px 12px; font-weight: 600; width: 25%;">연관 테이블명</th>
                <th style="padding: 10px 12px; font-weight: 600; width: 35%;">테이블 설명 (DB)</th>
                <th style="padding: 10px 12px; font-weight: 600; width: 30%;">관계 설명 배 메모 (수정은 가능)</th>
                <th style="padding: 10px 12px; font-weight: 600; width: 10%; text-align: center;">작업</th>
              </tr>
            </thead>
            <tbody>
              ${{relatedRowsHtml}}
            </tbody>
          </table>
        </div>
      </div>

      <!-- 탭 콘텐츠 2: 상세 설명 배 관계도 -->
      <div id="tab-memo-content" class="tab-content" style="display: ${{activeTab === 'memo' ? 'flex' : 'none'}}; overflow-y: auto; gap: 16px; padding-bottom: 20px;">
        <div class="relation-row" style="display: flex; flex-direction: column; gap: 12px; font-size: 13px; color: var(--text-muted); background: #f8fafc; border: 1px solid var(--border); padding: 16px; border-radius: 8px; overflow: hidden; width: 100%;">
          <div style="display:flex; align-items:center; gap:8px; width: 100%; overflow: hidden;">
            <span style="flex-shrink: 0; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;">의 <b>연관 화면</b>:</span>
            <div style="display: flex; gap: 6px; overflow-x: auto; white-space: nowrap; padding-bottom: 4px; flex-grow: 1; scrollbar-width: thin;">
              ${{screenBadges}}
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:8px; width: 100%; overflow: hidden;">
            <span style="flex-shrink: 0; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;">인덱스 <b>연관 배치</b>:</span>
            <div style="display: flex; gap: 6px; overflow-x: auto; white-space: nowrap; padding-bottom: 4px; flex-grow: 1; scrollbar-width: thin;">
              ${{batchBadges}}
            </div>
          </div>
        </div>
        ${{memoHtml || '<div style="color: var(--text-muted); font-size: 13px; text-align: center; padding: 48px 0; border: 1px dashed var(--border); border-radius: 8px; background: white;">등록된 상세 메모가 없습니다. 우측 상단의 "테이블 메모" 상자를 클릭해 Markdown 형태의 관계 설명을 등록했하다 수 있습니다.</div>'}}
      </div>

      <!-- 탭 콘텐츠 3: 연관 가이드 -->
      <div id="tab-guides-content" class="tab-content" style="display: ${{activeTab === 'guides' ? 'flex' : 'none'}}; overflow-y: auto; gap: 16px; padding-bottom: 20px;">
        <div style="font-size: 13.5px; color: var(--text-muted); font-weight: 500; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; width: 100%; gap: 16px;">
          <span style="display: flex; align-items: center; gap: 6px;">입 이 테이블과 매핑되거나 키워드가 포함된 분석 가이드 / QA 리포트 목록입니다.</span>
          <button onclick="showTableGuideInput('${{tbl.table_name}}')" style="flex-shrink: 0; background: var(--primary-light); color: var(--primary-accent); border: 1px solid #bfdbfe; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 4px; transition: all 0.15s ease;" onmouseover="this.style.backgroundColor='var(--primary-accent)'; this.style.color='white'" onmouseout="this.style.backgroundColor='var(--primary-light)'; this.style.color='var(--primary-accent)'">
            위 수동 가이드 추가
          </button>
        </div>
        
        <!-- 수동 가이드 추가 입력 탭 -->
        <div id="table-guide-input-container" style="display: none; background: #f8fafc; border: 1px solid var(--border); padding: 16px; border-radius: 8px; width: 100%; gap: 12px; flex-direction: column;">
          <div style="font-weight: 700; font-size: 13px; color: var(--text-main);">위 테이블 연관 가이드 추가</div>
          <div style="display: flex; gap: 8px; width: 100%;">
            <input type="text" id="table-guide-input" class="input-field" style="flex: 1; font-size: 13px; padding: 6px 10px;" placeholder="가이드 매덊겕다슫 파일명을 입력하세요 (예: my_guide.md)...">
            <button onclick="saveTableGuide('${{tbl.table_name}}')" style="background: var(--primary-accent); color: white; border: none; padding: 6px 16px; border-radius: 6px; font-size: 12.5px; font-weight: 700; cursor: pointer;">추가</button>
            <button onclick="document.getElementById('table-guide-input-container').style.display='none'" style="background: var(--border); color: var(--text-main); border: 1px solid var(--border); padding: 6px 16px; border-radius: 6px; font-size: 12.5px; font-weight: 700; cursor: pointer;">취소</button>
          </div>
        </div>

        <div class="guides-grid">
          ${{guideCardsHtml}}
        </div>
      </div>

      <!-- 탭 콘텐츠 4: CUDR 시점별 메모 -->
      <div id="tab-cudrmemos-content" class="tab-content" style="display: ${{activeTab === 'cudrmemos' ? 'flex' : 'none'}}; overflow-y: auto; gap: 16px; padding-bottom: 20px;">
        ${{cudrMemosHtml}}
      </div>
    </div>
  `;
  
  content.appendChild(detailCard);

  // 관련 테이블 설명 칸 높이 자동 조절
  detailCard.querySelectorAll("textarea").forEach(ta => {{
    ta.style.height = 'auto';
    ta.style.height = (ta.scrollHeight + 4) + 'px';
  }});

  // 기본 Unique 인덱스 자동 선택란은 배 하이라이트 처리
  if (tbl.indexes.length > 0) {{
    let defaultIdx = tbl.indexes.findIndex(idx => idx.index_def.toLowerCase().includes("unique"));
    if (defaultIdx === -1) defaultIdx = 0;
    
    const indexCards = detailCard.querySelectorAll(".index-card");
    if (indexCards[defaultIdx]) {{
      // 테이블 상세 로드 시에는 기본 인덱스 하이라이트만 켜고, 자동 스크롤은 하지 않습니다. (상단 인덱스가 가려지는 현상 방지)
      toggleIndexHighlight(indexCards[defaultIdx], false);
    }}
  }}

  // 검색어가 있고 스크롤 활성화인 경우, 처 번째 매칭된 컬럼으로 부드럽게 스크롤 이동
  if (searchKeyword.trim() && shouldScroll) {{
    const firstMatchMark = detailCard.querySelector("tbody mark.search-match");
    if (firstMatchMark) {{
      const row = firstMatchMark.closest("tr");
      if (row) {{
        setTimeout(() => {{
          row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}, 150);
      }}
    }}
  }}
}}

function addRelatedTable(currentTableName) {{
  const selectEl = document.getElementById("add-related-select");
  const descEl = document.getElementById("add-related-desc");
  if (!selectEl || !descEl) return;
  const relTableName = selectEl.value;
  const desc = descEl.value.trim();
  
  if (!relTableName) {{
    alert("연관할 테이블을 선택해 주세요.");
    return;
  }}
  
  const tbl = TABLES.find(x => x.table_name === currentTableName);
  if (!tbl) return;
  
  if (!tbl.related_tables) {{
    tbl.related_tables = [];
  }}
  
  if (tbl.related_tables.some(r => r.table_name === relTableName)) {{
    alert("이미 추가된 관련 테이블입니다.");
    return;
  }}
  
  tbl.related_tables.push({{
    table_name: relTableName,
    description: desc
  }});
  
  localStorage.setItem("related_tables:table:" + currentTableName, JSON.stringify(tbl.related_tables));
  selectTable(tbl, false);
}}
window.addRelatedTable = addRelatedTable;

function deleteRelatedTable(currentTableName, relTableName) {{
  if (!confirm("해당 연관 관계를 삭제하시겠습니까?")) return;
  
  const tbl = TABLES.find(x => x.table_name === currentTableName);
  if (!tbl) return;
  
  if (tbl.related_tables) {{
    tbl.related_tables = tbl.related_tables.filter(r => r.table_name !== relTableName);
  }}
  
  localStorage.setItem("related_tables:table:" + currentTableName, JSON.stringify(tbl.related_tables));
  selectTable(tbl, false);
}}
window.deleteRelatedTable = deleteRelatedTable;

function updateRelatedTableDesc(currentTableName, relTableName, newDesc) {{
  const tbl = TABLES.find(x => x.table_name === currentTableName);
  if (!tbl) return;
  
  if (tbl.related_tables) {{
    const rel = tbl.related_tables.find(r => r.table_name === relTableName);
    if (rel) {{
      rel.description = newDesc.trim();
    }}
  }}
  
  localStorage.setItem("related_tables:table:" + currentTableName, JSON.stringify(tbl.related_tables));
}}
window.updateRelatedTableDesc = updateRelatedTableDesc;

function selectTableByName(name) {{
  const tbl = TABLES.find(x => x.table_name.toLowerCase() === name.toLowerCase());
  if (tbl) {{
    selectTable(tbl, true);
  }}
}}
window.selectTableByName = selectTableByName;

function toggleIndexHighlight(cardElem, shouldScroll = true) {{
  const indexDef = cardElem.dataset.indexDef;
  const isActive = cardElem.classList.contains("active");

  document.querySelectorAll(".index-card").forEach(c => c.classList.remove("active"));
  document.querySelectorAll("tr.index-highlight-row").forEach(tr => tr.classList.remove("index-highlight-row"));

  if (isActive) return;

  cardElem.classList.add("active");

  const cols = parseIndexColumns(indexDef);
  if (cols.length === 0) return;

  let firstRow = null;
  cols.forEach(colName => {{
    const row = document.querySelector(`tr[data-column-name="${{colName.toLowerCase()}}"]`);
    if (row) {{
      row.classList.add("index-highlight-row");
      if (!firstRow) firstRow = row;
    }}
  }});

  if (firstRow && shouldScroll) {{
    setTimeout(() => {{
      firstRow.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}, 100);
  }}
}}

function parseIndexColumns(indexDef) {{
  const match = indexDef.match(/using\s+\w+\s*\(([^)]+)\)/i);
  if (!match) return [];
  return match[1].split(',').map(col => col.trim().replace(/['"`]/g, ''));
}}

function editTableMemo(tname) {{
  const container = document.getElementById("table-memo-container");
  const tableMemoKey = "memo:table:" + tname;
  const currentMemo = localStorage.getItem(tableMemoKey) || currentTable.custom_memo || "";
  
  container.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 8px; width: 100%;">
      <textarea id="table-memo-textarea" class="input-field" style="font-family: inherit; font-size: 13px; height: 80px; resize: vertical;" placeholder="테이블에 대한 메모를 입력하세요...">${{escHtml(currentMemo)}}</textarea>
      <div style="display: flex; gap: 8px; justify-content: flex-end;">
        <button onclick="saveTableMemo('${{tname}}')" class="btn btn-save" style="padding: 4px 12px; font-size: 12px; background: var(--primary-accent); color: white; border: none; border-radius: 4px; cursor: pointer;">저장</button>
        <button onclick="selectTable(currentTable, false)" class="btn btn-cancel" style="padding: 4px 12px; font-size: 12px; background: var(--text-muted); color: white; border: none; border-radius: 4px; cursor: pointer;">취소</button>
      </div>
    </div>
  `;
}}

function saveTableMemo(tname) {{
  const textarea = document.getElementById("table-memo-textarea");
  const text = textarea.value.trim();
  const key = "memo:table:" + tname;
  if (text) {{
    localStorage.setItem(key, text);
  }} else {{
    localStorage.removeItem(key);
  }}
  selectTable(currentTable, false);
}}

function editColMemo(tname, cname) {{
  const span = document.getElementById("memo-col-val-" + cname);
  const key = "memo:col:" + tname + ":" + cname;
  
  // Find custom memo from TABLES as fallback
  let customMemo = "";
  if (currentTable && currentTable.columns) {{
    const colObj = currentTable.columns.find(c => c.column_name === cname);
    if (colObj) customMemo = colObj.custom_memo || "";
  }}
  
  const currentMemo = localStorage.getItem(key) || customMemo || "";
  
  span.parentElement.innerHTML = `
    <span style="font-weight: 600;">입 메모:</span>
    <input type="text" id="memo-col-input-${{cname}}" class="input-field" style="display: inline-block; width: 60%; padding: 2px 6px; font-size: 12px; height: auto;" value="${{escHtml(currentMemo)}}" placeholder="메모 입력 후 엔터...">
    <button onclick="saveColMemo('${{tname}}', '${{cname}}')" style="padding: 2px 8px; font-size: 11px; background: var(--primary-accent); color: white; border: none; border-radius: 4px; cursor: pointer; margin-left:4px;">장</button>
    <button onclick="selectTable(currentTable, false)" style="padding: 2px 8px; font-size: 11px; background: var(--text-muted); color: white; border: none; border-radius: 4px; cursor: pointer; margin-left:4px;">취소</button>
  `;
  
  const input = document.getElementById("memo-col-input-" + cname);
  input.focus();
  input.addEventListener("keydown", e => {{
    if (e.key === "Enter") {{
      saveColMemo(tname, cname);
    }}
  }});
}}

function saveColMemo(tname, cname) {{
  const input = document.getElementById("memo-col-input-" + cname);
  const text = input.value.trim();
  const key = "memo:col:" + tname + ":" + cname;
  if (text) {{
    localStorage.setItem(key, text);
  }} else {{
    localStorage.removeItem(key);
  }}
  selectTable(currentTable, false);
}}

function editColGuide(tname, cname) {{
  const span = document.getElementById("guide-col-val-" + cname);
  const key = "guide:col:" + tname + ":" + cname;
  
  let customGuide = "";
  if (currentTable && currentTable.columns) {{
    const colObj = currentTable.columns.find(c => c.column_name === cname);
    if (colObj) customGuide = colObj.manual_guide || "";
  }}
  
  const currentGuide = localStorage.getItem(key) || customGuide || "";
  
  span.parentElement.innerHTML = `
    <input type="text" id="guide-col-input-${{cname}}" class="input-field" style="display: inline-block; width: 80%; padding: 2px 6px; font-size: 11px; height: auto;" value="${{escHtml(currentGuide)}}" placeholder="D:\\path\\to\\report.md 형식 입력 후 엔터...">
    <div style="margin-top: 4px; display: flex; gap: 4px; justify-content: flex-end;">
      <button onclick="saveColGuide('${{tname}}', '${{cname}}')" style="padding: 2px 6px; font-size: 10px; background: var(--primary-accent); color: white; border: none; border-radius: 4px; cursor: pointer;">장</button>
      <button onclick="selectTable(currentTable, false)" style="padding: 2px 6px; font-size: 10px; background: var(--text-muted); color: white; border: none; border-radius: 4px; cursor: pointer;">취소</button>
    </div>
  `;
  
  const input = document.getElementById("guide-col-input-" + cname);
  input.focus();
  input.addEventListener("keydown", e => {{
    if (e.key === "Enter") {{
      saveColGuide(tname, cname);
    }}
  }});
}}

function saveColGuide(tname, cname) {{
  const input = document.getElementById("guide-col-input-" + cname);
  const text = input.value.trim();
  const key = "guide:col:" + tname + ":" + cname;
  if (text) {{
    localStorage.setItem(key, text);
  }} else {{
    localStorage.removeItem(key);
  }}
  selectTable(currentTable, false);
}}

function showTableGuideInput(tableName) {{
  const container = document.getElementById('table-guide-input-container');
  if (container) {{
    container.style.display = container.style.display === 'none' ? 'flex' : 'none';
    if (container.style.display === 'flex') {{
      const input = document.getElementById('table-guide-input');
      if (input) {{
        input.value = '';
        input.focus();
      }}
    }}
  }}
}}
window.showTableGuideInput = showTableGuideInput;

function saveTableGuide(tableName) {{
  const input = document.getElementById('table-guide-input');
  if (!input) return;
  const newGuide = input.value.trim();
  if (!newGuide) {{
    alert('가이드 파일명을 입력하세요.');
    return;
  }}
  
  const tbl = TABLES.find(x => x.table_name === tableName);
  if (!tbl) return;
  
  const key = "guide:table:" + tableName;
  const currentVal = localStorage.getItem(key) || tbl.manual_guide || "";
  let guides = currentVal ? currentVal.split(",").map(x => x.trim()).filter(Boolean) : [];
  
  if (guides.includes(newGuide)) {{
    alert('이미 등록된 가이드입니다.');
    return;
  }}
  
  guides.push(newGuide);
  localStorage.setItem(key, guides.join(","));
  
  selectTable(tbl, false);
}}
window.saveTableGuide = saveTableGuide;

function removeTableGuide(tableName, guideName) {{
  if (!confirm('이 테이블에서 해당 연관 가이드 링크를 제거하시겠습니까?')) return;
  
  const tbl = TABLES.find(x => x.table_name === tableName);
  if (!tbl) return;
  
  const key = "guide:table:" + tableName;
  const currentVal = localStorage.getItem(key) || tbl.manual_guide || "";
  let guides = currentVal ? currentVal.split(",").map(x => x.trim()).filter(Boolean) : [];
  
  guides = guides.filter(g => g !== guideName);
  
  if (guides.length > 0) {{
    localStorage.setItem(key, guides.join(","));
  }} else {{
    localStorage.removeItem(key);
  }}
  
  selectTable(tbl, false);
}}
window.removeTableGuide = removeTableGuide;

function openDrawer(tbl) {{
  if (!tbl) return;
  
  // Populate the drawer info
  document.getElementById('drawer-table-name').textContent = tbl.table_name;
  document.getElementById('drawer-table-comment').textContent = tbl.comment || '테이블 설명 없음';
  
  // Screens badges
  const screensDiv = document.getElementById('drawer-table-screens');
  if (tbl.screens && tbl.screens.length) {{
    screensDiv.innerHTML = tbl.screens.map(scr => `<span class="badge screen-id" style="margin-right: 4px; margin-bottom: 4px; display: inline-block;" title="백오피스 화면: ${{scr.name || ''}}">${{scr.id}}${{scr.name ? ` (${{scr.name}})` : ''}}</span>`).join('');
  }} else {{
    screensDiv.innerHTML = '<span style="color:var(--text-muted);font-size:12px;">연관 화면 없음</span>';
  }}
  
  // Batches badges
  const batchesDiv = document.getElementById('drawer-table-batches');
  if (tbl.batches && tbl.batches.length) {{
    batchesDiv.innerHTML = tbl.batches.map(bat => `<span class="badge batch-id" style="margin-right: 4px; margin-bottom: 4px; display: inline-block;" title="배치 작업: ${{bat.name || ''}}">${{bat.id}}${{bat.name ? ` (${{bat.name}})` : ''}}</span>`).join('');
  }} else {{
    batchesDiv.innerHTML = '<span style="color:var(--text-muted);font-size:12px;">연관 배치 없음</span>';
  }}
  
  // Memo content
  const tableMemoKey = "memo:table:" + tbl.table_name;
  const currentMemo = localStorage.getItem(tableMemoKey) || tbl.custom_memo || "";
  
  const textarea = document.getElementById('drawer-table-memo-txt');
  textarea.value = currentMemo;
  
  const currentCMemo = localStorage.getItem("memo:c:table:" + tbl.table_name) || "";
  const currentUMemo = localStorage.getItem("memo:u:table:" + tbl.table_name) || "";
  const currentDMemo = localStorage.getItem("memo:d:table:" + tbl.table_name) || "";
  const currentRMemo = localStorage.getItem("memo:r:table:" + tbl.table_name) || "";
  
  document.getElementById('drawer-c-memo-txt').value = currentCMemo;
  document.getElementById('drawer-u-memo-txt').value = currentUMemo;
  document.getElementById('drawer-d-memo-txt').value = currentDMemo;
  document.getElementById('drawer-r-memo-txt').value = currentRMemo;
  
  // Show drawer
  const drawer = document.getElementById('detail-drawer');
  const overlay = document.getElementById('drawer-overlay');
  
  drawer.classList.add('open');
  overlay.style.display = 'block';
  setTimeout(() => {{
    overlay.style.opacity = '1';
  }}, 10);
}}

function closeDrawer() {{
  if (currentTable) {{
    saveDrawerTableMemo(currentTable.table_name);
  }}
  const drawer = document.getElementById('detail-drawer');
  const overlay = document.getElementById('drawer-overlay');
  drawer.classList.remove('open');
  overlay.style.opacity = '0';
  setTimeout(() => {{
    overlay.style.display = 'none';
  }}, 300);
}}

function saveDrawerTableMemo(tname) {{
  const textarea = document.getElementById('drawer-table-memo-txt');
  if (!textarea) return;
  const text = textarea.value.trim();
  const key = "memo:table:" + tname;
  const prevVal = localStorage.getItem(key) || "";
  
  const cTextarea = document.getElementById('drawer-c-memo-txt');
  const uTextarea = document.getElementById('drawer-u-memo-txt');
  const dTextarea = document.getElementById('drawer-d-memo-txt');
  const rTextarea = document.getElementById('drawer-r-memo-txt');
  
  const cText = cTextarea ? cTextarea.value.trim() : "";
  const uText = uTextarea ? uTextarea.value.trim() : "";
  const dText = dTextarea ? dTextarea.value.trim() : "";
  const rText = rTextarea ? rTextarea.value.trim() : "";
  
  let changed = false;
  
  if (text !== prevVal) {{
    if (text) localStorage.setItem(key, text);
    else localStorage.removeItem(key);
    changed = true;
  }}
  
  const cKey = "memo:c:table:" + tname;
  if (cText !== (localStorage.getItem(cKey) || "")) {{
    if (cText) localStorage.setItem(cKey, cText);
    else localStorage.removeItem(cKey);
    changed = true;
  }}
  
  const uKey = "memo:u:table:" + tname;
  if (uText !== (localStorage.getItem(uKey) || "")) {{
    if (uText) localStorage.setItem(uKey, uText);
    else localStorage.removeItem(uKey);
    changed = true;
  }}
  
  const dKey = "memo:d:table:" + tname;
  if (dText !== (localStorage.getItem(dKey) || "")) {{
    if (dText) localStorage.setItem(dKey, dText);
    else localStorage.removeItem(dKey);
    changed = true;
  }}
  
  const rKey = "memo:r:table:" + tname;
  if (rText !== (localStorage.getItem(rKey) || "")) {{
    if (rText) localStorage.setItem(rKey, rText);
    else localStorage.removeItem(rKey);
    changed = true;
  }}
  
  if (changed) {{
    renderTableList();
    
    const miniMemoEl = document.getElementById("table-memo-val-" + tname);
    if (miniMemoEl) miniMemoEl.textContent = text || '등록된 메모가 없습니다.';
    
    const cEl = document.getElementById("c-memo-val-" + tname);
    const uEl = document.getElementById("u-memo-val-" + tname);
    const dEl = document.getElementById("d-memo-val-" + tname);
    const rEl = document.getElementById("r-memo-val-" + tname);
    
    if (cEl) cEl.textContent = cText || '비꾩뼱엳쓬';
    if (uEl) uEl.textContent = uText || '비꾩뼱엳쓬';
    if (dEl) dEl.textContent = dText || '비꾩뼱엳쓬';
    if (rEl) rEl.textContent = rText || '비꾩뼱엳쓬';
    
    showToast("메모가 자동 저장되었습니다.");
  }}
}}

function showToast(message) {{
  const toast = document.getElementById('toast-msg');
  if (!toast) return;
  toast.innerText = message;
  toast.classList.add('show');
  setTimeout(() => {{
    toast.classList.remove('show');
  }}, 2000);
}}

function exportMemos() {{
  const memoData = {{ tables: {{}}, sortQueue: [] }};
  
  // Get sort queue from localStorage
  let sortQueue = [];
  try {{
    sortQueue = JSON.parse(localStorage.getItem("sortQueue")) || [];
  }} catch(e) {{}}
  memoData.sortQueue = sortQueue;

  // 1. Gather from TABLES
  TABLES.forEach(tbl => {{
    const starred = tbl.starred || false;
    const color = tbl.color || "none";
    const sortOrder = tbl.sort_order !== undefined && tbl.sort_order !== 9999 ? String(tbl.sort_order) : "9999";

    const hasCUDR = tbl.memo_c || tbl.memo_u || tbl.memo_d || tbl.memo_r;
    const hasRelated = tbl.related_tables && tbl.related_tables.length > 0;

    if (tbl.custom_memo || starred || color !== "none" || sortOrder !== "9999" || hasCUDR || hasRelated || (tbl.columns && tbl.columns.some(c => c.custom_memo || c.manual_guide))) {{
      if (!memoData.tables[tbl.table_name]) {{
        memoData.tables[tbl.table_name] = {{
          memo: tbl.custom_memo || "",
          memo_c: tbl.memo_c || "",
          memo_u: tbl.memo_u || "",
          memo_d: tbl.memo_d || "",
          memo_r: tbl.memo_r || "",
          starred: starred,
          color: color,
          sortOrder: sortOrder,
          related_tables: tbl.related_tables || [],
          columns: {{}}
        }};
      }}
    }}
    tbl.columns.forEach(col => {{
      if (col.custom_memo || col.manual_guide) {{
        if (!memoData.tables[tbl.table_name]) {{
          memoData.tables[tbl.table_name] = {{
            memo: "",
            starred: starred,
            color: color,
            sortOrder: sortOrder,
            columns: {{}}
          }};
        }}
        if (col.manual_guide) {{
          memoData.tables[tbl.table_name].columns[col.column_name] = {{
            memo: col.custom_memo || "",
            guide: col.manual_guide || ""
          }};
        }} else {{
          memoData.tables[tbl.table_name].columns[col.column_name] = col.custom_memo || "";
        }}
      }}
    }});
  }});
  
  // 2. Overwrite/merge with localStorage
  for (let i = 0; i < localStorage.length; i++) {{
    const key = localStorage.key(i);
    if (key.startsWith("memo:table:")) {{
      const tname = key.replace("memo:table:", "");
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: val, starred: false, color: "none", sortOrder: "9999", columns: {{}} }};
      }} else {{
        memoData.tables[tname].memo = val;
      }}
    }} else if (key.startsWith("memo:c:table:")) {{
      const tname = key.replace("memo:c:table:", "");
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: "none", sortOrder: "9999", columns: {{}} }};
      }}
      memoData.tables[tname].memo_c = val || "";
    }} else if (key.startsWith("memo:u:table:")) {{
      const tname = key.replace("memo:u:table:", "");
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: "none", sortOrder: "9999", columns: {{}} }};
      }}
      memoData.tables[tname].memo_u = val || "";
    }} else if (key.startsWith("memo:d:table:")) {{
      const tname = key.replace("memo:d:table:", "");
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: "none", sortOrder: "9999", columns: {{}} }};
      }}
      memoData.tables[tname].memo_d = val || "";
    }} else if (key.startsWith("memo:r:table:")) {{
      const tname = key.replace("memo:r:table:", "");
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: "none", sortOrder: "9999", columns: {{}} }};
      }}
      memoData.tables[tname].memo_r = val || "";
    }} else if (key.startsWith("star:table:")) {{
      const tname = key.replace("star:table:", "");
      const val = localStorage.getItem(key) === "true";
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: val, color: "none", sortOrder: "9999", columns: {{}} }};
      }} else {{
        memoData.tables[tname].starred = val;
      }}
    }} else if (key.startsWith("color:table:")) {{
      const tname = key.replace("color:table:", "");
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: val, sortOrder: "9999", columns: {{}} }};
      }} else {{
        memoData.tables[tname].color = val;
      }}
    }} else if (key.startsWith("sortOrder:table:")) {{
      const tname = key.replace("sortOrder:table:", "");
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: "none", sortOrder: val, columns: {{}} }};
      }} else {{
        memoData.tables[tname].sortOrder = val;
      }}
    }} else if (key.startsWith("guide:table:")) {{
      const tname = key.replace("guide:table:", "");
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: "none", sortOrder: "9999", columns: {{}} }};
      }}
      memoData.tables[tname].guide = val || "";
    }} else if (key.startsWith("related_tables:table:")) {{
      const tname = key.replace("related_tables:table:", "");
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: "none", sortOrder: "9999", related_tables: [], columns: {{}} }};
      }}
      try {{
        memoData.tables[tname].related_tables = JSON.parse(val) || [];
      }} catch(e) {{
        memoData.tables[tname].related_tables = [];
      }}
    }} else if (key.startsWith("memo:col:")) {{
      const parts = key.split(":");
      const tname = parts[2];
      const cname = parts[3];
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: "none", sortOrder: "9999", columns: {{}} }};
      }}
      if (!memoData.tables[tname].columns[cname]) {{
        memoData.tables[tname].columns[cname] = val || "";
      }} else if (typeof memoData.tables[tname].columns[cname] === 'object') {{
        memoData.tables[tname].columns[cname].memo = val || "";
      }} else {{
        memoData.tables[tname].columns[cname] = val || "";
      }}
    }} else if (key.startsWith("guide:col:")) {{
      const parts = key.split(":");
      const tname = parts[2];
      const cname = parts[3];
      const val = localStorage.getItem(key);
      if (!memoData.tables[tname]) {{
        memoData.tables[tname] = {{ memo: "", starred: false, color: "none", sortOrder: "9999", columns: {{}} }};
      }}
      if (!memoData.tables[tname].columns[cname]) {{
        memoData.tables[tname].columns[cname] = {{ memo: "", guide: val || "" }};
      }} else if (typeof memoData.tables[tname].columns[cname] === 'object') {{
        memoData.tables[tname].columns[cname].guide = val || "";
      }} else {{
        memoData.tables[tname].columns[cname] = {{
          memo: memoData.tables[tname].columns[cname],
          guide: val || ""
        }};
      }}
    }}
  }}
  
  // Clean up empty tables
  Object.keys(memoData.tables).forEach(tname => {{
    const t = memoData.tables[tname];
    const hasAnyCUDR = t.memo_c || t.memo_u || t.memo_d || t.memo_r;
    if (!t.memo && !t.starred && t.color === "none" && t.sortOrder === "9999" && !t.guide && !hasAnyCUDR && Object.keys(t.columns).length === 0) {{
      delete memoData.tables[tname];
    }}
  }});

  // Download JSON
  const jsonStr = JSON.stringify(memoData, null, 2);
  const blob = new Blob([jsonStr], {{ type: "application/json" }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const filename = document.getElementById("export-filename").value.trim() || "table_memos.json";
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}}

const EMBEDDED_MEMOS = /*EMBEDDED_MEMOS_PLACEHOLDER*/;

function importMemos() {{
  const dirPath = document.getElementById("export-filepath").value.trim();
  let rawFileName = document.getElementById("export-filename").value.trim();
  
  if (!rawFileName) {{
    if (confirm("파일명이 비어 있습니다. 기본 파일명(table_memos.json)으로 복원을 진행하시겠습니까?")) {{
      rawFileName = "table_memos.json";
      document.getElementById("export-filename").value = "table_memos.json";
    }} else {{
      return;
    }}
  }}
  const fileName = rawFileName;
  
  let fullPath = dirPath;
  if (fullPath && !fullPath.endsWith("\\\\") && !fullPath.endsWith("/")) {{
    fullPath += (fullPath.indexOf("/") !== -1) ? "/" : "\\\\";
  }}
  fullPath += fileName;
  
  // 1. 만약 입력된 경로가 로컬 백업 기본 경로와 같으면 Fetch 없이 내장된 데이터를 이용해 복원
  const defaultPath = "D:/hmTest/backoffice/QaReport/table_memos.json";
  const normalizedFull = fullPath.toLowerCase().split("\\\\").join("/");
  const normalizedDefault = defaultPath.toLowerCase().split("\\\\").join("/");
  
  if (normalizedFull === normalizedDefault && typeof EMBEDDED_MEMOS !== "undefined" && EMBEDDED_MEMOS && EMBEDDED_MEMOS.tables) {{
    console.log("로컬 보안 정책 우회: 내장된 메모 데이터를 로드하여 복원을 처리합니다.");
    executeImport(EMBEDDED_MEMOS);
    return;
  }}
  
  // 2. 다른 경로일 경우 Fetch 시도
  let targetUrl = fullPath;
  if (/^[a-zA-Z]:/.test(targetUrl)) {{
    targetUrl = "file:///" + targetUrl.split("\\\\").join("/");
  }} else if (!targetUrl.startsWith("file://") && !targetUrl.startsWith("http")) {{
    targetUrl = "./" + targetUrl;
  }}
  
  fetch(targetUrl)
    .then(response => {{
      if (!response.ok) {{
        throw new Error("파일 읽기 실패 (HTTP status " + response.status + ")");
      }}
      return response.json();
    }})
    .then(data => {{
      executeImport(data);
    }})
    .catch(err => {{
      console.warn("자동 복원 실패. 파일 선택 창을 통해 복원을 진행합니다.", err);
      if (confirm("경로에서 직접 복원에 실패했습니다: " + fullPath + ". 수동 파일 선택 창을 띄워 복원하시겠습니까?")) {{
        document.getElementById("import-memos-file").click();
      }}
    }});
}}

function executeImport(data) {{
  if (!data || !data.tables) {{
    alert("올바른 DB 명세 JSON 형식이 아닙니다.");
    return;
  }}
  let importCount = 0;
  if (data.sortQueue) {{
    localStorage.setItem("sortQueue", JSON.stringify(data.sortQueue));
  }}
  Object.keys(data.tables).forEach(tname => {{
    const t = data.tables[tname];
    if (t.memo !== undefined) {{
      localStorage.setItem("memo:table:" + tname, t.memo);
      importCount++;
    }}
    if (t.memo_c !== undefined) {{
      localStorage.setItem("memo:c:table:" + tname, t.memo_c);
    }}
    if (t.memo_u !== undefined) {{
      localStorage.setItem("memo:u:table:" + tname, t.memo_u);
    }}
    if (t.memo_d !== undefined) {{
      localStorage.setItem("memo:d:table:" + tname, t.memo_d);
    }}
    if (t.memo_r !== undefined) {{
      localStorage.setItem("memo:r:table:" + tname, t.memo_r);
    }}
    if (t.starred !== undefined) {{
      localStorage.setItem("star:table:" + tname, t.starred ? "Y" : "N");
    }}
    if (t.color !== undefined) {{
      localStorage.setItem("color:table:" + tname, t.color);
    }}
    if (t.sortOrder !== undefined) {{
      localStorage.setItem("sortOrder:table:" + tname, t.sortOrder.toString());
    }}
    if (t.related_tables !== undefined) {{
      localStorage.setItem("relation:table:" + tname, JSON.stringify(t.related_tables));
    }}
    if (t.columns) {{
      Object.keys(t.columns).forEach(cname => {{
        const col = t.columns[cname];
        if (col.custom_memo !== undefined) {{
          localStorage.setItem("memo:column:" + tname + ":" + cname, col.custom_memo);
        }}
        if (col.manual_guide !== undefined) {{
          localStorage.setItem("memo:guide:" + tname + ":" + cname, col.manual_guide);
        }}
      }});
    }}
  }});
  alert("성공적으로 " + importCount + "개 테이블의 메모를 복원했습니다.");
  location.reload();
}}

function clearLocalMemos() {{
  if (confirm("브라우저 로컬 장소에 캐시된 메모 중요도 설정을 초기화하고, 서버의 최신 table_memos.json 데이터로 되돌리시겠습니까?")) {{
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {{
      const key = localStorage.key(i);
      if (key.startsWith("memo:") || key.startsWith("star:") || key.startsWith("color:") || key.startsWith("sortOrder:") || key.startsWith("guide:") || key === "sortQueue") {{
        keysToRemove.push(key);
      }}
    }}
    keysToRemove.forEach(key => localStorage.removeItem(key));
    alert("로컬 캐시가 초기화되었습니다. 페이지를 새로고침합니다.");
    location.reload();
  }}
}}
window.clearLocalMemos = clearLocalMemos;

function handleImportFile(event) {{
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {{
    try {{
      const data = JSON.parse(e.target.result);
      if (!data || !data.tables) {{
        alert("올바른 백업 파일 형식이 아닙니다.");
        return;
      }}
      let importCount = 0;
      if (data.sortQueue) {{
        localStorage.setItem("sortQueue", JSON.stringify(data.sortQueue));
      }}
      Object.keys(data.tables).forEach(tname => {{
        const t = data.tables[tname];
        if (t.memo !== undefined) {{
          localStorage.setItem("memo:table:" + tname, t.memo);
          importCount++;
        }}
        if (t.memo_c !== undefined) {{
          localStorage.setItem("memo:c:table:" + tname, t.memo_c);
          importCount++;
        }}
        if (t.memo_u !== undefined) {{
          localStorage.setItem("memo:u:table:" + tname, t.memo_u);
          importCount++;
        }}
        if (t.memo_d !== undefined) {{
          localStorage.setItem("memo:d:table:" + tname, t.memo_d);
          importCount++;
        }}
        if (t.memo_r !== undefined) {{
          localStorage.setItem("memo:r:table:" + tname, t.memo_r);
          importCount++;
        }}
        if (t.guide !== undefined) {{
          localStorage.setItem("guide:table:" + tname, t.guide);
          importCount++;
        }}
        if (t.related_tables !== undefined) {{
          localStorage.setItem("related_tables:table:" + tname, JSON.stringify(t.related_tables));
          const tbl = TABLES.find(x => x.table_name === tname);
          if (tbl) tbl.related_tables = t.related_tables;
          importCount++;
        }}
        if (t.starred !== undefined) {{
          localStorage.setItem("star:table:" + tname, t.starred);
          const tbl = TABLES.find(x => x.table_name === tname);
          if (tbl) tbl.starred = t.starred;
        }}
        if (t.color !== undefined) {{
          localStorage.setItem("color:table:" + tname, t.color);
          const tbl = TABLES.find(x => x.table_name === tname);
          if (tbl) tbl.color = t.color;
        }}
        if (t.sortOrder !== undefined) {{
          localStorage.setItem("sortOrder:table:" + tname, t.sortOrder);
          const tbl = TABLES.find(x => x.table_name === tname);
          if (tbl) {{
            const parsed = parseInt(t.sortOrder);
            tbl.sort_order = isNaN(parsed) ? 9999 : parsed;
          }}
        }}
        if (t.columns) {{
          Object.keys(t.columns).forEach(cname => {{
            const colInfo = t.columns[cname];
            if (colInfo && typeof colInfo === 'object') {{
              if (colInfo.memo !== undefined) {{
                localStorage.setItem("memo:col:" + tname + ":" + cname, colInfo.memo);
              }}
              if (colInfo.guide !== undefined) {{
                localStorage.setItem("guide:col:" + tname + ":" + cname, colInfo.guide);
              }}
            }} else {{
              localStorage.setItem("memo:col:" + tname + ":" + cname, colInfo || "");
            }}
            importCount++;
          }});
        }}
      }});
      if (data.sortQueue && data.sortQueue.length > 0) {{
        localStorage.setItem("sortChoice", data.sortQueue[0]);
        const selectEl = document.getElementById("sort-choice");
        if (selectEl) selectEl.value = data.sortQueue[0];
      }}
      alert("성공적으로 " + importCount + "개의 사용자 메모를 복원했습니다.");
      renderTableList();
      if (currentTable) {{
        selectTable(currentTable, false);
      }}
    }} catch (err) {{
      alert("파일을 읽는 도중 오류가 발생했습니다: " + err.message);
    }}
  }};
  reader.readAsText(file);
  event.target.value = "";
}}

// 이벤트 리스너 바인딩
const chkAll = document.getElementById("chk-all-search");
const chkTable = document.getElementById("chk-table-search");
const chkColumn = document.getElementById("chk-column-search");
const chkMemo = document.getElementById("chk-memo-search");
const chkRelation = document.getElementById("chk-relation-search");
const chkGuide = document.getElementById("chk-guide-search");

document.getElementById("search").addEventListener("input", e => {{
  searchKeyword = e.target.value;
  renderTableList();
}});

// Drawer event listeners
document.getElementById('close-drawer').addEventListener('click', closeDrawer);
document.getElementById('drawer-overlay').addEventListener('click', closeDrawer);
document.getElementById('drawer-save-btn').addEventListener('click', () => {{
  if (currentTable) {{
    saveDrawerTableMemo(currentTable.table_name);
  }}
  closeDrawer();
}});
['drawer-table-memo-txt', 'drawer-c-memo-txt', 'drawer-u-memo-txt', 'drawer-d-memo-txt', 'drawer-r-memo-txt'].forEach(id => {{
  const el = document.getElementById(id);
  if (el) {{
    el.addEventListener('blur', () => {{
      if (currentTable) {{
        saveDrawerTableMemo(currentTable.table_name);
      }}
    }});
  }}
}});

chkAll.addEventListener("change", e => {{
  const val = e.target.checked;
  chkTable.checked = val;
  chkColumn.checked = val;
  chkMemo.checked = val;
  chkRelation.checked = val;
  chkGuide.checked = val;
  
  includeTableSearch = val;
  includeColumnSearch = val;
  includeMemoSearch = val;
  includeRelationSearch = val;
  includeGuideSearch = val;
  renderTableList();
}});

function syncAllCheckbox() {{
  chkAll.checked = chkTable.checked && chkColumn.checked && chkMemo.checked && chkRelation.checked && chkGuide.checked;
}}

chkTable.addEventListener("change", e => {{
  includeTableSearch = e.target.checked;
  syncAllCheckbox();
  renderTableList();
}});

chkColumn.addEventListener("change", e => {{
  includeColumnSearch = e.target.checked;
  syncAllCheckbox();
  renderTableList();
}});

chkMemo.addEventListener("change", e => {{
  includeMemoSearch = e.target.checked;
  syncAllCheckbox();
  renderTableList();
}});

chkRelation.addEventListener("change", e => {{
  includeRelationSearch = e.target.checked;
  syncAllCheckbox();
  renderTableList();
}});

chkGuide.addEventListener("change", e => {{
  includeGuideSearch = e.target.checked;
  syncAllCheckbox();
  renderTableList();
}});
function switchTab(tabName) {{
  const fieldsTab = document.getElementById("tab-btn-fields");
  const relatedTab = document.getElementById("tab-btn-related");
  const memoTab = document.getElementById("tab-btn-memo");
  const guidesTab = document.getElementById("tab-btn-guides");
  const cudrmemosTab = document.getElementById("tab-btn-cudrmemos");
  
  const fieldsContent = document.getElementById("tab-fields-content");
  const relatedContent = document.getElementById("tab-related-content");
  const memoContent = document.getElementById("tab-memo-content");
  const guidesContent = document.getElementById("tab-guides-content");
  const cudrmemosContent = document.getElementById("tab-cudrmemos-content");
  
  if (!fieldsTab || !memoTab || !guidesTab || !fieldsContent || !memoContent || !guidesContent) return;
  
  fieldsTab.classList.remove("active");
  if (relatedTab) relatedTab.classList.remove("active");
  memoTab.classList.remove("active");
  guidesTab.classList.remove("active");
  if (cudrmemosTab) cudrmemosTab.classList.remove("active");
  
  fieldsContent.style.display = "none";
  if (relatedContent) relatedContent.style.display = "none";
  memoContent.style.display = "none";
  guidesContent.style.display = "none";
  if (cudrmemosContent) cudrmemosContent.style.display = "none";
  
  if (tabName === "fields") {{
    fieldsTab.classList.add("active");
    fieldsContent.style.display = "flex";
    localStorage.setItem("activeTab", "fields");
  }} else if (tabName === "related") {{
    if (relatedTab) relatedTab.classList.add("active");
    if (relatedContent) relatedContent.style.display = "flex";
    localStorage.setItem("activeTab", "related");
  }} else if (tabName === "memo") {{
    memoTab.classList.add("active");
    memoContent.style.display = "flex";
    localStorage.setItem("activeTab", "memo");
  }} else if (tabName === "guides") {{
    guidesTab.classList.add("active");
    guidesContent.style.display = "flex";
    localStorage.setItem("activeTab", "guides");
  }} else if (tabName === "cudrmemos") {{
    if (cudrmemosTab) cudrmemosTab.classList.add("active");
    if (cudrmemosContent) cudrmemosContent.style.display = "flex";
    localStorage.setItem("activeTab", "cudrmemos");
  }}
}}
window.switchTab = switchTab;

// 초기화
document.getElementById("total-count").textContent = TABLES.length;
document.getElementById("header-total-tables").textContent = TABLES.length;
renderTableList();

// 기본적으로 처 번째 테이블 자동 선택란은
if (TABLES.length > 0) {{
  selectTable(TABLES[0]);
}}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
