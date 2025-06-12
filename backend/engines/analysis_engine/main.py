"""
main.py

ورودی و نقطه شروع ماژول analysis_engine:
- مدیریت اجرای سرویس تحلیل
- هندل ورودی/خروجی (CLI, API, ...)
- اجرای pipeline کامل تحلیل بازار
- لاگ‌گیری و مدیریت خطا

Author: farbodbod1990
"""

import argparse
import logging
from preprocessing import preprocess_ohlcv
from candlestick import analyze as candlestick_analyze
from indicators import calculate_indicators
from trend import analyze_trend
from divergence import detect_divergence

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    return logging.getLogger("analysis_engine")

def run_analysis(data_files, symbols, timeframes):
    logger = setup_logger()
    logger.info(f"شروع تحلیل برای {symbols} در تایم‌فریم {timeframes}")
    # فرض: هر symbol یک فایل داده دارد (csv)
    dfs = {}
    for sym in symbols:
        try:
            dfs[sym] = pd.read_csv(data_files[sym])
        except Exception as e:
            logger.error(f"خطا در خواندن داده {sym}: {e}")
    # --- پیش‌پردازش
    preprocessed = preprocess_ohlcv(dfs, timeframes=timeframes, logger=logger)
    results = {}
    for sym in symbols:
        results[sym] = {}
        for tf in timeframes:
            df = preprocessed[sym][tf]
            results[sym][tf] = {
                "candlestick": candlestick_analyze(df),
                "indicators": calculate_indicators(df),
                "trend": analyze_trend(df),
                "divergence": detect_divergence(df)
            }
    logger.info("پایان تحلیل")
    return results

def main():
    parser = argparse.ArgumentParser(description="Analysis Engine CLI")
    parser.add_argument("--symbols", nargs="+", default=["BTC", "ETH", "XRP", "SOL", "DOGE"])
    parser.add_argument("--timeframes", nargs="+", default=["1m", "5m", "1h"])
    parser.add_argument("--data", type=str, required=True, help="JSON mapping symbol->filepath")
    args = parser.parse_args()

    import json
    data_files = json.loads(args.data)
    results = run_analysis(data_files, args.symbols, args.timeframes)
    print("Analysis Results:")
    print(results)

if __name__ == "__main__":
    main()
