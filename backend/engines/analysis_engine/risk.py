"""
risk.py

ماژول مدیریت ریسک و محاسبه اندازه پوزیشن:
- محاسبه پوزیشن سایز بر اساس ریسک، بالانس، stop loss، لوریج
- پشتیبانی compound risk، مدیریت چند پوزیشن همزمان
- شامل ابزارهای حرفه‌ای: Risk/Reward، Kelly Criterion، Max Drawdown
- توسعه‌پذیر برای مدیریت پرتفوی و ریسک گروهی

Author: farbodbod1990
"""

import math
from typing import Dict, Any, List

def calc_position_size(balance: float, risk_pct: float, entry: float, stop: float, leverage: float = 1.0) -> float:
    """
    محاسبه اندازه پوزیشن با توجه به ریسک
    - balance: موجودی اکانت
    - risk_pct: درصد ریسک (مثلاً 0.01 یعنی 1%)
    - entry: قیمت ورود
    - stop: قیمت حد ضرر
    - leverage: لوریج
    """
    risk_amount = balance * risk_pct
    risk_per_unit = abs(entry - stop)
    if risk_per_unit == 0:
        return 0
    position_size = (risk_amount / risk_per_unit) * leverage
    return position_size

def calc_risk_reward(entry: float, stop: float, target: float) -> float:
    """
    نسبت ریسک به پاداش (Risk/Reward Ratio)
    """
    risk = abs(entry - stop)
    reward = abs(target - entry)
    if risk == 0:
        return float('inf')
    return reward / risk

def kelly_criterion(win_rate: float, win_loss_ratio: float) -> float:
    """
    فرمول کِلی برای مدیریت سرمایه
    - win_rate: احتمال برد (مثلاً 0.6)
    - win_loss_ratio: نسبت میانگین سود به زیان
    """
    kelly = win_rate - (1 - win_rate) / win_loss_ratio if win_loss_ratio != 0 else 0
    return max(0, kelly)

def max_drawdown(equity_curve: List[float]) -> float:
    """
    محاسبه بیشترین افت سرمایه (Max Drawdown)
    """
    max_dd = 0
    peak = equity_curve[0]
    for x in equity_curve:
        if x > peak:
            peak = x
        dd = (peak - x) / peak
        if dd > max_dd:
            max_dd = dd
    return max_dd

def advanced_risk_analysis(balance: float, entry: float, stop: float, targets: List[float], risk_pct: float, leverage: float = 1.0, win_rate: float = 0.5) -> Dict[str, Any]:
    """
    آنالیز حرفه‌ای ریسک برای چند تارگت
    """
    analysis = {}
    for target in targets:
        size = calc_position_size(balance, risk_pct, entry, stop, leverage)
        rr = calc_risk_reward(entry, stop, target)
        kelly = kelly_criterion(win_rate, rr)
        analysis[target] = {
            'position_size': size,
            'risk_reward': rr,
            'kelly_fraction': kelly
        }
    return analysis

# مثال استفاده:
"""
balance = 1000
entry = 100
stop = 95
targets = [110, 120]
risk_pct = 0.01
leverage = 2
win_rate = 0.6
res = advanced_risk_analysis(balance, entry, stop, targets, risk_pct, leverage, win_rate)
print(res)
"""
