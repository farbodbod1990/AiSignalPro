"""
multi_exchange_fetcher.py

Dispatcher حرفه‌ای برای دریافت دیتا از چندین صرافی (multi-exchange):
- پشتیبانی coingecko (کامل)، kucoin, gate.io, okx, mexc, coinmarketcap, bitfinex (قابل توسعه)
- خروجی DataFrame استاندارد با ستون‌های [timestamp, open, high, low, close, volume]
- انتخاب خودکار fetcher بر اساس نام صرافی
- آماده برای توسعه و افزودن هر صرافی جدید

Author: farbodbod1990
"""

import pandas as pd
from typing import Optional

# Coingecko fetcher (کامل)
import requests

class CoingeckoFetcher:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def fetch_ohlcv(self, coin_id: str, vs_currency: str = "usd", days: str = "max", interval: str = "hourly") -> pd.DataFrame:
        url = f"{self.BASE_URL}/coins/{coin_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days, "interval": interval}
        r = requests.get(url, params=params)
        data = r.json()
        if 'prices' not in data:
            raise ValueError("No data returned from Coingecko API.")
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        # فقط ستون close و volume را داریم
        if 'total_volumes' in data:
            df['volume'] = [v[1] for v in data['total_volumes']]
        # open/high/low را با close پر می‌کنیم (برای تحلیل ساده)
        for col in ['open', 'high', 'low']:
            df[col] = df['close']
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        return df

# اسکلت سایر fetcherها (قابل توسعه)
class KucoinFetcher:
    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        raise NotImplementedError("Kucoin fetcher باید توسعه داده شود.")

class GateioFetcher:
    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        raise NotImplementedError("Gate.io fetcher باید توسعه داده شود.")

class OkxFetcher:
    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        raise NotImplementedError("OKX fetcher باید توسعه داده شود.")

class MexcFetcher:
    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        raise NotImplementedError("MEXC fetcher باید توسعه داده شود.")

class CoinmarketcapFetcher:
    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        raise NotImplementedError("Coinmarketcap fetcher باید توسعه داده شود.")

class BitfinexFetcher:
    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        raise NotImplementedError("Bitfinex fetcher باید توسعه داده شود.")

# Dispatcher
class MultiExchangeFetcher:
    def __init__(self, source: str):
        self.source = source.lower()
        if self.source == "coingecko":
            self.fetcher = CoingeckoFetcher()
        elif self.source == "kucoin":
            self.fetcher = KucoinFetcher()
        elif self.source == "gate.io":
            self.fetcher = GateioFetcher()
        elif self.source == "okx":
            self.fetcher = OkxFetcher()
        elif self.source == "mexc":
            self.fetcher = MexcFetcher()
        elif self.source == "coinmarketcap":
            self.fetcher = CoinmarketcapFetcher()
        elif self.source == "bitfinex":
            self.fetcher = BitfinexFetcher()
        else:
            raise ValueError(f"Unknown exchange: {self.source}")

    def fetch_ohlcv(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        فراخوانی fetcher مناسب و بازگرداندن DataFrame استاندارد
        - برای coingecko، symbol باید coin_id باشد (مثلاً 'bitcoin')
        """
        return self.fetcher.fetch_ohlcv(symbol, **kwargs)

# مثال استفاده:
"""
fetcher = MultiExchangeFetcher('coingecko')
df = fetcher.fetch_ohlcv('bitcoin', vs_currency='usd', days=30, interval='hourly')
print(df.head())
"""

