"""
active_trade_manager.py

مدیریت معاملات فعال هوشمند:
- ثبت، مانیتورینگ و مدیریت معاملات فعال لانگ و شورت
- همکاری زنده با موتور تحلیل، موتور هوش مصنوعی و موتور سیگنال‌دهی
- پایش قیمت، امتیاز AI، وضعیت بازار، نزدیکی به تارگت یا استاپ‌لاس
- ارائه هشدار خروج/ادامه، ثبت دلایل و آرشیو کامل معاملات

Author: farbodbod1990
"""

import time
import pandas as pd
from typing import Dict, Any, List, Optional

class ActiveTrade:
    def __init__(
        self,
        trade_id: str,
        symbol: str,
        timeframe: str,
        signal_obj: Dict[str, Any],
        entry_price: float,
        entry_time: str,
        direction: str,  # 'long' or 'short'
        targets: List[float],
        stop_loss: float,
        support_levels: List[float],
        resistance_levels: List[float],
        ai_score: float,
        reasons: List[str]
    ):
        self.trade_id = trade_id
        self.symbol = symbol
        self.timeframe = timeframe
        self.signal_obj = signal_obj
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.direction = direction
        self.targets = targets
        self.stop_loss = stop_loss
        self.support_levels = support_levels
        self.resistance_levels = resistance_levels
        self.ai_score = ai_score
        self.reasons = reasons
        self.status = "open"  # "open", "closed"
        self.close_price = None
        self.close_time = None
        self.result = None
        self.history = []

    def update_status(self, current_price: float, ai_score: float, analysis_obj: Dict[str, Any]):
        """
        بروزرسانی وضعیت معامله، امتیاز AI و تحلیل
        """
        self.ai_score = ai_score
        # ثبت وضعیت جاری
        status_obj = {
            "time": pd.Timestamp.now(),
            "current_price": current_price,
            "ai_score": ai_score,
            "analysis": analysis_obj,
            "comment": None
        }
        # بررسی رسیدن به تارگت یا استاپ‌لاس
        closed = False
        if self.direction == "long":
            for idx, t in enumerate(self.targets):
                if current_price >= t:
                    self.close_price = t
                    self.close_time = str(pd.Timestamp.now())
                    self.status = "closed"
                    self.result = f"target_{idx+1}"
                    status_obj["comment"] = f"✅ رسیدن به تارگت {idx+1}"
                    closed = True
                    break
            if not closed and current_price <= self.stop_loss:
                self.close_price = self.stop_loss
                self.close_time = str(pd.Timestamp.now())
                self.status = "closed"
                self.result = "stop_loss"
                status_obj["comment"] = "🛑 فعال شدن استاپ‌لاس"
                closed = True
        else:  # short
            for idx, t in enumerate(self.targets):
                if current_price <= t:
                    self.close_price = t
                    self.close_time = str(pd.Timestamp.now())
                    self.status = "closed"
                    self.result = f"target_{idx+1}"
                    status_obj["comment"] = f"✅ رسیدن به تارگت {idx+1}"
                    closed = True
                    break
            if not closed and current_price >= self.stop_loss:
                self.close_price = self.stop_loss
                self.close_time = str(pd.Timestamp.now())
                self.status = "closed"
                self.result = "stop_loss"
                status_obj["comment"] = "🛑 فعال شدن استاپ‌لاس"
                closed = True
        self.history.append(status_obj)

    def manual_close(self, current_price: float):
        """
        بستن دستی معامله توسط کاربر
        """
        self.close_price = current_price
        self.close_time = str(pd.Timestamp.now())
        self.status = "closed"
        self.result = "manual"
        self.history.append({
            "time": pd.Timestamp.now(),
            "current_price": current_price,
            "ai_score": self.ai_score,
            "analysis": {},
            "comment": "🔔 بستن دستی معامله توسط کاربر"
        })

    def get_state(self) -> Dict[str, Any]:
        """
        خروجی کامل وضعیت فعلی معامله
        """
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time,
            "direction": self.direction,
            "targets": self.targets,
            "stop_loss": self.stop_loss,
            "status": self.status,
            "close_price": self.close_price,
            "close_time": self.close_time,
            "result": self.result,
            "ai_score": self.ai_score,
            "reasons": self.reasons,
            "history": self.history
        }

class ActiveTradeManager:
    def __init__(self):
        self.active_trades: Dict[str, ActiveTrade] = {}

    def start_trade(self, signal_obj: Dict[str, Any], entry_price: float, direction: str, entry_time: Optional[str]=None):
        """
        ثبت معامله جدید (ورود کاربر به معامله)
        """
        trade_id = f"{signal_obj['symbol']}_{signal_obj['timeframe']}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
        trade = ActiveTrade(
            trade_id=trade_id,
            symbol=signal_obj["symbol"],
            timeframe=signal_obj["timeframe"],
            signal_obj=signal_obj,
            entry_price=entry_price,
            entry_time=entry_time or str(pd.Timestamp.now()),
            direction=direction,
            targets=signal_obj.get("targets", []),
            stop_loss=signal_obj.get("stop_loss"),
            support_levels=signal_obj.get("support_levels", []),
            resistance_levels=signal_obj.get("resistance_levels", []),
            ai_score=signal_obj.get("ai_score", 0),
            reasons=signal_obj.get("reasons", [])
        )
        self.active_trades[trade_id] = trade
        return trade_id

    def update_all(self, current_prices: Dict[str, float], ai_scores: Dict[str, float], analytics_objs: Dict[str, Any]):
        """
        بروزرسانی همه معاملات فعال (توسط دیتا و تحلیل زنده)
        """
        for trade_id, trade in self.active_trades.items():
            if trade.status == "open":
                price = current_prices.get(trade.symbol, trade.entry_price)
                ai_score = ai_scores.get(trade.symbol, trade.ai_score)
                analytics = analytics_objs.get(trade.symbol, {})
                trade.update_status(price, ai_score, analytics)

    def manual_close_trade(self, trade_id: str, current_price: float):
        """
        بستن دستی یک معامله
        """
        if trade_id in self.active_trades and self.active_trades[trade_id].status == "open":
            self.active_trades[trade_id].manual_close(current_price)

    def get_all_states(self) -> List[Dict[str, Any]]:
        """
        خروجی وضعیت همه معاملات فعال و بسته شده
        """
        return [trade.get_state() for trade in self.active_trades.values()]

# مثال استفاده:
"""
manager = ActiveTradeManager()
trade_id = manager.start_trade(signal_obj, entry_price=65500, direction='long')
# هر دقیقه/ثانیه:
manager.update_all(
    current_prices={'BTCUSDT': 65800},
    ai_scores={'BTCUSDT': 0.91},
    analytics_objs={'BTCUSDT': {'trend': 'bullish'}}
)
state = manager.get_all_states()
print(state)
"""
