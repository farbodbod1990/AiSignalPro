"""
trend.py

ماژول تشخیص روند و فاز بازار:
- استفاده از EMA/SMA برای شناسایی روند (صعودی، نزولی، رنج)
- محاسبه ADX/DMI برای قدرت روند
- خروجی فاز بازار و سیگنال روند در هر تایم‌فریم
- توسعه‌پذیر برای افزودن الگوریتم‌های جدید

Author: farbodbod1990
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def calc_ema(df, period=20):
    return df['close'].ewm(span=period, adjust=False).mean()

def calc_sma(df, period=20):
    return df['close'].rolling(window=period).mean()

def calc_adx(df, period=14):
    """محاسبه اندیکاتور ADX برای سنجش قدرت روند"""
    df = df.copy()
    df['tr1'] = abs(df['high'] - df['low'])
    df['tr2'] = abs(df['high'] - df['close'].shift())
    df['tr3'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    df['plus_dm'] = np.where((df['high'] - df['high'].shift()) > (df['low'].shift() - df['low']), 
                             np.maximum(df['high'] - df['high'].shift(), 0), 0)
    df['minus_dm'] = np.where((df['low'].shift() - df['low']) > (df['high'] - df['high'].shift()), 
                              np.maximum(df['low'].shift() - df['low'], 0), 0)
    tr14 = df['tr'].rolling(window=period).sum()
    plus_dm14 = df['plus_dm'].rolling(window=period).sum()
    minus_dm14 = df['minus_dm'].rolling(window=period).sum()
    plus_di = 100 * (plus_dm14 / tr14)
    minus_di = 100 * (minus_dm14 / tr14)
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    df['adx'] = adx
    return df['adx']

def analyze_trend(df: pd.DataFrame) -> Dict[str, Any]:
    """
    تحلیل روند و فاز بازار: خروجی dict شامل سیگنال و پارامترها
    """
    out = df.copy()
    out['ema20'] = calc_ema(out, 20)
    out['sma50'] = calc_sma(out, 50)
    out['adx'] = calc_adx(out, 14)

    # فاز بازار: صعودی، نزولی، رنج
    def get_phase(row):
        if row['close'] > row['ema20'] > row['sma50'] and row['adx'] > 25:
            return 'uptrend'
        elif row['close'] < row['ema20'] < row['sma50'] and row['adx'] > 25:
            return 'downtrend'
        elif row['adx'] < 20:
            return 'range'
        else:
            return 'neutral'

    out['phase'] = out.apply(get_phase, axis=1)
    # سیگنال آخرین کندل
    signal = out['phase'].iloc[-1] if len(out) else 'neutral'
    return {
        'trend_df': out,
        'signal': signal,
        'last_adx': out['adx'].iloc[-1] if len(out) else None,
        'last_ema20': out['ema20'].iloc[-1] if len(out) else None,
        'last_sma50': out['sma50'].iloc[-1] if len(out) else None
    }

# مثال استفاده:
"""
import pandas as pd
df = pd.read_csv('btc_1h.csv')
result = analyze_trend(df)
print(result['signal'])
"""
