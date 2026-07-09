import json
import datetime
import yfinance as yf
from config.settings import groq_client, GROQ_MODEL
from utils.portfolio import load_portfolio, save_portfolio
from utils.file_loader import load_file

def agent_5_portfolio_manager(ticker: str, analyst_data: dict, critic_data: dict):
    print(f"\n--- AGENT 5: Portfolio Manager ({ticker}) ---")
    risk_framework = load_file("rules/risk_framework.md")
    portfolio = load_portfolio()
    
    prompt = f"""You are the Portfolio Manager. You make the final execution decision.
    
    Risk Framework:
    {risk_framework}
    
    Portfolio State:
    Available Cash: {portfolio['available_cash']}
    Total Portfolio Value: {portfolio['total_portfolio_value']}
    Current Holdings: {[h['ticker'] for h in portfolio['active_holdings']]}
    
    Stock: {ticker}
    Analyst Thesis: {analyst_data['thesis']}
    Analyst Summary: {analyst_data['summary']}
    Critic Verdict: {critic_data['verdict']}
    Critic Rebuttal: {critic_data['rebuttal']}
    
    Based on the Risk Framework, the Analyst's thesis, and the Critic's rebuttal, make a final decision: EXECUTE_BUY, EXECUTE_SELL, or REJECT.
    
    IMPORTANT GUIDELINES:
    - If the Analyst says BUY on a quality bluechip stock with institutional backing, you should EXECUTE_BUY unless there is a CRITICAL specific risk.
    - The Critic disagreeing alone is NOT sufficient to reject. Weigh the Analyst's data-driven thesis heavily.
    - If Analyst and Critic AGREE on BUY: allocate 8-10%.
    - If Analyst says BUY but Critic DISAGREES: still EXECUTE_BUY with 5% allocation.
    - Only REJECT if there is a concrete, specific, fundamental risk (not vague concerns).
    - Your job is to deploy capital into quality stocks, not to sit on cash.
    
    Return a JSON object with exactly these fields:
    - "action": one of "EXECUTE_BUY", "EXECUTE_SELL", or "REJECT"
    - "allocation_pct": percentage of portfolio to allocate (0 if REJECT or SELL)
    - "reasoning": explanation of the decision against risk rules
    """
        
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a Portfolio Manager. You must return ONLY a valid JSON object matching the requested schema. Do not output any markdown backticks, code blocks, or conversational text. Start your response directly with '{'."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    
    pm_decision = json.loads(response.choices[0].message.content)
    action = pm_decision['action']
    print(f"PM Decision: {action} (Alloc: {pm_decision['allocation_pct']}%)")
    print(f"Reasoning: {pm_decision['reasoning']}")
    
    # Execution Logic
    try:
        current_price = yf.Ticker(ticker).history(period='1d')['Close'].iloc[-1]
    except Exception:
        print("Could not fetch current price for execution. Skipping.")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if action == "EXECUTE_BUY":
        if any(h['ticker'] == ticker for h in portfolio['active_holdings']):
            print(f"Already holding {ticker}. Skipping buy to prevent over-allocation.")
            return
            
        alloc_amt = portfolio['total_portfolio_value'] * (pm_decision['allocation_pct'] / 100.0)
        
        min_cash = portfolio['total_portfolio_value'] * 0.10
        if portfolio['available_cash'] - alloc_amt < min_cash:
            print("Trade rejected: violates 10% minimum cash reserve.")
            return
            
        qty = int(alloc_amt // current_price)
        if qty > 0:
            cost = qty * current_price
            portfolio['available_cash'] -= cost
            portfolio['active_holdings'].append({
                "ticker": ticker,
                "avg_price": current_price,
                "qty": qty
            })
            portfolio['total_trades'] += 1
            portfolio['trade_log'].append({
                "timestamp": timestamp,
                "ticker": ticker,
                "action": "BUY",
                "price": current_price,
                "qty": qty,
                "reasoning": pm_decision['reasoning']
            })
            print(f"EXECUTED BUY: {qty} shares of {ticker} @ {current_price:.2f}")

    elif action == "EXECUTE_SELL":
        holding = next((h for h in portfolio['active_holdings'] if h['ticker'] == ticker), None)
        if holding:
            proceeds = holding['qty'] * current_price
            portfolio['available_cash'] += proceeds
            
            pnl = proceeds - (holding['qty'] * holding['avg_price'])
            portfolio['net_pnl'] += pnl
            
            portfolio['active_holdings'] = [h for h in portfolio['active_holdings'] if h['ticker'] != ticker]
            portfolio['total_trades'] += 1
            portfolio['trade_log'].append({
                "timestamp": timestamp,
                "ticker": ticker,
                "action": "SELL",
                "price": current_price,
                "qty": holding['qty'],
                "reasoning": pm_decision['reasoning'],
                "realized_pnl": pnl
            })
            print(f"EXECUTED SELL: {holding['qty']} shares of {ticker} @ {current_price:.2f}. PnL: {pnl:.2f}")
        else:
            print(f"Cannot sell {ticker}, not in portfolio.")
            
    # Update portfolio value
    total_holdings_value = 0
    for h in portfolio['active_holdings']:
        try:
            p = yf.Ticker(h['ticker']).history(period='1d')['Close'].iloc[-1]
            total_holdings_value += (p * h['qty'])
        except:
            total_holdings_value += (h['avg_price'] * h['qty'])
            
    portfolio['total_portfolio_value'] = portfolio['available_cash'] + total_holdings_value
    portfolio['net_pnl_percentage'] = ((portfolio['total_portfolio_value'] - 1000000.0) / 1000000.0) * 100
    
    save_portfolio(portfolio)
