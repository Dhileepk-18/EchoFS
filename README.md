# EchoFS — Persistent Virtual Filesystem using FUSE

**EchoFS** is a lightweight virtual filesystem implemented in Python using **FUSE (Filesystem in Userspace)**. The project stores filesystem state in a JSON file and exposes a mounted directory through which normal Linux file operations can be performed.

The project demonstrates core operating-system filesystem concepts such as file and directory management, persistence, metadata, logging, deletion handling, and concurrent access.

## Features

- Virtual filesystem mounted through FUSE
- Create and remove directories
- Create, read, write, and truncate files
- Rename files
- Delete files by moving them to a virtual **Trash**
- Restore deleted files from Trash
- Persistent filesystem state using JSON
- Operation logging using Python's logging module
- File metadata including type, size, creation time, modification time, and tags
- Add custom tags to files
- Search file contents by keyword
- Thread-safe filesystem state updates
- Temporary editor files such as .swp, .swx, and backup files ending in ~ are handled without being placed in Trash or logged as normal user operations

## How It Works

The filesystem keeps its virtual state in fs.json. Each file or directory is represented as a node in the JSON state.

At startup:

1. main.py loads fs.json.
2. If the state file does not exist, the root directory (/) and /Trash are created.
3. FUSE mounts the virtual filesystem at the directory supplied on the command line.
4. File operations performed inside the mount point are handled by the SimpleFS class.
5. Changes are written back to fs.json.
6. Filesystem operations are recorded in fs.log.

When a normal file is deleted, it is moved to /Trash instead of being permanently removed.

## Requirements

The current implementation is intended for Linux systems because it depends on FUSE.

### Software

- Ubuntu 20.04 / 22.04 or a compatible Linux distribution
- Python 3
- FUSE 3
- Git
- Python virtual environment support
- fusepy

### Hardware

- At least 4 GB RAM
- At least 10 GB available storage

## Installation

### 1. Install system dependencies

    sudo apt update
    sudo apt install fuse3 libfuse3-dev python3 python3-pip python3-venv git

### 2. Clone the repository

    git clone https://github.com/Dhileepk-18/EchoFS.git
    cd EchoFS

### 3. Create and activate a virtual environment

    python3 -m venv venv
    source venv/bin/activate

### 4. Install Python dependency

    pip install fusepy

## Running the Filesystem

Create a mount directory if it does not already exist:

    mkdir -p mount_dir

Start the filesystem:

    python3 main.py mount_dir

The filesystem runs in the foreground. Keep this terminal open while using the mounted filesystem.

Open a second terminal to perform filesystem operations.

## Basic File Operations

From the second terminal:

    cd ~/EchoFS/mount_dir

    mkdir demo
    cd demo

    touch file.txt
    printf "Hello Virtual FS\n" > file.txt
    cat file.txt

    mv file.txt renamed.txt
    rm renamed.txt

The deleted renamed.txt is moved to the virtual Trash.

You can inspect the Trash from the mounted filesystem:

    ls ~/EchoFS/mount_dir/Trash

## Restore a Deleted File

From the project root, run:

    python3 restore.py

Enter the filename stored in Trash when prompted.

The script restores the file to the filesystem root using a name such as:

    restored_filename.txt

If that name already exists, a numbered name is generated.

## Search File Contents

Run:

    python3 search.py

Enter a keyword when prompted. The script searches the contents of files stored in the filesystem state and prints matching paths.

## Add a File Tag

Run:

    python3 tag_file.py

Enter the filesystem path and the tag when prompted.

For example:

    Enter file path: /demo/notes.txt
    Enter tag: important

Tags are stored with the file metadata in fs.json.

## View File Metadata

Run:

    python3 show_meta.py

Enter a filesystem path to display:

- File type
- Creation time
- Modification time
- Size
- Tags

## Project Structure

    EchoFS/
    ├── main.py          # FUSE filesystem implementation
    ├── restore.py       # Restore a file from Trash
    ├── search.py        # Search file contents
    ├── show_meta.py     # Display file metadata
    ├── tag_file.py      # Add tags to files
    ├── README.md        # Project documentation
    ├── .gitignore       # Ignored runtime/generated files
    ├── fs.json          # Runtime filesystem state (generated)
    ├── fs.log           # Runtime operation log (generated)
    ├── mount_dir/       # FUSE mount point (created locally)
    └── venv/            # Python virtual environment (local)

## Data Storage

### fs.json

Stores the persistent virtual filesystem state, including:

- Files and directories
- File contents
- File sizes
- Creation and modification timestamps
- File tags
- Directory-child relationships
- The virtual Trash directory

fs.json is generated at runtime and is intentionally excluded from Git.

### fs.log

Stores filesystem operation logs such as file creation, reads, writes, renames, deletions, and directory operations.

fs.log is also generated at runtime and excluded from Git.

## Architecture

The core implementation is contained in main.py.

The SimpleFS class implements FUSE filesystem operations and maintains the virtual state in memory. A thread lock protects state-changing operations before they are persisted to fs.json.

The main filesystem operations include:

| Operation | Implementation |
|---|---|
| List directory | readdir() |
| File/directory metadata | getattr() |
| Create directory | mkdir() |
| Remove directory | rmdir() |
| Create file | create() |
| Open file | open() |
| Read file | read() |
| Write file | write() |
| Resize file | truncate() |
| Delete file | unlink() |
| Rename file/directory | rename() |

## Execution Flow

    Start main.py
         │
         ▼
    Load or initialize fs.json
         │
         ▼
    Mount filesystem with FUSE
         │
         ▼
    User performs normal file operations
         │
         ├── Create / Read / Write
         ├── Rename
         ├── Directory operations
         └── Delete
                 │
                 ▼
           Move deleted file
              to /Trash
                 │
                 ▼
         Persist state to fs.json
                 │
                 ▼
           Log operation to fs.log

## Limitations and Notes

- The project currently targets Linux/FUSE environments rather than native Windows.
- The filesystem is implemented as a simple JSON-backed virtual filesystem and is intended primarily for learning and demonstration.
- Runtime files such as fs.json, fs.log, and mount_dir/ are excluded from version control.
- The filesystem must be running before operations are performed through the mounted directory.
- The helper scripts operate directly on fs.json, so they should be run from the project directory where that file is located.
- There is currently no delete_forever.py file in the repository; therefore permanent deletion from Trash is not documented as an available command.

## Learning Objectives

This project can be used to understand:

- User-space filesystem design
- FUSE and filesystem callbacks
- File and directory abstractions
- Persistent state management
- JSON-based storage
- File metadata management
- Logging
- Basic concurrency control
- Trash/recovery mechanisms
- Interaction between operating-system file commands and a custom filesystem

## License

No license file is currently present in the repository. Add an appropriate license if this project is intended for redistribution or open-source use.
