"""Turn raw articles into the 4-point beginner format.

Engine priority:
  1. Claude API        - if ANTHROPIC_API_KEY is set (best quality)
  2. GitHub Models     - free, uses the GITHUB_TOKEN automatically present
                         in GitHub Actions (rate-limited but no cost)
  3. Plain fallback    - article passes through un-simplified (site still publishes)
"""
import json
import os
import re
import time
import urllib.request

CLAUDE_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = os.environ.get("DIGEST_MODEL", "claude-haiku-4-5-20251001")
GH_URL = "https://models.github.ai/inference/chat/completions"
GH_MODEL = os.environ.get("GITHUB_MODEL", "openai/gpt-4o-mini")

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


def _post_json(url, body, headers, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _call_claude(prompt, api_key):
    resp = _post_json(CLAUDE_URL, {
        "model": CLAUDE_MODEL, "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }, {
        "x-api-key": api_key, "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    return resp["content"][0]["text"]


def _call_github_models(prompt, token):
    resp = _post_json(GH_URL, {
        "model": GH_MODEL, "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }, {
        "Authorization": f"Bearer {token}", "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
    })
    return resp["choices"][0]["message"]["content"]


def _call_llm(prompt, engine, cred, max_retries=3):
    for attempt in range(max_retries):
        try:
            if engine == "claude":
                return _call_claude(prompt, cred)
            return _call_github_models(prompt, cred)
        except Exception as e:
            wait = 5 * 2 ** attempt  # 5s, 10s, 20s - handles per-minute rate limits
            print(f"  [retry {attempt+1}] {type(e).__name__}: {e} (waiting {wait}s)")
            time.sleep(wait)
    return None


def _parse_json(text):
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _plain_fallback(article):
    """No AI available - publish the story un-simplified rather than not at all."""
    article.update({
        "quick_take": article["title"],
        "simplified_article": article["summary"] or article["title"],
        "investor_impact": "AI simplification wasn't available for this story - "
                           "the original article below has the full picture.",
        "key_terms": [],
    })
    return article


def simplify_article(article, engine, cred):
    if engine == "none":
        return _plain_fallback(article)
    prompt = PROMPT.format(
        title=article["title"], source=article["source"],
        summary=article["summary"] or "(no summary available - work from the title)",
    )
    parsed = _parse_json(_call_llm(prompt, engine, cred))
    if not parsed or "quick_take" not in parsed:
        print(f"  [fallback to plain] {article['title'][:50]}")
        return _plain_fallback(article)
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


def pick_engine():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude", os.environ["ANTHROPIC_API_KEY"], 0.3
    if os.environ.get("GITHUB_TOKEN"):
        # free tier is rate-limited per minute - pace calls ~6s apart
        return "github", os.environ["GITHUB_TOKEN"], 6.0
    print("[warn] no ANTHROPIC_API_KEY or GITHUB_TOKEN - publishing plain summaries")
    return "none", None, 0


def simplify_all(articles_by_cat):
    engine, cred, pace = pick_engine()
    print(f"[simplify] engine: {engine}")
    out = {}
    for cat, articles in articles_by_cat.items():
        print(f"[simplify] {cat} ({len(articles)} articles)")
        done = []
        for a in articles:
            done.append(simplify_article(a, engine, cred))
            if pace:
                time.sleep(pace)
        out[cat] = done
    return out
