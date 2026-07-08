import json
import os

PORTFOLIO_FILE = "paper_portfolio.json"

def load_portfolio() -> dict:
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading portfolio: {e}")
    
    return {
        "total_portfolio_value": 1000000.0,
        "available_cash": 1000000.0,
        "net_pnl": 0.0,
        "net_pnl_percentage": 0.0,
        "total_trades": 0,
        "active_holdings": [],
        "trade_log": []
    }

def save_portfolio(portfolio: dict):
    with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, indent=4)
