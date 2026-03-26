import json

with open("fs.json", "r") as f:
    state = json.load(f)

path = input("Enter file path: ").strip()
tag = input("Enter tag: ").strip()

if path in state and state[path].get("type") == "file":
    if "tags" not in state[path]:
        state[path]["tags"] = []
    if tag not in state[path]["tags"]:
        state[path]["tags"].append(tag)

    with open("fs.json", "w") as f:
        json.dump(state, f, indent=4)

    print("Tag added successfully.")
else:
    print("File not found.")
