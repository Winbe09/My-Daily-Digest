# =============================================================================
# KritiDigest — Article Fetcher
# Handles RSS, scraping, newsletters, and social trending signals.
# =============================================================================

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import time
import logging

from config import (
    RSS_SOURCES, SECONDARY_RSS_SOURCES, SCRAPE_SOURCES, NEWSLETTER_SOURCES,
    REDDIT_SUBREDDITS, HN_STORY_LIMIT,
    REDDIT_DIVISOR, HN_DIVISOR, TRENDING_CAP, TRENDING_BADGE_THRESHOLD,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

HEADERS = {"User-Agent": "KritiDigest/1.0 (personal news digest; contact via GitHub)"}
REQUEST_TIMEOUT = 10   # seconds


# =============================================================================
# HELPERS
# =============================================================================

def _now_utc():
    return datetime.now(timezone.utc)


def _parse_date(entry):
    """Extract publication datetime from a feedparser entry. Returns UTC datetime or None."""
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _is_recent(dt, max_age_hours=24):
    if dt is None:
        return True   # include if we can't determine age
    return (_now_utc() - dt).total_seconds() < max_age_hours * 3600


def _snippet(text, max_chars=300):
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    return text[:max_chars].rsplit(" ", 1)[0] + "…" if len(text) > max_chars else text


def _make_article(title, url, source, snippet="", published=None, is_secondary=False, is_newsletter=False):
    return {
        "title": title.strip(),
        "url": url.strip(),
        "source": source,
        "snippet": snippet,
        "published": published.isoformat() if published else None,
        "is_secondary": is_secondary,
        "is_newsletter": is_newsletter,
        "trending_score": 0.0,
        "is_trending": False,
        "also_covered_by": [],
        # Filled by score.py:
        "score": None,
        "section": None,
        "reason": None,
        "summary": None,
    }


# =============================================================================
# RSS FETCHING
# =============================================================================

def fetch_rss(source, max_age_hours=24, is_secondary=False):
    """Fetch articles from an RSS feed. Returns list of article dicts."""
    articles = []
    log.info(f"Fetching RSS: {source['name']} ({source['url']})")
    try:
        feed = feedparser.parse(source["url"])
        if feed.bozo and not feed.entries:
            log.warning(f"  Feed parse error for {source['name']}: {feed.bozo_exception}")
            return []
        for entry in feed.entries:
            published = _parse_date(entry)
            if not _is_recent(published, max_age_hours=max_age_hours if not is_secondary else 7 * 24):
                continue
            title = entry.get("title", "").strip()
            url   = entry.get("link", "").strip()
            if not title or not url:
                continue
            snippet = _snippet(entry.get("summary", "") or entry.get("content", [{}])[0].get("value", ""))
            articles.append(_make_article(title, url, source["name"], snippet, published, is_secondary=is_secondary))
        log.info(f"  → {len(articles)} articles fetched")
    except Exception as e:
        log.error(f"  Failed to fetch {source['name']}: {e}")
    return articles


# =============================================================================
# WEB SCRAPING
# =============================================================================

def scrape_source(source):
    """Scrape article links from a homepage using a CSS selector."""
    articles = []
    log.info(f"Scraping: {source['name']} ({source['url']})")
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        seen_urls = set()
        for el in soup.select(source["article_selector"]):
            title = el.get_text(strip=True)
            href  = el.get("href", "")
            if not title or not href or len(title) < 20:
                continue
            if not href.startswith("http"):
                from urllib.parse import urljoin
                href = urljoin(source["url"], href)
            if href in seen_urls:
                continue
            seen_urls.add(href)
            articles.append(_make_article(title, href, source["name"]))
            if len(articles) >= 20:
                break
        log.info(f"  → {len(articles)} articles scraped")
    except Exception as e:
        log.error(f"  Failed to scrape {source['name']}: {e}")
    return articles


# =============================================================================
# SOCIAL TRENDING SIGNALS
# =============================================================================

def fetch_reddit_posts():
    """Fetch top posts from configured subreddits. Returns list of {title, score}."""
    posts = []
    for sub in REDDIT_SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=20"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            for child in data.get("data", {}).get("children", []):
                p = child.get("data", {})
                posts.append({
                    "title": p.get("title", ""),
                    "score": p.get("score", 0),
                    "subreddit": sub,
                })
            time.sleep(0.5)   # be polite to Reddit
        except Exception as e:
            log.warning(f"  Reddit r/{sub} failed: {e}")
    log.info(f"Fetched {len(posts)} Reddit posts across {len(REDDIT_SUBREDDITS)} subreddits")
    return posts


def fetch_hn_posts():
    """Fetch top Hacker News stories. Returns list of {title, score}."""
    posts = []
    try:
        url = f"https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage={HN_STORY_LIMIT}"
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        for hit in resp.json().get("hits", []):
            posts.append({
                "title": hit.get("title", ""),
                "score": hit.get("points", 0),
            })
        log.info(f"Fetched {len(posts)} HN stories")
    except Exception as e:
        log.warning(f"  HN fetch failed: {e}")
    return posts


def _jaccard_similarity(a, b):
    """Token-level Jaccard similarity between two strings."""
    sa = set(a.lower().split())
    sb = set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def enrich_with_trending(articles, reddit_posts, hn_posts):
    """
    Compute a trending score for each article by matching it against
    Reddit and HN posts. Mutates articles in place.
    """
    for article in articles:
        title = article["title"]
        reddit_score = 0
        hn_score = 0

        for post in reddit_posts:
            if _jaccard_similarity(title, post["title"]) >= 0.4:
                reddit_score = max(reddit_score, post["score"])

        for post in hn_posts:
            if _jaccard_similarity(title, post["title"]) >= 0.4:
                hn_score = max(hn_score, post["score"])

        trending = min(
            (reddit_score / REDDIT_DIVISOR) + (hn_score / HN_DIVISOR),
            TRENDING_CAP,
        )
        article["trending_score"] = round(trending, 2)
        article["is_trending"] = trending >= TRENDING_BADGE_THRESHOLD

    return articles


# =============================================================================
# MAIN FETCH ORCHESTRATOR
# =============================================================================

def fetch_all():
    """
    Fetch all articles from all sources and enrich with trending signals.
    Returns a flat list of article dicts, ready for deduplication.
    """
    articles = []

    # Primary RSS
    for source in RSS_SOURCES:
        articles.extend(fetch_rss(source))

    # Secondary RSS (HBR etc — 7-day window)
    for source in SECONDARY_RSS_SOURCES:
        articles.extend(fetch_rss(source, is_secondary=True))

    # Scrape sources
    for source in SCRAPE_SOURCES:
        articles.extend(scrape_source(source))

    # Newsletter RSS (treated same as primary)
    for source in NEWSLETTER_SOURCES:
        fetched = fetch_rss({**source, "priority": 99}, is_newsletter=True)
        for a in fetched:
            a["is_newsletter"] = True
        articles.extend(fetched)

    # Trending signals
    reddit_posts = fetch_reddit_posts()
    hn_posts     = fetch_hn_posts()
    articles     = enrich_with_trending(articles, reddit_posts, hn_posts)

    log.info(f"Total articles fetched (pre-dedup): {len(articles)}")
    return articles
