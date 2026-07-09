import json
import os
import yfinance as yf
try:
    from supabase import create_client, Client
except ImportError:
    pass

PORTFOLIO_FILE = "paper_portfolio.json"

def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return create_client(url, key)
    return None

def load_portfolio() -> dict:
    client = get_supabase_client()
    if client:
        try:
            # 1. Fetch portfolio state
            port_res = client.table('portfolio').select('*').eq('id', 1).execute()
            if port_res.data:
                state = port_res.data[0]
                
                # 2. Fetch active holdings
                hold_res = client.table('holdings').select('*').execute()
                holdings = []
                for h in hold_res.data:
                    holdings.append({
                        "ticker": h['ticker'],
                        "avg_price": float(h['avg_price']),
                        "qty": int(h['qty'])
                    })
                
                # 3. Fetch trade log
                trade_res = client.table('trades').select('*').order('executed_at', desc=True).execute()
                trade_log = []
                for t in trade_res.data:
                    trade_log.append({
                        "timestamp": t['executed_at'],
                        "ticker": t['ticker'],
                        "action": t['action'],
                        "price": float(t['price']),
                        "qty": int(t['qty']),
                        "reasoning": t['reasoning'],
                        "realized_pnl": float(t['realized_pnl']) if t['realized_pnl'] is not None else 0.0
                    })
                
                # Reverse to chronological order (codebase handles reversal inside dashboard UI)
                trade_log.reverse()

                return {
                    "total_portfolio_value": float(state['total_value']),
                    "available_cash": float(state['available_cash']),
                    "net_pnl": float(state['net_pnl']),
                    "net_pnl_percentage": float(state['net_pnl_pct']),
                    "total_trades": int(state['total_trades']),
                    "active_holdings": holdings,
                    "trade_log": trade_log
                }
        except Exception as e:
            print(f"Supabase load error: {e}")

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
    client = get_supabase_client()
    if client:
        try:
            # 1. Update portfolio state
            client.table('portfolio').update({
                "total_value": portfolio['total_portfolio_value'],
                "available_cash": portfolio['available_cash'],
                "net_pnl": portfolio['net_pnl'],
                "net_pnl_pct": portfolio['net_pnl_percentage'],
                "total_trades": portfolio['total_trades']
            }).eq('id', 1).execute()
            
            # 2. Sync holdings
            db_holdings_res = client.table('holdings').select('ticker').execute()
            db_tickers = {h['ticker'] for h in db_holdings_res.data}
            
            new_holdings = portfolio['active_holdings']
            new_tickers = {h['ticker'] for h in new_holdings}
            
            # Delete sold holdings
            tickers_to_delete = db_tickers - new_tickers
            for ticker in tickers_to_delete:
                client.table('holdings').delete().eq('ticker', ticker).execute()
                
            # Upsert active holdings
            for h in new_holdings:
                try:
                    current_price = yf.Ticker(h['ticker']).history(period='1d')['Close'].iloc[-1]
                except:
                    current_price = h['avg_price']
                
                current_value = current_price * h['qty']
                total_cost = h['avg_price'] * h['qty']
                unrealized_pnl = current_value - total_cost
                
                client.table('holdings').upsert({
                    "ticker": h['ticker'],
                    "avg_price": h['avg_price'],
                    "qty": h['qty'],
                    "current_price": current_price,
                    "current_value": current_value,
                    "unrealized_pnl": unrealized_pnl
                }, on_conflict='ticker').execute()
                
            # 3. Sync trade log (append new entries only)
            db_trades_res = client.table('trades').select('id').execute()
            db_trades_count = len(db_trades_res.data)
            
            new_trades = portfolio['trade_log']
            if len(new_trades) > db_trades_count:
                trades_to_insert = new_trades[db_trades_count:]
                for t in trades_to_insert:
                    # Clean up timezone or date strings if they have trailing offsets
                    executed_at = t['timestamp']
                    client.table('trades').insert({
                        "ticker": t['ticker'],
                        "action": t['action'],
                        "price": t['price'],
                        "qty": t['qty'],
                        "reasoning": t.get('reasoning', ''),
                        "realized_pnl": t.get('realized_pnl', 0.0),
                        "executed_at": executed_at
                    }).execute()
        except Exception as e:
            print(f"Supabase save error: {e}")

    with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, indent=4)
