# orchestration/run_pipeline.py

import logging
import asyncio
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
        try:
            html = await get_notice_html(url)
            if not html:
                logger.warning(f"Scrape failed for {url}, skipping")
                continue

            # 1) GPT‑generated descriptive title
            title = await extract_descriptive_title(html)
            # 2) 200‑char subject matter summary
            subject = await summarize_subject_matter(html)
            # 3) HTML criteria snippet
            criteria = await summarize_eligibility(html)

            tenders.append({
                "title": title,
                "subject_matter": subject,
                "url": url,
                "summary_html": criteria
            })

        except Exception:
            logger.exception(f"Error processing tender at {url}")

    return tenders
