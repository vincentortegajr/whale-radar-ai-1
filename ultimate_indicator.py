#!/usr/bin/env python3
"""
WHALE RADAR AI - THE ULTIMATE INDICATOR 🐋📡
Combines all 4 steps to find where whales are hunting next
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
import json

from src.utils.logger_setup import setup_logger
from src.strategies.master_strategy import MasterStrategy
from src.api.telegram_bot import TelegramNotifier
from src.utils.database import db

logger = setup_logger(__name__)


class UltimateIndicator:
    """The Ultimate Whale Hunting System - Combines all indicators"""
    
    def __init__(self):
        self.strategy = MasterStrategy()
        self.telegram = TelegramNotifier()
        self.top_opportunities = []
        
    async def run_ultimate_analysis(self):
        """Run the complete 4-step analysis process"""
        print("="*80)
        print("🐋 WHALE RADAR AI - ULTIMATE INDICATOR SYSTEM 🐋")
        print("="*80)
        print(f"Started at: {datetime.now()}")
        print("="*80)
        
        try:
            # STEP 1: Visual Screeners - Find top movers
            print("\n📊 STEP 1: ANALYZING VISUAL SCREENERS...")
            top_movers = await self._analyze_visual_screeners()
            
            # STEP 2: Liquidation Heatmaps - Find whale hunting zones
            print("\n🎯 STEP 2: ANALYZING LIQUIDATION HEATMAPS...")
            whale_zones = await self._analyze_liquidations(top_movers)
            
            # STEP 3: RSI Heatmap - Confirm oversold/overbought
            print("\n📈 STEP 3: ANALYZING RSI HEATMAP...")
            rsi_confirmations = await self._analyze_rsi_heatmap(whale_zones)
            
            # STEP 4: Generate signals and send alerts
            print("\n🚨 STEP 4: GENERATING ULTIMATE SIGNALS...")
            signals = await self._generate_ultimate_signals(rsi_confirmations)
            
            # Send Telegram notifications for top signals
            await self._send_telegram_alerts(signals)
            
            # Display summary
            self._display_summary(signals)
            
            return signals
            
        except Exception as e:
            logger.error(f"Ultimate indicator error: {e}")
            print(f"\n❌ Error in ultimate analysis: {e}")
            return []
    
    async def _analyze_visual_screeners(self) -> List[Dict]:
        """Step 1: Find top movers from visual screeners"""
        
        # Scan top movers on multiple timeframes
        timeframes = ["5m", "15m", "1h", "4h"]
        all_movers = []
        
        for tf in timeframes:
            print(f"   Scanning {tf} timeframe...")
            movers = await self.strategy.screener.scan_top_movers(tf, top_n=20)
            
            for mover in movers:
                # Only include high momentum coins
                if mover.momentum_score > 70:
                    all_movers.append({
                        "symbol": mover.symbol,
                        "timeframe": tf,
                        "momentum_score": mover.momentum_score,
                        "price_change": mover.price_change_pct,
                        "volume_change": mover.volume_change_pct,
                        "oi_change": mover.oi_change_pct,
                        "bias": mover.bias
                    })
        
        # Sort by momentum and remove duplicates
        unique_movers = {}
        for mover in all_movers:
            symbol = mover["symbol"]
            if symbol not in unique_movers or mover["momentum_score"] > unique_movers[symbol]["momentum_score"]:
                unique_movers[symbol] = mover
        
        top_movers = sorted(unique_movers.values(), key=lambda x: x["momentum_score"], reverse=True)[:10]
        
        print(f"\n✅ Found {len(top_movers)} high-momentum coins:")
        for i, mover in enumerate(top_movers[:5]):
            print(f"   {i+1}. {mover['symbol']} - Momentum: {mover['momentum_score']}, "
                  f"Price: {mover['price_change']:.1f}%, Volume: {mover['volume_change']:.1f}%")
        
        return top_movers
    
    async def _analyze_liquidations(self, top_movers: List[Dict]) -> List[Dict]:
        """Step 2: Analyze liquidation heatmaps for whale zones"""
        
        whale_zones = []
        
        for mover in top_movers[:5]:  # Analyze top 5
            symbol = mover["symbol"]
            print(f"\n   Analyzing liquidations for {symbol}...")
            
            try:
                # Get current price (mock for now)
                current_price = await self.strategy._get_current_price(symbol)
                
                # Analyze liquidations
                liq_data = await self.strategy.liquidation.analyze_liquidations(symbol, current_price)
                
                if liq_data and liq_data.confidence in ["HIGH", "MEDIUM"]:
                    whale_zone = {
                        **mover,
                        "current_price": current_price,
                        "liquidation_direction": liq_data.direction,
                        "liquidation_confidence": liq_data.confidence,
                        "liquidation_ratio": liq_data.liquidation_ratio,
                        "scale_in_zones": liq_data.scale_in_zones,
                        "total_long_liquidations": liq_data.total_long_value,
                        "total_short_liquidations": liq_data.total_short_value
                    }
                    
                    whale_zones.append(whale_zone)
                    
                    print(f"      ✅ {symbol}: Direction={liq_data.direction}, "
                          f"Ratio={liq_data.liquidation_ratio:.2f}, "
                          f"Confidence={liq_data.confidence}")
                
            except Exception as e:
                logger.error(f"Error analyzing liquidations for {symbol}: {e}")
                continue
        
        return whale_zones
    
    async def _analyze_rsi_heatmap(self, whale_zones: List[Dict]) -> List[Dict]:
        """Step 3: Confirm with RSI heatmap"""
        
        rsi_confirmations = []
        
        # Get RSI data for all timeframes
        rsi_data = await self.strategy.rsi.scan_extreme_rsi("1h", limit=100)
        
        # Create RSI lookup
        rsi_lookup = {item["symbol"]: item["rsi"] for item in rsi_data}
        
        for zone in whale_zones:
            symbol = zone["symbol"]
            
            try:
                # Get multi-timeframe RSI
                rsi_multi = await self.strategy.rsi.analyze_rsi(symbol)
                
                if rsi_multi:
                    # Check RSI confirmation
                    direction = "UP" if zone["liquidation_direction"] == "UP" else "DOWN"
                    rsi_confirm = self.strategy.rsi.confirm_direction_with_rsi(rsi_multi, direction)
                    
                    zone["rsi_1h"] = rsi_multi.rsi_1h
                    zone["rsi_4h"] = rsi_multi.rsi_4h
                    zone["rsi_status"] = rsi_multi.status
                    zone["rsi_confluence"] = rsi_multi.confluence_score
                    zone["rsi_confirmation"] = rsi_confirm["confidence"]
                    
                    # Only keep high-confidence signals
                    if rsi_confirm["confidence"] in ["HIGH", "MEDIUM"]:
                        rsi_confirmations.append(zone)
                        print(f"   ✅ {symbol}: RSI={rsi_multi.rsi_1h:.1f}, "
                              f"Status={rsi_multi.status}, "
                              f"Confirmation={rsi_confirm['confidence']}")
                
            except Exception as e:
                logger.error(f"Error analyzing RSI for {symbol}: {e}")
                continue
        
        return rsi_confirmations
    
    async def _generate_ultimate_signals(self, confirmations: List[Dict]) -> List[Dict]:
        """Step 4: Generate ultimate trading signals"""
        
        ultimate_signals = []
        
        for conf in confirmations:
            try:
                # Run full master strategy analysis
                signal = await self.strategy.analyze_symbol(conf["symbol"], conf["current_price"])
                
                if signal and signal.action != "NEUTRAL":
                    # Enhance signal with all our data
                    ultimate_signal = {
                        "symbol": signal.symbol,
                        "action": signal.action,
                        "confidence": signal.confidence,
                        "signal_strength": signal.signal_strength,
                        "current_price": signal.current_price,
                        "stop_loss": signal.stop_loss,
                        "take_profit_targets": signal.take_profit_targets,
                        "scale_in_zones": signal.scale_in_zones,
                        
                        # Visual screener data
                        "momentum_score": conf["momentum_score"],
                        "price_change": conf["price_change"],
                        "volume_change": conf["volume_change"],
                        "oi_change": conf["oi_change"],
                        
                        # Liquidation data
                        "liquidation_direction": conf["liquidation_direction"],
                        "liquidation_ratio": conf["liquidation_ratio"],
                        "total_longs": conf["total_long_liquidations"],
                        "total_shorts": conf["total_short_liquidations"],
                        
                        # RSI data
                        "rsi_1h": conf["rsi_1h"],
                        "rsi_4h": conf["rsi_4h"],
                        "rsi_status": conf["rsi_status"],
                        
                        # Meta
                        "timestamp": datetime.now(timezone.utc),
                        "reasons": signal.reasons
                    }
                    
                    ultimate_signals.append(ultimate_signal)
                    
                    # Save to database
                    db.save_signal(signal)
                
            except Exception as e:
                logger.error(f"Error generating signal for {conf['symbol']}: {e}")
                continue
        
        # Sort by signal strength
        ultimate_signals.sort(key=lambda x: x["signal_strength"], reverse=True)
        
        return ultimate_signals
    
    async def _send_telegram_alerts(self, signals: List[Dict]):
        """Send Telegram notifications for top signals"""
        
        if not signals:
            await self.telegram.send_message("🔍 No high-confidence whale hunting opportunities found at this time.")
            return
        
        # Send summary first
        summary = f"""🐋 **WHALE RADAR AI - ULTIMATE SIGNALS** 🐋

Found {len(signals)} high-probability opportunities!

Top 3 Whale Hunting Zones:"""
        
        for i, signal in enumerate(signals[:3]):
            summary += f"""

{i+1}. **{signal['symbol']}** - {signal['action']} 
   • Signal Strength: {signal['signal_strength']}/100
   • Price: ${signal['current_price']:,.2f}
   • Momentum: {signal['momentum_score']}
   • Liquidation Ratio: {signal['liquidation_ratio']:.2f}"""
        
        await self.telegram.send_message(summary)
        
        # Send detailed signals for top opportunities
        for signal in signals[:2]:  # Top 2 detailed
            # Create detailed signal object for formatting
            from src.strategies.master_strategy import MasterSignal
            detailed_signal = MasterSignal(
                symbol=signal["symbol"],
                action=signal["action"],
                confidence=signal["confidence"],
                momentum_score=signal["momentum_score"],
                liquidation_direction=signal["liquidation_direction"],
                rsi_status=signal["rsi_status"],
                current_price=signal["current_price"],
                scale_in_zones=signal["scale_in_zones"],
                stop_loss=signal["stop_loss"],
                take_profit_targets=signal["take_profit_targets"],
                screener_data=None,
                liquidation_data=None,
                rsi_data=None,
                signal_strength=signal["signal_strength"],
                reasons=signal["reasons"],
                timestamp=signal["timestamp"]
            )
            
            await self.telegram.send_signal_alert(detailed_signal)
    
    def _display_summary(self, signals: List[Dict]):
        """Display summary of ultimate analysis"""
        
        print("\n" + "="*80)
        print("📊 ULTIMATE INDICATOR SUMMARY")
        print("="*80)
        
        if not signals:
            print("No high-confidence trading opportunities found.")
            return
        
        print(f"\n✅ Found {len(signals)} ULTIMATE trading signals!\n")
        
        for i, signal in enumerate(signals):
            print(f"{i+1}. {signal['symbol']} - {signal['action']} (Strength: {signal['signal_strength']}/100)")
            print(f"   • Current Price: ${signal['current_price']:,.2f}")
            print(f"   • Stop Loss: ${signal['stop_loss']:,.2f}")
            print(f"   • Take Profits: {[f'${tp:,.2f}' for tp in signal['take_profit_targets']]}")
            print(f"   • Momentum Score: {signal['momentum_score']}")
            print(f"   • Liquidation Ratio: {signal['liquidation_ratio']:.2f}")
            print(f"   • RSI 1H: {signal['rsi_1h']:.1f} ({signal['rsi_status']})")
            print(f"   • Volume Change: {signal['volume_change']:+.1f}%")
            
            if signal['scale_in_zones']:
                print(f"   • Scale-in Zones:")
                for zone in signal['scale_in_zones'][:3]:
                    print(f"     - ${zone['price']:,.2f} ({zone['position_pct']}%)")
            
            print()
        
        print("="*80)
        print("🎯 Ready to hunt whales! Check Telegram for detailed alerts.")
        print("="*80)


async def main():
    """Run the ultimate indicator"""
    indicator = UltimateIndicator()
    
    while True:
        try:
            # Run complete analysis
            signals = await indicator.run_ultimate_analysis()
            
            # Wait for next scan (5 minutes by default)
            print(f"\n⏰ Next scan in 5 minutes...")
            await asyncio.sleep(300)  # 5 minutes
            
        except KeyboardInterrupt:
            print("\n👋 Whale hunting stopped by user.")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            print(f"\n❌ Error in main loop: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retry


if __name__ == "__main__":
    print("""
    🐋 WHALE RADAR AI - ULTIMATE INDICATOR 🐋
    
    Combining:
    • Visual Screeners (Price vs OI, Price vs Volume, Volume vs OI)
    • Liquidation Heatmaps (Model 2)
    • RSI Multi-timeframe Analysis
    • Real-time Telegram Alerts
    
    Press Ctrl+C to stop
    """)
    
    asyncio.run(main())