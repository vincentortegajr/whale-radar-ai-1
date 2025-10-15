"""CoinGlass Pro API Client ($900/month tier)"""

import aiohttp
import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json
from src.utils.logger_setup import setup_logger
from src.utils.config import settings
from src.utils.validators import validate_api_response, validate_symbol, RateLimiter
from src.utils.error_handler import APIError, RateLimitError, async_handle_errors, retry_strategy
from src.utils.monitoring import performance_monitor, monitor_api_call

logger = setup_logger(__name__)


class CoinGlassClient:
    """CoinGlass Pro API Client with rate limiting and retry logic"""
    
    def __init__(self):
        self.api_key = settings.coinglass_api_key
        self.base_url = settings.coinglass_base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.rate_limiter = RateLimiter(settings.api_calls_per_second)
        
        # Connection pooling
        self.connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Per-host connection limit
            ttl_dns_cache=300  # DNS cache timeout
        )
        
        # Session configuration
        self.timeout = aiohttp.ClientTimeout(
            total=30,  # Total timeout
            connect=5,  # Connection timeout
            sock_read=10  # Socket read timeout
        )
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=self.timeout,
            headers={"User-Agent": "WhaleRadar.ai/1.0"}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        await self.connector.close()
            
    async def _rate_limit(self):
        """Implement rate limiting"""
        if not self.rate_limiter.can_make_call():
            # Calculate wait time
            await asyncio.sleep(0.1)  # Small delay before retry
            if not self.rate_limiter.can_make_call():
                raise RateLimitError(retry_after=1)
        
        self.rate_limiter.record_call()
        
    @async_handle_errors
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request with enhanced error handling and monitoring"""
        
        # Input validation
        if not endpoint.startswith('/'):
            endpoint = f'/{endpoint}'
            
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Execute with retry strategy
        async def _execute():
            await self._rate_limit()
            
            if not self.session:
                raise APIError("Session not initialized. Use 'async with' context manager.")
            
            start_time = time.time()
            
            try:
                async with self.session.get(url, headers=headers, params=params) as response:
                    response_text = await response.text()
                    duration = time.time() - start_time
                    
                    # Record metric
                    performance_monitor.record_api_call(
                        endpoint, duration, response.status, response.status == 200
                    )
                    
                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            
                            # Validate response structure
                            if not validate_api_response(data, ['success', 'data']):
                                raise APIError(f"Invalid response structure: {response_text[:200]}")
                                
                            return data
                            
                        except json.JSONDecodeError as e:
                            raise APIError(f"Invalid JSON response: {e}")
                            
                    elif response.status == 429:
                        # Extract retry-after header if available
                        retry_after = response.headers.get('Retry-After', 60)
                        raise RateLimitError(retry_after=int(retry_after))
                        
                    elif response.status == 401:
                        raise APIError("Invalid API key", status_code=401)
                        
                    elif response.status == 403:
                        raise APIError("Access forbidden - check API permissions", status_code=403)
                        
                    else:
                        raise APIError(
                            f"API request failed: {response_text[:500]}", 
                            status_code=response.status
                        )
                        
            except asyncio.TimeoutError:
                duration = time.time() - start_time
                performance_monitor.record_api_call(endpoint, duration, None, False)
                raise APIError("Request timeout", status_code=408)
                
            except aiohttp.ClientError as e:
                duration = time.time() - start_time
                performance_monitor.record_api_call(endpoint, duration, None, False)
                raise APIError(f"Network error: {e}")
                
        return await retry_strategy.execute_with_retry(_execute)
        
    # Visual Screener Endpoints
    @monitor_api_call(performance_monitor, "visual_screener_price_oi")
    async def get_visual_screener_price_oi(self, timeframe: str = "5m") -> List[Dict]:
        """Get Price vs Open Interest change data"""
        from src.utils.validators import validate_timeframe
        
        if not validate_timeframe(timeframe):
            raise ValueError(f"Invalid timeframe: {timeframe}")
            
        logger.info(f"Fetching Price vs OI screener data (timeframe: {timeframe})")
        endpoint = "/api/v4/perpetual/visual-screener/price-oi-change"
        params = {"timeframe": timeframe}
        response = await self._make_request(endpoint, params)
        
        # Return data array from response
        return response.get('data', [])
        
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