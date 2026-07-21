import os
import sys

def search_text_in_dir(directory, query):
    results = []
    query_lower = query.lower()
    for root, dirs, files in os.walk(directory):
        # Exclude directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules', 'target', 'bin', 'build')]
        for file in files:
            if file.endswith(('.java', '.xml', '.properties', '.sql', '.md', '.txt')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if query_lower in line.lower():
                                results.append((filepath, line_num, line.strip()))
                except Exception as e:
                    pass
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_codebase_references.py [search_query]")
        return
        
    query = sys.argv[1]
    root_dir = r"d:\workspace\hmotors\workspace_hms20260326"
    print(f"Searching for '{query}' in {root_dir}...")
    matches = search_text_in_dir(root_dir, query)
    print(f"Found {len(matches)} matches:")
    for match in matches[:100]:
        print(f"{match[0]}:{match[1]} - {match[2]}")

if __name__ == '__main__':
    main()
