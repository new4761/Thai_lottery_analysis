"""
Simple API server for serving lottery data to the web generator.

Can be deployed to:
- Heroku
- Railway
- Render
- AWS Lambda
- Google Cloud Functions
- Or your own server

Usage:
    python api_server.py

Then access:
    http://localhost:5000/api/history - Get historical data
    http://localhost:5000/api/stats - Get statistics
    http://localhost:5000/health - Health check
"""

from flask import Flask, jsonify, CORS
from flask_caching import Cache
from data_analysis import LotteryDataAnalysis
from thai_context import get_event_context, is_holiday
import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Configure caching (cache for 1 hour)
cache_config = {'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 3600}
cache = Cache(app, config=cache_config)

# Initialize analysis (lazy load)
_analysis = None

def get_analysis():
    """Lazy load analysis."""
    global _analysis
    if _analysis is None:
        _analysis = LotteryDataAnalysis()
    return _analysis


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Thai Lottery API running'})


@app.route('/api/info', methods=['GET'])
@cache.cached()
def api_info():
    """Get generator info and data overview."""
    analysis = get_analysis()
    start_date, end_date = analysis.get_date_range()

    return jsonify({
        'generator': {
            'modes': {
                'pure_random': {
                    'name': 'Pure Random',
                    'description': 'Cryptographically secure, completely random',
                },
                'data_driven': {
                    'name': 'Data-Driven',
                    'description': 'Weighted by 3+ years of historical patterns',
                },
                'thai_aware': {
                    'name': 'Thai-Aware',
                    'description': 'Considers Thai holidays and cultural luck',
                },
            }
        },
        'data': {
            'total_draws': len(analysis.draws),
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'years_covered': end_date.year - start_date.year + 1 if start_date and end_date else 0,
        }
    })


@app.route('/api/history', methods=['GET'])
@cache.cached()
def api_history():
    """Get hot/cold numbers from historical data."""
    analysis = get_analysis()
    data_3yr = analysis.get_3year_data()

    historical_data = {}

    for field in ['first', 'second', 'third', 'fourth', 'fifth', 'last2', 'last3f', 'last3b', 'near1']:
        hot_cold = analysis.get_hot_cold_numbers(field, top_n=20)

        if hot_cold:
            historical_data[field] = {
                'hot': [num for num, count, pct in hot_cold['hot_numbers']],
                'cold': [num for num, count, pct in hot_cold['cold_numbers']],
                'total_appearances': hot_cold['total_appearances'],
            }

    return jsonify({
        'status': 'success',
        'data': historical_data,
        'period': '3-year (2023-2026)',
        'cache_seconds': 3600,
    })


@app.route('/api/stats', methods=['GET'])
@cache.cached()
def api_stats():
    """Get statistical analysis."""
    analysis = get_analysis()
    data_3yr = analysis.get_3year_data()

    stats = {}

    for field in ['first', 'second', 'last2']:
        dist = analysis.analyze_distribution(field, data_3yr)

        if 'error' not in dist:
            stats[field] = {
                'unique_numbers': dist['unique_numbers'],
                'total_appearances': dist['total_numbers'],
                'distribution_evenness': dist['distribution_evenness'],
                'most_common': {
                    'number': dist['most_common'][0][0],
                    'count': dist['most_common'][0][1],
                } if dist['most_common'] else None,
            }

    temporal = analysis.analyze_temporal_patterns()
    holidays = analysis.analyze_holiday_correlation()

    return jsonify({
        'status': 'success',
        'prize_analysis': stats,
        'temporal': {
            'draws_by_season': temporal['draws_by_season'],
        },
        'holidays': {
            'draws_on_holidays': holidays['holiday_draws'],
            'draws_on_cultural_dates': holidays['cultural_draws'],
            'regular_draws': holidays['regular_draws'],
        }
    })


@app.route('/api/today', methods=['GET'])
def api_today():
    """Get today's context."""
    today = datetime.date.today()
    context = get_event_context(today)
    is_auspicious = is_holiday(today)

    return jsonify({
        'date': today.isoformat(),
        'context': context,
        'is_auspicious': is_auspicious,
        'day_name': today.strftime('%A'),
    })


@app.route('/api/generate', methods=['GET'])
def api_generate():
    """Generate numbers (read-only, for testing)."""
    from lottery_generator import LotteryGenerator

    mode = request.args.get('mode', 'pure').lower()

    if mode not in ['pure', 'driven', 'thai']:
        return jsonify({'error': 'Invalid mode'}), 400

    gen = LotteryGenerator()

    if mode == 'driven':
        numbers = gen.generate_data_driven()
    elif mode == 'thai':
        numbers = gen.generate_thai_aware()
    else:
        numbers = gen.generate_pure_random()

    return jsonify({
        'status': 'success',
        'mode': mode,
        'numbers': numbers,
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Available endpoints: /health, /api/info, /api/history, /api/stats, /api/today, /api/generate'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500


if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
