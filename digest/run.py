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
            with urllib.request.urlopen(req, timeout=1
