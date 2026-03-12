"""
Part C — Interview Ready
========================
Q1  Conceptual  : json.load() vs json.loads()
Q2  Coding      : find_large_files()
Q3  Debug/Analyze: merge_csv_files() — 3 bugs fixed
"""

import csv
import json
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Q1 — Conceptual Answer
# ─────────────────────────────────────────────────────────────────────────────

"""
QUESTION
--------
Explain the difference between json.load() and json.loads().

ANSWER
------

┌──────────────┬──────────────────────────────────────────────────────────────┐
│ Function     │ Description                                                  │
├──────────────┼──────────────────────────────────────────────────────────────┤
│ json.load()  │ Reads JSON from a FILE OBJECT (open file handle / stream).   │
│              │ Internally calls .read() on the object you pass in.          │
├──────────────┼──────────────────────────────────────────────────────────────┤
│ json.loads() │ Parses JSON from a STRING (or bytes) already in memory.      │
│              │ The trailing 's' literally means "string".                   │
└──────────────┴──────────────────────────────────────────────────────────────┘

When to use json.load():
    When you need to read a JSON file from disk (or any file-like stream).
    The file handle is passed directly — no need to call .read() yourself.

When to use json.loads():
    When the JSON arrives as text in memory — e.g. an HTTP API response,
    a value fetched from a database column, or a string you built at runtime.

Real-world examples:
"""

# --- json.load() example ---
# Config file on disk  →  open it, pass the handle directly

def load_config(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)      # f is a file object, NOT a string
    return config


# --- json.loads() example ---
# API response arrives as a raw string  →  parse the string

import urllib.request

def fetch_exchange_rates(url: str) -> dict:
    with urllib.request.urlopen(url) as response:
        raw_text = response.read().decode("utf-8")   # raw_text is a str
    return json.loads(raw_text)                       # parse the STRING


# ─────────────────────────────────────────────────────────────────────────────
# Q2 — Coding: find_large_files()
# ─────────────────────────────────────────────────────────────────────────────

def find_large_files(directory: str, size_mb: float) -> list[tuple[str, float]]:
    """
    Recursively search *directory* and return files larger than *size_mb* MB.

    Parameters
    ----------
    directory : str
        Root folder to search (searched recursively).
    size_mb : float
        Size threshold in megabytes.

    Returns
    -------
    list[tuple[str, float]]
        List of (filename, size_in_mb) tuples, sorted by size descending.
    """
    threshold = size_mb * 1024 * 1024       # convert MB → bytes
    results: list[tuple[str, float]] = []

    for path in Path(directory).rglob("*"):
        if path.is_file():
            size_bytes = path.stat().st_size
            if size_bytes > threshold:
                size_in_mb = round(size_bytes / (1024 * 1024), 4)
                results.append((path.name, size_in_mb))

    results.sort(key=lambda item: item[1], reverse=True)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Q3 — Debugged merge_csv_files()
# ─────────────────────────────────────────────────────────────────────────────

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  BUG 1 — Missing import                                                ║
# ║  Original code used csv.reader / csv.writer but never imported csv.    ║
# ║  Fix: add  import csv  at the top of the file.                         ║
# ╠══════════════════════════════════════════════════════════════════════════╣
# ║  BUG 2 — Header duplicated from every file                             ║
# ║  csv.DictReader / csv.reader includes the header row as a normal row.  ║
# ║  When looping over multiple files each header gets appended to         ║
# ║  all_data, so the merged file contains N copies of the header.         ║
# ║  Fix: call next(reader) to consume & discard the header before the     ║
# ║  inner for-loop; keep only the first file's header.                    ║
# ╠══════════════════════════════════════════════════════════════════════════╣
# ║  BUG 3 — Missing  newline=""  on open() calls                         ║
# ║  On Windows, Python's universal newline translation adds an extra \r   ║
# ║  which csv.writer then double-encodes, producing blank rows between    ║
# ║  every data row in the output file.                                    ║
# ║  Fix: pass  newline=""  to every open() call that touches a CSV.       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def merge_csv_files(file_list: list[str]) -> int:
    all_data: list[list[str]] = []
    header: list[str] | None = None

    for filename in file_list:
        with open(filename, "r", newline="", encoding="utf-8") as f:  # Fix 3
            reader = csv.reader(f)
            file_header = next(reader)                                 # Fix 2 – consume header

            if header is None:
                header = file_header
                all_data.append(header)                                # write header once

            for row in reader:
                all_data.append(row)

    with open("merged.csv", "w", newline="", encoding="utf-8") as f:  # Fix 3
        writer = csv.writer(f)
        writer.writerows(all_data)

    return len(all_data)


# ─────────────────────────────────────────────────────────────────────────────
# Quick smoke-test (run this file directly to verify)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Q2 — find_large_files('/tmp', 0.01):")
    for name, mb in find_large_files("/tmp", 0.01):
        print(f"  {name:<40}  {mb} MB")
