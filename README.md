# Virtual Notes Filesystem using FUSE (Python)

## Overview
The Virtual Notes Filesystem is a user-space filesystem implemented using FUSE (Filesystem in Userspace) in Python. 
This filesystem allows users to create, read, write, rename, and delete files inside a mounted directory. 
Deleted files are moved to a Trash folder instead of being permanently removed. 
The filesystem also supports persistent storage, logging, metadata, tagging, and search functionality.

This project demonstrates file system concepts implemented in user space using Python and FUSE.

---

## Features
- Virtual filesystem using FUSE
- Create directories and files
- Read and write file content
- Rename files
- Delete files (moved to Trash)
- Restore files from Trash
- Permanent delete from Trash
- Persistent storage using JSON
- Logging of filesystem operations
- File metadata (size, created, modified)
- File tagging system
- File search by name and content
- Thread-safe filesystem operations

---

## System Requirements

### Hardware Requirements
- Laptop/Desktop
- Minimum 4 GB RAM
- Minimum 10 GB Storage

### Software Requirements
- Ubuntu Linux (20.04 / 22.04)
- Python 3.x
- FUSE
- Git
- Python Virtual Environment (venv)

---

## Installation

### Install Required Packages
sudo apt update
sudo apt install fuse3 libfuse3-dev
sudo apt install python3 python3-pip python3-venv
sudo apt install git

---

## Project Setup

### Clone Repository
git clone https://github.com/YOUR_USERNAME/vfs_project.git
cd vfs_project

### Create Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install fusepy

---

## Running the Filesystem

### Step 1 – Activate Virtual Environment
source venv/bin/activate

### Step 2 – Run Filesystem
python main.py mount_dir

The filesystem will mount in mount_dir and run in the foreground.

---

## Filesystem Operations
Open another terminal and execute:

cd ~/vfs_project/mount_dir
mkdir demo
cd demo
touch file.txt
printf "Hello Virtual FS\n" > file.txt
cat file.txt
mv file.txt renamed.txt
rm renamed.txt
cd ..
ls Trash

This demonstrates file creation, writing, reading, renaming, deleting, and Trash functionality.

---

## Additional Features

### Search Files
python3 search.py

### Restore File from Trash
python3 restore.py

### Add Tag to File
python3 tag_file.py

### Show File Metadata
python3 show_meta.py

### Permanent Delete from Trash
python3 delete_forever.py

---

## Project Structure

vfs_project/
│
├── main.py
├── fs.json
├── fs.log
├── search.py
├── restore.py
├── tag_file.py
├── show_meta.py
├── delete_forever.py
├── mount_dir/
├── Trash/
├── venv/
├── README.md

---

## Persistent Storage
All filesystem data is stored in:
fs.json

Logs of filesystem operations are stored in:
fs.log

---

## Execution Workflow
Run filesystem → Mount directory → Create files → Write → Rename → Delete
→ File moves to Trash → Restore/Search/Tag/Metadata → Logs stored → Data stored in JSON

---

## Conclusion
The Virtual Notes Filesystem using FUSE was successfully implemented in Python. 
The filesystem supports file operations, Trash recovery, persistent storage, logging, metadata, tagging, and search functionality. 
This project demonstrates how operating system file management concepts can be implemented in user space using Python and FUSE.
