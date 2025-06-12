"""
whale.py

ماژول تشخیص رفتار نهنگ‌ها و دستکاری مارکت:
- شناسایی سفارشات بزرگ (whale orders) در volume/ob و کندل‌ها
- تشخیص رفتارهای مشکوک مانند spoofing, wash trading, pump&dump
- توسعه‌پذیر جهت افزودن الگوریتم‌های رفتارشناسی جدید

Author: farbodbod1990
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

def detect_whale_candles(df: pd.DataFrame, vol_thresh: float = 3.0) -> List[Dict[str, Any]]:
    """
    شناسایی کندل‌هایی با حجم غیرعادی (whale candles)
    vol_thresh: چند برابر میانگین حجم
    """
    whale_candles = []
    mean_vol = df['volume'].rolling(window=20).mean()
    for i in range(len(df)):
        if df['volume'].iloc[i] > vol_thresh * mean_vol.iloc[i]:
            whale_candles.append({
                'index': i,
                'timestamp': df['timestamp'].iloc[i],
                'volume': df['volume'].iloc[i],
                'price': df['close'].iloc[i]
            })
    return whale_candles

def detect_spoofing(df: pd.DataFrame, price_col='close', window=10, jump_thresh=2.0) -> List[Dict[str, Any]]:
    """
    تشخیص رفتار spoofing ساده: کندل‌های با حجم بالا و برگشت سریع قیمت
    """
    spoofings = []
    for i in range(window, len(df)):
        vol_now = df['volume'].iloc[i]
        price_now = df[price_col].iloc[i]
        price_prev = df[price_col].iloc[i-window]
        if vol_now > 2 * df['volume'].rolling(window=window).mean().iloc[i]:
            if abs(price_now - price_prev) > jump_thresh * df[price_col].rolling(window=window).std().iloc[i]:
                spoofings.append({'index': i, 'timestamp': df['timestamp'].iloc[i], 'volume': vol_now, 'price_jump': price_now - price_prev})
    return spoofings

def detect_wash_trading(df: pd.DataFrame, window=10) -> List[Dict[str, Any]]:
    """
    تشخیص ساده wash trading: حجم غیرعادی بدون تغییر قیمت
    """
    washes = []
    for i in range(window, len(df)):
        vol_now = df['volume'].iloc[i]
        price_change = abs(df['close'].iloc[i] - df['open'].iloc[i])
        if vol_now > 2 * df['volume'].rolling(window=window).mean().iloc[i] and price_change < 0.1 * df['close'].iloc[i]:
            washes.append({'index': i, 'timestamp': df['timestamp'].iloc[i], 'volume': vol_now, 'price_change': price_change})
    return washes

def analyze_whale(df: pd.DataFrame) -> Dict[str, Any]:
    """
    اجرای همه الگوریتم‌های تحلیل نهنگ و رفتار مارکت
    """
    return {
        'whale_candles': detect_whale_candles(df),
        'spoofing': detect_spoofing(df),
        'wash_trading': detect_wash_trading(df)
    }

# مثال استفاده:
"""
import pandas as pd
df = pd.read_csv('btc_1m.csv')
res = analyze_whale(df)
print(res['whale_candles'])
"""
