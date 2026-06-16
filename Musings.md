# Musings — Project Briefing for Claude Code

## Overview

Create and manage a static HTML article site published via GitHub Pages.

**Live URL:** `https://pa-sankar.github.io/musings/`
**GitHub repo:** Create new public repo named `musings` under account `pa-sankar`
**Author pseudonym:** Paa Sankar
**Site title:** Musings of an Indian

---

## Site Structure

```
musings/
├── index.html                          ← Homepage
├── assets/
│   ├── style.css                       ← Shared stylesheet
│   └── script.js                       ← Minimal JS if needed
└── history-repeats/
    └── index.html                      ← First article
```

Each future article gets its own subfolder with an `index.html` — same pattern as pa-sankar's existing game repos (`village-of-your-choice`, `village-elder`).

---

## Google Analytics

**Measurement ID:** `G-PZHG2G2YWF`
**Stream name:** My Musings
**Stream URL:** `https://pa-sankar.github.io/musings/`

Include this in the `<head>` of every HTML page:

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-PZHG2G2YWF"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-PZHG2G2YWF');
</script>
```

---

## Homepage — `index.html`

### Content

**Title:** Musings of an Indian

**Tagline:** *(to be decided — leave a placeholder comment in HTML)*

**About Paa Sankar** — short paragraph covering these passions:
- Organic Farming
- Independent Socially Responsible Living
- Leveraging AI for meaningful outcomes
- Educating the next generation
- Studying history to find solutions to today's problems

**Articles section** — a simple list/grid of published articles, each linking to its subfolder URL. Start with one entry:
- *History Repeats in the Future — Or Will It?* → `./history-repeats/`

### Design direction
- Clean, readable, long-form writing aesthetic
- Works well on mobile and desktop
- No flashy animations — the writing is the focus
- Warm but not cluttered
- Typography-forward — the kind of page where you want to sit and read
- Footer: "© Paa Sankar" with current year via JS

---

## First Article — `history-repeats/index.html`

**Source content:** `history_repeats_in_the_future.md` (in this same folder — copy to local working directory)

**Article metadata:**
- Title: History Repeats in the Future — Or Will It?
- Subtitle: An historical village reimagined in the near future
- Author: Paa Sankar
- Date: June 2026

### Content structure to render:
- Nine numbered sections (I through IX) each with **Past.** and **Future.** subsections
- A closing section: *The Same Story, Told Twice*
- An italicised closing note
- A **note on Uttiramerur** as a styled footnote/aside at the bottom

### Design requirements:
- Same stylesheet as homepage (`../assets/style.css`)
- **Past.** sections visually distinct from **Future.** sections — suggest subtle background tint or left border colour difference. Past = muted/sepia tone. Future = slightly warmer or greener tone. Not heavy-handed — just enough to guide the eye
- Section headings (I, II, III...) clearly marked
- Breadcrumb or back link to homepage at top: `← Musings of an Indian`
- Reading time estimate at top (calculate from word count ~4000 words ≈ 16 min read)
- Mobile-friendly, comfortable line length (65-75 chars), generous line height

---

## Git Workflow

### Initial setup (one time)
```bash
# Create local folder
mkdir musings && cd musings
git init
git remote add origin https://github.com/pa-sankar/musings.git

# After creating files
git add .
git commit -m "Initial commit — homepage and first article"
git push -u origin main
```

### GitHub Pages setup (one time, in GitHub repo settings)
- Go to repo Settings → Pages
- Source: Deploy from branch
- Branch: `main` / `root`
- Save — site will be live at `https://pa-sankar.github.io/musings/`

### For each new article or edit
```bash
git add .
git commit -m "Brief description of what changed"
git push
```
GitHub Pages auto-deploys within ~60 seconds of each push.

### Suggested commit message conventions
- `Add article: [article title]` — new article
- `Edit: [section or article name] — [what changed]` — content edit
- `Style: [what changed]` — CSS/design changes
- `Fix: [what]` — bug or broken link fix

---

## Future Articles Pipeline

These topics are in discussion and may become future articles:

1. **The Circle Economy** — nano and micro economic circles, village surplus feeding cities not the reverse
2. **Uttiramerur — The Constitution We Forgot** — deeper dive into the inscription and its modern implications
3. **Universal Basic Survival vs Universal Basic Income** — the full policy argument
4. **Silver, Gold and the Patience of the Long View** — investment philosophy piece (possibly under a different section/tag)

---

## Notes for Claude Code

- Keep dependencies zero or minimal — pure HTML/CSS/JS only, no frameworks, no npm
- No build step — what's in the repo is what's served
- Shared CSS in `assets/style.css` — all pages import from there
- Test locally by opening `index.html` in browser before pushing
- Validate all internal links before each commit
- Keep HTML semantic — use `<article>`, `<section>`, `<header>`, `<footer>`, `<nav>` appropriately for accessibility and future SEO
- Add `<meta>` description and Open Graph tags to each page for clean social sharing previews
- robots.txt not needed for now — GitHub Pages is publicly crawlable by default

---

## Open Questions (decide before or during build)

1. **Tagline** under "Musings of an Indian" on homepage — Paa Sankar to decide
2. **Comments / feedback** — no plan for now; may add later (options: GitHub Discussions, utterances, or a simple mailto link)
3. **Article tags/categories** — not needed yet; add when article count grows
4. **RSS feed** — consider adding once 3+ articles are published
