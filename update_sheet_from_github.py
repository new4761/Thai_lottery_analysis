import os
import json
import gspread
import requests
import csv
import time
from io import StringIO
from google.oauth2.service_account import Credentials


REQUEST_TIMEOUT_SECONDS = 30
REQUIRED_COLUMNS = {"date", "first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"}
REQUEST_RETRIES = 3


def fetch_csv_rows(csv_url):
    last_error = None
    for attempt in range(1, REQUEST_RETRIES + 1):
        try:
            response = requests.get(csv_url, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            rows = list(csv.reader(StringIO(response.text)))
            if not rows or len(rows) < 2:
                raise RuntimeError(f"No data rows found in CSV payload from {csv_url}")
            header = [column.strip().lstrip("\ufeff") for column in rows[0]]
            if not REQUIRED_COLUMNS.issubset(set(header)):
                raise RuntimeError(
                    f"CSV from {csv_url} is missing required columns."
                )
            return rows
        except Exception as error:
            last_error = error
            if attempt < REQUEST_RETRIES:
                time.sleep(2 * attempt)
                continue
    raise RuntimeError(
        f"Failed to fetch valid CSV from {csv_url} after {REQUEST_RETRIES} attempts: {last_error}"
    )


def update_sheet_from_csv(spreadsheet_name, csv_url):
    print(f"Starting update for spreadsheet named: '{spreadsheet_name}'")

    csv_data = fetch_csv_rows(csv_url)

    # Load credentials from env var
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_json:
        raise RuntimeError("Missing GOOGLE_APPLICATION_CREDENTIALS environment variable")
    creds_info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)

    client = gspread.authorize(creds)

    # Open spreadsheet by name and get first sheet
    spreadsheet = client.open(spreadsheet_name)
    worksheet = spreadsheet.sheet1

    # Clear existing data
    worksheet.clear()

    # Update sheet (values first, range second)
    worksheet.update(values=csv_data, range_name='A1')

    print(f"Successfully updated '{spreadsheet.title}' (sheet: '{worksheet.title}') with data from {csv_url}")

if __name__ == "__main__":
    update_sheet_from_csv(
        "lottery_results",
        "https://raw.githubusercontent.com/new4761/Thai_lottery_analysis/refs/heads/main/lottery_results.csv"
    )
    update_sheet_from_csv(
        "lottery_results_looker_ready",
        "https://raw.githubusercontent.com/new4761/Thai_lottery_analysis/refs/heads/main/lottery_results_looker_ready.csv"
    )
