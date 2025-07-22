import asyncio
from asyncio_throttle import Throttler

from ingestion.ted_playwright_search import search_tender_urls
from ingestion.html_scraper import fetch_tender_html
from analysis.openai_summary import summarize_eligibility
from utils.supabase_client import get_all_users, save_tender_data
from utils.emailer import send_tender_email

# Limit to 5 concurrent tasks per second (adjust to your OpenAI & TED limits)
throttler = Throttler(rate_limit=5, period=1)

async def process_user(user: dict) -> None:
    user_id = user["id"]
    keyword = user.get("keyword")
    cpv = user.get("cpv")
    email = user.get("email")

    # 1) Discover tender notice URLs
    urls = await search_tender_urls(keyword, cpv)

    # 2) Fetch, summarize & save
    async def handle_url(url: str) -> dict:
        async with throttler:
            html = await fetch_tender_html(url)
            summary = await summarize_eligibility(html)
            # upsert into Supabase
            await save_tender_data(
                user_id=user_id,
                cpv=cpv,
                keyword=keyword,
                tender_url=url,
                criteria_summary=summary,
            )
            return {"url": url, "summary": summary}

    tasks = [asyncio.create_task(handle_url(u)) for u in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 3) Collate successful summaries
    successes = [r for r in results if not isinstance(r, Exception)]

    # 4) Send one email per user with all results
    if successes:
        await send_tender_email(user_email=email, summaries=successes)

async def main() -> None:
    users = await get_all_users()
    await asyncio.gather(*(process_user(u) for u in users))

if __name__ == "__main__":
    asyncio.run(main())