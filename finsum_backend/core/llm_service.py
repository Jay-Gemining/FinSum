import os
import json
import random
# from openai import OpenAI # This would be the actual import for OpenAI

# Attempt to get API key (though it won't be used in the mocked version)
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
# print("Warning: OPENAI_API_KEY environment variable not set. LLM calls will be mocked.")
# client = None
# else:
# client = OpenAI(api_key=OPENAI_API_KEY)


def get_mock_llm_response(news_items: list, market_data: dict) -> dict:
    """
    Generates a mocked LLM response based on input data, adhering to the PRD's JSON structure.
    """
    sentiments = ["Optimistic", "Pessimistic", "Neutral", "Mixed"]
    chosen_sentiment = random.choice(sentiments)

    executive_summary = "Market activity was notable today, with diverse movements across sectors."
    if market_data:
        sp500_change = market_data.get("S&P 500", {}).get("change_percent", "0%")
        nasdaq_change = market_data.get("NASDAQ Composite", {}).get("change_percent", "0%")
        if "N/A" not in sp500_change and "N/A" not in nasdaq_change:
             executive_summary = f"Markets showed {chosen_sentiment.lower()} trends; S&P 500 moved {sp500_change} and NASDAQ {nasdaq_change}."


    sentiment_reason = f"The market sentiment is {chosen_sentiment.lower()} due to a variety of factors observed in today's trading session and news flow."
    if chosen_sentiment == "Optimistic":
        sentiment_reason = "Positive economic indicators and strong corporate earnings in key sectors contributed to an optimistic outlook."
    elif chosen_sentiment == "Pessimistic":
        sentiment_reason = "Concerns over inflation and potential interest rate hikes led to a pessimistic sentiment among investors."
    elif chosen_sentiment == "Neutral":
        sentiment_reason = "The market showed no clear direction, with gains in some sectors offset by losses in others, resulting in a neutral stance."
    elif chosen_sentiment == "Mixed":
        sentiment_reason = "A mixed sentiment prevailed as positive tech performance contrasted with broader market uncertainties."

    top_stories_mock = []
    if news_items:
        # Select up to 3 news items for the mock summary
        selected_news = news_items[:3]
        for i, news_item in enumerate(selected_news):
            top_stories_mock.append({
                "title": news_item.get("title", f"Sample News Title {i+1}"),
                "summary": f"This is a mocked LLM summary for '{news_item.get('title', 'this news item')}'. It highlights key aspects and potential market impact. The content is generated for testing purposes.",
                "url": news_item.get("url", "#"),
                "source": news_item.get("source", "MockSource")
            })
    else: # Fallback if no news items
        for i in range(3):
            top_stories_mock.append({
                "title": f"Placeholder News Title {i+1}",
                "summary": "This is a placeholder summary as no specific news items were provided to the LLM.",
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
    Generates a market summary. Uses a mocked response for now.
    Constructs a prompt (for future real LLM call) and expects a JSON response.
    """
    print("Attempting to generate summary from LLM (currently mocked)...")

    # Constructing the prompt based on PRD F3 (useful for future real implementation)
    prompt_content = f"""
    Analyze the following financial market data and news items.
    Provide a concise, data-driven summary in JSON format.

    Market Data:
    {json.dumps(market_data, indent=2)}

    News Items (Top 10 provided, select and summarize the 3 most impactful):
    {json.dumps(news_items, indent=2)}

    Instructions:
    1.  "executive_summary": A single, highly condensed sentence summarizing the day's market activity and overall tone.
    2.  "market_sentiment":
        *   "sentiment": Choose one: "Optimistic", "Pessimistic", "Neutral", "Mixed".
        *   "reason": Briefly explain the factors driving this sentiment, referencing market data or news if applicable.
    3.  "top_stories": An array of exactly 3 objects, each representing a key news story. For each story:
        *   "title": The original title of the news story.
        *   "summary": Your concise summary of the news story and its potential market impact (2-3 sentences).
        *   "url": The original URL of the news story.
        *   "source": The original source of the news (e.g., "Reuters", "Yahoo Finance").

    Return ONLY the JSON object, with no additional text or explanations.
    The JSON structure MUST be:
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
    #         print("Making actual call to OpenAI API...") # This part won't run if client is None
    #         response = await client.chat.completions.create( # Use await for async client if available, else sync
    #             model="gpt-3.5-turbo-0125", # Or your preferred model that supports JSON mode
    #             messages=[{"role": "system", "content": "You are a financial news summarizer. Respond in JSON format."},
    #                       {"role": "user", "content": prompt_content}],
    #             response_format={"type": "json_object"}
    #         )
    #         llm_output_json_str = response.choices[0].message.content
    #         print("Received response from OpenAI API.")
    #     except Exception as e:
    #         print(f"Error calling OpenAI API: {e}")
    #         print("Falling back to mocked LLM response due to API error.")
    #         llm_output_json_str = json.dumps(get_mock_llm_response(news_items, market_data))
    # else:
    #     # Mocked LLM call if API key is not available or client is not initialized
    #     print("Using mocked LLM response.")
    llm_output_json_str = json.dumps(get_mock_llm_response(news_items, market_data))

    try:
        parsed_response = json.loads(llm_output_json_str)
        # Basic validation against the PRD structure
        if not all(key in parsed_response for key in ["executive_summary", "market_sentiment", "top_stories"]):
            raise ValueError("LLM response missing one or more main keys.")
        if not isinstance(parsed_response["market_sentiment"], dict) or \
           not all(key in parsed_response["market_sentiment"] for key in ["sentiment", "reason"]):
             raise ValueError("LLM response missing market_sentiment keys.")
        if not isinstance(parsed_response["top_stories"], list):
            raise ValueError("LLM response 'top_stories' is not a list.")
        # Could add more validation for each story item if needed.

        print("LLM response parsed and validated successfully.")
        return parsed_response
    except json.JSONDecodeError as e:
        print(f"Critical: Error decoding LLM JSON response: {e}. Response was: {llm_output_json_str}")
        raise ValueError(f"LLM returned malformed JSON. Content: {llm_output_json_str[:500]}...") # Show part of the content
    except ValueError as e:
        print(f"Critical: LLM response validation error: {e}. Response was: {llm_output_json_str}")
        raise # Re-raise the ValueError for the caller to handle


if __name__ == '__main__':
    # Example usage (for testing this module directly)
    async def main_test():
        print("\n--- Testing LLM Service (Mocked) ---")
        sample_news = [
            {"title": "Tech Rally Continues Amidst AI Hype", "url": "https://example.com/news_tech_rally", "source": "Yahoo Finance"},
            {"title": "Fed Hints at Rate Cuts Later This Year", "url": "https://example.com/news_fed_rates", "source": "Reuters"},
            {"title": "Oil Prices Climb on Supply Concerns", "url": "https://example.com/news_oil_prices", "source": "Reuters"},
            {"title": "Retail Sales Show Unexpected Slowdown", "url": "https://example.com/news_retail_slowdown", "source": "Yahoo Finance"},
        ]
        sample_market_data = {
            "S&P 500": {"price": "5450.20", "change": "+25.80", "change_percent": "+0.48%"},
            "NASDAQ Composite": {"price": "17800.90", "change": "+150.10", "change_percent": "+0.85%"},
        }

        print("\nTest Case 1: With news and market data")
        try:
            summary = await generate_summary_from_llm(sample_news, sample_market_data)
            print("Generated Summary (Test Case 1):")
            print(json.dumps(summary, indent=2))
        except ValueError as e:
            print(f"Error in Test Case 1: {e}")

        print("\nTest Case 2: With empty news and market data")
        try:
            summary_empty = await generate_summary_from_llm([], {})
            print("Generated Summary (Test Case 2):")
            print(json.dumps(summary_empty, indent=2))
        except ValueError as e:
            print(f"Error in Test Case 2: {e}")

        print("\nTest Case 3: With news and N/A market data")
        sample_market_data_na = {
            "S&P 500": {"price": "N/A", "change": "N/A", "change_percent": "N/A"},
            "NASDAQ Composite": {"price": "N/A", "change": "N/A", "change_percent": "N/A"},
        }
        try:
            summary_na_market = await generate_summary_from_llm(sample_news, sample_market_data_na)
            print("Generated Summary (Test Case 3):")
            print(json.dumps(summary_na_market, indent=2))
        except ValueError as e:
            print(f"Error in Test Case 3: {e}")


    import asyncio
    asyncio.run(main_test())
