import json

log_path = r"C:\Users\uoshj\.gemini\antigravity-ide\brain\1ad2d3a1-b696-423f-be4c-a56cd6471abe\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "ssgoodtb_memo" in line:
            # Print a snippet of where it occurs
            idx = line.find("ssgoodtb_memo")
            print("FOUND ssgoodtb_memo:")
            print(line[idx-500:idx+1500])
            print("="*40)
