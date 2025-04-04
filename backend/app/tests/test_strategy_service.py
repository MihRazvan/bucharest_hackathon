import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

# Import the services to be tested
from app.services.ai_strategy_service import ai_strategy_service

# Create mock response for token_metrics_service methods
mock_market_sentiment = {
    "status": "success",
    "market_sentiment": {
        "grade": 65.5,
        "label": "positive",
        "last_signal": 1,
        "date": "2023-10-01"
    }
}

mock_token_info = {
    "status": "success",
    "token_info": {
        "id": "3375",
        "name": "Bitcoin",
        "symbol": "BTC",
        "exchange_list": ["binance", "coinbase"],
        "category_list": ["currency"],
        "contract_address": "0x...",
        "tm_link": "https://tokenmetrics.com/coin/BTC"
    }
}

mock_trader_grades = {
    "status": "success",
    "trader_grades": [
        {
            "DATE": "2023-10-01",
            "TM_TRADER_GRADE": 85.2,
            "TA_GRADE": 82.3,
            "QUANT_GRADE": 78.5
        }
    ]
}

mock_market_metrics = {
    "status": "success",
    "market_metrics": [
        {
            "DATE": "2023-10-01",
            "TOTAL_CRYPTO_MCAP": 1500000000000,
            "TM_GRADE_PERC_HIGH_COINS": 65.2
        }
    ]
}

# Define test functions
@pytest.mark.asyncio
async def test_collect_token_metrics_data():
    """Test collecting Token Metrics data with mocked responses"""
    with patch('app.services.token_metrics.token_metrics_service.get_market_sentiment', 
              return_value=mock_market_sentiment), \
         patch('app.services.token_metrics.token_metrics_service.get_token_info', 
              return_value=mock_token_info), \
         patch('app.services.token_metrics.token_metrics_service.get_trader_grades', 
              return_value=mock_trader_grades), \
         patch('app.services.token_metrics.token_metrics_service.get_market_metrics', 
              return_value=mock_market_metrics):
        
        result = await ai_strategy_service.collect_token_metrics_data()
        
        assert result["status"] == "success"
        assert "data" in result
        assert "market_sentiment" in result["data"]
        assert "tokens" in result["data"]
        assert "market_metrics" in result["data"]
        
        # Verify market sentiment data
        assert result["data"]["market_sentiment"]["grade"] == 65.5
        
        # Verify token data
        assert "BTC" in result["data"]["tokens"]  # Assuming BTC is one of the tokens collected

@pytest.mark.asyncio
async def test_format_data_for_prompt():
    """Test formatting data for the OpenAI prompt"""
    # Create sample data
    sample_data = {
        "market_sentiment": {
            "grade": 65.5,
            "label": "positive",
            "last_signal": 1
        },
        "tokens": {
            "BTC": {
                "info": {
                    "id": "3375",
                    "name": "Bitcoin"
                },
                "trader_grades": [
                    {
                        "TM_TRADER_GRADE": 85.2,
                        "TA_GRADE": 82.3,
                        "QUANT_GRADE": 78.5
                    }
                ]
            }
        },
        "market_metrics": [
            {
                "TOTAL_CRYPTO_MCAP": 1500000000000,
                "TM_GRADE_PERC_HIGH_COINS": 65.2
            }
        ]
    }
    
    formatted = ai_strategy_service._format_data_for_prompt(sample_data)
    
    # Check that formatting works
    assert "MARKET SENTIMENT: positive" in formatted
    assert "SENTIMENT GRADE: 65.5/100" in formatted
    assert "BTC:" in formatted
    assert "TM TRADER GRADE: 85.2" in formatted

@pytest.mark.asyncio
async def test_parse_strategy():
    """Test parsing a strategy response with a simplified approach"""
    # Create a simple strategy text
    sample_strategy = """
    ETH/USDT: Entry at $3000, exit at $3200, position size 30%
    BTC/USDT: Entry at $60000, exit at $65000, position size 25%
    Stop losses at 5% for all positions
    Hold for 2-3 hours
    """
    
    # For simplicity, directly check if we can call the method without error
    parsed = ai_strategy_service._parse_strategy(sample_strategy)
    
    # Only verify that parsing doesn't fail and returns a dictionary
    assert isinstance(parsed, dict)

@pytest.mark.asyncio
async def test_save_and_load_strategy():
    """Test saving and loading strategy data"""
    # Mock the file operations
    with patch('builtins.open', create=True), \
         patch('json.dump'), \
         patch('json.load', return_value={"history": [{"id": "test_strategy", "raw_strategy": "test"}]}), \
         patch('os.path.exists', return_value=True):
        
        # Test loading data
        ai_strategy_service.load_data()
        assert len(ai_strategy_service.strategy_history) == 1
        assert ai_strategy_service.strategy_history[0]["id"] == "test_strategy"
        
        # Test saving data
        result = ai_strategy_service.save_data()
        assert result == True