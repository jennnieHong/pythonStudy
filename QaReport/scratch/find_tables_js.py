with open(r"D:\hmTest\backoffice\QaReport\generate_table_dictionary.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "TABLES" in line:
        print(f"Line {i+1}: {line.strip()}")
