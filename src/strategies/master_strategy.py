"""Master Strategy - The Triple Threat Combination"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from src.utils.logger_setup import setup_logger
from src.utils.config import settings
from src.api.coinglass_client import CoinGlassClient
from src.indicators.visual_screener import VisualScreenerAnalyzer, ScreenerData
from src.indicators.liquidation_analyzer import LiquidationAnalyzer, LiquidationAnalysis
from src.indicators.rsi_heatmap import RSIAnalyzer, RSIData
from src.indicators.deep_liquidation_analyzer import DeepLiquidationAnalyzer

logger = setup_logger(__name__)


@dataclass
class MasterSignal:
    """Complete trading signal with all analyses"""
    symbol: str
    action: str  # "LONG", "SHORT", "NEUTRAL"
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    
    # Component scores
    momentum_score: int
    liquidation_direction: str
    rsi_status: str
    
    # Trading parameters
    current_price: float
    scale_in_zones: List[Dict]
    stop_loss: float
    take_profit_targets: List[float]
    
    # Analysis details
    screener_data: ScreenerData
    liquidation_data: LiquidationAnalysis
    rsi_data: RSIData
    
    # Meta
    signal_strength: int  # 0-100
    reasons: List[str]
    timestamp: datetime


class MasterStrategy:
    """Combines all indicators to generate high-probability signals"""
    
    def __init__(self):
        self.client = CoinGlassClient()
        self.screener = VisualScreenerAnalyzer(self.client)
        self.liquidation = LiquidationAnalyzer(self.client)
        self.rsi = RSIAnalyzer(self.client)
        
    async def analyze_symbol(self, symbol: str, current_price: float) -> Optional[MasterSignal]:
        """Complete analysis for a single symbol"""
        logger.info(f"Running master analysis for {symbol}")
        
        try:
            # Step 1: Visual Screener Analysis
            screener_data = await self.screener.analyze_all_screeners(symbol)
            if not screener_data:
                logger.warning(f"No screener data for {symbol}")
                return None
                
            # Step 2: Liquidation Analysis
            liquidation_data = await self.liquidation.analyze_liquidations(symbol, current_price)
            if not liquidation_data:
                logger.warning(f"No liquidation data for {symbol}")
                return None
                
            # Step 3: RSI Analysis
            rsi_data = await self.rsi.analyze_rsi(symbol)
            if not rsi_data:
                logger.warning(f"No RSI data for {symbol}")
                return None
                
            # Step 4: Combine analyses
            signal = self._generate_signal(
                symbol, current_price, screener_data, liquidation_data, rsi_data
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
            
    async def scan_market(self, top_n: int = 20) -> List[MasterSignal]:
        """Scan entire market for opportunities"""
        logger.info(f"Scanning market for top {top_n} opportunities")
        
        signals = []
        
        # Get top movers from screener
        top_movers = await self.screener.scan_top_movers(timeframe="5m", top_n=top_n * 2)
        
        for mover in top_movers:
            # Skip if momentum is too low
            if mover.momentum_score < 60:
                continue
                
            try:
                # Get current price (would need price API in real implementation)
                current_price = await self._get_current_price(mover.symbol)
                if not current_price:
                    continue
                    
                # Run full analysis
                signal = await self.analyze_symbol(mover.symbol, current_price)
                
                if signal and signal.action != "NEUTRAL":
                    signals.append(signal)
                    
            except Exception as e:
                logger.error(f"Error processing {mover.symbol}: {e}")
                continue
                
        # Sort by signal strength
        signals.sort(key=lambda x: x.signal_strength, reverse=True)
        
        return signals[:top_n]
        
    def _generate_signal(self, symbol: str, current_price: float,
                        screener: ScreenerData, liquidation: LiquidationAnalysis,
                        rsi: RSIData) -> MasterSignal:
        """Generate master signal from all analyses"""
        
        # Initialize signal parameters
        action = "NEUTRAL"
        confidence = "LOW"
        reasons = []
        signal_strength = 0
        
        # 1. Check screener bias
        if screener.bias in ["STRONG_LONG", "LONG"]:
            action = "LONG"
            signal_strength += 20
            reasons.append(f"Visual screener shows {screener.bias} bias (momentum: {screener.momentum_score})")
            
        elif screener.bias in ["STRONG_SHORT", "SHORT"]:
            action = "SHORT"
            signal_strength += 20
            reasons.append(f"Visual screener shows {screener.bias} bias (momentum: {screener.momentum_score})")
            
        # 2. Validate with liquidations
        if liquidation.direction == "UP" and action == "LONG":
            signal_strength += 30
            confidence = liquidation.confidence
            reasons.append(f"Liquidations confirm UP direction (ratio: {liquidation.liquidation_ratio:.2f})")
            
        elif liquidation.direction == "DOWN" and action == "SHORT":
            signal_strength += 30
            confidence = liquidation.confidence
            reasons.append(f"Liquidations confirm DOWN direction (ratio: {liquidation.liquidation_ratio:.2f})")
            
        elif liquidation.direction == "RANGE":
            action = "NEUTRAL"
            reasons.append("Liquidations suggest range-bound market")
            
        else:
            # Conflicting signals
            signal_strength -= 10
            confidence = "LOW"
            reasons.append("Screener and liquidations show conflicting signals")
            
        # 3. Confirm with RSI
        rsi_confirmation = self.rsi.confirm_direction_with_rsi(rsi, action)
        
        if rsi_confirmation["confidence"] == "HIGH":
            signal_strength += 20
            reasons.extend(rsi_confirmation["reasons"])
        elif rsi_confirmation["confidence"] == "MEDIUM":
            signal_strength += 10
            reasons.extend(rsi_confirmation["reasons"])
        else:
            signal_strength -= 5
            reasons.append("RSI does not confirm direction")
            
        # 4. Add confluence bonuses
        if screener.volume_change_pct > 300 and screener.oi_change_pct > 50:
            signal_strength += 10
            reasons.append(f"High volume ({screener.volume_change_pct:.0f}%) and OI ({screener.oi_change_pct:.0f}%) spike")
            
        if rsi.confluence_score > 80:
            signal_strength += 10
            reasons.append(f"Strong RSI confluence across timeframes (score: {rsi.confluence_score})")
            
        # 5. Final confidence adjustment
        if signal_strength >= 70:
            confidence = "HIGH"
        elif signal_strength >= 50:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
            
        # 6. Calculate trading parameters
        stop_loss, take_profits = self._calculate_risk_reward(
            action, current_price, liquidation
        )
        
        # Cap signal strength at 100
        signal_strength = min(100, max(0, signal_strength))
        
        return MasterSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            momentum_score=screener.momentum_score,
            liquidation_direction=liquidation.direction,
            rsi_status=rsi.status,
            current_price=current_price,
            scale_in_zones=liquidation.scale_in_zones,
            stop_loss=stop_loss,
            take_profit_targets=take_profits,
            screener_data=screener,
            liquidation_data=liquidation,
            rsi_data=rsi,
            signal_strength=signal_strength,
            reasons=reasons,
            timestamp=datetime.now(timezone.utc)
        )
        
    def _calculate_risk_reward(self, action: str, current_price: float,
                             liquidation: LiquidationAnalysis) -> Tuple[float, List[float]]:
        """Calculate stop loss and take profit levels"""
        
        if action == "LONG":
            # Stop loss below major long liquidation cluster
            if liquidation.long_liquidations:
                # Find the largest liquidation cluster below
                major_support = min(c.price for c in liquidation.long_liquidations[:3])
                stop_loss = major_support * 0.995  # Just below support
            else:
                stop_loss = current_price * 0.97  # 3% default
                
            # Take profits at short liquidation clusters
            if liquidation.short_liquidations:
                take_profits = [c.price for c in liquidation.short_liquidations[:3]]
            else:
                take_profits = [
                    current_price * 1.02,  # 2%
                    current_price * 1.05,  # 5%
                    current_price * 1.10   # 10%
                ]
                
        elif action == "SHORT":
            # Stop loss above major short liquidation cluster
            if liquidation.short_liquidations:
                major_resistance = max(c.price for c in liquidation.short_liquidations[:3])
                stop_loss = major_resistance * 1.005  # Just above resistance
            else:
                stop_loss = current_price * 1.03  # 3% default
                
            # Take profits at long liquidation clusters
            if liquidation.long_liquidations:
                take_profits = [c.price for c in liquidation.long_liquidations[:3]]
            else:
                take_profits = [
                    current_price * 0.98,  # 2%
                    current_price * 0.95,  # 5%
                    current_price * 0.90   # 10%
                ]
                
        else:  # NEUTRAL
            stop_loss = current_price
            take_profits = [current_price]
            
        return stop_loss, take_profits
        
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        # In real implementation, this would fetch from price API
        # For now, return a mock price
        mock_prices = {
            "BTC": 43250.0,
            "ETH": 2280.0,
            "SOL": 98.50,
            "BNB": 315.0
        }
        return mock_prices.get(symbol, 100.0)