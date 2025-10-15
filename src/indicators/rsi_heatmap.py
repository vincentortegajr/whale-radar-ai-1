"""RSI Heatmap Analyzer - Confluence Confirmation"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from src.utils.logger import setup_logger
from src.utils.config import settings
from src.api.coinglass_client import CoinGlassClient

logger = setup_logger(__name__)


@dataclass
class RSIData:
    """RSI data for a symbol across timeframes"""
    symbol: str
    rsi_5m: float
    rsi_15m: float
    rsi_1h: float
    rsi_4h: float
    rsi_12h: float
    rsi_1d: float
    rsi_1w: float
    status: str  # "OVERBOUGHT", "OVERSOLD", "NEUTRAL", "STRONG", "WEAK"
    confluence_score: int  # 0-100
    timestamp: datetime


class RSIAnalyzer:
    """Analyzes RSI across multiple timeframes for confluence"""
    
    def __init__(self, client: CoinGlassClient):
        self.client = client
        self.oversold_threshold = settings.rsi_oversold
        self.overbought_threshold = settings.rsi_overbought
        
    async def analyze_rsi(self, symbol: str) -> RSIData:
        """Get multi-timeframe RSI analysis for a symbol"""
        logger.info(f"Analyzing RSI for {symbol}")
        
        # Get RSI data for all timeframes
        rsi_values = await self.client.get_rsi_multi_timeframe(symbol)
        
        if not rsi_values:
            logger.warning(f"No RSI data for {symbol}")
            return None
            
        # Calculate status and confluence
        status = self._determine_rsi_status(rsi_values)
        confluence_score = self._calculate_confluence_score(rsi_values)
        
        return RSIData(
            symbol=symbol,
            rsi_5m=rsi_values.get("5m", 50),
            rsi_15m=rsi_values.get("15m", 50),
            rsi_1h=rsi_values.get("1h", 50),
            rsi_4h=rsi_values.get("4h", 50),
            rsi_12h=rsi_values.get("12h", 50),
            rsi_1d=rsi_values.get("1d", 50),
            rsi_1w=rsi_values.get("1w", 50),
            status=status,
            confluence_score=confluence_score,
            timestamp=datetime.now(timezone.utc)
        )
        
    async def scan_extreme_rsi(self, timeframe: str = "1h", limit: int = 50) -> List[Dict]:
        """Scan for coins with extreme RSI values"""
        logger.info(f"Scanning for extreme RSI on {timeframe}")
        
        # Get RSI heatmap data
        rsi_data = await self.client.get_rsi_heatmap(timeframe, limit)
        
        extreme_coins = []
        
        for coin in rsi_data:
            symbol = coin.get("symbol")
            rsi = coin.get("rsi", 50)
            
            # Check for extremes
            if rsi <= self.oversold_threshold:
                extreme_coins.append({
                    "symbol": symbol,
                    "rsi": rsi,
                    "status": "OVERSOLD",
                    "timeframe": timeframe
                })
            elif rsi >= self.overbought_threshold:
                extreme_coins.append({
                    "symbol": symbol,
                    "rsi": rsi,
                    "status": "OVERBOUGHT",
                    "timeframe": timeframe
                })
                
        # Sort by RSI (most extreme first)
        extreme_coins.sort(key=lambda x: x["rsi"] if x["status"] == "OVERSOLD" else 100 - x["rsi"])
        
        return extreme_coins
        
    def confirm_direction_with_rsi(self, rsi_data: RSIData, proposed_direction: str) -> Dict:
        """Confirm a trading direction with RSI analysis"""
        confidence = "LOW"
        reasons = []
        
        if proposed_direction == "UP":
            # Check for oversold conditions
            if rsi_data.status in ["OVERSOLD", "WEAK"]:
                confidence = "HIGH"
                reasons.append("RSI indicates oversold conditions")
                
            # Check specific timeframes
            if rsi_data.rsi_4h < 35 and rsi_data.rsi_1d < 40:
                confidence = "HIGH"
                reasons.append("4H and 1D RSI both oversold")
            elif rsi_data.rsi_1h < 30:
                confidence = "MEDIUM"
                reasons.append("1H RSI oversold")
                
            # Check for bullish divergence potential
            if rsi_data.rsi_1h < rsi_data.rsi_4h < rsi_data.rsi_1d:
                reasons.append("RSI showing potential bullish divergence")
                
        elif proposed_direction == "DOWN":
            # Check for overbought conditions
            if rsi_data.status in ["OVERBOUGHT", "STRONG"]:
                confidence = "HIGH"
                reasons.append("RSI indicates overbought conditions")
                
            # Check specific timeframes
            if rsi_data.rsi_4h > 65 and rsi_data.rsi_1d > 60:
                confidence = "HIGH"
                reasons.append("4H and 1D RSI both overbought")
            elif rsi_data.rsi_1h > 70:
                confidence = "MEDIUM"
                reasons.append("1H RSI overbought")
                
            # Check for bearish divergence potential
            if rsi_data.rsi_1h > rsi_data.rsi_4h > rsi_data.rsi_1d:
                reasons.append("RSI showing potential bearish divergence")
                
        # Lower confidence if RSI is neutral
        if 45 <= rsi_data.rsi_4h <= 55:
            confidence = "LOW"
            reasons.append("4H RSI is neutral")
            
        return {
            "confidence": confidence,
            "reasons": reasons,
            "rsi_status": rsi_data.status,
            "confluence_score": rsi_data.confluence_score
        }
        
    def _determine_rsi_status(self, rsi_values: Dict[str, float]) -> str:
        """Determine overall RSI status based on multiple timeframes"""
        # Count oversold/overbought across timeframes
        oversold_count = 0
        overbought_count = 0
        
        important_timeframes = ["1h", "4h", "12h", "1d"]
        
        for tf in important_timeframes:
            rsi = rsi_values.get(tf, 50)
            
            if rsi <= self.oversold_threshold:
                oversold_count += 1
            elif rsi >= self.overbought_threshold:
                overbought_count += 1
                
        # Determine status
        if oversold_count >= 3:
            return "OVERSOLD"
        elif overbought_count >= 3:
            return "OVERBOUGHT"
        elif oversold_count >= 2:
            return "WEAK"
        elif overbought_count >= 2:
            return "STRONG"
        else:
            return "NEUTRAL"
            
    def _calculate_confluence_score(self, rsi_values: Dict[str, float]) -> int:
        """Calculate how aligned RSI is across timeframes (0-100)"""
        values = [rsi_values.get(tf, 50) for tf in ["1h", "4h", "12h", "1d"]]
        
        # Calculate standard deviation
        avg_rsi = sum(values) / len(values)
        variance = sum((x - avg_rsi) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # Lower std dev = higher confluence
        if std_dev < 5:
            confluence = 100
        elif std_dev < 10:
            confluence = 80
        elif std_dev < 15:
            confluence = 60
        elif std_dev < 20:
            confluence = 40
        else:
            confluence = 20
            
        # Bonus for extreme values in same direction
        if all(v <= self.oversold_threshold for v in values):
            confluence = min(100, confluence + 20)
        elif all(v >= self.overbought_threshold for v in values):
            confluence = min(100, confluence + 20)
            
        return confluence