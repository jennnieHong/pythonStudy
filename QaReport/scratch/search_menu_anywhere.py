import os

workspace_dir = r"d:\workspace\hmotors\workspace_hms20260326"

print("Searching for menu tables in ANY text files:")
count = 0
for root, dirs, files in os.walk(workspace_dir):
    # Exclude directories
    if any(p in root for p in [".git", ".idea", "target", "build", "node_modules", "bin"]):
        continue
    for file in files:
        if file.endswith((".java", ".xml", ".properties", ".yml", ".yaml", ".jsp", ".html", ".js", ".css", ".txt")):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "menumctb" in content.lower() or "menulctb" in content.lower() or "menummtb" in content.lower():
                    print(f"Found in: {file_path}")
                    count += 1
                    if count >= 30:
                        break
            except Exception:
                pass
    if count >= 30:
        break
print("Search complete!")
