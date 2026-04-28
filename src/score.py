# =============================================================================
# KritiDigest — AI Scoring & Summarisation
# Sends each article to Gemini Flash for relevance scoring, section
# classification, and personalised summary generation.
# =============================================================================

import json
import logging
import time
import os

import google.generativeai as genai

from config import (
    PREFERENCE_PROFILE, GEMINI_MODEL, GEMINI_MAX_RETRIES, GEMINI_RETRY_DELAY,
    MIN_SCORE, SECONDARY_MIN_SCORE,
    MAX_ARTICLES_NEWS, MAX_ARTICLES_CULTURE, MAX_ARTICLES_THOUGHT,
)

log = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
_model = genai.GenerativeModel(GEMINI_MODEL)

SCORING_PROMPT = """You are a personal news curator for the following person:

{preference_profile}

Score this article for relevance to this person's interests (1–10).
Classify it into exactly one section:
  - "news"    → current events, geopolitics, macroeconomics, business, tech trends
  - "culture" → art, entertainment, film, music, lifestyle, sports
  - "thought" → longform strategy, leadership, business frameworks, educational content (e.g. HBR, McKinsey)

Article title:   {title}
Source:          {source}
Snippet:         {snippet}
Trending signal: {trending_score} (0–3 scale; higher = more social traction today)

Reply with valid JSON only — no markdown, no explanation:
{{"score": <1-10>, "section": "<news|culture|thought>", "reason": "<one sentence why>", "summary": "<2-3 sentences summarising the article, framed for this person's context and role>"}}"""


def _score_single(article):
    """Call Gemini to score and summarise one article. Returns updated article dict."""
    prompt = SCORING_PROMPT.format(
        preference_profile=PREFERENCE_PROFILE.strip(),
        title=article["title"],
        source=article["source"],
        snippet=article["snippet"] or "(no snippet available)",
        trending_score=article.get("trending_score", 0),
    )

    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            response = _model.generate_content(prompt)
            raw = response.text.strip()

            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            data = json.loads(raw)
            article["score"]   = int(data.get("score", 0))
            article["section"] = data.get("section", "news")
            article["reason"]  = data.get("reason", "")
            article["summary"] = data.get("summary", "")
            return article

        except json.JSONDecodeError as e:
            log.warning(f"  JSON parse error on attempt {attempt} for '{article['title'][:50]}': {e}")
        except Exception as e:
            log.warning(f"  Gemini error on attempt {attempt} for '{article['title'][:50]}': {e}")
            if attempt < GEMINI_MAX_RETRIES:
                time.sleep(GEMINI_RETRY_DELAY * attempt)

    # Graceful fallback: use first snippet sentences as summary, score 0 (will be filtered)
    log.error(f"  Scoring failed after {GEMINI_MAX_RETRIES} attempts: '{article['title'][:60]}' — using fallback")
    article["score"]   = 0
    article["section"] = "news"
    article["reason"]  = "Scoring unavailable"
    article["summary"] = article.get("snippet", article["title"])
    return article


def score_articles(articles):
    """
    Score all articles. Applies minimum score filters and returns
    a dict with three section lists, each sorted by score descending.
    """
    log.info(f"Scoring {len(articles)} articles with Gemini {GEMINI_MODEL}...")
    scored = []

    for i, article in enumerate(articles):
        log.info(f"  [{i+1}/{len(articles)}] {article['title'][:70]}")
        scored.append(_score_single(article))
        # Gentle rate-limit throttle (Gemini free tier: 15 req/min)
        time.sleep(1.5)

    # Apply minimum score thresholds
    def passes_threshold(a):
        if a["score"] is None or a["score"] == 0:
            return False
        if a.get("is_secondary") or a.get("is_newsletter"):
            return a["score"] >= SECONDARY_MIN_SCORE
        return a["score"] >= MIN_SCORE

    filtered = [a for a in scored if passes_threshold(a)]
    log.info(f"After filtering: {len(filtered)} articles pass threshold ({len(scored) - len(filtered)} removed)")

    # Split into sections and sort each by score descending
    news    = sorted([a for a in filtered if a["section"] == "news"],    key=lambda x: x["score"], reverse=True)
    culture = sorted([a for a in filtered if a["section"] == "culture"], key=lambda x: x["score"], reverse=True)
    thought = sorted([a for a in filtered if a["section"] == "thought"], key=lambda x: x["score"], reverse=True)

    # Apply per-section caps
    news    = news[:MAX_ARTICLES_NEWS]
    culture = culture[:MAX_ARTICLES_CULTURE]
    thought = thought[:MAX_ARTICLES_THOUGHT]

    log.info(f"Final: {len(news)} news | {len(culture)} culture | {len(thought)} thought leadership")

    return {
        "news":    news,
        "culture": culture,
        "thought": thought,
    }


def generate_glance(sections):
    """
    Generate the 'Today at a Glance' bullet points from top articles across sections.
    Returns a list of 3-4 short strings.
    """
    top_articles = (
        sections["news"][:4] +
        sections["culture"][:1] +
        sections["thought"][:1]
    )
    if not top_articles:
        return ["No articles available today."]

    titles_and_summaries = "\n".join(
        f"- {a['title']}: {a.get('summary', '')}" for a in top_articles[:6]
    )

    prompt = f"""Based on these top articles from today's digest, write 3-4 crisp bullet points for a 'Today at a Glance' section.
Each bullet should be one sentence, factual, and framed for a strategy professional who leads AI GTM for a devtools company.
Start each bullet directly with the insight — no numbering, no labels.

Articles:
{titles_and_summaries}

Reply with a JSON array of strings only, e.g. ["Point one.", "Point two.", "Point three."]"""

    try:
        response = _model.generate_content(prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        log.warning(f"Glance generation failed: {e} — using article titles as fallback")
        return [a["title"] for a in top_articles[:4]]
