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
    1) Fetch up to `pages` pages of TED tender URLs matching cpv + keyword
       via fetch_notice_urls()
    2) Scrape each URL’s HTML via get_notice_html()
    3) Summarize eligibility & award criteria via summarize_eligibility()
    Returns a list of {"url": ..., "summary": ...}.
    """
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)  # from ingestion/ted_playwright_search.py :contentReference[oaicite:0]{index=0}
    results = []

    for url in urls[:max_items]:
        html    = await get_notice_html(url)                     # from ingestion/html_scraper.py :contentReference[oaicite:1]{index=1}
        summary = summarize_eligibility(html)                    # from analysis/openai_summary.py :contentReference[oaicite:2]{index=2}
        results.append({"url": url, "summary": summary})

    return results
