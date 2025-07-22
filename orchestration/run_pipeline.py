import logging
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import summarize_eligibility

logger = logging.getLogger("tender-bot.pipeline")

async def run_pipeline_with_params(
    cpv: str,
    keyword: str,
    pages: int = 1
) -> list[dict]:
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)
    logger.info(f"Found {len(urls)} tender URLs for {cpv} + {keyword}")

    tenders = []
    for url in urls[:20]:
        try:
            html = await get_notice_html(url)
            if not html:
                logger.warning(f"Failed scraping {url}, skipping")
                continue

            summary = await summarize_eligibility(html)
            tenders.append({"url": url, "summary": summary})
        except Exception:
            logger.exception(f"Error processing tender at {url}")
    return tenders
