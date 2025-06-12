"""
leg_pivot.py

ماژول شناسایی لگ‌ها و پیوت‌های اصلی/فرعی:
- تشخیص پیوت‌های قوی و ضعیف (با الگوریتم‌های Zigzag و Swing High/Low)
- محاسبه Legها (Leg1, Leg2, ...)
- ترسیم ساختار موجی و شناسایی نقاط برگشتی (Reversal)
- توسعه‌پذیر جهت الگوهای پیچیده‌تر

Author: farbodbod1990
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any

def find_pivots(df: pd.DataFrame, left: int = 3, right: int = 3) -> List[Dict[str, Any]]:
    """
    شناسایی پیوت‌های اصلی (local maxima/minima)
    left/right: تعداد کندل‌های سمت چپ و راست برای تایید پیوت
    """
    pivots = []
    for i in range(left, len(df)-right):
        window = df.iloc[i-left:i+right+1]
        center = df.iloc[i]
        # High Pivot (سقف)
        if center['high'] == window['high'].max():
            pivots.append({'index': i, 'type': 'high', 'price': center['high']})
        # Low Pivot (کف)
        if center['low'] == window['low'].min():
            pivots.append({'index': i, 'type': 'low', 'price': center['low']})
    return pivots

def extract_legs(pivots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    استخراج ساختار لگ‌ها از لیست پیوت‌ها
    """
    legs = []
    for i in range(1, len(pivots)):
        leg = {
            'start_idx': pivots[i-1]['index'],
            'end_idx': pivots[i]['index'],
            'start_price': pivots[i-1]['price'],
            'end_price': pivots[i]['price'],
            'type': f"{pivots[i-1]['type']}_to_{pivots[i]['type']}",
            'direction': 'up' if pivots[i]['price'] > pivots[i-1]['price'] else 'down',
            'length': abs(pivots[i]['price'] - pivots[i-1]['price'])
        }
        legs.append(leg)
    return legs

def detect_leg_pivot(df: pd.DataFrame, left: int = 3, right: int = 3) -> Dict[str, Any]:
    """
    شناسایی پیوت‌ها و لگ‌ها و خروجی ساختار موجی
    """
    pivots = find_pivots(df, left, right)
    legs = extract_legs(pivots)
    return {
        'pivots': pivots,
        'legs': legs
    }

# مثال استفاده:
"""
import pandas as pd
df = pd.read_csv('btc_1h.csv')
result = detect_leg_pivot(df)
print(result['pivots'])
print(result['legs'])
"""
