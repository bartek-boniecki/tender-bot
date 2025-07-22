from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import summarize_eligibility

import asyncio

async def run_pipeline_with_params(cpv, keyword, pages=1):
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)
    urls = urls[:20]
    tenders = []
    for url in urls:
        html = await get_notice_html(url)
        summary = summarize_eligibility(html)
        tenders.append({
            "url": url,
            "summary": summary,
        })
    return tenders