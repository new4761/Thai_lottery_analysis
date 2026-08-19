import datetime
import unittest

from query import get_draw_dates, get_pending_draw_dates


class GetDrawDatesTests(unittest.TestCase):
    def test_returns_draw_dates_within_requested_range(self):
        # Given
        start_date = "2024-04-01"
        end_date = datetime.date(2024, 5, 16)

        # When
        result = get_draw_dates(start_date, end_date)

        # Then
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
        # Given
        start_date = "2024-05-03"
        end_date = datetime.date(2024, 5, 15)

        # When
        result = get_draw_dates(start_date, end_date)

        # Then
        self.assertEqual(result, [])

    def test_excludes_regular_draw_date_before_requested_start(self):
        # Given
        start_date = "2024-06-02"
        end_date = datetime.date(2024, 7, 1)

        # When
        result = get_draw_dates(start_date, end_date)

        # Then
        self.assertEqual(
            result,
            [datetime.date(2024, 6, 16), datetime.date(2024, 7, 1)],
        )


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
