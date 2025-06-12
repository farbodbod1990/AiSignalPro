"""
preprocessing.py

ماژول پردازش اولیه داده‌های بازار:
- تغییر تایم‌فریم (resample)
- پاک‌سازی داده (cleaning)
- حذف داده‌های بی‌کیفیت و outlierها
- هماهنگ‌سازی با ساختار استاندارد تحلیل
- قابلیت توسعه برای افزودن stage جدید

Author: farbodbod1990
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

def clean_ohlcv(df: pd.DataFrame, z_thresh: float = 5.0) -> pd.DataFrame:
    """
    پاک‌سازی داده و حذف outlierها با روش Z-Score
    """
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df_clean = df.copy()
    for col in numeric_cols:
        if col in df_clean.columns:
            z = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
            df_clean = df_clean[z < z_thresh]
    df_clean = df_clean.drop_duplicates(subset=['timestamp'])
    df_clean = df_clean.sort_values('timestamp')
    return df_clean.reset_index(drop=True)

def resample_ohlcv(df: pd.DataFrame, from_tf: str, to_tf: str) -> pd.DataFrame:
    """
    تغییر تایم‌فریم داده از مثلا 1m به 5m یا 1h
    """
    tf_map = {'m': 'T', 'h': 'H', 'd': 'D'}
    rule = to_tf
    for k, v in tf_map.items():
        rule = rule.replace(k, v)
    df = df.copy()
    df['dt'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df.set_index('dt')
    df_resampled = df.resample(rule).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    df_resampled['timestamp'] = df_resampled.index.astype(np.int64) // 10**9
    return df_resampled.reset_index(drop=True)

def preprocess_ohlcv(
    dfs: Dict[str, Any], 
    timeframes: List[str], 
    logger=None
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    پردازش کامل داده‌ها برای هر نماد و تایم‌فریم
    """
    result = {}
    for symbol, df in dfs.items():
        result[symbol] = {}
        # پاک‌سازی و outlier
        if logger: logger.info(f"پاک‌سازی {symbol}")
        clean_df = clean_ohlcv(df)
        orig_tf = "1m"  # فرض بر این که ورودی 1m است، می‌توان پارامتری کرد
        for tf in timeframes:
            if tf == orig_tf:
                final_df = clean_df
            else:
                final_df = resample_ohlcv(clean_df, orig_tf, tf)
            # حذف کندل‌های ناقص (مثلاً حجم = صفر)
            final_df = final_df[final_df['volume'] > 0]
            result[symbol][tf] = final_df.reset_index(drop=True)
            if logger:
                logger.info(f"{symbol} تایم‌فریم {tf}: {len(final_df)} داده")
    return result

# مثال استفاده:
"""
import pandas as pd
btc = pd.read_csv('btc_1m.csv')
dfs = {'BTC': btc}
result = preprocess_ohlcv(dfs, ['1m', '5m', '1h'])
"""
