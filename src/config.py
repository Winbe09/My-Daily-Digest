# =============================================================================
# KritiDigest — Configuration
# Edit this file to add sources, update your preference profile, or
# adjust scoring thresholds. No other files need to change.
# =============================================================================

# -----------------------------------------------------------------------------
# PREFERENCE PROFILE
# Injected into every AI scoring prompt. Update this as your interests evolve.
# -----------------------------------------------------------------------------
PREFERENCE_PROFILE = """
I am a strategy professional (MBA + Engineer) leading AI GTM strategy for a devtools company.

Prioritise articles about:
- Global geopolitics and international relations
- Macroeconomics, markets, and investing trends
- AI and tech product trends (not funding news)
- Business strategy and leadership
- Devtools ecosystem and enterprise software
- Art, culture, and entertainment

Deprioritise (score low):
- Startup funding rounds and VC deal news
- Celebrity gossip and sports
- Clickbait or opinion pieces with no data
- Repetitive regulatory news without new developments
"""

# -----------------------------------------------------------------------------
# NEWS SOURCES — Primary (RSS)
# -----------------------------------------------------------------------------
RSS_SOURCES = [
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "priority": 1,
    },
    {
        "name": "The Guardian",
        "url": "https://www.theguardian.com/world/rss",
        "priority": 2,
    },
    {
        "name": "Economic Times",
        "url": "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
        "priority": 3,
    },
    {
        "name": "Times of India",
        "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "priority": 4,
    },
]

# -----------------------------------------------------------------------------
# NEWS SOURCES — Secondary (RSS, polled for content from past 7 days)
# Articles included only if AI relevance score >= SECONDARY_MIN_SCORE
# -----------------------------------------------------------------------------
SECONDARY_RSS_SOURCES = [
    {
        "name": "HBR",
        "url": "https://feeds.hbr.org/harvardbusiness",
        "priority": 5,
    },
]

# -----------------------------------------------------------------------------
# SOURCES REQUIRING SCRAPING
# BeautifulSoup used to extract article links from homepage
# -----------------------------------------------------------------------------
SCRAPE_SOURCES = [
    {
        "name": "Captable",
        "url": "https://captable.in",
        "article_selector": "h2 a, h3 a",   # CSS selector for article links
        "priority": 6,
    },
    {
        "name": "McKinsey",
        "url": "https://www.mckinsey.com/insights",
        "article_selector": "h2 a, h3 a, .article-title a",
        "priority": 7,
    },
]

# -----------------------------------------------------------------------------
# NEWSLETTER SOURCES
# Add Substack RSS or Kill the Newsletter feeds here.
# No code changes needed — just add entries to this list.
#
# Substack format:
#   {"name": "My Newsletter", "url": "https://example.substack.com/feed"}
#
# Kill the Newsletter format:
#   {"name": "My Newsletter", "url": "https://kill-the-newsletter.com/feeds/XXXXXX.xml"}
# -----------------------------------------------------------------------------
NEWSLETTER_SOURCES = [
    # Add your newsletter RSS feeds here, for example:
    # {"name": "Stratechery", "url": "https://stratechery.com/feed/"},
    # {"name": "The Diff", "url": "https://www.thediff.co/feed"},
]

# -----------------------------------------------------------------------------
# TRENDING SIGNAL SOURCES
# Used only for scoring enrichment — not as direct article sources
# -----------------------------------------------------------------------------
REDDIT_SUBREDDITS = [
    "technology",
    "worldnews",
    "investing",
    "artificial",
    "geopolitics",
    "IndiaInvestments",
]

# Hacker News: top N stories fetched
HN_STORY_LIMIT = 30

# -----------------------------------------------------------------------------
# SCORING & FILTERING THRESHOLDS
# -----------------------------------------------------------------------------
MIN_SCORE = 5               # Articles below this score are discarded
SECONDARY_MIN_SCORE = 7     # Min score for HBR / McKinsey / newsletter sources

MAX_ARTICLES_NEWS    = 20   # Max articles in Section 1 (What's Happening)
MAX_ARTICLES_CULTURE = 5    # Max articles in Section 2 (Art & Culture)
MAX_ARTICLES_THOUGHT = 5    # Max articles in Section 3 (Thought Leadership)
MAX_TOTAL = 30              # Hard cap across all sections

# Deduplication: articles with title cosine similarity above this are merged
DEDUP_THRESHOLD = 0.75

# Trending score: (reddit_upvotes / REDDIT_DIVISOR) + (hn_score / HN_DIVISOR), capped at TRENDING_CAP
REDDIT_DIVISOR  = 1000
HN_DIVISOR      = 100
TRENDING_CAP    = 3.0
TRENDING_BADGE_THRESHOLD = 1.5   # Trending badge shown if score >= this

# -----------------------------------------------------------------------------
# OUTPUT PATHS
# Relative to project root — GitHub Actions writes here, GitHub Pages serves it
# -----------------------------------------------------------------------------
DOCS_DIR        = "docs"
DIGEST_FILENAME = "{date}.html"     # e.g. 2026-04-17.html
INDEX_FILENAME  = "index.html"

# -----------------------------------------------------------------------------
# AI MODEL
# -----------------------------------------------------------------------------
GEMINI_MODEL = "gemini-2.0-flash-lite"
GEMINI_MAX_RETRIES = 3
GEMINI_RETRY_DELAY = 5   # seconds between retries on rate limit
