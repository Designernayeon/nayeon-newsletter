# Nayeon Newsletter — English Automation Patch

## Automated workflow

Every day at 06:15 KST, GitHub Actions runs Claude web search, generates an English AI briefing, builds the web issue, archive, email HTML, and RSS feed, and deploys the updated GitHub Pages site.

RSS feed:

`https://designernayeon.github.io/nayeon-newsletter/feeds/ai-briefing.xml`

## Required GitHub Secret

Open `Settings → Secrets and variables → Actions → New repository secret` and add:

- `ANTHROPIC_API_KEY`: your Anthropic API key

Optional Beehiiv Enterprise secrets:

- `BEEHIIV_AUTO_SEND`: `true`
- `BEEHIIV_API_KEY`
- `BEEHIIV_PUBLICATION_ID`
- `BEEHIIV_NEWSLETTER_LIST_ID` (only when sending to a specific list)

## First test

Open `Actions → Daily English AI Newsletter Generate + Deploy → Run workflow → Run workflow`.

After a successful run, confirm these files exist:

- `out/content_ai-briefing_YYYY-MM-DD.json`
- `out/email_ai-briefing_YYYY-MM-DD.html`
- `newsletters/ai-briefing/YYYY-MM-DD.html`
- `feeds/ai-briefing.xml`

## Beehiiv plan limitation

External RSS ingestion may require an eligible Beehiiv plan. Fully automated post creation and scheduled sending through the Beehiiv API may require Enterprise access.

Without Enterprise API access, the workflow still automates English content generation, website publishing, email HTML creation, and RSS generation. The final Beehiiv send must be completed manually.
