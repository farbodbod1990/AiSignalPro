"""
candlestick.py

ماژول تحلیل کندل و شناسایی الگوهای کندلی:
- شناسایی الگوهای مشهور (Doji, Engulfing, Hammer, Shooting Star, ...)
- محاسبه سایه بالا/پایین
- تشخیص کندل‌های قدرتمند و ترکیب کندل‌ها
- توسعه‌پذیر جهت افزودن الگوهای جدید

Author: farbodbod1990
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def upper_shadow(row):
    return row['high'] - max(row['close'], row['open'])

def lower_shadow(row):
    return min(row['close'], row['open']) - row['low']

def real_body(row):
    return abs(row['close'] - row['open'])

def is_doji(row, threshold=0.1):
    body = real_body(row)
    rng = row['high'] - row['low']
    return body < threshold * rng

def is_bullish_engulfing(row_prev, row):
    return (row_prev['close'] < row_prev['open'] and
            row['close'] > row['open'] and
            row['open'] < row_prev['close'] and
            row['close'] > row_prev['open'])

def is_bearish_engulfing(row_prev, row):
    return (row_prev['close'] > row_prev['open'] and
            row['close'] < row['open'] and
            row['open'] > row_prev['close'] and
            row['close'] < row_prev['open'])

def is_hammer(row, body_ratio=0.33, shadow_ratio=2.0):
    body = real_body(row)
    lower = lower_shadow(row)
    upper = upper_shadow(row)
    rng = row['high'] - row['low']
    return (body < body_ratio * rng and
            lower > shadow_ratio * body and
            upper < body)

def is_shooting_star(row, body_ratio=0.33, shadow_ratio=2.0):
    body = real_body(row)
    lower = lower_shadow(row)
    upper = upper_shadow(row)
    rng = row['high'] - row['low']
    return (body < body_ratio * rng and
            upper > shadow_ratio * body and
            lower < body)

def analyze(df: pd.DataFrame) -> Dict[str, Any]:
    """
    استخراج الگوهای کندلی و ویژگی‌های کلیدی
    """
    patterns = []
    for i in range(1, len(df)):
        row_prev = df.iloc[i-1]
        row = df.iloc[i]
        pattern = None
        if is_doji(row):
            pattern = "doji"
        elif is_bullish_engulfing(row_prev, row):
            pattern = "bullish_engulfing"
        elif is_bearish_engulfing(row_prev, row):
            pattern = "bearish_engulfing"
        elif is_hammer(row):
            pattern = "hammer"
        elif is_shooting_star(row):
            pattern = "shooting_star"
        else:
            pattern = ""
        patterns.append(pattern)
    df_out = df.iloc[1:].copy()
    df_out['pattern'] = patterns
    df_out['upper_shadow'] = df_out.apply(upper_shadow, axis=1)
    df_out['lower_shadow'] = df_out.apply(lower_shadow, axis=1)
    df_out['body'] = df_out.apply(real_body, axis=1)
    df_out['strong_bullish'] = (df_out['close'] > df_out['open']) & (df_out['body'] > df_out['body'].mean())
    df_out['strong_bearish'] = (df_out['close'] < df_out['open']) & (df_out['body'] > df_out['body'].mean())
    return df_out

# مثال استفاده:
"""
import pandas as pd
df = pd.read_csv('btc_1m.csv')
result = analyze(df)
print(result[result['pattern']=='doji'])
"""
