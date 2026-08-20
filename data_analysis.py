"""
Deep Data Analysis of Thai Lottery Draws.

Comprehensive statistical analysis including:
- Distribution analysis (chi-square tests)
- Temporal patterns and trends
- Number frequency and hot/cold analysis
- Thai holiday correlation
- Statistical insights and anomalies
"""

import csv
import datetime
import math
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set

from thai_context import (
    get_event_context,
    is_holiday,
    is_cultural_significance,
    get_thai_holidays,
)


class LotteryDataAnalysis:
    """Comprehensive analysis of lottery draw data."""

    def __init__(self, csv_path: str = "lottery_results.csv"):
        """Initialize analysis with lottery CSV data."""
        self.csv_path = csv_path
        self.draws = []
        self.load_data()

    def load_data(self):
        """Load lottery data from CSV."""
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.draws = list(reader)
        print(f"✅ Loaded {len(self.draws)} lottery draws")

    def get_date_range(self) -> Tuple[datetime.date, datetime.date]:
        """Get date range of data."""
        if not self.draws:
            return None, None
        dates = [datetime.datetime.strptime(d["date"], "%Y-%m-%d").date() for d in self.draws]
        return min(dates), max(dates)

    def get_3year_data(self) -> List[Dict]:
        """Get data from last 3 years."""
        if not self.draws:
            return []
        latest_date = datetime.datetime.strptime(self.draws[-1]["date"], "%Y-%m-%d").date()
        three_years_ago = latest_date - datetime.timedelta(days=365 * 3)
        return [
            d for d in self.draws
            if datetime.datetime.strptime(d["date"], "%Y-%m-%d").date() >= three_years_ago
        ]

    def extract_numbers(self, field: str, draws: List[Dict] = None) -> List[str]:
        """Extract all numbers from a specific prize field.

        Args:
            field: Prize field name (first, second, third, etc.)
            draws: Draws to analyze (default: all)

        Returns:
            List of all lottery numbers for that prize
        """
        if draws is None:
            draws = self.draws

        numbers = []
        for draw in draws:
            prize_str = draw.get(field, "").strip()
            if prize_str:
                numbers.extend(prize_str.split(","))
        return numbers

    def analyze_distribution(self, field: str, draws: List[Dict] = None) -> Dict:
        """Analyze distribution of numbers in a prize field."""
        if draws is None:
            draws = self.draws

        numbers = self.extract_numbers(field, draws)
        if not numbers:
            return {"error": f"No data for {field}"}

        counter = Counter(numbers)
        total = len(numbers)

        return {
            "field": field,
            "total_numbers": total,
            "unique_numbers": len(counter),
            "most_common": counter.most_common(5),
            "least_common": counter.most_common()[-5:],
            "distribution_evenness": self.calculate_chi_square(counter, total),
        }

    def calculate_chi_square(self, counter: Counter, total: int) -> float:
        """Calculate chi-square statistic for distribution uniformity.

        Higher value = more uneven distribution.
        For uniform distribution: chi_square ≈ 0
        """
        if not counter:
            return 0.0

        expected = total / len(counter)
        chi_square = sum((count - expected) ** 2 / expected for count in counter.values())
        return chi_square

    def get_hot_cold_numbers(self, field: str, top_n: int = 10) -> Dict:
        """Get hot (most frequent) and cold (least frequent) numbers."""
        numbers = self.extract_numbers(field)
        if not numbers:
            return {}

        counter = Counter(numbers)
        total = len(numbers)

        hot = counter.most_common(top_n)
        cold = counter.most_common()[-top_n:]

        return {
            "field": field,
            "hot_numbers": [(num, count, f"{count/total*100:.1f}%") for num, count in hot],
            "cold_numbers": [(num, count, f"{count/total*100:.1f}%") for num, count in cold],
            "total_appearances": total,
        }

    def analyze_temporal_patterns(self) -> Dict:
        """Analyze patterns over time (by year, month, season)."""
        draws_by_year = defaultdict(int)
        draws_by_month = defaultdict(int)
        draws_by_season = defaultdict(int)

        for draw in self.draws:
            date = datetime.datetime.strptime(draw["date"], "%Y-%m-%d").date()
            year = date.year
            month = date.month

            draws_by_year[year] += 1
            draws_by_month[f"{year}-{month:02d}"] += 1

            # Thai seasons (simplified)
            if month in [4, 5]:
                season = "Hot/Songkran"
            elif month in [6, 7, 8, 9, 10]:
                season = "Rainy"
            else:
                season = "Cool"
            draws_by_season[season] += 1

        return {
            "draws_by_year": dict(sorted(draws_by_year.items())),
            "draws_by_season": dict(draws_by_season),
            "draws_per_month": dict(sorted(draws_by_month.items())),
        }

    def analyze_holiday_correlation(self) -> Dict:
        """Analyze if draws near holidays show patterns."""
        holiday_draws = []
        regular_draws = []
        cultural_draws = []

        for draw in self.draws:
            date = datetime.datetime.strptime(draw["date"], "%Y-%m-%d").date()

            if is_holiday(date):
                holiday_draws.append(draw)
            elif is_cultural_significance(date):
                cultural_draws.append(draw)
            else:
                regular_draws.append(draw)

        return {
            "holiday_draws": len(holiday_draws),
            "cultural_draws": len(cultural_draws),
            "regular_draws": len(regular_draws),
            "holiday_sample": holiday_draws[:3] if holiday_draws else [],
            "holiday_percentage": f"{len(holiday_draws)/len(self.draws)*100:.1f}%" if self.draws else "N/A",
        }

    def generate_report(self, include_3year: bool = True) -> str:
        """Generate comprehensive analysis report."""
        report = "\n" + "=" * 80 + "\n"
        report += "THAI LOTTERY DATA DEEP ANALYSIS\n"
        report += "=" * 80 + "\n\n"

        # Basic stats
        start_date, end_date = self.get_date_range()
        report += f"📊 DATA OVERVIEW\n"
        report += f"Total draws: {len(self.draws)}\n"
        report += f"Date range: {start_date} to {end_date}\n"
        report += f"Years covered: {end_date.year - start_date.year + 1}\n\n"

        if include_3year:
            data_3yr = self.get_3year_data()
            report += f"3-Year Analysis (2023-2026): {len(data_3yr)} draws\n\n"

            # Distribution analysis
            report += "📈 DISTRIBUTION ANALYSIS (Last 3 Years)\n"
            for field in ["first", "second", "last2"]:
                dist = self.analyze_distribution(field, data_3yr)
                if "error" not in dist:
                    report += f"\n{field.upper()}:\n"
                    report += f"  Unique numbers: {dist['unique_numbers']}\n"
                    report += f"  Total appearances: {dist['total_numbers']}\n"
                    report += f"  Distribution evenness: {dist['distribution_evenness']:.1f}\n"
                    report += f"  Most common: {dist['most_common'][0] if dist['most_common'] else 'N/A'}\n"

            # Hot/Cold numbers
            report += "\n🔥 HOT/COLD NUMBERS (Last 3 Years)\n"
            hot_cold = self.get_hot_cold_numbers("first", top_n=5)
            if hot_cold:
                report += f"\nFirst Prize - Hot Numbers:\n"
                for num, count, pct in hot_cold["hot_numbers"][:3]:
                    report += f"  {num}: {count} times ({pct})\n"
                report += f"\nFirst Prize - Cold Numbers:\n"
                for num, count, pct in hot_cold["cold_numbers"][:3]:
                    report += f"  {num}: {count} times ({pct})\n"

        # Temporal patterns
        report += "\n⏰ TEMPORAL PATTERNS\n"
        temporal = self.analyze_temporal_patterns()
        report += f"Draws per year (recent): {temporal['draws_by_year']}\n"
        report += f"Seasonal distribution: {temporal['draws_by_season']}\n"

        # Holiday correlation
        report += "\n🎉 HOLIDAY CORRELATION\n"
        holidays = self.analyze_holiday_correlation()
        report += f"Draws on holidays: {holidays['holiday_draws']}\n"
        report += f"Draws on cultural dates: {holidays['cultural_draws']}\n"
        report += f"Regular draws: {holidays['regular_draws']}\n"

        report += "\n" + "=" * 80 + "\n"
        return report

    def export_summary(self, output_file: str = "lottery_analysis_summary.txt"):
        """Export analysis to file."""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(self.generate_report())
        print(f"✅ Analysis exported to {output_file}")


if __name__ == "__main__":
    analysis = LotteryDataAnalysis()
    print(analysis.generate_report())

    # Export summary
    analysis.export_summary()

    # Detailed analysis
    print("\n" + "=" * 80)
    print("DETAILED PRIZE ANALYSIS")
    print("=" * 80)

    data_3yr = analysis.get_3year_data()
    for field in ["first", "second", "third"]:
        dist = analysis.analyze_distribution(field, data_3yr)
        if "error" not in dist:
            print(f"\n{field.upper()} Prize Distribution:")
            print(f"  Chi-Square: {dist['distribution_evenness']:.2f} (lower = more even)")
            print(f"  Unique numbers: {dist['unique_numbers']}")
