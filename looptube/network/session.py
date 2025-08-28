from fake_useragent import UserAgent
from playwright.async_api import async_playwright, Page, Dialog, Locator
from looptube.core import LTModel
from time import sleep
from typing import Any
import re
import asyncio

from joblib import Parallel, delayed

from .downloader import LTDownloader


class LTRequest(LTModel):
    """Async session for Looptube"""

    COOKIE_JAR: list = []
    LOCAL_STORAGE: dict[str, Any] = dict()
    SESSION_STORAGE: dict[str, Any] = dict()

    def __init__(
        self,
        headless: bool = False,
        scroll: bool = True,
        clicks: list[str] | None = None,
        wait_fors: list[str] | None = None,
        max_scroll: int = 5,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.headless = headless
        self.scroll = scroll
        self.clicks = clicks
        self.wait_fors = wait_fors
        self.max_scroll = max_scroll

    async def validate_locator(self, locator: Locator) -> bool:
        """Validate the locator."""
        if await locator.count() > 0:
            await locator.first.scroll_into_view_if_needed(
                timeout=self.__env__.request_timeout
            )
            await locator.first.click(no_wait_after=False)
            return True
        else:
            return False

    @staticmethod
    def get_user_agent() -> str:
        """Get a random user agent"""
        return UserAgent(
            browsers=["Chrome", "Firefox", "Edge"],
            os=["Windows", "Linux", "Mac"],
            platforms=["desktop"],
        ).random

    async def handle_dialog(dialog: Dialog):
        await dialog.dismiss()

    async def get_local_storage(self, page: Page) -> dict[str, Any]:
        """Get the local storage of the page."""
        return await page.evaluate(
            """() => {
                let data = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        data[key] = localStorage.getItem(key);
                    }
                return data;
            }"""
        )

    async def get_session_storage(self, page: Page) -> dict[str, Any]:
        """Get the session storage of the page."""
        return await page.evaluate(
            """() => {
                let data = {};
                    for (let i = 0; i < sessionStorage.length; i++) {
                        const key = sessionStorage.key(i);
                        data[key] = sessionStorage.getItem(key);
                    }
                return data;
            }"""
        )

    async def scroll_func(self, page: Page) -> str:
        """_summary"""
        await page.evaluate(
            """
                var intervalID = setInterval(function () {
                    var scrollingElement = (
                        document.scrollingElement || document.body
                    );
                    scrollingElement.scrollTop = scrollingElement.scrollHeight;
                }, 200);
            """
        )

        prev_height, scroll_count = None, self.max_scroll
        while bool(scroll_count):
            curr_height = await page.evaluate("(window.innerHeight + window.scrollY)")
            if not prev_height:
                prev_height = curr_height
                sleep(1)
            elif prev_height == curr_height:
                await page.evaluate("clearInterval(intervalID)")
                break
            else:
                prev_height = curr_height
                sleep(1)
                if scroll_count > 0:
                    scroll_count -= 1

    async def doplay(self, url: str) -> str | bytes:
        """Get a playwright page"""
        async with async_playwright() as player:
            browser = await player.chromium.launch(
                headless=self.headless,
                env=self.__env__.model_dump(exclude_none=True),
                timeout=self.__env__.request_timeout,
            )
            page = await browser.new_page(
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True,
                locale="en-US",  # TODO: Make this dynamic, REPLACE WITH LOCALE
                user_agent=self.get_user_agent(),
            )
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.__env__.request_timeout,
            )

            await page.wait_for_load_state("domcontentloaded")

            if self.clicks:
                for _l in self.clicks:
                    locator = page.get_by_role(
                        "button", name=re.compile(_l, re.IGNORECASE)
                    )
                    await self.validate_locator(locator)

                    """if has_local_storage := await self.get_local_storage(page):
                        self.LOCAL_STORAGE.update(has_local_storage)
                    if has_session_storage := await self.get_session_storage(page):
                        self.SESSION_STORAGE.update(has_session_storage)
                    if cookies := await page.context.cookies():
                        self.COOKIE_JAR.extend(cookies)"""

                    await page.wait_for_load_state("networkidle")

            if self.scroll:
                await self.scroll_func(page)

            if self.wait_fors:
                for wait_for in self.wait_fors:
                    await page.wait_for_selector(
                        wait_for,
                        state="visible",
                        timeout=self.__env__.request_timeout,
                    )

            await page.wait_for_load_state("domcontentloaded")
            content = await page.content()
            await page.close()
            await browser.close()

        return content

    def download(self, url: str) -> str | bytes:
        """Download the page"""
        return LTDownloader(url=url).download()

    def run(self, url: str) -> str | bytes:
        return asyncio.run(self.doplay(url))

    def run_parallel(self, urls: list[str]) -> list[str | bytes]:
        parallel = Parallel(n_jobs=-1, backend="loky")
        return parallel(delayed(self.run)(url) for url in urls)
