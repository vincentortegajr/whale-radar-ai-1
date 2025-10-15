#!/usr/bin/env python3
"""Test updated v4 endpoints"""

import asyncio
import json
from src.api.coinglass_client import CoinGlassClient

async def test_v4_endpoints():
    """Test the updated v4 endpoints"""
    print("="*80)
    print("🔍 TESTING UPDATED V4 ENDPOINTS")
    print("="*80)
    
    async with CoinGlassClient() as client:
        # Test 1: RSI endpoint
        print("\n1. Testing RSI endpoint...")
        try:
            rsi_data = await client.get_rsi_heatmap("1h", 10)
            print(f"✅ RSI data received: {len(rsi_data)} items")
            if rsi_data and isinstance(rsi_data[0], dict):
                print(f"   First item: {json.dumps(rsi_data[0], indent=2)[:200]}...")
        except Exception as e:
            print(f"❌ RSI error: {e}")
            
        # Test 2: Liquidation heatmap
        print("\n2. Testing liquidation heatmap (model 2)...")
        try:
            liq_data = await client.get_liquidation_heatmap("BTC", model=2, timeframe="24h")
            print(f"✅ Liquidation data received")
            print(f"   Response type: {type(liq_data)}")
            if isinstance(liq_data, dict):
                print(f"   Keys: {list(liq_data.keys())}")
        except Exception as e:
            print(f"❌ Liquidation error: {e}")
            
        # Test 3: Whale alerts
        print("\n3. Testing whale alerts...")
        try:
            whale_data = await client.get_whale_alerts(limit=5)
            print(f"✅ Whale data received: {len(whale_data)} alerts")
            if whale_data:
                print(f"   First alert: {json.dumps(whale_data[0], indent=2)[:200]}...")
        except Exception as e:
            print(f"❌ Whale alert error: {e}")
            
        # Test 4: Visual screener data extraction
        print("\n4. Testing visual screener for BTC...")
        try:
            from src.indicators.visual_screener import VisualScreenerAnalyzer
            screener = VisualScreenerAnalyzer(client)
            btc_data = await screener.analyze_all_screeners("BTC", "5m")
            
            if btc_data:
                print(f"✅ BTC screener data:")
                print(f"   Price change: {btc_data.price_change_pct:.2f}%")
                print(f"   Volume change: {btc_data.volume_change_pct:.2f}%")
                print(f"   OI change: {btc_data.oi_change_pct:.2f}%")
                print(f"   Momentum score: {btc_data.momentum_score}")
                print(f"   Bias: {btc_data.bias}")
            else:
                print("❌ No BTC data found")
        except Exception as e:
            print(f"❌ Screener error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_v4_endpoints())