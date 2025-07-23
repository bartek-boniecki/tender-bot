# orchestration/run_pipeline.py

import logging
from bs4 import BeautifulSoup
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import summarize_eligibility

logger = logging.getLogger("tender-bot.pipeline")

async def run_pipeline_with_params(
    cpv: str,
    keyword: str,
    pages: int = 1
) -> list[dict]:
    """
    1) Fetch TED URLs for cpv+keyword
    2) Scrape each notice’s HTML
    3) Extract the page <title> as tender title
    4) Summarize criteria via GPT
    Returns a list of {"title", "url", "summary"} dicts.
    """
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)
    logger.info(f"Found {len(urls)} tender URLs for {cpv} + {keyword}")

    tenders = []
    for url in urls[:20]:
        try:
            html = await get_notice_html(url)
            if not html:
                logger.warning(f"Failed scraping {url}, skipping")
                continue

            # Extract the tender title from the <title> tag
            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.get_text().strip() if title_tag else "Tender Notice"

            # Summarize the eligibility & award criteria
            summary = await summarize_eligibility(html)

            # Append with title, summary, and URL
            tenders.append({
                "title": title,
                "summary": summary,
                "url": url
            })

        except Exception:
            logger.exception(f"Error processing tender at {url}")

    return tenders
