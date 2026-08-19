import csv
import datetime
import os
import time
import requests
import re
import io

LOTTERY_RESULTS_FILE = "lottery_results.csv"
LOTTERY_START_DATE = "2010-03-01"
FIELD_NAMES = ["date", "first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]
API_URL = "https://www.glo.or.th/api/checking/getLotteryResult"
RECOVERY_LOOKBACK_DAYS = 45
CONNECT_TIMEOUT_SECONDS = 4
READ_TIMEOUT_SECONDS = 12
REQUEST_RETRIES = 3
REQUEST_RETRY_DELAY_SECONDS = 2
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


# Get the list of draw dates based on the year and special conditions for May
def get_draw_dates(start_date=LOTTERY_START_DATE, end_date=None):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = end_date or datetime.date.today()  # Use today as default end date

    draw_dates = []
    for year in range(start_date.year, end_date.year + 1):
        for month in range(1, 13):
            if year == start_date.year and month < start_date.month:
                continue  # Skip months before the start date year-month
            if year == end_date.year and month > end_date.month:
                break  # Stop if the year-month is after the end date

            draw_days = [2, 16] if month == 5 else [1, 16]
            for day in draw_days:
                date = datetime.date(year, month, day)
                if start_date <= date <= end_date:
                    draw_dates.append(date)
    draw_dates.sort()
    return draw_dates


def get_pending_draw_dates(latest_known_date, end_date=None):
    end_date = end_date or datetime.date.today()

    if latest_known_date:
        recovery_window_start = latest_known_date - datetime.timedelta(days=RECOVERY_LOOKBACK_DAYS)
        start_date_obj = datetime.datetime.strptime(LOTTERY_START_DATE, "%Y-%m-%d").date()
        start_date = max(start_date_obj, recovery_window_start).strftime("%Y-%m-%d")
        candidate_dates = get_draw_dates(start_date, end_date)
        return [date for date in candidate_dates if date > latest_known_date]

    return get_draw_dates(LOTTERY_START_DATE, end_date)


def parse_lottery_date(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def read_local_lottery_data(filename=LOTTERY_RESULTS_FILE):
    if not os.path.exists(filename):
        return []

    rows = []
    with open(filename, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            draw_date = (row.get("date") or "").strip()
            if not draw_date:
                continue

            if parse_lottery_date(draw_date) is None:
                print(f"⚠️ Skipping invalid date row in local CSV: {draw_date}")
                continue

            normalized_row = {field: (row.get(field) or "").strip() for field in FIELD_NAMES}
            normalized_row["date"] = draw_date
            rows.append(normalized_row)
    return rows


def get_latest_local_draw_date(rows):
    latest = None
    for row in rows:
        row_date = parse_lottery_date(row.get("date"))
        if row_date and (latest is None or row_date > latest):
            latest = row_date
    return latest


def sanitize_number(value):
    digits_only = re.sub(r"\D", "", str(value).strip())
    return digits_only


def require_row_fields(row):
    missing = [field for field in FIELD_NAMES if field not in row]
    if missing:
        raise ValueError(f"Missing required lottery columns: {', '.join(missing)}")
    return row


def normalize_prize_value(prize_name, value):
    cleaned = sanitize_number(value)
    if not cleaned:
        return ""

    width = PRIZE_WIDTHS.get(prize_name, 0)
    if width:
        return cleaned.zfill(width)
    return cleaned


def validate_lottery_response(payload):
    if not isinstance(payload, dict):
        return False

    response = payload.get("response")
    result = response.get("result") if isinstance(response, dict) else None
    data = result.get("data") if isinstance(result, dict) else None
    if not isinstance(data, dict):
        return False

    for prize_name, prize_payload in data.items():
        if not isinstance(prize_payload, dict):
            continue
        numbers = prize_payload.get("number")
        if numbers is None:
            continue
        if not isinstance(numbers, list):
            return False
        for number_entry in numbers:
            if not isinstance(number_entry, dict):
                return False
            if "value" not in number_entry:
                return False

    return True


def fetch_lottery_result(date):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "ThaiLotteryBot/1.0"
    }
    data = {
        "date": date.strftime("%d"),
        "month": date.strftime("%m"),
        "year": str(date.year),
    }

    last_error = None
    for attempt in range(1, REQUEST_RETRIES + 1):
        try:
            response = requests.post(
                API_URL,
                json=data,
                headers=headers,
                timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
            )
            response.raise_for_status()
            json_response = response.json()
            if validate_lottery_response(json_response):
                return json_response
            print(f"⚠️ Invalid response schema for {date} (attempt {attempt}/{REQUEST_RETRIES})")
            last_error = f"Invalid response schema for {date} (attempt {attempt}/{REQUEST_RETRIES})"
            if attempt < REQUEST_RETRIES:
                time.sleep(REQUEST_RETRY_DELAY_SECONDS * attempt)
                continue
            return None
        except requests.RequestException as error:
            last_error = str(error)
            if attempt < REQUEST_RETRIES:
                print(f"⚠️ Fetch attempt {attempt}/{REQUEST_RETRIES} for {date} failed: {error}")
                time.sleep(REQUEST_RETRY_DELAY_SECONDS * attempt)
            continue

        except Exception as error:
            last_error = str(error)
            print(f"⚠️ Unexpected error for {date} (attempt {attempt}/{REQUEST_RETRIES}): {error}")
            if attempt < REQUEST_RETRIES:
                time.sleep(REQUEST_RETRY_DELAY_SECONDS * attempt)
                continue
            return None

    print(f"❌ Failed for {date} after {REQUEST_RETRIES} attempts: {last_error}")
    return None


# Extract data and ignore round numbers, only storing values
def extract_lottery_data(lottery_result):
    data = lottery_result["response"]["result"]["data"]
    extracted_data = {}

    # Prize groups to include
    prize_groups = ["first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]

    # Iterate through each group like 'first', 'second', 'third', etc.
    for key in prize_groups:
        if key in data:
            # Extract all the 'value' entries for each group
            prize_payload = data[key]
            if not isinstance(prize_payload, dict):
                extracted_data[key] = ""
                continue

            normalized_numbers = [
                normalize_prize_value(key, number.get("value"))
                for number in prize_payload.get("number", [])
                if isinstance(number, dict)
            ]
            unique_numbers = []
            for num in normalized_numbers:
                if not num or num in unique_numbers:
                    continue
                unique_numbers.append(num)
            extracted_data[key] = ",".join(unique_numbers)
        else:
            extracted_data[key] = ""  # If no data, add an empty string

    return extracted_data


def has_any_numbers(extracted_data):
    return any(bool(value) for value in extracted_data.values())


def coerce_and_sort_rows(raw_rows):
    if not raw_rows:
        return []

    normalized = []
    for row in raw_rows:
        normalized_row = {field: "" for field in FIELD_NAMES}
        for field in FIELD_NAMES:
            value = row.get(field, "")
            normalized_row[field] = "" if value is None else str(value).strip()

        draw_date = parse_lottery_date(normalized_row["date"])
        if draw_date is None:
            raise ValueError(f"Invalid date format in row: {normalized_row['date']}")
        normalized_row["date"] = draw_date.isoformat()

        require_row_fields(normalized_row)
        normalized.append(normalized_row)

    return sorted(normalized, key=lambda row: row["date"])


# Collect all the data for the dates
def collect_all_data():
    existing_data = read_local_lottery_data(LOTTERY_RESULTS_FILE)
    latest_known_date = get_latest_local_draw_date(existing_data)

    all_data = {row["date"]: row for row in existing_data if row.get("date")}
    today = datetime.date.today()
    draw_dates = get_pending_draw_dates(latest_known_date, today)

    if not draw_dates:
        print(
            f"ℹ️ No new draw dates found after {latest_known_date or 'no existing data'}; "
            f"keeping {len(all_data)} cached rows."
        )
        return coerce_and_sort_rows([row for row in all_data.values()])

    for date in draw_dates:
        result = fetch_lottery_result(date)
        if result:
            extracted_data = extract_lottery_data(result)
            if not has_any_numbers(extracted_data):
                print(f"⚠️ No draw numbers returned for {date}; skipping row write")
                continue
            all_data[str(date)] = {"date": str(date), **extracted_data}
        time.sleep(1)  # Be polite to the server

    coalesced_rows = [all_data[key] for key in sorted(all_data)]
    return coerce_and_sort_rows(coalesced_rows)


# Save the collected data to a CSV file
def save_to_csv(data, filename=LOTTERY_RESULTS_FILE):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELD_NAMES)
    writer.writeheader()
    for entry in data:
        writer.writerow(entry)
    serialized = output.getvalue()

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as existing_file:
            if existing_file.read() == serialized:
                print("ℹ️ lottery_results.csv is already current; skipping write.")
                return

    temp_filename = f"{filename}.tmp"
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write(serialized)
    os.replace(temp_filename, filename)


# Run the script
if __name__ == "__main__":
    data = collect_all_data()
    save_to_csv(data)
    print("✅ Done! Data saved to lottery_results.csv")
