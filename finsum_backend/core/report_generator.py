import datetime
import json
import asyncio # 测试块必需

from .scraper import scrape_news, get_market_data
from .llm_service import generate_summary_from_llm

async def generate_report_data() -> dict:
    """
    协调从爬虫获取数据、从 LLM 服务获取 AI 分析，
    并根据 PRD 规范构建最终报告。
    """
    print("正在启动报告生成序列...")

    # 步骤 1：并发获取数据
    print("正在获取新闻和市场数据...")
    try:
        news_items, market_data_raw = await asyncio.gather(
            scrape_news(),
            get_market_data()
        )
        print(f"成功获取 {len(news_items)} 条新闻。")
        print(f"成功获取市场数据：{', '.join(market_data_raw.keys())}")
    except Exception as e:
        print(f"数据抓取过程中发生严重错误：{e}")
        # 根据 main.py 中期望的处理方式，返回最小错误结构或引发错误
        # 目前，我们构建一个指示此阶段失败的报告。
        return {
            "report_date": datetime.date.today().strftime("%B %d, %Y"),
            "executive_summary": "由于数据抓取错误，未能生成报告。",
            "market_sentiment": {"sentiment": "错误", "reason": f"抓取失败：{e}"},
            "key_indices": {},
            "top_stories": []
        }

    # 步骤 2：获取 AI 生成的摘要和分析
    print("正在使用 LLM 服务处理数据...")
    try:
        # llm_analysis 预期包含：executive_summary、market_sentiment、top_stories
        llm_analysis = await generate_summary_from_llm(news_items, market_data_raw)
        print("LLM 处理完成。")
    except Exception as e:
        print(f"LLM 处理过程中发生严重错误：{e}")
        # 构建一个指示此阶段失败的报告，但如果可用，则包含抓取的数据
        return {
            "report_date": datetime.date.today().strftime("%B %d, %Y"),
            "executive_summary": "由于 AI 分析错误，未能生成报告。",
            "market_sentiment": {"sentiment": "错误", "reason": f"LLM 处理失败：{e}"},
            "key_indices": market_data_raw, # 如果 LLM 失败，则返回原始市场数据
            "top_stories": [ # 如果 LLM 未能总结，则可能包含原始新闻标题
                {"title": news.get("title", "原始新闻条目"), "summary": "AI 摘要不可用。", "url": news.get("url", "#"), "source": news.get("source", "未知")}
                for news in news_items[:3] # 显示前 3 条原始新闻条目
            ]
        }

    # 步骤 3：根据 PRD 构建最终报告
    # PRD 中的“报告结构”指定了这 4 个主要部分：
    # 1. 一句话摘要（执行摘要）
    # 2. 市场情绪和原因
    # 3. 主要指数（名称、价格、变动金额、变动百分比）
    # 4. 头条新闻前 3 条（标题、LLM 摘要、原始链接）

    final_report = {
        "report_date": datetime.date.today().strftime("%B %d, %Y"), # 根据页眉组件规范

        "executive_summary": llm_analysis.get("executive_summary", "执行摘要不可用。"),

        "market_sentiment": {
            "sentiment": llm_analysis.get("market_sentiment", {}).get("sentiment", "未知"),
            "reason": llm_analysis.get("market_sentiment", {}).get("reason", "原因不可用。")
        },

        # key_indices 应直接来自爬虫，因为 LLM 不应修改它。
        # 爬虫已将其格式化为：{"S&P 500": {"price": ..., "change": ..., "change_percent": ...}, ...}
        "key_indices": market_data_raw if market_data_raw else {
            "S&P 500": {"price": "N/A", "change": "N/A", "change_percent": "N/A"},
            "NASDAQ Composite": {"price": "N/A", "change": "N/A", "change_percent": "N/A"}
        },

        # top_stories 由 LLM 生成。
        # 确保它是一个列表，并且每个报道都具有必需的字段。
        "top_stories": []
    }

    raw_llm_stories = llm_analysis.get("top_stories", [])
    if isinstance(raw_llm_stories, list):
        for story_data in raw_llm_stories[:3]: # 确保只取前 3 条
            final_report["top_stories"].append({
                "title": story_data.get("title", "标题不可用"),
                "summary": story_data.get("summary", "摘要不可用。"),
                "url": story_data.get("url", "#"), # 如果缺少 URL，则默认为“#”
                "source": story_data.get("source", "来源不可用")
            })

    # 如果 LLM 提供的报道少于 3 条，则仅包含提供的内容。
    # 如果 LLM 提供的报道多于 3 条，则截断为 3 条。

    print("报告数据已成功构建。")
    return final_report

if __name__ == '__main__':
    # 更全面的 report_generator.py 测试
    async def main_test_report_generator():
        print("\n--- 测试报告生成器 ---")

        # 如果需要，可以模拟爬虫和 llm_service 以进行隔离测试，
        # 但这里我们将调用实际的（模拟的）依赖项。

        print("\n测试用例：成功生成")
        report = await generate_report_data()
        print("\n最终报告（成功案例）：")
        print(json.dumps(report, indent=2, ensure_ascii=False))

        # 要测试错误条件，理想情况下，您应该模拟依赖项以引发错误。
        # 例如，模拟 core.scraper.scrape_news 以引发异常。
        # 如果没有像 unittest.mock 或 pytest 的 monkeypatch 这样的模拟库，这很难做到。

        # 通过临时破坏依赖项来模拟爬虫错误（概念上）
        # 这仅用于说明；不建议直接修改进行测试。
        # _original_scrape_news = core.scraper.scrape_news
        # async def mock_scrape_news_error():
        #     raise ConnectionError("模拟的爬虫连接错误")
        # core.scraper.scrape_news = mock_scrape_news_error
        # print("\n测试用例：爬虫故障（概念性 - 需要实际模拟）")
        # report_scraper_fail = await generate_report_data()
        # print("\n最终报告（爬虫故障案例）：")
        # print(json.dumps(report_scraper_fail, indent=2, ensure_ascii=False))
        # core.scraper.scrape_news = _original_scrape_news # 恢复

    asyncio.run(main_test_report_generator())
