"""Feed configuration: category -> list of RSS feeds.

Add/remove feeds freely. Dead feeds are skipped automatically at runtime.
"""

CATEGORIES = {
    "india-macro": {
        "label": "India Macro & Economy",
        "emoji": "\U0001F1EE\U0001F1F3",
        "feeds": [
            "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
            "https://economictimes.indiatimes.com/news/economy/finance/rssfeeds/1378272861.cms",
            "https://www.business-standard.com/rss/economy-policy-10601.rss",
            "https://www.livemint.com/rss/economy",
            "https://www.financialexpress.com/economy/feed/",
            "https://www.moneycontrol.com/rss/economy.xml",
        ],
        "max_articles": 8,
    },
    "indian-markets": {
        "label": "Indian Markets",
        "emoji": "\U0001F4C8",
        "feeds": [
            "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
            "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
            "https://www.business-standard.com/rss/markets-106.rss",
            "https://www.livemint.com/rss/markets",
            "https://www.moneycontrol.com/rss/marketreports.xml",
            "https://www.financialexpress.com/market/feed/",
        ],
        "max_articles": 8,
    },
    "global-macro": {
        "label": "Global Macro",
        "emoji": "\U0001F30D",
        "feeds": [
            "https://feeds.reuters.com/reuters/businessNews",
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://www.theguardian.com/business/rss",
            "https://www.cnbc.com/id/20910258/device/rss/rss.html",
            "https://www.aljazeera.com/xml/rss/all.xml",
        ],
        "max_articles": 8,
    },
    "us-global": {
        "label": "US & Global Markets",
        "emoji": "\U0001F30E",
        "feeds": [
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://feeds.content.dowjones.io/public/rss/mw_topstories",
            "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
            "https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=rss_headline",
        ],
        "max_articles": 8,
    },
    "banking-economy": {
        "label": "Banking & Finance",
        "emoji": "\U0001F3E6",
        "feeds": [
            "https://economictimes.indiatimes.com/industry/banking/finance/rssfeeds/13358259.cms",
            "https://economictimes.indiatimes.com/industry/banking/finance/banking/rssfeeds/13358261.cms",
            "https://www.business-standard.com/rss/finance-10304.rss",
            "https://www.livemint.com/rss/money",
            "https://www.moneycontrol.com/rss/economy.xml",
        ],
        "max_articles": 8,
    },
    "sectors": {
        "label": "Sectors",
        "emoji": "\U0001F3ED",
        "feeds": [
            "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
            "https://economictimes.indiatimes.com/industry/healthcare/biotech/rssfeeds/13358050.cms",
            "https://economictimes.indiatimes.com/industry/auto/rssfeeds/13359412.cms",
            "https://economictimes.indiatimes.com/industry/energy/rssfeeds/13358361.cms",
            "https://economictimes.indiatimes.com/industry/cons-products/rssfeeds/13358902.cms",
            "https://economictimes.indiatimes.com/industry/services/property-/-cstruction/rssfeeds/13360437.cms",
            "https://economictimes.indiatimes.com/industry/indl-goods/svs/metals-mining/rssfeeds/13358269.cms",
            "https://economictimes.indiatimes.com/industry/telecom/rssfeeds/13357713.cms",
            "https://economictimes.indiatimes.com/industry/indl-goods/svs/construction/rssfeeds/13359437.cms",
        ],
        "max_articles": 10,
    },
    "crypto": {
        "label": "Crypto",
        "emoji": "\U0001FA99",
        "feeds": [
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cointelegraph.com/rss",
        ],
        "max_articles": 6,
    },
}
