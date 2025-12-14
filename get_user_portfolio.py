def get_user_portfolio():
    tickers = input("Enter tickers separated by commas: ").upper().split(",")
    tickers = [t.strip() for t in tickers]

    weights = input("Enter weights (same order), separated by commas: ").split(",")
    weights = [float(w) for w in weights]

    if len(tickers) != len(weights):
        raise ValueError("Number of weights must match number of tickers.")

    total = sum(weights)
    weights = [w / total for w in weights]

    return tickers, weights

