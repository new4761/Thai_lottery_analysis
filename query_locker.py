import re
import pandas as pd

# 📥 Load the raw data with stable typing for lottery numbers
df = pd.read_csv("lottery_results.csv", dtype=str).fillna("")

# 🎯 Columns to extract
prize_columns = ["first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]
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
        return cleaned.zfill(width)
    return cleaned


def assert_required_columns(df):
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
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
            records.append({
                "date": row_date,
                "prize_type": prize,
                "number": normalized
            })


# 🔁 Flatten into long format
records = []
assert_required_columns(df)

for idx, row in df.iterrows():
    for prize in prize_columns:
        append_prize_records(records, row["date"], prize, row[prize])

# 📊 Final Looker-friendly format
df_looker = pd.DataFrame(records, columns=["date", "prize_type", "number"])
if df_looker.empty:
    df_looker = pd.DataFrame(columns=["date", "prize_type", "number"])
    print("⚠️ No lottery rows were available for Looker transform.")

# 💾 Save to CSV
df_looker = df_looker.sort_values(["date", "prize_type", "number"]).drop_duplicates()
df_looker.to_csv("lottery_results_looker_ready.csv", index=False)
print("✅ Looker-ready dataset saved as 'lottery_results_looker_ready.csv'")
