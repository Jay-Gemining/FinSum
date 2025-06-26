import httpx
from bs4 import BeautifulSoup
import asyncio
import re

# Common headers to mimic a browser
COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

async def fetch_url_content(client: httpx.AsyncClient, url: str) -> str | None:
    """Helper function to fetch URL content with error handling."""
    try:
        response = await client.get(url, headers=COMMON_HEADERS, timeout=10.0, follow_redirects=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except httpx.RequestError as e:
        print(f"Error fetching {url}: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching {url}: {e.response.status_code} - {e.response.text[:200]}")
    return None

async def scrape_reuters_financial_news(client: httpx.AsyncClient) -> list[dict]:
    """Scrapes financial news from Reuters."""
    # Reuters URL for business/finance news. This might change.
    # Using a more general finance news page if available or a top news page.
    # For the sake of example, let's assume a general "business" section.
    # url = "https://www.reuters.com/business/finance/" # This specific URL might not have easily scrapable headlines
    url = "https://www.reuters.com/world/" # Using a more general top news, often includes finance
    # A more specific category might be better if available and stable.
    # Example: url = "https://www.reuters.com/news/archive/businessnews" (archive pages can be more stable)

    print(f"Scraping Reuters: {url}")
    content = await fetch_url_content(client, url)
    if not content:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    news_items = []

    # Selectors are highly volatile. These are examples and will likely need adjustment.
    # Attempt 1: Common structure for story cards
    # Note: Reuters uses dynamic class names often. This is a best-effort.
    # Looking for article links within list items or specific card-like elements.
    # This is a very generic selector, might need to be much more specific.
    # It's common for Reuters to have links like "/world/asia-pacific/some-news-title-date/"

    # Try to find a container for news items first
    # Common patterns: <section>, <ul class="news-list">, <div class="grid"> etc.
    # For Reuters, let's try to find elements with 'data-testid' attributes which can be more stable.
    # Example: <a data-testid="Heading" href="..."><h2>Title</h2></a>
    # Or: <div data-testid="StoryCard"> ... <a data-testid="Link"> ... <span data-testid="Title">Title</span> ... </a> ... </div>

    # Simplified approach: find <a> tags with hrefs that look like article links
    # and have some text content. This is very broad.
    # We'll try to find links that look like article URLs and have meaningful text.

    # Trying to find <a> tags with hrefs and some text, then filter by URL structure
    # This is a very broad selector and will need refinement based on actual Reuters structure.
    links = soup.find_all('a', href=True, limit=20) # Limit to reduce noise

    for link in links:
        href = link['href']
        title_element = link.find('h2') or link.find('h3') or link.find('span') # Common title tags within links
        title_text = ""

        if title_element:
            title_text = title_element.get_text(strip=True)
        elif len(link.get_text(strip=True)) > 30 : # If no specific title tag, take link text if long enough
             title_text = link.get_text(strip=True)


        if title_text and href.startswith('/') and not href.startswith('//') and len(title_text) > 20: # Basic filter
            full_url = f"https://www.reuters.com{href}"
            if not any(item['url'] == full_url for item in news_items): # Avoid duplicates
                 news_items.append({"title": title_text, "url": full_url, "source": "Reuters"})
            if len(news_items) >= 5: # Limit to 5 news items from Reuters
                break

    print(f"Found {len(news_items)} news items from Reuters.")
    return news_items


async def scrape_yahoo_finance_homepage(client: httpx.AsyncClient) -> list[dict]:
    """Scrapes news from Yahoo Finance homepage."""
    url = "https://finance.yahoo.com/"
    print(f"Scraping Yahoo Finance: {url}")
    content = await fetch_url_content(client, url)
    if not content:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    news_items = []

    # Yahoo Finance selectors. These are also highly volatile.
    # Common structure for news items on Yahoo Finance might be within <li> tags or specific divs.
    # Example: <li class="..."><a href="..."><h3 class="...">Title</h3></a></li>
    # Or: <a href="..."><h2 class="...">Title</h2></a>

    # Attempt to find news headlines, typically in <a> tags with class or within <h3>
    # Yahoo often has a stream of news items in list format
    # Look for links with 'data-test-id="mega-item-header-link"' or similar test IDs
    # Or links within list items (e.g., <li class="js-stream-content Pos(r)">)

    # A common pattern is an <a> tag with an <h3> inside it for the title.
    links = soup.find_all('a', href=True, limit=30) # Limit to reduce noise and processing

    for link in links:
        href = link['href']
        title = ""

        # Try to find a common title element (h3, h2) within the link
        h_tag = link.find(['h3', 'h2'])
        if h_tag:
            title = h_tag.get_text(strip=True)
        elif len(link.get_text(strip=True)) > 30 and not link.find_parents(['nav', 'footer']): # Fallback to link text if long enough and not in nav/footer
            title = link.get_text(strip=True)

        # Filter for valid news links (heuristic)
        if title and href.startswith('/') and not href.startswith('//') and "news/" in href and not href.endswith(".html"):
            # Yahoo Finance links are often relative, like /news/some-article-123456789.html
            # Sometimes they are fully qualified, sometimes they are just paths
            # The PRD asks for Yahoo Finance homepage, so internal links are expected.
            # The ".html" part is often present, but sometimes not.
             full_url = href if href.startswith('https://') else f"https://finance.yahoo.com{href}"
             if not any(item['url'] == full_url for item in news_items): # Avoid duplicates
                 news_items.append({"title": title, "url": full_url, "source": "Yahoo Finance"})
             if len(news_items) >= 5: # Limit to 5 news items from Yahoo Finance
                break

    print(f"Found {len(news_items)} news items from Yahoo Finance.")
    return news_items


async def scrape_news() -> list[dict]:
    """
    Scrapes news from Reuters and Yahoo Finance.
    Returns a list of dictionaries, each with "title", "url", and "source".
    """
    news_items = []
    async with httpx.AsyncClient() as client:
        # Run scrapers concurrently
        results = await asyncio.gather(
            scrape_reuters_financial_news(client),
            scrape_yahoo_finance_homepage(client)
        )
        for result_list in results:
            news_items.extend(result_list)

    # Simple de-duplication based on URL (though already handled within scrapers)
    # And limit total news items if necessary (e.g., to top 10 overall before LLM processing)
    unique_news = {item['url']: item for item in news_items}.values()
    print(f"Total unique news items scraped: {len(unique_news)}")
    return list(unique_news)[:10] # Return up to 10 unique news items


async def get_market_data() -> dict:
    """
    Fetches market data for S&P 500 and NASDAQ Composite from Yahoo Finance.
    Returns a dictionary with keys "S&P 500" and "NASDAQ Composite".
    Each key has a sub-dictionary with "price", "change", "change_percent".
    """
    print("Fetching market data from Yahoo Finance...")
    indices_to_fetch = {
        "S&P 500": {"ticker": "^GSPC", "name": "S&P 500"},
        "NASDAQ Composite": {"ticker": "^IXIC", "name": "NASDAQ Composite"}
    }
    market_data_results = {}

    async with httpx.AsyncClient() as client:
        for key_name, data in indices_to_fetch.items():
            url = f"https://finance.yahoo.com/quote/{data['ticker']}"
            print(f"Fetching data for {data['name']} from {url}")
            content = await fetch_url_content(client, url)
            if not content:
                market_data_results[key_name] = {"price": "N/A", "change": "N/A", "change_percent": "N/A"}
                continue

            soup = BeautifulSoup(content, 'html.parser')

            try:
                # Yahoo Finance uses specific data attributes for these values.
                # These selectors are specific and might break.
                # Example: <fin-streamer data-symbol="^GSPC" data-field="regularMarketPrice" ...>PRICE</fin-streamer>
                # Example: <fin-streamer data-symbol="^GSPC" data-field="regularMarketChange" ...>CHANGE</fin-streamer>
                # Example: <fin-streamer data-symbol="^GSPC" data-field="regularMarketChangePercent" ...>CHANGE_PERCENT</fin-streamer>

                price_selector = f'fin-streamer[data-symbol="{data["ticker"]}"][data-field="regularMarketPrice"]'
                change_selector = f'fin-streamer[data-symbol="{data["ticker"]}"][data-field="regularMarketChange"]'
                change_percent_selector = f'fin-streamer[data-symbol="{data["ticker"]}"][data-field="regularMarketChangePercent"]'

                price_el = soup.select_one(price_selector)
                change_el = soup.select_one(change_selector)
                change_percent_el = soup.select_one(change_percent_selector)

                price = price_el.get_text(strip=True) if price_el else "N/A"
                change_raw = change_el.get_text(strip=True) if change_el else "N/A"
                change_percent_raw = change_percent_el.get_text(strip=True) if change_percent_el else "N/A"

                # The change_percent often comes in parentheses, e.g., "(+0.25%)". Remove them.
                change_percent = change_percent_raw.strip('()')

                market_data_results[key_name] = {
                    "price": price,
                    "change": change_raw, # Already includes + or -
                    "change_percent": change_percent
                }
                print(f"Successfully parsed data for {data['name']}: {market_data_results[key_name]}")

            except Exception as e:
                print(f"Error parsing data for {data['name']}: {e}")
                market_data_results[key_name] = {"price": "N/A", "change": "N/A", "change_percent": "N/A (parse error)"}

    if not market_data_results.get("S&P 500"):
         market_data_results["S&P 500"] = {"price": "N/A", "change": "N/A", "change_percent": "N/A (not found)"}
    if not market_data_results.get("NASDAQ Composite"):
         market_data_results["NASDAQ Composite"] = {"price": "N/A", "change": "N/A", "change_percent": "N/A (not found)"}


    print(f"Market data fetched: {market_data_results}")
    return market_data_results


if __name__ == '__main__':
    async def test_scraper():
        print("--- Testing News Scraper ---")
        news = await scrape_news()
        if news:
            for item in news:
                print(f"  Title: {item['title']}")
                print(f"  URL: {item['url']}")
                print(f"  Source: {item['source']}\n")
        else:
            print("  No news items found.")

        print("\n--- Testing Market Data Scraper ---")
        market_data = await get_market_data()
        if market_data:
            for index, data in market_data.items():
                print(f"  {index}: Price: {data['price']}, Change: {data['change']}, Percent: {data['change_percent']}")
        else:
            print("  No market data found.")

    asyncio.run(test_scraper())
