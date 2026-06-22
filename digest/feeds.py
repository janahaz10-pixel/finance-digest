"""Feed configuration: category -> list of RSS feeds.

Add/remove feeds freely. Dead feeds are skipped automatically at runtime.
"""

CATEGORIES = {
    "india-macro": {
        "label": "India Macro & Economy",
        "emoji": "\U0001F1EE\U0001F1F3",
        "feeds": [
            # ET Economy (policy, GDP, inflation, trade)
            "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
            # ET Finance & Budget
            "https://economictimes.indiatimes.com/news/economy/finance/rssfeeds/1378272861.cms",
            # Business Standard Economy & Policy
            "https://www.business-standard.com/rss/economy-policy-10601.rss",
            # LiveMint Economy
            "https://www.livemint.com/rss/economy",
            # Financial Express Economy
            "https://www.financialexpress.com/economy/feed/",
            # MoneyControl Economy
            "https://www.moneycontrol.com/rss/economy.xml",
        ],
        "max_articles": 8,
    },
    "indian-markets": {
        "label": "Indian Markets",
        "emoji": "\U0001F4C8",
        "feeds": [
            # ET Markets (stocks, IPOs, FII/DII flows)
            "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
            # ET Stocks
            "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
            # Business Standard Markets
            "https://www.business-standard.com/rss/markets-106.rss",
            # LiveMint Markets
            "https://www.livemint.com/rss/markets",
            # MoneyControl Markets
            "https://www.moneycontrol.com/rss/marketreports.xml",
            # Financial Express Markets
            "https://www.financialexpress.com/market/feed/",
        ],
        "max_articles": 8,
    },
    "global-macro": {
        "label": "Global Macro",
        "emoji": "\U0001F30D",
        "feeds": [
            # Reuters Business & Economy (Fed, ECB, macro data)
            "https://feeds.reuters.com/reuters/businessNews",
            # BBC Business (global economic events)
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            # The Guardian Business
            "https://www.theguardian.com/business/rss",
            # CNBC Economy (US macro, Fed, jobs, inflation)
            "https://www.cnbc.com/id/20910258/device/rss/rss.html",
            # Al Jazeera Economy & Business
            "https://www.aljazeera.com/xml/rss/all.xml",
        ],
        "max_articles": 8,
    },
    "us-global": {
        "label": "US & Global Markets",
        "emoji": "\U0001F30E",
        "feeds": [
            # CNBC Markets
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            # MarketWatch Top Stories
            "https://feeds.content.dowjones.io/public/rss/mw_topstories",
            # MarketWatch Markets
            "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
            # Investopedia News
            "https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=rss_headline",
        ],
        "max_articles": 8,
    },
    "banking-economy": {
        "label": "Banking & Finance",
        "emoji": "\U0001F3E6",
        "feeds": [
            # ET Banking & Finance
            "https://economictimes.indiatimes.com/industry/banking/finance/rssfeeds/13358259.cms",
            # ET NBFCs & Insurance
            "https://economictimes.indiatimes.com/industry/banking/finance/banking/rssfeeds/13358261.cms",
            # Business Standard Finance
            "https://www.business-standard.com/rss/finance-10304.rss",
            # LiveMint Money
            "https://www.livemint.com/rss/money",
            # MoneyControl Economy
            "https://www.moneycontrol.com/rss/economy.xml",
        ],
        "max_articles": 8,
    },
    "sectors": {
        "label": "Sectors",
        "emoji": "\U0001F3ED",
        "feeds": [
            # IT & Technology
            "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
            # Pharma & Healthcare
            "https://economictimes.indiatimes.com/industry/healthcare/biotech/rssfeeds/13358050.cms",
            # Auto & EV
            "https://economictimes.indiatimes.com/industry/auto/rssfeeds/13359412.cms",
            # Energy & Power
            "https://economictimes.indiatimes.com/industry/energy/rssfeeds/13358361.cms",
            # FMCG & Consumer Products
            "https://economictimes.indiatimes.com/industry/cons-products/rssfeeds/13358902.cms",
            # Real Estate & Construction
            "https://economictimes.indiatimes.com/industry/services/property-/-cstruction/rssfeeds/13360437.cms",
            # Metals & Mining
            "https://economictimes.indiatimes.com/industry/indl-goods/svs/metals-mining/rssfeeds/13358269.cms",
            # Telecom
            "https://economictimes.indiatimes.com/industry/telecom/rssfeeds/13357713.cms",
            # Infrastructure
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
