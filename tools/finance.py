import yfinance as yf

def get_mtfa_data(ticker: str) -> str:
    """Fetches Multi-Timeframe Analysis data using yfinance."""
    print(f"Fetching MTFA data for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        data_summary = ""
        
        # Helper to get return over a period
        def get_return(period):
            hist = stock.history(period=period)
            if len(hist) >= 2:
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                return f"{((end_price - start_price) / start_price * 100):.2f}%"
            return "N/A"
        
        data_summary += f"Current Price (Approx): {stock.history(period='1d')['Close'].iloc[-1]:.2f}\n"
        data_summary += f"5-Day Return: {get_return('5d')}\n"
        data_summary += f"1-Month Return: {get_return('1mo')}\n"
        data_summary += f"6-Month Return: {get_return('6mo')}\n"
        data_summary += f"1-Year Return: {get_return('1y')}\n"
        data_summary += f"5-Year Return: {get_return('5y')}\n"
        
        return data_summary
    except Exception as e:
        return f"Failed to fetch MTFA data for {ticker}: {e}"
