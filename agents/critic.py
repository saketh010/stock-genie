import json
from config.settings import groq_client, GROQ_MODEL
from utils.file_loader import load_file

def agent_4_critic(ticker: str, analyst_data: dict) -> dict:
    print(f"\n--- AGENT 4: The Critic ({ticker}) ---")
    philosophy = load_file("rules/trading_philosophy.md")
    
    prompt = f"""You are the Devil's Advocate Critic. Your job is to poke holes in the Analyst's thesis based strictly on our Trading Philosophy.
    
    Trading Philosophy:
    {philosophy}
    
    Stock: {ticker}
    Analyst Thesis: {json.dumps(analyst_data)}
    
    Attack this thesis. Find flaws. (e.g., are they buying a 5-day breakout when the 5-year trend is bearish? Are they ignoring 'quality first'?)
    
    Return a JSON object with exactly these fields:
    - "verdict": one of "AGREE" or "DISAGREE"
    - "rebuttal": your argument criticizing or validating the Analyst's thesis based on philosophy
    """
    
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a Devil's Advocate Critic. You must return ONLY a valid JSON object matching the requested schema. Do not output any markdown backticks, code blocks, or conversational text. Start your response directly with '{'."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.5,
    )
    
    data = json.loads(response.choices[0].message.content)
    print(f"Critic Verdict: {data['verdict']}")
    return data
