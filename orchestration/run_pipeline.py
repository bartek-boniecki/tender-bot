# orchestration/run_pipeline.py

import asyncio
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import summarize_eligibility

async def run_pipeline_with_params(
    cpv: str,
    keyword: str,
    pages: int = 1,
    max_items: int = 20
) -> list[dict]:
    """
    1) Fetch up to `pages` pages of TED tender URLs matching cpv+keyword
       (async def fetch_notice_urls in ingestion/ted_playwright_search.py) :contentReference[oaicite:0]{index=0}
    2) Scrape each notice’s HTML (async def get_notice_html in ingestion/html_scraper.py) :contentReference[oaicite:1]{index=1}
    3) Summarize eligibility & award criteria (def summarize_eligibility in analysis/openai_summary.py) :contentReference[oaicite:2]{index=2}
    Returns a list of {"url": ..., "summary": ...}.
    """
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)
    results = []
    for url in urls[:max_items]:
        html = await get_notice_html(url)
        summary = summarize_eligibility(html)
        results.append({"url": url, "summary": summary})
    return results
