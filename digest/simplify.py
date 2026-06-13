"""Turn raw articles into the 4-point beginner format.

Engine priority:
  1. Claude API        - if ANTHROPIC_API_KEY is set (best quality)
  2. GitHub Models     - free, uses the GITHUB_TOKEN automatically present
                         in GitHub Actions (no cost, rate-limited)
  3. Plain fallback    - article passes through un-simplified (site still publishes)
"""
import json
import os
import re
import time
import urllib.request

CLAUDE_URL   = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = os.environ.get("DIGEST_MODEL", "claude-haiku-4-5-20251001")
GH_URL       = "https://models.github.ai/inference/chat/completions"
GH_MODEL     = os.environ.get("GITHUB_MODEL", "openai/gpt-4o-mini")

PROMPT = """You simplify financial news for people with zero finance background.

News item:
Title: {title}
Source: {source}
Summary: {summary}

Respond with ONLY a valid JSON object -- no markdown fences, no extra text:
{{
  "quick_take": "<ONE punchy sentence: WHAT happened + WHY it matters. If a specific number/company/country is in the story, it MUST appear here. Write like a smart friend texting you -- clear, specific, no jargon. Bad: 'Markets moved on policy news.' Good: 'RBI held rates at 6.5% for the 8th time, signalling it still fears inflation despite slowing growth.'>",

  "simplified_article": "<The full story in 4-6 short sentences. Follow this structure: (1) what happened, (2) why it happened / what caused it, (3) relevant background in one sentence, (4-6) what happens next and who is affected. If you must use a technical term, immediately explain it in plain brackets like: 'repo rate [the interest rate at which RBI lends money to banks]'. Write at the level of a smart 16-year-old who reads the news but has never studied finance.>",

  "investor_impact": "<2-3 sentences that directly answer: 'So what does this mean for MY money?' Be concrete -- name the sectors, asset types, or categories of people affected. Examples of the specificity required: 'This could push home loan EMIs up by Rs 500-800/month on a Rs 50 lakh loan.' or 'Tech stocks, especially IT exporters like TCS and Infosys, benefit when the rupee weakens.' or 'Gold prices typically rise during uncertainty -- this is relevant if you hold gold ETFs or sovereign gold bonds.' Never give buy/sell advice. Avoid empty phrases like 'markets may react' or 'investors should watch'.>",

  "key_terms": [
    {{"term": "<jargon word from the story>", "meaning": "<one plain sentence -- what it is and why it matters in this context>"}}
  ]
}}

Strict rules:
- quick_take: must include a specific figure, name, or percentage if the story has one
- simplified_article: never use a jargon word without explaining it immediately
- investor_impact: must be specific to this story -- not generic market commentary
- key_terms: 2-4 terms maximum, only if genuinely technical and present in the story; return [] if none
- Never invent numbers or facts not present in the title/summary
- Never say 'consult a financial advisor' or give buy/sell recommendations"""

DAY_SUMMARY_PROMPT = """You are writing the opening paragraph for a daily financial news digest aimed at everyday Indian investors and savers.

Today's key headlines:
{headlines}

Write 2-3 sentences summarising today's most important financial developments.
Requirements:
- Lead with the single biggest story of the day
- Weave in 1-2 other notable themes or developments
- Sound like a smart, warm friend catching you up over coffee -- clear and vivid, zero jargon
- Include specific names, numbers, or percentages where they add meaning
- Do NOT open with "Today", "In today's digest", or any meta-phrase about the newsletter
- Do NOT use bullet points -- write flowing prose

Respond with ONLY the summary text, nothing else."""


def _post_json(url, body, headers, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _call_claude(prompt, api_key):
    resp = _post_json(CLAUDE_URL, {
        "model": CLAUDE_MODEL, "max_tokens": 1200,
        "messages": [{"role": "user", "content": prompt}],
    }, {
        "x-api-key": api_key, "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    return resp["content"][0]["text"]


def _call_github_models(prompt, token):
    resp = _post_json(GH_URL, {
        "model": GH_MODEL, "max_tokens": 1200,
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
            wait = 5 * 2 ** attempt
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
    """No AI available -- publish un-simplified so the site still works."""
    article.update({
        "quick_take": article["title"],
        "simplified_article": article["summary"] or article["title"],
        "investor_impact": (
            "AI simplification wasn't available for this story -- "
            "the original article below has the full picture."
        ),
        "key_terms": [],
    })
    return article


def simplify_article(article, engine, cred):
    if engine == "none":
        return _plain_fallback(article)
    prompt = PROMPT.format(
        title=article["title"],
        source=article["source"],
        summary=article["summary"] or "(no summary available -- work from the title only)",
    )
    parsed = _parse_json(_call_llm(prompt, engine, cred))
    if not parsed or "quick_take" not in parsed:
        print(f"  [fallback to plain] {article['title'][:55]}")
        return _plain_fallback(article)
    article.update({
        "quick_take":         str(parsed.get("quick_take", "")).strip(),
        "simplified_article": str(parsed.get("simplified_article", "")).strip(),
        "investor_impact":    str(parsed.get("investor_impact", "")).strip(),
        "key_terms": [
            {
                "term":    str(t.get("term", "")).strip(),
                "meaning": str(t.get("meaning", "")).strip(),
            }
            for t in parsed.get("key_terms", [])
            if isinstance(t, dict) and t.get("term")
        ][:4],
    })
    return article


def generate_day_summary(articles_by_cat, engine, cred):
    """Generate a 2-3 sentence 'what happened today' summary across all categories."""
    all_takes = [
        a["quick_take"]
        for arts in articles_by_cat.values()
        for a in arts
        if a.get("quick_take") and len(a["quick_take"]) > 20
    ]
    if not all_takes or engine == "none":
        return ""
    headlines = "\n".join(f"- {t}" for t in all_takes[:22])
    result = _call_llm(DAY_SUMMARY_PROMPT.format(headlines=headlines), engine, cred)
    return result.strip() if result else ""


def pick_engine():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude", os.environ["ANTHROPIC_API_KEY"], 0.3
    if os.environ.get("GITHUB_TOKEN"):
        return "github", os.environ["GITHUB_TOKEN"], 6.0
    print("[warn] no ANTHROPIC_API_KEY or GITHUB_TOKEN -- publishing plain summaries")
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
