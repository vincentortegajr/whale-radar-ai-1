# 🐋 WHALERADAR.AI - CLAUDE CONTEXT & ORACLE DEV BLUEPRINT
## THE $900/MONTH COINGLASS PRO API BEAST MODE SYSTEM

---

## 🎯 DIVINE ARCHITECT MISSION STATEMENT

You are building **WhaleRadar.ai** - the world's most accurate crypto trading indicator platform that combines Visual Screeners + Liquidation Heatmaps + RSI Analysis into ONE UNIFIED SYSTEM. This isn't just another indicator - it's a complete trading intelligence system that follows where whales hunt liquidations.

**Core Philosophy**: "Follow the Liquidations, Not the Price" - Whales move markets to hunt liquidation levels. We identify where they're going next.

---

## 🚀 PROJECT OVERVIEW & CURRENT STATE

### What We've Built (Phase 1 - COMPLETE ✅)
1. **Visual Screener Integration** - All 3 types working (Price vs OI, Price vs Volume, Volume vs OI)
2. **Liquidation Heatmap Analysis** - Model 2 integration with multi-timeframe analysis
3. **RSI Multi-Timeframe Confirmation** - 5m to 1w confluence checking
4. **Master Strategy Combiner** - Generates signals when all indicators align
5. **Telegram Alert System** - Rich formatted notifications with all metrics

### Current Architecture
```
whale-radar-ai-1/
├── src/
│   ├── indicators/          # Core analysis modules
│   │   ├── visual_screener.py      # Triple screener analysis
│   │   ├── liquidation_analyzer.py # Whale hunting zones
│   │   └── rsi_heatmap.py         # RSI confluence
│   ├── api/
│   │   ├── coinglass_client.py    # $900/month Pro API
│   │   └── telegram_bot.py        # Alert notifications
│   ├── strategies/
│   │   └── master_strategy.py     # Signal generation
│   └── main.py                    # Application entry
```

---

## 🔑 ACTIVE CREDENTIALS & CONFIGURATION

```python
# CoinGlass Pro API ($900/month tier)
COINGLASS_API_KEY = "0e0cdf60bc4745aeb7e14532704f8a57"
COINGLASS_BASE_URL = "https://open-api-v4.coinglass.com"

# Telegram Bot (Active and Working)
TELEGRAM_BOT_TOKEN = "7962125603:AAGjbdOc4knxFI-ed2s9PaMs8GngXrsRv68"
TELEGRAM_CHAT_ID = "722324078"

# Bybit (Phase 3 - Ready for Auto-Trading)
BYBIT_API_KEY = "cPknlvGxnxsRd1nXav"
BYBIT_SECRET = "iTlBxV6XJMwcy0lgMhwRqJwb4Ji7t7CA1Xid"
BYBIT_TESTNET = true
```

---

## 🚨 CRITICAL: ALWAYS VERIFY ENDPOINTS WITH OFFICIAL DOCS

⚠️ **IMPORTANT**: CoinGlass API endpoints change frequently. ALWAYS cross-check with the latest documentation at https://docs.coinglass.com/ before implementing any endpoint. The endpoints below are verified as of the last update but may change.

---

## 📊 COINGLASS PRO API ENDPOINTS IN USE

### Base URL & Authentication
```
Base URL: https://open-api-v4.coinglass.com
Header Name: CG-API-KEY
Header Format: { "accept": "application/json", "CG-API-KEY": "your-api-key" }
```

### ⚠️ API Version Note
CoinGlass has multiple API versions:
- **v1 PRO API**: https://api.coinglass.com/api/pro/v1 (OLD - DO NOT USE)
- **v4 Open API**: https://open-api-v4.coinglass.com (CURRENT - USE THIS)

### Visual Screener Endpoints (IMPLEMENTED ✅)
```python
GET /api/futures/coins/markets
# Params: timeframe (5m, 15m, 1h, etc.)
# Returns: Price change %, Volume change %, OI change %
# Status: ✅ VERIFIED & WORKING (897 coins)
```

### Liquidation Heatmap Endpoints (IMPLEMENTED ✅)
```python
GET /api/futures/liquidation/aggregated-heatmap/model2
# Required params: symbol, range (12h, 24h, 3d, 7d, 30d, 1y)
# Returns: Liquidation clusters by price level
# Status: ✅ VERIFIED & WORKING
```

### RSI Heatmap Endpoints (IMPLEMENTED ✅)
```python
GET /api/futures/rsi/list
# Params: interval (5m, 15m, 1h, 4h, 12h, 1d, 1w), limit
# Returns: RSI values for all coins
# Status: ✅ VERIFIED & WORKING
```

### Future Endpoints (Phase 2)
```python
GET /api/futures/hyperliquid/whale-alert  # Large position alerts
GET /api/onchain/inflow-outflow/{coin}   # Exchange flows
GET /api/futures/open-interest/history    # OI trends
```

---

## 🎯 CORE ALGORITHMS & LOGIC

### 1. THE TRIPLE THREAT SIGNAL GENERATION
```python
def generate_master_signal(coin):
    # Step 1: Visual Screener Analysis
    momentum_score = analyze_visual_screeners(coin)
    # Price change + Volume spike + OI change = Momentum 0-100
    
    # Step 2: Liquidation Analysis  
    direction, scale_zones = analyze_liquidations(coin)
    # Find where shorts > longs * 1.5 = UP
    # Find where longs > shorts * 1.5 = DOWN
    
    # Step 3: RSI Confirmation
    confidence = confirm_with_rsi(coin, direction)
    # Oversold + UP direction = HIGH confidence
    # Overbought + DOWN direction = HIGH confidence
    
    # Signal only if:
    # - Momentum > 70
    # - Liquidations confirm direction
    # - RSI aligns
    return signal
```

### 2. SCALE-IN ZONE CALCULATION
```python
def calculate_scale_zones(liquidation_clusters, current_price):
    # Identify major liquidation levels
    # Distribute position: [30%, 30%, 25%, 15%]
    # Stop loss: Beyond last major cluster
    # Take profit: At opposite liquidation clusters
```

### 3. ALERT CRITERIA
- Scan every 1-5 minutes (while others scan at 15)
- Only alert on HIGH/MEDIUM confidence
- Signal strength must be >= 60/100
- Must have clear liquidation direction

---

## 🚨 CRITICAL IMPLEMENTATION NOTES

### What Makes This Different
1. **Aggregated Data** - ALL exchanges, not single exchange
2. **Model 2 Liquidations** - Most accurate for whale hunting
3. **Multi-Timeframe** - 12h to 1y liquidation analysis
4. **Scale Trading** - Never get stopped out with distributed entries
5. **Speed** - 1-5 minute alerts vs 15 minute competition

### Risk Management Built-In
- Scale-in zones prevent all-in mistakes
- Stop loss beyond liquidation clusters
- Multiple take profit targets
- Position sizing recommendations

### Performance Targets
- Signal Accuracy: >80%
- False Positive Rate: <10%
- Alert Latency: <60 seconds
- Profitable Signals: >70%

---

## 🔮 DEVELOPMENT ROADMAP

### Phase 1 ✅ COMPLETE (Current)
- [x] Visual Screeners Integration
- [x] Liquidation Heatmap Model 2
- [x] RSI Multi-Timeframe Analysis
- [x] Telegram Alert System
- [x] Master Strategy Combiner
- [x] Deep Liquidation Analyzer (NEW!)
- [x] Comprehensive Reporter (NEW!)

### Phase 1.5 🆕 COMPREHENSIVE ANALYSIS (COMPLETE)
- [x] Top 10 Visual Screener Deep Analysis
- [x] ALL Timeframe Liquidation Levels (12h to 1y)
- [x] Liquidation Imbalance Scoring
- [x] RSI Extreme Verification with Liquidations
- [x] RSI Neutral Zone Exclusion (45-55) for API optimization
- [x] Whale Target Predictions
- [x] Referral Links Integration (CoinGlass & Bybit)

### Phase 2 🔄 IN PROGRESS
- [ ] Whale Alert Integration (Large transfers)
- [ ] On-chain Flow Analysis (Exchange in/outflows)
- [ ] Hyper Liquid Whale Tracking
- [ ] Enhanced filtering for false positives

### Phase 3 📅 PLANNED
- [ ] Bybit Auto-Trading Integration
- [ ] Position Management System
- [ ] Risk Calculator with Kelly Criterion
- [ ] Performance Analytics Dashboard

### Phase 4 🚀 FUTURE VISION
- [ ] Machine Learning Pattern Recognition
- [ ] Cross-Exchange Arbitrage Detection
- [ ] AI-Powered Signal Optimization
- [ ] Mobile App with Push Notifications

---

## 💻 QUICK DEVELOPMENT COMMANDS

```bash
# Run the main scanner
cd /Users/vincentortegajr/whale-radar-ai-1
python -m src.main

# Run COMPREHENSIVE deep analysis (NEW!)
python -m src.comprehensive_scanner        # Continuous scanning
python -m src.comprehensive_scanner --once # Run once and exit
python -m src.comprehensive_scanner --sample # Show sample report

# Test individual components
python -m src.indicators.visual_screener
python -m src.indicators.liquidation_analyzer
python -m src.indicators.rsi_heatmap
python -m src.indicators.deep_liquidation_analyzer

# Check logs
tail -f logs/whaleradar_*.log

# Run tests
python test_complete_system.py

# Git workflow
git add -A && git commit -m "🐋 Update message" && git push

# Install new dependencies
pip install package_name && pip freeze > requirements.txt
```

---

## 🎯 VINCENT'S VISION ALIGNMENT

This platform embodies the Oracle Dev standard:
- **Revenue Focused** - Every signal drives toward profit
- **Production Grade** - No TODOs, no placeholders
- **Beast Mode** - Using $900/month Pro API to fullest
- **First Principles** - Follow liquidations, not opinions
- **Scale Empire** - Built for billions, not thousands

**Key Differentiators**:
1. Nobody else combines these 3 indicators
2. Nobody else watches liquidation levels like this
3. Nobody else gives 1-5 minute alerts
4. Nobody else scales orders across liquidation zones

---

## 📱 TELEGRAM ALERT FORMAT EXAMPLE

```
🐋 WHALE RADAR ALERT 🎯

🟢 $BTC - LONG SIGNAL
━━━━━━━━━━━━━━━━━━━━━
📊 MOMENTUM INDICATORS:
• Price Change: +3.2%
• Volume Spike: +472%
• Open Interest: +25%
• Momentum Score: 85/100

💧 LIQUIDATION ANALYSIS:
• Direction: UP (Hunting Shorts)
• Short Liquidations: $847M @ $44,800
• Long Liquidations: $234M @ $41,200
• Risk/Reward: 3.6:1

📈 RSI CONFIRMATION:
• 5m RSI: 42 (Neutral)
• 1h RSI: 31 (Oversold)
• 4h RSI: 28 (Oversold)
• 1d RSI: 35 (Oversold)

🎯 SCALE-IN ZONES:
• Entry 1: $43,250 (20%)
• Entry 2: $43,100 (30%)
• Entry 3: $42,950 (30%)
• Entry 4: $42,800 (20%)
• Stop Loss: $41,900

🐳 WHALE ACTIVITY:
• Large Buy Orders: 3
• Hyperliquid: $12M Long Added
• Exchange Outflow: +2,341 BTC

📊 QUICK LINKS:
[View Liquidation Map]
[View Visual Screener]
[Trade on Bybit]

⚡ Alert Time: 13:42:15 UTC
━━━━━━━━━━━━━━━━━━━━━
```

---

## 🚨 ACTIVE DEVELOPMENT PRIORITIES

1. **Immediate** - Verify all endpoints with https://docs.coinglass.com/
2. **This Week** - Add whale alert integration
3. **Next Week** - Implement on-chain flow analysis
4. **This Month** - Launch auto-trading beta

---

## 📝 ORACLE DEV STANDARDS FOR THIS PROJECT

1. **ALWAYS** verify API endpoints with official docs first
2. **ALWAYS** use the liquidation data to confirm direction
3. **NEVER** signal without triple confirmation
4. **SCALE** orders across zones - never all-in
5. **SPEED** matters - 1-5 minute scans only
6. **VISUAL** proof via screenshots when debugging
7. **REVENUE** focus - every feature must drive profit

---

## 💡 KEY TECHNICAL ARCHITECTURE

### API Client Design
- **Async First**: Uses `aiohttp` for concurrent requests
- **Retry Logic**: Exponential backoff with max 3 retries
- **Rate Limiting**: Respects 10 calls/sec, 600/min limits
- **Circuit Breaker**: Prevents cascade failures
- **Performance Monitoring**: Built-in metrics collection

### Data Processing Pipeline
```python
Raw API Data → Validation (Pydantic) → Analysis → Signal Generation → Alerts
     ↓              ↓                      ↓            ↓              ↓
   Cache         Database              Indicators    Strategy      Telegram
```

### Position Sizing Algorithm
```python
# Scale-in distribution for different entry counts
1 entry:  [100%]
2 entries: [60%, 40%]
3 entries: [40%, 35%, 25%]
4 entries: [30%, 30%, 25%, 15%]
5+ entries: Even distribution with slight front-loading
```

### Signal Strength Calculation
```python
Base Score = 50
+ Visual Screener Impact (±20 points)
+ Volume Spike Bonus (±20 points)  
+ OI Change Impact (±10 points)
+ Confluence Bonus (±10 points)
+ Liquidation Confirmation (±30 points)
+ RSI Alignment (±20 points)
= Final Score (0-100)
```

---

## 🛠️ CURRENT IMPLEMENTATION STATUS

### ✅ Phase 1 Complete (100% Working)
- Visual Screener Integration (3 types)
- Liquidation Heatmap Model 2
- RSI Multi-timeframe Analysis  
- Master Strategy Signal Generation
- Telegram Rich Notifications
- Database Operations
- Error Handling & Recovery
- Performance Monitoring

### 🔄 Active Development
- Whale Alert Integration
- On-chain Flow Analysis
- Enhanced False Positive Filtering
- Production Deployment Scripts

### 📊 Latest Test Results
```
✅ API Auth: CG-API-KEY header working
✅ Endpoints: All v4 endpoints verified
✅ Data: 897 perpetual coins available
✅ Signals: Generation working with scale zones
✅ Alerts: 970 char Telegram messages formatted
✅ Performance: <60s latency, 31% CPU, 36% RAM
✅ Accuracy: Mathematical calculations verified
✅ Reliability: Graceful error handling active
```

---

## 🔥 THE BOTTOM LINE

You're building the Bloomberg Terminal of crypto liquidations. This isn't about price prediction - it's about following whale footprints through liquidation data. When Visual Screeners show momentum, Liquidations show direction, and RSI confirms - that's when we strike.

**Remember**: 
- The whales always hunt the liquidations
- We just follow their trail
- Set it and forget it
- Scale across liquidations
- Never get stopped out again

---

## 📞 QUICK REFERENCE

```python
# Credentials (Active & Working)
COINGLASS_API_KEY = "0e0cdf60bc4745aeb7e14532704f8a57"
TELEGRAM_BOT_TOKEN = "7962125603:AAGjbdOc4knxFI-ed2s9PaMs8GngXrsRv68"
TELEGRAM_CHAT_ID = "722324078"

# Key Files
Main App: src/main.py
Visual Screener: src/indicators/visual_screener.py
Liquidations: src/indicators/liquidation_analyzer.py
Master Strategy: src/strategies/master_strategy.py

# Quick Commands
Run: python -m src.main
Test: python test_complete_system.py
Logs: tail -f logs/whaleradar_*.log
```

---

*Last Updated: [Current Date]*  
*Maintained by: Vincent Ortega Jr - The Oracle Dev*  
*Target: $1B+ Trading Platform*

"Nobody else has combined these indicators into ONE system. This changes EVERYTHING."