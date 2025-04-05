# app/services/trading_agent_service.py
import os
import json
import pandas as pd
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

from app.services.token_metrics import token_metrics_service
from app.services.agent_service import agent_service

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

class TradingAgentService:
    """Service for AI-powered trading of idle funds in the vault"""
    
    def __init__(self):
        self.data_file = "/tmp/trading_data.json"
        self.trade_history = []
        self.active_positions = []
        self.load_data()
        
    def load_data(self):
        """Load trading data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.trade_history = data.get("trade_history", [])
                    self.active_positions = data.get("active_positions", [])
        except Exception as e:
            print(f"Error loading trading data: {e}")
            self.trade_history = []
            self.active_positions = []
    
    def save_data(self):
        """Save trading data to file"""
        try:
            data = {
                "trade_history": self.trade_history,
                "active_positions": self.active_positions,
                "last_updated": datetime.now().isoformat()
            }
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving trading data: {e}")
            return False
            
    async def get_market_data(self):
        """Get market data for trading decisions"""
        try:
            # Get market sentiment
            sentiment = await token_metrics_service.get_market_sentiment()
            
            # Get trader grades for major tokens
            tokens = ["ETH", "BTC", "LINK", "MATIC", "AAVE"]
            token_data = {}
            
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")  # Increased from 3 to 30 days
            
            for symbol in tokens:
                # Get token info
                token_info = await self._get_token_info(symbol)
                
                # Only process tokens that we found data for
                if token_info["status"] == "success":
                    token_data[symbol] = {
                        "info": token_info["token_info"]
                    }
                    
                    # Get trader grades
                    grades = await self._get_trader_grades(symbol, start_date, end_date)
                    if grades["status"] == "success":
                        token_data[symbol]["trader_grades"] = grades["trader_grades"]
            
            # Structure collected data
            collected_data = {
                "market_sentiment": sentiment.get("market_sentiment", {}),
                "tokens": token_data,
                "timestamp": datetime.now().isoformat()
            }
            
            return {"status": "success", "data": collected_data}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _get_token_info(self, symbol):
        """Get info about a token - provide mock data if real data unavailable"""
        try:
            # First try to get data from Token Metrics API
            result = await token_metrics_service.get_token_info(symbol)
            if result["status"] == "success" and result.get("token_info"):
                return result
            
            # If API fails, provide mock data for the demo
            mock_id = int(hashlib.md5(symbol.encode()).hexdigest(), 16) % 10000
            return {
                "status": "success",
                "token_info": {
                    "id": mock_id,
                    "name": symbol,
                    "symbol": symbol,
                    "exchange_list": ["binance", "coinbase"],
                    "category_list": ["crypto"],
                    "contract_address": "0x" + "0" * 40,
                    "tm_link": f"https://tokenmetrics.com/tokens/{symbol}"
                }
            }
        except Exception as e:
            print(f"Error getting token info for {symbol}: {e}")
            # Even if error, return mock data for the demo
            mock_id = int(hashlib.md5(symbol.encode()).hexdigest(), 16) % 10000
            return {
                "status": "success",
                "token_info": {
                    "id": mock_id,
                    "name": symbol,
                    "symbol": symbol,
                    "exchange_list": ["binance", "coinbase"],
                    "category_list": ["crypto"],
                    "contract_address": "0x" + "0" * 40,
                    "tm_link": f"https://tokenmetrics.com/tokens/{symbol}"
                }
            }
    
    async def _get_trader_grades(self, symbol, start_date, end_date):
        """Get trader grades with fallback to mock data"""
        try:
            # First try to get data from Token Metrics API
            grades = await token_metrics_service.get_trader_grades(symbol, start_date, end_date)
            
            # Debug info
            print(f"Trader grades for {symbol}: Status={grades['status']}, Has data={len(grades.get('trader_grades', []))}")
            
            if grades["status"] == "success" and grades.get("trader_grades"):
                return grades
            
            # If no real data or API fails, provide mock data
            # Generate deterministic mock data based on symbol
            seed = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
            
            # Current date for the latest datapoint
            current_date = datetime.now()
            
            # Generate mock trader grades for the last 30 days
            mock_grades = []
            base_grade = (seed % 30) + 60  # Base grade between 60-90
            
            for i in range(30):
                date = (current_date - timedelta(days=i)).strftime("%Y-%m-%d")
                # Fluctuate the grade slightly for each day
                daily_fluctuation = ((seed + i) % 10) - 5  # -5 to +4
                
                tm_grade = min(100, max(10, base_grade + daily_fluctuation))
                ta_grade = min(100, max(10, tm_grade + ((seed + i) % 10) - 5))
                quant_grade = min(100, max(10, tm_grade - ((seed + i) % 8) + 4))
                
                # Generate mock price data
                if symbol == "BTC":
                    base_price = 65000
                elif symbol == "ETH":
                    base_price = 3500
                elif symbol == "LINK":
                    base_price = 15
                elif symbol == "MATIC":
                    base_price = 0.8
                else:
                    base_price = 100
                
                # Add some daily price movement
                price_change = ((seed + i) % 10) - 5  # -5% to +4%
                price = base_price * (1 + (price_change / 100))
                
                mock_grades.append({
                    "DATE": date,
                    "TOKEN_ID": seed % 10000,
                    "TOKEN_SYMBOL": symbol,
                    "TM_TRADER_GRADE": tm_grade,
                    "TA_GRADE": ta_grade,
                    "QUANT_GRADE": quant_grade,
                    "OPEN": price * 0.99,
                    "HIGH": price * 1.02,
                    "LOW": price * 0.98,
                    "CLOSE": price,
                    "VOLUME": base_price * 1000 * (1 + ((seed + i) % 20) / 100),
                    "is_mock": True
                })
            
            return {
                "status": "success",
                "trader_grades": mock_grades
            }
            
        except Exception as e:
            print(f"Error getting trader grades for {symbol}: {e}")
            return {"status": "error", "message": str(e), "trader_grades": []}
    
    async def get_active_positions(self):
        """Get all active trading positions (mocked)"""
        return {
            "status": "success",
            "active_positions": self.active_positions
        }
    
    async def get_trade_history(self):
        """Get trading history (mocked)"""
        return {
            "status": "success",
            "trade_history": self.trade_history
        }
    
    async def get_performance_stats(self):
        """Get performance statistics (mocked)"""
        # Create mock stats for the dashboard
        total_trades = len(self.trade_history)
        successful_trades = total_trades * 0.7  # 70% success rate
        
        # Calculate mock profit
        total_profit_percentage = 0
        total_traded_amount = 0
        
        for plan in self.trade_history:
            if plan.get("executed", False):
                amount = plan.get("idle_funds_amount", 0)
                total_traded_amount += amount
                
                # Generate random profit between -5% and +15%
                import random
                profit_percentage = random.uniform(-5, 15)
                total_profit_percentage += profit_percentage * amount
        
        # Calculate weighted average profit percentage
        avg_profit_percentage = 0
        if total_traded_amount > 0:
            avg_profit_percentage = total_profit_percentage / total_traded_amount
        
        return {
            "status": "success",
            "performance": {
                "total_trades": total_trades,
                "successful_trades": int(successful_trades),
                "avg_profit_percentage": round(avg_profit_percentage, 2),
                "total_profit_eth": round(total_traded_amount * avg_profit_percentage / 100, 4),
                "uptime_days": 30,  # Mock value
                "trade_frequency": "2.5 per day",  # Mock value
                "best_performing_pair": "ETH/USDT",  # Mock value
                "worst_performing_pair": "LINK/USDT",  # Mock value
                "last_updated": datetime.now().isoformat()
            }
        }
    
    async def _get_trading_signals(self, symbol, start_date, end_date):
        """Get trading signals with fallback to mock data"""
        try:
            # Generate mock trading signals based on symbol
            seed = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
            
            # Calculate bullish vs bearish signals based on seed
            bullish_count = (seed % 5) + 1  # 1-5 bullish signals
            bearish_count = ((seed >> 4) % 3) + 1  # 1-3 bearish signals
            
            # Calculate signal strength (0.5-0.9)
            signal_strength = 0.5 + ((seed % 5) / 10)
            
            return {
                "bullish_signals": bullish_count,
                "bearish_signals": bearish_count,
                "signal_strength": signal_strength
            }
        except Exception as e:
            print(f"Error getting trading signals for {symbol}: {e}")
            # Return default values
            return {
                "bullish_signals": 2,
                "bearish_signals": 1,
                "signal_strength": 0.7
            }
    
    async def backtest_strategy(self, idle_funds_amount):
        """Backtest a trading strategy with historical data"""
        try:
            # 1. Generate a trading plan
            plan_result = await self.generate_tm_trading_strategy(idle_funds_amount)
            if plan_result["status"] != "success":
                return plan_result
            
            # 2. Get historical data for the tokens in the plan
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            backtest_data = {}
            total_profit_pct = 0
            total_win_count = 0
            total_loss_count = 0
            
            for trade in plan_result["trading_plan"]:
                symbol = trade["symbol"]
                
                # Get historical OHLCV data
                trader_grades = await self._get_trader_grades(symbol, start_date, end_date)
                
                if trader_grades["status"] != "success" or not trader_grades.get("trader_grades"):
                    continue
                
                # Convert to pandas DataFrame
                df = pd.DataFrame(trader_grades["trader_grades"])
                
                # Sort by date
                df['DATE'] = pd.to_datetime(df['DATE'])
                df = df.sort_values('DATE')
                
                # Calculate daily returns
                df['DAILY_RETURN'] = df['CLOSE'].pct_change()
                
                # Generate signals based on TM_TRADER_GRADE changes
                df['SIGNAL'] = 0
                for i in range(1, len(df)):
                    # If trader grade is increasing, it's a buy signal
                    if df['TM_TRADER_GRADE'].iloc[i] > df['TM_TRADER_GRADE'].iloc[i-1]:
                        df.loc[df.index[i], 'SIGNAL'] = 1
                    # If trader grade is decreasing, it's a sell signal
                    elif df['TM_TRADER_GRADE'].iloc[i] < df['TM_TRADER_GRADE'].iloc[i-1]:
                        df.loc[df.index[i], 'SIGNAL'] = -1
                
                # Calculate strategy returns
                trades = []
                in_position = False
                entry_price = 0
                entry_date = None
                
                for i, row in df.iterrows():
                    # If not in position and we get a buy signal
                    if not in_position and row['SIGNAL'] == 1:
                        in_position = True
                        entry_price = row['CLOSE']
                        entry_date = row['DATE']
                    
                    # If in position and we get a sell signal
                    elif in_position and row['SIGNAL'] == -1:
                        in_position = False
                        exit_price = row['CLOSE']
                        profit_pct = (exit_price / entry_price - 1) * 100
                        
                        trades.append({
                            "entry_date": entry_date.strftime("%Y-%m-%d") if entry_date else "Unknown",
                            "exit_date": row['DATE'].strftime("%Y-%m-%d"),
                            "entry_price": float(entry_price),  # ensure these are float not np.float
                            "exit_price": float(exit_price),
                            "profit_pct": float(profit_pct),
                            "win": bool(profit_pct > 0),  # <--- Cast to pure Python bool
                        })
                        
                        # Update totals
                        total_profit_pct += profit_pct
                        if profit_pct > 0:
                            total_win_count += 1
                        else:
                            total_loss_count += 1
                
                # If still in position at the end, close the position
                if in_position:
                    exit_price = df['CLOSE'].iloc[-1]
                    profit_pct = (exit_price / entry_price - 1) * 100
                    
                    trades.append({
                        "entry_date": entry_date.strftime("%Y-%m-%d") if entry_date else "Unknown",
                        "exit_date": df['DATE'].iloc[-1].strftime("%Y-%m-%d"),
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "profit_pct": profit_pct,
                        "win": profit_pct > 0
                    })
                    
                    # Update totals
                    total_profit_pct += profit_pct
                    if profit_pct > 0:
                        total_win_count += 1
                    else:
                        total_loss_count += 1
                
                # Calculate performance metrics
                win_rate = 0
                if trades:
                    win_rate = sum(1 for t in trades if t["win"]) / len(trades) * 100
                    
                backtest_data[symbol] = {
                    "trades": trades,
                    "performance": {
                        "total_trades": len(trades),
                        "win_rate": win_rate,
                        "avg_profit_pct": sum(t["profit_pct"] for t in trades) / len(trades) if trades else 0,
                        "price_data": [
                            {"date": date.strftime("%Y-%m-%d"), "close": close} 
                            for date, close in zip(df['DATE'], df['CLOSE'])
                        ]
                    }
                }
            
            # Calculate overall performance
            total_trades = total_win_count + total_loss_count
            win_rate = total_win_count / total_trades * 100 if total_trades > 0 else 0
            
            return {
                "status": "success",
                "plan_id": plan_result["plan_id"],
                "backtest_data": backtest_data,
                "overall_performance": {
                    "total_profit_pct": total_profit_pct,
                    "win_rate": win_rate,
                    "total_trades": total_trades
                },
                "trading_plan": plan_result["trading_plan"]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def generate_tm_trading_strategy(self, idle_funds_amount):
        """Generate a trading strategy based on Token Metrics data and hourly OHLCV"""
        try:
            # Get current date range
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")  # Two weeks of data
            
            # 1. Get market sentiment for overall direction
            market_data = token_metrics_service.client.market_metrics.get_dataframe(
                startDate=start_date,
                endDate=end_date
            )
            
            # Extract market sentiment
            sentiment = {
                "grade": 50,  # Default neutral
                "label": "neutral",
                "last_signal": 0,
                "date": end_date
            }
            
            if not market_data.empty:
                latest = market_data.iloc[-1]
                sentiment = {
                    "grade": float(latest.get("MARKET_SENTIMENT_GRADE", 50)),
                    "label": latest.get("MARKET_SENTIMENT_LABEL", "neutral"),
                    "last_signal": int(latest.get("LAST_TM_GRADE_SIGNAL", 0)),
                    "date": latest.get("DATE", end_date)
                }
            
            # 2. Select target tokens (focus on major ones to ensure data availability)
            target_tokens = ["BTC", "ETH", "LINK", "SOL", "AVAX"]
            token_data = {}
            
            # 3. Get data for each token
            for symbol in target_tokens:
                print(f"Fetching data for {symbol}...")
                
                # 3.1 Get hourly OHLCV data for recent price action
                hourly_data = token_metrics_service.client.hourly_ohlcv.get_dataframe(
                    symbol=symbol.lower(),  # Use lowercase for API
                    startDate=(datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),  # Last 3 days hourly data
                    endDate=end_date
                )
                
                # 3.2 Get trader grades for sentiment
                trader_grades = token_metrics_service.client.trader_grades.get_dataframe(
                    symbol=symbol.lower(),
                    startDate=start_date,
                    endDate=end_date
                )
                
                # 3.3 Get trading signals for entry/exit confirmation
                trading_signals = token_metrics_service.client.trading_signals.get_dataframe(
                    symbol=symbol.lower(),
                    startDate=start_date,
                    endDate=end_date
                )
                
                # Skip tokens with missing critical data
                if hourly_data.empty:
                    print(f"No hourly data available for {symbol}, skipping")
                    continue
                    
                # Sort data by date
                if 'DATE' in hourly_data.columns:
                    hourly_data['DATE'] = pd.to_datetime(hourly_data['DATE'])
                    hourly_data = hourly_data.sort_values('DATE')
                elif 'TIMESTAMP' in hourly_data.columns:
                    hourly_data['TIMESTAMP'] = pd.to_datetime(hourly_data['TIMESTAMP'])
                    hourly_data = hourly_data.sort_values('TIMESTAMP')
                
                # Extract latest price with error handling
                latest_price = None
                try:
                    if not hourly_data.empty and 'CLOSE' in hourly_data.columns:
                        latest_price = float(hourly_data['CLOSE'].iloc[-1])
                except (IndexError, ValueError) as e:
                    print(f"Error extracting latest price for {symbol}: {e}")
                
                # If we couldn't get a price, use default values
                if latest_price is None:
                    if symbol == "BTC":
                        latest_price = 63000
                    elif symbol == "ETH":
                        latest_price = 3000
                    elif symbol == "LINK":
                        latest_price = 15
                    elif symbol == "SOL":
                        latest_price = 140
                    elif symbol == "AVAX":
                        latest_price = 35
                    else:
                        latest_price = 100
                    print(f"Using default price for {symbol}: {latest_price}")
                
                # Store data
                token_data[symbol] = {
                    "hourly_data": hourly_data,
                    "trader_grades": trader_grades,
                    "trading_signals": trading_signals,
                    "latest_price": latest_price
                }
            
            # 4. Score tokens based on multiple factors
            scored_tokens = []
            
            for symbol, data in token_data.items():
                # Skip tokens with no price data
                if "latest_price" not in data or data["latest_price"] is None:
                    continue
                    
                # 4.1 Calculate basic metrics
                latest_price = data["latest_price"]
                
                # 4.2 Get trader grade if available
                trader_grade = 50  # Default neutral
                if not data["trader_grades"].empty and 'TM_TRADER_GRADE' in data["trader_grades"].columns:
                    trader_grade = float(data["trader_grades"]['TM_TRADER_GRADE'].iloc[-1])
                
                # 4.3 Get trading signal if available
                signal = 0  # Default neutral
                if not data["trading_signals"].empty and 'TRADING_SIGNAL' in data["trading_signals"].columns:
                    signal = int(data["trading_signals"]['TRADING_SIGNAL'].iloc[-1])
                
                # 4.4 Calculate technical indicators using hourly data
                hourly = data["hourly_data"]
                
                # Calculate 20/50 EMA crossover signal (similar to their example)
                ema_signal = 0
                try:
                    if len(hourly) >= 50:
                        hourly['EMA20'] = hourly['CLOSE'].ewm(span=20).mean()
                        hourly['EMA50'] = hourly['CLOSE'].ewm(span=50).mean()
                        ema_signal = 1 if hourly['EMA20'].iloc[-1] > hourly['EMA50'].iloc[-1] else -1
                except Exception as e:
                    print(f"Error calculating EMA for {symbol}: {e}")
                
                # Calculate RSI
                rsi = 50  # Default
                rsi_signal = 0
                try:
                    if len(hourly) >= 14 and 'CLOSE' in hourly.columns:
                        delta = hourly['CLOSE'].diff()
                        gain = delta.clip(lower=0).rolling(window=14).mean()
                        loss = -delta.clip(upper=0).rolling(window=14).mean()
                        rs = gain / loss
                        hourly['RSI'] = 100 - (100 / (1 + rs))
                        rsi = hourly['RSI'].iloc[-1]
                        
                        # RSI signal: Bullish if RSI is rising from oversold, bearish if falling from overbought
                        if rsi < 30:
                            rsi_signal = 1  # Oversold, potential buy
                        elif rsi > 70:
                            rsi_signal = -1  # Overbought, potential sell
                except Exception as e:
                    print(f"Error calculating RSI for {symbol}: {e}")
                
                # 4.5 Calculate consolidated score
                # Combine trader grade, TM signal, EMA signal, and RSI
                score = (
                    trader_grade * 0.4 +                  # Trader grade (40%)
                    (signal * 25 + 50) * 0.3 +            # TM signal normalized to 0-100 (30%)
                    (ema_signal * 25 + 50) * 0.2 +        # EMA signal normalized to 0-100 (20%)
                    (50 - abs(rsi - 50)) * 0.1            # RSI - closer to 50 is better (10%)
                )
                
                # 4.6 Adjust by market sentiment
                market_factor = 1.0
                if sentiment["last_signal"] == 1:  # Bullish market
                    market_factor = 1.1
                elif sentiment["last_signal"] == -1:  # Bearish market
                    market_factor = 0.9
                    
                score *= market_factor
                
                # 4.7 Store scored token
                scored_tokens.append({
                    "symbol": symbol,
                    "score": score,
                    "trader_grade": trader_grade,
                    "tm_signal": signal,
                    "ema_signal": ema_signal,
                    "rsi": rsi,
                    "latest_price": latest_price
                })
            
            # 5. Sort tokens by score and select top performers
            scored_tokens = sorted(scored_tokens, key=lambda x: x["score"], reverse=True)
            
            # Ensure we have at least some tokens
            if not scored_tokens:
                # Fallback to predefined values if no token data available
                scored_tokens = [
                    {"symbol": "BTC", "score": 75, "trader_grade": 75, "latest_price": 63000},
                    {"symbol": "ETH", "score": 70, "trader_grade": 70, "latest_price": 3000}
                ]
            
            # 6. Build allocation based on scores
            allocation = []
            total_score = sum(token["score"] for token in scored_tokens[:3])  # Top 3 tokens
            
            for token in scored_tokens[:3]:  # Limit to top 3
                weight = token["score"] / total_score
                amount = idle_funds_amount * weight
                
                allocation.append({
                    "symbol": token["symbol"],
                    "weight": weight,
                    "amount": amount,
                    "score": token["score"],
                    "trader_grade": token.get("trader_grade", 50),
                    "current_price": token["latest_price"]
                })
            
            # 7. Generate specific trading parameters
            trading_plan = []
            
            for token in allocation:
                symbol = token["symbol"]
                current_price = token.get("latest_price", 100)
                
                # Calculate entry price (slightly below current)
                entry_price = current_price * 0.995
                
                # Calculate exit price based on score
                score_factor = token["score"] / 100
                exit_price = current_price * (1 + 0.03 * score_factor)  # 1-3% target based on score
                
                # Calculate stop loss
                stop_loss = current_price * (1 - 0.02)  # 2% stop loss
                
                # Determine hold duration based on signal strength
                hold_duration = "24-48 hours"  # Default
                
                trading_plan.append({
                    "symbol": symbol,
                    "weight": token["weight"],
                    "amount": token["amount"],
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "stop_loss": stop_loss,
                    "hold_duration": hold_duration,
                    "current_price": current_price,
                    "expected_profit_pct": ((exit_price / entry_price) - 1) * 100
                })
            
            # 8. Create a unique plan ID
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            plan_entry = {
                "id": plan_id,
                "timestamp": datetime.now().isoformat(),
                "executed": False,
                "idle_funds_amount": idle_funds_amount,
                "market_sentiment": sentiment,
                "allocation": allocation,
                "trading_plan": trading_plan
            }

            self.trade_history.append(plan_entry)
            self.save_data()

            # 9. Store and return the plan
            return {
                "status": "success",
                "plan_id": plan_id,
                "market_sentiment": sentiment,
                "allocation": allocation,
                "trading_plan": trading_plan
            }
        

            
        except Exception as e:
            print(f"Error generating trading strategy: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    async def execute_trade(self, plan_id):
        """Execute a trade based on the trading plan (mocked)"""
        try:
            # Find the trading plan
            plan = next((p for p in self.trade_history if p.get("id") == plan_id), None)
            if not plan:
                return {"status": "error", "message": "Trading plan not found"}
            
            # Check if plan was already executed
            if plan.get("executed", False):
                return {
                    "status": "success", 
                    "message": "Trading plan was already executed",
                    "plan_id": plan_id,
                    "execution_details": plan.get("execution_details", {})
                }
            
            # Get wallet details from agent service (only for address info)
            wallet_details = agent_service.get_wallet_details()
            if wallet_details["status"] == "error":
                # Create mock wallet details if agent not initialized
                wallet_details = {
                    "status": "success",
                    "data": {
                        "address": "0x" + os.urandom(20).hex(),
                        "network": {"network_id": "base-sepolia"}
                    }
                }
                    
            trading_plan = plan.get("trading_plan", [])
            
            # Record execution details
            execution_details = {
                "timestamp": datetime.now().isoformat(),
                "wallet_address": wallet_details["data"]["address"],
                "network": wallet_details["data"]["network"]["network_id"],
                "trades": []
            }
            
            # Total amount being traded
            total_amount = sum(float(trade.get("amount", 0)) for trade in trading_plan)
            
            # Simulate trades for each asset in the plan
            for trade in trading_plan:
                symbol = trade.get("symbol")
                amount = float(trade.get("amount", 0))
                entry_price = float(trade.get("entry_price", 0))
                exit_price = float(trade.get("exit_price", 0))
                expected_profit = float(trade.get("expected_profit_pct", 0))
                
                # Calculate amount of token based on current price
                token_amount = amount / entry_price if entry_price > 0 else 0
                
                trade_record = {
                    "symbol": symbol,
                    "token_amount": token_amount,
                    "eth_amount": amount,
                    "percentage_of_total": (amount / total_amount * 100) if total_amount > 0 else 0,
                    "entry_price": entry_price,
                    "exit_target": exit_price,
                    "stop_loss": trade.get("stop_loss"),
                    "expected_profit_pct": expected_profit,
                    "entry_time": datetime.now().isoformat(),
                    "status": "opened",
                    "tx_hash": f"0x{os.urandom(32).hex()}"  # Simulated transaction hash
                }
                
                execution_details["trades"].append(trade_record)
                
                # Add to active positions
                self.active_positions.append({
                    "plan_id": plan_id,
                    "symbol": symbol,
                    "entry_time": datetime.now().isoformat(),
                    "token_amount": token_amount,
                    "eth_amount": amount,
                    "entry_price": entry_price,
                    "exit_target": exit_price,
                    "stop_loss": trade.get("stop_loss"),
                    "expected_profit_pct": expected_profit,
                    "status": "active",
                    "current_price": entry_price  # Start at entry price
                })
            
            # Mark plan as executed
            plan["executed"] = True
            plan["execution_timestamp"] = datetime.now().isoformat()
            plan["execution_details"] = execution_details
            self.save_data()
            
            return {
                "status": "success",
                "message": "Trading plan executed successfully (mocked)",
                "plan_id": plan_id,
                "execution_details": execution_details
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create a single instance to be used throughout the application
trading_agent_service = TradingAgentService()