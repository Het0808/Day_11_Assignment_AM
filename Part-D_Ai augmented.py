"""
Part D — AI-Augmented Task
===========================
Script that reads a CSV file, auto-detects the delimiter, and converts it to
a properly formatted JSON file.

Supported delimiters: comma (,)  tab (\\t)  semicolon (;)  pipe (|)
"""

import csv
import json
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Prompt used with Claude (AI)
# ─────────────────────────────────────────────────────────────────────────────
#
# "Write a Python script that:
#  1. Accepts a path to a CSV file as a command-line argument.
#  2. Automatically detects the delimiter — it could be comma, tab,
#     semicolon, or pipe.
#  3. Parses the CSV using the detected delimiter.
#  4. Converts every row into a dictionary using the header row as keys.
#  5. Saves the result as a nicely indented JSON file next to the original.
#
#  Requirements:
#  - Use csv.Sniffer() for auto-detection with a fallback to comma.
#  - Handle edge cases: empty file, header-only file, BOM in UTF-8 files.
#  - Use pathlib throughout, not os.path."
#
# ─────────────────────────────────────────────────────────────────────────────
# AI-generated code (pasted verbatim, then tested — see evaluation below)
# ─────────────────────────────────────────────────────────────────────────────


def csv_to_json(csv_path: str) -> str:
    """
    Auto-detect delimiter and convert *csv_path* to a JSON file.

    Returns the path of the output .json file as a string.
    Raises ValueError for empty or header-only files.
    """
    source = Path(csv_path)

    # Guard: file must exist and have content
    if not source.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")
    if source.stat().st_size == 0:
        raise ValueError(f"File is empty: {csv_path}")

    # encoding="utf-8-sig" strips the BOM that Excel sometimes writes
    with open(source, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)

        # Attempt automatic delimiter detection
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
        except csv.Error:
            # Sniffer fails on very uniform single-column files → fall back
            dialect = csv.excel   # csv.excel uses comma by default

        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)
        rows = [
            {k: v for k, v in row.items() if k is not None}   # drop stray None keys
            for row in reader
        ]

    if not rows:
        raise ValueError("CSV has a header but contains no data rows.")

    output_path = source.with_suffix(".json")
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(rows, out, indent=2, ensure_ascii=False)

    print(f"Converted '{source.name}'  →  '{output_path.name}'  ({len(rows)} rows)")
    return str(output_path)


# ─────────────────────────────────────────────────────────────────────────────
# Test — run with two different delimiter styles
# ─────────────────────────────────────────────────────────────────────────────

def _create_test_files() -> list[Path]:
    """Create two sample CSVs with different delimiters for testing."""

    # Test file 1: standard comma-delimited
    comma_file = Path("test_comma.csv")
    comma_file.write_text(
        "date,product,qty,price\n"
        "2025-01-15,Laptop,2,45000\n"
        "2025-01-16,Mouse,5,900\n",
        encoding="utf-8"
    )

    # Test file 2: semicolon-delimited (common European Excel export)
    semi_file = Path("test_semicolon.csv")
    semi_file.write_text(
        "date;product;qty;price\n"
        "2025-01-15;Keyboard;3;2800\n"
        "2025-01-16;Monitor;1;22000\n",
        encoding="utf-8"
    )

    return [comma_file, semi_file]


# ─────────────────────────────────────────────────────────────────────────────
# Critical Evaluation  (~200 words)
# ─────────────────────────────────────────────────────────────────────────────
EVALUATION = """
CRITICAL EVALUATION OF AI-GENERATED CODE
=========================================

What the AI got right
----------------------
The AI correctly identified csv.Sniffer() as the standard-library tool for
delimiter detection and passed the right delimiters= argument to limit the
search space. Using DictReader instead of plain reader was a good call because
it maps each row to a dictionary automatically, giving the JSON output
meaningful keys out of the box. The fallback to csv.excel when Sniffer raises
csv.Error is also a sound defensive pattern for edge cases like single-column
files where there is no delimiter to detect.

What it missed
--------------
The AI did not handle the UTF-8 BOM that Microsoft Excel silently writes at
the start of CSV exports. Without encoding="utf-8-sig", the BOM character
becomes part of the first column name, which breaks JSON consumers downstream.
The script also did not guard against None keys, which DictReader creates when
a row has more columns than the header. Both issues were fixed in the final
version above.

Whether it used csv.Sniffer()
------------------------------
Yes — the AI used csv.Sniffer().sniff() with the correct delimiters argument.

Improvements made
-----------------
1. Changed encoding to "utf-8-sig" to strip the Excel BOM automatically.
2. Added a None-key filter on each row dictionary.
3. Added ensure_ascii=False to json.dump() so non-ASCII product names
   (e.g. Indian language characters) are written as-is, not as \\uXXXX escapes.
4. Added a FileNotFoundError guard before the size check.
"""


if __name__ == "__main__":
    # Run tests
    test_files = _create_test_files()
    print("=== Part D Test Run ===\n")
    for tf in test_files:
        csv_to_json(str(tf))
    print()
    print(EVALUATION)
