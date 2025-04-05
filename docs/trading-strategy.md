![github banner (4)](https://github.com/user-attachments/assets/ec50f8d6-d1d7-4186-a5fa-612d2a0b258e)

This strategy leverages four major Token Metrics API endpoints to create a **short-term crypto trading strategy**. The goal is to allocate a specified `idle_funds_amount` across the **top 3 scoring tokens** and generate specific **entry**, **exit**, and **stop-loss** parameters for each token.

### Key Components:
1. **Market Metrics**: Provides overall market sentiment (bullish, bearish, or neutral).
2. **Hourly OHLCV**: Provides hourly price data used to calculate technical indicators.
3. **Trader Grades**: AI-generated short-term grade for each token.
4. **Trading Signals**: Proprietary buy/sell signals from the Token Metrics AI model.

---

## 2. API Endpoints in Detail

### 2.1 Market Metrics Endpoint
```python
market_data = await token_metrics_service.client.market_metrics.get_dataframe(
    startDate=start_date,
    endDate=end_date
)
```
Retrieves a DataFrame containing daily or near-daily metrics for the entire crypto market.

#### Key Columns:
- **MARKET_SENTIMENT_GRADE**: Numeric sentiment gauge (0–100).
- **MARKET_SENTIMENT_LABEL**: Sentiment label ("bullish", "bearish", "neutral").
- **LAST_TM_GRADE_SIGNAL**: Final integer signal for the overall market (1 = bullish, -1 = bearish, 0 = neutral).
- **DATE**: Date of the record.

#### Usage:
The latest row is checked to determine the market's sentiment:
- **Bullish** (`last_signal = 1`)
- **Bearish** (`last_signal = -1`)
- **Neutral** (`last_signal = 0`)

An adjustment factor of **+10%** (for bullish) or **-10%** (for bearish) is applied to each token's score based on the overall market sentiment.

---

### 2.2 Hourly OHLCV Endpoint
```python
hourly_data = await token_metrics_service.client.hourly_ohlcv.get_dataframe(
    symbol=symbol.lower(),
    startDate=(datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
    endDate=end_date
)
```
Returns hourly candles (Open, High, Low, Close, Volume) for a given token.

#### Key Columns:
- **DATE** or **TIMESTAMP**
- **OPEN**, **HIGH**, **LOW**, **CLOSE**, **VOLUME**

#### Usage:
Recent hourly data (last 3 days) is used to calculate key technical indicators:
- **Exponential Moving Averages (EMA) 20 & 50**: Trend indicators.
- **Relative Strength Index (RSI) 14**: Overbought/Oversold conditions.

If `hourly_data` is empty for a token, it is skipped. The **latest close** price is also stored as the `latest_price` for the token.

---

### 2.3 Trader Grades Endpoint
```python
trader_grades = await token_metrics_service.client.trader_grades.get_dataframe(
    symbol=symbol.lower(),
    startDate=start_date,
    endDate=end_date
)
```
Provides the Token Metrics AI-generated short-term grade for each token (0–100 scale).

#### Key Column:
- **TM_TRADER_GRADE**: The short-term trader grade.

#### Usage:
The **latest TM_TRADER_GRADE** value is used to represent how bullish or bearish the AI model is for the token in the short-term. If no data is available, the default grade is set to **50** (neutral).

---

### 2.4 Trading Signals Endpoint
```python
trading_signals = await token_metrics_service.client.trading_signals.get_dataframe(
    symbol=symbol.lower(),
    startDate=start_date,
    endDate=end_date
)
```
Returns buy/sell signals (bullish, bearish, or none) from Token Metrics' proprietary model.

#### Key Column:
- **TRADING_SIGNAL**: The final signal (1 = bullish, -1 = bearish, 0 = none).

#### Usage:
The **last trading signal** for a given token is checked and incorporated into the final scoring model.

---

## 3. Final Composite Score Formula

The core formula to calculate the composite score for each token is as follows:

```text
core_score = (
    (Trader_Grade * 0.4) +
    (((TM_Signal * 25) + 50) * 0.3) +
    (((EMA_Signal * 25) + 50) * 0.2) +
    ((50 - abs(RSI - 50)) * 0.1)
)
```

### Components:
- **Trader Grade** (40% weight): The raw scale (0–100) directly from the **Trader Grades** endpoint.
- **TM Trading Signal** (30% weight): Mapped from -1 → 25, +1 → 75, then adjusted with a +50 offset.
- **EMA Crossover** (20% weight): Similar to TM Signal, but based on the **EMA 20 & 50** crossovers.
- **RSI** (10% weight): Calculated as `(50 - abs(RSI - 50))`, where the ideal value is 50.

#### Example Calculation:
- If **RSI** = 50: `50 - abs(50 - 50)` = 50
- If **RSI** = 30: `50 - abs(30 - 50)` = 30
- If **RSI** = 70: `50 - abs(70 - 50)` = 30

---

## 4. Strategy Implementation

1. **Pull Market Metrics**: Adjust token scores based on market sentiment.
2. **For Each Token**:
   - Retrieve **Trader Grade**, **Trading Signals**, and **Hourly OHLCV** data.
   - Compute technical indicators like **EMA** and **RSI**.
   - Calculate the **final composite score**.
3. **Rank Tokens**: Rank the tokens based on their final score.
4. **Allocate Funds**: Distribute `idle_funds_amount` across the **top 3 tokens**.
5. **Generate Trade Plan**:
   - **Entry Price**: The latest closing price.
   - **Exit Target**: Typically a **+5% to +15%** price movement.
   - **Stop-Loss**: Usually a **-3% to -7%** risk based on RSI levels.

---

## 5. Example Output (JSON)

```json
[
  {
    "token": "BTC",
    "score": 88.5,
    "allocation": 0.4,
    "entry_price": 45000,
    "target_price": 48500,
    "stop_loss": 43000
  },
  {
    "token": "ETH",
    "score": 85.7,
    "allocation": 0.3,
    "entry_price": 3500,
    "target_price": 3800,
    "stop_loss": 3350
  },
  {
    "token": "SOL",
    "score": 82.3,
    "allocation": 0.3,
    "entry_price": 120,
    "target_price": 135,
    "stop_loss": 115
  }
]
```

---

## 6. Notes and Potential Enhancements
- **Risk Management**: Consider implementing dynamic stop-loss based on volatility.
- **Portfolio Constraints**: Adjust for specific asset restrictions (e.g., excluding certain tokens).
- **Position Sizing**: Modify allocation based on confidence score (e.g., higher confidence = larger allocation).
