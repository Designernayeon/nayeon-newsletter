# Nayeon Kim Newsletter — 아카이브 사이트 + 자동 발행 파이프라인

**역할 분담**
- **이 사이트 (GitHub Pages)** — 공식 아카이브. 매일 오전 7시 전에 새 호가 자동 게시됩니다.
- **Beehiiv / 스티비** — 구독자 관리 + 이메일 발송 담당.

```
06:40 KST  GitHub Actions 기동
   ↓  ① generate.py   — Claude API(웹 검색)가 당일 최신 뉴스로 뉴스레터 콘텐츠 생성
   ↓  ② build_site.py — 웹 페이지 + 아카이브 렌더링, 기사 og:image 자동 삽입
   ↓  ③ git push      — 사이트에 새 호 게시  +  out/에 이메일용 HTML 저장
07:00 KST  Beehiiv/스티비에서 구독자에게 발송 (아래 3번 참고)
```

- **매일**: From Economics to AI · AI Global News Daily Briefing
- **수요일 추가**: Weekly AI Success Stories
- 4대 원칙(당일 최신성 / 대중적 주제 / 실제 링크 / 기사 이미지)은 `automation/config.py`의 프롬프트에 내장.

---

## 1. 사이트 개설 (약 20분)

1. github.com → 새 저장소 `nayeon-newsletter` 생성 (Public)
2. 이 폴더 전체 업로드:
   ```bash
   git init && git add . && git commit -m "init"
   git remote add origin https://github.com/<아이디>/nayeon-newsletter.git
   git push -u origin main
   ```
3. Settings → Pages → Build and deployment → Source에서 `GitHub Actions` 선택
   저장소의 `.github/workflows/deploy-pages.yml`이 `site/` 폴더를 자동 배포합니다.
4. 몇 분 후 `https://designernayeon.github.io/nayeon-newsletter/` 접속 확인
5. `automation/config.py`의 `SITE_URL`을 실제 주소로 수정

> 지금은 발행된 호가 없으므로 아카이브에 "아직 발행된 호가 없어요" 빈 상태가 표시됩니다. 정상입니다.
> 첫 발행이 되면 자동으로 카드가 채워집니다.

## 2. 자동 발행 켜기

- Settings → Secrets and variables → Actions → `ANTHROPIC_API_KEY` 등록 (console.anthropic.com에서 발급)
- Actions 탭 → "Daily Newsletter Publish" → **Run workflow**로 첫 테스트
- 성공하면 사이트에 오늘자 호가 올라가고, 이후 매일 06:40 KST 자동 실행

## 3. Beehiiv / 스티비 연결

### 구독 폼 (사이트 → 플랫폼)
`site/index.html`의 `<!-- ▼▼ 뉴스레터 플랫폼 연결 지점 ▼▼ -->` 주석 위치에:
- **Beehiiv**: 대시보드 → Grow → Subscribe Forms → **Embed** 코드를 기존 `<form>` 대신 붙여넣기
- **스티비**: 구독 페이지 주소를 발급받아
  `<a class="btn btn-yellow" href="https://page.stibee.com/subscribe/xxxx">Get the 7AM drop</a>` 로 교체

### 이메일 발송 (플랫폼 → 구독자)
매일 워크플로가 `out/email_<뉴스레터>_<날짜>.html`을 만들어 저장소에 커밋합니다.
- **수동(권장 시작점)**: 파일 내용을 복사해 Beehiiv/스티비 에디터의 HTML 블록에 붙여넣고 오전 7시 예약 발송
- **완전 자동(2단계)**: Beehiiv **API**(Enterprise/Scale 플랜) `POST /posts`로 초안 생성 + 예약까지 자동화 가능
  → 원하시면 워크플로에 발송 스텝을 추가해 드릴 수 있습니다. 스티비도 API로 이메일 발송을 지원합니다.

## 4. 로그인 · 구독자 이벤트 (로드맵)

Beehiiv는 구독자 관리·세그먼트·추천 프로그램을 자체 제공하므로 별도 로그인 시스템 없이도
구독자 이벤트(추첨, 리퍼럴 보상 등) 운영이 가능합니다. 사이트에 로그인이 꼭 필요해지면
그 시점에 Supabase(무료)를 붙이는 것을 권장합니다.

## 5. 자주 손대는 파일

| 파일 | 내용 |
|---|---|
| `automation/config.py` | 뉴스레터 3종 프롬프트 · 발행 요일 · 사이트 URL |
| `site/index.html`, `site/assets/style.css` | 랜딩 페이지 (핑크 에디토리얼 뉴스레터 디자인 시스템) |
| `.github/workflows/daily-newsletter.yml` | 발행 시각 (cron, UTC) |

로컬 테스트:
```bash
pip install -r automation/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python automation/generate.py ai-briefing
python automation/build_site.py
python3 -m http.server 8000 --directory site
open http://localhost:8000
```
