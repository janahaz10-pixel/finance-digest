"""Orchestrator. Usage:
    python -m digest.run            # full run (needs ANTHROPIC_API_KEY)
    python -m digest.run --demo    # offline demo with sample data (no key needed)
"""
import sys
from datetime import datetime, timezone, timedelta

from .feeds import CATEGORIES
from .build import build_site

SITE_DIR = "site"
DATA_DIR = "data"
SITE_NAME = "My Finance Digest"   # rename to whatever you like
IST = timezone(timedelta(hours=5, minutes=30))


def main():
    demo = "--demo" in sys.argv
    now = datetime.now(IST)
    if demo:
        from .demo_data import DEMO_ARTICLES
        articles = DEMO_ARTICLES
        print("[demo] using bundled sample articles (no network / API)")
    else:
        from .fetch import fetch_all
        from .simplify import simplify_all
        articles = simplify_all(fetch_all(CATEGORIES))

    total = sum(len(v) for v in articles.values())
    if total == 0:
        raise SystemExit("No articles produced - aborting so yesterday's site isn't overwritten with an empty page")

    data = {
        "date": now.strftime("%Y-%m-%d"),
        "date_label": now.strftime("%A, %d %B %Y"),
        "generated_at": now.isoformat(),
        "articles": articles,
    }
    build_site(data, CATEGORIES, SITE_DIR, DATA_DIR, SITE_NAME)
    print(f"[done] {total} articles across {len(articles)} categories")


if __name__ == "__main__":
    main()
