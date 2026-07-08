import json
from google.genai import types
from config.settings import gemini_client
from tools.search import search_financial_news
from schemas.models import IntelligenceOutput

def agent_2_intelligence(ticker: str) -> dict:
    print(f"\n--- AGENT 2: The Intelligence Agent ({ticker}) ---")
    
    prompt = f"Find the latest institutional buy/sell ratings, target prices, and news for the Indian stock {ticker}."
    
    chat = gemini_client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            tools=[search_financial_news],
            temperature=0.2
        )
    )
    
    response = chat.send_message(prompt)
    
    if response.function_calls:
        for function_call in response.function_calls:
            if function_call.name == "search_financial_news":
                args = function_call.args
                query = args.get("query", f"{ticker} target price rating Motilal Oswal Morgan Stanley")
                tool_result = search_financial_news(query)
                
                response = chat.send_message(
                    types.Part.from_function_response(
                        name="search_financial_news",
                        response={"result": tool_result}
                    )
                )

    summary_prompt = "Based on the information gathered, output a JSON summary of the sentiment, target price, and news."
    
    final_response = gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"Context from conversation:\n{response.text}\n\n{summary_prompt}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=IntelligenceOutput,
            temperature=0.2
        ),
    )
    
    data = json.loads(final_response.text)
    print(f"Intelligence output: {data['sentiment']} (Target: {data.get('target_price')})")
    return data
