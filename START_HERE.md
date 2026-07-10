# Nayeon Kim Newsletter — 공개 배포 시작하기

## 1. GitHub에 프로젝트 업로드

저장소 주소:
`https://github.com/Designernayeon/nayeon-newsletter`

터미널에서 이 프로젝트 폴더로 이동한 뒤:

```bash
git init
git config user.name "Designernayeon"
git config user.email "designaistudio2@gmail.com"
git add .
git commit -m "Initial newsletter site"
git branch -M main
git remote add origin https://github.com/Designernayeon/nayeon-newsletter.git
git push -u origin main
```

## 2. GitHub Pages 활성화

GitHub 저장소에서:

`Settings → Pages → Build and deployment → Source → GitHub Actions`

업로드 후 Actions의 `Deploy Newsletter Site`가 완료되면 다음 주소로 공개됩니다.

`https://designernayeon.github.io/nayeon-newsletter/`

## 3. Beehiiv 구독 폼 연결

Beehiiv에서:

`Subscribers → Subscribe forms → Create new form → Save changes → Get embed code`

발급된 embed script를 `site/index.html`의 임시 `<form class="sub-form">...</form>` 대신 넣습니다.

## 4. 자동 뉴스레터 생성

GitHub 저장소에서:

`Settings → Secrets and variables → Actions → New repository secret`

이름: `ANTHROPIC_API_KEY`

등록 후 Actions에서 `Daily Newsletter Publish (07:00 KST)`를 수동 실행해 테스트합니다.
