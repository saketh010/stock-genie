import json
from config.settings import groq_client, GROQ_MODEL
from tools.finance import get_mtfa_data

def agent_3_analyst(ticker: str, intelligence_data: dict) -> dict:
    print(f"\n--- AGENT 3: The Analyst ({ticker}) ---")
    mtfa_data = get_mtfa_data(ticker)
    
    prompt = f"""You are an expert Technical and Fundamental Analyst for the Indian Stock Market.
    
    Stock: {ticker}
    
    Multi-Timeframe Analysis (MTFA):
    {mtfa_data}
    
    Institutional Sentiment & News:
    {json.dumps(intelligence_data)}
    
    Analyze the short-term momentum, medium-term trends, and long-term macro cycles against the institutional sentiment.
    Formulate a thesis (BUY, SELL, or HOLD).
    
    Return a JSON object with exactly these fields:
    - "thesis": one of "BUY", "SELL", or "HOLD"
    - "bullish_points": a list of strings supporting a bull case
    - "bearish_points": a list of strings supporting a bear case  
    - "summary": a detailed explanation of your thesis based on MTFA and sentiment
    """
    
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a technical and fundamental stock analyst. You must return ONLY a valid JSON object matching the requested schema. Do not output any markdown backticks, code blocks, or conversational text. Start your response directly with '{'."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    
    data = json.loads(response.choices[0].message.content)
    print(f"Analyst Thesis: {data['thesis']}")
    return data
