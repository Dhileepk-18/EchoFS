import json

with open("fs.json", "r") as f:
    state = json.load(f)

keyword = input("Enter keyword to search: ").strip()

found = False

for path, node in state.items():
    if node.get("type") == "file":
        content = node.get("content", "")
        if keyword in content:
            print("Found in:", path)
            found = True

if not found:
    print("Keyword not found.")
