"""
Automated Sonar profile creation for Crawl4AI.

This script logs into `https://alamobb.sonar.software` using credentials
provided in a `.env` file and saves a persistent browser profile. The
resulting profile can be reused for crawling authenticated pages without
repeating the login process.

Required environment variables in `.env`:
  SONAR_USERNAME - your Sonar login username
  SONAR_PASSWORD - your Sonar password
"""

import asyncio
import os
from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler, BrowserConfig
from crawl4ai.browser_profiler import BrowserProfiler
from crawl4ai.async_logger import AsyncLogger
from playwright.async_api import Page, BrowserContext

load_dotenv()

SONAR_USERNAME = os.getenv("SONAR_USERNAME")
SONAR_PASSWORD = os.getenv("SONAR_PASSWORD")

if not SONAR_USERNAME or not SONAR_PASSWORD:
    raise SystemExit("SONAR_USERNAME and SONAR_PASSWORD must be set in the .env file")

PROFILE_NAME = "sonar_profile"
LOGIN_URL = "https://alamobb.sonar.software/login"
TARGET_URL = "https://alamobb.sonar.software/assets/apidoc/index.html"

async def on_page_context_created(page: Page, context: BrowserContext, **_):
    """Login to the site once the page is ready."""
    await page.goto(LOGIN_URL, wait_until="domcontentloaded")
    await page.fill("input[name='username']", SONAR_USERNAME)
    await page.fill("input[name='password']", SONAR_PASSWORD)
    await page.click("button[type='submit']")
    await page.wait_for_load_state("networkidle")
    # Save storage state in the profile folder as backup
    storage_path = os.path.join(profile_path, "storage_state.json")
    await context.storage_state(path=storage_path)
    return page

async def main():
    logger = AsyncLogger(verbose=True)
    profiler = BrowserProfiler(logger=logger)
    global profile_path
    profile_path = profiler.get_profile_path(PROFILE_NAME) or os.path.join(profiler.profiles_dir, PROFILE_NAME)
    os.makedirs(profile_path, exist_ok=True)

    browser_config = BrowserConfig(
        headless=False,
        use_managed_browser=True,
        user_data_dir=profile_path,
        use_persistent_context=True,
        verbose=True,
    )

    async with AsyncWebCrawler(config=browser_config, logger=logger) as crawler:
        crawler.crawler_strategy.set_hook("on_page_context_created", on_page_context_created)
        await crawler.arun(TARGET_URL)

    logger.success(f"Profile saved at: {profile_path}", tag="PROFILE")

if __name__ == "__main__":
    asyncio.run(main())
