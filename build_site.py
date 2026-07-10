# -*- coding: utf-8 -*-
"""Render newsletter JSON as English web pages, archives, email HTML, and RSS."""
from __future__ import annotations

import datetime as dt
import email.utils
import glob
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from config import NEWSLETTERS, SITE_NAME, SITE_URL

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
ISSUES_JSON = ROOT / "issues.json"
KST = ZoneInfo("Asia/Seoul")

TAG_CLS = {"ai-briefing": "tag-red"}


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def paragraphs(value: str) -> str:
    return "".join(f"<p>{esc(part.strip())}</p>" for part in (value or "").split("\n") if part.strip())


def item_headline(item: dict) -> str:
    return str(item.get("headline") or item.get("title_en") or item.get("title_ko") or "")


def item_summary(item: dict) -> str:
    return str(item.get("summary") or item.get("body_en") or item.get("body_ko") or "")


def og_image(url: str) -> str:
    if not url:
        return ""
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (NayeonNewsletterBot/1.0)"})
        document = urllib.request.urlopen(request, timeout=8).read(150_000).decode("utf-8", "ignore")
        patterns = (
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        )
        for pattern in patterns:
            match = re.search(pattern, document, re.I)
            if match:
                return match.group(1)
    except Exception as exc:
        print(f"[image] skipped {url}: {exc}")
    return ""


def render_item_web(item: dict) -> str:
    image = f'<img src="{esc(item.get("image"))}" alt="" loading="lazy">' if item.get("image") else ""
    return f"""<article class="article">
  <span class="cat">{esc(item.get('category'))}</span>
  {image}
  <h3>{esc(item_headline(item))}</h3>
  {paragraphs(item_summary(item))}
  <a class="src" href="{esc(item.get('link'))}" target="_blank" rel="noopener">Read the original source →</a>
</article>"""


def render_issue_page(data: dict) -> str:
    definition = NEWSLETTERS[data["slug"]]
    items = "\n".join(render_item_web(item) for item in data["items"])
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(data['title'])} — {SITE_NAME}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../style.css"></head>
<body><div class="inner-page">
<header class="site-header">
  <a class="wordmark" href="../../index.html"><strong>NAYEON KIM</strong><span>NEWSLETTER</span></a>
  <nav class="nav-right"><a href="index.html">ARCHIVE</a><a class="nav-circle" href="../../index.html#subscribe">♡</a></nav>
</header>
<main class="issue-wrap">
  <div class="issue-hero">
    <span class="tag {TAG_CLS.get(data['slug'], '')}">{esc(definition['name'])}</span>
    <h1>{esc(data['title'])}</h1>
    <p class="issue-meta">{esc(definition['tagline'])}</p>
    <p class="issue-meta">{esc(data.get('intro'))}</p>
    <p class="issue-meta">{data['date']} · 07:00 KST</p>
  </div>
  {items}
  <a class="back" href="index.html">← View all issues</a>
</main>
<footer class="site-footer"><div class="footer-bottom"><p>© 2026 {SITE_NAME}</p><a href="../../index.html">HOME</a><a href="../../index.html#subscribe">SUBSCRIBE</a></div></footer>
</div></body></html>"""


def render_archive(slug: str, issues: list[dict]) -> str:
    definition = NEWSLETTERS[slug]
    cards = "\n".join(
        f'<a class="news-card ai-card" href="{issue["date"]}.html">'
        f'<div class="news-thumb"><span>AI NEWS</span><small>{issue["date"]}</small></div>'
        f'<p class="news-cat">{esc(definition["name"])}</p>'
        f'<h3 class="news-title">{esc(issue["title"])}</h3><em>READ ISSUE →</em></a>'
        for issue in issues
    )
    if not cards:
        cards = '<div class="empty"><span>The first issue is on its way.</span><p>New issues will appear here automatically after publication.</p></div>'
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(definition['name'])} — Archive</title>
<link rel="stylesheet" href="../../style.css"></head>
<body><div class="inner-page">
<header class="site-header"><a class="wordmark" href="../../index.html"><strong>NAYEON KIM</strong><span>NEWSLETTER</span></a></header>
<main class="archive-wrap"><div class="archive-head"><p class="section-kicker">NEWSLETTER ARCHIVE</p><h1>{esc(definition['name'])}</h1><p>{esc(definition['tagline'])}</p></div>
<div class="news-grid">{cards}</div><a class="back" href="../../index.html">← Back to home</a></main>
</div></body></html>"""


def render_email_body(data: dict) -> str:
    blocks: list[str] = []
    for item in data["items"]:
        image = (
            f'<img src="{esc(item.get("image"))}" width="100%" style="display:block;border-radius:12px;border:1px solid #c8bfbc;margin:10px 0 16px;" alt="">'
            if item.get("image")
            else ""
        )
        blocks.append(
            f'<div style="background:#fffdfb;border:1px solid #c8bfbc;border-radius:16px;padding:24px;margin:0 0 18px;">'
            f'<div style="font-size:11px;letter-spacing:.08em;color:#6f6967;font-weight:700;">{esc(item.get("category"))}</div>'
            f'{image}<h2 style="font-family:Georgia,serif;font-size:25px;line-height:1.2;margin:14px 0 10px;">{esc(item_headline(item))}</h2>'
            f'<p style="font-size:15px;line-height:1.75;margin:0 0 18px;">{esc(item_summary(item))}</p>'
            f'<a href="{esc(item.get("link"))}" style="display:inline-block;background:#f8e3ed;border-radius:999px;padding:10px 16px;color:#262322;font-weight:700;text-decoration:none;font-size:12px;">Read the original source →</a>'
            f'</div>'
        )
    web_url = f"{SITE_URL}/newsletters/{data['slug']}/{data['date']}.html"
    return (
        f'<div style="font-family:Arial,Helvetica,sans-serif;color:#262322;max-width:620px;margin:0 auto;">'
        f'<div style="text-align:center;background:#fffdfb;border:1px solid #c8bfbc;border-radius:18px;padding:32px 24px;margin-bottom:18px;">'
        f'<div style="font-family:Georgia,serif;font-size:22px;font-weight:700;">NAYEON KIM NEWSLETTER</div>'
        f'<h1 style="font-family:Georgia,serif;font-size:32px;line-height:1.15;margin:20px 0 10px;">{esc(data["title"])}</h1>'
        f'<p style="font-size:14px;line-height:1.65;color:#6f6967;">{esc(data.get("intro"))}</p>'
        f'</div>{"".join(blocks)}'
        f'<div style="text-align:center;padding:20px;font-size:12px;"><a href="{web_url}" style="color:#262322;">View in browser</a></div></div>'
    )


def render_full_email(data: dict) -> str:
    return f'<!DOCTYPE html><html lang="en"><body style="margin:0;padding:28px 12px;background:#f2d3e2;">{render_email_body(data)}</body></html>'


def load_issues() -> list[dict]:
    if not ISSUES_JSON.exists():
        return []
    try:
        data = json.loads(ISSUES_JSON.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_issues(issues: list[dict]) -> None:
    ISSUES_JSON.write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")


def rss_cdata(value: str) -> str:
    return value.replace("]]>", "]]]]><![CDATA[>")


def render_rss(slug: str, content_files: list[Path]) -> str:
    definition = NEWSLETTERS[slug]
    entries = []
    for path in sorted(content_files, reverse=True)[:30]:
        data = json.loads(path.read_text(encoding="utf-8"))
        issue_url = f"{SITE_URL}/newsletters/{slug}/{data['date']}.html"
        date = dt.datetime.strptime(data["date"], "%Y-%m-%d").replace(hour=6, minute=50, tzinfo=KST)
        content = render_email_body(data)
        entries.append(f"""<item>
<title>{esc(data['title'])}</title>
<link>{esc(issue_url)}</link>
<guid isPermaLink="true">{esc(issue_url)}</guid>
<pubDate>{email.utils.format_datetime(date)}</pubDate>
<description><![CDATA[{rss_cdata(esc(data.get('intro')))}]]></description>
<content:encoded><![CDATA[{rss_cdata(content)}]]></content:encoded>
</item>""")
    build_time = email.utils.format_datetime(dt.datetime.now(KST))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
<title>{esc(definition['name'])}</title>
<link>{esc(SITE_URL + '/newsletters/' + slug + '/')}</link>
<description>{esc(definition['tagline'])}</description>
<language>en-US</language>
<lastBuildDate>{build_time}</lastBuildDate>
<generator>Nayeon Newsletter Automation</generator>
{"".join(entries)}
</channel></rss>"""


def build(json_path: Path, fetch_images: bool = True) -> Path:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    slug = data["slug"]
    date = data["date"]

    if fetch_images:
        for item in data["items"]:
            if not item.get("image"):
                item["image"] = og_image(item.get("link", ""))
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    newsletter_dir = ROOT / "newsletters" / slug
    newsletter_dir.mkdir(parents=True, exist_ok=True)
    (newsletter_dir / f"{date}.html").write_text(render_issue_page(data), encoding="utf-8")

    issues = [item for item in load_issues() if not (item.get("slug") == slug and item.get("date") == date)]
    issues.append({"slug": slug, "date": date, "title": data["title"]})
    issues.sort(key=lambda item: item["date"], reverse=True)
    save_issues(issues)
    (newsletter_dir / "index.html").write_text(
        render_archive(slug, [item for item in issues if item["slug"] == slug]), encoding="utf-8"
    )

    OUT.mkdir(parents=True, exist_ok=True)
    email_path = OUT / f"email_{slug}_{date}.html"
    email_path.write_text(render_full_email(data), encoding="utf-8")

    feed_dir = ROOT / "feeds"
    feed_dir.mkdir(parents=True, exist_ok=True)
    content_files = [Path(path) for path in glob.glob(str(OUT / f"content_{slug}_*.json"))]
    (feed_dir / f"{slug}.xml").write_text(render_rss(slug, content_files), encoding="utf-8")
    print(f"[build] {slug} {date}: web + archive + email + RSS")
    return email_path


if __name__ == "__main__":
    paths = [Path(value) for value in sys.argv[1:]] or [Path(value) for value in sorted(glob.glob(str(OUT / "content_*.json")))]
    if not paths:
        raise SystemExit("No generated content JSON files were found.")
    fetch_images = os.getenv("FETCH_IMAGES", "1") == "1"
    for path in paths:
        build(path, fetch_images=fetch_images)
