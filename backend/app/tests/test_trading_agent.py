# app/tests/test_trading_agent.py
import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from app.services.trading_agent_service import trading_agent_service

# Create mock responses
mock_market_data = {
    "status": "success",
    "data": {
        "market_sentiment": {
            "grade": 65.5,
            "label": "positive",
            "last_signal": 1
        },
        "tokens": {
            "ETH": {
                "info": {"id": "3306", "name": "Ethereum"},
                "trader_grades": [
                    {
                        "DATE": "2023-10-01",
                        "TM_TRADER_GRADE": 85.2,
                        "TA_GRADE": 82.3,
                        "QUANT_GRADE": 78.5
                    }
                ]
            },
            "BTC": {
                "info": {"id": "3375", "name": "Bitcoin"},
                "trader_grades": [
                    {
                        "DATE": "2023-10-01",
                        "TM_TRADER_GRADE": 88.7,
                        "TA_GRADE": 86.1,
                        "QUANT_GRADE": 81.2
                    }
                ]
            }
        },
        "timestamp": datetime.now().isoformat()
    }
}

# Mock OpenAI response
mock_openai_response = """
1. Trading Pairs:
   - ETH/USDT: Entry at $3000, exit at $3200
   - BTC/USDT: Entry at $60000, exit at $62500

2. Position Sizes:
   - ETH/USDT: 40% of idle funds
   - BTC/USDT: 30% of idle funds

3. Stop Losses:
   - ETH/USDT: $2850 (5% below entry)
   - BTC/USDT: $57000 (5% below entry)

4. Hold Duration:
   - ETH/USDT: 2-3 hours
   - BTC/USDT: 1-2 hours
"""

@pytest.mark.asyncio
async def test_generate_trading_plan():
    """Test that the trading agent can generate a trading plan for idle funds"""
    # Mock dependencies
    with patch('app.services.trading_agent_service.trading_agent_service.get_market_data', 
              return_value=mock_market_data), \
         patch('app.services.trading_agent_service.client.chat.completions.create') as mock_create:
        
        # Setup mock completion - simpler approach
        mock_message = MagicMock()
        mock_message.content = mock_openai_response
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_create.return_value = mock_completion
        
        # Call the method with 1 ETH of idle funds
        result = await trading_agent_service.generate_trading_plan(1.0)
        
        # Verify the result
        assert result["status"] == "success"
        assert "plan_id" in result
        assert "trading_plan" in result
        assert "parsed_plan" in result
        
        # Verify the parsed plan
        parsed_plan = result["parsed_plan"]
        assert "trading_pairs" in parsed_plan
        assert "max_positions" in parsed_plan
        assert "stop_losses" in parsed_plan
        
        # Verify that ETH/USDT is included as a trading pair
        assert any("ETH" in pair for pair in parsed_plan["trading_pairs"])

@pytest.mark.asyncio
async def test_trading_plan_parsing():
    """Test the parsing of a trading plan"""
    sample_plan = """
    ETH/USDT: Entry at $3000, exit at $3200, position size 40%
    BTC/USDT: Entry at $60000, exit at $65000, position size 30%
    Stop loss for ETH at $2850
    Stop loss for BTC at $57000
    Hold ETH for 2-3 hours
    Hold BTC for 1-2 hours
    """
    
    parsed = trading_agent_service._parse_trading_plan(sample_plan)
    
    # Check parsing worked
    assert "trading_pairs" in parsed
    assert len(parsed["trading_pairs"]) > 0
    
    # Check position sizes are extracted
    assert "max_positions" in parsed
    if "ETH/USDT" in parsed["max_positions"]:
        assert parsed["max_positions"]["ETH/USDT"] == 40