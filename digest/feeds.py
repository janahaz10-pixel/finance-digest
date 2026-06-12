"""Feed configuration: category -> list of RSS feeds.

Add/remove feeds freely. Dead feeds are skipped automatically at runtime.
"""

CATEGORIES = {
    "indian-markets": {
        "label": "Indian Markets",
        "emoji": "\U0001F1EE\U0001F1F3",
        "feeds": [
            "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
            "https://www.moneycontrol.com/rss/marketreports.xml",
            "https://www.livemint.com/rss/markets",
        ],
        "max_articles": 8,
    },
    "us-global": {
        "label": "US & Global Markets",
        "emoji": "\U0001F30E",
        "feeds": [
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        ],
        "max_articles": 8,
    },
    "banking-economy": {
        "label": "Banking & Economy",
        "emoji": "\U0001F3E6",
        "feeds": [
            "https://economictimes.indiatimes.com/industry/banking/finance/rssfeeds/13358259.cms",
            "https://www.moneycontrol.com/rss/economy.xml",
            "https://www.livemint.com/rss/economy",
        ],
        "max_articles": 8,
    },
    "sectors": {
        "label": "Sectors",
        "emoji": "\U0001F3ED",
        "feeds": [
            "https://economictimes.indiatimes.com/industry/auto/rssfeeds/13359412.cms",
            "https://economictimes.indiatimes.com/industry/healthcare/biotech/rssfeeds/13358050.cms",
            "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
            "https://economictimes.indiatimes.com/industry/energy/rssfeeds/13358361.cms",
        ],
        "max_articles": 8,
    },
    "crypto": {
        "label": "Crypto",
        "emoji": "\U0001FA99",
        "feeds": [
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cointelegraph.com/rss",
        ],
        "max_articles": 8,
    },
}
