# orchestration/run_pipeline.py

import asyncio
from ingestion.ted_playwright_search import fetch_notice_urls
from ingestion.html_scraper import get_notice_html
from analysis.openai_summary import summarize_eligibility

async def run_pipeline_with_params(cpv, keyword, pages=1):
    urls = await fetch_notice_urls(cpv, keyword, pages=pages)
    # Limit to 10 tenders maximum
    urls = urls[:10]
    tenders = []
    for url in urls:
        html = await get_notice_html(url)
        summary = summarize_eligibility(html)
        tenders.append({
            "url": url,
            "summary": summary,
        })
    return tenders

# For CLI testing only
if __name__ == "__main__":
    import sys
    cpv = sys.argv[1] if len(sys.argv) > 1 else "45000000"
    keyword = sys.argv[2] if len(sys.argv) > 2 else "construction"
    asyncio.run(run_pipeline_with_params(cpv, keyword))
