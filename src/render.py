# =============================================================================
# KritiDigest — HTML Renderer
# Generates the styled digest HTML and the archive index page.
# =============================================================================

from datetime import date
import html as html_module


# =============================================================================
# CSS (embedded — no external dependencies)
# =============================================================================

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Georgia', serif; background: #F4F6FA; color: #1A1A2E; }

header {
  background: linear-gradient(135deg, #0F3D91 0%, #1A1A2E 100%);
  color: white; padding: 28px 32px 22px;
}
.header-top { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; }
.digest-title { font-size: 28px; font-weight: 700; letter-spacing: -0.5px; font-family: Arial, sans-serif; }
.digest-subtitle { font-size: 13px; color: #A8C4F0; margin-top: 3px; font-family: Arial, sans-serif; }
.header-meta { text-align: right; font-family: Arial, sans-serif; }
.header-date { font-size: 13px; color: #A8C4F0; }
.header-count { font-size: 12px; color: #7AAAE8; margin-top: 2px; }

.glance { background: rgba(255,255,255,0.1); border-left: 3px solid #5BA3FF; margin-top: 18px; padding: 12px 16px; border-radius: 4px; }
.glance-label { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; color: #5BA3FF; text-transform: uppercase; font-family: Arial, sans-serif; margin-bottom: 8px; }
.glance-list { list-style: none; display: flex; flex-direction: column; gap: 6px; }
.glance-list li { font-size: 13px; line-height: 1.5; color: #D8E8FF; font-family: Arial, sans-serif; padding-left: 14px; position: relative; }
.glance-list li::before { content: '–'; position: absolute; left: 0; color: #5BA3FF; font-weight: 700; }

main { max-width: 960px; margin: 0 auto; padding: 28px 16px 60px; }

.big-section { margin: 36px 0 20px; padding: 14px 20px; border-radius: 8px; display: flex; align-items: baseline; gap: 10px; }
.big-section.news    { background: #E8EDF8; border-left: 4px solid #0F3D91; }
.big-section.culture { background: #FDF3E8; border-left: 4px solid #C06000; }
.big-section.thought { background: #EAF4EE; border-left: 4px solid #1A7A40; }
.big-section-num   { font-size: 11px; font-weight: 700; font-family: Arial, sans-serif; opacity: 0.5; }
.big-section-title { font-size: 15px; font-weight: 700; font-family: Arial, sans-serif; }
.big-section.news    .big-section-title { color: #0F3D91; }
.big-section.culture .big-section-title { color: #8B4500; }
.big-section.thought .big-section-title { color: #1A7A40; }
.big-section-desc  { font-size: 12px; font-family: Arial, sans-serif; color: #666; margin-left: auto; font-style: italic; }
@media (max-width: 600px) { .big-section-desc { display: none; } }

.section-header { display: flex; align-items: center; gap: 10px; margin: 24px 0 12px; }
.section-icon  { font-size: 15px; }
.section-title { font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #666; font-family: Arial, sans-serif; }
.section-line  { flex: 1; height: 1px; background: #D8DFF0; }

.card-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 700px) { .card-grid { grid-template-columns: 1fr; } }

.card { background: white; border-radius: 8px; padding: 16px 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.07); border: 1px solid #E4EAF6; display: flex; flex-direction: column; gap: 8px; transition: box-shadow 0.15s; }
.card:hover { box-shadow: 0 4px 14px rgba(15,61,145,0.1); }
.card.culture-card  { border-color: #F0DEC8; }
.card.culture-card:hover { box-shadow: 0 4px 14px rgba(192,96,0,0.1); }
.card.thought-card  { border-color: #C8E8D0; background: #FAFFFE; }
.card.thought-card:hover { box-shadow: 0 4px 14px rgba(26,122,64,0.1); }

.card-top    { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.card-badges { display: flex; gap: 5px; flex-wrap: wrap; flex-shrink: 0; }

.badge { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 10px; font-family: Arial, sans-serif; letter-spacing: 0.3px; white-space: nowrap; }
.badge-source   { background: #E8EDF8; color: #0F3D91; }
.badge-culture  { background: #FDEBD0; color: #8B4500; }
.badge-thought  { background: #D8F0E0; color: #1A7A40; }
.badge-trending { background: #FFF0E0; color: #D4700A; }
.badge-score-high { background: #E6F7EE; color: #1A7A40; }
.badge-score-mid  { background: #FFF8E1; color: #9A6B00; }

.card-headline { font-size: 14.5px; font-weight: 700; line-height: 1.4; font-family: Arial, sans-serif; color: #1A1A2E; text-decoration: none; display: block; }
.card-headline:hover { color: #0F3D91; text-decoration: underline; }
.thought-card .card-headline:hover { color: #1A7A40; }
.culture-card .card-headline:hover { color: #8B4500; }

.card-summary { font-size: 12.5px; line-height: 1.6; color: #444466; font-family: Arial, sans-serif; }

.card-footer { display: flex; align-items: center; margin-top: 4px; padding-top: 8px; border-top: 1px solid #F0F4FF; }
.thought-card .card-footer { border-top-color: #D8F0E0; }
.culture-card .card-footer { border-top-color: #F5E8D8; }
.card-also { font-size: 10.5px; color: #8899BB; font-family: Arial, sans-serif; font-style: italic; }

.card.featured { grid-column: 1 / -1; flex-direction: row; gap: 20px; background: linear-gradient(135deg, #F0F5FF 0%, #FAFBFF 100%); border: 1px solid #C0CFEE; }
.featured-body { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.featured-label { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; color: #0F3D91; text-transform: uppercase; font-family: Arial, sans-serif; }
.card.featured .card-headline { font-size: 17px; }
.card.featured .card-summary  { font-size: 13px; }

.card.thought-featured { grid-column: 1 / -1; flex-direction: row; gap: 20px; background: linear-gradient(135deg, #EAF7EE 0%, #F8FFFA 100%); border: 1px solid #A8DABC; }
.thought-featured .featured-label { color: #1A7A40; }
.thought-featured .card-headline  { font-size: 17px; }
.thought-featured .card-headline:hover { color: #1A7A40; }
.thought-featured .card-footer { border-top-color: #C8E8D0; }

@media (max-width: 700px) { .card.featured, .card.thought-featured { flex-direction: column; } }

.big-divider { border: none; border-top: 2px dashed #D0D8EE; margin: 44px 0 0; }

.archive-bar { text-align: center; margin-top: 48px; padding-top: 24px; border-top: 1px solid #D8E0F0; font-family: Arial, sans-serif; }
.archive-bar a { font-size: 12px; color: #0F3D91; text-decoration: none; }
.archive-bar a:hover { text-decoration: underline; }
.archive-bar span { color: #AAB8D8; margin: 0 8px; }
"""


# =============================================================================
# HELPERS
# =============================================================================

def _e(text):
    """HTML-escape a string."""
    return html_module.escape(str(text or ""))


def _score_badge(score):
    css = "badge-score-high" if score >= 7 else "badge-score-mid"
    return f'<span class="badge {css}">{score}</span>'


def _source_badge(source, section):
    css = {"culture": "badge-culture", "thought": "badge-thought"}.get(section, "badge-source")
    return f'<span class="badge {css}">{_e(source)}</span>'


def _render_card(article, featured=False, featured_label=None, section="news"):
    card_class = {"culture": "culture-card", "thought": "thought-card"}.get(section, "")
    featured_class = ""
    if featured:
        featured_class = "thought-featured" if section == "thought" else "featured"

    badges = _source_badge(article["source"], section)
    if article.get("is_trending"):
        badges += ' <span class="badge badge-trending">🔥 Trending</span>'
    badges += " " + _score_badge(article["score"])

    also = ""
    if article.get("also_covered_by"):
        also = f'<span class="card-also">Also covered by: {_e(", ".join(article["also_covered_by"]))}</span>'

    headline_hover = {"culture": "#8B4500", "thought": "#1A7A40"}.get(section, "#0F3D91")

    if featured:
        label_color = "#1A7A40" if section == "thought" else "#0F3D91"
        label_html = f'<div class="featured-label" style="color:{label_color};">{_e(featured_label or "Top Story")}</div>' if featured_label else '<div class="featured-label">Top Story</div>'
        return f"""
    <div class="card {featured_class} {card_class}">
      <div class="featured-body">
        {label_html}
        <div class="card-top">
          <a href="{_e(article['url'])}" class="card-headline" target="_blank" rel="noopener" style="">{_e(article['title'])}</a>
          <div class="card-badges">{badges}</div>
        </div>
        <div class="card-summary">{_e(article.get('summary') or article.get('snippet', ''))}</div>
        <div class="card-footer">{also}</div>
      </div>
    </div>"""
    else:
        return f"""
    <div class="card {card_class}">
      <div class="card-top">
        <a href="{_e(article['url'])}" class="card-headline" target="_blank" rel="noopener">{_e(article['title'])}</a>
        <div class="card-badges">{badges}</div>
      </div>
      <div class="card-summary">{_e(article.get('summary') or article.get('snippet', ''))}</div>
      <div class="card-footer">{also}</div>
    </div>"""


def _render_section_header(icon, title):
    return f"""
  <div class="section-header">
    <span class="section-icon">{icon}</span>
    <span class="section-title">{title}</span>
    <div class="section-line"></div>
  </div>"""


def _render_card_group(articles, icon, title, section):
    if not articles:
        return ""
    cards_html = ""
    for i, a in enumerate(articles):
        featured = (i == 0 and section == "thought")
        label = a["source"] if featured and section == "thought" else "Top Story"
        cards_html += _render_card(a, featured=(i == 0 and section in ("news", "thought")),
                                   featured_label=label, section=section)
    return _render_section_header(icon, title) + f'\n  <div class="card-grid">{cards_html}\n  </div>'


# Subsections for news
NEWS_SUBSECTIONS = [
    ("🌍", "Geopolitics",       lambda a: any(k in (a.get("reason","") + a.get("summary","")).lower()
                                              for k in ["geopolit","war","sanction","treaty","diplomat","election","government","china","russia","india","pakistan","iran","us ","eu ","nato"])),
    ("📈", "Business &amp; Markets", lambda a: any(k in (a.get("reason","") + a.get("summary","")).lower()
                                                   for k in ["market","gdp","economy","invest","rate","rbi","fed","stock","fund","revenue","growth","pe ","vc "])),
    ("⚡", "Tech Trends",       lambda a: True),   # catch-all
]


def _bucket_news(articles):
    """Split news articles into geopolitics / business / tech buckets."""
    buckets = {"geo": [], "biz": [], "tech": []}
    used = set()
    for a in articles:
        text = (a.get("reason","") + " " + a.get("summary","") + " " + a.get("title","")).lower()
        if id(a) in used:
            continue
        if any(k in text for k in ["geopolit","war","sanction","treaty","diplomat","election","government","pakistan","iran","russia","ukraine","nato","bilateral"]):
            buckets["geo"].append(a); used.add(id(a))
        elif any(k in text for k in ["market","gdp","economy","interest rate","inflation","invest","rbi","fed","stock","fund","revenue","pe ","vc ","valuation"]):
            buckets["biz"].append(a); used.add(id(a))
        else:
            buckets["tech"].append(a); used.add(id(a))
    return buckets


# =============================================================================
# MAIN RENDER
# =============================================================================

def render_digest(sections, glance_bullets, digest_date, prev_date=None, next_date=None):
    """
    Render the full digest HTML page.

    Args:
        sections      : dict with keys 'news', 'culture', 'thought' — lists of article dicts
        glance_bullets: list of strings for Today at a Glance
        digest_date   : date object for this digest
        prev_date     : date object for previous digest (or None)
        next_date     : date object for next digest (or None)

    Returns:
        HTML string
    """
    date_str  = digest_date.strftime("%A, %B %-d, %Y")
    total     = len(sections["news"]) + len(sections["culture"]) + len(sections["thought"])
    n_sources = len({a["source"] for s in sections.values() for a in s})
    n_trending = sum(1 for s in sections.values() for a in s if a.get("is_trending"))

    # Glance bullets
    bullets_html = "\n".join(f"      <li>{_e(b)}</li>" for b in glance_bullets)

    # Section 1 — News
    news_buckets = _bucket_news(sections["news"])
    news_html = ""
    if news_buckets["geo"]:
        news_html += _render_card_group(news_buckets["geo"], "🌍", "Geopolitics", "news")
    if news_buckets["biz"]:
        news_html += _render_card_group(news_buckets["biz"], "📈", "Business &amp; Markets", "news")
    if news_buckets["tech"]:
        news_html += _render_card_group(news_buckets["tech"], "⚡", "Tech Trends", "news")

    # Section 2 — Culture
    culture_html = ""
    if sections["culture"]:
        culture_html = f"""
  <hr class="big-divider">
  <div class="big-section culture">
    <span class="big-section-num">02</span>
    <span class="big-section-title">Art, Culture &amp; Lifestyle</span>
    <span class="big-section-desc">Entertainment · Arts · Living</span>
  </div>
  {_render_section_header("🎨", "Entertainment &amp; Arts")}
  <div class="card-grid">{"".join(_render_card(a, section="culture") for a in sections["culture"])}</div>"""

    # Section 3 — Thought Leadership
    thought_html = ""
    if sections["thought"]:
        thought_html = f"""
  <hr class="big-divider">
  <div class="big-section thought">
    <span class="big-section-num">03</span>
    <span class="big-section-title">Thought Leadership &amp; Education</span>
    <span class="big-section-desc">HBR · McKinsey · Longform · Strategy</span>
  </div>
  {_render_section_header("🧠", "Strategy &amp; Leadership")}
  <div class="card-grid">{"".join(_render_card(a, featured=(i == 0), featured_label=a["source"], section="thought") for i, a in enumerate(sections["thought"]))}</div>"""

    # Archive nav
    prev_link = f'<a href="{prev_date}.html">← {prev_date}</a>' if prev_date else '<span style="color:#ccc;">← Previous</span>'
    next_link = f'<a href="{next_date}.html">{next_date} →</a>' if next_date else '<span style="color:#ccc;">Next →</span>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KritiDigest — {_e(date_str)}</title>
<style>{CSS}</style>
</head>
<body>

<header>
  <div class="header-top">
    <div>
      <div class="digest-title">KritiDigest</div>
      <div class="digest-subtitle">Your personalised AI news briefing</div>
    </div>
    <div class="header-meta">
      <div class="header-date">{_e(date_str)}</div>
      <div class="header-count">{total} articles · {n_sources} sources · {n_trending} trending</div>
    </div>
  </div>
  <div class="glance">
    <div class="glance-label">Today at a Glance</div>
    <ul class="glance-list">
{bullets_html}
    </ul>
  </div>
</header>

<main>

  <div class="big-section news">
    <span class="big-section-num">01</span>
    <span class="big-section-title">What's Happening</span>
    <span class="big-section-desc">News · Geopolitics · Business · Tech</span>
  </div>
{news_html}
{culture_html}
{thought_html}

  <div class="archive-bar">
    {prev_link}
    <span>|</span>
    <a href="index.html">All digests</a>
    <span>|</span>
    {next_link}
  </div>

</main>
</body>
</html>"""


# =============================================================================
# ARCHIVE INDEX
# =============================================================================

def render_index(dates):
    """
    Render the archive index listing all past digests.
    dates: list of date objects, most recent first.
    """
    items = "\n".join(
        f'    <li><a href="{d}.html">{d.strftime("%A, %B %-d, %Y")}</a></li>'
        for d in dates
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KritiDigest — Archive</title>
<style>
  body {{ font-family: Arial, sans-serif; background: #F4F6FA; color: #1A1A2E; max-width: 600px; margin: 60px auto; padding: 0 20px; }}
  h1 {{ font-size: 24px; margin-bottom: 6px; }}
  p  {{ font-size: 13px; color: #666; margin-bottom: 28px; }}
  ul {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
  li a {{ font-size: 15px; color: #0F3D91; text-decoration: none; }}
  li a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
  <h1>KritiDigest</h1>
  <p>Your personalised AI news briefing — all editions</p>
  <ul>
{items}
  </ul>
</body>
</html>"""
