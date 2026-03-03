import re

# VADER-inspired lexicon (simplified)
POS_WORDS = {
    "good": 1.9, "great": 3.1, "excellent": 3.4, "amazing": 3.2, "outstanding": 3.5,
    "profit": 2.1, "growth": 2.3, "surge": 2.0, "bullish": 2.4, "gains": 1.9,
    "strong": 1.8, "positive": 1.9, "recovery": 2.0, "innovation": 1.8, "breakthrough": 2.5,
    "beat": 2.0, "record": 2.2, "rise": 1.7, "boost": 2.0, "rally": 2.1,
    "up": 1.2, "increase": 1.7, "upgrade": 2.0, "buy": 1.5, "outperform": 2.2,
}

NEG_WORDS = {
    "bad": -1.9, "terrible": -3.2, "awful": -3.1, "loss": -2.3, "decline": -2.0,
    "fall": -1.8, "crash": -3.1, "bearish": -2.5, "fraud": -3.3, "scandal": -3.1,
    "weak": -1.9, "negative": -2.0, "recession": -2.8, "cut": -1.7, "drop": -2.0,
    "down": -1.4, "decrease": -1.8, "downgrade": -2.2, "sell": -1.5, "underperform": -2.3,
    "fear": -2.1, "panic": -2.8, "risk": -1.4, "uncertainty": -1.7, "volatile": -1.5,
}

NEGATORS = {"not", "no", "never", "neither", "nor", "nothing", "nobody", "nowhere"}
AMPLIFIERS = {"very", "extremely", "highly", "really", "absolutely"}
DAMPENERS = {"somewhat", "slightly", "barely", "hardly", "little"}

def tokenize(text):
    return re.findall(r"[a-z]+", text.lower())

def analyze_text_sentiment(text):
    if not text or len(text.strip()) < 5:
        return {"score": 0, "label": "NEUTRAL", "compound": 0,
                "positive": 0.33, "negative": 0.33, "neutral": 0.34, "error": "Text too short"}

    tokens = tokenize(text)
    scores = []
    i = 0
    while i < len(tokens):
        word = tokens[i]
        multiplier = 1.0

        # Check 3-word window behind for negators/amplifiers
        window = tokens[max(0, i-3):i]
        if any(w in NEGATORS for w in window):
            multiplier *= -0.74
        if any(w in AMPLIFIERS for w in window):
            multiplier *= 1.3
        if any(w in DAMPENERS for w in window):
            multiplier *= 0.6

        if word in POS_WORDS:
            scores.append(POS_WORDS[word] * multiplier)
        elif word in NEG_WORDS:
            scores.append(NEG_WORDS[word] * multiplier)
        i += 1

    if not scores:
        compound = 0.0
    else:
        total = sum(scores)
        # Normalize to [-1, 1] using VADER-style normalization
        alpha = 15
        compound = total / (abs(total) + alpha)

    compound = round(compound, 4)

    if compound >= 0.05:
        label = "POSITIVE"
        pos = round(0.4 + compound * 0.4, 3)
        neg = round(0.1 + (1 - compound) * 0.05, 3)
    elif compound <= -0.05:
        label = "NEGATIVE"
        neg = round(0.4 + abs(compound) * 0.4, 3)
        pos = round(0.1 + (1 - abs(compound)) * 0.05, 3)
    else:
        label = "NEUTRAL"
        pos = round(0.25 + compound * 0.1, 3)
        neg = round(0.25 - compound * 0.1, 3)

    neutral = round(max(0, 1.0 - pos - neg), 3)
    score = round(compound, 4)

    # Find contributing words
    contrib = []
    for word in tokens:
        if word in POS_WORDS:
            contrib.append({"word": word, "score": POS_WORDS[word], "type": "positive"})
        elif word in NEG_WORDS:
            contrib.append({"word": word, "score": NEG_WORDS[word], "type": "negative"})

    return {
        "score": score,
        "compound": compound,
        "label": label,
        "positive": pos,
        "negative": neg,
        "neutral": neutral,
        "word_count": len(tokens),
        "contributing_words": contrib[:8],
        "interpretation": get_interpretation(compound),
    }

def get_interpretation(compound):
    if compound >= 0.5:
        return "Strongly positive sentiment — likely to suppress short-term volatility"
    elif compound >= 0.05:
        return "Mildly positive — slight downward pressure on volatility expected"
    elif compound <= -0.5:
        return "Strongly negative — high volatility spike predicted within 1-3 trading days"
    elif compound <= -0.05:
        return "Mildly negative — moderate volatility increase possible"
    else:
        return "Neutral sentiment — minimal expected impact on market volatility"
