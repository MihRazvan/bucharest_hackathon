# app/services/trading_agent_service.py
import os
import json
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
            start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            
            for symbol in tokens:
                # Get token info
                token_info = await token_metrics_service.get_token_info(symbol)
                
                # Only process tokens that we found data for
                if token_info["status"] == "success":
                    token_data[symbol] = {
                        "info": token_info["token_info"]
                    }
                    
                    # Get trader grades
                    grades = await token_metrics_service.get_trader_grades(
                        symbol, start_date, end_date
                    )
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
                latest_grade = grades[-1] if len(grades) > 0 else {}
                
                grade_value = latest_grade.get('TM_TRADER_GRADE', 'N/A')
                formatted.append(f"  TM TRADER GRADE: {grade_value}")
                ta_grade = latest_grade.get('TA_GRADE', 'N/A')
                formatted.append(f"  TA GRADE: {ta_grade}")
                
                # Add grade change if available
                if len(grades) > 1:
                    previous_grade = grades[-2]
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
            "stop_losses": stop_losses,
            "exit_points": exit_points,
            "hold_durations": hold_durations,
            "raw_text": plan_text
        }
    
    async def execute_trade(self, plan_id):
        """Execute a trade based on the trading plan"""
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
            
            # Simulate trade execution
            # In a real implementation, we would use AgentKit to execute trades
            
            # Check if we have agent initialized
            if not agent_service.agent_kit:
                return {"status": "error", "message": "Agent not initialized"}
                
            # Get wallet details
            wallet_details = agent_service.get_wallet_details()
            if wallet_details["status"] == "error":
                return wallet_details
                
            parsed_plan = plan.get("parsed_plan", {})
            
            # Record execution details
            execution_details = {
                "timestamp": datetime.now().isoformat(),
                "wallet_address": wallet_details["data"]["address"],
                "network": wallet_details["data"]["network"]["network_id"],
                "trades": []
            }
            
            # Simulate trades for each pair
            for pair in parsed_plan.get("trading_pairs", []):
                trade = {
                    "pair": pair,
                    "position_size": parsed_plan.get("max_positions", {}).get(pair, "Unknown"),
                    "entry_time": datetime.now().isoformat(),
                    "status": "opened",
                    "tx_hash": f"0x{os.urandom(32).hex()}"  # Simulated transaction hash
                }
                
                execution_details["trades"].append(trade)
                
                # Add to active positions
                self.active_positions.append({
                    "plan_id": plan_id,
                    "pair": pair,
                    "entry_time": datetime.now().isoformat(),
                    "position_size": parsed_plan.get("max_positions", {}).get(pair, 0),
                    "stop_loss": parsed_plan.get("stop_losses", {}).get(pair, "Unknown"),
                    "exit_point": parsed_plan.get("exit_points", {}).get(pair, "Unknown"),
                    "status": "active"
                })
            
            # Mark plan as executed
            plan["executed"] = True
            plan["execution_timestamp"] = datetime.now().isoformat()
            plan["execution_details"] = execution_details
            self.save_data()
            
            return {
                "status": "success",
                "message": "Trading plan executed successfully",
                "plan_id": plan_id,
                "execution_details": execution_details
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_active_positions(self):
        """Get all active trading positions"""
        return {
            "status": "success",
            "active_positions": self.active_positions
        }
    
    async def get_trade_history(self):
        """Get trading history"""
        return {
            "status": "success",
            "trade_history": self.trade_history
        }

# Create a single instance to be used throughout the application
trading_agent_service = TradingAgentService()