import pandas as pd

# def analyze_portfolio(data):
#     """Berechnet einfache Kennzahlen für das Portfolio."""
#     results = {}
#     for t, df in data.items():
#         returns = df["Close"].pct_change().dropna()
#         results[t] = {
#             "Rendite": returns.mean(),
#             "Volatilität": returns.std()
#         }
#     return results

def analyze_portfolio(data, weights=None):
    all_returns = []

    # 1. Calculate daily returns per asset
    for df in data.values():
        ret = df["Close"].pct_change().dropna()
        all_returns.append(ret)

    # 2. Combine into DataFrame
    returns = pd.concat(all_returns, axis=1)
    returns.columns = data.keys()

    # 3. Per-asset stats
    per_asset = returns.agg(["mean", "std"]).T

    # 4. Portfolio stats
    if weights:
        import numpy as np

        weights = np.array(weights)
        port_returns = returns.dot(weights)
        port_mean = port_returns.mean()
        port_std = port_returns.std()
        sharpe = port_mean / port_std if port_std != 0 else None
    else:
        port_mean = port_std = sharpe = None

    return {
        "Asset Stats": per_asset,
        "Portfolio Return": port_mean,
        "Portfolio Volatility": port_std,
        "Sharpe Ratio": sharpe,
        "Correlation Matrix": returns.corr()
    }
