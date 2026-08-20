"""
Generate comprehensive HTML report combining Thai context and data analysis.
"""

import csv
import datetime
from pathlib import Path
from data_analysis import LotteryDataAnalysis
from thai_context import (
    describe_year,
    get_events_for_year,
    get_event_context,
    THAI_CONTEXT_SUMMARY,
)


def generate_html_report():
    """Generate comprehensive HTML analysis report."""
    analysis = LotteryDataAnalysis()
    start_date, end_date = analysis.get_date_range()

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thai Lottery Data Analysis Report</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; border-radius: 8px; margin-bottom: 30px; text-align: center; }
            h1 { font-size: 2.5em; margin-bottom: 10px; }
            .subtitle { font-size: 1.1em; opacity: 0.9; }
            .section { background: white; padding: 30px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .section h2 { color: #667eea; font-size: 1.8em; margin-bottom: 20px; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
            .section h3 { color: #764ba2; font-size: 1.3em; margin-top: 20px; margin-bottom: 15px; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; }
            .stat-label { font-size: 0.9em; opacity: 0.9; margin-top: 5px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th { background: #f0f0f0; padding: 12px; text-align: left; font-weight: bold; border-bottom: 2px solid #667eea; }
            td { padding: 12px; border-bottom: 1px solid #ddd; }
            tr:hover { background: #f9f9f9; }
            .highlight { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0; border-radius: 4px; }
            .thai-event { background: #e3f2fd; padding: 12px; margin: 10px 0; border-left: 4px solid #2196f3; border-radius: 4px; }
            .number-freq { display: flex; align-items: center; margin: 8px 0; }
            .number-bar { background: #667eea; height: 20px; border-radius: 3px; margin: 0 10px; min-width: 5px; }
            .footer { text-align: center; color: #666; margin-top: 30px; padding: 20px; border-top: 1px solid #ddd; }
            .chart { margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🎰 Thai Lottery Data Analysis</h1>
                <p class="subtitle">Comprehensive Statistical Analysis & Cultural Context (2010-2026)</p>
            </header>
    """

    # Overview Section
    html += f"""
            <div class="section">
                <h2>📊 Data Overview</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{len(analysis.draws)}</div>
                        <div class="stat-label">Total Draws</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{start_date}</div>
                        <div class="stat-label">Start Date</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{end_date}</div>
                        <div class="stat-label">Latest Draw</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(analysis.get_3year_data())}</div>
                        <div class="stat-label">3-Year Draws</div>
                    </div>
                </div>
            </div>
    """

    # Thai Cultural Context
    html += """
            <div class="section">
                <h2>🏛️ Thai Cultural Context</h2>
    """

    html += f"""
                <div class="highlight">
                    {THAI_CONTEXT_SUMMARY.replace(chr(10), '<br>')}
                </div>
    """

    # Recent Years Events
    for year in [2024, 2025, 2026]:
        events = get_events_for_year(year)
        if events:
            html += f"<h3>{year} Major Events ({len(events)} events)</h3>"
            for date, name, category in events[:10]:  # Show first 10
                html += f'<div class="thai-event"><strong>{date.strftime("%b %d")}</strong>: {name} <em>({category})</em></div>'
            if len(events) > 10:
                html += f'<p style="margin-top: 10px; color: #666;">... and {len(events) - 10} more events</p>'

    html += """
            </div>
    """

    # Distribution Analysis
    html += """
            <div class="section">
                <h2>📈 Statistical Analysis (Last 3 Years)</h2>
    """

    data_3yr = analysis.get_3year_data()

    for field in ["first", "second", "third"]:
        dist = analysis.analyze_distribution(field, data_3yr)
        if "error" not in dist:
            html += f"""
                <h3>{field.upper()} Prize</h3>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Unique Numbers</td>
                        <td><strong>{dist['unique_numbers']}</strong></td>
                    </tr>
                    <tr>
                        <td>Total Appearances</td>
                        <td><strong>{dist['total_numbers']}</strong></td>
                    </tr>
                    <tr>
                        <td>Distribution Evenness (Chi-Square)</td>
                        <td><strong>{dist['distribution_evenness']:.2f}</strong> (lower = more even)</td>
                    </tr>
                    <tr>
                        <td>Most Common</td>
                        <td><strong>{dist['most_common'][0][0]}</strong> ({dist['most_common'][0][1]} times)</td>
                    </tr>
                </table>
            """

    html += """
            </div>
    """

    # Hot/Cold Numbers
    html += """
            <div class="section">
                <h2>🔥 Hot & Cold Numbers (Last 3 Years)</h2>
    """

    hot_cold = analysis.get_hot_cold_numbers("first", top_n=10)
    if hot_cold:
        html += """
                <h3>First Prize - Hot Numbers (Most Frequent)</h3>
                <table>
                    <tr>
                        <th>Number</th>
                        <th>Frequency</th>
                        <th>Percentage</th>
                    </tr>
        """
        for num, count, pct in hot_cold["hot_numbers"][:5]:
            html += f"""
                    <tr>
                        <td>{num}</td>
                        <td>{count}</td>
                        <td>{pct}</td>
                    </tr>
            """
        html += """
                </table>

                <h3>First Prize - Cold Numbers (Least Frequent)</h3>
                <table>
                    <tr>
                        <th>Number</th>
                        <th>Frequency</th>
                        <th>Percentage</th>
                    </tr>
        """
        for num, count, pct in hot_cold["cold_numbers"][:5]:
            html += f"""
                    <tr>
                        <td>{num}</td>
                        <td>{count}</td>
                        <td>{pct}</td>
                    </tr>
            """
        html += """
                </table>
            </div>
        """

    # Temporal Patterns
    html += """
            <div class="section">
                <h2>⏰ Temporal Patterns</h2>
    """

    temporal = analysis.analyze_temporal_patterns()

    html += """
                <h3>Draws by Season</h3>
                <table>
                    <tr>
                        <th>Season</th>
                        <th>Draws</th>
                    </tr>
    """
    for season, count in sorted(temporal["draws_by_season"].items()):
        html += f"""
                    <tr>
                        <td>{season}</td>
                        <td><strong>{count}</strong></td>
                    </tr>
        """
    html += """
                </table>

                <h3>Draws by Year (Recent)</h3>
                <table>
                    <tr>
                        <th>Year</th>
                        <th>Draws</th>
                    </tr>
    """
    for year, count in sorted(temporal["draws_by_year"].items())[-5:]:
        html += f"""
                    <tr>
                        <td>{year}</td>
                        <td><strong>{count}</strong></td>
                    </tr>
        """
    html += """
                </table>
            </div>
    """

    # Holiday Correlation
    html += """
            <div class="section">
                <h2>🎉 Holiday Correlation</h2>
    """

    holidays = analysis.analyze_holiday_correlation()
    html += f"""
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{holidays['holiday_draws']}</div>
                        <div class="stat-label">Draws on Holidays</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{holidays['cultural_draws']}</div>
                        <div class="stat-label">Cultural Significance Days</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{holidays['regular_draws']}</div>
                        <div class="stat-label">Regular Days</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{holidays['holiday_percentage']}</div>
                        <div class="stat-label">% on Holidays</div>
                    </div>
                </div>
            </div>
    """

    # Footer
    html += f"""
            <div class="footer">
                <p>📊 Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Data source: lottery_results.csv ({len(analysis.draws)} draws, {start_date} to {end_date})</p>
                <p>Analysis includes Thai cultural context, statistical distribution analysis, and temporal patterns</p>
            </div>

        </div>
    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    html = generate_html_report()

    output_file = "lottery_analysis_report.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Report generated: {output_file}")

    # Also generate text summary
    analysis = LotteryDataAnalysis()
    print(analysis.generate_report())
