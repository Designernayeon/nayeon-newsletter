# -*- coding: utf-8 -*-
"""Schedule today's English newsletter for 07:00 KST through Beehiiv Enterprise.

Note: Beehiiv Create Post / Send API access requires an eligible Enterprise plan.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
KST = ZoneInfo("Asia/Seoul")


def scheduled_at(now: dt.datetime) -> dt.datetime:
    send = now.replace(hour=7, minute=0, second=0, microsecond=0)
    if send <= now:
        send += dt.timedelta(days=1)
    return send


def main() -> None:
    api_key = os.environ.get("BEEHIIV_API_KEY", "").strip()
    publication_id = os.environ.get("BEEHIIV_PUBLICATION_ID", "").strip()
    if not api_key or not publication_id:
        raise SystemExit("BEEHIIV_API_KEY and BEEHIIV_PUBLICATION_ID are required.")

    today = dt.datetime.now(KST).strftime("%Y-%m-%d")
    content_path = OUT / f"content_ai-briefing_{today}.json"
    email_path = OUT / f"email_ai-briefing_{today}.html"
    if not content_path.exists() or not email_path.exists():
        raise SystemExit("Today's AI briefing files were not found.")

    content = json.loads(content_path.read_text(encoding="utf-8"))
    payload = {
        "title": content["title"],
        "subtitle": content.get("intro", ""),
        "body_content": email_path.read_text(encoding="utf-8"),
        "status": "confirmed",
        "scheduled_at": scheduled_at(dt.datetime.now(KST)).isoformat(),
        "recipients": {"email": {"tier_ids": ["free", "premium"]}},
        "email_settings": {
            "email_subject_line": content["title"],
            "email_preview_text": content.get("intro", "")[:180],
        },
        "web_settings": {"hide_from_feed": False},
    }
    newsletter_list_id = os.environ.get("BEEHIIV_NEWSLETTER_LIST_ID", "").strip()
    if newsletter_list_id:
        payload["newsletter_list_id"] = newsletter_list_id

    url = f"https://api.beehiiv.com/v2/publications/{publication_id}/posts"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        if error.code == 403:
            print("Beehiiv returned 403. Create Post / Send API access may require an Enterprise plan.", file=sys.stderr)
        print(body, file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
