with open(r"D:\hmTest\backoffice\QaReport\update_memos_json.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace strnddtb with strndttb
new_content = content.replace("strnddtb", "strndttb")

with open(r"D:\hmTest\backoffice\QaReport\update_memos_json.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Replaced all strnddtb with strndttb successfully!")
