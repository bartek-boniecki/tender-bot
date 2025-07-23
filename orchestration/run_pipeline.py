# orchestration/run_pipeline.py

import logging
import asyncio
from bs4 import BeautifulSoup
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import summarize_eligibility, extract_descriptive_title

logger = logging.getLogger("tender-bot.pipeline")

async def run_pipeline_with_params(
    cpv: str,
    keyword: str,
    pages: int = 1
) -> list[dict]:
    """
    1) Fetch TED URLs matching cpv+keyword
    2) Scrape HTML for each
    3) Extract a meaningful title via GPT (fallback to <h1>)
    4) Summarize criteria in English via GPT
    Returns list of {"title","url","summary"}.
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

            # 1) Extract descriptive title
            title = await extract_descriptive_title(html)

            # 2) Summarize eligibility & award criteria in English
            summary = await summarize_eligibility(html)

            tenders.append({
                "title": title,
                "url": url,
                "summary": summary
            })

        except Exception:
            logger.exception(f"Error processing tender at {url}")

    return tenders
