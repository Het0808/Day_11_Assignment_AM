import csv
import json
from pathlib import Path
from datetime import datetime


def load_csv_files(folder: Path) -> list[dict]:
    """Read all csv files from folder using glob and return combined rows."""
    all_rows = []

    for filepath in sorted(folder.glob("data*.csv")):
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_rows.append(dict(row))

    return all_rows


def remove_duplicates(rows: list[dict]) -> list[dict]:
    """Drop rows where all four fields are identical."""
    seen = set()
    unique = []

    for row in rows:
        # build a hashable key from the four fields we care about
        key = (row["date"], row["product"], row["qty"], row["price"])
        if key not in seen:
            seen.add(key)
            unique.append(row)

    return unique


def compute_revenue(rows: list[dict]) -> dict[str, float]:
    """Return total revenue (qty * price) grouped by product name."""
    revenue: dict[str, float] = {}

    for row in rows:
        product = row["product"]
        qty = int(row["qty"])
        price = float(row["price"])
        revenue[product] = revenue.get(product, 0.0) + qty * price

    return revenue


def export_merged_csv(rows: list[dict], output_path: Path) -> None:
    """Write deduplicated rows sorted by date to a CSV file."""
    sorted_rows = sorted(rows, key=lambda r: r["date"])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "product", "qty", "price"])
        writer.writeheader()
        writer.writerows(sorted_rows)


def export_revenue_json(
    revenue: dict[str, float],
    files_processed: int,
    total_rows: int,
    output_path: Path,
) -> None:
    """Write revenue summary with metadata to a JSON file."""
    total_revenue = round(sum(revenue.values()), 2)

    summary = {
        "metadata": {
            "files_processed": files_processed,
            "total_rows": total_rows,
            "total_revenue": total_revenue,
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "revenue_by_product": {k: round(v, 2) for k, v in revenue.items()},
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


def main() -> None:
    data_folder = Path(".")
    output_folder = Path(".")

    # ── Step 1: load ──────────────────────────────────────────────────────────
    raw_rows = load_csv_files(data_folder)
    files_processed = len(list(data_folder.glob("data*.csv")))
    print(f"Loaded {len(raw_rows)} rows from {files_processed} file(s).")

    # ── Step 2: deduplicate ───────────────────────────────────────────────────
    unique_rows = remove_duplicates(raw_rows)
    print(f"After deduplication: {len(unique_rows)} unique rows.")

    # ── Step 3: compute revenue ───────────────────────────────────────────────
    revenue = compute_revenue(unique_rows)

    # ── Step 4a: export merged CSV ────────────────────────────────────────────
    merged_path = output_folder / "merged_sales.csv"
    export_merged_csv(unique_rows, merged_path)
    print(f"Merged CSV written → {merged_path}")

    # ── Step 4b: export revenue JSON ──────────────────────────────────────────
    json_path = output_folder / "revenue_summary.json"
    export_revenue_json(revenue, files_processed, len(unique_rows), json_path)
    print(f"Revenue JSON written → {json_path}")

    # quick preview
    print("\nRevenue by product:")
    for product, rev in revenue.items():
        print(f"  {product:12s}  ₹{rev:,.2f}")


if __name__ == "__main__":
    main()
