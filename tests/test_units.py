"""Unit tests for WhaleRadar.ai core components"""

import pytest
from datetime import datetime, timezone
from src.utils.validators import RateLimiter, SignalValidator
from src.utils.error_handler import RetryStrategy, ErrorRecovery
from src.indicators.visual_screener import VisualScreenerAnalyzer
from src.indicators.liquidation_analyzer import LiquidationAnalyzer
from src.indicators.rsi_heatmap import RSIAnalyzer
from unittest.mock import Mock, AsyncMock, patch


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_allows_calls_under_limit(self):
        """Test that rate limiter allows calls under the limit"""
        limiter = RateLimiter(calls_per_second=5)
        
        # Should allow first 5 calls
        for _ in range(5):
            assert limiter.can_make_call() == True
            limiter.record_call()
    
    def test_rate_limiter_blocks_calls_over_limit(self):
        """Test that rate limiter blocks calls over the limit"""
        limiter = RateLimiter(calls_per_second=5)
        
        # Record 5 calls
        for _ in range(5):
            limiter.record_call()
        
        # 6th call should be blocked
        assert limiter.can_make_call() == False
    
    def test_rate_limiter_resets_after_time_window(self):
        """Test that rate limiter resets after time window"""
        import time
        limiter = RateLimiter(calls_per_second=5)
        
        # Fill up the limit
        for _ in range(5):
            limiter.record_call()
        
        # Should be blocked
        assert limiter.can_make_call() == False
        
        # Wait for window to pass
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.can_make_call() == True


class TestErrorRecovery:
    """Test error recovery mechanisms"""
    
    def test_error_counting(self):
        """Test error counting functionality"""
        recovery = ErrorRecovery()
        
        # Record some errors
        recovery.record_error("APIError")
        recovery.record_error("APIError")
        
        assert recovery.error_counts["APIError"] == 2
        assert not recovery.should_circuit_break("APIError")
        
        # Record more to trigger circuit breaker
        for _ in range(3):
            recovery.record_error("APIError")
        
        assert recovery.should_circuit_break("APIError") == True
    
    def test_error_window_cleanup(self):
        """Test that old errors are cleaned up"""
        recovery = ErrorRecovery()
        recovery.error_window = 0.1  # 100ms for testing
        
        recovery.record_error("TestError")
        assert recovery.error_counts["TestError"] == 1
        
        # Wait for window to pass
        import time
        time.sleep(0.2)
        
        # Should be cleaned up
        recovery._clean_old_errors()
        assert "TestError" not in recovery.error_counts


class TestVisualScreenerLogic:
    """Test visual screener calculation logic"""
    
    def test_momentum_score_calculation(self):
        """Test momentum score calculation"""
        analyzer = VisualScreenerAnalyzer(Mock())
        
        # Test neutral case
        data = {"price_change": 0, "volume_change": 0, "oi_change": 0}
        score = analyzer._calculate_momentum_score(data)
        assert score == 50  # Neutral
        
        # Test bullish case
        data = {"price_change": 5, "volume_change": 300, "oi_change": 50}
        score = analyzer._calculate_momentum_score(data)
        assert score > 70  # Bullish
        
        # Test bearish case
        data = {"price_change": -5, "volume_change": 50, "oi_change": -30}
        score = analyzer._calculate_momentum_score(data)
        assert score < 30  # Bearish
    
    def test_bias_determination(self):
        """Test market bias determination"""
        analyzer = VisualScreenerAnalyzer(Mock())
        
        # Test strong long bias
        data = {"price_change": 10, "volume_change": 500, "oi_change": 100}
        momentum = 85
        bias = analyzer._determine_bias(data, momentum)
        assert bias == "STRONG_LONG"
        
        # Test neutral bias
        data = {"price_change": 1, "volume_change": 50, "oi_change": 5}
        momentum = 50
        bias = analyzer._determine_bias(data, momentum)
        assert bias == "NEUTRAL"


class TestLiquidationLogic:
    """Test liquidation analysis logic"""
    
    def test_direction_determination(self):
        """Test liquidation direction determination"""
        analyzer = LiquidationAnalyzer(Mock())
        
        # Mock liquidation clusters
        long_clusters = [Mock(distance_from_price_pct=3) for _ in range(5)]
        short_clusters = [Mock(distance_from_price_pct=3) for _ in range(10)]
        
        # More shorts than longs should indicate UP
        direction, confidence = analyzer._determine_direction(
            long_clusters, short_clusters, 
            total_long=1_000_000, total_short=2_000_000
        )
        
        assert direction == "UP"
        assert confidence in ["HIGH", "MEDIUM"]
    
    def test_scale_zone_calculation(self):
        """Test scale-in zone calculation"""
        analyzer = LiquidationAnalyzer(Mock())
        
        # Test position distribution
        assert analyzer._distribute_position(1) == [100]
        assert analyzer._distribute_position(2) == [60, 40]
        assert analyzer._distribute_position(3) == [40, 35, 25]
        assert analyzer._distribute_position(4) == [30, 30, 25, 15]
        
        # Test that distributions sum to 100
        for n in range(1, 10):
            distribution = analyzer._distribute_position(n)
            assert sum(distribution) == 100


class TestRSILogic:
    """Test RSI analysis logic"""
    
    def test_rsi_status_determination(self):
        """Test RSI status determination"""
        analyzer = RSIAnalyzer(Mock())
        
        # Test oversold
        rsi_values = {"1h": 25, "4h": 28, "12h": 30, "1d": 35}
        status = analyzer._determine_rsi_status(rsi_values)
        assert status in ["OVERSOLD", "WEAK"]
        
        # Test overbought
        rsi_values = {"1h": 75, "4h": 72, "12h": 71, "1d": 70}
        status = analyzer._determine_rsi_status(rsi_values)
        assert status in ["OVERBOUGHT", "STRONG"]
        
        # Test neutral
        rsi_values = {"1h": 50, "4h": 52, "12h": 48, "1d": 51}
        status = analyzer._determine_rsi_status(rsi_values)
        assert status == "NEUTRAL"
    
    def test_confluence_score_calculation(self):
        """Test RSI confluence score calculation"""
        analyzer = RSIAnalyzer(Mock())
        
        # Test high confluence (all similar)
        rsi_values = {"1h": 30, "4h": 32, "12h": 31, "1d": 30}
        score = analyzer._calculate_confluence_score(rsi_values)
        assert score >= 80
        
        # Test low confluence (divergent)
        rsi_values = {"1h": 20, "4h": 50, "12h": 70, "1d": 80}
        score = analyzer._calculate_confluence_score(rsi_values)
        assert score <= 40


@pytest.mark.asyncio
async def test_retry_strategy():
    """Test retry strategy with exponential backoff"""
    strategy = RetryStrategy(max_retries=3, base_delay=0.1)
    
    call_count = 0
    
    async def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Network error")
        return "Success"
    
    result = await strategy.execute_with_retry(failing_function)
    
    assert result == "Success"
    assert call_count == 3  # Should retry twice before succeeding


if __name__ == "__main__":
    pytest.main([__file__, "-v"])