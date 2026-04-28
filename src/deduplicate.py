# =============================================================================
# KritiDigest — Deduplication
# Collapses duplicate stories (same event covered by multiple sources)
# using TF-IDF cosine similarity on article titles.
# =============================================================================

import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import DEDUP_THRESHOLD, RSS_SOURCES, SECONDARY_RSS_SOURCES, SCRAPE_SOURCES

log = logging.getLogger(__name__)

# Source priority map — lower number = higher priority (kept when deduplicating)
_PRIORITY = {}
for s in RSS_SOURCES:
    _PRIORITY[s["name"]] = s["priority"]
for s in SECONDARY_RSS_SOURCES:
    _PRIORITY[s["name"]] = s["priority"]
for s in SCRAPE_SOURCES:
    _PRIORITY[s["name"]] = s["priority"]


def _source_priority(article):
    """Return priority rank. Lower = more preferred. Unknown sources get rank 50."""
    return _PRIORITY.get(article["source"], 50)


def deduplicate(articles):
    """
    Identify duplicate stories (same event, different sources) using TF-IDF
    cosine similarity on titles. For each cluster of duplicates:
      - Keep the article from the highest-priority source
      - Tag it with "also_covered_by" listing other sources

    Returns a deduplicated list of articles.
    """
    if len(articles) < 2:
        return articles

    titles = [a["title"] for a in articles]

    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(titles)
        sim_matrix = cosine_similarity(tfidf_matrix)
    except Exception as e:
        log.error(f"TF-IDF dedup failed: {e}. Returning articles without deduplication.")
        return articles

    n = len(articles)
    visited = [False] * n
    clusters = []   # list of lists of indices

    for i in range(n):
        if visited[i]:
            continue
        cluster = [i]
        visited[i] = True
        for j in range(i + 1, n):
            if not visited[j] and sim_matrix[i][j] >= DEDUP_THRESHOLD:
                cluster.append(j)
                visited[j] = True
        clusters.append(cluster)

    deduped = []
    duplicates_removed = 0

    for cluster in clusters:
        if len(cluster) == 1:
            deduped.append(articles[cluster[0]])
        else:
            # Sort cluster by source priority — keep lowest priority number
            sorted_cluster = sorted(cluster, key=lambda idx: _source_priority(articles[idx]))
            winner_idx = sorted_cluster[0]
            winner = articles[winner_idx].copy()

            # Tag with other sources
            other_sources = [
                articles[idx]["source"]
                for idx in sorted_cluster[1:]
                if articles[idx]["source"] != winner["source"]
            ]
            # Deduplicate source names while preserving order
            seen = set()
            unique_others = []
            for s in other_sources:
                if s not in seen:
                    seen.add(s)
                    unique_others.append(s)
            winner["also_covered_by"] = unique_others
            deduped.append(winner)
            duplicates_removed += len(cluster) - 1

    log.info(f"Deduplication: {len(articles)} → {len(deduped)} articles ({duplicates_removed} duplicates removed)")
    return deduped
