# =============================================================================
# KritiDigest — Main Orchestrator
# Fetch → Deduplicate → Render. No AI required.
#
# Usage:
#   python src/main.py
# =============================================================================

import sys
import logging
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import DOCS_DIR, DIGEST_FILENAME, INDEX_FILENAME
from fetch import fetch_all
from deduplicate import deduplicate
from score import organise
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

    today = date.today()

    # Step 1: Fetch
    log.info("STEP 1 — Fetching articles from all sources")
    articles = fetch_all()
    if not articles:
        log.error("No articles fetched. Check source configs. Exiting.")
        sys.exit(1)

    # Step 2: Deduplicate
    log.info("STEP 2 — Deduplicating")
    articles = deduplicate(articles)

    # Step 3: Organise by source
    log.info("STEP 3 — Organising by source")
    grouped = organise(articles)

    # Step 4: Render
    log.info("STEP 4 — Rendering HTML digest")
    digest_html = render_digest(
        grouped=grouped,
        digest_date=today,
        prev_date=today - timedelta(days=1),
        next_date=None,
    )

    # Step 5: Write files
    log.info("STEP 5 — Writing output files")
    docs_path = Path(DOCS_DIR)
    docs_path.mkdir(parents=True, exist_ok=True)

    digest_path = docs_path / DIGEST_FILENAME.format(date=today)
    digest_path.write_text(digest_html, encoding="utf-8")
    log.info(f"  Digest written: {digest_path}")

    dated_files  = sorted([f.stem for f in docs_path.glob("????-??-??.html")], reverse=True)
    date_objects = []
    for stem in dated_files:
        try:
            date_objects.append(date.fromisoformat(stem))
        except ValueError:
            pass

    index_path = docs_path / INDEX_FILENAME
    index_path.write_text(render_index(date_objects), encoding="utf-8")
    log.info(f"  Index written: {index_path}")

    total = sum(len(v) for v in grouped.values())
    log.info("=" * 60)
    log.info(f"KritiDigest complete — {total} articles across {len(grouped)} sources")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
