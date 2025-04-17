import requests
import datetime
import time
import csv

# Get the list of draw dates based on the year and special conditions for May
def get_draw_dates(start_date="2010-03-01", end_date=None):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = end_date or datetime.date.today()  # Use today as default end date

    draw_dates = []
    for year in range(start_date.year, end_date.year + 1):
        for month in range(1, 13):
            if year == start_date.year and month < start_date.month:
                continue  # Skip months before the start date year-month
            if year == end_date.year and month > end_date.month:
                break  # Stop if the year-month is after the end date

            if month == 5:
                draw_dates.append(datetime.date(year, 5, 2))  # May special case
                draw_dates.append(datetime.date(year, 5, 16))
            else:
                for day in [1, 16]:
                    try:
                        date = datetime.date(year, month, day)
                        if date <= end_date:  # Only add dates within range
                            draw_dates.append(date)
                    except:
                        pass
    draw_dates.sort()
    return draw_dates

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
            else:
                print(f"⚠️ No data for {date} (null response field)")
                return None
        else:
            print(f"❌ Failed for {date}, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception for {date}: {e}")
        return None

# Extract data and ignore round numbers, only storing values
def extract_lottery_data(lottery_result):
    data = lottery_result['response']['result']['data']
    extracted_data = {}

    # Prize groups to include
    prize_groups = ['first', 'second', 'third', 'fourth', 'fifth', 'last2', 'last3f', 'last3b', 'near1']

    # Iterate through each group like 'first', 'second', 'third', etc.
    for key in prize_groups:
        if key in data:
            # Extract all the 'value' entries for each group, treating numbers as strings to preserve leading zeros
            extracted_data[key] = ','.join([str(number['value']).zfill(len(number['value'])) for number in data[key]['number']])
        else:
            extracted_data[key] = ''  # If no data, add an empty string

    return extracted_data

# Collect all the data for the dates
def collect_all_data():
    all_data = []
    draw_dates = get_draw_dates("2010-03-01")  # Starting from March 1, 2010
    today = datetime.date.today()
    for date in draw_dates:
        if date > today:
            break  # Stop if the date is in the future
        result = fetch_lottery_result(date)
        if result:
            extracted_data = extract_lottery_data(result)
            all_data.append({"date": str(date), **extracted_data})
        time.sleep(1)  # Be polite to the server
    return all_data

# Save the collected data to a CSV file
def save_to_csv(data, filename="lottery_results.csv"):
    # Define the column headers
    fieldnames = ["date", "first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

# Run the script
if __name__ == "__main__":
    data = collect_all_data()
    save_to_csv(data)
    print("✅ Done! Data saved to lottery_results.csv")
