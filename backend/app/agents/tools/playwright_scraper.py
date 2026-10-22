"""Playwright scraper — headless browser scraping for JS-heavy sites."""

import asyncio
from typing import Any, Dict, Optional

from app.config.logging_config import get_logger
from app.config.settings import settings
from app.utils.text_cleaner import TextCleaner


class PlaywrightScraperTool:
    """
    Scrapes a URL using Playwright (Chromium headless).

    Handles JS-rendered pages, waits for network idle, and extracts
    clean text from the resulting HTML.
    """

    def __init__(
        self,
        headless: Optional[bool] = None,
        timeout: Optional[int] = None,
    ):
        self.logger = get_logger(__name__)
        self.headless = headless if headless is not None else settings.PLAYWRIGHT_HEADLESS
        self.timeout = timeout or settings.PLAYWRIGHT_TIMEOUT
        self.cleaner = TextCleaner()

    async def _scrape_async(self, url: str) -> Dict[str, Any]:
        from playwright.async_api import async_playwright

        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                )
                page = await context.new_page()
                await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                try:
                    await page.wait_for_load_state("networkidle", timeout=self.timeout)
                except Exception:
                    pass

                title = await page.title()
                html = await page.content()
                await browser.close()

                text = self.cleaner.extract_main_text(html)
                return {
                    "success": True,
                    "url": url,
                    "title": title,
                    "text": text,
                    "error": None,
                }
        except Exception as exc:
            self.logger.warning(f"Playwright scrape failed for {url}: {exc}")
            return {
                "success": False,
                "url": url,
                "title": None,
                "text": None,
                "error": str(exc),
            }

    def scrape(self, url: str) -> Dict[str, Any]:
        """Synchronous wrapper around the async scraper."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're inside an async context; use a new loop in a thread
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(
                        lambda: asyncio.run(self._scrape_async(url))
                    ).result()
            return loop.run_until_complete(self._scrape_async(url))
        except RuntimeError:
            return asyncio.run(self._scrape_async(url))

    async def scrape_many(self, urls: list[str]) -> list[Dict[str, Any]]:
        """Scrape multiple URLs concurrently."""
        sem = asyncio.Semaphore(settings.PLAYWRIGHT_MAX_CONCURRENT)

        async def _bounded(u: str):
            async with sem:
                return await self._scrape_async(u)

        return await asyncio.gather(*[_bounded(u) for u in urls])