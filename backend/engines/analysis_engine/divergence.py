"""
divergence.py

ماژول تشخیص واگرایی‌ها (Regular و Hidden) بین قیمت و اندیکاتورها:
- پشتیبانی واگرایی معمولی و مخفی بین قیمت و RSI و MACD
- توسعه‌پذیر برای افزودن اندیکاتور جدید (OBV و ...)
- خروجی قابل استفاده در مولتی‌تایم‌فریم

Author: farbodbod1990
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

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

def find_divergence(price: pd.Series, indicator: pd.Series, kind='regular', window=20) -> List[Dict[str, Any]]:
    """
    شناسایی واگرایی (معمولی یا مخفی) بین قیمت و اندیکاتور
    kind: "regular" یا "hidden"
    """
    divs = []
    for i in range(window, len(price)):
        price_slice = price[i-window:i]
        ind_slice = indicator[i-window:i]
        if price_slice.is_monotonic_increasing and not ind_slice.is_monotonic_increasing:
            if kind == 'regular':
                divs.append({'index': i, 'type': 'bearish'})
            elif kind == 'hidden':
                divs.append({'index': i, 'type': 'bullish'})
        if price_slice.is_monotonic_decreasing and not ind_slice.is_monotonic_decreasing:
            if kind == 'regular':
                divs.append({'index': i, 'type': 'bullish'})
            elif kind == 'hidden':
                divs.append({'index': i, 'type': 'bearish'})
    return divs

def detect_divergence(df: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
    """
    تشخیص واگرایی معمولی و مخفی بین قیمت و RSI و MACD
    """
    df = df.copy()
    df['rsi'] = calc_rsi(df)
    macd_line, signal_line, macd_hist = calc_macd(df)
    df['macd'] = macd_line

    # واگرایی بین قیمت و RSI
    rsi_reg_divs = find_divergence(df['close'], df['rsi'], kind='regular', window=window)
    rsi_hid_divs = find_divergence(df['close'], df['rsi'], kind='hidden', window=window)
    # واگرایی بین قیمت و MACD
    macd_reg_divs = find_divergence(df['close'], df['macd'], kind='regular', window=window)
    macd_hid_divs = find_divergence(df['close'], df['macd'], kind='hidden', window=window)

    return {
        'rsi_regular': rsi_reg_divs,
        'rsi_hidden': rsi_hid_divs,
        'macd_regular': macd_reg_divs,
        'macd_hidden': macd_hid_divs
    }

# مثال استفاده:
"""
import pandas as pd
df = pd.read_csv('btc_1h.csv')
result = detect_divergence(df)
print(result['rsi_regular'])
"""
