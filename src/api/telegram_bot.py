"""Telegram Bot for WhaleRadar.ai Notifications"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone
from telegram import Bot, ParseMode
from telegram.error import TelegramError
from src.utils.logger import setup_logger
from src.utils.config import settings
from src.strategies.master_strategy import MasterSignal

logger = setup_logger(__name__)


class TelegramNotifier:
    """Sends rich formatted alerts to Telegram"""
    
    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token)
        self.chat_id = settings.telegram_chat_id
        self.sent_alerts = {}  # Track sent alerts to avoid duplicates
        
    async def send_signal_alert(self, signal: MasterSignal):
        """Send a formatted trading signal alert"""
        try:
            # Check for duplicate
            alert_key = f"{signal.symbol}_{signal.action}_{signal.timestamp.hour}"
            if alert_key in self.sent_alerts:
                logger.info(f"Skipping duplicate alert for {signal.symbol}")
                return
                
            # Format the message
            message = self._format_signal_message(signal)
            
            # Send to Telegram
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            
            # Track sent alert
            self.sent_alerts[alert_key] = datetime.now(timezone.utc)
            
            logger.info(f"Alert sent for {signal.symbol} - {signal.action}")
            
        except TelegramError as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            
    async def send_batch_alerts(self, signals: List[MasterSignal]):
        """Send multiple signals with rate limiting"""
        for signal in signals:
            await self.send_signal_alert(signal)
            await asyncio.sleep(1)  # Rate limit
            
    def _format_signal_message(self, signal: MasterSignal) -> str:
        """Format signal into rich Telegram message"""
        
        # Emoji based on action
        if signal.action == "LONG":
            emoji = "🟢"
            action_text = "LONG"
        elif signal.action == "SHORT":
            emoji = "🔴"
            action_text = "SHORT"
        else:
            emoji = "⚪"
            action_text = "NEUTRAL"
            
        # Confidence emoji
        conf_emoji = {"HIGH": "🔥", "MEDIUM": "⚡", "LOW": "⚠️"}.get(signal.confidence, "❓")
        
        # Format scale-in zones
        scale_zones_text = ""
        for i, zone in enumerate(signal.scale_in_zones[:4], 1):
            scale_zones_text += f"• Entry {i}: ${zone['price']:,.2f} ({zone['position_pct']}%)\n"
            
        # Format take profit targets
        tp_text = ""
        for i, tp in enumerate(signal.take_profit_targets[:3], 1):
            tp_pct = abs((tp - signal.current_price) / signal.current_price * 100)
            tp_text += f"• TP{i}: ${tp:,.2f} (+{tp_pct:.1f}%)\n"
            
        # Calculate risk/reward
        risk = abs(signal.current_price - signal.stop_loss)
        reward = abs(signal.take_profit_targets[0] - signal.current_price) if signal.take_profit_targets else 0
        rr_ratio = reward / risk if risk > 0 else 0
        
        message = f"""
🐋 *WHALE RADAR ALERT* 🎯

{emoji} *${signal.symbol} - {action_text} SIGNAL*
━━━━━━━━━━━━━━━━━━━━━

📊 *MOMENTUM INDICATORS:*
• Price Change: {signal.screener_data.price_change_pct:+.2f}%
• Volume Spike: {signal.screener_data.volume_change_pct:+.0f}%
• Open Interest: {signal.screener_data.oi_change_pct:+.1f}%
• Momentum Score: {signal.momentum_score}/100

💧 *LIQUIDATION ANALYSIS:*
• Direction: {signal.liquidation_direction}
• Short Liquidations: ${signal.liquidation_data.total_short_value/1e6:.1f}M
• Long Liquidations: ${signal.liquidation_data.total_long_value/1e6:.1f}M
• Risk/Reward: {rr_ratio:.1f}:1

📈 *RSI CONFIRMATION:*
• 5m RSI: {signal.rsi_data.rsi_5m:.0f}
• 1h RSI: {signal.rsi_data.rsi_1h:.0f} ({signal.rsi_data.status})
• 4h RSI: {signal.rsi_data.rsi_4h:.0f}
• 1d RSI: {signal.rsi_data.rsi_1d:.0f}

🎯 *SCALE-IN ZONES:*
{scale_zones_text}
• Stop Loss: ${signal.stop_loss:,.2f}

💰 *TAKE PROFIT TARGETS:*
{tp_text}

{conf_emoji} *Signal Strength: {signal.signal_strength}/100*
*Confidence: {signal.confidence}*

📝 *Analysis:*
{self._format_reasons(signal.reasons)}

📊 *Quick Links:*
[Liquidation Map](https://www.coinglass.com/pro/futures/LiquidationHeatMapNew?coin={signal.symbol})
[Visual Screener](https://www.coinglass.com/pro/i/VisualScreener)
[Trade on Bybit](https://www.bybit.com/trade/usdt/{signal.symbol}USDT)

⏰ *Alert Time: {signal.timestamp.strftime('%H:%M:%S UTC')}*
━━━━━━━━━━━━━━━━━━━━━
        """
        
        return message.strip()
        
    def _format_reasons(self, reasons: List[str]) -> str:
        """Format analysis reasons"""
        if not reasons:
            return "• No additional notes"
            
        formatted = ""
        for reason in reasons[:5]:  # Limit to 5 reasons
            formatted += f"• {reason}\n"
            
        return formatted.strip()
        
    async def send_summary_report(self, signals_sent: int, top_performers: List[Dict]):
        """Send daily summary report"""
        message = f"""
📊 *DAILY WHALE RADAR REPORT* 📊

📈 *Statistics:*
• Signals Generated: {signals_sent}
• Top Performers: {len(top_performers)}
• Active Monitoring: 850+ perpetuals

🏆 *Top Performers:*
"""
        
        for i, perf in enumerate(top_performers[:5], 1):
            message += f"{i}. ${perf['symbol']}: {perf['pnl']:+.2f}% PnL\n"
            
        message += """

⚡ *WhaleRadar.ai Status: ACTIVE*
━━━━━━━━━━━━━━━━━━━━━
        """
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        except TelegramError as e:
            logger.error(f"Failed to send summary report: {e}")
            
    async def send_error_alert(self, error_type: str, error_message: str):
        """Send error notifications"""
        message = f"""
⚠️ *WHALE RADAR ERROR* ⚠️

*Type:* {error_type}
*Message:* {error_message}
*Time:* {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

The system will attempt to recover automatically.
        """
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        except TelegramError as e:
            logger.error(f"Failed to send error alert: {e}")
            
    def cleanup_old_alerts(self):
        """Remove old alerts from tracking"""
        current_time = datetime.now(timezone.utc)
        
        # Remove alerts older than 1 hour
        self.sent_alerts = {
            k: v for k, v in self.sent_alerts.items()
            if (current_time - v).total_seconds() < 3600
        }