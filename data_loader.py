# data_loader.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def load_data(tickers, period="10y"):
    """
    Load historical price data for given tickers
    
    Parameters:
    - tickers: list of ticker symbols
    - period: time period (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)
    """
    data = {}
    
    for t in tickers:
        try:
            # Download data
            df = yf.download(t, period=period, auto_adjust=True)
            if df.empty:
                print(f"No data found for {t}")
                continue
                
            # Keep only necessary columns
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            data[t] = df
            
            print(f"Loaded {t}: {len(df)} trading days")
            
        except Exception as e:
            print(f"Error loading {t}: {e}")
    
    return data