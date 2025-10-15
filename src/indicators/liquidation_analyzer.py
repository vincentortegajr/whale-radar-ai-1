"""Liquidation Heatmap Analyzer - Where the Whales Hunt"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import statistics
from src.utils.logger import setup_logger
from src.utils.config import settings
from src.api.coinglass_client import CoinGlassClient

logger = setup_logger(__name__)


@dataclass
class LiquidationCluster:
    """Represents a cluster of liquidations at a price level"""
    price: float
    value_usd: float
    type: str  # "long" or "short"
    cumulative_value: float
    distance_from_price_pct: float


@dataclass
class LiquidationAnalysis:
    """Complete liquidation analysis for a symbol"""
    symbol: str
    current_price: float
    direction: str  # "UP", "DOWN", or "RANGE"
    long_liquidations: List[LiquidationCluster]
    short_liquidations: List[LiquidationCluster]
    total_long_value: float
    total_short_value: float
    liquidation_ratio: float  # shorts/longs ratio
    scale_in_zones: List[Dict]
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    timestamp: datetime


class LiquidationAnalyzer:
    """Analyzes liquidation heatmaps to identify whale hunting zones"""
    
    def __init__(self, client: CoinGlassClient):
        self.client = client
        self.min_cluster_value = settings.min_liquidation_value_usd
        self.ratio_threshold = settings.liquidation_ratio_threshold
        
    async def analyze_liquidations(self, symbol: str, current_price: float) -> LiquidationAnalysis:
        """Complete liquidation analysis for a symbol"""
        logger.info(f"Analyzing liquidations for {symbol} at ${current_price}")
        
        # Get liquidation data for multiple timeframes
        heatmap_data = await self.client.get_liquidation_heatmap_all_timeframes(symbol, model=2)
        
        if not heatmap_data:
            logger.warning(f"No liquidation data for {symbol}")
            return None
            
        # Process liquidation clusters
        long_clusters, short_clusters = self._process_clusters(heatmap_data, current_price)
        
        # Calculate totals
        total_long_value = sum(c.value_usd for c in long_clusters)
        total_short_value = sum(c.value_usd for c in short_clusters)
        
        # Determine direction
        direction, confidence = self._determine_direction(
            long_clusters, short_clusters, total_long_value, total_short_value
        )
        
        # Calculate scale-in zones
        scale_zones = self._calculate_scale_zones(
            direction, long_clusters, short_clusters, current_price
        )
        
        # Calculate liquidation ratio
        liq_ratio = total_short_value / total_long_value if total_long_value > 0 else 0
        
        return LiquidationAnalysis(
            symbol=symbol,
            current_price=current_price,
            direction=direction,
            long_liquidations=long_clusters,
            short_liquidations=short_clusters,
            total_long_value=total_long_value,
            total_short_value=total_short_value,
            liquidation_ratio=liq_ratio,
            scale_in_zones=scale_zones,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc)
        )
        
    def _process_clusters(self, heatmap_data: Dict, current_price: float) -> Tuple[List, List]:
        """Process raw heatmap data into liquidation clusters"""
        long_clusters = []
        short_clusters = []
        
        # Aggregate data from all timeframes
        aggregated_longs = {}
        aggregated_shorts = {}
        
        for timeframe, data in heatmap_data.items():
            if not data or "data" not in data:
                continue
                
            liquidation_data = data.get("data", {})
            
            # Process long liquidations (below current price)
            for price_str, value in liquidation_data.get("longs", {}).items():
                price = float(price_str)
                if price < current_price:
                    if price in aggregated_longs:
                        aggregated_longs[price] += value
                    else:
                        aggregated_longs[price] = value
                        
            # Process short liquidations (above current price)
            for price_str, value in liquidation_data.get("shorts", {}).items():
                price = float(price_str)
                if price > current_price:
                    if price in aggregated_shorts:
                        aggregated_shorts[price] += value
                    else:
                        aggregated_shorts[price] = value
                        
        # Create clusters for significant levels
        cumulative_long = 0
        for price in sorted(aggregated_longs.keys(), reverse=True):  # Start from top
            value = aggregated_longs[price]
            if value >= self.min_cluster_value:
                cumulative_long += value
                distance = abs((price - current_price) / current_price * 100)
                
                long_clusters.append(LiquidationCluster(
                    price=price,
                    value_usd=value,
                    type="long",
                    cumulative_value=cumulative_long,
                    distance_from_price_pct=distance
                ))
                
        cumulative_short = 0
        for price in sorted(aggregated_shorts.keys()):  # Start from bottom
            value = aggregated_shorts[price]
            if value >= self.min_cluster_value:
                cumulative_short += value
                distance = abs((price - current_price) / current_price * 100)
                
                short_clusters.append(LiquidationCluster(
                    price=price,
                    value_usd=value,
                    type="short",
                    cumulative_value=cumulative_short,
                    distance_from_price_pct=distance
                ))
                
        return long_clusters, short_clusters
        
    def _determine_direction(self, long_clusters: List, short_clusters: List,
                           total_long: float, total_short: float) -> Tuple[str, str]:
        """Determine likely price direction based on liquidations"""
        # Check liquidation ratio
        if total_long > 0:
            ratio = total_short / total_long
        else:
            ratio = float('inf') if total_short > 0 else 1
            
        # Count nearby clusters (within 5% of current price)
        nearby_longs = sum(1 for c in long_clusters if c.distance_from_price_pct < 5)
        nearby_shorts = sum(1 for c in short_clusters if c.distance_from_price_pct < 5)
        
        # Determine direction
        if ratio > self.ratio_threshold and nearby_shorts > nearby_longs:
            direction = "UP"  # More shorts to hunt
            confidence = "HIGH" if ratio > 2.0 else "MEDIUM"
            
        elif ratio < (1 / self.ratio_threshold) and nearby_longs > nearby_shorts:
            direction = "DOWN"  # More longs to hunt
            confidence = "HIGH" if ratio < 0.5 else "MEDIUM"
            
        else:
            direction = "RANGE"
            confidence = "LOW"
            
        # Check for massive one-sided liquidations
        if total_short > total_long * 3:
            direction = "UP"
            confidence = "HIGH"
        elif total_long > total_short * 3:
            direction = "DOWN"
            confidence = "HIGH"
            
        return direction, confidence
        
    def _calculate_scale_zones(self, direction: str, long_clusters: List,
                             short_clusters: List, current_price: float) -> List[Dict]:
        """Calculate optimal scale-in zones based on liquidations"""
        zones = []
        
        if direction == "UP":
            # For longs, scale in below current price at support levels
            support_levels = self._find_support_levels(long_clusters, current_price)
            
            if support_levels:
                # Distribute position across support levels
                position_pcts = self._distribute_position(len(support_levels))
                
                for i, (price, strength) in enumerate(support_levels[:4]):  # Max 4 entries
                    zones.append({
                        "price": price,
                        "position_pct": position_pcts[i],
                        "reason": f"Support level with ${strength/1e6:.1f}M liquidations"
                    })
                    
        elif direction == "DOWN":
            # For shorts, scale in above current price at resistance levels
            resistance_levels = self._find_resistance_levels(short_clusters, current_price)
            
            if resistance_levels:
                position_pcts = self._distribute_position(len(resistance_levels))
                
                for i, (price, strength) in enumerate(resistance_levels[:4]):
                    zones.append({
                        "price": price,
                        "position_pct": position_pcts[i],
                        "reason": f"Resistance level with ${strength/1e6:.1f}M liquidations"
                    })
                    
        else:  # RANGE
            # Find both support and resistance for range trading
            support = self._find_support_levels(long_clusters, current_price)
            resistance = self._find_resistance_levels(short_clusters, current_price)
            
            if support and resistance:
                # Range trade between levels
                zones.append({
                    "price": support[0][0],
                    "position_pct": 50,
                    "reason": "Range bottom - buy zone"
                })
                zones.append({
                    "price": resistance[0][0],
                    "position_pct": 50,
                    "reason": "Range top - sell zone"
                })
                
        return zones
        
    def _find_support_levels(self, long_clusters: List, current_price: float) -> List[Tuple[float, float]]:
        """Find support levels from long liquidations"""
        # Support is where longs get liquidated (below price)
        support_levels = []
        
        for cluster in long_clusters:
            if cluster.distance_from_price_pct < 20:  # Within 20% of current price
                support_levels.append((cluster.price, cluster.cumulative_value))
                
        # Sort by strength (cumulative value)
        support_levels.sort(key=lambda x: x[1], reverse=True)
        return support_levels
        
    def _find_resistance_levels(self, short_clusters: List, current_price: float) -> List[Tuple[float, float]]:
        """Find resistance levels from short liquidations"""
        # Resistance is where shorts get liquidated (above price)
        resistance_levels = []
        
        for cluster in short_clusters:
            if cluster.distance_from_price_pct < 20:  # Within 20% of current price
                resistance_levels.append((cluster.price, cluster.cumulative_value))
                
        # Sort by strength
        resistance_levels.sort(key=lambda x: x[1], reverse=True)
        return resistance_levels
        
    def _distribute_position(self, num_entries: int) -> List[int]:
        """Distribute position size across entries"""
        if num_entries == 1:
            return [100]
        elif num_entries == 2:
            return [60, 40]
        elif num_entries == 3:
            return [40, 35, 25]
        elif num_entries == 4:
            return [30, 30, 25, 15]
        else:
            # Evenly distribute for more than 4
            base = 100 // num_entries
            remainder = 100 % num_entries
            distribution = [base] * num_entries
            for i in range(remainder):
                distribution[i] += 1
            return distribution