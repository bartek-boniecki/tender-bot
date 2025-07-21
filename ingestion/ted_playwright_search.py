# ingestion/ted_playwright_search.py
import asyncio
from playwright.async_api import async_playwright

async def fetch_notice_urls(cpv: str, keyword: str, pages: int = 1) -> list[str]:
    base_url = "https://ted.europa.eu/en/search/result"
    urls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for page_num in range(1, pages + 1):
            search_url = (
                f"{base_url}?FT={keyword}&classification-cpv={cpv}"
                f"&search-scope=ACTIVE&scope=ACTIVE&onlyLatestVersions=false"
                f"&sortColumn=publication-number&sortOrder=DESC&page={page_num}"
            )
            print(f"Scraping: {search_url}")
            await page.goto(search_url, timeout=60000)

            try:
                # Accept cookies
                cookie_button = await page.query_selector('button:has-text("Accept all cookies")')
                if cookie_button:
                    await cookie_button.click()
                    await asyncio.sleep(1)
            except Exception:
                pass

            try:
                await page.wait_for_selector("a[href*='/notice/-/detail/']", timeout=15000)
                anchors = await page.query_selector_all("a[href*='/notice/-/detail/']")
                for a in anchors:
                    href = await a.get_attribute("href")
                    if href and href.startswith("/en/notice/-/detail/"):
                        full_url = "https://ted.europa.eu" + href
                        if full_url not in urls:
                            urls.append(full_url)
            except Exception as e:
                print(f"Warning: Failed to extract links on page {page_num}: {e}")

        await browser.close()

    print(f"Total notices found: {len(urls)}")
    return urls
