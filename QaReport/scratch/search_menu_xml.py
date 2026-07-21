import os
import re

workspace_dir = r"d:\workspace\hmotors\workspace_hms20260326"

print("Searching for menu tables in XML files:")
for root, dirs, files in os.walk(workspace_dir):
    for file in files:
        if file.lower().endswith(".xml"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "menulctb" in content or "menumctb" in content or "menummtb" in content:
                    print(f"Found in XML: {file_path}")
                    # Print lines containing them
                    lines = content.splitlines()
                    for idx, line in enumerate(lines):
                        if any(x in line for x in ["menulctb", "menumctb", "menummtb"]):
                            print(f"  Line {idx+1}: {line.strip()}")
            except Exception:
                pass
