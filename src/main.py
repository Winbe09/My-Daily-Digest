# =============================================================================
# KritiDigest — Main Orchestrator
# Run this script daily (via GitHub Actions) to generate the digest.
#
# Usage:
#   python src/main.py
#
# Required env var:
#   GEMINI_API_KEY — your Google AI Studio API key
# =============================================================================

import os
import sys
import logging
from datetime import date, timedelta
from pathlib import Path

# Allow imports from src/
sys.path.insert(0, str(Path(__file__).parent))

from config import DOCS_DIR, DIGEST_FILENAME, INDEX_FILENAME
from fetch import fetch_all
from deduplicate import deduplicate
from score import score_articles, generate_glance
from render import render_digest, render_index

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def main():
    log.info("=" * 60)
    log.info("KritiDigest — starting daily run")
    log.info("=" * 60)

    # Validate environment
    if not os.environ.get("GEMINI_API_KEY"):
        log.error("GEMINI_API_KEY environment variable not set. Exiting.")
        sys.exit(1)

    today = date.today()

    # ------------------------------------------------------------------
    # Step 1: Fetch
    # ------------------------------------------------------------------
    log.info("STEP 1 — Fetching articles from all sources")
    articles = fetch_all()

    if not articles:
        log.error("No articles fetched. Check source configs and network. Exiting.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 2: Deduplicate
    # ------------------------------------------------------------------
    log.info("STEP 2 — Deduplicating")
    articles = deduplicate(articles)

    # ------------------------------------------------------------------
    # Step 3: Score & classify
    # ------------------------------------------------------------------
    log.info("STEP 3 — Scoring and classifying with Gemini")
    sections = score_articles(articles)

    total = sum(len(v) for v in sections.values())
    if total == 0:
        log.error("All articles were filtered out. Check scoring thresholds. Exiting.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 4: Generate 'Today at a Glance'
    # ------------------------------------------------------------------
    log.info("STEP 4 — Generating Today at a Glance")
    glance = generate_glance(sections)

    # ------------------------------------------------------------------
    # Step 5: Render HTML
    # ------------------------------------------------------------------
    log.info("STEP 5 — Rendering HTML digest")
    prev_date = today - timedelta(days=1)
    next_date = None   # future digest doesn't exist yet

    digest_html = render_digest(
        sections=sections,
        glance_bullets=glance,
        digest_date=today,
        prev_date=prev_date,
        next_date=next_date,
    )

    # ------------------------------------------------------------------
    # Step 6: Write output files
    # ------------------------------------------------------------------
    log.info("STEP 6 — Writing output files")
    docs_path = Path(DOCS_DIR)
    docs_path.mkdir(parents=True, exist_ok=True)

    # Daily digest file
    digest_path = docs_path / DIGEST_FILENAME.format(date=today)
    digest_path.write_text(digest_html, encoding="utf-8")
    log.info(f"  Digest written: {digest_path}")

    # Update archive index — scan all dated HTML files in docs/
    dated_files = sorted(
        [f.stem for f in docs_path.glob("????-??-??.html")],
        reverse=True,
    )
    date_objects = []
    for stem in dated_files:
        try:
            date_objects.append(date.fromisoformat(stem))
        except ValueError:
            pass

    index_html = render_index(date_objects)
    index_path = docs_path / INDEX_FILENAME
    index_path.write_text(index_html, encoding="utf-8")
    log.info(f"  Index written: {index_path} ({len(date_objects)} digests listed)")

    log.info("=" * 60)
    log.info(f"KritiDigest complete — {total} articles across 3 sections")
    log.info(f"  News: {len(sections['news'])} | Culture: {len(sections['culture'])} | Thought: {len(sections['thought'])}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
