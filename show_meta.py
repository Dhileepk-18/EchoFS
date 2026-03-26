import json

with open("fs.json", "r") as f:
    state = json.load(f)

path = input("Enter file path: ").strip()

if path in state:
    node = state[path]
    print("Type:", node.get("type"))
    print("Created:", node.get("created"))
    print("Modified:", node.get("modified"))
    print("Size:", node.get("size"))
    print("Tags:", node.get("tags", []))
else:
    print("Path not found.")
