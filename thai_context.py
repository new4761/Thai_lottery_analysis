"""
Thai Lottery Context & Cultural Events.

Provides Thai holidays, cultural events, and news events that may correlate
with lottery draw patterns and public interest.
"""

import datetime
from typing import List, Tuple, Dict


class ThaiEvent:
    """Represents a Thai cultural event or holiday."""

    def __init__(self, date: datetime.date, name: str, significance: str, category: str):
        self.date = date
        self.name = name
        self.significance = significance
        self.category = category

    def __repr__(self):
        return f"{self.date} | {self.name} ({self.category})"


# Thai public holidays & major events (recurring annually)
THAI_HOLIDAYS = {
    (1, 1): "New Year's Day",
    (2, 26): "Makha Bucha (Buddhist holiday)",
    (4, 6): "Chakri Memorial Day",
    (4, 13): "Songkran Festival (Thai New Year start)",
    (4, 14): "Songkran Festival",
    (4, 15): "Songkran Festival (end)",
    (5, 1): "International Labor Day",
    (7, 28): "King Vajiralongkorn's Birthday",
    (7, 29): "Asahna Bucha (Buddhist holiday)",
    (7, 30): "Buddhist Lent (Vassa) begins",
    (10, 13): "King Bhumibol Memorial Day",
    (10, 14): "King Bhumibol Memorial Day (observed)",
    (10, 23): "Chulalongkorn Memorial Day",
    (12, 5): "King Bhumibol's Birthday (National Day)",
    (12, 10): "Constitution Day",
    (12, 31): "New Year's Eve",
}

# Thai cultural/religious significant dates
THAI_CULTURAL_DATES = {
    (1, 1): "New Year - Shopping, festivities",
    (2, 26): "Makha Bucha - Temple visits, merit-making",
    (4, 6): "Chakri Day - National holiday",
    (4, 13): "Songkran - Water festival, travel peak, family time",
    (4, 14): "Songkran - Celebration peak",
    (4, 15): "Songkran - End festivities",
    (5, 1): "Labor Day",
    (5, 22): "Visakha Bucha - Buddhist celebration",
    (7, 28): "King's Birthday - National celebration",
    (7, 29): "Asahna Bucha - Temple visits",
    (7, 30): "Buddhist Lent - Monks in temples, reduced traveling",
    (10, 13): "King Bhumibol Day - National mourning",
    (10, 23): "King Chulalongkorn Day - Respect",
    (12, 5): "National Day - King's birthday, celebrations",
    (12, 25): "Christmas - International celebration",
    (12, 31): "New Year's Eve - Celebrations, travel home",
}

# News events that might affect lottery interest (2023-2026)
MAJOR_NEWS_EVENTS = {
    (2024, 2, 24): "Thailand elections held - Political interest spike",
    (2024, 3, 25): "Thai government formed - Political news cycle",
    (2024, 4, 6): "Chakri Day - National holiday week",
    (2024, 5, 22): "Visakha Bucha - Major Buddhist holiday",
    (2024, 8, 28): "Thailand National Day - Celebrations",
    (2025, 1, 1): "New Year - Holiday season",
    (2025, 4, 13): "Songkran - Major travel & gathering season",
    (2025, 12, 5): "King's Birthday - National celebration",
}


def get_thai_holidays() -> Dict[Tuple[int, int], str]:
    """Get all Thai holidays (month, day) -> name."""
    return THAI_HOLIDAYS.copy()


def get_thai_cultural_dates() -> Dict[Tuple[int, int], str]:
    """Get Thai cultural/religious significant dates."""
    return THAI_CULTURAL_DATES.copy()


def get_events_for_year(year: int) -> List[Tuple[datetime.date, str, str]]:
    """Get all major events for a specific year.

    Returns:
        List of (date, event_name, significance)
    """
    events = []

    # Add recurring holidays
    for (month, day), name in THAI_HOLIDAYS.items():
        try:
            date = datetime.date(year, month, day)
            events.append((date, name, "Holiday"))
        except ValueError:
            pass  # Invalid date (e.g., Feb 29 in non-leap year)

    # Add specific news events for this year
    for (event_year, month, day), description in MAJOR_NEWS_EVENTS.items():
        if event_year == year:
            date = datetime.date(year, month, day)
            events.append((date, description.split(" - ")[0], "News/Event"))

    return sorted(events, key=lambda x: x[0])


def get_event_context(date: datetime.date) -> str:
    """Get context/description for a specific date.

    Args:
        date: datetime.date to check

    Returns:
        Description of any events on that date
    """
    context_parts = []

    # Check holidays
    key = (date.month, date.day)
    if key in THAI_HOLIDAYS:
        context_parts.append(f"Holiday: {THAI_HOLIDAYS[key]}")

    # Check cultural dates
    if key in THAI_CULTURAL_DATES:
        context_parts.append(f"Cultural: {THAI_CULTURAL_DATES[key]}")

    # Check major news events
    for (event_year, month, day), description in MAJOR_NEWS_EVENTS.items():
        if (date.year, date.month, date.day) == (event_year, month, day):
            context_parts.append(f"News: {description}")

    return " | ".join(context_parts) if context_parts else "Regular day"


def is_holiday(date: datetime.date) -> bool:
    """Check if date is a Thai holiday."""
    return (date.month, date.day) in THAI_HOLIDAYS


def is_cultural_significance(date: datetime.date) -> bool:
    """Check if date has cultural significance."""
    return (date.month, date.day) in THAI_CULTURAL_DATES


def get_holidays_nearby(date: datetime.date, days_before: int = 7, days_after: int = 7) -> List[Tuple[datetime.date, str]]:
    """Get holidays near a specific date.

    Args:
        date: Center date
        days_before: Days to look back
        days_after: Days to look ahead

    Returns:
        List of (holiday_date, holiday_name)
    """
    nearby = []
    start = date - datetime.timedelta(days=days_before)
    end = date + datetime.timedelta(days=days_after)

    current = start
    while current <= end:
        if is_holiday(current):
            holiday_name = THAI_HOLIDAYS[(current.month, current.day)]
            nearby.append((current, holiday_name))
        current += datetime.timedelta(days=1)

    return nearby


def describe_year(year: int) -> str:
    """Get a summary description of major events in a year."""
    events = get_events_for_year(year)

    description = f"\n=== Thai Events in {year} ===\n"
    description += f"Total events: {len(events)}\n\n"

    holidays = [e for e in events if e[2] == "Holiday"]
    news = [e for e in events if e[2] == "News/Event"]

    if holidays:
        description += f"Holidays ({len(holidays)}):\n"
        for date, name, _ in holidays[:5]:  # Show first 5
            description += f"  {date.strftime('%b %d')}: {name}\n"
        if len(holidays) > 5:
            description += f"  ... and {len(holidays) - 5} more\n"

    if news:
        description += f"\nMajor News/Events ({len(news)}):\n"
        for date, name, _ in news:
            description += f"  {date.strftime('%b %d')}: {name}\n"

    return description


# Thai cultural context summary
THAI_CONTEXT_SUMMARY = """
Thai Lottery Cultural Context
==============================

KEY FACTORS AFFECTING LOTTERY DRAWS:

1. SONGKRAN (April 13-15)
   - Thai New Year celebration
   - Water festival, major travel period
   - Family gatherings nationwide
   - Peak holiday season - high lottery interest

2. BUDDHIST HOLIDAYS
   - Makha Bucha (Feb 26): Temple visits, merit-making
   - Visakha Bucha (May): Major Buddhist celebration
   - Asahna Bucha (July): Buddhist Lent begins
   - Temple activities correlate with draws

3. ROYAL CELEBRATIONS
   - King Bhumibol Birthday (Oct 13): National day
   - King Vajiralongkorn Birthday (July 28)
   - Chakri Day (April 6): Dynasty founding
   - National pride, celebrations

4. POLITICAL EVENTS
   - Elections (Feb 2024): High public engagement
   - Government formation: Political news cycle
   - Constitutional events: Civic participation

5. TRAVEL SEASONS
   - Songkran (April): Major travel exodus
   - Year-end (Dec): Holiday returns home
   - Buddhist Lent (July-Oct): Reduced traveling
   - Travel affects lottery ticket distribution

6. CULTURAL BELIEFS
   - Lucky numbers associated with holidays
   - Buddhist merit-making on special days
   - Auspicious dates for major activities
   - Lunar calendar significance

7. ECONOMIC CYCLES
   - Bonus seasons (May, December)
   - Festival spending patterns
   - Tourism peaks (Dec, April)
   - Affects lottery participation

DRAW SCHEDULE CONTEXT:
- Draws on 1st and 16th (biweekly)
- May draws on 2nd and 16th (Songkran compensation)
- Holiday shifts create missed/rescheduled draws
- Special draws for major holidays possible
"""


if __name__ == "__main__":
    # Example usage
    print(THAI_CONTEXT_SUMMARY)
    print(describe_year(2024))
    print(describe_year(2025))

    # Test event lookup
    test_date = datetime.date(2024, 4, 13)
    print(f"\n{test_date}: {get_event_context(test_date)}")
    print(f"Nearby holidays: {get_holidays_nearby(test_date, 3, 3)}")
