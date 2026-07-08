import json
from google.genai import types
from config.settings import gemini_client
from tools.finance import get_mtfa_data
from schemas.models import AnalystOutput

def agent_3_analyst(ticker: str, intelligence_data: dict) -> dict:
    print(f"\n--- AGENT 3: The Analyst ({ticker}) ---")
    mtfa_data = get_mtfa_data(ticker)
    
    prompt = f"""
    You are an expert Technical and Fundamental Analyst for the Indian Stock Market.
    
    Stock: {ticker}
    
    Multi-Timeframe Analysis (MTFA):
    {mtfa_data}
    
    Institutional Sentiment & News:
    {json.dumps(intelligence_data)}
    
    Analyze the short-term momentum, medium-term trends, and long-term macro cycles against the institutional sentiment.
    Formulate a thesis (BUY, SELL, or HOLD).
    Output your analysis as JSON.
    """
    
    response = gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnalystOutput,
            temperature=0.4
        ),
    )
    
    data = json.loads(response.text)
    print(f"Analyst Thesis: {data['thesis']}")
    return data
