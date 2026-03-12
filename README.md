# 🛒 Retail Sales Data Pipeline

A multi-part Python assignment covering CSV/JSON file handling, automated backups, and AI-assisted development.

---

## 📁 Project Structure

```
├── data1.csv               # Branch 1 daily sales
├── data2.csv               # Branch 2 daily sales
├── data3.csv               # Branch 3 daily sales
├── sales_pipeline.py       # Part A — merge, deduplicate, export
├── backup_manager.py       # Part B — automated backup with rotation
├── part_c_interview.py     # Part C — interview Q&A + debug fixes
├── part_d_ai_task.py       # Part D — AI-generated CSV→JSON converter
├── merged_sales.csv        # Output: all unique rows sorted by date
├── revenue_summary.json    # Output: revenue totals + metadata
├── test_comma.json         # Part D test output (comma delimiter)
└── test_semicolon.json     # Part D test output (semicolon delimiter)
```

---

## ⚙️ How to Run

**Part A — Sales Pipeline**
```bash
python sales_pipeline.py
```
Reads `data1.csv`, `data2.csv`, `data3.csv` → removes duplicates → exports `merged_sales.csv` and `revenue_summary.json`.

**Part B — Backup Manager**
```bash
python backup_manager.py <source_dir> <backup_dir>
```
Copies `.csv` and `.json` files with timestamps, keeps last 5 backups per file, logs all actions to `backup_log.txt`.

**Part D — CSV to JSON Converter**
```bash
python part_d_ai_task.py
```
Auto-detects delimiter (`,` `\t` `;` `|`) using `csv.Sniffer()` and converts to JSON.

---

## 🛠️ Requirements

- Python 3.10+
- Standard library only — no external packages needed
