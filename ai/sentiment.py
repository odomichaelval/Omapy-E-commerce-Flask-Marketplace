"""
Sentiment analysis for review text, using VADER (Valence Aware Dictionary
and sEntiment Reasoner) - a pretrained, rule-based sentiment analyzer
built specifically for short, informal text like reviews. No training
required - unlike the classifier/regressor, this ships ready to use.
"""
#completed the Sentiment Analysis Implementation
#see code below for the implementation of the Sentiment Analysis using VADER
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text):
    """
    Returns (label, compound_score).
    compound_score ranges -1 (most negative) to +1 (most positive).
    Thresholds below are VADER's own standard recommendation, not
    something we tuned ourselves.
    """
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return label, compound