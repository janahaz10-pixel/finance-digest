import json
import os
import re
import datetime

CAT_COLORS = {
    "indian-markets":   "#0EA5E9",
    "global-markets":   "#8B5CF6",
    "crypto":           "#F59E0B",
    "economy":          "#10B981",
    "stocks":           "#EF4444",
    "personal-finance": "#EC4899",
    "technology":       "#6366F1",
    "commodities":      "#F97316",
}
DEFAULT_COLOR = "#64748B"


def _src_label(url="", fallback=""):
    try:
        h = url.split("/")[2].lower()
        h = re.sub(r"^(www\.|feeds\.|rss\.|m\.)", "", h)
        parts = h.split(".")
        return parts[0].replace("-", " ").title()
    except Exception:
        return fallback or "Source"


def _fmt_pub(pub=""):
    try:
        dt = datetime.datetime.fromisoformat(pub.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        diff = now - dt
        h = diff.total_seconds() / 3600
        if h < 1:
            return f"{int(diff.total_seconds() / 60)}m ago"
        if h < 24:
            return f"{int(h)}h ago"
        if h < 48:
            return "Yesterday"
        return dt.strftime("%b %d")
    except Exception:
  2     return pub[:10] if pub else ""


def _est_read(a):
    text = " ".join(filter(None, [
        a.get("q", ""), a.get("take", ""),
        a.get("expand", {}).get("what", "") if isinstance(a.get("expand"), dict) else "",
        a.get("expand", {}).get("why", "") if isinstance(a.get("expand"), dict) else "",
    ]))
    mins = max(1, round(len(text.split()) / 180))
    return f"{mins} min"


PAGE = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#667EEA">
<title>{site_name} — Finance News Simplified</title>
<meta name="description" content="Daily finance news simplified for everyday investors">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300..900;1,14..32,300..900&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:#F7F8FA;--surface:#fff;--surface2:#F1F5F9;--surface3:#E8EDF3;
  --ink:#0F172A;--ink2:#334155;--ink3:#64748B;--muted:#94A3B8;
  --border:#E2E8F0;--border2:#CBD5E1;
  --accent:#667EEA;--accent2:#10B981;
  --grad:linear-gradient(135deg,#667EEA 0%,#764BA2 100%);
  --grad2:linear-gradient(135deg,#10B981 0%,#059669 100%);
  --r:14px;--r-sm:8px;
  --sh0:0 1px 3px rgba(15,23,42,.06),0 1px 2px rgba(15,23,42,.04);
  --sh1:0 4px 16px rgba(15,23,42,.09),0 2px 6px rgba(15,23,42,.05);
  --sh2:0 12px 40px rgba(15,23,42,.13),0 4px 12px rgba(15,23,42,.07);
}}
[data-theme="dark"] {{
  --bg:#080C14;--surface:#0F1724;--surface2:#162032;--surface3:#1E2D42;
  --ink:#F1F5F9;--ink2:#CBD5E1;--ink3:#94A3B8;--muted:#64748B;
  --border:#1E2D42;--border2:#243550;
  --accent:#818CF8;--accent2:#34D399;
  --sh0:0 1px 3px rgba(0,0,0,.3);
  --sh1:0 4px 16px rgba(0,0,0,.4);
  --sh2:0 12px 40px rgba(0,0,0,.65);
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',system-ui,-apple-system,sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.6;
  -webkit-font-smoothing:antialiased;
  transition:background .3s,color .3s;}}

/* ── Progress ── */
#prog{{position:fixed;top:0;left:0;height:2px;width:0;
  background:var(--grad);z-index:9999;
  transition:width .1s linear;pointer-events:none;}}

/* ── Ticker ── */
.tkr{{background:var(--surface);border-bottom:1px solid var(--border);
  overflow:hidden;height:34px;display:flex;align-items:center;
  white-space:nowrap;user-select:none;}}
.tkr-inner{{display:inline-flex;
  animation:ticker 55s linear infinite;}}
.tkr-inner:hover{{animation-play-state:paused}}
.ti{{display:inline-flex;align-items:center;gap:6px;padding:0 20px;
  border-right:1px solid var(--border);
  font-size:.71rem;font-weight:600;letter-spacing:.01em;}}
.tn{{color:var(--ink);font-weight:800}}
.tp{{color:var(--muted);font-size:.65rem;font-weight:500}}
.up{{color:#10B981}}.dn{{color:#EF4444}}.fl{{color:var(--muted)}}
.ti-arr{{font-size:.55rem}}
@keyframes ticker{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}

/* ── Header ── */
header{{background:rgba(247,248,250,.9);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:200;}}
[data-theme="dark"] header{{background:rgba(8,12,20,.9)}}
.h-inner{{max-width:1200px;margin:0 auto;padding:0 24px}}
.h-row1{{display:flex;align-items:center;justify-content:space-between;
  gap:16px;height:58px;}}
.brand-logo{{display:flex;align-items:center;gap:10px;text-decoration:none;}}
.brand-icon{{width:32px;height:32px;border-radius:9px;
  background:var(--grad);display:flex;align-items:center;
  justify-content:center;font-size:.9rem;flex-shrink:0;
  box-shadow:0 2px 10px rgba(102,126,234,.4);}}
.brand-name{{font-size:1.2rem;font-weight:900;letter-spacing:-.045em;
  background:var(--grad);-webkit-background-clip:text;
  background-clip:text;color:transparent;}}
.brand-sub{{font-size:.64rem;color:var(--muted);font-weight:500;
  letter-spacing:.005em;margin-top:1px;}}
.h-center{{flex:1;max-width:380px;margin:0 16px;position:relative;}}
.s-ic{{position:absolute;left:11px;top:50%;transform:translateY(-50%);
  color:var(--muted);font-size:.8rem;pointer-events:none;}}
#search{{width:100%;background:var(--surface2);
  border:1.5px solid var(--border);color:var(--ink);
  border-radius:10px;padding:8px 12px 8px 32px;
  font-size:.82rem;font-family:inherit;outline:none;
  transition:border-color .15s,background .15s,box-shadow .15s;}}
#search:focus{{border-color:var(--accent);background:var(--surface);
  box-shadow:0 0 0 3px rgba(102,126,234,.1);}}
#search::placeholder{{color:var(--muted)}}
.h-right{{display:flex;align-items:center;gap:8px;}}
.live-chip{{display:flex;align-items:center;gap:5px;font-size:.66rem;
  font-weight:800;letter-spacing:.07em;text-transform:uppercase;
  color:var(--accent2);padding:4px 10px;border-radius:999px;
  background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.2);}}
.live-dot{{width:6px;height:6px;border-radius:50%;background:#10B981;
  animation:lp 2s ease infinite;flex-shrink:0;}}
@keyframes lp{{
  0%,100%{{box-shadow:0 0 0 0 rgba(16,185,129,.5)}}
  50%{{box-shadow:0 0 0 5px rgba(16,185,129,0)}}
}}
.icon-btn{{width:34px;height:34px;border-radius:9px;
  border:1.5px solid var(--border);background:var(--surface);
  color:var(--ink3);font-size:.9rem;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:all .15s;}}
.icon-btn:hover{{border-color:var(--accent);color:var(--accent);
  background:rgba(102,126,234,.06);}}

/* ── Category nav ── */
.cat-strip{{border-top:1px solid var(--border);overflow-x:auto;
  scrollbar-width:none;}}
.cat-strip::-webkit-scrollbar{{display:none}}
.cat-nav{{display:flex;width:max-content;min-width:100%;}}
.cat-pill{{display:inline-flex;align-items:center;gap:5px;
  padding:8px 14px;color:var(--muted);font-size:.78rem;font-weight:600;
  border-bottom:2px solid transparent;white-space:nowrap;cursor:pointer;
  transition:all .15s;text-decoration:none;}}
.cat-pill:hover{{color:var(--ink2)}}
.cat-pill.active{{color:var(--accent);border-bottom-color:var(--accent);}}
.cat-dot{{width:5px;height:5px;border-radius:50%;flex-shrink:0;}}
.cat-count{{font-size:.62rem;font-weight:700;
  background:var(--surface2);color:var(--muted);
  padding:1px 6px;border-radius:999px;}}
.cat-pill.active .cat-count{{
  background:rgba(102,126,234,.12);color:var(--accent);}}

/* ── Main ── */
.main-wrap{{max-width:1200px;margin:0 auto;padding:28px 24px 100px;}}
.date-bar{{display:flex;align-items:center;margin-bottom:22px;gap:8px;
  font-size:.8rem;color:var(--muted);font-weight:500;}}
.date-bar strong{{color:var(--ink);font-weight:700;}}

/* ── Day summary ── */
.day-sum{{border-radius:var(--r);padding:22px 26px;margin-bottom:32px;
  background:var(--grad);color:#fff;position:relative;overflow:hidden;}}
.day-sum::before{{content:'';position:absolute;inset:0;opacity:.06;
  background-image:radial-gradient(ellipse at 85% 40%,#fff 0%,transparent 60%);}}
.day-sum::after{{content:'';position:absolute;bottom:-30px;right:-30px;
  width:200px;height:200px;border-radius:50%;
  background:rgba(255,255,255,.04);pointer-events:none;}}
.ds-label{{font-size:.59rem;font-weight:800;letter-spacing:.16em;
  text-transform:uppercase;opacity:.7;margin-bottom:7px;}}
.ds-text{{font-size:.92rem;line-height:1.78;position:relative;z-index:1;}}

/* ── Sections ── */
section{{margin-bottom:48px;}}
.sec-header{{display:flex;align-items:center;gap:10px;
  margin-bottom:16px;padding-bottom:12px;
  border-bottom:2px solid var(--border);position:relative;}}
.sec-header::after{{content:'';position:absolute;bottom:-2px;left:0;
  width:44px;height:2px;background:var(--c,var(--accent));
  border-radius:99px;transition:width .35s cubic-bezier(.4,0,.2,1);}}
section:hover .sec-header::after{{width:80px;}}
.sec-emoji{{font-size:1.15rem;line-height:1;}}
.sec-title{{font-size:1rem;font-weight:800;letter-spacing:-.02em;}}
.sec-count{{font-size:.67rem;font-weight:700;color:var(--muted);
  background:var(--surface2);border:1px solid var(--border);
  padding:2px 8px;border-radius:999px;margin-left:auto;}}

/* ── Card grid ── */
.card-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}}

/* ── Cards ── */
.card{{
  background:var(--surface);border-radius:var(--r);
  border:1px solid var(--border);box-shadow:var(--sh0);
  overflow:hidden;
  transition:box-shadow .25s cubic-bezier(.4,0,.2,1),
             transform .25s cubic-bezier(.4,0,.2,1),
             border-color .25s;
  animation:rise .45s ease both;
  border-top:3px solid var(--c,var(--accent));
  display:flex;flex-direction:column;
  will-change:transform;
}}
.card:hover{{
  box-shadow:var(--sh2);
  transform:translateY(-4px);
  border-color:var(--c,var(--accent));
}}
.card.hidden{{display:none!important}}
.card.hero{{grid-column:span 2}}
@keyframes rise{{
  from{{opacity:0;transform:translateY(16px)}}
  to{{opacity:1;transform:translateY(0)}}
}}

/* ── Card inner ── */
.card summary{{list-style:none;cursor:pointer;
  padding:16px 16px 12px;
  flex:1;display:flex;flex-direction:column;}}
.card summary::-webkit-details-marker{{display:none}}
.card-badge{{display:inline-flex;align-items:center;gap:4px;
  font-size:.58rem;font-weight:800;letter-spacing:.1em;
  text-transform:uppercase;color:var(--c,var(--accent));
  margin-bottom:7px;opacity:.9;}}
.badge-dot{{width:4px;height:4px;border-radius:50%;
  background:var(--c,var(--accent));}}
.qt{{font-size:.93rem;font-weight:700;line-height:1.46;
  margin-bottom:7px;color:var(--ink);letter-spacing:-.012em;}}
.card.hero .qt{{font-size:1.08rem;font-weight:800;}}
.take{{font-size:.8rem;color:var(--ink3);line-height:1.67;
  display:-webkit-box;-webkit-line-clamp:2;
  -webkit-box-orient:vertical;overflow:hidden;}}
.card.hero .take{{-webkit-line-clamp:3;}}

/* ── Card meta ── */
.card-meta{{display:flex;flex-wrap:wrap;align-items:center;
  gap:5px;padding-top:10px;margin-top:auto;
  border-top:1px solid var(--border);font-size:.68rem;}}
.src-pill{{background:var(--surface2);color:var(--ink2);
  border-radius:5px;padding:1px 7px;
  font-weight:700;font-size:.64rem;}}
.meta-dot{{color:var(--border2);}}
.pub-time,.read-t{{color:var(--muted);}}
.orig{{color:var(--c,var(--accent));text-decoration:none;
  font-weight:700;margin-left:auto;font-size:.78rem;
  display:flex;align-items:center;gap:2px;
  transition:opacity .15s;}}
.orig:hover{{opacity:.75;}}
.toggler{{color:var(--muted);font-weight:600;font-size:.67rem;
  padding:2px 9px;border-radius:6px;
  background:var(--surface2);border:1px solid var(--border);
  cursor:pointer;transition:all .15s;font-family:inherit;}}
.toggler:hover{{background:var(--c,var(--accent));color:#fff;
  border-color:var(--c,var(--accent));}}
details[open] .toggler .cls-txt{{display:none}}
details:not([open]) .toggler .opn-txt{{display:none}}

/* ── Expanded ── */
.exp{{padding:4px 16px 16px;
  border-top:1px dashed var(--border);background:var(--surface);
  animation:expIn .2s ease;}}
@keyframes expIn{{
  from{{opacity:0;transform:translateY(-6px)}}
  to{{opacity:1;transform:translateY(0)}}
}}
.exp-block{{margin-top:14px;}}
.exp-block h4{{font-size:.58rem;font-weight:800;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);margin-bottom:7px;}}
.exp-block p{{font-size:.86rem;line-height:1.77;color:var(--ink2)}}
.exp-block.impact{{
  background:linear-gradient(135deg,rgba(16,185,129,.07),rgba(16,185,129,.02));
  border-radius:10px;padding:12px 14px;border-left:3px solid #10B981;}}
.exp-block.impact h4{{color:#059669}}
.exp-block.impact p{{color:var(--ink)}}
.terms{{display:flex;flex-direction:column;gap:7px;margin-top:4px;}}
.term{{background:var(--surface2);border-radius:8px;padding:9px 12px;
  font-size:.82rem;color:var(--ink);
  border-left:3px solid var(--c,var(--accent));}}
.term b{{color:var(--c,var(--accent));}}
.exp-actions{{display:flex;align-items:center;gap:8px;
  margin-top:16px;flex-wrap:wrap;}}
.read-orig{{display:inline-flex;align-items:center;gap:5px;
  font-size:.8rem;color:#fff;
  background:var(--c,var(--grad));text-decoration:none;
  font-weight:700;padding:8px 16px;border-radius:9px;
  transition:opacity .15s,transform .15s;}}
.read-orig:hover{{opacity:.88;transform:translateY(-1px);}}
.share-btn{{font-size:.75rem;color:var(--muted);
  background:var(--surface2);border:1px solid var(--border);
  padding:7px 13px;border-radius:9px;cursor:pointer;
  font-weight:600;font-family:inherit;transition:all .15s;}}
.share-btn:hover{{color:var(--accent);border-color:var(--accent);}}

/* ── No match ── */
.no-match{{color:var(--muted);font-size:.88rem;text-align:center;
  padding:48px 0;display:none;}}

/* ── Footer ── */
.disclaimer{{color:var(--muted);font-size:.7rem;text-align:center;
  padding:18px 0 8px;border-top:1px solid var(--border);margin-top:28px;}}
footer{{text-align:center;padding:18px;font-size:.74rem;color:var(--muted);
  border-top:1px solid var(--border);background:var(--surface);}}
footer a{{color:var(--accent);text-decoration:none;}}
footer a:hover{{text-decoration:underline;}}

/* ── Back to top ── */
#btt{{position:fixed;bottom:24px;right:20px;
  background:var(--grad);color:#fff;border:none;
  width:40px;height:40px;border-radius:12px;font-size:.95rem;
  cursor:pointer;display:none;align-items:center;justify-content:center;
  box-shadow:0 4px 16px rgba(102,126,234,.4);
  transition:opacity .2s,transform .2s;z-index:50;}}
#btt.show{{display:flex;}}
#btt:hover{{opacity:.88;transform:translateY(-2px);}}

/* ── Responsive ── */
@media(max-width:900px){{
  .card-grid{{grid-template-columns:repeat(2,1fr);}}
  .card.hero{{grid-column:span 2;}}
}}
@media(max-width:640px){{
  .card-grid{{grid-template-columns:1fr;}}
  .card.hero{{grid-column:span 1;}}
  .brand-name{{font-size:1.05rem;}}
  .main-wrap{{padding:20px 14px 80px;}}
  .h-inner{{padding:0 14px;}}
  .h-center{{display:none;}}
  .live-chip{{display:none;}}
}}
</style>
</head>
<body>
<div id="prog"></div>
{ticker}
<header>
  <div class="h-inner">
    <div class="h-row1">
      <a class="brand-logo" href="#">
        <div class="brand-icon">📈</div>
        <div>
          <div class="brand-name">{site_name}</div>
          <div class="brand-sub">Finance news · simplified daily</div>
        </div>
      </a>
      <div class="h-center">
        <span class="s-ic">🔍</span>
        <input id="search" type="search" placeholder="Search stories…" autocomplete="off">
      </div>
      <div class="h-right">
        <div class="live-chip"><span class="live-dot"></span>Live</div>
        <button class="icon-btn" id="theme-btn" title="Toggle theme">🌙</button>
      </div>
    </div>
    <div class="cat-strip">
      <nav class="cat-nav" id="cat-nav">{nav_links}</nav>
    </div>
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
  var t=localStorage.getItem('theme');
  if(!t){{t=window.matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';}}
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
window.addEventListener('scroll',function(){{
  btt.classList.toggle('show',window.scrollY>400);
}},{{passive:true}});
btt.addEventListener('click',function(){{
  window.scrollTo({{top:0,behavior:'smooth'}});
}});
document.querySelectorAll('.card').forEach(function(c,i){{
  c.style.animationDelay=(i*.04)+'s';
}});
var inp=document.getElementById('search');
var nm=document.getElementById('no-match');
if(inp){{
  inp.addEventListener('input',function(){{
    var q=this.value.toLowerCase().trim();var v=0;
    document.querySelectorAll('.card').forEach(function(c){{
      var m=!q||c.textContent.toLowerCase().includes(q);
      c.classList.toggle('hidden',!m);if(m)v++;
    }});
    nm.style.display=(v===0&&q)?'block':'none';
  }});
}}
var pills=document.querySelectorAll('.cat-pill');
var secs=document.querySelectorAll('section[id]');
function setActive(id){{
  pills.forEach(function(p){{
    var match=(id==='all'&&p.getAttribute('data-target')==='all')||
              p.getAttribute('data-target')===id;
    p.classList.toggle('active',match);
  }});
}}
if('IntersectionObserver' in window&&secs.length){{
  var io=new IntersectionObserver(function(entries){{
    entries.forEach(function(e){{
      if(e.isIntersecting)setActive(e.target.id);
    }});
  }},{{rootMargin:'-5% 0px -70% 0px',threshold:0}});
  secs.forEach(function(s){{io.observe(s);}});
  window.addEventListener('scroll',function(){{
    if(window.scrollY<150)setActive('all');
  }},{{passive:true}});
}}
pills.forEach(function(a){{
  a.addEventListener('click',function(){{
    var id=this.getAttribute('data-target');
    if(id==='all'){{window.scrollTo({{top:0,behavior:'smooth'}});setActive('all');return;}}
    var el=document.getElementById(id);
    if(el)el.scrollIntoView({{behavior:'smooth',block:'start'}});
  }});
}});
document.querySelectorAll('.share-btn').forEach(function(btn){{
  btn.addEventListener('click',function(){{
    var qt=this.closest('.card')?.querySelector('.qt')?.textContent||'';
    if(navigator.share)navigator.share({{title:qt,url:window.location.href}});
    else if(navigator.clipboard)navigator.clipboard.writeText(qt+' '+window.location.href).then(function(){{
      btn.textContent='✓ Copied!';
      setTimeout(function(){{btn.textContent='⎘ Share';}},2000);
    }});
  }});
}});
</script>
</body>
</html>"""


def _render_ticker(market_data):
    items = []
    for sym, info in (market_data or {}).items():
        price = info.get("price", "")
        chg   = info.get("change_pct", 0) or 0
        if chg > 0:
            cls = "up"; arrow = "▲"
        elif chg < 0:
            cls = "dn"; arrow = "▼"
        else:
            cls = "fl"; arrow = "—"
        items.append(
            f'<span class="ti">'
            f'<span class="tn">{sym}</span>'
            f'<span class="tp">{price}</span>'
            f'<span class="{cls} ti-arr">{arrow}</span>'
            f'<span class="{cls}">{chg:+.2f}%</span>'
            f'</span>'
        )
    if not items:
        return ""
    row = "".join(items)
    return f'<div class="tkr"><div class="tkr-inner">{row}{row}</div></div>'


def _render_day_summary(text):
    if not text:
        return ""
    return (
        f'<div class="day-sum">'
        f'<div class="ds-label">📋 Market Briefing</div>'
        f'<div class="ds-text">{text}</div>'
        f'</div>'
    )


def render_card(a, color, cat_label="", cat_emoji="", hero=False):
    hero_cls = " hero" if hero else ""
    q    = a.get("q") or a.get("title", "Untitled")
    take = a.get("take", "")
    url  = a.get("url") or a.get("link", "#")
    pub  = _fmt_pub(a.get("published", ""))
    src  = _src_label(url, a.get("source", ""))
    rt   = _est_read(a)
    exp  = a.get("expand") or {}
    if not isinstance(exp, dict):
        exp = {}

    badge = ""
    if cat_label:
        badge = (
            f'<div class="card-badge" style="--c:{color}">'
            f'<span class="badge-dot"></span>'
            f'{cat_emoji} {cat_label}'
            f'</div>'
        )

    meta = (
        f'<div class="card-meta">'
        f'<span class="src-pill">{src}</span>'
        f'<span class="meta-dot">·</span>'
        f'<span class="pub-time">{pub}</span>'
        f'<span class="meta-dot">·</span>'
        f'<span class="read-t">{rt}</span>'
        f'<a class="orig" href="{url}" target="_blank" rel="noopener">↗</a>'
        f'<button class="toggler">'
        f'<span class="opn-txt">▾ More</span>'
        f'<span class="cls-txt">▴ Less</span>'
        f'</button>'
        f'</div>'
    )

    exp_html = ""
    if exp:
        what   = exp.get("what", "")
        why    = exp.get("why", "")
        impact = exp.get("impact", "")
        terms  = exp.get("terms") or []

        parts = ""
        if what:
            parts += f'<div class="exp-block"><h4>What happened</h4><p>{what}</p></div>'
        if why:
            parts += f'<div class="exp-block"><h4>Why it matters</h4><p>{why}</p></div>'
        if impact:
  2         parts += f'<div class="exp-block impact"><h4>Market impact</h4><p>{impact}</p></div>'
        if terms:
            tdivs = "".join(
                f'<div class="term"><b>{t.get("term","")}</b> — {t.get("def","")}</div>'
                for t in terms if isinstance(t, dict)
            )
            parts += f'<div class="exp-block"><h4>Key terms</h4><div class="terms">{tdivs}</div></div>'

        parts += (
            f'<div class="exp-actions">'
            f'<a class="read-orig" href="{url}" target="_blank" rel="noopener"'
            f' style="background:{color}">Read original ↗</a>'
            f'<button class="share-btn">⎘ Share</button>'
            f'</div>'
        )
        exp_html = f'<div class="exp" style="--c:{color}">{parts}</div>'

    return (
        f'<details class="card{hero_cls}" style="--c:{color}">'
        f'<summary>'
        f'{badge}'
        f'<div class="card-top">'
        f'<div class="qt">{q}</div>'
        f'<div class="take">{take}</div>'
        f'</div>'
        f'{meta}'
        f'</summary>'
        f'{exp_html}'
        f'</details>'
    )


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
        cards = "".join(
            render_card(a, color, label, emoji, hero=(i == 0))
            for i, a in enumerate(arts)
        )
        sections_html += (
            f'<section id="{slug}" style="--c:{color}">'
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
