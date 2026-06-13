"""Orchestrator. Usage:
    python -m digest.run            # full run (uses GitHub Models or Claude API)
    python -m digest.run --demo    # offline demo with bundled sample data
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

from .feeds import CATEGORIES
from .build import build_site

SITE_DIR  = "site"
DATA_DIR  = "data"
SITE_NAME = "My Finance Digest"
IST       = timezone(timedelta(hours=5, minutes=30))

_YF_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def fetch_market_data():
    """Fetch Nifty 50, Sensex, USD/INR, BTC at build time from Yahoo Finance.

    Returns a dict like:
      {"nifty": {"price": 22456.0, "change_pct": 1.23}, ...}
    Any symbol that fails returns None for that key.
    """
    symbols = {
        "nifty":  "^NSEI",
        "sensex": "^BSESN",
        "usdinr": "USDINR=X",
        "btcusd": "BTC-USD",
    }
    results = {}
    for name, symbol in symbols.items():
        try:
            url = (
                f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                f"?interval=1d&range=1d"
            )
            req = urllib.request.Request(url, headers=_YF_HEADERS)
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read())
            meta   = data["chart"]["result"][0]["meta"]
            price  = float(meta.get("regularMarketPrice") or 0)
            prev   = float(meta.get("chartPreviousClose") or price)
            change = ((price - prev) / prev * 100) if prev else 0.0
            results[name] = {"price": price, "change_pct": change}
            print(f"[market] {name}: {price:.2f} ({change:+.2f}%)")
            time.sleep(0.5)
        except Exception as e:
            print(f"[market] {name}: failed — {e}")
            results[name] = None
    return results


def main():
    demo = "--demo" in sys.argv
    now  = datetime.now(IST)

    if demo:
        from .demo_data import DEMO_ARTICLES
        articles    = DEMO_ARTICLES
        market_data = {}
        day_summary = ""
        print("[demo] using bundled sample articles (no network / API)")
    else:
        from .fetch    import fetch_all
        from .simplify import simplify_all, pick_engine, generate_day_summary

        # 1. Fetch & simplify articles
        engine, cred, pace = pick_engine()
        articles = simplify_all(fetch_all(CATEGORIES))

        # 2. Fetch live market prices
        print("[market] fetching market data...")
        market_data = fetch_market_data()

        # 3. Generate the "Today at a glance" summary
        print("[summary] generating day summary...")
        day_summary = generate_day_summary(articles, engine, cred)
        if pace:
            time.sleep(pace)  # pace after extra LLM call

    total = sum(len(v) for v in articles.values())
    if total == 0:
        raise SystemExit(
            "No articles produced -- aborting so yesterday's site isn't overwritten."
        )

    data = {
        "date":        now.strftime("%Y-%m-%d"),
        "date_label":  now.strftime("%A, %d %B %Y"),
        "generated_at": now.isoformat(),
        "articles":    articles,
        "market_data": market_data,
        "day_summary": day_summary,
    }
    build_site(data, CATEGORIES, SITE_DIR, DATA_DIR, SITE_NAME)
    print(f"[done] {total} articles across {len(articles)} categories")


if __name__ == "__main__":
    main()
