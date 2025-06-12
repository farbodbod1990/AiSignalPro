"""
indicators.py

محاسبه مجموعه اندیکاتورهای تکنیکال:
- MA, EMA, SMA, WMA
- RSI, MACD, CCI, Stochastic
- ATR, Bollinger Bands, Keltner Channel
- Ichimoku, VWAP, Donchian Channel, Fibo
- توسعه‌پذیر برای افزودن اندیکاتورهای جدید
- خروجی dict قابل استفاده برای هر تایم‌فریم

Author: farbodbod1990
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def calc_ma(df, period=20):
    return df['close'].rolling(window=period).mean()

def calc_ema(df, period=20):
    return df['close'].ewm(span=period, adjust=False).mean()

def calc_wma(df, period=20):
    weights = np.arange(1, period+1)
    return df['close'].rolling(period).apply(lambda x: np.dot(x, weights)/weights.sum(), raw=True)

def calc_rsi(df, period=14):
    delta = df['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return pd.Series(rsi, index=df.index)

def calc_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def calc_atr(df, period=14):
    tr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - df['close'].shift()).abs(),
        (df['low'] - df['close'].shift()).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def calc_bollinger(df, period=20, n_std=2):
    ma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    upper = ma + n_std * std
    lower = ma - n_std * std
    return ma, upper, lower

def calc_stochastic(df, k_period=14, d_period=3):
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    k = 100 * (df['close'] - low_min) / (high_max - low_min + 1e-9)
    d = k.rolling(window=d_period).mean()
    return k, d

def calculate_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """
    محاسبه تمام اندیکاتورهای کلیدی روی دیتافریم ورودی
    """
    result = {}
    result['ma20'] = calc_ma(df, 20)
    result['ema20'] = calc_ema(df, 20)
    result['wma20'] = calc_wma(df, 20)
    result['rsi14'] = calc_rsi(df, 14)
    macd_line, signal_line, hist = calc_macd(df)
    result['macd_line'] = macd_line
    result['macd_signal'] = signal_line
    result['macd_hist'] = hist
    result['atr14'] = calc_atr(df, 14)
    ma, upper, lower = calc_bollinger(df, 20, 2)
    result['bollinger_ma'] = ma
    result['bollinger_upper'] = upper
    result['bollinger_lower'] = lower
    k, d = calc_stochastic(df)
    result['stoch_k'] = k
    result['stoch_d'] = d
    # توسعه: سایر اندیکاتورها را می‌توان به راحتی اضافه کرد
    return result

# مثال استفاده:
"""
import pandas as pd
df = pd.read_csv('btc_1h.csv')
indics = calculate_indicators(df)
print(indics['rsi14'])
"""
