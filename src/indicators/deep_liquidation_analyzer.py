"""Deep Liquidation Analyzer - Complete Multi-Level Analysis"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import asyncio
from src.utils.logger import setup_logger
from src.utils.config import settings
from src.api.coinglass_client import CoinGlassClient

logger = setup_logger(__name__)


@dataclass
class LiquidationLevel:
    """Single liquidation level data"""
    price: float
    value_usd: float
    type: str  # "long" or "short"
    timeframe: str
    distance_from_price_pct: float


@dataclass
class DeepLiquidationAnalysis:
    """Complete liquidation analysis across all timeframes"""
    symbol: str
    current_price: float
    
    # All liquidation levels by timeframe
    levels_12h: List[LiquidationLevel]
    levels_24h: List[LiquidationLevel]
    levels_3d: List[LiquidationLevel]
    levels_7d: List[LiquidationLevel]
    levels_30d: List[LiquidationLevel]
    levels_90d: List[LiquidationLevel]
    levels_1y: List[LiquidationLevel]
    
    # Aggregate analysis
    total_long_liquidations: float
    total_short_liquidations: float
    liquidation_imbalance_pct: float  # Positive = more shorts, Negative = more longs
    next_whale_target: Dict  # Price and reasoning
    liquidation_score: int  # 0-100, higher = stronger directional bias
    
    # Top liquidation clusters
    major_long_clusters: List[Dict]
    major_short_clusters: List[Dict]
    
    # Recommendations
    recommended_direction: str
    confidence: str
    scale_in_zones: List[Dict]
    
    # URLs
    coinglass_url: str
    bybit_url: str
    
    timestamp: datetime


class DeepLiquidationAnalyzer:
    """Analyzes liquidation levels across ALL timeframes"""
    
    def __init__(self, client: CoinGlassClient):
        self.client = client
        self.referral_codes = {
            "coinglass": "YOUR_COINGLASS_REF",  # Add your CoinGlass referral
            "bybit": "JWNJQWP"
        }
        
    async def analyze_top_visual_screener_coins(self, top_n: int = 10) -> List[DeepLiquidationAnalysis]:
        """Get top coins from visual screener and analyze all liquidation levels"""
        logger.info(f"Analyzing top {top_n} visual screener coins")
        
        # Get visual screener data for all 3 types
        price_oi = await self.client.get_visual_screener_price_oi("5m")
        price_volume = await self.client.get_visual_screener_price_volume("5m")
        volume_oi = await self.client.get_visual_screener_volume_oi("5m")
        
        # Combine and score all coins
        coin_scores = self._score_visual_screener_coins(price_oi, price_volume, volume_oi)
        
        # Get top N coins
        top_coins = sorted(coin_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # Analyze liquidations for each top coin
        analyses = []
        for symbol, score in top_coins:
            try:
                # Get current price (would need price API)
                current_price = await self._get_current_price(symbol)
                if not current_price:
                    continue
                    
                analysis = await self.analyze_all_liquidation_levels(symbol, current_price)
                if analysis:
                    analyses.append(analysis)
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                
        return analyses
        
    async def analyze_all_liquidation_levels(self, symbol: str, current_price: float) -> DeepLiquidationAnalysis:
        """Analyze ALL liquidation levels for a symbol"""
        logger.info(f"Deep liquidation analysis for {symbol} at ${current_price}")
        
        # Fetch liquidation data for ALL timeframes
        timeframes = ["12h", "24h", "3d", "7d", "30d", "90d", "1y"]
        all_levels = {}
        
        # Parallel fetch all timeframes
        tasks = []
        for tf in timeframes:
            tasks.append(self._fetch_liquidation_levels(symbol, tf))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for tf, result in zip(timeframes, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch {tf} for {symbol}: {result}")
                all_levels[tf] = []
            else:
                all_levels[tf] = result
                
        # Extract levels by timeframe
        levels_by_tf = self._process_all_levels(all_levels, current_price)
        
        # Calculate aggregates
        total_longs, total_shorts = self._calculate_totals(levels_by_tf)
        imbalance_pct = ((total_shorts - total_longs) / (total_shorts + total_longs) * 100) if (total_shorts + total_longs) > 0 else 0
        
        # Find major clusters
        major_long_clusters = self._find_major_clusters(levels_by_tf, "long", current_price)
        major_short_clusters = self._find_major_clusters(levels_by_tf, "short", current_price)
        
        # Determine next whale target
        next_target = self._predict_whale_target(major_long_clusters, major_short_clusters, imbalance_pct, current_price)
        
        # Calculate liquidation score
        liq_score = self._calculate_liquidation_score(imbalance_pct, major_long_clusters, major_short_clusters)
        
        # Determine direction and scale-in zones
        direction, confidence = self._determine_direction(imbalance_pct, liq_score)
        scale_zones = self._calculate_scale_zones(major_long_clusters, major_short_clusters, direction, current_price)
        
        # Generate URLs
        coinglass_url = f"https://www.coinglass.com/pro/futures/LiquidationHeatMapNew?coin={symbol}&ref={self.referral_codes['coinglass']}"
        bybit_url = f"https://bybit.com/en/trade/usdt/{symbol}USDT?ref={self.referral_codes['bybit']}"
        
        return DeepLiquidationAnalysis(
            symbol=symbol,
            current_price=current_price,
            levels_12h=levels_by_tf.get("12h", []),
            levels_24h=levels_by_tf.get("24h", []),
            levels_3d=levels_by_tf.get("3d", []),
            levels_7d=levels_by_tf.get("7d", []),
            levels_30d=levels_by_tf.get("30d", []),
            levels_90d=levels_by_tf.get("90d", []),
            levels_1y=levels_by_tf.get("1y", []),
            total_long_liquidations=total_longs,
            total_short_liquidations=total_shorts,
            liquidation_imbalance_pct=imbalance_pct,
            next_whale_target=next_target,
            liquidation_score=liq_score,
            major_long_clusters=major_long_clusters,
            major_short_clusters=major_short_clusters,
            recommended_direction=direction,
            confidence=confidence,
            scale_in_zones=scale_zones,
            coinglass_url=coinglass_url,
            bybit_url=bybit_url,
            timestamp=datetime.now(timezone.utc)
        )
        
    async def analyze_rsi_extremes_liquidations(self) -> Dict:
        """Analyze liquidations for top RSI oversold/overbought coins"""
        logger.info("Analyzing RSI extremes with liquidations")
        
        # Get RSI data
        rsi_data = await self.client.get_rsi_heatmap("1h", 200)
        
        # Find extremes
        oversold = []
        overbought = []
        
        for coin in rsi_data:
            if coin['rsi'] <= 30:
                oversold.append(coin)
            elif coin['rsi'] >= 70:
                overbought.append(coin)
                
        # Sort by RSI
        oversold.sort(key=lambda x: x['rsi'])
        overbought.sort(key=lambda x: x['rsi'], reverse=True)
        
        # Take top 10 each
        top_oversold = oversold[:10]
        top_overbought = overbought[:10]
        
        # Analyze liquidations for each
        oversold_analyses = []
        overbought_analyses = []
        
        for coin in top_oversold:
            try:
                price = await self._get_current_price(coin['symbol'])
                if price:
                    analysis = await self.analyze_all_liquidation_levels(coin['symbol'], price)
                    if analysis:
                        oversold_analyses.append({
                            'symbol': coin['symbol'],
                            'rsi': coin['rsi'],
                            'liquidation_score': analysis.liquidation_score,
                            'imbalance': analysis.liquidation_imbalance_pct,
                            'true_oversold': analysis.liquidation_imbalance_pct > 20,  # More shorts to hunt
                            'analysis': analysis
                        })
            except Exception as e:
                logger.error(f"Error analyzing oversold {coin['symbol']}: {e}")
                
        for coin in top_overbought:
            try:
                price = await self._get_current_price(coin['symbol'])
                if price:
                    analysis = await self.analyze_all_liquidation_levels(coin['symbol'], price)
                    if analysis:
                        overbought_analyses.append({
                            'symbol': coin['symbol'],
                            'rsi': coin['rsi'],
                            'liquidation_score': analysis.liquidation_score,
                            'imbalance': analysis.liquidation_imbalance_pct,
                            'true_overbought': analysis.liquidation_imbalance_pct < -20,  # More longs to hunt
                            'analysis': analysis
                        })
            except Exception as e:
                logger.error(f"Error analyzing overbought {coin['symbol']}: {e}")
                
        return {
            'oversold': oversold_analyses,
            'overbought': overbought_analyses
        }
        
    async def _fetch_liquidation_levels(self, symbol: str, timeframe: str) -> List[Dict]:
        """Fetch liquidation levels for a specific timeframe"""
        try:
            data = await self.client.get_liquidation_heatmap(symbol, model=2, timeframe=timeframe)
            return data.get('data', {})
        except Exception as e:
            logger.error(f"Error fetching {symbol} {timeframe}: {e}")
            return {}
            
    def _process_all_levels(self, all_data: Dict, current_price: float) -> Dict[str, List[LiquidationLevel]]:
        """Process raw liquidation data into structured levels"""
        processed = {}
        
        for tf, data in all_data.items():
            levels = []
            
            # Process longs
            for price_str, value in data.get('longs', {}).items():
                try:
                    price = float(price_str)
                    distance = abs((price - current_price) / current_price * 100)
                    
                    levels.append(LiquidationLevel(
                        price=price,
                        value_usd=value,
                        type="long",
                        timeframe=tf,
                        distance_from_price_pct=distance
                    ))
                except:
                    pass
                    
            # Process shorts
            for price_str, value in data.get('shorts', {}).items():
                try:
                    price = float(price_str)
                    distance = abs((price - current_price) / current_price * 100)
                    
                    levels.append(LiquidationLevel(
                        price=price,
                        value_usd=value,
                        type="short",
                        timeframe=tf,
                        distance_from_price_pct=distance
                    ))
                except:
                    pass
                    
            # Sort by value
            levels.sort(key=lambda x: x.value_usd, reverse=True)
            processed[tf] = levels
            
        return processed
        
    def _calculate_totals(self, levels_by_tf: Dict) -> Tuple[float, float]:
        """Calculate total long and short liquidations"""
        total_longs = 0
        total_shorts = 0
        
        for tf, levels in levels_by_tf.items():
            for level in levels:
                if level.type == "long":
                    total_longs += level.value_usd
                else:
                    total_shorts += level.value_usd
                    
        return total_longs, total_shorts
        
    def _find_major_clusters(self, levels_by_tf: Dict, liq_type: str, current_price: float) -> List[Dict]:
        """Find major liquidation clusters"""
        all_levels = []
        
        # Aggregate all levels of the specified type
        for tf, levels in levels_by_tf.items():
            for level in levels:
                if level.type == liq_type:
                    all_levels.append(level)
                    
        # Sort by value
        all_levels.sort(key=lambda x: x.value_usd, reverse=True)
        
        # Take top clusters
        clusters = []
        for level in all_levels[:10]:  # Top 10 clusters
            clusters.append({
                'price': level.price,
                'value_usd': level.value_usd,
                'value_millions': level.value_usd / 1e6,
                'distance_pct': level.distance_from_price_pct,
                'timeframe': level.timeframe
            })
            
        return clusters
        
    def _predict_whale_target(self, long_clusters: List[Dict], short_clusters: List[Dict], 
                            imbalance: float, current_price: float) -> Dict:
        """Predict where whales are likely to push price next"""
        
        # Find nearest major liquidations
        nearest_long = min(long_clusters, key=lambda x: x['distance_pct']) if long_clusters else None
        nearest_short = min(short_clusters, key=lambda x: x['distance_pct']) if short_clusters else None
        
        if imbalance > 30:  # Heavy short imbalance
            target_price = nearest_short['price'] if nearest_short else current_price * 1.05
            reasoning = f"Heavy short liquidations (${nearest_short['value_millions']:.1f}M) at ${target_price:,.0f}"
            direction = "UP"
            
        elif imbalance < -30:  # Heavy long imbalance
            target_price = nearest_long['price'] if nearest_long else current_price * 0.95
            reasoning = f"Heavy long liquidations (${nearest_long['value_millions']:.1f}M) at ${target_price:,.0f}"
            direction = "DOWN"
            
        else:  # Balanced - look for biggest cluster
            if nearest_short and nearest_long:
                if nearest_short['value_usd'] > nearest_long['value_usd']:
                    target_price = nearest_short['price']
                    reasoning = f"Larger short cluster (${nearest_short['value_millions']:.1f}M) nearby"
                    direction = "UP"
                else:
                    target_price = nearest_long['price']
                    reasoning = f"Larger long cluster (${nearest_long['value_millions']:.1f}M) nearby"
                    direction = "DOWN"
            else:
                target_price = current_price
                reasoning = "Balanced liquidations - range likely"
                direction = "RANGE"
                
        return {
            'price': target_price,
            'direction': direction,
            'reasoning': reasoning,
            'confidence': "HIGH" if abs(imbalance) > 30 else "MEDIUM"
        }
        
    def _calculate_liquidation_score(self, imbalance: float, long_clusters: List, short_clusters: List) -> int:
        """Calculate 0-100 score for liquidation strength"""
        score = 50
        
        # Imbalance impact (up to ±30 points)
        score += min(30, abs(imbalance) / 2) * (1 if imbalance > 0 else -1)
        
        # Cluster concentration (up to ±20 points)
        if long_clusters and short_clusters:
            total_long_value = sum(c['value_usd'] for c in long_clusters[:3])
            total_short_value = sum(c['value_usd'] for c in short_clusters[:3])
            
            if total_short_value > total_long_value * 2:
                score += 20
            elif total_long_value > total_short_value * 2:
                score -= 20
                
        # Normalize to 0-100
        return max(0, min(100, score))
        
    def _determine_direction(self, imbalance: float, score: int) -> Tuple[str, str]:
        """Determine trading direction and confidence"""
        if score > 70:
            return ("LONG", "HIGH") if imbalance > 0 else ("SHORT", "HIGH")
        elif score > 60:
            return ("LONG", "MEDIUM") if imbalance > 0 else ("SHORT", "MEDIUM")
        elif score < 30:
            return ("SHORT", "HIGH") if imbalance < 0 else ("LONG", "HIGH")
        elif score < 40:
            return ("SHORT", "MEDIUM") if imbalance < 0 else ("LONG", "MEDIUM")
        else:
            return ("NEUTRAL", "LOW")
            
    def _calculate_scale_zones(self, long_clusters: List, short_clusters: List,
                             direction: str, current_price: float) -> List[Dict]:
        """Calculate scale-in zones based on liquidation clusters"""
        zones = []
        
        if direction == "LONG":
            # Scale in at support levels (long liquidations)
            targets = sorted([c for c in long_clusters if c['price'] < current_price], 
                           key=lambda x: x['price'], reverse=True)[:4]
            
            position_sizes = [30, 30, 25, 15]
            for i, target in enumerate(targets):
                zones.append({
                    'price': target['price'],
                    'position_pct': position_sizes[i],
                    'reasoning': f"Support at ${target['value_millions']:.1f}M liquidations"
                })
                
        elif direction == "SHORT":
            # Scale in at resistance levels (short liquidations)
            targets = sorted([c for c in short_clusters if c['price'] > current_price], 
                           key=lambda x: x['price'])[:4]
            
            position_sizes = [30, 30, 25, 15]
            for i, target in enumerate(targets):
                zones.append({
                    'price': target['price'],
                    'position_pct': position_sizes[i],
                    'reasoning': f"Resistance at ${target['value_millions']:.1f}M liquidations"
                })
                
        return zones
        
    def _score_visual_screener_coins(self, price_oi: List, price_volume: List, volume_oi: List) -> Dict[str, float]:
        """Score coins based on all visual screener data"""
        scores = {}
        
        # Score based on price vs OI
        for item in price_oi:
            symbol = item['symbol']
            price_change = abs(item.get('price_change_pct', 0))
            oi_change = abs(item.get('oi_change_pct', 0))
            scores[symbol] = scores.get(symbol, 0) + (price_change + oi_change) / 2
            
        # Add price vs volume scores
        for item in price_volume:
            symbol = item['symbol']
            price_change = abs(item.get('price_change_pct', 0))
            volume_change = abs(item.get('volume_change_pct', 0))
            scores[symbol] = scores.get(symbol, 0) + (price_change + volume_change) / 2
            
        # Add volume vs OI scores
        for item in volume_oi:
            symbol = item['symbol']
            volume_change = abs(item.get('volume_change_pct', 0))
            oi_change = abs(item.get('oi_change_pct', 0))
            scores[symbol] = scores.get(symbol, 0) + (volume_change + oi_change) / 2
            
        return scores
        
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        # In real implementation, fetch from price API
        mock_prices = {
            "BTC": 43250.0,
            "ETH": 2280.0,
            "SOL": 98.50,
            "BNB": 315.0,
            "XRP": 0.52,
            "DOGE": 0.081,
            "ADA": 0.285,
            "AVAX": 21.30,
            "MATIC": 0.72,
            "LINK": 14.25
        }
        return mock_prices.get(symbol, 100.0)