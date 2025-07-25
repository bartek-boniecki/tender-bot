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
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)
    logger.info(f"Found {len(urls)} tender URLs for {cpv} + {keyword}")
    tenders = []

    for url in urls[:20]:
        html = await get_notice_html(url)
        if not html:
            logger.warning(f"Scrape failed for {url}, skipping")
            continue

        # 1) Title
        title = await extract_descriptive_title(html)

        # 2) Subject matter
        subject = await summarize_subject_matter(html)

        # 3) Criteria summary (key now 'summary')
        summary = await summarize_eligibility(html)

        # Skip if absolutely nothing was retrieved
        if not any([title, subject, summary]):
            logger.warning(f"No GPT output for {url}, skipping")
            continue

        tenders.append({
            "title": title,
            "subject_matter": subject,
            "url": url,
            "summary": summary
        })

    return tenders
