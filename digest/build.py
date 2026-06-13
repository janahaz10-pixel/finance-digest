"""Generate the static site from digest JSON data."""
import html
import json
import os

CAT_COLORS = {
    "indian-markets": "#FF6B35",
    "us-global":      "#3B82F6",
    "banking-economy":"#8B5CF6",
    "sectors":        "#10B981",
    "crypto":         "#F59E0B",
}
DEFAULT_COLOR = "#3B82F6"


def esc(s):
    return html.escape(str(s or ""))


def _read_time(article):
    words = len(
        (article.get("simplified_article", "") + " " + article.get("investor_impact", "")).split()
    )
    mins = max(1, round(words / 200))
    return f"~{mins} min"


def _render_ticker(market_data):
    if not market_data:
        return ""
    labels  = {"nifty": "NIFTY 50", "sensex": "SENSEX", "usdinr": "USD/INR", "btcusd": "BTC/USD"}
    formats = {"nifty": "{:,.0f}", "sensex": "{:,.0f}", "usdinr": "₹{:.2f}", "btcusd": "${:,.0f}"}
    items = []
    for key, label in labels.items():
        d = market_data.get(key)
        if not d:
            continue
        price = d["price"]
        chg   = d["change_pct"]
        p_str = formats[key].format(price)
        if chg > 0.05:
            arrow = f'<span class="up">▲ {chg:.2f}%</span>'
        elif chg < -0.05:
            arrow = f'<span class="dn">▼ {abs(chg):.2f}%</span>'
        else:
            arrow = f'<span class="fl">— {abs(chg):.2f}%</span>'
        items.append(
            f'<span class="ti"><span class="tn">{label}</span>'
            f'<span class="tp">{p_str}</span>{arrow}</span>'
        )
    if not items:
        return ""
    inner = "".join(items)
    return (
        f'<div class="tkr" aria-hidden="true">'
        f'<div class="tkr-inner">{inner}{inner}</div>'
        f'</div>'
    )


def _render_day_summary(summary):
    if not summary or not summary.strip():
        return ""
    return (
        f'<div class="day-sum">'
        f'<div class="ds-badge">📊 Today at a glance</div>'
        f'<p class="ds-text">{esc(summary.strip())}</p>'
        f'</div>'
    )


def render_card(a, color, hero=False):
    terms_html = "".join(
        f'<div class="term"><b>{esc(t["term"])}</b> — {esc(t["meaning"])}</div>'
        for t in a.get("key_terms", [])
    )
    terms_block = (
        f'<div class="exp-block"><h4>🔑 Key terms</h4><div class="terms">{terms_html}</div></div>'
        if terms_html else ""
    )
    link      = esc(a["link"])
    read_time = _read_time(a)
    pub       = esc(a.get("published", ""))[:17]
    hero_cls  = " hero" if hero else ""
    return f"""<details class="card{hero_cls}" style="--c:{color}">
  <summary>
    <div class="card-top">
      <div class="qt">{esc(a["quick_take"])}</div>
      <div class="take">{esc(a.get("simplified_article",""))}</div>
    </div>
    <div class="card-meta">
      <span class="src-pill">{esc(a["source"])}</span>
      <span class="rtime">{read_time}</span>
      {f'<span class="pub">{pub}</span>' if pub else ''}
      <a class="orig" href="{link}" target="_blank" rel="noopener">Original ↗</a>
      <span class="toggler"><span class="cls-txt">Read simply ▾</span><span class="opn-txt">Close ▴</span></span>
    </div>
  </summary>
  <div class="exp">
    <div class="exp-block"><h4>📖 The story, simply</h4><p>{esc(a["simplified_article"])}</p></div>
    <div class="exp-block impact"><h4>💡 What this means for investors</h4><p>{esc(a["investor_impact"])}</p></div>
    {terms_block}
    <div class="exp-actions">
      <a class="read-orig" href="{link}" target="_blank" rel="noopener">Read the original ↗</a>
      <button class="share-btn" type="button">⎘ Share</button>
    </div>
  </div>
</details>"""


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site_name} — {date_label}</title>
<meta name="description" content="Daily financial news, simplified for everyday investors.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:#F7F8FA;--surface:#FFFFFF;--surface2:#F0F2F7;
  --ink:#111827;--ink2:#374151;--muted:#6B7280;--border:#E5E7EB;
  --accent:#5C6BC0;--accent2:#26C6DA;
  --grad:linear-gradient(135deg,#667EEA 0%,#764BA2 100%);
  --grad2:linear-gradient(135deg,#5C6BC0,#26C6DA);
  --sh0:0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04);
  --sh1:0 4px 16px rgba(0,0,0,.08);
  --sh2:0 12px 40px rgba(0,0,0,.13);
  --r:16px;
}}
[data-theme="dark"] {{
  --bg:#0B0F1A;--surface:#131929;--surface2:#1C2438;
  --ink:#F1F5F9;--ink2:#CBD5E1;--muted:#94A3B8;--border:#1E2D45;
  --accent:#818CF8;--accent2:#34D399;
  --sh0:0 1px 3px rgba(0,0,0,.3);
  --sh1:0 4px 16px rgba(0,0,0,.4);
  --sh2:0 12px 40px rgba(0,0,0,.6);
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.6;
  transition:background .3s,color .3s;-webkit-font-smoothing:antialiased;}}

#prog{{position:fixed;top:0;left:0;height:3px;width:0;
  background:var(--grad2);z-index:999;transition:width .1s linear;pointer-events:none}}

.tkr{{background:var(--surface);border-bottom:1px solid var(--border);
  overflow:hidden;padding:8px 0;white-space:nowrap;user-select:none;}}
.tkr-inner{{display:inline-flex;animation:ticker 40s linear infinite}}
.tkr-inner:hover{{animation-play-state:paused}}
.ti{{display:inline-flex;align-items:center;gap:8px;padding:0 24px;
  border-right:1px solid var(--border);font-size:.76rem;font-weight:600;letter-spacing:.01em;}}
.tn{{color:var(--ink);font-weight:800}}.tp{{color:var(--muted)}}
.up{{color:#10B981}}.dn{{color:#EF4444}}.fl{{color:var(--muted)}}
@keyframes ticker{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}

header{{background:rgba(247,248,250,.88);backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:100;}}
[data-theme="dark"] header{{background:rgba(11,15,26,.88)}}
.h-inner{{max-width:1160px;margin:0 auto;padding:14px 20px}}
.h-row1{{display:flex;align-items:center;justify-content:space-between;gap:16px}}
.brand-name{{font-size:1.5rem;font-weight:900;letter-spacing:-.04em;
  background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;}}
.brand-tag{{font-size:.74rem;color:var(--muted);font-weight:500;margin-top:2px}}
.h-controls{{display:flex;gap:8px}}
.icon-btn{{width:38px;height:38px;border-radius:12px;border:1px solid var(--border);
  background:var(--surface);color:var(--ink);font-size:1rem;cursor:pointer;
  display:flex;align-items:center;justify-content:center;transition:border-color .15s;}}
.icon-btn:hover{{border-color:var(--accent)}}
.h-search{{padding:10px 0 0;position:relative}}
.s-ic{{position:absolute;left:14px;top:50%;transform:translateY(-50%);
  color:var(--muted);font-size:.9rem;pointer-events:none}}
#search{{width:100%;max-width:500px;background:var(--surface2);border:1px solid var(--border);
  color:var(--ink);border-radius:12px;padding:10px 14px 10px 40px;
  font-size:.875rem;font-family:inherit;outline:none;transition:border-color .15s,background .15s;}}
#search:focus{{border-color:var(--accent);background:var(--surface)}}
#search::placeholder{{color:var(--muted)}}

.cat-nav{{display:flex;gap:8px;overflow-x:auto;padding:12px 0 2px;scrollbar-width:none}}
.cat-nav::-webkit-scrollbar{{display:none}}
.cat-pill{{display:inline-flex;align-items:center;gap:6px;padding:7px 16px;
  border-radius:999px;color:var(--muted);font-size:.83rem;font-weight:600;
  border:1.5px solid var(--border);background:var(--surface);white-space:nowrap;
  transition:all .15s;cursor:pointer;text-decoration:none;}}
.cat-pill:hover{{color:var(--ink);border-color:var(--accent)}}
.cat-pill.active{{background:var(--grad);border-color:transparent;color:#fff}}
.cat-dot{{width:7px;height:7px;border-radius:50%;flex-shrink:0}}
.cat-count{{font-size:.7rem;font-weight:700;padding:1px 6px;border-radius:999px;
  background:var(--surface2);color:var(--muted);}}
.cat-pill.active .cat-count{{background:rgba(255,255,255,.25);color:#fff}}

.main-wrap{{max-width:1160px;margin:0 auto;padding:28px 20px 100px}}
.date-bar{{display:flex;align-items:center;gap:8px;margin-bottom:24px;
  font-size:.88rem;font-weight:600;color:var(--muted);}}
.live-dot{{width:8px;height:8px;border-radius:50%;background:#10B981;flex-shrink:0;
  box-shadow:0 0 0 4px rgba(16,185,129,.15);}}

.day-sum{{border-radius:var(--r);padding:22px 26px;margin-bottom:32px;
  background:var(--grad);color:#fff;position:relative;overflow:hidden;}}
.day-sum::before{{content:'';position:absolute;inset:0;opacity:.06;
  background-image:radial-gradient(circle at 80% 50%,#fff 0%,transparent 60%);}}
.ds-badge{{font-size:.68rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;
  opacity:.8;margin-bottom:10px;}}
.ds-text{{font-size:1rem;line-height:1.72;position:relative;z-index:1}}

section{{margin-bottom:52px}}
.sec-header{{display:flex;align-items:center;gap:12px;margin-bottom:20px;
  padding-bottom:14px;border-bottom:2px solid var(--border);}}
.sec-emoji{{font-size:1.35rem;line-height:1}}
.sec-title{{font-size:1.15rem;font-weight:800;letter-spacing:-.02em}}
.sec-count{{font-size:.72rem;font-weight:700;color:var(--muted);
  background:var(--surface2);border:1px solid var(--border);
  padding:2px 10px;border-radius:999px;margin-left:auto;}}

.card-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}

.card{{background:var(--surface);border-radius:var(--r);border:1px solid var(--border);
  box-shadow:var(--sh0);overflow:hidden;transition:box-shadow .2s,transform .2s;
  animation:rise .4s ease both;border-top:3px solid var(--c,var(--accent));
  display:flex;flex-direction:column;}}
.card:hover{{box-shadow:var(--sh1);transform:translateY(-3px)}}
.card.hidden{{display:none!important}}
.card.hero{{grid-column:span 2}}
@keyframes rise{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}

.card summary{{list-style:none;cursor:pointer;padding:18px 18px 14px;
  flex:1;display:flex;flex-direction:column;}}
.card summary::-webkit-details-marker{{display:none}}
.card-top{{flex:1;margin-bottom:12px}}
.qt{{font-size:.97rem;font-weight:700;line-height:1.45;margin-bottom:8px;
  color:var(--ink);letter-spacing:-.01em;}}
.card.hero .qt{{font-size:1.1rem}}
.take{{font-size:.82rem;color:var(--muted);line-height:1.6;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}}
.card.hero .take{{-webkit-line-clamp:3}}
.card-meta{{display:flex;flex-wrap:wrap;align-items:center;gap:7px;font-size:.74rem;
  padding-top:12px;border-top:1px solid var(--border);margin-top:auto;}}
.src-pill{{background:var(--surface2);color:var(--ink2);border-radius:6px;
  padding:2px 8px;font-weight:700;font-size:.72rem;}}
.rtime,.pub{{color:var(--muted)}}
.orig{{color:var(--accent);text-decoration:none;font-weight:600;margin-left:auto;}}
.orig:hover{{text-decoration:underline}}
.toggler{{color:var(--muted);font-weight:600;font-size:.74rem;padding:3px 10px;
  border-radius:8px;background:var(--surface2);border:1px solid var(--border);
  cursor:pointer;transition:background .15s,color .15s,border-color .15s;}}
.toggler:hover{{background:var(--accent);color:#fff;border-color:var(--accent)}}
details[open] .toggler .cls-txt{{display:none}}
details:not([open]) .toggler .opn-txt{{display:none}}

.exp{{padding:4px 18px 18px;border-top:1px dashed var(--border);background:var(--surface)}}
.exp-block{{margin-top:16px}}
.exp-block h4{{font-size:.65rem;font-weight:800;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);margin-bottom:8px;}}
.exp-block p{{font-size:.9rem;line-height:1.75;color:var(--ink2)}}
.exp-block.impact{{background:linear-gradient(135deg,rgba(16,185,129,.07),rgba(16,185,129,.02));
  border-radius:12px;padding:14px 16px;border-left:3px solid #10B981;}}
.exp-block.impact h4{{color:#059669}}.exp-block.impact p{{color:var(--ink)}}
.terms{{display:flex;flex-direction:column;gap:8px;margin-top:4px}}
.term{{background:var(--surface2);border-radius:10px;padding:10px 14px;
  font-size:.86rem;color:var(--ink);border-left:3px solid var(--accent);}}
.term b{{color:var(--accent)}}
.exp-actions{{display:flex;align-items:center;gap:10px;margin-top:18px;flex-wrap:wrap}}
.read-orig{{display:inline-flex;align-items:center;gap:6px;font-size:.85rem;color:#fff;
  background:var(--grad);text-decoration:none;font-weight:700;padding:9px 18px;
  border-radius:10px;transition:opacity .15s;}}
.read-orig:hover{{opacity:.88}}
.share-btn{{font-size:.8rem;color:var(--muted);background:var(--surface2);
  border:1px solid var(--border);padding:8px 14px;border-radius:10px;
  cursor:pointer;font-weight:600;font-family:inherit;transition:color .15s,border-color .15s;}}
.share-btn:hover{{color:var(--accent);border-color:var(--accent)}}

.no-match{{color:var(--muted);font-size:.9rem;text-align:center;padding:40px 0;display:none}}
.disclaimer{{color:var(--muted);font-size:.74rem;text-align:center;
  padding:20px 0 10px;border-top:1px solid var(--border);margin-top:30px;}}
footer{{text-align:center;padding:20px;font-size:.78rem;color:var(--muted);
  border-top:1px solid var(--border);background:var(--surface);}}
footer a{{color:var(--accent);text-decoration:none}}
footer a:hover{{text-decoration:underline}}
#btt{{position:fixed;bottom:28px;right:22px;background:var(--grad);color:#fff;
  border:none;width:44px;height:44px;border-radius:14px;font-size:1.1rem;
  cursor:pointer;display:none;align-items:center;justify-content:center;
  box-shadow:0 4px 16px rgba(92,107,192,.35);transition:opacity .2s,transform .2s;z-index:50;}}
#btt.show{{display:flex}}
#btt:hover{{opacity:.88;transform:translateY(-2px)}}

@media(max-width:900px){{
  .card-grid{{grid-template-columns:repeat(2,1fr)}}
  .card.hero{{grid-column:span 2}}
}}
@media(max-width:600px){{
  .card-grid{{grid-template-columns:1fr}}
  .card.hero{{grid-column:span 1}}
  .brand-name{{font-size:1.25rem}}
  .main-wrap{{padding:20px 14px 80px}}
  .h-inner{{padding:12px 14px}}
}}
</style>
</head>
<body>
<div id="prog"></div>
{ticker}
<header>
  <div class="h-inner">
    <div class="h-row1">
      <div>
        <div class="brand-name">{site_name}</div>
        <div class="brand-tag">Finance news, simplified for everyday investors</div>
      </div>
      <div class="h-controls">
        <button class="icon-btn" id="theme-btn" title="Toggle dark mode">🌙</button>
      </div>
    </div>
    <div class="h-search">
      <span class="s-ic">🔍</span>
      <input id="search" type="search" placeholder="Search stories…" autocomplete="off">
    </div>
    <nav class="cat-nav">{nav_links}</nav>
  </div>
</header>
<div class="main-wrap">
  <div class="date-bar">
    <span class="live-dot"></span>
    <span>Updated <strong>{date_label}</strong></span>
  </div>
  {day_summary}
  <div class="no-match" id="no-match">No stories match your search.</div>
  {sections}
  <p class="disclaimer">For informational &amp; educational purposes only. Not financial advice.</p>
</div>
<footer>Built with ❤ using Python &amp; GitHub Actions &nbsp;·&nbsp; <a href="{data_url}">Raw JSON</a></footer>
<button id="btt" aria-label="Back to top">↑</button>
<script>
(function(){{
  var t=localStorage.getItem('theme')||'light';
  document.documentElement.setAttribute('data-theme',t);
  document.getElementById('theme-btn').textContent=t==='dark'?'☀':'🌙';
}})();
document.getElementById('theme-btn').addEventListener('click',function(){{
  var d=document.documentElement;
  var t=d.getAttribute('data-theme')==='dark'?'light':'dark';
  d.setAttribute('data-theme',t);localStorage.setItem('theme',t);
  this.textContent=t==='dark'?'☀':'🌙';
}});
var prog=document.getElementById('prog');
window.addEventListener('scroll',function(){{
  var h=document.body.scrollHeight-window.innerHeight;
  prog.style.width=(h>0?window.scrollY/h*100:0)+'%';
}},{{passive:true}});
var btt=document.getElementById('btt');
window.addEventListener('scroll',function(){{btt.classList.toggle('show',window.scrollY>400);}},{{passive:true}});
btt.addEventListener('click',function(){{window.scrollTo({{top:0,behavior:'smooth'}});}});
document.querySelectorAll('.card').forEach(function(c,i){{c.style.animationDelay=(i*.04)+'s';}});
var inp=document.getElementById('search');
var nm=document.getElementById('no-match');
inp.addEventListener('input',function(){{
  var q=this.value.toLowerCase().trim();var v=0;
  document.querySelectorAll('.card').forEach(function(c){{
    var m=!q||c.textContent.toLowerCase().includes(q);
    c.classList.toggle('hidden',!m);if(m)v++;
  }});
  nm.style.display=v===0&&q?'block':'none';
}});
document.querySelectorAll('.cat-pill').forEach(function(a){{
  a.addEventListener('click',function(){{
    document.querySelectorAll('.cat-pill').forEach(function(p){{p.classList.remove('active');}});
    this.classList.add('active');
    var id=this.getAttribute('data-target');
    if(id==='all'){{window.scrollTo({{top:0,behavior:'smooth'}});return;}}
    var el=document.getElementById(id);
    if(el)el.scrollIntoView({{behavior:'smooth',block:'start'}});
  }});
}});
document.querySelectorAll('.share-btn').forEach(function(btn){{
  btn.addEventListener('click',function(){{
    var qt=this.closest('.card')?.querySelector('.qt')?.textContent||'';
    if(navigator.share)navigator.share({{title:qt,url:window.location.href}});
    else if(navigator.clipboard)navigator.clipboard.writeText(qt+' '+window.location.href).then(function(){{
      btn.textContent='✓ Copied!';setTimeout(function(){{btn.textContent='⎘ Share';}},2000);
    }});
  }});
}});
</script>
</body>
</html>"""


def render_page(data, categories, site_name, data_url):
    articles    = data["articles"]
    market_data = data.get("market_data", {})
    day_summary = data.get("day_summary", "")

    ticker       = _render_ticker(market_data)
    day_sum_html = _render_day_summary(day_summary)

    nav_links = '<span class="cat-pill active" data-target="all">All</span>'
    for slug, cat in categories.items():
        label = cat["label"] if isinstance(cat, dict) else cat
        emoji = cat.get("emoji", "") if isinstance(cat, dict) else ""
        color = CAT_COLORS.get(slug, DEFAULT_COLOR)
        count = len(articles.get(slug, []))
        nav_links += (
            f'<span class="cat-pill" data-target="{slug}">'
            f'<span class="cat-dot" style="background:{color}"></span>'
            f'{emoji} {label}'
            f'<span class="cat-count">{count}</span>'
            f'</span>'
        )

    sections_html = ""
    for slug, cat in categories.items():
        label = cat["label"] if isinstance(cat, dict) else cat
        emoji = cat.get("emoji", "") if isinstance(cat, dict) else ""
        arts  = articles.get(slug, [])
        if not arts:
            continue
        color = CAT_COLORS.get(slug, DEFAULT_COLOR)
        cards = "".join(render_card(a, color, hero=(i == 0)) for i, a in enumerate(arts))
        sections_html += (
            f'<section id="{slug}">'
            f'<div class="sec-header">'
            f'<span class="sec-emoji">{emoji}</span>'
            f'<span class="sec-title">{label}</span>'
            f'<span class="sec-count">{len(arts)} stories</span>'
            f'</div>'
            f'<div class="card-grid">{cards}</div>'
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
