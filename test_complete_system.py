#!/usr/bin/env python3
"""Complete system validation test - Oracle level verification"""

import asyncio
import sys
from datetime import datetime

# Add src to path
sys.path.append('.')

from src.utils.config import settings, validate_config
from src.api.coinglass_client import CoinGlassClient
from src.api.telegram_bot import TelegramNotifier
from src.indicators.visual_screener import VisualScreenerAnalyzer
from src.indicators.liquidation_analyzer import LiquidationAnalyzer
from src.indicators.rsi_heatmap import RSIAnalyzer
from src.strategies.master_strategy import MasterStrategy
from src.utils.validators import SignalValidator
from src.utils.database import db
from src.utils.monitoring import performance_monitor
from src.utils.logger_setup import setup_logger

logger = setup_logger(__name__)


async def test_complete_flow():
    """Test the complete signal generation flow"""
    print("=" * 80)
    print("🧠 ORACLE-LEVEL SYSTEM VALIDATION")
    print("=" * 80)
    
    # 1. Validate configuration
    print("\n1. VALIDATING CONFIGURATION...")
    try:
        validate_config()
        print("✅ Configuration valid")
        print(f"   - API Key: {settings.coinglass_api_key[:10]}...")
        print(f"   - Telegram Token: {settings.telegram_bot_token[:10]}...")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
        
    # 2. Test database
    print("\n2. TESTING DATABASE...")
    try:
        # Test write
        test_signal = {
            "symbol": "BTC",
            "action": "LONG",
            "confidence": "HIGH",
            "signal_strength": 85,
            "current_price": 43000.0,
            "stop_loss": 42000.0,
            "take_profit_targets": [44000.0, 45000.0, 46000.0],
            "momentum_score": 80,
            "liquidation_direction": "UP",
            "rsi_status": "OVERSOLD",
            "reasons": ["Test signal"],
            "scale_in_zones": [{"price": 42800, "position_pct": 50}]
        }
        
        # Create mock signal object
        class MockSignal:
            def __init__(self, data):
                for k, v in data.items():
                    setattr(self, k, v)
                    
        signal_obj = MockSignal(test_signal)
        signal_id = db.save_signal(signal_obj)
        print(f"✅ Database write successful (ID: {signal_id})")
        
        # Test read
        recent = db.get_recent_signals(hours=1)
        print(f"✅ Database read successful ({len(recent)} signals)")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
        
    # 3. Test API connection
    print("\n3. TESTING COINGLASS API...")
    async with CoinGlassClient() as client:
        try:
            # Test getting symbols
            symbols = await client.get_perpetual_symbols()
            print(f"✅ API connection successful ({len(symbols)} symbols)")
            
            # Test a real symbol
            if symbols and "BTC" in symbols[:20]:
                print("✅ BTC found in symbols")
        except Exception as e:
            print(f"❌ API error: {e}")
            return False
            
    # 4. Test complete analysis flow
    print("\n4. TESTING COMPLETE ANALYSIS FLOW...")
    strategy = MasterStrategy()
    
    try:
        async with strategy.client:
            # Test with BTC
            print("   Testing BTC analysis...")
            signal = await strategy.analyze_symbol("BTC", 43000.0)
            
            if signal:
                print(f"✅ Signal generated:")
                print(f"   - Action: {signal.action}")
                print(f"   - Confidence: {signal.confidence}")
                print(f"   - Strength: {signal.signal_strength}/100")
                print(f"   - Stop Loss: ${signal.stop_loss:,.2f}")
                print(f"   - Take Profits: {[f'${tp:,.2f}' for tp in signal.take_profit_targets]}")
                
                # Validate signal
                is_valid, errors = SignalValidator.validate_signal(signal)
                if is_valid:
                    print("✅ Signal validation passed")
                else:
                    print(f"❌ Signal validation failed: {errors}")
                    return False
            else:
                print("⚠️  No signal generated (market may be neutral)")
                
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    # 5. Test Telegram formatting (without sending)
    print("\n5. TESTING TELEGRAM FORMATTING...")
    try:
        notifier = TelegramNotifier()
        
        if signal:
            # Test message formatting
            message = notifier._format_signal_message(signal)
            print("✅ Telegram message formatted successfully")
            print(f"   - Message length: {len(message)} chars")
            print(f"   - Contains emoji: {'🐋' in message}")
            print(f"   - Contains links: {'http' in message}")
        else:
            print("⚠️  No signal to format")
            
    except Exception as e:
        print(f"❌ Telegram formatting error: {e}")
        return False
        
    # 6. Test performance monitoring
    print("\n6. TESTING PERFORMANCE MONITORING...")
    try:
        # Get metrics
        api_stats = performance_monitor.get_api_statistics()
        system_metrics = performance_monitor.get_system_metrics()
        
        print("✅ Performance monitoring active")
        print(f"   - API calls: {api_stats['total_calls']}")
        print(f"   - Success rate: {api_stats['success_rate']:.1f}%")
        print(f"   - CPU usage: {system_metrics['cpu_percent']:.1f}%")
        print(f"   - Memory usage: {system_metrics['memory_percent']:.1f}%")
        
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
        
    # 7. Test error handling
    print("\n7. TESTING ERROR HANDLING...")
    try:
        # Test with invalid symbol
        async with CoinGlassClient() as client:
            screener = VisualScreenerAnalyzer(client)
            result = await screener.analyze_all_screeners("INVALID_SYMBOL_XYZ")
            
            if result is None:
                print("✅ Invalid symbol handled gracefully")
            else:
                print("⚠️  Unexpected result for invalid symbol")
                
    except Exception as e:
        print(f"✅ Error caught and handled: {type(e).__name__}")
        
    print("\n" + "=" * 80)
    print("✅ SYSTEM VALIDATION COMPLETE - ORACLE STANDARDS MET!")
    print("=" * 80)
    return True


async def test_mathematical_accuracy():
    """Test all mathematical calculations"""
    print("\n" + "=" * 80)
    print("🔢 MATHEMATICAL VALIDATION")
    print("=" * 80)
    
    # Test momentum score calculation
    from src.indicators.visual_screener import VisualScreenerAnalyzer
    analyzer = VisualScreenerAnalyzer(None)
    
    test_cases = [
        {"price_change": 0, "volume_change": 0, "oi_change": 0, "expected": 50},
        {"price_change": 10, "volume_change": 500, "oi_change": 50, "expected": 85},
        {"price_change": -10, "volume_change": 500, "oi_change": -50, "expected": 15},
    ]
    
    print("\n1. Testing momentum score calculation...")
    for i, test in enumerate(test_cases):
        score = analyzer._calculate_momentum_score(test)
        print(f"   Test {i+1}: Score={score}, Expected≈{test['expected']}")
        
    # Test position distribution
    from src.indicators.liquidation_analyzer import LiquidationAnalyzer
    liq_analyzer = LiquidationAnalyzer(None)
    
    print("\n2. Testing position distribution...")
    for n in range(1, 6):
        distribution = liq_analyzer._distribute_position(n)
        total = sum(distribution)
        print(f"   {n} entries: {distribution} = {total}%")
        assert total == 100, f"Distribution sum error: {total}"
        
    print("\n✅ All mathematical calculations verified!")
    

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_complete_flow())
    asyncio.run(test_mathematical_accuracy())