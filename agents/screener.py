import json
from config.settings import groq_client, tavily_client, GROQ_MODEL
from schemas.models import ScreenerOutput

def agent_1_screener() -> list[str]:
    print("\n--- AGENT 1: The Screener ---")
    queries = [
        "Latest buy sell ratings Indian stocks NSE broker recommendations upgrades largecap midcap smallcap Jefferies Kotak Motilal",
        "Top stock picks India broker ratings upgrades JP Morgan Nomura Morgan Stanley ICICI",
    ]
    
    print("Scraping web for recent ratings...")
    context = ""
    if tavily_client:
        for q in queries:
            try:
                search_res = tavily_client.search(query=q, search_depth="advanced", max_results=3)
                context += "\n".join([f"{res['title']}: {res['content']}" for res in search_res.get('results', [])]) + "\n"
            except Exception as e:
                context += f"Search failed for query: {e}\n"
    else:
        context = "No search available (missing API key)."

    prompt = f"""
    Based on the following recent news and ratings about the Indian stock market:
    {context}
    
    Identify ALL NSE ticker symbols of stocks mentioned that have recent institutional ratings, target price upgrades, or strong momentum.
    Include stocks of any market cap — largecap, midcap, and smallcap are all welcome.
    Cover multiple sectors — include banks, IT, pharma, energy, auto, FMCG, and any other sector mentioned.
    Do not limit yourself — include every stock that has a clear recommendation from a major institution or brokerage.
    You MUST return at least 5 stocks if they are available in the search results. Aim for 5-10 diverse tickers.
    Return ONLY a valid JSON object with a "tickers" key containing a list of strings.
    Example: {{"tickers": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SUNPHARMA.NS"]}}
    Ensure all tickers have the '.NS' suffix for Yahoo Finance compatibility.
    """
    
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a stock market screener. You must return ONLY a valid JSON object matching the requested schema. Do not output any markdown backticks, code blocks, or conversational text. Start your response directly with '{'."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    
    try:
        data = json.loads(response.choices[0].message.content)
        tickers = data.get("tickers", [])
        print(f"Screener identified: {tickers}")
        return tickers
    except Exception as e:
        print(f"Agent 1 failed to parse: {e}")
        return ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS"]  # Fallback
