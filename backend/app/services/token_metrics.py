import os
from tmai_api import TokenMetricsClient
from datetime import datetime, timedelta

class TokenMetricsService:
    """Service for interacting with Token Metrics API"""
    
    def __init__(self):
        self.api_key = os.getenv("TOKEN_METRICS_API_KEY")
        self.client = TokenMetricsClient(api_key=self.api_key)
        
    async def get_market_sentiment(self):
        """Get the overall market sentiment data"""
        try:
            # Get current date and date from 7 days ago
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            # Fetch market metrics
            market_metrics = self.client.market_metrics.get_dataframe(
                startDate=start_date,
                endDate=end_date
            )
            
            if market_metrics.empty:
                return {"status": "error", "message": "No market metrics data available"}
            
            # Get the latest market sentiment data
            latest_metrics = market_metrics.iloc[-1]
            
            return {
                "status": "success",
                "market_sentiment": {
                    "grade": float(latest_metrics.get("MARKET_SENTIMENT_GRADE", 50)),
                    "label": latest_metrics.get("MARKET_SENTIMENT_LABEL", "neutral"),
                    "last_signal": int(latest_metrics.get("LAST_TM_GRADE_SIGNAL", 0)),
                    "date": latest_metrics.get("DATE", end_date)
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_stablecoin_health(self, symbols=["USDC", "USDT", "DAI"]):
        """Get health metrics for stablecoins"""
        try:
            # Get current date and date from 7 days ago
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            # Fetch trader grades for stablecoins
            trader_grades = self.client.trader_grades.get_dataframe(
                symbol=",".join(symbols),
                startDate=start_date,
                endDate=end_date
            )
            
            if trader_grades.empty:
                return {"status": "error", "message": "No stablecoin data available"}
            
            # Process the data to get the latest grades for each stablecoin
            result = {}
            for symbol in symbols:
                symbol_data = trader_grades[trader_grades["SYMBOL"] == symbol]
                if not symbol_data.empty:
                    latest = symbol_data.iloc[-1]
                    result[symbol] = {
                        "grade": float(latest.get("TM_TRADER_GRADE", 50)),
                        "ta_grade": float(latest.get("TA_GRADE", 50)),
                        "quant_grade": float(latest.get("QUANT_GRADE", 50)),
                        "date": latest.get("DATE", end_date)
                    }
            
            return {"status": "success", "stablecoin_health": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

token_metrics = TokenMetricsService()