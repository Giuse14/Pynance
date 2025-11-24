import pandas as pd

def analyze_portfolio(data):
    """Berechnet einfache Kennzahlen für das Portfolio."""
    results = {}
    for t, df in data.items():
        returns = df["Close"].pct_change().dropna()
        results[t] = {
            "Rendite": returns.mean(),
            "Volatilität": returns.std()
        }
    return results