import time
import datetime
from config.settings import GROQ_API_KEY
from agents.screener import agent_1_screener
from agents.intelligence import agent_2_intelligence
from agents.analyst import agent_3_analyst
from agents.critic import agent_4_critic
from agents.portfolio_manager import agent_5_portfolio_manager
from utils.portfolio import load_portfolio

def run_pipeline():
    print(f"Starting Multi-Agent Trading Pipeline at {datetime.datetime.now()}")
    tickers = agent_1_screener()
    
    portfolio = load_portfolio()
    existing_tickers = [h['ticker'] for h in portfolio.get('active_holdings', [])]
    
    all_tickers_to_evaluate = list(set(tickers + existing_tickers))
    print(f"Total tickers to evaluate today: {all_tickers_to_evaluate}")
    
    for ticker in all_tickers_to_evaluate:
        try:
            intel = agent_2_intelligence(ticker)
            analyst = agent_3_analyst(ticker, intel)
            critic = agent_4_critic(ticker, analyst)
            agent_5_portfolio_manager(ticker, analyst, critic)
            time.sleep(2)  # Small delay between stocks (Groq handles rate limits well)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            
    print("Pipeline execution complete.")

if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("Please set GROQ_API_KEY environment variable in your .env file or system. Exiting.")
    else:
        run_pipeline()
