import json
from google.genai import types
from config.settings import gemini_client
from schemas.models import CriticOutput
from utils.file_loader import load_file

def agent_4_critic(ticker: str, analyst_data: dict) -> dict:
    print(f"\n--- AGENT 4: The Critic ({ticker}) ---")
    philosophy = load_file("rules/trading_philosophy.md")
    
    prompt = f"""
    You are the Devil's Advocate Critic. Your job is to poke holes in the Analyst's thesis based strictly on our Trading Philosophy.
    
    Trading Philosophy:
    {philosophy}
    
    Stock: {ticker}
    Analyst Thesis: {json.dumps(analyst_data)}
    
    Attack this thesis. Find flaws. (e.g., are they buying a 5-day breakout when the 5-year trend is bearish? Are they ignoring 'quality first'?)
    Output your verdict (AGREE or DISAGREE) and your rebuttal as JSON.
    """
    
    response = gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CriticOutput,
            temperature=0.5
        ),
    )
    
    data = json.loads(response.text)
    print(f"Critic Verdict: {data['verdict']}")
    return data
