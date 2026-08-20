"""
Tests for data validators module.

Validates:
- CSV schema validation
- Data integrity checks
- Looker CSV format
"""

import csv
import datetime
import tempfile
import unittest
from pathlib import Path

from validators import (
    validate_csv_schema,
    validate_csv_integrity,
    validate_looker_csv,
    REQUIRED_COLUMNS,
)


class ValidateCsvSchemaTests(unittest.TestCase):
    """Test CSV schema validation."""

    def test_valid_schema_with_all_columns(self):
        """Should pass when all required columns present."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["date", "first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"])
            writer.writerow(["2024-01-01", "123456", "", "", "", "", "", "", "", ""])
            f.flush()

            result = validate_csv_schema(f.name)
            self.assertTrue(result)

    def test_missing_required_column_fails(self):
        """Should fail when required column missing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["date", "first", "second"])  # Missing most columns
            f.flush()

            with self.assertRaises(ValueError) as ctx:
                validate_csv_schema(f.name)
            self.assertIn("missing required columns", str(ctx.exception).lower())

    def test_file_not_found_fails(self):
        """Should fail if file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            validate_csv_schema("/nonexistent/path/file.csv")

    def test_empty_file_fails(self):
        """Should fail if file has no header."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("")
            f.flush()

            with self.assertRaises(ValueError):
                validate_csv_schema(f.name)


class ValidateCsvIntegrityTests(unittest.TestCase):
    """Test CSV data integrity validation."""

    def test_valid_data_passes(self):
        """Valid data should pass integrity check."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=list(REQUIRED_COLUMNS))
            writer.writeheader()
            writer.writerow({
                "date": "2024-01-01",
                "first": "123456",
                "second": "789012",
                "third": "", "fourth": "", "fifth": "",
                "last2": "34", "last3f": "567", "last3b": "012", "near1": "345678"
            })
            f.flush()

            info = validate_csv_integrity(f.name)
            self.assertEqual(info["row_count"], 1)
            self.assertIsNotNone(info["date_range"])

    def test_duplicate_dates_fail(self):
        """Duplicate dates should fail validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=list(REQUIRED_COLUMNS))
            writer.writeheader()
            for i in range(2):
                writer.writerow({
                    "date": "2024-01-01",  # Same date twice
                    "first": "123456",
                    "second": "", "third": "", "fourth": "", "fifth": "",
                    "last2": "", "last3f": "", "last3b": "", "near1": ""
                })
            f.flush()

            with self.assertRaises(ValueError) as ctx:
                validate_csv_integrity(f.name)
            self.assertIn("duplicate", str(ctx.exception).lower())

    def test_missing_date_fails(self):
        """Row without date should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=list(REQUIRED_COLUMNS))
            writer.writeheader()
            writer.writerow({
                "date": "",  # Missing date
                "first": "123456",
                "second": "", "third": "", "fourth": "", "fifth": "",
                "last2": "", "last3f": "", "last3b": "", "near1": ""
            })
            f.flush()

            with self.assertRaises(ValueError) as ctx:
                validate_csv_integrity(f.name)
            self.assertIn("missing date", str(ctx.exception).lower())

    def test_invalid_date_format_fails(self):
        """Invalid date format should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=list(REQUIRED_COLUMNS))
            writer.writeheader()
            writer.writerow({
                "date": "01-01-2024",  # Wrong format (not YYYY-MM-DD)
                "first": "123456",
                "second": "", "third": "", "fourth": "", "fifth": "",
                "last2": "", "last3f": "", "last3b": "", "near1": ""
            })
            f.flush()

            with self.assertRaises(ValueError) as ctx:
                validate_csv_integrity(f.name)
            self.assertIn("invalid date format", str(ctx.exception).lower())

    def test_future_date_fails(self):
        """Future dates should fail validation."""
        future_date = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=list(REQUIRED_COLUMNS))
            writer.writeheader()
            writer.writerow({
                "date": future_date,
                "first": "123456",
                "second": "", "third": "", "fourth": "", "fifth": "",
                "last2": "", "last3f": "", "last3b": "", "near1": ""
            })
            f.flush()

            with self.assertRaises(ValueError) as ctx:
                validate_csv_integrity(f.name)
            self.assertIn("future", str(ctx.exception).lower())

    def test_no_data_rows_fails(self):
        """Empty CSV should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=list(REQUIRED_COLUMNS))
            writer.writeheader()
            # No data rows
            f.flush()

            with self.assertRaises(ValueError) as ctx:
                validate_csv_integrity(f.name)
            self.assertIn("no data rows", str(ctx.exception).lower())

    def test_row_count_decrease_fails(self):
        """Row count should not decrease."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=list(REQUIRED_COLUMNS))
            writer.writeheader()
            writer.writerow({
                "date": "2024-01-01",
                "first": "123456",
                "second": "", "third": "", "fourth": "", "fifth": "",
                "last2": "", "last3f": "", "last3b": "", "near1": ""
            })
            f.flush()

            # Validate with previous row count of 10 (current is 1)
            with self.assertRaises(ValueError) as ctx:
                validate_csv_integrity(f.name, previous_row_count=10)
            self.assertIn("row count decreased", str(ctx.exception).lower())


class ValidateLookerCsvTests(unittest.TestCase):
    """Test Looker CSV format validation."""

    def test_valid_looker_csv_passes(self):
        """Valid Looker CSV should pass."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["date", "prize_type", "number"])
            writer.writerow(["2024-01-01", "first", "123456"])
            writer.writerow(["2024-01-01", "second", "789012"])
            f.flush()

            info = validate_looker_csv(f.name)
            self.assertEqual(info["row_count"], 2)
            self.assertEqual(info["unique_dates"], 1)

    def test_wrong_schema_fails(self):
        """Wrong column names should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["date", "prize", "value"])  # Wrong columns
            writer.writerow(["2024-01-01", "first", "123456"])
            f.flush()

            with self.assertRaises(ValueError) as ctx:
                validate_looker_csv(f.name)
            self.assertIn("wrong schema", str(ctx.exception).lower())

    def test_no_data_rows_fails(self):
        """Looker CSV with no data should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["date", "prize_type", "number"])
            # No data
            f.flush()

            with self.assertRaises(ValueError) as ctx:
                validate_looker_csv(f.name)
            self.assertIn("no data rows", str(ctx.exception).lower())

    def test_missing_date_fails(self):
        """Row without date should fail."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(["date", "prize_type", "number"])
            writer.writerow(["", "first", "123456"])  # Missing date
            f.flush()

            with self.assertRaises(ValueError) as ctx:
                validate_looker_csv(f.name)
            self.assertIn("missing date", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
