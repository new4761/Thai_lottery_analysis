"""
Thai lottery draw date calendar with holiday exception handling.

Normally draws occur on the 1st and 16th of each month, with May 2nd instead of May 16th.
However, official lottery draws may be shifted due to Thai public holidays.

This module handles the standard calendar and known exceptions.
"""

import datetime


STANDARD_DRAW_DAYS = {
    1: [1, 16],      # January
    2: [1, 16],      # February
    3: [1, 16],      # March
    4: [1, 16],      # April
    5: [2, 16],      # May (2nd instead of 16th)
    6: [1, 16],      # June
    7: [1, 16],      # July
    8: [1, 16],      # August
    9: [1, 16],      # September
    10: [1, 16],     # October
    11: [1, 16],     # November
    12: [1, 16],     # December
}

# Known holiday shifts: (original_date, shifted_date, reason)
# Format: datetime.date objects for shift dates
KNOWN_SHIFTS = {
    # 2024 New Year shift (if drawn earlier)
    datetime.date(2024, 1, 1): datetime.date(2023, 12, 30),  # New Year (Jan 1 -> Dec 30)
    # Thai New Year (Songkran) - April typically shifted
    datetime.date(2024, 4, 13): datetime.date(2024, 4, 10),  # Songkran week shift
    datetime.date(2024, 4, 14): datetime.date(2024, 4, 10),  # Songkran day
    # Add more known shifts as they're discovered
    # Format: if lottery would normally be on X, but was actually on Y
}


def get_draw_dates(start_date="2010-03-01", end_date=None):
    """
    Get all expected lottery draw dates in the given range.
    Accounts for standard schedule and known holiday exceptions.

    Args:
        start_date: Start date (string YYYY-MM-DD or date object)
        end_date: End date (defaults to today)

    Returns:
        List of datetime.date objects in chronological order
    """
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date is None:
        end_date = datetime.date.today()
    elif isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    dates = set()

    # Generate standard schedule
    current = start_date
    while current <= end_date:
        month = current.month
        day = current.day

        if month in STANDARD_DRAW_DAYS:
            for draw_day in STANDARD_DRAW_DAYS[month]:
                try:
                    draw_date = datetime.date(current.year, month, draw_day)
                    if start_date <= draw_date <= end_date:
                        dates.add(draw_date)
                except ValueError:
                    pass  # Day doesn't exist in this month (e.g., Feb 29 in non-leap year)

        # Move to next month
        if month == 12:
            current = datetime.date(current.year + 1, 1, 1)
        else:
            current = datetime.date(current.year, month + 1, 1)

    # Apply known shifts (if original was scheduled, use shifted date instead)
    shifted_dates = set()
    for original, shifted in KNOWN_SHIFTS.items():
        if original in dates and start_date <= shifted <= end_date:
            dates.discard(original)
            dates.add(shifted)
            shifted_dates.add(shifted)

    return sorted(list(dates))


def get_draw_dates_description():
    """Return human-readable description of draw schedule."""
    desc = (
        "Thai lottery draws occur on:\n"
        "- 1st and 16th of most months\n"
        "- 2nd and 16th of May (Songkran exception)\n"
        "\n"
        "Holiday shifts may move draws earlier or later. "
        "See KNOWN_SHIFTS for documented exceptions."
    )
    return desc


if __name__ == "__main__":
    # Quick test
    dates = get_draw_dates("2024-01-01", "2024-12-31")
    print(f"Draw dates in 2024: {len(dates)} dates")
    print(f"Expected: ~24 dates (12 months × 2)")
    print(f"\nFirst 5: {dates[:5]}")
    print(f"Last 5: {dates[-5:]}")
