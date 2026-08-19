import csv
import datetime
from pathlib import Path


REQUIRED_COLUMNS = {"date", "first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"}
PRIZE_COLUMNS = {"first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"}


def validate_csv_schema(csv_path):
    """Validate CSV has all required columns."""
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {csv_path}")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        return True


def validate_csv_integrity(csv_path, previous_row_count=None):
    """Validate CSV data integrity."""
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("CSV has no data rows")

    dates = set()
    max_date = None
    min_date = None
    rows_with_data = 0

    for i, row in enumerate(rows, start=2):  # Start at 2 (after header)
        date = row.get("date", "").strip()
        if not date:
            raise ValueError(f"Row {i} missing date")

        if date in dates:
            raise ValueError(f"Duplicate date: {date} (rows {list(dates).index(date) + 2} and {i})")
        dates.add(date)

        try:
            parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Row {i} has invalid date format: {date}")

        if parsed_date > datetime.date.today():
            raise ValueError(f"Row {i} has future date: {date}")

        if min_date is None or parsed_date < min_date:
            min_date = parsed_date
        if max_date is None or parsed_date > max_date:
            max_date = parsed_date

        has_data = any(row.get(col, "").strip() for col in PRIZE_COLUMNS)
        if has_data:
            rows_with_data += 1

    if rows_with_data == 0:
        raise ValueError("CSV has no rows with prize data")

    if previous_row_count is not None and len(rows) < previous_row_count:
        raise ValueError(
            f"Row count decreased: {previous_row_count} → {len(rows)}. "
            "This suggests data loss."
        )

    return {
        "row_count": len(rows),
        "date_range": (min_date, max_date),
        "latest_date": max_date,
    }


def validate_looker_csv(csv_path):
    """Validate Looker-ready CSV has correct format."""
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Looker CSV has no header: {csv_path}")

        expected = {"date", "prize_type", "number"}
        if set(reader.fieldnames) != expected:
            raise ValueError(
                f"Looker CSV has wrong schema. "
                f"Expected {expected}, got {set(reader.fieldnames)}"
            )

        rows = list(reader)
        if not rows:
            raise ValueError("Looker CSV has no data rows")

        dates = set()
        for i, row in enumerate(rows, start=2):
            date = row.get("date", "").strip()
            if not date:
                raise ValueError(f"Looker row {i} missing date")
            dates.add(date)

        return {
            "row_count": len(rows),
            "unique_dates": len(dates),
        }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: validators.py <csv_path> [previous_row_count]")
        sys.exit(1)

    csv_path = sys.argv[1]
    previous_count = int(sys.argv[2]) if len(sys.argv) > 2 else None

    try:
        validate_csv_schema(csv_path)
        info = validate_csv_integrity(csv_path, previous_count)
        print(f"✅ CSV valid: {info['row_count']} rows, "
              f"dates {info['date_range'][0]} to {info['date_range'][1]}")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
