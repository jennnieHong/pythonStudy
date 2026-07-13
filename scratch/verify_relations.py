import json
import re

def main():
    path = r'd:\hmTest\backoffice\QaReport\hms_db_dictionary.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Let's find all script tags and check their content
    script_blocks = re.findall(r'<script.*?>([\s\S]*?)</script>', html, re.IGNORECASE)
    print(f"Found {len(script_blocks)} script blocks.")
    
    for idx, block in enumerate(script_blocks):
        if 'sdailytb' in block.lower():
            print(f"Block {idx} contains 'sdailytb'. Length: {len(block)}")
            # Try to find the JSON array inside this block
            # Since it's a JSON array of tables, it starts with [ and ends with ]
            match = re.search(r'(\[[\s\S]*?\])\s*;', block)
            if not match:
                # Let's try matching from first [ to last ]
                start = block.find('[')
                end = block.rfind(']')
                if start != -1 and end != -1:
                    json_str = block[start:end+1]
                    try:
                        data = json.loads(json_str)
                        table = next((t for t in data if t['table_name'].lower() == 'sdailytb'), None)
                        if table:
                            print("Successfully loaded sdailytb from script block!")
                            print(f"Memo: {table.get('custom_memo')}")
                            print(f"Comment: {table.get('comment')}")
                            print("\nRelated Tables:")
                            for rel in table.get('related_tables', []):
                                print(f"- {rel['table_name']}: {rel['description']}")
                            return
                    except Exception as e:
                        print(f"Failed to parse JSON from start/end indices: {e}")
            else:
                try:
                    data = json.loads(match.group(1))
                    table = next((t for t in data if t['table_name'].lower() == 'sdailytb'), None)
                    if table:
                        print("Successfully loaded sdailytb from regex match!")
                        print(f"Memo: {table.get('custom_memo')}")
                        print(f"Comment: {table.get('comment')}")
                        print("\nRelated Tables:")
                        for rel in table.get('related_tables', []):
                            print(f"- {rel['table_name']}: {rel['description']}")
                        return
                except Exception as e:
                    print(f"Failed to parse JSON from regex match: {e}")

if __name__ == '__main__':
    main()
