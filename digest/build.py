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


def esc(s):
    return html.escape(str(s or ""))


def _read_time(article):
    words = len(
        (article.get("simplified_article", "") + " " + article.get("investor_impact", "")).split()
    )
    mins = max(1, round(words / 200))
    return f"~{mins} min"


def _render_ticker(market_data):
    """Render scrolling market ticker. Returns '' if no data."""
    if not market_data:
        return ""
    labels  = {"nifty": "NIFTY 50", "sensex": "SENSEX", "usdinr": "USD/INR", "btcusd": "BTC/USD"}
    formats = {"nifty": "{:,.0f}", "sensex": "{:,.0f}", "usdinr": "₹{:.2f}", "btcusd": "${:,.0f}"}
    items = []
    for key, label in labels.items():
        d = market_data.get(key)
        if not d:
            continue
        price   = d["price"]
        chg     = d["change_pct"]
        p_str   = formats[key].format(price)
        if chg > 0.05:
            chg_html = f'<span class="tick-up">▲ {chg:.2f}%</span>'
        elif chg < -0.05:
            chg_html = f'<span class="tick-down">▼ {abs(chg):.2f}%</span>'
        else:
            chg_html = f'<span class="tick-flat">— {abs(chg):.2f}%</span>'
        items.append(
            f'<span class="tick-item"><span class="tick-name">{label}</span>'
            f'<span class="tick-price">{p_str}</span>{chg_html}</span>'
        )
    if not items:
        return ""
    inner = "".join(items)
    # Duplicate for seamless CSS loop
    return (
        f'<div class="ticker-wrap" aria-hidden="true">'
        f'<div class="ticker-move">{inner}{inner}</div>'
        f'</div>'
    )


def _render_day_summary(summary):
    if not summary or not summary.strip():
        return ""
    return (
        f'<div class="day-summary">'
        f'<div class="ds-label">📊 Today at a glance</div>'
        f'<p>{esc(summary.strip())}</p>'
        f'</div>'
    )


def render_card(a, color):
    terms_html = "".join(
        f'<div class="term"><b>{esc(t["term"])}</b> — {esc(t["meaning"])}</div>'
        for t in a.get("key_terms", [])
    )
    terms_block = (
        f'<div class="block"><h4>🔑 Key terms</h4><div class="terms">{terms_html}</div></div>'
        if terms_html else ""
    )
    link      = esc(a["link"])
    read_time = _read_time(a)
    pub       = esc(a.get("published", ""))[:17]
    return f"""<details class="card" style="--cat:{color}">
  <summary>
    <div class="qt">{esc(a["quick_take"])}</div>
    <div class="meta">
      <span class="src">{esc(a["source"])}</span>
      <span class="rtime">{read_time}</span>
      {f'<span class="pub">{pub}</span>' if pub else ''}
      <a class="origlink" href="{link}" target="_blank" rel="noopener">Original ↗</a>
      <span class="hint"><span class="closed-txt">Read simply ▾</span><span class="open-txt">Close ▴</span></span>
    </div>
  </summary>
  <div class="body">
    <div class="block"><h4>📖 The story, simply</h4><p>{esc(a["simplified_article"])}</p></div>
    <div class="block impact"><h4>💡 What this means for investors</h4><p>{esc(a["investor_impact"])}</p></div>
    {terms_block}
    <div class="card-actions">
      <a class="readorig" href="{link}" target="_blank" rel="noopener">Read the original ↗</a>
      <button class="sharebtn" type="button">⎘ Share</button>
    </div>
  </div>
</details>"""


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site_name} — {date_label}</title>
<meta name="description" content="Daily financial news, simplified for beginners. No jargon, no finance degree needed.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#f4f6fb; --bg2:#edf0f7; --card:#ffffff; --ink:#131a2a;
    --muted:#5d6778; --border:#e4e8f0; --accent:#4f6df5; --accent2:#18b2c8;
    --chip-bg:#ffffff; --impact-bg:#ecf8f2; --impact-ink:#0c6e48;
    --term-bg:#fdf4dd; --term-ink:#7a5b00;
    --shadow:0 1px 3px rgba(16,24,40,.07);
    --shadow-hover:0 8px 28px rgba(16,24,40,.12);
  }}
  [data-theme="dark"] {{
    --bg:#0c111d; --bg2:#101727; --card:#161e31; --ink:#eef2fa;
    --muted:#97a3b8; --border:#232d45; --accent:#7b93ff; --accent2:#2dd4bf;
    --chip-bg:#161e31; --impact-bg:#0e2b21; --impact-ink:#5fd6a2;
    --term-bg:#2b2410; --term-ink:#e8c35c;
    --shadow:0 1px 3px rgba(0,0,0,.4);
    --shadow-hover:0 8px 28px rgba(0,0,0,.55);
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  html{{scroll-behavior:smooth}}
  body{{
    font-family:'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
    background:var(--bg);color:var(--ink);line-height:1.65;
    transition:background .25s,color .25s;
  }}

  /* ── Reading progress bar ── */
  #progress{{
    position:fixed;top:0;left:0;height:3px;width:0%;
    background:linear-gradient(90deg,var(--accent),var(--accent2));
    z-index:200;transition:width .08s linear;pointer-events:none;
  }}

  /* ── Ticker strip ── */
  .ticker-wrap{{
    background:var(--bg2);border-bottom:1px solid var(--border);
    overflow:hidden;padding:7px 0;font-size:.76rem;font-weight:600;
    letter-spacing:.01em;color:var(--muted);user-select:none;
  }}
  .ticker-move{{
    display:inline-flex;white-space:nowrap;
    animation:ticker-scroll 36s linear infinite;
  }}
  .ticker-move:hover{{animation-play-state:paused}}
  .tick-item{{padding:0 28px;border-right:1px solid var(--border)}}
  .tick-name{{color:var(--ink);font-weight:800;margin-right:6px}}
  .tick-price{{margin-right:4px}}
  .tick-up{{color:#22c55e}}
  .tick-down{{color:#ef4444}}
  .tick-flat{{color:var(--muted)}}
  @keyframes ticker-scroll{{0%{{transform:translateX(0)}}100%{{transform:translateX(-50%)}}}}

  /* ── Header ── */
  header{{
    background:var(--card);border-bottom:1px solid var(--border);
    position:sticky;top:0;z-index:20;box-shadow:var(--shadow);
  }}
  .hwrap{{max-width:960px;margin:0 auto;padding:14px 18px 0}}
  .hrow{{display:flex;align-items:center;justify-content:space-between;gap:12px}}
  .brand{{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}}
  h1{{font-size:1.45rem;letter-spacing:-.03em;font-weight:800}}
  h1 em{{
    font-style:normal;
    background:linear-gradient(120deg,var(--accent),var(--accent2));
    -webkit-background-clip:text;background-clip:text;color:transparent;
  }}
  .tagline{{color:var(--muted);font-size:.82rem;font-weight:500}}
  .hbtns{{display:flex;gap:8px;align-items:center}}
  .btn{{
    border:1px solid var(--border);background:var(--chip-bg);color:var(--ink);
    border-radius:10px;padding:6px 12px;font-size:.82rem;font-weight:600;
    cursor:pointer;text-decoration:none;font-family:inherit;
    transition:border-color .15s,color .15s;
  }}
  .btn:hover{{border-color:var(--accent);color:var(--accent)}}

  /* ── Search bar ── */
  .search-wrap{{padding:10px 0 0}}
  .search-rel{{position:relative;display:inline-block;width:100%;max-width:420px}}
  .search-icon{{
    position:absolute;left:13px;top:50%;transform:translateY(-50%);
    color:var(--muted);font-size:.88rem;pointer-events:none;
  }}
  #search{{
    width:100%;background:var(--bg2);border:1px solid var(--border);color:var(--ink);
    border-radius:12px;padding:9px 14px 9px 36px;font-size:.88rem;font-family:inherit;
    outline:none;transition:border-color .15s;
  }}
  #search::placeholder{{color:var(--muted)}}
  #search:focus{{border-color:var(--accent);background:var(--card)}}

  /* ── Category nav ── */
  nav{{display:flex;gap:8px;overflow-x:auto;padding:12px 0;scrollbar-width:none}}
  nav::-webkit-scrollbar{{display:none}}
  nav a{{
    white-space:nowrap;padding:6px 14px;border-radius:999px;text-decoration:none;
    color:var(--muted);font-size:.85rem;font-weight:600;border:1px solid var(--border);
    background:var(--chip-bg);display:flex;align-items:center;gap:7px;
    transition:color .15s,border-color .15s,background .15s;
  }}
  nav a .dot{{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0}}
  nav a .nbadge{{
    background:var(--bg2);color:var(--muted);font-size:.7rem;font-weight:700;
    padding:1px 6px;border-radius:999px;
  }}
  nav a:hover{{color:var(--ink);border-color:var(--accent)}}

  /* ── Main ── */
  main{{max-width:960px;margin:0 auto;padding:28px 18px 90px}}
  .datebar{{
    display:flex;align-items:center;gap:10px;margin-bottom:20px;
    color:var(--muted);font-size:.9rem;font-weight:500;
  }}
  .datebar .live{{
    width:8px;height:8px;border-radius:50%;background:#22c55e;
    box-shadow:0 0 0 4px rgba(34,197,94,.18);flex-shrink:0;
  }}
  .datebar b{{color:var(--ink);font-weight:700}}

  /* ── Day summary ── */
  .day-summary{{
    background:var(--card);border:1px solid var(--border);border-radius:16px;
    padding:18px 20px;margin-bottom:30px;box-shadow:var(--shadow);
    border-left:4px solid var(--accent);
  }}
  .ds-label{{
    font-size:.68rem;font-weight:800;letter-spacing:.1em;
    text-transform:uppercase;color:var(--accent);margin-bottom:9px;
  }}
  .day-summary p{{font-size:.97rem;line-height:1.72;color:var(--ink)}}

  /* ── Sections & cards ── */
  section{{margin-bottom:46px}}
  .sechead{{display:flex;align-items:center;gap:10px;margin-bottom:16px}}
  .sechead .bar{{width:5px;height:22px;border-radius:3px;flex-shrink:0}}
  .sechead h2{{font-size:1.15rem;letter-spacing:-.01em;font-weight:800}}
  .count{{
    color:var(--muted);font-size:.78rem;font-weight:700;
    border:1px solid var(--border);padding:2px 10px;border-radius:999px;
  }}

  @keyframes fadeSlideUp{{
    from{{opacity:0;transform:translateY(14px)}}
    to{{opacity:1;transform:translateY(0)}}
  }}
  .card{{
    background:var(--card);border:1px solid var(--border);border-radius:16px;
    margin-bottom:14px;overflow:hidden;box-shadow:var(--shadow);
    transition:box-shadow .2s,transform .2s;
    border-left:4px solid var(--cat,var(--accent));
    animation:fadeSlideUp .42s ease both;
  }}
  .card:hover{{box-shadow:var(--shadow-hover);transform:translateY(-2px)}}
  .card.hidden{{display:none!important}}

  .card summary{{list-style:none;cursor:pointer;padding:16px 18px 14px}}
  .card summary::-webkit-details-marker{{display:none}}
  .qt{{font-size:1.02rem;font-weight:700;margin-bottom:10px;letter-spacing:-.01em;line-height:1.42}}
  .meta{{
    font-size:.76rem;color:var(--muted);
    display:flex;gap:10px;align-items:center;flex-wrap:wrap;
  }}
  .src{{
    border:1px solid var(--border);padding:2px 9px;border-radius:999px;
    font-weight:700;color:var(--ink);
  }}
  .rtime{{color:var(--muted)}}
  .pub{{color:var(--muted)}}
  .origlink{{color:var(--accent);text-decoration:none;font-weight:700}}
  .origlink:hover{{text-decoration:underline}}
  .hint{{margin-left:auto;color:var(--muted);font-weight:600;white-space:nowrap}}
  details[open] .hint .closed-txt{{display:none}}
  details:not([open]) .hint .open-txt{{display:none}}

  .body{{padding:4px 18px 18px}}
  .block{{margin-top:16px}}
  .block h4{{
    font-size:.67rem;font-weight:800;letter-spacing:.1em;
    text-transform:uppercase;color:var(--muted);margin-bottom:8px;
  }}
  .block p{{font-size:.95rem;line-height:1.72}}
  .impact{{background:var(--impact-bg);border-radius:12px;padding:14px 16px}}
  .impact h4,.impact p{{color:var(--impact-ink)}}
  .terms{{display:flex;flex-direction:column;gap:8px}}
  .term{{
    background:var(--term-bg);border-radius:10px;
    padding:10px 14px;font-size:.88rem;color:var(--ink);
  }}
  .term b{{color:var(--term-ink)}}

  /* ── Card action row ── */
  .card-actions{{display:flex;align-items:center;gap:10px;margin-top:18px;flex-wrap:wrap}}
  .readorig{{
    display:inline-flex;align-items:center;gap:6px;font-size:.88rem;
    color:#fff;background:linear-gradient(120deg,var(--accent),var(--accent2));
    text-decoration:none;font-weight:700;padding:9px 18px;border-radius:10px;
    transition:opacity .15s;
  }}
  .readorig:hover{{opacity:.88}}
  .sharebtn{{
    display:inline-flex;align-items:center;gap:5px;font-size:.82rem;
    color:var(--muted);background:var(--bg2);border:1px solid var(--border);
    padding:8px 14px;border-radius:10px;cursor:pointer;font-weight:600;
    font-family:inherit;transition:color .15s,border-color .15s;
  }}
  .sharebtn:hover{{color:var(--accent);border-color:var(--accent)}}

  /* ── Footer & misc ── */
  .empty{{color:var(--muted);font-size:.9rem;padding:12px 0}}
  .no-match{{color:var(--muted);font-size:.9rem;padding:24px 0;text-align:center;display:none}}
  .disclaimer{{
       color:var(--muted);font-size:.75rem;text-align:center;
    padding:20px 0 10px;border-top:1px solid var(--border);margin-top:30px;
  }}
  footer{{
    text-align:center;padding:18px;font-size:.78rem;color:var(--muted);
    border-top:1px solid var(--border);background:var(--card);
  }}
  #backtop{{
    position:fixed;bottom:28px;right:22px;
    background:var(--accent);color:#fff;border:none;
    width:42px;height:42px;border-radius:50%;font-size:1.1rem;
    cursor:pointer;display:none;align-items:center;justify-content:center;
    box-shadow:0 4px 16px rgba(79,109,245,.35);transition:opacity .2s,transform .2s;
    z-index:50;
  }}
  #backtop.show{{display:flex}}
  #backtop:hover{{opacity:.88;transform:translateY(-2px)}}
  @media(max-width:600px){{
    h1{{font-size:1.2rem}}
    .tagline{{display:none}}
    main{{padding:18px 14px 80px}}
    .hwrap{{padding:12px 14px 0}}
  }}
</style>
</head>
<body>
<div id="progress"></div>
{ticker}
<header>
  <div class="hwrap">
    <div class="hrow">
      <div class="brand">
        <h1><em>{site_name}</em></h1>
        <span class="tagline">Finance, simplified.</span>
      </div>
      <div class="hbtns">
        <button class="btn" id="themetoggle" title="Toggle dark mode">🌙</button>
      </div>
    </div>
    <div class="search-wrap">
      <div class="search-rel">
        <span class="search-icon">🔍</span>
        <input id="search" type="search" placeholder="Search stories…" autocomplete="off">
      </div>
    </div>
    <nav>{nav_links}</nav>
  </div>
</header>
<main>
  <div class="datebar">
    <span class="live"></span>
    <span>Updated <b>{date_label}</b></span>
  </div>
  {day_summary}
  <div class="no-match" id="no-match">No stories match your search.</div>
  {sections}
  <p class="disclaimer">For informational purposes only. Not financial advice.</p>
</main>
<footer>Built with ❤ using Python &amp; GitHub Actions · <a href="{data_url}" style="color:var(--accent)">Raw JSON</a></footer>
<button id="backtop" aria-label="Back to top" title="Back to top">↑</button>
<script>
(function(){{
  const s=localStorage.getItem('theme')||'light';
  document.documentElement.setAttribute('data-theme',s);
  document.getElementById('themetoggle').textContent=s==='dark'?'☀':'🌙';
}})();
document.getElementById('themetoggle').addEventListener('click',function(){{
  const d=document.documentElement;
  const t=d.getAttribute('data-theme')==='dark'?'light':'dark';
  d.setAttribute('data-theme',t);
  localStorage.setItem('theme',t);
  this.textContent=t==='dark'?'☀':'🌙';
}});
const prog=document.getElementById('progress');
window.addEventListener('scroll',function(){{
  const h=document.body.scrollHeight-window.innerHeight;
  prog.style.width=(h>0?window.scrollY/h*100:0)+'%';
}},{{passive:true}});
const bt=document.getElementById('backtop');
window.addEventListener('scroll',function(){{
  bt.classList.toggle('show',window.scrollY>400);
}},{{passive:true}});
bt.addEventListener('click',function(){{window.scrollTo({{top:0,behavior:'smooth'}});}});
document.querySelectorAll('.card').forEach(function(c,i){{
  c.style.animationDelay=(i*0.06)+'s';
}});
const inp=document.getElementById('search');
const noMatch=document.getElementById('no-match');
inp.addEventListener('input',function(){{
  const q=this.value.toLowerCase().trim();
  let visible=0;
  document.querySelectorAll('.card').forEach(function(c){{
    const match=!q||c.textContent.toLowerCase().includes(q);
    c.classList.toggle('hidden',!match);
    if(match)visible++;
  }});
  noMatch.style.display=visible===0&&q?'block':'none';
}});
document.querySelectorAll('nav a').forEach(function(a){{
  a.addEventListener('click',function(e){{
    e.preventDefault();
    const id=this.getAttribute('href').slice(1);
    const el=document.getElementById(id);
    if(el)el.scrollIntoView({{behavior:'smooth',block:'start'}});
  }});
}});
document.querySelectorAll('.sharebtn').forEach(function(btn){{
  btn.addEventListener('click',function(){{
    const card=this.closest('.card');
    const qt=card?card.querySelector('.qt')?.textContent:'';
    const txt=(qt||document.title)+' '+window.location.href;
    if(navigator.share){{navigator.share({{title:qt,url:window.location.href}});}}
    else if(navigator.clipboard){{
      navigator.clipboard.writeText(txt).then(function(){{
        btn.textContent='✓ Copied!';setTimeout(function(){{btn.textContent='⎘ Share';}},2000);
      }});
    }}
  }});
}});
</script>
</body>
</html>"""


def render_page(data, categories, site_name, data_url):
    articles     = data["articles"]
    market_data  = data.get("market_data", {})
    day_summary  = data.get("day_summary", "")

    ticker       = _render_ticker(market_data)
    day_sum_html = _render_day_summary(day_summary)

    nav_links = '<a href="#all">All</a>'
    for slug, label in categories.items():
        color = CAT_COLORS.get(slug, DEFAULT_COLOR)
        count = len(articles.get(slug, []))
        nav_links += (
            f'<a href="#{slug}">'
            f'<span class="dot" style="background:{color}"></span>'
            f'{label}'
            f'<span class="nbadge">{count}</span>'
            f'</a>'
        )

    sections_html = ""
    for slug, label in categories.items():
        arts = articles.get(slug, [])
        if not arts:
            continue
        color = CAT_COLORS.get(slug, DEFAULT_COLOR)
        cards = "".join(render_card(a, color) for a in arts)
        sections_html += (
            f'<section id="{slug}">'
            f'<div class="sechead">'
            f'<span class="bar" style="background:{color}"></span>'
            f'<h2>{label}</h2>'
            f'<span class="count">{len(arts)}</span>'
            f'</div>'
            f'{cards}'
            f'</section>'
        )

    return PAGE.format(
        site_name=site_name,
        date_label=data["date_label"],
        ticker=ticker,
        nav_links=nav_links,
        day_summary=day_sum_html,
        sections=sections_html,
        data_url=data_url,
    )


def build_site(data, categories, site_dir, data_dir, site_name):
    os.makedirs(site_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    date  = data["date"]
    fname = f"{data_dir}/{date}.json"
    with open(fname, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[build] saved {fname}")

    data_url = f"../{fname}"
    html_out = render_page(data, categories, site_name, data_url)
    index    = f"{site_dir}/index.html"
    with open(index, "w") as f:
        f.write(html_out)
    print(f"[build] wrote {index} ({len(html_out):,} chars)")
