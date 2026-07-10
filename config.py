# -*- coding: utf-8 -*-
"""뉴스레터 3종의 정의 · 발행 규칙 · 생성 프롬프트."""

SITE_NAME = "Nayeon Kim Newsletter"
SITE_URL = "https://designernayeon.github.io/nayeon-newsletter"  # 배포 후 실제 주소로 교체

# 모든 뉴스레터가 공통으로 지켜야 할 4대 원칙 (시스템 프롬프트에 주입됨)
EDITORIAL_RULES = """
You are the automated editor of the '{site_name}'. Non-negotiable rules:
1. Only cover news that is genuinely current as of TODAY ({date}). Use web search to verify.
2. Pick topics with broad general interest (global economy, finance, AI, major world affairs).
3. Every link you output MUST be a real, working URL to an article whose content matches your summary.
   Never invent URLs. If you cannot verify a URL via search, use a Google News search query URL instead:
   https://news.google.com/search?q=<url-encoded-query>
4. Write clean prose. No emojis. No markdown headers inside body text.

OUTPUT FORMAT — return ONLY a single JSON object, no prose before or after, matching:
{{
  "title": "<issue title string>",
  "intro": "<1-3 sentence opening, may be empty string>",
  "items": [
    {{
      "category": "<short category label, e.g. 'Economy & Trade'>",
      "title_ko": "<Korean headline>",
      "body_ko": "<Korean body paragraph(s)>",
      "title_en": "<English headline>",
      "body_en": "<English body paragraph(s)>",
      "link": "<verified article URL>"
    }}
  ]
}}
For English-only newsletters, put the English text in title_en/body_en and leave title_ko/body_ko as "".
"""

NEWSLETTERS = {
    # ──────────────────────────────────────────────────────────────
    "economics": {
        "name": "From Economics to AI",
        "tagline": "We get to the core of global economics and finance.",
        "schedule": "daily",          # 매일 발행
        "accent": "#1C2B1C",
        "items_min": 4,
        "prompt": (
            "Generate a daily AI global news briefing for today ({date}), covering economy, "
            "finance, AI, current affairs, and global trends. Include Korean and English "
            "editions for every item (title + body + link). Make sure to use real, verifiable "
            "news URLs for the specific topics where possible, or high-quality Google News "
            "search-query URLs if specific article URLs cannot be reliably verified. "
            "The issue title must start with: "
            "\"AI Global News Daily Briefing | The AI Director's Lab — {date}\". "
            "The intro should be: \"Welcome to today's briefing. Here are the core global "
            "updates covering the economy, finance, artificial intelligence, current affairs, "
            "and global trends, meticulously curated from major reputable outlets and research "
            "institutions.\" Produce 4-6 items across different categories "
            "(세계 경제 및 무역 / Economy & Trade, 금융 시장 / Financial Markets, "
            "AI 산업 / AI Industry, 국제 정세 / Global Affairs 등)."
        ),
    },
    # ──────────────────────────────────────────────────────────────
    "ai-briefing": {
        "name": "AI Global News Daily Briefing",
        "tagline": "Welcome to 'Today's AI NEWS,' your daily source for the latest trends in artificial intelligence.",
        "schedule": "daily",
        "accent": "#D9F2A0",
        "items_min": 5,
        "prompt": (
            "오늘({date})의 주요 글로벌 AI 뉴스 TOP 5를 웹 검색으로 찾아 요약해 주세요. "
            "'주요 내용', '시사점' 같은 소제목 단어는 제거하고 줄글로 작성하며 이모티콘은 사용하지 마세요. "
            "각 항목에 실제 관련 기사 링크를 삽입해 주세요. "
            "내용은 전부 한국을 제외한 다른 세계 각국의 AI 기술 동향을 다루세요. "
            "전체 한글 본문 합계 최소 1000자 이상, 각 항목마다 한글과 영문을 모두 제공하세요. "
            "이슈 제목(title)은 반드시 다음 형식으로: "
            "\"[{date_kr}] 인공지능 분야의 주요 소식을 정리해 드립니다.\""
        ),
    },
    # ──────────────────────────────────────────────────────────────
    "success-stories": {
        "name": "Weekly AI Success Stories",
        "tagline": "Delivering 5 global AI success stories every Wednesday morning. Strategic insights and actionable inspiration.",
        "schedule": "wednesday",      # 매주 수요일만 발행
        "accent": "#F7BEDF",
        "items_min": 5,
        "prompt": (
            "Search the latest global news and find 5 AI Success Stories. If this week's news "
            "is thin, prioritize cases that inspire CEOs and founders. All content in English "
            "only (leave title_ko/body_ko empty). For each case, structure body_en as: "
            "the case study, a 'Success Equation' ([X × Y = Outcome] style), and a one-line "
            "'Formula for Leaders'. End each item with its related article link in the link "
            "field. The issue title must be exactly \"Weekly AI Success Stories _ {yy}Y {m}M {w}W\" "
            "where {yy}=2-digit year, {m}=month number, {w}=week-of-month of today ({date}). "
            "The intro should set the week's strategic theme in 2-3 sentences."
        ),
    },
}
