"""
part_c_and_d.py
---------------
Answers for Part C (Interview Ready) and Part D (AI-Augmented Task).
"""

import csv
import json
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════════
# Part C — Q1  (Conceptual answer is in the docstring below)
# ══════════════════════════════════════════════════════════════════════════════

"""
Q1 — json.load() vs json.loads()

json.load(f)
    Reads JSON directly from a FILE OBJECT (something you've already opened
    with open()). Internally it calls f.read() for you.

    When to use: whenever the JSON lives on disk or comes from any stream
    (network response, stdin, etc.) and you already have a file handle.

    Real-world example:
        with open("config.json") as f:
            config = json.load(f)   # ← file object, not a string

json.loads(s)
    Parses JSON from a STRING (or bytes) that is already in memory.
    The trailing 's' stands for "string".

    When to use: when the JSON arrives as a string — e.g. an API response
    body, a value pulled from a database column, or text you built yourself.

    Real-world example:
        import urllib.request
        with urllib.request.urlopen("https://api.example.com/data") as r:
            raw = r.read().decode()        # raw is now a str
        data = json.loads(raw)             # ← string, not a file
"""


# ══════════════════════════════════════════════════════════════════════════════
# Part C — Q2  (Coding)
# ══════════════════════════════════════════════════════════════════════════════

def find_large_files(directory: str, size_mb: float) -> list[tuple[str, float]]:
    """
    Recursively search *directory* for files larger than *size_mb* megabytes.

    Returns a list of (filename, size_in_mb) tuples sorted by size descending.
    """
    threshold_bytes = size_mb * 1024 * 1024
    results: list[tuple[str, float]] = []

    for path in Path(directory).rglob("*"):
        if path.is_file():
            file_size = path.stat().st_size
            if file_size > threshold_bytes:
                size_in_mb = round(file_size / (1024 * 1024), 4)
                results.append((path.name, size_in_mb))

    results.sort(key=lambda x: x[1], reverse=True)
    return results


# ══════════════════════════════════════════════════════════════════════════════
# Part C — Q3  (Debugged version)
# ══════════════════════════════════════════════════════════════════════════════

# Bug 1 — missing import (csv was never imported)
# Bug 2 — header row gets duplicated from every file (need to skip it after first)
# Bug 3 — open() calls are missing newline="" which causes blank rows on Windows

def merge_csv_files(file_list: list[str]) -> int:
    """Fixed version of the provided buggy function."""

    all_data: list[list[str]] = []
    header: list[str] | None = None

    for filename in file_list:
        with open(filename, "r", newline="", encoding="utf-8") as f:  # Fix 3: newline=""
            reader = csv.reader(f)
            file_header = next(reader)                                 # Fix 2: read header separately

            if header is None:
                header = file_header                                   # keep only the first file's header
                all_data.append(header)

            for row in reader:
                all_data.append(row)

    with open("merged.csv", "w", newline="", encoding="utf-8") as f:  # Fix 3: newline=""
        writer = csv.writer(f)
        writer.writerows(all_data)

    return len(all_data)


# ══════════════════════════════════════════════════════════════════════════════
# Part D — AI-Augmented Task
# ══════════════════════════════════════════════════════════════════════════════

# ── Prompt I used ──────────────────────────────────────────────────────────────
# "Write a Python script that:
#  1. Accepts a path to a CSV file as input.
#  2. Automatically detects the delimiter — it could be comma, tab, semicolon, or pipe.
#  3. Parses the CSV using the detected delimiter.
#  4. Converts the data to a well-formatted JSON file saved next to the original.
#  Use csv.Sniffer() for detection and handle edge cases like empty files or
#  files where Sniffer fails."

# ── AI-generated code (Claude, pasted verbatim then lightly tested) ────────────

def csv_to_json(csv_path: str) -> str:
    """
    Auto-detect delimiter and convert a CSV file to JSON.

    Returns the path of the output JSON file.
    Raises ValueError for empty files; falls back to comma if Sniffer fails.
    """
    source = Path(csv_path)

    if source.stat().st_size == 0:
        raise ValueError(f"File is empty: {csv_path}")

    with open(source, newline="", encoding="utf-8") as f:
        sample = f.read(4096)   # read a chunk for Sniffer

        # attempt automatic detection
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
        except csv.Error:
            # Sniffer can fail on very uniform files; default to comma
            dialect = csv.excel

        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)
        rows = [dict(row) for row in reader]

    if not rows:
        raise ValueError("CSV has a header but no data rows.")

    output_path = source.with_suffix(".json")
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(rows, out, indent=2)

    return str(output_path)


# ── Critical evaluation (≈200 words) ──────────────────────────────────────────
"""
CRITICAL EVALUATION OF AI-GENERATED CODE

What the AI got right:
The generated script correctly identified csv.Sniffer() as the right tool for
delimiter detection, which shows the AI understood the standard-library approach.
The fallback to csv.excel (comma dialect) when Sniffer raises csv.Error is a
solid defensive pattern. Wrapping the output in json.dump with indent=2 gives
clean, human-readable JSON rather than a single-line blob. Using DictReader
instead of reader was a good choice because it preserves column names as
dictionary keys, making the JSON output immediately meaningful.

What it missed:
The AI did not handle the BOM (Byte Order Mark) that Excel sometimes writes at
the start of UTF-8 CSV files. Passing encoding="utf-8-sig" instead of "utf-8"
would fix this silently. It also didn't handle files where the first row
contains blank cells, which causes DictReader to create None keys that break
json.dump. A simple {k: v for k, v in row.items() if k} filter on each row
would guard against that. The script also doesn't validate that all rows have
the same number of columns as the header.

Overall verdict:
The AI produced working, readable code for the common case. It does use
csv.Sniffer() correctly. I would add encoding="utf-8-sig", strip None keys,
and add a column-count assertion before calling it production-ready.
"""


if __name__ == "__main__":
    # quick smoke-test for find_large_files
    print("Large files in /tmp (> 0.001 MB):")
    for name, mb in find_large_files("/tmp", 0.001):
        print(f"  {name:40s}  {mb} MB")
