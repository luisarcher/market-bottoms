import numpy as np
import pandas as pd

def williams_vix_fix(df, pd_=22, bbl=20, mult=2.0, lb=50, ph=0.85, pl=1.01):
    """
    Williams Vix Fix indicator logic, returns a DataFrame with 'wvf', 'upperBand', 'rangeHigh', and 'bottom' columns.
    'bottom' is 1 if it's a good day to buy, else 0.
    """
    df = df.copy()
    # Calculate WVF
    df['wvf'] = (df['High'].rolling(pd_).max() - df['Low']) / df['High'].rolling(pd_).max() * 100
    # Bands
    sDev = mult * df['wvf'].rolling(bbl).std()
    midLine = df['wvf'].rolling(bbl).mean()
    df['upperBand'] = midLine + sDev
    df['rangeHigh'] = df['wvf'].rolling(lb).max() * ph
    # Good day to buy condition
    df['bottom'] = ((df['wvf'] >= df['upperBand']) | (df['wvf'] >= df['rangeHigh'])).astype(int)
    return df[['wvf', 'upperBand', 'rangeHigh', 'bottom']]
