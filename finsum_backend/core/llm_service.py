import os
import json
import xml.etree.ElementTree as ET
from openai import OpenAI # 这才是 OpenAI 的实际导入语句

# 尝试获取 API 密钥
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = None
if not OPENAI_API_KEY:
    print("警告：未设置 OPENAI_API_KEY 环境变量。LLM 调用将无法进行。")
else:
    client = OpenAI(api_key=OPENAI_API_KEY)


def xml_to_dict(xml_string: str) -> dict:
    """
    将LLM返回的XML字符串转换为符合前端期望的字典结构。
    """
    root = ET.fromstring(xml_string)

    data = {}

    executive_summary_el = root.find("executive_summary")
    if executive_summary_el is not None:
        data["executive_summary"] = executive_summary_el.text
    else:
        data["executive_summary"] = "执行摘要不可用。"

    market_sentiment_el = root.find("market_sentiment")
    if market_sentiment_el is not None:
        sentiment_el = market_sentiment_el.find("sentiment")
        reason_el = market_sentiment_el.find("reason")
        data["market_sentiment"] = {
            "sentiment": sentiment_el.text if sentiment_el is not None else "未知",
            "reason": reason_el.text if reason_el is not None else "原因不可用。"
        }
    else:
        data["market_sentiment"] = {"sentiment": "未知", "reason": "原因不可用。"}

    top_stories_el = root.find("top_stories")
    stories_list = []
    if top_stories_el is not None:
        for story_el in top_stories_el.findall("story"):
            title_el = story_el.find("title")
            summary_el = story_el.find("summary")
            url_el = story_el.find("url")
            source_el = story_el.find("source")
            stories_list.append({
                "title": title_el.text if title_el is not None else "标题不可用",
                "summary": summary_el.text if summary_el is not None else "摘要不可用。",
                "url": url_el.text if url_el is not None else "#",
                "source": source_el.text if source_el is not None else "来源不可用"
            })
    data["top_stories"] = stories_list
    return data

async def generate_summary_from_llm(news_items: list, market_data: dict) -> dict:
    """
    生成市场摘要。调用真实的 LLM 服务并期望 XML 响应，然后将其转换为 JSON。
    """
    if not client:
        print("错误：OpenAI API 客户端未初始化。请检查 OPENAI_API_KEY 环境变量。")
        # 返回一个表示错误的结构，以便前端可以显示
        return {
            "executive_summary": "LLM 服务配置错误。",
            "market_sentiment": {"sentiment": "错误", "reason": "OpenAI API 客户端未初始化。"},
            "top_stories": []
        }

    print("正在尝试从 LLM 生成摘要...")

    prompt_content = f"""
    请分析以下金融市场数据和新闻条目。
    请以 XML 格式提供简洁、数据驱动的摘要。XML 结构必须如下所示：
    <report>
      <executive_summary>总结当日市场活动和整体基调的一句话。</executive_summary>
      <market_sentiment>
        <sentiment>乐观、悲观、中性或复杂中的一个</sentiment>
        <reason>简要解释驱动这种情绪的因素，可参考市场数据或新闻。</reason>
      </market_sentiment>
      <top_stories>
        <story>
          <title>新闻报道的原始标题</title>
          <summary>对新闻报道及其潜在市场影响的简洁摘要（2-3句话）</summary>
          <url>新闻报道的原始URL</url>
          <source>新闻的原始来源（例如，路透社）</source>
        </story>
        <!-- 最多重复3次 story 元素 -->
      </top_stories>
    </report>

    市场数据:
    {json.dumps(market_data, indent=2)}

    新闻条目 (提供前 10 条，请选择并总结影响最大的 3 条):
    {json.dumps(news_items, indent=2)}

    请仅返回 <report>...</report> XML 结构，不要包含任何其他文本或解释。
    """

    llm_output_xml_str = ""
    try:
        print("正在对 OpenAI API 进行实际调用...")
        # 注意：OpenAI SDK v1.x.x 使用 client.chat.completions.create
        # response_format={"type": "text"} 因为我们要求自定义 XML，而不是 JSON 对象模式。
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", # 或者您偏好的模型
            messages=[
                {"role": "system", "content": "你是一个财经新闻摘要器。请严格按照要求的XML格式回应。"},
                {"role": "user", "content": prompt_content}
            ],
            temperature=0.7, # 可以调整以获得或多或少的创意性回答
        )
        llm_output_xml_str = response.choices[0].message.content
        print("已收到来自 OpenAI API 的响应。")
        # 移除代码块标记 (如果LLM意外添加了)
        llm_output_xml_str = llm_output_xml_str.strip()
        if llm_output_xml_str.startswith("```xml"):
            llm_output_xml_str = llm_output_xml_str[len("```xml"):]
        if llm_output_xml_str.endswith("```"):
            llm_output_xml_str = llm_output_xml_str[:-len("```")]
        llm_output_xml_str = llm_output_xml_str.strip()

    except Exception as e:
        print(f"调用 OpenAI API 时出错：{e}")
        # 在API调用失败时返回错误信息
        return {
            "executive_summary": "调用 LLM API 时出错。",
            "market_sentiment": {"sentiment": "错误", "reason": f"API 调用失败: {e}"},
            "top_stories": []
        }

    try:
        # 将XML转换为字典
        parsed_response_dict = xml_to_dict(llm_output_xml_str)

        # 基本验证 (可以根据xml_to_dict的行为调整)
        if not all(key in parsed_response_dict for key in ["executive_summary", "market_sentiment", "top_stories"]):
            raise ValueError("从XML转换后的字典缺少一个或多个主要密钥。")
        if not isinstance(parsed_response_dict["market_sentiment"], dict) or \
           not all(key in parsed_response_dict["market_sentiment"] for key in ["sentiment", "reason"]):
             raise ValueError("从XML转换后的字典缺少 market_sentiment 密钥。")
        if not isinstance(parsed_response_dict["top_stories"], list):
            raise ValueError("从XML转换后的字典 'top_stories' 不是列表。")

        print("LLM XML响应已成功解析并转换为JSON兼容的字典。")
        return parsed_response_dict
    except ET.ParseError as e:
        print(f"严重：解析 LLM XML 响应时出错：{e}。响应为：\n{llm_output_xml_str}")
        raise ValueError(f"LLM 返回了格式错误的 XML。内容：{llm_output_xml_str[:500]}...")
    except ValueError as e: # 捕捉自定义的验证错误
        print(f"严重：LLM XML 内容验证错误：{e}。XML响应为：\n{llm_output_xml_str}")
        raise # 重新引发 ValueError 以供调用者处理
    except Exception as e: # 捕获其他意外错误
        print(f"严重：处理 LLM 响应时发生未知错误：{e}。XML响应为：\n{llm_output_xml_str}")
        raise ValueError(f"处理 LLM 响应时发生未知错误。")


if __name__ == '__main__':
    # 示例用法（用于直接测试此模块）
    async def main_test():
        if not OPENAI_API_KEY:
            print("未设置 OPENAI_API_KEY，跳过 LLM 服务测试。")
            return

        print("\n--- 测试 LLM 服务 (实际调用) ---")
        sample_news = [
            {"title": "科技股在人工智能热潮中持续上涨", "url": "https://example.com/news_tech_rally", "source": "雅虎财经"},
            {"title": "美联储暗示今年晚些时候降息", "url": "https://example.com/news_fed_rates", "source": "路透社"},
            {"title": "油价因供应担忧上涨", "url": "https://example.com/news_oil_prices", "source": "路透社"},
            # {"title": "零售销售额意外放缓", "url": "https://example.com/news_retail_slowdown", "source": "雅虎财经"},
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
        except Exception as e:
            print(f"测试用例 1 发生意外错误：{e}")

        # print("\n测试用例 2：包含空新闻和市场数据")
        # try:
        #     summary_empty = await generate_summary_from_llm([], {})
        #     print("生成的摘要（测试用例 2）：")
        #     print(json.dumps(summary_empty, indent=2, ensure_ascii=False))
        # except ValueError as e:
        #     print(f"测试用例 2 出错：{e}")


    import asyncio
    asyncio.run(main_test())
