import os
import sys
import json
import errno
import stat
import time
import logging
import threading
from fuse import FUSE, Operations, FuseOSError

STATE_FILE = "fs.json"
LOG_FILE = "fs.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_event(message):
    logging.info(message)

def is_temp_file(path):
    name = os.path.basename(path)
    return name.startswith(".") and (name.endswith(".swp") or name.endswith(".swx") or name.endswith("~"))

def default_dir():
    now = time.time()
    return {
        "type": "dir",
        "children": {},
        "created": now,
        "modified": now
    }

def default_file():
    now = time.time()
    return {
        "type": "file",
        "content": "",
        "created": now,
        "modified": now,
        "size": 0,
        "tags": []
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def load_state():
    if not os.path.exists(STATE_FILE) or os.path.getsize(STATE_FILE) == 0:
        state = {
            "/": default_dir(),
            "/Trash": default_dir()
        }
        save_state(state)
        return state

    with open(STATE_FILE, "r") as f:
        state = json.load(f)

    if "/" not in state:
        state["/"] = default_dir()
    if "/Trash" not in state:
        state["/Trash"] = default_dir()

    return state

class SimpleFS(Operations):
    def __init__(self):
        self.state = load_state()
        self.fs_lock = threading.Lock()
        log_event("Filesystem initialized successfully")

    def _save(self):
        save_state(self.state)

    def _get_parent(self, path):
        parent = os.path.dirname(path)
        if parent == "":
            parent = "/"
        return parent

    def getattr(self, path, fh=None):
        if path not in self.state:
            raise FuseOSError(errno.ENOENT)

        node = self.state[path]

        if node["type"] == "dir":
            mode = stat.S_IFDIR | 0o755
            nlink = 2
            size = 0
        else:
            mode = stat.S_IFREG | 0o644
            nlink = 1
            size = node.get("size", len(node.get("content", "")))

        return {
            "st_mode": mode,
            "st_nlink": nlink,
            "st_size": size,
            "st_ctime": node.get("created", time.time()),
            "st_mtime": node.get("modified", time.time()),
            "st_atime": node.get("modified", time.time()),
        }

    def readdir(self, path, fh):
        if path not in self.state or self.state[path]["type"] != "dir":
            raise FuseOSError(errno.ENOENT)

        return [".", ".."] + list(self.state[path]["children"].keys())

    def mkdir(self, path, mode):
        with self.fs_lock:
            if path in self.state:
                raise FuseOSError(errno.EEXIST)

            parent = self._get_parent(path)
            name = os.path.basename(path)

            if parent not in self.state or self.state[parent]["type"] != "dir":
                raise FuseOSError(errno.ENOENT)

            self.state[path] = default_dir()
            self.state[parent]["children"][name] = path
            self.state[parent]["modified"] = time.time()
            self._save()
            log_event(f"Directory created: {path}")

    def rmdir(self, path):
        with self.fs_lock:
            if path not in self.state or self.state[path]["type"] != "dir":
                raise FuseOSError(errno.ENOENT)

            if self.state[path]["children"]:
                raise FuseOSError(errno.ENOTEMPTY)

            parent = self._get_parent(path)
            name = os.path.basename(path)

            del self.state[path]

            if parent in self.state and name in self.state[parent]["children"]:
                del self.state[parent]["children"][name]
                self.state[parent]["modified"] = time.time()

            self._save()
            log_event(f"Directory removed: {path}")

    def create(self, path, mode):
        with self.fs_lock:
            if path in self.state:
                raise FuseOSError(errno.EEXIST)

            parent = self._get_parent(path)
            name = os.path.basename(path)

            if parent not in self.state or self.state[parent]["type"] != "dir":
                raise FuseOSError(errno.ENOENT)

            self.state[path] = default_file()
            self.state[parent]["children"][name] = path
            self.state[parent]["modified"] = time.time()
            self._save()

            if not is_temp_file(path):
                log_event(f"File created: {path}")

            return 0

    def open(self, path, flags):
        if path not in self.state or self.state[path]["type"] != "file":
            raise FuseOSError(errno.ENOENT)
        return 0

    def read(self, path, size, offset, fh):
        if path not in self.state or self.state[path]["type"] != "file":
            raise FuseOSError(errno.ENOENT)

        content = self.state[path]["content"]
        if not is_temp_file(path):
            log_event(f"Read from file: {path}")
        return content[offset:offset + size].encode("utf-8")

    def write(self, path, data, offset, fh):
        with self.fs_lock:
            if path not in self.state or self.state[path]["type"] != "file":
                raise FuseOSError(errno.ENOENT)

            content = self.state[path]["content"]

            if isinstance(data, bytes):
                decoded_data = data.decode("utf-8", errors="ignore")
            else:
                decoded_data = str(data)

            if offset > len(content):
                content = content + ("\x00" * (offset - len(content)))

            new_content = content[:offset] + decoded_data
            if offset + len(decoded_data) < len(content):
                new_content += content[offset + len(decoded_data):]

            self.state[path]["content"] = new_content
            self.state[path]["modified"] = time.time()
            self.state[path]["size"] = len(new_content)
            self._save()

            if not is_temp_file(path):
                log_event(f"Written to file: {path}")

            return len(data)

    def truncate(self, path, length, fh=None):
        with self.fs_lock:
            if path not in self.state or self.state[path]["type"] != "file":
                raise FuseOSError(errno.ENOENT)

            content = self.state[path]["content"]

            if length < len(content):
                self.state[path]["content"] = content[:length]
            else:
                self.state[path]["content"] = content.ljust(length, "\x00")

            self.state[path]["modified"] = time.time()
            self.state[path]["size"] = len(self.state[path]["content"])
            self._save()

            if not is_temp_file(path):
                log_event(f"Truncated file: {path}")

    def unlink(self, path):
        with self.fs_lock:
            if path not in self.state or self.state[path]["type"] != "file":
                raise FuseOSError(errno.ENOENT)

            parent = self._get_parent(path)
            name = os.path.basename(path)

            if is_temp_file(path):
                del self.state[path]
                if parent in self.state and name in self.state[parent]["children"]:
                    del self.state[parent]["children"][name]
                    self.state[parent]["modified"] = time.time()
                self._save()
                return

            trash_path = f"/Trash/{name}"
            counter = 1
            while trash_path in self.state:
                trash_path = f"/Trash/{name}_{counter}"
                counter += 1

            self.state[trash_path] = self.state[path]
            self.state["/Trash"]["children"][os.path.basename(trash_path)] = trash_path
            self.state["/Trash"]["modified"] = time.time()

            del self.state[path]

            if parent in self.state and name in self.state[parent]["children"]:
                del self.state[parent]["children"][name]
                self.state[parent]["modified"] = time.time()

            self._save()
            log_event(f"Moved to Trash: {path}")

    def rename(self, old, new):
        with self.fs_lock:
            if old not in self.state:
                raise FuseOSError(errno.ENOENT)

            new_parent = self._get_parent(new)
            old_parent = self._get_parent(old)
            old_name = os.path.basename(old)
            new_name = os.path.basename(new)

            if new_parent not in self.state or self.state[new_parent]["type"] != "dir":
                raise FuseOSError(errno.ENOENT)

            self.state[new] = self.state[old]
            self.state[new]["modified"] = time.time()
            del self.state[old]

            if old_parent in self.state and old_name in self.state[old_parent]["children"]:
                del self.state[old_parent]["children"][old_name]
                self.state[old_parent]["modified"] = time.time()

            self.state[new_parent]["children"][new_name] = new
            self.state[new_parent]["modified"] = time.time()

            self._save()

            if not is_temp_file(old) and not is_temp_file(new):
                log_event(f"Renamed: {old} -> {new}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <mountpoint>")
        sys.exit(1)

    mountpoint = sys.argv[1]
    FUSE(SimpleFS(), mountpoint, foreground=True, nothreads=True)
