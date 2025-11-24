# asset_database.py
ASSET_DATABASE = {
    # Stocks & Equity ETFs
    "SPY": {"name": "SPDR S&P 500 ETF", "type": "US Large Cap Stocks", "category": "Equity"},
    "QQQ": {"name": "Invesco QQQ Trust", "type": "US Growth Stocks", "category": "Equity"},
    "VTI": {"name": "Vanguard Total Stock Market", "type": "US Total Market Stocks", "category": "Equity"},
    "VXUS": {"name": "Vanguard Total International Stock", "type": "International Stocks", "category": "Equity"},
    "IWN": {"name": "iShares Russell 2000 Value ETF", "type": "US Small Cap Value Stocks", "category": "Equity"},
    
    # Bonds & Fixed Income
    "TLT": {"name": "iShares 20+ Year Treasury Bond", "type": "Long-term Treasury Bonds", "category": "Fixed Income"},
    "AGG": {"name": "iShares Core U.S. Aggregate Bond", "type": "Total Bond Market", "category": "Fixed Income"},
    "BND": {"name": "Vanguard Total Bond Market", "type": "Total Bond Market", "category": "Fixed Income"},
    "IEF": {"name": "iShares 7-10 Year Treasury Bond", "type": "Intermediate Treasury Bonds", "category": "Fixed Income"},
    "SHY": {"name": "iShares 1-3 Year Treasury Bond", "type": "Short-term Treasury Bonds", "category": "Fixed Income"},
    "LQD": {"name": "iShares iBoxx $ Investment Grade Corporate Bond", "type": "Corporate Bonds", "category": "Fixed Income"},
    
    # Commodities
    "GLD": {"name": "SPDR Gold Shares", "type": "Gold", "category": "Commodity"},
    "SLV": {"name": "iShares Silver Trust", "type": "Silver", "category": "Commodity"},
    "DBC": {"name": "Invesco DB Commodity Index Tracking", "type": "Broad Commodities", "category": "Commodity"},
    "USO": {"name": "United States Oil Fund", "type": "Oil", "category": "Commodity"},
    
    # Real Estate
    "VNQ": {"name": "Vanguard Real Estate ETF", "type": "Real Estate", "category": "Real Estate"},
    "IYR": {"name": "iShares U.S. Real Estate ETF", "type": "Real Estate", "category": "Real Estate"},
    
    # Individual Stocks (examples)
    "AAPL": {"name": "Apple Inc.", "type": "Technology", "category": "Equity"},
    "MSFT": {"name": "Microsoft Corporation", "type": "Technology", "category": "Equity"},
    "GOOGL": {"name": "Alphabet Inc.", "type": "Technology", "category": "Equity"},
    "AMZN": {"name": "Amazon.com Inc.", "type": "Consumer Discretionary", "category": "Equity"},
    "TSLA": {"name": "Tesla Inc.", "type": "Automotive", "category": "Equity"},
    "JPM": {"name": "JPMorgan Chase & Co.", "type": "Financial Services", "category": "Equity"},
    "JNJ": {"name": "Johnson & Johnson", "type": "Healthcare", "category": "Equity"},
    "XOM": {"name": "Exxon Mobil Corporation", "type": "Energy", "category": "Equity"},
    "META": {"name": "Meta Platforms Inc.", "type": "Technology", "category": "Equity"},
    "NVDA": {"name": "NVIDIA Corporation", "type": "Technology", "category": "Equity"},
}

PORTFOLIO_STRATEGIES = {
    "All Weather (Ray Dalio)": {
        "description": "Designed to perform well in all economic environments",
        "assets": {
            "TLT": 0.40,    # Long-term bonds (perform well in deflation)
            "SPY": 0.30,    # US stocks (perform well in growth)
            "IEF": 0.15,    # Intermediate bonds (balance)
            "GLD": 0.075,   # Gold (inflation hedge)
            "DBC": 0.075,   # Commodities (inflation hedge)
        }
    },
    "60/40 Portfolio": {
        "description": "Traditional balanced portfolio with 60% stocks, 40% bonds",
        "assets": {
            "SPY": 0.60,    # US stocks
            "AGG": 0.40,    # US bonds
        }
    },
    "Permanent Portfolio": {
        "description": "Conservative portfolio designed for all economic conditions",
        "assets": {
            "SPY": 0.25,    # Stocks (prosperity)
            "TLT": 0.25,    # Long-term bonds (deflation)
            "GLD": 0.25,    # Gold (inflation)
            "SHY": 0.25,    # Short-term bonds (recession)
        }
    },
    "Three Fund Portfolio": {
        "description": "Simple diversified portfolio using three total market funds",
        "assets": {
            "VTI": 0.50,    # Total US stock market
            "VXUS": 0.30,   # Total international stock market
            "BND": 0.20,    # Total bond market
        }
    },
    "Golden Butterfly": {
        "description": "Aggressive alternative to Permanent Portfolio with higher stock allocation",
        "assets": {
            "SPY": 0.20,    # US stocks
            "IWN": 0.20,    # Small cap value stocks
            "TLT": 0.20,    # Long-term bonds
            "SHY": 0.20,    # Short-term bonds
            "GLD": 0.20,    # Gold
        }
    }
}

def get_asset_info(ticker):
    """Get asset information from database"""
    return ASSET_DATABASE.get(ticker, {"name": ticker, "type": "Unknown", "category": "Unknown"})

def get_portfolio_allocation(portfolio_tickers, portfolio_weights):
    """Calculate allocation by asset category"""
    allocation = {}
    for ticker, weight in zip(portfolio_tickers, portfolio_weights):
        asset_info = get_asset_info(ticker)
        category = asset_info["category"]
        allocation[category] = allocation.get(category, 0) + weight
    return allocation