# app/tests/test_rate_agent.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.rate_agent_service import rate_agent_service

# Create mock response
mock_market_sentiment = {
    "status": "success",
    "market_sentiment": {
        "grade": 75.5,  # High sentiment (bullish)
        "label": "positive",
        "last_signal": 1,
        "date": "2023-10-01"
    }
}

@pytest.mark.asyncio
async def test_get_recommended_rates():
    """Test that the rate agent can recommend factoring rates based on market sentiment"""
    with patch('app.services.token_metrics.token_metrics_service.get_market_sentiment', 
              return_value=mock_market_sentiment):
        
        result = await rate_agent_service.get_recommended_rates()
        
        # Verify the result structure
        assert result["status"] == "success"
        assert "rates" in result
        assert "fee_range" in result["rates"]
        assert "advance_percentage" in result["rates"]
        
        # Since we mocked a high sentiment (75.5), verify it recommends favorable rates
        fee_min, fee_max = result["rates"]["fee_range"]
        assert fee_min < 2.5  # Lower fee minimum for positive sentiment
        
        advance_min, advance_max = result["rates"]["advance_percentage"]
        assert advance_max >= 85  # Higher advance % for positive sentiment