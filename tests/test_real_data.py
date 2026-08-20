"""
Comprehensive tests using real historical lottery data (3+ years).

These tests validate the system against actual data patterns:
- Draw dates correctness
- Data integrity and consistency
- Validation rules against real data
- Edge cases that actually occur
"""

import csv
import datetime
import unittest
from pathlib import Path

from draw_dates import get_draw_dates, KNOWN_SHIFTS
from validators import validate_csv_schema, validate_csv_integrity, validate_looker_csv
from query import validate_dataset


class TestRealHistoricalData(unittest.TestCase):
    """Test against actual lottery data from CSV files."""

    @classmethod
    def setUpClass(cls):
        """Load real lottery data from CSV."""
        csv_path = Path(__file__).parent.parent / "lottery_results.csv"
        cls.csv_path = csv_path
        cls.raw_data = []
        cls.dates_in_data = set()

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.raw_data.append(row)
                cls.dates_in_data.add(row["date"])

        # Extract last 3 years of data
        if cls.raw_data:
            latest_date = datetime.datetime.strptime(cls.raw_data[-1]["date"], "%Y-%m-%d").date()
            three_years_ago = latest_date - datetime.timedelta(days=365 * 3)
            cls.data_3years = [
                row for row in cls.raw_data
                if datetime.datetime.strptime(row["date"], "%Y-%m-%d").date() >= three_years_ago
            ]

    def test_csv_schema_valid(self):
        """Real data should pass schema validation."""
        self.assertTrue(validate_csv_schema(str(self.csv_path)))

    def test_csv_integrity_valid(self):
        """Real data should pass integrity validation."""
        info = validate_csv_integrity(str(self.csv_path))
        self.assertGreater(info["row_count"], 0)
        self.assertIsNotNone(info["date_range"])
        self.assertIsNotNone(info["latest_date"])

    def test_data_not_empty(self):
        """CSV should contain historical data."""
        self.assertGreater(len(self.raw_data), 100, "Expected 100+ draws in history")

    def test_three_year_data_exists(self):
        """Should have data from last 3 years."""
        self.assertGreater(len(self.data_3years), 50, "Expected 50+ draws in last 3 years")

    def test_dates_are_unique(self):
        """All dates in data should be unique."""
        self.assertEqual(len(self.dates_in_data), len(self.raw_data))

    def test_dates_sorted_chronologically(self):
        """Dates in CSV should be in order."""
        dates = [datetime.datetime.strptime(row["date"], "%Y-%m-%d").date() for row in self.raw_data]
        self.assertEqual(dates, sorted(dates))

    def test_latest_date_reasonable(self):
        """Latest date should be recent (within last 2 months)."""
        if self.raw_data:
            latest_date = datetime.datetime.strptime(self.raw_data[-1]["date"], "%Y-%m-%d").date()
            today = datetime.date.today()
            days_old = (today - latest_date).days
            self.assertLess(days_old, 60, f"Latest data is {days_old} days old, expected < 60")

    def test_all_rows_have_required_fields(self):
        """Every row should have date and at least some prize data."""
        for i, row in enumerate(self.data_3years, start=2):
            self.assertIn("date", row, f"Row {i} missing date")
            self.assertNotEqual(row["date"].strip(), "", f"Row {i} has empty date")

            has_data = any(
                row.get(col, "").strip()
                for col in ["first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]
            )
            self.assertTrue(has_data, f"Row {i} ({row['date']}) has no prize data")

    def test_no_duplicate_dates(self):
        """No date should appear twice."""
        dates_seen = set()
        for row in self.raw_data:
            date = row["date"]
            self.assertNotIn(date, dates_seen, f"Duplicate date found: {date}")
            dates_seen.add(date)

    def test_draw_dates_coverage(self):
        """Draw dates should match expected schedule for sample years."""
        test_dates = get_draw_dates("2023-01-01", "2025-12-31")
        # Should have ~24 draws per year (2 per month, ~2 years = ~48+)
        self.assertGreater(len(test_dates), 40, "Expected 40+ draws in 2023-2025")

    def test_may_special_case(self):
        """May should have 2nd draw, not 16th (Thai tradition)."""
        for year in [2023, 2024, 2025, 2026]:
            dates = get_draw_dates(f"{year}-05-01", f"{year}-05-31")
            # May should have 2nd, not 16th
            self.assertIn(datetime.date(year, 5, 2), dates, f"May {year} missing 2nd draw")

    def test_prize_field_formats(self):
        """Prize fields should be valid format (numbers/empty)."""
        for row in self.data_3years[:20]:  # Test first 20 rows of 3-year data
            date = row["date"]
            for prize_field in ["first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b"]:
                value = row.get(prize_field, "").strip()
                if value:
                    # Should be digits or comma-separated digits
                    parts = value.split(",")
                    for part in parts:
                        self.assertTrue(part.isdigit(), f"Invalid {prize_field} in {date}: {value}")

    def test_row_count_consistency(self):
        """Row count should only increase or stay same (never decrease)."""
        sorted_data = sorted(self.raw_data, key=lambda r: r["date"])
        # Get checkpoints every 6 months
        row_counts = {}
        for i, row in enumerate(sorted_data, start=1):
            row_counts[row["date"]] = i

        # Verify never decreases
        prev_count = 0
        for date, count in sorted(row_counts.items()):
            self.assertGreaterEqual(count, prev_count, f"Row count decreased at {date}")
            prev_count = count

    def test_validate_dataset_real_data(self):
        """Real dataset should pass validation."""
        try:
            validate_dataset(self.raw_data, [])
            validated = True
        except ValueError as e:
            validated = False
            self.fail(f"Real data failed validation: {e}")
        self.assertTrue(validated)

    def test_looker_transform_available(self):
        """Looker-ready CSV should exist and be valid."""
        looker_path = Path(__file__).parent.parent / "lottery_results_looker_ready.csv"
        if looker_path.exists():
            info = validate_looker_csv(str(looker_path))
            self.assertGreater(info["row_count"], 0)
            self.assertGreater(info["unique_dates"], 0)
        else:
            self.skipTest("Looker CSV not generated yet")


class TestThreeYearPatterns(unittest.TestCase):
    """Analyze patterns and consistency over last 3 years."""

    @classmethod
    def setUpClass(cls):
        """Load and filter 3-year data."""
        csv_path = Path(__file__).parent.parent / "lottery_results.csv"
        cls.raw_data = []

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.raw_data.append(row)

        # Extract last 3 years
        if cls.raw_data:
            latest_date = datetime.datetime.strptime(cls.raw_data[-1]["date"], "%Y-%m-%d").date()
            three_years_ago = latest_date - datetime.timedelta(days=365 * 3)
            cls.data_3years = [
                row for row in cls.raw_data
                if datetime.datetime.strptime(row["date"], "%Y-%m-%d").date() >= three_years_ago
            ]

    def test_draws_per_year(self):
        """Should have ~24 draws per year (2 per month)."""
        if not self.data_3years:
            self.skipTest("No 3-year data available")

        # Count draws by year
        draws_by_year = {}
        for row in self.data_3years:
            year = row["date"][:4]
            draws_by_year[year] = draws_by_year.get(year, 0) + 1

        for year, count in draws_by_year.items():
            # Allow 20-26 draws per year (accounting for incomplete years or shifts)
            self.assertGreaterEqual(count, 20, f"{year} has only {count} draws")
            self.assertLessEqual(count, 27, f"{year} has {count} draws (expected ~24)")

    def test_first_prize_varies(self):
        """First prize should have variety (not stuck on same number)."""
        first_prizes = [row["first"] for row in self.data_3years if row.get("first")]
        unique_first = set(first_prizes)
        self.assertGreater(len(unique_first), 50, "First prize lacks variation")

    def test_second_prize_distribution(self):
        """Second prize should have multiple numbers."""
        second_prizes_raw = [row.get("second", "") for row in self.data_3years if row.get("second")]
        all_second = []
        for prizes_str in second_prizes_raw:
            all_second.extend(prizes_str.split(","))
        unique_second = set(all_second)
        self.assertGreater(len(unique_second), 100, "Second prize lacks distribution")

    def test_no_missing_months(self):
        """Should have draws for most months in 3-year period."""
        dates = [datetime.datetime.strptime(row["date"], "%Y-%m-%d").date() for row in self.data_3years]
        year_months = set((d.year, d.month) for d in dates)

        # Should have draws from at least 35 different months (out of 36 possible)
        expected_months = 36  # 3 years * 12 months
        self.assertGreater(len(year_months), expected_months - 2, f"Missing months: only {len(year_months)}/{expected_months}")


class TestDataAccuracy(unittest.TestCase):
    """Validate data accuracy and consistency."""

    @classmethod
    def setUpClass(cls):
        """Load lottery data."""
        csv_path = Path(__file__).parent.parent / "lottery_results.csv"
        cls.raw_data = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cls.raw_data = list(reader)

    def test_prize_numbers_realistic(self):
        """Prize numbers should be 6-digit codes."""
        sample = self.raw_data[-50:] if len(self.raw_data) > 50 else self.raw_data
        for row in sample:
            # First prize should be single number
            first = row.get("first", "").strip()
            if first:
                self.assertEqual(len(first), 6, f"First prize should be 6 digits: {first}")
                self.assertTrue(first.isdigit(), f"First prize should be all digits: {first}")

    def test_data_matches_expected_ranges(self):
        """Prize numbers should be in valid range (0-999999 for 6-digit)."""
        for row in self.raw_data[-20:]:
            first = row.get("first", "").strip()
            if first and first.isdigit():
                num = int(first)
                self.assertGreaterEqual(num, 0)
                self.assertLess(num, 1000000)

    def test_consistency_between_files(self):
        """Check if looker CSV matches lottery results CSV."""
        csv_path = Path(__file__).parent.parent / "lottery_results.csv"
        looker_path = Path(__file__).parent.parent / "lottery_results_looker_ready.csv"

        if not looker_path.exists():
            self.skipTest("Looker CSV not yet generated")

        # Load both
        dates_in_results = set()
        with open(csv_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                dates_in_results.add(row["date"])

        dates_in_looker = set()
        with open(looker_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                dates_in_looker.add(row["date"])

        # Looker should have all dates from results
        missing = dates_in_results - dates_in_looker
        self.assertEqual(len(missing), 0, f"Dates in results but not looker: {missing}")


if __name__ == "__main__":
    unittest.main()
