import os
import json
import gspread
import requests
import csv
from io import StringIO
from google.oauth2.service_account import Credentials


REQUEST_TIMEOUT_SECONDS = 30


def fetch_csv_rows(csv_url):
    response = requests.get(csv_url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    rows = list(csv.reader(StringIO(response.text)))
    if not rows:
        raise RuntimeError(f"No rows found in CSV payload from {csv_url}")
    return rows


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
