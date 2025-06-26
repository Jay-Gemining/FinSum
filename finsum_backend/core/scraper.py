import httpx
from bs4 import BeautifulSoup
import asyncio
import re

# 模拟浏览器的通用请求头
COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

async def fetch_url_content(client: httpx.AsyncClient, url: str) -> str | None:
    """辅助函数，用于获取 URL 内容并处理错误。"""
    try:
        response = await client.get(url, headers=COMMON_HEADERS, timeout=10.0, follow_redirects=True)
        response.raise_for_status()  # 针对 HTTP 错误引发异常
        return response.text
    except httpx.RequestError as e:
        print(f"获取 {url} 时出错：{e}")
    except httpx.HTTPStatusError as e:
        print(f"获取 {url} 时发生 HTTP 错误：{e.response.status_code} - {e.response.text[:200]}")
    return None

async def scrape_reuters_financial_news(client: httpx.AsyncClient) -> list[dict]:
    """从路透社抓取财经新闻。"""
    # 路透社商业/财经新闻的 URL。这可能会改变。
    # 如果有更通用的财经新闻页面，则使用该页面，否则使用头条新闻页面。
    # 为举例起见，我们假设一个通用的“商业”版块。
    # url = "https://www.reuters.com/business/finance/" # 这个特定的 URL 可能没有易于抓取的标题
    url = "https://www.reuters.com/world/" # 使用更通用的头条新闻，通常包括财经新闻
    # 如果有更具体且稳定的类别，可能会更好。
    # 示例：url = "https://www.reuters.com/news/archive/businessnews" （存档页面可能更稳定）

    print(f"正在抓取路透社：{url}")
    content = await fetch_url_content(client, url)
    if not content:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    news_items = []

    # 选择器非常不稳定。这些是示例，很可能需要调整。
    # 尝试 1：报道卡片的通用结构
    # 注意：路透社经常使用动态类名。这是尽力而为的做法。
    # 在列表项或特定卡片式元素中查找文章链接。
    # 这是一个非常通用的选择器，可能需要更具体。
    # 路透社通常有类似 "/world/asia-pacific/some-news-title-date/" 的链接

    # 首先尝试找到新闻条目的容器
    # 常见模式：<section>、<ul class="news-list">、<div class="grid"> 等。
    # 对于路透社，我们尝试查找具有“data-testid”属性的元素，这些属性可能更稳定。
    # 示例：<a data-testid="Heading" href="..."><h2>标题</h2></a>
    # 或：<div data-testid="StoryCard"> ... <a data-testid="Link"> ... <span data-testid="Title">标题</span> ... </a> ... </div>

    # 简化方法：查找具有 href 且看起来像文章链接并包含一些文本内容的 <a> 标签。这非常宽泛。
    # 我们将尝试查找看起来像文章 URL 且具有有意义文本的链接。

    # 尝试查找具有 href 和一些文本的 <a> 标签，然后按 URL 结构进行筛选
    # 这是一个非常宽泛的选择器，需要根据路透社的实际结构进行细化。
    links = soup.find_all('a', href=True, limit=20) # 限制数量以减少噪音

    for link in links:
        href = link['href']
        title_element = link.find('h2') or link.find('h3') or link.find('span') # 链接中常见的标题标签
        title_text = ""

        if title_element:
            title_text = title_element.get_text(strip=True)
        elif len(link.get_text(strip=True)) > 30 : # 如果没有特定的标题标签，并且链接文本足够长，则使用链接文本
             title_text = link.get_text(strip=True)


        if title_text and href.startswith('/') and not href.startswith('//') and len(title_text) > 20: # 基本筛选
            full_url = f"https://www.reuters.com{href}"
            if not any(item['url'] == full_url for item in news_items): # 避免重复
                 news_items.append({"title": title_text, "url": full_url, "source": "Reuters"})
            if len(news_items) >= 5: # 限制从路透社获取 5 条新闻
                break

    print(f"从路透社找到 {len(news_items)} 条新闻。")
    return news_items


async def scrape_yahoo_finance_homepage(client: httpx.AsyncClient) -> list[dict]:
    """从雅虎财经主页抓取新闻。"""
    url = "https://finance.yahoo.com/"
    print(f"正在抓取雅虎财经：{url}")
    content = await fetch_url_content(client, url)
    if not content:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    news_items = []

    # 雅虎财经选择器。这些也非常不稳定。
    # 雅虎财经上新闻条目的常见结构可能在 <li> 标签或特定的 div 中。
    # 示例：<li class="..."><a href="..."><h3 class="...">标题</h3></a></li>
    # 或：<a href="..."><h2 class="...">标题</h2></a>

    # 尝试查找新闻标题，通常在具有类名的 <a> 标签中或在 <h3> 中
    # 雅虎通常以列表格式显示新闻流
    # 查找具有“data-test-id="mega-item-header-link"”或类似测试 ID 的链接
    # 或列表项中的链接（例如，<li class="js-stream-content Pos(r)">）

    # 一种常见的模式是在 <a> 标签内部有一个 <h3> 用于标题。
    links = soup.find_all('a', href=True, limit=30) # 限制数量以减少噪音和处理量

    for link in links:
        href = link['href']
        title = ""

        # 尝试在链接中查找常见的标题元素（h3、h2）
        h_tag = link.find(['h3', 'h2'])
        if h_tag:
            title = h_tag.get_text(strip=True)
        elif len(link.get_text(strip=True)) > 30 and not link.find_parents(['nav', 'footer']): # 如果链接文本足够长且不在导航栏/页脚中，则回退到链接文本
            title = link.get_text(strip=True)

        # 筛选有效的新闻链接（启发式）
        if title and href.startswith('/') and not href.startswith('//') and "news/" in href and not href.endswith(".html"):
            # 雅虎财经链接通常是相对的，例如 /news/some-article-123456789.html
            # 有时它们是完全限定的，有时它们只是路径
            # PRD 要求雅虎财经主页，因此预期会有内部链接。
            # ".html" 部分通常存在，但有时不存在。
             full_url = href if href.startswith('https://') else f"https://finance.yahoo.com{href}"
             if not any(item['url'] == full_url for item in news_items): # 避免重复
                 news_items.append({"title": title, "url": full_url, "source": "Yahoo Finance"})
             if len(news_items) >= 5: # 限制从雅虎财经获取 5 条新闻
                break

    print(f"从雅虎财经找到 {len(news_items)} 条新闻。")
    return news_items


async def scrape_news() -> list[dict]:
    """
    从路透社和雅虎财经抓取新闻。
    返回一个字典列表，每个字典包含“title”、“url”和“source”。
    """
    news_items = []
    async with httpx.AsyncClient() as client:
        # 并发运行爬虫
        results = await asyncio.gather(
            scrape_reuters_financial_news(client),
            scrape_yahoo_finance_homepage(client)
        )
        for result_list in results:
            news_items.extend(result_list)

    # 基于 URL 的简单去重（尽管在爬虫内部已处理）
    # 并在必要时限制新闻总数（例如，在 LLM 处理前限制为总体前 10 条）
    unique_news = {item['url']: item for item in news_items}.values()
    print(f"抓取到的独立新闻条目总数：{len(unique_news)}")
    return list(unique_news)[:10] # 最多返回 10 条独立新闻条目


async def get_market_data() -> dict:
    """
    从雅虎财经获取标普 500 指数和纳斯达克综合指数的市场数据。
    返回一个字典，键为“S&P 500”和“NASDAQ Composite”。
    每个键都有一个子字典，包含“price”、“change”、“change_percent”。
    """
    print("正在从雅虎财经获取市场数据...")
    indices_to_fetch = {
        "S&P 500": {"ticker": "^GSPC", "name": "S&P 500"},
        "NASDAQ Composite": {"ticker": "^IXIC", "name": "NASDAQ Composite"}
    }
    market_data_results = {}

    async with httpx.AsyncClient() as client:
        for key_name, data in indices_to_fetch.items():
            url = f"https://finance.yahoo.com/quote/{data['ticker']}"
            print(f"正在从 {url} 获取 {data['name']} 的数据")
            content = await fetch_url_content(client, url)
            if not content:
                market_data_results[key_name] = {"price": "N/A", "change": "N/A", "change_percent": "N/A"}
                continue

            soup = BeautifulSoup(content, 'html.parser')

            try:
                # 雅虎财经对这些值使用特定的数据属性。
                # 这些选择器是特定的，可能会失效。
                # 示例：<fin-streamer data-symbol="^GSPC" data-field="regularMarketPrice" ...>价格</fin-streamer>
                # 示例：<fin-streamer data-symbol="^GSPC" data-field="regularMarketChange" ...>变动</fin-streamer>
                # 示例：<fin-streamer data-symbol="^GSPC" data-field="regularMarketChangePercent" ...>变动百分比</fin-streamer>

                price_selector = f'fin-streamer[data-symbol="{data["ticker"]}"][data-field="regularMarketPrice"]'
                change_selector = f'fin-streamer[data-symbol="{data["ticker"]}"][data-field="regularMarketChange"]'
                change_percent_selector = f'fin-streamer[data-symbol="{data["ticker"]}"][data-field="regularMarketChangePercent"]'

                price_el = soup.select_one(price_selector)
                change_el = soup.select_one(change_selector)
                change_percent_el = soup.select_one(change_percent_selector)

                price = price_el.get_text(strip=True) if price_el else "N/A"
                change_raw = change_el.get_text(strip=True) if change_el else "N/A"
                change_percent_raw = change_percent_el.get_text(strip=True) if change_percent_el else "N/A"

                # change_percent 通常带有括号，例如“(+0.25%)”。将其删除。
                change_percent = change_percent_raw.strip('()')

                market_data_results[key_name] = {
                    "price": price,
                    "change": change_raw, # 已包含 + 或 -
                    "change_percent": change_percent
                }
                print(f"成功解析 {data['name']} 的数据：{market_data_results[key_name]}")

            except Exception as e:
                print(f"解析 {data['name']} 的数据时出错：{e}")
                market_data_results[key_name] = {"price": "N/A", "change": "N/A", "change_percent": "N/A (解析错误)"}

    if not market_data_results.get("S&P 500"):
         market_data_results["S&P 500"] = {"price": "N/A", "change": "N/A", "change_percent": "N/A (未找到)"}
    if not market_data_results.get("NASDAQ Composite"):
         market_data_results["NASDAQ Composite"] = {"price": "N/A", "change": "N/A", "change_percent": "N/A (未找到)"}


    print(f"获取的市场数据：{market_data_results}")
    return market_data_results


if __name__ == '__main__':
    async def test_scraper():
        print("--- 测试新闻抓取器 ---")
        news = await scrape_news()
        if news:
            for item in news:
                print(f"  标题：{item['title']}")
                print(f"  URL：{item['url']}")
                print(f"  来源：{item['source']}\n")
        else:
            print("  未找到新闻条目。")

        print("\n--- 测试市场数据抓取器 ---")
        market_data = await get_market_data()
        if market_data:
            for index, data in market_data.items():
                print(f"  {index}：价格：{data['price']}，变动：{data['change']}，百分比：{data['change_percent']}")
        else:
            print("  未找到市场数据。")

    asyncio.run(test_scraper())
