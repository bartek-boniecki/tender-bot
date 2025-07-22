import asyncio
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import summarize_eligibility

async def run_pipeline_with_params(
    cpv: str,
    keyword: str,
    pages: int = 1
) -> list[dict]:
    """
    1) Fetch up to `pages` pages of TED tender URLs matching cpv + keyword
    2) Scrape each notice’s HTML
    3) Summarize eligibility & award criteria
    Returns a list of {"url": ..., "summary": ...}.
    """
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)
    tenders = []

    for url in urls[:20]:
        html = await get_notice_html(url)
        if not html:
            # if scraping failed, skip
            continue
        summary = await summarize_eligibility(html)
        tenders.append({"url": url, "summary": summary})

    return tenders
