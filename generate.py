# -*- coding: utf-8 -*-
"""Generate today's English AI newsletter JSON with Claude web search."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import anthropic

from config import DEFAULT_MODEL, EDITORIAL_RULES, NEWSLETTERS, SITE_NAME

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
KST = ZoneInfo("Asia/Seoul")


def now_kst() -> dt.datetime:
    return dt.datetime.now(KST)


def fill_prompt(prompt: str, now: dt.datetime) -> str:
    return (
        prompt.replace("{date}", now.strftime("%Y-%m-%d"))
        .replace("{date_long}", now.strftime("%B %d, %Y"))
    )


def extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I | re.M)
    start = text.find("{")
    if start < 0:
        raise ValueError("Could not find the start of a JSON object in the model response.")
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text[start:], start=start):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : index + 1])
    raise ValueError("The JSON object in the model response was incomplete.")


def validate(data: dict, minimum_items: int) -> None:
    if not isinstance(data.get("title"), str) or not data["title"].strip():
        raise ValueError("The issue title is missing.")
    if not isinstance(data.get("intro"), str) or not data["intro"].strip():
        raise ValueError("The issue introduction is missing.")
    items = data.get("items")
    if not isinstance(items, list) or len(items) < minimum_items:
        raise ValueError(f"At least {minimum_items} newsletter items are required.")
    for index, item in enumerate(items, start=1):
        link = str(item.get("link", ""))
        if not link.startswith(("https://", "http://")):
            raise ValueError(f"Item {index} has an invalid source URL: {link}")
        for key in ("category", "headline", "summary"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"Item {index} is missing a valid '{key}' value.")


def generate(slug: str = "ai-briefing", when: dt.datetime | None = None) -> Path:
    when = when or now_kst()
    definition = NEWSLETTERS[slug]
    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY is not configured.")
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=model,
        max_tokens=10000,
        system=EDITORIAL_RULES.format(site_name=SITE_NAME, date=when.strftime("%Y-%m-%d")),
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 12}],
        messages=[{"role": "user", "content": fill_prompt(definition["prompt"], when)}],
    )
    text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
    data = extract_json(text)
    validate(data, definition["items_min"])
    data["slug"] = slug
    data["date"] = when.strftime("%Y-%m-%d")

    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / f"content_{slug}_{data['date']}.json"
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[generate] {output} ({len(data['items'])} items, model={model})")
    return output


if __name__ == "__main__":
    targets = sys.argv[1:] or ["ai-briefing"]
    for target in targets:
        if target not in NEWSLETTERS:
            raise SystemExit(f"Unsupported newsletter: {target}")
        generate(target)
