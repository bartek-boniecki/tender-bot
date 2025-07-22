# orchestration/run_pipeline.py

import asyncio
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_html
from analysis.openai_summary import summarize_criteria

async def _run_pipeline(cpv: str, keyword: str, max_items: int = 20):
    """
    1) Fetch up to max_items TED tender URLs matching cpv + keyword
       via fetch_notice_urls()
    2) Scrape each URL’s HTML via get_html()
    3) Summarize eligibility & award criteria via summarize_criteria()
    Returns a list of {"url": ..., "summary": ...}.
    """
    urls = await fetch_notice_urls(cpv, keyword)
    results = []

    for url in urls[:max_items]:
        html    = await get_html(url)
        summary = await summarize_criteria(html)
        results.append({"url": url, "summary": summary})

    return results

def run_pipeline_with_params(cpv: str, keyword: str):
    """
    Synchronous entry‑point for both FastAPI (main.py) and weekly_job.py
    """
    return asyncio.run(_run_pipeline(cpv, keyword))
