import csv
import re

PRIZE_COLUMNS = ["first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]
REQUIRED_COLUMNS = ["date", "first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]
PRIZE_WIDTHS = {
    "first": 6,
    "second": 6,
    "third": 6,
    "fourth": 6,
    "fifth": 6,
    "last2": 2,
    "last3f": 3,
    "last3b": 3,
    "near1": 6,
}


def sanitize_number(value):
    digits_only = re.sub(r"\D", "", str(value).strip())
    return digits_only


def normalize_prize_value(prize_name, value):
    cleaned = sanitize_number(value)
    if not cleaned:
        return ""

    width = PRIZE_WIDTHS.get(prize_name, 0)
    if width:
        if len(cleaned) > width:
            return ""
        return cleaned.zfill(width)
    return cleaned


def assert_required_columns(header):
    missing = [col for col in REQUIRED_COLUMNS if col not in header]
    if missing:
        raise ValueError(f"Missing required lottery columns: {', '.join(missing)}")


def is_iso_date(value):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", (value or "").strip()))


def append_prize_records(records, row_date, prize, raw_values):
    values = (raw_values or "").strip()
    if not values or not is_iso_date(row_date):
        return

    for val in values.split(","):
        normalized = normalize_prize_value(prize, val.strip())
        if normalized:
            records.append([row_date, prize, normalized])


def transform_lottery_data(input_filename, output_filename):
    records = []
    invalid_rows = 0

    with open(input_filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV {input_filename} has no header")
        assert_required_columns(reader.fieldnames)

        for row in reader:
            if not is_iso_date(row.get("date", "")):
                invalid_rows += 1
                continue

            for prize in PRIZE_COLUMNS:
                append_prize_records(records, row["date"], prize, row.get(prize, ""))

    if invalid_rows:
        print(f"⚠️ Skipped {invalid_rows} rows in lottery_results.csv due invalid date format.")
    if not records:
        print("⚠️ No lottery rows were available for Looker transform.")

    records.sort()
    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "prize_type", "number"])
        writer.writerows(records)


if __name__ == "__main__":
    transform_lottery_data("lottery_results.csv", "lottery_results_looker_ready.csv")
    print("✅ Looker-ready dataset saved as 'lottery_results_looker_ready.csv'")
