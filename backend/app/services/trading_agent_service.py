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
    
    async def generate_trading_plan(self, idle_funds_amount):
        """Generate a trading plan for idle funds"""
        try:
            # Get market data
            market_data = await self.get_market_data()
            if market_data["status"] != "success":
                return market_data
                
            # Format data for the prompt
            formatted_data = self._format_data_for_prompt(market_data["data"])
            
            # Create prompt for OpenAI
            prompt = f"""
You are a high-frequency crypto trading bot managing idle funds from an invoice factoring pool.
You need to generate short-term (minutes to hours) trading opportunities for {idle_funds_amount} ETH.

Current market data:
{formatted_data}

Your goal is to maximize returns while ensuring the funds can be quickly liquidated if needed for invoice factoring.

Based on the data, provide:
1. Top 2-3 trading pairs to focus on
2. Entry and exit price points for each pair
3. Maximum position size for each trade (in % of idle funds)
4. Stop-loss levels to manage risk
5. Expected hold duration (in minutes/hours)

Keep your answers precise and actionable. These trades need to be executed automatically.
"""
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI trading bot specializing in high-frequency crypto trading. You provide specific, concise trading instructions that can be executed by automated systems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Extract the trading plan
            trading_plan = response.choices[0].message.content
            
            # Parse the trading plan
            parsed_plan = self._parse_trading_plan(trading_plan)
            
            # Generate a unique ID for this trading plan
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Store the trading plan
            plan_entry = {
                "id": plan_id,
                "timestamp": datetime.now().isoformat(),
                "idle_funds_amount": idle_funds_amount,
                "raw_plan": trading_plan,
                "parsed_plan": parsed_plan,
                "executed": False
            }
            
            self.trade_history.append(plan_entry)
            self.save_data()
            
            return {
                "status": "success",
                "plan_id": plan_id,
                "trading_plan": trading_plan,
                "parsed_plan": parsed_plan
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def _format_data_for_prompt(self, data):
        """Format market data for the prompt"""
        formatted = []
        
        # Format market sentiment
        sentiment = data.get("market_sentiment", {})
        formatted.append(f"MARKET SENTIMENT: {sentiment.get('label', 'neutral')}")
        formatted.append(f"SENTIMENT GRADE: {sentiment.get('grade', 50)}/100")
        formatted.append(f"MARKET SIGNAL: {sentiment.get('last_signal', 0)} (1=bullish, -1=bearish, 0=neutral)")
        
        # Format token data
        formatted.append("\nTOKEN ANALYSIS:")
        tokens = data.get("tokens", {})
        for symbol, token_data in tokens.items():
            formatted.append(f"\n{symbol}:")
            
            # Add trader grades if available
            grades = token_data.get("trader_grades", [])
            if grades:
                # Get the most recent grade
                latest_grade = grades[0] if len(grades) > 0 else {}
                
                grade_value = latest_grade.get('TM_TRADER_GRADE', 'N/A')
                formatted.append(f"  TM TRADER GRADE: {grade_value}")
                ta_grade = latest_grade.get('TA_GRADE', 'N/A')
                formatted.append(f"  TA GRADE: {ta_grade}")
                
                # Add current price if available
                price = latest_grade.get('CLOSE', 'N/A')
                formatted.append(f"  CURRENT PRICE: {price}")
                
                # Add grade change if available
                if len(grades) > 1:
                    previous_grade = grades[1]
                    current = float(latest_grade.get('TM_TRADER_GRADE', 0))
                    previous = float(previous_grade.get('TM_TRADER_GRADE', 0))
                    grade_change = current - previous
                    formatted.append(f"  GRADE CHANGE: {grade_change:+.2f}")
        
        return "\n".join(formatted)
    
    def _parse_trading_plan(self, plan_text):
        """Parse the trading plan text into structured format"""
        # Simple parsing for trading pairs, position sizes, etc.
        trading_pairs = []
        max_positions = {}
        stop_losses = {}
        exit_points = {}
        hold_durations = {}
        entry_prices = {}
        
        lines = plan_text.split('\n')
        current_pair = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains a trading pair
            if any(token in line.upper() for token in ["ETH/", "BTC/", "LINK/", "/USD", "/USDT", "/USDC"]):
                for pair_candidate in line.split():
                    if '/' in pair_candidate:
                        current_pair = pair_candidate.strip(',.:()')
                        trading_pairs.append(current_pair)
                        break
            
            # Extract position size
            if current_pair and ("position" in line.lower() or "size" in line.lower()) and "%" in line:
                try:
                    percentage = int(''.join(filter(str.isdigit, line.split("%")[0].split()[-1])))
                    max_positions[current_pair] = percentage
                except:
                    pass
            
            # Extract entry price
            if current_pair and ("entry" in line.lower() or "buy" in line.lower()) and "$" in line:
                try:
                    price = float(''.join(filter(lambda x: x.isdigit() or x == '.', 
                                    line.split('$')[1].split()[0])))
                    entry_prices[current_pair] = price
                except:
                    pass
            
            # Extract stop-loss
            if current_pair and "stop" in line.lower() and any(c.isdigit() for c in line):
                try:
                    # Extract number after $ or number before %
                    if '$' in line:
                        price = float(''.join(filter(lambda x: x.isdigit() or x == '.', 
                                        line.split('$')[1].split()[0])))
                        stop_losses[current_pair] = price
                    elif '%' in line:
                        percentage = float(''.join(filter(lambda x: x.isdigit() or x == '.', 
                                          line.split('%')[0].split()[-1])))
                        stop_losses[current_pair] = f"{percentage}%"
                except:
                    pass
            
            # Extract exit point
            if current_pair and any(term in line.lower() for term in ["exit", "take profit", "target"]):
                try:
                    if '$' in line:
                        price = float(''.join(filter(lambda x: x.isdigit() or x == '.', 
                                        line.split('$')[1].split()[0])))
                        exit_points[current_pair] = price
                except:
                    pass
            
            # Extract hold duration
            if current_pair and any(term in line.lower() for term in ["duration", "hold", "time"]) and (
                    any(unit in line.lower() for unit in ["minute", "hour", "day"])):
                hold_durations[current_pair] = line
        
        return {
            "trading_pairs": trading_pairs,
            "max_positions": max_positions,
            "entry_prices": entry_prices,
            "stop_losses": stop_losses,
            "exit_points": exit_points,
            "hold_durations": hold_durations,
            "raw_text": plan_text
        }
    
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
            
            # Get the advanced trading plan
            advanced_plan = await self.generate_advanced_trading_plan(plan.get("idle_funds_amount", 1.0))
            
            # Use either the advanced plan or fallback to the parsed GPT-4 plan
            parsed_plan = plan.get("parsed_plan", {})
            trading_pairs = parsed_plan.get("trading_pairs", [])
            
            # Record execution details
            execution_details = {
                "timestamp": datetime.now().isoformat(),
                "wallet_address": wallet_details["data"]["address"],
                "network": wallet_details["data"]["network"]["network_id"],
                "trades": []
            }
            
            # Execute trades based on parsed plan
            for pair in trading_pairs:
                # Extract token from pair (e.g., "ETH/USDT" -> "ETH")
                token = pair.split('/')[0] if '/' in pair else pair
                
                # Get position size for this pair
                position_size = parsed_plan.get("max_positions", {}).get(pair, 33)  # Default to 33%
                
                # Calculate amount to trade
                amount_to_trade = plan.get("idle_funds_amount", 1.0) * (position_size / 100)
                
                # Get entry and exit prices
                entry_price = parsed_plan.get("entry_prices", {}).get(pair, 0)
                exit_price = parsed_plan.get("exit_points", {}).get(pair, 0)
                stop_loss = parsed_plan.get("stop_losses", {}).get(pair, 0)
                
                # If we have better data from the advanced plan, use it
                if advanced_plan["status"] == "success":
                    for trade in advanced_plan.get("trading_plan", []):
                        if trade.get("symbol") == token:
                            entry_price = trade.get("entry_price", entry_price)
                            exit_price = trade.get("exit_price", exit_price) 
                            stop_loss = trade.get("stop_loss", stop_loss)
                            amount_to_trade = trade.get("amount", amount_to_trade)
                
                # If still missing prices, use defaults based on token
                if entry_price == 0:
                    if token == "BTC":
                        entry_price = 65000
                    elif token == "ETH":
                        entry_price = 3500
                    elif token == "LINK":
                        entry_price = 15
                    else:
                        entry_price = 100
                
                if exit_price == 0:
                    exit_price = entry_price * 1.05  # 5% profit target
                
                if stop_loss == 0 or isinstance(stop_loss, str):
                    stop_loss = entry_price * 0.95  # 5% stop loss
                
                # Calculate token amount
                token_amount = amount_to_trade / entry_price if entry_price > 0 else 0
                
                # Create trade record
                trade_record = {
                    "token": token,
                    "pair": pair,
                    "token_amount": token_amount,
                    "eth_amount": amount_to_trade,
                    "percentage": position_size,
                    "entry_price": entry_price,
                    "exit_target": exit_price,
                    "stop_loss": stop_loss,
                    "expected_profit_pct": ((exit_price / entry_price) - 1) * 100 if entry_price > 0 else 5,
                    "entry_time": datetime.now().isoformat(),
                    "status": "opened",
                    "tx_hash": f"0x{os.urandom(32).hex()}"  # Simulated transaction hash
                }
                
                execution_details["trades"].append(trade_record)
                
                # Add to active positions
                self.active_positions.append({
                    "plan_id": plan_id,
                    "token": token,
                    "pair": pair,
                    "entry_time": datetime.now().isoformat(),
                    "token_amount": token_amount,
                    "eth_amount": amount_to_trade,
                    "entry_price": entry_price,
                    "exit_target": exit_price,
                    "stop_loss": stop_loss,
                    "expected_profit_pct": ((exit_price / entry_price) - 1) * 100 if entry_price > 0 else 5,
                    "status": "active",
                    "current_price": entry_price  # Start at entry price
                })
            
            # If no trades were executed but we have advanced planning data, use that
            if not execution_details["trades"] and advanced_plan["status"] == "success":
                for trade in advanced_plan.get("trading_plan", []):
                    token = trade.get("symbol")
                    pair = f"{token}/USDT"  # Default pair format
                    
                    trade_record = {
                        "token": token,
                        "pair": pair,
                        "token_amount": trade.get("amount", 0) / trade.get("entry_price", 1),
                        "eth_amount": trade.get("amount", 0),
                        "percentage": trade.get("weight", 0.33) * 100,
                        "entry_price": trade.get("entry_price", 0),
                        "exit_target": trade.get("exit_price", 0),
                        "stop_loss": trade.get("stop_loss", 0),
                        "expected_profit_pct": trade.get("expected_profit_pct", 5),
                        "entry_time": datetime.now().isoformat(),
                        "status": "opened",
                        "tx_hash": f"0x{os.urandom(32).hex()}"  # Simulated transaction hash
                    }
                    
                    execution_details["trades"].append(trade_record)
                    
                    # Add to active positions
                    self.active_positions.append({
                        "plan_id": plan_id,
                        "token": token,
                        "pair": pair,
                        "entry_time": datetime.now().isoformat(),
                        "token_amount": trade_record["token_amount"],
                        "eth_amount": trade_record["eth_amount"],
                        "entry_price": trade_record["entry_price"],
                        "exit_target": trade_record["exit_target"],
                        "stop_loss": trade_record["stop_loss"],
                        "expected_profit_pct": trade_record["expected_profit_pct"],
                        "status": "active",
                        "current_price": trade_record["entry_price"]  # Start at entry price
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
    
    async def generate_advanced_trading_plan(self, idle_funds_amount):
        """Generate an advanced trading plan using multiple Token Metrics data sources"""
        try:
            # 1. Get market sentiment for overall direction
            sentiment = await token_metrics_service.get_market_sentiment()
            if sentiment["status"] != "success":
                # Don't fail, just use default values
                sentiment = {
                    "status": "success",
                    "market_sentiment": {
                        "grade": 50,
                        "label": "neutral",
                        "last_signal": 0,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                }

            market_signal = sentiment["market_sentiment"].get("last_signal", 0)
            sentiment_grade = sentiment["market_sentiment"].get("grade", 50)
            
            # 2. Get token info for potential trading pairs
            potential_tokens = ["ETH", "BTC", "LINK", "MATIC", "SOL", "AAVE"]
            token_data = {}
            
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # 3. For each token, collect multi-dimensional data
            for symbol in potential_tokens:
                # Get token basic info
                token_info = await self._get_token_info(symbol)
                if token_info["status"] != "success":
                    continue
                
                # Get trader grades (short-term signals)
                trader_grades = await self._get_trader_grades(symbol, start_date, end_date)
                
                # Get trading signals
                trading_signals = await self._get_trading_signals(symbol, start_date, end_date)
                
                # Store collected data
                token_data[symbol] = {
                    "info": token_info["token_info"],
                    "trader_grades": trader_grades.get("trader_grades", []),
                    "trading_signals": trading_signals
                }
            
            # 4. Score and rank tokens based on multiple factors
            scored_tokens = self._score_trading_opportunities(token_data, sentiment_grade, market_signal)
            
            # 5. Build optimal portfolio allocation based on scores
            allocation = self._build_portfolio_allocation(scored_tokens, idle_funds_amount)
            
            # 6. Generate specific entry/exit points
            trading_plan = self._generate_trading_parameters(allocation, token_data)
            
            # 7. Create a unique ID for this trading plan
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            plan_entry = {
                "id": plan_id,
                "timestamp": datetime.now().isoformat(),
                "idle_funds_amount": idle_funds_amount,
                "market_sentiment": sentiment["market_sentiment"],
                "allocation": allocation,
                "trading_plan": trading_plan,
                "executed": False
            }
            
            self.trade_history.append(plan_entry)
            self.save_data()
            
            return {
                "status": "success",
                "plan_id": plan_id,
                "market_sentiment": sentiment["market_sentiment"],
                "allocation": allocation,
                "trading_plan": trading_plan
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _score_trading_opportunities(self, token_data, sentiment_grade, market_signal):
        """Score tokens based on multiple factors with fallbacks for missing data"""
        scored_tokens = []
        
        for symbol, data in token_data.items():
            # Check if trader grades exist and aren't empty
            has_grades = "trader_grades" in data and len(data["trader_grades"]) > 0
            
            # If no grades, generate a score based on symbol
            if not has_grades:
                # Generate mock score based on symbol
                # This ensures we have *something* to display for demo
                seed = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
                mock_score = (seed % 40) + 60  # Score between 60-100
                
                scored_tokens.append({
                    "symbol": symbol,
                    "score": mock_score,
                    "trader_grade": 75,  # Default
                    "ta_grade": 70,  # Default
                    "signal_strength": 0.7,  # Default
                    "bull_bear_ratio": 0.6,  # Default
                    "is_mocked": True
                })
                continue
                
            # Get the latest trader grade
            latest_grade = data["trader_grades"][0] if data["trader_grades"] else {}
            
            # Calculate a composite score based on multiple factors
            # 1. Trader grade (0-100)
            trader_grade = float(latest_grade.get("TM_TRADER_GRADE", 50))
            
            # 2. Technical analysis grade (0-100)
            ta_grade = float(latest_grade.get("TA_GRADE", 50))
            
            # 3. Trading signal strength (0-1)
            signal_strength = data.get("trading_signals", {}).get("signal_strength", 0.6)
            
            # 4. Bullish vs bearish signal ratio
            bullish_signals = data.get("trading_signals", {}).get("bullish_signals", 2)
            bearish_signals = data.get("trading_signals", {}).get("bearish_signals", 1)
            
            bull_bear_ratio = 0.5
            total_signals = bullish_signals + bearish_signals
            if total_signals > 0:
                bull_bear_ratio = bullish_signals / total_signals
            
            # Adjust weights based on market sentiment
            sentiment_factor = sentiment_grade / 50  # Normalize to 0-2 range
            market_direction = 1 if market_signal > 0 else -1 if market_signal < 0 else 0
            
            # Calculate final score - this is where the magic happens
            score = (
                trader_grade * 0.35 +                        # Trader grade (35% weight)
                ta_grade * 0.25 +                            # Technical analysis (25% weight)
                signal_strength * 100 * 0.20 +               # Signal strength (20% weight)
                bull_bear_ratio * 100 * 0.20                 # Bull/bear ratio (20% weight)
            ) * (0.8 + sentiment_factor * 0.2)               # Adjust by market sentiment
            
            # Add market direction bias
            if market_direction != 0:
                # If market is bullish, boost tokens with high bull/bear ratio
                # If bearish, boost tokens with low bull/bear ratio
                direction_alignment = bull_bear_ratio if market_direction > 0 else (1 - bull_bear_ratio)
                score *= (1 + direction_alignment * 0.1)
            
            scored_tokens.append({
                "symbol": symbol,
                "score": score,
                "trader_grade": trader_grade,
                "ta_grade": ta_grade,
                "signal_strength": signal_strength,
                "bull_bear_ratio": bull_bear_ratio,
                "is_mocked": False
            })
        
        # If no tokens were scored, add default tokens
        if not scored_tokens:
            for i, symbol in enumerate(["ETH", "BTC", "LINK"]):
                scored_tokens.append({
                    "symbol": symbol,
                    "score": 75 + (10 if i == 0 else 5 if i == 1 else 0),
                    "trader_grade": 75,
                    "ta_grade": 70,
                    "signal_strength": 0.7,
                    "bull_bear_ratio": 0.6,
                    "is_mocked": True
                })
        
        # Sort by score (highest first)
        return sorted(scored_tokens, key=lambda x: x["score"], reverse=True)

    def _build_portfolio_allocation(self, scored_tokens, idle_funds_amount):
        """Build portfolio allocation based on scores"""
        # Start with empty allocation
        allocation = []
        
        # If no tokens scored, return empty allocation
        if not scored_tokens:
            return allocation
        
        # Always include at least the top token
        viable_tokens = [scored_tokens[0]]
        
        # If there are more tokens with decent scores, include them too
        for token in scored_tokens[1:3]:  # Consider top 3
            if token["score"] > 50:  # Lower threshold
                viable_tokens.append(token)
        
        # Calculate weights based on relative scores
        total_score = sum(t["score"] for t in viable_tokens)
        
        # Generate current prices for tokens (mocked or from data)
        prices = {
            "ETH": 3500,
            "BTC": 65000,
            "LINK": 15,
            "MATIC": 0.75,
            "SOL": 150,
            "AAVE": 90
        }
        
        for token in viable_tokens:
            symbol = token["symbol"]
            weight = token["score"] / total_score if total_score > 0 else 1.0
            # Determine amount based on weight
            amount = idle_funds_amount * weight
            
            # Get current price (mocked)
            current_price = prices.get(symbol, 100)  # Default to 100 if not in our mock data
            
            allocation.append({
                "symbol": symbol,
                "weight": weight,
                "amount": amount,
                "score": token["score"],
                "trader_grade": token["trader_grade"],
                "ta_grade": token["ta_grade"],
                "current_price": current_price,
                "token_amount": amount / current_price if current_price > 0 else 0,
                "is_mocked": token.get("is_mocked", False)
            })
        
        return allocation

    def _generate_trading_parameters(self, allocation, token_data):
        """Generate specific entry/exit points for each token"""
        trading_plan = []
        
        for token in allocation:
            symbol = token["symbol"]
            is_mocked = token.get("is_mocked", False)
            
            # For mocked data, generate reasonable trading parameters
            if is_mocked or symbol not in token_data:
                current_price = token.get("current_price", 100)
                
                # Generate trading parameters based on score
                score = token.get("score", 75)
                confidence = score / 100
                
                # Higher score = higher target and tighter stop loss
                target_multiplier = 1.0 + (0.05 * confidence)
                stop_loss_pct = 0.05 * (1 - confidence * 0.5)
                
                trading_plan.append({
                    "symbol": symbol,
                    "weight": token.get("weight", 0.33),
                    "amount": token.get("amount", 1.0),
                    "entry_price": current_price * 0.995,  # Slightly below current
                    "exit_price": current_price * target_multiplier,
                    "stop_loss": current_price * (1 - stop_loss_pct),
                    "hold_duration": "24-48 hours",
                    "current_price": current_price,
                    "expected_profit_pct": ((current_price * target_multiplier / (current_price * 0.995)) - 1) * 100,
                    "is_mocked": True
                })
                continue
            
            data = token_data.get(symbol, {})
            
            # Skip tokens with insufficient data
            if not data.get("trader_grades"):
                continue
            
            # Get the latest trader grade
            latest_grade = data["trader_grades"][0] if data["trader_grades"] else {}
            
            # Calculate entry price (slightly below current price)
            current_price = token.get("current_price", 100)
            if latest_grade.get("CLOSE"):
                current_price = float(latest_grade.get("CLOSE"))
            
            entry_price = current_price * 0.995  # 0.5% below current price
            
            # Calculate exit price based on TA Grade
            ta_grade = float(latest_grade.get("TA_GRADE", 50))
            exit_multiplier = 1.0 + (ta_grade / 1000)  # Higher TA grade = higher target
            exit_price = current_price * exit_multiplier
            
            # Calculate stop loss based on signal strength
            signal_strength = data.get("trading_signals", {}).get("signal_strength", 0.7)
            stop_loss_pct = 0.02 + (0.03 * (1 - signal_strength))  # 2-5% depending on signal confidence
            stop_loss = current_price * (1 - stop_loss_pct)
            
            # Determine hold duration based on trader grade trend
            hold_duration = "24-48 hours"  # Default
            if len(data["trader_grades"]) > 1:
                prev_grade = float(data["trader_grades"][1].get("TM_TRADER_GRADE", 50))
                curr_grade = float(latest_grade.get("TM_TRADER_GRADE", 50))
                if curr_grade > prev_grade + 5:
                    hold_duration = "48-72 hours"  # Strong uptrend
                elif curr_grade < prev_grade - 5:
                    hold_duration = "12-24 hours"  # Weakening trend
            
            trading_plan.append({
                "symbol": symbol,
                "weight": token["weight"],
                "amount": token["amount"],
                "entry_price": entry_price,
                "exit_price": exit_price,
                "stop_loss": stop_loss, 
                "hold_duration": hold_duration,
                "current_price": current_price,
                "expected_profit_pct": ((exit_price / entry_price) - 1) * 100,
                "is_mocked": False
            })
        
        return trading_plan
    
    async def backtest_strategy(self, idle_funds_amount):
        """Backtest a trading strategy with historical data"""
        try:
            # 1. Generate a trading plan
            plan_result = await self.generate_advanced_trading_plan(idle_funds_amount)
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
        
    async def _get_latest_candle_price(self, symbol: str) -> float:
        """
        Fetch the most recent hourly candle close for a given symbol using 
        the Token Metrics 'hourly_ohlcv' endpoint. 
        Returns None if no valid price found.
        """
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")  
            # or however far back you want to go

            # Query the Token Metrics service for hourly data
            # (Adjust symbol.lower() or uppercase to match the endpoint's convention)
            hourly_data = await token_metrics_service.get_hourly_ohlcv(
                symbol=symbol.lower(),
                start_date=start_date,
                end_date=end_date
            )
            # Example shape: { "status": "success", "data": [...] } or a DataFrame
            if hourly_data["status"] != "success" or not hourly_data.get("data"):
                return None
            
            # Convert to DataFrame if needed
            df = pd.DataFrame(hourly_data["data"])
            if df.empty or "CLOSE" not in df.columns:
                return None
            
            # Convert DATE or TIMESTAMP to datetime, sort by ascending
            if "DATE" in df.columns:
                df["DATE"] = pd.to_datetime(df["DATE"])
                df = df.sort_values(by="DATE")
            elif "TIMESTAMP" in df.columns:
                df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
                df = df.sort_values(by="TIMESTAMP")
            
            # Grab the most recent candle close
            latest_row = df.iloc[-1]
            latest_close = float(latest_row["CLOSE"])  
            return latest_close
        except Exception as e:
            print(f"Error fetching latest candle price for {symbol}: {e}")
            return None


# Create a single instance to be used throughout the application
trading_agent_service = TradingAgentService()