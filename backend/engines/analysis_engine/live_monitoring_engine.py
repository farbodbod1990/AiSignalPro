"""
live_monitoring_engine.py

ماژول مانیتورینگ زنده بازار:
- دریافت دیتا به صورت real-time یا نزدیک به زنده از صرافی یا Coingecko
- اجرای تحلیل و سیگنال‌ساز (signal_generator) روی آخرین دیتا
- ارسال هشدار و ثبت لاگ (قابل توسعه برای ارسال به تلگرام/ایمیل)
- فاقد قابلیت ترید (امن و فقط هشداردهنده)
- توسعه‌پذیر برای اتصال به هر ماژول و هر نوع نوتیف

Author: farbodbod1990
"""

import time
import pandas as pd
from typing import Dict, Any, List
from multi_exchange_fetcher import MultiExchangeFetcher
import multi_timeframe_analysis
import signal_generator

class LiveMonitoringEngine:
    def __init__(
        self,
        source: str,
        symbol: str,
        timeframes: List[str],
        fetcher_kwargs: Dict[str, Any] = {},
        poll_interval: int = 60,
        alert_handler=None
    ):
        """
        source: نام صرافی یا منبع دیتا (مثلاً 'coingecko')
        symbol: نماد یا coin_id (مثلاً 'bitcoin')
        timeframes: تایم‌فریم‌های مورد نظر (مثلاً ['1h','4h','1d'])
        fetcher_kwargs: پارامترهای اضافه برای fetcher
        poll_interval: فاصله بین هر بار دریافت دیتا (ثانیه)
        alert_handler: تابع یا شیء برای ارسال هشدار (مثلاً ارسال به تلگرام)
        """
        self.source = source
        self.symbol = symbol
        self.timeframes = timeframes
        self.fetcher_kwargs = fetcher_kwargs
        self.poll_interval = poll_interval
        self.alert_handler = alert_handler
        self.analysis = multi_timeframe_analysis.MultiTimeframeAnalysis(
            source=source,
            symbol=symbol,
            timeframes=timeframes,
            fetcher_kwargs=fetcher_kwargs
        )

    def run(self, run_once: bool = False):
        """
        اجرای مانیتورینگ زنده (تا وقتی که اجرا نشه یا با run_once فقط یک بار)
        """
        while True:
            print(f"دریافت دیتا و تحلیل برای {self.symbol} ...")
            results = self.analysis.run_all()
            tf_signals = signal_generator.multi_tf_signal(results)
            consensus = signal_generator.consensus_signal(tf_signals)
            alert = {
                "symbol": self.symbol,
                "signals": consensus,
                "time": pd.Timestamp.now(),
                "details": tf_signals
            }
            self._send_alert(alert)
            if run_once:
                break
            time.sleep(self.poll_interval)

    def _send_alert(self, alert: Dict[str, Any]):
        """
        ارسال هشدار یا ثبت لاگ (قابل توسعه)
        """
        msg = f"[{alert['time']}] سیگنال برای {alert['symbol']}: {alert['signals']}"
        print(msg)
        # اگر alert_handler تعریف شد، فراخوانی شود
        if self.alert_handler:
            self.alert_handler(alert)

# مثال استفاده:
"""
engine = LiveMonitoringEngine(
    source='coingecko',
    symbol='bitcoin',
    timeframes=['1h','4h','1d'],
    fetcher_kwargs={'vs_currency':'usd','days':7},
    poll_interval=60
)
engine.run(run_once=True)  # یا بدون run_once برای اجرا دائمی
"""
