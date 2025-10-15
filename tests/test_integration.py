"""Integration tests for WhaleRadar.ai"""

import pytest
import asyncio
from datetime import datetime, timezone
from src.utils.config import settings
from src.api.coinglass_client import CoinGlassClient
from src.indicators.visual_screener import VisualScreenerAnalyzer
from src.indicators.liquidation_analyzer import LiquidationAnalyzer
from src.indicators.rsi_heatmap import RSIAnalyzer
from src.strategies.master_strategy import MasterStrategy
from src.utils.validators import SignalValidator
from src.utils.error_handler import WhaleRadarError


class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_coinglass_connection(self):
        """Test CoinGlass API connectivity"""
        async with CoinGlassClient() as client:
            # Test getting symbols
            symbols = await client.get_perpetual_symbols()
            
            assert isinstance(symbols, list)
            assert len(symbols) > 0
            assert "BTC" in symbols or "BTCUSDT" in symbols
    
    @pytest.mark.asyncio
    async def test_visual_screener_analysis(self):
        """Test visual screener analysis"""
        async with CoinGlassClient() as client:
            analyzer = VisualScreenerAnalyzer(client)
            
            # Test analyzing BTC
            result = await analyzer.analyze_all_screeners("BTC", timeframe="1h")
            
            if result:  # May be None if no data
                assert result.symbol == "BTC"
                assert 0 <= result.momentum_score <= 100
                assert result.bias in ["STRONG_LONG", "LONG", "NEUTRAL", "SHORT", "STRONG_SHORT", "WEAK_LONG", "WEAK_SHORT"]
    
    @pytest.mark.asyncio
    async def test_liquidation_analysis(self):
        """Test liquidation heatmap analysis"""
        async with CoinGlassClient() as client:
            analyzer = LiquidationAnalyzer(client)
            
            # Test analyzing BTC at a specific price
            current_price = 43000.0  # Example price
            result = await analyzer.analyze_liquidations("BTC", current_price)
            
            if result:
                assert result.symbol == "BTC"
                assert result.current_price == current_price
                assert result.direction in ["UP", "DOWN", "RANGE"]
                assert isinstance(result.scale_in_zones, list)
    
    @pytest.mark.asyncio
    async def test_rsi_analysis(self):
        """Test RSI analysis"""
        async with CoinGlassClient() as client:
            analyzer = RSIAnalyzer(client)
            
            # Test analyzing BTC RSI
            result = await analyzer.analyze_rsi("BTC")
            
            if result:
                assert result.symbol == "BTC"
                assert 0 <= result.rsi_1h <= 100
                assert 0 <= result.rsi_4h <= 100
                assert result.status in ["OVERBOUGHT", "OVERSOLD", "NEUTRAL", "STRONG", "WEAK"]
    
    @pytest.mark.asyncio
    async def test_master_strategy_signal_generation(self):
        """Test complete signal generation"""
        strategy = MasterStrategy()
        
        async with strategy.client:
            # Test analyzing BTC
            signal = await strategy.analyze_symbol("BTC", 43000.0)
            
            if signal:
                # Validate signal structure
                is_valid, errors = SignalValidator.validate_signal(signal)
                
                assert is_valid, f"Signal validation failed: {errors}"
                assert signal.symbol == "BTC"
                assert signal.action in ["LONG", "SHORT", "NEUTRAL"]
                assert 0 <= signal.signal_strength <= 100
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling mechanisms"""
        async with CoinGlassClient() as client:
            # Test invalid symbol
            analyzer = VisualScreenerAnalyzer(client)
            
            # Should handle gracefully
            result = await analyzer.analyze_all_screeners("INVALID_SYMBOL_12345")
            assert result is None or isinstance(result, type(None))
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        async with CoinGlassClient() as client:
            # Make multiple rapid requests
            tasks = []
            for i in range(15):  # More than rate limit
                tasks.append(client.get_market_overview())
            
            # Should handle rate limiting gracefully
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Some should succeed, some might be rate limited
                successful = [r for r in results if not isinstance(r, Exception)]
                assert len(successful) > 0
                
            except WhaleRadarError:
                # Rate limiting kicked in - this is expected
                pass
    
    @pytest.mark.asyncio
    async def test_data_validation(self):
        """Test data validation"""
        from src.utils.validators import (
            validate_symbol, 
            validate_timeframe,
            validate_percentage,
            validate_numerical_data
        )
        
        # Test symbol validation
        assert validate_symbol("BTC") == True
        assert validate_symbol("ETH123") == True
        assert validate_symbol("") == False
        assert validate_symbol("TOO_LONG_SYMBOL_NAME") == False
        
        # Test timeframe validation
        assert validate_timeframe("5m") == True
        assert validate_timeframe("1h") == True
        assert validate_timeframe("invalid") == False
        
        # Test percentage validation
        assert validate_percentage(50.0) == True
        assert validate_percentage(-50.0) == True
        assert validate_percentage(10000.0) == True
        assert validate_percentage(20000.0) == False
        
        # Test numerical validation
        assert validate_numerical_data(100, min_val=0, max_val=1000) == True
        assert validate_numerical_data(-10, min_val=0) == False
        assert validate_numerical_data(float('nan')) == False


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])