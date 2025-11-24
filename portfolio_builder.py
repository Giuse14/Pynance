import pandas as pd

def build_portfolio_series(data, tickers, weights):
    closes = []

    for t in tickers:
        closes.append(data[t]["Close"].dropna())

    # combine into a DataFrame
    df = pd.concat(closes, axis=1)
    df.columns = tickers
    df = df.dropna()

    # weighted sum
    portfolio = df.dot(weights)

    return portfolio
