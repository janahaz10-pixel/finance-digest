# My Finance Digest

A self-updating financial news site for beginners. Every day it pulls top stories
from ET, Moneycontrol, LiveMint, CNBC, BBC, MarketWatch, CoinDesk and Cointelegraph,
then uses the Claude API to rewrite each one into four beginner-friendly parts:

- **Quick Take** — what happened, in one line
- **The Story, Simply** — the article retold in plain language
- **What This Means For Investors** — the real implication, no advice
- **Key Terms** — jargon explained inline

Covers Indian markets, US/global markets, banking & economy, sectors, and crypto.
Runs entirely free on GitHub Actions + GitHub Pages. Only cost is the Claude API
(~$1–3/month with Haiku at ~25 articles/day).

## Try it locally first (no API key needed)

```bash
python -m digest.run --demo
```

Open `site/index.html` in your browser to see the site with sample articles.

## Deploy (one-time setup, ~10 minutes)

1. **Create a GitHub repo** and push this folder to it:
   ```bash
   git init && git add . && git commit -m "initial"
   git remote add origin https://github.com/YOUR_USERNAME/finance-digest.git
   git push -u origin main
   ```

2. **Get a Claude API key** at https://console.anthropic.com → API Keys.

3. **Add the key as a secret**: repo → Settings → Secrets and variables →
   Actions → New repository secret. Name: `ANTHROPIC_API_KEY`, value: your key.

4. **Enable GitHub Pages**: repo → Settings → Pages → Source: **GitHub Actions**.

5. **Run it**: repo → Actions → "Daily Digest" → Run workflow.
   After ~3 minutes your site is live at `https://YOUR_USERNAME.github.io/finance-digest/`.

From then on it refreshes itself daily at 6:15 PM IST automatically.

## Customize

| What | Where |
|---|---|
| Site name | `SITE_NAME` in `digest/run.py` |
| Add/remove news feeds | `digest/feeds.py` |
| Articles per category | `max_articles` in `digest/feeds.py` |
| Update time | `cron` in `.github/workflows/daily.yml` (UTC; IST = UTC+5:30) |
| Tone/format of summaries | `PROMPT` in `digest/simplify.py` |
| Claude model | `DIGEST_MODEL` env var (default: Haiku, the cheapest) |
| Look & feel | CSS inside `digest/build.py` |

## Custom domain (optional)

Settings → Pages → Custom domain, then point a CNAME record at
`YOUR_USERNAME.github.io` from your DNS provider.

## How it works

```
GitHub Actions (daily cron)
  └─ digest/fetch.py     pulls RSS feeds, dedupes, caps per category
  └─ digest/simplify.py  one Claude call per article → 4-point JSON
  └─ digest/build.py     renders static HTML (today + archive)
  └─ data/YYYY-MM-DD.json committed back (permanent archive)
  └─ site/ deployed to GitHub Pages
```

No servers, no database, no frameworks — pure Python standard library.

## Notes

- Dead/blocked feeds are skipped automatically; the run never fails because one source is down.
- If zero articles are produced, the run aborts rather than publishing an empty page.
- Summaries link back to the original articles; the site shows only AI-rewritten text, not the original reporting.
- The footer carries an "educational only, not investment advice" disclaimer — keep it.
