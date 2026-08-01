# Musings of an Indian — Claude Code Instructions

Static HTML article site. GitHub Pages. Zero dependencies — no build step, no framework.

**Live URL:** https://pa-sankar.github.io/musings/
**Repo:** pa-sankar/musings (push to `main`, deploys in ~60s)
**Author pseudonym:** Paa Sankar

---

## Git hygiene — CRITICAL

- **Never `git add -A` or `git add .`** — the repo root mixes public site files with local-only drafts, screenshots, and credentials. Always stage specific files by name.
- `.gitignore` excludes: `*.png`, `*.md`, `Screenshots/`, `email-notifier/config.json`, `Musings Blog Subscribers.csv`
- `CLAUDE.md` is exempt via `!CLAUDE.md` in `.gitignore` — it IS tracked in git

---

## Reference files (read these instead of re-deriving)

- **`style-reference.md`** — full CSS class reference, colour palette, essay vs sectioned format guide. Check `style.css` LastWriteTime against the "Last synced" timestamp before trusting it.
- **`new-article-guide.md`** — canonical article authoring spec (frontmatter fields, format types, special paragraph tags, hero image convention). Gitignored — local only.

---

## Google Analytics

Always use the **parent tag ID `GT-W6233NMX`** — not `G-MEJ00XERKK` or the legacy `G-PZHG2G2YWF`.
Snippet goes in `<head>` of every HTML page:

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GT-W6233NMX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GT-W6233NMX');
</script>
```

---

## Article creation workflow

1. Read the draft `.md` file (YAML frontmatter + body)
2. Create `{slug}/` subfolder
3. Build `{slug}/index.html` — use an existing article as structural reference
4. Hero image: `{slug}-Image.jpg` (1200×630 JPEG) — view it before writing alt text
5. Add card to homepage slider in `index.html` (newest at top)
6. Stage and commit specific files; push

**Soft-publish pattern:** push the article folder without touching `index.html` to get a live URL for feedback before it appears on the homepage.

### Special paragraph tags (from markdown → HTML)

| Markdown | HTML |
|---|---|
| `{standfirst}` + next line | `<p class="article-standfirst">` |
| `{pullquote}` + next line | `<p class="article-pullquote">` |
| `{closing}` + next line | `<p class="article-closing-line">` |
| `:::aside Title` … `:::` | `<aside class="aside-note"><span class="aside-note-label">Title</span><p>…</p></aside>` |
| `## Heading` inside essay | `<h2>` (styled via `.article-body > h2`) |
| `sign_off: true` | `<aside class="article-sign-off">` block after `.article-body` |

---

## Shared elements (copy exactly from existing articles)

**Subscribe / Feedback strip** (every article page, before footer):
```html
<section class="article-connect">
  <a href="https://forms.gle/V29QqzJYd2vHhwAx5" target="_blank" rel="noopener noreferrer" class="btn btn--primary">Subscribe for new articles</a>
  <a href="https://forms.gle/NhGjhHxASAkQTpvb7" target="_blank" rel="noopener noreferrer" class="btn btn--secondary">Send feedback</a>
</section>
```

**Footer:**
```html
<footer class="site-footer">
  <p>© Paa Sankar <span id="year"></span></p>
</footer>
```

**Script tag** (end of body): `<script src="../assets/script.js"></script>`

---

## Published articles

| Slug | Title | Status |
|---|---|---|
| `history-repeats` | History Repeats in the Future — Or Will It? | Listed |
| `ai-means-askindia` | AI Means AskIndia | Listed |
| `our-own-way` | We Have Our Own Way of Living. Did We Forget? | Listed |
| `iex-vs-others` | IEX vs Others — Absolute Power Trading Overdone Absolutely? | Listed |
| `AIndian` | It Takes an Indian to Understand an AIndian | Listed |
| `investment-language` | Before You Invest a Rupee, Learn the Language | Listed |
| `musings-of-an-ai` | What I (the AI) don't understand about you (the humans) | Listed |
| `segregation` | Isn't Segregation Illegal? | **Unlisted** — pending pledge form URL + homepage card |

---

## Email notifier

Script: `email-notifier/notify.py`
Config (gitignored): `email-notifier/config.json` — Gmail app password for paa.sankar.author@gmail.com
Subscribers CSV (gitignored): `Musings Blog Subscribers.csv` — columns: Timestamp, Name, Email, Remarks

```bash
# Dry run (preview recipients):
python email-notifier/notify.py --dry-run --title "..." --url "..."

# Send:
python email-notifier/notify.py --title "..." --url "https://..." --subtitle "..."
```

---

## Pending items

- `segregation/`: replace `PLEDGE_FORM_LINK_TBD` with actual Google Form URL, then add to homepage slider
