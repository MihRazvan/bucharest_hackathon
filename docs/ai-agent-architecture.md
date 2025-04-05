![github banner (3)](https://github.com/user-attachments/assets/623077c0-9cb8-4b03-88c8-e009895107b6)

Below you can find the AI engine powering Pipe It!!'s yield strategy leverages multi-factor signals, market sentiment, and technical analysis to build and execute optimal trades on idle funds.

---

## Core AI Agents

### 1. TokenMetricsService

Fetches market intelligence data:
- `get_token_info()` – Token fundamentals
- `get_trader_grades()` – Quantitative + technical + TA scores
- `get_market_sentiment()` – Overall market trend
- `get_market_metrics()` – Composite metrics

Used by trading and rate agents to derive decisions.

---

### 2. TradingAgentService

Uses AI + market data to generate and execute trading plans.

#### Key Capabilities:
- `generate_advanced_trading_plan()` – Merges data into actionable plans
- `execute_trade()` – Simulates real trades (agent-ready)
- `backtest_strategy()` – Historical testing with performance metrics
- `get_performance_stats()` – ROI, win rate, volatility metrics

#### Strategy Algorithm:
- **Scoring Model**:
  - Trader grades + sentiment + technicals
- **Market Sentiment Adjustment**:
  - Adjusts position size and risk dynamically
- **Signal Confirmation**:
  - Only high-confidence trades executed
- **Dynamic Allocation**:
  - Diversified position sizing based on strength

---

### 3. RateAgentService

Uses sentiment data to personalize factoring offers.

#### Core Logic:
- Bullish market = lower fees, higher advance %
- Bearish market = higher fees, lower advance %
- `get_recommended_rates()` returns a min-max fee and advance range

---

### 4. VaultService

Smart contract interface for deposits, withdrawals, share tracking.

- `deposit()` → Sends ETH to the vault
- `withdraw()` → Redeems shares
- `get_balance()` → Share ownership
- `get_vault_stats()` → Vault TVL, performance, yield data

---

### 5. AgentService

Built on Coinbase AgentKit

- Wallet management
- Simulated trading via DEXes
- Testnet + mainnet supported

---

## Trading Flow Overview

1. **Detect Idle Capital**
2. **Generate Plan**: 
   - `generate_advanced_trading_plan()` uses:
     - `trader_grades` for token selection
     - `market_sentiment` for sizing
     - `trading_signals` for entry/exit
3. **Score Tokens**: Normalize & weigh grades
4. **Allocate Portfolio**: Risk-adjusted weight
5. **Simulate or Execute Trades**:
   - Simulated via `execute_trade()` or on-chain via `AgentKit`
6. **Report Profits**: Smart contract updates vault TVL

---

## Backtesting Agent

- `backtest_strategy()` runs a dry test of AI strategies
- Pulls historical data from Token Metrics:
  - Price OHLCV
  - Historical trader grades
  - Historical sentiment
- Calculates:
  - Profit & loss
  - Win rate
  - Max drawdown
- Helps tune hyperparameters & weights

---

## API Dependencies

| Feature              | API Endpoint Used                |
|----------------------|----------------------------------|
| Market Analysis      | `/market_metrics`                |
| Token Selection      | `/tokens`, `/trader_grades`      |
| Signal Confirmation  | `/trading_signals`               |
| Risk Management      | `TA_GRADE` from `/trader_grades` |
| Rate Adjustment      | `/market_metrics`                |

---

## Strategy Files

Plans and trade executions are stored in:
- `trading_plans/{plan_id}.json`
- Contains token list, weights, entry/exit, timestamps, and metadata.
