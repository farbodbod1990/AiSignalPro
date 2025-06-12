"""
multi_timeframe_analysis.py

Dispatcher حرفه‌ای تحلیل مولتی‌تایم‌فریم:
- دریافت دیتا از هر صرافی و تایم‌فریم دلخواه (اتوماتیک)
- اجرای همه ماژول‌های تحلیلی (leg/pivot, pattern, whale, risk, ...)
- ذخیره و لاگ نتایج هر تایم‌فریم
- توسعه‌پذیر برای اضافه‌کردن هر ماژول تحلیلی جدید
- آماده برای تولید سیگنال، مانیتورینگ و داشبورد

Author: farbodbod1990
"""

import pandas as pd
from typing import List, Dict, Any

from multi_exchange_fetcher import MultiExchangeFetcher
import leg_pivot
import pattern
import whale
import risk
import portfolio

class MultiTimeframeAnalysis:
    def __init__(self, source: str, symbol: str, timeframes: List[str], fetcher_kwargs: Dict[str, Any]={}):
        """
        source: نام صرافی (مثل 'coingecko')
        symbol: نماد یا coin_id (مثل 'bitcoin')
        timeframes: لیست تایم‌فریم‌ها (مثل ['1h', '4h', '1d'])
        fetcher_kwargs: پارامترهای اضافی fetcher (مثل vs_currency, days و ...)
        """
        self.source = source
        self.symbol = symbol
        self.timeframes = timeframes
        self.fetcher_kwargs = fetcher_kwargs
        self.fetcher = MultiExchangeFetcher(source)

    def run_all(self) -> Dict[str, Dict[str, Any]]:
        """
        اجرای کامل تحلیل روی همه تایم‌فریم‌ها و خروجی ساختار یافته
        """
        results = {}
        for tf in self.timeframes:
            print(f"دریافت دیتا: {self.symbol} - {tf} - {self.source}")
            df = self.fetcher.fetch_ohlcv(self.symbol, **self.fetcher_kwargs, interval=tf)
            print(f"تحلیل لگ و پیوت...")
            pivots = leg_pivot.detect_leg_pivot(df)
            print(f"تحلیل الگوهای کلاسیک...")
            patterns = pattern.analyze_pattern(df)
            print(f"تحلیل رفتار نهنگ‌ها...")
            whales = whale.analyze_whale(df)
            # ریسک و پورتفوی اختیاری (در صورت نیاز، با داده‌های پوزیشن)
            results[tf] = {
                'pivots': pivots,
                'patterns': patterns,
                'whale': whales,
                'raw': df.tail(3).to_dict()  # نمونه دیتای آخر برای مانیتورینگ
            }
        return results

# مثال استفاده:
"""
analysis = MultiTimeframeAnalysis(
    source='coingecko',
    symbol='bitcoin',
    timeframes=['1h', '4h', '1d'],
    fetcher_kwargs={'vs_currency': 'usd', 'days': '30'}
)
results = analysis.run_all()
print('نتایج:', results['1h']['patterns'])
"""
