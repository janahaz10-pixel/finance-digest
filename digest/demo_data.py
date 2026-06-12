"""Sample pre-simplified articles so you can preview the site without an API key."""

DEMO_ARTICLES = {
    "indian-markets": [
        {
            "id": "demo01", "source": "economictimes.indiatimes.com",
            "title": "Sensex rallies 600 points as FII buying returns",
            "link": "https://example.com/demo", "published": "Fri, 12 Jun 2026",
            "quick_take": "Indian stocks jumped today because big foreign investors started buying again.",
            "simplified_article": "The Sensex, India's main stock market scoreboard, rose about 600 points today. The main reason: foreign institutional investors (big overseas funds) bought Indian shares after weeks of selling. When large investors buy, prices rise because demand goes up. Banking and IT stocks gained the most.",
            "investor_impact": "If you hold Indian mutual funds or stocks, your portfolio likely went up today. One good day doesn't make a trend though - foreign money can leave as quickly as it arrives.",
            "key_terms": [
                {"term": "Sensex", "meaning": "An index tracking 30 of the biggest companies on the Bombay Stock Exchange - a quick health check for Indian markets."},
                {"term": "FII", "meaning": "Foreign Institutional Investor - large overseas funds that invest in Indian markets."},
            ],
        },
        {
            "id": "demo02", "source": "moneycontrol.com",
            "title": "Nifty Midcap index hits record high amid retail inflows",
            "link": "https://example.com/demo", "published": "Fri, 12 Jun 2026",
            "quick_take": "Mid-sized company stocks hit an all-time high, driven by ordinary investors putting in money via SIPs.",
            "simplified_article": "The index that tracks mid-sized Indian companies reached its highest level ever. The push is coming from regular people investing monthly through SIPs in mutual funds. Fund managers receiving that money keep buying midcap shares, lifting prices. Some analysts worry prices are now expensive compared to company earnings.",
            "investor_impact": "Midcap funds have done well lately, but record highs plus 'expensive valuations' warnings mean future returns could be lower. Diversification matters more when one segment gets this hot.",
            "key_terms": [
                {"term": "Midcap", "meaning": "Medium-sized companies - bigger than small startups, smaller than giants like Reliance."},
                {"term": "SIP", "meaning": "Systematic Investment Plan - investing a fixed amount into a mutual fund every month."},
                {"term": "Valuation", "meaning": "What a stock costs relative to what the company actually earns - 'expensive' means you pay a lot per rupee of profit."},
            ],
        },
    ],
    "us-global": [
        {
            "id": "demo03", "source": "cnbc.com",
            "title": "Fed holds rates steady, signals patience on cuts",
            "link": "https://example.com/demo", "published": "Fri, 12 Jun 2026",
            "quick_take": "The US central bank kept interest rates unchanged and said it's in no hurry to cut them.",
            "simplified_article": "The Federal Reserve, America's central bank, decided to leave interest rates where they are. Markets had hoped for a signal that cheaper borrowing was coming soon, but the Fed said it wants to see inflation fall further first. Stock markets dipped slightly on the news, since higher rates for longer makes borrowing costlier for companies.",
            "investor_impact": "US rate decisions ripple worldwide - they affect everything from tech stock prices to how much foreign money flows into markets like India. 'Higher for longer' usually means more cautious markets.",
            "key_terms": [
                {"term": "Federal Reserve (Fed)", "meaning": "The US central bank - it sets the base interest rate for the world's largest economy."},
                {"term": "Rate cut", "meaning": "When a central bank lowers interest rates, making loans cheaper and usually boosting stocks."},
            ],
        },
    ],
    "banking-economy": [
        {
            "id": "demo04", "source": "livemint.com",
            "title": "RBI keeps repo rate unchanged; inflation forecast trimmed",
            "link": "https://example.com/demo", "published": "Fri, 12 Jun 2026",
            "quick_take": "India's central bank left its key lending rate unchanged but expects inflation to ease.",
            "simplified_article": "The Reserve Bank of India kept the repo rate - the rate at which it lends to banks - unchanged. It also lowered its inflation forecast, meaning it expects prices to rise more slowly than before. If inflation keeps cooling, the RBI gets room to cut rates later, which would make home and car loans cheaper.",
            "investor_impact": "No immediate change to your loan EMIs. But a lower inflation forecast raises the odds of rate cuts ahead - good news for borrowers and often for stock markets too.",
            "key_terms": [
                {"term": "Repo rate", "meaning": "The interest rate at which the RBI lends money to commercial banks - it influences all other interest rates in the economy."},
                {"term": "Inflation", "meaning": "The rate at which everyday prices rise. Lower inflation means your money keeps its buying power longer."},
            ],
        },
    ],
    "sectors": [
        {
            "id": "demo05", "source": "economictimes.indiatimes.com",
            "title": "EV sales cross 10% of total auto sales for first time",
            "link": "https://example.com/demo", "published": "Fri, 12 Jun 2026",
            "quick_take": "Electric vehicles now make up over 10% of all vehicles sold in India - a first.",
            "simplified_article": "For the first time, more than one in ten vehicles sold in India was electric. Cheaper batteries, more charging stations, and government incentives are driving the shift. Traditional carmakers are racing to launch electric models while EV-focused companies are scaling up production.",
            "investor_impact": "The auto sector is splitting into EV winners and laggards. Companies slow to adapt may lose market share, while battery makers and charging firms form an emerging investment theme.",
            "key_terms": [
                {"term": "EV", "meaning": "Electric Vehicle - runs on batteries instead of petrol or diesel."},
                {"term": "Market share", "meaning": "A company's slice of total sales in its industry."},
            ],
        },
    ],
    "crypto": [
        {
            "id": "demo06", "source": "coindesk.com",
            "title": "Bitcoin steadies near $90K as ETF inflows resume",
            "link": "https://example.com/demo", "published": "Fri, 12 Jun 2026",
            "quick_take": "Bitcoin's price stabilized around $90,000 as money flowed back into Bitcoin investment funds.",
            "simplified_article": "After a volatile month, Bitcoin found stability near $90,000. The calm comes from renewed buying in Bitcoin ETFs - funds that let people invest in Bitcoin through a normal brokerage account without owning the coin directly. Steady ETF inflows often signal that bigger, institutional investors are buying.",
            "investor_impact": "Crypto remains the most volatile mainstream asset - stability today guarantees nothing. ETFs have made it easier to get exposure, but the swings are just as wild either way.",
            "key_terms": [
                {"term": "ETF", "meaning": "Exchange-Traded Fund - a fund you can buy like a stock; a Bitcoin ETF tracks Bitcoin's price."},
                {"term": "Volatility", "meaning": "How wildly a price swings up and down. High volatility means big gains AND big losses are possible."},
            ],
        },
    ],
}
