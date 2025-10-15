"""CoinGlass Pro API Client ($900/month tier)"""

import aiohttp
import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json
from src.utils.logger_setup import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)


class CoinGlassClient:
    """CoinGlass Pro API Client with rate limiting and retry logic"""
    
    def __init__(self):
        self.api_key = settings.coinglass_api_key
        self.base_url = settings.coinglass_base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.calls_per_second = settings.api_calls_per_second
        self.last_call_time = 0
        self.call_times: List[float] = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def _rate_limit(self):
        """Implement rate limiting"""
        now = time.time()
        
        # Remove calls older than 1 second
        self.call_times = [t for t in self.call_times if now - t < 1]
        
        # If we've hit the rate limit, wait
        if len(self.call_times) >= self.calls_per_second:
            sleep_time = 1 - (now - self.call_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                
        # Record this call
        self.call_times.append(now)
        
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request with retry logic"""
        await self._rate_limit()
        
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        for attempt in range(3):
            try:
                async with self.session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 429:  # Rate limited
                        logger.warning(f"Rate limited, waiting {2 ** attempt} seconds...")
                        await asyncio.sleep(2 ** attempt)
                    else:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        raise Exception(f"API error {response.status}: {error_text}")
                        
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}/3): {e}")
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
                
        raise Exception("Max retries exceeded")
        
    # Visual Screener Endpoints
    async def get_visual_screener_price_oi(self, timeframe: str = "5m") -> List[Dict]:
        """Get Price vs Open Interest change data"""
        logger.info(f"Fetching Price vs OI screener data (timeframe: {timeframe})")
        endpoint = "/api/v4/perpetual/visual-screener/price-oi-change"
        params = {"timeframe": timeframe}
        return await self._make_request(endpoint, params)
        
    async def get_visual_screener_price_volume(self, timeframe: str = "5m") -> List[Dict]:
        """Get Price vs Volume change data"""
        logger.info(f"Fetching Price vs Volume screener data (timeframe: {timeframe})")
        endpoint = "/api/v4/perpetual/visual-screener/price-volume-change"
        params = {"timeframe": timeframe}
        return await self._make_request(endpoint, params)
        
    async def get_visual_screener_volume_oi(self, timeframe: str = "5m") -> List[Dict]:
        """Get Volume vs Open Interest change data"""
        logger.info(f"Fetching Volume vs OI screener data (timeframe: {timeframe})")
        endpoint = "/api/v4/perpetual/visual-screener/volume-oi-change"
        params = {"timeframe": timeframe}
        return await self._make_request(endpoint, params)
        
    # Liquidation Heatmap Endpoints
    async def get_liquidation_heatmap(self, symbol: str, model: int = 2, timeframe: str = "24h") -> Dict:
        """Get liquidation heatmap data"""
        logger.info(f"Fetching liquidation heatmap for {symbol} (model: {model}, timeframe: {timeframe})")
        endpoint = f"/api/v4/futures/liquidation-heatmap/model{model}/{symbol}"
        params = {"timeframe": timeframe}
        return await self._make_request(endpoint, params)
        
    async def get_liquidation_heatmap_all_timeframes(self, symbol: str, model: int = 2) -> Dict:
        """Get liquidation heatmap for all timeframes"""
        timeframes = ["12h", "24h", "3d", "7d", "30d", "1y"]
        results = {}
        
        for tf in timeframes:
            try:
                results[tf] = await self.get_liquidation_heatmap(symbol, model, tf)
            except Exception as e:
                logger.error(f"Failed to get liquidation data for {symbol} {tf}: {e}")
                
        return results
        
    # RSI Heatmap Endpoints
    async def get_rsi_heatmap(self, timeframe: str = "1h", top: int = 100) -> List[Dict]:
        """Get RSI heatmap data for top coins"""
        logger.info(f"Fetching RSI heatmap (timeframe: {timeframe}, top: {top})")
        endpoint = "/api/v4/indicator/rsi-heatmap"
        params = {"timeframe": timeframe, "limit": top}
        return await self._make_request(endpoint, params)
        
    async def get_rsi_multi_timeframe(self, symbol: str) -> Dict:
        """Get RSI for multiple timeframes for a specific symbol"""
        timeframes = ["5m", "15m", "1h", "4h", "12h", "1d", "1w"]
        results = {}
        
        for tf in timeframes:
            try:
                data = await self.get_rsi_heatmap(tf, 200)
                # Find the symbol in the results
                for coin in data:
                    if coin.get("symbol") == symbol:
                        results[tf] = coin.get("rsi", 50)
                        break
            except Exception as e:
                logger.error(f"Failed to get RSI for {symbol} {tf}: {e}")
                results[tf] = 50  # Default to neutral
                
        return results
        
    # Whale Alert Endpoints
    async def get_whale_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent whale transaction alerts"""
        logger.info("Fetching whale alerts")
        endpoint = "/api/v4/whale-alert/transactions"
        params = {"limit": limit}
        return await self._make_request(endpoint, params)
        
    # On-chain Flow Endpoints  
    async def get_onchain_flow(self, coin: str) -> Dict:
        """Get on-chain inflow/outflow data"""
        logger.info(f"Fetching on-chain flow for {coin}")
        endpoint = f"/api/v4/onchain/inflow-outflow/{coin}"
        return await self._make_request(endpoint)
        
    # Market Overview
    async def get_market_overview(self) -> Dict:
        """Get overall market metrics"""
        logger.info("Fetching market overview")
        endpoint = "/api/v4/market/overview"
        return await self._make_request(endpoint)
        
    # Get all perpetual symbols
    async def get_perpetual_symbols(self) -> List[str]:
        """Get list of all available perpetual symbols"""
        logger.info("Fetching perpetual symbols list")
        endpoint = "/api/v4/perpetual/symbols"
        data = await self._make_request(endpoint)
        return [s["symbol"] for s in data if s.get("active", True)]