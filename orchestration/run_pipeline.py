# orchestration/run_pipeline.py

import logging
import asyncio
from bs4 import BeautifulSoup
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import (
    extract_descriptive_title,
    summarize_subject_matter,
    summarize_eligibility
)

logger = logging.getLogger("tender-bot.pipeline")

async def run_pipeline_with_params(cpv: str, keyword: str, pages: int = 1) -> list[dict]:
    """
    1) Fetch TED URLs for cpv+keyword
    2) Scrape each notice’s HTML
    3) Extract a human‑friendly title via GPT (fallback to <h1>)
    4) Generate a short (≤200 char) subject‑matter summary in English
    5) Generate the HTML eligibility snippet in English
    Returns a list of dicts:
      {
        "title": str,
        "subject_matter": str,
        "url": str,
        "summary": str
      }
    """
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)
    logger.info(f"Found {len(urls)} tender URLs for {cpv} + {keyword}")

    tenders = []
    for url in urls[:20]:
        try:
            html = await get_notice_html(url)
            if not html:
                logger.warning(f"Scrape failed for {url}, skipping")
                continue

            # 3) Descriptive title
            title = await extract_descriptive_title(html)

            # 4) 200‑char subject summary (what work is required)
            subject_matter = await summarize_subject_matter(html)

            # 5) Eligibility & award criteria snippet
            criteria_html = await summarize_eligibility(html)

            tenders.append({
                "title": title,
                "subject_matter": subject_matter,
                "url": url,
                "summary": criteria_html
            })

        except Exception:
            logger.exception(f"Error processing tender at {url}")

    return tenders
