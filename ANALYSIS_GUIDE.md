# Thai Lottery Data Analysis Guide

## 🎯 Overview

This guide explains how to use the deep data analysis tools for understanding Thai lottery patterns with cultural context.

## 📊 Available Analysis Tools

### 1. Thai Context Integration (`thai_context.py`)

Thai holidays, cultural events, and news correlations.

**Key Features:**
- Thai public holidays (12+ major holidays)
- Buddhist celebrations (Makha Bucha, Visakha Bucha, etc.)
- Royal ceremonies (King's birthday, Chakri Day)
- Songkran festival (April 13-15) - Major event
- Political events (elections, government formation)
- Cultural significance dates

**Usage:**
```python
from thai_context import get_event_context, get_events_for_year

# Get context for a specific date
context = get_event_context(datetime.date(2024, 4, 13))
print(context)  # "Holiday: Songkran Festival | Cultural: Water festival..."

# Get all events for a year
events_2024 = get_events_for_year(2024)
```

### 2. Statistical Analysis (`data_analysis.py`)

Comprehensive statistical analysis of lottery draw data.

**Key Features:**
- Distribution analysis (chi-square testing)
- Hot/cold number identification
- Temporal patterns (yearly, seasonal, monthly)
- Holiday correlation analysis
- 3-year focused deep dive
- Statistical metrics

**Usage:**
```python
from data_analysis import LotteryDataAnalysis

# Initialize analysis
analysis = LotteryDataAnalysis()

# Generate full report
print(analysis.generate_report())

# Get 3-year data
data_3yr = analysis.get_3year_data()

# Analyze distribution
dist = analysis.analyze_distribution("first", data_3yr)

# Get hot/cold numbers
hot_cold = analysis.get_hot_cold_numbers("first", top_n=10)

# Export summary
analysis.export_summary("summary.txt")
```

### 3. HTML Report Generation (`generate_analysis_report.py`)

Beautiful HTML report combining all analysis.

**Usage:**
```bash
python generate_analysis_report.py
# Generates: lottery_analysis_report.html
```

**Report Includes:**
- Data overview (360+ draws, 16 years)
- Distribution analysis
- Hot/cold number rankings
- Temporal patterns
- Holiday correlations
- Thai cultural context

## 🏛️ Thai Cultural Context Details

### Major Holidays & Impact

**Songkran (April 13-15)**
- Thai New Year celebration
- Water festival, national holiday
- Travel season peak
- High lottery participation
- Impact: Draws may be rescheduled

**Buddhist Holidays**
- Makha Bucha (Feb 26): Temple visits, merit-making
- Visakha Bucha (May): Major celebration
- Asahna Bucha (July): Buddhist Lent begins
- Impact: Spiritual activities, reduced traveling

**Royal Celebrations**
- King's Birthday (Oct 13): National day
- Chakri Day (April 6): Dynasty founding
- King Chulalongkorn Day (Oct 23): Respect day
- Impact: National pride, celebrations

**Seasonal Patterns**
- Cool season (Nov-Feb): Festivals, travel
- Hot season (Mar-May): Songkran, summer
- Rainy season (Jun-Oct): Buddhist Lent, monsoon

## 📈 Statistical Insights

### Distribution Analysis

**Chi-Square Metric:**
- Lower value = more even distribution
- Higher value = uneven (some numbers appear more)
- Helps identify if certain numbers are favored

**Example Output:**
```
FIRST Prize Distribution:
  Chi-Square: 42.5 (slightly uneven)
  Unique numbers: 850+
  Total appearances: 1,500+
  Most common: 123456 (5 times, 0.3%)
```

### Hot/Cold Numbers

**Hot Numbers** (Most Frequent)
- Appear more frequently than average
- May indicate genuine patterns or coincidence
- Use for reference, not prediction

**Cold Numbers** (Least Frequent)
- Haven't appeared recently
- Could be "due" to appear (gambler's fallacy)
- Equal probability in fair lottery

**Example:**
```
FIRST Prize Hot Numbers:
  100001: 6 times (0.4%)
  200002: 5 times (0.3%)
  300003: 5 times (0.3%)

FIRST Prize Cold Numbers:
  999999: 0 times (0.0%)
  888888: 1 time (0.1%)
```

## 📊 Temporal Patterns

### Seasonal Analysis

**Distribution by Season:**
- Hot/Songkran (Apr-May): Peak activities
- Rainy (Jun-Oct): Festival period (Buddhist Lent)
- Cool (Nov-Mar): Year-end holidays

### Yearly Analysis

**Draws per Year:**
- Expected: ~24 draws per year (2 per month)
- Actual: Varies due to holiday shifts
- 2024-2026: 20-24 draws per year

## 🎯 How to Use for Number Generation

### Data-Driven Generator

Use analysis to improve random number generation:

```python
from data_analysis import LotteryDataAnalysis

analysis = LotteryDataAnalysis()

# Get distribution of past numbers
dist = analysis.analyze_distribution("first")

# For fair generation: Use uniform distribution
# For "realistic" generation: Weight numbers by historical frequency

# Example: Generate numbers matching historical distribution
import random
hot_cold = analysis.get_hot_cold_numbers("first", top_n=100)
hot_numbers = [num for num, count, pct in hot_cold["hot_numbers"]]

# 50% from hot numbers, 50% random
if random.random() < 0.5:
    generated = random.choice(hot_numbers)
else:
    generated = str(random.randint(0, 999999)).zfill(6)
```

## 💡 Key Insights from Analysis

### What the Data Shows

1. **No Single Pattern**: Lottery draws appear random with no consistent pattern
2. **Fair Distribution**: Numbers generally appear with similar frequency
3. **Holiday Effects**: Draw dates may shift due to Thai holidays
4. **Seasonal Peaks**: Interest peaks during Songkran and year-end
5. **No Prediction**: Past results don't predict future draws

### Best Practices

✅ **Do:**
- Use analysis for understanding patterns
- Recognize Thai cultural calendar effects
- See historical trends (informational)
- Use for data validation/integrity

❌ **Don't:**
- Try to predict future draws
- Rely solely on "hot" numbers
- Assume patterns will continue
- Use old data for new predictions

## 📈 Running Analysis

### Basic Report
```bash
python data_analysis.py
```

### Generate HTML Report
```bash
python generate_analysis_report.py
```

### Custom Analysis
```python
from data_analysis import LotteryDataAnalysis
from thai_context import get_event_context

analysis = LotteryDataAnalysis()

# Get last 3 years
data_3yr = analysis.get_3year_data()

# Analyze specific prize
dist = analysis.analyze_distribution("second", data_3yr)
print(f"Second prize distribution: {dist}")

# Check Thai context for a specific date
import datetime
date = datetime.date(2024, 4, 13)
print(f"Context: {get_event_context(date)}")
```

## 📊 Data Quality Checks

All analysis files include data validation:

```python
# Schema validation
validate_csv_schema("lottery_results.csv")

# Integrity validation
validate_csv_integrity("lottery_results.csv")

# Distribution checks
analysis.analyze_distribution("first")
```

## 🚀 Future Enhancements

Potential improvements:
- [ ] Machine learning models for pattern detection
- [ ] API integration with Thai holiday sources
- [ ] Real-time news correlation
- [ ] Predictive modeling (for research)
- [ ] Interactive dashboard
- [ ] Export to multiple formats (JSON, CSV)

## 📚 Reference

**Files Involved:**
- `thai_context.py`: Cultural context and events
- `data_analysis.py`: Statistical analysis
- `generate_analysis_report.py`: Report generation
- `lottery_results.csv`: Raw data (360+ draws)
- `lottery_results_looker_ready.csv`: Transformed data

**Data Range:**
- Start: March 1, 2010
- End: August 16, 2026 (latest)
- Total: 350+ draws across 16 years
- Focus: 2023-2026 (60+ draws)

## ⚖️ Disclaimer

This analysis is for informational and research purposes only. Thai lottery draws are random events. Past patterns do not predict future results. Use this data responsibly.

---

**Last Updated**: August 2026  
**Data Coverage**: 2010-2026 (16 years)  
**Focus Period**: 2023-2026 (3 years)
