"""Fetch and normalize articles from RSS feeds."""
import hashlib
import html
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 (compatible; FinanceDigestBot/1.0)"}


def _clean(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)          # strip tags
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_rss(data):
    """Parse RSS 2.0 or Atom. Returns list of dicts."""
    root = ET.fromstring(data)
    items = []
    # RSS 2.0
    for item in root.findall(".//item"):
        items.append({
            "title": _clean(item.findtext("title")),
            "summary": _clean(item.findtext("description")),
            "link": (item.findtext("link") or "").strip(),
            "published": (item.findtext("pubDate") or "").strip(),
        })
    # Atom fallback
    if not items:
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//a:entry", ns):
            link_el = entry.find("a:link", ns)
            items.append({
                "title": _clean(entry.findtext("a:title", namespaces=ns)),
                "summary": _clean(entry.findtext("a:summary", namespaces=ns)
                                  or entry.findtext("a:content", namespaces=ns)),
                "link": link_el.get("href", "") if link_el is not None else "",
                "published": (entry.findtext("a:updated", namespaces=ns) or "").strip(),
            })
    return items


def fetch_feed(url, timeout=20):
    """Fetch one feed; returns [] on any failure (dead feeds are fine)."""
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=timeout).read()
        return _parse_rss(data)
    except Exception as e:
        print(f"  [skip] {url}: {type(e).__name__}: {e}")
        return []


def _fingerprint(title):
    """Loose dedupe key: lowercase alphanumeric words."""
    words = re.findall(r"[a-z0-9]+", title.lower())
    return " ".join(words[:10])


def fetch_category(cat_key, cat_cfg, seen_global):
    """Fetch all feeds in a category, dedupe, cap at max_articles."""
    collected, seen_local = [], set()
    for feed_url in cat_cfg["feeds"]:
        entries = fetch_feed(feed_url)
        print(f"  {feed_url} -> {len(entries)} entries")
        source = re.sub(r"^www\.", "", re.sub(r"^https?://([^/]+).*", r"\1", feed_url))
        for e in entries:
            if not e["title"] or not e["link"]:
                continue
            fp = _fingerprint(e["title"])
            if fp in seen_local or fp in seen_global:
                continue
            seen_local.add(fp)
            e["source"] = source
            e["id"] = hashlib.md5(e["link"].encode()).hexdigest()[:10]
            collected.append(e)
        time.sleep(0.5)  # be polite
    seen_global |= seen_local
    # Prefer entries with a usable summary, keep feed order (freshest first per feed)
    collected.sort(key=lambda e: len(e["summary"]) < 40)
    return collected[: cat_cfg["max_articles"]]


def fetch_all(categories):
    """Returns {category_key: [article, ...]}"""
    out, seen = {}, set()
    for key, cfg in categories.items():
        print(f"[fetch] {cfg['label']}")
        out[key] = fetch_category(key, cfg, seen)
        print(f"  -> kept {len(out[key])}")
    return out
