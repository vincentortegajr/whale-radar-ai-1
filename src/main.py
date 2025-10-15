"""WhaleRadar.ai - Main Application Entry Point"""

import asyncio
import signal
import sys
from datetime import datetime, timezone
from typing import List
from src.utils.logger_setup import setup_logger
from src.utils.config import settings, validate_config
from src.api.coinglass_client import CoinGlassClient
from src.api.telegram_bot import TelegramNotifier
from src.strategies.master_strategy import MasterStrategy, MasterSignal

logger = setup_logger(__name__)


class WhaleRadar:
    """Main application class for WhaleRadar.ai"""
    
    def __init__(self):
        self.running = False
        self.strategy = None
        self.notifier = None
        self.scan_interval = settings.scan_interval_minutes * 60  # Convert to seconds
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("🐋 Initializing WhaleRadar.ai...")
        
        # Validate configuration
        try:
            validate_config()
            logger.info("✅ Configuration validated")
        except ValueError as e:
            logger.error(f"❌ Configuration error: {e}")
            sys.exit(1)
            
        # Initialize components
        self.strategy = MasterStrategy()
        self.notifier = TelegramNotifier()
        
        # Test connections
        await self._test_connections()
        
        logger.info("🚀 WhaleRadar.ai initialized successfully!")
        
    async def _test_connections(self):
        """Test API connections"""
        logger.info("Testing connections...")
        
        # Test CoinGlass API
        async with self.strategy.client as client:
            try:
                symbols = await client.get_perpetual_symbols()
                logger.info(f"✅ CoinGlass API connected - {len(symbols)} perpetuals available")
            except Exception as e:
                logger.error(f"❌ CoinGlass API error: {e}")
                sys.exit(1)
                
        # Test Telegram
        try:
            await self.notifier.bot.send_message(
                chat_id=self.notifier.chat_id,
                text="🐋 WhaleRadar.ai is starting up! 🚀"
            )
            logger.info("✅ Telegram connected")
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
            sys.exit(1)
            
    async def run(self):
        """Main application loop"""
        self.running = True
        logger.info("Starting main scanning loop...")
        
        scan_count = 0
        
        while self.running:
            try:
                scan_count += 1
                logger.info(f"🔍 Starting scan #{scan_count}")
                
                # Run market scan
                signals = await self._scan_market()
                
                if signals:
                    logger.info(f"📊 Found {len(signals)} signals")
                    # Send alerts
                    await self.notifier.send_batch_alerts(signals)
                else:
                    logger.info("No strong signals found this scan")
                    
                # Clean up old alerts
                self.notifier.cleanup_old_alerts()
                
                # Wait for next scan
                logger.info(f"💤 Sleeping for {self.scan_interval}s until next scan...")
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await self.notifier.send_error_alert("Main Loop Error", str(e))
                await asyncio.sleep(60)  # Wait 1 minute before retry
                
    async def _scan_market(self) -> List[MasterSignal]:
        """Perform market scan"""
        async with self.strategy.client:
            # Get top signals
            signals = await self.strategy.scan_market(top_n=10)
            
            # Filter for high confidence only
            high_confidence_signals = [
                s for s in signals 
                if s.confidence in ["HIGH", "MEDIUM"] and s.signal_strength >= 60
            ]
            
            return high_confidence_signals
            
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down WhaleRadar.ai...")
        self.running = False
        
        # Send shutdown notification
        try:
            await self.notifier.bot.send_message(
                chat_id=self.notifier.chat_id,
                text="🛑 WhaleRadar.ai is shutting down for maintenance."
            )
        except:
            pass
            
        logger.info("👋 Shutdown complete")
        

async def main():
    """Main entry point"""
    # Create application instance
    app = WhaleRadar()
    
    # Initialize
    await app.initialize()
    
    # Set up signal handlers
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        asyncio.create_task(app.shutdown())
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run application
    try:
        await app.run()
    except KeyboardInterrupt:
        await app.shutdown()
        

if __name__ == "__main__":
    # Print startup banner
    print("""
    🐋 WhaleRadar.ai - $900/month CoinGlass Pro Beast Mode 🐋
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Visual Screeners + Liquidation Heatmaps + RSI Analysis
    The Triple Threat Indicator System
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    # Run the application
    asyncio.run(main())