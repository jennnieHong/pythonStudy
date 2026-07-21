import json

log_path = r"C:\Users\uoshj\.gemini\antigravity-ide\brain\1ad2d3a1-b696-423f-be4c-a56cd6471abe\.system_generated\logs\transcript.jsonl"

found_blocks = []
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "sspromtb_memo" in line:
            found_blocks.append(line)

print(f"Found {len(found_blocks)} occurrences.")
# Print the last one (most recent)
if found_blocks:
    last_block = found_blocks[-1]
    # Let's search for "sspromtb_memo =" in it
    idx = last_block.find("sspromtb_memo =")
    if idx != -1:
        print(last_block[idx:idx+3000])
    else:
        print("sspromtb_memo not found in last block, printing snippet:")
        print(last_block[:1000])
