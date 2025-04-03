import os
from dotenv import load_dotenv
from tmai_api import TokenMetricsClient
from datetime import datetime, timedelta

load_dotenv()

class TokenMetricsService:
    """Service for interacting with Token Metrics API"""

    def __init__(self):
        self.api_key = os.getenv("TOKEN_METRICS_API_KEY")
        self.client = TokenMetricsClient(api_key=self.api_key)

    async def get_token_info(self, symbol):
        try:
            tokens = self.client.tokens.get_dataframe(symbol=symbol)
            if tokens.empty:
                return {"status": "error", "message": f"No data available for {symbol}"}
            latest = tokens.iloc[0]
            return {
                "status": "success",
                "token_info": {
                    "id": latest.get("TOKEN_ID"),
                    "name": latest.get("TOKEN_NAME"),
                    "symbol": latest.get("TOKEN_SYMBOL"),
                    "exchange_list": latest.get("EXCHANGE_LIST"),
                    "category_list": latest.get("CATEGORY_LIST"),
                    "contract_address": latest.get("CONTRACT_ADDRESS"),
                    "tm_link": latest.get("TM_LINK")
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_trader_grades(self, symbol, start_date=None, end_date=None):
        try:
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            trader_grades = self.client.trader_grades.get_dataframe(
                SYMBOL=symbol,
                startDate=start_date,
                endDate=end_date
            )

            if trader_grades.empty:
                return {"status": "error", "message": "No trader grades data available"}

            data = trader_grades.to_dict(orient="records")

            return {"status": "success", "trader_grades": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_market_sentiment(self):
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            sentiment = self.client.market_metrics.get_dataframe(
                startDate=start_date, 
                endDate=end_date
            )

            if sentiment.empty:
                return {"status": "error", "message": "No market sentiment data available"}

            latest = sentiment.iloc[-1]
            return {
                "status": "success",
                "market_sentiment": {
                    "grade": float(latest.get("MARKET_SENTIMENT_GRADE", 50)),
                    "label": latest.get("MARKET_SENTIMENT_LABEL", "neutral"),
                    "last_signal": int(latest.get("LAST_TM_GRADE_SIGNAL", 0)),
                    "date": latest.get("DATE", end_date)
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Instantiate the service
token_metrics_service = TokenMetricsService()
