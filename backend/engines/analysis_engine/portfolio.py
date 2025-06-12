"""
portfolio.py

ماژول مدیریت پرتفوی و مانیتورینگ سود/زیان:
- نگهداری لیست پوزیشن‌ها و معاملات باز/بسته
- محاسبه PnL (سود/زیان تحقق‌یافته و تحقق‌نیافته)
- مانیتورینگ ریسک تجمعی و Exposure بر اساس نماد و تایم‌فریم
- گزارش‌دهی حرفه‌ای، پشتیبانی مولتی‌اکانت
- توسعه‌پذیر برای مدیریت پیشرفته پورتفوی و الگوریتمیک

Author: farbodbod1990
"""

import pandas as pd
from typing import List, Dict, Any, Optional

class Portfolio:
    def __init__(self):
        self.positions = []  # لیست پوزیشن‌های باز
        self.trades = []     # تاریخچه معاملات بسته‌شده

    def open_position(self, symbol: str, entry: float, size: float, sl: Optional[float]=None, tp: Optional[float]=None, t_open: Optional[str]=None):
        pos = {
            'symbol': symbol,
            'entry': entry,
            'size': size,
            'sl': sl,
            'tp': tp,
            't_open': t_open,
            't_close': None,
            'exit': None,
            'status': 'open'
        }
        self.positions.append(pos)

    def close_position(self, idx: int, exit_price: float, t_close: Optional[str]=None):
        if 0 <= idx < len(self.positions) and self.positions[idx]['status'] == 'open':
            pos = self.positions[idx]
            pos['exit'] = exit_price
            pos['t_close'] = t_close
            pos['status'] = 'closed'
            pnl = (exit_price - pos['entry']) * pos['size']
            pos['pnl'] = pnl
            self.trades.append(pos)
            self.positions[idx] = pos

    def unrealized_pnl(self, price_dict: Dict[str, float]) -> float:
        pnl = 0
        for pos in self.positions:
            if pos['status'] == 'open' and pos['symbol'] in price_dict:
                pnl += (price_dict[pos['symbol']] - pos['entry']) * pos['size']
        return pnl

    def total_realized_pnl(self) -> float:
        return sum([p.get('pnl', 0) for p in self.trades])

    def exposure_by_symbol(self) -> Dict[str, float]:
        exp = {}
        for pos in self.positions:
            if pos['status'] == 'open':
                exp[pos['symbol']] = exp.get(pos['symbol'], 0) + pos['size']
        return exp

    def risk_snapshot(self, price_dict: Dict[str, float]) -> Dict[str, Any]:
        return {
            'open_positions': len([p for p in self.positions if p['status'] == 'open']),
            'unrealized_pnl': self.unrealized_pnl(price_dict),
            'realized_pnl': self.total_realized_pnl(),
            'exposure': self.exposure_by_symbol()
        }

    def report(self, price_dict: Dict[str, float]) -> Dict[str, Any]:
        df_open = pd.DataFrame([p for p in self.positions if p['status'] == 'open'])
        df_closed = pd.DataFrame(self.trades)
        snapshot = self.risk_snapshot(price_dict)
        return {
            'open_positions': df_open,
            'closed_trades': df_closed,
            'snapshot': snapshot
        }

# مثال استفاده:
"""
portfolio = Portfolio()
portfolio.open_position('BTCUSDT', entry=35000, size=0.1, sl=34000, tp=37000, t_open='2025-06-12 18:00')
portfolio.open_position('ETHUSDT', entry=1900, size=0.5, sl=1800, tp=2100, t_open='2025-06-12 19:00')
portfolio.close_position(0, exit_price=36000, t_close='2025-06-12 20:00')
prices = {'BTCUSDT': 35900, 'ETHUSDT': 1920}
report = portfolio.report(prices)
print(report['snapshot'])
print(report['open_positions'])
print(report['closed_trades'])
"""
