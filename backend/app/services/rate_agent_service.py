# app/services/rate_agent_service.py
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

from app.services.token_metrics import token_metrics_service

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

class RateAgentService:
    """Very simple agent for adjusting factoring rates and advance percentages"""
    
    def __init__(self):
        self.default_fee_range = (2.5, 4.5)  # Default fee range (min, max)
        self.default_advance_percentage = (65, 80)  # Default advance percentage range (min, max)
    
    async def get_recommended_rates(self):
        """Get recommended factoring rates based on market sentiment"""
        try:
            # Get market sentiment
            sentiment = await token_metrics_service.get_market_sentiment()
            
            if sentiment["status"] != "success":
                return {
                    "status": "error",
                    "message": "Failed to get market sentiment",
                    "rates": {
                        "fee_range": self.default_fee_range,
                        "advance_percentage": self.default_advance_percentage
                    }
                }
            
            # Simple logic for adjusting rates based on sentiment
            sentiment_data = sentiment["market_sentiment"]
            sentiment_grade = sentiment_data.get("grade", 50)
            sentiment_signal = sentiment_data.get("last_signal", 0)
            
            # Adjust fee range based on sentiment
            # Higher sentiment = lower fees (better for borrowers)
            if sentiment_grade > 70:  # Very positive sentiment
                fee_range = (2.0, 3.5)
            elif sentiment_grade > 50:  # Positive sentiment
                fee_range = (2.5, 4.0)
            elif sentiment_grade > 30:  # Neutral sentiment
                fee_range = (3.0, 4.5)
            else:  # Negative sentiment
                fee_range = (3.5, 5.0)
                
            # Adjust advance percentage based on sentiment
            # Higher sentiment = higher advance percentage (better for borrowers)
            if sentiment_grade > 70:  # Very positive sentiment
                advance_percentage = (75, 90)
            elif sentiment_grade > 50:  # Positive sentiment
                advance_percentage = (70, 85)
            elif sentiment_grade > 30:  # Neutral sentiment
                advance_percentage = (65, 80)
            else:  # Negative sentiment
                advance_percentage = (55, 70)
            
            return {
                "status": "success",
                "rates": {
                    "fee_range": fee_range,
                    "advance_percentage": advance_percentage,
                },
                "market_data": {
                    "sentiment_grade": sentiment_grade,
                    "sentiment_label": sentiment_data.get("label", "neutral"),
                    "market_signal": sentiment_signal,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e),
                "rates": {
                    "fee_range": self.default_fee_range,
                    "advance_percentage": self.default_advance_percentage
                }
            }

# Create a single instance to be used throughout the application
rate_agent_service = RateAgentService()