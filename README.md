# File Integrity Checker – Folder Scan & Compare Tool

A desktop application that scans directories, generates file metadata, and compares scans to detect missing, extra, or modified files. Built using PyQt6 with real-time progress tracking and a responsive UI.

---

## Features

- Recursive folder scanning (includes subdirectories)
- Two scan modes:
  - Size Mode (fast)
  - MD5 Mode (accurate)
- Real-time progress tracking
- Displays currently scanned file
- Export scan results to JSON
- Compare two scans to detect:
  - Missing files
  - Extra files
  - Modified files
- Threaded execution (UI remains responsive)
- Color-coded comparison results

---

## Dataset & Output

- Scan results are stored in JSON format
- Each file entry contains:
  - File size
  - Optional MD5 hash
- Output can be reused for comparison across systems

---

## Project Structure

project/
│
├── main.py        # PyQt6 GUI
├── core.py        # Scanning and comparison logic
└── README.md

---

## How It Works

### Scanning

- Traverses directories using os.walk
- Counts total files before scanning
- Processes each file and updates progress
- Optionally computes MD5 hash

### Progress Tracking

- Real-time percentage updates
- Displays current file being scanned
- Runs in a separate thread (QThread)

### Comparison

- Loads two JSON scan files
- Compares file paths and metadata
- Detects missing, extra, and mismatched files

---

## Dependencies

### Python Dependencies

- PyQt6
- numpy
- hashlib (built-in)
- json (built-in)
- os (built-in)

Install using:

pip install PyQt6 numpy

---

## Usage

### Scan

1. Open the application
2. Select "Scan Folder"
3. Choose directory
4. Select mode (Size or MD5)
5. Click Scan
6. Save JSON file

### Compare

1. Select "Compare Scans"
2. Choose two JSON files
3. Click Compare
4. View results in table
