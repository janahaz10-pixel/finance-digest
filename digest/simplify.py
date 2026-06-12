"""Turn raw articles into the 4-point beginner-friendly format via the Claude API."""
import json
import os
import re
import time
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("DIGEST_MODEL", "claude-haiku-4-5-20251001")

PROMPT = """You write for absolute beginners learning about financial markets.

Here is a news item:
Title: {title}
Source: {source}
Summary: {summary}

Rewrite it in plain, jargon-free language. Respond with ONLY a JSON object, no markdown fences:
{{
  "quick_take": "<what happened, ONE short sentence>",
  "simplified_article": "<the story retold in 3-5 short, plain sentences a beginner can follow. Explain cause and effect simply. No jargon.>",
  "investor_impact": "<what this actually means for an ordinary investor, 1-3 plain sentences. Be concrete, not generic. Never give buy/sell advice.>",
  "key_terms": [{{"term": "<jargon word from the story>", "meaning": "<one-line plain explanation>"}}]
}}

Rules:
- key_terms: 1-4 terms actually present in or central to the story; if none, return [].
- Write at the reading level of someone with zero finance background.
- Stick to the facts given; do not invent numbers or details not in the summary.
- investor_impact must be educational context, never a recommendation."""


def _call_claude(prompt, api_key, max_retries=3):
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(API_URL, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r:
                resp = json.loads(r.read())
            return resp["content"][0]["text"]
        except Exception as e:
            wait = 2 ** (attempt + 1)
            print(f"  [retry {attempt+1}] {type(e).__name__}: {e} (waiting {wait}s)")
            time.sleep(wait)
    return None


def _parse_json(text):
    """Tolerant JSON extraction."""
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def simplify_article(article, api_key):
    """Returns article dict enriched with the 4 points, or None on failure."""
    prompt = PROMPT.format(
        title=article["title"],
        source=article["source"],
        summary=article["summary"] or "(no summary available - work from the title)",
    )
    parsed = _parse_json(_call_claude(prompt, api_key))
    if not parsed or "quick_take" not in parsed:
        print(f"  [fail] {article['title'][:50]}")
        return None
    article.update({
        "quick_take": str(parsed.get("quick_take", "")).strip(),
        "simplified_article": str(parsed.get("simplified_article", "")).strip(),
        "investor_impact": str(parsed.get("investor_impact", "")).strip(),
        "key_terms": [
            {"term": str(t.get("term", "")).strip(), "meaning": str(t.get("meaning", "")).strip()}
            for t in parsed.get("key_terms", []) if isinstance(t, dict) and t.get("term")
        ][:4],
    })
    return article


def simplify_all(articles_by_cat):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY is not set")
    out = {}
    for cat, articles in articles_by_cat.items():
        print(f"[simplify] {cat} ({len(articles)} articles)")
        done = []
        for a in articles:
            result = simplify_article(a, api_key)
            if result:
                done.append(result)
            time.sleep(0.3)
        out[cat] = done
    return out
