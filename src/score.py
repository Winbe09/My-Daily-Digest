# =============================================================================
# KritiDigest — Article Organiser
# No AI scoring. Groups deduplicated articles by source for rendering.
# =============================================================================

import logging
from config import RSS_SOURCES, SECONDARY_RSS_SOURCES, SCRAPE_SOURCES

log = logging.getLogger(__name__)

# Source priority order for display (matches config priority values)
SOURCE_ORDER = (
    [s["name"] for s in RSS_SOURCES] +
    [s["name"] for s in SCRAPE_SOURCES] +
    [s["name"] for s in SECONDARY_RSS_SOURCES]
)


def organise(articles):
    """
    Group articles by source. Returns an ordered dict: source name → list of articles.
    Sources are ordered by their priority in config.py.
    Newsletter sources and unknown sources appear at the end.
    """
    grouped = {}
    for article in articles:
        source = article["source"]
        grouped.setdefault(source, []).append(article)

    # Sort sources by priority order; unknown sources go last alphabetically
    def sort_key(source):
        try:
            return SOURCE_ORDER.index(source)
        except ValueError:
            return len(SOURCE_ORDER)

    ordered = dict(sorted(grouped.items(), key=lambda x: sort_key(x[0])))

    total = sum(len(v) for v in ordered.values())
    log.info(f"Organised {total} articles across {len(ordered)} sources")
    for source, arts in ordered.items():
        log.info(f"  {source}: {len(arts)} articles")

    return ordered
