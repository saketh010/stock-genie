import json
from config.settings import groq_client, GROQ_MODEL
from tools.search import search_financial_news

def agent_2_intelligence(ticker: str) -> dict:
    print(f"\n--- AGENT 2: The Intelligence Agent ({ticker}) ---")
    
    # Step 1: Search for financial news directly using Tavily (no need for LLM tool calling)
    query = f"{ticker} latest institutional buy/sell ratings, target prices, and news"
    search_results = search_financial_news(query)
    
    # Step 2: Ask Groq to summarize into structured JSON
    prompt = f"""You are a financial intelligence analyst. Based on the following search results about {ticker}, 
    extract a structured summary.

    Search Results:
    {search_results}

    Return a JSON object with exactly these fields:
    - "sentiment": one of "Bullish", "Bearish", or "Neutral"
    - "summary": a concise summary of the institutional ratings and news
    - "target_price": the consensus target price as a number, or null if not available
    
    Example: {{"sentiment": "Bullish", "summary": "Morgan Stanley upgraded to Buy...", "target_price": 2500.0}}
    """
    
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a financial intelligence analyst. You must return ONLY a valid JSON object matching the requested schema. Do not output any markdown backticks, code blocks, or conversational text. Start your response directly with '{'."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    
    data = json.loads(response.choices[0].message.content)
    print(f"Intelligence output: {data['sentiment']} (Target: {data.get('target_price')})")
    return data
