# Sonar API Docs Profile Setup

This guide shows how to create a persistent browser profile for the Sonar API documentation using Crawl4AI.

1. **Create a `.env` file** with your login credentials:

```bash
SONAR_USERNAME=your_username
SONAR_PASSWORD=your_password
```

2. **Run the profile creator script**:

```bash
python docs/examples/sonar_profile_creator.py
```

The script logs into `https://alamobb.sonar.software` and saves a profile named `sonar_profile` under `~/.crawl4ai/profiles/`.

3. **Reuse the profile** when crawling protected pages:

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

browser_config = BrowserConfig(
    headless=True,
    use_managed_browser=True,
    user_data_dir="~/.crawl4ai/profiles/sonar_profile",
    use_persistent_context=True,
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun("https://alamobb.sonar.software/assets/apidoc/index.html")
    print("Markdown length:", len(result.markdown.raw_markdown))
```

After the initial run, the session data is preserved in the profile so you will not need to log in again.
