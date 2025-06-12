"""
signal_generator.py

تبدیل خروجی تحلیل‌های تکنیکال و رفتاری به سیگنال قابل اجرا:
- تبدیل الگوهای کلاسیک، رفتار نهنگ، پیوت و ... به سیگنال خرید/فروش/هشدار
- پشتیبانی استراتژی‌های مولتی‌تایم‌فریم (تایید چند تایم‌فریم)
- آماده برای بک‌تست، اتوماسیون و ارسال به تریدر
- توسعه‌پذیر برای افزودن استراتژی‌های پیچیده و هوش مصنوعی

Author: farbodbod1990
"""

from typing import Dict, Any, List

def pattern_to_signal(patterns: Dict[str, Any]) -> List[str]:
    """
    تبدیل خروجی الگوها به سیگنال متنی
    """
    signals = []
    if patterns['double_bottom']:
        signals.append("احتمال رشد (Double Bottom تشخیص داده شد)")
    if patterns['double_top']:
        signals.append("احتمال ریزش (Double Top تشخیص داده شد)")
    if patterns['head_shoulders']:
        signals.append("هشدار برگشت روند (Head & Shoulders)")
    if patterns['triangle_ascending']:
        signals.append("احتمال Breakout صعودی (Ascending Triangle)")
    if patterns['triangle_descending']:
        signals.append("احتمال Breakout نزولی (Descending Triangle)")
    return signals

def whale_to_signal(whale_events: Dict[str, Any]) -> List[str]:
    """
    تبدیل رفتار نهنگ‌ها به سیگنال
    """
    signals = []
    if whale_events['whale_candles']:
        signals.append("ورود پول سنگین (Whale Candle)")
    if whale_events['spoofing']:
        signals.append("احتمال دستکاری قیمت (Spoofing)")
    if whale_events['wash_trading']:
        signals.append("دیده شدن Wash Trading (معاملات مشکوک)")
    return signals

def pivot_to_signal(pivots: Any) -> List[str]:
    """
    تبدیل پیوت و لگ به سیگنال (قابل توسعه)
    """
    signals = []
    if pivots and isinstance(pivots, dict):
        if pivots.get('major_pivot_up'):
            signals.append("پیوت اصلی صعودی")
        if pivots.get('major_pivot_down'):
            signals.append("پیوت اصلی نزولی")
    return signals

def multi_tf_signal(multi_results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    جمع‌بندی سیگنال‌ها از چند تایم‌فریم
    """
    tf_signals = {}
    for tf, res in multi_results.items():
        signals = []
        signals += pattern_to_signal(res['patterns'])
        signals += whale_to_signal(res['whale'])
        signals += pivot_to_signal(res['pivots'])
        tf_signals[tf] = signals
    return tf_signals

def consensus_signal(tf_signals: Dict[str, List[str]]) -> List[str]:
    """
    استخراج سیگنال اجماعی از چند تایم‌فریم (مثلاً وقتی 2 تایم‌فریم موافق باشند)
    """
    from collections import Counter
    all_signals = sum(tf_signals.values(), [])
    counter = Counter(all_signals)
    consensus = [sig for sig, count in counter.items() if count >= 2]
    return consensus

# مثال استفاده:
"""
from multi_timeframe_analysis import MultiTimeframeAnalysis

analysis = MultiTimeframeAnalysis(
    source='coingecko',
    symbol='bitcoin',
    timeframes=['1h', '4h', '1d'],
    fetcher_kwargs={'vs_currency': 'usd', 'days': '30'}
)
multi_results = analysis.run_all()
tf_signals = multi_tf_signal(multi_results)
final = consensus_signal(tf_signals)
print("سیگنال اجماعی:", final)
print("سیگنال هر تایم‌فریم:", tf_signals)
"""
