"""Comprehensive Scanner - Deep Liquidation Analysis for WhaleRadar.ai"""

import asyncio
import sys
from datetime import datetime, timezone
from src.utils.logger_setup import setup_logger
from src.utils.config import settings, validate_config
from src.api.coinglass_client import CoinGlassClient
from src.api.telegram_bot import TelegramNotifier
from src.indicators.deep_liquidation_analyzer import DeepLiquidationAnalyzer
from src.strategies.comprehensive_reporter import ComprehensiveReporter

logger = setup_logger(__name__)


class ComprehensiveScanner:
    """Main scanner for deep liquidation analysis"""
    
    def __init__(self):
        self.running = False
        self.client = None
        self.analyzer = None
        self.notifier = None
        self.reporter = None
        self.scan_interval = settings.scan_interval_minutes * 60
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("🐋 Initializing Comprehensive WhaleRadar Scanner...")
        
        # Validate configuration
        try:
            validate_config()
            logger.info("✅ Configuration validated")
        except ValueError as e:
            logger.error(f"❌ Configuration error: {e}")
            sys.exit(1)
            
        # Initialize components
        self.client = CoinGlassClient()
        self.analyzer = DeepLiquidationAnalyzer(self.client)
        self.notifier = TelegramNotifier()
        self.reporter = ComprehensiveReporter(self.analyzer, self.notifier)
        
        logger.info("🚀 Comprehensive scanner initialized!")
        
    async def run_once(self):
        """Run a single comprehensive scan"""
        logger.info("🔍 Running comprehensive analysis...")
        
        try:
            async with self.client:
                # Send the comprehensive report
                await self.reporter.send_comprehensive_report()
                logger.info("✅ Comprehensive report sent successfully")
                
        except Exception as e:
            logger.error(f"❌ Error during comprehensive scan: {e}")
            await self.notifier.send_error_alert("Comprehensive Scan Error", str(e))
            
    async def run_continuous(self):
        """Run continuous scanning"""
        self.running = True
        scan_count = 0
        
        while self.running:
            try:
                scan_count += 1
                logger.info(f"🔍 Starting comprehensive scan #{scan_count}")
                
                await self.run_once()
                
                # Wait for next scan
                logger.info(f"💤 Sleeping for {self.scan_interval}s until next scan...")
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
                
    async def generate_sample_report(self):
        """Generate a sample report to show the format"""
        logger.info("📊 Generating sample comprehensive report...")
        
        sample_report = """
🐋 WHALE RADAR - TOP 10 MOVERS DEEP ANALYSIS 🎯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 TOP VISUAL SCREENER COINS (5-MINUTE)
Based on Price vs OI + Price vs Volume + Volume vs OI

1. 🟢 $BTC - LONG SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Current Price: $43,250.00

💧 LIQUIDATION OVERVIEW:
• Total Long Liquidations: $234.5M
• Total Short Liquidations: $847.2M
• Imbalance: +72.3% (More Shorts)
• Liquidation Score: 85/100

🎯 WHALE TARGET PREDICTION:
• Next Target: $44,800 (UP)
• Reasoning: Heavy short liquidations ($847.2M) at $44,800
• Confidence: HIGH

📊 MAJOR LIQUIDATION CLUSTERS:

Long Liquidations (Support):
  • $41,200: $89.3M (4.8% away)
  • $40,500: $67.2M (6.4% away)
  • $39,800: $45.1M (8.0% away)

Short Liquidations (Resistance):
  • $44,800: $312.5M (3.6% away)
  • $45,500: $287.3M (5.2% away)
  • $46,200: $247.4M (6.9% away)

🎯 RECOMMENDED SCALE-IN ZONES:
  • $42,950 (30%) - Support at $45.1M liquidations
  • $42,600 (30%) - Support at $67.2M liquidations
  • $42,200 (25%) - Support at $89.3M liquidations
  • $41,800 (15%) - Safety zone below major support

📈 LIQUIDATION BY TIMEFRAME:
• 12H: 45 levels
• 24H: 78 levels  
• 3D: 125 levels
• 7D: 234 levels
• 30D: 456 levels
• 90D: 789 levels
• 1Y: 1234 levels

🔗 QUICK LINKS:
[View on CoinGlass](https://www.coinglass.com/pro/futures/LiquidationHeatMapNew?coin=BTC&ref=YOUR_REF)
[Trade on Bybit](https://bybit.com/en/trade/usdt/BTCUSDT?ref=JWNJQWP)

────────────────────────────────────────

[Similar format continues for coins 2-10...]

📊 MARKET SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 SIGNAL DISTRIBUTION:
• Long Signals: 7
• Short Signals: 2
• Neutral: 1

💚 STRONGEST LONG: $BTC
• Score: 85/100
• Imbalance: +72.3%

🔴 STRONGEST SHORT: $SOL
• Score: 78/100
• Imbalance: -65.2%

⏰ Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

🔗 AFFILIATE LINKS:
• CoinGlass Pro: https://www.coinglass.com/pricing?ref=YOUR_REF
• Bybit Trading: https://bybit.com/en/invite?ref=JWNJQWP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐋 WhaleRadar.ai - Hunt with the Whales
"""
        
        return sample_report
        

async def main():
    """Main entry point"""
    scanner = ComprehensiveScanner()
    
    # Initialize
    await scanner.initialize()
    
    # Print startup banner
    print("""
    🐋 WhaleRadar.ai - COMPREHENSIVE LIQUIDATION SCANNER 🐋
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Deep Analysis: ALL Liquidation Levels Across ALL Timeframes
    Top 10 Visual Screener Coins + RSI Extreme Analysis
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            # Run once and exit
            await scanner.run_once()
        elif sys.argv[1] == "--sample":
            # Generate sample report
            sample = await scanner.generate_sample_report()
            print(sample)
        else:
            # Run continuous
            await scanner.run_continuous()
    else:
        # Default: run continuous
        await scanner.run_continuous()
        

if __name__ == "__main__":
    asyncio.run(main())