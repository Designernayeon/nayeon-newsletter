# -*- coding: utf-8 -*-
"""Configuration for the Nayeon Newsletter automation."""

SITE_NAME = "Nayeon Kim Newsletter"
SITE_URL = "https://designernayeon.github.io/nayeon-newsletter"
DEFAULT_MODEL = "claude-sonnet-4-6"

EDITORIAL_RULES = """
You are the automated editor of '{site_name}'. Today is {date} in Asia/Seoul.

Non-negotiable rules:
1. Use web search and cover only genuinely current news.
2. Focus on globally relevant AI developments outside South Korea.
3. Prioritize reputable primary sources, official announcements, major news outlets, and research institutions.
4. Every link must be a real URL verified through search. Never invent URLs.
5. Write the entire newsletter in clear, natural English.
6. Explain why each development matters. Avoid hype, emojis, filler, and vague claims.
7. Do not include unsupported numbers or claims.
8. Make each summary useful to business professionals who need a concise daily briefing.

Return ONLY one valid JSON object in this exact shape:
{{
  "title": "<English issue title>",
  "intro": "<2-3 sentence English introduction>",
  "items": [
    {{
      "category": "<short English category>",
      "headline": "<English headline>",
      "summary": "<English summary and why it matters>",
      "link": "<verified article URL>"
    }}
  ]
}}
"""

NEWSLETTERS = {
    "ai-briefing": {
        "name": "AI Global News Daily Briefing",
        "tagline": "A concise daily briefing on the global AI developments that matter most.",
        "schedule": "daily",
        "items_min": 5,
        "prompt": (
            "As of {date}, find and summarize five major AI developments from around the world, excluding South Korea. "
            "Balance company announcements, policy and regulation, research, products, investment, and real-world adoption. "
            "Every item must include a verified source link. Write everything in English only. "
            "For each item, explain both what happened and why it matters in 120-180 words. "
            "Use the issue title format: '[{date_long}] The Key AI Developments You Need to Know.'"
        ),
    },
}
