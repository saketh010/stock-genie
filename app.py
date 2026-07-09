import streamlit as st
import json
import pandas as pd
import os

# Set page config for a sleek dark mode look
st.set_page_config(
    page_title="Autonomous Trading Agent (NSE)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for aesthetic
st.markdown("""
<style>
    /* Sleek container styling */
    .metric-container {
        background-color: #1e1e2d;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

from utils.portfolio import load_portfolio
from main import run_pipeline
import sys
import contextlib

class StreamlitRedirect:
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.buffer = ""
    def write(self, string):
        self.buffer += string
        self.placeholder.text(self.buffer)
    def flush(self):
        pass

@contextlib.contextmanager
def st_capture(placeholder):
    old_stdout = sys.stdout
    sys.stdout = StreamlitRedirect(placeholder)
    try:
        yield
    finally:
        sys.stdout = old_stdout

def main():
    st.title("📈 Autonomous Indian Stock Market Trading Agent")
    st.markdown("### A 5-Agent Pipeline Paper Trading Dashboard (NSE)")
    
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("🚀 Start Review (Run Agents)", width="stretch"):
            st.session_state.run_agents = True

    # If button was clicked, run the pipeline with streaming logs
    if getattr(st.session_state, 'run_agents', False):
        st.markdown("### 🧠 Live Agent Reasoning")
        log_placeholder = st.empty()
        with st_capture(log_placeholder):
            run_pipeline()
        st.success("Pipeline Execution Complete!")
        st.session_state.run_agents = False
    
    data = load_portfolio()
    
    if not data:
        st.warning("No portfolio data found. Run the pipeline to initialize.")
        return

    # Top Metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Portfolio Value", value=f"₹{data.get('total_portfolio_value', 1000000):,.2f}")
    with col2:
        pnl = data.get('net_pnl', 0)
        pnl_pct = data.get('net_pnl_percentage', 0)
        st.metric(label="Net P&L", value=f"₹{pnl:,.2f}", delta=f"{pnl_pct:.2f}%")
    with col3:
        st.metric(label="Available Cash", value=f"₹{data.get('available_cash', 1000000):,.2f}")
    with col4:
        st.metric(label="Total Trades Executed", value=data.get('total_trades', 0))

    st.markdown("---")
    
    st.subheader("💼 Active Holdings")
    holdings = data.get('active_holdings', [])
    if holdings:
        df_holdings = pd.DataFrame(holdings)
        # Reorder and format columns
        df_holdings.columns = ['Ticker', 'Average Price', 'Quantity']
        df_holdings['Average Price'] = pd.to_numeric(df_holdings['Average Price'], errors='coerce')
        df_holdings['Quantity'] = pd.to_numeric(df_holdings['Quantity'], errors='coerce')
        df_holdings['Total Cost'] = df_holdings['Average Price'] * df_holdings['Quantity']
        st.dataframe(df_holdings.style.format({
            "Average Price": "₹{:.2f}",
            "Total Cost": "₹{:.2f}"
        }), width="stretch", hide_index=True)
    else:
        st.info("No active holdings at the moment. Cash is a position!")

    st.markdown("---")
    
    st.subheader("📜 Trade Log & Agent Reasoning")
    trade_log = data.get('trade_log', [])
    if trade_log:
        # Reverse to show newest first
        df_trades = pd.DataFrame(reversed(trade_log))
        # Format columns if they exist
        if 'realized_pnl' in df_trades.columns:
            df_trades['realized_pnl'] = df_trades['realized_pnl'].fillna(0).map("₹{:,.2f}".format)
        
        df_trades['price'] = df_trades['price'].map("₹{:,.2f}".format)
        
        # We will use st.data_editor or st.dataframe to display
        st.dataframe(
            df_trades,
            column_config={
                "timestamp": "Time",
                "ticker": "Ticker",
                "action": "Action",
                "price": "Exec Price",
                "qty": "Quantity",
                "reasoning": st.column_config.TextColumn(
                    "Agent Reasoning (Why?)",
                    help="The Portfolio Manager's justification based on Analyst/Critic inputs.",
                    width="large"
                ),
                "realized_pnl": "Realized P&L"
            },
            hide_index=True,
            width="stretch"
        )
    else:
        st.info("No trades executed yet.")

if __name__ == "__main__":
    main()
