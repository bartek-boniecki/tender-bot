import logging
import asyncio
from bs4 import BeautifulSoup
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import (
    summarize_eligibility,
    summarize_subject_matter
)

logger = logging.getLogger("tender-bot.pipeline")

async def run_pipeline_with_params(
    cpv: str,
    keyword: str,
    pages: int = 1
) -> list[dict]:
    """
    1) Fetch TED URLs for cpv+keyword
    2) Scrape HTML
    3) Extract the true <h1> as `title`
    4) Generate a short (≤200 chars) subject‑matter summary in English
    5) Generate the HTML eligibility snippet
    Returns a list of dicts: {title, subject_matter, url, summary_html}
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

            # 3) Official title from <h1>
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            title = h1.get_text().strip() if h1 else "Tender Notice"

            # 4) Short subject‑matter summary (≤200 chars, English)
            subject_matter = await summarize_subject_matter(html)

            # 5) Eligibility & award criteria snippet (English HTML)
            criteria_html = await summarize_eligibility(html)

            tenders.append({
                "title": title,
                "subject_matter": subject_matter,
                "url": url,
                "summary_html": criteria_html
            })

        except Exception:
            logger.exception(f"Error processing tender at {url}")

    return tenders
