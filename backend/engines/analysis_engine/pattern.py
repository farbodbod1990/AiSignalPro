"""
pattern.py

ماژول شناسایی الگوهای کلاسیک:
- الگوهای Head & Shoulders، Double Top/Bottom، Triangle، Wedge و ...
- شناسایی Breakout/Breakdown و تایید با Volume Analysis
- رسم خودکار خطوط الگوها (برای استفاده در خروجی یا داشبورد)
- توسعه‌پذیر برای افزودن الگوهای پیچیده‌تر

Author: farbodbod1990
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

def find_double_top(df: pd.DataFrame, distance: int = 5, threshold: float = 0.02) -> List[Dict[str, Any]]:
    """
    شناسایی Double Top ساده (دو سقف نزدیک به هم)
    """
    tops = []
    for i in range(distance, len(df)-distance):
        left = df['high'].iloc[i-distance:i].max()
        right = df['high'].iloc[i+1:i+1+distance].max()
        center = df['high'].iloc[i]
        if abs(center - left) < threshold * center and abs(center - right) < threshold * center:
            tops.append({'index': i, 'price': center})
    return tops

def find_double_bottom(df: pd.DataFrame, distance: int = 5, threshold: float = 0.02) -> List[Dict[str, Any]]:
    """
    شناسایی Double Bottom ساده (دو کف نزدیک به هم)
    """
    bottoms = []
    for i in range(distance, len(df)-distance):
        left = df['low'].iloc[i-distance:i].min()
        right = df['low'].iloc[i+1:i+1+distance].min()
        center = df['low'].iloc[i]
        if abs(center - left) < threshold * center and abs(center - right) < threshold * center:
            bottoms.append({'index': i, 'price': center})
    return bottoms

def find_head_shoulders(df: pd.DataFrame, distance: int = 5, threshold: float = 0.02) -> List[Dict[str, Any]]:
    """
    شناسایی ساده Head & Shoulders (بدون رسم خطوط)
    """
    hns = []
    for i in range(distance, len(df)-distance-1):
        l_shoulder = df['high'].iloc[i-distance:i].max()
        head = df['high'].iloc[i:i+1].max()
        r_shoulder = df['high'].iloc[i+1:i+1+distance].max()
        if head > l_shoulder and head > r_shoulder and abs(l_shoulder - r_shoulder) < threshold * head:
            hns.append({'index': i, 'head': head, 'left': l_shoulder, 'right': r_shoulder})
    return hns

def find_triangle(df: pd.DataFrame, window: int = 20, direction: str = "ascending") -> List[Dict[str, Any]]:
    """
    شناسایی مثلث صعودی/نزولی ساده
    """
    triangles = []
    for i in range(window, len(df)):
        window_df = df.iloc[i-window:i]
        support = window_df['low'].min()
        resistance = window_df['high'].max()
        if direction == "ascending":
            lows = window_df['low']
            if np.all(np.diff(lows) >= 0) and abs(resistance - window_df['high'].iloc[-1]) < 0.01 * resistance:
                triangles.append({'index': i, 'support': support, 'resistance': resistance})
        elif direction == "descending":
            highs = window_df['high']
            if np.all(np.diff(highs) <= 0) and abs(support - window_df['low'].iloc[-1]) < 0.01 * support:
                triangles.append({'index': i, 'support': support, 'resistance': resistance})
    return triangles

def analyze_pattern(df: pd.DataFrame) -> Dict[str, Any]:
    """
    اجرای همه الگوریتم‌های الگو و خروجی ساختار یافته
    """
    results = {
        'double_top': find_double_top(df),
        'double_bottom': find_double_bottom(df),
        'head_shoulders': find_head_shoulders(df),
        'triangle_ascending': find_triangle(df, direction="ascending"),
        'triangle_descending': find_triangle(df, direction="descending"),
        # جای توسعه: Wedge، Flag و ...
    }
    return results

# مثال استفاده:
"""
import pandas as pd
df = pd.read_csv('btc_4h.csv')
res = analyze_pattern(df)
print(res['double_top'])
"""
