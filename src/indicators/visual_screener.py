"""Visual Screener Analysis Module - The Triple Threat"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from src.utils.logger_setup import setup_logger
from src.utils.config import settings
from src.api.coinglass_client import CoinGlassClient

logger = setup_logger(__name__)


@dataclass
class ScreenerData:
    """Container for visual screener data"""
    symbol: str
    price_change_pct: float
    volume_change_pct: float
    oi_change_pct: float
    momentum_score: int
    bias: str  # STRONG_LONG, LONG, NEUTRAL, SHORT, STRONG_SHORT
    timestamp: datetime


class VisualScreenerAnalyzer:
    """Analyzes the three visual screeners to identify opportunities"""
    
    def __init__(self, client: CoinGlassClient):
        self.client = client
        self.volume_spike_threshold = settings.volume_spike_threshold
        self.oi_spike_threshold = settings.oi_spike_threshold
        
    async def analyze_all_screeners(self, symbol: str, timeframe: str = "5m") -> ScreenerData:
        """Analyze all three visual screeners for a symbol"""
        logger.info(f"Analyzing visual screeners for {symbol}")
        
        # Fetch all three screener types
        price_oi_data = await self.client.get_visual_screener_price_oi(timeframe)
        price_volume_data = await self.client.get_visual_screener_price_volume(timeframe)
        volume_oi_data = await self.client.get_visual_screener_volume_oi(timeframe)
        
        # Extract data for our symbol
        symbol_data = self._extract_symbol_data(
            symbol, price_oi_data, price_volume_data, volume_oi_data
        )
        
        if not symbol_data:
            logger.warning(f"No data found for {symbol}")
            return None
            
        # Calculate momentum score
        momentum_score = self._calculate_momentum_score(symbol_data)
        
        # Determine bias
        bias = self._determine_bias(symbol_data, momentum_score)
        
        return ScreenerData(
            symbol=symbol,
            price_change_pct=symbol_data["price_change"],
            volume_change_pct=symbol_data["volume_change"],
            oi_change_pct=symbol_data["oi_change"],
            momentum_score=momentum_score,
            bias=bias,
            timestamp=datetime.now(timezone.utc)
        )
        
    async def scan_top_movers(self, timeframe: str = "5m", top_n: int = 20) -> List[ScreenerData]:
        """Scan for top moving coins across all screeners"""
        logger.info(f"Scanning top {top_n} movers")
        
        # Fetch all screener data
        price_oi_data = await self.client.get_visual_screener_price_oi(timeframe)
        price_volume_data = await self.client.get_visual_screener_price_volume(timeframe)
        volume_oi_data = await self.client.get_visual_screener_volume_oi(timeframe)
        
        # Process all symbols
        all_symbols_data = []
        
        # Get unique symbols from all screeners
        symbols = set()
        for data_list in [price_oi_data, price_volume_data, volume_oi_data]:
            for item in data_list:
                symbols.add(item.get("symbol"))
                
        for symbol in symbols:
            symbol_data = self._extract_symbol_data(
                symbol, price_oi_data, price_volume_data, volume_oi_data
            )
            
            if symbol_data:
                momentum_score = self._calculate_momentum_score(symbol_data)
                bias = self._determine_bias(symbol_data, momentum_score)
                
                all_symbols_data.append(ScreenerData(
                    symbol=symbol,
                    price_change_pct=symbol_data["price_change"],
                    volume_change_pct=symbol_data["volume_change"],
                    oi_change_pct=symbol_data["oi_change"],
                    momentum_score=momentum_score,
                    bias=bias,
                    timestamp=datetime.now(timezone.utc)
                ))
                
        # Sort by momentum score and return top N
        all_symbols_data.sort(key=lambda x: x.momentum_score, reverse=True)
        return all_symbols_data[:top_n]
        
    def _extract_symbol_data(self, symbol: str, price_oi: List[Dict], 
                           price_volume: List[Dict], volume_oi: List[Dict]) -> Optional[Dict]:
        """Extract data for a specific symbol from all screeners"""
        result = {
            "price_change": 0.0,
            "volume_change": 0.0,
            "oi_change": 0.0
        }
        
        # All three endpoints return the same data, so we can use any one
        # Find symbol in the data (they all have the same format)
        for item in price_oi:
            if isinstance(item, dict) and item.get("symbol") == symbol:
                # Extract price change from various fields
                result["price_change"] = item.get("price_change_percent_1h", 0) or \
                                       item.get("price_change_percent_4h", 0) or \
                                       item.get("price_change_percent_24h", 0)
                
                # Extract volume change
                result["volume_change"] = item.get("volume_change_percent_1h", 0) or \
                                        item.get("volume_change_percent_4h", 0) or \
                                        item.get("volume_change_percent_24h", 0)
                
                # Extract OI change
                result["oi_change"] = item.get("oi_change_percent_1h", 0) or \
                                    item.get("oi_change_percent_4h", 0) or \
                                    item.get("oi_change_percent_24h", 0)
                
                # If we have the data, no need to check other lists
                if any(v != 0 for v in result.values()):
                    return result
                
        # Return None if no data found
        if all(v == 0 for v in result.values()):
            return None
            
        return result
        
    def _calculate_momentum_score(self, data: Dict) -> int:
        """Calculate momentum score 0-100 based on all indicators"""
        score = 50  # Start neutral
        
        price_change = data["price_change"]
        volume_change = data["volume_change"]
        oi_change = data["oi_change"]
        
        # Price change impact (max ±20 points)
        if abs(price_change) > 10:
            score += min(20, abs(price_change)) * (1 if price_change > 0 else -1)
        else:
            score += price_change * 2
            
        # Volume spike impact (max ±20 points)
        if volume_change > self.volume_spike_threshold:
            score += min(20, volume_change / 20)
        elif volume_change > 100:
            score += 10
        elif volume_change > 50:
            score += 5
            
        # Open Interest impact (max ±10 points)
        if abs(oi_change) > self.oi_spike_threshold:
            score += min(10, abs(oi_change) / 10) * (1 if oi_change > 0 else -1)
        else:
            score += oi_change / 5
            
        # Confluence bonus
        if price_change > 0 and volume_change > 100 and oi_change > 20:
            score += 10  # Bullish confluence
        elif price_change < 0 and volume_change > 100 and oi_change > 20:
            score -= 10  # Bearish confluence
            
        # Cap score between 0-100
        return max(0, min(100, int(score)))
        
    def _determine_bias(self, data: Dict, momentum_score: int) -> str:
        """Determine market bias based on data"""
        price_change = data["price_change"]
        volume_change = data["volume_change"]
        oi_change = data["oi_change"]
        
        # Strong signals
        if momentum_score > 80 and price_change > 5:
            return "STRONG_LONG"
        elif momentum_score < 20 and price_change < -5:
            return "STRONG_SHORT"
            
        # Regular signals
        elif momentum_score > 65 and price_change > 0:
            return "LONG"
        elif momentum_score < 35 and price_change < 0:
            return "SHORT"
            
        # Check for divergences
        elif price_change > 3 and volume_change < 50:
            return "WEAK_LONG"  # Price up but no volume
        elif price_change < -3 and volume_change < 50:
            return "WEAK_SHORT"  # Price down but no volume
            
        else:
            return "NEUTRAL"