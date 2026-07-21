import os

log_path = r"C:\Users\uoshj\.gemini\antigravity-ide\brain\1ad2d3a1-b696-423f-be4c-a56cd6471abe\.system_generated\logs\transcript.jsonl"
print("File size:", os.path.getsize(log_path))

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if "sspromtb" in line.lower():
            print(f"Line {i} matches!")
            # print first 500 chars of line
            print(line[:500])
