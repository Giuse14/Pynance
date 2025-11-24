import yfinance as yf
import pandas as pd

def load_data(tickers, period="1y"):
    """Lädt historische Kursdaten für mehrere Aktien."""
    data = {}
    for t in tickers:
        df = yf.download(t, period=period)
        data[t] = df
    return data