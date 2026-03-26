import json

with open("fs.json", "r") as f:
    state = json.load(f)

name = input("Enter file name to restore from Trash: ").strip()
trash_path = f"/Trash/{name}"

if trash_path not in state:
    print("File not found in Trash.")
    exit()

restore_name = f"restored_{name}"
restore_path = f"/{restore_name}"

counter = 1
while restore_path in state:
    restore_name = f"restored_{counter}_{name}"
    restore_path = f"/{restore_name}"
    counter += 1

state[restore_path] = state[trash_path]
state["/"]["children"][restore_name] = restore_path

if name in state["/Trash"]["children"]:
    del state["/Trash"]["children"][name]

del state[trash_path]

with open("fs.json", "w") as f:
    json.dump(state, f, indent=4)

print("Restored successfully as", restore_name)
