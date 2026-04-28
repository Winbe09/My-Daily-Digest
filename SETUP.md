# KritiDigest — Setup Guide

Get your digest live in under 30 minutes.

## Prerequisites
- A GitHub account (free)
- A Google AI Studio account (free) — for the Gemini API key

---

## Step 1 — Get your Gemini API key
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API key → Create API key**
3. Copy the key — you'll need it in Step 3

---

## Step 2 — Create your GitHub repository
1. Go to github.com → New repository
2. Name it `kritidigest` (or anything you like)
3. Set it to **Public** (required for free GitHub Pages)
4. Upload all files from this folder, preserving the folder structure

---

## Step 3 — Add your API key as a GitHub Secret
1. In your repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `GEMINI_API_KEY`
4. Value: paste your key from Step 1
5. Click **Add secret**

---

## Step 4 — Enable GitHub Pages
1. In your repo → **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / folder: `/docs`
4. Click **Save**

Your digest will be live at: `https://[your-username].github.io/kritidigest/`

---

## Step 5 — Run your first digest manually
1. Go to your repo → **Actions → Daily Digest**
2. Click **Run workflow → Run workflow**
3. Wait ~3 minutes for it to complete
4. Visit your GitHub Pages URL — your first digest is live

---

## Step 6 — Add newsletters (optional)

**Substack newsletters:**
Edit `src/config.py` → `NEWSLETTER_SOURCES`:
```python
{"name": "Stratechery", "url": "https://stratechery.com/feed/"},
```

**Other newsletters via Kill the Newsletter:**
1. Go to [kill-the-newsletter.com](https://kill-the-newsletter.com)
2. Enter a name → Get a unique email address + RSS feed URL
3. Subscribe your newsletter to that email address
4. Add the RSS URL to `NEWSLETTER_SOURCES` in `config.py`

---

## Customisation

All settings live in `src/config.py`:

| Setting | What it controls |
|---|---|
| `PREFERENCE_PROFILE` | Your persona — update as interests change |
| `RSS_SOURCES` | Primary news sources |
| `NEWSLETTER_SOURCES` | Newsletter feeds |
| `MIN_SCORE` | Minimum relevance score to include (default: 5) |
| `MAX_ARTICLES_*` | Article cap per section |

After any change, commit to GitHub → the next run picks it up automatically.

---

## Digest schedule
The digest runs daily at **7:00 AM IST** (01:30 UTC). To change the time, edit the cron expression in `.github/workflows/digest.yml`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Workflow fails | Check Actions tab → click the failed run → read the error log |
| No articles | A source may be blocking scrapers — check `SCRAPE_SOURCES` selectors |
| All articles filtered | Lower `MIN_SCORE` temporarily to debug |
| Gemini rate limit | The script retries automatically; free tier supports personal use |
