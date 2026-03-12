"""
backup_manager.py
-----------------
Copies .csv and .json files from source_directory → backup_directory,
appending a timestamp to each filename and keeping only the last 5
backups per original file.

Usage:
    python backup_manager.py <source_directory> <backup_directory>
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


KEEP_LAST_N = 5
ALLOWED_EXTENSIONS = {".csv", ".json"}
LOG_FILE = "backup_log.txt"


def log(message: str) -> None:
    """Append a timestamped line to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry, end="")


def make_backup_name(original: Path) -> str:
    """Build the backup filename with a timestamp suffix."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{original.stem}_{ts}{original.suffix}"


def prune_old_backups(backup_dir: Path, stem: str, suffix: str) -> None:
    """Keep only the KEEP_LAST_N most recent backups for a given file."""
    pattern = f"{stem}_*{suffix}"
    existing = sorted(backup_dir.glob(pattern))   # glob returns in filesystem order

    # sort by name – timestamps in the filename make lexicographic sort work fine
    existing.sort()

    if len(existing) > KEEP_LAST_N:
        to_delete = existing[: len(existing) - KEEP_LAST_N]
        for old_file in to_delete:
            old_file.unlink()
            log(f"Deleted old backup: {old_file.name}")


def backup_files(source_dir: Path, backup_dir: Path) -> None:
    """Main backup routine."""
    backup_dir.mkdir(parents=True, exist_ok=True)

    files_found = [
        f for f in source_dir.iterdir()
        if f.is_file() and f.suffix in ALLOWED_EXTENSIONS
    ]

    if not files_found:
        log("No eligible files found in source directory.")
        return

    log(f"Starting backup: {source_dir} → {backup_dir}")

    for source_file in files_found:
        backup_name = make_backup_name(source_file)
        destination = backup_dir / backup_name

        shutil.copy2(source_file, destination)
        log(f"Copied: {source_file.name} → {backup_name}")

        # clean up old backups for this file
        prune_old_backups(backup_dir, source_file.stem, source_file.suffix)

    log("Backup complete.\n")


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python backup_manager.py <source_directory> <backup_directory>")
        sys.exit(1)

    source_dir = Path(sys.argv[1])
    backup_dir = Path(sys.argv[2])

    if not source_dir.exists():
        print(f"Error: source directory '{source_dir}' does not exist.")
        sys.exit(1)

    backup_files(source_dir, backup_dir)


if __name__ == "__main__":
    main()
