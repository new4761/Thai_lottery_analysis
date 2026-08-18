import csv
import datetime
import os
import time
import requests

LOTTERY_RESULTS_FILE = "lottery_results.csv"
LOTTERY_START_DATE = "2010-03-01"
FIELD_NAMES = ["date", "first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]


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
            if row.get("date"):
                rows.append(row)
    return rows


def get_latest_local_draw_date(rows):
    latest = None
    for row in rows:
        row_date = parse_lottery_date(row.get("date"))
        if row_date and (latest is None or row_date > latest):
            latest = row_date
    return latest


# Function to fetch lottery results
def fetch_lottery_result(date):
    url = "https://www.glo.or.th/api/checking/getLotteryResult"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "date": date.strftime("%d"),
        "month": date.strftime("%m"),
        "year": str(date.year),
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            json_response = response.json()
            if json_response.get("response") is not None:
                return json_response
            print(f"⚠️ No data for {date} (null response field)")
            return None
        print(f"❌ Failed for {date}, status code: {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Exception for {date}: {e}")
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
            # Extract all the 'value' entries for each group, treating numbers as strings to preserve leading zeros
            extracted_data[key] = ",".join([str(number["value"]).zfill(len(number["value"])) for number in data[key]["number"]])
        else:
            extracted_data[key] = ""  # If no data, add an empty string

    return extracted_data


# Collect all the data for the dates
def collect_all_data():
    existing_data = read_local_lottery_data(LOTTERY_RESULTS_FILE)
    latest_known_date = get_latest_local_draw_date(existing_data)

    start_date = LOTTERY_START_DATE
    if latest_known_date:
        # Re-check one draw cycle to recover from transient fetch misses.
        resume_from = latest_known_date - datetime.timedelta(days=14)
        start_date_obj = datetime.datetime.strptime(LOTTERY_START_DATE, "%Y-%m-%d").date()
        start_date = max(start_date_obj, resume_from).strftime("%Y-%m-%d")

    all_data = {row["date"]: row for row in existing_data if row.get("date")}
    today = datetime.date.today()
    draw_dates = get_draw_dates(start_date, today)

    for date in draw_dates:
        if latest_known_date and date <= latest_known_date:
            continue
        result = fetch_lottery_result(date)
        if result:
            extracted_data = extract_lottery_data(result)
            all_data[str(date)] = {"date": str(date), **extracted_data}
        time.sleep(1)  # Be polite to the server

    return [all_data[key] for key in sorted(all_data)]


# Save the collected data to a CSV file
def save_to_csv(data, filename=LOTTERY_RESULTS_FILE):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)


# Run the script
if __name__ == "__main__":
    data = collect_all_data()
    save_to_csv(data)
    print("✅ Done! Data saved to lottery_results.csv")
