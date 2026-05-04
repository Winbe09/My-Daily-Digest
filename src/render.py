# =============================================================================
# KritiDigest — HTML Renderer
# Renders a simple linked list of articles grouped by source.
# =============================================================================

from datetime import date
import html as html_module


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #F4F6FA; color: #1A1A2E; }

header {
  background: linear-gradient(135deg, #0F3D91 0%, #1A1A2E 100%);
  color: white; padding: 28px 32px 22px;
}
.header-top { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; }
.digest-title { font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }
.digest-subtitle { font-size: 15px; color: #A8C4F0; margin-top: 3px; }
.header-meta { text-align: right; }
.header-date  { font-size: 15px; color: #A8C4F0; }
.header-count { font-size: 13px; color: #7AAAE8; margin-top: 2px; }

main { max-width: 860px; margin: 0 auto; padding: 32px 20px 60px; }

.source-block { margin-bottom: 32px; }
.source-name {
  font-size: 13px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
  color: #0F3D91; margin-bottom: 10px;
  padding-bottom: 6px; border-bottom: 2px solid #D0D8EE;
}
.article-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.article-item { display: flex; align-items: baseline; gap: 8px; }
.article-item::before { content: '→'; color: #A0AABF; font-size: 12px; flex-shrink: 0; }
.article-link {
  font-size: 16px; color: #1A1A2E; text-decoration: none; line-height: 1.4;
}
.article-link:hover { color: #0F3D91; text-decoration: underline; }
.article-also { font-size: 12px; color: #AABBCC; margin-left: 4px; font-style: italic; white-space: nowrap; }

.archive-bar {
  text-align: center; margin-top: 48px; padding-top: 24px;
  border-top: 1px solid #D8E0F0;
}
.archive-bar a { font-size: 14px; color: #0F3D91; text-decoration: none; }
.archive-bar a:hover { text-decoration: underline; }
.archive-bar span { color: #AAB8D8; margin: 0 8px; }
"""


def _e(text):
    return html_module.escape(str(text or ""))


def render_digest(grouped, digest_date, prev_date=None, next_date=None):
    """
    Render the digest as a linked list grouped by source.

    Args:
        grouped   : OrderedDict of source → list of article dicts
        digest_date: date object
        prev_date : date object or None
        next_date : date object or None
    Returns:
        HTML string
    """
    date_str = digest_date.strftime("%A, %B %-d, %Y")
    total    = sum(len(arts) for arts in grouped.values())

    # Build source blocks
    blocks = ""
    for source, articles in grouped.items():
        items = ""
        for a in articles:
            also = ""
            if a.get("also_covered_by"):
                also = f'<span class="article-also">· also: {_e(", ".join(a["also_covered_by"]))}</span>'
            items += f'<li class="article-item"><a href="{_e(a["url"])}" class="article-link" target="_blank" rel="noopener">{_e(a["title"])}</a>{also}</li>\n'
        blocks += f"""
  <div class="source-block">
    <div class="source-name">{_e(source)}</div>
    <ul class="article-list">{items}</ul>
  </div>"""

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
      <div class="digest-subtitle">Your daily news digest</div>
    </div>
    <div class="header-meta">
      <div class="header-date">{_e(date_str)}</div>
      <div class="header-count">{total} articles · {len(grouped)} sources</div>
    </div>
  </div>
</header>

<main>
{blocks}
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


def render_index(dates):
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
  <p>Your daily news digest — all editions</p>
  <ul>
{items}
  </ul>
</body>
</html>"""
