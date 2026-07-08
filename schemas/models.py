from pydantic import BaseModel, Field
from typing import List, Optional

class ScreenerOutput(BaseModel):
    tickers: List[str] = Field(description="List of NSE ticker symbols (e.g., ['RELIANCE.NS', 'TCS.NS'])")

class IntelligenceOutput(BaseModel):
    sentiment: str = Field(description="Overall sentiment (Bullish, Bearish, Neutral)")
    summary: str = Field(description="Summary of recent institutional ratings and news")
    target_price: Optional[float] = Field(description="Consensus target price if available, otherwise null")

class AnalystOutput(BaseModel):
    thesis: str = Field(description="BUY, SELL, or HOLD")
    bullish_points: List[str] = Field(description="Points supporting a bull case")
    bearish_points: List[str] = Field(description="Points supporting a bear case")
    summary: str = Field(description="Detailed explanation of the thesis based on MTFA and sentiment")

class CriticOutput(BaseModel):
    verdict: str = Field(description="AGREE or DISAGREE with the Analyst's thesis")
    rebuttal: str = Field(description="The argument criticizing or validating the Analyst's thesis based on philosophy")

class PMOutput(BaseModel):
    action: str = Field(description="EXECUTE_BUY, EXECUTE_SELL, or REJECT")
    allocation_pct: float = Field(description="Percentage of portfolio to allocate (0 if REJECT or SELL)")
    reasoning: str = Field(description="Explanation of the decision against risk rules")
