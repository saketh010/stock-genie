import json
from google.genai import types
from config.settings import gemini_client, tavily_client
from schemas.models import ScreenerOutput

def agent_1_screener() -> list[str]:
    print("\n--- AGENT 1: The Screener ---")
    query = "Latest buy or sell ratings for Indian bluechip stocks (NIFTY 50) from Motilal Oswal, Morgan Stanley, Moneycontrol, ICICI Direct"
    
    print("Scraping web for recent ratings...")
    if tavily_client:
        try:
            search_res = tavily_client.search(query=query, search_depth="advanced", max_results=5)
            context = "\n".join([f"{res['title']}: {res['content']}" for res in search_res.get('results', [])])
        except Exception as e:
            context = f"Search failed: {e}"
    else:
        context = "No search available (missing API key)."

    prompt = f"""
    Based on the following recent news and ratings about the Indian stock market:
    {context}
    
    Identify 3 to 5 NSE ticker symbols of bluechip stocks that have strong recent institutional ratings or momentum.
    Return ONLY a valid JSON list of strings (e.g. ["RELIANCE.NS", "TCS.NS"]). Ensure they have the '.NS' suffix for Yahoo Finance compatibility.
    """
    
    response = gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ScreenerOutput,
            temperature=0.2
        ),
    )
    
    try:
        data = json.loads(response.text)
        tickers = data.get("tickers", [])
        print(f"Screener identified: {tickers}")
        return tickers
    except Exception as e:
        print(f"Agent 1 failed to parse: {e}")
        return ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS"] # Fallback
