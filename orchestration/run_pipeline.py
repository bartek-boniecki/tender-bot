# orchestration/run_pipeline.py

import asyncio
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import summarize_eligibility

async def _run_pipeline(
    cpv: str,
    keyword: str,
    pages: int = 1,
    max_items: int = 20
) -> list[dict]:
    """
    1) Fetch up to `pages` pages of TED tender URLs for cpv+keyword
    2) Scrape each notice’s HTML via get_notice_html
    3) Summarize eligibility & award criteria via summarize_eligibility
    Returns a list of {"url": ..., "summary": ...}.
    """
    # Step 1: discover URLs
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)

    results = []
    # Step 2 & 3: scrape + summarize, cap to max_items
    for url in urls[:max_items]:
        html    = await get_notice_html(url)
        summary = await summarize_eligibility(html)
        results.append({"url": url, "summary": summary})

    return results

def run_pipeline_with_params(
    cpv: str,
    keyword: str,
    pages: int = 1
) -> list[dict]:
    """
    Synchronous entry‑point for FastAPI and weekly_job.
    """
    return asyncio.run(_run_pipeline(cpv, keyword, pages=pages))
