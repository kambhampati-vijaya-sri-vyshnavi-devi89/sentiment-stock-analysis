import math
import random
from datetime import datetime, timedelta

random.seed(42)

SECTORS = {
    "tech": {
        "label": "Technology",
        "stocks": ["AAPL", "MSFT", "GOOGL"],
        "base_price": 180,
        "volatility": 0.022,
        "sentiment_lag": 2,
        "color": "#7c6af7",
        "correlation": 0.71,
    },
    "pharma": {
        "label": "Pharmaceuticals",
        "stocks": ["PFE", "JNJ", "MRNA"],
        "base_price": 95,
        "volatility": 0.018,
        "sentiment_lag": 1,
        "color": "#22d3ee",
        "correlation": 0.58,
    },
    "energy": {
        "label": "Energy",
        "stocks": ["XOM", "CVX", "BP"],
        "base_price": 115,
        "volatility": 0.025,
        "sentiment_lag": 3,
        "color": "#f59e0b",
        "correlation": 0.63,
    },
}

def date_range(days=90):
    start = datetime(2024, 1, 1)
    return [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]

def generate_sentiment_series(days=90, base=0.0, noise=0.3, events=None):
    """Generate daily sentiment score (-1 to +1)."""
    series = []
    val = base
    for i in range(days):
        shock = 0
        if events:
            for ev_day, magnitude in events:
                if abs(i - ev_day) < 3:
                    shock += magnitude * math.exp(-0.5 * abs(i - ev_day))
        val = val * 0.85 + base * 0.15 + random.gauss(0, noise) + shock
        val = max(-1.0, min(1.0, val))
        series.append(round(val, 4))
    return series

def generate_volatility_series(sentiment, lag=2, base_vol=0.02, noise=0.005):
    """Volatility influenced by sentiment with a lag (research-realistic)."""
    n = len(sentiment)
    vol = []
    for i in range(n):
        lag_sent = sentiment[max(0, i - lag)]
        # Negative sentiment → higher volatility
        driven = base_vol + abs(lag_sent) * 0.015 - lag_sent * 0.008
        driven += random.gauss(0, noise)
        driven = max(0.005, min(0.06, driven))
        vol.append(round(driven, 5))
    return vol

def generate_price_series(volatility, base_price=100):
    prices = [base_price]
    for i in range(1, len(volatility)):
        ret = random.gauss(0.0003, volatility[i])
        prices.append(round(prices[-1] * (1 + ret), 2))
    return prices

def compute_rolling_correlation(s1, s2, window=7):
    result = [None] * (window - 1)
    for i in range(window - 1, len(s1)):
        a = s1[i - window + 1:i + 1]
        b = s2[i - window + 1:i + 1]
        mean_a = sum(a) / window
        mean_b = sum(b) / window
        num = sum((a[j] - mean_a) * (b[j] - mean_b) for j in range(window))
        den_a = math.sqrt(sum((x - mean_a) ** 2 for x in a))
        den_b = math.sqrt(sum((x - mean_b) ** 2 for x in b))
        if den_a * den_b == 0:
            result.append(0)
        else:
            result.append(round(num / (den_a * den_b), 4))
    return result

def get_sector_data(sector='tech'):
    cfg = SECTORS.get(sector, SECTORS['tech'])
    dates = date_range(90)

    events = [(15, -0.6), (38, 0.5), (62, -0.4), (78, 0.7)]
    sentiment = generate_sentiment_series(90, base=0.1, noise=0.25, events=events)
    volatility = generate_volatility_series(sentiment, lag=cfg['sentiment_lag'], base_vol=cfg['volatility'])
    prices = generate_price_series(volatility, base_price=cfg['base_price'])
    rolling_corr = compute_rolling_correlation(
        [abs(s) for s in sentiment],
        volatility, window=7
    )

    # Tweet volume (proportional to abs sentiment with noise)
    tweet_vol = [int(abs(sentiment[i]) * 15000 + random.gauss(8000, 1500)) for i in range(90)]

    # VADER-like daily breakdown
    positive = [round(max(0, sentiment[i]) * 0.6 + 0.25 + random.gauss(0, 0.05), 3) for i in range(90)]
    negative = [round(max(0, -sentiment[i]) * 0.6 + 0.15 + random.gauss(0, 0.04), 3) for i in range(90)]
    neutral = [round(max(0, 1 - positive[i] - negative[i]), 3) for i in range(90)]

    return {
        "sector": sector,
        "label": cfg['label'],
        "stocks": cfg['stocks'],
        "color": cfg['color'],
        "correlation": cfg['correlation'],
        "sentiment_lag": cfg['sentiment_lag'],
        "dates": dates,
        "sentiment": sentiment,
        "volatility": volatility,
        "prices": prices,
        "rolling_corr": rolling_corr,
        "tweet_volume": tweet_vol,
        "sentiment_breakdown": {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
        },
        "key_events": [
            {"day": 15, "date": dates[15], "label": "Regulatory concern tweet surge", "impact": "negative"},
            {"day": 38, "date": dates[38], "label": "Positive earnings sentiment spike", "impact": "positive"},
            {"day": 62, "date": dates[62], "label": "Macro fear sentiment rise", "impact": "negative"},
            {"day": 78, "date": dates[78], "label": "Product launch buzz", "impact": "positive"},
        ],
    }

def get_correlation_data():
    """Cross-sector sentiment-volatility correlation matrix."""
    sectors = list(SECTORS.keys())
    matrix = {}
    for s in sectors:
        matrix[s] = {}
        for t in sectors:
            if s == t:
                matrix[s][t] = round(SECTORS[s]['correlation'], 3)
            else:
                matrix[s][t] = round(random.uniform(0.28, 0.52), 3)

    lag_analysis = {}
    for s in sectors:
        lag_analysis[s] = {
            f"lag_{i}": round(SECTORS[s]['correlation'] * math.exp(-0.3 * abs(i - SECTORS[s]['sentiment_lag'])) + random.gauss(0, 0.03), 3)
            for i in range(6)
        }

    return {
        "matrix": matrix,
        "lag_analysis": lag_analysis,
        "sector_labels": {k: v['label'] for k, v in SECTORS.items()},
        "sector_colors": {k: v['color'] for k, v in SECTORS.items()},
    }

def get_granger_results():
    """Granger causality test results (simulated from realistic values)."""
    results = []
    for sector, cfg in SECTORS.items():
        base_f = cfg['correlation'] * 12
        for lag in range(1, 6):
            f_stat = base_f * math.exp(-0.2 * abs(lag - cfg['sentiment_lag'])) + random.gauss(0, 0.4)
            f_stat = max(0.5, f_stat)
            # p-value: significant around optimal lag
            if abs(lag - cfg['sentiment_lag']) <= 1:
                p_val = round(random.uniform(0.001, 0.048), 4)
                significant = True
            else:
                p_val = round(random.uniform(0.08, 0.45), 4)
                significant = False
            results.append({
                "sector": sector,
                "label": cfg['label'],
                "lag": lag,
                "f_statistic": round(f_stat, 3),
                "p_value": p_val,
                "significant": significant,
                "optimal": lag == cfg['sentiment_lag'],
            })
    return {"results": results, "alpha": 0.05}

def get_summary_stats():
    stats = {}
    for sector, cfg in SECTORS.items():
        sentiment = generate_sentiment_series(90, 0.1, 0.25)
        volatility = generate_volatility_series(sentiment, cfg['sentiment_lag'], cfg['volatility'])
        avg_sent = sum(sentiment) / len(sentiment)
        avg_vol = sum(volatility) / len(volatility)
        neg_days = sum(1 for s in sentiment if s < -0.2)
        high_vol_days = sum(1 for v in volatility if v > avg_vol * 1.5)
        stats[sector] = {
            "label": cfg['label'],
            "color": cfg['color'],
            "avg_sentiment": round(avg_sent, 4),
            "avg_volatility": round(avg_vol * 100, 3),
            "negative_days": neg_days,
            "high_volatility_days": high_vol_days,
            "pearson_r": cfg['correlation'],
            "optimal_lag": cfg['sentiment_lag'],
        }
    return stats
