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
| `ageless-wisdom` | Ageless Wisdom | Listed |
| `ai-is-killing-the-curious-cat` | AI is killing the curious cat (series part 1 of 5) | Listed |
| `a-solution-from-the-past-rediscovered` | A solution from the past, rediscovered (series part 2 of 5) | Listed |
| `show-your-work-prove-you-meant-it` | Show your work, prove you meant it (series part 3 of 5) | Listed |
| `the-peer-whos-too-polite` | The peer who's too polite, and the liar who's worse (series part 4 of 5) | Listed |
| `segregation` | Isn't Segregation Illegal? | **Unlisted** — pending pledge form URL + homepage card |

---

## Email notifier

**Windows console encoding:** the default console codepage (cp1252) can't print non-ASCII characters (arrows, em dashes, smart quotes). Run every script below with `PYTHONIOENCODING=utf-8` set, e.g. `PYTHONIOENCODING=utf-8 python email-notifier/notify.py ...`. Without it, a crash mid-loop (e.g. after the first `sendmail()` succeeds but before its `print()`) can silently skip the remaining recipients — always verify send counts.

### Subscriber tracking (the actual source of truth)

Sankar downloads a fresh export from the Google Form over `Musings Blog Subscribers.csv` (gitignored) whenever someone new subscribes — it's a raw snapshot, always overwritten wholesale, so it has no memory of who's already been welcomed or asked to stop. That memory lives in a separate, tracked state file instead:

- **`email-notifier/subscriber_state.csv`** (gitignored — subscriber PII) — one row per subscriber: `Email, Name, SubscribedTimestamp, SignupContextTitle, SignupContextUrl, WelcomeSentDate, Status, Notes`. `Status` is `active` / `do-not-send` / `bounced`. **`notify.py` and `welcome.py` both read only from this file**, filtered to `Status == active` — never from the raw CSV directly.
- **`email-notifier/sync_subscribers.py`** — run this first, every time the raw CSV is re-downloaded. Diffs it against the state file by email and appends anyone new (`Status=active`, empty `WelcomeSentDate`). Prints the new names so you know who still needs a welcome email.
  ```bash
  PYTHONIOENCODING=utf-8 python email-notifier/sync_subscribers.py --dry-run   # just report
  PYTHONIOENCODING=utf-8 python email-notifier/sync_subscribers.py \
    --current-article-title "..." --current-article-url "https://..."          # tag context + write
  ```
- **`email-notifier/manage_subscriber.py`** — change a subscriber's status (e.g. they asked to stop, or an address bounced), or list everyone with their status/welcome date.
  ```bash
  PYTHONIOENCODING=utf-8 python email-notifier/manage_subscriber.py --list
  PYTHONIOENCODING=utf-8 python email-notifier/manage_subscriber.py --email x@y.com --status do-not-send --note "asked to unsubscribe 2026-09-24"
  ```

**Workflow whenever the CSV is re-downloaded:** run `sync_subscribers.py` → run `welcome.py` with no arguments (it auto-sends to everyone active and not yet welcomed) → for any unsubscribe/bounce, run `manage_subscriber.py`.

### notify.py — new-article blast to all active subscribers

Config (gitignored): `email-notifier/config.json` — Gmail app password for paa.sankar.author@gmail.com, plus `subscriber_state_csv` path.

The email includes a clickable hero image, auto-derived from `--url` via the `{slug}-Image.jpg` convention (same as `og:image`). Override with `--image <url>`, or drop it with `--no-image` if the article has no hero image yet.

```bash
PYTHONIOENCODING=utf-8 python email-notifier/notify.py --dry-run --title "..." --url "..."
PYTHONIOENCODING=utf-8 python email-notifier/notify.py --title "..." --url "https://..." --subtitle "..."
```

### welcome.py — auto-sends to everyone not yet welcomed

No arguments needed for the normal case: finds every tracked subscriber who's `active` with an empty `WelcomeSentDate` and sends each one individually, recording the date as it goes (persisted after every attempt, not just at the end — safe to interrupt). Links to the **homepage**, not the latest article — someone who just subscribed almost certainly already read whatever piece got them there; the welcome email's job is surfacing everything else.

```bash
PYTHONIOENCODING=utf-8 python email-notifier/welcome.py --dry-run   # preview who'd get one
PYTHONIOENCODING=utf-8 python email-notifier/welcome.py             # send to all unwelcomed
```

Pass `--name` or `--email` to target just one subscriber instead (e.g. a deliberate re-send) — this sends even if they already have a `WelcomeSentDate`.

```bash
PYTHONIOENCODING=utf-8 python email-notifier/welcome.py --name "Jagan" --dry-run
PYTHONIOENCODING=utf-8 python email-notifier/welcome.py --email jagan.xbox@gmail.com
```

---

## Pending items

- `segregation/`: replace `PLEDGE_FORM_LINK_TBD` with actual Google Form URL, then add to homepage slider
- AI curiosity series (`ai-curiosity-series/` hub): part 5 still work in progress (drafts for part 5 and an extra unplanned "6-same-well-different-problem" exist in `learning-series/` as of 2026-09-23). Swap its "Coming soon" badge in the hub for a real link once finalized.
