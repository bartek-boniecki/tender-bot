# ingestion/html_scraper.py
import asyncio
from playwright.async_api import async_playwright

async def get_notice_html(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url, timeout=60000)
            await asyncio.sleep(1)

            # Accept cookies
            try:
                cookie_btn = await page.query_selector('button:has-text("Accept all cookies")')
                if cookie_btn:
                    await cookie_btn.click()
                    await asyncio.sleep(1)
            except Exception:
                pass

            await page.wait_for_selector("div#notice", timeout=40000)
            html = await page.content()
            return html
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return ""
        finally:
            await browser.close()
