import os
import json

def parse_markdown_table(md_path):
    screens = []
    if not os.path.exists(md_path):
        print(f"Error: {md_path} does not exist.")
        return screens
        
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Parse only valid table rows
            if line.startswith("|") and not line.startswith("| 대분류") and not line.startswith("| :---"):
                parts = [p.strip() for p in line.split("|")]
                # Expected parts: ['', lclass, mclass, seq, name, file, path, '']
                if len(parts) >= 8:
                    screens.append({
                        "lclass": parts[1],
                        "mclass": parts[2],
                        "seq": parts[3],
                        "name": parts[4],
                        "file": parts[5],
                        "path": parts[6]
                    })
    return screens

def get_html_template(screens_list):
    screens_json = json.dumps(screens_list, ensure_ascii=False)
    
    # Calculate unique categories to populate dropdown options in Python
    lclasses = sorted(list(set(s["lclass"] for s in screens_list)))
    lclass_options = "".join(f'<option value="{lc}">{lc}</option>' for lc in lclasses)
    
    # JavaScript curly braces are escaped by doubling them {{ }} in the f-string
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HMS 영업정보시스템 화면 디렉토리</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-color: #F8FAFC;
            --card-bg: rgba(255, 255, 255, 0.85);
            --border-color: rgba(0, 0, 0, 0.08);
            --text-primary: #1F2937;
            --text-secondary: #4B5563;
            --text-muted: #6B7280;
            --accent-blue: #2563EB;
            --accent-blue-glow: rgba(37, 99, 235, 0.06);
            --accent-green: #059669;
            --accent-green-glow: rgba(5, 150, 105, 0.06);
            --accent-red: #E11D48;
            --accent-red-glow: rgba(225, 29, 72, 0.06);
            --accent-orange: #D97706;
            --accent-orange-glow: rgba(217, 119, 6, 0.06);
            --glass-bg: rgba(255, 255, 255, 0.65);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', 'Noto Sans KR', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            padding: 30px 20px;
            min-height: 100vh;
            background-image: radial-gradient(circle at 5% 10%, rgba(37, 99, 235, 0.04) 0%, transparent 40%),
                              radial-gradient(circle at 95% 90%, rgba(225, 29, 72, 0.03) 0%, transparent 45%);
            background-attachment: fixed;
            overflow-x: hidden;
        }}

        .container {{
            max-width: 1500px;
            margin: 0 auto;
        }}

        /* Header design */
        header {{
            margin-bottom: 25px;
            padding: 24px 30px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            backdrop-filter: blur(16px);
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        }}

        .title-area h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #1E293B 0%, #475569 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .title-area h1 span.logo-badge {{
            font-size: 11px;
            font-weight: 800;
            padding: 3px 8px;
            background: linear-gradient(135deg, var(--accent-blue) 0%, #60A5FA 100%);
            -webkit-text-fill-color: #FFFFFF;
            border-radius: 6px;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
        }}

        .title-area p {{
            color: var(--text-secondary);
            font-size: 13px;
        }}

        /* Summary widgets */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 25px;
        }}

        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 18px 24px;
            backdrop-filter: blur(12px);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(0, 0, 0, 0.15);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        }}

        .stat-info .stat-label {{
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .stat-info .stat-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #0F172A;
        }}

        .stat-card.all-card {{ border-left: 4px solid var(--accent-blue); }}
        .stat-card.hq-card {{ border-left: 4px solid var(--accent-blue); }}
        .stat-card.st-card {{ border-left: 4px solid var(--accent-green); }}
        .stat-card.admin-card {{ border-left: 4px solid var(--accent-red); }}

        .stat-icon {{
            width: 42px;
            height: 42px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
            font-family: 'Outfit', sans-serif;
        }}

        .all-card .stat-icon {{ background: var(--accent-blue-glow); color: var(--accent-blue); }}
        .hq-card .stat-icon {{ background: var(--accent-blue-glow); color: var(--accent-blue); }}
        .st-card .stat-icon {{ background: var(--accent-green-glow); color: var(--accent-green); }}
        .admin-card .stat-icon {{ background: var(--accent-red-glow); color: var(--accent-red); }}

        /* Filter panel */
        .control-panel {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 25px;
            backdrop-filter: blur(16px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
        }}

        .scope-filters {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            padding-bottom: 16px;
        }}

        .scope-btn {{
            padding: 10px 20px;
            background: rgba(0, 0, 0, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .scope-btn:hover {{
            background: rgba(0, 0, 0, 0.05);
            color: #000000;
        }}

        .scope-btn.active {{
            background: rgba(0, 0, 0, 0.05);
            color: #000000;
            font-weight: 600;
        }}

        .scope-btn.active.all {{ border-color: var(--accent-blue); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1); }}
        .scope-btn.active.hq {{ border-color: var(--accent-blue); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1); }}
        .scope-btn.active.st {{ border-color: var(--accent-green); box-shadow: 0 4px 12px rgba(5, 150, 105, 0.1); }}
        .scope-btn.active.admin {{ border-color: var(--accent-red); box-shadow: 0 4px 12px rgba(225, 29, 72, 0.1); }}

        .search-filters-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: center;
        }}

        .search-box {{
            flex: 2;
            min-width: 300px;
            position: relative;
        }}

        .search-box input {{
            width: 100%;
            padding: 12px 40px 12px 42px;
            background: #FFFFFF;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 14px;
            transition: all 0.2s ease;
        }}

        .search-box input:focus {{
            border-color: var(--accent-blue);
            outline: none;
            box-shadow: 0 0 10px rgba(37, 99, 235, 0.15);
        }}

        .search-box .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            fill: var(--text-secondary);
            width: 16px;
            height: 16px;
            pointer-events: none;
        }}

        .search-box .clear-btn {{
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 4px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }}

        .search-box .clear-btn:hover {{
            color: #000000;
            background: rgba(0, 0, 0, 0.05);
        }}

        .select-group {{
            display: flex;
            gap: 12px;
            flex: 3;
            min-width: 350px;
        }}

        .select-group select {{
            flex: 1;
            padding: 12px 30px 12px 16px;
            background: #FFFFFF;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 14px;
            cursor: pointer;
            outline: none;
            transition: all 0.2s ease;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%234B5563' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 12px center;
        }}

        .select-group select:focus {{
            border-color: var(--accent-blue);
        }}

        .action-buttons {{
            display: flex;
            gap: 10px;
        }}

        .action-btn {{
            padding: 12px 18px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1px solid var(--border-color);
        }}

        .btn-secondary {{
            background: #FFFFFF;
            color: var(--text-primary);
        }}

        .btn-secondary:hover {{
            background: #F1F5F9;
            border-color: rgba(0, 0, 0, 0.15);
        }}

        .btn-primary {{
            background: rgba(37, 99, 235, 0.06);
            color: var(--accent-blue);
            border-color: rgba(37, 99, 235, 0.2);
        }}

        .btn-primary:hover {{
            background: rgba(37, 99, 235, 0.12);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}

        /* Grid / Table */
        .grid-container {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            overflow: hidden;
            backdrop-filter: blur(16px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
            margin-bottom: 40px;
        }}

        .table-wrapper {{
            overflow-x: auto;
            max-height: 65vh;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            text-align: left;
        }}

        th {{
            background: rgba(0, 0, 0, 0.02);
            padding: 16px 20px;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            cursor: pointer;
            user-select: none;
            transition: all 0.2s ease;
            position: sticky;
            top: 0;
            z-index: 10;
            backdrop-filter: blur(8px);
        }}

        th:hover {{
            color: #000000;
            background: rgba(0, 0, 0, 0.04);
        }}

        th.sorted-asc::after {{
            content: ' ▲';
            font-size: 10px;
            color: var(--accent-blue);
        }}

        th.sorted-desc::after {{
            content: ' ▼';
            font-size: 10px;
            color: var(--accent-blue);
        }}

        td {{
            padding: 15px 20px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            vertical-align: middle;
            color: var(--text-primary);
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tbody tr {{
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        tbody tr:hover {{
            background: rgba(37, 99, 235, 0.02);
        }}

        /* Styling cells */
        .seq-cell {{
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            color: var(--text-muted);
            text-align: center;
        }}

        .name-cell {{
            font-weight: 600;
            color: #0F172A;
        }}

        .file-cell {{
            font-family: 'Outfit', monospace;
            font-size: 13px;
            color: var(--text-secondary);
        }}

        .path-cell {{
            font-family: 'Outfit', monospace;
            font-size: 12px;
            color: var(--text-muted);
        }}

        .memo-cell {{
            font-size: 13px;
            color: var(--text-secondary);
            max-width: 250px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .row-complete-chk {{
            accent-color: var(--accent-blue);
        }}

        /* Badges */
        .tag {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}

        .tag-sys {{ background: var(--accent-red-glow); color: #B91C1C; border: 1px solid rgba(225, 29, 72, 0.15); }}
        .tag-mst {{ background: var(--accent-blue-glow); color: #1D4ED8; border: 1px solid rgba(37, 99, 235, 0.15); }}
        .tag-sales {{ background: var(--accent-orange-glow); color: #B45309; border: 1px solid rgba(217, 119, 6, 0.15); }}
        .tag-stock {{ background: var(--accent-green-glow); color: #047857; border: 1px solid rgba(5, 150, 105, 0.15); }}
        .tag-other {{ background: rgba(0, 0, 0, 0.04); color: var(--text-secondary); border: 1px solid var(--border-color); }}

        .tag-mclass {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            background: rgba(0, 0, 0, 0.02);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }}

        .scope-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .scope-hq {{ background: rgba(37, 99, 235, 0.08); color: var(--accent-blue); border: 1px solid rgba(37, 99, 235, 0.2); }}
        .scope-st {{ background: rgba(5, 150, 105, 0.08); color: var(--accent-green); border: 1px solid rgba(5, 150, 105, 0.2); }}
        .scope-admin {{ background: rgba(225, 29, 72, 0.08); color: var(--accent-red); border: 1px solid rgba(225, 29, 72, 0.2); }}

        /* Highlight text match */
        mark {{
            background: #FDE047;
            color: #000000;
            padding: 1px 3px;
            border-radius: 3px;
            font-weight: 600;
        }}

        .no-results {{
            padding: 60px;
            text-align: center;
            color: var(--text-secondary);
            font-size: 15px;
        }}

        /* Side details drawer */
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
            background: rgba(255, 255, 255, 0.96);
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
            font-family: 'Outfit', sans-serif;
            color: #0F172A;
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
            color: var(--text-secondary);
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
            color: var(--text-primary);
            background: rgba(0, 0, 0, 0.01);
            border: 1px solid rgba(0, 0, 0, 0.04);
            padding: 12px 16px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .detail-value.code-val {{
            font-family: 'Outfit', monospace;
            font-size: 13px;
        }}

        .copy-icon-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}

        .copy-icon-btn:hover {{
            color: #000000;
            background: rgba(0, 0, 0, 0.05);
        }}

        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translate(-50%, 100px);
            background: rgba(37, 99, 235, 0.95);
            color: #FFFFFF;
            padding: 12px 24px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 600;
            z-index: 1001;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25);
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            pointer-events: none;
        }}

        .toast.show {{
            transform: translate(-50%, 0);
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Dashboard Header -->
        <header>
            <div class="title-area">
                <h1>HMS Screen Directory <span class="logo-badge">ACTIVE</span></h1>
                <p>HMS 영업정보시스템 화면 및 호출 정보 대시보드 (MENUMMTB 마스터 연동)</p>
            </div>
            <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                <div id="progress-summary" style="font-size: 12.5px; color: var(--text-secondary); background: rgba(0,0,0,0.03); padding: 6px 14px; border-radius: 20px; border: 1px solid var(--border-color); font-weight: 500;">
                    0 / 0 완료 (0%)
                </div>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--text-secondary);">
                    <span>저장 파일명:</span>
                    <input type="text" id="export-filename" value="hms_screens_progress.json" style="padding: 6px 10px; font-size: 12px; border-radius: 8px; border: 1px solid var(--border-color); outline: none; width: 160px; background: #FFF;">
                </div>
                <button onclick="exportProgress()" class="action-btn btn-primary" style="padding: 6px 12px; font-size: 12px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 4px;">📝 진행상황 백업 (JSON)</button>
                <button onclick="importProgress()" class="action-btn btn-primary" style="padding: 6px 12px; font-size: 12px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 4px;">📥 진행상황 복원 (JSON)</button>
                <input type="file" id="import-progress-file" style="display: none;" accept=".json" onchange="handleImportProgress(event)">
                <div class="badge-total" id="matched-counter" style="background: var(--text-primary); color: white; padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600;">
                    Showing 0 of 0 screens
                </div>
            </div>
        </header>

        <!-- Stats Overview Row -->
        <div class="stats-grid">
            <div class="stat-card all-card">
                <div class="stat-info">
                    <div class="stat-label">전체 화면 수</div>
                    <div class="stat-value" id="stat-total">0</div>
                </div>
                <div class="stat-icon">ALL</div>
            </div>
            <div class="stat-card hq-card">
                <div class="stat-info">
                    <div class="stat-label">본사 화면 (hq_)</div>
                    <div class="stat-value" id="stat-hq">0</div>
                </div>
                <div class="stat-icon">HQ</div>
            </div>
            <div class="stat-card st-card">
                <div class="stat-info">
                    <div class="stat-label">매장 화면 (st_)</div>
                    <div class="stat-value" id="stat-st">0</div>
                </div>
                <div class="stat-icon">ST</div>
            </div>
            <div class="stat-card admin-card">
                <div class="stat-info">
                    <div class="stat-label">어드민 화면 (admin_)</div>
                    <div class="stat-value" id="stat-admin">0</div>
                </div>
                <div class="stat-icon">ADM</div>
            </div>
        </div>

        <!-- Filter Panel -->
        <div class="control-panel">
            <!-- Scope selection pills -->
            <div class="scope-filters">
                <button class="scope-btn active all" data-scope="all">
                    <span>전체보기</span>
                </button>
                <button class="scope-btn hq" data-scope="hq">
                    <span class="scope-badge scope-hq">HQ</span>
                    <span>본사 전용</span>
                </button>
                <button class="scope-btn st" data-scope="st">
                    <span class="scope-badge scope-st">Store</span>
                    <span>매장 전용</span>
                </button>
                <button class="scope-btn admin" data-scope="admin">
                    <span class="scope-badge scope-admin">Admin</span>
                    <span>시스템 관리자</span>
                </button>
            </div>

            <!-- Text Search & Select dropdowns -->
            <div class="search-filters-row">
                <div class="search-box">
                    <svg class="search-icon" viewBox="0 0 24 24">
                        <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                    </svg>
                    <input type="text" id="search-input" placeholder="화면코드, 화면명, 파일명, 메모 검색..." autocomplete="off">
                    <button class="clear-btn" id="clear-search" style="display: none;">✕</button>
                </div>
                
                <div class="select-group">
                    <select id="lclass-filter">
                        <option value="">대분류 전체</option>
                        {lclass_options}
                    </select>

                    <select id="mclass-filter">
                        <option value="">중분류 전체</option>
                    </select>

                    <select id="complete-filter">
                        <option value="">완료여부 전체</option>
                        <option value="completed">테스트 완료</option>
                        <option value="incomplete">테스트 미완료</option>
                    </select>
                </div>

                <div class="action-buttons">
                    <button class="action-btn btn-secondary" id="reset-filters">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
                        </svg>
                        초기화
                    </button>
                    <button class="action-btn btn-primary" id="export-csv">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
                        </svg>
                        CSV 내보내기
                    </button>
                </div>
            </div>
        </div>

        <!-- Screens Grid Table -->
        <div class="grid-container">
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 70px; text-align: center;" data-sort="complete">완료</th>
                            <th style="width: 100px; text-align: center;" data-sort="seq">화면코드</th>
                            <th style="width: 100px; text-align: center;" data-sort="scope">유형</th>
                            <th style="width: 120px;" data-sort="lclass">대분류</th>
                            <th style="width: 130px;" data-sort="mclass">중분류</th>
                            <th data-sort="name">화면명 (MENU_NM)</th>
                            <th data-sort="custom_name">사용자 화면명</th>
                            <th data-sort="file">물리 파일명 (VIEW_FILE)</th>
                            <th data-sort="path">호출 경로 (VIEW_PATH)</th>
                            <th style="width: 160px;" data-sort="memo">사용자 메모</th>
                            <th style="width: 140px;" data-sort="test_case">TestCase</th>
                            <th style="width: 140px;" data-sort="qa_report">QaReport</th>
                            <th style="width: 160px;" data-sort="data_flow">데이터 흐름 가이드</th>
                            <th style="width: 160px;" data-sort="data_input">데이터 가공</th>
                            <th style="width: 160px;" data-sort="trigger">DB 트리거</th>
                        </tr>
                    </thead>
                    <tbody id="table-body">
                        <!-- Dynamic Rows -->
                    </tbody>
                </table>
            </div>
            <div id="no-results-msg" class="no-results" style="display: none;">
                검색 조건에 맞는 화면이 존재하지 않습니다.
            </div>
        </div>
    </div>

    <!-- Side details drawer -->
    <div class="drawer-overlay" id="drawer-overlay"></div>
    <div class="drawer" id="detail-drawer">
        <div class="drawer-header">
            <h2>화면 상세 정보</h2>
            <button class="close-btn" id="close-drawer">✕</button>
        </div>
        <div class="drawer-content" style="display: grid; grid-template-columns: 420px 1fr; gap: 24px; align-items: start;">
            <!-- Left Info Column -->
            <div style="display: flex; flex-direction: column; gap: 16px; min-width: 0;">
                <div class="detail-group">
                    <div class="detail-label">화면 유형</div>
                    <div id="detail-scope"></div>
                </div>
                <div class="detail-group">
                    <div class="detail-label">화면코드</div>
                    <div class="detail-value code-val" id="detail-seq"></div>
                </div>
                <div class="detail-group">
                    <div class="detail-label">대분류</div>
                    <div class="detail-value" id="detail-lclass"></div>
                </div>
                <div class="detail-group">
                    <div class="detail-label">중분류</div>
                    <div class="detail-value" id="detail-mclass"></div>
                </div>
                <div class="detail-group">
                    <div class="detail-label">화면명 (MENU_NM)</div>
                    <div class="detail-value" id="detail-name" style="font-weight: 600;"></div>
                </div>
                <div class="detail-group">
                    <div class="detail-label">JSP 파일명 (VIEW_FILE)</div>
                    <div class="detail-value code-val">
                        <span id="detail-file"></span>
                        <button class="copy-icon-btn" onclick="copyText('detail-file')">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="detail-group">
                    <div class="detail-label">호출 경로 (VIEW_PATH)</div>
                    <div class="detail-value code-val">
                        <span id="detail-path"></span>
                        <button class="copy-icon-btn" onclick="copyText('detail-path')">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="detail-group">
                    <div class="detail-label">Full URL (Spring Controller 호출용)</div>
                    <div class="detail-value code-val">
                        <span id="detail-full-url"></span>
                        <button class="copy-icon-btn" onclick="copyText('detail-full-url')">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="detail-group">
                    <div class="detail-label">DBeaver 권한 매핑 조회용 SQL</div>
                    <div class="detail-value code-val" style="background: rgba(0,0,0,0.03); font-size: 12px; white-space: pre-wrap; display: block; overflow-x: auto; max-height: 120px; line-height: 1.5; padding: 12px 14px;">
                        <span id="detail-sql-query"></span>
                    </div>
                </div>
            </div>
            
            <!-- Right Memo Column -->
            <div style="display: flex; flex-direction: column; gap: 16px; height: 100%;">
                <div class="detail-group" style="background: rgba(37, 99, 235, 0.04); border: 1px dashed rgba(37, 99, 235, 0.2); padding: 20px; border-radius: 12px; height: 100%; display: flex; flex-direction: column; justify-content: flex-start;">
                    <div class="detail-label" style="color: var(--accent-blue); font-weight: 700;">진행 상태 & 메모 관리</div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 12px; margin-bottom: 16px;">
                        <input type="checkbox" id="detail-complete-chk" style="width: 18px; height: 18px; cursor: pointer;">
                        <label for="detail-complete-chk" style="font-size: 14px; font-weight: 600; cursor: pointer;">테스트 완료</label>
                    </div>
                    <div class="detail-label" style="margin-bottom: 8px;">사용자지정 화면명 (Custom Name)</div>
                    <input type="text" id="detail-custom-name-txt" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13.5px; outline: none; margin-bottom: 16px;" placeholder="사용자 지정 화면명 입력...">
                    <div class="detail-label" style="margin-bottom: 8px;">TestCase 파일 경로</div>
                    <input type="text" id="detail-test-case-txt" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13.5px; outline: none; margin-bottom: 16px;" placeholder="D:\path\to\TestCase.md 형식으로 입력...">
                    <div class="detail-label" style="margin-bottom: 8px;">QaReport 파일 경로</div>
                    <input type="text" id="detail-qa-report-txt" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13.5px; outline: none; margin-bottom: 16px;" placeholder="D:\path\to\QaReport.md 형식으로 입력...">
                    <div class="detail-label" style="margin-bottom: 8px;">데이터 흐름 가이드 파일 경로</div>
                    <input type="text" id="detail-data-flow-txt" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13.5px; outline: none; margin-bottom: 16px;" placeholder="D:\path\to\guide.md 형식으로 입력...">
                    <div class="detail-label" style="margin-bottom: 8px;">데이터 가공 파일 경로</div>
                    <input type="text" id="detail-data-input-txt" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13.5px; outline: none; margin-bottom: 16px;" placeholder="D:\path\to\DataInput.md 형식으로 입력...">
                    <div class="detail-label" style="margin-bottom: 8px;">DB 트리거 파일 경로</div>
                    <input type="text" id="detail-trigger-txt" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13.5px; outline: none; margin-bottom: 16px;" placeholder="D:\path\to\trigger.md 형식으로 입력...">
                    <div class="detail-label" style="margin-bottom: 8px;">사용자 메모</div>
                    <textarea id="detail-memo-txt" style="width: 100%; flex-grow: 1; min-height: 200px; padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 13.5px; resize: vertical; outline: none; transition: border-color 0.2s;" placeholder="화면 관련 메모 입력..."></textarea>
                    <div style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px;">
                        <button onclick="saveDetailProgress()" class="action-btn btn-primary" style="padding: 8px 18px; font-size: 13px; border-radius: 6px; cursor: pointer; background: var(--accent-blue); color: white;">저장</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast" id="toast-msg">복사되었습니다.</div>

    <script>
        // Loaded screen database
        const screensData = {screens_json};

        // UI States
        let activeScope = 'all';
        let currentSortColumn = 'seq';
        let currentSortDirection = 'asc';

        // Element handles
        const searchInput = document.getElementById('search-input');
        const clearSearchBtn = document.getElementById('clear-search');
        const lclassFilter = document.getElementById('lclass-filter');
        const mclassFilter = document.getElementById('mclass-filter');
        const completeFilter = document.getElementById('complete-filter');
        const resetBtn = document.getElementById('reset-filters');
        const exportCsvBtn = document.getElementById('export-csv');
        const tableBody = document.getElementById('table-body');
        const noResultsMsg = document.getElementById('no-results-msg');
        const matchedCounter = document.getElementById('matched-counter');
        const tableHeaders = document.querySelectorAll('th[data-sort]');

        const drawer = document.getElementById('detail-drawer');
        const drawerOverlay = document.getElementById('drawer-overlay');
        const closeDrawerBtn = document.getElementById('close-drawer');
        const toast = document.getElementById('toast-msg');

        // Dynamic Large to Medium Category Map
        const lToMMapping = {{}};
        screensData.forEach(s => {{
            if (!lToMMapping[s.lclass]) {{
                lToMMapping[s.lclass] = [];
            }}
            if (!lToMMapping[s.lclass].includes(s.mclass)) {{
                lToMMapping[s.lclass].push(s.mclass);
            }}
        }});
        Object.keys(lToMMapping).forEach(l => {{
            lToMMapping[l].sort();
        }});

        // Helper functions
        function getScope(filename) {{
            if (filename.startsWith('hq_')) return 'HQ';
            if (filename.startsWith('st_')) return 'Store';
            if (filename.startsWith('admin_')) return 'Admin';
            return 'Other';
        }}

        function getTagClass(lclass) {{
            if (lclass.includes('시스템')) return 'tag-sys';
            if (lclass.includes('마스터')) return 'tag-mst';
            if (lclass.includes('매출') || lclass.includes('승인')) return 'tag-sales';
            if (lclass.includes('재고') || lclass.includes('매입')) return 'tag-stock';
            return 'tag-other';
        }}

        function getScopeBadge(scope) {{
            if (scope === 'HQ') return `<span class="scope-badge scope-hq">HQ</span>`;
            if (scope === 'Store') return `<span class="scope-badge scope-st">Store</span>`;
            if (scope === 'Admin') return `<span class="scope-badge scope-admin">Admin</span>`;
            return `<span class="scope-badge" style="background: rgba(255,255,255,0.05); color: var(--text-secondary);">Other</span>`;
        }}

        function highlightMatch(text, query) {{
            if (!query) return text;
            const index = text.toLowerCase().indexOf(query.toLowerCase());
            if (index === -1) return text;
            
            const rawMatch = text.substring(index, index + query.length);
            return text.substring(0, index) + `<mark>${{rawMatch}}</mark>` + text.substring(index + query.length);
        }}

        // Local Storage Helpers
        function isScreenCompleted(file) {{
            const val = localStorage.getItem("screen:complete:" + file);
            if (val !== null) {{
                return val === "true";
            }}
            const item = screensData.find(s => s.file === file);
            return item ? (item.custom_complete === true) : false;
        }}

        function getScreenMemo(file) {{
            const val = localStorage.getItem("screen:memo:" + file);
            if (val !== null && val.trim() !== "") {{
                return val;
            }}
            const item = screensData.find(s => s.file === file);
            return item ? (item.custom_memo || "") : "";
        }}

        function getScreenCustomName(file) {{
            const val = localStorage.getItem("screen:custom_name:" + file);
            if (val !== null && val.trim() !== "") {{
                return val;
            }}
            const item = screensData.find(s => s.file === file);
            return item ? (item.custom_name || "") : "";
        }}

        function getScreenDataFlow(file) {{
            const val = localStorage.getItem("screen:data_flow:" + file);
            if (val !== null && val.trim() !== "") {{
                return val;
            }}
            const item = screensData.find(s => s.file === file);
            return item ? (item.data_flow || "") : "";
        }}

        function getScreenDataInput(file) {{
            const val = localStorage.getItem("screen:data_input:" + file);
            if (val !== null && val.trim() !== "") {{
                return val;
            }}
            const item = screensData.find(s => s.file === file);
            return item ? (item.data_input || "") : "";
        }}

        function getScreenTrigger(file) {{
            const val = localStorage.getItem("screen:trigger:" + file);
            if (val !== null && val.trim() !== "") {{
                return val;
            }}
            const item = screensData.find(s => s.file === file);
            return item ? (item.trigger || "") : "";
        }}

        function getScreenTestCase(file) {{
            const val = localStorage.getItem("screen:test_case:" + file);
            if (val !== null && val.trim() !== "") {{
                return val;
            }}
            const item = screensData.find(s => s.file === file);
            return item ? (item.test_case || "") : "";
        }}

        function getScreenQaReport(file) {{
            const val = localStorage.getItem("screen:qa_report:" + file);
            if (val !== null && val.trim() !== "") {{
                return val;
            }}
            const item = screensData.find(s => s.file === file);
            return item ? (item.qa_report || "") : "";
        }}

        function toggleRowComplete(event, file) {{
            event.stopPropagation(); // Stop row click (open drawer)
            const checked = event.target.checked;
            if (checked) {{
                localStorage.setItem("screen:complete:" + file, "true");
            }} else {{
                localStorage.removeItem("screen:complete:" + file);
            }}
            
            const memo = getScreenMemo(file);
            const customName = getScreenCustomName(file);
            const dataFlow = getScreenDataFlow(file);
            const dataInput = getScreenDataInput(file);
            const trigger = getScreenTrigger(file);
            const testCase = getScreenTestCase(file);
            const qaReport = getScreenQaReport(file);

            // 실시간 파일 연동 API 전송
            fetch('http://localhost:8000/api/save', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    file: file,
                    complete: checked,
                    memo: memo,
                    custom_name: customName,
                    data_flow: dataFlow,
                    data_input: dataInput,
                    trigger: trigger,
                    test_case: testCase,
                    qa_report: qaReport
                }})
            }}).then(response => response.json())
            .then(data => {{
                console.log('Status saved to local file:', data);
                updateStats();
            }}).catch(err => {{
                console.warn('Failed to sync state to local server:', err);
                updateStats();
            }});
        }}

        // Dynamic Chained Dropdowns
        lclassFilter.addEventListener('change', () => {{
            const selectedL = lclassFilter.value;
            const previousM = mclassFilter.value;
            
            mclassFilter.innerHTML = '<option value="">중분류 전체</option>';
            
            if (!selectedL) {{
                const allM = new Set();
                screensData.forEach(s => allM.add(s.mclass));
                Array.from(allM).sort().forEach(m => {{
                    mclassFilter.innerHTML += `<option value="${{m}}">${{m}}</option>`;
                }});
            }} else {{
                const matchedM = lToMMapping[selectedL] || [];
                matchedM.forEach(m => {{
                    mclassFilter.innerHTML += `<option value="${{m}}">${{m}}</option>`;
                }});
            }}
            
            if (Array.from(mclassFilter.options).some(o => o.value === previousM)) {{
                mclassFilter.value = previousM;
            }}
            
            filterData();
        }});

        mclassFilter.addEventListener('change', filterData);
        completeFilter.addEventListener('change', filterData);

        // Sorting event listeners
        tableHeaders.forEach(th => {{
            th.addEventListener('click', () => {{
                const sortCol = th.getAttribute('data-sort');
                if (currentSortColumn === sortCol) {{
                    currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
                }} else {{
                    currentSortColumn = sortCol;
                    currentSortDirection = 'asc';
                }}
                
                tableHeaders.forEach(h => h.className = '');
                th.classList.add(currentSortDirection === 'asc' ? 'sorted-asc' : 'sorted-desc');
                
                filterData();
            }});
        }});

        // Render Table Grid
        function renderTable(data, searchQuery) {{
            tableBody.innerHTML = '';
            matchedCounter.innerText = `Showing ${{data.length}} of ${{screensData.length}} screens`;

            if (data.length === 0) {{
                noResultsMsg.style.display = 'block';
                return;
            }}
            noResultsMsg.style.display = 'none';

            data.forEach(item => {{
                const tr = document.createElement('tr');
                const scope = getScope(item.file);
                const scopeBadge = getScopeBadge(scope);
                const tagClass = getTagClass(item.lclass);
                
                const isCompleted = isScreenCompleted(item.file);
                const memoText = getScreenMemo(item.file);
                const customNameText = getScreenCustomName(item.file);
                const dataFlowText = getScreenDataFlow(item.file);
                const safeLink = dataFlowText ? `file:///${{dataFlowText.replace(/\\\\/g, '/')}}` : '';
                const actualFileName = dataFlowText ? dataFlowText.substring(Math.max(dataFlowText.lastIndexOf('/'), dataFlowText.lastIndexOf('\\\\')) + 1) : '';

                const dataInputText = getScreenDataInput(item.file);
                const safeDataInputLink = dataInputText ? `file:///${{dataInputText.replace(/\\\\/g, '/')}}` : '';
                const actualDataInputName = dataInputText ? dataInputText.substring(Math.max(dataInputText.lastIndexOf('/'), dataInputText.lastIndexOf('\\\\')) + 1) : '';

                const triggerText = getScreenTrigger(item.file);
                const safeTriggerLink = triggerText ? `file:///${{triggerText.replace(/\\\\/g, '/')}}` : '';
                const actualTriggerName = triggerText ? triggerText.substring(Math.max(triggerText.lastIndexOf('/'), triggerText.lastIndexOf('\\\\')) + 1) : '';

                const testCaseText = getScreenTestCase(item.file);
                const safeTestCaseLink = testCaseText ? `file:///${{testCaseText.replace(/\\\\/g, '/')}}` : '';
                const actualTestCaseName = testCaseText ? testCaseText.substring(Math.max(testCaseText.lastIndexOf('/'), testCaseText.lastIndexOf('\\\\')) + 1) : '';

                const qaReportText = getScreenQaReport(item.file);
                const safeQaReportLink = qaReportText ? `file:///${{qaReportText.replace(/\\\\/g, '/')}}` : '';
                const actualQaReportName = qaReportText ? qaReportText.substring(Math.max(qaReportText.lastIndexOf('/'), qaReportText.lastIndexOf('\\\\')) + 1) : '';

                tr.addEventListener('click', () => {{
                    const selection = window.getSelection().toString();
                    if (selection) {{
                        return;
                    }}
                    openDrawer(item);
                }});

                tr.innerHTML = `
                    <td style="text-align: center;">
                        <input type="checkbox" class="row-complete-chk" ${{isCompleted ? 'checked' : ''}} onclick="toggleRowComplete(event, '${{item.file}}')" style="width: 16px; height: 16px; cursor: pointer;">
                    </td>
                    <td class="seq-cell">${{highlightMatch(item.seq, searchQuery)}}</td>
                    <td style="text-align: center;">${{scopeBadge}}</td>
                    <td><span class="tag ${{tagClass}}">${{item.lclass}}</span></td>
                    <td><span class="tag tag-mclass">${{item.mclass}}</span></td>
                    <td class="name-cell">${{highlightMatch(item.name, searchQuery)}}</td>
                    <td class="custom-name-cell" style="font-weight: 500; color: var(--accent-blue);">${{customNameText ? highlightMatch(customNameText, searchQuery) : '<span style="color:#cbd5e1; font-size:12px;">지정 없음</span>'}}</td>
                    <td class="file-cell">${{highlightMatch(item.file, searchQuery)}}</td>
                    <td class="path-cell">${{item.path}}</td>
                    <td class="memo-cell">
                        ${{memoText ? `📝 ${{highlightMatch(memoText, searchQuery)}}` : '<span style="color:#cbd5e1; font-size:12px;">메모 없음</span>'}}
                    </td>
                    <td class="test-case-cell" style="font-family: 'Outfit', monospace; font-size: 12px; color: var(--accent-blue);">
                        ${{testCaseText ? `<a href="${{safeTestCaseLink}}" target="_blank" onclick="event.stopPropagation()" style="text-decoration: none; color: var(--accent-blue); font-weight: 600;">🔗 ${{highlightMatch(actualTestCaseName, searchQuery)}}</a>` : '<span style="color:#cbd5e1; font-size:12px;">-</span>'}}
                    </td>
                    <td class="qa-report-cell" style="font-family: 'Outfit', monospace; font-size: 12px; color: var(--accent-blue);">
                        ${{qaReportText ? `<a href="${{safeQaReportLink}}" target="_blank" onclick="event.stopPropagation()" style="text-decoration: none; color: var(--accent-blue); font-weight: 600;">🔗 ${{highlightMatch(actualQaReportName, searchQuery)}}</a>` : '<span style="color:#cbd5e1; font-size:12px;">-</span>'}}
                    </td>
                    <td class="data-flow-cell" style="font-family: 'Outfit', monospace; font-size: 12px; color: var(--accent-blue);">
                        ${{dataFlowText ? `<a href="${{safeLink}}" target="_blank" onclick="event.stopPropagation()" style="text-decoration: none; color: var(--accent-blue); font-weight: 600;">🔗 ${{highlightMatch(actualFileName, searchQuery)}}</a>` : '<span style="color:#cbd5e1; font-size:12px;">-</span>'}}
                    </td>
                    <td class="data-input-cell" style="font-family: 'Outfit', monospace; font-size: 12px; color: var(--accent-blue);">
                        ${{dataInputText ? `<a href="${{safeDataInputLink}}" target="_blank" onclick="event.stopPropagation()" style="text-decoration: none; color: var(--accent-blue); font-weight: 600;">🔗 ${{highlightMatch(actualDataInputName, searchQuery)}}</a>` : '<span style="color:#cbd5e1; font-size:12px;">-</span>'}}
                    </td>
                    <td class="trigger-cell" style="font-family: 'Outfit', monospace; font-size: 12px; color: var(--accent-blue);">
                        ${{triggerText ? `<a href="${{safeTriggerLink}}" target="_blank" onclick="event.stopPropagation()" style="text-decoration: none; color: var(--accent-blue); font-weight: 600;">🔗 ${{highlightMatch(actualTriggerName, searchQuery)}}</a>` : '<span style="color:#cbd5e1; font-size:12px;">-</span>'}}
                    </td>
                `;
                tableBody.appendChild(tr);
            }});
        }}

        // Filter & Sort core logic
        function filterData() {{
            const searchVal = searchInput.value.toLowerCase().trim();
            const lclassVal = lclassFilter.value;
            const mclassVal = mclassFilter.value;
            const completeVal = completeFilter.value;
            
            clearSearchBtn.style.display = searchVal ? 'flex' : 'none';

            let filtered = screensData.filter(item => {{
                // Text search match (includes memo text, custom name text and data flow text)
                const memoText = getScreenMemo(item.file);
                const customNameText = getScreenCustomName(item.file);
                const dataFlowText = getScreenDataFlow(item.file);
                const dataInputText = getScreenDataInput(item.file);
                const triggerText = getScreenTrigger(item.file);
                const testCaseText = getScreenTestCase(item.file);
                const qaReportText = getScreenQaReport(item.file);
                
                const matchesSearch = !searchVal || 
                    item.name.toLowerCase().includes(searchVal) || 
                    item.seq.toLowerCase().includes(searchVal) || 
                    item.file.toLowerCase().includes(searchVal) ||
                    memoText.toLowerCase().includes(searchVal) ||
                    customNameText.toLowerCase().includes(searchVal) ||
                    dataFlowText.toLowerCase().includes(searchVal) ||
                    dataInputText.toLowerCase().includes(searchVal) ||
                    triggerText.toLowerCase().includes(searchVal) ||
                    testCaseText.toLowerCase().includes(searchVal) ||
                    qaReportText.toLowerCase().includes(searchVal);
                
                const matchesLclass = !lclassVal || item.lclass === lclassVal;
                const matchesMclass = !mclassVal || item.mclass === mclassVal;
                
                const scope = getScope(item.file);
                let matchesScope = true;
                if (activeScope === 'hq') matchesScope = scope === 'HQ';
                else if (activeScope === 'st') matchesScope = scope === 'Store';
                else if (activeScope === 'admin') matchesScope = scope === 'Admin';

                const isCompleted = isScreenCompleted(item.file);
                let matchesComplete = true;
                if (completeVal === 'completed') matchesComplete = isCompleted;
                else if (completeVal === 'incomplete') matchesComplete = !isCompleted;

                return matchesSearch && matchesLclass && matchesMclass && matchesScope && matchesComplete;
            }});

            // Apply sort
            filtered.sort((a, b) => {{
                let valA, valB;
                
                if (currentSortColumn === 'seq') {{
                    valA = a.seq;
                    valB = b.seq;
                }} else if (currentSortColumn === 'scope') {{
                    valA = getScope(a.file);
                    valB = getScope(b.file);
                }} else if (currentSortColumn === 'lclass') {{
                    valA = a.lclass;
                    valB = b.lclass;
                }} else if (currentSortColumn === 'mclass') {{
                    valA = a.mclass;
                    valB = b.mclass;
                }} else if (currentSortColumn === 'name') {{
                    valA = a.name;
                    valB = b.name;
                }} else if (currentSortColumn === 'file') {{
                    valA = a.file;
                    valB = b.file;
                }} else if (currentSortColumn === 'path') {{
                    valA = a.path;
                    valB = b.path;
                }} else if (currentSortColumn === 'complete') {{
                    valA = isScreenCompleted(a.file) ? 1 : 0;
                    valB = isScreenCompleted(b.file) ? 1 : 0;
                }} else if (currentSortColumn === 'memo') {{
                    valA = getScreenMemo(a.file);
                    valB = getScreenMemo(b.file);
                }} else if (currentSortColumn === 'custom_name') {{
                    valA = getScreenCustomName(a.file);
                    valB = getScreenCustomName(b.file);
                }} else if (currentSortColumn === 'data_flow') {{
                    valA = getScreenDataFlow(a.file);
                    valB = getScreenDataFlow(b.file);
                }} else if (currentSortColumn === 'test_case') {{
                    valA = getScreenTestCase(a.file);
                    valB = getScreenTestCase(b.file);
                }} else if (currentSortColumn === 'qa_report') {{
                    valA = getScreenQaReport(a.file);
                    valB = getScreenQaReport(b.file);
                }} else if (currentSortColumn === 'data_input') {{
                    valA = getScreenDataInput(a.file);
                    valB = getScreenDataInput(b.file);
                }} else if (currentSortColumn === 'trigger') {{
                    valA = getScreenTrigger(a.file);
                    valB = getScreenTrigger(b.file);
                }}

                if (valA < valB) return currentSortDirection === 'asc' ? -1 : 1;
                if (valA > valB) return currentSortDirection === 'asc' ? 1 : -1;
                return 0;
            }});

            renderTable(filtered, searchVal);
            updateStats();
        }}

        // Search Input listeners
        searchInput.addEventListener('input', filterData);
        clearSearchBtn.addEventListener('click', () => {{
            searchInput.value = '';
            filterData();
        }});

        // Scope filter click handling
        const scopeBtns = document.querySelectorAll('.scope-btn');
        scopeBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                scopeBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeScope = btn.getAttribute('data-scope');
                filterData();
            }});
        }});

        // Reset Filters action
        resetBtn.addEventListener('click', () => {{
            searchInput.value = '';
            lclassFilter.value = '';
            mclassFilter.value = '';
            completeFilter.value = '';
            activeScope = 'all';
            
            scopeBtns.forEach(b => b.classList.remove('active'));
            document.querySelector('.scope-btn.all').classList.add('active');
            
            mclassFilter.innerHTML = '<option value="">중분류 전체</option>';
            const allM = new Set();
            screensData.forEach(s => allM.add(s.mclass));
            Array.from(allM).sort().forEach(m => {{
                mclassFilter.innerHTML += `<option value="${{m}}">${{m}}</option>`;
            }});
            
            filterData();
        }});

        // Stats card counters & progress update
        function updateStats() {{
            let countHq = 0;
            let countSt = 0;
            let countAdmin = 0;
            let completedCount = 0;

            screensData.forEach(s => {{
                const sc = getScope(s.file);
                if (sc === 'HQ') countHq++;
                else if (sc === 'Store') countSt++;
                else if (sc === 'Admin') countAdmin++;

                if (isScreenCompleted(s.file)) {{
                    completedCount++;
                }}
            }});

            const progressPct = screensData.length > 0 ? ((completedCount / screensData.length) * 100).toFixed(1) : 0;
            
            document.getElementById('stat-total').innerText = screensData.length;
            document.getElementById('stat-hq').innerText = countHq;
            document.getElementById('stat-st').innerText = countSt;
            document.getElementById('stat-admin').innerText = countAdmin;

            document.getElementById('progress-summary').innerHTML = `
                <span style="color: var(--accent-blue); font-weight: 700;">${{completedCount}}</span> / ${{screensData.length}} 완료 (${{progressPct}}%)
            `;
        }}

        // Details drawer logic
        let activeDrawerItem = null;
        function openDrawer(item) {{
            activeDrawerItem = item;
            const scope = getScope(item.file);
            document.getElementById('detail-scope').innerHTML = getScopeBadge(scope);
            document.getElementById('detail-seq').innerText = item.seq;
            document.getElementById('detail-lclass').innerText = item.lclass;
            document.getElementById('detail-mclass').innerText = item.mclass;
            document.getElementById('detail-name').innerText = item.name;
            document.getElementById('detail-file').innerText = item.file;
            document.getElementById('detail-path').innerText = item.path;
            
            const fullUrl = item.path + '/' + item.file;
            document.getElementById('detail-full-url').innerText = fullUrl;

            const querySql = `SELECT * FROM hmsfns.MENUMMTB \\nWHERE VIEW_FILE = '${{item.file}}';\\n\\n-- 사용자 권한 맵핑 조회\\nSELECT u.user_id, u.user_nm, m.menu_seq, m.menu_nm\\nFROM hmsfns.MUSERSTB u\\nJOIN hmsfns.USERMLTB um ON u.user_id = um.user_id\\nJOIN hmsfns.MENUMMTB m ON um.menu_seq = m.menu_seq\\nWHERE m.VIEW_FILE = '${{item.file}}';`;
            document.getElementById('detail-sql-query').innerText = querySql;

            // Set progress chk and memo txt
            document.getElementById('detail-complete-chk').checked = isScreenCompleted(item.file);
            document.getElementById('detail-memo-txt').value = getScreenMemo(item.file);
            document.getElementById('detail-custom-name-txt').value = getScreenCustomName(item.file);
            document.getElementById('detail-test-case-txt').value = getScreenTestCase(item.file);
            document.getElementById('detail-qa-report-txt').value = getScreenQaReport(item.file);
            document.getElementById('detail-data-flow-txt').value = getScreenDataFlow(item.file);
            document.getElementById('detail-data-input-txt').value = getScreenDataInput(item.file);
            document.getElementById('detail-trigger-txt').value = getScreenTrigger(item.file);

            drawer.classList.add('open');
            drawerOverlay.style.display = 'block';
            setTimeout(() => {{
                drawerOverlay.style.opacity = '1';
            }}, 10);
        }}

        function saveData() {{
            if (!activeDrawerItem) return false;
            const file = activeDrawerItem.file;
            const checked = document.getElementById('detail-complete-chk').checked;
            const memo = document.getElementById('detail-memo-txt').value.trim();
            const customName = document.getElementById('detail-custom-name-txt').value.trim();
            const dataFlow = document.getElementById('detail-data-flow-txt').value.trim();
            const dataInput = document.getElementById('detail-data-input-txt').value.trim();
            const trigger = document.getElementById('detail-trigger-txt').value.trim();
            const testCase = document.getElementById('detail-test-case-txt').value.trim();
            const qaReport = document.getElementById('detail-qa-report-txt').value.trim();

            const prevChecked = isScreenCompleted(file);
            const prevMemo = getScreenMemo(file);
            const prevCustomName = getScreenCustomName(file);
            const prevDataFlow = getScreenDataFlow(file);
            const prevDataInput = getScreenDataInput(file);
            const prevTrigger = getScreenTrigger(file);
            const prevTestCase = getScreenTestCase(file);
            const prevQaReport = getScreenQaReport(file);
            if (checked === prevChecked && memo === prevMemo && customName === prevCustomName && dataFlow === prevDataFlow && dataInput === prevDataInput && trigger === prevTrigger && testCase === prevTestCase && qaReport === prevQaReport) {{
                return false;
            }}

            if (checked) {{
                localStorage.setItem("screen:complete:" + file, "true");
            }} else {{
                localStorage.removeItem("screen:complete:" + file);
            }}

            if (memo) {{
                localStorage.setItem("screen:memo:" + file, memo);
            }} else {{
                localStorage.removeItem("screen:memo:" + file);
            }}

            if (customName) {{
                localStorage.setItem("screen:custom_name:" + file, customName);
            }} else {{
                localStorage.removeItem("screen:custom_name:" + file);
            }}

            if (dataFlow) {{
                localStorage.setItem("screen:data_flow:" + file, dataFlow);
            }} else {{
                localStorage.removeItem("screen:data_flow:" + file);
            }}

            if (dataInput) {{
                localStorage.setItem("screen:data_input:" + file, dataInput);
            }} else {{
                localStorage.removeItem("screen:data_input:" + file);
            }}

            if (trigger) {{
                localStorage.setItem("screen:trigger:" + file, trigger);
            }} else {{
                localStorage.removeItem("screen:trigger:" + file);
            }}

            if (testCase) {{
                localStorage.setItem("screen:test_case:" + file, testCase);
            }} else {{
                localStorage.removeItem("screen:test_case:" + file);
            }}

            if (qaReport) {{
                localStorage.setItem("screen:qa_report:" + file, qaReport);
            }} else {{
                localStorage.removeItem("screen:qa_report:" + file);
            }}

            // 실시간 백엔드 파일 연동 API 전송
            fetch('http://localhost:8000/api/save', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    file: file,
                    complete: checked,
                    memo: memo,
                    custom_name: customName,
                    data_flow: dataFlow,
                    data_input: dataInput,
                    trigger: trigger,
                    test_case: testCase,
                    qa_report: qaReport
                }})
            }}).then(response => response.json())
            .then(data => {{
                console.log('Progress successfully synchronized to file:', data);
            }}).catch(err => {{
                console.warn('Failed to sync progress to local server:', err);
            }});

            return true;
        }}

        function closeDrawer() {{
            const changed = saveData();
            
            drawer.classList.remove('open');
            drawerOverlay.style.opacity = '0';
            setTimeout(() => {{
                drawerOverlay.style.display = 'none';
            }}, 300);
            activeDrawerItem = null;
            
            if (changed) {{
                showToast("진행상황이 자동 저장되었습니다.");
                filterData();
            }}
        }}

        closeDrawerBtn.addEventListener('click', closeDrawer);
        drawerOverlay.addEventListener('click', closeDrawer);

        function saveDetailProgress() {{
            const changed = saveData();
            if (changed) {{
                showToast("진행상황이 저장되었습니다.");
            }}
            closeDrawer();
            filterData();
        }}

        // Backup and Restore Progress
        function exportProgress() {{
            const progressData = {{ screens: {{}} }};
            screensData.forEach(item => {{
                const complete = isScreenCompleted(item.file);
                const memo = getScreenMemo(item.file);
                const customName = getScreenCustomName(item.file);
                const dataFlow = getScreenDataFlow(item.file);
                const dataInput = getScreenDataInput(item.file);
                const trigger = getScreenTrigger(item.file);
                const testCase = getScreenTestCase(item.file);
                const qaReport = getScreenQaReport(item.file);
                if (complete || memo || customName || dataFlow || dataInput || trigger || testCase || qaReport) {{
                    progressData.screens[item.file] = {{
                        complete: complete,
                        memo: memo,
                        custom_name: customName,
                        data_flow: dataFlow,
                        data_input: dataInput,
                        trigger: trigger,
                        test_case: testCase,
                        qa_report: qaReport
                    }};
                }}
            }});
            
            const jsonStr = JSON.stringify(progressData, null, 2);
            const blob = new Blob([jsonStr], {{ type: "application/json" }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            const filename = document.getElementById("export-filename").value.trim() || "screen_memos.json";
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast("다운로드되었습니다.");
        }}

        // Restore Progress
        function importProgress() {{
            document.getElementById("import-progress-file").click();
        }}

        function handleImportProgress(event) {{
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {{
                try {{
                    const data = JSON.parse(e.target.result);
                    if (!data || !data.screens) {{
                        alert("올바른 백업 파일 형식이 아닙니다.");
                        return;
                    }}
                    
                    // Clear existing keys
                    for (let i = localStorage.length - 1; i >= 0; i--) {{
                        const key = localStorage.key(i);
                        if (key.startsWith("screen:complete:") || key.startsWith("screen:memo:") || key.startsWith("screen:custom_name:") || key.startsWith("screen:data_flow:") || key.startsWith("screen:data_input:") || key.startsWith("screen:trigger:") || key.startsWith("screen:test_case:") || key.startsWith("screen:qa_report:")) {{
                            localStorage.removeItem(key);
                        }}
                    }}
                    
                    let importCount = 0;
                    Object.keys(data.screens).forEach(fKey => {{
                        const item = data.screens[fKey];
                        if (item.complete) {{
                            localStorage.setItem("screen:complete:" + fKey, "true");
                            importCount++;
                        }}
                        if (item.memo) {{
                            localStorage.setItem("screen:memo:" + fKey, item.memo);
                            importCount++;
                        }}
                        if (item.custom_name) {{
                            localStorage.setItem("screen:custom_name:" + fKey, item.custom_name);
                            importCount++;
                        }}
                        if (item.data_flow) {{
                            localStorage.setItem("screen:data_flow:" + fKey, item.data_flow);
                            importCount++;
                        }}
                        if (item.data_input) {{
                            localStorage.setItem("screen:data_input:" + fKey, item.data_input);
                            importCount++;
                        }}
                        if (item.trigger) {{
                            localStorage.setItem("screen:trigger:" + fKey, item.trigger);
                            importCount++;
                        }}
                        if (item.test_case) {{
                            localStorage.setItem("screen:test_case:" + fKey, item.test_case);
                            importCount++;
                        }}
                        if (item.qa_report) {{
                            localStorage.setItem("screen:qa_report:" + fKey, item.qa_report);
                            importCount++;
                        }}
                    }});
                    
                    alert("성공적으로 " + Object.keys(data.screens).length + "개 화면의 진행상황을 복원했습니다.");
                    filterData();
                }} catch (err) {{
                    alert("파일을 읽는 도중 오류가 발생했습니다: " + err.message);
                }}
            }};
            reader.readAsText(file);
            event.target.value = "";
        }}

        // Copy Text feature
        function copyText(elementId) {{
            const text = document.getElementById(elementId).innerText;
            navigator.clipboard.writeText(text).then(() => {{
                showToast("복사되었습니다.");
            }}).catch(err => {{
                console.error('Copy failed:', err);
            }});
        }}

        function showToast(message) {{
            if (message) {{
                toast.innerText = message;
            }} else {{
                toast.innerText = "복사되었습니다.";
            }}
            toast.classList.add('show');
            setTimeout(() => {{
                toast.classList.remove('show');
            }}, 2000);
        }}

        // CSV Export Logic
        exportCsvBtn.addEventListener('click', () => {{
            let csvContent = "data:text/csv;charset=utf-8,\\ufeff";
            csvContent += "화면코드,유형,대분류,중분류,화면명,사용자화면명,물리파일명,호출경로,완료여부,메모,TestCase,QaReport,데이터흐름,데이터가공,DB트리거\\n";

            screensData.forEach(item => {{
                const scope = getScope(item.file);
                const isCompleted = isScreenCompleted(item.file) ? "완료" : "미완료";
                const memoText = getScreenMemo(item.file).replace(/"/g, '""');
                const customNameText = getScreenCustomName(item.file).replace(/"/g, '""');
                const testCaseText = getScreenTestCase(item.file).replace(/"/g, '""');
                const qaReportText = getScreenQaReport(item.file).replace(/"/g, '""');
                const dataFlowText = getScreenDataFlow(item.file).replace(/"/g, '""');
                const dataInputText = getScreenDataInput(item.file).replace(/"/g, '""');
                const triggerText = getScreenTrigger(item.file).replace(/"/g, '""');
                
                const name = item.name.replace(/"/g, '""');
                const file = item.file.replace(/"/g, '""');
                const path = item.path.replace(/"/g, '""');

                csvContent += `"${{item.seq}}","${{scope}}","${{item.lclass}}","${{item.mclass}}","${{name}}","${{customNameText}}","${{file}}","${{path}}","${{isCompleted}}","${{memoText}}","${{testCaseText}}","${{qaReportText}}","${{dataFlowText}}","${{dataInputText}}","${{triggerText}}"\\n`;
            }});

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", `HMS_Screen_List_Export.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }});

        // Initialize Table Sort Class
        document.querySelector('th[data-sort="seq"]').classList.add('sorted-asc');
        
        // Initial Populate and Load
        const allM = new Set();
        screensData.forEach(s => allM.add(s.mclass));
        Array.from(allM).sort().forEach(m => {{
            mclassFilter.innerHTML += `<option value="${{m}}">${{m}}</option>`;
        }});

        filterData();
    </script>
</body>
</html>
"""

def build_html():
    md_path = r"D:\hmTest\backoffice\QaReport\All_HMS_Screens.md"
    html_path = r"D:\hmTest\backoffice\QaReport\All_HMS_Screens.html"
    memo_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
    
    print("Parsing All_HMS_Screens.md...")
    screens = parse_markdown_table(md_path)
    if not screens:
        print("No screens parsed. Aborting.")
        return
        
    print(f"Parsed {len(screens)} screens.")
    
    # Pre-scan TestCase and QaReport files
    backoffice_dir = r"D:\hmTest\backoffice"
    qa_report_dir = r"D:\hmTest\backoffice\QaReport"
    
    testcase_files = {}
    if os.path.exists(backoffice_dir):
        for f in os.listdir(backoffice_dir):
            if f.lower().endswith("_testcase.md"):
                prefix = f[:-12].lower() # remove _testcase.md
                testcase_files[prefix] = f

    qareport_files = {}
    if os.path.exists(qa_report_dir):
        for f in os.listdir(qa_report_dir):
            if f.lower().endswith("_qareport.md"):
                prefix = f[:-12].lower() # remove _qareport.md
                qareport_files[prefix] = f

    datainput_files = {}
    if os.path.exists(qa_report_dir):
        for f in os.listdir(qa_report_dir):
            f_lower = f.lower()
            if f_lower.endswith("_datainput.md"):
                prefix = f_lower[:-13]
                datainput_files[prefix] = f
            elif f_lower.endswith("_datainputguide.md"):
                prefix = f_lower[:-18]
                datainput_files[prefix] = f
            elif f_lower.endswith("_datausage_guide.md"):
                prefix = f_lower[:-19]
                datainput_files[prefix] = f

    trigger_files = {}
    if os.path.exists(qa_report_dir):
        for f in os.listdir(qa_report_dir):
            f_lower = f.lower()
            if f_lower.endswith("_trigger.md"):
                prefix = f_lower[:-11]
                trigger_files[prefix] = f
            elif f_lower.endswith("_triggerguide.md"):
                prefix = f_lower[:-16]
                trigger_files[prefix] = f
                
    # Load screen memos if exists
    memos = {}
    if os.path.exists(memo_path):
        try:
            with open(memo_path, "r", encoding="utf-8") as f:
                memos = json.load(f)
            print(f"Loaded custom screen progress from: {memo_path}")
        except Exception as e:
            print("Failed to read screen memos:", e)
            
    screen_memos = memos.get("screens", {})
    for s in screens:
        file_key = s["file"]
        file_key_lower = file_key.lower()
        
        # Load TestCase
        auto_tc = testcase_files.get(file_key_lower, "")
        if auto_tc:
            auto_tc_path = os.path.join(backoffice_dir, auto_tc)
        else:
            auto_tc_path = ""
            
        # Load QaReport
        auto_qr = qareport_files.get(file_key_lower, "")
        if auto_qr:
            auto_qr_path = os.path.join(qa_report_dir, auto_qr)
        else:
            auto_qr_path = ""

        # Load DataInput
        auto_di = datainput_files.get(file_key_lower, "")
        if auto_di:
            auto_di_path = os.path.join(qa_report_dir, auto_di)
        else:
            auto_di_path = ""

        if file_key in screen_memos:
            # Load Trigger
            auto_tr = trigger_files.get(file_key_lower, "")
            if auto_tr:
                auto_tr_path = os.path.join(qa_report_dir, auto_tr)
            else:
                auto_tr_path = ""

            s["custom_complete"] = screen_memos[file_key].get("complete", False)
            s["custom_memo"] = screen_memos[file_key].get("memo", "")
            s["custom_name"] = screen_memos[file_key].get("custom_name", "")
            s["data_flow"] = screen_memos[file_key].get("data_flow", "")
            s["data_input"] = screen_memos[file_key].get("data_input", auto_di_path)
            s["trigger"] = screen_memos[file_key].get("trigger", auto_tr_path)
            s["test_case"] = screen_memos[file_key].get("test_case", auto_tc_path)
            s["qa_report"] = screen_memos[file_key].get("qa_report", auto_qr_path)
        else:
            # Load Trigger
            auto_tr = trigger_files.get(file_key_lower, "")
            if auto_tr:
                auto_tr_path = os.path.join(qa_report_dir, auto_tr)
            else:
                auto_tr_path = ""

            s["custom_complete"] = False
            s["custom_memo"] = ""
            s["custom_name"] = ""
            s["data_flow"] = ""
            s["data_input"] = auto_di_path
            s["trigger"] = auto_tr_path
            s["test_case"] = auto_tc_path
            s["qa_report"] = auto_qr_path
            
    print("Generating All_HMS_Screens.html content...")
    html_content = get_html_template(screens)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Success! Generated All_HMS_Screens.html at {html_path}")

import sys
import http.server
import socketserver

class ProgressApiHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/save':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                file_key = data.get('file')
                complete = data.get('complete', False)
                memo = data.get('memo', '')
                custom_name = data.get('custom_name', '')
                data_flow = data.get('data_flow', '')
                data_input = data.get('data_input', '')
                trigger = data.get('trigger', '')
                test_case = data.get('test_case', '')
                qa_report = data.get('qa_report', '')
                
                memo_path = r"D:\hmTest\backoffice\QaReport\hms_screens_progress.json"
                memos = {"screens": {}}
                if os.path.exists(memo_path):
                    try:
                        with open(memo_path, "r", encoding="utf-8") as f:
                            memos = json.load(f)
                    except Exception:
                        pass
                
                if "screens" not in memos:
                    memos["screens"] = {}
                
                # Update progress memo
                memos["screens"][file_key] = {
                    "complete": complete,
                    "memo": memo,
                    "custom_name": custom_name,
                    "data_flow": data_flow,
                    "data_input": data_input,
                    "trigger": trigger,
                    "test_case": test_case,
                    "qa_report": qa_report
                }
                
                # Clean up if all empty
                if not complete and not memo and not custom_name and not data_flow and not data_input and not trigger and not test_case and not qa_report:
                    if file_key in memos["screens"]:
                        del memos["screens"][file_key]
                
                with open(memo_path, "w", encoding="utf-8") as f:
                    json.dump(memos, f, indent=2, ensure_ascii=False)
                
                # Rebuild All_HMS_Screens.html automatically
                build_html()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                print(f"[API SERVER] Auto-saved & Rebuilt: {file_key}")
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    build_html()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        PORT = 8000
        handler = ProgressApiHandler
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"[API SERVER] Running on port {PORT}...")
            print(f"[API SERVER] Real-time file sync enabled. Ready for requests.")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[API SERVER] Stopping server...")
                httpd.shutdown()

if __name__ == "__main__":
    main()
