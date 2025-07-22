# orchestration/run_pipeline.py

import asyncio
from ingestion.ted_playwright_search import search_tenders
from ingestion.html_scraper import get_html
from analysis.openai_summary import summarize_criteria

async def _run_pipeline(cpv: str, keyword: str, max_items: int = 20):
    """
    1) Searches TED for up to max_items tender URLs matching cpv + keyword
    2) Scrapes each URL’s HTML
    3) Summarizes eligibility & award criteria via GPT
    Returns a list of dicts: [{"url": ..., "summary": ...}, ...]
    """
    # Step 1: find matching tenders
    urls = await search_tenders(cpv, keyword)
    results = []

    # Step 2 & 3: for each URL, scrape + summarize
    for url in urls[:max_items]:
        html = await get_html(url)
        summary = await summarize_criteria(html)
        results.append({"url": url, "summary": summary})

    return results

def run_pipeline_with_params(cpv: str, keyword: str):
    """
    Synchronous entry‑point for both FastAPI and our weekly_job.
    """
    return asyncio.run(_run_pipeline(cpv, keyword))
