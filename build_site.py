# -*- coding: utf-8 -*-
"""
build_site.py — generate.py가 만든 JSON을 사이트 페이지 + 이메일 HTML로 렌더링.

- site/newsletters/<slug>/<date>.html  (웹 페이지)
- site/newsletters/<slug>/index.html   (해당 뉴스레터 아카이브)
- site/data/issues.json                (홈 화면 최신 호 목록)
- out/email_<slug>_<date>.html         (이메일 발송용, 인라인 스타일)

기사 이미지: 각 링크의 og:image 메타태그를 가져와 삽입 (원칙 #4).
"""
import json, glob, html, os, re, sys
import urllib.request
from config import NEWSLETTERS, SITE_NAME, SITE_URL

ROOT = os.path.join(os.path.dirname(__file__), "..")
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(ROOT, "out")

TAG_CLS = {"economics": "tag-blue", "ai-briefing": "tag-red", "success-stories": "tag-green"}


def og_image(url: str) -> str:
    """링크된 기사의 대표 이미지(og:image) URL을 추출. 실패 시 빈 문자열."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (newsletter-bot)"})
        head = urllib.request.urlopen(req, timeout=8).read(120000).decode("utf-8", "ignore")
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', head) \
            or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', head)
        return m.group(1) if m else ""
    except Exception:
        return ""


def esc(s):
    return html.escape(s or "")


def para(s):
    return "".join(f"<p>{esc(p.strip())}</p>" for p in (s or "").split("\n") if p.strip())


# ───────────────────────── 웹 페이지 렌더링 ─────────────────────────
def render_item_web(it) -> str:
    img = f'<img src="{esc(it.get("image", ""))}" alt="" loading="lazy">' if it.get("image") else ""
    ko = (f'<span class="lang-label">한국어</span><h3>{esc(it.get("title_ko"))}</h3>{para(it.get("body_ko"))}'
          if it.get("title_ko") else "")
    en = (f'<span class="lang-label">English</span><h3>{esc(it.get("title_en"))}</h3>{para(it.get("body_en"))}'
          if it.get("title_en") else "")
    return f"""<article class="article">
  <span class="cat">{esc(it.get("category"))}</span>
  {img}{ko}{en}
  <a class="src" href="{esc(it.get("link"))}" target="_blank" rel="noopener">원문 기사 보기 · Read the article →</a>
</article>"""


def render_issue_page(data) -> str:
    nl = NEWSLETTERS[data["slug"]]
    items = "\n".join(render_item_web(it) for it in data["items"])
    intro = f'<p class="issue-meta">{esc(data.get("intro"))}</p>' if data.get("intro") else ""
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(data["title"])} — {SITE_NAME}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/style.css"></head>
<body>
<div class="inner-page">
<header class="site-header">
  <a class="wordmark" href="../../index.html"><strong>NAYEON KIM</strong><span>NEWSLETTER</span></a>
  <nav class="nav-right"><a href="index.html">ARCHIVE</a><a class="nav-circle" href="../../index.html#subscribe">♡</a></nav>
</header>
<main class="issue-wrap">
  <div class="issue-hero">
    <span class="tag {TAG_CLS[data["slug"]]}">{esc(nl["name"])}</span>
    <h1>{esc(data["title"])}</h1>
    <p class="issue-meta">{esc(nl["tagline"])}</p>
    {intro}
    <p class="issue-meta">{data["date"]} · 07:00 KST</p>
  </div>
  {items}
  <a class="back" href="index.html">← 지난 호 전체 보기</a>
</main>
<footer class="site-footer"><div class="footer-bottom"><p>© 2026 {SITE_NAME}</p><a href="../../index.html">HOME</a><a href="../../index.html#subscribe">SUBSCRIBE</a></div></footer>
</div>
</body></html>"""


def render_archive(slug, issues) -> str:
    nl = NEWSLETTERS[slug]
    cls = {"economics": "economics-card", "ai-briefing": "ai-card", "success-stories": "success-card"}[slug]
    icon = {"economics": "ECONOMICS", "ai-briefing": "AI NEWS", "success-stories": "SUCCESS"}[slug]
    cards = "\n".join(
        f'<a class="news-card {cls}" href="{i["date"]}.html">'
        f'<div class="news-thumb"><span>{icon}</span><small>{i["date"]}</small></div>'
        f'<p class="news-cat">{esc(nl["name"])}</p>'
        f'<h3 class="news-title">{esc(i["title"])}</h3><em>READ ISSUE →</em></a>'
        for i in issues)
    empty = '<div class="empty"><span>첫 발행을 준비하고 있어요.</span><p>첫 호가 발행되면 이곳에 자동으로 정리됩니다.</p></div>'
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(nl["name"])} — Archive</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/style.css"></head>
<body>
<div class="inner-page">
<header class="site-header">
  <a class="wordmark" href="../../index.html"><strong>NAYEON KIM</strong><span>NEWSLETTER</span></a>
  <nav class="nav-right"><a href="../../index.html#newsletters">NEWSLETTERS</a><a class="nav-circle" href="../../index.html#subscribe">♡</a></nav>
</header>
<main class="archive-wrap">
  <div class="archive-head"><p class="section-kicker">NEWSLETTER ARCHIVE</p><h1>{esc(nl["name"])}</h1><p>{esc(nl["tagline"])}</p></div>
  <div class="news-grid">{cards or empty}</div>
  <a class="back" href="../../index.html">← 홈으로 돌아가기</a>
</main>
<footer class="site-footer"><div class="footer-bottom"><p>© 2026 {SITE_NAME}</p><a href="../../index.html">HOME</a><a href="../../index.html#subscribe">SUBSCRIBE</a></div></footer>
</div>
</body></html>"""


# ───────────────────────── 이메일 렌더링 (인라인 스타일) ─────────────────────────
def render_email(data) -> str:
    nl = NEWSLETTERS[data["slug"]]
    blocks = []
    for it in data["items"]:
        img = (f'<img src="{esc(it["image"])}" width="100%" '
               f'style="border-radius:12px;border:1px solid #b4aaa7;margin:8px 0 14px;" alt="">'
               if it.get("image") else "")
        ko = (f'<h3 style="font-family:Georgia,serif;font-size:24px;margin:14px 0 8px;">{esc(it.get("title_ko"))}</h3>'
              f'<p style="margin:0 0 12px;line-height:1.75;">{esc(it.get("body_ko"))}</p>' if it.get("title_ko") else "")
        en = (f'<h3 style="font-family:Georgia,serif;font-size:24px;margin:14px 0 8px;">{esc(it.get("title_en"))}</h3>'
              f'<p style="margin:0 0 12px;line-height:1.75;">{esc(it.get("body_en"))}</p>' if it.get("title_en") else "")
        blocks.append(f"""
<tr><td style="padding:26px;background:#fffdfb;border:1px solid #c8beba;border-radius:18px;">
  <span style="display:inline-block;background:#f8e3ed;border-radius:999px;padding:5px 10px;font-size:10px;font-weight:bold;letter-spacing:.08em;">{esc(it.get("category"))}</span>
  {img}{ko}{en}
  <a href="{esc(it.get("link"))}" style="display:inline-block;background:#f8e3ed;border-radius:999px;padding:9px 16px;color:#262322;font-weight:bold;text-decoration:none;font-size:12px;">
     원문 기사 보기 · Read the article →</a>
</td></tr><tr><td height="16"></td></tr>""")

    page_url = f"{SITE_URL}/newsletters/{data['slug']}/{data['date']}.html"
    return f"""<!DOCTYPE html><html><body style="margin:0;background:#f2d3e2;
font-family:Arial,sans-serif;color:#262322;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 12px;">
<table role="presentation" width="620" style="max-width:620px;" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:36px 24px;background:#fffdfb;border-radius:22px 22px 0 0;">
    <div style="font-family:Georgia,serif;font-size:24px;font-weight:bold;">NAYEON KIM</div>
    <div style="font-size:9px;letter-spacing:.25em;margin-top:5px;">NEWSLETTER</div>
    <h1 style="font-family:Georgia,serif;font-weight:normal;font-size:34px;margin:22px 0 8px;">{esc(data["title"])}</h1>
    <p style="margin:0;font-size:13px;color:#77706d;">{esc(nl["tagline"])}</p>
    <p style="margin:7px 0 0;font-size:11px;color:#77706d;">{data["date"]} · 07:00 KST</p>
  </td></tr>
  <tr><td height="16"></td></tr>
  {"".join(blocks)}
  <tr><td align="center" style="padding:22px;font-size:11px;background:#cfe4ef;border-radius:0 0 22px 22px;">
    <a href="{page_url}" style="color:#262322;">웹에서 보기</a> ·
    <a href="{SITE_URL}" style="color:#262322;">지난 호 아카이브</a> ·
    <a href="{{{{unsubscribe_url}}}}" style="color:#262322;">구독 해지</a>
  </td></tr>
</table></td></tr></table></body></html>"""


# ───────────────────────── 메인 ─────────────────────────
def build(json_path: str, fetch_images: bool = True):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    slug, date = data["slug"], data["date"]

    if fetch_images:
        for it in data["items"]:
            if not it.get("image"):
                it["image"] = og_image(it.get("link", ""))

    nl_dir = os.path.join(SITE, "newsletters", slug)
    os.makedirs(nl_dir, exist_ok=True)

    with open(os.path.join(nl_dir, f"{date}.html"), "w", encoding="utf-8") as f:
        f.write(render_issue_page(data))

    idx_path = os.path.join(SITE, "data", "issues.json")
    issues = []
    if os.path.exists(idx_path):
        with open(idx_path, encoding="utf-8") as f:
            issues = json.load(f)
    issues = [i for i in issues if not (i["slug"] == slug and i["date"] == date)]
    issues.insert(0, {"slug": slug, "date": date, "title": data["title"]})
    issues.sort(key=lambda i: i["date"], reverse=True)
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)

    with open(os.path.join(nl_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_archive(slug, [i for i in issues if i["slug"] == slug]))

    email_path = os.path.join(OUT, f"email_{slug}_{date}.html")
    with open(email_path, "w", encoding="utf-8") as f:
        f.write(render_email(data))

    print(f"[build] {slug} {date} → 페이지 + 아카이브 + 이메일 완료")
    return email_path


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(OUT, "content_*.json")))
    fetch = os.environ.get("FETCH_IMAGES", "1") == "1"
    for p in paths:
        build(p, fetch_images=fetch)
