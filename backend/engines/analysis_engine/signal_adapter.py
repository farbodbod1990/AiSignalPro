"""
signal_adapter.py

Adapter ترکیبی برای تولید سیگنال نهایی پروژه:
- ترکیب خروجی AI Engine، موتور تحلیل تکنیکال و موتور سیگنال‌دهی
- منطق اجماع، رأی‌گیری، وزن‌دهی و ساخت خروجی استاندارد برای داشبورد/ربات/مدیریت معاملات
- توسعه‌پذیر و قابل شخصی‌سازی برای هر استراتژی ترکیبی

Author: farbodbod1990
"""

from typing import Dict, Any, List, Optional

class SignalAdapter:
    def __init__(self,
                 ai_output: Dict[str, Any],
                 analytics_output: Dict[str, Any],
                 signal_output: Optional[Dict[str, Any]] = None,
                 weights: Dict[str, float] = {"ai": 0.5, "analytics": 0.5}):
        """
        ai_output: خروجی موتور هوش مصنوعی
        analytics_output: خروجی موتور تحلیل تکنیکال
        signal_output: خروجی موتور سیگنال‌دهی (در صورت نیاز به ترکیب سه‌گانه)
        weights: وزن هر موتور در صدور سیگنال
        """
        self.ai = ai_output
        self.analytics = analytics_output
        self.signal = signal_output
        self.weights = weights

    def combine(self) -> Dict[str, Any]:
        """
        ترکیب خروجی‌ها و تولید سیگنال نهایی ساختاریافته
        """
        # منطق اجماع و رأی‌گیری (قابل توسعه)
        ai_sig = self.ai.get("signal")
        an_sig = self.analytics.get("signal")
        ai_conf = self.ai.get("confidence", 0)
        an_conf = self.analytics.get("confidence", 0)
        ai_score = self.ai.get("ai_score", 0)
        reasons = self.ai.get("reasons", []) + self.analytics.get("reasons", [])

        # منطق ترکیبی: فقط اگر هر دو موتور BUY (یا SELL) باشند سیگنال معتبر صادر شود، وگرنه HOLD
        if ai_sig == an_sig and ai_sig in ["buy", "sell"]:
            final_signal = ai_sig
            confidence = self.weights["ai"] * ai_conf + self.weights["analytics"] * an_conf
            ai_score = ai_score
        else:
            final_signal = "hold"
            confidence = min(ai_conf, an_conf) * 0.5
            ai_score = 0

        # ترکیب سایر فیلدها (ورودی، تارگت و ...)
        entry_zone = self.ai.get("entry_zone", []) or self.analytics.get("entry_zone", [])
        targets = self.ai.get("targets", []) or self.analytics.get("targets", [])
        stop_loss = self.ai.get("stop_loss") or self.analytics.get("stop_loss")
        rr_ratio = self.analytics.get("risk_reward") or "-"
        support = self.analytics.get("support_levels", [])
        resistance = self.analytics.get("resistance_levels", [])
        explanation = (
            f"سیگنال {final_signal.upper()} با اجماع AI و تحلیل: "
            + " | ".join(self.ai.get("explanation", "").split("\n") + self.analytics.get("explanation", "").split("\n"))
        )

        # فرمت نهایی استاندارد برای داشبورد/ربات
        signal_obj = {
            "symbol": self.ai.get("symbol") or self.analytics.get("symbol"),
            "signal_type": final_signal,
            "timeframe": self.ai.get("timeframe") or self.analytics.get("timeframe"),
            "current_price": self.ai.get("current_price") or self.analytics.get("current_price"),
            "entry_zone": entry_zone,
            "targets": targets,
            "stop_loss": stop_loss,
            "risk_reward": rr_ratio,
            "support_levels": support,
            "resistance_levels": resistance,
            "accuracy": self.analytics.get("accuracy", "-"),
            "confidence": confidence,
            "ai_score": ai_score,
            "valid_until": self.ai.get("valid_until") or self.analytics.get("valid_until"),
            "issued_at": self.ai.get("issued_at") or self.analytics.get("issued_at"),
            "reasons": reasons,
            "explanation": explanation
        }
        return signal_obj

# مثال استفاده:
"""
from ai_engine import AIEngine
from analytics_engine import AnalyticsEngine

ai = AIEngine({...})
an = AnalyticsEngine({...})
ai_output = ai.infer()
an_output = an.analyze()

adapter = SignalAdapter(ai_output, an_output)
final_signal = adapter.combine()
print(final_signal)
"""
