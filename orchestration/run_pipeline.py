# orchestration/run_pipeline.py

import logging
import asyncio
from bs4 import BeautifulSoup
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import summarize_eligibility, summarize_subject_matter

logger = logging.getLogger("tender-bot.pipeline")

async def run_pipeline_with_params(
    cpv: str,
    keyword: str,
    pages: int = 1
) -> list[dict]:
    """
    1) Fetch TED URLs for cpv+keyword
    2) Scrape each notice’s HTML
    3) Extract the real <h1> as title
    4) Generate a 200‑char subject‐matter summary
    5) Generate the HTML eligibility snippet
    Returns a list of {"title","subject_summary","url","summary"}.
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

            # 3) Official title from the page's <h1>
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            title = h1.get_text().strip() if h1 else "Tender Notice"

            # 4) Short subject summary of required work
            subject_summary = await summarize_subject_matter(html)

            # 5) Eligibility & award criteria snippet
            criteria_html = await summarize_eligibility(html)

            tenders.append({
                "title": title,
                "subject_summary": subject_summary,
                "url": url,
                "summary": criteria_html
            })

        except Exception:
            logger.exception(f"Error processing tender at {url}")

    return tenders
