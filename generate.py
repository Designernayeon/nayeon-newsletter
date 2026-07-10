# -*- coding: utf-8 -*-
"""
generate.py — Claude API(웹 검색 포함)로 오늘자 뉴스레터 콘텐츠를 JSON으로 생성.

사용법:
    python generate.py                # 오늘 발행 대상 전체 (수요일이면 3종, 아니면 2종)
    python generate.py economics      # 특정 뉴스레터만
출력:
    out/content_<slug>_<YYYY-MM-DD>.json
필요 환경변수:
    ANTHROPIC_API_KEY
"""
import json, os, re, sys, datetime
from zoneinfo import ZoneInfo
import anthropic
from config import NEWSLETTERS, SITE_NAME, EDITORIAL_RULES

KST = ZoneInfo("Asia/Seoul")
OUT = os.path.join(os.path.dirname(__file__), "..", "out")


def today():
    return datetime.datetime.now(KST)


def due_today(slug: str, now=None) -> bool:
    now = now or today()
    sched = NEWSLETTERS[slug]["schedule"]
    return sched == "daily" or (sched == "wednesday" and now.weekday() == 2)


def _fill(prompt: str, now) -> str:
    week_of_month = (now.day - 1) // 7 + 1
    return (prompt
            .replace("{date}", now.strftime("%Y-%m-%d"))
            .replace("{date_kr}", f"{now.year}년 {now.month}월 {now.day}일")
            .replace("{yy}", now.strftime("%y"))
            .replace("{m}", str(now.month))
            .replace("{w}", str(week_of_month)))


def _extract_json(text: str) -> dict:
    """모델 응답에서 첫 번째 완전한 JSON 오브젝트를 추출."""
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M)
    start = text.find("{")
    if start == -1:
        raise ValueError("응답에 JSON이 없습니다.")
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("JSON이 중간에 끊겼습니다.")


def generate(slug: str, now=None) -> str:
    now = now or today()
    nl = NEWSLETTERS[slug]
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 사용

    system = EDITORIAL_RULES.format(site_name=SITE_NAME, date=now.strftime("%Y-%m-%d"))
    print(f"[generate] {slug} … 웹 검색 기반 생성 시작")

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=12000,
        system=system,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
        messages=[{"role": "user", "content": _fill(nl["prompt"], now)}],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    data = _extract_json(text)

    # 최소 검증
    assert data.get("title"), "title 누락"
    assert len(data.get("items", [])) >= 1, "items 비어 있음"
    for it in data["items"]:
        if not str(it.get("link", "")).startswith("http"):
            it["link"] = ("https://news.google.com/search?q="
                          + re.sub(r"\s+", "+", it.get("title_en") or it.get("title_ko", "")))

    data["slug"] = slug
    data["date"] = now.strftime("%Y-%m-%d")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"content_{slug}_{data['date']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[generate] 저장: {path} (items: {len(data['items'])})")
    return path


if __name__ == "__main__":
    targets = sys.argv[1:] or [s for s in NEWSLETTERS if due_today(s)]
    if not targets:
        print("[generate] 오늘 발행할 뉴스레터가 없습니다.")
    for slug in targets:
        generate(slug)
