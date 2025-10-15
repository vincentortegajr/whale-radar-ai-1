# 🐋 WhaleRadar.ai - The Ultimate Crypto Trading Indicator Platform

> **The $900/month CoinGlass Pro API Beast Mode System**
> 
> Visual Screeners + Liquidation Heatmaps + RSI Analysis = The Triple Threat

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

1. **API Limits**: CoinGlass Pro allows 10 calls/second, 600/minute
2. **Scan Interval**: 1-5 minutes recommended for best results
3. **Position Sizing**: Always use proper risk management
4. **Market Hours**: Crypto trades 24/7, ensure system uptime

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

**Remember**: You're not just trading. You're hunting with the whales. 🐋

*"Nobody else has combined these indicators into ONE system. This changes EVERYTHING."*