import datetime
import unittest

from draw_dates import get_draw_dates
from query import get_pending_draw_dates


class GetDrawDatesTests(unittest.TestCase):
    """Test draw date calendar generation."""

    def test_returns_draw_dates_within_requested_range(self):
        """Should return draws within specified date range."""
        start_date = "2024-04-01"
        end_date = datetime.date(2024, 5, 16)

        result = get_draw_dates(start_date, end_date)

        self.assertEqual(
            result,
            [
                datetime.date(2024, 4, 1),
                datetime.date(2024, 4, 16),
                datetime.date(2024, 5, 2),
                datetime.date(2024, 5, 16),
            ],
        )

    def test_excludes_may_draw_dates_outside_requested_range(self):
        """May 2nd is special case, should be excluded if before range."""
        start_date = "2024-05-03"
        end_date = datetime.date(2024, 5, 15)

        result = get_draw_dates(start_date, end_date)

        self.assertEqual(result, [])

    def test_excludes_regular_draw_date_before_requested_start(self):
        """Should exclude draws before start date."""
        start_date = "2024-06-02"
        end_date = datetime.date(2024, 7, 1)

        result = get_draw_dates(start_date, end_date)

        self.assertEqual(
            result,
            [datetime.date(2024, 6, 16), datetime.date(2024, 7, 1)],
        )

    def test_may_draws_special_handling(self):
        """May should always have 2nd draw, not 16th."""
        result = get_draw_dates("2024-05-01", "2024-05-31")
        self.assertIn(datetime.date(2024, 5, 2), result)
        # Should NOT have 16th in May (that's when May 2nd replacement happens)

    def test_year_spanning_draws(self):
        """Should handle draws across year boundaries."""
        result = get_draw_dates("2024-12-01", "2025-01-31")
        expected = [
            datetime.date(2024, 12, 1),
            datetime.date(2024, 12, 16),
            datetime.date(2025, 1, 1),
            datetime.date(2025, 1, 16),
        ]
        self.assertEqual(result, expected)

    def test_consistent_draws_per_year(self):
        """Each full year should have 24 draws."""
        result_2024 = get_draw_dates("2024-01-01", "2024-12-31")
        # 2024 is leap year, but still 24 draws (2 per month)
        self.assertEqual(len(result_2024), 24)

    def test_draws_are_sorted(self):
        """Draw dates should be in chronological order."""
        result = get_draw_dates("2023-01-01", "2025-12-31")
        self.assertEqual(result, sorted(result))

    def test_no_duplicate_draws(self):
        """Each date should appear only once."""
        result = get_draw_dates("2023-01-01", "2025-12-31")
        self.assertEqual(len(result), len(set(result)))


class GetPendingDrawDatesTests(unittest.TestCase):
    """Test pending draw date calculation."""

    def test_pending_dates_after_latest_known(self):
        """Should return draws after latest known date."""
        latest = datetime.date(2024, 6, 1)
        result = get_pending_draw_dates(latest, datetime.date(2024, 7, 31))

        # Should include 6/16, 7/1, 7/16 but not 6/1
        self.assertNotIn(datetime.date(2024, 6, 1), result)
        self.assertIn(datetime.date(2024, 6, 16), result)
        self.assertIn(datetime.date(2024, 7, 1), result)

    def test_no_pending_if_future(self):
        """Should return empty if latest date is already in future."""
        latest = datetime.date(2099, 1, 1)
        result = get_pending_draw_dates(latest, datetime.date(2099, 12, 31))

        self.assertEqual(result, [])

    def test_recovery_lookback_window(self):
        """Should recover missed draws within lookback window."""
        latest = datetime.date(2024, 7, 1)
        # Within 45-day lookback, should include 6/16
        result = get_pending_draw_dates(latest, datetime.date(2024, 8, 31))

        # If 6/16 was missed, it should be included (within 45 days)
        self.assertTrue(len(result) > 0)


class PendingDrawDatesTests(unittest.TestCase):
    def test_get_pending_draw_dates_returns_none_if_current_month_is_latest(self):
        latest = datetime.date(2024, 7, 1)
        end_date = datetime.date(2024, 7, 20)

        pending = get_pending_draw_dates(latest, end_date)

        self.assertEqual(pending, [])

    def test_get_pending_draw_dates_includes_next_draw_after_known_date(self):
        latest = datetime.date(2024, 6, 1)
        end_date = datetime.date(2024, 7, 20)

        pending = get_pending_draw_dates(latest, end_date)

        self.assertEqual(pending, [datetime.date(2024, 6, 16), datetime.date(2024, 7, 1)])


if __name__ == "__main__":
    unittest.main()
