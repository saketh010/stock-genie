from config.settings import tavily_client

def search_financial_news(query: str) -> str:
    """Searches the web for the latest financial news and institutional ratings for a stock."""
    print(f"Tool Executing: search_financial_news for query: '{query}'")
    if not tavily_client:
        return "Tavily API key missing. Cannot search."
    try:
        response = tavily_client.search(query=query, search_depth="advanced", max_results=3)
        results = "\n".join([f"- {res['title']}: {res['content']}" for res in response.get('results', [])])
        return results if results else "No significant news found."
    except Exception as e:
        return f"Search failed: {e}"
