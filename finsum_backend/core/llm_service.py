import os
import json
import random
# from openai import OpenAI # 这才是 OpenAI 的实际导入语句

# 尝试获取 API 密钥（尽管在模拟版本中不会使用）
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
# print("警告：未设置 OPENAI_API_KEY 环境变量。LLM 调用将被模拟。")
# client = None
# else:
# client = OpenAI(api_key=OPENAI_API_KEY)


def get_mock_llm_response(news_items: list, market_data: dict) -> dict:
    """
    根据输入数据生成模拟的 LLM 响应，并遵循 PRD 的 JSON 结构。
    """
    sentiments = ["乐观", "悲观", "中性", "复杂"]
    chosen_sentiment = random.choice(sentiments)

    executive_summary = "今日市场活动显著，各板块走势分化。"
    if market_data:
        sp500_change = market_data.get("S&P 500", {}).get("change_percent", "0%")
        nasdaq_change = market_data.get("NASDAQ Composite", {}).get("change_percent", "0%")
        if "N/A" not in sp500_change and "N/A" not in nasdaq_change:
             executive_summary = f"市场呈现{chosen_sentiment.lower()}趋势；标普 500 指数变动 {sp500_change}，纳斯达克指数变动 {nasdaq_change}。"


    sentiment_reason = f"由于今日交易时段和新闻流中观察到的多种因素，市场情绪为{chosen_sentiment.lower()}。"
    if chosen_sentiment == "乐观":
        sentiment_reason = "积极的经济指标和关键行业强劲的企业盈利促成了乐观的前景。"
    elif chosen_sentiment == "悲观":
        sentiment_reason = "对通货膨胀和潜在加息的担忧导致投资者情绪悲观。"
    elif chosen_sentiment == "中性":
        sentiment_reason = "市场没有明确的方向，一些行业的上涨被其他行业的下跌所抵消，导致了中性的立场。"
    elif chosen_sentiment == "复杂":
        sentiment_reason = "由于积极的科技股表现与更广泛的市场不确定性形成对比，市场情绪复杂。"

    top_stories_mock = []
    if news_items:
        # 为模拟摘要选择最多 3 个新闻条目
        selected_news = news_items[:3]
        for i, news_item in enumerate(selected_news):
            top_stories_mock.append({
                "title": news_item.get("title", f"示例新闻标题 {i+1}"),
                "summary": f"这是针对“{news_item.get('title', '此新闻条目')}”的模拟 LLM 摘要。它突出了关键方面和潜在的市场影响。内容是为测试目的生成的。",
                "url": news_item.get("url", "#"),
                "source": news_item.get("source", "MockSource")
            })
    else: # 如果没有新闻条目则回退
        for i in range(3):
            top_stories_mock.append({
                "title": f"占位新闻标题 {i+1}",
                "summary": "这是一个占位摘要，因为没有向 LLM 提供特定的新闻条目。",
                "url": "#",
                "source": "PlaceholderSource"
            })


    return {
        "executive_summary": executive_summary,
        "market_sentiment": {
            "sentiment": chosen_sentiment,
            "reason": sentiment_reason
        },
        "top_stories": top_stories_mock
    }

async def generate_summary_from_llm(news_items: list, market_data: dict) -> dict:
    """
    生成市场摘要。目前使用模拟响应。
    构建提示（用于将来实际的 LLM 调用）并期望 JSON 响应。
    """
    print("正在尝试从 LLM 生成摘要（当前为模拟）...")

    # 根据 PRD F3 构建提示（对将来实际实现有用）
    prompt_content = f"""
    分析以下金融市场数据和新闻条目。
    以 JSON 格式提供简洁、数据驱动的摘要。

    市场数据:
    {json.dumps(market_data, indent=2)}

    新闻条目（提供前 10 条，选择并总结影响最大的 3 条）:
    {json.dumps(news_items, indent=2)}

    说明:
    1.  "executive_summary": 一个高度浓缩的句子，总结当天的市场活动和整体基调。
    2.  "market_sentiment":
        *   "sentiment": 选择一个："乐观"、"悲观"、"中性"、"复杂"。
        *   "reason": 简要解释驱动这种情绪的因素，如果适用，请参考市场数据或新闻。
    3.  "top_stories": 一个包含正好 3 个对象的数组，每个对象代表一个关键新闻报道。对于每个报道：
        *   "title": 新闻报道的原始标题。
        *   "summary": 您对新闻报道及其潜在市场影响的简洁摘要（2-3 句话）。
        *   "url": 新闻报道的原始 URL。
        *   "source": 新闻的原始来源（例如，“路透社”、“雅虎财经”）。

    仅返回 JSON 对象，不含其他文本或解释。
    JSON 结构必须是:
    {{
      "executive_summary": "string",
      "market_sentiment": {{
        "sentiment": "string",
        "reason": "string"
      }},
      "top_stories": [
        {{
          "title": "string",
          "summary": "string",
          "url": "string",
          "source": "string"
        }}
      ]
    }}
    """

    # if client:
    #     try:
    #         print("正在对 OpenAI API 进行实际调用...") # 如果 client 为 None，则此部分不会运行
    #         response = await client.chat.completions.create( # 如果可用，则对异步客户端使用 await，否则使用同步
    #             model="gpt-3.5-turbo-0125", # 或您首选的支持 JSON 模式的模型
    #             messages=[{"role": "system", "content": "你是一个财经新闻摘要器。以 JSON 格式回应。"},
    #                       {"role": "user", "content": prompt_content}],
    #             response_format={"type": "json_object"}
    #         )
    #         llm_output_json_str = response.choices[0].message.content
    #         print("已收到来自 OpenAI API 的响应。")
    #     except Exception as e:
    #         print(f"调用 OpenAI API 时出错：{e}")
    #         print("由于 API 错误，将回退到模拟的 LLM 响应。")
    #         llm_output_json_str = json.dumps(get_mock_llm_response(news_items, market_data))
    # else:
    #     # 如果 API 密钥不可用或客户端未初始化，则进行模拟的 LLM 调用
    #     print("正在使用模拟的 LLM 响应。")
    llm_output_json_str = json.dumps(get_mock_llm_response(news_items, market_data))

    try:
        parsed_response = json.loads(llm_output_json_str)
        # 根据 PRD 结构进行基本验证
        if not all(key in parsed_response for key in ["executive_summary", "market_sentiment", "top_stories"]):
            raise ValueError("LLM 响应缺少一个或多个主要密钥。")
        if not isinstance(parsed_response["market_sentiment"], dict) or \
           not all(key in parsed_response["market_sentiment"] for key in ["sentiment", "reason"]):
             raise ValueError("LLM 响应缺少 market_sentiment 密钥。")
        if not isinstance(parsed_response["top_stories"], list):
            raise ValueError("LLM 响应 'top_stories' 不是列表。")
        # 如果需要，可以为每个报道项目添加更多验证。

        print("LLM 响应已成功解析和验证。")
        return parsed_response
    except json.JSONDecodeError as e:
        print(f"严重：解码 LLM JSON 响应时出错：{e}。响应为：{llm_output_json_str}")
        raise ValueError(f"LLM 返回了格式错误的 JSON。内容：{llm_output_json_str[:500]}...") # 显示部分内容
    except ValueError as e:
        print(f"严重：LLM 响应验证错误：{e}。响应为：{llm_output_json_str}")
        raise # 重新引发 ValueError 以供调用者处理


if __name__ == '__main__':
    # 示例用法（用于直接测试此模块）
    async def main_test():
        print("\n--- 测试 LLM 服务（模拟）---")
        sample_news = [
            {"title": "科技股在人工智能热潮中持续上涨", "url": "https://example.com/news_tech_rally", "source": "雅虎财经"},
            {"title": "美联储暗示今年晚些时候降息", "url": "https://example.com/news_fed_rates", "source": "路透社"},
            {"title": "油价因供应担忧上涨", "url": "https://example.com/news_oil_prices", "source": "路透社"},
            {"title": "零售销售额意外放缓", "url": "https://example.com/news_retail_slowdown", "source": "雅虎财经"},
        ]
        sample_market_data = {
            "S&P 500": {"price": "5450.20", "change": "+25.80", "change_percent": "+0.48%"},
            "NASDAQ Composite": {"price": "17800.90", "change": "+150.10", "change_percent": "+0.85%"},
        }

        print("\n测试用例 1：包含新闻和市场数据")
        try:
            summary = await generate_summary_from_llm(sample_news, sample_market_data)
            print("生成的摘要（测试用例 1）：")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        except ValueError as e:
            print(f"测试用例 1 出错：{e}")

        print("\n测试用例 2：包含空新闻和市场数据")
        try:
            summary_empty = await generate_summary_from_llm([], {})
            print("生成的摘要（测试用例 2）：")
            print(json.dumps(summary_empty, indent=2, ensure_ascii=False))
        except ValueError as e:
            print(f"测试用例 2 出错：{e}")

        print("\n测试用例 3：包含新闻和 N/A 市场数据")
        sample_market_data_na = {
            "S&P 500": {"price": "N/A", "change": "N/A", "change_percent": "N/A"},
            "NASDAQ Composite": {"price": "N/A", "change": "N/A", "change_percent": "N/A"},
        }
        try:
            summary_na_market = await generate_summary_from_llm(sample_news, sample_market_data_na)
            print("生成的摘要（测试用例 3）：")
            print(json.dumps(summary_na_market, indent=2, ensure_ascii=False))
        except ValueError as e:
            print(f"测试用例 3 出错：{e}")


    import asyncio
    asyncio.run(main_test())
