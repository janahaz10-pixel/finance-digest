"""Generate the static site from digest JSON data."""
import html
import json
import os

CAT_COLORS = {
    "indian-markets": "#ff7a45",
    "us-global": "#2f9bff",
    "banking-economy": "#9d6bff",
    "sectors": "#00b88a",
    "crypto": "#f4b400",
}
DEFAULT_COLOR = "#2f9bff"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site_name} — {date_label}</title>
<meta name="description" content="Daily financial news, simplified for beginners. No jargon, no finance degree needed.">
<style>
  :root {{
    --muted: #5d6778; --border: #e4e8f0; --accent: #4f6df5; --accent2: #18b2c8;
    --chip-bg: #ffffff; --impact-bg: #ecf8f2; --impact-ink: #0c6e48;
    --term-bg: #fdf4dd; --term-ink: #7a5b00; --shadow: 0 1px 3px rgba(16,24,40,.06);
    --shadow-hover: 0 8px 24px rgba(16,24,40,.10);
  }}
  [data-theme="dark"] {{
    --bg: #0c111d; --bg2: #101727; --card: #161e31; --ink: #eef2fa; --muted: #97a3b8;
    --border: #232d45; --accent: #7b93ff; --accent2: #2dd4bf;
    --chip-bg: #161e31; --impact-bg: #0e2b21; --impact-ink: #5fd6a2;
    --term-bg: #2b2410; --term-ink: #e8c35c; --shadow: 0 1px 3px rgba(0,0,0,.4);
    --shadow-hover: 0 8px 24px rgba(0,0,0,.5);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, sans-serif;
         background: var(--bg); color: var(--ink); line-height: 1.65;
         transition: background .25s, color .25s; }}
  .topbar {{ background: linear-gradient(120deg, var(--accent), var(--accent2)); padding: 2px 0; }}
  header {{ background: var(--card); border-bottom: 1px solid var(--border);
            position: sticky; top: 0; z-index: 20; box-shadow: var(--shadow); }}
  .hwrap {{ max-width: 920px; margin: 0 auto; padding: 14px 18px 0; }}
  .hrow {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
  .brand {{ display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }}
  h1 {{ font-size: 1.45rem; letter-spacing: -0.03em; font-weight: 800; }}
  h1 em {{ font-style: normal; background: linear-gradient(120deg, var(--accent), var(--accent2));
           -webkit-background-clip: text; background-clip: text; color: transparent; }}
  .tagline {{ color: var(--muted); font-size: .82rem; }}
  .hbtns {{ display: flex; gap: 8px; align-items: center; }}
  .btn {{ border: 1px solid var(--border); background: var(--chip-bg); color: var(--ink);
          border-radius: 10px; padding: 6px 12px; font-size: .82rem; font-weight: 600;
          cursor: pointer; text-decoration: none; }}
  .btn:hover {{ border-color: var(--accent); color: var(--accent); }}
  nav {{ display: flex; gap: 8px; overflow-x: auto; padding: 12px 0; scrollbar-width: none; }}
  nav::-webkit-scrollbar {{ display: none; }}
  nav a {{ white-space: nowrap; padding: 6px 14px; border-radius: 999px; text-decoration: none;
           color: var(--muted); font-size: .85rem; font-weight: 650; border: 1px solid var(--border);
           background: var(--chip-bg); display: flex; align-items: center; gap: 7px; }}
  nav a .dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
  nav a:hover {{ color: var(--ink); border-color: currentColor; }}
  main {{ max-width: 920px; margin: 0 auto; padding: 26px 18px 60px; }}
  .datebar {{ display: flex; align-items: center; gap: 10px; margin-bottom: 22px; color: var(--muted);
              font-size: .9rem; }}
  .datebar .live {{ width: 8px; height: 8px; border-radius: 50%; background: #22c55e;
                    box-shadow: 0 0 0 4px rgba(34,197,94,.18); }}
  .datebar b {{ color: var(--ink); font-weight: 700; }}
  section {{ margin-bottom: 40px; }}
  .sechead {{ display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }}
  .sechead .bar {{ width: 5px; height: 22px; border-radius: 3px; }}
  .sechead h2 {{ font-size: 1.18rem; letter-spacing: -0.01em; font-weight: 750; }}
  .count {{ color: var(--muted); font-size: .8rem; font-weight: 700; border: 1px solid var(--border);
            padding: 1px 10px; border-radius: 999px; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px;
           margin-bottom: 14px; overflow: hidden; box-shadow: var(--shadow);
           transition: box-shadow .2s, transform .2s; border-left: 4px solid var(--cat, var(--accent)); }}
  .card:hover {{ box-shadow: var(--shadow-hover); transform: translateY(-1px); }}
  .card summary {{ list-style: none; cursor: pointer; padding: 16px 18px 14px; }}
  .card summary::-webkit-details-marker {{ display: none; }}
  .qt {{ font-size: 1.04rem; font-weight: 680; margin-bottom: 9px; letter-spacing: -0.01em; }}
  .meta {{ font-size: .78rem; color: var(--muted); display: flex; gap: 12px; align-items: center;
           flex-wrap: wrap; }}
  .src {{ border: 1px solid var(--border); padding: 1px 9px; border-radius: 999px; font-weight: 650; }}
  .origlink {{ color: var(--accent); text-decoration: none; font-weight: 700; }}
  .origlink:hover {{ text-decoration: underline; }}
  .hint {{ margin-left: auto; color: var(--muted); font-weight: 600; }}
  details[open] .hint .closed-txt {{ display: none; }}
  details:not([open]) .hint .open-txt {{ display: none; }}
  .body {{ padding: 2px 18px 18px; }}
  .block {{ margin-top: 14px; }}
  .block h4 {{ font-size: .7rem; font-weight: 800; letter-spacing: .09em; text-transform: uppercase;
               color: var(--muted); margin-bottom: 6px; }}
  .block p {{ font-size: .94rem; }}
  .impact {{ background: var(--impact-bg); border-radius: 12px; padding: 12px 15px; }}
  .impact h4, .impact p {{ color: var(--impact-ink); }}
  .impact p {{ opacity: .95; }}
  .terms {{ display: flex; flex-direction: column; gap: 8px; }}
  .term {{ background: var(--term-bg); border-radius: 10px; padding: 9px 14px; font-size: .88rem;
           color: var(--ink); }}
  .term b {{ color: var(--term-ink); }}
  .readorig {{ display: inline-flex; align-items: center; gap: 6px; margin-top: 16px; font-size: .88rem;
               color: #fff; background: linear-gradient(120deg, var(--accent), var(--accent2));
               text-decoration: none; font-weight: 700; padding: 8px 16px; border-radius: 10px; }}
  .readorig:hover {{ opacity: .9; }}
  .empty {{ color: var(--muted); font-size: .9rem; padding: 12px 0; }}
  .disclaimer {{ background: var(--term-bg); color: var(--term-ink); border-radius: 12px;
                 padding: 12px 16px; font-size: .82rem; margin-top: 8px; }}
  footer {{ text-align: center; color: var(--muted); font-size: .8rem; padding: 26px 16px 44px; }}
  footer a {{ color: var(--accent); }}
  @media (max-width: 560px) {{ .tagline {{ display: none; }} h1 {{ font-size: 1.25rem; }} }}
</style>
</head>
<body>
<div class="topbar"></div>
<header><div class="hwrap">
  <div class="hrow">
    <div class="brand"><h1>📰 {site_name_html}</h1><span class="tagline">Financial news, minus the jargon</span></div>
    <div class="hbtns">
      <a class="btn" href="{archive_href}">📅 Archive</a>
      <button class="btn" id="themeBtn" aria-label="Toggle theme">🌙</button>
    </div>
  </div>
  <nav>{nav}</nav>
</div></header>
<main>
  <div class="datebar"><span class="live"></span> Updated daily · <b>{date_label}</b></div>
  {sections}
  <div class="disclaimer">⚠️ Educational content only — nothing here is investment advice. Summaries are AI-generated from public news feeds; always read the linked original article and do your own research.</div>
</main>
<footer>Auto-updates every day · Original reporting belongs to the linked sources</footer>
<script>
  const root = document.documentElement, btn = document.getElementById('themeBtn');
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  function setTheme(t) {{
    root.setAttribute('data-theme', t);
    btn.textContent = t === 'dark' ? '☀️' : '🌙';
    localStorage.setItem('theme', t);
  }}
  setTheme(saved || (prefersDark ? 'dark' : 'light'));
  btn.addEventListener('click', () => setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'));
  // don't toggle the card when clicking the original-article link in the summary
  document.querySelectorAll('summary a').forEach(a => a.addEventListener('click', e => e.stopPropagation()));
</script>
</body>
</html>"""

ARCHIVE_PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site_name} — Archive</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#f5f7fb;
         color:#131a2a; max-width:920px; margin:0 auto; padding:32px 18px; line-height:1.7; }}
  @media (prefers-color-scheme: dark) {{ body {{ background:#0c111d; color:#eef2fa; }} }}
  h1 {{ font-size:1.4rem; margin-bottom:16px; }}
  a {{ color:#4f6df5; text-decoration:none; font-weight:600; }}
  li {{ margin:6px 0; }}
</style></head><body>
<h1>📅 Past digests</h1>
<p><a href="../index.html">← Back to today</a></p>
<ul>{links}</ul>
</body></html>"""


def esc(s):
    return html.escape(str(s or ""))


def render_card(a, color):
    terms = "".join(
        f'<div class="term"><b>{esc(t["term"])}</b> — {esc(t["meaning"])}</div>'
        for t in a.get("key_terms", [])
    )
    terms_block = f'<div class="block"><h4>🔑 Key terms</h4><div class="terms">{terms}</div></div>' if terms else ""
    link = esc(a["link"])
    return f"""<details class="card" style="--cat: {color}">
  <summary>
    <div class="qt">{esc(a["quick_take"])}</div>
    <div class="meta">
      <span class="src">{esc(a["source"])}</span>
      <span>{esc(a.get("published", ""))[:17]}</span>
      <a class="origlink" href="{link}" target="_blank" rel="noopener">Original ↗</a>
      <span class="hint"><span class="closed-txt">Read simply ▾</span><span class="open-txt">Close ▴</span></span>
    </div>
  </summary>
  <div class="body">
    <div class="block"><h4>📖 The story, simply</h4><p>{esc(a["simplified_article"])}</p></div>
    <div class="block impact"><h4>💡 What this means for investors</h4><p>{esc(a["investor_impact"])}</p></div>
    {terms_block}
    <a class="readorig" href="{link}" target="_blank" rel="noopener">Read the original article ↗</a>
  </div>
</details>"""


def render_page(data, categories, site_name, archive_href="archive/index.html"):
    nav, sections = [], []
    for key, cfg in categories.items():
        color = CAT_COLORS.get(key, DEFAULT_COLOR)
        arts = data["articles"].get(key, [])
        nav.append(f'<a href="#{key}"><span class="dot" style="background:{color}"></span>{esc(cfg["label"])}</a>')
        cards = "".join(render_card(a, color) for a in arts) or '<p class="empty">No stories today.</p>'
        sections.append(
            f'<section id="{key}"><div class="sechead"><span class="bar" style="background:{color}"></span>'
            f'<h2>{cfg["emoji"]} {esc(cfg["label"])}</h2><span class="count">{len(arts)} stories</span></div>{cards}</section>'
        )
    name = esc(site_name)
    if " " in name:
        first, rest = name.split(" ", 1)
        name_html = f"{first} <em>{rest}</em>"
    else:
        name_html = f"<em>{name}</em>"
    return PAGE.format(
        site_name=site_name, site_name_html=name_html,
        date_label=esc(data["date_label"]), nav="".join(nav),
        sections="".join(sections), archive_href=archive_href,
    )


def build_site(data, categories, site_dir, data_dir, site_name="My Finance Digest"):
    os.makedirs(site_dir, exist_ok=True)
    os.makedirs(os.path.join(site_dir, "archive"), exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    # 1. persist today's data
    with open(os.path.join(data_dir, f"{data['date']}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    # 2. today's page
    with open(os.path.join(site_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_page(data, categories, site_name))

    # 3. archive pages (one per stored day) + archive index
    days = sorted((d[:-5] for d in os.listdir(data_dir) if d.endswith(".json")), reverse=True)
    for day in days:
        with open(os.path.join(data_dir, f"{day}.json"), encoding="utf-8") as f:
            day_data = json.load(f)
        with open(os.path.join(site_dir, "archive", f"{day}.html"), "w", encoding="utf-8") as f:
            f.write(render_page(day_data, categories, site_name, archive_href="index.html"))
    links = "".join(f'<li><a href="{d}.html">{d}</a></li>' for d in days)
    with open(os.path.join(site_dir, "archive", "index.html"), "w", encoding="utf-8") as f:
        f.write(ARCHIVE_PAGE.format(site_name=site_name, links=links))
    print(f"[build] site written to {site_dir} ({len(days)} day(s) archived)")
