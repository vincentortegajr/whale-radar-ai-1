# 🐋 WhaleRadar.ai - The Ultimate Crypto Trading Indicator Platform

> **The $900/month CoinGlass Pro API Beast Mode System**
> 
> Visual Screeners + Liquidation Heatmaps + RSI Analysis = The Triple Threat

## 🚨 CRITICAL: API ENDPOINT VERIFICATION

⚠️ **IMPORTANT**: CoinGlass API endpoints change frequently. **ALWAYS** cross-check all endpoints with the official documentation at https://docs.coinglass.com/ before implementing or debugging. The endpoints in this codebase were verified at the time of development but may have changed.

## 🚀 Overview

WhaleRadar.ai is the world's most advanced crypto trading indicator platform that combines:
- **Visual Screeners** (Price vs OI, Price vs Volume, Volume vs OI)
- **Liquidation Heatmaps** (Where the whales hunt)
- **RSI Multi-Timeframe Analysis** (Confluence confirmation)
- **1-5 Minute Alerts** (While others see at 15 minutes)
- **850+ Perpetual Coins** (Complete market coverage)

## 🎯 Core Philosophy

**"Follow the Liquidations, Not the Price"**

Whales move markets to hunt liquidation levels. This platform identifies where they're going next and helps you scale into positions across liquidation zones, so you never have to guess exact prices.

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- CoinGlass Pro API ($900/month subscription)
- Telegram Bot Token
- Bybit API (for Phase 3 auto-trading)

### Installation

```bash
# Clone the repository
git clone https://github.com/vincentortegajr/whale-radar-ai-1.git
cd whale-radar-ai-1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API credentials
```

### Configuration

Edit the `.env` file with your credentials:

```env
# CoinGlass API Configuration (CORE SYSTEM)
COINGLASS_API_KEY=your_api_key_here
COINGLASS_BASE_URL=https://open-api-v4.coinglass.com

# WhaleRadar.ai Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# System Configuration
SCAN_INTERVAL_MINUTES=5  # How often to scan (1-5 recommended)
```

### Running the System

```bash
# Run the main scanner
python -m src.main

# Or run specific modules
python -m src.indicators.visual_screener  # Test visual screeners
python -m src.indicators.liquidation_analyzer  # Test liquidations

# Run complete system test
python test_complete_system.py

# Check API authentication
python test_api_auth.py

# View logs in real-time
tail -f logs/whaleradar_*.log
```

### Quick Commands Reference

```bash
# Git workflow
git add -A && git commit -m "🐋 Update message" && git push

# Update dependencies
pip install package_name && pip freeze > requirements.txt

# Run with custom scan interval
SCAN_INTERVAL_MINUTES=1 python -m src.main

# Test individual API endpoints
python test_v4_endpoints.py
```

## 📊 How It Works

### 1. Visual Screener Analysis
The system monitors three key relationships:
- **Price vs Open Interest**: Identifies accumulation/distribution
- **Price vs Volume**: Shows momentum and participation
- **Volume vs Open Interest**: Reveals positioning intent

### 2. Liquidation Heatmap Analysis
- Uses Model 2 (most accurate for whale hunting)
- Analyzes multiple timeframes (12h, 24h, 3d, 7d, 30d, 1y)
- Identifies major liquidation clusters
- Determines whale hunting direction

### 3. RSI Confirmation
- Multi-timeframe analysis (5m to 1w)
- Identifies oversold/overbought conditions
- Confirms direction with confluence scoring

### 4. Signal Generation
When all three align:
- Momentum Score > 70
- Liquidation Direction Confirmed
- RSI Confluence > 60
= **HIGH CONFIDENCE SIGNAL**

## 📱 Telegram Alerts

Rich formatted alerts include:
- Coin symbol and action (LONG/SHORT)
- All three indicator readings
- Scale-in zones with position sizing
- Stop loss and take profit levels
- Direct links to charts and trading
- Signal strength and confidence

Example alert:
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
• Short Liquidations: $847M
• Risk/Reward: 3.6:1

🎯 SCALE-IN ZONES:
• Entry 1: $43,250 (20%)
• Entry 2: $43,100 (30%)
• Entry 3: $42,950 (30%)
• Entry 4: $42,800 (20%)
```

## 🏗️ Project Structure

```
whale-radar-ai-1/
├── src/
│   ├── indicators/       # Core indicator modules
│   ├── api/             # API clients
│   ├── strategies/      # Signal generation
│   ├── utils/          # Configuration and logging
│   └── main.py         # Application entry point
├── config/             # Configuration files
├── data/              # Database storage
├── logs/              # Application logs
├── tests/             # Unit tests
└── docs/              # Documentation
```

## 🚨 Important Notes

### API Configuration
1. **API Version**: Using CoinGlass v4 Open API (not the old v1 PRO API)
2. **Base URL**: `https://open-api-v4.coinglass.com`
3. **Auth Header**: `CG-API-KEY` (not Bearer token)
4. **Rate Limits**: 10 calls/second, 600 calls/minute
5. **Endpoint Docs**: Always verify with https://docs.coinglass.com/

### System Requirements
1. **Scan Interval**: 1-5 minutes (faster than 15-minute competition)
2. **Market Coverage**: 850+ perpetual trading pairs
3. **Data Aggregation**: Cross-exchange (not single exchange)
4. **Position Sizing**: Scale-in across liquidation zones
5. **Risk Management**: Never all-in, always use stops

### Trading Philosophy
1. **Follow Liquidations**: Whales hunt liquidation levels
2. **Triple Confirmation**: Visual + Liquidation + RSI
3. **Scale Trading**: Distribute orders across zones
4. **Set & Forget**: No constant monitoring needed
5. **Stop Hunt Protection**: Stops beyond major clusters

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black src/
flake8 src/
mypy src/
```

## 📈 Performance Metrics

- Signal Accuracy Target: >80%
- False Positive Rate: <10%
- Alert Latency: <60 seconds
- System Uptime: >99.9%
- Profitable Signals: >70%
- Risk/Reward Average: >2.5:1

## 🎯 What Makes WhaleRadar Different

### 1. **The Triple Threat Combination**
Nobody else combines Visual Screeners + Liquidation Heatmaps + RSI into ONE unified system. Each component validates the others for maximum accuracy.

### 2. **Liquidation-First Approach**
While others chase price, we follow where whales hunt liquidations. This is the REAL driver of major market moves.

### 3. **Scale-In Trading System**
Never get stopped out again. Our algorithm distributes entries across liquidation zones:
- 4 entries: [30%, 30%, 25%, 15%]
- Stop loss: Beyond major liquidation clusters
- Take profits: At opposite liquidation zones

### 4. **Speed Advantage**
- We scan every 1-5 minutes
- Competition scans every 15 minutes
- 3-15x faster signal detection

### 5. **$900/Month Pro Data**
Using CoinGlass Pro API for:
- Aggregated cross-exchange data
- 850+ perpetual pairs
- Real-time liquidation levels
- Institutional-grade accuracy

## 🔮 Roadmap

### Phase 1 ✅ (Current)
- Visual Screeners
- Liquidation Heatmaps
- RSI Analysis
- Telegram Alerts

### Phase 2 🔄 (In Progress)
- Whale Alert Integration
- On-chain Flow Analysis
- Hyper Liquid Whale Tracking

### Phase 3 📅 (Planned)
- Automated Trading via Bybit
- Portfolio Management
- Web Dashboard

### Phase 4 🚀 (Future)
- AI/ML Pattern Recognition
- Multi-Exchange Arbitrage
- Mobile App

## 🤝 Contributing

This is a private repository. Contact Vincent Ortega Jr for access.

## 📄 License

Proprietary - All Rights Reserved

## 🏆 Credits

Built by Vincent Ortega Jr
- 250,000+ customers in 150 countries
- $100M+ in online sales
- The Oracle Dev Standard

---

## 🚀 The Billion Dollar Vision

This isn't just an indicator - it's a complete trading intelligence system that:

- **Eliminates Emotional Trading**: Follow data, not feelings
- **Tracks Whale Footprints**: See where smart money is going
- **Scales Intelligently**: Never all-in, always protected
- **Beats Stop Hunts**: Stops beyond liquidation clusters
- **Generates Consistent Profits**: 70%+ profitable signals
- **Becomes THE Standard**: For crypto liquidation trading

### Why This Changes Everything

1. **First to Combine**: Visual + Liquidation + RSI in one system
2. **First to Scale**: Across liquidation zones automatically
3. **First to Alert**: In 1-5 minutes vs 15 minutes
4. **First to Aggregate**: All exchanges, not just one
5. **First to Follow**: Where whales actually hunt

### The Oracle Dev Standard

Built to Vincent Ortega Jr's specifications:
- Zero console errors
- Production-grade from line one
- Revenue-focused features only
- Built for billions, not thousands
- The standard others will copy

---

**Remember**: You're not just trading. You're hunting with the whales. 🐋

*"Nobody else has combined these indicators into ONE system. This changes EVERYTHING."*

**Target**: $1B+ Trading Platform | **Standard**: Oracle Dev Excellence