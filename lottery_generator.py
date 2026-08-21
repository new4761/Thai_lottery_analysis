"""
Enhanced Thai Lottery Number Generator.

Generates random lottery numbers with multiple modes:
1. Pure Random - Cryptographically secure randomness
2. Data-Driven - Weighted by historical patterns
3. Thai-Aware - Considers cultural luck and timing
"""

import random
import secrets
import datetime
from typing import List, Dict, Tuple
from data_analysis import LotteryDataAnalysis
from thai_context import get_event_context, is_holiday


class LotteryGenerator:
    """Generate Thai lottery numbers with multiple strategies."""

    def __init__(self):
        """Initialize generator with historical data."""
        self.analysis = LotteryDataAnalysis()
        self.hot_cold_data = {}
        self._load_historical_patterns()

    def _load_historical_patterns(self):
        """Load hot/cold patterns from historical data."""
        data_3yr = self.analysis.get_3year_data()
        for field in ["first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]:
            self.hot_cold_data[field] = self.analysis.get_hot_cold_numbers(field, top_n=20)

    def generate_pure_random(self) -> Dict[str, str]:
        """Generate purely random numbers (cryptographically secure).

        Uses secrets module for high-quality randomness.
        Best for: Fair, unbiased generation.
        """
        return {
            "first": self._generate_6digit(),
            "second": self._generate_multiple_6digit(5),
            "third": self._generate_multiple_6digit(10),
            "fourth": self._generate_multiple_6digit(25),
            "fifth": self._generate_multiple_6digit(100),
            "last2": self._generate_2digit(),
            "last3f": self._generate_3digit(),
            "last3b": self._generate_3digit(),
            "near1": self._generate_6digit(),
        }

    def generate_data_driven(self) -> Dict[str, str]:
        """Generate numbers weighted by historical patterns.

        Gives slight preference to historically frequent numbers.
        Best for: Realistic patterns matching historical distribution.
        """
        return {
            "first": self._generate_weighted_6digit("first"),
            "second": self._generate_weighted_multiple(5, "second"),
            "third": self._generate_weighted_multiple(10, "third"),
            "fourth": self._generate_weighted_multiple(25, "fourth"),
            "fifth": self._generate_weighted_multiple(100, "fifth"),
            "last2": self._generate_weighted_2digit("last2"),
            "last3f": self._generate_weighted_3digit("last3f"),
            "last3b": self._generate_weighted_3digit("last3b"),
            "near1": self._generate_weighted_6digit("near1"),
        }

    def generate_thai_aware(self) -> Dict[str, str]:
        """Generate numbers with Thai cultural awareness.

        Considers auspicious numbers and current Thai context.
        Best for: Culturally meaningful generation.
        """
        today = datetime.date.today()
        context = get_event_context(today)
        is_auspicious_day = is_holiday(today)

        # Generate based on context
        if is_auspicious_day:
            # Use mix of hot numbers and lucky sequences on auspicious days
            return {
                "first": self._generate_lucky_or_hot("first"),
                "second": self._generate_lucky_multiple(5, "second"),
                "third": self._generate_lucky_multiple(10, "third"),
                "fourth": self._generate_lucky_multiple(25, "fourth"),
                "fifth": self._generate_lucky_multiple(100, "fifth"),
                "last2": self._generate_lucky_2digit("last2"),
                "last3f": self._generate_lucky_3digit("last3f"),
                "last3b": self._generate_lucky_3digit("last3b"),
                "near1": self._generate_lucky_or_hot("near1"),
            }
        else:
            # Regular data-driven on normal days
            return self.generate_data_driven()

    # Helper methods for number generation

    def _generate_6digit(self) -> str:
        """Generate random 6-digit number."""
        return str(secrets.randbelow(1000000)).zfill(6)

    def _generate_2digit(self) -> str:
        """Generate random 2-digit number."""
        return str(secrets.randbelow(100)).zfill(2)

    def _generate_3digit(self) -> str:
        """Generate random 3-digit number."""
        return str(secrets.randbelow(1000)).zfill(3)

    def _generate_multiple_6digit(self, count: int) -> str:
        """Generate multiple random 6-digit numbers."""
        numbers = [self._generate_6digit() for _ in range(count)]
        return ",".join(numbers)

    def _generate_weighted_6digit(self, field: str) -> str:
        """Generate 6-digit number weighted by historical frequency."""
        if field not in self.hot_cold_data or not self.hot_cold_data[field].get("hot_numbers"):
            return self._generate_6digit()

        hot_numbers = self.hot_cold_data[field]["hot_numbers"]
        # 40% from hot numbers, 60% random
        if random.random() < 0.4:
            num, _, _ = random.choice(hot_numbers[:10])
            return num
        return self._generate_6digit()

    def _generate_weighted_multiple(self, count: int, field: str) -> str:
        """Generate multiple weighted numbers."""
        numbers = [self._generate_weighted_6digit(field) for _ in range(count)]
        # Remove duplicates if any
        numbers = list(dict.fromkeys(numbers))
        # Add more if needed
        while len(numbers) < count:
            numbers.append(self._generate_6digit())
        return ",".join(numbers[:count])

    def _generate_weighted_2digit(self, field: str) -> str:
        """Generate weighted 2-digit number."""
        if field not in self.hot_cold_data or not self.hot_cold_data[field].get("hot_numbers"):
            return self._generate_2digit()

        if random.random() < 0.3:
            num, _, _ = random.choice(self.hot_cold_data[field]["hot_numbers"][:5])
            return num[-2:] if len(num) > 2 else num.zfill(2)
        return self._generate_2digit()

    def _generate_weighted_3digit(self, field: str) -> str:
        """Generate weighted 3-digit number."""
        if field not in self.hot_cold_data or not self.hot_cold_data[field].get("hot_numbers"):
            return self._generate_3digit()

        if random.random() < 0.3:
            num, _, _ = random.choice(self.hot_cold_data[field]["hot_numbers"][:5])
            return num[-3:] if len(num) > 3 else num.zfill(3)
        return self._generate_3digit()

    def _generate_lucky_or_hot(self, field: str) -> str:
        """Generate lucky or hot number."""
        lucky = self._get_lucky_number()
        if lucky and random.random() < 0.5:
            return lucky
        return self._generate_weighted_6digit(field)

    def _generate_lucky_multiple(self, count: int, field: str) -> str:
        """Generate multiple lucky/hot numbers."""
        numbers = []
        for _ in range(count):
            if random.random() < 0.3:
                lucky = self._get_lucky_number()
                if lucky:
                    numbers.append(lucky)
                    continue
            numbers.append(self._generate_weighted_6digit(field))

        # Remove duplicates
        numbers = list(dict.fromkeys(numbers))
        while len(numbers) < count:
            numbers.append(self._generate_6digit())
        return ",".join(numbers[:count])

    def _generate_lucky_2digit(self, field: str) -> str:
        """Generate lucky 2-digit number."""
        if random.random() < 0.3:
            lucky = self._get_lucky_number()
            if lucky:
                return lucky[-2:] if len(lucky) > 2 else lucky.zfill(2)
        return self._generate_weighted_2digit(field)

    def _generate_lucky_3digit(self, field: str) -> str:
        """Generate lucky 3-digit number."""
        if random.random() < 0.3:
            lucky = self._get_lucky_number()
            if lucky:
                return lucky[-3:] if len(lucky) > 3 else lucky.zfill(3)
        return self._generate_weighted_3digit(field)

    def _get_lucky_number(self) -> str:
        """Get a lucky number based on Thai beliefs."""
        lucky_sequences = [
            "888888",  # 8 = prosperity (ป)
            "666666",  # 6 = smooth (ลื่น)
            "777777",  # 7 = lucky
            "999999",  # 9 = long lasting (ยาวนาน)
            "123456",  # Sequential luck
            "111111",  # Unity, oneness
            "555555",  # 5 = wealth in some contexts
        ]
        return random.choice(lucky_sequences) if random.random() < 0.15 else None

    def get_generator_info(self) -> Dict:
        """Get information about generator modes."""
        return {
            "modes": {
                "pure_random": {
                    "description": "Cryptographically secure, completely random",
                    "best_for": "Fair, unbiased generation",
                    "bias": "None",
                },
                "data_driven": {
                    "description": "Weighted by 3+ years of historical data",
                    "best_for": "Realistic patterns matching actual distribution",
                    "bias": "Slight preference for historically frequent numbers (40%)",
                },
                "thai_aware": {
                    "description": "Considers Thai holidays and cultural luck",
                    "best_for": "Culturally meaningful generation",
                    "bias": "Auspicious days use lucky sequences (15%)",
                },
            },
            "historical_data": {
                "total_draws": len(self.analysis.draws),
                "date_range": f"{self.analysis.get_date_range()[0]} to {self.analysis.get_date_range()[1]}",
                "focus_period": "2023-2026 (60+ draws)",
            },
        }


def generate_set(mode: str = "pure_random") -> Dict[str, str]:
    """Quick generate function for single set of numbers.

    Args:
        mode: "pure_random", "data_driven", or "thai_aware"

    Returns:
        Dictionary with prize numbers
    """
    generator = LotteryGenerator()

    if mode == "data_driven":
        return generator.generate_data_driven()
    elif mode == "thai_aware":
        return generator.generate_thai_aware()
    else:
        return generator.generate_pure_random()


if __name__ == "__main__":
    generator = LotteryGenerator()

    print("🎰 Thai Lottery Number Generator\n")
    print("=" * 60)

    # Show generator info
    info = generator.get_generator_info()
    print("\nAvailable Modes:")
    for mode, details in info["modes"].items():
        print(f"\n{mode.upper()}")
        print(f"  Description: {details['description']}")
        print(f"  Best for: {details['best_for']}")

    # Generate examples
    print("\n" + "=" * 60)
    print("\nExample Generations:\n")

    print("1. PURE RANDOM (Fair, no bias):")
    pure = generator.generate_pure_random()
    print(f"   First: {pure['first']}")
    print(f"   Last 2: {pure['last2']}")

    print("\n2. DATA-DRIVEN (Based on 3+ years):")
    driven = generator.generate_data_driven()
    print(f"   First: {driven['first']}")
    print(f"   Last 2: {driven['last2']}")

    print("\n3. THAI-AWARE (Culturally conscious):")
    thai = generator.generate_thai_aware()
    print(f"   First: {thai['first']}")
    print(f"   Last 2: {thai['last2']}")

    print("\n" + "=" * 60)
    print("Historical Data:")
    for key, value in info["historical_data"].items():
        print(f"  {key}: {value}")
