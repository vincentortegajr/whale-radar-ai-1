"""Comprehensive Reporting System for Deep Analysis"""

from typing import Dict, List, Optional
from datetime import datetime, timezone
from src.utils.logger import setup_logger
from src.indicators.deep_liquidation_analyzer import DeepLiquidationAnalyzer, DeepLiquidationAnalysis
from src.api.telegram_bot import TelegramNotifier

logger = setup_logger(__name__)


class ComprehensiveReporter:
    """Generates comprehensive reports with all liquidation data"""
    
    def __init__(self, analyzer: DeepLiquidationAnalyzer, notifier: TelegramNotifier):
        self.analyzer = analyzer
        self.notifier = notifier
        
    async def generate_top_movers_report(self) -> str:
        """Generate report for top 10 visual screener coins with deep liquidation analysis"""
        logger.info("Generating top movers comprehensive report")
        
        # Get analyses
        analyses = await self.analyzer.analyze_top_visual_screener_coins(top_n=10)
        
        if not analyses:
            return "No data available for analysis"
            
        report = """🐋 WHALE RADAR - TOP 10 MOVERS DEEP ANALYSIS 🎯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 TOP VISUAL SCREENER COINS (5-MINUTE)
Based on Price vs OI + Price vs Volume + Volume vs OI

"""
        
        for i, analysis in enumerate(analyses, 1):
            report += self._format_coin_analysis(i, analysis)
            report += "\n" + "─" * 40 + "\n\n"
            
        # Add summary
        report += self._generate_summary(analyses)
        
        return report
        
    def _format_coin_analysis(self, rank: int, analysis: DeepLiquidationAnalysis) -> str:
        """Format individual coin analysis"""
        
        # Determine emoji based on direction
        direction_emoji = {"LONG": "🟢", "SHORT": "🔴", "NEUTRAL": "⚪"}.get(analysis.recommended_direction, "❓")
        
        report = f"""
{rank}. {direction_emoji} ${analysis.symbol} - {analysis.recommended_direction} SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Current Price: ${analysis.current_price:,.2f}

💧 LIQUIDATION OVERVIEW:
• Total Long Liquidations: ${analysis.total_long_liquidations/1e6:,.1f}M
• Total Short Liquidations: ${analysis.total_short_liquidations/1e6:,.1f}M
• Imbalance: {analysis.liquidation_imbalance_pct:+.1f}% {"(More Shorts)" if analysis.liquidation_imbalance_pct > 0 else "(More Longs)"}
• Liquidation Score: {analysis.liquidation_score}/100

🎯 WHALE TARGET PREDICTION:
• Next Target: ${analysis.next_whale_target['price']:,.2f} ({analysis.next_whale_target['direction']})
• Reasoning: {analysis.next_whale_target['reasoning']}
• Confidence: {analysis.next_whale_target['confidence']}

📊 MAJOR LIQUIDATION CLUSTERS:
"""
        
        # Add top 3 long clusters
        if analysis.major_long_clusters:
            report += "\nLong Liquidations (Support):\n"
            for cluster in analysis.major_long_clusters[:3]:
                report += f"  • ${cluster['price']:,.0f}: ${cluster['value_millions']:.1f}M ({cluster['distance_pct']:.1f}% away)\n"
                
        # Add top 3 short clusters
        if analysis.major_short_clusters:
            report += "\nShort Liquidations (Resistance):\n"
            for cluster in analysis.major_short_clusters[:3]:
                report += f"  • ${cluster['price']:,.0f}: ${cluster['value_millions']:.1f}M ({cluster['distance_pct']:.1f}% away)\n"
                
        # Add scale-in zones if available
        if analysis.scale_in_zones:
            report += "\n🎯 RECOMMENDED SCALE-IN ZONES:\n"
            for zone in analysis.scale_in_zones:
                report += f"  • ${zone['price']:,.2f} ({zone['position_pct']}%) - {zone['reasoning']}\n"
                
        # Add timeframe breakdown
        report += f"""
📈 LIQUIDATION BY TIMEFRAME:
• 12H: {len(analysis.levels_12h)} levels
• 24H: {len(analysis.levels_24h)} levels  
• 3D: {len(analysis.levels_3d)} levels
• 7D: {len(analysis.levels_7d)} levels
• 30D: {len(analysis.levels_30d)} levels
• 90D: {len(analysis.levels_90d)} levels
• 1Y: {len(analysis.levels_1y)} levels

🔗 QUICK LINKS:
[View on CoinGlass]({analysis.coinglass_url})
[Trade on Bybit]({analysis.bybit_url})
"""
        
        return report
        
    async def generate_rsi_liquidation_report(self) -> str:
        """Generate RSI extreme analysis with liquidation confirmation"""
        logger.info("Generating RSI liquidation report")
        
        # Get RSI extreme analyses
        rsi_data = await self.analyzer.analyze_rsi_extremes_liquidations()
        
        report = """🐋 WHALE RADAR - RSI EXTREMES LIQUIDATION CHECK 🎯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RSI OVERSOLD vs LIQUIDATION ANALYSIS
Checking if RSI oversold coins are TRULY oversold based on liquidations

"""
        
        # Oversold analysis
        true_oversold_count = 0
        for coin_data in rsi_data['oversold']:
            if coin_data['true_oversold']:
                true_oversold_count += 1
                
            status = "✅ TRUE OVERSOLD" if coin_data['true_oversold'] else "❌ FALSE OVERSOLD"
            
            report += f"""
${coin_data['symbol']}:
• RSI: {coin_data['rsi']:.1f} (Oversold)
• Liquidation Imbalance: {coin_data['imbalance']:+.1f}%
• Status: {status}
• Liquidation Score: {coin_data['liquidation_score']}/100
"""
            
        report += f"\n✅ {true_oversold_count}/{len(rsi_data['oversold'])} coins are TRUE OVERSOLD (shorts > longs)\n"
        
        # Overbought analysis
        report += "\n📊 RSI OVERBOUGHT vs LIQUIDATION ANALYSIS\n"
        report += "Checking if RSI overbought coins are TRULY overbought based on liquidations\n\n"
        
        true_overbought_count = 0
        for coin_data in rsi_data['overbought']:
            if coin_data['true_overbought']:
                true_overbought_count += 1
                
            status = "✅ TRUE OVERBOUGHT" if coin_data['true_overbought'] else "❌ FALSE OVERBOUGHT"
            
            report += f"""
${coin_data['symbol']}:
• RSI: {coin_data['rsi']:.1f} (Overbought)
• Liquidation Imbalance: {coin_data['imbalance']:+.1f}%
• Status: {status}
• Liquidation Score: {coin_data['liquidation_score']}/100
"""
            
        report += f"\n✅ {true_overbought_count}/{len(rsi_data['overbought'])} coins are TRUE OVERBOUGHT (longs > shorts)\n"
        
        # Best opportunities
        report += "\n🎯 BEST OPPORTUNITIES:\n\n"
        
        # Find best oversold opportunities
        best_oversold = sorted(
            [c for c in rsi_data['oversold'] if c['true_oversold']], 
            key=lambda x: x['liquidation_score'], 
            reverse=True
        )[:3]
        
        if best_oversold:
            report += "TOP OVERSOLD LONGS:\n"
            for coin in best_oversold:
                analysis = coin['analysis']
                report += f"• ${coin['symbol']}: RSI {coin['rsi']:.0f}, Score {coin['liquidation_score']}/100\n"
                report += f"  [CoinGlass]({analysis.coinglass_url}) | [Bybit]({analysis.bybit_url})\n\n"
                
        # Find best overbought opportunities
        best_overbought = sorted(
            [c for c in rsi_data['overbought'] if c['true_overbought']], 
            key=lambda x: x['liquidation_score'], 
            reverse=True
        )[:3]
        
        if best_overbought:
            report += "\nTOP OVERBOUGHT SHORTS:\n"
            for coin in best_overbought:
                analysis = coin['analysis']
                report += f"• ${coin['symbol']}: RSI {coin['rsi']:.0f}, Score {coin['liquidation_score']}/100\n"
                report += f"  [CoinGlass]({analysis.coinglass_url}) | [Bybit]({analysis.bybit_url})\n\n"
                
        return report
        
    def _generate_summary(self, analyses: List[DeepLiquidationAnalysis]) -> str:
        """Generate summary statistics"""
        
        # Count directions
        long_signals = sum(1 for a in analyses if a.recommended_direction == "LONG")
        short_signals = sum(1 for a in analyses if a.recommended_direction == "SHORT")
        neutral_signals = sum(1 for a in analyses if a.recommended_direction == "NEUTRAL")
        
        # Find strongest signals
        strongest_long = max((a for a in analyses if a.recommended_direction == "LONG"), 
                           key=lambda x: x.liquidation_score, default=None)
        strongest_short = max((a for a in analyses if a.recommended_direction == "SHORT"), 
                            key=lambda x: x.liquidation_score, default=None)
        
        summary = f"""
📊 MARKET SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 SIGNAL DISTRIBUTION:
• Long Signals: {long_signals}
• Short Signals: {short_signals}
• Neutral: {neutral_signals}

"""
        
        if strongest_long:
            summary += f"""💚 STRONGEST LONG: ${strongest_long.symbol}
• Score: {strongest_long.liquidation_score}/100
• Imbalance: {strongest_long.liquidation_imbalance_pct:+.1f}%
• [CoinGlass]({strongest_long.coinglass_url}) | [Bybit]({strongest_long.bybit_url})

"""
            
        if strongest_short:
            summary += f"""🔴 STRONGEST SHORT: ${strongest_short.symbol}
• Score: {strongest_short.liquidation_score}/100
• Imbalance: {strongest_short.liquidation_imbalance_pct:+.1f}%
• [CoinGlass]({strongest_short.coinglass_url}) | [Bybit]({strongest_short.bybit_url})

"""
            
        # Add timestamp
        summary += f"""
⏰ Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

🔗 AFFILIATE LINKS:
• CoinGlass Pro: https://www.coinglass.com/pricing?ref=YOUR_REF
• Bybit Trading: https://bybit.com/en/invite?ref=JWNJQWP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐋 WhaleRadar.ai - Hunt with the Whales
"""
        
        return summary
        
    async def send_comprehensive_report(self):
        """Send complete analysis via Telegram"""
        try:
            # Generate top movers report
            top_movers_report = await self.generate_top_movers_report()
            
            # Split into chunks if too long
            chunks = self._split_report(top_movers_report, 4000)  # Telegram limit
            
            for chunk in chunks:
                await self.notifier.bot.send_message(
                    chat_id=self.notifier.chat_id,
                    text=chunk,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                await asyncio.sleep(1)
                
            # Generate and send RSI report
            rsi_report = await self.generate_rsi_liquidation_report()
            chunks = self._split_report(rsi_report, 4000)
            
            for chunk in chunks:
                await self.notifier.bot.send_message(
                    chat_id=self.notifier.chat_id,
                    text=chunk,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error sending comprehensive report: {e}")
            
    def _split_report(self, report: str, max_length: int) -> List[str]:
        """Split long reports into chunks"""
        if len(report) <= max_length:
            return [report]
            
        chunks = []
        lines = report.split('\n')
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk) + len(line) + 1 > max_length:
                chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks